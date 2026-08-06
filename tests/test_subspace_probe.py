"""Phase-8 subspace probe: the lasso probe finds the true carrier set
(axis-aligned, subspace, distributed), the shuffled reference sits at ~0,
and slab-conditional MI separates a redundant latent copy from a
complementary carrier."""
import pathlib
import sys

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

import subspace_probe as sp  # noqa: E402


@pytest.fixture(scope="module")
def world():
    rng = np.random.default_rng(0)
    n = 2500
    a, b = rng.standard_normal(n), rng.standard_normal(n)
    Z = np.column_stack([
        a,                                            # z0
        a + 0.25 * rng.standard_normal(n),            # z1: noisy copy of z0
        b,                                            # z2
        (a + b) / np.sqrt(2),                         # z3: subspace carrier
    ])
    Z = (Z - Z.mean(0)) / Z.std(0)
    return Z, a, b, rng


def test_probe_axis_aligned(world):
    Z, _a, b, _ = world
    rng = np.random.default_rng(1)
    y = sp.rank_normal(2.0 * b + 0.05 * rng.standard_normal(len(b)))
    out = sp.lasso_probe(Z, y, seed=0)
    assert out["a_star"]["support"] == [2]
    assert out["a_star"]["cv_r2"] > 0.95
    assert out["r2_full"] > 0.95


def test_probe_finds_subspace_carrier(world):
    Z, a, b, _ = world
    rng = np.random.default_rng(2)
    y = sp.rank_normal(a + b + 0.2 * rng.standard_normal(len(a)))
    out = sp.lasso_probe(Z, y, seed=0)
    assert out["a_star"]["support"] == [3]        # one latent spans (a+b)
    assert out["a_star"]["cv_r2"] > 0.9


def test_probe_shuffled_reference_is_null(world):
    Z, _a, b, _ = world
    rng = np.random.default_rng(3)
    y = sp.rank_normal(b)
    out = sp.lasso_probe(Z, rng.permutation(y), n_alphas=4, seed=0)
    assert abs(out["r2_full"]) < 0.1


def test_redundant_copy_detected(world):
    Z, a, _b, _ = world
    rng = np.random.default_rng(4)
    y = sp.rank_normal(a + 0.2 * rng.standard_normal(len(a)))
    mi_u = sp.mutual_information_gmm(Z[:, [1]], y.reshape(-1, 1),
                                     max_samples=1200, seed=0)[0, 0]
    cond = sp.slab_conditional_mi(Z[:, 1], y, Z[:, 0], n_slabs=8,
                                  max_samples=1200, min_slab=150, seed=0)
    assert mi_u > 1.0                              # copy carries the signal
    red = 1.0 - cond["mi_cond"] / mi_u
    assert red > 0.7                               # ...but adds ~nothing


def test_complementary_carrier_not_flagged(world):
    Z, _a, b, _ = world
    rng = np.random.default_rng(5)
    y = sp.rank_normal(b + 0.3 * rng.standard_normal(len(b)))
    mi_u = sp.mutual_information_gmm(Z[:, [2]], y.reshape(-1, 1),
                                     max_samples=1200, seed=0)[0, 0]
    cond = sp.slab_conditional_mi(Z[:, 2], y, Z[:, 0], n_slabs=8,
                                  max_samples=1200, min_slab=150, seed=0)
    red = 1.0 - cond["mi_cond"] / mi_u
    assert mi_u > 0.8
    assert red < 0.3                # conditioning on z0 keeps the b signal


def test_build_candidates_focus_and_f2():
    sem = {"latents": {
        "z0": {"canonical_cluster": 0,
               "clusters": [{"cluster": 0, "representative": "n_s"}]},
        "z2": {"canonical_cluster": 1,
               "clusters": [{"cluster": 1, "representative": "tau"}]}}}
    res = {"latents": [{"latent": 0, "f2": {"expr": "omega_b"}},
                       {"latent": 2, "f2": None}]}
    cands = sp.build_candidates("lcdm_tt_beta3e-4", 2, sem, res, [0, 2])
    tags = [(c["latent"], c["stage"], c["focus"]) for c in cands]
    assert tags == [(0, "f1", False), (0, "f2", False), (2, "f1", True)]

    sem_ee = {"latents": {"z4": {
        "canonical_cluster": 0,
        "clusters": [{"cluster": 0, "representative": "tau"}]}}}
    res_ee = {"latents": [{"latent": 4, "f2": None}]}
    cands = sp.build_candidates("lcdm_tt_ee_lowl", 5, sem_ee, res_ee, [4])
    assert cands[0]["focus"] is True     # role mentions the amplitude sector
