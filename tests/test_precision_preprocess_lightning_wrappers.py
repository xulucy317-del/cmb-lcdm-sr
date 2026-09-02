"""Scheduler-free wrapper contract for precision_preprocess_v1."""
import csv
import os
import pathlib
import subprocess

import pytest


REPO = pathlib.Path(__file__).resolve().parents[1]
CONSOLIDATE = REPO / "hpc" / "lightning" / "run_precision_preprocess_consolidation.sh"
RESUME = REPO / "hpc" / "lightning" / "resume_precision_preprocess.sh"
RUNS = ("lcdm_tt_beta3e-4", "lcdm_tt_ee_lowl")
ARMS = ("raw64", "physical_o1_64", "logamp64")


def _project(tmp_path, pool_pending=0, pool_invalid=0, audit_rc=0):
    python = tmp_path / ".venv-lightning" / "bin" / "python"
    python.parent.mkdir(parents=True, exist_ok=True)
    python.write_text(
        '#!/bin/bash\n'
        'if [[ " $* " == *" --dry-run "* ]]; then\n'
        '  echo "[pool] precision_preprocess: 330/330 complete, '
        '${POOL_PENDING} pending, ${POOL_INVALID} invalid"\n'
        '  echo "[dry-run] ${POOL_PENDING} task(s) would run"\n'
        '  exit "${POOL_AUDIT_RC}"\n'
        'fi\n'
        'printf "%s\\n" "$@"\n'
    )
    python.chmod(0o755)
    env_file = tmp_path / "hpc" / "lightning" / "env.sh"
    env_file.parent.mkdir(parents=True, exist_ok=True)
    env_file.write_text(':\n')
    fake_consolidation = tmp_path / "fake_consolidation.sh"
    fake_consolidation.write_text(
        '#!/bin/bash\nprintf "%s\\t%s\\n" "$1" "${2:-}" >> "${CALLS}"\n')
    fake_consolidation.chmod(0o755)
    return dict(
        os.environ,
        PROJ=str(tmp_path),
        PYTHON=str(python),
        LIGHTNING_ENV=str(env_file),
        POOL_PENDING=str(pool_pending),
        POOL_INVALID=str(pool_invalid),
        POOL_AUDIT_RC=str(audit_rc),
        CONSOLIDATION_SCRIPT=str(fake_consolidation),
        CALLS=str(tmp_path / "calls.tsv"),
    )


def _root(run, arm):
    return f"results/{run}/precision_preprocess_v1/{arm}"


def _touch(tmp_path, relative):
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()


def _consolidation_argv(tmp_path, mode, cell=None, required=()):
    env = _project(tmp_path)
    for path in required:
        _touch(tmp_path, path)
    command = ["bash", str(CONSOLIDATE), mode]
    if cell is not None:
        command.append(str(cell))
    proc = subprocess.run(
        command, cwd=REPO, env=env, text=True, capture_output=True, check=True)
    return [line for line in proc.stdout.splitlines()
            if line and not line.startswith("[consolidate]")]


def test_consolidation_cell_matrix_is_complete():
    proc = subprocess.run(
        ["bash", str(CONSOLIDATE)], cwd=REPO,
        env=dict(os.environ, PRINT_CELLS="1"),
        text=True, capture_output=True, check=True)
    rows = list(csv.DictReader(proc.stdout.splitlines(), delimiter="\t"))
    assert [(row["run"], row["arm"]) for row in rows] == [
        (run, arm) for run in RUNS for arm in ARMS]
    assert len(rows) == len({row["confirmation"] for row in rows}) == 6


@pytest.mark.parametrize("cell", range(6))
def test_select_argv_matches_consolidator_cli(tmp_path, cell):
    run, arm = RUNS[cell // 3], ARMS[cell % 3]
    root = _root(run, arm)
    assert _consolidation_argv(tmp_path, "select", cell) == [
        "scripts/consolidate_precision_preprocess.py", "select",
        "--run", run, "--arm", arm,
        "--results-root", "results",
        "--out", f"{root}/selection_manifest.json",
    ]


def test_calibrate_confirm_and_render_argv(tmp_path):
    root = _root(RUNS[1], ARMS[2])
    manifest = f"{root}/selection_manifest.json"
    calibration = f"{root}/calibration.json"
    baseline = "docs/ols_mi_sr_mse_sr_t2_comparison_codex_output.md"
    assert _consolidation_argv(
        tmp_path / "cal", "calibrate", 5, [manifest]) == [
            "scripts/consolidate_precision_preprocess.py", "calibrate",
            "--manifest", manifest, "--dataset-dir", "data",
            "--models-root", "models", "--out", f"{root}/calibration.json",
        ]
    assert _consolidation_argv(
        tmp_path / "confirm", "confirm", 5,
        [manifest, calibration, baseline]) == [
            "scripts/consolidate_precision_preprocess.py", "confirm",
            "--manifest", manifest, "--calibration", calibration,
            "--dataset-dir", "data", "--models-root", "models",
            "--experiments-dir", "experiments",
            "--baseline-report", baseline,
            "--out", f"{root}/confirmation.json",
        ]

    confirmations = [
        f"{_root(run, arm)}/confirmation.json"
        for run in RUNS for arm in ARMS]
    argv = _consolidation_argv(
        tmp_path / "render", "render", required=confirmations)
    start = argv.index("--confirmations") + 1
    stop = argv.index("--out-json")
    assert argv[start:stop] == confirmations
    assert argv[stop:] == [
        "--out-json", "experiments/precision_preprocess_v1_comparison.json",
        "--out-md", "docs/precision_preprocess_v1_comparison.md",
    ]


def test_consolidation_guards_inputs_and_cells(tmp_path):
    env = _project(tmp_path)
    missing = subprocess.run(
        ["bash", str(CONSOLIDATE), "calibrate", "0"], cwd=REPO,
        env=env, text=True, capture_output=True)
    assert missing.returncode == 2
    assert "required frozen artifact is missing" in missing.stderr
    invalid = subprocess.run(
        ["bash", str(CONSOLIDATE), "select", "6"], cwd=REPO,
        env=env, text=True, capture_output=True)
    assert invalid.returncode == 2


def test_resume_defaults_pool_then_runs_four_strict_stages(tmp_path):
    env = _project(tmp_path)
    proc = subprocess.run(
        ["bash", str(RESUME)], cwd=REPO, env=env,
        text=True, capture_output=True, check=True)
    assert "--workers\n2\n--threads\n2\n--ledger\nlogs/precision_preprocess_pool_ledger.jsonl" \
        in proc.stdout
    calls = (tmp_path / "calls.tsv").read_text().splitlines()
    assert calls == (
        [f"select\t{cell}" for cell in range(6)]
        + [f"calibrate\t{cell}" for cell in range(6)]
        + [f"confirm\t{cell}" for cell in range(6)]
        + ["render\t"]
    )


@pytest.mark.parametrize(
    ("pending", "invalid", "audit_rc", "needle"),
    [
        (1, 0, 0, "consolidation is gated"),
        (0, 1, 0, "invalid report(s)"),
        (0, 0, 3, "pool dry-run failed"),
    ],
)
def test_resume_never_consolidates_unless_audit_is_clean(
        tmp_path, pending, invalid, audit_rc, needle):
    env = _project(tmp_path, pending, invalid, audit_rc)
    proc = subprocess.run(
        ["bash", str(RESUME)], cwd=REPO, env=env,
        text=True, capture_output=True)
    assert needle in (proc.stdout + proc.stderr)
    assert not (tmp_path / "calls.tsv").exists()


def test_resume_passes_budget_and_overrides(tmp_path):
    env = _project(tmp_path, pool_pending=1)
    env.update(WORKERS="1", THREADS="4", TIME_BUDGET_MINUTES="210")
    proc = subprocess.run(
        ["bash", str(RESUME)], cwd=REPO, env=env,
        text=True, capture_output=True, check=True)
    assert "--workers\n1\n--threads\n4" in proc.stdout
    assert "--time-budget-minutes\n210" in proc.stdout


def test_lightning_wrappers_have_valid_bash_syntax():
    for path in (CONSOLIDATE, RESUME):
        subprocess.run(["bash", "-n", str(path)], check=True)
