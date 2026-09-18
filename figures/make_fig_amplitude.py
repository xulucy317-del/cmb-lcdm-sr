"""Fig. 1 of the paper: amplitude latent vs. the textbook combination.

Post-hoc illustration only (the derived combination is computed here, in the
figure script, never inside the search pipeline). Points: subsample of T2
(confirmatory tier). x = ln(10^10 A_s) - 2*tau = ln(A_s e^{-2tau}) + const.
y = encoder posterior mean of the amplitude latent (standardised for display).
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

from figstyle import REPO, OUT  # noqa: E402  (repo root derived from this file's location)

sys.path.insert(0, str(REPO / "src"))
from cmb_lcdm_sr.tiers import T2, split_test_indices  # noqa: E402

OUT.mkdir(parents=True, exist_ok=True)

# dataviz palette: categorical slot 1 (light-mode), sequential steps of same hue
BLUE = "#2a78d6"
INK = "#1a1a19"
MUTED = "#5f5e56"

theta = np.load(REPO / "data" / "theta.npy")
test_idx = split_test_indices(REPO / "data")
th_t2 = theta[test_idx[T2]]  # (25000, 6) sampled basis
lnAs = th_t2[:, 4]  # ln 10^10 A_s
tau = th_t2[:, 3]
x = lnAs - 2.0 * tau  # = ln(A_s e^{-2 tau}) + 10 ln 10

rng = np.random.default_rng(0)
sub = rng.choice(len(th_t2), size=4000, replace=False)

panels = [
    ("lcdm_tt_beta3e-4", 2, "TT-only, $z_2$ (degeneracy present)",
     r"top form, 5/5 seeds: $A_s(\tau-0.598)$"),
    ("lcdm_tt_ee_lowl", 5, "TT+EE-lowl, $z_5$ (degeneracy broken)",
     r"top forms: $A_s(\tau-0.579)$; $A_s e^{-2\tau}$ (seed 3)"),
]

fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.85), sharex=True)
for ax, (run, k, title, note) in zip(axes, panels):
    mu = np.load(REPO / "models" / run / "analysis" / "encoder_means_test.npy")
    y = mu[T2, k]
    y = (y - y.mean()) / y.std()
    rho = spearmanr(x, y).statistic
    sgn = -1.0 if rho < 0 else 1.0  # display convention: orient increasing
    ax.scatter(x[sub], sgn * y[sub], s=2.5, c=BLUE, alpha=0.22, linewidths=0,
               rasterized=True)
    ax.set_title(title, fontsize=9, color=INK)
    ax.set_xlabel(r"$\ln(10^{10}A_s) - 2\tau\;=\;\ln(A_s e^{-2\tau}) + \mathrm{const}$",
                  fontsize=9)
    ax.text(0.03, 0.94, rf"$|\rho_S| = {abs(rho):.3f}$", transform=ax.transAxes,
            fontsize=9, va="top", color=INK)
    ax.text(0.03, 0.845, note, transform=ax.transAxes, fontsize=7.5, va="top",
            color=MUTED)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(True, color="#e8e6dc", linewidth=0.6)
    ax.set_axisbelow(True)
axes[0].set_ylabel(r"latent posterior mean $\mu_k$ (standardised)", fontsize=9)

fig.tight_layout(pad=0.4)
fig.savefig(OUT / "amplitude_scatter.pdf", dpi=300)
fig.savefig(OUT / "amplitude_scatter.png", dpi=200)
print("wrote", OUT / "amplitude_scatter.pdf")
