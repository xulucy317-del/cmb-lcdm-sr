# All-params blind SR — TT+EE-lowl (`models/lcdm_tt_ee_lowl`, L=6, amplitude latent z5)

**Design.** The reference blind-SR study exposes PySR to the raw pair `(A_s, tau)` and targets the single amplitude latent selected by the disentanglement audit. That leaves two human-made choices in the loop: *which inputs* and *which latent*. This experiment removes both for completeness of the blindness: PySR receives **all 6 raw LCDM parameters** (`omega_b, omega_cdm, H0, tau, A_s, n_s` — no derived columns) and is run against **every latent** of this model (6 latents x 5 PySR seeds; the companion regime is consolidated in its own file by the same script). Everything else is protocol-identical to the reference study: gmm_mi pure-Julia inner loss, 200 iterations, 15 populations, maxsize 10, 5000 samples (4000 fit / 1000 val), operators `exp, log, neg, square` / `+, *, -, /`, post-hoc ranking by held-out GMM-MI.

Under the bijection-invariant MI loss the search must now also do **variable selection**: nothing tells it which of the 6 parameters a latent encodes. And because the encoder posterior means are *deterministic* functions of the 6 parameters (spectrum -> encoder is a fixed map), once all inputs are exposed the val MI is no longer capped by marginalising over hidden parameters — it keeps rising along the Pareto front as sub-dominant dependencies are absorbed (the reference study's 0.822 / 1.196 nat were exactly such marginalisation ceilings). The per-seed readout below is therefore the **top Pareto equation by val MI**. The complexity budget is a *search-time* hyperparameter, not a report-time filter: these runs use PySR `maxsize 10`; for a lower-complexity (reference-comparable) discovery, lower the budget and rerun — `sbatch --array=... hpc/slurm_allparams_sr.sh <run> "0 1 2 3 4" <maxsize>` — which concentrates the evolutionary search on small forms instead of post-hoc slicing a front evolved toward the cap.


## Cross-seed summary

| latent | audit-expected param | top MI (mean +/- std over seeds) | params in top forms |
|---|---|---:|---|
| z0 | omega_cdm | 1.423 +/- 0.017 | omega_b (5/5), omega_cdm (5/5), H0 (5/5), n_s (5/5), A_s (1/5) |
| z1 | H0 | 1.780 +/- 0.082 | omega_b (5/5), omega_cdm (5/5), H0 (5/5), n_s (3/5), tau (1/5) |
| z2 | omega_b | 2.474 +/- 0.242 | omega_b (5/5), omega_cdm (5/5), n_s (5/5), A_s (1/5) |
| z3 | n_s | 2.012 +/- 0.030 | omega_b (5/5), omega_cdm (5/5), n_s (5/5), H0 (1/5) |
| z4 | tau (amplitude sector) | 1.854 +/- 0.019 | tau (5/5), A_s (5/5), omega_cdm (2/5), omega_b (1/5) |
| z5 | amplitude (A_s, tau) | 1.751 +/- 0.122 | omega_cdm (5/5), tau (5/5), A_s (5/5), n_s (2/5), omega_b (1/5), H0 (1/5) |

## Per-latent results — top Pareto equation, every seed


### z0 — audit-expected: omega_cdm

| seed | c | val MI +/- err | top form (argmax val MI) |
|---:|---:|---:|---|
| 0 | 9 | 1.413 +/- 0.030 | `n_s*omega_b*(H0 + 26.100569)/omega_cdm` |
| 1 | 10 | 1.414 +/- 0.029 | `-H0**2*n_s**2*omega_b**2/omega_cdm**2 + H0` |
| 2 | 10 | 1.456 +/- 0.030 | `-omega_cdm/(n_s*omega_b*(H0 - log(A_s)))` |
| 3 | 10 | 1.416 +/- 0.030 | `-n_s*omega_b*(H0 + 26.113224)/omega_cdm` |
| 4 | 10 | 1.416 +/- 0.030 | `-n_s*omega_b*(H0 + 26.103731)/omega_cdm` |

Cross-seed top MI 1.423 +/- 0.017 nat.

### z1 — audit-expected: H0

| seed | c | val MI +/- err | top form (argmax val MI) |
|---:|---:|---:|---|
| 0 | 10 | 1.738 +/- 0.025 | `n_s + log(omega_b/(H0**4*omega_cdm**2))` |
| 1 | 10 | 1.742 +/- 0.023 | `omega_cdm + log(H0**2*omega_cdm*log(omega_b)**2)` |
| 2 | 10 | 1.943 +/- 0.023 | `log(H0**2*omega_cdm*(tau + log(omega_b))**2)` |
| 3 | 10 | 1.735 +/- 0.025 | `log(H0**2*omega_cdm*log(n_s*omega_b)**2)` |
| 4 | 10 | 1.740 +/- 0.025 | `log(n_s*omega_b/(H0**4*omega_cdm**2))` |

Cross-seed top MI 1.780 +/- 0.082 nat.

### z2 — audit-expected: omega_b

| seed | c | val MI +/- err | top form (argmax val MI) |
|---:|---:|---:|---|
| 0 | 7 | 2.341 +/- 0.024 | `omega_b*exp(-(n_s - omega_cdm)**2)` |
| 1 | 10 | 2.959 +/- 0.031 | `omega_b*exp(-(n_s - omega_cdm)**2)/log(A_s)` |
| 2 | 10 | 2.353 +/- 0.024 | `-omega_b + log((0.00955452961139817*n_s - 0.00955452961139817*omega_cdm + 1)**4) + 18.6029597283122` |
| 3 | 10 | 2.365 +/- 0.021 | `exp(n_s - 26.3857993316688*omega_b - 1.1035595*omega_cdm)` |
| 4 | 7 | 2.353 +/- 0.024 | `n_s - 26.3786143087048*omega_b - omega_cdm` |

Cross-seed top MI 2.474 +/- 0.242 nat.

### z3 — audit-expected: n_s

| seed | c | val MI +/- err | top form (argmax val MI) |
|---:|---:|---:|---|
| 0 | 9 | 2.013 +/- 0.029 | `-log(omega_b)/(n_s + 2*omega_cdm)` |
| 1 | 9 | 2.003 +/- 0.028 | `omega_b*(n_s - 0.65878135)*(omega_cdm + 0.04017927)` |
| 2 | 9 | 2.013 +/- 0.029 | `-log(omega_b)/(n_s + 2*omega_cdm)` |
| 3 | 10 | 2.062 +/- 0.030 | `-log(H0)/(omega_b*omega_cdm*(n_s - 0.7090522))` |
| 4 | 10 | 1.967 +/- 0.031 | `log(n_s**4*omega_b*(omega_b + omega_cdm))` |

Cross-seed top MI 2.012 +/- 0.030 nat.

### z4 — audit-expected: tau (amplitude sector)

| seed | c | val MI +/- err | top form (argmax val MI) |
|---:|---:|---:|---|
| 0 | 9 | 1.832 +/- 0.038 | `A_s*log(A_s*omega_cdm/tau**2)` |
| 1 | 9 | 1.851 +/- 0.035 | `A_s/(omega_cdm - log(tau) + 4.35370939838504)` |
| 2 | 9 | 1.849 +/- 0.025 | `log(omega_b + log((0.46628493 - tau)/A_s))` |
| 3 | 9 | 1.849 +/- 0.033 | `-A_s*tau**0.12693374` |
| 4 | 9 | 1.889 +/- 0.032 | `(tau*log(A_s) - log(tau) - 292.56662)/log(A_s)` |

Cross-seed top MI 1.854 +/- 0.019 nat.

### z5 — audit-expected: amplitude (A_s, tau)

Reference study (inputs `A_s, tau` only): top form `A_s*(tau - 0.579) variants; literal A_s*exp(-2*tau) at seed 3`, val MI 1.196 nat.

| seed | c | val MI +/- err | r(top) | top form (argmax val MI) |
|---:|---:|---:|---:|---|
| 0 | 10 | 1.714 +/- 0.027 | -2.089 | `log(A_s*log(n_s - log(omega_cdm + tau)))` |
| 1 | 10 | 1.698 +/- 0.026 | -1.970 | `(-n_s*(tau + 0.31837177) - omega_cdm)/(A_s*n_s)` |
| 2 | 10 | 1.684 +/- 0.027 | -2.083 | `(tau + (-omega_b + omega_cdm + 0.54736805)**2)/A_s` |
| 3 | 10 | 1.993 +/- 0.028 | -1.948 | `(omega_cdm + tau + 0.32826653)*log(H0)/A_s` |
| 4 | 10 | 1.666 +/- 0.025 | -1.933 | `(omega_cdm + exp(tau + exp(omega_cdm)))**2/A_s` |

Cross-seed top MI 1.751 +/- 0.122 nat.

**Implied tau exponent** r = (df/dtau)/(df/dlnA_s) at the prior midpoint (r = -2 iff the (A_s, tau)-dependence enters through `ln(A_s*e^(r*tau))`, any wrapper, any shape terms): -2.005 +/- 0.068 (n=5). Reference study's OLS readout of the same quantity: -1.9995.

Scan over all 47 Pareto equations (same regexes as the reference study's section 3d): **6 strict textbook hits**, 0 expanded `A_s*tau` bilinear hits. Literal `exp(b*tau)` slopes found in [-2.5, -1.5]: [-2.0].

## Shuffled-target negative control (z5, all 6 inputs)

Identical PySR configuration, target column permuted across rows: quantifies the null MI floor with the enlarged input set (more inputs -> more room to overfit spurious MI).

| shuffle seed | best expr (by shuffled-target MI) | MI vs shuffled | MI vs TRUE | textbook form on front |
|---:|---|---:|---:|---|
| 0 | `log(H0)/omega_cdm` | 0.017 | 0.046 | no |
| 1 | `log(omega_b + 12380.007)` | 0.018 | 0.011 | no |
| 2 | `exp(H0*omega_cdm)` | 0.018 | 0.050 | no |

## What the runs show

**Every latent is a multi-parameter composite.** Cross-seed mean top MI spans 1.42-2.47 nat across the 6 latents (3/6 use >=5 of the 6 parameters in their top forms) — far above the single-parameter audit MIs, consistent with the encoder means being deterministic functions of the parameters. The audit's one-latent-one-parameter labels are the leading order of each latent, not the whole story: the amplitude latent's top MI (1.75 nat) is x1.5 the (A_s, tau)-restricted ceiling (1.196 nat) as SR absorbs the shape-sector dependencies the 2-input study marginalised over.

**The -2 reionization-suppression exponent survives full blindness.** The amplitude latent z5 carries the textbook -2 in every seed once read with the derivative ratio: r = -2.005 +/- 0.068 over 5 top forms, and the literal `exp(-2*tau)` appears on the Pareto front. At maxsize 10 with all inputs exposed, the crisp two-variable textbook form is outcompeted on the front by higher-MI shape-blended composites; the derivative-ratio readout (not the literal-form scan) is the right instrument for the exponent. Forcing the *selection* of a low-complexity form is a search-time budget cut (rerun with a smaller maxsize), not a post-hoc filter of this front.

**The control stays null.** Best MI against the shuffled target <= 0.018 nat over 3 shuffle seeds, no textbook structure on any control front. Evaluated against the TRUE latent those same expressions reach at most 0.050 nat vs 1.75 for the real runs — the enlarged search space does not hallucinate the result.

_Runtime: 30 SR runs (6 latents x 5 seeds), mean fit 240 s at 16 threads (reference study: ~340 s)._


---
_Generated by `scripts/consolidate_allparams.py` from `results/lcdm_tt_ee_lowl/allparams_ms10/*/report.json`. Runs: `hpc/slurm_allparams_{encode,sr,control}.sh`; per-latent cross-seed pooling in `results/lcdm_tt_ee_lowl/allparams_ms10/pooled_z<k>/`._
