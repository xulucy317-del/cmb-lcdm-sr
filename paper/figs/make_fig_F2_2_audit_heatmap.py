"""F2.2 — the raw disentanglement audit: MI(mu_k; theta_j), both checkpoints.

Display recompute of the pre-SR audit (the pipeline's only latent-role
input): pairwise KSG mutual information (sklearn mutual_info_regression,
n_neighbors=4) between each encoder posterior mean and each raw parameter,
on an 8k subsample of T1. Cached to _cache_audit_mi.npz beside this script.
The amplitude columns (tau, lnAs) are boxed: one amplitude-sector latent in
TT, two in TT+EE — the section-9 fingerprint, visible before any SR.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt

import figstyle as st

sys.path.insert(0, str(st.REPO / "src"))
from cmb_lcdm_sr.tiers import T1, split_test_indices  # noqa: E402

st.apply_rc()

CACHE = Path(__file__).resolve().parent / "_cache_audit_mi.npz"
N_SUB, SEED = 8000, 0


def audit_mi():
    if CACHE.exists():
        return dict(np.load(CACHE))
    from sklearn.feature_selection import mutual_info_regression
    theta = np.load(st.REPO / "data" / "theta.npy")
    th_t1 = theta[split_test_indices(st.REPO / "data")][T1]
    rng = np.random.default_rng(SEED)
    sub = rng.choice(th_t1.shape[0], size=N_SUB, replace=False)
    out = {}
    for run in st.RUNS:
        mu = np.load(st.REPO / "models" / run / "analysis"
                     / "encoder_means_test.npy")[T1][sub]
        X = th_t1[sub]
        M = np.zeros((mu.shape[1], 6))
        for k in range(mu.shape[1]):
            M[k] = mutual_info_regression(X, mu[:, k], n_neighbors=4,
                                          random_state=SEED)
            print(run, f"z{k}", np.round(M[k], 2))
        out[run] = M
    np.savez(CACHE, **out)
    return out


mi = audit_mi()
n_tt, n_ee = mi[st.RUNS[0]].shape[0], mi[st.RUNS[1]].shape[0]
vmax = max(float(mi[r].max()) for r in st.RUNS)

fig, axes = plt.subplots(
    1, 2, figsize=(st.COL_W, 2.55),
    gridspec_kw={"width_ratios": [1, 1], "wspace": 0.30})

cols = [st.PARAM_TEX_SHORT[p] for p in st.PARAMS]
for ax, run in zip(axes, st.RUNS):
    M = mi[run]
    mesh = st.heatmap(ax, M, [f"$z_{k}$" for k in range(M.shape[0])], cols,
                      vmax=vmax, fontsize=5.6)
    ax.set_title(st.MODEL_LABEL[run], fontsize=8, color=st.SECONDARY, pad=3)
    # box the amplitude pair columns (tau=3, lnAs=4)
    ax.add_patch(plt.Rectangle((3.03, 0.03), 1.94, M.shape[0] - 0.06,
                               fill=False, edgecolor=st.INK, linewidth=1.0,
                               zorder=5))

cb = fig.colorbar(mesh, ax=axes, fraction=0.035, pad=0.02)
cb.set_label(r"MI$(\mu_k;\theta_j)$ [nat]", fontsize=7)
cb.ax.tick_params(labelsize=6.5)
cb.outline.set_visible(False)

st.save(fig, "F2_2_audit_heatmap")
