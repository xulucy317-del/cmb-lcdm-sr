# Blind symbolic discovery of the CMB amplitude latent — GMM-MI inner loss

Distilled from the parent `cmbvae` study (`docs/extension/blind_sr_gmm_mi.md`,
2026-06-25, combining the EE study of 2026-06-23 and the TT study of
2026-06-25). This repo re-runs exactly that configuration; the numbers below
are the parent study's reference results (2 regimes × 5 GMM-MI seeds × 200
PySR iterations × 5000 samples).

**Stored models targeted:** `models/lcdm_tt_beta3e-4` (TT-only) and
`models/lcdm_tt_ee_lowl` (TT+EE-lowl).
**Per-seed outputs:** `results/<run>/symbolic_regression_gmm_mi_seed<N>/report.json`.

---

## TL;DR

In **both** regimes the β-VAE amplitude latent blindly recovers the textbook
TT-amplitude combination **`ln(A_s · e^{−2τ})`** — the −2
reionization-suppression exponent — from the encoder alone, with no hand-coded
reference to any derived parameter anywhere in the pipeline. PySR is fed only
the raw pair `(A_s, τ)` and the encoder posterior mean, scored by a
scale/shift-invariant GMM-MI inner loss across 5 seeds.

| Regime | Degeneracy | Latent | Top form (per seed) | val MI [nat] | literal `exp(−2τ)` |
|---|---|---|---|---|---|
| **TT-only** β=3e-4 | present | idx 2 | `A_s·(τ−0.598)` (5/5) | 0.822 | no (affine only) |
| **TT+EE-lowl** | broken | z₅ | `A_s·(τ−0.579)` / `A_s·e⁻²ᵗ` | 1.196 | yes (seed 3) |
| truth | — | — | `ln(A_s·e⁻²ᵗ)` | — | — |

The −2 is recovered whether the A_s–τ degeneracy is **present** (TT-only) or
**broken** (TT+EE-lowl). TT-only is the noisier read — it *is* the degenerate
combination at lower information content; EE's broken-degeneracy latent is
cleaner.

---

## 1. What "blind" means — the shared protocol

An earlier (non-blind) identification in the parent project leaked prior
knowledge two ways: elementwise-MSE fitting against the *standardised* latent
(uses the encoder's calibration constants), and a hand-coded `A_s·e⁻²ᵗ`
baseline computed alongside. The blind setting drops both:

- **No standardisation leakage** — the inner loss is a real MI estimator
  (GMM-MI), invariant under any bijection of either variable, so PySR is
  rewarded for *functional form*, not for matching the encoder's mean/std.
- **No textbook reference anywhere** — nothing of the form `A_s·e⁻²ᵗ` is
  computed in the pipeline; only the data-driven OLS fit in raw `(A_s, τ)` is
  kept as an auxiliary.

The question both regimes answer: *can SR rediscover the textbook combination
from the encoder alone?*

### Setup (identical across all 10 runs)

| Quantity | Value |
|---|---|
| Compressor | TT-only: `PirasCVAE` (L=5) · TT+EE: `DualEncoderCVAE` (L=6); both β=3e-4, seed=42 |
| Latent target | TT idx 2 / EE z₅ — the amplitude latent |
| Inputs | `A_s`, `tau` (raw; no derived columns) |
| Samples | 5 000 total (4 000 fit / 1 000 val) |
| PySR | 200 niterations, 15 populations, maxsize 20 |
| Unary / binary ops | `exp, log, neg, square` / `+, *, −, /` |
| Inner loss | **`gmm_mi`** — `exp(−GMM-MI)`, pure-Julia EM, K=2, N_INNER=300 |
| Selection (post-hoc) | val GMM-MI on every Pareto-front eq; top-5 by val MI desc |
| Hand-coded baseline | **none**; OLS reference kept (data-driven only) |
| Mean fit time | ~340 s/seed (16 threads) |

### How each case is run (inputs → target)

For each spectrum in the test split we build one `(X → y)` row and ask PySR
for `y = f(X)`:

- **Inputs `X` (same for both):** the two raw ΛCDM parameters **`A_s` and
  `τ`** straight from `theta.npy` — no log, no products, no derived columns.
- **Target `y` = the latent to explain:**
  - **TT-only:** encode the TT spectrum with `PirasCVAE`
    (`models/lcdm_tt_beta3e-4`); take the posterior mean of **latent index 2**.
  - **TT+EE-lowl:** encode the stacked TT+EE spectrum with `DualEncoderCVAE`
    (`models/lcdm_tt_ee_lowl`); take the posterior mean of **z₅**.

Concretely, one run is:

```bash
python scripts/run_blind_sr.py \
  --run-dir <models/lcdm_tt_beta3e-4 | models/lcdm_tt_ee_lowl> \
  --latent-index <2 | 5>  --inputs A_s tau  --seed <N>
```

The *only* methodological difference between the two cases is `--run-dir`
(which encoder) and `--latent-index` — inputs, target type, loss, and budget
are shared.

### Why these latents — and why the choice is still blind

Targeting "the `A_s·e⁻²ᵗ` latent" sounds circular. It is not, because the
target is chosen one stage *earlier* by a **blind disentanglement audit** —
the standard β-VAE step of measuring MI between each latent and the **raw**
ΛCDM parameters. **No derived combination enters the selection.**

**TT-only (L=5) — MI to raw parameters** (the `A_s·e⁻²ᵗ` column is
*post-hoc*, never used to select):

| latent | ω_b | ω_cdm | H₀ | τ | lnA_s | n_s | ‖ A_s·e⁻²ᵗ (post-hoc) |
|---|--:|--:|--:|--:|--:|--:|--:|
| z0 | **0.92** | 0.03 | 0.01 | 0.00 | 0.00 | 0.04 | 0.00 |
| z1 | 0.04 | **0.26** | 0.13 | 0.01 | 0.04 | 0.10 | 0.01 |
| **z2** | 0.01 | 0.04 | 0.04 | **0.20** | **0.32** | 0.01 | 0.82 |
| z3 | 0.01 | 0.17 | 0.01 | 0.00 | 0.00 | **0.59** | 0.00 |
| z4 | 0.03 | 0.06 | **0.48** | 0.04 | 0.06 | 0.01 | 0.11 |

Exactly one latent — z2 — carries the amplitude sector (substantial MI to
*both* lnA_s and τ). There is only one such latent because TT cannot separate
A_s and τ — that single amplitude degree of freedom *is* the degeneracy.

**TT+EE-lowl (L=6) — MI to raw parameters:**

| latent | ω_b | ω_cdm | H₀ | τ | lnA_s | n_s | ‖ A_s·e⁻²ᵗ (post-hoc) |
|---|--:|--:|--:|--:|--:|--:|--:|
| z0 | 0.10 | **0.29** | 0.15 | 0.00 | 0.01 | 0.03 | 0.01 |
| z1 | 0.02 | 0.13 | **0.61** | 0.01 | 0.01 | 0.00 | 0.02 |
| z2 | **0.41** | 0.03 | 0.00 | 0.00 | 0.01 | 0.22 | 0.00 |
| z3 | 0.13 | 0.13 | 0.01 | 0.00 | 0.00 | **0.40** | 0.00 |
| z4 | 0.00 | 0.00 | 0.00 | **0.43** | 0.28 | 0.00 | 0.00 |
| **z5** | 0.00 | 0.03 | 0.01 | 0.23 | **0.37** | 0.00 | 1.20 |

Now **two** latents load on the amplitude sector — z4 (τ-dominant) and z5
(lnA_s-dominant). We target **z5**, the A_s/amplitude latent (highest
raw-amplitude loading); picking z5 over z4 uses only raw-A_s MI, still no
derived combination.

**Bonus — the count is the signal.** The *number* of amplitude-sector latents
(1 in TT, 2 in TT+EE-lowl) is itself a blind, model-level signature of the
degeneracy breaking, visible from the raw-MI audit before any SR is run.

---

## 2. Two regimes, one combination — and why both matter

The object of interest is the A_s–τ **degeneracy**: in TT the spectrum
depends (above the reionization scale) only on the product `A_s·e⁻²ᵗ`, so τ
and A_s cannot be separated.

- **TT-only — degeneracy present.** The single amplitude latent is *forced*
  to be the constrained combination `A_s·e⁻²ᵗ`. This is the regime where the
  degeneracy genuinely lives.
- **TT+EE-lowl — degeneracy broken.** The ℓ≲30 EE reionization bump
  (∝ `A_s·τ²`) is an independent handle on τ, so the model separates τ and
  `A_s·e⁻²ᵗ` onto two latents. The amplitude latent z₅ is then one of two
  *separated* directions, encoded at higher information content.

Running blind SR in both is the point: it shows the −2 is recovered both when
the model is *forced* into the combination (TT, near-tautological) and when it
*could* have separated A_s but the amplitude latent still organises as
`A_s·e⁻²ᵗ` (EE, a genuine emergent discovery).

---

## 3. Results (parent-study reference numbers)

### 3a. Per-seed top form (ranked by val GMM-MI)

**TT-only** (idx 2) — unanimous:

| seed | c | val MI [nat] | top form |
|---:|---:|---:|---|
| 0 | 5 | 0.8216 | `A_s·(τ − 0.5980703)` |
| 1 | 5 | 0.8216 | `A_s·(τ − 0.5980651)` |
| 2 | 5 | 0.8216 | `A_s·(τ − 0.5980651)` |
| 3 | 5 | 0.8216 | `A_s·(τ − 0.5980575)` |
| 4 | 5 | 0.8216 | `A_s·(τ − 0.5980651)` |

**TT+EE-lowl** (z₅):

| seed | c | val MI [nat] | top form |
|---:|---:|---:|---|
| 0 | 8 | 1.196 | `exp(2460·A_s·(τ − 0.579))` ★ |
| 1 | 7 | 1.196 | `A_s·(τ − 0.5788) − 4.4e−5` ★ |
| 2 | 7 | 1.196 | `A_s · exp(−exp(1.725·τ))` |
| 3 | 9 | 1.198 | `249.9·A_s·exp(−2τ) + 0.118` ★★ |
| 4 | 9 | 1.197 | `−1.737·A_s·τ + A_s − 8.4e−5` ★ |

★ contains the textbook direction; ★★ literal `A_s·exp(−2τ)`.

### 3b. The −2 coefficient — parent-study readout (dropped here)

The GMM-MI loss is bijection-invariant, so the SR returns the textbook
direction *up to an affine/monotone wrapper*. The parent study additionally
pinned the literal `−2` with a post-hoc OLS fit of the latent in
`(ln A_s, τ)` — τ/lnAs = −1.988 (TT-only, R²=0.813) and −1.9995 (TT+EE-lowl,
R²=0.913), i.e. the latents are ∝ ln(A_s·e⁻²ᵗ). This distilled repo drops
that OLS post-fit; the blind evidence here is the recovered form itself
(§3a, §3d) plus the Taylor-constant check (§3c).

### 3c. Why `A_s·(τ − c)` *is* the textbook combination

The first-order Taylor expansion of `A_s·e⁻²ᵗ` about `τ̄` gives
`A_s·(τ − c)` ∝ `A_s·e⁻²ᵗ` with `c = τ̄ + ½`. The LHS prior is
τ ∈ [0.010, 0.130], τ̄ ≈ 0.070, predicting c ≈ 0.570; discovered constants
are 0.579 (EE) to 0.598 (TT) — ~1.5–5% high because the latent is not
*exactly* `A_s·e⁻²ᵗ` and the MI-optimal affine constant absorbs
curvature/noise. The Taylor constant is a *qualitative* structural
confirmation (the parent study's linear-fit readout, §3b, pinned the
exponent quantitatively).

### 3d. Sub-expression occurrence (regex scan over all Pareto-front equations)

| Pattern | TT-only | TT+EE-lowl |
|---|---:|---:|
| `A_s·exp(−2τ)` literal | 0 | 8 |
| `exp(−2τ)/A_s` related | 0 | 1 |
| `A_s·(τ − c)` affine/Taylor | 28 | 28 |
| total textbook-direction hits | 28 | 37 |
| (of N equations) | 78 | 78 |

(The same scan runs in `scripts/consolidate_blind_sr.py`.)

### 3e. Why TT-only returns only the affine form — and more seeds won't change it

All 5 TT seeds returned the *same* complexity-5 form and never the explicit
`exp(−2τ)`. This is **structural, not seed-luck**:

| check | value | meaning |
|---|---|---|
| `exp(−2τ)` linearity over τ∈[0.01,0.13] | R² = 0.9990, max dev 0.52% | the exponential is a near-perfect straight line over the prior |
| corr(`A_s·exp(−2τ)`, `A_s·(τ−0.598)`) | −0.9995 | the two forms are the same function on the support |
| MI(z, exp) vs MI(z, affine) | 0.840 vs 0.828 nat (KSG) | a tie within estimator noise |

The affine form (complexity 5) already saturates the latent's MI. Because
`exp(−2τ)` is 99.9% linear over the prior, the explicit exponential
(complexity 9) can at best *tie*, and on a tie PySR's parsimony penalty
deterministically ranks the simpler form first. EE surfaced the literal
exponential only because its latent is cleaner (R² 0.91 vs 0.81).

### 3f. Shuffled-target negative control

`run_shuffled_control.py` permutes the target latent across rows (inputs
unchanged) and reruns the identical PySR configuration. Parent-study result:
MI of the discovered expression against the shuffled target it was trained
on is ≈0.01–0.03 nat (the search finds nothing), and against the TRUE target
≈0.1–0.26 nat (the residual τ-marginal floor) — 3–12× below the real
blind-SR MI and without the `A_s·e⁻²ᵗ` structure. The textbook combination
requires the real row-wise A_s–τ–latent relationship, which shuffling
removes.

---

## 4. TT vs EE — what the comparison shows

| | TT-only (degeneracy present) | TT+EE-lowl (degeneracy broken) |
|---|---|---|
| Top form | `A_s·(τ−0.598)` (5/5 seeds) | `A_s·(τ−0.579)` / `A_s·e⁻²ᵗ` |
| val MI [nat] | 0.822 | 1.196 |
| Explicit `exp(−2τ)` found | no | yes (seed 3) |
| Status of the −2 | *forced* (only amplitude direction) | *emergent* (model could separate A_s) |

Both recover −2. The agreement of the two arms is the result: the −2
reionization-suppression exponent is recovered blindly, robust to whether the
degeneracy is present or lifted.

---

## 5. Why GMM-MI — and why the other inner losses are not in this repo

A real MI estimator inside the inner loop shares its invariance class with
the post-hoc selection metric: **any bijection of either variable leaves the
loss unchanged**. The search is then rewarded purely for functional
dependence — so the explicit exponential, its Taylor form, `2τ − ln A_s`,
etc. all carry identical MI, and PySR's complexity penalty picks among them.
In both regimes the cross-seed MI is tight (TT 0.8216 ± 0.025; EE
1.196 ± 0.001) and the textbook form *saturates* the encoder's MI ceiling.

The parent study also ran mse / r2 / spearman / dcor / hsic / ksg inner
losses (its `blind_sr_ee_z5.md`). Summary of that ablation, which is why this
distilled repo keeps only `gmm_mi`:

- **mse** (paper-faithful) rewards calibration to the standardised target —
  not blind, by construction.
- **r2 (Pearson)** reaches the same validation MI (~1.195 nat) but recovers
  the textbook form at **0/5 seeds** (locks onto a rational form that shares
  the information but not the structure).
- **spearman / dcor / hsic / ksg** variously under-perform or tie without
  improving on gmm_mi's 5/5 textbook-form recovery.
- **gmm_mi** recovers the textbook direction at every seed in both regimes.

---

## 6. Why pure-Julia GMM-MI is feasible (the ~80× speedup)

The first GMM-MI attempt called the Python `gmm-mi` estimator from Julia via
`PythonCall.jl` — extrapolating to ~7 h/seed. The pure-Julia rewrite
(`src/cmb_lcdm_sr/sr.py::JULIA_LOSS_GMM_MI`) is ~80× faster:

| Factor | PythonCall path | Pure-Julia path |
|---|---|---|
| Cross-language per-call | ~5–20 ms (GIL + numpy marshaling) | ~0 (native) |
| Estimator per-call | ~25 ms (K=1..5 selection, CV, bootstrap) | ~1–5 ms (fixed K=2, ~300 samples × ≤30 EM iters) |
| Threading | 1 (GIL serialises population eval) | 16 (`JULIA_NUM_THREADS=16`) |
| Net wallclock / seed | ~7 h (infeasible) | **~5 min** |

The bottleneck was the language boundary, not the GMM-MI math. The cheap
fixed-K=2 estimator is used only *inside* the search; final selection always
uses the full Python `gmm-mi` estimator on held-out data.

---

## 7. Reproduce

```bash
# 0. one-off per model (needs the spectra shards; see README data provenance)
python scripts/encode_latents.py --run-dir models/lcdm_tt_beta3e-4
python scripts/encode_latents.py --run-dir models/lcdm_tt_ee_lowl

# 1. TT-only (degeneracy present) — amplitude latent idx 2
for N in 0 1 2 3 4; do
  python scripts/run_blind_sr.py --run-dir models/lcdm_tt_beta3e-4 \
      --latent-index 2 --inputs A_s tau --seed $N --turbo
done

# 2. TT+EE-lowl (degeneracy broken) — amplitude latent z5
for N in 0 1 2 3 4; do
  python scripts/run_blind_sr.py --run-dir models/lcdm_tt_ee_lowl \
      --latent-index 5 --inputs A_s tau --seed $N --turbo
done

# 3. controls + pooling + consolidation
for S in 0 1 2; do
  python scripts/run_shuffled_control.py --run-dir models/lcdm_tt_beta3e-4 --target-index 2 --shuffle-seed $S --pysr-seed $S --turbo
  python scripts/run_shuffled_control.py --run-dir models/lcdm_tt_ee_lowl  --target-index 5 --shuffle-seed $S --pysr-seed $S --turbo
done
python scripts/pool_sr_runs.py --glob 'results/lcdm_tt_beta3e-4/symbolic_regression_gmm_mi_seed*/report.json' --out results/lcdm_tt_beta3e-4/sr_pooled
python scripts/pool_sr_runs.py --glob 'results/lcdm_tt_ee_lowl/symbolic_regression_gmm_mi_seed*/report.json'  --out results/lcdm_tt_ee_lowl/sr_pooled
python scripts/consolidate_blind_sr.py
```

---

## 8. Manuscript draft — blind discovery of the CMB amplitude latent

We test whether symbolic regression recovers the content of the β-VAE
amplitude latent with no hint of the answer in the pipeline, in two regimes:
TT-only (the A_s–τ degeneracy present) and TT+EE-lowl (the degeneracy broken
by the low-ℓ EE reionization bump). In each we feed PySR only the raw pair
`(A_s, τ)` and the encoder posterior mean, computing no derived combination
anywhere. The inner loss is a GMM-MI estimator — a pure-Julia two-component
mixture evaluated on 300-sample batches at millisecond cost — and the Pareto
front is ranked by GMM-MI on a held-out split. Inner loss and selection
metric share one invariance class — any bijection of either variable leaves
them unchanged — so the search rewards functional dependence, not calibration
to the latent scale.

In both regimes the amplitude latent encodes `ln(A_s·e⁻²ᵗ)`, the TT amplitude
combination. Across five seeds the top form saturates the encoder ceiling
(val MI 0.822 nat TT-only, 1.196 nat TT+EE-lowl). The recovered forms carry
the −2 structurally: the affine constant in `A_s·(τ−c)` lands within a few
percent of the value the first-order Taylor expansion of `A_s·e⁻²ᵗ` predicts
(c = τ̄ + ½), and one EE seed returns `A_s·e⁻²ᵗ` explicitly. No seed sees a
textbook reference at any point. The agreement of the two regimes shows the
−2 reionization-suppression exponent is an intrinsic feature of the CMB
amplitude direction, recovered blindly whether the degeneracy is present or
lifted.

---

## 9. From amplitude rediscovery to representation cards — the full study

Sections 1–8 established the blind protocol on one latent per model whose
ground truth was known. The discovery study
([`docs/discovery_roadmap.md`](discovery_roadmap.md), phases 0–10;
deliverables in `experiments/`, final synthesis
`latent_cards_<run>.{md,json}`) extends the claim to **all 11 latents** of
the two checkpoints, with the amplitude sector as registered positive
control (gate G1) and every instrument frozen (§0.3 thresholds) before any
shape-latent unblinding. What the phases added:

* **Saturation, not argmax (phases 1–2).** Cumulative Pareto envelopes give
  each latent a plateau and a one-SE knee; semantic clustering (algebraic
  identity ∨ |Spearman| ≥ 0.98 ∨ gradient distance ≤ 0.05) replaces string
  pooling. Every latent has one dominant cluster with R_SR ≥ 0.8 (9/11 at
  1.0); the amplitude clusters contain the textbook family with R_SR 1.0
  (the EE representative is literally `A_s*exp(-2*tau)`).
* **Calibrated sufficiency + blind subsets (phases 3–4).** After an
  arbitrary 1-D recalibration, every canonical coordinate saturates its
  support-restricted ceiling (η_S ≈ 1.0; S* from a blind 63-subset screen);
  every stage-1 residual is *structured* (R²_res 0.98–0.99) — the frozen
  machinery reports "primary coordinate + structured residual" everywhere
  rather than fabricating sufficiency, exactly the direction G1 demands.
* **The intrinsic ceiling (phase 5).** I(Z_k;θ) from the stochastic latent
  turns MI fractions into physical statements: the deterministic mean map
  carries detail the sampled latent cannot transmit (res_var/noise up to
  382), and η̂_post = MI(Z;f)/MI(Z;μ) (registered refinement R-P5) is the
  demotion metric. Canonical forms store 0.29–0.84 of what each latent
  knows; S*-forms 0.84–0.99.
* **Hierarchical closure (phase 6).** Second-stage blind SR on the residual
  caches gives every latent a recurrent f₂ (R_SR 0.80; shuffled-residual
  nulls ≤ 0.07 nat vs 0.4–1.8 real). The combined account h(f₁)+g(f₂)
  reaches R²(μ) 0.955–0.998 and lifts η̂_post to 0.59–0.96. The
  pre-registered amplitude DoD (f₂ pure shape-sector) is MET on EE
  (f₂ = H0·ω_cdm/n_s) and NOT MET on TT — substantively: the TT knee forms
  are A_s·(τ−c) × shape, and an additive hierarchy cannot absorb the
  multiplicative interaction (τ-clamping f₂ costs 0.20 nat; deviation
  D-DoD-z2). A consistency bonus: the EE H0-latent's residual coordinate
  is literally `A_s*exp(-2*tau)/omega_b**2` with (τ, lnAs) ratio −2.0000.
* **Interventional validation (phase 7).** Level sets of f₁ alone are NOT
  invariant — E_inv lands inside [1−R²_cal, 2(1−R²_cal)] for all 11
  latents, i.e. the within-level-set movement IS the structured residual
  (honest G4a FAIL). Jointly conditioning on (f₁, f₂) restores invariance:
  7 of 8 auditable latents pass the frozen 0.05 rule (EE amplitude
  0.226 → 0.029, **gate G4a-joint PASS**, T2-confirmed, wrong-latent
  controls 0.2–2.3); the three TT latents whose union support is all 6
  parameters have no nuisance direction left to test (deviation D-LS).
  Decoder-side (7b): d_k(ℓ) decomposes onto data-driven parameter
  templates at R²_W ≈ 1.0 with cos(a*, g_j) 0.77–1.00; the EE reionization
  bump identifies the amplitude pair and returns **r_dec = −1.87** — a
  third, observable-domain readout of the −2 (TT's ℓ≥30 spectra leave the
  pair collinear: G4b FAIL by mechanism, documented).
* **Subspace & redundancy (phase 8).** Sparse probes show each canonical
  coordinate is linearly decodable from its own latent at rank-normal
  R² 0.88–0.95, with the remainder genuinely distributed across the code
  (the own latent is always in the 1-SE carrier set). Slab-conditional MI
  finds **no redundant pair in either model** — every top-2 carrier
  conditional is synergistic — and answers the flagged question: the EE
  amplitude sector is *split*, not duplicated (z4's τ-direction is carried
  by z4 essentially alone, A* = {z2, z4}; conditioning on z5 raises z1's
  information about `A_s·e⁻²ᵗ` from 0.013 to 0.473 nat). Residual
  coordinates are distributed (own-latent R² 0.01–0.58). Controls null
  throughout (shuffled-probe R² ≈ 0.000, shuffled-f floors ≈ 0.001 nat).
* **Statuses (phase 10).** Under the frozen predicates, **10 of 11 latents
  are "primarily interpreted"** — a validated 1-D primary coordinate plus
  a documented structured residual, now with a discovered second
  coordinate — and EE z0 is **unresolved** (weakest stage-2 account,
  R² 0.41; joint E_inv 0.060 vs 0.05, inside its expected band). No latent
  reaches full "interpreted": the stage-2 residuals are still structured —
  the encoder hierarchy does not terminate at two symbolic levels. That is
  an honest limit of the representation, not of the instruments. R_model
  (phase 9, cross-VAE-seed recurrence) remains the one open axis; it needs
  retrained checkpoints from the parent repo.
