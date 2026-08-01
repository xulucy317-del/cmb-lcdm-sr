# PySR hyperparameter sweep `hp_v1` — TT+EE-lowl (`models/lcdm_tt_ee_lowl`)

**Design.** All-params blind SR (omega_b, omega_cdm, H0, tau, A_s, n_s -> latent), protocol identical to the reference study except for the swept PySR hyperparameters. Baseline: niterations 200, populations 15, maxsize 20, PySR 1.5 defaults otherwise (population_size 27, ncycles_per_iteration 380). Mode **star** over `niterations` [100, 400], `populations` [8, 31], `maxsize` [10, 15, 30], `population_size` [54, 108], `ncycles_per_iteration` [190, 760]; latents [5], seeds [0, 1, 2]; 36/36 runs loaded.

**How to read the metrics.** *Top val MI* is the study's headline readout (argmax held-out GMM-MI over the Pareto front) but with all 6 inputs it grows with any capacity knob — it measures search power. *MI @ c<=10* holds the complexity budget fixed across configs, so it is the parsimony-matched comparison. *pars c* is the complexity of the most parsimonious form within 1 sigma of the top MI. For the amplitude latent, *r(top)* is the implied tau exponent (textbook -2) and *tb* counts strict textbook forms on the front.


## Latent z5 (audit-expected: amplitude (A_s, tau))

| config | ni | pop | ms | extra | seeds | top MI (mean +/- std) | dMI vs base | MI@c<=10 | pars c | fit s | r(top) | tb |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 200 | 15 | 20 | - | 3 | 3.618 +/- 0.275 | - | 2.016 | 18.3 | 299 | -2.002 +/- 0.009 | 10 |
| `ni100` | 100 | 15 | 20 | - | 3 | 3.442 +/- 0.375 | -0.176 | 2.018 | 18.7 | 193 | -2.023 +/- 0.032 | 19 |
| `ni400` | 400 | 15 | 20 | - | 3 | 3.825 +/- 0.163 | +0.207 | 2.018 | 19.0 | 550 | -1.996 +/- 0.011 | 16 |
| `pop8` | 200 | 8 | 20 | - | 3 | 3.435 +/- 0.215 | -0.183 | 2.019 | 19.0 | 209 | -1.962 +/- 0.017 | 12 |
| `pop31` | 200 | 31 | 20 | - | 3 | 3.878 +/- 0.139 | +0.260 | 2.018 | 19.0 | 572 | -1.997 +/- 0.005 | 17 |
| `ms10` | 200 | 15 | 10 | - | 3 | 1.686 +/- 0.017 | -1.932 | 1.686 | 9.3 | 208 | -2.004 +/- 0.029 | 4 |
| `ms15` | 200 | 15 | 15 | - | 3 | 2.823 +/- 0.050 | -0.795 | 2.018 | 14.3 | 274 | -1.989 +/- 0.016 | 9 |
| `ms30` | 200 | 15 | 30 | - | 3 | 4.049 +/- 0.136 | +0.431 | 2.018 | 23.7 | 339 | -1.993 +/- 0.006 | 20 |
| `ps54` | 200 | 15 | 20 | population_size=54 | 3 | 3.857 +/- 0.224 | +0.239 | 2.018 | 19.0 | 564 | -2.002 +/- 0.002 | 23 |
| `ps108` | 200 | 15 | 20 | population_size=108 | 3 | 3.890 +/- 0.142 | +0.272 | 2.016 | 19.7 | 1063 | -2.000 +/- 0.000 | 17 |
| `ncyc190` | 200 | 15 | 20 | ncycles_per_iteration=190 | 3 | 3.821 +/- 0.225 | +0.203 | 2.018 | 18.7 | 181 | -1.998 +/- 0.003 | 19 |
| `ncyc760` | 200 | 15 | 20 | ncycles_per_iteration=760 | 3 | 3.597 +/- 0.360 | -0.021 | 2.018 | 19.0 | 510 | -2.001 +/- 0.029 | 14 |

Best top MI: `ms30` (4.049 +/- 0.136 nat). Best MI@c<=10: `pop8` (2.019 nat).

### One-factor effects vs baseline (top MI 3.618 +/- 0.275, MI@c<=10 2.016, fit 299 s)

| axis | value | dTop MI | dMI@c<=10 | d fit s |
|---|---:|---:|---:|---:|
| niterations | 100 | -0.176 | +0.002 | -106 |
| niterations | 400 | +0.207 | +0.001 | +251 |
| populations | 8 | -0.183 | +0.003 | -90 |
| populations | 31 | +0.260 | +0.001 | +274 |
| maxsize | 10 | -1.932 | -0.330 | -91 |
| maxsize | 15 | -0.795 | +0.001 | -25 |
| maxsize | 30 | +0.431 | +0.001 | +40 |
| population_size | 54 | +0.239 | +0.001 | +265 |
| population_size | 108 | +0.272 | +0.000 | +764 |
| ncycles_per_iteration | 190 | +0.203 | +0.001 | -118 |
| ncycles_per_iteration | 760 | -0.021 | +0.001 | +211 |

### Per-seed top forms (z5)


**c00_baseline**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 19 | 3.329 +/- 0.029 | 2.015 (10) | `(omega_b - 0.19451405)*(omega_cdm + 0.677587250030441*tau + 0.177799233201613)*log(H0/n_s**2)/A_s` |
| 1 | 20 | 3.536 +/- 0.030 | 2.015 (10) | `log(A_s*((tau - 0.7361663)/log(log(H0) - 0.117946066) + omega_cdm/n_s)/(omega_b - 0.19090208))` |
| 2 | 19 | 3.989 +/- 0.028 | 2.019 (10) | `-5.7416734*omega_b + 2*tau + log(log(H0)/A_s) + 2.8708367*omega_cdm/n_s` |

**c01_ni100**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 20 | 3.972 +/- 0.030 | 2.019 (10) | `log(A_s*(n_s*(2*omega_b + 0.7774814) - omega_cdm)**2*exp(-2*tau)/(n_s**2*log(H0)))**2` |
| 1 | 18 | 3.163 +/- 0.032 | 2.017 (10) | `log((-omega_b + log(-omega_b + tau + 1.2638941) + omega_cdm/n_s)*log(H0)/A_s)` |
| 2 | 19 | 3.191 +/- 0.028 | 2.019 (10) | `A_s*exp(-2*tau - 2.70176266799202*exp(-omega_b + omega_cdm))/log(H0/n_s**2)` |

**c02_ni400**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 20 | 3.602 +/- 0.033 | 2.015 (10) | `log(A_s*(-(omega_b + log(2.551874 - tau))**2 + omega_cdm/n_s)**2/log(1.285029*H0))` |
| 1 | 19 | 3.991 +/- 0.032 | 2.019 (10) | `log(exp(-5.676566*omega_b + 2*tau + 2.838283*omega_cdm/n_s)*log(H0)/A_s)` |
| 2 | 20 | 3.881 +/- 0.033 | 2.019 (10) | `log((exp(tau) - 0.53130794)*(-2*omega_b + 0.27743292 + omega_cdm/n_s)*log(H0)/A_s)` |

**c03_pop8**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 20 | 3.359 +/- 0.031 | 2.019 (10) | `log(omega_cdm + log((-2*omega_b + 0.37699434 + (omega_cdm + tau)/n_s)*log(H0)/A_s))` |
| 1 | 18 | 3.218 +/- 0.027 | 2.019 (10) | `log(A_s*(omega_b + 0.14958467)/(24.860575 + omega_cdm*(H0 + 627.07715*tau)/n_s))` |
| 2 | 20 | 3.729 +/- 0.033 | 2.019 (10) | `omega_b - 0.1756471*omega_cdm - 0.1756471*log((0.858605*n_s + omega_cdm + tau)**2*log(H0)/(A_s*n_s**2))` |

**c04_pop31**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 19 | 3.684 +/- 0.030 | 2.019 (10) | `-omega_b + 0.18216233*log(exp(2*tau)*log(H0)/(A_s*(n_s - log(omega_cdm))))` |
| 1 | 19 | 3.947 +/- 0.035 | 2.019 (10) | `log(exp(-2*omega_b + 2*tau + 2*(-omega_b + omega_cdm)/(n_s - 0.27532873))*log(H0)/A_s)` |
| 2 | 20 | 4.002 +/- 0.031 | 2.015 (10) | `log((-2.8480976*omega_b + tau + 10.592454 + 1.4240488*omega_cdm/n_s)*log(log(H0)/A_s))` |

**c05_ms10**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 9 | 1.698 +/- 0.026 | 1.698 (9) | `exp(2*(n_s*tau + omega_cdm)/n_s)/A_s` |
| 1 | 10 | 1.662 +/- 0.026 | 1.662 (10) | `log(tau + 1.1980306*exp(omega_cdm))/A_s` |
| 2 | 10 | 1.698 +/- 0.026 | 1.698 (10) | `(-n_s*(tau + 0.31837177) - omega_cdm)/(A_s*n_s)` |

**c06_ms15**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 14 | 2.752 +/- 0.030 | 2.015 (10) | `(n_s*(0.706294*tau + 0.18462792) + omega_cdm)*log(H0)/(A_s*n_s)` |
| 1 | 15 | 2.850 +/- 0.024 | 2.019 (10) | `log(A_s*exp(-2*tau - 2.8179422*omega_cdm/n_s)/log(H0))` |
| 2 | 15 | 2.865 +/- 0.031 | 2.019 (10) | `(tau + (-omega_b + omega_cdm + 0.569251)**2)*log(H0/n_s)/A_s` |

**c07_ms30**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 30 | 3.868 +/- 0.029 | 2.015 (10) | `-exp(2*exp(0.1370506/(tau - log(A_s*(n_s*(0.34776232*tau - 0.496441283774528) + omega_cdm)/(n_s*(omega_b - 0.20187607)*log(H0 - log(omega_cdm)))))))` |
| 1 | 30 | 4.197 +/- 0.039 | 2.019 (10) | `log(-omega_b + 0.18080369*omega_cdm + 0.36160738*tau - 0.18080369*log(A_s) + 0.0384025536889373*log(omega_cdm*(0.6468141*H0 - exp(omega_cdm + tau)))/n_s)` |
| 2 | 29 | 4.081 +/- 0.034 | 2.019 (10) | `log(-0.09241223*n_s + 0.09241223*log(exp(-5.6376656*omega_b + 2*tau + 2.8188328*omega_cdm/n_s)*log(H0)/A_s)**2 - 0.09241223*log(log(H0)))` |

**c08_ps54**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 20 | 4.016 +/- 0.031 | 2.019 (10) | `log(log(exp(2*tau + 0.0027020744/omega_b + 2.8383982*omega_cdm/n_s)*log(H0)/A_s))` |
| 1 | 20 | 4.016 +/- 0.032 | 2.019 (10) | `log(log(exp(2*tau + 0.002696558/omega_b + 2.8380374*omega_cdm/n_s)*log(H0)/A_s))` |
| 2 | 20 | 3.540 +/- 0.036 | 2.015 (10) | `log(log(log(H0)/(A_s*(omega_b + 0.15239385)*log(n_s - log(1.4103556*omega_cdm + tau)))))` |

**c09_ps108**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 20 | 3.991 +/- 0.035 | 2.015 (10) | `log(4*(-omega_b + 0.3141286 + omega_cdm/(2*n_s))**2*exp(2*tau)*log(H0)/A_s)` |
| 1 | 19 | 3.991 +/- 0.032 | 2.019 (10) | `log(exp(-5.6731316*omega_b + 2*tau + 2.8365658*omega_cdm/n_s)*log(H0)/A_s)` |
| 2 | 20 | 3.689 +/- 0.030 | 2.015 (10) | `log(A_s*(n_s - log(omega_cdm))*(omega_b + 0.1602059)*exp(-2*tau)/log(H0)) - 3.7999472` |

**c10_ncyc190**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 19 | 3.970 +/- 0.030 | 2.015 (10) | `log(4*A_s*(-omega_b - 0.389892 + omega_cdm/(2*n_s))**2*exp(-2*tau)/log(H0))` |
| 1 | 19 | 3.991 +/- 0.032 | 2.019 (10) | `log(exp(-5.708056*omega_b + 2*tau + 2.83643968389014*omega_cdm/n_s)*log(H0)/A_s)` |
| 2 | 20 | 3.502 +/- 0.027 | 2.019 (10) | `(-2.9367606*omega_b + 1.4683803*omega_cdm + tau + 10.5812546056957)*log(log(H0/n_s**2)/A_s)` |

**c11_ncyc760**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 19 | 3.999 +/- 0.032 | 2.019 (10) | `log(A_s*(omega_b + 0.15336177)*exp(-(2*n_s*tau + 2.83672504235479*omega_cdm)/n_s)/log(H0))` |
| 1 | 19 | 3.125 +/- 0.032 | 2.015 (10) | `-H0*(omega_b - omega_cdm)*(-omega_b + tau + 0.46085003)/(A_s*(0.4105482*H0*(omega_b - omega_cdm) - n_s + omega_cdm))` |
| 2 | 19 | 3.666 +/- 0.031 | 2.019 (10) | `(n_s*log(omega_b) - (n_s*(tau + 10.288135) + 1.40842908186339*omega_cdm)*log(log(H0)/A_s))/n_s` |

---
_Generated by `scripts/consolidate_hp_sweep.py` from `results/lcdm_tt_ee_lowl/hpsweep_hp_v1/*/z*/report.json`. Plan/submit/status: `scripts/sweep_blind_sr.py` + `hpc/slurm_hpsweep_sr.sh`._
