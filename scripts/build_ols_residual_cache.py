#!/usr/bin/env python
"""Build OLS-stage-1 residual caches for the hybrid (affine + SR) account.

Step 2 of the staged nonlinearity plan
(docs/evidence_record.md §6.4): fit the exact
six-input affine map in the *sampled* basis (omega_b, omega_cdm, H0, tau,
ln10^10 A_s, n_s) on the 4,000 T0-fit rows only — inputs centred/scaled with
T0-fit statistics, full-rank lstsq, identical conventions to the
coordinate-matched audit's `logamp64` arm and the §6.5 quadratic pilot — and
cache the residual e = mu_k − OLS(theta) over all 50k test rows as the blind
stage-2 search target:

    models/<run>/analysis/residual_ols_z<K>_v1.npy

A provenance record (coefficients, per-tier NMSE, sha256 of each cache) is
written next to them. Deterministic: rerunning reproduces byte-identical
caches.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401

import numpy as np

SAMPLED_NAMES = ["omega_b", "omega_cdm", "H0", "tau", "ln10As", "n_s"]
FIT = slice(0, 4000)
TIERS = {"T0_fit": slice(0, 4000), "T0_val": slice(4000, 5000),
         "T1": slice(5000, 25000), "T2": slice(25000, 50000)}


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-dir", required=True)
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--latents", type=int, nargs="+", required=True)
    args = p.parse_args()

    run_dir = Path(args.run_dir)
    data = Path(args.dataset_dir)
    theta = np.load(data / "theta.npy")
    sid = np.load(data / "splits_v1.npz")["split_id"]
    theta_test = theta[sid == 2]
    if theta_test.shape != (50000, 6):
        raise SystemExit(f"unexpected test theta shape {theta_test.shape}")
    means = np.load(run_dir / "analysis" / "encoder_means_test.npy")

    mu = theta_test[FIT].mean(axis=0)
    sd = theta_test[FIT].std(axis=0)
    U = (theta_test - mu) / sd
    A = np.hstack([np.ones((len(U), 1)), U])

    record = {
        "kind": "ols_stage1_residual_cache",
        "version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "basis": "sampled (logamp): " + ", ".join(SAMPLED_NAMES),
        "fit_rows": "T0_fit [0:4000) of the test split",
        "standardization": {"mean": mu.tolist(), "std": sd.tolist()},
        "latents": {},
    }
    for k in args.latents:
        y = means[:, k].astype(np.float64)
        w, *_ = np.linalg.lstsq(A[FIT], y[FIT], rcond=None)
        pred = A @ w
        resid = y - pred
        out = run_dir / "analysis" / f"residual_ols_z{k}_v1.npy"
        np.save(out, resid)
        nmse = {name: float(np.mean(resid[s] ** 2) / y[s].var())
                for name, s in TIERS.items()}
        record["latents"][str(k)] = {
            "cache": str(out),
            "sha256": file_sha256(out),
            "coef_standardized": w[1:].tolist(),
            "intercept_standardized": float(w[0]),
            "coef_sampled_basis": (w[1:] / sd).tolist(),
            "intercept_sampled_basis": float(w[0] - np.sum(w[1:] * mu / sd)),
            "nmse_by_tier": nmse,
            "residual_std_over_latent_std_T2":
                float(resid[TIERS["T2"]].std() / y[TIERS["T2"]].std()),
        }
        print(f"z{k}: T2 NMSE {100*nmse['T2']:.4f}%  cache {out.name}  "
              f"sha {record['latents'][str(k)]['sha256'][:12]}")

    rec_path = run_dir / "analysis" / "residual_ols_v1_fit.json"
    with open(rec_path, "w") as f:
        json.dump(record, f, indent=1, sort_keys=True)
    print(f"provenance: {rec_path}")


if __name__ == "__main__":
    main()
