"""run_blind_sr.resolve_target — latent-column vs arbitrary-target mode (M1)."""
import pathlib
import sys

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

from run_blind_sr import resolve_target  # noqa: E402


def test_exactly_one_source_required(tmp_path):
    with pytest.raises(SystemExit, match="exactly one"):
        resolve_target(tmp_path, None, None, None)
    tgt = tmp_path / "t.npy"
    np.save(tgt, np.zeros(10))
    with pytest.raises(SystemExit, match="exactly one"):
        resolve_target(tmp_path, 2, str(tgt), None)


def test_target_npy_vector_label_from_stem(tmp_path):
    v = np.arange(7.0)
    p = tmp_path / "residual_z2_v1.npy"
    np.save(p, v)
    y, label = resolve_target(tmp_path, None, str(p), None)
    assert np.array_equal(y, v) and y.dtype == np.float64
    assert label == "residual_z2_v1"
    _, label2 = resolve_target(tmp_path, None, str(p), "res_z2")
    assert label2 == "res_z2"


def test_target_npy_shape_handling(tmp_path):
    col = tmp_path / "col.npy"
    np.save(col, np.ones((5, 1)))
    y, _ = resolve_target(tmp_path, None, str(col), None)
    assert y.shape == (5,)                    # (n, 1) squeezed
    bad = tmp_path / "bad.npy"
    np.save(bad, np.ones((5, 2)))
    with pytest.raises(SystemExit, match="1-D"):
        resolve_target(tmp_path, None, str(bad), None)


def test_latent_mode_reads_means_column(tmp_path):
    run = tmp_path / "run"
    (run / "analysis").mkdir(parents=True)
    means = np.random.default_rng(0).normal(size=(20, 5))
    np.save(run / "analysis" / "encoder_means_test.npy", means)
    y, label = resolve_target(run, 3, None, None)
    assert label == "z3"
    assert np.allclose(y, means[:, 3])
    with pytest.raises(IndexError, match="out of range"):
        resolve_target(run, 9, None, None)


def test_latent_mode_missing_means_hint(tmp_path):
    with pytest.raises(FileNotFoundError, match="encode_latents"):
        resolve_target(tmp_path, 0, None, None)
