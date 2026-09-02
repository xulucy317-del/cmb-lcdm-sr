# Held-out T2 comparison: OLS, MI-SR, and MSE-SR

This table compares the six-input OLS baseline, the actual MI-selected
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

## Evaluation protocol

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

## Descriptive summary

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
