#!/usr/bin/env python
"""Blind variable-subset selection — Phase 4 consolidation (roadmap gap 3).

**4a screen readout.** For every latent and every input subset S (one sweep
config per non-empty subset, ``mode: subsets``), the screen ran 2 seeds at
the reduced budget (ni100, full maxsize 20). Per (latent, S):

  * Î_S = across-seed mean of the front-max val MI, SE = std(ddof=1)/sqrt(n);
  * C_S = the subset's own one-SE knee (smallest c whose 2-seed pooled
    envelope reaches Î_S − SE, reusing the Phase-1 envelope machinery);
  * within-screen sufficiency  η̃_S = Î_S / Î_full  with Î_full the S=all-6
    config of the SAME screen (same ni100 budget — never mix budgets in a
    ratio), SE(η̃) propagated from both numerator and denominator.

**Selection rule** (roadmap Phase 4): keep the Pareto frontier of
(|S|, C_S, −η̃_S) — smaller support, smaller knee complexity, higher
sufficiency — plus every subset that becomes non-dominated when credited
with one SE of its own η̃. Those are the 4b finalists.

**Finalist emission.** ``--emit-finalists`` writes a wrapper-compatible
``tasks.tsv`` (+ manifest) under ``results/<run>/hpsweep_subsets_v1_finals/``
rerunning each finalist at the full protocol (ni200, seeds 0-4). The S=all-6
reference is excluded — its full-protocol runs are ``results/<run>/allparams``.

Reads:  results/<run>/hpsweep_subsets_v1/{manifest.json, c*/z*_seed*/report.json}
Writes: experiments/subset_selection_<run>.{md,json}
        [--emit-finalists] results/<run>/hpsweep_subsets_v1_finals/tasks.tsv

    python scripts/consolidate_subsets.py --run lcdm_tt_beta3e-4
    python scripts/consolidate_subsets.py --run lcdm_tt_ee_lowl --emit-finalists
"""
import argparse
import json
import re
from pathlib import Path

import _bootstrap  # noqa: F401

import numpy as np

from consolidate_allparams import AUDIT_EXPECTED, MODELS, expr_of
from knee_readout import first_crossing, pool_family, seed_envelope

SEED_DIR = re.compile(r"^z(\d+)_seed(\d+)$")
FULL_POOL = ["omega_b", "omega_cdm", "H0", "tau", "A_s", "n_s"]
FINAL_PROTOCOL = {"niterations": 200, "populations": 15, "maxsize": 20,
                  "seeds": [0, 1, 2, 3, 4], "n_samples": 5000}


# ---- loading ----------------------------------------------------------------

def front_rows(rep: dict) -> list:
    """[(complexity, mi, err, expr)] — finite-MI rows of one report."""
    return [(int(r["complexity"]), float(r["mi_val"]),
             float(r.get("mi_val_err") or 0.0), expr_of(r))
            for r in rep.get("all_equations", [])
            if r.get("mi_val") is not None and np.isfinite(r["mi_val"])]


def load_screen(sweep_dir: Path):
    """(configs, fronts): configs by id; fronts[(cid, latent)][seed] = rows."""
    manifest = json.loads((sweep_dir / "manifest.json").read_text())
    configs = {c["config_id"]: c for c in manifest["configs"]}
    fronts = {}
    for cid in configs:
        for rp in sorted((sweep_dir / cid).glob("z*_seed*/report.json")):
            m = SEED_DIR.match(rp.parent.name)
            if not m:
                continue
            k, s = int(m.group(1)), int(m.group(2))
            fronts.setdefault((cid, k), {})[s] = front_rows(
                json.loads(rp.read_text()))
    return configs, fronts, manifest


def load_family(family_dir: Path) -> dict:
    """fronts[latent][seed] = rows from a flat z*_seed*/report.json family
    (e.g. results/<run>/allparams — the full-protocol all-6 reference)."""
    fronts = {}
    for rp in sorted(family_dir.glob("z*_seed*/report.json")):
        m = SEED_DIR.match(rp.parent.name)
        if not m:
            continue
        k, s = int(m.group(1)), int(m.group(2))
        fronts.setdefault(k, {})[s] = front_rows(json.loads(rp.read_text()))
    return fronts


def load_finals(finals_dir: Path):
    """(configs, fronts, coverage) of the 4b rerun tree. Configs come from
    tasks.tsv — the finals manifest has no per-config list."""
    lines = (finals_dir / "tasks.tsv").read_text().strip().splitlines()
    hdr = lines[0].split("\t")
    i_cid, i_inputs = hdr.index("config_id"), hdr.index("inputs")
    configs = {}
    for ln in lines[1:]:
        f = ln.split("\t")
        configs.setdefault(f[i_cid], f[i_inputs].split())
    fronts, n_reports = {}, 0
    for cid in configs:
        for rp in sorted((finals_dir / cid).glob("z*_seed*/report.json")):
            m = SEED_DIR.match(rp.parent.name)
            if not m:
                continue
            k, s = int(m.group(1)), int(m.group(2))
            fronts.setdefault((cid, k), {})[s] = front_rows(
                json.loads(rp.read_text()))
            n_reports += 1
    return configs, fronts, {"n_tasks": len(lines) - 1,
                             "n_reports": n_reports}


def subset_stats(seed_rows: dict, maxsize: int = 20):
    """Î_S, SE, one-SE knee C_S and best form from one subset's seed fronts."""
    per_seed_max = {s: max((mi for _c, mi, *_ in rows), default=np.nan)
                    for s, rows in seed_rows.items()}
    vals = [v for v in per_seed_max.values() if np.isfinite(v)]
    if not vals:
        return None
    mi = float(np.mean(vals))
    se = (float(np.std(vals, ddof=1) / np.sqrt(len(vals)))
          if len(vals) > 1 else 0.0)
    cmax = max([maxsize] + [c for rows in seed_rows.values()
                            for c, *_ in rows])
    grid = np.arange(1, cmax + 1)
    envs = {s: seed_envelope([(c, m, e, x) for c, m, e, x in rows], grid)
            for s, rows in seed_rows.items()}
    pooled = pool_family(envs, grid)
    c_star = first_crossing(grid, pooled["mean"], mi - se)
    best = max((r for rows in seed_rows.values() for r in rows),
               key=lambda r: r[1])
    return {"mi": mi, "se": se, "n_seeds": len(vals),
            "per_seed_max": {str(s): (None if not np.isfinite(v) else float(v))
                             for s, v in sorted(per_seed_max.items())},
            "c_star": c_star,
            "best_expr": best[3], "best_c": best[0], "best_mi": best[1]}


# ---- selection --------------------------------------------------------------

def dominates(a: dict, b: dict) -> bool:
    """a dominates b in (|S| min, C min, eta max)."""
    ge = (a["size"] <= b["size"] and a["c_star"] <= b["c_star"]
          and a["eta"] >= b["eta"])
    strict = (a["size"] < b["size"] or a["c_star"] < b["c_star"]
              or a["eta"] > b["eta"])
    return ge and strict


def select_finalists(entries: list) -> None:
    """Mark 'frontier' and 'keep_1se' in place (entries: one per subset)."""
    for e in entries:
        e["frontier"] = not any(dominates(o, e) for o in entries if o is not e)
    for e in entries:
        if e["frontier"]:
            e["keep_1se"] = False
            continue
        boosted = {**e, "eta": e["eta"] + e["eta_se"]}
        e["keep_1se"] = not any(dominates(o, boosted)
                                for o in entries if o is not e)
    for e in entries:
        e["finalist"] = e["frontier"] or e["keep_1se"]


def consolidate_latent(k: int, configs: dict, fronts: dict) -> dict:
    """All subset entries + selection for one latent (None w/o all-6 ref)."""
    full_cid = next((cid for cid, c in configs.items()
                     if len(c["inputs"]) == len(FULL_POOL)), None)
    if full_cid is None or (full_cid, k) not in fronts:
        return None
    ref = subset_stats(fronts[(full_cid, k)],
                       configs[full_cid].get("maxsize", 20))
    if ref is None or ref["mi"] <= 0:
        return None

    entries = []
    for cid, cfg in configs.items():
        seed_rows = fronts.get((cid, k))
        if not seed_rows:
            continue
        st = subset_stats(seed_rows, cfg.get("maxsize", 20))
        if st is None or st["c_star"] is None:
            continue
        eta = st["mi"] / ref["mi"]
        eta_se = eta * float(np.hypot(
            st["se"] / st["mi"] if st["mi"] else 0.0,
            ref["se"] / ref["mi"]))
        entries.append({
            "config_id": cid, "inputs": cfg["inputs"],
            "size": len(cfg["inputs"]), "c_star": st["c_star"],
            "eta": eta, "eta_se": eta_se, **st,
        })
    select_finalists(entries)
    entries.sort(key=lambda e: (-e["finalist"], e["size"], -e["eta"]))

    staircase = {}
    for e in entries:
        cur = staircase.get(e["size"])
        if cur is None or e["eta"] > cur["eta"]:
            staircase[e["size"]] = {"eta": e["eta"], "eta_se": e["eta_se"],
                                    "config_id": e["config_id"]}
    return {"ref_config": full_cid, "ref": ref, "entries": entries,
            "staircase": {str(s): v for s, v in sorted(staircase.items())},
            "n_subsets_scored": len(entries),
            "n_finalists": sum(e["finalist"] for e in entries)}


# ---- finalist task emission -------------------------------------------------

def emit_finalists(run: str, run_dir: str, latents: dict, out_dir: Path) -> int:
    """Wrapper-compatible tasks.tsv for the 4b full-protocol reruns."""
    cols = ["idx", "config_id", "latent", "seed", "niterations", "populations",
            "maxsize", "extra_json", "run_dir", "inputs", "n_samples",
            "out_dir"]
    rows = []
    for zk, lat in sorted(latents.items()):
        if lat is None:
            continue
        k = int(zk[1:])
        for e in lat["entries"]:
            if not e["finalist"] or e["size"] == len(FULL_POOL):
                continue  # all-6 reference already exists at full protocol
            for s in FINAL_PROTOCOL["seeds"]:
                rows.append([
                    len(rows), e["config_id"], k, s,
                    FINAL_PROTOCOL["niterations"],
                    FINAL_PROTOCOL["populations"], FINAL_PROTOCOL["maxsize"],
                    "{}", run_dir, " ".join(e["inputs"]),
                    FINAL_PROTOCOL["n_samples"],
                    str(out_dir / e["config_id"] / f"z{k}_seed{s}"),
                ])
    out_dir.mkdir(parents=True, exist_ok=True)
    tsv = out_dir / "tasks.tsv"
    with open(tsv, "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(v) for v in r) + "\n")
    (out_dir / "manifest.json").write_text(json.dumps({
        "sweep_name": "subsets_v1_finals", "run_dir": run_dir,
        "run_name": run, "protocol": FINAL_PROTOCOL, "n_tasks": len(rows),
        "generated_by": "scripts/consolidate_subsets.py"}, indent=2))
    print(f"[write] {tsv} ({len(rows)} tasks)")
    if rows:
        print(f"  submit: sbatch --array=0-{len(rows) - 1}%16 "
              f"hpc/slurm_hpsweep_sr.sh {out_dir}")
    return len(rows)


# ---- 4b finals: minimal sufficient subset + gate G2 -------------------------

AMP_EXPECTED = {"A_s", "tau"}


def annotate_minimality(entries: list) -> None:
    """§0.3 subset minimality over the measured candidates, in place: an
    entry is `minimal` iff its Î_S is within one combined SE of every
    measured superset. The comparison runs on Î, not η — both η share the
    all-6 denominator, so it cancels and its noise must not count twice."""
    for e in entries:
        margins = [(o["config_id"], float(e["mi"] - o["mi"]),
                    float(np.hypot(e["se"], o["se"])))
                   for o in entries
                   if o is not e and set(e["inputs"]) < set(o["inputs"])]
        e["minimal"] = all(gap >= -tol for _c, gap, tol in margins)
        worst = min(margins, key=lambda m: m[1] + m[2], default=None)
        e["worst_superset"] = (None if worst is None else
                               {"config_id": worst[0], "gap": worst[1],
                                "tol": worst[2]})


def pick_s_star(entries: list):
    """Smallest |S| (ties -> smaller knee C, then higher Î) among minimal."""
    ok = [e for e in entries if e.get("minimal")]
    if not ok:
        return None
    return min(ok, key=lambda e: (
        e["size"], e["c_star"] if e["c_star"] is not None else 10**6,
        -e["mi"]))


def screen_recurrence(screen_entries: list, target_inputs: list) -> dict:
    """Is S* minimal in EACH screen seed separately (§0.3 'recurrent across
    screen seeds')? Per-seed Î from per_seed_max with the pooled 2-seed SEs
    as tolerance; also each seed's own §0.3 pick (pooled knees as tie-break —
    no per-seed envelope is stored)."""
    seeds = sorted({s for e in screen_entries for s in e["per_seed_max"]})
    tgt = set(target_inputs)
    out = {"seed_minimal": {}, "seed_s_star": {}}
    for s in seeds:
        cand = [{**e, "mi_s": e["per_seed_max"][s]} for e in screen_entries
                if e["per_seed_max"].get(s) is not None]
        for c in cand:
            c["minimal_s"] = all(
                c["mi_s"] >= o["mi_s"] - np.hypot(c["se"], o["se"])
                for o in cand if set(c["inputs"]) < set(o["inputs"]))
        me = next((c for c in cand if set(c["inputs"]) == tgt), None)
        out["seed_minimal"][s] = bool(me and me["minimal_s"])
        ok = [c for c in cand if c["minimal_s"]]
        pick = min(ok, key=lambda c: (
            c["size"], c["c_star"] if c["c_star"] is not None else 10**6,
            -c["mi_s"])) if ok else None
        out["seed_s_star"][s] = pick["inputs"] if pick else None
    out["recurrent"] = bool(seeds) and all(out["seed_minimal"].values())
    picks = list(out["seed_s_star"].values())
    out["same_pick_all_seeds"] = (None not in picks and
                                  len({tuple(p) for p in picks}) == 1)
    return out


def consolidate_finals_latent(k: int, screen_lat: dict, fin_cfgs: dict,
                              fin_fronts: dict, ref_rows: dict):
    """4b table + S* for one latent: full-protocol finalist stats against
    the full-protocol all-6 reference (results/<run>/allparams)."""
    if screen_lat is None or not ref_rows:
        return None
    ref = subset_stats(ref_rows)
    if ref is None or ref["mi"] <= 0:
        return None
    entries = []
    for cid, inputs in fin_cfgs.items():
        seed_rows = fin_fronts.get((cid, k))
        if not seed_rows:
            continue
        st = subset_stats(seed_rows)
        if st is None:
            continue
        eta = st["mi"] / ref["mi"]
        eta_se = eta * float(np.hypot(
            st["se"] / st["mi"] if st["mi"] else 0.0,
            ref["se"] / ref["mi"]))
        entries.append({"config_id": cid, "inputs": inputs,
                        "size": len(inputs), "eta": eta, "eta_se": eta_se,
                        **st})
    if not entries:
        return None
    entries.append({"config_id": "allparams", "inputs": list(FULL_POOL),
                    "size": len(FULL_POOL), "eta": 1.0, "eta_se": 0.0, **ref})
    annotate_minimality(entries)
    s_star = pick_s_star(entries)
    entries.sort(key=lambda e: (e["size"], -e["eta"]))
    rec = (screen_recurrence(screen_lat["entries"], s_star["inputs"])
           if s_star else None)
    staircase = {}
    for e in entries:
        cur = staircase.get(e["size"])
        if cur is None or e["eta"] > cur["eta"]:
            staircase[e["size"]] = {"eta": e["eta"], "eta_se": e["eta_se"],
                                    "config_id": e["config_id"]}
    keep = ("config_id", "inputs", "size", "eta", "eta_se", "c_star",
            "mi", "se")
    return {"ref": ref, "entries": entries,
            "s_star": ({kk: s_star[kk] for kk in keep} if s_star else None),
            "screen_recurrence": rec,
            "staircase": {str(s): v for s, v in sorted(staircase.items())}}


def gate_g2(amp_idx: int, finals: dict) -> dict:
    """Gate G2 (roadmap Phase 4): amplitude S* = {A_s, tau} (or a measured
    superset better by >1 combined SE), reproducible across screen seeds;
    shape-latent S* recurrent across the 2 screen seeds."""
    per = {}
    for zk in sorted(finals):
        fin, k = finals[zk], int(zk[1:])
        is_amp = (k == amp_idx)
        role = "amplitude" if is_amp else "shape"
        if fin is None or fin.get("s_star") is None:
            per[zk] = {"role": role, "verdict": "INCOMPLETE",
                       "reason": "no 4b data"}
            continue
        s = fin["s_star"]
        rec = bool(fin["screen_recurrence"] and
                   fin["screen_recurrence"]["recurrent"])
        got = set(s["inputs"])
        ent = {"role": role, "s_star": sorted(got), "eta": s["eta"],
               "recurrent_across_screen_seeds": rec}
        if is_amp:
            if got == AMP_EXPECTED:
                ent["verdict"] = ("PASS" if rec
                                  else "FAIL (not screen-recurrent)")
            elif got > AMP_EXPECTED:
                two = next((e for e in fin["entries"]
                            if set(e["inputs"]) == AMP_EXPECTED), None)
                beats = bool(two and (s["mi"] - two["mi"]
                                      > np.hypot(s["se"], two["se"])))
                ent["beats_2input_by_gt1se"] = beats
                ent["verdict"] = ("PASS (superset finding)"
                                  if beats and rec else "FAIL")
            else:
                ent["verdict"] = "FAIL"
        else:
            ent["verdict"] = ("PASS" if rec
                              else "ATTENTION (not screen-recurrent)")
        per[zk] = ent
    amp = per.get(f"z{amp_idx}", {})
    amp_pass = str(amp.get("verdict", "")).startswith("PASS")
    flagged = [zk for zk, p in per.items() if p["role"] == "shape"
               and not str(p["verdict"]).startswith("PASS")]
    overall = ("PASS" if amp_pass and not flagged else
               "FAIL (amplitude)" if not amp_pass else
               f"PARTIAL ({', '.join(flagged)} flagged)")
    return {"per_latent": per, "overall": overall}


def recluster_finalists(run: str, fin_cfgs: dict, fin_fronts: dict,
                        allparams: dict, n_latents: int,
                        dataset_dir: str = "data") -> dict:
    """Phase-2 semantic clustering over finalist + all-6 full-protocol fronts
    (roadmap 4b: 'finalist forms re-clustered'). The all-6 family is named
    'allparams' so latent_recurrence's headline R_SR applies to it; per-
    finalist recurrence is read off the returned per-family r_sr. Skips with
    a reason when the Phase-1 knee JSON or the dataset is unavailable."""
    knee_path = Path(f"experiments/knee_readout_{run}.json")
    if not knee_path.exists():
        return {"skipped": f"missing {knee_path}"}
    try:
        from semantic_recurrence import latent_recurrence
        from cmb_lcdm_sr import tiers
        anchors = tiers.anchor_theta(dataset_dir)
        _mid, half = tiers.load_prior_box(dataset_dir)
    except Exception as exc:                                         # noqa: BLE001
        return {"skipped": f"anchors unavailable: {exc}"}
    knee = json.loads(knee_path.read_text())
    out = {}
    for k in range(n_latents):
        fam_runs = {cid: {s: {"rows": rows,
                              "maxsize": FINAL_PROTOCOL["maxsize"]}
                          for s, rows in fin_fronts[(cid, kk)].items()}
                    for (cid, kk) in fin_fronts if kk == k}
        if allparams.get(k):
            fam_runs["allparams"] = {
                s: {"rows": rows, "maxsize": FINAL_PROTOCOL["maxsize"]}
                for s, rows in allparams[k].items()}
        plat = knee["latents"].get(f"z{k}", {}).get("plateau",
                                                    {}).get("mi_plat")
        if not fam_runs or plat is None:
            continue
        lat = latent_recurrence(fam_runs, plat, anchors, half)
        clusters = []
        for c in lat["clusters"][:6]:
            fin_r = {f: r["r"] for f, r in c["r_sr"].items()
                     if f != "allparams"}
            clusters.append({
                "representative": c["representative"],
                "rep_complexity": c["rep_complexity"],
                "rep_support": c["rep_support"],
                "best_mi": c["best_mi"],
                "n_forms": c["n_forms"],
                "r_allparams": c["r_sr"].get("allparams", {}).get("r"),
                "r_finalists": fin_r,
            })
        out[f"z{k}"] = {"canonical_cluster": lat["canonical_cluster"],
                        "n_forms": lat["n_forms"],
                        "clusters": clusters}
    return out


# ---- outputs ----------------------------------------------------------------

def fmt_inputs(inputs):
    return "{" + ", ".join(inputs) + "}"


def finals_markdown(run: str, finals: dict) -> list:
    md = ["\n\n# 4b finals — full protocol (ni200 x 5 seeds)\n"]
    cov = finals["coverage"]
    md.append(f"_Finals coverage: {cov['n_reports']}/{cov['n_tasks']} "
              "reports. Reference = `allparams` (full-protocol all-6, "
              "5 seeds). S* = smallest |S| (ties: smaller knee C) whose Î_S "
              "is within one combined SE of every measured superset; "
              "recurrence = the same minimality holds in each 4a screen "
              "seed separately._\n")
    for zk, fin in sorted(finals["latents"].items()):
        k = int(zk[1:])
        md.append(f"\n## {zk} — {AUDIT_EXPECTED.get(run, {}).get(k, '?')}\n")
        if fin is None:
            md.append("_No 4b data (finals missing or no allparams "
                      "reference)._")
            continue
        md.append(f"Reference Î_all-6 = {fin['ref']['mi']:.3f} +/- "
                  f"{fin['ref']['se']:.3f} nat.")
        s = fin["s_star"]
        if s is not None:
            rec = fin["screen_recurrence"]
            md.append(
                f"**S\\* = {fmt_inputs(s['inputs'])}** — η_S = "
                f"{s['eta']:.3f} +/- {s['eta_se']:.3f}, C_S = {s['c_star']}"
                f", screen-recurrent: {rec['recurrent']} "
                f"(per-seed minimal: "
                + ", ".join(f"s{sd}={v}" for sd, v in
                            sorted(rec["seed_minimal"].items()))
                + f"; per-seed picks agree: {rec['same_pick_all_seeds']}).\n")
        md.append("Staircase (best η_S per support size): " + "; ".join(
            f"|S|={sz}: {v['eta']:.3f}" for sz, v in
            fin["staircase"].items()) + ".\n")
        md.append("| | S | \\|S\\| | C_S | η_S +/- SE | Î_S +/- SE "
                  "| minimal | best form |")
        md.append("|---|---|---:|---:|---|---|---|---|")
        for e in fin["entries"]:
            tag = "**S\\***" if (s is not None and
                                 e["config_id"] == s["config_id"]) else ""
            md.append(
                f"| {tag} | {fmt_inputs(e['inputs'])} | {e['size']} "
                f"| {e['c_star']} | {e['eta']:.3f} +/- {e['eta_se']:.3f} "
                f"| {e['mi']:.3f} +/- {e['se']:.3f} "
                f"| {'yes' if e['minimal'] else 'no'} "
                f"| `{e['best_expr'][:44]}` |")
        cl = finals.get("clusters", {}).get(zk)
        if cl and cl.get("clusters"):
            top = cl["clusters"][0]
            md.append(
                f"\nRe-clustered finalist forms (Phase-2 machinery, "
                f"{cl['n_forms']} forms): top cluster rep "
                f"`{top['representative'][:60]}` (c={top['rep_complexity']}, "
                f"support {fmt_inputs(top['rep_support'])}, "
                f"R_allparams={top['r_allparams']}).")
    g2 = finals["gate_G2"]
    md.append("\n\n# Gate G2\n")
    md.append("| latent | role | S* | η_S | screen-recurrent | verdict |")
    md.append("|---|---|---|---|---|---|")
    for zk, p in sorted(g2["per_latent"].items()):
        s_str = fmt_inputs(p["s_star"]) if p.get("s_star") else "—"
        eta_str = f"{p['eta']:.3f}" if p.get("eta") is not None else "—"
        rec_str = str(p.get("recurrent_across_screen_seeds", "—"))
        md.append(f"| {zk} | {p['role']} | {s_str} | {eta_str} "
                  f"| {rec_str} | **{p['verdict']}** |")
    md.append(f"\n**Overall: {g2['overall']}**")
    return md


def to_markdown(run: str, latents: dict, coverage: dict,
                has_finals: bool = False) -> str:
    md = [f"# Blind subset selection — `{run}` (roadmap Phase 4, screen 4a)\n"]
    md.append(
        "All 63 non-empty input subsets x 2 seeds per latent at the reduced "
        "screen budget (ni100, maxsize 20). Per subset: Î_S (across-seed "
        "mean front-max val MI), its one-SE knee C_S, and within-screen "
        "sufficiency η̃_S = Î_S / Î_all-6 at the SAME budget. Finalists = "
        "Pareto frontier of (|S|, C_S, −η̃_S) plus subsets non-dominated "
        "when credited one SE of their η̃; finalists go to the 4b "
        "full-protocol rerun (ni200, 5 seeds). Gate G2 is judged on 4b, "
        "not on this screen.\n")
    md.append(f"_Screen coverage: {coverage['n_reports']}/"
              f"{coverage['n_tasks']} reports present._\n")
    for zk, lat in sorted(latents.items()):
        k = int(zk[1:])
        md.append(f"\n## {zk} — {AUDIT_EXPECTED.get(run, {}).get(k, '?')}\n")
        if lat is None:
            md.append("_All-6 reference config missing — latent skipped "
                      "(screen incomplete)._")
            continue
        md.append(f"In-screen reference Î_all-6 = {lat['ref']['mi']:.3f} "
                  f"+/- {lat['ref']['se']:.3f} nat "
                  f"({lat['n_subsets_scored']} subsets scored, "
                  f"{lat['n_finalists']} finalists).\n")
        md.append("Staircase (best η̃ per support size): " + "; ".join(
            f"|S|={s}: {v['eta']:.3f}" for s, v in lat["staircase"].items())
            + ".\n")
        md.append("| finalist | S | \\|S\\| | C_S | η̃ +/- SE | Î_S "
                  "| best screen form |")
        md.append("|---|---|---:|---:|---|---:|---|")
        for e in lat["entries"]:
            if not e["finalist"] and e["eta"] < 0.5:
                continue  # keep the table readable; JSON has everything
            tag = ("frontier" if e["frontier"]
                   else "1-SE keep" if e["keep_1se"] else "")
            md.append(
                f"| {tag} | {fmt_inputs(e['inputs'])} | {e['size']} "
                f"| {e['c_star']} | {e['eta']:.3f} +/- {e['eta_se']:.3f} "
                f"| {e['mi']:.3f} | `{e['best_expr'][:44]}` |")
    md.append("\n---\n_Generated by `scripts/consolidate_subsets.py` from "
              "`hpsweep_subsets_v1`._" if has_finals else
              "\n---\n_Generated by `scripts/consolidate_subsets.py` from "
              "`hpsweep_subsets_v1`. 4b fields (S*, full-protocol η_S, "
              "re-clustered finalist forms) are added after the finalist "
              "batch lands._")
    return "\n".join(md) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", required=True)
    p.add_argument("--results-root", default="results")
    p.add_argument("--sweep", default="hpsweep_subsets_v1")
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--emit-finalists", action="store_true")
    p.add_argument("--out", default=None)
    args = p.parse_args()

    model = next((m for m in MODELS if m[1] == args.run), None)
    if model is None:
        print(f"[FAIL] unknown run {args.run}")
        return 1
    _label, run, n_latents, amp_idx = model

    sweep_dir = Path(args.results_root) / run / args.sweep
    configs, fronts, manifest = load_screen(sweep_dir)
    coverage = {"n_tasks": manifest.get("n_tasks"),
                "n_reports": sum(len(v) for v in fronts.values())}
    print(f"[screen] {coverage['n_reports']}/{coverage['n_tasks']} reports")

    latents = {f"z{k}": consolidate_latent(k, configs, fronts)
               for k in range(n_latents)}
    for zk, lat in sorted(latents.items()):
        if lat is None:
            print(f"  {zk}: SKIPPED (no all-6 reference yet)")
            continue
        fins = [e for e in lat["entries"] if e["finalist"]]
        print(f"  {zk}: ref {lat['ref']['mi']:.3f}  finalists "
              f"{lat['n_finalists']}: "
              + ", ".join(fmt_inputs(e["inputs"]) + f" η̃={e['eta']:.2f}"
                          for e in fins[:6]))

    # ---- 4b fold-in (auto-detected once finalist reports exist) -------------
    finals_dir = Path(args.results_root) / run / f"{args.sweep}_finals"
    finals = None
    if (finals_dir / "tasks.tsv").exists():
        fin_cfgs, fin_fronts, fin_cov = load_finals(finals_dir)
        if fin_cov["n_reports"]:
            print(f"[finals] {fin_cov['n_reports']}/{fin_cov['n_tasks']} "
                  "reports")
            allparams = load_family(Path(args.results_root) / run
                                    / "allparams")
            fin_lat = {f"z{k}": consolidate_finals_latent(
                           k, latents.get(f"z{k}"), fin_cfgs, fin_fronts,
                           allparams.get(k))
                       for k in range(n_latents)}
            g2 = gate_g2(amp_idx, fin_lat)
            finals = {"coverage": fin_cov, "latents": fin_lat,
                      "clusters": recluster_finalists(
                          run, fin_cfgs, fin_fronts, allparams, n_latents,
                          dataset_dir=args.dataset_dir),
                      "gate_G2": g2}
            for zk, fin in sorted(fin_lat.items()):
                if fin is None or fin["s_star"] is None:
                    print(f"  {zk}: 4b incomplete")
                    continue
                s, rec = fin["s_star"], fin["screen_recurrence"]
                print(f"  {zk}: S* = {fmt_inputs(s['inputs'])}  "
                      f"eta_S = {s['eta']:.3f} +/- {s['eta_se']:.3f}  "
                      f"recurrent={rec['recurrent']}")
            print(f"[gate G2] {g2['overall']}")

    out = Path(args.out or f"experiments/subset_selection_{run}")
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"run": run, "sweep": args.sweep, "coverage": coverage,
               "latents": latents, "finals": finals,
               "generated_by": "scripts/consolidate_subsets.py"}
    out.with_suffix(".json").write_text(json.dumps(payload, indent=2))
    print(f"[write] {out.with_suffix('.json')}")
    md = to_markdown(run, latents, coverage, has_finals=finals is not None)
    if finals is not None:
        md += "\n".join(finals_markdown(run, finals)) + "\n"
    out.with_suffix(".md").write_text(md)
    print(f"[write] {out.with_suffix('.md')}")

    if args.emit_finalists:
        emit_finalists(run, manifest["run_dir"], latents,
                       Path(args.results_root) / run / f"{args.sweep}_finals")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
