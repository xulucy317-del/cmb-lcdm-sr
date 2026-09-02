#!/usr/bin/env bash
set -uo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${PROJECT_DIR}"

JULIA_EXE="${PROJECT_DIR}/.julia-bin/Julia-1.11.app/Contents/Resources/julia/bin/julia"
JULIA_PROJECT="${PROJECT_DIR}/.venv-lightning/julia_env"
PYTHON_EXE="${PROJECT_DIR}/.venv-lightning/bin/python"
LEDGER="logs/precision_preprocess_mac_m2_seed234_ledger.jsonl"
WORKER_LOG_DIR="logs/precision_preprocess_mac_m2_seed234"
BATCH_SIZE=10

export PYTHONUNBUFFERED=1
export PYTHON_JULIAPKG_EXE="${JULIA_EXE}"
export PYTHON_JULIAPKG_PROJECT="${JULIA_PROJECT}"
export PYTHON_JULIAPKG_OFFLINE=yes
export JULIA_PKG_OFFLINE=true
export PYTHON_JULIACALL_THREADS=4
export JULIA_NUM_THREADS=4
export PYTHON_JULIACALL_HANDLE_SIGNALS=yes

task_ids=()
for ((task_id = 0; task_id < 330; task_id++)); do
    remainder=$((task_id % 5))
    if ((remainder == 2 || remainder == 3 || remainder == 4)); then
        task_ids+=("${task_id}")
    fi
done
task_spec="$(IFS=,; printf '%s' "${task_ids[*]}")"

while true; do
    preflight="$(${PYTHON_EXE} scripts/run_precision_preprocess_pool.py \
        --task-ids "${task_spec}" --limit 1 --dry-run 2>&1)"
    preflight_status=$?
    printf '%s\n' "${preflight}"
    if ((preflight_status != 0)); then
        exit "${preflight_status}"
    fi
    if [[ "${preflight}" == *"[dry-run] 0 task(s) would run"* ]]; then
        printf '%s\n' "[batched] all assigned tasks are complete"
        exit 0
    fi

    session_stamp="$(date -u +%Y%m%dT%H%M%SZ)"
    session_log="logs/precision_preprocess_mac_m2_seed234_batch_${session_stamp}.out"
    printf '%s\n' "[batched] starting up to ${BATCH_SIZE} tasks -> ${session_log}"
    ${PYTHON_EXE} scripts/run_precision_preprocess_pool.py \
        --task-ids "${task_spec}" \
        --workers 2 \
        --threads 4 \
        --limit "${BATCH_SIZE}" \
        --ledger "${LEDGER}" \
        --worker-log-dir "${WORKER_LOG_DIR}" \
        >>"${session_log}" 2>&1
    session_status=$?
    if ((session_status != 0)); then
        printf '%s\n' \
            "[batched] session failed with status ${session_status}; stopping"
        exit "${session_status}"
    fi
done
