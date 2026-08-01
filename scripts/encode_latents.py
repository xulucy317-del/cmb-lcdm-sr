#!/usr/bin/env python
"""Encoder pass: cache the test-split posterior means for a stored run.

Loads ``best_model.pt`` + ``scaler.npz`` from the run dir, streams the test
split (50k rows) from the spectra shards, applies the training-time
preprocessing (log10(spec/ref), then per-ell standardisation with the stored
stats), and saves:

    <run-dir>/analysis/encoder_means_test.npy     (50000, L)
    <run-dir>/analysis/encoder_logvars_test.npy   (50000, L)

This is the only step that needs the large spectra shards. Everything else in
the blind-SR pipeline runs from the cached means + theta.npy + splits_v1.npz.

Shard location resolution (first match wins):
    --shards tt=DIR [ee=DIR]    explicit per-channel dirs
    --shards-root DIR           DIR/<original shard-dir basename> per channel
    (neither)                   absolute paths recorded in config_used.json
                                (valid on the HPC filesystem, e.g. CSD3)

Examples:
    # On CSD3 (config paths valid as-is):
    python scripts/encode_latents.py --run-dir models/lcdm_tt_beta3e-4

    # Anywhere else, pointing at a synced copy of the shards:
    python scripts/encode_latents.py --run-dir models/lcdm_tt_ee_lowl \
        --shards-root /path/to/cmbvae/data
"""
import argparse
import time
from pathlib import Path

import _bootstrap  # noqa: F401


def parse_shards(pairs):
    out = {}
    for item in pairs or []:
        if "=" not in item:
            raise argparse.ArgumentTypeError(
                f"--shards expects channel=dir pairs, got {item!r}")
        ch, d = item.split("=", 1)
        out[ch] = d
    return out


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run-dir", required=True, help="models/<run> directory.")
    p.add_argument("--dataset-dir", default="data",
                   help="Holds splits_v1.npz (default: data/).")
    p.add_argument("--shards", nargs="*", default=None, metavar="CH=DIR",
                   help="Explicit per-channel shard dirs, e.g. tt=/x/shards_global_lhs.")
    p.add_argument("--shards-root", default=None,
                   help="Root holding the shard dirs under their original basenames.")
    p.add_argument("--batch-size", type=int, default=1024)
    p.add_argument("--num-workers", type=int, default=0)
    p.add_argument("--device", default="auto", help="cpu | cuda | mps | auto.")
    p.add_argument("--out", default=None,
                   help="Defaults to <run-dir>/analysis/encoder_means_test.npy.")
    args = p.parse_args()

    from cmb_lcdm_sr.encoder import generate_encoder_means
    from cmb_lcdm_sr.utils import get_device

    device = get_device(args.device)
    print(f"[setup] run_dir={args.run_dir}  device={device}")
    t0 = time.time()
    out = generate_encoder_means(
        run_dir=args.run_dir,
        dataset_dir=args.dataset_dir,
        shard_dirs=parse_shards(args.shards) or None,
        shards_root=args.shards_root,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        device=device,
        out_path=args.out,
    )
    import numpy as np
    means = np.load(out)
    print(f"[done] {out}  shape={means.shape}  ({time.time() - t0:.1f}s)")
    print(f"[done] per-latent std: {np.array2string(means.std(axis=0), precision=3)}")
    if Path(args.run_dir).name == "lcdm_tt_beta3e-4":
        print("[hint] amplitude latent for this run: --latent-index 2")
    elif Path(args.run_dir).name == "lcdm_tt_ee_lowl":
        print("[hint] amplitude latent for this run: --latent-index 5")


if __name__ == "__main__":
    main()
