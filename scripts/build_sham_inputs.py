#!/usr/bin/env python
"""Cache provably-irrelevant "sham" input columns for the dilution control.

The exhaustive-support experiment (post-closure follow-up to roadmap Phase 4)
asks whether feeding PySR inputs a latent does not depend on *degrades the
discovery* at a matched complexity budget. Comparing supports against each
other cannot settle the mechanism on its own: when {omega_b, ...} loses to a
subset, one can always argue omega_b carries a little real information that
the search simply failed to use.

A sham column removes that argument. It is a random permutation of a real
theta column, so it has *exactly* the marginal of a genuine cosmological
parameter while carrying zero information about any latent by construction.
Appended as a 7th input beside the full all-6 support, it isolates the search
cost of one useless variable: any drop in MI@c<=10 against the existing
all-6 full-protocol runs (results/<run>/allparams, same protocol, 5 seeds) is
dilution and nothing else.

Row convention: the permutation is applied *within* the SR block (the first
--n-samples test rows, which is what run_blind_sr.py consumes) and separately
within the remainder, so the used block holds the identical multiset of values
as the donor column's used block — a marginal matched exactly, not just in
distribution. The columns are model-independent (they derive from theta
alone), hence they live in data/ rather than under a run's analysis/.

Reads:  data/{theta.npy, splits_v1.npz}
Writes: data/sham_v1_<donor>.npy   (50k rows, float64) + data/sham_v1.json

    python scripts/build_sham_inputs.py
"""
import argparse
import json
from pathlib import Path

import numpy as np

# donor label -> (theta column, RNG seed). Three donors, so the null is read
# across three different parameter marginals rather than one.
DONORS = {"ob": (0, 90001), "tau": (3, 90002), "ns": (5, 90003)}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--n-samples", type=int, default=5000,
                   help="Size of the SR block permuted in isolation (protocol: 5000).")
    args = p.parse_args()

    data = Path(args.dataset_dir)
    theta = np.load(data / "theta.npy")
    splits = np.load(data / "splits_v1.npz")
    test_idx = np.where(splits["split_id"] == 2)[0]
    n = min(args.n_samples, len(test_idx))
    col_test = theta[test_idx]

    meta = {"n_test_rows": int(len(test_idx)), "sr_block": int(n), "donors": {}}
    for label, (col, seed) in DONORS.items():
        v = col_test[:, col].astype(np.float64).copy()
        rng = np.random.default_rng(seed)
        v[:n] = v[:n][rng.permutation(n)]
        v[n:] = v[n:][rng.permutation(len(v) - n)]
        out = data / f"sham_v1_{label}.npy"
        np.save(out, v)
        # Sanity: same multiset as the donor block, different row order.
        donor = col_test[:n, col].astype(np.float64)
        assert np.array_equal(np.sort(v[:n]), np.sort(donor))
        frac_moved = float((v[:n] != donor).mean())
        meta["donors"][label] = {"theta_col": col, "seed": seed,
                                 "path": str(out), "frac_rows_moved": frac_moved}
        print(f"[sham] {label}: theta col {col}, seed {seed}, "
              f"{frac_moved:.4f} of SR rows moved -> {out}")

    (data / "sham_v1.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"[sham] wrote {data / 'sham_v1.json'}")


if __name__ == "__main__":
    main()
