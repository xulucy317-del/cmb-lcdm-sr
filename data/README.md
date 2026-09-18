# data/ — inputs shared by every stage

| file | contents |
|---|---|
| `theta.npy` | `(500000, 6)` float64: the Latin-hypercube parameter table the spectra were computed from, columns in the order of `meta.json` — `omega_b`, `omega_cdm`, `H0`, `tau_reio`, `ln10^{10}A_s`, `n_s`. Note the amplitude is *sampled* as ln 10¹⁰A_s; the search scripts hand it to PySR in linear scale (`A_s = 10⁻¹⁰ eˣ`), an order-preserving transform of one input, and the linear fits use the sampled form |
| `splits_v1.npz` | `split_id` ∈ {0, 1, 2} per row — 400,000 train / 50,000 validation / 50,000 test (split seed 123; the LHS itself and the training runs use seed 42). Only the test rows are used here; `src/cmb_lcdm_sr/tiers.py` cuts them into T0 (search), T1 (calibration) and T2 (confirmation) |
| `meta.json` | the prior box: parameter names and ranges (ω_b 0.020–0.024, ω_cdm 0.100–0.130, H₀ 62–80, τ 0.01–0.13, ln 10¹⁰A_s 2.90–3.18, n_s 0.92–1.01) |
| `sham_v1_{ob,tau,ns}.npy`, `sham_v1.json` | the sham-input columns of the R-P4 dilution control: each is a row permutation of one real parameter column over the 50,000 test rows, so it has a genuine parameter's marginal and provably zero information about any latent (`scripts/build_sham_inputs.py`; the JSON records donor column, seed and the fraction of rows moved) |
| `inputs_manifest.json` | the sha256 contract for every input the pipeline reads beyond the committed code — the encoder and residual caches, each of the 200 spectra shards, and one aggregate per campaign of raw fronts (35 campaigns, 5,836 `report.json`). Written on CSD3 on 2026-09-18 with `scripts/check_inputs.py --write-manifest`; a clone verifies whatever it has obtained against it (`scripts/check_inputs.py`) |
| `spectral_templates_v1.npz` | the data-driven parameter templates t_j(ℓ) = ∂log₁₀D_ℓ/∂u_j per channel, estimated by locally weighted quadratic regression over a train-split subsample, with a half-bandwidth set for the sensitivity check (`scripts/spectral_templates.py`; used by the decoder-effect stage) |

Not here, and not published: the 500,000 CLASS spectra themselves
(`shards_global_lhs/` for TT and `shards_global_lhs_ee_lowl/` for EE, 100
`spectra_*.npz` shards each, ≈4.5 GB per channel, 9.0 GB in all). They are
needed only for the one-off encoder pass
(`scripts/encode_latents.py`) that produces the encoder caches under
`models/<run>/analysis/`, and for regenerating the spectral templates.

## Publishing the inputs that are not in git (maintainers)

Three groups of files complete a clone; the order below goes from the one
that unlocks most to the one that unlocks least.

1. **The caches under `models/<run>/analysis/`** (≈15 MB: the four encoder
   caches, the 22 per-latent residual caches, which can only be rebuilt
   from the raw fronts, and the stage-3 OLS-residual targets that exist) —
   commit them. On the machine that holds the canonical copies:

   ```bash
   python scripts/check_inputs.py            # "canonical" for both encoder_means_test.npy, 22/22 residual caches present
   git add models/lcdm_tt_beta3e-4/analysis/ models/lcdm_tt_ee_lowl/analysis/
   git status --short models/                # the 26 caches plus the residual_ols files, nothing else
   git commit -m "Ship the canonical encoder and residual caches"
   ```

   `.gitignore` admits exactly these files under `models/*/analysis/`. With
   them in the repository every search, audit and campaign of stages 1–3
   runs from a plain clone.

2. **The manifest** — on the same machine, with the spectra shards and the
   raw `results/` tree present:

   ```bash
   python scripts/check_inputs.py --write-manifest --shards-root /path/to/shards
   git add data/inputs_manifest.json && git commit -m "Record the inputs manifest"
   ```

   This hashes every shard (9 GB, a few minutes) and every campaign's
   `report.json` files, so that archives obtained from anywhere can be
   verified with `scripts/check_inputs.py --full`.

3. **The raw fronts** — distributed as a release asset, not in git
   (done 2026-09-18: release `v1.0.0`, `cmb-lcdm-sr-results.tar.gz`, 13 MB):

   ```bash
   tar --exclude='*.png' --exclude='pysr_state' -czf cmb-lcdm-sr-results.tar.gz results/
   ```

   attached to a GitHub release. A user downloads it from
   <https://github.com/xulucy317-del/cmb-lcdm-sr/releases/download/v1.0.0/cmb-lcdm-sr-results.tar.gz>, extracts it at the repository root and runs
   `python scripts/check_inputs.py --full`.

4. **The spectra shards are not published** (decision of 2026-09-18): they
   are the parent project's training set. The manifest still pins every
   shard's sha256, so a holder of a copy can verify it with
   `python scripts/check_inputs.py --shards-root <dir> --full`; without one,
   the encoder pass, the template fit and the stage-4 attribution cannot be
   re-run, but all three outputs are committed.
