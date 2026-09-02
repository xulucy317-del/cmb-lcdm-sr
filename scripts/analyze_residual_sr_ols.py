#!/usr/bin/env python
"""First-pass analysis of the Step-2 hybrid runs (OLS stage 1 + blind SR).

Reads results/<run>/residual_sr_ols/{z<k>_seed*,shuffled_res_ols_z<k>_s*}
and reports, per latent:

* per-seed best form (held-out GMM-MI) and its MI against the OLS residual;
* shuffled-residual control MI (null floor);
* recurrence under the frozen §0.3 equivalence rule (cluster_forms on the
  2048-row T1 anchor set) with the dominant-cluster representative;
* |Spearman| of the new coordinate against the Phase-6 additive f2 of the
  same latent (linear mop-up check);
* the combined hybrid account: OLS + 64-bin T1-only monotone q(f2_new),
  T2 NMSE — against the affine and quadratic rungs of the ladder.

Analysis only; writes results/<run>/residual_sr_ols/analysis_summary.json.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401

import numpy as np

from cmb_lcdm_sr import semantics
from cmb_lcdm_sr.calibrate import fit_h

T1 = slice(5000, 25000)
T2 = slice(25000, 50000)
PHASE6_F2 = {  # canonical additive stage-2 coordinates, for comparison
    "lcdm_tt_ee_lowl": {0: "A_s*H0*omega_cdm/n_s", 4: "tau"},
}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", default="lcdm_tt_ee_lowl")
    p.add_argument("--latents", type=int, nargs="+", default=[0, 4])
    p.add_argument("--subdir", default="residual_sr_ols")
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--n-anchors", type=int, default=2048)
    args = p.parse_args()

    data = Path(args.dataset_dir)
    theta = np.load(data / "theta.npy")
    sid = np.load(data / "splits_v1.npz")["split_id"]
    theta_test = theta[sid == 2]
    meta = json.load(open(data / "meta.json"))
    prior = meta.get("priors") or meta.get("prior_ranges") or meta
    half = np.array([(hi - lo) / 2.0 for lo, hi in
                     (prior[k] for k in meta["prior_keys"])])
    anchors = theta_test[T1][: args.n_anchors]

    run = args.run
    root = Path("results") / run / args.subdir
    means = np.load(Path("models") / run / "analysis" / "encoder_means_test.npy")

    summary = {"kind": "residual_sr_ols_analysis", "run": run,
               "created_utc": datetime.now(timezone.utc).isoformat(),
               "latents": {}}
    for k in args.latents:
        resid = np.load(Path("models") / run / "analysis"
                        / f"residual_ols_z{k}_v1.npy")
        y = means[:, k].astype(np.float64)
        ols_pred = y - resid
        var2 = y[T2].var()
        nmse_aff = float(np.mean(resid[T2] ** 2) / var2)

        forms, rows = [], []
        for s in range(5):
            rp = root / f"z{k}_seed{s}" / "report.json"
            if not rp.exists():
                print(f"[warn] missing {rp}")
                continue
            r = json.load(open(rp))
            # selection = held-out GMM-MI winner; newer reports store it as
            # best_expression, older schemas only carry the scored front.
            if r.get("best_expression") is not None:
                expr = r["best_expression"]
                best = next((eq for eq in r.get("all_equations", [])
                             if eq.get("expression_raw") == expr
                             or eq.get("index") == r.get("best_index")), {})
                mi = r.get("best_mi_val", best.get("mi_val"))
            else:
                scored = [eq for eq in r["all_equations"]
                          if eq.get("mi_val") is not None
                          and np.isfinite(eq["mi_val"])]
                best = max(scored, key=lambda eq: eq["mi_val"])
                expr, mi = best["expression_raw"], best["mi_val"]
            fe = semantics.evaluate_form(
                expr, anchors, half, complexity=best.get("complexity"),
                meta={"seed": s, "mi_val": mi})
            forms.append(fe)
            rows.append(r)

        labels = semantics.cluster_forms(forms)
        sizes = {c: labels.count(c) for c in set(labels)}
        dom = max(sizes, key=lambda c: sizes[c])
        r_sr = sizes[dom] / len(forms)
        members = [f for f, c in zip(forms, labels) if c == dom]
        rep = min(members, key=lambda f: (f.complexity or 99))

        # linear mop-up check: |Spearman| vs the Phase-6 additive f2
        old = PHASE6_F2.get(run, {}).get(k)
        rho_old = None
        if old:
            fe_old = semantics.evaluate_form(old, anchors, half)
            rho_old = semantics.spearman_abs(rep.values, fe_old.values)

        # combined hybrid account per seed: OLS + q(f2_new), T1-fit, T2 score
        combined = []
        for fe in forms:
            vals = semantics.evaluate_on_theta(fe.expr, theta_test)
            fin1 = np.isfinite(vals[T1]) & np.isfinite(resid[T1])
            entry = {"seed": fe.meta["seed"]}
            for tag, mono in (("nmse_T2", True), ("nmse_T2_nonmonotone", False)):
                q = fit_h(vals[T1][fin1], resid[T1][fin1], monotone=mono)
                pred = ols_pred + q(vals)
                fin2 = np.isfinite(pred[T2])
                entry[tag] = float(np.mean((pred[T2][fin2] - y[T2][fin2]) ** 2)
                                   / var2)
                entry.setdefault("finite_frac_T2", float(fin2.mean()))
            # any-function 1-D bound: flexible probe residual <- f2_new,
            # fit on the first half of T1, scored on the second
            from sklearn.ensemble import HistGradientBoostingRegressor
            v1, r1 = vals[T1][fin1], resid[T1][fin1]
            n_half = len(v1) // 2
            g = HistGradientBoostingRegressor(max_iter=300, random_state=0)
            g.fit(v1[:n_half, None], r1[:n_half])
            entry["probe_r2_1d"] = float(g.score(v1[n_half:, None], r1[n_half:]))
            combined.append(entry)

        controls = []
        for s in range(2):
            cp = root / f"shuffled_res_ols_z{k}_s{s}" / "report.json"
            if cp.exists():
                c = json.load(open(cp))
                controls.append({
                    "shuffle_seed": s,
                    "mi_shuffled_eval": c.get("best_mi_val_shuffled_eval"),
                    "mi_unshuffled_eval": c.get("best_mi_val_unshuffled_eval"),
                })

        rec = {
            "n_seeds": len(forms),
            "per_seed": [{"seed": f.meta["seed"], "mi_val": f.meta["mi_val"],
                          "complexity": f.complexity, "support": f.support,
                          "expr": f.expr_str} for f in forms],
            "cluster_sizes": sorted(sizes.values(), reverse=True),
            "R_SR": r_sr,
            "representative": {"expr": rep.expr_str,
                               "complexity": rep.complexity,
                               "support": rep.support,
                               "canonical": rep.canonical},
            "spearman_vs_phase6_f2": rho_old,
            "phase6_f2": old,
            "nmse_T2_affine": nmse_aff,
            "combined_hybrid": combined,
            "combined_hybrid_median_nmse_T2":
                float(np.median([c["nmse_T2"] for c in combined])),
            "combined_hybrid_median_nmse_T2_nonmonotone":
                float(np.median([c["nmse_T2_nonmonotone"] for c in combined])),
            "probe_r2_1d_median":
                float(np.median([c["probe_r2_1d"] for c in combined])),
            "controls": controls,
        }
        summary["latents"][str(k)] = rec

        mi = [f'{f.meta["mi_val"]:.3f}' for f in forms]
        print(f"\n=== {run} z{k} ===")
        print(f"per-seed best MI vs residual: {mi}")
        print(f"R_SR {r_sr:.2f}  cluster sizes {rec['cluster_sizes']}")
        print(f"representative (c={rep.complexity}, support {rep.support}):")
        print(f"  {rep.expr_str}")
        print(f"|Spearman| vs Phase-6 f2 ({old}): {rho_old}")
        print(f"affine NMSE {100*nmse_aff:.3f}%  ->  hybrid median "
              f"{100*rec['combined_hybrid_median_nmse_T2']:.3f}% (monotone) / "
              f"{100*rec['combined_hybrid_median_nmse_T2_nonmonotone']:.3f}% "
              f"(free)  |  1-D any-function probe R^2 "
              f"{rec['probe_r2_1d_median']:.3f}")
        for c in controls:
            print(f"control s{c['shuffle_seed']}: shuffled-eval MI "
                  f"{c['mi_shuffled_eval']}, unshuffled-eval "
                  f"{c['mi_unshuffled_eval']}")

    out = root / "analysis_summary.json"
    with open(out, "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
