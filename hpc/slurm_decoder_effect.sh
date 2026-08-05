#!/bin/bash
#! Phase-7b (docs/discovery_roadmap.md): one streaming pass over the train
#! shards for the data-driven parameter templates (skipped if the cache
#! already exists), then the decoder-effect triangulation for both models.
#!
#!   sbatch hpc/slurm_decoder_effect.sh
#!
#! Outputs: data/spectral_templates_v1.npz,
#!          experiments/decoder_effect_<run>.{md,json},
#!          experiments/decoder_effect_<run>_curves.{png,npz}
#!
#SBATCH --job-name=decoder_fx
#SBATCH --output=logs/decoder_fx_%j.out
#SBATCH --error=logs/decoder_fx_%j.err
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --partition=icelake
#SBATCH --account=MPHIL-DIS-SL2-CPU
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zx332@cam.ac.uk

PROJ="${PROJ:-/rds/user/zx332/hpc-work/cmb-lcdm-sr}"

set +u; source ~/.bashrc; source "${PROJ}/.venv/bin/activate"
set -euo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=4

cd "${PROJ}"; mkdir -p logs

if [[ -f data/spectral_templates_v1.npz ]]; then
    echo "[skip] data/spectral_templates_v1.npz already exists"
else
    python scripts/spectral_templates.py
fi

python scripts/decoder_effect.py --run lcdm_tt_beta3e-4
python scripts/decoder_effect.py --run lcdm_tt_ee_lowl
