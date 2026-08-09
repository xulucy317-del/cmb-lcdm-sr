#!/bin/bash
#! Shuffled-residual negative control for the interaction-aware stage 2:
#! identical 7-input configuration (all 6 raw params + f1hat) as
#! slurm_residual_sr_ia.sh, target permuted across rows. One job = one
#! (run, latent, shuffle-seed) triple:
#!   sbatch hpc/slurm_residual_sr_ia_control.sh models/lcdm_tt_beta3e-4 2 0
#!   sbatch hpc/slurm_residual_sr_ia_control.sh models/lcdm_tt_ee_lowl  5 1
#! Output: results/<run>/residual_sr_ia/shuffled_res_z<k>_s<seed>/report.json
#!
#SBATCH --job-name=residual_sr_ia_ctl
#SBATCH --output=logs/residual_sr_ia_ctl_%j.out
#SBATCH --error=logs/residual_sr_ia_ctl_%j.err
#SBATCH --time=02:00:00
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

RUN_DIR="${1:?usage: sbatch hpc/slurm_residual_sr_ia_control.sh <run-dir> <latent> <shuffle-seed>}"
K="${2:?latent index required}"
SHUF="${3:?shuffle seed required}"

cd "${PROJ}"; mkdir -p logs
RUN_NAME="$(basename "${RUN_DIR}")"
OUT_DIR="results/${RUN_NAME}/residual_sr_ia/shuffled_res_z${K}_s${SHUF}"

if [[ -f "${OUT_DIR}/report.json" ]]; then
    echo "[skip] ${OUT_DIR}/report.json already exists"
    exit 0
fi

python scripts/run_shuffled_control.py \
    --run-dir "${RUN_DIR}" \
    --dataset-dir data \
    --target-npy "${RUN_DIR}/analysis/residual_z${K}_v1.npy" \
    --target-label "res_z${K}" \
    --inputs omega_b omega_cdm H0 tau A_s n_s \
    --extra-input-npy "f1hat=${RUN_DIR}/analysis/f1hat_z${K}_v1.npy" \
    --n-samples 5000 \
    --niterations 200 \
    --shuffle-seed "${SHUF}" \
    --pysr-seed "${SHUF}" \
    --turbo \
    --parallelism multithreading \
    --out-dir "${OUT_DIR}"
