"""F5.6 — the derivative-ratio readout as a distribution (section 5.x).

r_top = (df/dtau)/(df/dlnAs) evaluated on the TOP form of every unrestricted
6-input search (per latent, per seed; absent where the top form carries no
tau). The amplitude latents cluster at -2 (TT z2: -1.974+-0.018; EE z5:
-1.993+-0.008, seed SD); the textbook combination inside TT z4's and EE
z1's composites lands there too. Ink diamonds: the frozen answer-agnostic
ratio-field detector's card value r_raw = -2.000 (cv ~ 0). Sources:
allparams_blind_sr_*.json, latent_cards_*.json.
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
REGEX = {"lcdm_tt_beta3e-4": "28/78", "lcdm_tt_ee_lowl": "37/78"}

fig, ax = plt.subplots(figsize=(st.COL_W, 2.5))
rng = np.random.default_rng(2)

x, ticks, tickx = 0, [], []
for run in st.RUNS:
    with open(st.EXP / f"allparams_blind_sr_{run}.json") as f:
        ap = json.load(f)
    cards = {c["latent"]: c for c in st.load_cards(run)["cards"]}
    col = st.MODEL_COLOR[run]
    lat = ap["latents"]
    items = (sorted(lat.items(), key=lambda kv: int(kv[0][1:]))
             if isinstance(lat, dict) else list(enumerate(lat)))
    x0 = x
    for z, l in items:
        k = int(z[1:]) if isinstance(z, str) else z
        rs = [s.get("r_top") for s in l["per_seed"] if s.get("r_top") is not None]
        if rs:
            xj = x + (rng.random(len(rs)) - 0.5) * 0.34
            ax.scatter(xj, rs, s=11, facecolor=col, edgecolor="white",
                       linewidth=0.4, alpha=0.9, zorder=3)
        else:
            ax.text(x, -3.32, "–", ha="center", va="center", fontsize=7,
                    color=st.MUTED)
        rp = cards[k]["signature"]["ratio_pairs"]
        pair = next((p for p in rp if p["pair"] == ["tau", "ln10As"]), None)
        if pair is not None:
            ax.scatter([x], [pair["r_raw"]], s=26, marker="D",
                       facecolor="none", edgecolor=st.INK, linewidth=1.0,
                       zorder=5)
        if k == AMP[run]:
            m, sd = np.mean(rs), np.std(rs, ddof=1)
            ax.annotate(f"${m:.3f}\\pm{sd:.3f}$", (x, min(rs)),
                        xytext=(0, -11), textcoords="offset points",
                        fontsize=6.0, ha="center", color=st.SECONDARY)
            print(run, f"z{k} pooled {m:.4f} +- {sd:.4f}")
        ticks.append(f"$z_{k}$")
        tickx.append(x)
        x += 1
    ax.text((x0 + x - 1) / 2, 3.05, st.MODEL_LABEL[run], ha="center",
            fontsize=6.8, color=st.SECONDARY)
    ax.text((x0 + x - 1) / 2, 2.55, f"textbook in {REGEX[run]} front eqs",
            ha="center", fontsize=5.6, color=st.MUTED)
    x += 1.0

ax.axhline(-2.0, color=st.INK, lw=0.7, ls=(0, (4, 3)), zorder=1)
ax.text(-0.72, -1.83, r"$-2$", va="bottom", ha="left", fontsize=7,
        color=st.INK)
ax.text(x - 0.7, -1.35, "– : no $\\tau$ in top form", ha="right",
        va="center", fontsize=5.6, color=st.MUTED)
ax.set_xticks(tickx)
ax.set_xticklabels(ticks, fontsize=6.6)
ax.set_xlim(-0.8, x - 0.6)
ax.set_ylim(-3.5, 3.4)
ax.set_ylabel(r"$r_{\rm top}=(\partial f/\partial\tau)\,/\,"
              r"(\partial f/\partial \ln A_s)$", fontsize=7.5)
st.despine(ax)
ax.grid(axis="y", color=st.GRID, lw=0.5)
ax.set_axisbelow(True)
ax.tick_params(axis="x", length=0)

handles = [
    plt.Line2D([], [], marker="o", ls="none", markersize=4,
               markerfacecolor=st.SECONDARY, markeredgecolor="white",
               label="top form, per seed"),
    plt.Line2D([], [], marker="D", ls="none", markersize=5,
               markerfacecolor="none", markeredgecolor=st.INK,
               label=r"frozen detector $r_{\rm raw}$"),
]
ax.legend(handles=handles, loc="lower left", fontsize=6.2,
          handletextpad=0.3, borderaxespad=0.2, labelspacing=0.3)

st.save(fig, "F5_6_ratio_readout")
