#!/bin/bash
#! Guarded select -> calibrate -> confirm stages for one checkpoint.
#!
#! Submit each stage with afterok dependencies on the preceding stage. Select
#! must depend on BOTH the main-search and shuffled-control arrays:
#!
#!   S=$(sbatch --parsable --dependency=afterok:<mainJID>:<ctlJID> \
#!       hpc/slurm_mse_one_stage_consolidate.sh select lcdm_tt_beta3e-4)
#!   C=$(sbatch --parsable --dependency=afterok:${S} \
#!       hpc/slurm_mse_one_stage_consolidate.sh calibrate lcdm_tt_beta3e-4)
#!   sbatch --dependency=afterok:${C} \
#!       hpc/slurm_mse_one_stage_consolidate.sh confirm lcdm_tt_beta3e-4
#!
#! The packed launcher can execute these modes as job steps under `intr`.
#SBATCH --job-name=mse1_cons
#SBATCH --output=logs/mse1_cons_%j.out
#SBATCH --error=logs/mse1_cons_%j.err
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --partition=icelake
#SBATCH --account=MPHIL-DIS-SL2-CPU
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zx332@cam.ac.uk

set -euo pipefail

PROJ="${PROJ:-/rds/user/zx332/hpc-work/cmb-lcdm-sr}"
# The usage text lives in a variable: a literal "}" inside ${1:?...}
# would close the expansion early and end up appended to the value.
USAGE="usage: $0 {select|calibrate|confirm} <run-name>"
MODE="${1:?$USAGE}"
RUN="${2:?$USAGE}"
MANIFEST="results/${RUN}/mse_one_stage_selection_manifest.json"
CALIBRATION="results/${RUN}/mse_one_stage_calibration.json"

PYTHON="${PROJ}/.venv/bin/python"
[[ -x "${PYTHON}" ]] || { echo "[err] missing interpreter ${PYTHON}"; exit 1; }
export PATH="${PROJ}/.venv/bin:${PATH}"
export PYTHON_JULIAPKG_PROJECT="${PROJ}/.venv/julia_env"
export PYTHON_JULIAPKG_OFFLINE="${PYTHON_JULIAPKG_OFFLINE:-yes}"
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=1

cd "${PROJ}"
mkdir -p logs

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
            --mi-jobs "${SLURM_CPUS_PER_TASK:-16}" \
            --out "experiments/mse_one_stage_sr_${RUN}"
        ;;
    *)
        echo "[err] unknown mode '${MODE}'; expected select, calibrate, or confirm"
        exit 2
        ;;
esac
