"""Extra-input registry (interaction-aware stage 2): semantics extension +
run_blind_sr --extra-input-npy parsing.

The registry must be invisible when empty (every frozen Phase 1-8 path
bit-identical), and when an extra symbol is registered with chain-rule
gradients, the composite must be indistinguishable from the same function
spelled in raw theta — evaluation, gradients, support, and clustering.
"""
import pathlib
import sys

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

from run_blind_sr import load_extra_inputs  # noqa: E402

from cmb_lcdm_sr import semantics  # noqa: E402

HALF = np.array([0.003, 0.03, 10.0, 0.06, 0.11, 0.04])


@pytest.fixture(autouse=True)
def _clean_registry():
    semantics.clear_extra_inputs()
    yield
    semantics.clear_extra_inputs()


def _theta(n=64, seed=0):
    rng = np.random.default_rng(seed)
    lo = np.array([0.019, 0.09, 60.0, 0.01, 2.98, 0.92])
    hi = np.array([0.025, 0.15, 80.0, 0.13, 3.20, 1.00])
    return lo + (hi - lo) * rng.random((n, 6))


def _register_ob_sq(with_grads=True):
    grads = (lambda th: np.column_stack(
        [2.0 * th[:, 0] * HALF[0]] + [np.zeros(len(th))] * 5)
    ) if with_grads else None
    semantics.register_extra_input("f1hat", lambda th: th[:, 0] ** 2, grads)


def test_parse_rejects_unregistered():
    assert semantics.parse_expr("f1hat + omega_b") is None


def test_parse_eval_registered():
    semantics.register_extra_input("f1hat", lambda th: 2.0 * th[:, 0])
    th = _theta()
    expr = semantics.parse_expr("f1hat + omega_b")
    assert expr is not None
    np.testing.assert_allclose(semantics.evaluate_on_theta(expr, th),
                               3.0 * th[:, 0], rtol=1e-12)


def test_support_lists_extra_after_sampled():
    _register_ob_sq()
    fe = semantics.evaluate_form("f1hat*n_s", _theta(), HALF)
    assert fe is not None
    assert fe.support == ["n_s", "f1hat"]


def test_gradients_chain_rule_matches_raw_spelling():
    _register_ob_sq()
    th = _theta()
    g = semantics.gradients_on_theta("f1hat*n_s", th, HALF)
    g_raw = semantics.gradients_on_theta("omega_b**2*n_s", th, HALF)
    np.testing.assert_allclose(g, g_raw, rtol=1e-9)


def test_gradients_abstain_without_chain_rule():
    _register_ob_sq(with_grads=False)
    g = semantics.gradients_on_theta("f1hat*n_s", _theta(), HALF)
    assert np.isnan(g).all()


def test_plain_forms_bit_identical_with_registry_active():
    th = _theta()
    v0 = semantics.evaluate_on_theta("n_s + omega_cdm", th)
    g0 = semantics.gradients_on_theta("n_s + omega_cdm", th, HALF)
    _register_ob_sq()
    np.testing.assert_array_equal(
        v0, semantics.evaluate_on_theta("n_s + omega_cdm", th))
    np.testing.assert_array_equal(
        g0, semantics.gradients_on_theta("n_s + omega_cdm", th, HALF))


def test_clustering_bridges_f1hat_and_raw_spelling():
    _register_ob_sq()
    th = _theta(256)
    a = semantics.evaluate_form("f1hat*n_s", th, HALF)
    b = semantics.evaluate_form("omega_b**2*n_s", th, HALF)
    assert semantics.same_cluster(a, b)


def test_sobol_composite(tmp_path):
    _register_ob_sq()
    mid = np.array([0.022, 0.12, 70.0, 0.07, 3.09, 0.96])
    s = semantics.sobol_indices("f1hat", mid, HALF, n_base=256, seed=0)
    assert s["n_effective"] > 200
    assert s["ST"][0] > 0.9 and max(abs(s["ST"][j]) for j in range(1, 6)) < 0.05


def test_load_extra_inputs_roundtrip_and_errors(tmp_path):
    v = np.arange(50.0)
    p = tmp_path / "col.npy"
    np.save(p, v)
    labels, cols = load_extra_inputs([f"f1hat={p}"], 50)
    assert labels == ["f1hat"]
    np.testing.assert_array_equal(cols[0], v)
    with pytest.raises(SystemExit):
        load_extra_inputs(["nolabelpath"], 50)
    with pytest.raises(SystemExit):
        load_extra_inputs([f"bad-label={p}"], 50)
    with pytest.raises(SystemExit):
        load_extra_inputs([f"f1hat={p}"], 49)
    with pytest.raises(SystemExit):
        load_extra_inputs([f"f1hat={p}", f"f1hat={p}"], 50)
