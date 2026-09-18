<!-- Text of findings_atlas.html, kept in step with it (regenerate with
     scripts/html_to_markdown.py). Interactive charts appear as *[...]*
     placeholders; the one static figure is the report's F4.1 render in
     figures/, referenced directly rather than duplicated here. -->

# Symbolic regression on CMB β-VAE latents

## 0 · The study in one page — The question, the probe, and the results

**The question.** Earlier work showed that the latents of a β-VAE trained on CMB spectra line up with physical parameters. This extension study asked: starting from the six cosmological parameters alone, can a blind search recover the exact formula each latent computes, and can we assign physical meaning to that formula? “Blind” means the search is never told the answer, and every threshold was fixed before the results were seen.

**The probe.** Two of the six parameters, the primordial amplitude A_s and the reionization optical depth τ, are famously degenerate: at all but the largest angular scales the spectrum depends on them only through the product A_se^{−2τ}. The one place this breaks is large-scale polarization, the reionization bump at multipoles ℓ < 30 in the EE spectrum. That gives a probe with a known answer. A network that sees only temperature above ℓ = 30 can only ever learn the product; a network that also sees low-ℓ polarization could learn the two separately.

- **STAGE 1 · Discovery search** — A recurring formula for every latent, the −2 found five ways, and polarization shown to split the amplitude information rather than copy it. Ten of eleven latents earn “primarily interpreted”.
- **STAGE 2 · A pre-registered linear baseline** — A plain seven-number linear fit matches or beats the discovered formulas for most latents, on reconstruction and on information alike. But the search never generated the linear candidate.
- **STAGE 3 · Search what the linear fit leaves** — An exact quadratic closes most of the remainder for nine latents. On the two it cannot, the search finds a pole in *τ* and a rational curvature that no polynomial expresses.
- **STAGE 4 · Look inside the encoder** — One latent alone reads the reionization window. The temperature-only network discards the amplitude split at its final compression step.

**Results, in short.** The blind search recovered a formula for every latent, found the −2 five independent ways, and showed that adding polarization splits the amplitude information across two latents instead of copying it. Then a control registered before the results were known, a plain linear fit with one weight per parameter, matched or beat the discovered formulas for most latents. The latents are, to about 99.8% of their variance, weighted sums of the six parameters — plausibly because in the log-spectrum basis the leading physics is additive. What lies beyond the sum is small but real: an exact quadratic closes most of it for nine latents, and the search proved its worth on the remaining two. Finally, gradients through the encoder show exactly where the degeneracy-breaking information enters and where it is lost.

The original aim, a certified formula per latent, is out of reach for this data by construction rather than for lack of searching. Over the narrow parameter box the linear part dominates each latent’s variance, and reconstruction accuracy cannot tell a discovered formula from the linear fit for eight or nine of the eleven latents.

## 1 · Setup

Both compressors are stored checkpoints from the parent reproduction of Piras, Herold, Lucie-Smith & Komatsu (2025). They were trained on the same 500,000 spectra computed by the CLASS Boltzmann code over a space-filling design in the six parameters below. Spectra are handled as log_{10} of the power at each multipole, relative to a reference spectrum and standardised per ℓ.

- **TT-only**: one encoder, **5 latents**, sees the temperature spectrum over ℓ ∈ [30, 2500].
- **TT+EE-lowl**: two encoders, **6 latents**, sees the temperature spectrum and the EE polarization spectrum over ℓ ∈ [2, 2500], reionization bump included.

For each latent k the encoder outputs a mean μ_k(θ) and a variance. The object interpreted throughout is the mean, a deterministic function of the six parameters θ, evaluated on the 50,000 spectra of the held-out test set. The noisy version Z_k is used once, to measure how much information a latent physically transmits.


| parameter                  | symbol        | range sampled  | sector    |
| -------------------------- | ------------- | -------------- | --------- |
| baryon density             | ω_b          | 0.020 – 0.024 | shape     |
| cold-dark-matter density   | ω_{cdm}      | 0.100 – 0.130 | shape     |
| Hubble constant            | H_0           | 62 – 80       | shape     |
| reionization optical depth | τ            | 0.01 – 0.13   | amplitude |
| primordial amplitude (log) | ln 10^{10}A_s | 2.90 – 3.18   | amplitude |
| primordial tilt            | n_s           | 0.92 – 1.01   | shape     |

> The ranges are narrow: the shape parameters vary by ±9–13%. That matters in Stage 2. The search receives the six raw parameters and nothing else; the combination A_se^{−2τ} is never computed anywhere in the pipeline. The amplitude is sampled as ln 10^{10}A_s but handed to the search in linear scale, so discovered formulas print A_s; the linear fits of Stage 2 use the sampled log form.

### Blind symbolic regression, scored by mutual information

**Symbolic regression** (SR) searches over formulas built from the inputs, constants and a fixed operator set (+, −, ×, ÷, exp, log, square), evolving a population of candidate expressions and keeping, for each formula **size** (the number of nodes in its expression tree), the best one found. The engine is PySR. Each search is repeated with five random seeds.

The unusual choice is the score. Formulas are ranked not by fit error but by **mutual information** (MI) with the latent. MI is unchanged by any invertible transformation, so a formula and its logarithm score the same. The search is therefore rewarded for the right *dependence* on the parameters, never for matching units, and the answer is a *family* of equivalent formulas.

The 50,000 test rows are split into **search rows** (the first 5,000; 4,000 to fit, 1,000 to validate), **calibration rows** (the next 20,000, used to fit every calibration and audit after the search) and **confirmation rows** (the last 25,000, opened once to compute the reported numbers).

> **Reading the numbers.** **NMSE** is the fraction of a latent’s variance a fit leaves unexplained, in percent; 0 is perfect. **MI** is in nats; real signals here are 1–4 nat and the nulls are below 0.07 nat. **Fractions of a ceiling**, written η, compare a formula’s MI with some maximum; 1 means the ceiling is reached. A **calibration** is a fitted one-dimensional monotone map that converts a formula’s output into the latent’s units.

## 2 · Stage 1 — Discovery search

Does each latent have a recoverable formula, does that formula account for the latent, and does the network find the known physics?

Blind SR with all six inputs on every latent (143 searches over three size limits); a sweep of the search’s own settings (72); a second search on what each formula left behind, repeated with the first formula exposed as an extra input (61); and an exhaustive screen of all 63 non-empty input subsets, rerun with a sham-input control (3,465 cells plus 165 sham runs).

**Figure 1 — Each latent has a dominant parameter, visible before any search**

*[interactive chart: `ch-roles`]*

Mutual information between each latent’s mean and each raw parameter, in nats (darker is more). Read along a row to see what a latent responds to; the dominant parameter is that latent’s **role**, fixed here and used as the expectation for everything downstream. The boxed columns are the amplitude pair: in TT-only **one** latent (z_2) responds to it, in TT+EE-lowl **two** do, z_4 anchored to τ and z_5 to the combination. Calibration rows, 8,000-row subsample.

*Source: report F2.2 · figures/_cache_audit_mi.npz*

Every latent yields a formula that recurs across seeds. Two things were not expected. First, the hope that shape latents would be free of (A_s, τ) and amplitude latents free of the shape parameters did **not** materialise at the level of *which inputs appear*: every latent’s best formulas use at least five of the six parameters, and the TT H_0 latent’s formula, A_sH_0^2ω_{cdm}e^{−2τ}, carries the amplitude combination inside it. Second, the information keeps growing with formula size for every latent instead of saturating at a small formula. Separation did hold at the level of the *leading direction*: five independent instruments — the raw MI of Figure 1, the search’s sensitivity signatures, the first inputs a fit-error search recruits, the decoder analysis, and the dominant weights of the linear fit of Stage 2 — agree on which parameter dominates each latent, all eleven times.

**Figure 2 — Information keeps growing with formula size, far above the null**

![Per-latent curves of validation mutual information against formula complexity for both networks, with the shuffled-target null band near zero and a dashed marker at the one-standard-error knee.](../figures/F4_1_envelopes.png)

For each latent, the MI of the best formula found as a function of the size limit (heavy line; faint lines are the three size-limit families it pools). The dashed vertical marks where more size stops adding information within one standard error. The grey band at the bottom is the null: the same search on a randomly permuted latent reaches at most 0.06 nat, against real values of 1.8–4.3 nat. Search rows.

*Source: report F4.1 · experiments/knee_readout_*.json*

### The physics check: the exponent −2, recovered blind

The exponent in A_se^{−2τ} is the one number in this study whose value is known in advance, so it is the calibration of the whole method. Nine readings were taken. Five come from the encoder side and are independent of each other; they land on −2. Two come from the decoder side, where the spectrum’s responses to τ and to lnA_s are almost exactly antiparallel (template cosine −0.9996 in TT), so the fitted ratio slides along a ridge and gives no reading at all — that is the degeneracy of the one-page summary seen from the other side, and it returns in Stage 4.

**Table 1 — Nine readings of the ratio of a formula’s sensitivity to τ and to lnA_s; the textbook value is −2**

| readout | value | source |
| --- | --- | --- |
| Discovered formula, EE amplitude latent: A_s exp(−2τ), 5 of 5 seeds | −2 (exact) | report §2.3 readout 1 |
| Derivative ratio ∂f/∂τ ÷ ∂f/∂lnA_s over the best formulas, TT-only | −1.974 ± 0.018 | readout 2, every seed and sweep setting |
| Same derivative ratio, TT+EE-lowl | −1.993 ± 0.008 | readout 2 |
| Frozen constant-ratio detector, scanning all parameter pairs unprompted | −2.0000, the (τ, lnA_s) pair emerges | readout 3 |
| Second formula of the EE H_0 latent, A_s exp(−2τ) / ω_b², found twice | −2.0000 | readout 4, unplanned |
| Linear-fit weight ratio, TT-only: 8.42 (lnA_s − 1.979 τ) | −1.979 | readout 5, Stage 2 |
| Linear-fit weight ratio, TT+EE-lowl: 8.97 (lnA_s − 1.997 τ) | −1.997 | readout 5, Stage 2 |
| Decoder decomposition, TT+EE-lowl: −2.32 to −1.67 across fit variants | ridge, no readout | report §2.5; template cosine −0.9902 |
| Decoder decomposition, TT-only: −2.85 to +0.60 | ridge, no readout | report §2.5; template cosine −0.9996 |

*Source: report §2.3, §2.5 · experiments/allparams_blind_sr_*.json, latent_cards_*.json, decoder_effect_*.json*

The combination is never computed anywhere in the pipeline, so readouts 1–4 are the search building it from the raw parameters unprompted. Readout 5 shows that a linear probe in the sampled basis reads the same structure; what the blind search added is that it located the combination without being handed the logarithm.

### Each formula uses its inputs fully, yet misses much of the latent

“Accounts for the latent” needs a definition. Three ratios were used, each a formula’s MI divided by a ceiling:

1) η_S divides by the best MI any formula restricted to the *same input variables* achieved in the exhaustive 63-subset campaign (does the formula extract everything its own variables offer?)
2) η_{plat} divides by the best MI achieved with all six inputs at the largest size (what fraction of the searchable map is it?)
3) η̂_{post} divides by the information the latent *physically transmits*, measured from its noisy version (what fraction of what the latent stores does the formula carry?).

**Figure 3 — Every first formula exhausts its own inputs and carries 29–84% of what its latent stores**

*[interactive chart: `ch-eta`]*

The light circles (η_S) sit on the line at 1 for every latent: each formula exhausts its own inputs. The dark diamonds (η̂_{post} of the first formula) sit well below 1. That gap is the result. The positive control passes: the amplitude pair is rediscovered among the 63 subsets with no special treatment and saturates its ceiling. EE z_4’s 1.07 reflects noise in the ceiling estimate, not a real excess.

*Source: report F5.1 · experiments/latent_cards_*.json*

The remainder was then tested directly. After a calibration that maps each formula onto its latent, the leftover is still predictable from the six parameters at R^2 of 0.96–0.99, against nulls of about ±0.002. The frozen rule required R^2 ≤ 0.05, and that is the informative outcome: the amplitude latents have signal-to-noise of several thousand, so their leftover is stored information, not noise. A second blind search on the leftover gives a second formula f_2 per latent.

**The pair does not complete the picture.** Every latent gains — f_1 and f_2 together carry 59–96% of the information the latent stores, against 29–84% for f_1 alone — but no latent reaches 1, and what is left after two formulas is itself still predictable from the same six parameters. Re-running the second search with the first formula available as a seventh input returns the same second formula for 8 of 11 latents, and confirms, for the TT amplitude latent, that its amplitude and shape information combine multiplicatively, which an additive two-formula account cannot absorb. The hierarchy of formulas does not terminate; Stage 3 puts a number on what remains.

### The intervention test

Association is not the same as being the latent’s coordinate. The defining test is an intervention: hold the formula’s value fixed, move every other parameter direction as far as possible, and measure how much the latent moves. Pairs of parameter settings with equal formula value are drawn, and the **invariance error** is the mean squared latent difference within pairs, scaled so that randomly matched pairs score 1; the frozen rule requires ≤ 0.05. The first formula alone fails everywhere (0.05–0.23). Holding the pair (f_1, f_2) fixed brings the error down by about an order of magnitude and passes for 7 of the 8 latents on which it can be run, the exception being EE z_0 at 0.060 ± 0.002. For three TT latents the two formulas between them use all six parameters, leaving nothing to vary; those are recorded as untestable (†), not as passes. The nulls sit far away: shuffled formulas and formulas transferred to the wrong latent score 0.2–2.8.

### Adding polarization splits the amplitude information rather than copying it

Two latents respond to the amplitude pair in TT+EE-lowl, one in TT (Figure 1). The two are not copies. If they were, knowing one would make the other uninformative; instead, conditioning on z_5 *raises* the information z_1 holds about the combination from 0.013 to 0.473 nat, and no pair of latents in either network is redundant. Each first formula can be read off its own latent by a linear probe (rank-correlation R^2 0.88–0.95), while the second formulas cannot be read off any single latent: they are spread across the latent space. None of this depends on the symbolic search.

### The results

**Table 2 — The atlas as frozen: one row per latent**

> *Size* is the number of nodes in the formula. *Seeds* is how many of the five search seeds returned a formula equivalent to f_1. The two *stored-info* columns are η̂_{post} for the first formula and for both. *Invariance* is the intervention test for the pair; † means the pair uses all six parameters and the test cannot be run. **“Primarily interpreted”** was defined in advance as: a first formula that recurs across seeds and exhausts its own inputs, a documented second formula, and a passed intervention test for the pair, while the leftover is still structured. It does **not** say the latent is explained (no latent met the full bar, which requires an unstructured leftover), and, as Stage 2 shows, it does not say the pair does better than a plain linear fit.


| network | z | role      | first formula f_1                | size | seeds | η_S | stored info, f_1 | second formula f_2                         | stored info, f_1+f_2 | invariance, pair | status                    |
| ------- | - | --------- | -------------------------------- | ---- | ----- | ---- | ---------------- | ------------------------------------------ | -------------------- | ---------------- | ------------------------- |
| TT      | 0 | ω_b      | n_s/ω_b                         | 3    | 5/5   | 1.00 | 0.53             | n_s(H_0 + 1325 ω_{cdm})                   | 0.90                 | 0.022            | **primarily interpreted** |
| TT      | 1 | ω_{cdm}  | H_0^2n_s^2ω_b / (A_sω_{cdm}^2) | 10   | 4/5   | 1.00 | 0.77             | n_s / ln(−H_0/(τ − 0.447)) + ω_b       | 0.96                 | n/a †           | **primarily interpreted** |
| TT      | 2 | amplitude | A_s / ln(H_0(ω_{cdm} + τ))     | 8    | 5/5   | 1.00 | 0.35             | n_s^2ω_bτ / (ω_{cdm}τ + 3.1×10^{−4}) | 0.60                 | n/a †           | **primarily interpreted** |
| TT      | 3 | n_s       | n_s + ω_{cdm}                   | 3    | 5/5   | 1.00 | 0.45             | H_0 / (ω_b^2ω_{cdm}^2)                   | 0.84                 | 0.013            | **primarily interpreted** |
| TT      | 4 | H_0       | A_sH_0^2ω_{cdm}e^{−2τ}        | 9    | 4/5   | 1.00 | 0.37             | ln(H_0) / (n_sω_b)                        | 0.76                 | n/a †           | **primarily interpreted** |
| TT+EE   | 0 | ω_{cdm}  | ω_{cdm} / (H_0n_sω_b)          | 7    | 5/5   | 1.00 | 0.76             | A_sH_0ω_{cdm} / n_s                       | 0.84                 | 0.060            | **unresolved**            |
| TT+EE   | 1 | H_0       | H_0^2ω_{cdm}                    | 4    | 5/5   | 1.00 | 0.35             | A_se^{−2τ} / ω_b^2                      | 0.66                 | 0.023            | **primarily interpreted** |
| TT+EE   | 2 | ω_b      | ω_b / n_s^2                     | 4    | 5/5   | 1.00 | 0.57             | n_s(A_s + 1.04×10^{−5} ω_bω_{cdm}^2)   | 0.96                 | 0.014            | **primarily interpreted** |
| TT+EE   | 3 | n_s       | ln(ω_b) / (n_s + ω_{cdm})      | 6    | 4/5   | 0.99 | 0.49             | H_0 / ω_{cdm}^2                           | 0.86                 | 0.014            | **primarily interpreted** |
| TT+EE   | 4 | τ        | −A_s / (τ − 0.445)            | 5    | 5/5   | 1.07 | 0.84             | τ                                         | 0.84                 | 0.031            | **primarily interpreted** |
| TT+EE   | 5 | amplitude | A_se^{−2τ}                     | 5    | 5/5   | 1.00 | 0.29             | H_0ω_{cdm} / n_s                          | 0.59                 | 0.029            | **primarily interpreted** |

*Source: report Table 2.7 · experiments/latent_cards_*.json*

Beyond the atlas, the exhaustive subset campaign returned a mixed result: in TT, adding an uninformative sham input measurably degrades the search (dilution), yet almost no restricted input set beats the full six; in TT+EE-lowl five restricted sets do beat the full six, by 0.09–0.13 nat, yet the sham control shows no dilution. No status changed.

### Two warning signs

The sweep of search settings showed raising the size limit alone moves MI from 1.6 to 4.05 nat, while the MI read off at a fixed size of 10 nodes is flat across every setting. And a later fit-error study showed that the **seeds stop agreeing as size grows**: at size ≤ 5, seven of eleven latents have all five seeds on the same algebraic family; at size ≤ 40 the dominant family usually holds only 2–3 of 5, while accuracy is saturated. Capacity buys fit, not discovery. Stage 2 explains both.

## 3 · Stage 2 — A plain linear fit as the baseline

How much of what the symbolic search found would a trivial model also find?

A follow-up study that searched with fit error instead of MI (165 searches at size limits 20, 30 and 40, plus 12 controls) carried, as a pre-registered control, an **ordinary least-squares** (OLS) fit: the latent as a weighted sum of the six parameters plus an offset, seven numbers, fitted on the 4,000 search rows and scored on the confirmation rows. When that control turned out to matter, three possible artefacts were tested in turn: unfair units (an identical calibration was applied to both sides), single-precision arithmetic and badly scaled inputs (330 searches rerun in double precision with three input conventions), and the linear fit being denied the log-amplitude input (a coordinate-matched audit refits OLS in each convention’s own inputs). Two further measurements followed: replaying the stored search results with the OLS formula injected, and computing for the OLS fit the same stored-information fraction that had been computed for every discovered formula.

**The result on both endpoints.** On reconstruction, in the search’s own raw-parameter convention the linear fit beats the best size-40 symbolic formula for 9 of 11 latents, and it still wins 6 to 5 in the search’s most favourable convention (double precision, inputs rescaled to order one). On information, measured the same way as η̂_{post} in Table 2, it carries more of what the latent stores than f_1 for **10 of 11** latents and more than the two-formula account for **9 of 11**, with no violation of the data-processing inequality. The single latent where the symbolic account wins on both endpoints is EE z_4 — the same latent Stage 3 finds genuinely non-polynomial.

*Source: report F12.1 · experiments/coordinate_matched_ols_v1.json (logamp64 arm), eta_post_ols_index_v1.json*

### Why the search lost

The stored fronts were replayed with the exact linear formula, written as a 25-node expression, injected into the candidate pool:

- **38 / 55** — size-40 searches in which the linear fit beats *every* formula on the front, at any size the search explored
- **43 / 55** — searches in which the injected linear formula would have been kept by the unchanged selection rules
- **39 / 55** — searches in which it would have been chosen outright

The rules never discarded a linear candidate; the search never produced one. The failure is generative: a stochastic search over formula trees does not reliably assemble a six-term weighted sum, even when it can represent it within the allowed complexity. The 16 searches where the symbolic formula legitimately wins are exactly the latents where nonlinearity is real (all seeds of EE z_3 and EE z_4, some of EE z_2 and z_5, one of TT z_3).

With τ and lnA_s as two separate, unconstrained inputs, the linear fit’s amplitude weights come out as 8.42 (lnA_s − 1.979 τ) for the TT amplitude latent and 8.97 (lnA_s − 1.997 τ) for the EE one: the fifth readout of Table 1.

### This does not mean the latents are linear

What the linear fit leaves behind is itself 97–99% predictable from the same six parameters by gradient boosting, a flexible nonlinear regressor used here only as a measuring instrument: its own leftover is the **floor**, the best any method could hope for on this data. Both the linear fit and the 40-node formula sit about two orders of magnitude above that floor. The mean maps are smooth, essentially deterministic, genuinely nonlinear functions of the parameters, whose *linear part dominates the variance* because the parameter box is narrow, while their nonlinear part is tiny in variance and enormous in signal-to-noise.

**Table 3 — The nonlinear part of each latent, in variance and in spread**

| network | z | role | linear fit leaves (NMSE) | gradient boosting then leaves | ratio | nonlinear part, % of spread | floor, % of spread | of the leftover, predictable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TT-only | 0 | ω_b | 0.186% | 0.0024% | 75× | 4.25% | 0.49% | 98.7% |
| TT-only | 1 | ω_{cdm} | 1.39% | 0.0229% | 60× | 11.7% | 1.51% | 98.3% |
| TT-only | 2 | amp | 0.044% | 0.00084% | 53× | 2.13% | 0.29% | 98.1% |
| TT-only | 3 | n_s | 0.214% | 0.0023% | 93× | 4.65% | 0.48% | 98.9% |
| TT-only | 4 | H_0 | 0.040% | 0.00041% | 94× | 1.97% | 0.20% | 98.9% |
| TT+EE-lowl | 0 | ω_{cdm} | 3.95% | 0.093% | 43× | 20.0% | 3.06% | 97.7% |
| TT+EE-lowl | 1 | H_0 | 0.095% | 0.00079% | 114× | 3.01% | 0.28% | 99.1% |
| TT+EE-lowl | 2 | ω_b | 0.171% | 0.0034% | 50× | 4.12% | 0.58% | 98.0% |
| TT+EE-lowl | 3 | n_s | 0.311% | 0.0052% | 60× | 5.57% | 0.72% | 98.3% |
| TT+EE-lowl | 4 | τ (amp) | 4.18% | 0.043% | 99× | 20.7% | 2.07% | 99.0% |
| TT+EE-lowl | 5 | amp | 0.045% | 0.0013% | 34× | 2.12% | 0.36% | 97.1% |

> Linear fit in the sampled basis, coefficients from the search rows; gradient boosting trained and scored on disjoint calibration rows. *Nonlinear part* is the root-mean-square size of what the linear fit leaves, as a percentage of the latent’s standard deviation; *floor* is the same for what gradient boosting leaves. The two quantities NMSE conflates are visible side by side: the nonlinear part’s variance share is tiny, its signal-to-noise (the ratio column) is 34–114×.

### Why a linear fit is the right physics here

The networks compress the *logarithm* of the spectrum, and in that basis the leading responses are additive by construction. Above the reionization regime the spectrum is proportional to A_se^{−2τ}, so its log is *exactly* linear in lnA_s and τ, at any prior width. The tilt enters as (n_s − 1) times a fixed function of ℓ. The shape-sector responses are smooth over a ±9–13% box, with curvature entering at the percent level. The genuine nonlinearities are localised: the low-ℓ polarization bump, lensing, and whatever warping the encoder itself adds. A near-linear latent is therefore the correct account of this data, not a failed one, and the places where the symbolic search genuinely beat the linear fit (Stage 3) are exactly where the physics is nonlinear and the box makes it visible. Widening the box would change the shape sector and little else, which is why a wider-prior campaign was set aside as a question of scope rather than run.

### Two accounts of the same latent

Every latent now has two descriptions, and they are not competing entries on one scale. They are built differently, chosen differently and scored differently:

|                              | Stage 1: the symbolic pair                                                   | Stages 2–3: the ladder                                                                                  |
| ---------------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| built from                   | f_1, then f_2 on what f_1 leaves, each with a fitted monotone calibration     | 7 linear coefficients, then 21 quadratic ones, then a formula on what the linear fit leaves                 |
| how the pieces were chosen   | stochastic search, ranked by mutual information                              | exact least squares; the search is used only on the two leftovers the quadratic cannot close               |
| scored by                    | η̂_{post}, the fraction of the information the latent stores (0–1, higher better) | NMSE, the share of the latent’s variance left unexplained (%, lower better)                                |
| answers                      | which coordinates the network uses, and whether the known physics is recovered | how much of the latent each class of function can actually reproduce                                       |
| reported in                  | Table 2                                                                      | Tables 3–5                                                                                                 |

The two meet at one comparison, made on the same rows with the same instrument: the seven-number linear fit carries more of what the latent stores than f_1 for 10 of 11 latents and more than f_1 + f_2 for 9 of 11 (the exceptions are TT z_1, where the pair wins narrowly, and EE z_4). So Stage 1 is the **discovery record** — what a blind search finds, and the five readings of the −2 — and Stages 2–3 are the **account of record** for how much of each latent is actually described. The formulas of Table 2 are not superseded as findings; they are superseded as descriptions. For that reason f_1 is not a rung on the Stage-3 ladder: it is a different decomposition of the same latent, and it appears there only as a reference point.

> **Takeaway.** A pre-registered seven-number linear fit matches or beats the discovered formulas for most latents on reconstruction and on information, and the stored search results show why: the search never generated a linear candidate it could represent. The latents are not linear, but their linear part dominates the variance over a narrow box, so reconstruction accuracy is a weak discriminator here, and a matched classical baseline is a mandatory control for symbolic interpretation of latents.

## 4 · Stage 3 — Searching what the linear fit leaves behind

Accepting that the linear part is the physics, is there any compact formula in what remains?

A ladder of hypothesis classes, **linear** (7 coefficients, exact least squares) → **quadratic** (the same plus all 21 products and squares of the six parameters, 28 coefficients, still exact least squares; run on all 11 latents) → **symbolic search on the leftover of the linear fit**, run only where the quadratic left the gap open. The logic: exhaust what exact solvers can express, so that when the unreliable stochastic search is finally spent it is pointed at a target already proven to be beyond cheaper classes.

**Table 4 — The nonlinearity ladder: nine latents close at second order, two do not**

| network | z | role | linear | quadratic | gap closed | leading second-order terms |
| --- | --- | --- | --- | --- | --- | --- |
| TT-only | 0 | ω_b | 0.186% | 0.0118% | 94% | ω_bω_{cdm}, ω_b² |
| TT-only | 1 | ω_{cdm} | 1.39% | 0.930% | 33% | τ², H_0² |
| TT-only | 2 | amp | 0.044% | 0.0138% | 69% | ω_{cdm}², ω_b² |
| TT-only | 3 | n_s | 0.214% | 0.0377% | 82% | ω_b², ω_{cdm}² |
| TT-only | 4 | H_0 | 0.040% | 0.0026% | 94% | ω_{cdm}², H_0² |
| TT+EE-lowl | 0 | ω_{cdm} | 3.95% | 3.78% | **4%** | H_0², ω_bH_0 |
| TT+EE-lowl | 1 | H_0 | 0.095% | 0.0271% | 72% | ω_{cdm}², H_0² |
| TT+EE-lowl | 2 | ω_b | 0.171% | 0.0517% | 70% | H_0², τ² |
| TT+EE-lowl | 3 | n_s | 0.311% | 0.0956% | 69% | ω_b², ω_{cdm}² |
| TT+EE-lowl | 4 | τ (amp) | 4.18% | 3.87% | **8%** | ω_{cdm}τ, H_0τ, ω_bτ |
| TT+EE-lowl | 5 | amp | 0.045% | 0.0216% | 52% | ω_b², ω_{cdm}n_s |

> Unexplained variance on the confirmation rows; *gap closed* is the share of the beyond-linear gap the 21 quadratic terms remove. For nine latents they close 33–94%, and after this rung the quadratic beats the size-40 symbolic winner everywhere except EE z_4. The terms that carry the gain name the physics: squares and cross-terms of the shape parameters, the curvature of the acoustic-peak heights, with τ² and τ cross-terms where the amplitude sector enters. TT z_1’s large remainder is plausibly noise-limited; it is the latent with the lowest signal-to-noise, 5. The two latents in bold are the ones handed to the search.

*Source: report F13.1, Table 4.1 · experiments/coordinate_matched_ols_v1.json, capacity_and_noise_floor_v1.json; the linear and quadratic rungs refitted from data/ and models/*

**Table 5 — What the search finds on the leftover of the linear fit, for the two latents the quadratic cannot close**

|                                                         | EE z_0 (ω_{cdm}, unresolved)                 | EE z_4 (τ)             |
| ------------------------------------------------------- | --------------------------------------------- | ----------------------- |
| MI between the found formula and the leftover, per seed | 0.50 – 0.54 nat                              | 0.77 – 0.89 nat        |
| the same search on a permuted leftover                  | 0.066 – 0.072 nat                            | 0.051 – 0.056 nat      |
| seeds agreeing                                          | 4 of 5                                        | 5 of 5                  |
| the formula (size)                                      | (ω_{cdm} / (ω_b(H_0 − 85.5)))^2 (8)        | A_s / τ (3)            |
| relation to the Stage-1 second formula                  | a different direction (rank correlation 0.58) | the same family (0.986) |
| linear + formula, fixed monotone calibration            | 3.75%                                         | 2.41%                   |
| linear + formula, unrestricted 1-D map                  | 1.83%                                         | 1.30%                   |
| for comparison: linear → quadratic                     | 3.95% → 3.78%                                | 4.18% → 3.87%          |

Both latents carry a real, recurring coordinate beyond the linear fit, 7–14 times above the permuted controls. **EE z_4** is the compact answer: every seed lands in one family whose simplest member is A_s/τ, the ratio of amplitude to optical depth that governs the reionization bump; the combined account (seven linear weights, a three-node ratio, one calibration map) at 1.30% is the best reconstruction of that latent ever measured, against a previous best of about 1.4% and a quadratic wall of 3.87%. **EE z_0**, the one unresolved latent, yields a rational curvature of the shape parameters with a pole just outside the H_0 range, which no polynomial expresses, and something more useful: its relation to the leftover is strongly **non-monotone**, so the fixed monotone calibration converts half a nat of information into only 5% of the leftover while an unrestricted map converts it into 54%. That is why every earlier account of this latent, all monotone by rule, had stalled.

**What the ladder settles.** All eleven latents were answered: nine are essentially closed at second order, two were characterised by the search.

> **Takeaway.** Exhaust the exact classes first. An exact quadratic settles nine latents in minutes, and the stochastic search, pointed only at the two targets proven to be beyond it, finds real non-polynomial structure exactly where the physics predicts it: a pole in τ at the reionization latent, a rational curvature at the one latent that had never been resolved.

## 5 · Stage 4 — Looking inside the encoder

Where, in the network, does the degeneracy-breaking information enter, and where is it lost?

Three instruments borrowed from the interpretability of large language models were run on the encoders. **Gradient attribution**: the derivative of each latent’s mean with respect to every input bin, one backward pass per latent, at 64 anchor spectra. **A layer-wise probe**: how well each parameter, and the combination lnA_s − 2τ, can be read off linearly from the standardised input, from each of the encoder’s three convolutional blocks (the *trunk*), and from the latent means themselves (the *bottleneck*). **Input optimisation**: search for the smallest change to a spectrum that moves one latent while holding the others, and compare that change with the spectrum’s physical responses. A caveat was measured first: a spectrum has about 5,000 bins, but only six directions in that space can be produced by changing cosmology, and only 0.03–1.3% of each latent’s gradient lies along them. The readout used is the gradient **projected** onto those six physical directions, the part an actual change of cosmology could excite.

**Figure 4 — One latent alone reads the reionization window**

*[interactive chart: `ch-reion`]*

The share of each latent’s projected gradient that falls in the reionization window ℓ < 30 of the EE spectrum, for the TT+EE-lowl network. Those 28 bins are 0.56% of all bins (dashed line). EE z_4 puts **24%** of its projected gradient there, against 0.3–1.0% for every other latent: about 43 times the uniform share, while everything else sits at or below uniform. It is z_4 alone that reads the bump, not z_4 and z_5 together, which is the expected physics: the bump constrains τ, and A_s then follows from the amplitude at high ℓ. The TT-only network has no bins below ℓ = 30 and is exactly zero there.

*Source: report F14.1a · experiments/encoder_gradient_attribution_lcdm_tt_ee_lowl.json*

**Figure 5 — Which multipoles each latent listens to, both networks and both channels**

*[interactive chart: `ch-bands`]*

Projected-gradient mass per multipole band, as a percentage of each latent’s total, so every row sums to 100 across the ten cells. The TT-only network has only the five temperature bands. The boxed column is the EE reionization window of Figure 4. Shape latents spread their mass over the acoustic-peak bands of both channels; the amplitude latents in TT+EE-lowl lean on the temperature channel above ℓ = 500, and only z_4 reaches into ℓ < 30.

*Source: experiments/encoder_gradient_attribution_*.json (bands_projected)*

**Figure 6 — The degeneracy is created at the bottleneck, and only in the network whose inputs cannot break it**

#### TT-only

*[interactive chart: `ch-probe-tt`]*

#### TT+EE-lowl

*[interactive chart: `ch-probe-ee`]*

Held-out R^2 of a linear read-out of τ, lnA_s and their degenerate combination at each depth of the encoder, from the input to the latent means; the four shape parameters are drawn in grey for context. Everything is linearly decodable from the raw input (R^2 ≥ 0.994) and stays so through all three convolutional blocks in both networks: the trunk loses nothing. The two networks part company only at the latent means. The TT network keeps the combination (0.997) and drops its constituents (τ to 0.41, lnA_s to 0.63); the TT+EE-lowl network keeps all three above 0.97. That is the same fact as Figure 4 seen from inside the representation. Calibration rows, 2,500 spectra.

*Source: report F14.1b · experiments/encoder_trunk_probe_*.json*

**Input optimisation is a clean negative.** Over all 44 combinations of latent and step budget, the direction that moves one latent while holding the others is essentially orthogonal to every physical response (largest cosine 0.01–0.13, median 0.05) while pushing the target latent by 3 to 800 standard deviations, far outside the ±3 it ever takes on real spectra, and taking smaller steps does not help. Unconstrained input optimisation finds adversarial directions the physics cannot produce, the same fact as the 0.03–1.3% on-manifold figure above. The instrument that works is the projected gradient at a real spectrum; steering would need an explicit constraint to the physical manifold, which is a different experiment.

> **Takeaway.** The degeneracy-breaking information enters through one latent, at the multipoles the physics says it should, and the temperature-only network discards the amplitude split at its final compression step rather than anywhere in its trunk. Two instruments carried over from language-model interpretability worked; the third, unconstrained steering, does not transfer without a manifold constraint.

## 6 · Conclusions — What stands, and what the symbolic search was for

**Claims that stand.**

- The amplitude sector organises as A_se^{−2τ}, and the −2 is determined five independent ways (Table 1).
- Each latent’s dominant parameter and input set are robust: five instruments agree, all eleven times (Figure 1).
- Adding polarization splits the amplitude information across two complementary latents rather than duplicating it; this is visible in the raw MI, in the latent-space conditionals, in the gradient bands and in the layer probe, and none of it needs the symbolic search (Stage 1, Stage 4).
- The latents are near-deterministic and close to linear over the parameter box, with real structure at every level probed: no account tried (two symbolic formulas, a 40-node formula, linear, quadratic) leaves an unstructured remainder (Stages 2–3).
- Where the search beat the linear fit it found real nonlinearity: the pole in τ and the coordinate A_s/τ at EE z_4, the rational curvature at EE z_0, and more moderately EE z_3 (Stage 3).
- Methodological lessons that transfer: the MI at the top of a front measures search capacity, not discovery; comparing an MI-selected formula with a fit-error one needs symmetric calibration; a single large formula hides rather than absorbs a known secondary coordinate; a matched classical baseline is a mandatory control for symbolic interpretation of latents; and held-out error cannot detect non-identification, while agreement across seeds can.
- The controls are clean: permuted-target searches ≤ 0.06 nat, permuted leftovers ≤ 0.074 nat against 0.40–1.77 real, intervention nulls 0.2–2.8 against passes ≤ 0.03, probe nulls at zero, and the residual audit honestly failed on the positive control.

**Table 6 — What the search could have been for**

|     | what the search could have been for                                                                       | verdict                                                                                                                                                         |
| --- | --------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `A` | Which parameter does latent k encode?                                                                     | **redundant** · the raw MI of Figure 1 answers it before any search                                                                                            |
| `B` | What *function* of the parameters is latent k? The stated aim.                                            | **mostly defeated** · for 8–9 of 11 latents the answer is “a weighted sum”, and the data cannot tell the discovered formula from the linear fit             |
| `C` | Does the network find a physically meaningful *combination*?                                              | **delivered** · A_se^{−2τ} is a derived degenerate combination, and the blind search built the logarithm itself, which a linear probe structurally cannot do |
| `D` | Where is the representation genuinely non-polynomial?                                                     | **delivered** · only the search answers this, and it did: EE z_4 and EE z_0, both where the physics says nonlinearity should live                              |
| `E` | Is the representation compressible into a small exact formula at all?                                     | **answered: no** · robustly, in every class probed; a finding, not a failure                                                                                   |
| `F` | What does blind symbolic regression on a scientific autoencoder establish, with a full control programme? | **delivered** · arguably the most transferable output                                                                                                          |

The search was hired to name the latents. Most latents turn out not to need naming: they are sums, and the name is the weight vector. What the search is demonstrably good for is narrower: finding the right basis when the natural coordinates are not the sampled ones, locating genuine non-polynomial structure once the cheap exact classes are exhausted, and being the subject of a control programme whose pre-registered baseline caught its own over-reading.
