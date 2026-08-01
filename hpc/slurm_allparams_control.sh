#!/bin/bash
#! Shuffled-target negative control for the ALL-PARAMS blind SR: identical
#! PySR configuration with all 6 raw parameters exposed, target latent
#! permuted across rows. Quantifies the null MI floor with the enlarged
#! input set (more inputs -> more room to overfit spurious MI).
#!
#! Positional args:
#!   1 RUN_DIR     (default: models/lcdm_tt_beta3e-4)
#!   2 TARGET_IDX  (default: 2)   amplitude latent of the model
#!   3 SHUF_SEEDS  (default: "0 1 2")
#!   4 MAXSIZE     (default: 20)  keep matched to the real runs' budget
#!
#! Outputs: results/<run>/allparams[_ms<MAXSIZE>]/shuffled_z<idx>_s<seed>/report.json
#!
#SBATCH --job-name=allparams_ctrl
#SBATCH --output=logs/allparams_ctrl_%j.out
#SBATCH --error=logs/allparams_ctrl_%j.err
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

RUN_DIR="${1:-models/lcdm_tt_beta3e-4}"
TARGET_IDX="${2:-2}"
SHUF_SEEDS="${3:-0 1 2}"
MAXSIZE="${4:-20}"
INPUTS="omega_b omega_cdm H0 tau A_s n_s"

SUBDIR="allparams"
if [[ "${MAXSIZE}" != "20" ]]; then SUBDIR="allparams_ms${MAXSIZE}"; fi

cd "${PROJ}"; mkdir -p logs

RUN_NAME="$(basename "${RUN_DIR}")"
for S in ${SHUF_SEEDS}; do
    OUT_DIR="results/${RUN_NAME}/${SUBDIR}/shuffled_z${TARGET_IDX}_s${S}"
    if [[ -f "${OUT_DIR}/report.json" ]]; then
        echo "[skip] ${OUT_DIR}/report.json already exists"
        continue
    fi
    echo "[control] run=${RUN_NAME} target=z${TARGET_IDX} shuffle_seed=${S} maxsize=${MAXSIZE}"
    # shellcheck disable=SC2086
    python scripts/run_shuffled_control.py \
        --run-dir "${RUN_DIR}" \
        --dataset-dir data \
        --target-index "${TARGET_IDX}" \
        --inputs ${INPUTS} \
        --n-samples 5000 \
        --niterations 200 \
        --maxsize "${MAXSIZE}" \
        --turbo \
        --parallelism multithreading \
        --shuffle-seed "${S}" \
        --pysr-seed "${S}" \
        --out-dir "${OUT_DIR}"
done
