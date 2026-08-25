#!/usr/bin/env bash
#! Build the resume environment on a fresh CPU machine (Lightning AI Studio).
#!
#!   bash hpc/lightning/bootstrap_env.sh
#!
#! Creates .venv-lightning, installs the frozen Python pins, seeds the Julia
#! project from the CSD3 Manifest, starts Julia once so PySR precompiles, and
#! reports every version plus any drift from the CSD3 environment. Safe to
#! re-run: an existing venv is reused.
set -euo pipefail

PROJ="${PROJ:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "${PROJ}"
LIGHTNING_VENV="${LIGHTNING_VENV:-${PROJ}/.venv-lightning}"
REFERENCE="${PROJ}/hpc/lightning/julia_env_reference"
REQUIREMENTS="${PROJ}/hpc/lightning/requirements-lightning.txt"

echo "[bootstrap] project    = ${PROJ}"
echo "[bootstrap] virtualenv = ${LIGHTNING_VENV}"

# --- interpreter ----------------------------------------------------------
if [[ ! -x "${LIGHTNING_VENV}/bin/python" ]]; then
    if [[ -n "${PYTHON_BIN:-}" ]]; then
        echo "[bootstrap] creating venv with ${PYTHON_BIN}"
        "${PYTHON_BIN}" -m venv "${LIGHTNING_VENV}"
    elif command -v uv >/dev/null 2>&1; then
        echo "[bootstrap] creating venv with uv (python 3.12)"
        # --seed puts pip inside the venv; a bare `uv venv` does not, and the
        # install step below calls `python -m pip`.
        uv venv --python 3.12 --seed "${LIGHTNING_VENV}"
    elif command -v python3.12 >/dev/null 2>&1; then
        echo "[bootstrap] creating venv with python3.12"
        python3.12 -m venv "${LIGHTNING_VENV}"
    else
        echo "[bootstrap] WARNING: python3.12 not found; falling back to" \
             "$(python3 -V). CSD3 ran 3.12.12 — record this deviation."
        python3 -m venv "${LIGHTNING_VENV}"
    fi
else
    echo "[bootstrap] reusing existing venv"
fi
PY="${LIGHTNING_VENV}/bin/python"
"${PY}" -V

# --- python packages ------------------------------------------------------
echo "[bootstrap] installing frozen pins"
"${PY}" -m pip install --quiet --upgrade pip setuptools wheel
"${PY}" -m pip install -r "${REQUIREMENTS}"

# --- julia project --------------------------------------------------------
export PYTHON_JULIAPKG_PROJECT="${LIGHTNING_VENV}/julia_env"
mkdir -p "${PYTHON_JULIAPKG_PROJECT}"
for toml in Project.toml Manifest.toml; do
    if [[ ! -f "${PYTHON_JULIAPKG_PROJECT}/${toml}" ]]; then
        cp "${REFERENCE}/${toml}" "${PYTHON_JULIAPKG_PROJECT}/${toml}"
        echo "[bootstrap] seeded ${toml} from the CSD3 reference"
    fi
done

# First start must be online: juliapkg downloads Julia 1.11.9 and instantiates
# the project. Later runs use hpc/lightning/env.sh, which defaults to offline.
export PYTHON_JULIAPKG_OFFLINE=no
export PYTHONUNBUFFERED=1
echo "[bootstrap] starting Julia once (first run downloads Julia + packages)"
"${PY}" - <<'PYCODE'
import time
t0 = time.time()
import pysr
from pysr.julia_extensions import load_required_packages
from juliacall import Main as jl

print(f"[bootstrap] pysr {pysr.__version__}")
print(f"[bootstrap] julia {jl.seval('string(VERSION)')} "
      f"threads={jl.seval('Threads.nthreads()')}")
# The frozen search uses --turbo, and PySR resolves LoopVectorization.jl
# lazily inside the first fit (Pkg.add + Pkg.resolve, i.e. network). Do it
# here, once, while this bootstrap is explicitly online.
load_required_packages(turbo=True)
print("[bootstrap] LoopVectorization loaded (required by --turbo)")
print(f"[bootstrap] first Julia start took {time.time() - t0:.1f}s")
PYCODE

# --- drift report ---------------------------------------------------------
echo "[bootstrap] comparing the resolved Julia manifest with CSD3"
"${PY}" - "${REFERENCE}/Manifest.toml" \
        "${PYTHON_JULIAPKG_PROJECT}/Manifest.toml" <<'PYCODE'
import re
import sys
from pathlib import Path


def versions(path):
    out, name = {}, None
    for line in Path(path).read_text().splitlines():
        block = re.match(r"\[\[deps\.([^\]]+)\]\]", line)
        if block:
            name = block.group(1)
        version = re.match(r'version = "([^"]+)"', line)
        if version and name:
            out[name] = version.group(1)
    return out


was, now = versions(sys.argv[1]), versions(sys.argv[2])
drift = {k: (was.get(k), now.get(k)) for k in sorted(set(was) | set(now))
         if was.get(k) != now.get(k)}
key = "SymbolicRegression"
print(f"[bootstrap] SymbolicRegression.jl: CSD3 {was.get(key)} -> "
      f"here {now.get(key)}")
if not drift:
    print("[bootstrap] julia package versions identical to CSD3")
else:
    print(f"[bootstrap] {len(drift)} julia package version difference(s):")
    for name, (a, b) in drift.items():
        print(f"[bootstrap]   {name}: {a} -> {b}")
    print("[bootstrap] record these in the execution provenance before "
          "resuming compute.")
PYCODE

echo
echo "[bootstrap] done. Next:"
echo "  source hpc/lightning/env.sh"
echo "  python scripts/verify_mse_one_stage_state.py \\"
echo "      --json experiments/mse_one_stage_state_lightning.json \\"
echo "      --compare experiments/mse_one_stage_state_csd3.json --check-julia"
