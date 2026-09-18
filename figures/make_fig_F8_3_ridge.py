"""F8.3 — why the decoder yields no fourth -2 readout (section 8).

All geometry lives in the model's own design space: templates divided by the
per-ell scaler sigma (T_norm = T_phys / sigma), exactly as in
scripts/decoder_effect.py. (a) Normalised t_tau overlaid on -t_lnAs for the
TT channel (cos -0.9996) and the EE channel (cos -0.977) — near-antiparallel
even in the degeneracy-breaking channel. (b, c) The fitted amplitude split of
each model's amplitude latent in natural units b_j = a_j/h_j (so r_dec =
b_tau/b_lnAs): the four frozen fit variants slide along the design's flat
(ridge) direction at ~no change in R2_W; the r_dec = -2 ray is the reference
the gate wanted. TT lands at +0.35; EE spans -1.67..-2.32.
Sources: data/spectral_templates_v1.npz, models/*/scaler.npz,
experiments/decoder_effect_*.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt

import figstyle as st

sys.path.insert(0, str(st.REPO / "src"))
from cmb_lcdm_sr.scaler import ShardedScaler  # noqa: E402

st.apply_rc()

T = np.load(st.REPO / "data" / "spectral_templates_v1.npz")
half = {str(n): float(h) for n, h in zip(T["theta_order"], T["half"])}
h_tau, h_lnas = half["tau_reio"], half["ln10^{10}A_s"]
i_tau, i_lnas = 3, 4

def ucos(a, b):
    return float(a @ b / np.sqrt((a @ a) * (b @ b)))

# per-run design: concat channels, templates / scaler sigma
design = {}
for run in st.RUNS:
    sc = ShardedScaler.load(st.REPO / "models" / run / "scaler.npz")
    blocks, sig_blocks = [], []
    for ch in sc.channels:
        sig = sc.channel_stats(ch)[1]
        blocks.append(T[f"templates_{ch}"] / sig)
        sig_blocks.append((ch, T[f"ell_{ch}"], T[f"templates_{ch}"] / sig))
    Tn = np.concatenate(blocks, axis=1)
    design[run] = (Tn, sig_blocks)
    print(run, "channels", sc.channels,
          "concat cos", round(ucos(Tn[i_tau], Tn[i_lnas]), 4))

AMP = {"lcdm_tt_beta3e-4": 2, "lcdm_tt_ee_lowl": 5}
VARIANTS = [("a_ols", "r_dec", "OLS"), ("a_weighted", "r_dec_weighted",
            r"$(2\ell{+}1)$-wt"), ("a_hcheck", "r_dec_hcheck", "h/2"),
            ("a_anchor", "r_dec_anchor", "anchor")]

ridge = {}
for run in st.RUNS:
    with open(st.EXP / f"decoder_effect_{run}.json") as f:
        d = json.load(f)
    lat = d["latents"]
    if isinstance(lat, dict):
        lz = lat[str(AMP[run])]
    else:
        lz = next(l for l in lat if l["latent"] == AMP[run])
    pts = []
    for akey, rkey, lab in VARIANTS:
        a = lz[akey]
        pts.append(((a[i_tau] / h_tau, a[i_lnas] / h_lnas), lz.get(rkey), lab))
        print(run, lab, "b=", np.round(pts[-1][0], 2), "r_dec=", lz.get(rkey))
    Tn = design[run][0]
    cols = np.stack([h_tau * Tn[i_tau], h_lnas * Tn[i_lnas]], axis=1)
    w, v = np.linalg.eigh(cols.T @ cols)
    ridge[run] = (pts, v[:, 0], d["template_identifiability"])

LABEL_OFF = {  # (run, variant) -> (dx pt, dy pt, ha): hand-set, no collisions
    ("lcdm_tt_beta3e-4", "OLS"): (3, -10, "left"),
    ("lcdm_tt_beta3e-4", r"$(2\ell{+}1)$-wt"): (4, 5, "left"),
    ("lcdm_tt_beta3e-4", "h/2"): (5, -5, "left"),
    ("lcdm_tt_beta3e-4", "anchor"): (2, -11, "center"),
    ("lcdm_tt_ee_lowl", "OLS"): (5, -8, "left"),
    ("lcdm_tt_ee_lowl", r"$(2\ell{+}1)$-wt"): (2, 7, "left"),
    ("lcdm_tt_ee_lowl", "h/2"): (6, -1, "left"),
    ("lcdm_tt_ee_lowl", "anchor"): (-4, -10, "right"),
}

fig = plt.figure(figsize=(st.FULL_W, 2.6))
gs = fig.add_gridspec(2, 3, width_ratios=[1.3, 1, 1], hspace=0.14,
                      wspace=0.44)

# ------------------------------------------------- (a) template collinearity
tt_run, ee_run = st.RUNS
rows_a = [
    ("TT channel", dict(design[tt_run][1])["tt"] if False else None),
]
# assemble: row 1 = TT channel of the TT-only design; row 2 = EE channel
blk_tt = [b for b in design[tt_run][1] if b[0] == "tt"][0]
blk_ee = [b for b in design[ee_run][1] if b[0] == "ee"][0]
for row, (name, (ch, ell, Tn_ch)) in enumerate(
        [("TT channel", blk_tt), ("EE channel", blk_ee)]):
    ax = fig.add_subplot(gs[row, 0])
    ta, ln = Tn_ch[i_tau], Tn_ch[i_lnas]
    cs = ucos(ta, ln)
    yt = ta / np.linalg.norm(ta)
    yl = -ln / np.linalg.norm(ln)
    ax.plot(ell, yt, color=st.PARAM_COLOR["tau"], lw=1.6)
    ax.plot(ell, yl, color=st.PARAM_COLOR["A_s"], lw=1.0, ls=(0, (5, 2)))
    ax.text(0.98, 0.05, f"{name}:  cos $= {cs:.4f}$", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=6.8, color=st.SECONDARY)
    # direct labels at the curves' left ends (relief rule for the yellow)
    ax.annotate(r"$t_\tau$", (ell[0], yt[0]), xytext=(2, 5),
                textcoords="offset points", fontsize=7,
                color="#b57b00", ha="left")
    ax.annotate(r"$-t_{\ln A_s}$", (ell[0], yl[0]), xytext=(2, -9),
                textcoords="offset points", fontsize=7,
                color="#c94f7c", ha="left")
    ax.set_xscale("log")
    ax.set_yticks([])
    pad_y = 0.18 * (max(yt.max(), yl.max()) - min(yt.min(), yl.min()))
    ax.set_ylim(min(yt.min(), yl.min()) - pad_y, max(yt.max(), yl.max()) + pad_y)
    st.despine(ax, keep=("bottom",))
    ax.grid(axis="x", color=st.GRID, lw=0.5)
    ax.set_axisbelow(True)
    if row == 0:
        ax.tick_params(labelbottom=False)
        ax.set_title(r"(a)  templates in design space ($-t_{\ln A_s}$ flipped)",
                     loc="left", fontsize=8, color=st.INK, pad=3)
    else:
        ax.set_xlabel(r"$\ell$", labelpad=1)

# ------------------------------------------- (b, c) the ridge, per model
for col, run in enumerate(st.RUNS, start=1):
    pts, flat, ident = ridge[run]
    ax = fig.add_subplot(gs[:, col])
    P = np.array([p[0] for p in pts])
    ctr = P.mean(axis=0)
    span = max(3.2, 1.45 * np.abs(P - ctr).max())
    tline = np.linspace(-2.6 * span, 2.6 * span, 2)
    ax.plot(ctr[0] + tline * flat[0], ctr[1] + tline * flat[1],
            color=st.NULL_EDGE, lw=2.4, alpha=0.4, zorder=1,
            solid_capstyle="round")
    xx = np.array([-2.9 * span + ctr[0], 2.9 * span + ctr[0]])
    ax.plot(xx, -xx / 2.0, color=st.INK, lw=0.7, ls=(0, (4, 3)), zorder=2)
    ax.axhline(0, color=st.BASELINE, lw=0.5, zorder=0)
    ax.axvline(0, color=st.BASELINE, lw=0.5, zorder=0)
    mcol = st.MODEL_COLOR[run]
    for (b, r, lab), mk in zip(pts, ["o", "s", "D", "^"]):
        ax.scatter([b[0]], [b[1]], s=26, marker=mk, facecolor=mcol,
                   edgecolor="white", linewidth=0.6, zorder=4)
        rtxt = "n/a" if r is None else f"{r:+.2f}"
        dx, dy, ha = LABEL_OFF[(run, lab)]
        ax.annotate(f"{lab}: {rtxt}", b, xytext=(dx, dy),
                    textcoords="offset points", fontsize=6.0, ha=ha,
                    color=st.SECONDARY, zorder=5)
    ax.set_xlim(ctr[0] - span, ctr[0] + span)
    ax.set_ylim(ctr[1] - span, ctr[1] + span)
    ax.set_aspect("equal")
    key = "tt" if run == tt_run else "concat"
    ax.set_title(f"({'bc'[col-1]})  {st.MODEL_LABEL[run]} "
                 f"$z_{AMP[run]}$ — cond {ident[key]['cond']:.1f}",
                 loc="left", fontsize=8, color=st.INK, pad=3)
    ax.set_xlabel(r"$b_\tau = a_\tau/h_\tau$", labelpad=1)
    ax.set_ylabel(r"$b_{\ln A_s}$", labelpad=0.5)
    st.despine(ax)
    ax.grid(True, color=st.GRID, lw=0.4)
    ax.set_axisbelow(True)
    # label the -2 ray where it is clear of the point cloud
    xr = ctr[0] + (0.62 if run == tt_run else -0.55) * span
    ax.annotate(r"$r_{\rm dec}=-2$", (xr, -xr / 2), fontsize=6.2,
                color=st.INK, xytext=(0, 6 if run == tt_run else -10),
                textcoords="offset points", ha="center")
    # label the ridge near the panel edge, on the line
    t_lab = 0.80 * span * (1 if run == tt_run else -1)
    ax.annotate("ridge", (ctr[0] + t_lab * flat[0], ctr[1] + t_lab * flat[1]),
                fontsize=6.4, color=st.NULL_EDGE, ha="center",
                xytext=(0, 8), textcoords="offset points")

st.save(fig, "F8_3_ridge")
