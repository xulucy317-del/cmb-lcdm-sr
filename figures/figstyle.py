"""Shared style for all report figures (one make_fig_* script per figure ID).

Palette = the dataviz reference instance, used verbatim (same hexes, same
slot order — its adjacent-pair CVD validation is documented in the skill's
palette.md; no re-stepping here). Print surface is white; the sub-3:1
slots (aqua/yellow/magenta) therefore always appear WITH direct text labels
(the relief rule), never as color-alone identity.

Fixed color assignments (color follows the entity, across every figure):
  parameters  -> categorical slots 1..6 in theta order
  checkpoints -> slots 7 (TT-only, violet) and 8 (TT+EE-lowl, red)
  eta ladder  -> ordinal steps of the sequential blue ramp (250/400/550/700)
  statuses    -> status palette (never reused for series)
  nulls       -> neutral grays, drawn in-panel as bands/hollow marks
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# Repo root: derived from this file's location (<repo>/figures/figstyle.py) so
# the scripts run unchanged on CSD3 and on a local checkout. CMB_LCDM_SR_REPO
# overrides if the figures ever need to read a different tree.
import os

REPO = Path(os.environ.get("CMB_LCDM_SR_REPO",
                           Path(__file__).resolve().parents[1]))
EXP = REPO / "experiments"
OUT = REPO / "figures"

# ---------------------------------------------------------------- ink & chrome
INK = "#0b0b0b"
SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e8e6dc"
BASELINE = "#c3c2b7"
NULL_FILL = "#e1e0d9"   # shaded null/control bands
NULL_EDGE = "#898781"   # null marks / band edges

# ------------------------------------------------- categorical: the 6 parameters
# theta order: omega_b, omega_cdm, H0, tau, ln10^10 A_s, n_s  (slots 1..6)
PARAMS = ["omega_b", "omega_cdm", "H0", "tau", "A_s", "n_s"]
PARAM_COLOR = {
    "omega_b": "#2a78d6",   # blue
    "omega_cdm": "#eb6834", # orange
    "H0": "#1baf7a",        # aqua
    "tau": "#eda100",       # yellow
    "A_s": "#e87ba4",       # magenta
    "n_s": "#008300",       # green
}
PARAM_TEX = {
    "omega_b": r"$\omega_b$",
    "omega_cdm": r"$\omega_{cdm}$",
    "H0": r"$H_0$",
    "tau": r"$\tau$",
    "A_s": r"$\ln 10^{10}A_s$",
    "n_s": r"$n_s$",
}
PARAM_TEX_SHORT = {  # for tight tick labels
    "omega_b": r"$\omega_b$",
    "omega_cdm": r"$\omega_c$",
    "H0": r"$H_0$",
    "tau": r"$\tau$",
    "A_s": r"$A_s$",
    "n_s": r"$n_s$",
}

# ----------------------------------------------------- checkpoints (slots 7, 8)
RUNS = ["lcdm_tt_beta3e-4", "lcdm_tt_ee_lowl"]
MODEL_LABEL = {"lcdm_tt_beta3e-4": "TT-only", "lcdm_tt_ee_lowl": "TT+EE-lowl"}
MODEL_COLOR = {"lcdm_tt_beta3e-4": "#4a3aa7", "lcdm_tt_ee_lowl": "#e34948"}

# ------------------------------------- eta ladder (ordinal blue, light->dark)
ETA_S = "#86b6ef"        # step 250: saturates its own support
ETA_PLAT = "#3987e5"     # step 400: fraction of the searchable map
ETA_POST_F1 = "#1c5cab"  # step 550: fraction of what the latent stores, f1
ETA_POST_COMB = "#0d366b"  # step 700: same, f1+f2

# ------------------------------------------------------------- status (fixed)
STATUS = {"interpreted": "#0ca30c", "attention": "#fab219", "unresolved": "#ec835a"}

FULL_W = 7.05   # \textwidth figure (in)
COL_W = 3.35    # \columnwidth figure (in)


def apply_rc():
    plt.rcParams.update({
        "font.size": 8,
        "axes.titlesize": 9,
        "axes.labelsize": 8,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
        "legend.fontsize": 7.5,
        "axes.edgecolor": MUTED,
        "axes.labelcolor": INK,
        "axes.linewidth": 0.7,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelcolor": SECONDARY,
        "ytick.labelcolor": SECONDARY,
        "text.color": INK,
        "axes.grid": False,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "legend.frameon": False,
        "pdf.fonttype": 42,
        "figure.dpi": 110,
    })


def despine(ax, keep=("left", "bottom")):
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(s in keep)


def save(fig, stem):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{stem}.pdf", dpi=300, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(OUT / f"{stem}.png", dpi=200, bbox_inches="tight", pad_inches=0.02)
    print("wrote", OUT / f"{stem}.pdf")


def load_cards(run):
    import json
    with open(EXP / f"latent_cards_{run}.json") as f:
        return json.load(f)


ROLE_SHORT = {  # audit-expected role -> compact display
    "omega_b": r"$\omega_b$",
    "omega_cdm": r"$\omega_{cdm}$",
    "omega_cdm envelope / early-ISW": r"$\omega_{cdm}$/ISW",
    "H0": r"$H_0$",
    "tau": r"$\tau$",
    "n_s": r"$n_s$",
    "amplitude": "amp",
    "amplitude (A_s, tau)": "amp",
    "tau (amplitude sector)": r"$\tau$ (amp)",
}


def latent_tick(run, card):
    """'z2 amp' style tick label for per-latent axes (card order)."""
    role = card.get("role", "")
    disp = ROLE_SHORT.get(role, role)
    return f"$z_{{{card['latent']}}}$ {disp}"


# ------------------------------------------------- sequential ramp + heatmaps
SEQ_BLUE = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7",
            "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281",
            "#0d366b"]


def seq_cmap():
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list("seq_blue", SEQ_BLUE)


def heatmap(ax, M, row_labels, col_labels, vmax=None, fmt="{:.1f}",
            cmap=None, fontsize=6.2):
    """Sequential heatmap with 2px white cell gaps and in-cell value labels
    (text flips to white on dark cells). Returns the mesh for a colorbar."""
    import numpy as np
    cmap = cmap or seq_cmap()
    vmax = vmax if vmax is not None else float(np.nanmax(M))
    n, m = M.shape
    mesh = ax.pcolormesh(M, cmap=cmap, vmin=0.0, vmax=vmax,
                         edgecolors="white", linewidth=1.4)
    for i in range(n):
        for j in range(m):
            v = M[i, j]
            frac = v / vmax if vmax else 0.0
            ax.text(j + 0.5, i + 0.5, fmt.format(v), ha="center",
                    va="center", fontsize=fontsize,
                    color="white" if frac > 0.55 else INK)
    ax.set_xticks(np.arange(m) + 0.5)
    ax.set_xticklabels(col_labels, fontsize=7)
    ax.set_yticks(np.arange(n) + 0.5)
    ax.set_yticklabels(row_labels, fontsize=7)
    ax.invert_yaxis()  # z0 on top
    ax.tick_params(length=0)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    return mesh
