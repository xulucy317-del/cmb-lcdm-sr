#!/bin/bash
#! All-params blind SR: feed ALL 6 raw LCDM parameters as PySR inputs and
#! discover the expression for EVERY latent — no input pre-selection, no
#! latent pre-selection. Protocol otherwise identical to the reference
#! (A_s, tau) study: gmm_mi inner loss, 200 iterations, 5000 samples,
#! seeds 0..4. The complexity budget is the MAXSIZE hyperparameter (PySR
#! maxsize; default 20 = reference protocol). A non-default MAXSIZE writes
#! to a sibling namespace results/<run>/allparams_ms<MAXSIZE>/ so budgets
#! never mix; consolidate it with
#!   python scripts/consolidate_allparams.py --subdir allparams_ms<MAXSIZE>
#!
#! Submit as an array over latent indices (one task per latent), after the
#! encoder-means job for the same model:
#!   sbatch --array=0-4 --dependency=afterok:<encJID> hpc/slurm_allparams_sr.sh models/lcdm_tt_beta3e-4
#!   sbatch --array=0-5 --dependency=afterok:<encJID> hpc/slurm_allparams_sr.sh models/lcdm_tt_ee_lowl
#! Lower-complexity variant (search-time budget, not a post-hoc filter):
#!   sbatch --array=0-4 hpc/slurm_allparams_sr.sh models/lcdm_tt_beta3e-4 "0 1 2 3 4" 10
#!
#! Positional args:
#!   1 RUN_DIR   (default: models/lcdm_tt_beta3e-4)
#!   2 SEEDS     (default: "0 1 2 3 4")
#!   3 MAXSIZE   (default: 20)
#!
#! Outputs: results/<run>/allparams[_ms<MAXSIZE>]/z<latent>_seed<seed>/report.json
#! (kept out of the reference study's symbolic_regression_gmm_mi_seed* namespace)
#!
#SBATCH --job-name=allparams_sr
#SBATCH --output=logs/allparams_sr_%A_%a.out
#SBATCH --error=logs/allparams_sr_%A_%a.err
#SBATCH --time=06:00:00
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
SEEDS="${2:-0 1 2 3 4}"
MAXSIZE="${3:-20}"
LATENT="${SLURM_ARRAY_TASK_ID:?run as an array job: --array=<latent indices>}"
INPUTS="omega_b omega_cdm H0 tau A_s n_s"

SUBDIR="allparams"
if [[ "${MAXSIZE}" != "20" ]]; then SUBDIR="allparams_ms${MAXSIZE}"; fi

cd "${PROJ}"; mkdir -p logs

RUN_NAME="$(basename "${RUN_DIR}")"
for SEED in ${SEEDS}; do
    OUT_DIR="results/${RUN_NAME}/${SUBDIR}/z${LATENT}_seed${SEED}"
    if [[ -f "${OUT_DIR}/report.json" ]]; then
        echo "[skip] ${OUT_DIR}/report.json already exists"
        continue
    fi
    echo "[run] run=${RUN_NAME} latent=${LATENT} seed=${SEED} maxsize=${MAXSIZE} inputs='${INPUTS}'"
    # shellcheck disable=SC2086
    python scripts/run_blind_sr.py \
        --run-dir "${RUN_DIR}" \
        --dataset-dir data \
        --latent-index "${LATENT}" \
        --inputs ${INPUTS} \
        --n-samples 5000 \
        --niterations 200 \
        --maxsize "${MAXSIZE}" \
        --turbo \
        --parallelism multithreading \
        --seed "${SEED}" \
        --out-dir "${OUT_DIR}"
done
