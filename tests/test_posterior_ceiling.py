"""Phase-5 posterior ceiling: analytic Gaussian channel, clamp handling,
eta_post/DPI wiring, candidate assembly, and the latent worker end-to-end
on a shrunken synthetic world."""
import pathlib
import sys

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

import posterior_ceiling as pc  # noqa: E402
from cmb_lcdm_sr import tiers  # noqa: E402

MID = np.array([0.022, 0.115, 71.0, 0.07, 3.04, 0.965])
HALF = np.array([0.002, 0.015, 9.0, 0.04, 0.14, 0.025])


def test_gaussian_channel_matches_analytic():
    """mu ~ N(0,1), sigma^2 = 0.25 -> Z Gaussian, I = 1/2 ln(1 + 4)."""
    rng = np.random.default_rng(0)
    n = 20000
    mu = rng.standard_normal(n)
    logvar = np.full(n, np.log(0.25))
    out = pc.intrinsic_ceiling(mu, logvar, m_draws=4,
                               rng=np.random.default_rng(1), n_boot=200)
    i_true = 0.5 * np.log(1.0 + 1.0 / 0.25)
    assert abs(out["I"] - i_true) < 0.05
    assert out["K_bic"] <= 2                    # BIC should not overfit a Gaussian
    assert 0.0 < out["se"] < 0.05
    ns = pc.noise_summary(mu, logvar)
    assert abs(ns["i_gauss"] - i_true) < 0.03   # here the channel IS Gaussian
    assert ns["clamp_frac"] == 0.0


def test_conditional_term_uses_clamped_logvar():
    mu = np.zeros(128)
    lv = np.full(128, -30.0)                    # far below the model clamp
    ns = pc.noise_summary(mu, lv)
    assert ns["e_sigma2"] == pytest.approx(np.exp(-10.0))
    assert ns["clamp_frac"] == 1.0
    out = pc.intrinsic_ceiling(np.random.default_rng(2).standard_normal(2000),
                               np.full(2000, -30.0), m_draws=2,
                               rng=np.random.default_rng(3), n_boot=50)
    # conditional entropy computed at the clamp, not at exp(-30)
    assert out["H_cond"] == pytest.approx(0.5 * (pc.LN2PIE - 10.0))


def test_eta_post_and_dpi_on_sufficient_and_useless_coordinates():
    """mu = 2 tanh(u_tau), sigma = 0.3: quadrature truth I = 1.1237 nat.

    The cross-entropy ceiling must land on the truth; the GMM-MI numerator
    is allowed its known ~7% upward bias, which the same-estimator ratio
    eta_post_hat = MI(Z;f)/MI(Z;mu) and the estimator-consistent DPI check
    must absorb (that pair is exactly why the refinement exists).
    """
    rng = np.random.default_rng(4)
    n = 6000
    u = 2.0 * rng.random(n) - 1.0
    mu = 2.0 * np.tanh(u)
    logvar = np.full(n, 2.0 * np.log(0.3))
    ceil = pc.intrinsic_ceiling(mu, logvar, m_draws=4,
                                rng=np.random.default_rng(5), n_boot=100)
    assert abs(ceil["I"] - 1.1237) < 0.06       # matches quadrature truth
    z = mu + 0.3 * rng.standard_normal(n)

    mi, err, frac = pc.numerator_mi(z, u, max_samples=2000, seed=0)
    mi_ref, err_ref, _ = pc.numerator_mi(z, mu, max_samples=2000, seed=999)
    assert frac == 1.0 and mi is not None and mi_ref is not None

    eta, eta_se = pc.eta_with_se(mi, err, ceil["I"], ceil["se"])
    assert 0.8 < eta < 1.15                     # sufficient coordinate
    assert eta_se is not None and eta_se < 0.1
    eta_hat, _ = pc.eta_with_se(mi, err, mi_ref, err_ref)
    assert 0.9 < eta_hat < 1.1                  # shared bias cancels

    ok, margin_ref, margin_analytic = pc.dpi_check(
        mi, err, mi_ref, err_ref, ceil["I"], ceil["se"])
    assert ok                                   # estimator-consistent DPI
    assert margin_analytic is not None          # analytic margin still reported

    mi0, _err0, _ = pc.numerator_mi(z, rng.random(n), max_samples=2000, seed=1)
    eta0, _ = pc.eta_with_se(mi0, _err0, mi_ref, err_ref)
    assert eta0 < 0.2                           # independent coordinate

    # NaN-heavy candidate is refused, not mis-scored
    bad = np.where(rng.random(n) < 0.7, np.nan, u)
    mi_b, err_b, frac_b = pc.numerator_mi(z, bad, max_samples=2000, seed=2)
    assert mi_b is None and frac_b < 0.5


def test_assemble_candidates_dedupes_and_keeps_config_ids():
    sem_lat = {"canonical_cluster": 0,
               "clusters": [{"cluster": 0, "representative": "tau**2"}]}
    fin_lat = {
        "ref": {"best_expr": "tau + n_s", "best_c": 5},
        "s_star": {"config_id": "c1"},
        "entries": [
            {"config_id": "c1", "inputs": ["tau"], "size": 1,
             "best_expr": "tau**2", "best_c": 3},
            {"config_id": "c2", "inputs": ["tau", "n_s"], "size": 2,
             "best_expr": "tau + n_s", "best_c": 5},
        ],
    }
    cands = pc.assemble_candidates(sem_lat, fin_lat)
    assert len(cands) == 2
    c_canon = next(c for c in cands if c["expr"] == "tau**2")
    assert c_canon["kind"] == "canonical"       # canonical wins the merge
    assert c_canon["config_ids"] == ["canonical", "c1"]
    assert c_canon["inputs"] == ["tau"] and c_canon["size"] == 1
    c_ref = next(c for c in cands if c["expr"] == "tau + n_s")
    assert c_ref["config_ids"] == ["allparams", "c2"]


def test_latent_worker_end_to_end(tmp_path, monkeypatch):
    rng = np.random.default_rng(6)
    n = 3000
    monkeypatch.setattr(tiers, "T1", slice(500, 1500))
    monkeypatch.setattr(tiers, "T2", slice(1500, 3000))
    theta = MID + (2.0 * rng.random((n, 6)) - 1.0) * HALF
    mu = np.zeros((n, 1))
    mu[:, 0] = 2.0 * np.tanh((theta[:, 3] - MID[3]) / HALF[3])
    logvar = np.full((n, 1), 2.0 * np.log(0.3))
    (tmp_path / "analysis").mkdir(parents=True)
    np.save(tmp_path / "analysis" / "residual_z0_v1.npy",
            0.05 * rng.standard_normal(n))

    pc._G.clear()
    pc._G.update({
        "run": "lcdm_tt_beta3e-4", "run_dir": str(tmp_path),
        "mu": mu, "logvar": logvar,
        "theta_t2": theta[tiers.T2],
        "semantic": {"latents": {"z0": {
            "canonical_cluster": 0,
            "clusters": [{"cluster": 0, "representative": "tau"}]}}},
        "finals": {"latents": {"z0": {
            "ref": {"best_expr": "tau + 0.001*n_s", "best_c": 5},
            "s_star": {"config_id": "c1"},
            "entries": [{"config_id": "c1", "inputs": ["tau"], "size": 1,
                         "best_expr": "tau**2", "best_c": 3}]}}},
        "knee": {"latents": {"z0": {"plateau": {"mi_plat": 2.0}}}},
        "residual_fail": {0: True},
        "m_draws": 4, "n_boot": 50, "max_samples_mi": 1000,
    })
    out = pc._latent_worker(0)

    assert out["ceiling_ok"] and out["ceiling"]["I"] > 0.5
    assert out["mi_mu_ref"] is not None and out["eta_post_mu"] is not None
    etas = {c["expr"]: c["eta_post_hat"] for c in out["candidates"]}
    assert etas["tau"] is not None and etas["tau"] > 0.8
    assert out["canonical_eta_post_hat"] == etas["tau"]
    assert out["s_star_config"] == "c1"
    assert out["s_star_eta_post_hat"] == etas["tau**2"]
    assert out["phase6_needed"] is not None
    # residual cache picked up: var 0.05^2 vs noise 0.3^2
    assert out["residual_var_over_noise"] == pytest.approx(
        0.05 ** 2 / 0.09, rel=0.25)
    # supports resolved from the expressions where finals carry none
    canon = next(c for c in out["candidates"] if c["kind"] == "canonical")
    assert canon["support"] == ["tau"]
    assert all(c["dpi_ok"] for c in out["candidates"])

    g3 = pc.gate_g3([out], amp_idx=0)
    assert g3["amplitude"]["eta_post_hat_canonical"] == etas["tau"]
    assert isinstance(g3["pass"], bool)
