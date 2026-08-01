"""Per-channel normalisation bundle saved at training time (``scaler.npz``).

The training preprocessing chain was:
    1) y = spec / ref            (per-ell ratio to a reference spectrum)
    2) y = log10(y)
    3) y = (y - mu) / sigma      (per-ell standardise; stats fit on train only)

Each stored run dir in ``models/`` contains a ``scaler.npz`` written by the
parent project's training loop. It bundles ``refs`` and ``(mu, sigma)`` per
channel — everything the encoder pass needs to reproduce steps (1)–(3) for
the test split, with no recomputation of training statistics.

Two storage modes exist in the stored files:
* Same-length channels (TT-only): stacked ``mu``/``sigma`` of shape (C, L).
* Different-length channels (dual-encoder TT + EE-lowl): per-channel keys
  ``mu_<ch>`` / ``sigma_<ch>`` of shape (L_ch,).
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np


class ShardedScaler:
    """Refs + normalisation stats for the sharded preprocessing (and its inverse).

    Exposes:
        channels               list of channel names in training order
        refs[ch]               (L_ch,) reference spectrum
        mu, sigma              stacked (C, L) arrays, or None in per-channel mode
        channel_stats(ch)      -> (mu_ch, sigma_ch) each (L_ch,)
        inverse_transform*     normalised log-ratio space -> physical D_ell
    """

    def __init__(self, refs: Dict[str, np.ndarray], mu, sigma,
                 channels: list[str] | None = None):
        self.channels = channels or list(refs.keys())
        self.refs = {c: np.asarray(refs[c], dtype=np.float64) for c in self.channels}

        if isinstance(mu, dict):
            # Per-channel dict path (different-length channels)
            self._mu_ch   = {ch: np.asarray(mu[ch],    dtype=np.float64) for ch in self.channels}
            self._sig_ch  = {ch: np.asarray(sigma[ch], dtype=np.float64) for ch in self.channels}
            self.mu = self.sigma = None   # not available in stacked form
        else:
            mu_a = np.asarray(mu, dtype=np.float64)
            sg_a = np.asarray(sigma, dtype=np.float64)
            if mu_a.ndim == 1:
                mu_a = mu_a[None, :]
                sg_a = sg_a[None, :]
            self.mu    = mu_a
            self.sigma = sg_a
            self._mu_ch  = {ch: mu_a[c]  for c, ch in enumerate(self.channels)}
            self._sig_ch = {ch: sg_a[c]  for c, ch in enumerate(self.channels)}

    def channel_stats(self, ch: str) -> tuple[np.ndarray, np.ndarray]:
        return self._mu_ch[ch], self._sig_ch[ch]

    def inverse_transform_channel(self, ch: str, normalised: np.ndarray) -> np.ndarray:
        """Inverse-transform for a single channel.  normalised: (N, L_ch) or (L_ch,)."""
        x = np.asarray(normalised, dtype=np.float64)
        squeezed = x.ndim == 1
        if squeezed:
            x = x[None]
        log_ratio = x * self._sig_ch[ch] + self._mu_ch[ch]
        out = (10.0 ** log_ratio) * self.refs[ch]
        return out[0] if squeezed else out

    def inverse_transform(self, normalised):
        """Map normalised log-ratio space back to physical D_ell.

        Accepts an ndarray (N, C, L) / (C, L) or a dict {ch: (N, L_ch)};
        returns the same type as the input.
        """
        if isinstance(normalised, dict):
            return {ch: self.inverse_transform_channel(ch, normalised[ch])
                    for ch in normalised}
        x = np.asarray(normalised, dtype=np.float64)
        squeezed = x.ndim == 2
        if squeezed:
            x = x[None]
        log_ratio = x * self.sigma + self.mu
        out = np.empty_like(log_ratio)
        for c, ch in enumerate(self.channels):
            out[:, c, :] = (10.0 ** log_ratio[:, c, :]) * self.refs[ch]
        return out[0] if squeezed else out

    def save(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        payload = {"channels": np.array(self.channels)}
        for ch, arr in self.refs.items():
            payload[f"ref_{ch}"] = arr
        for ch in self.channels:
            payload[f"mu_{ch}"]    = self._mu_ch[ch]
            payload[f"sigma_{ch}"] = self._sig_ch[ch]
        if self.mu is not None:
            payload["mu"]    = self.mu
            payload["sigma"] = self.sigma
        np.savez(path, **payload)

    @classmethod
    def load(cls, path: str | Path) -> "ShardedScaler":
        d = np.load(path, allow_pickle=False)
        channels = [str(c) for c in d["channels"]]
        refs = {c: d[f"ref_{c}"] for c in channels}
        # Prefer stacked mu/sigma (same-length channels, backward compat).
        # Fall back to per-channel keys (different-length channels).
        if "mu" in d:
            mu    = d["mu"]
            sigma = d["sigma"]
        else:
            mu    = {ch: d[f"mu_{ch}"]    for ch in channels}
            sigma = {ch: d[f"sigma_{ch}"] for ch in channels}
        return cls(refs=refs, mu=mu, sigma=sigma, channels=channels)
