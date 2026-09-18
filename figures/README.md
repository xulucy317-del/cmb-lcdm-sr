# figures/ — the report figures and their generators

One `make_fig_<ID>_<name>.py` per figure ID, all sharing `figstyle.py`
(palette, checkpoint colours, the `save()` that writes the `.pdf` + `.png`
pair beside the script). Figure IDs are stable project identifiers:
`F<section>.<n>` numbered through the sections of the stage-1 report
(`docs/report_content.md`), with F12–F14 added for `report_conclusive.md`.
Gaps in the numbering are figures that were planned and not built, or built
and withdrawn.

Run any script from anywhere; the repository root is derived from the
script's location (`CMB_LCDM_SR_REPO` overrides). Most read only the
committed `experiments/*.json`; the four marked † also need the encoder
caches under `models/<run>/analysis/`, which are not in the repository.

| ID | file stem | shows | inputs | embedded in |
|---|---|---|---|---|
| F2.2 | `F2_2_audit_heatmap` † | MI(μ_k; θ_j) heatmap, both networks — the roles before any search (caches the KSG estimates in `_cache_audit_mi.npz`, git-ignored) | encoder means | conclusive §2.1, stage-1 §2 |
| F4.1 | `F4_1_envelopes` | cumulative Pareto envelopes with the shuffled-target null in-panel | `knee_readout_*`, `allparams_blind_sr_*` | conclusive §2.2, stage-1 §4, atlas |
| F5.1 | `F5_1_eta_ladder` | the η ladder per latent: η_S ≈ 1, η̂_post < 1 | `latent_cards_*` | conclusive §2.4, stage-1 §5 |
| F5.2 | `F5_2_staircases` | support-restricted ceiling vs support size | `latent_cards_*`, `subsets_full_*` | stage-1 §5 |
| F5.3 | `F5_3_residual_audit` † → writes `F5_3_residual_structure` | the EE z₅ stage-1 residual against ω_cdm: structured, not noise | residual caches | stage-1 §5 |
| F5.4 | `F5_4_signatures` | normalised sensitivity signatures g_j | `latent_cards_*` | stage-1 §5 |
| F5.5 | `amplitude_scatter` (`make_fig_amplitude.py`) † | the amplitude latent against ln(A_s e^{−2τ}), both networks | encoder means | README, conclusive §2.3, stage-1 §5.x |
| F5.6 | `F5_6_ratio_readout` | the derivative ratio per seed, with the constant-ratio detector | `allparams_blind_sr_*`, `latent_cards_*` | conclusive §2.3 |
| F5.7 | `F5_7_affine_vs_literal` | e^{−2τ} over the prior with its best affine fit (pure function plot) | — | stage-1 §5.x |
| F6.1 | `F6_1_stage2_gain` | what the second coordinate buys in η̂_post | `latent_cards_*` | conclusive §2.4, stage-1 §6 |
| F7.1 | `F7_1_invariance_ledger` | invariance error, f₁ alone vs the pair (f₁, f₂), log axis | `levelset_audit_*`, `latent_cards_*` | conclusive §2.5 |
| F7.2 | `F7_2_audit_vs_calibration` | E_inv(f₁) against 1 − R²_cal with the predicted band | `latent_cards_*` | stage-1 §7 |
| F8.2 | `F8_2_agreement` | cos(a\*, g_j): decoder loadings vs symbolic signatures | `latent_cards_*` | stage-1 §8 |
| F8.3 | `F8_3_ridge` | template collinearity and the drifting amplitude split | `decoder_effect_*`, `data/spectral_templates_v1.npz` | stage-1 §8 |
| F8.1 | (`experiments/decoder_effect_*_curves.png`) | the decoder-effect atlas, reused from the deliverable | — | stage-1 §8 |
| F11.2 | `F11_2_rp4_sham` | subset advantages on T2 and the sham-input control | `subsets_full_*`, `sham_control_*`, `latent_cards_*` | stage-1 §11 |
| F12.1 | `F12_1_affine_parity` | linear-baseline parity: reconstruction and stored-information fraction | `coordinate_matched_ols_v1`, `eta_post_ols_index_v1`, `latent_cards_*` | README, conclusive §3.1 |
| F13.1 | `F13_1_nonlinearity_ladder` † | the ladder linear → quadratic → SR on the leftover (refits the linear and quadratic rungs and asserts agreement with the audit) | encoder means, `coordinate_matched_ols_v1` | conclusive §4 |
| F14.1 | `F14_1_encoder_attribution` | reionization-window share of the projected gradient; layer-wise probe R² | `encoder_gradient_attribution_*`, `encoder_trunk_probe_*`, `latent_cards_*` | conclusive §5 |
| — | `decoder_amplitude` (`make_fig_decoder.py`) | amplitude rows of the decoder-effect curves in physical units | `decoder_effect_*_curves.npz` | archived paper draft |

**Withdrawn** (script kept as the recipe, no render committed): F1.1
pipeline schematic, F3.1 invariance schematic, F4.2 capacity dial, F9.1
count fingerprint, F9.2 split-not-duplicated. `make_fig_F1_1_pipeline.py`
draws the stage-1 pipeline overview and is a reasonable starting point for
a new schematic.
