#!/bin/bash
#! Precision/preprocessing comparison: three frozen input configurations,
#! both SR objectives, both checkpoints, every latent, and five search seeds.
#! One array task is exactly one run_blind_sr.py invocation.
#!
#! Matrix:
#!   raw64, physical_o1_64, logamp64
#!   x {gmm_mi at maxsize 20, mse at maxsize 40}
#!   x {TT z0..z4, TT+EE z0..z5}
#!   x seeds 0..4
#!   = 330 independent/resumable searches.
#!
#! Dry-run and smoke before submitting the production array:
#!   PRINT_MATRIX=1 bash hpc/slurm_precision_preprocess_v1.sh
#!   sbatch --array=0,55,110,165,220,275%1 --export=ALL,SMOKE=1 \
#!       hpc/slurm_precision_preprocess_v1.sh
#!   sbatch hpc/slurm_precision_preprocess_v1.sh
#!
#! Production outputs:
#!   results/<run>/precision_preprocess_v1/<arm>/<loss>_ms<budget>/
#!       z<latent>_seed<seed>/report.json
#!
#! A present report is skipped only after its complete task identity and
#! selected-result fields validate. A stale, corrupt, or mismatched report is
#! never overwritten automatically: the task exits non-zero for inspection.
#SBATCH --job-name=precprep_sr
#SBATCH --output=logs/precprep_sr_%A_%a.out
#SBATCH --error=logs/precprep_sr_%A_%a.err
#SBATCH --array=0-329%16
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=16G
#SBATCH --partition=icelake
#SBATCH --account=MPHIL-DIS-SL2-CPU
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zx332@cam.ac.uk

set -euo pipefail

PROJ="${PROJ:-/rds/user/zx332/hpc-work/cmb-lcdm-sr}"
DEFAULT_ACCOUNT="MPHIL-DIS-SL2-CPU"
ACCOUNT="${ACCOUNT:-${DEFAULT_ACCOUNT}}"
[[ "${ACCOUNT}" =~ ^[A-Za-z0-9_.-]+$ ]] || {
    echo "[err] unsafe ACCOUNT value '${ACCOUNT}'" >&2
    exit 2
}
# Case-insensitive account comparison via tr (works on bash 3.2 as well as 4+).
if [[ -n "${SLURM_JOB_ACCOUNT:-}" && \
      "$(printf '%s' "${SLURM_JOB_ACCOUNT}" | tr '[:upper:]' '[:lower:]')" != \
      "$(printf '%s' "${ACCOUNT}" | tr '[:upper:]' '[:lower:]')" ]]; then
    echo "[err] ACCOUNT=${ACCOUNT} does not match SLURM_JOB_ACCOUNT=${SLURM_JOB_ACCOUNT}" >&2
    exit 2
fi
TOTAL_TASKS=330
ARMS=(raw64 physical_o1_64 logamp64)
SEEDS=(0 1 2 3 4)
TASKS_PER_OBJECTIVE=55
TASKS_PER_ARM=110

task_fields() {
    local idx="$1" arm_idx within_arm objective_idx cell
    local run_dir local_cell latent seed inner_loss selection_metric
    local posthoc_mi maxsize family

    (( idx >= 0 && idx < TOTAL_TASKS )) || return 1
    arm_idx=$(( idx / TASKS_PER_ARM ))
    within_arm=$(( idx % TASKS_PER_ARM ))
    objective_idx=$(( within_arm / TASKS_PER_OBJECTIVE ))
    cell=$(( within_arm % TASKS_PER_OBJECTIVE ))

    if (( cell < 25 )); then
        run_dir="models/lcdm_tt_beta3e-4"
        local_cell="${cell}"
    else
        run_dir="models/lcdm_tt_ee_lowl"
        local_cell=$(( cell - 25 ))
    fi
    latent=$(( local_cell / ${#SEEDS[@]} ))
    seed="${SEEDS[$(( local_cell % ${#SEEDS[@]} ))]}"

    if (( objective_idx == 0 )); then
        inner_loss="gmm_mi"
        selection_metric="mi"
        posthoc_mi="full"
        maxsize=20
        family="gmm_mi_ms20"
    else
        inner_loss="mse"
        selection_metric="mse"
        posthoc_mi="none"
        maxsize=40
        family="mse_ms40"
    fi

    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "${run_dir}" "${ARMS[${arm_idx}]}" "${inner_loss}" \
        "${selection_metric}" "${posthoc_mi}" "${latent}" "${seed}" \
        "${maxsize}" "${family}"
}

if [[ "${PRINT_MATRIX:-0}" == "1" ]]; then
    printf 'task_id\trun_dir\tarm\tinner_loss\tselection_metric\tposthoc_mi\tlatent\tseed\tmaxsize\tfamily\tout_dir\n'
    for (( task_id=0; task_id<TOTAL_TASKS; task_id++ )); do
        fields="$(task_fields "${task_id}")"
        IFS=$'\t' read -r run_dir arm inner_loss selection_metric \
            posthoc_mi latent seed maxsize family <<< "${fields}"
        run_name="$(basename "${run_dir}")"
        out_dir="results/${run_name}/precision_preprocess_v1/${arm}/${family}/z${latent}_seed${seed}"
        printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
            "${task_id}" "${run_dir}" "${arm}" "${inner_loss}" \
            "${selection_metric}" "${posthoc_mi}" "${latent}" "${seed}" \
            "${maxsize}" "${family}" "${out_dir}"
    done
    exit 0
fi

IDX="${SLURM_ARRAY_TASK_ID:?submit as a Slurm array or use PRINT_MATRIX=1}"
FIELDS="$(task_fields "${IDX}")" || {
    echo "[err] invalid task id ${IDX}; expected 0-$((TOTAL_TASKS - 1))"
    exit 1
}
IFS=$'\t' read -r RUN_DIR ARM INNER_LOSS SELECTION_METRIC POSTHOC_MI \
    LATENT SEED MAXSIZE FAMILY <<< "${FIELDS}"

PYTHON="${PROJ}/.venv/bin/python"
[[ -x "${PYTHON}" ]] || { echo "[err] missing interpreter ${PYTHON}"; exit 1; }
export PATH="${PROJ}/.venv/bin:${PATH}"
export PYTHON_JULIAPKG_PROJECT="${PROJ}/.venv/julia_env"
export PYTHON_JULIAPKG_OFFLINE="${PYTHON_JULIAPKG_OFFLINE:-yes}"
export PYTHONUNBUFFERED=1
export JULIA_NUM_THREADS="${SLURM_CPUS_PER_TASK:-16}"

cd "${PROJ}"
mkdir -p logs
RUN_NAME="$(basename "${RUN_DIR}")"
if [[ "${SMOKE:-0}" == "1" ]]; then
    N_SAMPLES="${N_SAMPLES:-500}"
    NITERATIONS="${NITERATIONS:-1}"
    POPULATIONS="${POPULATIONS:-2}"
    SMOKE_ID="${SMOKE_TAG:-${SLURM_ARRAY_JOB_ID:-manual}}"
    [[ "${SMOKE_ID}" =~ ^[A-Za-z0-9_.-]+$ ]] || {
        echo "[err] unsafe smoke tag '${SMOKE_ID}'"
        exit 1
    }
    STUDY_DIR="precision_preprocess_v1_smoke_${SMOKE_ID}"
    START_DELAY=0
else
    N_SAMPLES="${N_SAMPLES:-5000}"
    NITERATIONS="${NITERATIONS:-200}"
    POPULATIONS="${POPULATIONS:-15}"
    STUDY_DIR="precision_preprocess_v1"
    if [[ "${PACKED:-0}" == "1" ]]; then
        START_DELAY=0
    else
        START_DELAY=$(( (IDX % 16) * 7 ))
    fi
fi
OUT_DIR="results/${RUN_NAME}/${STUDY_DIR}/${ARM}/${FAMILY}/z${LATENT}_seed${SEED}"
REPORT="${OUT_DIR}/report.json"

validate_report() {
    "${PYTHON}" - "$@" <<'PY'
import json
import math
import pathlib
import sys

(path_s, run_name, arm, latent_s, seed_s, inner_loss, selection_metric,
 posthoc_mi, maxsize_s, n_samples_s, niterations_s, populations_s) = sys.argv[1:]
path = pathlib.Path(path_s)


def fail(message):
    print(message)
    raise SystemExit(1)


try:
    report = json.loads(path.read_text())
except Exception as exc:
    fail(f"invalid JSON: {exc}")
if not isinstance(report, dict):
    fail("report root is not an object")

latent = int(latent_s)
seed = int(seed_s)
maxsize = int(maxsize_s)
n_samples = int(n_samples_s)
niterations = int(niterations_s)
populations = int(populations_s)

expected = {
    "regime": run_name,
    "input_config": arm,
    "latent_index": latent,
    "seed": seed,
    "n_samples": n_samples,
    "n_fit": n_samples - int(n_samples * 0.2),
    "n_val": int(n_samples * 0.2),
    "inner_loss": inner_loss,
    "selection_metric": selection_metric,
    "posthoc_mi_mode": posthoc_mi,
    "selection_direction": "descending" if selection_metric == "mi" else "ascending",
}
for key, value in expected.items():
    if report.get(key) != value:
        fail(f"{key}: expected {value!r}, found {report.get(key)!r}")

if pathlib.Path(str(report.get("run_dir", ""))).name != run_name:
    fail(f"run_dir does not name {run_name!r}")
if report.get("target_npy") is not None:
    fail("target_npy must be null for a latent-target search")
if report.get("extra_inputs") not in ([], None):
    fail("extra_inputs must be empty")

ols = report.get("ols_baseline")
if not isinstance(ols, dict):
    fail("ols_baseline must be an object")
if ols.get("status") != "skipped":
    fail("ols_baseline.status must be 'skipped'")
if ols.get("reason") != "fixed_old_ols_reused_downstream":
    fail("ols_baseline.reason does not match the frozen campaign contract")

names = report.get("input_names")
labels = report.get("input_labels")
expressions = report.get("input_sampled_expressions")
if not isinstance(names, list) or len(names) != 6 or not all(
        isinstance(x, str) and x for x in names):
    fail("input_names must contain six non-empty strings")
if not isinstance(labels, list) or len(labels) != 6 or not all(
        isinstance(x, str) and x for x in labels):
    fail("input_labels must contain six non-empty strings")
if len(set(labels)) != 6:
    fail("input_labels are not unique")
if not isinstance(expressions, dict) or set(expressions) != set(labels):
    fail("input_sampled_expressions must map every input label exactly once")
if not all(isinstance(value, str) and value for value in expressions.values()):
    fail("input_sampled_expressions contains an empty/non-string expression")

kwargs = report.get("pysr_kwargs")
if not isinstance(kwargs, dict):
    fail("pysr_kwargs is missing or not an object")
kw_expected = {
    "niterations": niterations,
    "populations": populations,
    "maxsize": maxsize,
    "parallelism": "multithreading",
    "random_state": seed,
    "precision": 64,
    "print_precision": 17,
}
for key, value in kw_expected.items():
    if kwargs.get(key) != value:
        fail(f"pysr_kwargs.{key}: expected {value!r}, found {kwargs.get(key)!r}")
if kwargs.get("binary_operators") != ["+", "*", "-", "/"]:
    fail("unexpected binary operator grammar")
if kwargs.get("unary_operators") != ["exp", "log", "neg", "square"]:
    fail("unexpected unary operator grammar")
if not isinstance(kwargs.get("run_id"), str) or not kwargs["run_id"]:
    fail("pysr_kwargs.run_id is empty")

if report.get("posthoc_mi_status") != (
        "computed" if posthoc_mi == "full" else "skipped_not_selected"):
    fail("posthoc_mi_status is inconsistent with the task")
if not isinstance(report.get("best_expression"), str) or not report["best_expression"].strip():
    fail("best_expression is empty")
equations = report.get("all_equations")
if not isinstance(equations, list) or not equations:
    fail("all_equations is empty")
if report.get("n_equations") != len(equations):
    fail("n_equations does not match all_equations")
metric_key = "best_mi_val" if selection_metric == "mi" else "best_mse_val"
metric = report.get(metric_key)
if not isinstance(metric, (int, float)) or not math.isfinite(float(metric)):
    fail(f"{metric_key} is missing or non-finite")

print("ok")
PY
}

if [[ -f "${REPORT}" ]]; then
    if VALIDATION_OUTPUT="$(validate_report "${REPORT}" "${RUN_NAME}" "${ARM}" \
            "${LATENT}" "${SEED}" "${INNER_LOSS}" "${SELECTION_METRIC}" \
            "${POSTHOC_MI}" "${MAXSIZE}" "${N_SAMPLES}" "${NITERATIONS}" \
            "${POPULATIONS}" 2>&1)"; then
        echo "[skip] validated ${REPORT}"
        exit 0
    fi
    echo "[err] existing report failed task validation: ${REPORT}"
    echo "[err] ${VALIDATION_OUTPUT}"
    exit 2
fi

# Shared Julia-environment cold starts can race; spread production starts.
sleep "${START_DELAY}"

RUN_TOKEN="${SLURM_ARRAY_JOB_ID:-manual}_${IDX}_${SLURM_RESTART_COUNT:-0}"
echo "[run] task=${IDX}/$((TOTAL_TASKS - 1)) run=${RUN_NAME} latent=${LATENT} seed=${SEED}"
echo "[run] arm=${ARM} loss=${INNER_LOSS} selector=${SELECTION_METRIC} maxsize=${MAXSIZE}"
echo "[run] account=${ACCOUNT} cpu=${SLURM_CPUS_PER_TASK:-16} precision=profile"
echo "[run] smoke=${SMOKE:-0} samples=${N_SAMPLES} iterations=${NITERATIONS} populations=${POPULATIONS}"
"${PYTHON}" scripts/run_blind_sr.py \
    --run-dir "${RUN_DIR}" \
    --dataset-dir data \
    --latent-index "${LATENT}" \
    --input-config "${ARM}" \
    --n-samples "${N_SAMPLES}" \
    --niterations "${NITERATIONS}" \
    --populations "${POPULATIONS}" \
    --maxsize "${MAXSIZE}" \
    --inner-loss "${INNER_LOSS}" \
    --selection-metric "${SELECTION_METRIC}" \
    --posthoc-mi "${POSTHOC_MI}" \
    --skip-ols-baseline \
    --turbo \
    --parallelism multithreading \
    --pysr-run-id "run_${RUN_TOKEN}" \
    --seed "${SEED}" \
    --out-dir "${OUT_DIR}"
