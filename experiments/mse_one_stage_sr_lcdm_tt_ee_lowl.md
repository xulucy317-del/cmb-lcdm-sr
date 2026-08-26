# One-stage MSE symbolic reconstruction — `lcdm_tt_ee_lowl`

Frozen direct latent reconstruction with T0-selected equations, T1-only calibrations, and T2 confirmation. The existing interaction-aware hierarchy is recomputed on T2; its stored T1 combined R² is never reused as a confirmatory score.

| latent | classification | flags | MSE20 | MSE30 | MSE40 | IA hierarchy MSE | objective | capacity | f2 absorbed | matches IA | saturated | R_SR |
|---:|---|---|---:|---:|---:|---:|---|---|---|---|---|---:|
| z0 | no capacity gain | symbolically-stable | 0.04372 | 0.04117 | 0.05147 | 0.04287 | PASS | FAIL | FAIL | FAIL | FAIL | 1.00 |
| z1 | partial absorption | symbolically-stable | 0.01821 | 0.01508 | 0.01142 | 0.005481 | PASS | PASS | FAIL | FAIL | PASS | 1.00 |
| z2 | no capacity gain | symbolically-stable | 0.006186 | 0.00471 | 0.001991 | 0.002812 | PASS | FAIL | FAIL | PASS | FAIL | 1.00 |
| z3 | partial absorption | symbolically-stable | 0.00364 | 0.003547 | 0.002217 | 0.007671 | PASS | PASS | FAIL | PASS | FAIL | 1.00 |
| z4 | partial absorption | symbolically-stable | 0.1127 | 0.02596 | 0.02403 | 0.03994 | PASS | PASS | FAIL | PASS | FAIL | 1.00 |
| z5 | partial absorption | symbolically-stable | 0.02353 | 0.09465 | 0.00507 | 0.007235 | PASS | PASS | FAIL | FAIL | PASS | 1.00 |

## z0

| method | seed | symbolic core | T0 val MSE | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---:|---|---|
| mi20-mi | 0 | 16 | 6.369e+12 | 6.414e+12 | 7.035e+12 | -7.035e+12 | valid | `omega_b*(H0 + 27.826664)*(n_s - 0.095620185)*log(A_s)**4/omega_cdm` |
| mi20-mi | 1 | 20 | 16.06 | 15.8 | 17.33 | -16.33 | valid | `log(tau - log(49.0100838112454*A_s**2*(-1 + 0.614772339966153*omega_c...` |
| mi20-mi | 2 | 20 | 10.35 | 10.14 | 11.13 | -10.13 | valid | `log(n_s*(1.4913623*H0*omega_b/omega_cdm + 2.56879)/log(H0) - omega_cd...` |
| mi20-mi | 3 | 16 | 9.405e+12 | 9.466e+12 | 1.038e+13 | -1.038e+13 | valid | `-n_s*(omega_b*(H0 + 27.79619) + 1.825506*omega_cdm)*log(A_s)**4/omega...` |
| mi20-mi | 4 | 19 | 6.936e+04 | 6.954e+04 | 7.628e+04 | -7.628e+04 | valid | `-H0 - 0.460366792638367*log((tau + exp((6.5674596*n_s*omega_b - omega...` |
| mi20-mse | 0 | 11 | 0.922 | 0.9124 | 1.001 | -0.0007895 | valid | `A_s*(n_s + log(omega_b/omega_cdm))**2/H0**2` |
| mi20-mse | 1 | 8 | 0.91 | 0.9055 | 0.9932 | 0.006801 | valid | `-omega_cdm/(H0*n_s*omega_b)` |
| mi20-mse | 2 | 3 | 0.9223 | 0.9126 | 1.001 | -0.0009847 | valid | `omega_cdm/H0` |
| mi20-mse | 3 | 8 | 0.91 | 0.9055 | 0.9932 | 0.006801 | valid | `-omega_cdm/(H0*n_s*omega_b)` |
| mi20-mse | 4 | 3 | 0.9223 | 0.9126 | 1.001 | -0.0009847 | valid | `omega_cdm/H0` |
| mse20 | 0 | 20 | 0.03697 | 0.03811 | 0.0418 | 0.9582 | valid | `(A_s*omega_b*(0.099378526*H0 - 1.3216175)*(n_s - omega_cdm) - 1.26697...` |
| mse20 | 1 | 20 | 0.03841 | 0.03997 | 0.04384 | 0.9562 | valid | `(n_s*(A_s - omega_b*(H0 + 2.9416294)*(log(A_s) + 15.420904) + 1.46221...` |
| mse20 | 2 | 20 | 0.03867 | 0.03973 | 0.04358 | 0.9564 | valid | `(-n_s*(H0*omega_b + 0.3431502)*(log(A_s) + 15.35462) + 74.147224*omeg...` |
| mse20 | 3 | 20 | 0.03759 | 0.03927 | 0.04308 | 0.9569 | valid | `0.09524143*H0 - omega_b - 1.5979607*omega_cdm/(n_s*omega_b) + 4.09357...` |
| mse20 | 4 | 19 | 0.05861 | 0.06154 | 0.0675 | 0.9325 | valid | `-0.10115089779604*H0*omega_cdm + 0.10937819918444*H0 + 1.096418*n_s -...` |
| mse30 | 0 | 26 | 0.04177 | 0.04203 | 0.04611 | 0.9539 | valid | `(-1.222317*H0*n_s*omega_b*omega_cdm - (A_s**2 + 1.9525921)*(H0*n_s*om...` |
| mse30 | 1 | 29 | 0.0369 | 0.03859 | 0.04233 | 0.9577 | valid | `-3.96858357163858*omega_b - omega_cdm - 1.96858357163858*log(A_s) + 4...` |
| mse30 | 2 | 30 | 0.03704 | 0.03832 | 0.04203 | 0.958 | valid | `4.625449*n_s*omega_b*(H0 + 12.553398) - 75.85313*omega_cdm - 2.009128...` |
| mse30 | 3 | 20 | 0.04303 | 0.04625 | 0.05073 | 0.9493 | valid | `(n_s*(1.09120196157956*H0*(4.6935387*omega_b - omega_cdm + 0.10054615...` |
| mse30 | 4 | 28 | 0.03891 | 0.04067 | 0.04461 | 0.9554 | valid | `-21.1050886707563*A_s*H0*(0.217673925547899*H0 + 1)**2/(n_s*omega_b**...` |
| mse40 | 0 | 33 | 0.03752 | 0.03894 | 0.04271 | 0.9573 | valid | `(H0*n_s*(omega_cdm + 0.16227016)*(0.611909908504171*n_s - omega_cdm -...` |
| mse40 | 1 | 39 | 0.05898 | 0.06208 | 0.0681 | 0.9319 | valid | `(H0*(2.58571971129302*n_s*omega_b - 0.49200463*omega_cdm + 0.04769657...` |
| mse40 | 2 | 36 | 0.05912 | 0.06131 | 0.06725 | 0.9328 | valid | `9.122279*n_s*log(n_s + 1.6585479*omega_b*(n_s + 0.8684513) - 2.556969...` |
| mse40 | 3 | 25 | 0.03512 | 0.03639 | 0.03992 | 0.9601 | valid | `-13554076.368663*A_s*H0 + 0.126157322535035*H0 - omega_cdm + 10.00578...` |
| mse40 | 4 | 36 | 0.05568 | 0.05862 | 0.0643 | 0.9357 | valid | `-(exp(2*omega_cdm) - 0.82838506)*(A_s*n_s + 1.8987488*n_s*omega_b**4*...` |
| h(f1) | fixed | 7 | n/a | 0.06927 | 0.07598 | 0.924 | fixed baseline | `h(omega_cdm/(H0*n_s*omega_b))` |
| h(f1)+g(f2), additive | fixed | 2e+01 | n/a | 0.04161 | 0.04565 | 0.9544 | fixed baseline | `h(omega_cdm/(H0*n_s*omega_b)) + g(A_s*H0*omega_cdm/n_s)` |
| h(f1)+g(f2), interaction-aware | fixed | 2e+01 | n/a | 0.04287 | 0.04702 | 0.953 | fixed baseline | `h(omega_cdm/(H0*n_s*omega_b)) + g(-A_s*H0**2*(f1hat - 10.8708105))` |

Canonical known `f2` audit source: additive residual hierarchy; expression `A_s*H0*omega_cdm/n_s`. The interaction-aware hierarchy remains the reconstruction denominator only.

### T0 one-standard-error readout

| method | metric | c_min | one-SE complexity | threshold | per-seed retained complexity |
|---|---|---:|---:|---:|---|
| mse20 | nmse_val | 20 | 20 | 0.05011 | s0:c20, s1:c20, s2:c20, s3:c20, s4:c19 |
| mse30 | nmse_val | 30 | 25 | 0.04422 | s0:c23, s1:c25, s2:c25, s3:c20, s4:c24 |
| mse40 | nmse_val | 39 | 17 | 0.05925 | s0:c17, s1:c17, s2:c15, s3:c17, s4:c17 |

One-SE equations are secondary confirmations and do not carry success decisions.

| method | seed | complexity | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---|---|
| mse20 | 0 | 20 | 0.03811 | 0.0418 | 0.9582 | valid | `(A_s*omega_b*(0.099378526*H0 - 1.3216175)*(n_s - omega_cdm) - 1.26697...` |
| mse20 | 1 | 20 | 0.03997 | 0.04384 | 0.9562 | valid | `(n_s*(A_s - omega_b*(H0 + 2.9416294)*(log(A_s) + 15.420904) + 1.46221...` |
| mse20 | 2 | 20 | 0.03973 | 0.04358 | 0.9564 | valid | `(-n_s*(H0*omega_b + 0.3431502)*(log(A_s) + 15.35462) + 74.147224*omeg...` |
| mse20 | 3 | 20 | 0.03927 | 0.04308 | 0.9569 | valid | `0.09524143*H0 - omega_b - 1.5979607*omega_cdm/(n_s*omega_b) + 4.09357...` |
| mse20 | 4 | 19 | 0.06154 | 0.0675 | 0.9325 | valid | `-0.10115089779604*H0*omega_cdm + 0.10937819918444*H0 + 1.096418*n_s -...` |
| mse30 | 0 | 23 | 0.04199 | 0.04606 | 0.9539 | valid | `-(1.0760937*exp(omega_cdm) + 1)*(H0*n_s*omega_b*(log(A_s) + 16.479298...` |
| mse30 | 1 | 25 | 0.03873 | 0.04248 | 0.9575 | valid | `-1.92856350079789*omega_b - omega_cdm - 1.92856350079789*log(A_s) + 4...` |
| mse30 | 2 | 25 | 0.03894 | 0.04271 | 0.9573 | valid | `4.625449*n_s*omega_b*(H0 + 12.553398) - 75.85313*omega_cdm - 2.009128...` |
| mse30 | 3 | 20 | 0.04625 | 0.05073 | 0.9493 | valid | `(n_s*(1.09120196157956*H0*(4.6935387*omega_b - omega_cdm + 0.10054615...` |
| mse30 | 4 | 24 | 0.04437 | 0.04867 | 0.9513 | valid | `-A_s*H0**3/(n_s*omega_b**2) + 0.16079454*H0/n_s + 1/omega_cdm - 13.68...` |
| mse40 | 0 | 17 | 0.04132 | 0.04533 | 0.9547 | valid | `4.5105166*H0*omega_b/n_s + 1/omega_cdm - 17.49021/n_s + 4.224316e-9/(...` |
| mse40 | 1 | 17 | 0.06591 | 0.07229 | 0.9277 | valid | `1.69945233109288*H0*(3.1563853201569*n_s*omega_b - 0.6340853*omega_cd...` |
| mse40 | 2 | 15 | 0.06476 | 0.07103 | 0.929 | valid | `4.74109249468464*H0*n_s*omega_b + 2*n_s - 78.80207*omega_cdm` |
| mse40 | 3 | 17 | 0.0404 | 0.04432 | 0.9557 | valid | `(n_s*(5.38043*H0*(-1988523.5*A_s + omega_b) + 2.0424628) - 74.15264*o...` |
| mse40 | 4 | 17 | 0.06453 | 0.07078 | 0.9292 | valid | `0.011132531*H0/omega_cdm - 0.45012355 + 0.209451757656028/omega_cdm -...` |

### T0 common-complexity front comparison

| cut | method | metric | mean validation error | SE |
|---:|---|---|---:|---:|
| 1 | mse20 | nmse_val | 0.9998 | 5.551e-17 |
| 1 | mse30 | nmse_val | 0.9998 | 5.071e-05 |
| 1 | mse40 | nmse_val | 0.9999 | 6.219e-05 |
| 2 | mse20 | nmse_val | 0.9876 | 0 |
| 2 | mse30 | nmse_val | 0.9876 | 0 |
| 2 | mse40 | nmse_val | 0.9876 | 0 |
| 3 | mse20 | nmse_val | 0.9789 | 0 |
| 3 | mse30 | nmse_val | 0.9789 | 0 |
| 3 | mse40 | nmse_val | 0.9789 | 0 |
| 4 | mse20 | nmse_val | 0.9116 | 0.005505 |
| 4 | mse30 | nmse_val | 0.9252 | 0.0132 |
| 4 | mse40 | nmse_val | 0.9322 | 0.01243 |
| 5 | mse20 | nmse_val | 0.5252 | 0.02345 |
| 5 | mse30 | nmse_val | 0.5439 | 0.01201 |
| 5 | mse40 | nmse_val | 0.5439 | 0.01201 |
| 6 | mse20 | nmse_val | 0.5061 | 0.02345 |
| 6 | mse30 | nmse_val | 0.5368 | 0.01118 |
| 6 | mse40 | nmse_val | 0.5439 | 0.01201 |
| 7 | mse20 | nmse_val | 0.2915 | 0.0146 |
| 7 | mse30 | nmse_val | 0.3205 | 0.01341 |
| 7 | mse40 | nmse_val | 0.2957 | 0.00986 |
| 8 | mse20 | nmse_val | 0.2915 | 0.0146 |
| 8 | mse30 | nmse_val | 0.3205 | 0.01341 |
| 8 | mse40 | nmse_val | 0.2957 | 0.00986 |
| 9 | mse20 | nmse_val | 0.1324 | 0.0016 |
| 9 | mse30 | nmse_val | 0.1744 | 0.02325 |
| 9 | mse40 | nmse_val | 0.135 | 0.0009055 |
| 10 | mse20 | nmse_val | 0.1324 | 0.0016 |
| 10 | mse30 | nmse_val | 0.1501 | 0.01704 |
| 10 | mse40 | nmse_val | 0.135 | 0.0009055 |
| 11 | mse20 | nmse_val | 0.07611 | 0.002204 |
| 11 | mse30 | nmse_val | 0.08765 | 0.01001 |
| 11 | mse40 | nmse_val | 0.07699 | 0.002046 |
| 13 | mse20 | nmse_val | 0.06651 | 0.0008077 |
| 13 | mse30 | nmse_val | 0.06915 | 0.0009834 |
| 13 | mse40 | nmse_val | 0.07009 | 0.001912 |
| 14 | mse20 | nmse_val | 0.06648 | 0.0008143 |
| 14 | mse30 | nmse_val | 0.06835 | 0.001129 |
| 14 | mse40 | nmse_val | 0.06964 | 0.001969 |
| 15 | mse20 | nmse_val | 0.06522 | 0.0009959 |
| 15 | mse30 | nmse_val | 0.0654 | 0.000712 |
| 15 | mse40 | nmse_val | 0.06118 | 0.004474 |
| 16 | mse20 | nmse_val | 0.06005 | 0.004281 |
| 16 | mse30 | nmse_val | 0.06533 | 0.0007005 |
| 16 | mse40 | nmse_val | 0.06115 | 0.004464 |
| 17 | mse20 | nmse_val | 0.05205 | 0.004911 |
| 17 | mse30 | nmse_val | 0.063 | 0.002556 |
| 17 | mse40 | nmse_val | 0.0572 | 0.006114 |
| 18 | mse20 | nmse_val | 0.05056 | 0.00545 |
| 18 | mse30 | nmse_val | 0.0598 | 0.003352 |
| 18 | mse40 | nmse_val | 0.05647 | 0.005858 |
| 19 | mse20 | nmse_val | 0.05044 | 0.005381 |
| 19 | mse30 | nmse_val | 0.05457 | 0.004286 |
| 19 | mse40 | nmse_val | 0.05573 | 0.006001 |
| 20 | mse20 | nmse_val | 0.04561 | 0.004502 |
| 20 | mse30 | nmse_val | 0.05016 | 0.003702 |
| 20 | mse40 | nmse_val | 0.05532 | 0.005868 |

## z1

| method | seed | symbolic core | T0 val MSE | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---:|---|---|
| mi20-mi | 0 | 20 | 7.735 | 7.79 | 7.652 | -6.652 | valid | `log(-log(n_s) + log(A_s*omega_cdm**4*(0.00141385081781373*H0**2 + 1)*...` |
| mi20-mi | 1 | 20 | 54.78 | 54.58 | 53.61 | -52.61 | valid | `tau + 46.233837/log((H0 + omega_b*log(omega_cdm)*log(A_s*omega_cdm/n_...` |
| mi20-mi | 2 | 19 | 75.45 | 75.32 | 73.98 | -72.98 | valid | `log(n_s) - log(A_s*H0**7*omega_cdm**4*exp(-2*tau)/omega_b**2)` |
| mi20-mi | 3 | 20 | 155.2 | 155 | 152.3 | -151.3 | valid | `n_s + 2*tau - log(A_s*omega_cdm**4*(0.00140701198492809*H0**2 + 1)**4...` |
| mi20-mi | 4 | 18 | 77.26 | 77.64 | 76.26 | -75.26 | valid | `log(A_s*H0**7*omega_cdm**4*exp(-2*tau)/(n_s*omega_b**2))` |
| mi20-mse | 0 | 8 | 1.054 | 1.018 | 1 | -4.188e-05 | valid | `(-omega_b - 0.015186661)/(H0**2*omega_cdm)` |
| mi20-mse | 1 | 14 | 1.045 | 1.009 | 0.9908 | 0.009202 | valid | `-H0/((tau - log(omega_cdm - 0.03731274))*log(A_s)**2) + omega_b` |
| mi20-mse | 2 | 8 | 1.053 | 1.017 | 0.9994 | 0.0006351 | valid | `0.00107176032169693*omega_b/(omega_cdm**2*(0.0327377507122425*H0 - 1)...` |
| mi20-mse | 3 | 8 | 1.053 | 1.018 | 1 | 2.122e-06 | valid | `(omega_b + 0.015110244)/(H0**2*omega_cdm)` |
| mi20-mse | 4 | 8 | 1.053 | 1.017 | 0.9994 | 0.0006355 | valid | `0.00107123918884438*omega_b/(omega_cdm**2*(0.032729790540796*H0 - 1)**2)` |
| mse20 | 0 | 20 | 0.02009 | 0.01985 | 0.0195 | 0.9805 | valid | `-56.311096*omega_cdm + 3.2444456*tau + log(n_s) - 1.5460356 - 0.07880...` |
| mse20 | 1 | 19 | 0.02161 | 0.02177 | 0.02138 | 0.9786 | valid | `-0.0011388696*H0**2 + 17.58436*omega_b/omega_cdm - 0.67970943 + 0.328...` |
| mse20 | 2 | 20 | 0.01868 | 0.0185 | 0.01817 | 0.9818 | valid | `-n_s + 56.210857*omega_b*exp(n_s + tau) - 56.210857*omega_cdm - 44.99...` |
| mse20 | 3 | 19 | 0.01883 | 0.01885 | 0.01852 | 0.9815 | valid | `2.27545031446154*H0*(omega_b - 0.347414530640537*omega_cdm - 0.053673...` |
| mse20 | 4 | 20 | 0.01208 | 0.01208 | 0.01187 | 0.9881 | valid | `-25.285965*omega_cdm + 3.269083*tau - 5.2875495 - 0.6792998*omega_cdm...` |
| mse30 | 0 | 28 | 0.01441 | 0.0135 | 0.01326 | 0.9867 | valid | `-omega_cdm + 3*tau - log(A_s) - 25.080301 - omega_cdm/omega_b - 10.05...` |
| mse30 | 1 | 22 | 0.02092 | 0.02075 | 0.02038 | 0.9796 | valid | `1.23415179400624*tau + 0.961981090079382*(n_s + tau)**2 + 2.43605 - 1...` |
| mse30 | 2 | 29 | 0.002461 | 0.002431 | 0.002388 | 0.9976 | valid | `2.2830062*H0*omega_b - 0.77759147*H0*omega_cdm + 0.32361785*H0 + 8.94...` |
| mse30 | 3 | 27 | 0.01917 | 0.01897 | 0.01864 | 0.9814 | valid | `0.253369465508245*H0*omega_b/omega_cdm - 0.253369465508245*H0 + 0.004...` |
| mse30 | 4 | 30 | 0.02035 | 0.01974 | 0.01939 | 0.9806 | valid | `3.2787654*tau - 0.92839026 - 2.9276538/omega_cdm + 14.376769/(omega_c...` |
| mse40 | 0 | 40 | 0.01815 | 0.01817 | 0.01785 | 0.9822 | valid | `(H0*n_s*omega_b*((n_s + tau)**2 + 2.0184882) + H0*omega_b*tau + 14.34...` |
| mse40 | 1 | 37 | 0.01736 | 0.01709 | 0.01679 | 0.9832 | valid | `(H0*omega_b*omega_cdm*(1.85441786688757*n_s + tau + 3.1201410476778) ...` |
| mse40 | 2 | 40 | 0.003252 | 0.003138 | 0.003082 | 0.9969 | valid | `((H0 + 0.8049228*log(A_s/n_s))*(-H0 + 2*tau + log(omega_b)) + ((H0 + ...` |
| mse40 | 3 | 39 | 0.01661 | 0.01667 | 0.01638 | 0.9836 | valid | `-10.3202674027993*A_s*H0**2/omega_b**2 - 55.736713*omega_cdm + tau + ...` |
| mse40 | 4 | 35 | 0.002053 | 0.00205 | 0.002013 | 0.998 | valid | `0.7039488*H0/log(omega_cdm**2) - tau*log(omega_cdm) + tau + 155.3249*...` |
| h(f1) | fixed | 4 | n/a | 0.06961 | 0.06838 | 0.9316 | fixed baseline | `h(H0**2*omega_cdm)` |
| h(f1)+g(f2), additive | fixed | 1e+01 | n/a | 0.005481 | 0.005383 | 0.9946 | fixed baseline | `h(H0**2*omega_cdm) + g(A_s*exp(-2*tau)/omega_b**2)` |
| h(f1)+g(f2), interaction-aware | fixed | 1e+01 | n/a | 0.005481 | 0.005383 | 0.9946 | fixed baseline | `h(H0**2*omega_cdm) + g(A_s*exp(-2*tau)/omega_b**2)` |

Canonical known `f2` audit source: additive residual hierarchy; expression `A_s*exp(-2*tau)/omega_b**2`. The interaction-aware hierarchy remains the reconstruction denominator only.

### T0 one-standard-error readout

| method | metric | c_min | one-SE complexity | threshold | per-seed retained complexity |
|---|---|---:|---:|---:|---|
| mse20 | nmse_val | 20 | 19 | 0.01889 | s0:c19, s1:c19, s2:c19, s3:c19, s4:c18 |
| mse30 | nmse_val | 30 | 22 | 0.01796 | s0:c22, s1:c22, s2:c22, s3:c22, s4:c22 |
| mse40 | nmse_val | 40 | 25 | 0.01434 | s0:c24, s1:c25, s2:c25, s3:c25, s4:c25 |

One-SE equations are secondary confirmations and do not carry success decisions.

| method | seed | complexity | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---|---|
| mse20 | 0 | 19 | 0.0199 | 0.01955 | 0.9805 | valid | `n_s - 56.19319*omega_cdm + 3.24453820405767*tau - 2.5618815 - 0.07877...` |
| mse20 | 1 | 19 | 0.02177 | 0.02138 | 0.9786 | valid | `-0.0011388696*H0**2 + 17.58436*omega_b/omega_cdm - 0.67970943 + 0.328...` |
| mse20 | 2 | 19 | 0.01959 | 0.01924 | 0.9808 | valid | `(H0*(-n_s + 55.97205*omega_b*exp(n_s + tau) - 55.97205*omega_cdm - 7....` |
| mse20 | 3 | 19 | 0.01885 | 0.01852 | 0.9815 | valid | `2.27545031446154*H0*(omega_b - 0.347414530640537*omega_cdm - 0.053673...` |
| mse20 | 4 | 18 | 0.01817 | 0.01784 | 0.9822 | valid | `-24.894564*omega_cdm + tau - 5.122665 - 0.6862679*omega_cdm/omega_b -...` |
| mse30 | 0 | 22 | 0.01798 | 0.01767 | 0.9823 | valid | `(-14.497076*H0*omega_b*omega_cdm - H0*omega_b*(n_s + tau)*(log(A_s) +...` |
| mse30 | 1 | 22 | 0.02075 | 0.02038 | 0.9796 | valid | `1.23415179400624*tau + 0.961981090079382*(n_s + tau)**2 + 2.43605 - 1...` |
| mse30 | 2 | 22 | 0.004985 | 0.004896 | 0.9951 | valid | `2.3053908*H0*omega_b - 0.79125077*H0*omega_cdm + 0.3096105*H0 + 8.638...` |
| mse30 | 3 | 22 | 0.019 | 0.01867 | 0.9813 | valid | `0.253715305446841*H0*omega_b/omega_cdm - 0.253715305446841*H0 + 0.004...` |
| mse30 | 4 | 22 | 0.02237 | 0.02198 | 0.978 | valid | `3.256828*tau - 3.0914862 - 2.9284127/omega_cdm + 14.399827/(omega_cdm...` |
| mse40 | 0 | 24 | 0.02071 | 0.02035 | 0.9797 | valid | `(omega_b + 1.0447563)*(H0*omega_b*(tau + (n_s + tau)**2 + 2.1689014) ...` |
| mse40 | 1 | 25 | 0.01788 | 0.01757 | 0.9824 | valid | `0.09228686*H0*tau - 0.06091901*H0 - 0.0021677404*H0/omega_b - 3.22796...` |
| mse40 | 2 | 25 | 0.01093 | 0.01074 | 0.9893 | valid | `(H0*((n_s + tau)**2 - 13.956129) - (H0 - 11.485902)*(H0*(-2*omega_b +...` |
| mse40 | 3 | 25 | 0.01923 | 0.01889 | 0.9811 | valid | `n_s**2 - 56.17069*omega_cdm - 81.7823444172245*tau**4 + 3.5080562*tau...` |
| mse40 | 4 | 25 | 0.004919 | 0.004832 | 0.9952 | valid | `0.7074167*H0/log(omega_cdm**2) + (n_s + tau)**2 + 148.22435*exp(omega...` |

### T0 common-complexity front comparison

| cut | method | metric | mean validation error | SE |
|---:|---|---|---:|---:|
| 1 | mse20 | nmse_val | 0.9984 | 0.0005184 |
| 1 | mse30 | nmse_val | 0.9979 | 0 |
| 1 | mse40 | nmse_val | 0.9984 | 0.0005187 |
| 2 | mse20 | nmse_val | 0.9982 | 0.0003157 |
| 2 | mse30 | nmse_val | 0.9979 | 0 |
| 2 | mse40 | nmse_val | 0.9982 | 0.0003157 |
| 3 | mse20 | nmse_val | 0.9914 | 5.551e-17 |
| 3 | mse30 | nmse_val | 0.9914 | 5.551e-17 |
| 3 | mse40 | nmse_val | 0.9914 | 5.551e-17 |
| 4 | mse20 | nmse_val | 0.8688 | 0.01581 |
| 4 | mse30 | nmse_val | 0.8891 | 0.003596 |
| 4 | mse40 | nmse_val | 0.9222 | 0.02302 |
| 5 | mse20 | nmse_val | 0.1946 | 0.0402 |
| 5 | mse30 | nmse_val | 0.2602 | 0.03282 |
| 5 | mse40 | nmse_val | 0.2274 | 0.0402 |
| 6 | mse20 | nmse_val | 0.194 | 0.03987 |
| 6 | mse30 | nmse_val | 0.2599 | 0.03276 |
| 6 | mse40 | nmse_val | 0.2274 | 0.0402 |
| 7 | mse20 | nmse_val | 0.09442 | 0.01119 |
| 7 | mse30 | nmse_val | 0.1116 | 0.008903 |
| 7 | mse40 | nmse_val | 0.1493 | 0.0398 |
| 8 | mse20 | nmse_val | 0.09289 | 0.0119 |
| 8 | mse30 | nmse_val | 0.1116 | 0.008903 |
| 8 | mse40 | nmse_val | 0.09271 | 0.01197 |
| 9 | mse20 | nmse_val | 0.05802 | 0.002052 |
| 9 | mse30 | nmse_val | 0.05901 | 0.002468 |
| 9 | mse40 | nmse_val | 0.06232 | 0.002143 |
| 10 | mse20 | nmse_val | 0.05776 | 0.002164 |
| 10 | mse30 | nmse_val | 0.05855 | 0.002252 |
| 10 | mse40 | nmse_val | 0.05615 | 0.002739 |
| 11 | mse20 | nmse_val | 0.04215 | 0.003245 |
| 11 | mse30 | nmse_val | 0.0457 | 0.003438 |
| 11 | mse40 | nmse_val | 0.05065 | 0.004129 |
| 12 | mse20 | nmse_val | 0.03815 | 0.001455 |
| 12 | mse30 | nmse_val | 0.04445 | 0.002223 |
| 12 | mse40 | nmse_val | 0.04583 | 0.003287 |
| 13 | mse20 | nmse_val | 0.03301 | 0.001532 |
| 13 | mse30 | nmse_val | 0.03513 | 0.001884 |
| 13 | mse40 | nmse_val | 0.03695 | 0.001651 |
| 14 | mse20 | nmse_val | 0.0308 | 0.000461 |
| 14 | mse30 | nmse_val | 0.03392 | 0.001087 |
| 14 | mse40 | nmse_val | 0.03474 | 0.0007647 |
| 15 | mse20 | nmse_val | 0.02478 | 0.001918 |
| 15 | mse30 | nmse_val | 0.02818 | 0.001391 |
| 15 | mse40 | nmse_val | 0.0283 | 0.001479 |
| 16 | mse20 | nmse_val | 0.0229 | 0.001211 |
| 16 | mse30 | nmse_val | 0.02677 | 0.001147 |
| 16 | mse40 | nmse_val | 0.02572 | 0.001505 |
| 17 | mse20 | nmse_val | 0.02124 | 0.001045 |
| 17 | mse30 | nmse_val | 0.02309 | 0.001374 |
| 17 | mse40 | nmse_val | 0.02258 | 0.0007325 |
| 18 | mse20 | nmse_val | 0.01977 | 0.0008674 |
| 18 | mse30 | nmse_val | 0.02019 | 0.001091 |
| 18 | mse40 | nmse_val | 0.02183 | 0.0008799 |
| 19 | mse20 | nmse_val | 0.01874 | 0.0005429 |
| 19 | mse30 | nmse_val | 0.01968 | 0.001077 |
| 19 | mse40 | nmse_val | 0.02065 | 0.0008653 |
| 20 | mse20 | nmse_val | 0.01734 | 0.001549 |
| 20 | mse30 | nmse_val | 0.01842 | 0.002143 |
| 20 | mse40 | nmse_val | 0.01879 | 0.0007903 |

## z2

| method | seed | symbolic core | T0 val MSE | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---:|---|---|
| mi20-mi | 0 | 19 | 113.6 | 113.1 | 115.5 | -114.5 | valid | `log(H0 + (omega_cdm + (log(A_s) - 6.6247473)*(-n_s + exp(omega_cdm) -...` |
| mi20-mi | 1 | 20 | 111.2 | 111.4 | 113.8 | -112.8 | valid | `-9.63122112224589*n_s + 260.550680122098*omega_b + 10.6312211222459*o...` |
| mi20-mi | 2 | 19 | 2.097 | 2.028 | 2.071 | -1.071 | valid | `((n_s - 27.104689*omega_b)*log(A_s) + 17.5407371455653)*exp(1.3992021...` |
| mi20-mi | 3 | 20 | 50.75 | 51.02 | 52.11 | -51.11 | valid | `log((-omega_b*exp(-1.18363128588324*(0.919161408603829*n_s - omega_cd...` |
| mi20-mi | 4 | 17 | 138 | 138.6 | 141.6 | -140.6 | valid | `H0*((n_s - 1.0812154*omega_cdm)*log(A_s) + 61.77855)/(H0*log(omega_b)...` |
| mi20-mse | 0 | 4 | 1.006 | 0.9759 | 0.9967 | 0.003263 | valid | `omega_b/n_s**2` |
| mi20-mse | 1 | 9 | 0.9864 | 0.9706 | 0.9913 | 0.008683 | valid | `-n_s + 26.552305*omega_b + 1.0805545*omega_cdm` |
| mi20-mse | 2 | 9 | 0.9829 | 0.9661 | 0.9868 | 0.01323 | valid | `-0.92421293*n_s + 24.5724632173026*omega_b + omega_cdm` |
| mi20-mse | 3 | 4 | 1.006 | 0.9759 | 0.9967 | 0.003263 | valid | `omega_b/n_s**2` |
| mi20-mse | 4 | 9 | 0.9863 | 0.9705 | 0.9912 | 0.008786 | valid | `-n_s + 26.55216*omega_b + 1.0821509*omega_cdm` |
| mse20 | 0 | 20 | 0.008903 | 0.0087 | 0.008886 | 0.9911 | valid | `-23.790573*n_s + 647.945*omega_b + 26.126965*omega_cdm + (2*omega_b -...` |
| mse20 | 1 | 20 | 0.001957 | 0.001905 | 0.001946 | 0.9981 | valid | `-(tau - 647.69275)*(-0.036707442*n_s + omega_b + 0.040413447*omega_cd...` |
| mse20 | 2 | 20 | 0.001957 | 0.001905 | 0.001946 | 0.9981 | valid | `-23.775621625317*n_s + 647.6949792275*omega_b + 26.174798470387*omega...` |
| mse20 | 3 | 20 | 0.009385 | 0.009089 | 0.009283 | 0.9907 | valid | `-23.748552*n_s + 26.039036*omega_b + 26.039036*omega_cdm + 32.7619610...` |
| mse20 | 4 | 18 | 0.009598 | 0.009331 | 0.00953 | 0.9905 | valid | `(-23.790144*n_s*omega_b + omega_b*(25.82332*omega_cdm + 32.59354)*exp...` |
| mse30 | 0 | 27 | 0.001613 | 0.001562 | 0.001595 | 0.9984 | valid | `(omega_cdm + 0.890892)*(H0*(643.9052*A_s - 23.636637*n_s + 643.9052*o...` |
| mse30 | 1 | 29 | 0.002286 | 0.002283 | 0.002332 | 0.9977 | valid | `-0.0026502458*H0 - 23.721403*n_s + 26.128754*omega_cdm + log(A_s) + l...` |
| mse30 | 2 | 25 | 0.008737 | 0.008495 | 0.008676 | 0.9913 | valid | `-0.0030335942*H0 - 23.795397*n_s + 647.7352*omega_b + 26.113057242350...` |
| mse30 | 3 | 29 | 0.001743 | 0.001684 | 0.00172 | 0.9983 | valid | `-0.0030336527*H0 + n_s*omega_cdm + omega_b*(16.1386339722666*tau**2 +...` |
| mse30 | 4 | 28 | 0.009771 | 0.009526 | 0.009729 | 0.9903 | valid | `-(0.323893971851626*n_s - omega_b*(-9.079216*n_s + 26.125875*omega_cd...` |
| mse40 | 0 | 35 | 0.001567 | 0.001508 | 0.001541 | 0.9985 | valid | `-23.773088*n_s + 611.63058333384*omega_b - 100.94259*omega_cdm/log(om...` |
| mse40 | 1 | 40 | 0.00286 | 0.002821 | 0.002882 | 0.9971 | valid | `(-0.25864327*n_s**2*omega_cdm + omega_b*omega_cdm*(log(A_s) + 33.7971...` |
| mse40 | 2 | 33 | 0.001539 | 0.001509 | 0.001542 | 0.9985 | valid | `(omega_cdm + 0.8767359)*(H0**4*(0.0336795864254562*H0 - 1)**4*(-23.99...` |
| mse40 | 3 | 37 | 0.001684 | 0.001635 | 0.00167 | 0.9983 | valid | `(-1.05862905777178*H0 + 14.066162*tau + (0.07526069*H0 - tau)*(-23.83...` |
| mse40 | 4 | 37 | 0.002515 | 0.002481 | 0.002534 | 0.9975 | valid | `489663499.0*A_s - 0.0026444618*H0 - 23.752577*n_s + 2*omega_b + 25.75...` |
| h(f1) | fixed | 4 | n/a | 0.06975 | 0.07124 | 0.9288 | fixed baseline | `h(omega_b/n_s**2)` |
| h(f1)+g(f2), additive | fixed | 2e+01 | n/a | 0.002392 | 0.002443 | 0.9976 | fixed baseline | `h(omega_b/n_s**2) + g(n_s*(A_s + 1.03524857872784e-5*omega_b*omega_cdm**2))` |
| h(f1)+g(f2), interaction-aware | fixed | 2e+01 | n/a | 0.002812 | 0.002872 | 0.9971 | fixed baseline | `h(omega_b/n_s**2) + g(log(A_s*omega_b*(n_s*omega_cdm - 0.024653804)**2))` |

Canonical known `f2` audit source: additive residual hierarchy; expression `n_s*(A_s + 1.03524857872784e-5*omega_b*omega_cdm**2)`. The interaction-aware hierarchy remains the reconstruction denominator only.

### T0 one-standard-error readout

| method | metric | c_min | one-SE complexity | threshold | per-seed retained complexity |
|---|---|---:|---:|---:|---|
| mse20 | nmse_val | 20 | 16 | 0.008098 | s0:c16, s1:c16, s2:c16, s3:c16, s4:c13 |
| mse30 | nmse_val | 29 | 16 | 0.006595 | s0:c16, s1:c16, s2:c15, s3:c16, s4:c15 |
| mse40 | nmse_val | 40 | 25 | 0.002289 | s0:c24, s1:c25, s2:c25, s3:c24, s4:c23 |

One-SE equations are secondary confirmations and do not carry success decisions.

| method | seed | complexity | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---|---|
| mse20 | 0 | 16 | 0.008726 | 0.008912 | 0.9911 | valid | `-23.790888*n_s + 647.9447*omega_b + omega_cdm*(tau**2 + 26.126217) + ...` |
| mse20 | 1 | 16 | 0.001912 | 0.001953 | 0.998 | valid | `-23.775465*n_s + 647.86176*omega_b + 26.1744683379379*omega_cdm + log...` |
| mse20 | 2 | 16 | 0.008711 | 0.008897 | 0.9911 | valid | `-23.792448733339*n_s + 647.3078*omega_b + 26.131544*omega_cdm + tau**...` |
| mse20 | 3 | 16 | 0.009426 | 0.009627 | 0.9904 | valid | `-23.748077*n_s + 25.966745*omega_cdm + tau**2 + 34.11453 - 0.31113505...` |
| mse20 | 4 | 13 | 0.009446 | 0.009648 | 0.9904 | valid | `-23.71784*n_s + 26.100897*omega_cdm + 34.071873 - 0.31104508/omega_b` |
| mse30 | 0 | 16 | 0.001938 | 0.00198 | 0.998 | valid | `-23.787523*n_s + 643.94714*omega_b + 26.184011*omega_cdm + log(A_s) +...` |
| mse30 | 1 | 16 | 0.002682 | 0.00274 | 0.9973 | valid | `-23.727468*n_s + 26.103739*omega_cdm + log(A_s) + 54.07849 - 0.311312...` |
| mse30 | 2 | 15 | 0.008732 | 0.008918 | 0.9911 | valid | `-n_s*(n_s + 21.861654) + 647.73364*omega_b + 26.1233198738385*omega_c...` |
| mse30 | 3 | 16 | 0.002089 | 0.002133 | 0.9979 | valid | `646.8083*omega_b + omega_cdm + 1.1966802*(n_s - omega_cdm)*log(A_s) +...` |
| mse30 | 4 | 15 | 0.01033 | 0.01055 | 0.9895 | valid | `(0.5870092*n_s*(omega_cdm - 0.6631435) + omega_b*(22.9106837895288 - ...` |
| mse40 | 0 | 24 | 0.001612 | 0.001646 | 0.9984 | valid | `-23.772982*n_s + 614.94135*omega_b - 100.93783*omega_cdm/log(omega_b)...` |
| mse40 | 1 | 25 | 0.003183 | 0.003251 | 0.9967 | valid | `-0.00029947178*H0/omega_cdm - 0.25813583*n_s/omega_b + log(A_s)/n_s +...` |
| mse40 | 2 | 25 | 0.001784 | 0.001822 | 0.9982 | valid | `1.13934851545217e+17*A_s**2 - 2.0590232e-5*H0**2 - 23.93021*n_s + 647...` |
| mse40 | 3 | 24 | 0.001904 | 0.001945 | 0.9981 | valid | `-23.763739*n_s + 647.68996915576*omega_b + 1.0272489*log(A_s) + 22.72...` |
| mse40 | 4 | 23 | 0.002662 | 0.002719 | 0.9973 | valid | `489420500.0*A_s - 0.002280015*H0 - 23.804436*n_s + 24.804436*omega_cd...` |

### T0 common-complexity front comparison

| cut | method | metric | mean validation error | SE |
|---:|---|---|---:|---:|
| 1 | mse20 | nmse_val | 0.9993 | 5.551e-17 |
| 1 | mse30 | nmse_val | 0.9997 | 0.0001914 |
| 1 | mse40 | nmse_val | 0.9997 | 0.0001914 |
| 2 | mse20 | nmse_val | 0.9993 | 5.551e-17 |
| 2 | mse30 | nmse_val | 0.9994 | 6.408e-05 |
| 2 | mse40 | nmse_val | 0.9994 | 6.408e-05 |
| 3 | mse20 | nmse_val | 0.9698 | 2.402e-07 |
| 3 | mse30 | nmse_val | 0.9698 | 2.976e-07 |
| 3 | mse40 | nmse_val | 0.9699 | 0.0001749 |
| 4 | mse20 | nmse_val | 0.8675 | 2.109e-07 |
| 4 | mse30 | nmse_val | 0.8677 | 0.0001172 |
| 4 | mse40 | nmse_val | 0.8675 | 6.752e-07 |
| 5 | mse20 | nmse_val | 0.4317 | 0.0001611 |
| 5 | mse30 | nmse_val | 0.4317 | 0.0001614 |
| 5 | mse40 | nmse_val | 0.4315 | 3.296e-07 |
| 7 | mse20 | nmse_val | 0.1042 | 9.092e-08 |
| 7 | mse30 | nmse_val | 0.1046 | 0.0003491 |
| 7 | mse40 | nmse_val | 0.1048 | 0.0005474 |
| 8 | mse20 | nmse_val | 0.08354 | 0.008451 |
| 8 | mse30 | nmse_val | 0.09076 | 0.008618 |
| 8 | mse40 | nmse_val | 0.09357 | 0.007115 |
| 9 | mse20 | nmse_val | 0.055 | 0.004594 |
| 9 | mse30 | nmse_val | 0.05116 | 0.005335 |
| 9 | mse40 | nmse_val | 0.05049 | 0.005642 |
| 10 | mse20 | nmse_val | 0.055 | 0.004594 |
| 10 | mse30 | nmse_val | 0.05116 | 0.005335 |
| 10 | mse40 | nmse_val | 0.05049 | 0.005641 |
| 11 | mse20 | nmse_val | 0.03269 | 0.008944 |
| 11 | mse30 | nmse_val | 0.02047 | 0.005165 |
| 11 | mse40 | nmse_val | 0.03004 | 0.01 |
| 12 | mse20 | nmse_val | 0.02389 | 0.00744 |
| 12 | mse30 | nmse_val | 0.01933 | 0.005119 |
| 12 | mse40 | nmse_val | 0.01969 | 0.008131 |
| 13 | mse20 | nmse_val | 0.009176 | 0.0001871 |
| 13 | mse30 | nmse_val | 0.009426 | 0.0003527 |
| 13 | mse40 | nmse_val | 0.01161 | 0.002319 |
| 14 | mse20 | nmse_val | 0.009176 | 0.0001871 |
| 14 | mse30 | nmse_val | 0.008084 | 0.001481 |
| 14 | mse40 | nmse_val | 0.01147 | 0.002357 |
| 15 | mse20 | nmse_val | 0.009175 | 0.0001873 |
| 15 | mse30 | nmse_val | 0.008076 | 0.001478 |
| 15 | mse40 | nmse_val | 0.006857 | 0.001581 |
| 16 | mse20 | nmse_val | 0.007781 | 0.001468 |
| 16 | mse30 | nmse_val | 0.005266 | 0.001868 |
| 16 | mse40 | nmse_val | 0.005397 | 0.001761 |
| 17 | mse20 | nmse_val | 0.007693 | 0.001447 |
| 17 | mse30 | nmse_val | 0.005116 | 0.00177 |
| 17 | mse40 | nmse_val | 0.005347 | 0.001777 |
| 18 | mse20 | nmse_val | 0.006327 | 0.001794 |
| 18 | mse30 | nmse_val | 0.005087 | 0.001782 |
| 18 | mse40 | nmse_val | 0.003806 | 0.001235 |
| 19 | mse20 | nmse_val | 0.006325 | 0.001793 |
| 19 | mse30 | nmse_val | 0.005021 | 0.001744 |
| 19 | mse40 | nmse_val | 0.003796 | 0.001239 |
| 20 | mse20 | nmse_val | 0.006311 | 0.001787 |
| 20 | mse30 | nmse_val | 0.004908 | 0.00179 |
| 20 | mse40 | nmse_val | 0.003739 | 0.001252 |

## z3

| method | seed | symbolic core | T0 val MSE | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---:|---|---|
| mi20-mi | 0 | 17 | 13.08 | 13.58 | 13.75 | -12.75 | valid | `log(tau**2 + exp(-4.407752*n_s)*log(H0)/(omega_cdm*(omega_b - 0.00598...` |
| mi20-mi | 1 | 20 | 9.225 | 9.622 | 9.74 | -8.74 | valid | `log(-log(omega_b*(n_s - 0.51070356)*(H0*(omega_cdm + 0.014487113) + 1...` |
| mi20-mi | 2 | 18 | 41.39 | 40.86 | 41.37 | -40.37 | valid | `log(log(exp(n_s**4*(omega_b - 0.0048390473)*(omega_cdm - 0.019833282 ...` |
| mi20-mi | 3 | 18 | 115.2 | 114.2 | 115.6 | -114.6 | valid | `-omega_cdm + log(n_s**4*omega_b*omega_cdm/log(H0*exp(n_s)/omega_b)**2)` |
| mi20-mi | 4 | 17 | 21.97 | 22.61 | 22.89 | -21.89 | valid | `log(log(H0)/(omega_cdm*(omega_b*exp(3.20512692102287*n_s))**1.3713861...` |
| mi20-mse | 0 | 10 | 0.728 | 0.7844 | 0.7941 | 0.2059 | valid | `3.28277603966376*n_s + 6.47301226415742*omega_cdm + log(omega_b)` |
| mi20-mse | 1 | 13 | 0.9276 | 0.9876 | 0.9998 | 0.0002428 | valid | `omega_b*(n_s - 0.65226924)*(H0*(omega_cdm + 0.015713928) + 1.9769914)/H0` |
| mi20-mse | 2 | 13 | 0.9268 | 0.987 | 0.9992 | 0.0008377 | valid | `omega_b*(omega_cdm + 0.03980415)*(H0*n_s**4 + 14.988577)/H0` |
| mi20-mse | 3 | 10 | 0.8621 | 0.9208 | 0.9321 | 0.06785 | valid | `n_s + 2*omega_cdm + 0.3059527*log(omega_b)` |
| mi20-mse | 4 | 11 | 0.9177 | 0.9833 | 0.9954 | 0.004573 | valid | `n_s**2*(1.6434555*omega_b*log(H0) + omega_cdm)/log(H0)` |
| mse20 | 0 | 20 | 0.003624 | 0.003851 | 0.003899 | 0.9961 | valid | `(omega_b*(-0.00015971308587619*H0**2 + 28.2233954971792*n_s + omega_b...` |
| mse20 | 1 | 20 | 0.004961 | 0.005162 | 0.005225 | 0.9948 | valid | `(-26.642788*n_s - 390.60156*omega_b - 53.285576*omega_cdm + log(H0) +...` |
| mse20 | 2 | 19 | 0.002708 | 0.002933 | 0.002969 | 0.997 | valid | `-0.0230308669247791*H0 + 56.252795200844*omega_cdm + 30.772179 - 0.19...` |
| mse20 | 3 | 17 | 0.002622 | 0.002979 | 0.003016 | 0.997 | valid | `28.145832*n_s + 403.81552*omega_b - 31.462837 - 0.7123556/omega_cdm +...` |
| mse20 | 4 | 20 | 0.003058 | 0.003277 | 0.003318 | 0.9967 | valid | `-0.00016824318*H0**2*n_s + 28.9927116006847*n_s + 403.32678*omega_b +...` |
| mse30 | 0 | 25 | 0.001943 | 0.002217 | 0.002245 | 0.9978 | valid | `A_s - 0.022730602*H0 + 28.005856*n_s + 2*omega_cdm - 10.8064454 - 0.6...` |
| mse30 | 1 | 30 | 0.00179 | 0.002033 | 0.002058 | 0.9979 | valid | `-(n_s*(omega_b + omega_cdm) + omega_b + 0.86120814)*(-n_s*omega_b*ome...` |
| mse30 | 2 | 30 | 0.002489 | 0.002733 | 0.002767 | 0.9972 | valid | `(403.06772*n_s*(0.06555233*H0 + 0.06555233*log(0.000415377946157329/o...` |
| mse30 | 3 | 28 | 0.004973 | 0.005352 | 0.005418 | 0.9946 | valid | `(omega_cdm*(H0 - 2.728758)*(28.102356*n_s + omega_b**2 + 6.7175721747...` |
| mse30 | 4 | 22 | 0.004999 | 0.005401 | 0.005468 | 0.9945 | valid | `(4.7709036*omega_b - (log(H0) - 1.3541244)*(0.4035701*omega_b - (n_s ...` |
| mse40 | 0 | 36 | 0.002476 | 0.002778 | 0.002812 | 0.9972 | valid | `(-1.5866493*(0.23623509483528*H0 - 1)**4 + (4.56140432502323*omega_cd...` |
| mse40 | 1 | 39 | 0.002176 | 0.002468 | 0.002498 | 0.9975 | valid | `-1.1705339*n_s + log((-omega_b**4*(n_s**4*omega_cdm + 0.4861598684259...` |
| mse40 | 2 | 39 | 0.001881 | 0.002069 | 0.002095 | 0.9979 | valid | `0.00526937*H0 + 28.155476*n_s - 54.406345*omega_b + 54.406345*omega_c...` |
| mse40 | 3 | 27 | 0.001717 | 0.001888 | 0.001911 | 0.9981 | valid | `(-0.0020762782*H0 + omega_b**2*(H0 - 36.39311)*(H0*omega_b*omega_cdm ...` |
| mse40 | 4 | 26 | 0.001645 | 0.001882 | 0.001905 | 0.9981 | valid | `(-0.000504265*H0 + omega_b*(28.1700678693762*n_s - 249.838974272061*o...` |
| h(f1) | fixed | 6 | n/a | 0.06373 | 0.06452 | 0.9355 | fixed baseline | `h(log(omega_b)/(n_s + omega_cdm))` |
| h(f1)+g(f2), additive | fixed | 1e+01 | n/a | 0.007671 | 0.007765 | 0.9922 | fixed baseline | `h(log(omega_b)/(n_s + omega_cdm)) + g(H0/omega_cdm**2)` |
| h(f1)+g(f2), interaction-aware | fixed | 1e+01 | n/a | 0.007671 | 0.007765 | 0.9922 | fixed baseline | `h(log(omega_b)/(n_s + omega_cdm)) + g(H0/omega_cdm**2)` |

Canonical known `f2` audit source: additive residual hierarchy; expression `H0/omega_cdm**2`. The interaction-aware hierarchy remains the reconstruction denominator only.

### T0 one-standard-error readout

| method | metric | c_min | one-SE complexity | threshold | per-seed retained complexity |
|---|---|---:|---:|---:|---|
| mse20 | nmse_val | 20 | 18 | 0.004133 | s0:c18, s1:c18, s2:c17, s3:c17, s4:c18 |
| mse30 | nmse_val | 30 | 18 | 0.004282 | s0:c17, s1:c18, s2:c17, s3:c17, s4:c18 |
| mse40 | nmse_val | 39 | 26 | 0.002306 | s0:c26, s1:c26, s2:c24, s3:c26, s4:c26 |

One-SE equations are secondary confirmations and do not carry success decisions.

| method | seed | complexity | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---|---|
| mse20 | 0 | 18 | 0.003853 | 0.003901 | 0.9961 | valid | `(omega_b*(-0.000159236580112454*H0**2 + 28.2395430294395*n_s - 17.631...` |
| mse20 | 1 | 18 | 0.005289 | 0.005354 | 0.9946 | valid | `28.164545*n_s + 396.35327*omega_b + 54.32909*omega_cdm - log(H0) - 37...` |
| mse20 | 2 | 17 | 0.004014 | 0.004064 | 0.9959 | valid | `-0.02273892*H0 + 37.576923 + 1.1847267*omega_cdm/omega_b - 0.3299427/...` |
| mse20 | 3 | 17 | 0.002979 | 0.003016 | 0.997 | valid | `28.145832*n_s + 403.81552*omega_b - 31.462837 - 0.7123556/omega_cdm +...` |
| mse20 | 4 | 18 | 0.00328 | 0.003321 | 0.9967 | valid | `-0.0001624571*H0**2 + 28.1369997911262*n_s + 403.32678*omega_b + 54.3...` |
| mse30 | 0 | 17 | 0.00224 | 0.002268 | 0.9977 | valid | `-0.023083042*H0 + 28.072802*n_s - 10.388966 - 0.71120924/omega_cdm - ...` |
| mse30 | 1 | 18 | 0.002304 | 0.002332 | 0.9977 | valid | `19.339926*n_s - log(H0 - 27.774836) - 0.7083165/omega_cdm - 0.1843140...` |
| mse30 | 2 | 17 | 0.002978 | 0.003014 | 0.997 | valid | `26.426220136728*n_s + 403.0652*omega_b + 54.405334*omega_cdm - 42.274...` |
| mse30 | 3 | 17 | 0.005418 | 0.005485 | 0.9945 | valid | `28.141514*n_s + 45.487324*omega_b/omega_cdm - 20.944746 - 1.896666753...` |
| mse30 | 4 | 18 | 0.00668 | 0.006763 | 0.9932 | valid | `(7.201814*omega_b + ((n_s - 0.68721503)*(1.354238*omega_b + omega_cdm...` |
| mse40 | 0 | 26 | 0.002784 | 0.002819 | 0.9972 | valid | `0.21699251*(4.60845399686837*(omega_cdm - tau**4)*(28.144*n_s + 402.0...` |
| mse40 | 1 | 26 | 0.002723 | 0.002757 | 0.9972 | valid | `0.9805272*log(omega_b**8*(n_s**4*omega_cdm + 0.575656945401627*omega_...` |
| mse40 | 2 | 24 | 0.002249 | 0.002277 | 0.9977 | valid | `(omega_b*(-0.02296759*H0 + 28.144213*n_s - omega_b - omega_cdm*(omega...` |
| mse40 | 3 | 26 | 0.001923 | 0.001947 | 0.9981 | valid | `(-0.0021089015*H0 + omega_b**2*(H0 - 38.46404)*(28.1634586019955*n_s ...` |
| mse40 | 4 | 26 | 0.001882 | 0.001905 | 0.9981 | valid | `(-0.000504265*H0 + omega_b*(28.1700678693762*n_s - 249.838974272061*o...` |

### T0 common-complexity front comparison

| cut | method | metric | mean validation error | SE |
|---:|---|---|---:|---:|
| 1 | mse20 | nmse_val | 0.9998 | 0 |
| 1 | mse30 | nmse_val | 0.9998 | 0 |
| 1 | mse40 | nmse_val | 1.001 | 0.0007537 |
| 2 | mse20 | nmse_val | 0.9694 | 5.551e-17 |
| 2 | mse30 | nmse_val | 0.9694 | 5.551e-17 |
| 2 | mse40 | nmse_val | 0.9694 | 5.551e-17 |
| 3 | mse20 | nmse_val | 0.9401 | 5.551e-17 |
| 3 | mse30 | nmse_val | 0.9401 | 5.551e-17 |
| 3 | mse40 | nmse_val | 0.9401 | 5.551e-17 |
| 4 | mse20 | nmse_val | 0.8281 | 0 |
| 4 | mse30 | nmse_val | 0.8281 | 0 |
| 4 | mse40 | nmse_val | 0.8281 | 0 |
| 5 | mse20 | nmse_val | 0.4898 | 2.064e-06 |
| 5 | mse30 | nmse_val | 0.4897 | 5.65e-05 |
| 5 | mse40 | nmse_val | 0.4897 | 6.939e-05 |
| 6 | mse20 | nmse_val | 0.4898 | 2.064e-06 |
| 6 | mse30 | nmse_val | 0.4897 | 5.65e-05 |
| 6 | mse40 | nmse_val | 0.4897 | 6.889e-05 |
| 7 | mse20 | nmse_val | 0.305 | 5.746e-05 |
| 7 | mse30 | nmse_val | 0.3914 | 0.03538 |
| 7 | mse40 | nmse_val | 0.3606 | 0.0342 |
| 8 | mse20 | nmse_val | 0.2993 | 0.003707 |
| 8 | mse30 | nmse_val | 0.3169 | 0.01466 |
| 8 | mse40 | nmse_val | 0.3266 | 0.02977 |
| 9 | mse20 | nmse_val | 0.2195 | 0.02349 |
| 9 | mse30 | nmse_val | 0.245 | 0.006763 |
| 9 | mse40 | nmse_val | 0.2511 | 0.005639 |
| 10 | mse20 | nmse_val | 0.2 | 0.02902 |
| 10 | mse30 | nmse_val | 0.1731 | 0.04004 |
| 10 | mse40 | nmse_val | 0.227 | 0.02289 |
| 11 | mse20 | nmse_val | 0.1128 | 0.04608 |
| 11 | mse30 | nmse_val | 0.06657 | 0.03297 |
| 11 | mse40 | nmse_val | 0.08208 | 0.04399 |
| 12 | mse20 | nmse_val | 0.06633 | 0.03956 |
| 12 | mse30 | nmse_val | 0.06657 | 0.03297 |
| 12 | mse40 | nmse_val | 0.03715 | 0.008396 |
| 13 | mse20 | nmse_val | 0.0191 | 9.594e-05 |
| 13 | mse30 | nmse_val | 0.01972 | 0.0007315 |
| 13 | mse40 | nmse_val | 0.02266 | 0.002947 |
| 14 | mse20 | nmse_val | 0.01901 | 0.0001032 |
| 14 | mse30 | nmse_val | 0.0195 | 0.000587 |
| 14 | mse40 | nmse_val | 0.01904 | 0.0005582 |
| 15 | mse20 | nmse_val | 0.01682 | 0.002113 |
| 15 | mse30 | nmse_val | 0.01728 | 0.001874 |
| 15 | mse40 | nmse_val | 0.01604 | 0.002742 |
| 16 | mse20 | nmse_val | 0.01237 | 0.002736 |
| 16 | mse30 | nmse_val | 0.009903 | 0.002897 |
| 16 | mse40 | nmse_val | 0.01604 | 0.002742 |
| 17 | mse20 | nmse_val | 0.007262 | 0.002909 |
| 17 | mse30 | nmse_val | 0.004745 | 0.001095 |
| 17 | mse40 | nmse_val | 0.006662 | 0.003242 |
| 18 | mse20 | nmse_val | 0.003909 | 0.0004427 |
| 18 | mse30 | nmse_val | 0.003904 | 0.0009432 |
| 18 | mse40 | nmse_val | 0.006321 | 0.003278 |
| 19 | mse20 | nmse_val | 0.003691 | 0.0004815 |
| 19 | mse30 | nmse_val | 0.003899 | 0.0009413 |
| 19 | mse40 | nmse_val | 0.003007 | 0.0005622 |
| 20 | mse20 | nmse_val | 0.003669 | 0.000464 |
| 20 | mse30 | nmse_val | 0.003684 | 0.0008099 |
| 20 | mse40 | nmse_val | 0.002999 | 0.0005645 |

## z4

| method | seed | symbolic core | T0 val MSE | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---:|---|---|
| mi20-mi | 0 | 14 | 0.9257 | 0.9476 | 1 | -0.0001931 | valid | `2.60037297451584*A_s*(0.620129195236019*log(log(0.24930401/tau)) - 1)...` |
| mi20-mi | 1 | 17 | 5.754e+05 | 5.752e+05 | 6.072e+05 | -6.071e+05 | valid | `log(168.933888466849*A_s**2*(0.0769381272044216*log(n_s*tau) + 1)**2/...` |
| mi20-mi | 2 | 17 | 0.9255 | 0.9474 | 1 | -5.035e-05 | valid | `A_s/(tau + 0.21998107*log(log(omega_b) - log((tau - 0.011009995)**2))...` |
| mi20-mi | 3 | 19 | 0.9255 | 0.9474 | 1 | -5.036e-05 | valid | `A_s*(13.917685*exp(tau) + log(n_s**2*(H0*tau - 4.4762926*omega_cdm)))` |
| mi20-mi | 4 | 20 | 871.7 | 872.1 | 920.5 | -919.5 | valid | `exp(omega_b + tau) + log((tau*log(-A_s**2/(tau - 0.19279961))**2 + 0....` |
| mi20-mse | 0 | 4 | 0.9255 | 0.9474 | 1 | -5.035e-05 | valid | `A_s/log(tau)` |
| mi20-mse | 1 | 12 | 0.9255 | 0.9474 | 1 | -5.011e-05 | valid | `A_s*(log(tau) + 13.023911)/(tau**4*(log(tau) + 13.023911) - 0.021775315)` |
| mi20-mse | 2 | 12 | 0.9255 | 0.9474 | 1 | -5.033e-05 | valid | `A_s*log(A_s**2*(tau**2 - 0.017046053)**2/tau**4)` |
| mi20-mse | 3 | 13 | 0.9255 | 0.9474 | 1 | -5.034e-05 | valid | `-A_s*(log(H0*tau - 0.5234489) + 13.814054)*exp(tau)` |
| mi20-mse | 4 | 15 | 0.9255 | 0.9474 | 1 | -5.004e-05 | valid | `-1.0904413*tau**2/(tau**2*log(-A_s/(tau - 0.5005168))**4 + 0.5088716)` |
| mse20 | 0 | 20 | 0.07479 | 0.07351 | 0.07759 | 0.9224 | valid | `(tau + 0.9574965)**4*(59.54124*log(-log(A_s**4*tau) - 35.928722) - 22...` |
| mse20 | 1 | 19 | 0.02941 | 0.03055 | 0.03225 | 0.9678 | valid | `-n_s - 19.0123443819827*tau - 7.6674848*log(A_s) - 151.011327825574 +...` |
| mse20 | 2 | 17 | 0.3954 | 0.3838 | 0.4051 | 0.5949 | valid | `(-0.64217615*n_s*tau**2 + 0.146605257389129*omega_b)/(n_s*tau*(omega_...` |
| mse20 | 3 | 20 | 0.03423 | 0.03603 | 0.03803 | 0.962 | valid | `-105.899412073536*(0.0971747037920679*tau + 1)**2 + 260.51813 + 3062....` |
| mse20 | 4 | 19 | 0.03693 | 0.03953 | 0.04173 | 0.9583 | valid | `omega_cdm - 21.402592*tau - log(n_s - omega_b**2/tau) - 6.342145 + 1....` |
| mse30 | 0 | 26 | 0.02238 | 0.02302 | 0.0243 | 0.9757 | valid | `-n_s + 0.246140978108441*omega_b**2/tau**2 + omega_b*tau + tau - 2.46...` |
| mse30 | 1 | 30 | 0.02697 | 0.02733 | 0.02885 | 0.9712 | valid | `(0.00010385548*A_s*(0.733858937781751*tau - 1)**2 - n_s**2*tau**2*(0....` |
| mse30 | 2 | 30 | 0.02889 | 0.02987 | 0.03153 | 0.9685 | valid | `(n_s*tau**2*(7.706172*(n_s + 1.5468171)*(omega_b - tau) - 7.706172*lo...` |
| mse30 | 3 | 28 | 0.02513 | 0.02653 | 0.028 | 0.972 | valid | `(-0.000510895458627464*omega_cdm**2 + tau**2*(tau + 0.20892406*log(A_...` |
| mse30 | 4 | 30 | 0.02201 | 0.02304 | 0.02432 | 0.9757 | valid | `(-A_s*tau**2*(74.554054*tau + 25.982765) + A_s*(0.000839994058125295*...` |
| mse40 | 0 | 35 | 0.01639 | 0.01803 | 0.01903 | 0.981 | valid | `(tau*(1.0817714*n_s*(n_s + omega_b**2 - 2.248102) - 1.0817714*(181.83...` |
| mse40 | 1 | 36 | 0.02784 | 0.02898 | 0.03059 | 0.9694 | valid | `23287325765892.5*A_s**2 + 46574651531784.9*A_s**2/tau + 2228987022065...` |
| mse40 | 2 | 36 | 0.01584 | 0.01616 | 0.01706 | 0.9829 | valid | `-(n_s - log((tau*exp(2782257200.0*A_s) + log(0.054009993*tau*exp(0.10...` |
| mse40 | 3 | 35 | 0.03009 | 0.03177 | 0.03353 | 0.9665 | valid | `(tau*(tau - 3.5768354) - (omega_cdm + tau*(29.586397 - log(n_s**2/(ta...` |
| mse40 | 4 | 38 | 0.02432 | 0.02522 | 0.02662 | 0.9734 | valid | `(A_s*n_s*tau**2*(omega_b - 0.044704568) + 0.11212051772976*A_s*n_s*(t...` |
| h(f1) | fixed | 5 | n/a | 0.04128 | 0.04357 | 0.9564 | fixed baseline | `h(-A_s/(tau - 0.4454238))` |
| h(f1)+g(f2), additive | fixed | 7 | n/a | 0.03994 | 0.04216 | 0.9578 | fixed baseline | `h(-A_s/(tau - 0.4454238)) + g(tau)` |
| h(f1)+g(f2), interaction-aware | fixed | 7 | n/a | 0.03994 | 0.04216 | 0.9578 | fixed baseline | `h(-A_s/(tau - 0.4454238)) + g(tau)` |

Canonical known `f2` audit source: additive residual hierarchy; expression `tau`. The interaction-aware hierarchy remains the reconstruction denominator only.

### T0 one-standard-error readout

| method | metric | c_min | one-SE complexity | threshold | per-seed retained complexity |
|---|---|---:|---:|---:|---|
| mse20 | nmse_val | 20 | 10 | 0.1998 | s0:c9, s1:c10, s2:c10, s3:c10, s4:c9 |
| mse30 | nmse_val | 30 | 25 | 0.02852 | s0:c22, s1:c25, s2:c25, s3:c24, s4:c25 |
| mse40 | nmse_val | 38 | 26 | 0.0279 | s0:c26, s1:c26, s2:c26, s3:c26, s4:c26 |

One-SE equations are secondary confirmations and do not carry success decisions.

| method | seed | complexity | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---|---|
| mse20 | 0 | 9 | 0.2345 | 0.2475 | 0.7525 | valid | `-1.3361765*log(A_s**2*tau) - 57.18029` |
| mse20 | 1 | 10 | 0.04196 | 0.04429 | 0.9557 | valid | `-21.4091364327*tau - 7.70475*log(A_s) - 152.48530051575` |
| mse20 | 2 | 10 | 0.3891 | 0.4107 | 0.5893 | valid | `(omega_b - 764.4417641316*tau**4)/tau` |
| mse20 | 3 | 10 | 0.04203 | 0.04437 | 0.9556 | valid | `-21.408823*tau + 154.989 + 3067.5435/log(A_s)` |
| mse20 | 4 | 9 | 0.0419 | 0.04423 | 0.9558 | valid | `-21.398323*tau - 6.2113123 + 1.606601e-8/A_s` |
| mse30 | 0 | 22 | 0.02303 | 0.02431 | 0.9757 | valid | `-n_s + 0.246142367263117*omega_b**2/tau**2 + tau - 2.4650238/(omega_b...` |
| mse30 | 1 | 25 | 0.02765 | 0.02918 | 0.9708 | valid | `(-0.540090830945715*A_s*tau**2*(30.66536*tau - 1.1347975) + 0.0001099...` |
| mse30 | 2 | 25 | 0.03058 | 0.03228 | 0.9677 | valid | `19.0616757298512*omega_b - 19.0616757298512*tau - 7.706172*log(A_s) -...` |
| mse30 | 3 | 24 | 0.02655 | 0.02802 | 0.972 | valid | `0.806586438889742*(-0.000510895458627464*omega_cdm**2 + tau**2*(tau +...` |
| mse30 | 4 | 25 | 0.02819 | 0.02975 | 0.9702 | valid | `(0.0008325557133258*A_s*omega_cdm*(tau + (tau - 0.99138695)*log(H0)) ...` |
| mse40 | 0 | 26 | 0.01897 | 0.02002 | 0.98 | valid | `(-tau*(1.3394003*n_s + (157.73572*tau + 63.451225)*(tau + 0.1032205*l...` |
| mse40 | 1 | 26 | 0.02944 | 0.03108 | 0.9689 | valid | `21593724566061.3*A_s**2/tau**2 - 18.95251*tau - 7.8034480884643 + 1.1...` |
| mse40 | 2 | 26 | 0.01829 | 0.01931 | 0.9807 | valid | `-n_s + 2.5464983*log(exp(-1462110600.0*A_s)*log(0.038978126*tau*exp(0...` |
| mse40 | 3 | 26 | 0.03604 | 0.03804 | 0.962 | valid | `(-1.650841*n_s*tau - (omega_cdm + tau*(tau + 34.926605))*(tau + log(e...` |
| mse40 | 4 | 26 | 0.02792 | 0.02947 | 0.9705 | valid | `(-A_s*tau**2*(18.718685*tau + log(n_s) + 5.757772) + 0.11635177508613...` |

### T0 common-complexity front comparison

| cut | method | metric | mean validation error | SE |
|---:|---|---|---:|---:|
| 1 | mse20 | nmse_val | 1 | 4.616e-07 |
| 1 | mse30 | nmse_val | 1 | 5.416e-07 |
| 1 | mse40 | nmse_val | 1 | 6.654e-07 |
| 2 | mse20 | nmse_val | 0.9574 | 0 |
| 2 | mse30 | nmse_val | 0.9574 | 0 |
| 2 | mse40 | nmse_val | 0.9574 | 0 |
| 3 | mse20 | nmse_val | 0.8288 | 6.42e-08 |
| 3 | mse30 | nmse_val | 0.8288 | 3.906e-11 |
| 3 | mse40 | nmse_val | 0.8288 | 1.997e-08 |
| 4 | mse20 | nmse_val | 0.4906 | 4.506e-07 |
| 4 | mse30 | nmse_val | 0.4906 | 1.773e-06 |
| 4 | mse40 | nmse_val | 0.5445 | 0.05391 |
| 5 | mse20 | nmse_val | 0.4586 | 2.452e-08 |
| 5 | mse30 | nmse_val | 0.4586 | 2.923e-08 |
| 5 | mse40 | nmse_val | 0.4586 | 2.099e-08 |
| 6 | mse20 | nmse_val | 0.4439 | 0.01343 |
| 6 | mse30 | nmse_val | 0.456 | 4.733e-07 |
| 6 | mse40 | nmse_val | 0.4571 | 0.0006347 |
| 7 | mse20 | nmse_val | 0.3956 | 0.03718 |
| 7 | mse30 | nmse_val | 0.4238 | 0.0297 |
| 7 | mse40 | nmse_val | 0.3963 | 0.03708 |
| 8 | mse20 | nmse_val | 0.3289 | 0.03628 |
| 8 | mse30 | nmse_val | 0.3092 | 0.06387 |
| 8 | mse40 | nmse_val | 0.2965 | 0.06858 |
| 9 | mse20 | nmse_val | 0.2404 | 0.06253 |
| 9 | mse30 | nmse_val | 0.09372 | 0.03233 |
| 9 | mse40 | nmse_val | 0.1487 | 0.07905 |
| 10 | mse20 | nmse_val | 0.1639 | 0.07945 |
| 10 | mse30 | nmse_val | 0.07223 | 0.02917 |
| 10 | mse40 | nmse_val | 0.06505 | 0.02297 |
| 11 | mse20 | nmse_val | 0.1635 | 0.07919 |
| 11 | mse30 | nmse_val | 0.04226 | 0.000453 |
| 11 | mse40 | nmse_val | 0.04271 | 0.001186 |
| 12 | mse20 | nmse_val | 0.1499 | 0.07635 |
| 12 | mse30 | nmse_val | 0.04195 | 0.0005373 |
| 12 | mse40 | nmse_val | 0.04225 | 0.001292 |
| 13 | mse20 | nmse_val | 0.1495 | 0.07627 |
| 13 | mse30 | nmse_val | 0.04062 | 0.0005927 |
| 13 | mse40 | nmse_val | 0.0419 | 0.001039 |
| 14 | mse20 | nmse_val | 0.133 | 0.07565 |
| 14 | mse30 | nmse_val | 0.0405 | 0.0005741 |
| 14 | mse40 | nmse_val | 0.03992 | 0.00118 |
| 15 | mse20 | nmse_val | 0.1326 | 0.07533 |
| 15 | mse30 | nmse_val | 0.03873 | 0.001339 |
| 15 | mse40 | nmse_val | 0.03941 | 0.001198 |
| 16 | mse20 | nmse_val | 0.1326 | 0.07534 |
| 16 | mse30 | nmse_val | 0.03848 | 0.001255 |
| 16 | mse40 | nmse_val | 0.03857 | 0.001334 |
| 17 | mse20 | nmse_val | 0.1303 | 0.07535 |
| 17 | mse30 | nmse_val | 0.03487 | 0.001805 |
| 17 | mse40 | nmse_val | 0.03703 | 0.001805 |
| 18 | mse20 | nmse_val | 0.1283 | 0.07567 |
| 18 | mse30 | nmse_val | 0.03353 | 0.002264 |
| 18 | mse40 | nmse_val | 0.03574 | 0.001363 |
| 19 | mse20 | nmse_val | 0.1266 | 0.07609 |
| 19 | mse30 | nmse_val | 0.03295 | 0.002207 |
| 19 | mse40 | nmse_val | 0.03557 | 0.001378 |
| 20 | mse20 | nmse_val | 0.1234 | 0.07648 |
| 20 | mse30 | nmse_val | 0.03139 | 0.001539 |
| 20 | mse40 | nmse_val | 0.03286 | 0.003083 |

## z5

| method | seed | symbolic core | T0 val MSE | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---:|---|---|
| mi20-mi | 0 | 20 | 395.9 | 395.3 | 396.4 | -395.4 | valid | `log(A_s*exp(5.5231444*omega_b - 2*tau + 2.7615722*(n_s/omega_cdm - 2....` |
| mi20-mi | 1 | 19 | 15.86 | 15.72 | 15.76 | -14.76 | valid | `omega_b - 0.17572255*log(exp((2*n_s*tau + 2.8387810535324*omega_cdm)/...` |
| mi20-mi | 2 | 20 | 52.96 | 52.72 | 52.86 | -51.86 | valid | `2*omega_b - 0.706194989617168*tau + 0.356474307390437*log(A_s) - omeg...` |
| mi20-mi | 3 | 19 | 480.2 | 479.5 | 480.8 | -479.8 | valid | `log(A_s*exp(5.6754548*omega_b - 2*tau - 2.8377274*omega_cdm/n_s)/log(...` |
| mi20-mi | 4 | 20 | 464.6 | 465.4 | 466.6 | -465.6 | valid | `log(5.87278128727684*(-omega_b + 0.412646424488882*tau + 0.3388730221...` |
| mi20-mse | 0 | 12 | 1.009 | 0.9973 | 1 | -8.271e-06 | valid | `A_s*exp(-2*tau + 2*exp(n_s/(H0*omega_cdm)))` |
| mi20-mse | 1 | 1 | 1.009 | 0.9973 | 1 | -8.274e-06 | valid | `A_s` |
| mi20-mse | 2 | 8 | 1.009 | 0.9973 | 1 | -8.273e-06 | valid | `A_s*(n_s - log(omega_cdm + tau))` |
| mi20-mse | 3 | 1 | 1.009 | 0.9973 | 1 | -8.274e-06 | valid | `A_s` |
| mi20-mse | 4 | 1 | 1.009 | 0.9973 | 1 | -8.274e-06 | valid | `A_s` |
| mse20 | 0 | 19 | 0.007287 | 0.007546 | 0.007567 | 0.9924 | valid | `-0.027911885*H0 + n_s*(tau + 181.911927925729*(0.0741428731683096*ome...` |
| mse20 | 1 | 18 | 0.03399 | 0.03438 | 0.03447 | 0.9655 | valid | `(-6.086418*A_s*tau + A_s*(n_s - 0.617876)*(6.086418*log(omega_cdm) + ...` |
| mse20 | 2 | 19 | 0.007661 | 0.007796 | 0.007817 | 0.9922 | valid | `(176.38174*H0 + (omega_cdm + 8.743812)*(H0*(-2*tau + log(A_s)) + 16.3...` |
| mse20 | 3 | 20 | 0.02602 | 0.02645 | 0.02652 | 0.9735 | valid | `omega_cdm + 4.5428095*tau*log(omega_b) + 4.5428095*log(A_s**2) + 185....` |
| mse20 | 4 | 19 | 0.04251 | 0.04148 | 0.04159 | 0.9584 | valid | `(A_s*(log(n_s**4) + 9.042901) - 2.7566414e-6*omega_cdm**2*tau - 1.597...` |
| mse30 | 0 | 29 | 0.001413 | 0.00141 | 0.001414 | 0.9986 | valid | `0.8079668*H0*omega_b - 0.0470678603120928*H0 + 0.35938920761092*n_s/o...` |
| mse30 | 1 | 26 | 0.005925 | 0.005942 | 0.005957 | 0.994 | valid | `3.9233449*n_s - 25.9419835199049*omega_cdm - 18.0952937199049*tau + 7...` |
| mse30 | 2 | 13 | 0.4478 | 0.4401 | 0.4413 | 0.5587 | valid | `(A_s*(tau + 1.5865281) - 4.1268066e-8*tau - 5.67428e-10)/(A_s*n_s)` |
| mse30 | 3 | 29 | 0.02214 | 0.02252 | 0.02258 | 0.9774 | valid | `1.17678355728348*omega_b - 17.9779095132054*tau - 1.17678355728348*lo...` |
| mse30 | 4 | 30 | 0.003391 | 0.003279 | 0.003288 | 0.9967 | valid | `omega_b*log(n_s) + 46.478407*omega_b - 17.8204*tau + 5.7030816 - 25.7...` |
| mse40 | 0 | 40 | 0.000687 | 0.0007418 | 0.0007438 | 0.9993 | valid | `(n_s*omega_cdm**2 + (n_s*(omega_b - 7.73451*omega_cdm + log(n_s) + lo...` |
| mse40 | 1 | 40 | 0.0005776 | 0.0006344 | 0.000636 | 0.9994 | valid | `(H0*(n_s - 2*omega_b - 26.341993*omega_cdm - tau*(log(n_s) + 17.86662...` |
| mse40 | 2 | 36 | 0.004225 | 0.004136 | 0.004147 | 0.9959 | valid | `1.011365*n_s*omega_b/omega_cdm + 0.33324038828955*n_s/omega_cdm + 1.0...` |
| mse40 | 3 | 40 | 0.003756 | 0.004147 | 0.004158 | 0.9958 | valid | `(4.05180101456671e+16*A_s**2 + omega_b - omega_cdm - 0.75670004*tau +...` |
| mse40 | 4 | 32 | 0.01515 | 0.01569 | 0.01573 | 0.9843 | valid | `omega_cdm + tau - 0.06374692 + (2.2001908*n_s*(-tau + 0.6569637 + 4.1...` |
| h(f1) | fixed | 5 | n/a | 0.08862 | 0.08886 | 0.9111 | fixed baseline | `h(A_s*exp(-2*tau))` |
| h(f1)+g(f2), additive | fixed | 1e+01 | n/a | 0.007235 | 0.007255 | 0.9927 | fixed baseline | `h(A_s*exp(-2*tau)) + g(H0*omega_cdm/n_s)` |
| h(f1)+g(f2), interaction-aware | fixed | 1e+01 | n/a | 0.007235 | 0.007255 | 0.9927 | fixed baseline | `h(A_s*exp(-2*tau)) + g(H0*omega_cdm/n_s)` |

Canonical known `f2` audit source: additive residual hierarchy; expression `H0*omega_cdm/n_s`. The interaction-aware hierarchy remains the reconstruction denominator only.

### T0 one-standard-error readout

| method | metric | c_min | one-SE complexity | threshold | per-seed retained complexity |
|---|---|---:|---:|---:|---|
| mse20 | nmse_val | 20 | 18 | 0.03027 | s0:c17, s1:c18, s2:c18, s3:c18, s4:c18 |
| mse30 | nmse_val | 30 | 9 | 0.1826 | s0:c9, s1:c9, s2:c9, s3:c9, s4:c9 |
| mse40 | nmse_val | 40 | 26 | 0.007492 | s0:c26, s1:c25, s2:c26, s3:c26, s4:c26 |

One-SE equations are secondary confirmations and do not carry success decisions.

| method | seed | complexity | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---|---|
| mse20 | 0 | 17 | 0.01356 | 0.0136 | 0.9864 | valid | `-0.027772387*H0 + n_s*(181.913978027401*(0.074142455386075*omega_cdm ...` |
| mse20 | 1 | 18 | 0.03438 | 0.03447 | 0.9655 | valid | `(-6.086418*A_s*tau + A_s*(n_s - 0.617876)*(6.086418*log(omega_cdm) + ...` |
| mse20 | 2 | 18 | 0.008429 | 0.008452 | 0.9915 | valid | `(176.22318*H0 + (omega_cdm + 8.751241)*(H0*(-2*tau + log(A_s)) + 18.2...` |
| mse20 | 3 | 18 | 0.02648 | 0.02655 | 0.9735 | valid | `4.5508814*tau*log(omega_b) + 4.5508814*log(A_s**2) + 186.15706 - 25.4...` |
| mse20 | 4 | 18 | 0.04244 | 0.04255 | 0.9574 | valid | `(A_s*(log(n_s**2) + 9.065641) - 2.810866e-6*omega_cdm**2*tau - 1.6122...` |
| mse30 | 0 | 9 | 0.089 | 0.08923 | 0.9108 | valid | `-17.820156*tau + 10.185287 - 1.863041e-8/A_s` |
| mse30 | 1 | 9 | 0.08933 | 0.08957 | 0.9104 | valid | `-17.272799*tau + 10.1923275 - 1.8731386e-8/A_s` |
| mse30 | 2 | 9 | 0.4522 | 0.4534 | 0.5466 | valid | `(1.5865281*A_s - 4.1268066e-8*tau - 5.67428e-10)/A_s` |
| mse30 | 3 | 9 | 0.08976 | 0.09 | 0.91 | valid | `-18.519096*tau + 10.1321535 - 1.8414271e-8/A_s` |
| mse30 | 4 | 9 | 0.08935 | 0.08958 | 0.9104 | valid | `10.232994*exp(-2*tau) - 1.8587606e-8/A_s` |
| mse40 | 0 | 26 | 0.002134 | 0.00214 | 0.9979 | valid | `(n_s*(-8.37326*omega_cdm + log(omega_b) + 13.597701) + (n_s*(log(A_s*...` |
| mse40 | 1 | 25 | 0.004284 | 0.004295 | 0.9957 | valid | `n_s**2 + n_s - 26.234165*omega_cdm - 17.823137*tau + 8.933948*log(A_s...` |
| mse40 | 2 | 26 | 0.005727 | 0.005742 | 0.9943 | valid | `2*n_s*tau + 0.35656828*n_s/omega_cdm - 19.4450915338794*tau + 6.23315...` |
| mse40 | 3 | 26 | 0.006889 | 0.006908 | 0.9931 | valid | `9.96178882312381e+17*A_s**2 + 22.9200012881041*omega_b - 22.920001288...` |
| mse40 | 4 | 26 | 0.017 | 0.01704 | 0.983 | valid | `-2.2001908*n_s*tau/omega_cdm + 1.44544548867396*n_s/omega_cdm + omega...` |

### T0 common-complexity front comparison

| cut | method | metric | mean validation error | SE |
|---:|---|---|---:|---:|
| 1 | mse20 | nmse_val | 1 | 3.773e-08 |
| 1 | mse30 | nmse_val | 1 | 2.805e-08 |
| 1 | mse40 | nmse_val | 1 | 6.516e-09 |
| 2 | mse20 | nmse_val | 0.9662 | 5.551e-17 |
| 2 | mse30 | nmse_val | 0.9662 | 5.551e-17 |
| 2 | mse40 | nmse_val | 0.9662 | 5.551e-17 |
| 3 | mse20 | nmse_val | 0.8958 | 1.311e-06 |
| 3 | mse30 | nmse_val | 0.8958 | 6.787e-07 |
| 3 | mse40 | nmse_val | 0.8958 | 3.809e-07 |
| 4 | mse20 | nmse_val | 0.6927 | 0.04336 |
| 4 | mse30 | nmse_val | 0.6493 | 2.186e-06 |
| 4 | mse40 | nmse_val | 0.7343 | 0.05208 |
| 5 | mse20 | nmse_val | 0.5907 | 0.03018 |
| 5 | mse30 | nmse_val | 0.5002 | 0.03018 |
| 5 | mse40 | nmse_val | 0.5608 | 0.03682 |
| 6 | mse20 | nmse_val | 0.4837 | 0.01463 |
| 6 | mse30 | nmse_val | 0.5002 | 0.03018 |
| 6 | mse40 | nmse_val | 0.5002 | 0.03018 |
| 7 | mse20 | nmse_val | 0.4622 | 0.008259 |
| 7 | mse30 | nmse_val | 0.4394 | 0.00895 |
| 7 | mse40 | nmse_val | 0.4742 | 0.02601 |
| 8 | mse20 | nmse_val | 0.2036 | 0.0701 |
| 8 | mse30 | nmse_val | 0.2877 | 0.06833 |
| 8 | mse40 | nmse_val | 0.3724 | 0.06943 |
| 9 | mse20 | nmse_val | 0.09634 | 0.000363 |
| 9 | mse30 | nmse_val | 0.1661 | 0.07233 |
| 9 | mse40 | nmse_val | 0.2384 | 0.0878 |
| 10 | mse20 | nmse_val | 0.08404 | 0.01024 |
| 10 | mse30 | nmse_val | 0.1661 | 0.07233 |
| 10 | mse40 | nmse_val | 0.1473 | 0.06654 |
| 11 | mse20 | nmse_val | 0.07787 | 0.01024 |
| 11 | mse30 | nmse_val | 0.1531 | 0.07402 |
| 11 | mse40 | nmse_val | 0.1034 | 0.03166 |
| 12 | mse20 | nmse_val | 0.04657 | 0.004591 |
| 12 | mse30 | nmse_val | 0.1403 | 0.07728 |
| 12 | mse40 | nmse_val | 0.07078 | 0.01257 |
| 13 | mse20 | nmse_val | 0.046 | 0.004848 |
| 13 | mse30 | nmse_val | 0.1305 | 0.0786 |
| 13 | mse40 | nmse_val | 0.06015 | 0.01332 |
| 14 | mse20 | nmse_val | 0.0419 | 0.005816 |
| 14 | mse30 | nmse_val | 0.1285 | 0.07904 |
| 14 | mse40 | nmse_val | 0.03497 | 0.0039 |
| 15 | mse20 | nmse_val | 0.0386 | 0.007665 |
| 15 | mse30 | nmse_val | 0.1232 | 0.08036 |
| 15 | mse40 | nmse_val | 0.03319 | 0.004053 |
| 16 | mse20 | nmse_val | 0.03231 | 0.008216 |
| 16 | mse30 | nmse_val | 0.1195 | 0.08115 |
| 16 | mse40 | nmse_val | 0.02905 | 0.004589 |
| 17 | mse20 | nmse_val | 0.03157 | 0.008598 |
| 17 | mse30 | nmse_val | 0.1079 | 0.08414 |
| 17 | mse40 | nmse_val | 0.02605 | 0.004895 |
| 18 | mse20 | nmse_val | 0.02492 | 0.006532 |
| 18 | mse30 | nmse_val | 0.1078 | 0.08415 |
| 18 | mse40 | nmse_val | 0.02341 | 0.004083 |
| 19 | mse20 | nmse_val | 0.02329 | 0.006981 |
| 19 | mse30 | nmse_val | 0.1051 | 0.08488 |
| 19 | mse40 | nmse_val | 0.0169 | 0.00325 |
| 20 | mse20 | nmse_val | 0.02329 | 0.006981 |
| 20 | mse30 | nmse_val | 0.1028 | 0.0854 |
| 20 | mse40 | nmse_val | 0.0146 | 0.002269 |

## Shuffled-target controls

| method | latent | seed | T0 val R² vs true | T0 val R² vs shuffle | T2 R² vs true | T2 R² vs independent shuffle |
|---|---:|---:|---:|---:|---:|---:|
| mse20-shuffled | z5 | 0 | -0.001295 | -0.00103 | 0.0004815 | -0.002061 |
| mse20-shuffled | z5 | 1 | 0.004877 | -0.0001441 | 0.003732 | -0.0003833 |
| mse20-shuffled | z5 | 2 | 0.006901 | -0.0002723 | 0.005115 | -0.004189 |
| mse40-shuffled | z5 | 0 | -0.002808 | -0.0006838 | -0.0005556 | -0.001154 |
| mse40-shuffled | z5 | 1 | 0.004878 | -0.0001433 | 0.003732 | -0.0003833 |
| mse40-shuffled | z5 | 2 | 0.00537 | -0.0003295 | 0.002047 | -0.004709 |

---
_Generated by `scripts/consolidate_mse_one_stage.py confirm`._
