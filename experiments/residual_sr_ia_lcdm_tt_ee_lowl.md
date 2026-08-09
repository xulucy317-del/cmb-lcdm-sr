# Residual SR (interaction-aware) — `lcdm_tt_ee_lowl` (post-closure follow-up to roadmap Phase 6)

Blind second-stage SR on the SAME Phase-3 residual caches e1 = mu − h(f1) as Phase 6 (protocol budget, 5 seeds), with one change: the stage-1 prediction **f1hat = h(f1)** is exposed as a 7th input column, so the search can express the amplitude × shape interactions the additive hierarchy could not absorb (deviation D-DoD-z2). Consolidated with the frozen Phase 1–3 machinery; f1hat is registered as a semantics extra input — evaluated as the θ-function h_full(f1(θ)) reconstructed exactly from the T2 rows of the caches, with chain-rule u-gradients — so clustering, signatures, Sobol and supports treat f1hat-bearing forms as θ-functions. The combined account and the stage-2 residual audit are unchanged (g is a 1-D monotone recalibration of f2, which may itself contain f1hat — a multiplicative interaction lives inside f2). DoD (amplitude): the θ-part of f2's support is pure shape-sector (f1hat itself allowed), R_SR >= 0.6.

| latent | role | res plat +/- SE | c* | f2 (rep) | support | theta-shape | f1hat | R_SR | R2 st2(e1) | comb R2(mu) | eta_plat_comb | eta_hat f1 -> f1+f2 | st2 residual |
|---|---|---|---:|---|---|---|---|---:|---:|---:|---:|---|---|
| z0 | omega_cdm | 0.505 +/- 0.005 | 15 | `-A_s*H0**2*(f1hat - 10.8708105)` | {H0, ln10As, f1hat} | False | True | 1.00 | 0.391 | 0.954 | 0.942 | 0.756 -> 0.843 | FAIL (omega_b, omega_cdm, H0, tau, ln10As, n_s) |
| z1 | H0 | 2.059 +/- 0.034 | 18 | `A_s*exp(-2*tau)/omega_b**2` | {omega_b, tau, ln10As} | False | False | 0.80 | 0.921 | 0.995 | 0.652 | 0.348 -> 0.663 | FAIL (omega_b, omega_cdm, H0, tau, ln10As, n_s) |
| z2 | omega_b | 1.646 +/- 0.188 | 20 | `log(A_s*omega_b*(n_s*omega_cdm - 0.0` | {omega_b, omega_cdm, ln10As, n_s} | False | False | 0.80 | 0.960 | 0.997 | 0.922 | 0.574 -> 0.963 | FAIL (omega_b, omega_cdm, H0, tau, ln10As, n_s) |
| z3 | n_s | 1.584 +/- 0.001 | 19 | `H0/omega_cdm**2` | {omega_cdm, H0} | True | False | 0.80 | 0.880 | 0.992 | 0.819 | 0.493 -> 0.864 | FAIL (omega_b, omega_cdm, H0, tau, ln10As, n_s) |
| z4 | tau (amplitude sector) | 0.794 +/- 0.027 | 16 | `tau` | {tau} | False | False | 0.60 | 0.033 | 0.957 | 0.761 | 0.842 -> 0.842 | FAIL (omega_b, omega_cdm, H0, tau, ln10As, n_s) |
| z5 | amplitude (A_s, tau) | 2.743 +/- 0.012 | 17 | `H0*omega_cdm/n_s` | {omega_cdm, H0, n_s} | True | False | 0.80 | 0.919 | 0.993 | 0.609 | 0.289 -> 0.590 | FAIL (omega_b, omega_cdm, H0, ln10As, n_s) |

## Against the additive Phase-6 account

| latent | comb R2(mu) add -> ia | eta_hat_comb add -> ia | st2 residual add -> ia | additive f2 |
|---|---|---|---|---|
| z0 | 0.955 -> 0.954 | 0.842 -> 0.843 | FAIL -> FAIL | `A_s*H0*omega_cdm/n_s` |
| z1 | 0.995 -> 0.995 | 0.663 -> 0.663 | FAIL -> FAIL | `A_s*exp(-2*tau)/omega_b**2` |
| z2 | 0.998 -> 0.997 | 0.963 -> 0.963 | FAIL -> FAIL | `n_s*(A_s + 1.03524857872784e-5*omega` |
| z3 | 0.992 -> 0.992 | 0.864 -> 0.864 | FAIL -> FAIL | `H0/omega_cdm**2` |
| z4 | 0.957 -> 0.957 | 0.842 -> 0.842 | FAIL -> FAIL | `tau` |
| z5 | 0.993 -> 0.993 | 0.590 -> 0.590 | FAIL -> FAIL | `H0*omega_cdm/n_s` |

## z0 — omega_cdm

f2 = `-A_s*H0**2*(f1hat - 10.8708105)` (c=8, support {H0, ln10As, f1hat}, R_SR 1.00, MI vs e1 = 0.499 +/- 0.013)

f1hat = h_full(`omega_cdm/(H0*n_s*omega_b)`): T2 reconstruction max err 0.00e+00; T1 fold scatter p99 2.40e-02 (max 3.60e-02)

Signature g_j: omega_b 0.13, omega_cdm 0.19, H0 0.33, ln10As 0.28, n_s 0.07

Top clusters:

| cluster | representative | C | support | R_SR | best MI |
|---:|---|---:|---|---:|---:|
| 0 | `-A_s*H0**2*(f1hat - 10.8708105)` | 8 | {H0, ln10As, f1hat} | 1.00 | 0.520 |
| 1 | `A_s` | 1 | {ln10As} | 0.00 | 0.240 |

## z1 — H0

f2 = `A_s*exp(-2*tau)/omega_b**2` (c=7, support {omega_b, tau, ln10As}, R_SR 0.80, MI vs e1 = 1.281 +/- 0.013)

f1hat = h_full(`H0**2*omega_cdm`): T2 reconstruction max err 0.00e+00; T1 fold scatter p99 2.09e-02 (max 2.92e-02)

Signature g_j: omega_b 0.41, tau 0.27, ln10As 0.32
* constant ratio (omega_b, tau): r_raw = +45.6546 (cv 0.047)
* constant ratio (omega_b, ln10As): r_raw = -91.3092 (cv 0.047)
* constant ratio (tau, ln10As): r_raw = -2.0000 (cv 0.000)

Top clusters:

| cluster | representative | C | support | R_SR | best MI |
|---:|---|---:|---|---:|---:|
| 1 | `A_s*exp(-2*tau)/omega_b**2` | 7 | {omega_b, tau, ln10As} | 0.80 | 2.138 |
| 2 | `tau + log(omega_b/A_s)` | 6 | {omega_b, tau, ln10As} | 0.00 | 0.758 |
| 0 | `omega_b**2/A_s` | 4 | {omega_b, ln10As} | 0.00 | 0.683 |

## z2 — omega_b

f2 = `log(A_s*omega_b*(n_s*omega_cdm - 0.024653804)**2)` (c=11, support {omega_b, omega_cdm, ln10As, n_s}, R_SR 0.80, MI vs e1 = 1.734 +/- 0.013)

f1hat = h_full(`omega_b/n_s**2`): T2 reconstruction max err 0.00e+00; T1 fold scatter p99 2.02e-02 (max 3.50e-02)

Signature g_j: omega_b 0.13, omega_cdm 0.49, ln10As 0.20, n_s 0.17
* constant ratio (omega_b, ln10As): r_raw = +45.6546 (cv 0.047)
* constant ratio (ln10As, n_s): r_raw = +0.3749 (cv 0.034)

Top clusters:

| cluster | representative | C | support | R_SR | best MI |
|---:|---|---:|---|---:|---:|
| 0 | `log(A_s*omega_b*(n_s*omega_cdm - 0.02465` | 11 | {omega_b, omega_cdm, ln10As, n_s} | 0.80 | 1.851 |
| 1 | `n_s*omega_cdm + omega_b` | 5 | {omega_b, omega_cdm, n_s} | 0.00 | 0.894 |
| 2 | `omega_cdm` | 1 | {omega_cdm} | 0.00 | 0.787 |

## z3 — n_s

f2 = `H0/omega_cdm**2` (c=4, support {omega_cdm, H0}, R_SR 0.80, MI vs e1 = 1.065 +/- 0.013)

f1hat = h_full(`log(omega_b)/(n_s + omega_cdm)`): T2 reconstruction max err 0.00e+00; T1 fold scatter p99 2.35e-02 (max 3.42e-02)

Signature g_j: omega_cdm 0.68, H0 0.32

Top clusters:

| cluster | representative | C | support | R_SR | best MI |
|---:|---|---:|---|---:|---:|
| 0 | `H0/omega_cdm**2` | 4 | {omega_cdm, H0} | 0.80 | 1.588 |
| 1 | `omega_cdm` | 1 | {omega_cdm} | 0.00 | 0.588 |

## z4 — tau (amplitude sector)

f2 = `tau` (c=1, support {tau}, R_SR 0.60, MI vs e1 = 0.702 +/- 0.011)

f1hat = h_full(`-A_s/(tau - 0.4454238)`): T2 reconstruction max err 0.00e+00; T1 fold scatter p99 1.94e-02 (max 2.81e-02)

Signature g_j: tau 1.00

Top clusters:

| cluster | representative | C | support | R_SR | best MI |
|---:|---|---:|---|---:|---:|
| 1 | `tau` | 1 | {tau} | 0.60 | 0.850 |
| 0 | `H0 + f1hat**4 - 111.305844375122*(0.0947` | 12 | {H0, tau, f1hat} | 0.00 | 0.704 |

## z5 — amplitude (A_s, tau)

f2 = `H0*omega_cdm/n_s` (c=5, support {omega_cdm, H0, n_s}, R_SR 0.80, MI vs e1 = 1.250 +/- 0.014)

f1hat = h_full(`A_s*exp(-2*tau)`): T2 reconstruction max err 0.00e+00; T1 fold scatter p99 2.38e-02 (max 3.59e-02)

Signature g_j: omega_cdm 0.43, H0 0.42, n_s 0.15

Top clusters:

| cluster | representative | C | support | R_SR | best MI |
|---:|---|---:|---|---:|---:|
| 0 | `H0*omega_cdm/n_s` | 5 | {omega_cdm, H0, n_s} | 0.80 | 2.783 |

## Shuffled-residual controls

| target | shuffle seed | best MI vs TRUE residual |
|---|---:|---:|
| res_z0 | 0 | 0.026 |
| res_z0 | 1 | 0.014 |
| res_z5 | 0 | 0.035 |
| res_z5 | 1 | 0.053 |

**Definition of done, ia (amplitude z5): theta-support pure shape = True, uses f1hat = False, R_SR = 0.80 -> MET**

---
_Generated by `scripts/consolidate_residual_sr.py`._
