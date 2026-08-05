#!/bin/bash
#! Phase-6 residual SR (docs/discovery_roadmap.md): blind rerun on the
#! Phase-3 residual caches e_k = mu_k − h(f1) (analysis/residual_z<k>_v1.npy),
#! ALL 6 raw parameters as inputs (restricting to S*∁ would presume
#! separability), protocol budget (ni200, ms20, 5000 samples), 5 PySR seeds.
#!
#! Positional args:
#!   1 RUN_DIR   (e.g. models/lcdm_tt_beta3e-4)
#!   2 LATENTS   (space-separated latent indices, e.g. "0 1 2 3 4")
#!   3 SEEDS     (default "0 1 2 3 4")
#!
#! Submit as an array over latent × seed pairs, task id ->
#! (latent = LATENTS[id / NSEEDS], seed = SEEDS[id % NSEEDS]):
#!   sbatch --array=0-24%16 hpc/slurm_residual_sr.sh models/lcdm_tt_beta3e-4 "0 1 2 3 4"
#!   sbatch --array=0-29%16 hpc/slurm_residual_sr.sh models/lcdm_tt_ee_lowl  "0 1 2 3 4 5"
#!
#! Outputs: results/<run>/residual_sr/z<latent>_seed<seed>/report.json
#! Completed tasks (report.json present) exit immediately; resubmitting any
#! index range is safe.
#!
#SBATCH --job-name=residual_sr
#SBATCH --output=logs/residual_sr_%A_%a.out
#SBATCH --error=logs/residual_sr_%A_%a.err
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

RUN_DIR="${1:?usage: sbatch --array=0-<N*S-1> hpc/slurm_residual_sr.sh <run-dir> \"<latents>\" [\"<seeds>\"]}"
LATENTS_STR="${2:?latent indices required, e.g. \"0 1 2 3 4\"}"
SEEDS_STR="${3:-0 1 2 3 4}"
IDX="${SLURM_ARRAY_TASK_ID:?run as an array job over latent x seed pairs}"

read -ra LATS <<< "${LATENTS_STR}"
read -ra SEEDS <<< "${SEEDS_STR}"
NS=${#SEEDS[@]}
NTASKS=$(( ${#LATS[@]} * NS ))
(( IDX < NTASKS )) || { echo "[err] idx ${IDX} >= ${NTASKS} tasks"; exit 1; }
K="${LATS[$(( IDX / NS ))]}"
SEED="${SEEDS[$(( IDX % NS ))]}"

cd "${PROJ}"; mkdir -p logs
RUN_NAME="$(basename "${RUN_DIR}")"
TARGET="${RUN_DIR}/analysis/residual_z${K}_v1.npy"
[[ -f "${TARGET}" ]] || { echo "[err] ${TARGET} missing — rerun Phase 3"; exit 1; }
OUT_DIR="results/${RUN_NAME}/residual_sr/z${K}_seed${SEED}"

if [[ -f "${OUT_DIR}/report.json" ]]; then
    echo "[skip] ${OUT_DIR}/report.json already exists"
    exit 0
fi

# Stagger startups within the concurrency window (shared julia_env manifest
# races at simultaneous cold starts — see slurm_hpsweep_sr.sh).
sleep "$(( (SLURM_ARRAY_TASK_ID % 16) * 7 ))"

echo "[run] run=${RUN_DIR} residual z${K} pysr_seed=${SEED}"
python scripts/run_blind_sr.py \
    --run-dir "${RUN_DIR}" \
    --dataset-dir data \
    --target-npy "${TARGET}" \
    --target-label "res_z${K}" \
    --inputs omega_b omega_cdm H0 tau A_s n_s \
    --n-samples 5000 \
    --niterations 200 \
    --turbo \
    --parallelism multithreading \
    --seed "${SEED}" \
    --out-dir "${OUT_DIR}"
