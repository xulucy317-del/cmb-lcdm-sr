# Decision checkpoint: symbolic regression versus coordinate-matched OLS

*Codex-generated checkpoint, frozen 2026-08-31. This is the canonical one-file
synthesis for the OLS/SR
decision. It combines the original discovery result, the one-stage MSE
extension, the Float64/preprocessing sensitivity campaign, and the completed
coordinate-matched OLS audit. The detailed frozen tables and provenance are
retained below.*

## Checkpoint synthesis

### Executive conclusion

There is no paradox in the current result, and the result is **not** that
symbolic regression cannot win. SR wins particular latents, sometimes by a
large margin. The result is narrower:

- On these two fixed VAE checkpoints and this narrow parameter prior, there is
  no robust predictive-performance justification for choosing the reported SR
  pipelines over a six-input OLS baseline. OLS is the pragmatic reconstruction
  default because its fitting problem is deterministic and exactly solved, and
  it wins more latent-level comparisons; this is a model-selection decision,
  not a proof of global OLS superiority or equivalence.
- The mathematical SR hypothesis class may contain the OLS solution, but the
  *reported SR estimator* is a finite stochastic grammar search with nonlinear
  constant optimization, Pareto pruning, and validation selection. OLS solves
  the seven-parameter affine subproblem directly and essentially exactly.
  Function-class inclusion therefore does not imply that a finite PySR run
  must find, retain, or select the OLS expression.
- The fitted encoder maps are not exhausted by an affine model. A
  gradient-boosting probe fitted on the first half of T1 predicts 97--99% of
  the variance of each OLS residual on the second half of T1, which was held
  out from that probe's fit; typical NMSE falls from about `2e-3` to `3e-5`.
  Thus predictable non-affine structure remains at smaller variance.
- The blind SR results are not numerically invalidated. They remain evidence
  that the search repeatedly generated physically meaningful symbolic
  hypotheses, structured primary and residual coordinates, and the familiar
  amplitude direction. What is invalidated is the stronger interpretation
  that SR was *necessary*, *unique*, or predictively *superior*—especially for
  the `-2` direction, which OLS also recovers.

The cleanest statement is therefore: **SR supplies frozen, recurrent symbolic
hypotheses and wins selected nonlinear cells, but it has not demonstrated a
general predictive or uniquely interpretive advantage over coordinate-matched
OLS in this study.**

### Three different questions were being mixed together

| Method/readout | Question it answers | What a win means | What it does not mean |
|---|---|---|---|
| Six-input OLS | How well can an exactly fitted affine map reconstruct the latent? | The least-squares optimum within the affine class on T0-fit also has the lowest observed held-out error in that comparison | The latent is truly linear, or the coefficients are a unique physical decomposition |
| MI-SR (`mi20-mi`) | Can a compact symbolic coordinate carry dependence with the latent, up to a bijection? | A useful dependence coordinate | Correct scale/offset, lowest NMSE, or superiority to OLS |
| Calibrated MI-SR | How well can that frozen coordinate reconstruct after a T1-only monotone map? | Coordinate plus calibrator predicts the latent | The symbolic expression alone is a calibrated law |
| MSE-SR (`mse40`) | Can finite-budget symbolic search directly reconstruct the latent? | The returned symbolic predictor has low numerical error | The global optimum over every representable expression was found |

MI and NMSE can consequently disagree without contradiction. In the matched
`logamp64` audit, the median MI-SR point estimate has higher MI than OLS for
6/11 latents, while OLS has lower median calibrated NMSE for 7/11; neither
winner count is a significance test. Those endpoints measure different
properties. The common 64-bin calibration can also worsen an already
well-calibrated OLS predictor—for example, log-amplitude TT z2 moves from
0.044% raw NMSE to 0.140% calibrated NMSE—so the calibrated table tests equal
coordinate treatment, not the best deployment of each pipeline.

### Evidence ladder and final status

| Stage | What was run | Main result | Status at this checkpoint |
|---|---|---|---|
| Blind MI discovery | Two fixed seed-42 VAE checkpoints, 11 latents, five PySR search seeds | Recurrent symbolic coordinates; `10/11` cards primarily interpreted and EE z0 unresolved; every first-stage residual structured; a recurrent second coordinate for `11/11`; blind `-2` readouts | Valid as per-checkpoint structural evidence; not a head-to-head predictive test against OLS |
| One-stage MSE extension | 165 searches at maxsize 20/30/40 plus 12 shuffled controls | No one-stage replacement; 6 partial absorption, 5 no capacity gain; known `f2` absorbed in `0/11`; OLS beats median `mse40` in `8/11` latents | Valid reconstruction result; shows that this finite search did not subsume the hierarchy or reliably match OLS |
| Primary three-way T2 snapshot | Raw OLS, T1-calibrated MI-SR, raw MSE-SR | Latent-median NMSE winners: OLS 7, MI-SR 2, MSE-SR 2 | Frozen descriptive pipeline comparison; the three columns do not share one objective/calibration treatment |
| Float64/preprocessing campaign | 330 fresh SR searches in `raw64`, `physical_o1_64`, and `logamp64` | Mixed winners appeared as OLS/SR = 9/2, 6/5, and 5/6 | The `logamp64` 5/6 apparent SR edge is **retired for method comparison** because OLS was not refitted in the SR coordinate |
| Coordinate-matched audit | OLS refitted in every arm; the same T1-only calibration procedure fitted separately to OLS and MI-SR; frozen SR replay | In `logamp64`, direct raw OLS/MSE-SR = 7/4 and calibrated OLS/MI-SR = 7/4; mixed pipeline = 7/1/3 | Main fairness result, but post-hoc and not a fresh preregistered holdout |

The discovery compendium's opening synthesis and totals predate the later
extensions and are now stale. Its underlying SR measurements remain source
evidence, but this checkpoint supersedes any older headline language implying
that SR uniquely recovered the physics or was the better predictive model. Its
three encoder-side `-2` results are three readout instruments on shared
checkpoints and data, not independent experimental replications.

### Why a richer SR grammar can lose to OLS here

The usual nesting argument applies only if the larger class is optimized to
its global optimum under the same loss and selection rule. That is not the
experiment that produced these rows.

1. **Exact small optimization versus heuristic large search.** OLS solves one
   convex seven-coefficient problem. A generic dense six-input affine tree has
   complexity 25 under the campaign's unit node costs, so it fits inside
   `maxsize=40`; nevertheless PySR must evolve that structure and tune seven
   constants while exploring many nonlinear alternatives. Representability is
   not discoverability. The `maxsize=20` MI search does not contain a generic
   dense six-input affine tree at that complexity.
2. **The search gap is visible before T2.** Across the 55 frozen `mse40`
   reports, OLS has lower T0-validation MSE than the validation-selected SR
   equation in 39/55 seed runs (TT 24/25; TT+EE 15/30). The median ratio
   `MSE_val(SR) / MSE_val(OLS)` is 1.445, with range 0.425--328.597. More
   strongly, OLS has lower T0-fit MSE than every returned front equation in
   38/55 runs. The latter replays each stored `ols_baseline.coefs` vector on
   the 4,000 T0-fit rows in the same standardized target and compares it with
   every stored `all_equations[].mse_fit_eval`. These post-hoc mechanism
   diagnostics use `ols_baseline.mse_val`, `best_mse_val`, the stored
   evaluated front, and a replay of the stored OLS coefficients on T0-fit from
   `results/*/mse_one_stage_ms40/*/report.json`. They localize most losses to
   candidate discovery, constant fitting, or front retention in these
   runs—not to a surprise created by T2. They do not distinguish among those
   three mechanisms.
3. **The sampled target geometry is mostly affine.** The median OLS error is
   already at roughly the `10^-3` dimensionless-NMSE scale (about 99.8% of
   variance captured), although difficult cells such as TT+EE z0/z4 are much
   less affine. The nonlinear remainder is real but small enough in many
   latents that SR's search error can exceed the benefit of extra flexibility.
4. **The prior makes key physics nearly linear.** Over
   `tau in [0.01, 0.13]`, `exp(-2*tau)` is 99.90% linear, with maximum
   deviation 0.52%. Using `ln10As` makes
   `ln10As - 2*tau` explicitly affine. A parsimonious search can prefer a
   Taylor surrogate, and matched OLS receives almost all of the same local
   predictive advantage.
5. **MI-SR deliberately solves a different problem.** GMM-MI is invariant to
   an invertible remapping of the expression, so MI search is indifferent to
   numerical calibration. At the latent-median level, symmetric T1 calibration
   reduced the apparent `mse20`-over-`mi20-mse` advantage from 11/11 to 9/11
   in the one-stage study. This explains MI-SR/NMSE disagreements; it does not
   explain MSE-SR losses, which instead point to search difficulty and
   near-affine geometry.
6. **The evolutionary search is coordinate-sensitive.** `raw64` and
   `physical_o1_64` are the same affine hypothesis class and give numerically
   identical matched OLS predictions, yet their SR winner counts change under
   harmless input rescaling. `logamp64` genuinely changes the affine class.
   The original apparent SR advantage disappears when OLS is given that same
   coordinate.

TT+EE z4 is the important counterexample to any claim that OLS simply dominates:
in the matched `logamp64` arm, raw MSE-SR has 1.368% median NMSE versus 4.179%
for raw OLS, and calibrated MI-SR has 1.438% versus 4.062% for calibrated OLS.
This is a clear latent-specific SR success, but the audit does not isolate why
TT+EE z4 is favorable; the overall result is heterogeneous, not “SR cannot
win.”

### What OLS recovering `-2` means

The matched `logamp64` OLS receives separate `tau` and `ln10As` columns. It
is not given `ln10As - 2*tau`, and its coefficients are not tied. After
returning the standardized fit to the input basis, the conditional
partial-slope ratios are:

| Previously designated amplitude latent | `b_tau / b_ln10As` | Difference from `-2` | Raw T2 NMSE |
|---|---:|---:|---:|
| TT z2 | -1.97853231 | 1.073% | 0.0444213% |
| TT+EE z5 | -1.99674227 | 0.163% | 0.0451330% |

Because `ln10As - 2*tau` differs from `ln(A_s exp(-2 tau))` only by a
constant absorbed by the intercept, OLS reproduces the familiar
screened-amplitude direction. The ratios are well conditioned and fixed from
T0-fit, but they have no coefficient-ratio confidence interval. They are
conditional on the other four inputs, were inspected for already-designated
amplitude latents, and reproduce an earlier T1 OLS diagnostic on the same
checkpoints and dataset. This is recovery of a direction, not an independent
discovery, proof of exact equality, or proof that the entire latent is
one-dimensional.

Blind SR still generated the direction without an engineered composite: the
two-input EE search produced a literal `A_s*exp(-2*tau)` expression, the
all-input top forms had derivative ratios `-1.974 +/- 0.018` (TT) and
`-1.993 +/- 0.008` (TT+EE), and exact composites recur elsewhere in the
cards and residual searches on the same checkpoints and data. This is repeated
recovery of a physically recognizable structure within these checkpoints. The
OLS evidence changes the exclusivity claim: SR was neither necessary nor
uniquely capable of exposing it.

### What survives, what is retired, and what remains unknown

Survives:

- the frozen numerical SR equations, recurrence measurements, null controls,
  residual tests, and level-set results;
- the per-checkpoint card statuses under their actual predicates: 10/11
  primarily interpreted and EE z0 unresolved;
- the conclusion that the latent maps contain nonlinear, hierarchical
  structure and that a single maxsize-40 expression absorbed the known `f2`
  in 0/11 latents;
- the conclusion that blind SR generated physically meaningful
  nonlinear/compositional hypotheses without an engineered composite, with
  strong individual wins such as TT+EE z4.

Retired or unsupported:

- “SR generally outperforms OLS”;
- “SR was required to recover the `-2` direction” or “only SR found it”;
- the unmatched `logamp64` 6-to-5 SR headline;
- interpreting a card status as proof that its SR coordinate is the unique,
  simplest, or best explanation relative to OLS;
- pooling latent, seed, arm, or confidence-interval winner counts into a
  global significance claim.

Still unknown:

- whether these symbolic coordinates and the OLS/SR balance recur across
  independently trained VAE seeds;
- whether SR gains grow on a wider parameter domain where
  Taylor-linearization is weaker;
- whether a prespecified nonlinear model improves on OLS on genuinely fresh
  simulations;
- whether matched description length, interpretability, or extrapolation
  favors SR. OLS is itself explicit, and no matched interpretability study has
  yet established SR's incremental advantage.

### Count hygiene: why the reported totals differ

The denominators refer to different units and should never be interchanged:

- `17/55` is the number of individual MSE-SR **seed runs** beating OLS NMSE
  in the original primary comparison.
- `8/11` is the number of **latent medians** won by OLS against `mse40` in
  the original physical-input one-stage campaign.
- `7/11` is the number of **latent-level pipeline winners** for OLS in the
  primary mixed three-way table; it is also the OLS count in each matched
  `logamp64` like-for-like reconstruction comparison, but from a different SR
  campaign.
- `33/21/1` and `35/20/0` are **seedwise paired-row CI verdicts** in the
  matched `logamp64` direct and calibrated comparisons. They are conditional,
  unadjusted, share one OLS fit across seeds, and are not 55 independent model
  replications.

Likewise, the original physical-input 8/3 result and matched `raw64` 9/2
result are not contradictory: `raw64` is a fresh Float64 SR search campaign.
Tiny OLS MI differences across reports are fresh GMM estimates, not changed
OLS predictions.

### Decision and next tests

Freeze the same-data predictive conclusion now: use OLS as the reconstruction
baseline/default, present SR as a structural-discovery method with
latent-specific predictive successes, and do not tune a new headline against
the already-inspected T2.

The smallest next diagnostic is to inject the exact T0-fit OLS expression into
each frozen `mse40` candidate set at its true complexity and apply the
unchanged T0-validation selection/scoring logic. This requires no broad new SR
campaign and separates three possibilities:

1. If injected OLS beats every returned member on fit and validation, its
   omission is an output-set failure consistent with candidate discovery,
   constant fitting, or front retention; this test does not distinguish them.
2. If a nonlinear member beats OLS on fit but loses on validation, that member
   overfits relative to OLS; because OLS was absent from the original candidate
   set, this alone does not diagnose validation selection.
3. If the augmented readout closes a cell's gap, candidate-set omission
   explains that stored cell; it does not establish why PySR omitted OLS or
   generalize beyond these runs.

Then test geometry, still labelled diagnostic on existing tiers, with an exact
regularized quadratic model or GAM and error stratified by distance from the
prior-box center. For a new predictive claim, preregister OLS, nonlinear
residual/hybrid, and SR comparisons and evaluate once on fresh simulations.
For an architecture-level scientific claim, retrain independent VAE seeds and
test semantic recurrence after latent alignment. A wider-prior experiment is
the relevant extension if extrapolative nonlinear physics—not interpolation in
this narrow box—is the objective. Simply increasing PySR iterations is not the
next informative step until the candidate-injection diagnostic identifies the
failure mode.

### Source map

- Original discovery synthesis and limitations:
  `docs/results_compendium.md`, with authoritative per-stage artifacts in
  `experiments/`.
- One-stage reconstruction extension: `docs/mse_one_stage_results.md` and
  `experiments/mse_one_stage_sr_<run>.{json,md}`.
- Coordinate-matched audit:
  `experiments/coordinate_matched_ols_v1.json` and the generated detailed
  report `docs/coordinate_matched_ols_v1.md`.
- The tables below retain the complete comparison and matched-audit record so
  this file can be read as the decision checkpoint without reconstructing the
  chronology from those sources.

## Primary frozen three-way comparison

The table below compares the six-input OLS baseline, the actual MI-selected
symbolic-regression coordinate (`mi20-mi`), and the primary MSE-trained
symbolic-regression model (`mse40`).

| Latent | OLS MI | MI-SR MI | MSE-SR MI | OLS NMSE % | MI-SR calibrated NMSE % | MSE-SR raw NMSE % |
|---|---:|---:|---:|---:|---:|---:|
| TT z0 | 3.312±.014 | 3.309 [3.266,3.372] | 2.800 [2.698,3.153] | .186 | .185 [.166,.190] | .398 [.215,.466] |
| TT z1 | 2.315±.014 | 2.328 [2.293,2.329] | 2.180 [1.223,2.392] | 1.402 | 1.672 [1.552,1.730] | 1.840 [1.518,8.563] |
| TT z2 | 3.520±.014 | 3.871 [3.698,3.937] | 2.285 [.613,3.528] | .099 | .158 [.146,.169] | 1.195 [.095,29.547] |
| TT z3 | 3.120±.014 | 3.109 [3.095,3.150] | 3.068 [2.840,3.155] | .214 | .258 [.253,.267] | .250 [.208,.387] |
| TT z4 | 3.870±.012 | 3.587 [3.467,3.795] | 3.110 [2.607,3.758] [^gmm-failure] | .054 | .202 [.171,.230] | .299 [.063,.743] |
| TT+EE z0 | 1.729±.014 | 1.760 [1.749,1.772] | 1.429 [1.392,1.737] | 3.949 | 4.575 [4.499,5.225] | 6.430 [3.992,6.810] |
| TT+EE z1 | 3.723±.010 | 3.695 [2.833,3.820] | 2.077 [2.030,3.642] | .097 | .154 [.142,.433] | 1.638 [.201,1.785] |
| TT+EE z2 | 3.265±.014 | 3.278 [3.208,3.311] | 3.285 [3.027,3.335] | .173 | .216 [.204,.248] | .167 [.154,.288] |
| TT+EE z3 | 2.980±.014 | 3.131 [3.101,3.211] | 3.203 [3.033,3.238] | .311 | .306 [.288,.343] | .209 [.190,.281] |
| TT+EE z4 | 1.847±.014 | 2.182 [2.047,2.272] | 2.074 [1.984,2.257] | 4.283 | 1.767 [1.492,5.191] | 2.662 [1.706,3.353] |
| TT+EE z5 | 3.549±.014 | 3.872 [3.557,3.963] | 2.882 [2.151,3.825] | .115 | .126 [.117,.203] | .415 [.064,1.573] |

MI is in nats and higher is better. NMSE is
`100 * MSE / Var_T2(encoder mean)`, expressed as a percentage, and lower is
better. OLS MI is shown as point estimate ± GMM bootstrap standard deviation.
Each SR entry is the median [minimum, maximum] over five frozen search seeds.

### Evaluation protocol

- OLS is fitted on the 4,000 T0-fit rows using all six cosmological inputs and
  an intercept.
- Each SR equation is fitted on T0-fit and selected on the separate 1,000-row
  T0-validation split.
- MI-SR is the `mi20-mi` winner: maximum held-out GMM-MI from each
  maxsize-20 MI-search front.
- MSE-SR is the `mse40` winner: minimum held-out MSE from each primary
  maxsize-40 MSE-search front. Realized expression complexity can be below 40.
- MI-SR receives a frozen 64-bin monotone calibration fitted only on the
  20,000 T1 rows. MSE-SR is scored as its direct, inverse-standardized
  prediction without T1 calibration.
- NMSE uses all 25,000 T2 rows. GMM-MI uses the same deterministic 5,000-row
  T2 subset for every method, with `gmm-mi==0.8.2` and its unchanged default
  50-bootstrap estimator.

[^gmm-failure]: The MSE-SR MI summary for TT z4 uses four valid seeds. Seed 2
    had fully finite predictions, but the unchanged GMM estimator failed from
    covariance collapse.

### Descriptive result

- MI-SR has higher GMM-MI than MSE-SR in 41 of 54 valid seedwise comparisons.
- MI-SR has lower NMSE than MSE-SR in 34 of 55 seedwise comparisons.
- MSE-SR has higher MI than OLS in 20 of 54 valid comparisons and lower NMSE
  than OLS in 17 of 55 comparisons.
- By median T2 NMSE, the best method is OLS for 7 of 11 latents, MI-SR for 2,
  and MSE-SR for 2.

These are descriptive point-estimate counts, not significance tests. The SR
range measures stochastic search variability, whereas the OLS MI uncertainty
is the estimator's bootstrap variation. This is a comparison of the primary
pipelines, not a matched-complexity objective ablation: MI-SR has maxsize 20,
while primary MSE-SR has maxsize 40. A budget-matched comparison would use
`mse20` separately.

## Float64/preprocessing sensitivity: unmatched diagnostic

The separate `precision_preprocess_v1` campaign originally produced these
descriptive median-T2-NMSE winner counts. For each latent, the winner is the
lowest of frozen OLS, median calibrated MI-SR, and median raw MSE-SR. “SR”
aggregates wins by either SR pipeline and is not a single pooled method.

| Input arm | OLS wins | SR wins | Total latents |
|---|---:|---:|---:|
| `raw64` | 9 | 2 | 11 |
| `physical_o1_64` | 6 | 5 | 11 |
| `logamp64` | 5 | 6 | 11 |

These counts are retained as an audit trail, but they are not a valid
cross-arm OLS/SR comparison. The same physical-`A_s` OLS fit was frozen in all
three rows, including `logamp64`; OLS therefore was not refitted in the
coordinates given to SR. In particular, the apparent 6-to-5 SR edge in the
`logamp64` row cannot be used as evidence for SR. These are also descriptive
winner counts, not significance or equivalence tests.

## Coordinate-matched OLS audit

The additive `coordinate_matched_ols_v1` audit closes that
coordinate-mismatch loophole within this fixed dataset. It refits a six-input,
full-rank OLS separately in each arm on T0-fit after centering and scaling
every column with T0-fit statistics. It then applies the same T1-only 64-bin
monotone calibration procedure separately to OLS and MI-SR for the coordinate
comparison, uses T2 only at the audit's confirmation stage, and uses the exact
frozen 5,000-row GMM-MI subset. The frozen SR equations are replayed without a
new search or refit.

### Extension design and tier isolation

- The audit has six cells: two encoder runs (TT and TT+EE) crossed with
  `raw64`, `physical_o1_64`, and `logamp64`.
- In each cell, OLS uses all six arm-specific inputs plus an intercept. It is
  fitted in the native latent target on the 4,000 T0-fit rows. The 1,000
  T0-validation rows are diagnostic only.
- Every input column is centered and scaled using T0-fit statistics before
  `numpy.linalg.lstsq`. All fits have rank 7. This conditioning does not
  change the affine function class.
- T1 contains 20,000 rows. It supplies a five-fold cross-fit diagnostic. For
  T2 confirmation, the same frozen 64-bin monotone procedure/settings are used
  to fit a separate final map for each OLS and MI-SR predictor on all finite T1
  rows; OLS and MI-SR do not share one calibration map.
- T2 contains 25,000 rows. Within this audit pipeline, it is first read at
  confirmation; study-wide, T2 had already been inspected before this post-hoc
  audit was designed. NMSE uses all 25,000 rows. OLS GMM-MI is recomputed on
  the exact frozen 5,000-row subset; frozen SR MI values and equations are
  replayed rather than reselected.
- Direct reconstruction compares raw OLS with raw MSE-SR. Coordinate
  reconstruction compares OLS and MI-SR after each is separately calibrated
  with the same frozen procedure. The mixed table compares raw OLS, calibrated
  MI-SR, and raw MSE-SR.
- The renderer requires the conditioned `raw64` and `physical_o1_64` OLS
  coefficients and intercepts to agree to `rtol=1e-10, atol=1e-12`. They pass
  and therefore constitute one affine-invariance check, not independent wins.

### How OLS recovers the −2 direction

The `logamp64` design matrix contains the six separate columns
`[omega_b, omega_cdm, H0, tau, ln10As, n_s]`, where
`ln10As = ln(10^10 A_s)`. It does **not** contain the engineered combination
`ln10As - 2*tau`, and the two coefficients are not tied or constrained.
TT z2 and TT+EE z5 are the previously designated amplitude latents; they were
not selected by scanning the new T2 results for ratios closest to −2.

For numerical conditioning, the audit fits

`z_hat = alpha + sum_j beta_j (x_j - mean_j) / scale_j`.

It then returns to the input-arm basis using
`b_j = beta_j / scale_j` and
`a = alpha - sum_j beta_j mean_j / scale_j`. The diagnostic ratio must use
these arm-basis partial coefficients, not the standardized coefficients:

`r = b_tau / b_ln10As
    = (beta_tau / scale_tau) / (beta_ln10As / scale_ln10As)`.

The two fitted affine equations are:

```text
TT z2:
z2_hat = -22.72689191
         + 90.93866607 omega_b - 33.07432386 omega_cdm
         - 0.05472624 H0 - 16.65269993 tau
         + 8.41669346 ln10As + 4.13710990 n_s

TT+EE z5:
z5_hat = -25.31645702
         + 51.70291283 omega_b - 26.39414435 omega_cdm
         - 0.02943715 H0 - 17.90260000 tau
         + 8.96590424 ln10As + 3.41974106 n_s
```

Thus their amplitude-dependent pieces factor as

```text
TT z2:    8.41669346 * (ln10As - 1.97853231 tau)
TT+EE z5: 8.96590424 * (ln10As - 1.99674227 tau)
```

Because
`ln10As - 2*tau = ln(10^10 A_s) - 2*tau
                  = constant + ln(A_s exp(-2*tau))`,
the fitted coefficient ratios reproduce the familiar screened-amplitude
direction. OLS therefore does not symbolically invent a composite expression;
it estimates two unconstrained partial slopes whose ratio exposes the same
direction after the fit. The ratios are conditional on the other four
cosmological inputs in a six-input regression. They do not prove that the
entire latent depends only on this one direction or that OLS recovered the full
multiplicative original-basis formula.

| Run and latent | `b_tau` | `b_ln10As` | Ratio | T0-fit R2 | T0-val R2 | T2 raw NMSE % | T2 raw MI |
|---|---:|---:|---:|---:|---:|---:|---:|
| TT z2 | -16.65269993 | 8.41669346 | -1.97853231 | 0.9995721 | 0.9995864 | 0.0444213 | 3.99995±0.01478 |
| TT+EE z5 | -17.90260000 | 8.96590424 | -1.99674227 | 0.9995650 | 0.9996086 | 0.0451330 | 4.04152±0.01188 |

Both standardized designs have condition number 1.02093, so the ratios are not
an ill-conditioned least-squares artifact. The coefficients are fixed entirely
from T0-fit: T1 calibration and T2 evaluation do not alter them. T1 raw R2 is
0.9995589 for TT z2 and 0.9995549 for TT+EE z5; the corresponding five-fold
calibration diagnostic R2 values are 0.9987148 and 0.9989572. No uncertainty
interval was fitted for either coefficient ratio, so closeness to −2 is a
structural diagnostic rather than a formal test of exact equality. The TT and
TT+EE ratios differ from −2 by 1.073% and 0.163%, respectively.

This extension is tier-isolated but post-hoc: it was designed after T2 had
already been used by the preceding frozen comparison. Its fit/calibrate/confirm
staging prevents additional within-extension leakage, but it is not a
preregistered test on a never-before-seen holdout. The near−2 values reproduce
earlier T1 OLS ratios on the same trained models and dataset across tiers; they
are not an independent-dataset replication.

### Aggregate extension results

| Input arm | Median MI-SR MI > matched OLS | Direct raw-NMSE winners (OLS / MSE-SR) | Calibrated coordinate-NMSE winners (OLS / MI-SR) | Mixed-pipeline winners (OLS / MI-SR / MSE-SR) |
|---|---:|---:|---:|---:|
| `raw64` | 5 / 11 | 9 / 2 | 6 / 5 | 9 / 0 / 2 |
| `physical_o1_64` | 7 / 11 | 6 / 5 | 6 / 5 | 6 / 1 / 4 |
| `logamp64` | 6 / 11 | 7 / 4 | 7 / 4 | 7 / 1 / 3 |

The coordinate-matched `logamp64` descriptive comparison reverses the
unmatched diagnostic: once OLS uses the same amplitude coordinate as SR, OLS
wins 7 of 11 latents and SR wins 4 of 11 in the mixed comparison, rather than
the earlier apparent 5-to-6 split. OLS also wins 7-to-4 in each like-for-like
reconstruction comparison: raw OLS versus raw MSE-SR and calibrated OLS versus
calibrated MI-SR. Median MI-SR GMM-MI is higher for 6 of 11 `logamp64`
latents, but that descriptive point-estimate count is neither a significance
result nor a general predictive advantage.

For each latent and frozen search seed, the audit also forms a 95% normal
paired-row confidence interval for
`NMSE(SR) - NMSE(OLS)`. Positive intervals favor OLS.

| Input arm | Direct CI verdicts (OLS lower / SR lower / inconclusive) | Calibrated CI verdicts (OLS lower / SR lower / inconclusive) |
|---|---:|---:|
| `raw64` | 36 / 19 / 0 | 31 / 22 / 2 |
| `physical_o1_64` | 20 / 31 / 3 [^matched-invalid] | 24 / 30 / 1 |
| `logamp64` | 33 / 21 / 1 | 35 / 20 / 0 |

These are unadjusted, per-seed normal row-CI verdicts conditional on the frozen
fits and calibrators and the observed T2 NMSE denominator. They omit search-,
training-, and calibration-fit uncertainty and are not independent
replications or a pooled global significance test. The raw and physical OLS
predictors pass the required affine-invariance check to numerical tolerance;
those two arms are therefore one OLS invariance check, not two independent
pieces of evidence. Their differing winner counts arise from the arm-specific
SR equations. `logamp64` is the genuinely different affine model. Effects are
heterogeneous across latents and arms; the audit formally establishes neither
global OLS superiority nor equivalence.

The coordinate-matched log-amplitude OLS yields amplitude-direction diagnostic
ratios `b_tau / b_ln10As = -1.9785` for TT z2 and `-1.9967` for TT+EE z5.
No coefficient-ratio uncertainty is estimated, so these are diagnostics rather
than formal tests of an exact −2 coefficient. All 33 matched-OLS GMM-MI
evaluations are valid. Two frozen arm-specific MSE-SR MI replays are invalid,
as recorded in the confirmation artifacts, and are excluded from the
corresponding valid-only MI summaries.

[^matched-invalid]: One TT+EE physical-arm direct contrast (z0, MSE-SR seed 4)
    is invalid because only 93.116% of its T2 predictions are finite, so this
    row contains 54 rather than 55 valid direct verdicts.

### Full per-latent T2 confirmation results

These tables copy the complete coordinate-matched confirmation view into this
record. Every SR metric is the median [minimum, maximum] over valid frozen
search seeds. In a Delta cell, the first value and bracket summarize up to five
valid seedwise point estimates of `NMSE(SR) - NMSE(OLS)` in percentage points;
they are not a confidence interval. `OLS/SR/inc` separately counts the valid
seedwise paired-row 95% CI verdicts. Positive Delta favors OLS. OLS MI is the
point estimate ± its GMM bootstrap error; MI-SR MI is median [minimum, maximum].

#### `raw64`

| Latent | OLS raw NMSE % | MSE-SR raw NMSE % | Direct Delta % | OLS calibrated NMSE % | MI-SR calibrated NMSE % | Calibrated Delta % | OLS MI | MI-SR MI |
|---|---:|---:|---|---:|---:|---|---:|---:|
| TT z0 | 0.186 | 0.227 [0.159,0.470] | +0.041 [-0.027,+0.284]; OLS/SR/inc=3/2/0 | 0.213 | 0.191 [0.128,0.214] | -0.022 [-0.085,+0.001]; OLS/SR/inc=0/4/1 | 3.312±0.014 | 3.278 [3.239,3.504] |
| TT z1 | 1.402 | 1.729 [1.195,2.990] | +0.327 [-0.207,+1.589]; OLS/SR/inc=3/2/0 | 1.480 | 1.710 [1.552,2.129] | +0.230 [+0.072,+0.649]; OLS/SR/inc=5/0/0 | 2.312±0.014 | 2.304 [2.197,2.324] |
| TT z2 | 0.099 | 0.243 [0.054,0.572] | +0.144 [-0.045,+0.473]; OLS/SR/inc=4/1/0 | 0.195 | 0.163 [0.133,0.186] | -0.032 [-0.061,-0.009]; OLS/SR/inc=0/5/0 | 3.521±0.013 | 3.748 [3.596,4.098] |
| TT z3 | 0.214 | 0.230 [0.201,0.508] | +0.016 [-0.013,+0.294]; OLS/SR/inc=4/1/0 | 0.243 | 0.268 [0.256,0.274] | +0.025 [+0.013,+0.031]; OLS/SR/inc=5/0/0 | 3.122±0.014 | 3.102 [3.095,3.136] |
| TT z4 | 0.054 | 0.152 [0.111,0.489] | +0.099 [+0.057,+0.435]; OLS/SR/inc=5/0/0 | 0.160 | 0.200 [0.187,0.216] | +0.040 [+0.027,+0.056]; OLS/SR/inc=5/0/0 | 3.869±0.011 | 3.631 [3.469,3.687] |
| TT+EE z0 | 3.949 | 4.139 [3.979,5.931] | +0.190 [+0.030,+1.982]; OLS/SR/inc=5/0/0 | 3.950 | 4.989 [4.501,5.341] | +1.039 [+0.551,+1.391]; OLS/SR/inc=5/0/0 | 1.724±0.015 | 1.762 [1.724,1.797] |
| TT+EE z1 | 0.097 | 0.181 [0.098,0.935] | +0.084 [+0.001,+0.838]; OLS/SR/inc=5/0/0 | 0.146 | 0.154 [0.154,0.193] | +0.008 [+0.008,+0.047]; OLS/SR/inc=5/0/0 | 3.723±0.010 | 3.693 [3.442,3.693] |
| TT+EE z2 | 0.173 | 0.186 [0.155,0.911] | +0.014 [-0.017,+0.738]; OLS/SR/inc=3/2/0 | 0.211 | 0.226 [0.211,0.228] | +0.015 [-0.000,+0.017]; OLS/SR/inc=4/0/1 | 3.264±0.014 | 3.239 [3.235,3.265] |
| TT+EE z3 | 0.311 | 0.249 [0.208,0.294] | -0.062 [-0.102,-0.017]; OLS/SR/inc=0/5/0 | 0.369 | 0.306 [0.291,0.322] | -0.063 [-0.078,-0.047]; OLS/SR/inc=0/5/0 | 2.978±0.014 | 3.136 [3.114,3.182] |
| TT+EE z4 | 4.283 | 1.217 [1.084,2.557] | -3.067 [-3.199,-1.726]; OLS/SR/inc=0/5/0 | 4.162 | 1.409 [1.226,5.486] | -2.753 [-2.935,+1.324]; OLS/SR/inc=1/4/0 | 1.844±0.013 | 2.307 [1.898,2.358] |
| TT+EE z5 | 0.115 | 0.453 [0.110,0.574] | +0.338 [-0.005,+0.459]; OLS/SR/inc=4/1/0 | 0.168 | 0.123 [0.117,0.183] | -0.045 [-0.051,+0.015]; OLS/SR/inc=1/4/0 | 3.550±0.014 | 3.918 [3.435,3.960] |

#### `physical_o1_64`

| Latent | OLS raw NMSE % | MSE-SR raw NMSE % | Direct Delta % | OLS calibrated NMSE % | MI-SR calibrated NMSE % | Calibrated Delta % | OLS MI | MI-SR MI |
|---|---:|---:|---|---:|---:|---|---:|---:|
| TT z0 | 0.186 | 0.082 [0.060,0.180] | -0.104 [-0.126,-0.006]; OLS/SR/inc=0/5/0 | 0.213 | 0.178 [0.114,0.225] | -0.035 [-0.098,+0.012]; OLS/SR/inc=1/4/0 | 3.312±0.014 | 3.320 [3.230,3.631] |
| TT z1 | 1.402 | 1.507 [1.242,1.763] | +0.106 [-0.159,+0.361]; OLS/SR/inc=3/1/1 | 1.480 | 1.557 [1.532,1.853] | +0.077 [+0.051,+0.373]; OLS/SR/inc=5/0/0 | 2.312±0.014 | 2.285 [2.273,2.350] |
| TT z2 | 0.099 | 0.129 [0.094,0.167] | +0.031 [-0.005,+0.069]; OLS/SR/inc=4/1/0 | 0.195 | 0.182 [0.163,0.191] | -0.012 [-0.032,-0.003]; OLS/SR/inc=0/5/0 | 3.521±0.013 | 3.628 [3.567,3.716] |
| TT z3 | 0.214 | 0.166 [0.159,0.194] | -0.048 [-0.055,-0.020]; OLS/SR/inc=0/5/0 | 0.243 | 0.195 [0.179,0.203] | -0.048 [-0.064,-0.040]; OLS/SR/inc=0/5/0 | 3.122±0.014 | 3.308 [3.292,3.406] |
| TT z4 | 0.054 | 0.096 [0.054,0.298] | +0.042 [+0.001,+0.244]; OLS/SR/inc=4/0/1 | 0.160 | 0.183 [0.156,0.239] | +0.023 [-0.004,+0.079]; OLS/SR/inc=3/2/0 | 3.869±0.011 | 3.717 [3.528,3.983] |
| TT+EE z0 | 3.949 | 3.951 [3.467,4.028] | +0.002 [-0.482,+0.079]; OLS/SR/inc=2/1/1 | 3.950 | 4.778 [4.737,4.865] | +0.828 [+0.786,+0.915]; OLS/SR/inc=5/0/0 | 1.724±0.015 | 1.794 [1.790,1.806] |
| TT+EE z1 | 0.097 | 0.117 [0.063,0.251] | +0.021 [-0.034,+0.154]; OLS/SR/inc=4/1/0 | 0.146 | 0.169 [0.140,0.238] | +0.023 [-0.006,+0.091]; OLS/SR/inc=3/1/1 | 3.723±0.010 | 3.542 [3.455,3.776] |
| TT+EE z2 | 0.173 | 0.141 [0.124,0.156] | -0.032 [-0.049,-0.017]; OLS/SR/inc=0/5/0 | 0.211 | 0.228 [0.163,0.238] | +0.017 [-0.048,+0.027]; OLS/SR/inc=3/2/0 | 3.264±0.014 | 3.264 [3.200,3.392] |
| TT+EE z3 | 0.311 | 0.226 [0.193,0.247] | -0.085 [-0.118,-0.064]; OLS/SR/inc=0/5/0 | 0.369 | 0.276 [0.254,0.309] | -0.093 [-0.115,-0.060]; OLS/SR/inc=0/5/0 | 2.978±0.014 | 3.279 [3.086,3.293] |
| TT+EE z4 | 4.283 | 1.784 [1.379,2.712] | -2.499 [-2.904,-1.571]; OLS/SR/inc=0/5/0 | 4.162 | 1.378 [1.126,5.579] | -2.783 [-3.036,+1.417]; OLS/SR/inc=1/4/0 | 1.844±0.013 | 2.309 [2.085,2.408] |
| TT+EE z5 | 0.115 | 0.121 [0.064,0.210] | +0.006 [-0.051,+0.094]; OLS/SR/inc=3/2/0 | 0.168 | 0.171 [0.155,0.189] | +0.003 [-0.014,+0.021]; OLS/SR/inc=3/2/0 | 3.550±0.014 | 3.560 [3.452,3.703] |

#### `logamp64`

| Latent | OLS raw NMSE % | MSE-SR raw NMSE % | Direct Delta % | OLS calibrated NMSE % | MI-SR calibrated NMSE % | Calibrated Delta % | OLS MI | MI-SR MI |
|---|---:|---:|---|---:|---:|---|---:|---:|
| TT z0 | 0.186 | 0.180 [0.129,0.203] | -0.006 [-0.057,+0.017]; OLS/SR/inc=2/3/0 | 0.212 | 0.160 [0.139,0.216] | -0.052 [-0.073,+0.004]; OLS/SR/inc=1/4/0 | 3.301±0.014 | 3.386 [3.154,3.466] |
| TT z1 | 1.390 | 1.402 [1.177,1.462] | +0.012 [-0.213,+0.072]; OLS/SR/inc=2/2/1 | 1.469 | 1.854 [1.786,2.027] | +0.385 [+0.317,+0.559]; OLS/SR/inc=5/0/0 | 2.322±0.015 | 2.276 [2.241,2.379] |
| TT z2 | 0.044 | 0.311 [0.109,0.366] | +0.266 [+0.064,+0.322]; OLS/SR/inc=5/0/0 | 0.140 | 0.173 [0.130,0.287] | +0.033 [-0.010,+0.146]; OLS/SR/inc=4/1/0 | 4.000±0.015 | 3.706 [3.252,4.194] |
| TT z3 | 0.214 | 0.221 [0.179,0.240] | +0.007 [-0.035,+0.025]; OLS/SR/inc=3/2/0 | 0.243 | 0.248 [0.238,0.266] | +0.005 [-0.006,+0.023]; OLS/SR/inc=4/1/0 | 3.121±0.014 | 3.162 [3.110,3.202] |
| TT z4 | 0.040 | 0.261 [0.105,0.789] | +0.221 [+0.065,+0.748]; OLS/SR/inc=5/0/0 | 0.148 | 0.199 [0.184,0.317] | +0.051 [+0.036,+0.169]; OLS/SR/inc=5/0/0 | 4.040±0.012 | 3.583 [3.182,3.687] |
| TT+EE z0 | 3.954 | 4.120 [4.054,4.183] | +0.167 [+0.100,+0.230]; OLS/SR/inc=5/0/0 | 3.955 | 5.165 [4.924,5.350] | +1.209 [+0.969,+1.395]; OLS/SR/inc=5/0/0 | 1.722±0.014 | 1.781 [1.753,1.791] |
| TT+EE z1 | 0.095 | 0.095 [0.057,0.427] | +0.000 [-0.038,+0.332]; OLS/SR/inc=3/2/0 | 0.145 | 0.126 [0.124,0.151] | -0.019 [-0.021,+0.007]; OLS/SR/inc=2/3/0 | 3.740±0.011 | 3.844 [3.646,3.873] |
| TT+EE z2 | 0.171 | 0.149 [0.113,0.193] | -0.021 [-0.058,+0.022]; OLS/SR/inc=2/3/0 | 0.209 | 0.223 [0.206,0.229] | +0.014 [-0.003,+0.020]; OLS/SR/inc=4/1/0 | 3.272±0.014 | 3.259 [3.237,3.280] |
| TT+EE z3 | 0.311 | 0.236 [0.156,0.332] | -0.075 [-0.155,+0.021]; OLS/SR/inc=1/4/0 | 0.369 | 0.314 [0.248,0.360] | -0.055 [-0.121,-0.009]; OLS/SR/inc=0/5/0 | 2.979±0.014 | 3.141 [3.068,3.331] |
| TT+EE z4 | 4.179 | 1.368 [1.118,1.598] | -2.811 [-3.062,-2.581]; OLS/SR/inc=0/5/0 | 4.062 | 1.438 [1.013,3.321] | -2.623 [-3.048,-0.740]; OLS/SR/inc=0/5/0 | 1.839±0.013 | 2.327 [2.258,2.424] |
| TT+EE z5 | 0.045 | 0.104 [0.055,0.172] | +0.059 [+0.010,+0.127]; OLS/SR/inc=5/0/0 | 0.111 | 0.134 [0.117,0.285] | +0.022 [+0.006,+0.174]; OLS/SR/inc=5/0/0 | 4.042±0.012 | 3.823 [3.237,3.956] |

### Artifact, execution, and validation record

- The immutable per-cell outputs are
  `results/<run>/coordinate_matched_ols_v1/<arm>/{fit,calibration,confirmation}.json`:
  18 JSON artifacts across six run/arm cells.
- The canonical aggregate is
  `experiments/coordinate_matched_ols_v1.json`; the generated detailed report
  is `docs/coordinate_matched_ols_v1.md`.
- The aggregate was rendered at `2026-08-31T13:13:54.516266+00:00`. Its
  `render_sha256` is
  `86a179276fb1dde21be50e6f6a77eb070db41736bc88f82f15ee140ac76ca23d`.
- Every confirmation uses the common T2 subset hash
  `758b51fd7e9301ab5bf35765776a1520e25f1a77952db125d9e0ef052e5b6fd2`
  with exactly 5,000 positions.
- All 18 internal artifact digests verify. The retrieved files match the
  Lightning copies byte for byte. The renderer's raw/physical affine
  equivalence check passes.
- All 33 matched-OLS GMM-MI estimates are valid. Two frozen MSE-SR MI replays
  are invalid: TT+EE `logamp64` z4 seed 3 has finite predictions but a
  non-finite GMM-MI result, and TT+EE `physical_o1_64` z0 seed 4 has
  non-finite predictions on the matched subset. The latter is also the one
  invalid direct paired contrast documented above.
- The audit ran scheduler-free on a CPU Lightning Studio with BLAS thread
  counts fixed to one. The focused suite passes 17/17 on Lightning; the full
  audit and related regression selection passes 67/67 locally.
- Implementation and launch entry points are
  `scripts/audit_coordinate_matched_ols.py` and
  `hpc/lightning/run_coordinate_matched_ols_audit.sh`. The wrapper enforces
  `fit -> calibrate -> confirm -> render` and writes only the additive study
  namespace.

## Canonical wording for downstream use

> On two fixed seed-42 VAE checkpoints, blind symbolic regression repeatedly
> generated physically meaningful symbolic hypotheses, including expressions
> aligned with the screened-amplitude direction and recurrent nonlinear
> residual coordinates. A coordinate-matched audit nevertheless finds no
> consistent predictive advantage over exact six-input OLS, and OLS reproduces
> the near-`-2` conditional amplitude direction. The evidence therefore
> supports SR as a structural, hypothesis-generating probe on these
> checkpoints—not its necessity, uniqueness, or general reconstruction
> superiority. SR retains clear latent-specific successes, especially TT+EE
> z4; broader claims require independent VAE seeds and fresh confirmation
> data.

The current T2 evidence is frozen. Further work on these rows is diagnostic;
it cannot convert this post-hoc audit into a fresh confirmation.
