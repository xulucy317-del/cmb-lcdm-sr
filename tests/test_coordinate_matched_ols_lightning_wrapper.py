"""Contract tests for the scheduler-free coordinate-matched OLS audit."""
import csv
import os
import pathlib
import subprocess

import pytest


REPO = pathlib.Path(__file__).resolve().parents[1]
WRAPPER = REPO / "hpc" / "lightning" / "run_coordinate_matched_ols_audit.sh"
RUNS = ("lcdm_tt_beta3e-4", "lcdm_tt_ee_lowl")
ARMS = ("raw64", "physical_o1_64", "logamp64")


def _project(tmp_path):
    python = tmp_path / ".venv-lightning" / "bin" / "python"
    python.parent.mkdir(parents=True, exist_ok=True)
    python.write_text(
        "#!/bin/bash\n"
        "printf '%s\\n' \"$@\"\n"
        "if [[ -n \"${CALLS:-}\" ]]; then\n"
        "  printf '%s' \"$1\" >> \"${CALLS}\"\n"
        "  for arg in \"${@:2}\"; do printf '\\t%s' \"${arg}\" >> \"${CALLS}\"; done\n"
        "  printf '\\n' >> \"${CALLS}\"\n"
        "fi\n"
        "args=(\"$@\")\n"
        "for ((i=0; i<${#args[@]}; i++)); do\n"
        "  case \"${args[$i]}\" in\n"
        "    --out|--out-json|--out-md)\n"
        "      path=\"${args[$((i+1))]}\"\n"
        "      mkdir -p \"$(dirname \"${path}\")\"\n"
        "      : > \"${path}\"\n"
        "      ;;\n"
        "  esac\n"
        "done\n"
    )
    python.chmod(0o755)
    env_file = tmp_path / "hpc" / "lightning" / "env.sh"
    env_file.parent.mkdir(parents=True, exist_ok=True)
    env_file.write_text(":\n")
    auditor = tmp_path / "scripts" / "audit_coordinate_matched_ols.py"
    auditor.parent.mkdir(parents=True, exist_ok=True)
    auditor.touch()
    return dict(
        os.environ,
        PROJ=str(tmp_path),
        PYTHON=str(python),
        LIGHTNING_ENV=str(env_file),
        AUDITOR=str(auditor),
        CALLS=str(tmp_path / "calls.tsv"),
    )


def _precision_root(run, arm):
    return f"results/{run}/precision_preprocess_v1/{arm}"


def _audit_root(run, arm):
    return f"results/{run}/coordinate_matched_ols_v1/{arm}"


def _touch(tmp_path, relative, text=""):
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def _argv(tmp_path, mode, cell=None, required=()):
    env = _project(tmp_path)
    for path in required:
        _touch(tmp_path, path)
    command = ["bash", str(WRAPPER), mode]
    if cell is not None:
        command.append(str(cell))
    proc = subprocess.run(
        command, cwd=REPO, env=env, text=True, capture_output=True,
        check=True,
    )
    return [line for line in proc.stdout.splitlines()
            if line and not line.startswith("[ols-audit]")]


def test_cell_matrix_is_complete_and_paths_are_disjoint():
    proc = subprocess.run(
        ["bash", str(WRAPPER)], cwd=REPO,
        env=dict(os.environ, PRINT_CELLS="1"), text=True,
        capture_output=True, check=True,
    )
    rows = list(csv.DictReader(proc.stdout.splitlines(), delimiter="\t"))
    assert [(row["run"], row["arm"]) for row in rows] == [
        (run, arm) for run in RUNS for arm in ARMS]
    assert len(rows) == 6
    for row in rows:
        upstream = _precision_root(row["run"], row["arm"])
        audit = _audit_root(row["run"], row["arm"])
        assert row["precision_manifest"] == f"{upstream}/selection_manifest.json"
        assert row["precision_calibration"] == f"{upstream}/calibration.json"
        assert row["precision_confirmation"] == f"{upstream}/confirmation.json"
        assert row["fit"] == f"{audit}/fit.json"
        assert row["calibration"] == f"{audit}/calibration.json"
        assert row["confirmation"] == f"{audit}/confirmation.json"
        assert "coordinate_matched_ols_v1" not in row["precision_manifest"]
        assert "precision_preprocess_v1" not in row["fit"]


@pytest.mark.parametrize("cell", range(6))
def test_fit_argv_for_every_cell(tmp_path, cell):
    run, arm = RUNS[cell // 3], ARMS[cell % 3]
    upstream = _precision_root(run, arm)
    audit = _audit_root(run, arm)
    manifest = f"{upstream}/selection_manifest.json"
    assert _argv(tmp_path, "fit", cell, [manifest]) == [
        str(tmp_path / "scripts" / "audit_coordinate_matched_ols.py"),
        "fit", "--manifest", manifest,
        "--dataset-dir", "data", "--models-root", "models",
        "--out", f"{audit}/fit.json",
    ]


def test_calibrate_confirm_and_render_argv(tmp_path):
    run, arm = RUNS[1], ARMS[2]
    upstream = _precision_root(run, arm)
    audit = _audit_root(run, arm)
    fit = f"{audit}/fit.json"
    calibration = f"{audit}/calibration.json"
    manifest = f"{upstream}/selection_manifest.json"
    precision_calibration = f"{upstream}/calibration.json"
    precision_confirmation = f"{upstream}/confirmation.json"

    assert _argv(tmp_path / "calibrate", "calibrate", 5, [fit]) == [
        str(tmp_path / "calibrate" / "scripts" /
            "audit_coordinate_matched_ols.py"),
        "calibrate", "--fit", fit,
        "--dataset-dir", "data", "--models-root", "models",
        "--out", calibration,
    ]
    assert _argv(
        tmp_path / "confirm", "confirm", 5,
        [fit, calibration, manifest, precision_calibration,
         precision_confirmation],
    ) == [
        str(tmp_path / "confirm" / "scripts" /
            "audit_coordinate_matched_ols.py"),
        "confirm", "--fit", fit, "--calibration", calibration,
        "--precision-manifest", manifest,
        "--precision-calibration", precision_calibration,
        "--precision-confirmation", precision_confirmation,
        "--dataset-dir", "data", "--models-root", "models",
        "--out", f"{audit}/confirmation.json",
    ]

    confirmations = [
        f"{_audit_root(r, a)}/confirmation.json"
        for r in RUNS for a in ARMS]
    rendered = _argv(
        tmp_path / "render", "render", required=confirmations)
    start = rendered.index("--confirmations") + 1
    stop = rendered.index("--out-json")
    assert rendered[start:stop] == confirmations
    assert rendered[stop:] == [
        "--out-json", "experiments/coordinate_matched_ols_v1.json",
        "--out-md", "experiments/coordinate_matched_ols_v1.md",
    ]


def test_missing_upstream_and_invalid_cells_fail_closed(tmp_path):
    env = _project(tmp_path)
    missing = subprocess.run(
        ["bash", str(WRAPPER), "fit", "0"], cwd=REPO, env=env,
        text=True, capture_output=True,
    )
    assert missing.returncode == 2
    assert "required frozen artifact is missing" in missing.stderr

    invalid = subprocess.run(
        ["bash", str(WRAPPER), "fit", "6"], cwd=REPO, env=env,
        text=True, capture_output=True,
    )
    assert invalid.returncode == 2


def test_all_preserves_upstream_and_runs_strict_stage_order(tmp_path):
    env = _project(tmp_path)
    upstream_paths = []
    for run in RUNS:
        for arm in ARMS:
            root = _precision_root(run, arm)
            for name in ("selection_manifest.json", "calibration.json",
                         "confirmation.json"):
                upstream_paths.append(_touch(
                    tmp_path, f"{root}/{name}", text=f"frozen:{run}:{arm}:{name}"))
    before = {path: path.read_bytes() for path in upstream_paths}

    subprocess.run(
        ["bash", str(WRAPPER), "all"], cwd=REPO, env=env,
        text=True, capture_output=True, check=True,
    )
    calls = [line.split("\t") for line in
             (tmp_path / "calls.tsv").read_text().splitlines()]
    assert [call[1] for call in calls] == (
        ["fit"] * 6 + ["calibrate"] * 6 + ["confirm"] * 6 + ["render"])
    assert all(path.read_bytes() == before[path] for path in upstream_paths)

    output_flags = {"--out", "--out-json", "--out-md"}
    for call in calls:
        for index, token in enumerate(call[:-1]):
            if token in output_flags:
                assert "precision_preprocess_v1" not in call[index + 1]


def test_wrapper_is_portable_and_has_valid_bash_syntax():
    subprocess.run(["bash", "-n", str(WRAPPER)], check=True)
    text = WRAPPER.read_text()
    assert "hpc/lightning/env.sh" in text
    assert "#SBATCH" not in text
    assert "sbatch" not in text
    assert "srun" not in text
    assert "/rds/user" not in text
