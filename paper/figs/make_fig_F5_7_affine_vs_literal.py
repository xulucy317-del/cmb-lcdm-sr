"""F5.7 — why TT finds the affine form and EE the literal exponential (5.x).

Over the prior tau in [0.01, 0.13], exp(-2 tau) is 99.9% linear (best affine
fit, max deviation 0.52%): A_s(tau - c) ties A_s e^{-2 tau} in MI, so
parsimony deterministically prefers the affine form — and its discovered
constants (0.598 TT / 0.579 EE) sit within 1.5-5% of the Taylor prediction
c = tau-bar + 1/2 = 0.570. Pure function plot; constants from method.md 3e.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt

import figstyle as st

st.apply_rc()

TAU = np.linspace(0.01, 0.13, 400)
f = np.exp(-2 * TAU)
A = np.polyfit(TAU, f, 1)
lin = np.polyval(A, TAU)
dev = np.abs(f - lin) / f
print("max relative deviation:", f"{dev.max():.4%}", " slope:", A[0])

fig, (ax, axd) = plt.subplots(
    2, 1, figsize=(st.COL_W, 2.5), sharex=True,
    gridspec_kw={"height_ratios": [2.6, 1], "hspace": 0.12})

ax.plot(TAU, f, color=st.PARAM_COLOR["tau"], lw=1.8, label=r"$e^{-2\tau}$")
ax.plot(TAU, lin, color=st.INK, lw=0.9, ls=(0, (4, 3)),
        label="best affine fit")
ax.annotate(r"$e^{-2\tau}$", (TAU[60], f[60]), xytext=(0, 7),
            textcoords="offset points", fontsize=7, color="#b57b00")
ax.annotate("affine", (TAU[300], lin[300]), xytext=(2, -11),
            textcoords="offset points", fontsize=7, color=st.INK)
ax.set_ylabel(r"$e^{-2\tau}$", labelpad=1)
tbl = ("discovered constants vs Taylor\n"
       "$c=\\bar\\tau+1/2\\approx0.570$:\n"
       r"TT $A_s(\tau-0.598)$ · EE $A_s(\tau-0.579)$" "\n"
       r"EE seed 3: literal $A_s e^{-2\tau}$")
ax.text(0.02, 0.05, tbl, transform=ax.transAxes, fontsize=6.0,
        color=st.SECONDARY, va="bottom", linespacing=1.4)
st.despine(ax)
ax.grid(True, color=st.GRID, lw=0.4)
ax.set_axisbelow(True)

axd.plot(TAU, 100 * dev, color=st.SECONDARY, lw=1.0)
axd.set_ylabel("dev. [%]", fontsize=6.5, labelpad=1)
axd.set_ylim(0, 0.6)
axd.text(0.5, 0.94, f"max {dev.max():.2%} — the two forms tie in MI; "
         "parsimony picks affine", transform=axd.transAxes, fontsize=6.0,
         ha="center", va="top", color=st.SECONDARY)
axd.set_xlabel(r"$\tau$  (prior range)", labelpad=1.5)
st.despine(axd)
axd.grid(True, color=st.GRID, lw=0.4)
axd.set_axisbelow(True)

st.save(fig, "F5_7_affine_vs_literal")
