#!/bin/bash
#! Blind symbolic regression of a VAE amplitude latent (GMM-MI inner loss).
#!
#! Positional args:
#!   1 RUN_DIR     (default: models/lcdm_tt_beta3e-4)
#!   2 LATENT_IDX  (default: 2)
#!   3 INPUTS      (default: "A_s tau")
#!   4 SEED        (default: 0)
#!   5 NITER       (default: 200)
#!   6 NSAMP       (default: 5000)
#!
#! The two study regimes (5 seeds each):
#!   for N in 0 1 2 3 4; do sbatch hpc/slurm_blind_sr.sh models/lcdm_tt_beta3e-4 2 "A_s tau" $N; done
#!   for N in 0 1 2 3 4; do sbatch hpc/slurm_blind_sr.sh models/lcdm_tt_ee_lowl  5 "A_s tau" $N; done
#!
#SBATCH --job-name=blind_sr_gmm_mi
#SBATCH --output=logs/blind_sr_%j.out
#SBATCH --error=logs/blind_sr_%j.err
#SBATCH --time=10:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=16G
#SBATCH --partition=icelake
#SBATCH --account=MPHIL-DIS-SL2-CPU
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zx332@cam.ac.uk

# Project root on the cluster; override at submit time if it lives elsewhere:
#   sbatch --export=ALL,PROJ=/some/where hpc/slurm_blind_sr.sh ...
PROJ="${PROJ:-/rds/user/zx332/hpc-work/cmb-lcdm-sr}"

set +u; source ~/.bashrc; source "${PROJ}/.venv/bin/activate"
set -euo pipefail
export PYTHONUNBUFFERED=1
export JULIA_NUM_THREADS=16

RUN_DIR="${1:-models/lcdm_tt_beta3e-4}"
LATENT_INDEX="${2:-2}"
INPUTS="${3:-A_s tau}"
SEED="${4:-0}"
NITER="${5:-200}"
NSAMP="${6:-5000}"

cd "${PROJ}"; mkdir -p logs

# One-off per run dir: cache the encoder means if absent (needs the shards;
# SHARDS_ROOT defaults to the parent project's data dir on CSD3).
if [[ ! -f "${RUN_DIR}/analysis/encoder_means_test.npy" ]]; then
    SHARDS_ROOT="${SHARDS_ROOT:-/rds/user/zx332/hpc-work/cmbvae/data}"
    echo "[pre] encoder means missing; running encoder pass (shards: ${SHARDS_ROOT})"
    python scripts/encode_latents.py \
        --run-dir "${RUN_DIR}" \
        --dataset-dir data \
        --shards-root "${SHARDS_ROOT}"
fi

# shellcheck disable=SC2086
python scripts/run_blind_sr.py \
    --run-dir "${RUN_DIR}" \
    --dataset-dir data \
    --latent-index "${LATENT_INDEX}" \
    --inputs ${INPUTS} \
    --n-samples "${NSAMP}" \
    --niterations "${NITER}" \
    --turbo \
    --parallelism multithreading \
    --seed "${SEED}"
