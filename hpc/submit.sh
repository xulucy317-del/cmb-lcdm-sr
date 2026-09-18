#!/usr/bin/env bash
#! Submit any hpc/slurm_*.sh launcher on a SLURM cluster other than CSD3.
#!
#!   hpc/submit.sh [sbatch options] hpc/slurm_<launcher>.sh [launcher args]
#!
#! Examples:
#!   hpc/submit.sh hpc/slurm_blind_sr.sh models/lcdm_tt_beta3e-4 2 "A_s tau" 0
#!   hpc/submit.sh --array=0-35%16 hpc/slurm_hpsweep_sr.sh results/lcdm_tt_beta3e-4/hpsweep_hp_v1
#!   DRY_RUN=1 hpc/submit.sh hpc/slurm_subspace_probe.sh      # print the sbatch line only
#!
#! The launchers are kept exactly as they ran on CSD3: their #SBATCH lines name
#! CSD3's account, partition and notification address, and their PROJ default
#! is the CSD3 path. sbatch command-line options take precedence over #SBATCH
#! lines, so this wrapper reads hpc/site.env (copy hpc/site.env.example) and
#! passes your site's values on the command line, plus PROJ, SHARDS_ROOT and
#! ACCOUNT through --export. Nothing in hpc/slurm_*.sh needs editing.
#!
#! Everything before the first argument ending in ".sh" is handed to sbatch
#! (e.g. --array=..., --time=...); everything after it goes to the launcher.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${HERE}/.." && pwd)"

# shellcheck disable=SC1091
[[ -f "${HERE}/site.env" ]] && source "${HERE}/site.env"
PROJ="${PROJ:-${REPO_ROOT}}"

sbatch_opts=()
launcher=""
launcher_args=()
for arg in "$@"; do
    if [[ -z "${launcher}" ]]; then
        if [[ "${arg}" == *.sh ]]; then
            launcher="${arg}"
        else
            sbatch_opts+=("${arg}")
        fi
    else
        launcher_args+=("${arg}")
    fi
done
if [[ -z "${launcher}" ]]; then
    echo "usage: hpc/submit.sh [sbatch options] hpc/slurm_<launcher>.sh [launcher args]" >&2
    exit 2
fi
[[ -f "${launcher}" ]] || { echo "[submit] launcher not found: ${launcher}" >&2; exit 2; }
launcher="$(cd "$(dirname "${launcher}")" && pwd)/$(basename "${launcher}")"

site_opts=()
[[ -n "${SLURM_ACCOUNT:-}" ]] && site_opts+=("--account=${SLURM_ACCOUNT}")
[[ -n "${SLURM_PARTITION:-}" ]] && site_opts+=("--partition=${SLURM_PARTITION}")
if [[ -n "${MAIL_USER:-}" ]]; then
    site_opts+=("--mail-user=${MAIL_USER}" "--mail-type=FAIL")
else
    site_opts+=("--mail-type=NONE")
fi
if [[ -n "${SLURM_EXTRA:-}" ]]; then
    # shellcheck disable=SC2206
    extra=(${SLURM_EXTRA})
    site_opts+=(${extra[@]+"${extra[@]}"})
fi

# The launchers read PROJ (project root), SHARDS_ROOT (encoder pass) and, for
# the precision-campaign launchers, ACCOUNT (must equal the job's account).
export_list="ALL,PROJ=${PROJ}"
[[ -n "${SHARDS_ROOT:-}" ]] && export_list+=",SHARDS_ROOT=${SHARDS_ROOT}"
[[ -n "${SLURM_ACCOUNT:-}" ]] && export_list+=",ACCOUNT=${SLURM_ACCOUNT}"

cmd=(sbatch ${site_opts[@]+"${site_opts[@]}"} "--export=${export_list}" ${sbatch_opts[@]+"${sbatch_opts[@]}"} "${launcher}" ${launcher_args[@]+"${launcher_args[@]}"})

if [[ -n "${DRY_RUN:-}" ]]; then
    printf '%q ' "${cmd[@]}"; echo
    exit 0
fi
cd "${PROJ}"
mkdir -p logs
exec "${cmd[@]}"
