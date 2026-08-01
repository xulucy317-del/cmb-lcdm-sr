# All-params blind SR — TT-only (`models/lcdm_tt_beta3e-4`, L=5, amplitude latent z2)

**Design.** The reference blind-SR study exposes PySR to the raw pair `(A_s, tau)` and targets the single amplitude latent selected by the disentanglement audit. That leaves two human-made choices in the loop: *which inputs* and *which latent*. This experiment removes both for completeness of the blindness: PySR receives **all 6 raw LCDM parameters** (`omega_b, omega_cdm, H0, tau, A_s, n_s` — no derived columns) and is run against **every latent** of this model (5 latents x 5 PySR seeds; the companion regime is consolidated in its own file by the same script). Everything else is protocol-identical to the reference study: gmm_mi pure-Julia inner loss, 200 iterations, 15 populations, maxsize 10, 5000 samples (4000 fit / 1000 val), operators `exp, log, neg, square` / `+, *, -, /`, post-hoc ranking by held-out GMM-MI.

Under the bijection-invariant MI loss the search must now also do **variable selection**: nothing tells it which of the 6 parameters a latent encodes. And because the encoder posterior means are *deterministic* functions of the 6 parameters (spectrum -> encoder is a fixed map), once all inputs are exposed the val MI is no longer capped by marginalising over hidden parameters — it keeps rising along the Pareto front as sub-dominant dependencies are absorbed (the reference study's 0.822 / 1.196 nat were exactly such marginalisation ceilings). The per-seed readout below is therefore the **top Pareto equation by val MI**. The complexity budget is a *search-time* hyperparameter, not a report-time filter: these runs use PySR `maxsize 10`; for a lower-complexity (reference-comparable) discovery, lower the budget and rerun — `sbatch --array=... hpc/slurm_allparams_sr.sh <run> "0 1 2 3 4" <maxsize>` — which concentrates the evolutionary search on small forms instead of post-hoc slicing a front evolved toward the cap.


## Cross-seed summary

| latent | audit-expected param | top MI (mean +/- std over seeds) | params in top forms |
|---|---|---:|---|
| z0 | omega_b | 2.083 +/- 0.016 | omega_b (5/5), omega_cdm (5/5), n_s (5/5) |
| z1 | omega_cdm | 1.170 +/- 0.050 | omega_b (5/5), omega_cdm (5/5), H0 (5/5), n_s (5/5), A_s (3/5) |
| z2 | amplitude (A_s, tau) | 1.419 +/- 0.138 | omega_cdm (5/5), tau (5/5), A_s (5/5), H0 (4/5) |
| z3 | n_s | 2.184 +/- 0.017 | omega_b (5/5), omega_cdm (5/5), n_s (5/5) |
| z4 | H0 | 1.276 +/- 0.024 | omega_cdm (5/5), H0 (5/5), tau (5/5), A_s (5/5) |

## Per-latent results — top Pareto equation, every seed


### z0 — audit-expected: omega_b

| seed | c | val MI +/- err | top form (argmax val MI) |
|---:|---:|---:|---|
| 0 | 9 | 2.081 +/- 0.028 | `omega_b/(n_s - 2.31715261798275*omega_cdm + 0.8230552)` |
| 1 | 10 | 2.067 +/- 0.028 | `0.21039343771968*omega_b/(0.458686644365934*n_s - 0.917373288731867*omega_cdm + 1)**2` |
| 2 | 10 | 2.065 +/- 0.031 | `0.225462970118993*omega_b/(0.474829411598516*n_s - 0.949658823197031*omega_cdm + 1)**2` |
| 3 | 8 | 2.090 +/- 0.029 | `omega_b*(-0.4488103*n_s + exp(omega_cdm))` |
| 4 | 9 | 2.109 +/- 0.028 | `-omega_b*(n_s*(omega_cdm + 0.12529756) + 0.40101779)/n_s` |

Cross-seed top MI 2.083 +/- 0.016 nat.

### z1 — audit-expected: omega_cdm

| seed | c | val MI +/- err | top form (argmax val MI) |
|---:|---:|---:|---|
| 0 | 10 | 1.211 +/- 0.031 | `H0**2*n_s**2*omega_b/(A_s*omega_cdm**2)` |
| 1 | 10 | 1.112 +/- 0.025 | `H0**2*omega_b*(n_s - 0.5106389)**2/omega_cdm**2` |
| 2 | 9 | 1.106 +/- 0.024 | `H0**2*n_s**4*omega_b/omega_cdm**2` |
| 3 | 10 | 1.211 +/- 0.031 | `H0**2*n_s**2*omega_b/(A_s*omega_cdm**2)` |
| 4 | 10 | 1.211 +/- 0.031 | `H0**2*n_s**2*omega_b/(A_s*omega_cdm**2)` |

Cross-seed top MI 1.170 +/- 0.050 nat.

### z2 — audit-expected: amplitude (A_s, tau)

Reference study (inputs `A_s, tau` only): top form `A_s*(tau - 0.598)  (5/5 seeds)`, val MI 0.822 nat.

| seed | c | val MI +/- err | r(top) | top form (argmax val MI) |
|---:|---:|---:|---:|---|
| 0 | 10 | 1.487 +/- 0.030 | -2.099 | `log(log(H0*(omega_cdm + tau))/A_s)**2` |
| 1 | 10 | 1.487 +/- 0.030 | -2.099 | `log(log(H0*(omega_cdm + tau))/A_s)**2` |
| 2 | 10 | 1.487 +/- 0.030 | -2.099 | `log(log(H0*(omega_cdm + tau))/A_s)**2` |
| 3 | 8 | 1.490 +/- 0.029 | -2.099 | `A_s/log(H0*(omega_cdm + tau))` |
| 4 | 9 | 1.143 +/- 0.028 | -1.878 | `(2*omega_cdm + tau + 0.23251294)/A_s` |

Cross-seed top MI 1.419 +/- 0.138 nat.

**Implied tau exponent** r = (df/dtau)/(df/dlnA_s) at the prior midpoint (r = -2 iff the (A_s, tau)-dependence enters through `ln(A_s*e^(r*tau))`, any wrapper, any shape terms): -2.055 +/- 0.088 (n=5). Reference study's OLS readout of the same quantity: -1.988.

Scan over all 50 Pareto equations (same regexes as the reference study's section 3d): **5 strict textbook hits**, 0 expanded `A_s*tau` bilinear hits. No literal `exp(b*tau)` slope in [-2.5, -1.5] on any front.

### z3 — audit-expected: n_s

| seed | c | val MI +/- err | top form (argmax val MI) |
|---:|---:|---:|---|
| 0 | 9 | 2.159 +/- 0.028 | `-omega_b + exp(n_s/(omega_cdm - 0.6201554))` |
| 1 | 10 | 2.201 +/- 0.026 | `omega_b + log(0.507140873135313*n_s + omega_b + omega_cdm)` |
| 2 | 9 | 2.205 +/- 0.025 | `(omega_b - exp(-n_s*(omega_cdm + 0.3747385)))**2` |
| 3 | 10 | 2.178 +/- 0.030 | `exp(-omega_b + exp(-n_s - 2*omega_cdm))` |
| 4 | 10 | 2.178 +/- 0.030 | `exp(-omega_b + exp(-n_s - 2*omega_cdm))` |

Cross-seed top MI 2.184 +/- 0.017 nat.

### z4 — audit-expected: H0

| seed | c | val MI +/- err | top form (argmax val MI) |
|---:|---:|---:|---|
| 0 | 9 | 1.245 +/- 0.027 | `-tau + log(A_s*H0**2*omega_cdm)` |
| 1 | 9 | 1.303 +/- 0.025 | `A_s*H0**2*omega_cdm*exp(-2*tau)` |
| 2 | 10 | 1.291 +/- 0.024 | `exp(2*tau)/(A_s*H0**2*omega_cdm)` |
| 3 | 9 | 1.291 +/- 0.024 | `exp(2*tau)/(A_s*H0**2*omega_cdm)` |
| 4 | 10 | 1.250 +/- 0.025 | `exp(exp(tau))/(A_s*H0**2*omega_cdm)` |

Cross-seed top MI 1.276 +/- 0.024 nat.

## Shuffled-target negative control (z2, all 6 inputs)

Identical PySR configuration, target column permuted across rows: quantifies the null MI floor with the enlarged input set (more inputs -> more room to overfit spurious MI).

| shuffle seed | best expr (by shuffled-target MI) | MI vs shuffled | MI vs TRUE | textbook form on front |
|---:|---|---:|---:|---|
| 0 | `-tau/(omega_cdm*(omega_b - 0.022799859)**2)` | 0.033 | 0.044 | no |
| 1 | `H0` | 0.001 | 0.044 | no |
| 2 | `0.535115942792119*omega_b**8/(0.051325074983624 ` | 0.017 | 0.018 | no |

## What the runs show

**Every latent is a multi-parameter composite.** Cross-seed mean top MI spans 1.17-2.18 nat across the 5 latents (1/5 use >=5 of the 6 parameters in their top forms) — far above the single-parameter audit MIs, consistent with the encoder means being deterministic functions of the parameters. The audit's one-latent-one-parameter labels are the leading order of each latent, not the whole story: the amplitude latent's top MI (1.42 nat) is x1.7 the (A_s, tau)-restricted ceiling (0.822 nat) as SR absorbs the shape-sector dependencies the 2-input study marginalised over.

**The -2 reionization-suppression exponent survives full blindness.** The amplitude latent z2 carries the textbook -2 in every seed once read with the derivative ratio: r = -2.055 +/- 0.088 over 5 top forms; the literal exponential never surfaces — it is 99.9% linear over the prior, so the parsimony penalty always prefers its affine/rational surrogates. At maxsize 10 with all inputs exposed, the crisp two-variable textbook form is outcompeted on the front by higher-MI shape-blended composites; the derivative-ratio readout (not the literal-form scan) is the right instrument for the exponent. Forcing the *selection* of a low-complexity form is a search-time budget cut (rerun with a smaller maxsize), not a post-hoc filter of this front.

**The control stays null.** Best MI against the shuffled target <= 0.033 nat over 3 shuffle seeds, no textbook structure on any control front. Evaluated against the TRUE latent those same expressions reach at most 0.044 nat vs 1.42 for the real runs — the enlarged search space does not hallucinate the result.

_Runtime: 25 SR runs (5 latents x 5 seeds), mean fit 216 s at 16 threads (reference study: ~340 s)._


---
_Generated by `scripts/consolidate_allparams.py` from `results/lcdm_tt_beta3e-4/allparams_ms10/*/report.json`. Runs: `hpc/slurm_allparams_{encode,sr,control}.sh`; per-latent cross-seed pooling in `results/lcdm_tt_beta3e-4/allparams_ms10/pooled_z<k>/`._
