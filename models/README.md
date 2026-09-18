# models/ — the two stored β-VAE checkpoints

Both were trained on the same 500,000 CLASS spectra (log₁₀ D_ℓ relative to
a reference spectrum, standardised per multipole) with the β-VAE objective at
β = 3 × 10⁻⁴, training seed 42, 750 epochs, batch 1024, learning rate 10⁻³,
in a separate reproduction of Piras, Herold, Lucie-Smith & Komatsu (2025).
`src/cmb_lcdm_sr/model.py` holds the PyTorch architectures needed to load
them.

| run directory | network | sees | latents |
|---|---|---|---|
| `lcdm_tt_beta3e-4/` | `PirasCVAE` — one convolutional encoder | TT, ℓ ∈ [30, 2500], 2471 bins | 5 (`z0…z4`; amplitude latent z₂) |
| `lcdm_tt_ee_lowl/` | `DualEncoderCVAE` — two encoders | TT (2471 bins) + EE with the low-ℓ reionization bump, ℓ ∈ [2, 2500] (2499 bins) | 6 (`z0…z5`; amplitude latents z₄ and z₅) |

Each directory holds:

| file | contents |
|---|---|
| `best_model.pt` | `model_cfg` + state dict (`cmb_lcdm_sr.encoder.load_checkpoint`) |
| `scaler.npz` | per-channel reference spectrum and per-multipole mean/σ of the standardised log-ratio (`cmb_lcdm_sr.scaler.ShardedScaler`) |
| `config_used.json` | the training configuration as recorded by the training run, verbatim — including the cluster paths of its data and outputs, which are provenance, not paths this repository reads |
| `analysis/` | the caches every later stage starts from — committed (29 files, ≈15 MB, byte-identical to the copies every reported number came from): `encoder_means_test.npy` and `encoder_logvars_test.npy` `(50000, L)` from the encoder pass, then the per-latent residual caches (`residual_z<k>_v1.npy`, `f1hat_z<k>_v1.npy`, `residual_ols_z<k>_v1.npy`) the stage-1 and stage-3 scripts add |

The encoder caches are the target every search and audit starts from and
are regenerated with `scripts/encode_latents.py --run-dir models/<run>
--shards-root <dir>` where the spectra shards live; the sha256 of the
canonical means used for every reported number is pinned in
`experiments/mse_one_stage_state_csd3.json`.
