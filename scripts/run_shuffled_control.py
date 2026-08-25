#!/usr/bin/env python
"""Shuffled-target negative control for blind symbolic regression.

Companion to ``run_blind_sr.py``. The real blind-SR runs feed PySR the raw
pair (A_s, tau) and the encoder amplitude latent, scored by the GMM-MI inner
loss, and recover the textbook ln(A_s·e^{-2τ}) direction. This control
destroys the physical row-wise relation by permuting the target latent across
rows while keeping the (A_s, tau) inputs fixed, then runs the IDENTICAL PySR
configuration.

Expected: the discovered expressions should NOT contain the textbook form and
their validation MI should sit at the null/noise level.

For MI-selected runs, each Pareto-front equation reports MI against both the
shuffled and true targets. MSE-selected controls skip those expensive
secondary diagnostics by default and retain the planned MSE/R2 readouts.

Usage (one regime × one shuffle seed):
    python scripts/run_shuffled_control.py \
        --run-dir models/lcdm_tt_beta3e-4 --target-index 2 \
        --shuffle-seed 0 --pysr-seed 0 --inputs A_s tau \
        --n-samples 5000 --niterations 200

Phase-6 variant (shuffled-RESIDUAL control): the target may instead be any
cached test-aligned vector via --target-npy/--target-label — the same M1
interface as run_blind_sr.py — e.g. the Phase-3 residual caches:
    python scripts/run_shuffled_control.py \
        --run-dir models/lcdm_tt_beta3e-4 \
        --target-npy models/lcdm_tt_beta3e-4/analysis/residual_z2_v1.npy \
        --target-label res_z2 --shuffle-seed 0 \
        --inputs omega_b omega_cdm H0 tau A_s n_s --niterations 200
"""
import argparse
import json
import time
from pathlib import Path

import _bootstrap  # noqa: F401

import numpy as np

from run_blind_sr import load_extra_inputs, resolve_target

# Reuse the EXACT blind-SR machinery so this is the same configuration.
from cmb_lcdm_sr.sr import (
    INNER_LOSS_NAME,
    LOSS_SPECS,
    build_inputs,
    pysr_loss_kwargs,
    rank_front,
    resolve_loss,
    resolve_posthoc_mi,
)
from cmb_lcdm_sr.utils import save_json


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run-dir", required=True)
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--target-index", type=int, default=None,
                   help="Latent column (0-indexed) of the latent to shuffle.")
    p.add_argument("--target-npy", default=None,
                   help="Shuffle an arbitrary test-aligned cached vector "
                        "instead of a latent column (mutually exclusive "
                        "with --target-index).")
    p.add_argument("--target-label", default=None,
                   help="Label for --target-npy targets (default: file stem).")
    p.add_argument("--inputs", nargs="+", default=["A_s", "tau"])
    p.add_argument("--extra-input-npy", action="append", default=[],
                   metavar="LABEL=PATH",
                   help="Additional SR input column ('label=path.npy', "
                        "repeatable) — same interface as run_blind_sr.py, so "
                        "the interaction-aware control exposes f1hat too.")
    p.add_argument("--n-samples", type=int, default=5000)
    p.add_argument("--val-frac", type=float, default=0.2)
    p.add_argument("--niterations", type=int, default=200)
    p.add_argument("--populations", type=int, default=15)
    p.add_argument("--maxsize", type=int, default=20)
    p.add_argument("--shuffle-seed", type=int, required=True)
    p.add_argument("--pysr-seed", type=int, default=0)
    p.add_argument("--inner-loss", choices=sorted(LOSS_SPECS),
                   default=INNER_LOSS_NAME)
    p.add_argument("--selection-metric", choices=["auto", "mi", "mse"],
                   default="auto")
    p.add_argument("--posthoc-mi", choices=["auto", "full", "none"],
                   default="auto",
                   help="Full GMM-MI front diagnostics; auto computes them "
                        "only when MI selects the front.")
    p.add_argument("--unary-operators", nargs="*", default=["exp", "log", "neg", "square"])
    p.add_argument("--binary-operators", nargs="*", default=["+", "*", "-", "/"])
    p.add_argument("--parallelism", choices=["serial", "multithreading", "multiprocessing"],
                   default="multithreading")
    p.add_argument("--turbo", action="store_true")
    p.add_argument("--pysr-extra", default="{}",
                   help="JSON object of additional PySRRegressor kwargs.")
    p.add_argument("--pysr-run-id", default="run",
                   help="Internal PySR state subdirectory (default: run).")
    p.add_argument("--out-dir", default=None,
                   help="Defaults to results/<run-name>/symbolic_regression_shuffled_seed<N>.")
    args = p.parse_args()

    run_dir = Path(args.run_dir)
    loss_spec, selection_metric = resolve_loss(
        args.inner_loss, args.selection_metric)
    posthoc_mi = resolve_posthoc_mi(args.posthoc_mi, selection_metric)
    y_full, target_label = resolve_target(run_dir, args.target_index,
                                          args.target_npy, args.target_label,
                                          dataset_dir=args.dataset_dir)
    theta = np.load(Path(args.dataset_dir) / "theta.npy")
    splits = np.load(Path(args.dataset_dir) / "splits_v1.npz")
    test_idx = np.where(splits["split_id"] == 2)[0]
    if len(y_full) != len(test_idx):
        raise SystemExit(f"target has {len(y_full)} rows, test split has "
                         f"{len(test_idx)} — must be row-aligned")
    n = min(args.n_samples, len(test_idx))
    test_idx = test_idx[:n]
    y_true = y_full[:n]

    # Inputs — UNCHANGED (only the target is permuted).
    extra_labels, extra_cols = load_extra_inputs(args.extra_input_npy,
                                                 len(y_full))
    X_raw, input_labels = build_inputs(theta[test_idx], args.inputs)
    if extra_labels:
        X_raw = np.column_stack([X_raw] + [c[:n] for c in extra_cols])
        input_labels = input_labels + extra_labels

    # Permute ONLY the target across rows (preserves marginal, kills relation).
    perm = np.random.default_rng(args.shuffle_seed).permutation(n)
    y_shuf = y_true[perm]

    if args.out_dir:
        out_dir = Path(args.out_dir)
    elif args.target_npy is not None:
        namespace = ("residual_sr" if args.inner_loss == INNER_LOSS_NAME
                     else "mse_one_stage_control")
        out_dir = (Path("results") / run_dir.name / namespace
                   / f"shuffled_{target_label}_s{args.shuffle_seed}")
    else:
        stem = ("symbolic_regression_shuffled"
                if args.inner_loss == INNER_LOSS_NAME
                else "symbolic_regression_mse_shuffled")
        out_dir = (Path("results") / run_dir.name
                   / f"{stem}_seed{args.shuffle_seed}")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[setup] out_dir={out_dir}")
    print(f"[setup] run={run_dir.name} target={target_label} "
          f"shuffle_seed={args.shuffle_seed} pysr_seed={args.pysr_seed} n={n}")

    # Train/val split (deterministic prefix split, matching the real SR script).
    n_val = int(round(n * args.val_frac))
    n_fit = n - n_val
    X_fit, X_val = X_raw[:n_fit], X_raw[n_fit:]
    y_shuf_fit, y_shuf_val = y_shuf[:n_fit], y_shuf[n_fit:]
    y_true_val = y_true[n_fit:]

    # Standardise the (shuffled) target on fit-only stats, as the real script does.
    y_mean, y_std = float(y_shuf_fit.mean()), float(y_shuf_fit.std())
    if not np.isfinite(y_std) or y_std <= 0:
        raise SystemExit("fit target has zero or non-finite standard deviation")
    y_shuf_fit_s = (y_shuf_fit - y_mean) / y_std
    y_shuf_val_s = (y_shuf_val - y_mean) / y_std
    y_true_val_s = (y_true_val - y_mean) / y_std

    # --- PySR with the identical selected inner loss -------------------------
    from pysr import PySRRegressor
    sr_kwargs = dict(
        niterations=args.niterations,
        populations=args.populations,
        maxsize=args.maxsize,
        binary_operators=list(args.binary_operators),
        unary_operators=list(args.unary_operators),
        random_state=args.pysr_seed,
        parallelism=args.parallelism,
        progress=False,
        verbosity=1,
        output_directory=str(out_dir / "pysr_state"),
        run_id=args.pysr_run_id,
    )
    sr_kwargs.update(pysr_loss_kwargs(args.inner_loss))
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

    model = PySRRegressor(**sr_kwargs)
    t0 = time.time()
    model.fit(X_fit, y_shuf_fit_s, variable_names=input_labels)
    t_fit = time.time() - t0
    print(f"[pysr] fit done in {t_fit:.1f}s")

    eqs = model.equations_
    if eqs is None or len(eqs) == 0:
        raise RuntimeError("PySR returned no equations.")
    eqs.to_csv(out_dir / "equations.csv", index=False)

    import sympy

    if posthoc_mi == "full":
        from cmb_lcdm_sr.mi import mutual_information_gmm

        def mi(a, b):
            try:
                m, _ = mutual_information_gmm(
                    a.reshape(-1, 1), b.reshape(-1, 1),
                    return_uncertainty=True, max_samples=len(a), seed=0)
                return float(m[0, 0])
            except Exception:  # noqa: BLE001
                return None
    else:
        print(f"[selection={selection_metric}] skipping secondary GMM-MI "
              "front diagnostics")

        def mi(a, b):
            return None

    rows = []
    for i in range(len(eqs)):
        try:
            yhat_fit_s = np.asarray(
                model.predict(X_fit, index=i), dtype=np.float64).reshape(-1)
            yhat_val_s = np.asarray(
                model.predict(X_val, index=i), dtype=np.float64).reshape(-1)
            finite_fit = np.isfinite(yhat_fit_s) & np.isfinite(y_shuf_fit_s)
            finite = (np.isfinite(yhat_val_s)
                      & np.isfinite(y_shuf_val_s)
                      & np.isfinite(y_true_val_s))
            finite_frac_fit = float(finite_fit.mean())
            finite_frac = float(finite.mean())
            if finite_frac_fit < 0.999 or finite_frac < 0.999:
                raise ValueError(
                    "finite prediction fraction below 0.999: "
                    f"fit={finite_frac_fit:.6f}, val={finite_frac:.6f}")
            mse_fit = float(np.mean(
                (y_shuf_fit_s[finite_fit] - yhat_fit_s[finite_fit]) ** 2))
            mse_shuf = float(np.mean(
                (y_shuf_val_s[finite] - yhat_val_s[finite]) ** 2))
            mse_true = float(np.mean(
                (y_true_val_s[finite] - yhat_val_s[finite]) ** 2))
            prediction_native = y_mean + y_std * yhat_val_s[finite]
            shuffled_native = y_shuf_val[finite]
            true_native = y_true_val[finite]
            err_shuf_native = shuffled_native - prediction_native
            err_true_native = true_native - prediction_native
            mse_shuf_native = float(np.mean(err_shuf_native**2))
            mse_true_native = float(np.mean(err_true_native**2))
            var_shuf = float(np.var(shuffled_native))
            var_true = float(np.var(true_native))
            r2_shuf = (float(1.0 - mse_shuf_native / var_shuf)
                       if var_shuf > 0 else None)
            r2_true = (float(1.0 - mse_true_native / var_true)
                       if var_true > 0 else None)
            mi_shuf = mi(y_shuf_val_s[finite], yhat_val_s[finite])
            mi_true = mi(y_true_val_s[finite], yhat_val_s[finite])
            eval_error = None
        except Exception as exc:  # noqa: BLE001
            finite_frac_fit = 0.0
            finite_frac = 0.0
            mse_fit = None
            mse_shuf = mse_true = mi_shuf = mi_true = None
            mse_shuf_native = mse_true_native = None
            r2_shuf = r2_true = None
            eval_error = str(exc)
        try:
            expr_simpl = str(sympy.simplify(model.sympy(index=i)))
        except Exception as exc:  # noqa: BLE001
            expr_simpl = f"<sympy failed: {exc}>"
        rows.append({
            "index": int(i),
            "complexity": int(eqs.iloc[i]["complexity"]),
            "loss_train": float(eqs.iloc[i]["loss"]),
            "expression_raw": str(eqs.iloc[i]["equation"]),
            "expression_simplified": expr_simpl,
            "finite_frac_fit": finite_frac_fit,
            "finite_frac_val": finite_frac,
            "mse_fit_eval": mse_fit,
            "mse_val": mse_shuf,
            "mse_val_standardized": mse_shuf,
            "mse_val_shuffled": mse_shuf,
            "mse_val_unshuffled": mse_true,
            "mse_val_shuffled_native": mse_shuf_native,
            "mse_val_unshuffled_native": mse_true_native,
            "r2_val_shuffled": r2_shuf,
            "r2_val_unshuffled": r2_true,
            # MI vs the shuffled target it was trained on:
            "mi_val": mi_shuf,
            "mi_val_shuffled": mi_shuf,
            # MI vs the TRUE unshuffled target (the primary control number):
            "mi_val_unshuffled": mi_true,
        })
        if eval_error is not None:
            rows[-1]["eval_error"] = eval_error

    # Selection exactly mirrors run_blind_sr.py on the shuffled target.
    ranked = rank_front(rows, selection_metric)
    if not ranked:
        raise RuntimeError(
            f"no equation has a finite validation {selection_metric}")
    best = ranked[0]

    report = {
        "run_dir": str(run_dir),
        "regime": run_dir.name,
        "target_index": args.target_index,
        "target_label": target_label,
        "inputs_exposed": input_labels,
        "extra_inputs": args.extra_input_npy,
        "inner_loss": args.inner_loss,
        "loss_kind": loss_spec["kind_label"],
        "selection_metric": selection_metric,
        "selection_direction": (
            "ascending" if selection_metric == "mse" else "descending"),
        "posthoc_mi_mode": posthoc_mi,
        "posthoc_mi_status": (
            "computed" if posthoc_mi == "full" else "skipped_not_selected"),
        "tie_break": ["complexity_ascending", "equation_index_ascending"],
        "control": "shuffled_target",
        "shuffle_seed": args.shuffle_seed,
        "pysr_seed": args.pysr_seed,
        "n_samples": n, "n_fit": n_fit, "n_val": n_val,
        "fit_seconds": t_fit,
        "target_transform": {
            "kind": "standardize",
            "fit_rows": [0, n_fit],
            "mean": y_mean,
            "std": y_std,
        },
        "pysr_kwargs": {
            "niterations": args.niterations,
            "populations": args.populations,
            "maxsize": args.maxsize,
            "binary_operators": list(args.binary_operators),
            "unary_operators": list(args.unary_operators),
            "parallelism": args.parallelism,
            "random_state": args.pysr_seed,
            "run_id": args.pysr_run_id,
            "loss_kind": loss_spec["kind_label"],
            "pysr_version": __import__("pysr").__version__,
            **pysr_extra,
        },
        "best_index": best["index"],
        "best_expression": best["expression_simplified"],
        "best_mse_val_shuffled_eval": best["mse_val_shuffled"],
        "best_mse_val_unshuffled_eval": best["mse_val_unshuffled"],
        "best_mi_val_shuffled_eval": best["mi_val_shuffled"],
        "best_mi_val_unshuffled_eval": best["mi_val_unshuffled"],
        "pysr_version": __import__("pysr").__version__,
        "all_equations": rows,
    }
    save_json(report, out_dir / "report.json")
    print(f"[done] best expr={best['expression_simplified']}")
    print(f"[done] MSE vs shuffled={best['mse_val_shuffled']}  "
          f"MSE vs TRUE={best['mse_val_unshuffled']}")
    print(f"[done] MI vs shuffled={best['mi_val_shuffled']}  MI vs TRUE={best['mi_val_unshuffled']}")
    print(f"[done] -> {out_dir / 'report.json'}")


if __name__ == "__main__":
    main()
