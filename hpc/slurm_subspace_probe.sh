#!/bin/bash
#! Phase-8 subspace probe (docs/discovery_roadmap.md): sparse linear probe
#! Z -> f per discovered coordinate (lasso path, 1-SE minimal carrier set,
#! T2 confirmation) + slab-conditional GMM-MI redundancy between the two
#! strongest carriers. GMM-MI needs a compute node (login-node pools get
#! SIGKILLed).
#!
#! Positional args:
#!   1 RUN_NAME  (e.g. lcdm_tt_beta3e-4)
#!
#!   sbatch hpc/slurm_subspace_probe.sh lcdm_tt_beta3e-4
#!   sbatch hpc/slurm_subspace_probe.sh lcdm_tt_ee_lowl
#!
#! Output: experiments/subspace_probe_<run>.{md,json}
#!
#SBATCH --job-name=subspace
#SBATCH --output=logs/subspace_%j.out
#SBATCH --error=logs/subspace_%j.err
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --partition=icelake
#SBATCH --account=MPHIL-DIS-SL2-CPU
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zx332@cam.ac.uk

PROJ="${PROJ:-/rds/user/zx332/hpc-work/cmb-lcdm-sr}"

set +u; source ~/.bashrc; source "${PROJ}/.venv/bin/activate"
set -euo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=1

RUN_NAME="${1:?usage: sbatch hpc/slurm_subspace_probe.sh <run-name>}"

cd "${PROJ}"; mkdir -p logs

echo "[run] subspace probe for ${RUN_NAME}"
python scripts/subspace_probe.py --run "${RUN_NAME}" --jobs 6
