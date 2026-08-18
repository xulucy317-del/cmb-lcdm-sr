"""F4.1 — cumulative Pareto envelopes per latent, both checkpoints (sec 4).

Per latent: the combined envelope (max over the ms10/ms20/ms30 families of
the cross-seed mean envelope), the plateau band mi_plat +- SE (ms30 family),
the one-SE knee c*, and the shuffled-target control band drawn in-panel
(max over control seeds' best MI vs the shuffled target, <= 0.06 nat vs
1.8-4.3 real). 10/11 envelopes classify "no knee (diffuse)"; EE z2 is the
knee + slow-climb exception. Sources: knee_readout_*.json,
allparams_blind_sr_*.json (controls).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt

import figstyle as st

st.apply_rc()

fig, axes = plt.subplots(2, 6, figsize=(st.FULL_W, 2.75), sharex=True,
                         sharey=True, gridspec_kw={"hspace": 0.34,
                                                   "wspace": 0.10})

for row, run in enumerate(st.RUNS):
    with open(st.EXP / f"knee_readout_{run}.json") as f:
        kn = json.load(f)
    with open(st.EXP / f"allparams_blind_sr_{run}.json") as f:
        ap = json.load(f)
    null_hi = max(e["mi_shuffled"] for e in ap["control"])
    cards = {c["latent"]: c for c in st.load_cards(run)["cards"]}
    col = st.MODEL_COLOR[run]
    zs = sorted(kn["latents"], key=lambda s: int(s[1:]))
    print(run, "null_hi", round(null_hi, 3),
          "c*:", {z: kn["latents"][z]["c_star"] for z in zs})

    for i, z in enumerate(zs):
        l = kn["latents"][z]
        ax = axes[row][i]
        # family mean envelopes, thin
        for fam, v in l["envelopes"].items():
            ax.plot(v["c"], v["mean"], color=col, lw=0.55, alpha=0.30,
                    zorder=2)
        ce = l["combined_envelope"]
        ax.plot(ce["c"], ce["max_of_means"], color=col, lw=1.5, zorder=3)
        # plateau band (ms30 family) and one-SE knee
        p = l["plateau"]
        ax.axhspan(p["mi_plat"] - p["se"], p["mi_plat"] + p["se"],
                   color=col, alpha=0.13, lw=0, zorder=1)
        cs, mi_cs = l["c_star"], l["mi_at_c_star"]
        ax.axvline(cs, color=st.INK, lw=0.6, ls=(0, (3, 2)), zorder=2)
        ax.scatter([cs], [mi_cs], s=13, facecolor="white", edgecolor=st.INK,
                   linewidth=0.8, zorder=4)
        # shuffled-target control band, in-panel
        ax.axhspan(0.0, null_hi, color=st.NULL_FILL, alpha=0.95, lw=0,
                   zorder=1)
        ax.set_title(st.latent_tick(run, cards[int(z[1:])]), fontsize=7.5,
                     pad=2)
        if l["classification"] != "no knee (diffuse)":
            ax.text(0.96, 0.06, l["classification"], transform=ax.transAxes,
                    fontsize=5.8, ha="right", va="bottom", color=st.SECONDARY)
        st.despine(ax)
        ax.grid(True, color=st.GRID, lw=0.4)
        ax.set_axisbelow(True)
        ax.tick_params(labelsize=6.5)

    axes[row][0].set_ylabel(f"{st.MODEL_LABEL[run]}\nval MI [nat]",
                            fontsize=7.5)
    axes[row][0].annotate(f"shuffled-target null $\\leq{null_hi:.2f}$",
                          (1.5, null_hi), xytext=(3, 14),
                          textcoords="offset points", fontsize=5.8,
                          color=st.SECONDARY,
                          arrowprops=dict(arrowstyle="-", color=st.MUTED,
                                          lw=0.5, shrinkB=0))

# legend in the unused TT cell
axl = axes[0][5]
axl.axis("off")
handles = [
    plt.Line2D([], [], color=st.SECONDARY, lw=1.5, label="combined envelope"),
    plt.Line2D([], [], color=st.SECONDARY, lw=0.55, alpha=0.4,
               label="family means (ms10/20/30)"),
    plt.Rectangle((0, 0), 1, 1, facecolor=st.SECONDARY, alpha=0.15,
                  label=r"plateau $\pm$ SE"),
    plt.Line2D([], [], color=st.INK, lw=0.6, ls=(0, (3, 2)),
               marker="o", markersize=3.6, markerfacecolor="white",
               label=r"one-SE knee $c^\ast$"),
    plt.Rectangle((0, 0), 1, 1, facecolor=st.NULL_FILL,
                  label="shuffled-target null"),
]
axl.legend(handles=handles, loc="center left", fontsize=6.4,
           handlelength=1.7, handletextpad=0.5, labelspacing=0.55,
           borderaxespad=0.0, frameon=False)

axes[1][0].set_xlim(1, 30)
axes[1][0].set_ylim(0, 4.5)
for ax in axes[1]:
    ax.set_xlabel("complexity $c$", fontsize=7, labelpad=1)
fig.align_ylabels()

st.save(fig, "F4_1_envelopes")
