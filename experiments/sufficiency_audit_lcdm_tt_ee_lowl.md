# Sufficiency audit — `lcdm_tt_ee_lowl` (roadmap Phase 3, gate G1)

Per latent: the Phase-2 canonical coordinate audited with the sensitivity signature (normalised E|df/du_j| on the T1 anchors), Sobol indices on the prior box, constant-ratio pairs (the answer-agnostic -2 detector), and the calibrated sufficiency test: 5-fold cross-fitted monotone h on T1, residual e = mu - h(f), R2_res via single-threaded HistGBM and per-parameter GMM-MI against permutation nulls (frozen rule: R2_res <= 0.05 AND max-MI <= max-null p97.5). `^` marks parameters above their per-parameter null. Residuals over all 50k rows are cached as `analysis/residual_z<k>_v1.npy` for Phase 6.

## Draft latent cards v0

| latent | audit-expected | canonical coordinate | R_SR | eta_plat | R2_res | residual | draft status |
|---|---|---|---:|---:|---:|---|---|
| z0 | omega_cdm | `omega_cdm/(H0*n_s*omega_b)` | 1.00 | 0.732 | 0.960 | FAIL | primarily interpreted (draft) |
| z1 | H0 | `H0**2*omega_cdm` | 1.00 | 0.338 | 0.993 | FAIL | primarily interpreted (draft) |
| z2 | omega_b | `omega_b/n_s**2` | 1.00 | 0.394 | 0.993 | FAIL | primarily interpreted (draft) |
| z3 | n_s | `log(omega_b)/(n_s + omega_cdm)` | 0.80 | 0.424 | 0.991 | FAIL | primarily interpreted (draft) |
| z4 | tau (amplitude sector) | `-A_s/(tau - 0.4454238)` | 1.00 | 0.734 | 0.980 | FAIL | primarily interpreted (draft) |
| z5 | amplitude (A_s, tau) | `A_s*exp(-2*tau)` | 1.00 | 0.292 | 0.994 | FAIL | primarily interpreted (draft) |

_Pending card components: eta_S (Phase 4), eta_post (Phase 5), level-set E_inv (Phase 7), subspace probe (Phase 8)._


## z0 — omega_cdm

Canonical coordinate (R_SR 1.00): `omega_cdm/(H0*n_s*omega_b)`

| param | g_j | Sobol S1 | Sobol ST | MI(e;theta_j) | null p97.5 |
|---|---|---:|---:|---:|---:|
| omega_b | `###.........` 0.23 | 0.190 | 0.191 | 0.014 **^** | 0.008 |
| omega_cdm | `####........` 0.33 | 0.387 | 0.390 | 0.063 **^** | 0.006 |
| H0 | `####........` 0.32 | 0.370 | 0.373 | 0.171 **^** | 0.006 |
| tau | `............` 0.00 | 0.000 | 0.000 | 0.019 **^** | 0.008 |
| ln10As | `............` 0.00 | 0.000 | 0.000 | 0.220 **^** | 0.014 |
| n_s | `#...........` 0.12 | 0.050 | 0.050 | 0.013 **^** | 0.010 |

No constant-ratio pair (no fixed linear combination).

MI(f; mu) = 1.308 +/- 0.013, eta_plat = 0.732; calibration R2 = 0.924; R2_res = 0.960 (null p97.5 -0.002); max MI(e;theta) 0.220 vs max-null p97.5 0.014 -> residual FAIL (loadings: omega_b, omega_cdm, H0, tau, ln10As, n_s)

## z1 — H0

Canonical coordinate (R_SR 1.00): `H0**2*omega_cdm`

| param | g_j | Sobol S1 | Sobol ST | MI(e;theta_j) | null p97.5 |
|---|---|---:|---:|---:|---:|
| omega_b | `............` 0.00 | -0.000 | 0.000 | 0.357 **^** | 0.001 |
| omega_cdm | `####........` 0.34 | 0.210 | 0.214 | 0.012 **^** | 0.001 |
| H0 | `########....` 0.66 | 0.786 | 0.790 | 0.002 **^** | 0.000 |
| tau | `............` 0.00 | -0.000 | 0.000 | 0.093 **^** | 0.000 |
| ln10As | `............` 0.00 | -0.000 | 0.000 | 0.128 **^** | 0.001 |
| n_s | `............` 0.00 | -0.000 | 0.000 | 0.019 **^** | 0.000 |

No constant-ratio pair (no fixed linear combination).

MI(f; mu) = 1.353 +/- 0.009, eta_plat = 0.338; calibration R2 = 0.931; R2_res = 0.993 (null p97.5 -0.002); max MI(e;theta) 0.357 vs max-null p97.5 0.001 -> residual FAIL (loadings: omega_b, omega_cdm, H0, tau, ln10As, n_s)

## z2 — omega_b

Canonical coordinate (R_SR 1.00): `omega_b/n_s**2`

| param | g_j | Sobol S1 | Sobol ST | MI(e;theta_j) | null p97.5 |
|---|---|---:|---:|---:|---:|
| omega_b | `######......` 0.49 | 0.486 | 0.487 | 0.044 **^** | 0.001 |
| omega_cdm | `............` 0.00 | 0.000 | 0.000 | 0.640 **^** | 0.001 |
| H0 | `............` 0.00 | 0.000 | 0.000 | 0.002 **^** | 0.001 |
| tau | `............` 0.00 | 0.000 | 0.000 | 0.000 | 0.001 |
| ln10As | `............` 0.00 | 0.000 | 0.000 | 0.052 **^** | 0.001 |
| n_s | `######......` 0.51 | 0.513 | 0.514 | 0.042 **^** | 0.000 |

No constant-ratio pair (no fixed linear combination).

MI(f; mu) = 1.311 +/- 0.012, eta_plat = 0.394; calibration R2 = 0.927; R2_res = 0.993 (null p97.5 -0.002); max MI(e;theta) 0.640 vs max-null p97.5 0.001 -> residual FAIL (loadings: omega_b, omega_cdm, H0, ln10As, n_s)

## z3 — n_s

Canonical coordinate (R_SR 0.80): `log(omega_b)/(n_s + omega_cdm)`

| param | g_j | Sobol S1 | Sobol ST | MI(e;theta_j) | null p97.5 |
|---|---|---:|---:|---:|---:|
| omega_b | `####........` 0.30 | 0.227 | 0.228 | 0.012 **^** | 0.001 |
| omega_cdm | `##..........` 0.17 | 0.077 | 0.077 | 0.548 **^** | 0.000 |
| H0 | `............` 0.00 | -0.000 | 0.000 | 0.116 **^** | 0.000 |
| tau | `............` 0.00 | -0.000 | 0.000 | 0.000 | 0.001 |
| ln10As | `............` 0.00 | -0.000 | 0.000 | 0.001 **^** | 0.001 |
| n_s | `######......` 0.52 | 0.695 | 0.695 | 0.037 **^** | 0.000 |

Constant-ratio pairs (cv < 5%):
* (omega_b, omega_cdm): r_raw = +12.9095 (cv 0.039, valid 100%)
* (omega_b, n_s): r_raw = +12.9095 (cv 0.039, valid 100%)
* (omega_cdm, n_s): r_raw = +1.0000 (cv 0.000, valid 100%)

MI(f; mu) = 1.363 +/- 0.013, eta_plat = 0.424; calibration R2 = 0.935; R2_res = 0.991 (null p97.5 -0.002); max MI(e;theta) 0.548 vs max-null p97.5 0.001 -> residual FAIL (loadings: omega_b, omega_cdm, H0, ln10As, n_s)

## z4 — tau (amplitude sector)

Canonical coordinate (R_SR 1.00): `-A_s/(tau - 0.4454238)`

| param | g_j | Sobol S1 | Sobol ST | MI(e;theta_j) | null p97.5 |
|---|---|---:|---:|---:|---:|
| omega_b | `............` 0.00 | 0.000 | 0.000 | 0.051 **^** | 0.011 |
| omega_cdm | `............` 0.00 | 0.000 | 0.000 | 0.024 **^** | 0.016 |
| H0 | `............` 0.00 | 0.000 | 0.000 | 0.035 **^** | 0.014 |
| tau | `######......` 0.54 | 0.569 | 0.573 | 0.690 **^** | 0.017 |
| ln10As | `######......` 0.46 | 0.427 | 0.431 | 0.046 **^** | 0.014 |
| n_s | `............` 0.00 | 0.000 | 0.000 | 0.050 **^** | 0.016 |

No constant-ratio pair (no fixed linear combination).

MI(f; mu) = 1.739 +/- 0.013, eta_plat = 0.734; calibration R2 = 0.955; R2_res = 0.980 (null p97.5 -0.003); max MI(e;theta) 0.690 vs max-null p97.5 0.019 -> residual FAIL (loadings: omega_b, omega_cdm, H0, tau, ln10As, n_s)

## z5 — amplitude (A_s, tau)

Canonical coordinate (R_SR 1.00): `A_s*exp(-2*tau)`

| param | g_j | Sobol S1 | Sobol ST | MI(e;theta_j) | null p97.5 |
|---|---|---:|---:|---:|---:|
| omega_b | `............` 0.00 | 0.000 | 0.000 | 0.019 **^** | 0.000 |
| omega_cdm | `............` 0.00 | 0.000 | 0.000 | 0.455 **^** | 0.000 |
| H0 | `............` 0.00 | 0.000 | 0.000 | 0.146 **^** | 0.001 |
| tau | `######......` 0.46 | 0.423 | 0.425 | 0.000 | 0.001 |
| ln10As | `######......` 0.54 | 0.575 | 0.578 | 0.000 | 0.000 |
| n_s | `............` 0.00 | 0.000 | 0.000 | 0.049 **^** | 0.000 |

Constant-ratio pairs (cv < 5%):
* (tau, ln10As): r_raw = -2.0000 (cv 0.000, valid 100%)

MI(f; mu) = 1.194 +/- 0.012, eta_plat = 0.292; calibration R2 = 0.910; R2_res = 0.994 (null p97.5 -0.002); max MI(e;theta) 0.455 vs max-null p97.5 0.001 -> residual FAIL (loadings: omega_b, omega_cdm, H0, n_s)

### Gate G1 (amplitude positive control)

Knee-slice 2-var coordinate: `A_s*exp(-2*tau)` (c=5, stored MI 1.198); reference ceiling 1.196 nat, stored r -1.9995.

| param | g_j | Sobol S1 | Sobol ST | MI(e;theta_j) | null p97.5 |
|---|---|---:|---:|---:|---:|
| omega_b | `............` 0.00 | 0.000 | 0.000 | 0.016 **^** | 0.001 |
| omega_cdm | `............` 0.00 | 0.000 | 0.000 | 0.463 **^** | 0.001 |
| H0 | `............` 0.00 | 0.000 | 0.000 | 0.150 **^** | 0.001 |
| tau | `######......` 0.46 | 0.423 | 0.425 | 0.001 **^** | 0.000 |
| ln10As | `######......` 0.54 | 0.575 | 0.578 | 0.001 | 0.001 |
| n_s | `............` 0.00 | 0.000 | 0.000 | 0.053 **^** | 0.001 |

Constant-ratio pairs (cv < 5%):
* (tau, ln10As): r_raw = -2.0000 (cv 0.000, valid 100%)

MI(f; mu) = 1.214 +/- 0.012; calibration R2 = 0.910; R2_res = 0.994 (null p97.5 -0.002); max MI(e;theta) 0.463 vs max-null p97.5 0.001 -> residual FAIL (loadings: omega_b, omega_cdm, H0, tau, n_s)

| G1 bullet | numbers | pass |
|---|---|---|
| slice support + recurrence | support {tau, ln10As}, slice recurrence 1.00, joins canonical cluster: True | PASS |
| amplitude direction r | latent-level r_lin = -1.9953 (stored -1.9995); form-level r = -2.0000 (cv 0.000), legacy midpoint -2.0000 | PASS |
| eta_S vs reference | 1.015 | PASS |
| residual fails structured | R2_res 0.994, shape loadings H0, n_s, omega_b, omega_cdm | PASS |

**G1 verdict: PASS**

### Shuffled-control audit (negative control)

| shuffle seed | MI vs TRUE latent | R2_cal | R2_res |
|---:|---:|---:|---:|
| 0 | 0.131 | 0.216 | 0.995 |
| 1 | 0.233 | 0.315 | 0.995 |
| 2 | 0.057 | 0.100 | 0.995 |

_Control coordinates explain ~nothing of the true latent (MI, R2_cal ~ 0), so their residual is the latent itself and R2_res is trivially high — the audit correctly reports total insufficiency._

---
_Generated by `scripts/sufficiency_audit.py`._
