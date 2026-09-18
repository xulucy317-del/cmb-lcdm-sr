# cmb-lcdm-sr — blind symbolic interpretation of CMB β-VAE latents

Can a blind search, starting from the six ΛCDM parameters alone, recover the
formula each latent of a CMB autoencoder computes — and can it prove the
formula is right?

Two β-VAE compressors of CMB power spectra (one sees temperature only, one
also sees low-ℓ polarization) are interrogated with symbolic regression whose
**inner loss and selection metric are both mutual-information estimators**.
MI is invariant under any invertible transform of either variable, so the
search is rewarded for finding the right *dependence* on the parameters and
never for matching the latent's units, scale or offset — and the textbook
answer `A_s·e^{−2τ}` is computed nowhere in the pipeline. Every pass/fail
rule was frozen before the results were seen, every instrument ships with a
null, and a pre-registered linear baseline was run afterwards to find out
what the search had actually added.

The project is complete (closed 2026-09-09). **The write-up of record is
[`report_conclusive.md`](report_conclusive.md)**; the same findings as an
interactive page are in [`docs/findings_atlas.html`](docs/findings_atlas.html)
(open it in a browser; text-only twin: [`docs/findings_atlas.md`](docs/findings_atlas.md)).

## Findings in brief

The study ran in four stages, each answering the question the previous one
raised.

1. **Discovery and validation (stage 1).** Every one of the 11 latents has a
   recurring symbolic coordinate. The −2 exponent of the degenerate
   combination `A_s·e^{−2τ}` is recovered blind, five independent ways
   (the discovered forms themselves; the derivative ratio over all top forms,
   −1.974 ± 0.018 TT / −1.993 ± 0.008 TT+EE; an answer-agnostic
   constant-ratio detector, −2.0000; an unplanned reappearance in another
   latent's residual; the weights of a plain linear fit). Adding
   polarization **splits** the amplitude information across two
   complementary latents rather than duplicating it. Under the frozen rules
   10/11 latents are "primarily interpreted"; EE z₀ is the one honest
   failure. The decoder side gives *no* reading of the −2: its (τ, ln A_s)
   templates are near-collinear, so that readout is unidentifiable.
2. **A pre-registered linear baseline (stage 2).** A seven-number linear fit
   matches or beats the discovered formulas for most latents, on
   reconstruction and on information alike — and the search never
   generated the linear candidate. Over this parameter box the latents are
   ~99.8 % weighted sums of the parameters, because in the log-spectrum
   basis the leading physics *is* additive. The stage-1 measurements stand;
   what they license changed (`report_conclusive.md` §3.5).
3. **Searching what the linear fit leaves (stage 3).** An exact quadratic
   closes most of the remainder for nine latents. On the two it cannot, the
   search earns its keep: a pole in τ (`A_s/τ`, the ratio governing the
   reionization bump) at EE z₄, and a rational curvature no polynomial
   expresses at EE z₀.
4. **Inside the encoder (stage 4).** Gradient attribution, a layer-wise
   probe and input optimisation show where the degeneracy-breaking
   information enters and where it is lost: EE z₄ alone reads the
   reionization window (ℓ < 30), and the temperature-only network discards
   the (A_s, τ) split at its final compression step, not earlier.

<p align="center">
  <img src="figures/amplitude_scatter.png" width="88%"
       alt="Amplitude latent of each network against ln(A_s e^-2tau): tight monotone curves">
</p>

*The amplitude latent of each network against `ln(A_s·e^{−2τ})`, computed
here only to draw the plot. The TT search returns the linearised form
`A_s·(τ − c)`; the TT+EE search returns the literal `A_s·e^{−2τ}`.*

<p align="center">
  <img src="figures/F12_1_affine_parity.png" width="92%"
       alt="Linear-baseline parity: reconstruction error and stored-information fraction per latent">
</p>

*Stage 2 in one figure. (a) Unexplained variance on the confirmation rows:
the seven-coefficient linear fit (black) against the best 40-node symbolic
formula (blue, range over five seeds). (b) The fraction of the information
each latent physically stores that is carried by the first formula, by the
two-formula account, and by the linear fit.*

## What is in the repository

```
cmb-lcdm-sr/
├── report_conclusive.md   ★ the write-up of record (all four stages, glossary, artifact map)
├── src/cmb_lcdm_sr/       the library: models, encoder pass, GMM-MI inner loss, tiers, semantics
├── scripts/               every runner, audit and consolidator, one CLI each   → scripts/README.md
├── hpc/                   SLURM launchers (CSD3) and scheduler-free resume kits → hpc/README.md
├── experiments/           consolidated, committed results of every campaign   → experiments/README.md
├── figures/               the report figures and the script that makes each   → figures/README.md
├── docs/                  method, pre-registered roadmap, evidence record, …  → docs/README.md
├── data/                  parameter table, splits, priors, sham inputs, templates → data/README.md
├── models/                the two stored β-VAE checkpoints                     → models/README.md
├── results/               raw run outputs (git-ignored)                       → results/README.md
└── tests/                 pytest suite (347 tests)
```

Each directory README indexes its contents by pipeline stage. The
consolidated results in `experiments/` are what every number in the reports
traces to; the raw fronts of the ~5,100 PySR searches behind them are not
committed.

**Naming.** The two checkpoints are referred to by their run names
throughout the artifacts: `lcdm_tt_beta3e-4` is the temperature-only network
("TT", 5 latents) and `lcdm_tt_ee_lowl` is the temperature + low-ℓ
polarization network ("EE" or "TT+EE-lowl", 6 latents). Latents are `z0…z4`
/ `z0…z5`. Per-checkpoint files carry the run name as a suffix
(`experiments/<experiment>_<run>.{md,json}`).

## Installation

```bash
git clone https://github.com/xulucy317-del/cmb-lcdm-sr.git && cd cmb-lcdm-sr
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt        # or: pip install -e .[dev]
pytest -q                              # ~8 min; needs nothing beyond the repo
python scripts/check_inputs.py         # what this checkout can run, and what it is missing
```

The scripts run from the repository root without installing the package
(`scripts/_bootstrap.py` puts `src/` on the path). PySR downloads its own
Julia on first import (one-off, several minutes). All searches are CPU-only;
the study ran with PySR 1.5.10 / Julia 1.11.9 and 16 Julia threads
(`JULIA_NUM_THREADS=16`). `torch` is needed only for the encoder pass, the decoder-effect
stage and the stage-4 attribution scripts.

## Data and models

A clone holds the code, both checkpoints, the parameter table and every
consolidated result. What it can *run* depends on three groups of inputs
that are too large or too derived for git. `python scripts/check_inputs.py`
prints exactly this table for your checkout, verifies every file that has a
canonical sha256, and names what each missing group blocks.

| to run … | you need | in a clone? |
|---|---|---|
| the tests; every figure built from `experiments/*.json` | nothing beyond the clone | yes |
| **any SR search or audit** — stages 1–3, the MSE and precision campaigns, the four figure scripts marked † in `figures/README.md` | the caches under `models/<run>/analysis/`: the encoder posterior means and log-variances over the 50,000 test rows (4 files, ≈4 MB), which every search targets, and the per-latent residual caches the later phases start from (≈11 MB) | see below |
| the encoder pass, the spectral templates, stage 4 (encoder attribution) | the 500,000 CLASS spectra: `shards_global_lhs/` and `shards_global_lhs_ee_lowl/`, 100 `spectra_*.npz` each, ≈3.4 GB per channel | no |
| re-consolidating a published campaign without re-running its searches | the raw fronts, `results/<run>/<campaign>/…/report.json` (≈5,100 searches) | no |

**Encoder caches.** They are the pipeline's entry point, and the repository
is set up to carry them together with the per-latent residual caches next
to them (`residual_z<k>`, `f1hat_z<k>`: 22 files that phases 5–8 and stage 2
start from and that can only be rebuilt from the raw fronts; plus the
stage-3 `residual_ols_z<k>` targets where that search ran). `.gitignore`
admits exactly those files (≈15 MB); the canonical sha256 are pinned in
`experiments/mse_one_stage_state_csd3.json`.
The item-by-item status of what is still to be added is
[`docs/inputs_checklist.md`](docs/inputs_checklist.md). Until the encoder
caches are committed, regenerate them from the shards:

```bash
python scripts/encode_latents.py --run-dir models/lcdm_tt_beta3e-4 --shards-root /path/to/shards
python scripts/encode_latents.py --run-dir models/lcdm_tt_ee_lowl  --shards-root /path/to/shards
python scripts/check_inputs.py --shards-root /path/to/shards
```

A cache regenerated on different hardware agrees with the canonical one to
float32 precision but is not byte-identical; `check_inputs.py` says which
you have.

**Shards and raw fronts.** Both are read-only inputs of the published
numbers: the shards feed one encoder pass, one template fit and the stage-4
scripts; the fronts are what the `consolidate_*` scripts turn into
`experiments/`. `data/inputs_manifest.json`, once written with
`scripts/check_inputs.py --write-manifest` on a machine holding everything,
records their sha256 so an archive obtained from anywhere can be verified
(`data/README.md` gives the maintainers' procedure). The checkpoints were
trained in a separate reproduction of Piras, Herold, Lucie-Smith & Komatsu
(2025); `config_used.json` records that training run verbatim, including its
cluster paths.

## Running the pipeline

The unit of work everywhere is one `scripts/run_blind_sr.py` invocation: one
target × one input set × one PySR seed, writing `report.json` (the whole
Pareto front with per-equation held-out scores), `equations.csv` and
`pareto.png` under `results/<run>/…`. Every campaign is a matrix of such
runs plus a `consolidate_*` step that writes the committed
`experiments/*.{md,json}`.

The smallest end-to-end example is the two-input amplitude study (about
5 min per seed at 16 threads), once the encoder caches exist:

```bash
# blind SR on the amplitude latent with only (A_s, tau) exposed, 5 seeds per network
for N in 0 1 2 3 4; do
  python scripts/run_blind_sr.py --run-dir models/lcdm_tt_beta3e-4 --latent-index 2 --inputs A_s tau --seed $N --turbo
  python scripts/run_blind_sr.py --run-dir models/lcdm_tt_ee_lowl  --latent-index 5 --inputs A_s tau --seed $N --turbo
done
# the negative control: same search against a row-shuffled latent
python scripts/run_shuffled_control.py --run-dir models/lcdm_tt_beta3e-4 --target-index 2 --shuffle-seed 0 --pysr-seed 0 --turbo
# pool the seeds by canonical form and write the summary tables
python scripts/pool_sr_runs.py --glob 'results/lcdm_tt_beta3e-4/symbolic_regression_gmm_mi_seed*/report.json' \
                               --out results/lcdm_tt_beta3e-4/sr_pooled
python scripts/consolidate_blind_sr.py
```

The full programme — six-input search on every latent, the hyperparameter
sweep, the ten-phase validation roadmap, the MSE and precision campaigns,
the linear-baseline audit, the residual ladder and the encoder attribution —
is laid out stage by stage in [`scripts/README.md`](scripts/README.md)
(which script, which inputs, which `experiments/` file it writes) and
[`hpc/README.md`](hpc/README.md) (the launchers that ran it). The reproduction
table in `report_conclusive.md` §9 maps every stage to its scripts and
artifacts.

**On your own cluster.** The launchers ran on CSD3 and are kept as they ran;
`hpc/submit.sh` submits any of them on another SLURM cluster with your site's
account, partition and paths from `hpc/site.env`, and `hpc/run_tasks.sh`
runs any launcher's task matrix under PBS/LSF/SGE or with no scheduler at
all. See [`hpc/README.md`](hpc/README.md), "Running them somewhere other
than CSD3".

**The GMM-MI inner loss** (`src/cmb_lcdm_sr/sr.py::JULIA_LOSS_GMM_MI`) is a
custom PySR `loss_function`: a pure-Julia two-dimensional Gaussian-mixture MI
estimator (fixed K = 2, EM with regularised covariances, a strided 300-row
sub-batch), returned as `exp(−MI)` so the loss is positive. Post-hoc
selection re-scores every front expression with the full Python `gmm-mi`
estimator on held-out rows. Inner loss and selection metric share one
invariance class, which is what makes the protocol blind. An earlier variant
that called the Python estimator through PythonCall.jl was ~80× slower.

**Data hygiene.** The 50,000 test rows are cut into three tiers that never
mix (`src/cmb_lcdm_sr/tiers.py`): T0 = rows 0–4,999, the only rows any
search sees (4,000 fit / 1,000 validation); T1 = rows 5,000–24,999 for every
calibration, audit and anchor set; T2 = rows 25,000–49,999, opened once for
the reported numbers.

## Documentation map

| read this | for |
|---|---|
| [`report_conclusive.md`](report_conclusive.md) | the whole story, written for a reader who has not followed the project |
| [`docs/findings_atlas.html`](docs/findings_atlas.html) | the same findings as an interactive page |
| [`docs/method.md`](docs/method.md) | the stage-1 methodology and its numbers, compactly |
| [`docs/discovery_roadmap.md`](docs/discovery_roadmap.md) | the pre-registered validation programme: frozen thresholds, gates, closure, deviations |
| [`docs/results_compendium.md`](docs/results_compendium.md) | every stage-1 number, traced to its `experiments/` file |
| [`docs/evidence_record.md`](docs/evidence_record.md) | the stage 2–4 evidence record: what each claim rests on after the linear-baseline audit |
| [`docs/README.md`](docs/README.md) | the full index, including the superseded drafts kept under `docs/archive/` |

## Citation and acknowledgements

If you use this code or these results, cite the repository (see
[`CITATION.cff`](CITATION.cff)). The β-VAE architecture is a PyTorch port of
the CVAE of [Piras, Herold, Lucie-Smith & Komatsu (2025), arXiv:2502.09810](https://arxiv.org/abs/2502.09810);
the selection metric is [GMM-MI (Piras et al. 2023)](https://github.com/dpiras/GMM-MI);
symbolic regression is [PySR](https://github.com/MilesCranmer/PySR). The
searches ran on the Cambridge CSD3 cluster, a Lightning AI CPU Studio and a
Mac. Code is released under the [MIT License](LICENSE).
