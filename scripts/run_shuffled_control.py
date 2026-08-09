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

For each Pareto-front equation we report MI of its prediction against BOTH:
  * the shuffled target it was trained on  (validation_MI_shuffled_eval), and
  * the TRUE unshuffled target            (validation_MI_unshuffled_eval, primary).

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
    JULIA_LOSS_GMM_MI,
    LOSS_KIND_LABEL,
    build_inputs,
)


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
    p.add_argument("--unary-operators", nargs="*", default=["exp", "log", "neg", "square"])
    p.add_argument("--binary-operators", nargs="*", default=["+", "*", "-", "/"])
    p.add_argument("--parallelism", choices=["serial", "multithreading", "multiprocessing"],
                   default="multithreading")
    p.add_argument("--turbo", action="store_true")
    p.add_argument("--out-dir", default=None,
                   help="Defaults to results/<run-name>/symbolic_regression_shuffled_seed<N>.")
    args = p.parse_args()

    run_dir = Path(args.run_dir)
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
        out_dir = (Path("results") / run_dir.name / "residual_sr"
                   / f"shuffled_{target_label}_s{args.shuffle_seed}")
    else:
        out_dir = (Path("results") / run_dir.name
                   / f"symbolic_regression_shuffled_seed{args.shuffle_seed}")
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
    y_shuf_fit_s = (y_shuf_fit - y_mean) / y_std
    y_shuf_val_s = (y_shuf_val - y_mean) / y_std

    # --- PySR with the IDENTICAL gmm_mi inner loss ---------------------------
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
        loss_function=JULIA_LOSS_GMM_MI,
        output_directory=str(out_dir / "pysr_state"),
        run_id="run",
    )
    if args.turbo:
        sr_kwargs["turbo"] = True
    if args.parallelism == "serial":
        sr_kwargs["deterministic"] = True

    model = PySRRegressor(**sr_kwargs)
    t0 = time.time()
    model.fit(X_fit, y_shuf_fit_s, variable_names=input_labels)
    t_fit = time.time() - t0
    print(f"[pysr] fit done in {t_fit:.1f}s")

    eqs = model.equations_
    if eqs is None or len(eqs) == 0:
        raise RuntimeError("PySR returned no equations.")
    eqs.to_csv(out_dir / "equations.csv", index=False)

    from cmb_lcdm_sr.mi import mutual_information_gmm
    import sympy

    def mi(a, b):
        try:
            m, _ = mutual_information_gmm(a.reshape(-1, 1), b.reshape(-1, 1),
                                          return_uncertainty=True, max_samples=len(a), seed=0)
            return float(m[0, 0])
        except Exception:  # noqa: BLE001
            return None

    rows = []
    for i in range(len(eqs)):
        yhat_val_s = model.predict(X_val, index=i)
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
            # MI vs the shuffled target it was trained on:
            "mi_val_shuffled": mi(y_shuf_val_s, yhat_val_s),
            # MI vs the TRUE unshuffled target (the primary control number):
            "mi_val_unshuffled": mi(y_true_val, yhat_val_s),
        })

    # Selection mimics the real pipeline: best by shuffled-target val MI.
    def _key(r):
        v = r.get("mi_val_shuffled")
        return v if v is not None and np.isfinite(v) else float("-inf")
    best = max(rows, key=_key)

    report = {
        "run_dir": str(run_dir),
        "regime": run_dir.name,
        "target_index": args.target_index,
        "target_label": target_label,
        "inputs_exposed": input_labels,
        "extra_inputs": args.extra_input_npy,
        "inner_loss": INNER_LOSS_NAME,
        "control": "shuffled_target",
        "shuffle_seed": args.shuffle_seed,
        "pysr_seed": args.pysr_seed,
        "n_samples": n, "n_fit": n_fit, "n_val": n_val,
        "fit_seconds": t_fit,
        "best_expression": best["expression_simplified"],
        "best_mi_val_shuffled_eval": best["mi_val_shuffled"],
        "best_mi_val_unshuffled_eval": best["mi_val_unshuffled"],
        "pysr_version": __import__("pysr").__version__,
        "loss_kind": LOSS_KIND_LABEL,
        "all_equations": rows,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2))
    print(f"[done] best expr={best['expression_simplified']}")
    print(f"[done] MI vs shuffled={best['mi_val_shuffled']}  MI vs TRUE={best['mi_val_unshuffled']}")
    print(f"[done] -> {out_dir / 'report.json'}")


if __name__ == "__main__":
    main()
