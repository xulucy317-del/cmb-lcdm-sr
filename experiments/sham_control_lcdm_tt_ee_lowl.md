# Sham-input dilution control — `lcdm_tt_ee_lowl` (R-P4 rule 2)

The all-6 blind SR rerun with one provably-irrelevant 7th input (a permutation of a real theta column: a genuine parameter's marginal, zero information about any latent). Baseline is `results/<run>/allparams (all-6, same protocol, same seeds)`, so Delta_sham = M^(c<=10) with sham minus without, paired by seed. Frozen predicate: dilution is demonstrated iff the pooled Delta_sham is negative by more than 1 SE.

**Pooled Delta_sham = +0.0137 +/- 0.0126 nat** (n=90) -> not demonstrated

Forms spending complexity on the sham symbol: 0.0% of best-at-c<=10 forms.

| donor | n | mean Delta | SE | forms using sham |
|---|---:|---:|---:|---:|
| ob | 30 | +0.0215 | 0.0194 | 0.0% |
| tau | 30 | +0.0106 | 0.0194 | 0.0% |
| ns | 30 | +0.0090 | 0.0267 | 0.0% |

| latent | n | mean Delta | SE |
|---|---:|---:|---:|
| z0 | 15 | -0.0049 | 0.0034 |
| z1 | 15 | -0.0060 | 0.0067 |
| z2 | 15 | +0.0056 | 0.0682 |
| z3 | 15 | +0.0462 | 0.0321 |
| z4 | 15 | +0.0407 | 0.0125 |
| z5 | 15 | +0.0007 | 0.0009 |
