"""Focused contracts for the additive coordinate-matched OLS audit."""
import json
import pathlib
import sys

import numpy as np
import pytest


REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import audit_coordinate_matched_ols as audit  # noqa: E402


RUN = "lcdm_tt_beta3e-4"


def _write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload))
    return path


def _precision_artifact(kind, digest_key, **fields):
    body = {
        "schema_version": 1,
        "kind": kind,
        "study": audit.cpp.STUDY,
        "source_files": {},
        **fields,
    }
    return audit.cpp._attach_digest(body, digest_key)


def _audit_artifact(kind, digest_key, **fields):
    body = {
        "schema_version": 1,
        "kind": kind,
        "study": audit.STUDY,
        "source_files": {},
        **fields,
    }
    return audit._attach_digest(body, digest_key)


def _theta(n, offset=0.0):
    rng = np.random.default_rng(1000 + n + int(round(1000 * offset)))
    x = rng.uniform(-1.0, 1.0, size=(n, 6)) + offset
    return np.column_stack([
        0.022 + 0.001 * x[:, 0],
        0.12 + 0.005 * x[:, 1],
        68.0 + 2.0 * x[:, 2],
        0.055 + 0.008 * x[:, 3],
        3.04 + 0.08 * x[:, 4],
        0.965 + 0.02 * x[:, 5],
    ])


def test_standardized_ols_is_full_rank_and_affine_arm_invariant():
    rng = np.random.default_rng(4)
    theta = np.column_stack([
        rng.uniform(0.02, 0.024, 500),
        rng.uniform(0.10, 0.14, 500),
        rng.uniform(60, 80, 500),
        rng.uniform(0.03, 0.08, 500),
        rng.uniform(2.9, 3.2, 500),
        rng.uniform(0.92, 1.01, 500),
    ])
    y = (3 * theta[:, 0] - theta[:, 1] + 0.02 * theta[:, 2]
         - 2 * theta[:, 3] + 7e8 * np.exp(theta[:, 4]) * 1e-10
         + theta[:, 5])
    predictions = {}
    definitions = {}
    for arm in ("raw64", "physical_o1_64"):
        X, _ = audit._arm_matrix(theta, arm)
        definitions[arm], predictions[arm] = audit._fit_ols(X, y)
        assert definitions[arm]["rank"] == 7
        assert definitions[arm]["condition_number_standardized"] < 1.5
    np.testing.assert_allclose(
        predictions["raw64"], predictions["physical_o1_64"],
        rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(
        definitions["raw64"]["coef_standardized"],
        definitions["physical_o1_64"]["coef_standardized"],
        rtol=1e-11, atol=1e-11)


def test_paired_nmse_contrast_has_fixed_sign_convention_and_ci():
    y = np.linspace(-2, 2, 1000)
    ols = y + 0.01 * np.sin(np.arange(len(y)))
    worse_sr = y + 0.2 * np.sin(np.arange(len(y)))
    better_sr = y + 0.001 * np.sin(np.arange(len(y)))
    worse = audit.paired_nmse_contrast(y, worse_sr, ols)
    better = audit.paired_nmse_contrast(y, better_sr, ols)
    assert worse["delta_nmse"] > 0
    assert worse["verdict"] == "ols_lower_nmse"
    assert better["delta_nmse"] < 0
    assert better["verdict"] == "sr_lower_nmse"
    assert worse["ci_low"] < worse["ci_high"]
    assert worse["n_rows"] == len(y)


def test_fit_opens_only_t0_and_uses_manifest_arm(tmp_path, monkeypatch):
    arm = "logamp64"
    manifest = _precision_artifact(
        "precision_preprocess_selection", "manifest_sha256",
        run=RUN, arm=arm, arm_config=audit.cpp._normalised_config(arm),
        latents=[0], seeds=[0], selections=[])
    manifest_path = _write(tmp_path / "manifest.json", manifest)
    fit_theta, val_theta = _theta(80), _theta(30, 0.1)
    calls = []

    def fake_theta(_dataset, tier):
        calls.append(("theta", tier))
        if tier == audit.tiers.T0_FIT:
            return fit_theta
        assert tier == audit.tiers.T0_VAL
        return val_theta

    def fake_target(_models, _run, tier, _latent):
        calls.append(("target", tier))
        rows = fit_theta if tier == audit.tiers.T0_FIT else val_theta
        return 0.4 * rows[:, 4] - 2 * rows[:, 3] + rows[:, 0]

    monkeypatch.setattr(audit.cpp, "_test_theta", fake_theta)
    monkeypatch.setattr(audit.cpp, "_target_tier", fake_target)
    monkeypatch.setattr(audit, "_tier_sources", lambda *args: {})
    artifact = audit.build_fit_artifact(manifest_path)
    assert {tier for _, tier in calls} == {
        audit.tiers.T0_FIT, audit.tiers.T0_VAL}
    assert artifact["arm"] == arm
    assert artifact["variables"] == list(
        audit.cpp._normalised_config(arm)["inputs"])
    assert artifact["latents"][0]["definition"]["rank"] == 7
    audit.cpp.verify_digest(artifact, "fit_sha256")


def _fit_payload(arm="raw64"):
    theta = _theta(100)
    X, labels = audit._arm_matrix(theta, arm)
    definition, prediction = audit._fit_ols(X, 2 * theta[:, 0] - theta[:, 3])
    return _audit_artifact(
        "coordinate_matched_ols_fit", "fit_sha256",
        run=RUN, arm=arm, arm_config=audit.cpp._normalised_config(arm),
        variables=labels,
        upstream={"manifest_sha256": "manifest-hash"},
        latents=[{
            "latent": 0, "definition": definition,
            "T0_fit": audit.cpp.reconstruction_metrics(
                2 * theta[:, 0] - theta[:, 3], prediction),
            "T0_val": {},
        }])


def test_calibration_opens_t1_only_and_uses_frozen_fit(
        tmp_path, monkeypatch):
    fit = _fit_payload()
    fit_path = _write(tmp_path / "fit.json", fit)
    theta = _theta(120, 0.03)
    target = 3 * theta[:, 0] - 0.5 * theta[:, 3]
    calls = []

    def fake_theta(_dataset, tier):
        calls.append(tier)
        assert tier == audit.tiers.T1
        return theta

    def fake_target(_models, _run, tier, _latent):
        calls.append(tier)
        assert tier == audit.tiers.T1
        return target

    monkeypatch.setattr(audit.cpp, "_test_theta", fake_theta)
    monkeypatch.setattr(audit.cpp, "_target_tier", fake_target)
    monkeypatch.setattr(audit, "_tier_sources", lambda *args: {})
    artifact = audit.build_calibration_artifact(fit_path)
    assert set(calls) == {audit.tiers.T1}
    assert artifact["settings"] == audit.CALIBRATION_SETTINGS
    assert artifact["diagnostics"][0]["monotone_calibration_T1"]["valid"]


def test_confirmation_replays_sr_uses_exact_subset_and_only_estimates_ols_mi(
        tmp_path, monkeypatch):
    arm = "raw64"
    theta_t1, theta_t2 = _theta(140), _theta(160, 0.04)
    target_t1 = 1.8 * theta_t1[:, 0] - theta_t1[:, 3]
    target_t2 = 1.8 * theta_t2[:, 0] - theta_t2[:, 3]
    fit = _fit_payload(arm)
    manifest = _precision_artifact(
        "precision_preprocess_selection", "manifest_sha256",
        run=RUN, arm=arm, arm_config=audit.cpp._normalised_config(arm),
        latents=[0], seeds=[0], selections=[])
    fit["upstream"]["manifest_sha256"] = manifest["manifest_sha256"]
    fit.pop("fit_sha256")
    fit = audit._attach_digest(fit, "fit_sha256")
    fit_path = _write(tmp_path / "fit.json", fit)
    fit_row = fit["latents"][0]
    ols_t1 = audit.ols_prediction(fit, fit_row, theta_t1)
    raw_t1 = audit.cpp.reconstruction_metrics(target_t1, ols_t1)
    ols_cal = _audit_artifact(
        "coordinate_matched_ols_calibration", "calibration_sha256",
        run=RUN, arm=arm, fit_sha256=fit["fit_sha256"],
        diagnostics=[{
            "latent": 0, "raw_T1": raw_t1,
            "monotone_calibration_T1": {"valid": True},
        }])
    ols_cal_path = _write(tmp_path / "ols_cal.json", ols_cal)

    def selection(method):
        return {
            "run": RUN, "arm": arm, "method": method, "latent": 0,
            "seed": 0, "index": 2, "complexity": 4,
            "expression": "omega_b", "input_labels": list(
                audit.cpp._normalised_config(arm)["inputs"]),
            "target_transform": {
                "kind": "standardize", "mean": 0.0, "std": 1.0,
                "fit_rows": [0, 4000]},
        }

    manifest["selections"] = [selection("mi20-mi"), selection("mse40")]
    manifest.pop("manifest_sha256")
    manifest = audit.cpp._attach_digest(manifest, "manifest_sha256")
    fit["upstream"]["manifest_sha256"] = manifest["manifest_sha256"]
    fit.pop("fit_sha256")
    fit = audit._attach_digest(fit, "fit_sha256")
    fit_path = _write(tmp_path / "fit2.json", fit)
    ols_t1 = audit.ols_prediction(fit, fit["latents"][0], theta_t1)
    raw_t1 = audit.cpp.reconstruction_metrics(target_t1, ols_t1)
    ols_cal["fit_sha256"] = fit["fit_sha256"]
    ols_cal["diagnostics"][0]["raw_T1"] = raw_t1
    ols_cal.pop("calibration_sha256")
    ols_cal = audit._attach_digest(ols_cal, "calibration_sha256")
    ols_cal_path = _write(tmp_path / "ols_cal2.json", ols_cal)
    manifest_path = _write(tmp_path / "manifest.json", manifest)
    precision_cal = _precision_artifact(
        "precision_preprocess_calibration", "calibration_sha256",
        run=RUN, arm=arm, manifest_sha256=manifest["manifest_sha256"],
        settings={"n_folds": 5, "n_bins": 64, "monotone": True},
        diagnostics=[])
    precision_cal_path = _write(tmp_path / "precision_cal.json", precision_cal)

    def prediction(method, theta):
        return ((1.75 if method == "mse40" else 1.0) * theta[:, 0]
                - (0.95 if method == "mse40" else 0.2) * theta[:, 3])

    stored_methods = {}
    for method in ("mi20-mi", "mse40"):
        p1, p2 = prediction(method, theta_t1), prediction(method, theta_t2)
        calibrated = (audit._calibrated_prediction(p1, target_t1, p2)
                      if method == "mi20-mi" else None)
        stored_methods[method] = {"0": {
            "T2_raw": audit.cpp.reconstruction_metrics(target_t2, p2),
            "T2_calibrated": (audit.cpp.reconstruction_metrics(
                target_t2, calibrated) if calibrated is not None else None),
            "T2_gmm_mi_raw": {
                "valid": True, "mi": 1.2, "mi_err": 0.03},
        }}
    positions = np.array([1, 4, 7, 13, 19, 25, 31, 44, 57, 80])
    precision = _precision_artifact(
        "precision_preprocess_confirmation", "confirmation_sha256",
        run=RUN, arm=arm, manifest_sha256=manifest["manifest_sha256"],
        calibration_sha256=precision_cal["calibration_sha256"],
        matched_gmm_mi_subset={
            "positions": positions.tolist(),
            "positions_sha256": audit.cpp.array_sha256(positions),
            "size": len(positions), "tier": "T2"},
        latents=[{"latent": 0, "methods": stored_methods}])
    precision_path = _write(tmp_path / "precision.json", precision)

    def fake_theta(_dataset, tier):
        assert tier in (audit.tiers.T1, audit.tiers.T2)
        return theta_t1 if tier == audit.tiers.T1 else theta_t2

    def fake_target(_models, _run, tier, _latent):
        assert tier in (audit.tiers.T1, audit.tiers.T2)
        return target_t1 if tier == audit.tiers.T1 else target_t2

    monkeypatch.setattr(audit.cpp, "_test_theta", fake_theta)
    monkeypatch.setattr(audit.cpp, "_target_tier", fake_target)
    monkeypatch.setattr(audit, "_tier_sources", lambda *args: {})
    monkeypatch.setattr(
        audit.cpp, "evaluate_selection",
        lambda entry, theta: prediction(entry["method"], theta))
    estimator_calls = []

    def estimator(a, b, **kwargs):
        estimator_calls.append((a.copy(), b.copy(), kwargs))
        return np.array([[2.1]]), np.array([[0.02]])

    artifact = audit.build_confirmation_artifact(
        fit_path, ols_cal_path, manifest_path, precision_cal_path,
        precision_path, mi_estimator=estimator)
    assert len(estimator_calls) == 1
    np.testing.assert_allclose(estimator_calls[0][0][:, 0], target_t2[positions])
    row = artifact["latents"][0]
    assert row["ols"]["T2_gmm_mi_raw"]["mi"] == 2.1
    assert row["paired_contrasts"]["direct_mse40_vs_ols"]["0"]["valid"]
    assert row["paired_contrasts"]["calibrated_mi20_vs_ols"]["0"]["valid"]


def _confirmation(run, arm):
    latent = audit.AMPLITUDE_LATENTS[run]
    definition = {
        "coef_standardized": [1, 2, 3, 4, 5, 6],
        "intercept_standardized": 0.2,
    }
    metric = {"valid": True, "nmse": 0.01}
    gmm = {"valid": True, "mi": 1.5, "mi_err": 0.02}
    contrast = {
        "valid": True, "delta_nmse": 0.005, "paired_se": 0.001,
        "ci_low": 0.003, "ci_high": 0.007, "verdict": "ols_lower_nmse",
    }
    methods = {}
    for method in ("mi20-mi", "mse40"):
        methods[method] = {str(seed): {
            "T2_raw": metric,
            "T2_calibrated": metric if method == "mi20-mi" else None,
            "T2_gmm_mi_raw": gmm,
        } for seed in range(5)}
    return _audit_artifact(
        "coordinate_matched_ols_confirmation", "confirmation_sha256",
        run=run, arm=arm,
        matched_gmm_mi_subset={"positions_sha256": "same"},
        latents=[{
            "latent": latent,
            "ols": {"definition": definition, "T2_raw": metric,
                    "T2_calibrated": metric, "T2_gmm_mi_raw": gmm,
                    "tau_over_ln10As_coefficient_ratio": (
                        -2.0 if arm == "logamp64" else None)},
            "sr_replay": methods,
            "paired_contrasts": {
                "direct_mse40_vs_ols": {str(i): contrast for i in range(5)},
                "calibrated_mi20_vs_ols": {
                    str(i): contrast for i in range(5)},
            },
        }])


def test_render_requires_six_cells_and_checks_affine_invariance(tmp_path):
    paths = []
    for run in audit.MODELS:
        for arm in audit.ARM_IDS:
            paths.append(_write(
                tmp_path / f"{run}_{arm}.json", _confirmation(run, arm)))
    payload, markdown = audit.build_render_artifact(paths)
    assert set(payload["arms"]) == set(audit.ARM_IDS)
    assert payload["key_results"]["logamp64"]["n_latents"] == 2
    assert markdown.count("b_tau / b_ln10As = -2.0000") == 2
    assert markdown.count("| Latent | OLS raw NMSE %") == 3
    assert "not two independent wins" in markdown
    assert "up to five valid seedwise" in markdown
    assert "median [minimum, maximum]" in markdown
    with pytest.raises(ValueError, match="render requires"):
        audit.build_render_artifact(paths[:-1])

    changed = json.loads(paths[1].read_text())
    changed["latents"][0]["ols"]["definition"]["coef_standardized"][0] = 9
    changed.pop("confirmation_sha256")
    changed = audit._attach_digest(changed, "confirmation_sha256")
    paths[1].write_text(json.dumps(changed))
    with pytest.raises(ValueError, match="raw64/physical"):
        audit.build_render_artifact(paths)
