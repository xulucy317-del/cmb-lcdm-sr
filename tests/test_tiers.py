"""Evaluation tiers + prior-box geometry (roadmap Phase 0, M3)."""
import numpy as np

from cmb_lcdm_sr import tiers


def test_tiers_partition_the_test_split():
    assert tiers.T0.start == 0 and tiers.T0.stop == tiers.T1.start
    assert tiers.T1.stop == tiers.T2.start and tiers.T2.stop == 50_000
    assert tiers.T0_FIT.stop == tiers.T0_VAL.start and tiers.T0_VAL.stop == tiers.T0.stop
    # anchors sit at the start of T1, never touching the SR slice
    assert tiers.ANCHORS.start == tiers.T1.start
    assert tiers.ANCHORS.stop - tiers.ANCHORS.start == tiers.N_ANCHORS
    assert tiers.ANCHORS.stop <= tiers.T1.stop


def test_prior_box_matches_meta(repo_root):
    mid, half = tiers.load_prior_box(repo_root / "data")
    assert mid.shape == half.shape == (6,)
    assert (half > 0).all()
    # spot-check tau_reio in [0.01, 0.13] and H0 in [62, 80]
    import pytest
    j_tau = tiers.THETA_ORDER.index("tau_reio")
    assert mid[j_tau] == pytest.approx(0.07) and half[j_tau] == pytest.approx(0.06)
    j_h0 = tiers.THETA_ORDER.index("H0")
    assert mid[j_h0] == 71.0 and half[j_h0] == 9.0


def test_theta_to_u_maps_box_to_unit_cube(repo_root):
    mid, half = tiers.load_prior_box(repo_root / "data")
    assert np.allclose(tiers.theta_to_u(mid + half, mid, half), 1.0)
    assert np.allclose(tiers.theta_to_u(mid - half, mid, half), -1.0)
    assert np.allclose(tiers.theta_to_u(mid, mid, half), 0.0)


def test_split_and_tier_shapes(repo_root):
    idx = tiers.split_test_indices(repo_root / "data")
    assert idx.shape == (50_000,)
    assert (np.diff(idx) > 0).all()          # file order — cache row alignment
    anchors = tiers.anchor_theta(repo_root / "data")
    assert anchors.shape == (tiers.N_ANCHORS, 6)
    mid, half = tiers.load_prior_box(repo_root / "data")
    u = tiers.theta_to_u(anchors, mid, half)
    assert np.abs(u).max() <= 1.0 + 1e-9     # anchors live inside the prior box
