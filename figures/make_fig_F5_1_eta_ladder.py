"""F5.1 — the eta ladder, per latent (report section 5 centrepiece).

For every latent: eta_S (saturates its own support), eta_plat (fraction of
the SR-accessible mean map at the knee slice), eta_post_hat(f1) (fraction of
what the latent physically stores). The visible gap between eta_S ~ 1 and
eta_post_hat < 1 is the section-title claim. Values: T2-confirmed card
numbers (experiments/latent_cards_*.json).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt

import figstyle as st

st.apply_rc()

RUNGS = [
    ("eta_s", None, st.ETA_S, "o", r"$\eta_S$ — own-support ceiling"),
    ("eta_plat", None, st.ETA_PLAT, "s", r"$\eta_{\rm plat}$ — search plateau"),
    ("eta_post_hat", "eta_post_hat_se", st.ETA_POST_F1, "D",
     r"$\hat\eta_{\rm post}(f_1)$ — latent's stored info"),
]

data = {}
for run in st.RUNS:
    cards = st.load_cards(run)["cards"]
    rows = []
    for c in cards:
        suf = c["sufficiency"]
        rows.append({
            "tick": st.latent_tick(run, c),
            "eta_s": suf["eta_s"],
            "eta_s_se": c["s_star"].get("eta_se", 0.0) or 0.0,
            "eta_plat": suf["eta_plat"],
            "eta_post_hat": suf["eta_post_hat"],
            "eta_post_hat_se": suf.get("eta_post_hat_se", 0.0) or 0.0,
        })
    data[run] = rows
    print(run)
    for r in rows:
        print(f"  {r['tick']:<26s} eta_S={r['eta_s']:.3f}  "
              f"eta_plat={r['eta_plat']:.3f}  eta_post={r['eta_post_hat']:.3f}")

n_tt, n_ee = len(data[st.RUNS[0]]), len(data[st.RUNS[1]])
fig, axes = plt.subplots(
    2, 1, figsize=(st.COL_W, 3.95), sharex=True,
    gridspec_kw={"height_ratios": [n_tt, n_ee], "hspace": 0.16},
)

for ax, run in zip(axes, st.RUNS):
    rows = data[run]
    n = len(rows)
    ys = np.arange(n)[::-1]  # card order top -> bottom
    ax.set_xlim(0.0, 1.14)
    ax.set_ylim(-0.6, n - 0.4)

    ax.axvline(1.0, color=st.INK, lw=0.7, ls=(0, (4, 3)), zorder=1)

    for y, r in zip(ys, rows):
        vals = [r["eta_s"], r["eta_plat"], r["eta_post_hat"]]
        ax.plot([min(vals), max(vals)], [y, y], color=st.GRID, lw=1.6,
                solid_capstyle="round", zorder=2)
    for key, sekey, color, marker, _ in RUNGS:
        for y, r in zip(ys, rows):
            se = r.get(f"{key}_se" if sekey is None else sekey, 0.0)
            if key == "eta_s":
                se = r["eta_s_se"]
            if se and se > 1e-4:
                ax.plot([r[key] - se, r[key] + se], [y, y], color=color,
                        lw=0.9, zorder=3)
        ax.scatter([r[key] for r in rows], ys, s=26, marker=marker,
                   facecolor=color, edgecolor="white", linewidth=0.6, zorder=4)

    ax.set_yticks(ys)
    ax.set_yticklabels([r["tick"] for r in rows])
    ax.set_title(st.MODEL_LABEL[run], loc="left", fontsize=8.5,
                 color=st.SECONDARY, pad=3)
    st.despine(ax, keep=("bottom",))
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=st.GRID, lw=0.5)
    ax.set_axisbelow(True)

axes[1].set_xlabel("fraction of ceiling  (dashed: saturation)")

handles = [
    plt.Line2D([], [], marker=m, ls="none", markersize=5.5,
               markerfacecolor=c, markeredgecolor="white", markeredgewidth=0.6,
               label=lab)
    for _, _, c, m, lab in RUNGS
]
axes[0].legend(handles=handles, loc="lower left", bbox_to_anchor=(-0.02, 1.06),
               ncol=1, handletextpad=0.4, borderaxespad=0.0, labelspacing=0.25)

st.save(fig, "F5_1_eta_ladder")
