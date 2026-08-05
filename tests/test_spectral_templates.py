"""Phase-7b spectral templates: the streaming local-quadratic fit recovers
planted gradients from synthetic shards; misaligned shard theta is a hard
error; the CLI writes a complete cache."""
import json
import pathlib
import sys

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

import spectral_templates as st  # noqa: E402
from cmb_lcdm_sr import tiers  # noqa: E402

MID = np.array([0.022, 0.115, 71.0, 0.07, 3.04, 0.965])
HALF = np.array([0.002, 0.015, 9.0, 0.06, 0.14, 0.045])
N, SHARD_ROWS, L = 2000, 500, 12


def make_shards(tmp_path, rng, corrupt_shard=None):
    """Synthetic shard dir with planted log10 D = c0 + b·u + quadratics."""
    theta = MID + (2.0 * rng.random((N, 6)) - 1.0) * HALF
    u = (theta - MID) / HALF
    ell = np.arange(30, 30 + L)
    c0 = rng.normal(3.0, 0.2, L)
    b = rng.normal(0.0, 0.5, (6, L))
    quad = 0.4 * (u[:, 0] * u[:, 1] + 0.5 * u[:, 3] ** 2)
    y = c0 + u @ b + quad[:, None] * rng.normal(1.0, 0.1, L)
    y += 1e-3 * rng.standard_normal((N, L))

    d = tmp_path / "shards_tt"
    d.mkdir()
    for sid in range(N // SHARD_ROWS):
        sl = slice(sid * SHARD_ROWS, (sid + 1) * SHARD_ROWS)
        th = theta[sl].copy()
        if corrupt_shard == sid:
            th[0, 0] += 1e-3
        np.savez(d / f"spectra_{sid:05d}.npz",
                 spectra=(10.0 ** y[sl]).astype(np.float32),
                 theta=th, ell=ell)
    return d, theta, b, c0


def test_recovers_planted_gradients(tmp_path):
    rng = np.random.default_rng(11)
    d, theta, b, c0 = make_shards(tmp_path, rng)
    rows = np.sort(rng.choice(N, size=1500, replace=False))
    fits = st.accumulate_templates(theta, rows, {"tt": str(d)}, MID, HALF,
                                   [0.6, 0.3], shard_rows=SHARD_ROWS)
    for h in (0.6, 0.3):
        got = fits[h]["coefs"]["tt"]["templates"]
        assert got.shape == (6, L)
        assert np.abs(got - b).max() < 0.05
        assert np.abs(fits[h]["coefs"]["tt"]["intercept"] - c0).max() < 0.05
    assert fits[0.3]["n_eff"] < fits[0.6]["n_eff"] <= 1500


def test_theta_misalignment_raises(tmp_path):
    rng = np.random.default_rng(12)
    d, theta, *_ = make_shards(tmp_path, rng, corrupt_shard=1)
    rows = np.arange(N)
    with pytest.raises(AssertionError, match="misalignment"):
        st.accumulate_templates(theta, rows, {"tt": str(d)}, MID, HALF,
                                [0.6], shard_rows=SHARD_ROWS)


def test_cli_writes_cache(tmp_path, monkeypatch):
    rng = np.random.default_rng(13)
    d, theta, b, _ = make_shards(tmp_path, rng)
    data = tmp_path / "data"
    data.mkdir()
    np.save(data / "theta.npy", theta)
    np.savez(data / "splits_v1.npz", split_id=np.zeros(N, dtype=np.int64))
    (data / "meta.json").write_text(json.dumps({
        "prior_keys": tiers.THETA_ORDER,
        "priors": {k: [float(MID[j] - HALF[j]), float(MID[j] + HALF[j])]
                   for j, k in enumerate(tiers.THETA_ORDER)}}))

    out = tmp_path / "tpl.npz"
    monkeypatch.setattr(st, "SHARD_ROWS", SHARD_ROWS)
    monkeypatch.setattr(sys, "argv",
                        ["spectral_templates.py", "--dataset-dir", str(data),
                         "--channels", "tt", "--shards", f"tt={d}",
                         "--n-sub", "1500", "--out", str(out)])
    assert st.main() == 0

    z = np.load(out, allow_pickle=False)
    assert list(z["channels"]) == ["tt"]
    assert z["templates_tt"].shape == (6, L)
    assert z["templates_hcheck_tt"].shape == (6, L)
    assert z["ell_tt"][0] == 30
    assert np.abs(z["templates_tt"] - b).max() < 0.05
    assert float(z["n_eff_main"]) > float(z["n_eff_check"])
