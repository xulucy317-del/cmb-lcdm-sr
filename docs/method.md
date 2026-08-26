# Methodology pipeline — blind symbolic interpretation of CMB β-VAE latents

Four discovery stages, each with what it does and what it returned, plus a
fifth **post-closure reconstruction follow-up** (§5) that deliberately sits
outside the blind-discovery protocol. All numbers are the T2-confirmed values
in `docs/results_compendium.md`; sources named inline.

**Scope**: 2 checkpoints (TT-only `PirasCVAE` L=5; TT+EE-lowl
`DualEncoderCVAE` L=6; both β=3e-4, seed 42) · 11 latents · ≈2,000 PySR
searches ≈1,800 core-h. All claims per-checkpoint.

---

## 0. What is fixed before any stage runs

| | |
|---|---|
| Data | 500k LHS ΛCDM θ = (ω_b, ω_cdm, H0, τ, ln10¹⁰A_s, n_s) → CLASS spectra → stored encoders. SR target = posterior mean μ_k on the 50k test rows |
| Search protocol | PySR, 5000 samples, ni200 / pop15 / maxsize20, 5 seeds per config |
| Inner loss | `exp(−GMM-MI)` — pure-Julia fixed-K=2 EM, N_INNER=300 (~80× the PythonCall route) |
| Selection | full Python `gmm-mi` on held-out rows |
| Blindness | inputs are raw parameters only; no derived combination (`A_s·e⁻²ᵗ` or otherwise) is computed anywhere. Loss and selection metric share one invariance class — any bijection of either variable — so the search is rewarded for functional dependence, never calibration |
| Data hygiene | T0 = test[0:5000) SR fit+val · T1 = [5000:25000) calibration/anchors/audits · T2 = [25000:50000) confirmatory only (`src/cmb_lcdm_sr/tiers.py`) |
| Pre-registration | every threshold frozen in `docs/discovery_roadmap.md` §0.3 *before* shape-latent unblinding; instruments validated on the amplitude sector first (gate G1); post-freeze calls logged in a deviations register |

---

## 1. Six-input blind SR

**What**: all 6 raw parameters → each of the 11 latents, 5 seeds. No input
pre-selection, no latent pre-selection, no derived columns.

**Results** (`experiments/allparams_blind_sr_*`, `hpsweep_hp_v1_*`,
`knee_readout_*`, `semantic_recurrence_*`):

* **Every latent is a multi-parameter composite** — top forms use ≥5 of 6
  parameters. Cross-seed top MI 2.3–3.8 nat (TT) / 1.8–3.8 nat (EE), far
  above the 2-input amplitude ceilings because nothing is marginalised out.
* **The −2 survives full blindness**: derivative ratio
  r = (∂f/∂τ)/(∂f/∂lnA_s) over all top forms = **−1.974 ± 0.018** (TT) /
  **−1.993 ± 0.008** (EE).
* **Plateaus and knees**: cumulative Pareto envelopes 2.52–4.31 nat (TT) /
  1.79–4.18 nat (EE); one-SE knees c* = 18–29; envelope shape "no knee
  (diffuse)" for 10/11 — front information is spread over complexity.
* **Semantic recurrence, not string pooling**: canonical sympy ∨ |Spearman|
  ≥ 0.98 on anchors ∨ gradient-cosine ≤ 0.05, union-find with anti-chaining.
  One dominant cluster per latent; R_SR ≥ 0.8 for all 11.
* **Hyperparameters move the dial, not the discovery** (12 configs × 3 seeds
  × 2 models): maxsize alone swings top MI 1.6 → 4.05 nat, but the
  budget-matched MI@c≤10 is flat across every knob (~1.89 TT / ~2.02 EE).
  Search big then slice: the ms10 search's own front is *worse* at c≤10 than
  the sliced ms20 front (1.60 vs 1.89 TT; 1.69 vs 2.02 EE). r ≈ −1.97…−2.00
  in every config.
* **Control**: shuffled-target all-params SR ≤ 0.06 nat, no textbook
  structure on any control front.

---

## 2. Per-latent results and interpretation

**What**: each latent gets a card — canonical primary coordinate f₁ from
stage 1, a discovered second coordinate f₂ from blind SR on the cached
residual e₁ = μ − h(f₁) (all-6 inputs, 5 seeds), and a status under the
frozen predicates.

**TT-only (`lcdm_tt_beta3e-4`)**

| z | role | f₁ (canonical, blind) | η_S | η̂_post f₁ | η̂_post f₁+f₂ | R_SR | status |
|---|---|---|---:|---:|---:|---:|---|
| 0 | ω_b | `n_s/ω_b` | 1.003 | 0.531 | 0.903 | 1.00 | primarily interpreted |
| 1 | ω_cdm | `H0²·n_s²·ω_b/(A_s·ω_cdm²)` | 1.000 | 0.770 | 0.957 | 0.80 | primarily interpreted |
| 2 | amplitude (A_s, τ) | `A_s/log(H0·(ω_cdm+τ))` | 1.000 | 0.347 | 0.601 | 1.00 | primarily interpreted |
| 3 | n_s | `n_s + ω_cdm` | 0.997 | 0.447 | 0.838 | 1.00 | primarily interpreted |
| 4 | H0 | `A_s·H0²·ω_cdm·e^{−2τ}` | 1.000 | 0.371 | 0.758 | 0.80 | primarily interpreted |

**TT+EE-lowl (`lcdm_tt_ee_lowl`)**

| z | role | f₁ | η_S | η̂_post f₁ | η̂_post f₁+f₂ | R_SR | status |
|---|---|---|---:|---:|---:|---:|---|
| 0 | ω_cdm / early-ISW | `ω_cdm/(H0·n_s·ω_b)` | 1.000 | 0.756 | 0.842 | 1.00 | **unresolved** |
| 1 | H0 | `H0²·ω_cdm` | 1.000 | 0.348 | 0.663 | 1.00 | primarily interpreted |
| 2 | ω_b | `ω_b/n_s²` | 0.995 | 0.574 | 0.963 | 1.00 | primarily interpreted |
| 3 | n_s | `log(ω_b)/(n_s+ω_cdm)` | 0.992 | 0.493 | 0.864 | 0.80 | primarily interpreted |
| 4 | τ (amplitude sector) | `−A_s/(τ−0.445)` | 1.068 | 0.842 | 0.842 | 1.00 | primarily interpreted |
| 5 | amplitude (A_s, τ) | `A_s·e^{−2τ}` | 1.000 | 0.289 | 0.590 | 1.00 | primarily interpreted |

**Interpretation** (`experiments/latent_cards_*`, `residual_sr_*`,
`subspace_probe_*`):

* **10/11 "primarily interpreted", 1 unresolved.** Every latent has a 1-D
  symbolic primary that saturates its own support and recurs across seeds.
* **Second stage works**: recurrent f₂ for all 11 (R_SR 0.80; MI vs e₁
  0.40–1.77 nat against shuffled-residual nulls ≤ 0.074). Combined
  h(f₁) + g(f₂) reaches R²(μ) 0.955–0.998, lifting η̂_post from 0.29–0.84 to
  0.59–0.96.
* **No latent reaches full "interpreted"**: stage-2 residuals are still
  structured for all 11 — the encoder hierarchy does not terminate at two
  symbolic levels. Robust to an interaction-aware stage-2 ansatz (f1hat
  exposed as a 7th input: 8/11 return the identical canonical f₂).
* **EE z0 is the honest failure**: weakest stage-2 account (R² 0.39–0.41),
  joint level sets 0.060–0.062 vs the frozen 0.05 — a localised blocker, its
  residual holds more than one coordinate's worth of structure.
* **Degeneracy breaking is visible blind and model-level**: the raw
  disentanglement audit (MI to raw parameters only) shows **one**
  amplitude-sector latent in TT and **two** in TT+EE — before any SR runs.
  The EE sector is *split, not duplicated*: z4's τ-direction is carried by
  z4 essentially alone; no redundant latent pair exists in either model
  (all top-2 carrier conditionals synergistic; conditioning on z5 raises
  z1's information about `A_s·e⁻²ᵗ` from 0.013 to 0.473 nat).
* **Coordinates are latent-anchored, tails distributed**: each f₁ is
  linearly decodable from its own latent at rank-normal R² 0.88–0.95
  (axis-aligned = False for all 11); f₂ coordinates are genuinely
  distributed (own-latent R² 0.01–0.58).
* **Amplitude DoD** (f₂ pure shape-sector) MET on EE (f₂ = `H0·ω_cdm/n_s`),
  NOT MET on TT — recorded as D-DoD-z2: TT knee forms are A_s·(τ−c) × shape
  and an additive hierarchy cannot absorb a multiplicative interaction
  (τ-clamping the TT f₂ costs 0.20 nat). The interaction-aware rerun
  confirms this is real structure, not an ansatz artifact.

---

## 3. Sufficiency test

**What**: does the discovered coordinate account for the latent? Four legs,
all pre-registered.

**3a. Signatures and the answer-agnostic exponent detector.** Sensitivity
signatures g_j and Sobol indices per canonical form; constant-ratio field
ρ_ij = (∂f/∂u_i)/(∂f/∂u_j) flagged where cv < 5%. The (τ, lnA_s) pair emerges
with **r_raw = −2.000** on the cards (TT z4 f₁, EE z5 f₁) — the detector is
answer-agnostic and frozen. G1 knee-slice latent-level r_lin = −1.977 (TT).

**3b. Calibrated sufficiency.** After 5-fold cross-fitted monotone
recalibration, stage-1 residuals are **structured for all 11** latents:
R²_res 0.981–0.994 (TT), 0.960–0.994 (EE), against permutation nulls
≈ −0.002 / 0.001, with full-sector loadings.

**3c. Blind subset selection (the 63-subset campaign).** All 2⁶−1 = 63
supports × 2 screen seeds × 11 latents, finalists rerun at full protocol →
S* per latent with support-restricted ceilings Î_S. η_S = 0.99–1.07 for all
11: **every primary saturates its own support**. Minimal supports run |S| = 3
(EE z4: {ω_b, τ, A_s}) to 6. The amplitude latents return S* = all-6 as a
reproducible **superset finding** — shape-sector modulation is real
information. Three latents carry N-G2 attention flags (S* not
screen-recurrent: TT z0, EE z3, EE z4).

**3d. The intrinsic ceiling.** I(Z_k; θ) from the stochastic latent = 0.92–4.30
nat (TT), 1.34–4.18 nat (EE); posterior SNR 5.1 (TT z1) to 5,491 (TT z2) —
amplitude posteriors are near-deterministic, so their structured residuals are
*real stored information*, not sub-noise detail (DPI sanity holds throughout).
This converts MI fractions into physical statements via the **η ladder**:
η_S (does f saturate its own variables?) · η_plat (fraction of the
SR-accessible mean map) · η̂_post = MI(Z;f)/MI(Z;μ) (fraction of what the
latent physically stores; the demotion metric). A latent can honestly score
η_S = 1.00 and η_plat = 0.35 — that distinction is what makes "primarily
interpreted" precise.

**3e. Interventional leg — level-set invariance.** f₁-only: E_inv FAILS the
frozen 0.05 rule for **all 11** — and the failure *is* the structured
residual quantitatively, E_inv/(1−R²_cal) ∈ [1.1, 2.6] (6 inside the
predicted band, 5 above its factor-2 cap at the extreme-separation pairs the
audit deliberately draws). Joint (f₁, f₂) restores invariance: **7 of 8
auditable latents pass** (EE amplitude z5: 0.226 → 0.029, T2-confirmed);
EE z0 is the one joint FAIL (0.060, in-band); three TT latents whose union
support is all 6 have no nuisance direction left to test (D-LS). Nulls:
shuffled-form E_inv 0.81–2.20 (TT) / 1.59–1.81 (EE); wrong-latent 0.2–2.8.

**Gate G1** (amplitude positive control) **PASS on both models**: the frozen
machinery rediscovers {τ, lnA_s}, η_S = 1.000, recovers r — *and* correctly
fails the residual audit in the expected structured direction. It does not
fabricate sufficiency.

Sources: `experiments/sufficiency_audit_*`, `subset_selection_*`,
`posterior_ceiling_*`, `levelset_audit_*`, `levelset_audit_joint_*`.

---

## 4. Decoder effect (observable-domain triangulation)

**What**: leave the parameter domain entirely. Compute d_k(ℓ) = ∂Decoder/∂z_k
— what moving latent k does to the spectrum — and decompose it onto
data-driven parameter templates t_j(ℓ), d_k(ℓ) ≈ Σ_j a_j t_j(ℓ). The loading
vector a* is then compared to the symbolic signature g_j from stage 3.

**Results** (`experiments/decoder_effect_*`):

* Templates account for the decoder effect at **R²_W 0.988–1.000**.
* **cos(a*, g_j) = 0.77–1.00** across all 11 latents — the symbolic
  coordinate and the decoder's actual observable effect agree about which
  parameters a latent moves. This is the stage's solid result.
* **Gate G4b FAILS on both models**, for the same reason. The (τ, lnA_s)
  templates are near-antiparallel — uncentered cos(t_τ, t_lnAs) = −0.9902
  (EE concat), −0.9996 (TT); cond 14.2 and 70.2. Moving θ along the
  degenerate direction (δτ, δlnA_s) ∝ (1, 2) leaves these spectra invisible,
  so the fitted (a_τ, a_lnAs) split slides freely along that ridge at no cost
  to R². **r_dec and amplitude mass are therefore not identifiable in this
  design** and the deliverables report them "for completeness, not as
  claims".

  | bullet (frozen) | TT | EE |
  |---|---|---|
  | amplitude-sector mass ≥ 0.8 | 0.64 FAIL | 0.79 FAIL |
  | \|r_dec + 2\| ≤ 0.3 | +0.351 FAIL | −1.873 PASS (not identifiable) |
  | decomposition R²_W ≥ 0.8 | 1.000 PASS | 1.000 PASS |

  EE's r_dec = −1.87 is one point on the ridge, not a measurement: across
  fit variants it moves −1.87 (OLS) / −1.67 (2ℓ+1-weighted) / −1.77
  (h/2 templates) / −2.32 (anchor point).
* **What *is* identifiable**: the shape-sector coefficients, and proj_brk —
  the projection onto the degeneracy-breaking direction (−2, 1)/√5 (EE z5:
  0.047, stable across all variants). The degenerate component proj_deg is
  not.
* **Consequence**: the decoder confirms *which parameters* each latent moves,
  but yields **no observable-domain readout of the −2** in either model.

**This stage does not contribute a −2 readout.** Earlier drafts of this file
and of `results_compendium.md` listed r_dec = −1.87 as a fourth independent
readout and recorded EE G4b as "PASS-equivalent"; both are corrected here
against `experiments/decoder_effect_*.md`, which state the ridge limitation
and record **G4b: FAIL** for EE (mass 0.79) as well as TT.

---

## 5. One-stage MSE reconstruction (post-closure follow-up, 2026-08-26)

**What**: ask whether *one* larger symbolic expression can reconstruct a latent
directly — including the structure the two-stage hierarchy recovers only via
`f2` — by changing the objective rather than the inputs. Same six raw
parameters, same 5000 T0 samples, same ni200/pop15, seeds 0–4; what changes is
the inner loss, the selector, and the budget ladder.

**This is a reconstruction and compression study, not a discovery result.** MSE
is calibration-sensitive by construction: it rewards the scale, offset and shape
that reproduce μ_k, so it leaves the bijection-invariance class that makes
stages 1–4 blind. It changes no card, no status and no frozen threshold.

Methods added for it, all reusable:

| addition | what it does |
|---|---|
| Loss/selection dispatch | explicit registry over `{gmm_mi, mse}`; `--inner-loss`, `--selection-metric`, `--posthoc-mi`. GMM-MI goes through PySR's `loss_function`, MSE through an explicit elementwise `(pred − target)²` via `elementwise_loss` — never both. Existing GMM-MI invocations keep their previous behaviour exactly |
| Fit-only target standardisation | μ_k standardised with T0-fit statistics only, inverted before any native-unit metric; equivalent to raw-latent MSE up to a fixed per-latent factor, with better conditioning |
| Lifted budget ladder | fixed `maxsize ∈ {20, 30, 40}` for every latent, no data-dependent escalation; **budget-saturated** flagged when ≥3/5 `mse40` winners reach complexity ≥38 |
| Three-stage immutable consolidation | `select` (T0 only) → `calibrate` (T1 only) → `confirm` (T2, once). Each stage hashes its output; the next verifies that digest before running, so no equation or budget can be re-chosen in light of a later tier |
| Cross-seed one-standard-error readout | mean envelope `E_s(c)` over seeds, then the smallest complexity within `sd(E_s(c_min))/√5` of the minimum — a parsimony readout, never a success criterion |
| Two-leg known-`f2` absorption test | five-fold 64-bin monotone `q(f2)` cross-fit on T1 and refit on all T1, then on T2 both `R²_f2 ≤ 0.05` **and** `MI(e_direct; f2)` ≤ its own 97.5th-percentile 39-permutation null. No map or threshold fitted on T2. Under amendment A2 this is the experiment's only newly computed MI |
| MSE shuffled-target controls | protocol-identical searches on independently permuted targets at both endpoint budgets — the GMM-MI-era controls cannot stand in for an MSE search |
| Scheduler-free execution | `scripts/run_mse_one_stage_pool.py` runs the frozen task matrix in persistent Julia/PySR workers (startup amortised once per worker, not once per task), skipping only reports that validate against their own task. The Slurm launchers remain the definition of task identity via `PRINT_MATRIX=1` |

**Results** (`docs/mse_one_stage_results.md`; 165 searches + 12 controls, zero
failures):

* **The known `f2` is absorbed in 0/11 latents**, and the two legs disagree
  systematically: the variance leg passes 32/55 latent–seed audits, the MI leg
  2/55, with observed MI running 10×–140× its permutation null. A single large
  expression *launders* the second stage — removing `f2`'s monotone-predictable
  contribution — rather than absorbing it. No latent reached
  `one-stage replacement`.
* **Capacity helps 6/11** under the paired rule; **EE z0 is the one latent
  where a larger budget actively hurts**, consistent with its standing
  unresolved status.
* **The apparent objective win is mostly calibration.** Raw, `mi20-mse` scores
  NMSE ≈ 1.0 — MI-selected expressions carry no numerical calibration by
  construction. Given the *same* monotone T1 map, the MSE objective wins 9/11
  rather than 11/11, and TT z1 and EE z4 reverse. MSE search finds
  better-*calibrated* expressions, not uniformly better *coordinates*.
* **Plain six-input OLS beats the maxsize-40 symbolic winner in 8/11 latents**,
  sometimes by an order of magnitude. As pure reconstruction, direct symbolic
  regression is not the right tool for these latents; the experiment's value is
  the structural finding above, not reconstruction accuracy.

---

## The −2, read three independent ways

| # | Readout | Value |
|---|---|---|
| 1 | The discovered forms (2-input reference study) | TT `A_s·(τ−0.598)` 5/5 seeds; EE `A_s·(τ−0.579)` + literal `A_s·e⁻²ᵗ`; affine constants match the Taylor prediction c = τ̄ + ½ ≈ 0.570 to 1.5–5% |
| 2 | Derivative ratio over 6-input top forms (stage 1) | −1.974 ± 0.018 (TT) / −1.993 ± 0.008 (EE) |
| 3 | Frozen constant-ratio detector (stage 3a) | r_raw = −2.000 (TT z4 f₁, EE z5 f₁) |

All three are encoder-side. **There is no observable-domain readout**: the
decoder-template ratio r_dec is unidentifiable in this design (stage 4).

Fourth appearance: the EE H0-latent's *residual* coordinate is literally
`A_s·exp(−2τ)/ω_b²` with ratio −2.0000 — found blindly in stage 2 and again
by the independent interaction-aware rerun.

---

## Limitations

1. **Per-checkpoint.** Five PySR seeds establish *search* stability (R_SR);
   VAE-training-seed stability (R_model) was not run — it needs GPU
   retraining in the parent repo.
2. **The hierarchy does not terminate at two symbolic levels**, under both
   additive and interaction-aware stage-2 ansätze. A statement about the
   representation, not the instruments. The §5 follow-up adds the converse:
   one stage does not *collapse* into two either — at `maxsize` 40 the direct
   expression still leaves `f2`-dependence at 10×–140× its permutation null in
   every latent.
3. **EE z0 unresolved.**
4. **Decoder triangulation of the amplitude pair is structurally unavailable
   in both models** — the (τ, lnA_s) templates are near-collinear (cond 70.2
   TT, 14.2 EE), so r_dec and amplitude mass are not identifiable and G4b
   FAILS on both. The decoder stage supports the *shape*-sector attributions
   and cos(a*, g_j), not the −2.
5. **Level-set legs for TT z1/z2/z4** are response-only (union support = all
   6 leaves no nuisance direction).
6. Estimator caveats handled by design: η ratios rather than raw MI drive
   decisions; bootstrap SEs throughout; DPI sanity checks.

7. **§5 is calibration-sensitive by design** and sits outside the blind
   protocol; its numbers must never be quoted as discovery results. Its own
   scope limits (unpaired hierarchy denominator, incomparable complexities, no
   residual-completeness claim) are listed in `docs/mse_one_stage_results.md`.

Full record: `docs/results_compendium.md` · one-stage MSE follow-up:
`docs/mse_one_stage_results.md` · frozen rules: `docs/discovery_roadmap.md`
§0.3 · deliverables: `experiments/`.
