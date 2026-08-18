"""F9.1 — the count fingerprint, before any SR (section 9).

The amplitude columns (tau, lnAs) of the raw disentanglement audit (F2.2),
isolated: ONE latent loads on the pair in TT-only, TWO in TT+EE-lowl (z4
tau-anchored, z5 the combination). Blind and model-level: the audit sees
raw parameters only and runs before any symbolic search. Data: the cached
F2.2 recompute (_cache_audit_mi.npz; run make_fig_F2_2 first).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt

import figstyle as st

st.apply_rc()

CACHE = Path(__file__).resolve().parent / "_cache_audit_mi.npz"
if not CACHE.exists():
    raise SystemExit("run make_fig_F2_2_audit_heatmap.py first (builds cache)")
mi = dict(np.load(CACHE))

fig, axes = plt.subplots(1, 2, figsize=(st.COL_W * 0.72, 2.35),
                         gridspec_kw={"wspace": 0.9})
cols = [st.PARAM_TEX_SHORT["tau"], st.PARAM_TEX_SHORT["A_s"]]
vmax = max(float(mi[r][:, 3:5].max()) for r in st.RUNS)
counts = {}
for ax, run in zip(axes, st.RUNS):
    M = mi[run][:, 3:5]
    mesh = st.heatmap(ax, M, [f"$z_{k}$" for k in range(M.shape[0])], cols,
                      vmax=vmax, fmt="{:.2f}", fontsize=5.6)
    ax.set_box_aspect(M.shape[0] / 2.2)
    ax.set_anchor("N")
    # amplitude-sector rows: pair MI clearly above the off-sector floor
    loaded = np.where(M.sum(axis=1) > 0.15)[0]
    counts[run] = len(loaded)
    for k in loaded:
        ax.add_patch(plt.Rectangle((0.03, k + 0.03), 1.94, 0.94, fill=False,
                                   edgecolor=st.INK, linewidth=1.1, zorder=5))
    ax.set_title(f"{st.MODEL_LABEL[run]}\n{len(loaded)} amplitude latent"
                 + ("s" if len(loaded) != 1 else ""),
                 fontsize=7.5, color=st.INK, pad=3)
print("counts:", counts)

fig.text(0.5, 0.015, "raw-parameter MI audit — before any SR",
         ha="center", fontsize=6.6, color=st.SECONDARY)

st.save(fig, "F9_1_fingerprint")
