"""Joint (f1, f2) level-set audit: invariance holds when mu = F(f1) + G(f2)
(where the f1-only audit correctly fails), a hidden confounder still breaks
it, full-support unions degenerate gracefully, and the joint cells really
pin both coordinates."""
import pathlib
import sys

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

import levelset_audit as la  # noqa: E402
import levelset_audit_joint as laj  # noqa: E402

from cmb_lcdm_sr import semantics  # noqa: E402

MID = np.array([0.022, 0.115, 71.0, 0.07, 3.04, 0.965])
HALF = np.array([0.002, 0.015, 9.0, 0.04, 0.14, 0.025])
CFG = {"n_bins_axis": 12, "pairs_per_bin": 10, "bin_cap": 300,
       "n_boot": 100, "n_seeds": 300, "k_nn": 30, "caliper_q": 0.05}
CFG_1D = {"n_bins": 100, "pairs_per_bin": 10, "bin_cap": 300,
          "n_boot": 100, "n_seeds": 300, "k_nn": 30, "caliper_q": 0.05}


@pytest.fixture(scope="module")
def world():
    rng = np.random.default_rng(0)
    n = 4000
    theta = MID + (2.0 * rng.random((n, 6)) - 1.0) * HALF
    u = (theta - MID) / HALF
    rng_mu = np.random.default_rng(1)
    # two-coordinate latent: F(tau) + G(n_s) + small noise
    mu = 2.0 * np.tanh(u[:, 3]) + 1.0 * u[:, 5] \
        + 0.02 * rng_mu.standard_normal(n)
    yhat = 2.0 * np.tanh(u[:, 3]) + 1.0 * u[:, 5]
    comp_idx = [0, 1, 2, 4]                      # complement of {tau, n_s}
    return theta, u, mu, yhat, comp_idx


def test_joint_invariance_where_f1_alone_fails(world):
    theta, u, mu, yhat, comp_idx = world
    # f1 alone leaves the G(n_s) term in the level sets -> 7a-style FAIL
    out1 = la.audit_levelsets("tau", mu, theta, u, CFG_1D, seed=0)
    assert out1["e_inv"] > 0.2
    # jointly conditioning on (f1, f2) restores invariance
    out = laj.audit_joint(theta[:, 3], theta[:, 5], yhat, mu,
                          u[:, comp_idx], CFG, seed=0)
    assert out["n_pairs"] > 300
    assert out["e_inv"] < 0.05
    assert 0.7 < out["e_inv_random_ref"] < 1.3
    assert out["response"]["r2_response"] > 0.95
    assert out["levelset_pass"] is True


def test_hidden_confounder_still_fails(world):
    theta, u, _mu, yhat, comp_idx = world
    rng = np.random.default_rng(2)
    mu_c = 2.0 * np.tanh(u[:, 3]) + 1.0 * u[:, 5] + 0.8 * u[:, 1] \
        + 0.02 * rng.standard_normal(len(u))
    out = laj.audit_joint(theta[:, 3], theta[:, 5], yhat, mu_c,
                          u[:, comp_idx], CFG, seed=0)
    assert out["e_inv"] > 0.2
    assert out["response"]["r2_response"] < 0.9
    assert out["levelset_pass"] is False


def test_full_union_degenerates_to_none(world):
    theta, u, mu, yhat, _ = world
    out = laj.audit_joint(theta[:, 3], theta[:, 5], yhat, mu,
                          u[:, :0], CFG, seed=0)
    assert out["e_inv"] is None
    assert out["levelset_pass"] is None
    assert "no nuisance direction" in out["note"]
    assert out["response"]["r2_response"] > 0.95   # response leg still runs


def test_joint_cells_pin_both_coordinates(world):
    theta, u, _mu, _yhat, comp_idx = world
    nb = CFG["n_bins_axis"]
    f1v, f2v = theta[:, 3], theta[:, 5]
    cells = (la.quantile_bins(f1v, nb) * (nb + 1)
             + la.quantile_bins(f2v, nb))
    i, j, _ = la.pair_within_bins(f1v, u[:, comp_idx], bins=cells,
                                  pairs_per_bin=CFG["pairs_per_bin"],
                                  bin_cap=CFG["bin_cap"],
                                  rng=np.random.default_rng(0))
    assert len(i) > 300
    assert np.array_equal(cells[i], cells[j])     # pairs never cross cells


def test_joint_support_union():
    e1 = semantics.parse_expr("A_s*exp(-2*tau)")
    e2 = semantics.parse_expr("H0*omega_cdm/n_s")
    support, comp = laj.joint_support(e1, e2)
    assert set(support) == {"tau", "ln10As", "H0", "omega_cdm", "n_s"}
    assert comp == ["omega_b"]
