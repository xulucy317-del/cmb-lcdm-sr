#!/usr/bin/env python
"""eta_post for the plain six-input OLS index — the missing ceiling column.

Open item 2 of §7 of `docs/evidence_record.md`,
item 7 of §5.1 of `docs/sr_objective_discussion_2026-09-02.md`. Every
"fraction of what the latent stores" statement in the record is quoted for the
discovered coordinates (canonical f1, the hierarchical f1+f2 composite, the
subset winner s*) and never for the affine baseline that beats them on
reconstruction. This adds that column.

The trap this script exists to avoid: the coordinate-matched audit's `ols_mi`
is MI(mu_k; w.theta) — mutual information against the encoder **mean**, not
against a posterior draw Z_k. It is a different quantity with a different
ceiling, and normalising it by MI(Z;mu) gives ratios above 1 (up to 2.55),
i.e. trivially DPI-violating. The numerator must be recomputed as
MI(Z_k; w.theta) on the same fresh T2 posterior draw the ceiling study used.

Reproduces `posterior_ceiling.py` exactly for the parts that must match:

  * the T2 posterior draw Z_k = mu_k + exp(logvar/2) * eps, with
    logvar clipped to +-10 and rng = default_rng([SEED_BASE, k, 7]);
  * `numerator_mi` = GMM-MI on jointly finite rows, max_samples 5000;
  * the seed convention for the numerator, offset past the stored candidate
    block so the OLS index never collides with a stored candidate's seed.

Denominators (`ceiling.I`, `mi_mu_ref`) and the comparison columns
(`canonical_eta_post_hat`, `hierarchy.eta_post_hat_comb`) are read from the
frozen artifacts, not recomputed.

The OLS index is the `logamp64` arm of the coordinate-matched audit: the exact
six-input affine map in the sampled basis, coefficients fitted on the 4,000
T0-fit rows. It is read from the stored fit so this script cannot drift from
the audit.

    python scripts/eta_post_ols_index.py --run lcdm_tt_ee_lowl

Post-hoc on T2 rows already opened by the ceiling study; this is a diagnostic
column, not a frozen gate. Deterministic.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")

import _bootstrap  # noqa: F401,E402

import numpy as np  # noqa: E402

from cmb_lcdm_sr import tiers  # noqa: E402

from posterior_ceiling import (  # noqa: E402
    LOGVAR_CLAMP, SEED_BASE, dpi_check, eta_with_se, numerator_mi,
)

RUNS = ("lcdm_tt_beta3e-4", "lcdm_tt_ee_lowl")
# Past every stored candidate index (assemble_candidates never returns 500).
OLS_SEED_OFFSET = 500


def ols_index(fit: dict, latent: int, theta_test: np.ndarray) -> np.ndarray:
    """w.theta from the audit's stored logamp64 fit, in standardized inputs."""
    entry = next(x for x in fit["latents"] if x["latent"] == latent)
    d = entry["definition"]
    x = (theta_test - np.asarray(d["x_mean"])) / np.asarray(d["x_scale"])
    return float(d["intercept_standardized"]) + x @ np.asarray(
        d["coef_standardized"])


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", choices=RUNS, default=None,
                   help="default: both checkpoints")
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--models-root", default="models")
    p.add_argument("--results-root", default="results")
    p.add_argument("--arm", default="logamp64")
    p.add_argument("--max-samples-mi", type=int, default=5000)
    p.add_argument("--out", default="experiments/eta_post_ols_index_v1.json")
    args = p.parse_args()

    data = Path(args.dataset_dir)
    theta = np.load(data / "theta.npy")
    sid = np.load(data / "splits_v1.npz")["split_id"]
    theta_test = theta[sid == 2]
    t2 = tiers.T2
    theta_t2 = theta_test[t2]

    record = {
        "kind": "eta_post_ols_index",
        "version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "arm": args.arm,
        "numerator": "MI(Z_k; w.theta) on the T2 posterior draw, GMM-MI",
        "draw": "identical to posterior_ceiling.py "
                "(rng default_rng([SEED_BASE, k, 7]), logvar clipped +-10)",
        "denominators": "ceiling.I and mi_mu_ref read from "
                        "experiments/posterior_ceiling_<run>.json",
        "status": "post-hoc diagnostic on already-opened T2 rows; not a gate",
        "runs": {},
    }

    for run in ([args.run] if args.run else list(RUNS)):
        ceiling = json.load(open(f"experiments/posterior_ceiling_{run}.json"))
        fit = json.load(open(f"{args.results_root}/{run}/"
                             f"coordinate_matched_ols_v1/{args.arm}/fit.json"))
        resid = json.load(open(f"experiments/residual_sr_{run}.json"))
        comb = {r["latent"]: r.get("hierarchy", {}).get("eta_post_hat_comb")
                for r in resid["latents"]}

        mu = np.load(Path(args.models_root) / run / "analysis"
                     / "encoder_means_test.npy").astype(np.float64)
        lv = np.load(Path(args.models_root) / run / "analysis"
                     / "encoder_logvars_test.npy").astype(np.float64)

        rows = []
        print(f"\n### {run}")
        print(f"{'k':>3} {'MI(Z;OLS)':>11} {'eta_post':>9} {'eta_hat':>9} "
              f"{'canon hat':>10} {'f1+f2 hat':>10} {'DPI':>5}")
        for entry in ceiling["latents"]:
            k = entry["latent"]
            lv_t2 = np.clip(lv[t2, k], -LOGVAR_CLAMP, LOGVAR_CLAMP)
            z = (mu[t2, k] + np.exp(0.5 * lv_t2)
                 * np.random.default_rng([SEED_BASE, k, 7])
                 .standard_normal(t2.stop - t2.start))

            fv = ols_index(fit, k, theta_t2)
            mi, err, frac = numerator_mi(
                z, fv, max_samples=args.max_samples_mi,
                seed=SEED_BASE + 1000 * k + OLS_SEED_OFFSET)

            I, I_se = entry["ceiling"]["I"], entry["ceiling"]["se"]
            ref, ref_err = entry["mi_mu_ref"], entry["mi_mu_ref_err"]
            eta, eta_se = eta_with_se(mi, err, I, I_se)
            hat, hat_se = eta_with_se(mi, err, ref, ref_err)
            dpi_ok, margin, margin_analytic = dpi_check(
                mi, err, ref, ref_err, I, I_se)

            rows.append({
                "latent": k, "finite_frac_T2": frac,
                "mi": mi, "mi_err": err,
                "eta_post": eta, "eta_post_se": eta_se,
                "eta_post_hat": hat, "eta_post_hat_se": hat_se,
                "dpi_ok": dpi_ok, "dpi_margin": margin,
                "dpi_margin_analytic": margin_analytic,
                "canonical_eta_post_hat": entry["canonical_eta_post_hat"],
                "hierarchy_eta_post_hat_comb": comb.get(k),
                "ceiling_I": I, "mi_mu_ref": ref,
            })
            print(f"z{k:<2} {mi:>11.4f} {eta:>9.4f} {hat:>9.4f} "
                  f"{entry['canonical_eta_post_hat']:>10.4f} "
                  f"{(comb.get(k) if comb.get(k) is not None else float('nan')):>10.4f} "
                  f"{str(dpi_ok):>5}")

        beats_f1 = sum(r["eta_post_hat"] > r["canonical_eta_post_hat"]
                       for r in rows)
        beats_comb = sum(r["eta_post_hat"] > r["hierarchy_eta_post_hat_comb"]
                         for r in rows
                         if r["hierarchy_eta_post_hat_comb"] is not None)
        record["runs"][run] = {
            "latents": rows,
            "ols_beats_canonical_f1": beats_f1,
            "ols_beats_hierarchy_f1_f2": beats_comb,
            "n_latents": len(rows),
            "dpi_violations": sum(r["dpi_ok"] is False for r in rows),
        }
        print(f"OLS index beats canonical f1 on eta_hat in "
              f"{beats_f1}/{len(rows)}; beats f1+f2 in {beats_comb}/{len(rows)}; "
              f"DPI violations {record['runs'][run]['dpi_violations']}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(record, f, indent=1, sort_keys=True)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
