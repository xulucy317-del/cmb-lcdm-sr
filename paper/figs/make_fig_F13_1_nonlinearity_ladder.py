"""F13.1 — the nonlinearity ladder, per latent (conclusive report, stage 3).

T2 NMSE (log axis) of the exact hypothesis classes and of the searches:

  * affine — six-input OLS in the sampled basis, T0-fit coefficients
    (recomputed here; reproduces the audit's `logamp64` OLS values);
  * quadratic — the same plus all 21 second-order terms (28 coefficients),
    exact least squares, T0-fit (recomputed here; reproduces the record's
    §6.5 table);
  * MSE-SR ms40 and calibrated MI-SR ms20 medians in the `logamp64` arm
    (experiments/coordinate_matched_ols_v1.json);
  * the OLS + SR-on-residual hybrid for the two latents Step 2 ran on
    (results/lcdm_tt_ee_lowl/residual_sr_ols/analysis_summary.json):
    frozen monotone map, and the free 1-D map as a diagnostic;
  * the six-input gradient-boosting floor beneath the OLS residual
    (experiments/capacity_and_noise_floor_v1.json), drawn as the lower bound.

Conventions match scripts/build_ols_residual_cache.py: inputs standardised
with T0-fit statistics, full-rank lstsq on the 4,000 T0-fit rows, NMSE on
the 25,000 T2 rows. Deterministic.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt

import figstyle as st

st.apply_rc()

T0_FIT = slice(0, 4000)
T2 = slice(25000, 50000)

# ------------------------------------------------------------ exact classes
theta = np.load(st.REPO / "data" / "theta.npy")
sid = np.load(st.REPO / "data" / "splits_v1.npz")["split_id"]
th = theta[sid == 2]
assert th.shape == (50000, 6)
mu0, sd0 = th[T0_FIT].mean(0), th[T0_FIT].std(0)
U = (th - mu0) / sd0
iu = np.triu_indices(6)
Q = np.stack([U[:, i] * U[:, j] for i, j in zip(*iu)], axis=1)  # 21 terms
A_aff = np.hstack([np.ones((len(U), 1)), U])
A_quad = np.hstack([A_aff, Q])


def nmse_T2(A, y):
    w, *_ = np.linalg.lstsq(A[T0_FIT], y[T0_FIT], rcond=None)
    r = y - A @ w
    return float(np.mean(r[T2] ** 2) / y[T2].var())


# ------------------------------------------------------------- search rungs
with open(st.EXP / "coordinate_matched_ols_v1.json") as f:
    audit = json.load(f)["arms"]["logamp64"]
with open(st.EXP / "capacity_and_noise_floor_v1.json") as f:
    det = json.load(f)["determinism"]
with open(st.REPO / "results" / "lcdm_tt_ee_lowl" / "residual_sr_ols"
          / "analysis_summary.json") as f:
    step2 = json.load(f)["latents"]


def floor_for(run, k):
    return float(det[run][f"z{k}"]["nmse_gbm_floor"])


rows = {run: [] for run in st.RUNS}
for run in st.RUNS:
    means = np.load(st.REPO / "models" / run / "analysis" / "encoder_means_test.npy")
    cards = {c["latent"]: c for c in st.load_cards(run)["cards"]}
    for a in [x for x in audit if x["run"] == run]:
        k = a["latent"]
        y = means[:, k].astype(np.float64)
        aff, quad = nmse_T2(A_aff, y), nmse_T2(A_quad, y)
        r = {
            "k": k,
            "tick": st.latent_tick(run, cards[k]),
            "affine": 100 * aff,
            "quadratic": 100 * quad,
            "gap_closed": (aff - quad) / aff,
            "mse40": 100 * a["mse_sr_raw_nmse"]["median"],
            "misr": 100 * a["mi_sr_calibrated_nmse"]["median"],
            "floor": 100 * floor_for(run, k),
            "audit_ols": 100 * a["ols_raw_nmse"],
        }
        if run == "lcdm_tt_ee_lowl" and str(k) in step2:
            s = step2[str(k)]
            r["hybrid"] = 100 * s["combined_hybrid_median_nmse_T2"]
            r["hybrid_free"] = 100 * s["combined_hybrid_median_nmse_T2_nonmonotone"]
        rows[run].append(r)
    print(run)
    for r in rows[run]:
        extra = (f"  hybrid {r['hybrid']:.3f}% / free {r['hybrid_free']:.3f}%"
                 if "hybrid" in r else "")
        print(f"  {r['tick']:<26s} affine {r['affine']:.3f}% (audit {r['audit_ols']:.3f}%)"
              f"  quad {r['quadratic']:.3f}%  closed {100*r['gap_closed']:.0f}%"
              f"  mse40 {r['mse40']:.3f}%  MI-SR {r['misr']:.3f}%"
              f"  floor {r['floor']:.4f}%{extra}")
        assert abs(r["affine"] - r["audit_ols"]) < 2e-3, "affine fit drifted from the audit"

# ------------------------------------------------------------------- figure
AFF_C, QUAD_C = "#0b0b0b", st.ETA_PLAT
SR_C = st.MUTED
HYB_C = st.STATUS["unresolved"]
FLOOR_C = st.NULL_EDGE

n_tt, n_ee = len(rows[st.RUNS[0]]), len(rows[st.RUNS[1]])
fig, axes = plt.subplots(
    2, 1, figsize=(st.COL_W + 0.9, 4.1), sharex=True,
    gridspec_kw={"height_ratios": [n_tt, n_ee], "hspace": 0.16},
)
for ax, run in zip(axes, st.RUNS):
    rs = rows[run]
    n = len(rs)
    ys = np.arange(n)[::-1]
    ax.set_xscale("log")
    ax.set_xlim(2e-4, 40)
    ax.set_ylim(-0.6, n - 0.4)
    for y, r in zip(ys, rs):
        # floor band: from the floor to the affine value, faint
        ax.plot([r["floor"], r["affine"]], [y, y], color=st.GRID, lw=1.6,
                solid_capstyle="round", zorder=1)
        ax.plot([r["quadratic"], r["affine"]], [y, y], color=QUAD_C, lw=2.2,
                alpha=0.45, solid_capstyle="butt", zorder=2)
        ax.plot([r["floor"]], [y], marker="|", markersize=7, color=FLOOR_C,
                mew=1.2, ls="none", zorder=3)
        if "hybrid" in r:
            ax.plot([r["hybrid_free"], r["hybrid"]], [y, y], color=HYB_C,
                    lw=1.0, ls=(0, (2, 2)), zorder=3)
            ax.scatter([r["hybrid"]], [y], s=42, marker="*", facecolor=HYB_C,
                       edgecolor="white", linewidth=0.5, zorder=7)
            ax.scatter([r["hybrid_free"]], [y], s=42, marker="*", facecolor="white",
                       edgecolor=HYB_C, linewidth=0.8, zorder=7)
    ax.scatter([r["mse40"] for r in rs], ys, s=20, marker="^", facecolor="white",
               edgecolor=SR_C, linewidth=0.8, zorder=4)
    ax.scatter([r["misr"] for r in rs], ys, s=20, marker="v", facecolor="white",
               edgecolor=SR_C, linewidth=0.8, zorder=4)
    ax.scatter([r["quadratic"] for r in rs], ys, s=26, marker="s", facecolor=QUAD_C,
               edgecolor="white", linewidth=0.6, zorder=5)
    ax.scatter([r["affine"] for r in rs], ys, s=30, marker="o", facecolor=AFF_C,
               edgecolor="white", linewidth=0.6, zorder=6)
    for y, r in zip(ys, rs):
        ax.text(13.0, y, f"{100*r['gap_closed']:.0f}%", fontsize=6.4,
                color=QUAD_C, va="center", ha="left")
    ax.set_yticks(ys)
    ax.set_yticklabels([r["tick"] for r in rs])
    ax.set_title(st.MODEL_LABEL[run], loc="left", fontsize=8.5,
                 color=st.SECONDARY, pad=2)
    st.despine(ax, keep=("bottom",))
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=st.GRID, lw=0.5)
    ax.set_axisbelow(True)

axes[1].set_xlabel("T2 NMSE [%]  (log)\nright-hand label: share of the beyond-affine gap closed at second order")

handles = [
    plt.Line2D([], [], marker="o", ls="none", markersize=5.6, markerfacecolor=AFF_C,
               markeredgecolor="white", label="affine (7 coeff.)"),
    plt.Line2D([], [], marker="s", ls="none", markersize=5.2, markerfacecolor=QUAD_C,
               markeredgecolor="white", label="quadratic (28 coeff.)"),
    plt.Line2D([], [], marker="^", ls="none", markersize=4.6, markerfacecolor="white",
               markeredgecolor=SR_C, label="MSE-SR ms40 (median)"),
    plt.Line2D([], [], marker="v", ls="none", markersize=4.6, markerfacecolor="white",
               markeredgecolor=SR_C, label="MI-SR ms20, calibrated (median)"),
    plt.Line2D([], [], marker="*", ls="none", markersize=7, markerfacecolor=HYB_C,
               markeredgecolor="white", label="OLS + SR-on-residual hybrid (frozen monotone)"),
    plt.Line2D([], [], marker="*", ls="none", markersize=7, markerfacecolor="white",
               markeredgecolor=HYB_C, label="same, free 1-D map (diagnostic)"),
    plt.Line2D([], [], marker="|", ls="none", markersize=7, color=FLOOR_C, mew=1.2,
               label="6-input GBM floor beneath the OLS residual"),
]
axes[0].legend(handles=handles, loc="lower left", bbox_to_anchor=(-0.02, 1.08),
               ncol=2, columnspacing=0.8, handletextpad=0.4, borderaxespad=0.0,
               labelspacing=0.25, fontsize=6.6)

st.save(fig, "F13_1_nonlinearity_ladder")
