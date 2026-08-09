# Latent cards — `lcdm_tt_beta3e-4` (roadmap Phase 10)

One §0.1 card per latent, statuses from the frozen §0.3 predicates (deviation register at the end; D-LS defines the level-set leg). All numbers are merged verbatim from the Phase 1-8 deliverables named on each line — no new computation.

| latent | role | status | f1 | eta_S | eta_post_hat | eta_ph_comb | R_SR | E_inv joint | axis-aligned |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| z0 | omega_b | **primarily interpreted** | `n_s/omega_b` | 1.003 | 0.531 | 0.903 | 1.00 | 0.022 | False |
| z1 | omega_cdm | **primarily interpreted** | `H0**2*n_s**2*omega_b/(A_s*omega_cdm*` | 1.000 | 0.770 | 0.957 | 0.80 | n/a | False |
| z2 | amplitude (A_s, tau) | **primarily interpreted** | `A_s/log(H0*(omega_cdm + tau))` | 1.000 | 0.347 | 0.601 | 1.00 | n/a | False |
| z3 | n_s | **primarily interpreted** | `n_s + omega_cdm` | 0.997 | 0.447 | 0.838 | 1.00 | 0.013 | False |
| z4 | H0 | **primarily interpreted** | `A_s*H0**2*omega_cdm*exp(-2*tau)` | 1.000 | 0.371 | 0.758 | 0.80 | n/a | False |

## z0 — omega_b

**Status: primarily interpreted** — eta_S + R_SR + level-set evidence green; stage-1 residual structured (f2 documented)

* f1 `n_s/omega_b` (C=3, support {omega_b, n_s}, R_SR 1.00, cohesion 0.96) [semantic_recurrence]
* knee c* = 26, plateau 3.570 +/- 0.059 nat (allparams_ms30), MI@c<=10 2.561, envelope: no knee (diffuse) [knee_readout]
* S* = {omega_b, omega_cdm, H0, A_s, n_s} (|S|=5, eta_S 1.003 +/- 0.020, screen-recurrent False) [subset_selection]
* ceiling I(Z;theta) = 1.984 +/- 0.002 nat (SNR 55.4); eta_post 0.545 +/- 0.005, eta_post_hat 0.531 +/- 0.006; combined (f1+f2): eta_post_hat 0.903, eta_plat 0.688 [posterior_ceiling, residual_sr]
* signature g_j: ob=0.66 ns=0.34; decoder cos_g 0.95 [sufficiency_audit, decoder_effect]
* stage-1 residual: R2_cal 0.904, R2_res 0.992 -> FAIL (loadings {omega_b, omega_cdm, H0, tau, ln10As, n_s}) [sufficiency_audit]
* f2 `n_s*(H0 + 1325.0747*omega_cdm)` (support {omega_cdm, H0, n_s}, shape-sector True, R_SR 0.80, MI vs e1 1.106); combined R2(mu) 0.989; stage-2 residual FAIL [residual_sr]
* level sets: f1-only E_inv 0.205 (band 0.096-0.192, resp R2 0.91) -> FAIL; joint (f1,f2) E_inv 0.022 (band 0.011-0.022, resp 0.99) -> PASS [levelset_audit, levelset_audit_joint]
* decoder effect: a = [ob=-0.52 oc=-0.15 H0=-0.05 tau=+0.05 lnAs=+0.01 ns=+0.17], R2_W 1.000, amp mass 0.07, frac_brk 0.41 [decoder_effect]
* subspace probe: A* = {z0, z2, z3, z4} (axis-aligned False), R2 own 0.884 / full 0.985 (T2 0.984); top pair (z0, z3), redundancy(2|1) -11.31 [subspace_probe]
* deviations: **D-LS** level-set leg via joint (f1,f2) audit; **N-G2** S* not recurrent across the two screen seeds (ATTENTION (not screen-recurrent))

## z1 — omega_cdm

**Status: primarily interpreted** — eta_S + R_SR + level-set evidence green; stage-1 residual structured (f2 documented)

* f1 `H0**2*n_s**2*omega_b/(A_s*omega_cdm**2)` (C=10, support {omega_b, omega_cdm, H0, ln10As, n_s}, R_SR 0.80, cohesion 0.67) [semantic_recurrence]
* knee c* = 29, plateau 2.515 +/- 0.013 nat (allparams_ms30), MI@c<=10 1.211, envelope: no knee (diffuse) [knee_readout]
* S* = {omega_b, omega_cdm, H0, tau, A_s, n_s} (|S|=6, eta_S 1.000 +/- 0.000, screen-recurrent True) [subset_selection]
* ceiling I(Z;theta) = 0.919 +/- 0.003 nat (SNR 5.1); eta_post 0.761 +/- 0.014, eta_post_hat 0.770 +/- 0.018; combined (f1+f2): eta_post_hat 0.957, eta_plat 0.824 [posterior_ceiling, residual_sr]
* signature g_j: ob=0.11 oc=0.32 H0=0.30 lnAs=0.17 ns=0.11; decoder cos_g 0.94; ratio pairs: (omega_b,ln10As) r=-45.655; (ln10As,n_s) r=-0.483 [sufficiency_audit, decoder_effect]
* stage-1 residual: R2_cal 0.906, R2_res 0.981 -> FAIL (loadings {omega_b, omega_cdm, H0, tau, ln10As, n_s}) [sufficiency_audit]
* f2 `n_s/log(-H0/(tau - 0.44653893)) + omega_b` (support {omega_b, H0, tau, n_s}, shape-sector False, R_SR 0.80, MI vs e1 0.888); combined R2(mu) 0.981; stage-2 residual FAIL [residual_sr]
* level sets: f1-only E_inv 0.126 (band 0.094-0.189, resp R2 0.91) -> FAIL; joint (f1,f2) E_inv n/a (band 0.019-0.037, resp 0.98) -> undefined (union=all 6) [levelset_audit, levelset_audit_joint]
* decoder effect: a = [ob=+0.12 oc=-0.29 H0=+0.22 tau=-0.13 lnAs=-0.19 ns=+0.19], R2_W 0.997, amp mass 0.28, frac_brk 0.15 [decoder_effect]
* subspace probe: A* = {z0, z1, z2, z3, z4} (axis-aligned False), R2 own 0.905 / full 0.983 (T2 0.982); top pair (z1, z2), redundancy(2|1) -9.07 [subspace_probe]
* deviations: **D-LS** level-set leg via response-only (joint union support = all 6)

## z2 — amplitude (A_s, tau)

**Status: primarily interpreted** — eta_S + R_SR + level-set evidence green; stage-1 residual structured (f2 documented)

* f1 `A_s/log(H0*(omega_cdm + tau))` (C=8, support {omega_cdm, H0, tau, ln10As}, R_SR 1.00, cohesion 0.99) [semantic_recurrence]
* knee c* = 24, plateau 4.175 +/- 0.043 nat (allparams_ms30), MI@c<=10 1.891, envelope: no knee (diffuse) [knee_readout]
* S* = {omega_b, omega_cdm, H0, tau, A_s, n_s} (|S|=6, eta_S 1.000 +/- 0.000, screen-recurrent True) [subset_selection]
* ceiling I(Z;theta) = 4.304 +/- 0.003 nat (SNR 5490.8); eta_post 0.347 +/- 0.003, eta_post_hat 0.347 +/- 0.003; combined (f1+f2): eta_post_hat 0.601, eta_plat 0.629 [posterior_ceiling, residual_sr]
* signature g_j: oc=0.10 H0=0.14 tau=0.38 lnAs=0.38; decoder cos_g 0.81; ratio pairs: (omega_cdm,tau) r=+1.000 [sufficiency_audit, decoder_effect]
* stage-1 residual: R2_cal 0.947, R2_res 0.985 -> FAIL (loadings {omega_b, omega_cdm, H0, tau, ln10As, n_s}) [sufficiency_audit]
* f2 `n_s**2*omega_b*tau/(omega_cdm*tau + 0.00031008976)` (support {omega_b, omega_cdm, tau, n_s}, shape-sector False, R_SR 0.80, MI vs e1 1.058); combined R2(mu) 0.993; stage-2 residual FAIL [residual_sr]
* level sets: f1-only E_inv 0.098 (band 0.053-0.106, resp R2 0.95) -> FAIL; joint (f1,f2) E_inv n/a (band 0.007-0.014, resp 0.99) -> undefined (union=all 6) [levelset_audit, levelset_audit_joint]
* decoder effect: a = [ob=+0.05 oc=-0.19 H0=-0.16 tau=+0.12 lnAs=+0.77 ns=+0.10], R2_W 1.000, amp mass 0.64, r_dec 0.35, frac_brk 0.30 [decoder_effect]
* subspace probe: A* = {z0, z1, z2, z3, z4} (axis-aligned False), R2 own 0.946 / full 0.983 (T2 0.982); top pair (z2, z4), redundancy(2|1) -8.79 [subspace_probe]
* deviations: **D-DoD-z2** Phase-6 amplitude DoD NOT MET, and substantively: f2 keeps tau (tau-clamping costs 0.20 nat of MI vs e1, Spearman 0.92 < 0.98, d_grad 0.127 > 0.05 vs the shape-only approximant) — the additive h(f1)+g(f2) hierarchy cannot absorb the multiplicative amplitude x shape interaction of the knee forms. Commit a38e6c8.; **D-LS** level-set leg via response-only (joint union support = all 6)

## z3 — n_s

**Status: primarily interpreted** — eta_S + R_SR + level-set evidence green; stage-1 residual structured (f2 documented)

* f1 `n_s + omega_cdm` (C=3, support {omega_cdm, n_s}, R_SR 1.00, cohesion 1.00) [semantic_recurrence]
* knee c* = 27, plateau 3.147 +/- 0.030 nat (allparams_ms30), MI@c<=10 2.279, envelope: no knee (diffuse) [knee_readout]
* S* = {omega_b, omega_cdm, H0, tau, n_s} (|S|=5, eta_S 0.997 +/- 0.005, screen-recurrent True) [subset_selection]
* ceiling I(Z;theta) = 2.646 +/- 0.003 nat (SNR 204.7); eta_post 0.449 +/- 0.004, eta_post_hat 0.447 +/- 0.004; combined (f1+f2): eta_post_hat 0.838, eta_plat 0.816 [posterior_ceiling, residual_sr]
* signature g_j: oc=0.25 ns=0.75; decoder cos_g 0.90; ratio pairs: (omega_cdm,n_s) r=+1.000 [sufficiency_audit, decoder_effect]
* stage-1 residual: R2_cal 0.916, R2_res 0.993 -> FAIL (loadings {omega_b, omega_cdm, H0, tau, ln10As, n_s}) [sufficiency_audit]
* f2 `H0/(omega_b**2*omega_cdm**2)` (support {omega_b, omega_cdm, H0}, shape-sector True, R_SR 0.80, MI vs e1 1.087); combined R2(mu) 0.989; stage-2 residual FAIL [residual_sr]
* level sets: f1-only E_inv 0.122 (band 0.084-0.168, resp R2 0.92) -> FAIL; joint (f1,f2) E_inv 0.013 (band 0.011-0.023, resp 0.99) -> PASS [levelset_audit, levelset_audit_joint]
* decoder effect: a = [ob=+0.09 oc=+0.29 H0=-0.04 tau=-0.01 ns=+0.49], R2_W 0.999, amp mass 0.23, frac_brk 0.06 [decoder_effect]
* subspace probe: A* = {z0, z1, z3} (axis-aligned False), R2 own 0.910 / full 0.974 (T2 0.974); top pair (z3, z1), redundancy(2|1) -6.28 [subspace_probe]
* deviations: **D-LS** level-set leg via joint (f1,f2) audit

## z4 — H0

**Status: primarily interpreted** — eta_S + R_SR + level-set evidence green; stage-1 residual structured (f2 documented)

* f1 `A_s*H0**2*omega_cdm*exp(-2*tau)` (C=9, support {omega_cdm, H0, tau, ln10As}, R_SR 0.80, cohesion 0.96) [semantic_recurrence]
* knee c* = 24, plateau 4.313 +/- 0.120 nat (allparams_ms30), MI@c<=10 1.318, envelope: no knee (diffuse) [knee_readout]
* S* = {omega_b, omega_cdm, H0, tau, A_s, n_s} (|S|=6, eta_S 1.000 +/- 0.000, screen-recurrent True) [subset_selection]
* ceiling I(Z;theta) = 3.441 +/- 0.003 nat (SNR 986.5); eta_post 0.370 +/- 0.004, eta_post_hat 0.371 +/- 0.004; combined (f1+f2): eta_post_hat 0.758, eta_plat 0.636 [posterior_ceiling, residual_sr]
* signature g_j: oc=0.20 H0=0.39 tau=0.19 lnAs=0.22; decoder cos_g 0.77; ratio pairs: (tau,ln10As) r=-2.000 [sufficiency_audit, decoder_effect]
* stage-1 residual: R2_cal 0.921, R2_res 0.989 -> FAIL (loadings {omega_b, omega_cdm, H0, tau, ln10As, n_s}) [sufficiency_audit]
* f2 `log(H0)/(n_s*omega_b)` (support {omega_b, H0, n_s}, shape-sector True, R_SR 0.80, MI vs e1 1.186); combined R2(mu) 0.993; stage-2 residual FAIL [residual_sr]
* level sets: f1-only E_inv 0.208 (band 0.079-0.157, resp R2 0.92) -> FAIL; joint (f1,f2) E_inv n/a (band 0.007-0.015, resp 0.99) -> undefined (union=all 6) [levelset_audit, levelset_audit_joint]
* decoder effect: a = [ob=+0.10 oc=-0.15 H0=-0.48 tau=+0.35 ns=+0.05], R2_W 0.996, amp mass 0.64, frac_brk 0.17 [decoder_effect]
* subspace probe: A* = {z0, z1, z2, z3, z4} (axis-aligned False), R2 own 0.918 / full 0.996 (T2 0.996); top pair (z4, z0), redundancy(2|1) -10.92 [subspace_probe]
* deviations: **D-LS** level-set leg via response-only (joint union support = all 6)

# Gates

| gate | verdict | source |
|---|---|---|
| G1 (amplitude positive control) | PASS | sufficiency_audit_lcdm_tt_beta3e-4.md (amplitude positive control; both models 2026-08-03) |
| G2 (S* selection) | see per-latent verdicts | subset_selection_lcdm_tt_beta3e-4.md |
| G3 (posterior ceiling, DPI) | PASS | posterior_ceiling_lcdm_tt_beta3e-4.md |
| G4a (level sets, f1-only) | FAIL | levelset_audit_lcdm_tt_beta3e-4.md |
| G4a-joint (level sets, f1+f2) | UNDEFINED | levelset_audit_joint_lcdm_tt_beta3e-4.md |
| G4b (decoder triangulation) | FAIL | decoder_effect_lcdm_tt_beta3e-4.md |

# Controls appendix

| control | value |
|---|---|
| stage-1 perm null z0: R2 p97.5 / max-MI p97.5 | -0.002 / 0.001 |
| stage-1 perm null z1: R2 p97.5 / max-MI p97.5 | -0.002 / 0.001 |
| stage-1 perm null z2: R2 p97.5 / max-MI p97.5 | -0.002 / 0.001 |
| stage-1 perm null z3: R2 p97.5 / max-MI p97.5 | -0.002 / 0.001 |
| stage-1 perm null z4: R2 p97.5 / max-MI p97.5 | -0.002 / 0.001 |
| shuffled-residual SR (res_z2, seed 0) best MI vs true residual | 0.074 |
| shuffled-residual SR (res_z2, seed 1) best MI vs true residual | 0.066 |
| level-set shuffled form (seed 0) E_inv | 1.73 |
| level-set shuffled form (seed 1) E_inv | 0.81 |
| level-set shuffled form (seed 2) E_inv | 2.20 |
| wrong-latent E_inv (f1-only + joint) | z0 2.79, z1 1.54, z3 2.36, z4 1.06 |
| subspace shuffled-probe max R2 | -0.000 |

# Deviation register

* **D-P2a** (phase 2): R_SR seed-level tolerance = one cross-seed SD, not SE-of-mean (the literal §0.3 rule caps R_SR ~0.7 by seed scatter alone even for perfectly stable coordinates). semantic_recurrence md.
* **D-P2b** (phase 2): cluster representatives must be directly equivalent to a majority of sampled members (anti-chaining guard on union-find; cohesion reported per cluster). semantic_recurrence md.
* **R-P5** (phase 5): registered refinement (decided on the synthetic positive control before real data): eta_post_hat = MI(Z;f)/MI(Z;mu) drives the 0.95 demotion rule; analytic eta_post = MI/I stays the headline. posterior_ceiling md.
* **D-LS** (phase 7a/10): level-set status leg evaluated on the joint (f1,f2) audit (and response-only where the joint union support is all 6); the f1-only E_inv failure is the Phase-3 structured residual identically. Frozen thresholds unchanged; a joint FAIL still blocks. levelset_audit_joint md + this docstring.

---
_Generated by `scripts/build_latent_cards.py`._
