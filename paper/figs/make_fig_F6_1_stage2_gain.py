"""F6.1 — what the second coordinate buys, and what it does not close (sec 6).

Left, per latent: eta_post_hat(f1) -> eta_post_hat(f1+f2) dumbbells (fraction
of what the latent physically stores). Right, aligned: MI(f2; e1) against the
shuffled-residual null band (control run at the amplitude latent, 2 shuffle
seeds per model). Large gain, still-structured residuals — one figure.
Sources: latent_cards_*.json; nulls from residual_sr_*.json controls
(consolidated onto the cards).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt

import figstyle as st

st.apply_rc()

F1C, COMBC = st.ETA_POST_F1, st.ETA_POST_COMB

data = {}
for run in st.RUNS:
    d = st.load_cards(run)
    rows = []
    for c in d["cards"]:
        suf = c["sufficiency"]
        rows.append({
            "tick": st.latent_tick(run, c),
            "f1": suf["eta_post_hat"], "f1_se": suf.get("eta_post_hat_se", 0.0),
            "comb": suf["eta_post_hat_comb"],
            "mi": c["f2"]["mi_vs_e1"],
        })
    null_hi = max(e["best_mi_unshuffled"] for e in d["controls"]["residual_shuffled"])
    data[run] = (rows, null_hi)
    print(run, "null_hi", round(null_hi, 4))
    for r in rows:
        print(f"  {r['tick']:<26s} {r['f1']:.3f} -> {r['comb']:.3f}   mi={r['mi']:.3f}")

n_tt, n_ee = len(data[st.RUNS[0]][0]), len(data[st.RUNS[1]][0])
fig, axes = plt.subplots(
    2, 2, figsize=(st.COL_W, 3.9), sharex="col",
    gridspec_kw={"height_ratios": [n_tt, n_ee], "width_ratios": [2.35, 1.0],
                 "hspace": 0.16, "wspace": 0.06},
)

for (axL, axR), run in zip(axes, st.RUNS):
    rows, null_hi = data[run]
    n = len(rows)
    ys = np.arange(n)[::-1]

    # -- left: dumbbells on [0, 1]
    axL.set_xlim(0.0, 1.06)
    axL.set_ylim(-0.6, n - 0.4)
    axL.axvline(1.0, color=st.INK, lw=0.7, ls=(0, (4, 3)), zorder=1)
    for y, r in zip(ys, rows):
        axL.plot([r["f1"], r["comb"]], [y, y], color=st.BASELINE, lw=1.6,
                 solid_capstyle="round", zorder=2)
        if r["f1_se"] > 1e-4:
            axL.plot([r["f1"] - r["f1_se"], r["f1"] + r["f1_se"]], [y, y],
                     color=F1C, lw=0.9, zorder=3)
    axL.scatter([r["comb"] for r in rows], ys, s=30, marker="o",
                facecolor=COMBC, edgecolor="white", linewidth=0.6, zorder=4)
    axL.scatter([r["f1"] for r in rows], ys, s=22, marker="D", facecolor=F1C,
                edgecolor="white", linewidth=0.6, zorder=5)
    axL.set_yticks(ys)
    axL.set_yticklabels([r["tick"] for r in rows])
    axL.set_title(st.MODEL_LABEL[run], loc="left", fontsize=8.5,
                  color=st.SECONDARY, pad=2)
    st.despine(axL, keep=("bottom",))
    axL.tick_params(axis="y", length=0)
    axL.grid(axis="x", color=st.GRID, lw=0.5)
    axL.set_axisbelow(True)

    # -- right: stage-2 residual MI vs shuffled-residual null
    axR.set_xscale("log")
    axR.set_xlim(4e-3, 3.2)
    axR.set_ylim(-0.6, n - 0.4)
    axR.axvspan(4e-3, null_hi, color=st.NULL_FILL, alpha=0.8, lw=0, zorder=1)
    axR.axvline(null_hi, color=st.NULL_EDGE, lw=0.7, zorder=2)
    axR.scatter([r["mi"] for r in rows], ys, s=22, facecolor=COMBC,
                edgecolor="white", linewidth=0.6, zorder=4)
    axR.set_yticks(ys); axR.set_yticklabels([])
    st.despine(axR, keep=("bottom",))
    axR.tick_params(axis="y", length=0)
    axR.tick_params(axis="x", which="minor", length=0)
    axR.grid(axis="x", color=st.GRID, lw=0.5)
    axR.set_axisbelow(True)

axes[1, 0].set_xlabel(r"$\hat\eta_{\rm post}$ — fraction of stored info")
axes[1, 1].set_xlabel(r"MI$(f_2;e_1)$ [nat]")
axes[0, 1].set_title("stage-2 signal\nvs null", fontsize=7, loc="left",
                     color=st.SECONDARY, pad=2)

handles = [
    plt.Line2D([], [], marker="D", ls="none", markersize=5, markerfacecolor=F1C,
               markeredgecolor="white", label=r"$\hat\eta_{\rm post}(f_1)$"),
    plt.Line2D([], [], marker="o", ls="none", markersize=5.4,
               markerfacecolor=COMBC, markeredgecolor="white",
               label=r"$\hat\eta_{\rm post}(f_1{+}f_2)$"),
    plt.Rectangle((0, 0), 1, 1, facecolor=st.NULL_FILL,
                  label="shuffled-residual null"),
]
axes[0, 0].legend(handles=handles, loc="lower left",
                  bbox_to_anchor=(-0.02, 1.12), ncol=2, columnspacing=0.8,
                  handletextpad=0.4, borderaxespad=0.0, labelspacing=0.3)

st.save(fig, "F6_1_stage2_gain")
