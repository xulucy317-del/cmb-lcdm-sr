#!/usr/bin/env python
"""Select and confirm the one-stage MSE symbolic-reconstruction experiment.

The command is deliberately split:

``select``
    Reads T0-only ``report.json``/``equations.csv`` artifacts, freezes one
    validation-MSE winner per run/latent/budget/seed, computes the cross-seed
    one-standard-error readout, and writes an immutable SHA256 manifest.

``calibrate``
    Verifies the selection manifest, opens T1 (never T2), computes frozen
    calibration diagnostics, and writes a separately hashed contract.

``confirm``
    Verifies both digests and every source-file hash *before* loading any data,
    then scores the frozen equations on T2 and performs the planned hierarchy,
    known-f2, and residual checks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

os.environ.setdefault("TQDM_DISABLE", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import _bootstrap  # noqa: F401,E402

import numpy as np  # noqa: E402

from cmb_lcdm_sr import calibrate, semantics, tiers, utils  # noqa: E402
from cmb_lcdm_sr.mi import mutual_information_gmm  # noqa: E402
from cmb_lcdm_sr.sr import build_inputs, rank_front  # noqa: E402

MODELS = {
    "lcdm_tt_beta3e-4": {"n_latents": 5, "amplitude": 2},
    "lcdm_tt_ee_lowl": {"n_latents": 6, "amplitude": 5},
}
DEFAULT_BUDGETS = (20, 30, 40)
DEFAULT_SEEDS = (0, 1, 2, 3, 4)
FINITE_MIN = 0.999
SCHEMA_VERSION = 1


def _json_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def object_sha256(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _finite_float(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if np.isfinite(value) else None


def _jsonable(value):
    if isinstance(value, np.ndarray):
        return [_jsonable(v) for v in value.tolist()]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def expression_of(row: dict) -> str:
    expr = row.get("expression_simplified")
    if not expr or str(expr).startswith("<sympy failed"):
        expr = row.get("expression_raw")
    if not expr:
        raise ValueError(f"equation {row.get('index')} has no usable expression")
    return str(expr)


def valid_front(report: dict, metric: str = "mse") -> list[dict]:
    """Return deterministically ranked, domain-valid report rows."""
    rows = []
    for source in report.get("all_equations", []):
        row = dict(source)
        frac_fit = _finite_float(row.get("finite_frac_fit", 1.0))
        frac_val = _finite_float(row.get("finite_frac_val", 1.0))
        if (frac_fit is None or frac_fit < FINITE_MIN
                or frac_val is None or frac_val < FINITE_MIN):
            continue
        rows.append(row)
    return rank_front(rows, metric)


def one_se_readout(fronts: dict[int, list[dict]]) -> dict:
    """Frozen cross-seed MSE envelope and common one-SE complexity."""
    if not fronts:
        raise ValueError("one-SE readout requires at least one seed front")
    metric_key = "nmse_val"
    if any(_finite_float(row.get(metric_key)) is None
           for rows in fronts.values() for row in rows):
        # Compatibility for legacy fixtures/reports predating NMSE storage.
        metric_key = "mse_val"
    complexities = sorted({
        int(row["complexity"]) for rows in fronts.values() for row in rows
        if _finite_float(row.get(metric_key)) is not None
    })
    envelope = []
    for complexity in complexities:
        seed_values = {}
        for seed, rows in sorted(fronts.items()):
            eligible = [
                row for row in rows
                if int(row["complexity"]) <= complexity
                and _finite_float(row.get(metric_key)) is not None
            ]
            if not eligible:
                break
            seed_values[seed] = float(eligible[0][metric_key])
        if len(seed_values) != len(fronts):
            continue
        vals = np.asarray(list(seed_values.values()), dtype=np.float64)
        envelope.append({
            "complexity": complexity,
            "mean": float(vals.mean()),
            "se": (float(vals.std(ddof=1) / np.sqrt(len(vals)))
                   if len(vals) > 1 else 0.0),
            "by_seed": {str(k): v for k, v in seed_values.items()},
        })
    if not envelope:
        raise ValueError("no common finite MSE envelope across seeds")
    minimum = min(envelope, key=lambda row: (row["mean"], row["complexity"]))
    threshold = minimum["mean"] + minimum["se"]
    chosen_complexity = min(
        row["complexity"] for row in envelope if row["mean"] <= threshold)
    chosen = {}
    for seed, rows in sorted(fronts.items()):
        eligible = [
            row for row in rows if int(row["complexity"]) <= chosen_complexity
        ]
        row = eligible[0]
        chosen[str(seed)] = {
            "index": int(row["index"]),
            "complexity": int(row["complexity"]),
            "mse_val": float(row["mse_val"]),
            "nmse_val": _finite_float(row.get("nmse_val")),
            "support": row.get("support"),
            "expression": expression_of(row),
        }
    return {
        "metric": metric_key,
        "c_min": int(minimum["complexity"]),
        "minimum_mean": float(minimum["mean"]),
        "minimum_se": float(minimum["se"]),
        "threshold": float(threshold),
        "complexity": int(chosen_complexity),
        "envelope": envelope,
        "by_seed": chosen,
    }


def common_complexity_readout(
        all_fronts: dict[tuple[int, int, int], list[dict]], latent: int,
        budgets: Iterable[int], seeds: Iterable[int]) -> dict:
    """Compare every budget at each distinct meaningful shared front cut."""
    budgets, seeds = tuple(map(int, budgets)), tuple(map(int, seeds))
    if not budgets:
        return {"maximum_common_complexity": None, "cuts": []}
    maximum = min(budgets)
    candidates = {maximum}
    for budget in budgets:
        for seed in seeds:
            candidates.update(
                int(row["complexity"])
                for row in all_fronts.get((latent, budget, seed), [])
                if int(row["complexity"]) <= maximum)

    cuts = []
    previous_signature = None
    for cut in sorted(candidates):
        methods = {}
        signature = []
        complete = True
        for budget in budgets:
            by_seed = {}
            for seed in seeds:
                eligible = [
                    row for row in all_fronts.get((latent, budget, seed), [])
                    if int(row["complexity"]) <= cut]
                if not eligible:
                    complete = False
                    break
                row = eligible[0]
                signature.append((budget, seed, int(row["index"])))
                by_seed[str(seed)] = {
                    "index": int(row["index"]),
                    "complexity": int(row["complexity"]),
                    "mse_val": _finite_float(row.get("mse_val")),
                    "nmse_val": _finite_float(row.get("nmse_val")),
                }
            if not complete:
                break
            metric_key = (
                "nmse_val" if all(row["nmse_val"] is not None
                                  for row in by_seed.values())
                else "mse_val")
            values = np.asarray(
                [row[metric_key] for row in by_seed.values()],
                dtype=np.float64)
            methods[f"mse{budget}"] = {
                "metric": metric_key,
                "by_seed": by_seed,
                "mean": float(values.mean()),
                "se": (float(values.std(ddof=1) / np.sqrt(len(values)))
                       if len(values) > 1 else 0.0),
            }
        if not complete:
            continue
        signature = tuple(signature)
        if signature == previous_signature and cut != maximum:
            continue
        cuts.append({"complexity_cut": int(cut), "methods": methods})
        previous_signature = signature

    out = {
        "maximum_common_complexity": int(maximum),
        "cuts": cuts,
    }
    if cuts:
        # Preserve the old endpoint fields for downstream compatibility.
        out["complexity_cut"] = cuts[-1]["complexity_cut"]
        out["methods"] = cuts[-1]["methods"]
    return out


def _source_key(path: Path) -> str:
    return str(path.resolve())


def add_source(sources: dict[str, str], path: Path, *, required=True) -> None:
    if not path.exists():
        if required:
            raise FileNotFoundError(path)
        return
    sources[_source_key(path)] = file_sha256(path)


def _git_revision() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True,
            stderr=subprocess.DEVNULL).strip()
    except Exception:  # noqa: BLE001
        return None


def _git_dirty() -> bool | None:
    """Return whether the manifest was created from a dirty worktree."""
    try:
        status = subprocess.check_output(
            ["git", "status", "--porcelain", "--untracked-files=normal"],
            text=True, stderr=subprocess.DEVNULL)
        return bool(status.strip())
    except Exception:  # noqa: BLE001
        return None


def _selection_record(method: str, run: str, latent: int, seed: int,
                      budget: int, report_path: Path, report: dict,
                      row: dict) -> dict:
    transform = report.get("target_transform") or {
        "kind": "standardize",
        "fit_rows": [0, int(report.get("n_fit", 4000))],
        "mean": report.get("y_mean_train"),
        "std": report.get("y_std_train"),
    }
    mse_standardized = _finite_float(row.get("mse_val"))
    scale = _finite_float(transform.get("std"))
    mse_native = _finite_float(row.get("mse_val_native"))
    if mse_native is None and mse_standardized is not None and scale is not None:
        mse_native = float(mse_standardized * scale**2)
    return {
        "method": method,
        "run": run,
        "latent": int(latent),
        "seed": int(seed),
        "budget": int(budget),
        "report": _source_key(report_path),
        "report_config_sha256": object_sha256(report.get("pysr_kwargs", {})),
        "index": int(row["index"]),
        "complexity": int(row["complexity"]),
        "expression": expression_of(row),
        "mse_val": mse_standardized,
        "mse_val_standardized": mse_standardized,
        "mse_val_native": mse_native,
        "nmse_val": _finite_float(row.get("nmse_val")),
        "r2_val": _finite_float(row.get("r2_val")),
        "r2_val_shuffled": _finite_float(row.get("r2_val_shuffled")),
        "r2_val_unshuffled": _finite_float(row.get("r2_val_unshuffled")),
        "mi_val": _finite_float(row.get("mi_val")),
        "finite_frac_fit": _finite_float(row.get("finite_frac_fit", 1.0)),
        "finite_frac_val": _finite_float(row.get("finite_frac_val", 1.0)),
        "support": row.get("support"),
        "target_transform": transform,
    }


def build_selection_manifest(
        run: str, results_root: str | Path = "results",
        budgets: Iterable[int] = DEFAULT_BUDGETS,
        seeds: Iterable[int] = DEFAULT_SEEDS,
        latents: Iterable[int] | None = None, include_baselines: bool = True,
        include_controls: bool = True, require_complete: bool = True) -> dict:
    """Build a T0-only selection manifest; this function never loads arrays."""
    if run not in MODELS and latents is None:
        raise ValueError(f"unknown run {run}; pass explicit latents for fixtures")
    budgets, seeds = tuple(map(int, budgets)), tuple(map(int, seeds))
    if latents is None:
        latents = range(MODELS[run]["n_latents"])
    latents = tuple(map(int, latents))
    root = Path(results_root) / run
    sources: dict[str, str] = {}
    selections = []
    one_se = {}
    all_fronts = {}
    missing = []

    for latent in latents:
        for budget in budgets:
            fronts = {}
            for seed in seeds:
                report_path = (
                    root / f"mse_one_stage_ms{budget}"
                    / f"z{latent}_seed{seed}" / "report.json")
                if not report_path.exists():
                    missing.append(str(report_path))
                    continue
                report = json.loads(report_path.read_text())
                if report.get("inner_loss") != "mse":
                    raise ValueError(f"{report_path}: inner_loss is not mse")
                if int(report.get("pysr_kwargs", {}).get("maxsize", -1)) != budget:
                    raise ValueError(f"{report_path}: stale maxsize metadata")
                front = valid_front(report, "mse")
                if not front:
                    raise ValueError(f"{report_path}: no valid MSE front member")
                fronts[seed] = front
                all_fronts[(latent, budget, seed)] = front
                selections.append(_selection_record(
                    f"mse{budget}", run, latent, seed, budget,
                    report_path, report, front[0]))
                add_source(sources, report_path)
                add_source(sources, report_path.parent / "equations.csv",
                           required=False)
            if fronts and (len(fronts) == len(seeds) or not require_complete):
                one_se[f"z{latent}:mse{budget}"] = one_se_readout(fronts)

    common_complexity = {}
    for latent in latents:
        common_complexity[f"z{latent}"] = common_complexity_readout(
            all_fronts, latent, budgets, seeds)

    baselines = []
    if include_baselines:
        for latent in latents:
            for seed in seeds:
                report_path = (
                    root / "allparams" / f"z{latent}_seed{seed}" / "report.json")
                if not report_path.exists():
                    missing.append(str(report_path))
                    continue
                report = json.loads(report_path.read_text())
                for method, metric in (("mi20-mi", "mi"), ("mi20-mse", "mse")):
                    front = valid_front(report, metric)
                    if not front:
                        raise ValueError(
                            f"{report_path}: no valid {metric} front member")
                    baselines.append(_selection_record(
                        method, run, latent, seed, 20,
                        report_path, report, front[0]))
                add_source(sources, report_path)
                add_source(sources, report_path.parent / "equations.csv",
                           required=False)

    controls = []
    if include_controls and run in MODELS:
        amp = MODELS[run]["amplitude"]
        for budget in (20, 40):
            for seed in (0, 1, 2):
                report_path = (
                    root / f"mse_one_stage_control_ms{budget}"
                    / f"z{amp}_shuffle{seed}_seed{seed}" / "report.json")
                if not report_path.exists():
                    missing.append(str(report_path))
                    continue
                report = json.loads(report_path.read_text())
                front = valid_front(report, "mse")
                if not front:
                    raise ValueError(f"{report_path}: no valid control member")
                controls.append(_selection_record(
                    f"mse{budget}-shuffled", run, amp, seed, budget,
                    report_path, report, front[0])
                    | {"shuffle_seed": int(report["shuffle_seed"])})
                add_source(sources, report_path)
                add_source(sources, report_path.parent / "equations.csv",
                           required=False)

    if missing and require_complete:
        preview = "\n".join(missing[:12])
        raise FileNotFoundError(
            f"{len(missing)} required reports are missing; first paths:\n{preview}")

    for source in (
            Path("scripts/run_blind_sr.py"),
            Path("scripts/run_shuffled_control.py"),
            Path("scripts/consolidate_mse_one_stage.py"),
            Path("src/cmb_lcdm_sr/sr.py"),
            Path("experiments/mse_one_stage_sr_plan.md"),
            Path("experiments/mse_one_stage_execution_provenance.json")):
        add_source(sources, source, required=False)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "kind": "mse_one_stage_selection",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "run": run,
        "results_root": str(Path(results_root).resolve()),
        "budgets": list(budgets),
        "seeds": list(seeds),
        "latents": list(latents),
        "finite_fraction_min": FINITE_MIN,
        "selection": "minimum T0 validation MSE; complexity then index ties",
        "git_revision": _git_revision(),
        "git_dirty": _git_dirty(),
        "selections": selections,
        "baseline_selections": baselines,
        "controls": controls,
        "one_se": one_se,
        "common_complexity": common_complexity,
        "missing": missing,
        "source_files": dict(sorted(sources.items())),
    }
    manifest["manifest_sha256"] = object_sha256(manifest)
    return manifest


def verify_hashed_payload(payload: dict, digest_key: str) -> None:
    claimed = payload.get(digest_key)
    if not claimed:
        raise ValueError(f"missing {digest_key}")
    body = dict(payload)
    body.pop(digest_key, None)
    actual = object_sha256(body)
    if actual != claimed:
        raise ValueError(
            f"{digest_key} mismatch: expected {claimed}, recomputed {actual}")


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


def verify_manifest(path: str | Path) -> dict:
    payload = json.loads(Path(path).read_text())
    if payload.get("kind") != "mse_one_stage_selection":
        raise ValueError("not an MSE one-stage selection manifest")
    verify_hashed_payload(payload, "manifest_sha256")
    verify_sources(payload.get("source_files", {}))
    return payload


def write_immutable_json(path: str | Path, payload: dict,
                         digest_key: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = json.loads(path.read_text())
        if existing.get(digest_key) == payload.get(digest_key):
            return path
        raise FileExistsError(
            f"refusing to overwrite immutable artifact with different digest: {path}")
    utils.save_json(_jsonable(payload), path)
    return path


def reconstruction_metrics(
        y: np.ndarray, prediction: np.ndarray) -> dict:
    """Native-latent reconstruction metrics on jointly finite rows."""
    y = np.asarray(y, dtype=np.float64)
    prediction = np.asarray(prediction, dtype=np.float64)
    if y.shape != prediction.shape:
        raise ValueError(
            f"metric shape mismatch: target {y.shape}, prediction {prediction.shape}")
    finite = np.isfinite(y) & np.isfinite(prediction)
    finite_frac = float(finite.mean())
    out = {"finite_frac": finite_frac, "n_finite": int(finite.sum())}
    if finite_frac < FINITE_MIN or finite.sum() < 16:
        return out | {"valid": False}
    yt, yp = y[finite], prediction[finite]
    err = yt - yp
    mse = float(np.mean(err**2))
    variance = float(np.var(yt))
    abs_err = np.abs(err)
    out.update({
        "valid": True,
        "mse": mse,
        "rmse": float(np.sqrt(mse)),
        "nmse": float(mse / variance) if variance > 0 else None,
        "r2": float(1.0 - mse / variance) if variance > 0 else None,
        "mae": float(abs_err.mean()),
        "abs_error_p95": float(np.quantile(abs_err, 0.95)),
        "abs_error_p99": float(np.quantile(abs_err, 0.99)),
    })
    return out


def decision_domain_status(t1_metrics: dict, t2_metrics: dict) -> dict:
    """Eligibility of a frozen winner; later tiers never trigger fallback."""
    tier_valid = {
        "T1": bool(t1_metrics.get("valid")
                   and _finite_float(t1_metrics.get("finite_frac")) is not None
                   and float(t1_metrics["finite_frac"]) >= FINITE_MIN),
        "T2": bool(t2_metrics.get("valid")
                   and _finite_float(t2_metrics.get("finite_frac")) is not None
                   and float(t2_metrics["finite_frac"]) >= FINITE_MIN),
    }
    invalid_tiers = [tier for tier, valid in tier_valid.items() if not valid]
    return {
        "eligible": not invalid_tiers,
        "tier_valid": tier_valid,
        "invalid_tiers": invalid_tiers,
        "reason": (None if not invalid_tiers else
                   "frozen winner failed finite-prediction domain check on "
                   + ", ".join(invalid_tiers)),
        "fallback_used": False,
    }


def _eligible_t2_mse(row: dict | None) -> float | None:
    if not row or not (row.get("decision_domain") or {}).get("eligible"):
        return None
    metrics = row.get("T2") or {}
    if not metrics.get("valid"):
        return None
    return _finite_float(metrics.get("mse"))


def evaluate_selection(entry: dict, theta: np.ndarray,
                       target: np.ndarray) -> tuple[np.ndarray, dict]:
    """Evaluate a frozen standardized expression and invert its transform."""
    standardized = semantics.evaluate_on_theta(entry["expression"], theta)
    transform = entry["target_transform"]
    if transform.get("kind") != "standardize":
        raise ValueError(f"unsupported target transform {transform}")
    mean = float(transform["mean"])
    std = float(transform["std"])
    prediction = mean + std * standardized
    return prediction, reconstruction_metrics(target, prediction)


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


def calibration_source_paths(
        manifest: dict, dataset_dir: str | Path = "data",
        models_root: str | Path = "models",
        experiments_dir: str | Path = "experiments") -> list[Path]:
    run = manifest["run"]
    paths = [
        Path(dataset_dir) / "theta.npy",
        Path(dataset_dir) / "splits_v1.npz",
        Path(models_root) / run / "analysis" / "encoder_means_test.npy",
        Path(experiments_dir) / f"residual_sr_{run}.json",
        Path(experiments_dir) / f"residual_sr_ia_{run}.json",
        Path(experiments_dir) / f"latent_cards_{run}.json",
        Path("src/cmb_lcdm_sr/calibrate.py"),
        Path("src/cmb_lcdm_sr/semantics.py"),
        Path("scripts/consolidate_mse_one_stage.py"),
    ]
    for latent in manifest["latents"]:
        paths.extend([
            Path(models_root) / run / "analysis" / f"residual_z{latent}_v1.npy",
            Path(models_root) / run / "analysis" / f"f1hat_z{latent}_v1.npy",
        ])
    return paths


def build_calibration_artifact(
        manifest_path: str | Path, dataset_dir: str | Path = "data",
        models_root: str | Path = "models",
        experiments_dir: str | Path = "experiments") -> dict:
    """Verify selection, then compute diagnostics using T1 and only T1."""
    manifest = verify_manifest(manifest_path)
    theta_t1 = _test_theta(dataset_dir, tiers.T1)
    diagnostics = []
    all_entries = manifest["selections"] + manifest["baseline_selections"]
    for entry in all_entries:
        target = _target_tier(
            models_root, manifest["run"], tiers.T1, entry["latent"])
        prediction, raw = evaluate_selection(entry, theta_t1, target)
        finite = np.isfinite(prediction) & np.isfinite(target)
        calibrated = {"valid": False, "finite_frac": float(finite.mean())}
        if finite.mean() >= FINITE_MIN:
            cal = calibrate.crossfit_calibration(
                prediction, target, n_folds=5, n_bins=64,
                monotone=True, seed=entry["seed"])
            calibrated = {
                "valid": True,
                "finite_frac": float(cal["finite_frac"]),
                "r2_crossfit": _finite_float(cal["r2_cal"]),
            }
        diagnostics.append({
            "method": entry["method"],
            "latent": entry["latent"],
            "seed": entry["seed"],
            "raw_T1": raw,
            "monotone_calibration_T1": calibrated,
        })

    sources = {}
    add_source(sources, Path(manifest_path))
    for path in calibration_source_paths(
            manifest, dataset_dir, models_root, experiments_dir):
        add_source(sources, path)
    artifact = {
        "schema_version": SCHEMA_VERSION,
        "kind": "mse_one_stage_calibration",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "run": manifest["run"],
        "manifest": _source_key(Path(manifest_path)),
        "manifest_sha256": manifest["manifest_sha256"],
        "tier": {"name": "T1", "slice": [tiers.T1.start, tiers.T1.stop]},
        "settings": {
            "n_folds": 5,
            "n_bins": 64,
            "monotone": True,
        },
        "diagnostics": diagnostics,
        "source_files": dict(sorted(sources.items())),
    }
    artifact["calibration_sha256"] = object_sha256(artifact)
    return artifact


def verify_calibration(path: str | Path, manifest: dict) -> dict:
    payload = json.loads(Path(path).read_text())
    if payload.get("kind") != "mse_one_stage_calibration":
        raise ValueError("not an MSE one-stage calibration artifact")
    verify_hashed_payload(payload, "calibration_sha256")
    if payload.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise ValueError("calibration artifact belongs to a different manifest")
    verify_sources(payload.get("source_files", {}))
    return payload


def _evaluate_with_f1hat(expr: str, theta: np.ndarray,
                         f1hat: np.ndarray) -> np.ndarray:
    semantics.clear_extra_inputs()
    semantics.register_extra_input(
        "f1hat", lambda _theta: np.asarray(f1hat, dtype=np.float64))
    try:
        return semantics.evaluate_on_theta(expr, theta)
    finally:
        semantics.clear_extra_inputs()


def _hierarchy_prediction(
        f2_expr: str, theta_t1: np.ndarray, theta_t2: np.ndarray,
        f1hat_t1: np.ndarray, f1hat_t2: np.ndarray,
        e1_t1: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if "f1hat" in f2_expr:
        f2_t1 = _evaluate_with_f1hat(f2_expr, theta_t1, f1hat_t1)
        f2_t2 = _evaluate_with_f1hat(f2_expr, theta_t2, f1hat_t2)
    else:
        f2_t1 = semantics.evaluate_on_theta(f2_expr, theta_t1)
        f2_t2 = semantics.evaluate_on_theta(f2_expr, theta_t2)
    finite = np.isfinite(f2_t1) & np.isfinite(e1_t1)
    if finite.mean() < FINITE_MIN:
        return (np.full(len(theta_t2), np.nan), f2_t1, f2_t2)
    g = calibrate.fit_h(
        f2_t1[finite], e1_t1[finite], n_bins=64, monotone=True)
    correction = np.full(len(theta_t2), np.nan)
    finite_t2 = np.isfinite(f2_t2)
    correction[finite_t2] = g(f2_t2[finite_t2])
    return f1hat_t2 + correction, f2_t1, f2_t2


def canonical_known_f2(hierarchy_f2: dict) -> tuple | None:
    """The frozen additive residual coordinate, never the IA follow-up."""
    return hierarchy_f2.get("additive")


def _mi_scalar(a: np.ndarray, b: np.ndarray, seed: int,
               max_samples: int | None) -> tuple[float | None, float | None]:
    finite = np.isfinite(a) & np.isfinite(b)
    if finite.mean() < FINITE_MIN or finite.sum() < 256:
        return None, None
    value, error = mutual_information_gmm(
        a[finite].reshape(-1, 1), b[finite].reshape(-1, 1),
        return_uncertainty=True, max_samples=max_samples, seed=seed)
    return _finite_float(value[0, 0]), _finite_float(error[0, 0])


def _perm_scalar_mi_call(args) -> float | None:
    """Picklable worker for the one-dimensional f2 permutation null."""
    residual, f2, seed, max_samples = args
    value, _ = _mi_scalar(residual, f2, seed, max_samples)
    return value


def f2_incremental_audit(
        residual_t1: np.ndarray, residual_t2: np.ndarray,
        f2_t1: np.ndarray, f2_t2: np.ndarray, seed: int,
        n_perm_mi: int = 39, max_samples_mi: int | None = 5000,
        compute_mi: bool = True, mi_jobs: int = 1) -> dict:
    finite_t1 = np.isfinite(residual_t1) & np.isfinite(f2_t1)
    finite_t2 = np.isfinite(residual_t2) & np.isfinite(f2_t2)
    out = {
        "eligible": True,
        "status": None,
        "reason": None,
        "finite_frac_T1": float(finite_t1.mean()),
        "finite_frac_T2": float(finite_t2.mean()),
        "r2_f2": None,
        "mi": None,
        "mi_err": None,
        "mi_null_p975": None,
        "mi_null": [],
        "pass_mi": None,
        "mi_permutation_seeds": [],
        "T1_crossfit_r2_f2": None,
    }
    if finite_t1.mean() < FINITE_MIN or finite_t2.mean() < FINITE_MIN:
        out["eligible"] = False
        out["status"] = "invalid"
        out["reason"] = "known f2 or direct residual failed a tier domain check"
        out["absorbed"] = False
        return out
    f2_t1_finite = f2_t1[finite_t1]
    residual_t1_finite = residual_t1[finite_t1]
    crossfit = calibrate.crossfit_calibration(
        f2_t1_finite, residual_t1_finite, n_folds=5, n_bins=64,
        monotone=True, seed=seed)
    out["T1_crossfit_r2_f2"] = _finite_float(crossfit["r2_cal"])
    q = calibrate.fit_h(
        f2_t1_finite, residual_t1_finite,
        n_bins=64, monotone=True)
    e2 = residual_t2[finite_t2]
    correction = q(f2_t2[finite_t2])
    sst = float(np.sum((e2 - e2.mean()) ** 2))
    sse = float(np.sum((e2 - correction) ** 2))
    out["r2_f2"] = float(1.0 - sse / sst) if sst > 0 else None
    if compute_mi:
        mi, err = _mi_scalar(
            residual_t2, f2_t2, seed=seed,
            max_samples=max_samples_mi)
        out["mi"], out["mi_err"] = mi, err
        permutation_seeds = [seed + 1 + p for p in range(n_perm_mi)]
        residual_finite = residual_t2[finite_t2]
        f2_finite = f2_t2[finite_t2]
        tasks = [
            (np.random.default_rng(permutation_seed).permutation(
                residual_finite), f2_finite, permutation_seed, max_samples_mi)
            for permutation_seed in permutation_seeds]
        if mi_jobs > 1 and tasks:
            from concurrent.futures import ProcessPoolExecutor

            with ProcessPoolExecutor(max_workers=mi_jobs) as executor:
                values = list(executor.map(_perm_scalar_mi_call, tasks))
        else:
            values = [_perm_scalar_mi_call(task) for task in tasks]
        null = [value for value in values if value is not None]
        out["mi_null"] = null
        out["mi_permutation_seeds"] = permutation_seeds
        out["mi_null_p975"] = (
            float(np.quantile(null, 0.975)) if null else None)
    mi_complete = bool(
        compute_mi and n_perm_mi > 0
        and out["mi"] is not None and out["mi_null_p975"] is not None
        and len(out["mi_null"]) == n_perm_mi)
    if not mi_complete:
        out["absorbed"] = None
        out["status"] = "indeterminate"
        out["reason"] = (
            "MI audit disabled" if not compute_mi else
            "observed or permutation-null MI is incomplete")
        return out
    if out["r2_f2"] is None:
        out["absorbed"] = None
        out["status"] = "indeterminate"
        out["reason"] = "R2_f2 is undefined"
        return out
    out["pass_mi"] = bool(out["mi"] <= out["mi_null_p975"])
    out["absorbed"] = bool(
        out["r2_f2"] <= 0.05 and out["pass_mi"])
    out["status"] = "pass" if out["absorbed"] else "fail"
    return out


def unavailable_seed_audit(
        outcome_key: str, status: str, reason: str,
        decision_domain: dict | None = None) -> dict:
    """Record a failed/indeterminate seed without substituting an equation."""
    if status not in {"invalid", "indeterminate"}:
        raise ValueError(f"unsupported unavailable audit status {status}")
    return {
        "eligible": False,
        "status": status,
        "reason": reason,
        outcome_key: False if status == "invalid" else None,
        "decision_domain": decision_domain,
    }


def audit_decision(rows: dict[str, dict], outcome_key: str,
                   expected_n: int = 5) -> dict:
    """Aggregate a 4/5 audit while preserving invalid/unknown seed states."""
    n_pass = sum(row.get(outcome_key) is True for row in rows.values())
    n_invalid = sum(row.get("status") == "invalid" for row in rows.values())
    n_indeterminate = sum(
        row.get("status") == "indeterminate"
        or row.get(outcome_key) is None for row in rows.values())
    complete = len(rows) == expected_n
    if not complete or n_indeterminate:
        status, passes = "indeterminate", False
    else:
        passes = n_pass >= 4
        status = "pass" if passes else "fail"
    return {
        "n_pass": int(n_pass),
        "n": len(rows),
        "n_invalid": int(n_invalid),
        "n_indeterminate": int(n_indeterminate),
        "status": status,
        "pass": bool(passes),
    }


def direct_recurrence(entries: list[dict], dataset_dir: str | Path) -> dict:
    anchors = tiers.anchor_theta(dataset_dir)
    _mid, half = tiers.load_prior_box(dataset_dir)
    forms = []
    for entry in sorted(entries, key=lambda item: item["seed"]):
        form = semantics.evaluate_form(
            entry["expression"], anchors, half,
            complexity=entry["complexity"], meta={"seed": entry["seed"]})
        if form is not None and form.finite_frac >= FINITE_MIN:
            forms.append(form)
    if not forms:
        return {"r_sr": 0.0, "stable": False, "n_forms": 0}
    labels = semantics.cluster_forms(forms)
    counts = Counter(labels)
    winner = min(
        (label for label, count in counts.items()
         if count == max(counts.values())))
    members = [form for form, label in zip(forms, labels) if label == winner]
    representative = min(
        members, key=lambda form: (
            form.complexity if form.complexity is not None else 10**9,
            form.meta["seed"]))
    r_sr = len({form.meta["seed"] for form in members}) / len(entries)
    return {
        "r_sr": float(r_sr),
        "stable": bool(r_sr >= 0.8),
        "n_forms": len(forms),
        "n_clusters": len(counts),
        "cluster_sizes": dict(sorted(
            (str(label), count) for label, count in counts.items())),
        "representative": representative.expr_str,
        "representative_complexity": representative.complexity,
        "support": representative.support,
        "seeds": sorted(form.meta["seed"] for form in members),
    }


def one_sided_upper(values: list[float]) -> float | None:
    vals = np.asarray([v for v in values if np.isfinite(v)], dtype=np.float64)
    if len(vals) == 0:
        return None
    if len(vals) == 1:
        return float(vals[0])
    return float(vals.mean() + 2.132 * vals.std(ddof=1) / np.sqrt(len(vals)))


def _paired_ratio_rule(values: list[float], margin: float,
                       *, inclusive: bool = True) -> dict:
    upper = one_sided_upper(values)
    passes = [v <= margin if inclusive else v < margin for v in values]
    upper_passes = (
        (upper <= margin if inclusive else upper < margin)
        if upper is not None else False)
    return {
        "ratios": [float(v) for v in values],
        "n_below_margin": int(sum(passes)),
        "margin": float(margin),
        "inclusive": bool(inclusive),
        "u95": upper,
        "pass": bool(
            len(values) == 5
            and sum(passes) >= 4
            and upper is not None and upper_passes),
    }


def paired_ratio_readout(values_by_seed: dict[str, float | None],
                         margin: float, *, inclusive: bool = True) -> dict:
    values = [float(value) for value in values_by_seed.values()
              if _finite_float(value) is not None]
    out = _paired_ratio_rule(values, margin, inclusive=inclusive)
    invalid = [seed for seed, value in values_by_seed.items()
               if _finite_float(value) is None]
    out.update({
        "by_seed": {
            str(seed): _finite_float(value)
            for seed, value in values_by_seed.items()},
        "invalid_seeds": invalid,
        "status": ("invalid" if invalid else
                   "pass" if out["pass"] else "fail"),
    })
    return out


def classify_outcome(capacity: dict, absorption: dict,
                     reconstruction: dict) -> str:
    """Classify only identified outcomes; unavailable evidence stays unknown."""
    if capacity.get("status") == "fail":
        return "no capacity gain"
    if capacity.get("status") != "pass":
        return "indeterminate"
    if (absorption.get("status") == "pass"
            and reconstruction.get("status") == "pass"):
        return "one-stage replacement"
    if (absorption.get("status") == "fail"
            or reconstruction.get("status") == "fail"):
        return "partial absorption"
    return "indeterminate"


def _latent_from_hierarchy(payload: dict, latent: int) -> dict | None:
    return next(
        (row for row in payload.get("latents", [])
         if int(row.get("latent", -1)) == latent),
        None)


def _controls_on_t2(manifest: dict, theta_t2: np.ndarray,
                    target_by_latent: dict[int, np.ndarray]) -> list[dict]:
    out = []
    for entry in manifest.get("controls", []):
        target = target_by_latent[entry["latent"]]
        prediction, true_metrics = evaluate_selection(entry, theta_t2, target)
        shuffled = np.random.default_rng(
            entry["shuffle_seed"]).permutation(target)
        out.append({
            "method": entry["method"],
            "latent": entry["latent"],
            "seed": entry["seed"],
            "shuffle_seed": entry["shuffle_seed"],
            "expression": entry["expression"],
            "T0_validation": {
                "r2_vs_shuffled": entry.get("r2_val_shuffled"),
                "r2_vs_true": entry.get("r2_val_unshuffled"),
            },
            "T2_true": true_metrics,
            "T2_independently_shuffled": reconstruction_metrics(
                shuffled, prediction),
        })
    return out


def confirm_experiment(
        manifest_path: str | Path, calibration_path: str | Path,
        dataset_dir: str | Path = "data", models_root: str | Path = "models",
        experiments_dir: str | Path = "experiments",
        n_perm_mi: int = 39,
        max_samples_mi: int | None = 5000, mi_jobs: int = 1,
        compute_known_f2_mi: bool = True) -> dict:
    """Verify frozen artifacts first, then open T2 exactly once."""
    # These two calls must remain before every np.load/data helper below.
    manifest = verify_manifest(manifest_path)
    calibration_artifact = verify_calibration(calibration_path, manifest)

    run = manifest["run"]
    run_dir = Path(models_root) / run
    theta_t0_fit = _test_theta(dataset_dir, tiers.T0_FIT)
    theta_t1 = _test_theta(dataset_dir, tiers.T1)
    theta_t2 = _test_theta(dataset_dir, tiers.T2)
    means = np.load(
        run_dir / "analysis" / "encoder_means_test.npy", mmap_mode="r")
    targets_t0 = {
        latent: np.asarray(means[tiers.T0_FIT, latent], dtype=np.float64)
        for latent in manifest["latents"]}
    targets_t1 = {
        latent: np.asarray(means[tiers.T1, latent], dtype=np.float64)
        for latent in manifest["latents"]}
    targets_t2 = {
        latent: np.asarray(means[tiers.T2, latent], dtype=np.float64)
        for latent in manifest["latents"]}

    additive_payload = json.loads(
        (Path(experiments_dir) / f"residual_sr_{run}.json").read_text())
    ia_payload = json.loads(
        (Path(experiments_dir) / f"residual_sr_ia_{run}.json").read_text())
    cards_payload = json.loads(
        (Path(experiments_dir) / f"latent_cards_{run}.json").read_text())
    cards_by_latent = {
        int(row["latent"]): row for row in cards_payload.get("cards", [])}

    by_latent = defaultdict(list)
    for entry in manifest["selections"] + manifest["baseline_selections"]:
        by_latent[int(entry["latent"])].append(entry)

    calibration_by_key = {
        (row["method"], int(row["latent"]), int(row["seed"])): row
        for row in calibration_artifact.get("diagnostics", [])
    }
    latent_rows = []
    for latent in manifest["latents"]:
        target_t0 = targets_t0[latent]
        target_t1 = targets_t1[latent]
        target_t2 = targets_t2[latent]
        method_results = defaultdict(dict)
        predictions_t1 = {}
        predictions_t2 = {}

        for entry in by_latent[latent]:
            pred_t1, metrics_t1 = evaluate_selection(
                entry, theta_t1, target_t1)
            pred_t2, _ = evaluate_selection(entry, theta_t2, target_t2)
            key = (entry["method"], entry["seed"])
            predictions_t1[key] = pred_t1
            predictions_t2[key] = pred_t2
            metrics = reconstruction_metrics(target_t2, pred_t2)
            domain = decision_domain_status(metrics_t1, metrics)

            # Common-form T1 monotone calibration is diagnostic only.
            finite_t1 = np.isfinite(pred_t1) & np.isfinite(target_t1)
            calibrated_t2 = None
            if finite_t1.mean() >= FINITE_MIN:
                h = calibrate.fit_h(
                    pred_t1[finite_t1], target_t1[finite_t1],
                    n_bins=64, monotone=True)
                cal_pred = np.full(len(pred_t2), np.nan)
                finite_t2 = np.isfinite(pred_t2)
                cal_pred[finite_t2] = h(pred_t2[finite_t2])
                calibrated_t2 = reconstruction_metrics(target_t2, cal_pred)

            method_results[entry["method"]][str(entry["seed"])] = {
                "index": entry["index"],
                "complexity": entry["complexity"],
                "expression": entry["expression"],
                "T0_validation_mse": entry["mse_val_native"],
                "T0_validation_mse_native": entry["mse_val_native"],
                "T0_validation_mse_standardized": entry["mse_val"],
                "T0_validation_mi": entry["mi_val"],
                "T1_calibration": calibration_by_key.get(
                    (entry["method"], latent, entry["seed"])),
                "T1": metrics_t1,
                "T2": metrics,
                "decision_domain": domain,
                "T2_after_T1_monotone_calibration_diagnostic": calibrated_t2,
            }

        # The one-SE equations are frozen secondary selections. Confirm them
        # on the same tiers, but never feed them into success decisions.
        primary_entries = {
            (entry["method"], str(entry["seed"])): entry
            for entry in by_latent[latent]}
        one_se_confirmed = {}
        for budget in manifest.get("budgets", DEFAULT_BUDGETS):
            method = f"mse{int(budget)}"
            readout = manifest.get("one_se", {}).get(
                f"z{latent}:{method}")
            if readout is None:
                continue
            confirmed_by_seed = {}
            for seed, choice in sorted(
                    readout.get("by_seed", {}).items(),
                    key=lambda item: int(item[0])):
                base = primary_entries.get((method, str(seed)))
                if base is None:
                    continue
                selected = dict(base)
                selected.update({
                    "index": choice["index"],
                    "complexity": choice["complexity"],
                    "expression": choice["expression"],
                    "mse_val": choice.get("mse_val"),
                    "nmse_val": choice.get("nmse_val"),
                    "support": choice.get("support"),
                })
                pred_t1, metrics_t1 = evaluate_selection(
                    selected, theta_t1, target_t1)
                pred_t2, _ = evaluate_selection(
                    selected, theta_t2, target_t2)
                metrics_t2 = reconstruction_metrics(target_t2, pred_t2)
                transform_std = _finite_float(
                    selected["target_transform"].get("std"))
                mse_native = (
                    float(choice["mse_val"]) * transform_std**2
                    if _finite_float(choice.get("mse_val")) is not None
                    and transform_std is not None else None)
                confirmed_by_seed[str(seed)] = {
                    "selection_role": "secondary_one_se",
                    "index": int(choice["index"]),
                    "complexity": int(choice["complexity"]),
                    "expression": choice["expression"],
                    "support": choice.get("support"),
                    "T0_validation_mse_native": mse_native,
                    "T0_validation_mse_standardized": choice.get("mse_val"),
                    "T0_validation_nmse": choice.get("nmse_val"),
                    "T1": metrics_t1,
                    "T2": metrics_t2,
                    "decision_domain": decision_domain_status(
                        metrics_t1, metrics_t2),
                    "used_for_success_decisions": False,
                }
            one_se_confirmed[method] = confirmed_by_seed

        # Fit-only mean and six-input OLS baselines.
        X0, labels = build_inputs(
            theta_t0_fit,
            ["omega_b", "omega_cdm", "H0", "tau", "A_s", "n_s"])
        X2, _ = build_inputs(
            theta_t2,
            ["omega_b", "omega_cdm", "H0", "tau", "A_s", "n_s"])
        mean_prediction = np.full(len(target_t2), float(target_t0.mean()))
        beta, *_ = np.linalg.lstsq(
            np.column_stack([X0, np.ones(len(X0))]), target_t0, rcond=None)
        ols_prediction = np.column_stack([X2, np.ones(len(X2))]) @ beta
        simple_baselines = {
            "fit_mean": reconstruction_metrics(target_t2, mean_prediction),
            "six_input_ols": {
                "metrics": reconstruction_metrics(target_t2, ols_prediction),
                "coefs": beta.tolist(),
                "variables": labels + ["bias"],
            },
        }

        # Recompute the frozen stage-1/additive/interaction-aware hierarchy on T2.
        e1_all = np.load(
            run_dir / "analysis" / f"residual_z{latent}_v1.npy",
            mmap_mode="r")
        e1_t1 = np.asarray(e1_all[tiers.T1], dtype=np.float64)
        e1_t2 = np.asarray(e1_all[tiers.T2], dtype=np.float64)
        f1hat_t1 = target_t1 - e1_t1
        f1hat_t2 = target_t2 - e1_t2
        f1_info = (cards_by_latent.get(latent, {}).get("f1") or {})
        f1_complexity = f1_info.get("complexity")
        hierarchy = {
            "h_f1": {
                "expression_f1": f1_info.get("expr"),
                "f1_complexity": f1_complexity,
                "symbolic_core_lower_bound": f1_complexity,
                "non_symbolic_calibrators": ["h"],
                "T2": reconstruction_metrics(target_t2, f1hat_t2),
            },
            "additive": None,
            "interaction_aware": None,
        }
        hierarchy_predictions = {}
        hierarchy_f2 = {}
        for name, source_payload in (
                ("additive", additive_payload),
                ("interaction_aware", ia_payload)):
            source = _latent_from_hierarchy(source_payload, latent)
            f2_info = (source or {}).get("f2") or {}
            f2_expr = f2_info.get("expr")
            if not f2_expr:
                continue
            prediction, f2_t1, f2_t2 = _hierarchy_prediction(
                f2_expr, theta_t1, theta_t2,
                f1hat_t1, f1hat_t2, e1_t1)
            hierarchy_predictions[name] = prediction
            hierarchy_f2[name] = (f2_expr, f2_t1, f2_t2)
            f2_complexity = f2_info.get("complexity")
            core_complexity = (
                int(f1_complexity) + int(f2_complexity) + 1
                if f1_complexity is not None and f2_complexity is not None
                else None)
            hierarchy[name] = {
                "expression_f1": f1_info.get("expr"),
                "expression_f2": f2_expr,
                "f1_complexity": f1_complexity,
                "f2_complexity": f2_complexity,
                "symbolic_core_lower_bound": core_complexity,
                "non_symbolic_calibrators": ["h", "g"],
                "stored_T1_combined_r2": (
                    (source.get("hierarchy") or {}).get("combined_r2_vs_mu")),
                "T2": reconstruction_metrics(target_t2, prediction),
            }

        primary_hierarchy = hierarchy.get("interaction_aware")
        known_f2 = canonical_known_f2(hierarchy_f2)

        absorption = {}
        mse40_entries = sorted(
            (entry for entry in by_latent[latent]
             if entry["method"] == "mse40"),
            key=lambda entry: entry["seed"])
        for entry in mse40_entries:
            seed = entry["seed"]
            key = ("mse40", seed)
            residual_t1 = target_t1 - predictions_t1[key]
            residual_t2 = target_t2 - predictions_t2[key]
            direct_row = method_results["mse40"][str(seed)]
            domain = direct_row["decision_domain"]
            if not domain["eligible"]:
                absorption[str(seed)] = unavailable_seed_audit(
                    "absorbed", "invalid", domain["reason"], domain)
                continue
            if known_f2 is None:
                absorption[str(seed)] = unavailable_seed_audit(
                    "absorbed", "indeterminate",
                    "canonical additive f2 is unavailable", domain)
            else:
                f2_expr, f2_t1, f2_t2 = known_f2
                absorption[str(seed)] = f2_incremental_audit(
                    residual_t1, residual_t2, f2_t1, f2_t2,
                    seed=3000 + 100 * latent + seed,
                    n_perm_mi=n_perm_mi,
                    max_samples_mi=max_samples_mi,
                    compute_mi=compute_known_f2_mi, mi_jobs=mi_jobs) | {
                        "f2_source": "canonical_additive",
                        "f2_expression": f2_expr,
                    }

        recurrence = direct_recurrence(mse40_entries, dataset_dir)

        def mse(method: str, seed: int) -> float | None:
            row = method_results.get(method, {}).get(str(seed))
            return _eligible_t2_mse(row)

        seed_ids = tuple(map(int, manifest.get("seeds", DEFAULT_SEEDS)))
        q_obj, q_cap, q_rec = {}, {}, {}
        hierarchy_metrics = ((primary_hierarchy or {}).get("T2") or {})
        hierarchy_mse = (
            _finite_float(hierarchy_metrics.get("mse"))
            if hierarchy_metrics.get("valid") else None)
        for seed in seed_ids:
            a, b = mse("mse20", seed), mse("mi20-mse", seed)
            q_obj[str(seed)] = (
                a / b if a is not None and b not in (None, 0) else None)
            a, b = mse("mse40", seed), mse("mse20", seed)
            q_cap[str(seed)] = (
                a / b if a is not None and b not in (None, 0) else None)
            a = mse("mse40", seed)
            q_rec[str(seed)] = (
                a / hierarchy_mse
                if a is not None and hierarchy_mse not in (None, 0) else None)
        objective_rule = paired_ratio_readout(
            q_obj, 1.0, inclusive=False)
        capacity_rule = paired_ratio_readout(
            q_cap, 1.0, inclusive=False)
        reconstruction_rule = paired_ratio_readout(q_rec, 1.10)
        reconstruction_rule["pairing"] = "unpaired_fixed_canonical_hierarchy"
        saturated_count = sum(
            int(entry["complexity"]) >= 38 for entry in mse40_entries)
        decisions = {
            "mse_objective_helps": objective_rule,
            "capacity_helps": capacity_rule,
            "one_stage_matches_interaction_aware": reconstruction_rule,
            "known_f2_absorbed": audit_decision(
                absorption, "absorbed"),
            "symbolically_stable": {
                "r_sr": recurrence["r_sr"],
                "pass": recurrence["stable"],
            },
            "budget_saturated": {
                "n_at_or_above_38": int(saturated_count),
                "n": len(mse40_entries),
                "saturated": bool(
                    len(mse40_entries) == 5 and saturated_count >= 3),
            },
        }
        classification = classify_outcome(
            capacity_rule, decisions["known_f2_absorbed"],
            reconstruction_rule)
        flags = []
        if recurrence["stable"]:
            flags.append("symbolically-stable")

        one_se = {}
        for budget in manifest.get("budgets", DEFAULT_BUDGETS):
            method = f"mse{int(budget)}"
            readout = manifest.get("one_se", {}).get(
                f"z{latent}:{method}")
            if readout is not None:
                one_se[method] = readout | {
                    "confirmed_by_seed": one_se_confirmed.get(method, {})}

        latent_rows.append({
            "latent": latent,
            "methods": dict(method_results),
            "simple_baselines": simple_baselines,
            "hierarchy": hierarchy,
            "known_f2_definition": {
                "source": "canonical_additive",
                "artifact": _source_key(
                    Path(experiments_dir) / f"residual_sr_{run}.json"),
                "expression": known_f2[0] if known_f2 is not None else None,
            },
            "known_f2_absorption": absorption,
            "direct_recurrence": recurrence,
            "T0_one_se": one_se,
            "T0_common_complexity": manifest.get(
                "common_complexity", {}).get(f"z{latent}"),
            "decisions": decisions,
            "classification": classification,
            "flags": flags,
        })

    controls = _controls_on_t2(manifest, theta_t2, targets_t2)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "kind": "mse_one_stage_confirmation",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "run": run,
        "manifest": _source_key(Path(manifest_path)),
        "manifest_sha256": manifest["manifest_sha256"],
        "calibration": _source_key(Path(calibration_path)),
        "calibration_sha256": calibration_artifact["calibration_sha256"],
        "tiers": {
            "T0_fit": [tiers.T0_FIT.start, tiers.T0_FIT.stop],
            "T1": [tiers.T1.start, tiers.T1.stop],
            "T2": [tiers.T2.start, tiers.T2.stop],
        },
        "settings": {
            "finite_fraction_min": FINITE_MIN,
            "n_perm_mi": n_perm_mi,
            "max_samples_mi": max_samples_mi,
            "mi_jobs": mi_jobs,
            "compute_known_f2_mi": compute_known_f2_mi,
        },
        "latents": latent_rows,
        "controls": controls,
        "generated_by": "scripts/consolidate_mse_one_stage.py confirm",
    }
    payload["confirmation_sha256"] = object_sha256(_jsonable(payload))
    return _jsonable(payload)


def _mean_method_mse(latent: dict, method: str) -> float | None:
    values = [
        _eligible_t2_mse(row)
        for row in latent.get("methods", {}).get(method, {}).values()
    ]
    values = [float(value) for value in values if value is not None]
    return float(np.mean(values)) if values else None


def _fmt(value, digits=4) -> str:
    return "n/a" if value is None else f"{float(value):.{digits}g}"


def _decision_label(decision: dict, key: str = "pass") -> str:
    status = decision.get("status")
    if status == "indeterminate":
        return "INDETERMINATE"
    if status == "invalid":
        return "INVALID"
    return "PASS" if decision.get(key) else "FAIL"


def confirmation_markdown(payload: dict) -> str:
    run = payload["run"]
    lines = [
        f"# One-stage MSE symbolic reconstruction — `{run}`",
        "",
        "Frozen direct latent reconstruction with T0-selected equations, "
        "T1-only calibrations, and T2 confirmation. The existing interaction-"
        "aware hierarchy is recomputed on T2; its stored T1 combined R² is "
        "never reused as a confirmatory score.",
        "",
        "| latent | classification | flags | MSE20 | MSE30 | MSE40 | "
        "IA hierarchy MSE | objective | capacity | f2 absorbed | matches IA | "
        "saturated | R_SR |",
        "|---:|---|---|---:|---:|---:|---:|---|---|---|---|---|---:|",
    ]
    for latent in payload["latents"]:
        decisions = latent["decisions"]
        ia_mse = (
            ((latent["hierarchy"].get("interaction_aware") or {})
             .get("T2") or {}).get("mse"))
        lines.append(
            f"| z{latent['latent']} | {latent['classification']} "
            f"| {', '.join(latent['flags']) or '—'} "
            f"| {_fmt(_mean_method_mse(latent, 'mse20'))} "
            f"| {_fmt(_mean_method_mse(latent, 'mse30'))} "
            f"| {_fmt(_mean_method_mse(latent, 'mse40'))} "
            f"| {_fmt(ia_mse)} "
            f"| {_decision_label(decisions['mse_objective_helps'])} "
            f"| {_decision_label(decisions['capacity_helps'])} "
            f"| {_decision_label(decisions['known_f2_absorbed'])} "
            f"| {_decision_label(decisions['one_stage_matches_interaction_aware'])} "
            f"| {_decision_label(decisions['budget_saturated'], 'saturated')} "
            f"| {decisions['symbolically_stable']['r_sr']:.2f} |")

    for latent in payload["latents"]:
        lines.extend([
            "",
            f"## z{latent['latent']}",
            "",
            "| method | seed | symbolic core | T0 val MSE | T2 MSE | T2 NMSE | "
            "T2 R² | decision domain | expression |",
            "|---|---:|---:|---:|---:|---:|---:|---|---|",
        ])
        for method in ("mi20-mi", "mi20-mse", "mse20", "mse30", "mse40"):
            for seed, row in sorted(
                    latent.get("methods", {}).get(method, {}).items(),
                    key=lambda item: int(item[0])):
                metrics = row.get("T2") or {}
                expr = row["expression"]
                if len(expr) > 72:
                    expr = expr[:69] + "..."
                domain = row.get("decision_domain") or {}
                domain_label = (
                    "valid" if domain.get("eligible") else
                    "INVALID (" + ", ".join(
                        domain.get("invalid_tiers", [])) + ")")
                lines.append(
                    f"| {method} | {seed} | {row['complexity']} "
                    f"| {_fmt(row['T0_validation_mse'])} "
                    f"| {_fmt(metrics.get('mse'))} "
                    f"| {_fmt(metrics.get('nmse'))} "
                    f"| {_fmt(metrics.get('r2'))} | {domain_label} | `{expr}` |")
        hierarchy_labels = (
            ("h_f1", "h(f1)"),
            ("additive", "h(f1)+g(f2), additive"),
            ("interaction_aware", "h(f1)+g(f2), interaction-aware"),
        )
        for key, label in hierarchy_labels:
            row = latent.get("hierarchy", {}).get(key)
            if not row:
                continue
            metrics = row.get("T2") or {}
            if key == "h_f1":
                expr = f"h({row.get('expression_f1')})"
            else:
                expr = (f"h({row.get('expression_f1')}) + "
                        f"g({row.get('expression_f2')})")
            lines.append(
                f"| {label} | fixed | "
                f"{_fmt(row.get('symbolic_core_lower_bound'), 0)} | n/a "
                f"| {_fmt(metrics.get('mse'))} "
                f"| {_fmt(metrics.get('nmse'))} "
                f"| {_fmt(metrics.get('r2'))} | fixed baseline | `{expr}` |")

        known_f2 = latent.get("known_f2_definition") or {}
        lines.extend([
            "",
            "Canonical known `f2` audit source: additive residual hierarchy; "
            f"expression `{known_f2.get('expression') or 'unavailable'}`. "
            "The interaction-aware hierarchy remains the reconstruction "
            "denominator only.",
        ])

        one_se = latent.get("T0_one_se") or {}
        if one_se:
            lines.extend([
                "",
                "### T0 one-standard-error readout",
                "",
                "| method | metric | c_min | one-SE complexity | threshold | "
                "per-seed retained complexity |",
                "|---|---|---:|---:|---:|---|",
            ])
            for method, row in sorted(one_se.items()):
                choices = ", ".join(
                    f"s{seed}:c{choice['complexity']}"
                    for seed, choice in sorted(
                        row.get("by_seed", {}).items(),
                        key=lambda item: int(item[0])))
                lines.append(
                    f"| {method} | {row.get('metric', 'mse_val')} "
                    f"| {row.get('c_min')} | {row.get('complexity')} "
                    f"| {_fmt(row.get('threshold'))} | {choices or 'n/a'} |")
            lines.extend([
                "",
                "One-SE equations are secondary confirmations and do not "
                "carry success decisions.",
                "",
                "| method | seed | complexity | T2 MSE | T2 NMSE | T2 R² | "
                "decision domain | expression |",
                "|---|---:|---:|---:|---:|---:|---|---|",
            ])
            for method, readout in sorted(one_se.items()):
                for seed, row in sorted(
                        readout.get("confirmed_by_seed", {}).items(),
                        key=lambda item: int(item[0])):
                    metrics = row.get("T2") or {}
                    domain = row.get("decision_domain") or {}
                    domain_label = (
                        "valid" if domain.get("eligible") else
                        "INVALID (" + ", ".join(
                            domain.get("invalid_tiers", [])) + ")")
                    expr = row.get("expression") or ""
                    if len(expr) > 72:
                        expr = expr[:69] + "..."
                    lines.append(
                        f"| {method} | {seed} | {row.get('complexity')} "
                        f"| {_fmt(metrics.get('mse'))} "
                        f"| {_fmt(metrics.get('nmse'))} "
                        f"| {_fmt(metrics.get('r2'))} | {domain_label} "
                        f"| `{expr}` |")

        common = latent.get("T0_common_complexity") or {}
        cuts = common.get("cuts") or []
        if not cuts and common.get("methods"):
            cuts = [{
                "complexity_cut": common.get("complexity_cut"),
                "methods": common["methods"],
            }]
        if cuts:
            lines.extend([
                "",
                "### T0 common-complexity front comparison",
                "",
                "| cut | method | metric | mean validation error | SE |",
                "|---:|---|---|---:|---:|",
            ])
            for cut in cuts:
                for method, row in sorted(cut.get("methods", {}).items()):
                    lines.append(
                        f"| {cut.get('complexity_cut')} | {method} "
                        f"| {row.get('metric', 'mse_val')} "
                        f"| {_fmt(row.get('mean'))} | {_fmt(row.get('se'))} |")
    if payload.get("controls"):
        lines.extend([
            "",
            "## Shuffled-target controls",
            "",
            "| method | latent | seed | T0 val R² vs true | "
            "T0 val R² vs shuffle | T2 R² vs true | "
            "T2 R² vs independent shuffle |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ])
        for row in payload["controls"]:
            lines.append(
                f"| {row['method']} | z{row['latent']} | {row['seed']} "
                f"| {_fmt(row['T0_validation'].get('r2_vs_true'))} "
                f"| {_fmt(row['T0_validation'].get('r2_vs_shuffled'))} "
                f"| {_fmt(row['T2_true'].get('r2'))} "
                f"| {_fmt(row['T2_independently_shuffled'].get('r2'))} |")
    lines.extend([
        "",
        "---",
        "_Generated by `scripts/consolidate_mse_one_stage.py confirm`._",
        "",
    ])
    return "\n".join(lines)


def _default_manifest(run: str) -> Path:
    return Path("results") / run / "mse_one_stage_selection_manifest.json"


def _default_calibration(manifest_path: str | Path) -> Path:
    return Path(manifest_path).with_name("mse_one_stage_calibration.json")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_select = sub.add_parser("select", help="T0-only immutable selection")
    p_select.add_argument("--run", required=True, choices=sorted(MODELS))
    p_select.add_argument("--results-root", default="results")
    p_select.add_argument("--budgets", nargs="+", type=int,
                          default=list(DEFAULT_BUDGETS))
    p_select.add_argument("--seeds", nargs="+", type=int,
                          default=list(DEFAULT_SEEDS))
    p_select.add_argument("--latents", nargs="*", type=int, default=None)
    p_select.add_argument("--manifest", default=None)
    p_select.add_argument("--allow-incomplete", action="store_true")
    p_select.add_argument("--no-baselines", action="store_true")
    p_select.add_argument("--no-controls", action="store_true")

    p_cal = sub.add_parser("calibrate", help="T1-only calibration contract")
    p_cal.add_argument("--manifest", required=True)
    p_cal.add_argument("--dataset-dir", default="data")
    p_cal.add_argument("--models-root", default="models")
    p_cal.add_argument("--experiments-dir", default="experiments")
    p_cal.add_argument("--out", default=None)

    p_confirm = sub.add_parser("confirm", help="verified T2 confirmation")
    p_confirm.add_argument("--manifest", required=True)
    p_confirm.add_argument("--calibration", default=None)
    p_confirm.add_argument("--dataset-dir", default="data")
    p_confirm.add_argument("--models-root", default="models")
    p_confirm.add_argument("--experiments-dir", default="experiments")
    p_confirm.add_argument("--n-perm-mi", type=int, default=39)
    p_confirm.add_argument("--max-samples-mi", type=int, default=5000)
    p_confirm.add_argument("--mi-jobs", type=int, default=1)
    p_confirm.add_argument(
        "--skip-known-f2-mi", action="store_true",
        help="Debug only: skip the required known-f2 MI permutation test")
    p_confirm.add_argument("--out", default=None,
                           help="Output stem; defaults to experiments/"
                                "mse_one_stage_sr_<run>.")
    args = parser.parse_args()

    if args.command == "select":
        path = Path(args.manifest or _default_manifest(args.run))
        if path.exists():
            manifest = verify_manifest(path)
            if manifest.get("run") != args.run:
                raise ValueError(f"{path}: existing manifest is for another run")
            if manifest.get("budgets") != list(args.budgets):
                raise ValueError(f"{path}: existing manifest uses other budgets")
            if manifest.get("seeds") != list(args.seeds):
                raise ValueError(f"{path}: existing manifest uses other seeds")
            if args.latents is not None and manifest.get("latents") != args.latents:
                raise ValueError(f"{path}: existing manifest uses other latents")
            print(f"[reuse] verified immutable {path} "
                  f"(digest {manifest['manifest_sha256']})")
            return 0
        manifest = build_selection_manifest(
            args.run, args.results_root, args.budgets, args.seeds,
            args.latents, include_baselines=not args.no_baselines,
            include_controls=not args.no_controls,
            require_complete=not args.allow_incomplete)
        write_immutable_json(path, manifest, "manifest_sha256")
        print(f"[write] {path} ({len(manifest['selections'])} MSE choices, "
              f"{len(manifest['baseline_selections'])} baseline choices, "
              f"digest {manifest['manifest_sha256']})")
        return 0

    if args.command == "calibrate":
        path = Path(args.out or _default_calibration(args.manifest))
        if path.exists():
            manifest = verify_manifest(args.manifest)
            artifact = verify_calibration(path, manifest)
            print(f"[reuse] verified immutable {path} "
                  f"(digest {artifact['calibration_sha256']})")
            return 0
        artifact = build_calibration_artifact(
            args.manifest, args.dataset_dir, args.models_root,
            args.experiments_dir)
        write_immutable_json(path, artifact, "calibration_sha256")
        print(f"[write] {path} (digest {artifact['calibration_sha256']})")
        return 0

    calibration_path = args.calibration or _default_calibration(args.manifest)
    manifest = verify_manifest(args.manifest)
    calibration_artifact = verify_calibration(calibration_path, manifest)
    stem = Path(args.out or
                Path(args.experiments_dir) / f"mse_one_stage_sr_{manifest['run']}")
    json_path = stem.with_suffix(".json")
    md_path = stem.with_suffix(".md")
    if json_path.exists():
        payload = json.loads(json_path.read_text())
        verify_hashed_payload(payload, "confirmation_sha256")
        if payload.get("manifest_sha256") != manifest["manifest_sha256"]:
            raise ValueError("existing confirmation belongs to another manifest")
        if (payload.get("calibration_sha256")
                != calibration_artifact["calibration_sha256"]):
            raise ValueError(
                "existing confirmation belongs to another calibration")
        markdown = confirmation_markdown(payload)
        if md_path.exists() and md_path.read_text() != markdown:
            raise FileExistsError(
                f"existing confirmation Markdown differs: {md_path}")
        if not md_path.exists():
            utils.save_text(markdown, md_path)
        print(f"[reuse] verified immutable {json_path}")
        print(f"[reuse] verified {md_path}")
        return 0
    payload = confirm_experiment(
        args.manifest, calibration_path, args.dataset_dir, args.models_root,
        args.experiments_dir, n_perm_mi=args.n_perm_mi,
        max_samples_mi=args.max_samples_mi, mi_jobs=args.mi_jobs,
        compute_known_f2_mi=not args.skip_known_f2_mi)
    write_immutable_json(json_path, payload, "confirmation_sha256")
    markdown = confirmation_markdown(payload)
    if md_path.exists() and md_path.read_text() != markdown:
        raise FileExistsError(
            f"refusing to overwrite different confirmation report: {md_path}")
    utils.save_text(markdown, md_path)
    print(f"[write] {json_path}")
    print(f"[write] {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
