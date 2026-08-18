"""F4.2 — top-front MI is a capacity dial; the budget-matched readout is flat.

hp_v1 sweep, amplitude latent, 12 configs x 3 seeds x both models.
(a) top-front validation MI vs config — every capacity knob moves it
(maxsize alone: ~1.6 -> ~4.1 nat). (b) budget-matched MI@c<=10 — flat at
~1.89 (TT) / ~2.02 (EE) across every knob, EXCEPT the ms10 search itself:
its own front is worse at c<=10 than the sliced ms20 front. Complexity is a
report-time slice, not a search-time budget. Source: hpsweep_hp_v1_*.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt

import figstyle as st

st.apply_rc()

ORDER = ["baseline", "ni100", "ni400", "pop8", "pop31", "ms10", "ms15",
         "ms30", "ps54", "ps108", "ncyc190", "ncyc760"]
SEPS = [0.5, 2.5, 4.5, 7.5, 9.5]   # knob-group separators
MS10_X = ORDER.index("ms10")

data = {}
for run in st.RUNS:
    with open(st.EXP / f"hpsweep_hp_v1_{run}.json") as f:
        hp = json.load(f)
    per = {}
    for c in hp["configs"]:
        z = list(c["latents"].values())[0]
        per[c["label"]] = {
            "top": [s["top_mi"] for s in z["per_seed"]],
            "cap": [s["mi_cap"] for s in z["per_seed"]],
        }
    data[run] = per
    print(run, "baseline cap mean:", round(np.mean(per["baseline"]["cap"]), 3))

fig, axes = plt.subplots(2, 1, figsize=(st.COL_W, 3.5), sharex=True,
                         gridspec_kw={"hspace": 0.10})
OFF = {st.RUNS[0]: -0.18, st.RUNS[1]: +0.18}
rng = np.random.default_rng(3)

for ax, key, ylab in [(axes[0], "top", "top-front val MI"),
                      (axes[1], "cap", r"MI @ $c\leq10$")]:
    for run in st.RUNS:
        col = st.MODEL_COLOR[run]
        for i, lab in enumerate(ORDER):
            vals = data[run][lab][key]
            xj = i + OFF[run] + (rng.random(len(vals)) - 0.5) * 0.10
            ax.scatter(xj, vals, s=7, facecolor="none", edgecolor=col,
                       linewidth=0.7, alpha=0.75, zorder=3)
            ax.plot([i + OFF[run] - 0.14, i + OFF[run] + 0.14],
                    [np.mean(vals)] * 2, color=col, lw=1.6, zorder=4,
                    solid_capstyle="round")
        if key == "cap":
            base = np.mean(data[run]["baseline"]["cap"])
            ax.axhline(base, color=col, lw=0.6, ls=(0, (4, 3)), alpha=0.65,
                       zorder=1)
    ax.axvspan(MS10_X - 0.5, MS10_X + 0.5, color=st.NULL_FILL, alpha=0.55,
               lw=0, zorder=0)
    for xs in SEPS:
        ax.axvline(xs, color=st.GRID, lw=0.6, zorder=0)
    ax.set_ylabel(ylab + " [nat]")
    st.despine(ax, keep=("left", "bottom"))
    ax.set_axisbelow(True)

axes[0].set_title("(a)  capacity dial", loc="left", fontsize=8, pad=3)
axes[1].set_title("(b)  budget-matched readout: flat — except the ms10 "
                  "search itself", loc="left", fontsize=8, pad=3)
axes[1].set_xticks(range(len(ORDER)))
axes[1].set_xticklabels(ORDER, rotation=45, ha="right", fontsize=6.6)
axes[1].set_xlim(-0.65, len(ORDER) - 0.35)
axes[1].annotate("searching small loses\nto slicing big",
                 (MS10_X, 1.52), xytext=(MS10_X + 1.6, 1.50), fontsize=6.4,
                 color=st.SECONDARY, va="center",
                 arrowprops=dict(arrowstyle="-", color=st.MUTED, lw=0.6))

handles = [plt.Line2D([], [], marker="o", ls="none", markersize=4,
                      markerfacecolor="none", markeredgecolor=st.MODEL_COLOR[r],
                      label=st.MODEL_LABEL[r]) for r in st.RUNS]
axes[0].legend(handles=handles, loc="lower right", fontsize=6.8,
               handletextpad=0.2, borderaxespad=0.2, labelspacing=0.25)

st.save(fig, "F4_2_capacity_dial")
