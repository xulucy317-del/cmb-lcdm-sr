"""SR input construction and the Julia loss string."""
import numpy as np
import pytest

from cmb_lcdm_sr.sr import (
    INPUT_ALIASES,
    JULIA_LOSS_GMM_MI,
    build_inputs,
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
