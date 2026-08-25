#!/usr/bin/env bash
#! Shared environment for scheduler-free execution (Lightning AI Studio or any
#! single CPU box). Source it; do not execute it.
#!
#!   source hpc/lightning/env.sh
#!
#! Overridable: PROJ, LIGHTNING_VENV, JULIA_NUM_THREADS, PYTHON_JULIAPKG_OFFLINE.

if [[ -z "${PROJ:-}" ]]; then
    _env_src="${BASH_SOURCE[0]:-$0}"
    PROJ="$(cd "$(dirname "${_env_src}")/../.." && pwd)"
    unset _env_src
fi
export PROJ

export LIGHTNING_VENV="${LIGHTNING_VENV:-${PROJ}/.venv-lightning}"
export PYTHON="${PYTHON:-${LIGHTNING_VENV}/bin/python}"
export PATH="${LIGHTNING_VENV}/bin:${PATH}"

# The Julia depot/project for this checkout. bootstrap_env.sh seeds it from
# hpc/lightning/julia_env_reference/ so package resolution starts from the
# CSD3-frozen Manifest.
export PYTHON_JULIAPKG_PROJECT="${PYTHON_JULIAPKG_PROJECT:-${LIGHTNING_VENV}/julia_env}"
export PYTHON_JULIAPKG_OFFLINE="${PYTHON_JULIAPKG_OFFLINE:-yes}"

# PySR searches with Julia threads. One thread per available core is the
# default; scripts/run_mse_one_stage_pool.py overrides this per worker.
if [[ -z "${JULIA_NUM_THREADS:-}" ]]; then
    JULIA_NUM_THREADS="$(nproc 2>/dev/null || echo 1)"
fi
export JULIA_NUM_THREADS
export PYTHONUNBUFFERED=1
