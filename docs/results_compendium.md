# Results compendium — blind symbolic discovery in CMB β-VAE latents

*Assembled 2026-08-09 at project wrap-up. This is the single-source digest of
every result in the repository, written as raw material for the official
write-up: each number traces to a consolidated deliverable in `experiments/`
(named inline), none is new analysis. Sections 2–5 are the headline results;
§6 is the complete layer-by-layer record; §7 collects every control; §9 is a
ranked menu of candidate claims with their evidence chains and caveats.*

**Numbers at a glance.** 2 stored β-VAE checkpoints (TT-only `PirasCVAE`
L=5; TT+EE-lowl `DualEncoderCVAE` L=6; both β=3e-4, training seed 42) ·
11 latents · one frozen search protocol (PySR, pure-Julia GMM-MI inner loss,
5000 samples, ni200/pop15/ms20, 5 seeds per config) · ≈2,000 PySR searches
≈1,800 core-h (icelake) · 12 consolidated experiment deliverables + latent
cards · final statuses **10/11 "primarily interpreted", 1 unresolved** ·
all claims **per-checkpoint** (VAE-seed stability untested).

---

## 1. Setup (what was run, and what "blind" means)

* **Data**: 500k LHS ΛCDM samples θ = (ω_b, ω_cdm, H0, τ, ln10¹⁰A_s, n_s)
  → CLASS spectra → the two stored compressors (from the parent `cmbvae`
  reproduction of Piras, Herold, Lucie-Smith & Komatsu 2025,
  arXiv:2502.09810). SR targets the encoder posterior mean μ_k over the 50k
  test rows; the stochastic latent Z_k (via cached logvars) gives the
  intrinsic ceiling.
* **Blindness**: inputs are raw parameters only; the inner loss (fixed-K=2
  pure-Julia GMM-MI, ~80× faster than the PythonCall route) and the post-hoc
  selection metric (full `gmm-mi` on held-out rows) share one invariance
  class — any bijection of either variable — so the search is rewarded for
  functional dependence, never calibration. No derived combination
  (`A_s·e⁻²ᵗ` or otherwise) is computed anywhere in the pipeline.
* **Data hygiene**: T0 = test[0:5000) (SR fit+val), T1 = [5000:25000)
  (calibration, anchors, audits), T2 = [25000:50000) (confirmatory numbers
  only) — `src/cmb_lcdm_sr/tiers.py`.
* **Pre-registration**: every decision rule (sufficiency levels, knee,
  cluster equivalence, recurrence, subset minimality, residual pass,
  level-set pass, status predicates) frozen in `docs/discovery_roadmap.md`
  §0.3 *before* any shape-latent unblinding; instruments validated on the
  amplitude sector first (gate G1); post-freeze judgement calls recorded in
  a deviations register (D-P2a/b, R-P5, D-LS, D-DoD-z2, N-G2 flags).

---

## 2. Headline 1 — the −2 reionization exponent, recovered blindly, three ways

The textbook TT amplitude combination is `ln(A_s·e^{−2τ})`. Independent
blind readouts of the −2 (all encoder-side; the observable-domain attempt is
row 4, which does **not** yield a readout):

| # | Readout | Instrument | Value | Source |
|---|---|---|---|---|
| 1 | The discovered forms themselves | 2-input blind SR, (A_s, τ) → amplitude latent | TT: `A_s·(τ−0.598)` in 5/5 seeds; EE: `A_s·(τ−0.579)` + **literal `A_s·e⁻²ᵗ`** (seed 3). Affine constants match the Taylor prediction c = τ̄ + ½ ≈ 0.570 to 1.5–5% | `docs/method.md` §3 |
| 2 | Derivative ratio r = (∂f/∂τ)/(∂f/∂lnA_s) over all-params top forms | 6-input blind SR, every latent | **−1.974 ± 0.018** (TT) / **−1.993 ± 0.008** (EE) | `experiments/allparams_blind_sr_*` |
| 3 | Constant-ratio detector (answer-agnostic, frozen) | Phase-3 ratio field ρ_ij = (∂f/∂u_i)/(∂f/∂u_j), cv < 5% | (τ, lnA_s) pair emerges with **r_raw = −2.000** on the cards (TT z4 f₁, EE z5 f₁); G1 knee-slice latent-level r_lin = −1.977 (TT) vs stored −1.988 | `experiments/sufficiency_audit_*`, `latent_cards_*` |
| — | Observable domain: decoder effect decomposed onto data-driven parameter templates | Phase 7b, d_k(ℓ) ≈ Σ a_j t_j(ℓ) | **No readout.** The (τ, lnA_s) templates are near-antiparallel in both designs (uncentered cos −0.9902 EE / −0.9996 TT; cond 14.2 / 70.2), so the fitted split — and hence r_dec — drifts freely along the degenerate ridge. EE's r_dec = −1.87 is one point on that ridge (−1.67 to −2.32 across fit variants); TT gives +0.351. G4b FAILS on both. Only proj_brk and the shape-sector coefficients are identifiable | `experiments/decoder_effect_*` |

**Bonus fourth appearance**: the EE H0-latent's *residual* coordinate is
literally `A_s·exp(−2τ)/ω_b²` with ratio −2.0000 — found blindly in Phase 6
and found *again* by the independent interaction-aware rerun (§6.12).

Supporting structure:
* Regex scan over all Pareto-front equations (reference study): textbook
  direction in 28/78 (TT) and 37/78 (EE) equations; the literal exponential
  appears only in EE — and that is *structural*, not seed luck: over the
  prior τ ∈ [0.01, 0.13], `exp(−2τ)` is 99.90% linear (max dev 0.52%), the
  affine form ties its MI, and parsimony deterministically prefers it
  (`method.md` §3e).
* Both regimes matter: TT is the degeneracy *present* arm (the latent is
  forced into the combination); EE is the degeneracy *broken* arm (the model
  could separate A_s and τ, yet the amplitude latent still organises as
  `A_s·e⁻²ᵗ`) — the agreement of the two arms is the result (`method.md`
  §2, §4).

---

## 3. Headline 2 — a validated card for every latent (the discovery study)

Final statuses under the frozen predicates (`experiments/latent_cards_*`):

**TT-only (`lcdm_tt_beta3e-4`, 5 latents)**

| z | role (audit-expected) | f₁ (canonical, blind) | η_S | η̂_post f₁ | η̂_post f₁+f₂ | R_SR | status |
|---|---|---|---:|---:|---:|---:|---|
| 0 | ω_b | `n_s/omega_b` | 1.003 | 0.531 | 0.903 | 1.00 | primarily interpreted |
| 1 | ω_cdm | `H0²·n_s²·ω_b/(A_s·ω_cdm²)` | 1.000 | 0.770 | 0.957 | 0.80 | primarily interpreted |
| 2 | amplitude (A_s, τ) | `A_s/log(H0·(ω_cdm+τ))` | 1.000 | 0.347 | 0.601 | 1.00 | primarily interpreted |
| 3 | n_s | `n_s + ω_cdm` | 0.997 | 0.447 | 0.838 | 1.00 | primarily interpreted |
| 4 | H0 | `A_s·H0²·ω_cdm·e^{−2τ}` | 1.000 | 0.371 | 0.758 | 0.80 | primarily interpreted |

**TT+EE-lowl (`lcdm_tt_ee_lowl`, 6 latents)**

| z | role | f₁ | η_S | η̂_post f₁ | η̂_post f₁+f₂ | R_SR | status |
|---|---|---|---:|---:|---:|---:|---|
| 0 | ω_cdm / early-ISW | `ω_cdm/(H0·n_s·ω_b)` | 1.000 | 0.756 | 0.842 | 1.00 | **unresolved** |
| 1 | H0 | `H0²·ω_cdm` | 1.000 | 0.348 | 0.663 | 1.00 | primarily interpreted |
| 2 | ω_b | `ω_b/n_s²` | 0.995 | 0.574 | 0.963 | 1.00 | primarily interpreted |
| 3 | n_s | `log(ω_b)/(n_s+ω_cdm)` | 0.992 | 0.493 | 0.864 | 0.80 | primarily interpreted |
| 4 | τ (amplitude sector) | `−A_s/(τ−0.445)` | 1.068 | 0.842 | 0.842 | 1.00 | primarily interpreted |
| 5 | amplitude (A_s, τ) | `A_s·e^{−2τ}` | 1.000 | 0.289 | 0.590 | 1.00 | primarily interpreted |

What the statuses mean, in claims:

* Every latent has a **1-D symbolic primary coordinate that saturates its
  own support** (η_S 0.99–1.07 vs the blind 63-subset ceilings) and recurs
  across search seeds (R_SR ≥ 0.8 everywhere, 8/11 at 1.00 on the cards).
* **Every stage-1 residual is structured** (R²_res 0.96–0.994 against
  permutation nulls ≈ 0) — the deterministic encoder map carries more than
  one symbolic level. Phase 6 gives each latent a *discovered* second
  coordinate f₂ (R_SR 0.80), lifting the intrinsic-information fraction
  η̂_post to 0.59–0.96.
* **No latent reaches full "interpreted"**: stage-2 residuals are still
  structured (combined R²(μ) 0.954–0.998, yet the frozen audit fails for
  all 11) — the encoder hierarchy does not terminate at two symbolic
  levels. Confirmed robust to the interaction-aware ansatz (§6.12).
* **EE z0 is the honest failure**: weakest stage-2 account (R² 0.39–0.41),
  joint level sets at E_inv 0.060–0.062 vs the frozen 0.05 (inside its
  predicted band). The blocker is localised: its residual holds more than
  one coordinate's worth of structure.

---

## 4. Headline 3 — structural facts about the codes

* **The degeneracy-breaking fingerprint is blind and model-level**: the raw
  disentanglement audit (MI to raw parameters only) shows **one**
  amplitude-sector latent in TT and **two** in TT+EE — visible before any
  SR runs (`method.md` §1).
* **The EE amplitude sector is split, not duplicated** (Phase 8): z4's
  τ-direction is carried by z4 essentially alone (carrier set A* = {z2, z4},
  own-latent probe R² 0.946), and no redundant latent pair exists in either
  model — every top-2 carrier conditional is synergistic. Conditioning on
  z5 raises z1's information about `A_s·e⁻²ᵗ` from 0.013 to 0.473 nat
  (`experiments/subspace_probe_*`).
* **Coordinates are latent-anchored but the tails are distributed**: every
  canonical f₁ is linearly decodable from its own latent at rank-normal
  R² 0.88–0.95, with the remainder spread across the code (axis-aligned =
  False for all 11); residual coordinates f₂ are genuinely distributed
  (own-latent R² 0.01–0.58).
* **The mean map outruns the channel**: the deterministic μ_k(θ) carries
  detail the sampled latent cannot transmit (residual variance up to 382×
  the posterior noise; Phase 5) — high-capacity SR keeps finding MI in μ_k
  far above the finite I(Z_k; θ).

---

## 5. Headline 4 — the methodology (reusable beyond this project)

The pipeline is a worked example of **pre-registered, answer-agnostic VAE
interpretation** with falsifiable gates:

1. **Freeze → validate on positive control → unblind.** All thresholds in
   §0.3 before shape-latent unblinding; G1 required the machinery to
   *rediscover* {A_s, τ}, the −2, η_S ≈ 1 — and to *fail* the residual
   audit in the expected structured direction (an honesty check: the
   instruments must not fabricate sufficiency). G1 PASS on both models.
2. **Gates ledger**: G0 PASS · G1 PASS (both models) · G2 8/11 PASS +
   3 ATTENTION (S* not screen-recurrent: TT z0, EE z3, EE z4; amplitude =
   "PASS (superset finding)") · G3 PASS (DPI holds; residuals are real
   stored information) · G4a f₁-only FAIL everywhere — *by design
   informative* (§6.9) — G4a-joint PASS on EE, TT undefined-by-support ·
   **G4b FAIL on both models** by the same mechanism (collinear (τ, lnA_s)
   templates make the amplitude split unidentifiable): TT mass 0.64 /
   r_dec +0.351, EE mass 0.79 / r_dec −1.873; R²_W bullet passes on both.
3. **The η ladder** separates claims that are otherwise conflated:
   η_S (does f saturate its own variables?) vs η_plat (fraction of the
   SR-accessible mean map) vs η_post (fraction of what the latent
   *physically stores*). A latent can honestly score η_S = 1.00 and
   η_plat = 0.35 — that distinction is what makes "primarily interpreted"
   a precise status.
4. **Semantic recurrence, not string pooling**: three frozen equivalence
   tests (canonical sympy ∨ |Spearman| ≥ 0.98 on anchors ∨ gradient-cosine
   ≤ 0.05) + union-find with anti-chaining cohesion diagnostics.
5. **Deviations register** instead of silent judgement: D-P2a (R_SR seed
   tolerance = cross-seed SD), D-P2b (representative majority guard), R-P5
   (η̂_post as demotion metric, decided on synthetic control), D-LS (joint
   level-set leg), D-DoD-z2 (additive-hierarchy limit) — each on the cards.
6. **Every instrument ships its null** (§7).

---

## 6. Complete layer-by-layer record

### 6.1 Reference-study reproduction (2 inputs → amplitude latent)

5 seeds × 2 regimes, protocol above. TT: top form `A_s·(τ−0.598)` in 5/5
seeds, val MI 0.8216 ± 0.0000-level across seeds (cross-seed 0.822 ± 0.025);
EE: `A_s·(τ−0.579)`-family top, literal `A_s·e⁻²ᵗ` at seed 3, val MI
1.196 ± 0.001. Textbook-direction regex hits 28/78 (TT) and 37/78 (EE)
front equations. Latent choice is itself blind (raw-parameter MI audit
only). Source: `docs/method.md` §1–§4, `experiments/` reference tables.

### 6.2 All-params blind SR (6 inputs → all 11 latents)

No input or latent pre-selection. Every latent is a multi-parameter
composite (top forms use ≥5 of 6 parameters); cross-seed top MI 2.3–3.8 nat
(TT) / 1.8–3.8 nat (TT+EE) — far above the 2-input ceilings (0.822/1.196)
because nothing is marginalised out. The −2 survives full blindness (r =
−1.974 ± 0.018 / −1.993 ± 0.008 over all top forms). Sources:
`experiments/allparams_blind_sr_*` (+ `_ms10` variants).

### 6.3 Hyperparameter sweep `hp_v1` (12 configs × 3 seeds × 2 models)

* **Top val MI is a capacity dial, not a discovery meter**: maxsize alone
  swings it 1.6 → 4.05 nat; every capacity knob raises it; the winning
  forms are complexity-20 composites that differ structurally seed-to-seed.
* **The budget-matched readout MI@c≤10 is flat across every knob**
  (~1.89 TT / ~2.02 EE): the leading-order discovery is saturated at
  protocol settings — no tuning gain exists on the aim-aligned metric.
* **Search big, then slice**: the maxsize-10 search's own front is *worse*
  at c≤10 than the sliced maxsize-20 front (1.60 vs 1.89 TT; 1.69 vs 2.02
  EE) — parsimony is a report-time slice, not a search-time budget.
* **Physics is hyperparameter-robust**: r ≈ −1.97…−2.00 in every config.
* **Cost**: `ncycles_per_iteration 190` matches baseline at ~60% runtime;
  `population_size 108` is ~4× cost past diminishing returns.
Sources: `experiments/hpsweep_hp_v1_*`.

### 6.4 Phase 1–2 — plateaus, knees, semantic recurrence

Cumulative Pareto envelopes per latent: plateaus (ms30, 3 seeds) 2.52–4.31
nat (TT) and 1.79–4.18 nat (EE); one-SE knees c* = 18–29; envelope shape
"no knee (diffuse)" for 10/11 (EE z2 shows knee + slow climb) — the
front information is spread over complexity, another face of the
non-terminating hierarchy. Semantic clustering: one dominant cluster per
latent, R_SR ≥ 0.8 for all 11 (8/11 at 1.00 on the cards); the amplitude
clusters contain the textbook family with R_SR 1.0, the EE representative
literally `A_s*exp(-2*tau)`. Sources: `experiments/knee_readout_*`,
`semantic_recurrence_*`.

### 6.5 Phase 3 — signatures + calibrated sufficiency (gate G1)

Sensitivity signatures g_j and Sobol indices per canonical form;
constant-ratio pairs as the answer-agnostic exponent detector (§2 row 3).
Calibrated sufficiency: after 5-fold cross-fitted monotone recalibration,
stage-1 residuals are structured for **all 11** latents (R²_res 0.981–0.994
TT, 0.960–0.994 EE; permutation nulls ≈ −0.002/0.001), with full-sector
loadings. G1 (amplitude positive control) PASS on both models: knee-slice
support {τ, lnA_s}, η_S = 1.000 vs the reference ceiling, r recovered,
residual fails in the expected structured direction. η_plat of the
canonical TT forms at the knee slice: 0.30–0.48. Sources:
`experiments/sufficiency_audit_*`.

### 6.6 Phase 4 — blind subset selection (the 63-subset campaign)

All 2⁶−1 = 63 supports × 2 screen seeds × 11 latents (ni100 screen, ms20),
finalists rerun at full protocol: S* per latent with support-restricted
ceilings Î_S. Headline: the amplitude latents return S* = all-6 as a
reproducible **superset finding** — the all-parameter ceiling beats
{A_s, τ} by more than 1 SE because the shape-sector modulation is real
information (G2 "PASS (superset finding)"). Minimal supports elsewhere
range |S| = 3 (EE z4: {ω_b, τ, A_s}) to 6. Three latents carry N-G2
attention flags (S* not screen-recurrent: TT z0, EE z3, EE z4) — all
three dispositioned by the post-closure exhaustive full-protocol grid
(§6.13). Sources: `experiments/subset_selection_*` (staircase tables per
latent).

### 6.7 Phase 5 — the intrinsic ceiling I(Z_k; θ)

Finite ceilings from the stochastic latent: I = 0.92–4.30 nat (TT),
1.34–4.18 nat (EE); posterior SNR spans 5.1 (TT z1) to 5,491 (TT z2) —
amplitude posteriors are near-deterministic, so their structured residuals
are *real stored information*, not sub-noise detail (the G3 fork's
informative branch; DPI sanity holds for all candidates). Canonical forms
store η̂_post = 0.29–0.84 of what each latent knows (registered refinement
R-P5: η̂_post = MI(Z;f)/MI(Z;μ) is the demotion metric). Sources:
`experiments/posterior_ceiling_*`.

### 6.8 Phase 6 — second-stage discovery on the residuals

Blind SR on cached residuals e₁ = μ − h(f₁), all-6 inputs, 5 seeds:
recurrent f₂ for all 11 (R_SR 0.80; MI vs e₁ 0.40–1.77 nat vs
shuffled-residual nulls ≤ 0.074). Combined accounts h(f₁) + g(f₂) reach
R²(μ) 0.955–0.998; η̂_post 0.59–0.96. Amplitude DoD (f₂ pure shape-sector)
**MET on EE** (f₂ = `H0·ω_cdm/n_s`) and **NOT MET on TT** — recorded as
D-DoD-z2: the TT knee forms are A_s·(τ−c) × shape, and an additive
hierarchy cannot absorb a multiplicative interaction (τ-clamping the TT f₂
costs 0.20 nat). Stage-2 residuals fail the frozen audit for all 11.
Sources: `experiments/residual_sr_*`.

### 6.9 Phase 7a — level-set invariance (the interventional test)

f₁-only: E_inv FAILS the 0.05 rule for all 11 — and the failure is
*quantitatively the structured residual*: E_inv/(1−R²_cal) ∈ [1.1, 2.6]
across all 11 latents (6 inside the predicted band [1−R², 2(1−R²)], 5
above its factor-2 cap at the extreme-separation pairs the audit
deliberately draws; distance curves rise monotonically). Audit and
calibration agree about what moves within level sets.

Joint (f₁, f₂): invariance is restored — 7 of 8 auditable latents pass
(EE amplitude z5: 0.226 → 0.029; **gate G4a-joint PASS on EE**,
T2-confirmed); the three TT latents whose union support is all 6 have no
nuisance direction left (D-LS; response legs 0.98–0.99). EE z0 is the one
joint FAIL (0.060, in-band). Matched-nuisance responses are 1-D at spline
R² 0.91–1.00 throughout. Sources: `experiments/levelset_audit_*`,
`levelset_audit_joint_*`.

### 6.10 Phase 7b — decoder-effect triangulation (observable domain)

d_k(ℓ) = ∂Decoder/∂z_k decomposes onto data-driven parameter templates
t_j(ℓ) at R²_W 0.988–1.000; cos(a*, g_j) between the decoder-side loading
and the symbolic signature = 0.77–1.00 across the 11 latents — the stage's
solid result: the decoder's observable effect and the symbolic coordinate
agree about which parameters each latent moves.

**The amplitude split is not identifiable, and G4b FAILS on both models.**
The (τ, lnA_s) templates are near-antiparallel (uncentered cos −0.9902 EE
concat / −0.9996 TT; cond 14.2 / 70.2): moving θ along the degenerate
direction (δτ, δlnA_s) ∝ (1, 2) leaves these spectra invisible, so the
fitted (a_τ, a_lnAs) split — hence r_dec and amplitude mass — slides freely
along that ridge at no cost to R². The deliverables report r_dec and
proj_deg "for completeness, not as claims". Frozen bullets: amplitude mass
0.64 (TT) / 0.79 (EE) vs ≥0.8 — FAIL both; |r_dec+2| ≤ 0.3 — TT +0.351 FAIL,
EE −1.873 nominally PASS but unidentifiable (−1.87 OLS / −1.67 (2ℓ+1)-weighted
/ −1.77 h/2 templates / −2.32 anchor point); R²_W PASS both. Identifiable
statements: the shape-sector coefficients and proj_brk, the projection on the
degeneracy-breaking direction (−2, 1)/√5 (EE z5: 0.047, stable across
variants). Sources: `experiments/decoder_effect_*` (+ curve PNGs/NPZs).

### 6.11 Phase 8 — subspace & redundancy

Cross-validated sparse probes + slab-conditional MI: own-latent
decodability R² 0.88–0.95 for every f₁ (own latent always in the 1-SE
carrier set); **no redundant pair in either model** (all top-2 carrier
conditionals synergistic); EE amplitude split as in §4; f₂ coordinates
distributed (own R² 0.01–0.58). Shuffled-probe null R² ≈ 0.000. Sources:
`experiments/subspace_probe_*`.

### 6.12 Post-closure — interaction-aware stage 2 (2026-08-09)

The Closure's open-item 3, executed: Phase-6 rerun with the stage-1
prediction f1hat = h(f₁) exposed as a 7th input (55 runs + 6 controls,
98 core-h; f1hat composite reconstructed exactly — T2 error 0). Three
verdicts:

1. **D-DoD-z2 is real structure, not an ansatz artifact**: TT z2's
   recurrent knee coordinate is the *same* τ-bearing form as the additive
   run (f1hat unused; DoD-ia NOT MET) even though the search demonstrably
   used f1hat elsewhere.
2. **EE z0 upgrades but stays unresolved**: f₂ becomes the *unanimous*
   interaction form `−A_s·H0²·(f1hat − 10.87)` (R_SR 1.00 vs 0.80; MI vs
   e₁ 0.40 → 0.50), yet joint E_inv stays at 0.062 ± 0.002 (T2 0.067; band
   [0.046, 0.093]) — the stage-2 residual (R² 0.39) needs a third
   coordinate.
3. **The additive account is robust**: 8/11 latents return the identical
   canonical f₂ under the enriched space; EE amplitude DoD still MET; EE
   z1's residual is again literally `A_s·e⁻²ᵗ/ω_b²` (ratio −2.0000).
   Where interactions are real the machinery sees them: TT z4's cluster
   carries the f1hat forms (residual MI 2.40 vs 2.16 additive plateau;
   η̂_comb 0.758 → 0.787), TT z3 reaches R_SR 1.00.

No card status changes. Sources: `experiments/residual_sr_ia_*`,
`levelset_audit_joint_ia_*`.

### 6.13 Post-closure — R-P4, exhaustive support at full protocol (2026-08-14)

Phase 4 screened all 63 supports with a *capacity* readout (front-max
Î_S) and promoted only finalists to protocol; R-P4 ran the **complete**
63-support × 5-seed grid at the study protocol for every latent (3,465
cells; 2,425 fresh runs, 1,040 reused with verified protocol match;
≈5,800 core-h measured) and read it with the pre-registered
budget-matched M_S^(c≤10), two-stage: select S⁺ on T0-val over the 62
strict subsets, confirm S⁺ − all-6 paired on T2 (> +1 SE), plus a
sham-input control (the all-6 search rerun with a permuted real θ column
— a genuine parameter's marginal, provably zero information). Rules
frozen before any full-protocol result existed (roadmap, "Post-closure
pre-registration (2026-08-13)", which also discloses the 4a-screen
re-scoring as a peek carrying nothing).

* **Dilution predicate: 6/11 latents confirm** a strict subset above
  all-6 on T2 — substantively TT z3 (+0.090 ± 0.062 nat, drop {τ, A_s}),
  EE z2 (+0.115 ± 0.104, drop {H0, τ}), EE z3 (+0.085 ± 0.040, drop
  A_s), EE z4 (+0.126 ± 0.047, S⁺ = {ω_cdm, τ, A_s, n_s}); EE z0/z5
  pass at ≤ 0.003 nat (hairline, recorded as confirmed, read as
  negligible). The other five: not confirmed.
* **The sham mechanism test crosses**: TT pooled Δ_sham = **−0.0404 ±
  0.0134** nat → dilution demonstrated (3 SE; z0 most affected, −0.138);
  EE +0.0137 ± 0.0126 → null. In both models **0.0 %** of best-at-c≤10
  forms use the sham symbol — degradation, where present, is
  search-space dilution, never complexity spend.
* **Reading**: TT has the mechanism but (z3 aside) no confirmed subset
  advantage; EE has five subset advantages but no generic-dilution
  mechanism — its gains come from removing *specific* real inputs (a
  distractor effect), not from a smaller search space per se.
* **N-G2 dispositions** (all three flags resolved; no status flips, no
  headline change): TT z0 → all-6 stands (S⁺ not confirmed; the
  screen-era instability was near-ties among top supports); EE z3 →
  dilution-affected, S⁺ drops A_s; EE z4 → dilution-affected, the
  study's strongest case (every top-10 support beats all-6 on val).
  Cards carry the new `s_star.exhaustive_full` field + amended N-G2
  notes; every pre-existing card number is unchanged.

Sources: `experiments/subsets_full_*`, `sham_control_*`; full tables and
the per-rule verdicts in the roadmap "Outcome (2026-08-14)" section.

---

### 6.14 Post-closure — one-stage MSE reconstruction (2026-08-26)

A deliberately **non-blind** follow-up: can *one* larger expression reconstruct
a latent directly, including what the hierarchy recovers only through `f2`?
Same six raw inputs and search protocol; the inner loss becomes explicit
elementwise squared error, selection becomes held-out MSE, and the budget
ladder lifts to `maxsize ∈ {20, 30, 40}` (165 searches + 12 MSE shuffled
controls, zero failures). Because MSE rewards scale and offset rather than a
bijection class, this is a **reconstruction and compression** result and
changes no card, status or frozen threshold.

* **Known `f2` absorbed: 0/11 latents**, and the mechanism is the finding. The
  pre-specified test has two legs; across all 55 latent–seed audits the
  variance leg (`R²_f2 ≤ 0.05`, monotone cross-fit) passes **32/55** but the
  information leg (`MI ≤` its 39-permutation 97.5th-percentile null) passes
  **2/55**, with observed MI at **10×–140×** the null. The direct expression
  *launders* the second stage — stripping `f2`'s monotone-predictable part —
  rather than absorbing it. No latent reached `one-stage replacement`
  (6 `partial absorption`, 5 `no capacity gain`).
* **Capacity helps 6/11** under the paired rule (TT z1, z4; EE z1, z3, z4, z5);
  **EE z0 is the one latent a larger budget actively hurts** (`U95` 1.505),
  consistent with its standing unresolved status. Budget-saturated in 4/11;
  reported, not escalated past 40.
* **The objective's apparent landslide is mostly calibration.** Raw,
  `mi20-mse` scores NMSE ≈ 1.0 — MI-selected expressions have no numerical
  calibration by construction. Given the *same* monotone T1 map, MSE wins
  **9/11 not 11/11**, and TT z1 (2.92) and EE z4 (1.48) reverse.
* **Plain six-input OLS beats the maxsize-40 symbolic winner in 8/11 latents**,
  at times by an order of magnitude (TT z2: 0.00099 vs 0.01195 T2 NMSE). As
  pure reconstruction, direct symbolic regression is not the right tool for
  these latents.
* **Symbolic stability 11/11** (R_SR = 1.00 for ten latents, 0.80 for TT z2).

Executed off-CSD3 on a Lightning AI CPU Studio after the account hit its CPU
allowance; environment, per-task thread attribution and both recorded
deviations are in the `lightning_execution` block of
`experiments/mse_one_stage_execution_provenance.json`.

Sources: `docs/mse_one_stage_results.md` (combined, both checkpoints) ·
`experiments/mse_one_stage_sr_<run>.{json,md}` · protocol
`experiments/mse_one_stage_sr_plan.md`.

---

## 7. Controls (every null in one place)

| Control | Result | Where |
|---|---|---|
| Shuffled-target SR (amplitude, 2-input) | discovered-expression MI vs shuffled target ≈ 0.01–0.03 nat; vs true target ≈ 0.1–0.26 (τ-marginal floor), 3–12× below real; no textbook structure | `method.md` §3f |
| Shuffled-target SR (all-params) | ≤ 0.06 nat, no textbook structure on any control front | `allparams_blind_sr_*` |
| Stage-1 permutation nulls (R², per-param MI) | p97.5 ≈ −0.002 / 0.001 for all 11 latents | `sufficiency_audit_*`, cards appendix |
| Shuffled-residual SR (additive stage 2) | best MI vs true residual 0.066–0.074 (TT z2), 0.009–0.060 (EE z5) vs real 0.40–1.77 | `residual_sr_*` |
| Shuffled-residual SR (interaction-aware, 7-input) | 0.010–0.053 nat (TT z2, EE z0, EE z5 × 2 seeds) | `residual_sr_ia_*` |
| Sham-input dilution control (all-6 + permuted real θ column) | TT pooled Δ_sham −0.040 ± 0.013 (dilution demonstrated); EE +0.014 ± 0.013 (null); sham symbol in 0.0 % of best-at-c≤10 forms | `sham_control_*` |
| Level-set shuffled-form E_inv | 0.81–2.20 (TT), 1.59–1.81 (EE) vs pass threshold 0.05 | `levelset_audit_*` |
| Wrong-latent E_inv (specificity) | 0.2–2.8 across latents (amplitude cells are not invariant for other latents) | `levelset_audit_*`, `_joint_*` |
| Subspace shuffled-probe | max R² ≈ 0.000; shuffled-f MI floors ≈ 0.001 nat | `subspace_probe_*` |
| Positive control (G1) | machinery recovers the known amplitude answer *and* correctly reports its structured residual | `sufficiency_audit_*` |
| MSE shuffled-target SR (one-stage follow-up) | all 12 controls within \|R²\| ≤ 0.006 of zero on T2 against **both** the true and their own shuffled target, at ms20 and ms40 alike — a lifted budget buys a shuffled target nothing | `mse_one_stage_sr_*` |

---

## 8. Limitations and scope (state these prominently)

1. **Per-checkpoint claims.** Five PySR seeds establish *search* stability
   (R_SR); VAE-training-seed stability (R_model, roadmap Phase 9) was not
   run — it needs GPU retraining in the parent repo. Partial cross-model
   evidence exists (the amplitude family recurs across two different
   architectures/regimes with the count fingerprint matching the physics)
   but is not a substitute. Phase 9 remains executable later without
   touching any frozen threshold.
2. **The hierarchy does not terminate at two symbolic levels** — for any
   latent, under both additive and interaction-aware stage-2 ansätze. A
   statement about the representation, not the instruments.
3. **EE z0 unresolved** (see §6.12 for the localised blocker).
4. **Decoder triangulation of the amplitude pair is structurally unavailable
   in both models** — the (τ, lnA_s) templates are near-collinear (cond 70.2
   TT, 14.2 EE), so r_dec and amplitude mass are not identifiable and G4b
   FAILS on both. Phase 7b supports the shape-sector attributions and
   cos(a*, g_j); it contributes no −2 readout. All three surviving readouts
   of the −2 are encoder-side.
5. **Level-set legs for TT z1/z2/z4** are response-only (union support =
   all 6 leaves no nuisance direction; D-LS).
6. Estimator caveats are handled by design: η ratios rather than raw MI
   drive decisions, bootstrap SEs throughout, DPI sanity in Phase 5.

---

## 9. Candidate claims for the official write-up (ranked menu)

| # | Claim | Evidence chain | Caveats | Suggested placement |
|---|---|---|---|---|
| C1 | A β-VAE amplitude latent blindly re-derives `ln(A_s·e^{−2τ})`; the −2 is read three independent ways (forms, derivative ratio, frozen ratio-field detector) and re-appears in another latent's residual | §2; `method.md` stage 1 + stage 3a, `sufficiency_audit_*`, `residual_sr_*` | all three readouts are encoder-side — the decoder domain gives none (§6.10); per-checkpoint | **Main result** |
| C2 | All 11 latents of both models receive validated symbolic cards under pre-registered predicates: 10/11 "primarily interpreted" (saturating 1-D primary + discovered secondary), 1 honest unresolved | §3; `latent_cards_*` | statuses are per-checkpoint; "interpreted" bar not reached (by the representation, not the method) | **Main result** |
| C3 | Degeneracy breaking is visible blind, twice: the amplitude-latent *count* (1 → 2) before any SR, and the split-not-duplicated structure after (z4 alone carries τ; no redundant pair; synergy 0.013 → 0.473 nat) | §4; `method.md` §1, `subspace_probe_*` | — | **Main or strong secondary** |
| C4 | The methodology: freeze → validate-on-positive-control → unblind, with an η ladder (η_S/η_plat/η_post), semantic recurrence, interventional level sets, decoder triangulation, and a deviations register — a reusable recipe for scientific-VAE interpretation | §5; roadmap §0.3–0.5, gates in every deliverable | — | **Methods centerpiece** |
| C5 | The encoder hierarchy is symbolically non-terminating: structured residuals at every level probed, robust to interaction-aware enrichment; level-set failures agree *quantitatively* with calibration (E_inv/(1−R²) ∈ [1.1, 2.6]) | §6.5, §6.9, §6.12 | two levels probed (+ enriched ansatz); third level not attempted | **Secondary result / discussion** |
| C6 | Negative results with practical value: top-front MI is a capacity dial (search big, slice small); MI@c≤10 is tuning-flat; the additive-hierarchy limit at the TT amplitude latent is real structure (D-DoD-z2 → §6.12); input-set dilution is model-dependent — sham-demonstrated on TT, absent on EE, 6/11 budget-matched subset confirmations (§6.13) | §6.3, §6.12, §6.13 | — | **Methods / appendix** |
| C7 | The intrinsic-ceiling reframing: η̂_post turns "fraction of a search plateau" into "fraction of what the latent physically stores" (0.29–0.84 for primaries, 0.59–0.96 with secondaries) | §6.7–6.8; `posterior_ceiling_*` | GMM entropy estimate; DPI-checked | **Methods + results table** |
| C8 | Scope statement: everything is per-checkpoint pending R_model | §8 | — | **Limitations (verbatim)** |

---

## 10. Artifact map

| Deliverable (in `experiments/`) | Content |
|---|---|
| `allparams_blind_sr_<run>{,_ms10}` | all-params fronts, r-ratio, controls |
| `hpsweep_hp_v1_<run>` | sweep tables, one-factor effects |
| `knee_readout_<run>` (+ envelope PNGs) | plateaus, knees, η-level forms |
| `semantic_recurrence_<run>` | clusters, R_SR, canonical coordinates |
| `sufficiency_audit_<run>` | signatures, ratio pairs, residual audits, G1 |
| `subset_selection_<run>` | 63-subset screen + finalists, S*, G2 |
| `posterior_ceiling_<run>` | I(Z;θ), noise table, η_post, G3 |
| `residual_sr_<run>` | f₂, hierarchical accounts, stage-2 audits, DoD |
| `levelset_audit_<run>`, `levelset_audit_joint_<run>` | E_inv f₁-only/joint, responses, G4a |
| `decoder_effect_<run>` (+ curves) | d_k(ℓ), template decomposition, r_dec, G4b |
| `subspace_probe_<run>` | carrier sets, redundancy/synergy |
| `latent_cards_<run>` | **the synthesis**: cards, gates, controls, deviations |
| `residual_sr_ia_<run>`, `levelset_audit_joint_ia_<run>` | post-closure interaction-aware follow-up |
| `subsets_full_<run>`, `sham_control_<run>` | post-closure R-P4: budget-matched exhaustive support + sham dilution control |
| `mse_one_stage_sr_<run>`, `mse_one_stage_sr_plan.md`, `mse_one_stage_execution_provenance.json` | post-closure one-stage MSE reconstruction: ledger, frozen protocol, execution record (combined write-up: `docs/mse_one_stage_results.md`) |

Narrative: `docs/method.md` (protocol + amplitude story + §9 full-study
synthesis) · programme + closure: `docs/discovery_roadmap.md` (§0.3 frozen
rules; Closure section with phase ledger and Phase-9 disposition) ·
motivation/derivations: `docs/next_step.md` (superseded, annotated).
Compute: roadmap budget table (~1,700 core-h planned; hp_v1 ~77/model,
1b ~65, 4a screen ~1,015, ia follow-up 98 measured, R-P4 grid + sham
≈5,800 measured).

*Everything in this file is reproducible from `experiments/*.json`; the
per-latent numbers quoted here are the T2-confirmed card values.*
