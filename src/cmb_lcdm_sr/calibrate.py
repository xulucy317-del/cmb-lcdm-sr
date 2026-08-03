"""Cross-fitted 1-D calibration h and residual diagnostics.

Phase-0 infrastructure of ``docs/discovery_roadmap.md`` (M4), used by the
Phase-3 sufficiency audit and the Phase-6 residual targets. The MI protocol
identifies a discovered coordinate f only up to a bijection of its output, so
sufficiency must be tested on the residual

    e_k(θ) = μ_k(θ) − h(f(θ))

after fitting an arbitrary scalar calibration h — never on raw MSE. h is fit
by K-fold *cross-fitting* (each row's prediction comes from a fold-model that
never saw it), so a flexible h cannot fake sufficiency.

Default h is **monotone** (the MI-equivalence class on an interval): isotonic
regression on quantile-bin means, interpolated with a monotonicity-preserving
PCHIP, flat beyond the observed range. ``monotone=False`` gives the general
(non-monotone) fallback — its use must be flagged on the latent card.

Residual diagnostics (frozen thresholds in roadmap §0.3):
* cross-validated R²(e ← θ) with a gradient-boosted regressor, plus a
  row-permutation null (pass: R²_res ≤ 0.05 and ≤ null 97.5th percentile);
* per-parameter GMM-MI Î(e; θ_j) (reusing ``mi.mutual_information_gmm``),
  with an optional permutation null (pass: ≤ null 97.5th percentile).
"""
from __future__ import annotations

from typing import Callable, Optional

import numpy as np


# --- the 1-D calibration h ---------------------------------------------------

def _spearman_sign(x: np.ndarray, y: np.ndarray) -> float:
    from scipy.stats import spearmanr

    rho = spearmanr(x, y).statistic
    return 1.0 if (not np.isfinite(rho)) or rho >= 0 else -1.0


def fit_h(x: np.ndarray, y: np.ndarray, n_bins: int = 64,
          monotone: bool = True) -> Callable[[np.ndarray], np.ndarray]:
    """Fit h on (x, y) → callable. Quantile-bin means → (isotonic) → PCHIP."""
    from scipy.interpolate import PchipInterpolator

    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    edges = np.unique(np.quantile(x, np.linspace(0.0, 1.0, n_bins + 1)))
    if len(edges) < 3:                      # (near-)constant x — no information
        const = float(y.mean())
        return lambda xn: np.full(np.asarray(xn).shape, const)

    idx = np.clip(np.searchsorted(edges, x, side="right") - 1, 0, len(edges) - 2)
    centers, means = [], []
    for b in range(len(edges) - 1):
        m = idx == b
        if m.any():
            centers.append(float(x[m].mean()))
            means.append(float(y[m].mean()))
    centers = np.array(centers)
    means = np.array(means)
    if len(centers) < 2:
        const = float(y.mean())
        return lambda xn: np.full(np.asarray(xn).shape, const)

    if monotone:
        from sklearn.isotonic import IsotonicRegression

        increasing = _spearman_sign(x, y) > 0
        means = IsotonicRegression(increasing=increasing).fit_transform(centers, means)

    interp = PchipInterpolator(centers, means)  # monotone data → monotone curve
    lo, hi = centers[0], centers[-1]

    def h(xn: np.ndarray) -> np.ndarray:
        return interp(np.clip(np.asarray(xn, dtype=np.float64), lo, hi))

    return h


def crossfit_calibration(f_vals: np.ndarray, y: np.ndarray, n_folds: int = 5,
                         n_bins: int = 64, monotone: bool = True,
                         seed: int = 0) -> dict:
    """Cross-fitted ŷ = h(f) and residual e = y − ŷ.

    Rows where f is non-finite get NaN predictions/residuals. Returns
    ``{"yhat", "residual", "h_full", "r2_cal", "monotone", "finite_frac"}``
    with r2_cal the cross-fitted R² of ŷ against y (the *calibration* fit
    quality, not a sufficiency verdict).
    """
    f_vals = np.asarray(f_vals, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    n = len(y)
    finite = np.isfinite(f_vals) & np.isfinite(y)
    yhat = np.full(n, np.nan)

    rows = np.where(finite)[0]
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(rows))
    folds = np.array_split(perm, n_folds)
    for hold in folds:
        if len(hold) == 0:
            continue
        train = rows[np.setdiff1d(perm, hold, assume_unique=True)]
        test = rows[hold]
        h = fit_h(f_vals[train], y[train], n_bins=n_bins, monotone=monotone)
        yhat[test] = h(f_vals[test])

    residual = y - yhat
    yv, yh = y[finite], yhat[finite]
    ss_res = float(np.sum((yv - yh) ** 2))
    ss_tot = float(np.sum((yv - yv.mean()) ** 2))
    r2_cal = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return {
        "yhat": yhat,
        "residual": residual,
        "h_full": fit_h(f_vals[finite], y[finite], n_bins=n_bins, monotone=monotone),
        "r2_cal": r2_cal,
        "monotone": monotone,
        "finite_frac": float(finite.mean()),
    }


# --- residual diagnostics ----------------------------------------------------

def _crossval_r2(e: np.ndarray, theta: np.ndarray, n_folds: int, seed: int,
                 max_iter: int = 100) -> float:
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.model_selection import KFold, cross_val_score
    from threadpoolctl import threadpool_limits

    model = HistGradientBoostingRegressor(random_state=seed, max_iter=max_iter)
    cv = KFold(n_splits=n_folds, shuffle=True, random_state=seed)
    # Single-threaded on purpose: HistGBM's OpenMP pool spin-waits itself to
    # death on this data size (measured 121 s vs 1.9 s for one crossval on an
    # M-series Mac); parallelism belongs at the per-latent caller level.
    with threadpool_limits(limits=1):
        scores = cross_val_score(model, theta, e, scoring="r2", cv=cv)
    return float(scores.mean())


def residual_diagnostics(residual: np.ndarray, theta: np.ndarray,
                         n_folds: int = 5, seed: int = 0, n_perm_r2: int = 10,
                         compute_mi: bool = True, n_perm_mi: int = 0,
                         max_samples_mi: Optional[int] = 5000,
                         gbm_max_iter: int = 100) -> dict:
    """Is the residual still predictable from θ?

    Returns ``{"r2_res", "r2_null", "r2_null_p975", "n_rows",
    "mi" (6,), "mi_err" (6,), "mi_null" (n_perm_mi, 6), "mi_null_p975" (6,)}``
    (MI keys None when disabled). Null distributions come from re-running the
    identical pipeline on row-permuted residuals.
    """
    residual = np.asarray(residual, dtype=np.float64)
    theta = np.asarray(theta, dtype=np.float64)
    finite = np.isfinite(residual)
    e, th = residual[finite], theta[finite]
    rng = np.random.default_rng(seed)

    r2 = _crossval_r2(e, th, n_folds, seed, max_iter=gbm_max_iter)
    r2_null = np.array([_crossval_r2(rng.permutation(e), th, n_folds,
                                     seed + 1 + p, max_iter=gbm_max_iter)
                        for p in range(n_perm_r2)])
    out = {
        "r2_res": r2,
        "r2_null": r2_null,
        "r2_null_p975": float(np.quantile(r2_null, 0.975)) if len(r2_null) else None,
        "n_rows": int(finite.sum()),
        "mi": None, "mi_err": None, "mi_null": None, "mi_null_p975": None,
    }

    if compute_mi:
        from .mi import mutual_information_gmm

        mi, err = mutual_information_gmm(
            e.reshape(-1, 1), th, return_uncertainty=True,
            max_samples=max_samples_mi, seed=seed,
        )
        out["mi"], out["mi_err"] = mi[0], err[0]
        if n_perm_mi > 0:
            null = np.stack([
                mutual_information_gmm(
                    rng.permutation(e).reshape(-1, 1), th,
                    return_uncertainty=False, max_samples=max_samples_mi,
                    seed=seed + 1 + p,
                )[0]
                for p in range(n_perm_mi)
            ])
            out["mi_null"] = null
            out["mi_null_p975"] = np.quantile(null, 0.975, axis=0)
    return out
