# cmb-lcdm-sr — blind symbolic regression of β-VAE CMB amplitude latents

Can symbolic regression rediscover the textbook TT amplitude combination
**`ln(A_s·e^{−2τ})`** — the −2 reionization-suppression exponent — from a
trained β-VAE encoder alone, with **no hand-coded reference to the answer
anywhere in the pipeline**?

This repo is a distilled, standalone extraction of the *blind-SR* study from
the parent [`cmbvae`](../cmbvae) project (an independent reproducibility study
of [Piras, Herold, Lucie-Smith & Komatsu 2025, arXiv:2502.09810](https://arxiv.org/abs/2502.09810)).
It keeps exactly **one** search configuration — PySR with a **pure-Julia
GMM-MI inner loss**, selected post hoc by held-out GMM-MI — and ships the
stored trained models it targets. The alternative inner losses explored in the
parent study (mse / r2 / spearman / dcor / hsic / ksg) are deliberately not
included; see `docs/method.md` §"Why GMM-MI" for the ablation summary.

## The result being reproduced

Two regimes, one combination (5 PySR seeds each, 200 iterations, 5000 samples):

| Regime | Degeneracy | Latent | Top form (per seed) | val MI [nat] |
|---|---|---|---|---|
| **TT-only** (β=3e-4) | present | idx 2 | `A_s·(τ−0.598)` (5/5) | 0.822 |
| **TT+EE-lowl** | broken | z₅ | `A_s·(τ−0.579)` / `A_s·e⁻²ᵗ` | 1.196 |
| truth | — | — | `ln(A_s·e⁻²ᵗ)` | — |

PySR is fed only the **raw pair (A_s, τ)** and the encoder posterior mean of
the amplitude latent. The inner loss is a real MI estimator, invariant under
any bijection of either variable, so the search is rewarded for functional
form — never for matching the encoder's calibration. The −2 shows up in the
discovered forms themselves: the first-order Taylor direction `A_s·(τ−c)`
with c ≈ τ̄ + ½, and (TT+EE) the literal `A_s·e⁻²ᵗ`. Full protocol,
per-seed tables, and the negative control: [`docs/method.md`](docs/method.md).

## What's here

```
cmb-lcdm-sr/
├── models/                      stored trained models (from the parent project)
│   ├── lcdm_tt_beta3e-4/        PirasCVAE, L=5, β=3e-4, seed 42   → amplitude latent idx 2
│   │   ├── best_model.pt        model_cfg + weights
│   │   ├── scaler.npz           per-channel refs + normalisation stats
│   │   └── config_used.json     training config (records HPC shard paths)
│   └── lcdm_tt_ee_lowl/         DualEncoderCVAE, L=6, β=3e-4      → amplitude latent z5
├── data/
│   ├── theta.npy                (500000, 6) LHS ΛCDM samples
│   ├── splits_v1.npz            split_id ∈ {0,1,2} (400k/50k/50k train/val/test)
│   └── meta.json                prior_keys + prior ranges
├── src/cmb_lcdm_sr/
│   ├── sr.py                    ★ the Julia GMM-MI inner loss + input builder
│   ├── mi.py                    post-hoc GMM-MI selection metric (gmm-mi package)
│   ├── model.py                 PirasCVAE / DualEncoderCVAE (to load the checkpoints)
│   ├── scaler.py, dataset.py    stored normalisation stats + test-split streaming
│   └── encoder.py               encoder pass → encoder_means_test.npy
├── scripts/
│   ├── run_blind_sr.py          ★ one blind-SR run (one regime × one seed)
│   ├── run_shuffled_control.py  shuffled-target negative control
│   ├── encode_latents.py        cache test-split posterior means (needs shards)
│   ├── pool_sr_runs.py          cross-seed pooling by canonical form
│   └── consolidate_blind_sr.py  summary tables + textbook-form scan + summary.md
├── hpc/                         SLURM wrappers (CSD3/icelake, 16 CPU, JULIA_NUM_THREADS=16)
├── tests/                       pytest — model shapes, checkpoint loads, MI
└── docs/method.md               distilled protocol + results + controls
```

★ = the heart of the repo.

## Setup

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q          # sanity: models load, artifacts intact  (~30 s)
```

PySR bootstraps its own Julia environment on first use (one-off download,
several minutes). The SR runs are CPU-only; 16 threads recommended
(`JULIA_NUM_THREADS=16`).

## Running the study

**Step 0 — encoder means (one-off per model, needs the spectra shards).**
The SR target is the encoder posterior mean over the 50k-row test split,
cached at `models/<run>/analysis/encoder_means_test.npy`. This cache is not
checked in; regenerate it where the shards live (each shard dir is ~3.4 GB —
see *Data provenance* below):

```bash
# On CSD3 the shard paths recorded in config_used.json are valid as-is:
python scripts/encode_latents.py --run-dir models/lcdm_tt_beta3e-4
python scripts/encode_latents.py --run-dir models/lcdm_tt_ee_lowl

# Elsewhere, point at a synced copy of the shard dirs:
python scripts/encode_latents.py --run-dir models/lcdm_tt_beta3e-4 \
    --shards-root /path/to/cmbvae/data
```

**Step 1 — blind SR, 5 seeds per regime (~5 min/seed at 16 threads).**

```bash
# TT-only (degeneracy present) — amplitude latent idx 2
for N in 0 1 2 3 4; do
  python scripts/run_blind_sr.py --run-dir models/lcdm_tt_beta3e-4 \
      --latent-index 2 --inputs A_s tau --seed $N --turbo
done

# TT+EE-lowl (degeneracy broken) — amplitude latent z5
for N in 0 1 2 3 4; do
  python scripts/run_blind_sr.py --run-dir models/lcdm_tt_ee_lowl \
      --latent-index 5 --inputs A_s tau --seed $N --turbo
done
```

Each run writes `results/<run>/symbolic_regression_gmm_mi_seed<N>/` with
`report.json` (all Pareto equations + val MSE + val GMM-MI), `equations.csv`,
and `pareto.png`.

**Step 2 — negative control (shuffled target, identical PySR config).**

```bash
for S in 0 1 2; do
  python scripts/run_shuffled_control.py --run-dir models/lcdm_tt_beta3e-4 \
      --target-index 2 --shuffle-seed $S --pysr-seed $S --turbo
  python scripts/run_shuffled_control.py --run-dir models/lcdm_tt_ee_lowl \
      --target-index 5 --shuffle-seed $S --pysr-seed $S --turbo
done
```

**Step 3 — pool + consolidate.**

```bash
python scripts/pool_sr_runs.py \
    --glob 'results/lcdm_tt_beta3e-4/symbolic_regression_gmm_mi_seed*/report.json' \
    --out  results/lcdm_tt_beta3e-4/sr_pooled
python scripts/pool_sr_runs.py \
    --glob 'results/lcdm_tt_ee_lowl/symbolic_regression_gmm_mi_seed*/report.json' \
    --out  results/lcdm_tt_ee_lowl/sr_pooled
python scripts/consolidate_blind_sr.py     # tables + summary.md
```

**On CSD3**, the SLURM wrappers do step 0 automatically when needed:

```bash
for N in 0 1 2 3 4; do sbatch hpc/slurm_blind_sr.sh models/lcdm_tt_beta3e-4 2 "A_s tau" $N; done
for N in 0 1 2 3 4; do sbatch hpc/slurm_blind_sr.sh models/lcdm_tt_ee_lowl  5 "A_s tau" $N; done
sbatch hpc/slurm_shuffled_control.sh models/lcdm_tt_beta3e-4 2
sbatch hpc/slurm_shuffled_control.sh models/lcdm_tt_ee_lowl 5
```

## The GMM-MI inner loss in one paragraph

`src/cmb_lcdm_sr/sr.py::JULIA_LOSS_GMM_MI` is a custom PySR `loss_function`:
a pure-Julia 2-D GMM-MI estimator — fixed K=2 Gaussian mixture fit by EM (≤30
iterations, regularised covariances) on a strided 300-sample sub-batch, MI as
the Monte-Carlo average `⟨log p_xy − log p_x − log p_y⟩`, returned as
`exp(−MI)` so the loss is positive (PySR's HallOfFame takes `log(loss)`). An
earlier variant that called the Python `gmm-mi` estimator through PythonCall.jl
was ~80× slower (GIL-serialised threading + cross-language marshaling,
~7 h/seed extrapolated); the pure-Julia rewrite runs ~5 min/seed at 16
threads. Post-hoc selection uses the full Python `gmm-mi` estimator
(K-selection + bootstrap errors) on a held-out validation split — inner loss
and selection metric share one invariance class (bijections of either
variable), which is what makes the protocol blind.

## Data provenance

Copied from the parent `cmbvae` project (stored trained-model data):

* `models/*/` — trained checkpoints, normalisation scalers, training configs
  (runs `lcdm_tt_beta3e-4` and `lcdm_tt_ee_lowl`, both β=3e-4, seed 42).
* `data/theta.npy`, `data/splits_v1.npz`, `data/meta.json` — the LHS parameter
  table, train/val/test split, and priors for the 500k-spectra dataset.

Not copied (large; only needed to regenerate the encoder-means cache):

* Spectra shards — `shards_global_lhs/` (TT) and `shards_global_lhs_ee_lowl/`
  (EE), 100 × `spectra_*.npz` each, ~3.4 GB per channel. Canonical location:
  `/rds/user/zx332/hpc-work/cmbvae/data/` on CSD3. Note: the shard copies in
  the local `cmbvae/data/` sibling checkout are truncated (partial sync) and
  will fail to load — re-sync from CSD3 if you need a local encoder pass.

## Provenance / citation

Method and numbers distilled from the parent study's
`docs/extension/blind_sr_gmm_mi.md` (2026-06-25). The β-VAE architecture is a
paper-faithful PyTorch port of the TensorFlow CVAE of Piras et al. (2025),
arXiv:2502.09810; the GMM-MI selection metric is
[GMM-MI (Piras+2023)](https://github.com/dpiras/GMM-MI); symbolic regression is
[PySR](https://github.com/MilesCranmer/PySR) (study ran v1.5.10, Julia 1.11.9).
