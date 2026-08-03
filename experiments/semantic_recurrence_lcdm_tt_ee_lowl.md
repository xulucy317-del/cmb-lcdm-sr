# Semantic recurrence — `lcdm_tt_ee_lowl` (roadmap Phase 2)

Front equations with eta_plat >= 0.25 (vs the Phase-1 ms30-firmed plateau) pooled by the three frozen equivalence tests (canonical sympy identity; |Spearman| >= 0.98 on the 2048-theta anchors; gradient-cosine distance <= 0.05 in u-coordinates) and union-find clustered. R_SR per family = fraction of that family's seeds whose front carries a cluster member at knee level (c <= c*_F, MI >= M_F(c*_F) - SD_F; seed-level tolerance = one cross-seed SD — documented deviation from the SE-of-mean wording of section 0.3, which would cap R_SR at ~0.7 by seed-scatter alone). Where semantic pooling beats exact-string pooling, the best single-string recurrence is shown in parentheses — the `pool_sr_runs` comparison. Supports are in the sampled basis (`ln10As` = ln 10^10 A_s).


## z0 — omega_cdm

Family knees: `allparams` c*=18, knee MI 1.758 (plat 1.769+/-0.007, n=5); `allparams_ms10` c*=10, knee MI 1.415 (plat 1.423+/-0.008, n=5); `allparams_ms30` c*=19, knee MI 1.773 (plat 1.788+/-0.008, n=3).

172 front rows above the floor, 120 unique simplified forms, 0 unparseable, 2 semantic clusters.

**Canonical coordinate** (cluster 0, R_SR 1.00): `omega_cdm/(H0*n_s*omega_b)` (c=7, support {omega_b, omega_cdm, H0, n_s})

| cluster | representative (c) | support(rep) | R_SR ms10 | R_SR ms20 | R_SR ms30 | best MI +/- err (family/seed) | C range | forms | cohesion rep/pair | textbook |
|---:|---|---|---|---|---|---|---|---:|---|---|
| 0 | `omega_cdm/(H0*n_s*omega_b)` (7) | omega_b, omega_cdm, H0, n_s | 5/5 (exact 1/5) | 4/5 (exact 1/5) | 2/3 (exact 1/3) | 1.803 +/- 0.036 (`allparams_ms30`/s2) | 5-30 | 119 | 0.99/0.97 | yes |
| 1 | `omega_cdm/H0` (3) | omega_cdm, H0 | 0/5 | 0/5 | 0/3 | 0.615 +/- 0.020 (`allparams`/s0) | 3-3 | 1 | 1.00/1.00 |  |

## z1 — H0

Family knees: `allparams` c*=18, knee MI 3.229 (plat 3.572+/-0.176, n=5); `allparams_ms10` c*=9, knee MI 1.719 (plat 1.780+/-0.041, n=5); `allparams_ms30` c*=25, knee MI 3.953 (plat 4.006+/-0.045, n=3).

208 front rows above the floor, 133 unique simplified forms, 0 unparseable, 1 semantic clusters.

**Canonical coordinate** (cluster 0, R_SR 1.00): `H0**2*omega_cdm` (c=4, support {omega_cdm, H0})

| cluster | representative (c) | support(rep) | R_SR ms10 | R_SR ms20 | R_SR ms30 | best MI +/- err (family/seed) | C range | forms | cohesion rep/pair | textbook |
|---:|---|---|---|---|---|---|---|---:|---|---|
| 0 | `H0**2*omega_cdm` (4) | omega_cdm, H0 | 5/5 (exact 3/5) | 4/5 (exact 1/5) | 2/3 (exact 1/3) | 4.064 +/- 0.032 (`allparams_ms30`/s1) | 3-30 | 133 | 0.99/0.98 | yes |

## z2 — omega_b

Family knees: `allparams` c*=20, knee MI 3.259 (plat 3.282+/-0.022, n=5); `allparams_ms10` c*=10, knee MI 2.353 (plat 2.474+/-0.121, n=5); `allparams_ms30` c*=22, knee MI 3.293 (plat 3.330+/-0.020, n=3).

199 front rows above the floor, 145 unique simplified forms, 0 unparseable, 1 semantic clusters.

**Canonical coordinate** (cluster 0, R_SR 1.00): `omega_b/n_s**2` (c=4, support {omega_b, n_s})

| cluster | representative (c) | support(rep) | R_SR ms10 | R_SR ms20 | R_SR ms30 | best MI +/- err (family/seed) | C range | forms | cohesion rep/pair | textbook |
|---:|---|---|---|---|---|---|---|---:|---|---|
| 0 | `omega_b/n_s**2` (4) | omega_b, n_s | 5/5 (exact 3/5) | 4/5 (exact 1/5) | 3/3 (exact 1/3) | 3.369 +/- 0.033 (`allparams_ms30`/s0) | 3-30 | 145 | 0.99/0.99 |  |

## z3 — n_s

Family knees: `allparams` c*=17, knee MI 3.073 (plat 3.117+/-0.024, n=5); `allparams_ms10` c*=10, knee MI 1.996 (plat 2.012+/-0.015, n=5); `allparams_ms30` c*=18, knee MI 3.115 (plat 3.212+/-0.071, n=3).

169 front rows above the floor, 145 unique simplified forms, 0 unparseable, 1 semantic clusters.

**Canonical coordinate** (cluster 0, R_SR 0.80): `log(omega_b)/(n_s + omega_cdm)` (c=6, support {omega_b, omega_cdm, n_s})

| cluster | representative (c) | support(rep) | R_SR ms10 | R_SR ms20 | R_SR ms30 | best MI +/- err (family/seed) | C range | forms | cohesion rep/pair | textbook |
|---:|---|---|---|---|---|---|---|---:|---|---|
| 0 | `log(omega_b)/(n_s + omega_cdm)` (6) | omega_b, omega_cdm, n_s | 4/5 (exact 2/5) | 4/5 (exact 1/5) | 2/3 (exact 1/3) | 3.314 +/- 0.038 (`allparams_ms30`/s0) | 6-30 | 145 | 0.98/0.98 |  |

## z4 — tau (amplitude sector)

Family knees: `allparams` c*=17, knee MI 2.105 (plat 2.166+/-0.043, n=5); `allparams_ms10` c*=9, knee MI 1.845 (plat 1.854+/-0.009, n=5); `allparams_ms30` c*=20, knee MI 2.216 (plat 2.370+/-0.082, n=3).

185 front rows above the floor, 160 unique simplified forms, 0 unparseable, 1 semantic clusters.

**Canonical coordinate** (cluster 0, R_SR 1.00): `-A_s/(tau - 0.4454238)` (c=5, support {tau, ln10As})

| cluster | representative (c) | support(rep) | R_SR ms10 | R_SR ms20 | R_SR ms30 | best MI +/- err (family/seed) | C range | forms | cohesion rep/pair | textbook |
|---:|---|---|---|---|---|---|---|---:|---|---|
| 0 | `-A_s/(tau - 0.4454238)` (5) | tau, ln10As | 4/5 (exact 1/5) | 4/5 (exact 1/5) | 3/3 (exact 1/3) | 2.471 +/- 0.033 (`allparams_ms30`/s2) | 3-30 | 160 | 0.79/0.81 |  |

## z5 — amplitude (A_s, tau)

Family knees: `allparams` c*=20, knee MI 3.742 (plat 3.830+/-0.087, n=5); `allparams_ms10` c*=10, knee MI 1.690 (plat 1.751+/-0.061, n=5); `allparams_ms30` c*=28, knee MI 4.081 (plat 4.087+/-0.004, n=3); `hpsweep_hp_v1/c00_baseline` c*=19, knee MI 3.421 (plat 3.618+/-0.195, n=3); `hpsweep_hp_v1/c01_ni100` c*=18, knee MI 3.106 (plat 3.442+/-0.265, n=3); `hpsweep_hp_v1/c02_ni400` c*=19, knee MI 3.663 (plat 3.825+/-0.116, n=3); `hpsweep_hp_v1/c03_pop8` c*=19, knee MI 3.166 (plat 3.435+/-0.152, n=3); `hpsweep_hp_v1/c04_pop31` c*=19, knee MI 3.779 (plat 3.878+/-0.098, n=3); `hpsweep_hp_v1/c05_ms10` c*=10, knee MI 1.674 (plat 1.686+/-0.012, n=3); `hpsweep_hp_v1/c06_ms15` c*=14, knee MI 2.763 (plat 2.823+/-0.035, n=3); `hpsweep_hp_v1/c07_ms30` c*=22, knee MI 3.861 (plat 4.049+/-0.096, n=3); `hpsweep_hp_v1/c08_ps54` c*=18, knee MI 3.654 (plat 3.857+/-0.159, n=3); `hpsweep_hp_v1/c09_ps108` c*=19, knee MI 3.753 (plat 3.890+/-0.101, n=3); `hpsweep_hp_v1/c10_ncyc190` c*=18, knee MI 3.547 (plat 3.821+/-0.159, n=3); `hpsweep_hp_v1/c11_ncyc760` c*=18, knee MI 3.179 (plat 3.597+/-0.255, n=3).

735 front rows above the floor, 461 unique simplified forms, 0 unparseable, 1 semantic clusters.

**Canonical coordinate** (cluster 0, R_SR 1.00): `A_s*exp(-2*tau)` (c=5, support {tau, ln10As})

| cluster | representative (c) | support(rep) | R_SR ms10 | R_SR ms20 | R_SR ms30 | best MI +/- err (family/seed) | C range | forms | cohesion rep/pair | textbook |
|---:|---|---|---|---|---|---|---|---:|---|---|
| 0 | `A_s*exp(-2*tau)` (5) | tau, ln10As | 5/5 (exact 1/5) | 4/5 (exact 1/5) | 3/3 (exact 1/3) | 4.197 +/- 0.039 (`hpsweep_hp_v1/c07_ms30`/s1) | 5-30 | 461 | 0.98/1.00 | yes |

---
_Generated by `scripts/semantic_recurrence.py` from the same fronts as the Phase-1 readout; hpsweep families contribute members and JSON R_SR entries but no headline._
