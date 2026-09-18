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

The `#SBATCH` headers carry CSD3's account, partition and the author's
notification address, and every launcher defaults its project root to the
CSD3 path. None of that needs editing — `sbatch` command-line options
override `#SBATCH` directives, and `PROJ` is read from the environment:

```bash
sbatch --account=<your-account> --partition=<your-partition> \
       --mail-type=NONE \
       --export=ALL,PROJ=$PWD \
       hpc/slurm_blind_sr.sh models/lcdm_tt_beta3e-4 2 "A_s tau" 0
```

Submit from the repository root (the `--output=logs/…` directives are
relative to it, and `logs/` is created on the fly). The launchers activate
`${PROJ}/.venv` and set `JULIA_NUM_THREADS=16`; the reference-study and
encode launchers run the encoder pass themselves when
`models/<run>/analysis/encoder_means_test.npy` is missing (`SHARDS_ROOT`
points them at the spectra shards). Two launchers
(`slurm_precision_preprocess_*.sh`) additionally refuse to run if the
job's account does not match `ACCOUNT`; pass `ACCOUNT=<your-account>` in
`--export` alongside `PROJ`.

Without a scheduler, `hpc/lightning/` runs the same task matrices in
persistent PySR/Julia workers (see below).

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
