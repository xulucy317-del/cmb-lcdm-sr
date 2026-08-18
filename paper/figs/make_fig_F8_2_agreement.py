"""F8.2 — decoder loadings agree with symbolic signatures (section 8).

Per latent: cos(a*, g_j) between the decoder-effect template loading and the
canonical form's sensitivity signature (0.77-1.00). Amplitude-sector latents
are drawn hollow: their cosines rest partly on ridge-drifting (tau, lnAs)
components (F8.3), so they are weaker evidence than the shape-sector ones.
The in-row gray text gives the decomposition R2_W. Source: latent_cards_*.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt

import figstyle as st

st.apply_rc()

AMP_SECTOR = {"lcdm_tt_beta3e-4": {2}, "lcdm_tt_ee_lowl": {4, 5}}

fig, ax = plt.subplots(figsize=(st.COL_W, 2.55))
y = 0
yticks, ylabels = [], []
for run in st.RUNS:
    cards = st.load_cards(run)["cards"]
    col = st.MODEL_COLOR[run]
    ax.text(0.665, y + 0.42, st.MODEL_LABEL[run], fontsize=7.2,
            color=st.SECONDARY, va="center")
    y -= 1
    for c in cards:
        cos = c["signature"]["decoder_cos_g"]
        amp = c["latent"] in AMP_SECTOR[run]
        ax.plot([0.66, cos], [y, y], color=st.GRID, lw=1.2, zorder=2)
        ax.scatter([cos], [y], s=24,
                   facecolor="white" if amp else col, edgecolor=col,
                   linewidth=1.1, zorder=4)
        ax.text(1.045, y, f"$R^2_W$ {c['decoder']['r2_W']:.3f}",
                fontsize=5.8, color=st.MUTED, va="center")
        yticks.append(y)
        ylabels.append(st.latent_tick(run, c))
        y -= 1
    y -= 0.4
ax.axvline(1.0, color=st.INK, lw=0.7, ls=(0, (4, 3)), zorder=1)
ax.set_xlim(0.66, 1.20)
ax.set_ylim(y + 0.8, 0.9)
ax.set_xticks([0.7, 0.8, 0.9, 1.0])
ax.set_yticks(yticks)
ax.set_yticklabels(ylabels, fontsize=6.5)
ax.set_xlabel(r"cos$(a^\ast, g_j)$: decoder loading vs symbolic signature",
              fontsize=7.5)
st.despine(ax, keep=("bottom",))
ax.tick_params(axis="y", length=0)
ax.grid(axis="x", color=st.GRID, lw=0.5)
ax.set_axisbelow(True)

h = [plt.Line2D([], [], marker="o", ls="none", markersize=5,
                markerfacecolor=st.INK, markeredgecolor=st.INK,
                label="shape sector"),
     plt.Line2D([], [], marker="o", ls="none", markersize=5,
                markerfacecolor="white", markeredgecolor=st.INK,
                label="amplitude (ridge-drifting)")]
ax.legend(handles=h, loc="lower left", bbox_to_anchor=(-0.02, 1.01),
          ncol=2, fontsize=6.2, handletextpad=0.3, columnspacing=0.9,
          borderaxespad=0.0, labelspacing=0.3)

st.save(fig, "F8_2_agreement")
