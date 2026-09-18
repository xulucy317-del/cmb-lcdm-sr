#!/usr/bin/env python
"""Frozen evaluation for the ``precision_preprocess_v1`` SR campaign.

The campaign has three input configurations (``raw64``,
``physical_o1_64``, and ``logamp64``), but deliberately retains the scientific
endpoints of the existing OLS/MI-SR/MSE-SR comparison:

* MI-SR is selected from a maxsize-20 GMM-MI search front;
* MSE-SR is selected from a maxsize-40 MSE search front;
* MI-SR receives a T1-only monotone calibration for reconstruction;
* GMM-MI is evaluated on one matched subset of T2 and NMSE on all of T2; and
* the existing physical-input OLS coefficients are reused, never refitted.

The four subcommands enforce the data boundary explicitly: ``select`` reads
reports only, ``calibrate`` opens T1 only, ``confirm`` is the first stage that
opens T2, and ``render`` reads confirmation JSON only.  All defaults write
under new ``precision_preprocess_v1`` namespaces.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

import _bootstrap  # noqa: F401

import numpy as np
import sympy

from cmb_lcdm_sr import calibrate, semantics, tiers, utils
from cmb_lcdm_sr.mi import mutual_information_gmm
from cmb_lcdm_sr.sr import build_inputs, rank_front, resolve_input_config


STUDY = "precision_preprocess_v1"
SCHEMA_VERSION = 1
ARM_IDS = ("raw64", "physical_o1_64", "logamp64")
MODELS = {
    "lcdm_tt_beta3e-4": {"n_latents": 5, "label": "TT"},
    "lcdm_tt_ee_lowl": {"n_latents": 6, "label": "TT+EE"},
}
SEEDS = (0, 1, 2, 3, 4)
FINITE_MIN = 0.999
MI_SUBSET_SIZE = 5000
MI_SUBSET_SEED = 0
METHOD_SPECS = {
    "mi20-mi": {
        "subdir": "gmm_mi_ms20",
        "inner_loss": "gmm_mi",
        "selection_metric": "mi",
        "budget": 20,
    },
    "mse40": {
        "subdir": "mse_ms40",
        "inner_loss": "mse",
        "selection_metric": "mse",
        "budget": 40,
    },
}


def _jsonable(value):
    if isinstance(value, np.ndarray):
        return [_jsonable(item) for item in value.tolist()]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def object_sha256(value: object) -> str:
    encoded = json.dumps(
        _jsonable(value), sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_key(path: str | Path) -> str:
    return str(Path(path).resolve())


def add_source(sources: dict[str, str], path: str | Path) -> None:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    sources[_source_key(path)] = file_sha256(path)


def verify_sources(sources: dict[str, str]) -> None:
    for raw_path, expected in sources.items():
        path = Path(raw_path)
        if not path.exists():
            raise FileNotFoundError(f"frozen source missing: {path}")
        actual = file_sha256(path)
        if actual != expected:
            raise ValueError(
                f"frozen source changed: {path}\n"
                f"expected {expected}\nactual   {actual}")


def _attach_digest(payload: dict, key: str) -> dict:
    out = _jsonable(payload)
    out[key] = object_sha256(out)
    return out


def verify_digest(payload: dict, key: str) -> None:
    claimed = payload.get(key)
    if not claimed:
        raise ValueError(f"missing {key}")
    body = dict(payload)
    body.pop(key, None)
    actual = object_sha256(body)
    if claimed != actual:
        raise ValueError(
            f"{key} mismatch: expected {claimed}, recomputed {actual}")


def write_immutable_json(path: str | Path, payload: dict, key: str) -> Path:
    path = Path(path)
    if path.exists():
        existing = json.loads(path.read_text())
        if existing.get(key) == payload.get(key):
            return path
        raise FileExistsError(
            f"refusing to overwrite immutable artifact: {path}")
    utils.save_json(payload, path)
    return path


def verify_artifact(path: str | Path, kind: str, digest_key: str) -> dict:
    payload = json.loads(Path(path).read_text())
    if payload.get("kind") != kind or payload.get("study") != STUDY:
        raise ValueError(f"unexpected artifact kind/study in {path}")
    verify_digest(payload, digest_key)
    verify_sources(payload.get("source_files", {}))
    return payload


def arm_root(results_root: str | Path, run: str, arm: str) -> Path:
    return Path(results_root) / run / STUDY / arm


def report_path(results_root: str | Path, run: str, arm: str,
                method: str, latent: int, seed: int) -> Path:
    spec = METHOD_SPECS[method]
    return (arm_root(results_root, run, arm) / spec["subdir"] /
            f"z{latent}_seed{seed}" / "report.json")


def _normalised_config(arm: str) -> dict:
    config = resolve_input_config(arm)
    return _jsonable(config)


def _expected_config_fields(arm: str) -> tuple[list[str], dict]:
    config = _normalised_config(arm)
    labels = list(config.get("input_labels", config.get("labels", ())))
    if not labels:
        labels = list(config.get("sampled_expressions", {}).keys())
    expressions = dict(config.get("sampled_expressions", {}))
    if not labels or set(labels) != set(expressions):
        raise ValueError(f"input config '{arm}' has inconsistent labels")
    return labels, expressions


def validate_report(report: dict, arm: str, method: str, path: Path) -> None:
    spec = METHOD_SPECS[method]
    labels, expressions = _expected_config_fields(arm)
    config = _normalised_config(arm)
    posthoc_mode = "full" if method == "mi20-mi" else "none"
    checks = {
        "input_config": (report.get("input_config"), arm),
        "input_names": (list(report.get("input_names", ())),
                        list(config["inputs"])),
        "inner_loss": (report.get("inner_loss"), spec["inner_loss"]),
        "selection_metric": (
            report.get("selection_metric"), spec["selection_metric"]),
        "selection_direction": (
            report.get("selection_direction"),
            "descending" if spec["selection_metric"] == "mi" else "ascending"),
        "posthoc_mi_mode": (report.get("posthoc_mi_mode"), posthoc_mode),
        "posthoc_mi_status": (
            report.get("posthoc_mi_status"),
            "computed" if posthoc_mode == "full" else "skipped_not_selected"),
        "n_samples": (int(report.get("n_samples", -1)), 5000),
        "n_fit": (int(report.get("n_fit", -1)), 4000),
        "n_val": (int(report.get("n_val", -1)), 1000),
        "input_labels": (list(report.get("input_labels", ())), labels),
        "input_sampled_expressions": (
            report.get("input_sampled_expressions"), expressions),
    }
    kwargs = report.get("pysr_kwargs", {})
    checks.update({
        "niterations": (int(kwargs.get("niterations", -1)), 200),
        "populations": (int(kwargs.get("populations", -1)), 15),
        "maxsize": (int(kwargs.get("maxsize", -1)), spec["budget"]),
        "precision": (int(kwargs.get("precision", -1)), 64),
        "print_precision": (int(kwargs.get("print_precision", -1)), 17),
        "parallelism": (kwargs.get("parallelism"), "multithreading"),
        "binary_operators": (
            kwargs.get("binary_operators"), ["+", "*", "-", "/"]),
        "unary_operators": (
            kwargs.get("unary_operators"), ["exp", "log", "neg", "square"]),
    })
    for name, (actual, expected) in checks.items():
        if actual != expected:
            raise ValueError(
                f"{path}: {name}={actual!r}, expected {expected!r}")
    if report.get("target_npy") is not None:
        raise ValueError(f"{path}: target_npy must be null")
    if report.get("extra_inputs") not in ([], None):
        raise ValueError(f"{path}: extra_inputs must be empty")
    if report.get("tie_break") != [
            "complexity_ascending", "equation_index_ascending"]:
        raise ValueError(f"{path}: unexpected tie_break")
    ols = report.get("ols_baseline")
    if not isinstance(ols, dict) or ols != {
            "status": "skipped",
            "reason": "fixed_old_ols_reused_downstream",
    }:
        raise ValueError(
            f"{path}: ols_baseline must be the exact frozen skipped status")
    if int(kwargs.get("random_state", -1)) != int(report.get("seed", -2)):
        raise ValueError(f"{path}: pysr random_state does not match seed")
    if not isinstance(kwargs.get("run_id"), str) or not kwargs["run_id"]:
        raise ValueError(f"{path}: pysr run_id is empty")
    equations = report.get("all_equations")
    if (not isinstance(equations, list) or not equations or
            int(report.get("n_equations", -1)) != len(equations)):
        raise ValueError(f"{path}: invalid equation-front cardinality")
    if not isinstance(report.get("best_expression"), str) or not (
            report["best_expression"].strip()):
        raise ValueError(f"{path}: best_expression is empty")
    best_metric = (
        report.get("best_mi_val") if spec["selection_metric"] == "mi"
        else report.get("best_mse_val"))
    if not isinstance(best_metric, (int, float)) or not np.isfinite(best_metric):
        raise ValueError(f"{path}: selected validation metric is non-finite")
    transform = report.get("target_transform", {})
    if (transform.get("kind") != "standardize" or
            list(transform.get("fit_rows", ())) != [0, 4000] or
            not np.isfinite(float(transform.get("mean", np.nan))) or
            not np.isfinite(float(transform.get("std", np.nan))) or
            float(transform["std"]) <= 0):
        raise ValueError(f"{path}: invalid T0-fit target transform")


def expression_of(row: dict) -> str:
    expression = row.get("expression_simplified")
    if not expression or str(expression).startswith("<sympy failed"):
        expression = row.get("expression_raw")
    if not expression:
        raise ValueError(f"equation {row.get('index')} has no expression")
    return str(expression)


def ranked_valid_front(report: dict, metric: str) -> list[dict]:
    rows = []
    for source in report.get("all_equations", []):
        row = dict(source)
        fit_frac = float(row.get("finite_frac_fit", 1.0))
        val_frac = float(row.get("finite_frac_val", 1.0))
        if (not np.isfinite(fit_frac) or not np.isfinite(val_frac) or
                fit_frac < FINITE_MIN or val_frac < FINITE_MIN):
            continue
        rows.append(row)
    return rank_front(rows, metric)


def _selection_record(report: dict, row: dict, report_file: Path,
                      arm: str, method: str, run: str, latent: int,
                      seed: int) -> dict:
    return {
        "run": run,
        "arm": arm,
        "method": method,
        "latent": int(latent),
        "seed": int(seed),
        "index": int(row["index"]),
        "complexity": int(row["complexity"]),
        "expression": expression_of(row),
        "mi_val": row.get("mi_val"),
        "mi_val_err": row.get("mi_val_err"),
        "mse_val": row.get("mse_val"),
        "mse_val_native": row.get("mse_val_native"),
        "nmse_val": row.get("nmse_val"),
        "finite_frac_fit": row.get("finite_frac_fit", 1.0),
        "finite_frac_val": row.get("finite_frac_val", 1.0),
        "target_transform": report["target_transform"],
        "input_names": report["input_names"],
        "input_labels": report["input_labels"],
        "input_sampled_expressions": report["input_sampled_expressions"],
        "report": _source_key(report_file),
    }


def build_selection_manifest(
        run: str, arm: str, results_root: str | Path = "results",
        latents: Iterable[int] | None = None,
        seeds: Iterable[int] = SEEDS) -> dict:
    """Freeze T0-only per-seed MI20 and MSE40 selections."""
    if run not in MODELS and latents is None:
        raise ValueError(f"unknown run '{run}'; pass explicit latents")
    if arm not in ARM_IDS:
        raise ValueError(f"unknown arm '{arm}'")
    if latents is None:
        latents = range(MODELS[run]["n_latents"])
    latents, seeds = tuple(map(int, latents)), tuple(map(int, seeds))
    sources: dict[str, str] = {}
    selections = []
    transforms: dict[int, dict] = {}
    for latent in latents:
        for method, spec in METHOD_SPECS.items():
            for seed in seeds:
                path = report_path(
                    results_root, run, arm, method, latent, seed)
                if not path.exists():
                    raise FileNotFoundError(path)
                report = json.loads(path.read_text())
                validate_report(report, arm, method, path)
                identity = {
                    "regime": (report.get("regime"), run),
                    "run_dir": (Path(report.get("run_dir", "")).name, run),
                    "latent_index": (int(report.get("latent_index", -1)), latent),
                    "seed": (int(report.get("seed", -1)), seed),
                }
                for name, (actual, expected) in identity.items():
                    if actual != expected:
                        raise ValueError(
                            f"{path}: {name}={actual!r}, expected {expected!r}")
                front = ranked_valid_front(report, spec["selection_metric"])
                if not front:
                    raise ValueError(f"{path}: no valid front member")
                record = _selection_record(
                    report, front[0], path, arm, method, run, latent, seed)
                selections.append(record)
                transform = _jsonable(record["target_transform"])
                previous = transforms.setdefault(latent, transform)
                if previous != transform:
                    raise ValueError(
                        f"z{latent}: target transform differs across runs")
                add_source(sources, path)
                equations = path.with_name("equations.csv")
                add_source(sources, equations)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "kind": "precision_preprocess_selection",
        "study": STUDY,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "run": run,
        "arm": arm,
        "arm_config": _normalised_config(arm),
        "latents": list(latents),
        "seeds": list(seeds),
        "methods": _jsonable(METHOD_SPECS),
        "selection_rules": {
            "mi20-mi": "maximum T0 validation GMM-MI",
            "mse40": "minimum T0 validation MSE",
            "ties": ["complexity_ascending", "equation_index_ascending"],
            "finite_fraction_min": FINITE_MIN,
        },
        "target_transforms": {str(k): v for k, v in transforms.items()},
        "selections": selections,
        "source_files": dict(sorted(sources.items())),
    }
    return _attach_digest(payload, "manifest_sha256")


def verify_selection(path: str | Path) -> dict:
    return verify_artifact(
        path, "precision_preprocess_selection", "manifest_sha256")


# ---- Arm-aware expression evaluation ---------------------------------------

def build_arm_inputs(theta: np.ndarray, arm: str,
                     labels: Iterable[str] | None = None) -> tuple[np.ndarray, list[str]]:
    """Evaluate one named input configuration on sampled-basis theta rows."""
    expected_labels, expressions = _expected_config_fields(arm)
    labels = expected_labels if labels is None else list(labels)
    if labels != expected_labels:
        raise ValueError(
            f"input labels {labels!r} do not match arm '{arm}' "
            f"labels {expected_labels!r}")
    columns = []
    for label in labels:
        values = semantics.evaluate_on_theta(expressions[label], theta)
        values = np.asarray(values, dtype=np.float64).reshape(-1)
        if len(values) != len(theta):
            raise ValueError(f"arm input '{label}' has wrong row count")
        columns.append(values)
    return np.column_stack(columns), labels


def parse_arm_expression(expression: str, labels: Iterable[str]) -> sympy.Expr:
    labels = list(labels)
    symbols = {label: sympy.Symbol(label) for label in labels}
    locals_ = dict(symbols)
    locals_.update({
        "exp": sympy.exp,
        "log": sympy.log,
        "sqrt": sympy.sqrt,
        "Abs": sympy.Abs,
        "square": lambda value: value**2,
        "neg": lambda value: -value,
    })
    parsed = sympy.sympify(str(expression).replace("^", "**"), locals=locals_)
    unknown = {str(symbol) for symbol in parsed.free_symbols} - set(labels)
    if unknown:
        raise ValueError(f"expression uses unknown arm symbols: {sorted(unknown)}")
    return parsed


def expression_in_sampled_basis(expression: str, arm: str,
                                labels: Iterable[str]) -> str:
    """Rewrite an arm expression into the six sampled physical coordinates."""
    labels = list(labels)
    parsed = parse_arm_expression(expression, labels)
    _, sampled_expressions = _expected_config_fields(arm)
    replacements = {}
    for label in labels:
        sampled = semantics.parse_expr(sampled_expressions[label])
        if sampled is None:
            raise ValueError(
                f"cannot parse sampled semantics for {arm}/{label}")
        replacements[sympy.Symbol(label)] = sampled
    return str(sympy.simplify(parsed.xreplace(replacements)))


def has_as_tau_signature(sampled_expression: str,
                         tolerance: float = 0.02) -> bool:
    """Detect f(ln10As - 2*tau, ...) through its differential signature."""
    parsed = semantics.parse_expr(sampled_expression)
    if parsed is None:
        return False
    tau = sympy.Symbol("tau")
    ln10as = sympy.Symbol("ln10As")
    d_tau = sympy.simplify(sympy.diff(parsed, tau))
    d_ln = sympy.simplify(sympy.diff(parsed, ln10as))
    if d_tau == 0 or d_ln == 0:
        return False
    relation = sympy.simplify(d_tau + 2 * d_ln)
    if relation == 0:
        return True
    ratio = sympy.simplify(d_tau / d_ln)
    if ratio.free_symbols:
        return False
    try:
        return bool(np.isclose(
            float(ratio), -2.0, atol=tolerance, rtol=tolerance))
    except (TypeError, ValueError):
        return False


def evaluate_arm_expression(expression: str, theta: np.ndarray, arm: str,
                            labels: Iterable[str]) -> np.ndarray:
    """Evaluate an SR expression using the exact arm-specific input columns."""
    matrix, labels = build_arm_inputs(theta, arm, labels)
    parsed = parse_arm_expression(expression, labels)
    symbols = [sympy.Symbol(label) for label in labels]
    fn = sympy.lambdify(symbols, parsed, modules="numpy")
    with np.errstate(all="ignore"):
        values = fn(*[matrix[:, j] for j in range(matrix.shape[1])])
    values = np.asarray(values)
    if values.ndim == 0:
        values = np.full(len(theta), values)
    values = np.squeeze(values)
    if values.shape != (len(theta),):
        raise ValueError(
            f"expression returned shape {values.shape}, expected {(len(theta),)}")
    if np.iscomplexobj(values):
        close = np.isclose(values.imag, 0.0, atol=1e-12, rtol=1e-12)
        real = np.full(len(values), np.nan, dtype=np.float64)
        real[close] = values.real[close]
        return real
    return values.astype(np.float64, copy=False)


def evaluate_selection(entry: dict, theta: np.ndarray) -> np.ndarray:
    standardised = evaluate_arm_expression(
        entry["expression"], theta, entry["arm"], entry["input_labels"])
    transform = entry["target_transform"]
    if transform.get("kind") != "standardize":
        raise ValueError(f"unsupported target transform: {transform}")
    return float(transform["mean"]) + float(transform["std"]) * standardised


def reconstruction_metrics(target: np.ndarray, prediction: np.ndarray) -> dict:
    target = np.asarray(target, dtype=np.float64)
    prediction = np.asarray(prediction, dtype=np.float64)
    if target.shape != prediction.shape:
        raise ValueError(
            f"metric shape mismatch: {target.shape} vs {prediction.shape}")
    finite = np.isfinite(target) & np.isfinite(prediction)
    out = {"finite_frac": float(finite.mean()), "n_finite": int(finite.sum())}
    if finite.mean() < FINITE_MIN or finite.sum() < 16:
        return out | {"valid": False}
    y, pred = target[finite], prediction[finite]
    error = y - pred
    mse = float(np.mean(error**2))
    variance = float(np.var(y))
    out.update({
        "valid": True,
        "mse": mse,
        "rmse": float(np.sqrt(mse)),
        "nmse": float(mse / variance) if variance > 0 else None,
        "r2": float(1.0 - mse / variance) if variance > 0 else None,
        "mae": float(np.mean(np.abs(error))),
    })
    return out


def _test_theta(dataset_dir: str | Path, tier: slice) -> np.ndarray:
    dataset_dir = Path(dataset_dir)
    split_id = np.load(dataset_dir / "splits_v1.npz")["split_id"]
    test_idx = np.where(split_id == 2)[0]
    theta = np.load(dataset_dir / "theta.npy", mmap_mode="r")
    return np.asarray(theta[test_idx[tier]], dtype=np.float64)


def _target_tier(models_root: str | Path, run: str, tier: slice,
                 latent: int) -> np.ndarray:
    means = np.load(
        Path(models_root) / run / "analysis" / "encoder_means_test.npy",
        mmap_mode="r")
    return np.asarray(means[tier, latent], dtype=np.float64)


def _data_sources(manifest: dict, dataset_dir: str | Path,
                  models_root: str | Path) -> dict[str, str]:
    sources = {}
    add_source(sources, Path(dataset_dir) / "theta.npy")
    add_source(sources, Path(dataset_dir) / "splits_v1.npz")
    add_source(
        sources,
        Path(models_root) / manifest["run"] / "analysis" /
        "encoder_means_test.npy",
    )
    return sources


# ---- T1 calibration ---------------------------------------------------------

def build_calibration_artifact(
        manifest_path: str | Path, dataset_dir: str | Path = "data",
        models_root: str | Path = "models") -> dict:
    """Verify selections, then open T1 only and freeze calibration diagnostics."""
    manifest = verify_selection(manifest_path)
    theta_t1 = _test_theta(dataset_dir, tiers.T1)
    diagnostics = []
    for entry in manifest["selections"]:
        target = _target_tier(
            models_root, manifest["run"], tiers.T1, int(entry["latent"]))
        prediction = evaluate_selection(entry, theta_t1)
        raw = reconstruction_metrics(target, prediction)
        row = {
            "method": entry["method"],
            "latent": int(entry["latent"]),
            "seed": int(entry["seed"]),
            "raw_T1": raw,
            "monotone_calibration_T1": None,
        }
        if entry["method"] == "mi20-mi":
            finite = np.isfinite(target) & np.isfinite(prediction)
            if finite.mean() >= FINITE_MIN:
                result = calibrate.crossfit_calibration(
                    prediction, target, n_folds=5, n_bins=64,
                    monotone=True, seed=int(entry["seed"]),
                )
                row["monotone_calibration_T1"] = {
                    "valid": True,
                    "finite_frac": float(result["finite_frac"]),
                    "r2_crossfit": float(result["r2_cal"]),
                }
            else:
                row["monotone_calibration_T1"] = {
                    "valid": False,
                    "finite_frac": float(finite.mean()),
                }
        diagnostics.append(row)
    sources = _data_sources(manifest, dataset_dir, models_root)
    add_source(sources, manifest_path)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "kind": "precision_preprocess_calibration",
        "study": STUDY,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "run": manifest["run"],
        "arm": manifest["arm"],
        "manifest": _source_key(manifest_path),
        "manifest_sha256": manifest["manifest_sha256"],
        "tier": {"name": "T1", "slice": [tiers.T1.start, tiers.T1.stop]},
        "settings": {
            "n_folds": 5,
            "n_bins": 64,
            "monotone": True,
            "role": "MI-SR reconstruction calibration only",
        },
        "diagnostics": diagnostics,
        "source_files": dict(sorted(sources.items())),
    }
    return _attach_digest(payload, "calibration_sha256")


def verify_calibration(path: str | Path, manifest: dict) -> dict:
    payload = verify_artifact(
        path, "precision_preprocess_calibration", "calibration_sha256")
    if payload.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise ValueError("calibration belongs to a different selection manifest")
    return payload


# ---- T2 confirmation --------------------------------------------------------

def common_mi_positions(n_rows: int, size: int = MI_SUBSET_SIZE,
                        seed: int = MI_SUBSET_SEED) -> np.ndarray:
    if n_rows < 1:
        raise ValueError("MI subset requires at least one row")
    size = min(int(size), int(n_rows))
    return np.random.default_rng(seed).choice(n_rows, size=size, replace=False)


def array_sha256(array: np.ndarray) -> str:
    canonical = np.asarray(array, dtype="<i8")
    return hashlib.sha256(canonical.tobytes(order="C")).hexdigest()


def estimate_pair_mi(
        target: np.ndarray, prediction: np.ndarray,
        estimator: Callable = mutual_information_gmm) -> dict:
    """Run unchanged post-hoc GMM-MI on already matched rows."""
    target = np.asarray(target, dtype=np.float64)
    prediction = np.asarray(prediction, dtype=np.float64)
    if target.shape != prediction.shape:
        raise ValueError("matched MI arrays have different shapes")
    finite = np.isfinite(target) & np.isfinite(prediction)
    if not finite.all():
        return {
            "valid": False,
            "n_rows": int(len(target)),
            "finite_frac": float(finite.mean()),
            "error": "non-finite prediction on the frozen matched subset",
        }
    try:
        value, error = estimator(
            target.reshape(-1, 1), prediction.reshape(-1, 1),
            return_uncertainty=True, max_samples=None, seed=MI_SUBSET_SEED,
        )
        mi = float(value[0, 0])
        sd = float(error[0, 0])
        if not np.isfinite(mi) or not np.isfinite(sd):
            raise ValueError("non-finite GMM-MI result")
        return {
            "valid": True,
            "n_rows": int(len(target)),
            "finite_frac": 1.0,
            "mi": mi,
            "mi_err": sd,
        }
    except Exception as exc:  # noqa: BLE001 - failure is a scientific result
        return {
            "valid": False,
            "n_rows": int(len(target)),
            "finite_frac": 1.0,
            "error": str(exc),
        }


def _legacy_latent(payload: dict, latent: int) -> dict:
    matches = [row for row in payload.get("latents", [])
               if int(row.get("latent", -1)) == int(latent)]
    if len(matches) != 1:
        raise ValueError(f"legacy artifact has {len(matches)} rows for z{latent}")
    return matches[0]


def load_frozen_ols_cells(path: str | Path) -> dict[str, dict]:
    """Read the displayed OLS cells from the prior frozen comparison report."""
    cells = {}
    for line in Path(path).read_text().splitlines():
        if not (line.startswith("| TT z") or line.startswith("| TT+EE z")):
            continue
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if len(columns) != 7:
            raise ValueError(f"malformed frozen comparison row: {line}")
        mi_cell = columns[1].replace(" ", "")
        if "±" not in mi_cell:
            raise ValueError(f"malformed frozen OLS MI cell: {mi_cell}")
        mi, mi_err = mi_cell.split("±", 1)
        cells[columns[0]] = {
            "mi": float(mi),
            "mi_err": float(mi_err),
            "nmse": float(columns[4]) / 100.0,
            "display": {"mi": columns[1], "nmse_percent": columns[4]},
        }
    if not cells:
        raise ValueError(f"no frozen OLS rows found in {path}")
    return cells


def frozen_ols_prediction(legacy_latent: dict, theta: np.ndarray) -> tuple[np.ndarray, dict]:
    """Evaluate stored OLS coefficients; intentionally contains no fit path."""
    block = legacy_latent.get("simple_baselines", {}).get("six_input_ols", {})
    variables = list(block.get("variables", ()))
    coefficients = np.asarray(block.get("coefs", ()), dtype=np.float64)
    if not variables or variables[-1] != "bias":
        raise ValueError("frozen OLS variables must end in bias")
    if coefficients.shape != (len(variables),):
        raise ValueError("frozen OLS coefficient/variable mismatch")
    matrix, labels = build_inputs(theta, variables[:-1])
    if labels != variables[:-1]:
        raise ValueError("frozen OLS input labels changed")
    prediction = np.column_stack([matrix, np.ones(len(matrix))]) @ coefficients
    return prediction, {
        "coefs": coefficients.tolist(),
        "variables": variables,
        "source_metrics": block.get("metrics"),
    }


def _gmm_version() -> str | None:
    for name in ("gmm-mi", "gmm_mi"):
        try:
            return importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            pass
    return None


def build_confirmation_artifact(
        manifest_path: str | Path, calibration_path: str | Path,
        dataset_dir: str | Path = "data", models_root: str | Path = "models",
        experiments_dir: str | Path = "experiments",
        baseline_report: str | Path =
        "experiments/ols_mi_sr_mse_sr_t2_comparison.md",
        mi_estimator: Callable = mutual_information_gmm) -> dict:
    """Verify frozen T0/T1 artifacts, then score once on matched T2 rows."""
    manifest = verify_selection(manifest_path)
    calibration_artifact = verify_calibration(calibration_path, manifest)
    run, arm = manifest["run"], manifest["arm"]
    legacy_path = Path(experiments_dir) / f"mse_one_stage_sr_{run}.json"
    if not legacy_path.exists():
        raise FileNotFoundError(legacy_path)
    legacy = json.loads(legacy_path.read_text())
    frozen_ols_cells = load_frozen_ols_cells(baseline_report)

    theta_t1 = _test_theta(dataset_dir, tiers.T1)
    theta_t2 = _test_theta(dataset_dir, tiers.T2)
    positions = common_mi_positions(len(theta_t2))
    subset = {
        "tier": "T2",
        "tier_slice": [tiers.T2.start, tiers.T2.stop],
        "seed": MI_SUBSET_SEED,
        "size": int(len(positions)),
        "positions_sha256": array_sha256(positions),
        "positions": positions.tolist(),
    }
    calibration_by_key = {
        (row["method"], int(row["latent"]), int(row["seed"])): row
        for row in calibration_artifact["diagnostics"]
    }
    selections_by_latent: dict[int, list[dict]] = defaultdict(list)
    for entry in manifest["selections"]:
        selections_by_latent[int(entry["latent"])].append(entry)

    latent_rows = []
    for latent in manifest["latents"]:
        target_t1 = _target_tier(models_root, run, tiers.T1, latent)
        target_t2 = _target_tier(models_root, run, tiers.T2, latent)
        legacy_row = _legacy_latent(legacy, latent)
        ols_prediction, ols_definition = frozen_ols_prediction(
            legacy_row, theta_t2)
        replay_metrics = reconstruction_metrics(target_t2, ols_prediction)
        ols_metrics = _jsonable(ols_definition.get("source_metrics") or {})
        stored_nmse = ols_metrics.get("nmse")
        if (stored_nmse is None or not ols_metrics.get("valid")):
            raise ValueError(f"z{latent}: frozen OLS metrics are missing/invalid")
        if not np.isclose(
                float(stored_nmse), float(replay_metrics["nmse"]),
                rtol=1e-11, atol=1e-13):
            raise ValueError(
                f"z{latent}: frozen OLS replay differs from stored T2 NMSE")
        ols_label = f"{MODELS.get(run, {}).get('label', run)} z{latent}"
        if ols_label not in frozen_ols_cells:
            raise ValueError(f"missing frozen OLS report cell for {ols_label}")
        frozen_cell = frozen_ols_cells[ols_label]
        # The Markdown cell is rounded to 0.001 percentage points.  Assert it
        # identifies the same stored NMSE, then preserve the JSON value exactly.
        if not np.isclose(
                float(stored_nmse), float(frozen_cell["nmse"]),
                rtol=0.0, atol=5.1e-6):
            raise ValueError(f"{ols_label}: frozen OLS report/JSON mismatch")
        ols_mi = {
            "valid": True,
            "source": "copied frozen comparison cell; estimator not rerun",
            "mi": frozen_cell["mi"],
            "mi_err": frozen_cell["mi_err"],
            "display": frozen_cell["display"],
        }

        methods: dict[str, dict[str, dict]] = defaultdict(dict)
        for entry in selections_by_latent[latent]:
            method, seed = entry["method"], int(entry["seed"])
            prediction_t1 = evaluate_selection(entry, theta_t1)
            prediction_t2 = evaluate_selection(entry, theta_t2)
            raw_t2 = reconstruction_metrics(target_t2, prediction_t2)
            gmm_mi = estimate_pair_mi(
                target_t2[positions], prediction_t2[positions], mi_estimator)
            calibrated_t2 = None
            if method == "mi20-mi":
                diagnostic = calibration_by_key.get((method, latent, seed))
                if not diagnostic or not (
                        diagnostic.get("monotone_calibration_T1") or {}).get("valid"):
                    raise ValueError(
                        f"z{latent} seed {seed}: MI calibration is not valid")
                finite_t1 = np.isfinite(target_t1) & np.isfinite(prediction_t1)
                h = calibrate.fit_h(
                    prediction_t1[finite_t1], target_t1[finite_t1],
                    n_bins=64, monotone=True)
                calibrated_prediction = np.full(len(prediction_t2), np.nan)
                finite_t2 = np.isfinite(prediction_t2)
                calibrated_prediction[finite_t2] = h(prediction_t2[finite_t2])
                calibrated_t2 = reconstruction_metrics(
                    target_t2, calibrated_prediction)
            methods[method][str(seed)] = {
                "index": int(entry["index"]),
                "complexity": int(entry["complexity"]),
                "expression": entry["expression"],
                "T0_selection": {
                    "mi_val": entry.get("mi_val"),
                    "mi_val_err": entry.get("mi_val_err"),
                    "mse_val": entry.get("mse_val"),
                    "nmse_val": entry.get("nmse_val"),
                },
                "T1_diagnostic": calibration_by_key.get((method, latent, seed)),
                "T2_raw": raw_t2,
                "T2_calibrated": calibrated_t2,
                "T2_gmm_mi_raw": gmm_mi,
            }
        latent_rows.append({
            "latent": int(latent),
            "ols": {
                "role": (
                    "frozen physical-input OLS; coefficients replayed only "
                    "as a provenance assertion; MI estimator not rerun"),
                "definition": ols_definition,
                "T2_raw": ols_metrics,
                "T2_gmm_mi_raw": ols_mi,
            },
            "methods": dict(methods),
        })

    sources = _data_sources(manifest, dataset_dir, models_root)
    for path in (manifest_path, calibration_path, legacy_path, baseline_report):
        add_source(sources, path)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "kind": "precision_preprocess_confirmation",
        "study": STUDY,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "run": run,
        "arm": arm,
        "arm_config": manifest["arm_config"],
        "manifest": _source_key(manifest_path),
        "manifest_sha256": manifest["manifest_sha256"],
        "calibration": _source_key(calibration_path),
        "calibration_sha256": calibration_artifact["calibration_sha256"],
        "tiers": {
            "T0_fit": [tiers.T0_FIT.start, tiers.T0_FIT.stop],
            "T0_val": [tiers.T0_VAL.start, tiers.T0_VAL.stop],
            "T1": [tiers.T1.start, tiers.T1.stop],
            "T2": [tiers.T2.start, tiers.T2.stop],
        },
        "matched_gmm_mi_subset": subset,
        "gmm_mi": {
            "package_version": _gmm_version(),
            "max_samples": None,
            "return_uncertainty": True,
            "scope": "SR predictions only; OLS cells copied from frozen report",
        },
        "latents": latent_rows,
        "source_files": dict(sorted(sources.items())),
    }
    return _attach_digest(payload, "confirmation_sha256")


def verify_confirmation(path: str | Path) -> dict:
    return verify_artifact(
        path, "precision_preprocess_confirmation", "confirmation_sha256")


# ---- Three-table rendering --------------------------------------------------

def _finite_float(value) -> float | None:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if np.isfinite(value) else None


def _seed_values(latent: dict, method: str,
                 getter: Callable[[dict], object]) -> list[float]:
    values = []
    for _, row in sorted(
            latent.get("methods", {}).get(method, {}).items(),
            key=lambda item: int(item[0])):
        value = _finite_float(getter(row))
        if value is not None:
            values.append(value)
    return values


def _representative(latent: dict, arm: str, method: str) -> dict | None:
    """Choose a display equation using T0 only, never T1/T2 performance."""
    candidates = []
    for seed, row in latent.get("methods", {}).get(method, {}).items():
        selected = row.get("T0_selection", {})
        metric_name = "mi_val" if method == "mi20-mi" else "mse_val"
        metric = _finite_float(selected.get(metric_name))
        if metric is None:
            continue
        direction = -metric if method == "mi20-mi" else metric
        candidates.append((
            direction, int(row["complexity"]), int(row["index"]), int(seed), row))
    if not candidates:
        return None
    _, _, _, seed, row = min(candidates, key=lambda item: item[:4])
    labels, _ = _expected_config_fields(arm)
    sampled = expression_in_sampled_basis(row["expression"], arm, labels)
    return {
        "seed": seed,
        "complexity": int(row["complexity"]),
        "expression": row["expression"],
        "sampled_expression": sampled,
        "as_tau_signature": has_as_tau_signature(sampled),
        "selection_rule": (
            "max T0 validation MI" if method == "mi20-mi"
            else "min T0 validation MSE"),
    }


def _summary(values: Iterable[float]) -> dict:
    values = sorted(float(value) for value in values if np.isfinite(value))
    if not values:
        return {"n": 0, "median": None, "min": None, "max": None}
    return {
        "n": len(values),
        "median": float(np.median(values)),
        "min": float(values[0]),
        "max": float(values[-1]),
    }


def _fmt_number(value: float | None, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{digits}f}"


def _fmt_sr(summary: dict, scale: float = 1.0, digits: int = 3) -> str:
    if not summary.get("n"):
        return "n/a"
    text = (
        f"{scale * summary['median']:.{digits}f} "
        f"[{scale * summary['min']:.{digits}f},"
        f"{scale * summary['max']:.{digits}f}]")
    if summary["n"] != len(SEEDS):
        text += f" (n={summary['n']})"
    return text


def _latent_summary(run: str, arm: str, latent: dict) -> dict:
    ols_mi = latent["ols"].get("T2_gmm_mi_raw", {})
    ols_nmse = _finite_float(latent["ols"].get("T2_raw", {}).get("nmse"))
    mi_values = _seed_values(
        latent, "mi20-mi",
        lambda row: (row.get("T2_gmm_mi_raw") or {}).get("mi")
        if (row.get("T2_gmm_mi_raw") or {}).get("valid") else None)
    mse_mi_values = _seed_values(
        latent, "mse40",
        lambda row: (row.get("T2_gmm_mi_raw") or {}).get("mi")
        if (row.get("T2_gmm_mi_raw") or {}).get("valid") else None)
    mi_nmse = _seed_values(
        latent, "mi20-mi",
        lambda row: (row.get("T2_calibrated") or {}).get("nmse")
        if (row.get("T2_calibrated") or {}).get("valid") else None)
    mse_nmse = _seed_values(
        latent, "mse40",
        lambda row: (row.get("T2_raw") or {}).get("nmse")
        if (row.get("T2_raw") or {}).get("valid") else None)
    return {
        "run": run,
        "arm": arm,
        "latent": int(latent["latent"]),
        "label": f"{MODELS.get(run, {}).get('label', run)} z{latent['latent']}",
        "ols_mi": _finite_float(ols_mi.get("mi")) if ols_mi.get("valid") else None,
        "ols_mi_err": (
            _finite_float(ols_mi.get("mi_err")) if ols_mi.get("valid") else None),
        "ols_mi_display": (
            (ols_mi.get("display") or {}).get("mi")
            if ols_mi.get("valid") else None),
        "ols_nmse": ols_nmse,
        "mi_sr_mi": _summary(mi_values),
        "mse_sr_mi": _summary(mse_mi_values),
        "mi_sr_nmse": _summary(mi_nmse),
        "mse_sr_nmse": _summary(mse_nmse),
        "representative": {
            "mi20-mi": _representative(latent, arm, "mi20-mi"),
            "mse40": _representative(latent, arm, "mse40"),
        },
    }


def _key_results(arm_summaries: dict[str, list[dict]]) -> dict:
    out = {}
    for arm, rows in arm_summaries.items():
        mi_over_ols = sum(
            row["mi_sr_mi"]["median"] is not None and
            row["ols_mi"] is not None and
            row["mi_sr_mi"]["median"] > row["ols_mi"]
            for row in rows)
        mi_over_mse = sum(
            row["mi_sr_mi"]["median"] is not None and
            row["mse_sr_mi"]["median"] is not None and
            row["mi_sr_mi"]["median"] > row["mse_sr_mi"]["median"]
            for row in rows)
        nmse_winners = defaultdict(int)
        for row in rows:
            choices = {
                "OLS": row["ols_nmse"],
                "MI-SR": row["mi_sr_nmse"]["median"],
                "MSE-SR": row["mse_sr_nmse"]["median"],
            }
            finite = {name: value for name, value in choices.items()
                      if value is not None}
            if finite:
                nmse_winners[min(finite, key=finite.get)] += 1
        signatures = {"mi20-mi": 0, "mse40": 0}
        for row in rows:
            for method in signatures:
                rep = row["representative"].get(method)
                signatures[method] += int(bool(
                    rep and rep.get("as_tau_signature")))
        out[arm] = {
            "n_latents": len(rows),
            "mi_sr_median_mi_over_ols": mi_over_ols,
            "mi_sr_median_mi_over_mse_sr": mi_over_mse,
            "median_nmse_winners": dict(nmse_winners),
            "representative_as_tau_signatures": signatures,
        }
    return out


def build_render_artifact(
        confirmation_paths: Iterable[str | Path],
        require_complete: bool = True) -> tuple[dict, str]:
    confirmations = [verify_confirmation(path) for path in confirmation_paths]
    grouped: dict[str, dict[str, dict]] = defaultdict(dict)
    sources = {}
    subset_hashes = set()
    arm_configs = {}
    for path, payload in zip(confirmation_paths, confirmations):
        arm, run = payload["arm"], payload["run"]
        if run in grouped[arm]:
            raise ValueError(f"duplicate confirmation for {arm}/{run}")
        grouped[arm][run] = payload
        config = payload.get("arm_config")
        if config is None:
            raise ValueError(f"confirmation {arm}/{run} lacks arm_config")
        previous_config = arm_configs.setdefault(arm, config)
        if previous_config != config:
            raise ValueError(f"input config changed between checkpoints for {arm}")
        add_source(sources, path)
        subset_hashes.add(
            payload["matched_gmm_mi_subset"]["positions_sha256"])
    if len(subset_hashes) != 1:
        raise ValueError("confirmations did not use one matched GMM-MI subset")
    if require_complete:
        if set(grouped) != set(ARM_IDS):
            raise ValueError(f"render requires arms {ARM_IDS}")
        for arm in ARM_IDS:
            if set(grouped[arm]) != set(MODELS):
                raise ValueError(f"render requires both checkpoints for {arm}")

    # Reuse of one OLS definition is an invariant, not a visual coincidence.
    ols_reference = {}
    for arm, runs in grouped.items():
        for run, payload in runs.items():
            for latent in payload["latents"]:
                key = (run, int(latent["latent"]))
                signature = {
                    "coefs": latent["ols"]["definition"]["coefs"],
                    "variables": latent["ols"]["definition"]["variables"],
                    "nmse": latent["ols"]["T2_raw"]["nmse"],
                }
                previous = ols_reference.setdefault(key, signature)
                if previous != signature:
                    raise ValueError(f"OLS definition changed across arms for {key}")

    arm_summaries = {}
    for arm in ARM_IDS:
        if arm not in grouped:
            continue
        rows = []
        for run in MODELS:
            payload = grouped[arm].get(run)
            if payload is None:
                continue
            for latent in sorted(payload["latents"], key=lambda row: row["latent"]):
                rows.append(_latent_summary(run, arm, latent))
        arm_summaries[arm] = rows

    payload = {
        "schema_version": SCHEMA_VERSION,
        "kind": "precision_preprocess_render",
        "study": STUDY,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "matched_gmm_mi_subset_sha256": next(iter(subset_hashes)),
        "arm_configs": arm_configs,
        "arms": arm_summaries,
        "key_results": _key_results(arm_summaries),
        "source_files": dict(sorted(sources.items())),
    }
    payload = _attach_digest(payload, "render_sha256")
    return payload, render_markdown(payload)


def render_markdown(payload: dict) -> str:
    lines = [
        "# Held-out T2 precision/preprocessing comparison",
        "",
        "## Setup and protocol",
        "",
        "This is a separate numerical-sensitivity experiment. Each arm reruns "
        "the same five-seed searches in Float64 (`precision=64`, "
        "`print_precision=17`): GMM-MI with maxsize 20 and MSE with maxsize 40. "
        "Each per-seed equation is frozen by its 1,000-row T0 validation score "
        "after fitting/searching on the other 4,000 T0 rows.",
        "",
        "MI-SR receives a 64-bin monotone calibration fitted on T1 only. On T2, "
        "raw GMM-MI uses one shared, hashed 5,000-row subset and NMSE uses all "
        "25,000 rows. MSE-SR is scored without calibration.",
        "",
        "The OLS columns are not recomputed: coefficients and native NMSE are "
        "copied from the frozen one-stage JSON (with coefficient replay used only "
        "as a provenance assertion), and displayed MI/uncertainty are copied "
        "exactly from the prior comparison report.",
        "",
        "## Preprocessing definitions",
    ]
    for arm in ARM_IDS:
        config = payload.get("arm_configs", {}).get(arm)
        if config is None:
            continue
        expressions = config.get("sampled_expressions", {})
        definition = ", ".join(
            f"`{label} = {expression}`"
            for label, expression in expressions.items())
        lines.extend(["", f"- `{arm}`: {definition}."])

    lines.extend(["", "## Key result summary"])
    for arm in ARM_IDS:
        result = payload.get("key_results", {}).get(arm)
        if result is None:
            continue
        winners = result.get("median_nmse_winners", {})
        lines.extend([
            "",
            f"- `{arm}`: median MI-SR MI exceeds frozen OLS for "
            f"{result['mi_sr_median_mi_over_ols']}/{result['n_latents']} latents "
            f"and exceeds median MSE-SR MI for "
            f"{result['mi_sr_median_mi_over_mse_sr']}/{result['n_latents']}. "
            f"Median-NMSE winners are OLS {winners.get('OLS', 0)}, MI-SR "
            f"{winners.get('MI-SR', 0)}, and MSE-SR "
            f"{winners.get('MSE-SR', 0)}.",
            f"  The exact amplitude/optical-depth differential signature "
            f"`∂f/∂tau = -2 ∂f/∂ln10As` appears in "
            f"{result['representative_as_tau_signatures']['mi20-mi']} MI-SR and "
            f"{result['representative_as_tau_signatures']['mse40']} MSE-SR "
            "representative equations.",
        ])

    lines.extend(["", "## Representative T0-selected equations"])
    for arm in ARM_IDS:
        rows = payload.get("arms", {}).get(arm)
        if rows is None:
            continue
        lines.extend(["", f"### `{arm}`"])
        for row in rows:
            pieces = []
            for method, label in (("mi20-mi", "MI-SR"), ("mse40", "MSE-SR")):
                rep = row["representative"].get(method)
                if rep is None:
                    pieces.append(f"{label}: unavailable")
                    continue
                sampled_note = ""
                if rep["sampled_expression"] != rep["expression"]:
                    sampled_note = f" → sampled `{rep['sampled_expression']}`"
                marker = (
                    "; A_s–tau signature" if rep["as_tau_signature"] else "")
                pieces.append(
                    f"{label} seed {rep['seed']}, c={rep['complexity']}: "
                    f"`{rep['expression']}`{sampled_note}{marker}")
            lines.extend(["", f"- {row['label']} — " + "; ".join(pieces) + "."])

    lines.extend([
        "",
        "## Final held-out T2 tables",
        "",
        "MI is in nats and higher is better. NMSE is "
        "`100 * MSE / Var_T2(encoder mean)` and lower is better. SR entries are "
        "median [minimum, maximum] over five frozen seeds; OLS is one frozen "
        "point estimate with its copied GMM bootstrap uncertainty.",
    ])
    for arm in ARM_IDS:
        rows = payload.get("arms", {}).get(arm)
        if rows is None:
            continue
        lines.extend([
            "",
            f"### `{arm}`",
            "",
            "| Latent | OLS MI | MI-SR MI | MSE-SR MI | OLS NMSE % | "
            "MI-SR calibrated NMSE % | MSE-SR raw NMSE % |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ])
        for row in rows:
            ols_mi = row.get("ols_mi_display")
            if ols_mi is None:
                ols_mi = (
                    f"{_fmt_number(row['ols_mi'])}±"
                    f"{_fmt_number(row['ols_mi_err'])}"
                    if row["ols_mi"] is not None else "n/a")
            lines.append(
                f"| {row['label']} | {ols_mi} "
                f"| {_fmt_sr(row['mi_sr_mi'])} "
                f"| {_fmt_sr(row['mse_sr_mi'])} "
                f"| {_fmt_number(100.0 * row['ols_nmse']) if row['ols_nmse'] is not None else 'n/a'} "
                f"| {_fmt_sr(row['mi_sr_nmse'], scale=100.0)} "
                f"| {_fmt_sr(row['mse_sr_nmse'], scale=100.0)} |")
    return "\n".join(lines) + "\n"


def write_immutable_text(path: str | Path, text: str) -> Path:
    path = Path(path)
    if path.exists():
        if path.read_text() == text:
            return path
        raise FileExistsError(f"refusing to overwrite immutable report: {path}")
    utils.save_text(text, path)
    return path


# ---- CLI -------------------------------------------------------------------

def _default_artifact(results_root: str | Path, run: str, arm: str,
                      name: str) -> Path:
    return arm_root(results_root, run, arm) / name


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    select = sub.add_parser("select", help="freeze report-only T0 selections")
    select.add_argument("--run", required=True, choices=sorted(MODELS))
    select.add_argument("--arm", required=True, choices=ARM_IDS)
    select.add_argument("--results-root", default="results")
    select.add_argument("--out", default=None)

    cal = sub.add_parser("calibrate", help="fit T1-only MI calibrations")
    cal.add_argument("--manifest", required=True)
    cal.add_argument("--dataset-dir", default="data")
    cal.add_argument("--models-root", default="models")
    cal.add_argument("--out", default=None)

    confirm = sub.add_parser("confirm", help="score frozen methods once on T2")
    confirm.add_argument("--manifest", required=True)
    confirm.add_argument("--calibration", required=True)
    confirm.add_argument("--dataset-dir", default="data")
    confirm.add_argument("--models-root", default="models")
    confirm.add_argument("--experiments-dir", default="experiments")
    confirm.add_argument(
        "--baseline-report",
        default="experiments/ols_mi_sr_mse_sr_t2_comparison.md")
    confirm.add_argument("--out", default=None)

    render = sub.add_parser("render", help="render the three final tables")
    render.add_argument("--confirmations", nargs="+", required=True)
    render.add_argument("--out-json", required=True)
    render.add_argument("--out-md", required=True)

    args = parser.parse_args()
    if args.command == "select":
        out = Path(args.out or _default_artifact(
            args.results_root, args.run, args.arm, "selection_manifest.json"))
        if out.exists():
            verify_selection(out)
            print(f"[exists] {out}")
            return
        artifact = build_selection_manifest(
            args.run, args.arm, results_root=args.results_root)
        write_immutable_json(out, artifact, "manifest_sha256")
    elif args.command == "calibrate":
        out = Path(args.out or Path(args.manifest).with_name("calibration.json"))
        if out.exists():
            verify_calibration(out, verify_selection(args.manifest))
            print(f"[exists] {out}")
            return
        artifact = build_calibration_artifact(
            args.manifest, args.dataset_dir, args.models_root)
        write_immutable_json(out, artifact, "calibration_sha256")
    elif args.command == "confirm":
        out = Path(args.out or Path(args.manifest).with_name("confirmation.json"))
        if out.exists():
            verify_confirmation(out)
            print(f"[exists] {out}")
            return
        artifact = build_confirmation_artifact(
            args.manifest, args.calibration, args.dataset_dir,
            args.models_root, args.experiments_dir, args.baseline_report)
        write_immutable_json(out, artifact, "confirmation_sha256")
    else:
        out_json, out_md = Path(args.out_json), Path(args.out_md)
        if out_json.exists() or out_md.exists():
            if not (out_json.exists() and out_md.exists()):
                raise FileExistsError("render outputs must both exist or neither")
            payload = verify_artifact(
                out_json, "precision_preprocess_render", "render_sha256")
            if out_md.read_text() != render_markdown(payload):
                raise ValueError("existing Markdown does not match render JSON")
            print(f"[exists] {out_json} and {out_md}")
            return
        artifact, markdown = build_render_artifact(args.confirmations)
        write_immutable_json(out_json, artifact, "render_sha256")
        write_immutable_text(out_md, markdown)
        print(f"[write] {out_json} and {out_md}")


if __name__ == "__main__":
    main()
