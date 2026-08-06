#!/usr/bin/env python
"""Latent cards — Phase 10 of docs/discovery_roadmap.md (final synthesis).

Pure JSON merge, no new computation: one §0.1 card per latent assembled
from the Phase 1-8 deliverables, status assigned by the frozen §0.3
predicates, plus a gates summary, a controls appendix, and an explicit
deviations register.

Status predicates (§0.3, frozen), with one documented reinterpretation:

  interpreted           minimal-stable S*, R_SR >= 0.8, eta_S >= 0.95,
                        stage-1 residual PASS, eta_post >= 0.95 (and the
                        registered eta_post_hat >= 0.95 demotion guard),
                        level-set: strict f1 pass OR joint (f1,f2) pass
  primarily interpreted eta_S >= 0.95, R_SR >= 0.6, level-set evidence,
                        stage-1 residual FAILS (structured; f2 documented)
  subspace/mixed        no 1-D f reaches eta_S >= 0.9, but the Phase-8
                        probe carries it with <= 3 latents at R2 >= 0.9
  unresolved            anything else

**Deviation D-LS** (registered before per-latent joint results were
computed — see levelset_audit_joint.py): §0.3 wrote "level-set pass" for
the canonical f1 alone, but Phase 7a showed E_inv(f1) equals the Phase-3
structured residual identically (E_inv in [1-R2_cal, 2(1-R2_cal)] for all
11 latents) — the literal leg is unsatisfiable exactly when the residual
leg of "primarily interpreted" fires. The status leg therefore reads:
level-set evidence = strict f1 pass OR joint pass (frozen 0.05/0.9
thresholds unchanged) OR, where the joint union support is all 6 (no
nuisance direction exists), matched response R2 >= 0.9 on both tiers.
A joint FAIL where defined blocks the leg — no tolerance is added.

Reads (experiments/):  knee_readout, semantic_recurrence,
  sufficiency_audit, subset_selection, posterior_ceiling, residual_sr,
  levelset_audit, levelset_audit_joint, decoder_effect, subspace_probe
  (each `<name>_<run>.json`; subspace_probe optional -> column pending)
Writes: experiments/latent_cards_<run>.{md,json}

    python scripts/build_latent_cards.py --run lcdm_tt_beta3e-4
"""
import argparse
import json
from pathlib import Path

import _bootstrap  # noqa: F401,E402

import numpy as np  # noqa: E402

from consolidate_allparams import MODELS  # noqa: E402

# Post-hoc curve labels (assigned AFTER inspecting the derived d_k(l)
# curves, Phase 7b commit fb540a1 — recorded next to, never instead of,
# the quantitative decomposition). None for the TT model: not assigned.
POSTHOC_LABELS = {
    "lcdm_tt_ee_lowl": {0: "omega_cdm envelope / early-ISW",
                        1: "H0 acoustic phase shift",
                        2: "omega_b odd-even contrast",
                        3: "tilt",
                        4: "reionization bump",
                        5: "overall amplitude"},
}

# Register of documented deviations / registered refinements.
DEVIATIONS_GLOBAL = [
    {"id": "D-P2a", "phase": 2, "text":
        "R_SR seed-level tolerance = one cross-seed SD, not SE-of-mean "
        "(the literal §0.3 rule caps R_SR ~0.7 by seed scatter alone even "
        "for perfectly stable coordinates). semantic_recurrence md."},
    {"id": "D-P2b", "phase": 2, "text":
        "cluster representatives must be directly equivalent to a majority "
        "of sampled members (anti-chaining guard on union-find; cohesion "
        "reported per cluster). semantic_recurrence md."},
    {"id": "R-P5", "phase": 5, "text":
        "registered refinement (decided on the synthetic positive control "
        "before real data): eta_post_hat = MI(Z;f)/MI(Z;mu) drives the "
        "0.95 demotion rule; analytic eta_post = MI/I stays the headline. "
        "posterior_ceiling md."},
    {"id": "D-LS", "phase": "7a/10", "text":
        "level-set status leg evaluated on the joint (f1,f2) audit (and "
        "response-only where the joint union support is all 6); the f1-only "
        "E_inv failure is the Phase-3 structured residual identically. "
        "Frozen thresholds unchanged; a joint FAIL still blocks. "
        "levelset_audit_joint md + this docstring."},
]

DEVIATIONS_CARD = {
    ("lcdm_tt_beta3e-4", 2): [{"id": "D-DoD-z2", "phase": 6, "text":
        "Phase-6 amplitude DoD NOT MET, and substantively: f2 keeps tau "
        "(tau-clamping costs 0.20 nat of MI vs e1, Spearman 0.92 < 0.98, "
        "d_grad 0.127 > 0.05 vs the shape-only approximant) — the additive "
        "h(f1)+g(f2) hierarchy cannot absorb the multiplicative "
        "amplitude x shape interaction of the knee forms. Commit a38e6c8."}],
}


def _load(exp_dir: Path, name: str, run: str, required: bool = True):
    p = exp_dir / f"{name}_{run}.json"
    if not p.exists():
        if required:
            raise FileNotFoundError(p)
        return None
    return json.loads(p.read_text())


def _ok(v, thr):
    return bool(v is not None and v >= thr)


def assign_status(legs: dict) -> tuple[str, str]:
    """Frozen §0.3 predicates over the named legs -> (status, reason)."""
    if (legs["minimal_stable"] and _ok(legs["r_sr"], 0.8)
            and _ok(legs["eta_s"], 0.95) and legs["residual1_pass"]
            and _ok(legs["eta_post"], 0.95)
            and _ok(legs["eta_post_hat"], 0.95)
            and (legs["ls_strict"] or legs["ls_joint"] is True)):
        return "interpreted", "all six legs green"
    if (_ok(legs["eta_s"], 0.95) and _ok(legs["r_sr"], 0.6)
            and legs["ls_evidence"] and not legs["residual1_pass"]):
        return ("primarily interpreted",
                "eta_S + R_SR + level-set evidence green; stage-1 residual "
                "structured (f2 documented)")
    if not _ok(legs["eta_s"], 0.90):
        if legs.get("subspace_small") and _ok(legs.get("subspace_r2"), 0.9):
            return "subspace/mixed", "Phase-8 probe carries it (<=3 latents)"
        return "unresolved", "no 1-D f reaches eta_S >= 0.9"
    failed = [n for n, cond in [
        ("level-set evidence", legs["ls_evidence"]),
        ("R_SR >= 0.6", _ok(legs["r_sr"], 0.6)),
        ("eta_S >= 0.95", _ok(legs["eta_s"], 0.95)),
    ] if not cond]
    return "unresolved", "failed: " + ", ".join(failed)


def build_card(run: str, k: int, src: dict) -> dict:
    knee = src["knee"]["latents"][f"z{k}"]
    sem = src["semantic"]["latents"][f"z{k}"]
    canon_cl = next(c for c in sem["clusters"]
                    if c["cluster"] == sem["canonical_cluster"])
    suf = next(L for L in src["sufficiency"]["latents"] if L["latent"] == k)
    can = suf["canonical"]
    fin = src["subsets"]["finals"]["latents"][f"z{k}"]
    post = next(L for L in src["posterior"]["latents"] if L["latent"] == k)
    res = next(L for L in src["residual"]["latents"] if L["latent"] == k)
    ls = next(L for L in src["levelset"]["latents"] if L["latent"] == k)
    lsj = next(L for L in src["levelset_joint"]["latents"]
               if L["latent"] == k)
    dec = next(L for L in src["decoder"]["latents"] if L["latent"] == k)
    sub = None
    if src.get("subspace"):
        sub = next((c for c in src["subspace"]["candidates"]
                    if c["latent"] == k and c["stage"] == "f1"
                    and "probe" in c), None)

    f2 = res.get("f2")
    hier = res.get("hierarchy") or {}
    st2 = res.get("stage2_residual") or {}
    g2 = (src["subsets"]["finals"].get("gate_G2") or {}) \
        .get("per_latent", {}).get(f"z{k}", {})

    card = {
        "latent": k,
        "role": knee.get("audit_expected"),
        "posthoc_label": POSTHOC_LABELS.get(run, {}).get(k),
        "f1": {
            "expr": canon_cl["representative"],
            "complexity": canon_cl["rep_complexity"],
            "support": canon_cl["rep_support"],
            "cluster": sem["canonical_cluster"],
            "r_sr": canon_cl["r_sr_headline"],
            "cohesion": canon_cl.get("pair_cohesion"),
        },
        "knee": {
            "c_star": knee["c_star"],
            "mi_plat": knee["plateau"]["mi_plat"],
            "mi_plat_se": knee["plateau"]["se"],
            "family": knee["plateau"]["family"],
            "mi_at_c10": knee.get("mi_at_c10"),
            "classification": knee.get("classification"),
        },
        "s_star": {
            "inputs": fin["s_star"]["inputs"],
            "size": fin["s_star"]["size"],
            "eta": fin["s_star"]["eta"],
            "eta_se": fin["s_star"]["eta_se"],
            "screen_recurrent": fin["screen_recurrence"]["recurrent"],
            "gate_G2_verdict": g2.get("verdict"),
        },
        "sufficiency": {
            "eta_s": fin["s_star"]["eta"],
            "eta_plat": can.get("eta_plat"),
            "eta_post": post.get("canonical_eta_post"),
            "eta_post_se": post.get("canonical_eta_post_se"),
            "eta_post_hat": post.get("canonical_eta_post_hat"),
            "eta_post_hat_se": post.get("canonical_eta_post_hat_se"),
            "eta_plat_comb": hier.get("eta_plat_comb"),
            "eta_post_comb": hier.get("eta_post_comb"),
            "eta_post_hat_comb": hier.get("eta_post_hat_comb"),
        },
        "ceiling": {
            "I": post["ceiling"]["I"], "se": post["ceiling"]["se"],
            "snr": post["noise"]["snr"],
        },
        "signature": {
            "g_j": can.get("signature"),
            "sobol_ST": can.get("sobol_ST"),
            "ratio_pairs": can.get("ratio_pairs"),
            "decoder_cos_g": dec.get("cos_signature_p3"),
        },
        "residual_stage1": {
            "r2_cal": can.get("r2_cal"), "r2_res": can.get("r2_res"),
            "residual_pass": can.get("residual_pass"),
            "loadings": can.get("residual_loadings"),
        },
        "f2": (None if f2 is None else {
            "expr": f2["expr"], "support": f2["support"],
            "shape_sector": f2["shape_sector"], "r_sr": f2["r_sr"],
            "mi_vs_e1": f2["mi_vs_e1"],
            "r2_stage2": hier.get("r2_stage2_of_residual"),
            "combined_r2_vs_mu": hier.get("combined_r2_vs_mu"),
            "stage2_residual_pass": st2.get("residual_pass"),
            "stage2_loadings": st2.get("loadings"),
        }),
        "levelset": {
            "f1_e_inv": ls["t1"].get("e_inv"),
            "f1_e_inv_se": ls["t1"].get("e_inv_se"),
            "f1_band": ls.get("e_inv_expected_band"),
            "f1_response_r2": (ls["t1"].get("response") or {})
            .get("r2_response"),
            "f1_response_r2_t2": (ls["t2"].get("response") or {})
            .get("r2_response"),
            "f1_pass": ls.get("levelset_pass"),
            "joint_e_inv": lsj.get("t1", {}).get("e_inv"),
            "joint_band": lsj.get("e_inv_expected_band"),
            "joint_response_r2": (lsj.get("t1", {}).get("response") or {})
            .get("r2_response"),
            "joint_response_r2_t2": (lsj.get("t2", {}).get("response") or {})
            .get("r2_response"),
            "joint_pass": lsj.get("levelset_pass"),
            "joint_union": lsj.get("support_union"),
            "joint_complement": lsj.get("complement"),
        },
        "decoder": {
            "a": dec.get("a_postlasso") or dec.get("a_ols"),
            "r2_W": dec.get("r2_W"), "amp_mass": dec.get("amp_mass"),
            "frac_brk": dec.get("frac_brk"), "r_dec": dec.get("r_dec"),
        },
        "subspace": (None if sub is None else {
            "a_star": sub["probe"]["a_star"]["support"],
            "axis_aligned": sub["probe"]["axis_aligned"],
            "r2_own": sub["probe"].get("r2_own"),
            "r2_full": sub["probe"]["r2_full"],
            "r2_t2": sub["probe"].get("r2_t2"),
            "top_pair": [sub["redundancy"]["top1"],
                         sub["redundancy"]["top2"]],
            "redundancy_2_given_1":
                sub["redundancy"]["top2_given_top1"].get("redundancy"),
        }),
    }

    resp_ok = (_ok(card["levelset"]["f1_response_r2"], 0.9)
               and _ok(card["levelset"]["f1_response_r2_t2"], 0.9))
    joint_resp_ok = (_ok(card["levelset"]["joint_response_r2"], 0.9)
                     and _ok(card["levelset"]["joint_response_r2_t2"], 0.9))
    jp = card["levelset"]["joint_pass"]
    legs = {
        "minimal_stable": bool(card["s_star"]["screen_recurrent"]),
        "r_sr": card["f1"]["r_sr"],
        "eta_s": card["sufficiency"]["eta_s"],
        "residual1_pass": bool(card["residual_stage1"]["residual_pass"]),
        "eta_post": card["sufficiency"]["eta_post"],
        "eta_post_hat": card["sufficiency"]["eta_post_hat"],
        "ls_strict": bool(card["levelset"]["f1_pass"]),
        "ls_joint": jp,
        "ls_evidence": bool(card["levelset"]["f1_pass"] or jp is True
                            or (jp is None and joint_resp_ok)),
        "response_ok": resp_ok,
        "subspace_small": (None if card["subspace"] is None
                           else len(card["subspace"]["a_star"]) <= 3),
        "subspace_r2": (None if card["subspace"] is None
                        else card["subspace"]["r2_full"]),
    }
    card["legs"] = legs
    card["status"], card["status_reason"] = assign_status(legs)

    devs = list(DEVIATIONS_CARD.get((run, k), []))
    if not legs["ls_strict"] and legs["ls_evidence"]:
        devs.append({"id": "D-LS", "phase": "7a/10", "text":
                     ("level-set leg via joint (f1,f2) audit"
                      if jp is True else
                      "level-set leg via response-only (joint union "
                      "support = all 6)")})
    if not card["s_star"]["screen_recurrent"]:
        devs.append({"id": "N-G2", "phase": 4, "text":
                     "S* not recurrent across the two screen seeds "
                     f"({card['s_star']['gate_G2_verdict']})"})
    card["deviations"] = devs
    return card


def build_run(run: str, n_latents: int, amp_idx: int, exp_dir: Path) -> dict:
    src = {
        "knee": _load(exp_dir, "knee_readout", run),
        "semantic": _load(exp_dir, "semantic_recurrence", run),
        "sufficiency": _load(exp_dir, "sufficiency_audit", run),
        "subsets": _load(exp_dir, "subset_selection", run),
        "posterior": _load(exp_dir, "posterior_ceiling", run),
        "residual": _load(exp_dir, "residual_sr", run),
        "levelset": _load(exp_dir, "levelset_audit", run),
        "levelset_joint": _load(exp_dir, "levelset_audit_joint", run),
        "decoder": _load(exp_dir, "decoder_effect", run),
        "subspace": _load(exp_dir, "subspace_probe", run, required=False),
    }
    cards = [build_card(run, k, src) for k in range(n_latents)]

    gates = {
        "G1": {"verdict": "PASS", "source": f"sufficiency_audit_{run}.md "
               "(amplitude positive control; both models 2026-08-03)"},
        "G2": src["subsets"]["finals"].get("gate_G2"),
        "G3": src["posterior"].get("gate_G3"),
        "G4a_f1_only": src["levelset"].get("gate_G4a"),
        "G4a_joint": src["levelset_joint"].get("gate_G4a_joint"),
        "G4b": src["decoder"].get("gate_G4b"),
    }
    controls = {
        "stage1_permutation": [
            {"latent": L["latent"],
             "r2_null_p975": L["canonical"].get("r2_null_p975"),
             "mi_res_p975_max": L["canonical"].get("mi_res_p975_max")}
            for L in src["sufficiency"]["latents"]],
        "residual_shuffled": src["residual"].get("controls"),
        "levelset_controls": src["levelset"].get("controls"),
        "levelset_joint_wrong_latent":
            (src["levelset_joint"].get("controls") or {}).get("wrong_latent"),
        "subspace_shuffled_probe_max": (
            None if not src.get("subspace") else max(
                (c["probe"]["r2_full_shuffled"]
                 for c in src["subspace"]["candidates"] if "probe" in c),
                default=None)),
    }
    return {"run": run, "amp_idx": amp_idx, "cards": cards, "gates": gates,
            "controls": controls, "deviations_global": DEVIATIONS_GLOBAL,
            "subspace_pending": src.get("subspace") is None,
            "generated_by": "scripts/build_latent_cards.py"}


# ---- markdown ----------------------------------------------------------------

def fmt(x, prec=3):
    if x is None:
        return "n/a"
    if isinstance(x, bool):
        return str(x)
    return f"{x:.{prec}f}"


def _pm(v, se, prec=3):
    return f"{fmt(v, prec)} +/- {fmt(se, prec)}"


def _sup(labels) -> str:
    return "{" + ", ".join(labels) + "}" if labels else "n/a"


def to_markdown(payload: dict) -> str:
    run = payload["run"]
    md = [f"# Latent cards — `{run}` (roadmap Phase 10)\n"]
    md.append("One §0.1 card per latent, statuses from the frozen §0.3 "
              "predicates (deviation register at the end; D-LS defines the "
              "level-set leg). All numbers are merged verbatim from the "
              "Phase 1-8 deliverables named on each line — no new "
              "computation.\n")
    if payload.get("subspace_pending"):
        md.append("**NOTE: Phase-8 subspace columns pending** (probe jobs "
                  "not yet consolidated when this was built).\n")

    md.append("| latent | role | status | f1 | eta_S | eta_post_hat "
              "| eta_ph_comb | R_SR | E_inv joint | axis-aligned |")
    md.append("|---|---|---|---|---:|---:|---:|---:|---:|---|")
    for c in payload["cards"]:
        sub = c["subspace"]
        md.append(
            f"| z{c['latent']} | {c['role']} | **{c['status']}** "
            f"| `{c['f1']['expr'][:36]}` "
            f"| {fmt(c['sufficiency']['eta_s'])} "
            f"| {fmt(c['sufficiency']['eta_post_hat'])} "
            f"| {fmt(c['sufficiency']['eta_post_hat_comb'])} "
            f"| {fmt(c['f1']['r_sr'], 2)} "
            f"| {fmt(c['levelset']['joint_e_inv'])} "
            f"| {'pending' if sub is None else sub['axis_aligned']} |")

    for c in payload["cards"]:
        k = c["latent"]
        md.append(f"\n## z{k} — {c['role']}"
                  + (f" ({c['posthoc_label']})" if c["posthoc_label"]
                     else "") + "\n")
        md.append(f"**Status: {c['status']}** — {c['status_reason']}\n")
        f1, s = c["f1"], c["s_star"]
        md.append(f"* f1 `{f1['expr']}` (C={f1['complexity']}, support "
                  f"{_sup(f1['support'])}, R_SR {fmt(f1['r_sr'], 2)}, "
                  f"cohesion {fmt(f1['cohesion'], 2)}) "
                  "[semantic_recurrence]")
        kn = c["knee"]
        md.append(f"* knee c* = {kn['c_star']}, plateau "
                  f"{_pm(kn['mi_plat'], kn['mi_plat_se'])} nat "
                  f"({kn['family']}), MI@c<=10 {fmt(kn['mi_at_c10'])}, "
                  f"envelope: {kn['classification']} [knee_readout]")
        md.append(f"* S* = {_sup(s['inputs'])} (|S|={s['size']}, eta_S "
                  f"{_pm(s['eta'], s['eta_se'])}, screen-recurrent "
                  f"{s['screen_recurrent']}) [subset_selection]")
        suf, ce = c["sufficiency"], c["ceiling"]
        md.append(f"* ceiling I(Z;theta) = {_pm(ce['I'], ce['se'])} nat "
                  f"(SNR {fmt(ce['snr'], 1)}); eta_post "
                  f"{_pm(suf['eta_post'], suf['eta_post_se'])}, "
                  f"eta_post_hat {_pm(suf['eta_post_hat'],
                                      suf['eta_post_hat_se'])}; "
                  f"combined (f1+f2): eta_post_hat "
                  f"{fmt(suf['eta_post_hat_comb'])}, eta_plat "
                  f"{fmt(suf['eta_plat_comb'])} [posterior_ceiling, "
                  "residual_sr]")
        sig = c["signature"]
        if sig["g_j"]:
            gj = " ".join(f"{n}={v:.2f}" for n, v in
                          zip(["ob", "oc", "H0", "tau", "lnAs", "ns"],
                              sig["g_j"]) if v and v > 0.005)
            md.append(f"* signature g_j: {gj}; decoder cos_g "
                      f"{fmt(sig['decoder_cos_g'], 2)}"
                      + (f"; ratio pairs: "
                         + "; ".join(f"({p['pair'][0]},{p['pair'][1]}) "
                                     f"r={p['r_raw']:+.3f}"
                                     for p in sig["ratio_pairs"])
                         if sig["ratio_pairs"] else "")
                      + " [sufficiency_audit, decoder_effect]")
        r1 = c["residual_stage1"]
        md.append(f"* stage-1 residual: R2_cal {fmt(r1['r2_cal'])}, "
                  f"R2_res {fmt(r1['r2_res'])} -> "
                  f"{'PASS' if r1['residual_pass'] else 'FAIL'} "
                  f"(loadings {_sup(r1['loadings'])}) [sufficiency_audit]")
        if c["f2"]:
            f2 = c["f2"]
            md.append(f"* f2 `{f2['expr']}` (support {_sup(f2['support'])}, "
                      f"shape-sector {f2['shape_sector']}, R_SR "
                      f"{fmt(f2['r_sr'], 2)}, MI vs e1 "
                      f"{fmt(f2['mi_vs_e1'])}); combined R2(mu) "
                      f"{fmt(f2['combined_r2_vs_mu'])}; stage-2 residual "
                      f"{'PASS' if f2['stage2_residual_pass'] else 'FAIL'} "
                      f"[residual_sr]")
        lv = c["levelset"]
        band = lv["f1_band"]
        jband = lv["joint_band"]
        md.append(
            f"* level sets: f1-only E_inv {fmt(lv['f1_e_inv'])} "
            f"(band {f'{band[0]:.3f}-{band[1]:.3f}' if band else 'n/a'}, "
            f"resp R2 {fmt(lv['f1_response_r2'], 2)}) -> "
            f"{'PASS' if lv['f1_pass'] else 'FAIL'}; joint (f1,f2) E_inv "
            f"{fmt(lv['joint_e_inv'])} "
            f"(band {f'{jband[0]:.3f}-{jband[1]:.3f}' if jband else 'n/a'}, "
            f"resp {fmt(lv['joint_response_r2'], 2)}) -> "
            f"{'undefined (union=all 6)' if lv['joint_pass'] is None else 'PASS' if lv['joint_pass'] else 'FAIL'} "
            "[levelset_audit, levelset_audit_joint]")
        dc = c["decoder"]
        a_str = ("n/a" if not dc["a"] else " ".join(
            f"{n}={v:+.2f}" for n, v in
            zip(["ob", "oc", "H0", "tau", "lnAs", "ns"], dc["a"])
            if v is not None and abs(v) >= 0.005))
        # r_dec is a within-amplitude-pair split: rendered only on the
        # amplitude card (G4b evaluates it there; elsewhere it is not a
        # meaningful readout and for TT the pair is collinear anyway).
        show_rdec = (k == payload["amp_idx"] and dc["r_dec"] is not None)
        md.append(f"* decoder effect: a = [{a_str}], R2_W "
                  f"{fmt(dc['r2_W'], 3)}, amp mass {fmt(dc['amp_mass'], 2)}"
                  + (f", r_dec {fmt(dc['r_dec'], 2)}" if show_rdec else "")
                  + f", frac_brk {fmt(dc['frac_brk'], 2)} [decoder_effect]")
        if c["subspace"]:
            sb = c["subspace"]
            md.append(f"* subspace probe: A* = {_sup([f'z{i}' for i in sb['a_star']])} "
                      f"(axis-aligned {sb['axis_aligned']}), R2 own "
                      f"{fmt(sb['r2_own'])} / full {fmt(sb['r2_full'])} "
                      f"(T2 {fmt(sb['r2_t2'])}); top pair "
                      f"(z{sb['top_pair'][0]}, z{sb['top_pair'][1]}), "
                      f"redundancy(2|1) {fmt(sb['redundancy_2_given_1'], 2)} "
                      "[subspace_probe]")
        else:
            md.append("* subspace probe: **pending**")
        if c["deviations"]:
            md.append("* deviations: "
                      + "; ".join(f"**{d['id']}** {d['text']}"
                                  for d in c["deviations"]))

    g = payload["gates"]
    md.append("\n# Gates\n")
    md.append("| gate | verdict | source |")
    md.append("|---|---|---|")
    md.append(f"| G1 (amplitude positive control) | {g['G1']['verdict']} "
              f"| {g['G1']['source']} |")

    def _passfail(d, key="pass"):
        if d is None:
            return "n/a"
        v = d.get(key)
        return "PASS" if v else ("UNDEFINED" if v is None else "FAIL")
    md.append(f"| G2 (S* selection) | see per-latent verdicts "
              f"| subset_selection_{run}.md |")
    md.append(f"| G3 (posterior ceiling, DPI) | {_passfail(g['G3'])} "
              f"| posterior_ceiling_{run}.md |")
    md.append(f"| G4a (level sets, f1-only) | {_passfail(g['G4a_f1_only'])} "
              f"| levelset_audit_{run}.md |")
    md.append(f"| G4a-joint (level sets, f1+f2) | "
              f"{_passfail(g['G4a_joint'])} "
              f"| levelset_audit_joint_{run}.md |")
    md.append(f"| G4b (decoder triangulation) | {_passfail(g['G4b'])} "
              f"| decoder_effect_{run}.md |")

    md.append("\n# Controls appendix\n")
    ctl = payload["controls"]
    md.append("| control | value |")
    md.append("|---|---|")
    for L in ctl["stage1_permutation"]:
        md.append(f"| stage-1 perm null z{L['latent']}: R2 p97.5 / "
                  f"max-MI p97.5 | {fmt(L['r2_null_p975'])} / "
                  f"{fmt(L['mi_res_p975_max'])} |")
    for c in (ctl.get("residual_shuffled") or []):
        md.append(f"| shuffled-residual SR (seed {c.get('shuffle_seed')}) "
                  f"best MI | {fmt(c.get('best_mi_vs_true'))} |")
    lc = ctl.get("levelset_controls") or {}
    for c in (lc.get("shuffled") or []):
        md.append(f"| level-set shuffled form (seed {c['shuffle_seed']}) "
                  f"E_inv | {fmt(c['e_inv'], 2)} |")
    wl = (lc.get("wrong_latent") or []) + \
        (ctl.get("levelset_joint_wrong_latent") or [])
    if wl:
        vals = ", ".join(f"z{c['latent']} {fmt(c['e_inv'], 2)}" for c in wl)
        md.append(f"| wrong-latent E_inv (f1-only + joint) | {vals} |")
    if ctl.get("subspace_shuffled_probe_max") is not None:
        md.append(f"| subspace shuffled-probe max R2 | "
                  f"{fmt(ctl['subspace_shuffled_probe_max'])} |")

    md.append("\n# Deviation register\n")
    for d in payload["deviations_global"]:
        md.append(f"* **{d['id']}** (phase {d['phase']}): {d['text']}")

    md.append("\n---\n_Generated by `scripts/build_latent_cards.py`._")
    return "\n".join(md) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", required=True)
    p.add_argument("--experiments-dir", default="experiments")
    p.add_argument("--out", default=None)
    args = p.parse_args()

    model = next((m for m in MODELS if m[1] == args.run), None)
    if model is None:
        print(f"[FAIL] unknown run {args.run}")
        return 1
    _label, run, n_latents, amp_idx = model

    payload = build_run(run, n_latents, amp_idx, Path(args.experiments_dir))
    statuses = [c["status"] for c in payload["cards"]]
    for c in payload["cards"]:
        print(f"  z{c['latent']}: {c['status']} ({c['status_reason']})")
    print(f"  -> {statuses.count('interpreted')} interpreted, "
          f"{statuses.count('primarily interpreted')} primarily, "
          f"{statuses.count('subspace/mixed')} subspace/mixed, "
          f"{statuses.count('unresolved')} unresolved")

    out = Path(args.out or f"experiments/latent_cards_{run}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(payload, indent=2))
    print(f"[write] {out.with_suffix('.json')}")
    out.with_suffix(".md").write_text(to_markdown(payload))
    print(f"[write] {out.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
