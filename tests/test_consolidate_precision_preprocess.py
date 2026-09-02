"""Staged, arm-aware consolidation for the precision/preprocessing study."""
import json
import pathlib
import re
import sys

import numpy as np
import pytest


REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import consolidate_precision_preprocess as cpp  # noqa: E402


def _entry(method, arm="raw64", seed=0, expression="omega_b"):
    labels, _ = cpp._expected_config_fields(arm)
    return {
        "run": "lcdm_tt_beta3e-4",
        "arm": arm,
        "method": method,
        "latent": 0,
        "seed": seed,
        "index": seed + 2,
        "complexity": 4 + seed,
        "expression": expression,
        "mi_val": 1.2 - 0.01 * seed,
        "mi_val_err": 0.02,
        "mse_val": 0.1 + 0.01 * seed,
        "mse_val_native": 0.1 + 0.01 * seed,
        "nmse_val": 0.1 + 0.01 * seed,
        "finite_frac_fit": 1.0,
        "finite_frac_val": 1.0,
        "target_transform": {
            "kind": "standardize", "fit_rows": [0, 4000],
            "mean": 0.0, "std": 1.0,
        },
        "input_labels": labels,
        "input_sampled_expressions": cpp._expected_config_fields(arm)[1],
        "report": "/unused/report.json",
    }


def _artifact(kind, digest_key, **fields):
    body = {
        "schema_version": 1,
        "kind": kind,
        "study": cpp.STUDY,
        "source_files": {},
        **fields,
    }
    return cpp._attach_digest(body, digest_key)


def _write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload))
    return path


def _report(arm, method):
    labels, expressions = cpp._expected_config_fields(arm)
    spec = cpp.METHOD_SPECS[method]
    if method == "mi20-mi":
        rows = [
            {"index": 5, "complexity": 7, "mi_val": 0.8,
             "mse_val": 0.4, "expression_raw": "omega_b"},
            {"index": 3, "complexity": 5, "mi_val": 0.8,
             "mse_val": 0.5, "expression_raw": "omega_cdm"},
            {"index": 2, "complexity": 5, "mi_val": 0.8,
             "mse_val": 0.6, "expression_raw": "H0"},
            {"index": 1, "complexity": 2, "mi_val": 0.7,
             "mse_val": 0.3, "expression_raw": "tau"},
        ]
    else:
        rows = [
            {"index": 5, "complexity": 7, "mi_val": None,
             "mse_val": 0.2, "expression_raw": "omega_b"},
            {"index": 3, "complexity": 5, "mi_val": None,
             "mse_val": 0.2, "expression_raw": "omega_cdm"},
            {"index": 2, "complexity": 5, "mi_val": None,
             "mse_val": 0.2, "expression_raw": "H0"},
            {"index": 1, "complexity": 2, "mi_val": None,
             "mse_val": 0.3, "expression_raw": "tau"},
        ]
    for row in rows:
        row.update({
            "mi_val_err": 0.01 if row["mi_val"] is not None else None,
            "mse_val_native": row["mse_val"],
            "nmse_val": row["mse_val"],
            "finite_frac_fit": 1.0,
            "finite_frac_val": 1.0,
        })
    return {
        "input_config": arm,
        "input_names": list(cpp._normalised_config(arm)["inputs"]),
        "input_labels": labels,
        "input_sampled_expressions": expressions,
        "inner_loss": spec["inner_loss"],
        "selection_metric": spec["selection_metric"],
        "selection_direction": (
            "descending" if spec["selection_metric"] == "mi" else "ascending"),
        "posthoc_mi_mode": "full" if method == "mi20-mi" else "none",
        "posthoc_mi_status": (
            "computed" if method == "mi20-mi" else "skipped_not_selected"),
        "n_samples": 5000,
        "n_fit": 4000,
        "n_val": 1000,
        "pysr_kwargs": {
            "niterations": 200, "populations": 15,
            "maxsize": spec["budget"], "precision": 64,
            "print_precision": 17,
            "parallelism": "multithreading", "random_state": 0,
            "run_id": "test-run",
            "binary_operators": ["+", "*", "-", "/"],
            "unary_operators": ["exp", "log", "neg", "square"],
        },
        "regime": "lcdm_tt_beta3e-4",
        "run_dir": "/models/lcdm_tt_beta3e-4",
        "latent_index": 0,
        "seed": 0,
        "target_npy": None,
        "extra_inputs": [],
        "tie_break": ["complexity_ascending", "equation_index_ascending"],
        "ols_baseline": {
            "status": "skipped", "reason": "fixed_old_ols_reused_downstream"},
        "target_transform": {
            "kind": "standardize", "fit_rows": [0, 4000],
            "mean": 2.0, "std": 3.0,
        },
        "n_equations": len(rows),
        "best_expression": "H0",
        "best_mi_val": 0.8 if method == "mi20-mi" else None,
        "best_mse_val": 0.2 if method == "mse40" else 0.6,
        "all_equations": rows,
    }


def test_arm_aware_evaluation_raw_operators_and_sampled_semantics():
    theta = np.array([
        [0.02, 0.12, 70.0, 0.05, 3.0, 0.96],
        [0.03, 0.10, 65.0, 0.08, 3.1, 1.01],
    ])
    matrix, labels = cpp.build_arm_inputs(theta, "physical_o1_64")
    assert labels == ["wb100", "wc10", "h", "tau", "A9", "n_s"]
    expected = np.column_stack([
        100 * theta[:, 0], 10 * theta[:, 1], theta[:, 2] / 100,
        theta[:, 3], np.exp(theta[:, 4]) / 10, theta[:, 5],
    ])
    np.testing.assert_allclose(matrix, expected)

    values = cpp.evaluate_arm_expression(
        "square(wb100) + neg(wc10) + h + A9", theta,
        "physical_o1_64", labels)
    np.testing.assert_allclose(
        values, expected[:, 0] ** 2 - expected[:, 1] +
        expected[:, 2] + expected[:, 4])

    sampled = cpp.expression_in_sampled_basis(
        "log(A9) - 2*tau", "physical_o1_64", labels)
    assert cpp.has_as_tau_signature(sampled)
    assert cpp.has_as_tau_signature("ln10As - 2.01*tau")
    assert not cpp.has_as_tau_signature("ln10As + tau")


def test_selection_is_report_only_ranked_and_hashed(tmp_path, monkeypatch):
    for method in cpp.METHOD_SPECS:
        path = cpp.report_path(
            tmp_path / "results", "lcdm_tt_beta3e-4", "raw64",
            method, 0, 0)
        _write(path, _report("raw64", method))
        path.with_name("equations.csv").write_text("equation\nomega_b\n")

    monkeypatch.setattr(
        cpp.np, "load",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("T0 selection must not load data arrays")))
    manifest = cpp.build_selection_manifest(
        "lcdm_tt_beta3e-4", "raw64", tmp_path / "results",
        latents=[0], seeds=[0])
    selected = {row["method"]: row for row in manifest["selections"]}
    assert selected["mi20-mi"]["index"] == 2
    assert selected["mse40"]["index"] == 2
    cpp.verify_digest(manifest, "manifest_sha256")
    assert len(manifest["source_files"]) == 4

    changed = json.loads(json.dumps(manifest))
    changed["selections"][0]["index"] = 99
    with pytest.raises(ValueError, match="manifest_sha256 mismatch"):
        cpp.verify_digest(changed, "manifest_sha256")

    bad = _report("raw64", "mse40")
    bad["pysr_kwargs"]["precision"] = 32
    with pytest.raises(ValueError, match="precision=32"):
        cpp.validate_report(bad, "raw64", "mse40", pathlib.Path("bad.json"))

    computed_ols = _report("raw64", "mse40")
    computed_ols["ols_baseline"] = {"coefs": [1.0], "mse_val": 0.1}
    with pytest.raises(ValueError, match="exact frozen skipped status"):
        cpp.validate_report(
            computed_ols, "raw64", "mse40", pathlib.Path("computed.json"))


def test_calibration_stage_opens_t1_only_and_only_calibrates_mi(
        tmp_path, monkeypatch):
    manifest = _artifact(
        "precision_preprocess_selection", "manifest_sha256",
        run="lcdm_tt_beta3e-4", arm="raw64",
        arm_config=cpp._normalised_config("raw64"), latents=[0], seeds=[0],
        selections=[_entry("mi20-mi"), _entry("mse40")])
    manifest_path = _write(tmp_path / "manifest.json", manifest)
    calls = []
    theta = np.zeros((40, 6))
    theta[:, 0] = np.linspace(-1, 1, len(theta))

    def fake_theta(_dataset, tier):
        calls.append(("theta", tier))
        assert tier == cpp.tiers.T1
        return theta

    def fake_target(_models, _run, tier, _latent):
        calls.append(("target", tier))
        assert tier == cpp.tiers.T1
        return 2 * theta[:, 0] + 0.1

    monkeypatch.setattr(cpp, "_test_theta", fake_theta)
    monkeypatch.setattr(cpp, "_target_tier", fake_target)
    monkeypatch.setattr(cpp, "_data_sources", lambda *args: {})
    monkeypatch.setattr(
        cpp, "evaluate_selection",
        lambda entry, rows: rows[:, 0] if entry["method"] == "mi20-mi"
        else rows[:, 0] ** 2)
    crossfit_calls = []
    monkeypatch.setattr(
        cpp.calibrate, "crossfit_calibration",
        lambda *args, **kwargs: (
            crossfit_calls.append(kwargs) or
            {"finite_frac": 1.0, "r2_cal": 0.9}))

    artifact = cpp.build_calibration_artifact(manifest_path)
    assert all(tier == cpp.tiers.T1 for _, tier in calls)
    assert crossfit_calls == [{
        "n_folds": 5, "n_bins": 64, "monotone": True, "seed": 0}]
    diagnostics = {row["method"]: row for row in artifact["diagnostics"]}
    assert diagnostics["mi20-mi"]["monotone_calibration_T1"]["valid"]
    assert diagnostics["mse40"]["monotone_calibration_T1"] is None


def test_matched_subset_and_gmm_wrapper_are_deterministic():
    first = cpp.common_mi_positions(100, size=20, seed=7)
    second = cpp.common_mi_positions(100, size=20, seed=7)
    np.testing.assert_array_equal(first, second)
    assert len(np.unique(first)) == 20
    assert cpp.array_sha256(first) == cpp.array_sha256(second)

    seen = {}

    def estimator(a, b, **kwargs):
        seen.update({"a": a.copy(), "b": b.copy(), **kwargs})
        return np.array([[1.25]]), np.array([[0.03]])

    target = np.arange(20.0)
    prediction = target**2
    result = cpp.estimate_pair_mi(target, prediction, estimator)
    assert result == {
        "valid": True, "n_rows": 20, "finite_frac": 1.0,
        "mi": 1.25, "mi_err": 0.03,
    }
    assert seen["max_samples"] is None
    np.testing.assert_array_equal(seen["a"][:, 0], target)
    assert not cpp.estimate_pair_mi(
        target, np.where(target == 3, np.nan, prediction), estimator)["valid"]


def test_confirmation_replays_but_never_refits_or_reestimates_ols(
        tmp_path, monkeypatch):
    run, arm = "lcdm_tt_beta3e-4", "raw64"
    manifest = _artifact(
        "precision_preprocess_selection", "manifest_sha256",
        run=run, arm=arm, arm_config=cpp._normalised_config(arm),
        latents=[0], seeds=[0],
        selections=[_entry("mi20-mi"), _entry("mse40")])
    manifest_path = _write(tmp_path / "manifest.json", manifest)
    diagnostics = [
        {"method": "mi20-mi", "latent": 0, "seed": 0,
         "monotone_calibration_T1": {"valid": True}},
        {"method": "mse40", "latent": 0, "seed": 0,
         "monotone_calibration_T1": None},
    ]
    calibration = _artifact(
        "precision_preprocess_calibration", "calibration_sha256",
        run=run, arm=arm, manifest_sha256=manifest["manifest_sha256"],
        diagnostics=diagnostics)
    calibration_path = _write(tmp_path / "calibration.json", calibration)

    theta_t1 = np.zeros((40, 6))
    theta_t2 = np.zeros((40, 6))
    theta_t1[:, 0] = np.linspace(-0.9, 0.9, 40)
    theta_t2[:, 0] = np.linspace(-1.0, 1.0, 40)
    target_t1 = theta_t1[:, 0] + 0.05 * np.sin(3 * theta_t1[:, 0])
    target_t2 = theta_t2[:, 0] + 0.05 * np.sin(3 * theta_t2[:, 0])
    ols_prediction = theta_t2[:, 0]
    ols_metrics = cpp.reconstruction_metrics(target_t2, ols_prediction)

    experiments = tmp_path / "experiments"
    legacy = {
        "latents": [{
            "latent": 0,
            "simple_baselines": {"six_input_ols": {
                "metrics": ols_metrics,
                "coefs": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                "variables": [
                    "omega_b", "omega_cdm", "H0", "tau", "A_s", "n_s",
                    "bias",
                ],
            }},
        }],
    }
    legacy_path = _write(
        experiments / f"mse_one_stage_sr_{run}.json", legacy)
    baseline = tmp_path / "baseline.md"
    baseline.write_text(
        "| Latent | OLS MI | MI-SR MI | MSE-SR MI | OLS NMSE % | "
        "MI-SR calibrated NMSE % | MSE-SR raw NMSE % |\n"
        f"| TT z0 | 1.234±.056 | 0 | 0 | {100 * ols_metrics['nmse']:.12f} "
        "| 0 | 0 |\n")

    def fake_theta(_dataset, tier):
        if tier == cpp.tiers.T1:
            return theta_t1
        assert tier == cpp.tiers.T2
        return theta_t2

    def fake_target(_models, _run, tier, _latent):
        if tier == cpp.tiers.T1:
            return target_t1
        assert tier == cpp.tiers.T2
        return target_t2

    monkeypatch.setattr(cpp, "_test_theta", fake_theta)
    monkeypatch.setattr(cpp, "_target_tier", fake_target)
    monkeypatch.setattr(cpp, "_data_sources", lambda *args: {})
    monkeypatch.setattr(cpp, "_gmm_version", lambda: "test")
    monkeypatch.setattr(
        cpp, "evaluate_selection",
        lambda entry, rows: (
            rows[:, 0] + 0.02 if entry["method"] == "mi20-mi"
            else 0.95 * rows[:, 0]))
    monkeypatch.setattr(
        cpp.np.linalg, "lstsq",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("frozen OLS must never be refitted")))
    estimator_calls = []

    def estimator(a, b, **kwargs):
        estimator_calls.append((a.copy(), b.copy(), kwargs))
        return np.array([[2.0]]), np.array([[0.1]])

    artifact = cpp.build_confirmation_artifact(
        manifest_path, calibration_path,
        experiments_dir=experiments, baseline_report=baseline,
        mi_estimator=estimator)
    assert len(estimator_calls) == 2  # MI-SR + MSE-SR; never OLS
    row = artifact["latents"][0]
    assert row["ols"]["T2_raw"] == ols_metrics
    assert row["ols"]["T2_gmm_mi_raw"]["mi"] == 1.234
    assert row["ols"]["T2_gmm_mi_raw"]["mi_err"] == 0.056
    assert row["methods"]["mi20-mi"]["0"]["T2_calibrated"]["valid"]
    assert row["methods"]["mse40"]["0"]["T2_calibrated"] is None
    assert str(legacy_path.resolve()) in artifact["source_files"]
    assert str(baseline.resolve()) in artifact["source_files"]
    cpp.verify_digest(artifact, "confirmation_sha256")


def _summary_row(arm):
    representative = {
        "mi20-mi": {
            "seed": 0, "complexity": 7,
            "expression": "ln10As - 2*tau",
            "sampled_expression": "ln10As - 2*tau",
            "as_tau_signature": True,
        },
        "mse40": {
            "seed": 1, "complexity": 8, "expression": "omega_b",
            "sampled_expression": "omega_b", "as_tau_signature": False,
        },
    }
    return {
        "run": "lcdm_tt_beta3e-4", "arm": arm, "latent": 0,
        "label": "TT z0", "ols_mi": 1.0, "ols_mi_err": 0.02,
        "ols_mi_display": "1.000±.020",
        "ols_nmse": 0.01,
        "mi_sr_mi": {"n": 5, "median": 1.2, "min": 1.1, "max": 1.3},
        "mse_sr_mi": {"n": 5, "median": 0.9, "min": 0.8, "max": 1.0},
        "mi_sr_nmse": {"n": 5, "median": 0.02, "min": 0.01, "max": 0.03},
        "mse_sr_nmse": {"n": 5, "median": 0.03, "min": 0.02, "max": 0.04},
        "representative": representative,
    }


def test_renderer_is_substantive_and_ends_with_exactly_three_tables():
    arms = {arm: [_summary_row(arm)] for arm in cpp.ARM_IDS}
    payload = {
        "arm_configs": {arm: cpp._normalised_config(arm) for arm in cpp.ARM_IDS},
        "arms": arms,
        "key_results": cpp._key_results(arms),
    }
    markdown = cpp.render_markdown(payload)
    assert "## Setup and protocol" in markdown
    assert "## Preprocessing definitions" in markdown
    assert "## Key result summary" in markdown
    assert "## Representative T0-selected equations" in markdown
    assert "A_s–tau signature" in markdown
    assert markdown.count("| Latent | OLS MI | MI-SR MI | MSE-SR MI |") == 3
    final_start = markdown.index("## Final held-out T2 tables")
    final = markdown[final_start:]
    assert len(re.findall(r"^### `(?:raw64|physical_o1_64|logamp64)`$",
                         final, flags=re.MULTILINE)) == 3
    assert not re.search(r"^## ", final.split("\n", 1)[1], flags=re.MULTILINE)
    assert markdown.rstrip().endswith("| 3.000 [2.000,4.000] |")
