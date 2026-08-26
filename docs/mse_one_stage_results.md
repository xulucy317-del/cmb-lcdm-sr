# One-stage MSE latent reconstruction — combined results

**Both checkpoints in one place.** Generated 2026-08-26 from
`experiments/mse_one_stage_sr_lcdm_tt_beta3e-4.{json,md}` and
`experiments/mse_one_stage_sr_lcdm_tt_ee_lowl.{json,md}`, which remain the
authoritative per-checkpoint artifacts. Protocol: `experiments/mse_one_stage_sr_plan.md`
(with execution amendments A1 and A2). Execution record:
the `lightning_execution` block of `experiments/mse_one_stage_execution_provenance.json`.

## 0. Scope boundary — read this first

This is a **latent reconstruction and compression** study, not a replacement for
the blind MI-discovery result. MSE is deliberately calibration-sensitive: unlike
GMM-MI it does not identify a coordinate up to an arbitrary bijection, it rewards
the numerical scale, offset and shape that reproduce `mu_k`. Nothing here changes
the frozen discovery protocol, any latent card, or any status in
`docs/discovery_roadmap.md`.

Two further boundaries, both pre-registered in the plan and both load-bearing for
how §5 below reads:

* the hierarchy comparison uses a single canonical denominator and is therefore
  labelled **unpaired**;
* direct and hierarchical *complexities* are not comparable — the hierarchy's
  `h` and `g` are flexible non-symbolic calibrators whose cost is absent from
  every PySR node count quoted here.

## 1. What was run

For each of the 11 scalar encoder means, from the same six raw ΛCDM inputs and
with no residual target, no `f1hat` input and no post-SR spline:

* PySR 1.5.10 with an explicit elementwise squared-error loss, 5000 T0 samples,
  200 iterations, 15 populations, seeds 0–4, at `maxsize ∈ {20, 30, 40}`
  — **165 searches**;
* protocol-identical MSE shuffled-target controls on both amplitude latents,
  seeds 0–2 at the endpoint budgets — **12 controls**;
* selection on the untouched 1000-row T0 validation block, then `select` (T0),
  `calibrate` (T1) and a single `confirm` (T2), each verifying the previous
  stage's digest before running.

165/165 searches and 12/12 controls completed; 141 task attempts, **zero
failures and zero invalid reports**. Tier contract as always:
T0 `[0:5000)`, T1 `[5000:25000)`, T2 `[25000:50000)`.

## 2. Headline

**No latent reached `one-stage replacement`.** Six are classified
`partial absorption`, five `no capacity gain`. The known `f2` was absorbed in
**0 of 11** latents. One large expression does not subsume the hierarchy's
second stage.

Two results qualify the reconstruction framing itself, and both are in §5
rather than buried: the apparent H1 landslide is mostly a calibration artifact,
and a plain six-input linear model beats the best symbolic expression in 8 of
11 latents.

## 3. Decision ledger

Rules exactly as frozen in §6 of the plan; `U95(x) = mean + 2.132·sd/√5` over
the five seed-paired values, seeds (not rows) being the replication unit.

| model | latent | H1 objective | H2 capacity | H3 vs two-stage | known `f2` absorbed | R_SR | saturated | classification |
|---|---|---|---|---|---|---|---|---|
| TT | z0 | **pass** (0.005) | fail (1.022) | **pass** (0.43) | **fail** (1/5) | 1.00 | no | no capacity gain |
| TT | z1 | **pass** (0.095) | **pass** (0.939) | fail (3.44) | **fail** (1/5) | 1.00 | yes | partial absorption |
| TT | z2 | **pass** (0.342) | fail (13.190) | fail (25.81) | **fail** (0/5) | 0.80 | no | no capacity gain |
| TT | z3 | **pass** (0.005) | fail (1.430) | **pass** (0.29) | **fail** (0/5) | 1.00 | no | no capacity gain |
| TT | z4 | **pass** (0.124) | **pass** (0.057) | fail (1.18) | **fail** (0/5) | 1.00 | yes | partial absorption |
| TT+EE | z0 | **pass** (0.058) | fail (1.505) | fail (1.48) | **fail** (0/5) | 1.00 | no | no capacity gain |
| TT+EE | z1 | **pass** (0.021) | **pass** (0.949) | fail (3.49) | **fail** (0/5) | 1.00 | yes | partial absorption |
| TT+EE | z2 | **pass** (0.010) | fail (1.118) | **pass** (0.92) | **fail** (0/5) | 1.00 | no | no capacity gain |
| TT+EE | z3 | **pass** (0.005) | **pass** (0.718) | **pass** (0.34) | **fail** (0/5) | 1.00 | no | partial absorption |
| TT+EE | z4 | **pass** (0.272) | **pass** (0.929) | **pass** (0.76) | **fail** (0/5) | 1.00 | no | partial absorption |
| TT+EE | z5 | **pass** (0.038) | **pass** (0.438) | fail (1.52) | **fail** (0/5) | 1.00 | yes | partial absorption |

Totals: H1 11/11, H2 6/11, H3 5/11, absorption 0/11, stability 11/11,
saturation 4/11.

## 4. The known-`f2` result, and why the mechanism matters more than the verdict

The pre-specified test has two legs, and a seed passes only if **both** hold:
`R²_f2 ≤ 0.05` for a five-fold, 64-bin monotone `q(f2)` cross-fit on T1 and
refit on all of T1, **and** `MI(e_direct; f2)` no greater than its own
97.5th-percentile 39-permutation T2 null. No map or threshold is fitted on T2.

| model | latent | max `R²_f2` | R² leg pass | max MI / null | MI leg pass | both |
|---|---|---|---|---|---|---|
| TT | z0 | 0.1664 | 4/5 | 35× | 1/5 | 1/5 |
| TT | z1 | 0.1625 | 3/5 | 23× | 1/5 | 1/5 |
| TT | z2 | 0.2065 | 2/5 | 140× | 0/5 | 0/5 |
| TT | z3 | 0.0738 | 3/5 | 22× | 0/5 | 0/5 |
| TT | z4 | 0.0875 | 4/5 | 10× | 0/5 | 0/5 |
| TT+EE | z0 | 0.1468 | 2/5 | 62× | 0/5 | 0/5 |
| TT+EE | z1 | 0.3617 | 2/5 | 51× | 0/5 | 0/5 |
| TT+EE | z2 | 0.0548 | 4/5 | 11× | 0/5 | 0/5 |
| TT+EE | z3 | 0.0400 | 5/5 | 13× | 0/5 | 0/5 |
| TT+EE | z4 | 0.0572 | 2/5 | 30× | 0/5 | 0/5 |
| TT+EE | z5 | 0.1261 | 1/5 | 19× | 0/5 | 0/5 |
| **total** | | | **32/55** | | **2/55** | **2/55** |

**The two legs disagree systematically.** The variance leg passes in 32 of 55
latent–seed audits — the direct expression really does remove most of what a
monotone function of `f2` can predict about its own residual, often leaving
under 5 % of residual variance explainable. The information leg passes twice.
Observed MI runs **10× to 140×** the 97.5th-percentile permutation null.

Read plainly: a single large expression *launders* the second stage rather than
absorbing it. It removes `f2`'s monotone-predictable contribution while leaving
dependence that a distribution-free MI test detects at overwhelming margins.
That is a sharper statement than "one stage failed", and it is the result worth
carrying forward.

A2 scope reminder: this is the **only** newly computed MI in the experiment, and
no global residual-termination claim is made. Structure other than the known
`f2` may remain and was not tested.

## 5. Two findings that qualify the reconstruction framing

### 5.1 H1's raw margin is mostly a calibration artifact

Raw, uncalibrated T2 NMSE makes MSE search look 3×–200× better than the GMM-MI
front. That number is close to meaningless, because **MI-selected expressions
carry no numerical calibration by construction** — `mi20-mse` scores NMSE ≈ 1.0,
i.e. no better than predicting the fit mean, in 10 of 11 latents.

The plan pre-specified the fair comparison: fit the *same* monotone calibration
family on T1 for the frozen `mi20-mse` and `mse20` winners, then compare
calibrated T2 errors. Median over five seeds:

| model | latent | `mse20` raw | `mse20` calibrated | `mi20-mse` raw | `mi20-mse` calibrated | calibrated ratio |
|---|---|---|---|---|---|---|
| TT | z0 | 0.00469 | 0.00496 | 0.99857 | 0.01605 | 0.31 |
| TT | z1 | 0.08681 | 0.08718 | 1.00040 | 0.02985 | **2.92** |
| TT | z2 | 0.10986 | 0.10677 | 1.00000 | 0.52968 | 0.20 |
| TT | z3 | 0.00299 | 0.00307 | 0.95653 | 0.31279 | 0.01 |
| TT | z4 | 0.11355 | 0.11461 | 1.00003 | 0.15570 | 0.74 |
| TT+EE | z0 | 0.04358 | 0.04336 | 1.00079 | 0.07598 | 0.57 |
| TT+EE | z1 | 0.01852 | 0.01848 | 0.99936 | 0.03300 | 0.56 |
| TT+EE | z2 | 0.00889 | 0.00924 | 0.99132 | 0.00944 | 0.98 |
| TT+EE | z3 | 0.00332 | 0.00389 | 0.99543 | 0.00673 | 0.58 |
| TT+EE | z4 | 0.04173 | 0.04052 | 1.00005 | 0.02730 | **1.48** |
| TT+EE | z5 | 0.02652 | 0.02700 | 1.00001 | 0.47484 | 0.06 |

Once scale and offset are treated symmetrically the MSE objective wins **9/11,
not 11/11**, and TT z1 and EE z4 reverse outright. The honest statement is that
MSE search finds *better-calibrated* expressions, not uniformly better
*coordinates*: some GMM-MI front members are excellent coordinates that merely
need a monotone map (TT z0 calibrates from 0.9986 to 0.0161).

This diagnostic cannot carry a success decision, and does not — the frozen H1
rule uses the uncalibrated endpoint. It is reported because quoting the raw
margin alone would misrepresent what the objective actually bought.

### 5.2 A six-input linear model beats the symbolic winner in 8 of 11 latents

The plan keeps a plain OLS model in the six raw inputs as a reconstruction
baseline. Fit on T0-fit only, scored on T2:

| model | latent | 6-input OLS | `mse40` (median) | winner |
|---|---|---|---|---|
| TT | z0 | 0.00186 | 0.00398 | OLS |
| TT | z1 | 0.01402 | 0.01840 | OLS |
| TT | z2 | 0.00099 | 0.01195 | OLS |
| TT | z3 | 0.00214 | 0.00250 | OLS |
| TT | z4 | 0.00054 | 0.00299 | OLS |
| TT+EE | z0 | 0.03949 | 0.06430 | OLS |
| TT+EE | z1 | 0.00097 | 0.01638 | OLS |
| TT+EE | z2 | 0.00173 | 0.00167 | `mse40` |
| TT+EE | z3 | 0.00311 | 0.00209 | `mse40` |
| TT+EE | z4 | 0.04283 | 0.02662 | `mse40` |
| TT+EE | z5 | 0.00115 | 0.00415 | OLS |

Seven least-squares coefficients outperform a 40-node symbolic expression in
8/11 latents, sometimes by an order of magnitude (TT z2: 0.00099 vs 0.01195).
The latents are largely linear in the six parameters, and a stochastic search
over a 40-node space with in-search constant optimisation does not reliably
match exact least squares on the criterion it is optimising.

**Consequence for the write-up.** As *reconstruction*, direct symbolic
regression is not the right tool here and should not be sold as one. The
experiment's value is the structural finding of §4 — what the residual still
contains — not reconstruction accuracy per se.

## 6. Full reconstruction table

T2 NMSE, median over five seeds; hierarchy rows are the frozen T1-fitted maps
re-evaluated on the same T2 rows.

| model | latent | `mi20-mi` | `mi20-mse` | `mse20` | `mse30` | `mse40` | `h(f1)` | `h+g` | interaction | 6-input OLS |
|---|---|---|---|---|---|---|---|---|---|---|
| TT | z0 | 57.27995 | 0.99857 | 0.00469 | 0.00408 | 0.00398 | 0.09495 | 0.01093 | 0.01094 | 0.00186 |
| TT | z1 | 812.05832 | 1.00040 | 0.08681 | 0.03598 | 0.01840 | 0.09510 | 0.01887 | 0.01961 | 0.01402 |
| TT | z2 | 542.52473 | 1.00000 | 0.10986 | 0.04972 | 0.01195 | 0.05260 | 0.00735 | 0.00742 | 0.00099 |
| TT | z3 | 1.04717 | 0.95653 | 0.00299 | 0.00256 | 0.00250 | 0.08419 | 0.01160 | 0.01168 | 0.00214 |
| TT | z4 | 61.71592 | 1.00003 | 0.11355 | 0.00405 | 0.00299 | 0.07918 | 0.00731 | 0.00535 | 0.00054 |
| TT+EE | z0 | 76280.71998 | 1.00079 | 0.04358 | 0.04461 | 0.06430 | 0.07598 | 0.04565 | 0.04702 | 0.03949 |
| TT+EE | z1 | 73.98375 | 0.99936 | 0.01852 | 0.01864 | 0.01638 | 0.06838 | 0.00538 | 0.00538 | 0.00097 |
| TT+EE | z2 | 113.80700 | 0.99132 | 0.00889 | 0.00233 | 0.00167 | 0.07124 | 0.00244 | 0.00287 | 0.00173 |
| TT+EE | z3 | 22.88692 | 0.99543 | 0.00332 | 0.00277 | 0.00209 | 0.06452 | 0.00777 | 0.00777 | 0.00311 |
| TT+EE | z4 | 1.00019 | 1.00005 | 0.04173 | 0.02800 | 0.02662 | 0.04357 | 0.04216 | 0.04216 | 0.04283 |
| TT+EE | z5 | 396.37415 | 1.00001 | 0.02652 | 0.00596 | 0.00415 | 0.08886 | 0.00725 | 0.00725 | 0.00115 |

The `mi20-mi` column is uninterpretable as accuracy (values up to 7.6 × 10⁴)
and is shown only to make the calibration point of §5.1 concrete: MI selection
optimises a bijection-invariant criterion and has no reason to return a
numerically calibrated expression.

## 7. Controls

Protocol-identical MSE searches on independently permuted targets, selected by
shuffled-target validation MSE, scored on T2 against both targets:

| model | latent | budget | shuffle seed | R² vs true target | R² vs its own shuffled target |
|---|---|---|---|---|---|
| TT | z2 | ms20 | 0 | -0.0022 | -0.0011 |
| TT | z2 | ms20 | 1 | +0.0048 | -0.0004 |
| TT | z2 | ms20 | 2 | -0.0001 | -0.0001 |
| TT | z2 | ms40 | 0 | -0.0057 | -0.0000 |
| TT | z2 | ms40 | 1 | +0.0048 | -0.0004 |
| TT | z2 | ms40 | 2 | -0.0001 | -0.0001 |
| TT+EE | z5 | ms20 | 0 | +0.0005 | -0.0021 |
| TT+EE | z5 | ms20 | 1 | +0.0037 | -0.0004 |
| TT+EE | z5 | ms20 | 2 | +0.0051 | -0.0042 |
| TT+EE | z5 | ms40 | 0 | -0.0006 | -0.0012 |
| TT+EE | z5 | ms40 | 1 | +0.0037 | -0.0004 |
| TT+EE | z5 | ms40 | 2 | +0.0020 | -0.0047 |

Every control sits within |R²| ≤ 0.006 of zero against both targets, at both
budgets. Lifting the budget from 20 to 40 buys a shuffled target nothing —
the capacity gains in §3 are not an artifact of a larger search space. These
are diagnostics only; three permutations do not estimate any threshold.

## 8. Capacity, saturation, stability

* **Capacity (H2) passes 6/11.** TT z4 is decisive (`U95` 0.057); EE z5 (0.438)
  and EE z3 (0.718) follow. TT z0 (1.022) and EE z2 (1.118) miss narrowly.
  TT z2 fails at 13.190 — its seed spread is extreme, not a clean negative.
* **EE z0 is the one latent where capacity actively hurts** (T0 40/20 ratio
  1.17; T2 `U95` 1.505). It is also the latent this project has carried as
  unresolved since Phase 2, so this is consistent with, not new to, the record.
* **`mse30` need not be monotone and is not**: EE z5 runs 0.0265 → 0.0060 →
  0.0042 on T2 but its T0 selection tier was non-monotone. Reported, as the
  plan requires, without adjustment.
* **Budget saturation in 4/11** (TT z1, TT z4, EE z1, EE z5): at least 3/5
  `mse40` winners at complexity ≥ 38. Reported, **not** escalated —
  `maxsize > 40` was excluded from this experiment by design.
* **Symbolic stability 11/11.** `R_SR = 1.00` for ten latents, 0.80 for TT z2,
  all clearing the ≥ 0.8 rule. Stability is reported independently and cannot
  rescue a failed reconstruction criterion — and here it does not need to.
* **One-standard-error parsimony.** Common complexities land at 9–30 against
  winners up to 40, so most of the achievable accuracy is available well below
  the budget ceiling. Per-latent envelopes are in the per-checkpoint reports.

## 9. Limitations

1. **Calibration replaces coordinate discovery** — expected under MSE, and §5.1
   quantifies how much of the apparent H1 margin it accounts for.
2. **Direct and hierarchical complexity are not comparable.** The hierarchy's
   `h`/`g` calibrators are excluded from every node count here.
3. **The hierarchy comparison is unpaired.** A single canonical denominator is
   applied to all five direct seeds, as §6 of the plan permits and labels.
4. **No residual-completeness claim.** A2 removed the maximum-parameter MI
   audit; only the *known* `f2` was tested. Other structure may remain.
5. **T2 is held out from this search and selection procedure but is not
   globally pristine** with respect to earlier repository analyses.
6. **Thread-count and process-model deviations** between the first 36 CSD3
   reports and the remaining 129 are recorded in the provenance file. Search
   volume, operators, seeds and the budget ladder are unchanged.

## 10. Artifacts

| what | where |
|---|---|
| per-checkpoint results | `experiments/mse_one_stage_sr_lcdm_tt_beta3e-4.{json,md}`, `..._lcdm_tt_ee_lowl.{json,md}` |
| frozen selections (T0) | `results/<run>/mse_one_stage_selection_manifest.json` |
| T1 calibration contract | `results/<run>/mse_one_stage_calibration.json` |
| searches / controls | `results/<run>/mse_one_stage_ms{20,30,40}/`, `mse_one_stage_control_ms{20,40}/` |
| protocol | `experiments/mse_one_stage_sr_plan.md` |
| execution record | `lightning_execution` in `experiments/mse_one_stage_execution_provenance.json` |
| per-task ledger | `logs/mse_one_stage_pool_ledger_lightning.jsonl` |
