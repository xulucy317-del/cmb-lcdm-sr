# Report skeleton

No separate Results part: the pipeline already runs *question → instrument →
result → next question*, so a claim-oriented Part III would restate evidence
the reader has just been given. Claims stay visible by sitting **in the
section titles**; the cards become a cross-stage capstone at the end of
Part II. Nulls are introduced beside their instrument, not deferred.

Dropped: the 2-input amplitude reference study, entirely — including as a
control (§5 carries the self-contained replacement). Retained as a negative
result: the decoder stage, now §8.

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

  **6.x A multiplicative amplitude–shape interaction defeats the additive
  hierarchy**
  The specific mechanism, demonstrated in the TT amplitude latent: the forms
  are amplitude × shape, and an additive two-level account cannot absorb a
  multiplicative interaction. The pre-registered separation test fails there
  and only there; the interaction-aware rerun confirms real structure rather
  than an omission from the search ansatz. Claim scope: the multiplicative
  interaction is *demonstrated here*, not asserted of every latent.
  → *Raises*: is (f₁, f₂) the latent's coordinate system, or just a good fit?

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

**9. Degeneracy breaking splits rather than duplicates the amplitude sector**
Sparse probes for decodability from each latent; conditional MI for
redundancy versus synergy. Null: shuffled probes.
→ *Result*: one amplitude-sector latent in TT versus two in TT+EE — visible
in the raw disentanglement audit *before* any SR, so the fingerprint is blind
and model-level; after SR, the EE τ-direction is carried predominantly by one
latent, no redundant pair exists in either model, and the relevant latent
combinations are synergistic. Primaries are latent-anchored with distributed
tails; residual coordinates are genuinely distributed.

**10. The symbolic latent atlas**
The capstone, after all validation evidence: one card table per checkpoint —
role, f₁, support, recurrence, η ladder, level-set outcome, status (f₂ in an
extended table or appendix). What each status licenses and what it does not.
*Across two checkpoints, 10 of 11 latents are "primarily interpreted", with
one explicitly unresolved case.*

**11. Robustness, controls, and deviations**
An audit ledger, not a late reveal — each null has already appeared beside
its instrument; this collects them: shuffled-target SR, residual permutation
and shuffled-residual nulls, shuffled-form and wrong-latent level sets,
shuffled subspace probes, the positive-control gate, and the deviations
register.
