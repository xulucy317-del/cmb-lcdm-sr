#!/usr/bin/env bash
#! Run a launcher's tasks without SLURM: on a workstation, inside a PBS/LSF/SGE
#! job, or on any node you already hold.
#!
#!   hpc/run_tasks.sh [--tasks 0-35 | --tasks 3,7,9] [--parallel N] [--cpus 16]
#!                    hpc/slurm_<launcher>.sh [launcher args]
#!
#! Examples:
#!   hpc/run_tasks.sh hpc/slurm_blind_sr.sh models/lcdm_tt_beta3e-4 2 "A_s tau" 0
#!   hpc/run_tasks.sh --tasks 0-35 --parallel 2 hpc/slurm_hpsweep_sr.sh results/lcdm_tt_beta3e-4/hpsweep_hp_v1
#!   hpc/run_tasks.sh --tasks 0-164 hpc/slurm_mse_one_stage_sr.sh
#!
#! Every hpc/slurm_*.sh launcher except slurm_mse_one_stage_pack.sh is plain
#! bash once SLURM's variables are supplied: the #SBATCH lines are comments,
#! and the array launchers pick their task from SLURM_ARRAY_TASK_ID. This
#! script sets those variables and runs the launcher under bash, one task at a
#! time or --parallel N at a time, logging each task to logs/. A task whose
#! report.json already exists is skipped by the launcher itself, so a run can
#! be resumed by repeating the command.
#!
#! Inside another scheduler's job array, map its index instead:
#!   SLURM_ARRAY_TASK_ID=$PBS_ARRAY_INDEX bash hpc/slurm_<launcher>.sh args   # PBS
#!   SLURM_ARRAY_TASK_ID=$LSB_JOBINDEX    bash hpc/slurm_<launcher>.sh args   # LSF
#!   SLURM_ARRAY_TASK_ID=$SGE_TASK_ID     bash hpc/slurm_<launcher>.sh args   # SGE
#! (together with PROJ=<repo root>; see hpc/README.md).
#!
#! Reads hpc/site.env for PROJ, SHARDS_ROOT, SLURM_ACCOUNT and TASK_CPUS.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${HERE}/.." && pwd)"
# shellcheck disable=SC1091
[[ -f "${HERE}/site.env" ]] && source "${HERE}/site.env"
PROJ="${PROJ:-${REPO_ROOT}}"

tasks=""
parallel=1
cpus="${TASK_CPUS:-16}"
launcher=""
launcher_args=()
while [[ $# -gt 0 ]]; do
    if [[ -n "${launcher}" ]]; then
        launcher_args+=("$1"); shift; continue
    fi
    case "$1" in
        --tasks)    tasks="$2"; shift 2 ;;
        --tasks=*)  tasks="${1#*=}"; shift ;;
        --parallel) parallel="$2"; shift 2 ;;
        --parallel=*) parallel="${1#*=}"; shift ;;
        --cpus)     cpus="$2"; shift 2 ;;
        --cpus=*)   cpus="${1#*=}"; shift ;;
        -h|--help)  sed -n 's/^#! \{0,1\}//p' "${BASH_SOURCE[0]}"; exit 0 ;;
        *.sh)       launcher="$1"; shift ;;
        *)          echo "[run_tasks] unknown option: $1" >&2; exit 2 ;;
    esac
done
[[ -n "${launcher}" ]] || { sed -n 's/^#! \{0,1\}//p' "${BASH_SOURCE[0]}" >&2; exit 2; }
[[ -f "${launcher}" ]] || { echo "[run_tasks] launcher not found: ${launcher}" >&2; exit 2; }
launcher="$(cd "$(dirname "${launcher}")" && pwd)/$(basename "${launcher}")"
name="$(basename "${launcher}" .sh)"

# Expand "0-35" / "3,7,9" / "0-3,10" into a list of task ids.
ids=()
if [[ -n "${tasks}" ]]; then
    IFS=',' read -r -a parts <<< "${tasks}"
    for part in "${parts[@]}"; do
        if [[ "${part}" =~ ^([0-9]+)-([0-9]+)$ ]]; then
            for ((i = BASH_REMATCH[1]; i <= BASH_REMATCH[2]; i++)); do ids+=("${i}"); done
        elif [[ "${part}" =~ ^[0-9]+$ ]]; then
            ids+=("${part}")
        else
            echo "[run_tasks] bad --tasks entry: ${part}" >&2; exit 2
        fi
    done
fi

export PROJ
[[ -n "${SHARDS_ROOT:-}" ]] && export SHARDS_ROOT
[[ -n "${SLURM_ACCOUNT:-}" ]] && export ACCOUNT="${SLURM_ACCOUNT}"
cd "${PROJ}"
mkdir -p logs

run_one() {
    # $1 = task id, or "" for a launcher that is not an array
    local id="$1" log
    if [[ -n "${id}" ]]; then
        log="logs/${name}_task${id}.out"
        echo "[run_tasks] ${name} task ${id} -> ${log}"
        SLURM_ARRAY_TASK_ID="${id}" SLURM_ARRAY_JOB_ID="local" \
        SLURM_JOB_ID="local-${id}" SLURM_CPUS_PER_TASK="${cpus}" \
        SLURM_RESTART_COUNT=0 SLURM_JOB_ACCOUNT="${ACCOUNT:-}" \
            bash "${launcher}" ${launcher_args[@]+"${launcher_args[@]}"} > "${log}" 2>&1
    else
        log="logs/${name}_$(date +%Y%m%d-%H%M%S).out"
        echo "[run_tasks] ${name} -> ${log}"
        SLURM_JOB_ID="local-$$" SLURM_CPUS_PER_TASK="${cpus}" \
        SLURM_RESTART_COUNT=0 SLURM_JOB_ACCOUNT="${ACCOUNT:-}" \
            bash "${launcher}" ${launcher_args[@]+"${launcher_args[@]}"} > "${log}" 2>&1
    fi
}

# Internal re-entry used by the parallel runner below (one task per process).
if [[ "${RUN_TASKS_ONE:-}" == "1" ]]; then
    run_one "${RUN_TASKS_ID}"
    exit $?
fi

if [[ ${#ids[@]} -eq 0 ]]; then
    run_one ""
    exit $?
fi

# xargs -P runs up to --parallel tasks at once and exits non-zero (123) if any
# task failed; the per-task logs say which. (bash 3.2 has no `wait -n`.)
export RUN_TASKS_ONE=1
status=0
printf '%s\n' "${ids[@]}" | xargs -P "${parallel}" -I{} env RUN_TASKS_ID={} \
    bash "${BASH_SOURCE[0]}" --cpus "${cpus}" "${launcher}" \
    ${launcher_args[@]+"${launcher_args[@]}"} || status=$?
if [[ ${status} -eq 0 ]]; then
    echo "[run_tasks] ${#ids[@]} task(s) finished, none failed"
else
    echo "[run_tasks] ${#ids[@]} task(s) finished, some FAILED (see logs/${name}_task*.out)" >&2
fi
exit ${status}
