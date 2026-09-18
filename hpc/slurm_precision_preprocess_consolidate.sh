#!/bin/bash
#! Guarded consolidation for the precision/preprocessing comparison.
#!
#! Search reports are frozen by one six-cell select array, T1 calibration is a
#! second six-cell array, and T2 confirmation is a third. Rendering is a
#! single job which consumes all six confirmations. Keep the full barriers:
#!
#!   SEARCH_JID=<completed-or-submitted-search-array-id>
#!   SELECT_JID=$(sbatch --parsable --dependency=afterok:${SEARCH_JID} \
#!       --array=0-5 hpc/slurm_precision_preprocess_consolidate.sh select)
#!   CALIBRATE_JID=$(sbatch --parsable --dependency=afterok:${SELECT_JID} \
#!       --array=0-5 hpc/slurm_precision_preprocess_consolidate.sh calibrate)
#!   CONFIRM_JID=$(sbatch --parsable --dependency=afterok:${CALIBRATE_JID} \
#!       --array=0-5 hpc/slurm_precision_preprocess_consolidate.sh confirm)
#!   sbatch --dependency=afterok:${CONFIRM_JID} \
#!       hpc/slurm_precision_preprocess_consolidate.sh render
#!
#! The default account is the campaign account below. To use another account
#! deliberately, export ACCOUNT and pass the same value to `sbatch --account`;
#! the runtime guard rejects an ACCOUNT/SLURM_JOB_ACCOUNT mismatch.
#!
#!   export ACCOUNT=<authorised-account>
#!   sbatch --account="${ACCOUNT}" ...
#!
#! Cell map (also available with PRINT_CELLS=1):
#!   0 TT    raw64             3 TT+EE raw64
#!   1 TT    physical_o1_64    4 TT+EE physical_o1_64
#!   2 TT    logamp64          5 TT+EE logamp64
#SBATCH --job-name=precprep_cons
#SBATCH --output=logs/precprep_cons_%A_%a.out
#SBATCH --error=logs/precprep_cons_%A_%a.err
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --partition=icelake
#SBATCH --account=MPHIL-DIS-SL2-CPU
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zx332@cam.ac.uk

set -euo pipefail

PROJ="${PROJ:-/rds/user/zx332/hpc-work/cmb-lcdm-sr}"
DEFAULT_ACCOUNT="MPHIL-DIS-SL2-CPU"
ACCOUNT="${ACCOUNT:-${DEFAULT_ACCOUNT}}"
STUDY="precision_preprocess_v1"
RUNS=(
    lcdm_tt_beta3e-4
    lcdm_tt_beta3e-4
    lcdm_tt_beta3e-4
    lcdm_tt_ee_lowl
    lcdm_tt_ee_lowl
    lcdm_tt_ee_lowl
)
ARMS=(
    raw64
    physical_o1_64
    logamp64
    raw64
    physical_o1_64
    logamp64
)

fail() {
    echo "[err] $*" >&2
    exit 2
}

[[ "${ACCOUNT}" =~ ^[A-Za-z0-9_.-]+$ ]] || \
    fail "unsafe ACCOUNT value '${ACCOUNT}'"
# Case-insensitive account comparison via tr (works on bash 3.2 as well as 4+).
if [[ -n "${SLURM_JOB_ACCOUNT:-}" && \
      "$(printf '%s' "${SLURM_JOB_ACCOUNT}" | tr '[:upper:]' '[:lower:]')" != \
      "$(printf '%s' "${ACCOUNT}" | tr '[:upper:]' '[:lower:]')" ]]; then
    fail "ACCOUNT=${ACCOUNT} does not match SLURM_JOB_ACCOUNT=${SLURM_JOB_ACCOUNT}"
fi

cell_fields() {
    local cell="$1"
    [[ "${cell}" =~ ^[0-9]+$ ]] || return 1
    (( cell >= 0 && cell < ${#RUNS[@]} )) || return 1
    printf '%s\t%s\n' "${RUNS[${cell}]}" "${ARMS[${cell}]}"
}

artifact_root() {
    local run="$1" arm="$2"
    printf 'results/%s/%s/%s' "${run}" "${STUDY}" "${arm}"
}

if [[ "${PRINT_CELLS:-0}" == "1" ]]; then
    printf 'cell\trun\tarm\tmanifest\tcalibration\tconfirmation\n'
    for (( cell=0; cell<${#RUNS[@]}; cell++ )); do
        root="$(artifact_root "${RUNS[${cell}]}" "${ARMS[${cell}]}")"
        printf '%s\t%s\t%s\t%s/selection_manifest.json\t%s/calibration.json\t%s/confirmation.json\n' \
            "${cell}" "${RUNS[${cell}]}" "${ARMS[${cell}]}" \
            "${root}" "${root}" "${root}"
    done
    exit 0
fi

USAGE="usage: $0 {select|calibrate|confirm|render}"
MODE="${1:?${USAGE}}"
case "${MODE}" in
    select|calibrate|confirm)
        if [[ -n "${CELL_ID:-}" && -n "${SLURM_ARRAY_TASK_ID:-}" && \
              "${CELL_ID}" != "${SLURM_ARRAY_TASK_ID}" ]]; then
            fail "CELL_ID=${CELL_ID} disagrees with SLURM_ARRAY_TASK_ID=${SLURM_ARRAY_TASK_ID}"
        fi
        CELL="${CELL_ID:-${SLURM_ARRAY_TASK_ID:-}}"
        [[ -n "${CELL}" ]] || fail "${MODE} requires a cell via --array=0-5 or CELL_ID"
        FIELDS="$(cell_fields "${CELL}")" || fail "invalid cell '${CELL}'; expected 0-5"
        IFS=$'\t' read -r RUN ARM <<< "${FIELDS}"
        ;;
    render)
        [[ -z "${CELL_ID:-}" && -z "${SLURM_ARRAY_TASK_ID:-}" ]] || \
            fail "render is a single job and must not receive a cell/array id"
        ;;
    *)
        fail "unknown mode '${MODE}'; expected select, calibrate, confirm, or render"
        ;;
esac

PYTHON="${PROJ}/.venv/bin/python"
[[ -x "${PYTHON}" ]] || fail "missing interpreter ${PYTHON}"
export PATH="${PROJ}/.venv/bin:${PATH}"
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

cd "${PROJ}"
mkdir -p logs

require_file() {
    [[ -f "$1" ]] || fail "required frozen artifact is missing: $1"
}

if [[ "${MODE}" != "render" ]]; then
    ROOT="$(artifact_root "${RUN}" "${ARM}")"
    MANIFEST="${ROOT}/selection_manifest.json"
    CALIBRATION="${ROOT}/calibration.json"
    CONFIRMATION="${ROOT}/confirmation.json"
    echo "[consolidate] mode=${MODE} cell=${CELL} run=${RUN} arm=${ARM} account=${ACCOUNT}"
fi

case "${MODE}" in
    select)
        "${PYTHON}" scripts/consolidate_precision_preprocess.py select \
            --run "${RUN}" \
            --arm "${ARM}" \
            --results-root results \
            --out "${MANIFEST}"
        ;;
    calibrate)
        require_file "${MANIFEST}"
        "${PYTHON}" scripts/consolidate_precision_preprocess.py calibrate \
            --manifest "${MANIFEST}" \
            --dataset-dir data \
            --models-root models \
            --out "${CALIBRATION}"
        ;;
    confirm)
        require_file "${MANIFEST}"
        require_file "${CALIBRATION}"
        require_file experiments/ols_mi_sr_mse_sr_t2_comparison.md
        "${PYTHON}" scripts/consolidate_precision_preprocess.py confirm \
            --manifest "${MANIFEST}" \
            --calibration "${CALIBRATION}" \
            --dataset-dir data \
            --models-root models \
            --experiments-dir experiments \
            --baseline-report experiments/ols_mi_sr_mse_sr_t2_comparison.md \
            --out "${CONFIRMATION}"
        ;;
    render)
        CONFIRMATIONS=()
        for (( cell=0; cell<${#RUNS[@]}; cell++ )); do
            root="$(artifact_root "${RUNS[${cell}]}" "${ARMS[${cell}]}")"
            confirmation="${root}/confirmation.json"
            require_file "${confirmation}"
            CONFIRMATIONS+=("${confirmation}")
        done
        echo "[consolidate] mode=render confirmations=${#CONFIRMATIONS[@]} account=${ACCOUNT}"
        "${PYTHON}" scripts/consolidate_precision_preprocess.py render \
            --confirmations "${CONFIRMATIONS[@]}" \
            --out-json experiments/precision_preprocess_v1_comparison.json \
            --out-md experiments/precision_preprocess_v1_comparison.md
        ;;
esac
