"""Parity checks for the scheduler-free (Lightning AI) execution path.

The Slurm launchers stay the definition of task identity. These tests prove
that scripts/run_mse_one_stage_pool.py rebuilds exactly the same command for
the same task id, that its resume contract only skips reports that belong to
the task, and that the Lightning wrappers carry no CSD3/Slurm assumptions.
"""
import json
import os
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import run_mse_one_stage_pool as pool                            # noqa: E402

LIGHTNING = REPO / "hpc" / "lightning"
MAIN_SAMPLE = [0, 1, 2, 35, 36, 74, 75, 90, 164]
CONTROL_SAMPLE = list(range(12))


def _shim_project(tmp_path):
    """A fake PROJ whose .venv/bin/python just prints its arguments."""
    python = tmp_path / ".venv" / "bin" / "python"
    python.parent.mkdir(parents=True)
    python.write_text('#!/bin/bash\nprintf "%s\\n" "$@"\n')
    python.chmod(0o755)
    return tmp_path


def _launcher_argv(tmp_path, family, task_id):
    launcher = pool.FAMILIES[family]["launcher"]
    env = dict(os.environ,
               PROJ=str(_shim_project(tmp_path)),
               SLURM_ARRAY_TASK_ID=str(task_id),
               SLURM_CPUS_PER_TASK="16",
               PACKED="1")                     # skip the anti-thundering sleep
    proc = subprocess.run(["bash", str(launcher)], env=env, check=True,
                          text=True, capture_output=True)
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    start = next(i for i, line in enumerate(lines)
                 if line.endswith(".py"))
    return lines[start:]


def _strip_run_id(argv):
    out, skip = [], False
    for token in argv:
        if skip:
            skip = False
            continue
        if token == "--pysr-run-id":
            skip = True
            continue
        out.append(token)
    return out


@pytest.mark.parametrize("family,task_id",
                         [("main", i) for i in MAIN_SAMPLE]
                         + [("control", i) for i in CONTROL_SAMPLE])
def test_pool_rebuilds_the_launcher_command(tmp_path, family, task_id):
    rows = pool.read_matrix(family)
    task = pool.build_task(family, rows[task_id], None)
    launcher = _launcher_argv(tmp_path, family, task_id)
    assert launcher[0] == f"scripts/{task['module']}.py"
    assert _strip_run_id(launcher[1:]) == task["argv"]
    assert "--pysr-run-id" in launcher                 # the launcher sets one


def test_pool_matrices_have_the_frozen_sizes():
    assert len(pool.enumerate_tasks("main", None)) == 165
    assert len(pool.enumerate_tasks("control", None)) == 12
    out_dirs = {t["out_dir"] for t in pool.enumerate_tasks("main", None)}
    assert len(out_dirs) == 165


def test_every_task_uses_mse_search_and_no_posthoc_mi():
    for family in ("main", "control"):
        for task in pool.enumerate_tasks(family, None):
            argv = task["argv"]
            assert argv[argv.index("--inner-loss") + 1] == "mse"
            assert argv[argv.index("--selection-metric") + 1] == "mse"
            assert argv[argv.index("--posthoc-mi") + 1] == "none"
            assert argv[argv.index("--n-samples") + 1] == "5000"
            assert argv[argv.index("--niterations") + 1] == "200"
            assert argv[argv.index("--populations") + 1] == "15"
            assert "--turbo" in argv
            assert argv[argv.index("--parallelism") + 1] == "multithreading"


def test_smoke_namespace_cannot_collide_with_frozen_results():
    frozen = {t["out_dir"] for t in pool.enumerate_tasks("main", None)} | \
             {t["out_dir"] for t in pool.enumerate_tasks("control", None)}
    for family in ("main", "control"):
        for task in pool.enumerate_tasks(family, "tag1"):
            assert "smoke_tag1" in task["out_dir"]
            assert task["out_dir"] not in frozen
            assert task["argv"][task["argv"].index("--n-samples") + 1] == "500"
            assert task["argv"][task["argv"].index("--niterations") + 1] == "1"


def test_control_paths_match_the_consolidator_contract():
    tasks = pool.enumerate_tasks("control", None)
    expected = {
        f"results/{run}/mse_one_stage_control_ms{budget}"
        f"/z{amp}_shuffle{seed}_seed{seed}"
        for run, amp in (("lcdm_tt_beta3e-4", 2), ("lcdm_tt_ee_lowl", 5))
        for budget in (20, 40) for seed in (0, 1, 2)
    }
    assert {t["out_dir"] for t in tasks} == expected


def test_validate_report_binds_a_report_to_its_task(tmp_path):
    task = pool.build_task("main", pool.read_matrix("main")[0], None)
    report_path = REPO / task["out_dir"] / "report.json"
    if not report_path.is_file():
        pytest.skip("no completed report available in this checkout")
    valid, reason = pool.validate_report(report_path, task)
    assert valid, reason

    payload = json.loads(report_path.read_text())
    for mutation in ({"seed": 4}, {"latent_index": 3},
                     {"inner_loss": "gmm_mi"}, {"best_expression": ""},
                     {"pysr_kwargs": {**payload["pysr_kwargs"], "maxsize": 40}}):
        broken = tmp_path / "report.json"
        broken.write_text(json.dumps({**payload, **mutation}))
        ok, _ = pool.validate_report(broken, task)
        assert not ok, f"{mutation} should not validate"

    missing = tmp_path / "absent.json"
    assert pool.validate_report(missing, task) == (False, "missing")


def test_parse_ids_accepts_ranges_and_rejects_out_of_range():
    assert pool.parse_ids("36-38,40", 165) == {36, 37, 38, 40}
    assert pool.parse_ids(None, 165) is None
    with pytest.raises(SystemExit):
        pool.parse_ids("165", 165)


@pytest.mark.parametrize("name", ["env.sh", "bootstrap_env.sh",
                                  "run_consolidation.sh", "resume_all.sh",
                                  "make_transfer_bundle.sh"])
def test_lightning_wrappers_are_portable(name):
    path = LIGHTNING / name
    assert path.is_file()
    subprocess.run(["bash", "-n", str(path)], check=True)
    text = path.read_text()
    assert "#SBATCH" not in text
    assert "sbatch" not in text
    assert "srun" not in text
    assert "/rds/user" not in text
    assert "MPHIL-DIS-SL2-CPU" not in text


def test_consolidation_wrapper_keeps_the_phase_contract():
    text = (LIGHTNING / "run_consolidation.sh").read_text()
    for mode in ("select)", "calibrate)", "confirm)"):
        assert mode in text
    assert "--n-perm-mi 39" in text
    assert "--max-samples-mi 5000" in text
    assert "--n-perm-r2" not in text
    assert "--manifest" in text and "--calibration" in text


def test_consolidation_launchers_parse_their_own_arguments():
    """A literal '}' inside ${1:?...} closes the expansion early.

    `MODE="${1:?usage: $0 {select|...} <run-name>}"` leaves MODE holding
    'select <run-name>}', which reaches the case statement and fails. Both
    launchers carried this; the guard is static plus functional.
    """
    launchers = (LIGHTNING / "run_consolidation.sh",
                 REPO / "hpc" / "slurm_mse_one_stage_consolidate.sh")
    for path in launchers:
        assert ":?usage: $0 {" not in path.read_text(), path

    env = dict(os.environ, PYTHON="/bin/echo", SLURM_CPUS_PER_TASK="1")
    proc = subprocess.run(
        ["bash", str(LIGHTNING / "run_consolidation.sh"), "bogus", "somerun"],
        env=env, cwd=REPO, text=True, capture_output=True)
    assert "unknown mode 'bogus'" in proc.stdout, proc.stdout

    proc = subprocess.run(
        ["bash", str(LIGHTNING / "run_consolidation.sh"), "select", "somerun"],
        env=env, cwd=REPO, text=True, capture_output=True, check=True)
    assert "consolidate_mse_one_stage.py select --run somerun" in proc.stdout
    assert "<run-name>" not in proc.stdout


def test_frozen_environment_reference_is_carried():
    requirements = (LIGHTNING / "requirements-lightning.txt").read_text()
    assert "pysr==1.5.10" in requirements
    assert "scikit-learn==1.5.2" in requirements
    assert "gmm_mi @ git+" in requirements
    manifest = (LIGHTNING / "julia_env_reference" / "Manifest.toml").read_text()
    assert 'julia_version = "1.11.9"' in manifest
    assert "SymbolicRegression" in manifest
    project = (LIGHTNING / "julia_env_reference" / "Project.toml").read_text()
    assert "SymbolicRegression" in project
    # --turbo makes PySR Pkg.add LoopVectorization inside the first fit; the
    # carried environment must already contain it so no search depends on a
    # mid-run package install.
    assert "LoopVectorization" in project
    assert "LoopVectorization" in manifest
    bootstrap = (LIGHTNING / "bootstrap_env.sh").read_text()
    assert "load_required_packages(turbo=True)" in bootstrap
