"""F5.4 — sensitivity signatures of the canonical primaries (section 5).

Heatmap of the normalised signature shares g_j of each canonical f1 over the
six raw parameters (T1 anchors; rows sum to ~1). This is the object the
answer-agnostic ratio detector reads, and the symbolic side of the section-8
decoder comparison cos(a*, g_j). Companion panel to F2.2 (audit-expected
role vs discovered-form signature). Source: latent_cards_*.json.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt

import figstyle as st

st.apply_rc()

fig, axes = plt.subplots(1, 2, figsize=(st.COL_W, 2.55),
                         gridspec_kw={"wspace": 0.30})
cols = [st.PARAM_TEX_SHORT[p] for p in st.PARAMS]
for ax, run in zip(axes, st.RUNS):
    cards = st.load_cards(run)["cards"]
    M = np.array([c["signature"]["g_j"] for c in cards])
    mesh = st.heatmap(ax, M, [f"$z_{{{c['latent']}}}$" for c in cards], cols,
                      vmax=1.0, fmt="{:.2f}", fontsize=5.4)
    ax.set_title(st.MODEL_LABEL[run], fontsize=8, color=st.SECONDARY, pad=3)

cb = fig.colorbar(mesh, ax=axes, fraction=0.035, pad=0.02)
cb.set_label(r"signature share $g_j(f_1)$", fontsize=7)
cb.ax.tick_params(labelsize=6.5)
cb.outline.set_visible(False)

st.save(fig, "F5_4_signatures")
