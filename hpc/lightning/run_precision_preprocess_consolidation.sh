#!/usr/bin/env bash
#! Scheduler-free precision_preprocess_v1 consolidation.
#!
#!   bash hpc/lightning/run_precision_preprocess_consolidation.sh select 0
#!   bash hpc/lightning/run_precision_preprocess_consolidation.sh calibrate 0
#!   bash hpc/lightning/run_precision_preprocess_consolidation.sh confirm 0
#!   bash hpc/lightning/run_precision_preprocess_consolidation.sh render
#!
#! Cells are run-major:
#!   0..2: TT x {raw64, physical_o1_64, logamp64}
#!   3..5: TT+EE x {raw64, physical_o1_64, logamp64}
#!
#! Select reads T0 reports, calibrate opens T1, confirm is the first stage to
#! open T2, and render consumes all six immutable confirmations.
set -euo pipefail

PROJ="${PROJ:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
LIGHTNING_ENV="${LIGHTNING_ENV:-${PROJ}/hpc/lightning/env.sh}"
# shellcheck source=/dev/null
source "${LIGHTNING_ENV}"
cd "${PROJ}"

STUDY="precision_preprocess_v1"
RUNS=(
    lcdm_tt_beta3e-4 lcdm_tt_beta3e-4 lcdm_tt_beta3e-4
    lcdm_tt_ee_lowl lcdm_tt_ee_lowl lcdm_tt_ee_lowl
)
ARMS=(
    raw64 physical_o1_64 logamp64
    raw64 physical_o1_64 logamp64
)
CONSOLIDATOR="${CONSOLIDATOR:-scripts/consolidate_precision_preprocess.py}"

fail() {
    echo "[err] $*" >&2
    exit 2
}

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
mkdir -p logs

cell_fields() {
    local cell="$1"
    [[ "${cell}" =~ ^[0-5]$ ]] || return 1
    printf '%s\t%s\n' "${RUNS[${cell}]}" "${ARMS[${cell}]}"
}

artifact_root() {
    printf 'results/%s/%s/%s' "$1" "${STUDY}" "$2"
}

require_file() {
    [[ -f "$1" ]] || fail "required frozen artifact is missing: $1"
}

if [[ "${PRINT_CELLS:-0}" == "1" ]]; then
    printf 'cell\trun\tarm\tmanifest\tcalibration\tconfirmation\n'
    for (( cell=0; cell<6; cell++ )); do
        root="$(artifact_root "${RUNS[${cell}]}" "${ARMS[${cell}]}")"
        printf '%s\t%s\t%s\t%s/selection_manifest.json\t%s/calibration.json\t%s/confirmation.json\n' \
            "${cell}" "${RUNS[${cell}]}" "${ARMS[${cell}]}" \
            "${root}" "${root}" "${root}"
    done
    exit 0
fi

# Checked here, not at the top: PRINT_CELLS above is a static listing of the
# cell matrix and needs no interpreter, so it stays runnable on any machine
# (CSD3 included, where .venv-lightning does not exist).
[[ -x "${PYTHON}" ]] || fail "missing interpreter ${PYTHON}; run bootstrap_env.sh first"

USAGE="usage: $0 {select|calibrate|confirm} <cell 0-5> | render"
MODE="${1:?${USAGE}}"
case "${MODE}" in
    select|calibrate|confirm)
        CELL="${2:-}"
        FIELDS="$(cell_fields "${CELL}")" || \
            fail "${MODE} requires one cell in 0-5"
        IFS=$'\t' read -r RUN ARM <<< "${FIELDS}"
        ROOT="$(artifact_root "${RUN}" "${ARM}")"
        MANIFEST="${ROOT}/selection_manifest.json"
        CALIBRATION="${ROOT}/calibration.json"
        CONFIRMATION="${ROOT}/confirmation.json"
        echo "[consolidate] mode=${MODE} cell=${CELL} run=${RUN} arm=${ARM}"
        ;;
    render)
        [[ $# -eq 1 ]] || fail "render does not accept a cell"
        ;;
    *)
        fail "unknown mode '${MODE}'; ${USAGE}"
        ;;
esac

case "${MODE}" in
    select)
        "${PYTHON}" "${CONSOLIDATOR}" select \
            --run "${RUN}" \
            --arm "${ARM}" \
            --results-root results \
            --out "${MANIFEST}"
        ;;
    calibrate)
        require_file "${MANIFEST}"
        "${PYTHON}" "${CONSOLIDATOR}" calibrate \
            --manifest "${MANIFEST}" \
            --dataset-dir data \
            --models-root models \
            --out "${CALIBRATION}"
        ;;
    confirm)
        require_file "${MANIFEST}"
        require_file "${CALIBRATION}"
        require_file docs/ols_mi_sr_mse_sr_t2_comparison_codex_output.md
        "${PYTHON}" "${CONSOLIDATOR}" confirm \
            --manifest "${MANIFEST}" \
            --calibration "${CALIBRATION}" \
            --dataset-dir data \
            --models-root models \
            --experiments-dir experiments \
            --baseline-report docs/ols_mi_sr_mse_sr_t2_comparison_codex_output.md \
            --out "${CONFIRMATION}"
        ;;
    render)
        CONFIRMATIONS=()
        for (( cell=0; cell<6; cell++ )); do
            root="$(artifact_root "${RUNS[${cell}]}" "${ARMS[${cell}]}")"
            confirmation="${root}/confirmation.json"
            require_file "${confirmation}"
            CONFIRMATIONS+=("${confirmation}")
        done
        echo "[consolidate] mode=render confirmations=${#CONFIRMATIONS[@]}"
        "${PYTHON}" "${CONSOLIDATOR}" render \
            --confirmations "${CONFIRMATIONS[@]}" \
            --out-json experiments/precision_preprocess_v1_comparison.json \
            --out-md docs/precision_preprocess_v1_comparison.md
        ;;
esac
