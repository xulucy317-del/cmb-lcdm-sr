"""Post-hoc GMM-MI estimator sanity (skipped if gmm-mi is not installed)."""
import numpy as np
import pytest

pytest.importorskip("gmm_mi")

from cmb_lcdm_sr.mi import mutual_information_gmm


def test_gmm_mi_correlated_gaussian():
    # For a bivariate Gaussian, MI = -0.5 * ln(1 - rho^2).
    rho = 0.8
    rng = np.random.default_rng(0)
    n = 3000
    x = rng.normal(size=n)
    y = rho * x + np.sqrt(1 - rho**2) * rng.normal(size=n)
    truth = -0.5 * np.log(1 - rho**2)          # ≈ 0.511 nat

    mi, err = mutual_information_gmm(
        x.reshape(-1, 1), y.reshape(-1, 1),
        return_uncertainty=True, max_samples=n, seed=0,
    )
    assert mi.shape == (1, 1)
    assert mi[0, 0] == pytest.approx(truth, abs=0.1)
    assert err[0, 0] >= 0


def test_gmm_mi_independent_near_zero():
    rng = np.random.default_rng(1)
    x = rng.normal(size=2000).reshape(-1, 1)
    y = rng.normal(size=2000).reshape(-1, 1)
    mi = mutual_information_gmm(x, y, max_samples=2000, seed=0)
    assert abs(mi[0, 0]) < 0.05
