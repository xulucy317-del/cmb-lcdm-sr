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
            rep = json.loads(rp.read_text())
            rows = [(int(r["complexity"]), float(r["mi_val"]),
                     float(r.get("mi_val_err") or 0.0), expr_of(r))
                    for r in rep.get("all_equations", [])
                    if r.get("mi_val") is not None and np.isfinite(r["mi_val"])]
            fronts.setdefault((cid, k), {})[s] = rows
    return configs, fronts, manifest


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


# ---- outputs ----------------------------------------------------------------

def fmt_inputs(inputs):
    return "{" + ", ".join(inputs) + "}"


def to_markdown(run: str, latents: dict, coverage: dict) -> str:
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

    out = Path(args.out or f"experiments/subset_selection_{run}")
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"run": run, "sweep": args.sweep, "coverage": coverage,
               "latents": latents,
               "generated_by": "scripts/consolidate_subsets.py"}
    out.with_suffix(".json").write_text(json.dumps(payload, indent=2))
    print(f"[write] {out.with_suffix('.json')}")
    out.with_suffix(".md").write_text(to_markdown(run, latents, coverage))
    print(f"[write] {out.with_suffix('.md')}")

    if args.emit_finalists:
        emit_finalists(run, manifest["run_dir"], latents,
                       Path(args.results_root) / run / f"{args.sweep}_finals")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
