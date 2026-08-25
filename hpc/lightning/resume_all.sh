#!/usr/bin/env bash
#! One resumable command for the whole remaining experiment on one machine.
#!
#!   bash hpc/lightning/resume_all.sh                 # run until done
#!   TIME_BUDGET_MINUTES=210 bash hpc/lightning/resume_all.sh
#!   WORKERS=2 THREADS=2 bash hpc/lightning/resume_all.sh
#!
#! Stage order matches hpc/slurm_mse_one_stage_pack.sh: all 165 main searches,
#! then the 12 shuffled controls, then select -> calibrate -> confirm for both
#! checkpoints. Searches are skipped when a valid report.json exists, so
#! re-running after a studio shutdown continues where it stopped. The
#! consolidation stages only start once their inputs are all present.
set -euo pipefail

PROJ="${PROJ:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
# shellcheck source=/dev/null
source "${PROJ}/hpc/lightning/env.sh"
cd "${PROJ}"
mkdir -p logs

RUNS=(lcdm_tt_beta3e-4 lcdm_tt_ee_lowl)
WORKERS="${WORKERS:-1}"
THREADS="${THREADS:-}"
POOL_ARGS=(--workers "${WORKERS}")
[[ -n "${THREADS}" ]] && POOL_ARGS+=(--threads "${THREADS}")
[[ -n "${TIME_BUDGET_MINUTES:-}" ]] && \
    POOL_ARGS+=(--time-budget-minutes "${TIME_BUDGET_MINUTES}")

[[ -x "${PYTHON}" ]] || { echo "[err] missing interpreter ${PYTHON};" \
    "run hpc/lightning/bootstrap_env.sh first"; exit 1; }

pending_count() {   # family -> number of tasks still to run
    "${PYTHON}" scripts/run_mse_one_stage_pool.py --family "$1" --dry-run \
        | awk '/task\(s\) would run/ {print $2}'
}

echo "[resume] === stage 1/3: searches ==="
"${PYTHON}" scripts/run_mse_one_stage_pool.py --family main "${POOL_ARGS[@]}"
"${PYTHON}" scripts/run_mse_one_stage_pool.py --family control "${POOL_ARGS[@]}"

for family in main control; do
    left="$(pending_count "${family}")"
    if [[ "${left}" != "0" ]]; then
        echo "[resume] ${family}: ${left} task(s) still pending — consolidation"
        echo "[resume] needs the complete matrix. Re-run this script to continue."
        exit 0
    fi
done

echo "[resume] === stage 2/3: select + calibrate (T0, then T1) ==="
for run in "${RUNS[@]}"; do
    bash hpc/lightning/run_consolidation.sh select "${run}"
done
for run in "${RUNS[@]}"; do
    bash hpc/lightning/run_consolidation.sh calibrate "${run}"
done

echo "[resume] === stage 3/3: confirm (opens T2 once) ==="
for run in "${RUNS[@]}"; do
    bash hpc/lightning/run_consolidation.sh confirm "${run}"
done

echo "[resume] complete. Result artifacts:"
for run in "${RUNS[@]}"; do
    ls -l "experiments/mse_one_stage_sr_${run}.json" \
          "experiments/mse_one_stage_sr_${run}.md" 2>/dev/null || true
done
