"""run_blind_sr.resolve_target — latent-column vs arbitrary-target mode (M1),
and the shuffled control's Phase-6 reuse of the same interface."""
import json
import pathlib
import sys
import types

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


# ---- shuffled control reuses the same target interface (Phase 6) ------------

class _StubPySR:
    """Minimal PySRRegressor stand-in: two fixed front members."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def fit(self, X, y, variable_names=None):
        import pandas as pd

        self._labels = variable_names
        self.equations_ = pd.DataFrame({
            "complexity": [1, 3],
            "loss": [0.9, 0.5],
            "equation": ["x0", "x0 * x1"],
        })
        return self

    def predict(self, X, index=0):
        return X[:, 0] if index == 0 else X[:, 0] * X[:, 1]

    def sympy(self, index=0):
        import sympy

        a, b = sympy.symbols("a b")
        return a if index == 0 else a * b


def _control_world(tmp_path):
    rng = np.random.default_rng(0)
    n_all, n_test = 400, 320
    data = tmp_path / "data"
    data.mkdir()
    np.save(data / "theta.npy", rng.uniform(0.5, 1.5, size=(n_all, 6)))
    split_id = np.zeros(n_all, dtype=np.int64)
    split_id[:n_test] = 2
    np.savez(data / "splits_v1.npz", split_id=split_id)
    run_dir = tmp_path / "models" / "demo"
    (run_dir / "analysis").mkdir(parents=True)
    np.save(run_dir / "analysis" / "encoder_means_test.npy",
            rng.normal(size=(n_test, 3)))
    tgt = run_dir / "analysis" / "residual_z0_v1.npy"
    np.save(tgt, rng.normal(size=n_test))
    return data, run_dir, tgt


def test_shuffled_control_target_npy_and_latent_modes(tmp_path, monkeypatch):
    import run_shuffled_control as rsc

    assert rsc.resolve_target is resolve_target   # shared M1 interface
    data, run_dir, tgt = _control_world(tmp_path)
    stub = types.ModuleType("pysr")
    stub.__version__ = "stub"
    stub.PySRRegressor = _StubPySR
    monkeypatch.setitem(sys.modules, "pysr", stub)

    out1 = tmp_path / "out_npy"
    monkeypatch.setattr(sys, "argv", [
        "run_shuffled_control.py", "--run-dir", str(run_dir),
        "--dataset-dir", str(data), "--target-npy", str(tgt),
        "--target-label", "res_z0", "--shuffle-seed", "1",
        "--inputs", "omega_b", "tau", "--n-samples", "300",
        "--out-dir", str(out1)])
    rsc.main()
    rep = json.loads((out1 / "report.json").read_text())
    assert rep["target_label"] == "res_z0"
    assert rep["target_index"] is None
    assert rep["control"] == "shuffled_target"
    assert rep["n_samples"] == 300 and rep["best_expression"]

    out2 = tmp_path / "out_latent"
    monkeypatch.setattr(sys, "argv", [
        "run_shuffled_control.py", "--run-dir", str(run_dir),
        "--dataset-dir", str(data), "--target-index", "1",
        "--shuffle-seed", "1", "--inputs", "omega_b", "tau",
        "--n-samples", "300", "--out-dir", str(out2)])
    rsc.main()
    rep2 = json.loads((out2 / "report.json").read_text())
    assert rep2["target_label"] == "z1" and rep2["target_index"] == 1
