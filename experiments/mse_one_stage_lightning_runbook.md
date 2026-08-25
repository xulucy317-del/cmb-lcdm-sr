# Lightning AI resume runbook — one-stage MSE experiment

**Written:** 2026-08-25 on CSD3 (`login-q-1`), against git `cbd9385` + the
uncommitted MSE one-stage worktree.
**Authority:** `experiments/mse_one_stage_sr_plan.md` §11 is the scientific
contract. This file is only the operational path for executing §11.3 on a
single CPU machine instead of a Slurm cluster.

## 0. What is frozen, what is left

| item | state |
|---|---|
| main searches (`mse20/30/40`, 11 latents × 5 seeds) | **36 / 165 complete**, 129 remain |
| MSE shuffled controls | **0 / 12** |
| selection manifest / T1 calibration / T2 confirmation | not created; T2 never opened |
| legacy GMM-MI fronts (`mi20-mi`, `mi20-mse`) | reused read-only — **never rerun** |

Non-negotiables carried over from the plan:

* an existing valid `report.json` is an immutable resume point — skip, never
  overwrite;
* the two Slurm launchers stay the definition of task identity, even though
  Slurm itself is not used here (`PRINT_MATRIX=1` is the source of truth);
* stage order is searches → controls → `select` (T0) → `calibrate` (T1) →
  `confirm` (T2, once).

## 1. Lightning AI account and Studio (browser)

1. Sign in at <https://lightning.ai> and create a **new Studio**.
2. Keep it on **CPU**. Nothing in this experiment uses a GPU, and on the free
   plan a GPU Studio spends credits for no benefit. Check the machine selector
   for the core count you actually get (the free CPU Studio is typically 4
   cores / 16 GB); note that number — it sets `--threads` below.
3. Confirm where persistent storage lives:

   ```bash
   echo "$HOME"; ls -ld /teamspace/studios/this_studio
   ```

   Put the project inside the Studio directory (usually `$HOME`, i.e.
   `/teamspace/studios/this_studio`). Only that tree survives a stop/start.
4. Enable SSH: Studio → **SSH** → *Connect via SSH*, add the public key from
   CSD3, and copy the exact `ssh s_…@ssh.lightning.ai` address it shows.

   On CSD3, if you do not already have a key:

   ```bash
   ls ~/.ssh/id_ed25519.pub || ssh-keygen -t ed25519 -C "csd3-to-lightning"
   cat ~/.ssh/id_ed25519.pub          # paste this into the Lightning UI
   ```

   Outbound SSH from the CSD3 login node to `ssh.lightning.ai:22` was verified
   reachable on 2026-08-25.
5. Free-plan session behaviour: a free CPU Studio can be stopped automatically
   (idle timeout, and the plan's own session limit). Everything below is
   resumable at task granularity — after a stop, start the Studio and re-run
   the same command.

## 2. Pack the bundle (on CSD3)

```bash
cd /rds/user/zx332/hpc-work/cmb-lcdm-sr
bash hpc/lightning/make_transfer_bundle.sh
```

This records the source-machine state in
`experiments/mse_one_stage_state_csd3.json`, then writes
`../cmb-lcdm-sr-mse-one-stage-<stamp>.tar.gz` plus a `.sha256` and a
`.manifest.txt` (git revision, dirty flag, packed paths).

It carries code, tests, `data/`, `models/` (including the cached encoder means
and the `residual_z*`/`f1hat_z*` vectors), all of `experiments/`, the legacy
`allparams` GMM-MI fronts, and every existing `mse_one_stage_ms*` /
`mse_one_stage_control_ms*` result directory. It deliberately omits `logs/`,
`.git`, the shared `.venv`, `paper/`, the old CSD3 smoke directories, and the
result families this experiment does not read.

## 3. Ship it

```bash
# from the CSD3 login node — use the address the Studio SSH panel showed
scp ../cmb-lcdm-sr-mse-one-stage-<stamp>.tar.gz \
    ../cmb-lcdm-sr-mse-one-stage-<stamp>.tar.gz.sha256 \
    s_XXXXXXXX@ssh.lightning.ai:~/
```

Alternatives if SSH is inconvenient: drag the tarball into the Studio's file
browser, or use the `lightning` CLI. Any path is fine — the checksum in step 4
is what matters.

## 4. Unpack and build the environment (in the Studio terminal)

```bash
cd ~ && sha256sum -c cmb-lcdm-sr-mse-one-stage-<stamp>.tar.gz.sha256
mkdir -p ~/cmb-lcdm-sr
tar -xzf cmb-lcdm-sr-mse-one-stage-<stamp>.tar.gz -C ~/cmb-lcdm-sr
cd ~/cmb-lcdm-sr
bash hpc/lightning/bootstrap_env.sh
```

`bootstrap_env.sh` creates `.venv-lightning`, installs the exact CSD3 pins
(`hpc/lightning/requirements-lightning.txt`: PySR 1.5.10, numpy 2.4.2,
scikit-learn 1.5.2, the pinned `gmm-mi` commit; **no torch** — the encoder pass
is already cached), seeds the Julia project from the CSD3 `Project.toml` +
`Manifest.toml` (Julia 1.11.9, SymbolicRegression.jl 1.11.3,
LoopVectorization.jl 0.12.174), starts Julia once so PySR precompiles, and
prints any Julia package drift. Budget 10–25 minutes for the first run; it is
idempotent afterwards.

One thing it deliberately front-loads: the frozen search runs with `--turbo`,
and PySR resolves `LoopVectorization.jl` lazily *inside the first fit* with
`Pkg.add` + `Pkg.resolve`. Bootstrap calls `load_required_packages(turbo=True)`
while it is explicitly online, so no search task can be blocked by, or silently
change its environment through, a mid-run package install.

Record what it prints — Python, PySR, Julia and any drift lines go into the
provenance entry in step 9.

## 5. Verify before spending any compute

```bash
source hpc/lightning/env.sh

python -m pytest -q tests/test_mse_loss_selection.py \
    tests/test_mse_one_stage_consolidation.py \
    tests/test_mse_one_stage_hpc.py tests/test_mse_one_stage_lightning.py

python scripts/verify_mse_one_stage_state.py --check-julia \
    --json experiments/mse_one_stage_state_lightning.json \
    --compare experiments/mse_one_stage_state_csd3.json

PRINT_MATRIX=1 bash hpc/slurm_mse_one_stage_sr.sh | tail -3
PRINT_MATRIX=1 bash hpc/slurm_mse_one_stage_control.sh | tail -3
python scripts/run_mse_one_stage_pool.py --family all --dry-run | tail -3
```

Expected: 57 tests pass (23 + 34); `--compare` reports that every carried
input, source file and existing report matches CSD3 byte for byte; the
matrices print 165 and 12 rows; the pool reports `main: 36/165 complete`,
`control: 0/12`, `141 task(s) would run`. **Do not start compute if `--compare`
reports a mismatch** — re-transfer instead.

## 6. Smoke, then benchmark (the plan's "benchmark one representative task")

```bash
# 1. end-to-end check in an isolated smoke namespace (500 rows, 1 iteration)
python scripts/run_mse_one_stage_pool.py --family main --smoke lightning1 \
    --task-ids 36 --limit 1 --no-worker-logs

# 2. one real task, fully timed
python scripts/run_mse_one_stage_pool.py --family main --limit 1 \
    --no-worker-logs
```

Then read the timings back:

```bash
tail -3 logs/mse_one_stage_pool_ledger.jsonl | python -m json.tool
```

CSD3 reference for the 36 completed reports (16 icelake threads):
`fit_seconds` 36–60 s — median 39 s at `ms20`, 44 s at `ms30`, 51 s at `ms40`.

Measured amortization, on the CSD3 login node at 2 threads with the smoke
configuration (so the numbers below are almost pure overhead, not search):

| | wall | fit |
|---|---:|---:|
| worker startup (`import pysr` + `using SymbolicRegression`) | 7.7 s | — |
| first task in the process (Julia JIT of the search kernels) | 68 s | 60.6 s |
| second task | 2 s | 0.9 s |
| third task | 1 s | 0.6 s |

That is the whole point of the pool: one-process-per-task pays ~60–215 s of
startup **for every one of the 141 remaining tasks**; a persistent worker pays
it once and then ~1–2 s per task.

Choose the process layout from measurement, not theory — on a 4-core box
compare, over ~4 tasks each:

```bash
python scripts/run_mse_one_stage_pool.py --family main --limit 4 --workers 1 --threads 4
python scripts/run_mse_one_stage_pool.py --family main --limit 4 --workers 2 --threads 2
```

and keep whichever gives more completed tasks per minute — ignoring the first
task of each invocation, which carries the one-off JIT. Rough expectation
before measuring: 2–4× the CSD3 fit time at 4 threads, so ≈2.5–3.5 min/task and
≈6–9 h for all 141 remaining searches. Replace this with your measured rate.

## 7. Run the remaining searches

Use a terminal multiplexer so a browser disconnect cannot kill the run:

```bash
tmux new -s mse          # or: nohup ... > logs/resume.log 2>&1 &
cd ~/cmb-lcdm-sr && source hpc/lightning/env.sh
WORKERS=1 THREADS=4 bash hpc/lightning/resume_all.sh
```

`resume_all.sh` runs searches → controls → `select` → `calibrate` → `confirm`,
and refuses to start consolidation while any search task is missing.

If the free plan cuts sessions at a fixed length, bound each pass so it stops
cleanly instead of being killed mid-fit:

```bash
TIME_BUDGET_MINUTES=210 WORKERS=1 THREADS=4 bash hpc/lightning/resume_all.sh
```

After any stop — planned, idle-timeout, or crash — **re-run the identical
command**. Completed tasks are skipped after validation; a task interrupted
mid-fit simply has no `report.json` and is redone from scratch.

Finer control, if you prefer to drive it yourself:

```bash
python scripts/run_mse_one_stage_pool.py --family main --task-ids 36-100 --workers 1
python scripts/run_mse_one_stage_pool.py --family control
```

Progress and provenance land in `logs/mse_one_stage_pool_ledger.jsonl` (one
JSON line per task: task id, out dir, status, wall seconds, `fit_seconds`,
worker, thread count, host).

## 8. Consolidation

`resume_all.sh` does this automatically once all 177 reports exist. Manually:

```bash
for run in lcdm_tt_beta3e-4 lcdm_tt_ee_lowl; do
    bash hpc/lightning/run_consolidation.sh select "$run"      # T0 only
done
for run in lcdm_tt_beta3e-4 lcdm_tt_ee_lowl; do
    bash hpc/lightning/run_consolidation.sh calibrate "$run"   # T1 only
done
for run in lcdm_tt_beta3e-4 lcdm_tt_ee_lowl; do
    MI_JOBS=4 bash hpc/lightning/run_consolidation.sh confirm "$run"   # opens T2
done
```

`confirm` is the expensive consolidation stage: the required known-`f2`
absorption audit is 11 latents × 5 seeds = 55 residual audits, each with one
observed GMM-MI plus a 39-permutation null on up to 5000 rows (2200 GMM-MI
evaluations). `MI_JOBS` parallelises the permutations; set it to your core
count. Under amendment A2 no other MI is computed.

Outputs: `experiments/mse_one_stage_sr_<run>.{json,md}` per checkpoint.

## 9. Bring the results back to CSD3 and record provenance

```bash
# from the CSD3 login node; --ignore-existing protects the 36 frozen reports
rsync -avz --ignore-existing \
    s_XXXXXXXX@ssh.lightning.ai:'~/cmb-lcdm-sr/results/' results/
rsync -avz s_XXXXXXXX@ssh.lightning.ai:'~/cmb-lcdm-sr/experiments/' experiments/
rsync -avz s_XXXXXXXX@ssh.lightning.ai:'~/cmb-lcdm-sr/logs/mse_one_stage_pool_ledger.jsonl' logs/
python scripts/verify_mse_one_stage_state.py \
    --compare experiments/mse_one_stage_state_csd3.json
```

If the Studio has no `rsync`, tar the same three paths there and `scp` the
archive back instead — but keep `--ignore-existing` semantics by unpacking into
a staging directory and copying only new task directories across.

Then append a `lightning_execution` block to
`experiments/mse_one_stage_execution_provenance.json` recording, at minimum:
platform and machine type, core count, `JULIA_NUM_THREADS` per worker, workers
per session, Python/PySR/Julia versions, any Julia manifest drift from
`bootstrap_env.sh`, the state-artifact hashes from both machines, and the two
deviations in §10.

## 10. Deviations from the CSD3 execution, to be recorded not hidden

1. **Thread count.** The first 36 reports were searched with
   `JULIA_NUM_THREADS=16`; the remainder will use however many cores the free
   Studio provides. PySR's multithreaded search is already non-deterministic at
   fixed seed, and the amount of search (200 iterations × 15 populations) is
   unchanged — but the thread count is not recorded inside `report.json`, so it
   must be recorded in the provenance entry and in the ledger (the pool writes
   `threads_per_worker` into every session record).
2. **Process model.** CSD3 ran one Python process per task; the pool runs many
   fits inside one persistent Julia/PySR process. Each task still constructs a
   fresh `PySRRegressor` with its own `output_directory`/`run_id`, and the
   report contract is unchanged (the parity test in
   `tests/test_mse_one_stage_lightning.py` proves the command is identical).

Neither touches the objective, the selection rule, the tier contract, or any
decision threshold.

## 11. Files added for this handoff

| path | role |
|---|---|
| `scripts/run_mse_one_stage_pool.py` | persistent-worker executor + resume contract + ledger |
| `scripts/verify_mse_one_stage_state.py` | environment/input/report state artifact and `--compare` gate |
| `hpc/lightning/env.sh` | shared environment (venv, Julia project, threads) |
| `hpc/lightning/bootstrap_env.sh` | build `.venv-lightning`, pin Julia, report drift |
| `hpc/lightning/requirements-lightning.txt` | exact CSD3 Python pins, minus torch |
| `hpc/lightning/julia_env_reference/` | CSD3 `Project.toml` + `Manifest.toml` (Julia 1.11.9) |
| `hpc/lightning/make_transfer_bundle.sh` | CSD3-side packer with checksums and manifest |
| `hpc/lightning/run_consolidation.sh` | scheduler-free `select`/`calibrate`/`confirm` |
| `hpc/lightning/resume_all.sh` | one resumable command for the whole remainder |
| `tests/test_mse_one_stage_lightning.py` | launcher/pool command parity + portability checks |

The CSD3 Slurm launchers are untouched and remain valid if the allowance is
renewed.
