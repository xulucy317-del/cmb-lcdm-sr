#!/bin/bash
#! MSE shuffled-target controls for the two amplitude latents.
#!
#! The embedded array covers TT z2 and EE z5, paired seeds 0..2, and endpoint
#! budgets {20,40}: 12 independent/resumable diagnostic tasks.
#!
#!   mkdir -p logs
#!   PRINT_MATRIX=1 bash hpc/slurm_mse_one_stage_control.sh
#!   sbatch hpc/slurm_mse_one_stage_control.sh
#! Use hpc/slurm_mse_one_stage_pack.sh when only the `intr` QoS is available.
#SBATCH --job-name=mse1_ctl
#SBATCH --output=logs/mse1_ctl_%A_%a.out
#SBATCH --error=logs/mse1_ctl_%A_%a.err
#SBATCH --array=0-11%12
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
TOTAL_TASKS=12
INPUTS=(omega_b omega_cdm H0 tau A_s n_s)
SEEDS=(0 1 2)
BUDGETS=(20 40)
RUN_DIRS=(models/lcdm_tt_beta3e-4 models/lcdm_tt_ee_lowl)
AMP_LATENTS=(2 5)

task_fields() {
    local idx="$1" local_idx run_idx seed budget
    (( idx >= 0 && idx < TOTAL_TASKS )) || return 1
    local_idx="${idx}"
    budget="${BUDGETS[$(( local_idx % ${#BUDGETS[@]} ))]}"
    local_idx=$(( local_idx / ${#BUDGETS[@]} ))
    seed="${SEEDS[$(( local_idx % ${#SEEDS[@]} ))]}"
    run_idx=$(( local_idx / ${#SEEDS[@]} ))
    printf '%s\t%s\t%s\t%s\n' "${RUN_DIRS[${run_idx}]}" \
        "${AMP_LATENTS[${run_idx}]}" "${seed}" "${budget}"
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
OUT_DIR="results/${RUN_NAME}/mse_one_stage_control_ms${MAXSIZE}/z${LATENT}_shuffle${SEED}_seed${SEED}"

if [[ -f "${OUT_DIR}/report.json" ]]; then
    echo "[skip] ${OUT_DIR}/report.json already exists"
    exit 0
fi

if [[ "${PACKED:-0}" != "1" ]]; then
    sleep "$(( (IDX % 12) * 7 ))"
fi

echo "[run] control task=${IDX}/${TOTAL_TASKS} run=${RUN_NAME} latent=${LATENT}"
echo "[run] shuffle_seed=${SEED} pysr_seed=${SEED} maxsize=${MAXSIZE}"
"${PYTHON}" scripts/run_shuffled_control.py \
    --run-dir "${RUN_DIR}" \
    --dataset-dir data \
    --target-index "${LATENT}" \
    --inputs "${INPUTS[@]}" \
    --n-samples 5000 \
    --niterations 200 \
    --populations 15 \
    --maxsize "${MAXSIZE}" \
    --inner-loss mse \
    --selection-metric mse \
    --posthoc-mi none \
    --turbo \
    --parallelism multithreading \
    --pysr-run-id "run_${SLURM_RESTART_COUNT:-0}" \
    --shuffle-seed "${SEED}" \
    --pysr-seed "${SEED}" \
    --out-dir "${OUT_DIR}"
