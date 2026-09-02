#!/usr/bin/env python
"""Additive, staged coordinate-matched OLS audit of precision_preprocess_v1.

``fit`` opens T0 only, ``calibrate`` opens T1 only, ``confirm`` is the first
stage to open T2, and ``render`` reads confirmation JSON only.  Existing
precision-preprocessing artifacts are verified and replayed, never modified.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import NormalDist
from typing import Callable, Iterable

import _bootstrap  # noqa: F401

import numpy as np

import consolidate_precision_preprocess as cpp
from cmb_lcdm_sr import calibrate, tiers
from cmb_lcdm_sr.mi import mutual_information_gmm


STUDY = "coordinate_matched_ols_v1"
SCHEMA_VERSION = 1
ARM_IDS = cpp.ARM_IDS
MODELS = cpp.MODELS
FINITE_MIN = cpp.FINITE_MIN
AMPLITUDE_LATENTS = {
    "lcdm_tt_beta3e-4": 2,
    "lcdm_tt_ee_lowl": 5,
}
CALIBRATION_SETTINGS = {
    "n_folds": 5,
    "n_bins": 64,
    "monotone": True,
    "seed": 0,
}
CI_LEVEL = 0.95


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _attach_digest(payload: dict, key: str) -> dict:
    return cpp._attach_digest(payload, key)


def _source_files(*paths: str | Path, base: dict[str, str] | None = None) -> dict:
    sources = dict(base or {})
    for path in paths:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(path)
        sources[str(path)] = cpp.file_sha256(path)
    return dict(sorted(sources.items()))


def _verify_sources(sources: dict[str, str]) -> None:
    for raw_path, expected in sources.items():
        path = Path(raw_path)
        if not path.exists():
            raise FileNotFoundError(f"frozen source missing: {path}")
        actual = cpp.file_sha256(path)
        if actual != expected:
            raise ValueError(
                f"frozen source changed: {path}\n"
                f"expected {expected}\nactual   {actual}")


def _verify(path: str | Path, kind: str, digest_key: str) -> dict:
    payload = json.loads(Path(path).read_text())
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"unsupported schema in {path}")
    if payload.get("kind") != kind or payload.get("study") != STUDY:
        raise ValueError(f"unexpected artifact kind/study in {path}")
    cpp.verify_digest(payload, digest_key)
    _verify_sources(payload.get("source_files", {}))
    return payload


def verify_fit(path: str | Path) -> dict:
    return _verify(path, "coordinate_matched_ols_fit", "fit_sha256")


def verify_calibration(path: str | Path, fit: dict | None = None) -> dict:
    payload = _verify(
        path, "coordinate_matched_ols_calibration", "calibration_sha256")
    if fit is not None and payload.get("fit_sha256") != fit.get("fit_sha256"):
        raise ValueError("calibration belongs to a different OLS fit")
    return payload


def verify_confirmation(path: str | Path) -> dict:
    return _verify(
        path, "coordinate_matched_ols_confirmation", "confirmation_sha256")


def _rows(payload: dict) -> dict[int, dict]:
    rows = {int(row["latent"]): row for row in payload.get("latents", [])}
    if len(rows) != len(payload.get("latents", [])):
        raise ValueError("duplicate latent rows")
    return rows


def _assert_identity(*payloads: dict) -> tuple[str, str]:
    identities = {(p.get("run"), p.get("arm")) for p in payloads}
    if len(identities) != 1:
        raise ValueError(f"run/arm mismatch: {sorted(identities)}")
    run, arm = next(iter(identities))
    if run not in MODELS or arm not in ARM_IDS:
        raise ValueError(f"unsupported run/arm: {run}/{arm}")
    return str(run), str(arm)


def _tier_sources(run: str, dataset_dir: str | Path,
                  models_root: str | Path) -> dict[str, str]:
    sources: dict[str, str] = {}
    for path in (
        Path(dataset_dir) / "theta.npy",
        Path(dataset_dir) / "splits_v1.npz",
        Path(models_root) / run / "analysis" / "encoder_means_test.npy",
    ):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(path)
        sources[str(path)] = cpp.file_sha256(path)
    return sources


def _arm_matrix(theta: np.ndarray, arm: str) -> tuple[np.ndarray, list[str]]:
    matrix, labels = cpp.build_arm_inputs(theta, arm)
    if not np.isfinite(matrix).all():
        raise ValueError(f"{arm} inputs contain non-finite values")
    return matrix, labels


def _fit_ols(X: np.ndarray, y: np.ndarray) -> tuple[dict, np.ndarray]:
    """Fit a numerically conditioned OLS without changing its function class."""
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    x_mean = X.mean(axis=0)
    x_scale = X.std(axis=0)
    if (not np.isfinite(x_mean).all() or not np.isfinite(x_scale).all()
            or np.any(x_scale <= 0)):
        raise ValueError("OLS inputs have a zero or non-finite T0-fit scale")
    Z = (X - x_mean) / x_scale
    design = np.column_stack([Z, np.ones(len(Z))])
    beta, _, rank, singular = np.linalg.lstsq(design, y, rcond=None)
    if int(rank) != design.shape[1]:
        raise ValueError(
            f"coordinate-matched OLS design is rank {rank}, expected "
            f"{design.shape[1]}")
    coef_z, intercept_z = beta[:-1], float(beta[-1])
    coef_arm = coef_z / x_scale
    intercept_arm = intercept_z - float(np.dot(coef_z, x_mean / x_scale))
    definition = {
        "x_mean": x_mean.tolist(),
        "x_scale": x_scale.tolist(),
        "coef_standardized": coef_z.tolist(),
        "intercept_standardized": intercept_z,
        "coef_arm_basis": coef_arm.tolist(),
        "intercept_arm_basis": intercept_arm,
        "rank": int(rank),
        "singular_values": singular.tolist(),
        "condition_number_standardized": float(singular[0] / singular[-1]),
    }
    return definition, design @ beta


def ols_prediction(fit: dict, latent_row: dict,
                   theta: np.ndarray) -> np.ndarray:
    X, labels = _arm_matrix(theta, fit["arm"])
    if labels != list(fit["variables"]):
        raise ValueError("OLS variable order changed")
    definition = latent_row["definition"]
    mean = np.asarray(definition["x_mean"], dtype=np.float64)
    scale = np.asarray(definition["x_scale"], dtype=np.float64)
    coef = np.asarray(definition["coef_standardized"], dtype=np.float64)
    return ((X - mean) / scale) @ coef + float(
        definition["intercept_standardized"])


def _tau_logamp_ratio(fit: dict, latent_row: dict) -> float | None:
    labels = list(fit["variables"])
    if "tau" not in labels or "ln10As" not in labels:
        return None
    coefficients = np.asarray(
        latent_row["definition"]["coef_arm_basis"], dtype=np.float64)
    denominator = float(coefficients[labels.index("ln10As")])
    if abs(denominator) <= 1e-300:
        return None
    return float(coefficients[labels.index("tau")] / denominator)


def build_fit_artifact(
        manifest_path: str | Path, dataset_dir: str | Path = "data",
        models_root: str | Path = "models") -> dict:
    """Fit one arm's OLS models on T0-fit and diagnose on T0-val."""
    manifest = cpp.verify_selection(manifest_path)
    run, arm = manifest["run"], manifest["arm"]
    theta_fit = cpp._test_theta(dataset_dir, tiers.T0_FIT)
    theta_val = cpp._test_theta(dataset_dir, tiers.T0_VAL)
    X_fit, labels = _arm_matrix(theta_fit, arm)
    X_val, val_labels = _arm_matrix(theta_val, arm)
    if labels != val_labels:
        raise ValueError("arm labels changed between T0-fit and T0-val")

    latent_rows = []
    for latent in manifest["latents"]:
        y_fit = cpp._target_tier(models_root, run, tiers.T0_FIT, latent)
        y_val = cpp._target_tier(models_root, run, tiers.T0_VAL, latent)
        definition, pred_fit = _fit_ols(X_fit, y_fit)
        pred_val = ((X_val - np.asarray(definition["x_mean"])) /
                    np.asarray(definition["x_scale"])) @ np.asarray(
                        definition["coef_standardized"]) + float(
                            definition["intercept_standardized"])
        latent_rows.append({
            "latent": int(latent),
            "definition": definition,
            "T0_fit": cpp.reconstruction_metrics(y_fit, pred_fit),
            "T0_val": cpp.reconstruction_metrics(y_val, pred_val),
        })

    sources = _tier_sources(run, dataset_dir, models_root)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "kind": "coordinate_matched_ols_fit",
        "study": STUDY,
        "created_utc": _now(),
        "run": run,
        "arm": arm,
        "arm_config": manifest["arm_config"],
        "variables": labels,
        "latents": latent_rows,
        "tiers": {
            "T0_fit": [tiers.T0_FIT.start, tiers.T0_FIT.stop],
            "T0_val": [tiers.T0_VAL.start, tiers.T0_VAL.stop],
        },
        "protocol": {
            "model": "ordinary_least_squares",
            "intercept": True,
            "solver": "numpy.linalg.lstsq",
            "rcond": None,
            "input_conditioning": "column mean/std fitted on T0-fit only",
            "target_units": "native encoder mean",
            "selection": "none; OLS has no tuned hyperparameter",
        },
        "upstream": {
            "precision_manifest": str(Path(manifest_path).resolve()),
            "manifest_sha256": manifest["manifest_sha256"],
        },
        "source_files": _source_files(manifest_path, base=sources),
    }
    return _attach_digest(payload, "fit_sha256")


def build_calibration_artifact(
        fit_path: str | Path, dataset_dir: str | Path = "data",
        models_root: str | Path = "models") -> dict:
    """Open T1 only and freeze OLS monotone-calibration diagnostics."""
    fit = verify_fit(fit_path)
    theta_t1 = cpp._test_theta(dataset_dir, tiers.T1)
    diagnostics = []
    for latent, row in sorted(_rows(fit).items()):
        target = cpp._target_tier(models_root, fit["run"], tiers.T1, latent)
        prediction = ols_prediction(fit, row, theta_t1)
        finite = np.isfinite(target) & np.isfinite(prediction)
        crossfit = None
        if finite.mean() >= FINITE_MIN:
            result = calibrate.crossfit_calibration(
                prediction, target, **CALIBRATION_SETTINGS)
            crossfit = {
                "valid": True,
                "finite_frac": float(result["finite_frac"]),
                "r2_crossfit": float(result["r2_cal"]),
            }
        else:
            crossfit = {"valid": False, "finite_frac": float(finite.mean())}
        diagnostics.append({
            "latent": latent,
            "raw_T1": cpp.reconstruction_metrics(target, prediction),
            "monotone_calibration_T1": crossfit,
        })
    sources = _tier_sources(fit["run"], dataset_dir, models_root)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "kind": "coordinate_matched_ols_calibration",
        "study": STUDY,
        "created_utc": _now(),
        "run": fit["run"],
        "arm": fit["arm"],
        "fit": str(Path(fit_path).resolve()),
        "fit_sha256": fit["fit_sha256"],
        "tier": {"name": "T1", "slice": [tiers.T1.start, tiers.T1.stop]},
        "settings": CALIBRATION_SETTINGS,
        "diagnostics": diagnostics,
        "source_files": _source_files(fit_path, base=sources),
    }
    return _attach_digest(payload, "calibration_sha256")


def _metric_replay(stored: dict | None, replayed: dict, label: str) -> None:
    if not stored or bool(stored.get("valid")) != bool(replayed.get("valid")):
        raise ValueError(f"{label}: stored/replayed validity differs")
    for key in ("finite_frac", "mse", "nmse", "r2", "mae"):
        a, b = stored.get(key), replayed.get(key)
        if a is None and b is None:
            continue
        if a is None or b is None or not np.isclose(
                float(a), float(b), rtol=1e-10, atol=1e-12):
            raise ValueError(f"{label}: stored/replayed {key} differs")


def paired_nmse_contrast(
        target: np.ndarray, sr_prediction: np.ndarray,
        ols_prediction_: np.ndarray, ci_level: float = CI_LEVEL) -> dict:
    """Paired analytic row CI for NMSE(SR) - NMSE(OLS)."""
    y = np.asarray(target, dtype=np.float64)
    sr = np.asarray(sr_prediction, dtype=np.float64)
    ols = np.asarray(ols_prediction_, dtype=np.float64)
    if not (y.shape == sr.shape == ols.shape):
        raise ValueError("paired contrast arrays have different shapes")
    finite = np.isfinite(y) & np.isfinite(sr) & np.isfinite(ols)
    base = {
        "valid": False,
        "n_rows": int(finite.sum()),
        "finite_frac": float(finite.mean()),
        "estimand": "NMSE(SR) - NMSE(OLS)",
        "positive_means": "OLS has lower squared error",
        "ci_method": "normal CI from paired T2 rowwise loss differences",
        "ci_level": float(ci_level),
    }
    if finite.mean() < FINITE_MIN or finite.sum() < 16:
        return base
    y, sr, ols = y[finite], sr[finite], ols[finite]
    variance = float(np.var(y))
    if variance <= 0 or not np.isfinite(variance):
        return base
    losses = ((y - sr) ** 2 - (y - ols) ** 2) / variance
    delta = float(losses.mean())
    se = float(losses.std(ddof=1) / np.sqrt(len(losses)))
    z = NormalDist().inv_cdf(0.5 + float(ci_level) / 2.0)
    low, high = delta - z * se, delta + z * se
    verdict = "ols_lower_nmse" if low > 0 else (
        "sr_lower_nmse" if high < 0 else "inconclusive")
    return base | {
        "valid": True,
        "delta_nmse": delta,
        "paired_se": se,
        "ci_low": float(low),
        "ci_high": float(high),
        "verdict": verdict,
    }


def _calibrated_prediction(x_t1: np.ndarray, y_t1: np.ndarray,
                           x_t2: np.ndarray) -> np.ndarray:
    finite1 = np.isfinite(x_t1) & np.isfinite(y_t1)
    if finite1.mean() < FINITE_MIN:
        raise ValueError("insufficient finite T1 rows for monotone calibration")
    h = calibrate.fit_h(
        x_t1[finite1], y_t1[finite1],
        n_bins=CALIBRATION_SETTINGS["n_bins"],
        monotone=CALIBRATION_SETTINGS["monotone"])
    out = np.full(len(x_t2), np.nan)
    finite2 = np.isfinite(x_t2)
    out[finite2] = h(x_t2[finite2])
    return out


def _selection_map(manifest: dict) -> dict[tuple[str, int, int], dict]:
    result = {}
    for entry in manifest["selections"]:
        key = (entry["method"], int(entry["latent"]), int(entry["seed"]))
        if key in result:
            raise ValueError(f"duplicate precision selection {key}")
        result[key] = entry
    return result


def _precision_latents(confirmation: dict) -> dict[int, dict]:
    return {int(row["latent"]): row for row in confirmation["latents"]}


def build_confirmation_artifact(
        fit_path: str | Path, calibration_path: str | Path,
        precision_manifest_path: str | Path,
        precision_calibration_path: str | Path,
        precision_confirmation_path: str | Path,
        dataset_dir: str | Path = "data", models_root: str | Path = "models",
        mi_estimator: Callable = mutual_information_gmm) -> dict:
    """Replay frozen SR, then score coordinate-matched OLS once on T2."""
    fit = verify_fit(fit_path)
    ols_cal = verify_calibration(calibration_path, fit)
    manifest = cpp.verify_selection(precision_manifest_path)
    precision_cal = cpp.verify_calibration(
        precision_calibration_path, manifest)
    precision = cpp.verify_confirmation(precision_confirmation_path)
    run, arm = _assert_identity(fit, ols_cal, manifest, precision_cal, precision)
    if precision.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise ValueError("precision confirmation/manifest mismatch")
    if precision.get("calibration_sha256") != precision_cal.get(
            "calibration_sha256"):
        raise ValueError("precision confirmation/calibration mismatch")
    if fit.get("upstream", {}).get("manifest_sha256") != manifest.get(
            "manifest_sha256"):
        raise ValueError("OLS fit used a different precision manifest")
    expected_settings = precision_cal.get("settings", {})
    for key in ("n_folds", "n_bins", "monotone"):
        if expected_settings.get(key) != CALIBRATION_SETTINGS[key]:
            raise ValueError(f"precision calibration setting {key} differs")

    positions = np.asarray(
        precision["matched_gmm_mi_subset"]["positions"], dtype=np.int64)
    if (cpp.array_sha256(positions) !=
            precision["matched_gmm_mi_subset"]["positions_sha256"]):
        raise ValueError("precision GMM-MI subset hash mismatch")
    if len(np.unique(positions)) != len(positions):
        raise ValueError("precision GMM-MI subset contains duplicates")

    theta_t1 = cpp._test_theta(dataset_dir, tiers.T1)
    theta_t2 = cpp._test_theta(dataset_dir, tiers.T2)
    if len(positions) == 0 or positions.min() < 0 or positions.max() >= len(theta_t2):
        raise ValueError("precision GMM-MI subset is outside T2")
    fit_rows = _rows(fit)
    ols_cal_rows = {int(row["latent"]): row
                    for row in ols_cal["diagnostics"]}
    selected = _selection_map(manifest)
    precision_rows = _precision_latents(precision)
    latent_rows = []

    for latent in manifest["latents"]:
        target_t1 = cpp._target_tier(models_root, run, tiers.T1, latent)
        target_t2 = cpp._target_tier(models_root, run, tiers.T2, latent)
        ols_t1 = ols_prediction(fit, fit_rows[latent], theta_t1)
        ols_t2 = ols_prediction(fit, fit_rows[latent], theta_t2)
        ols_raw = cpp.reconstruction_metrics(target_t2, ols_t2)
        _metric_replay(
            ols_cal_rows[latent]["raw_T1"],
            cpp.reconstruction_metrics(target_t1, ols_t1),
            f"z{latent} OLS T1")
        if not ols_cal_rows[latent]["monotone_calibration_T1"].get("valid"):
            raise ValueError(f"z{latent}: invalid frozen OLS calibration")
        ols_cal_t2 = _calibrated_prediction(ols_t1, target_t1, ols_t2)
        ols_cal_metrics = cpp.reconstruction_metrics(target_t2, ols_cal_t2)
        ols_mi = cpp.estimate_pair_mi(
            target_t2[positions], ols_t2[positions], mi_estimator)

        replayed: dict[str, dict[str, dict]] = defaultdict(dict)
        contrasts = {"direct_mse40_vs_ols": {},
                     "calibrated_mi20_vs_ols": {}}
        stored_latent = precision_rows[latent]
        for method in cpp.METHOD_SPECS:
            for seed in manifest["seeds"]:
                key = (method, int(latent), int(seed))
                entry = selected.get(key)
                if entry is None:
                    raise ValueError(f"missing frozen selection {key}")
                pred_t1 = cpp.evaluate_selection(entry, theta_t1)
                pred_t2 = cpp.evaluate_selection(entry, theta_t2)
                raw_metrics = cpp.reconstruction_metrics(target_t2, pred_t2)
                stored = stored_latent["methods"][method][str(seed)]
                _metric_replay(
                    stored["T2_raw"], raw_metrics,
                    f"z{latent} {method} seed {seed} raw T2")
                calibrated_metrics = None
                calibrated_pred = None
                if method == "mi20-mi":
                    calibrated_pred = _calibrated_prediction(
                        pred_t1, target_t1, pred_t2)
                    calibrated_metrics = cpp.reconstruction_metrics(
                        target_t2, calibrated_pred)
                    _metric_replay(
                        stored["T2_calibrated"], calibrated_metrics,
                        f"z{latent} {method} seed {seed} calibrated T2")
                    contrasts["calibrated_mi20_vs_ols"][str(seed)] = (
                        paired_nmse_contrast(
                            target_t2, calibrated_pred, ols_cal_t2))
                elif method == "mse40":
                    contrasts["direct_mse40_vs_ols"][str(seed)] = (
                        paired_nmse_contrast(target_t2, pred_t2, ols_t2))
                replayed[method][str(seed)] = {
                    "index": int(entry["index"]),
                    "complexity": int(entry["complexity"]),
                    "expression": entry["expression"],
                    "T2_raw": raw_metrics,
                    "T2_calibrated": calibrated_metrics,
                    "T2_gmm_mi_raw": stored["T2_gmm_mi_raw"],
                }
        latent_rows.append({
            "latent": int(latent),
            "ols": {
                "definition": fit_rows[latent]["definition"],
                "T2_raw": ols_raw,
                "T2_calibrated": ols_cal_metrics,
                "T2_gmm_mi_raw": ols_mi,
                "tau_over_ln10As_coefficient_ratio": _tau_logamp_ratio(
                    fit, fit_rows[latent]),
            },
            "sr_replay": dict(replayed),
            "paired_contrasts": contrasts,
        })

    sources = _tier_sources(run, dataset_dir, models_root)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "kind": "coordinate_matched_ols_confirmation",
        "study": STUDY,
        "created_utc": _now(),
        "run": run,
        "arm": arm,
        "arm_config": fit["arm_config"],
        "variables": fit["variables"],
        "tiers": {
            "T0_fit": [tiers.T0_FIT.start, tiers.T0_FIT.stop],
            "T0_val": [tiers.T0_VAL.start, tiers.T0_VAL.stop],
            "T1": [tiers.T1.start, tiers.T1.stop],
            "T2": [tiers.T2.start, tiers.T2.stop],
        },
        "matched_gmm_mi_subset": precision["matched_gmm_mi_subset"],
        "paired_uncertainty": {
            "ci_level": CI_LEVEL,
            "unit": "T2 row",
            "method": "analytic normal CI of paired rowwise loss differences",
            "denominator": "fixed full-T2 population variance per latent",
            "search_seed_variation": "reported separately; not folded into row CI",
        },
        "upstream": {
            "fit_sha256": fit["fit_sha256"],
            "ols_calibration_sha256": ols_cal["calibration_sha256"],
            "precision_manifest_sha256": manifest["manifest_sha256"],
            "precision_calibration_sha256": precision_cal["calibration_sha256"],
            "precision_confirmation_sha256": precision["confirmation_sha256"],
        },
        "latents": latent_rows,
        "source_files": _source_files(
            fit_path, calibration_path, precision_manifest_path,
            precision_calibration_path, precision_confirmation_path,
            base=sources),
    }
    return _attach_digest(payload, "confirmation_sha256")


def _numbers(rows: Iterable[dict], path: tuple[str, ...]) -> list[float]:
    values = []
    for row in rows:
        value = row
        for key in path:
            value = value.get(key, {}) if isinstance(value, dict) else None
        if isinstance(value, (int, float)) and np.isfinite(value):
            values.append(float(value))
    return values


def _summary(values: Iterable[float]) -> dict:
    values = sorted(float(v) for v in values if np.isfinite(v))
    return ({"n": 0, "median": None, "min": None, "max": None}
            if not values else {
                "n": len(values), "median": float(np.median(values)),
                "min": values[0], "max": values[-1]})


def _contrast_summary(rows: dict[str, dict]) -> dict:
    valid = [row for row in rows.values() if row.get("valid")]
    verdicts = defaultdict(int)
    for row in valid:
        verdicts[row["verdict"]] += 1
    return {
        "delta_nmse": _summary(row["delta_nmse"] for row in valid),
        "seedwise_ci_verdicts": dict(verdicts),
    }


def _lowest(choices: dict[str, float | None]) -> str | None:
    finite = {name: float(value) for name, value in choices.items()
              if value is not None and np.isfinite(value)}
    return min(finite, key=finite.get) if finite else None


def _key_results(arms: dict[str, list[dict]]) -> dict:
    results = {}
    for arm, rows in arms.items():
        direct = defaultdict(int)
        coordinate = defaultdict(int)
        mixed = defaultdict(int)
        mi_over_ols = 0
        for row in rows:
            direct_winner = _lowest({
                "OLS": row["ols_raw_nmse"],
                "MSE-SR": row["mse_sr_raw_nmse"]["median"],
            })
            coordinate_winner = _lowest({
                "OLS": row["ols_calibrated_nmse"],
                "MI-SR": row["mi_sr_calibrated_nmse"]["median"],
            })
            mixed_winner = _lowest({
                "OLS": row["ols_raw_nmse"],
                "MI-SR": row["mi_sr_calibrated_nmse"]["median"],
                "MSE-SR": row["mse_sr_raw_nmse"]["median"],
            })
            if direct_winner:
                direct[direct_winner] += 1
            if coordinate_winner:
                coordinate[coordinate_winner] += 1
            if mixed_winner:
                mixed[mixed_winner] += 1
            median_mi = row["mi_sr_mi"]["median"]
            mi_over_ols += int(
                median_mi is not None and row["ols_mi"] is not None and
                median_mi > row["ols_mi"])
        results[arm] = {
            "n_latents": len(rows),
            "median_mi_sr_mi_over_matched_ols": mi_over_ols,
            "direct_raw_nmse_winners": dict(direct),
            "coordinate_calibrated_nmse_winners": dict(coordinate),
            "mixed_pipeline_nmse_winners": dict(mixed),
        }
    return results


def _assert_affine_arm_equivalence(grouped: dict[str, dict[str, dict]]) -> None:
    """raw64 and physical_o1_64 must define the same affine predictor."""
    for run in MODELS:
        raw = _rows(grouped["raw64"][run])
        physical = _rows(grouped["physical_o1_64"][run])
        if set(raw) != set(physical):
            raise ValueError(f"raw/physical latent sets differ for {run}")
        for latent in raw:
            a = raw[latent]["ols"]["definition"]
            b = physical[latent]["ols"]["definition"]
            if not (np.allclose(
                    a["coef_standardized"], b["coef_standardized"],
                    rtol=1e-10, atol=1e-12) and np.isclose(
                        a["intercept_standardized"],
                        b["intercept_standardized"],
                        rtol=1e-10, atol=1e-12)):
                raise ValueError(
                    f"{run} z{latent}: raw64/physical OLS predictions differ")


def build_render_artifact(
        confirmation_paths: Iterable[str | Path], require_complete: bool = True
        ) -> tuple[dict, str]:
    paths = list(confirmation_paths)
    confirmations = [verify_confirmation(path) for path in paths]
    grouped: dict[str, dict[str, dict]] = defaultdict(dict)
    subset_hashes = set()
    for payload in confirmations:
        run, arm = payload["run"], payload["arm"]
        if run in grouped[arm]:
            raise ValueError(f"duplicate confirmation for {run}/{arm}")
        grouped[arm][run] = payload
        subset_hashes.add(
            payload["matched_gmm_mi_subset"]["positions_sha256"])
    if require_complete:
        if set(grouped) != set(ARM_IDS):
            raise ValueError(f"render requires arms {ARM_IDS}")
        for arm in ARM_IDS:
            if set(grouped[arm]) != set(MODELS):
                raise ValueError(f"render requires both checkpoints for {arm}")
        _assert_affine_arm_equivalence(grouped)
    if len(subset_hashes) != 1:
        raise ValueError("confirmations used different GMM-MI subsets")

    arms = {}
    for arm in ARM_IDS:
        arm_rows = []
        for run in MODELS:
            if run not in grouped.get(arm, {}):
                continue
            for latent in sorted(grouped[arm][run]["latents"],
                                 key=lambda row: row["latent"]):
                mse_rows = latent["sr_replay"]["mse40"]
                mi_rows = latent["sr_replay"]["mi20-mi"]
                arm_rows.append({
                    "run": run,
                    "arm": arm,
                    "latent": int(latent["latent"]),
                    "label": f"{MODELS[run]['label']} z{latent['latent']}",
                    "ols_raw_nmse": latent["ols"]["T2_raw"].get("nmse"),
                    "ols_calibrated_nmse": latent["ols"]["T2_calibrated"].get("nmse"),
                    "ols_mi": latent["ols"]["T2_gmm_mi_raw"].get("mi"),
                    "ols_mi_err": latent["ols"]["T2_gmm_mi_raw"].get("mi_err"),
                    "tau_over_ln10As_coefficient_ratio": latent["ols"].get(
                        "tau_over_ln10As_coefficient_ratio"),
                    "mse_sr_raw_nmse": _summary(_numbers(
                        mse_rows.values(), ("T2_raw", "nmse"))),
                    "mi_sr_calibrated_nmse": _summary(_numbers(
                        mi_rows.values(), ("T2_calibrated", "nmse"))),
                    "mse_sr_mi": _summary(_numbers(
                        mse_rows.values(), ("T2_gmm_mi_raw", "mi"))),
                    "mi_sr_mi": _summary(_numbers(
                        mi_rows.values(), ("T2_gmm_mi_raw", "mi"))),
                    "direct_contrast": _contrast_summary(
                        latent["paired_contrasts"]["direct_mse40_vs_ols"]),
                    "calibrated_contrast": _contrast_summary(
                        latent["paired_contrasts"]["calibrated_mi20_vs_ols"]),
                })
        arms[arm] = arm_rows
    payload = {
        "schema_version": SCHEMA_VERSION,
        "kind": "coordinate_matched_ols_render",
        "study": STUDY,
        "created_utc": _now(),
        "matched_gmm_mi_subset_sha256": next(iter(subset_hashes)),
        "arms": arms,
        "key_results": _key_results(arms),
        "source_files": _source_files(*paths),
    }
    payload = _attach_digest(payload, "render_sha256")
    return payload, render_markdown(payload)


def _fmt(value, digits=3) -> str:
    return "n/a" if value is None else f"{float(value):.{digits}f}"


def _fmt_range(summary: dict, scale: float = 1.0) -> str:
    if not summary.get("n"):
        return "n/a"
    return (f"{scale*summary['median']:.3f} "
            f"[{scale*summary['min']:.3f},{scale*summary['max']:.3f}]")


def _fmt_contrast(summary: dict) -> str:
    delta = summary["delta_nmse"]
    if not delta.get("n"):
        return "n/a"
    verdicts = summary["seedwise_ci_verdicts"]
    return (f"{100*delta['median']:+.3f} "
            f"[{100*delta['min']:+.3f},{100*delta['max']:+.3f}]; "
            f"OLS/SR/inc={verdicts.get('ols_lower_nmse',0)}/"
            f"{verdicts.get('sr_lower_nmse',0)}/"
            f"{verdicts.get('inconclusive',0)}")


def render_markdown(payload: dict) -> str:
    lines = [
        "# Coordinate-matched OLS audit",
        "",
        "OLS is refitted separately in each preprocessing arm on the 4,000 "
        "T0-fit rows. Every input column is centered and scaled using T0-fit "
        "statistics before the full-rank least-squares solve; this changes "
        "conditioning, not the affine hypothesis class.",
        "",
        "Direct reconstruction compares uncalibrated OLS with uncalibrated "
        "MSE-SR. Coordinate reconstruction applies the identical 64-bin "
        "T1-only monotone calibration to OLS and MI-SR. T2 is opened only in "
        "confirmation. GMM-MI uses the exact frozen precision-campaign subset.",
        "",
        "`Delta` is `NMSE(SR) - NMSE(OLS)` in percentage points; positive "
        "values favor OLS. OLS/SR/inc counts classify up to five valid "
        "seedwise 95% unadjusted paired-row normal CIs. These intervals are "
        "conditional on the frozen fits and calibrators and the observed T2 "
        "variance; they do not include search-, training-, or calibration-fit "
        "uncertainty and are not a pooled global test. A verdict total below "
        "five means an invalid seed was excluded.",
        "",
        "Every SR bracket in the tables is the median [minimum, maximum] "
        "across valid frozen search seeds, not a confidence interval.",
        "",
        "## Summary",
    ]
    for arm in ARM_IDS:
        result = payload["key_results"][arm]
        direct = result["direct_raw_nmse_winners"]
        coordinate = result["coordinate_calibrated_nmse_winners"]
        mixed = result["mixed_pipeline_nmse_winners"]
        lines.extend([
            "",
            f"- `{arm}`: median MI-SR MI exceeds matched OLS for "
            f"{result['median_mi_sr_mi_over_matched_ols']}/"
            f"{result['n_latents']} latents. Direct raw-NMSE winners: OLS "
            f"{direct.get('OLS', 0)}, MSE-SR {direct.get('MSE-SR', 0)}. "
            f"Coordinate calibrated-NMSE winners: OLS "
            f"{coordinate.get('OLS', 0)}, MI-SR "
            f"{coordinate.get('MI-SR', 0)}. Mixed pipeline winners: OLS "
            f"{mixed.get('OLS', 0)}, MI-SR {mixed.get('MI-SR', 0)}, MSE-SR "
            f"{mixed.get('MSE-SR', 0)}.",
        ])

    lines.extend(["", "## Log-amplitude OLS −2 diagnostic", ""])
    log_rows = payload["arms"]["logamp64"]
    for run, latent in AMPLITUDE_LATENTS.items():
        row = next((item for item in log_rows
                    if item["run"] == run and item["latent"] == latent), None)
        if row is None:
            continue
        lines.append(
            f"- {row['label']}: `b_tau / b_ln10As = "
            f"{_fmt(row['tau_over_ln10As_coefficient_ratio'], 4)}`.")
    for arm in ARM_IDS:
        rows = payload.get("arms", {}).get(arm)
        if rows is None:
            continue
        lines.extend([
            "", f"## `{arm}`", "",
            "| Latent | OLS raw NMSE % | MSE-SR raw NMSE % | Direct Delta % | "
            "OLS calibrated NMSE % | MI-SR calibrated NMSE % | Calibrated Delta % | OLS MI | MI-SR MI |",
            "|---|---:|---:|---|---:|---:|---|---:|---:|",
        ])
        for row in rows:
            ols_mi = (_fmt(row["ols_mi"]) + "±" + _fmt(row["ols_mi_err"])
                      if row["ols_mi"] is not None else "n/a")
            lines.append(
                f"| {row['label']} | {_fmt(100*row['ols_raw_nmse'])} | "
                f"{_fmt_range(row['mse_sr_raw_nmse'],100)} | "
                f"{_fmt_contrast(row['direct_contrast'])} | "
                f"{_fmt(100*row['ols_calibrated_nmse'])} | "
                f"{_fmt_range(row['mi_sr_calibrated_nmse'],100)} | "
                f"{_fmt_contrast(row['calibrated_contrast'])} | {ols_mi} | "
                f"{_fmt_range(row['mi_sr_mi'])} |")
    lines.extend([
        "", "The `raw64` and `physical_o1_64` OLS predictors are required to "
        "agree after T0-fit conditioning because their inputs differ only by "
        "invertible affine rescaling. They are one invariance check, not two "
        "independent wins. `logamp64` is the genuinely different affine model.",
        "", "GMM-MI uncertainties are estimator bootstrap errors copied for "
        "frozen SR and recomputed for matched OLS. They are descriptive and "
        "are not treated as paired significance tests.",
    ])
    return "\n".join(lines) + "\n"


def _write_json(path: str | Path, payload: dict, digest_key: str) -> None:
    cpp.write_immutable_json(path, payload, digest_key)


def _write_text(path: str | Path, content: str) -> None:
    cpp.write_immutable_text(path, content)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    fit = sub.add_parser("fit")
    fit.add_argument("--manifest", required=True)
    fit.add_argument("--dataset-dir", default="data")
    fit.add_argument("--models-root", default="models")
    fit.add_argument("--out", required=True)
    cal = sub.add_parser("calibrate")
    cal.add_argument("--fit", required=True)
    cal.add_argument("--dataset-dir", default="data")
    cal.add_argument("--models-root", default="models")
    cal.add_argument("--out", required=True)
    confirm = sub.add_parser("confirm")
    confirm.add_argument("--fit", required=True)
    confirm.add_argument("--calibration", required=True)
    confirm.add_argument("--precision-manifest", required=True)
    confirm.add_argument("--precision-calibration", required=True)
    confirm.add_argument("--precision-confirmation", required=True)
    confirm.add_argument("--dataset-dir", default="data")
    confirm.add_argument("--models-root", default="models")
    confirm.add_argument("--out", required=True)
    render = sub.add_parser("render")
    render.add_argument("--confirmations", nargs="+", required=True)
    render.add_argument("--out-json", required=True)
    render.add_argument("--out-md", required=True)
    args = parser.parse_args()

    if args.command == "fit":
        out = Path(args.out)
        if out.exists():
            verify_fit(out)
            print(f"[exists] {out}")
            return
        _write_json(out, build_fit_artifact(
            args.manifest, args.dataset_dir, args.models_root), "fit_sha256")
    elif args.command == "calibrate":
        out = Path(args.out)
        if out.exists():
            verify_calibration(out, verify_fit(args.fit))
            print(f"[exists] {out}")
            return
        _write_json(out, build_calibration_artifact(
            args.fit, args.dataset_dir, args.models_root), "calibration_sha256")
    elif args.command == "confirm":
        out = Path(args.out)
        if out.exists():
            verify_confirmation(out)
            print(f"[exists] {out}")
            return
        artifact = build_confirmation_artifact(
            args.fit, args.calibration, args.precision_manifest,
            args.precision_calibration, args.precision_confirmation,
            args.dataset_dir, args.models_root)
        _write_json(out, artifact, "confirmation_sha256")
    else:
        out_json, out_md = Path(args.out_json), Path(args.out_md)
        if out_json.exists() or out_md.exists():
            if not (out_json.exists() and out_md.exists()):
                raise FileExistsError("render outputs must both exist or neither")
            payload = _verify(
                out_json, "coordinate_matched_ols_render", "render_sha256")
            if out_md.read_text() != render_markdown(payload):
                raise ValueError("existing Markdown does not match render JSON")
            print(f"[exists] {out_json} and {out_md}")
            return
        artifact, markdown = build_render_artifact(args.confirmations)
        _write_json(out_json, artifact, "render_sha256")
        _write_text(out_md, markdown)
        print(f"[write] {out_json} and {out_md}")


if __name__ == "__main__":
    main()
