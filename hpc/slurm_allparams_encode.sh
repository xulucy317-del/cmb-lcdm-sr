#!/bin/bash
#! Encoder pass only: cache <run-dir>/analysis/encoder_means_test.npy.
#! Submitted once per model ahead of the all-params SR arrays so that the
#! array tasks never race on writing the cache.
#!
#! Positional args:
#!   1 RUN_DIR   (default: models/lcdm_tt_beta3e-4)
#!
#SBATCH --job-name=allparams_encode
#SBATCH --output=logs/allparams_encode_%j.out
#SBATCH --error=logs/allparams_encode_%j.err
#SBATCH --time=01:00:00
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

RUN_DIR="${1:-models/lcdm_tt_beta3e-4}"
cd "${PROJ}"; mkdir -p logs

if [[ -f "${RUN_DIR}/analysis/encoder_means_test.npy" ]]; then
    echo "[skip] ${RUN_DIR}/analysis/encoder_means_test.npy already exists"
    exit 0
fi

SHARDS_ROOT="${SHARDS_ROOT:-/rds/user/zx332/hpc-work/cmbvae/data}"
echo "[encode] ${RUN_DIR} (shards: ${SHARDS_ROOT})"
python scripts/encode_latents.py \
    --run-dir "${RUN_DIR}" \
    --dataset-dir data \
    --shards-root "${SHARDS_ROOT}"
