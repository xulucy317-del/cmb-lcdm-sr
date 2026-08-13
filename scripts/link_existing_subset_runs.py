#!/usr/bin/env python
"""Link already-completed full-protocol runs into the exhaustive subset sweep.

The exhaustive sweep (hpc/sweeps/subsets_full_*.json) asks for all 63 supports
x every latent x 5 seeds at the study protocol (ni200, pops15, ms20, 5000
samples). Two earlier campaigns already ran a subset of exactly that grid at
exactly that protocol:

* results/<run>/hpsweep_subsets_v1_finals — the Phase-4b finalist reruns, laid
  out under the same deterministic config ids (c00..c62) the sweep planner
  generates, so the mapping is the identity;
* results/<run>/allparams — the all-6 reference (config c62), which 4b
  deliberately skipped because it already existed.

Symlinking those run directories into the new sweep dir makes the SLURM
wrapper's "report.json present -> skip" check fire on them, so the array only
spends walltime on genuinely new (support, latent, seed) cells. Every donor's
protocol is verified against the sweep manifest before it is linked; a
mismatch is an error, never a silent reuse.

    python scripts/link_existing_subset_runs.py --spec hpc/sweeps/subsets_full_tt.json
    python scripts/link_existing_subset_runs.py --spec hpc/sweeps/subsets_full_ee.json --apply
"""
import argparse
import csv
import json
import os
from pathlib import Path

import _bootstrap  # noqa: F401

from cmb_lcdm_sr.sr import INPUT_ALIASES  # noqa: F401  (import-time protocol check)

PROTOCOL_KEYS = ("niterations", "populations", "maxsize")


def donor_runs(run_name: str):
    """Yield (target_relpath_parts, donor_dir) candidates for one run."""
    finals = Path("results") / run_name / "hpsweep_subsets_v1_finals"
    for report in sorted(finals.glob("*/*/report.json")):
        cell = report.parent
        yield (cell.parent.name, cell.name), cell
    allparams = Path("results") / run_name / "allparams"
    for report in sorted(allparams.glob("z*_seed*/report.json")):
        cell = report.parent
        d = json.loads(report.read_text())
        if len(d.get("input_labels", [])) != 6 or d.get("extra_inputs"):
            continue
        seed = d["pysr_kwargs"]["random_state"]
        yield ("c62_S-ob-oc-H0-tau-As-ns", f"z{d['target_label'][1:]}_seed{seed}"), cell


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--spec", required=True, help="Sweep spec (hpc/sweeps/subsets_full_*.json).")
    p.add_argument("--apply", action="store_true", help="Create the links (default: dry run).")
    args = p.parse_args()

    spec = json.loads(Path(args.spec).read_text())
    run_name = Path(spec["run_dir"]).name
    sweep_dir = Path("results") / run_name / f"hpsweep_{spec['name']}"
    tasks_tsv = sweep_dir / "tasks.tsv"
    if not tasks_tsv.exists():
        raise SystemExit(f"{tasks_tsv} not found — run sweep_blind_sr.py plan first")
    want = {(r["config_id"], Path(r["out_dir"]).name)
            for r in csv.DictReader(tasks_tsv.open(), delimiter="\t")}
    protocol = {k: spec["baseline"][k] for k in PROTOCOL_KEYS}

    linked, skipped, mismatched = [], 0, []
    for key, donor in donor_runs(run_name):
        if key not in want:
            continue
        target = sweep_dir / key[0] / key[1]
        if (target / "report.json").exists():
            skipped += 1
            continue
        d = json.loads((donor / "report.json").read_text())
        got = {k: d["pysr_kwargs"][k] for k in PROTOCOL_KEYS}
        if got != protocol or d.get("n_samples") != spec["n_samples"]:
            mismatched.append((str(donor), got, d.get("n_samples")))
            continue
        linked.append((target, donor))

    for target, donor in linked:
        if not args.apply:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            target.unlink()
        target.symlink_to(os.path.relpath(donor, target.parent), target_is_directory=True)

    verb = "linked" if args.apply else "would link"
    print(f"[link] {run_name}: {verb} {len(linked)} cells, {skipped} already present, "
          f"{len(mismatched)} protocol mismatches, {len(want)} tasks total")
    for donor, got, n in mismatched:
        print(f"  [mismatch] {donor}: {got} n_samples={n}")
    if args.apply:
        record = sweep_dir / "reused_runs.json"
        record.write_text(json.dumps(
            {"protocol": protocol, "n_samples": spec["n_samples"],
             "reused": [{"cell": str(t.relative_to(sweep_dir)),
                         "donor": str(d)} for t, d in linked]}, indent=2) + "\n")
        print(f"[link] provenance -> {record}")
    else:
        print("[link] dry run — pass --apply to create the symlinks")


if __name__ == "__main__":
    main()
