# Decoder-effect triangulation — `lcdm_tt_ee_lowl` (roadmap Phase 7b, gate G4b)

d_k(ℓ) = ∂Decoder(z)_ℓ/∂z_k by JVP at the T1 mean (anchor) and across 64 T1 posterior-mean rows (spread mean ± band); per-ℓ σ from `scaler.npz` converts to physical ∂log₁₀D_ℓ/∂z_k. Decomposition d_k ≈ Σ_j a_kj·t_j against the local-quadratic templates (h=0.6, check h=0.3), no intercept, W = identity in normalised space; a_kj = u_j-units per unit z_k. r_dec = (a_τ/half_τ)/(a_lnAs/half_lnAs) is the implied raw-space amplitude-pair ratio. cos g_j triangulates |a| against the Phase-3 symbolic signature. Figure: `decoder_effect_lcdm_tt_ee_lowl_curves.png`; full curves in the twin .npz.

## Template identifiability of the (τ, lnAs) split

| design | uncentered cos(t_τ, t_lnAs) | cond |
|---|---:|---:|
| concat | -0.9902 | 14.2 |
| tt | -0.9996 | 70.2 |
| ee | -0.9770 | 9.3 |

_The pair is **ridge-limited** in this run's design (cond > 10): moving θ along the degenerate direction (δτ, δlnAs) ∝ (1, 2) leaves these spectra invisible, so the fitted (a_τ, a_lnAs) split — hence r_dec and amp mass — drifts freely along that ridge and only proj_brk (the degeneracy-breaking component, direction (−2, 1)/√5 in raw (τ, lnAs)) is identifiable. proj_deg and r_dec below are reported for completeness, not as claims._

| latent | role | a (u-units/z, OLS) | R²_W | lasso support | amp mass | r_dec | proj_deg | proj_brk | cos g_j | min stab cos |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| z0 | omega_cdm | omega_b=+0.21 omega_cdm=-0.33 H0=+0.25 tau=+0.03 ln10As=-0.06 n_s=+0.12 | 0.997 | {omega_b, omega_cdm, H0, tau, ln10As, n_s} | 0.09 | -1.36 | -0.006 | -0.005 | 0.99 | 1.000 |
| z1 | H0 | omega_b=+0.08 omega_cdm=-0.16 H0=-0.52 tau=+0.17 ln10As=-0.02 n_s=+0.01 | 0.989 | {omega_b, omega_cdm, H0, tau, ln10As, n_s} | 0.20 | -24.16 | 0.003 | -0.010 | 0.93 | 0.822 |
| z2 | omega_b | omega_b=+0.42 omega_cdm=+0.13 H0=-0.01 ln10As=+0.04 n_s=-0.35 | 1.000 | {omega_b, omega_cdm, H0, tau, ln10As, n_s} | 0.05 | -0.27 | 0.005 | 0.003 | 0.97 | 0.999 |
| z3 | n_s | omega_b=+0.27 omega_cdm=+0.26 H0=-0.07 ln10As=-0.01 n_s=+0.43 | 1.000 | {omega_b, omega_cdm, H0, ln10As, n_s} | 0.01 | n/a | -0.001 | -0.000 | 0.97 | 0.995 |
| z4 | tau (amplitude sector) | omega_cdm=+0.03 H0=-0.02 tau=-0.40 ln10As=-0.33 n_s=-0.03 | 0.988 | {omega_b, omega_cdm, H0, tau, ln10As, n_s} | 0.90 | 2.80 | -0.053 | 0.001 | 1.00 | 1.000 |
| z5 | amplitude (A_s, tau) | omega_b=+0.02 omega_cdm=-0.09 H0=-0.05 tau=-0.36 ln10As=+0.44 n_s=+0.05 | 1.000 | {omega_b, omega_cdm, H0, tau, ln10As, n_s} | 0.79 | -1.87 | 0.046 | 0.047 | 0.98 | 0.989 |

_Stability cosines compare the OLS coefficient vector against the (2ℓ+1)-weighted physical-space refit, the halved-bandwidth templates, and the anchor-point curve; on a ridge-limited design they are dominated by ridge drift of the (τ, lnAs) split and understate the stability of the identifiable components._


## z0 — omega_cdm

| variant | a | R² | r_dec | proj_deg | proj_brk |
|---|---|---:|---:|---:|---:|
| OLS (normalised) | omega_b=+0.21 omega_cdm=-0.33 H0=+0.25 tau=+0.03 ln10As=-0.06 n_s=+0.12 | 0.997 | -1.36 | -0.006 | -0.005 |
| post-lasso | omega_b=+0.21 omega_cdm=-0.33 H0=+0.25 tau=+0.03 ln10As=-0.06 n_s=+0.12 |  |  | n/a | n/a |
| (2ℓ+1)-weighted | omega_b=+0.21 omega_cdm=-0.33 H0=+0.25 tau=+0.03 ln10As=-0.06 n_s=+0.12 | 0.992 | -1.16 | -0.006 | -0.005 |
| templates h/2 | omega_b=+0.21 omega_cdm=-0.33 H0=+0.25 tau=+0.04 ln10As=-0.05 n_s=+0.12 | 0.997 | -1.63 | -0.005 | -0.005 |
| anchor point | omega_b=+0.31 omega_cdm=-0.49 H0=+0.37 tau=+0.04 ln10As=-0.09 n_s=+0.18 | 0.995 | -1.01 | -0.010 | -0.008 |

## z1 — H0

| variant | a | R² | r_dec | proj_deg | proj_brk |
|---|---|---:|---:|---:|---:|
| OLS (normalised) | omega_b=+0.08 omega_cdm=-0.16 H0=-0.52 tau=+0.17 ln10As=-0.02 n_s=+0.01 | 0.989 | -24.16 | 0.003 | -0.010 |
| post-lasso | omega_b=+0.08 omega_cdm=-0.16 H0=-0.52 tau=+0.17 ln10As=-0.02 n_s=+0.01 |  |  | n/a | n/a |
| (2ℓ+1)-weighted | omega_b=+0.07 omega_cdm=+0.15 H0=-0.71 tau=+0.21 ln10As=+0.11 n_s=-0.24 | 0.994 | 4.41 | 0.019 | -0.004 |
| templates h/2 | omega_b=+0.11 omega_cdm=-0.12 H0=-0.51 tau=+0.20 ln10As=+0.02 n_s=+0.03 | 0.981 | 23.83 | 0.008 | -0.010 |
| anchor point | omega_b=-0.02 omega_cdm=-0.22 H0=-0.61 tau=+0.07 ln10As=-0.13 n_s=-0.03 | 0.995 | -1.19 | -0.015 | -0.012 |

## z2 — omega_b

| variant | a | R² | r_dec | proj_deg | proj_brk |
|---|---|---:|---:|---:|---:|
| OLS (normalised) | omega_b=+0.42 omega_cdm=+0.13 H0=-0.01 ln10As=+0.04 n_s=-0.35 | 1.000 | -0.27 | 0.005 | 0.003 |
| post-lasso | omega_b=+0.42 omega_cdm=+0.13 H0=-0.01 ln10As=+0.04 n_s=-0.35 |  |  | n/a | n/a |
| (2ℓ+1)-weighted | omega_b=+0.42 omega_cdm=+0.13 H0=-0.01 ln10As=+0.04 n_s=-0.36 | 1.000 | -0.25 | 0.005 | 0.003 |
| templates h/2 | omega_b=+0.42 omega_cdm=+0.12 H0=-0.01 tau=-0.01 ln10As=+0.04 n_s=-0.35 | 1.000 | -0.30 | 0.005 | 0.003 |
| anchor point | omega_b=+0.45 omega_cdm=+0.15 H0=-0.02 ln10As=+0.05 n_s=-0.38 | 0.999 | -0.01 | 0.007 | 0.003 |

## z3 — n_s

| variant | a | R² | r_dec | proj_deg | proj_brk |
|---|---|---:|---:|---:|---:|
| OLS (normalised) | omega_b=+0.27 omega_cdm=+0.26 H0=-0.07 ln10As=-0.01 n_s=+0.43 | 1.000 | n/a | -0.001 | -0.000 |
| post-lasso | omega_b=+0.27 omega_cdm=+0.26 H0=-0.07 ln10As=-0.01 n_s=+0.43 |  |  | n/a | n/a |
| (2ℓ+1)-weighted | omega_b=+0.27 omega_cdm=+0.25 H0=-0.06 ln10As=-0.01 n_s=+0.44 | 1.000 | n/a | -0.002 | -0.001 |
| templates h/2 | omega_b=+0.27 omega_cdm=+0.26 H0=-0.07 tau=-0.01 ln10As=-0.01 n_s=+0.42 | 0.999 | n/a | -0.002 | -0.000 |
| anchor point | omega_b=+0.27 omega_cdm=+0.32 H0=-0.10 ln10As=+0.01 n_s=+0.43 | 0.999 | n/a | 0.001 | 0.000 |

## z4 — tau (amplitude sector)

| variant | a | R² | r_dec | proj_deg | proj_brk |
|---|---|---:|---:|---:|---:|
| OLS (normalised) | omega_cdm=+0.03 H0=-0.02 tau=-0.40 ln10As=-0.33 n_s=-0.03 | 0.988 | 2.80 | -0.053 | 0.001 |
| post-lasso | omega_cdm=+0.03 H0=-0.02 tau=-0.40 ln10As=-0.33 n_s=-0.03 |  |  | n/a | n/a |
| (2ℓ+1)-weighted | omega_cdm=+0.04 H0=-0.03 tau=-0.39 ln10As=-0.33 n_s=-0.03 | 0.997 | 2.81 | -0.051 | 0.001 |
| templates h/2 | omega_cdm=+0.03 H0=-0.02 tau=-0.39 ln10As=-0.33 n_s=-0.03 | 0.946 | 2.80 | -0.051 | 0.001 |
| anchor point | omega_cdm=+0.05 H0=-0.03 tau=-0.56 ln10As=-0.47 n_s=-0.05 | 0.921 | 2.82 | -0.073 | 0.001 |

## z5 — amplitude (A_s, tau)

| variant | a | R² | r_dec | proj_deg | proj_brk |
|---|---|---:|---:|---:|---:|
| OLS (normalised) | omega_b=+0.02 omega_cdm=-0.09 H0=-0.05 tau=-0.36 ln10As=+0.44 n_s=+0.05 | 1.000 | -1.87 | 0.046 | 0.047 |
| post-lasso | omega_b=+0.02 omega_cdm=-0.09 H0=-0.05 tau=-0.36 ln10As=+0.44 n_s=+0.05 |  |  | n/a | n/a |
| (2ℓ+1)-weighted | omega_b=+0.02 omega_cdm=-0.03 H0=-0.08 tau=-0.34 ln10As=+0.47 n_s=+0.01 | 1.000 | -1.67 | 0.050 | 0.048 |
| templates h/2 | omega_b=+0.03 omega_cdm=-0.09 H0=-0.04 tau=-0.34 ln10As=+0.45 n_s=+0.06 | 1.000 | -1.77 | 0.048 | 0.047 |
| anchor point | omega_cdm=-0.08 H0=-0.08 tau=-0.41 ln10As=+0.42 n_s=+0.02 | 1.000 | -2.32 | 0.041 | 0.048 |

# Gate G4b (decoder bullet of G4)

| bullet | numbers | pass |
|---|---|---|
| amplitude-sector mass ≥ 0.8 | 0.79 | FAIL |
| \|r_dec + 2\| ≤ 0.3 | r_dec = -1.873 | PASS |
| decomposition R²_W ≥ 0.8 | 1.000 | PASS |

**Gate G4b: FAIL**

_Mechanism: with cond = 14.2 the r_dec and amp-mass bullets test a within-pair split this run's spectra cannot express — the A_s e^{−2τ} degenerate direction is invisible to them, so the frozen rule is evaluated as registered but its FAIL here reflects template collinearity, not a wrong decoder direction. The identifiable decoder-side statement is proj_brk and the shape-sector coefficients above._

G4a (level-set bullet, Phase 7a): **FAIL** — the documented structured-residual E_inv verdict; see `levelset_audit_lcdm_tt_ee_lowl.md`.

---
_Generated by `scripts/decoder_effect.py`._
