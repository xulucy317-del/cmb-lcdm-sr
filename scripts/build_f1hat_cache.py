#!/usr/bin/env python
"""Cache the stage-1 prediction f1hat_k = mu_k − e1_k for every latent.

Interaction-aware stage-2 SR (post-closure follow-up to roadmap Phase 6)
exposes the stage-1 calibrated prediction h(f1) as a 7th input column so the
search can express amplitude × shape interactions the additive hierarchy
h(f1) + g(f2(θ)) cannot absorb (deviation D-DoD-z2 on the TT z2 card).

The column needs no new computation: the Phase-3 residual cache stores
e1 = mu − h(f1) over all 50k test rows (T1 rows via the cross-fitted
fold-h, all other rows — including the T0 SR rows — via the full-T1 h), so
f1hat = mu − e1 recovers h(f1) exactly, with the same row convention the
Phase-6 additive stage-2 consolidation already uses.

Reads:  models/<run>/analysis/{encoder_means_test.npy, residual_z<k>_v1.npy}
Writes: models/<run>/analysis/f1hat_z<k>_v1.npy   (50k rows, float64)

    python scripts/build_f1hat_cache.py --run-dir models/lcdm_tt_beta3e-4
    python scripts/build_f1hat_cache.py --run-dir models/lcdm_tt_ee_lowl
"""
import argparse
from pathlib import Path

import _bootstrap  # noqa: F401

import numpy as np


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run-dir", required=True,
                   help="models/<run> with analysis/ caches.")
    p.add_argument("--n-sr-rows", type=int, default=5000,
                   help="Leading rows the SR consumes (T0); must be all-finite.")
    args = p.parse_args()

    analysis = Path(args.run_dir) / "analysis"
    mu = np.load(analysis / "encoder_means_test.npy")
    n_rows, n_latents = mu.shape
    status = 0
    for k in range(n_latents):
        res_path = analysis / f"residual_z{k}_v1.npy"
        if not res_path.exists():
            print(f"[err] {res_path} missing — rerun Phase 3")
            status = 1
            continue
        e1 = np.load(res_path)
        if e1.shape != (n_rows,):
            print(f"[err] z{k}: residual shape {e1.shape} != ({n_rows},)")
            status = 1
            continue
        f1hat = (mu[:, k] - e1).astype(np.float64)
        finite = np.isfinite(f1hat)
        n_bad_sr = int((~finite[:args.n_sr_rows]).sum())
        out = analysis / f"f1hat_z{k}_v1.npy"
        np.save(out, f1hat)
        fv = f1hat[finite]
        print(f"[z{k}] -> {out.name}  finite {finite.mean():.4f}  "
              f"range [{fv.min():.3g}, {fv.max():.3g}]  std {fv.std():.3g}  "
              f"nonfinite-in-first-{args.n_sr_rows} {n_bad_sr}")
        if n_bad_sr:
            print(f"[err] z{k}: {n_bad_sr} non-finite rows inside the SR "
                  f"window — PySR input would be poisoned")
            status = 1
    return status


if __name__ == "__main__":
    raise SystemExit(main())
