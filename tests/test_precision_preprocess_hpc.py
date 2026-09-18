"""Frozen matrix and resume contract for the precision/preprocessing array."""
import csv
import json
import os
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
LAUNCHER = REPO / "hpc" / "slurm_precision_preprocess_v1.sh"


def _matrix():
    env = dict(
        os.environ,
        PRINT_MATRIX="1",
        ACCOUNT="MPHIL-DIS-SL2-CPU",
        SLURM_JOB_ACCOUNT="mphil-dis-sl2-cpu",
    )
    proc = subprocess.run(
        ["bash", str(LAUNCHER)], cwd=REPO, env=env, check=True,
        text=True, capture_output=True)
    return list(csv.DictReader(proc.stdout.splitlines(), delimiter="\t"))


def _python_project(tmp_path):
    python = tmp_path / ".venv" / "bin" / "python"
    python.parent.mkdir(parents=True)
    python.symlink_to(sys.executable)
    return tmp_path


def _task_env(tmp_path, task_id):
    return dict(
        os.environ,
        PROJ=str(_python_project(tmp_path)),
        SLURM_ARRAY_TASK_ID=str(task_id),
        SLURM_ARRAY_JOB_ID="98765",
        SLURM_CPUS_PER_TASK="16",
        SLURM_RESTART_COUNT="0",
        PACKED="1",
        ACCOUNT="MPHIL-DIS-SL2-CPU",
        SLURM_JOB_ACCOUNT="mphil-dis-sl2-cpu",
    )


def _valid_report(row):
    n_samples = 5000
    selection = row["selection_metric"]
    posthoc = row["posthoc_mi"]
    labels = ["x0", "x1", "x2", "x3", "x4", "x5"]
    return {
        "run_dir": row["run_dir"],
        "regime": pathlib.Path(row["run_dir"]).name,
        "latent_index": int(row["latent"]),
        "target_npy": None,
        "input_config": row["arm"],
        "input_names": ["a", "b", "c", "d", "e", "f"],
        "input_labels": labels,
        "input_sampled_expressions": {label: label for label in labels},
        "extra_inputs": [],
        "n_samples": n_samples,
        "n_fit": 4000,
        "n_val": 1000,
        "inner_loss": row["inner_loss"],
        "selection_metric": selection,
        "selection_direction": "descending" if selection == "mi" else "ascending",
        "posthoc_mi_mode": posthoc,
        "posthoc_mi_status": (
            "computed" if posthoc == "full" else "skipped_not_selected"),
        "ols_baseline": {
            "status": "skipped",
            "reason": "fixed_old_ols_reused_downstream",
        },
        "seed": int(row["seed"]),
        "pysr_kwargs": {
            "niterations": 200,
            "populations": 15,
            "maxsize": int(row["maxsize"]),
            "binary_operators": ["+", "*", "-", "/"],
            "unary_operators": ["exp", "log", "neg", "square"],
            "parallelism": "multithreading",
            "random_state": int(row["seed"]),
            "run_id": "run_123",
            "precision": 64,
            "print_precision": 17,
        },
        "n_equations": 1,
        "all_equations": [{"index": 0}],
        "best_expression": "x0",
        "best_mi_val": 1.0,
        "best_mse_val": 0.1,
    }


def test_matrix_is_complete_unique_and_has_frozen_block_order():
    rows = _matrix()
    assert len(rows) == 330
    keys = {
        (r["run_dir"], r["arm"], r["inner_loss"], int(r["latent"]), int(r["seed"]))
        for r in rows
    }
    assert len(keys) == 330
    assert {r["arm"] for r in rows} == {"raw64", "physical_o1_64", "logamp64"}
    assert {int(r["seed"]) for r in rows} == set(range(5))

    expected_blocks = [
        (0, 54, "raw64", "gmm_mi", "mi", "full", 20),
        (55, 109, "raw64", "mse", "mse", "none", 40),
        (110, 164, "physical_o1_64", "gmm_mi", "mi", "full", 20),
        (165, 219, "physical_o1_64", "mse", "mse", "none", 40),
        (220, 274, "logamp64", "gmm_mi", "mi", "full", 20),
        (275, 329, "logamp64", "mse", "mse", "none", 40),
    ]
    for lo, hi, arm, loss, selector, posthoc, maxsize in expected_blocks:
        block = rows[lo:hi + 1]
        assert {r["arm"] for r in block} == {arm}
        assert {r["inner_loss"] for r in block} == {loss}
        assert {r["selection_metric"] for r in block} == {selector}
        assert {r["posthoc_mi"] for r in block} == {posthoc}
        assert {int(r["maxsize"]) for r in block} == {maxsize}

    for block in (rows[0:55], rows[55:110], rows[110:165],
                  rows[165:220], rows[220:275], rows[275:330]):
        tt = [r for r in block if r["run_dir"].endswith("lcdm_tt_beta3e-4")]
        ee = [r for r in block if r["run_dir"].endswith("lcdm_tt_ee_lowl")]
        assert len(tt) == 25 and {int(r["latent"]) for r in tt} == set(range(5))
        assert len(ee) == 30 and {int(r["latent"]) for r in ee} == set(range(6))


def test_paths_are_unique_and_do_not_collide_with_prior_studies():
    rows = _matrix()
    paths = [r["out_dir"] for r in rows]
    assert len(paths) == len(set(paths)) == 330
    for row in rows:
        expected = (
            f"results/{pathlib.Path(row['run_dir']).name}/precision_preprocess_v1/"
            f"{row['arm']}/{row['family']}/z{row['latent']}_seed{row['seed']}"
        )
        assert row["out_dir"] == expected
        assert "/allparams/" not in expected
        assert "/mse_one_stage_" not in expected


def test_launcher_resources_and_profile_only_cli_contract():
    text = LAUNCHER.read_text()
    assert "#SBATCH --array=0-329%16" in text
    assert "#SBATCH --time=02:00:00" in text
    assert "#SBATCH --cpus-per-task=16" in text
    assert "#SBATCH --mem=16G" in text
    assert "#SBATCH --partition=icelake" in text
    assert "#SBATCH --account=MPHIL-DIS-SL2-CPU" in text
    assert 'DEFAULT_ACCOUNT="MPHIL-DIS-SL2-CPU"' in text
    assert 'ACCOUNT="${ACCOUNT:-${DEFAULT_ACCOUNT}}"' in text
    assert "^[A-Za-z0-9_.-]+$" in text
    # case-insensitive account guard, spelled portably (bash 3.2 has no ${var,,})
    assert ("\"$(printf '%s' \"${SLURM_JOB_ACCOUNT}\" | tr '[:upper:]' '[:lower:]')\" != \\\n"
            "      \"$(printf '%s' \"${ACCOUNT}\" | tr '[:upper:]' '[:lower:]')\"") in text
    assert 'account=${ACCOUNT}' in text
    assert "#SBATCH --qos" not in text
    assert "source ~/.bashrc" not in text
    assert 'PYTHON="${PROJ}/.venv/bin/python"' in text
    assert 'PYTHON_JULIAPKG_PROJECT="${PROJ}/.venv/julia_env"' in text
    assert '--input-config "${ARM}"' in text
    assert "--skip-ols-baseline" in text
    assert "--inputs" not in text
    assert "--pysr-extra" not in text
    assert '"precision": 64' in text
    assert '"print_precision": 17' in text


@pytest.mark.parametrize(
    ("account", "job_account", "message"),
    [
        ("unsafe/account", "unsafe/account", "unsafe ACCOUNT value"),
        ("different-account", "mphil-dis-sl2-cpu",
         "does not match SLURM_JOB_ACCOUNT"),
    ],
)
def test_account_guard_fails_closed(account, job_account, message):
    env = dict(
        os.environ,
        PRINT_MATRIX="1",
        ACCOUNT=account,
        SLURM_JOB_ACCOUNT=job_account,
    )
    proc = subprocess.run(
        ["bash", str(LAUNCHER)], cwd=REPO, env=env,
        text=True, capture_output=True)
    assert proc.returncode == 2
    assert message in proc.stderr


@pytest.mark.parametrize("task_id", [0, 54, 55, 109, 110, 164, 165,
                                     219, 220, 274, 275, 329])
def test_valid_existing_report_is_skipped(tmp_path, task_id):
    row = _matrix()[task_id]
    report = tmp_path / row["out_dir"] / "report.json"
    report.parent.mkdir(parents=True)
    report.write_text(json.dumps(_valid_report(row)))

    proc = subprocess.run(
        ["bash", str(LAUNCHER)], cwd=REPO,
        env=_task_env(tmp_path, task_id), text=True, capture_output=True,
        check=True)
    assert "[skip] validated" in proc.stdout


@pytest.mark.parametrize(
    "mutation",
    [
        {"input_config": "raw64"},
        {"seed": 4},
        {"latent_index": 4},
        {"inner_loss": "mse"},
        {"selection_metric": "mse"},
        {"best_expression": ""},
        {"input_sampled_expressions": {}},
        {"ols_baseline": None},
        {"ols_baseline": {
            "status": "computed",
            "reason": "fixed_old_ols_reused_downstream",
        }},
        {"ols_baseline": {
            "status": "skipped",
            "reason": "wrong_reason",
        }},
        {"pysr_kwargs": {"precision": 32}},
    ],
)
def test_mismatched_existing_report_fails_closed(tmp_path, mutation):
    task_id = 110  # physical_o1_64, GMM-MI, TT z0 seed0
    row = _matrix()[task_id]
    payload = _valid_report(row)
    if "pysr_kwargs" in mutation:
        payload["pysr_kwargs"].update(mutation["pysr_kwargs"])
    else:
        payload.update(mutation)
    report = tmp_path / row["out_dir"] / "report.json"
    report.parent.mkdir(parents=True)
    report.write_text(json.dumps(payload))

    proc = subprocess.run(
        ["bash", str(LAUNCHER)], cwd=REPO,
        env=_task_env(tmp_path, task_id), text=True, capture_output=True)
    assert proc.returncode == 2
    assert "existing report failed task validation" in proc.stdout


def test_smoke_command_uses_separate_namespace_and_reduced_work(tmp_path):
    shim = tmp_path / ".venv" / "bin" / "python"
    shim.parent.mkdir(parents=True)
    shim.write_text('#!/bin/bash\nprintf "%s\\n" "$@"\n')
    shim.chmod(0o755)
    env = dict(
        os.environ,
        PROJ=str(tmp_path),
        SLURM_ARRAY_TASK_ID="275",
        SLURM_ARRAY_JOB_ID="smoke123",
        SLURM_CPUS_PER_TASK="16",
        SMOKE="1",
        PACKED="1",
        ACCOUNT="Campaign-Account",
        SLURM_JOB_ACCOUNT="campaign-account",
    )
    proc = subprocess.run(
        ["bash", str(LAUNCHER)], cwd=REPO, env=env,
        text=True, capture_output=True, check=True)
    assert "[run] account=Campaign-Account" in proc.stdout
    argv = [line for line in proc.stdout.splitlines() if line.strip()]
    assert "scripts/run_blind_sr.py" in argv
    assert argv[argv.index("--input-config") + 1] == "logamp64"
    assert argv[argv.index("--inner-loss") + 1] == "mse"
    assert argv[argv.index("--maxsize") + 1] == "40"
    assert argv[argv.index("--n-samples") + 1] == "500"
    assert argv[argv.index("--niterations") + 1] == "1"
    assert "--skip-ols-baseline" in argv
    out_dir = argv[argv.index("--out-dir") + 1]
    assert "precision_preprocess_v1_smoke_smoke123" in out_dir
    assert "/precision_preprocess_v1/" not in out_dir


def test_launcher_has_valid_bash_syntax():
    subprocess.run(["bash", "-n", str(LAUNCHER)], check=True)
