#!/usr/bin/env python
"""Second-stage discovery on structured residuals — Phase 6 consolidation
of docs/discovery_roadmap.md.

For every latent whose Phase-3 residual audit failed AND whose Phase-5
eta_post_hat < 0.95 (both models: all latents), 5-seed blind SR was run on
the cached residual e1 = mu_k − h(f1) with all 6 raw parameters exposed
(hpc/slurm_residual_sr.sh). This consolidator applies the frozen Phase 1–3
machinery to the residual fronts:

  1. residual knee/plateau (one-SE rule) per latent;
  2. semantic clustering + seed recurrence (frozen equivalence tests,
     eta floor 0.25 of the residual plateau) → the canonical secondary
     coordinate **f2** with its R_SR, support, sensitivity signature and
     constant-ratio pairs;
  3. hierarchical account z_k ~ h(f1) + g(f2): stage-2 cross-fitted
     calibration of e1 on f2 (T1), the combined prediction
     yhat = h(f1) + g(f2) with combined R² and MI(mu; yhat) on T1
     (eta_plat_comb against the Phase-1 plateau), and the posterior-ceiling
     ratios eta_post_comb = MI(Z; yhat)/I and eta_post_hat_comb =
     MI(Z; yhat)/MI(Z; mu) on T2 — the SAME posterior draw as Phase 5
     (seed convention imported from posterior_ceiling);
  4. stage-2 residual audit e2 = e1 − g(f2) (HistGBM R² + per-parameter
     GMM-MI vs permutation nulls, frozen section-0.3 rule) — does the
     hierarchy terminate at two levels?
  5. shuffled-residual controls (run_shuffled_control --target-npy):
     best control MI vs the TRUE residual = the metric-level null.

Definition of done (amplitude latents): f2 is a shape-sector coordinate —
support ⊆ {omega_b, omega_cdm, H0, n_s} — with its own recurrence.

Reads:  results/<run>/residual_sr/z<k>_seed*/report.json (+ shuffled_res_*),
        experiments/{knee_readout,posterior_ceiling}_<run>.json,
        models/<run>/analysis/{encoder_means_test.npy,residual_z<k>_v1.npy}
Writes: experiments/residual_sr_<run>.{md,json}

    python scripts/consolidate_residual_sr.py --run lcdm_tt_beta3e-4 --jobs 5
"""
import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

os.environ.setdefault("TQDM_DISABLE", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import _bootstrap  # noqa: F401,E402

import numpy as np  # noqa: E402

import posterior_ceiling as pc  # noqa: E402  (draw-seed convention + helpers)
import semantic_recurrence as sr_mod  # noqa: E402
from consolidate_allparams import AUDIT_EXPECTED, MODELS  # noqa: E402
from knee_readout import load_front  # noqa: E402

from cmb_lcdm_sr import calibrate, semantics, tiers  # noqa: E402
from cmb_lcdm_sr.mi import mutual_information_gmm  # noqa: E402

SHAPE_SECTOR = {"omega_b", "omega_cdm", "H0", "n_s"}  # sampled-basis labels

_G: dict = {}


def make_f1hat_extra_input(f1_str: str, mu_col: np.ndarray,
                           e1_all: np.ndarray, theta_t1: np.ndarray,
                           theta_t2: np.ndarray, half: np.ndarray):
    """(values_fn, grads_fn, diag) for f1hat = h_full(f1(θ)) as a θ-function.

    The Phase-3 cache wrote every non-T1 row of e1 through the full-T1
    calibration h_full — including the T0 rows the stage-2 search consumed —
    so the (f1(θ), mu − e1) pairs on T2 lie exactly on h_full's graph and a
    PCHIP through them reconstructs the function the search saw. grads_fn is
    the chain rule h'(f1)·∇_u f1, so the frozen clustering / signature /
    Sobol instruments apply verbatim to f1hat-bearing forms as θ-functions.
    diag: exactness on T2; the T1 rows carry the cross-fitted fold-h, whose
    scatter vs h_full is reported, not used. The caller registers.
    """
    from scipy.interpolate import PchipInterpolator

    f1_expr = semantics.parse_expr(f1_str)
    if f1_expr is None:
        raise RuntimeError(f"cannot parse canonical f1 '{f1_str}'")
    t1, t2 = tiers.T1, tiers.T2
    f1hat_all = mu_col - e1_all
    x2 = semantics.evaluate_on_theta(f1_expr, theta_t2)
    y2 = f1hat_all[t2]
    m2 = np.isfinite(x2) & np.isfinite(y2)
    xs, first = np.unique(x2[m2], return_index=True)
    pch = PchipInterpolator(xs, y2[m2][first], extrapolate=True)
    hprime = pch.derivative()

    def values_fn(theta):
        x = semantics.evaluate_on_theta(f1_expr, theta)
        out = np.full(x.shape, np.nan)
        fin = np.isfinite(x)
        out[fin] = pch(x[fin])
        return out

    def grads_fn(theta):
        x = semantics.evaluate_on_theta(f1_expr, theta)
        g1 = semantics.gradients_on_theta(f1_expr, theta, half)
        hp = np.full(x.shape, np.nan)
        fin = np.isfinite(x)
        hp[fin] = hprime(x[fin])
        return hp[:, None] * g1

    x1 = semantics.evaluate_on_theta(f1_expr, theta_t1)
    y1 = f1hat_all[t1]
    m1 = np.isfinite(x1) & np.isfinite(y1)
    fold = np.abs(pch(x1[m1]) - y1[m1]) if m1.any() else np.array([0.0])
    recon = np.abs(pch(x2[m2]) - y2[m2]) if m2.any() else np.array([0.0])
    diag = {"f1_expr": f1_str,
            "recon_max_err_t2": float(recon.max()),
            "fold_scatter_t1_max": float(fold.max()),
            "fold_scatter_t1_p99": float(np.quantile(fold, 0.99))}
    return values_fn, grads_fn, diag


def _register_f1hat(k: int) -> dict:
    """Interaction-aware variant: register f1hat for latent k (worker-side)."""
    semantics.clear_extra_inputs()
    e1_all = np.load(Path(_G["run_dir"]) / "analysis"
                     / f"residual_z{k}_v1.npy")
    values_fn, grads_fn, diag = make_f1hat_extra_input(
        _G["f1_exprs"][k], _G["mu"][:, k], e1_all,
        _G["theta_t1"], _G["theta_t2"], _G["half"])
    semantics.register_extra_input("f1hat", values_fn, grads_fn)
    return diag


def _f(v):
    return float(v) if v is not None and np.isfinite(v) else None


def _fl(arr):
    return None if arr is None else [_f(v) for v in arr]


def mi_scalar(a: np.ndarray, b: np.ndarray, seed: int = 0):
    """(mi, err) between two scalar columns on jointly finite rows."""
    m = np.isfinite(a) & np.isfinite(b)
    if m.mean() < 0.5 or m.sum() < 256:
        return None, None
    mi, err = mutual_information_gmm(a[m].reshape(-1, 1), b[m].reshape(-1, 1),
                                     return_uncertainty=True,
                                     max_samples=_G["max_samples_mi"],
                                     seed=seed)
    v, e = float(mi[0, 0]), float(err[0, 0])
    return (v, e) if np.isfinite(v) else (None, None)


# ---- per-latent worker -------------------------------------------------------

def latent_worker(k: int) -> dict:
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=1):
        return _latent_worker(k)


def _tick(k: int, stage: str, t0: float) -> float:
    """Stage-boundary progress print (streamed to the job log)."""
    t1 = time.time()
    print(f"[z{k}] {stage}: {t1 - t0:.0f}s", flush=True)
    return t1


def _latent_worker(k: int) -> dict:
    run = _G["run"]
    subdir = _G.get("subdir", "residual_sr")
    out = {"latent": k, "audit_expected": AUDIT_EXPECTED[run].get(k)}
    if _G.get("variant") == "ia":
        out["f1hat"] = _register_f1hat(k)
    t = time.time()

    seed_dirs = sorted(Path(_G["results_root"], run, subdir)
                       .glob(f"z{k}_seed*/report.json"))
    fronts = {int(p.parent.name.split("seed")[1]): load_front(p)
              for p in seed_dirs}
    out["n_seeds"] = len(fronts)
    if not fronts:
        out["error"] = f"no {subdir} reports"
        return out

    # 1–2: residual knee + semantic recurrence (frozen machinery)
    rec = sr_mod.latent_recurrence({subdir: fronts},
                                   plat_ref=sr_mod.family_knee(fronts)["plat"],
                                   anchors=_G["anchors"], half=_G["half"],
                                   eta_floor=_G["eta_floor"])
    knee = rec["families"][subdir]
    out["residual_plateau"] = {"mi_plat": _f(knee["plat"]),
                               "se": _f(knee["se"]),
                               "c_star": knee["c_star"],
                               "n_seeds": knee["n_seeds"]}
    out["clusters"] = [{kk: c[kk] for kk in
                        ("cluster", "representative", "rep_complexity",
                         "rep_support", "c_range", "n_forms", "n_rows",
                         "rep_linked", "pair_cohesion", "r_sr_headline")}
                       | {"best_mi": c["best_mi"],
                          "r_sr": c["r_sr"].get(subdir)}
                       for c in rec["clusters"][:8]]
    out["canonical_cluster"] = rec["canonical_cluster"]
    t = _tick(k, "recurrence", t)
    if rec["canonical_cluster"] is None:
        out["f2"] = None
        return out

    canon = next(c for c in rec["clusters"]
                 if c["cluster"] == rec["canonical_cluster"])
    f2_expr = canon["representative"]
    expr = semantics.parse_expr(f2_expr)
    grads = semantics.gradients_on_theta(expr, _G["anchors"], _G["half"])
    sig = semantics.sensitivity_signature(grads)
    theta_support = [s for s in canon["rep_support"]
                     if s not in semantics.EXTRA_INPUTS]
    f2 = {
        "expr": f2_expr,
        "complexity": canon["rep_complexity"],
        "support": canon["rep_support"],
        "theta_support": theta_support,
        "uses_f1hat": "f1hat" in canon["rep_support"],
        "r_sr": canon["r_sr_headline"],
        "signature": [float(v) for v in sig],
        "ratio_pairs": semantics.constant_ratio_pairs(grads, _G["half"]),
        "sobol_ST": _fl(semantics.sobol_indices(
            expr, _G["mid"], _G["half"], n_base=2048, seed=0)["ST"]),
        "shape_sector": bool(set(canon["rep_support"]) <= SHAPE_SECTOR),
        "theta_shape_sector": bool(set(theta_support) <= SHAPE_SECTOR),
    }
    out["f2"] = f2
    t = _tick(k, "signature+sobol", t)

    # 3: hierarchical account on T1
    t1, t2 = tiers.T1, tiers.T2
    mu_all = _G["mu"][:, k]
    e1_all = np.load(Path(_G["run_dir"]) / "analysis"
                     / f"residual_z{k}_v1.npy")
    theta_t1, theta_t2 = _G["theta_t1"], _G["theta_t2"]

    f2_t1 = semantics.evaluate_on_theta(expr, theta_t1)
    mi_f2_e1 = mi_scalar(f2_t1, e1_all[t1], seed=10 + k)
    f2["mi_vs_e1"], f2["mi_vs_e1_err"] = _f(mi_f2_e1[0]), _f(mi_f2_e1[1])

    cal2 = calibrate.crossfit_calibration(f2_t1, e1_all[t1],
                                          n_folds=5, seed=k)
    yhat1_t1 = mu_all[t1] - e1_all[t1]           # cross-fitted stage-1 pred
    yhat_comb_t1 = yhat1_t1 + cal2["yhat"]
    mu_t1 = mu_all[t1]
    fin = np.isfinite(yhat_comb_t1)
    var_mu = float(np.var(mu_t1[fin]))
    comb_r2 = (1.0 - float(np.mean((mu_t1[fin] - yhat_comb_t1[fin]) ** 2))
               / var_mu) if var_mu > 0 else None
    comb_mi, comb_mi_err = mi_scalar(mu_t1, yhat_comb_t1, seed=20 + k)

    plat = _G["knee"]["latents"][f"z{k}"]["plateau"]["mi_plat"]
    hier = {
        "r2_stage2_of_residual": _f(cal2["r2_cal"]),
        "combined_r2_vs_mu": _f(comb_r2),
        "combined_mi_vs_mu": _f(comb_mi),
        "combined_mi_err": _f(comb_mi_err),
        "eta_plat_comb": _f(comb_mi / plat if comb_mi else None),
        "plat_ref": _f(plat),
    }

    # posterior ratios on T2, reproducing the Phase-5 draw exactly
    lv_t2 = np.clip(_G["logvar"][t2, k], -pc.LOGVAR_CLAMP, pc.LOGVAR_CLAMP)
    z_num = (mu_all[t2] + np.exp(0.5 * lv_t2) *
             np.random.default_rng([pc.SEED_BASE, k, 7])
             .standard_normal(t2.stop - t2.start))
    f2_t2 = semantics.evaluate_on_theta(expr, theta_t2)
    g_full = cal2["h_full"]
    yhat_comb_t2 = np.where(np.isfinite(f2_t2),
                            (mu_all[t2] - e1_all[t2])
                            + g_full(np.nan_to_num(f2_t2)), np.nan)
    mi_comb_z, mi_comb_z_err, _ = pc.numerator_mi(
        z_num, yhat_comb_t2, max_samples=_G["max_samples_mi"], seed=30 + k)
    p5 = _G["p5"]["latents"][k]
    I, mi_mu = p5["ceiling"]["I"], p5["mi_mu_ref"]
    hier.update({
        "mi_z_comb": _f(mi_comb_z), "mi_z_comb_err": _f(mi_comb_z_err),
        "eta_post_comb": _f(mi_comb_z / I if (mi_comb_z and I) else None),
        "eta_post_hat_comb": _f(mi_comb_z / mi_mu
                                if (mi_comb_z and mi_mu) else None),
        "eta_post_hat_f1": p5["canonical_eta_post_hat"],
    })
    out["hierarchy"] = hier
    t = _tick(k, "hierarchy MIs", t)

    # 4: stage-2 residual audit (frozen rule)
    diag2 = calibrate.residual_diagnostics(
        cal2["residual"], theta_t1, n_folds=5, seed=k,
        n_perm_r2=_G["n_perm_r2"], compute_mi=True,
        n_perm_mi=_G["n_perm_mi"], max_samples_mi=_G["max_samples_mi"],
        gbm_max_iter=100, mi_jobs=_G.get("mi_jobs", 1))
    t = _tick(k, "stage2 audit", t)
    p975 = (np.quantile(diag2["mi_null"], 0.975, axis=0)
            if diag2["mi_null"] is not None else None)
    p975_max = (float(np.quantile(diag2["mi_null"].max(axis=1), 0.975))
                if diag2["mi_null"] is not None else None)
    mi_e2 = diag2["mi"]
    pass_r2 = bool(diag2["r2_res"] <= 0.05)
    pass_mi = (bool(np.nanmax(mi_e2) <= p975_max)
               if p975_max is not None else None)
    out["stage2_residual"] = {
        "r2_res": _f(diag2["r2_res"]),
        "r2_null_p975": _f(diag2["r2_null_p975"]),
        "mi": _fl(mi_e2), "mi_p975": _fl(p975),
        "mi_p975_max": _f(p975_max),
        "pass_r2": pass_r2, "pass_mi": pass_mi,
        "residual_pass": (bool(pass_r2 and pass_mi)
                          if pass_mi is not None else None),
        "loadings": [tiers.SAMPLED_LABELS[j] for j in range(6)
                     if p975 is not None and np.isfinite(mi_e2[j])
                     and mi_e2[j] > p975[j]],
    }
    return out


# ---- outputs -----------------------------------------------------------------

def fmt(x, prec=3):
    return "n/a" if x is None else f"{x:.{prec}f}"


def to_markdown(payload: dict) -> str:
    run = payload["run"]
    ia = payload.get("variant") == "ia"
    if ia:
        md = [f"# Residual SR (interaction-aware) — `{run}` "
              "(post-closure follow-up to roadmap Phase 6)\n"]
        md.append(
            "Blind second-stage SR on the SAME Phase-3 residual caches "
            "e1 = mu − h(f1) as Phase 6 (protocol budget, 5 seeds), with "
            "one change: the stage-1 prediction **f1hat = h(f1)** is "
            "exposed as a 7th input column, so the search can express the "
            "amplitude × shape interactions the additive hierarchy could "
            "not absorb (deviation D-DoD-z2). Consolidated with the frozen "
            "Phase 1–3 machinery; f1hat is registered as a semantics extra "
            "input — evaluated as the θ-function h_full(f1(θ)) "
            "reconstructed exactly from the T2 rows of the caches, with "
            "chain-rule u-gradients — so clustering, signatures, Sobol and "
            "supports treat f1hat-bearing forms as θ-functions. The "
            "combined account and the stage-2 residual audit are unchanged "
            "(g is a 1-D monotone recalibration of f2, which may itself "
            "contain f1hat — a multiplicative interaction lives inside "
            "f2). DoD (amplitude): the θ-part of f2's support is pure "
            "shape-sector (f1hat itself allowed), R_SR >= 0.6.\n")
    else:
        md = [f"# Residual SR — `{run}` (roadmap Phase 6)\n"]
        md.append(
            "Blind second-stage SR on the Phase-3 residual caches e1 = mu − "
            "h(f1) (all-6 inputs, protocol budget, 5 seeds), consolidated with "
            "the frozen Phase 1–3 machinery. f2 = canonical residual coordinate "
            "(most recurrent cluster at the residual knee). Hierarchical "
            "account: combined yhat = h(f1) + g(f2), both stages cross-fitted "
            "on T1; eta_post ratios on T2 against the Phase-5 ceiling (same "
            "posterior draw). Stage-2 residual audited with the frozen rule "
            "(R2 <= 0.05 AND max MI <= null p97.5) — PASS means the hierarchy "
            "terminates at two levels. Shuffled-residual controls give the "
            "residual-MI null.\n")

    shape_col = "theta-shape | f1hat" if ia else "shape-sector"
    md.append("| latent | role | res plat +/- SE | c* | f2 (rep) | support "
              f"| {shape_col} | R_SR | R2 st2(e1) | comb R2(mu) "
              "| eta_plat_comb | eta_hat f1 -> f1+f2 | st2 residual |")
    md.append("|---|---|---|---:|---|---|---|" + ("---|" if ia else "")
              + "---:|---:|---:|---:|---|---|")
    for L in payload["latents"]:
        if L.get("error") or L.get("f2") is None:
            md.append(f"| z{L['latent']} | {L['audit_expected']} | — | — "
                      f"| {L.get('error', 'no recurrent cluster')} "
                      "| — | — | " + ("— | " if ia else "")
                      + "— | — | — | — | — | — |")
            continue
        f2, h, s2 = L["f2"], L["hierarchy"], L["stage2_residual"]
        rp = L["residual_plateau"]
        verdict = ("PASS" if s2["residual_pass"]
                   else "FAIL" if s2["residual_pass"] is False else "n/a")
        shape_cell = (f"{f2['theta_shape_sector']} | {f2['uses_f1hat']}"
                      if ia else f"{f2['shape_sector']}")
        md.append(
            f"| z{L['latent']} | {L['audit_expected']} "
            f"| {fmt(rp['mi_plat'])} +/- {fmt(rp['se'])} | {rp['c_star']} "
            f"| `{f2['expr'][:36]}` | {{{', '.join(f2['support'])}}} "
            f"| {shape_cell} | {f2['r_sr']:.2f} "
            f"| {fmt(h['r2_stage2_of_residual'])} "
            f"| {fmt(h['combined_r2_vs_mu'])} | {fmt(h['eta_plat_comb'])} "
            f"| {fmt(h['eta_post_hat_f1'])} -> {fmt(h['eta_post_hat_comb'])} "
            f"| {verdict} ({', '.join(s2['loadings']) or 'none'}) |")

    base = payload.get("baseline_additive")
    if ia and base:
        md.append("\n## Against the additive Phase-6 account\n")
        md.append("| latent | comb R2(mu) add -> ia | eta_hat_comb add -> ia "
                  "| st2 residual add -> ia | additive f2 |")
        md.append("|---|---|---|---|---|")
        for L in payload["latents"]:
            b = base.get(str(L["latent"])) or base.get(L["latent"])
            if b is None or L.get("f2") is None:
                continue
            h, s2 = L["hierarchy"], L["stage2_residual"]

            def _pf(v):
                return ("PASS" if v else "FAIL" if v is False else "n/a")
            md.append(
                f"| z{L['latent']} "
                f"| {fmt(b['combined_r2_vs_mu'])} -> "
                f"{fmt(h['combined_r2_vs_mu'])} "
                f"| {fmt(b['eta_post_hat_comb'])} -> "
                f"{fmt(h['eta_post_hat_comb'])} "
                f"| {_pf(b['st2_pass'])} -> {_pf(s2['residual_pass'])} "
                f"| `{(b['f2'] or '')[:36]}` |")

    for L in payload["latents"]:
        if L.get("error") or L.get("f2") is None:
            continue
        f2 = L["f2"]
        md.append(f"\n## z{L['latent']} — {L['audit_expected']}\n")
        md.append(f"f2 = `{f2['expr']}` (c={f2['complexity']}, support "
                  f"{{{', '.join(f2['support'])}}}, R_SR {f2['r_sr']:.2f}, "
                  f"MI vs e1 = {fmt(f2['mi_vs_e1'])} +/- "
                  f"{fmt(f2['mi_vs_e1_err'])})")
        fh = L.get("f1hat")
        if ia and fh:
            md.append(f"\nf1hat = h_full(`{fh['f1_expr']}`): T2 "
                      f"reconstruction max err {fh['recon_max_err_t2']:.2e}; "
                      f"T1 fold scatter p99 {fh['fold_scatter_t1_p99']:.2e} "
                      f"(max {fh['fold_scatter_t1_max']:.2e})")
        sig = f2["signature"]
        md.append("\nSignature g_j: " + ", ".join(
            f"{lab} {sig[j]:.2f}" for j, lab in
            enumerate(tiers.SAMPLED_LABELS) if sig[j] > 0.01))
        if f2["ratio_pairs"]:
            for pr in f2["ratio_pairs"]:
                md.append(f"* constant ratio ({pr['pair'][0]}, "
                          f"{pr['pair'][1]}): r_raw = {pr['r_raw']:+.4f} "
                          f"(cv {pr['cv']:.3f})")
        md.append("\nTop clusters:\n")
        md.append("| cluster | representative | C | support | R_SR | best MI |")
        md.append("|---:|---|---:|---|---:|---:|")
        for c in L["clusters"][:5]:
            md.append(f"| {c['cluster']} | `{c['representative'][:40]}` "
                      f"| {c['rep_complexity']} "
                      f"| {{{', '.join(c['rep_support'])}}} "
                      f"| {c['r_sr_headline']:.2f} "
                      f"| {c['best_mi']['mi']:.3f} |")

    if payload["controls"]:
        md.append("\n## Shuffled-residual controls\n")
        md.append("| target | shuffle seed | best MI vs TRUE residual |")
        md.append("|---|---:|---:|")
        for c in payload["controls"]:
            md.append(f"| {c['target_label']} | {c['shuffle_seed']} "
                      f"| {fmt(c['best_mi_unshuffled'])} |")

    dod = payload["dod_amplitude"]
    if dod is not None and dod.get("variant") == "ia":
        md.append(f"\n**Definition of done, ia (amplitude z{dod['latent']}): "
                  f"theta-support pure shape = {dod['theta_shape_sector']}, "
                  f"uses f1hat = {dod['uses_f1hat']}, R_SR = "
                  f"{fmt(dod['r_sr'], 2)} -> "
                  f"{'MET' if dod['met'] else 'NOT MET'}**")
    elif dod is not None:
        md.append(f"\n**Definition of done (amplitude z{dod['latent']}): "
                  f"f2 shape-sector = {dod['shape_sector']}, R_SR = "
                  f"{fmt(dod['r_sr'], 2)} -> "
                  f"{'MET' if dod['met'] else 'NOT MET'}**")
    md.append("\n---\n_Generated by `scripts/consolidate_residual_sr.py`._")
    return "\n".join(md) + "\n"


# ---- main --------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", required=True)
    p.add_argument("--results-root", default="results")
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--latents", nargs="*", type=int, default=None)
    p.add_argument("--jobs", type=int, default=6)
    p.add_argument("--mi-jobs", type=int, default=1,
                   help="Inner process pool for the stage-2 permutation-null "
                        "MI calls (bit-identical to serial; see "
                        "calibrate.residual_diagnostics).")
    p.add_argument("--eta-floor", type=float, default=0.25)
    p.add_argument("--n-perm-mi", type=int, default=39)
    p.add_argument("--n-perm-r2", type=int, default=10)
    p.add_argument("--max-samples-mi", type=int, default=5000)
    p.add_argument("--variant", choices=["", "ia"], default="",
                   help="'' = the frozen Phase-6 additive consolidation. "
                        "'ia' = interaction-aware follow-up: fronts from "
                        "results/<run>/residual_sr_ia (stage-1 prediction "
                        "f1hat exposed as a 7th input), f1hat registered as "
                        "a semantics extra input with chain-rule gradients, "
                        "DoD judged on the θ-support (f1hat allowed).")
    p.add_argument("--out", default=None)
    args = p.parse_args()

    model = next((m for m in MODELS if m[1] == args.run), None)
    if model is None:
        print(f"[FAIL] unknown run {args.run}")
        return 1
    _label, run, n_latents, amp_idx = model
    subdir = "residual_sr_ia" if args.variant == "ia" else "residual_sr"

    # the residual family is the canonical family for R_SR headlines here
    sr_mod.CANONICAL_FAMILIES = [subdir]

    f1_exprs = None
    if args.variant == "ia":
        rec_json = json.loads(
            Path(f"experiments/semantic_recurrence_{run}.json").read_text())
        f1_exprs = {}
        for name, L in rec_json["latents"].items():
            ci = L.get("canonical_cluster")
            f1_exprs[int(name[1:])] = (L["clusters"][ci]["representative"]
                                       if ci is not None else None)

    knee = json.loads(Path(f"experiments/knee_readout_{run}.json").read_text())
    p5_raw = json.loads(Path(f"experiments/posterior_ceiling_{run}.json")
                        .read_text())
    p5 = {"latents": {L["latent"]: L for L in p5_raw["latents"]}}

    run_dir = Path("models") / run
    mu = np.load(run_dir / "analysis" / "encoder_means_test.npy")
    logvar = np.load(run_dir / "analysis" / "encoder_logvars_test.npy")
    theta = np.load(Path(args.dataset_dir) / "theta.npy")
    theta_all = theta[tiers.split_test_indices(args.dataset_dir)]
    mid, half = tiers.load_prior_box(args.dataset_dir)

    _G.update({
        "run": run, "run_dir": str(run_dir),
        "results_root": args.results_root,
        "variant": args.variant, "subdir": subdir, "f1_exprs": f1_exprs,
        "knee": knee, "p5": p5,
        "mu": mu, "logvar": logvar,
        "theta_t1": theta_all[tiers.T1], "theta_t2": theta_all[tiers.T2],
        "anchors": tiers.anchor_theta(args.dataset_dir),
        "mid": mid, "half": half,
        "eta_floor": args.eta_floor,
        "n_perm_mi": args.n_perm_mi, "n_perm_r2": args.n_perm_r2,
        "max_samples_mi": args.max_samples_mi, "mi_jobs": args.mi_jobs,
    })

    def _summary(L: dict) -> None:
        if L.get("error") or L.get("f2") is None:
            print(f"  z{L['latent']}: {L.get('error', 'no canonical cluster')}",
                  flush=True)
            return
        f2, h, s2 = L["f2"], L["hierarchy"], L["stage2_residual"]
        print(f"  z{L['latent']}: f2=`{f2['expr'][:40]}` "
              f"S={{{','.join(f2['support'])}}} shape={f2['shape_sector']} "
              f"R_SR={f2['r_sr']:.2f} R2st2={fmt(h['r2_stage2_of_residual'])} "
              f"combR2={fmt(h['combined_r2_vs_mu'])} "
              f"eta_hat {fmt(h['eta_post_hat_f1'])}->"
              f"{fmt(h['eta_post_hat_comb'])} "
              f"st2res={'PASS' if s2['residual_pass'] else 'FAIL'}"
              f"({','.join(s2['loadings']) or '-'})", flush=True)

    ks = args.latents if args.latents is not None else list(range(n_latents))
    latents_out = []
    if args.jobs > 1 and len(ks) > 1:
        with ProcessPoolExecutor(max_workers=min(args.jobs, len(ks))) as ex:
            futures = {ex.submit(latent_worker, k): k for k in ks}
            for fut in as_completed(futures):
                L = fut.result()
                _summary(L)
                latents_out.append(L)
        latents_out.sort(key=lambda L: L["latent"])
    else:
        for k in ks:
            L = latent_worker(k)
            _summary(L)
            latents_out.append(L)

    controls = []
    for path in sorted(Path(args.results_root, run, subdir)
                       .glob("shuffled_*/report.json")):
        rep = json.loads(path.read_text())
        controls.append({
            "target_label": rep.get("target_label"),
            "shuffle_seed": rep.get("shuffle_seed"),
            "best_mi_unshuffled": _f(rep.get("best_mi_val_unshuffled_eval")),
        })

    dod = None
    amp = next((L for L in latents_out if L["latent"] == amp_idx), None)
    if amp is not None and amp.get("f2") is not None:
        if args.variant == "ia":
            dod = {"latent": amp_idx, "variant": "ia",
                   "theta_shape_sector": amp["f2"]["theta_shape_sector"],
                   "uses_f1hat": amp["f2"]["uses_f1hat"],
                   "r_sr": amp["f2"]["r_sr"],
                   "met": bool(amp["f2"]["theta_shape_sector"]
                               and amp["f2"]["r_sr"] >= 0.6)}
            print(f"  DoD-ia (amplitude): theta-shape-sector="
                  f"{dod['theta_shape_sector']} uses_f1hat="
                  f"{dod['uses_f1hat']} R_SR={dod['r_sr']:.2f} -> "
                  f"{'MET' if dod['met'] else 'NOT MET'}")
        else:
            dod = {"latent": amp_idx,
                   "shape_sector": amp["f2"]["shape_sector"],
                   "r_sr": amp["f2"]["r_sr"],
                   "met": bool(amp["f2"]["shape_sector"]
                               and amp["f2"]["r_sr"] >= 0.6)}
            print(f"  DoD (amplitude): shape-sector={dod['shape_sector']} "
                  f"R_SR={dod['r_sr']:.2f} -> "
                  f"{'MET' if dod['met'] else 'NOT MET'}")

    baseline = None
    if args.variant == "ia":
        base_path = Path(f"experiments/residual_sr_{run}.json")
        if base_path.exists():
            bj = json.loads(base_path.read_text())
            baseline = {L["latent"]: {
                "f2": (L.get("f2") or {}).get("expr"),
                "shape_sector": (L.get("f2") or {}).get("shape_sector"),
                "combined_r2_vs_mu":
                    (L.get("hierarchy") or {}).get("combined_r2_vs_mu"),
                "eta_post_hat_comb":
                    (L.get("hierarchy") or {}).get("eta_post_hat_comb"),
                "st2_pass":
                    (L.get("stage2_residual") or {}).get("residual_pass"),
            } for L in bj["latents"]}

    suffix = "_ia" if args.variant == "ia" else ""
    out = Path(args.out or f"experiments/residual_sr{suffix}_{run}")
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"run": run, "variant": args.variant, "subdir": subdir,
               "eta_floor": args.eta_floor,
               "n_perm_mi": args.n_perm_mi, "n_perm_r2": args.n_perm_r2,
               "latents": latents_out, "controls": controls,
               "dod_amplitude": dod, "baseline_additive": baseline,
               "generated_by": "scripts/consolidate_residual_sr.py"}
    out.with_suffix(".json").write_text(json.dumps(payload, indent=2))
    print(f"[write] {out.with_suffix('.json')}")
    out.with_suffix(".md").write_text(to_markdown(payload))
    print(f"[write] {out.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
