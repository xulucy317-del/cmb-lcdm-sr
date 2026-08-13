#!/bin/bash
#! Sham-input dilution control (post-closure follow-up to roadmap Phase 4):
#! the all-6 blind SR rerun with one provably-irrelevant 7th input column
#! (data/sham_v1_<donor>.npy — a permutation of a real theta column, so it
#! carries a genuine parameter's marginal and zero information about any
#! latent; see scripts/build_sham_inputs.py).
#!
#! Protocol is byte-identical to results/<run>/allparams (ni200, pops15,
#! ms20, 5000 samples, 5 PySR seeds), which is therefore the free paired
#! baseline: MI@c<=10 sham vs MI@c<=10 all-6 isolates the search cost of one
#! useless variable, with no argument about whether a real parameter "might"
#! matter a little.
#!
#! Positional args:
#!   1 RUN_DIR   (e.g. models/lcdm_tt_beta3e-4)
#!   2 LATENTS   (space-separated latent indices, e.g. "0 1 2 3 4")
#!   3 SEEDS     (default "0 1 2 3 4")
#!   4 DONORS    (default "ob tau ns")
#!
#! Array over donor x latent x seed, task id ->
#! (donor = DONORS[id / (NLAT*NSEEDS)], latent, seed):
#!   sbatch --array=0-74%16 hpc/slurm_sham_control.sh models/lcdm_tt_beta3e-4 "0 1 2 3 4"
#!   sbatch --array=0-89%16 hpc/slurm_sham_control.sh models/lcdm_tt_ee_lowl  "0 1 2 3 4 5"
#!
#! Outputs: results/<run>/sham_control/<donor>/z<latent>_seed<seed>/report.json
#! Completed tasks (report.json present) exit immediately; resubmitting any
#! index range is safe.
#!
#SBATCH --job-name=sham_control
#SBATCH --output=logs/sham_control_%A_%a.out
#SBATCH --error=logs/sham_control_%A_%a.err
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

RUN_DIR="${1:?usage: sbatch --array=0-<D*N*S-1> hpc/slurm_sham_control.sh <run-dir> \"<latents>\" [\"<seeds>\"] [\"<donors>\"]}"
LATENTS_STR="${2:?latent indices required, e.g. \"0 1 2 3 4\"}"
SEEDS_STR="${3:-0 1 2 3 4}"
DONORS_STR="${4:-ob tau ns}"
IDX="${SLURM_ARRAY_TASK_ID:?run as an array job over donor x latent x seed}"

read -ra LATS <<< "${LATENTS_STR}"
read -ra SEEDS <<< "${SEEDS_STR}"
read -ra DONORS <<< "${DONORS_STR}"
NS=${#SEEDS[@]}
NL=${#LATS[@]}
NTASKS=$(( ${#DONORS[@]} * NL * NS ))
(( IDX < NTASKS )) || { echo "[err] idx ${IDX} >= ${NTASKS} tasks"; exit 1; }
DONOR="${DONORS[$(( IDX / (NL * NS) ))]}"
REM=$(( IDX % (NL * NS) ))
K="${LATS[$(( REM / NS ))]}"
SEED="${SEEDS[$(( REM % NS ))]}"

cd "${PROJ}"; mkdir -p logs
RUN_NAME="$(basename "${RUN_DIR}")"
SHAM="data/sham_v1_${DONOR}.npy"
[[ -f "${SHAM}" ]] || { echo "[err] ${SHAM} missing — run scripts/build_sham_inputs.py"; exit 1; }
OUT_DIR="results/${RUN_NAME}/sham_control/${DONOR}/z${K}_seed${SEED}"

if [[ -f "${OUT_DIR}/report.json" ]]; then
    echo "[skip] ${OUT_DIR}/report.json already exists"
    exit 0
fi

# Stagger startups within the concurrency window (shared julia_env manifest
# races at simultaneous cold starts — see slurm_hpsweep_sr.sh).
sleep "$(( (SLURM_ARRAY_TASK_ID % 16) * 7 ))"

echo "[run] run=${RUN_DIR} sham=${DONOR} z${K} pysr_seed=${SEED}"
python scripts/run_blind_sr.py \
    --run-dir "${RUN_DIR}" \
    --dataset-dir data \
    --latent-index "${K}" \
    --inputs omega_b omega_cdm H0 tau A_s n_s \
    --extra-input-npy "sham=${SHAM}" \
    --n-samples 5000 \
    --niterations 200 \
    --populations 15 \
    --maxsize 20 \
    --turbo \
    --parallelism multithreading \
    --seed "${SEED}" \
    --out-dir "${OUT_DIR}"
