#!/bin/bash
#! Phase-6 consolidation (docs/discovery_roadmap.md): apply the frozen
#! Phase 1-3 machinery to the residual-SR fronts — knee/clusters/R_SR for
#! f2, hierarchical combined eta, stage-2 residual audit, shuffled-residual
#! control, DoD amplitude check. GMM-MI permutation nulls need a compute
#! node (login-node pools get SIGKILLed).
#!
#! Positional args:
#!   1 RUN_NAME  (e.g. lcdm_tt_beta3e-4)
#!   2 VARIANT   ("" = frozen Phase-6 additive; "ia" = interaction-aware
#!               follow-up on results/<run>/residual_sr_ia)
#!
#!   sbatch hpc/slurm_residual_consolidate.sh lcdm_tt_beta3e-4
#!   sbatch hpc/slurm_residual_consolidate.sh lcdm_tt_ee_lowl  ia
#!
#! Output: experiments/residual_sr[_ia]_<run>.{md,json}
#!
#SBATCH --job-name=res_consol
#SBATCH --output=logs/res_consol_%j.out
#SBATCH --error=logs/res_consol_%j.err
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

RUN_NAME="${1:?usage: sbatch hpc/slurm_residual_consolidate.sh <run-name> [variant]}"
VARIANT="${2:-}"

cd "${PROJ}"; mkdir -p logs

echo "[run] consolidate residual SR for ${RUN_NAME} variant='${VARIANT}'"
python scripts/consolidate_residual_sr.py --run "${RUN_NAME}" \
    --variant "${VARIANT}" --jobs 6 --mi-jobs 5
