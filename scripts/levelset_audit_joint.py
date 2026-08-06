#!/usr/bin/env python
"""Joint (f1, f2) level-set invariance audit — the Phase-7a follow-up after
Phase 6 (docs/discovery_roadmap.md: "re-run on (f1, f2) jointly").

Phase 7a audited the canonical coordinate f1 alone and FAILED G4a everywhere,
with E_inv landing inside the expected band [1−R²_cal, 2(1−R²_cal)]: the
within-level-set movement of mu IS the Phase-3 structured residual. Phase 6
discovered the residual coordinate f2. This audit asks the sharpened
question: does moving theta while holding BOTH coordinates fixed still move
the latent?

Per latent, on T1 (pairs) with a T2 confirmation pass:

  1. **E_inv joint** — quantile-bin f1 and f2 each into n_bins_axis
     equal-count bins; the joint cells (≤ n_bins_axis², delta ~ 7% per axis;
     the within-cell coordinate leakage contributes O(binwidth²/12) ≈ 1e-3
     to E_inv, negligible against the frozen 0.05 threshold) replace the 1-D
     bins; within-cell disjoint pairs maximise nuisance distance in the
     complement of the UNION support S(f1) ∪ S(f2). Same statistic, same
     frozen threshold E_inv <= 0.05, same random-pairing reference (~1).
     Latents whose union support is all 6 have no nuisance direction:
     E_inv is undefined (pass = None) — itself a card-worthy statement
     (the two-stage account spans every parameter).
  2. **Response** — the matched-nuisance response of mu against the
     hierarchical composite yhat = h(f1) + g(f2), where h(f1) = mu − e1
     (the Phase-3 cross-fitted stage-1 prediction) and g is the stage-2
     calibration refit exactly as in consolidate_residual_sr (cross-fitted
     on T1, seed = k; g_full applied for T2). Frozen rule: cross-fitted
     general spline R² >= 0.9 on nuisance-matched rows.
  3. **Expected band** — [1−R²_comb, 2(1−R²_comb)] from the Phase-6 combined
     account: if E_inv lands inside it, audit and calibration agree that
     what moves within joint level sets is exactly the (still-structured)
     stage-2 residual.
  4. **Control** — wrong-latent specificity: the amplitude latent's joint
     cells must NOT be invariant for the other latents (E_inv >> 0.05).
     (The shuffled-target control has no joint analogue — a shuffled run
     has no Phase-6 residual coordinate — and is omitted.)

Gate G4a-joint (amplitude latent): E_inv <= 0.05 AND response R² >= 0.9,
confirmed on T2 — or, when the union support is all 6, the response legs
alone with E_inv reported as undefined.

Reads:  experiments/semantic_recurrence_<run>.json   (f1 canonical)
        experiments/residual_sr_<run>.json           (f2 + combined R²)
        experiments/levelset_audit_<run>.json        (f1-only E_inv column)
        models/<run>/analysis/encoder_means_test.npy
        models/<run>/analysis/residual_z<k>_v1.npy
Writes: experiments/levelset_audit_joint_<run>.{md,json}

    python scripts/levelset_audit_joint.py --run lcdm_tt_beta3e-4
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
from levelset_audit import (SEED_BASE, distance_curve, e_inv_stat, fmt,  # noqa: E402
                            matched_response, pair_within_bins, quantile_bins)

from cmb_lcdm_sr import calibrate, semantics, tiers  # noqa: E402


def _f(v):
    return float(v) if v is not None and np.isfinite(v) else None


def joint_support(expr1, expr2) -> tuple[list, list]:
    """(union support, complement) of two parsed exprs, sampled-basis labels."""
    syms = (semantics._sampledify(expr1).free_symbols
            | semantics._sampledify(expr2).free_symbols)
    support = [lab for lab, s in zip(tiers.SAMPLED_LABELS,
                                     semantics.SAMPLED_SYMBOLS) if s in syms]
    comp = [lab for lab in tiers.SAMPLED_LABELS if lab not in support]
    return support, comp


def audit_joint(f1v: np.ndarray, f2v: np.ndarray, yhat: np.ndarray,
                mu_col: np.ndarray, u_comp: np.ndarray, cfg: dict,
                seed: int = 0) -> dict:
    """E_inv over joint (f1, f2) cells + matched response vs the composite.

    All arrays row-aligned; rows with any non-finite entry are dropped here.
    """
    fin = (np.isfinite(f1v) & np.isfinite(f2v) & np.isfinite(yhat)
           & np.isfinite(mu_col))
    out = {"finite_frac": float(fin.mean())}
    if fin.mean() < 0.5:
        out["error"] = "mostly non-finite"
        return out
    f1v, f2v, yhat, mu = f1v[fin], f2v[fin], yhat[fin], mu_col[fin]
    u_comp = u_comp[fin]
    var_mu = float(np.var(mu))
    rng = np.random.default_rng([SEED_BASE, seed, 47])

    if u_comp.shape[1] > 0:
        nb = cfg["n_bins_axis"]
        cells = quantile_bins(f1v, nb) * (nb + 1) + quantile_bins(f2v, nb)
        i, j, dist = pair_within_bins(f1v, u_comp, bins=cells,
                                      pairs_per_bin=cfg["pairs_per_bin"],
                                      bin_cap=cfg["bin_cap"], rng=rng)
        e_inv, se, d2 = e_inv_stat(mu, i, j, var_mu,
                                   n_boot=cfg["n_boot"], rng=rng)
        perm = rng.permutation(len(f1v) - len(f1v) % 2)
        ri, rj = perm[0::2][:len(i)], perm[1::2][:len(i)]
        e_rand, _, _ = e_inv_stat(mu, ri, rj, var_mu, n_boot=8, rng=rng)
        curve = distance_curve(d2, dist)
        out.update({
            "n_cells": int(len(np.unique(cells))),
            "n_pairs": int(len(i)),
            "e_inv": _f(e_inv), "e_inv_se": _f(se),
            "e_inv_random_ref": _f(e_rand),
            "e_inv_curve": curve,
            "e_inv_top_quartile": (_f(curve[-1]["e_inv"]) if curve else None),
            "mean_pair_nuisance_dist": _f(dist.mean()) if len(dist) else None,
        })
    else:
        out.update({"n_cells": None, "n_pairs": 0, "e_inv": None,
                    "e_inv_se": None, "e_inv_random_ref": None,
                    "e_inv_curve": [], "e_inv_top_quartile": None,
                    "mean_pair_nuisance_dist": None,
                    "note": "union support = all 6 — no nuisance direction"})

    out["response"] = matched_response(yhat, mu, u_comp,
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
    res = json.loads(Path(args.residual_json or
                          f"experiments/residual_sr_{run}.json").read_text())
    res_by_k = {L["latent"]: L for L in res["latents"]}

    ls_f1 = {}
    ls_path = Path(args.levelset_json or
                   f"experiments/levelset_audit_{run}.json")
    if ls_path.exists():
        for L in json.loads(ls_path.read_text())["latents"]:
            ls_f1[L["latent"]] = L["t1"].get("e_inv")

    run_dir = Path("models") / run
    mu = np.load(run_dir / "analysis" / "encoder_means_test.npy")
    theta = np.load(Path(args.dataset_dir) / "theta.npy")
    theta_all = theta[tiers.split_test_indices(args.dataset_dir)]
    mid, half = tiers.load_prior_box(args.dataset_dir)

    cfg = {"n_bins_axis": args.n_bins_axis,
           "pairs_per_bin": args.pairs_per_bin, "bin_cap": args.bin_cap,
           "n_boot": args.n_boot, "n_seeds": args.n_seeds,
           "k_nn": args.k_nn, "caliper_q": args.caliper_q}

    tier_rows = {}
    for name, sl in (("T1", tiers.T1), ("T2", tiers.T2)):
        th = theta_all[sl]
        tier_rows[name] = (th, tiers.theta_to_u(th, mid, half), sl)

    ks = args.latents if args.latents is not None else list(range(n_latents))
    latents_out, amp_cells = [], None
    for k in ks:
        sem_lat = sem["latents"][f"z{k}"]
        canon = next(c for c in sem_lat["clusters"]
                     if c["cluster"] == sem_lat["canonical_cluster"])
        f2_rec = (res_by_k.get(k) or {}).get("f2")
        L = {"latent": k, "audit_expected": AUDIT_EXPECTED[run].get(k),
             "f1_expr": canon["representative"],
             "f2_expr": f2_rec["expr"] if f2_rec else None,
             "e_inv_f1_only": ls_f1.get(k)}
        if f2_rec is None:
            L["note"] = "no Phase-6 residual coordinate"
            latents_out.append(L)
            continue
        expr1 = semantics.parse_expr(L["f1_expr"])
        expr2 = semantics.parse_expr(L["f2_expr"])
        support, comp = joint_support(expr1, expr2)
        comp_idx = [jx for jx, lab in enumerate(tiers.SAMPLED_LABELS)
                    if lab in comp]
        L["support_union"], L["complement"] = support, comp

        r2_comb = (res_by_k[k].get("hierarchy") or {}).get("combined_r2_vs_mu")
        L["r2_comb_phase6"] = r2_comb
        L["e_inv_expected_band"] = ([1.0 - r2_comb, 2.0 * (1.0 - r2_comb)]
                                    if r2_comb is not None else None)

        e1_all = np.load(run_dir / "analysis" / f"residual_z{k}_v1.npy")

        # stage-2 calibration, exact consolidate_residual_sr conventions
        th1, u1, sl1 = tier_rows["T1"]
        f1_t1 = semantics.evaluate_on_theta(expr1, th1)
        f2_t1 = semantics.evaluate_on_theta(expr2, th1)
        cal2 = calibrate.crossfit_calibration(f2_t1, e1_all[sl1],
                                              n_folds=5, seed=k)
        yhat_t1 = (mu[sl1, k] - e1_all[sl1]) + cal2["yhat"]
        L["t1"] = audit_joint(f1_t1, f2_t1, yhat_t1, mu[sl1, k],
                              u1[:, comp_idx], cfg, seed=k)

        th2, u2, sl2 = tier_rows["T2"]
        f1_t2 = semantics.evaluate_on_theta(expr1, th2)
        f2_t2 = semantics.evaluate_on_theta(expr2, th2)
        g_full = cal2["h_full"]
        yhat_t2 = np.where(np.isfinite(f2_t2),
                           (mu[sl2, k] - e1_all[sl2])
                           + g_full(np.nan_to_num(f2_t2)), np.nan)
        L["t2"] = audit_joint(f1_t2, f2_t2, yhat_t2, mu[sl2, k],
                              u2[:, comp_idx], cfg, seed=100 + k)

        L["levelset_pass"] = L["t1"].get("levelset_pass")
        if k == amp_idx:
            amp_cells = (f1_t1, f2_t1, u1)
        latents_out.append(L)
        t1 = L["t1"]
        print(f"  z{k}: |S|={len(support)} comp={{{','.join(comp)}}} "
              f"E_inv={fmt(t1.get('e_inv'))}+/-{fmt(t1.get('e_inv_se'))} "
              f"(f1-only {fmt(L['e_inv_f1_only'])}, "
              f"rand {fmt(t1.get('e_inv_random_ref'), 2)}) "
              f"R2_resp={fmt(t1.get('response', {}).get('r2_response'))} "
              f"T2: E_inv={fmt(L['t2'].get('e_inv'))} "
              f"R2={fmt(L['t2'].get('response', {}).get('r2_response'))} "
              f"-> pass={L['levelset_pass']}", flush=True)

    # ---- wrong-latent specificity (amplitude joint cells) -------------------
    controls = {"wrong_latent": []}
    amp_L = next((L for L in latents_out if L["latent"] == amp_idx), None)
    if amp_L is not None and amp_cells is not None \
            and amp_L.get("complement"):
        f1a, f2a, u1 = amp_cells
        comp_idx = [jx for jx, lab in enumerate(tiers.SAMPLED_LABELS)
                    if lab in amp_L["complement"]]
        _, _, sl1 = tier_rows["T1"]
        nb = cfg["n_bins_axis"]
        fin = np.isfinite(f1a) & np.isfinite(f2a)
        cells = (quantile_bins(f1a[fin], nb) * (nb + 1)
                 + quantile_bins(f2a[fin], nb))
        for L in latents_out:
            if L["latent"] == amp_idx:
                continue
            rng = np.random.default_rng([SEED_BASE, 300 + L["latent"], 47])
            mu_w = mu[sl1, L["latent"]][fin]
            i, j, _dist = pair_within_bins(
                f1a[fin], u1[fin][:, comp_idx], bins=cells,
                pairs_per_bin=cfg["pairs_per_bin"], bin_cap=cfg["bin_cap"],
                rng=rng)
            e_inv, se, _ = e_inv_stat(mu_w, i, j, float(np.var(mu_w)),
                                      n_boot=64, rng=rng)
            controls["wrong_latent"].append(
                {"latent": L["latent"], "e_inv": _f(e_inv),
                 "e_inv_se": _f(se)})

    # ---- gate G4a-joint ------------------------------------------------------
    g4a = None
    if amp_L is not None and "t1" in amp_L:
        t1, t2 = amp_L["t1"], amp_L["t2"]
        e1v, r1 = t1.get("e_inv"), t1.get("response", {}).get("r2_response")
        e2v, r2 = t2.get("e_inv"), t2.get("response", {}).get("r2_response")
        e_defined = e1v is not None
        g4a = {
            "latent": amp_idx, "e_inv_defined": e_defined,
            "e_inv_t1": e1v, "r2_response_t1": r1,
            "e_inv_t2": e2v, "r2_response_t2": r2,
            "pass_e_inv": (bool(e1v <= 0.05) if e_defined else None),
            "pass_response": bool(r1 is not None and r1 >= 0.9),
            "pass_t2_confirm": bool(
                (e2v is not None and e2v <= 0.05 if e_defined else True)
                and r2 is not None and r2 >= 0.9),
            "controls_sane": bool(
                controls["wrong_latent"] == [] or
                all((c["e_inv"] or 0.0) > 0.05
                    for c in controls["wrong_latent"])),
        }
        g4a["pass"] = (bool(g4a["pass_e_inv"] and g4a["pass_response"]
                            and g4a["pass_t2_confirm"])
                       if e_defined else None)
        verdict = ("PASS" if g4a["pass"]
                   else "FAIL" if g4a["pass"] is False
                   else "UNDEFINED (union support = all 6)")
        print(f"  G4a-joint: E_inv {fmt(e1v)} R2 {fmt(r1)} "
              f"T2 confirm {g4a['pass_t2_confirm']} controls "
              f"{g4a['controls_sane']} -> {verdict}")

    return {"run": run, "config": cfg, "seed_base": SEED_BASE,
            "latents": latents_out, "controls": controls,
            "gate_G4a_joint": g4a,
            "generated_by": "scripts/levelset_audit_joint.py"}


# ---- outputs -----------------------------------------------------------------

def to_markdown(payload: dict) -> str:
    run, cfg = payload["run"], payload["config"]
    md = [f"# Joint (f1, f2) level-set audit — `{run}` "
          "(Phase 7a follow-up after Phase 6)\n"]
    md.append(
        f"Pairs are drawn within joint quantile cells "
        f"({cfg['n_bins_axis']}x{cfg['n_bins_axis']} equal-count on f1 x f2, "
        "T1), maximising nuisance distance in the complement of the union "
        "support; frozen rule unchanged (E_inv <= 0.05, matched-response "
        "R2 >= 0.9 vs the hierarchical composite h(f1) + g(f2)). The "
        "`f1-only` column is the Phase-7a E_inv this audit sharpens; the "
        "expected band is [1-R2_comb, 2(1-R2_comb)] from the Phase-6 "
        "combined account. Latents whose union support is all 6 parameters "
        "have no nuisance direction: E_inv undefined, pass = None, and "
        "only the response legs are evidence.\n\n"
        "_Reading the band_: inside = the movement within joint level sets "
        "is exactly the (still-structured) stage-2 residual, audit and "
        "calibration agree. Above = that residual is itself systematic "
        "along the remaining nuisance directions, amplified at the "
        "extreme-separation pairs this audit deliberately draws (the "
        "distance curve rises); the band's factor-2 cap assumes typical, "
        "not extremal, separations. Below = the stage-2 misfit lives along "
        "the support coordinates themselves, so the joint cells pin it "
        "instead of the nuisance moves exposing it.\n")

    md.append("| latent | role | union S | comp | E_inv +/- SE | f1-only "
              "| expected band | rand | R2 resp (n) | T2 E_inv | T2 R2 "
              "| pass |")
    md.append("|---|---|---|---|---|---:|---|---:|---|---:|---:|---|")
    for L in payload["latents"]:
        if "t1" not in L:
            md.append(f"| z{L['latent']} | {L['audit_expected']} | — | — "
                      f"| — | {fmt(L.get('e_inv_f1_only'))} | — | — | — "
                      f"| — | — | {L.get('note', 'n/a')} |")
            continue
        t1, t2 = L["t1"], L["t2"]
        resp = t1.get("response", {})
        band = L.get("e_inv_expected_band")
        md.append(
            f"| z{L['latent']} | {L['audit_expected']} "
            f"| {{{', '.join(L['support_union'])}}} "
            f"| {{{', '.join(L['complement'])}}} "
            f"| {fmt(t1.get('e_inv'))} +/- {fmt(t1.get('e_inv_se'))} "
            f"| {fmt(L.get('e_inv_f1_only'))} "
            f"| {f'{band[0]:.3f}-{band[1]:.3f}' if band else 'n/a'} "
            f"| {fmt(t1.get('e_inv_random_ref'), 2)} "
            f"| {fmt(resp.get('r2_response'))} ({resp.get('n_matched')}) "
            f"| {fmt(t2.get('e_inv'))} "
            f"| {fmt(t2.get('response', {}).get('r2_response'))} "
            f"| {L['levelset_pass']} |")

    for L in payload["latents"]:
        if "t1" not in L:
            continue
        t1 = L["t1"]
        md.append(f"\n## z{L['latent']} — {L['audit_expected']}\n")
        md.append(f"f1 `{L['f1_expr']}`; f2 `{L['f2_expr']}`; "
                  f"{t1.get('n_cells')} joint cells, {t1.get('n_pairs', 0)} "
                  "pairs, mean nuisance distance "
                  f"{fmt(t1.get('mean_pair_nuisance_dist'), 2)}.")
        if t1.get("note"):
            md.append(f"_{t1['note']}_")
        if t1.get("e_inv_curve"):
            md.append("\nE_inv vs nuisance distance:")
            md.append("| d range | E_inv | n |")
            md.append("|---|---:|---:|")
            for c in t1["e_inv_curve"]:
                md.append(f"| {c['d_lo']:.2f}-{c['d_hi']:.2f} "
                          f"| {c['e_inv']:.3f} | {c['n_pairs']} |")

    ctl = payload["controls"]
    if ctl["wrong_latent"]:
        md.append("\n## Wrong-latent specificity (amplitude joint cells)\n")
        md.append("The amplitude (f1, f2) cells must NOT be invariant for "
                  "the other latents:\n")
        md.append("| latent | E_inv +/- SE |")
        md.append("|---:|---|")
        for c in ctl["wrong_latent"]:
            md.append(f"| z{c['latent']} | {fmt(c['e_inv'], 2)} +/- "
                      f"{fmt(c['e_inv_se'], 2)} |")

    g = payload["gate_G4a_joint"]
    if g is not None:
        md.append("\n# Gate G4a-joint\n")
        if not g["e_inv_defined"]:
            md.append("E_inv is undefined for the amplitude latent (union "
                      "support = all 6 parameters — the two-stage account "
                      "leaves no nuisance direction). Response legs: "
                      f"T1 R2 {fmt(g['r2_response_t1'])}, "
                      f"T2 R2 {fmt(g['r2_response_t2'])}.")
        else:
            md.append("| bullet | numbers | pass |")
            md.append("|---|---|---|")
            md.append(f"| E_inv <= 0.05 | {fmt(g['e_inv_t1'])} "
                      f"| {'PASS' if g['pass_e_inv'] else 'FAIL'} |")
            md.append(f"| response R2 >= 0.9 | {fmt(g['r2_response_t1'])} "
                      f"| {'PASS' if g['pass_response'] else 'FAIL'} |")
            md.append(f"| T2 confirmation | E_inv {fmt(g['e_inv_t2'])}, R2 "
                      f"{fmt(g['r2_response_t2'])} "
                      f"| {'PASS' if g['pass_t2_confirm'] else 'FAIL'} |")
            md.append(f"| wrong-latent controls > 0.05 | see table "
                      f"| {'PASS' if g['controls_sane'] else 'FAIL'} |")
            md.append(f"\n**Gate G4a-joint: "
                      f"{'PASS' if g['pass'] else 'FAIL'}**")

    md.append("\n---\n_Generated by `scripts/levelset_audit_joint.py`._")
    return "\n".join(md) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", required=True)
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--semantic-json", default=None)
    p.add_argument("--residual-json", default=None)
    p.add_argument("--levelset-json", default=None)
    p.add_argument("--latents", nargs="*", type=int, default=None)
    p.add_argument("--n-bins-axis", type=int, default=14)
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

    out = Path(args.out or f"experiments/levelset_audit_joint_{run}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(payload, indent=2))
    print(f"[write] {out.with_suffix('.json')}")
    out.with_suffix(".md").write_text(to_markdown(payload))
    print(f"[write] {out.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
