# Report skeleton

No separate Results part: the pipeline already runs *question → instrument →
result → next question*, so a claim-oriented Part III would restate evidence
the reader has just been given. Claims stay visible by sitting **in the
section titles**; the cards become a cross-stage capstone at the end of
Part II. Nulls are introduced beside their instrument, not deferred.

Dropped: the 2-input amplitude reference study, entirely — including as a
control (§5 carries the self-contained replacement). Retained as a negative
result: the decoder stage, now §8.

**Figure & table programme (added 2026-08-18).** Sections below carry a
*Figures & tables* block. IDs are F⟨sec⟩.⟨n⟩ / T⟨sec⟩.⟨n⟩, numbered through
the ⟨sec⟩.x subsections; gaps left by dropped items (F1.1, F4.2, F5.6) are
not renumbered, so IDs stay stable against the built files. Status tags: *(exists)* — finished artifact on disk;
*(exists — extend)* — artifact or paper table to adapt; *(build: JSON)* —
render from a consolidated deliverable in `experiments/*.json`, no recompute;
*(build: cache)* — recompute from stored arrays (`models/*/analysis/`,
`data/`, `results/<run>/…`); *(build: doc)* — assembled from frozen text
(roadmap/compendium), no data; *(schematic)* — drawn, not computed. Items are
core unless tagged *(optional)* or *(appendix)*. Conventions, a
minimum-viable set, and a build order close the file.

---

## Part I — Setup

**1. Introduction**
Compressors are used as if their latents were physical; they are opaque.
Question: can a latent's content be recovered symbolically *without* telling
the search what to look for? Contributions: a pre-registered blind pipeline,
a validated card for every latent of two checkpoints, and structural findings
about how the encoder organises information.

**2. Data and models**
LHS ΛCDM samples → CLASS spectra → two stored β-VAE compressors (TT-only,
TT+EE-lowl). SR target = encoder posterior mean; the stochastic latent
supplies the intrinsic ceiling used in §5. Test-split tiers T0/T1/T2 and what
each may be used for.

*Figures & tables:*
* **T2.1 — checkpoints at a glance** *(build: JSON)*. Two rows
  (`lcdm_tt_beta3e-4`, `lcdm_tt_ee_lowl`): data regime, architecture
  (PirasCVAE L=5 / DualEncoderCVAE L=6), β = 3e-4, training seed, latent
  count, SR target (posterior mean μ), test rows. Sources:
  `models/*/config_used.json`, `data/meta.json`.
* **T2.2 — parameters and priors** *(build: JSON)*. The six raw inputs
  θ = (ω_b, ω_cdm, H0, τ, ln10¹⁰A_s, n_s) with LHS ranges from
  `data/meta.json` — the point being what the search is *not* given (no
  derived combination anywhere). May fold into T2.1's caption if space.
* **F2.1 — data → model → tiers** *(build: cache + schematic; optional)*.
  Three panels: (a) fan of CLASS spectra over the prior (colour = one
  parameter) for TT and EE-lowl; (b) encoder/decoder sketch with μ, logvar
  and the sampled Z — the stochastic latent that later supplies the §5
  intrinsic ceiling; (c) tier bar T0/T1/T2 with allowed uses (fit+val /
  calibration+audits / confirmatory only). Spectra from the parent `cmbvae`
  repo or decoder outputs; tiers from `src/cmb_lcdm_sr/tiers.py`. Panel (c)
  alone is the load-bearing part and can migrate into F3.1.
* **F2.2 — raw disentanglement audit** *(build: cache)*. Heatmap
  MI(μ_k; θ_j), all 11 latents × 6 parameters, both checkpoints side by
  side — fixes the audit-expected roles used everywhere downstream, and
  quietly shows the amplitude-column fingerprint §9 will read (one amplitude
  latent in TT, two in TT+EE). Recompute from
  `models/*/analysis/encoder_means_test.npy` + `data/theta.npy` (T1 rows);
  the finding itself is already stated in `docs/method.md` §1.

**3. Blind symbolic interpretation and pre-registered inference**
Inputs are raw parameters only; no derived combination is computed anywhere.
The inner loss is a real MI estimator, so it shares an invariance class with
the selection metric: any bijection of either variable leaves both unchanged.
Consequence — the search is rewarded for functional dependence, never for
matching the encoder's calibration. Two corollaries carried through the
report: the answer is an *equivalence class*, not an equation (forces the
canonical selection in §4); and the readable physics is whatever is
*invariant* under that class (forces the ratio field in §5, not the raw
coefficients). Pre-registration: thresholds frozen before unblinding, gates,
and a deviations register instead of silent judgement.

*Subsection*: the GMM-MI inner loss — fixed-K density model, cost, why an MI
loss rather than MSE. This is the reason blindness holds.

*Figures & tables:*
* **T3.1 — the frozen rulebook** *(build: doc)*. One row per pre-registered
  decision rule: plateau/one-SE knee, the three equivalence tests
  (canonical sympy ∨ |Spearman| ≥ 0.98 ∨ gradient-cosine ≤ 0.05), R_SR
  threshold, subset minimality, sufficiency levels + the η definitions,
  residual-audit pass, level-set 0.05, status predicates — columns: rule,
  frozen value, where it bites (§), outcome pointer. Source:
  `docs/discovery_roadmap.md` §0.3. This is the report's instrument ladder;
  the paper's ladder table is its condensed form.
* **F3.1 — the invariance class and its two corollaries** *(schematic)*.
  Left: raw θ only. Middle: SR with the GMM-MI inner loss. Right: held-out
  `gmm-mi` selection. The shared invariance class drawn as an orbit
  (g∘f ≃ f for any bijection g), with the two arrows the report keeps
  using: → equivalence class, hence canonical selection (§4); → invariant
  readout, hence the ratio field (§5). The tier bar (F2.1c) can live along
  the bottom.
* **F3.2 — inner loss vs selection metric** *(build: cache; optional)*.
  Scatter of the pure-Julia fixed-K=2 inner MI against the post-hoc full
  `gmm-mi` value on held-out rows, for every front expression of one
  all-params run (both models pooled), y = x overlay; annotate the ~80×
  speedup. The subsection's claim — the inner loss is a *real* MI
  estimator, so blindness holds — as one panel. Sources: run dirs under
  `results/<run>/allparams/z*_seed*/` + `experiments/allparams_blind_sr_*`.

---

## Part II — Discovery, validation, and results

**4. Every latent has a recurrent, low-complexity primary coordinate**
Six-input blind SR — all raw parameters into every latent, multiple seeds, no
input or latent pre-selection — returning Pareto fronts; then selection from
those fronts: cumulative envelopes, plateau and one-SE knee (saturation, not
argmax), and semantic recurrence across seeds by algebraic/statistical
equivalence rather than string matching. Generating fronts and choosing the
coordinate from them are one scientific step, not two.
*Include*: the hyperparameter finding — top-front MI is a capacity dial while
the budget-matched readout is flat, so complexity is a report-time slice, not
a search-time budget (search broadly, slice afterward). Null: shuffled-target
SR.
→ *Result*: a recurrent primary coordinate for every latent; every latent is
a multi-parameter composite; the −2 direction already appears in the
unrestricted search.
→ *Raises*: does f₁ actually account for the latent?

*Figures & tables:*
* **F4.1 — cumulative Pareto envelopes, both checkpoints** *(exists —
  extend)*. MI vs complexity per latent; plateau band and one-SE knee c*
  marked; shuffled-target control envelope overlaid at the bottom (≤ 0.06
  nat vs 2.3–3.8 real) so the null sits in-panel. Exists per model as
  `experiments/knee_readout_*_envelopes.png` (EE version already in the
  paper); rebuild as one two-row figure adding the control band from
  `allparams_blind_sr_*.json`.
* **T4.1 — primary coordinates, discovery columns** *(build: JSON)*. Per
  latent: audit-expected role, canonical f₁, knee c*, plateau MI, envelope
  shape (diffuse for 10/11), R_SR with cluster occupancy (n/5 seeds).
  Validation columns (η ladder, level sets, status) deliberately wait for
  the §10 cards. Sources: `experiments/knee_readout_*.json`,
  `semantic_recurrence_*.json`.
* **F4.3 — recurrence matrix** *(build: JSON; appendix)*. Latents × seeds,
  cell colour = semantic cluster of the knee-slice form — R_SR made
  visible, and with it the equivalence-class clustering (union-find +
  anti-chaining cohesion) doing real work. Source:
  `semantic_recurrence_*.json`.
* The "−2 already in the unrestricted search" readout is carried by the
  readout table (T5.2), not by a figure here — §4 only states it.

**5. Primary coordinates saturate their own support but not the full latent**
The central tension, and the reason "interpreted" needs a precise definition.
Instruments:
* sensitivity signatures and the answer-agnostic constant-ratio detector —
  a ratio of partials is the invariant that survives the equivalence class of
  §3, which is why physics is read here rather than off raw coefficients;
* exhaustive subset campaign (all non-empty supports, screened then rerun) →
  support-restricted ceilings → η_S;
* intrinsic ceiling from the stochastic latent → η̂_post;
* calibrated sufficiency — monotone recalibration, then residual audit
  against permutation nulls.
Define the **η ladder** here: saturates its own variables / fraction of the
searchable map / fraction of what the latent physically stores.
→ *Positive control, self-contained*: the amplitude latents' {A_s, τ} entry
in the subset campaign is the reference. The frozen machinery must rediscover
that support, saturate against its own ceiling, recover the exponent, **and**
still report the residual as structured — a control that can fail in both
directions.
→ *Result*: η_S ≈ 1 while η̂_post(f₁) < 1, with every stage-1 residual
structured. Each f₁ saturates its own variables yet accounts for only part of
what its latent physically stores. The instruments do not fabricate
sufficiency.
→ *Raises*: what is in the residual?

*Figures & tables:*
* **T5.1 — the three η's** *(build: doc)*. Three rows — η_S / η_plat /
  η̂_post: ratio of what to what, the question each answers (saturates its
  own variables? / fraction of the searchable map? / fraction of what the
  latent physically stores?), tier computed on, frozen role (η̂_post is the
  R-P5 demotion metric). Small, but every later section leans on it.
* **F5.1 — the η ladder, per latent** *(build: JSON)*. The section's
  centrepiece and the report's central quantitative figure: for each of the
  11 latents, aligned markers for η_S (≈ 1, with subset-ceiling SEs),
  η_plat at the knee slice, and η̂_post(f₁) — the visible gap between
  η_S ≈ 1 and η̂_post < 1 *is* the claim in the section title. Both
  checkpoints, card ordering. Sources: `experiments/latent_cards_*.json`
  (T2-confirmed rungs), backed by `sufficiency_audit_*.json` and
  `posterior_ceiling_*.json`.
* **F5.2 — subset-campaign staircases** *(build: JSON)*. Small multiples,
  one per latent: best support-restricted ceiling vs support size |S| over
  the complete 63-support × 5-seed full-protocol grid (budget-matched
  M_S^(c≤10)); S* and all-6 marked. The amplitude panels double as the
  positive control: the {A_s, τ} step highlighted and the all-6 superset
  finding annotated; caption names both fail directions the control armed
  (fabricated saturation / missed residual). Source:
  `experiments/subsets_full_*.json` (definitive; screen-era
  `subset_selection_*` only for provenance).
* **F5.3 — stage-1 residuals are structured** *(build: JSON + cache)*. Per
  latent, calibrated-residual R²_res (0.96–0.994) as dots with the
  permutation-null band (p97.5 ≈ ±0.002) hugging zero; inset: e₁ against
  its leading parameter direction for one representative latent, so the
  structure is *seen*, not just scored. Sources:
  `experiments/sufficiency_audit_*.json`; inset from
  `models/*/analysis/residual_z*.npy` + `data/theta.npy`.
* **F5.4 — sensitivity signatures** *(build: JSON)*. Heatmap of the
  normalised signature g_j (or Sobol share) of each canonical f₁ over the
  six parameters, both checkpoints — the instrument the ratio detector
  reads, and the object §8 will compare against decoder loadings
  (cos(a*, g_j)). Renders naturally as a companion panel to F2.2
  (audit-expected role vs discovered-form signature, side by side). Source:
  `experiments/sufficiency_audit_*.json`.
* **T5.3 — intrinsic ceilings** *(build: JSON)*. Per latent: I(Z_k; θ)
  (0.92–4.30 TT / 1.34–4.18 EE nat), posterior SNR (5.1 → 5,491 — the
  amplitude posteriors are near-deterministic, so their structured
  residuals are *real stored information*, the G3 fork), η̂_post(f₁).
  Mergeable into T6.1/T10.1 as columns if the venue wants fewer tables.
  Source: `experiments/posterior_ceiling_*.json`.

  **5.x The amplitude sector, recovered blind**
  The −2 evidence collected in one place, though it arises at different
  points of the pipeline: the discovered forms themselves; the derivative
  ratio across all top forms from the unrestricted search; the frozen
  answer-agnostic ratio detector; and the subset campaign, which finds the
  amplitude pair among all supports with no special status. Plus an unplanned
  reappearance inside another latent's residual coordinate (forward-reference
  to §6). Emphasise: no textbook reference exists anywhere in the pipeline,
  the readouts are methodologically independent, and the two checkpoints
  agree.

  *Figures & tables:*
  * **F5.5 — amplitude latent vs textbook combination** *(exists)*.
    `paper/figs/amplitude_scatter.pdf` — μ_amp against ln(A_s·e^{−2τ}),
    both checkpoints, tight monotone curves; report version may overlay the
    calibrated h(f₁). Built by `paper/figs/make_fig_amplitude.py`.
  * **T5.2 — every blind readout of the −2** *(exists — extend)*. The
    paper's readout table, kept as the subsection's spine: the discovered
    forms (affine constants vs the Taylor prediction); the derivative ratio
    over all top forms (−1.974 ± 0.018 TT / −1.993 ± 0.008 EE); the frozen
    ratio-field detector (r_raw = −2.000 on the cards); a decoder row
    stating **no readout** (forward-ref §8); a bonus row for the EE
    H0-latent residual `A_s·e^{−2τ}/ω_b²`, ratio −2.0000, found twice
    (§6/§6.x). Sources: `docs/results_compendium.md` §2 and the
    deliverables named there.
  * **F5.7 — why TT is affine and EE literal** *(build: trivial;
    optional)*. exp(−2τ) over the prior τ ∈ [0.01, 0.13] with its best
    affine fit (max deviation 0.52%): the two forms tie in MI, parsimony
    picks the affine one, and the discovered constants (0.598 TT / 0.579
    EE) sit within 1.5–5% of the Taylor prediction c = τ̄ + ½ ≈ 0.570.
    Pure function plot + constants from `docs/method.md` §3e.

**6. The latent map contains structure beyond two symbolic coordinates**
Blind SR on the stage-1 residual e₁ = μ − h(f₁), all inputs again;
hierarchical account h(f₁) + g(f₂); the interaction-aware rerun exposing the
stage-1 prediction as an extra input. Null: shuffled residuals.
→ *Result*: a recurrent second coordinate for every latent and a large gain
in η̂_post — but stage-2 residuals remain structured under both the additive
and the enriched ansatz. What is *global* is persistence beyond two
coordinates.
→ *Raises*: is the failure to close a property of the representation, or of
the additive ansatz?

*Figures & tables:*
* **F6.1 — what the second coordinate buys** *(build: JSON)*. Dumbbell per
  latent: η̂_post(f₁) → η̂_post(f₁+f₂) (0.29–0.84 → 0.59–0.96); right
  margin, per latent: stage-2 residual MI against the shuffled-residual
  null (0.40–1.77 vs ≤ 0.074 nat) — the large gain and the refusal to
  close in one figure. Sources: `experiments/latent_cards_*.json`,
  `residual_sr_*.json`.
* **T6.1 — second coordinates** *(build: JSON)*. Per latent: canonical f₂,
  R_SR, MI(f₂; e₁) with its null floor, combined R²(μ) (0.955–0.998),
  η̂_post(f₁+f₂), own-latent probe R² (0.01–0.58 — genuinely distributed;
  column borrowed from §9's instrument). This is the extended table §10
  defers; placing it here keeps the capstone cards compact. Sources:
  `experiments/residual_sr_*.json`, `subspace_probe_*.json`.

  **6.x A multiplicative amplitude–shape interaction defeats the additive
  hierarchy**
  The specific mechanism, demonstrated in the TT amplitude latent: the forms
  are amplitude × shape, and an additive two-level account cannot absorb a
  multiplicative interaction. The pre-registered separation test fails there
  and only there; the interaction-aware rerun confirms real structure rather
  than an omission from the search ansatz. Claim scope: the multiplicative
  interaction is *demonstrated here*, not asserted of every latent.
  → *Raises*: is (f₁, f₂) the latent's coordinate system, or just a good fit?

  *Figures & tables:*
  * **T6.2 — interaction-aware verdicts** *(build: JSON)*. Per latent:
    additive f₂ ≡ enriched f₂? f1hat used? DoD outcome. Highlighted rows:
    TT z2 — same τ-bearing knee coordinate with f1hat available but unused,
    so the additive failure is real structure (D-DoD-z2); EE z0 — unanimous
    interaction form, R_SR 0.80 → 1.00, invariance unchanged; EE z1 —
    residual again literally `A_s·e^{−2τ}/ω_b²` (cross-ref T5.2). Sources:
    `experiments/residual_sr_ia_*.{json,md}`.
  * **F6.2 — the multiplicative mechanism at TT z2** *(build: JSON +
    schematic; optional)*. Bar of the τ-clamp cost (0.20 nat at TT z2 vs
    ≈ 0 elsewhere) beside a two-line schematic: amplitude × shape vs
    h(f₁) + g(f₂) — why an additive hierarchy cannot absorb the
    interaction. Source: DoD numbers in `experiments/residual_sr_*.json`.

**7. The joint coordinate pair, not the primary alone, is the latent's
coordinate system**
Level sets: hold the coordinate fixed, move everything else, measure how much
the latent moves — for f₁ alone and for the joint pair. Nulls: shuffled form,
wrong latent.
→ *Result*: f₁ alone is not invariant, and the size of the failure matches
the calibrated residual variance quantitatively — audit and calibration agree
about what moves inside a level set. The joint pair restores approximate
invariance for nearly every auditable latent; the exception localises the one
unresolved case (EE z₀), whose residual holds more than one coordinate's
worth of structure.
→ *Raises*: does this hold outside the parameter domain?

*Figures & tables:*
* **F7.1 — invariance ledger** *(build: JSON)*. Per latent, E_inv on a log
  axis: f₁-only vs joint (f₁, f₂); frozen 0.05 line; shuffled-form
  (0.81–2.20) and wrong-latent (0.2–2.8) null ranges shaded above; EE z5's
  0.226 → 0.029 restoration and EE z0's joint fail (0.060–0.062, inside its
  predicted band) flagged; TT z1/z2/z4 marked "no nuisance direction left"
  (D-LS) rather than plotted as passes. Sources:
  `experiments/levelset_audit_*.json`, `levelset_audit_joint_*.json`
  (+ `_joint_ia_` for the EE z0 confirm).
* **F7.2 — audit agrees with calibration** *(build: JSON)*. Scatter of
  E_inv(f₁) against 1 − R²_cal, all 11 latents, with the predicted band
  [1−R², 2(1−R²)] shaded: 6 in-band, 5 above the factor-2 cap at the
  deliberately extreme-separation pairs (annotated). The section's
  quantitative claim — the level-set failure *is* the calibrated residual —
  in one panel. Sources: `levelset_audit_*.json` +
  `sufficiency_audit_*.json`.
* **F7.3 — distance curves and 1-D responses** *(build: JSON/cache;
  appendix)*. For one representative latent and for EE z0: invariance error
  vs level-set separation (monotone rise) and the matched-nuisance response
  leg with its spline fit (R² 0.91–1.00). Source:
  `levelset_audit_*.json` (curve arrays; recompute from caches if absent).

**8. Observable-domain triangulation: agreement where identifiable, and a
structural non-identifiability**
Decoder-effect templates — what moving a latent does to the spectrum,
decomposed onto data-driven parameter templates and compared against the
symbolic sensitivities of §5.
→ *Result, positive*: the decomposition is essentially complete and the
decoder-side loadings agree with the symbolic signatures — cross-domain
confirmation of *which parameters* a latent moves, for the shape sector.
→ *Result, negative*: the (τ, lnA_s) templates are near-collinear in both
designs, so the amplitude split lies along a degenerate ridge and is not
identifiable; the frozen gate fails on both models and the ratio it produces
drifts across fit variants. **The decoder yields no fourth −2 readout.** Note
that the amplitude latents' agreement cosines rest partly on ridge-drifting
components, so they are weaker evidence than the shape-sector ones. Report as
a genuine negative result: the stage works everywhere except the place it was
recruited to support.
→ *Raises*: is a coordinate a property of its own latent, or of the code?

*Figures & tables:*
* **F8.1 — decoder-effect atlas** *(exists — re-render)*. d_k(ℓ) for all 11
  latents (mean ± spread over anchors) with the template reconstruction
  overlaid and R²_W in-panel (0.988–1.000). Exists as
  `experiments/decoder_effect_*_curves.png`; re-render for print from
  `decoder_effect_*_curves.npz`.
* **F8.2 — cross-domain agreement** *(build: JSON)*. cos(a*, g_j) per
  latent (0.77–1.00): decoder-side loading vs symbolic signature (F5.4).
  Shape-sector points solid; amplitude-latent points hollow — their cosines
  rest partly on ridge-drifting components, the honest weakening behind
  "where identifiable". Source: `experiments/decoder_effect_*.json`.
* **F8.3 — the ridge: why there is no fourth readout** *(build: JSON +
  cache)*. The negative result gets a real figure. (a) t_τ(ℓ) and
  t_lnAs(ℓ) overlaid after scaling — near-antiparallel (uncentered cos
  −0.9996 TT / −0.9902 EE; condition numbers 70.2 / 14.2), the invisible
  direction (δτ, δlnA_s) ∝ (1, 2) stated in-panel; (b) the fitted amplitude
  split across fit variants (OLS / (2ℓ+1)-weighted / h/2 templates /
  anchor) sliding along the ridge at ≈ no change in R²_W, each point
  labelled with its implied r_dec (EE −1.87 / −1.67 / −1.77 / −2.32; TT
  +0.351). Caption: the decoder yields no fourth −2 readout. Sources:
  `data/spectral_templates_v1.npz`, `experiments/decoder_effect_*.json`;
  panel-(a) precursor exists as `paper/figs/decoder_amplitude.pdf`
  (`make_fig_decoder.py`).
* **T8.1 — G4b ledger** *(build: JSON)*. Frozen bullets vs outcomes per
  model: amplitude mass 0.64 / 0.79 vs ≥ 0.8 — FAIL both; |r_dec + 2| — TT
  FAIL, EE nominal pass ruled unidentifiable; R²_W — PASS both. Then the
  identifiable survivors: shape-sector coefficients and proj_brk on the
  degeneracy-breaking direction (EE z5: 0.047, stable across variants).
  Source: `experiments/decoder_effect_*.md`.

**9. Degeneracy breaking splits rather than duplicates the amplitude sector**
Sparse probes for decodability from each latent; conditional MI for
redundancy versus synergy. Null: shuffled probes.
→ *Result*: one amplitude-sector latent in TT versus two in TT+EE — visible
in the raw disentanglement audit *before* any SR, so the fingerprint is blind
and model-level; after SR, the EE τ-direction is carried predominantly by one
latent, no redundant pair exists in either model, and the relevant latent
combinations are synergistic. Primaries are latent-anchored with distributed
tails; residual coordinates are genuinely distributed.

*Figures & tables:*
* **F9.1 — the count fingerprint, before any SR** *(build: cache)*. The
  amplitude columns of the F2.2 audit isolated and annotated: one latent
  loading on (A_s, τ) in TT, two in TT+EE (z4 τ-anchored, z5 the
  combination); "pre-SR" stamped in-figure. Either a called-out crop of
  F2.2 referenced here, or its own small panel. Source: same recompute as
  F2.2.
* **F9.2 — split, not duplicated** *(build: JSON)*. (a) Paired bars per
  coordinate: own-latent probe R² for f₁ (0.88–0.95, latent-anchored) vs f₂
  (0.01–0.58, distributed), with the shuffled-probe null (≈ 0.000) as
  baseline; (b) the synergy exhibit: I(z1; A_s·e^{−2τ}) alone vs
  conditioned on z5 — 0.013 → 0.473 nat — plus a per-model glyph row for
  "no redundant pair; every top-2 carrier conditional synergistic".
  Source: `experiments/subspace_probe_*.json`.
* **T9.1 — carrier sets** *(build: JSON; appendix)*. Per coordinate: 1-SE
  carrier set (own latent always present for f₁; A* = {z2, z4} for the EE
  τ-direction, own-probe R² 0.946), own-latent R², redundancy-vs-synergy
  verdict. Folds into T6.1 columns if space is tight. Source:
  `experiments/subspace_probe_*.json`.

**10. The symbolic latent atlas**
The capstone, after all validation evidence: one card table per checkpoint —
role, f₁, support, recurrence, η ladder, level-set outcome, status (f₂ in an
extended table or appendix). What each status licenses and what it does not.
*Across two checkpoints, 10 of 11 latents are "primarily interpreted", with
one explicitly unresolved case.*

*Figures & tables:*
* **T10.1 — the cards, both checkpoints** *(exists — extend)*. The capstone
  table, one row per latent: role, f₁, support (S* + the new
  `s_star.exhaustive_full`), η_S, η̂_post(f₁), η̂_post(f₁+f₂), R_SR,
  level-set outcome (joint E_inv or D-LS), flags (N-G2 dispositions),
  status. f₂ itself lives in T6.1. The paper's card table is the starting
  point; all values are the T2-confirmed card numbers. Source:
  `experiments/latent_cards_*.{json,md}`.
* **T10.2 — what a status licenses** *(build: doc)*. Two columns for
  "primarily interpreted": licensed claims vs explicitly not-licensed
  (no full sufficiency, per-checkpoint scope, no VAE-seed claim); one row
  for "unresolved" (EE z0) naming the localised blocker — a residual
  holding more than one coordinate's worth of structure.
* **F10.1 — the atlas plate** *(build: JSON; optional)*. One page, 11
  mini-cards: role, f₁ typeset, mini η ladder, level-set tick/cross, status
  colour. The report's poster figure if the venue rewards it; the
  highest-effort visual in the programme and purely presentational — all
  content already in T10.1.

**11. Robustness, controls, and deviations**
An audit ledger, not a late reveal — each null has already appeared beside
its instrument; this collects them: shuffled-target SR, residual permutation
and shuffled-residual nulls, shuffled-form and wrong-latent level sets,
shuffled subspace probes, the positive-control gate, and the deviations
register.

*Figures & tables:*
* **T11.1 — master controls ledger** *(exists — adapt)*. The compendium's
  §7 table, one row per null: control, real-signal value, null value, and
  the section where it was introduced. Source: `docs/results_compendium.md`
  §7 (the paper carries the condensed form).
* **F11.1 — control margins at a glance** *(build: JSON; optional)*. One
  strip, log axis: paired dots (real vs null) for every control — the
  3×–1000× separations visible without reading a number. Data = T11.1.
* **T11.2 — gates ledger** *(build: JSON)*. G0–G4b × model, one-line
  outcomes: G1 PASS both (positive control, both fail directions armed);
  G2 8/11 PASS + 3 ATTENTION → all dispositioned by R-P4; G3 PASS (DPI
  holds; residuals are stored information); G4a f₁-only FAIL everywhere —
  *by design informative* — G4a-joint PASS (EE) / undefined-by-support
  (TT); G4b FAIL both (§8). Source: the gates blocks in
  `experiments/latent_cards_*.json`.
* **T11.3 — deviations register** *(build: doc)*. D-P2a, D-P2b, R-P5,
  D-LS, D-DoD-z2, and the three N-G2 flags with their R-P4 dispositions:
  frozen gap → decision → evidence → effect on claims (none flipped a
  status). Sources: cards + `docs/discovery_roadmap.md`.
* **F11.2 — R-P4: subset advantages and the sham mechanism** *(build:
  JSON)*. (a) Per latent, the T2 paired contrast M_{S⁺} − M_{all-6} with
  ±SE and the 6/11 confirmations marked (substantive: TT z3 +0.090 ± 0.062
  dropping {τ, A_s}; EE z2 +0.115 ± 0.104 dropping {H0, τ}; EE z3
  +0.085 ± 0.040 dropping A_s; EE z4 +0.126 ± 0.047 with
  S⁺ = {ω_cdm, τ, A_s, n_s}; hairline: EE z0/z5 ≤ 0.003). (b) Sham control
  per model: TT Δ_sham = −0.0404 ± 0.0134 (dilution demonstrated, 3 SE) vs
  EE +0.0137 ± 0.0126 (null); annotate "sham symbol in 0.0% of
  best-at-c≤10 forms" — degradation is search-space dilution, never
  complexity spend. Caption carries the crossed reading: TT has the
  mechanism but (z3 aside) no confirmed subset advantage; EE has five
  advantages but no generic mechanism — specific-distractor removal, not
  search-space size. Sources: `experiments/subsets_full_*.json`,
  `sham_control_*.json`.
* **T11.4 — compute ledger** *(build: doc; appendix)*. Per stage: searches
  and core-h (hp_v1 ~77/model; 4a screen ~1,015; ia follow-up 98 measured;
  R-P4 grid + sham ≈ 5,800 measured; ≈ 1,800 pre-R-P4 → ≈ 7,600 all-in),
  hardware (icelake), and the grid accounting (3,465 cells; 2,425 fresh,
  1,040 reused with verified protocol match). Sources: roadmap budget
  table, compendium header + §10.

---

## Figure & table inventory (build notes)

**Built (2026-08-18).** 16 in-programme figures rendered to
`paper/figs/F<id>_*.{pdf,png}`, one script per ID
(`paper/figs/make_fig_F*.py`, shared style in `figstyle.py`; palette = the
dataviz reference instance, validated order): F2.2 audit heatmap (KSG
recompute, cached in `_cache_audit_mi.npz`) · F3.1 invariance schematic ·
F4.1 envelopes (rebuilt, both models + null band) · F5.1 η ladder ·
F5.2 staircases · F5.3 residual audit · F5.4 signatures · F5.7
affine-vs-literal · F6.1 stage-2 gain · F7.1 invariance ledger · F7.2
audit-vs-calibration · F8.2 agreement · F8.3 the ridge · F9.1 fingerprint ·
F9.2 split-not-duplicated · F11.2 R-P4 + sham. Every number cross-checked
against the compendium during the build; note F8.3 works in
scaler-standardised design space (T_norm = T_phys/σ — the raw npz
templates do NOT reproduce the documented cos values) and shows all four
fit variants (TT spans r_dec +0.60 → −2.85 along the ridge; the frozen
OLS bullet is +0.35). *Dropped from the programme (2026-08-18): F1.1
pipeline schematic, F4.2 capacity dial, F5.6 ratio readout — their
scripts/renders remain in `paper/figs/` but they are not part of the
report; the hyperparameter finding and the derivative-ratio readout are
carried in text and by T5.2.* Still to build: F5.5/T5.2/T10.1/T11.1 reuse
paper material; F2.1, F3.2, F4.3, F6.2, F7.3, F10.1, F11.1 optional; F8.1
re-render from the existing `_curves.npz` when needed; all T-tables are
report-text work.

**Counts.** Core: 16 figures, 13 tables; plus 10 optional/appendix items.
Heavier than a letter, right for a full report — and the per-latent tables
are designed as non-overlapping column sets, so consolidation is mechanical:
T5.3 folds into T6.1, T4.1's discovery columns and T9.1 fold into T10.1.

**Minimum viable set** (if the venue is tight, these alone carry the
argument): F4.1 (envelopes + null), F5.1 (η ladder), F5.5 (amplitude
scatter), F6.1 (second-coordinate dumbbells), F7.1 (invariance ledger),
F8.3 (the ridge), F9.2 (split-not-duplicated), F11.2 (R-P4/sham) + tables
T3.1 (rulebook), T5.2 (−2 readouts), T10.1 (cards), T11.1 (controls).

**Conventions.**
* Both checkpoints in every per-latent figure (TT row above, EE row below,
  or paired columns); latent order = card order everywhere.
* Nulls are drawn in-panel (shaded band or paired dot), never quoted only in
  captions — "nulls beside their instrument" applies to the visuals too.
* One fixed colour per parameter across all figures; one accent per
  checkpoint; one shared 3-level status scale (interpreted / attention /
  unresolved) across F9.2, T10.1, F10.1.
* Log axes wherever a frozen threshold is compared against nulls (F7.1,
  F11.1) or MI spans decades.
* Per-latent numbers in tables are the T2-confirmed card values; every
  figure caption names the tier it draws on (T0-val vs T1 vs T2), matching
  the §2 hygiene table.
* Captions end with the per-checkpoint scope note wherever a claim could be
  misread as model-general (compendium C8).

**Sources of truth.** Consolidated `experiments/*.json` are canonical; raw
run dirs under `results/<run>/…` only for F3.2 and appendix panels;
`models/*/analysis/*.npy` + `data/theta.npy` for anything needing rows.
Finished artifacts to reuse: `paper/figs/amplitude_scatter.pdf` (F5.5),
`paper/figs/decoder_amplitude.pdf` (F8.3a precursor),
`experiments/knee_readout_*_envelopes.png` (F4.1),
`experiments/decoder_effect_*_curves.{png,npz}` (F8.1). The
`paper/figs/make_fig_*.py` scripts are the pattern to extend; new figure
scripts should live beside them, one script per figure ID.

**Suggested build order (leverage ÷ effort; executed 2026-08-18).**
1. F5.1 (η ladder) — the report's centrepiece; pure JSON read.
2. F7.1 + F7.2 — carries §7 on their own; pure JSON.
3. F6.1 (dumbbells + stage-2 nulls).
4. F11.2 (R-P4 contrasts + sham) — the freshest result; pure JSON.
5. F8.3 (the ridge) — the honest negative deserves its figure early.
6. F4.1 rebuild (both models + null band in one figure).
7. F2.2 / F5.4 / F9.1 (audit + signature heatmaps; one cheap MI recompute —
   sbatch it, not the login node).
8. F5.2 (staircases), F5.3 (residual audit).
9. Schematic (F3.1) and the doc-built tables — text-side work, no compute.
