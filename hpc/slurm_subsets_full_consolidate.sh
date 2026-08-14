#!/bin/bash
#! R-P4 consolidation (docs/discovery_roadmap.md, "Post-closure
#! pre-registration (2026-08-13) — R-P4"): budget-matched readout M_S^(c<=10)
#! over the complete 63-support grid, then the frozen two-stage
#! select-then-confirm rule. The T2 confirmation leg re-scores each seed's
#! best-at-c<=10 form with full GMM-MI, which wants a compute node
#! (login-node pools get SIGKILLed).
#!
#! Positional args:
#!   1 RUN_NAME  (e.g. lcdm_tt_beta3e-4)
#!
#!   sbatch hpc/slurm_subsets_full_consolidate.sh lcdm_tt_beta3e-4
#!   sbatch hpc/slurm_subsets_full_consolidate.sh lcdm_tt_ee_lowl
#!
#! Output: experiments/subsets_full_<run>.{md,json}
#!
#! The sham-control leg (scripts/consolidate_sham_control.py) reads M^(c<=10)
#! straight off the existing reports and fits nothing, so it runs fine on a
#! login node and has no wrapper here.
#!
#SBATCH --job-name=subs_consol
#SBATCH --output=logs/subs_consol_%j.out
#SBATCH --error=logs/subs_consol_%j.err
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=36
#SBATCH --mem=48G
#SBATCH --partition=icelake
#SBATCH --account=MPHIL-DIS-SL2-CPU
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zx332@cam.ac.uk

PROJ="${PROJ:-/rds/user/zx332/hpc-work/cmb-lcdm-sr}"

set +u; source ~/.bashrc; source "${PROJ}/.venv/bin/activate"
set -euo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=1

RUN_NAME="${1:?usage: sbatch hpc/slurm_subsets_full_consolidate.sh <run-name>}"

cd "${PROJ}"; mkdir -p logs

echo "[run] consolidate exhaustive-support grid for ${RUN_NAME}"
python scripts/consolidate_subsets_full.py --run "${RUN_NAME}"
