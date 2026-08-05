# Decoder-effect triangulation — `lcdm_tt_beta3e-4` (roadmap Phase 7b, gate G4b)

d_k(ℓ) = ∂Decoder(z)_ℓ/∂z_k by JVP at the T1 mean (anchor) and across 64 T1 posterior-mean rows (spread mean ± band); per-ℓ σ from `scaler.npz` converts to physical ∂log₁₀D_ℓ/∂z_k. Decomposition d_k ≈ Σ_j a_kj·t_j against the local-quadratic templates (h=0.6, check h=0.3), no intercept, W = identity in normalised space; a_kj = u_j-units per unit z_k. r_dec = (a_τ/half_τ)/(a_lnAs/half_lnAs) is the implied raw-space amplitude-pair ratio. cos g_j triangulates |a| against the Phase-3 symbolic signature. Figure: `decoder_effect_lcdm_tt_beta3e-4_curves.png`; full curves in the twin .npz.

## Template identifiability of the (τ, lnAs) split

| design | uncentered cos(t_τ, t_lnAs) | cond |
|---|---:|---:|
| concat | -0.9996 | 70.2 |
| tt | -0.9996 | 70.2 |

_The pair is **ridge-limited** in this run's design (cond > 10): moving θ along the degenerate direction (δτ, δlnAs) ∝ (1, 2) leaves these spectra invisible, so the fitted (a_τ, a_lnAs) split — hence r_dec and amp mass — drifts freely along that ridge and only proj_brk (the degeneracy-breaking component, direction (−2, 1)/√5 in raw (τ, lnAs)) is identifiable. proj_deg and r_dec below are reported for completeness, not as claims._

| latent | role | a (u-units/z, OLS) | R²_W | lasso support | amp mass | r_dec | proj_deg | proj_brk | cos g_j | min stab cos |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| z0 | omega_b | omega_b=-0.52 omega_cdm=-0.15 H0=-0.05 tau=+0.05 ln10As=+0.01 n_s=+0.17 | 1.000 | {omega_b, omega_cdm, H0, tau, ln10As, n_s} | 0.07 | n/a | 0.003 | -0.002 | 0.95 | 0.990 |
| z1 | omega_cdm | omega_b=+0.12 omega_cdm=-0.29 H0=+0.22 tau=-0.13 ln10As=-0.19 n_s=+0.19 | 0.997 | {omega_b, omega_cdm, H0, tau, ln10As, n_s} | 0.28 | 1.61 | -0.027 | -0.005 | 0.94 | 0.955 |
| z2 | amplitude (A_s, tau) | omega_b=+0.05 omega_cdm=-0.19 H0=-0.16 tau=+0.12 ln10As=+0.77 n_s=+0.10 | 1.000 | {omega_b, omega_cdm, H0, tau, ln10As, n_s} | 0.64 | 0.35 | 0.100 | 0.042 | 0.81 | 0.566 |
| z3 | n_s | omega_b=+0.08 omega_cdm=+0.31 H0=-0.06 tau=-0.16 ln10As=-0.12 n_s=+0.47 | 0.999 | {omega_b, omega_cdm, H0, tau, n_s} | 0.23 | 3.19 | -0.019 | 0.001 | 0.90 | 0.848 |
| z4 | H0 | omega_b=+0.11 omega_cdm=-0.26 H0=-0.40 tau=+1.05 ln10As=+0.56 n_s=+0.14 | 0.996 | {omega_b, omega_cdm, H0, tau, n_s} | 0.64 | 4.32 | 0.099 | -0.021 | 0.77 | -0.218 |

_Stability cosines compare the OLS coefficient vector against the (2ℓ+1)-weighted physical-space refit, the halved-bandwidth templates, and the anchor-point curve; on a ridge-limited design they are dominated by ridge drift of the (τ, lnAs) split and understate the stability of the identifiable components._


## z0 — omega_b

| variant | a | R² | r_dec | proj_deg | proj_brk |
|---|---|---:|---:|---:|---:|
| OLS (normalised) | omega_b=-0.52 omega_cdm=-0.15 H0=-0.05 tau=+0.05 ln10As=+0.01 n_s=+0.17 | 1.000 | n/a | 0.003 | -0.002 |
| post-lasso | omega_b=-0.52 omega_cdm=-0.15 H0=-0.05 tau=+0.05 ln10As=+0.01 n_s=+0.17 |  |  | n/a | n/a |
| (2ℓ+1)-weighted | omega_b=-0.52 omega_cdm=-0.14 H0=-0.05 tau=+0.06 ln10As=+0.02 n_s=+0.17 | 0.999 | n/a | 0.004 | -0.002 |
| templates h/2 | omega_b=-0.52 omega_cdm=-0.15 H0=-0.05 tau=+0.06 ln10As=+0.02 n_s=+0.17 | 0.999 | n/a | 0.004 | -0.002 |
| anchor point | omega_b=-0.56 omega_cdm=-0.15 H0=-0.07 tau=-0.01 ln10As=-0.04 n_s=+0.17 | 1.000 | n/a | -0.005 | -0.002 |

## z1 — omega_cdm

| variant | a | R² | r_dec | proj_deg | proj_brk |
|---|---|---:|---:|---:|---:|
| OLS (normalised) | omega_b=+0.12 omega_cdm=-0.29 H0=+0.22 tau=-0.13 ln10As=-0.19 n_s=+0.19 | 0.997 | 1.61 | -0.027 | -0.005 |
| post-lasso | omega_b=+0.12 omega_cdm=-0.29 H0=+0.22 tau=-0.13 ln10As=-0.19 n_s=+0.19 |  |  | n/a | n/a |
| (2ℓ+1)-weighted | omega_b=+0.12 omega_cdm=-0.29 H0=+0.22 tau=-0.12 ln10As=-0.18 n_s=+0.19 | 0.991 | 1.56 | -0.025 | -0.005 |
| templates h/2 | omega_b=+0.12 omega_cdm=-0.29 H0=+0.22 tau=-0.10 ln10As=-0.16 n_s=+0.19 | 0.997 | 1.45 | -0.023 | -0.005 |
| anchor point | omega_b=+0.19 omega_cdm=-0.46 H0=+0.36 tau=-0.03 ln10As=-0.15 n_s=+0.31 | 0.998 | 0.45 | -0.019 | -0.008 |

## z2 — amplitude (A_s, tau)

| variant | a | R² | r_dec | proj_deg | proj_brk |
|---|---|---:|---:|---:|---:|
| OLS (normalised) | omega_b=+0.05 omega_cdm=-0.19 H0=-0.16 tau=+0.12 ln10As=+0.77 n_s=+0.10 | 1.000 | 0.35 | 0.100 | 0.042 |
| post-lasso | omega_b=+0.05 omega_cdm=-0.19 H0=-0.16 tau=+0.12 ln10As=+0.77 n_s=+0.10 |  |  | n/a | n/a |
| (2ℓ+1)-weighted | omega_b=+0.01 omega_cdm=-0.12 H0=-0.21 tau=+0.23 ln10As=+0.89 n_s=+0.04 | 1.000 | 0.60 | 0.118 | 0.043 |
| templates h/2 | omega_b=+0.07 omega_cdm=-0.21 H0=-0.14 tau=+0.22 ln10As=+0.86 n_s=+0.12 | 1.000 | 0.60 | 0.114 | 0.042 |
| anchor point | omega_b=+0.03 omega_cdm=-0.14 H0=-0.24 tau=-0.42 ln10As=+0.34 n_s=+0.02 | 1.000 | -2.85 | 0.032 | 0.044 |

## z3 — n_s

| variant | a | R² | r_dec | proj_deg | proj_brk |
|---|---|---:|---:|---:|---:|
| OLS (normalised) | omega_b=+0.08 omega_cdm=+0.31 H0=-0.06 tau=-0.16 ln10As=-0.12 n_s=+0.47 | 0.999 | 3.19 | -0.019 | 0.001 |
| post-lasso | omega_b=+0.09 omega_cdm=+0.29 H0=-0.04 tau=-0.01 n_s=+0.49 |  |  | n/a | n/a |
| (2ℓ+1)-weighted | omega_b=+0.10 omega_cdm=+0.28 H0=-0.04 tau=-0.20 ln10As=-0.16 n_s=+0.49 | 1.000 | 2.93 | -0.025 | 0.001 |
| templates h/2 | omega_b=+0.08 omega_cdm=+0.32 H0=-0.07 tau=-0.22 ln10As=-0.17 n_s=+0.46 | 0.999 | 3.06 | -0.027 | 0.001 |
| anchor point | omega_b=+0.10 omega_cdm=+0.29 H0=-0.02 tau=+0.09 ln10As=+0.09 n_s=+0.52 | 0.999 | 2.40 | 0.014 | 0.001 |

## z4 — H0

| variant | a | R² | r_dec | proj_deg | proj_brk |
|---|---|---:|---:|---:|---:|
| OLS (normalised) | omega_b=+0.11 omega_cdm=-0.26 H0=-0.40 tau=+1.05 ln10As=+0.56 n_s=+0.14 | 0.996 | 4.32 | 0.099 | -0.021 |
| post-lasso | omega_b=+0.10 omega_cdm=-0.15 H0=-0.48 tau=+0.35 n_s=+0.05 |  |  | n/a | n/a |
| (2ℓ+1)-weighted | omega_b=+0.04 omega_cdm=-0.13 H0=-0.49 tau=+1.25 ln10As=+0.78 n_s=+0.04 | 0.998 | 3.73 | 0.132 | -0.018 |
| templates h/2 | omega_b=+0.14 omega_cdm=-0.29 H0=-0.35 tau=+1.29 ln10As=+0.77 n_s=+0.19 | 0.993 | 3.91 | 0.131 | -0.021 |
| anchor point | omega_b=+0.06 omega_cdm=-0.09 H0=-0.61 tau=-0.22 ln10As=-0.47 n_s=-0.05 | 0.998 | 1.09 | -0.065 | -0.018 |

# Gate G4b (decoder bullet of G4)

| bullet | numbers | pass |
|---|---|---|
| amplitude-sector mass ≥ 0.8 | 0.64 | FAIL |
| \|r_dec + 2\| ≤ 0.3 | r_dec = 0.351 | FAIL |
| decomposition R²_W ≥ 0.8 | 1.000 | PASS |

**Gate G4b: FAIL**

_Mechanism: with cond = 70.2 the r_dec and amp-mass bullets test a within-pair split this run's spectra cannot express — the A_s e^{−2τ} degenerate direction is invisible to them, so the frozen rule is evaluated as registered but its FAIL here reflects template collinearity, not a wrong decoder direction. The identifiable decoder-side statement is proj_brk and the shape-sector coefficients above._

G4a (level-set bullet, Phase 7a): **FAIL** — the documented structured-residual E_inv verdict; see `levelset_audit_lcdm_tt_beta3e-4.md`.

---
_Generated by `scripts/decoder_effect.py`._
