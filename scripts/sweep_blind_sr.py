#!/usr/bin/env python
"""Plan and track a PySR hyperparameter sweep of the all-params blind-SR run.

The unit of work is one run_blind_sr.py invocation (one hyperparameter config
x one latent x one PySR seed). A sweep spec (JSON, see hpc/sweeps/) declares a
baseline config — the study protocol: niterations=200, populations=15,
maxsize=20, PySR defaults otherwise — plus axes of alternative values, expanded
either one-factor-at-a-time around the baseline (``mode: star``) or as a full
cartesian product (``mode: grid``). Axis keys are either the dedicated
run_blind_sr.py flags (niterations, populations, maxsize) or any other
PySRRegressor kwarg (population_size, ncycles_per_iteration, parsimony, ...),
which are routed through ``--pysr-extra``.

    # 1. expand the spec into a manifest + task table, print the sbatch line
    python scripts/sweep_blind_sr.py plan --spec hpc/sweeps/allparams_hp_v1.json

    # 2. submit (command printed by `plan`)
    sbatch --array=0-<N-1>%16 hpc/slurm_hpsweep_sr.sh <sweep-dir>

    # 3. check progress / get the resubmit array for missing runs
    python scripts/sweep_blind_sr.py status --spec hpc/sweeps/allparams_hp_v1.json

    # 4. consolidate into experiments/hpsweep_<name>_<run>.{md,json}
    python scripts/consolidate_hp_sweep.py --sweep-dir <sweep-dir>

Everything is idempotent: outputs are keyed by config_id/latent/seed (never by
array index), completed runs are skipped on resubmission, and re-planning an
unchanged spec rewrites identical files.
"""
import argparse
import itertools
import json
import sys
from pathlib import Path

# Keys handled by dedicated run_blind_sr.py flags (everything else in an axis
# goes through --pysr-extra).
CORE_KEYS = ("niterations", "populations", "maxsize")

# Kwargs owned by run_blind_sr.py itself — sweeping them would silently break
# the protocol (seed handling, loss, output layout), so refuse them as axes.
FORBIDDEN_KEYS = {
    "random_state", "parallelism", "loss_function", "elementwise_loss",
    "output_directory", "run_id", "progress", "verbosity", "turbo",
    "deterministic", "binary_operators", "unary_operators", "batching",
}

# Short axis labels for config ids / result dir names.
ABBREV = {
    "niterations": "ni", "populations": "pop", "maxsize": "ms",
    "population_size": "ps", "ncycles_per_iteration": "ncyc",
    "parsimony": "par", "adaptive_parsimony_scaling": "aps",
    "tournament_selection_n": "tsn", "fraction_replaced": "fr",
    "weight_optimize": "wopt", "topn": "topn",
}

TSV_COLS = ["idx", "config_id", "latent", "seed", "niterations", "populations",
            "maxsize", "extra_json", "run_dir", "inputs", "n_samples", "out_dir"]


def _fmt_val(v) -> str:
    return f"{v:g}" if isinstance(v, float) else str(v)


def _label(cfg: dict, baseline: dict, axis_order: list) -> str:
    """Compact human label: the keys on which cfg differs from baseline."""
    diffs = []
    for key in axis_order:
        b = baseline["extra"].get(key) if key not in CORE_KEYS else baseline[key]
        c = cfg["extra"].get(key) if key not in CORE_KEYS else cfg[key]
        if c != b:
            diffs.append(f"{ABBREV.get(key, key)}{_fmt_val(c)}")
    return "_".join(diffs) if diffs else "baseline"


def _apply(baseline: dict, assignment: dict) -> dict:
    """Baseline config with axis assignment {key: value} applied."""
    cfg = {k: baseline[k] for k in CORE_KEYS}
    cfg["extra"] = dict(baseline.get("extra") or {})
    for key, val in assignment.items():
        if key in CORE_KEYS:
            cfg[key] = val
        else:
            cfg["extra"][key] = val
    return cfg


def expand_configs(spec: dict) -> list:
    """Spec -> ordered list of unique configs (baseline first for star mode)."""
    baseline = dict(spec["baseline"])
    baseline.setdefault("extra", {})
    axes = spec.get("axes") or {}
    axis_order = list(axes)
    for key in axes:
        if key in FORBIDDEN_KEYS:
            raise SystemExit(f"axis '{key}' is managed by run_blind_sr.py and cannot be swept")
    mode = spec.get("mode", "star")

    raw = []
    if mode == "star":
        raw.append(_apply(baseline, {}))
        for key, values in axes.items():
            for v in values:
                raw.append(_apply(baseline, {key: v}))
    elif mode == "grid":
        for combo in itertools.product(*axes.values()):
            raw.append(_apply(baseline, dict(zip(axes, combo))))
    else:
        raise SystemExit(f"unknown mode '{mode}' (star|grid)")

    configs, seen = [], set()
    for cfg in raw:
        key = json.dumps(cfg, sort_keys=True)
        if key in seen:
            continue  # e.g. a star axis value equal to the baseline
        seen.add(key)
        label = _label(cfg, baseline, axis_order)
        safe = "".join(ch if (ch.isalnum() or ch in "_.-") else "-" for ch in label)
        configs.append({"config_id": f"c{len(configs):02d}_{safe}", "label": label, **cfg})
    return configs


def build_tasks(spec: dict, configs: list, sweep_dir: Path) -> list:
    tasks = []
    for cfg in configs:
        for latent in spec["latents"]:
            for seed in spec["seeds"]:
                out_dir = sweep_dir / cfg["config_id"] / f"z{latent}_seed{seed}"
                tasks.append({"idx": len(tasks), "config_id": cfg["config_id"],
                              "latent": latent, "seed": seed,
                              "out_dir": str(out_dir)})
    return tasks


def rough_seconds(cfg: dict) -> float:
    """Very rough per-run walltime at 16 threads, calibrated on the study's
    allparams runs: ~330 s at (ni=200, pop=15, ps=27, ncyc=380, ms=20) and
    ~0.68x that at ms=10. Linear in evolution work, affine in maxsize."""
    extra = cfg.get("extra") or {}
    work = (cfg["niterations"] / 200) * (cfg["populations"] / 15) \
        * (extra.get("population_size", 27) / 27) \
        * (extra.get("ncycles_per_iteration", 380) / 380)
    f_ms = 0.35 + 0.65 * cfg["maxsize"] / 20
    return 330.0 * work * f_ms


def sweep_dir_of(spec: dict) -> Path:
    run_name = Path(spec["run_dir"]).name
    return Path("results") / run_name / f"hpsweep_{spec['name']}"


def load_spec(path: str) -> dict:
    spec = json.loads(Path(path).read_text())
    for field in ("name", "run_dir", "latents", "seeds", "inputs", "baseline"):
        if field not in spec:
            raise SystemExit(f"spec {path} missing required field '{field}'")
    return spec


def load_manifest(sweep_dir: Path) -> dict:
    path = Path(sweep_dir) / "manifest.json"
    if not path.exists():
        raise SystemExit(f"{path} not found — run `sweep_blind_sr.py plan` first")
    return json.loads(path.read_text())


def write_tsv(spec: dict, tasks: list, configs: list, path: Path) -> None:
    by_id = {c["config_id"]: c for c in configs}
    lines = ["\t".join(TSV_COLS)]
    for t in tasks:
        cfg = by_id[t["config_id"]]
        extra_json = json.dumps(cfg["extra"], sort_keys=True, separators=(",", ":"))
        lines.append("\t".join(str(x) for x in (
            t["idx"], t["config_id"], t["latent"], t["seed"],
            cfg["niterations"], cfg["populations"], cfg["maxsize"], extra_json,
            spec["run_dir"], " ".join(spec["inputs"]),
            spec.get("n_samples", 5000), t["out_dir"])))
    path.write_text("\n".join(lines) + "\n")


def compact_ranges(idxs: list) -> str:
    """[0,1,2,5,7,8] -> '0-2,5,7-8' (sbatch --array syntax)."""
    parts, i = [], 0
    while i < len(idxs):
        j = i
        while j + 1 < len(idxs) and idxs[j + 1] == idxs[j] + 1:
            j += 1
        parts.append(str(idxs[i]) if i == j else f"{idxs[i]}-{idxs[j]}")
        i = j + 1
    return ",".join(parts)


def build_manifest(spec: dict, sweep_dir: Path, spec_path: str = "") -> dict:
    configs = expand_configs(spec)
    tasks = build_tasks(spec, configs, sweep_dir)
    return {"sweep_name": spec["name"], "spec_path": str(spec_path),
            "run_dir": spec["run_dir"], "run_name": Path(spec["run_dir"]).name,
            "spec": spec, "configs": configs, "tasks": tasks,
            "n_configs": len(configs), "n_tasks": len(tasks)}


def cmd_plan(args) -> None:
    spec = load_spec(args.spec)
    sweep_dir = sweep_dir_of(spec)
    manifest = build_manifest(spec, sweep_dir, spec_path=args.spec)
    configs, tasks = manifest["configs"], manifest["tasks"]

    man_path = sweep_dir / "manifest.json"
    if man_path.exists():
        old = json.loads(man_path.read_text())
        if {k: old.get(k) for k in ("configs", "tasks", "spec")} != \
           {k: manifest[k] for k in ("configs", "tasks", "spec")} and not args.force:
            raise SystemExit(
                f"{man_path} exists with a different plan. Outputs are keyed by "
                "config_id/latent/seed, so re-planning is safe iff unchanged "
                "config_ids still mean the same config. Re-run with --force to "
                "overwrite the manifest.")

    sweep_dir.mkdir(parents=True, exist_ok=True)
    man_path.write_text(json.dumps(manifest, indent=2))
    write_tsv(spec, tasks, configs, sweep_dir / "tasks.tsv")

    n_runs_per_cfg = len(spec["latents"]) * len(spec["seeds"])
    print(f"[plan] sweep '{spec['name']}' on {spec['run_dir']}  "
          f"(mode={spec.get('mode', 'star')}, latents={spec['latents']}, seeds={spec['seeds']})")
    print(f"[plan] {len(configs)} configs x {n_runs_per_cfg} runs = {len(tasks)} tasks "
          f"-> {sweep_dir}")
    total_s = 0.0
    print(f"\n  {'config_id':<28} {'ni':>4} {'pop':>4} {'ms':>3}  {'extra':<32} {'~min/run':>8}")
    for cfg in configs:
        est = rough_seconds(cfg)
        total_s += est * n_runs_per_cfg
        extra = json.dumps(cfg["extra"]) if cfg["extra"] else "-"
        print(f"  {cfg['config_id']:<28} {cfg['niterations']:>4} {cfg['populations']:>4} "
              f"{cfg['maxsize']:>3}  {extra:<32} {est / 60:>8.1f}")
    print(f"\n[plan] very rough total: {total_s / 3600:.1f} task-hours "
          f"({total_s * 16 / 3600:.0f} CPU-core-hours at 16 threads/task)")
    print(f"[plan] wrote {man_path}")
    print(f"[plan] wrote {sweep_dir / 'tasks.tsv'}")
    print("\nSubmit (throttle %16 optional):\n"
          f"  sbatch --array=0-{len(tasks) - 1}%16 hpc/slurm_hpsweep_sr.sh {sweep_dir}")


def cmd_status(args) -> None:
    sweep_dir = Path(args.sweep_dir) if args.sweep_dir else sweep_dir_of(load_spec(args.spec))
    manifest = load_manifest(sweep_dir)
    missing = []
    print(f"[status] sweep '{manifest['sweep_name']}' at {sweep_dir}")
    for cfg in manifest["configs"]:
        cfg_tasks = [t for t in manifest["tasks"] if t["config_id"] == cfg["config_id"]]
        done = [t for t in cfg_tasks if (Path(t["out_dir"]) / "report.json").exists()]
        missing += [t["idx"] for t in cfg_tasks if t not in done]
        marker = "done" if len(done) == len(cfg_tasks) else "...."
        print(f"  [{marker}] {cfg['config_id']:<28} {len(done)}/{len(cfg_tasks)}")
        if args.verbose:
            for t in cfg_tasks:
                if t["idx"] in missing:
                    print(f"           missing idx={t['idx']} z{t['latent']} seed{t['seed']}")
    missing.sort()
    print(f"[status] {len(manifest['tasks']) - len(missing)}/{len(manifest['tasks'])} reports present")
    if missing:
        print("\nSubmit the missing tasks:\n"
              f"  sbatch --array={compact_ranges(missing)} hpc/slurm_hpsweep_sr.sh {sweep_dir}")
    else:
        print("\nAll runs complete. Consolidate with:\n"
              f"  python scripts/consolidate_hp_sweep.py --sweep-dir {sweep_dir}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("plan", help="expand the spec, write manifest + tasks.tsv")
    sp.add_argument("--spec", required=True, help="Sweep spec JSON (see hpc/sweeps/).")
    sp.add_argument("--force", action="store_true",
                    help="Overwrite an existing manifest that differs from this plan.")
    sp.set_defaults(fn=cmd_plan)
    ss = sub.add_parser("status", help="report done/missing tasks, print resubmit line")
    g = ss.add_mutually_exclusive_group(required=True)
    g.add_argument("--spec", help="Sweep spec JSON (sweep dir derived from it).")
    g.add_argument("--sweep-dir", help="results/<run>/hpsweep_<name> directly.")
    ss.add_argument("--verbose", action="store_true", help="List each missing task.")
    ss.set_defaults(fn=cmd_status)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
