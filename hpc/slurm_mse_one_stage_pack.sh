#!/bin/bash
#! Single-job executor for the dis-L2 `intr` QoS.
#!
#! `intr` currently permits one submitted job and three nodes per user, so a
#! Slurm array is not admissible.  This allocation launches the frozen 165
#! main tasks and 12 controls as independent 16-CPU job steps, three at a
#! time (one per `intr` node). Existing report.json files are skipped. A
#! five-minute Slurm signal
#! requeues this same job before its one-hour wall limit; immutable downstream
#! stages are replay-safe and never reselect after T1/T2 access.
#!
#!   mkdir -p logs
#!   sbatch hpc/slurm_mse_one_stage_pack.sh
#SBATCH --job-name=mse1_pack
#SBATCH --output=logs/mse1_pack_%j.out
#SBATCH --error=logs/mse1_pack_%j.err
#SBATCH --open-mode=append
#SBATCH --time=01:00:00
#SBATCH --signal=B:USR1@300
#SBATCH --requeue
#SBATCH --nodes=3
#SBATCH --ntasks=3
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --partition=icelake
#SBATCH --account=MPHIL-DIS-SL2-CPU
#SBATCH --qos=intr
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zx332@cam.ac.uk

set -euo pipefail

PROJ="${PROJ:-/rds/user/zx332/hpc-work/cmb-lcdm-sr}"
PYTHON="${PROJ}/.venv/bin/python"
[[ -x "${PYTHON}" ]] || { echo "[err] missing interpreter ${PYTHON}"; exit 1; }
export PATH="${PROJ}/.venv/bin:${PATH}"
export PYTHON_JULIAPKG_PROJECT="${PROJ}/.venv/julia_env"
export PYTHON_JULIAPKG_OFFLINE="${PYTHON_JULIAPKG_OFFLINE:-yes}"
export PYTHONUNBUFFERED=1
export PACKED=1

cd "${PROJ}"
mkdir -p logs

RESTART="${SLURM_RESTART_COUNT:-0}"
MAX_RESTARTS=20
BATCH_WIDTH=3
SOFT_LIMIT_SECONDS=2400
CONFIRM_LATEST_START_SECONDS=1200
START_SECONDS="${SECONDS}"
REQUEUE_REQUESTED=0

if (( RESTART > MAX_RESTARTS )); then
    echo "[err] restart count ${RESTART} exceeds ${MAX_RESTARTS}"
    exit 1
fi

elapsed_seconds() {
    echo "$(( SECONDS - START_SECONDS ))"
}

requeue_self() {
    if (( REQUEUE_REQUESTED )); then
        return
    fi
    REQUEUE_REQUESTED=1
    trap - USR1
    echo "[requeue] job=${SLURM_JOB_ID} restart=${RESTART} elapsed=$(elapsed_seconds)s"
    scontrol requeue "${SLURM_JOB_ID}"
    exit 0
}

trap requeue_self USR1

run_batch() {
    local script="$1" family="$2" first="$3" last="$4"
    local idx out err pid failures=0
    local -a pids=() indexes=()
    echo "[batch] family=${family} tasks=${first}-${last} restart=${RESTART}"
    for (( idx=first; idx<=last; idx++ )); do
        out="logs/mse1_pack_${SLURM_JOB_ID}_r${RESTART}_${family}_${idx}.out"
        err="logs/mse1_pack_${SLURM_JOB_ID}_r${RESTART}_${family}_${idx}.err"
        srun --exclusive --exact --nodes=1 --ntasks=1 --cpus-per-task=16 \
            env SLURM_ARRAY_TASK_ID="${idx}" \
                SLURM_CPUS_PER_TASK=16 \
                SLURM_RESTART_COUNT="${RESTART}" \
                PACKED=1 \
            bash "${script}" >"${out}" 2>"${err}" &
        pids+=("$!")
        indexes+=("${idx}")
    done
    for (( idx=0; idx<${#pids[@]}; idx++ )); do
        pid="${pids[${idx}]}"
        if ! wait "${pid}"; then
            echo "[warn] ${family} task ${indexes[${idx}]} failed; see task log"
            failures=$(( failures + 1 ))
        fi
    done
    (( failures == 0 ))
}

run_family() {
    local script="$1" family="$2" total="$3"
    local first last
    for (( first=0; first<total; first+=BATCH_WIDTH )); do
        if (( $(elapsed_seconds) >= SOFT_LIMIT_SECONDS )); then
            requeue_self
        fi
        last=$(( first + BATCH_WIDTH - 1 ))
        (( last < total )) || last=$(( total - 1 ))
        if ! run_batch "${script}" "${family}" "${first}" "${last}"; then
            requeue_self
        fi
    done
}

run_pair() {
    local mode="$1" run pid failures=0
    local -a pids=()
    for run in lcdm_tt_beta3e-4 lcdm_tt_ee_lowl; do
        srun --exclusive --exact --nodes=1 --ntasks=1 --cpus-per-task=16 \
            bash hpc/slurm_mse_one_stage_consolidate.sh "${mode}" "${run}" \
            >"logs/mse1_pack_${SLURM_JOB_ID}_r${RESTART}_${mode}_${run}.out" \
            2>"logs/mse1_pack_${SLURM_JOB_ID}_r${RESTART}_${mode}_${run}.err" &
        pids+=("$!")
    done
    for pid in "${pids[@]}"; do
        if ! wait "${pid}"; then
            failures=$(( failures + 1 ))
        fi
    done
    if (( failures > 0 )); then
        echo "[err] ${mode} failed for ${failures} checkpoint(s)"
        return 1
    fi
}

echo "[start] packed MSE experiment job=${SLURM_JOB_ID} restart=${RESTART}"
run_family hpc/slurm_mse_one_stage_sr.sh main 165
run_family hpc/slurm_mse_one_stage_control.sh control 12

if (( $(elapsed_seconds) >= SOFT_LIMIT_SECONDS )); then
    requeue_self
fi
run_pair select
run_pair calibrate

# Leave at least forty minutes for the two parallel confirmatory checkpoints.
if (( $(elapsed_seconds) >= CONFIRM_LATEST_START_SECONDS )); then
    requeue_self
fi
run_pair confirm

trap - USR1
echo "[done] packed MSE experiment and both confirmation chains completed"
