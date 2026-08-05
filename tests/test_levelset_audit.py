"""Phase-7a level-set audit: E_inv discriminates sufficient from confounded
coordinates, random-pair normalisation sits at 1, the matched-nuisance
response test catches hidden confounders, and degenerate supports are
handled."""
import pathlib
import sys

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

import levelset_audit as la  # noqa: E402

MID = np.array([0.022, 0.115, 71.0, 0.07, 3.04, 0.965])
HALF = np.array([0.002, 0.015, 9.0, 0.04, 0.14, 0.025])
CFG = {"n_bins": 100, "pairs_per_bin": 10, "bin_cap": 300,
       "n_boot": 100, "n_seeds": 300, "k_nn": 30, "caliper_q": 0.05}


@pytest.fixture(scope="module")
def world():
    rng = np.random.default_rng(0)
    n = 4000
    theta = MID + (2.0 * rng.random((n, 6)) - 1.0) * HALF
    u = (theta - MID) / HALF
    return theta, u, rng


def test_sufficient_coordinate_is_invariant(world):
    theta, u, _ = world
    rng = np.random.default_rng(1)
    mu = 2.0 * np.tanh(u[:, 3]) + 0.02 * rng.standard_normal(len(u))
    out = la.audit_levelsets("tau", mu, theta, u, CFG, seed=0)
    assert out["support"] == ["tau"]
    assert set(out["complement"]) == {"omega_b", "omega_cdm", "H0",
                                      "ln10As", "n_s"}
    assert out["n_pairs"] > 500
    assert out["e_inv"] < 0.05                       # frozen threshold
    assert out["e_inv_top_quartile"] < 0.05          # even at large moves
    assert 0.7 < out["e_inv_random_ref"] < 1.3       # normalisation ~ 1
    assert out["response"]["r2_response"] > 0.95
    assert out["levelset_pass"] is True


def test_confounded_coordinate_fails(world):
    theta, u, _ = world
    rng = np.random.default_rng(2)
    mu = 2.0 * np.tanh(u[:, 3]) + 1.0 * u[:, 5] \
        + 0.02 * rng.standard_normal(len(u))
    out = la.audit_levelsets("tau", mu, theta, u, CFG, seed=0)
    assert out["e_inv"] > 0.2                        # far above threshold
    assert out["response"]["r2_response"] < 0.9      # confounder breaks 1-D
    assert out["levelset_pass"] is False


def test_wrong_latent_not_invariant(world):
    theta, u, _ = world
    rng = np.random.default_rng(3)
    mu_other = u[:, 5] + 0.02 * rng.standard_normal(len(u))
    out = la.audit_levelsets("tau", mu_other, theta, u, CFG, seed=0)
    assert out["e_inv"] > 0.5                        # specificity control


def test_full_support_has_no_nuisance_direction(world):
    theta, u, _ = world
    rng = np.random.default_rng(4)
    expr = "omega_b + omega_cdm + H0 + tau + A_s + n_s"
    mu = theta @ np.ones(6) + 0.01 * rng.standard_normal(len(u))
    out = la.audit_levelsets(expr, mu, theta, u, CFG, seed=0)
    assert out["complement"] == []
    assert out["e_inv"] is None and out["levelset_pass"] is None
    assert out["response"]["r2_response"] is not None   # unconditional R2


def test_deterministic_and_curve_shape(world):
    theta, u, _ = world
    rng = np.random.default_rng(5)
    mu = 2.0 * np.tanh(u[:, 3]) + 0.05 * rng.standard_normal(len(u))
    a = la.audit_levelsets("tau", mu, theta, u, CFG, seed=7)
    b = la.audit_levelsets("tau", mu, theta, u, CFG, seed=7)
    assert a["e_inv"] == b["e_inv"]
    assert a["response"]["r2_response"] == b["response"]["r2_response"]
    curve = a["e_inv_curve"]
    assert 1 <= len(curve) <= 4
    assert sum(c["n_pairs"] for c in curve) == a["n_pairs"]


def test_pair_within_bins_disjoint_and_far():
    rng = np.random.default_rng(6)
    f = rng.random(1000)
    u_comp = rng.uniform(-1, 1, size=(1000, 2))
    i, j, d = la.pair_within_bins(f, u_comp, n_bins=20, pairs_per_bin=5,
                                  rng=np.random.default_rng(0))
    used = np.concatenate([i, j])
    assert len(used) == len(np.unique(used))         # disjoint
    # each pair stays within its f bin (delta <= bin width by construction)
    assert np.all(np.abs(f[i] - f[j]) < 0.11)
    # matched pairs are farther in nuisance space than random ones
    rand = np.sqrt(((u_comp[rng.integers(0, 1000, 500)]
                     - u_comp[rng.integers(0, 1000, 500)]) ** 2).sum(-1))
    assert d.mean() > rand.mean()
