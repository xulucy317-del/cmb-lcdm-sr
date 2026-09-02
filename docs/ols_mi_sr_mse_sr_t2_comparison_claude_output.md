# What the record establishes — OLS vs MI-SR vs MSE-SR, and the state of every claim

*Written 2026-08-31 from the repository's own artifacts (`experiments/`,
`docs/`, `results/`, git history). Provenance note: this file was drafted
**without consulting** `docs/ols_mi_sr_mse_sr_t2_comparison_codex_output.md`,
per instruction; any agreement or disagreement with that file is independent.
An additive completion pass the same day — after the codex checkpoint was
read — folded in the fresh-experiment record it covered and this draft had
not: the §2.2 chronology/seedwise/count-hygiene material, §2.5–§2.6, the
expanded −2 record in §2.4, inventory row 8, and §7 items 4 and 7. Every
number in those additions was **re-verified against primary artifacts** (the
audit's fit/confirmation JSONs; an independent replay of the 55 stored
`mse_one_stage_ms40` fronts, reproducing the stored OLS validation MSE to
< 10⁻⁶ relative; sums and derivations over the frozen tables) — none is
quoted unverified. A third pass (2026-09-01) added §6 — the additive-physics
reading, the attribution reframing, the hybrid plan, and a measured Step-1
quadratic pilot — and renumbered the final two sections to §7/§8. Later
same-day/next-day additions carry their own dates in place: §6.6 (the Step-2
hybrid campaign), the tightened §6.2 trust-scope argument, the W3
absence-claims retraction, §7 item 9 (PySR v2.0 assessment), and §0.1
(the four-step storyline). "T2" throughout means the confirmatory tier
(test rows 25k–50k, `src/cmb_lcdm_sr/tiers.py`), as everywhere in the repo.*

---

## 0. Verdict

A refitted six-input ordinary-least-squares map — seven numbers per latent —
is the strongest single account of most encoder means, on the SR methods' own
endpoints. Both confounds that could have explained this away have now been
tested and ruled out as the main story: calibration asymmetry (the MSE
follow-up's TM3) and float32/ill-conditioned inputs (the three-arm float64
precision/preprocessing campaign with its coordinate-matched OLS audit,
T2-opened 2026-08-31). Across the three arms, OLS wins the mixed-pipeline
reconstruction comparison in 6–9 of 11 latents and matches or beats the median
MI-SR winner's *mutual information* in 4–6 of 11.

This does **not** invalidate any recorded number, gate, or control — the frozen
record stands, and it is the programme's own honesty machinery (pre-registered
baselines and diagnostics) that surfaced the problem. What changes is what the
record *licenses*. Claims about the representation survive: the amplitude
sector organises as `A_s·e^{−2τ}` with the −2 read multiple independent ways;
the per-latent role atlas; the degeneracy-breaking split; near-determinism
plus a structured remainder at every probed level. Claims that give the
*specific discovered expressions* privileged explanatory status do not
survive: for 8–9 of 11 latents the canonical symbolic coordinates are one
member of a large near-equivalence class that contains a plain affine map, and
the affine member is usually the better account. The clean SR-specific value
is concentrated in two latents (EE z4, EE z3) plus the basis-free discovery of
the amplitude combination.

§6 records the constructive reading adopted on top of this verdict: in the
log-spectrum basis the additive account *is* the physics, the deliverable
becomes component attribution, and a measured nonlinearity ladder (affine →
quadratic → SR) localises the genuinely beyond-polynomial content to EE z4
and EE z0. Step 2 of that ladder (§6.6) has now characterised both: a
unanimous `A_s/τ` coordinate at z4 — whose hybrid account, at 1.30% NMSE,
is the best reconstruction of that latent ever measured — and a recurrent,
strongly non-monotone shape-sector curvature at z0 worth half of its
residual.

### 0.1 The storyline — how the study moved, in four steps

*Added 2026-09-02 from discussion. A narrative complement to the verdict
above; §1–§8 are the record it summarises. Item 4 proposes work that has not
been run and is not in the §7 open-items list.*

1. **The aim, and the probe.** We set out to use SR to find an expression for
   each of the 11 learnt latents across the two checkpoints, feeding all six
   cosmological parameters as inputs and selecting on MI (MSE came later, as
   the one-stage follow-up of §1 row 7). We hoped the sectors would separate —
   shape latents free of `A_s` and τ, amplitude latents free of the shape
   parameters — and we planned to use the known combination `A_s·e^{−2τ}` as a
   probe of whether the network had found the physics. The separation did
   **not** appear at the level of support: every latent came back a
   ≥5-parameter composite, and TT z4 is an H0 latent whose canonical form
   contains both `A_s` and `e^{−2τ}`. It did appear at the level of leading
   direction, where five independent instruments agree on which parameter
   dominates each latent (E2). The probe worked, and better than planned: the
   reionization exponent reads **−1.974 ± 0.018** (TT) and **−1.993 ± 0.008**
   (EE) as a derivative ratio over all top forms, and −2.0000 from a frozen
   answer-agnostic detector (E1).

2. **What the affine baseline actually showed.** The hyperparameter sweep
   did not show forms becoming linear at high complexity — it showed that
   top-of-front MI is a *capacity dial* (§1 row 3), and that at high
   capacity the returned forms become *idiosyncratic* rather than convergent
   (TM8, W1). What surfaced the real problem was the **pre-registered OLS
   baseline inside the MSE follow-up**: a plain six-input affine map, seven
   numbers per latent, beat the ms40 symbolic winner in 8 of 11 latents. The
   coordinate-matched audit (§2) then ruled out the three confounds that
   could have explained it away — calibration asymmetry, float32
   conditioning, and the basis mismatch that had been handing SR the
   log-amplitude coordinate while denying it to OLS — and OLS still wins 6–9
   of 11. Crucially this does **not** mean the latents are linear, and that
   over-reading was corrected explicitly (commit `71b395c`): the OLS
   residual is itself 97–99% predictable from the same six parameters, so
   each mean map is a steep, essentially deterministic function whose
   *second* derivative, not its first, is small. Narrow priors are also only
   half the diagnosis. Because the target is log D_ℓ, the amplitude and tilt
   sectors are linear *exactly*, at any prior width; the narrow box only
   suppresses the genuinely nonlinear *shape*-sector curvature to about the
   percent level (§6.1). Widening the priors would change the shape sector
   and essentially nothing else — a limit on **scope**, not a flaw in the
   result, which is why the wider-prior campaign is parked (§7 item 7).

3. **Why we then searched the residual.** Accepting the affine floor, we ran
   SR again on the exact OLS residual — but *not* because the physics hides
   there. In the log basis the affine part **is** the physics, and its
   coefficients are the attribution deliverable: which latent carries which
   parameter combination (§6.2). We ran residual SR because it is the only
   question left with an unknown answer, and because the affine → quadratic →
   SR ladder localises where beyond-polynomial structure actually lives. It
   does: 21 exact quadratic terms close 33–94% of the beyond-affine gap in 9 of
   11 latents, and fail on exactly two (§6.5). Residual SR then characterised
   both (§6.6). EE z4 gave `A_s/τ` at complexity 3, unanimous across five
   seeds, whose hybrid account at 1.30% NMSE is the best reconstruction of that
   latent ever measured. EE z0 gave recurrent shape-sector curvature that no
   polynomial expresses, and — more useful — a *mechanism*: its relation to the
   residual is strongly non-monotone, which is why every earlier
   monotone-calibrated account of that latent stalled. The honest limit is that
   this is two latents out of eleven, on the two Step 1 had already flagged,
   all post-hoc on T2 rows already read.

4. **What transfers from LLM interpretability** *(proposals, none run)*. Most
   of that machinery exists to defeat **superposition**, and there is none here
   — a 5–6 dimensional bottleneck with a known candidate feature basis, so
   sparse autoencoders and dictionary learning have nothing to resolve. Three
   of those methods already run in this programme under other names: *steering*
   is the decoder-side intervention (which hit a wall — the template
   collinearity that failed G4b), *interchange intervention* is the level-set
   audit, and the *probing ladder* is affine → quadratic → SR, with the ceiling
   (η̂_post) and null battery that probing papers usually lack. Three things
   would be genuinely new: **gradient attribution** ∂z_k/∂C_ℓ, one backward
   pass per latent, giving ℓ-space attribution immune to the collinearity that
   killed G4b; **encoder input optimisation**, driving a target latent while
   holding the others fixed and comparing the resulting spectral pattern
   against the true CAMB response functions; and a **layer-wise probe of the
   encoder trunk**, asking where the (lnA_s − 2τ) combination first becomes
   linearly decodable — the one circuits question never opened here (the model
   lives in the parent `cmbvae` repo). One connection worth keeping: z0's
   non-monotonicity (§6.6) is the *linear representation hypothesis* failing
   locally, which is exactly the regime that literature has language for.

---

## 1. What has been done — complete inventory

Two stored β-VAE checkpoints (TT `PirasCVAE` L=5; TT+EE-lowl
`DualEncoderCVAE` L=6; both β=3e-4, training seed 42), 11 latents, one frozen
search protocol (PySR, GMM-MI inner loss, 5000 T0 samples, ni200/pop15/ms20,
5 seeds), tiered data hygiene T0/T1/T2. All claims per-checkpoint.

| # | Layer | When | Scale | Deliverable | Headline |
|---|---|---|---|---|---|
| 1 | Reference reproduction: (A_s, τ) → amplitude latent | pre-08 | 10 runs + 6 controls | `docs/method.md` §1–4 | `A_s·(τ−0.598)` 5/5 TT seeds; literal `A_s·e^{−2τ}` in EE; constants match the Taylor prediction c = τ̄+½ to 1.5–5% |
| 2 | All-params blind SR (6 inputs → all 11 latents; +ms10/ms30) | pre-08 | ~143 runs | `experiments/allparams_blind_sr_*` | every latent a ≥5-parameter composite; r = (∂f/∂τ)/(∂f/∂lnA_s) = **−1.974 ± 0.018** (TT) / **−1.993 ± 0.008** (EE); shuffled controls ≤ 0.06 nat |
| 3 | Hyperparameter sweep `hp_v1` | pre-08 | 72 runs | `experiments/hpsweep_hp_v1_*` | top-front MI is a capacity dial (1.6 → 4.05 nat on maxsize alone); budget-matched MI@c≤10 flat (~1.89/2.02 nat); r ≈ −2 in every config |
| 4 | Discovery roadmap phases 0–8, 10 | 08-03 → 08-06, closed 08-09 | ~1,700 core-h incl. the 1,386-run 63-subset screen | `experiments/{knee_readout,semantic_recurrence,sufficiency_audit,subset_selection,posterior_ceiling,residual_sr,levelset_audit*,decoder_effect,subspace_probe,latent_cards}_*` | gates G0/G1/G3 PASS; G2 8/11 + 3 attention; G4a-joint PASS on EE (7/8 auditable latents); G4b FAIL both (template collinearity); **10/11 "primarily interpreted", EE z0 unresolved**; hierarchy non-terminating |
| 5 | Interaction-aware stage 2 (f1hat as 7th input) | 08-09 | 55 + 6 controls, 98 core-h | `experiments/residual_sr_ia_*`, `levelset_audit_joint_ia_*` | D-DoD-z2 is real structure; 8/11 return the identical f₂; EE z0 upgrades to a unanimous interaction form yet stays unresolved; no status changes |
| 6 | R-P4: exhaustive 63-support grid at full protocol + sham control | 08-13/14 | 3,465 cells (2,425 fresh) + 165 sham, ≈5,800 core-h | `experiments/subsets_full_*`, `sham_control_*` | crossed result: TT has the dilution mechanism (Δ_sham −0.040 ± 0.013, 3 SE) but almost no confirmed subset advantage; EE has five confirmations (four substantive, +0.09 to +0.13 nat) but a null sham; 0.0% of best forms use the sham symbol; all three N-G2 flags dispositioned, no status flips |
| 7 | One-stage MSE reconstruction | 08-26 (Lightning AI) | 165 searches + 12 controls | `docs/mse_one_stage_results.md`, `experiments/mse_one_stage_sr_*` | no `one-stage replacement`; known f₂ absorbed **0/11** (variance leg 32/55, MI leg 2/55 — "laundering"); calibration explains most of the apparent MSE-objective landslide (9/11, not 11/11); **plain 6-input OLS beats the ms40 winner 8/11** |
| 8 | Primary three-way T2 snapshot: frozen physical-basis OLS vs T1-calibrated MI-SR (`mi20-mi`) vs raw MSE-SR (`mse40`) | 08-26 → 08-31 | replay of the stored fronts, no new search | `docs/ols_mi_sr_mse_sr_t2_comparison.md.orig` (preserved verbatim inside the codex checkpoint) | mixed winners by median T2 NMSE: **OLS 7 · MI-SR 2 (TT z0, EE z4) · MSE-SR 2 (EE z2, EE z3)**; seedwise, MSE-SR beats OLS NMSE in only 17/55 runs |
| 9 | Precision/preprocessing campaign (three float64 arms) | 08-28 → 08-31 (Lightning/Mac, scheduler-free pool) | 330 searches (3 arms × 2 objectives × 11 latents × 5 seeds) | arm profiles in `src/cmb_lcdm_sr/sr.py` (`raw64`, `physical_o1_64`, `logamp64`); campaign deliverable `docs/precision_preprocess_v1_comparison.md` + `experiments/precision_preprocess_v1_comparison.json` (recovered from the studio to CSD3, 2026-09-01); raw run artifacts off-CSD3 | reruns both objectives at precision 64 with (a) raw inputs, (b) order-one physical rescalings, (c) `ln10¹⁰A_s` in place of `A_s`; its own *unmatched* readout (frozen OLS vs each arm's SR) gave mixed winners 9/2 → 6/5 → 5/6, the only SR majority ever observed (§2.2) |
| 10 | Coordinate-matched OLS audit of the campaign | rendered 08-31 | fit(T0) → calibrate(T1) → confirm(T2) | `experiments/coordinate_matched_ols_v1.{json,md}`, `results/*/coordinate_matched_ols_v1/` | the pivot result of §2 below |
| 11 | Write-up state | 08-14 → 08-26 | — | `report.md` (§1–10), `paper/main.tex` (7 pp, incl. R-P4), `docs/report_content.md` (16 built figures), `docs/results_compendium.md` | none of these yet contains the OLS-parity result; compendium §9's claim menu C1–C8 predates it |

Working-tree note: the campaign/audit infrastructure is currently
**uncommitted** (modified `src/cmb_lcdm_sr/{sr,semantics}.py`,
`scripts/run_blind_sr.py`; untracked `scripts/{run_precision_preprocess_pool,
consolidate_precision_preprocess,audit_coordinate_matched_ols}.py`, tests,
HPC wrappers, and both audit deliverables), and the campaign's own
select/confirm artifacts live off-CSD3 (Lightning/Mac; only the audit-stage
JSONs are synced under `results/*/coordinate_matched_ols_v1/`).

---

## 2. The pivot: affine parity

### 2.1 The comparison, as frozen

`scripts/audit_coordinate_matched_ols.py` refits OLS **per preprocessing arm**
on the 4,000 T0-fit rows (inputs centred/scaled with T0-fit statistics —
conditioning changes, the affine hypothesis class does not), and compares on
three endpoints, all confirmed on T2:

* **Direct reconstruction** — uncalibrated NMSE: OLS vs the MSE-SR ms40 winner.
* **Coordinate reconstruction** — the *identical* 64-bin T1-only monotone
  calibration applied to both OLS and the MI-SR ms20 winner, then NMSE.
* **Information** — full GMM-MI on the exact frozen 5,000-row T2 subset, OLS
  prediction vs the MI-SR winner.

Seedwise verdicts use unadjusted 95% paired-row CIs (descriptive, not a pooled
test); SR brackets are median [min, max] over valid seeds. One scope caveat the
audit itself carries: it is tier-disciplined internally (fit opens T0 only →
calibrate T1 only → confirm T2 once) but **post-hoc as a study** — T2 had
already been read by the earlier comparisons — so it is a fairness audit on
frozen artifacts, not a preregistered fresh holdout.

### 2.2 Headline counts (from `experiments/coordinate_matched_ols_v1.md`)

| Arm | Direct raw NMSE | Coordinate calibrated NMSE | Median MI-SR MI > matched OLS | Mixed-pipeline winner |
|---|---|---|---|---|
| `raw64` | OLS 9 · MSE-SR 2 | OLS 6 · MI-SR 5 | 5/11 | OLS 9 · MI-SR 0 · MSE-SR 2 |
| `physical_o1_64` | OLS 6 · MSE-SR 5 | OLS 6 · MI-SR 5 | 7/11 | OLS 6 · MI-SR 1 · MSE-SR 4 |
| `logamp64` | OLS 7 · MSE-SR 4 | OLS 7 · MI-SR 4 | 6/11 | OLS 7 · MI-SR 1 · MSE-SR 3 |

(`raw64` and `physical_o1_64` OLS are affine-equivalent by construction — one
invariance check, not two wins; `logamp64` is the genuinely different affine
model.)

**How the counts evolved.** Three passes were made over the same frozen T2
rows, and the movement between them is itself part of the result:

| Pass | OLS treatment | Mixed-pipeline winners (OLS · SR) |
|---|---|---|
| Original three-way snapshot (row 8 of §1; float32-era fronts) | frozen physical-basis OLS | 7 · 4 (MI-SR 2, MSE-SR 2) |
| Unmatched campaign readout (float64 arms) | same frozen OLS vs each arm's SR | `raw64` 9 · 2 → `physical` 6 · 5 → `logamp64` **5 · 6** |
| Coordinate-matched audit | OLS refitted per arm | `raw64` 9 · 2 → `physical` 6 · 5 → `logamp64` **7 · 4** |

The unmatched middle row is the only pass that ever produced an SR majority
(`logamp64`, 5·6) — and it is exactly the pass in which OLS was denied the
log-amplitude basis SR had been given. Matching the coordinate removes the
majority. (Middle-row counts re-derived here by setting the frozen OLS row
against each arm's SR medians; they reproduce.)

**Seedwise CI verdicts**, summed over the per-latent `OLS/SR/inc` counts of
the audit tables (unadjusted paired-row 95% CIs; descriptive, not a pooled
test):

| Arm | Direct (OLS / SR / inc) | Calibrated (OLS / SR / inc) |
|---|---|---|
| `raw64` | 36 / 19 / 0 | 31 / 22 / 2 |
| `physical_o1_64` | 20 / 31 / 3 (54 valid) | 24 / 30 / 1 |
| `logamp64` | 33 / 21 / 1 | 35 / 20 / 0 |

Count hygiene: the units disagree by design and must not be interchanged. In
`physical_o1_64` the seedwise direct verdicts lean **SR** (31/54) while the
latent-median winners lean OLS (6·5): SR's wins are concentrated (5/5 sweeps
on its latents), its losses diffuse. Likewise "8/11" (latent medians vs
`mse40`, float32 era), "17/55" (seed runs, original snapshot), and these CI
verdicts are different units on different campaigns. None is a significance
test.

One further equal-treatment caveat: the shared 64-bin calibration can *hurt*
an already well-calibrated OLS predictor (`logamp64` TT z2: raw 0.044% →
calibrated 0.140%), so the calibrated column tests symmetric coordinate
treatment, not each pipeline's best deployment.

### 2.3 The confounds are now checked, and they narrow but do not flip the verdict

1. **Calibration asymmetry** (MSE study TM3): raw `mi20-mse` NMSE ≈ 1.0 is an
   artifact of MI's bijection invariance; with symmetric monotone calibration
   the MSE objective wins 9/11 rather than 11/11. The coordinate-matched audit
   applies the identical calibrator to OLS and MI-SR — and OLS still wins 6–7
   of 11.
2. **Precision and conditioning** (this campaign): float64 plus order-one
   physical rescaling is the *best* arm for SR (direct winners go from 9–2 to
   6–5) — so numerics were a real, but secondary, handicap. No arm reverses
   any headline count.
3. **Coordinate mismatch**: the campaign's own unmatched readout — the frozen
   physical-basis OLS held fixed against each arm's SR — made `logamp64` look
   SR-favourable (mixed winners SR 6 · OLS 5; derivable by setting the frozen
   OLS row against the arm's SR medians). Refitting OLS in the arm's own
   coordinates reverses it to OLS 7 · MI-SR 1 · MSE-SR 3: the apparent SR edge
   was OLS being denied the basis SR had been given.
4. **Hypothesis-class budget**: a full 6-input affine map costs ≈ 25 PySR
   nodes (6 vars + 7 constants + 12 operators), so the ms20 MI search cannot
   even represent it — its comparison is budget-asymmetric *against* SR. But
   the ms40 MSE search can represent it, with in-search constant optimisation,
   and still loses 6–9 of 11: stochastic search does not reliably match exact
   least squares on its own criterion. Conversely, OLS is fitted for MSE, not
   MI — its MI showing is not rigged in its favour.

### 2.4 Why a 7-coefficient map is this strong

* **The mean maps are nearly affine over the prior box.** The LHS ranges are
  narrow (e.g. ω_b ∈ [0.020, 0.024], lnA_s span 0.28); OLS reaches NMSE
  0.04–1.4% on 9/11 latents (TM4/TM5). This is a statement about the box, not
  about ΛCDM in general.
* **Neither OLS nor SR is near the floor.** The OLS residual is itself 97–99%
  predictable from the same six parameters by gradient boosting (NMSE
  ≈ 2×10⁻³ → ≈ 3×10⁻⁵) — reconstruction margin discriminates weakly between
  hypotheses here, which is exactly why the discovery protocol selected on MI
  in the first place.
* **Even on MI the affine map is close to the ceiling.** Indicative cross-tier
  comparison (audit's T2 OLS MI vs the T0-val all-params plateau of T4.1): in
  each latent's best arm, OLS carries ≈ 92–99% of the plateau MI for 10 of 11
  latents. The exception is **EE z4 at ≈ 78%** — the one latent with a genuine
  low-dimensional nonlinearity.
* **The −2 falls out of the linear probe.** The `logamp64` design matrix
  contains six separate columns — `tau` and `ln10As` unconstrained and untied
  — yet the fitted amplitude pieces factor as
  `8.4167·(ln10As − 1.9785·τ)` (TT z2) and `8.9659·(ln10As − 1.9967·τ)`
  (TT+EE z5): b_τ/b_lnAs = **−1.9785** and **−1.9967**, fixed entirely from
  T0-fit, at standardised condition number 1.021 and T0-val R² of
  0.99959/0.99961 (verified against
  `results/*/coordinate_matched_ols_v1/logamp64/fit.json`). A linear readout
  in the *sampled* basis recovers the reionization exponent without any
  symbolic search. Caveats as the audit records them: the ratios carry no
  confidence interval, are conditional partial slopes in a six-input
  regression, and were inspected for the two *pre-designated* amplitude
  latents — recovery of a known direction, not an independent discovery, and
  no claim that either latent is one-dimensional.
* **A predicted (untested) corollary for the level sets**: the level-set audit
  itself validated E_inv ≈ [1, 2.6] × (1−R²_cal). With OLS residual fractions
  of 0.0005–0.014 on 9/11 latents, the plain OLS index would be expected to
  pass the frozen E_inv ≤ 0.05 rule on those latents — i.e. the interventional
  instrument, as frozen, would certify an affine coordinate too. Not run;
  stated as a prediction.

### 2.5 Where the search loses — mechanism, verified on the stored fronts

Two post-hoc diagnostics on the 55 stored `mse40` reports
(`results/*/mse_one_stage_ms40/*/report.json`), independently replayed for
this file (the replayed OLS validation MSE reproduces every stored
`ols_baseline.mse_val` to < 10⁻⁶ relative):

* **The gap is visible before T2.** The frozen OLS baseline has lower
  T0-*validation* MSE than the validation-selected SR equation in **39/55**
  seed runs (TT 24/25, EE 15/30); the median ratio
  MSE_val(SR)/MSE_val(OLS) is **1.445** (range 0.43–329).
* **Usually, no front member ever beat OLS.** Replaying the stored OLS
  coefficients on the 4,000 T0-fit rows in the same standardised target, OLS
  has lower fit MSE than **every** equation on the returned Pareto front in
  **38/55** runs (TT 23/25, EE 15/30). In most runs the loss is therefore not
  a selection or generalisation effect — the search never produced an
  affine-competitive candidate to select.
* **The 17 fit-side exceptions cluster exactly on the SR-favoured latents of
  the §3 ledger**: all five EE z4 seeds, all five EE z3 seeds, three EE z2
  seeds, two EE z5 seeds, and one seed each of TT z2/z3. The mechanism
  diagnostic and the endpoint verdicts agree about where nonlinearity pays.

Together these localise the SR losses to candidate discovery, constant
fitting, or front retention — which of the three cannot be separated from
stored artifacts alone (§7 item 4 is the test that separates them) — and not
to any surprise created on T2.

**Injection, selection-level (computed 2026-08-31 for this file).** Placing
the exact T0-fit OLS expression into each frozen `mse40` candidate set at its
true complexity (25) and applying the unchanged rules: it would be *retained*
on the Pareto front in **43/55** runs (lower fit MSE than every stored member
of complexity ≤ 25) and would *win* the unchanged minimum-validation-MSE
selection outright in **39/55** (TT 24/25, EE 15/30). Selection never
discarded affine candidates — the search never generated one. The 16 runs
where selection would legitimately keep the SR form over injected OLS are
exactly the SR-favoured cells of §3: EE z3 and EE z4 (all five seeds each),
EE z2 (seeds 0/2/3), EE z5 (seeds 0/1), TT z3 (seed 1). Front-retention vs
selection also splits one overfit case: TT z2 seed 4 beats OLS on fit but
loses on validation. Still open from the full staged diagnostic: *why* the
search never produced the candidate (mutation path vs constant tuning), and
the calibrate/confirm legs — though TM4 already gives the T2 answer at
latent-median level.

### 2.6 Validity and exclusion record (audit confirmation stage)

All matched-OLS GMM-MI evaluations are valid. Two frozen MSE-SR replays are
not, and are excluded from valid-only summaries (verified in
`results/lcdm_tt_ee_lowl/coordinate_matched_ols_v1/*/confirmation.json`; both
TT cells are clean): EE `physical_o1_64` z0 seed 4 — 93.116% finite T2
predictions, invalidating its raw-NMSE row, its MI replay, and one direct
paired contrast (that cell has 54, not 55, direct verdicts) — and EE
`logamp64` z4 seed 3 — fully finite predictions but a non-finite GMM-MI
estimate.

---

## 3. Per-latent ledger

Synthesis over the three arms and three endpoints (sources: the three tables
of `experiments/coordinate_matched_ols_v1.md`; TM4/TM5 of
`docs/mse_one_stage_results.md`). "SR value-added" asks: does *any* SR
pipeline beat matched OLS consistently across arms on at least one endpoint,
with margins above seed scatter?

| Latent | Role | Canonical f₁ | MI verdict | Calibrated-NMSE verdict | Direct-NMSE verdict | SR value-added |
|---|---|---|---|---|---|---|
| TT z0 | ω_b | `n_s/ω_b` | mixed (SR +0.09 nat in logamp only) | SR in all 3 arms (−0.02 to −0.05 pp) | arm-dependent | **partial** |
| TT z1 | ω_cdm | `H0²n_s²ω_b/(A_s ω_cdm²)` | OLS everywhere (small) | OLS 5/0 in all arms | OLS-lean | none |
| TT z2 | amplitude | `A_s/log(H0(ω_cdm+τ))` | SR beats raw-basis OLS (3.75 vs 3.52), loses to logamp OLS (3.71 vs 4.00) | SR in raw/physical, OLS in logamp | OLS all arms (up to 12× in float32 era) | **basis story only** |
| TT z3 | n_s | `n_s + ω_cdm` | SR in physical (+0.19) | mixed | SR in physical | partial |
| TT z4 | H0 | `A_s H0² ω_cdm e^{−2τ}` | OLS everywhere (−0.15 to −0.46) | OLS everywhere | OLS everywhere | none |
| EE z0 | ω_cdm/eISW (unresolved) | `ω_cdm/(H0 n_s ω_b)` | SR slightly (+0.04–0.07) | OLS everywhere (+0.8–1.2 pp) | OLS | none (worst reconstruction of all 11 for every method) |
| EE z1 | H0 | `H0² ω_cdm` | mixed | mixed | OLS-lean | none |
| EE z2 | ω_b | `ω_b/n_s²` | tie | OLS-lean | arm-dependent | none/marginal |
| EE z3 | n_s | `log(ω_b)/(n_s+ω_cdm)` | **SR all arms** (+0.16 to +0.30 nat) | **SR all arms** (−0.05 to −0.09 pp) | **SR all arms** | **yes** |
| EE z4 | τ (amplitude sector) | `−A_s/(τ−0.445)` | **SR all arms** (+0.46–0.49 nat) | **SR all arms** (−2.6 to −2.8 pp) | **SR all arms** (1.2–1.8 vs 4.2–4.3%) | **yes — the flagship** |
| EE z5 | amplitude | `A_s e^{−2τ}` | SR beats raw-basis OLS (3.92 vs 3.55), loses to logamp OLS (3.82 vs 4.04) | mixed → OLS in logamp | OLS all arms | **basis story only** |

Reading of the two "basis story" rows: on the amplitude latents, MI-SR's
advantage over raw-basis OLS is real, and it is precisely the search
*synthesising the logarithm* — hand the affine model the sampled log-amplitude
basis and the advantage disappears (and the −2 appears in its coefficients).
That is a genuine, well-circumscribed discovery role for SR: it found the right
basis blindly. It is not a claim that the symbolic form outperforms a linear
model given that basis.

---

## 4. What we can establish (claims that stand)

**E1 — The amplitude sector organises as `A_s·e^{−2τ}`, and the −2 is
multiply-determined.** Encoder-side readouts: (i) the discovered forms
(literal `A_s e^{−2τ}` in EE, affine `A_s(τ−c)` with c matching the Taylor
prediction in TT); (ii) the derivative ratio over all six-input top forms,
−1.974 ± 0.018 / −1.993 ± 0.008; (iii) the frozen answer-agnostic
constant-ratio detector, r_raw = −2.0000; (iv) the unplanned reappearance in
EE z1's residual, `A_s e^{−2τ}/ω_b²`, twice (additive and interaction-aware
runs); and now (v) the `logamp64` OLS coefficient ratios −1.979/−1.997.
The float64 campaign's frozen scan adds breadth: the exact differential
signature ∂f/∂τ = −2·∂f/∂lnA_s appears verbatim in representative
T0-selected equations in every arm (4 MI-SR in `raw64`, 1 in
`physical_o1_64`, 3 MI-SR + 2 MSE-SR in `logamp64`;
`docs/precision_preprocess_v1_comparison.md`).
Readout (v) *strengthens* the robustness of the physics while *weakening* the
"symbolic search was required" framing: state it as "the structure is strong
enough that even a linear probe in the sampled basis reads it; the blind
search located it without being given the basis." The decoder domain still
contributes no readout (G4b FAIL, template collinearity) — unchanged.

**E2 — The per-latent role atlas is robust.** The leading parameter(s) per
latent agree across five independent instruments: the raw MI audit (F2.2,
pre-SR), MI-SR sensitivity signatures, the MSE search's first-recruited
support at c≤5 (TM7: 11/11 agreement), the decoder-template loadings
(cos(a*, g) 0.77–1.00), and — implicitly — the dominant OLS coefficients.
Role-level and support-level statements ("TT z3 is the n_s+ω_cdm direction",
"EE z4 is the τ-anchored amplitude latent") are among the safest claims in
the repo.

**E3 — Degeneracy breaking splits, not duplicates, the amplitude sector —
SR-free.** One amplitude-sector latent in TT vs two in TT+EE, visible in raw
parameter MI before any search; z4 carries the τ-direction essentially alone;
no redundant latent pair in either model (all top-2 carrier conditionals
synergistic; conditioning on z5 raises z1's information about `A_s e^{−2τ}`
from 0.013 to 0.473 nat). None of this depends on symbolic regression.

**E4 — The representation is near-deterministic, close-to-affine over the
box, with real structure at every probed level.** Posterior SNR 5.1–5,491
(amplitude latents near-deterministic ⇒ residuals are stored information, not
noise; DPI checks hold). μ_k(θ) is ≈ 99.8% affine over the box, and what
remains is structure, not noise, at every level anyone has probed: stage-1
residuals structured 11/11 (R²_res 0.96–0.994 vs nulls ≈ 0), stage-2
residuals structured 11/11 under both additive and interaction-aware ansätze,
the direct ms40 expressions still leave f₂-dependence at 10–140× the
permutation null (the "laundering" result), and the OLS residual is 97–99%
GBM-predictable. The honest formulation of the old "non-terminating
hierarchy" claim is basis-free: *every account tried so far — symbolic
two-stage, direct ms40, affine — leaves behind structured, predictable
residue; the mean maps have no small exact description in any probed class.*

**E5 — Where SR genuinely beat the linear baseline, it found real
nonlinearity.** EE z4 (`−A_s/(τ−0.445)`, a pole in τ): SR wins every endpoint
in every arm (MI +0.46 nat; calibrated NMSE ~1.4% vs 4.2%), and its OLS MI
sits at only ~78% of plateau — the one latent whose leading structure is
irreducibly non-affine at this resolution. EE z3 is the second, more moderate
case. These are the exhibits for any claim that the SR stage detects what a
linear probe misses.

**E6 — A set of transferable methodological findings, each now
multiply-supported.**
* Top-of-front MI is a *capacity* dial, not a discovery meter; budget-matched
  readouts are flat across tuning (hp_v1).
* MI-selected expressions carry no calibration by construction; comparing
  objectives requires symmetric calibration (TM3).
* A single large expression *launders* rather than absorbs a known secondary
  coordinate — variance-based and information-based sufficiency tests
  disagree systematically (TM2); test both legs.
* Input-set dilution is model-dependent and mechanism-separable (R-P4's
  crossed sham/subset result; 0.0% sham-symbol uptake).
* **A matched classical baseline is a mandatory control for symbolic latent
  interpretation.** On near-affine targets, both MSE and MI endpoints are
  nearly saturated by least squares; without the OLS row, 8–9 of 11 of this
  study's "discovered coordinates" would have carried unearned weight. This
  is arguably the study's most exportable lesson, and the pipeline's frozen
  design (pre-registration → controls → confirmation tiers) is what caught it.

**E7 — The control battery is clean.** Shuffled-target ≤ 0.06 nat;
shuffled-residual ≤ 0.074 vs real 0.40–1.77; level-set shuffled/wrong-latent
nulls 0.2–2.8 vs passes ≤ 0.03; probe nulls ≈ 0; MSE shuffled controls
|R²| ≤ 0.006 even at ms40; permutation nulls ≈ ±0.002. G1 passed on both
models *including* the required honest failure of the residual audit. The
instruments do not fabricate structure.

**E8 — Scope, unchanged and now sharper.** Everything is per-checkpoint
(R_model/Phase 9 never run) and prior-box-local (near-affinity is a property
of the narrow LHS box; none of these statements extend beyond it).

---

## 5. What is weakened, and how to restate it

**W1 — "Latent k means f_k."** For 8–9/11 latents the canonical coordinate is
MI- and NMSE-matched (or beaten) by an affine map; the discovered form is one
representative of a broad equivalence class, selected by search idiosyncrasy
as much as by structure. Restate as: *the latent's leading dependence is
direction D with support S (E2); the printed algebraic form is a compact
representative, not an identified law.* The MSE study's TM8 says the same
thing internally: form-family consensus across seeds decays with capacity
even as accuracy saturates.

**W2 — "The primary coordinate saturates its own support" (η_S ≈ 1).** True
as frozen — but η_S is a ratio of *search outputs* (form MI over
restricted-front ceiling), and the audit shows a plain affine index carries
substantially more information about the latent than most canonical f₁'s
(e.g. TT z2: OLS MI 3.5–4.0 nat vs the knee-level M(c≤10) ≈ 1.89 the f₁
represents). η_S ≈ 1 licenses "f₁ exhausts its own variables at its own
complexity", not "f₁ is the latent's principal account". The η ladder was
built to keep these apart; the gloss around it sometimes hasn't.

**W3 — Structural readings of the discovered forms beyond leading direction
and the −2.** The specific nestings (`A_s/log(H0(ω_cdm+τ))`, the f₂ algebra,
etc.) should not be given mechanistic weight: they are not stable across
capacity, and affine parity shows the data cannot adjudicate between broad
families at these margins. The exceptions are the amplitude combination
(multiply-determined, E1) and EE z4's pole (E5). The same logic retracts
inference-from-absence: the diffuse-envelope reading ("front information is
spread over complexity") and any structural claim read off the *shape* of a
Pareto front are statements about the generator, not the data — §2.5's
invisible affine optimum is the counterexample (full argument in §6.2).

**W4 — The two-stage hierarchy as *the* architecture of the code.** The
h(f₁)+g(f₂) accounts (R²(μ) 0.954–0.998) are dominated on 8–9/11 latents by
the single OLS map (e.g. TT z2: h+g NMSE 0.74% vs OLS 0.10%). The hierarchy
is a property of the chosen decomposition, not of the representation; what is
representation-level is E4 (structure at every level, in every account
tried). The f₂ discoveries remain real recurrent structure in *those*
residuals, with clean nulls — but "the encoder computes f₁ then f₂" was
never licensed and should not be implied.

**W5 — The interventional certificate (G4a-joint).** The joint (f₁,f₂)
level-set pass is genuine but not discriminating: by the audit's own
validated E_inv↔residual relation, an affine index would be predicted to pass
the same frozen rule on at least 9/11 latents (§2.4, untested). Keep the
pass; drop any implication that passing singles out the symbolic pair.

**W6 — "10/11 primarily interpreted."** Keep only with the frozen-predicate
definition attached, plus one sentence of context: *the statuses certify
recurrence, own-support saturation, and joint-level-set invariance of the
discovered pair under pre-registered rules; they do not certify that the pair
outperforms — or is distinguishable from — a six-input affine account, which
subsequent audits show it generally is not.* The 10/11 number is unchanged;
its advertised meaning must be.

**Status table**

| Claim (compendium §9) | Status after the audits |
|---|---|
| C1 (−2, three readouts) | **stands, amended** — add the linear-probe corollary (E1) and drop "SR-necessary" implications |
| C2 (validated cards, 10/11) | **stands as frozen record; interpretive gloss weakened** (W1/W2/W6) |
| C3 (degeneracy-breaking split) | **stands** (SR-free) |
| C4 (methodology) | **stands, strengthened** — the baseline audit belongs inside it (E6) |
| C5 (non-terminating hierarchy) | **stands, restated basis-free** (E4, W4) |
| C6 (negative results) | **stands, extended** — laundering, calibration artifact, affine parity join it |
| C7 (η̂_post reframing) | **stands** as a metric; per-form values now need the OLS comparison column (§7 item 2) |
| C8 (per-checkpoint scope) | **stands** |

---

## 6. The constructive reading — additive physics, attribution, and the nonlinearity ladder

*Added 2026-09-01 from discussion. §6.1–§6.4 record framing and plan; §6.5 is
a measured Step-1 pilot.*

### 6.1 The affine floor is the physics, in this basis

The targets are compressions of log₁₀ D_ℓ, and in the log basis the leading
ΛCDM responses are additive by construction:

* **Amplitude sector.** C_ℓ ∝ A_s e^{−2τ} above the reionization regime, so
  log₁₀C_ℓ picks up (lnA_s − 2τ)·log₁₀e — *exactly* linear in the sampled
  basis (τ, ln10¹⁰A_s). This is why `logamp64` OLS reads the −2 directly and
  why F5.7 found e^{−2τ} 99.9%-linear even over the 13× τ range.
* **Tilt.** (n_s − 1)·ln(ℓ/ℓ*) per bin — linear in n_s at leading order.
* **Shape sector.** ω_b, ω_cdm, H0 vary ±9–13%; peak-height and
  acoustic-scale responses are smooth, with curvature entering at
  (Δθ/θ)² ~ 10⁻².
* **The genuine nonlinearities are localised**: the low-ℓ EE reionization
  bump (≈ A_s τ² physics, over the one fractionally-large range — τ spans
  13×); lensing smoothing (nonlinear in A_s, percent-level); oscillatory
  peak-shift structure (small); plus possibly the encoder's own warping (a
  network nonlinearity, not physics).

So log C_ℓ ≈ Σ_j θ_j t_j(ℓ) + small localised terms: **the ground truth is a
sum of parameter × spectral template, and near-affine latents are the correct
account of it, not a failed one.** Two design decisions follow and are
recorded: the **log target stays** (a linear-scale target would manufacture
curvature without adding information — each bin is a bijection of its log —
and break the parent-study anchor), and the **prior box stays** (the narrow
box is the regime real inference lives in; nothing in this framing requires
extending it, and rescaling was already shown to be a dead end — any smooth
reparametrisation is itself near-affine over a narrow box).

### 6.2 The deliverable becomes attribution

In an additive world the meaningful question is not "what formula is the
latent" but **which latent carries which physical component, with what
coefficients** — a three-way alignment: parameter direction w_k (the OLS
row) ↔ latent k ↔ spectral-template combination a_k (the decoder leg). The
robust instruments already deliver it: the role atlas (E2, five instruments
agreeing), the decoder-template decomposition (R²_W 0.988–1.000,
cos(a*, g) 0.77–1.00 — literally which ℓ-space components each latent
moves), the amplitude split (E3), and the −2 as the *coefficient of the
amplitude sum* (E1). Restated as findings: these latents are, to ~99.8%, six
parameter sums; identifiable curvature is confined mostly to the τ/EE-bump
sector. The internal consistency check is sharp — SR's genuine wins (EE z4;
the A_s e^{−2τ} organisation) sit exactly where the physics is nonlinear
*and* the box makes it identifiable. The method detects curvature where the
data contain it; its nulls elsewhere are the physics being flat.

**Trust scope for the discovered expressions, recorded** (tightened
2026-09-02). §2.5 proves the search is an incomplete, *biased* sampler of
its own hypothesis space, with demonstrated false negatives: the affine
optimum was representable at ms40, would have been retained and selected in
~39–43 of 55 runs had it appeared, and was absent from 38/55 fronts. Sort
every claim by what it needs from the search:

* **Existence plus out-of-search measurement — survives.** "Expression X
  scores this MI on rows the search never touched, recurs, passes level
  sets, and the same generator run on shuffled targets produces ≤ 0.07
  nat" — none of that requires the search to be a good optimizer. A weak
  generator can fail to find good expressions; it cannot make a found
  expression score well on held-out data, and the shuffled controls close
  the generator-artifact loophole. This is the proof-checker asymmetry:
  finding is hard, checking is easy, and trust attaches to the checked
  certificate, not the searcher. The possible error is one-sided — a
  missed better form means the latent is *more* structured than claimed,
  never less; verified performance is a lower bound.
* **Optimality and uniqueness — dead** (W1–W3): "this is *the* coordinate /
  the simplest form" required the space to have been surveyed; it
  demonstrably was not.
* **Inference from absence — dead.** "No simple form was returned, so none
  exists"; "the envelope is diffuse, so the information is spread over
  complexity"; "SR returned nonlinear forms, so the latent is nonlinear."
  The Pareto front's *shape* is a property of the generator, not the data;
  the invisible 25-node affine expression dominating 38/55 stored fronts
  is the constructive counterexample.
* **The recurrence caveat.** R_SR across five seeds shares one set of
  algorithmic biases — the same five seeds also *unanimously missed* the
  affine optimum, so unanimity certifies stability of this generator's
  output, not uniqueness of the answer. What upgrades a coordinate to
  trustworthy is agreement across instruments that do not share the bias,
  which the surviving claims have: SR derivative ratios (−1.974 ± 0.018 /
  −1.993 ± 0.008) vs exact-solver OLS coefficients (−1.9785 / −1.9967),
  the decoder templates, the raw-MI audit, and the quadratic pilot
  independently flagging the same two latents where SR wins.

This is not a post-hoc rescue: held-out MI selection, T2-only confirmation,
and shuffled controls were the pre-registered design — the OLS audit is
what proved that design was load-bearing.

### 6.3 The hybrid account, and the linear-mop-up suspicion

Suspicion (from discussion, untested): **the discovered stage-2 coordinates
may be substantially linear mop-up.** The two-stage accounts plateau at
h(f₁)+g(f₂) R²(μ) 0.955–0.998 — at or below the OLS level for 9/11 latents —
and several canonical f₂'s are near-linear composites over the box
(`n_s(H0+1311ω_cdm)`, `H0/ω_cdm²`). If stage 2 mostly recovers the affine
remainder a nonlinear f₁ missed, the f₂ forms' physical status is murky. The
clean per-latent question is: **does any identifiable coordinate exist beyond
the sum at all?** The hybrid account μ_k ≈ w·θ + (discovered residual
structure) concedes the affine part to the exact solver — answer-agnostic, so
blindness is preserved — and points discovery at only that question.
Expectation setting: the GBM probe already shows 97–99% of the OLS residual
is *predictable* for every latent, so beyond-affine structure exists
everywhere; what is open is whether it is low-order and compact
(interpretable candidate) or high-order/distributed (then it stays under
E4's "structure at every level").

### 6.4 Staged plan — cheap and coarse first (decided 2026-09-01)

1. **Step 1 — quadratic verdict, no SR.** Exact least squares with 6 linear
   + 21 second-order terms (+ intercept; 28 coefficients) in the sampled
   basis: fit on T0-fit, confirm on T2, paired-row CIs against the affine
   model, standardised coefficients reported. Three readouts per latent:
   does quadratic beat affine beyond CI noise; *which* second-order terms
   carry the gain (they name the responsible physics); how much of the
   beyond-affine gap closes at second order. Minutes, deterministic.
2. **Step 2 — proper SR, only where Step 1 leaves structure.** Blind SR on
   the exact OLS residual for flagged latents: 5 seeds, shuffled-residual
   controls, the frozen recurrence/clustering machinery — the existing
   stage-2 protocol with OLS as stage 1. Deliverable: a recurrent
   beyond-polynomial coordinate with nulls, or a recorded null.
   **Executed 2026-09-01 for EE z0 and EE z4 — results in §6.6.**
3. **Step 3 — atlas restatement.** Card rows become (w_k, template
   attribution a_k, quadratic verdict, beyond-affine coordinate where found,
   invariant ratios); discovered forms remain as compact annotations of
   directions per §6.2.

### 6.5 Step-1 pilot (run 2026-09-01)

Quadratic vs affine, both exact least squares on the 4,000 T0-fit rows in the
sampled basis (inputs standardised with T0-fit statistics), scored on all
25k T2 rows; Δ is quadratic − affine NMSE in percentage points with a
per-row paired 95% normal CI. The affine column reproduces the audit's
`logamp64` OLS values (0.0444 TT z2, 0.0402 TT z4, 0.0451 EE z5 …), so the
conventions match. **Pilot status: post-hoc, unregistered, deterministic
fits (no seed variance), T2 reused — promote via the audit's staging before
quoting as frozen.**

| Latent | affine % | quadratic % | Δ pp [95% CI] | gap closed | leading 2nd-order terms |
|---|---:|---:|---|---:|---|
| TT z0 | 0.186 | 0.012 | −0.174 [−0.179, −0.169] | 94% | ω_b·ω_cdm, ω_b² |
| TT z1 | 1.390 | 0.930 | −0.460 [−0.486, −0.433] | 33% | τ², H0² |
| TT z2 | 0.044 | 0.014 | −0.031 [−0.032, −0.030] | 69% | ω_cdm², ω_b² |
| TT z3 | 0.214 | 0.038 | −0.176 [−0.180, −0.173] | 82% | ω_b², ω_cdm² |
| TT z4 | 0.040 | 0.003 | −0.038 [−0.038, −0.037] | 94% | ω_cdm², H0² |
| EE z0 | 3.954 | 3.783 | −0.171 [−0.201, −0.141] | **4%** | H0², ω_b·H0 |
| EE z1 | 0.095 | 0.027 | −0.068 [−0.070, −0.066] | 72% | ω_cdm², H0² |
| EE z2 | 0.171 | 0.052 | −0.119 [−0.122, −0.116] | 70% | H0², τ² |
| EE z3 | 0.311 | 0.096 | −0.215 [−0.222, −0.209] | 69% | ω_b², ω_cdm² |
| EE z4 | 4.179 | 3.865 | −0.314 [−0.363, −0.264] | **8%** | ω_cdm·τ, H0·τ, ω_b·τ |
| EE z5 | 0.045 | 0.022 | −0.024 [−0.025, −0.023] | 52% | ω_b², ω_cdm·n_s |

Four readings:

1. **Identifiable second-order structure exists in all 11 latents** (every
   CI excludes zero), and its terms name the expected physics: shape-sector
   squares and crosses (peak-height curvature) dominate, with τ² appearing
   where the amplitude sector enters.
2. **The ladder's third rung is nearly empty except where SR already won.**
   For the nine "flat" latents, 21 extra exact coefficients close 33–94% of
   the beyond-affine gap. The two latents quadratic barely helps are exactly
   the two hard cases: **EE z4** (8%, its leading terms all τ-crosses — bump
   physics — yet the gain tiny, so the structure is beyond second order) and
   **EE z0** (4%, the unresolved card). These two are the Step-2 targets.
   (TT z1's large remainder is plausibly noise-limited — it has the study's
   lowest posterior SNR, 5.1.)
3. **After the quadratic rung, SR's reconstruction value narrows to EE z4
   alone**: quadratic beats the `mse40` medians essentially everywhere else
   (TT z0 0.012 vs 0.398; TT z2 0.014 vs 1.195; EE z3 0.096 vs 0.209; EE z5
   0.022 vs 0.415), while at EE z4 SR still wins (calibrated MI-SR ≈ 1.4 /
   `mse40` 2.66 vs quadratic 3.87). EE z4's status as the one genuinely
   non-polynomial latent is thereby *strengthened*, not weakened.
4. **The attribution framing gains an instrument**: the quadratic
   coefficients are themselves interpretable attribution (which parameter
   pairs interact per latent) at zero search cost — a natural card column
   for Step 3.

### 6.6 Step 2 — blind SR on the exact OLS residual (run 2026-09-01)

Executed on the Lightning studio (14 sequential tasks, ~8.7 h wall on 4
cores ≈ 35 core-h): the frozen stage-2 protocol (gmm_mi inner loss, 6 raw
inputs, 5000 T0 samples, ni200/pop15/ms20, seeds 0–4) against the exact
OLS-stage-1 residual of §6.4's caches, plus two shuffled-residual controls
per latent (`run_shuffled_control.py --target-npy`, protocol-identical).
Caches were built independently on CSD3 and the studio with byte-identical
sha256. Artifacts: `results/lcdm_tt_ee_lowl/residual_sr_ols/` (reports,
driver log, `analysis_summary.json`), generator
`scripts/build_ols_residual_cache.py` + provenance
`models/lcdm_tt_ee_lowl/analysis/residual_ols_v1_fit.json`, driver
`hpc/lightning/run_residual_sr_ols.sh`, analysis
`scripts/analyze_residual_sr_ols.py`.

| | EE z0 | EE z4 |
|---|---|---|
| per-seed best MI vs residual [nat] | 0.498–0.541 | 0.771–0.891 |
| shuffled-residual null MI | 0.066–0.072 | 0.051–0.056 |
| R_SR (frozen §0.3 rule) | 0.80 (cluster 4+1) | **1.00** |
| representative (complexity) | `(ω_cdm/(ω_b·(H0−85.5)))²` (8) | **`A_s/τ`** (3) |
| support | {ω_b, ω_cdm, H0} | {τ, A_s} |
| \|Spearman\| vs Phase-6 f₂ | 0.58 — *different direction* | 0.986 — *same equivalence class* |
| hybrid T2 NMSE, frozen monotone q | 3.750% | 2.407% |
| hybrid T2 NMSE, free 1-D q (diagnostic) | **1.834%** | **1.304%** |
| 1-D any-function probe R² (T1 halves) | 0.54 | 0.69 |
| ladder context (affine → quadratic) | 3.954% → 3.783% | 4.179% → 3.865% |

Five readings:

1. **Both flagged latents carry a real, recurrent beyond-affine
   coordinate**: discovered MI sits 7–14× above the shuffled-residual
   nulls, and the nulls reproduce the Phase-6 control band (≤ 0.074 nat).
2. **EE z4: the compact answer.** All five seeds land in one cluster whose
   minimal member is `A_s/τ` at complexity 3 — the reionization-bump
   amplitude-to-depth direction, and statistically the *same* class as the
   old f₂ = τ (ρ 0.986): z4's original stage-2 was already on the true
   beyond-affine direction; nothing there was mop-up. The hybrid
   (7 OLS coefficients + a 3-node ratio + one 1-D map) reaches 2.407%
   under the frozen monotone convention — already beating `mse40` (2.66%)
   — and 1.304% with a free 1-D map, **the best account of z4 ever
   measured** (prior best: calibrated MI-SR ≈ 1.38%; quadratic wall
   3.87%).
3. **EE z0: the mop-up verdict and the non-monotonicity finding.** The
   recurrent coordinate is A_s-free shape-sector curvature,
   `(ω_cdm/(ω_b·(H0−c)))²` with the fitted pole c ≈ 85–91 just outside
   the H0 prior box — a rational structure no quadratic in θ expresses
   (Step 1 closed only 4% here). It is *not* the old f₂ (ρ 0.58): z0's
   Phase-6 coordinate was substantially linear mop-up, confirming §6.3
   for this latent. And its relation to the residual is **strongly
   non-monotone**: the frozen monotone calibrator converts 0.5 nat of MI
   into only 5% of the residual, while a free 1-D map converts it into
   54% (3.954% → 1.834%, probe R² 0.54 — consistent with the
   Gaussian-equivalent bound of 0.5 nat). This mechanically explains why
   every earlier monotone-calibrated account of z0 stalled, and halves
   the previous best reconstruction of the study's one unresolved card.
   Interpretive note: the coordinate's core ratio is close to z0's own
   f₁ = ω_cdm/(H0·n_s·ω_b) — the residual looks like curvature along the
   latent's own primary direction, consistent with the interaction-aware
   finding (f₂ ∝ an f1hat interaction).
4. **The §6.3 suspicion resolves with a split verdict**: mop-up real at
   z0, absent at z4 — the hybrid basis is what separates the two cases.
5. **Scope**: no card status changes (the frozen card instruments were not
   rerun); the free-map numbers are diagnostics *outside* the frozen
   monotone convention and are labelled as such; T2 reuse is post-hoc as
   everywhere in §2–§6. Natural next legs if promoted to frozen
   deliverables: joint level sets for the pairs (OLS index, f₂_new), and
   a second residual round at z0 (1.83% remains structured — the
   multi-coordinate diagnosis of the closure stands).

---

## 7. Open items before any write-up freeze

1. **Staged nonlinearity ladder (§6.4) — Steps 1 and 2 both run.** The
   quadratic pilot (§6.5) and the Step-2 hybrid campaign (§6.6) are
   complete: real second-order structure in all 11 latents; EE z4/EE z0
   confirmed beyond-polynomial and now both characterised (unanimous
   `A_s/τ` at z4; recurrent non-monotone shape-sector curvature at z0).
   Remaining: promote both to frozen deliverables under the audit's
   staging; joint level sets for the (OLS index, f₂_new) pairs; a second
   residual round at z0.
2. **η̂_post for the OLS index** — MI(Z_k; w·θ) on T2. Cheap, and decisive for
   every "fraction of what the latent stores" statement: if OLS beats
   f₁+f₂ on η̂_post for most latents, W2/W4 harden into table rows.
3. **Level-set audit of the OLS index** — turn the §2.4 prediction into a
   measurement (the machinery exists; one consolidator pass).
4. **OLS-injection diagnostic — selection level now done** (result in §2.5:
   retained 43/55, wins selection 39/55; front retention and selection are
   *not* the failure modes). Remaining: separate candidate-discovery failure
   from constant-fitting failure (e.g. seed the search population with the
   affine scaffold, or hand PySR the affine tree and let only its constants
   be optimised), and, if wanted as a frozen deliverable, the staged
   calibrate/confirm legs. No new search campaign needed for the first part.
5. **Consolidate and commit.** The campaign's own deliverable
   (`docs/precision_preprocess_v1_comparison.md`,
   `experiments/precision_preprocess_v1_comparison.json`) was recovered from
   the Lightning studio to CSD3 on 2026-09-01, closing that gap; the campaign
   + audit + Step-2 code, tests, and these docs remain uncommitted. Freeze
   them before further analysis.
6. **Pre-existing opens, unchanged**: EE z0 three-coordinate account; R_model
   (Phase 9, GPU, parent repo); the hierarchy's third level (recorded, not
   pursued).
7. **Beyond this box.** The near-affinity that powers OLS is prior-box-local,
   so three tests could still change the verdict's *scope* (not its on-box
   content): a wider-prior campaign, where Taylor linearisation degrades; a
   preregistered OLS vs nonlinear-baseline vs SR comparison evaluated once on
   genuinely fresh simulations (every current comparison, the matched audit
   included, is post-hoc on already-inspected T2 rows); and a matched
   description-length / interpretability comparison — OLS is itself compact
   and readable, and SR's incremental interpretability advantage has never
   been quantified here. **Decision (2026-09-01): the wider-prior campaign is
   parked** — under the §6 framing the box stays, and near-affinity is read
   as physics, not artifact. The fresh-simulation confirmation and the
   description-length comparison remain relevant regardless.
8. **Framing decision for the paper.** Two defensible shapes: (a) a
   discovery-plus-audit paper — "blind SR interpretation of a scientific VAE,
   with the control programme that determines which of its outputs survive a
   linear baseline" (the crossed/negative results and E6 become central,
   EE z4 and the amplitude-basis story are the SR exhibits); or (b) a
   methods paper centred on the pipeline and its honesty machinery, with the
   atlas as the worked example. The current `report.md` §1–10 and compendium
   §9 menu predate affine parity and would over-claim if published as-is;
   whichever shape is chosen, §2 of this file needs to be in it. **Working
   direction (2026-09-01): the §6 attribution framing** — which latent
   carries which physical component, plus where genuinely beyond-polynomial
   curvature lives — i.e. shape (a) with the additive-physics reading as its
   spine and the affine→quadratic→SR ladder as the identifiability
   instrument.
9. **PySR v2.0.0 (assessed 2026-09-02, from the release notes).** Unusually
   relevant to the measured failure modes — as a *new registered arm*,
   never a drop-in:
   * `guesses` (initial expressions mixed into populations, constants
     optimized on entry, `fraction_replaced_guesses`) implements item 4's
     remaining diagnostic natively: seed the exact OLS expression per
     latent and watch whether evolution keeps, improves, or degrades it.
   * `BacksolveMutation` (backsolves what a subtree should return, fits
     replacements by forward selection) plus the new defaults —
     crossover probability up 8× (0.026 → 0.2), annealing and adaptive
     mutation weights on — target exactly §2.5's generative failure:
     assembling multi-term sums is a recombination/backsolve job that
     point-mutation lineages demonstrably could not do.
   * `TemplateExpressionSpec` (now the sole structured spec) can express
     the §6.3 hybrid natively: a fitted affine scaffold plus a free
     searched part, as one search object.
   * Variable-arity operators (`muladd`/`fma`) change the node
     accounting: a dense 6-input affine map drops to ≈19 nodes — inside
     ms20 — so §2.3's budget arithmetic must be redone for any v2 arm.
   * ~5× faster on this workload shape (benchmarks: 20k×5 63.9 → 12.7 s;
     evaluation arena −38%; startup 43 → 17 s), with auto-minibatching
     now default above 1000 rows.
   Constraints: the frozen record stays on pinned `pysr==1.5.10` — v2
   cannot load v1 checkpoints, changed defaults silently (annealing,
   crossover, batching), and the pure-Julia GMM-MI `loss_function` must be
   ported and re-validated against SymbolicRegression.jl 2.0 before any
   MI arm runs. And no engine upgrade changes the identifiability physics
   (§6.1): v2 can only shrink *search error* (false negatives), not make
   affine-degenerate forms distinguishable. Priority if pursued:
   (a) guesses-seeded MSE arm (cheap; settles item 4's
   discovery-vs-constant-tuning split), (b) template-hybrid arm,
   (c) v2 rerun of the two §6.6 latents as robustness.

---

## 8. Pointers

Frozen rules and closure: `docs/discovery_roadmap.md` (§0.3, Closure, R-P4
registration+outcome) · full digest to 08-14: `docs/results_compendium.md` ·
per-latent synthesis: `experiments/latent_cards_*` · MSE follow-up:
`docs/mse_one_stage_results.md` (+ plan and provenance JSON) · precision/
preprocessing arms: `src/cmb_lcdm_sr/sr.py` `INPUT_CONFIGS`,
`hpc/slurm_precision_preprocess_v1.sh` (330-task matrix),
`scripts/run_precision_preprocess_pool.py` · the audit:
`scripts/audit_coordinate_matched_ols.py`,
`experiments/coordinate_matched_ols_v1.{json,md}`,
`results/<run>/coordinate_matched_ols_v1/<arm>/{fit,calibration,confirmation}.json`
· discussion record (what SR was for; verified repo status; the eight
questions of 2026-09-02): `docs/sr_objective_discussion_2026-09-02.md`
· write-up state: `report.md`, `paper/main.tex`, `docs/report_content.md`
· original three-way snapshot: `docs/ols_mi_sr_mse_sr_t2_comparison.md.orig`
(embedded verbatim in `docs/ols_mi_sr_mse_sr_t2_comparison_codex_output.md`,
the decision-checkpoint companion to this file) · §2.5 mechanism diagnostics:
the `ols_baseline.{coefs,mse_val}`, `best_mse_val`, and
`all_equations[].mse_fit_eval` fields of
`results/*/mse_one_stage_ms40/*/report.json`, replayed with
`data/theta.npy` + `data/splits_v1.npz` (test split) and
`models/*/analysis/encoder_means_test.npy` under each report's stored
`y_mean_train`/`y_std_train` standardisation.
