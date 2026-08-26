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

## 7. The recovered expressions

For each latent, the canonical direct form: the representative of the dominant
semantic cluster over the five `mse40` seeds, under the repository's frozen
equivalence rule. Every representative below **is** one of the five seed
winners — the lowest-complexity member of its cluster — not a re-derived form.
Ten of eleven latents cluster as a single form across all five seeds
(`R_SR = 1.00`); TT z2 splits 4 + 1 (`R_SR = 0.80`).

Each is shown against the two-stage account it was trying to replace: the
frozen interaction-aware `f1` and `f2`, and the canonical additive `f2` that
the absorption test of §4 actually probes. The contrast is the point — the
direct forms are an order of magnitude larger in node count and still do not
absorb the coordinate the 7-node `f2` carries.


### TT — `lcdm_tt_beta3e-4`

**z0** — no capacity gain; canonical form from seed 3, complexity 31, support {omega_b, omega_cdm, H0, tau, n_s}; cluster sizes [5], `R_SR` = 1.00

```text
direct (mse40)   (n_s*(H0 - 10.3037253854979*tau)*(-794.84454*omega_b - tau*(tau + 0.48297423) + 26.9960943926482) + 97.4718336308724*n_s - (H0 - 10.3037253854979*tau)*(26.5958377070186*omega_cdm + 7.42503470649822))/(n_s*(H0 - 10.3037253854979*tau))

two-stage f1     n_s/omega_b   (complexity 3)
two-stage f2     n_s*(H0 + 1311.2706*omega_cdm)   (complexity 7)
known f2 probed  n_s*(H0 + 1325.0747*omega_cdm)
```

**z1** — partial absorption; canonical form from seed 1, complexity 21, support {omega_b, omega_cdm, H0, ln10As, n_s}; cluster sizes [5], `R_SR` = 1.00

```text
direct (mse40)   7.2245064*log(H0*n_s**2*omega_b**2/(0.190415417128964*A_s*omega_b + 0.190415417128964*A_s - omega_b - 0.190415417128964*omega_cdm)**2) - 23.9643695428481 + 7.655731e-9/A_s

two-stage f1     H0**2*n_s**2*omega_b/(A_s*omega_cdm**2)   (complexity 10)
two-stage f2     omega_b*(tau - (n_s - omega_cdm)**4)/H0   (complexity 11)
known f2 probed  n_s/log(-H0/(tau - 0.44653893)) + omega_b
```

**z2** — no capacity gain; canonical form from seed 3, complexity 29, support {omega_b, omega_cdm, H0, tau, ln10As, n_s}; cluster sizes [4, 1], `R_SR` = 0.80

```text
direct (mse40)   (H0*n_s*(tau*(omega_b - omega_cdm) - 0.29783544) + H0*(omega_b - omega_cdm)*(4035209500.0*A_s - (A_s - 17.716805)*(3.247568*omega_b - tau) - 15.620946) + 278.70035*omega_b - 278.70035*omega_cdm)/(H0*(omega_b - omega_cdm))

two-stage f1     A_s/log(H0*(omega_cdm + tau))   (complexity 8)
two-stage f2     n_s**2*omega_b*tau/(omega_cdm*tau + 0.0003273979)   (complexity 10)
known f2 probed  n_s**2*omega_b*tau/(omega_cdm*tau + 0.00031008976)
```

**z3** — no capacity gain; canonical form from seed 3, complexity 22, support {omega_b, omega_cdm, H0, tau, n_s}; cluster sizes [5], `R_SR` = 1.00

```text
direct (mse40)   -0.0187756448561935*H0 + n_s*(omega_b + 31.98304) + 112.28677*omega_b + omega_cdm**2*(266.8151 - tau) - 35.57421

two-stage f1     n_s + omega_cdm   (complexity 3)
two-stage f2     (H0 + 89.375175)/(omega_b*omega_cdm)   (complexity 7)
known f2 probed  H0/(omega_b**2*omega_cdm**2)
```

**z4** — partial absorption; canonical form from seed 0, complexity 38, support {omega_b, omega_cdm, H0, tau, ln10As, n_s}; cluster sizes [5], `R_SR` = 1.00

```text
direct (mse40)   -0.0942166610105264*H0 + n_s**2 - (omega_b + tau)**2 + 3.3386119 + tau/omega_cdm - 0.001039371/(n_s*omega_b**2) + 6.85627267206176e-8/(A_s*H0*omega_cdm)

two-stage f1     A_s*H0**2*omega_cdm*exp(-2*tau)   (complexity 9)
two-stage f2     (n_s*tau + log(H0))/(n_s*omega_b)   (complexity 8)
known f2 probed  log(H0)/(n_s*omega_b)
```


### TT+EE — `lcdm_tt_ee_lowl`

**z0** — no capacity gain; canonical form from seed 3, complexity 25, support {omega_b, omega_cdm, H0, ln10As, n_s}; cluster sizes [5], `R_SR` = 1.00

```text
direct (mse40)   -13554076.368663*A_s*H0 + 0.126157322535035*H0 - omega_cdm + 10.005785 - 0.17647429/omega_b - 73.519005*omega_cdm/n_s

two-stage f1     omega_cdm/(H0*n_s*omega_b)   (complexity 7)
two-stage f2     -A_s*H0**2*(f1hat - 10.8708105)   (complexity 8)
known f2 probed  A_s*H0*omega_cdm/n_s
```

**z1** — partial absorption; canonical form from seed 4, complexity 35, support {omega_b, omega_cdm, H0, tau, ln10As, n_s}; cluster sizes [5], `R_SR` = 1.00

```text
direct (mse40)   0.7039488*H0/log(omega_cdm**2) - tau*log(omega_cdm) + tau + 155.3249*exp(omega_b) - 146.783972485304 + 9.963138715392/log(omega_cdm**2) + 3.5641272e-9*n_s/A_s

two-stage f1     H0**2*omega_cdm   (complexity 4)
two-stage f2     A_s*exp(-2*tau)/omega_b**2   (complexity 7)
known f2 probed  A_s*exp(-2*tau)/omega_b**2
```

**z2** — no capacity gain; canonical form from seed 2, complexity 33, support {omega_b, omega_cdm, H0, ln10As, n_s}; cluster sizes [5], `R_SR` = 1.00

```text
direct (mse40)   (omega_cdm + 0.8767359)*(H0**4*(0.0336795864254562*H0 - 1)**4*(-23.995014*n_s + 652.982386720542*omega_b + 25.995014*omega_cdm + 5.247814) + 1.13934851545217e+17*(A_s*H0**2*(0.0336795864254562*H0 - 1)**2 + 9.63662046566921e-7)**2)/(H0**4*(0.0336795864254562*H0 - 1)**4)

two-stage f1     omega_b/n_s**2   (complexity 4)
two-stage f2     log(A_s*omega_b*(n_s*omega_cdm - 0.024653804)**2)   (complexity 11)
known f2 probed  n_s*(A_s + 1.03524857872784e-5*omega_b*omega_cdm**2)
```

**z3** — partial absorption; canonical form from seed 4, complexity 26, support {omega_b, omega_cdm, H0, n_s}; cluster sizes [5], `R_SR` = 1.00

```text
direct (mse40)   (-0.000504265*H0 + omega_b*(28.1700678693762*n_s - 249.838974272061*omega_cdm**2 + 111.862035092849*omega_cdm - 27.9030254036452) - 0.15781781)/omega_b

two-stage f1     log(omega_b)/(n_s + omega_cdm)   (complexity 6)
two-stage f2     H0/omega_cdm**2   (complexity 4)
known f2 probed  H0/omega_cdm**2
```

**z4** — partial absorption; canonical form from seed 0, complexity 35, support {omega_b, tau, ln10As, n_s}; cluster sizes [5], `R_SR` = 1.00

```text
direct (mse40)   (tau*(1.0817714*n_s*(n_s + omega_b**2 - 2.248102) - 1.0817714*(181.83203*tau + 81.92537)*(tau + 0.07527962*log(A_s) + 0.96936315) - 1.0817714*log(n_s) - 46.6351412550292) + 0.0256585531449424)/tau

two-stage f1     -A_s/(tau - 0.4454238)   (complexity 5)
two-stage f2     tau   (complexity 1)
known f2 probed  tau
```

**z5** — partial absorption; canonical form from seed 4, complexity 32, support {omega_b, omega_cdm, H0, tau, ln10As, n_s}; cluster sizes [5], `R_SR` = 1.00

```text
direct (mse40)   omega_cdm + tau - 0.06374692 + (2.2001908*n_s*(-tau + 0.6569637 + 4.1936865/H0 - 9.847395e-10/A_s)/omega_cdm - 3.34214928920744)/(n_s + omega_b)

two-stage f1     A_s*exp(-2*tau)   (complexity 5)
two-stage f2     H0*omega_cdm/n_s   (complexity 5)
known f2 probed  H0*omega_cdm/n_s
```

---

## 8. Controls

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

## 9. Capacity, saturation, stability

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

## 10. Limitations

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

## 11. Artifacts

| what | where |
|---|---|
| per-checkpoint results | `experiments/mse_one_stage_sr_lcdm_tt_beta3e-4.{json,md}`, `..._lcdm_tt_ee_lowl.{json,md}` |
| frozen selections (T0) | `results/<run>/mse_one_stage_selection_manifest.json` |
| T1 calibration contract | `results/<run>/mse_one_stage_calibration.json` |
| searches / controls | `results/<run>/mse_one_stage_ms{20,30,40}/`, `mse_one_stage_control_ms{20,40}/` |
| protocol | `experiments/mse_one_stage_sr_plan.md` |
| execution record | `lightning_execution` in `experiments/mse_one_stage_execution_provenance.json` |
| per-task ledger | `logs/mse_one_stage_pool_ledger_lightning.jsonl` |

---

## 12. Appendix — every `mse40` winner, and the parsimonious readout

The primary budget in full: all five seed winners per latent, with the T2 NMSE
each achieved, and beneath them the cross-seed one-standard-error readout —
the smallest common complexity whose mean T0 envelope is within
`sd(E_s(c_min))/√5` of the minimum. The one-SE forms are markedly shorter and
usually lose little; they are a parsimony readout and carry no success
decision.

`mse20` and `mse30` winners, full Pareto fronts and per-equation diagnostics
are in the per-checkpoint artifacts `experiments/mse_one_stage_sr_<run>.json`
and the immutable per-run `results/<run>/mse_one_stage_ms*/z*_seed*/`
directories.


### TT — `lcdm_tt_beta3e-4`

**z0**

```text
mse40 primary winners
  seed 0  c=37  T2 NMSE=0.00320
    (-1392.39141267514*A_s*H0**2 + 770.670243855226*omega_b**2 + 0.902853341586617*omega_b*omega_cdm*(-H0 + 565.74870373125*n_s + omega_b - 1683.87881149117) + 20.8594922935101*omega_cdm)/omega_cdm
  seed 1  c=37  T2 NMSE=0.00398
    -A_s + 1.1049995*n_s + 0.189879*n_s/omega_b + omega_b**2 - 413.411735*omega_b - 14.970405*omega_cdm - 226.968506844676*omega_cdm**2*tau**2/n_s**2 + 11.776864*n_s/(H0*omega_cdm)
  seed 2  c=37  T2 NMSE=0.00215
    (-3.91713328479001*A_s*(omega_b - tau)**2*(omega_cdm - 1.0495782) + A_s*(-10.732027*n_s + 768.54694*omega_b + 24.993128*omega_cdm + log(H0) - 13.1194225304697) + 5.8059122e-8*omega_b*(omega_cdm - 1.0495782))/(A_s*(omega_cdm - 1.0495782))
  seed 3  c=31  T2 NMSE=0.00457
    (n_s*(H0 - 10.3037253854979*tau)*(-794.84454*omega_b - tau*(tau + 0.48297423) + 26.9960943926482) + 97.4718336308724*n_s - (H0 - 10.3037253854979*tau)*(26.5958377070186*omega_cdm + 7.42503470649822))/(n_s*(H0 - 10.3037253854979*tau))
  seed 4  c=40  T2 NMSE=0.00466
    0.113194495*H0*n_s - 0.1301869*H0 - n_s*tau + 0.37281317*n_s/omega_cdm + tau**2 - 18.963026 + 0.3818727/omega_b + n_s*log(tau)/H0 - n_s*(omega_b + 0.37281317*tau)**2/(H0*tau**2)

one-standard-error readout at common complexity 22  (c_min=40, threshold=0.004070 NMSE)
  seed 0  c=22  T0 val NMSE=0.00385
    (747.45372880822*omega_b**2 + omega_b*omega_cdm*(-H0 + 512.098242215158*n_s - 1504.84471233154) + 20.6145379011286*omega_cdm)/omega_cdm
  seed 1  c=22  T0 val NMSE=0.00410
    -tau**2 + 0.19718611/omega_b - 372.4508*omega_b/n_s - 15.587016*omega_cdm/n_s + 11.021319/(H0*omega_cdm)
  seed 2  c=22  T0 val NMSE=0.00292
    11.2400820796977*n_s - 796.263146143202*omega_b - 25.8952867375807*omega_cdm - 1.03609817859121*log(H0) + 13.4323995024441 + 1.27784568250118e-9/A_s
  seed 3  c=22  T0 val NMSE=0.00432
    -794.8447*omega_b - 0.46785718*tau + 26.986241368073 - 26.6718850582912*omega_cdm/n_s - 7.4152961741833/n_s + 98.541340640873/H0
  seed 4  c=22  T0 val NMSE=0.00483
    0.1309481*H0 - 0.14589529*H0/n_s - 19.12339 + 0.35990542/omega_cdm + 0.38211325/omega_b - tau**2/n_s
```

**z1**

```text
mse40 primary winners
  seed 0  c=39  T2 NMSE=0.01518
    (n_s*(H0 - exp(2*omega_b))*(omega_b**2*(2*tau - 49.891968) + (omega_b**2*(omega_cdm + 1.99611856100836*tau**2 - 3.417642) - 1.6824895e-5)*log(A_s)) + 9.700308*omega_b**2*(-H0 + exp(2*omega_b)) - 85.1028*omega_b*omega_cdm)/(omega_b**2*(H0 - exp(2*omega_b)))
  seed 1  c=21  T2 NMSE=0.05319
    7.2245064*log(H0*n_s**2*omega_b**2/(0.190415417128964*A_s*omega_b + 0.190415417128964*A_s - omega_b - 0.190415417128964*omega_cdm)**2) - 23.9643695428481 + 7.655731e-9/A_s
  seed 2  c=38  T2 NMSE=0.08563
    -n_s*omega_b + (tau + 3.9161375)*(0.814081942964497*H0*omega_b + n_s**2*(0.03326165*H0*(omega_b + 1.3243906*omega_cdm) + n_s**2 - tau) - 21.3197705481015*omega_cdm)
  seed 3  c=38  T2 NMSE=0.01806
    (-0.794255562529119*H0*n_s**2*omega_b*(0.38122582*log(A_s) + 6.625871) + H0*omega_b*omega_cdm*(n_s - 1.70955819972922*omega_cdm)*(-2*omega_b - 0.09439021) - 0.794255562529119*H0*omega_b*omega_cdm*(24.230267880625*tau**2 + 1.8403795) - 7.3009893406138*omega_cdm)/(H0*omega_b*omega_cdm*(n_s - 1.70955819972922*omega_cdm))
  seed 4  c=38  T2 NMSE=0.01840
    -n_s*omega_b - (-n_s**2/omega_cdm + 16.3510350180551*omega_b + 3.3042338*tau + 4.60877108511481 + 9.532114/(H0*omega_b) - 6.76684e-9/A_s)/(n_s + 0.016759051)

one-standard-error readout at common complexity 21  (c_min=39, threshold=0.051410 NMSE)
  seed 0  c=20  T0 val NMSE=0.03406
    (H0*omega_b*(n_s*((omega_cdm - 3.4480197)*log(A_s) - 49.87621) - 10.000354) - 82.666534*omega_cdm)/(H0*omega_b)
  seed 1  c=21  T0 val NMSE=0.05405
    7.2245064*log(H0*n_s**2*omega_b**2/(0.190415417128964*A_s*omega_b + 0.190415417128964*A_s - omega_b - 0.190415417128964*omega_cdm)**2) - 23.9643695428481 + 7.655731e-9/A_s
  seed 2  c=20  T0 val NMSE=0.09097
    4.21400259611541*H0*n_s**2*omega_b + 3.5835445*n_s - 73.0419427778161*omega_cdm - 3.5835445*tau - 0.928131324271785
  seed 3  c=21  T0 val NMSE=0.02870
    -0.39193708*n_s**2*log(A_s)/omega_cdm - 6.8224497*n_s**2/omega_cdm - tau - 2.0101259 - 9.517737/(H0*omega_b)
  seed 4  c=21  T0 val NMSE=0.02155
    n_s/omega_cdm - 3.3043263*tau/n_s - 4.744928/n_s - 9.5332985/(H0*n_s*omega_b) + 6.2912693e-9/(A_s*n_s)
```

**z2**

```text
mse40 primary winners
  seed 0  c=37  T2 NMSE=0.01195
    (-0.0579337991333041*A_s*H0*omega_cdm + 1.39417319255902*n_s*(6.8100314*A_s*omega_cdm + (1.1889201533768*A_s - 4.896421855871e-8*omega_cdm)*(-omega_b + tau + 0.2404963)))/(A_s*omega_cdm*((n_s + tau)**2 - log(n_s + 0.04007876)))
  seed 1  c=39  T2 NMSE=0.04294
    (-A_s*omega_cdm*(1.3860478*n_s + exp(tau)) - (A_s*n_s*(log((omega_cdm*(H0 - 1.1562397) - 5.8780794)/(H0 - 1.1562397)) - 0.5107229) - (tau + 0.12651809)*(A_s*(A_s + 33.58002) - 1.10180416e-7))*(0.0978018350305454*n_s + 0.0705616610268025*exp(tau) + 1.8472162))/(A_s*(1.3860478*n_s + exp(tau)))
  seed 2  c=12  T2 NMSE=0.29547
    (0.40627283*A_s - 4.0068514e-8*omega_cdm*(omega_cdm + tau))/(A_s*omega_cdm)
  seed 3  c=29  T2 NMSE=0.00210
    (H0*n_s*(tau*(omega_b - omega_cdm) - 0.29783544) + H0*(omega_b - omega_cdm)*(4035209500.0*A_s - (A_s - 17.716805)*(3.247568*omega_b - tau) - 15.620946) + 278.70035*omega_b - 278.70035*omega_cdm)/(H0*(omega_b - omega_cdm))
  seed 4  c=39  T2 NMSE=0.00095
    (H0*(2*tau + (n_s + 18.793062*omega_b)*(tau + 4.351114) + 963.599511605) + (H0*(1.6578281*omega_cdm + tau + 2*log(A_s) + 88.4316) - 13.701953)*log(A_s))/H0

one-standard-error readout at common complexity 18  (c_min=39, threshold=0.124387 NMSE)
  seed 0  c=17  T0 val NMSE=0.10231
    5.395268*n_s + 1.2070274788026*tau/omega_cdm + 0.29039632707016/omega_cdm - 5.6910863981456e-8*tau/A_s - 1.36920709435705e-8/A_s
  seed 1  c=18  T0 val NMSE=0.07348
    0.825472564470026*(-A_s*log((H0*omega_cdm - 5.791741)/H0) + (38.94304*A_s - 1.18941365e-7)*(omega_cdm + tau))/A_s
  seed 2  c=12  T0 val NMSE=0.28823
    (0.40627283*A_s - 4.0068514e-8*omega_cdm*(omega_cdm + tau))/(A_s*omega_cdm)
  seed 3  c=17  T0 val NMSE=0.02320
    4035209500.0*A_s - 16.688637*tau - 15.0161295 + 0.43158054/omega_cdm + 278.7818/H0
  seed 4  c=16  T0 val NMSE=0.11420
    -0.24582634861374*H0*tau - 8.724445*omega_cdm + 8.724445*log(A_s) + 176.588604739688
```

**z3**

```text
mse40 primary winners
  seed 0  c=37  T2 NMSE=0.00223
    (n_s + 0.011812089*omega_cdm)*(H0*omega_b*omega_cdm*(4.4714913 - 3.417810007824*tau**2) + (1.5876365*omega_b + 0.22528028*omega_cdm)*(H0*(n_s + omega_cdm - 1.3064492) + 2.9229598))*exp(2.6091173*omega_cdm/n_s)/(H0*omega_b*omega_cdm)
  seed 1  c=26  T2 NMSE=0.00208
    31.774082*n_s + 61.427013*omega_cdm - 36.5154592998264 - 0.0549261897571295/omega_b - 0.466479788643606*tau/n_s + 92.950496093418/H0
  seed 2  c=38  T2 NMSE=0.00250
    -5.46425439142318*omega_cdm - 0.724104205256895*tau - 3.8262739564598*log((omega_b - 0.0678074274386009)**2/(n_s**8*omega_cdm**2)) - 6.56803118669722 + 2.03741364053299/(H0*omega_b)
  seed 3  c=22  T2 NMSE=0.00387
    -0.0187756448561935*H0 + n_s*(omega_b + 31.98304) + 112.28677*omega_b + omega_cdm**2*(266.8151 - tau) - 35.57421
  seed 4  c=37  T2 NMSE=0.00266
    -(omega_cdm + 4.8607607)*(omega_b + tau**2 - 6.17498130987532*log(n_s + exp(n_s)/H0) - 1.9400371 + exp(-log(omega_cdm/omega_b)**4) + 0.3048816/(2*omega_b + omega_cdm))

one-standard-error readout at common complexity 29  (c_min=38, threshold=0.003177 NMSE)
  seed 0  c=29  T0 val NMSE=0.00270
    (H0*omega_b*omega_cdm*(5.3967156 - 0.60173255*tau) + (1.8849965*omega_b + 0.27119568*omega_cdm)*(H0*(n_s + omega_cdm - 1.3076369) + 2.9207618))*(n_s + omega_b + omega_cdm)/(H0*omega_b*omega_cdm)
  seed 1  c=26  T0 val NMSE=0.00217
    31.774082*n_s + 61.427013*omega_cdm - 36.5154592998264 - 0.0549261897571295/omega_b - 0.466479788643606*tau/n_s + 92.950496093418/H0
  seed 2  c=29  T0 val NMSE=0.00346
    -5.36751106740526*omega_cdm - 3.8480370036263*log((omega_b - 0.070723317449584)**2/(n_s**8*omega_cdm**2)) - 6.10590595130582 + 1.90886862581894/(H0*omega_b)
  seed 3  c=22  T0 val NMSE=0.00422
    -0.0187756448561935*H0 + n_s*(omega_b + 31.98304) + 112.28677*omega_b + omega_cdm**2*(266.8151 - tau) - 35.57421
  seed 4  c=26  T0 val NMSE=0.00291
    (H0*(2*omega_b + omega_cdm)*(-omega_b - 0.66779876*tau + 30.652874*log(n_s) + 8.573629) + H0*(omega_cdm - 1.4952524) + 183.753931617903*omega_b + 91.8769658089514*omega_cdm)/(H0*(2*omega_b + omega_cdm))
```

**z4**

```text
mse40 primary winners
  seed 0  c=38  T2 NMSE=0.00258
    -0.0942166610105264*H0 + n_s**2 - (omega_b + tau)**2 + 3.3386119 + tau/omega_cdm - 0.001039371/(n_s*omega_b**2) + 6.85627267206176e-8/(A_s*H0*omega_cdm)
  seed 1  c=38  T2 NMSE=0.00743
    1.8916922*(tau - 0.97797483)*(0.806602178278494*n_s + omega_cdm*(-121.418686*A_s*H0**4 + exp(H0*omega_b) - 6.0647115923425) + 1.622959*tau)/(omega_cdm*(-0.0704542*H0 + omega_b + 2.044844))
  seed 2  c=40  T2 NMSE=0.00299
    -omega_b - omega_cdm + (n_s/omega_cdm - log(n_s))*(-0.011025735*H0 + tau + 1.2502856) - 4.05599617925696 - 0.0985735123015031/omega_b + 6.097998e-7/(A_s*H0)
  seed 3  c=38  T2 NMSE=0.00063
    4.30332076935801*n_s - 3*omega_cdm - 2*tau**2 + 8.79173634134096*tau - 4.30332076935801*log(A_s) - 10.791736341341*log(H0) - 4.30332076935801*log(omega_cdm/omega_b) - 37.3212765395905
  seed 4  c=38  T2 NMSE=0.00531
    (A_s*omega_cdm*(H0 - 1.0456314)*(omega_cdm - 1.65389991043216*tau**2 - log(H0) - log(H0 - 0.24386895) - 0.63409525) + A_s*((H0 - 1.0456314)*(23.837729*omega_b + tau - 1.0108964) + 67.6061) + 9.071215e-9*n_s*omega_cdm*(H0 - 1.0456314))/(A_s*omega_cdm*(H0 - 1.0456314))

one-standard-error readout at common complexity 27  (c_min=40, threshold=0.005204 NMSE)
  seed 0  c=27  T0 val NMSE=0.00457
    -0.0880467394355359*H0 + n_s**2 + n_s + 3.830791 + tau/omega_cdm - 0.09523616/omega_b + 7.17661753306419e-8/(A_s*H0*omega_cdm)
  seed 1  c=27  T0 val NMSE=0.01095
    (-898190.537269494*A_s*omega_cdm*(0.0232562953047168*H0 + 1)**4 - 0.41732386*n_s**2*omega_b*omega_cdm + n_s*omega_b*(omega_b + tau + 0.46448293))/(omega_b*omega_cdm)
  seed 2  c=27  T0 val NMSE=0.00320
    -0.011047057*H0*n_s/omega_cdm - n_s*omega_cdm + n_s*tau/omega_cdm + 1.2479999*n_s/omega_cdm - 4.037318 - 0.0986543604758712/omega_b + 6.113255e-7/(A_s*H0)
  seed 3  c=26  T0 val NMSE=0.00143
    4.32220013818074*n_s + 8.74231405418513*tau - 4.32220013818074*log(A_s) - 10.7423140541851*log(H0) - 4.32220013818074*log(omega_cdm/omega_b) - 38.2449808273534
  seed 4  c=27  T0 val NMSE=0.00557
    22.5915507652302*omega_b/omega_cdm - 2.0760078*log(H0) + 1.0380039*tau/omega_cdm - 1.02308487754608/omega_cdm + 69.997658055993/(H0*omega_cdm) + 8.9664084766914e-9*n_s/A_s
```


### TT+EE — `lcdm_tt_ee_lowl`

**z0**

```text
mse40 primary winners
  seed 0  c=33  T2 NMSE=0.04271
    (H0*n_s*(omega_cdm + 0.16227016)*(0.611909908504171*n_s - omega_cdm - 13.024976) - H0*(8.116705*omega_cdm + 1.3170990190228) + 0.3357956*n_s*(omega_cdm + 0.16227016) + n_s*(H0*(0.2547958*omega_b + 0.0136975255) - 0.3357956)*log(A_s)**2)/(H0*n_s*(omega_cdm + 0.16227016))
  seed 1  c=39  T2 NMSE=0.06810
    (H0*(2.58571971129302*n_s*omega_b - 0.49200463*omega_cdm + 0.047696576) + (H0*omega_b**2 + 0.8320242)*(omega_b*(n_s + omega_cdm) - 3.7659597))*exp((H0*omega_cdm*(omega_b + 0.03874645) + 2.1881316)/(H0*n_s*(omega_b + 0.03874645)))/(H0*omega_b**2 + 0.8320242)
  seed 2  c=36  T2 NMSE=0.06725
    9.122279*n_s*log(n_s + 1.6585479*omega_b*(n_s + 0.8684513) - 2.55696960236182*omega_b*(omega_cdm - 0.20849346)*(2.1579292*H0 - omega_cdm + 0.68900293) + 2.55696960236182*omega_b - 0.876577762112077) - omega_cdm
  seed 3  c=25  T2 NMSE=0.03992
    -13554076.368663*A_s*H0 + 0.126157322535035*H0 - omega_cdm + 10.005785 - 0.17647429/omega_b - 73.519005*omega_cdm/n_s
  seed 4  c=36  T2 NMSE=0.06430
    -(exp(2*omega_cdm) - 0.82838506)*(A_s*n_s + 1.8987488*n_s*omega_b**4*omega_cdm - 0.025945703*n_s*omega_b**4*(H0 - log(A_s)) - 0.047099736*n_s*omega_b**3*omega_cdm + 0.43811473*omega_b**3*omega_cdm)/(n_s*omega_b**4*omega_cdm)

one-standard-error readout at common complexity 17  (c_min=39, threshold=0.059251 NMSE)
  seed 0  c=17  T0 val NMSE=0.04343
    4.5105166*H0*omega_b/n_s + 1/omega_cdm - 17.49021/n_s + 4.224316e-9/(A_s*n_s)
  seed 1  c=17  T0 val NMSE=0.06764
    1.69945233109288*H0*(3.1563853201569*n_s*omega_b - 0.6340853*omega_cdm + 0.0640831) - 7.0030336
  seed 2  c=15  T0 val NMSE=0.06684
    4.74109249468464*H0*n_s*omega_b + 2*n_s - 78.80207*omega_cdm
  seed 3  c=17  T0 val NMSE=0.04108
    (n_s*(5.38043*H0*(-1988523.5*A_s + omega_b) + 2.0424628) - 74.15264*omega_cdm)/n_s
  seed 4  c=17  T0 val NMSE=0.06701
    0.011132531*H0/omega_cdm - 0.45012355 + 0.209451757656028/omega_cdm - 0.17510279/(n_s*omega_b)
```

**z1**

```text
mse40 primary winners
  seed 0  c=40  T2 NMSE=0.01785
    (H0*n_s*omega_b*((n_s + tau)**2 + 2.0184882) + H0*omega_b*tau + 14.344748*n_s*omega_b + n_s*(-1.15493339037164*H0*(omega_cdm + 0.15136993) + 16.567501005947))*exp((10.2919814554961*omega_b*(H0 + omega_b) - 14.344481)*exp(n_s)/(H0 + omega_b))/(H0*n_s*omega_b)
  seed 1  c=37  T2 NMSE=0.01679
    (H0*omega_b*omega_cdm*(1.85441786688757*n_s + tau + 3.1201410476778) + omega_b*(0.596927916282544*H0 + 10.0984062824152) - 1.010950348439*omega_cdm*(H0*(H0 + 7.8484507) - 0.04527054)*(omega_b*(0.10056925 - 0.02793439*tau) + 0.0009844113))/(H0*omega_b*omega_cdm)
  seed 2  c=40  T2 NMSE=0.00308
    ((H0 + 0.8049228*log(A_s/n_s))*(-H0 + 2*tau + log(omega_b)) + ((H0 + 0.8049228*log(A_s/n_s))*(2*omega_b - omega_cdm + 0.92914397) - 1.2114552*log(A_s/n_s))*(H0 + omega_b + omega_cdm + tau - 13.67243911))/(H0 + 0.8049228*log(A_s/n_s))
  seed 3  c=39  T2 NMSE=0.01638
    -10.3202674027993*A_s*H0**2/omega_b**2 - 55.736713*omega_cdm + tau + log(n_s) + 2.3726995*log(omega_b) + log(n_s - omega_b + 3.312648*tau + 0.005044803) + 4.476053 + 778.883164840577/H0
  seed 4  c=35  T2 NMSE=0.00201
    0.7039488*H0/log(omega_cdm**2) - tau*log(omega_cdm) + tau + 155.3249*exp(omega_b) - 146.783972485304 + 9.963138715392/log(omega_cdm**2) + 3.5641272e-9*n_s/A_s

one-standard-error readout at common complexity 25  (c_min=40, threshold=0.014344 NMSE)
  seed 0  c=24  T0 val NMSE=0.01981
    (omega_b + 1.0447563)*(H0*omega_b*(tau + (n_s + tau)**2 + 2.1689014) - 1.16028457742894*H0*(omega_cdm + 0.15002738) + 16.6059046905351)/(H0*omega_b)
  seed 1  c=25  T0 val NMSE=0.01686
    0.09228686*H0*tau - 0.06091901*H0 - 0.0021677404*H0/omega_b - 3.2279668756901*tau + 2.13079680444035 + 0.7485748/omega_cdm + 0.075822215711914/omega_b - 1.5884683/n_s + 44.6192/H0
  seed 2  c=25  T0 val NMSE=0.01035
    (H0*((n_s + tau)**2 - 13.956129) - (H0 - 11.485902)*(H0*(-2*omega_b + omega_cdm + 0.16627668) + 1.6123171*log(A_s)))/H0
  seed 3  c=25  T0 val NMSE=0.01854
    n_s**2 - 56.17069*omega_cdm - 81.7823444172245*tau**4 + 3.5080562*tau + 3.5080562*log(omega_b) + 7.218645 + 810.44970101322/H0
  seed 4  c=25  T0 val NMSE=0.00452
    0.7074167*H0/log(omega_cdm**2) + (n_s + tau)**2 + 148.22435*exp(omega_b) - 139.206758518092 + 13.216672/log(omega_cdm**2) + 2.6816396e-9/A_s
```

**z2**

```text
mse40 primary winners
  seed 0  c=35  T2 NMSE=0.00154
    -23.773088*n_s + 611.63058333384*omega_b - 100.94259*omega_cdm/log(omega_b + 13500.5803817453*tau**8) + log(A_s) - 0.217200286587708*log(H0) + 27.3583049054753
  seed 1  c=40  T2 NMSE=0.00288
    (-0.25864327*n_s**2*omega_cdm + omega_b*omega_cdm*(log(A_s) + 33.797157) - 0.0071337433)/(omega_b*omega_cdm*(A_s + (A_s - n_s + 6.765107*omega_b)*(n_s*omega_cdm + omega_b - 1.3209221)))
  seed 2  c=33  T2 NMSE=0.00154
    (omega_cdm + 0.8767359)*(H0**4*(0.0336795864254562*H0 - 1)**4*(-23.995014*n_s + 652.982386720542*omega_b + 25.995014*omega_cdm + 5.247814) + 1.13934851545217e+17*(A_s*H0**2*(0.0336795864254562*H0 - 1)**2 + 9.63662046566921e-7)**2)/(H0**4*(0.0336795864254562*H0 - 1)**4)
  seed 3  c=37  T2 NMSE=0.00167
    (-1.05862905777178*H0 + 14.066162*tau + (0.07526069*H0 - tau)*(-23.836819*n_s - (A_s - 322.99582)*(2*omega_b + 0.07364229) + 1.0288668*log(A_s) - 1.12266988)*log(omega_cdm) + exp(omega_b)*log(omega_cdm))/((0.07526069*H0 - tau)*log(omega_cdm))
  seed 4  c=37  T2 NMSE=0.00253
    489663499.0*A_s - 0.0026444618*H0 - 23.752577*n_s + 2*omega_b + 25.752577*omega_cdm + 33.22900615 - 0.31032595/omega_b

one-standard-error readout at common complexity 25  (c_min=40, threshold=0.002289 NMSE)
  seed 0  c=24  T0 val NMSE=0.00165
    -23.772982*n_s + 614.94135*omega_b - 100.93783*omega_cdm/log(omega_b) + log(A_s) - 0.22544362*log(H0) + 27.3255547366059
  seed 1  c=25  T0 val NMSE=0.00327
    -0.00029947178*H0/omega_cdm - 0.25813583*n_s/omega_b + log(A_s)/n_s + 33.815098/n_s - 0.0067566857/(n_s*omega_b*omega_cdm)
  seed 2  c=25  T0 val NMSE=0.00181
    1.13934851545217e+17*A_s**2 - 2.0590232e-5*H0**2 - 23.93021*n_s + 647.31708619305*omega_b + 25.93021*omega_cdm + 5.477421
  seed 3  c=24  T0 val NMSE=0.00194
    -23.763739*n_s + 647.68996915576*omega_b + 1.0272489*log(A_s) + 22.7205755632805 - 14.060923/log(omega_cdm)
  seed 4  c=23  T0 val NMSE=0.00265
    489420500.0*A_s - 0.002280015*H0 - 23.804436*n_s + 24.804436*omega_cdm + 33.3987492673816 - 0.31015143/omega_b
```

**z3**

```text
mse40 primary winners
  seed 0  c=36  T2 NMSE=0.00281
    (-1.5866493*(0.23623509483528*H0 - 1)**4 + (4.56140432502323*omega_cdm*(0.23623509483528*H0 - 1)**4 + 130.109235035005)*(28.147312*n_s + 402.250533650048*omega_b + 28.147312*omega_cdm - 1.5930623*log(H0 + tau) - 29.4344942072224))/(4.56140432502323*omega_cdm*(0.23623509483528*H0 - 1)**4 + 130.109235035005)
  seed 1  c=39  T2 NMSE=0.00250
    -1.1705339*n_s + log((-omega_b**4*(n_s**4*omega_cdm + 0.486159868425953*omega_b*exp(omega_cdm))**4 + 1.4889329537577e-13*(H0 + 12.954617)*(A_s - omega_b + (omega_b - 0.09667145)**2)*exp(4*omega_cdm))**2*exp(-8*omega_cdm)/(0.0771925561365496*H0 + 1)**2) + 53.8636007724634
  seed 2  c=39  T2 NMSE=0.00209
    0.00526937*H0 + 28.155476*n_s - 54.406345*omega_b + 54.406345*omega_cdm - exp(n_s - 0.6778744/tau) - 2*log(H0) - 14.0571699418992 - 0.22001667/omega_b
  seed 3  c=27  T2 NMSE=0.00191
    (-0.0020762782*H0 + omega_b**2*(H0 - 36.39311)*(H0*omega_b*omega_cdm + 28.1619120574521*n_s + 52.84133*omega_cdm - 29.971190213626) + 29.129369701263*omega_b**2 + 0.075562220923202)/(omega_b**2*(H0 - 36.39311))
  seed 4  c=26  T2 NMSE=0.00190
    (-0.000504265*H0 + omega_b*(28.1700678693762*n_s - 249.838974272061*omega_cdm**2 + 111.862035092849*omega_cdm - 27.9030254036452) - 0.15781781)/omega_b

one-standard-error readout at common complexity 26  (c_min=39, threshold=0.002306 NMSE)
  seed 0  c=26  T0 val NMSE=0.00269
    0.21699251*(4.60845399686837*(omega_cdm - tau**4)*(28.144*n_s + 402.09811248*omega_b + 28.144*omega_cdm - 1.6458133*log(H0) - 29.2206656064) - 1.5867089)/(omega_cdm - tau**4)
  seed 1  c=26  T0 val NMSE=0.00265
    0.9805272*log(omega_b**8*(n_s**4*omega_cdm + 0.575656945401627*omega_b*exp(omega_cdm))**8*exp(-8*omega_cdm)/(0.0771845246571753*H0 + 1)**2) + 51.5719953012702
  seed 2  c=24  T0 val NMSE=0.00222
    (omega_b*(-0.02296759*H0 + 28.144213*n_s - omega_b - omega_cdm*(omega_cdm - 54.584957) - 22.912968) - 0.19439627)/omega_b
  seed 3  c=26  T0 val NMSE=0.00190
    (-0.0021089015*H0 + omega_b**2*(H0 - 38.46404)*(28.1634586019955*n_s + 2*omega_b + 54.392596815959*omega_cdm - 29.8136689696288) + 23.0588796892815*omega_b**2 + 0.08111687165206)/(omega_b**2*(H0 - 38.46404))
  seed 4  c=26  T0 val NMSE=0.00178
    (-0.000504265*H0 + omega_b*(28.1700678693762*n_s - 249.838974272061*omega_cdm**2 + 111.862035092849*omega_cdm - 27.9030254036452) - 0.15781781)/omega_b
```

**z4**

```text
mse40 primary winners
  seed 0  c=35  T2 NMSE=0.01903
    (tau*(1.0817714*n_s*(n_s + omega_b**2 - 2.248102) - 1.0817714*(181.83203*tau + 81.92537)*(tau + 0.07527962*log(A_s) + 0.96936315) - 1.0817714*log(n_s) - 46.6351412550292) + 0.0256585531449424)/tau
  seed 1  c=36  T2 NMSE=0.03059
    23287325765892.5*A_s**2 + 46574651531784.9*A_s**2/tau + 22289870220658.6*A_s**2/tau**2 + 2*omega_b + 2*omega_cdm - 9.245917*tau**2 - 17.491834*tau - 6.87134419780165 + 1.6255271e-8/A_s
  seed 2  c=36  T2 NMSE=0.01706
    -(n_s - log((tau*exp(2782257200.0*A_s) + log(0.054009993*tau*exp(0.10209014*exp(tau*exp(omega_cdm + 21.810305*tau))))**4)*exp(-2782257200.0*A_s)))*(-omega_b + tau + 1.3318044)
  seed 3  c=35  T2 NMSE=0.03353
    (tau*(tau - 3.5768354) - (omega_cdm + tau*(29.586397 - log(n_s**2/(tau**2*log(A_s)**4))))*(tau + log(exp(-0.452064595962182*tau)/log(A_s)**4) + 11.850626))/tau
  seed 4  c=38  T2 NMSE=0.02662
    (A_s*n_s*tau**2*(omega_b - 0.044704568) + 0.11212051772976*A_s*n_s*(tau - 0.0414535582259881)**2 + tau**2*(-A_s*n_s*(18.999353*tau + 6.4968524) + A_s*(tau + 0.76786685) + 1.4527096e-8*n_s)*exp(1.56466399874409*tau/n_s**2))/(A_s*n_s*tau**2)

one-standard-error readout at common complexity 26  (c_min=38, threshold=0.027901 NMSE)
  seed 0  c=26  T0 val NMSE=0.01888
    (-tau*(1.3394003*n_s + (157.73572*tau + 63.451225)*(tau + 0.1032205*log(A_s) + 1.598419) + 28.378693) + 0.02236397)/tau
  seed 1  c=26  T0 val NMSE=0.03062
    21593724566061.3*A_s**2/tau**2 - 18.95251*tau - 7.8034480884643 + 1.181629/n_s + 1.6326226e-8/A_s
  seed 2  c=26  T0 val NMSE=0.01872
    -n_s + 2.5464983*log(exp(-1462110600.0*A_s)*log(0.038978126*tau*exp(0.2155689*exp(tau*exp(20.526651*tau))))**2)
  seed 3  c=26  T0 val NMSE=0.03712
    (-1.650841*n_s*tau - (omega_cdm + tau*(tau + 34.926605))*(tau + log(exp(-0.487220747905773*tau)/log(A_s)**4) + 11.902223))/tau
  seed 4  c=26  T0 val NMSE=0.02926
    (-A_s*tau**2*(18.718685*tau + log(n_s) + 5.757772) + 0.116351775086138*A_s*(tau - 0.040777307674549)**2 + 1.4525023e-8*tau**2)*exp(tau)/(A_s*tau**2)
```

**z5**

```text
mse40 primary winners
  seed 0  c=40  T2 NMSE=0.00074
    (n_s*omega_cdm**2 + (n_s*(omega_b - 7.73451*omega_cdm + log(n_s) + log(omega_b) + 13.174091) - (n_s*(3.9950275*tau - log(A_s**2) - 38.740917) + 3.9950275*omega_cdm)*log(H0))*(A_s - omega_b + 1.0693055))/n_s
  seed 1  c=40  T2 NMSE=0.00064
    (H0*(n_s - 2*omega_b - 26.341993*omega_cdm - tau*(log(n_s) + 17.866625) + 367.6913630784*(0.0521504770725643*n_s + omega_b)**2 + 8.930415*log(A_s) + 177.847718) + 145.99876460169)/H0
  seed 2  c=36  T2 NMSE=0.00415
    1.011365*n_s*omega_b/omega_cdm + 0.33324038828955*n_s/omega_cdm + 1.011365*omega_b - 19.6660849991619*tau + 6.2917185780569 + 4542.48676890167*(0.0149213158860179*H0*tau + 1)**2/H0**2 - 1.8736848365405e-8/A_s
  seed 3  c=40  T2 NMSE=0.00416
    (4.05180101456671e+16*A_s**2 + omega_b - omega_cdm - 0.75670004*tau + (omega_b + 0.01827646)*(-1.7211113*n_s + 2*omega_b - omega_cdm**2 + tau + 2.3216734) - 0.023913803*(exp(n_s) - log(H0))**2)/(omega_b + 0.01827646)
  seed 4  c=32  T2 NMSE=0.01573
    omega_cdm + tau - 0.06374692 + (2.2001908*n_s*(-tau + 0.6569637 + 4.1936865/H0 - 9.847395e-10/A_s)/omega_cdm - 3.34214928920744)/(n_s + omega_b)

one-standard-error readout at common complexity 26  (c_min=40, threshold=0.007492 NMSE)
  seed 0  c=26  T0 val NMSE=0.00206
    (n_s*(-8.37326*omega_cdm + log(omega_b) + 13.597701) + (n_s*(log(A_s**2) + 38.67537) - 4.029427*omega_cdm - 4.029427*tau)*log(H0))/n_s
  seed 1  c=25  T0 val NMSE=0.00428
    n_s**2 + n_s - 26.234165*omega_cdm - 17.823137*tau + 8.933948*log(A_s) + 178.855956 + 145.811251194336/H0
  seed 2  c=26  T0 val NMSE=0.00574
    2*n_s*tau + 0.35656828*n_s/omega_cdm - 19.4450915338794*tau + 6.2331586 + 4400.83689862713/H0**2 - 1.854942e-8/A_s
  seed 3  c=26  T0 val NMSE=0.00636
    9.96178882312381e+17*A_s**2 + 22.9200012881041*omega_b - 22.9200012881041*omega_cdm - 18.0616096510625*tau - 0.520417240287449*(exp(n_s) - log(H0))**2 + 0.378321695121988
  seed 4  c=26  T0 val NMSE=0.01639
    -2.2001908*n_s*tau/omega_cdm + 1.44544548867396*n_s/omega_cdm + omega_cdm + tau - 3.42339455920744 + 9.2269104553842*n_s/(H0*omega_cdm) - 2.1666147882966e-9*n_s/(A_s*omega_cdm)
```
