# PySR hyperparameter sweep `hp_v1` — TT-only (`models/lcdm_tt_beta3e-4`)

**Design.** All-params blind SR (omega_b, omega_cdm, H0, tau, A_s, n_s -> latent), protocol identical to the reference study except for the swept PySR hyperparameters. Baseline: niterations 200, populations 15, maxsize 20, PySR 1.5 defaults otherwise (population_size 27, ncycles_per_iteration 380). Mode **star** over `niterations` [100, 400], `populations` [8, 31], `maxsize` [10, 15, 30], `population_size` [54, 108], `ncycles_per_iteration` [190, 760]; latents [2], seeds [0, 1, 2]; 36/36 runs loaded.

**How to read the metrics.** *Top val MI* is the study's headline readout (argmax held-out GMM-MI over the Pareto front) but with all 6 inputs it grows with any capacity knob — it measures search power. *MI @ c<=10* holds the complexity budget fixed across configs, so it is the parsimony-matched comparison. *pars c* is the complexity of the most parsimonious form within 1 sigma of the top MI. For the amplitude latent, *r(top)* is the implied tau exponent (textbook -2) and *tb* counts strict textbook forms on the front.


## Latent z2 (audit-expected: amplitude (A_s, tau))

| config | ni | pop | ms | extra | seeds | top MI (mean +/- std) | dMI vs base | MI@c<=10 | pars c | fit s | r(top) | tb |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 200 | 15 | 20 | - | 3 | 3.746 +/- 0.070 | - | 1.889 | 19.7 | 279 | -1.984 +/- 0.013 | 10 |
| `ni100` | 100 | 15 | 20 | - | 3 | 3.767 +/- 0.038 | +0.021 | 1.848 | 19.3 | 177 | -1.977 +/- 0.008 | 3 |
| `ni400` | 400 | 15 | 20 | - | 3 | 3.870 +/- 0.051 | +0.124 | 1.891 | 19.0 | 517 | -1.985 +/- 0.013 | 17 |
| `pop8` | 200 | 8 | 20 | - | 3 | 3.518 +/- 0.409 | -0.228 | 1.799 | 19.3 | 176 | -1.971 +/- 0.022 | 13 |
| `pop31` | 200 | 31 | 20 | - | 3 | 3.868 +/- 0.183 | +0.122 | 1.774 | 20.0 | 531 | -1.980 +/- 0.015 | 16 |
| `ms10` | 200 | 15 | 10 | - | 3 | 1.601 +/- 0.124 | -2.145 | 1.601 | 9.7 | 240 | -1.937 +/- 0.152 | 2 |
| `ms15` | 200 | 15 | 15 | - | 3 | 3.231 +/- 0.561 | -0.515 | 1.684 | 14.7 | 288 | -1.982 +/- 0.018 | 8 |
| `ms30` | 200 | 15 | 30 | - | 3 | 4.053 +/- 0.065 | +0.307 | 1.889 | 23.7 | 308 | -1.969 +/- 0.003 | 4 |
| `ps54` | 200 | 15 | 20 | population_size=54 | 3 | 3.903 +/- 0.071 | +0.157 | 1.890 | 19.0 | 532 | -1.974 +/- 0.008 | 12 |
| `ps108` | 200 | 15 | 20 | population_size=108 | 3 | 3.786 +/- 0.153 | +0.040 | 1.886 | 19.7 | 1074 | -1.975 +/- 0.020 | 19 |
| `ncyc190` | 200 | 15 | 20 | ncycles_per_iteration=190 | 3 | 3.839 +/- 0.121 | +0.093 | 1.876 | 19.3 | 167 | -1.988 +/- 0.017 | 14 |
| `ncyc760` | 200 | 15 | 20 | ncycles_per_iteration=760 | 3 | 3.816 +/- 0.131 | +0.070 | 1.890 | 19.3 | 434 | -1.994 +/- 0.004 | 16 |

Best top MI: `ms30` (4.053 +/- 0.065 nat). Best MI@c<=10: `ni400` (1.891 nat).

### One-factor effects vs baseline (top MI 3.746 +/- 0.070, MI@c<=10 1.889, fit 279 s)

| axis | value | dTop MI | dMI@c<=10 | d fit s |
|---|---:|---:|---:|---:|
| niterations | 100 | +0.021 | -0.041 | -101 |
| niterations | 400 | +0.124 | +0.001 | +238 |
| populations | 8 | -0.228 | -0.090 | -103 |
| populations | 31 | +0.122 | -0.115 | +252 |
| maxsize | 10 | -2.145 | -0.289 | -39 |
| maxsize | 15 | -0.515 | -0.205 | +9 |
| maxsize | 30 | +0.307 | -0.000 | +29 |
| population_size | 54 | +0.157 | +0.000 | +253 |
| population_size | 108 | +0.040 | -0.003 | +795 |
| ncycles_per_iteration | 190 | +0.093 | -0.013 | -111 |
| ncycles_per_iteration | 760 | +0.070 | +0.001 | +156 |

### Per-seed top forms (z2)


**c00_baseline**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 19 | 3.689 +/- 0.027 | 1.889 (10) | `-n_s + log((tau + 0.43866473)**2*(H0*omega_cdm + 0.834438)*log(omega_b)**2/A_s**2)` |
| 1 | 20 | 3.703 +/- 0.026 | 1.890 (10) | `-omega_b - tau + log(A_s*(tau - 1.0795598)/(log(omega_b)*log(H0*omega_cdm/n_s)))` |
| 2 | 20 | 3.845 +/- 0.028 | 1.889 (10) | `(tau + 11.028644)*log(((log(omega_b) - 0.146223715729121)*log(n_s/(H0*omega_cdm)) + 0.15766977)/A_s)` |

**c01_ni100**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 19 | 3.780 +/- 0.026 | 1.767 (10) | `30.7334268368117*(-omega_b + 0.360765086785559*omega_cdm + 0.18038254339278*tau + 0.150780211320675)**2*log(H0/n_s)**2/A_s` |
| 1 | 19 | 3.806 +/- 0.033 | 1.889 (10) | `log(1.17642505693969*A_s*(1 - 0.92197228680382*tau)**2*(2.782241*omega_b + 0.0851808 + n_s/(H0*omega_cdm)))` |
| 2 | 20 | 3.715 +/- 0.025 | 1.889 (10) | `log((tau + log(H0*omega_cdm/n_s))*(-6.85353750478462*omega_b + tau + 0.7323243)/A_s)**2` |

**c02_ni400**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 20 | 3.918 +/- 0.034 | 1.889 (10) | `0.00908738833807186*exp(omega_b)/((0.0953277941529744*tau + 1)**2*log((log(H0*omega_cdm/n_s) + 0.110664668951753)/A_s)**2)` |
| 1 | 20 | 3.800 +/- 0.028 | 1.890 (10) | `-tau - 0.5032946*log(-log(omega_b)*log(H0*omega_cdm/(n_s - omega_b))/A_s)` |
| 2 | 20 | 3.893 +/- 0.030 | 1.892 (10) | `log(exp(2*tau)*log(omega_b)*log((n_s - 2*omega_b)/(H0*omega_cdm))/A_s)` |

**c03_pop8**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 20 | 2.957 +/- 0.026 | 1.616 (10) | `(-n_s + log(H0*(-1.98170902388049*omega_b + 1.98170902388049*omega_cdm + tau)/A_s**2))/(omega_b + 2.72774)` |
| 1 | 20 | 3.676 +/- 0.032 | 1.889 (10) | `-omega_b + log(-A_s/((tau + 0.4437433)*(log(omega_b)*log(H0*omega_cdm/n_s) - 0.37388486)))` |
| 2 | 20 | 3.921 +/- 0.032 | 1.892 (10) | `-log(A_s*exp(-2*tau)/((omega_b - 0.21180537)**2*log((H0*omega_cdm + 0.22198106)/n_s)))` |

**c04_pop31**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 20 | 3.634 +/- 0.027 | 1.541 (9) | `omega_cdm + log(A_s**2*n_s*(tau - 0.5785679)**2/(omega_cdm*(H0 + 6.54572)*log(omega_b)**2))` |
| 1 | 20 | 3.889 +/- 0.032 | 1.892 (10) | `log(A_s*(omega_b + 0.07316713)*exp(-2*tau)/log(H0*(omega_cdm + 0.0036845563)/n_s))**2` |
| 2 | 20 | 4.081 +/- 0.028 | 1.889 (10) | `(-5.382209*omega_b + tau - 10.6477785)/log(A_s**2*n_s/(H0*omega_cdm + 0.93056935*n_s))` |

**c05_ms10**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 10 | 1.544 +/- 0.028 | 1.544 (10) | `H0*(omega_cdm + tau + 0.3205514)**2/A_s**2` |
| 1 | 10 | 1.773 +/- 0.029 | 1.773 (10) | `H0*(omega_cdm + 0.5265874*tau)/A_s**2` |
| 2 | 9 | 1.485 +/- 0.029 | 1.485 (9) | `(log(H0) + log(omega_cdm + tau))/A_s` |

**c06_ms15**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 14 | 2.438 +/- 0.026 | 1.487 (9) | `H0*(-omega_b + omega_cdm + 0.501543625894597*tau)/(A_s**2*n_s)` |
| 1 | 15 | 3.597 +/- 0.028 | 1.892 (10) | `A_s*exp(-2*tau)/(log(omega_b)*log(H0*omega_cdm/n_s))` |
| 2 | 15 | 3.657 +/- 0.027 | 1.673 (10) | `(omega_b*(tau - 10.498599) + log(log(H0*omega_cdm/n_s)/A_s))/(tau - 10.498599)` |

**c07_ms30**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 28 | 4.009 +/- 0.032 | 1.889 (10) | `omega_cdm - (tau + 11.133777)*log(log(omega_b)*log((n_s - 2*omega_b)/(omega_cdm*(H0 + 0.26218426)))/A_s) - exp(omega_b)` |
| 1 | 30 | 4.006 +/- 0.030 | 1.889 (10) | `125.175192701584*(omega_b - 0.63620716*log(A_s/(log(omega_b)*log(n_s/(H0*omega_cdm + 0.33877105)))))**2*(0.0893801060620091*tau + 1)**2 + log(log(H0))**8` |
| 2 | 28 | 4.146 +/- 0.028 | 1.889 (10) | `exp(0.63645697/((omega_b - 1.9426348)*(-omega_cdm + 3.93501588841365*tau + log(omega_cdm*(0.0114838447199721*H0 + n_s)**2/(A_s**2*n_s**2)) + 1.58476126007841)))` |

**c08_ps54**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 20 | 3.913 +/- 0.033 | 1.889 (10) | `112.412772995121*(-0.495757882889574*omega_b + 0.0943174758304394*tau + 1)**2*log((log(H0*omega_cdm/n_s) + 0.0998248822718735)/A_s)**2` |
| 1 | 20 | 3.812 +/- 0.027 | 1.889 (10) | `omega_cdm - (omega_b + log(log(omega_b)*log(n_s/(H0*omega_cdm))/A_s))*(tau + 11.064182)` |
| 2 | 19 | 3.985 +/- 0.033 | 1.890 (10) | `omega_b - log((tau + 5.205375)*log(A_s/log((H0*omega_cdm + 0.31003577)/n_s))**2)` |

**c09_ps108**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 19 | 3.937 +/- 0.027 | 1.892 (10) | `omega_b - log(A_s*exp(-2*tau)*log(omega_cdm)/(log(omega_b)*log(n_s/H0)**2))` |
| 1 | 20 | 3.576 +/- 0.027 | 1.877 (10) | `log(omega_b) + log(A_s**4*n_s**2*log(tau + 0.61954564)**2/(H0*omega_cdm + n_s)**2)` |
| 2 | 20 | 3.845 +/- 0.026 | 1.889 (10) | `log((exp(tau) + 0.013135242)**2*(H0*omega_cdm/n_s + 5.9241247 + 0.09959153/omega_b)/A_s)` |

**c10_ncyc190**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 19 | 3.842 +/- 0.031 | 1.892 (10) | `log((2.1060395 - omega_b)*log((H0*omega_cdm/n_s + 10.289202)*exp(2*tau)/A_s))` |
| 1 | 20 | 3.689 +/- 0.030 | 1.890 (10) | `n_s + log(A_s**2*(tau - 0.57901275)**2/((omega_b - 0.11904917)**2*(log(H0*omega_cdm) + 0.135345036282361)**2))` |
| 2 | 20 | 3.986 +/- 0.026 | 1.846 (10) | `omega_b - log((n_s + log(A_s**2*exp(-4*tau)*log(omega_cdm)**2/(H0 + 6.092214)))**2)` |

**c11_ncyc760**

| seed | c | top MI +/- err | MI@c<=10 (c) | top form |
|---:|---:|---:|---:|---|
| 0 | 19 | 3.742 +/- 0.028 | 1.889 (10) | `log((exp(tau) - 0.53411746)*log(omega_b)*log((n_s - omega_b)/(H0*omega_cdm))/A_s)` |
| 1 | 20 | 3.706 +/- 0.028 | 1.890 (10) | `omega_b + tau + log(-(tau + 0.9399974)*log(omega_b)*log(H0*omega_cdm/n_s)/A_s)` |
| 2 | 19 | 4.000 +/- 0.032 | 1.892 (10) | `log(A_s*exp(-2*tau)/(0.115427883082636*log(omega_b)*log(H0*omega_cdm/n_s) - 1)**2) - 4.31821866585429` |

---
_Generated by `scripts/consolidate_hp_sweep.py` from `results/lcdm_tt_beta3e-4/hpsweep_hp_v1/*/z*/report.json`. Plan/submit/status: `scripts/sweep_blind_sr.py` + `hpc/slurm_hpsweep_sr.sh`._
