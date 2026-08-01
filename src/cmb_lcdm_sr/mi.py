"""Post-hoc GMM-MI estimation (Piras+2023, https://github.com/dpiras/GMM-MI).

This is the *selection* metric of the blind-SR pipeline: every Pareto-front
equation PySR returns is re-scored by GMM-MI between its prediction and the
latent on a held-out validation split. It shares one invariance class with the
Julia inner loss (any bijection of either variable leaves both unchanged), so
search and selection reward the same thing: functional dependence, not
calibration to the latent's scale.

The full estimator (component-count selection K=1..5, k-fold CV, bootstrap
uncertainty) is intentionally used here — post-hoc cost is negligible. The
inner loop uses the fast fixed-K=2 pure-Julia estimator in ``sr.py`` instead.
"""
from __future__ import annotations

import warnings

import numpy as np


def _standardize(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=np.float64)
    mu = a.mean(axis=0, keepdims=True)
    sd = a.std(axis=0, keepdims=True)
    sd = np.where(sd < 1e-12, 1.0, sd)
    return (a - mu) / sd


def mutual_information_gmm(
    latents: np.ndarray,
    params: np.ndarray,
    return_uncertainty: bool = False,
    max_samples: int | None = 5000,
    seed: int = 0,
) -> np.ndarray | tuple[np.ndarray, np.ndarray]:
    """MI[(latent_i ; param_j)] -> (n_latent, n_param) using GMM-MI.

    Both inputs are standardised first. ``max_samples`` subsamples large
    arrays for speed (GMM-MI bootstraps internally).
    """
    from gmm_mi.mi import EstimateMI  # imported lazily

    L = _standardize(latents)
    P = _standardize(params)
    if max_samples is not None and L.shape[0] > max_samples:
        rng = np.random.default_rng(seed)
        idx = rng.choice(L.shape[0], size=max_samples, replace=False)
        L = L[idx]; P = P[idx]

    n_lat, n_par = L.shape[1], P.shape[1]
    mi = np.zeros((n_lat, n_par))
    err = np.zeros((n_lat, n_par))
    for i in range(n_lat):
        for j in range(n_par):
            X = np.column_stack([L[:, i], P[:, j]])
            try:
                m, s = EstimateMI().fit_estimate(X)
            except Exception as exc:                       # noqa: BLE001
                warnings.warn(f"GMM-MI failed on (z{i}, p{j}): {exc}")
                m, s = np.nan, np.nan
            mi[i, j] = m
            err[i, j] = s
    return (mi, err) if return_uncertainty else mi
