#!/usr/bin/env python
"""Decoder-effect triangulation — Phase 7b of docs/discovery_roadmap.md
(the observable-domain half of gate G4).

What does latent k *do* to the spectrum? Autograd through the stored
decoder gives, per channel and per multipole,

    d_k(ell) = d Decoder(z)_ell / d z_k       (JVP along e_k),

evaluated at the T1 mean latent z-bar (anchor) and across a latent spread
(64 T1 posterior-mean rows, deterministic draw); the spread mean/std is the
reported curve/band. The decoder outputs per-ell *standardised* log-ratio
space; multiplying by the stored per-ell sigma (scaler.npz) converts to the
physical effect d log10 D_ell / d z_k.

Each d_k is then decomposed against the data-driven parameter templates
t_j(ell) = d log10 D_ell / d u_j (scripts/spectral_templates.py):

    d_k(ell) ~ sum_j a_kj t_j(ell)

by least squares in normalised space (W = identity; no intercept — a
constant log-offset IS a physical mode), with a lasso support scan
(unit-norm columns, 5-fold CV, fixed seed) and three frozen sensitivity
refits: (2 ell + 1)-weighted in physical space, halved-bandwidth templates,
and the anchor-point curve. a_kj is "moving one unit of z_k looks like
moving a_kj units of u_j"; in the isotropic prior box the implied raw-space
gradient ratio for the amplitude pair is

    r_dec = (a_tau / half_tau) / (a_lnAs / half_lnAs)

— the third, fully decoder-side readout of the -2 exponent (after the
discovered forms and the Phase-3 derivative ratio). Triangulation column:
cosine between |a_k| and the Phase-3 symbolic signature g_j(f*_k).

**Gate G4b** (amplitude latent; frozen before looking at any output):
amplitude-sector mass (|a_tau| + |a_lnAs|) / sum_j |a_j| >= 0.8, AND
|r_dec + 2| <= 0.3, AND decomposition R^2_W >= 0.8. The combined gate G4
report also restates the Phase-7a G4a verdict alongside.

Human-readable labels for shape latents are assigned only AFTER looking at
the derived curves (the .md carries the numbers and the figure; labels go
on the Phase-10 cards, next to — never instead of — the decomposition).

Reads:  models/<run>/{best_model.pt, scaler.npz, analysis/encoder_means_test.npy},
        data/spectral_templates_v1.npz,
        experiments/sufficiency_audit_<run>.json   (g_j triangulation),
        experiments/levelset_audit_<run>.json      (G4a restatement, optional)
Writes: experiments/decoder_effect_<run>.{md,json},
        experiments/decoder_effect_<run>_curves.{png,npz}

    python scripts/decoder_effect.py --run lcdm_tt_beta3e-4
"""
import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "4")

import _bootstrap  # noqa: F401,E402

import numpy as np  # noqa: E402

from consolidate_allparams import AUDIT_EXPECTED, MODELS  # noqa: E402

from cmb_lcdm_sr import tiers  # noqa: E402

SEED_BASE = 20260805
N_SPREAD = 64
I_TAU, I_AS = 3, 4          # THETA_ORDER positions of tau_reio, ln10^{10}A_s

# Frozen G4b rule (declared before any output was looked at):
G4B_AMP_MASS_MIN = 0.8
G4B_RATIO_TOL = 0.3
G4B_R2_MIN = 0.8


def _f(v):
    return float(v) if v is not None and np.isfinite(v) else None


def fmt(x, prec=3):
    return "n/a" if x is None else f"{x:.{prec}f}"


# ---- decoder Jacobian columns ------------------------------------------------

def decoder_columns(model, channels: list[str], z_pts: np.ndarray) -> np.ndarray:
    """d decode(z)/d z_k for every k at every z row, in normalised space.

    Returns (L_lat, P, sum_ch L_ch): JVP along each latent axis, channels
    concatenated in scaler order (matches the dual decoder's dict keys).
    """
    import torch
    from torch.autograd.functional import jvp

    def fn(z):
        out = model.decode(z)
        if isinstance(out, dict):
            return torch.cat([out[ch].reshape(z.shape[0], -1)
                              for ch in channels], dim=1)
        return out.reshape(z.shape[0], -1)

    z = torch.as_tensor(np.asarray(z_pts, dtype=np.float32))
    cols = []
    for k in range(z.shape[1]):
        v = torch.zeros_like(z)
        v[:, k] = 1.0
        _, jk = jvp(fn, (z,), (v,))
        cols.append(jk.detach().cpu().numpy().astype(np.float64))
    return np.stack(cols)


# ---- decomposition -----------------------------------------------------------

def decompose(y: np.ndarray, T: np.ndarray, weights: np.ndarray | None = None):
    """No-intercept least squares y ~ T^T a; returns (a (6,), uncentered R^2)."""
    A = T.T
    if weights is not None:
        sw = np.sqrt(weights)
        A, y = A * sw[:, None], y * sw
    a, *_ = np.linalg.lstsq(A, y, rcond=None)
    ss_res = float(((y - A @ a) ** 2).sum())
    ss_tot = float((y ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else None
    return a, _f(r2)


def lasso_support(y: np.ndarray, T: np.ndarray, seed: int = 0):
    """Support scan on unit-norm columns (5-fold CV lasso, fixed seed)."""
    from sklearn.linear_model import LassoCV
    from sklearn.model_selection import KFold

    A = T.T
    norms = np.linalg.norm(A, axis=0)
    norms[norms == 0] = 1.0
    A_std = A / norms
    cv = KFold(n_splits=5, shuffle=True, random_state=seed)
    las = LassoCV(fit_intercept=False, cv=cv, n_alphas=60,
                  max_iter=100_000).fit(A_std, y)
    support = [j for j in range(6) if abs(las.coef_[j]) > 1e-10]
    if not support:
        return [], None
    a_pl = np.zeros(6)
    sub, *_ = np.linalg.lstsq(A[:, support], y, rcond=None)
    a_pl[support] = sub
    return support, a_pl


def cosine(x: np.ndarray, y: np.ndarray):
    nx, ny = np.linalg.norm(x), np.linalg.norm(y)
    if nx == 0 or ny == 0:
        return None
    return _f(float(np.dot(x, y) / (nx * ny)))


def raw_ratio(a: np.ndarray, half: np.ndarray):
    """Implied raw-space (tau, lnAs) gradient ratio; None if lnAs part ~ 0."""
    num, den = a[I_TAU] / half[I_TAU], a[I_AS] / half[I_AS]
    scale = np.abs(a / half).max()
    if scale == 0 or abs(den) < 1e-3 * scale:
        return None
    return _f(num / den)


def amp_mass(a: np.ndarray):
    tot = np.abs(a).sum()
    return _f((abs(a[I_TAU]) + abs(a[I_AS])) / tot) if tot > 0 else None


def pair_projections(a: np.ndarray, half: np.ndarray):
    """Raw-space (tau, lnAs) displacement split along the A_s e^{-2 tau}
    DEGENERATE direction (1, 2)/sqrt(5) and the BREAKING direction
    (-2, 1)/sqrt(5). Where the two templates are collinear (TT-only spectra:
    the degenerate direction is spectrum-invisible), the fit's ridge moves
    the pair exactly along (1, 2) — proj_deg is then unidentifiable while
    proj_brk stays identifiable."""
    d = np.array([a[I_TAU] * half[I_TAU], a[I_AS] * half[I_AS]])
    s5 = np.sqrt(5.0)
    return (_f(float(d @ np.array([1.0, 2.0]) / s5)),
            _f(float(d @ np.array([-2.0, 1.0]) / s5)))


def pair_identifiability(T: np.ndarray) -> dict:
    """Collinearity of the (tau, lnAs) template pair in a design matrix:
    uncentered cosine and the condition number of the unit-norm 2-column
    submatrix. cond >> 1 means the within-pair split is ridge-limited."""
    u, v = T[I_TAU], T[I_AS]
    nu, nv = np.linalg.norm(u), np.linalg.norm(v)
    if nu == 0 or nv == 0:
        return {"cos": None, "cond": None}
    cos = float(np.dot(u, v) / (nu * nv))
    cond = float(np.linalg.cond(np.stack([u / nu, v / nv], axis=1)))
    return {"cos": _f(cos), "cond": _f(cond)}


# ---- per-run driver ----------------------------------------------------------

def run_decoder_effect(run: str, n_latents: int, amp_idx: int, args) -> dict:
    import torch

    from cmb_lcdm_sr.encoder import load_checkpoint
    from cmb_lcdm_sr.scaler import ShardedScaler

    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "4")))
    run_dir = Path("models") / run
    model, _ckpt = load_checkpoint(run_dir / "best_model.pt", device="cpu")
    scaler = ShardedScaler.load(run_dir / "scaler.npz")
    channels = scaler.channels
    means = np.load(run_dir / "analysis" / "encoder_means_test.npy")

    tpl = np.load(Path(args.templates), allow_pickle=False)
    tpl_channels = [str(c) for c in tpl["channels"]]
    missing = [ch for ch in channels if ch not in tpl_channels]
    if missing:
        raise ValueError(f"templates file lacks channels {missing}")
    lengths = {ch: len(scaler.refs[ch]) for ch in channels}
    for ch in channels:
        if tpl[f"templates_{ch}"].shape != (6, lengths[ch]):
            raise ValueError(f"template shape mismatch for '{ch}'")
    mid, half = tiers.load_prior_box(args.dataset_dir)
    if not np.allclose(tpl["half"], half):
        raise ValueError("prior box mismatch between templates and meta.json")

    sigma = np.concatenate([scaler.channel_stats(ch)[1] for ch in channels])
    ells = np.concatenate([tpl[f"ell_{ch}"] for ch in channels])
    T_phys = np.concatenate([tpl[f"templates_{ch}"] for ch in channels], axis=1)
    T_chk = np.concatenate([tpl[f"templates_hcheck_{ch}"] for ch in channels],
                           axis=1)
    T_norm, T_chk_norm = T_phys / sigma, T_chk / sigma

    # Evaluation points: T1 mean (anchor) + a deterministic T1 spread.
    mu_t1 = means[tiers.T1]
    rng = np.random.default_rng([SEED_BASE, 7])
    idx = rng.choice(mu_t1.shape[0], size=args.n_spread, replace=False)
    z_pts = np.vstack([mu_t1.mean(axis=0)[None, :], mu_t1[idx]])

    print(f"[jvp] {run}: {n_latents} latents x {z_pts.shape[0]} points "
          f"({sum(lengths.values())} output bins)")
    cols = decoder_columns(model, channels, z_pts)          # (L, P, sumL)

    # Phase-3 symbolic signatures for the triangulation column.
    sig_p3 = {}
    audit_path = Path(args.audit_json or
                      f"experiments/sufficiency_audit_{run}.json")
    if audit_path.exists():
        for L in json.loads(audit_path.read_text())["latents"]:
            sig_p3[L["latent"]] = L.get("canonical", {}).get("signature")

    # Identifiability of the (tau, lnAs) split in this run's design.
    ident = {"concat": pair_identifiability(T_norm)}
    off = 0
    for ch in channels:
        ident[ch] = pair_identifiability(T_norm[:, off:off + lengths[ch]])
        off += lengths[ch]
    ridge_limited = bool((ident["concat"]["cond"] or 0.0) > 10.0)

    w_ell = (2.0 * ells + 1.0)
    ks = args.latents if args.latents is not None else list(range(n_latents))
    latents_out, curves = [], {}
    for k in ks:
        anchor = cols[k, 0]
        spread = cols[k, 1:]
        y = spread.mean(axis=0)
        band = spread.std(axis=0)
        curves[k] = {"anchor_norm": anchor, "mean_norm": y, "std_norm": band}

        a_ols, r2 = decompose(y, T_norm)
        support, a_pl = lasso_support(y, T_norm, seed=SEED_BASE % 2**31)
        a_w, r2_w = decompose(y * sigma, T_phys, weights=w_ell)
        a_chk, r2_chk = decompose(y, T_chk_norm)
        a_anc, r2_anc = decompose(anchor, T_norm)

        g = sig_p3.get(k)
        stab = {"weighted_2l1": cosine(a_ols, a_w),
                "bandwidth_h2": cosine(a_ols, a_chk),
                "anchor_point": cosine(a_ols, a_anc)}
        entry = {
            "latent": k, "audit_expected": AUDIT_EXPECTED[run].get(k),
            "a_ols": [_f(v) for v in a_ols], "r2_W": r2,
            "lasso_support": [tiers.SAMPLED_LABELS[j] for j in support],
            "a_postlasso": ([_f(v) for v in a_pl] if a_pl is not None
                            else None),
            "a_weighted": [_f(v) for v in a_w], "r2_weighted": r2_w,
            "a_hcheck": [_f(v) for v in a_chk], "r2_hcheck": r2_chk,
            "a_anchor": [_f(v) for v in a_anc], "r2_anchor": r2_anc,
            "amp_mass": amp_mass(a_ols),
            "r_dec": raw_ratio(a_ols, half),
            "r_dec_weighted": raw_ratio(a_w, half),
            "r_dec_hcheck": raw_ratio(a_chk, half),
            "r_dec_anchor": raw_ratio(a_anc, half),
            "cos_signature_p3": (cosine(np.abs(a_ols), np.asarray(g))
                                 if g is not None else None),
            "stability_cos": stab,
            "proj_pair": {name: pair_projections(av, half)
                          for name, av in (("ols", a_ols), ("weighted", a_w),
                                           ("hcheck", a_chk),
                                           ("anchor", a_anc))},
            "curve_rms_phys": _f(float(np.sqrt(((y * sigma) ** 2).mean()))),
        }
        pd_, pb_ = entry["proj_pair"]["ols"]
        entry["frac_brk"] = (_f(abs(pb_) / (abs(pd_) + abs(pb_)))
                             if pd_ is not None and abs(pd_) + abs(pb_) > 0
                             else None)
        latents_out.append(entry)
        print(f"  z{k}: R2_W={fmt(r2)} support={{{','.join(entry['lasso_support'])}}} "
              f"amp_mass={fmt(entry['amp_mass'], 2)} r_dec={fmt(entry['r_dec'], 2)} "
              f"proj(deg,brk)=({fmt(pd_)},{fmt(pb_)}) "
              f"cos_g={fmt(entry['cos_signature_p3'], 2)}")

    # ---- gate G4b + combined G4 restatement ---------------------------------
    g4b = None
    amp_L = next((L for L in latents_out if L["latent"] == amp_idx), None)
    if amp_L is not None:
        m, r, r2a = amp_L["amp_mass"], amp_L["r_dec"], amp_L["r2_W"]
        g4b = {"latent": amp_idx, "amp_mass": m, "r_dec": r, "r2_W": r2a,
               "pass_mass": bool(m is not None and m >= G4B_AMP_MASS_MIN),
               "pass_ratio": bool(r is not None
                                  and abs(r + 2.0) <= G4B_RATIO_TOL),
               "pass_r2": bool(r2a is not None and r2a >= G4B_R2_MIN)}
        g4b["pass"] = bool(g4b["pass_mass"] and g4b["pass_ratio"]
                           and g4b["pass_r2"])
        print(f"  G4b: amp_mass {fmt(m, 2)} (>= {G4B_AMP_MASS_MIN}: "
              f"{g4b['pass_mass']}), r_dec {fmt(r, 2)} (|r+2| <= "
              f"{G4B_RATIO_TOL}: {g4b['pass_ratio']}), R2_W {fmt(r2a, 2)} "
              f"-> {'PASS' if g4b['pass'] else 'FAIL'}")

    g4a = None
    ls_path = Path(f"experiments/levelset_audit_{run}.json")
    if ls_path.exists():
        g4a = json.loads(ls_path.read_text()).get("gate_G4a")

    return {"run": run, "channels": channels,
            "config": {"n_spread": args.n_spread, "seed_base": SEED_BASE,
                       "templates": str(args.templates),
                       "h_main": _f(float(tpl["h_main"])),
                       "h_check": _f(float(tpl["h_check"])),
                       "g4b_rule": {"amp_mass_min": G4B_AMP_MASS_MIN,
                                    "ratio_tol": G4B_RATIO_TOL,
                                    "r2_min": G4B_R2_MIN}},
            "template_identifiability": ident,
            "pair_ridge_limited": ridge_limited,
            "latents": latents_out, "gate_G4b": g4b,
            "gate_G4a_restated": ({"pass": g4a.get("pass")} if g4a else None),
            "generated_by": "scripts/decoder_effect.py"}, curves, {
                "sigma": sigma, "ells": ells, "lengths": lengths,
                "channels": channels}


# ---- figure ------------------------------------------------------------------

def save_figure(run: str, payload: dict, curves: dict, aux: dict, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    channels, lengths = aux["channels"], aux["lengths"]
    sigma, ells = aux["sigma"], aux["ells"]
    edges = np.cumsum([0] + [lengths[ch] for ch in channels])
    ks = [L["latent"] for L in payload["latents"]]
    nrows, ncols = len(ks), len(channels)
    fig, axes = plt.subplots(nrows, ncols,
                             figsize=(4.6 * ncols, 1.9 * nrows),
                             squeeze=False, sharex="col")
    line_c, band_c, anchor_c = "#3557a7", "#3557a7", "#666666"
    for r, k in enumerate(ks):
        cv = curves[k]
        for c, ch in enumerate(channels):
            sl = slice(edges[c], edges[c + 1])
            ax = axes[r][c]
            x = ells[sl]
            mean_p = cv["mean_norm"][sl] * sigma[sl]
            std_p = cv["std_norm"][sl] * sigma[sl]
            anc_p = cv["anchor_norm"][sl] * sigma[sl]
            ax.axhline(0.0, color="#bbbbbb", lw=0.7, zorder=1)
            ax.fill_between(x, mean_p - std_p, mean_p + std_p,
                            color=band_c, alpha=0.18, lw=0, zorder=2,
                            label="spread ±1σ" if (r, c) == (0, 0) else None)
            ax.plot(x, mean_p, color=line_c, lw=1.4, zorder=3,
                    label="spread mean" if (r, c) == (0, 0) else None)
            ax.plot(x, anc_p, color=anchor_c, lw=0.9, ls="--", zorder=4,
                    label="anchor z̄" if (r, c) == (0, 0) else None)
            ax.set_xscale("log")
            ax.grid(alpha=0.15)
            role = payload["latents"][r]["audit_expected"]
            ax.set_title(f"z{k} · {ch}   ({role})", fontsize=9, loc="left")
            if r == nrows - 1:
                ax.set_xlabel(r"$\ell$")
            if c == 0:
                ax.set_ylabel(r"$\partial \log_{10} D_\ell / \partial z_k$",
                              fontsize=8)
    axes[0][0].legend(frameon=False, fontsize=7, loc="best")
    fig.suptitle(f"Decoder effect d_k(ℓ) — {run}", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.985))
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---- markdown ----------------------------------------------------------------

def _avec(a):
    return "n/a" if a is None else " ".join(
        f"{lab}={v:+.2f}" for lab, v in zip(tiers.SAMPLED_LABELS, a)
        if v is not None and abs(v) >= 0.005) or "~0"


def to_markdown(payload: dict) -> str:
    run = payload["run"]
    cfg = payload["config"]
    md = [f"# Decoder-effect triangulation — `{run}` (roadmap Phase 7b, "
          "gate G4b)\n"]
    md.append(
        f"d_k(ℓ) = ∂Decoder(z)_ℓ/∂z_k by JVP at the T1 mean (anchor) and "
        f"across {cfg['n_spread']} T1 posterior-mean rows (spread mean ± "
        "band); per-ℓ σ from `scaler.npz` converts to physical "
        "∂log₁₀D_ℓ/∂z_k. Decomposition d_k ≈ Σ_j a_kj·t_j against the "
        f"local-quadratic templates (h={cfg['h_main']}, check "
        f"h={cfg['h_check']}), no intercept, W = identity in normalised "
        "space; a_kj = u_j-units per unit z_k. r_dec = "
        "(a_τ/half_τ)/(a_lnAs/half_lnAs) is the implied raw-space "
        "amplitude-pair ratio. cos g_j triangulates |a| against the "
        "Phase-3 symbolic signature. Figure: "
        f"`decoder_effect_{run}_curves.png`; full curves in the twin "
        ".npz.\n")
    ident = payload["template_identifiability"]
    md.append("## Template identifiability of the (τ, lnAs) split\n")
    md.append("| design | uncentered cos(t_τ, t_lnAs) | cond |")
    md.append("|---|---:|---:|")
    for name in ["concat"] + payload["channels"]:
        d = ident[name]
        md.append(f"| {name} | {fmt(d['cos'], 4)} | {fmt(d['cond'], 1)} |")
    if payload["pair_ridge_limited"]:
        md.append(
            "\n_The pair is **ridge-limited** in this run's design (cond > "
            "10): moving θ along the degenerate direction (δτ, δlnAs) ∝ "
            "(1, 2) leaves these spectra invisible, so the fitted "
            "(a_τ, a_lnAs) split — hence r_dec and amp mass — drifts freely "
            "along that ridge and only proj_brk (the degeneracy-breaking "
            "component, direction (−2, 1)/√5 in raw (τ, lnAs)) is "
            "identifiable. proj_deg and r_dec below are reported for "
            "completeness, not as claims._\n")
    else:
        md.append(
            "\n_Well-conditioned pair: the low-ℓ EE reionization feature "
            "breaks the A_s e^{−2τ} degeneracy, so the within-pair split "
            "(r_dec, proj_deg vs proj_brk) is identifiable._\n")

    md.append("| latent | role | a (u-units/z, OLS) | R²_W | lasso support "
              "| amp mass | r_dec | proj_deg | proj_brk | cos g_j "
              "| min stab cos |")
    md.append("|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|")
    for L in payload["latents"]:
        stab = [v for v in L["stability_cos"].values() if v is not None]
        pd_, pb_ = L["proj_pair"]["ols"]
        md.append(
            f"| z{L['latent']} | {L['audit_expected']} "
            f"| {_avec(L['a_ols'])} | {fmt(L['r2_W'])} "
            f"| {{{', '.join(L['lasso_support'])}}} "
            f"| {fmt(L['amp_mass'], 2)} | {fmt(L['r_dec'], 2)} "
            f"| {fmt(pd_)} | {fmt(pb_)} "
            f"| {fmt(L['cos_signature_p3'], 2)} "
            f"| {fmt(min(stab) if stab else None, 3)} |")
    md.append("\n_Stability cosines compare the OLS coefficient vector "
              "against the (2ℓ+1)-weighted physical-space refit, the "
              "halved-bandwidth templates, and the anchor-point curve; on a "
              "ridge-limited design they are dominated by ridge drift of "
              "the (τ, lnAs) split and understate the stability of the "
              "identifiable components._\n")

    for L in payload["latents"]:
        md.append(f"\n## z{L['latent']} — {L['audit_expected']}\n")
        md.append("| variant | a | R² | r_dec | proj_deg | proj_brk |")
        md.append("|---|---|---:|---:|---:|---:|")
        for name, a_key, r2_key, r_key, p_key in (
                ("OLS (normalised)", "a_ols", "r2_W", "r_dec", "ols"),
                ("post-lasso", "a_postlasso", None, None, None),
                ("(2ℓ+1)-weighted", "a_weighted", "r2_weighted",
                 "r_dec_weighted", "weighted"),
                ("templates h/2", "a_hcheck", "r2_hcheck", "r_dec_hcheck",
                 "hcheck"),
                ("anchor point", "a_anchor", "r2_anchor", "r_dec_anchor",
                 "anchor")):
            pd_, pb_ = (L["proj_pair"][p_key] if p_key else (None, None))
            md.append(f"| {name} | {_avec(L.get(a_key))} "
                      f"| {fmt(L.get(r2_key)) if r2_key else ''} "
                      f"| {fmt(L.get(r_key), 2) if r_key else ''} "
                      f"| {fmt(pd_)} | {fmt(pb_)} |")

    g = payload["gate_G4b"]
    if g is not None:
        rule = cfg["g4b_rule"]
        md.append("\n# Gate G4b (decoder bullet of G4)\n")
        md.append("| bullet | numbers | pass |")
        md.append("|---|---|---|")
        md.append(f"| amplitude-sector mass ≥ {rule['amp_mass_min']} "
                  f"| {fmt(g['amp_mass'], 2)} "
                  f"| {'PASS' if g['pass_mass'] else 'FAIL'} |")
        md.append(f"| \\|r_dec + 2\\| ≤ {rule['ratio_tol']} "
                  f"| r_dec = {fmt(g['r_dec'], 3)} "
                  f"| {'PASS' if g['pass_ratio'] else 'FAIL'} |")
        md.append(f"| decomposition R²_W ≥ {rule['r2_min']} "
                  f"| {fmt(g['r2_W'], 3)} "
                  f"| {'PASS' if g['pass_r2'] else 'FAIL'} |")
        md.append(f"\n**Gate G4b: {'PASS' if g['pass'] else 'FAIL'}**")
        if payload["pair_ridge_limited"]:
            cond = payload["template_identifiability"]["concat"]["cond"]
            md.append(
                f"\n_Mechanism: with cond = {fmt(cond, 1)} the r_dec and "
                "amp-mass bullets test a within-pair split this run's "
                "spectra cannot express — the A_s e^{−2τ} degenerate "
                "direction is invisible to them, so the frozen rule is "
                "evaluated as registered but its FAIL here reflects "
                "template collinearity, not a wrong decoder direction. The "
                "identifiable decoder-side statement is proj_brk and the "
                "shape-sector coefficients above._")
        g4a = payload.get("gate_G4a_restated")
        if g4a is not None:
            md.append(f"\nG4a (level-set bullet, Phase 7a): "
                      f"**{'PASS' if g4a['pass'] else 'FAIL'}** — the "
                      "documented structured-residual E_inv verdict; see "
                      f"`levelset_audit_{run}.md`.")
    md.append("\n---\n_Generated by `scripts/decoder_effect.py`._")
    return "\n".join(md) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", required=True)
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--templates", default="data/spectral_templates_v1.npz")
    p.add_argument("--audit-json", default=None)
    p.add_argument("--latents", nargs="*", type=int, default=None)
    p.add_argument("--n-spread", type=int, default=N_SPREAD)
    p.add_argument("--out", default=None)
    args = p.parse_args()

    model = next((m for m in MODELS if m[1] == args.run), None)
    if model is None:
        print(f"[FAIL] unknown run {args.run}")
        return 1
    _label, run, n_latents, amp_idx = model

    payload, curves, aux = run_decoder_effect(run, n_latents, amp_idx, args)

    out = Path(args.out or f"experiments/decoder_effect_{run}")
    out.parent.mkdir(parents=True, exist_ok=True)

    npz = {f"z{k}_{key}": arr for k, cv in curves.items()
           for key, arr in cv.items()}
    npz["sigma"] = aux["sigma"]
    npz["ells"] = aux["ells"]
    npz["channels"] = np.array(aux["channels"])
    npz["lengths"] = np.array([aux["lengths"][ch] for ch in aux["channels"]])
    np.savez(out.parent / f"{out.name}_curves.npz", **npz)
    print(f"[write] {out.parent / (out.name + '_curves.npz')}")

    save_figure(run, payload, curves, aux,
                out.parent / f"{out.name}_curves.png")
    print(f"[write] {out.parent / (out.name + '_curves.png')}")

    out.with_suffix(".json").write_text(json.dumps(payload, indent=2))
    print(f"[write] {out.with_suffix('.json')}")
    out.with_suffix(".md").write_text(to_markdown(payload))
    print(f"[write] {out.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
