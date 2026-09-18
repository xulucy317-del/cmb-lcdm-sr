#!/usr/bin/env python
"""Data-driven spectral parameter templates — Phase 7b of docs/discovery_roadmap.md.

Per channel, the template of parameter j is the local derivative of the
log-spectrum at the prior midpoint,

    t_j(ell) = d log10 D_ell / d u_j |_{u=0},

estimated data-driven (no simulator call) by locally-weighted quadratic
regression over a train-split subsample: features [1, u_j, u_i u_j] with
Gaussian kernel weights w = exp(-||u||^2 / (2 h^2)). The quadratic block
keeps finite-sample curvature leakage out of the linear coefficients (the
LHS is symmetric around u = 0, so quadratic terms are orthogonal to linear
ones in expectation); remaining bias is O(h^2) * third derivatives. A
halved-bandwidth template set is stored alongside as the sensitivity check.

The normal-equation blocks are shared across ell (the design depends only on
u), so one streaming pass accumulates A = X^T W X (28 x 28, shared) and
B = X^T W Y per channel (28 x L_ch) — the whole fit is two small solves.

Row alignment between ``theta.npy`` and every touched shard is asserted
(max |theta_shard - theta_npy| < 1e-8) before a shard's rows are used.

Reads:  data/theta.npy + data/splits_v1.npz (train split = split_id 0),
        spectra shards per channel (CSD3 paths from the stored model
        configs by default: tt from models/lcdm_tt_beta3e-4, ee from
        models/lcdm_tt_ee_lowl).
Writes: data/spectral_templates_v1.npz  (small; checked in)

    python scripts/spectral_templates.py                 # on CSD3
    python scripts/spectral_templates.py --shards-root /path/to/shards
"""
import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")

import _bootstrap  # noqa: F401,E402

import numpy as np  # noqa: E402

from cmb_lcdm_sr import tiers  # noqa: E402
from cmb_lcdm_sr.encoder import resolve_shard_dirs  # noqa: E402

SEED_BASE = 20260805
SHARD_ROWS = 5000          # rows per shard in the parent project's layout
N_FEATURES = 1 + 6 + 21    # [1, u_j, upper-tri u_i u_j]

# Default channel -> run whose config records that channel's shard dir.
CHANNEL_CONFIG_RUNS = {"tt": "models/lcdm_tt_beta3e-4",
                       "ee": "models/lcdm_tt_ee_lowl"}


def quad_features(u: np.ndarray) -> np.ndarray:
    """(n, 6) u-rows -> (n, 28) design [1, u_j, u_i u_j (i <= j)]."""
    n = u.shape[0]
    cols = [np.ones((n, 1)), u]
    iu, ju = np.triu_indices(6)
    cols.append(u[:, iu] * u[:, ju])
    return np.concatenate(cols, axis=1)


def kernel_weights(u: np.ndarray, h: float) -> np.ndarray:
    return np.exp(-(u ** 2).sum(axis=1) / (2.0 * h * h))


def accumulate_templates(theta: np.ndarray, rows: np.ndarray,
                         shard_dirs: dict, mid: np.ndarray, half: np.ndarray,
                         bandwidths: list[float],
                         shard_rows: int | None = None) -> dict:
    """One streaming pass over the shards; returns per-(h, channel) solves.

    theta: (N_total, 6) full sampled-basis table; rows: global row indices of
    the subsample. Shards are opened once each; only subsample rows are read.
    """
    shard_rows = shard_rows or SHARD_ROWS
    channels = list(shard_dirs.keys())
    u_all = tiers.theta_to_u(theta[rows], mid, half)
    X = quad_features(u_all)
    W = {h: kernel_weights(u_all, h) for h in bandwidths}

    A = {h: np.zeros((N_FEATURES, N_FEATURES)) for h in bandwidths}
    B = {h: {ch: None for ch in channels} for h in bandwidths}

    order = np.argsort(rows)
    rows_s, X_s = rows[order], X[order]
    W_s = {h: W[h][order] for h in bandwidths}
    shard_ids = rows_s // shard_rows
    paths_ch = {ch: sorted(Path(shard_dirs[ch]).glob("spectra_*.npz"))
                for ch in channels}

    for h in bandwidths:
        A[h] += X_s.T @ (X_s * W_s[h][:, None])

    for sid in np.unique(shard_ids):
        pos = np.where(shard_ids == sid)[0]
        glob = rows_s[pos]
        local = glob - sid * shard_rows
        for ch in channels:
            path = paths_ch[ch][sid]
            with np.load(path) as z:
                th_shard = np.asarray(z["theta"])[local]
                err = np.abs(th_shard - theta[glob]).max()
                if err > 1e-8:
                    raise AssertionError(
                        f"theta misalignment in {path}: max|diff|={err:g}")
                Y = np.log10(np.clip(
                    np.asarray(z["spectra"])[local].astype(np.float64),
                    1e-30, None))
            for h in bandwidths:
                Xw = X_s[pos] * W_s[h][pos, None]
                contrib = Xw.T @ Y
                if B[h][ch] is None:
                    B[h][ch] = contrib
                else:
                    B[h][ch] += contrib

    out = {}
    for h in bandwidths:
        n_eff = float(W[h].sum() ** 2 / (W[h] ** 2).sum())
        coefs = {}
        for ch in channels:
            c = np.linalg.solve(A[h], B[h][ch])      # (28, L_ch)
            coefs[ch] = {"templates": c[1:7], "intercept": c[0]}
        out[h] = {"n_eff": n_eff, "coefs": coefs}
    return out


def load_ell(shard_dirs: dict) -> dict:
    ells = {}
    for ch, d in shard_dirs.items():
        p = sorted(Path(d).glob("spectra_*.npz"))[0]
        with np.load(p, mmap_mode="r") as z:
            ells[ch] = np.asarray(z["ell"], dtype=np.int64)
    return ells


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--channels", nargs="*", default=["tt", "ee"])
    p.add_argument("--shards", nargs="*", default=None, metavar="CH=DIR",
                   help="Explicit per-channel shard dirs (override).")
    p.add_argument("--shards-root", default=None,
                   help="Root holding the shard dirs under original basenames.")
    p.add_argument("--n-sub", type=int, default=100_000)
    p.add_argument("--bandwidth", type=float, default=0.6)
    p.add_argument("--bandwidth-check", type=float, default=0.3)
    p.add_argument("--out", default=None,
                   help="Default: <dataset-dir>/spectral_templates_v1.npz")
    args = p.parse_args()

    explicit = {}
    for item in args.shards or []:
        ch, d = item.split("=", 1)
        explicit[ch] = d
    shard_dirs = {}
    for ch in args.channels:
        if ch in explicit:
            shard_dirs[ch] = explicit[ch]
        else:
            resolved = resolve_shard_dirs(CHANNEL_CONFIG_RUNS[ch],
                                          shards_root=args.shards_root)
            shard_dirs[ch] = resolved[ch]
    for ch, d in shard_dirs.items():
        if not Path(d).is_dir():
            raise FileNotFoundError(f"shard dir for '{ch}' not found: {d}")

    theta = np.load(Path(args.dataset_dir) / "theta.npy")
    split_id = np.load(Path(args.dataset_dir) / "splits_v1.npz")["split_id"]
    train_rows = np.where(split_id == 0)[0]
    mid, half = tiers.load_prior_box(args.dataset_dir)

    rng = np.random.default_rng([SEED_BASE, 3])
    n_sub = min(args.n_sub, len(train_rows))
    rows = np.sort(rng.choice(train_rows, size=n_sub, replace=False))
    print(f"[setup] channels={list(shard_dirs)}  n_sub={n_sub} of "
          f"{len(train_rows)} train rows  h={args.bandwidth} "
          f"(check {args.bandwidth_check})")

    bandwidths = [args.bandwidth, args.bandwidth_check]
    fits = accumulate_templates(theta, rows, shard_dirs, mid, half, bandwidths)
    ells = load_ell(shard_dirs)

    out_path = Path(args.out or
                    Path(args.dataset_dir) / "spectral_templates_v1.npz")
    payload = {
        "channels": np.array(list(shard_dirs.keys())),
        "theta_order": np.array(tiers.THETA_ORDER),
        "sampled_labels": np.array(tiers.SAMPLED_LABELS),
        "mid": mid, "half": half,
        "h_main": args.bandwidth, "h_check": args.bandwidth_check,
        "n_sub": n_sub, "seed_base": SEED_BASE,
        "n_eff_main": fits[args.bandwidth]["n_eff"],
        "n_eff_check": fits[args.bandwidth_check]["n_eff"],
        "shard_dirs": np.array(json.dumps(
            {ch: str(d) for ch, d in shard_dirs.items()})),
    }
    for ch in shard_dirs:
        payload[f"ell_{ch}"] = ells[ch]
        payload[f"templates_{ch}"] = fits[args.bandwidth]["coefs"][ch]["templates"]
        payload[f"intercept_{ch}"] = fits[args.bandwidth]["coefs"][ch]["intercept"]
        payload[f"templates_hcheck_{ch}"] = \
            fits[args.bandwidth_check]["coefs"][ch]["templates"]
    np.savez(out_path, **payload)
    print(f"[write] {out_path}")

    for ch in shard_dirs:
        t = fits[args.bandwidth]["coefs"][ch]["templates"]
        t2 = fits[args.bandwidth_check]["coefs"][ch]["templates"]
        norms = np.linalg.norm(t, axis=1)
        cos_h = [float(np.dot(t[j], t2[j]) /
                       (np.linalg.norm(t[j]) * np.linalg.norm(t2[j]) + 1e-300))
                 for j in range(6)]
        print(f"[{ch}] n_eff={fits[args.bandwidth]['n_eff']:.0f}  "
              f"||t_j||: " +
              " ".join(f"{lab}={v:.2f}" for lab, v in
                       zip(tiers.SAMPLED_LABELS, norms)) +
              "  cos(h, h/2): " +
              " ".join(f"{c:.3f}" for c in cos_h))
        i_tau, i_as = 3, 4
        cc = float(np.dot(t[i_tau], t[i_as]) /
                   (np.linalg.norm(t[i_tau]) * np.linalg.norm(t[i_as])
                    + 1e-300))
        print(f"[{ch}] uncentered cos(t_tau, t_lnAs) = {cc:.4f} "
              "(A_s e^{-2 tau} degeneracy: ~ -1 where no low-ell "
              "reionization feature breaks it)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
