#!/usr/bin/env python
"""Consolidate a PySR hyperparameter sweep into one comparison summary.

Reads the manifest + per-run report.json written by scripts/sweep_blind_sr.py
plan / hpc/slurm_hpsweep_sr.sh and writes

    experiments/hpsweep_<sweep>_<run>.md    (comparison tables — the deliverable)
    experiments/hpsweep_<sweep>_<run>.json  (machine-readable payload)

Per config x latent, aggregated over seeds:

* top val MI      — argmax held-out GMM-MI over the Pareto front (the study's
                    headline readout). Caveat: with all 6 inputs exposed this
                    rises with any capacity knob (maxsize, iterations, ...), so
                    it measures search power, not parsimony.
* MI @ c<=CAP     — best val MI among front equations with complexity <= CAP
                    (default 10): a budget-matched readout comparable across
                    configs with different maxsize.
* parsimonious c  — complexity of the lowest-complexity equation within 1 sigma
                    of the top val MI (undoes MI tie-break noise among monotone
                    wrappers; same rule as consolidate_allparams).
* amplitude latent only: implied tau exponent r = (df/dtau)/(df/dlnA_s) of the
  top form (textbook -2), and the strict-textbook / A_s*tau-bilinear scan over
  every front equation.
* fit seconds     — the compute price of the config.

Star-mode sweeps additionally get a one-factor-effect section per axis.
Reports whose recorded pysr_kwargs disagree with the manifest config (stale
outputs from a re-planned sweep) are dropped with a warning.
"""
import argparse
import json
from pathlib import Path

import _bootstrap  # noqa: F401

import numpy as np

from consolidate_allparams import (
    AUDIT_EXPECTED,
    MODELS,
    _BILINEAR,
    amp_ratio,
    expr_of,
    fmt_mi,
    pick_forms,
    textbook_hit,
    vars_used,
)
from sweep_blind_sr import CORE_KEYS, load_manifest

RUN_INFO = {run: (label, n_lat, amp) for label, run, n_lat, amp in MODELS}


def mi_at_cap(rep: dict, cap: int):
    """Best val MI among Pareto equations with complexity <= cap."""
    eqs = [r for r in rep.get("all_equations", [])
           if r.get("mi_val") is not None and np.isfinite(r["mi_val"])
           and r["complexity"] <= cap]
    return max(eqs, key=lambda r: r["mi_val"]) if eqs else None


def summarize_report(rep: dict, cap: int, is_amp: bool) -> dict:
    """One run's report.json -> the per-seed metric row."""
    top, pars = pick_forms(rep)
    if top is None:
        return None
    capped = mi_at_cap(rep, cap)
    front = [expr_of(r) for r in rep.get("all_equations", [])]
    row = {
        "seed": rep.get("pysr_kwargs", {}).get("random_state", -1),
        "top_mi": top["mi_val"], "top_mi_err": top.get("mi_val_err"),
        "top_complexity": top["complexity"], "top_form": expr_of(top),
        "pars_mi": pars["mi_val"], "pars_complexity": pars["complexity"],
        "pars_form": expr_of(pars),
        "mi_cap": capped["mi_val"] if capped else None,
        "mi_cap_complexity": capped["complexity"] if capped else None,
        "mi_cap_form": expr_of(capped) if capped else None,
        "vars_top": vars_used(expr_of(top)),
        "n_equations": len(front),
        "fit_seconds": rep.get("fit_seconds"),
    }
    if is_amp:
        row["r_top"] = amp_ratio(expr_of(top))
        row["textbook_hits"] = sum(textbook_hit(e) for e in front)
        row["bilinear_hits"] = sum(bool(_BILINEAR.search(e)) for e in front)
    return row


def config_matches_report(cfg: dict, rep: dict) -> bool:
    kw = rep.get("pysr_kwargs") or {}
    if any(kw.get(k) != cfg[k] for k in CORE_KEYS):
        return False
    return all(kw.get(k) == v for k, v in (cfg.get("extra") or {}).items())


def _mean_std(vals):
    vals = [v for v in vals if v is not None and np.isfinite(v)]
    if not vals:
        return None, None
    return float(np.mean(vals)), (float(np.std(vals)) if len(vals) > 1 else None)


def aggregate(per_seed: list, is_amp: bool) -> dict:
    agg = {"n_seeds": len(per_seed), "per_seed": per_seed}
    for key in ("top_mi", "mi_cap", "pars_mi"):
        m, s = _mean_std([r[key] for r in per_seed])
        agg[f"{key}_mean"], agg[f"{key}_std"] = m, s
    agg["pars_complexity_mean"], _ = _mean_std([r["pars_complexity"] for r in per_seed])
    agg["fit_seconds_mean"], _ = _mean_std([r["fit_seconds"] for r in per_seed])
    if is_amp:
        r_all = [r["r_top"] for r in per_seed if r.get("r_top") is not None]
        agg["r_top_mean"], agg["r_top_std"] = _mean_std(r_all)
        agg["r_top_n"] = len(r_all)
        agg["textbook_hits"] = sum(r.get("textbook_hits", 0) for r in per_seed)
        agg["bilinear_hits"] = sum(r.get("bilinear_hits", 0) for r in per_seed)
    return agg


def changed_axis(cfg: dict, base: dict):
    """(axis_key, value) if cfg differs from the baseline in exactly one key."""
    diffs = [(k, cfg[k]) for k in CORE_KEYS if cfg[k] != base[k]]
    b_extra, c_extra = base.get("extra") or {}, cfg.get("extra") or {}
    for k in set(b_extra) | set(c_extra):
        if b_extra.get(k) != c_extra.get(k):
            diffs.append((k, c_extra.get(k)))
    return diffs[0] if len(diffs) == 1 else None


def _fmt(v, spec="{:.3f}", na="n/a"):
    return spec.format(v) if v is not None else na


def _delta(cfg_val, base_val):
    if cfg_val is None or base_val is None:
        return "n/a"
    return f"{cfg_val - base_val:+.3f}"


def consolidate(sweep_dir: Path, cap: int):
    manifest = load_manifest(sweep_dir)
    spec = manifest["spec"]
    run_name = manifest["run_name"]
    label, _, amp_idx = RUN_INFO.get(run_name, (run_name, None, None))
    mode = spec.get("mode", "star")

    tasks_by_cfg = {}
    for t in manifest["tasks"]:
        tasks_by_cfg.setdefault(t["config_id"], []).append(t)

    payload = {"sweep_name": manifest["sweep_name"], "run_name": run_name,
               "model_label": label, "mode": mode, "cap": cap, "spec": spec,
               "amplitude_latent": amp_idx, "configs": []}
    n_expected = len(manifest["tasks"])
    n_loaded = 0

    for cfg in manifest["configs"]:
        entry = {**{k: cfg[k] for k in ("config_id", "label", *CORE_KEYS, "extra")},
                 "latents": {}}
        for latent in spec["latents"]:
            is_amp = latent == amp_idx
            rows = []
            for t in tasks_by_cfg[cfg["config_id"]]:
                if t["latent"] != latent:
                    continue
                path = Path(t["out_dir"]) / "report.json"
                if not path.exists():
                    continue
                rep = json.loads(path.read_text())
                if not config_matches_report(cfg, rep):
                    print(f"[warn] {path}: pysr_kwargs disagree with manifest "
                          f"config {cfg['config_id']} — stale output? skipped")
                    continue
                row = summarize_report(rep, cap, is_amp)
                if row is not None:
                    rows.append(row)
                    n_loaded += 1
            entry["latents"][f"z{latent}"] = aggregate(rows, is_amp)
        payload["configs"].append(entry)

    payload["n_tasks"] = n_expected
    payload["n_reports_loaded"] = n_loaded

    base = next((c for c in payload["configs"] if c["label"] == "baseline"), None)

    # ---- markdown -----------------------------------------------------------
    md = []
    md.append(f"# PySR hyperparameter sweep `{manifest['sweep_name']}` — "
              f"{label} (`models/{run_name}`)\n")
    axes_str = ", ".join(f"`{k}` {v}" for k, v in (spec.get("axes") or {}).items())
    md.append(
        f"**Design.** All-params blind SR ({', '.join(spec['inputs'])} -> "
        f"latent), protocol identical to the reference study except for the "
        f"swept PySR hyperparameters. Baseline: niterations "
        f"{spec['baseline']['niterations']}, populations "
        f"{spec['baseline']['populations']}, maxsize {spec['baseline']['maxsize']}"
        f", PySR 1.5 defaults otherwise (population_size 27, "
        f"ncycles_per_iteration 380). Mode **{mode}** over {axes_str}; latents "
        f"{spec['latents']}, seeds {spec['seeds']}; {payload['n_reports_loaded']}"
        f"/{n_expected} runs loaded.\n")
    md.append(
        f"**How to read the metrics.** *Top val MI* is the study's headline "
        f"readout (argmax held-out GMM-MI over the Pareto front) but with all "
        f"6 inputs it grows with any capacity knob — it measures search "
        f"power. *MI @ c<={cap}* holds the complexity budget fixed across "
        f"configs, so it is the parsimony-matched comparison. *pars c* is the "
        f"complexity of the most parsimonious form within 1 sigma of the top "
        f"MI. For the amplitude latent, *r(top)* is the implied tau exponent "
        f"(textbook -2) and *tb* counts strict textbook forms on the front.\n")

    for latent in spec["latents"]:
        zkey = f"z{latent}"
        is_amp = latent == amp_idx
        expect = AUDIT_EXPECTED.get(run_name, {}).get(latent, "?")
        md.append(f"\n## Latent z{latent} (audit-expected: {expect})\n")

        head = (f"| config | ni | pop | ms | extra | seeds | top MI (mean +/- std) "
                f"| dMI vs base | MI@c<={cap} | pars c | fit s |")
        rule = "|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|"
        if is_amp:
            head += " r(top) | tb |"
            rule += "---:|---:|"
        md.append(head)
        md.append(rule)
        for c in payload["configs"]:
            a = c["latents"][zkey]
            b = base["latents"][zkey] if base else None
            extra = ", ".join(f"{k}={v}" for k, v in c["extra"].items()) or "-"
            cells = [
                c["label"] if c["label"] == "baseline" else f"`{c['label']}`",
                str(c["niterations"]), str(c["populations"]), str(c["maxsize"]),
                extra, str(a["n_seeds"]),
                fmt_mi(a["top_mi_mean"], a["top_mi_std"]) if a["n_seeds"] else "_pending_",
                (_delta(a["top_mi_mean"], b["top_mi_mean"])
                 if b and c is not base else "-"),
                _fmt(a.get("mi_cap_mean")),
                _fmt(a.get("pars_complexity_mean"), "{:.1f}"),
                _fmt(a.get("fit_seconds_mean"), "{:.0f}"),
            ]
            if is_amp:
                cells.append(fmt_mi(a.get("r_top_mean"), a.get("r_top_std"))
                             if a.get("r_top_mean") is not None else "n/a")
                cells.append(str(a.get("textbook_hits", 0)))
            md.append("| " + " | ".join(cells) + " |")

        done = [c for c in payload["configs"]
                if c["latents"][zkey].get("top_mi_mean") is not None]
        if len(done) > 1:
            def _agg(c):
                return c["latents"][zkey]
            by_top = max(done, key=lambda c: _agg(c)["top_mi_mean"])
            with_cap = [c for c in done if _agg(c).get("mi_cap_mean") is not None]
            line = (f"Best top MI: `{by_top['label']}` "
                    f"({fmt_mi(_agg(by_top)['top_mi_mean'], _agg(by_top)['top_mi_std'])} nat).")
            if with_cap:
                by_cap = max(with_cap, key=lambda c: _agg(c)["mi_cap_mean"])
                line += (f" Best MI@c<={cap}: `{by_cap['label']}` "
                         f"({_fmt(_agg(by_cap)['mi_cap_mean'])} nat).")
            md.append("")
            md.append(line)

        # ---- one-factor effects (star mode) ---------------------------------
        if mode == "star" and base is not None:
            base_cfg = {k: base[k] for k in CORE_KEYS} | {"extra": base["extra"]}
            by_axis = {}
            for c in payload["configs"]:
                if c is base:
                    continue
                ch = changed_axis({k: c[k] for k in CORE_KEYS} | {"extra": c["extra"]},
                                  base_cfg)
                if ch:
                    by_axis.setdefault(ch[0], []).append((ch[1], c))
            if by_axis:
                md.append(f"\n### One-factor effects vs baseline "
                          f"(top MI {fmt_mi(base['latents'][zkey]['top_mi_mean'], base['latents'][zkey]['top_mi_std'])}, "
                          f"MI@c<={cap} {_fmt(base['latents'][zkey].get('mi_cap_mean'))}, "
                          f"fit {_fmt(base['latents'][zkey].get('fit_seconds_mean'), '{:.0f}')} s)\n")
                md.append(f"| axis | value | dTop MI | dMI@c<={cap} | d fit s |")
                md.append("|---|---:|---:|---:|---:|")
                b = base["latents"][zkey]
                for axis, pairs in by_axis.items():
                    for val, c in sorted(pairs, key=lambda p: p[0]):
                        a = c["latents"][zkey]
                        dt = (f"{a['fit_seconds_mean'] - b['fit_seconds_mean']:+.0f}"
                              if a.get("fit_seconds_mean") is not None
                              and b.get("fit_seconds_mean") is not None else "n/a")
                        md.append(f"| {axis} | {val} | "
                                  f"{_delta(a['top_mi_mean'], b['top_mi_mean'])} | "
                                  f"{_delta(a.get('mi_cap_mean'), b.get('mi_cap_mean'))} | "
                                  f"{dt} |")

        # ---- per-seed appendix ----------------------------------------------
        md.append(f"\n### Per-seed top forms (z{latent})\n")
        for c in payload["configs"]:
            rows = c["latents"][zkey]["per_seed"]
            if not rows:
                continue
            md.append(f"\n**{c['config_id']}**")
            md.append("")
            md.append("| seed | c | top MI +/- err | MI@c<="
                      f"{cap} (c) | top form |")
            md.append("|---:|---:|---:|---:|---|")
            for r in sorted(rows, key=lambda r: r["seed"]):
                capped = (f"{_fmt(r['mi_cap'])} ({r['mi_cap_complexity']})"
                          if r.get("mi_cap") is not None else "n/a")
                md.append(f"| {r['seed']} | {r['top_complexity']} | "
                          f"{fmt_mi(r['top_mi'], r['top_mi_err'])} | {capped} | "
                          f"`{r['top_form']}` |")

    md.append("\n---\n_Generated by `scripts/consolidate_hp_sweep.py` from "
              f"`{sweep_dir}/*/z*/report.json`. Plan/submit/status: "
              "`scripts/sweep_blind_sr.py` + `hpc/slurm_hpsweep_sr.sh`._")
    return md, payload


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--sweep-dir", required=True,
                   help="results/<run>/hpsweep_<name> (holds manifest.json).")
    p.add_argument("--cap", type=int, default=10,
                   help="Complexity cap for the budget-matched MI readout (default 10).")
    p.add_argument("--out-dir", default="experiments")
    args = p.parse_args()

    sweep_dir = Path(args.sweep_dir)
    md, payload = consolidate(sweep_dir, args.cap)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"hpsweep_{payload['sweep_name']}_{payload['run_name']}"
    (out_dir / f"{stem}.json").write_text(json.dumps(payload, indent=2))
    (out_dir / f"{stem}.md").write_text("\n".join(md) + "\n")
    print(f"[write] {out_dir / (stem + '.md')}")
    print(f"[write] {out_dir / (stem + '.json')}")


if __name__ == "__main__":
    main()
