"""Slurm staging contract for precision/preprocessing consolidation."""
import csv
import os
import pathlib
import subprocess

import pytest


REPO = pathlib.Path(__file__).resolve().parents[1]
LAUNCHER = REPO / "hpc" / "slurm_precision_preprocess_consolidate.sh"
RUNS = ("lcdm_tt_beta3e-4", "lcdm_tt_ee_lowl")
ARMS = ("raw64", "physical_o1_64", "logamp64")


def _project(tmp_path):
    python = tmp_path / ".venv" / "bin" / "python"
    python.parent.mkdir(parents=True, exist_ok=True)
    python.write_text('#!/bin/bash\nprintf "%s\\n" "$@"\n')
    python.chmod(0o755)
    return tmp_path


def _env(tmp_path, **updates):
    env = dict(
        os.environ,
        PROJ=str(_project(tmp_path)),
        ACCOUNT="MPHIL-DIS-SL2-CPU",
        SLURM_JOB_ACCOUNT="mphil-dis-sl2-cpu",
    )
    env.update({key: str(value) for key, value in updates.items()})
    return env


def _root(run, arm):
    return f"results/{run}/precision_preprocess_v1/{arm}"


def _touch(tmp_path, relative):
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()


def _run(tmp_path, mode, cell=None, required=()):
    for path in required:
        _touch(tmp_path, path)
    updates = {}
    if cell is not None:
        updates["SLURM_ARRAY_TASK_ID"] = cell
    proc = subprocess.run(
        ["bash", str(LAUNCHER), mode], cwd=REPO,
        env=_env(tmp_path, **updates), text=True, capture_output=True,
        check=True,
    )
    return [line for line in proc.stdout.splitlines()
            if line and not line.startswith("[consolidate]")]


def test_cell_matrix_is_complete_and_frozen():
    proc = subprocess.run(
        ["bash", str(LAUNCHER)], cwd=REPO,
        env=dict(os.environ, PRINT_CELLS="1"),
        text=True, capture_output=True, check=True,
    )
    rows = list(csv.DictReader(proc.stdout.splitlines(), delimiter="\t"))
    assert [int(row["cell"]) for row in rows] == list(range(6))
    assert [(row["run"], row["arm"]) for row in rows] == [
        (run, arm) for run in RUNS for arm in ARMS
    ]
    assert len({row["confirmation"] for row in rows}) == 6
    for row in rows:
        root = _root(row["run"], row["arm"])
        assert row["manifest"] == f"{root}/selection_manifest.json"
        assert row["calibration"] == f"{root}/calibration.json"
        assert row["confirmation"] == f"{root}/confirmation.json"


def test_resources_dependencies_and_account_contract_are_explicit():
    text = LAUNCHER.read_text()
    assert "#SBATCH --time=24:00:00" in text
    assert "#SBATCH --cpus-per-task=1" in text
    assert "#SBATCH --mem=32G" in text
    assert "#SBATCH --partition=icelake" in text
    assert "#SBATCH --account=MPHIL-DIS-SL2-CPU" in text
    assert "DEFAULT_ACCOUNT=\"MPHIL-DIS-SL2-CPU\"" in text
    assert "SLURM_JOB_ACCOUNT" in text
    assert "OMP_NUM_THREADS=1" in text
    assert "OPENBLAS_NUM_THREADS=1" in text
    assert "--dependency=afterok:${SEARCH_JID}" in text
    assert "--dependency=afterok:${SELECT_JID}" in text
    assert "--dependency=afterok:${CALIBRATE_JID}" in text
    assert "--dependency=afterok:${CONFIRM_JID}" in text


@pytest.mark.parametrize("cell", range(6))
def test_select_argv_for_every_cell(tmp_path, cell):
    run = RUNS[cell // 3]
    arm = ARMS[cell % 3]
    root = _root(run, arm)
    argv = _run(tmp_path, "select", cell)
    assert argv == [
        "scripts/consolidate_precision_preprocess.py", "select",
        "--run", run,
        "--arm", arm,
        "--results-root", "results",
        "--out", f"{root}/selection_manifest.json",
    ]


def test_calibrate_argv_and_manifest_guard(tmp_path):
    run, arm = RUNS[0], ARMS[1]
    root = _root(run, arm)
    manifest = f"{root}/selection_manifest.json"
    argv = _run(tmp_path, "calibrate", 1, required=[manifest])
    assert argv == [
        "scripts/consolidate_precision_preprocess.py", "calibrate",
        "--manifest", manifest,
        "--dataset-dir", "data",
        "--models-root", "models",
        "--out", f"{root}/calibration.json",
    ]

    missing = subprocess.run(
        ["bash", str(LAUNCHER), "calibrate"], cwd=REPO,
        env=_env(tmp_path / "missing", SLURM_ARRAY_TASK_ID=1),
        text=True, capture_output=True,
    )
    assert missing.returncode == 2
    assert "required frozen artifact is missing" in missing.stderr


def test_confirm_argv_and_frozen_inputs(tmp_path):
    run, arm = RUNS[1], ARMS[2]
    root = _root(run, arm)
    manifest = f"{root}/selection_manifest.json"
    calibration = f"{root}/calibration.json"
    baseline = "docs/ols_mi_sr_mse_sr_t2_comparison_codex_output.md"
    argv = _run(
        tmp_path, "confirm", 5,
        required=[manifest, calibration, baseline],
    )
    assert argv == [
        "scripts/consolidate_precision_preprocess.py", "confirm",
        "--manifest", manifest,
        "--calibration", calibration,
        "--dataset-dir", "data",
        "--models-root", "models",
        "--experiments-dir", "experiments",
        "--baseline-report", baseline,
        "--out", f"{root}/confirmation.json",
    ]


def test_render_consumes_exactly_all_six_confirmations(tmp_path):
    confirmations = [
        f"{_root(run, arm)}/confirmation.json"
        for run in RUNS for arm in ARMS
    ]
    argv = _run(tmp_path, "render", required=confirmations)
    assert argv[:2] == [
        "scripts/consolidate_precision_preprocess.py", "render"]
    start = argv.index("--confirmations") + 1
    stop = argv.index("--out-json")
    assert argv[start:stop] == confirmations
    assert argv[stop:] == [
        "--out-json", "experiments/precision_preprocess_v1_comparison.json",
        "--out-md", "docs/precision_preprocess_v1_comparison.md",
    ]
    assert not any("mse_one_stage_sr_" in value for value in argv)


@pytest.mark.parametrize("cell", ["-1", "6", "bad"])
def test_invalid_cell_fails_closed(tmp_path, cell):
    proc = subprocess.run(
        ["bash", str(LAUNCHER), "select"], cwd=REPO,
        env=_env(tmp_path, SLURM_ARRAY_TASK_ID=cell),
        text=True, capture_output=True,
    )
    assert proc.returncode == 2
    assert "invalid cell" in proc.stderr


def test_cell_sources_and_account_must_agree(tmp_path):
    proc = subprocess.run(
        ["bash", str(LAUNCHER), "select"], cwd=REPO,
        env=_env(
            tmp_path, CELL_ID=0, SLURM_ARRAY_TASK_ID=1,
            ACCOUNT="different-account",
        ),
        text=True, capture_output=True,
    )
    assert proc.returncode == 2
    assert "does not match SLURM_JOB_ACCOUNT" in proc.stderr

    proc = subprocess.run(
        ["bash", str(LAUNCHER), "select"], cwd=REPO,
        env=_env(tmp_path / "cell", CELL_ID=0, SLURM_ARRAY_TASK_ID=1),
        text=True, capture_output=True,
    )
    assert proc.returncode == 2
    assert "disagrees with SLURM_ARRAY_TASK_ID" in proc.stderr


def test_render_rejects_array_context(tmp_path):
    proc = subprocess.run(
        ["bash", str(LAUNCHER), "render"], cwd=REPO,
        env=_env(tmp_path, SLURM_ARRAY_TASK_ID=0),
        text=True, capture_output=True,
    )
    assert proc.returncode == 2
    assert "render is a single job" in proc.stderr


def test_launcher_has_valid_bash_syntax():
    subprocess.run(["bash", "-n", str(LAUNCHER)], check=True)
