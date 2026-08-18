"""F11.2 — R-P4: budget-matched subset advantages and the sham mechanism.

(a) Per latent, the T2 paired contrast M(S+) - M(all-6) at c<=10 with +-SE;
filled = confirmed under the frozen rule (> +1 SE), open = not confirmed;
confirmed rows are annotated with the inputs S+ drops. (b) The sham-input
control: pooled Delta_sham per model (all-6 + one permuted real-theta column
vs all-6), per-latent deltas behind; TT demonstrates dilution at 3 SE, EE is
null; the sham symbol appears in 0.0% of best-at-c<=10 forms in both models.
Sources: experiments/subsets_full_*.json, sham_control_*.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt

import figstyle as st

st.apply_rc()

PARAM_SHORT = {"omega_b": r"\omega_b", "omega_cdm": r"\omega_{cdm}",
               "H0": r"H_0", "tau": r"\tau", "A_s": r"A_s", "n_s": r"n_s"}

rows_a, sham = [], {}
for run in st.RUNS:
    with open(st.EXP / f"subsets_full_{run}.json") as f:
        sf = json.load(f)["latents"]
    cards = {c["latent"]: c for c in st.load_cards(run)["cards"]}
    rows_a.append((run, []))
    for z in sorted(sf, key=lambda s: int(s[1:])):
        l = sf[z]
        t2 = l["t2_confirmation"]
        dropped = [p for p in st.PARAMS if p not in l["s_plus"]]
        rows_a[-1][1].append({
            "tick": st.latent_tick(run, cards[int(z[1:])]),
            "d": t2["mean_diff"], "se": t2["se"], "conf": t2["confirmed"],
            "drops": dropped,
        })
    with open(st.EXP / f"sham_control_{run}.json") as f:
        sh = json.load(f)
    sham[run] = sh

fig = plt.figure(figsize=(st.COL_W, 4.35))
gs = fig.add_gridspec(2, 1, height_ratios=[13, 3.6], hspace=0.42)
axA = fig.add_subplot(gs[0]); axB = fig.add_subplot(gs[1])

# ---------------------------------------------------------------- panel (a)
y = 0
yticks, ylabels = [], []
for run, rows in rows_a:
    axA.text(-0.155, y + 0.45, st.MODEL_LABEL[run], fontsize=8,
             color=st.SECONDARY, va="center", ha="left")
    y -= 1
    for r in rows:
        col = st.MODEL_COLOR[run]
        axA.plot([r["d"] - r["se"], r["d"] + r["se"]], [y, y], color=col,
                 lw=1.0, zorder=3)
        axA.scatter([r["d"]], [y], s=24,
                    facecolor=col if r["conf"] else "white", edgecolor=col,
                    linewidth=1.0, zorder=4)
        if r["conf"]:
            lab = ", ".join(f"${PARAM_SHORT[p]}$" for p in r["drops"])
            axA.annotate("drops " + lab, (r["d"] + r["se"], y),
                         xytext=(4, 0), textcoords="offset points",
                         fontsize=6.4, color=st.SECONDARY, va="center")
        yticks.append(y); ylabels.append(r["tick"])
        y -= 1
    y -= 0.35
axA.axvline(0.0, color=st.INK, lw=0.7, zorder=1)
axA.set_xlim(-0.16, 0.30)
axA.set_ylim(y + 0.7, 0.9)
axA.set_yticks(yticks); axA.set_yticklabels(ylabels)
axA.set_xlabel(r"subset advantage on T2:  $M_{S^+}-M_{\rm all\,6}$"
               r"  at $c\leq10$  [nat]", labelpad=1.5)
st.despine(axA, keep=("bottom",))
axA.tick_params(axis="y", length=0)
axA.grid(axis="x", color=st.GRID, lw=0.5)
axA.set_axisbelow(True)
axA.set_title("(a)  exhaustive 63-support grid, frozen two-stage rule",
              loc="left", fontsize=8, color=st.INK, pad=3)

hA = [
    plt.Line2D([], [], marker="o", ls="none", markersize=5,
               markerfacecolor=st.INK, markeredgecolor=st.INK,
               label=r"confirmed ($>+1$ SE)"),
    plt.Line2D([], [], marker="o", ls="none", markersize=5,
               markerfacecolor="white", markeredgecolor=st.INK,
               label="not confirmed"),
]
axA.legend(handles=hA, loc="upper right", handletextpad=0.3,
           borderaxespad=0.2, labelspacing=0.3, fontsize=6.8)

# ---------------------------------------------------------------- panel (b)
rng = np.random.default_rng(1)
for i, run in enumerate(st.RUNS):
    yc = -i
    col = st.MODEL_COLOR[run]
    pl = sham[run]["per_latent"]
    ds = [v["mean_delta"] for v in pl.values()]
    jit = (rng.random(len(ds)) - 0.5) * 0.30
    axB.scatter(ds, yc + jit, s=9, facecolor="none", edgecolor=st.NULL_EDGE,
                linewidth=0.7, zorder=3)
    p = sham[run]["pooled"]
    axB.plot([p["mean_delta"] - p["se"], p["mean_delta"] + p["se"]],
             [yc, yc], color=col, lw=1.2, zorder=4)
    axB.scatter([p["mean_delta"]], [yc], s=34,
                facecolor=col if p["dilution_demonstrated"] else "white",
                edgecolor=col, linewidth=1.2, zorder=5)
    verdict = ("dilution demonstrated" if p["dilution_demonstrated"]
               else "null")
    axB.text(0.062, yc, f"{st.MODEL_LABEL[run]}: {verdict}", fontsize=6.8,
             color=st.SECONDARY, va="center", ha="left")
axB.axvline(0.0, color=st.INK, lw=0.7, zorder=1)
axB.set_xlim(-0.155, 0.30)
axB.set_ylim(-2.35, 0.75)
axB.set_yticks([])
axB.set_xlabel(r"sham-input control:  $\Delta_{\rm sham}$  [nat]",
               labelpad=1.5)
st.despine(axB, keep=("bottom",))
axB.grid(axis="x", color=st.GRID, lw=0.5)
axB.set_axisbelow(True)
axB.set_title("(b)  all-6 + permuted real-$\\theta$ column (zero information)",
              loc="left", fontsize=8, color=st.INK, pad=3)
axB.text(-0.148, -2.0, "sham symbol in 0.0% of best forms, both models;"
         " open small marks: per-latent means", fontsize=6.4,
         color=st.SECONDARY, va="center")

st.save(fig, "F11_2_rp4_sham")
for run in st.RUNS:
    p = sham[run]["pooled"]
    print(run, "pooled", round(p["mean_delta"], 4), "+-", round(p["se"], 4),
          "demonstrated:", p["dilution_demonstrated"])
