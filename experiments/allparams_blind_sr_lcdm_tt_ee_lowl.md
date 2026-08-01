# All-params blind SR — TT+EE-lowl (`models/lcdm_tt_ee_lowl`, L=6, amplitude latent z5)

**Design.** The reference blind-SR study exposes PySR to the raw pair `(A_s, tau)` and targets the single amplitude latent selected by the disentanglement audit. That leaves two human-made choices in the loop: *which inputs* and *which latent*. This experiment removes both for completeness of the blindness: PySR receives **all 6 raw LCDM parameters** (`omega_b, omega_cdm, H0, tau, A_s, n_s` — no derived columns) and is run against **every latent** of this model (6 latents x 5 PySR seeds; the companion regime is consolidated in its own file by the same script). Everything else is protocol-identical to the reference study: gmm_mi pure-Julia inner loss, 200 iterations, 15 populations, maxsize 20, 5000 samples (4000 fit / 1000 val), operators `exp, log, neg, square` / `+, *, -, /`, post-hoc ranking by held-out GMM-MI.

Under the bijection-invariant MI loss the search must now also do **variable selection**: nothing tells it which of the 6 parameters a latent encodes. And because the encoder posterior means are *deterministic* functions of the 6 parameters (spectrum -> encoder is a fixed map), once all inputs are exposed the val MI is no longer capped by marginalising over hidden parameters — it keeps rising along the Pareto front as sub-dominant dependencies are absorbed (the reference study's 0.822 / 1.196 nat were exactly such marginalisation ceilings). The per-seed readout below is therefore the **top Pareto equation by val MI**. The complexity budget is a *search-time* hyperparameter, not a report-time filter: these runs use PySR `maxsize 20`; for a lower-complexity (reference-comparable) discovery, lower the budget and rerun — `sbatch --array=... hpc/slurm_allparams_sr.sh <run> "0 1 2 3 4" <maxsize>` — which concentrates the evolutionary search on small forms instead of post-hoc slicing a front evolved toward the cap.


## Cross-seed summary

| latent | audit-expected param | top MI (mean +/- std over seeds) | params in top forms |
|---|---|---:|---|
| z0 | omega_cdm | 1.769 +/- 0.014 | omega_b (5/5), omega_cdm (5/5), H0 (5/5), A_s (5/5), n_s (5/5), tau (2/5) |
| z1 | H0 | 3.572 +/- 0.352 | omega_b (5/5), omega_cdm (5/5), H0 (5/5), tau (5/5), A_s (5/5), n_s (5/5) |
| z2 | omega_b | 3.282 +/- 0.045 | omega_b (5/5), omega_cdm (5/5), H0 (5/5), A_s (5/5), n_s (5/5) |
| z3 | n_s | 3.117 +/- 0.048 | omega_b (5/5), omega_cdm (5/5), H0 (5/5), n_s (5/5), tau (1/5) |
| z4 | tau (amplitude sector) | 2.166 +/- 0.086 | tau (5/5), A_s (5/5), n_s (2/5), omega_b (2/5), omega_cdm (1/5), H0 (1/5) |
| z5 | amplitude (A_s, tau) | 3.830 +/- 0.174 | omega_b (5/5), omega_cdm (5/5), H0 (5/5), tau (5/5), A_s (5/5), n_s (5/5) |

## Per-latent results — top Pareto equation, every seed


### z0 — audit-expected: omega_cdm

| seed | c | val MI +/- err | top form (argmax val MI) |
|---:|---:|---:|---|
| 0 | 16 | 1.787 +/- 0.034 | `omega_b*(H0 + 27.826664)*(n_s - 0.095620185)*log(A_s)**4/omega_cdm` |
| 1 | 20 | 1.745 +/- 0.036 | `log(tau - log(49.0100838112454*A_s**2*(-1 + 0.614772339966153*omega_cdm/omega_b)**8/(H0**8*(0.41061375 - n_s)**8)))` |
| 2 | 20 | 1.774 +/- 0.037 | `log(n_s*(1.4913623*H0*omega_b/omega_cdm + 2.56879)/log(H0) - omega_cdm - log(A_s))` |
| 3 | 16 | 1.767 +/- 0.036 | `-n_s*(omega_b*(H0 + 27.79619) + 1.825506*omega_cdm)*log(A_s)**4/omega_cdm` |
| 4 | 19 | 1.772 +/- 0.036 | `-H0 - 0.460366792638367*log((tau + exp((6.5674596*n_s*omega_b - omega_cdm)/omega_b))/A_s)**2` |

Cross-seed top MI 1.769 +/- 0.014 nat.

### z1 — audit-expected: H0

| seed | c | val MI +/- err | top form (argmax val MI) |
|---:|---:|---:|---|
| 0 | 20 | 3.809 +/- 0.036 | `log(-log(n_s) + log(A_s*omega_cdm**4*(0.00141385081781373*H0**2 + 1)**4*exp(-2*tau)/omega_b**2) + 26.2457528829658)` |
| 1 | 20 | 2.876 +/- 0.024 | `tau + 46.233837/log((H0 + omega_b*log(omega_cdm)*log(A_s*omega_cdm/n_s)**2)**2/(log(omega_cdm)**2*log(A_s*omega_cdm/n_s)**4))` |
| 2 | 19 | 3.692 +/- 0.034 | `log(n_s) - log(A_s*H0**7*omega_cdm**4*exp(-2*tau)/omega_b**2)` |
| 3 | 20 | 3.793 +/- 0.036 | `n_s + 2*tau - log(A_s*omega_cdm**4*(0.00140701198492809*H0**2 + 1)**4/omega_b**2) - 26.2651479312544` |
| 4 | 18 | 3.690 +/- 0.034 | `log(A_s*H0**7*omega_cdm**4*exp(-2*tau)/(n_s*omega_b**2))` |

Cross-seed top MI 3.572 +/- 0.352 nat.

### z2 — audit-expected: omega_b

| seed | c | val MI +/- err | top form (argmax val MI) |
|---:|---:|---:|---|
| 0 | 19 | 3.213 +/- 0.032 | `log(H0 + (omega_cdm + (log(A_s) - 6.6247473)*(-n_s + exp(omega_cdm) - 1.3261139))**2/omega_b)` |
| 1 | 20 | 3.257 +/- 0.032 | `-9.63122112224589*n_s + 260.550680122098*omega_b + 10.6312211222459*omega_cdm + 0.416767593885653*log(A_s) + 2.066468/H0` |
| 2 | 19 | 3.285 +/- 0.031 | `((n_s - 27.104689*omega_b)*log(A_s) + 17.5407371455653)*exp(1.3992021/H0)/((omega_cdm - 0.57541263)*log(A_s))` |
| 3 | 20 | 3.311 +/- 0.033 | `log((-omega_b*exp(-1.18363128588324*(0.919161408603829*n_s - omega_cdm)**2) - 0.0048134807)*exp(0.5132131/H0)/log(A_s))` |
| 4 | 17 | 3.343 +/- 0.035 | `H0*((n_s - 1.0812154*omega_cdm)*log(A_s) + 61.77855)/(H0*log(omega_b) + 0.912889)` |

Cross-seed top MI 3.282 +/- 0.045 nat.

### z3 — audit-expected: n_s

| seed | c | val MI +/- err | top form (argmax val MI) |
|---:|---:|---:|---|
| 0 | 17 | 3.196 +/- 0.039 | `log(tau**2 + exp(-4.407752*n_s)*log(H0)/(omega_cdm*(omega_b - 0.0059834956)))` |
| 1 | 20 | 3.052 +/- 0.034 | `log(-log(omega_b*(n_s - 0.51070356)*(H0*(omega_cdm + 0.014487113) + 1.8308733)*exp(n_s)/H0))**2` |
| 2 | 18 | 3.098 +/- 0.036 | `log(log(exp(n_s**4*(omega_b - 0.0048390473)*(omega_cdm - 0.019833282 + 1.7693522/H0))))` |
| 3 | 18 | 3.103 +/- 0.036 | `-omega_cdm + log(n_s**4*omega_b*omega_cdm/log(H0*exp(n_s)/omega_b)**2)` |
| 4 | 17 | 3.135 +/- 0.036 | `log(log(H0)/(omega_cdm*(omega_b*exp(3.20512692102287*n_s))**1.371386191677))` |

Cross-seed top MI 3.117 +/- 0.048 nat.

### z4 — audit-expected: tau (amplitude sector)

| seed | c | val MI +/- err | top form (argmax val MI) |
|---:|---:|---:|---|
| 0 | 14 | 2.175 +/- 0.033 | `2.60037297451584*A_s*(0.620129195236019*log(log(0.24930401/tau)) - 1)**2/tau - 0.0067654504` |
| 1 | 17 | 2.232 +/- 0.035 | `log(168.933888466849*A_s**2*(0.0769381272044216*log(n_s*tau) + 1)**2/(tau**4*(log(n_s*tau) + 12.997457) - 0.024211021)**2)**2` |
| 2 | 17 | 2.121 +/- 0.031 | `A_s/(tau + 0.21998107*log(log(omega_b) - log((tau - 0.011009995)**2)) + 1.18100518667902)` |
| 3 | 19 | 2.029 +/- 0.039 | `A_s*(13.917685*exp(tau) + log(n_s**2*(H0*tau - 4.4762926*omega_cdm)))` |
| 4 | 20 | 2.276 +/- 0.037 | `exp(omega_b + tau) + log((tau*log(-A_s**2/(tau - 0.19279961))**2 + 0.42438555)**4/tau**4)` |

Cross-seed top MI 2.166 +/- 0.086 nat.

### z5 — audit-expected: amplitude (A_s, tau)

Reference study (inputs `A_s, tau` only): top form `A_s*(tau - 0.579) variants; literal A_s*exp(-2*tau) at seed 3`, val MI 1.196 nat.

| seed | c | val MI +/- err | r(top) | top form (argmax val MI) |
|---:|---:|---:|---:|---|
| 0 | 20 | 3.546 +/- 0.035 | -2.000 | `log(A_s*exp(5.5231444*omega_b - 2*tau + 2.7615722*(n_s/omega_cdm - 2.70032)/H0))` |
| 1 | 19 | 3.989 +/- 0.032 | -2.000 | `omega_b - 0.17572255*log(exp((2*n_s*tau + 2.8387810535324*omega_cdm)/n_s)*log(H0)/A_s)` |
| 2 | 20 | 3.913 +/- 0.032 | -1.981 | `2*omega_b - 0.706194989617168*tau + 0.356474307390437*log(A_s) - omega_cdm/n_s + 5.64159234258649/H0` |
| 3 | 19 | 3.988 +/- 0.032 | -2.000 | `log(A_s*exp(5.6754548*omega_b - 2*tau - 2.8377274*omega_cdm/n_s)/log(H0))` |
| 4 | 20 | 3.711 +/- 0.030 | -1.985 | `log(5.87278128727684*(-omega_b + 0.412646424488882*tau + 0.338873022175371 + 0.587353575511118*omega_cdm/n_s)**2*log(H0)/A_s)` |

Cross-seed top MI 3.830 +/- 0.174 nat.

**Implied tau exponent** r = (df/dtau)/(df/dlnA_s) at the prior midpoint (r = -2 iff the (A_s, tau)-dependence enters through `ln(A_s*e^(r*tau))`, any wrapper, any shape terms): -1.993 +/- 0.008 (n=5). Reference study's OLS readout of the same quantity: -1.9995.

Scan over all 100 Pareto equations (same regexes as the reference study's section 3d): **23 strict textbook hits**, 3 expanded `A_s*tau` bilinear hits. Literal `exp(b*tau)` slopes found in [-2.5, -1.5]: [-2.0].

## Shuffled-target negative control (z5, all 6 inputs)

Identical PySR configuration, target column permuted across rows: quantifies the null MI floor with the enlarged input set (more inputs -> more room to overfit spurious MI).

| shuffle seed | best expr (by shuffled-target MI) | MI vs shuffled | MI vs TRUE | textbook form on front |
|---:|---|---:|---:|---|
| 0 | `H0**2/(tau - 0.0520711)**2` | 0.060 | 0.126 | no |
| 1 | `-2.08581132063665*omega_cdm - (omega_b - tau)**4` | 0.004 | 0.302 | no |
| 2 | `tau**2/(n_s - 0.99386555)**2` | 0.029 | 0.074 | no |

## What the runs show

**Every latent is a multi-parameter composite.** Cross-seed mean top MI spans 1.77-3.83 nat across the 6 latents (6/6 use >=5 of the 6 parameters in their top forms) — far above the single-parameter audit MIs, consistent with the encoder means being deterministic functions of the parameters. The audit's one-latent-one-parameter labels are the leading order of each latent, not the whole story: the amplitude latent's top MI (3.83 nat) is x3.2 the (A_s, tau)-restricted ceiling (1.196 nat) as SR absorbs the shape-sector dependencies the 2-input study marginalised over.

**The -2 reionization-suppression exponent survives full blindness.** The amplitude latent z5 carries the textbook -2 in every seed once read with the derivative ratio: r = -1.993 +/- 0.008 over 5 top forms, and the literal `exp(-2*tau)` appears on the Pareto front. At maxsize 20 with all inputs exposed, the crisp two-variable textbook form is outcompeted on the front by higher-MI shape-blended composites; the derivative-ratio readout (not the literal-form scan) is the right instrument for the exponent. Forcing the *selection* of a low-complexity form is a search-time budget cut (rerun with a smaller maxsize), not a post-hoc filter of this front.

**The control stays null.** Best MI against the shuffled target <= 0.060 nat over 3 shuffle seeds, no textbook structure on any control front. Evaluated against the TRUE latent those same expressions reach at most 0.302 nat vs 3.83 for the real runs — the enlarged search space does not hallucinate the result.

_Runtime: 30 SR runs (6 latents x 5 seeds), mean fit 306 s at 16 threads (reference study: ~340 s)._


---
_Generated by `scripts/consolidate_allparams.py` from `results/lcdm_tt_ee_lowl/allparams/*/report.json`. Runs: `hpc/slurm_allparams_{encode,sr,control}.sh`; per-latent cross-seed pooling in `results/lcdm_tt_ee_lowl/allparams/pooled_z<k>/`._
