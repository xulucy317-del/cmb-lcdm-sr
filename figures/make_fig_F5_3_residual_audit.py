"""F5.3 — the stage-1 residual's structure, seen (section 5).

The EE amplitude latent's residual e1 = mu - h(f1) against its leading
loading parameter (T1 subsample) with a binned mean overlaid: the residual
is not noise, and the report says so with a picture rather than only a
score. Sources: latent_cards_*.json for the loading list;
models/<run>/analysis/residual_z<k>_v1.npy + data/theta.npy for the rows.

The companion R2_res-vs-permutation-null panel was dropped (2026-08-19);
those numbers are tabulated in the section text instead.

NOTE: needs models/*/analysis/, which lives on CSD3 and is not part of a
local checkout. Run this where the caches are (or sync them first).
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

fig, axR = plt.subplots(1, 1, figsize=(0.52 * st.COL_W, 2.35))

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

st.save(fig, "F5_3_residual_structure")
