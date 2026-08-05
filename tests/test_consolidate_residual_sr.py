"""Phase-6 consolidation: recovers a planted shape-sector f2 from synthetic
residual fronts, wires the hierarchical account, and terminates the stage-2
audit. Runs on shrunken tiers for speed."""
import json
import pathlib
import sys

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

import consolidate_residual_sr as crs  # noqa: E402
import semantic_recurrence as sr_mod  # noqa: E402
from cmb_lcdm_sr import tiers  # noqa: E402

MID = np.array([0.022, 0.115, 71.0, 0.07, 3.04, 0.965])
HALF = np.array([0.002, 0.015, 9.0, 0.04, 0.14, 0.025])


def test_latent_worker_recovers_f2(tmp_path, monkeypatch):
    rng = np.random.default_rng(0)
    n = 3000
    monkeypatch.setattr(tiers, "T1", slice(500, 1500))
    monkeypatch.setattr(tiers, "T2", slice(1500, 3000))
    theta = MID + (2.0 * rng.random((n, 6)) - 1.0) * HALF
    u = (theta - MID) / HALF

    # latent = h(f1) + shape-sector residual; f1 = tau already calibrated out
    mu = np.zeros((n, 1))
    mu[:, 0] = 2.0 * np.tanh(u[:, 3]) + 0.5 * u[:, 5]
    logvar = np.full((n, 1), 2.0 * np.log(0.3))
    e1 = 0.5 * u[:, 5] + 0.02 * rng.standard_normal(n)

    run_dir = tmp_path / "models" / "lcdm_tt_beta3e-4"
    (run_dir / "analysis").mkdir(parents=True)
    np.save(run_dir / "analysis" / "residual_z0_v1.npy", e1)

    res_root = tmp_path / "results" / "lcdm_tt_beta3e-4" / "residual_sr"
    for s in range(3):
        d = res_root / f"z0_seed{s}"
        d.mkdir(parents=True)
        eqs = [
            {"complexity": 1, "mi_val": 2.00 + 0.01 * s, "mi_val_err": 0.02,
             "expression_simplified": "n_s"},
            {"complexity": 3, "mi_val": 2.05 + 0.01 * s, "mi_val_err": 0.02,
             "expression_simplified": "n_s + 0.001*n_s**2"},
            {"complexity": 2, "mi_val": 0.30, "mi_val_err": 0.02,
             "expression_simplified": "tau**2"},
        ]
        (d / "report.json").write_text(json.dumps({"all_equations": eqs}))
    dctl = res_root / "shuffled_res_z0_s0"
    dctl.mkdir()
    (dctl / "report.json").write_text(json.dumps(
        {"target_label": "res_z0", "shuffle_seed": 0,
         "best_mi_val_unshuffled_eval": 0.03}))

    monkeypatch.setattr(sr_mod, "CANONICAL_FAMILIES", ["residual_sr"])
    crs._G.clear()
    crs._G.update({
        "run": "lcdm_tt_beta3e-4", "run_dir": str(run_dir),
        "results_root": str(tmp_path / "results"),
        "knee": {"latents": {"z0": {"plateau": {"mi_plat": 3.0}}}},
        "p5": {"latents": {0: {"ceiling": {"I": 1.3}, "mi_mu_ref": 1.3,
                               "canonical_eta_post_hat": 0.7}}},
        "mu": mu, "logvar": logvar,
        "theta_t1": theta[tiers.T1], "theta_t2": theta[tiers.T2],
        "anchors": theta[:256], "mid": MID, "half": HALF,
        "eta_floor": 0.25, "n_perm_mi": 1, "n_perm_r2": 2,
        "max_samples_mi": 600,
    })
    out = crs._latent_worker(0)
    json.dumps(out)                              # payload is JSON-clean

    assert out["f2"] is not None
    assert out["f2"]["support"] == ["n_s"]       # simplest rep of the cluster
    assert out["f2"]["shape_sector"] is True
    assert out["f2"]["r_sr"] == 1.0              # recurrent in all 3 seeds
    assert out["residual_plateau"]["c_star"] is not None

    h = out["hierarchy"]
    assert h["r2_stage2_of_residual"] > 0.9      # g(f2) explains e1
    assert h["combined_r2_vs_mu"] > 0.95         # h(f1)+g(f2) explains mu
    assert h["eta_post_hat_comb"] is not None
    assert 0.5 < h["eta_post_hat_comb"] < 1.3    # wiring, not calibration

    s2 = out["stage2_residual"]
    assert s2["r2_res"] < 0.2                    # hierarchy ~terminates
    assert out["audit_expected"] is not None
