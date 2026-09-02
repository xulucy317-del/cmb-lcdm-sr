#!/usr/bin/env bash
#! Resume precision_preprocess_v1 on one persistent Lightning CPU Studio.
#!
#!   WORKERS=2 THREADS=2 bash hpc/lightning/resume_precision_preprocess.sh
#!   TIME_BUDGET_MINUTES=210 bash hpc/lightning/resume_precision_preprocess.sh
#!
#! Search reports are validated before they are skipped. Consolidation cannot
#! start until the dry-run audit proves both zero pending and zero invalid.
#! Re-running this command resumes searches and immutable consolidation files.
set -euo pipefail

PROJ="${PROJ:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
LIGHTNING_ENV="${LIGHTNING_ENV:-${PROJ}/hpc/lightning/env.sh}"
# shellcheck source=/dev/null
source "${LIGHTNING_ENV}"
cd "${PROJ}"
mkdir -p logs

POOL_SCRIPT="${POOL_SCRIPT:-scripts/run_precision_preprocess_pool.py}"
CONSOLIDATION_SCRIPT="${CONSOLIDATION_SCRIPT:-hpc/lightning/run_precision_preprocess_consolidation.sh}"
LEDGER="${LEDGER:-logs/precision_preprocess_pool_ledger.jsonl}"
WORKERS="${WORKERS:-2}"
THREADS="${THREADS:-2}"

fail() {
    echo "[err] $*" >&2
    exit 2
}

[[ -x "${PYTHON}" ]] || fail "missing interpreter ${PYTHON}; run bootstrap_env.sh first"
[[ "${WORKERS}" =~ ^[1-9][0-9]*$ ]] || fail "WORKERS must be a positive integer"
[[ "${THREADS}" =~ ^[1-9][0-9]*$ ]] || fail "THREADS must be a positive integer"
[[ -f "${CONSOLIDATION_SCRIPT}" ]] || fail "missing ${CONSOLIDATION_SCRIPT}"

POOL_ARGS=(
    --workers "${WORKERS}"
    --threads "${THREADS}"
    --ledger "${LEDGER}"
)
[[ -n "${TIME_BUDGET_MINUTES:-}" ]] && \
    POOL_ARGS+=(--time-budget-minutes "${TIME_BUDGET_MINUTES}")
[[ -n "${TASK_IDS:-}" ]] && POOL_ARGS+=(--task-ids "${TASK_IDS}")
[[ -n "${RECYCLE_AFTER:-}" ]] && POOL_ARGS+=(--recycle-after "${RECYCLE_AFTER}")

echo "[resume] === stage 1/4: 330 resumable searches ==="
"${PYTHON}" "${POOL_SCRIPT}" "${POOL_ARGS[@]}"

set +e
AUDIT_OUTPUT="$("${PYTHON}" "${POOL_SCRIPT}" --dry-run 2>&1)"
AUDIT_RC=$?
set -e
printf '%s\n' "${AUDIT_OUTPUT}"

PENDING="$(printf '%s\n' "${AUDIT_OUTPUT}" \
    | sed -nE 's/^\[dry-run\] ([0-9]+) task\(s\) would run$/\1/p' \
    | tail -n 1)"
INVALID="$(printf '%s\n' "${AUDIT_OUTPUT}" \
    | sed -nE 's/.*[ ,]([0-9]+) invalid.*/\1/p' \
    | tail -n 1)"
[[ "${PENDING}" =~ ^[0-9]+$ ]] || fail "pool dry-run did not report pending count"
[[ "${INVALID}" =~ ^[0-9]+$ ]] || fail "pool dry-run did not report invalid count"

if (( INVALID > 0 )); then
    fail "${INVALID} invalid report(s); inspect them before any consolidation"
fi
if (( AUDIT_RC != 0 )); then
    fail "pool dry-run failed with status ${AUDIT_RC}"
fi
if (( PENDING > 0 )); then
    echo "[resume] ${PENDING} task(s) remain; consolidation is gated. Re-run to continue."
    exit 0
fi

echo "[resume] === stage 2/4: six T0 selections ==="
for cell in 0 1 2 3 4 5; do
    bash "${CONSOLIDATION_SCRIPT}" select "${cell}"
done

echo "[resume] === stage 3/4: six T1 calibrations ==="
for cell in 0 1 2 3 4 5; do
    bash "${CONSOLIDATION_SCRIPT}" calibrate "${cell}"
done

echo "[resume] === stage 4/4: six T2 confirmations, then render ==="
for cell in 0 1 2 3 4 5; do
    bash "${CONSOLIDATION_SCRIPT}" confirm "${cell}"
done
bash "${CONSOLIDATION_SCRIPT}" render

echo "[resume] complete"
ls -l experiments/precision_preprocess_v1_comparison.json \
      docs/precision_preprocess_v1_comparison.md 2>/dev/null || true
