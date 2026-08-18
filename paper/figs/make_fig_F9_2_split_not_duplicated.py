"""F9.2 — split, not duplicated (section 9).

(a) Own-latent sparse-probe R2 per coordinate: every f1 is latent-anchored
(0.88-0.95, own latent always in the 1-SE carrier set) while every f2 is
distributed (0.01-0.58); shuffled-probe null ~ 0.000. (b) Redundancy vs
synergy for every coordinate's top-2 carrier pair: conditional MI
I(f; z_top2 | z_top1) against the marginal I(f; z_top2) — every point sits
above the diagonal (synergy); no redundant pair exists in either model. The
labeled point is the EE textbook coordinate: z1's information about
A_s e^{-2tau} rises 0.013 -> 0.473 nat when conditioned on z5.
Source: subspace_probe_*.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt

import figstyle as st

st.apply_rc()

F1C, F2C = st.ETA_POST_F1, "#86b6ef"

cand = {}
for run in st.RUNS:
    with open(st.EXP / f"subspace_probe_{run}.json") as f:
        cand[run] = json.load(f)["candidates"]

fig = plt.figure(figsize=(st.COL_W, 4.6))
gs = fig.add_gridspec(3, 1, height_ratios=[5, 6, 9.5], hspace=0.42)

# ------------------------------------------------- (a) own-latent probe R2
for gi, run in enumerate(st.RUNS):
    ax = fig.add_subplot(gs[gi])
    cards = {c["latent"]: c for c in st.load_cards(run)["cards"]}
    per = {}
    for c in cand[run]:
        per.setdefault(c["latent"], {})[c["stage"]] = c["probe"]["r2_own"]
    n = len(per)
    ys = np.arange(n)[::-1]
    ax.set_xlim(0, 1.02)
    ax.set_ylim(-0.6, n - 0.4)
    for y, k in zip(ys, sorted(per)):
        ax.plot([per[k]["f2"], per[k]["f1"]], [y, y], color=st.GRID, lw=1.4,
                zorder=2)
    ax.scatter([per[k]["f1"] for k in sorted(per)], ys, s=22, marker="D",
               facecolor=F1C, edgecolor="white", linewidth=0.6, zorder=4)
    ax.scatter([per[k]["f2"] for k in sorted(per)], ys, s=22, marker="s",
               facecolor=F2C, edgecolor="white", linewidth=0.6, zorder=4)
    ax.axvline(0.0, color=st.NULL_EDGE, lw=0.8, zorder=1)
    ax.set_yticks(ys)
    ax.set_yticklabels([st.latent_tick(run, cards[k]) for k in sorted(per)],
                       fontsize=6.6)
    ax.set_title(st.MODEL_LABEL[run], loc="left", fontsize=7.5,
                 color=st.SECONDARY, pad=2)
    st.despine(ax, keep=("bottom",))
    ax.tick_params(axis="y", length=0, labelsize=6.4)
    ax.tick_params(axis="x", labelsize=6.4)
    ax.grid(axis="x", color=st.GRID, lw=0.4)
    ax.set_axisbelow(True)
    if gi == 0:
        fig.suptitle("(a)  own-latent probe $R^2$   (shuffled-probe null"
                     r" $\approx 0.000$)", x=0.125, y=0.995, ha="left",
                     fontsize=8, color=st.INK)
        # direct labels on the bottom row (clear of the panel title)
        kb = sorted(per)[-1]
        ax.annotate(r"$f_1$ anchored", (per[kb]["f1"], ys[-1]),
                    xytext=(-6, 5), textcoords="offset points", fontsize=6.2,
                    color=st.SECONDARY, ha="right")
        ax.annotate(r"$f_2$ distributed", (per[kb]["f2"], ys[-1]),
                    xytext=(8, 5), textcoords="offset points", fontsize=6.2,
                    color=st.SECONDARY, ha="left")

# ------------------------------------------------- (b) synergy vs redundancy
ax = fig.add_subplot(gs[2])
STAR = ("lcdm_tt_ee_lowl", 5, "f1")
for run in st.RUNS:
    col = st.MODEL_COLOR[run]
    for c in cand[run]:
        red = c.get("redundancy") or {}
        t21 = red.get("top2_given_top1")
        if not t21:
            continue
        xm, yc = red["mi_top2"], t21["mi_cond"]
        mk = "o" if c["stage"] == "f1" else "s"
        star = (run, c["latent"], c["stage"]) == STAR
        ax.scatter([xm], [yc], s=26 if star else 17, marker=mk,
                   facecolor=col, edgecolor=st.INK if star else "white",
                   linewidth=1.0 if star else 0.5, zorder=5 if star else 4)
        if star:
            ax.annotate("$z_1$'s info about $A_s e^{-2\\tau}$,\n"
                        "given $z_5$:  $0.013 \\to 0.473$",
                        (xm, yc), xytext=(8, 9), textcoords="offset points",
                        fontsize=6.0, color=st.INK, ha="left")
xx = np.array([2e-3, 2.0])
ax.plot(xx, xx, color=st.BASELINE, lw=0.8, zorder=1)
ax.fill_between(xx, xx * 1e-3, xx, color=st.NULL_FILL, alpha=0.5, lw=0,
                zorder=0)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(3e-3, 0.7); ax.set_ylim(8e-3, 2.0)
ax.text(0.30, 0.135, "redundant side\n(empty)", fontsize=6.0,
        color=st.SECONDARY, ha="center")
ax.set_xlabel(r"marginal  MI$(f; z_{\rm top2})$ [nat]", labelpad=1.5,
              fontsize=7)
ax.set_ylabel(r"conditional  MI$(f; z_{\rm top2}\,|\,z_{\rm top1})$",
              fontsize=7)
ax.set_title("(b)  top-2 carrier conditionals: all synergistic", loc="left",
             fontsize=8, color=st.INK, pad=3)
h = [plt.Line2D([], [], marker="o", ls="none", markersize=4.2,
                markerfacecolor=st.MODEL_COLOR[r], markeredgecolor="white",
                label=st.MODEL_LABEL[r]) for r in st.RUNS]
h += [plt.Line2D([], [], marker="s", ls="none", markersize=4.2,
                 markerfacecolor=st.MUTED, markeredgecolor="white",
                 label=r"$f_2$ (squares)")]
ax.legend(handles=h, loc="lower right", fontsize=6.0, handletextpad=0.25,
          borderaxespad=0.2, labelspacing=0.25)
st.despine(ax)
ax.grid(True, color=st.GRID, lw=0.4)
ax.set_axisbelow(True)
ax.tick_params(labelsize=6.4)
ax.tick_params(which="minor", length=0)

st.save(fig, "F9_2_split_not_duplicated")
