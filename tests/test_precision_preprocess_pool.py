"""Scheduler-free precision/preprocessing pool contracts."""
import csv
import json
import os
import pathlib
import subprocess
import sys

import pytest


REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_precision_preprocess_pool as pool  # noqa: E402


SAMPLE_IDS = [0, 54, 55, 109, 110, 164, 165, 219, 220, 274, 275, 329]


def _launcher_argv(tmp_path, task_id):
    python = tmp_path / ".venv" / "bin" / "python"
    python.parent.mkdir(parents=True, exist_ok=True)
    python.write_text('#!/bin/bash\nprintf "%s\\n" "$@"\n')
    python.chmod(0o755)
    env = dict(
        os.environ,
        PROJ=str(tmp_path),
        SLURM_ARRAY_TASK_ID=str(task_id),
        SLURM_ARRAY_JOB_ID="98765",
        SLURM_CPUS_PER_TASK="16",
        SLURM_RESTART_COUNT="0",
        PACKED="1",
        ACCOUNT="MPHIL-DIS-SL2-CPU",
        SLURM_JOB_ACCOUNT="mphil-dis-sl2-cpu",
    )
    proc = subprocess.run(
        ["bash", str(pool.LAUNCHER)], cwd=REPO, env=env, check=True,
        text=True, capture_output=True,
    )
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    start = lines.index("scripts/run_blind_sr.py")
    return lines[start + 1:]


def _without_run_id(argv):
    result = []
    skip = False
    for token in argv:
        if skip:
            skip = False
        elif token == "--pysr-run-id":
            skip = True
        else:
            result.append(token)
    return result


def _valid_report(task):
    profile = pool.PROFILE_CONTRACTS[task["arm"]]
    n_samples = task["n_samples"]
    n_val = round(n_samples * 0.2)
    n_fit = n_samples - n_val
    best_mi = 1.2 if task["selection_metric"] == "mi" else None
    equation = {
        "index": 0,
        "expression_simplified": profile["inputs"][0],
        "mse_val": 0.1,
        "mi_val": best_mi,
    }
    return {
        "run_dir": task["run_dir"],
        "regime": task["run"],
        "latent_index": task["latent"],
        "target_npy": None,
        "target_label": f"z{task['latent']}",
        "input_config": task["arm"],
        "input_names": profile["inputs"],
        "input_labels": profile["inputs"],
        "input_sampled_expressions": profile["sampled_expressions"],
        "extra_inputs": [],
        "n_samples": n_samples,
        "n_fit": n_fit,
        "n_val": n_val,
        "target_transform": {
            "kind": "standardize", "fit_rows": [0, n_fit],
            "mean": 0.2, "std": 1.1,
        },
        "inner_loss": task["inner_loss"],
        "selection_metric": task["selection_metric"],
        "selection_direction": (
            "descending" if task["selection_metric"] == "mi" else "ascending"
        ),
        "posthoc_mi_mode": task["posthoc_mi"],
        "posthoc_mi_status": (
            "computed" if task["posthoc_mi"] == "full"
            else "skipped_not_selected"
        ),
        "seed": task["seed"],
        "ols_baseline": {
            "status": "skipped",
            "reason": "fixed_old_ols_reused_downstream",
        },
        "pysr_kwargs": {
            "niterations": task["niterations"],
            "populations": task["populations"],
            "maxsize": task["maxsize"],
            "binary_operators": ["+", "*", "-", "/"],
            "unary_operators": ["exp", "log", "neg", "square"],
            "parallelism": "multithreading",
            "random_state": task["seed"],
            "run_id": "run_0",
            "pysr_version": "1.5.10",
            "precision": 64,
            "print_precision": 17,
        },
        "fit_seconds": 10.0,
        "n_equations": 1,
        "all_equations": [equation],
        "top5": [equation],
        "top5_ranked_by": f"VAL {task['selection_metric'].upper()} (primary)",
        "best_index": 0,
        "best_expression": equation["expression_simplified"],
        "best_mse_val": 0.1,
        "best_mi_val": best_mi,
    }


def test_matrix_is_read_from_frozen_launcher():
    rows = pool.read_matrix()
    assert len(rows) == pool.TOTAL_TASKS == 330
    assert [int(row["task_id"]) for row in rows] == list(range(330))
    assert len({row["out_dir"] for row in rows}) == 330


@pytest.mark.parametrize("task_id", SAMPLE_IDS)
def test_pool_rebuilds_exact_launcher_runner_argv(tmp_path, task_id):
    row = pool.read_matrix()[task_id]
    task = pool.build_task(row)
    assert task["argv"] == _without_run_id(_launcher_argv(tmp_path, task_id))
    assert "--input-config" in task["argv"]
    assert "--skip-ols-baseline" in task["argv"]
    assert "--pysr-extra" not in task["argv"]


def test_profile_contracts_match_the_runtime_registry():
    sys.path.insert(0, str(REPO / "src"))
    from cmb_lcdm_sr.sr import resolve_input_config

    for name, expected in pool.PROFILE_CONTRACTS.items():
        actual = resolve_input_config(name)
        assert actual["inputs"] == expected["inputs"]
        assert actual["sampled_expressions"] == expected["sampled_expressions"]
        assert actual["pysr_kwargs"] == {"precision": 64, "print_precision": 17}


def test_smoke_is_isolated_and_reduced():
    row = pool.read_matrix()[275]
    task = pool.build_task(row, "lightning1")
    assert "precision_preprocess_v1_smoke_lightning1" in task["out_dir"]
    assert "/precision_preprocess_v1/" not in task["out_dir"]
    assert task["n_samples"] == 500
    assert task["niterations"] == 1
    assert task["populations"] == 2
    assert task["argv"][task["argv"].index("--input-config") + 1] == "logamp64"


@pytest.mark.parametrize("task_id", [0, 55, 110, 165, 220, 275, 329])
def test_strict_report_validation_accepts_each_arm_and_objective(tmp_path, task_id):
    task = pool.build_task(pool.read_matrix()[task_id])
    path = tmp_path / "report.json"
    path.write_text(json.dumps(_valid_report(task)))
    assert pool.validate_report(path, task) == (True, "ok")


@pytest.mark.parametrize(
    "mutation",
    [
        {"input_config": "raw64"},
        {"seed": 4},
        {"latent_index": 4},
        {"n_samples": 4999},
        {"inner_loss": "mse"},
        {"selection_metric": "mse"},
        {"input_sampled_expressions": {}},
        {"best_expression": ""},
        {"best_mi_val": None},
        {"fit_seconds": None},
        {"ols_baseline": {"status": "computed"}},
    ],
)
def test_strict_report_validation_rejects_identity_or_result_drift(
        tmp_path, mutation):
    task = pool.build_task(pool.read_matrix()[110])
    payload = _valid_report(task)
    payload.update(mutation)
    path = tmp_path / "report.json"
    path.write_text(json.dumps(payload))
    valid, reason = pool.validate_report(path, task)
    assert not valid
    assert reason.startswith("failed checks:")


@pytest.mark.parametrize(
    "key,value",
    [
        ("precision", 32),
        ("print_precision", 8),
        ("random_state", 4),
        ("maxsize", 40),
        ("parallelism", "serial"),
        ("run_id", ""),
    ],
)
def test_strict_report_validation_rejects_pysr_drift(tmp_path, key, value):
    task = pool.build_task(pool.read_matrix()[110])
    payload = _valid_report(task)
    payload["pysr_kwargs"][key] = value
    path = tmp_path / "report.json"
    path.write_text(json.dumps(payload))
    assert not pool.validate_report(path, task)[0]


def test_resume_skips_only_valid_reports(monkeypatch, tmp_path):
    task = pool.build_task(pool.read_matrix()[110], "resume_test")
    monkeypatch.setattr(pool, "REPO", tmp_path)
    report = tmp_path / task["out_dir"] / "report.json"
    assert pool.task_status(task) == ("pending", "no report.json")
    report.parent.mkdir(parents=True)
    report.write_text(json.dumps(_valid_report(task)))
    assert pool.task_status(task) == ("done", "ok")
    payload = _valid_report(task)
    payload["pysr_kwargs"]["precision"] = 32
    report.write_text(json.dumps(payload))
    status, reason = pool.task_status(task)
    assert status == "invalid"
    assert "pysr_kwargs.precision" in reason


def test_interrupted_attempt_gets_a_new_unique_run_id(monkeypatch, tmp_path):
    task = pool.build_task(pool.read_matrix()[0], "runid_test")
    monkeypatch.setattr(pool, "REPO", tmp_path)
    state = tmp_path / task["out_dir"] / "pysr_state"
    (state / "run_0").mkdir(parents=True)
    (state / "run_1").mkdir()
    assert pool.next_run_id(task) == "run_2"
    argv = pool.runner_argv(task)
    assert argv[-2:] == ["--pysr-run-id", "run_2"]
    assert argv.count("--pysr-run-id") == 1


def test_cli_supports_scheduler_free_resume_controls():
    args = pool.make_parser().parse_args([
        "--task-ids", "0-5,110", "--workers", "2", "--threads", "2",
        "--time-budget-minutes", "210", "--smoke", "check1", "--dry-run",
    ])
    assert pool.parse_ids(args.task_ids) == {*range(6), 110}
    assert (args.workers, args.threads) == (2, 2)
    assert args.time_budget_minutes == 210
    assert args.smoke == "check1"
    assert args.dry_run
    assert pool.DEFAULT_LEDGER == "logs/precision_preprocess_pool_ledger.jsonl"


def test_multiprocessing_start_method_is_spawn_on_macos(monkeypatch):
    monkeypatch.setattr(pool.platform, "system", lambda: "Darwin")
    assert pool.multiprocessing_start_method() == "spawn"
    monkeypatch.setattr(pool.platform, "system", lambda: "Linux")
    assert pool.multiprocessing_start_method() == "fork"


def test_pool_script_has_valid_python_syntax_and_distinct_namespaces():
    subprocess.run([sys.executable, "-m", "py_compile", str(pool.__file__)],
                   check=True)
    text = pathlib.Path(pool.__file__).read_text()
    assert "mse_one_stage_pool_ledger" not in text
    assert "precision_preprocess_pool_ledger" in text
    assert "precision_preprocess_pool_" in text
