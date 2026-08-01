# All-params blind SR — TT-only (`models/lcdm_tt_beta3e-4`, L=5, amplitude latent z2)

**Design.** The reference blind-SR study exposes PySR to the raw pair `(A_s, tau)` and targets the single amplitude latent selected by the disentanglement audit. That leaves two human-made choices in the loop: *which inputs* and *which latent*. This experiment removes both for completeness of the blindness: PySR receives **all 6 raw LCDM parameters** (`omega_b, omega_cdm, H0, tau, A_s, n_s` — no derived columns) and is run against **every latent** of this model (5 latents x 5 PySR seeds; the companion regime is consolidated in its own file by the same script). Everything else is protocol-identical to the reference study: gmm_mi pure-Julia inner loss, 200 iterations, 15 populations, maxsize 20, 5000 samples (4000 fit / 1000 val), operators `exp, log, neg, square` / `+, *, -, /`, post-hoc ranking by held-out GMM-MI.

Under the bijection-invariant MI loss the search must now also do **variable selection**: nothing tells it which of the 6 parameters a latent encodes. And because the encoder posterior means are *deterministic* functions of the 6 parameters (spectrum -> encoder is a fixed map), once all inputs are exposed the val MI is no longer capped by marginalising over hidden parameters — it keeps rising along the Pareto front as sub-dominant dependencies are absorbed (the reference study's 0.822 / 1.196 nat were exactly such marginalisation ceilings). The per-seed readout below is therefore the **top Pareto equation by val MI**. The complexity budget is a *search-time* hyperparameter, not a report-time filter: these runs use PySR `maxsize 20`; for a lower-complexity (reference-comparable) discovery, lower the budget and rerun — `sbatch --array=... hpc/slurm_allparams_sr.sh <run> "0 1 2 3 4" <maxsize>` — which concentrates the evolutionary search on small forms instead of post-hoc slicing a front evolved toward the cap.


## Cross-seed summary

| latent | audit-expected param | top MI (mean +/- std over seeds) | params in top forms |
|---|---|---:|---|
| z0 | omega_b | 3.337 +/- 0.048 | omega_b (5/5), omega_cdm (5/5), H0 (5/5), A_s (5/5), n_s (5/5), tau (2/5) |
| z1 | omega_cdm | 2.334 +/- 0.009 | omega_b (5/5), omega_cdm (5/5), H0 (5/5), tau (5/5), A_s (5/5), n_s (5/5) |
| z2 | amplitude (A_s, tau) | 3.843 +/- 0.110 | omega_b (5/5), omega_cdm (5/5), H0 (5/5), tau (5/5), A_s (5/5), n_s (5/5) |
| z3 | n_s | 3.064 +/- 0.020 | omega_b (5/5), omega_cdm (5/5), H0 (5/5), n_s (5/5), tau (4/5) |
| z4 | H0 | 3.620 +/- 0.105 | omega_b (5/5), omega_cdm (5/5), H0 (5/5), tau (5/5), A_s (5/5), n_s (5/5) |

## Per-latent results — top Pareto equation, every seed


### z0 — audit-expected: omega_b

| seed | c | val MI +/- err | top form (argmax val MI) |
|---:|---:|---:|---|
| 0 | 20 | 3.308 +/- 0.032 | `log((H0 + log(A_s)/omega_b)*(-0.42306665*n_s + omega_cdm - 0.31238765) + log(A_s**4))` |
| 1 | 19 | 3.375 +/- 0.031 | `log(omega_b/((-n_s + log(omega_cdm)/log(H0))*(log(A_s*omega_b*omega_cdm) - 1.0421232)))` |
| 2 | 20 | 3.320 +/- 0.032 | `log(log((n_s*(omega_b + omega_cdm - 0.53592473) + 0.08759481)*log(A_s*H0**2)/omega_b**2))` |
| 3 | 20 | 3.275 +/- 0.029 | `-tau + log(-(0.3918173*n_s - omega_cdm)*(H0*omega_b**2 - 0.22008736674409)*log(A_s)**2/omega_b**2)**2` |
| 4 | 20 | 3.408 +/- 0.030 | `log(n_s*(omega_b*(tau**2 + log(H0)) + 0.42078545496165*omega_cdm - 0.309611316267397)*log(A_s)/omega_b)**2` |

Cross-seed top MI 3.337 +/- 0.048 nat.

### z1 — audit-expected: omega_cdm

| seed | c | val MI +/- err | top form (argmax val MI) |
|---:|---:|---:|---|
| 0 | 20 | 2.317 +/- 0.033 | `tau + log(A_s*(omega_b + omega_cdm)**2*exp(-2*n_s)/(H0**2*omega_b**2*(0.379196304807849*n_s - omega_b - omega_cdm)**2)) - 1.93940250670758` |
| 1 | 20 | 2.339 +/- 0.037 | `log(-tau + log(H0**2*omega_b*(n_s - 0.5812182)**2/(A_s*(omega_b - 0.7249824*omega_cdm)**2)))` |
| 2 | 20 | 2.334 +/- 0.038 | `tau - log(H0**2*omega_b*(n_s - 0.20020296)**4/(A_s*(omega_b - 0.71547997*omega_cdm)**2)) + 0.669603349573972` |
| 3 | 19 | 2.345 +/- 0.038 | `-tau + log(H0**2*omega_b*exp(2*exp(n_s))/(A_s*(omega_b - 0.74252105*omega_cdm)**2)) - 0.595408117077581` |
| 4 | 20 | 2.334 +/- 0.036 | `-n_s + omega_cdm + tau + log(A_s*(omega_b - omega_cdm)**2/(H0**2*n_s**4*omega_b))` |

Cross-seed top MI 2.334 +/- 0.009 nat.

### z2 — audit-expected: amplitude (A_s, tau)

Reference study (inputs `A_s, tau` only): top form `A_s*(tau - 0.598)  (5/5 seeds)`, val MI 0.822 nat.

| seed | c | val MI +/- err | r(top) | top form (argmax val MI) |
|---:|---:|---:|---:|---|
| 0 | 19 | 3.776 +/- 0.027 | -1.958 | `log((tau + 0.44084883)**2*(H0*omega_cdm/n_s + 0.8925628)/(A_s**2*(omega_b + 0.02437031)))` |
| 1 | 20 | 3.860 +/- 0.031 | -1.957 | `log((0.5243555 - exp(tau))*(omega_b - 0.11740347)*log((H0*omega_cdm + 0.27881274)/n_s)/A_s)` |
| 2 | 20 | 3.965 +/- 0.034 | -2.000 | `log((H0*omega_cdm + 0.72941446)*exp(-n_s + 4*tau)*log(omega_b)**2/A_s**2)` |
| 3 | 19 | 3.946 +/- 0.031 | -1.967 | `omega_b - log((0.095370451258642*tau + 1)**2*log(A_s/log((H0*omega_cdm + 0.25786397)/n_s))**2) - 4.69997296748024` |
| 4 | 19 | 3.670 +/- 0.027 | -1.991 | `tau + log((tau + 0.9386916)*log(H0*omega_cdm/n_s)/(A_s*(omega_b + 0.070458256)))` |

Cross-seed top MI 3.843 +/- 0.110 nat.

**Implied tau exponent** r = (df/dtau)/(df/dlnA_s) at the prior midpoint (r = -2 iff the (A_s, tau)-dependence enters through `ln(A_s*e^(r*tau))`, any wrapper, any shape terms): -1.974 +/- 0.018 (n=5). Reference study's OLS readout of the same quantity: -1.988.

Scan over all 99 Pareto equations (same regexes as the reference study's section 3d): **12 strict textbook hits**, 0 expanded `A_s*tau` bilinear hits. No literal `exp(b*tau)` slope in [-2.5, -1.5] on any front.

### z3 — audit-expected: n_s

| seed | c | val MI +/- err | top form (argmax val MI) |
|---:|---:|---:|---|
| 0 | 19 | 3.046 +/- 0.030 | `omega_b - exp((H0*(-1.02594449476132*n_s - 2*omega_cdm + tau**3) - 2.8444552)/H0)` |
| 1 | 20 | 3.084 +/- 0.032 | `log(n_s**2*(omega_b + 0.11972135)*(omega_cdm + 0.11387834 + (1.46814067252101 - 0.757778693006044*tau)/H0))` |
| 2 | 20 | 3.055 +/- 0.035 | `log(n_s + log(2*omega_cdm + exp(3.2191007*omega_b - (tau - 2.6334786)/H0) - 0.31979164))` |
| 3 | 18 | 3.045 +/- 0.032 | `log(n_s - 2.6130590290296*omega_b/(18.7285698339675*omega_b - omega_cdm) + 2.6130590290296*omega_cdm + 2.8444176/H0)` |
| 4 | 20 | 3.093 +/- 0.034 | `n_s + log(n_s*(omega_b + 0.122276284)*(H0*(omega_cdm + 0.11773269) - 0.74755806*tau + 1.4393876)/H0)` |

Cross-seed top MI 3.064 +/- 0.020 nat.

### z4 — audit-expected: H0

| seed | c | val MI +/- err | top form (argmax val MI) |
|---:|---:|---:|---|
| 0 | 20 | 3.489 +/- 0.030 | `(-n_s - (log(log(H0)) + 0.39339703)*exp(tau) + log(A_s) + log((-0.44049197*omega_b + omega_cdm)/omega_b))/(log(log(H0)) + 0.39339703)` |
| 1 | 20 | 3.798 +/- 0.030 | `n_s - omega_cdm - log(A_s*H0*omega_cdm*(0.0432008270366328*H0 + 1)**2*exp(-2*tau)/omega_b) - 6.28379127909765` |
| 2 | 20 | 3.617 +/- 0.030 | `n_s - omega_cdm + log(omega_b*(tau + 0.43412754)/(A_s*H0**2*omega_cdm*log(H0)**2))` |
| 3 | 20 | 3.546 +/- 0.029 | `n_s - log(A_s*omega_cdm*(0.0726314836854435*H0 - 1)**2*(0.931192769474384*tau - 1)**2*exp(omega_cdm)/omega_b) - 5.38729151670046` |
| 4 | 20 | 3.653 +/- 0.030 | `-omega_cdm + log(omega_b*exp(n_s + 2*tau)/(A_s*H0**2*omega_cdm*log(H0)**2))` |

Cross-seed top MI 3.620 +/- 0.105 nat.

## Shuffled-target negative control (z2, all 6 inputs)

Identical PySR configuration, target column permuted across rows: quantifies the null MI floor with the enlarged input set (more inputs -> more room to overfit spurious MI).

| shuffle seed | best expr (by shuffled-target MI) | MI vs shuffled | MI vs TRUE | textbook form on front |
|---:|---|---:|---:|---|
| 0 | `-tau**2/(omega_b - 2.046*tau)` | 0.011 | 0.195 | no |
| 1 | `A_s*omega_b/(H0*log(log(-log(tau) - 0.8179436))*` | 0.020 | 0.164 | no |
| 2 | `-0.193282131152702*H0**4*(omega_cdm - 0.11879504` | 0.020 | 0.046 | no |

## What the runs show

**Every latent is a multi-parameter composite.** Cross-seed mean top MI spans 2.33-3.84 nat across the 5 latents (5/5 use >=5 of the 6 parameters in their top forms) — far above the single-parameter audit MIs, consistent with the encoder means being deterministic functions of the parameters. The audit's one-latent-one-parameter labels are the leading order of each latent, not the whole story: the amplitude latent's top MI (3.84 nat) is x4.7 the (A_s, tau)-restricted ceiling (0.822 nat) as SR absorbs the shape-sector dependencies the 2-input study marginalised over.

**The -2 reionization-suppression exponent survives full blindness.** The amplitude latent z2 carries the textbook -2 in every seed once read with the derivative ratio: r = -1.974 +/- 0.018 over 5 top forms; the literal exponential never surfaces — it is 99.9% linear over the prior, so the parsimony penalty always prefers its affine/rational surrogates. At maxsize 20 with all inputs exposed, the crisp two-variable textbook form is outcompeted on the front by higher-MI shape-blended composites; the derivative-ratio readout (not the literal-form scan) is the right instrument for the exponent. Forcing the *selection* of a low-complexity form is a search-time budget cut (rerun with a smaller maxsize), not a post-hoc filter of this front.

**The control stays null.** Best MI against the shuffled target <= 0.020 nat over 3 shuffle seeds, no textbook structure on any control front. Evaluated against the TRUE latent those same expressions reach at most 0.195 nat vs 3.84 for the real runs — the enlarged search space does not hallucinate the result.

_Runtime: 25 SR runs (5 latents x 5 seeds), mean fit 303 s at 16 threads (reference study: ~340 s)._


---
_Generated by `scripts/consolidate_allparams.py` from `results/lcdm_tt_beta3e-4/allparams/*/report.json`. Runs: `hpc/slurm_allparams_{encode,sr,control}.sh`; per-latent cross-seed pooling in `results/lcdm_tt_beta3e-4/allparams/pooled_z<k>/`._
