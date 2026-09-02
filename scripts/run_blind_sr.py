#!/usr/bin/env python
"""Blind symbolic regression of a scalar VAE latent.

Discover the closed-form expression f(inputs) that best predicts a given
latent column, with no hint of the answer anywhere in the pipeline:

* Inputs are *raw* ΛCDM parameters (for the amplitude study: A_s and τ only —
  no derived columns, no hand-coded A_s·e^{−2τ} baseline).
* The original/default objective is the pure-Julia GMM-MI estimator
  (``exp(−MI)``, fixed K=2 EM, N_INNER=300).
* ``--inner-loss mse`` instead performs direct numerical reconstruction of
  the fit-standardised latent with explicit elementwise squared error.
* Every Pareto-front equation is re-scored by held-out MSE. Full post-hoc
  GMM-MI is computed only when MI selects the front, or when explicitly
  requested as a secondary diagnostic.

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
    INPUT_CONFIGS,
    LOSS_SPECS,
    build_inputs,
    pysr_loss_kwargs,
    rank_front,
    resolve_input_config,
    resolve_loss,
    resolve_posthoc_mi,
)
from cmb_lcdm_sr.utils import save_json


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


def default_out_dir(run_dir: Path, seed: int, tag: str,
                    inner_loss: str = INNER_LOSS_NAME,
                    input_config: str | None = None) -> Path:
    """Loss-isolated default result directory (GMM-MI name is unchanged)."""
    config_part = f"_{input_config}" if input_config else ""
    name = f"symbolic_regression_{inner_loss}{config_part}_seed{seed}"
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


def load_extra_inputs(specs, n_test_rows: int):
    """Parse repeated ``label=path.npy`` specs into (labels, columns).

    Each vector must be 1-D and row-aligned with the full test split (the
    caller truncates to --n-samples alongside the target). Labels must be
    identifiers (they become PySR/sympy variable names)."""
    labels, cols = [], []
    for spec in specs:
        label, sep, path = spec.partition("=")
        if not sep or not label.isidentifier():
            raise SystemExit("--extra-input-npy expects 'label=path.npy' with "
                             f"an identifier label, got '{spec}'")
        v = np.squeeze(np.asarray(np.load(path)))
        if v.ndim != 1:
            raise SystemExit(f"extra input '{label}' must be 1-D, got shape {v.shape}")
        if len(v) != n_test_rows:
            raise SystemExit(f"extra input '{label}' has {len(v)} rows, test "
                             f"split has {n_test_rows} — must be row-aligned")
        if label in labels:
            raise SystemExit(f"duplicate extra-input label '{label}'")
        labels.append(label)
        cols.append(v.astype(np.float64))
    return labels, cols


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
    input_group = p.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--inputs", nargs="+",
        help=f"Input names. One or more of: {list(INPUT_ALIASES)}")
    input_group.add_argument(
        "--input-config", choices=list(INPUT_CONFIGS),
        help="Named input/precision profile. Profiles fix the six input "
             "coordinates and enforce PySR precision=64, print_precision=17.")
    p.add_argument("--extra-input-npy", action="append", default=[],
                   metavar="LABEL=PATH",
                   help="Additional SR input column: 'label=path.npy', a 1-D "
                        "test-aligned cached vector appended after --inputs "
                        "(repeatable). Interaction-aware stage 2 exposes the "
                        "stage-1 prediction f1hat = mu - residual this way.")
    p.add_argument("--n-samples", type=int, default=5000)
    p.add_argument("--val-frac", type=float, default=0.2, help="Held-out fraction for MI rerank.")
    p.add_argument("--niterations", type=int, default=200)
    p.add_argument("--populations", type=int, default=15)
    p.add_argument("--maxsize", type=int, default=20)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--inner-loss", choices=sorted(LOSS_SPECS),
                   default=INNER_LOSS_NAME,
                   help="PySR search objective (default: gmm_mi).")
    p.add_argument("--selection-metric", choices=["auto", "mi", "mse"],
                   default="auto",
                   help="Held-out front selector; auto maps gmm_mi->mi and "
                        "mse->mse.")
    p.add_argument("--posthoc-mi", choices=["auto", "full", "none"],
                   default="auto",
                   help="Full GMM-MI evaluation of every validation-front "
                        "member. auto computes it only for MI selection; "
                        "default: auto.")
    p.add_argument(
        "--skip-ols-baseline", action="store_true",
        help="Do not refit the diagnostic OLS baseline. Campaigns that reuse "
             "the frozen historical OLS baseline should set this flag.")
    p.add_argument("--parallelism", choices=["serial", "multithreading", "multiprocessing"],
                   default="multithreading")
    p.add_argument("--unary-operators", nargs="*", default=["exp", "log", "neg", "square"])
    p.add_argument("--binary-operators", nargs="*", default=["+", "*", "-", "/"])
    p.add_argument("--turbo", action="store_true", help="PySR SIMD inner loops.")
    p.add_argument("--pysr-extra", default="{}",
                   help="JSON object of additional PySRRegressor kwargs, e.g. "
                        "'{\"population_size\": 50, \"parsimony\": 0.001}'. "
                        "Cannot override kwargs managed by dedicated flags.")
    p.add_argument("--pysr-run-id", default="run",
                   help="Internal PySR state subdirectory; use a new value on "
                        "a scheduler restart (default: run).")
    p.add_argument("--out-dir", default=None,
                   help="Defaults to a loss-specific results/<run-name>/ "
                        "symbolic_regression_<loss>_seed<seed> directory.")
    p.add_argument("--tag", default="", help="Optional suffix on the default out-dir.")
    args = p.parse_args()

    if args.input_config:
        input_spec = resolve_input_config(args.input_config)
        input_names = input_spec["inputs"]
        input_sampled_expressions = input_spec["sampled_expressions"]
        input_config_pysr_kwargs = input_spec["pysr_kwargs"]
    else:
        # Keep the legacy explicit-input path unchanged.
        input_names = list(args.inputs)
        input_sampled_expressions = None
        input_config_pysr_kwargs = {}

    run_dir = Path(args.run_dir)
    theta_path = Path(args.dataset_dir) / "theta.npy"
    splits_path = Path(args.dataset_dir) / "splits_v1.npz"
    for path in (theta_path, splits_path):
        if not path.exists():
            raise FileNotFoundError(path)
    y_full, target_label = resolve_target(run_dir, args.latent_index,
                                          args.target_npy, args.target_label,
                                          dataset_dir=args.dataset_dir)
    loss_spec, selection_metric = resolve_loss(
        args.inner_loss, args.selection_metric)
    posthoc_mi = resolve_posthoc_mi(args.posthoc_mi, selection_metric)

    tag = args.tag or (target_label if args.target_npy else "")
    out_dir = (Path(args.out_dir) if args.out_dir else
               default_out_dir(run_dir, args.seed, tag, args.inner_loss,
                               args.input_config))
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
    extra_labels, extra_cols = load_extra_inputs(args.extra_input_npy,
                                                 len(test_idx))
    n = min(args.n_samples, len(test_idx))
    test_idx = test_idx[:n]
    print(f"[load] using first {n} test indices")

    y_raw = y_full[:n]
    X_raw, input_labels = build_inputs(theta[test_idx], input_names)
    if extra_labels:
        clash = sorted(set(extra_labels) & set(input_labels))
        if clash:
            raise SystemExit(f"extra-input labels clash with --inputs: {clash}")
        X_raw = np.column_stack([X_raw] + [c[:n] for c in extra_cols])
        input_labels = input_labels + extra_labels
    print(f"[load] X shape={X_raw.shape}, input_labels={input_labels}, "
          f"y mean={y_raw.mean():.3f}, std={y_raw.std():.3f}")

    # --- Train/val split (deterministic) -------------------------------------
    n_val = int(round(n * args.val_frac))
    n_fit = n - n_val
    X_fit, X_val = X_raw[:n_fit], X_raw[n_fit:]
    y_fit, y_val = y_raw[:n_fit], y_raw[n_fit:]
    print(f"[split] n_fit={n_fit}, n_val={n_val}")

    # --- Standardise y (fit-only mean/std) -----------------------------------
    # Harmless under MI (a bijection) and conditioning-preserving under MSE.
    # The transform is fit on T0-fit only and is inverted for native metrics.
    y_mean, y_std = float(y_fit.mean()), float(y_fit.std())
    if not np.isfinite(y_std) or y_std <= 0:
        raise SystemExit("fit target has zero or non-finite standard deviation")
    y_fit_s = (y_fit - y_mean) / y_std
    y_val_s = (y_val - y_mean) / y_std

    # --- OLS baseline (data-driven only) -------------------------------------
    if args.skip_ols_baseline:
        ols_baseline = {
            "status": "skipped",
            "reason": "fixed_old_ols_reused_downstream",
        }
        print("[baseline OLS] skipped (fixed old OLS reused downstream)")
    else:
        X_fit_aug = np.column_stack([X_fit, np.ones(n_fit)])
        beta_ols, *_ = np.linalg.lstsq(X_fit_aug, y_fit_s, rcond=None)
        yhat_ols_val = np.column_stack([X_val, np.ones(n_val)]) @ beta_ols
        mse_ols = float(np.mean((yhat_ols_val - y_val_s) ** 2))
        ols_baseline = {
            "coefs": beta_ols.tolist(),
            "var_names": input_labels + ["bias"],
            "mse_val": mse_ols,
        }
        print(f"[baseline OLS] MSE_val={mse_ols:.4f}  beta={beta_ols}")

    # --- PySR fit -------------------------------------------------------------
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
        output_directory=str(out_dir / "pysr_state"),
        run_id=args.pysr_run_id,
    )
    sr_kwargs.update(input_config_pysr_kwargs)
    sr_kwargs.update(pysr_loss_kwargs(args.inner_loss))
    # Keep mini-batching disabled for parity across objectives (and because it
    # would bias the batch-level GMM-MI estimator on tiny sub-batches).
    if args.turbo:
        sr_kwargs["turbo"] = True
    if args.parallelism == "serial":
        sr_kwargs["deterministic"] = True
    pysr_extra = json.loads(args.pysr_extra)
    if not isinstance(pysr_extra, dict):
        raise SystemExit("--pysr-extra must be a JSON object")
    managed = set(sr_kwargs) | {"loss_function", "elementwise_loss"}
    clash = sorted(set(pysr_extra) & managed)
    if clash:
        raise SystemExit(f"--pysr-extra may not override managed kwargs: {clash}")
    sr_kwargs.update(pysr_extra)
    print(f"[pysr] inner_loss={args.inner_loss}  "
          f"selection_metric={selection_metric}")
    hidden = ("binary_operators", "unary_operators", "loss_function",
              "elementwise_loss")
    print(f"[pysr] kwargs={ {k: v for k, v in sr_kwargs.items() if k not in hidden} }")

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
    val_predictions = {}
    for i in range(len(eqs)):
        # Degenerate front members (e.g. sub-expressions that simplify to 1/0
        # -> ComplexInfinity) can fail sympy lambdification inside predict;
        # keep the row with mse_val=None so downstream MI selection skips it.
        try:
            yhat_fit_s = np.asarray(
                _with_timeout(120, model.predict, X_fit, index=i),
                dtype=np.float64,
            ).reshape(-1)
            yhat_val_s = np.asarray(
                _with_timeout(120, model.predict, X_val, index=i),
                dtype=np.float64,
            ).reshape(-1)
            if len(yhat_fit_s) != n_fit or len(yhat_val_s) != n_val:
                raise ValueError(
                    "prediction row mismatch: "
                    f"fit {len(yhat_fit_s)}/{n_fit}, "
                    f"val {len(yhat_val_s)}/{n_val}")
            finite_fit = np.isfinite(yhat_fit_s) & np.isfinite(y_fit_s)
            finite = np.isfinite(yhat_val_s) & np.isfinite(y_val_s)
            finite_frac_fit = float(finite_fit.mean())
            finite_frac = float(finite.mean())
            if finite_frac_fit < 0.999 or finite_frac < 0.999:
                raise ValueError(
                    "finite prediction fraction below 0.999: "
                    f"fit={finite_frac_fit:.6f}, val={finite_frac:.6f}")
            mse_fit_eval = float(np.mean(
                (yhat_fit_s[finite_fit] - y_fit_s[finite_fit]) ** 2))
            mse_val = float(np.mean((yhat_val_s[finite] - y_val_s[finite]) ** 2))
            yhat_val = y_mean + y_std * yhat_val_s[finite]
            y_val_finite = y_val[finite]
            error_native = y_val_finite - yhat_val
            mse_val_native = float(np.mean(error_native**2))
            variance_val = float(np.var(y_val_finite))
            abs_error_native = np.abs(error_native)
            rmse_val_native = float(np.sqrt(mse_val_native))
            nmse_val = (float(mse_val_native / variance_val)
                        if variance_val > 0 else None)
            r2_val = (float(1.0 - mse_val_native / variance_val)
                      if variance_val > 0 else None)
            mae_val_native = float(abs_error_native.mean())
            p95_val_native = float(np.quantile(abs_error_native, 0.95))
            p99_val_native = float(np.quantile(abs_error_native, 0.99))
            val_predictions[i] = (yhat_val_s, finite)
            eval_error = None
        except Exception as exc:                                     # noqa: BLE001
            mse_fit_eval = None
            mse_val = None
            mse_val_native = rmse_val_native = nmse_val = r2_val = None
            mae_val_native = p95_val_native = p99_val_native = None
            finite_frac_fit = 0.0
            finite_frac = 0.0
            eval_error = str(exc)
        row = {
            "index": int(i),
            "complexity": int(eqs.iloc[i]["complexity"]),
            "loss_train": float(eqs.iloc[i]["loss"]),
            "expression_raw": str(eqs.iloc[i]["equation"]),
            "mse_fit_eval": mse_fit_eval,
            "mse_val": mse_val,
            "mse_val_standardized": mse_val,
            "mse_val_native": mse_val_native,
            "rmse_val_native": rmse_val_native,
            "nmse_val": nmse_val,
            "r2_val": r2_val,
            "mae_val_native": mae_val_native,
            "abs_error_p95_native": p95_val_native,
            "abs_error_p99_native": p99_val_native,
            "finite_frac_fit": finite_frac_fit,
            "finite_frac_val": finite_frac,
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

    # --- Optional post-hoc GMM-MI on validation ------------------------------
    if posthoc_mi == "full":
        from cmb_lcdm_sr.mi import mutual_information_gmm
        print(f"[selection={selection_metric}] computing GMM-MI for all "
              f"{len(rows)} equations...")
    else:
        mutual_information_gmm = None
        print(f"[selection={selection_metric}] skipping secondary GMM-MI "
              "front diagnostics")
    for r in rows:
        if mutual_information_gmm is None:
            r["mi_val"] = None
            r["mi_val_err"] = None
        else:
            try:
                yhat_val, finite = val_predictions[r["index"]]
                mi, err = _with_timeout(
                    300, mutual_information_gmm,
                    y_val_s[finite].reshape(-1, 1),
                    yhat_val[finite].reshape(-1, 1),
                    return_uncertainty=True,
                    max_samples=int(finite.sum()), seed=0,
                )
                r["mi_val"] = float(mi[0, 0])
                r["mi_val_err"] = float(err[0, 0])
            except Exception as exc:                                 # noqa: BLE001
                r["mi_val"] = None
                r["mi_val_err"] = None
                r["mi_val_error"] = str(exc)
        r["expression_simplified"] = _simplify(r["index"])
        try:
            expression = sympy.sympify(r["expression_simplified"])
            r["support"] = sorted(
                str(symbol) for symbol in expression.free_symbols
                if str(symbol) in input_labels)
        except Exception:                                            # noqa: BLE001
            r["support"] = None

    rows_sorted = rank_front(rows, selection_metric)
    if not rows_sorted:
        raise RuntimeError(
            f"no equation has a finite validation {selection_metric}")
    top_k = rows_sorted[:5]
    rank_label = f"VAL {selection_metric.upper()} (primary)"

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
        ax.set_ylabel(f"train loss ({loss_spec['kind_label']})")
        ax.set_title(f"PySR Pareto front  (run={run_dir.name}, target={target_label}, "
                     f"inner_loss={args.inner_loss}, seed={args.seed})")
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
        "extra_inputs": args.extra_input_npy,
        "n_samples": n,
        "n_fit": n_fit,
        "n_val": n_val,
        "y_mean_train": y_mean,
        "y_std_train": y_std,
        "target_transform": {
            "kind": "standardize",
            "fit_rows": [0, n_fit],
            "mean": y_mean,
            "std": y_std,
        },
        "inner_loss": args.inner_loss,
        "loss_kind": loss_spec["kind_label"],
        "selection_metric": selection_metric,
        "selection_direction": (
            "ascending" if selection_metric == "mse" else "descending"),
        "posthoc_mi_mode": posthoc_mi,
        "posthoc_mi_status": (
            "computed" if posthoc_mi == "full" else "skipped_not_selected"),
        "tie_break": ["complexity_ascending", "equation_index_ascending"],
        "seed": args.seed,
        "pysr_kwargs": {
            "niterations": args.niterations,
            "populations": args.populations,
            "maxsize": args.maxsize,
            "binary_operators": list(args.binary_operators),
            "unary_operators": list(args.unary_operators),
            "parallelism": args.parallelism,
            "random_state": args.seed,
            "run_id": args.pysr_run_id,
            "loss_kind": loss_spec["kind_label"],
            "pysr_version": __import__("pysr").__version__,
            **input_config_pysr_kwargs,
            **pysr_extra,
        },
        "ols_baseline": ols_baseline,
        "fit_seconds": t_fit,
        "n_equations": len(eqs),
        "all_equations": rows,
        "top5": top_k,
        "top5_ranked_by": rank_label,
        "best_index": top_k[0]["index"],
        "best_expression": top_k[0]["expression_simplified"],
        "best_mse_val": top_k[0].get("mse_val"),
        "best_mse_val_native": top_k[0].get("mse_val_native"),
        "best_mi_val": top_k[0].get("mi_val"),
    }
    if args.input_config:
        report.update({
            "input_config": args.input_config,
            "input_names": input_names,
            "input_sampled_expressions": input_sampled_expressions,
        })
    out_json = out_dir / "report.json"
    save_json(report, out_json)
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
