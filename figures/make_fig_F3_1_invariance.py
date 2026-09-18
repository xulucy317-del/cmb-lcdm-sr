"""F3.1 — the shared invariance class and its two corollaries (section 3).

Left: raw parameters in, nothing derived. Middle/right: the inner GMM-MI
loss and the held-out selection metric share one invariance class — any
bijection g of either variable leaves both unchanged (inset: f and two
monotone warps g(f) carry identical MI). The two arrows the report keeps
using: answers are equivalence classes (-> canonical selection, §4);
readable physics is the class invariant (-> the ratio field, §5).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

import figstyle as st

st.apply_rc()

fig, ax = plt.subplots(figsize=(st.COL_W, 2.5))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")


def box(xc, yc, w, h, text, sub=None, fc="#e8effb", tc=None, fs=6.8):
    ax.add_patch(FancyBboxPatch((xc - w / 2, yc - h / 2), w, h,
                 boxstyle="round,pad=0.008,rounding_size=0.012",
                 facecolor=fc, edgecolor="none", mutation_aspect=0.75))
    dy = 0.045 if sub else 0.0
    ax.text(xc, yc + dy, text, ha="center", va="center", fontsize=fs,
            color=tc or st.INK, weight="bold", linespacing=1.25)
    if sub:
        ax.text(xc, yc - 0.052, sub, ha="center", va="center", fontsize=5.6,
                color=st.SECONDARY, linespacing=1.25)


TOP = 0.86
box(0.125, TOP, 0.21, 0.20, "raw $\\theta$ only", "no derived\ncombinations",
    fs=6.4)
box(0.46, TOP, 0.27, 0.20, "search:\nGMM-MI inner loss", None, fs=6.4)
box(0.85, TOP, 0.25, 0.20, "selection:\nheld-out gmm-mi", None, fs=6.4)
for x0, x1 in [(0.235, 0.320), (0.600, 0.720)]:
    ax.annotate("", (x1, TOP), (x0, TOP),
                arrowprops=dict(arrowstyle="-|>", color=st.SECONDARY, lw=0.9))

# the shared class
ax.plot([0.46, 0.46], [0.755, 0.685], color=st.BASELINE, lw=0.8)
ax.plot([0.85, 0.85], [0.755, 0.685], color=st.BASELINE, lw=0.8)
ax.plot([0.46, 0.85], [0.685, 0.685], color=st.BASELINE, lw=0.8)
ax.plot([0.66, 0.66], [0.685, 0.640], color=st.BASELINE, lw=0.8)
box(0.66, 0.545, 0.62, 0.185,
    "one invariance class:  MI$(g(f);\\mu)=$ MI$(f;\\mu)$",
    "for ANY bijection $g$ — rewarded for functional dependence,\n"
    "never for matching the encoder's calibration", fc="#f4f3ef", fs=6.6)

# inset: three monotone warps of the same f -> same MI
axi = fig.add_axes([0.045, 0.40, 0.155, 0.21])
x = np.linspace(0.02, 1, 120)
f = np.log(x * 8 + 1)
for g, lw_, a in [(f, 1.4, 1.0), (f ** 2.4, 1.0, 0.75),
                  (np.tanh(1.6 * f), 1.0, 0.55)]:
    axi.plot(x, (g - g.min()) / (g.max() - g.min()), color="#1c5cab",
             lw=lw_, alpha=a)
axi.set_xticks([]); axi.set_yticks([])
for s in axi.spines.values():
    s.set_color(st.BASELINE); s.set_linewidth(0.6)
axi.set_title("$f,\\;g_1{\\circ}f,\\;g_2{\\circ}f$\nsame MI", fontsize=5.4,
              color=st.SECONDARY, pad=1.5, linespacing=1.2)

# two corollaries
for xc, txt, sub in [
        (0.30, "answers are\nequivalence classes",
         "→ canonical selection\nby semantic recurrence (§4)"),
        (0.72, "readable physics =\nthe class invariant",
         "→ the ratio field\n$(\\partial f/\\partial\\tau)/"
         "(\\partial f/\\partial\\ln A_s)$ (§5)")]:
    ax.annotate("", (xc, 0.30), (0.66 if xc < 0.5 else 0.70, 0.435),
                arrowprops=dict(arrowstyle="-|>", color=st.SECONDARY, lw=0.9))
    box(xc, 0.155, 0.40, 0.27, txt, sub, fc="#ffffff")
    ax.add_patch(FancyBboxPatch((xc - 0.20, 0.155 - 0.135), 0.40, 0.27,
                 boxstyle="round,pad=0.008,rounding_size=0.012",
                 facecolor="none", edgecolor=st.BASELINE, linewidth=0.8,
                 mutation_aspect=0.75))

st.save(fig, "F3_1_invariance")
