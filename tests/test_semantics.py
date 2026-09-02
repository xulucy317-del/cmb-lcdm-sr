"""Form evaluation, equivalence clustering, signatures, Sobol (roadmap M3).

The load-bearing checks: the answer-agnostic instruments must *derive* the
known amplitude facts — the −2 exponent as a constant-ratio pair, and the
Taylor/exponential/log family as one semantic cluster — from expressions
alone, with nothing amplitude-specific in the machinery.
"""
import numpy as np
import pytest

from cmb_lcdm_sr import semantics, tiers


@pytest.fixture(scope="module")
def box(repo_root):
    return tiers.load_prior_box(repo_root / "data")


@pytest.fixture(scope="module")
def theta(box):
    mid, half = box
    rng = np.random.default_rng(7)
    return mid + (2.0 * rng.random((600, 6)) - 1.0) * half


# --- parsing + evaluation ----------------------------------------------------

def test_evaluate_matches_numpy(theta):
    vals = semantics.evaluate_on_theta("A_s*(tau - 0.598)", theta)
    a_s = np.exp(theta[:, 4]) * 1e-10
    expected = a_s * (theta[:, 3] - 0.598)
    assert np.allclose(vals, expected, rtol=1e-12)


def test_order_one_symbols_rewrite_exactly_to_sampled_basis(theta):
    vals = semantics.evaluate_on_theta("wb100 + wc10 + h + A9", theta)
    expected = (100.0 * theta[:, 0] + 10.0 * theta[:, 1]
                + theta[:, 2] / 100.0 + np.exp(theta[:, 4]) / 10.0)
    np.testing.assert_allclose(vals, expected, rtol=1e-13, atol=0.0)


def test_pysr_spellings_and_unknown_symbols(theta):
    sq = semantics.parse_expr("square(tau)")
    assert sq is not None and sq.equals(semantics.parse_expr("tau**2"))
    ng = semantics.parse_expr("neg(n_s)")
    assert ng is not None and ng.equals(semantics.parse_expr("-n_s"))
    assert semantics.parse_expr("x0 * tau") is None      # unknown symbol
    assert semantics.parse_expr("log(tau") is None       # unparseable
    assert np.isnan(semantics.evaluate_on_theta("log(tau", theta)).all()


def test_domain_violations_masked_not_raised(theta, box):
    # tau <= 0.13 on the box, so log(tau - 0.5) is invalid everywhere
    form = semantics.evaluate_form("log(tau - 0.5)", theta, box[1])
    assert form is not None
    assert form.finite_frac == 0.0
    assert np.isnan(form.values).all()


def test_support_in_sampled_basis(theta, box):
    form = semantics.evaluate_form("A_s*(tau - 0.598)", theta, box[1])
    assert form.support == ["tau", "ln10As"]             # A_s → ln10As axis


# --- gradients: the −2 must emerge -------------------------------------------

@pytest.mark.parametrize("expr", [
    "A_s*exp(-2*tau)",
    "A9*exp(-2*tau)",
    "ln10As - 2*tau",
    "log(A_s*exp(-2*tau))",
    "249.9*A_s*exp(-2*tau) + 0.118",
])
def test_constant_ratio_pair_recovers_minus_two(expr, theta, box):
    mid, half = box
    grads = semantics.gradients_on_theta(expr, theta, half)
    pairs = semantics.constant_ratio_pairs(grads, half)
    j_tau = tiers.SAMPLED_LABELS.index("tau")
    j_lnas = tiers.SAMPLED_LABELS.index("ln10As")
    hit = [p for p in pairs if (p["i"], p["j"]) == (j_tau, j_lnas)]
    assert len(hit) == 1, f"pair (tau, ln10As) not found in {pairs}"
    assert hit[0]["r_raw"] == pytest.approx(-2.0, abs=1e-6)
    assert hit[0]["cv"] < 1e-6


def test_taylor_form_ratio_is_not_constant(theta, box):
    # A_s*(tau - c) is NOT a function of one linear combination — the ratio
    # field varies with tau — so the detector must stay quiet about it.
    grads = semantics.gradients_on_theta("A_s*(tau - 0.57)", theta, box[1])
    pairs = semantics.constant_ratio_pairs(grads, box[1])
    j_tau = tiers.SAMPLED_LABELS.index("tau")
    j_lnas = tiers.SAMPLED_LABELS.index("ln10As")
    assert not any((p["i"], p["j"]) == (j_tau, j_lnas) for p in pairs)


def test_sensitivity_signature_one_hot(theta, box):
    grads = semantics.gradients_on_theta("tau", theta, box[1])
    sig = semantics.sensitivity_signature(grads)
    assert sig[tiers.SAMPLED_LABELS.index("tau")] == pytest.approx(1.0)
    assert sig.sum() == pytest.approx(1.0)


# --- clustering --------------------------------------------------------------

def test_amplitude_family_clusters_together(theta, box):
    exprs = [
        "A_s*(tau - 0.57)",                    # Taylor direction
        "A_s*tau - 0.57*A_s",                  # algebraic duplicate of ^
        "249.9*A_s*exp(-2*tau) + 0.118",       # literal textbook, affine wrap
        "log(A_s*exp(-2*tau))",                # log wrap of the direction
        "n_s",                                 # unrelated
        "log(tau - 0.5)",                      # invalid everywhere
    ]
    forms = [semantics.evaluate_form(e, theta, box[1]) for e in exprs]
    assert all(f is not None for f in forms)
    labels = semantics.cluster_forms(forms)
    assert labels[0] == labels[1] == labels[2] == labels[3]
    assert labels[4] != labels[0]
    assert labels[5] not in (labels[0], labels[4])       # all-NaN stays alone


def test_positive_control_clusters_across_all_input_bases(theta, box):
    exprs = [
        "A_s*exp(-2*tau)",
        "A9*exp(-2*tau)",
        "ln10As - 2*tau",
    ]
    forms = [semantics.evaluate_form(e, theta, box[1]) for e in exprs]
    assert all(f is not None for f in forms)
    assert all(f.support == ["tau", "ln10As"] for f in forms)
    assert len(set(semantics.cluster_forms(forms))) == 1


# --- Sobol -------------------------------------------------------------------

def test_sobol_single_variable(box):
    mid, half = box
    res = semantics.sobol_indices("tau", mid, half, n_base=1024, seed=0)
    j_tau = tiers.SAMPLED_LABELS.index("tau")
    assert res["S1"][j_tau] == pytest.approx(1.0, abs=0.05)
    assert res["ST"][j_tau] == pytest.approx(1.0, abs=0.05)
    others = [j for j in range(6) if j != j_tau]
    assert np.abs(res["ST"][others]).max() < 0.05


def test_sobol_additive_split_matches_analytic(box):
    mid, half = box
    res = semantics.sobol_indices("tau + n_s", mid, half, n_base=2048, seed=1)
    j_tau = tiers.SAMPLED_LABELS.index("tau")
    j_ns = tiers.SAMPLED_LABELS.index("n_s")
    frac_tau = half[j_tau] ** 2 / (half[j_tau] ** 2 + half[j_ns] ** 2)
    assert res["S1"][j_tau] == pytest.approx(frac_tau, abs=0.08)
    assert res["S1"][j_ns] == pytest.approx(1.0 - frac_tau, abs=0.08)


def test_sobol_degenerate_inputs(box):
    mid, half = box
    const = semantics.sobol_indices("1.5", mid, half, n_base=256, seed=0)
    assert const["variance"] == 0.0 and np.all(const["S1"] == 0)
    bad = semantics.sobol_indices("log(tau - 0.5)", mid, half, n_base=256, seed=0)
    assert bad["n_effective"] == 0 and np.isnan(bad["S1"]).all()
