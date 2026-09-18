"""hpc/submit.sh and hpc/run_tasks.sh: the routes for running the launchers
somewhere other than CSD3, without editing the (hash-pinned) launchers."""
import os
import pathlib
import shlex
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBMIT = REPO / "hpc" / "submit.sh"
RUN_TASKS = REPO / "hpc" / "run_tasks.sh"


def _clean_env(**updates):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("SLURM_", "MAIL_USER", "SHARDS_ROOT", "PROJ", "TASK_CPUS"))}
    env.update({k: str(v) for k, v in updates.items()})
    return env


def _launcher(tmp_path, body):
    path = tmp_path / "hpc" / "slurm_fake.sh"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/bash\n#SBATCH --account=MPHIL-DIS-SL2-CPU\n#SBATCH --partition=icelake\n" + body)
    path.chmod(0o755)
    return path


# ----------------------------------------------------------------- submit.sh

def test_submit_dry_run_puts_site_options_before_the_launcher(tmp_path):
    launcher = _launcher(tmp_path, "echo launcher\n")
    env = _clean_env(DRY_RUN=1, PROJ=tmp_path, SLURM_ACCOUNT="acc-x",
                     SLURM_PARTITION="cpu", SLURM_EXTRA="--qos=normal --time=04:00:00",
                     MAIL_USER="me@example.org", SHARDS_ROOT="/data/shards")
    out = subprocess.run(["bash", str(SUBMIT), "--array=0-3%2", str(launcher), "arg one", "2"],
                         env=env, text=True, capture_output=True, check=True).stdout
    argv = shlex.split(out)
    assert argv[0] == "sbatch"
    i = argv.index(str(launcher))
    sbatch_side, launcher_side = argv[1:i], argv[i + 1:]
    assert launcher_side == ["arg one", "2"]
    assert "--account=acc-x" in sbatch_side
    assert "--partition=cpu" in sbatch_side
    assert "--qos=normal" in sbatch_side and "--time=04:00:00" in sbatch_side
    assert "--mail-user=me@example.org" in sbatch_side and "--mail-type=FAIL" in sbatch_side
    assert "--array=0-3%2" in sbatch_side
    export = [a for a in sbatch_side if a.startswith("--export=")][0]
    assert export == f"--export=ALL,PROJ={tmp_path},SHARDS_ROOT=/data/shards,ACCOUNT=acc-x"
    # site options come first so that a caller's sbatch options can still win
    assert sbatch_side.index("--account=acc-x") < sbatch_side.index("--array=0-3%2")


def test_submit_defaults_to_no_mail_and_repo_root(tmp_path):
    launcher = _launcher(tmp_path, "echo launcher\n")
    env = _clean_env(DRY_RUN=1)
    out = subprocess.run(["bash", str(SUBMIT), str(launcher)], env=env, text=True,
                         capture_output=True, check=True).stdout
    argv = shlex.split(out)
    assert "--mail-type=NONE" in argv
    assert not any(a.startswith(("--account", "--partition", "--mail-user")) for a in argv)
    assert f"--export=ALL,PROJ={REPO}" in argv


def test_submit_reads_site_env_next_to_itself(tmp_path):
    hpc = tmp_path / "hpc"
    hpc.mkdir()
    (hpc / "submit.sh").write_bytes(SUBMIT.read_bytes())
    (hpc / "site.env").write_text("SLURM_ACCOUNT=from-site\nSLURM_PARTITION=part\nMAIL_USER=\n")
    launcher = _launcher(tmp_path, "echo launcher\n")
    out = subprocess.run(["bash", str(hpc / "submit.sh"), str(launcher)], env=_clean_env(DRY_RUN=1),
                         text=True, capture_output=True, check=True).stdout
    argv = shlex.split(out)
    assert "--account=from-site" in argv and "--partition=part" in argv
    assert "--mail-type=NONE" in argv
    assert f"--export=ALL,PROJ={tmp_path},ACCOUNT=from-site" in argv


def test_submit_calls_sbatch_from_the_project_root(tmp_path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    sbatch = fake_bin / "sbatch"
    sbatch.write_text('#!/bin/bash\necho "cwd=$PWD"\nprintf "arg=%s\\n" "$@"\n')
    sbatch.chmod(0o755)
    proj = tmp_path / "proj"
    proj.mkdir()
    launcher = _launcher(tmp_path, "echo launcher\n")
    env = _clean_env(PROJ=proj, SLURM_ACCOUNT="acc")
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    out = subprocess.run(["bash", str(SUBMIT), str(launcher), "x"], env=env, text=True,
                         capture_output=True, check=True).stdout
    assert f"cwd={proj}" in out
    assert (proj / "logs").is_dir()
    assert "arg=--account=acc" in out and f"arg={launcher}" in out and "arg=x" in out


def test_submit_rejects_missing_launcher(tmp_path):
    proc = subprocess.run(["bash", str(SUBMIT), "--array=0-1"], env=_clean_env(DRY_RUN=1),
                          text=True, capture_output=True)
    assert proc.returncode == 2
    proc = subprocess.run(["bash", str(SUBMIT), str(tmp_path / "nope.sh")], env=_clean_env(DRY_RUN=1),
                          text=True, capture_output=True)
    assert proc.returncode == 2 and "not found" in proc.stderr


# --------------------------------------------------------------- run_tasks.sh

PROBE = """
echo "task=${SLURM_ARRAY_TASK_ID:-none} job=${SLURM_JOB_ID:-} cpus=${SLURM_CPUS_PER_TASK:-} \
acct=${SLURM_JOB_ACCOUNT:-} restart=${SLURM_RESTART_COUNT:-} proj=${PROJ:-} shards=${SHARDS_ROOT:-} cwd=$PWD args=$*"
"""


def _read_logs(proj, name="slurm_fake"):
    return {p.name: p.read_text() for p in sorted((proj / "logs").glob(f"{name}_*.out"))}


def test_run_tasks_supplies_slurm_variables_per_task(tmp_path):
    launcher = _launcher(tmp_path, PROBE)
    proj = tmp_path / "proj"
    proj.mkdir()
    env = _clean_env(PROJ=proj, SLURM_ACCOUNT="acc", SHARDS_ROOT="/shards", TASK_CPUS=4)
    subprocess.run(["bash", str(RUN_TASKS), "--tasks", "0-2,7", "--parallel", "2",
                    str(launcher), "alpha", "b c"], env=env, text=True, capture_output=True, check=True)
    logs = _read_logs(proj)
    assert sorted(logs) == [f"slurm_fake_task{i}.out" for i in (0, 1, 2, 7)]
    for i in (0, 1, 2, 7):
        line = logs[f"slurm_fake_task{i}.out"]
        assert f"task={i} job=local-{i} cpus=4 acct=acc restart=0 proj={proj} shards=/shards" in line
        assert f"cwd={proj} args=alpha b c" in line


def test_run_tasks_without_tasks_runs_once_outside_array_context(tmp_path):
    launcher = _launcher(tmp_path, PROBE)
    proj = tmp_path / "proj"
    proj.mkdir()
    subprocess.run(["bash", str(RUN_TASKS), "--cpus", "2", str(launcher), "solo"],
                   env=_clean_env(PROJ=proj), text=True, capture_output=True, check=True)
    logs = _read_logs(proj)
    assert len(logs) == 1
    (text,) = logs.values()
    assert "task=none" in text and "cpus=2" in text and "args=solo" in text


def test_run_tasks_reports_failures_and_keeps_going(tmp_path):
    launcher = _launcher(tmp_path, 'echo "task=${SLURM_ARRAY_TASK_ID}"\n[[ "${SLURM_ARRAY_TASK_ID}" != 1 ]]\n')
    proj = tmp_path / "proj"
    proj.mkdir()
    proc = subprocess.run(["bash", str(RUN_TASKS), "--tasks=0-2", str(launcher)],
                          env=_clean_env(PROJ=proj), text=True, capture_output=True)
    assert proc.returncode != 0
    assert "FAILED" in proc.stderr
    assert sorted(_read_logs(proj)) == ["slurm_fake_task0.out", "slurm_fake_task1.out", "slurm_fake_task2.out"]


def test_run_tasks_rejects_bad_task_spec(tmp_path):
    launcher = _launcher(tmp_path, PROBE)
    proc = subprocess.run(["bash", str(RUN_TASKS), "--tasks", "0-x", str(launcher)],
                          env=_clean_env(PROJ=tmp_path), text=True, capture_output=True)
    assert proc.returncode == 2 and "bad --tasks" in proc.stderr


@pytest.mark.parametrize("launcher, n_lines", [
    ("slurm_mse_one_stage_sr.sh", 165),
    ("slurm_mse_one_stage_control.sh", 12),
])
def test_run_tasks_drives_a_real_launcher(tmp_path, launcher, n_lines):
    """PRINT_MATRIX=1 makes the campaign launchers list their task matrix and
    exit before touching Python, which exercises the whole bash path."""
    proj = tmp_path / "proj"
    (proj / ".venv" / "bin").mkdir(parents=True)
    (proj / ".venv" / "bin" / "activate").write_text("")
    env = _clean_env(PROJ=proj, PRINT_MATRIX=1, SLURM_ACCOUNT="mphil-dis-sl2-cpu")
    subprocess.run(["bash", str(RUN_TASKS), str(REPO / "hpc" / launcher)], env=env,
                   text=True, capture_output=True, check=True)
    (text,) = _read_logs(proj, launcher[:-3]).values()
    rows = [l for l in text.splitlines() if l and not l.startswith(("[", "task_id"))]
    assert len(rows) == n_lines
    assert rows[0].startswith("0\t") and rows[-1].startswith(f"{n_lines - 1}\t")
