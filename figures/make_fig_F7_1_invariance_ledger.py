"""F7.1 — level-set invariance ledger (report section 7).

Per latent: E_inv for f1 alone (open) vs the joint pair (filled), on a log
axis against the frozen 0.05 rule. Nulls drawn in-panel as interval strips:
shuffled-form and wrong-latent E_inv ranges. TT z1/z2/z4 have no joint leg
(union support = all 6 -> no nuisance direction; D-LS). EE z0 is the one
joint FAIL; its pre-registered predicted band is drawn behind the marker.
Sources: latent_cards_*.json (T2-backed card values + consolidated controls),
levelset_audit_joint_*.json for the TT wrong-latent control if present.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt

import figstyle as st

st.apply_rc()

JOINT = "#1c5cab"
THRESH = 0.05

data = {}
for run in st.RUNS:
    d = st.load_cards(run)
    rows = []
    for c in d["cards"]:
        ls = c["levelset"]
        rows.append({
            "tick": st.latent_tick(run, c),
            "f1": ls["f1_e_inv"], "f1_se": ls.get("f1_e_inv_se", 0.0),
            "joint": ls.get("joint_e_inv"),
            "joint_band": ls.get("joint_band"),
            "joint_pass": ls.get("joint_pass"),
            "dls": not ls.get("joint_complement"),
        })
    ctl = d["controls"]
    shuf = [e["e_inv"] for e in ctl["levelset_controls"]["shuffled"]]
    # specificity control: f1-only wrong-latent (both models) U joint variant (EE)
    wrong = [e["e_inv"] for e in ctl["levelset_joint_wrong_latent"]]
    with open(st.EXP / f"levelset_audit_{run}.json") as f:
        wrong += [e["e_inv"] for e in
                  json.load(f)["controls"].get("wrong_latent", [])]
    data[run] = (rows, (min(shuf), max(shuf)), (min(wrong), max(wrong)) if wrong else None)
    print(run, "shuffled-form", data[run][1], "wrong-latent", data[run][2])

n_tt, n_ee = len(data[st.RUNS[0]][0]), len(data[st.RUNS[1]][0])
fig, axes = plt.subplots(
    2, 1, figsize=(st.COL_W, 4.05), sharex=True,
    gridspec_kw={"height_ratios": [n_tt + 1.2, n_ee + 1.2], "hspace": 0.14},
)

for ax, run in zip(axes, st.RUNS):
    rows, shuf_rng, wrong_rng = data[run]
    n = len(rows)
    ys = np.arange(n)[::-1]
    ax.set_xscale("log")
    ax.set_xlim(8e-3, 3.6)
    ax.set_ylim(-0.6, n + 0.9)  # head-room row for the null strips

    ax.axvline(THRESH, color=st.INK, lw=0.7, ls=(0, (4, 3)), zorder=1)

    # null interval strips in the head-room row
    y_null = n + 0.28
    for rng, lab, dy in [(shuf_rng, "shuffled form", 0.0),
                         (wrong_rng, "wrong latent", 0.5)]:
        if rng is None:
            continue
        ax.plot(rng, [y_null + dy] * 2, color=st.NULL_EDGE, lw=2.6,
                solid_capstyle="round", alpha=0.55, zorder=2)
        ax.text(rng[0] * 0.92, y_null + dy, lab + "  ", ha="right",
                va="center", fontsize=6.6, color=st.SECONDARY)

    ticks = []
    for y, r in zip(ys, rows):
        ticks.append(r["tick"] + (r"$^\dagger$" if r["dls"] else ""))
        if r["joint"] is not None:
            ax.plot([r["joint"], r["f1"]], [y, y], color=st.BASELINE, lw=0.9,
                    zorder=2)
            if r["joint_pass"] is False and r["joint_band"]:
                ax.plot(r["joint_band"], [y, y], color=st.STATUS["unresolved"],
                        lw=3.2, alpha=0.45, solid_capstyle="round", zorder=2.5)
            ec = st.STATUS["unresolved"] if r["joint_pass"] is False else "white"
            ax.scatter([r["joint"]], [y], s=26, facecolor=JOINT, edgecolor=ec,
                       linewidth=0.9, zorder=4)
        ax.scatter([r["f1"]], [y], s=24, facecolor="white",
                   edgecolor=st.SECONDARY, linewidth=1.0, zorder=3)

    ax.set_yticks(ys)
    ax.set_yticklabels(ticks)
    ax.set_title(st.MODEL_LABEL[run], loc="left", fontsize=8.5,
                 color=st.SECONDARY, pad=2)
    st.despine(ax, keep=("bottom",))
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=st.GRID, lw=0.5)
    ax.set_axisbelow(True)

axes[1].set_xlabel(r"level-set invariance error $E_{\rm inv}$")
axes[0].text(THRESH * 0.93, n_tt - 0.40, "frozen rule\n0.05", fontsize=6.2,
             color=st.SECONDARY, ha="right", va="center", linespacing=1.2)

handles = [
    plt.Line2D([], [], marker="o", ls="none", markersize=5.2,
               markerfacecolor="white", markeredgecolor=st.SECONDARY,
               markeredgewidth=1.0, label=r"$f_1$ alone"),
    plt.Line2D([], [], marker="o", ls="none", markersize=5.2,
               markerfacecolor=JOINT, markeredgecolor="white",
               label=r"joint $(f_1,f_2)$"),
    plt.Line2D([], [], color=st.STATUS["unresolved"], lw=3.2, alpha=0.45,
               label="predicted band (joint FAIL)"),
]
axes[0].legend(handles=handles, loc="lower left", bbox_to_anchor=(-0.02, 1.10),
               ncol=2, columnspacing=0.9, handletextpad=0.4, borderaxespad=0.0,
               labelspacing=0.3)
fig.text(0.12, -0.035,
         r"$\dagger$ union support = all 6 — no nuisance direction to test"
         " (D-LS)", fontsize=6.6, color=st.SECONDARY, ha="left")

st.save(fig, "F7_1_invariance_ledger")
