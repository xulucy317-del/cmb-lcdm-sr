"""SR input construction and the Julia loss string."""
import numpy as np
import pytest

from cmb_lcdm_sr.sr import (
    INPUT_ALIASES,
    INPUT_CONFIGS,
    JULIA_LOSS_GMM_MI,
    build_inputs,
    resolve_input_config,
)


def _fake_theta(n=1000, seed=0):
    rng = np.random.default_rng(seed)
    theta = np.empty((n, 6))
    theta[:, 0] = rng.uniform(0.02, 0.024, n)     # omega_b
    theta[:, 1] = rng.uniform(0.10, 0.13, n)      # omega_cdm
    theta[:, 2] = rng.uniform(62, 80, n)          # H0
    theta[:, 3] = rng.uniform(0.010, 0.130, n)    # tau_reio
    theta[:, 4] = rng.uniform(2.90, 3.18, n)      # ln10^{10}A_s
    theta[:, 5] = rng.uniform(0.92, 1.01, n)      # n_s
    return theta


def test_build_inputs_As_tau():
    theta = _fake_theta()
    X, labels = build_inputs(theta, ["A_s", "tau"])
    assert labels == ["A_s", "tau"]
    assert X.shape == (len(theta), 2)
    assert np.allclose(X[:, 0], np.exp(theta[:, 4]) * 1e-10)
    assert np.allclose(X[:, 1], theta[:, 3])
    # tau_reio aliases to the same column with label "tau"
    X2, labels2 = build_inputs(theta, ["tau_reio"])
    assert labels2 == ["tau"]
    assert np.allclose(X2[:, 0], theta[:, 3])


def test_build_inputs_unknown_name():
    with pytest.raises(ValueError, match="Unknown input name"):
        build_inputs(_fake_theta(8), ["sigma_8"])


def test_named_float64_input_configs_are_exact_and_isolated():
    theta = _fake_theta(32)
    expected = {
        "raw64": np.column_stack([
            theta[:, 0], theta[:, 1], theta[:, 2], theta[:, 3],
            np.exp(theta[:, 4]) * 1e-10, theta[:, 5],
        ]),
        "physical_o1_64": np.column_stack([
            100.0 * theta[:, 0], 10.0 * theta[:, 1], theta[:, 2] / 100.0,
            theta[:, 3], np.exp(theta[:, 4]) / 10.0, theta[:, 5],
        ]),
        "logamp64": theta[:, [0, 1, 2, 3, 4, 5]],
    }
    expected_labels = {
        "raw64": ["omega_b", "omega_cdm", "H0", "tau", "A_s", "n_s"],
        "physical_o1_64": ["wb100", "wc10", "h", "tau", "A9", "n_s"],
        "logamp64": ["omega_b", "omega_cdm", "H0", "tau", "ln10As", "n_s"],
    }
    assert set(INPUT_CONFIGS) == set(expected)
    for name in expected:
        spec = resolve_input_config(name)
        X, labels = build_inputs(theta, spec["inputs"])
        assert labels == expected_labels[name]
        np.testing.assert_allclose(X, expected[name], rtol=1e-14, atol=0.0)
        assert spec["pysr_kwargs"] == {
            "precision": 64, "print_precision": 17}
        assert list(spec["sampled_expressions"]) == labels


def test_input_config_resolution_is_defensive_and_rejects_unknown():
    spec = resolve_input_config("raw64")
    spec["inputs"][0] = "tau"
    spec["pysr_kwargs"]["precision"] = 32
    assert resolve_input_config("raw64")["inputs"][0] == "omega_b"
    assert resolve_input_config("raw64")["pysr_kwargs"]["precision"] == 64
    with pytest.raises(ValueError, match="Unknown input config"):
        resolve_input_config("not_an_arm")


def test_julia_loss_string_sanity():
    # The loss is a source-code artifact handed to PySR; guard its key traits.
    assert "function eval_loss(tree, dataset::Dataset{T,L}, options) where {T,L}" in JULIA_LOSS_GMM_MI
    assert "_gmm_mi_2d" in JULIA_LOSS_GMM_MI
    assert "N_INNER = 300" in JULIA_LOSS_GMM_MI
    assert "exp(-max(mi, L(0)))" in JULIA_LOSS_GMM_MI
    # balanced function/end blocks (crude but catches truncation)
    assert JULIA_LOSS_GMM_MI.count("function ") == 5
    assert JULIA_LOSS_GMM_MI.count("\nend\n") >= 5


def test_alias_table_covers_theta_columns():
    theta = _fake_theta(16)
    for name in INPUT_ALIASES:
        X, labels = build_inputs(theta, [name])
        assert X.shape == (16, 1)
        assert len(labels) == 1
