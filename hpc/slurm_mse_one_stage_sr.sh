#!/bin/bash
#! One-stage latent reconstruction with explicit MSE inner loss.
#!
#! The embedded array covers both checkpoints, every latent, five PySR seeds,
#! and the frozen maxsize ladder {20,30,40}: 165 independent/resumable tasks.
#!
#!   mkdir -p logs
#!   PRINT_MATRIX=1 bash hpc/slurm_mse_one_stage_sr.sh
#!   sbatch --array=0 --export=ALL,SMOKE=1 \
#!       hpc/slurm_mse_one_stage_sr.sh                    # isolated smoke
#!   sbatch hpc/slurm_mse_one_stage_sr.sh                 # full 0-164%16 array
#!
#! Override --array at submission to rerun a subset. A task whose report.json
#! already exists exits successfully without touching it.
#! When the parent cpu1 allocation is unavailable, use the packed `intr`
#! launcher in hpc/slurm_mse_one_stage_pack.sh instead.
#SBATCH --job-name=mse1_sr
#SBATCH --output=logs/mse1_sr_%A_%a.out
#SBATCH --error=logs/mse1_sr_%A_%a.err
#SBATCH --array=0-164%16
#SBATCH --time=08:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=16G
#SBATCH --partition=icelake
#SBATCH --account=MPHIL-DIS-SL2-CPU
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zx332@cam.ac.uk

set -euo pipefail

PROJ="${PROJ:-/rds/user/zx332/hpc-work/cmb-lcdm-sr}"
TOTAL_TASKS=165
INPUTS=(omega_b omega_cdm H0 tau A_s n_s)
SEEDS=(0 1 2 3 4)
BUDGETS=(20 30 40)

task_fields() {
    local idx="$1" run_dir n_latents local_idx latent seed budget
    if (( idx < 75 )); then
        run_dir="models/lcdm_tt_beta3e-4"
        n_latents=5
        local_idx="${idx}"
    else
        run_dir="models/lcdm_tt_ee_lowl"
        n_latents=6
        local_idx=$(( idx - 75 ))
    fi
    (( idx >= 0 && idx < TOTAL_TASKS )) || return 1
    budget="${BUDGETS[$(( local_idx % ${#BUDGETS[@]} ))]}"
    local_idx=$(( local_idx / ${#BUDGETS[@]} ))
    seed="${SEEDS[$(( local_idx % ${#SEEDS[@]} ))]}"
    latent=$(( local_idx / ${#SEEDS[@]} ))
    (( latent < n_latents )) || return 1
    printf '%s\t%s\t%s\t%s\n' "${run_dir}" "${latent}" "${seed}" "${budget}"
}

if [[ "${PRINT_MATRIX:-0}" == "1" ]]; then
    printf 'task_id\trun_dir\tlatent\tseed\tmaxsize\n'
    for (( task_id=0; task_id<TOTAL_TASKS; task_id++ )); do
        printf '%s\t' "${task_id}"
        task_fields "${task_id}"
    done
    exit 0
fi

IDX="${SLURM_ARRAY_TASK_ID:?submit as a Slurm array or use PRINT_MATRIX=1}"
FIELDS="$(task_fields "${IDX}")" || {
    echo "[err] invalid task id ${IDX}; expected 0-$((TOTAL_TASKS - 1))"
    exit 1
}
IFS=$'\t' read -r RUN_DIR LATENT SEED MAXSIZE <<< "${FIELDS}"

PYTHON="${PROJ}/.venv/bin/python"
[[ -x "${PYTHON}" ]] || { echo "[err] missing interpreter ${PYTHON}"; exit 1; }
export PATH="${PROJ}/.venv/bin:${PATH}"
export PYTHON_JULIAPKG_PROJECT="${PROJ}/.venv/julia_env"
export PYTHON_JULIAPKG_OFFLINE="${PYTHON_JULIAPKG_OFFLINE:-yes}"
export PYTHONUNBUFFERED=1
export JULIA_NUM_THREADS="${SLURM_CPUS_PER_TASK:-16}"

cd "${PROJ}"
mkdir -p logs
RUN_NAME="$(basename "${RUN_DIR}")"
if [[ "${SMOKE:-0}" == "1" ]]; then
    N_SAMPLES="${N_SAMPLES:-500}"
    NITERATIONS="${NITERATIONS:-1}"
    POPULATIONS="${POPULATIONS:-2}"
    SMOKE_ID="${SMOKE_TAG:-${SLURM_ARRAY_JOB_ID:-manual}}"
    OUT_DIR="results/${RUN_NAME}/mse_one_stage_smoke_${SMOKE_ID}_ms${MAXSIZE}/z${LATENT}_seed${SEED}"
    START_DELAY=0
else
    N_SAMPLES="${N_SAMPLES:-5000}"
    NITERATIONS="${NITERATIONS:-200}"
    POPULATIONS="${POPULATIONS:-15}"
    OUT_DIR="results/${RUN_NAME}/mse_one_stage_ms${MAXSIZE}/z${LATENT}_seed${SEED}"
    if [[ "${PACKED:-0}" == "1" ]]; then
        START_DELAY=0
    else
        START_DELAY=$(( (IDX % 16) * 7 ))
    fi
fi

if [[ -f "${OUT_DIR}/report.json" ]]; then
    echo "[skip] ${OUT_DIR}/report.json already exists"
    exit 0
fi

# Shared Julia-environment cold starts can race. Spread each production wave.
sleep "${START_DELAY}"

echo "[run] task=${IDX}/${TOTAL_TASKS} run=${RUN_NAME} latent=${LATENT} "
echo "[run] seed=${SEED} maxsize=${MAXSIZE} account=MPHIL-DIS-SL2-CPU cpu=16"
echo "[run] smoke=${SMOKE:-0} samples=${N_SAMPLES} iterations=${NITERATIONS} populations=${POPULATIONS}"
"${PYTHON}" scripts/run_blind_sr.py \
    --run-dir "${RUN_DIR}" \
    --dataset-dir data \
    --latent-index "${LATENT}" \
    --inputs "${INPUTS[@]}" \
    --n-samples "${N_SAMPLES}" \
    --niterations "${NITERATIONS}" \
    --populations "${POPULATIONS}" \
    --maxsize "${MAXSIZE}" \
    --inner-loss mse \
    --selection-metric mse \
    --posthoc-mi none \
    --turbo \
    --parallelism multithreading \
    --pysr-run-id "run_${SLURM_RESTART_COUNT:-0}" \
    --seed "${SEED}" \
    --out-dir "${OUT_DIR}"
