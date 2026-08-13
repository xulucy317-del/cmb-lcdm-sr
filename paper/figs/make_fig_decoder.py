"""Compact decoder-effect figure for the paper: amplitude-sector latents only.

Rebuilt from experiments/decoder_effect_lcdm_tt_ee_lowl_curves.npz (the same
data behind the full 6x2 consolidated figure). Rows: z4, z5; columns: TT, EE.
"""
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path("/rds/user/zx332/hpc-work/cmb-lcdm-sr")
OUT = REPO / "paper" / "figs"

BLUE = "#2a78d6"
BAND = "#9ec5f4"
INK = "#1a1a19"
MUTED = "#5f5e56"

d = np.load(REPO / "experiments" / "decoder_effect_lcdm_tt_ee_lowl_curves.npz")
lengths = d["lengths"]
channels = [str(c) for c in d["channels"]]
print("channels", channels, "lengths", lengths)
bounds = np.concatenate([[0], np.cumsum(lengths)])
seg = {ch: slice(bounds[i], bounds[i + 1]) for i, ch in enumerate(channels)}
ells = d["ells"]

rows = [("z4", r"$z_4$ --- $\tau$ (amplitude sector)"),
        ("z5", r"$z_5$ --- amplitude ($A_s$, $\tau$)")]
cols = [(channels[0], "TT"), (channels[1], "EE")]

fig, axes = plt.subplots(2, 2, figsize=(3.5, 2.9))
for i, (zk, rlab) in enumerate(rows):
    for j, (ch, clab) in enumerate(cols):
        ax = axes[i, j]
        s = seg[ch]
        x = ells[s]
        sig = d["sigma"][s]  # per-ell sigma: normalised-space -> physical dlog10 D
        m = d[f"{zk}_mean_norm"][s] * sig
        sd = d[f"{zk}_std_norm"][s] * sig
        a = d[f"{zk}_anchor_norm"][s] * sig
        ax.fill_between(x, m - sd, m + sd, color=BAND, alpha=0.55, linewidth=0)
        ax.plot(x, m, color=BLUE, lw=1.0)
        ax.plot(x, a, color=MUTED, lw=0.7, ls="--")
        ax.axhline(0.0, color="#c9c7bc", lw=0.6, zorder=0)
        ax.set_xscale("log")
        ax.set_title(f"{rlab.split('---')[0].strip()} $\\cdot$ {clab}", fontsize=7.5,
                     color=INK, pad=2)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(MUTED)
        ax.tick_params(colors=MUTED, labelsize=6.5, pad=1.5)
        if i == 1:
            ax.set_xlabel(r"$\ell$", fontsize=8)
        if j == 0:
            ax.set_ylabel(r"$\partial \log_{10} D_\ell / \partial z_k$", fontsize=7.5)
axes[1, 0].text(0.05, 0.24, "spread mean $\\pm1\\sigma$", color=BLUE, fontsize=6.5,
                transform=axes[1, 0].transAxes)
axes[1, 0].text(0.05, 0.10, "anchor $\\bar z$", color=MUTED, fontsize=6.5,
                transform=axes[1, 0].transAxes)

fig.tight_layout(pad=0.35, h_pad=0.7, w_pad=0.6)
fig.savefig(OUT / "decoder_amplitude.pdf")
fig.savefig(OUT / "decoder_amplitude.png", dpi=200)
print("wrote", OUT / "decoder_amplitude.pdf")
