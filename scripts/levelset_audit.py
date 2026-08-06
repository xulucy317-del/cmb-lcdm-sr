#!/usr/bin/env python
"""Level-set invariance audit — Phase 7a of docs/discovery_roadmap.md
(the observable-free half of gate G4: association → coordinate).

Sufficient, recurrent association is not yet a coordinate claim. The
defining test is invariance along the level sets of the canonical
coordinate f: moving theta while holding f fixed must not move the latent.

Per latent, on T1 (pairs) with a T2 confirmation pass:

  1. **E_inv** — quantile-bin f into ~200 equal-count bins (delta ~ 0.5%);
     within each bin greedily draw disjoint row pairs maximising Euclidean
     distance in the COMPLEMENT u-coordinates u_{S^c} (S = the sampled-basis
     support of f); report

         E_inv(f) = E[ (mu_k - mu_k')^2 | pair ] / (2 Var(mu_k))

     (random pairs => 1; an empirically re-paired random reference is
     reported to validate the normalisation), its pair-bootstrap SE, and
     the curve of E_inv vs nuisance distance (quartiles — invariance must
     survive the LARGEST nuisance moves). Frozen threshold: <= 0.05.
  2. **Matched-nuisance response** — k-NN neighbourhoods in u_{S^c}
     (caliper = the caliper-q quantile of random-pair nuisance distances):
     within them f varies while the nuisance is pinned; the pooled response
     mu_k vs f must collapse to one 1-D curve — cross-fitted general
     (non-monotone) spline R^2 >= 0.9 (calibrate machinery, frozen rule).
  3. **Controls** (amplitude latent) — the shuffled-target control forms
     audited the same way (expect E_inv ~ 1: their level sets are
     physically meaningless), and wrong-latent specificity: the amplitude
     canonical f must NOT be invariant for the shape latents.

Per-latent `levelset_pass` = (E_inv <= 0.05) AND (response R^2 >= 0.9);
None when f has no complement (S = all 6 — no nuisance direction exists).

**Gate G4a** (amplitude): E_inv(f_amp) <= 0.05, matched response 1-D
(R^2 >= 0.9), and both confirmed on T2. (G4's decoder-side bullet —
a_tau/a_lnAs ~ -2 — lands with Phase 7b.)

Reads:  experiments/semantic_recurrence_<run>.json,
        models/<run>/analysis/encoder_means_test.npy,
        results/<run>/allparams/shuffled_z<amp>_s*/report.json
Writes: experiments/levelset_audit_<run>.{md,json}

    python scripts/levelset_audit.py --run lcdm_tt_beta3e-4
"""
import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("TQDM_DISABLE", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import _bootstrap  # noqa: F401,E402

import numpy as np  # noqa: E402

from consolidate_allparams import AUDIT_EXPECTED, MODELS  # noqa: E402

from cmb_lcdm_sr import calibrate, semantics, tiers  # noqa: E402

SEED_BASE = 20260807


def _f(v):
    return float(v) if v is not None and np.isfinite(v) else None


# ---- pair construction -------------------------------------------------------

def quantile_bins(fvals: np.ndarray, n_bins: int) -> np.ndarray:
    """Equal-count bin ids on one coordinate (constant f ⇒ one bin)."""
    edges = np.unique(np.quantile(fvals, np.linspace(0.0, 1.0, n_bins + 1)))
    if len(edges) < 2:
        return np.zeros(len(fvals), dtype=int)
    return np.clip(np.searchsorted(edges, fvals, side="right") - 1,
                   0, len(edges) - 2)


def pair_within_bins(fvals: np.ndarray, u_comp: np.ndarray, n_bins: int = 200,
                     pairs_per_bin: int = 25, bin_cap: int = 400,
                     min_bin: int = 4, rng: np.random.Generator | None = None,
                     bins: np.ndarray | None = None):
    """Disjoint within-bin pairs maximising ||u_comp_i − u_comp_j||.

    Rows are quantile-binned on fvals (equal-count, delta ~ 1/n_bins); within
    each bin a greedy max-distance matching draws up to pairs_per_bin disjoint
    pairs. Oversized bins (degenerate f) are subsampled to bin_cap first.
    Precomputed ``bins`` ids (e.g. joint 2-D cells) override the 1-D binning.
    Returns (idx_i, idx_j, dist) index arrays into fvals' rows.
    """
    rng = rng or np.random.default_rng(0)
    if bins is None:
        bins = quantile_bins(fvals, n_bins)
    ii, jj, dd = [], [], []
    for b in np.unique(bins):
        rows = np.where(bins == b)[0]
        if len(rows) < max(min_bin, 2):
            continue
        if len(rows) > bin_cap:
            rows = rng.choice(rows, size=bin_cap, replace=False)
        X = u_comp[rows]
        D = np.sqrt(((X[:, None, :] - X[None, :, :]) ** 2).sum(-1))
        np.fill_diagonal(D, -1.0)
        for _ in range(min(pairs_per_bin, len(rows) // 2)):
            a, c = np.unravel_index(np.argmax(D), D.shape)
            if D[a, c] < 0:
                break
            ii.append(rows[a]); jj.append(rows[c]); dd.append(D[a, c])
            D[a, :] = -1.0; D[:, a] = -1.0
            D[c, :] = -1.0; D[:, c] = -1.0
    return np.array(ii, dtype=int), np.array(jj, dtype=int), np.array(dd)


def e_inv_stat(mu_col: np.ndarray, i: np.ndarray, j: np.ndarray,
               var_mu: float, n_boot: int = 500,
               rng: np.random.Generator | None = None):
    """(e_inv, se, per-pair values) of E[(mu−mu')²]/(2 Var)."""
    rng = rng or np.random.default_rng(0)
    if len(i) == 0 or var_mu <= 0:
        return None, None, np.array([])
    d2 = (mu_col[i] - mu_col[j]) ** 2 / (2.0 * var_mu)
    boots = np.empty(n_boot)
    for b in range(n_boot):
        boots[b] = d2[rng.integers(0, len(d2), len(d2))].mean()
    return float(d2.mean()), float(boots.std(ddof=1)), d2


def distance_curve(d2: np.ndarray, dist: np.ndarray, n_q: int = 4) -> list:
    """E_inv per nuisance-distance quartile (invariance at LARGE moves)."""
    if len(d2) == 0:
        return []
    edges = np.quantile(dist, np.linspace(0.0, 1.0, n_q + 1))
    out = []
    for q in range(n_q):
        m = ((dist >= edges[q]) & (dist <= edges[q + 1]) if q == n_q - 1
             else (dist >= edges[q]) & (dist < edges[q + 1]))
        if m.sum() == 0:
            continue
        out.append({"d_lo": float(edges[q]), "d_hi": float(edges[q + 1]),
                    "e_inv": float(d2[m].mean()), "n_pairs": int(m.sum())})
    return out


def matched_response(fvals: np.ndarray, mu_col: np.ndarray,
                     u_comp: np.ndarray, n_seeds: int = 500, k_nn: int = 40,
                     caliper_q: float = 0.05, seed: int = 0) -> dict:
    """Cross-fitted 1-D spline R² of mu vs f on nuisance-matched rows.

    k-NN neighbourhoods in u_{S^c} keep the nuisance pinned while f varies;
    pooled matched rows are fit with the general (non-monotone) calibrator.
    With an empty complement every row is trivially matched (flagged).
    """
    rng = np.random.default_rng([SEED_BASE, seed, 11])
    n = len(fvals)
    if u_comp.shape[1] == 0:
        matched = np.arange(n)
        caliper = None
    else:
        from scipy.spatial import cKDTree

        pa = rng.integers(0, n, 2000)
        pb = rng.integers(0, n, 2000)
        rand_d = np.sqrt(((u_comp[pa] - u_comp[pb]) ** 2).sum(-1))
        caliper = float(np.quantile(rand_d[rand_d > 0], caliper_q))
        tree = cKDTree(u_comp)
        seeds = rng.choice(n, size=min(n_seeds, n), replace=False)
        dist, idx = tree.query(u_comp[seeds], k=min(k_nn, n))
        matched = np.unique(idx[dist <= caliper])
    if len(matched) < 64:
        return {"r2_response": None, "n_matched": int(len(matched)),
                "caliper": caliper, "note": "too few matched rows"}
    cal = calibrate.crossfit_calibration(fvals[matched], mu_col[matched],
                                         monotone=False, seed=seed)
    return {"r2_response": _f(cal["r2_cal"]), "n_matched": int(len(matched)),
            "caliper": caliper}


# ---- one-coordinate audit ----------------------------------------------------

def audit_levelsets(expr_str: str, mu_col: np.ndarray, theta_rows: np.ndarray,
                    u_rows: np.ndarray, cfg: dict, seed: int = 0) -> dict:
    """Full 7a audit of one coordinate against one latent column."""
    expr = semantics.parse_expr(expr_str)
    if expr is None:
        return {"expr": expr_str, "error": "unparseable"}
    fvals = semantics.evaluate_on_theta(expr, theta_rows)
    finite = np.isfinite(fvals)
    out = {"expr": expr_str, "finite_frac": float(finite.mean())}
    if finite.mean() < 0.5:
        out["error"] = "mostly non-finite"
        return out

    syms = semantics._sampledify(expr).free_symbols
    support = [lab for lab, s in zip(tiers.SAMPLED_LABELS,
                                     semantics.SAMPLED_SYMBOLS) if s in syms]
    comp_idx = [jx for jx, lab in enumerate(tiers.SAMPLED_LABELS)
                if lab not in support]
    out["support"] = support
    out["complement"] = [tiers.SAMPLED_LABELS[jx] for jx in comp_idx]

    fv, mu = fvals[finite], mu_col[finite]
    var_mu = float(np.var(mu))
    u_comp = u_rows[finite][:, comp_idx]
    rng = np.random.default_rng([SEED_BASE, seed])

    if comp_idx:
        i, j, dist = pair_within_bins(fv, u_comp, n_bins=cfg["n_bins"],
                                      pairs_per_bin=cfg["pairs_per_bin"],
                                      bin_cap=cfg["bin_cap"], rng=rng)
        e_inv, se, d2 = e_inv_stat(mu, i, j, var_mu,
                                   n_boot=cfg["n_boot"], rng=rng)
        # random re-pairing of the same rows — must sit at ~1
        perm = rng.permutation(len(fv) - len(fv) % 2)
        ri, rj = perm[0::2][:len(i)], perm[1::2][:len(i)]
        e_rand, _, _ = e_inv_stat(mu, ri, rj, var_mu,
                                  n_boot=8, rng=rng)
        curve = distance_curve(d2, dist)
        out.update({
            "n_pairs": int(len(i)),
            "e_inv": _f(e_inv), "e_inv_se": _f(se),
            "e_inv_random_ref": _f(e_rand),
            "e_inv_curve": curve,
            "e_inv_top_quartile": (_f(curve[-1]["e_inv"]) if curve else None),
            "mean_pair_nuisance_dist": _f(dist.mean()) if len(dist) else None,
        })
    else:
        out.update({"n_pairs": 0, "e_inv": None, "e_inv_se": None,
                    "e_inv_random_ref": None, "e_inv_curve": [],
                    "e_inv_top_quartile": None,
                    "mean_pair_nuisance_dist": None,
                    "note": "support = all 6 — no nuisance direction exists"})

    out["response"] = matched_response(fv, mu, u_comp,
                                       n_seeds=cfg["n_seeds"],
                                       k_nn=cfg["k_nn"],
                                       caliper_q=cfg["caliper_q"], seed=seed)
    e, r2 = out["e_inv"], out["response"]["r2_response"]
    out["levelset_pass"] = (bool(e <= 0.05 and r2 is not None and r2 >= 0.9)
                            if e is not None else None)
    return out


# ---- per-run driver ----------------------------------------------------------

def run_audit(run: str, n_latents: int, amp_idx: int, args) -> dict:
    sem = json.loads(Path(args.semantic_json or
                          f"experiments/semantic_recurrence_{run}.json")
                     .read_text())
    run_dir = Path("models") / run
    mu = np.load(run_dir / "analysis" / "encoder_means_test.npy")
    theta = np.load(Path(args.dataset_dir) / "theta.npy")
    theta_all = theta[tiers.split_test_indices(args.dataset_dir)]
    mid, half = tiers.load_prior_box(args.dataset_dir)

    cfg = {"n_bins": args.n_bins, "pairs_per_bin": args.pairs_per_bin,
           "bin_cap": args.bin_cap, "n_boot": args.n_boot,
           "n_seeds": args.n_seeds, "k_nn": args.k_nn,
           "caliper_q": args.caliper_q}

    tiers_data = {}
    for name, sl in (("T1", tiers.T1), ("T2", tiers.T2)):
        th = theta_all[sl]
        tiers_data[name] = (th, tiers.theta_to_u(th, mid, half), sl)

    # Phase-3 calibration R² per latent (cross-instrument consistency: for a
    # structured residual, E_inv is expected in [1−R²_cal, 2(1−R²_cal)] —
    # the upper end when the residual is anti-correlated across the box).
    r2_cal_p3 = {}
    audit_path = Path(args.audit_json or
                      f"experiments/sufficiency_audit_{run}.json")
    if audit_path.exists():
        for L in json.loads(audit_path.read_text())["latents"]:
            r2_cal_p3[L["latent"]] = L.get("canonical", {}).get("r2_cal")

    ks = args.latents if args.latents is not None else list(range(n_latents))
    latents_out = []
    for k in ks:
        sem_lat = sem["latents"][f"z{k}"]
        canon = next(c for c in sem_lat["clusters"]
                     if c["cluster"] == sem_lat["canonical_cluster"])
        L = {"latent": k, "audit_expected": AUDIT_EXPECTED[run].get(k),
             "canonical_expr": canon["representative"],
             "r2_cal_phase3": r2_cal_p3.get(k),
             "e_inv_expected_band": ([1.0 - r2_cal_p3[k],
                                      2.0 * (1.0 - r2_cal_p3[k])]
                                     if r2_cal_p3.get(k) is not None else None)}
        th1, u1, sl1 = tiers_data["T1"]
        L["t1"] = audit_levelsets(canon["representative"], mu[sl1, k],
                                  th1, u1, cfg, seed=k)
        th2, u2, sl2 = tiers_data["T2"]
        L["t2"] = audit_levelsets(canon["representative"], mu[sl2, k],
                                  th2, u2, cfg, seed=100 + k)
        L["levelset_pass"] = L["t1"].get("levelset_pass")
        latents_out.append(L)
        t1 = L["t1"]
        print(f"  z{k}: E_inv={fmt(t1.get('e_inv'))}"
              f"+/-{fmt(t1.get('e_inv_se'))} "
              f"(rand {fmt(t1.get('e_inv_random_ref'), 2)}, "
              f"topQ {fmt(t1.get('e_inv_top_quartile'))}) "
              f"R2_resp={fmt(t1.get('response', {}).get('r2_response'))} "
              f"T2: E_inv={fmt(L['t2'].get('e_inv'))} "
              f"R2={fmt(L['t2'].get('response', {}).get('r2_response'))} "
              f"-> pass={L['levelset_pass']}")

    # ---- amplitude controls -------------------------------------------------
    controls = {"shuffled": [], "wrong_latent": []}
    amp_L = next((L for L in latents_out if L["latent"] == amp_idx), None)
    if amp_L is not None:
        th1, u1, sl1 = tiers_data["T1"]
        for path in sorted((Path(args.results_root) / run / "allparams")
                           .glob(f"shuffled_z{amp_idx}_s*/report.json")):
            rep = json.loads(path.read_text())
            expr = rep.get("best_expression")
            if not expr:
                continue
            res = audit_levelsets(expr, mu[sl1, amp_idx], th1, u1, cfg,
                                  seed=200 + rep.get("shuffle_seed", 0))
            controls["shuffled"].append(
                {"shuffle_seed": rep.get("shuffle_seed"), "expr": expr,
                 "e_inv": res.get("e_inv"),
                 "r2_response": res.get("response", {}).get("r2_response")})
        amp_expr = amp_L["canonical_expr"]
        for L in latents_out:
            if L["latent"] == amp_idx:
                continue
            res = audit_levelsets(amp_expr, mu[sl1, L["latent"]], th1, u1,
                                  cfg, seed=300 + L["latent"])
            controls["wrong_latent"].append(
                {"latent": L["latent"], "e_inv": res.get("e_inv"),
                 "r2_response": res.get("response", {}).get("r2_response")})

    # ---- gate G4a -----------------------------------------------------------
    g4a = None
    if amp_L is not None:
        t1, t2 = amp_L["t1"], amp_L["t2"]
        e1, r1 = t1.get("e_inv"), t1.get("response", {}).get("r2_response")
        e2, r2 = t2.get("e_inv"), t2.get("response", {}).get("r2_response")
        g4a = {
            "latent": amp_idx,
            "e_inv_t1": e1, "r2_response_t1": r1,
            "e_inv_t2": e2, "r2_response_t2": r2,
            "pass_e_inv": bool(e1 is not None and e1 <= 0.05),
            "pass_response": bool(r1 is not None and r1 >= 0.9),
            "pass_t2_confirm": bool(e2 is not None and e2 <= 0.05
                                    and r2 is not None and r2 >= 0.9),
            "controls_sane": bool(
                all((c["e_inv"] or 0.0) > 0.5 for c in controls["shuffled"])
                and all((c["e_inv"] or 0.0) > 0.05
                        for c in controls["wrong_latent"])),
        }
        g4a["pass"] = bool(g4a["pass_e_inv"] and g4a["pass_response"]
                           and g4a["pass_t2_confirm"])
        print(f"  G4a: E_inv {fmt(e1)} (<=0.05: {g4a['pass_e_inv']}), "
              f"R2 {fmt(r1)} (>=0.9: {g4a['pass_response']}), "
              f"T2 confirm {g4a['pass_t2_confirm']}, controls sane "
              f"{g4a['controls_sane']} -> "
              f"{'PASS' if g4a['pass'] else 'FAIL'}")

    return {"run": run, "config": cfg, "seed_base": SEED_BASE,
            "latents": latents_out, "controls": controls, "gate_G4a": g4a,
            "generated_by": "scripts/levelset_audit.py"}


# ---- outputs -----------------------------------------------------------------

def fmt(x, prec=3):
    return "n/a" if x is None else f"{x:.{prec}f}"


def to_markdown(payload: dict) -> str:
    run, cfg = payload["run"], payload["config"]
    md = [f"# Level-set invariance audit — `{run}` (roadmap Phase 7a, "
          "gate G4a)\n"]
    md.append(
        f"Per latent: the Phase-2 canonical coordinate f, quantile-binned "
        f"into {cfg['n_bins']} equal-count bins on T1; within-bin disjoint "
        f"pairs maximising nuisance distance ||Δu_(S^c)|| (≤ "
        f"{cfg['pairs_per_bin']}/bin). E_inv = E[(mu−mu')²|pair]/(2 Var mu), "
        "normalised so random pairs = 1 (empirical random reference "
        "alongside); frozen pass rule E_inv <= 0.05. Response test: k-NN "
        f"nuisance matching (caliper = q{cfg['caliper_q']:.2f} of random "
        "nuisance distances), cross-fitted general spline R² of mu vs f >= "
        "0.9. T2 = independent confirmation pass. Latents whose canonical "
        "support is all 6 parameters have no nuisance direction: E_inv is "
        "undefined there (levelset_pass = None) and only the response R² "
        "is reported.\n")

    md.append("| latent | role | support | E_inv +/- SE | expected band "
              "| rand ref | top-quartile | R2 resp (n) | T2 E_inv | T2 R2 "
              "| pass |")
    md.append("|---|---|---|---|---|---:|---:|---|---:|---:|---|")
    for L in payload["latents"]:
        t1, t2 = L["t1"], L["t2"]
        resp = t1.get("response", {})
        band = L.get("e_inv_expected_band")
        md.append(
            f"| z{L['latent']} | {L['audit_expected']} "
            f"| {{{', '.join(t1.get('support', []))}}} "
            f"| {fmt(t1.get('e_inv'))} +/- {fmt(t1.get('e_inv_se'))} "
            f"| {f'{band[0]:.3f}–{band[1]:.3f}' if band else 'n/a'} "
            f"| {fmt(t1.get('e_inv_random_ref'), 2)} "
            f"| {fmt(t1.get('e_inv_top_quartile'))} "
            f"| {fmt(resp.get('r2_response'))} ({resp.get('n_matched')}) "
            f"| {fmt(t2.get('e_inv'))} "
            f"| {fmt(t2.get('response', {}).get('r2_response'))} "
            f"| {L['levelset_pass']} |")
    md.append(
        "\n_Expected band = [1−R²_cal, 2(1−R²_cal)] from the Phase-3 "
        "calibration: within-level-set movement of mu IS the structured "
        "residual, so for a latent whose f1 leaves a residual, E_inv cannot "
        "sit below 1−R²_cal (upper end when the residual is anti-correlated "
        "across nuisance space). E_inv landing inside the band while the "
        "response R² passes says the audit and the Phase-3 calibration "
        "agree: f1 is the primary 1-D coordinate, and the invariance "
        "failure is exactly the structured residual Phase 6 targets — not "
        "a confounded response._\n")

    for L in payload["latents"]:
        t1 = L["t1"]
        md.append(f"\n## z{L['latent']} — {L['audit_expected']}\n")
        md.append(f"Canonical `{L['canonical_expr']}`; support "
                  f"{{{', '.join(t1.get('support', []))}}}, complement "
                  f"{{{', '.join(t1.get('complement', []))}}}; "
                  f"{t1.get('n_pairs', 0)} pairs, mean nuisance distance "
                  f"{fmt(t1.get('mean_pair_nuisance_dist'), 2)}.")
        if t1.get("note"):
            md.append(f"_{t1['note']}_")
        if t1.get("e_inv_curve"):
            md.append("\nE_inv vs nuisance distance:")
            md.append("| d range | E_inv | n |")
            md.append("|---|---:|---:|")
            for c in t1["e_inv_curve"]:
                md.append(f"| {c['d_lo']:.2f}–{c['d_hi']:.2f} "
                          f"| {c['e_inv']:.3f} | {c['n_pairs']} |")

    ctl = payload["controls"]
    if ctl["shuffled"] or ctl["wrong_latent"]:
        md.append("\n## Controls (amplitude latent)\n")
        if ctl["shuffled"]:
            md.append("Shuffled-target forms (expect E_inv ~ 1 — "
                      "physically meaningless level sets):\n")
            md.append("| shuffle seed | E_inv | R2 resp |")
            md.append("|---:|---:|---:|")
            for c in ctl["shuffled"]:
                md.append(f"| {c['shuffle_seed']} | {fmt(c['e_inv'], 2)} "
                          f"| {fmt(c['r2_response'], 2)} |")
        if ctl["wrong_latent"]:
            md.append("\nWrong-latent specificity (amplitude f vs shape "
                      "latents — expect NOT invariant):\n")
            md.append("| latent | E_inv | R2 resp |")
            md.append("|---:|---:|---:|")
            for c in ctl["wrong_latent"]:
                md.append(f"| z{c['latent']} | {fmt(c['e_inv'], 2)} "
                          f"| {fmt(c['r2_response'], 2)} |")

    g = payload["gate_G4a"]
    if g is not None:
        md.append("\n# Gate G4a\n")
        md.append(f"| bullet | numbers | pass |")
        md.append("|---|---|---|")
        md.append(f"| E_inv <= 0.05 | {fmt(g['e_inv_t1'])} "
                  f"| {'PASS' if g['pass_e_inv'] else 'FAIL'} |")
        md.append(f"| matched response R2 >= 0.9 | {fmt(g['r2_response_t1'])} "
                  f"| {'PASS' if g['pass_response'] else 'FAIL'} |")
        md.append(f"| T2 confirmation | E_inv {fmt(g['e_inv_t2'])}, R2 "
                  f"{fmt(g['r2_response_t2'])} "
                  f"| {'PASS' if g['pass_t2_confirm'] else 'FAIL'} |")
        md.append(f"| controls sane | shuffled ~1, wrong-latent > 0.05 "
                  f"| {'PASS' if g['controls_sane'] else 'FAIL'} |")
        md.append(f"\n**Gate G4a: {'PASS' if g['pass'] else 'FAIL'}** "
                  "(decoder-side bullet lands with Phase 7b)")

    md.append("\n---\n_Generated by `scripts/levelset_audit.py`._")
    return "\n".join(md) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", required=True)
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--results-root", default="results")
    p.add_argument("--semantic-json", default=None)
    p.add_argument("--audit-json", default=None,
                   help="Phase-3 sufficiency_audit JSON for the E_inv "
                        "consistency band (optional).")
    p.add_argument("--latents", nargs="*", type=int, default=None)
    p.add_argument("--n-bins", type=int, default=200)
    p.add_argument("--pairs-per-bin", type=int, default=25)
    p.add_argument("--bin-cap", type=int, default=400)
    p.add_argument("--n-boot", type=int, default=500)
    p.add_argument("--n-seeds", type=int, default=500)
    p.add_argument("--k-nn", type=int, default=40)
    p.add_argument("--caliper-q", type=float, default=0.05)
    p.add_argument("--out", default=None)
    args = p.parse_args()

    model = next((m for m in MODELS if m[1] == args.run), None)
    if model is None:
        print(f"[FAIL] unknown run {args.run}")
        return 1
    _label, run, n_latents, amp_idx = model

    payload = run_audit(run, n_latents, amp_idx, args)

    out = Path(args.out or f"experiments/levelset_audit_{run}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(payload, indent=2))
    print(f"[write] {out.with_suffix('.json')}")
    out.with_suffix(".md").write_text(to_markdown(payload))
    print(f"[write] {out.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
