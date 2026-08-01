#!/bin/bash
#! Shuffled-target negative control for blind symbolic regression.
#! Runs scripts/run_shuffled_control.py for one regime over 3 shuffle seeds.
#!
#! Positional args:
#!   1 RUN_DIR       (e.g. models/lcdm_tt_beta3e-4 or models/lcdm_tt_ee_lowl)
#!   2 TARGET_INDEX  amplitude-latent column (2 for TT-only, 5 for EE)
#!   3 NITER         (default 200)
#!   4 NSAMP         (default 5000)
#!   5 SEEDS         (default "0 1 2")
#!
#! Example:
#!   sbatch hpc/slurm_shuffled_control.sh models/lcdm_tt_beta3e-4 2
#!   sbatch hpc/slurm_shuffled_control.sh models/lcdm_tt_ee_lowl 5
#!
#SBATCH --job-name=blind_sr_shuf
#SBATCH --output=logs/blind_sr_shuf_%j.out
#SBATCH --error=logs/blind_sr_shuf_%j.err
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

RUN_DIR="${1:?need RUN_DIR}"
TARGET_INDEX="${2:?need TARGET_INDEX}"
NITER="${3:-200}"
NSAMP="${4:-5000}"
SEEDS="${5:-0 1 2}"

cd "${PROJ}"; mkdir -p logs

if [[ ! -f "${RUN_DIR}/analysis/encoder_means_test.npy" ]]; then
    SHARDS_ROOT="${SHARDS_ROOT:-/rds/user/zx332/hpc-work/cmbvae/data}"
    echo "[pre] encoder means missing; running encoder pass (shards: ${SHARDS_ROOT})"
    python scripts/encode_latents.py \
        --run-dir "${RUN_DIR}" \
        --dataset-dir data \
        --shards-root "${SHARDS_ROOT}"
fi

for S in ${SEEDS}; do
    echo "=================== shuffle/pysr seed ${S} ==================="
    python scripts/run_shuffled_control.py \
        --run-dir "${RUN_DIR}" \
        --dataset-dir data \
        --target-index "${TARGET_INDEX}" \
        --inputs A_s tau \
        --n-samples "${NSAMP}" \
        --niterations "${NITER}" \
        --shuffle-seed "${S}" \
        --pysr-seed "${S}" \
        --turbo \
        --parallelism multithreading
done
echo "Done: $(date)"
