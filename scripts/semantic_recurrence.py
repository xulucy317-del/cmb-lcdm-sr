#!/usr/bin/env python
"""Semantic clustering & seed recurrence — Phase 2 of docs/discovery_roadmap.md.

Selection by *recurrence of meaning*, not string identity (README gap 2,
docs/next_step.md section 2.2). Per latent, every front equation with
eta_plat = mi_val / Î_plat >= --eta-floor (Î_plat from the Phase-1
``knee_readout_<run>.json``) is collected from every family (protocol
namespace) and clustered with the three frozen equivalence tests of roadmap
section 0.3 — any one suffices:

  (i)  identical canonical sympy form — the stored ``expression_simplified``
       is already ``str(sympy.simplify(...))`` (run_blind_sr), i.e. exactly
       the reduction ``pool_sr_runs.canonical_form`` applies, so it is used
       as the exact-pooling key without re-simplifying;
  (ii) |Spearman rho| >= 0.98 on the 2048-theta anchor set (tiers T1[:2048]);
  (iii) gradient-cosine distance d_grad <= 0.05 in u-coordinates.

Union-find over pairs (``semantics.cluster_forms``); anchors where a member
is non-finite are dropped pairwise and the finite fraction recorded.

Union-find takes the *transitive closure* of the pairwise tests, and front
forms are a near-continuum (adjacent complexities correlate >= 0.98), so a
cluster can chain together extremes that fail the direct tests. Rather than
altering the pre-registered rule, each cluster carries two cohesion
diagnostics: **rep-linked** — the fraction of member forms directly
equivalent to the representative — and **pair cohesion** — the direct pass
rate over (up to 200) sampled member pairs. A cluster with cohesion ~1 is a
genuine clique; low cohesion flags chained structure to read with care.

Recurrence R_SR (section 0.3) is evaluated *per family*, against that
family's own envelope: a seed counts for a cluster when its front holds a
member with complexity <= c*_F and val MI >= M_F(c*_F) - SD_F, where c*_F is
the family's one-SE knee. **Documented deviation from section 0.3:** the
seed-level tolerance is one cross-seed standard deviation, not the SE of the
mean. A single seed fluctuates by ~SD around the plateau, so the literal
SE-of-mean rule caps R_SR near P(z >= -1/sqrt(n)) ~ 0.7 even for a perfectly
stable coordinate — the artifact would dominate the statistic it is meant to
protect. (The envelope knee itself keeps the one-SE definition.) The headline R_SR of a cluster is the maximum over
the canonical capacity families (allparams, allparams_ms10, allparams_ms30):
the budget-matched ms10 family is where a simple recurrent coordinate shows
up; the ms20/ms30 families measure recurrence of the near-plateau composites.
Per family the best *exact-string* recurrence over the cluster's members is
reported next to the semantic one — the pool_sr_runs comparison column.

The latent's **canonical coordinate** = simplest representative of the most
recurrent cluster (ties: higher best MI). The representative is the simplest
member *directly equivalent to a majority of sampled members* — without the
majority constraint a chained-in low-complexity stub (e.g. bare ``omega_b``
linked to 2% of its cluster) would be elected to speak for a clique it is
not semantically part of.

Reads:  results/<run>/<subdir>/... via the knee_readout loaders,
        experiments/knee_readout_<run>.json  (Phase-1 plateaus)
Writes: experiments/semantic_recurrence_<run>.{md,json}

    python scripts/semantic_recurrence.py --run lcdm_tt_beta3e-4
    python scripts/semantic_recurrence.py --run lcdm_tt_ee_lowl
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

import _bootstrap  # noqa: F401

import numpy as np

from consolidate_allparams import AUDIT_EXPECTED, textbook_hit
from knee_readout import (DEFAULT_SUBDIRS, discover_families, first_crossing,
                          load_front, pool_family, seed_envelope)

from cmb_lcdm_sr import semantics, tiers

CANONICAL_FAMILIES = ["allparams", "allparams_ms10", "allparams_ms30"]


# ---- family envelope statistics --------------------------------------------

def family_knee(runs: dict) -> dict:
    """One-SE knee of one family: {n_seeds, plat, se, c_star, knee_mi}."""
    cmax = max(max(max((c for c, *_ in f["rows"]), default=1), f["maxsize"])
               for f in runs.values())
    grid = np.arange(1, cmax + 1)
    envs = {s: seed_envelope(f["rows"], grid) for s, f in runs.items()}
    pooled = pool_family(envs, grid)
    per_seed_max = [max((mi for _c, mi, *_ in f["rows"]), default=np.nan)
                    for f in runs.values()]
    per_seed_max = [v for v in per_seed_max if np.isfinite(v)]
    plat = float(np.mean(per_seed_max))
    se = (float(np.std(per_seed_max, ddof=1) / np.sqrt(len(per_seed_max)))
          if len(per_seed_max) > 1 else 0.0)
    sd = (float(np.std(per_seed_max, ddof=1)) if len(per_seed_max) > 1
          else 0.0)
    c_star = first_crossing(grid, pooled["mean"], plat - se)
    m_at = (float(pooled["mean"][np.where(grid == c_star)[0][0]])
            if c_star is not None else plat)
    return {"n_seeds": len(runs), "plat": plat, "se": se, "sd": sd,
            "c_star": c_star, "knee_mi": m_at - se,
            "knee_mi_seed": m_at - sd}


# ---- per-latent clustering + recurrence -------------------------------------

def latent_recurrence(fam_runs: dict, plat_ref: float, anchors: np.ndarray,
                      half: np.ndarray, eta_floor: float = 0.25,
                      rho_min: float = 0.98, grad_max: float = 0.05) -> dict:
    """fam_runs: {family: {seed: front}} for one latent (knee_readout loaders).

    Returns cluster table, per-family knees, and the canonical coordinate.
    """
    knees = {fam: family_knee(runs) for fam, runs in fam_runs.items()}
    floor_mi = eta_floor * plat_ref

    # rows above the floor, with provenance; dedup key = stored simplified str
    rows = [(fam, s, c, mi, err, expr)
            for fam, runs in fam_runs.items()
            for s, f in runs.items()
            for c, mi, err, expr in f["rows"] if mi >= floor_mi]
    keys = sorted({r[5] for r in rows})

    forms, dropped = {}, []
    for key in keys:
        expr = semantics.parse_expr(key)
        if expr is None:
            dropped.append(key)
            continue
        forms[key] = semantics.FormEval(
            expr_str=key, expr=expr, canonical=key,
            values=semantics.evaluate_on_theta(expr, anchors),
            grads_u=semantics.gradients_on_theta(expr, anchors, half))
    order = [k for k in keys if k in forms]
    labels = semantics.cluster_forms([forms[k] for k in order],
                                     rho_min=rho_min, grad_max=grad_max)
    label_of = dict(zip(order, labels))
    rows = [r for r in rows if r[5] in label_of]

    # ---- per-cluster statistics --------------------------------------------
    by_cluster = defaultdict(list)
    for r in rows:
        by_cluster[label_of[r[5]]].append(r)

    clusters = []
    for lab, members in sorted(by_cluster.items()):
        min_c = {}          # key -> smallest complexity seen
        best_of_key = {}    # key -> best (mi, family, seed)
        best = max(members, key=lambda r: r[3])
        for fam, s, c, mi, err, key in members:
            min_c[key] = min(min_c.get(key, c), c)
            if key not in best_of_key or mi > best_of_key[key][0]:
                best_of_key[key] = (mi, fam, s)
        # representative: simplest member directly equivalent to a majority
        # of (up to 24) sampled members — never a chained-in outlier stub
        member_keys = sorted(min_c)
        rng = np.random.default_rng(0)
        probes = (member_keys if len(member_keys) <= 24 else
                  [member_keys[i] for i in
                   rng.choice(len(member_keys), 24, replace=False)])
        cands = sorted(min_c, key=lambda k: (min_c[k], -best_of_key[k][0]))
        rep_key = cands[0]
        for k in cands:
            hits = [semantics.same_cluster(forms[k], forms[p])
                    for p in probes if p != k]
            if not hits or np.mean(hits) >= 0.5:
                rep_key = k
                break

        # cohesion: how much of the cluster is directly equivalent (vs
        # transitively chained through intermediates)
        others = [k for k in member_keys if k != rep_key]
        rep_linked = (np.mean([semantics.same_cluster(forms[rep_key], forms[k])
                               for k in others]) if others else 1.0)
        pairs = [(a, b) for i, a in enumerate(member_keys)
                 for b in member_keys[i + 1:]]
        if len(pairs) > 200:
            pairs = [pairs[i] for i in
                     rng.choice(len(pairs), 200, replace=False)]
        pair_cohesion = (np.mean([semantics.same_cluster(forms[a], forms[b])
                                  for a, b in pairs]) if pairs else 1.0)

        r_sr = {}
        for fam, kn in knees.items():
            if kn["c_star"] is None:
                continue
            fam_seeds = sorted(fam_runs[fam])
            hits_by_key = defaultdict(set)
            for f2, s, c, mi, _e, key in members:
                if (f2 == fam and c <= kn["c_star"]
                        and mi >= kn["knee_mi_seed"]):
                    hits_by_key[key].add(s)
            seeds_hit = sorted(set().union(*hits_by_key.values())
                               if hits_by_key else set())
            r_sr[fam] = {
                "n_seeds": len(fam_seeds), "hits": len(seeds_hit),
                "r": len(seeds_hit) / len(fam_seeds),
                "seeds_hit": seeds_hit,
                "best_exact_r": (max(len(v) for v in hits_by_key.values())
                                 / len(fam_seeds)) if hits_by_key else 0.0,
            }
        headline = max((r_sr[f]["r"] for f in CANONICAL_FAMILIES if f in r_sr),
                       default=0.0)

        clusters.append({
            "cluster": lab,
            "representative": rep_key,
            "rep_complexity": min_c[rep_key],
            "rep_support": forms[rep_key].support,
            "support_union": sorted({v for k in min_c
                                     for v in forms[k].support}),
            "c_range": [min(r[2] for r in members),
                        max(r[2] for r in members)],
            "best_mi": {"mi": best[3], "err": best[4], "family": best[0],
                        "seed": best[1], "complexity": best[2]},
            "n_forms": len(min_c), "n_rows": len(members),
            "rep_linked": float(rep_linked),
            "pair_cohesion": float(pair_cohesion),
            "finite_frac_min": min(forms[k].finite_frac for k in min_c),
            "textbook_any": any(textbook_hit(k) for k in min_c),
            "r_sr": r_sr, "r_sr_headline": headline,
        })
    clusters.sort(key=lambda c: (-c["r_sr_headline"], -c["best_mi"]["mi"]))

    canonical = None
    if clusters and clusters[0]["r_sr_headline"] > 0:
        top = max(clusters, key=lambda c: (c["r_sr_headline"],
                                           -c["rep_complexity"],
                                           c["best_mi"]["mi"]))
        canonical = top["cluster"]

    return {"families": knees, "floor_mi": floor_mi,
            "n_rows_above_floor": len(rows), "n_forms": len(order),
            "n_unparseable": len(dropped), "unparseable": dropped[:5],
            "clusters": clusters, "canonical_cluster": canonical}


# ---- outputs ----------------------------------------------------------------

def rsr_cell(cl: dict, fam: str) -> str:
    r = cl["r_sr"].get(fam)
    if r is None:
        return "—"
    ex = (f" (exact {int(round(r['best_exact_r'] * r['n_seeds']))}"
          f"/{r['n_seeds']})" if r["best_exact_r"] < r["r"] else "")
    return f"{r['hits']}/{r['n_seeds']}{ex}"


def to_markdown(run: str, out: dict, eta_floor: float) -> str:
    md = [f"# Semantic recurrence — `{run}` (roadmap Phase 2)\n"]
    md.append(
        "Front equations with eta_plat >= "
        f"{eta_floor} (vs the Phase-1 ms30-firmed plateau) pooled by the "
        "three frozen equivalence tests (canonical sympy identity; "
        "|Spearman| >= 0.98 on the 2048-theta anchors; gradient-cosine "
        "distance <= 0.05 in u-coordinates) and union-find clustered. R_SR "
        "per family = fraction of that family's seeds whose front carries a "
        "cluster member at knee level (c <= c*_F, MI >= M_F(c*_F) - SD_F; "
        "seed-level tolerance = one cross-seed SD — documented deviation "
        "from the SE-of-mean wording of section 0.3, which would cap R_SR "
        "at ~0.7 by seed-scatter alone). "
        "Where semantic pooling beats exact-string pooling, the best "
        "single-string recurrence is shown in parentheses — the "
        "`pool_sr_runs` comparison. Supports are in the sampled basis "
        "(`ln10As` = ln 10^10 A_s).\n")
    for zk, lat in sorted(out["latents"].items()):
        md.append(f"\n## {zk} — {lat['audit_expected']}\n")
        fams = lat["families"]
        md.append("Family knees: " + "; ".join(
            f"`{f}` c*={k['c_star']}, knee MI {k['knee_mi']:.3f} "
            f"(plat {k['plat']:.3f}+/-{k['se']:.3f}, n={k['n_seeds']})"
            for f, k in sorted(fams.items())) + ".\n")
        md.append(f"{lat['n_rows_above_floor']} front rows above the floor, "
                  f"{lat['n_forms']} unique simplified forms, "
                  f"{lat['n_unparseable']} unparseable, "
                  f"{len(lat['clusters'])} semantic clusters.\n")
        canon = lat["canonical_cluster"]
        if canon is not None:
            cl = next(c for c in lat["clusters"] if c["cluster"] == canon)
            md.append(f"**Canonical coordinate** (cluster {canon}, R_SR "
                      f"{cl['r_sr_headline']:.2f}): "
                      f"`{cl['representative']}` "
                      f"(c={cl['rep_complexity']}, support "
                      f"{{{', '.join(cl['rep_support'])}}})\n")
        md.append("| cluster | representative (c) | support(rep) | R_SR ms10 "
                  "| R_SR ms20 | R_SR ms30 | best MI +/- err (family/seed) "
                  "| C range | forms | cohesion rep/pair | textbook |")
        md.append("|---:|---|---|---|---|---|---|---|---:|---|---|")
        for cl in lat["clusters"]:
            b = cl["best_mi"]
            rep = cl["representative"]
            rep_s = rep if len(rep) <= 64 else rep[:61] + "..."
            md.append(
                f"| {cl['cluster']} | `{rep_s}` ({cl['rep_complexity']}) "
                f"| {', '.join(cl['rep_support'])} "
                f"| {rsr_cell(cl, 'allparams_ms10')} "
                f"| {rsr_cell(cl, 'allparams')} "
                f"| {rsr_cell(cl, 'allparams_ms30')} "
                f"| {b['mi']:.3f} +/- {b['err']:.3f} "
                f"(`{b['family']}`/s{b['seed']}) "
                f"| {cl['c_range'][0]}-{cl['c_range'][1]} | {cl['n_forms']} "
                f"| {cl['rep_linked']:.2f}/{cl['pair_cohesion']:.2f} "
                f"| {'yes' if cl['textbook_any'] else ''} |")
    md.append("\n---\n_Generated by `scripts/semantic_recurrence.py` from "
              "the same fronts as the Phase-1 readout; hpsweep families "
              "contribute members and JSON R_SR entries but no headline._")
    return "\n".join(md) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", required=True)
    p.add_argument("--results-root", default="results")
    p.add_argument("--subdirs", nargs="*", default=DEFAULT_SUBDIRS)
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--knee-json", default=None,
                   help="Phase-1 JSON (default experiments/knee_readout_<run>.json)")
    p.add_argument("--eta-floor", type=float, default=0.25)
    p.add_argument("--rho-min", type=float, default=0.98)
    p.add_argument("--grad-max", type=float, default=0.05)
    p.add_argument("--out", default=None)
    args = p.parse_args()

    knee_path = Path(args.knee_json or
                     f"experiments/knee_readout_{args.run}.json")
    knee = json.loads(knee_path.read_text())

    fams = discover_families(Path(args.results_root), args.run, args.subdirs)
    if not fams:
        print(f"[FAIL] no reports under {args.results_root}/{args.run}")
        return 1
    by_latent = {}
    for fam, latents in fams.items():
        for k, seeds in latents.items():
            for s, path in seeds.items():
                by_latent.setdefault(k, {}).setdefault(fam, {})[s] = \
                    load_front(path)

    anchors = tiers.anchor_theta(args.dataset_dir)
    _mid, half = tiers.load_prior_box(args.dataset_dir)

    out = {"run": args.run, "eta_floor": args.eta_floor,
           "rho_min": args.rho_min, "grad_max": args.grad_max,
           "knee_json": str(knee_path), "n_anchors": int(anchors.shape[0]),
           "latents": {}, "generated_by": "scripts/semantic_recurrence.py"}
    for k in sorted(by_latent):
        plat_ref = knee["latents"][f"z{k}"]["plateau"]["mi_plat"]
        lat = latent_recurrence(by_latent[k], plat_ref, anchors, half,
                                eta_floor=args.eta_floor,
                                rho_min=args.rho_min, grad_max=args.grad_max)
        lat["audit_expected"] = AUDIT_EXPECTED.get(args.run, {}).get(k)
        lat["plat_ref"] = plat_ref
        out["latents"][f"z{k}"] = lat
        canon = lat["canonical_cluster"]
        n_cl = len(lat["clusters"])
        top = lat["clusters"][0] if lat["clusters"] else None
        print(f"  z{k}: {lat['n_rows_above_floor']} rows -> {lat['n_forms']} "
              f"forms -> {n_cl} clusters; canonical={canon} "
              + (f"R_SR={top['r_sr_headline']:.2f} rep(c="
                 f"{top['rep_complexity']}) {top['representative'][:56]!r}"
                 if top else ""))

    out_path = Path(args.out or f"experiments/semantic_recurrence_{args.run}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.with_suffix(".json").write_text(json.dumps(out, indent=2))
    print(f"[write] {out_path.with_suffix('.json')}")
    out_path.with_suffix(".md").write_text(
        to_markdown(args.run, out, args.eta_floor))
    print(f"[write] {out_path.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
