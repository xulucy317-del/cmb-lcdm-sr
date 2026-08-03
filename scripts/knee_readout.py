#!/usr/bin/env python
"""Knee & plateau saturation readout — Phase 1 of docs/discovery_roadmap.md.

Replaces argmax-MI with the saturation readout of docs/next_step.md section 2.1.
For each latent k and PySR seed s the cumulative Pareto envelope is

    M_{k,s}(c) = max { val MI(f) : f on that run's front, complexity(f) <= c },

pooled within each results *family* (a protocol-homogeneous namespace such as
``allparams`` = maxsize 20 x 5 seeds, ``allparams_ms10``, ``allparams_ms30``,
or one hpsweep config like ``hpsweep_hp_v1/c07_ms30``) as mean +/- SE across
seeds. Per latent the readout reports

  * Î_plat +/- SE   — empirical plateau: mean +/- SE over seeds of the front
                      maximum, taken from the highest-capacity family available
                      (largest maxsize, then most seeds, then the non-sweep
                      namespace);
  * c*              — one-SE knee: smallest c with M(c) >= Î_plat - SE, where
                      M(c) is the combined envelope (max over family means);
  * MI@c<=10        — combined envelope at c = 10 (continuity with the sweep
                      tables);
  * eta-level forms — per eta in {0.90, 0.95, 0.99}, the simplest single front
                      equation anywhere (any family/seed) with
                      val MI >= eta * Î_plat, with its variable support;
  * envelope class  — with c_eta = pooled-envelope crossing of eta * Î_plat:
                      "single dominant knee"  if c_0.90 <= 10 and c* <= 10,
                      "knee + slow climb"     if c_0.90 <= 10 <  c*,
                      "no knee (diffuse)"     if c_0.90 > 10.

Reads:  results/<run>/<subdir>/z<k>_seed<s>/report.json   (shuffled_*/pooled_*
        skipped; hpsweep subdirs are scanned one config level down)
Writes: experiments/knee_readout_<run>.json           (feeds Phases 2-4)
        experiments/knee_readout_<run>.md             (the deliverable)
        experiments/knee_readout_<run>_envelopes.png  (one panel per latent)

    python scripts/knee_readout.py --run lcdm_tt_beta3e-4 \
        --subdirs allparams allparams_ms10 allparams_ms30 hpsweep_hp_v1 \
        --out experiments/knee_readout_lcdm_tt_beta3e-4

Re-run after the Phase-1b maxsize-30 batch lands so the shape-latent plateaus
use the ms30 ceiling instead of the interim ms20 one.
"""
import argparse
import json
import re
import warnings
from pathlib import Path

import _bootstrap  # noqa: F401

import numpy as np

from consolidate_allparams import AUDIT_EXPECTED, expr_of, vars_used

SEED_DIR = re.compile(r"^z(\d+)_seed(\d+)$")
DEFAULT_SUBDIRS = ["allparams", "allparams_ms10", "allparams_ms30",
                   "hpsweep_hp_v1"]

# Fixed family -> color (validated categorical palette, slots 1-4 in order);
# families outside this map feed the combined envelope but are not drawn.
FAMILY_COLORS = {
    "allparams":              "#2a78d6",
    "allparams_ms10":         "#eb6834",
    "allparams_ms30":         "#1baf7a",
    "hpsweep_hp_v1/c07_ms30": "#eda100",
}
INK, INK_MUTED = "#0b0b0b", "#52514e"


# ---- discovery & loading ----------------------------------------------------

def discover_families(results_root: Path, run: str, subdirs) -> dict:
    """{family_id: {latent: {seed: report_path}}} — z<k>_seed<s> dirs only."""
    fams = {}

    def scan(base: Path, fam_id: str):
        for rp in sorted(base.glob("z*_seed*/report.json")):
            m = SEED_DIR.match(rp.parent.name)
            if not m:
                continue
            k, s = int(m.group(1)), int(m.group(2))
            fams.setdefault(fam_id, {}).setdefault(k, {})[s] = rp

    for sub in subdirs:
        base = results_root / run / sub
        if not base.is_dir():
            print(f"[warn] missing {base} — skipped")
            continue
        if any(SEED_DIR.match(p.name) for p in base.iterdir() if p.is_dir()):
            scan(base, sub)
        else:  # sweep layout: one config level down
            for cfg in sorted(p for p in base.iterdir() if p.is_dir()):
                scan(cfg, f"{sub}/{cfg.name}")
    return fams


def load_front(path: Path) -> dict:
    """{'rows': [(c, mi, err, expr)], 'maxsize': int} — finite-MI rows only."""
    rep = json.loads(path.read_text())
    rows = []
    for r in rep.get("all_equations", []):
        mi = r.get("mi_val")
        if mi is None or not np.isfinite(mi):
            continue
        rows.append((int(r["complexity"]), float(mi),
                     float(r.get("mi_val_err") or 0.0), expr_of(r)))
    return {"rows": rows,
            "maxsize": int(rep.get("pysr_kwargs", {}).get("maxsize", 0))}


# ---- envelopes --------------------------------------------------------------

def seed_envelope(rows, grid: np.ndarray) -> np.ndarray:
    """Cumulative envelope on an integer grid; NaN below the front's smallest
    complexity, flat-extended above its largest (max over C(f)<=c)."""
    env = np.full(grid.shape, np.nan)
    for c, mi, _err, _e in sorted(rows):
        env[grid >= c] = np.fmax(env[grid >= c], mi)
    return env


def pool_family(seed_envs: dict, grid: np.ndarray) -> dict:
    """Across-seed mean/SE/count of the per-seed envelopes at each grid c."""
    stack = np.vstack([seed_envs[s] for s in sorted(seed_envs)])
    n = np.sum(np.isfinite(stack), axis=0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  # all-NaN / ddof slices
        mean = np.where(n > 0, np.nanmean(stack, axis=0), np.nan)
        sd = np.where(n > 1, np.nanstd(stack, axis=0, ddof=1), np.nan)
    se = np.where(n > 1, sd / np.sqrt(np.maximum(n, 1)), np.nan)
    return {"mean": mean, "se": se, "n": n}


def first_crossing(grid: np.ndarray, curve: np.ndarray, level: float):
    """Smallest c with curve(c) >= level (None if never reached)."""
    hit = np.where(np.isfinite(curve) & (curve >= level))[0]
    return int(grid[hit[0]]) if hit.size else None


def classify(c90, c_star, simple_c: int) -> str:
    if c90 is None or c90 > simple_c:
        return "no knee (diffuse)"
    if c_star is not None and c_star <= simple_c:
        return "single dominant knee"
    return "knee + slow climb"


# ---- per-latent readout -----------------------------------------------------

def latent_readout(fam_runs: dict, eta_levels, simple_c: int) -> dict:
    """fam_runs: {family_id: {seed: front dict}} for one latent."""
    cmax = max([simple_c] +
               [max(max((c for c, *_ in f["rows"]), default=1), f["maxsize"])
                for runs in fam_runs.values() for f in runs.values()])
    grid = np.arange(1, cmax + 1)

    pooled, fam_meta = {}, {}
    for fam, runs in fam_runs.items():
        envs = {s: seed_envelope(f["rows"], grid) for s, f in runs.items()}
        pooled[fam] = pool_family(envs, grid)
        fam_meta[fam] = {
            "maxsize": max(f["maxsize"] for f in runs.values()),
            "n_seeds": len(runs),
            "per_seed_max": {s: max((mi for _c, mi, *_ in f["rows"]),
                                    default=np.nan)
                             for s, f in sorted(runs.items())},
        }

    # plateau family: largest maxsize, then most seeds, then non-sweep, name
    plat_fam = max(fam_meta, key=lambda f: (fam_meta[f]["maxsize"],
                                            fam_meta[f]["n_seeds"],
                                            "/" not in f, f))
    plat_max = [v for v in fam_meta[plat_fam]["per_seed_max"].values()
                if np.isfinite(v)]
    mi_plat = float(np.mean(plat_max))
    se_plat = (float(np.std(plat_max, ddof=1) / np.sqrt(len(plat_max)))
               if len(plat_max) > 1 else 0.0)

    combined = np.full(grid.shape, np.nan)
    for fam in pooled:
        combined = np.fmax(combined, pooled[fam]["mean"])

    c_star = first_crossing(grid, combined, mi_plat - se_plat)
    crossings = {f"{eta:.2f}": first_crossing(grid, combined, eta * mi_plat)
                 for eta in eta_levels}

    # simplest single forms reaching eta * plateau, across every run
    all_rows = [(c, mi, err, expr, fam, s)
                for fam, runs in fam_runs.items()
                for s, f in runs.items() for c, mi, err, expr in f["rows"]]
    eta_forms = {}
    for eta in eta_levels:
        hits = [r for r in all_rows if r[1] >= eta * mi_plat]
        if not hits:
            eta_forms[f"{eta:.2f}"] = None
            continue
        c, mi, err, expr, fam, s = min(hits, key=lambda r: (r[0], -r[1]))
        eta_forms[f"{eta:.2f}"] = {
            "complexity": c, "mi_val": mi, "mi_val_err": err,
            "expression": expr, "support": vars_used(expr),
            "eta_achieved": mi / mi_plat if mi_plat else None,
            "family": fam, "seed": s,
        }

    # best single form in the simple regime (the c<=10 "knee form" whose
    # support feeds Phase 4's blind variable-subset selection)
    simple_rows = [r for r in all_rows if r[0] <= simple_c]
    simple_form = None
    if simple_rows:
        c, mi, err, expr, fam, s = max(simple_rows, key=lambda r: (r[1], -r[0]))
        simple_form = {"complexity": c, "mi_val": mi, "mi_val_err": err,
                       "expression": expr, "support": vars_used(expr),
                       "eta_achieved": mi / mi_plat if mi_plat else None,
                       "family": fam, "seed": s}

    i10 = np.where(grid == simple_c)[0]
    mi_at_10 = float(combined[i10[0]]) if i10.size and np.isfinite(
        combined[i10[0]]) else None
    ic = np.where(grid == c_star)[0] if c_star is not None else []
    return {
        "grid": grid, "pooled": pooled, "fam_meta": fam_meta,
        "plateau": {"family": plat_fam,
                    "maxsize": fam_meta[plat_fam]["maxsize"],
                    "n_seeds": len(plat_max), "mi_plat": mi_plat,
                    "se": se_plat,
                    "per_seed_max": fam_meta[plat_fam]["per_seed_max"]},
        "combined": combined,
        "c_star": c_star,
        "mi_at_c_star": float(combined[ic[0]]) if len(ic) else None,
        "mi_at_c10": mi_at_10,
        "eta_crossings": crossings,
        "eta_forms": eta_forms,
        "simple_form": simple_form,
        "classification": classify(crossings.get("0.90"), c_star, simple_c),
    }


# ---- outputs ----------------------------------------------------------------

def fmt(x, prec=3):
    return "n/a" if x is None else f"{x:.{prec}f}"


def to_payload(run: str, subdirs, eta_levels, simple_c: int,
               readouts: dict) -> dict:
    def arr(a):
        return [None if not np.isfinite(v) else float(v) for v in a]

    latents = {}
    for k, r in sorted(readouts.items()):
        latents[f"z{k}"] = {
            "audit_expected": AUDIT_EXPECTED.get(run, {}).get(k),
            "plateau": {**r["plateau"],
                        "per_seed_max": {str(s): (None if not np.isfinite(v)
                                                  else float(v))
                                         for s, v in
                                         r["plateau"]["per_seed_max"].items()}},
            "c_star": r["c_star"], "mi_at_c_star": r["mi_at_c_star"],
            "mi_at_c10": r["mi_at_c10"],
            "eta_crossings": r["eta_crossings"],
            "eta_forms": r["eta_forms"],
            "simple_form": r["simple_form"],
            "classification": r["classification"],
            "envelopes": {fam: {"c": [int(c) for c in r["grid"]],
                                "mean": arr(p["mean"]), "se": arr(p["se"]),
                                "n": [int(v) for v in p["n"]],
                                "maxsize": r["fam_meta"][fam]["maxsize"],
                                "n_seeds": r["fam_meta"][fam]["n_seeds"]}
                          for fam, p in sorted(r["pooled"].items())},
            "combined_envelope": {"c": [int(c) for c in r["grid"]],
                                  "max_of_means": arr(r["combined"])},
        }
    return {"run": run, "subdirs": list(subdirs),
            "eta_levels": [float(e) for e in eta_levels],
            "simple_c": simple_c, "latents": latents,
            "generated_by": "scripts/knee_readout.py"}


def to_markdown(run: str, readouts: dict, eta_levels, simple_c: int,
                fig_name: str) -> str:
    md = [f"# Knee & plateau readout — `{run}` (roadmap Phase 1)\n"]
    md.append(
        "Saturation readout replacing argmax-MI (docs/next_step.md section "
        "2.1): per latent and seed the cumulative Pareto envelope M(c) = best "
        "val MI at complexity <= c, pooled as mean +/- SE across seeds within "
        "each protocol family. **Î_plat** is the across-seed mean +/- SE of "
        "the front maximum in the highest-capacity family; **c\\*** is the "
        "one-SE knee, the smallest c whose combined envelope (max over family "
        "means) reaches Î_plat − SE; **MI@c<=10** keeps continuity with the "
        "sweep tables; the **eta forms** are the simplest single equations "
        "anywhere reaching eta x Î_plat. Envelope classes (c_eta = pooled "
        f"crossing of eta x Î_plat, simple = c <= {simple_c}): single "
        f"dominant knee (c_0.90 and c\\* both <= {simple_c}), knee + slow "
        f"climb (c_0.90 <= {simple_c} < c\\*), no knee/diffuse "
        f"(c_0.90 > {simple_c}).\n")
    md.append(f"![pooled envelopes]({fig_name})\n")

    md.append("## Summary — one row per latent\n")
    hdr = ("| latent | audit-expected | Î_plat +/- SE (family) | c* | M(c*) "
           "| MI@c<=10 | " +
           " | ".join(f"c_{eta:.2f}" for eta in eta_levels) +
           " | envelope class |")
    md.append(hdr)
    md.append("|" + "---|" * (7 + len(eta_levels)))
    for k, r in sorted(readouts.items()):
        p = r["plateau"]
        cross = " | ".join(str(r["eta_crossings"][f"{eta:.2f}"] or "n/a")
                           for eta in eta_levels)
        md.append(
            f"| z{k} | {AUDIT_EXPECTED.get(run, {}).get(k, '?')} "
            f"| {p['mi_plat']:.3f} +/- {p['se']:.3f} (`{p['family']}`, "
            f"ms{p['maxsize']}, n={p['n_seeds']}) | {r['c_star']} "
            f"| {fmt(r['mi_at_c_star'])} | {fmt(r['mi_at_c10'])} | {cross} "
            f"| {r['classification']} |")

    md.append("\n## Simplest forms at each sufficiency level\n")
    for k, r in sorted(readouts.items()):
        md.append(f"\n### z{k} — {AUDIT_EXPECTED.get(run, {}).get(k, '?')}: "
                  f"{r['classification']}\n")
        md.append("| eta | c | val MI +/- err | eta achieved | support "
                  "| family/seed | form |")
        md.append("|---:|---:|---:|---:|---|---|---|")
        sf = r["simple_form"]
        if sf is not None:
            md.append(
                f"| c<={simple_c} | {sf['complexity']} "
                f"| {sf['mi_val']:.3f} +/- {sf['mi_val_err']:.3f} "
                f"| {sf['eta_achieved']:.3f} | {', '.join(sf['support'])} "
                f"| `{sf['family']}`/s{sf['seed']} | `{sf['expression']}` |")
        for eta in eta_levels:
            f = r["eta_forms"][f"{eta:.2f}"]
            if f is None:
                md.append(f"| {eta:.2f} | n/a | n/a | n/a | n/a | n/a | "
                          "_no single form reaches this level_ |")
                continue
            md.append(
                f"| {eta:.2f} | {f['complexity']} "
                f"| {f['mi_val']:.3f} +/- {f['mi_val_err']:.3f} "
                f"| {f['eta_achieved']:.3f} | {', '.join(f['support'])} "
                f"| `{f['family']}`/s{f['seed']} | `{f['expression']}` |")

    md.append("\n---\n_Generated by `scripts/knee_readout.py`; families "
              "outside the drawn four still feed the combined envelope. "
              "Re-run after `allparams_ms30` (Phase 1b) lands._")
    return "\n".join(md) + "\n"


def plot_envelopes(run: str, readouts: dict, out_png: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ks = sorted(readouts)
    ncol = 3 if len(ks) > 4 else 2
    nrow = -(-len(ks) // ncol)
    fig, axes = plt.subplots(nrow, ncol, figsize=(4.2 * ncol, 3.1 * nrow),
                             sharex=False, squeeze=False)
    fig.patch.set_facecolor("#fcfcfb")

    for ax, k in zip(axes.flat, ks):
        r = readouts[k]
        grid, p = r["grid"], r["plateau"]
        for fam, color in FAMILY_COLORS.items():
            if fam not in r["pooled"]:
                continue
            pe = r["pooled"][fam]
            ok = np.isfinite(pe["mean"])
            ax.step(grid[ok], pe["mean"][ok], where="post", color=color,
                    lw=1.5, label=fam.split("/")[-1])
            band = np.isfinite(pe["se"]) & ok
            ax.fill_between(grid[band], (pe["mean"] - pe["se"])[band],
                            (pe["mean"] + pe["se"])[band], step="post",
                            color=color, alpha=0.18, lw=0)
        okc = np.isfinite(r["combined"])
        ax.step(grid[okc], r["combined"][okc], where="post", color=INK,
                lw=2.0, label="combined envelope")
        ax.axhspan(p["mi_plat"] - p["se"], p["mi_plat"] + p["se"],
                   color=INK_MUTED, alpha=0.12, lw=0)
        ax.axhline(p["mi_plat"], color=INK_MUTED, lw=1.0, ls="--")
        if r["c_star"] is not None:
            ax.axvline(r["c_star"], color=INK_MUTED, lw=1.0, ls=":")
        ax.set_title(f"z{k} — {AUDIT_EXPECTED.get(run, {}).get(k, '?')}\n"
                     f"plat {p['mi_plat']:.2f}$\\pm${p['se']:.2f}  "
                     f"c*={r['c_star']}  ({r['classification']})",
                     fontsize=9, color=INK)
        ax.set_xlabel("complexity c", fontsize=8)
        ax.set_ylabel("val MI [nat]", fontsize=8)
        ax.tick_params(labelsize=8)
        ax.grid(axis="y", color=INK_MUTED, alpha=0.2, lw=0.5)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    for ax in axes.flat[len(ks):]:
        ax.set_visible(False)

    from matplotlib.lines import Line2D
    present = [f for f in FAMILY_COLORS
               if any(f in readouts[k]["pooled"] for k in ks)]
    handles = [Line2D([], [], color=FAMILY_COLORS[f], lw=1.5) for f in present]
    handles.append(Line2D([], [], color=INK, lw=2.0))
    labels = [f.split("/")[-1] for f in present] + ["combined envelope"]
    fig.legend(handles, labels, loc="upper center", ncol=len(labels),
               fontsize=8, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.suptitle(f"Cumulative MI envelopes — {run}", y=1.04, fontsize=11,
                 color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(out_png, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)


# ---- main -------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", required=True, help="Run name under results/.")
    p.add_argument("--results-root", default="results")
    p.add_argument("--subdirs", nargs="*", default=DEFAULT_SUBDIRS)
    p.add_argument("--out", default=None,
                   help="Output prefix (default experiments/knee_readout_<run>).")
    p.add_argument("--eta-levels", nargs="*", type=float,
                   default=[0.90, 0.95, 0.99])
    p.add_argument("--simple-c", type=int, default=10,
                   help="Complexity cut for MI@c<=10 and the knee classes.")
    p.add_argument("--no-plot", action="store_true")
    args = p.parse_args()

    fams = discover_families(Path(args.results_root), args.run, args.subdirs)
    if not fams:
        print(f"[FAIL] no z*_seed*/report.json under "
              f"{args.results_root}/{args.run} for subdirs {args.subdirs}")
        return 1

    by_latent = {}
    for fam, latents in fams.items():
        for k, seeds in latents.items():
            for s, path in seeds.items():
                by_latent.setdefault(k, {}).setdefault(fam, {})[s] = \
                    load_front(path)

    readouts = {k: latent_readout(by_latent[k], args.eta_levels, args.simple_c)
                for k in sorted(by_latent)}

    out = Path(args.out or f"experiments/knee_readout_{args.run}")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig_name = f"{out.name}_envelopes.png"
    if not args.no_plot:
        plot_envelopes(args.run, readouts, out.with_name(fig_name))
        print(f"[write] {out.with_name(fig_name)}")

    payload = to_payload(args.run, args.subdirs, args.eta_levels,
                         args.simple_c, readouts)
    out.with_suffix(".json").write_text(json.dumps(payload, indent=2))
    print(f"[write] {out.with_suffix('.json')}")
    out.with_suffix(".md").write_text(
        to_markdown(args.run, readouts, args.eta_levels, args.simple_c,
                    fig_name))
    print(f"[write] {out.with_suffix('.md')}")

    for k, r in sorted(readouts.items()):
        pl = r["plateau"]
        print(f"  z{k}: plat {pl['mi_plat']:.3f}+/-{pl['se']:.3f} "
              f"({pl['family']}, ms{pl['maxsize']}, n={pl['n_seeds']})  "
              f"c*={r['c_star']}  MI@10={fmt(r['mi_at_c10'])}  "
              f"{r['classification']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
