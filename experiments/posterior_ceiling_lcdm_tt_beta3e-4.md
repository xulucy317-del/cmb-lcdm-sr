# Posterior ceiling — `lcdm_tt_beta3e-4` (roadmap Phase 5, gate G3)

The intrinsic ceiling I(Z_k; theta) = H(Z_k) − E[1/2 ln(2 pi e sigma_k^2)] from the cached encoder logvars (clamped to (−10, 10) as in the model): H(Z_k) from 4 posterior draws per row over T1 u T2, 1-D GMM (BIC over K <= 5) fit on half the draws, held-out cross-entropy on the rest, SE by joint row bootstrap (exact on the synthetic positive control, I_true = 1.124 vs 1.126 +/- 0.016). Numerators MI(Z_k; f) on a fresh posterior draw over T2 (confirmatory tier). Because the GMM-MI numerator over-estimates near-sufficient relations by ~7% on the same control, each latent also scores the same-estimator ceiling proxy MI(Z_k; mu_k): **eta_post = MI/I** (principled headline), **eta_post_hat = MI/MI(Z;mu)** (same-estimator ratio, shared bias cancels — drives the frozen 0.95 demotion rule and phase6_needed), DPI = MI(Z;f) <= MI(Z;mu) + 2 SE. eta_post_mu = MI(Z;mu)/I is the fraction of the analytic ceiling the estimator can even see (the practical top of the eta_post scale). Var(e1)/E[sigma^2] compares the Phase-3 residual to the posterior noise floor — the direct 'is the leftover modulation above the noise' readout.

## Noise table

| latent | role | E[sigma^2] | med sigma | Var(mu) | SNR | clamp frac | I_gauss |
|---|---|---:|---:|---:|---:|---:|---:|
| z0 | omega_b | 1.759e-02 | 1.326e-01 | 0.974 | 5.535e+01 | 0.000 | 2.016 |
| z1 | omega_cdm | 1.665e-01 | 3.822e-01 | 0.845 | 5.077e+00 | 0.000 | 0.902 |
| z2 | amplitude (A_s, tau) | 1.788e-04 | 1.330e-02 | 0.981 | 5.491e+03 | 0.000 | 4.306 |
| z3 | n_s | 4.793e-03 | 6.917e-02 | 0.981 | 2.047e+02 | 0.000 | 2.663 |
| z4 | H0 | 1.007e-03 | 3.179e-02 | 0.993 | 9.865e+02 | 0.000 | 3.448 |

## Intrinsic ceilings

| latent | H(Z) | H(Z\|theta) | I(Z;theta) +/- SE | K | I_gauss | MI(Z;mu) | eta_post_mu | I_plat (SR) | I/plat | Var(e1)/E[s2] |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| z0 | 1.382 | -0.602 | 1.984 +/- 0.002 | 3 | 2.016 | 2.038 | 1.03 | 3.570 | 0.56 | 5.29 |
| z1 | 1.423 | 0.504 | 0.919 +/- 0.003 | 2 | 0.902 | 0.909 | 0.99 | 2.515 | 0.37 | 0.48 |
| z2 | 1.407 | -2.896 | 4.304 +/- 0.003 | 2 | 4.306 | 4.305 | 1.00 | 4.175 | 1.03 | 289.43 |
| z3 | 1.395 | -1.252 | 2.646 +/- 0.003 | 5 | 2.663 | 2.659 | 1.00 | 3.147 | 0.84 | 17.19 |
| z4 | 1.409 | -2.032 | 3.441 +/- 0.003 | 2 | 3.448 | 3.435 | 1.00 | 4.313 | 0.80 | 77.91 |

## z0 — omega_b

I(Z;theta) = 1.984 +/- 0.002 nat; MI(Z;mu) = 2.038 +/- 0.011; canonical eta_post = 0.545, eta_post_hat = 0.531 +/- 0.006; S* = `c58_S-ob-oc-H0-As-ns`, eta_post_hat = 0.988; residual audit failed: True -> phase6_needed = True.

| candidate | S | \|S\| | expr | finite | MI(Z;f) +/- | eta_post | eta_post_hat +/- | DPI |
|---|---|---:|---|---:|---|---:|---|---|
| canonical | {omega_b, n_s} (from expr) | — | `n_s/omega_b` | 1.00 | 1.082 +/- 0.010 | 0.545 | 0.531 +/- 0.006 | ok |
| reference | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | `log(n_s*(omega_b*(tau**2 + log(H0)) + 0.4207` | 1.00 | 1.998 +/- 0.012 | 1.007 | 0.981 +/- 0.008 | ok |
|  | {omega_b} | 1 | `log(omega_b)` | 1.00 | 0.885 +/- 0.013 | 0.446 | 0.434 +/- 0.007 | ok |
|  | {n_s} | 1 | `-n_s*(n_s - 0.9839874)/(159595.72*n_s - 1570` | 1.00 | 0.042 +/- 0.004 | 0.021 | 0.021 +/- 0.002 | ok |
|  | {omega_b, n_s} | 2 | `(609.5965*n_s + omega_b + 350.3551033152)/(n` | 1.00 | 1.197 +/- 0.014 | 0.604 | 0.588 +/- 0.007 | ok |
|  | {omega_b, omega_cdm, n_s} | 3 | `omega_b*omega_cdm**2/(3.55682418197613*omega` | 1.00 | 1.732 +/- 0.013 | 0.873 | 0.850 +/- 0.008 | ok |
|  | {omega_b, H0, n_s} | 3 | `log(-H0 + 0.08971138*(n_s + 0.6861281)**2/om` | 1.00 | 1.292 +/- 0.011 | 0.651 | 0.634 +/- 0.006 | ok |
|  | {omega_b, A_s, n_s} | 3 | `exp(-omega_b/(n_s*log(A_s) - 13.440298))` | 1.00 | 1.218 +/- 0.010 | 0.614 | 0.598 +/- 0.006 | ok |
|  | {omega_b, tau, n_s} | 3 | `12.3858787654462*omega_b/log(0.18626378/n_s)` | 1.00 | 1.192 +/- 0.010 | 0.601 | 0.585 +/- 0.006 | ok |
|  | {omega_b, tau, A_s} | 3 | `log(exp(exp(0.569928748328717*exp(4.35936975` | 1.00 | 0.879 +/- 0.012 | 0.443 | 0.431 +/- 0.006 | ok |
|  | {omega_b, omega_cdm, H0, n_s} | 4 | `-1.9012555/log(-0.0056098355*H0/omega_cdm - ` | 1.00 | 1.923 +/- 0.012 | 0.969 | 0.944 +/- 0.008 | ok |
|  | {omega_b, omega_cdm, A_s, n_s} | 4 | `-omega_b/((n_s + 0.59309566)*(log(A_s) - log` | 1.00 | 1.759 +/- 0.011 | 0.887 | 0.863 +/- 0.007 | ok |
|  | {omega_b, omega_cdm, tau, n_s} | 4 | `exp(-0.09903916*omega_b**2/(-0.24773481*n_s*` | 1.00 | 1.720 +/- 0.013 | 0.867 | 0.844 +/- 0.008 | ok |
|  | {omega_b, tau, A_s, n_s} | 4 | `omega_b/(n_s*log(A_s) - 13.969693)` | 1.00 | 1.205 +/- 0.009 | 0.607 | 0.591 +/- 0.006 | ok |
| S* | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | `log(log(n_s*(log(A_s) - log(omega_b))*(H0 - ` | 1.00 | 2.013 +/- 0.013 | 1.015 | 0.988 +/- 0.009 | ok |
|  | {omega_b, omega_cdm, H0, tau, n_s} | 5 | `omega_b*(tau*(n_s + 0.54691976) + 83.66754*e` | 1.00 | 1.914 +/- 0.013 | 0.965 | 0.939 +/- 0.008 | ok |
|  | {omega_b, omega_cdm, tau, A_s, n_s} | 5 | `log((-0.009269168*n_s + omega_b*omega_cdm - ` | 1.00 | 1.762 +/- 0.014 | 0.888 | 0.864 +/- 0.008 | ok |

## z1 — omega_cdm

I(Z;theta) = 0.919 +/- 0.003 nat; MI(Z;mu) = 0.909 +/- 0.014; canonical eta_post = 0.761, eta_post_hat = 0.770 +/- 0.018; S* = `allparams`, eta_post_hat = 0.955; residual audit failed: True -> phase6_needed = True.

| candidate | S | \|S\| | expr | finite | MI(Z;f) +/- | eta_post | eta_post_hat +/- | DPI |
|---|---|---:|---|---:|---|---:|---|---|
| canonical | {omega_b, omega_cdm, H0, ln10As, n_s} (from expr) | — | `H0**2*n_s**2*omega_b/(A_s*omega_cdm**2)` | 1.00 | 0.699 +/- 0.012 | 0.761 | 0.770 +/- 0.018 | ok |
| reference S* | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | `-tau + log(H0**2*omega_b*exp(2*exp(n_s))/(A_` | 1.00 | 0.868 +/- 0.012 | 0.944 | 0.955 +/- 0.020 | ok |
|  | {omega_cdm} | 1 | `1.2657905*omega_cdm + 34847.3071522114*(0.01` | 1.00 | 0.223 +/- 0.009 | 0.243 | 0.246 +/- 0.010 | ok |
|  | {omega_cdm, H0} | 2 | `-omega_cdm + 60322.683244926 - 493.797503445` | 1.00 | 0.399 +/- 0.009 | 0.434 | 0.439 +/- 0.012 | ok |
|  | {omega_cdm, n_s} | 2 | `log(n_s/omega_cdm - 5.852781/n_s)**2` | 1.00 | 0.339 +/- 0.009 | 0.368 | 0.372 +/- 0.012 | ok |
|  | {omega_cdm, H0, n_s} | 3 | `1518.7882*n_s**2/omega_cdm + (H0 + exp(n_s))` | 1.00 | 0.588 +/- 0.010 | 0.640 | 0.647 +/- 0.015 | ok |
|  | {omega_cdm, H0, A_s} | 3 | `exp(A_s*H0*(omega_cdm - 1)/(omega_cdm*(log(A` | 1.00 | 0.452 +/- 0.012 | 0.491 | 0.497 +/- 0.015 | ok |
|  | {omega_cdm, A_s, n_s} | 3 | `log(log(((n_s - 0.66611344)/(omega_cdm - 0.0` | 1.00 | 0.385 +/- 0.010 | 0.418 | 0.423 +/- 0.012 | ok |
|  | {omega_b, omega_cdm, H0, n_s} | 4 | `H0*(-n_s**2 + omega_b + 1.5324805*omega_cdm)` | 1.00 | 0.704 +/- 0.012 | 0.766 | 0.774 +/- 0.017 | ok |
|  | {omega_cdm, H0, A_s, n_s} | 4 | `exp(2*log(log((H0*(n_s - omega_cdm)**2 - 27.` | 1.00 | 0.699 +/- 0.013 | 0.760 | 0.769 +/- 0.019 | ok |
|  | {omega_cdm, H0, tau, n_s} | 4 | `H0*(-n_s**2 + omega_cdm*exp(3.07667381901029` | 1.00 | 0.639 +/- 0.011 | 0.695 | 0.703 +/- 0.017 | ok |
|  | {omega_b, omega_cdm, H0, A_s} | 4 | `log((omega_b*(H0 - 33.75204) + 6.7582*(omega` | 1.00 | 0.510 +/- 0.010 | 0.555 | 0.562 +/- 0.014 | ok |
|  | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | `-1.2091329/(log(omega_b*(0.316690568359496*H` | 1.00 | 0.840 +/- 0.013 | 0.914 | 0.925 +/- 0.020 | ok |

## z2 — amplitude (A_s, tau)

I(Z;theta) = 4.304 +/- 0.003 nat; MI(Z;mu) = 4.305 +/- 0.014; canonical eta_post = 0.347, eta_post_hat = 0.347 +/- 0.003; S* = `allparams`, eta_post_hat = 0.857; residual audit failed: True -> phase6_needed = True.

| candidate | S | \|S\| | expr | finite | MI(Z;f) +/- | eta_post | eta_post_hat +/- | DPI |
|---|---|---:|---|---:|---|---:|---|---|
| canonical | {omega_cdm, H0, tau, ln10As} (from expr) | — | `A_s/log(H0*(omega_cdm + tau))` | 1.00 | 1.494 +/- 0.013 | 0.347 | 0.347 +/- 0.003 | ok |
| reference S* | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | `log((H0*omega_cdm + 0.72941446)*exp(-n_s + 4` | 1.00 | 3.689 +/- 0.011 | 0.857 | 0.857 +/- 0.004 | ok |
|  | {A_s} | 1 | `-3.5091463e-5*log(-log(A_s)) - 1.71274320225` | 1.00 | 0.323 +/- 0.010 | 0.075 | 0.075 +/- 0.002 | ok |
|  | {tau} | 1 | `tau**2` | 1.00 | 0.209 +/- 0.007 | 0.048 | 0.048 +/- 0.002 | ok |
|  | {tau, A_s} | 2 | `A_s*(tau - 0.024579916)**2/(A_s + (tau - 0.0` | 1.00 | 0.819 +/- 0.010 | 0.190 | 0.190 +/- 0.002 | ok |
|  | {omega_cdm, A_s} | 2 | `-log(omega_cdm - 0.29198268*log(A_s) + 18044` | 1.00 | 0.398 +/- 0.009 | 0.093 | 0.093 +/- 0.002 | ok |
|  | {H0, A_s} | 2 | `log(H0 - 22.374554)/A_s` | 1.00 | 0.397 +/- 0.008 | 0.092 | 0.092 +/- 0.002 | ok |
|  | {omega_b, tau} | 2 | `tau*(1.3587387*omega_b*(tau - 0.017220784) +` | 1.00 | 0.218 +/- 0.008 | 0.051 | 0.051 +/- 0.002 | ok |
|  | {tau, n_s} | 2 | `tau + (tau - 6.5895e-5/(tau - 0.02800559))**` | 1.00 | 0.212 +/- 0.008 | 0.049 | 0.049 +/- 0.002 | ok |
|  | {H0, tau, A_s} | 3 | `-5.53001701530935*A_s*exp(-(tau + log(log(H0` | 1.00 | 1.147 +/- 0.010 | 0.267 | 0.266 +/- 0.003 | ok |
|  | {omega_cdm, tau, A_s} | 3 | `A_s*(tau - 0.5744104)*log(omega_cdm)` | 1.00 | 1.129 +/- 0.011 | 0.262 | 0.262 +/- 0.003 | ok |
|  | {omega_cdm, H0, A_s} | 3 | `2.75907161205555*exp(0.0985992689594882/log(` | 1.00 | 0.506 +/- 0.009 | 0.117 | 0.117 +/- 0.002 | ok |
|  | {tau, A_s, n_s} | 3 | `A_s*(n_s + exp(A_s/(tau - 0.1292945)**2))*ex` | 1.00 | n/a +/- n/a | n/a | n/a +/- n/a | n/a |
|  | {omega_cdm, H0, tau, A_s} | 4 | `106.349821886025*(0.096968709651926*tau + 1)` | 1.00 | 1.873 +/- 0.013 | 0.435 | 0.435 +/- 0.003 | ok |
|  | {omega_cdm, tau, A_s, n_s} | 4 | `A_s*exp(-2*tau)*log(omega_cdm/n_s)` | 1.00 | 1.226 +/- 0.011 | 0.285 | 0.285 +/- 0.003 | ok |
|  | {omega_b, H0, tau, A_s} | 4 | `0.49686998*A_s*exp(-2*tau + 9.217652*exp(ome` | 1.00 | 1.226 +/- 0.010 | 0.285 | 0.285 +/- 0.002 | ok |
|  | {omega_b, omega_cdm, tau, A_s} | 4 | `A_s*exp(-2*tau)*log(omega_cdm)/log(omega_b)` | 1.00 | 1.204 +/- 0.010 | 0.280 | 0.280 +/- 0.003 | ok |
|  | {H0, tau, A_s, n_s} | 4 | `0.0928945240831609*(1.20169968745718e-7*n_s*` | 1.00 | 1.150 +/- 0.013 | 0.267 | 0.267 +/- 0.003 | ok |
|  | {omega_cdm, H0, tau, A_s, n_s} | 5 | `108.546830053561*(0.0959823607456716*tau + 1` | 1.00 | 2.211 +/- 0.011 | 0.514 | 0.514 +/- 0.003 | ok |
|  | {omega_b, omega_cdm, H0, tau, A_s} | 5 | `log(log(-(omega_b - 0.068843)*(H0*omega_cdm ` | 1.00 | 2.202 +/- 0.009 | 0.512 | 0.512 +/- 0.003 | ok |
|  | {omega_b, omega_cdm, tau, A_s, n_s} | 5 | `A_s*exp(-(n_s*(-9.12020027230182*omega_b + 2` | 1.00 | 1.344 +/- 0.009 | 0.312 | 0.312 +/- 0.002 | ok |
|  | {omega_b, H0, tau, A_s, n_s} | 5 | `A_s*exp(-2*tau)/((omega_b - 0.12984979)*log(` | 1.00 | 1.344 +/- 0.011 | 0.312 | 0.312 +/- 0.003 | ok |

## z3 — n_s

I(Z;theta) = 2.646 +/- 0.003 nat; MI(Z;mu) = 2.659 +/- 0.010; canonical eta_post = 0.449, eta_post_hat = 0.447 +/- 0.004; S* = `c57_S-ob-oc-H0-tau-ns`, eta_post_hat = 0.928; residual audit failed: True -> phase6_needed = True.

| candidate | S | \|S\| | expr | finite | MI(Z;f) +/- | eta_post | eta_post_hat +/- | DPI |
|---|---|---:|---|---:|---|---:|---|---|
| canonical | {omega_cdm, n_s} (from expr) | — | `n_s + omega_cdm` | 1.00 | 1.189 +/- 0.010 | 0.449 | 0.447 +/- 0.004 | ok |
| reference | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | `n_s + log(n_s*(omega_b + 0.122276284)*(H0*(o` | 1.00 | 2.481 +/- 0.015 | 0.938 | 0.933 +/- 0.007 | ok |
|  | {n_s} | 1 | `2.26354738078266*exp(-5.359835e-5*exp(-n_s))` | 1.00 | 0.585 +/- 0.010 | 0.221 | 0.220 +/- 0.004 | ok |
|  | {A_s} | 1 | `-3.94632249814609*(A_s + 0.00108626425534677` | 1.00 | 0.001 +/- 0.001 | 0.000 | 0.000 +/- 0.000 | ok |
|  | {omega_cdm, n_s} | 2 | `exp((n_s + omega_cdm)**2)*log(4.5259075*n_s ` | 1.00 | 1.690 +/- 0.012 | 0.639 | 0.636 +/- 0.005 | ok |
|  | {H0, n_s} | 2 | `0.000153517274378945*H0/(0.0123902088109501*` | 1.00 | 0.612 +/- 0.008 | 0.231 | 0.230 +/- 0.003 | ok |
|  | {tau, n_s} | 2 | `-4.34422534359579*(0.770185325073661*log(0.6` | 1.00 | 0.578 +/- 0.011 | 0.218 | 0.217 +/- 0.004 | ok |
|  | {omega_b, omega_cdm, n_s} | 3 | `-omega_b**4 + 0.07082517 + 0.000314219230012` | 1.00 | 2.059 +/- 0.013 | 0.778 | 0.775 +/- 0.006 | ok |
|  | {omega_cdm, H0, n_s} | 3 | `log(227.438762831329*n_s**2*(0.0663082792583` | 1.00 | 1.853 +/- 0.013 | 0.700 | 0.697 +/- 0.005 | ok |
|  | {omega_cdm, A_s, n_s} | 3 | `-exp(exp(-0.11377507*log(-omega_cdm/(n_s**2 ` | 1.00 | 1.713 +/- 0.011 | 0.647 | 0.644 +/- 0.005 | ok |
|  | {H0, tau, n_s} | 3 | `0.40121186*log(exp((0.0044544354*n_s - 0.004` | 1.00 | 0.583 +/- 0.008 | 0.220 | 0.219 +/- 0.003 | ok |
|  | {tau, A_s, n_s} | 3 | `(-8.5201961451395*n_s + (1.63324380217459*n_` | 1.00 | 0.578 +/- 0.010 | 0.218 | 0.217 +/- 0.004 | ok |
|  | {omega_b, omega_cdm, H0, n_s} | 4 | `n_s + 1.9523982*omega_cdm - exp(28.082127931` | 1.00 | 2.435 +/- 0.011 | 0.920 | 0.916 +/- 0.006 | ok |
|  | {omega_b, omega_cdm, tau, n_s} | 4 | `log(omega_cdm*exp(4.427859*n_s)/(tau - 5.093` | 1.00 | 2.058 +/- 0.013 | 0.778 | 0.774 +/- 0.006 | ok |
|  | {omega_b, omega_cdm, A_s, n_s} | 4 | `47.861794*(0.0208934917901322*(n_s + omega_b` | 1.00 | 2.032 +/- 0.014 | 0.768 | 0.764 +/- 0.006 | ok |
|  | {H0, tau, A_s, n_s} | 4 | `4.13569309525967*exp(0.5990084*(n_s - 0.9119` | 1.00 | 0.628 +/- 0.007 | 0.237 | 0.236 +/- 0.003 | ok |
| S* | {omega_b, omega_cdm, H0, tau, n_s} | 5 | `H0*(omega_cdm + (n_s - tau**3)*(omega_cdm + ` | 1.00 | 2.469 +/- 0.011 | 0.933 | 0.928 +/- 0.005 | ok |
|  | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | `exp(omega_b) + log(-log((H0*(omega_b + 0.003` | 1.00 | 2.456 +/- 0.013 | 0.928 | 0.924 +/- 0.006 | ok |
|  | {omega_b, omega_cdm, tau, A_s, n_s} | 5 | `10.643872594646*(0.306513894550781*tau**2 - ` | 1.00 | 2.052 +/- 0.013 | 0.775 | 0.772 +/- 0.006 | ok |

## z4 — H0

I(Z;theta) = 3.441 +/- 0.003 nat; MI(Z;mu) = 3.435 +/- 0.017; canonical eta_post = 0.370, eta_post_hat = 0.371 +/- 0.004; S* = `allparams`, eta_post_hat = 0.937; residual audit failed: True -> phase6_needed = True.

| candidate | S | \|S\| | expr | finite | MI(Z;f) +/- | eta_post | eta_post_hat +/- | DPI |
|---|---|---:|---|---:|---|---:|---|---|
| canonical | {omega_cdm, H0, tau, ln10As} (from expr) | — | `A_s*H0**2*omega_cdm*exp(-2*tau)` | 1.00 | 1.273 +/- 0.013 | 0.370 | 0.371 +/- 0.004 | ok |
| reference S* | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | `n_s - omega_cdm - log(A_s*H0*omega_cdm*(0.04` | 1.00 | 3.220 +/- 0.013 | 0.936 | 0.937 +/- 0.006 | ok |
|  | {H0} | 1 | `-3.64982775134539e+15*(H0 + 0.00021219947865` | 1.00 | 0.486 +/- 0.009 | 0.141 | 0.141 +/- 0.003 | ok |
|  | {omega_cdm, H0} | 2 | `6.78883971735916e-5*omega_cdm**2/(0.28876212` | 1.00 | 0.656 +/- 0.009 | 0.191 | 0.191 +/- 0.003 | ok |
|  | {omega_cdm, H0, A_s} | 3 | `78.1306204324*A_s*omega_cdm*(0.0110847700026` | 1.00 | 0.944 +/- 0.012 | 0.274 | 0.275 +/- 0.004 | ok |
|  | {omega_cdm, H0, tau} | 3 | `-(H0 - 1.1845531)*log(-H0*(tau - 0.2379105)*` | 1.00 | 0.838 +/- 0.011 | 0.244 | 0.244 +/- 0.003 | ok |
|  | {H0, tau, A_s} | 3 | `exp(126.666831492496*A_s*(0.0888522738540811` | 1.00 | 0.814 +/- 0.009 | 0.237 | 0.237 +/- 0.003 | ok |
|  | {omega_b, omega_cdm, H0} | 3 | `85.9256218619839*omega_cdm/(H0**4*(omega_b -` | 1.00 | 0.763 +/- 0.011 | 0.222 | 0.222 +/- 0.003 | ok |
|  | {omega_cdm, H0, n_s} | 3 | `log(n_s/omega_cdm)/H0` | 1.00 | 0.688 +/- 0.010 | 0.200 | 0.200 +/- 0.003 | ok |
|  | {omega_cdm, H0, tau, A_s} | 4 | `(A_s*H0**4*omega_cdm - 0.0654118365203833*ta` | 1.00 | 1.344 +/- 0.010 | 0.391 | 0.391 +/- 0.004 | ok |
|  | {omega_b, omega_cdm, H0, A_s} | 4 | `(H0 - (omega_cdm + log(42.939632*A_s*omega_c` | 1.00 | 1.152 +/- 0.009 | 0.335 | 0.335 +/- 0.003 | ok |
|  | {omega_b, omega_cdm, H0, tau} | 4 | `(-omega_b - 0.25901407*omega_cdm)/(H0*omega_` | 1.00 | 1.076 +/- 0.009 | 0.313 | 0.313 +/- 0.003 | ok |
|  | {omega_b, omega_cdm, H0, tau, A_s} | 5 | `(omega_cdm - log(-H0**2 + omega_b*exp(2*tau)` | 1.00 | 2.197 +/- 0.009 | 0.638 | 0.640 +/- 0.004 | ok |

# Gate G3

DPI: PASS (0 violation(s)).

Amplitude latent z2: I = 4.304 +/- 0.003 nat; canonical eta_post = 0.347 +/- 0.003, eta_post_hat = 0.347 +/- 0.003; S* eta_post_hat = 0.857.

**Branch: residual is genuinely stored information (eta_post_hat < 0.95) — Phase 6 matters**

**Gate G3: PASS**

Phase-6 scope (residual audit failed AND eta_post_hat < 0.95): z0, z1, z2, z3, z4.

---
_Generated by `scripts/posterior_ceiling.py`._
