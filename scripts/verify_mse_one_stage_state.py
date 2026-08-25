#!/usr/bin/env python
"""Preflight/handoff verification for the MSE one-stage experiment.

Answers, in one artifact, the questions Section 11.3 step 1 of the plan asks
before any compute resumes on a new machine:

* which interpreter, packages and (optionally) Julia are present;
* whether every input artifact the search and the confirmation stages read is
  present with the expected sha256;
* whether the frozen source files still hash to what the execution-provenance
  record says produced the existing reports;
* whether both task matrices still enumerate 165 and 12 tasks;
* which reports exist, whether each validates, and their sha256.

Typical use::

    # on the source machine, before packing
    python scripts/verify_mse_one_stage_state.py --json experiments/state_csd3.json

    # on the target machine, after unpacking
    python scripts/verify_mse_one_stage_state.py --json experiments/state_lightning.json \
        --compare experiments/state_csd3.json --check-julia

``--compare`` exits non-zero if any carried input, source file or existing
report differs, so a silent transfer corruption cannot reach the search.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import run_mse_one_stage_pool as pool                            # noqa: E402

PROVENANCE = REPO / "experiments" / "mse_one_stage_execution_provenance.json"
PROVENANCE_BLOCKS = ("initial_execution", "replacement_execution",
                     "execution_amendment_a1", "execution_amendment_a2")
RUNS = ["lcdm_tt_beta3e-4", "lcdm_tt_ee_lowl"]
N_LATENTS = {"lcdm_tt_beta3e-4": 5, "lcdm_tt_ee_lowl": 6}
PACKAGES = ["pysr", "juliacall", "juliapkg", "numpy", "scipy", "pandas",
            "sympy", "scikit-learn", "matplotlib", "gmm_mi", "torch"]

SOURCE_FILES = [
    "scripts/run_blind_sr.py",
    "scripts/run_shuffled_control.py",
    "scripts/consolidate_mse_one_stage.py",
    "src/cmb_lcdm_sr/sr.py",
    "src/cmb_lcdm_sr/utils.py",
    "src/cmb_lcdm_sr/calibrate.py",
    "src/cmb_lcdm_sr/tiers.py",
    "src/cmb_lcdm_sr/semantics.py",
    "src/cmb_lcdm_sr/mi.py",
    "hpc/slurm_mse_one_stage_sr.sh",
    "hpc/slurm_mse_one_stage_control.sh",
    "hpc/slurm_mse_one_stage_consolidate.sh",
    "experiments/mse_one_stage_sr_plan.md",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def provenance_source_names() -> list[str]:
    """Every source file any provenance block pins, newest hash wins."""
    if not PROVENANCE.is_file():
        return []
    payload = json.loads(PROVENANCE.read_text())
    names: list[str] = []
    for block in PROVENANCE_BLOCKS:
        names.extend((payload.get(block) or {}).get("source_sha256", {}))
    return names


def source_paths() -> list[str]:
    """SOURCE_FILES plus anything the provenance record pins."""
    return sorted(dict.fromkeys(list(SOURCE_FILES) + provenance_source_names()))


def hash_map(paths) -> dict:
    out = {}
    for rel in paths:
        path = REPO / rel
        out[str(rel)] = (sha256(path) if path.is_file() else None)
    return out


def input_paths() -> list[str]:
    paths = ["data/theta.npy", "data/splits_v1.npz", "data/meta.json"]
    for run in RUNS:
        paths.append(f"models/{run}/analysis/encoder_means_test.npy")
        paths.append(f"models/{run}/config_used.json")
        for k in range(N_LATENTS[run]):
            paths.append(f"models/{run}/analysis/residual_z{k}_v1.npy")
            paths.append(f"models/{run}/analysis/f1hat_z{k}_v1.npy")
        paths.append(f"experiments/residual_sr_{run}.json")
        paths.append(f"experiments/residual_sr_ia_{run}.json")
    return paths


def baseline_result_paths() -> list[str]:
    """Legacy GMM-MI fronts re-ranked by `mi20-mse` / reused by `mi20-mi`."""
    paths = []
    for run in RUNS:
        for k in range(N_LATENTS[run]):
            for seed in range(5):
                paths.append(f"results/{run}/allparams/z{k}_seed{seed}/report.json")
    return paths


def environment() -> dict:
    from importlib.metadata import PackageNotFoundError, version

    packages = {}
    for name in PACKAGES:
        try:
            packages[name] = version(name)
        except PackageNotFoundError:
            packages[name] = None
    return {
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "cpu_count": os.cpu_count(),
        "env": {k: os.environ.get(k) for k in
                ("JULIA_NUM_THREADS", "PYTHON_JULIAPKG_PROJECT",
                 "PYTHON_JULIAPKG_OFFLINE", "OMP_NUM_THREADS")},
        "packages": packages,
    }


def julia_version() -> dict:
    try:
        from juliacall import Main as jl                          # noqa: PLC0415

        return {"julia_version": str(jl.seval("string(VERSION)")),
                "julia_nthreads": int(jl.seval("Threads.nthreads()"))}
    except Exception as exc:                                     # noqa: BLE001
        return {"julia_version": None, "error": f"{type(exc).__name__}: {exc}"}


def matrix_state() -> dict:
    state = {}
    for family in ("main", "control"):
        tasks = pool.enumerate_tasks(family, None)
        rows, done, pending, invalid = [], [], [], []
        for task in tasks:
            status, reason = pool.task_status(task)
            report = REPO / task["out_dir"] / "report.json"
            row = {"task_id": task["task_id"], "out_dir": task["out_dir"],
                   "status": status, "reason": reason,
                   "sha256": sha256(report) if report.is_file() else None}
            rows.append(row)
            {"done": done, "pending": pending,
             "invalid": invalid}[status].append(task["task_id"])
        state[family] = {
            "total": len(tasks), "complete": len(done),
            "pending_ids": pending, "invalid_ids": invalid, "tasks": rows,
        }
    return state


def provenance_drift(sources: dict) -> dict:
    if not PROVENANCE.is_file():
        return {"available": False}
    payload = json.loads(PROVENANCE.read_text())
    expected = {}
    for block in PROVENANCE_BLOCKS:
        expected.update((payload.get(block) or {}).get("source_sha256", {}))
    drift = {}
    for rel, want in expected.items():
        have = sources.get(rel)
        if have != want:
            drift[rel] = {"provenance": want, "worktree": have,
                          "present": (REPO / rel).is_file()}
    return {"available": True, "checked": len(expected),
            "matching": len(expected) - len(drift), "drift": drift,
            "note": "each file is compared with the newest provenance "
                    "block that names it; drift is not automatically an "
                    "error, but it must be explicit before compute resumes."}


def build_state(check_julia: bool) -> dict:
    sources = hash_map(source_paths())
    state = {
        "kind": "mse_one_stage_machine_state",
        "schema_version": 1,
        "repo": str(REPO),
        "environment": environment(),
        "inputs_sha256": hash_map(input_paths()),
        "baseline_reports_sha256": hash_map(baseline_result_paths()),
        "sources_sha256": sources,
        "provenance_drift": provenance_drift(sources),
        "matrices": matrix_state(),
    }
    if check_julia:
        state["environment"].update(julia_version())
    return state


def compare(state: dict, baseline_path: Path) -> int:
    base = json.loads(baseline_path.read_text())
    problems: list[str] = []

    for section in ("inputs_sha256", "sources_sha256",
                    "baseline_reports_sha256"):
        for rel, want in base.get(section, {}).items():
            have = state.get(section, {}).get(rel)
            if want is None and have is None:
                continue
            if have != want:
                problems.append(f"{section}: {rel} {want} -> {have}")

    for family in ("main", "control"):
        base_tasks = {t["task_id"]: t
                      for t in base["matrices"][family]["tasks"]}
        now_tasks = {t["task_id"]: t
                     for t in state["matrices"][family]["tasks"]}
        if len(base_tasks) != len(now_tasks):
            problems.append(f"{family}: matrix size "
                            f"{len(base_tasks)} -> {len(now_tasks)}")
        for task_id, was in base_tasks.items():
            now = now_tasks.get(task_id)
            if now is None:
                problems.append(f"{family} task {task_id} missing from matrix")
                continue
            if was["out_dir"] != now["out_dir"]:
                problems.append(f"{family} task {task_id} path "
                                f"{was['out_dir']} -> {now['out_dir']}")
            if was["sha256"] and was["sha256"] != now["sha256"]:
                problems.append(
                    f"{family} task {task_id} report changed or lost "
                    f"({was['sha256'][:12]} -> "
                    f"{(now['sha256'] or 'missing')[:12]})")

    print(f"[compare] baseline={baseline_path}")
    if problems:
        for line in problems:
            print(f"[compare] MISMATCH {line}")
        print(f"[compare] {len(problems)} mismatch(es)")
        return 1
    print("[compare] every carried input, source and existing report matches "
          "the baseline")
    return 0


def summarise(state: dict) -> None:
    env = state["environment"]
    print(f"[state] host={env['host']} cpus={env['cpu_count']} "
          f"python={env['python_version']}")
    print(f"[state] platform={env['platform']}")
    for name in ("pysr", "numpy", "scikit-learn", "sympy", "pandas", "gmm_mi"):
        print(f"[state]   {name}={env['packages'].get(name)}")
    if "julia_version" in env:
        print(f"[state]   julia={env['julia_version']} "
              f"threads={env.get('julia_nthreads')}")
    missing = [k for k, v in state["inputs_sha256"].items() if v is None]
    print(f"[state] inputs: {len(state['inputs_sha256']) - len(missing)}/"
          f"{len(state['inputs_sha256'])} present")
    for rel in missing:
        print(f"[state]   MISSING {rel}")
    missing_base = [k for k, v in state["baseline_reports_sha256"].items()
                    if v is None]
    print(f"[state] legacy GMM-MI fronts: "
          f"{len(state['baseline_reports_sha256']) - len(missing_base)}/"
          f"{len(state['baseline_reports_sha256'])} present")
    for rel in missing_base[:5]:
        print(f"[state]   MISSING {rel}")
    drift = state["provenance_drift"]
    if drift.get("available"):
        print(f"[state] provenance: {drift['matching']}/{drift['checked']} "
              f"recorded source hashes match")
        for rel, pair in drift["drift"].items():
            print(f"[state]   DRIFT {rel}")
    for family, block in state["matrices"].items():
        print(f"[state] {family}: {block['complete']}/{block['total']} "
              f"complete, {len(block['pending_ids'])} pending, "
              f"{len(block['invalid_ids'])} invalid")
        if block["invalid_ids"]:
            print(f"[state]   invalid ids: {block['invalid_ids']}")


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", default=None, help="Write the state artifact here.")
    p.add_argument("--compare", default=None,
                   help="Baseline state artifact to diff against.")
    p.add_argument("--check-julia", action="store_true",
                   help="Start Julia to record its version (slow, ~1 min).")
    args = p.parse_args()

    os.chdir(REPO)
    state = build_state(args.check_julia)
    summarise(state)
    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
        print(f"[state] wrote {out}")
    if args.compare:
        return compare(state, Path(args.compare))
    return 0


if __name__ == "__main__":
    sys.exit(main())
