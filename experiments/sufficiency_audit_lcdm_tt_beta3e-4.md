# Sufficiency audit — `lcdm_tt_beta3e-4` (roadmap Phase 3, gate G1)

Per latent: the Phase-2 canonical coordinate audited with the sensitivity signature (normalised E|df/du_j| on the T1 anchors), Sobol indices on the prior box, constant-ratio pairs (the answer-agnostic -2 detector), and the calibrated sufficiency test: 5-fold cross-fitted monotone h on T1, residual e = mu - h(f), R2_res via single-threaded HistGBM and per-parameter GMM-MI against permutation nulls (frozen rule: R2_res <= 0.05 AND max-MI <= max-null p97.5). `^` marks parameters above their per-parameter null. Residuals over all 50k rows are cached as `analysis/residual_z<k>_v1.npy` for Phase 6.

## Draft latent cards v0

| latent | audit-expected | canonical coordinate | R_SR | eta_plat | R2_res | residual | draft status |
|---|---|---|---:|---:|---:|---|---|
| z0 | omega_b | `n_s/omega_b` | 1.00 | 0.326 | 0.992 | FAIL | primarily interpreted (draft) |
| z1 | omega_cdm | `H0**2*n_s**2*omega_b/(A_s*omega_cdm**2)` | 0.80 | 0.475 | 0.981 | FAIL | primarily interpreted (draft) |
| z2 | amplitude (A_s, tau) | `A_s/log(H0*(omega_cdm + tau))` | 1.00 | 0.352 | 0.985 | FAIL | primarily interpreted (draft) |
| z3 | n_s | `n_s + omega_cdm` | 1.00 | 0.379 | 0.993 | FAIL | primarily interpreted (draft) |
| z4 | H0 | `A_s*H0**2*omega_cdm*exp(-2*tau)` | 0.80 | 0.301 | 0.989 | FAIL | primarily interpreted (draft) |

_Pending card components: eta_S (Phase 4), eta_post (Phase 5), level-set E_inv (Phase 7), subspace probe (Phase 8)._


## z0 — omega_b

Canonical coordinate (R_SR 1.00): `n_s/omega_b`

| param | g_j | Sobol S1 | Sobol ST | MI(e;theta_j) | null p97.5 |
|---|---|---:|---:|---:|---:|
| omega_b | `########....` 0.66 | 0.792 | 0.793 | 0.040 **^** | 0.001 |
| omega_cdm | `............` 0.00 | 0.000 | 0.000 | 0.450 **^** | 0.001 |
| H0 | `............` 0.00 | 0.000 | 0.000 | 0.056 **^** | 0.001 |
| tau | `............` 0.00 | 0.000 | 0.000 | 0.001 **^** | 0.000 |
| ln10As | `............` 0.00 | 0.000 | 0.000 | 0.014 **^** | 0.001 |
| n_s | `####........` 0.34 | 0.207 | 0.208 | 0.092 **^** | 0.001 |

No constant-ratio pair (no fixed linear combination).

MI(f; mu) = 1.162 +/- 0.010, eta_plat = 0.326; calibration R2 = 0.904; R2_res = 0.992 (null p97.5 -0.002); max MI(e;theta) 0.450 vs max-null p97.5 0.001 -> residual FAIL (loadings: omega_b, omega_cdm, H0, tau, ln10As, n_s)

## z1 — omega_cdm

Canonical coordinate (R_SR 0.80): `H0**2*n_s**2*omega_b/(A_s*omega_cdm**2)`

| param | g_j | Sobol S1 | Sobol ST | MI(e;theta_j) | null p97.5 |
|---|---|---:|---:|---:|---:|
| omega_b | `#...........` 0.11 | 0.049 | 0.050 | 0.020 **^** | 0.001 |
| omega_cdm | `####........` 0.32 | 0.402 | 0.414 | 0.009 **^** | 0.001 |
| H0 | `####........` 0.30 | 0.367 | 0.381 | 0.056 **^** | 0.000 |
| tau | `............` 0.00 | 0.000 | 0.000 | 0.097 **^** | 0.000 |
| ln10As | `##..........` 0.17 | 0.114 | 0.119 | 0.015 **^** | 0.001 |
| n_s | `#...........` 0.11 | 0.052 | 0.053 | 0.393 **^** | 0.000 |

Constant-ratio pairs (cv < 5%):
* (omega_b, ln10As): r_raw = -45.6546 (cv 0.047, valid 100%)
* (ln10As, n_s): r_raw = -0.4829 (cv 0.025, valid 100%)

MI(f; mu) = 1.193 +/- 0.013, eta_plat = 0.475; calibration R2 = 0.906; R2_res = 0.981 (null p97.5 -0.002); max MI(e;theta) 0.393 vs max-null p97.5 0.001 -> residual FAIL (loadings: omega_b, omega_cdm, H0, tau, ln10As, n_s)

## z2 — amplitude (A_s, tau)

Canonical coordinate (R_SR 1.00): `A_s/log(H0*(omega_cdm + tau))`

| param | g_j | Sobol S1 | Sobol ST | MI(e;theta_j) | null p97.5 |
|---|---|---:|---:|---:|---:|
| omega_b | `............` 0.00 | -0.000 | 0.000 | 0.121 **^** | 0.000 |
| omega_cdm | `#...........` 0.10 | 0.029 | 0.033 | 0.199 **^** | 0.000 |
| H0 | `##..........` 0.14 | 0.060 | 0.063 | 0.020 **^** | 0.000 |
| tau | `#####.......` 0.38 | 0.433 | 0.441 | 0.092 **^** | 0.001 |
| ln10As | `#####.......` 0.38 | 0.468 | 0.471 | 0.002 **^** | 0.001 |
| n_s | `............` 0.00 | -0.000 | 0.000 | 0.125 **^** | 0.001 |

Constant-ratio pairs (cv < 5%):
* (omega_cdm, tau): r_raw = +1.0000 (cv 0.000, valid 100%)

MI(f; mu) = 1.470 +/- 0.012, eta_plat = 0.352; calibration R2 = 0.947; R2_res = 0.985 (null p97.5 -0.002); max MI(e;theta) 0.199 vs max-null p97.5 0.001 -> residual FAIL (loadings: omega_b, omega_cdm, H0, tau, ln10As, n_s)

### Gate G1 (amplitude positive control)

Knee-slice 2-var coordinate: `-A_s*(tau - 0.5976987)` (c=5, stored MI 0.824); reference ceiling 0.822 nat, stored r -1.988.

| param | g_j | Sobol S1 | Sobol ST | MI(e;theta_j) | null p97.5 |
|---|---|---:|---:|---:|---:|
| omega_b | `............` 0.00 | -0.000 | 0.000 | 0.031 **^** | 0.000 |
| omega_cdm | `............` 0.00 | -0.000 | 0.000 | 0.287 **^** | 0.000 |
| H0 | `............` 0.00 | -0.000 | 0.000 | 0.278 **^** | 0.001 |
| tau | `#####.......` 0.45 | 0.397 | 0.399 | 0.001 **^** | 0.000 |
| ln10As | `#######.....` 0.55 | 0.601 | 0.603 | 0.000 | 0.000 |
| n_s | `............` 0.00 | -0.000 | 0.000 | 0.037 **^** | 0.001 |

No constant-ratio pair (no fixed linear combination).

MI(f; mu) = 0.822 +/- 0.012; calibration R2 = 0.807; R2_res = 0.994 (null p97.5 -0.002); max MI(e;theta) 0.287 vs max-null p97.5 0.001 -> residual FAIL (loadings: omega_b, omega_cdm, H0, tau, n_s)

| G1 bullet | numbers | pass |
|---|---|---|
| slice support + recurrence | support {tau, ln10As}, slice recurrence 1.00, joins canonical cluster: False | PASS |
| amplitude direction r | latent-level r_lin = -1.9767 (stored -1.988); form-level no pair at cv<5% (Taylor curvature), legacy midpoint -1.8950 | PASS |
| eta_S vs reference | 1.000 | PASS |
| residual fails structured | R2_res 0.994, shape loadings H0, n_s, omega_b, omega_cdm | PASS |

**G1 verdict: PASS**

### Shuffled-control audit (negative control)

| shuffle seed | MI vs TRUE latent | R2_cal | R2_res |
|---:|---:|---:|---:|
| 0 | 0.181 | 0.274 | 0.989 |
| 1 | 0.245 | 0.379 | 0.996 |
| 2 | 0.001 | 0.053 | 0.996 |

_Control coordinates explain ~nothing of the true latent (MI, R2_cal ~ 0), so their residual is the latent itself and R2_res is trivially high — the audit correctly reports total insufficiency._

## z3 — n_s

Canonical coordinate (R_SR 1.00): `n_s + omega_cdm`

| param | g_j | Sobol S1 | Sobol ST | MI(e;theta_j) | null p97.5 |
|---|---|---:|---:|---:|---:|
| omega_b | `............` 0.00 | -0.000 | 0.000 | 0.121 **^** | 0.000 |
| omega_cdm | `###.........` 0.25 | 0.100 | 0.100 | 0.440 **^** | 0.001 |
| H0 | `............` 0.00 | -0.000 | 0.000 | 0.051 **^** | 0.000 |
| tau | `............` 0.00 | -0.000 | 0.000 | 0.005 **^** | 0.001 |
| ln10As | `............` 0.00 | -0.000 | 0.000 | 0.002 **^** | 0.001 |
| n_s | `#########...` 0.75 | 0.900 | 0.900 | 0.030 **^** | 0.000 |

Constant-ratio pairs (cv < 5%):
* (omega_cdm, n_s): r_raw = +1.0000 (cv 0.000, valid 100%)

MI(f; mu) = 1.194 +/- 0.011, eta_plat = 0.379; calibration R2 = 0.916; R2_res = 0.993 (null p97.5 -0.002); max MI(e;theta) 0.440 vs max-null p97.5 0.001 -> residual FAIL (loadings: omega_b, omega_cdm, H0, tau, ln10As, n_s)

## z4 — H0

Canonical coordinate (R_SR 0.80): `A_s*H0**2*omega_cdm*exp(-2*tau)`

| param | g_j | Sobol S1 | Sobol ST | MI(e;theta_j) | null p97.5 |
|---|---|---:|---:|---:|---:|
| omega_b | `............` 0.00 | -0.001 | 0.000 | 0.596 **^** | 0.000 |
| omega_cdm | `##..........` 0.20 | 0.146 | 0.151 | 0.001 **^** | 0.000 |
| H0 | `#####.......` 0.39 | 0.548 | 0.558 | 0.033 **^** | 0.001 |
| tau | `##..........` 0.19 | 0.124 | 0.128 | 0.012 **^** | 0.001 |
| ln10As | `###.........` 0.22 | 0.169 | 0.174 | 0.022 **^** | 0.001 |
| n_s | `............` 0.00 | -0.001 | 0.000 | 0.078 **^** | 0.000 |

Constant-ratio pairs (cv < 5%):
* (tau, ln10As): r_raw = -2.0000 (cv 0.000, valid 100%)

MI(f; mu) = 1.297 +/- 0.011, eta_plat = 0.301; calibration R2 = 0.921; R2_res = 0.989 (null p97.5 -0.002); max MI(e;theta) 0.596 vs max-null p97.5 0.001 -> residual FAIL (loadings: omega_b, omega_cdm, H0, tau, ln10As, n_s)

---
_Generated by `scripts/sufficiency_audit.py`._
