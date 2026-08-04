#!/usr/bin/env python
"""Blind symbolic regression of a VAE amplitude latent — GMM-MI inner loss.

Discover the closed-form expression f(inputs) that best predicts a given
latent column, with no hint of the answer anywhere in the pipeline:

* Inputs are *raw* ΛCDM parameters (for the amplitude study: A_s and τ only —
  no derived columns, no hand-coded A_s·e^{−2τ} baseline).
* The inner loss PySR optimises is a pure-Julia GMM-MI estimator
  (``exp(−MI)``, fixed K=2 EM, N_INNER=300) — invariant under any bijection
  of either variable, so the search is rewarded for functional form, never
  for matching the encoder's standardisation.
* Every Pareto-front equation is then re-scored post hoc by the full GMM-MI
  estimator (gmm-mi package) on a held-out validation split; the top-5 are
  ranked by validation MI.

The only auxiliary is a data-driven OLS baseline in the raw inputs.
Cross-seed consolidation (tables + textbook-form scan) lives in
scripts/consolidate_blind_sr.py.

Usage (the two study regimes):

    # TT-only (degeneracy present) — amplitude latent idx 2, seeds 0..4
    python scripts/run_blind_sr.py --run-dir models/lcdm_tt_beta3e-4 \
        --latent-index 2 --inputs A_s tau --seed 0

    # TT+EE-lowl (degeneracy broken) — amplitude latent z5, seeds 0..4
    python scripts/run_blind_sr.py --run-dir models/lcdm_tt_ee_lowl \
        --latent-index 5 --inputs A_s tau --seed 0

Requires <run-dir>/analysis/encoder_means_test.npy. If it is missing, generate
it first (needs the spectra shards):

    python scripts/encode_latents.py --run-dir <run-dir> --shards-root <dir>

Instead of a latent column, --target-npy regresses an arbitrary cached 1-D
vector row-aligned with the 50k test split (Phase-6 residual targets of
docs/discovery_roadmap.md), e.g.:

    python scripts/run_blind_sr.py --run-dir <run-dir> \
        --target-npy <run-dir>/analysis/residual_z2_v1.npy \
        --inputs omega_b omega_cdm H0 tau A_s n_s --seed 0
"""
import argparse
import json
import signal
import time
from pathlib import Path

import _bootstrap  # noqa: F401

import numpy as np

from cmb_lcdm_sr.sr import (
    INNER_LOSS_NAME,
    INPUT_ALIASES,
    JULIA_LOSS_GMM_MI,
    LOSS_KIND_LABEL,
    build_inputs,
)


def _with_timeout(seconds, fn, *args, **kwargs):
    """Run fn under a SIGALRM deadline. Degenerate Pareto-front members can
    make sympy simplify/lambdify (and, through them, predict) hang for hours
    (seen: 25+ min on nested exp/exp float towers), which turns a 5-min task
    into a walltime kill. Main-thread only."""
    def _raise(signum, frame):
        raise TimeoutError(f"timed out after {seconds}s")
    old = signal.signal(signal.SIGALRM, _raise)
    signal.alarm(seconds)
    try:
        return fn(*args, **kwargs)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)


def default_out_dir(run_dir: Path, seed: int, tag: str) -> Path:
    """results/<model-name>/symbolic_regression_gmm_mi_seed<N>[_<tag>]"""
    name = f"symbolic_regression_gmm_mi_seed{seed}"
    if tag:
        name = f"{name}_{tag}"
    return Path("results") / run_dir.name / name


def resolve_target(run_dir: Path, latent_index, target_npy, target_label,
                   dataset_dir="data"):
    """(y_full, label) — a latent column of the encoder-means cache, or an
    arbitrary cached vector (--target-npy), both row-aligned with the test
    split. Exactly one of latent_index / target_npy must be given; truncation
    to --n-samples happens at the call site."""
    if (latent_index is None) == (target_npy is None):
        raise SystemExit("exactly one of --latent-index / --target-npy is required")
    if target_npy is not None:
        y = np.squeeze(np.asarray(np.load(target_npy)))
        if y.ndim != 1:
            raise SystemExit(f"--target-npy must hold a 1-D vector, got shape {y.shape}")
        return y.astype(np.float64), (target_label or Path(target_npy).stem)
    means_path = run_dir / "analysis" / "encoder_means_test.npy"
    if not means_path.exists():
        raise FileNotFoundError(
            f"{means_path} not found. Generate it with:\n"
            f"    python scripts/encode_latents.py --run-dir {run_dir} "
            f"--dataset-dir {dataset_dir} --shards-root <dir-with-spectra-shards>"
        )
    means = np.load(means_path)
    if latent_index < 0 or latent_index >= means.shape[1]:
        raise IndexError(f"latent-index {latent_index} out of range for L={means.shape[1]}")
    return means[:, latent_index].astype(np.float64), f"z{latent_index}"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run-dir", required=True,
                   help="Stored run dir (models/<run>) holding analysis/encoder_means_test.npy.")
    p.add_argument("--dataset-dir", default="data",
                   help="Holds theta.npy + splits_v1.npz (default: data/).")
    p.add_argument("--latent-index", type=int, default=None,
                   help="Which latent column to regress (numpy 0-indexed). "
                        "Exactly one of --latent-index / --target-npy.")
    p.add_argument("--target-npy", default=None,
                   help="Regress an arbitrary cached target instead of a latent "
                        "column: path to a 1-D .npy vector row-aligned with the "
                        "50k test split (e.g. analysis/residual_z2_v1.npy).")
    p.add_argument("--target-label", default=None,
                   help="Label for --target-npy outputs (default: file stem).")
    p.add_argument("--inputs", nargs="+", required=True,
                   help=f"Input names. One or more of: {list(INPUT_ALIASES)}")
    p.add_argument("--n-samples", type=int, default=5000)
    p.add_argument("--val-frac", type=float, default=0.2, help="Held-out fraction for MI rerank.")
    p.add_argument("--niterations", type=int, default=200)
    p.add_argument("--populations", type=int, default=15)
    p.add_argument("--maxsize", type=int, default=20)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--parallelism", choices=["serial", "multithreading", "multiprocessing"],
                   default="multithreading")
    p.add_argument("--unary-operators", nargs="*", default=["exp", "log", "neg", "square"])
    p.add_argument("--binary-operators", nargs="*", default=["+", "*", "-", "/"])
    p.add_argument("--turbo", action="store_true", help="PySR SIMD inner loops.")
    p.add_argument("--pysr-extra", default="{}",
                   help="JSON object of additional PySRRegressor kwargs, e.g. "
                        "'{\"population_size\": 50, \"parsimony\": 0.001}'. "
                        "Cannot override kwargs managed by dedicated flags.")
    p.add_argument("--out-dir", default=None,
                   help="Defaults to results/<run-name>/symbolic_regression_gmm_mi_seed<seed>.")
    p.add_argument("--tag", default="", help="Optional suffix on the default out-dir.")
    args = p.parse_args()

    run_dir = Path(args.run_dir)
    theta_path = Path(args.dataset_dir) / "theta.npy"
    splits_path = Path(args.dataset_dir) / "splits_v1.npz"
    for path in (theta_path, splits_path):
        if not path.exists():
            raise FileNotFoundError(path)
    y_full, target_label = resolve_target(run_dir, args.latent_index,
                                          args.target_npy, args.target_label,
                                          dataset_dir=args.dataset_dir)

    tag = args.tag or (target_label if args.target_npy else "")
    out_dir = Path(args.out_dir) if args.out_dir else default_out_dir(run_dir, args.seed, tag)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[setup] out_dir={out_dir}  target={target_label}")

    # --- Load + assemble (X, y) ---------------------------------------------
    print(f"[load] theta={theta_path}")
    theta = np.load(theta_path)
    splits = np.load(splits_path)
    test_idx = np.where(splits["split_id"] == 2)[0]
    if len(y_full) != len(test_idx):
        raise SystemExit(f"target has {len(y_full)} rows, test split has "
                         f"{len(test_idx)} — must be row-aligned")
    n = min(args.n_samples, len(test_idx))
    test_idx = test_idx[:n]
    print(f"[load] using first {n} test indices")

    y_raw = y_full[:n]
    X_raw, input_labels = build_inputs(theta[test_idx], args.inputs)
    print(f"[load] X shape={X_raw.shape}, input_labels={input_labels}, "
          f"y mean={y_raw.mean():.3f}, std={y_raw.std():.3f}")

    # --- Train/val split (deterministic) -------------------------------------
    n_val = int(round(n * args.val_frac))
    n_fit = n - n_val
    X_fit, X_val = X_raw[:n_fit], X_raw[n_fit:]
    y_fit, y_val = y_raw[:n_fit], y_raw[n_fit:]
    print(f"[split] n_fit={n_fit}, n_val={n_val}")

    # --- Standardise y (fit-only mean/std) -----------------------------------
    # Note: harmless under an MI loss (standardisation is a bijection); kept so
    # equation constants stay on the same scale as the parent study.
    y_mean, y_std = float(y_fit.mean()), float(y_fit.std())
    y_fit_s = (y_fit - y_mean) / y_std
    y_val_s = (y_val - y_mean) / y_std

    # --- OLS baseline (data-driven only) -------------------------------------
    X_fit_aug = np.column_stack([X_fit, np.ones(n_fit)])
    beta_ols, *_ = np.linalg.lstsq(X_fit_aug, y_fit_s, rcond=None)
    yhat_ols_val = np.column_stack([X_val, np.ones(n_val)]) @ beta_ols
    mse_ols = float(np.mean((yhat_ols_val - y_val_s) ** 2))
    print(f"[baseline OLS] MSE_val={mse_ols:.4f}  beta={beta_ols}")

    # --- PySR fit (gmm_mi inner loss) ----------------------------------------
    from pysr import PySRRegressor
    sr_kwargs = dict(
        niterations=args.niterations,
        populations=args.populations,
        maxsize=args.maxsize,
        binary_operators=list(args.binary_operators),
        unary_operators=list(args.unary_operators),
        random_state=args.seed,
        parallelism=args.parallelism,
        progress=False,
        verbosity=1,
        loss_function=JULIA_LOSS_GMM_MI,
        output_directory=str(out_dir / "pysr_state"),
        run_id="run",
    )
    # The loss is batch-level: PySR mini-batching would bias the EM fit on tiny
    # sub-batches, so it is not enabled here.
    if args.turbo:
        sr_kwargs["turbo"] = True
    if args.parallelism == "serial":
        sr_kwargs["deterministic"] = True
    pysr_extra = json.loads(args.pysr_extra)
    if not isinstance(pysr_extra, dict):
        raise SystemExit("--pysr-extra must be a JSON object")
    clash = sorted(set(pysr_extra) & set(sr_kwargs))
    if clash:
        raise SystemExit(f"--pysr-extra may not override managed kwargs: {clash}")
    sr_kwargs.update(pysr_extra)
    print(f"[pysr] inner_loss={INNER_LOSS_NAME}  selection_metric=mi")
    print(f"[pysr] kwargs={ {k: v for k, v in sr_kwargs.items() if k not in ('binary_operators', 'unary_operators', 'loss_function')} }")

    model = PySRRegressor(**sr_kwargs)
    t0 = time.time()
    model.fit(X_fit, y_fit_s, variable_names=input_labels)
    t_fit = time.time() - t0
    print(f"[pysr] fit done in {t_fit:.1f}s")

    # --- Collect equations + evaluate on val ---------------------------------
    eqs = model.equations_
    if eqs is None or len(eqs) == 0:
        raise RuntimeError("PySR returned no equations.")
    eqs_csv = out_dir / "equations.csv"
    eqs.to_csv(eqs_csv, index=False)
    print(f"[pysr] {len(eqs)} equations -> {eqs_csv}")

    rows = []
    for i in range(len(eqs)):
        # Degenerate front members (e.g. sub-expressions that simplify to 1/0
        # -> ComplexInfinity) can fail sympy lambdification inside predict;
        # keep the row with mse_val=None so downstream MI selection skips it.
        try:
            yhat_val_s = _with_timeout(120, model.predict, X_val, index=i)
            mse_val = float(np.mean((yhat_val_s - y_val_s) ** 2))
            eval_error = None
        except Exception as exc:                                     # noqa: BLE001
            mse_val = None
            eval_error = str(exc)
        row = {
            "index": int(i),
            "complexity": int(eqs.iloc[i]["complexity"]),
            "loss_train": float(eqs.iloc[i]["loss"]),
            "expression_raw": str(eqs.iloc[i]["equation"]),
            "mse_val": mse_val,
        }
        if eval_error is not None:
            row["eval_error"] = eval_error
        rows.append(row)

    import sympy

    def _simplify(i):
        try:
            expr = _with_timeout(60, model.sympy, index=i)
            return str(_with_timeout(60, sympy.simplify, expr))
        except Exception as exc:                                     # noqa: BLE001
            return f"<sympy failed: {exc}>"

    # --- Post-hoc GMM-MI on val for every Pareto-front equation --------------
    from cmb_lcdm_sr.mi import mutual_information_gmm

    print(f"[selection=mi] computing GMM-MI for all {len(rows)} equations...")
    for r in rows:
        try:
            yhat_val = _with_timeout(120, model.predict, X_val, index=r["index"])
            mi, err = _with_timeout(
                300, mutual_information_gmm,
                y_val_s.reshape(-1, 1), yhat_val.reshape(-1, 1),
                return_uncertainty=True, max_samples=n_val, seed=0,
            )
            r["mi_val"] = float(mi[0, 0])
            r["mi_val_err"] = float(err[0, 0])
        except Exception as exc:                                     # noqa: BLE001
            r["mi_val"] = None
            r["mi_val_err"] = None
            r["mi_val_error"] = str(exc)
        r["expression_simplified"] = _simplify(r["index"])

    def _mi_key(r):
        v = r.get("mi_val")
        return (v if v is not None and np.isfinite(v) else float("-inf"))

    rows_sorted = sorted(rows, key=_mi_key, reverse=True)
    top_k = rows_sorted[:5]
    rank_label = "VAL MI (primary)"

    # --- Pareto plot ----------------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        comp = eqs["complexity"].values
        loss = eqs["loss"].values
        fig, ax = plt.subplots(figsize=(6, 4), dpi=120)
        ax.scatter(comp, loss, s=24, alpha=0.7)
        for i, (c, l) in enumerate(zip(comp, loss)):
            ax.annotate(str(i), (c, l), fontsize=7, xytext=(3, 3), textcoords="offset points")
        if loss.min() > 0:
            ax.set_yscale("log")
        ax.set_xlabel("complexity")
        ax.set_ylabel(f"train loss ({LOSS_KIND_LABEL})")
        ax.set_title(f"PySR Pareto front  (run={run_dir.name}, target={target_label}, "
                     f"inner_loss={INNER_LOSS_NAME}, seed={args.seed})")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(out_dir / "pareto.png")
        plt.close(fig)
    except Exception as exc:                                         # noqa: BLE001
        print(f"[plot] pareto.png failed: {exc}")

    # --- Save report.json ----------------------------------------------------
    report = {
        "run_dir": str(run_dir),
        "regime": run_dir.name,
        "latent_index": args.latent_index,
        "target_npy": args.target_npy,
        "target_label": target_label,
        "input_labels": input_labels,
        "n_samples": n,
        "n_fit": n_fit,
        "n_val": n_val,
        "y_mean_train": y_mean,
        "y_std_train": y_std,
        "inner_loss": INNER_LOSS_NAME,
        "selection_metric": "mi",
        "pysr_kwargs": {
            "niterations": args.niterations,
            "populations": args.populations,
            "maxsize": args.maxsize,
            "binary_operators": list(args.binary_operators),
            "unary_operators": list(args.unary_operators),
            "parallelism": args.parallelism,
            "random_state": args.seed,
            "loss_kind": LOSS_KIND_LABEL,
            "pysr_version": __import__("pysr").__version__,
            **pysr_extra,
        },
        "ols_baseline": {
            "coefs": beta_ols.tolist(),
            "var_names": input_labels + ["bias"],
            "mse_val": mse_ols,
        },
        "fit_seconds": t_fit,
        "n_equations": len(eqs),
        "all_equations": rows,
        "top5": top_k,
        "top5_ranked_by": rank_label,
    }
    out_json = out_dir / "report.json"
    with open(out_json, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[done] -> {out_json}")

    print(f"\n--- TOP-5 BY {rank_label} ---")
    for r in top_k:
        mi_str = (f"{r['mi_val']:.3f}±{r['mi_val_err']:.3f}"
                  if r.get("mi_val") is not None else "n/a")
        mse_str = (f"{r['mse_val']:.4f}" if r.get("mse_val") is not None else "n/a")
        print(f"  c={r['complexity']:>2}  mse_val={mse_str}  "
              f"mi_val={mi_str}  expr={r['expression_simplified']}")


if __name__ == "__main__":
    main()
