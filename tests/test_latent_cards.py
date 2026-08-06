"""Phase-10 card builder: frozen status predicates fire on the right legs,
and the merge runs end-to-end on the committed Phase 1-8 JSONs (with the
Phase-8 subspace input optional/pending)."""
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

import build_latent_cards as blc  # noqa: E402

LEGS_GREEN = {"minimal_stable": True, "r_sr": 0.8, "eta_s": 0.99,
              "residual1_pass": True, "eta_post": 0.97,
              "eta_post_hat": 0.96, "ls_strict": False, "ls_joint": True,
              "ls_evidence": True, "response_ok": True,
              "subspace_small": True, "subspace_r2": 0.99}


def test_status_interpreted():
    st, _ = blc.assign_status(dict(LEGS_GREEN))
    assert st == "interpreted"


def test_status_demoted_by_eta_post_hat():
    st, _ = blc.assign_status(dict(LEGS_GREEN, eta_post_hat=0.90,
                                   residual1_pass=False))
    assert st == "primarily interpreted"


def test_status_primarily_on_structured_residual():
    st, why = blc.assign_status(dict(LEGS_GREEN, residual1_pass=False))
    assert st == "primarily interpreted"
    assert "structured" in why


def test_status_joint_fail_blocks_levelset_leg():
    st, _ = blc.assign_status(dict(LEGS_GREEN, residual1_pass=False,
                                   ls_joint=False, ls_evidence=False))
    assert st == "unresolved"


def test_status_subspace_mixed():
    st, _ = blc.assign_status(dict(LEGS_GREEN, eta_s=0.6,
                                   residual1_pass=False))
    assert st == "subspace/mixed"


def test_status_unresolved_no_account():
    st, _ = blc.assign_status(dict(LEGS_GREEN, eta_s=0.6,
                                   residual1_pass=False, subspace_small=False))
    assert st == "unresolved"


@pytest.mark.parametrize("run,n", [("lcdm_tt_beta3e-4", 5),
                                   ("lcdm_tt_ee_lowl", 6)])
def test_build_run_end_to_end(run, n, tmp_path):
    payload = blc.build_run(run, n, 2 if n == 5 else 5,
                            REPO / "experiments")
    assert len(payload["cards"]) == n
    allowed = {"interpreted", "primarily interpreted", "subspace/mixed",
               "unresolved"}
    for c in payload["cards"]:
        assert c["status"] in allowed
        assert c["f1"]["expr"]
        assert c["sufficiency"]["eta_post_hat"] is not None
    md = blc.to_markdown(payload)
    assert "# Gates" in md and "Deviation register" in md
    amp = payload["cards"][2 if n == 5 else 5]
    assert amp["f2"] is not None
    if run == "lcdm_tt_beta3e-4":
        assert any(d["id"] == "D-DoD-z2" for d in amp["deviations"])
        # joint audit undefined for TT amplitude (union support = all 6)
        assert amp["levelset"]["joint_pass"] is None
    else:
        assert amp["levelset"]["joint_pass"] is True
        z0 = payload["cards"][0]
        assert z0["levelset"]["joint_pass"] is False   # 0.060 > 0.05
        assert z0["status"] == "unresolved"
