# Residual SR — `lcdm_tt_ee_lowl` (roadmap Phase 6)

Blind second-stage SR on the Phase-3 residual caches e1 = mu − h(f1) (all-6 inputs, protocol budget, 5 seeds), consolidated with the frozen Phase 1–3 machinery. f2 = canonical residual coordinate (most recurrent cluster at the residual knee). Hierarchical account: combined yhat = h(f1) + g(f2), both stages cross-fitted on T1; eta_post ratios on T2 against the Phase-5 ceiling (same posterior draw). Stage-2 residual audited with the frozen rule (R2 <= 0.05 AND max MI <= null p97.5) — PASS means the hierarchy terminates at two levels. Shuffled-residual controls give the residual-MI null.

| latent | role | res plat +/- SE | c* | f2 (rep) | support | shape-sector | R_SR | R2 st2(e1) | comb R2(mu) | eta_plat_comb | eta_hat f1 -> f1+f2 | st2 residual |
|---|---|---|---:|---|---|---|---:|---:|---:|---:|---|---|
| z0 | omega_cdm | 0.505 +/- 0.006 | 14 | `A_s*H0*omega_cdm/n_s` | {omega_cdm, H0, ln10As, n_s} | False | 0.80 | 0.406 | 0.955 | 0.925 | 0.756 -> 0.842 | FAIL (omega_b, omega_cdm, tau, ln10As, n_s) |
| z1 | H0 | 2.084 +/- 0.044 | 19 | `A_s*exp(-2*tau)/omega_b**2` | {omega_b, tau, ln10As} | False | 0.80 | 0.921 | 0.995 | 0.652 | 0.348 -> 0.663 | FAIL (omega_b, omega_cdm, H0, tau, ln10As, n_s) |
| z2 | omega_b | 1.629 +/- 0.184 | 11 | `n_s*(A_s + 1.03524857872784e-5*omega` | {omega_b, omega_cdm, ln10As, n_s} | False | 0.80 | 0.966 | 0.998 | 0.933 | 0.574 -> 0.963 | FAIL (omega_b, omega_cdm, H0, tau, ln10As, n_s) |
| z3 | n_s | 1.594 +/- 0.008 | 16 | `H0/omega_cdm**2` | {omega_cdm, H0} | True | 0.80 | 0.880 | 0.992 | 0.819 | 0.493 -> 0.864 | FAIL (omega_b, omega_cdm, H0, tau, ln10As, n_s) |
| z4 | tau (amplitude sector) | 0.827 +/- 0.013 | 17 | `tau` | {tau} | False | 0.80 | 0.033 | 0.957 | 0.761 | 0.842 -> 0.842 | FAIL (omega_b, omega_cdm, H0, tau, ln10As, n_s) |
| z5 | amplitude (A_s, tau) | 2.735 +/- 0.003 | 15 | `H0*omega_cdm/n_s` | {omega_cdm, H0, n_s} | True | 0.80 | 0.919 | 0.993 | 0.609 | 0.289 -> 0.590 | FAIL (omega_b, omega_cdm, H0, ln10As, n_s) |

## z0 — omega_cdm

f2 = `A_s*H0*omega_cdm/n_s` (c=7, support {omega_cdm, H0, ln10As, n_s}, R_SR 0.80, MI vs e1 = 0.401 +/- 0.010)

Signature g_j: omega_cdm 0.29, H0 0.29, ln10As 0.32, n_s 0.11
* constant ratio (ln10As, n_s): r_raw = -0.9657 (cv 0.025)

Top clusters:

| cluster | representative | C | support | R_SR | best MI |
|---:|---|---:|---|---:|---:|
| 0 | `A_s*H0*omega_cdm/n_s` | 7 | {omega_cdm, H0, ln10As, n_s} | 0.80 | 0.517 |
| 1 | `A_s` | 1 | {ln10As} | 0.00 | 0.240 |

## z1 — H0

f2 = `A_s*exp(-2*tau)/omega_b**2` (c=7, support {omega_b, tau, ln10As}, R_SR 0.80, MI vs e1 = 1.281 +/- 0.013)

Signature g_j: omega_b 0.41, tau 0.27, ln10As 0.32
* constant ratio (omega_b, tau): r_raw = +45.6546 (cv 0.047)
* constant ratio (omega_b, ln10As): r_raw = -91.3092 (cv 0.047)
* constant ratio (tau, ln10As): r_raw = -2.0000 (cv 0.000)

Top clusters:

| cluster | representative | C | support | R_SR | best MI |
|---:|---|---:|---|---:|---:|
| 0 | `A_s*exp(-2*tau)/omega_b**2` | 7 | {omega_b, tau, ln10As} | 0.80 | 2.179 |
| 2 | `tau + log(omega_b/A_s)` | 6 | {omega_b, tau, ln10As} | 0.00 | 0.758 |
| 1 | `omega_b**2/A_s` | 4 | {omega_b, ln10As} | 0.00 | 0.683 |

## z2 — omega_b

f2 = `n_s*(A_s + 1.03524857872784e-5*omega_b*omega_cdm**2)` (c=10, support {omega_b, omega_cdm, ln10As, n_s}, R_SR 0.80, MI vs e1 = 1.765 +/- 0.013)

Signature g_j: omega_b 0.17, omega_cdm 0.49, ln10As 0.18, n_s 0.15
* constant ratio (omega_cdm, n_s): r_raw = +9.8764 (cv 0.041)

Top clusters:

| cluster | representative | C | support | R_SR | best MI |
|---:|---|---:|---|---:|---:|
| 0 | `n_s*(A_s + 1.03524857872784e-5*omega_b*o` | 10 | {omega_b, omega_cdm, ln10As, n_s} | 0.80 | 1.844 |
| 1 | `n_s*omega_cdm + omega_b` | 5 | {omega_b, omega_cdm, n_s} | 0.00 | 0.894 |
| 2 | `omega_cdm` | 1 | {omega_cdm} | 0.00 | 0.787 |

## z3 — n_s

f2 = `H0/omega_cdm**2` (c=4, support {omega_cdm, H0}, R_SR 0.80, MI vs e1 = 1.065 +/- 0.013)

Signature g_j: omega_cdm 0.68, H0 0.32

Top clusters:

| cluster | representative | C | support | R_SR | best MI |
|---:|---|---:|---|---:|---:|
| 0 | `H0/omega_cdm**2` | 4 | {omega_cdm, H0} | 0.80 | 1.613 |
| 1 | `omega_cdm` | 1 | {omega_cdm} | 0.00 | 0.588 |

## z4 — tau (amplitude sector)

f2 = `tau` (c=1, support {tau}, R_SR 0.80, MI vs e1 = 0.702 +/- 0.011)

Signature g_j: tau 1.00

Top clusters:

| cluster | representative | C | support | R_SR | best MI |
|---:|---|---:|---|---:|---:|
| 0 | `tau` | 1 | {tau} | 0.80 | 0.858 |

## z5 — amplitude (A_s, tau)

f2 = `H0*omega_cdm/n_s` (c=5, support {omega_cdm, H0, n_s}, R_SR 0.80, MI vs e1 = 1.250 +/- 0.014)

Signature g_j: omega_cdm 0.43, H0 0.42, n_s 0.15

Top clusters:

| cluster | representative | C | support | R_SR | best MI |
|---:|---|---:|---|---:|---:|
| 0 | `H0*omega_cdm/n_s` | 5 | {omega_cdm, H0, n_s} | 0.80 | 2.746 |

## Shuffled-residual controls

| target | shuffle seed | best MI vs TRUE residual |
|---|---:|---:|
| res_z5 | 0 | 0.009 |
| res_z5 | 1 | 0.060 |

**Definition of done (amplitude z5): f2 shape-sector = True, R_SR = 0.80 -> MET**

---
_Generated by `scripts/consolidate_residual_sr.py`._
