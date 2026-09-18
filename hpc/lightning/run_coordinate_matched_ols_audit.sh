#!/usr/bin/env bash
#! Scheduler-free coordinate-matched OLS audit for a Lightning CPU Studio.
#!
#! The precision_preprocess_v1 artifacts are immutable upstream inputs.  This
#! wrapper writes only below coordinate_matched_ols_v1 (plus the two rendered
#! deliverables) and preserves the tier order fit (T0) -> calibrate (T1) ->
#! confirm (T2) -> render.
#!
#!   bash hpc/lightning/run_coordinate_matched_ols_audit.sh fit 0
#!   bash hpc/lightning/run_coordinate_matched_ols_audit.sh calibrate 0
#!   bash hpc/lightning/run_coordinate_matched_ols_audit.sh confirm 0
#!   bash hpc/lightning/run_coordinate_matched_ols_audit.sh render
#!   bash hpc/lightning/run_coordinate_matched_ols_audit.sh all
set -euo pipefail

PROJ="${PROJ:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
LIGHTNING_ENV="${LIGHTNING_ENV:-${PROJ}/hpc/lightning/env.sh}"
# shellcheck source=/dev/null
source "${LIGHTNING_ENV}"
cd "${PROJ}"

STUDY="coordinate_matched_ols_v1"
UPSTREAM_STUDY="precision_preprocess_v1"
RUNS=(
    lcdm_tt_beta3e-4 lcdm_tt_beta3e-4 lcdm_tt_beta3e-4
    lcdm_tt_ee_lowl lcdm_tt_ee_lowl lcdm_tt_ee_lowl
)
ARMS=(
    raw64 physical_o1_64 logamp64
    raw64 physical_o1_64 logamp64
)
AUDITOR="${AUDITOR:-scripts/audit_coordinate_matched_ols.py}"

fail() {
    echo "[err] $*" >&2
    exit 2
}

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

cell_fields() {
    local cell="$1"
    [[ "${cell}" =~ ^[0-5]$ ]] || return 1
    printf '%s\t%s\n' "${RUNS[${cell}]}" "${ARMS[${cell}]}"
}

upstream_root() {
    printf 'results/%s/%s/%s' "$1" "${UPSTREAM_STUDY}" "$2"
}

audit_root() {
    printf 'results/%s/%s/%s' "$1" "${STUDY}" "$2"
}

require_file() {
    [[ -f "$1" ]] || fail "required frozen artifact is missing: $1"
}

if [[ "${PRINT_CELLS:-0}" == "1" ]]; then
    printf 'cell\trun\tarm\tprecision_manifest\tprecision_calibration\tprecision_confirmation\tfit\tcalibration\tconfirmation\n'
    for (( cell=0; cell<6; cell++ )); do
        upstream="$(upstream_root "${RUNS[${cell}]}" "${ARMS[${cell}]}")"
        audit="$(audit_root "${RUNS[${cell}]}" "${ARMS[${cell}]}")"
        printf '%s\t%s\t%s\t%s/selection_manifest.json\t%s/calibration.json\t%s/confirmation.json\t%s/fit.json\t%s/calibration.json\t%s/confirmation.json\n' \
            "${cell}" "${RUNS[${cell}]}" "${ARMS[${cell}]}" \
            "${upstream}" "${upstream}" "${upstream}" \
            "${audit}" "${audit}" "${audit}"
    done
    exit 0
fi

[[ -x "${PYTHON}" ]] || \
    fail "missing interpreter ${PYTHON}; run bootstrap_env.sh first"
[[ -f "${AUDITOR}" ]] || fail "missing audit CLI ${AUDITOR}"

run_cell() {
    local mode="$1"
    local cell="$2"
    local fields run arm upstream audit
    local precision_manifest precision_calibration precision_confirmation
    local fit calibration confirmation

    fields="$(cell_fields "${cell}")" || \
        fail "${mode} requires one cell in 0-5"
    IFS=$'\t' read -r run arm <<< "${fields}"
    upstream="$(upstream_root "${run}" "${arm}")"
    audit="$(audit_root "${run}" "${arm}")"
    precision_manifest="${upstream}/selection_manifest.json"
    precision_calibration="${upstream}/calibration.json"
    precision_confirmation="${upstream}/confirmation.json"
    fit="${audit}/fit.json"
    calibration="${audit}/calibration.json"
    confirmation="${audit}/confirmation.json"

    # The audit namespace must remain disjoint from the frozen precision tree.
    [[ "${audit}" != "${upstream}" ]] || fail "audit/upstream path collision"
    mkdir -p "${audit}"
    echo "[ols-audit] mode=${mode} cell=${cell} run=${run} arm=${arm}"

    case "${mode}" in
        fit)
            require_file "${precision_manifest}"
            "${PYTHON}" "${AUDITOR}" fit \
                --manifest "${precision_manifest}" \
                --dataset-dir data \
                --models-root models \
                --out "${fit}"
            ;;
        calibrate)
            require_file "${fit}"
            "${PYTHON}" "${AUDITOR}" calibrate \
                --fit "${fit}" \
                --dataset-dir data \
                --models-root models \
                --out "${calibration}"
            ;;
        confirm)
            require_file "${fit}"
            require_file "${calibration}"
            require_file "${precision_manifest}"
            require_file "${precision_calibration}"
            require_file "${precision_confirmation}"
            "${PYTHON}" "${AUDITOR}" confirm \
                --fit "${fit}" \
                --calibration "${calibration}" \
                --precision-manifest "${precision_manifest}" \
                --precision-calibration "${precision_calibration}" \
                --precision-confirmation "${precision_confirmation}" \
                --dataset-dir data \
                --models-root models \
                --out "${confirmation}"
            ;;
        *)
            fail "unknown cell mode '${mode}'"
            ;;
    esac
}

render_all() {
    local confirmations=()
    local cell audit confirmation
    for (( cell=0; cell<6; cell++ )); do
        audit="$(audit_root "${RUNS[${cell}]}" "${ARMS[${cell}]}")"
        confirmation="${audit}/confirmation.json"
        require_file "${confirmation}"
        confirmations+=("${confirmation}")
    done
    echo "[ols-audit] mode=render confirmations=${#confirmations[@]}"
    "${PYTHON}" "${AUDITOR}" render \
        --confirmations "${confirmations[@]}" \
        --out-json experiments/coordinate_matched_ols_v1.json \
        --out-md experiments/coordinate_matched_ols_v1.md
}

USAGE="usage: $0 {fit|calibrate|confirm} <cell 0-5> | render | all"
MODE="${1:-}"
case "${MODE}" in
    fit|calibrate|confirm)
        [[ $# -eq 2 ]] || fail "${USAGE}"
        run_cell "${MODE}" "$2"
        ;;
    render)
        [[ $# -eq 1 ]] || fail "${USAGE}"
        render_all
        ;;
    all)
        [[ $# -eq 1 ]] || fail "${USAGE}"
        for stage in fit calibrate confirm; do
            for (( cell=0; cell<6; cell++ )); do
                run_cell "${stage}" "${cell}"
            done
        done
        render_all
        ;;
    *)
        fail "${USAGE}"
        ;;
esac
