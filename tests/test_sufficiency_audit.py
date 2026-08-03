"""Phase-3 sufficiency audit: calibrated residual verdicts, ratio detector,
residual-cache stitching, draft statuses. Runs on a shrunken T1 for speed."""
import pathlib
import sys

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

import sufficiency_audit as sa  # noqa: E402
from cmb_lcdm_sr import tiers  # noqa: E402

MID = np.array([0.022, 0.115, 71.0, 0.07, 3.04, 0.965])
HALF = np.array([0.002, 0.015, 9.0, 0.04, 0.14, 0.025])
T1_SMALL = slice(100, 1300)


@pytest.fixture
def small_world(monkeypatch):
    """Synthetic theta/mu with a shrunken T1 injected into the module state."""
    rng = np.random.default_rng(0)
    n = 1500
    theta = MID + (2.0 * rng.random((n, 6)) - 1.0) * HALF
    monkeypatch.setattr(tiers, "T1", T1_SMALL)
    sa._G.clear()
    sa._G.update({
        "anchors": theta[:256], "mid": MID, "half": HALF,
        "theta_all": theta, "theta_t1": theta[T1_SMALL],
        "n_perm_mi": 2, "n_perm_r2": 2,
        "max_samples_mi": 500, "gbm_max_iter": 40,
    })
    return theta


def u(theta, j):
    return (theta[:, j] - MID[j]) / HALF[j]


def test_sufficient_coordinate_passes_residual(small_world):
    theta = small_world
    rng = np.random.default_rng(1)
    mu = np.zeros((len(theta), 1))
    mu[:, 0] = 2.0 * np.tanh(u(theta, 3)) + 0.02 * rng.standard_normal(len(theta))
    sa._G["mu"] = mu

    res = sa.audit_coordinate("tau", k=0)
    res.pop("_cal")
    assert res["r2_cal"] > 0.98            # h recovers the tanh wrapper
    # sufficiency in absolute terms: residual unpredictable and near-zero MI
    # (the pass/fail verdict itself needs the production 39-perm null, whose
    # p975 is meaningless at the 2 permutations used here)
    assert res["pass_r2"] and res["r2_res"] < 0.05
    # near-zero, not zero: cross-fitted quantile-bin error is genuinely
    # theta-dependent (~sigma/sqrt(rows per bin)) and small-n GMM-MI is
    # positively biased — far below the insufficient case's > 0.2 signal
    assert max(res["mi_res"]) < 0.12
    assert res["support"] == ["tau"]
    assert res["signature"][3] > 0.99


def test_insufficient_coordinate_fails_with_loadings_and_ratio(small_world):
    theta = small_world
    mu = np.zeros((len(theta), 1))
    mu[:, 0] = u(theta, 3) + u(theta, 5)   # tau + n_s: f=exp form misses n_s
    sa._G["mu"] = mu

    res = sa.audit_coordinate("A_s*exp(-2*tau)", k=0)
    res.pop("_cal")
    # the -2 detector: constant (tau, ln10As) ratio, exact for the literal form
    pair = next(p for p in res["ratio_pairs"]
                if set(p["pair"]) == {"tau", "ln10As"})
    assert abs(pair["r_raw"] + 2.0) < 1e-6 and pair["cv"] < 1e-6
    assert abs(res["amp_ratio_legacy"] + 2.0) < 1e-6
    # residual audit fails in the structured direction: n_s above its null
    assert not res["pass_r2"]
    assert res["residual_pass"] is False
    assert res["mi_res"][5] > 0.2          # n_s information left behind
    assert "n_s" in (res["residual_loadings"] or [])


def test_stitch_residual_oof_inside_full_outside():
    mu = np.arange(8, dtype=float)
    f = np.array([0.0, 1.0, 2.0, np.nan, 4.0, 5.0, 6.0, 7.0])
    oof = np.array([100.0, 200.0])
    e = sa.stitch_residual(mu, f, slice(2, 4), oof, h_full=lambda x: 10 * x)
    assert e[2] == mu[2] - 100.0 and e[3] == mu[3] - 200.0   # OOF inside T1
    assert e[0] == 0.0 - 0.0 and e[5] == 5.0 - 50.0          # h_full outside
    assert np.isfinite(e[:3]).all()


def test_draft_status_branches():
    assert sa.draft_status(0.9, 0.99, True) == "interpreted (draft)"
    assert sa.draft_status(0.8, 0.5, False) == "primarily interpreted (draft)"
    assert sa.draft_status(0.4, 0.99, True) == "unresolved (draft)"
    assert sa.draft_status(0.9, 0.5, True) == "unresolved (draft)"
