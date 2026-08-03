#!/usr/bin/env python
"""Sensitivity signatures + calibrated sufficiency audit — Phase 3 of
docs/discovery_roadmap.md (gate G1).

The answer-agnostic replacement for the r-ratio and textbook regexes: for
each latent's **canonical coordinate** f* (Phase-2 semantic recurrence):

  1. sensitivity signature g_j = normalised E|df/du_j| on the 2048 T1
     anchors, plus first-/total-order Sobol indices on the prior box;
  2. constant-ratio pairs (the answer-agnostic -2 detector,
     ``semantics.constant_ratio_pairs``), with the legacy midpoint
     ``amp_ratio`` kept as a cross-check column;
  3. calibrated sufficiency: 5-fold cross-fitted monotone-PCHIP h on T1,
     residual e_k = mu_k - h(f*), diagnostics R2_res(e <- theta) (HistGBM,
     single-threaded) and per-parameter GMM-MI with permutation nulls.
     Frozen pass rule (roadmap section 0.3): R2_res <= 0.05 AND
     max_j MI(e; theta_j) <= 97.5th percentile of the permutation null of
     the max (per-parameter nulls are reported alongside).
     e_k over all 50k test rows (T1 rows cross-fitted, the rest through the
     full-T1 h) is cached to models/<run>/analysis/residual_z<k>_v1.npy for
     Phase 6;
  4. the same audit on the best shuffled-control expressions evaluated
     against the TRUE latent — the metric-level negative control.

**Gate G1** (amplitude latents; the 2-input reference study's raw fronts are
not in this repo's results/, so the stored reference ceilings 0.822 / 1.196
nat and r-readouts serve as the frozen comparison values, per section 0.2's
"pre-Phase-4 proxy"): the audit also runs on f_2var — the best front member
with support {A_s, tau} and c <= 10 (the knee slice) — and checks
  (1) the {A_s,tau} knee-slice coordinate recurs: the best slice member of
      each allparams seed is semantically equivalent to f_2var in >= 0.8 of
      seeds, and f_2var's support is exactly {tau, ln10As}. (Documented
      deviation from the "canonical cluster support = {A_s, tau}" wording:
      on TT the slice ceiling 0.822 nat sits BELOW the Phase-2 eta-floor
      0.25 x 4.18, so slice forms are structurally excluded from the
      canonical cluster — a property of the all-params design knowable from
      the amplitude sector alone. Whether f_2var joins the canonical
      cluster is still reported.)
  (2) the (tau, ln10As) direction reads r = -2.0 +/- 0.05 on the
      **latent-level linear readout** r_lin = b_tau/b_lnAs (OLS of mu_k on
      theta over T1 — answer-agnostic, and the instrument behind the stored
      reference values). The form-level constant-ratio detection stays at
      the frozen cv < 5% and is reported as-is: a Taylor-surrogate front
      (TT: A_s*(tau-0.598), ratio-field cv 5.9%, slope -1.90) genuinely is
      not a fixed linear combination and cannot read -2.0 by any
      convention; the literal exponential (EE) is, at exactly -2.000.
  (3) eta_S = MI(f_2var; mu_k on T1) / reference ceiling >= 0.95;
  (4) the residual audit FAILS in the expected direction (R2_res > 0.05
      with shape-sector parameters above their nulls).

Draft latent cards v0 (statuses per section 0.3, with the Phase-4/5/7
components marked pending) are assembled into the deliverable.

Reads:  experiments/{semantic_recurrence,knee_readout}_<run>.json,
        models/<run>/analysis/encoder_means_test.npy, results/<run>/...
Writes: experiments/sufficiency_audit_<run>.{md,json}
        models/<run>/analysis/residual_z<k>_v1.npy

    python scripts/sufficiency_audit.py --run lcdm_tt_beta3e-4 --jobs 6
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

from consolidate_allparams import (AUDIT_EXPECTED, MODELS,  # noqa: E402
                                   REFERENCE_2INPUT, REFERENCE_OLS_R,
                                   amp_ratio, vars_used)
from knee_readout import DEFAULT_SUBDIRS, discover_families, load_front  # noqa: E402

from cmb_lcdm_sr import calibrate, semantics, tiers  # noqa: E402
from cmb_lcdm_sr.mi import mutual_information_gmm  # noqa: E402

SHAPE_PARAMS = ["omega_b", "omega_cdm", "H0", "n_s"]  # sampled-basis names

# worker-shared state (populated in main, inherited by fork)
_G: dict = {}


# ---- helpers ----------------------------------------------------------------

def _f(v):
    """float(v) if finite else None — keeps the JSON standard-parseable."""
    return float(v) if v is not None and np.isfinite(v) else None


def _fl(arr):
    return None if arr is None else [_f(v) for v in arr]


def eval_masked(expr, theta):
    v = semantics.evaluate_on_theta(expr, theta)
    return v, np.isfinite(v)


def mi_vs_latent(fvals: np.ndarray, mu_col: np.ndarray, seed: int = 0):
    """(mi, err) of f vs mu on jointly finite rows (None if too thin)."""
    m = np.isfinite(fvals) & np.isfinite(mu_col)
    if m.mean() < 0.5:
        return None, None
    mi, err = mutual_information_gmm(mu_col[m].reshape(-1, 1),
                                     fvals[m].reshape(-1, 1),
                                     return_uncertainty=True,
                                     max_samples=_G["max_samples_mi"],
                                     seed=seed)
    return float(mi[0, 0]), float(err[0, 0])


def stitch_residual(mu_col: np.ndarray, fvals_all: np.ndarray,
                    t1: slice, oof_yhat_t1: np.ndarray, h_full) -> np.ndarray:
    """e over all rows: T1 gets cross-fitted OOF predictions, the rest h_full."""
    yhat = np.full(mu_col.shape, np.nan)
    finite = np.isfinite(fvals_all)
    yhat[finite] = h_full(fvals_all[finite])
    yhat[t1] = oof_yhat_t1
    return mu_col - yhat


def audit_coordinate(expr_str: str, k: int, seed: int = 0,
                     with_nulls: bool = True) -> dict:
    """Full Phase-3 audit of one coordinate against latent k."""
    expr = semantics.parse_expr(expr_str)
    if expr is None:
        return {"expr": expr_str, "error": "unparseable"}
    anchors, half, mid = _G["anchors"], _G["half"], _G["mid"]
    theta_t1, mu = _G["theta_t1"], _G["mu"]
    mu_t1 = mu[tiers.T1, k]

    grads = semantics.gradients_on_theta(expr, anchors, half)
    sig = semantics.sensitivity_signature(grads)
    sob = semantics.sobol_indices(expr, mid, half, n_base=2048, seed=0)
    pairs = semantics.constant_ratio_pairs(grads, half)

    fvals_t1, m1 = eval_masked(expr, theta_t1)
    mi_f, mi_f_err = mi_vs_latent(fvals_t1, mu_t1, seed=seed)

    cal = calibrate.crossfit_calibration(fvals_t1, mu_t1, n_folds=5, seed=seed)
    diag = calibrate.residual_diagnostics(
        cal["residual"], theta_t1, n_folds=5, seed=seed,
        n_perm_r2=_G["n_perm_r2"] if with_nulls else 0,
        compute_mi=True, n_perm_mi=_G["n_perm_mi"] if with_nulls else 0,
        max_samples_mi=_G["max_samples_mi"], gbm_max_iter=_G["gbm_max_iter"])

    mi_e = diag["mi"]
    pass_r2 = diag["r2_res"] <= 0.05
    p975_param = p975_max = None
    pass_mi = loaded = None
    if diag["mi_null"] is not None:
        p975_param = np.quantile(diag["mi_null"], 0.975, axis=0)
        p975_max = float(np.quantile(diag["mi_null"].max(axis=1), 0.975))
        pass_mi = bool(np.nanmax(mi_e) <= p975_max)
        loaded = [tiers.SAMPLED_LABELS[j] for j in range(6)
                  if np.isfinite(mi_e[j]) and mi_e[j] > p975_param[j]]

    return {
        "expr": expr_str,
        "support": [lab for lab, s in
                    zip(tiers.SAMPLED_LABELS, sig) if s > 0.01],
        "signature": [float(v) for v in sig],
        "sobol_S1": _fl(sob["S1"]),
        "sobol_ST": _fl(sob["ST"]),
        "sobol_n_eff": sob["n_effective"],
        "ratio_pairs": pairs,
        "amp_ratio_legacy": _f(amp_ratio(expr_str)),
        "finite_frac_T1": float(m1.mean()),
        "mi_f": _f(mi_f), "mi_f_err": _f(mi_f_err),
        "r2_cal": _f(cal["r2_cal"]),
        "r2_res": _f(diag["r2_res"]),
        "r2_null_p975": _f(diag["r2_null_p975"]),
        "mi_res": _fl(mi_e),
        "mi_res_err": _fl(diag["mi_err"]),
        "mi_res_p975_param": _fl(p975_param),
        "mi_res_p975_max": _f(p975_max),
        "pass_r2": bool(pass_r2),
        "pass_mi": pass_mi,
        "residual_pass": (bool(pass_r2 and pass_mi)
                          if pass_mi is not None else None),
        "residual_loadings": loaded,
        "_cal": cal,           # stripped before JSON; used for the cache
    }


def draft_status(r_sr: float, eta_plat, residual_pass) -> str:
    """Section 0.3 statuses restricted to the components available today."""
    if residual_pass and r_sr >= 0.8 and (eta_plat or 0.0) >= 0.95:
        return "interpreted (draft)"
    if r_sr >= 0.6 and residual_pass is False:
        return "primarily interpreted (draft)"
    return "unresolved (draft)"


# ---- per-latent worker ------------------------------------------------------

def latent_worker(k: int) -> dict:
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=1):
        return _latent_worker(k)


def _latent_worker(k: int) -> dict:
    run = _G["run"]
    sem = _G["semantic"]["latents"][f"z{k}"]
    canon = next(c for c in sem["clusters"]
                 if c["cluster"] == sem["canonical_cluster"])
    knee_lat = _G["knee"]["latents"][f"z{k}"]

    out = {"latent": k, "audit_expected": AUDIT_EXPECTED[run].get(k),
           "canonical_expr": canon["representative"],
           "r_sr": canon["r_sr_headline"],
           "plat_ref": knee_lat["plateau"]["mi_plat"]}

    res = audit_coordinate(canon["representative"], k, seed=k)
    cal = res.pop("_cal", None)
    out["canonical"] = res
    if "error" in res:
        return out
    out["canonical"]["eta_plat"] = _f((res["mi_f"] / out["plat_ref"])
                                      if res["mi_f"] is not None else None)

    # residual cache over all 50k rows (T1 cross-fitted, rest through h_full)
    expr = semantics.parse_expr(canon["representative"])
    fvals_all, _ = eval_masked(expr, _G["theta_all"])
    e_all = stitch_residual(_G["mu"][:, k], fvals_all, tiers.T1,
                            cal["yhat"], cal["h_full"])
    cache = Path(_G["run_dir"]) / "analysis" / f"residual_z{k}_v1.npy"
    np.save(cache, e_all)
    out["residual_cache"] = str(cache)
    out["status"] = draft_status(out["r_sr"], out["canonical"]["eta_plat"],
                                 res["residual_pass"])

    if k == _G["amp_idx"]:
        out["g1"] = g1_audit(k, canon)
        out["controls"] = control_audit(k)
    return out


def g1_audit(k: int, canon: dict) -> dict:
    """Gate-G1 extras on the amplitude latent (see module docstring)."""
    run = _G["run"]
    ref = REFERENCE_2INPUT[run]

    # best {A_s, tau}-supported front member at the knee slice (c <= 10)
    def slice_rows(front):
        return [(c, mi, err, e) for c, mi, err, e in front["rows"]
                if c <= 10 and set(vars_used(e)) <= {"A_s", "tau"}
                and set(vars_used(e))]

    best = None
    for fam, latents in _G["fronts"].items():
        for s, front in latents.get(k, {}).items():
            for c, mi, err, e in slice_rows(front):
                if best is None or mi > best[0]:
                    best = (mi, err, c, e)
    g1 = {"reference_ceiling": ref["mi"], "reference_form": ref["form"],
          "reference_ols_r": REFERENCE_OLS_R[run]}
    if best is None:
        g1["error"] = "no {A_s,tau}-supported form at c<=10 on any front"
        return g1

    mi0, err0, c0, expr0 = best
    g1["f_2var"] = {"expr": expr0, "complexity": c0,
                    "mi_stored": mi0, "mi_stored_err": err0}
    res = audit_coordinate(expr0, k, seed=100 + k)
    res.pop("_cal", None)
    g1["f_2var"].update(res)

    # slice recurrence: per allparams seed, is its best slice member
    # semantically equivalent to f_2var?
    f0 = _form(expr0)
    slice_hits, slice_members = {}, {}
    ap = _G["fronts"].get("allparams", {}).get(k, {})
    for s, front in ap.items():
        rows = slice_rows(front)
        if not rows:
            continue
        _c, _mi, _err, e = max(rows, key=lambda r: r[1])
        slice_members[s] = e
        f = _form(e)
        if f is not None and f0 is not None and semantics.same_cluster(f, f0):
            slice_hits[s] = e
    g1["slice_members"] = slice_members
    g1["slice_recurrence"] = (len(slice_hits) / len(ap)) if ap else 0.0

    rep_form = _form(canon["representative"])
    in_cluster = (f0 is not None and rep_form is not None
                  and semantics.same_cluster(f0, rep_form))

    # latent-level linear readout of the amplitude direction (the stored
    # reference instrument): OLS mu_k ~ theta on T1, r_lin = b_tau/b_lnAs
    th, mu_t1 = _G["theta_t1"], _G["mu"][tiers.T1, k]
    X = np.column_stack([np.ones(len(th)), th])
    beta = np.linalg.lstsq(X, mu_t1, rcond=None)[0]
    r_lin = _f(beta[4] / beta[5] if abs(beta[5]) > 1e-300 else None)
    g1["r_lin"] = r_lin

    tau_pair = next((p for p in res.get("ratio_pairs", [])
                     if set(p["pair"]) == {"tau", "ln10As"}), None)
    eta_s = _f((res["mi_f"] / ref["mi"]) if res.get("mi_f") else None)
    shape_loaded = sorted(set(res.get("residual_loadings") or [])
                          & set(SHAPE_PARAMS))

    g1["bullets"] = {
        "b1_support_and_recurrence": {
            "in_canonical_cluster": bool(in_cluster),
            "support": res.get("support"),
            "slice_recurrence": g1["slice_recurrence"],
            "pass": bool(set(res.get("support", [])) == {"tau", "ln10As"}
                         and g1["slice_recurrence"] >= 0.8),
        },
        "b2_constant_ratio": {
            "pair_found": tau_pair is not None,
            "r_form": tau_pair["r_raw"] if tau_pair else None,
            "cv_form": tau_pair["cv"] if tau_pair else None,
            "amp_ratio_legacy": res.get("amp_ratio_legacy"),
            "r_lin": r_lin,
            "pass": bool(r_lin is not None and abs(r_lin + 2.0) <= 0.05),
        },
        "b3_eta_s": {"eta_s": eta_s,
                     "pass": bool(eta_s is not None and eta_s >= 0.95)},
        "b4_residual_fails_structured": {
            "r2_res": res.get("r2_res"),
            "shape_loadings": shape_loaded,
            "pass": bool((res.get("r2_res") or 0.0) > 0.05
                         and len(shape_loaded) > 0),
        },
    }
    g1["pass"] = all(b["pass"] for b in g1["bullets"].values())
    return g1


def control_audit(k: int) -> list:
    """Best shuffled-control expressions audited against the TRUE latent."""
    out = []
    for path in sorted(Path(_G["results_root"], _G["run"], "allparams")
                       .glob(f"shuffled_z{k}_s*/report.json")):
        rep = json.loads(path.read_text())
        expr = rep.get("best_expression")
        if not expr:
            continue
        res = audit_coordinate(expr, k, seed=200, with_nulls=False)
        res.pop("_cal", None)
        out.append({"shuffle_seed": rep.get("shuffle_seed"),
                    "expr": expr,
                    "mi_true": res.get("mi_f"),
                    "r2_cal": res.get("r2_cal"),
                    "r2_res": res.get("r2_res")})
    return out


def _form(expr_str: str):
    expr = semantics.parse_expr(expr_str)
    if expr is None:
        return None
    return semantics.FormEval(
        expr_str=expr_str, expr=expr, canonical=expr_str,
        values=semantics.evaluate_on_theta(expr, _G["anchors"]),
        grads_u=semantics.gradients_on_theta(expr, _G["anchors"], _G["half"]))


# ---- outputs ----------------------------------------------------------------

def bar(x: float, width: int = 12) -> str:
    n = int(round(x * width))
    return "#" * n + "." * (width - n)


def fmt(x, prec=3):
    return "n/a" if x is None else f"{x:.{prec}f}"


def coord_md(md: list, res: dict, plat_ref=None):
    md.append("| param | g_j | Sobol S1 | Sobol ST | MI(e;theta_j) | null p97.5 |")
    md.append("|---|---|---:|---:|---:|---:|")
    for j, lab in enumerate(tiers.SAMPLED_LABELS):
        mi_e = res["mi_res"][j] if res["mi_res"] else None
        p975 = (res["mi_res_p975_param"][j]
                if res["mi_res_p975_param"] else None)
        flag = " **^**" if (mi_e is not None and p975 is not None
                           and mi_e > p975) else ""
        md.append(f"| {lab} | `{bar(res['signature'][j])}` "
                  f"{res['signature'][j]:.2f} | {res['sobol_S1'][j]:.3f} "
                  f"| {res['sobol_ST'][j]:.3f} | {fmt(mi_e)}{flag} "
                  f"| {fmt(p975)} |")
    if res["ratio_pairs"]:
        md.append("\nConstant-ratio pairs (cv < 5%):")
        for p in res["ratio_pairs"]:
            md.append(f"* ({p['pair'][0]}, {p['pair'][1]}): "
                      f"r_raw = {p['r_raw']:+.4f} (cv {p['cv']:.3f}, "
                      f"valid {p['frac_valid']:.0%})")
    else:
        md.append("\nNo constant-ratio pair (no fixed linear combination).")
    md.append(f"\nMI(f; mu) = {fmt(res['mi_f'])} +/- {fmt(res['mi_f_err'])}"
              + (f", eta_plat = {res['eta_plat']:.3f}"
                 if res.get("eta_plat") is not None else "")
              + f"; calibration R2 = {fmt(res['r2_cal'])}; "
              f"R2_res = {fmt(res['r2_res'])} "
              f"(null p97.5 {fmt(res['r2_null_p975'])}); "
              f"max MI(e;theta) {fmt(max(res['mi_res']) if res['mi_res'] else None)} "
              f"vs max-null p97.5 {fmt(res['mi_res_p975_max'])} -> "
              f"residual {'PASS' if res['residual_pass'] else 'FAIL'}"
              f" (loadings: {', '.join(res['residual_loadings'] or []) or 'none'})")


def to_markdown(run: str, latents: list) -> str:
    md = [f"# Sufficiency audit — `{run}` (roadmap Phase 3, gate G1)\n"]
    md.append(
        "Per latent: the Phase-2 canonical coordinate audited with the "
        "sensitivity signature (normalised E|df/du_j| on the T1 anchors), "
        "Sobol indices on the prior box, constant-ratio pairs (the "
        "answer-agnostic -2 detector), and the calibrated sufficiency test: "
        "5-fold cross-fitted monotone h on T1, residual "
        "e = mu - h(f), R2_res via single-threaded HistGBM and per-parameter "
        "GMM-MI against permutation nulls (frozen rule: R2_res <= 0.05 AND "
        "max-MI <= max-null p97.5). `^` marks parameters above their "
        "per-parameter null. Residuals over all 50k rows are cached as "
        "`analysis/residual_z<k>_v1.npy` for Phase 6.\n")

    md.append("## Draft latent cards v0\n")
    md.append("| latent | audit-expected | canonical coordinate | R_SR "
              "| eta_plat | R2_res | residual | draft status |")
    md.append("|---|---|---|---:|---:|---:|---|---|")
    for L in latents:
        c = L["canonical"]
        if "error" in c:
            md.append(f"| z{L['latent']} | {L['audit_expected']} "
                      f"| `{L['canonical_expr']}` | — | — | — | — | error |")
            continue
        md.append(
            f"| z{L['latent']} | {L['audit_expected']} "
            f"| `{L['canonical_expr'][:48]}` | {L['r_sr']:.2f} "
            f"| {fmt(c.get('eta_plat'))} | {fmt(c['r2_res'])} "
            f"| {'PASS' if c['residual_pass'] else 'FAIL'} "
            f"| {L['status']} |")
    md.append("\n_Pending card components: eta_S (Phase 4), eta_post "
              "(Phase 5), level-set E_inv (Phase 7), subspace probe "
              "(Phase 8)._\n")

    for L in latents:
        md.append(f"\n## z{L['latent']} — {L['audit_expected']}\n")
        md.append(f"Canonical coordinate (R_SR {L['r_sr']:.2f}): "
                  f"`{L['canonical_expr']}`\n")
        if "error" in L["canonical"]:
            md.append(f"_Audit failed: {L['canonical']['error']}_")
            continue
        coord_md(md, L["canonical"])

        if "g1" in L:
            g1 = L["g1"]
            md.append("\n### Gate G1 (amplitude positive control)\n")
            if "error" in g1:
                md.append(f"_G1 failed to run: {g1['error']}_")
            else:
                f2 = g1["f_2var"]
                md.append(f"Knee-slice 2-var coordinate: `{f2['expr']}` "
                          f"(c={f2['complexity']}, stored MI "
                          f"{f2['mi_stored']:.3f}); reference ceiling "
                          f"{g1['reference_ceiling']} nat, stored r "
                          f"{g1['reference_ols_r']}.\n")
                coord_md(md, f2)
                md.append("\n| G1 bullet | numbers | pass |")
                md.append("|---|---|---|")
                b = g1["bullets"]["b1_support_and_recurrence"]
                md.append(f"| slice support + recurrence | support "
                          f"{{{', '.join(b['support'] or [])}}}, slice "
                          f"recurrence {b['slice_recurrence']:.2f}, joins "
                          f"canonical cluster: {b['in_canonical_cluster']} "
                          f"| {'PASS' if b['pass'] else 'FAIL'} |")
                b = g1["bullets"]["b2_constant_ratio"]
                md.append(f"| amplitude direction r | latent-level r_lin = "
                          f"{fmt(b['r_lin'], 4)} (stored "
                          f"{g1['reference_ols_r']}); form-level "
                          + (f"r = {fmt(b['r_form'], 4)} (cv "
                             f"{fmt(b['cv_form'])})" if b["pair_found"] else
                             "no pair at cv<5% (Taylor curvature)")
                          + f", legacy midpoint "
                          f"{fmt(b['amp_ratio_legacy'], 4)} "
                          f"| {'PASS' if b['pass'] else 'FAIL'} |")
                b = g1["bullets"]["b3_eta_s"]
                md.append(f"| eta_S vs reference | {fmt(b['eta_s'])} "
                          f"| {'PASS' if b['pass'] else 'FAIL'} |")
                b = g1["bullets"]["b4_residual_fails_structured"]
                md.append(f"| residual fails structured | R2_res "
                          f"{fmt(b['r2_res'])}, shape loadings "
                          f"{', '.join(b['shape_loadings']) or 'none'} "
                          f"| {'PASS' if b['pass'] else 'FAIL'} |")
                md.append(f"\n**G1 verdict: "
                          f"{'PASS' if g1['pass'] else 'FAIL'}**")

        if L.get("controls"):
            md.append("\n### Shuffled-control audit (negative control)\n")
            md.append("| shuffle seed | MI vs TRUE latent | R2_cal | R2_res |")
            md.append("|---:|---:|---:|---:|")
            for ctl in L["controls"]:
                md.append(f"| {ctl['shuffle_seed']} | {fmt(ctl['mi_true'])} "
                          f"| {fmt(ctl['r2_cal'])} | {fmt(ctl['r2_res'])} |")
            md.append("\n_Control coordinates explain ~nothing of the true "
                      "latent (MI, R2_cal ~ 0), so their residual is the "
                      "latent itself and R2_res is trivially high — the "
                      "audit correctly reports total insufficiency._")

    md.append("\n---\n_Generated by `scripts/sufficiency_audit.py`._")
    return "\n".join(md) + "\n"


# ---- main -------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", required=True)
    p.add_argument("--results-root", default="results")
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--semantic-json", default=None)
    p.add_argument("--knee-json", default=None)
    p.add_argument("--latents", nargs="*", type=int, default=None)
    p.add_argument("--jobs", type=int, default=6)
    p.add_argument("--n-perm-mi", type=int, default=39)
    p.add_argument("--n-perm-r2", type=int, default=10)
    p.add_argument("--max-samples-mi", type=int, default=5000)
    p.add_argument("--gbm-max-iter", type=int, default=100)
    p.add_argument("--g1-only", action="store_true",
                   help="Recompute only the amplitude latent's G1 block and "
                        "merge it into the existing deliverable.")
    p.add_argument("--out", default=None)
    args = p.parse_args()

    model = next((m for m in MODELS if m[1] == args.run), None)
    if model is None:
        print(f"[FAIL] unknown run {args.run}")
        return 1
    _label, run, n_latents, amp_idx = model

    sem = json.loads(Path(args.semantic_json or
                          f"experiments/semantic_recurrence_{run}.json")
                     .read_text())
    knee = json.loads(Path(args.knee_json or
                           f"experiments/knee_readout_{run}.json").read_text())

    run_dir = Path("models") / run
    mu = np.load(run_dir / "analysis" / "encoder_means_test.npy")
    theta = np.load(Path(args.dataset_dir) / "theta.npy")
    theta_all = theta[tiers.split_test_indices(args.dataset_dir)]
    mid, half = tiers.load_prior_box(args.dataset_dir)

    fronts = {}
    fams = discover_families(Path(args.results_root), run, DEFAULT_SUBDIRS)
    for fam, latents in fams.items():
        fronts[fam] = {k: {s: load_front(path) for s, path in seeds.items()}
                       for k, seeds in latents.items()}

    _G.update({
        "run": run, "run_dir": str(run_dir), "amp_idx": amp_idx,
        "results_root": args.results_root,
        "semantic": sem, "knee": knee, "fronts": fronts,
        "mu": mu, "theta_all": theta_all,
        "theta_t1": theta_all[tiers.T1],
        "anchors": tiers.anchor_theta(args.dataset_dir),
        "mid": mid, "half": half,
        "n_perm_mi": args.n_perm_mi, "n_perm_r2": args.n_perm_r2,
        "max_samples_mi": args.max_samples_mi,
        "gbm_max_iter": args.gbm_max_iter,
    })

    if args.g1_only:
        from threadpoolctl import threadpool_limits

        out_path = Path(args.out or f"experiments/sufficiency_audit_{run}")
        payload = json.loads(out_path.with_suffix(".json").read_text())
        sem_lat = sem["latents"][f"z{amp_idx}"]
        canon = next(c for c in sem_lat["clusters"]
                     if c["cluster"] == sem_lat["canonical_cluster"])
        with threadpool_limits(limits=1):
            g1 = g1_audit(amp_idx, canon)
        for L in payload["latents"]:
            if L["latent"] == amp_idx:
                L["g1"] = g1
        out_path.with_suffix(".json").write_text(json.dumps(payload, indent=2))
        out_path.with_suffix(".md").write_text(
            to_markdown(run, payload["latents"]))
        if "bullets" in g1:
            bs = {n.split('_')[0]: ('P' if b['pass'] else 'F')
                  for n, b in g1["bullets"].items()}
            print(f"  G1 {bs} -> {'PASS' if g1['pass'] else 'FAIL'}")
        print(f"[write] {out_path.with_suffix('.json')}")
        print(f"[write] {out_path.with_suffix('.md')}")
        return 0

    ks = args.latents if args.latents is not None else list(range(n_latents))
    if args.jobs > 1 and len(ks) > 1:
        with ProcessPoolExecutor(max_workers=min(args.jobs, len(ks))) as ex:
            latents_out = list(ex.map(latent_worker, ks))
    else:
        latents_out = [latent_worker(k) for k in ks]

    for L in latents_out:
        c = L["canonical"]
        if "error" in c:
            print(f"  z{L['latent']}: ERROR {c['error']}")
            continue
        print(f"  z{L['latent']}: eta_plat={fmt(c.get('eta_plat'))} "
              f"R2_cal={fmt(c['r2_cal'])} R2_res={fmt(c['r2_res'])} "
              f"residual={'PASS' if c['residual_pass'] else 'FAIL'} "
              f"loadings={','.join(c['residual_loadings'] or []) or '-'} "
              f"-> {L.get('status')}")
        if "g1" in L and "bullets" in L["g1"]:
            bs = {n.split('_')[0]: ('P' if b['pass'] else 'F')
                  for n, b in L["g1"]["bullets"].items()}
            print(f"      G1 {bs} -> "
                  f"{'PASS' if L['g1']['pass'] else 'FAIL'}")

    out = Path(args.out or f"experiments/sufficiency_audit_{run}")
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"run": run, "n_perm_mi": args.n_perm_mi,
               "n_perm_r2": args.n_perm_r2,
               "max_samples_mi": args.max_samples_mi,
               "latents": latents_out,
               "generated_by": "scripts/sufficiency_audit.py"}
    out.with_suffix(".json").write_text(json.dumps(payload, indent=2))
    print(f"[write] {out.with_suffix('.json')}")
    out.with_suffix(".md").write_text(to_markdown(run, latents_out))
    print(f"[write] {out.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
