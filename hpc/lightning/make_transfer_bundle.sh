#!/usr/bin/env bash
#! Pack everything the MSE one-stage resume needs, from CSD3 to any CPU box.
#!
#!   bash hpc/lightning/make_transfer_bundle.sh
#!   OUT=/some/where/bundle.tar.gz bash hpc/lightning/make_transfer_bundle.sh
#!
#! Includes: code, tests, the pinned environment reference, data/, models/
#! (with the cached encoder means and residual/f1hat vectors), experiments/,
#! the legacy GMM-MI `allparams` fronts that `mi20-mi` / `mi20-mse` reuse, and
#! every existing mse_one_stage result directory. Excludes logs, .git, the
#! shared .venv, the paper, and result families this experiment does not read.
#!
#! Writes <bundle>.tar.gz, <bundle>.tar.gz.sha256 and <bundle>.manifest.txt.
set -euo pipefail
shopt -s nullglob

PROJ="${PROJ:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "${PROJ}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="${OUT:-${PROJ}/../cmb-lcdm-sr-mse-one-stage-${STAMP}.tar.gz}"
mkdir -p "$(dirname "${OUT}")"
OUT="$(cd "$(dirname "${OUT}")" && pwd)/$(basename "${OUT}")"
PYTHON="${PYTHON:-${PROJ}/.venv/bin/python}"
STATE="experiments/mse_one_stage_state_csd3.json"

echo "[pack] project = ${PROJ}"
echo "[pack] output  = ${OUT}"

# 1. Freeze the source-side state so the target machine can prove it matches.
if [[ -x "${PYTHON}" ]]; then
    echo "[pack] recording source-machine state -> ${STATE}"
    "${PYTHON}" scripts/verify_mse_one_stage_state.py --json "${STATE}" >/dev/null
else
    echo "[pack] WARNING: ${PYTHON} not executable; skipping the state artifact"
fi

# 2. Assemble the path list.
PATHS=(
    pyproject.toml requirements.txt README.md .gitignore
    src scripts hpc tests docs
    data models experiments
)
for run in lcdm_tt_beta3e-4 lcdm_tt_ee_lowl; do
    for dir in "results/${run}/allparams" \
               "results/${run}"/mse_one_stage_ms* \
               "results/${run}"/mse_one_stage_control_ms*; do
        [[ -d "${dir}" ]] && PATHS+=("${dir}")
    done
done

MISSING=0
for path in "${PATHS[@]}"; do
    [[ -e "${path}" ]] || { echo "[pack] MISSING ${path}"; MISSING=1; }
done
(( MISSING == 0 )) || { echo "[pack] refusing to pack an incomplete tree"; exit 1; }

# 3. Pack.
tar --create --gzip --file "${OUT}" \
    --exclude='__pycache__' --exclude='*.pyc' --exclude='.pytest_cache' \
    --exclude='data/shards_*' --exclude='.DS_Store' \
    "${PATHS[@]}"

# 4. Checksums and a human-readable manifest.
( cd "$(dirname "${OUT}")" && sha256sum "$(basename "${OUT}")" ) \
    > "${OUT}.sha256"
{
    echo "bundle        : $(basename "${OUT}")"
    echo "created_utc   : ${STAMP}"
    echo "source_host   : $(hostname)"
    echo "source_path   : ${PROJ}"
    echo "git_revision  : $(git rev-parse HEAD 2>/dev/null || echo unknown)"
    echo "git_dirty     : $(test -n "$(git status --porcelain 2>/dev/null)" \
                            && echo yes || echo no)"
    echo "sha256        : $(cut -d' ' -f1 < "${OUT}.sha256")"
    echo "size_bytes    : $(stat -c %s "${OUT}")"
    echo
    echo "--- git status at pack time ---"
    git status --short 2>/dev/null || true
    echo
    echo "--- packed top-level paths ---"
    printf '%s\n' "${PATHS[@]}"
} > "${OUT%.tar.gz}.manifest.txt"

echo "[pack] wrote ${OUT} ($(du -h "${OUT}" | cut -f1))"
echo "[pack] wrote ${OUT}.sha256"
echo "[pack] wrote ${OUT%.tar.gz}.manifest.txt"
cat <<EOF

Next, from this login node (needs your Lightning SSH key in ~/.ssh):

    scp ${OUT} ${OUT}.sha256 <studio-user>@ssh.lightning.ai:~/

then, inside the Studio:

    sha256sum -c ~/$(basename "${OUT}").sha256
    mkdir -p ~/cmb-lcdm-sr && tar -xzf ~/$(basename "${OUT}") -C ~/cmb-lcdm-sr
    cd ~/cmb-lcdm-sr
    bash hpc/lightning/bootstrap_env.sh
EOF
