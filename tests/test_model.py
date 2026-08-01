"""Model architecture: shapes, CPAct init, config-driven construction."""
import json

import pytest

torch = pytest.importorskip("torch")

from cmb_lcdm_sr.model import CPAct, CVAE, DualEncoderCVAE, build_model


def test_cpact_initial_identity_half():
    act = CPAct()
    x = torch.randn(64)
    assert torch.allclose(act(x), 0.5 * x)


def test_cvae_shapes():
    m = CVAE(input_dim=2471, latent_dim=5, n_channels=1)
    m.eval()
    x = torch.randn(2, 1, 2471)
    recon, mu, logvar = m(x)
    assert recon.shape == (2, 1, 2471)
    assert mu.shape == (2, 5)
    assert logvar.shape == (2, 5)
    assert logvar.min() >= -10.0 and logvar.max() <= 10.0


def test_dual_encoder_shapes():
    m = DualEncoderCVAE(input_dims={"tt": 2471, "ee": 2499}, latent_dim=6)
    m.eval()
    x = {"tt": torch.randn(2, 2471), "ee": torch.randn(2, 2499)}
    recon, mu, logvar = m(x)
    assert mu.shape == (2, 6)
    assert recon["tt"].shape == (2, 1, 2471)
    assert recon["ee"].shape == (2, 1, 2499)


def test_build_model_from_stored_configs(model_dirs):
    tt_cfg = json.loads((model_dirs["tt"] / "config_used.json").read_text())
    m_tt = build_model(tt_cfg["model"], n_ell=2471, n_channels=1)
    assert isinstance(m_tt, CVAE)
    assert m_tt.latent_dim == 5

    ee_cfg = json.loads((model_dirs["ee"] / "config_used.json").read_text())
    m_ee = build_model(ee_cfg["model"], n_ell={"tt": 2471, "ee": 2499}, n_channels=2)
    assert isinstance(m_ee, DualEncoderCVAE)
    assert m_ee.latent_dim == 6
    assert m_ee.channels == ["tt", "ee"]
