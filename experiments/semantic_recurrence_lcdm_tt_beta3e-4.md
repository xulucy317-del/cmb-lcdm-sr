# Semantic recurrence — `lcdm_tt_beta3e-4` (roadmap Phase 2)

Front equations with eta_plat >= 0.25 (vs the Phase-1 ms30-firmed plateau) pooled by the three frozen equivalence tests (canonical sympy identity; |Spearman| >= 0.98 on the 2048-theta anchors; gradient-cosine distance <= 0.05 in u-coordinates) and union-find clustered. R_SR per family = fraction of that family's seeds whose front carries a cluster member at knee level (c <= c*_F, MI >= M_F(c*_F) - SD_F; seed-level tolerance = one cross-seed SD — documented deviation from the SE-of-mean wording of section 0.3, which would cap R_SR at ~0.7 by seed-scatter alone). Where semantic pooling beats exact-string pooling, the best single-string recurrence is shown in parentheses — the `pool_sr_runs` comparison. Supports are in the sampled basis (`ln10As` = ln 10^10 A_s).


## z0 — omega_b

Family knees: `allparams` c*=19, knee MI 3.291 (plat 3.337+/-0.024, n=5); `allparams_ms10` c*=10, knee MI 2.074 (plat 2.083+/-0.008, n=5); `allparams_ms30` c*=26, knee MI 3.458 (plat 3.570+/-0.059, n=3).

237 front rows above the floor, 157 unique simplified forms, 0 unparseable, 1 semantic clusters.

**Canonical coordinate** (cluster 0, R_SR 1.00): `n_s/omega_b` (c=3, support {omega_b, n_s})

| cluster | representative (c) | support(rep) | R_SR ms10 | R_SR ms20 | R_SR ms30 | best MI +/- err (family/seed) | C range | forms | cohesion rep/pair | textbook |
|---:|---|---|---|---|---|---|---|---:|---|---|
| 0 | `n_s/omega_b` (3) | omega_b, n_s | 5/5 (exact 1/5) | 4/5 (exact 1/5) | 3/3 (exact 1/3) | 3.648 +/- 0.030 (`allparams_ms30`/s0) | 1-30 | 157 | 0.71/0.96 |  |

## z1 — omega_cdm

Family knees: `allparams` c*=20, knee MI 2.329 (plat 2.334+/-0.005, n=5); `allparams_ms10` c*=10, knee MI 1.145 (plat 1.170+/-0.025, n=5); `allparams_ms30` c*=29, knee MI 2.502 (plat 2.515+/-0.013, n=3).

180 front rows above the floor, 103 unique simplified forms, 0 unparseable, 1 semantic clusters.

**Canonical coordinate** (cluster 0, R_SR 0.80): `H0**2*n_s**2*omega_b/(A_s*omega_cdm**2)` (c=10, support {omega_b, omega_cdm, H0, ln10As, n_s})

| cluster | representative (c) | support(rep) | R_SR ms10 | R_SR ms20 | R_SR ms30 | best MI +/- err (family/seed) | C range | forms | cohesion rep/pair | textbook |
|---:|---|---|---|---|---|---|---|---:|---|---|
| 0 | `H0**2*n_s**2*omega_b/(A_s*omega_cdm**2)` (10) | omega_b, omega_cdm, H0, ln10As, n_s | 3/5 | 4/5 (exact 1/5) | 2/3 (exact 1/3) | 2.529 +/- 0.042 (`allparams_ms30`/s0) | 5-30 | 103 | 0.61/0.67 |  |

## z2 — amplitude (A_s, tau)

Family knees: `allparams` c*=19, knee MI 3.740 (plat 3.843+/-0.055, n=5); `allparams_ms10` c*=9, knee MI 1.350 (plat 1.419+/-0.069, n=5); `allparams_ms30` c*=24, knee MI 4.115 (plat 4.175+/-0.043, n=3); `hpsweep_hp_v1/c00_baseline` c*=19, knee MI 3.665 (plat 3.746+/-0.050, n=3); `hpsweep_hp_v1/c01_ni100` c*=20, knee MI 3.740 (plat 3.767+/-0.027, n=3); `hpsweep_hp_v1/c02_ni400` c*=19, knee MI 3.826 (plat 3.870+/-0.036, n=3); `hpsweep_hp_v1/c03_pop8` c*=17, knee MI 2.955 (plat 3.518+/-0.289, n=3); `hpsweep_hp_v1/c04_pop31` c*=19, knee MI 3.612 (plat 3.868+/-0.129, n=3); `hpsweep_hp_v1/c05_ms10` c*=10, knee MI 1.513 (plat 1.601+/-0.088, n=3); `hpsweep_hp_v1/c06_ms15` c*=15, knee MI 2.834 (plat 3.231+/-0.397, n=3); `hpsweep_hp_v1/c07_ms30` c*=22, knee MI 3.972 (plat 4.053+/-0.046, n=3); `hpsweep_hp_v1/c08_ps54` c*=19, knee MI 3.836 (plat 3.903+/-0.050, n=3); `hpsweep_hp_v1/c09_ps108` c*=20, knee MI 3.677 (plat 3.786+/-0.108, n=3); `hpsweep_hp_v1/c10_ncyc190` c*=20, knee MI 3.753 (plat 3.839+/-0.086, n=3); `hpsweep_hp_v1/c11_ncyc760` c*=19, knee MI 3.711 (plat 3.816+/-0.093, n=3).

564 front rows above the floor, 446 unique simplified forms, 0 unparseable, 1 semantic clusters.

**Canonical coordinate** (cluster 0, R_SR 1.00): `A_s/log(H0*(omega_cdm + tau))` (c=8, support {omega_cdm, H0, tau, ln10As})

| cluster | representative (c) | support(rep) | R_SR ms10 | R_SR ms20 | R_SR ms30 | best MI +/- err (family/seed) | C range | forms | cohesion rep/pair | textbook |
|---:|---|---|---|---|---|---|---|---:|---|---|
| 0 | `A_s/log(H0*(omega_cdm + tau))` (8) | omega_cdm, H0, tau, ln10As | 4/5 (exact 2/5) | 3/5 (exact 1/5) | 3/3 (exact 1/3) | 4.226 +/- 0.029 (`allparams_ms30`/s0) | 8-30 | 446 | 1.00/0.99 | yes |

## z3 — n_s

Family knees: `allparams` c*=20, knee MI 3.054 (plat 3.064+/-0.010, n=5); `allparams_ms10` c*=10, knee MI 2.176 (plat 2.184+/-0.008, n=5); `allparams_ms30` c*=27, knee MI 3.096 (plat 3.147+/-0.030, n=3).

203 front rows above the floor, 141 unique simplified forms, 0 unparseable, 1 semantic clusters.

**Canonical coordinate** (cluster 0, R_SR 1.00): `n_s + omega_cdm` (c=3, support {omega_cdm, n_s})

| cluster | representative (c) | support(rep) | R_SR ms10 | R_SR ms20 | R_SR ms30 | best MI +/- err (family/seed) | C range | forms | cohesion rep/pair | textbook |
|---:|---|---|---|---|---|---|---|---:|---|---|
| 0 | `n_s + omega_cdm` (3) | omega_cdm, n_s | 4/5 (exact 2/5) | 5/5 (exact 1/5) | 3/3 (exact 1/3) | 3.193 +/- 0.033 (`allparams_ms30`/s2) | 3-30 | 141 | 0.96/1.00 |  |

## z4 — H0

Family knees: `allparams` c*=20, knee MI 3.568 (plat 3.620+/-0.053, n=5); `allparams_ms10` c*=10, knee MI 1.264 (plat 1.276+/-0.012, n=5); `allparams_ms30` c*=24, knee MI 4.120 (plat 4.313+/-0.120, n=3).

131 front rows above the floor, 101 unique simplified forms, 0 unparseable, 1 semantic clusters.

**Canonical coordinate** (cluster 0, R_SR 0.80): `A_s*H0**2*omega_cdm*exp(-2*tau)` (c=9, support {omega_cdm, H0, tau, ln10As})

| cluster | representative (c) | support(rep) | R_SR ms10 | R_SR ms20 | R_SR ms30 | best MI +/- err (family/seed) | C range | forms | cohesion rep/pair | textbook |
|---:|---|---|---|---|---|---|---|---:|---|---|
| 0 | `A_s*H0**2*omega_cdm*exp(-2*tau)` (9) | omega_cdm, H0, tau, ln10As | 4/5 (exact 2/5) | 4/5 (exact 1/5) | 2/3 (exact 1/3) | 4.552 +/- 0.030 (`allparams_ms30`/s2) | 8-29 | 101 | 0.97/0.96 | yes |

---
_Generated by `scripts/semantic_recurrence.py` from the same fronts as the Phase-1 readout; hpsweep families contribute members and JSON R_SR entries but no headline._
