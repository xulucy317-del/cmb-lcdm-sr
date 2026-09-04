"""F14.1 — encoder-side attribution (conclusive report, stage 4).

(a) Fraction of each latent's on-manifold (template-projected) input-gradient
    mass that falls in the EE reionization window, ell in [2, 30), for the
    TT+EE model; the TT model has no bins below ell = 30 and is structurally
    zero there. Source: experiments/encoder_gradient_attribution_<run>.json.
(b) Layer-wise linear decodability (held-out ridge-probe R^2) of tau, lnA_s
    and the degenerate combination lnA_s - 2tau, from the standardised input
    through the three conv blocks to the posterior mean, for both models.
    Source: experiments/encoder_trunk_probe_<run>.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt

import figstyle as st

st.apply_rc()

LAYERS = ["input", "block1", "block2", "block3", "mu"]
LAYER_LAB = ["in", "c1", "c2", "c3", r"$\mu$"]
TARGETS = [
    ("ln10As_minus_2tau", r"$\ln A_s - 2\tau$", st.INK, "o"),
    ("ln10As", r"$\ln A_s$", st.PARAM_COLOR["A_s"], "s"),
    ("tau", r"$\tau$", st.PARAM_COLOR["tau"], "D"),
]

grad, probe = {}, {}
for run in st.RUNS:
    with open(st.EXP / f"encoder_gradient_attribution_{run}.json") as f:
        grad[run] = json.load(f)
    with open(st.EXP / f"encoder_trunk_probe_{run}.json") as f:
        probe[run] = json.load(f)

fig = plt.figure(figsize=(st.FULL_W, 2.55))
gs = fig.add_gridspec(1, 3, width_ratios=[1.25, 1, 1], wspace=0.38)
axA = fig.add_subplot(gs[0, 0])
axB = [fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[0, 2])]

# ---------------------------------------------------------------- (a) bands
ee_run = "lcdm_tt_ee_lowl"
cards = st.load_cards(ee_run)["cards"]
ticks, vals, onman = [], [], []
for c in cards:
    z = f"z{c['latent']}"
    g = grad[ee_run]["latents"][z]
    ticks.append(st.latent_tick(ee_run, c))
    vals.append(100 * g["bands_projected"]["ee"]["2-29"])
    onman.append(g["on_manifold_frac"])
uniform = 100 * 28 / 4970  # the 28 bins are 0.56% of the 4,970 the model sees
print("TT+EE-lowl: projected-gradient mass in EE ell<30 [%]")
for t, v, o in zip(ticks, vals, onman):
    print(f"  {t:<24s} {v:6.2f}%   on-manifold frac {o:.4f}")
tt_zero = all(
    grad["lcdm_tt_beta3e-4"]["latents"][f"z{k}"]["bands_projected"]["tt"]["2-29"] == 0.0
    for k in range(5))
print("TT-only: all latents exactly 0 at ell<30:", tt_zero)

ys = np.arange(len(ticks))[::-1]
axA.barh(ys, vals, height=0.62, color=st.MODEL_COLOR[ee_run], zorder=3)
axA.axvline(uniform, color=st.NULL_EDGE, lw=0.8, ls=(0, (3, 2)), zorder=2)
axA.text(uniform + 0.6, -0.62, "uniform share of bins (0.56%)", fontsize=6.2,
         color=st.SECONDARY, va="center", ha="left")
for y, v in zip(ys, vals):
    axA.text(v + 0.5, y, f"{v:.1f}%", fontsize=6.6, va="center", ha="left",
             color=st.INK)
axA.set_yticks(ys)
axA.set_yticklabels(ticks)
axA.set_xlim(0, 32)
axA.set_ylim(-0.95, len(ticks) - 0.35)
axA.set_xlabel(r"(a)  on-manifold gradient mass at $\ell<30$ (EE) [%]")
axA.set_title("TT+EE-lowl   (TT-only: all 0)",
              loc="left", fontsize=8.5, color=st.SECONDARY, pad=3)
st.despine(axA, keep=("bottom",))
axA.tick_params(axis="y", length=0)
axA.grid(axis="x", color=st.GRID, lw=0.5)
axA.set_axisbelow(True)

# ---------------------------------------------------------------- (b) trunk
def spread(vals, gap):
    """Label positions with a minimum vertical separation, order preserved."""
    order = np.argsort(vals)
    pos = np.array(vals, dtype=float)
    for a, b in zip(order[:-1], order[1:]):
        if pos[b] - pos[a] < gap:
            pos[b] = pos[a] + gap
    return pos


x = np.arange(len(LAYERS))
for ax, run in zip(axB, st.RUNS):
    r2 = probe[run]["r2"]
    ends = [r2[key][LAYERS[-1]] for key, *_ in TARGETS]
    label_y = spread(ends, 0.04)
    for (key, lab, col, mk), ly in zip(TARGETS, label_y):
        v = [r2[key][l] for l in LAYERS]
        ax.plot(x, v, color=col, lw=1.4, marker=mk, markersize=4.2,
                markeredgecolor="white", markeredgewidth=0.5, label=lab, zorder=3)
        ax.text(x[-1] + 0.14, ly, f"{v[-1]:.2f}", fontsize=6.2, color=col,
                va="center", ha="left")
        print(f"{run} {key:>18s}: " + "  ".join(f"{t:.4f}" for t in v))
    ax.set_xticks(x)
    ax.set_xticklabels(LAYER_LAB)
    ax.set_xlim(-0.3, len(LAYERS) + 0.2)
    ax.set_ylim(0.3, 1.09)
    ax.set_title(st.MODEL_LABEL[run], loc="left", fontsize=8.5,
                 color=st.SECONDARY, pad=3)
    st.despine(ax, keep=("left", "bottom"))
    ax.grid(axis="y", color=st.GRID, lw=0.5)
    ax.set_axisbelow(True)
axB[0].set_ylabel(r"held-out probe $R^2$")
axB[1].tick_params(axis="y", labelleft=False)
axB[0].legend(loc="lower left", handlelength=1.6, handletextpad=0.5,
              labelspacing=0.25, fontsize=6.8)
fig.text(0.72, -0.04, "(b)  linear decodability: input → conv blocks → posterior mean",
         ha="center", va="top", fontsize=8)

st.save(fig, "F14_1_encoder_attribution")
