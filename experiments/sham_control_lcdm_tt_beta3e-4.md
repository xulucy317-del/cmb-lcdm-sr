# Sham-input dilution control — `lcdm_tt_beta3e-4` (R-P4 rule 2)

The all-6 blind SR rerun with one provably-irrelevant 7th input (a permutation of a real theta column: a genuine parameter's marginal, zero information about any latent). Baseline is `results/<run>/allparams (all-6, same protocol, same seeds)`, so Delta_sham = M^(c<=10) with sham minus without, paired by seed. Frozen predicate: dilution is demonstrated iff the pooled Delta_sham is negative by more than 1 SE.

**Pooled Delta_sham = -0.0404 +/- 0.0134 nat** (n=75) -> **DEMONSTRATED**

Forms spending complexity on the sham symbol: 0.0% of best-at-c<=10 forms.

| donor | n | mean Delta | SE | forms using sham |
|---|---:|---:|---:|---:|
| ob | 25 | -0.0289 | 0.0225 | 0.0% |
| tau | 25 | -0.0604 | 0.0278 | 0.0% |
| ns | 25 | -0.0318 | 0.0187 | 0.0% |

| latent | n | mean Delta | SE |
|---|---:|---:|---:|
| z0 | 15 | -0.1376 | 0.0444 |
| z1 | 15 | +0.0000 | 0.0000 |
| z2 | 15 | -0.0553 | 0.0364 |
| z3 | 15 | +0.0079 | 0.0169 |
| z4 | 15 | -0.0168 | 0.0115 |
