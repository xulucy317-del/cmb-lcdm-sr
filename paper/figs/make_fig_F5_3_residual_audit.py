"""F5.3 — every stage-1 residual is structured (section 5).

Left: calibrated-residual audit R2_res per latent (predicting e1 = mu -
h(f1) from raw parameters) against the per-latent permutation null (p97.5
~ +-0.002, an invisible band at zero). Right: the structure itself — the
EE amplitude latent's residual e1 against its leading loading parameter
(T1 subsample) with a binned mean. Sources: latent_cards_*.json;
models/*/analysis/residual_z*_v1.npy + data/theta.npy for the inset.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

import figstyle as st

sys.path.insert(0, str(st.REPO / "src"))
from cmb_lcdm_sr.tiers import T1, split_test_indices  # noqa: E402

st.apply_rc()

fig, (axL, axR) = plt.subplots(
    1, 2, figsize=(st.COL_W, 2.35), gridspec_kw={"width_ratios": [1.35, 1],
                                                 "wspace": 0.42})

# ---------------------------------------------------------------- left panel
xpos, ticks = [], []
x = 0
for run in st.RUNS:
    d = st.load_cards(run)
    nulls = {e["latent"]: e["r2_null_p975"]
             for e in d["controls"]["stage1_permutation"]}
    col = st.MODEL_COLOR[run]
    xs = []
    for c in d["cards"]:
        r2 = c["residual_stage1"]["r2_res"]
        axL.scatter([x], [r2], s=20, facecolor=col, edgecolor="white",
                    linewidth=0.6, zorder=4)
        axL.scatter([x], [nulls[c["latent"]]], s=13, facecolor="white",
                    edgecolor=st.NULL_EDGE, linewidth=0.8, zorder=3)
        xs.append(x)
        ticks.append(f"$z_{{{c['latent']}}}$")
        x += 1
    axL.text(np.mean(xs), 1.075, st.MODEL_LABEL[run], ha="center",
             fontsize=6.8, color=st.SECONDARY)
    x += 0.8
axL.axhline(0.0, color=st.BASELINE, lw=0.6, zorder=1)
axL.set_xticks([i for i in range(5)] + [j + 5.8 for j in range(6)])
axL.set_xticklabels(ticks, fontsize=6.4)
axL.set_ylim(-0.06, 1.13)
axL.set_ylabel(r"residual audit $R^2_{\rm res}$")
axL.annotate("permutation null\n($p_{97.5}\\approx\\pm0.002$)",
             (5.8, 0.0), xytext=(0, 10), textcoords="offset points",
             fontsize=6.0, color=st.SECONDARY, ha="center")
st.despine(axL)
axL.grid(axis="y", color=st.GRID, lw=0.5)
axL.set_axisbelow(True)
axL.tick_params(axis="x", length=0)

# ------------------------------------------------- right panel: the structure
RUN, Z = "lcdm_tt_ee_lowl", 5
theta = np.load(st.REPO / "data" / "theta.npy")
th_t1 = theta[split_test_indices(st.REPO / "data")][T1]
e1 = np.load(st.REPO / "models" / RUN / "analysis"
             / f"residual_z{Z}_v1.npy")
e1_t1 = e1[T1] if e1.shape[0] == 50000 else e1
print("residual shape:", e1.shape)

card = {c["latent"]: c for c in st.load_cards(RUN)["cards"]}[Z]
load_names = card["residual_stage1"]["loadings"]
idx = {p: i for i, p in enumerate(st.PARAMS)}
best_p, best_rho = None, 0.0
for p in load_names:
    rho = abs(spearmanr(th_t1[:, idx[p]], e1_t1).statistic)
    if rho > best_rho:
        best_p, best_rho = p, rho
print("leading loading:", best_p, "|rho| =", round(best_rho, 3))

xv = th_t1[:, idx[best_p]]
rng = np.random.default_rng(0)
sub = rng.choice(len(xv), size=3000, replace=False)
axR.scatter(xv[sub], e1_t1[sub], s=2.0, c=st.MODEL_COLOR[RUN], alpha=0.16,
            linewidths=0, rasterized=True, zorder=2)
bins = np.quantile(xv, np.linspace(0, 1, 25))
ib = np.clip(np.digitize(xv, bins) - 1, 0, 23)
bm = [np.mean(e1_t1[ib == b]) for b in range(24)]
bc = 0.5 * (bins[:-1] + bins[1:])
axR.plot(bc, bm, color=st.INK, lw=1.4, zorder=3)
axR.set_xlabel(st.PARAM_TEX[best_p], labelpad=1)
axR.set_ylabel(rf"$e_1$  (EE $z_{Z}$)", labelpad=1)
axR.set_title(f"the structure, seen\n(binned mean; "
              rf"$|\rho_S|={best_rho:.2f}$)", fontsize=6.8,
              color=st.SECONDARY, pad=2, loc="left")
st.despine(axR)
axR.grid(True, color=st.GRID, lw=0.4)
axR.set_axisbelow(True)
axR.tick_params(labelsize=6.3)

st.save(fig, "F5_3_residual_audit")
