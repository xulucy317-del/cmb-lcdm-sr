# scripts/ — the pipeline, one CLI per step

Every script runs from the repository root (`python scripts/<name>.py --help`);
`_bootstrap.py` puts `src/` on the path so nothing needs to be installed.
Inputs are the stored checkpoints, `data/`, and the caches under
`models/<run>/analysis/`; raw outputs go to `results/`, consolidated
deliverables to `experiments/`. Stage numbers follow the report
(`index.html`); the phase numbers in the docstrings follow the
pre-registered roadmap that produced the stage-1 deliverables.

## What a clone can run

`python scripts/check_inputs.py` prints this for your checkout, verifies
every input that has a canonical sha256, and names what a missing group
blocks.

| to run … | you need | in a clone? |
|---|---|---|
| the tests; every figure built from `experiments/*.json` | nothing beyond the clone | yes |
| **any SR search or audit** — stages 1–3, the MSE and precision campaigns, the four figure scripts marked † in `figures/README.md` | the caches under `models/<run>/analysis/`: the encoder posterior means and log-variances over the 50,000 test rows (4 files), which every search targets, and the per-latent residual caches the later phases start from (25 files) | **yes** — committed, byte-identical to the copies every reported number came from (sha256 in `data/inputs_manifest.json`) |
| the encoder pass, the spectral templates, stage 4 (encoder attribution) | the 500,000 CLASS spectra (`shards_global_lhs/`, `shards_global_lhs_ee_lowl/`, 100 `spectra_*.npz` each, 9.0 GB) | no — **not published**; the outputs of these three steps are committed, so they can be verified but not re-run |
| re-consolidating a published campaign without re-running its searches | the raw fronts, `results/<run>/<campaign>/…/report.json` (5,836 files) | the 13 MB asset of release [`v1.0.0`](https://github.com/xulucy317-del/cmb-lcdm-sr/releases/tag/v1.0.0): `gh release download v1.0.0 -p 'cmb-lcdm-sr-results.tar.gz*'`, `shasum -a 256 -c …sha256`, `tar -xzf` at the repository root, `python scripts/check_inputs.py --full` → 35/35 campaigns `canonical` |

A cache regenerated on different hardware agrees with the canonical one to
float32 precision but is not byte-identical (the residual caches to
≈10⁻¹⁵); `check_inputs.py` says which you have.

## Environment

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt        # or: pip install -e .[dev]
pytest -q                              # ~8 min; needs nothing beyond the repo
```

PySR downloads its own Julia on first import (one-off, several minutes).
All searches are CPU-only; the study ran with PySR 1.5.10 / Julia 1.11.9
and 16 Julia threads (`JULIA_NUM_THREADS=16`). `torch` is needed only for
the encoder pass, the decoder-effect stage and the stage-4 scripts.

## The unit of work, and the smallest end-to-end run

Everything is a matrix of `run_blind_sr.py` invocations — one target × one
input set × one PySR seed, writing `report.json` (the whole Pareto front
with per-equation held-out scores), `equations.csv` and `pareto.png` under
`results/<run>/…` — plus a `consolidate_*` step that writes the committed
`experiments/*.{md,json}`. The two-input amplitude study (about 5 min per
seed at 16 threads):

```bash
for N in 0 1 2 3 4; do
  python scripts/run_blind_sr.py --run-dir models/lcdm_tt_beta3e-4 --latent-index 2 --inputs A_s tau --seed $N --turbo
  python scripts/run_blind_sr.py --run-dir models/lcdm_tt_ee_lowl  --latent-index 5 --inputs A_s tau --seed $N --turbo
done
python scripts/run_shuffled_control.py --run-dir models/lcdm_tt_beta3e-4 --target-index 2 --shuffle-seed 0 --pysr-seed 0 --turbo
python scripts/pool_sr_runs.py --glob 'results/lcdm_tt_beta3e-4/symbolic_regression_gmm_mi_seed*/report.json' \
                               --out results/lcdm_tt_beta3e-4/sr_pooled
python scripts/consolidate_blind_sr.py
```

Two design points: the **GMM-MI inner loss** (`src/cmb_lcdm_sr/sr.py::JULIA_LOSS_GMM_MI`)
is a pure-Julia two-dimensional Gaussian-mixture MI estimator (fixed K = 2,
EM with regularised covariances, a strided 300-row sub-batch) returned as
`exp(−MI)`, and post-hoc selection re-scores every front expression with the
full Python `gmm-mi` estimator on held-out rows — inner loss and selection
metric share one invariance class, which is what makes the protocol blind.
**Data hygiene**: the 50,000 test rows are cut into three tiers that never
mix (`src/cmb_lcdm_sr/tiers.py`): T0 = rows 0–4,999, the only rows any
search sees; T1 = rows 5,000–24,999 for every calibration, audit and anchor
set; T2 = rows 25,000–49,999, opened once for the reported numbers.

**Naming.** `lcdm_tt_beta3e-4` is the temperature-only network ("TT",
5 latents) and `lcdm_tt_ee_lowl` the temperature + low-ℓ polarization
network ("EE", 6 latents); latents are `z0…z4` / `z0…z5`. Launchers for the
full campaigns, and how to submit them on another cluster, are in
`hpc/README.md`.

## Core: one search, one control, one encoder pass

| script | does |
|---|---|
| `encode_latents.py` | the one-off encoder pass: streams the test split through a stored checkpoint and caches `analysis/encoder_{means,logvars}_test.npy` (the only step that needs the spectra shards) |
| `run_blind_sr.py` | **one blind SR search**: one target (a latent column, or any cached vector via `--target-npy`) × one input set × one PySR seed, GMM-MI inner loss by default (`--inner-loss mse` for the stage-2 study), every front equation re-scored on held-out rows; writes `report.json`, `equations.csv`, `pareto.png` |
| `run_shuffled_control.py` | the negative control: the identical search against a row-permuted target |
| `pool_sr_runs.py` | pools per-seed `report.json` files by canonical form and ranks by cross-seed MI |
| `verify_phase0.py` | gate G0: the encoder caches exist, have the right shape, are finite, and a stored front re-parses end to end |
| `check_inputs.py` | what this checkout can run: reports the encoder caches, derived caches, spectra shards and raw fronts, verifies sha256 against `data/inputs_manifest.json` (or the pinned state file), and writes that manifest with `--write-manifest` |

## Stage 1 — discovery and validation (writes `experiments/<name>_<run>.*`)

| script | phase | does |
|---|---|---|
| `consolidate_blind_sr.py` | reference study | per-seed tables and the textbook-form scan for the two-input (A_s, τ) amplitude study |
| `consolidate_allparams.py` | six-input search | per-latent front tables, the derivative-ratio readout of the −2, shuffled controls |
| `sweep_blind_sr.py` | sweep planner | expands a spec in `hpc/sweeps/` into a task manifest (`plan`), reports progress and resubmit lines (`status`); also plans the 63-subset screen (`mode: subsets`) |
| `consolidate_hp_sweep.py` | sweep | comparison tables: top MI vs budget-matched MI@c≤10, one-factor effects, cost |
| `knee_readout.py` | 1 | cumulative Pareto envelopes, plateau, one-SE knee |
| `semantic_recurrence.py` | 2 | semantic clustering of front forms → canonical f₁ and R_SR |
| `sufficiency_audit.py` | 3 | sensitivity signatures, constant-ratio detector, calibrated sufficiency and the residual audit |
| `consolidate_subsets.py` | 4 | the blind subset screen and finalist fold-in → S\* and Î_S |
| `link_existing_subset_runs.py` | 4 / R-P4 | symlinks already-completed full-protocol runs into the exhaustive sweep so they are not re-run |
| `posterior_ceiling.py` | 5 | intrinsic ceiling I(Z_k; θ), posterior SNR, η_post |
| `consolidate_residual_sr.py` | 6 | second-stage coordinate f₂ from the residual fronts; `--variant ia` for the interaction-aware rerun |
| `build_f1hat_cache.py` | 6 (ia) | caches the stage-1 prediction h(f₁) used as the seventh input of that rerun |
| `levelset_audit.py`, `levelset_audit_joint.py` | 7a | the interventional level-set test for f₁ alone and for the pair (f₁, f₂) |
| `spectral_templates.py`, `decoder_effect.py` | 7b | data-driven parameter templates t_j(ℓ), then the decoder-effect decomposition |
| `subspace_probe.py` | 8 | sparse probes of the latent space and slab-conditional MI |
| `build_latent_cards.py` | 10 | assembles one card per latent under the frozen status predicates |
| `build_sham_inputs.py`, `consolidate_subsets_full.py`, `consolidate_sham_control.py` | R-P4 | the sham-input columns, the exhaustive-support readout and the dilution control |

## Stage 2 — the MSE study, the precision campaign and the linear baseline

| script | does |
|---|---|
| `consolidate_mse_one_stage.py` | `select` (T0) → `calibrate` (T1) → `confirm` (T2) for the one-stage MSE study; each stage hashes its output and the next verifies it |
| `run_mse_one_stage_pool.py` | scheduler-free executor of the MSE task matrix in persistent PySR/Julia workers (Lightning AI); task identity comes from the SLURM launcher's `PRINT_MATRIX=1` table |
| `verify_mse_one_stage_state.py` | hand-over verification: interpreter, packages, sha256 of every input, source and report against the execution-provenance record |
| `run_precision_preprocess_pool.py`, `consolidate_precision_preprocess.py` | the same pattern for the float64 precision / preprocessing campaign (three input conventions) |
| `audit_coordinate_matched_ols.py` | the coordinate-matched OLS audit (`fit` → `calibrate` → `confirm` → `render`) |
| `replay_ols_injection.py` | replays the stored maxsize-40 fronts with the exact OLS expression injected |
| `eta_post_ols_index.py` | η̂_post for the OLS index, on the same posterior draw as the discovered coordinates |
| `capacity_and_noise_floor.py` | train/validation gap, nearest-neighbour noise floor, gradient-boosting floor |

## Stage 3 — the ladder

| script | does |
|---|---|
| `build_ols_residual_cache.py` | caches e = μ_k − OLS(θ) over the test rows as the blind stage-2 target |
| `run_blind_sr.py --target-npy …`, `run_shuffled_control.py --target-npy …` | the search on that leftover and its permuted control (`hpc/lightning/run_residual_sr_ols.sh`) |
| `analyze_residual_sr_ols.py` | recurrence, nulls and the combined linear + formula account for the two latents searched |

## Stage 4 — inside the encoder

| script | does |
|---|---|
| `encoder_gradient_attribution.py` | ∂μ_k/∂x_ℓ at anchor spectra, projected onto the six physical response directions |
| `encoder_trunk_probe.py` | `--mode probe`: layer-wise linear probes through the trunk; `--mode steer`: input optimisation |

## Utilities

| script | does |
|---|---|
| `_bootstrap.py` | adds `src/` to `sys.path` for the other scripts |
