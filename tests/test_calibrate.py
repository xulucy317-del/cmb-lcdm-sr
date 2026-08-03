"""Cross-fitted calibration h + residual diagnostics (roadmap M4)."""
import numpy as np
import pytest

pytest.importorskip("sklearn")

from cmb_lcdm_sr import calibrate, semantics, tiers


@pytest.fixture(scope="module")
def setup(repo_root):
    mid, half = tiers.load_prior_box(repo_root / "data")
    rng = np.random.default_rng(11)
    theta = mid + (2.0 * rng.random((3000, 6)) - 1.0) * half
    f = semantics.evaluate_on_theta("A_s*(tau - 0.57)", theta)
    f_std = (f - f.mean()) / f.std()
    return theta, f_std, rng


def test_monotone_calibration_recovers_wrapper(setup):
    theta, f, rng = setup
    y = np.tanh(f) + 0.1 * rng.normal(size=len(f))
    cal = calibrate.crossfit_calibration(f, y, monotone=True, seed=0)
    assert cal["finite_frac"] == 1.0
    assert cal["r2_cal"] > 0.95
    # h_full is usable on new points and monotone over the observed range
    grid = np.linspace(f.min(), f.max(), 200)
    hg = cal["h_full"](grid)
    assert (np.diff(hg) >= -1e-9).all()


def test_clean_residual_passes_null(setup):
    theta, f, rng = setup
    y = np.tanh(f) + 0.1 * rng.normal(size=len(f))
    cal = calibrate.crossfit_calibration(f, y, monotone=True, seed=0)
    diag = calibrate.residual_diagnostics(cal["residual"], theta, n_folds=3,
                                          n_perm_r2=3, compute_mi=False,
                                          gbm_max_iter=25, seed=0)
    assert diag["r2_res"] < 0.05
    assert diag["r2_res"] <= diag["r2_null_p975"] + 0.05


def test_structured_residual_detected_and_attributed(setup, repo_root):
    theta, f, rng = setup
    mid, half = tiers.load_prior_box(repo_root / "data")
    u_ns = (theta[:, 5] - mid[5]) / half[5]
    y = np.tanh(f) + 0.5 * u_ns + 0.1 * rng.normal(size=len(f))
    cal = calibrate.crossfit_calibration(f, y, monotone=True, seed=0)
    # MI attribution on a 2-column slice (tau vs n_s): the full 6-param
    # gmm-mi pass costs ~10 min and belongs to the Phase-3 audit, not pytest.
    diag = calibrate.residual_diagnostics(cal["residual"], theta[:, [3, 5]],
                                          n_folds=3, n_perm_r2=3,
                                          compute_mi=True, max_samples_mi=600,
                                          gbm_max_iter=25, seed=0)
    assert diag["r2_res"] > 0.3
    assert diag["r2_res"] > diag["r2_null_p975"]
    assert int(np.nanargmax(diag["mi"])) == 1          # n_s carries the residual


def test_general_fallback_needed_for_non_monotone(setup):
    theta, f, rng = setup
    y = f**2 + 0.05 * rng.normal(size=len(f))
    mono = calibrate.crossfit_calibration(f, y, monotone=True, seed=0)
    general = calibrate.crossfit_calibration(f, y, monotone=False, seed=0)
    assert general["r2_cal"] > 0.9
    assert general["r2_cal"] > mono["r2_cal"] + 0.3
    assert mono["monotone"] and not general["monotone"]


def test_degenerate_and_masked_inputs(setup):
    theta, f, rng = setup
    y = np.tanh(f)
    # constant coordinate carries nothing — mean predictor, r2 ≈ 0, no crash
    const = calibrate.crossfit_calibration(np.ones_like(f), y, seed=0)
    assert const["r2_cal"] == pytest.approx(0.0, abs=0.01)
    # NaNs in f propagate to yhat/residual, finite rows unaffected
    f_masked = f.copy()
    f_masked[:100] = np.nan
    cal = calibrate.crossfit_calibration(f_masked, y, seed=0)
    assert np.isnan(cal["yhat"][:100]).all()
    assert np.isfinite(cal["yhat"][100:]).all()
    assert cal["finite_frac"] == pytest.approx(2900 / 3000)
