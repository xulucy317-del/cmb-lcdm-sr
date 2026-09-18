# experiments/ — consolidated results (the committed deliverables)

One entry per campaign, written by the matching `consolidate_*` / audit
script from the raw fronts under `results/` (not committed). Per-checkpoint
files carry the run name as a suffix: `<experiment>_lcdm_tt_beta3e-4.*` is
the temperature-only network (TT, 5 latents), `<experiment>_lcdm_tt_ee_lowl.*`
the temperature + low-ℓ polarization network (TT+EE-lowl, 6 latents). The
`.md` is the human-readable summary, the `.json` the machine-readable payload
every figure and report number is traced to. Campaign-level files
(`*_v1.*`) cover both checkpoints in one file.

The stage numbers follow `report_conclusive.md`; the "phase" numbers quoted
inside the stage-1 files follow `docs/discovery_roadmap.md`, the
pre-registered programme that produced them.

## Stage 1 — discovery and validation under frozen rules

| files (`_<run>.{md,json}` unless noted) | what it holds | produced by |
|---|---|---|
| `allparams_blind_sr`, `allparams_blind_sr_ms10` | six-input blind SR on every latent, 5 seeds, maxsize 20 (and the maxsize-10 rerun): per-latent front tables, derivative-ratio readout of the −2, shuffled-target controls | `scripts/consolidate_allparams.py` |
| `hpsweep_hp_v1` | the PySR hyperparameter sweep on the amplitude latents (12 configs × 3 seeds): top MI vs the budget-matched MI@c≤10, one-factor effects, cost | `scripts/consolidate_hp_sweep.py` |
| `knee_readout` (+ `_envelopes.png`) | Phase 1 — cumulative Pareto envelopes pooled over capacity families; plateau Î_plat, one-SE knee c\*, envelope class per latent | `scripts/knee_readout.py` |
| `semantic_recurrence` | Phase 2 — semantic clustering of front forms (canonical sympy ∨ Spearman ∨ gradient distance); the canonical primary coordinate f₁ and its recurrence R_SR | `scripts/semantic_recurrence.py` |
| `sufficiency_audit` | Phase 3 — sensitivity signatures, the answer-agnostic constant-ratio detector, cross-fitted monotone calibration h(f₁) and the stage-1 residual audit (gate G1) | `scripts/sufficiency_audit.py` |
| `subset_selection` | Phase 4 — the blind 63-subset screen and the full-protocol finalist reruns: minimal support S\* per latent and the support-restricted ceilings Î_S (gate G2) | `scripts/consolidate_subsets.py` |
| `posterior_ceiling` | Phase 5 — the intrinsic ceiling I(Z_k; θ) from the stochastic latent, posterior SNR, η_post (gate G3) | `scripts/posterior_ceiling.py` |
| `residual_sr` | Phase 6 — blind SR on the stage-1 residual e₁ = μ − h(f₁): the second coordinate f₂, combined account h(f₁)+g(f₂), shuffled-residual nulls | `scripts/consolidate_residual_sr.py` |
| `residual_sr_ia` | the interaction-aware rerun of Phase 6 with the stage-1 prediction exposed as a seventh input | `scripts/consolidate_residual_sr.py` (+ `scripts/build_f1hat_cache.py`) |
| `levelset_audit`, `levelset_audit_joint`, `levelset_audit_joint_ia` | Phase 7a — the interventional level-set test: invariance error for f₁ alone, for the pair (f₁, f₂), and for the interaction-aware pair (gate G4a) | `scripts/levelset_audit.py`, `scripts/levelset_audit_joint.py` |
| `decoder_effect` (+ `_curves.{npz,png}`) | Phase 7b — decoder-effect templates d_k(ℓ) decomposed onto data-driven parameter templates; the collinearity ridge that leaves the amplitude split unidentifiable (gate G4b) | `scripts/decoder_effect.py` (templates: `scripts/spectral_templates.py`) |
| `subspace_probe` | Phase 8 — sparse linear probes of the latent space (carrier sets A\*) and slab-conditional MI redundancy; "split, not duplicated" | `scripts/subspace_probe.py` |
| `latent_cards` | Phase 10 — one card per latent assembling Phases 1–8 under the frozen status predicates, plus the gates table, controls appendix and deviations register | `scripts/build_latent_cards.py` |
| `subsets_full`, `sham_control` | post-closure R-P4 — the exhaustive 63-support grid at full protocol under a budget-matched readout, and the sham-input dilution control | `scripts/consolidate_subsets_full.py`, `scripts/consolidate_sham_control.py` |

## Stage 2 — the linear baseline and the objective comparison

| files | what it holds | produced by |
|---|---|---|
| `mse_one_stage_sr_<run>.{md,json}` | the one-stage MSE reconstruction study (165 searches at maxsize 20/30/40 + 12 controls) with its three-stage immutable consolidation, and the pre-registered six-input OLS control that turned out to matter | `scripts/consolidate_mse_one_stage.py` |
| `mse_one_stage_sr_plan.md` | the pre-registered plan for that study, with its execution amendments A1/A2 | written before the runs |
| `mse_one_stage_execution_provenance.json`, `mse_one_stage_state_csd3.json`, `mse_one_stage_state_lightning.json`, `mse_one_stage_lightning_runbook.md` | the execution record: sha256 of every input, source file and report, the CSD3 → Lightning AI hand-over, machine state on both sides. These pin file paths and commit IDs as they were at execution time; see `docs/README.md` for what was renamed since | `scripts/verify_mse_one_stage_state.py`, `hpc/lightning/` |
| `precision_preprocess_v1_comparison.json` (summary: `docs/precision_preprocess_v1_comparison.md`) | the float64 precision / input-preprocessing campaign (330 searches in three input conventions) | `scripts/consolidate_precision_preprocess.py` |
| `coordinate_matched_ols_v1.json` (summary: `docs/coordinate_matched_ols_v1.md`) | the coordinate-matched OLS audit: OLS refitted in each convention's own inputs and compared on three endpoints | `scripts/audit_coordinate_matched_ols.py` |
| `ols_injection_replay_v1.json` | replay of the stored maxsize-40 fronts with the exact OLS expression injected: the rules would have kept it in 43/55 runs — the search never generated it | `scripts/replay_ols_injection.py` |
| `eta_post_ols_index_v1.json` | the stored-information fraction η̂_post of the OLS index, the ceiling column missing from the stage-1 tables | `scripts/eta_post_ols_index.py` |
| `capacity_and_noise_floor_v1.{md,json}` | train/validation gap over every stored front (no overfitting anywhere), nearest-neighbour noise floor, and the gradient-boosting floor of Table 3.3 | `scripts/capacity_and_noise_floor.py` |

## Stage 3 — the ladder (linear → quadratic → SR on the leftover)

The quadratic rung is exact least squares and is recomputed inside
`figures/make_fig_F13_1_nonlinearity_ladder.py`. The blind search on the
OLS residual of EE z₀ and EE z₄ writes `results/lcdm_tt_ee_lowl/residual_sr_ols/`
(`scripts/build_ols_residual_cache.py`, `scripts/run_blind_sr.py --target-npy`,
`scripts/analyze_residual_sr_ols.py`); its numbers are recorded in
`docs/evidence_record.md` §6.5–§6.6 and `report_conclusive.md` §4.

## Stage 4 — inside the encoder

| files | what it holds | produced by |
|---|---|---|
| `encoder_gradient_attribution_<run>.{json,npz}` | ∂μ_k/∂x_ℓ at 64 anchor spectra, projected onto the six physical response directions; the reionization-window share per latent | `scripts/encoder_gradient_attribution.py` |
| `encoder_trunk_probe_<run>.json` | layer-wise ridge probes for τ, ln A_s and ln A_s − 2τ from the input, each convolutional block and the latent means | `scripts/encoder_trunk_probe.py --mode probe` |
| `encoder_input_optimisation_<run>.json` | the smallest input change that moves one latent while holding the others, compared with the physical responses (a clean negative) | `scripts/encoder_trunk_probe.py --mode steer` |
