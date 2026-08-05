#!/usr/bin/env python
"""Intrinsic information ceiling from the stochastic latent — Phase 5 of
docs/discovery_roadmap.md (gate G3).

Replaces "fraction of the maxsize-30 plateau" with "fraction of the
information the latent actually stores". The mean map theta -> mu_k is
deterministic, so I(mu_k; theta) is unbounded; the sampled latent
Z_k | theta ~ N(mu_k, sigma_k^2) gives a finite, principled ceiling

    I(Z_k; theta) = H(Z_k) - E_theta[ 1/2 ln(2 pi e sigma_k^2(theta)) ]

with the conditional term analytic from the cached logvars
(sigma_k = exp(logvar/2), logvar clamped to (-10, 10) as in the model).

Per latent, over T1 u T2 (the SR search never saw these rows):

  1. noise table first — E[sigma^2], median sigma, Var(mu), SNR, clamp
     fraction, and the Gaussian-channel reference 1/2 ln(1 + SNR): it
     predicts how binding the ceiling is before any estimation;
  2. H(Z_k): m = 4 posterior draws per row; 1-D GMM (BIC over K <= 5) fit
     on the first m/2 draws, cross-entropy -E[log q] on the held-out
     draws (an upper-bound-flavoured estimate: E[-log q] = H + KL(p||q));
     I and its SE from a joint row bootstrap of both terms;
  3. eta_post(f) = MI(Z_k; f(theta)) / I(Z_k; theta) for the Phase-2
     canonical coordinate and every 4b finalist form (subset_selection
     finals), numerator from the scalar-scalar GMM-MI machinery on a
     fresh posterior draw over T2 (confirmatory tier, section 0.4);
  4. sanity: data-processing bound MI(Z;f) <= I(Z;theta) within one
     combined SE, flagged per candidate; residual-variance cross-check
     Var(e_k)/E[sigma^2] from the Phase-3 residual caches — the direct
     "does the posterior noise sit above the leftover modulation" readout.

**Registered estimator-consistency refinement** (decided on the synthetic
positive control BEFORE any real-data run; roadmap section 0.3 deviation
protocol). On a channel with known truth (Z = 2 tanh(U) + noise,
I_true = 1.124 nat) the cross-entropy ceiling is exact (1.126 +/- 0.016)
but the GMM-MI numerator over-estimates by ~7% (1.202) — the risk
register's "GMM-MI SE underestimates at high MI" row. A raw
MI(Z;f) <= I comparison therefore flags sufficient coordinates, and the
0.95 rule on MI/I is structurally unreachable where the GMM-MI estimator
saturates below the analytic ceiling. Fix, applied uniformly: per latent
also score MI(Z_k; mu_k) on the same posterior draw — the same-estimator
ceiling proxy (mu is the model's own mean map; I(Z;theta) = I(Z;mu) up to
the negligible sigma-channel). Then

  * eta_post      = MI(Z;f) / I(Z;theta)   — principled headline ratio;
  * eta_post_hat  = MI(Z;f) / MI(Z;mu)     — same-estimator ratio (shared
    bias cancels): this drives the 0.95 demotion rule and phase6_needed;
  * DPI check     = MI(Z;f) <= MI(Z;mu) + 2 SE (same estimator, same
    draw); the analytic margin I − MI(Z;f) is reported alongside.

**Gate G3**: DPI holds for all candidates and the amplitude latent's
eta_post(f1) is reported. Branch (not pass/fail): eta_post_hat >= 0.95
(the frozen section-0.3 sufficiency default) demotes the structured
residual to sub-noise detail; eta_post_hat < 0.95 means the residual is
genuinely stored information and Phase 6 matters. The same rule sets each
latent's `phase6_needed` = (Phase-3 residual audit failed) AND
(eta_post_hat < 0.95).

Reads:  experiments/{semantic_recurrence,subset_selection,knee_readout,
        sufficiency_audit}_<run>.json,
        models/<run>/analysis/encoder_{means,logvars}_test.npy (+ residual caches)
Writes: experiments/posterior_ceiling_<run>.{md,json}

    python scripts/posterior_ceiling.py --run lcdm_tt_beta3e-4 --jobs 5
"""
import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ.setdefault("TQDM_DISABLE", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import _bootstrap  # noqa: F401,E402

import numpy as np  # noqa: E402

from consolidate_allparams import AUDIT_EXPECTED, MODELS  # noqa: E402

from cmb_lcdm_sr import semantics, tiers  # noqa: E402
from cmb_lcdm_sr.mi import mutual_information_gmm  # noqa: E402

SEED_BASE = 20260805
LN2PIE = float(np.log(2.0 * np.pi * np.e))
LOGVAR_CLAMP = 10.0
POOL_LABELS = ["omega_b", "omega_cdm", "H0", "tau", "A_s", "n_s"]  # spec order

# worker-shared state (populated in main, inherited by fork)
_G: dict = {}


def _f(v):
    """float(v) if finite else None — keeps the JSON standard-parseable."""
    return float(v) if v is not None and np.isfinite(v) else None


# ---- estimators --------------------------------------------------------------

def noise_summary(mu: np.ndarray, logvar_raw: np.ndarray) -> dict:
    """Per-latent noise table (computed first: predicts how binding I is)."""
    lv = np.clip(np.asarray(logvar_raw, np.float64), -LOGVAR_CLAMP, LOGVAR_CLAMP)
    sigma2 = np.exp(lv)
    var_mu = float(np.var(mu))
    e_s2 = float(sigma2.mean())
    snr = var_mu / e_s2
    return {
        "e_sigma2": e_s2,
        "median_sigma": float(np.median(np.exp(0.5 * lv))),
        "var_mu": var_mu,
        "snr": snr,
        "i_gauss": 0.5 * float(np.log1p(snr)),
        "logvar_min": float(np.min(logvar_raw)),
        "logvar_max": float(np.max(logvar_raw)),
        "clamp_frac": float((np.abs(logvar_raw) >= LOGVAR_CLAMP).mean()),
    }


def fit_gmm_bic(x: np.ndarray, k_max: int = 5, seed: int = 0):
    """(model, bic, K) of the BIC-best 1-D GaussianMixture with K <= k_max."""
    from sklearn.mixture import GaussianMixture

    X = x.reshape(-1, 1)
    best = None
    for K in range(1, k_max + 1):
        gm = GaussianMixture(n_components=K, covariance_type="full",
                             random_state=seed, n_init=2, max_iter=500).fit(X)
        bic = gm.bic(X)
        if best is None or bic < best[1]:
            best = (gm, float(bic), K)
    return best


def intrinsic_ceiling(mu: np.ndarray, logvar_raw: np.ndarray, m_draws: int = 4,
                      rng: np.random.Generator | None = None,
                      n_boot: int = 500, k_max: int = 5) -> dict:
    """I(Z; theta) = H(Z) − E[1/2 ln(2 pi e sigma^2)] with a row-bootstrap SE.

    H(Z) via held-out cross-entropy: GMM (BIC over K <= k_max) fit on the
    first m/2 draws, −E[log q] on the remaining draws. Both terms are
    per-row quantities, so one joint bootstrap over rows gives the SE of I.
    """
    rng = rng or np.random.default_rng(0)
    mu = np.asarray(mu, np.float64)
    lv = np.clip(np.asarray(logvar_raw, np.float64), -LOGVAR_CLAMP, LOGVAR_CLAMP)
    sigma = np.exp(0.5 * lv)
    n = mu.shape[0]
    m_fit = max(1, m_draws // 2)

    eps = rng.standard_normal((n, m_draws))
    Z = mu[:, None] + sigma[:, None] * eps
    fit = Z[:, :m_fit].ravel()
    held = Z[:, m_fit:]

    gm, _bic, K = fit_gmm_bic(fit, k_max=k_max)
    logq = gm.score_samples(held.reshape(-1, 1)).reshape(n, m_draws - m_fit)
    a_row = -logq.mean(axis=1)                 # held-out −log q per row
    c_row = 0.5 * (LN2PIE + lv)                # exact conditional entropy per row
    d_row = a_row - c_row
    boots = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, n)
        boots[b] = d_row[idx].mean()
    return {
        "H_z": float(a_row.mean()),
        "H_z_fitsplit": float(-gm.score_samples(fit.reshape(-1, 1)).mean()),
        "H_cond": float(c_row.mean()),
        "I": float(d_row.mean()),
        "se": float(boots.std(ddof=1)),
        "K_bic": int(K),
        "n_rows": int(n),
        "m_draws": int(m_draws),
    }


def numerator_mi(z_sample: np.ndarray, fvals: np.ndarray,
                 max_samples: int = 5000, seed: int = 0):
    """(mi, err, finite_frac) of GMM-MI(Z; f) on jointly finite rows."""
    m = np.isfinite(fvals) & np.isfinite(z_sample)
    frac = float(m.mean())
    if frac < 0.5 or m.sum() < 256:
        return None, None, frac
    mi, err = mutual_information_gmm(z_sample[m].reshape(-1, 1),
                                     fvals[m].reshape(-1, 1),
                                     return_uncertainty=True,
                                     max_samples=max_samples, seed=seed)
    v, e = float(mi[0, 0]), float(err[0, 0])
    if not np.isfinite(v):
        return None, None, frac
    return v, (e if np.isfinite(e) else None), frac


def eta_with_se(mi, mi_err, I, I_se):
    """eta_post = mi/I with first-order error propagation (mi = 0 safe)."""
    if mi is None or I is None or I <= 0:
        return None, None
    eta = float(mi / I)
    if mi_err is None or I_se is None:
        return eta, None
    se = float(np.sqrt((mi_err / I) ** 2 + (mi * I_se / I ** 2) ** 2))
    return eta, se


def dpi_check(mi, mi_err, mi_ref, mi_ref_err, I, I_se):
    """(ok, margin_ref, margin_analytic) of the estimator-consistent DPI test.

    Violation iff MI(Z;f) exceeds the same-estimator ceiling proxy MI(Z;mu)
    by more than 2 combined SEs; falls back to the analytic ceiling when the
    proxy is unavailable. The analytic margin I − mi is reported either way
    (it may go slightly negative where the GMM-MI estimator's upward bias
    exceeds its SE — that alone is not a violation).
    """
    if mi is None:
        return None, None, None
    margin_analytic = None if I is None else float(I - mi)
    if mi_ref is not None:
        comb = float(np.sqrt((mi_err or 0.0) ** 2 + (mi_ref_err or 0.0) ** 2))
        return bool(mi <= mi_ref + 2.0 * comb), float(mi_ref - mi), margin_analytic
    if I is None:
        return None, None, None
    comb = float(np.sqrt((mi_err or 0.0) ** 2 + (I_se or 0.0) ** 2))
    return bool(mi <= I + 2.0 * comb), None, margin_analytic


# ---- candidates --------------------------------------------------------------

def assemble_candidates(sem_lat: dict, fin_lat: dict) -> list[dict]:
    """Canonical coordinate + all-6 reference + every 4b finalist form.

    Deduplicated by expression string (the all-6 reference recurs as the
    'allparams' finals entry); every config id mapping to the surviving
    entry is kept in `config_ids` so S* can be located after the merge.
    """
    canon = next(c for c in sem_lat["clusters"]
                 if c["cluster"] == sem_lat["canonical_cluster"])
    raw = [{"kind": "canonical", "config_id": "canonical", "inputs": None,
            "size": None, "expr": canon["representative"], "best_c": None}]
    ref = fin_lat["ref"]
    raw.append({"kind": "reference", "config_id": "allparams",
                "inputs": list(POOL_LABELS), "size": 6,
                "expr": ref["best_expr"], "best_c": ref.get("best_c")})
    for e in fin_lat["entries"]:
        raw.append({"kind": "finalist", "config_id": e["config_id"],
                    "inputs": list(e["inputs"]), "size": int(e["size"]),
                    "expr": e["best_expr"], "best_c": e.get("best_c")})

    out: dict[str, dict] = {}
    for c in raw:
        cur = out.get(c["expr"])
        if cur is None:
            cur = {k: c[k] for k in ("kind", "inputs", "size", "expr", "best_c")}
            cur["config_ids"] = []
            out[c["expr"]] = cur
        if c["config_id"] not in cur["config_ids"]:
            cur["config_ids"].append(c["config_id"])
        if cur["inputs"] is None and c["inputs"] is not None:
            cur["inputs"], cur["size"] = c["inputs"], c["size"]
            cur["best_c"] = c["best_c"]
    return list(out.values())


def expr_support(expr_str: str):
    """Sampled-basis labels an expression depends on (None if unparseable)."""
    expr = semantics.parse_expr(expr_str)
    if expr is None:
        return None
    syms = semantics._sampledify(expr).free_symbols
    return [lab for lab, s in zip(tiers.SAMPLED_LABELS, semantics.SAMPLED_SYMBOLS)
            if s in syms]


# ---- per-latent worker -------------------------------------------------------

def latent_worker(k: int) -> dict:
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=1):
        return _latent_worker(k)


def _latent_worker(k: int) -> dict:
    assert tiers.T1.stop == tiers.T2.start, "T1 and T2 must be contiguous"
    rows = slice(tiers.T1.start, tiers.T2.stop)          # T1 u T2

    mu_all = _G["mu"][:, k]
    lv_all_raw = _G["logvar"][:, k]
    mu, lv_raw = mu_all[rows], lv_all_raw[rows]

    noise = noise_summary(mu, lv_raw)
    ceil = intrinsic_ceiling(mu, lv_raw, m_draws=_G["m_draws"],
                             rng=np.random.default_rng([SEED_BASE, k]),
                             n_boot=_G["n_boot"])
    I, I_se = ceil["I"], ceil["se"]
    ceiling_ok = bool(I > 0 and I > 3.0 * I_se)

    # residual-variance cross-check from the Phase-3 cache
    res_var = res_ratio = None
    res_path = Path(_G["run_dir"]) / "analysis" / f"residual_z{k}_v1.npy"
    if res_path.exists():
        e = np.load(res_path)[rows]
        if np.isfinite(e).mean() > 0.5:
            res_var = float(np.nanvar(e))
            res_ratio = res_var / noise["e_sigma2"]

    # fresh posterior draw on T2 for every numerator (never used in H)
    t2 = tiers.T2
    lv_t2 = np.clip(lv_all_raw[t2], -LOGVAR_CLAMP, LOGVAR_CLAMP)
    z_num = (mu_all[t2] + np.exp(0.5 * lv_t2) *
             np.random.default_rng([SEED_BASE, k, 7])
             .standard_normal(t2.stop - t2.start))
    theta_t2 = _G["theta_t2"]

    # same-estimator ceiling proxy: MI(Z; mu) on the same draw
    mi_ref, mi_ref_err, _ = numerator_mi(z_num, mu_all[t2],
                                         max_samples=_G["max_samples_mi"],
                                         seed=SEED_BASE + 1000 * k + 999)

    fin_lat = _G["finals"]["latents"][f"z{k}"]
    cands = assemble_candidates(_G["semantic"]["latents"][f"z{k}"], fin_lat)
    out_c = []
    for i, c in enumerate(cands):
        fv = semantics.evaluate_on_theta(c["expr"], theta_t2)
        mi, err, frac = numerator_mi(z_num, fv,
                                     max_samples=_G["max_samples_mi"],
                                     seed=SEED_BASE + 1000 * k + i)
        eta = eta_se = eta_hat = eta_hat_se = None
        dpi_ok = dpi_margin = dpi_margin_analytic = None
        if mi is not None and ceiling_ok:
            eta, eta_se = eta_with_se(mi, err, I, I_se)
            eta_hat, eta_hat_se = eta_with_se(mi, err, mi_ref, mi_ref_err)
            dpi_ok, dpi_margin, dpi_margin_analytic = dpi_check(
                mi, err, mi_ref, mi_ref_err, I, I_se)
        out_c.append({**c, "support": expr_support(c["expr"]),
                      "finite_frac_T2": frac, "mi": _f(mi), "mi_err": _f(err),
                      "eta_post": _f(eta), "eta_post_se": _f(eta_se),
                      "eta_post_hat": _f(eta_hat),
                      "eta_post_hat_se": _f(eta_hat_se),
                      "dpi_ok": dpi_ok, "dpi_margin": _f(dpi_margin),
                      "dpi_margin_analytic": _f(dpi_margin_analytic)})

    canonical = next(c for c in out_c if c["kind"] == "canonical")
    s_star_id = fin_lat["s_star"]["config_id"]
    sstar = next((c for c in out_c if s_star_id in c["config_ids"]), None)

    residual_fail = _G["residual_fail"].get(k)
    eta_c_hat = canonical["eta_post_hat"]
    phase6 = (bool(residual_fail and eta_c_hat < 0.95)
              if residual_fail is not None and eta_c_hat is not None else None)

    plat = _G["knee"]["latents"][f"z{k}"]["plateau"]["mi_plat"]
    return {
        "latent": k,
        "audit_expected": AUDIT_EXPECTED[_G["run"]].get(k),
        "noise": noise,
        "ceiling": ceil,
        "ceiling_ok": ceiling_ok,
        "plat_ref": _f(plat),
        "ceiling_over_plat": _f(I / plat if plat else None),
        "residual_var": _f(res_var),
        "residual_var_over_noise": _f(res_ratio),
        "mi_mu_ref": _f(mi_ref), "mi_mu_ref_err": _f(mi_ref_err),
        "eta_post_mu": _f(mi_ref / I if (mi_ref is not None and ceiling_ok)
                          else None),
        "s_star_config": s_star_id,
        "candidates": out_c,
        "canonical_eta_post": canonical["eta_post"],
        "canonical_eta_post_se": canonical["eta_post_se"],
        "canonical_eta_post_hat": eta_c_hat,
        "canonical_eta_post_hat_se": canonical["eta_post_hat_se"],
        "s_star_eta_post": sstar["eta_post"] if sstar else None,
        "s_star_eta_post_hat": sstar["eta_post_hat"] if sstar else None,
        "residual_audit_failed": residual_fail,
        "phase6_needed": phase6,
    }


# ---- gate + outputs ----------------------------------------------------------

def gate_g3(latents_out: list, amp_idx: int) -> dict:
    viol = [{"latent": L["latent"], "config_ids": c["config_ids"],
             "mi": c["mi"], "mi_mu_ref": L["mi_mu_ref"],
             "I": L["ceiling"]["I"]}
            for L in latents_out for c in L["candidates"]
            if c["dpi_ok"] is False]
    amp = next((L for L in latents_out if L["latent"] == amp_idx), None)
    amp_block = None
    if amp is not None:
        eta_hat = amp["canonical_eta_post_hat"]
        verdict = None
        if eta_hat is not None:
            verdict = ("residual demoted to sub-noise detail "
                       "(eta_post_hat >= 0.95)"
                       if eta_hat >= 0.95 else
                       "residual is genuinely stored information "
                       "(eta_post_hat < 0.95) — Phase 6 matters")
        amp_block = {"latent": amp_idx, "I": amp["ceiling"]["I"],
                     "I_se": amp["ceiling"]["se"],
                     "eta_post_canonical": amp["canonical_eta_post"],
                     "eta_post_canonical_se": amp["canonical_eta_post_se"],
                     "eta_post_hat_canonical": eta_hat,
                     "eta_post_hat_canonical_se": amp["canonical_eta_post_hat_se"],
                     "eta_post_s_star": amp["s_star_eta_post"],
                     "eta_post_hat_s_star": amp["s_star_eta_post_hat"],
                     "verdict": verdict}
    reported = amp_block is not None and amp_block["eta_post_canonical"] is not None
    return {"dpi_pass": not viol, "dpi_violations": viol,
            "amplitude": amp_block,
            "pass": bool(not viol and reported)}


def fmt(x, prec=3):
    return "n/a" if x is None else f"{x:.{prec}f}"


def _sname(inputs, support):
    if inputs:
        return "{" + ", ".join(inputs) + "}"
    if support:
        return "{" + ", ".join(support) + "} (from expr)"
    return "?"


def to_markdown(run: str, latents: list, g3: dict, meta: dict) -> str:
    md = [f"# Posterior ceiling — `{run}` (roadmap Phase 5, gate G3)\n"]
    md.append(
        "The intrinsic ceiling I(Z_k; theta) = H(Z_k) − E[1/2 ln(2 pi e "
        "sigma_k^2)] from the cached encoder logvars (clamped to (−10, 10) "
        f"as in the model): H(Z_k) from {meta['m_draws']} posterior draws "
        "per row over T1 u T2, 1-D GMM (BIC over K <= 5) fit on half the "
        "draws, held-out cross-entropy on the rest, SE by joint row "
        "bootstrap (exact on the synthetic positive control, "
        "I_true = 1.124 vs 1.126 +/- 0.016). Numerators MI(Z_k; f) on a "
        "fresh posterior draw over T2 (confirmatory tier). Because the "
        "GMM-MI numerator over-estimates near-sufficient relations by ~7% "
        "on the same control, each latent also scores the same-estimator "
        "ceiling proxy MI(Z_k; mu_k): **eta_post = MI/I** (principled "
        "headline), **eta_post_hat = MI/MI(Z;mu)** (same-estimator ratio, "
        "shared bias cancels — drives the frozen 0.95 demotion rule and "
        "phase6_needed), DPI = MI(Z;f) <= MI(Z;mu) + 2 SE. eta_post_mu = "
        "MI(Z;mu)/I is the fraction of the analytic ceiling the estimator "
        "can even see (the practical top of the eta_post scale). "
        "Var(e1)/E[sigma^2] compares the Phase-3 residual to the posterior "
        "noise floor — the direct 'is the leftover modulation above the "
        "noise' readout.\n")

    md.append("## Noise table\n")
    md.append("| latent | role | E[sigma^2] | med sigma | Var(mu) | SNR "
              "| clamp frac | I_gauss |")
    md.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for L in latents:
        ns = L["noise"]
        md.append(f"| z{L['latent']} | {L['audit_expected']} "
                  f"| {ns['e_sigma2']:.3e} | {ns['median_sigma']:.3e} "
                  f"| {ns['var_mu']:.3f} | {ns['snr']:.3e} "
                  f"| {ns['clamp_frac']:.3f} | {ns['i_gauss']:.3f} |")

    md.append("\n## Intrinsic ceilings\n")
    md.append("| latent | H(Z) | H(Z\\|theta) | I(Z;theta) +/- SE | K "
              "| I_gauss | MI(Z;mu) | eta_post_mu | I_plat (SR) | I/plat "
              "| Var(e1)/E[s2] |")
    md.append("|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|")
    for L in latents:
        ce = L["ceiling"]
        md.append(f"| z{L['latent']} | {ce['H_z']:.3f} | {ce['H_cond']:.3f} "
                  f"| {ce['I']:.3f} +/- {ce['se']:.3f} | {ce['K_bic']} "
                  f"| {L['noise']['i_gauss']:.3f} | {fmt(L['mi_mu_ref'])} "
                  f"| {fmt(L['eta_post_mu'], 2)} | {fmt(L['plat_ref'])} "
                  f"| {fmt(L['ceiling_over_plat'], 2)} "
                  f"| {fmt(L['residual_var_over_noise'], 2)} |")

    for L in latents:
        md.append(f"\n## z{L['latent']} — {L['audit_expected']}\n")
        md.append(f"I(Z;theta) = {L['ceiling']['I']:.3f} +/- "
                  f"{L['ceiling']['se']:.3f} nat; MI(Z;mu) = "
                  f"{fmt(L['mi_mu_ref'])} +/- {fmt(L['mi_mu_ref_err'])}; "
                  f"canonical eta_post = {fmt(L['canonical_eta_post'])}, "
                  f"eta_post_hat = {fmt(L['canonical_eta_post_hat'])} +/- "
                  f"{fmt(L['canonical_eta_post_hat_se'])}; S* = "
                  f"`{L['s_star_config']}`, eta_post_hat = "
                  f"{fmt(L['s_star_eta_post_hat'])}; residual audit failed: "
                  f"{L['residual_audit_failed']} -> phase6_needed = "
                  f"{L['phase6_needed']}.\n")
        md.append("| candidate | S | \\|S\\| | expr | finite | MI(Z;f) +/- "
                  "| eta_post | eta_post_hat +/- | DPI |")
        md.append("|---|---|---:|---|---:|---|---:|---|---|")

        def key(c):
            first = {"canonical": 0, "reference": 1}.get(c["kind"], 2)
            return (first, c["size"] or 9, -(c["eta_post_hat"] or 0.0))

        s_star_id = L["s_star_config"]
        for c in sorted(L["candidates"], key=key):
            tag = c["kind"] if c["kind"] != "finalist" else ""
            if s_star_id in c["config_ids"]:
                tag = (tag + " S*").strip()
            dpi = ("ok" if c["dpi_ok"] else "**VIOLATION**") \
                if c["dpi_ok"] is not None else "n/a"
            md.append(f"| {tag} | {_sname(c['inputs'], c['support'])} "
                      f"| {c['size'] if c['size'] is not None else '—'} "
                      f"| `{c['expr'][:44]}` | {c['finite_frac_T2']:.2f} "
                      f"| {fmt(c['mi'])} +/- {fmt(c['mi_err'])} "
                      f"| {fmt(c['eta_post'])} "
                      f"| {fmt(c['eta_post_hat'])} +/- "
                      f"{fmt(c['eta_post_hat_se'])} | {dpi} |")

    md.append("\n# Gate G3\n")
    md.append(f"DPI: {'PASS' if g3['dpi_pass'] else 'FAIL'} "
              f"({len(g3['dpi_violations'])} violation(s)).")
    if g3["dpi_violations"]:
        for v in g3["dpi_violations"]:
            md.append(f"* z{v['latent']} {v['config_ids']}: MI "
                      f"{fmt(v['mi'])} > MI(Z;mu) {fmt(v['mi_mu_ref'])} "
                      f"(I = {fmt(v['I'])})")
    amp = g3["amplitude"]
    if amp is not None:
        md.append(f"\nAmplitude latent z{amp['latent']}: I = "
                  f"{fmt(amp['I'])} +/- {fmt(amp['I_se'])} nat; canonical "
                  f"eta_post = {fmt(amp['eta_post_canonical'])} +/- "
                  f"{fmt(amp['eta_post_canonical_se'])}, eta_post_hat = "
                  f"{fmt(amp['eta_post_hat_canonical'])} +/- "
                  f"{fmt(amp['eta_post_hat_canonical_se'])}; S* "
                  f"eta_post_hat = {fmt(amp['eta_post_hat_s_star'])}.")
        md.append(f"\n**Branch: {amp['verdict']}**")
    md.append(f"\n**Gate G3: {'PASS' if g3['pass'] else 'FAIL'}**")

    p6 = [f"z{L['latent']}" for L in latents if L["phase6_needed"]]
    md.append("\nPhase-6 scope (residual audit failed AND eta_post_hat "
              f"< 0.95): {', '.join(p6) if p6 else 'none'}.")
    md.append("\n---\n_Generated by `scripts/posterior_ceiling.py`._")
    return "\n".join(md) + "\n"


# ---- main --------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", required=True)
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--semantic-json", default=None)
    p.add_argument("--subsets-json", default=None)
    p.add_argument("--knee-json", default=None)
    p.add_argument("--audit-json", default=None)
    p.add_argument("--latents", nargs="*", type=int, default=None)
    p.add_argument("--jobs", type=int, default=6)
    p.add_argument("--m-draws", type=int, default=4)
    p.add_argument("--n-boot", type=int, default=500)
    p.add_argument("--max-samples-mi", type=int, default=5000)
    p.add_argument("--out", default=None)
    args = p.parse_args()

    model = next((m for m in MODELS if m[1] == args.run), None)
    if model is None:
        print(f"[FAIL] unknown run {args.run}")
        return 1
    _label, run, n_latents, amp_idx = model

    sem = json.loads(Path(args.semantic_json or
                          f"experiments/semantic_recurrence_{run}.json").read_text())
    subs = json.loads(Path(args.subsets_json or
                           f"experiments/subset_selection_{run}.json").read_text())
    knee = json.loads(Path(args.knee_json or
                           f"experiments/knee_readout_{run}.json").read_text())
    audit = json.loads(Path(args.audit_json or
                            f"experiments/sufficiency_audit_{run}.json").read_text())
    residual_fail = {}
    for L in audit["latents"]:
        rp = L.get("canonical", {}).get("residual_pass")
        residual_fail[L["latent"]] = (None if rp is None else not rp)

    run_dir = Path("models") / run
    mu = np.load(run_dir / "analysis" / "encoder_means_test.npy")
    logvar = np.load(run_dir / "analysis" / "encoder_logvars_test.npy")
    if mu.shape != logvar.shape:
        print(f"[FAIL] means {mu.shape} vs logvars {logvar.shape}")
        return 1
    theta = np.load(Path(args.dataset_dir) / "theta.npy")
    theta_all = theta[tiers.split_test_indices(args.dataset_dir)]

    _G.update({
        "run": run, "run_dir": str(run_dir),
        "semantic": sem, "finals": subs["finals"], "knee": knee,
        "residual_fail": residual_fail,
        "mu": mu, "logvar": logvar,
        "theta_t2": theta_all[tiers.T2],
        "m_draws": args.m_draws, "n_boot": args.n_boot,
        "max_samples_mi": args.max_samples_mi,
    })

    ks = args.latents if args.latents is not None else list(range(n_latents))
    if args.jobs > 1 and len(ks) > 1:
        with ProcessPoolExecutor(max_workers=min(args.jobs, len(ks))) as ex:
            latents_out = list(ex.map(latent_worker, ks))
    else:
        latents_out = [latent_worker(k) for k in ks]

    for L in latents_out:
        ce, ns = L["ceiling"], L["noise"]
        print(f"  z{L['latent']}: I={ce['I']:.3f}+/-{ce['se']:.3f} "
              f"(K={ce['K_bic']}, gauss {ns['i_gauss']:.3f}, "
              f"MI(Z;mu)={fmt(L['mi_mu_ref'])}, plat {fmt(L['plat_ref'])}) "
              f"eta_hat(canon)={fmt(L['canonical_eta_post_hat'])} "
              f"eta_hat(S*)={fmt(L['s_star_eta_post_hat'])} "
              f"res_var/noise={fmt(L['residual_var_over_noise'], 2)} "
              f"phase6={L['phase6_needed']}")

    g3 = gate_g3(latents_out, amp_idx)
    print(f"  G3: DPI {'PASS' if g3['dpi_pass'] else 'FAIL'}; "
          f"amplitude verdict: "
          f"{g3['amplitude']['verdict'] if g3['amplitude'] else 'n/a'} "
          f"-> {'PASS' if g3['pass'] else 'FAIL'}")

    meta = {"m_draws": args.m_draws, "n_boot": args.n_boot,
            "max_samples_mi": args.max_samples_mi, "seed_base": SEED_BASE}
    out = Path(args.out or f"experiments/posterior_ceiling_{run}")
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"run": run, **meta,
               "tiers": {"entropy": "T1+T2", "numerator": "T2"},
               "latents": latents_out, "gate_G3": g3,
               "generated_by": "scripts/posterior_ceiling.py"}
    out.with_suffix(".json").write_text(json.dumps(payload, indent=2))
    print(f"[write] {out.with_suffix('.json')}")
    out.with_suffix(".md").write_text(to_markdown(run, latents_out, g3, meta))
    print(f"[write] {out.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
