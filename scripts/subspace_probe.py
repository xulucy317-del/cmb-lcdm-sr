#!/usr/bin/env python
"""Subspace & redundancy analysis — Phase 8 of docs/discovery_roadmap.md.

beta-VAEs don't guarantee axis-alignment. For every discovered coordinate
(the Phase-2 canonical f1 and the Phase-6 residual f2 of each latent) this
script asks two questions of the latent SPACE, not single latents:

  1. **Which latent subset carries the coordinate?** Cross-validated sparse
     linear probe Z -> f on T1: lasso path over all L latents, per-support-
     size best CV R2, minimal carrier set A* by the 1-SE rule against the
     all-latents OLS reference, refit confirmed on T2. The probe target is
     the rank-normal transform of f (sufficiency is defined up to a 1-D
     monotone recalibration throughout this study; MI is invariant to it) —
     the raw z-scored target is kept as a sensitivity column. A candidate is
     **axis-aligned** when A* = {its own latent}.
  2. **Is a second latent a redundant copy?** For the two latents with the
     highest unconditional MI(z_i; f), the slab-conditional GMM-MI
     I(z_b; f | z_a) ~ sum_s w_s I(z_b; f | z_a in slab_s) over n_slabs
     equal-count slabs of the conditioner, both directions, with
     redundancy(b|a) = 1 - I(z_b; f | z_a)/I(z_b; f). This is an
     approximation: residual within-slab dependence on the conditioner
     biases I_cond UP, i.e. redundancy DOWN — conservative for redundancy
     claims. Focus candidates (the amplitude-sector latents, e.g. the EE
     z4/z5 pair: "is z4 a redundant copy of the tau direction given z5?")
     additionally get a shuffled-f permutation floor for I_cond.

Roadmap branch (iii) — smallest latent set for the best REJECTED candidate
of latents with no adequate 1-D f — is vacuous here: Phase 3 gave every
latent of both models an f1 with eta_S >= 0.95. The per-candidate A* table
is the constructive replacement (it exhibits the carrying subspace of every
accepted coordinate).

Reads:  experiments/semantic_recurrence_<run>.json   (f1 per latent)
        experiments/residual_sr_<run>.json           (f2 per latent)
        models/<run>/analysis/encoder_means_test.npy
Writes: experiments/subspace_probe_<run>.{md,json}

    python scripts/subspace_probe.py --run lcdm_tt_beta3e-4 --jobs 6
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

from consolidate_allparams import AUDIT_EXPECTED, MODELS  # noqa: E402

from cmb_lcdm_sr import semantics, tiers  # noqa: E402
from cmb_lcdm_sr.mi import mutual_information_gmm  # noqa: E402

SEED_BASE = 20260808

_G: dict = {}


def _f(v):
    return float(v) if v is not None and np.isfinite(v) else None


def rank_normal(x: np.ndarray) -> np.ndarray:
    """Van der Waerden rank-normal scores (monotone-invariant target)."""
    from scipy.stats import norm, rankdata
    return norm.ppf((rankdata(x) - 0.5) / len(x))


# ---- (i) sparse linear probe -------------------------------------------------

def lasso_probe(Z: np.ndarray, y: np.ndarray, n_alphas: int = 50,
                n_folds: int = 5, seed: int = 0) -> dict:
    """Lasso-path probe y <- Z with per-support-size CV R2 and 1-SE A*.

    Z (n, L) and y (n,) are assumed standardised. The lasso path only
    CHOOSES each support (per size, the support of the alpha with best
    penalised CV R2); every chosen support is then scored by a
    cross-validated OLS refit (relaxed lasso), so shrinkage bias cannot
    push small supports below the 1-SE threshold. Returns the staircase
    (size -> refit CV R2 + support), the all-latents OLS reference, and
    the minimal 1-SE carrier set A* with its full-data refit coefficients.
    """
    from sklearn.linear_model import lasso_path
    from sklearn.model_selection import KFold

    n, L = Z.shape
    alphas, coefs, _ = lasso_path(Z, y, n_alphas=n_alphas, eps=1e-4)
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=seed)
    folds = list(kf.split(Z))

    def _ols_cv(cols) -> np.ndarray:
        out = np.empty(len(folds))
        for fi, (tr, te) in enumerate(folds):
            w, *_ = np.linalg.lstsq(
                np.column_stack([Z[tr][:, cols], np.ones(len(tr))]),
                y[tr], rcond=None)
            pred = Z[te][:, cols] @ w[:-1] + w[-1]
            out[fi] = 1.0 - (((y[te] - pred) ** 2).sum()
                             / ((y[te] - y[te].mean()) ** 2).sum())
        return out

    cv = np.full((n_folds, len(alphas)), np.nan)
    for fi, (tr, te) in enumerate(folds):
        _, ctr, _ = lasso_path(Z[tr], y[tr], alphas=alphas)
        b = y[tr].mean() - Z[tr].mean(axis=0) @ ctr
        pred = Z[te] @ ctr + b[None, :]
        ss_tot = ((y[te] - y[te].mean()) ** 2).sum()
        cv[fi] = 1.0 - ((y[te][:, None] - pred) ** 2).sum(axis=0) / ss_tot
    cv_mean = cv.mean(axis=0)
    cv_full = _ols_cv(list(range(L)))
    r2_full, r2_full_se = float(cv_full.mean()), float(cv_full.std(ddof=1)
                                                       / np.sqrt(n_folds))

    support = np.abs(coefs) > 1e-10                    # (L, n_alphas)
    sizes = support.sum(axis=0)
    staircase = []
    for s in sorted(set(sizes[sizes > 0])):
        idx = np.where(sizes == s)[0]
        best = idx[np.argmax(cv_mean[idx])]
        cols = np.where(support[:, best])[0].tolist()
        staircase.append({"size": int(s),
                          "cv_r2": _f(_ols_cv(cols).mean()),
                          "support": cols,
                          "alpha": _f(alphas[best])})
    thr = r2_full - r2_full_se
    a_star = next((st for st in staircase if st["cv_r2"] is not None
                   and st["cv_r2"] >= thr), None)
    if a_star is None:                                  # nothing reaches: all L
        a_star = {"size": L, "cv_r2": r2_full,
                  "support": list(range(L)), "alpha": None}
    cols = a_star["support"]
    w, *_ = np.linalg.lstsq(np.column_stack([Z[:, cols], np.ones(n)]),
                            y, rcond=None)
    return {"staircase": staircase, "r2_full": r2_full,
            "r2_full_se": r2_full_se, "a_star": a_star,
            "coef_a_star": w[:-1].tolist(), "intercept_a_star": float(w[-1])}


# ---- (ii) slab-conditional MI ------------------------------------------------

def slab_conditional_mi(z_i: np.ndarray, f: np.ndarray, z_cond: np.ndarray,
                        n_slabs: int = 8, max_samples: int = 2500,
                        min_slab: int = 200, seed: int = 0) -> dict:
    """I(z_i; f | z_cond) via equal-count slabs of the conditioner.

    Sample-weighted average of within-slab GMM-MI; the combined SE adds the
    per-slab uncertainties in weighted quadrature. Within-slab residual
    dependence on the conditioner biases the result UP (documented
    approximation — conservative for redundancy claims).
    """
    edges = np.unique(np.quantile(z_cond, np.linspace(0, 1, n_slabs + 1)))
    bins = np.clip(np.searchsorted(edges, z_cond, side="right") - 1,
                   0, max(len(edges) - 2, 0))
    slabs = []
    for b in np.unique(bins):
        idx = np.where(bins == b)[0]
        if len(idx) < min_slab:
            continue
        mi, err = mutual_information_gmm(
            z_i[idx].reshape(-1, 1), f[idx].reshape(-1, 1),
            return_uncertainty=True, max_samples=max_samples,
            seed=seed + int(b))
        slabs.append({"n": int(len(idx)), "mi": _f(mi[0, 0]),
                      "err": _f(err[0, 0])})
    ok = [s for s in slabs if s["mi"] is not None]
    if not ok:
        return {"mi_cond": None, "err": None, "slabs": slabs,
                "n_slabs_used": 0, "frac_rows_used": 0.0}
    w = np.array([s["n"] for s in ok], dtype=float)
    n_used = int(w.sum())
    w /= w.sum()
    mi_c = float(np.sum(w * np.array([s["mi"] for s in ok])))
    err_c = float(np.sqrt(np.sum((w * np.array(
        [s["err"] or 0.0 for s in ok])) ** 2)))
    return {"mi_cond": mi_c, "err": err_c, "slabs": slabs,
            "n_slabs_used": len(ok), "frac_rows_used": float(n_used
                                                             / len(z_cond))}


# ---- per-candidate worker ----------------------------------------------------

def candidate_worker(cand: dict) -> dict:
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=1):
        return _candidate_worker(cand)


def _candidate_worker(cand: dict) -> dict:
    t0 = time.time()
    k, stage, expr_str = cand["latent"], cand["stage"], cand["expr"]
    seed = 1000 + 10 * k + (0 if stage == "f1" else 1)
    out = dict(cand)

    expr = semantics.parse_expr(expr_str)
    f_t1 = semantics.evaluate_on_theta(expr, _G["theta_t1"])
    f_t2 = semantics.evaluate_on_theta(expr, _G["theta_t2"])
    fin1, fin2 = np.isfinite(f_t1), np.isfinite(f_t2)
    out["finite_frac_t1"] = float(fin1.mean())
    if fin1.mean() < 0.5:
        out["error"] = "mostly non-finite"
        return out

    Z1, Z2 = _G["z_t1"][fin1], _G["z_t2"][fin2]
    y1 = rank_normal(f_t1[fin1])
    y2 = rank_normal(f_t2[fin2])
    raw1 = (f_t1[fin1] - f_t1[fin1].mean()) / (f_t1[fin1].std() or 1.0)

    # --- probe -----------------------------------------------------------
    probe = lasso_probe(Z1, y1, n_alphas=_G["n_alphas"], seed=seed)
    cols = probe["a_star"]["support"]
    w = np.array(probe["coef_a_star"])
    pred2 = Z2[:, cols] @ w + probe["intercept_a_star"]
    probe["r2_t2"] = _f(1.0 - np.mean((y2 - pred2) ** 2) / np.var(y2))
    # raw-target sensitivity (all-latents OLS CV only) + shuffled control
    probe["r2_full_raw"] = lasso_probe(Z1, raw1, n_alphas=4,
                                       seed=seed)["r2_full"]
    rng = np.random.default_rng([SEED_BASE, seed, 3])
    probe["r2_full_shuffled"] = lasso_probe(Z1, rng.permutation(y1),
                                            n_alphas=4, seed=seed)["r2_full"]
    # own-latent-only reference: linear decodability from z_k alone
    probe["r2_own"] = lasso_probe(Z1[:, [k]], y1, n_alphas=2,
                                  seed=seed)["r2_full"]
    probe["axis_aligned"] = bool(cols == [k])
    probe["own_in_a_star"] = bool(k in cols)
    out["probe"] = probe

    # --- unconditional MI per latent + top-2 conditional ------------------
    mi_u, mi_u_err = mutual_information_gmm(
        Z1, y1.reshape(-1, 1), return_uncertainty=True,
        max_samples=_G["mi_max_samples"], seed=seed)
    mi_u, mi_u_err = mi_u[:, 0], mi_u_err[:, 0]
    out["mi_uncond"] = [_f(v) for v in mi_u]
    out["mi_uncond_err"] = [_f(v) for v in mi_u_err]

    # GMM-MI collapses on near-deterministic pairs; fall back to the
    # rank-Gaussian equivalent -0.5 ln(1 - rho_s^2) there (flagged).
    from scipy.stats import spearmanr
    rho = np.array([spearmanr(Z1[:, i], y1).statistic
                    for i in range(Z1.shape[1])])
    gauss_mi = -0.5 * np.log(np.clip(1.0 - rho ** 2, 1e-12, None))
    proxy = ~np.isfinite(mi_u)
    mi_u = np.where(proxy, gauss_mi, mi_u)
    out["spearman_abs"] = [float(abs(r)) for r in rho]
    out["mi_proxy_used"] = np.where(proxy)[0].tolist()

    order = np.argsort(-np.nan_to_num(mi_u))
    a, b = int(order[0]), int(order[1])
    red = {"top1": a, "top2": b,
           "mi_top1": _f(mi_u[a]), "mi_top2": _f(mi_u[b])}
    for tag, (zi, zc) in {"top2_given_top1": (b, a),
                          "top1_given_top2": (a, b)}.items():
        cond = slab_conditional_mi(Z1[:, zi], y1, Z1[:, zc],
                                   n_slabs=_G["n_slabs"],
                                   max_samples=_G["slab_max_samples"],
                                   seed=seed + 7 * zi)
        uncond = mi_u[zi]
        err_u = mi_u_err[zi] if np.isfinite(mi_u_err[zi]) else 0.0
        red[tag] = {
            "z": zi, "given": zc,
            "mi_cond": cond["mi_cond"], "err": cond["err"],
            "n_slabs_used": cond.get("n_slabs_used"),
            "redundancy": (_f(1.0 - cond["mi_cond"] / uncond)
                           if cond["mi_cond"] is not None
                           and np.isfinite(uncond)
                           and uncond > 2 * err_u else None),
        }
    out["redundancy"] = red

    # --- permutation floor for focus candidates ---------------------------
    if cand.get("focus"):
        rng = np.random.default_rng([SEED_BASE, seed, 11])
        floor = []
        for p in range(_G["n_perm"]):
            yp = rng.permutation(y1)
            c = slab_conditional_mi(Z1[:, b], yp, Z1[:, a],
                                    n_slabs=_G["n_slabs"],
                                    max_samples=_G["slab_max_samples"],
                                    seed=seed + 100 + p)
            if c["mi_cond"] is not None:
                floor.append(c["mi_cond"])
        out["perm_floor_cond"] = {"n": len(floor),
                                  "mean": _f(np.mean(floor)) if floor else None,
                                  "max": _f(np.max(floor)) if floor else None}

    out["seconds"] = round(time.time() - t0, 1)
    print(f"[z{k} {stage}] A*={out['probe']['a_star']['support']} "
          f"cvR2={fmt(out['probe']['a_star']['cv_r2'])} "
          f"(full {fmt(out['probe']['r2_full'])}) "
          f"T2 {fmt(out['probe']['r2_t2'])} "
          f"top2=({red['top1']},{red['top2']}) "
          f"red(b|a)={fmt(red['top2_given_top1']['redundancy'], 2)} "
          f"[{out['seconds']}s]", flush=True)
    return out


# ---- driver ------------------------------------------------------------------

def build_candidates(run: str, amp_idx: int, sem: dict, res: dict,
                     ks: list) -> list:
    roles = AUDIT_EXPECTED[run]
    res_by_k = {L["latent"]: L for L in res["latents"]}
    cands = []
    for k in ks:
        sem_lat = sem["latents"][f"z{k}"]
        canon = next(c for c in sem_lat["clusters"]
                     if c["cluster"] == sem_lat["canonical_cluster"])
        focus = (k == amp_idx) or ("amplitude" in (roles.get(k) or ""))
        cands.append({"latent": k, "stage": "f1", "role": roles.get(k),
                      "expr": canon["representative"], "focus": focus})
        f2 = (res_by_k.get(k) or {}).get("f2")
        if f2 is not None:
            cands.append({"latent": k, "stage": "f2", "role": roles.get(k),
                          "expr": f2["expr"], "focus": False})
    return cands


def run_probe(run: str, n_latents: int, amp_idx: int, args) -> dict:
    sem = json.loads(Path(args.semantic_json or
                          f"experiments/semantic_recurrence_{run}.json")
                     .read_text())
    res = json.loads(Path(args.residual_json or
                          f"experiments/residual_sr_{run}.json").read_text())

    run_dir = Path("models") / run
    mu = np.load(run_dir / "analysis" / "encoder_means_test.npy")
    theta = np.load(Path(args.dataset_dir) / "theta.npy")
    theta_all = theta[tiers.split_test_indices(args.dataset_dir)]

    m, s = mu[tiers.T1].mean(axis=0), mu[tiers.T1].std(axis=0)
    s = np.where(s < 1e-12, 1.0, s)
    _G.update({
        "theta_t1": theta_all[tiers.T1], "theta_t2": theta_all[tiers.T2],
        "z_t1": (mu[tiers.T1] - m) / s, "z_t2": (mu[tiers.T2] - m) / s,
        "n_alphas": args.n_alphas, "n_slabs": args.n_slabs,
        "mi_max_samples": args.mi_max_samples,
        "slab_max_samples": args.slab_max_samples, "n_perm": args.n_perm,
    })

    ks = args.latents if args.latents is not None else list(range(n_latents))
    cands = build_candidates(run, amp_idx, sem, res, ks)
    print(f"[plan] {len(cands)} candidates, jobs={args.jobs}", flush=True)

    results = []
    if args.jobs <= 1:
        for c in cands:
            results.append(candidate_worker(c))
    else:
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            futs = {ex.submit(candidate_worker, c): c for c in cands}
            for fu in as_completed(futs):
                results.append(fu.result())
    results.sort(key=lambda r: (r["latent"], r["stage"]))

    # per-latent status inputs
    latent_summary = []
    for k in ks:
        own = next((r for r in results
                    if r["latent"] == k and r["stage"] == "f1"
                    and "probe" in r), None)
        if own is None:
            continue
        latent_summary.append({
            "latent": k, "role": AUDIT_EXPECTED[run].get(k),
            "a_star_f1": own["probe"]["a_star"]["support"],
            "axis_aligned_f1": own["probe"]["axis_aligned"],
            "own_in_a_star_f1": own["probe"]["own_in_a_star"],
            "r2_own_f1": own["probe"]["r2_own"],
            "r2_full_f1": own["probe"]["r2_full"],
        })

    return {"run": run, "seed_base": SEED_BASE,
            "config": {kk: _G[kk] for kk in
                       ("n_alphas", "n_slabs", "mi_max_samples",
                        "slab_max_samples", "n_perm")},
            "candidates": results, "latent_summary": latent_summary,
            "branch_iii_note": (
                "vacuous: Phase 3 gave every latent an f1 with eta_S >= "
                "0.95; the per-candidate A* table is the constructive "
                "replacement"),
            "generated_by": "scripts/subspace_probe.py"}


# ---- outputs -----------------------------------------------------------------

def fmt(x, prec=3):
    return "n/a" if x is None else f"{x:.{prec}f}"


def _zset(cols) -> str:
    return "{" + ", ".join(f"z{c}" for c in cols) + "}"


def to_markdown(payload: dict) -> str:
    run = payload["run"]
    cfg = payload["config"]
    md = [f"# Subspace probe — `{run}` (roadmap Phase 8)\n"]
    md.append(
        "Per discovered coordinate (Phase-2 canonical f1, Phase-6 residual "
        "f2): sparse linear probe Z -> rank-normal(f) on T1 (lasso path, "
        "5-fold CV, minimal carrier set A* by the 1-SE rule vs the "
        "all-latents OLS reference, T2 confirmation of the A* refit; raw-f "
        "and shuffled-f references), then slab-conditional GMM-MI "
        f"({cfg['n_slabs']} equal-count slabs) between the two strongest "
        "carrier latents: redundancy(b|a) = 1 - I(z_b; f | z_a)/I(z_b; f). "
        "Within-slab residual dependence on the conditioner biases I_cond "
        "up and redundancy down — the approximation is conservative for "
        "redundancy claims. Axis-aligned = A* is exactly the candidate's "
        "own latent.\n")

    md.append("| candidate | role | A* | cv R2(A*) | R2 own | "
              "R2 full +/- SE | T2 R2(A*) | raw-f R2 | shuf R2 "
              "| axis-aligned |")
    md.append("|---|---|---|---:|---:|---|---:|---:|---:|---|")
    for r in payload["candidates"]:
        if "probe" not in r:
            md.append(f"| z{r['latent']} {r['stage']} | {r['role']} | — "
                      f"| — | — | — | — | — | — | {r.get('error', 'n/a')} |")
            continue
        p = r["probe"]
        md.append(
            f"| z{r['latent']} {r['stage']} | {r['role']} "
            f"| {_zset(p['a_star']['support'])} "
            f"| {fmt(p['a_star']['cv_r2'])} "
            f"| {fmt(p['r2_own'])} "
            f"| {fmt(p['r2_full'])} +/- {fmt(p['r2_full_se'])} "
            f"| {fmt(p['r2_t2'])} | {fmt(p['r2_full_raw'])} "
            f"| {fmt(p['r2_full_shuffled'])} | {p['axis_aligned']} |")

    md.append("\n| candidate | top-2 | MI(top1) | MI(top2) | "
              "I(top2; f \\| top1) | red(2\\|1) | I(top1; f \\| top2) | "
              "red(1\\|2) |")
    md.append("|---|---|---:|---:|---|---:|---|---:|")
    for r in payload["candidates"]:
        if "redundancy" not in r:
            continue
        d = r["redundancy"]
        c21, c12 = d["top2_given_top1"], d["top1_given_top2"]
        md.append(
            f"| z{r['latent']} {r['stage']} "
            f"| (z{d['top1']}, z{d['top2']}) "
            f"| {fmt(d['mi_top1'])} | {fmt(d['mi_top2'])} "
            f"| {fmt(c21['mi_cond'])} +/- {fmt(c21['err'])} "
            f"| {fmt(c21['redundancy'], 2)} "
            f"| {fmt(c12['mi_cond'])} +/- {fmt(c12['err'])} "
            f"| {fmt(c12['redundancy'], 2)} |")

    focus = [r for r in payload["candidates"]
             if r.get("focus") and "redundancy" in r]
    if focus:
        md.append("\n## Amplitude-sector focus\n")
        for r in focus:
            d = r["redundancy"]
            c21 = d["top2_given_top1"]
            rd = c21["redundancy"]
            verdict = ("redundant copy" if rd is not None and rd >= 0.8
                       else "partially redundant" if rd is not None
                       and rd >= 0.5 else "complementary")
            pf = r.get("perm_floor_cond") or {}
            md.append(
                f"* z{r['latent']} {r['stage']} `{r['expr']}`: carriers "
                f"(z{d['top1']}, z{d['top2']}); I(z{c21['z']}; f | "
                f"z{c21['given']}) = {fmt(c21['mi_cond'])} vs unconditional "
                f"{fmt(d['mi_top2'])} nat -> redundancy {fmt(rd, 2)} "
                f"(**{verdict}**; shuffled-f floor mean {fmt(pf.get('mean'))}"
                f", max {fmt(pf.get('max'))}, n={pf.get('n')}).")

    md.append("\n## Per-latent status inputs\n")
    md.append("| latent | role | A*(own f1) | axis-aligned | own in A* "
              "| R2 own | R2 full |")
    md.append("|---|---|---|---|---|---:|---:|")
    for L in payload["latent_summary"]:
        md.append(f"| z{L['latent']} | {L['role']} "
                  f"| {_zset(L['a_star_f1'])} | {L['axis_aligned_f1']} "
                  f"| {L['own_in_a_star_f1']} | {fmt(L['r2_own_f1'])} "
                  f"| {fmt(L['r2_full_f1'])} |")
    md.append(f"\n_Branch (iii): {payload['branch_iii_note']}._")

    md.append("\n---\n_Generated by `scripts/subspace_probe.py`._")
    return "\n".join(md) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", required=True)
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--semantic-json", default=None)
    p.add_argument("--residual-json", default=None)
    p.add_argument("--latents", nargs="*", type=int, default=None)
    p.add_argument("--jobs", type=int, default=4)
    p.add_argument("--n-alphas", type=int, default=50)
    p.add_argument("--n-slabs", type=int, default=8)
    p.add_argument("--mi-max-samples", type=int, default=5000)
    p.add_argument("--slab-max-samples", type=int, default=2500)
    p.add_argument("--n-perm", type=int, default=5)
    p.add_argument("--out", default=None)
    args = p.parse_args()

    model = next((m for m in MODELS if m[1] == args.run), None)
    if model is None:
        print(f"[FAIL] unknown run {args.run}")
        return 1
    _label, run, n_latents, amp_idx = model

    payload = run_probe(run, n_latents, amp_idx, args)

    out = Path(args.out or f"experiments/subspace_probe_{run}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(payload, indent=2))
    print(f"[write] {out.with_suffix('.json')}")
    out.with_suffix(".md").write_text(to_markdown(payload))
    print(f"[write] {out.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
