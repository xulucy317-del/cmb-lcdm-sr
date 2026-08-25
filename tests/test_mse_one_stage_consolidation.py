"""Frozen selection, hashing, and confirmation helpers for one-stage MSE SR."""
import inspect
import json
import pathlib
import sys

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

import consolidate_mse_one_stage as cms  # noqa: E402


def _row(index, complexity, mse, mi=0.1, expression="omega_b"):
    return {
        "index": index,
        "complexity": complexity,
        "mse_val": mse,
        "mi_val": mi,
        "finite_frac_val": 1.0,
        "expression_raw": expression,
        "expression_simplified": expression,
    }


def test_one_se_envelope_uses_cross_seed_standard_error():
    fronts = {
        0: [_row(2, 5, 0.39), _row(1, 3, 0.40), _row(0, 1, 1.0)],
        1: [_row(2, 5, 0.44), _row(1, 3, 0.45), _row(0, 1, 0.9)],
    }
    result = cms.one_se_readout(fronts)
    assert result["c_min"] == 5
    assert result["complexity"] == 3
    assert result["by_seed"]["0"]["index"] == 1
    assert result["by_seed"]["1"]["index"] == 1


def test_valid_front_ascending_ties_and_domain_filter():
    report = {"all_equations": [
        _row(4, 8, 0.2),
        _row(3, 5, 0.2),
        _row(2, 5, 0.2),
        _row(1, 1, 0.1) | {"finite_frac_val": 0.9},
    ]}
    assert [row["index"] for row in cms.valid_front(report)] == [2, 3, 4]


def _write_fake_report(root, run="demo", latent=0, seed=0, budget=20):
    out = (root / run / f"mse_one_stage_ms{budget}"
           / f"z{latent}_seed{seed}")
    out.mkdir(parents=True)
    report = {
        "inner_loss": "mse",
        "selection_metric": "mse",
        "latent_index": latent,
        "seed": seed,
        "n_fit": 4000,
        "y_mean_train": 1.5,
        "y_std_train": 0.25,
        "target_transform": {
            "kind": "standardize", "fit_rows": [0, 4000],
            "mean": 1.5, "std": 0.25,
        },
        "pysr_kwargs": {"maxsize": budget, "random_state": seed},
        "all_equations": [
            _row(0, 1, 0.8, expression="omega_b"),
            _row(1, 3, 0.2, expression="omega_b + n_s"),
        ],
    }
    (out / "report.json").write_text(json.dumps(report))
    (out / "equations.csv").write_text("complexity,loss,equation\n")
    return out / "report.json"


def _manifest_fixture(tmp_path):
    results = tmp_path / "results"
    report = _write_fake_report(results)
    manifest = cms.build_selection_manifest(
        "demo", results, budgets=[20], seeds=[0], latents=[0],
        include_baselines=False, include_controls=False)
    path = tmp_path / "manifest.json"
    cms.write_immutable_json(path, manifest, "manifest_sha256")
    return report, manifest, path


def test_manifest_freezes_report_equations_and_config(tmp_path):
    report, manifest, path = _manifest_fixture(tmp_path)
    checked = cms.verify_manifest(path)
    assert "git_dirty" in checked
    assert checked["manifest_sha256"] == manifest["manifest_sha256"]
    choice = checked["selections"][0]
    assert choice["index"] == 1
    assert choice["expression"] == "omega_b + n_s"
    assert choice["target_transform"]["mean"] == 1.5
    assert choice["mse_val_native"] == pytest.approx(0.2 * 0.25**2)
    common = checked["common_complexity"]["z0"]
    assert common["complexity_cut"] == 20
    assert common["methods"]["mse20"]["by_seed"]["0"]["index"] == 1

    payload = json.loads(report.read_text())
    payload["all_equations"][1]["mse_val"] = 0.1
    report.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="frozen source changed"):
        cms.verify_manifest(path)


def test_immutable_writer_refuses_different_digest(tmp_path):
    _report, manifest, path = _manifest_fixture(tmp_path)
    changed = dict(manifest)
    changed["created_utc"] = "different"
    changed["manifest_sha256"] = cms.object_sha256(
        {k: v for k, v in changed.items() if k != "manifest_sha256"})
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        cms.write_immutable_json(path, changed, "manifest_sha256")


def test_confirm_verifies_calibration_before_any_tier_load(tmp_path, monkeypatch):
    _report, manifest, manifest_path = _manifest_fixture(tmp_path)
    calibration = {
        "schema_version": 1,
        "kind": "mse_one_stage_calibration",
        "run": "demo",
        "manifest_sha256": manifest["manifest_sha256"],
        "source_files": {
            str(manifest_path.resolve()): cms.file_sha256(manifest_path),
        },
    }
    calibration["calibration_sha256"] = cms.object_sha256(calibration)
    calibration["run"] = "tampered-after-digest"
    calibration_path = tmp_path / "calibration.json"
    calibration_path.write_text(json.dumps(calibration))

    called = False

    def forbidden(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("tier loader called before verification")

    monkeypatch.setattr(cms, "_test_theta", forbidden)
    with pytest.raises(ValueError, match="calibration_sha256 mismatch"):
        cms.confirm_experiment(manifest_path, calibration_path)
    assert not called


def test_reconstruction_metrics_and_f2_incremental_r2():
    rng = np.random.default_rng(8)
    y = rng.normal(size=1000)
    exact = cms.reconstruction_metrics(y, y)
    assert exact["mse"] == pytest.approx(0.0)
    assert exact["r2"] == pytest.approx(1.0)

    f1, f2 = rng.normal(size=800), rng.normal(size=900)
    e1 = 2.0 * f1 + 0.05 * rng.normal(size=len(f1))
    e2 = 2.0 * f2 + 0.05 * rng.normal(size=len(f2))
    audit = cms.f2_incremental_audit(
        e1, e2, f1, f2, seed=0, compute_mi=False)
    assert audit["r2_f2"] > 0.9
    assert audit["T1_crossfit_r2_f2"] > 0.9
    assert audit["absorbed"] is None
    assert audit["status"] == "indeterminate"
    assert "MI audit disabled" in audit["reason"]


def test_ratio_rules_use_the_frozen_strict_and_inclusive_boundaries():
    strict = cms._paired_ratio_rule([1.0] * 5, 1.0, inclusive=False)
    inclusive = cms._paired_ratio_rule([1.0] * 5, 1.0, inclusive=True)
    assert not strict["pass"]
    assert inclusive["pass"]
    assert not cms._paired_ratio_rule([], 1.0)["pass"]


def test_later_tier_domain_failure_invalidates_seed_without_fallback():
    valid = {"valid": True, "finite_frac": 1.0, "mse": 0.2}
    invalid_t1 = {"valid": False, "finite_frac": 0.998}
    domain = cms.decision_domain_status(invalid_t1, valid)
    assert not domain["eligible"]
    assert domain["invalid_tiers"] == ["T1"]
    assert not domain["fallback_used"]
    assert cms._eligible_t2_mse({
        "decision_domain": domain, "T2": valid}) is None

    ratios = cms.paired_ratio_readout(
        {"0": 0.8, "1": 0.8, "2": 0.8, "3": 0.8, "4": None},
        1.0, inclusive=False)
    assert not ratios["pass"]
    assert ratios["status"] == "invalid"
    assert ratios["invalid_seeds"] == ["4"]



def test_confirm_path_runs_only_required_known_f2_mi():
    source = inspect.getsource(cms.confirm_experiment)
    assert "residual_diagnostics_holdout" not in source
    assert "direct_residual_audit" not in source
    assert source.count("compute_mi=") == 1
    assert "compute_mi=compute_known_f2_mi" in source

def test_indeterminate_seed_prevents_aggregate_audit_pass():
    rows = {
        str(seed): {"status": "pass", "absorbed": True}
        for seed in range(4)
    }
    rows["4"] = {"status": "indeterminate", "absorbed": None}
    decision = cms.audit_decision(rows, "absorbed")
    assert decision["n_pass"] == 4
    assert decision["n_indeterminate"] == 1
    assert decision["status"] == "indeterminate"
    assert not decision["pass"]
    incomplete = cms.audit_decision(
        {str(seed): {"status": "pass", "absorbed": True}
         for seed in range(4)}, "absorbed")
    assert incomplete["status"] == "indeterminate"
    assert not incomplete["pass"]


def test_known_f2_is_canonical_additive_not_interaction_aware():
    additive = ("canonical", np.array([1.0]), np.array([2.0]))
    interaction = ("ia", np.array([3.0]), np.array([4.0]))
    assert cms.canonical_known_f2({
        "additive": additive, "interaction_aware": interaction}) is additive
    assert cms.canonical_known_f2({
        "interaction_aware": interaction}) is None


def test_common_complexity_readout_reports_multiple_shared_cuts():
    fronts = {}
    for budget in (20, 40):
        for seed in (0, 1):
            fronts[(0, budget, seed)] = [
                _row(2, 5, 0.2),
                _row(1, 3, 0.4),
                _row(0, 1, 1.0),
            ]
    result = cms.common_complexity_readout(
        fronts, latent=0, budgets=(20, 40), seeds=(0, 1))
    assert [row["complexity_cut"] for row in result["cuts"]] == [1, 3, 5, 20]
    assert set(result["cuts"][1]["methods"]) == {"mse20", "mse40"}
    assert result["complexity_cut"] == 20


def test_classification_does_not_turn_unknown_evidence_into_failure():
    passed = {"status": "pass", "pass": True}
    failed = {"status": "fail", "pass": False}
    unknown = {"status": "indeterminate", "pass": False}
    invalid = {"status": "invalid", "pass": False}
    assert cms.classify_outcome(passed, passed, passed) == (
        "one-stage replacement")
    assert cms.classify_outcome(failed, unknown, unknown) == (
        "no capacity gain")
    assert cms.classify_outcome(passed, failed, passed) == (
        "partial absorption")
    assert cms.classify_outcome(passed, unknown, passed) == "indeterminate"
    assert cms.classify_outcome(invalid, failed, failed) == "indeterminate"


def test_confirmation_markdown_reports_confirmed_one_se_member():
    failed = {"status": "fail", "pass": False}
    payload = {
        "run": "demo",
        "controls": [],
        "latents": [{
            "latent": 0,
            "classification": "indeterminate",
            "flags": [],
            "methods": {},
            "hierarchy": {"interaction_aware": None},
            "known_f2_definition": {"expression": "omega_b"},
            "T0_common_complexity": {},
            "T0_one_se": {"mse20": {
                "metric": "nmse_val", "c_min": 8,
                "complexity": 5, "threshold": 0.2,
                "by_seed": {"0": {"complexity": 5}},
                "confirmed_by_seed": {"0": {
                    "complexity": 5, "expression": "omega_b",
                    "T2": {"mse": 0.1, "nmse": 0.2, "r2": 0.8},
                    "decision_domain": {"eligible": True},
                    "used_for_success_decisions": False,
                }},
            }},
            "decisions": {
                "mse_objective_helps": failed,
                "capacity_helps": failed,
                "known_f2_absorbed": failed,
                "one_stage_matches_interaction_aware": failed,
                "budget_saturated": {"saturated": False},
                "symbolically_stable": {"r_sr": 0.0},
            },
        }],
    }
    markdown = cms.confirmation_markdown(payload)
    assert "T0 one-standard-error readout" in markdown
    assert "One-SE equations are secondary confirmations" in markdown
    assert "| mse20 | 0 | 5 | 0.1 | 0.2 | 0.8 | valid | `omega_b` |" in markdown
