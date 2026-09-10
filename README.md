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

On top of the reference study the repo now carries two fully-blind
extensions — the **all-params experiment** (all 6 parameters → every latent)
and an automated **PySR hyperparameter sweep** — plus their consolidated
results; see *Where the project stands* below.

## Status: closed (2026-09-09) — start here

The project ran to completion in **four stages**, and the discovery search
described below is only the first of them. Two documents are the write-ups
of record; read one of these before anything else in this repo:

* [**`report_conclusive.md`**](report_conclusive.md) — the full report,
  written for a reader who has not followed the project. All four stages,
  every number traced to an artifact, glossary and reproduction table.
* [**`docs/findings_atlas.html`**](docs/findings_atlas.html) — the same
  findings as an interactive page (open it in a browser); the text-only
  companion is [`docs/findings_atlas.md`](docs/findings_atlas.md).

The four stages in one line each:

1. **Discovery search** — a recurring formula per latent, the −2 exponent
   found five ways, polarization shown to *split* amplitude information
   rather than duplicate it. 10/11 latents reach "primarily interpreted".
   *This is the stage documented in the rest of this README.*
2. **A pre-registered linear baseline** — a plain seven-number linear fit
   matches or beats the discovered formulas on most latents, on
   reconstruction and on information alike; the search never generated the
   linear candidate.
3. **Searching the linear residual** — an exact quadratic closes most of the
   remainder for nine latents; on the other two the search finds a pole in
   τ and a rational curvature no polynomial expresses.
4. **Inside the encoder** — gradient attribution, a trunk probe, and input
   optimisation, as a check on stages 1–3 from the network side.

`report.md` is the stage-1-only draft and is **superseded** by
`report_conclusive.md`. `paper/main.tex` is an earlier partial draft on the
same material.

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

## Where the project stands — stage 1 (2026-08-09)

*Everything from here on describes the discovery search (stage 1) and
the roadmap that executed it. Stages 2–4 ran afterwards and are covered
only in `report_conclusive.md` and the findings atlas.*

Six layers, protocol-identical throughout (gmm_mi pure-Julia inner loss,
5000 samples, post-hoc held-out GMM-MI ranking), each consolidated into
`experiments/`. **The complete numeric digest of every result — written as
raw material for the official write-up — is
[`docs/results_compendium.md`](docs/results_compendium.md).**

**1. Reference study — reproduced.** Inputs `(A_s, τ)` only, amplitude latent
only (table above): `A_s·(τ−c)` in every seed, literal `A_s·e⁻²ᵗ` in the
degeneracy-broken regime. See [`docs/method.md`](docs/method.md).

**2. All-params blind SR — done.** All 6 raw parameters in, **every** latent
targeted — no input or latent pre-selection left (5 seeds × 5+6 latents;
`experiments/allparams_blind_sr_*.md`). Every latent is a multi-parameter
composite: top forms use ≥5 of the 6 parameters, cross-seed top MI spans
2.3–3.8 nat (TT) / 1.8–3.8 nat (TT+EE) — far above the 2-input ceilings
(0.822 / 1.196 nat), because with all inputs exposed nothing is marginalised
out and the deterministic encoder map keeps yielding MI. The −2 reionization
exponent survives full blindness, read via the derivative ratio
r = (∂f/∂τ)/(∂f/∂ln A_s): **−1.974 ± 0.018** (TT) / **−1.993 ± 0.008**
(TT+EE) over all top forms. Shuffled-target controls stay null (≤ 0.06 nat,
no textbook structure on any control front).

**3. Hyperparameter sweep (`hp_v1`) — done.** Star design around the protocol
baseline, 12 configs × 3 seeds per model on the amplitude latents
(`experiments/hpsweep_hp_v1_*.md`). Findings:

* **Top val MI is a capacity dial, not a discovery meter**: maxsize alone
  swings it 1.6 → 4.05 nat; every capacity knob raises it; the winning forms
  are complexity-20 composites that differ structurally seed to seed.
* **The budget-matched readout MI@c≤10 is flat across every knob**
  (~1.89 TT / ~2.02 EE): the leading-order discovery is already saturated at
  the protocol settings — no tuning gain exists on the aim-aligned metric.
* **The physics is hyperparameter-robust**: r ≈ −1.97…−2.00 in every config,
  textbook building blocks on the fronts throughout.
* **Search big, then slice**: the maxsize-10 search's own front is *worse* at
  c≤10 than the sliced maxsize-20 front (1.60 vs 1.89 / 1.69 vs 2.02) —
  parsimony is a report-time slice, not a search-time budget cut.
* **Cost**: `ncycles_per_iteration 190` matches baseline quality at ~60%
  runtime; `population_size 108` is past diminishing returns (~4× cost).

**4. Discovery study (roadmap phases 0–8) — done.** The executable programme
in [`docs/discovery_roadmap.md`](docs/discovery_roadmap.md): every
instrument frozen (§0.3) and validated on the amplitude sector before any
shape-latent unblinding (gates G1–G4 in the experiment mds):

* **Phases 1–3** — plateau/knee readout, semantic clustering (one dominant
  cluster per latent, R_SR ≥ 0.8, 9/11 at 1.0), calibrated sufficiency:
  η_S ≈ 1.0 for all 11 latents; every stage-1 residual *structured*
  (R²_res 0.98–0.99) — the honest verdict gate G1 requires.
* **Phase 4** — the blind 63-subset screen closes the last human choice:
  S\* per latent at full protocol, no hand-picked inputs anywhere.
* **Phase 5** — the intrinsic ceiling I(Z_k;θ) from the stochastic latent;
  η̂_post = MI(Z;f)/MI(Z;μ) (registered refinement) is the demotion metric;
  canonical forms store 0.29–0.84 of what each latent knows.
* **Phase 6** — residual SR gives every latent a recurrent second
  coordinate f₂ (R_SR 0.80, shuffled-residual nulls ≤ 0.07 nat vs 0.4–1.8
  real); the combined h(f₁)+g(f₂) reaches R²(μ) 0.955–0.998 and lifts
  η̂_post to 0.59–0.96. Amplitude DoD MET on EE (f₂ pure shape-sector),
  NOT MET on TT — substantively: the TT knee forms are A_s·(τ−c) × shape,
  and an additive hierarchy cannot absorb the multiplicative interaction
  (deviation D-DoD-z2 on the card).
* **Phase 7** — level sets: f₁-only E_inv fails exactly as the structured
  residual predicts (E_inv ∈ [1−R², 2(1−R²)] for all 11 latents); joint
  (f₁,f₂) level sets restore invariance — 7/8 auditable latents pass, EE
  amplitude 0.226 → 0.029, **gate G4a-joint PASS**. Decoder: d_k(ℓ) ≈
  Σ a_j t_j at R²_W ≈ 1.0, cos(a\*, g_j) 0.77–1.00; the EE reionization
  bump identifies the amplitude pair and returns **r_dec = −1.87** — a
  third, observable-domain readout of the −2 (TT's ℓ≥30 pair is collinear:
  G4b FAIL by mechanism, documented).
* **Phase 8** — sparse probes + slab-conditional MI: every canonical
  coordinate is linearly decodable from its own latent (rank-normal
  R² 0.88–0.95) with the remainder genuinely distributed; **no redundant
  latent pair exists in either model** (all top-2 conditionals are
  synergistic). The EE amplitude sector is *split*, not duplicated: z4's
  τ-direction is carried by z4 essentially alone (A\* = {z2, z4}), and
  knowing z5 raises z1's information about `A_s·e⁻²ᵗ` from 0.013 to
  0.473 nat.

**5. Latent cards (phase 10) — the deliverable.**
`experiments/latent_cards_<run>.{md,json}`: one card per latent (canonical
cluster, S\*, η_S/η_plat/η_post, knee, R_SR, signature + constant-ratio
pairs, residual audits, E_inv, decoder decomposition, subspace probe,
status, deviations), plus a gates table, controls appendix, and deviation
register. Under the frozen predicates: **10/11 latents are "primarily
interpreted"** — a validated 1-D primary coordinate plus a documented
structured residual with a discovered f₂ — and **EE z0 is "unresolved"**
(weakest stage-2 account, R² 0.41; joint E_inv 0.060 > 0.05, inside its
expected band). No latent reaches full "interpreted": the stage-2
residuals remain structured — the encoder hierarchy does not terminate at
two symbolic levels.

**6. Interaction-aware stage 2 (post-closure follow-up, 2026-08-09) —
done.** The roadmap Closure's open-item 3: the Phase-6 residual SR rerun
with the stage-1 prediction f1hat = h(f₁) exposed as a 7th input, so the
search can express amplitude × shape interactions (55 protocol runs + 6
controls, ≈ 98 core-h; `experiments/residual_sr_ia_*.md`,
`levelset_audit_joint_ia_*.md`). Outcomes: **D-DoD-z2 sharpened** — TT
z2's recurrent knee coordinate keeps τ even with the interaction channel
available (same form as additive, f1hat unused): the τ-coupling is
genuine structure, not an ansatz artifact. **The additive account is
confirmed** where it was good (8/11 latents return the same canonical f₂;
EE amplitude DoD still MET; EE z1's residual again literally
`A_s·e⁻²ᵗ/ω_b²`, ratio −2.0000). **Interactions surface where real**: TT
z4's cluster carries f1hat forms (residual MI 2.40 vs 2.16; η̂_comb
0.758 → 0.787), TT z3 reaches R_SR 1.00, and EE z0's f₂ upgrades to the
unanimous interaction form `−A_s·H0²·(f1hat − c)` (R_SR 1.00, MI
0.40 → 0.50) — though its joint E_inv stays at 0.062 (band
[0.046, 0.093]), so the card remains unresolved. **No card status
changes**; controls null (≤ 0.053 nat); stage-2 residuals still fail the
frozen audit for all 11 — the non-terminating hierarchy is robust to the
enriched ansatz.

## Remaining gaps

1. **R_model (roadmap Phase 9).** Search-stability (5 PySR seeds) is
   established; architecture-stability needs 3 retrained VAE seeds per
   regime (parent `cmbvae` repo, GPU) plus the alignment/rerun machinery.
   The roadmap was **closed 2026-08-09 without this phase** (Closure
   section of `docs/discovery_roadmap.md`): every card claim is
   per-checkpoint, and Phase 9 remains executable later without touching
   the frozen thresholds or any existing card number.
2. **The hierarchy does not terminate.** Stage-2 residuals still fail the
   frozen audit for all 11 latents — confirmed robust to the
   interaction-aware ansatz (layer 6); a third stage is possible but the
   returns are shrinking (combined R²(μ) already 0.954–0.998). Recorded on
   the cards rather than pursued.
3. **EE z0.** Still the one unresolved card, now with the blocker
   localised (layer 6): even the unanimous interaction-form f₂ leaves
   joint E_inv at 0.062 vs the 0.05 rule, because the stage-2 residual
   (R² 0.39) holds more than one coordinate's worth of structure. A
   3-coordinate account is the concrete next experiment if this latent
   matters downstream.

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
│   ├── run_blind_sr.py          ★ one blind-SR run (one config × latent × seed)
│   ├── run_shuffled_control.py  shuffled-target negative control
│   ├── encode_latents.py        cache test-split posterior means (needs shards)
│   ├── pool_sr_runs.py          cross-seed pooling by canonical form
│   ├── consolidate_blind_sr.py  reference-study summary (tables + textbook scan)
│   ├── consolidate_allparams.py all-params summary (per-latent tables, r-ratio, control)
│   ├── sweep_blind_sr.py        hyperparameter-sweep planner/status (spec → manifest → sbatch)
│   └── consolidate_hp_sweep.py  sweep comparison (top MI / MI@c≤10 / one-factor effects)
├── hpc/                         SLURM wrappers (CSD3/icelake, 16 CPU); sweeps/ = sweep specs
├── experiments/                 consolidated deliverables (one .md + .json per experiment)
├── tests/                       pytest — model shapes, checkpoint loads, MI, sweep planner
├── report_conclusive.md         ★ the write-up of record — all four stages
├── report.md                    stage-1-only draft, superseded
├── paper/                       earlier partial LaTeX draft + figure scripts
└── docs/
    ├── findings_atlas.html      ★ interactive closing report (+ .md companion)
    ├── method.md                distilled protocol + results + controls
    ├── results_compendium.md    every stage-1 result in one digest
    ├── discovery_roadmap.md     the executed phase programme + Closure
    └── ols_mi_sr_mse_sr_t2_comparison_claude_output.md
                                 the stage-2/3 evidence record
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

## Hyperparameter sweeps (all-params blind SR)

On top of the all-params experiment (`hpc/slurm_allparams_sr.sh`, all 6 raw
parameters → every latent) there is an automated PySR hyperparameter-tuning
pipeline. A sweep spec (`hpc/sweeps/*.json`) declares the protocol baseline
(`niterations 200, populations 15, maxsize 20`) plus axes of alternatives —
either the dedicated flags or any other `PySRRegressor` kwarg
(`population_size`, `ncycles_per_iteration`, `parsimony`, …), routed through
`run_blind_sr.py --pysr-extra`. `mode: "star"` varies one factor at a time
around the baseline (cheap, directly interpretable); `mode: "grid"` takes the
full cartesian product.

```bash
# 1. expand the spec → results/<run>/hpsweep_<name>/{manifest.json,tasks.tsv},
#    printed per-config runtime estimates + the sbatch line
python scripts/sweep_blind_sr.py plan --spec hpc/sweeps/allparams_hp_v1_tt.json

# 2. submit: one array task = one (config × latent × seed) run, skip-if-done
sbatch --array=0-35%16 hpc/slurm_hpsweep_sr.sh results/lcdm_tt_beta3e-4/hpsweep_hp_v1

# 3. progress + resubmit line for any missing runs (idempotent)
python scripts/sweep_blind_sr.py status --spec hpc/sweeps/allparams_hp_v1_tt.json

# 4. comparison tables → experiments/hpsweep_hp_v1_lcdm_tt_beta3e-4.{md,json}
python scripts/consolidate_hp_sweep.py --sweep-dir results/lcdm_tt_beta3e-4/hpsweep_hp_v1
```

The same sweep for the TT+EE-lowl model (amplitude latent z5) is
`hpc/sweeps/allparams_hp_v1_ee.json` → `results/lcdm_tt_ee_lowl/hpsweep_hp_v1`.

The consolidated summary reports, per config (cross-seed mean ± std): the
headline **top val MI** (which grows with any capacity knob — it measures
search power), the budget-matched **MI @ complexity ≤ 10** (comparable across
different `maxsize`), the parsimonious-form complexity, fit seconds, and — for
the amplitude latent — the implied τ exponent r(top) (textbook −2) and the
textbook-form scan. Star-mode sweeps get a one-factor-effect table per axis.
The default specs (`allparams_hp_v1_{tt,ee}`) tune the amplitude latent of
each model (z2 / z5): 12 configs × 3 seeds ≈ 77 core-hours per model.

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
