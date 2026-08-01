"""Checkpoint loading and the encoder pass over the test split.

The blind-SR target is the encoder posterior mean of one latent, evaluated on
the 50k-row test split and cached as ``<run_dir>/analysis/encoder_means_test.npy``.
This module regenerates that cache from a stored run dir:

    models/<run>/best_model.pt     model_cfg + n_ell + n_channels + weights
    models/<run>/scaler.npz        per-channel refs + normalisation stats
    models/<run>/config_used.json  data section (shard dirs, n_shards, ...)

plus the spectra shards themselves (the only large external input).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import torch

from .dataset import build_test_loader
from .model import build_model
from .scaler import ShardedScaler


def load_checkpoint(path: str | Path, device: str = "cpu"):
    """Rebuild a CVAE or DualEncoderCVAE from a saved checkpoint."""
    ckpt = torch.load(path, map_location=device, weights_only=False)
    model = build_model(ckpt["model_cfg"], n_ell=ckpt["n_ell"], n_channels=ckpt.get("n_channels", 1))
    state = ckpt.get("model_state", ckpt.get("state_dict"))
    model.load_state_dict(state)
    model.to(device).eval()
    return model, ckpt


@torch.no_grad()
def encode_dataset(model, loader):
    """Run the encoder over a NormWrapper-wrapped loader.

    Returns (means, logvars). Works for both tensor and dict batches since
    model.encode() dispatches on input type.
    """
    means, logvars = [], []
    for x in loader:
        m, lv = model.encode(x)
        means.append(m.cpu().numpy())
        logvars.append(lv.cpu().numpy())
    return np.concatenate(means), np.concatenate(logvars)


def resolve_shard_dirs(
    run_dir: str | Path,
    shard_dirs: Optional[Dict[str, str]] = None,
    shards_root: Optional[str | Path] = None,
) -> Dict[str, str]:
    """Determine per-channel shard directories for a stored run.

    Priority: explicit ``shard_dirs`` > ``shards_root``/<original basename> >
    the absolute paths recorded in the run's ``config_used.json`` (valid on
    the HPC filesystem the models were trained on).
    """
    if shard_dirs:
        return dict(shard_dirs)
    cfg_path = Path(run_dir) / "config_used.json"
    with open(cfg_path) as f:
        data_cfg = json.load(f)["data"]
    if "shard_dirs" in data_cfg:
        recorded = {ch: str(d) for ch, d in data_cfg["shard_dirs"].items()}
    else:
        channels = data_cfg.get("channels", ["tt"])
        recorded = {channels[0]: str(data_cfg["shard_dir"])}
    if shards_root is not None:
        return {ch: str(Path(shards_root) / Path(d).name) for ch, d in recorded.items()}
    return recorded


def generate_encoder_means(
    run_dir: str | Path,
    dataset_dir: str | Path,
    shard_dirs: Optional[Dict[str, str]] = None,
    shards_root: Optional[str | Path] = None,
    batch_size: int = 1024,
    num_workers: int = 0,
    device: str = "cpu",
    out_path: Optional[str | Path] = None,
) -> Path:
    """Encoder pass over the test split; caches means (and logvars) to disk.

    Returns the path of the saved ``encoder_means_test.npy``.
    """
    run_dir = Path(run_dir)
    out_path = Path(out_path) if out_path else run_dir / "analysis" / "encoder_means_test.npy"

    cfg_path = run_dir / "config_used.json"
    n_shards, expected_n, force_dict = 100, 500_000, False
    if cfg_path.exists():
        with open(cfg_path) as f:
            data_cfg = json.load(f)["data"]
        n_shards = int(data_cfg.get("n_shards", 100))
        expected_n = int(data_cfg.get("expected_n", 500_000))
        force_dict = bool(data_cfg.get("force_dict_mode", False))

    scaler = ShardedScaler.load(run_dir / "scaler.npz")
    dirs = resolve_shard_dirs(run_dir, shard_dirs=shard_dirs, shards_root=shards_root)
    for ch, d in dirs.items():
        if not Path(d).is_dir():
            raise FileNotFoundError(
                f"shard dir for channel '{ch}' not found: {d}\n"
                "Point --shards / --shards-root at a location holding the full "
                "spectra_*.npz shards (see README: data provenance)."
            )

    dev = torch.device(device)
    loader = build_test_loader(
        dirs, scaler, Path(dataset_dir) / "splits_v1.npz",
        batch_size=batch_size, num_workers=num_workers, device=dev,
        n_shards=n_shards, expected_n=expected_n, force_dict_mode=force_dict,
    )
    model, _ = load_checkpoint(run_dir / "best_model.pt", device=device)
    means, logvars = encode_dataset(model, loader)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(out_path, means)
    np.save(out_path.parent / "encoder_logvars_test.npy", logvars)
    return out_path
