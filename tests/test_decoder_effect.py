"""Phase-7b decoder effect: JVP columns equal the exact Jacobian of a linear
stub decoder (single and dual paths); the template decomposition recovers
planted coefficients, support, and the implied raw-space ratio."""
import pathlib
import sys

import numpy as np
import torch

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

import decoder_effect as de  # noqa: E402

HALF = np.array([0.002, 0.015, 9.0, 0.06, 0.14, 0.045])


class LinSingle(torch.nn.Module):
    def __init__(self, W, b):
        super().__init__()
        self.register_buffer("W", torch.as_tensor(W, dtype=torch.float32))
        self.register_buffer("b", torch.as_tensor(b, dtype=torch.float32))

    def decode(self, z):
        out = z @ self.W.T + self.b
        return out.reshape(z.shape[0], 1, -1)


class LinDual(torch.nn.Module):
    def __init__(self, W1, W2):
        super().__init__()
        self.register_buffer("W1", torch.as_tensor(W1, dtype=torch.float32))
        self.register_buffer("W2", torch.as_tensor(W2, dtype=torch.float32))

    def decode(self, z):
        return {"tt": (z @ self.W1.T).reshape(z.shape[0], 1, -1),
                "ee": (torch.tanh(z) @ self.W2.T).reshape(z.shape[0], 1, -1)}


def test_columns_linear_single():
    rng = np.random.default_rng(0)
    W = rng.normal(size=(40, 3))
    model = LinSingle(W, rng.normal(size=40)).eval()
    z = rng.normal(size=(4, 3))
    cols = de.decoder_columns(model, ["tt"], z)
    assert cols.shape == (3, 4, 40)
    for k in range(3):
        for p in range(4):
            assert np.allclose(cols[k, p], W[:, k], atol=1e-5)


def test_columns_dual_concat_order_and_nonlinearity():
    rng = np.random.default_rng(1)
    W1, W2 = rng.normal(size=(30, 2)), rng.normal(size=(20, 2))
    model = LinDual(W1, W2).eval()
    z = np.array([[0.3, -0.7], [0.0, 0.0]])
    cols = de.decoder_columns(model, ["tt", "ee"], z)
    assert cols.shape == (2, 2, 50)
    # tt block: exact Jacobian W1; ee block: W2 * sech^2(z_k) row-wise
    for k in range(2):
        for p in range(2):
            assert np.allclose(cols[k, p, :30], W1[:, k], atol=1e-5)
            gain = 1.0 / np.cosh(z[p, k]) ** 2
            assert np.allclose(cols[k, p, 30:], W2[:, k] * gain, atol=1e-4)


def test_decompose_recovers_planted():
    rng = np.random.default_rng(2)
    T = rng.normal(size=(6, 400))
    a_true = np.array([0.0, 0.3, 0.0, -2.0, 1.0, 0.0])
    y = T.T @ a_true
    a, r2 = de.decompose(y, T)
    assert np.allclose(a, a_true, atol=1e-8)
    assert r2 > 0.999999
    a_w, r2_w = de.decompose(y, T, weights=np.linspace(1, 5, 400))
    assert np.allclose(a_w, a_true, atol=1e-8)
    assert r2_w > 0.999999


def test_lasso_support_and_ratio():
    rng = np.random.default_rng(3)
    T = rng.normal(size=(6, 500))
    a_true = np.array([0.0, 0.0, 0.0, -2.0 * HALF[3], HALF[4], 0.0])
    y = T.T @ a_true + 1e-4 * rng.standard_normal(500)
    support, a_pl = de.lasso_support(y, T, seed=0)
    assert support == [3, 4]
    assert np.abs(a_pl - a_true).max() < 1e-2
    # planted direction: a_j proportional to half_j * (df/dtheta_j) -> r = -2
    assert abs(de.raw_ratio(a_pl, HALF) - (-2.0)) < 0.05
    assert de.amp_mass(a_pl) > 0.99


def test_ratio_guards_and_cosine():
    assert de.raw_ratio(np.array([1.0, 0, 0, 0, 0, 0]), HALF) is None
    assert de.cosine(np.zeros(3), np.ones(3)) is None
    assert abs(de.cosine(np.array([1.0, 0]), np.array([2.0, 0])) - 1.0) < 1e-12


def test_pair_projections_basis():
    # pure degenerate raw displacement (dtau, dlnAs) = (1, 2): brk = 0
    a = np.zeros(6)
    a[3], a[4] = 1.0 / HALF[3], 2.0 / HALF[4]
    pd, pb = de.pair_projections(a, HALF)
    assert abs(pd - np.sqrt(5.0)) < 1e-12 and abs(pb) < 1e-12
    # pure breaking displacement (-2, 1): deg = 0
    a[3], a[4] = -2.0 / HALF[3], 1.0 / HALF[4]
    pd, pb = de.pair_projections(a, HALF)
    assert abs(pd) < 1e-12 and abs(pb - np.sqrt(5.0)) < 1e-12


def test_pair_identifiability_flags_collinear():
    rng = np.random.default_rng(5)
    T = rng.normal(size=(6, 200))
    good = de.pair_identifiability(T)
    assert good["cond"] < 3.0
    T[3] = -0.85 * T[4] + 1e-4 * rng.standard_normal(200)
    bad = de.pair_identifiability(T)
    assert bad["cond"] > 10.0 and bad["cos"] < -0.99
