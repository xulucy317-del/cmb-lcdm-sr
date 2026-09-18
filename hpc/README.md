# hpc/ — launchers

The searches were run as SLURM jobs on the Cambridge CSD3 cluster (icelake
partition, 16 CPU per task), and — once the CSD3 allocation ran out — on a
Lightning AI CPU Studio and a Mac with the scheduler-free kits below. The
launchers are kept exactly as they ran: they are the definition of each
task matrix (the three campaign launchers print theirs with
`PRINT_MATRIX=1 bash hpc/<launcher>.sh`), several are hash-pinned by the
execution-provenance records in `experiments/`, and the tests assert their
argument vectors.

## Running them somewhere other than CSD3

The launchers stay as they ran, but nothing about them is tied to CSD3 once
three things are supplied from outside: the project root (`PROJ`), your
site's scheduler options, and — for the encoder pass and stage 4 — the
location of the spectra shards. Two wrappers supply them; both read
`hpc/site.env` (copy `hpc/site.env.example`, git-ignored) and are covered by
`tests/test_hpc_portability.py`.

```bash
cp hpc/site.env.example hpc/site.env      # fill in account / partition / paths
python scripts/check_inputs.py            # what this checkout can run (see below)
```

**Another SLURM cluster — `hpc/submit.sh`.** `sbatch` command-line options
take precedence over `#SBATCH` lines, so the wrapper passes your account,
partition, notification address and any extras from `site.env` on the
command line and exports `PROJ`, `SHARDS_ROOT` and `ACCOUNT` to the job:

```bash
hpc/submit.sh hpc/slurm_blind_sr.sh models/lcdm_tt_beta3e-4 2 "A_s tau" 0
hpc/submit.sh --array=0-35%16 hpc/slurm_hpsweep_sr.sh results/lcdm_tt_beta3e-4/hpsweep_hp_v1
DRY_RUN=1 hpc/submit.sh hpc/slurm_subspace_probe.sh     # print the sbatch line
```

Everything before the first `*.sh` argument goes to `sbatch`, everything
after it to the launcher. Most launchers ask for 16 CPUs, 16 GB and 1–24 h
(the consolidators up to 36 CPUs / 48 GB); if your partition's limits differ,
put `--time=…`/`--mem=…`/`--cpus-per-task=…` in `SLURM_EXTRA` or on the
command line.

**PBS, LSF, SGE, or no scheduler at all — `hpc/run_tasks.sh`.** Every
launcher except `slurm_mse_one_stage_pack.sh` is plain bash once SLURM's
variables are supplied (the `#SBATCH` lines are comments; array launchers
read their task from `SLURM_ARRAY_TASK_ID`). The wrapper supplies them and
runs a launcher's task matrix one task at a time or `--parallel N` at a
time, one log per task under `logs/`; launchers skip tasks whose
`report.json` already exists, so the same command resumes an interrupted run.

```bash
hpc/run_tasks.sh hpc/slurm_blind_sr.sh models/lcdm_tt_beta3e-4 2 "A_s tau" 0
hpc/run_tasks.sh --tasks 0-35 --parallel 2 hpc/slurm_hpsweep_sr.sh results/lcdm_tt_beta3e-4/hpsweep_hp_v1
hpc/run_tasks.sh --tasks 0-164 hpc/slurm_mse_one_stage_sr.sh
```

Inside another scheduler's job array, map its index onto the same variable
and run the launcher directly (`PROJ` set to the repository root):

```bash
SLURM_ARRAY_TASK_ID=$PBS_ARRAY_INDEX bash hpc/slurm_residual_sr.sh models/lcdm_tt_ee_lowl "0 1 2 3 4 5"   # PBS
SLURM_ARRAY_TASK_ID=$LSB_JOBINDEX    bash hpc/slurm_residual_sr.sh …                                    # LSF
SLURM_ARRAY_TASK_ID=$SGE_TASK_ID     bash hpc/slurm_residual_sr.sh …                                    # SGE
```

The task matrices of the stage-2 campaigns can also be run in persistent
PySR/Julia workers, which amortises Julia start-up on a small machine:
`scripts/run_mse_one_stage_pool.py` and `scripts/run_precision_preprocess_pool.py`
(with `hpc/lightning/` as the worked example of a full off-cluster resume).
And every unit of work is one `scripts/run_blind_sr.py` call, which needs no
launcher at all.

**Environment on a cluster.** The launchers activate `${PROJ}/.venv`, so
create it there (`python3.12 -m venv .venv && pip install -r requirements.txt`).
PySR fetches Julia and its packages on first import; do that once on a node
with internet access (`python -c "import pysr"`), then compute nodes can run
offline (`PYTHON_JULIAPKG_OFFLINE=yes`, as `hpc/lightning/env.sh` does). The
search launchers set `JULIA_NUM_THREADS=16` to match their 16-CPU request;
PySR is CPU-only, so no GPU partition is needed. `torch` is imported only by the
encoder pass, the decoder-effect stage and the stage-4 scripts.

**Inputs.** A clone has the code, checkpoints, parameter table and every
consolidated result. Whether it can *run* depends on three groups of files
that are not in git — the encoder caches, the spectra shards and the raw
fronts; `python scripts/check_inputs.py` reports which are present, verifies
their hashes and says what each missing group blocks. The top-level README
("Data and models") says where each comes from.

## SLURM launchers (`hpc/slurm_*.sh`)

| launcher | stage / phase | runs |
|---|---|---|
| `slurm_blind_sr.sh` | reference study | one two-input (A_s, τ) search on an amplitude latent, one seed |
| `slurm_shuffled_control.sh` | reference study | its shuffled-target control, 3 seeds |
| `slurm_allparams_encode.sh` | stage 1 | the encoder pass alone, submitted once per model ahead of the arrays |
| `slurm_allparams_sr.sh`, `slurm_allparams_control.sh` | stage 1 | six-input search on every latent (array), and its shuffled control |
| `slurm_hpsweep_sr.sh` | stage 1 | one array task per (config × latent × seed) of a sweep planned by `scripts/sweep_blind_sr.py`; also runs the 63-subset screen |
| `slurm_residual_sr.sh`, `slurm_residual_consolidate.sh` | phase 6 | blind SR on the stage-1 residuals, then the Phase-6 consolidation |
| `slurm_residual_sr_ia.sh`, `slurm_residual_sr_ia_control.sh` | phase 6 (ia) | the interaction-aware rerun and its control |
| `slurm_decoder_effect.sh` | phase 7b | one streaming shard pass for the spectral templates, then the decoder-effect triangulation |
| `slurm_subspace_probe.sh` | phase 8 | the subspace probe for both models |
| `slurm_sham_control.sh`, `slurm_subsets_full_consolidate.sh` | R-P4 | the sham-input dilution control and the exhaustive-support consolidation |
| `slurm_mse_one_stage_sr.sh`, `slurm_mse_one_stage_control.sh` | stage 2 | the 165-task MSE ladder and its 12 controls (embedded arrays) |
| `slurm_mse_one_stage_pack.sh` | stage 2 | the same matrix packed into a single job for a one-job-per-user QoS |
| `slurm_mse_one_stage_consolidate.sh` | stage 2 | guarded `select` → `calibrate` → `confirm` |
| `slurm_precision_preprocess_v1.sh`, `slurm_precision_preprocess_consolidate.sh` | stage 2 | the 330-task precision / preprocessing campaign and its six-cell consolidation |

`hpc/submit.sh`, `hpc/run_tasks.sh` and `hpc/site.env.example` are the
portability layer described above.

`hpc/sweeps/*.json` are the sweep specifications those arrays expand:
`allparams_hp_v1_{tt,ee}` (the hyperparameter star), `subsets_v1_{tt,ee}`
(the Phase-4 screen) and `subsets_full_{tt,ee}` (the exhaustive R-P4 grid).

## Scheduler-free kits

`hpc/lightning/` — built to finish the stage-2 campaigns on a Lightning AI
free-plan CPU Studio after the CSD3 allocation was exhausted; the process
model changes (persistent workers, resumable at task granularity), the task
identities do not.

| file | does |
|---|---|
| `bootstrap_env.sh`, `env.sh`, `requirements-lightning.txt`, `julia_env_reference/` | build and source the frozen environment (exact pins that produced the first CSD3 reports; Julia manifest seeded from the CSD3 one) |
| `make_transfer_bundle.sh` | packs everything the resume needs on CSD3 into a hashed tarball |
| `resume_all.sh`, `run_consolidation.sh` | the MSE study: run the remaining matrix, then the three consolidation stages |
| `resume_precision_preprocess.sh`, `run_precision_preprocess_consolidation.sh` | the same for the precision campaign |
| `run_coordinate_matched_ols_audit.sh` | the coordinate-matched OLS audit |
| `run_residual_sr_ols.sh` | stage 3: blind SR on the OLS residual of EE z₀ and z₄ |

`hpc/mac/resume_precision_preprocess_batched.sh` ran three of the five
precision-campaign seeds on an Apple-silicon Mac with a local Julia, in
batches of ten tasks. The operational log of the Lightning hand-over is
`experiments/mse_one_stage_lightning_runbook.md`.
