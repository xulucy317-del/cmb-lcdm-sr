# Latent cards — `lcdm_tt_ee_lowl` (roadmap Phase 10)

One §0.1 card per latent, statuses from the frozen §0.3 predicates (deviation register at the end; D-LS defines the level-set leg). All numbers are merged verbatim from the Phase 1-8 and post-closure deliverables named on each line — no new computation.

| latent | role | status | f1 | eta_S | eta_post_hat | eta_ph_comb | R_SR | E_inv joint | axis-aligned |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| z0 | omega_cdm | **unresolved** | `omega_cdm/(H0*n_s*omega_b)` | 1.000 | 0.756 | 0.842 | 1.00 | 0.060 | False |
| z1 | H0 | **primarily interpreted** | `H0**2*omega_cdm` | 1.000 | 0.348 | 0.663 | 1.00 | 0.023 | False |
| z2 | omega_b | **primarily interpreted** | `omega_b/n_s**2` | 0.995 | 0.574 | 0.963 | 1.00 | 0.014 | False |
| z3 | n_s | **primarily interpreted** | `log(omega_b)/(n_s + omega_cdm)` | 0.992 | 0.493 | 0.864 | 0.80 | 0.014 | False |
| z4 | tau (amplitude sector) | **primarily interpreted** | `-A_s/(tau - 0.4454238)` | 1.068 | 0.842 | 0.842 | 1.00 | 0.031 | False |
| z5 | amplitude (A_s, tau) | **primarily interpreted** | `A_s*exp(-2*tau)` | 1.000 | 0.289 | 0.590 | 1.00 | 0.029 | False |

## z0 — omega_cdm (omega_cdm envelope / early-ISW)

**Status: unresolved** — failed: level-set evidence

* f1 `omega_cdm/(H0*n_s*omega_b)` (C=7, support {omega_b, omega_cdm, H0, n_s}, R_SR 1.00, cohesion 0.97) [semantic_recurrence]
* knee c* = 19, plateau 1.788 +/- 0.008 nat (allparams_ms30), MI@c<=10 1.457, envelope: no knee (diffuse) [knee_readout]
* S* = {omega_b, omega_cdm, H0, tau, A_s, n_s} (|S|=6, eta_S 1.000 +/- 0.000, screen-recurrent True) [subset_selection]
* R-P4 exhaustive full-protocol (M@c<=10 1.457 vs all-6 1.457): S+ = {omega_b, omega_cdm, H0, A_s, n_s}, paired T2 vs all-6 +0.0015 +/- 0.0013 nat -> dilution-affected [subsets_full]
* ceiling I(Z;theta) = 1.343 +/- 0.003 nat (SNR 11.5); eta_post 0.737 +/- 0.009, eta_post_hat 0.756 +/- 0.012; combined (f1+f2): eta_post_hat 0.842, eta_plat 0.925 [posterior_ceiling, residual_sr]
* signature g_j: ob=0.23 oc=0.33 H0=0.32 ns=0.12; decoder cos_g 0.99 [sufficiency_audit, decoder_effect]
* stage-1 residual: R2_cal 0.924, R2_res 0.960 -> FAIL (loadings {omega_b, omega_cdm, H0, tau, ln10As, n_s}) [sufficiency_audit]
* f2 `A_s*H0*omega_cdm/n_s` (support {omega_cdm, H0, ln10As, n_s}, shape-sector False, R_SR 0.80, MI vs e1 0.401); combined R2(mu) 0.955; stage-2 residual FAIL [residual_sr]
* level sets: f1-only E_inv 0.138 (band 0.076-0.153, resp R2 0.92) -> FAIL; joint (f1,f2) E_inv 0.060 (band 0.045-0.091, resp 0.95) -> FAIL [levelset_audit, levelset_audit_joint]
* decoder effect: a = [ob=+0.21 oc=-0.33 H0=+0.25 tau=+0.03 lnAs=-0.06 ns=+0.12], R2_W 0.997, amp mass 0.09, frac_brk 0.46 [decoder_effect]
* subspace probe: A* = {z0, z1, z2, z4, z5} (axis-aligned False), R2 own 0.920 / full 0.955 (T2 0.954); top pair (z0, z1), redundancy(2|1) n/a [subspace_probe]

## z1 — H0 (H0 acoustic phase shift)

**Status: primarily interpreted** — eta_S + R_SR + level-set evidence green; stage-1 residual structured (f2 documented)

* f1 `H0**2*omega_cdm` (C=4, support {omega_cdm, H0}, R_SR 1.00, cohesion 0.98) [semantic_recurrence]
* knee c* = 25, plateau 4.006 +/- 0.045 nat (allparams_ms30), MI@c<=10 1.952, envelope: no knee (diffuse) [knee_readout]
* S* = {omega_b, omega_cdm, H0, tau, A_s, n_s} (|S|=6, eta_S 1.000 +/- 0.000, screen-recurrent True) [subset_selection]
* R-P4 exhaustive full-protocol (M@c<=10 1.957 vs all-6 1.952): S+ = {omega_b, omega_cdm, H0, tau, A_s}, paired T2 vs all-6 -0.0113 +/- 0.0225 nat -> not confirmed (all-6 stands) [subsets_full]
* ceiling I(Z;theta) = 3.835 +/- 0.003 nat (SNR 2179.5); eta_post 0.352 +/- 0.003, eta_post_hat 0.348 +/- 0.004; combined (f1+f2): eta_post_hat 0.663, eta_plat 0.652 [posterior_ceiling, residual_sr]
* signature g_j: oc=0.34 H0=0.66; decoder cos_g 0.93 [sufficiency_audit, decoder_effect]
* stage-1 residual: R2_cal 0.931, R2_res 0.993 -> FAIL (loadings {omega_b, omega_cdm, H0, tau, ln10As, n_s}) [sufficiency_audit]
* f2 `A_s*exp(-2*tau)/omega_b**2` (support {omega_b, tau, ln10As}, shape-sector False, R_SR 0.80, MI vs e1 1.281); combined R2(mu) 0.995; stage-2 residual FAIL [residual_sr]
* level sets: f1-only E_inv 0.169 (band 0.069-0.137, resp R2 0.93) -> FAIL; joint (f1,f2) E_inv 0.023 (band 0.005-0.011, resp 0.99) -> PASS [levelset_audit, levelset_audit_joint]
* decoder effect: a = [ob=+0.08 oc=-0.16 H0=-0.52 tau=+0.17 lnAs=-0.02 ns=+0.01], R2_W 0.989, amp mass 0.20, frac_brk 0.80 [decoder_effect]
* subspace probe: A* = {z0, z1, z2, z3, z5} (axis-aligned False), R2 own 0.924 / full 0.991 (T2 0.991); top pair (z1, z5), redundancy(2|1) -3.99 [subspace_probe]
* deviations: **D-LS** level-set leg via joint (f1,f2) audit

## z2 — omega_b (omega_b odd-even contrast)

**Status: primarily interpreted** — eta_S + R_SR + level-set evidence green; stage-1 residual structured (f2 documented)

* f1 `omega_b/n_s**2` (C=4, support {omega_b, n_s}, R_SR 1.00, cohesion 0.99) [semantic_recurrence]
* knee c* = 22, plateau 3.330 +/- 0.020 nat (allparams_ms30), MI@c<=10 3.057, envelope: knee + slow climb [knee_readout]
* S* = {omega_b, omega_cdm, A_s, n_s} (|S|=4, eta_S 0.995 +/- 0.008, screen-recurrent True) [subset_selection]
* R-P4 exhaustive full-protocol (M@c<=10 3.005 vs all-6 2.885): S+ = {omega_b, omega_cdm, A_s, n_s}, paired T2 vs all-6 +0.1148 +/- 0.1039 nat -> dilution-affected [subsets_full]
* ceiling I(Z;theta) = 2.180 +/- 0.003 nat (SNR 78.6); eta_post 0.576 +/- 0.006, eta_post_hat 0.574 +/- 0.006; combined (f1+f2): eta_post_hat 0.963, eta_plat 0.933 [posterior_ceiling, residual_sr]
* signature g_j: ob=0.49 ns=0.51; decoder cos_g 0.97 [sufficiency_audit, decoder_effect]
* stage-1 residual: R2_cal 0.927, R2_res 0.993 -> FAIL (loadings {omega_b, omega_cdm, H0, ln10As, n_s}) [sufficiency_audit]
* f2 `n_s*(A_s + 1.03524857872784e-5*omega_b*omega_cdm**2)` (support {omega_b, omega_cdm, ln10As, n_s}, shape-sector False, R_SR 0.80, MI vs e1 1.765); combined R2(mu) 0.998; stage-2 residual FAIL [residual_sr]
* level sets: f1-only E_inv 0.164 (band 0.073-0.145, resp R2 0.93) -> FAIL; joint (f1,f2) E_inv 0.014 (band 0.002-0.005, resp 1.00) -> PASS [levelset_audit, levelset_audit_joint]
* decoder effect: a = [ob=+0.42 oc=+0.13 H0=-0.01 lnAs=+0.04 ns=-0.35], R2_W 1.000, amp mass 0.05, frac_brk 0.36 [decoder_effect]
* subspace probe: A* = {z0, z1, z2, z3, z4, z5} (axis-aligned False), R2 own 0.922 / full 0.990 (T2 0.990); top pair (z2, z3), redundancy(2|1) -15.40 [subspace_probe]
* deviations: **D-LS** level-set leg via joint (f1,f2) audit

## z3 — n_s (tilt)

**Status: primarily interpreted** — eta_S + R_SR + level-set evidence green; stage-1 residual structured (f2 documented)

* f1 `log(omega_b)/(n_s + omega_cdm)` (C=6, support {omega_b, omega_cdm, n_s}, R_SR 0.80, cohesion 0.98) [semantic_recurrence]
* knee c* = 18, plateau 3.212 +/- 0.071 nat (allparams_ms30), MI@c<=10 2.048, envelope: no knee (diffuse) [knee_readout]
* S* = {omega_b, omega_cdm, H0, n_s} (|S|=4, eta_S 0.992 +/- 0.010, screen-recurrent False) [subset_selection]
* R-P4 exhaustive full-protocol (M@c<=10 2.123 vs all-6 2.048): S+ = {omega_b, omega_cdm, H0, tau, n_s}, paired T2 vs all-6 +0.0854 +/- 0.0403 nat -> dilution-affected [subsets_full]
* ceiling I(Z;theta) = 2.724 +/- 0.003 nat (SNR 234.1); eta_post 0.493 +/- 0.005, eta_post_hat 0.493 +/- 0.005; combined (f1+f2): eta_post_hat 0.864, eta_plat 0.819 [posterior_ceiling, residual_sr]
* signature g_j: ob=0.30 oc=0.17 ns=0.52; decoder cos_g 0.97; ratio pairs: (omega_b,omega_cdm) r=+12.909; (omega_b,n_s) r=+12.909; (omega_cdm,n_s) r=+1.000 [sufficiency_audit, decoder_effect]
* stage-1 residual: R2_cal 0.935, R2_res 0.991 -> FAIL (loadings {omega_b, omega_cdm, H0, ln10As, n_s}) [sufficiency_audit]
* f2 `H0/omega_cdm**2` (support {omega_cdm, H0}, shape-sector True, R_SR 0.80, MI vs e1 1.065); combined R2(mu) 0.992; stage-2 residual FAIL [residual_sr]
* level sets: f1-only E_inv 0.086 (band 0.065-0.129, resp R2 0.94) -> FAIL; joint (f1,f2) E_inv 0.014 (band 0.008-0.016, resp 0.99) -> PASS [levelset_audit, levelset_audit_joint]
* decoder effect: a = [ob=+0.27 oc=+0.26 H0=-0.07 lnAs=-0.01 ns=+0.43], R2_W 1.000, amp mass 0.01, frac_brk 0.26 [decoder_effect]
* subspace probe: A* = {z0, z2, z3, z4, z5} (axis-aligned False), R2 own 0.933 / full 0.990 (T2 0.989); top pair (z3, z2), redundancy(2|1) n/a [subspace_probe]
* deviations: **D-LS** level-set leg via joint (f1,f2) audit; **N-G2** S* not recurrent across the two screen seeds (ATTENTION (not screen-recurrent)) — R-P4 disposition (2026-08-14): dilution-affected; budget-matched S+ = {omega_b, omega_cdm, H0, tau, n_s} (paired T2 +0.0854 +/- 0.0403 nat); no status change

## z4 — tau (amplitude sector) (reionization bump)

**Status: primarily interpreted** — eta_S + R_SR + level-set evidence green; stage-1 residual structured (f2 documented)

* f1 `-A_s/(tau - 0.4454238)` (C=5, support {tau, ln10As}, R_SR 1.00, cohesion 0.81) [semantic_recurrence]
* knee c* = 20, plateau 2.370 +/- 0.082 nat (allparams_ms30), MI@c<=10 1.905, envelope: no knee (diffuse) [knee_readout]
* S* = {omega_b, tau, A_s} (|S|=3, eta_S 1.068 +/- 0.026, screen-recurrent False) [subset_selection]
* R-P4 exhaustive full-protocol (M@c<=10 1.985 vs all-6 1.854): S+ = {omega_cdm, tau, A_s, n_s}, paired T2 vs all-6 +0.1259 +/- 0.0467 nat -> dilution-affected [subsets_full]
* ceiling I(Z;theta) = 1.535 +/- 0.003 nat (SNR 17.7); eta_post 0.811 +/- 0.006, eta_post_hat 0.842 +/- 0.011; combined (f1+f2): eta_post_hat 0.842, eta_plat 0.761 [posterior_ceiling, residual_sr]
* signature g_j: tau=0.54 lnAs=0.46; decoder cos_g 1.00 [sufficiency_audit, decoder_effect]
* stage-1 residual: R2_cal 0.955, R2_res 0.980 -> FAIL (loadings {omega_b, omega_cdm, H0, tau, ln10As, n_s}) [sufficiency_audit]
* f2 `tau` (support {tau}, shape-sector False, R_SR 0.80, MI vs e1 0.702); combined R2(mu) 0.957; stage-2 residual FAIL [residual_sr]
* level sets: f1-only E_inv 0.051 (band 0.045-0.089, resp R2 0.96) -> FAIL; joint (f1,f2) E_inv 0.031 (band 0.043-0.086, resp 0.96) -> PASS [levelset_audit, levelset_audit_joint]
* decoder effect: a = [oc=+0.03 H0=-0.02 tau=-0.40 lnAs=-0.33 ns=-0.03], R2_W 0.988, amp mass 0.90, frac_brk 0.01 [decoder_effect]
* subspace probe: A* = {z2, z4} (axis-aligned False), R2 own 0.946 / full 0.950 (T2 0.950); top pair (z4, z0), redundancy(2|1) -5.08 [subspace_probe]
* deviations: **D-LS** level-set leg via joint (f1,f2) audit; **N-G2** S* not recurrent across the two screen seeds (ATTENTION (not screen-recurrent)) — R-P4 disposition (2026-08-14): dilution-affected; budget-matched S+ = {omega_cdm, tau, A_s, n_s} (paired T2 +0.1259 +/- 0.0467 nat); no status change

## z5 — amplitude (A_s, tau) (overall amplitude)

**Status: primarily interpreted** — eta_S + R_SR + level-set evidence green; stage-1 residual structured (f2 documented)

* f1 `A_s*exp(-2*tau)` (C=5, support {tau, ln10As}, R_SR 1.00, cohesion 1.00) [semantic_recurrence]
* knee c* = 28, plateau 4.087 +/- 0.004 nat (allparams_ms30), MI@c<=10 2.019, envelope: no knee (diffuse) [knee_readout]
* S* = {omega_b, omega_cdm, H0, tau, A_s, n_s} (|S|=6, eta_S 1.000 +/- 0.000, screen-recurrent True) [subset_selection]
* R-P4 exhaustive full-protocol (M@c<=10 2.019 vs all-6 2.017): S+ = {omega_cdm, H0, tau, A_s, n_s}, paired T2 vs all-6 +0.0032 +/- 0.0032 nat -> dilution-affected [subsets_full]
* ceiling I(Z;theta) = 4.176 +/- 0.003 nat (SNR 4278.3); eta_post 0.290 +/- 0.003, eta_post_hat 0.289 +/- 0.003; combined (f1+f2): eta_post_hat 0.590, eta_plat 0.609 [posterior_ceiling, residual_sr]
* signature g_j: tau=0.46 lnAs=0.54; decoder cos_g 0.98; ratio pairs: (tau,ln10As) r=-2.000 [sufficiency_audit, decoder_effect]
* stage-1 residual: R2_cal 0.910, R2_res 0.994 -> FAIL (loadings {omega_b, omega_cdm, H0, n_s}) [sufficiency_audit]
* f2 `H0*omega_cdm/n_s` (support {omega_cdm, H0, n_s}, shape-sector True, R_SR 0.80, MI vs e1 1.250); combined R2(mu) 0.993; stage-2 residual FAIL [residual_sr]
* level sets: f1-only E_inv 0.226 (band 0.090-0.180, resp R2 0.91) -> FAIL; joint (f1,f2) E_inv 0.029 (band 0.007-0.015, resp 0.99) -> PASS [levelset_audit, levelset_audit_joint]
* decoder effect: a = [ob=+0.02 oc=-0.09 H0=-0.05 tau=-0.36 lnAs=+0.44 ns=+0.05], R2_W 1.000, amp mass 0.79, r_dec -1.87, frac_brk 0.50 [decoder_effect]
* subspace probe: A* = {z0, z1, z2, z4, z5} (axis-aligned False), R2 own 0.905 / full 0.994 (T2 0.993); top pair (z5, z1), redundancy(2|1) -34.63 [subspace_probe]
* deviations: **D-LS** level-set leg via joint (f1,f2) audit

# Gates

| gate | verdict | source |
|---|---|---|
| G1 (amplitude positive control) | PASS | sufficiency_audit_lcdm_tt_ee_lowl.md (amplitude positive control; both models 2026-08-03) |
| G2 (S* selection) | see per-latent verdicts | subset_selection_lcdm_tt_ee_lowl.md |
| G3 (posterior ceiling, DPI) | PASS | posterior_ceiling_lcdm_tt_ee_lowl.md |
| G4a (level sets, f1-only) | FAIL | levelset_audit_lcdm_tt_ee_lowl.md |
| G4a-joint (level sets, f1+f2) | PASS | levelset_audit_joint_lcdm_tt_ee_lowl.md |
| G4b (decoder triangulation) | FAIL | decoder_effect_lcdm_tt_ee_lowl.md |

# Controls appendix

| control | value |
|---|---|
| stage-1 perm null z0: R2 p97.5 / max-MI p97.5 | -0.002 / 0.014 |
| stage-1 perm null z1: R2 p97.5 / max-MI p97.5 | -0.002 / 0.001 |
| stage-1 perm null z2: R2 p97.5 / max-MI p97.5 | -0.002 / 0.001 |
| stage-1 perm null z3: R2 p97.5 / max-MI p97.5 | -0.002 / 0.001 |
| stage-1 perm null z4: R2 p97.5 / max-MI p97.5 | -0.003 / 0.019 |
| stage-1 perm null z5: R2 p97.5 / max-MI p97.5 | -0.002 / 0.001 |
| shuffled-residual SR (res_z5, seed 0) best MI vs true residual | 0.009 |
| shuffled-residual SR (res_z5, seed 1) best MI vs true residual | 0.060 |
| level-set shuffled form (seed 0) E_inv | 1.69 |
| level-set shuffled form (seed 1) E_inv | 1.59 |
| level-set shuffled form (seed 2) E_inv | 1.81 |
| wrong-latent E_inv (f1-only + joint) | z0 2.37, z1 2.44, z2 2.50, z3 2.53, z4 1.02, z0 1.41, z1 0.23, z2 2.27, z3 1.52, z4 1.01 |
| subspace shuffled-probe max R2 | -0.000 |

# Deviation register

* **D-P2a** (phase 2): R_SR seed-level tolerance = one cross-seed SD, not SE-of-mean (the literal §0.3 rule caps R_SR ~0.7 by seed scatter alone even for perfectly stable coordinates). semantic_recurrence md.
* **D-P2b** (phase 2): cluster representatives must be directly equivalent to a majority of sampled members (anti-chaining guard on union-find; cohesion reported per cluster). semantic_recurrence md.
* **R-P5** (phase 5): registered refinement (decided on the synthetic positive control before real data): eta_post_hat = MI(Z;f)/MI(Z;mu) drives the 0.95 demotion rule; analytic eta_post = MI/I stays the headline. posterior_ceiling md.
* **D-LS** (phase 7a/10): level-set status leg evaluated on the joint (f1,f2) audit (and response-only where the joint union support is all 6); the f1-only E_inv failure is the Phase-3 structured residual identically. Frozen thresholds unchanged; a joint FAIL still blocks. levelset_audit_joint md + this docstring.

---
_Generated by `scripts/build_latent_cards.py`._
