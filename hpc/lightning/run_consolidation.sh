#!/usr/bin/env bash
#! Scheduler-free equivalent of hpc/slurm_mse_one_stage_consolidate.sh.
#!
#!   bash hpc/lightning/run_consolidation.sh select    lcdm_tt_beta3e-4
#!   bash hpc/lightning/run_consolidation.sh calibrate lcdm_tt_beta3e-4
#!   bash hpc/lightning/run_consolidation.sh confirm   lcdm_tt_beta3e-4
#!
#! Same flags, same artifact paths, same phase ordering contract: select reads
#! T0 only, calibrate reads T1 only, confirm verifies both digests before it
#! opens T2.
set -euo pipefail

PROJ="${PROJ:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
# shellcheck source=/dev/null
source "${PROJ}/hpc/lightning/env.sh"
cd "${PROJ}"

# The usage text lives in a variable: a literal "}" inside ${1:?...}
# would close the expansion early and end up appended to the value.
USAGE="usage: $0 {select|calibrate|confirm} <run-name>"
MODE="${1:?$USAGE}"
RUN="${2:?$USAGE}"
MANIFEST="results/${RUN}/mse_one_stage_selection_manifest.json"
CALIBRATION="results/${RUN}/mse_one_stage_calibration.json"
MI_JOBS="${MI_JOBS:-$(nproc 2>/dev/null || echo 1)}"

[[ -x "${PYTHON}" ]] || { echo "[err] missing interpreter ${PYTHON};" \
    "run hpc/lightning/bootstrap_env.sh first"; exit 1; }
export OMP_NUM_THREADS=1
mkdir -p logs

echo "[consolidate] mode=${MODE} run=${RUN} mi_jobs=${MI_JOBS}"
case "${MODE}" in
    select)
        "${PYTHON}" scripts/consolidate_mse_one_stage.py select \
            --run "${RUN}" \
            --results-root results \
            --manifest "${MANIFEST}"
        ;;
    calibrate)
        "${PYTHON}" scripts/consolidate_mse_one_stage.py calibrate \
            --manifest "${MANIFEST}" \
            --dataset-dir data \
            --models-root models \
            --experiments-dir experiments \
            --out "${CALIBRATION}"
        ;;
    confirm)
        "${PYTHON}" scripts/consolidate_mse_one_stage.py confirm \
            --manifest "${MANIFEST}" \
            --calibration "${CALIBRATION}" \
            --dataset-dir data \
            --models-root models \
            --experiments-dir experiments \
            --n-perm-mi 39 \
            --max-samples-mi 5000 \
            --mi-jobs "${MI_JOBS}" \
            --out "experiments/mse_one_stage_sr_${RUN}"
        ;;
    *)
        echo "[err] unknown mode '${MODE}'; expected select, calibrate, or confirm"
        exit 2
        ;;
esac
