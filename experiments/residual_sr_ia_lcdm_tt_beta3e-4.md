# Residual SR (interaction-aware) — `lcdm_tt_beta3e-4` (post-closure follow-up to roadmap Phase 6)

Blind second-stage SR on the SAME Phase-3 residual caches e1 = mu − h(f1) as Phase 6 (protocol budget, 5 seeds), with one change: the stage-1 prediction **f1hat = h(f1)** is exposed as a 7th input column, so the search can express the amplitude × shape interactions the additive hierarchy could not absorb (deviation D-DoD-z2). Consolidated with the frozen Phase 1–3 machinery; f1hat is registered as a semantics extra input — evaluated as the θ-function h_full(f1(θ)) reconstructed exactly from the T2 rows of the caches, with chain-rule u-gradients — so clustering, signatures, Sobol and supports treat f1hat-bearing forms as θ-functions. The combined account and the stage-2 residual audit are unchanged (g is a 1-D monotone recalibration of f2, which may itself contain f1hat — a multiplicative interaction lives inside f2). DoD (amplitude): the θ-part of f2's support is pure shape-sector (f1hat itself allowed), R_SR >= 0.6.

| latent | role | res plat +/- SE | c* | f2 (rep) | support | theta-shape | f1hat | R_SR | R2 st2(e1) | comb R2(mu) | eta_plat_comb | eta_hat f1 -> f1+f2 | st2 residual |
|---|---|---|---:|---|---|---|---|---:|---:|---:|---:|---|---|
| z0 | omega_b | 1.727 +/- 0.014 | 19 | `n_s*(H0 + 1311.2706*omega_cdm)` | {omega_cdm, H0, n_s} | True | False | 0.80 | 0.887 | 0.989 | 0.688 | 0.531 -> 0.903 | FAIL (omega_b, omega_cdm, H0, tau, ln10As, n_s) |
| z1 | omega_cdm | 1.106 +/- 0.041 | 15 | `omega_b*(tau - (n_s - omega_cdm)**4)` | {omega_b, omega_cdm, H0, tau, n_s} | False | False | 0.80 | 0.797 | 0.981 | 0.858 | 0.770 -> 0.959 | FAIL (omega_cdm, H0, tau, ln10As, n_s) |
| z2 | amplitude (A_s, tau) | 1.468 +/- 0.016 | 20 | `n_s**2*omega_b*tau/(omega_cdm*tau + ` | {omega_b, omega_cdm, tau, n_s} | False | False | 0.80 | 0.862 | 0.993 | 0.630 | 0.347 -> 0.602 | FAIL (omega_b, omega_cdm, H0, tau, ln10As, n_s) |
| z3 | n_s | 1.533 +/- 0.044 | 18 | `(H0 + 89.375175)/(omega_b*omega_cdm)` | {omega_b, omega_cdm, H0} | True | False | 1.00 | 0.863 | 0.988 | 0.821 | 0.447 -> 0.847 | FAIL (omega_b, omega_cdm, tau, ln10As, n_s) |
| z4 | H0 | 2.311 +/- 0.044 | 17 | `(n_s*tau + log(H0))/(n_s*omega_b)` | {omega_b, H0, tau, n_s} | False | False | 0.60 | 0.932 | 0.995 | 0.670 | 0.371 -> 0.787 | FAIL (omega_b, omega_cdm, H0, ln10As, n_s) |

## Against the additive Phase-6 account

| latent | comb R2(mu) add -> ia | eta_hat_comb add -> ia | st2 residual add -> ia | additive f2 |
|---|---|---|---|---|
| z0 | 0.989 -> 0.989 | 0.903 -> 0.903 | FAIL -> FAIL | `n_s*(H0 + 1325.0747*omega_cdm)` |
| z1 | 0.981 -> 0.981 | 0.957 -> 0.959 | FAIL -> FAIL | `n_s/log(-H0/(tau - 0.44653893)) + om` |
| z2 | 0.993 -> 0.993 | 0.601 -> 0.602 | FAIL -> FAIL | `n_s**2*omega_b*tau/(omega_cdm*tau + ` |
| z3 | 0.989 -> 0.988 | 0.838 -> 0.847 | FAIL -> FAIL | `H0/(omega_b**2*omega_cdm**2)` |
| z4 | 0.993 -> 0.995 | 0.758 -> 0.787 | FAIL -> FAIL | `log(H0)/(n_s*omega_b)` |

## z0 — omega_b

f2 = `n_s*(H0 + 1311.2706*omega_cdm)` (c=7, support {omega_cdm, H0, n_s}, R_SR 0.80, MI vs e1 = 1.105 +/- 0.011)

f1hat = h_full(`n_s/omega_b`): T2 reconstruction max err 0.00e+00; T1 fold scatter p99 2.29e-02 (max 3.60e-02)

Signature g_j: omega_cdm 0.50, H0 0.23, n_s 0.26
* constant ratio (omega_cdm, H0): r_raw = +1311.2706 (cv 0.000)

Top clusters:

| cluster | representative | C | support | R_SR | best MI |
|---:|---|---:|---|---:|---:|
| 0 | `n_s*(H0 + 1311.2706*omega_cdm)` | 7 | {omega_cdm, H0, n_s} | 0.80 | 1.766 |
| 1 | `n_s*omega_cdm` | 3 | {omega_cdm, n_s} | 0.00 | 0.800 |
| 2 | `omega_cdm` | 1 | {omega_cdm} | 0.00 | 0.453 |

## z1 — omega_cdm

f2 = `omega_b*(tau - (n_s - omega_cdm)**4)/H0` (c=11, support {omega_b, omega_cdm, H0, tau, n_s}, R_SR 0.80, MI vs e1 = 0.947 +/- 0.014)

f1hat = h_full(`H0**2*n_s**2*omega_b/(A_s*omega_cdm**2)`): T2 reconstruction max err 0.00e+00; T1 fold scatter p99 2.44e-02 (max 3.23e-02)

Signature g_j: omega_b 0.14, omega_cdm 0.12, H0 0.19, tau 0.19, n_s 0.36
* constant ratio (omega_cdm, n_s): r_raw = -1.0000 (cv 0.000)

Top clusters:

| cluster | representative | C | support | R_SR | best MI |
|---:|---|---:|---|---:|---:|
| 0 | `omega_b*(tau - (n_s - omega_cdm)**4)/H0` | 11 | {omega_b, omega_cdm, H0, tau, n_s} | 0.80 | 1.187 |
| 3 | `tau - exp(n_s)` | 4 | {tau, n_s} | 0.00 | 0.650 |
| 2 | `n_s - tau` | 3 | {tau, n_s} | 0.00 | 0.460 |
| 1 | `n_s` | 1 | {n_s} | 0.00 | 0.419 |

## z2 — amplitude (A_s, tau)

f2 = `n_s**2*omega_b*tau/(omega_cdm*tau + 0.0003273979)` (c=10, support {omega_b, omega_cdm, tau, n_s}, R_SR 0.80, MI vs e1 = 1.062 +/- 0.012)

f1hat = h_full(`A_s/log(H0*(omega_cdm + tau))`): T2 reconstruction max err 0.00e+00; T1 fold scatter p99 2.02e-02 (max 2.54e-02)

Signature g_j: omega_b 0.22, omega_cdm 0.30, tau 0.26, n_s 0.22

Top clusters:

| cluster | representative | C | support | R_SR | best MI |
|---:|---|---:|---|---:|---:|
| 0 | `n_s**2*omega_b*tau/(omega_cdm*tau + 0.00` | 10 | {omega_b, omega_cdm, tau, n_s} | 0.80 | 1.511 |
| 1 | `omega_cdm/n_s**2` | 4 | {omega_cdm, n_s} | 0.00 | 0.481 |

## z3 — n_s

f2 = `(H0 + 89.375175)/(omega_b*omega_cdm)` (c=7, support {omega_b, omega_cdm, H0}, R_SR 1.00, MI vs e1 = 1.094 +/- 0.015)

f1hat = h_full(`n_s + omega_cdm`): T2 reconstruction max err 0.00e+00; T1 fold scatter p99 2.43e-02 (max 3.29e-02)

Signature g_j: omega_b 0.33, omega_cdm 0.47, H0 0.20

Top clusters:

| cluster | representative | C | support | R_SR | best MI |
|---:|---|---:|---|---:|---:|
| 0 | `(H0 + 89.375175)/(omega_b*omega_cdm)` | 7 | {omega_b, omega_cdm, H0} | 1.00 | 1.700 |
| 1 | `omega_cdm` | 1 | {omega_cdm} | 0.00 | 0.444 |

## z4 — H0

f2 = `(n_s*tau + log(H0))/(n_s*omega_b)` (c=8, support {omega_b, H0, tau, n_s}, R_SR 0.60, MI vs e1 = 1.382 +/- 0.010)

f1hat = h_full(`A_s*H0**2*omega_cdm*exp(-2*tau)`): T2 reconstruction max err 0.00e+00; T1 fold scatter p99 2.64e-02 (max 3.11e-02)

Signature g_j: omega_b 0.51, H0 0.16, tau 0.07, n_s 0.25
* constant ratio (tau, n_s): r_raw = -0.2190 (cv 0.050)

Top clusters:

| cluster | representative | C | support | R_SR | best MI |
|---:|---|---:|---|---:|---:|
| 0 | `(n_s*tau + log(H0))/(n_s*omega_b)` | 8 | {omega_b, H0, tau, n_s} | 0.60 | 2.400 |
| 1 | `omega_b` | 1 | {omega_b} | 0.00 | 0.640 |

## Shuffled-residual controls

| target | shuffle seed | best MI vs TRUE residual |
|---|---:|---:|
| res_z2 | 0 | 0.010 |
| res_z2 | 1 | 0.040 |

**Definition of done, ia (amplitude z2): theta-support pure shape = False, uses f1hat = False, R_SR = 0.80 -> NOT MET**

---
_Generated by `scripts/consolidate_residual_sr.py`._
