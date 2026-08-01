"""Paper-faithful PyTorch port of the Piras+2025 (arXiv:2502.09810) CVAE.

Carried over verbatim from the parent ``cmbvae`` project: the class and
attribute names here MUST stay exactly as they are, because the stored
checkpoints in ``models/`` were trained with these modules and their
state-dict keys encode the attribute layout.

Architecture transcribed from the authors' TensorFlow code
(``VAExEDE/vaexede/models.py``):

  encoder (B, C, 2471)
    -> Conv1d(C, 16, k=k1=5, s=3) -> CPAct -> BN(16)            # (B,16,823)
    -> Conv1d(16, 32, k=16,  s=3) -> CPAct -> BN(32)            # (B,32,270)
    -> Conv1d(32, 64, k=3,   s=3) -> CPAct -> BN(64)            # (B,64,90)
    -> Flatten -> Linear(5760, 2*L)  -> split (mu, logvar)

  decoder (B, L)
    -> Linear(L, 5760) -> CPAct -> view(B,64,90) -> BN(64)
    -> ConvT1d(64, 64, k=3,  s=3) -> CPAct -> BN(64)            # (B,64,270)
    -> ConvT1d(64, 32, k=16, s=3) -> CPAct -> BN(32)            # (B,32,823)
    -> ConvT1d(32, C,  k=k1=5, s=3)                              # (B,C,2471)

Notes:
* `k1 = input_dim - (output_layer1-1) * s1` matches the authors' hardcoded
  formula (input_dim=2471, output_layer1=823, s1=3 -> k1=5).
* `CPAct` is the trainable SPECULATOR activation
      f(x) = x * (sigmoid(x * beta) * (1 - gamma) + gamma)
  with gamma and beta scalar parameters initialised to 0 -> f(x)=0.5*x at start.
* logvar clamped to (-10, 10) to prevent KL explosion (deviation from strict
  paper faithfulness, matching the checkpoints as trained).
* `DualEncoderCVAE` adds per-channel encoder stacks for TT+EE-lowl where the
  two channels have different input_dims (2471 vs 2499); selected with
  ``architecture: dual`` in the model config.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import torch
import torch.nn as nn


class CPAct(nn.Module):
    """Trainable SPECULATOR activation: x * (sigmoid(x*beta)*(1-gamma) + gamma)."""

    def __init__(self):
        super().__init__()
        self.gamma = nn.Parameter(torch.zeros(1))
        self.beta = nn.Parameter(torch.zeros(1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x * (torch.sigmoid(x * self.beta) * (1.0 - self.gamma) + self.gamma)


class CVAE(nn.Module):
    """Paper-faithful CVAE. Supports multi-channel inputs (stacked, same length)."""

    def __init__(
        self,
        input_dim: int = 2471,
        latent_dim: int = 5,
        n_channels: int = 1,
    ):
        super().__init__()
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.n_channels = n_channels

        s1 = 3
        output_layer1 = 823
        k1 = input_dim - (output_layer1 - 1) * s1
        assert k1 > 0, (
            f"k1={k1}; input_dim={input_dim} is too small. The authors' formula "
            "k1 = input_dim - (output_layer1-1)*s1 must yield a positive kernel."
        )
        self._k1 = k1
        self._flat = 90 * 64

        # ── Encoder ──────────────────────────────────────────────────────────
        self.encoder = nn.Sequential(
            nn.Conv1d(n_channels, 16, kernel_size=k1, stride=s1),
            CPAct(),
            nn.BatchNorm1d(16),
            nn.Conv1d(16, 32, kernel_size=16, stride=3),
            CPAct(),
            nn.BatchNorm1d(32),
            nn.Conv1d(32, 64, kernel_size=3, stride=3),
            CPAct(),
            nn.BatchNorm1d(64),
            nn.Flatten(),
        )
        self.fc_mulogvar = nn.Linear(self._flat, 2 * latent_dim)

        # ── Decoder ──────────────────────────────────────────────────────────
        self.dec_fc = nn.Linear(latent_dim, self._flat)
        self.dec_act0 = CPAct()
        self.dec_bn0 = nn.BatchNorm1d(64)

        self.dec_ct1 = nn.ConvTranspose1d(64, 64, kernel_size=3, stride=3)
        self.dec_act1 = CPAct()
        self.dec_bn1 = nn.BatchNorm1d(64)

        self.dec_ct2 = nn.ConvTranspose1d(64, 32, kernel_size=16, stride=3)
        self.dec_act2 = CPAct()
        self.dec_bn2 = nn.BatchNorm1d(32)

        self.dec_ct3 = nn.ConvTranspose1d(32, n_channels, kernel_size=k1, stride=s1)

    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """x: (B, C, L). Returns (mu, logvar)."""
        h = self.encoder(x)
        mu, logvar = self.fc_mulogvar(h).chunk(2, dim=1)
        # Clamp logvar to (-10, 10): posterior σ ∈ (2e-3, 148) covers all
        # physically reasonable values while blocking float32 overflow.
        return mu, logvar.clamp(-10.0, 10.0)

    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        return mu + torch.randn_like(mu) * (0.5 * logvar).exp()

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        h = self.dec_act0(self.dec_fc(z))               # (B, 5760)
        h = self.dec_bn0(h.view(h.size(0), 64, 90))     # (B, 64, 90)
        h = self.dec_bn1(self.dec_act1(self.dec_ct1(h)))  # (B, 64, 270)
        h = self.dec_bn2(self.dec_act2(self.dec_ct2(h)))  # (B, 32, 823)
        return self.dec_ct3(h)                          # (B, C, input_dim)

    def forward(self, x: torch.Tensor):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        return self.decode(z), mu, logvar


# Back-compatibility aliases (checkpoints and docs refer to PirasCVAE).
ConvVAE = CVAE
PirasCVAE = CVAE


# --------------------------------------------------------------------------- #
# Dual-encoder CVAE for channels with different input_dims (TT + EE-lowl)
# --------------------------------------------------------------------------- #
class DualEncoderCVAE(nn.Module):
    """Two per-channel 1D-CNN encoder stacks → concat → fc_mulogvar; shared decoder.

    Designed for TT (2471 bins, k1=5) + EE-lowl (2499 bins, k1=33). Each channel
    has its own Conv1d stack; flattened outputs (each 5760-d) are concatenated
    before the μ/logσ² head. The decoder body is shared; per-channel heads
    restore each channel to its original length.

    encode() takes a dict {ch: (B, L_ch)} and returns (mu, logvar).
    decode() takes (B, latent_dim) and returns dict {ch: (B, 1, L_ch)}.
    """

    _FLAT = 90 * 64          # 5760 — flattened encoder output per channel
    _OUTPUT_L1 = 823         # first conv output length (same for all valid input_dims)
    _S1 = 3

    def __init__(
        self,
        input_dims: Dict[str, int],
        latent_dim: int = 6,
        channels: List[str] | None = None,
    ):
        super().__init__()
        self.channels: List[str] = channels or list(input_dims.keys())
        self.latent_dim = latent_dim
        self.input_dims = {ch: input_dims[ch] for ch in self.channels}

        # Per-channel encoder stacks: (B, 1, L_ch) → (B, 5760)
        self.encoders = nn.ModuleDict({
            ch: self._enc_stack(input_dims[ch]) for ch in self.channels
        })
        # Concatenated encoder outputs → 2L
        self.fc_mulogvar = nn.Linear(len(self.channels) * self._FLAT, 2 * latent_dim)

        # Shared decoder body: z → (B, 32, 823)
        self.dec_fc   = nn.Linear(latent_dim, self._FLAT)
        self.dec_act0 = CPAct()
        self.dec_bn0  = nn.BatchNorm1d(64)
        self.dec_ct1  = nn.ConvTranspose1d(64, 64, kernel_size=3,  stride=3)
        self.dec_act1 = CPAct()
        self.dec_bn1  = nn.BatchNorm1d(64)
        self.dec_ct2  = nn.ConvTranspose1d(64, 32, kernel_size=16, stride=3)
        self.dec_act2 = CPAct()
        self.dec_bn2  = nn.BatchNorm1d(32)

        # Per-channel output heads: (B, 32, 823) → (B, 1, L_ch)
        self.dec_heads = nn.ModuleDict({
            ch: nn.ConvTranspose1d(
                32, 1,
                kernel_size=input_dims[ch] - (self._OUTPUT_L1 - 1) * self._S1,
                stride=self._S1,
            )
            for ch in self.channels
        })

    @classmethod
    def _enc_stack(cls, input_dim: int) -> nn.Sequential:
        k1 = input_dim - (cls._OUTPUT_L1 - 1) * cls._S1
        assert k1 > 0, f"k1={k1} for input_dim={input_dim}; reduce ell range"
        return nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=k1, stride=cls._S1),
            CPAct(), nn.BatchNorm1d(16),
            nn.Conv1d(16, 32, kernel_size=16, stride=3),
            CPAct(), nn.BatchNorm1d(32),
            nn.Conv1d(32, 64, kernel_size=3, stride=3),
            CPAct(), nn.BatchNorm1d(64),
            nn.Flatten(),
        )

    def encode(self, x: Dict[str, torch.Tensor]) -> Tuple[torch.Tensor, torch.Tensor]:
        """x: dict {ch: (B, L_ch)} or {ch: (B, 1, L_ch)}. Returns (mu, logvar)."""
        feats = []
        for ch in self.channels:
            t = x[ch]
            if t.ndim == 2:
                t = t.unsqueeze(1)      # (B, L) → (B, 1, L)
            feats.append(self.encoders[ch](t))
        mu, logvar = self.fc_mulogvar(torch.cat(feats, dim=1)).chunk(2, dim=1)
        return mu, logvar.clamp(-10.0, 10.0)

    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        return mu + torch.randn_like(mu) * (0.5 * logvar).exp()

    def decode(self, z: torch.Tensor) -> Dict[str, torch.Tensor]:
        """z: (B, latent_dim). Returns dict {ch: (B, 1, L_ch)}."""
        h = self.dec_act0(self.dec_fc(z))
        h = self.dec_bn0(h.view(h.size(0), 64, 90))
        h = self.dec_bn1(self.dec_act1(self.dec_ct1(h)))
        h = self.dec_bn2(self.dec_act2(self.dec_ct2(h)))
        return {ch: self.dec_heads[ch](h) for ch in self.channels}

    def forward(self, x: Dict[str, torch.Tensor]):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        return self.decode(z), mu, logvar


def build_model(model_cfg: dict, n_ell, n_channels: int) -> nn.Module:
    """Construct CVAE or DualEncoderCVAE from a checkpoint's ``model_cfg``.

    n_ell: int for single-encoder; dict {ch: int} for dual-encoder.
    """
    arch = model_cfg.get("architecture", "single")
    if arch == "dual":
        input_dims = model_cfg.get("input_dims")
        if input_dims is None:
            if isinstance(n_ell, dict):
                input_dims = n_ell
            else:
                raise ValueError(
                    "DualEncoderCVAE requires model.input_dims in config or a dict n_ell"
                )
        return DualEncoderCVAE(
            input_dims={ch: int(d) for ch, d in input_dims.items()},
            latent_dim=int(model_cfg.get("latent_dim", 6)),
        )
    return CVAE(
        input_dim=int(n_ell) if isinstance(n_ell, int) else int(list(n_ell.values())[0]),
        latent_dim=int(model_cfg.get("latent_dim", 5)),
        n_channels=n_channels,
    )
