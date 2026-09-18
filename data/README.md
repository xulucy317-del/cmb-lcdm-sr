# data/ — inputs shared by every stage

| file | contents |
|---|---|
| `theta.npy` | `(500000, 6)` float64: the Latin-hypercube parameter table the spectra were computed from, columns in the order of `meta.json` — `omega_b`, `omega_cdm`, `H0`, `tau_reio`, `ln10^{10}A_s`, `n_s`. Note the amplitude is *sampled* as ln 10¹⁰A_s; the search scripts hand it to PySR in linear scale (`A_s = 10⁻¹⁰ eˣ`), an order-preserving transform of one input, and the linear fits use the sampled form |
| `splits_v1.npz` | `split_id` ∈ {0, 1, 2} per row — 400,000 train / 50,000 validation / 50,000 test (split seed 123; the LHS itself and the training runs use seed 42). Only the test rows are used here; `src/cmb_lcdm_sr/tiers.py` cuts them into T0 (search), T1 (calibration) and T2 (confirmation) |
| `meta.json` | the prior box: parameter names and ranges (ω_b 0.020–0.024, ω_cdm 0.100–0.130, H₀ 62–80, τ 0.01–0.13, ln 10¹⁰A_s 2.90–3.18, n_s 0.92–1.01) |
| `sham_v1_{ob,tau,ns}.npy`, `sham_v1.json` | the sham-input columns of the R-P4 dilution control: each is a row permutation of one real parameter column over the 50,000 test rows, so it has a genuine parameter's marginal and provably zero information about any latent (`scripts/build_sham_inputs.py`; the JSON records donor column, seed and the fraction of rows moved) |
| `spectral_templates_v1.npz` | the data-driven parameter templates t_j(ℓ) = ∂log₁₀D_ℓ/∂u_j per channel, estimated by locally weighted quadratic regression over a train-split subsample, with a half-bandwidth set for the sensitivity check (`scripts/spectral_templates.py`; used by the decoder-effect stage) |

Not here: the 500,000 CLASS spectra themselves (`shards_global_lhs/` for TT
and `shards_global_lhs_ee_lowl/` for EE, 100 `spectra_*.npz` shards each,
~3.4 GB per channel). They are needed only for the one-off encoder pass
(`scripts/encode_latents.py`) that produces the encoder caches under
`models/<run>/analysis/`, and for regenerating the spectral templates.
