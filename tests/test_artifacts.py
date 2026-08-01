"""The stored artifacts (checkpoints, scalers, splits, theta) load and agree."""
import numpy as np
import pytest


def test_theta_and_splits(repo_root):
    theta = np.load(repo_root / "data" / "theta.npy", mmap_mode="r")
    assert theta.shape == (500_000, 6)
    split_id = np.load(repo_root / "data" / "splits_v1.npz")["split_id"]
    assert split_id.shape == (500_000,)
    counts = np.bincount(split_id)
    assert counts.tolist() == [400_000, 50_000, 50_000]


def test_scalers_load(model_dirs):
    from cmb_lcdm_sr.scaler import ShardedScaler

    tt = ShardedScaler.load(model_dirs["tt"] / "scaler.npz")
    assert tt.channels == ["tt"]
    assert tt.refs["tt"].shape == (2471,)
    mu, sig = tt.channel_stats("tt")
    assert mu.shape == (2471,) and sig.shape == (2471,)
    assert np.all(sig > 0)

    ee = ShardedScaler.load(model_dirs["ee"] / "scaler.npz")
    assert ee.channels == ["tt", "ee"]
    assert ee.refs["tt"].shape == (2471,)
    assert ee.refs["ee"].shape == (2499,)
    mu_ee, sig_ee = ee.channel_stats("ee")
    assert mu_ee.shape == (2499,) and np.all(sig_ee > 0)


def test_scaler_roundtrip_channel(model_dirs):
    from cmb_lcdm_sr.scaler import ShardedScaler

    sc = ShardedScaler.load(model_dirs["ee"] / "scaler.npz")
    rng = np.random.default_rng(0)
    x = rng.normal(size=(4, 2499))
    phys = sc.inverse_transform_channel("ee", x)
    # invert manually: log10(phys/ref) standardised should give x back
    mu, sig = sc.channel_stats("ee")
    x_back = (np.log10(phys / sc.refs["ee"]) - mu) / sig
    assert np.allclose(x_back, x, atol=1e-10)


def test_checkpoints_load_and_encode_shapes(model_dirs):
    torch = pytest.importorskip("torch")
    from cmb_lcdm_sr.encoder import load_checkpoint

    m_tt, ck_tt = load_checkpoint(model_dirs["tt"] / "best_model.pt")
    assert ck_tt["model_cfg"]["latent_dim"] == 5
    mu, logvar = m_tt.encode(torch.zeros(2, 1, 2471))
    assert mu.shape == (2, 5)

    m_ee, ck_ee = load_checkpoint(model_dirs["ee"] / "best_model.pt")
    assert ck_ee["model_cfg"]["latent_dim"] == 6
    mu, logvar = m_ee.encode({"tt": torch.zeros(2, 2471), "ee": torch.zeros(2, 2499)})
    assert mu.shape == (2, 6)


def test_resolve_shard_dirs_from_config(model_dirs):
    from cmb_lcdm_sr.encoder import resolve_shard_dirs

    # Recorded (HPC) paths straight from config_used.json:
    tt = resolve_shard_dirs(model_dirs["tt"])
    assert list(tt) == ["tt"]
    assert tt["tt"].endswith("shards_global_lhs")

    # --shards-root remaps by basename, preserving channel order:
    ee = resolve_shard_dirs(model_dirs["ee"], shards_root="/x")
    assert list(ee) == ["tt", "ee"]
    assert ee["tt"] == "/x/shards_global_lhs"
    assert ee["ee"] == "/x/shards_global_lhs_ee_lowl"
