#!/usr/bin/env python
"""Exhaustive support under a budget-matched readout — R-P4 consolidation.

Implements the rules frozen in docs/discovery_roadmap.md, "Post-closure
pre-registration (2026-08-13) — R-P4". Written and committed *before* any
full-protocol result of the new grid existed, so nothing here can have been
tuned to what the data shows.

**Why a second readout.** Phase 4 scored supports by Î_S = the front-max val
MI. hp_v1 showed front-max MI is a capacity dial — every capacity knob raises
it — so Î_S is biased toward larger supports by construction and cannot see
*search dilution*: extra variables enlarge the mutation space at fixed
iteration budget, and a spurious variable that shaves train loss consumes
complexity the true structure needs. That damage only shows at a matched
complexity budget.

**Frozen readout.** M_S^(C) = mean over the 5 PySR seeds of (max val MI over
front equations of complexity <= C). Primary C = 10 (hp_v1's pre-existing
aim-aligned metric, defined before this experiment); C in {6, 14, 20}
descriptive only. Supports share the seed set, so every comparison is paired
by seed and SE is the standard error of the 5 paired differences.

**Frozen decision rule (two-stage).** Latent k is *dilution-affected* iff
  (a) selection: S+ = argmax over the 62 strict subsets of M_S^(10) on
      T0-val — winner's-cursed over 62 candidates, so it carries no claim;
  (b) confirmation: the per-seed best-at-c<=10 forms of S+ and of all-6 are
      re-scored by full gmm-mi on T2 (rows 25k-50k, confirmatory-only per
      src/cmb_lcdm_sr/tiers.py) and the paired T2 mean difference exceeds
      +1 SE.
Stage (b) is what carries the claim. A null result — no latent confirming —
is a registered outcome, not a failure.

Reads:  results/<run>/hpsweep_subsets_full/{manifest.json, c*/z*_seed*/report.json}
        models/<run>/analysis/encoder_means_test.npy, data/theta.npy
Writes: experiments/subsets_full_<run>.{md,json}

    python scripts/consolidate_subsets_full.py --run lcdm_tt_beta3e-4
    python scripts/consolidate_subsets_full.py --run lcdm_tt_ee_lowl
"""
import argparse
import json
import re
from pathlib import Path

import _bootstrap  # noqa: F401

import numpy as np

from consolidate_allparams import expr_of
from cmb_lcdm_sr import semantics, tiers
from cmb_lcdm_sr.mi import mutual_information_gmm

SEED_DIR = re.compile(r"^z(\d+)_seed(\d+)$")
FULL_POOL = ["omega_b", "omega_cdm", "H0", "tau", "A_s", "n_s"]
CAPS = (6, 10, 14, 20)
PRIMARY_CAP = 10
# Phase-4 N-G2 attention flags: S* not screen-recurrent. Their content is a
# statement about the two-tier screen design, which this grid removes.
N_G2 = {("lcdm_tt_beta3e-4", 0), ("lcdm_tt_ee_lowl", 3), ("lcdm_tt_ee_lowl", 4)}
MAX_SAMPLES_MI = 5000


def mi_of(entry: dict) -> float:
    """mi_val as a float, with every abstention mapped to nan.

    A front entry that fails to evaluate carries `mi_val: null` (an
    `eval_error` is recorded beside it) rather than the nan that a form
    evaluating to a non-finite value gets, so the two abstention paths need
    the same treatment here: no valid MI, hence excluded.
    """
    v = entry.get("mi_val")
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    return float("nan")


def best_at_cap(front: list, cap: int):
    """(mi_val, expression) of the best front entry with complexity <= cap."""
    sub = [e for e in front if e.get("complexity", 10**9) <= cap
           and np.isfinite(mi_of(e))]
    if not sub:
        return None, None
    row = max(sub, key=mi_of)
    return mi_of(row), expr_of(row)


def load_cells(sweep_dir: Path) -> dict:
    """(latent, support) -> {seed: {cap: (mi, expr)}}, support as a tuple."""
    cells: dict = {}
    for report in sorted(sweep_dir.glob("*/z*_seed*/report.json")):
        m = SEED_DIR.match(report.parent.name)
        if not m:
            continue
        d = json.loads(report.read_text())
        if d.get("extra_inputs"):
            continue  # sham runs never live here, but never mix them in
        latent, seed = int(m.group(1)), int(m.group(2))
        support = tuple(d["input_labels"])
        front = d.get("all_equations") or []
        cells.setdefault((latent, support), {})[seed] = {
            c: best_at_cap(front, c) for c in CAPS}
    return cells


def paired(cells: dict, latent: int, a: tuple, b: tuple, cap: int):
    """Seed-paired (mean_diff, se, n) of M_a^(cap) − M_b^(cap)."""
    sa, sb = cells.get((latent, a), {}), cells.get((latent, b), {})
    diffs = []
    for seed in sorted(set(sa) & set(sb)):
        va, vb = sa[seed][cap][0], sb[seed][cap][0]
        if va is not None and vb is not None:
            diffs.append(va - vb)
    if not diffs:
        return None, None, 0
    d = np.asarray(diffs, dtype=float)
    se = float(d.std(ddof=1) / np.sqrt(len(d))) if len(d) > 1 else float("nan")
    return float(d.mean()), se, len(d)


def mean_over_seeds(cells: dict, latent: int, support: tuple, cap: int):
    vals = [v[cap][0] for v in cells.get((latent, support), {}).values()
            if v[cap][0] is not None]
    if not vals:
        return None, None, 0
    a = np.asarray(vals, dtype=float)
    se = float(a.std(ddof=1) / np.sqrt(len(a))) if len(a) > 1 else float("nan")
    return float(a.mean()), se, len(a)


def t2_mi(expr: str, theta_t2: np.ndarray, mu_t2: np.ndarray, seed: int = 0):
    """Full gmm-mi between f(theta) and the latent mean, on T2 rows."""
    if not expr:
        return None
    f = semantics.evaluate_on_theta(expr, theta_t2)
    ok = np.isfinite(f) & np.isfinite(mu_t2)
    if ok.mean() < 0.5 or ok.sum() < 256 or np.ptp(f[ok]) == 0:
        return None
    mi, _ = mutual_information_gmm(f[ok].reshape(-1, 1), mu_t2[ok].reshape(-1, 1),
                                   return_uncertainty=True,
                                   max_samples=MAX_SAMPLES_MI, seed=seed)
    v = float(mi[0, 0])
    return v if np.isfinite(v) else None


def t2_confirm(cells, latent, s_plus, all6, theta_t2, mu_t2, cap):
    """Paired T2 re-scoring of the per-seed best-at-cap forms (frozen stage b)."""
    sa, sb = cells.get((latent, s_plus), {}), cells.get((latent, all6), {})
    rows, diffs = [], []
    for seed in sorted(set(sa) & set(sb)):
        ea, eb = sa[seed][cap][1], sb[seed][cap][1]
        va, vb = t2_mi(ea, theta_t2, mu_t2, seed), t2_mi(eb, theta_t2, mu_t2, seed)
        rows.append({"seed": seed, "t2_mi_s_plus": va, "t2_mi_all6": vb,
                     "expr_s_plus": ea, "expr_all6": eb})
        if va is not None and vb is not None:
            diffs.append(va - vb)
    if not diffs:
        return {"per_seed": rows, "mean_diff": None, "se": None, "n": 0,
                "confirmed": False}
    d = np.asarray(diffs, dtype=float)
    se = float(d.std(ddof=1) / np.sqrt(len(d))) if len(d) > 1 else float("nan")
    mean = float(d.mean())
    return {"per_seed": rows, "mean_diff": mean, "se": se, "n": len(d),
            "confirmed": bool(np.isfinite(se) and mean > se)}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", required=True, help="Run name, e.g. lcdm_tt_beta3e-4.")
    p.add_argument("--sweep", default="subsets_full")
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--out-dir", default="experiments")
    p.add_argument("--skip-t2", action="store_true",
                   help="Emit the T0-val table only (stage a); no claim without stage b.")
    args = p.parse_args()

    sweep_dir = Path("results") / args.run / f"hpsweep_{args.sweep}"
    cells = load_cells(sweep_dir)
    if not cells:
        raise SystemExit(f"no cells under {sweep_dir}")
    latents = sorted({k[0] for k in cells})
    all6 = tuple(FULL_POOL)

    theta_t2 = tiers.tier_theta(args.dataset_dir, tiers.T2)
    means = np.load(Path("models") / args.run / "analysis" / "encoder_means_test.npy")

    manifest = sweep_dir / "manifest.json"
    n_tasks = json.loads(manifest.read_text()).get("n_tasks") if manifest.exists() else None
    out = {"run": args.run, "sweep": args.sweep, "primary_cap": PRIMARY_CAP,
           "caps": list(CAPS), "rule": "R-P4 (docs/discovery_roadmap.md)",
           "coverage": {"n_tasks": n_tasks, "n_cells": len(cells)},
           "latents": {}, "generated_by": "scripts/consolidate_subsets_full.py"}

    for k in latents:
        supports = sorted({s for (kk, s) in cells if kk == k}, key=lambda s: (len(s), s))
        entries = []
        for s in supports:
            row = {"S": list(s), "size": len(s)}
            for c in CAPS:
                mean, se, n = mean_over_seeds(cells, k, s, c)
                row[f"M_c{c}"] = mean
                row[f"M_c{c}_se"] = se
                row[f"n_seeds_c{c}"] = n
            dm, dse, dn = paired(cells, k, s, all6, PRIMARY_CAP)
            row.update({"paired_vs_all6": dm, "paired_se": dse, "paired_n": dn})
            per_seed = cells[(k, s)]
            row["exprs_at_primary"] = {str(sd): v[PRIMARY_CAP][1]
                                       for sd, v in sorted(per_seed.items())}
            entries.append(row)

        strict = [e for e in entries if tuple(e["S"]) != all6
                  and e[f"M_c{PRIMARY_CAP}"] is not None]
        s_plus = max(strict, key=lambda e: e[f"M_c{PRIMARY_CAP}"])["S"] if strict else None

        staircase = {}
        for e in entries:
            v = e[f"M_c{PRIMARY_CAP}"]
            if v is None:
                continue
            cur = staircase.get(e["size"])
            if cur is None or v > cur["M"]:
                staircase[e["size"]] = {"M": v, "S": e["S"]}

        rec = {"supports_scored": len(entries), "staircase": staircase,
               "all6": {f"M_c{c}": mean_over_seeds(cells, k, all6, c)[0] for c in CAPS},
               "s_plus": s_plus, "entries": entries,
               "n_g2_flagged": (args.run, k) in N_G2}
        if s_plus and not args.skip_t2:
            rec["t2_confirmation"] = t2_confirm(cells, k, tuple(s_plus), all6,
                                                theta_t2, means[tiers.T2, k],
                                                PRIMARY_CAP)
            rec["dilution_affected"] = rec["t2_confirmation"]["confirmed"]
        else:
            rec["dilution_affected"] = None
        out["latents"][f"z{k}"] = rec
        print(f"[z{k}] supports={len(entries)} S+={s_plus} "
              f"dilution_affected={rec['dilution_affected']}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"subsets_full_{args.run}.json").write_text(json.dumps(out, indent=1) + "\n")
    (out_dir / f"subsets_full_{args.run}.md").write_text(render_md(out))
    print(f"[write] {out_dir}/subsets_full_{args.run}.{{md,json}}")


def render_md(out: dict) -> str:
    C = out["primary_cap"]
    L = [f"# Exhaustive support, budget-matched — `{out['run']}` (R-P4)", "",
         "All 63 supports x 5 seeds at the study protocol (ni200, pops15, ms20), "
         f"scored by the frozen budget-matched readout M_S^(c<={C}) = mean over "
         "seeds of the best val MI on the front at complexity <= "
         f"{C}. Comparisons are seed-paired. S+ = argmax over the 62 strict "
         "subsets (selection, winner's-cursed); the claim is carried by the "
         "paired T2 confirmation, per docs/discovery_roadmap.md R-P4.", "",
         f"_Coverage: {out['coverage']['n_cells']} (latent, support) cells._", ""]
    for z, rec in out["latents"].items():
        flag = " — **N-G2 flagged in Phase 4**" if rec["n_g2_flagged"] else ""
        L += [f"## {z}{flag}", ""]
        stair = "  ".join(f"{k}:{v['M']:.3f}" for k, v in sorted(rec["staircase"].items()))
        L += [f"Best M by support size: {stair}", "",
              f"all-6 M_c{C} = {rec['all6'][f'M_c{C}']:.3f} nat" if rec["all6"].get(f"M_c{C}") is not None else "all-6 M unavailable", ""]
        if rec.get("s_plus"):
            L += [f"S+ = {{{', '.join(rec['s_plus'])}}}", ""]
        t2 = rec.get("t2_confirmation")
        if t2 and t2["mean_diff"] is not None:
            verdict = "**CONFIRMED — dilution-affected**" if t2["confirmed"] else "not confirmed"
            L += [f"T2 confirmation: paired mean diff {t2['mean_diff']:+.4f} "
                  f"+/- {t2['se']:.4f} nat (n={t2['n']}) -> {verdict}", ""]
        elif t2:
            L += ["T2 confirmation: unavailable (no jointly valid seed pair).", ""]
        top = sorted((e for e in rec["entries"] if e.get(f"M_c{C}") is not None),
                     key=lambda e: -e[f"M_c{C}"])[:10]
        L += [f"| S | \\|S\\| | M_c<={C} | vs all-6 (paired) |", "|---|---:|---:|---|"]
        for e in top:
            d = ("—" if e["paired_vs_all6"] is None
                 else f"{e['paired_vs_all6']:+.4f} +/- {e['paired_se']:.4f}")
            L.append(f"| {{{', '.join(e['S'])}}} | {e['size']} | {e[f'M_c{C}']:.3f} | {d} |")
        L.append("")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
