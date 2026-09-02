#!/usr/bin/env bash
#! Step 2 of the staged nonlinearity plan (claude comparison doc §6.4):
#! blind SR on the exact OLS-stage-1 residual for the two latents the
#! quadratic pilot flagged as beyond-second-order — TT+EE z0 and z4.
#!
#! Frozen stage-2 protocol: gmm_mi inner loss, 6 raw inputs, 5000 samples,
#! ni200/pop15/ms20, seeds 0-4, plus 2 shuffled-residual controls per latent.
#! Sequential, resumable (skip-if-report-exists). Run on the Lightning studio:
#!
#!   nohup bash hpc/lightning/run_residual_sr_ols.sh \
#!       > logs/residual_sr_ols_driver.log 2>&1 &
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
source hpc/lightning/env.sh

RUN=models/lcdm_tt_ee_lowl
NAME=lcdm_tt_ee_lowl
mkdir -p logs

for K in 0 4; do
    CACHE="${RUN}/analysis/residual_ols_z${K}_v1.npy"
    [[ -f "${CACHE}" ]] || { echo "[err] ${CACHE} missing — run scripts/build_ols_residual_cache.py"; exit 1; }
done

for K in 0 4; do
    for S in 0 1 2 3 4; do
        OUT="results/${NAME}/residual_sr_ols/z${K}_seed${S}"
        if [[ -f "${OUT}/report.json" ]]; then echo "[skip] ${OUT}"; continue; fi
        echo "[run] z${K} seed${S} start $(date -u +%FT%TZ)"
        "${PYTHON}" scripts/run_blind_sr.py \
            --run-dir "${RUN}" --dataset-dir data \
            --target-npy "${RUN}/analysis/residual_ols_z${K}_v1.npy" \
            --target-label "res_ols_z${K}" \
            --inputs omega_b omega_cdm H0 tau A_s n_s \
            --n-samples 5000 --niterations 200 \
            --turbo --parallelism multithreading \
            --seed "${S}" --out-dir "${OUT}"
        echo "[ok]  z${K} seed${S} done  $(date -u +%FT%TZ)"
    done
done

for K in 0 4; do
    for S in 0 1; do
        OUT="results/${NAME}/residual_sr_ols/shuffled_res_ols_z${K}_s${S}"
        if [[ -f "${OUT}/report.json" ]]; then echo "[skip] ${OUT}"; continue; fi
        echo "[ctl] z${K} shuffle${S} start $(date -u +%FT%TZ)"
        "${PYTHON}" scripts/run_shuffled_control.py \
            --run-dir "${RUN}" --dataset-dir data \
            --target-npy "${RUN}/analysis/residual_ols_z${K}_v1.npy" \
            --target-label "res_ols_z${K}" \
            --shuffle-seed "${S}" --pysr-seed "${S}" \
            --inputs omega_b omega_cdm H0 tau A_s n_s \
            --turbo --parallelism multithreading \
            --out-dir "${OUT}"
        echo "[ok]  z${K} shuffle${S} done  $(date -u +%FT%TZ)"
    done
done
echo "[done] all 14 step-2 tasks complete $(date -u +%FT%TZ)"
