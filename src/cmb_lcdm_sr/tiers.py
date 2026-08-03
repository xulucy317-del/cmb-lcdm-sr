"""Evaluation tiers over the 50k-row test split + prior-box geometry.

Phase-0 infrastructure of ``docs/discovery_roadmap.md`` (§0.4). The SR
protocol only ever touches the first 5000 test rows; every validation-grade
statistic in later phases is computed on rows the search never saw:

    T0 [    0 :  5000)   SR fit + val (4000/1000) — the existing protocol slice
    T1 [ 5000 : 25000)   calibration h, residual audits, semantic anchors,
                         level-set pairs
    T2 [25000 : 50000)   confirmatory card numbers, computed once

ANCHORS — the first 2048 rows of T1 — is the fixed evaluation set used by
``semantics.py`` for the output- and gradient-equivalence tests, so cluster
membership is deterministic across runs and machines.

All slices index *positions within the test split* (rows of
``encoder_means_test.npy``), i.e. ``theta[split_test_indices(...)][T1]`` and
``means[T1]`` are row-aligned.

Also here: the prior box in the *sampled* basis — ``theta.npy`` column order
``(omega_b, omega_cdm, H0, tau_reio, ln10^{10}A_s, n_s)`` from
``data/meta.json`` — and the u-coordinates u_j = (θ_j − mid_j)/half_j in
which gradient signatures are comparable across parameters (the A_s axis is
ln10^{10}A_s, matching how the LHS was drawn).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

# --- tier slices (positions within the test split) ---------------------------
T0 = slice(0, 5000)
T0_FIT = slice(0, 4000)
T0_VAL = slice(4000, 5000)
T1 = slice(5000, 25000)
T2 = slice(25000, 50000)

N_ANCHORS = 2048
ANCHORS = slice(T1.start, T1.start + N_ANCHORS)

# theta.npy column order = data/meta.json prior_keys (the sampled basis).
THETA_ORDER = ["omega_b", "omega_cdm", "H0", "tau_reio", "ln10^{10}A_s", "n_s"]
# The SR-facing labels of the same columns (sr.INPUT_ALIASES output labels).
SAMPLED_LABELS = ["omega_b", "omega_cdm", "H0", "tau", "ln10As", "n_s"]


def split_test_indices(dataset_dir: str | Path = "data") -> np.ndarray:
    """Dataset row indices of the test split (split_id == 2), in file order.

    This is exactly the ordering run_blind_sr.py uses, so position i here is
    row i of the encoder means/logvars caches.
    """
    splits = np.load(Path(dataset_dir) / "splits_v1.npz")
    return np.where(splits["split_id"] == 2)[0]


def tier_theta(dataset_dir: str | Path = "data", tier: slice = T1) -> np.ndarray:
    """theta rows (n, 6) of one tier, in the sampled basis."""
    theta = np.load(Path(dataset_dir) / "theta.npy")
    return theta[split_test_indices(dataset_dir)[tier]]


def anchor_theta(dataset_dir: str | Path = "data") -> np.ndarray:
    """The fixed (N_ANCHORS, 6) anchor rows (start of T1)."""
    return tier_theta(dataset_dir, ANCHORS)


def load_prior_box(dataset_dir: str | Path = "data") -> tuple[np.ndarray, np.ndarray]:
    """(mid, half) of the LHS prior box, both (6,), in THETA_ORDER."""
    with open(Path(dataset_dir) / "meta.json") as f:
        meta = json.load(f)
    keys = meta["prior_keys"]
    if keys != THETA_ORDER:
        raise ValueError(f"unexpected prior_keys {keys}; expected {THETA_ORDER}")
    lo = np.array([meta["priors"][k][0] for k in keys], dtype=np.float64)
    hi = np.array([meta["priors"][k][1] for k in keys], dtype=np.float64)
    return (lo + hi) / 2.0, (hi - lo) / 2.0


def theta_to_u(theta: np.ndarray, mid: np.ndarray, half: np.ndarray) -> np.ndarray:
    """Standardise sampled-basis theta rows to the prior box: box → [−1, 1]⁶."""
    return (np.asarray(theta, dtype=np.float64) - mid) / half
