# Posterior ceiling — `lcdm_tt_ee_lowl` (roadmap Phase 5, gate G3)

The intrinsic ceiling I(Z_k; theta) = H(Z_k) − E[1/2 ln(2 pi e sigma_k^2)] from the cached encoder logvars (clamped to (−10, 10) as in the model): H(Z_k) from 4 posterior draws per row over T1 u T2, 1-D GMM (BIC over K <= 5) fit on half the draws, held-out cross-entropy on the rest, SE by joint row bootstrap (exact on the synthetic positive control, I_true = 1.124 vs 1.126 +/- 0.016). Numerators MI(Z_k; f) on a fresh posterior draw over T2 (confirmatory tier). Because the GMM-MI numerator over-estimates near-sufficient relations by ~7% on the same control, each latent also scores the same-estimator ceiling proxy MI(Z_k; mu_k): **eta_post = MI/I** (principled headline), **eta_post_hat = MI/MI(Z;mu)** (same-estimator ratio, shared bias cancels — drives the frozen 0.95 demotion rule and phase6_needed), DPI = MI(Z;f) <= MI(Z;mu) + 2 SE. eta_post_mu = MI(Z;mu)/I is the fraction of the analytic ceiling the estimator can even see (the practical top of the eta_post scale). Var(e1)/E[sigma^2] compares the Phase-3 residual to the posterior noise floor — the direct 'is the leftover modulation above the noise' readout.

## Noise table

| latent | role | E[sigma^2] | med sigma | Var(mu) | SNR | clamp frac | I_gauss |
|---|---|---:|---:|---:|---:|---:|---:|
| z0 | omega_cdm | 7.933e-02 | 2.342e-01 | 0.909 | 1.146e+01 | 0.000 | 1.261 |
| z1 | H0 | 4.669e-04 | 2.164e-02 | 1.018 | 2.180e+03 | 0.000 | 3.844 |
| z2 | omega_b | 1.250e-02 | 1.110e-01 | 0.982 | 7.858e+01 | 0.000 | 2.188 |
| z3 | n_s | 4.235e-03 | 6.466e-02 | 0.991 | 2.341e+02 | 0.000 | 2.730 |
| z4 | tau (amplitude sector) | 5.328e-02 | 2.033e-01 | 0.943 | 1.770e+01 | 0.000 | 1.464 |
| z5 | amplitude (A_s, tau) | 2.324e-04 | 1.513e-02 | 0.994 | 4.278e+03 | 0.000 | 4.181 |

## Intrinsic ceilings

| latent | H(Z) | H(Z\|theta) | I(Z;theta) +/- SE | K | I_gauss | MI(Z;mu) | eta_post_mu | I_plat (SR) | I/plat | Var(e1)/E[s2] |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| z0 | 1.403 | 0.061 | 1.343 +/- 0.003 | 3 | 1.261 | 1.309 | 0.97 | 1.788 | 0.75 | 0.87 |
| z1 | 1.418 | -2.417 | 3.835 +/- 0.003 | 4 | 3.844 | 3.880 | 1.01 | 4.006 | 0.96 | 149.29 |
| z2 | 1.407 | -0.773 | 2.180 +/- 0.003 | 4 | 2.188 | 2.187 | 1.00 | 3.330 | 0.65 | 5.64 |
| z3 | 1.410 | -1.314 | 2.724 +/- 0.003 | 3 | 2.730 | 2.722 | 1.00 | 3.212 | 0.85 | 15.11 |
| z4 | 1.412 | -0.124 | 1.535 +/- 0.003 | 2 | 1.464 | 1.478 | 0.96 | 2.370 | 0.65 | 0.78 |
| z5 | 1.411 | -2.765 | 4.176 +/- 0.003 | 3 | 4.181 | 4.180 | 1.00 | 4.087 | 1.02 | 382.23 |

## z0 — omega_cdm

I(Z;theta) = 1.343 +/- 0.003 nat; MI(Z;mu) = 1.309 +/- 0.013; canonical eta_post = 0.737, eta_post_hat = 0.756 +/- 0.012; S* = `allparams`, eta_post_hat = 0.854; residual audit failed: True -> phase6_needed = True.

| candidate | S | \|S\| | expr | finite | MI(Z;f) +/- | eta_post | eta_post_hat +/- | DPI |
|---|---|---:|---|---:|---|---:|---|---|
| canonical | {omega_b, omega_cdm, H0, n_s} (from expr) | — | `omega_cdm/(H0*n_s*omega_b)` | 1.00 | 0.989 +/- 0.011 | 0.737 | 0.756 +/- 0.012 | ok |
| reference S* | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | `omega_b*(H0 + 27.826664)*(n_s - 0.095620185)` | 1.00 | 1.117 +/- 0.015 | 0.832 | 0.854 +/- 0.014 | ok |
|  | {omega_cdm} | 1 | `log(omega_cdm - 0.09838888)` | 1.00 | 0.270 +/- 0.009 | 0.201 | 0.206 +/- 0.007 | ok |
|  | {H0} | 1 | `0.0167257418096133*exp(113.761091540569/H0**` | 1.00 | 0.140 +/- 0.009 | 0.104 | 0.107 +/- 0.007 | ok |
|  | {omega_cdm, H0} | 2 | `exp(0.0926810659285526*omega_cdm**6) + omega` | 1.00 | 0.510 +/- 0.009 | 0.380 | 0.390 +/- 0.008 | ok |
|  | {omega_b, omega_cdm} | 2 | `0.480796/log(omega_b/omega_cdm - 0.15215628)` | 1.00 | 0.434 +/- 0.011 | 0.323 | 0.332 +/- 0.009 | ok |
|  | {omega_cdm, n_s} | 2 | `exp(exp(-59.7797808349821*(0.102288411689581` | 1.00 | 0.316 +/- 0.009 | 0.236 | 0.242 +/- 0.007 | ok |
|  | {omega_b, n_s} | 2 | `-7.2611896e-5*omega_b + 1.112152*exp(0.47429` | 1.00 | 0.120 +/- 0.006 | 0.090 | 0.092 +/- 0.005 | ok |
|  | {omega_b, omega_cdm, H0} | 3 | `-omega_b*(H0*(omega_cdm - 0.20170897) - 1.80` | 1.00 | 0.812 +/- 0.013 | 0.604 | 0.620 +/- 0.012 | ok |
|  | {omega_cdm, H0, n_s} | 3 | `omega_cdm**2*(H0 - 113.93289)/n_s**2` | 1.00 | 0.598 +/- 0.012 | 0.445 | 0.457 +/- 0.010 | ok |
|  | {omega_b, omega_cdm, n_s} | 3 | `145278.501308389*(0.00262361028347138*n_s/om` | 1.00 | 0.542 +/- 0.015 | 0.404 | 0.414 +/- 0.013 | ok |
|  | {omega_b, omega_cdm, H0, n_s} | 4 | `omega_cdm*(omega_b**2 + 0.026196986)*exp(-n_` | 1.00 | 1.028 +/- 0.011 | 0.766 | 0.785 +/- 0.012 | ok |
|  | {omega_b, omega_cdm, H0, tau} | 4 | `-omega_b*(H0*(omega_b + omega_cdm - 0.224654` | 1.00 | 0.839 +/- 0.013 | 0.625 | 0.641 +/- 0.012 | ok |
|  | {omega_cdm, H0, tau, n_s} | 4 | `exp(0.00226407122601137*omega_cdm**2/((0.047` | 1.00 | 0.595 +/- 0.013 | 0.443 | 0.454 +/- 0.011 | ok |
|  | {omega_b, omega_cdm, tau, n_s} | 4 | `(0.00262293004262629*n_s + omega_b*omega_cdm` | 1.00 | 0.547 +/- 0.015 | 0.407 | 0.418 +/- 0.012 | ok |
|  | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | `(H0*omega_cdm + (H0*n_s*omega_b + omega_cdm*` | 1.00 | 1.120 +/- 0.014 | 0.834 | 0.856 +/- 0.014 | ok |

## z1 — H0

I(Z;theta) = 3.835 +/- 0.003 nat; MI(Z;mu) = 3.880 +/- 0.016; canonical eta_post = 0.352, eta_post_hat = 0.348 +/- 0.004; S* = `allparams`, eta_post_hat = 0.889; residual audit failed: True -> phase6_needed = True.

| candidate | S | \|S\| | expr | finite | MI(Z;f) +/- | eta_post | eta_post_hat +/- | DPI |
|---|---|---:|---|---:|---|---:|---|---|
| canonical | {omega_cdm, H0} (from expr) | — | `H0**2*omega_cdm` | 1.00 | 1.351 +/- 0.013 | 0.352 | 0.348 +/- 0.004 | ok |
| reference S* | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | `log(-log(n_s) + log(A_s*omega_cdm**4*(0.0014` | 1.00 | 3.450 +/- 0.011 | 0.900 | 0.889 +/- 0.005 | ok |
|  | {H0} | 1 | `0.89510218248256/H0**2` | 1.00 | 0.592 +/- 0.010 | 0.154 | 0.153 +/- 0.003 | ok |
|  | {omega_cdm} | 1 | `5.09355899810778*exp(-4.56093716494928e-5*om` | 1.00 | 0.126 +/- 0.006 | 0.033 | 0.033 +/- 0.001 | ok |
|  | {omega_cdm, H0} | 2 | `(log(H0*omega_cdm) - 0.802525753004956)/(ome` | 1.00 | 1.354 +/- 0.013 | 0.353 | 0.349 +/- 0.004 | ok |
|  | {H0, tau} | 2 | `-H0 + log(tau)` | 1.00 | 0.620 +/- 0.007 | 0.162 | 0.160 +/- 0.002 | ok |
|  | {omega_b, omega_cdm, H0} | 3 | `exp(omega_cdm)/(log(-H0*omega_cdm*(log(omega` | 1.00 | 1.726 +/- 0.010 | 0.450 | 0.445 +/- 0.003 | ok |
|  | {omega_cdm, H0, tau} | 3 | `0.281898492979282 + 1.08233239388204/log(log` | 1.00 | 1.461 +/- 0.009 | 0.381 | 0.376 +/- 0.003 | ok |
|  | {omega_cdm, H0, n_s} | 3 | `exp((-0.0070466674*H0*omega_cdm + 0.00704666` | 1.00 | 1.376 +/- 0.012 | 0.359 | 0.355 +/- 0.003 | ok |
|  | {omega_b, omega_cdm, H0, A_s} | 4 | `exp((0.043133087*H0 + 0.229761326867521*omeg` | 1.00 | 2.042 +/- 0.011 | 0.532 | 0.526 +/- 0.004 | ok |
|  | {omega_b, omega_cdm, H0, tau} | 4 | `tau + log(omega_b/(omega_cdm**2*(0.113700462` | 1.00 | 1.984 +/- 0.009 | 0.517 | 0.511 +/- 0.003 | ok |
|  | {omega_b, omega_cdm, H0, tau, A_s} | 5 | `omega_cdm + 2*tau + log(omega_b**2/(A_s*omeg` | 1.00 | 2.838 +/- 0.012 | 0.740 | 0.731 +/- 0.004 | ok |
|  | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | `-H0/(n_s + log(omega_b**2/A_s))**2 + 0.02565` | 1.00 | 2.135 +/- 0.010 | 0.557 | 0.550 +/- 0.003 | ok |
|  | {omega_b, omega_cdm, H0, tau, n_s} | 5 | `-n_s*(tau + 0.7072942) - 50.906757*omega_b +` | 1.00 | 2.044 +/- 0.012 | 0.533 | 0.527 +/- 0.004 | ok |

## z2 — omega_b

I(Z;theta) = 2.180 +/- 0.003 nat; MI(Z;mu) = 2.187 +/- 0.012; canonical eta_post = 0.576, eta_post_hat = 0.574 +/- 0.006; S* = `c46_S-ob-oc-As-ns`, eta_post_hat = 0.972; residual audit failed: True -> phase6_needed = True.

| candidate | S | \|S\| | expr | finite | MI(Z;f) +/- | eta_post | eta_post_hat +/- | DPI |
|---|---|---:|---|---:|---|---:|---|---|
| canonical | {omega_b, n_s} (from expr) | — | `omega_b/n_s**2` | 1.00 | 1.255 +/- 0.012 | 0.576 | 0.574 +/- 0.006 | ok |
| reference | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | `H0*((n_s - 1.0812154*omega_cdm)*log(A_s) + 6` | 1.00 | 2.108 +/- 0.012 | 0.967 | 0.964 +/- 0.008 | ok |
|  | {omega_b} | 1 | `log(exp(0.545885845707158*omega_b**4))**2/om` | 1.00 | 0.411 +/- 0.007 | 0.189 | 0.188 +/- 0.004 | ok |
|  | {n_s} | 1 | `58674737422.4144*exp(-2.57585652e-5*n_s)` | 1.00 | 0.234 +/- 0.009 | 0.107 | 0.107 +/- 0.004 | ok |
|  | {omega_cdm} | 1 | `2.88976948459684*(0.588258755260945*omega_cd` | 1.00 | 0.025 +/- 0.004 | 0.012 | 0.012 +/- 0.002 | ok |
|  | {omega_b, n_s} | 2 | `6402261.09328477/log(log((omega_b + 18.69483` | 1.00 | 1.314 +/- 0.012 | 0.603 | 0.601 +/- 0.006 | ok |
|  | {omega_b, A_s} | 2 | `exp(A_s*exp(340.5838410814*omega_b))` | 1.00 | 0.429 +/- 0.010 | 0.197 | 0.196 +/- 0.005 | ok |
|  | {omega_b, H0} | 2 | `exp(446.11487*omega_b)` | 1.00 | 0.428 +/- 0.009 | 0.196 | 0.196 +/- 0.004 | ok |
|  | {omega_b, tau} | 2 | `1.48299685562489e+19*exp(-0.0130337578606172` | 1.00 | 0.400 +/- 0.009 | 0.183 | 0.183 +/- 0.004 | ok |
|  | {omega_cdm, A_s} | 2 | `0.00897531251799187*A_s/(omega_cdm - 0.10418` | 1.00 | 0.032 +/- 0.003 | 0.014 | 0.014 +/- 0.002 | ok |
|  | {omega_cdm, H0} | 2 | `exp(2*H0*(omega_cdm - 0.10005605)/omega_cdm)` | 1.00 | 0.027 +/- 0.003 | 0.012 | 0.012 +/- 0.002 | ok |
|  | {H0, A_s} | 2 | `4285.84756496823*(0.0152750148033987*H0 - 1)` | 1.00 | 0.001 +/- 0.001 | 0.001 | 0.001 +/- 0.000 | ok |
|  | {omega_b, omega_cdm, n_s} | 3 | `(omega_cdm + 0.5359204)*(-n_s + 26.605696*om` | 1.00 | 1.908 +/- 0.012 | 0.875 | 0.872 +/- 0.007 | ok |
|  | {omega_b, A_s, n_s} | 3 | `0.0430672731054336*log((0.04689203*omega_b +` | 1.00 | 1.363 +/- 0.012 | 0.625 | 0.623 +/- 0.006 | ok |
|  | {omega_b, H0, n_s} | 3 | `56.4734180824034*(0.335590225578864*log(exp(` | 1.00 | 1.323 +/- 0.011 | 0.607 | 0.605 +/- 0.006 | ok |
|  | {omega_b, tau, n_s} | 3 | `omega_b*(n_s - 1.5624692) - 759.66046` | 1.00 | 1.316 +/- 0.013 | 0.603 | 0.602 +/- 0.007 | ok |
|  | {omega_cdm, H0, A_s} | 3 | `-omega_cdm**3/(omega_cdm**2*(H0 + 1.4876934)` | 1.00 | 0.027 +/- 0.003 | 0.012 | 0.012 +/- 0.001 | ok |
| S* | {omega_b, omega_cdm, A_s, n_s} | 4 | `log(log(log(exp(exp((omega_b/(omega_cdm - 0.` | 1.00 | 2.125 +/- 0.012 | 0.975 | 0.972 +/- 0.008 | ok |
|  | {omega_b, omega_cdm, tau, n_s} | 4 | `-omega_cdm + 0.625161995518996*exp(n_s - 26.` | 1.00 | 1.923 +/- 0.013 | 0.882 | 0.879 +/- 0.008 | ok |
|  | {omega_b, H0, tau, n_s} | 4 | `omega_b*(n_s - 1.5649613) + 779.9856` | 1.00 | 1.315 +/- 0.011 | 0.603 | 0.601 +/- 0.006 | ok |
|  | {omega_b, omega_cdm, H0, tau} | 4 | `-1.37307026130969*exp(exp(exp(-2*omega_cdm**` | 1.00 | 0.512 +/- 0.009 | 0.235 | 0.234 +/- 0.004 | ok |
|  | {omega_cdm, H0, tau, A_s} | 4 | `A_s**2/(tau - 0.011431578)**2 - A_s*omega_cd` | 1.00 | 0.029 +/- 0.005 | 0.013 | 0.013 +/- 0.002 | ok |
|  | {omega_b, omega_cdm, tau, A_s, n_s} | 5 | `exp((-8*n_s - 8*omega_b*(omega_cdm + 0.52580` | 1.00 | 2.134 +/- 0.014 | 0.979 | 0.976 +/- 0.008 | ok |
|  | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | `log(n_s*log(0.11159694/omega_b)*log(A_s/log(` | 1.00 | 2.114 +/- 0.014 | 0.970 | 0.967 +/- 0.008 | ok |
|  | {omega_b, H0, tau, A_s, n_s} | 5 | `12.4408386189433*(n_s*log(A_s) + 0.283514432` | 1.00 | 1.357 +/- 0.010 | 0.622 | 0.620 +/- 0.006 | ok |

## z3 — n_s

I(Z;theta) = 2.724 +/- 0.003 nat; MI(Z;mu) = 2.722 +/- 0.010; canonical eta_post = 0.493, eta_post_hat = 0.493 +/- 0.005; S* = `c43_S-ob-oc-H0-ns`, eta_post_hat = 0.931; residual audit failed: True -> phase6_needed = True.

| candidate | S | \|S\| | expr | finite | MI(Z;f) +/- | eta_post | eta_post_hat +/- | DPI |
|---|---|---:|---|---:|---|---:|---|---|
| canonical | {omega_b, omega_cdm, n_s} (from expr) | — | `log(omega_b)/(n_s + omega_cdm)` | 1.00 | 1.342 +/- 0.014 | 0.493 | 0.493 +/- 0.005 | ok |
| reference | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | `log(tau**2 + exp(-4.407752*n_s)*log(H0)/(ome` | 1.00 | 2.526 +/- 0.017 | 0.927 | 0.928 +/- 0.007 | ok |
|  | {n_s} | 1 | `1.0*n_s**4 - 2.33521995427032*n_s**2 + 20289` | 1.00 | 0.399 +/- 0.009 | 0.146 | 0.147 +/- 0.003 | ok |
|  | {omega_cdm} | 1 | `(omega_cdm - 0.09928881)**2` | 1.00 | 0.130 +/- 0.005 | 0.048 | 0.048 +/- 0.002 | ok |
|  | {omega_b} | 1 | `-omega_b - 0.03218924/(omega_b - 0.022519022` | 1.00 | 0.104 +/- 0.007 | 0.038 | 0.038 +/- 0.002 | ok |
|  | {omega_b, n_s} | 2 | `-0.127066336720944 - 4.55610447869809e-11/(0` | 1.00 | 0.713 +/- 0.011 | 0.262 | 0.262 +/- 0.004 | ok |
|  | {omega_cdm, n_s} | 2 | `log(n_s + 2.0668316*omega_cdm)` | 1.00 | 0.713 +/- 0.009 | 0.262 | 0.262 +/- 0.004 | ok |
|  | {omega_b, A_s} | 2 | `(6.09249603104346*A_s + omega_b*(omega_b - 0` | 1.00 | 0.128 +/- 0.006 | 0.047 | 0.047 +/- 0.002 | ok |
|  | {omega_cdm, A_s} | 2 | `(omega_cdm - 0.099475406)**2` | 1.00 | 0.117 +/- 0.006 | 0.043 | 0.043 +/- 0.002 | ok |
|  | {omega_b, omega_cdm, n_s} | 3 | `exp(38.9241277667367*omega_b) - log(n_s**4*o` | 1.00 | 1.937 +/- 0.011 | 0.711 | 0.711 +/- 0.005 | ok |
|  | {omega_b, H0, n_s} | 3 | `0.4133517*exp(exp((-2.4848341e-5*n_s*omega_b` | 1.00 | 0.731 +/- 0.011 | 0.268 | 0.269 +/- 0.004 | ok |
|  | {omega_cdm, A_s, n_s} | 3 | `-6.7703949692924*log(exp(5.01078484223454e-6` | 1.00 | 0.711 +/- 0.011 | 0.261 | 0.261 +/- 0.004 | ok |
|  | {omega_b, A_s, n_s} | 3 | `(n_s - 1.2664945)/omega_b` | 1.00 | 0.698 +/- 0.009 | 0.256 | 0.256 +/- 0.003 | ok |
|  | {omega_cdm, tau, A_s} | 3 | `0.772976919672024*A_s/(tau - 0.04585297)**2 ` | 1.00 | 0.128 +/- 0.006 | 0.047 | 0.047 +/- 0.002 | ok |
|  | {omega_b, tau, A_s} | 3 | `0.97157484/(-0.161084548287096*A_s/(omega_b ` | 1.00 | 0.117 +/- 0.006 | 0.043 | 0.043 +/- 0.002 | ok |
| S* | {omega_b, omega_cdm, H0, n_s} | 4 | `log(omega_b/((n_s + 2*omega_cdm)*(omega_b - ` | 1.00 | 2.535 +/- 0.013 | 0.931 | 0.931 +/- 0.006 | ok |
|  | {omega_b, omega_cdm, tau, n_s} | 4 | `omega_b**2*(n_s*omega_cdm + omega_cdm - 0.02` | 1.00 | 1.928 +/- 0.014 | 0.708 | 0.708 +/- 0.006 | ok |
|  | {omega_b, omega_cdm, A_s, n_s} | 4 | `(omega_b**2 + 0.005707082)*log(n_s**4*omega_` | 1.00 | 1.923 +/- 0.011 | 0.706 | 0.706 +/- 0.005 | ok |
|  | {omega_cdm, H0, tau, n_s} | 4 | `omega_cdm*(n_s - 0.7176179)/log(H0)` | 1.00 | 0.784 +/- 0.009 | 0.288 | 0.288 +/- 0.004 | ok |
|  | {omega_b, H0, tau, n_s} | 4 | `5.444962e-6*exp(n_s) + 5.444962e-6*log(omega` | 1.00 | 0.719 +/- 0.010 | 0.264 | 0.264 +/- 0.004 | ok |
|  | {omega_b, omega_cdm, H0, A_s} | 4 | `omega_b*(omega_cdm + 0.026575407) - 1493.072` | 1.00 | 0.285 +/- 0.008 | 0.105 | 0.105 +/- 0.003 | ok |
|  | {omega_b, omega_cdm, H0, tau, n_s} | 5 | `exp(2*H0*omega_b*exp(n_s)/(H0*omega_b*(log(o` | 1.00 | 2.552 +/- 0.013 | 0.937 | 0.937 +/- 0.006 | ok |
|  | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | `-0.5049022*n_s + omega_b - omega_cdm + 0.003` | 1.00 | 2.531 +/- 0.017 | 0.929 | 0.930 +/- 0.007 | ok |
|  | {omega_cdm, H0, tau, A_s, n_s} | 5 | `exp((A_s*H0 - (n_s + 2*omega_cdm)*(omega_cdm` | 1.00 | 0.763 +/- 0.011 | 0.280 | 0.280 +/- 0.004 | ok |

## z4 — tau (amplitude sector)

I(Z;theta) = 1.535 +/- 0.003 nat; MI(Z;mu) = 1.478 +/- 0.015; canonical eta_post = 0.811, eta_post_hat = 0.842 +/- 0.011; S* = `c28_S-ob-tau-As`, eta_post_hat = 0.957; residual audit failed: True -> phase6_needed = True.

| candidate | S | \|S\| | expr | finite | MI(Z;f) +/- | eta_post | eta_post_hat +/- | DPI |
|---|---|---:|---|---:|---|---:|---|---|
| canonical | {tau, ln10As} (from expr) | — | `-A_s/(tau - 0.4454238)` | 1.00 | 1.245 +/- 0.010 | 0.811 | 0.842 +/- 0.011 | ok |
| reference | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | `exp(omega_b + tau) + log((tau*log(-A_s**2/(t` | 1.00 | 1.376 +/- 0.014 | 0.896 | 0.931 +/- 0.013 | ok |
|  | {tau} | 1 | `(tau + 0.057059366)*(tau + log(tau) + 0.8349` | 1.00 | 0.420 +/- 0.012 | 0.273 | 0.284 +/- 0.009 | ok |
|  | {A_s} | 1 | `log(A_s)` | 1.00 | 0.261 +/- 0.010 | 0.170 | 0.177 +/- 0.007 | ok |
|  | {omega_cdm} | 1 | `(omega_cdm - 0.11134348)**2` | 1.00 | 0.015 +/- 0.003 | 0.010 | 0.010 +/- 0.002 | ok |
|  | {omega_b} | 1 | `0.02038491/(omega_b - 0.02038491)**2` | 1.00 | 0.014 +/- 0.003 | 0.009 | 0.009 +/- 0.002 | ok |
|  | {H0} | 1 | `-0.22077805/H0` | 1.00 | 0.000 +/- 0.000 | 0.000 | 0.000 +/- 0.000 | ok |
|  | {tau, A_s} | 2 | `-A_s/log(0.38789064*tau/(tau*exp(-595.272635` | 1.00 | 1.377 +/- 0.017 | 0.897 | 0.932 +/- 0.015 | ok |
|  | {omega_cdm, tau} | 2 | `omega_cdm*(log(log((1.55907515038449*tau + 0` | 1.00 | 0.443 +/- 0.011 | 0.288 | 0.299 +/- 0.008 | ok |
|  | {tau, n_s} | 2 | `21.270615551571*(tau - 3.92652815782611e-9)*` | 1.00 | 0.439 +/- 0.010 | 0.286 | 0.297 +/- 0.007 | ok |
|  | {H0, tau} | 2 | `log(-(tau - 0.10384653)**2 - 0.0062582484*lo` | 1.00 | 0.417 +/- 0.010 | 0.271 | 0.282 +/- 0.008 | ok |
|  | {H0, A_s} | 2 | `-log(1.6093085e-5*log(A_s) + 5.6511736)` | 1.00 | 0.266 +/- 0.011 | 0.173 | 0.180 +/- 0.007 | ok |
|  | {omega_b, A_s} | 2 | `0.39432669564521*exp(2*omega_b)/A_s` | 1.00 | 0.255 +/- 0.009 | 0.166 | 0.173 +/- 0.007 | ok |
|  | {A_s, n_s} | 2 | `A_s*(n_s**2 - 0.9250428)**2*log(n_s**2/A_s)/` | 1.00 | 0.244 +/- 0.010 | 0.159 | 0.165 +/- 0.007 | ok |
| S* | {omega_b, tau, A_s} | 3 | `A_s*log(log(tau) + 8.529404 + 8.020664040682` | 1.00 | 1.414 +/- 0.014 | 0.921 | 0.957 +/- 0.014 | ok |
|  | {omega_b, omega_cdm, tau} | 3 | `(-tau**4*log(omega_b)**4 + tau + 0.2760499)*` | 1.00 | 0.425 +/- 0.010 | 0.277 | 0.288 +/- 0.007 | ok |
|  | {omega_b, H0, tau, A_s} | 4 | `-A_s*(omega_b**4*(log(tau) + 11.781949) + 5.` | 1.00 | 1.423 +/- 0.012 | 0.927 | 0.963 +/- 0.013 | ok |
|  | {omega_cdm, H0, tau, A_s} | 4 | `0.0103309588329508*A_s/(((tau + 0.189403325)` | 1.00 | 1.406 +/- 0.013 | 0.916 | 0.952 +/- 0.013 | ok |
|  | {omega_b, tau, A_s, n_s} | 4 | `A_s*(n_s - omega_b)**2*log(tau + 0.078433886` | 1.00 | 1.401 +/- 0.012 | 0.913 | 0.948 +/- 0.013 | ok |
|  | {omega_b, omega_cdm, tau, A_s} | 4 | `-A_s*exp(-2*omega_b)/((tau - 0.22419287)*(-t` | 1.00 | 1.396 +/- 0.014 | 0.909 | 0.945 +/- 0.014 | ok |
|  | {omega_cdm, tau, A_s, n_s} | 4 | `exp(tau) - log(A_s*log(-n_s*tau/(A_s*(8079.6` | 1.00 | 1.391 +/- 0.012 | 0.906 | 0.941 +/- 0.013 | ok |
|  | {H0, tau, A_s, n_s} | 4 | `A_s/(log(tau*((tau - 0.0993644212953972)**2 ` | 1.00 | 1.390 +/- 0.016 | 0.905 | 0.941 +/- 0.015 | ok |
|  | {omega_cdm, H0, tau, n_s} | 4 | `166.650000851896*(0.07746354*omega_cdm + tau` | 1.00 | 0.453 +/- 0.013 | 0.295 | 0.307 +/- 0.009 | ok |
|  | {omega_b, omega_cdm, H0, tau} | 4 | `(tau + (omega_cdm*tau + 0.063239954)*log((-0` | 1.00 | 0.407 +/- 0.010 | 0.265 | 0.276 +/- 0.007 | ok |
|  | {omega_b, omega_cdm, tau, n_s} | 4 | `log(n_s + (0.000498020548507876*omega_cdm**2` | 1.00 | 0.404 +/- 0.010 | 0.263 | 0.274 +/- 0.007 | ok |
|  | {omega_cdm, H0, tau, A_s, n_s} | 5 | `A_s*log((n_s + 2.0463479)/(log(-log(tau)) - ` | 1.00 | 1.424 +/- 0.014 | 0.928 | 0.964 +/- 0.014 | ok |
|  | {omega_b, omega_cdm, H0, tau, A_s} | 5 | `-A_s*omega_b**2/((tau + 0.035367183)*(omega_` | 1.00 | 1.416 +/- 0.013 | 0.922 | 0.958 +/- 0.013 | ok |
|  | {omega_b, omega_cdm, H0, tau, n_s} | 5 | `(-omega_cdm + 29.1815565558993*tau**2)/(tau*` | 1.00 | 0.450 +/- 0.008 | 0.293 | 0.304 +/- 0.006 | ok |

## z5 — amplitude (A_s, tau)

I(Z;theta) = 4.176 +/- 0.003 nat; MI(Z;mu) = 4.180 +/- 0.012; canonical eta_post = 0.290, eta_post_hat = 0.289 +/- 0.003; S* = `allparams`, eta_post_hat = 0.883; residual audit failed: True -> phase6_needed = True.

| candidate | S | \|S\| | expr | finite | MI(Z;f) +/- | eta_post | eta_post_hat +/- | DPI |
|---|---|---:|---|---:|---|---:|---|---|
| canonical | {tau, ln10As} (from expr) | — | `A_s*exp(-2*tau)` | 1.00 | 1.209 +/- 0.011 | 0.290 | 0.289 +/- 0.003 | ok |
| reference S* | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | `omega_b - 0.17572255*log(exp((2*n_s*tau + 2.` | 1.00 | 3.690 +/- 0.013 | 0.884 | 0.883 +/- 0.004 | ok |
|  | {A_s} | 1 | `6.871011e-6*log(A_s) - 6.006013` | 1.00 | 0.383 +/- 0.008 | 0.092 | 0.092 +/- 0.002 | ok |
|  | {tau} | 1 | `tau**2` | 1.00 | 0.240 +/- 0.008 | 0.058 | 0.058 +/- 0.002 | ok |
|  | {tau, A_s} | 2 | `log(0.43541218424929*A_s**2/(tau - 0.1292972` | 1.00 | 1.181 +/- 0.014 | 0.283 | 0.282 +/- 0.004 | ok |
|  | {omega_cdm, A_s} | 2 | `A_s*log(omega_cdm)` | 1.00 | 0.419 +/- 0.010 | 0.100 | 0.100 +/- 0.002 | ok |
|  | {H0, A_s} | 2 | `log(H0)/A_s` | 1.00 | 0.407 +/- 0.009 | 0.097 | 0.097 +/- 0.002 | ok |
|  | {omega_b, A_s} | 2 | `41.2963914447567*(0.078111039684796 + exp(-A` | 1.00 | 0.372 +/- 0.009 | 0.089 | 0.089 +/- 0.002 | ok |
|  | {omega_b, tau} | 2 | `0.351968628525182*omega_b*tau**3/(0.59326944` | 1.00 | 0.272 +/- 0.008 | 0.065 | 0.065 +/- 0.002 | ok |
|  | {omega_cdm, tau, A_s} | 3 | `exp(8.99932081281424*(0.333345911585731*log(` | 1.00 | 1.660 +/- 0.012 | 0.398 | 0.397 +/- 0.003 | ok |
|  | {omega_b, omega_cdm, A_s} | 3 | `(A_s + 7.5001597)*(exp(A_s**0.54432831536285` | 1.00 | 0.410 +/- 0.009 | 0.098 | 0.098 +/- 0.002 | ok |
|  | {omega_cdm, tau, n_s} | 3 | `-0.759441946172441*log(0.55575466*omega_cdm*` | 1.00 | 0.295 +/- 0.009 | 0.071 | 0.071 +/- 0.002 | ok |
|  | {omega_b, tau, n_s} | 3 | `tau**2 + 4527.2505` | 1.00 | 0.277 +/- 0.009 | 0.066 | 0.066 +/- 0.002 | ok |
|  | {omega_cdm, H0, tau, A_s} | 4 | `-4.55264875659402*exp(0.014197185/log(A_s*ex` | 1.00 | 2.213 +/- 0.014 | 0.530 | 0.529 +/- 0.004 | ok |
|  | {omega_b, omega_cdm, A_s, n_s} | 4 | `-1.008317*A_s*(omega_b - omega_cdm + 0.32610` | 1.00 | 0.422 +/- 0.009 | 0.101 | 0.101 +/- 0.002 | ok |
|  | {omega_b, omega_cdm, H0, tau} | 4 | `H0*(omega_cdm**2 + (omega_cdm + tau)**2)` | 1.00 | 0.316 +/- 0.009 | 0.076 | 0.076 +/- 0.002 | ok |
|  | {omega_cdm, H0, tau, A_s, n_s} | 5 | `log((log(H0) + 0.4462526)*exp(2*tau + 2.7900` | 1.00 | 2.760 +/- 0.011 | 0.661 | 0.660 +/- 0.003 | ok |
|  | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | `A_s*(-n_s + log(omega_cdm))/log(H0)` | 1.00 | 0.463 +/- 0.009 | 0.111 | 0.111 +/- 0.002 | ok |
|  | {omega_b, omega_cdm, H0, tau, n_s} | 5 | `-3.16663601890773*n_s - 38.3510567664239*ome` | 1.00 | 0.293 +/- 0.007 | 0.070 | 0.070 +/- 0.002 | ok |

# Gate G3

DPI: PASS (0 violation(s)).

Amplitude latent z5: I = 4.176 +/- 0.003 nat; canonical eta_post = 0.290 +/- 0.003, eta_post_hat = 0.289 +/- 0.003; S* eta_post_hat = 0.883.

**Branch: residual is genuinely stored information (eta_post_hat < 0.95) — Phase 6 matters**

**Gate G3: PASS**

Phase-6 scope (residual audit failed AND eta_post_hat < 0.95): z0, z1, z2, z3, z4, z5.

---
_Generated by `scripts/posterior_ceiling.py`._
