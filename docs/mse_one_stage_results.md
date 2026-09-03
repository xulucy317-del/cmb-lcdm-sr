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

Rules exactly as frozen in §6 of the plan, with every threshold fixed before
T2 was opened.

#### TM1 — Decision ledger, per latent

**TT (temperature only)**

| $z$ | H1 | $U_{95}(Q_{\mathrm{obj}})$ | H2 | $U_{95}(Q_{\mathrm{cap}})$ | H3 | $U_{95}(Q_{\mathrm{rec}})$ | $f_2$ absorbed | $R_{\mathrm{SR}}$ | saturated | classification |
|---|---|---:|---|---:|---|---:|---:|---:|---|---|
| 0 | ✓ | 0.005 | — | 1.022 | ✓ | 0.43 | 1/5 | 1.00 | no | no capacity gain |
| 1 | ✓ | 0.095 | ✓ | 0.939 | — | 3.44 | 1/5 | 1.00 | yes | partial absorption |
| 2 | ✓ | 0.342 | — | 13.190 | — | 25.81 | 0/5 | 0.80 | no | no capacity gain |
| 3 | ✓ | 0.005 | — | 1.430 | ✓ | 0.29 | 0/5 | 1.00 | no | no capacity gain |
| 4 | ✓ | 0.124 | ✓ | 0.057 | — | 1.18 | 0/5 | 1.00 | yes | partial absorption |

**EE (temperature + low-$\ell$ polarization)**

| $z$ | H1 | $U_{95}(Q_{\mathrm{obj}})$ | H2 | $U_{95}(Q_{\mathrm{cap}})$ | H3 | $U_{95}(Q_{\mathrm{rec}})$ | $f_2$ absorbed | $R_{\mathrm{SR}}$ | saturated | classification |
|---|---|---:|---|---:|---|---:|---:|---:|---|---|
| 0 | ✓ | 0.058 | — | 1.505 | — | 1.48 | 0/5 | 1.00 | no | no capacity gain |
| 1 | ✓ | 0.021 | ✓ | 0.949 | — | 3.49 | 0/5 | 1.00 | yes | partial absorption |
| 2 | ✓ | 0.010 | — | 1.118 | ✓ | 0.92 | 0/5 | 1.00 | no | no capacity gain |
| 3 | ✓ | 0.005 | ✓ | 0.718 | ✓ | 0.34 | 0/5 | 1.00 | no | partial absorption |
| 4 | ✓ | 0.272 | ✓ | 0.929 | ✓ | 0.76 | 0/5 | 1.00 | no | partial absorption |
| 5 | ✓ | 0.038 | ✓ | 0.438 | — | 1.52 | 0/5 | 1.00 | yes | partial absorption |

**Table TM1.** Verdicts under the rules frozen in §6 of the experiment plan
before T2 was opened. For five seed-paired values,
$U_{95}(x)=\mathrm{mean}(x_s)+2.132\,\mathrm{sd}(x_s)/\sqrt{5}$; seeds, not rows,
are the replication unit. The ratios are
$Q_{\mathrm{obj}}=\mathrm{MSE}_{T2}(\texttt{mse20})/\mathrm{MSE}_{T2}(\texttt{mi20-mse})$,
$Q_{\mathrm{cap}}=\texttt{mse40}/\texttt{mse20}$ and
$Q_{\mathrm{rec}}=\texttt{mse40}/\text{interaction-aware hierarchy}$. A hypothesis
passes (✓) when at least 4/5 seed ratios fall below the
margin — 1.0 strict for H1 and H2, 1.10 inclusive for H3 — **and** $U_{95}$ does
too, so a single wild seed can fail an otherwise favourable latent (TT $z_2$).
"$f_2$ absorbed" counts seeds passing **both** legs of TM2. $R_{\mathrm{SR}}$ is
the dominant-cluster fraction over the five `mse40` winners under the frozen
semantic equivalence rule; "saturated" flags at least 3/5 winners at complexity
$\ge 38$. $Q_{\mathrm{rec}}$ is unpaired: one canonical hierarchy is the
denominator for all five direct seeds. T2-confirmed.

Totals: H1 11/11, H2 6/11, H3 5/11, absorption 0/11, stability 11/11,
saturation 4/11.

## 4. The known-`f2` result, and why the mechanism matters more than the verdict

The pre-specified test has two legs, and a seed passes only if **both** hold:
`R²_f2 ≤ 0.05` for a five-fold, 64-bin monotone `q(f2)` cross-fit on T1 and
refit on all of T1, **and** `MI(e_direct; f2)` no greater than its own
97.5th-percentile 39-permutation T2 null. No map or threshold is fitted on T2.

#### TM2 — Known-$f_2$ absorption, both legs

**TT (temperature only)**

| $z$ | max $R^2_{f_2}$ | $R^2$ leg | max MI/null | MI leg | both |
|---|---:|---:|---:|---:|---:|
| 0 | 0.1664 | 4/5 | 35 | 1/5 | 1/5 |
| 1 | 0.1625 | 3/5 | 23 | 1/5 | 1/5 |
| 2 | 0.2065 | 2/5 | 140 | 0/5 | 0/5 |
| 3 | 0.0738 | 3/5 | 22 | 0/5 | 0/5 |
| 4 | 0.0875 | 4/5 | 10 | 0/5 | 0/5 |

**EE (temperature + low-$\ell$ polarization)**

| $z$ | max $R^2_{f_2}$ | $R^2$ leg | max MI/null | MI leg | both |
|---|---:|---:|---:|---:|---:|
| 0 | 0.1468 | 2/5 | 62 | 0/5 | 0/5 |
| 1 | 0.3617 | 2/5 | 51 | 0/5 | 0/5 |
| 2 | 0.0548 | 4/5 | 11 | 0/5 | 0/5 |
| 3 | 0.0400 | 5/5 | 13 | 0/5 | 0/5 |
| 4 | 0.0572 | 2/5 | 30 | 0/5 | 0/5 |
| 5 | 0.1261 | 1/5 | 19 | 0/5 | 0/5 |

**Table TM2.** The pre-specified absorption test, per latent over five seeds.
A seed passes only if **both** legs hold: $R^2_{f_2}\le 0.05$ for a five-fold,
64-bin monotone $q(f_2)$ cross-fit on T1 and refit on all of T1, **and**
$\mathrm{MI}(e_{\mathrm{direct}};f_2)$ no greater than its own 97.5th-percentile
39-permutation T2 null. No map or threshold is fitted on T2. "max MI/null" is the
worst seed's observed MI as a multiple of that null. Pooled over all 55
latent–seed audits the variance leg passes **32/55** and the information leg
**2/55** — the direct expression removes what a monotone function of $f_2$ can
predict while leaving dependence the MI test sees at 10 to 140 times the null.
Under amendment A2 this is the experiment's only newly computed MI.
T2-confirmed.

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
calibrated T2 errors, median over five seeds.

#### TM3 — H1 re-read with both objectives symmetrically calibrated

**TT (temperature only)**

| $z$ | `mse20` raw | `mse20` cal. | `mi20-mse` raw | `mi20-mse` cal. | ratio |
|---|---:|---:|---:|---:|---:|
| 0 | 0.00469 | 0.00496 | 0.99857 | 0.01605 | 0.31 |
| 1 | 0.08681 | 0.08718 | 1.00040 | 0.02985 | 2.92 ✗ |
| 2 | 0.10986 | 0.10677 | 1.00000 | 0.52968 | 0.20 |
| 3 | 0.00299 | 0.00307 | 0.95653 | 0.31279 | 0.01 |
| 4 | 0.11355 | 0.11461 | 1.00003 | 0.15570 | 0.74 |

**EE (temperature + low-$\ell$ polarization)**

| $z$ | `mse20` raw | `mse20` cal. | `mi20-mse` raw | `mi20-mse` cal. | ratio |
|---|---:|---:|---:|---:|---:|
| 0 | 0.04358 | 0.04336 | 1.00079 | 0.07598 | 0.57 |
| 1 | 0.01852 | 0.01848 | 0.99936 | 0.03300 | 0.56 |
| 2 | 0.00889 | 0.00924 | 0.99132 | 0.00944 | 0.98 |
| 3 | 0.00332 | 0.00389 | 0.99543 | 0.00673 | 0.58 |
| 4 | 0.04173 | 0.04052 | 1.00005 | 0.02730 | 1.48 ✗ |
| 5 | 0.02652 | 0.02700 | 1.00001 | 0.47484 | 0.06 |

**Table TM3.** The labelled diagnostic the plan pre-specified for exactly this
purpose: the same monotone calibration family fitted on T1 to the frozen
`mi20-mse` and `mse20` winners, then scored on T2. Median over five seeds;
"raw" is the uncalibrated endpoint the frozen H1 rule uses, "cal." the calibrated
one. Ratio is `mse20` calibrated over `mi20-mse` calibrated, so below 1 favours
the MSE objective; ✗ marks the two latents that reverse. Raw `mi20-mse` sits at
NMSE $\approx 1$ — no better than predicting the fit mean — because MI selection
optimises a bijection-invariant criterion and has no reason to return a
numerically calibrated expression. Once scale and offset are treated
symmetrically the MSE objective wins 9/11 rather than 11/11. This diagnostic
cannot carry a success decision and does not. T2, T1-fitted calibration.

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
baseline, fitted on T0-fit only and scored on T2.

#### TM4 — Symbolic reconstruction against a six-input linear baseline

**TT (temperature only)**

| $z$ | 6-input OLS | `mse40` | ratio | winner |
|---|---:|---:|---:|---|
| 0 | 0.00186 | 0.00398 | 2.14 | OLS |
| 1 | 0.01402 | 0.01840 | 1.31 | OLS |
| 2 | 0.00099 | 0.01195 | 12.10 | OLS |
| 3 | 0.00214 | 0.00250 | 1.17 | OLS |
| 4 | 0.00054 | 0.00299 | 5.56 | OLS |

**EE (temperature + low-$\ell$ polarization)**

| $z$ | 6-input OLS | `mse40` | ratio | winner |
|---|---:|---:|---:|---|
| 0 | 0.03949 | 0.06430 | 1.63 | OLS |
| 1 | 0.00097 | 0.01638 | 16.92 | OLS |
| 2 | 0.00173 | 0.00167 | 0.97 | `mse40` |
| 3 | 0.00311 | 0.00209 | 0.67 | `mse40` |
| 4 | 0.04283 | 0.02662 | 0.62 | `mse40` |
| 5 | 0.00115 | 0.00415 | 3.60 | OLS |

**Table TM4.** The plan's OLS control: ordinary least squares in the six raw
parameters, fitted on the T0-fit rows only and scored on T2, against the median
`mse40` winner. Ratio is `mse40` over OLS, so above 1 means the linear model
wins. Seven least-squares coefficients beat a 40-node symbolic expression in
8 of 11 latents, at times by an order of magnitude (TT $z_2$, ratio 12.1). The
result does **not** imply the latents are linear: the OLS residual is itself
97–99 % predictable from the same six parameters by a flexible nonlinear model
on T1, so both rows sit about two orders of magnitude above the achievable
floor. T2-confirmed; ceiling probe on T1.

Seven least-squares coefficients outperform a 40-node symbolic expression in
8/11 latents, sometimes by an order of magnitude (TT z2: 0.00099 vs 0.01195):
a stochastic search over a 40-node space with in-search constant optimisation
does not reliably match exact least squares on the criterion it is optimising.

**This does not mean the latents are linear, and neither model is near the
ceiling.** Refitting the OLS on T0-fit, taking its residual on T1 and modelling
that residual from the *same six parameters* with gradient boosting (fitted on
the first half of T1, scored on the second) recovers **97–99 % of the residual
variance** in every latent, pulling NMSE from ≈2×10⁻³ down to ≈3×10⁻⁵. So
μ_k(θ) is a smooth, essentially deterministic function of θ; a linear proxy
captures ~99.8 % of its variance over this narrow LHS prior box, and what
remains is structure, not noise. Both the linear baseline and the maxsize-40
expression sit about two orders of magnitude above the achievable floor.

The consequence is about *evidence*, not about the latents: on this data
reconstruction accuracy discriminates weakly between hypotheses, since a plain
affine map already reaches NMSE ≈ 10⁻³. That is precisely why the discovery
protocol selects on a bijection-invariant criterion instead — a point §5.1
makes from the other direction.

**Consequence for the write-up.** As *reconstruction*, direct symbolic
regression is not the right tool here and should not be sold as one. The
experiment's value is the structural finding of §4 — what the residual still
contains — not reconstruction accuracy per se.

## 6. Full reconstruction table

T2 NMSE, median over five seeds; hierarchy rows are the frozen T1-fitted maps
re-evaluated on the same T2 rows.

#### TM5 — T2 reconstruction NMSE, all methods

**TT (temperature only)**

| $z$ | `mi20-mi` | `mi20-mse` | `mse20` | `mse30` | `mse40` | $h(f_1)$ | $h+g$ | interaction | OLS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 57.27995 | 0.99857 | 0.00469 | 0.00408 | 0.00398 | 0.09495 | 0.01093 | 0.01094 | 0.00186 |
| 1 | 812.05832 | 1.00040 | 0.08681 | 0.03598 | 0.01840 | 0.09510 | 0.01887 | 0.01961 | 0.01402 |
| 2 | 542.52473 | 1.00000 | 0.10986 | 0.04972 | 0.01195 | 0.05260 | 0.00735 | 0.00742 | 0.00099 |
| 3 | 1.04717 | 0.95653 | 0.00299 | 0.00256 | 0.00250 | 0.08419 | 0.01160 | 0.01168 | 0.00214 |
| 4 | 61.71592 | 1.00003 | 0.11355 | 0.00405 | 0.00299 | 0.07918 | 0.00731 | 0.00535 | 0.00054 |

**EE (temperature + low-$\ell$ polarization)**

| $z$ | `mi20-mi` | `mi20-mse` | `mse20` | `mse30` | `mse40` | $h(f_1)$ | $h+g$ | interaction | OLS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 76280.71998 | 1.00079 | 0.04358 | 0.04461 | 0.06430 | 0.07598 | 0.04565 | 0.04702 | 0.03949 |
| 1 | 73.98375 | 0.99936 | 0.01852 | 0.01864 | 0.01638 | 0.06838 | 0.00538 | 0.00538 | 0.00097 |
| 2 | 113.80700 | 0.99132 | 0.00889 | 0.00233 | 0.00167 | 0.07124 | 0.00244 | 0.00287 | 0.00173 |
| 3 | 22.88692 | 0.99543 | 0.00332 | 0.00277 | 0.00209 | 0.06452 | 0.00777 | 0.00777 | 0.00311 |
| 4 | 1.00019 | 1.00005 | 0.04173 | 0.02800 | 0.02662 | 0.04357 | 0.04216 | 0.04216 | 0.04283 |
| 5 | 396.37415 | 1.00001 | 0.02652 | 0.00596 | 0.00415 | 0.08886 | 0.00725 | 0.00725 | 0.00115 |

**Table TM5.** Normalised mean squared error on T2, median over five seeds,
against the variance of the scored tier. `mi20-mi` and `mi20-mse` are the stored
GMM-MI front re-read under its own MI selector and under the validation-MSE
selector respectively; `mse20/30/40` are the direct one-stage searches at each
budget. $h(f_1)$, $h+g$ and "interaction" are the frozen hierarchy baselines with
their T1-fitted calibrators re-evaluated on the same T2 rows; OLS is the
six-input linear control of TM4. The `mi20-mi` column is not interpretable as
accuracy — values reach $7.6\times10^{4}$ — and is shown to make the calibration
point of TM3 concrete. Direct and hierarchical complexities are **not**
comparable: $h$ and $g$ are flexible non-symbolic calibrators whose cost appears
in no node count here. T2-confirmed.

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


### 7.1 Canonical forms at the primary budget

#### TT — `lcdm_tt_beta3e-4`

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


#### TT+EE — `lcdm_tt_ee_lowl`

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

---

### 7.2 What MSE finds at each complexity ceiling

The ladder below takes, for every seed, the best equation by T0-validation NMSE
at or below each complexity ceiling, pooled over the three budget families, and
asks what kind of object it is. "Separable" means no product or quotient of two
distinct parameters appears anywhere in the expression; "coupled" means one
does. Counts are the number of seeds sharing the dominant answer. The
expressions themselves, for every latent at every ceiling, are in §7.3.

#### TM6 — Reconstruction against the complexity ceiling


**TT (temperature only)**

| $z$ | $c\le5$ | $c\le8$ | $c\le10$ | $c\le15$ | $c\le20$ | $c\le30$ | $c\le40$ |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0.840 | 0.910 | 0.939 | 0.993 | 0.996 | 0.996 | 0.996 |
| 1 | 0.541 | 0.775 | 0.830 | 0.902 | 0.965 | 0.982 | 0.982 |
| 2 | 0.469 | 0.732 | 0.844 | 0.909 | 0.986 | 0.988 | 0.998 |
| 3 | 0.664 | 0.904 | 0.968 | 0.993 | 0.997 | 0.998 | 0.998 |
| 4 | 0.663 | 0.721 | 0.804 | 0.916 | 0.982 | 0.998 | 0.998 |

**EE (temperature + low-$\ell$ polarization)**

| $z$ | $c\le5$ | $c\le8$ | $c\le10$ | $c\le15$ | $c\le20$ | $c\le30$ | $c\le40$ |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0.486 | 0.698 | 0.867 | 0.936 | 0.958 | 0.960 | 0.960 |
| 1 | 0.871 | 0.924 | 0.948 | 0.976 | 0.982 | 0.986 | 0.986 |
| 2 | 0.569 | 0.931 | 0.963 | 0.997 | 0.998 | 0.998 | 0.998 |
| 3 | 0.510 | 0.705 | 0.869 | 0.990 | 0.998 | 0.998 | 0.998 |
| 4 | 0.541 | 0.696 | 0.958 | 0.964 | 0.968 | 0.976 | 0.976 |
| 5 | 0.530 | 0.904 | 0.908 | 0.972 | 0.992 | 0.997 | 0.997 |

**Table TM6.** Median over five seeds of $R^2 = 1-\mathrm{NMSE}$ on the T0
validation block, for the best equation at or below each ceiling. Accuracy
saturates by $c\le 20$–$30$ everywhere; the last ten nodes of the budget buy
essentially nothing. EE $z_0$ tops out at 0.960, the lowest ceiling of the
eleven and the same latent the discovery programme carries as unresolved.
T0-validation.

#### TM7 — The first parameter recruited, against the role MI assigned


**TT (temperature only)**

| $z$ | support at $c\le5$ | seeds | $R^2$ | role from T4.1 | contains role |
|---|---|---:|---:|---|---|
| 0 | $\omega_b$ | 5/5 | 0.840 | $\omega_b$ | ✓ |
| 1 | $n_s$, $\omega_{\mathrm{cdm}}$ | 4/5 | 0.541 | $\omega_{\mathrm{cdm}}$ | ✓ |
| 2 | $A_s$ | 3/5 | 0.469 | amplitude $(\tau,A_s)$ | ✓ |
| 3 | $n_s$ | 5/5 | 0.664 | $n_s$ | ✓ |
| 4 | $H_0$, $\omega_{\mathrm{cdm}}$ | 4/5 | 0.663 | $H_0$ | ✓ |

**EE (temperature + low-$\ell$ polarization)**

| $z$ | support at $c\le5$ | seeds | $R^2$ | role from T4.1 | contains role |
|---|---|---:|---:|---|---|
| 0 | $\omega_b$, $\omega_{\mathrm{cdm}}$ | 2/5 | 0.486 | $\omega_{\mathrm{cdm}}$ / early ISW | ✓ |
| 1 | $H_0$, $\omega_{\mathrm{cdm}}$ | 4/5 | 0.871 | $H_0$ | ✓ |
| 2 | $\omega_b$ | 5/5 | 0.569 | $\omega_b$ | ✓ |
| 3 | $n_s$ | 5/5 | 0.510 | $n_s$ | ✓ |
| 4 | $\tau$ | 5/5 | 0.541 | $\tau$ | ✓ |
| 5 | $A_s$ | 5/5 | 0.530 | amplitude $(\tau,A_s)$ | ✓ |

**Table TM7.** The support of the best expression at complexity $\le 5$ — the
first one or two parameters the MSE search spends its budget on — against the
role assigned to that latent by the independent, MI-selected discovery
programme (T4.1 of the report). The two objectives have different invariance
classes and select on different tiers, yet **the leading parameter agrees in
all eleven latents**. Where the MI role is a pair, MSE recruits one member of
it first ($A_s$ for both amplitude latents, $\tau$ for EE $z_4$).
T0-validation.

#### TM8 — Form family and parameter count against the ceiling


**TT (temperature only)**

| $z$ | $c\le5$ | $c\le10$ | $c\le20$ | $c\le40$ | vars at $c\le10$ | at $c\le20$ | at $c\le40$ |
|---|---|---|---|---|---:|---:|---:|
| 0 | separable 5/5 | coupled 2/5 | coupled 3/5 | coupled 3/5 | 3 | 4 | 5 |
| 1 | coupled 4/5 | coupled 5/5 | coupled+log 4/5 | coupled+log 3/5 | 3 | 5 | 6 |
| 2 | separable 5/5 | coupled+log 3/5 | coupled+log 4/5 | coupled+log 3/5 | 3 | 5 | 6 |
| 3 | separable 5/5 | separable+log 2/5 | coupled+log 1/5 | coupled+log 2/5 | 2 | 5 | 5 |
| 4 | coupled 4/5 | coupled 2/5 | coupled 4/5 | coupled+log 2/5 | 3 | 6 | 6 |

**EE (temperature + low-$\ell$ polarization)**

| $z$ | $c\le5$ | $c\le10$ | $c\le20$ | $c\le40$ | vars at $c\le10$ | at $c\le20$ | at $c\le40$ |
|---|---|---|---|---|---:|---:|---:|
| 0 | coupled 3/5 | coupled 5/5 | coupled+log 3/5 | coupled 3/5 | 3 | 5 | 5 |
| 1 | coupled 4/5 | coupled 3/5 | coupled+log 2/5 | coupled+log 3/5 | 3 | 5 | 6 |
| 2 | separable 5/5 | separable 4/5 | coupled+log 2/5 | coupled+log 2/5 | 3 | 5 | 6 |
| 3 | separable 5/5 | coupled 2/5 | separable 2/5 | coupled 2/5 | 3 | 4 | 4 |
| 4 | separable 5/5 | separable+log 3/5 | coupled+log 2/5 | coupled+log+exp 2/5 | 2 | 3 | 5 |
| 5 | separable 5/5 | separable+log 2/5 | coupled+log 3/5 | coupled+log 3/5 | 2 | 5 | 6 |

**Table TM8.** The dominant form family among the five seeds, with the number
of seeds agreeing, and how many of the six parameters appear. Three things read
off it. **Consensus decays with capacity**: at $c\le5$ seven of eleven latents
have all five seeds on the same family, but by $c\le40$ the dominant family
usually holds only 2–3 of 5 — accuracy keeps improving while the *form* stops
agreeing. **Parameters are recruited at a steady rate**, roughly one per five
nodes: 1–2 at $c\le5$, three at $c\le10$, four at $c\le15$, five or six by
$c\le20$–30. **Coupling arrives early**: most latents move from a separable
form to one containing a genuine product or quotient of two parameters between
$c\le5$ and $c\le10$, with logarithms appearing from $c\le8$ onward.
T0-validation.

A worked ladder, TT $z_0$ — the same latent whose MI-discovered coordinate is
$n_s/\omega_b$ at complexity 3. These are the **best** seed at each ceiling, so
they run slightly above the medians in TM6:

```text
c<=5   c=5  R2 0.840
   (0.38232777 / omega_b) + -17.44024
c<=10  c=10 R2 0.952
   (omega_b * -743.5626) + ((n_s * 19.000467) / exp(omega_cdm))
c<=20  c=20 R2 0.999
   ((omega_b * -1218.7023) * (omega_cdm + 0.53690153)) + ((106.06416 / H0) + (5.052643 - ((log(A_s) * n_s) * 0.5659249)))
```

Expressions verbatim from the fronts. The first five nodes buy $\omega_b$ alone
and 84 % of the variance; the next five add $n_s$ and $\omega_{\mathrm{cdm}}$;
ten more reach 0.999 and recruit $H_0$ and $A_s$. The MI programme reaches the same leading
structure — the ratio $n_s/\omega_b$ — in three nodes, because it never has to
pay for the scale.

---

### 7.3 The expression at each complexity ceiling

For every ceiling, the best equation over all five seeds and all three budget
families, by T0-validation NMSE — verbatim from the fronts, in PySR's own
output form. Where a higher ceiling returns the same expression as the one
below, the ceilings are merged. The seed and family that produced each form are
given; the seed changes along a ladder, so these are the best available at each
budget rather than one seed's nested progression. The MI-discovered coordinate
for the same latent closes each block for comparison.


**TT (temperature only)**

**z0**

```text
c<=5       C=5   R2=0.840   seed 1, ms30
   (0.38232777 / omega_b) + -17.44024
c<=8       C=8   R2=0.921   seed 3, ms30
   (0.0042373203 / square(omega_b)) + (-8.527707 / n_s)
c<=10      C=10  R2=0.952   seed 2, ms30
   (omega_b * -743.5626) + ((n_s * 19.000467) / exp(omega_cdm))
c<=15      C=15  R2=0.995   seed 0, ms20
   ((n_s * 11.181059) + 6.731357) - ((H0 + 1151.4515) * ((omega_cdm + 0.53684545) * omega_b))
c<=20      C=20  R2=0.999   seed 2, ms30
   ((omega_b * -1218.7023) * (omega_cdm + 0.53690153)) + ((106.06416 / H0) + (5.052643 - ((log(A_s) * n_s) * 0.5659249)))
c<=30/40   C=27  R2=0.999   seed 2, ms30
   (((neg(266.6253 / n_s) - 987.2135) * ((omega_b * (omega_cdm + 0.513893)) - -0.021953644)) + n_s) + ((30.16227 - (-101.35592 / H0)) - (log(A_s) * 0.63323146))

MI f1:  n_s/omega_b  (C=3)
```

**z1**

```text
c<=5       C=5   R2=0.541   seed 3, ms20
   (n_s / omega_cdm) + -8.428477
c<=8       C=8   R2=0.818   seed 4, ms40
   (-574.4501 / H0) + (square(n_s) / omega_cdm)
c<=10      C=10  R2=0.855   seed 4, ms40
   (square(n_s) / omega_cdm) + ((-12.580762 / omega_b) / H0)
c<=15      C=15  R2=0.923   seed 4, ms40
   (n_s / omega_cdm) + ((-5.8111134 - (-7.1743838e-9 / A_s)) - ((9.408182 / omega_b) / H0))
c<=20      C=20  R2=0.978   seed 4, ms40
   (((-5.009064 - (tau * 3.3042338)) + (square(n_s) / omega_cdm)) - ((9.532114 / omega_b) / H0)) - (-6.821436e-9 / A_s)
c<=30/40   C=30  R2=0.987   seed 1, ms30
   ((A_s + ((((omega_b + ((omega_cdm * -0.28042328) / square(n_s))) - (H0 * -0.00039702255)) * 238.71527) - (62.380535 - (log(A_s) * -2.9589946)))) - square(tau * -5.05323)) + -0.28306273

MI f1:  H0^2*n_s^2*omega_b/(A_s*omega_cdm^2)  (C=10)
```

**z2**

```text
c<=5       C=5   R2=0.471   seed 3, ms40
   (A_s * 4.0371412e9) + -8.471649
c<=8       C=8   R2=0.795   seed 2, ms20
   (log(A_s) * (tau + 8.401264)) + 169.30128
c<=10      C=10  R2=0.870   seed 2, ms20
   (log(A_s) * (tau + (omega_cdm + 8.273824))) + 169.05579
c<=15      C=15  R2=0.953   seed 2, ms20
   172.19373 + ((H0 * ((tau + omega_cdm) * -0.25354075)) - (-4.224578 * log(square(A_s))))
c<=20      C=20  R2=0.990   seed 0, ms30
   ((((log(A_s) + 20.562733) - tau) - tau) / omega_cdm) + ((-0.024492383 + (-0.0006186646 / omega_b)) / (n_s / H0))
c<=30      C=29  R2=0.998   seed 0, ms30
   square(omega_cdm + (0.75172263 + omega_cdm)) * (((-0.04588346 / omega_b) + (-0.055094004 / (n_s / H0))) + ((((log(A_s) - tau) + (20.5795 - tau)) / omega_cdm) - -2.1942966))
c<=40      C=39  R2=0.999   seed 4, ms40
   ((((omega_b * 18.793062) + n_s) * (tau + 4.351114)) + tau) + (-0.099188395 + neg(((((omega_cdm * -1.6578281) + (13.701953 / H0)) - ((log(A_s) + (log(A_s) + tau)) - -88.4316)) * log(A_s)) + (-963.6987 - tau)))

MI f1:  A_s/log(H0*(omega_cdm+tau))  (C=8)
```

**z3**

```text
c<=5       C=5   R2=0.664   seed 1, ms40
   (n_s * 31.859848) + -30.746515
c<=8       C=8   R2=0.904   seed 4, ms20
   log((omega_cdm + n_s) + -0.079809666) / 0.028854627
c<=10      C=10  R2=0.968   seed 4, ms20
   ((log(omega_cdm) * 6.8172555) / n_s) + (n_s * 15.854074)
c<=15      C=15  R2=0.994   seed 3, ms20
   ((H0 * -0.0005515066) / omega_b) + (((omega_cdm * 61.07346) - (n_s * -31.376673)) + -35.526848)
c<=20      C=19  R2=0.998   seed 3, ms20
   ((omega_cdm * 61.12067) + (((H0 * -0.00040654212) - 0.02610201) / omega_b)) + (-35.15177 - (n_s * (tau + -31.799374)))
c<=30/40   C=29  R2=0.998   seed 4, ms30
   (((-0.055441473 / omega_b) - (log(log(H0)) * 5.5555844)) + (((log(n_s) + (omega_cdm - (square(omega_b) + -0.15276726))) + omega_cdm) * 30.60156)) - square(tau * log(omega_cdm))

MI f1:  n_s+omega_cdm  (C=3)
```

**z4**

```text
c<=5       C=5   R2=0.663   seed 4, ms20
   8.177262 - (H0 * omega_cdm)
c<=8       C=8   R2=0.756   seed 4, ms30
   ((H0 * 0.030480761) + log(omega_cdm)) * -4.9139185
c<=10      C=10  R2=0.825   seed 1, ms30
   4.3153996 - (omega_cdm * neg((6.989825e-8 / A_s) - H0))
c<=15      C=15  R2=0.938   seed 1, ms40
   (((A_s * square(square(H0))) / omega_b) * -1.187426) + ((tau + 0.27244925) / omega_cdm)
c<=20      C=19  R2=0.993   seed 4, ms40
   ((((84.57614 / H0) + tau) + -0.73530585) / omega_cdm) - (8.87678 - ((omega_b * n_s) * (4.1565448e-7 / A_s)))
c<=30/40   C=30  R2=1.000   seed 4, ms30
   (((((((A_s + tau) / 0.51228356) - 0.54263794) + ((log(omega_cdm) + (((H0 * 0.034617472) + 16.172451) - log(omega_b))) / -0.98865634)) - log(A_s)) + n_s) / 0.2298292) - omega_cdm

MI f1:  A_s*H0^2*omega_cdm*exp(-2*tau)  (C=9)
```


**EE (temperature + low-$\ell$ polarization)**

**z0**

```text
c<=5       C=5   R2=0.532   seed 4, ms20
   5.2530227 - (omega_cdm / omega_b)
c<=8       C=7   R2=0.767   seed 0, ms20
   (H0 * 0.07409914) - (omega_cdm / omega_b)
c<=10      C=10  R2=0.878   seed 4, ms30
   (omega_cdm * -55.70394) + square((omega_b * H0) + n_s)
c<=15      C=15  R2=0.955   seed 0, ms40
   (((H0 * 4.6741557) * omega_b) + ((n_s / omega_cdm) + -17.75083)) - (-4.2225654e-9 / A_s)
c<=20      C=19  R2=0.961   seed 3, ms40
   ((omega_cdm * -75.48971) - (-9.770476 - (-0.17575397 / omega_b))) + (((n_s * 0.13079788) + (A_s * -1.3575965e7)) * H0)
c<=30/40   C=25  R2=0.962   seed 3, ms40
   ((-73.519005 * omega_cdm) + (n_s * (((H0 * 5.546441) * ((A_s * -2.443743e6) + 0.022745635)) - (-10.005785 + (omega_cdm - (-0.17647429 / omega_b)))))) / n_s

MI f1:  omega_cdm/(H0*n_s*omega_b)  (C=7)
```

**z1**

```text
c<=5       C=5   R2=0.871   seed 0, ms40
   8.177283 - (H0 * omega_cdm)
c<=8       C=8   R2=0.932   seed 4, ms40
   ((H0 * 0.36557785) / log(omega_cdm)) + 12.009066
c<=10      C=10  R2=0.951   seed 3, ms40
   log(omega_b) + (((-12.558149 / H0) + omega_cdm) * -61.03679)
c<=15      C=15  R2=0.979   seed 3, ms20
   ((tau + 4.6441774) + (H0 * (((omega_cdm / -3.1083183) + -0.051321633) + omega_b))) / 0.40732908
c<=20      C=20  R2=0.990   seed 2, ms30
   ((((0.3178089 - (omega_cdm * 0.7922487)) + ((omega_b * 2.3013914) + (8.794496 / log(A_s)))) * H0) + 11.496486) + tau
c<=30      C=29  R2=0.998   seed 2, ms30
   (H0 * ((8.941077 / log(A_s)) + ((omega_b * 2.2830062) + ((omega_cdm * -0.77759147) + 0.32361785)))) + ((((tau * 3.2418492) + square(n_s)) + (10.518018 - omega_cdm)) + omega_b)
c<=40      C=35  R2=0.998   seed 4, ms40
   (((((H0 - (log(omega_cdm) * tau)) - 0.13133384) + (3.5641272e-9 * (n_s / A_s))) + ((exp(omega_b) + -0.94416696) * 155.3249)) + ((H0 + 14.153215) * (0.7039488 / log(square(omega_cdm))))) + (tau - H0)

MI f1:  H0^2*omega_cdm  (C=4)
```

**z2**

```text
c<=5       C=5   R2=0.569   seed 1, ms40
   (omega_b * 646.9943) - 14.222848
c<=8       C=8   R2=0.931   seed 1, ms20
   (square(n_s) * -13.765594) + (omega_b * 583.7985)
c<=10      C=9   R2=0.963   seed 2, ms40
   ((n_s - omega_cdm) + (omega_b * -38.65033)) * -18.735561
c<=15      C=14  R2=0.998   seed 3, ms30
   ((omega_b * 647.58685) + (log(A_s) - ((n_s - omega_cdm) * 24.016066))) + 26.160799
c<=20      C=20  R2=0.998   seed 0, ms30
   (((26.180275 * omega_cdm) - -25.534649) + (643.94214 * omega_b)) + (log(A_s) + (23.784016 * ((0.69232523 / H0) - n_s)))
c<=30      C=29  R2=0.998   seed 2, ms40
   (omega_cdm + omega_cdm) + (5.222128 - ((((n_s + (omega_b * -27.18802)) - omega_cdm) * 23.820364) - square(square((-535.50134 / H0) / (H0 + -28.545479)) + (A_s * 3.3754237e8))))
c<=40      C=33  R2=0.998   seed 2, ms40
   (omega_cdm + 0.8767359) * ((omega_cdm + (5.247814 - ((((n_s + (omega_b * -27.213253)) - omega_cdm) * 23.995014) - square((A_s * 3.3754237e8) + square((-535.50037 / H0) / (H0 + -29.691576)))))) + omega_cdm)

MI f1:  omega_b/n_s^2  (C=4)
```

**z3**

```text
c<=5       C=5   R2=0.510   seed 1, ms40
   -27.26517 - (n_s * -28.252415)
c<=8       C=8   R2=0.725   seed 1, ms40
   ((exp(n_s) + -3.3457797) / omega_cdm) + 6.2880898
c<=10      C=10  R2=0.978   seed 3, ms30
   6.2404895 + (((3.2168102 * n_s) + log(omega_b)) / omega_cdm)
c<=15      C=15  R2=0.995   seed 4, ms40
   (-18.894423 + (((-0.016102629 / omega_cdm) - (H0 * 0.00058350794)) / omega_b)) + (n_s * 28.18494)
c<=20      C=20  R2=0.998   seed 3, ms40
   omega_b + ((((omega_cdm + -0.5343802) + ((0.4871451 + (2.182766 / H0)) * n_s)) * 54.384098) + (-0.0021144766 / square(omega_b)))
c<=30/40   C=26  R2=0.998   seed 4, ms40
   ((((n_s * 0.7710757) + ((omega_cdm * 3.0619059) - 0.76376617)) * 36.533466) - square((omega_cdm + omega_cdm) * 7.9031477)) + (((H0 * -0.000504265) - 0.15781781) / omega_b)

MI f1:  log(omega_b)/(n_s+omega_cdm)  (C=6)
```

**z4**

```text
c<=5       C=5   R2=0.541   seed 4, ms20
   (tau * -21.524557) + 1.5057741
c<=8       C=8   R2=0.956   seed 3, ms40
   (log(A_s) * (tau + -7.7803397)) - 154.09563
c<=10      C=10  R2=0.958   seed 3, ms40
   (tau * -21.407675) - ((log(A_s) * 7.7120457) + 152.63124)
c<=15      C=15  R2=0.965   seed 0, ms30
   (((0.008557925 / tau) + -3.7975433) / (0.57230425 - tau)) + ((1.4931322e-8 / A_s) - -0.070685156)
c<=20      C=20  R2=0.978   seed 0, ms40
   (((45.89842 + (tau * 142.21918)) * (((log(A_s) * -0.13870822) + -2.3975525) - tau)) + (0.021731824 / tau)) - 17.300495
c<=30      C=29  R2=0.982   seed 2, ms40
   tau + ((log(square(square(log((exp(exp(tau * exp(tau * 21.871605)) * 0.12336833) * tau) * 0.054351967)) / exp(A_s * 1.3911286e9))) - n_s) * 1.3476927)
c<=40      C=36  R2=0.983   seed 2, ms40
   (log(tau + square(square(log(exp(0.10209014 * exp(exp(omega_cdm + (21.810305 * tau)) * tau)) * (0.054009993 * tau))) / exp(A_s * 1.3911286e9))) - n_s) * ((1.3318044 - neg(tau)) - omega_b)

MI f1:  -A_s/(tau-0.4454238)  (C=5)
```

**z5**

```text
c<=5       C=5   R2=0.530   seed 4, ms40
   (-1.8491493e-8 / A_s) - -8.873762
c<=8       C=8   R2=0.904   seed 0, ms20
   (log(A_s) * (tau + 8.869331)) - -178.6559
c<=10      C=10  R2=0.957   seed 1, ms40
   ((tau - (-8.742959 - omega_cdm)) * log(A_s)) + 178.43175
c<=15      C=15  R2=0.983   seed 0, ms20
   (square(omega_cdm - 13.487473) + ((tau + 8.778358) * log(A_s))) - (H0 * 0.027911885)
c<=20      C=19  R2=0.993   seed 0, ms20
   ((tau + (square(omega_cdm - 13.487473) + ((tau + 8.778358) * log(A_s)))) * n_s) - (H0 * 0.027911885)
c<=30      C=29  R2=0.999   seed 1, ms40
   (((((-16.323364 / H0) - log(A_s)) * -8.931066) + square(((omega_b * 18.410038) * n_s) + n_s)) + ((tau * -17.826727) + 25.635181)) - ((omega_cdm * 26.235544) + -153.22232)
c<=40      C=40  R2=0.999   seed 1, ms40
   (((square(((omega_b + omega_b) * 9.58764) + n_s) - ((omega_b + ((26.341993 * omega_cdm) - (14.661722 + n_s))) + -137.57384)) + ((-17.866625 - log(n_s)) * tau)) + (25.612156 - omega_b)) + (((-16.348486 / H0) - log(A_s)) * -8.930415)

MI f1:  A_s*exp(-2*tau)  (C=5)
```

---

## 8. Controls

Protocol-identical MSE searches on independently permuted targets, selected by
shuffled-target validation MSE, scored on T2 against both targets:

#### TM9 — MSE shuffled-target controls

**TT (temperature only)**

| $z$ | budget | shuffle seed | $C$ | $R^2$ vs true | $R^2$ vs shuffled |
|---|---|---:|---:|---:|---:|
| 2 | ms20 | 0 | 7 | -0.0022 | -0.0011 |
| 2 | ms20 | 1 | 3 | +0.0048 | -0.0004 |
| 2 | ms20 | 2 | 1 | -0.0001 | -0.0001 |
| 2 | ms40 | 0 | 2 | -0.0057 | -0.0000 |
| 2 | ms40 | 1 | 3 | +0.0048 | -0.0004 |
| 2 | ms40 | 2 | 1 | -0.0001 | -0.0001 |

**EE (temperature + low-$\ell$ polarization)**

| $z$ | budget | shuffle seed | $C$ | $R^2$ vs true | $R^2$ vs shuffled |
|---|---|---:|---:|---:|---:|
| 5 | ms20 | 0 | 10 | +0.0005 | -0.0021 |
| 5 | ms20 | 1 | 3 | +0.0037 | -0.0004 |
| 5 | ms20 | 2 | 20 | +0.0051 | -0.0042 |
| 5 | ms40 | 0 | 7 | -0.0006 | -0.0012 |
| 5 | ms40 | 1 | 3 | +0.0037 | -0.0004 |
| 5 | ms40 | 2 | 19 | +0.0020 | -0.0047 |

**Table TM9.** Protocol-identical MSE searches on independently permuted
targets, for the amplitude latent of each checkpoint at both endpoint budgets,
selected by shuffled-target validation MSE. $C$ is the selected complexity;
$R^2$ is reported on T2 against both the true latent and the control's own
shuffled target. Every control sits within $|R^2|\le 0.006$ of zero against both,
and lifting the budget from 20 to 40 buys a shuffled target nothing — the
capacity gains of TM1 are not an artifact of a larger search space. Six paired
controls per checkpoint; these are diagnostics only, and three permutations do
not estimate any threshold. T2.

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

### 9.1 The overfitting readout the plan asked for (added 2026-09-03)

§10 risk 2 of `experiments/mse_one_stage_sr_plan.md` reads *"Larger trees
overfit 4000 rows. Select on held-out T0 validation, **inspect train/validation
gaps**, use shuffled controls, and confirm only once on T2."* The first and
third were done; the gap itself was stored per equation and never reported.
TM10 and TM11 close that, from
`scripts/capacity_and_noise_floor.py` →
`experiments/capacity_and_noise_floor_v1.{json,md}`.

#### TM10 — Train/validation gap against the complexity ceiling

**Real targets** — 3234 front members over 11 latents × 5 seeds × 3 budgets,
standardized units.

| $c$ | $n$ | med fit MSE | med val MSE | med val/fit | p90 | max |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 165 | 1.000 | 1.017 | 1.017 | 1.040 | 1.064 |
| 5 | 165 | 0.4476 | 0.4440 | 1.005 | 1.044 | 1.058 |
| 10 | 80 | 0.1435 | 0.1497 | 0.999 | 1.066 | 1.077 |
| 15 | 119 | 0.03165 | 0.03090 | 1.006 | 1.058 | 1.127 |
| 20 | 101 | 0.02137 | 0.02101 | 0.990 | 1.059 | 1.101 |
| 25 | 57 | 0.005097 | 0.004983 | 0.999 | 1.070 | 1.099 |
| 30 | 54 | 0.005943 | 0.006048 | 0.988 | 1.048 | 1.091 |
| 35 | 22 | 0.002882 | 0.002980 | 0.992 | 1.047 | 1.093 |
| 40 | 12 | 0.003067 | 0.003209 | 0.992 | 1.068 | 1.092 |

**Shuffled-target controls** — 221 front members, same units.

| $c$ | $n$ | med fit MSE | med val MSE | med val/fit | p90 | max |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 12 | 1.000 | 0.9923 | 0.992 | 1.025 | 1.025 |
| 5 | 12 | 0.9988 | 0.9939 | 0.996 | 1.028 | 1.028 |
| 10 | 11 | 0.9969 | 0.9934 | 0.996 | 1.030 | 1.030 |
| 20 | 10 | 0.9959 | 0.9939 | 0.997 | 1.030 | 1.030 |
| 30 | 2 | 0.9957 | 0.9910 | 0.995 | 1.007 | 1.007 |
| 39 | 1 | 0.9954 | 0.9794 | 0.984 | 0.984 | 0.984 |

**Table TM10.** Held-out error against fit error for every valid front member,
pooled over latents, seeds and budgets. **There is no overfitting knee**: the
median ratio never leaves 0.98–1.02 from $c=1$ to $c=40$, p90 stays $\le 1.10$,
and the worst single equation among 3234 is 1.128. With `n_val = 1000` the
validation MSE carries $\sqrt{2/1000} \approx 4.5\%$ relative standard error, so
that p90 spread *is* the sampling noise — the measurement bounds overfitting at
$\lesssim 5\%$ of fit error at every complexity and resolves nothing smaller.
The controls give the complementary number: on a permuted target the best
expression moves fit MSE from 1.000 only to 0.9955 by $c \approx 39$, so a
size-40 tree absorbs **0.45%** of pure-noise variance on 4,000 rows — against a
signal of 96–99.8%, about 200:1. T0-fit vs T0-validation.

#### TM11 — How deterministic the target is

| latent | OLS NMSE | GBM floor | ratio | nonlinear rms (% of $\sigma_\mu$) | floor rms | NN intercept / Var | $d^2$ fit $R^2$ |
|---|---:|---:|---:|---:|---:|---:|---:|
| TT z0 | 1.81e-3 | 2.39e-5 | 75x | 4.25% | 0.49% | −5.16e-04 | 0.9951 |
| TT z1 | 1.37e-2 | 2.29e-4 | 60x | 11.68% | 1.51% | −7.12e-05 | 0.9952 |
| TT z2 | 4.52e-4 | 8.44e-6 | 54x | 2.13% | 0.29% | −2.51e-04 | 0.9984 |
| TT z3 | 2.16e-3 | 2.33e-5 | 93x | 4.65% | 0.48% | −3.62e-04 | 0.9947 |
| TT z4 | 3.87e-4 | 4.12e-6 | 94x | 1.97% | 0.20% | +4.29e-04 | 0.9963 |
| EE z0 | 4.02e-2 | 9.34e-4 | 43x | 20.05% | 3.06% | −9.63e-04 | 0.9890 |
| EE z1 | 9.07e-4 | 7.93e-6 | 114x | 3.01% | 0.28% | +1.21e-04 | 0.9958 |
| EE z2 | 1.69e-3 | 3.40e-5 | 50x | 4.12% | 0.58% | −6.83e-04 | 0.9949 |
| EE z3 | 3.11e-3 | 5.16e-5 | 60x | 5.57% | 0.72% | −5.31e-04 | 0.9949 |
| EE z4 | 4.27e-2 | 4.31e-4 | 99x | 20.67% | 2.07% | −4.10e-03 | 0.9708 |
| EE z5 | 4.51e-4 | 1.31e-5 | 34x | 2.12% | 0.36% | −2.80e-04 | 0.9977 |

**Table TM11.** The exact six-input affine map in the sampled basis (T0-fit
coefficients), the floor a six-input HistGBM reaches beneath it (fit
T1[5000:15000], scored T1[15000:25000]), and a difference-based variance
estimate: over the 50k nearest-neighbour pairs in standardized $\theta$
(distances min 0.094, median 0.425, max 0.836),
$E[(\mu_i-\mu_j)^2/2] = a + b\,d^2$ is fitted and $a/\mathrm{Var}(\mu)$ read off.
A negative intercept is unphysical for a variance and only says the
linear-in-$d^2$ extrapolation slightly overshoots: **every latent is consistent
with zero irreducible noise**, and the pure-$d^2$ model explains 97.1–99.8% of
the pair-gap profile — what a smooth deterministic map gives, with no
white-noise pedestal. EE z4 is the loosest fit, as expected for the one latent
with a pole in $\tau$.

Read together with TM8: **what decays with capacity is not generalisation but
agreement.** The gap is flat while the dominant form family falls from 5/5 to
2–3/5 seeds, so those high-complexity forms are not overfitted — they are
non-identified. Held-out MSE is structurally blind to that failure mode;
$R_{\mathrm{SR}}$ is the instrument that sees it.

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
| capacity / noise floor (TM10, TM11) | `scripts/capacity_and_noise_floor.py` → `experiments/capacity_and_noise_floor_v1.{json,md}` |
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
