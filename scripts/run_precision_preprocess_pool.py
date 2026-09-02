#!/usr/bin/env python
"""Scheduler-free executor for the frozen precision/preprocessing campaign.

The Slurm launcher remains the sole definition of the 330 task identities.
This executor reads its ``PRINT_MATRIX=1`` table and runs the same
``run_blind_sr.py`` argument vectors inside persistent PySR/Julia workers.
That amortises Julia startup on a small CPU machine and makes the campaign
resumable across Lightning Studio interruptions.

Examples::

    python scripts/run_precision_preprocess_pool.py --dry-run
    python scripts/run_precision_preprocess_pool.py --smoke lightning1 \
        --task-ids 0,55,110,165,220,275 --workers 1 --threads 4
    python scripts/run_precision_preprocess_pool.py --workers 2 --threads 2 \
        --time-budget-minutes 210

Only a report which validates against its complete task contract is skipped.
An invalid existing report is never overwritten by this executor.
"""
from __future__ import annotations

import argparse
import csv
import importlib
import json
import multiprocessing as mp
import os
import platform
import queue
import re
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
LAUNCHER = REPO / "hpc" / "slurm_precision_preprocess_v1.sh"
RUNNER = SCRIPTS / "run_blind_sr.py"
TOTAL_TASKS = 330

N_SAMPLES = 5000
NITERATIONS = 200
POPULATIONS = 15
SMOKE_N_SAMPLES = 500
SMOKE_NITERATIONS = 1
SMOKE_POPULATIONS = 2

DEFAULT_LEDGER = "logs/precision_preprocess_pool_ledger.jsonl"
DEFAULT_LOG_DIR = "logs"
SAFE_TAG = re.compile(r"^[A-Za-z0-9_.-]+$")

# This mirrors the named profiles in cmb_lcdm_sr.sr without importing numpy
# before worker processes fork.  A focused test binds the two definitions.
PROFILE_CONTRACTS = {
    "raw64": {
        "inputs": ["omega_b", "omega_cdm", "H0", "tau", "A_s", "n_s"],
        "sampled_expressions": {
            "omega_b": "omega_b",
            "omega_cdm": "omega_cdm",
            "H0": "H0",
            "tau": "tau",
            "A_s": "exp(ln10As)*1e-10",
            "n_s": "n_s",
        },
    },
    "physical_o1_64": {
        "inputs": ["wb100", "wc10", "h", "tau", "A9", "n_s"],
        "sampled_expressions": {
            "wb100": "100*omega_b",
            "wc10": "10*omega_cdm",
            "h": "H0/100",
            "tau": "tau",
            "A9": "exp(ln10As)/10",
            "n_s": "n_s",
        },
    },
    "logamp64": {
        "inputs": ["omega_b", "omega_cdm", "H0", "tau", "ln10As", "n_s"],
        "sampled_expressions": {
            "omega_b": "omega_b",
            "omega_cdm": "omega_cdm",
            "H0": "H0",
            "tau": "tau",
            "ln10As": "ln10As",
            "n_s": "n_s",
        },
    },
}

MATRIX_FIELDS = [
    "task_id", "run_dir", "arm", "inner_loss", "selection_metric",
    "posthoc_mi", "latent", "seed", "maxsize", "family", "out_dir",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(value) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and value == value
        and abs(value) != float("inf")
    )


def _integer(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


# ---------------------------------------------------------------------------
# Frozen task matrix: read from the launcher, never independently generated.
# ---------------------------------------------------------------------------
def read_matrix() -> list[dict[str, str]]:
    env = dict(os.environ, PRINT_MATRIX="1", ACCOUNT="MPHIL-DIS-SL2-CPU")
    # The account guard is relevant to sbatch, not to scheduler-free matrix
    # inspection.  Avoid inheriting a host Slurm allocation accidentally.
    env.pop("SLURM_JOB_ACCOUNT", None)
    proc = subprocess.run(
        ["bash", str(LAUNCHER)],
        cwd=REPO,
        env=env,
        check=True,
        text=True,
        capture_output=True,
    )
    reader = csv.DictReader(proc.stdout.splitlines(), delimiter="\t")
    if reader.fieldnames != MATRIX_FIELDS:
        raise SystemExit(
            f"[err] {LAUNCHER.name} matrix fields changed: {reader.fieldnames!r}"
        )
    rows = list(reader)
    if len(rows) != TOTAL_TASKS:
        raise SystemExit(
            f"[err] {LAUNCHER.name} printed {len(rows)} tasks, "
            f"expected {TOTAL_TASKS}"
        )
    _validate_matrix(rows)
    return rows


def _validate_matrix(rows: list[dict[str, str]]) -> None:
    seen_paths: set[str] = set()
    for expected_id, row in enumerate(rows):
        try:
            task_id = int(row["task_id"])
            latent = int(row["latent"])
            seed = int(row["seed"])
            maxsize = int(row["maxsize"])
        except (KeyError, TypeError, ValueError) as exc:
            raise SystemExit(f"[err] malformed matrix row {expected_id}: {exc}") from exc
        if task_id != expected_id:
            raise SystemExit(
                f"[err] matrix row {expected_id} has task_id={task_id}"
            )
        if row["arm"] not in PROFILE_CONTRACTS:
            raise SystemExit(f"[err] task {task_id} has unknown arm {row['arm']!r}")
        objective = (
            row["inner_loss"], row["selection_metric"], row["posthoc_mi"],
            maxsize, row["family"],
        )
        allowed = {
            ("gmm_mi", "mi", "full", 20, "gmm_mi_ms20"),
            ("mse", "mse", "none", 40, "mse_ms40"),
        }
        if objective not in allowed:
            raise SystemExit(
                f"[err] task {task_id} has unexpected objective contract {objective!r}"
            )
        run = Path(row["run_dir"]).name
        max_latent = 4 if run == "lcdm_tt_beta3e-4" else (
            5 if run == "lcdm_tt_ee_lowl" else -1
        )
        if not 0 <= latent <= max_latent or not 0 <= seed <= 4:
            raise SystemExit(
                f"[err] task {task_id} has invalid run/latent/seed "
                f"{run}/{latent}/{seed}"
            )
        expected_out = (
            f"results/{run}/precision_preprocess_v1/{row['arm']}/"
            f"{row['family']}/z{latent}_seed{seed}"
        )
        if row["out_dir"] != expected_out:
            raise SystemExit(
                f"[err] task {task_id} output changed: {row['out_dir']!r}"
            )
        if expected_out in seen_paths:
            raise SystemExit(f"[err] duplicate output directory {expected_out}")
        seen_paths.add(expected_out)


def build_task(row: dict[str, str], smoke: str | None = None) -> dict:
    task_id = int(row["task_id"])
    latent = int(row["latent"])
    seed = int(row["seed"])
    maxsize = int(row["maxsize"])
    run = Path(row["run_dir"]).name
    if smoke:
        out_dir = (
            Path("results") / run / f"precision_preprocess_v1_smoke_{smoke}"
            / row["arm"] / row["family"] / f"z{latent}_seed{seed}"
        )
        n_samples = SMOKE_N_SAMPLES
        niterations = SMOKE_NITERATIONS
        populations = SMOKE_POPULATIONS
    else:
        out_dir = Path(row["out_dir"])
        n_samples = N_SAMPLES
        niterations = NITERATIONS
        populations = POPULATIONS

    argv = [
        "--run-dir", row["run_dir"],
        "--dataset-dir", "data",
        "--latent-index", str(latent),
        "--input-config", row["arm"],
        "--n-samples", str(n_samples),
        "--niterations", str(niterations),
        "--populations", str(populations),
        "--maxsize", str(maxsize),
        "--inner-loss", row["inner_loss"],
        "--selection-metric", row["selection_metric"],
        "--posthoc-mi", row["posthoc_mi"],
        "--skip-ols-baseline",
        "--turbo",
        "--parallelism", "multithreading",
        "--seed", str(seed),
        "--out-dir", str(out_dir),
    ]
    return {
        "task_id": task_id,
        "run_dir": row["run_dir"],
        "run": run,
        "arm": row["arm"],
        "inner_loss": row["inner_loss"],
        "selection_metric": row["selection_metric"],
        "posthoc_mi": row["posthoc_mi"],
        "latent": latent,
        "seed": seed,
        "maxsize": maxsize,
        "family": row["family"],
        "out_dir": str(out_dir),
        "n_samples": n_samples,
        "niterations": niterations,
        "populations": populations,
        "argv": argv,
        "smoke": smoke,
    }


def enumerate_tasks(smoke: str | None = None) -> list[dict]:
    return [build_task(row, smoke) for row in read_matrix()]


# ---------------------------------------------------------------------------
# Resume contract.
# ---------------------------------------------------------------------------
def validate_report(path: Path, task: dict) -> tuple[bool, str]:
    try:
        report = json.loads(path.read_text())
    except FileNotFoundError:
        return False, "missing"
    except Exception as exc:  # noqa: BLE001
        return False, f"unreadable: {exc}"
    if not isinstance(report, dict):
        return False, "not a JSON object"

    n_samples = task["n_samples"]
    n_val = int(round(n_samples * 0.2))
    n_fit = n_samples - n_val
    profile = PROFILE_CONTRACTS[task["arm"]]
    expected = {
        "run_dir": task["run_dir"],
        "regime": task["run"],
        "latent_index": task["latent"],
        "target_npy": None,
        "target_label": f"z{task['latent']}",
        "input_config": task["arm"],
        "input_names": profile["inputs"],
        "input_labels": profile["inputs"],
        "input_sampled_expressions": profile["sampled_expressions"],
        "extra_inputs": [],
        "n_samples": n_samples,
        "n_fit": n_fit,
        "n_val": n_val,
        "inner_loss": task["inner_loss"],
        "selection_metric": task["selection_metric"],
        "selection_direction": (
            "descending" if task["selection_metric"] == "mi" else "ascending"
        ),
        "posthoc_mi_mode": task["posthoc_mi"],
        "posthoc_mi_status": (
            "computed" if task["posthoc_mi"] == "full"
            else "skipped_not_selected"
        ),
        "seed": task["seed"],
        "ols_baseline": {
            "status": "skipped",
            "reason": "fixed_old_ols_reused_downstream",
        },
        "top5_ranked_by": f"VAL {task['selection_metric'].upper()} (primary)",
    }
    bad = [key for key, value in expected.items() if report.get(key) != value]

    target_transform = report.get("target_transform")
    if not isinstance(target_transform, dict):
        bad.append("target_transform")
    else:
        if target_transform.get("kind") != "standardize":
            bad.append("target_transform.kind")
        if target_transform.get("fit_rows") != [0, n_fit]:
            bad.append("target_transform.fit_rows")
        if not _finite(target_transform.get("mean")):
            bad.append("target_transform.mean")
        if not _finite(target_transform.get("std")) or target_transform.get("std", 0) <= 0:
            bad.append("target_transform.std")

    kwargs = report.get("pysr_kwargs")
    kw_expected = {
        "niterations": task["niterations"],
        "populations": task["populations"],
        "maxsize": task["maxsize"],
        "binary_operators": ["+", "*", "-", "/"],
        "unary_operators": ["exp", "log", "neg", "square"],
        "parallelism": "multithreading",
        "random_state": task["seed"],
        "precision": 64,
        "print_precision": 17,
    }
    if not isinstance(kwargs, dict):
        bad.append("pysr_kwargs")
    else:
        bad.extend(
            f"pysr_kwargs.{key}"
            for key, value in kw_expected.items()
            if kwargs.get(key) != value
        )
        if not isinstance(kwargs.get("run_id"), str) or not kwargs["run_id"]:
            bad.append("pysr_kwargs.run_id")
        if not isinstance(kwargs.get("pysr_version"), str) or not kwargs["pysr_version"]:
            bad.append("pysr_kwargs.pysr_version")

    equations = report.get("all_equations")
    if (
        not isinstance(equations, list)
        or not equations
        or not all(isinstance(row, dict) for row in equations)
        or report.get("n_equations") != len(equations)
    ):
        bad.append("all_equations")
        equations = []
    top5 = report.get("top5")
    if (
        not isinstance(top5, list)
        or not 1 <= len(top5) <= 5
        or not all(isinstance(row, dict) for row in top5)
    ):
        bad.append("top5")
        top5 = []
    best_index = report.get("best_index")
    best_expression = report.get("best_expression")
    if not _integer(best_index):
        bad.append("best_index")
    if not isinstance(best_expression, str) or not best_expression.strip():
        bad.append("best_expression")
    if top5:
        if top5[0].get("index") != best_index:
            bad.append("top5[0].index")
        if top5[0].get("expression_simplified") != best_expression:
            bad.append("top5[0].expression_simplified")
    if equations and best_index not in {row.get("index") for row in equations}:
        bad.append("best_index_not_in_all_equations")

    if not _finite(report.get("best_mse_val")):
        bad.append("best_mse_val")
    if task["selection_metric"] == "mi":
        if not _finite(report.get("best_mi_val")):
            bad.append("best_mi_val")
    elif report.get("best_mi_val") is not None:
        bad.append("best_mi_val")
    if not _finite(report.get("fit_seconds")) or report.get("fit_seconds", -1) < 0:
        bad.append("fit_seconds")

    # Stable de-duplication makes diagnostics compact and deterministic.
    bad = list(dict.fromkeys(bad))
    return (not bad), ("ok" if not bad else "failed checks: " + ",".join(bad))


def task_status(task: dict) -> tuple[str, str]:
    report = REPO / task["out_dir"] / "report.json"
    if not report.exists():
        return "pending", "no report.json"
    valid, reason = validate_report(report, task)
    return ("done", reason) if valid else ("invalid", reason)


def next_run_id(task: dict) -> str:
    state = REPO / task["out_dir"] / "pysr_state"
    for number in range(1000):
        if not (state / f"run_{number}").exists():
            return f"run_{number}"
    return f"run_{int(time.time())}"


def runner_argv(task: dict) -> list[str]:
    return [*task["argv"], "--pysr-run-id", next_run_id(task)]


# ---------------------------------------------------------------------------
# Persistent worker implementation.
# ---------------------------------------------------------------------------
def _run_one_in_process(task: dict) -> None:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    module = importlib.import_module("run_blind_sr")
    old_argv = sys.argv
    sys.argv = [str(RUNNER), *runner_argv(task)]
    try:
        module.main()
    finally:
        sys.argv = old_argv


def _worker(worker_id: int, tasks: list[dict], counter, result_q, stop_evt,
            opts: dict) -> None:
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    os.chdir(REPO)
    os.environ["JULIA_NUM_THREADS"] = str(opts["threads"])
    os.environ["PYTHONUNBUFFERED"] = "1"
    # Julia owns the search threads.  Keep Python numerical libraries from
    # multiplying worker x Julia x BLAS thread counts during post-hoc MI.
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS"):
        os.environ[name] = "1"

    if opts["worker_log_dir"]:
        log_path = Path(opts["worker_log_dir"]) / (
            f"precision_preprocess_pool_{opts['stamp']}_worker{worker_id}.log"
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        os.dup2(fd, 1)
        os.dup2(fd, 2)
        os.close(fd)
        sys.stdout = os.fdopen(1, "w", buffering=1)
        sys.stderr = os.fdopen(2, "w", buffering=1)

    started = time.time()
    import pysr  # noqa: PLC0415

    julia_version = None
    try:
        from pysr.julia_import import SymbolicRegression, jl  # noqa: F401, PLC0415

        julia_version = str(jl.seval("string(VERSION)"))
    except Exception as exc:  # noqa: BLE001
        print(
            f"[worker {worker_id}] warm-up import failed ({exc}); "
            "Julia will start inside the first fit",
            flush=True,
        )
    startup = time.time() - started
    result_q.put({
        "kind": "startup",
        "worker": worker_id,
        "seconds": startup,
        "pysr_version": pysr.__version__,
        "julia_version": julia_version,
        "threads": opts["threads"],
    })
    print(
        f"[worker {worker_id}] pysr {pysr.__version__} / julia "
        f"{julia_version} ready in {startup:.1f}s with "
        f"{opts['threads']} thread(s)",
        flush=True,
    )

    done = 0
    while not stop_evt.is_set():
        if opts["deadline"] is not None and time.monotonic() >= opts["deadline"]:
            break
        with counter.get_lock():
            index = counter.value
            if index >= len(tasks):
                break
            counter.value = index + 1
        task = tasks[index]
        task_started = time.time()
        print(
            f"\n[worker {worker_id}] === task {task['task_id']}: "
            f"{task['out_dir']} ===",
            flush=True,
        )
        record = {
            "kind": "task",
            "worker": worker_id,
            "started_utc": utc_now(),
            **{
                key: task[key]
                for key in (
                    "task_id", "run", "arm", "inner_loss", "latent", "seed",
                    "maxsize", "family", "out_dir",
                )
            },
        }
        try:
            _run_one_in_process(task)
            record["status"] = "ok"
        except BaseException as exc:  # noqa: BLE001
            record["status"] = "failed"
            record["error"] = f"{type(exc).__name__}: {exc}"
            print(
                f"[worker {worker_id}] task {task['task_id']} FAILED: "
                f"{record['error']}",
                flush=True,
            )
        record["seconds"] = time.time() - task_started
        if record["status"] == "ok":
            report_path = REPO / task["out_dir"] / "report.json"
            valid, reason = validate_report(report_path, task)
            if not valid:
                record["status"] = "invalid_report"
                record["error"] = reason
            else:
                try:
                    record["fit_seconds"] = json.loads(
                        report_path.read_text()
                    ).get("fit_seconds")
                except Exception:  # noqa: BLE001
                    pass
        record["finished_utc"] = utc_now()
        result_q.put(record)
        done += 1
        if opts["recycle_after"] and done >= opts["recycle_after"]:
            print(f"[worker {worker_id}] recycling after {done} tasks", flush=True)
            break
    result_q.put({"kind": "worker_exit", "worker": worker_id, "tasks": done})


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------
def parse_ids(spec: str | None, total: int = TOTAL_TASKS) -> set[int] | None:
    if not spec:
        return None
    ids: set[int] = set()
    for part in spec.replace(" ", "").split(","):
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            lo_i, hi_i = int(lo), int(hi)
            if hi_i < lo_i:
                raise SystemExit(f"[err] descending task-id range {part!r}")
            ids.update(range(lo_i, hi_i + 1))
        else:
            ids.add(int(part))
    bad = sorted(task_id for task_id in ids if not 0 <= task_id < total)
    if bad:
        raise SystemExit(f"[err] task ids out of range 0-{total - 1}: {bad}")
    return ids


def append_ledger(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def multiprocessing_start_method() -> str:
    """Use a fresh interpreter for Julia workers on macOS.

    Forking a long-lived multiprocessing driver after its first worker
    generation is unsafe for Julia on macOS and can surface as GC corruption
    in recycled workers. Linux keeps the lower-overhead fork path.
    """
    return "spawn" if platform.system() == "Darwin" else "fork"


def make_parser() -> argparse.ArgumentParser:
    cpu = os.cpu_count() or 1
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--task-ids", default=None,
        help="Subset such as '0-54,110,220' from the global 0-329 matrix.",
    )
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument(
        "--threads", type=int, default=None,
        help=f"Julia threads per worker (default cpu/workers; cpu={cpu}).",
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--time-budget-minutes", type=float, default=None,
        help="Start no new task after this many wall-clock minutes.",
    )
    parser.add_argument(
        "--smoke", default=None, metavar="TAG",
        help="Use 500 rows, one iteration, and an isolated smoke namespace.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--ledger", default=DEFAULT_LEDGER)
    parser.add_argument("--worker-log-dir", default=DEFAULT_LOG_DIR)
    parser.add_argument("--no-worker-logs", action="store_true")
    parser.add_argument("--recycle-after", type=int, default=None)
    parser.add_argument("--max-consecutive-failures", type=int, default=3)
    return parser


def main() -> int:
    args = make_parser().parse_args()
    cpu = os.cpu_count() or 1
    if args.workers < 1:
        raise SystemExit("[err] --workers must be >= 1")
    if args.threads is not None and args.threads < 1:
        raise SystemExit("[err] --threads must be >= 1")
    if args.limit is not None and args.limit < 0:
        raise SystemExit("[err] --limit must be >= 0")
    if args.time_budget_minutes is not None and args.time_budget_minutes <= 0:
        raise SystemExit("[err] --time-budget-minutes must be > 0")
    if args.recycle_after is not None and args.recycle_after < 1:
        raise SystemExit("[err] --recycle-after must be >= 1")
    if args.max_consecutive_failures < 1:
        raise SystemExit("[err] --max-consecutive-failures must be >= 1")
    if args.smoke and not SAFE_TAG.fullmatch(args.smoke):
        raise SystemExit(
            "[err] --smoke tag must contain only letters, digits, '.', '_' or '-'"
        )

    os.chdir(REPO)
    threads = args.threads or max(1, cpu // args.workers)
    wanted = parse_ids(args.task_ids)
    tasks: list[dict] = []
    counts = {"done": 0, "pending": 0, "invalid": 0, "outside_filter": 0}
    invalid: list[tuple[dict, str]] = []
    for task in enumerate_tasks(args.smoke):
        if wanted is not None and task["task_id"] not in wanted:
            counts["outside_filter"] += 1
            continue
        status, reason = task_status(task)
        counts[status] += 1
        if status == "pending":
            tasks.append(task)
        elif status == "invalid":
            invalid.append((task, reason))

    print(f"[pool] repo={REPO}")
    print(
        f"[pool] host={socket.gethostname()} cpus={cpu} "
        f"workers={args.workers} threads/worker={threads}"
    )
    print(
        f"[pool] python={platform.python_version()}"
        + (f" smoke={args.smoke}" if args.smoke else "")
    )
    print(
        f"[pool] precision/preprocess: {counts['done']}/{TOTAL_TASKS} complete, "
        f"{counts['pending']} pending, {counts['invalid']} invalid"
        + (
            f", {counts['outside_filter']} outside --task-ids"
            if counts["outside_filter"] else ""
        )
    )
    if args.workers * threads > cpu:
        print(
            f"[pool] WARNING workers*threads={args.workers * threads} exceeds "
            f"reported cpus={cpu}"
        )
    for task, reason in invalid:
        print(
            f"[pool] INVALID task {task['task_id']} {task['out_dir']}: {reason}"
        )
    if invalid:
        print(
            "[pool] refusing to overwrite invalid reports; inspect or move them "
            "out of the campaign namespace first"
        )
        return 2

    if args.limit is not None:
        tasks = tasks[:args.limit]
    if args.dry_run:
        for task in tasks:
            print(
                f"[dry-run] {task['task_id']:>3} {task['arm']:<16} "
                f"{task['family']:<11} {task['out_dir']}"
            )
        print(f"[dry-run] {len(tasks)} task(s) would run")
        return 0
    if not tasks:
        print("[pool] nothing to do")
        return 0

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ledger = Path(args.ledger)
    start_method = multiprocessing_start_method()
    ctx = mp.get_context(start_method)
    result_q = ctx.Queue()
    stop_evt = ctx.Event()
    counter = ctx.Value("i", 0)
    t_start = time.monotonic()
    deadline = (
        t_start + args.time_budget_minutes * 60.0
        if args.time_budget_minutes is not None else None
    )
    opts = {
        "threads": threads,
        "stamp": stamp,
        "worker_log_dir": None if args.no_worker_logs else args.worker_log_dir,
        "recycle_after": args.recycle_after,
        "deadline": deadline,
    }
    append_ledger(ledger, {
        "kind": "session",
        "utc": utc_now(),
        "stamp": stamp,
        "host": socket.gethostname(),
        "cpus": cpu,
        "workers": args.workers,
        "threads_per_worker": threads,
        "multiprocessing_start_method": start_method,
        "blas_threads_per_worker": 1,
        "queued": len(tasks),
        "task_ids": [task["task_id"] for task in tasks],
        "smoke": args.smoke,
        "time_budget_minutes": args.time_budget_minutes,
        "python": platform.python_version(),
        "summary": counts,
    })

    interrupted = {"flag": False}
    procs: list[mp.Process] = []

    def request_stop(signum, _frame):
        if interrupted["flag"]:
            print("\n[pool] second signal: terminating workers now")
            for proc in procs:
                proc.terminate()
            return
        interrupted["flag"] = True
        stop_evt.set()
        print(
            f"\n[pool] signal {signum}: finishing running task(s), then "
            "stopping; re-run the same command to resume"
        )

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)

    def spawn(worker_id: int):
        proc = ctx.Process(
            target=_worker,
            name=f"precision-pool-w{worker_id}",
            args=(worker_id, tasks, counter, result_q, stop_evt, opts),
        )
        proc.daemon = False
        proc.start()
        procs.append(proc)
        return proc

    worker_count = min(args.workers, len(tasks))
    live = {worker_id: spawn(worker_id) for worker_id in range(worker_count)}
    if opts["worker_log_dir"]:
        print(
            f"[pool] worker output -> {opts['worker_log_dir']}/"
            f"precision_preprocess_pool_{stamp}_worker*.log"
        )

    completed = failed = abnormal_workers = 0
    consecutive_failures = 0
    while live:
        try:
            record = result_q.get(timeout=1.0)
        except queue.Empty:
            for worker_id, proc in list(live.items()):
                if not proc.is_alive():
                    proc.join(timeout=1)
                    live.pop(worker_id)
                    if proc.exitcode not in (0, None):
                        abnormal_workers += 1
                        print(
                            f"[pool] worker {worker_id} exited unexpectedly "
                            f"with code {proc.exitcode}"
                        )
                        stop_evt.set()
            if deadline is not None and time.monotonic() >= deadline:
                stop_evt.set()
            continue

        kind = record.pop("kind")
        if kind == "startup":
            append_ledger(ledger, {
                "utc": utc_now(), "stamp": stamp, "kind": "startup", **record,
            })
            print(
                f"[pool] worker {record['worker']} startup {record['seconds']:.1f}s "
                f"(pysr {record['pysr_version']}, julia "
                f"{record.get('julia_version')})"
            )
            continue
        if kind == "worker_exit":
            worker_id = record["worker"]
            proc = live.pop(worker_id, None)
            if proc is not None:
                proc.join(timeout=30)
            if (
                args.recycle_after
                and not stop_evt.is_set()
                and counter.value < len(tasks)
            ):
                new_id = max([*live, worker_id]) + 1
                live[new_id] = spawn(new_id)
            continue

        record.update({"stamp": stamp, "kind": "task"})
        append_ledger(ledger, record)
        if record["status"] == "ok":
            completed += 1
            consecutive_failures = 0
        else:
            failed += 1
            consecutive_failures += 1
        elapsed = time.monotonic() - t_start
        left = len(tasks) - completed - failed
        rate = elapsed / max(completed + failed, 1)
        print(
            f"[pool] {record['status']:>14} task {record['task_id']:>3} in "
            f"{record['seconds']:.0f}s | done {completed} failed {failed} "
            f"left {left} | eta {left * rate / 60:.0f} min"
        )
        if consecutive_failures >= args.max_consecutive_failures:
            print(
                f"[pool] {consecutive_failures} consecutive failures; stopping "
                "so the cause can be inspected"
            )
            stop_evt.set()
        if deadline is not None and time.monotonic() >= deadline:
            stop_evt.set()

    for proc in procs:
        proc.join(timeout=60)
    total_minutes = (time.monotonic() - t_start) / 60.0
    append_ledger(ledger, {
        "kind": "session_end",
        "utc": utc_now(),
        "stamp": stamp,
        "completed": completed,
        "failed": failed,
        "abnormal_workers": abnormal_workers,
        "minutes": total_minutes,
        "interrupted": interrupted["flag"],
        "time_budget_reached": (
            deadline is not None and time.monotonic() >= deadline
        ),
    })
    print(
        f"[pool] session done: {completed} completed, {failed} failed, "
        f"{abnormal_workers} abnormal worker(s), {total_minutes:.1f} min wall"
    )
    if interrupted["flag"]:
        return 130
    return 1 if failed or abnormal_workers else 0


if __name__ == "__main__":
    sys.exit(main())
