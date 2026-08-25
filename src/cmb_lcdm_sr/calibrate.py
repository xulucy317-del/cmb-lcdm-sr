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


def _perm_mi_call(args):
    """Module-level worker for the permutation-null MI pool (picklable)."""
    e_perm, th, max_samples_mi, call_seed = args
    from .mi import mutual_information_gmm

    return mutual_information_gmm(
        e_perm.reshape(-1, 1), th, return_uncertainty=False,
        max_samples=max_samples_mi, seed=call_seed,
    )[0]


def residual_diagnostics(residual: np.ndarray, theta: np.ndarray,
                         n_folds: int = 5, seed: int = 0, n_perm_r2: int = 10,
                         compute_mi: bool = True, n_perm_mi: int = 0,
                         max_samples_mi: Optional[int] = 5000,
                         gbm_max_iter: int = 100, mi_jobs: int = 1) -> dict:
    """Is the residual still predictable from θ?

    Returns ``{"r2_res", "r2_null", "r2_null_p975", "n_rows",
    "mi" (6,), "mi_err" (6,), "mi_null" (n_perm_mi, 6), "mi_null_p975" (6,)}``
    (MI keys None when disabled). Null distributions come from re-running the
    identical pipeline on row-permuted residuals.

    ``mi_jobs > 1`` evaluates the permutation-null MI calls in a process
    pool. The permutations themselves are always drawn sequentially from the
    same rng stream and each call keeps its own deterministic seed, so the
    result is bit-identical to the serial path.
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
            tasks = [(rng.permutation(e), th, max_samples_mi, seed + 1 + p)
                     for p in range(n_perm_mi)]
            if mi_jobs > 1:
                from concurrent.futures import ProcessPoolExecutor

                with ProcessPoolExecutor(max_workers=mi_jobs) as ex:
                    rows = list(ex.map(_perm_mi_call, tasks))
            else:
                rows = [_perm_mi_call(t) for t in tasks]
            null = np.stack(rows)
            out["mi_null"] = null
            out["mi_null_p975"] = np.quantile(null, 0.975, axis=0)
    return out


def _holdout_r2(e_train: np.ndarray, theta_train: np.ndarray,
                e_test: np.ndarray, theta_test: np.ndarray, seed: int,
                max_iter: int = 100) -> float:
    """Fit the frozen residual auditor on one tier and score another."""
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.metrics import r2_score
    from threadpoolctl import threadpool_limits

    model = HistGradientBoostingRegressor(random_state=seed, max_iter=max_iter)
    with threadpool_limits(limits=1):
        model.fit(theta_train, e_train)
        pred = model.predict(theta_test)
    return float(r2_score(e_test, pred))


def residual_diagnostics_holdout(
        residual_train: np.ndarray, theta_train: np.ndarray,
        residual_test: np.ndarray, theta_test: np.ndarray,
        seed: int = 0, n_perm_r2: int = 10, compute_mi: bool = True,
        n_perm_mi: int = 39, max_samples_mi: Optional[int] = 5000,
        gbm_max_iter: int = 100, mi_jobs: int = 1) -> dict:
    """Frozen T1→T2 residual audit used by confirmatory experiments.

    The HistGradientBoosting auditor is fit on ``(theta_train,
    residual_train)`` and scored once on the disjoint test tier.  R² nulls
    independently permute train and test residuals.  GMM-MI and its null are
    computed exclusively on the test tier, so observed values and thresholds
    always use identical rows and sample size.
    """
    residual_train = np.asarray(residual_train, dtype=np.float64)
    residual_test = np.asarray(residual_test, dtype=np.float64)
    theta_train = np.asarray(theta_train, dtype=np.float64)
    theta_test = np.asarray(theta_test, dtype=np.float64)
    finite_train = (np.isfinite(residual_train)
                    & np.isfinite(theta_train).all(axis=1))
    finite_test = (np.isfinite(residual_test)
                   & np.isfinite(theta_test).all(axis=1))
    e1, th1 = residual_train[finite_train], theta_train[finite_train]
    e2, th2 = residual_test[finite_test], theta_test[finite_test]
    if len(e1) < 16 or len(e2) < 16:
        raise ValueError("holdout residual audit requires at least 16 finite "
                         "rows in both train and test tiers")

    r2 = _holdout_r2(e1, th1, e2, th2, seed, max_iter=gbm_max_iter)
    r2_permutation_seeds = [seed + 1 + p for p in range(n_perm_r2)]
    r2_null = []
    for permutation_seed in r2_permutation_seeds:
        perm_rng = np.random.default_rng(permutation_seed)
        r2_null.append(_holdout_r2(
            perm_rng.permutation(e1), th1, perm_rng.permutation(e2), th2,
            permutation_seed, max_iter=gbm_max_iter))
    r2_null = np.asarray(r2_null, dtype=np.float64)
    out = {
        "r2_res": r2,
        "r2_null": r2_null,
        "r2_null_p975": (
            float(np.quantile(r2_null, 0.975)) if len(r2_null) else None),
        "observed_seed": int(seed),
        "r2_permutation_seeds": r2_permutation_seeds,
        "n_train": int(len(e1)),
        "n_test": int(len(e2)),
        "finite_frac_train": float(finite_train.mean()),
        "finite_frac_test": float(finite_test.mean()),
        "mi": None,
        "mi_err": None,
        "mi_null": None,
        "mi_null_p975": None,
        "mi_null_max_p975": None,
        "mi_permutation_seeds": [],
    }

    if compute_mi:
        from .mi import mutual_information_gmm

        mi, err = mutual_information_gmm(
            e2.reshape(-1, 1), th2, return_uncertainty=True,
            max_samples=max_samples_mi, seed=seed)
        out["mi"], out["mi_err"] = mi[0], err[0]
        if n_perm_mi > 0:
            mi_permutation_seeds = [seed + 1001 + p
                                    for p in range(n_perm_mi)]
            tasks = [
                (np.random.default_rng(permutation_seed).permutation(e2),
                 th2, max_samples_mi, permutation_seed)
                for permutation_seed in mi_permutation_seeds]
            if mi_jobs > 1:
                from concurrent.futures import ProcessPoolExecutor

                with ProcessPoolExecutor(max_workers=mi_jobs) as ex:
                    rows = list(ex.map(_perm_mi_call, tasks))
            else:
                rows = [_perm_mi_call(t) for t in tasks]
            null = np.stack(rows)
            out["mi_null"] = null
            out["mi_null_p975"] = np.quantile(null, 0.975, axis=0)
            out["mi_null_max_p975"] = float(np.quantile(
                np.nanmax(null, axis=1), 0.975))
            out["mi_permutation_seeds"] = mi_permutation_seeds
    return out
