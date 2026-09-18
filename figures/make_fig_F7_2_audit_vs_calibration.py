"""F7.2 — the level-set failure IS the calibrated residual (section 7).

x = 1 - R2_cal (stage-1 calibrated account, phase 3); y = E_inv(f1 alone)
(phase 7a). Shaded: the pre-registered predicted band [1-R2, 2(1-R2)].
All 11 latents; points above the factor-2 cap are the deliberately
extreme-separation pairs the audit draws. Source: latent_cards_*.json
(f1_band on the cards is exactly [1-R2, 2(1-R2)]).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt

import figstyle as st

st.apply_rc()

fig, ax = plt.subplots(figsize=(st.COL_W, 2.9))

xs_all, ys_all = [], []
MARK = {"lcdm_tt_beta3e-4": "o", "lcdm_tt_ee_lowl": "s"}
OFFSETS = {  # (run, latent) -> multiplicative label offset, collision fixes
    ("lcdm_tt_ee_lowl", 2): (1.05, 0.80),
    ("lcdm_tt_ee_lowl", 1): (0.88, 1.10),
}
for run in st.RUNS:
    d = st.load_cards(run)
    for c in d["cards"]:
        ls = c["levelset"]
        x = 1.0 - c["residual_stage1"]["r2_cal"]
        y, yse = ls["f1_e_inv"], ls.get("f1_e_inv_se", 0.0)
        xs_all.append(x); ys_all.append(y)
        ax.errorbar(x, y, yerr=yse, fmt="none", ecolor=st.MODEL_COLOR[run],
                    elinewidth=0.8, zorder=3)
        ax.scatter([x], [y], s=26, marker=MARK[run],
                   facecolor=st.MODEL_COLOR[run], edgecolor="white",
                   linewidth=0.6, zorder=4)
        ratio = y / x
        fx, fy = OFFSETS.get((run, c["latent"]), (1.06, 1.11))
        ax.annotate(f"$z_{{{c['latent']}}}$", (x, y), xytext=(x * fx, y * fy),
                    fontsize=6.3, color=st.SECONDARY, zorder=5)
        print(f"{st.MODEL_LABEL[run]:<11s} z{c['latent']}  1-R2={x:.4f}  "
              f"E_inv={y:.3f}  ratio={ratio:.2f}")

ax.set_xscale("log"); ax.set_yscale("log")
lo, hi = min(xs_all) * 0.72, max(xs_all) * 1.55
ax.set_xlim(lo, hi)
ax.set_ylim(min(ys_all) * 0.62, max(ys_all) * 1.6)

xx = np.array([lo, hi])
ax.fill_between(xx, xx, 2 * xx, color=st.NULL_FILL, alpha=0.75, lw=0, zorder=1)
ax.plot(xx, xx, color=st.BASELINE, lw=0.8, zorder=2)
ax.plot(xx, 2 * xx, color=st.BASELINE, lw=0.8, ls=(0, (4, 3)), zorder=2)

# label the band edges along the left side, at the lines' rendered angle
p1 = ax.transData.transform((lo, lo)); p2 = ax.transData.transform((hi, hi))
ang = np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0]))
x0 = lo * 1.25
ax.text(x0, x0 * 1.30, r"$E_{\rm inv}=1-R^2_{\rm cal}$", fontsize=6.6,
        rotation=ang, color=st.SECONDARY, ha="left", va="center",
        rotation_mode="anchor")
ax.text(x0, 2 * x0 * 1.28, r"$\times 2$ cap", fontsize=6.6, rotation=ang,
        color=st.SECONDARY, ha="left", va="center", rotation_mode="anchor")

handles = [
    plt.Line2D([], [], marker=MARK[r], ls="none", markersize=5,
               markerfacecolor=st.MODEL_COLOR[r], markeredgecolor="white",
               label=st.MODEL_LABEL[r]) for r in st.RUNS
]
ax.legend(handles=handles, loc="lower right", handletextpad=0.3,
          borderaxespad=0.2, labelspacing=0.3)

ax.set_xlabel(r"structured residual after calibration,  $1-R^2_{\rm cal}$")
ax.set_ylabel(r"$E_{\rm inv}(f_1$ alone$)$")
st.despine(ax)
ax.grid(True, which="major", color=st.GRID, lw=0.5)
ax.set_axisbelow(True)

st.save(fig, "F7_2_audit_vs_calibration")
