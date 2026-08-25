"""Static and dry-run checks for the dis-L2 CPU MSE arrays."""
import csv
import os
import pathlib
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[1]
MAIN = REPO / "hpc" / "slurm_mse_one_stage_sr.sh"
CONTROL = REPO / "hpc" / "slurm_mse_one_stage_control.sh"
CONSOLIDATE = REPO / "hpc" / "slurm_mse_one_stage_consolidate.sh"
PACK = REPO / "hpc" / "slurm_mse_one_stage_pack.sh"


def _matrix(path):
    env = dict(os.environ, PRINT_MATRIX="1")
    proc = subprocess.run(
        ["bash", str(path)], cwd=REPO, env=env, check=True,
        text=True, capture_output=True)
    return list(csv.DictReader(proc.stdout.splitlines(), delimiter="\t"))


def test_main_matrix_is_complete_unique_and_frozen():
    rows = _matrix(MAIN)
    assert len(rows) == 165
    keys = {(r["run_dir"], int(r["latent"]), int(r["seed"]),
             int(r["maxsize"])) for r in rows}
    assert len(keys) == 165
    assert {int(r["maxsize"]) for r in rows} == {20, 30, 40}
    assert {int(r["seed"]) for r in rows} == set(range(5))
    tt = [r for r in rows if r["run_dir"].endswith("lcdm_tt_beta3e-4")]
    ee = [r for r in rows if r["run_dir"].endswith("lcdm_tt_ee_lowl")]
    assert len(tt) == 75 and {int(r["latent"]) for r in tt} == set(range(5))
    assert len(ee) == 90 and {int(r["latent"]) for r in ee} == set(range(6))


def test_control_matrix_has_only_amplitude_endpoint_pairs():
    rows = _matrix(CONTROL)
    assert len(rows) == 12
    keys = {(r["run_dir"], int(r["latent"]), int(r["seed"]),
             int(r["maxsize"])) for r in rows}
    assert len(keys) == 12
    assert {int(r["seed"]) for r in rows} == {0, 1, 2}
    assert {int(r["maxsize"]) for r in rows} == {20, 40}
    assert {(r["run_dir"].split("/")[-1], int(r["latent"]))
            for r in rows} == {
                ("lcdm_tt_beta3e-4", 2),
                ("lcdm_tt_ee_lowl", 5),
            }


def test_launchers_use_requested_cpu_account_and_mse_path():
    for path in (MAIN, CONTROL, CONSOLIDATE, PACK):
        text = path.read_text()
        assert "#SBATCH --account=MPHIL-DIS-SL2-CPU" in text
        assert "#SBATCH --partition=icelake" in text
        assert "#SBATCH --cpus-per-task=16" in text
        assert "--gres" not in text
        assert "gpu" not in text.lower()
        assert "source ~/.bashrc" not in text
        assert ".venv/bin/activate" not in text
        assert 'PYTHON="${PROJ}/.venv/bin/python"' in text
        assert 'PYTHON_JULIAPKG_PROJECT="${PROJ}/.venv/julia_env"' in text
    pack_text = PACK.read_text()
    assert "#SBATCH --qos=intr" in pack_text
    assert "#SBATCH --time=01:00:00" in pack_text
    assert "#SBATCH --nodes=3" in pack_text
    assert "#SBATCH --ntasks=3" in pack_text
    assert "run_family hpc/slurm_mse_one_stage_sr.sh main 165" in pack_text
    assert "run_family hpc/slurm_mse_one_stage_control.sh control 12" in pack_text
    assert "run_pair select" in pack_text
    assert "run_pair calibrate" in pack_text
    assert "run_pair confirm" in pack_text
    assert "scontrol requeue" in pack_text
    for path in (MAIN, CONTROL):
        text = path.read_text()
        assert "--inner-loss mse" in text
        assert "--selection-metric mse" in text
        assert "--posthoc-mi none" in text
    main_text = MAIN.read_text()
    assert "mse_one_stage_smoke_${SMOKE_ID}_ms${MAXSIZE}" in main_text
    assert 'NITERATIONS="${NITERATIONS:-1}"' in main_text


def test_consolidation_launcher_preserves_phase_ordering_contract():
    text = CONSOLIDATE.read_text()
    assert "select)" in text and "calibrate)" in text and "confirm)" in text
    assert "--manifest" in text
    assert "--calibration" in text
    assert "--n-perm-mi 39" in text
    assert "--n-perm-r2" not in text
