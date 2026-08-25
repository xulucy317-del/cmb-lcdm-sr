# One-stage latent-reconstruction SR with MSE — experiment plan

**Status:** paused for Lightning AI handoff on 2026-08-25; no CSD3 job queued

**Date:** 2026-08-24

**Execution amendment A1 — remove non-selecting T0 MI diagnostics (2026-08-25):**
After 36 main MSE reports completed, and before creating any selection
manifest or opening T1/T2 in this experiment, full post-hoc GMM-MI was
removed from the MSE-front and shuffled-control task critical path. It
cannot affect MSE search, validation-MSE selection, expressions, or any
decision rule. The first 36 reports retain their historical MI fields;
subsequent MSE reports store explicit null MI fields plus skip metadata.
At A1, full GMM-MI remained enabled for MI-selected legacy fronts and the
confirmatory known-`f2` and full-residual audits; A2 below narrows that scope.

**Execution amendment A2 — remove optional MI audits and hand off
(2026-08-25):** Before any selection manifest, T1 calibration, or T2
confirmation was created, remove all newly computed reconstruction MI and the
optional H4 full direct-residual audit. Confirmation no longer computes
GMM-MI between predictions and targets for direct, one-SE, or hierarchy
methods; it also no longer runs the HistGradientBoosting/maximum-parameter-MI
termination audit or reports `residual-complete`. Retain only (a) stored MI
from the existing GMM-MI fronts and (b) the 39-permutation MI component of the
required known-`f2` absorption decision. No H1-H3 search, selection, equation,
or decision threshold changes. Execution is paused because the CSD3 account
has no remaining CPU allowance; Section 11 is the authoritative Lightning AI
resume checklist.

**Planned result artifacts:** `experiments/mse_one_stage_sr_<run>.{md,json}`

## 1. Question and motivation

The current all-parameters pipeline searches each scalar encoder mean
`mu_k(theta)` from the same six cosmological inputs
`(omega_b, omega_cdm, H0, tau, A_s, n_s)`. PySR optimises the custom GMM-MI
inner loss, and equations on its loss-versus-complexity front are re-ranked by
held-out GMM-MI. A recurrent low-complexity coordinate `f1` is then calibrated
with `h`; a second, separate SR run targets the structured residual

```text
e1 = mu_k - h(f1),
```

and the present two-stage reconstruction is `h(f1) + g(f2)`. The
interaction-aware variant still targets `e1`; it only exposes `f1hat = h(f1)`
as a seventh input.

This experiment asks a different question: can one larger symbolic expression
reconstruct the latent directly, including structure currently recovered only
by `f2`? It will:

1. optimise mean-squared reconstruction error against the latent itself;
2. select equations by held-out reconstruction error rather than MI; and
3. raise the first-stage expression budget so primary and secondary structure
   can be discovered jointly.

For latent `k`, the proposed model is

```text
z_k = (mu_k - mean_fit(mu_k)) / std_fit(mu_k)
F_k(theta) = PySR expression fitted by MSE
muhat_k(theta) = mean_fit(mu_k) + std_fit(mu_k) * F_k(theta).
```

There is no residual target, `f1hat` input, derived cosmological input, or
post-SR spline in the primary reconstruction.

## 2. Interpretation boundary

MSE is deliberately calibration-sensitive. Unlike the current GMM-MI
protocol, it does not identify a coordinate only up to an arbitrary bijection;
it rewards the numerical scale, offset, and shape that reproduce `mu_k`.
Consequently, this is a **latent reconstruction and compression experiment**,
not a replacement for the existing blind physical-discovery result. Under A2,
the only newly computed MI is the required known-`f2` absorption test; stored
legacy-front MI remains available descriptively.

The current two-stage model also contains flexible, non-symbolic calibrations
`h` and `g`, whose complexity is not included in the PySR node counts.
Therefore direct and hierarchical reconstruction accuracy can be compared,
but their reported symbolic complexities are not strictly equivalent. Report
both `C_direct` and the lower-bound symbolic core `C_f1 + C_f2 + 1`, with the
calibrators called out separately.

## 3. Hypotheses

- **H1 — objective:** at the same `maxsize=20` and with both fronts selected
  by validation MSE, MSE search produces a more useful **direct numerical
  reconstruction** than the existing GMM-MI search. This operational endpoint
  deliberately includes MSE's identification of scale and offset. A
  common-form T1 calibration diagnostic, described below, compares the
  coordinate content separately. Within the existing GMM-MI front, comparing
  its MI-selected and MSE-selected members measures the selector effect.
- **H2 — capacity:** lifting MSE search from `maxsize=20` through 30 to 40
  reduces out-of-sample reconstruction error and removes the incremental
  information presently supplied by the canonical `f2`.
- **H3 — one-stage account:** the selected direct expression is non-inferior
  in reconstruction MSE to the frozen interaction-aware
  `h(f1) + g(f2)` hierarchy. The additive hierarchy is a secondary baseline.

A2 deliberately makes no global residual-termination claim. H1-H3 and the
known-`f2` absorption test remain the experiment's scope.

## 4. Frozen design

### 4.1 Data, targets, and splits

- Run both stored checkpoints: TT-only (`L=5`) and TT+EE-lowl (`L=6`).
- Target every encoder posterior mean in
  `models/<run>/analysis/encoder_means_test.npy`: 11 scalar targets total.
- Give every run the exact existing six inputs: `omega_b`, `omega_cdm`, `H0`,
  `tau`, `A_s`, and `n_s`. Do not expose `f1`, `f1hat`, the cached residual,
  or any new derived feature. `A_s` is the runner's existing alias/transform
  of the stored log-amplitude column, not an extra seventh input.
- Preserve the tier contract in `src/cmb_lcdm_sr/tiers.py`:
  - T0 `[0:5000)`: SR only, with the existing deterministic 4000 fit / 1000
    validation split;
  - T1 `[5000:25000)`: diagnostic calibration and the known-`f2` absorption map;
  - T2 `[25000:50000)`: confirmatory scoring only, opened once after all
    choices are frozen from T0/T1.
- Standardise each target using T0-fit statistics only. Optimising standardised
  MSE is equivalent to raw-latent MSE up to a fixed per-latent factor and keeps
  numerical conditioning comparable. Invert that transform before reporting
  RMSE in latent units.

### 4.2 Search configurations

Keep all non-objective settings identical to the current all-parameters run:
PySR 1.5.10, 5000 T0 samples, 200 iterations, 15 populations, seeds 0–4,
operators `exp, log, neg, square` and `+, *, -, /`, multithreading, turbo, and
no mini-batching.

| ID | inner loss | selection on T0 validation | maxsize | purpose |
|---|---|---|---:|---|
| `mi20-mi` | GMM-MI | maximum GMM-MI | 20 | existing discovery choice; do not rerun |
| `mi20-mse` | GMM-MI | minimum MSE | 20 | re-score the same stored front; selector-controlled reference |
| `mse20` | MSE | minimum MSE | 20 | loss-only ablation |
| `mse30` | MSE | minimum MSE | 30 | intermediate capacity point |
| `mse40` | MSE | minimum MSE | 40 | primary one-stage lifted-budget run |

Use an explicit PySR elementwise loss such as
`loss(prediction, target) = (prediction - target)^2`; do not rely on an
implicit library default. Use the fixed `{20, 30, 40}` ladder for every latent;
there is no data-dependent budget escalation. `maxsize=40` is primary because
joining two former searches, each allowed up to 20 nodes, can require roughly
their combined symbolic core plus a join. Size 30 bridges the existing
hyperparameter sweep and distinguishes a gradual capacity response from a
single endpoint result.

Label a latent **budget-saturated** when at least 3/5 `mse40` validation
winners have complexity at least 38. Report saturation, but do not launch
`maxsize>40` as part of this experiment.

### 4.3 Front selection

PySR's Hall of Fame is the training-MSE-versus-complexity front. Re-score every
returned equation on the untouched 1000-row T0 validation block and retain:

- **primary reconstruction winner:** finite equation with minimum validation
  NMSE;
- **parsimonious readout:** the cross-seed one-standard-error choice described
  below;
- validation GMM-MI for MI-selected legacy fronts only, never as a
  tie-breaker for MSE selection. Under amendment A1, MSE fronts skip the
  full per-equation GMM-MI diagnostic.

Resolve an exact MSE tie in favour of lower complexity, then lower equation
index. Require at least 99.9% finite predictions on T0 fit, T0 validation, T1,
and T2 separately; otherwise mark that equation/tier invalid. Apply the primary
rule independently for each search seed. A frozen winner that later fails the
T1 or T2 domain check fails that seed; never fall back to another equation
after opening a later tier.

For the one-standard-error readout, define for seed `s`
`E_s(c) = min NMSE_val` among valid equations with complexity at most `c`.
Average `E_s(c)` over the five seeds. Let `c_min` minimise that mean, and choose
the smallest `c` whose mean envelope is no greater than the mean at `c_min`
plus `sd(E_s(c_min))/sqrt(5)`. For each seed, retain its best valid equation at
or below that common complexity. This is a secondary parsimony readout; all
success decisions use the per-seed primary winners.

## 5. Evaluation

### 5.1 Reconstruction metrics

For every front member on T0 validation, and for each frozen selected member on
T2, report:

- MSE and RMSE in native latent units;
- `NMSE_T = MSE_T / Var_T(mu_k)`, using the variance of the scored tier;
- MAE and the 95th/99th percentiles of absolute reconstruction error;
- `R2 = 1 - sum((mu-muhat)^2) / sum((mu-mean(mu))^2)`;
- no newly computed reconstruction MI for direct, one-SE, or hierarchy
  methods (A2);
- expression complexity, support, fit time, finite-prediction fraction, and
  evaluation failures.

Always score the primary direct expression as the inverse-standardised PySR
prediction, with no fitted `h`/`g` map. An optional T1-calibrated score may be
reported as a labelled diagnostic but cannot carry any success decision.

### 5.2 Required comparisons

1. `mse20` versus `mi20-mse`, at `maxsize=20` and under the same validation-MSE
   selector, measures the inner objective's effect on usable direct
   reconstruction. Because MI is invariant to bijective recalibration, this
   is not a calibration-free comparison of search geometry.
2. `mi20-mse` versus `mi20-mi` on the identical stored GMM-MI front isolates
   the selector. This is descriptive because GMM-MI expressions need not have
   a useful numerical calibration.
3. The seed-paired `mse20 -> mse30 -> mse40` curve isolates lifted capacity.
4. `mse40` direct reconstruction versus the frozen canonical `h(f1)`,
   additive `h(f1)+g(f2)`, and interaction-aware hierarchy tests whether one
   stage recovers the hierarchy.
5. Compare all three MSE fronts at common complexity cuts as well as their
   winners; this prevents a larger search from being credited merely for
   returning more high-complexity candidates.

As a labelled diagnostic, fit the same monotone calibration family on T1 for
the frozen `mi20-mse` and `mse20` winners, then compare their calibrated T2
errors. This asks whether the objectives found equally useful coordinates once
scale and offset are treated symmetrically. It cannot replace the uncalibrated
direct-reconstruction endpoint.

Use the same stored targets and T2 rows for every method. The existing
hierarchical result is a fixed baseline, not reselected in response to this
experiment. Rebuild its frozen T1-fitted `h`/`g` maps and predictions on T2.
Do not relabel the existing stored `combined_r2_vs_mu`, which is a T1 result,
as T2 performance. The latest interaction-aware residual result is the primary
two-stage comparator; the additive result is secondary.

### 5.3 Did the direct expression absorb `f2`?

Do not decide this by substring or formula resemblance. For each direct
winner, define

```text
e_direct = mu_k - muhat_k(theta).
```

Perform one pre-specified check. Using the same five-fold, 64-bin monotone
calibration family as the current hierarchy, cross-fit `q(f2)` against
`e_direct` on T1 for diagnostics, then refit `q` on all T1. On T2 compute
`R2_f2 = 1 - SSE(e_direct - q(f2)) / SST(e_direct)`, where
`SST(e_direct) = sum((e_direct - mean_T2(e_direct))^2)`. Estimate
`MI(e_direct; f2)` on those same T2 rows and compare it with its 97.5th
percentile 39-permutation T2 null. No map or threshold is fitted on T2. This is
the sole newly computed MI audit retained by A2.

Semantic recurrence and sensitivity-signature overlap with the old `f1` and
`f2` are useful supporting evidence, but they do not override reconstruction
and the known-`f2` absorption test. Cluster direct expressions with the repository's frozen
semantic equivalence rule and report `R_SR`; call the symbolic replacement
stable only at `R_SR >= 0.8`.

## 6. Frozen decision rules

Make calls per latent; also publish the full 11-latent ledger so aggregate
success cannot hide failures.

For any five paired seed-level values `x_s`, define the one-sided 95% upper
bound

```text
U95(x) = mean(x_s) + 2.132 * sd(x_s) / sqrt(5).
```

Seeds—not rows—are the replication unit. Report exact paired values as well as
the bound.

- **MSE objective helps:** with
  `Q_obj,s = MSE_T2(mse20_s) / MSE_T2(mi20-mse_s)`, at least 4/5
  `Q_obj,s < 1` and `U95(Q_obj) < 1`. If old front/seed identity is incomplete,
  report H1 descriptively rather than inventing a pairing.
- **Capacity helps:** with
  `Q_cap,s = MSE_T2(mse40_s) / MSE_T2(mse20_s)`, at least 4/5
  `Q_cap,s < 1` and `U95(Q_cap) < 1`. The `mse30` point must be reported but
  need not be monotone.
- **Known `f2` absorbed:** for at least 4/5 `mse40` seeds,
  `R2_f2 <= 0.05` and `MI(e_direct; f2)` is no greater than its same-tier
  97.5th-percentile permutation null.
- **One-stage reconstruction matches two-stage:** with the frozen
  interaction-aware hierarchy as denominator,
  `Q_rec,s = MSE_T2(mse40_s) / MSE_T2(hierarchy_s)`, at least 4/5
  `Q_rec,s <= 1.10` and `U95(Q_rec) <= 1.10`. Use seed-matched hierarchy
  outputs; if only a single canonical hierarchy exists, apply that fixed
  denominator to every direct seed and label the comparison unpaired.
- **Symbolically stable:** the primary semantic cluster has `R_SR >= 0.8`.
  Stability is reported independently and cannot rescue a failed
  reconstruction criterion.

Classify outcomes separately:

- `one-stage replacement`: known `f2` absorbed and two-stage accuracy matched;
- `partial absorption`: capacity helps, but either known `f2` remains
  incremental or the two-stage equivalence margin is missed;
- `no capacity gain`: the lifted budget fails the paired capacity rule;
- append `symbolically-stable` only when the independent recurrence rule
  passes.

## 7. Controls and run order

### 7.1 Controls

- Keep the fit-mean predictor and the existing six-input OLS model as
  reconstruction baselines.
- Add a protocol-identical MSE shuffled-target control for the amplitude latent
  of each checkpoint, pairing search seeds 0–2 at `maxsize=20` and 40.
  Independently permute the target within each tier using stored deterministic
  permutation seeds. Select by shuffled-target validation MSE and report
  validation/T2 `R2` against both shuffled and true targets.
  These six paired controls per checkpoint are diagnostics only; three
  permutations are not used to estimate any 97.5th-percentile threshold.
- Reuse existing `mi20` reports and existing residual-SR results read-only.
  Their current shuffled controls are GMM-MI controls and cannot stand in for
  the new MSE control.

### 7.2 Execution order

1. Implement loss/selection dispatch and test it on a small synthetic target
   with a known additive-plus-interaction expression.
2. Smoke-test one latent/seed and verify report metadata, ranking direction,
   inverse standardisation, and output isolation.
3. Run all 11 latents for seeds 0–4 at the fixed `mse20`, `mse30`, and
   `mse40` budgets: 165 main runs
   (`11 latents x 5 seeds x 3 budgets`).
4. Run the 12 diagnostic shuffled controls
   (`2 amplitude latents x 3 seeds x 2 endpoint budgets`).
5. Run consolidation in `select` mode. It may read T0 only and writes an
   immutable selection manifest containing run/latent/seed, budget, equation
   index, expression, target transform, report/config hashes, code revision,
   and a manifest digest.
6. Compute the common-form T1 calibration diagnostics from the frozen
   manifest. Store them as a separate hashed artifact; they cannot change any
   equation or budget choice.
7. Run `confirm --manifest <path> --calibration <path>`. It verifies both
   digests before opening T2, evaluates all frozen methods on exactly the same
   T2 rows, runs only the required known-`f2` MI audit, and generates the two
   per-checkpoint result files. T2 is held out
   from this new search and selection procedure, although it is not globally
   pristine with respect to earlier repository analyses.

## 8. Implementation plan

### Runner and loss dispatch

- In `src/cmb_lcdm_sr/sr.py`, add a small explicit loss registry/dispatcher
  for `gmm_mi` and `mse`, including stable names and plot labels. Preserve
  `JULIA_LOSS_GMM_MI` unchanged.
- In `scripts/run_blind_sr.py`, add
  `--inner-loss {gmm_mi,mse}`, `--selection-metric {auto,mi,mse}`, and
  `--posthoc-mi {auto,full,none}`. Selector `auto` maps GMM-MI to MI and
  MSE to MSE; post-hoc-MI `auto` computes full MI only for MI selection.
  Existing GMM-MI invocations must retain their current behaviour.
- Pass the GMM-MI source through `loss_function` only in GMM-MI mode and the
  explicit squared loss through `elementwise_loss` only in MSE mode.
- Generalise front ranking, console labels, plot labels, default output names,
  and `report.json` metadata. Store `mse_val` for every valid front member.
  For MSE-selected runs, store `mi_val=null`/`mi_val_err=null` with explicit
  post-hoc-MI skip metadata; MI-selected legacy invocations still compute
  full `mi_val`. Also store the target transform and deterministic tie-break
  rule.
- Apply the same loss and selection switches to
  `scripts/run_shuffled_control.py`; do not duplicate ranking logic.

### Launch and consolidation

- Add a dedicated `hpc/slurm_mse_one_stage_sr.sh` so new results cannot mix
  with `allparams`, `residual_sr`, or reference run directories.
- Write outputs under
  `results/<run>/mse_one_stage_ms<maxsize>/z<k>_seed<seed>/`.
- Add `scripts/consolidate_mse_one_stage.py` to pool seed-paired fronts,
  implement separate `select`, `calibrate`, and `confirm` modes, perform the
  T0 one-SE readout, evaluate frozen winners on T1/T2, recompute the
  hierarchical baseline on T2, run the required known-`f2` audit, and emit
  `experiments/mse_one_stage_sr_<run>.{md,json}`.
- Leave `hpc/slurm_residual_sr*.sh`, `scripts/build_f1hat_cache.py`, and the
  existing result artifacts unchanged; they provide baselines only.

### Tests

Add or extend tests for:

- loss dispatch and mutual exclusivity of `loss_function` /
  `elementwise_loss`;
- backward-compatible GMM-MI defaults;
- MSE ascending versus MI descending ranking, including non-finite rows and
  deterministic ties;
- the cross-seed envelope and one-standard-error complexity rule;
- report schema and output namespace isolation;
- fit-only target standardisation and inverse transformation;
- shuffled-control parity;
- run-matrix enumeration and consolidation on fixture reports;
- selection-manifest hashing and refusal on a changed report/config;
- T2 access occurring only in `confirm` after equation/budget choices are
  frozen.

## 9. Deliverables

- implementation and tests described above;
- immutable per-run `report.json`, `equations.csv`, and Pareto plots;
- one JSON and one Markdown consolidation per checkpoint;
- a compact comparison table per latent containing `mi20-mi`, `mi20-mse`,
  `mse20`, `mse30`, `mse40`, `h(f1)`, additive `h(f1)+g(f2)`, and
  interaction-aware hierarchy reconstruction metrics;
- a decision ledger for capacity gain, known-`f2` absorption, and two-stage
  equivalence;
- README/method updates only after results exist, clearly labelling this as a
  reconstruction follow-up rather than changing the frozen MI-discovery
  protocol.

## 10. Main risks

- **Calibration replaces coordinate discovery.** Expected under MSE; keep the
  claim scoped to reconstruction and use new MI only for the required
  known-`f2` absorption test.
- **Larger trees overfit 4000 rows.** Select on held-out T0 validation, inspect
  train/validation gaps, use shuffled controls, and confirm only once on T2.
- **A larger `maxsize` does not guarantee useful search coverage.** Report
  boundary saturation and front envelopes; do not adapt the budget after
  inspecting results.
- **Direct and hierarchical complexity are incomparable.** Report symbolic
  cores and non-symbolic calibrators separately; do not claim a complexity win
  from node counts alone.
- **A single expression may absorb the old `f2` but leave new structure.** A2
  accepts this limitation: report known-`f2` absorption but do not claim full
  residual completeness.

## 11. Current status and Lightning AI handoff (2026-08-25)

### 11.1 Frozen state

- CSD3 execution is paused because the account is at
  `AssocGrpCPUMinutesLimit`. Replacement job `34331307` was cancelled before
  starting, and the queue was empty when this handoff was written. Do not
  submit another CSD3 job without a renewed allowance.
- Main searches: **36/165 complete; 129 remain**. Completed array task IDs are
  0-35: TT `z0` and `z1` for every budget/seed, plus TT `z2` seeds 0-1 for
  every budget. Existing valid `report.json` files are immutable resume points
  and must be skipped, not overwritten.
- Shuffled controls: **0/12 complete**.
- No MSE selection manifest or MSE T1 calibration artifact exists, and this
  experiment has not opened T2. The select/calibrate/confirm stages must wait
  until all required search and control reports exist.
- The first 36 reports contain the historical non-selecting post-hoc MI fields.
  Later MSE reports will contain null MI fields plus explicit skip metadata.
  This mixed diagnostic presence is compatible because selection uses MSE.
- Do **not** rerun the existing GMM-MI searches. `mi20-mi` reuses their stored
  fronts and stored MI choice; `mi20-mse` re-ranks those same stored fronts by
  their stored validation MSE. Only unfinished `mse20`, `mse30`, `mse40`, and
  the 12 new MSE shuffled controls require search compute.

### 11.2 Files and environment to carry over

Copy the repository together with `data/`, `models/`, and `results/`, preserving
relative paths and all 36 completed report directories. The frozen software
contract is PySR 1.5.10 with the explicit Julia elementwise MSE loss. The CSD3
environment used Python 3.12 and Julia 1.11; on Lightning, record exact package
and Julia versions before resuming. The current Slurm launchers are useful as
matrix/configuration specifications but are CSD3-specific and should not be
run verbatim on Lightning.

Before compute, run:

```bash
python -m pytest -q tests/test_mse_loss_selection.py \
  tests/test_mse_one_stage_consolidation.py tests/test_mse_one_stage_hpc.py
PRINT_MATRIX=1 bash hpc/slurm_mse_one_stage_sr.sh
PRINT_MATRIX=1 bash hpc/slurm_mse_one_stage_control.sh
```

The matrix output is the source of truth for task identity. Preserve the
existing result path contract and skip a task only after validating its
`report.json`.

### 11.3 Next tasks on Lightning AI

1. Restore and verify the environment, input artifacts, existing 36 reports,
   matrix sizes (165 main and 12 control), and provenance hashes.
2. Adapt the matrix to Lightning orchestration. Prefer a persistent
   Python/Julia worker or coarse task batches so Julia/PySR startup is
   amortized; the no-MI smoke run spent about 156 of 215 seconds in startup
   outside the measured fit.
3. Resume main task IDs 36-164 while skipping all validated existing reports.
4. Run the 12 shuffled controls.
5. Run `select` for both checkpoints. This reads T0 only and freezes immutable
   manifests.
6. Run `calibrate` for both checkpoints. This reads T1 only and cannot change
   the selections.
7. Run `confirm` once for both checkpoints. It verifies both hashes before T2,
   computes reconstruction metrics and the required known-`f2` absorption MI
   test, and performs no optional reconstruction/full-residual MI audits.
8. Verify `experiments/mse_one_stage_sr_<run>.{json,md}` and only then update
   README/method text from observed results.

For capacity planning, the remaining workflow after A2 is approximately
**16,000-18,000 CSD3-equivalent CPU-minutes** with the current one-process-per-
task startup pattern: about 11,000-12,000 for unfinished searches/controls and
roughly 4,500 plus light overhead for the required known-`f2` confirmation.
The removed H4 audit alone was projected at about 27,000 CPU-minutes. Lightning
billing and persistent-worker startup amortization can make these figures
non-comparable, so benchmark one representative task there before scaling.
