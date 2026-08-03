#!/usr/bin/env python
"""Gate G0 checker — Phase 0 of docs/discovery_roadmap.md.

Verifies the artifacts every no-new-SR phase (1–3, 5, 7a, 8) depends on:

  1. Per model: analysis/encoder_means_test.npy AND encoder_logvars_test.npy
     exist, are (n_test, L), all-finite, logvars inside the model's clamp
     range (−10, 10); prints the per-latent posterior-noise summary that
     Phase 5 needs.
  2. One stored report.json re-parsed end to end by the new Phase-0 modules:
     top val-MI equation → semantics lambdify → GMM-MI against the latent on
     tier T1. Must reproduce the stored (T0-val) mi_val within tolerance —
     different rows + estimator noise, so this is a plumbing check, not a
     metrology one.

Run where results/ and the caches exist (CSD3, or locally after the Phase-0
rsync). Exit code 0 = G0 pass.

    python scripts/verify_phase0.py
    python scripts/verify_phase0.py --report results/lcdm_tt_beta3e-4/allparams/z2_seed0/report.json
"""
import argparse
import json
from glob import glob
from pathlib import Path

import _bootstrap  # noqa: F401

import numpy as np

DEFAULT_RUNS = ["models/lcdm_tt_beta3e-4", "models/lcdm_tt_ee_lowl"]
REPORT_GLOBS = ["{root}/{run}/allparams/z*_seed*/report.json",
                "{root}/{run}/symbolic_regression_gmm_mi_seed*/report.json",
                "{root}/{run}/**/report.json"]


def check_caches(run_dir: Path, n_expected: int) -> list:
    problems = []
    means_p = run_dir / "analysis" / "encoder_means_test.npy"
    logv_p = run_dir / "analysis" / "encoder_logvars_test.npy"
    missing = [p for p in (means_p, logv_p) if not p.exists()]
    if missing:
        return [f"missing {p}" for p in missing]
    means, logv = np.load(means_p), np.load(logv_p)
    if means.ndim != 2 or means.shape != logv.shape or means.shape[0] != n_expected:
        return [f"bad shapes: means {means.shape}, logvars {logv.shape} "
                f"(want ({n_expected}, L))"]
    if not np.isfinite(means).all():
        problems.append("non-finite encoder means")
    if not np.isfinite(logv).all():
        problems.append("non-finite logvars")
    elif logv.min() < -10.0 - 1e-6 or logv.max() > 10.0 + 1e-6:
        problems.append(f"logvars outside clamp (-10, 10): "
                        f"[{logv.min():.2f}, {logv.max():.2f}]")
    if not problems:
        var_mu = means.var(axis=0)
        mean_s2 = np.exp(logv).mean(axis=0)
        print(f"  [ok] {run_dir.name}: means/logvars ({means.shape[0]}, "
              f"{means.shape[1]}), finite, clamp respected")
        print("       latent  Var(mu)   E[sigma^2]   SNR")
        for k in range(means.shape[1]):
            snr = var_mu[k] / mean_s2[k] if mean_s2[k] > 0 else np.inf
            print(f"       z{k}      {var_mu[k]:>8.3f}  {mean_s2[k]:>10.4f}  {snr:>8.1f}")
    return problems


def pick_reports(results_root: str, run_name: str, explicit) -> list:
    if explicit:
        return [explicit]
    for pat in REPORT_GLOBS:
        hits = sorted(glob(pat.format(root=results_root, run=run_name),
                           recursive=True))
        if hits:
            return hits
    return []


def reparse_check(report_path: str, dataset_dir: str, tol_abs: float,
                  tol_sigma: float) -> bool:
    from cmb_lcdm_sr import semantics, tiers
    from cmb_lcdm_sr.mi import mutual_information_gmm

    rep = json.loads(Path(report_path).read_text())
    k = rep.get("latent_index")
    if k is None:
        print(f"  [skip] {report_path}: not a latent-target report")
        return True
    rows = [r for r in rep.get("all_equations", [])
            if r.get("mi_val") is not None and np.isfinite(r["mi_val"])]
    if not rows:
        print(f"  [FAIL] {report_path}: no scored equations")
        return False
    top = max(rows, key=lambda r: r["mi_val"])
    expr_str = top.get("expression_simplified") or top.get("expression_raw") or ""
    if expr_str.startswith("<sympy failed"):
        expr_str = top.get("expression_raw") or ""
    expr = semantics.parse_expr(expr_str)
    if expr is None:
        print(f"  [FAIL] cannot parse top expression: {expr_str!r}")
        return False

    theta1 = tiers.tier_theta(dataset_dir, tiers.T1)
    f_vals = semantics.evaluate_on_theta(expr, theta1)
    means = np.load(Path(rep["run_dir"]) / "analysis" / "encoder_means_test.npy")
    mu = means[tiers.T1, k]
    m = np.isfinite(f_vals)
    if m.mean() < 0.5:
        print(f"  [FAIL] top form finite on only {m.mean():.0%} of T1")
        return False
    mi, err = mutual_information_gmm(
        mu[m].reshape(-1, 1), f_vals[m].reshape(-1, 1),
        return_uncertainty=True, max_samples=5000, seed=0)
    mi, err = float(mi[0, 0]), float(err[0, 0])
    stored, stored_err = top["mi_val"], (top.get("mi_val_err") or 0.0)
    tol = max(tol_abs, tol_sigma * (stored_err + err))
    ok = abs(mi - stored) <= tol
    tag = "ok" if ok else "FAIL"
    print(f"  [{tag}] {report_path}\n"
          f"       top form (c={top['complexity']}): {expr_str}\n"
          f"       stored mi_val(T0-val) = {stored:.3f} +/- {stored_err:.3f}, "
          f"re-parsed MI(T1) = {mi:.3f} +/- {err:.3f}, "
          f"|delta| = {abs(mi - stored):.3f} (tol {tol:.3f}, "
          f"finite {m.mean():.0%})")
    return ok


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run-dirs", nargs="*", default=DEFAULT_RUNS)
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--results-root", default="results")
    p.add_argument("--report", default=None,
                   help="Explicit report.json for the re-parse check "
                        "(default: first found per model).")
    p.add_argument("--mi-tol-abs", type=float, default=0.15,
                   help="Absolute MI tolerance [nat] for the re-parse check.")
    p.add_argument("--mi-tol-sigma", type=float, default=5.0,
                   help="Tolerance in units of summed bootstrap errors.")
    args = p.parse_args()

    from cmb_lcdm_sr import tiers
    n_test = len(tiers.split_test_indices(args.dataset_dir))
    ok = True

    print("[G0] 1/2 encoder caches (means + logvars)")
    for run in args.run_dirs:
        problems = check_caches(Path(run), n_test)
        for prob in problems:
            print(f"  [FAIL] {run}: {prob}")
        ok &= not problems

    print("[G0] 2/2 report re-parse through semantics + tiers + mi")
    any_report = False
    for run in args.run_dirs:
        reports = pick_reports(args.results_root, Path(run).name, args.report)
        if not reports:
            print(f"  [FAIL] no report.json under {args.results_root}/{Path(run).name} "
                  f"— sync results/ first (roadmap Phase 0)")
            ok = False
            continue
        any_report = True
        ok &= reparse_check(reports[0], args.dataset_dir,
                            args.mi_tol_abs, args.mi_tol_sigma)
        if args.report:
            break
    ok &= any_report

    print(f"[G0] {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
