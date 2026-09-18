"""F5.2 — subset-campaign staircases at full protocol (section 5).

Per latent: best budget-matched support-restricted ceiling M_S^(c<=10) vs
support size |S|, over the complete 63-support x 5-seed full-protocol grid
(R-P4). Marked: the best strict subset S+ (filled) and the all-6 ceiling
(open, with a dashed level line). The amplitude panels double as the
positive control: the {tau, A_s} step is highlighted — the frozen machinery
finds the known pair among all supports with no special status, and the
all-6 superset finding sits above it. Source: subsets_full_*.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt

import figstyle as st

st.apply_rc()

AMP = {"lcdm_tt_beta3e-4": 2, "lcdm_tt_ee_lowl": 5}

fig, axes = plt.subplots(2, 6, figsize=(st.FULL_W, 2.7), sharex=True,
                         sharey=True, gridspec_kw={"hspace": 0.34,
                                                   "wspace": 0.10})

for row, run in enumerate(st.RUNS):
    with open(st.EXP / f"subsets_full_{run}.json") as f:
        sf = json.load(f)["latents"]
    cards = {c["latent"]: c for c in st.load_cards(run)["cards"]}
    col = st.MODEL_COLOR[run]
    zs = sorted(sf, key=lambda s: int(s[1:]))
    for i, z in enumerate(zs):
        l = sf[z]
        ax = axes[row][i]
        sizes = sorted(int(k) for k in l["staircase"])
        M = [l["staircase"][str(s)]["M"] for s in sizes]
        all6 = l["staircase"]["6"]["M"]
        # S+ = best strict subset on T0-val = staircase max over sizes 1..5
        strict = [(l["staircase"][str(s)]["M"], s) for s in sizes if s < 6]
        m_sp, s_sp = max(strict)
        if set(l["staircase"][str(s_sp)]["S"]) != set(l["s_plus"]):
            print("NOTE", run, z, "staircase argmax != s_plus")
        ax.axhline(all6, color=col, lw=0.6, ls=(0, (4, 3)), alpha=0.6,
                   zorder=1)
        ax.plot(sizes, M, color=col, lw=1.3, marker="o", markersize=2.6,
                markerfacecolor=col, markeredgecolor="none", zorder=3)
        ax.scatter([6], [all6], s=26, facecolor="white", edgecolor=col,
                   linewidth=1.1, zorder=4)
        ax.scatter([s_sp], [m_sp], s=28, facecolor=col, edgecolor="white",
                   linewidth=0.8, zorder=5)
        if int(z[1:]) == AMP[run]:
            pair = l["staircase"]["2"]
            is_pair = set(pair["S"]) == {"tau", "A_s"}
            ax.scatter([2], [pair["M"]], s=42, facecolor="none",
                       edgecolor=st.INK, linewidth=1.0, zorder=6)
            ax.annotate(r"$\{\tau, A_s\}$" if is_pair else "best pair",
                        (2, pair["M"]), xytext=(3, -10),
                        textcoords="offset points", fontsize=6.0,
                        color=st.INK)
            print(run, z, "size-2 best support:", pair["S"])
        ax.set_title(st.latent_tick(run, cards[int(z[1:])]), fontsize=7.5,
                     pad=2)
        st.despine(ax)
        ax.grid(True, color=st.GRID, lw=0.4)
        ax.set_axisbelow(True)
        ax.tick_params(labelsize=6.5)
    axes[row][0].set_ylabel(f"{st.MODEL_LABEL[run]}\n"
                            r"$M_S^{(c\leq10)}$ [nat]", fontsize=7.5)

axl = axes[0][5]
axl.axis("off")
handles = [
    plt.Line2D([], [], color=st.SECONDARY, lw=1.3, marker="o", markersize=2.6,
               label="best support per size"),
    plt.Line2D([], [], marker="o", ls="none", markersize=5.4,
               markerfacecolor=st.SECONDARY, markeredgecolor="white",
               label=r"$S^+$ (best strict subset)"),
    plt.Line2D([], [], marker="o", ls="none", markersize=5.2,
               markerfacecolor="white", markeredgecolor=st.SECONDARY,
               label="all-6 (dashed level)"),
    plt.Line2D([], [], marker="o", ls="none", markersize=6.4,
               markerfacecolor="none", markeredgecolor=st.INK,
               label=r"positive control $\{\tau, A_s\}$"),
]
axl.legend(handles=handles, loc="center left", fontsize=6.3,
           handlelength=1.5, handletextpad=0.5, labelspacing=0.55,
           borderaxespad=0.0, frameon=False)

axes[1][0].set_xlim(0.6, 6.4)
axes[1][0].set_xticks([1, 2, 3, 4, 5, 6])
for ax in axes[1]:
    ax.set_xlabel("support size $|S|$", fontsize=7, labelpad=1)
fig.align_ylabels()

st.save(fig, "F5_2_staircases")
