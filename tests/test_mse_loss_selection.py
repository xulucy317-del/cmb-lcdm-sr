"""MSE loss dispatch and selector-controlled SR front ranking."""
import json
import pathlib
import sys
import types

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

from cmb_lcdm_sr.sr import (  # noqa: E402
    JULIA_LOSS_GMM_MI,
    JULIA_LOSS_MSE,
    pysr_loss_kwargs,
    rank_front,
    resolve_loss,
    resolve_posthoc_mi,
)
from run_blind_sr import default_out_dir  # noqa: E402


def test_loss_dispatch_defaults_and_mutual_exclusivity():
    gmm, selector = resolve_loss("gmm_mi", "auto")
    assert selector == "mi"
    assert gmm["pysr_kwarg"] == "loss_function"
    assert pysr_loss_kwargs("gmm_mi") == {
        "loss_function": JULIA_LOSS_GMM_MI}

    mse, selector = resolve_loss("mse", "auto")
    assert selector == "mse"
    assert mse["pysr_kwarg"] == "elementwise_loss"
    assert pysr_loss_kwargs("mse") == {"elementwise_loss": JULIA_LOSS_MSE}
    assert "loss_function" not in pysr_loss_kwargs("mse")

    assert resolve_loss("mse", "mi")[1] == "mi"
    assert resolve_posthoc_mi("auto", "mse") == "none"
    assert resolve_posthoc_mi("auto", "mi") == "full"
    assert resolve_posthoc_mi("full", "mse") == "full"
    with pytest.raises(ValueError, match="cannot be disabled"):
        resolve_posthoc_mi("none", "mi")
    with pytest.raises(ValueError, match="Unknown post-hoc MI"):
        resolve_posthoc_mi("invalid", "mse")
    with pytest.raises(ValueError, match="Unknown inner loss"):
        resolve_loss("not-a-loss")
    with pytest.raises(ValueError, match="Unknown selection metric"):
        resolve_loss("mse", "not-a-metric")


def test_rank_front_directions_nonfinite_and_ties():
    rows = [
        {"index": 4, "complexity": 8, "mse_val": 0.2, "mi_val": 0.7},
        {"index": 3, "complexity": 5, "mse_val": 0.2, "mi_val": 0.7},
        {"index": 2, "complexity": 5, "mse_val": 0.2, "mi_val": 0.7},
        {"index": 1, "complexity": 2, "mse_val": 0.4, "mi_val": 0.9},
        {"index": 0, "complexity": 1, "mse_val": None, "mi_val": np.nan},
    ]
    assert [r["index"] for r in rank_front(rows, "mse")] == [2, 3, 4, 1]
    assert [r["index"] for r in rank_front(rows, "mi")] == [1, 2, 3, 4]


def test_loss_specific_default_output_namespace():
    run = pathlib.Path("models/demo")
    assert str(default_out_dir(run, 2, "")).endswith(
        "demo/symbolic_regression_gmm_mi_seed2")
    assert str(default_out_dir(run, 2, "z1", "mse")).endswith(
        "demo/symbolic_regression_mse_seed2_z1")


class _StubPySR:
    last_kwargs = None

    def __init__(self, **kwargs):
        type(self).last_kwargs = kwargs

    def fit(self, X, y, variable_names=None):
        import pandas as pd

        self._coef = np.polyfit(X[:, 0], y, 1)
        self.equations_ = pd.DataFrame({
            "complexity": [1, 2],
            "loss": [1.0, 0.0],
            "equation": ["0.0", "omega_b"],
        })
        return self

    def predict(self, X, index=0):
        if index == 0:
            return np.zeros(len(X))
        return self._coef[0] * X[:, 0] + self._coef[1]

    def sympy(self, index=0):
        import sympy

        return sympy.Float(0.0) if index == 0 else sympy.Symbol("omega_b")


def test_runner_mse_path_and_report(tmp_path, monkeypatch):
    import cmb_lcdm_sr.mi as mi_mod
    import run_blind_sr as runner

    rng = np.random.default_rng(4)
    n_all, n_test = 500, 400
    data = tmp_path / "data"
    data.mkdir()
    theta = rng.normal(size=(n_all, 6))
    np.save(data / "theta.npy", theta)
    split_id = np.zeros(n_all, dtype=np.int64)
    split_id[:n_test] = 2
    np.savez(data / "splits_v1.npz", split_id=split_id)

    run = tmp_path / "models" / "demo"
    (run / "analysis").mkdir(parents=True)
    means = np.column_stack([theta[:n_test, 0], theta[:n_test, 1]])
    np.save(run / "analysis" / "encoder_means_test.npy", means)

    pysr = types.ModuleType("pysr")
    pysr.__version__ = "stub"
    pysr.PySRRegressor = _StubPySR
    monkeypatch.setitem(sys.modules, "pysr", pysr)

    def fake_mi(a, b, **kwargs):
        raise AssertionError("MSE selection must skip post-hoc MI")

    monkeypatch.setattr(mi_mod, "mutual_information_gmm", fake_mi)
    out = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", [
        "run_blind_sr.py",
        "--run-dir", str(run),
        "--dataset-dir", str(data),
        "--latent-index", "0",
        "--inputs", "omega_b",
        "--n-samples", str(n_test),
        "--inner-loss", "mse",
        "--selection-metric", "auto",
        "--parallelism", "serial",
        "--out-dir", str(out),
    ])
    runner.main()

    kwargs = _StubPySR.last_kwargs
    assert kwargs["elementwise_loss"] == JULIA_LOSS_MSE
    assert "loss_function" not in kwargs
    report_text = (out / "report.json").read_text()
    assert "NaN" not in report_text and "Infinity" not in report_text
    report = json.loads(report_text)
    assert report["inner_loss"] == "mse"
    assert report["selection_metric"] == "mse"
    assert report["posthoc_mi_mode"] == "none"
    assert report["posthoc_mi_status"] == "skipped_not_selected"
    assert report["best_index"] == 1
    assert report["target_transform"]["fit_rows"] == [0, 320]
    assert report["seed"] == 0
    best = next(row for row in report["all_equations"]
                if row["index"] == report["best_index"])
    assert best["mse_val_native"] == pytest.approx(
        best["mse_val"] * report["target_transform"]["std"] ** 2)
    assert best["support"] == ["omega_b"]
    assert report["best_mi_val"] is None
    assert all(row["mi_val"] is None and row["mi_val_err"] is None
               for row in report["all_equations"])


class _ControlStubPySR:
    def __init__(self, **kwargs):
        pass

    def fit(self, X, y, variable_names=None):
        import pandas as pd

        self.equations_ = pd.DataFrame({
            "complexity": [1, 2],
            "loss": [1.0, 400.0],
            "equation": ["0.0", "20.0"],
        })
        return self

    def predict(self, X, index=0):
        return np.full(len(X), 0.0 if index == 0 else 20.0)

    def sympy(self, index=0):
        import sympy

        return sympy.Float(0.0 if index == 0 else 20.0)


def test_shuffled_runner_writes_nonfinite_diagnostics_as_null(
        tmp_path, monkeypatch):
    import cmb_lcdm_sr.mi as mi_mod
    import run_shuffled_control as runner

    rng = np.random.default_rng(8)
    n_all, n_test = 250, 200
    data = tmp_path / "data"
    data.mkdir()
    theta = rng.normal(size=(n_all, 6))
    np.save(data / "theta.npy", theta)
    split_id = np.zeros(n_all, dtype=np.int64)
    split_id[:n_test] = 2
    np.savez(data / "splits_v1.npz", split_id=split_id)

    run = tmp_path / "models" / "demo"
    (run / "analysis").mkdir(parents=True)
    np.save(run / "analysis" / "encoder_means_test.npy",
            theta[:n_test, :2])

    pysr = types.ModuleType("pysr")
    pysr.__version__ = "stub"
    pysr.PySRRegressor = _ControlStubPySR
    monkeypatch.setitem(sys.modules, "pysr", pysr)
    def fail_mi(*args, **kwargs):
        raise AssertionError("MSE control must skip post-hoc MI")

    monkeypatch.setattr(mi_mod, "mutual_information_gmm", fail_mi)

    out = tmp_path / "control"
    monkeypatch.setattr(sys, "argv", [
        "run_shuffled_control.py",
        "--run-dir", str(run),
        "--dataset-dir", str(data),
        "--target-index", "0",
        "--inputs", "omega_b",
        "--n-samples", str(n_test),
        "--shuffle-seed", "3",
        "--inner-loss", "mse",
        "--selection-metric", "mse",
        "--parallelism", "serial",
        "--out-dir", str(out),
    ])
    runner.main()

    report_text = (out / "report.json").read_text()
    assert "NaN" not in report_text and "Infinity" not in report_text
    report = json.loads(report_text)
    assert report["selection_metric"] == "mse"
    assert report["posthoc_mi_mode"] == "none"
    assert report["posthoc_mi_status"] == "skipped_not_selected"
    assert report["best_index"] == 0
    assert report["best_mi_val_shuffled_eval"] is None
    assert report["best_mi_val_unshuffled_eval"] is None
    assert all(row["mi_val_shuffled"] is None
               and row["mi_val_unshuffled"] is None
               for row in report["all_equations"])
