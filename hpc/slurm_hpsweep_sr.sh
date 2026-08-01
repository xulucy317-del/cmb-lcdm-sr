#!/bin/bash
#! PySR hyperparameter sweep: one array task = one run_blind_sr.py invocation
#! (one config x one latent x one seed), looked up by SLURM_ARRAY_TASK_ID in
#! the tasks.tsv written by scripts/sweep_blind_sr.py plan.
#!
#!   python scripts/sweep_blind_sr.py plan --spec hpc/sweeps/allparams_hp_v1.json
#!   sbatch --array=0-<N-1>%16 hpc/slurm_hpsweep_sr.sh results/<run>/hpsweep_<name>
#!   python scripts/sweep_blind_sr.py status --spec hpc/sweeps/allparams_hp_v1.json
#!
#! Positional args:
#!   1 SWEEP_DIR  (results/<run>/hpsweep_<name>, holds manifest.json + tasks.tsv)
#!
#! Completed tasks (report.json present) exit immediately, so resubmitting any
#! index range is safe. The walltime covers the largest star-mode configs;
#! for a big grid raise it at submit time: sbatch --time=... .
#!
#SBATCH --job-name=hpsweep_sr
#SBATCH --output=logs/hpsweep_sr_%A_%a.out
#SBATCH --error=logs/hpsweep_sr_%A_%a.err
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=16G
#SBATCH --partition=icelake
#SBATCH --account=MPHIL-DIS-SL2-CPU
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zx332@cam.ac.uk

PROJ="${PROJ:-/rds/user/zx332/hpc-work/cmb-lcdm-sr}"

set +u; source ~/.bashrc; source "${PROJ}/.venv/bin/activate"
set -euo pipefail
export PYTHONUNBUFFERED=1
export JULIA_NUM_THREADS=16

SWEEP_DIR="${1:?usage: sbatch --array=... hpc/slurm_hpsweep_sr.sh <sweep-dir>}"
IDX="${SLURM_ARRAY_TASK_ID:?run as an array job over tasks.tsv row indices}"

cd "${PROJ}"; mkdir -p logs
TASKS="${SWEEP_DIR}/tasks.tsv"
[[ -f "${TASKS}" ]] || { echo "[err] ${TASKS} not found — run sweep_blind_sr.py plan"; exit 1; }

LINE="$(awk -F'\t' -v id="${IDX}" 'NR>1 && $1==id {print; exit}' "${TASKS}")"
[[ -n "${LINE}" ]] || { echo "[err] no task with idx=${IDX} in ${TASKS}"; exit 1; }
IFS=$'\t' read -r _ CONFIG_ID LATENT SEED NITER POPS MAXSIZE EXTRA RUN_DIR INPUTS NSAMPLES OUT_DIR <<< "${LINE}"

if [[ -f "${OUT_DIR}/report.json" ]]; then
    echo "[skip] ${OUT_DIR}/report.json already exists"
    exit 0
fi

# Stagger startups within the concurrency window: simultaneous PySR/Julia
# cold starts race on the shared julia_env manifest ("expected package
# LoopVectorization to exist in the manifest", seen at 16 concurrent starts).
sleep "$(( (SLURM_ARRAY_TASK_ID % 16) * 7 ))"

echo "[run] idx=${IDX} config=${CONFIG_ID} run=${RUN_DIR} latent=${LATENT} seed=${SEED}"
echo "[run] niterations=${NITER} populations=${POPS} maxsize=${MAXSIZE} extra=${EXTRA}"
# shellcheck disable=SC2086
python scripts/run_blind_sr.py \
    --run-dir "${RUN_DIR}" \
    --dataset-dir data \
    --latent-index "${LATENT}" \
    --inputs ${INPUTS} \
    --n-samples "${NSAMPLES}" \
    --niterations "${NITER}" \
    --populations "${POPS}" \
    --maxsize "${MAXSIZE}" \
    --pysr-extra "${EXTRA}" \
    --turbo \
    --parallelism multithreading \
    --seed "${SEED}" \
    --out-dir "${OUT_DIR}"
