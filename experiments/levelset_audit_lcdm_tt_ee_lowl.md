# Level-set invariance audit — `lcdm_tt_ee_lowl` (roadmap Phase 7a, gate G4a)

Per latent: the Phase-2 canonical coordinate f, quantile-binned into 200 equal-count bins on T1; within-bin disjoint pairs maximising nuisance distance ||Δu_(S^c)|| (≤ 25/bin). E_inv = E[(mu−mu')²|pair]/(2 Var mu), normalised so random pairs = 1 (empirical random reference alongside); frozen pass rule E_inv <= 0.05. Response test: k-NN nuisance matching (caliper = q0.05 of random nuisance distances), cross-fitted general spline R² of mu vs f >= 0.9. T2 = independent confirmation pass. Latents whose canonical support is all 6 parameters have no nuisance direction: E_inv is undefined there (levelset_pass = None) and only the response R² is reported.

| latent | role | support | E_inv +/- SE | expected band | rand ref | top-quartile | R2 resp (n) | T2 E_inv | T2 R2 | pass |
|---|---|---|---|---|---:|---:|---|---:|---:|---|
| z0 | omega_cdm | {omega_b, omega_cdm, H0, n_s} | 0.138 +/- 0.002 | 0.076–0.153 | 1.03 | 0.211 | 0.920 (12682) | 0.150 | 0.926 | False |
| z1 | H0 | {omega_cdm, H0} | 0.169 +/- 0.003 | 0.069–0.137 | 1.01 | 0.224 | 0.933 (12619) | 0.178 | 0.934 | False |
| z2 | omega_b | {omega_b, n_s} | 0.164 +/- 0.002 | 0.073–0.145 | 0.98 | 0.211 | 0.929 (12643) | 0.174 | 0.933 | False |
| z3 | n_s | {omega_b, omega_cdm, n_s} | 0.086 +/- 0.001 | 0.065–0.129 | 1.01 | 0.096 | 0.936 (12822) | 0.093 | 0.936 | False |
| z4 | tau (amplitude sector) | {tau, ln10As} | 0.051 +/- 0.001 | 0.045–0.089 | 1.02 | 0.058 | 0.955 (12354) | 0.052 | 0.956 | False |
| z5 | amplitude (A_s, tau) | {tau, ln10As} | 0.226 +/- 0.003 | 0.090–0.180 | 1.01 | 0.304 | 0.913 (12543) | 0.241 | 0.915 | False |

_Expected band = [1−R²_cal, 2(1−R²_cal)] from the Phase-3 calibration: within-level-set movement of mu IS the structured residual, so for a latent whose f1 leaves a residual, E_inv cannot sit below 1−R²_cal (upper end when the residual is anti-correlated across nuisance space). E_inv landing inside the band while the response R² passes says the audit and the Phase-3 calibration agree: f1 is the primary 1-D coordinate, and the invariance failure is exactly the structured residual Phase 6 targets — not a confounded response._


## z0 — omega_cdm

Canonical `omega_cdm/(H0*n_s*omega_b)`; support {omega_b, omega_cdm, H0, n_s}, complement {tau, ln10As}; 5000 pairs, mean nuisance distance 1.96.

E_inv vs nuisance distance:
| d range | E_inv | n |
|---|---:|---:|
| 1.38–1.75 | 0.090 | 1250 |
| 1.75–1.92 | 0.111 | 1250 |
| 1.92–2.13 | 0.138 | 1250 |
| 2.13–2.75 | 0.211 | 1250 |

## z1 — H0

Canonical `H0**2*omega_cdm`; support {omega_cdm, H0}, complement {omega_b, tau, ln10As, n_s}; 5000 pairs, mean nuisance distance 2.58.

E_inv vs nuisance distance:
| d range | E_inv | n |
|---|---:|---:|
| 2.02–2.36 | 0.118 | 1250 |
| 2.36–2.54 | 0.154 | 1250 |
| 2.54–2.76 | 0.178 | 1250 |
| 2.76–3.50 | 0.224 | 1250 |

## z2 — omega_b

Canonical `omega_b/n_s**2`; support {omega_b, n_s}, complement {omega_cdm, H0, tau, ln10As}; 5000 pairs, mean nuisance distance 2.57.

E_inv vs nuisance distance:
| d range | E_inv | n |
|---|---:|---:|
| 2.01–2.35 | 0.125 | 1250 |
| 2.35–2.53 | 0.143 | 1250 |
| 2.53–2.75 | 0.176 | 1250 |
| 2.75–3.57 | 0.211 | 1250 |

## z3 — n_s

Canonical `log(omega_b)/(n_s + omega_cdm)`; support {omega_b, omega_cdm, n_s}, complement {H0, tau, ln10As}; 5000 pairs, mean nuisance distance 2.29.

E_inv vs nuisance distance:
| d range | E_inv | n |
|---|---:|---:|
| 1.71–2.07 | 0.076 | 1250 |
| 2.07–2.26 | 0.081 | 1250 |
| 2.26–2.48 | 0.090 | 1250 |
| 2.48–3.24 | 0.096 | 1250 |

## z4 — tau (amplitude sector)

Canonical `-A_s/(tau - 0.4454238)`; support {tau, ln10As}, complement {omega_b, omega_cdm, H0, n_s}; 5000 pairs, mean nuisance distance 2.58.

E_inv vs nuisance distance:
| d range | E_inv | n |
|---|---:|---:|
| 1.98–2.36 | 0.047 | 1250 |
| 2.36–2.54 | 0.048 | 1250 |
| 2.54–2.76 | 0.052 | 1250 |
| 2.76–3.51 | 0.058 | 1250 |

## z5 — amplitude (A_s, tau)

Canonical `A_s*exp(-2*tau)`; support {tau, ln10As}, complement {omega_b, omega_cdm, H0, n_s}; 5000 pairs, mean nuisance distance 2.58.

E_inv vs nuisance distance:
| d range | E_inv | n |
|---|---:|---:|
| 2.03–2.36 | 0.170 | 1250 |
| 2.36–2.54 | 0.197 | 1250 |
| 2.54–2.76 | 0.234 | 1250 |
| 2.76–3.69 | 0.304 | 1250 |

## Controls (amplitude latent)

Shuffled-target forms (expect E_inv ~ 1 — physically meaningless level sets):

| shuffle seed | E_inv | R2 resp |
|---:|---:|---:|
| 0 | 1.69 | 0.22 |
| 1 | 1.59 | 0.35 |
| 2 | 1.81 | 0.10 |

Wrong-latent specificity (amplitude f vs shape latents — expect NOT invariant):

| latent | E_inv | R2 resp |
|---:|---:|---:|
| z0 | 2.37 | 0.01 |
| z1 | 2.44 | 0.02 |
| z2 | 2.50 | -0.00 |
| z3 | 2.53 | -0.00 |
| z4 | 1.02 | 0.00 |

# Gate G4a

| bullet | numbers | pass |
|---|---|---|
| E_inv <= 0.05 | 0.226 | FAIL |
| matched response R2 >= 0.9 | 0.913 | PASS |
| T2 confirmation | E_inv 0.241, R2 0.915 | FAIL |
| controls sane | shuffled ~1, wrong-latent > 0.05 | PASS |

**Gate G4a: FAIL** (decoder-side bullet lands with Phase 7b)

---
_Generated by `scripts/levelset_audit.py`._
