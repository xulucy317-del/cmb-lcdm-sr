#!/usr/bin/env python
"""Sham-input dilution control — R-P4 mechanism test.

Implements the rule frozen in docs/discovery_roadmap.md, "Post-closure
pre-registration (2026-08-13) — R-P4", rule 2. Written and committed before
any result of the new grid existed.

**What this settles that the support comparison cannot.** When a strict
subset beats all-6 at a matched budget, one can always object that the
dropped parameter did carry a little real information the search failed to
exploit. A sham column removes the objection: it is a permutation of a real
theta column (scripts/build_sham_inputs.py), so it carries a genuine
parameter's marginal — the identical multiset of values over the SR block —
and provably zero information about any latent. Appended as a 7th input
beside the full all-6 support, any deficit it causes is search dilution and
nothing else.

**Frozen rule.** Delta_sham = seed-paired M^(c<=10) of (all-6 + sham) minus
(all-6), where the all-6 baseline is results/<run>/allparams — same protocol
(ni200, pops15, ms20, n=5000), same 5 seeds, so the pairing is exact and the
baseline costs nothing. Dilution is **demonstrated** iff the pooled
Delta_sham (over the 3 donors x every latent) is negative by more than 1 SE,
per model. Per-latent and per-donor values are descriptive.

Also reported, descriptively: how often the search *spends complexity on the
sham* — the fraction of per-seed best-at-c<=10 forms whose expression
contains the sham symbol. A useless variable that gets used is dilution made
visible in the equations themselves.

Reads:  results/<run>/sham_control/<donor>/z*_seed*/report.json
        results/<run>/allparams/z*_seed*/report.json
Writes: experiments/sham_control_<run>.{md,json}

    python scripts/consolidate_sham_control.py --run lcdm_tt_beta3e-4
    python scripts/consolidate_sham_control.py --run lcdm_tt_ee_lowl
"""
import argparse
import json
import re
from pathlib import Path

import _bootstrap  # noqa: F401

import numpy as np

from consolidate_subsets_full import PRIMARY_CAP, best_at_cap

SEED_DIR = re.compile(r"^z(\d+)_seed(\d+)$")
SHAM_SYMBOL = "sham"


def load_dir(pattern_root: Path) -> dict:
    """(latent, seed) -> (mi, expr) at the primary cap, for one run directory."""
    out = {}
    for report in sorted(pattern_root.glob("z*_seed*/report.json")):
        m = SEED_DIR.match(report.parent.name)
        if not m:
            continue
        d = json.loads(report.read_text())
        out[(int(m.group(1)), int(m.group(2)))] = best_at_cap(
            d.get("all_equations") or [], PRIMARY_CAP)
    return out


def se_of(a: np.ndarray):
    return float(a.std(ddof=1) / np.sqrt(len(a))) if len(a) > 1 else float("nan")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", required=True)
    p.add_argument("--donors", nargs="+", default=["ob", "tau", "ns"])
    p.add_argument("--out-dir", default="experiments")
    args = p.parse_args()

    root = Path("results") / args.run
    baseline = load_dir(root / "allparams")
    if not baseline:
        raise SystemExit(f"no all-6 baseline under {root / 'allparams'}")

    out = {"run": args.run, "primary_cap": PRIMARY_CAP,
           "rule": "R-P4 rule 2 (docs/discovery_roadmap.md)",
           "baseline": "results/<run>/allparams (all-6, same protocol, same seeds)",
           "donors": {}, "per_latent": {}, "pooled": {},
           "generated_by": "scripts/consolidate_sham_control.py"}

    all_diffs, uses = [], []
    per_latent: dict = {}
    for donor in args.donors:
        cells = load_dir(root / "sham_control" / donor)
        if not cells:
            print(f"[warn] no cells for donor '{donor}' — skipping")
            continue
        diffs, donor_uses = [], []
        for (k, seed), (mi, expr) in sorted(cells.items()):
            base = baseline.get((k, seed))
            if base is None or mi is None or base[0] is None:
                continue
            d = mi - base[0]
            diffs.append(d)
            all_diffs.append(d)
            used = bool(expr) and SHAM_SYMBOL in expr
            donor_uses.append(used)
            uses.append(used)
            per_latent.setdefault(k, []).append(d)
        a = np.asarray(diffs, dtype=float)
        out["donors"][donor] = {
            "n": len(a), "mean_delta": float(a.mean()) if len(a) else None,
            "se": se_of(a) if len(a) else None,
            "frac_forms_using_sham": float(np.mean(donor_uses)) if donor_uses else None}
        print(f"[{donor}] n={len(a)} mean_delta={a.mean():+.4f} "
              f"sham-in-form={np.mean(donor_uses):.2f}" if len(a) else f"[{donor}] empty")

    for k, ds in sorted(per_latent.items()):
        a = np.asarray(ds, dtype=float)
        out["per_latent"][f"z{k}"] = {"n": len(a), "mean_delta": float(a.mean()),
                                      "se": se_of(a)}

    a = np.asarray(all_diffs, dtype=float)
    if len(a):
        mean, se = float(a.mean()), se_of(a)
        out["pooled"] = {
            "n": len(a), "mean_delta": mean, "se": se,
            "frac_forms_using_sham": float(np.mean(uses)),
            # Frozen predicate: negative by more than 1 SE.
            "dilution_demonstrated": bool(np.isfinite(se) and mean < -se)}
        print(f"[pooled] n={len(a)} Delta_sham={mean:+.4f} +/- {se:.4f} -> "
              f"dilution_demonstrated={out['pooled']['dilution_demonstrated']}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"sham_control_{args.run}.json").write_text(json.dumps(out, indent=1) + "\n")
    (out_dir / f"sham_control_{args.run}.md").write_text(render_md(out))
    print(f"[write] {out_dir}/sham_control_{args.run}.{{md,json}}")


def render_md(out: dict) -> str:
    C = out["primary_cap"]
    pooled = out.get("pooled") or {}
    L = [f"# Sham-input dilution control — `{out['run']}` (R-P4 rule 2)", "",
         "The all-6 blind SR rerun with one provably-irrelevant 7th input "
         "(a permutation of a real theta column: a genuine parameter's "
         "marginal, zero information about any latent). Baseline is "
         f"`{out['baseline']}`, so Delta_sham = M^(c<={C}) with sham minus "
         "without, paired by seed. Frozen predicate: dilution is demonstrated "
         "iff the pooled Delta_sham is negative by more than 1 SE.", ""]
    if pooled:
        verdict = ("**DEMONSTRATED**" if pooled["dilution_demonstrated"]
                   else "not demonstrated")
        L += [f"**Pooled Delta_sham = {pooled['mean_delta']:+.4f} +/- "
              f"{pooled['se']:.4f} nat** (n={pooled['n']}) -> {verdict}", "",
              f"Forms spending complexity on the sham symbol: "
              f"{pooled['frac_forms_using_sham']:.1%} of best-at-c<={C} forms.", ""]
    L += ["| donor | n | mean Delta | SE | forms using sham |", "|---|---:|---:|---:|---:|"]
    for donor, r in out["donors"].items():
        L.append(f"| {donor} | {r['n']} | {r['mean_delta']:+.4f} | {r['se']:.4f} | "
                 f"{r['frac_forms_using_sham']:.1%} |")
    L += ["", "| latent | n | mean Delta | SE |", "|---|---:|---:|---:|"]
    for z, r in out["per_latent"].items():
        L.append(f"| {z} | {r['n']} | {r['mean_delta']:+.4f} | {r['se']:.4f} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
