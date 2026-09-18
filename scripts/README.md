# scripts/ — the pipeline, one CLI per step

Every script runs from the repository root (`python scripts/<name>.py --help`);
`_bootstrap.py` puts `src/` on the path so nothing needs to be installed.
Inputs are the stored checkpoints, `data/`, and the encoder caches under
`models/<run>/analysis/` (see the top-level README, "Data and models");
raw outputs go to `results/`, consolidated deliverables to `experiments/`.
Stage numbers follow `report_conclusive.md`; the phase numbers in the
docstrings follow `docs/discovery_roadmap.md`.

## Core: one search, one control, one encoder pass

| script | does |
|---|---|
| `encode_latents.py` | the one-off encoder pass: streams the test split through a stored checkpoint and caches `analysis/encoder_{means,logvars}_test.npy` (the only step that needs the spectra shards) |
| `run_blind_sr.py` | **one blind SR search**: one target (a latent column, or any cached vector via `--target-npy`) × one input set × one PySR seed, GMM-MI inner loss by default (`--inner-loss mse` for the stage-2 study), every front equation re-scored on held-out rows; writes `report.json`, `equations.csv`, `pareto.png` |
| `run_shuffled_control.py` | the negative control: the identical search against a row-permuted target |
| `pool_sr_runs.py` | pools per-seed `report.json` files by canonical form and ranks by cross-seed MI |
| `verify_phase0.py` | gate G0: the encoder caches exist, have the right shape, are finite, and a stored front re-parses end to end |

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
| `html_to_markdown.py` | regenerates `docs/findings_atlas.md` from `docs/findings_atlas.html` |
