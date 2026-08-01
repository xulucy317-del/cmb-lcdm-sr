#!/usr/bin/env python
"""Pool per-seed blind-SR runs and rank by cross-seed GMM-MI stats.

Reads multiple report.json files (each produced by run_blind_sr.py; reports
from the parent cmbvae project pool identically). For each unique
canonical-form expression, aggregates:
  - val MI per seed (mean ± std across seeds)
  - val MSE per seed
  - complexity (min / mode across seeds)
  - count: how many seeds found this expression

Output: a ranked Markdown table + a consolidated JSON for downstream use.
Runnable incrementally — re-run as more seeds finish.

Usage:
    python scripts/pool_sr_runs.py \
        --glob 'results/lcdm_tt_beta3e-4/symbolic_regression_gmm_mi_seed*/report.json' \
        --out  results/lcdm_tt_beta3e-4/sr_pooled
"""
import argparse
import json
from collections import defaultdict
from glob import glob
from pathlib import Path
from statistics import mean, stdev

import _bootstrap  # noqa: F401

import numpy as np
import sympy


def canonical_form(expr_str: str) -> str:
    """Reduce an expression to a canonical sympy string.

    Two expressions that are algebraically equivalent (up to simplification
    sympy can perform) should collapse to the same canonical form.
    """
    try:
        expr = sympy.sympify(expr_str)
        simplified = sympy.simplify(expr)
        return str(simplified)
    except Exception:
        return expr_str.strip()


def safe_float(v):
    if v is None:
        return None
    try:
        v = float(v)
        if not np.isfinite(v):
            return None
        return v
    except Exception:
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--glob", required=True, help="Glob of report.json paths.")
    p.add_argument("--out", required=True, help="Output directory.")
    p.add_argument("--min-seeds", type=int, default=1,
                   help="Only include canonical forms found by ≥N seeds.")
    p.add_argument("--consensus-seeds", type=int, default=3,
                   help="Seed count for the consensus section.")
    p.add_argument("--top-n", type=int, default=20,
                   help="Print top-N expressions in the markdown summary.")
    args = p.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    paths = sorted(glob(args.glob))
    if not paths:
        raise FileNotFoundError(f"No report.json found matching {args.glob}")
    print(f"[pool] {len(paths)} report files matched")

    # Collect per-expression records across all reports.
    records = defaultdict(list)
    per_report_meta = []

    for path in paths:
        try:
            with open(path) as f:
                rep = json.load(f)
        except Exception as exc:
            print(f"[pool]   skip {path}: {exc}")
            continue
        meta = {
            "path": path,
            "tag": Path(path).parent.name,
            "inner_loss": rep.get("inner_loss", "unknown"),
            "seed": rep.get("pysr_kwargs", {}).get("random_state", -1),
            "n_equations": rep.get("n_equations", 0),
            "selection_metric": rep.get("selection_metric"),
            "fit_seconds": rep.get("fit_seconds"),
        }
        per_report_meta.append(meta)

        for row in rep.get("all_equations", []):
            expr = row.get("expression_simplified") or row.get("expression_raw")
            if not expr:
                continue
            cf = canonical_form(expr)
            records[cf].append({
                "expression_raw": row.get("expression_raw"),
                "expression_simplified": row.get("expression_simplified"),
                "complexity": row.get("complexity"),
                "loss_train": row.get("loss_train"),
                "mse_val": safe_float(row.get("mse_val")),
                "mi_val": safe_float(row.get("mi_val")),
                "mi_val_err": safe_float(row.get("mi_val_err")),
                "seed": meta["seed"],
                "tag": meta["tag"],
            })

    # Aggregate per canonical form.
    pooled = []
    for cf, recs in records.items():
        seeds = sorted({r["seed"] for r in recs})
        if len(seeds) < args.min_seeds:
            continue
        mis = [r["mi_val"] for r in recs if r["mi_val"] is not None]
        mses = [r["mse_val"] for r in recs if r["mse_val"] is not None]
        complexities = [r["complexity"] for r in recs if r["complexity"] is not None]
        pooled.append({
            "canonical_form": cf,
            "n_records": len(recs),
            "n_unique_seeds": len(seeds),
            "seeds": seeds,
            "complexity_min": min(complexities) if complexities else None,
            "complexity_mode": max(set(complexities), key=complexities.count) if complexities else None,
            "mi_val_mean": mean(mis) if mis else None,
            "mi_val_std": stdev(mis) if len(mis) > 1 else None,
            "mi_val_min": min(mis) if mis else None,
            "mi_val_max": max(mis) if mis else None,
            "mse_val_min": min(mses) if mses else None,
            "n_mi_measurements": len(mis),
            "example_expression": recs[0].get("expression_simplified") or recs[0].get("expression_raw"),
        })

    # Rank: by mean MI desc, breaking ties by lower complexity.
    pooled.sort(key=lambda r: (
        -(r["mi_val_mean"] if r["mi_val_mean"] is not None else -1),
        r["complexity_min"] or 99,
    ))

    # Save consolidated JSON.
    with open(out_dir / "pooled.json", "w") as f:
        json.dump({
            "n_reports": len(per_report_meta),
            "per_report": per_report_meta,
            "pooled_expressions": pooled,
        }, f, indent=2)

    # Markdown summary.
    md_lines = []
    md_lines.append("# Pooled blind-SR runs summary\n")
    md_lines.append(f"**Reports pooled:** {len(per_report_meta)}\n")

    md_lines.append("## Reports\n")
    md_lines.append("| tag | seed | eqs found | fit time |")
    md_lines.append("|---|---:|---:|---:|")
    for m in per_report_meta:
        secs = f"{m['fit_seconds']:.1f}s" if m["fit_seconds"] is not None else "n/a"
        md_lines.append(f"| {m['tag']} | {m['seed']} | {m['n_equations']} | {secs} |")
    md_lines.append("")

    md_lines.append(f"## Top {args.top_n} canonical expressions by mean val MI\n")
    md_lines.append("Ranked by cross-seed mean MI desc. Tiebreaker: lower complexity.\n")
    md_lines.append("| Rank | c | mean MI [nat] | std MI [nat] | # records | # seeds | canonical form |")
    md_lines.append("|---:|---:|---:|---:|---:|---:|---|")
    for i, e in enumerate(pooled[:args.top_n]):
        mi_m = f"{e['mi_val_mean']:.4f}" if e["mi_val_mean"] is not None else "n/a"
        mi_s = f"{e['mi_val_std']:.4f}" if e["mi_val_std"] is not None else "n/a"
        c = e["complexity_min"]
        cf_short = e["canonical_form"]
        if len(cf_short) > 120:
            cf_short = cf_short[:117] + "..."
        md_lines.append(
            f"| {i + 1} | {c} | {mi_m} | {mi_s} | {e['n_records']} | "
            f"{e['n_unique_seeds']} | `{cf_short}` |"
        )

    md_lines.append(f"\n## Cross-seed consensus forms (found by ≥{args.consensus_seeds} seeds)\n")
    consensus = [e for e in pooled if e["n_unique_seeds"] >= args.consensus_seeds]
    md_lines.append(f"{len(consensus)} canonical forms appear in ≥{args.consensus_seeds} seeds.\n")
    for e in consensus[:args.top_n]:
        mi_m = f"{e['mi_val_mean']:.3f}" if e["mi_val_mean"] is not None else "n/a"
        md_lines.append(f"- **c={e['complexity_min']}** `{e['canonical_form'][:140]}` — "
                        f"seeds {e['seeds']}, n_records={e['n_records']}, mean MI = {mi_m}")

    md_path = out_dir / "pooled.md"
    md_path.write_text("\n".join(md_lines))
    print(f"[pool] -> {md_path}")
    print(f"[pool] -> {out_dir / 'pooled.json'}")
    print(f"[pool] {len(pooled)} unique canonical forms across {len(per_report_meta)} reports")
    if pooled:
        top = pooled[0]
        mi_m = f"{top['mi_val_mean']:.4f}" if top["mi_val_mean"] is not None else "n/a"
        print(f"[pool] top form: {top['canonical_form'][:80]}  "
              f"mean MI = {mi_m}  (n={top['n_records']})")


if __name__ == "__main__":
    main()
