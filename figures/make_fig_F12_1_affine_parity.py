"""F12.1 — affine parity on both endpoints (conclusive report, stage 2).

(a) Direct reconstruction on T2: the six-input OLS map refitted in the
    `logamp64` arm against the MSE-SR maxsize-40 winner (median and min–max
    over the five frozen seeds). Source: experiments/coordinate_matched_ols_v1.json.
(b) Information: the fraction of what each latent physically stores that is
    carried by the canonical f1, by the two-stage f1+f2 composite, and by the
    plain affine index w·theta (eta_post_hat, same T2 posterior draw).
    Source: experiments/eta_post_ols_index_v1.json.

Both panels: card order, TT above EE, per-checkpoint scope.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt

import figstyle as st

st.apply_rc()

OLS_C = "#0b0b0b"
SR_C = st.ETA_PLAT
F1C, COMBC = st.ETA_POST_F1, st.ETA_POST_COMB

with open(st.EXP / "coordinate_matched_ols_v1.json") as f:
    audit = json.load(f)["arms"]["logamp64"]
with open(st.EXP / "eta_post_ols_index_v1.json") as f:
    eta = json.load(f)["runs"]

rows = {run: [] for run in st.RUNS}
for run in st.RUNS:
    cards = {c["latent"]: c for c in st.load_cards(run)["cards"]}
    for a in [x for x in audit if x["run"] == run]:
        k = a["latent"]
        e = next(x for x in eta[run]["latents"] if x["latent"] == k)
        rows[run].append({
            "tick": st.latent_tick(run, cards[k]),
            "ols": 100 * a["ols_raw_nmse"],
            "sr_med": 100 * a["mse_sr_raw_nmse"]["median"],
            "sr_lo": 100 * a["mse_sr_raw_nmse"]["min"],
            "sr_hi": 100 * a["mse_sr_raw_nmse"]["max"],
            "f1": e["canonical_eta_post_hat"],
            "comb": e["hierarchy_eta_post_hat_comb"],
            "idx": e["eta_post_hat"],
            "idx_se": e["eta_post_hat_se"],
        })
    print(run)
    for r in rows[run]:
        print(f"  {r['tick']:<26s} OLS {r['ols']:.3f}%  mse40 {r['sr_med']:.3f}% "
              f"[{r['sr_lo']:.3f},{r['sr_hi']:.3f}]   eta f1 {r['f1']:.3f} "
              f"f1+f2 {r['comb']:.3f} index {r['idx']:.3f}")

n_tt, n_ee = len(rows[st.RUNS[0]]), len(rows[st.RUNS[1]])
fig, axes = plt.subplots(
    2, 2, figsize=(st.FULL_W, 3.7), sharex="col",
    gridspec_kw={"height_ratios": [n_tt, n_ee], "hspace": 0.18, "wspace": 0.42},
)

for i, run in enumerate(st.RUNS):
    rs = rows[run]
    n = len(rs)
    ys = np.arange(n)[::-1]

    # ---- (a) reconstruction
    ax = axes[i, 0]
    ax.set_xscale("log")
    ax.set_xlim(0.02, 12)
    ax.set_ylim(-0.6, n - 0.4)
    for y, r in zip(ys, rs):
        lo, hi = min(r["ols"], r["sr_lo"]), max(r["ols"], r["sr_hi"])
        ax.plot([r["sr_lo"], r["sr_hi"]], [y, y], color=SR_C, lw=2.2,
                alpha=0.35, solid_capstyle="butt", zorder=2)
    ax.scatter([r["sr_med"] for r in rs], ys, s=26, marker="s", facecolor=SR_C,
               edgecolor="white", linewidth=0.6, zorder=4)
    ax.scatter([r["ols"] for r in rs], ys, s=30, marker="o", facecolor=OLS_C,
               edgecolor="white", linewidth=0.6, zorder=5)
    ax.set_yticks(ys)
    ax.set_yticklabels([r["tick"] for r in rs])
    ax.set_title(st.MODEL_LABEL[run], loc="left", fontsize=8.5,
                 color=st.SECONDARY, pad=2)
    st.despine(ax, keep=("bottom",))
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=st.GRID, lw=0.5)
    ax.set_axisbelow(True)

    # ---- (b) information
    ax = axes[i, 1]
    ax.set_xlim(0.0, 1.06)
    ax.set_ylim(-0.6, n - 0.4)
    ax.axvline(1.0, color=st.INK, lw=0.7, ls=(0, (4, 3)), zorder=1)
    for y, r in zip(ys, rs):
        vals = [r["f1"], r["comb"], r["idx"]]
        ax.plot([min(vals), max(vals)], [y, y], color=st.BASELINE, lw=1.6,
                solid_capstyle="round", zorder=2)
        if r["idx_se"] > 1e-4:
            ax.plot([r["idx"] - r["idx_se"], r["idx"] + r["idx_se"]], [y, y],
                    color=OLS_C, lw=0.9, zorder=3)
    ax.scatter([r["f1"] for r in rs], ys, s=22, marker="D", facecolor=F1C,
               edgecolor="white", linewidth=0.6, zorder=4)
    ax.scatter([r["comb"] for r in rs], ys, s=30, marker="o", facecolor=COMBC,
               edgecolor="white", linewidth=0.6, zorder=5)
    ax.scatter([r["idx"] for r in rs], ys, s=34, marker="o", facecolor=OLS_C,
               edgecolor="white", linewidth=0.6, zorder=6)
    ax.set_yticks(ys)
    ax.set_yticklabels([r["tick"] for r in rs])
    ax.set_title(st.MODEL_LABEL[run], loc="left", fontsize=8.5,
                 color=st.SECONDARY, pad=2)
    st.despine(ax, keep=("bottom",))
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=st.GRID, lw=0.5)
    ax.set_axisbelow(True)

axes[1, 0].set_xlabel("(a)  direct reconstruction, T2 NMSE [%]  (log)")
axes[1, 1].set_xlabel(r"(b)  $\hat\eta_{\rm post}$ — fraction of stored info")

hA = [
    plt.Line2D([], [], marker="o", ls="none", markersize=5.6, markerfacecolor=OLS_C,
               markeredgecolor="white", label="six-input OLS (7 coefficients)"),
    plt.Line2D([], [], marker="s", ls="-", lw=2.2, color=SR_C, alpha=0.5,
               markersize=5, markerfacecolor=SR_C, markeredgecolor="white",
               label="MSE-SR ms40: median, min–max over 5 seeds"),
]
axes[0, 0].legend(handles=hA, loc="lower left", bbox_to_anchor=(-0.02, 1.13),
                  ncol=1, handletextpad=0.5, borderaxespad=0.0, labelspacing=0.25)
hB = [
    plt.Line2D([], [], marker="D", ls="none", markersize=5, markerfacecolor=F1C,
               markeredgecolor="white", label=r"canonical $f_1$"),
    plt.Line2D([], [], marker="o", ls="none", markersize=5.4, markerfacecolor=COMBC,
               markeredgecolor="white", label=r"$f_1{+}f_2$"),
    plt.Line2D([], [], marker="o", ls="none", markersize=5.8, markerfacecolor=OLS_C,
               markeredgecolor="white", label=r"OLS index $w\cdot\theta$"),
]
axes[0, 1].legend(handles=hB, loc="lower left", bbox_to_anchor=(-0.02, 1.13),
                  ncol=3, columnspacing=0.7, handletextpad=0.35,
                  borderaxespad=0.0, labelspacing=0.25, fontsize=7)

st.save(fig, "F12_1_affine_parity")
