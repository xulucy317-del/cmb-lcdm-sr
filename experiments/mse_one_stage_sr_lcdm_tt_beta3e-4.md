# One-stage MSE symbolic reconstruction — `lcdm_tt_beta3e-4`

Frozen direct latent reconstruction with T0-selected equations, T1-only calibrations, and T2 confirmation. The existing interaction-aware hierarchy is recomputed on T2; its stored T1 combined R² is never reused as a confirmatory score.

| latent | classification | flags | MSE20 | MSE30 | MSE40 | IA hierarchy MSE | objective | capacity | f2 absorbed | matches IA | saturated | R_SR |
|---:|---|---|---:|---:|---:|---:|---|---|---|---|---|---:|
| z0 | no capacity gain | symbolically-stable | 0.004544 | 0.003587 | 0.003607 | 0.01063 | PASS | FAIL | FAIL | PASS | FAIL | 1.00 |
| z1 | partial absorption | symbolically-stable | 0.06657 | 0.04139 | 0.03216 | 0.01655 | PASS | PASS | FAIL | FAIL | PASS | 1.00 |
| z2 | no capacity gain | symbolically-stable | 0.1649 | 0.1507 | 0.06965 | 0.007313 | PASS | FAIL | FAIL | FAIL | FAIL | 0.80 |
| z3 | no capacity gain | symbolically-stable | 0.003401 | 0.002389 | 0.002602 | 0.01139 | PASS | FAIL | FAIL | PASS | FAIL | 1.00 |
| z4 | partial absorption | symbolically-stable | 0.1067 | 0.009108 | 0.003762 | 0.005313 | PASS | PASS | FAIL | FAIL | PASS | 1.00 |

## z0

| method | seed | symbolic core | T0 val MSE | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---:|---|---|
| mi20-mi | 0 | 20 | 36.6 | 36.71 | 37.77 | -36.77 | valid | `log((H0 + log(A_s)/omega_b)*(-0.42306665*n_s + omega_cdm - 0.31238765...` |
| mi20-mi | 1 | 19 | 55.93 | 55.68 | 57.28 | -56.28 | valid | `log(omega_b/((-n_s + log(omega_cdm)/log(H0))*(log(A_s*omega_b*omega_c...` |
| mi20-mi | 2 | 20 | 5.619 | 5.636 | 5.798 | -4.798 | valid | `log(log((n_s*(omega_b + omega_cdm - 0.53592473) + 0.08759481)*log(A_s...` |
| mi20-mi | 3 | 20 | 1.231e+04 | 1.231e+04 | 1.266e+04 | -1.266e+04 | valid | `-tau + log(-(0.3918173*n_s - omega_cdm)*(H0*omega_b**2 - 0.2200873667...` |
| mi20-mi | 4 | 20 | 603.8 | 603.9 | 621.2 | -620.2 | valid | `log(n_s*(omega_b*(tau**2 + log(H0)) + 0.42078545496165*omega_cdm - 0....` |
| mi20-mse | 0 | 8 | 1.012 | 0.9718 | 0.9998 | 0.0001869 | valid | `omega_b**2/(-0.4681821*n_s + omega_cdm)` |
| mi20-mse | 1 | 11 | 1.011 | 0.9702 | 0.9982 | 0.001847 | valid | `-omega_b*log(H0)/(0.871055783196306*n_s*log(H0) - log(omega_cdm))` |
| mi20-mse | 2 | 8 | 1.011 | 0.9705 | 0.9984 | 0.001606 | valid | `-omega_b/(n_s - 0.2654656*log(omega_cdm))` |
| mi20-mse | 3 | 7 | 1.011 | 0.9706 | 0.9986 | 0.001426 | valid | `-omega_b*(n_s*omega_cdm + 0.42737794)/n_s` |
| mi20-mse | 4 | 7 | 1.012 | 0.9716 | 0.9996 | 0.0004411 | valid | `-omega_b/(exp(n_s) - log(omega_cdm))` |
| mse20 | 0 | 20 | 0.003963 | 0.00406 | 0.004177 | 0.9958 | valid | `(H0*(-1259.1335*A_s + 11.279385886209*n_s - 1259.1335*omega_b*(omega_...` |
| mse20 | 1 | 20 | 0.004449 | 0.004496 | 0.004625 | 0.9954 | valid | `11.2703491442568*n_s - 793.8564*omega_b - tau**2 + 2.02976006665092 +...` |
| mse20 | 2 | 20 | 0.004963 | 0.005007 | 0.005151 | 0.9948 | valid | `11.348798*n_s - 937.24910791648*omega_b + 16.4518690018052*omega_b/om...` |
| mse20 | 3 | 18 | 0.004483 | 0.004563 | 0.004694 | 0.9953 | valid | `11.278338*n_s - 793.70294*omega_b - 27.51522*omega_cdm + 8.3309060713...` |
| mse20 | 4 | 17 | 0.004552 | 0.004595 | 0.004727 | 0.9953 | valid | `-0.019869063*H0 + 11.2735930941027*n_s - 793.7023*omega_b + 4.8259936...` |
| mse30 | 0 | 30 | 0.003646 | 0.003755 | 0.003863 | 0.9961 | valid | `(-2.3760228*omega_cdm - 0.6462541)*(792.3245*A_s + H0*omega_b - 12.27...` |
| mse30 | 1 | 23 | 0.00436 | 0.004381 | 0.004507 | 0.9955 | valid | `((870.11786 - exp(2*A_s)/omega_cdm**2)*(omega_b - 0.12134217/H0) - 26...` |
| mse30 | 2 | 27 | 0.001434 | 0.001533 | 0.001577 | 0.9984 | valid | `(H0*n_s*(n_s - 0.63323146*log(A_s) + 30.16227) - H0*(987.2135*n_s + 2...` |
| mse30 | 3 | 25 | 0.004013 | 0.003963 | 0.004077 | 0.9959 | valid | `(exp(omega_cdm) - 0.119536564)**2*(H0*omega_b*(11.205064*n_s - 27.217...` |
| mse30 | 4 | 30 | 0.004355 | 0.004303 | 0.004427 | 0.9956 | valid | `(-omega_b*(0.01954136*H0 + 26.506264*omega_cdm + 5.97977360862559) - ...` |
| mse40 | 0 | 37 | 0.003151 | 0.003112 | 0.003202 | 0.9968 | valid | `(-1392.39141267514*A_s*H0**2 + 770.670243855226*omega_b**2 + 0.902853...` |
| mse40 | 1 | 37 | 0.003985 | 0.003866 | 0.003977 | 0.996 | valid | `-A_s + 1.1049995*n_s + 0.189879*n_s/omega_b + omega_b**2 - 413.411735...` |
| mse40 | 2 | 37 | 0.001992 | 0.002092 | 0.002152 | 0.9978 | valid | `(-3.91713328479001*A_s*(omega_b - tau)**2*(omega_cdm - 1.0495782) + A...` |
| mse40 | 3 | 31 | 0.004344 | 0.004438 | 0.004566 | 0.9954 | valid | `(n_s*(H0 - 10.3037253854979*tau)*(-794.84454*omega_b - tau*(tau + 0.4...` |
| mse40 | 4 | 40 | 0.004707 | 0.004529 | 0.004659 | 0.9953 | valid | `0.113194495*H0*n_s - 0.1301869*H0 - n_s*tau + 0.37281317*n_s/omega_cd...` |
| h(f1) | fixed | 3 | n/a | 0.0923 | 0.09495 | 0.905 | fixed baseline | `h(n_s/omega_b)` |
| h(f1)+g(f2), additive | fixed | 1e+01 | n/a | 0.01062 | 0.01093 | 0.9891 | fixed baseline | `h(n_s/omega_b) + g(n_s*(H0 + 1325.0747*omega_cdm))` |
| h(f1)+g(f2), interaction-aware | fixed | 1e+01 | n/a | 0.01063 | 0.01094 | 0.9891 | fixed baseline | `h(n_s/omega_b) + g(n_s*(H0 + 1311.2706*omega_cdm))` |

Canonical known `f2` audit source: additive residual hierarchy; expression `n_s*(H0 + 1325.0747*omega_cdm)`. The interaction-aware hierarchy remains the reconstruction denominator only.

### T0 one-standard-error readout

| method | metric | c_min | one-SE complexity | threshold | per-seed retained complexity |
|---|---|---:|---:|---:|---|
| mse20 | nmse_val | 20 | 20 | 0.004583 | s0:c20, s1:c20, s2:c20, s3:c18, s4:c17 |
| mse30 | nmse_val | 30 | 20 | 0.004058 | s0:c20, s1:c19, s2:c20, s3:c20, s4:c20 |
| mse40 | nmse_val | 40 | 22 | 0.00407 | s0:c22, s1:c22, s2:c22, s3:c22, s4:c22 |

One-SE equations are secondary confirmations and do not carry success decisions.

| method | seed | complexity | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---|---|
| mse20 | 0 | 20 | 0.00406 | 0.004177 | 0.9958 | valid | `(H0*(-1259.1335*A_s + 11.279385886209*n_s - 1259.1335*omega_b*(omega_...` |
| mse20 | 1 | 20 | 0.004496 | 0.004625 | 0.9954 | valid | `11.2703491442568*n_s - 793.8564*omega_b - tau**2 + 2.02976006665092 +...` |
| mse20 | 2 | 20 | 0.005007 | 0.005151 | 0.9948 | valid | `11.348798*n_s - 937.24910791648*omega_b + 16.4518690018052*omega_b/om...` |
| mse20 | 3 | 18 | 0.004563 | 0.004694 | 0.9953 | valid | `11.278338*n_s - 793.70294*omega_b - 27.51522*omega_cdm + 8.3309060713...` |
| mse20 | 4 | 17 | 0.004595 | 0.004727 | 0.9953 | valid | `-0.019869063*H0 + 11.2735930941027*n_s - 793.7023*omega_b + 4.8259936...` |
| mse30 | 0 | 20 | 0.004447 | 0.004575 | 0.9954 | valid | `-0.0198458731792269*H0 + 11.28235*n_s - 791.8307*omega_b - 27.736267*...` |
| mse30 | 1 | 19 | 0.004379 | 0.004505 | 0.9955 | valid | `-870.11914*omega_b + omega_b*exp(A_s)/omega_cdm**2 + 26.938654 - 10.4...` |
| mse30 | 2 | 20 | 0.00163 | 0.001677 | 0.9983 | valid | `(H0*(-0.5659249*n_s*log(A_s) - 1218.7023*omega_b*(omega_cdm + 0.53690...` |
| mse30 | 3 | 20 | 0.004341 | 0.004466 | 0.9955 | valid | `(11.232017*H0*n_s*omega_b + 0.3821401*H0 - omega_b*(tau**2 + 27.29441...` |
| mse30 | 4 | 20 | 0.00465 | 0.004784 | 0.9952 | valid | `-27.918356*omega_cdm - log(H0) + 1 + 0.37978023/omega_b - 10.811619/n...` |
| mse40 | 0 | 22 | 0.003842 | 0.003952 | 0.996 | valid | `(747.45372880822*omega_b**2 + omega_b*omega_cdm*(-H0 + 512.0982422151...` |
| mse40 | 1 | 22 | 0.004134 | 0.004253 | 0.9957 | valid | `-tau**2 + 0.19718611/omega_b - 372.4508*omega_b/n_s - 15.587016*omega...` |
| mse40 | 2 | 22 | 0.003006 | 0.003093 | 0.9969 | valid | `11.2400820796977*n_s - 796.263146143202*omega_b - 25.8952867375807*om...` |
| mse40 | 3 | 22 | 0.004472 | 0.004601 | 0.9954 | valid | `-794.8447*omega_b - 0.46785718*tau + 26.986241368073 - 26.67188505829...` |
| mse40 | 4 | 22 | 0.00476 | 0.004897 | 0.9951 | valid | `0.1309481*H0 - 0.14589529*H0/n_s - 19.12339 + 0.35990542/omega_cdm + ...` |

### T0 common-complexity front comparison

| cut | method | metric | mean validation error | SE |
|---:|---|---|---:|---:|
| 1 | mse20 | nmse_val | 1 | 6.774e-09 |
| 1 | mse30 | nmse_val | 1 | 1.739e-10 |
| 1 | mse40 | nmse_val | 1 | 2.193e-10 |
| 2 | mse20 | nmse_val | 0.9862 | 0 |
| 2 | mse30 | nmse_val | 0.9862 | 0 |
| 2 | mse40 | nmse_val | 0.9862 | 0 |
| 3 | mse20 | nmse_val | 0.976 | 0 |
| 3 | mse30 | nmse_val | 0.976 | 0 |
| 3 | mse40 | nmse_val | 0.976 | 0 |
| 4 | mse20 | nmse_val | 0.9184 | 0.01157 |
| 4 | mse30 | nmse_val | 0.9312 | 0.01491 |
| 4 | mse40 | nmse_val | 0.9675 | 0.0004247 |
| 5 | mse20 | nmse_val | 0.1599 | 1.438e-05 |
| 5 | mse30 | nmse_val | 0.1598 | 1.179e-05 |
| 5 | mse40 | nmse_val | 0.1599 | 1.444e-05 |
| 6 | mse20 | nmse_val | 0.1596 | 0.0001157 |
| 6 | mse30 | nmse_val | 0.1598 | 8.643e-05 |
| 6 | mse40 | nmse_val | 0.1599 | 1.444e-05 |
| 7 | mse20 | nmse_val | 0.0933 | 1.512e-05 |
| 7 | mse30 | nmse_val | 0.09322 | 6.166e-05 |
| 7 | mse40 | nmse_val | 0.09362 | 0.000187 |
| 8 | mse20 | nmse_val | 0.09166 | 0.001639 |
| 8 | mse30 | nmse_val | 0.0896 | 0.002806 |
| 8 | mse40 | nmse_val | 0.09271 | 0.0006101 |
| 9 | mse20 | nmse_val | 0.0731 | 1.574e-06 |
| 9 | mse30 | nmse_val | 0.06849 | 0.002837 |
| 9 | mse40 | nmse_val | 0.06889 | 0.002593 |
| 10 | mse20 | nmse_val | 0.07123 | 0.001776 |
| 10 | mse30 | nmse_val | 0.05982 | 0.004176 |
| 10 | mse40 | nmse_val | 0.06889 | 0.002593 |
| 11 | mse20 | nmse_val | 0.02837 | 0.004295 |
| 11 | mse30 | nmse_val | 0.03078 | 0.002464 |
| 11 | mse40 | nmse_val | 0.03662 | 0.004507 |
| 12 | mse20 | nmse_val | 0.01932 | 0.00166 |
| 12 | mse30 | nmse_val | 0.02339 | 0.002578 |
| 12 | mse40 | nmse_val | 0.03158 | 0.004008 |
| 13 | mse20 | nmse_val | 0.01506 | 0.0001774 |
| 13 | mse30 | nmse_val | 0.01609 | 0.0009628 |
| 13 | mse40 | nmse_val | 0.01783 | 0.001654 |
| 14 | mse20 | nmse_val | 0.01504 | 0.0001766 |
| 14 | mse30 | nmse_val | 0.01313 | 0.001811 |
| 14 | mse40 | nmse_val | 0.01549 | 0.0002217 |
| 15 | mse20 | nmse_val | 0.01075 | 0.002129 |
| 15 | mse30 | nmse_val | 0.01309 | 0.001802 |
| 15 | mse40 | nmse_val | 0.01469 | 0.0005292 |
| 16 | mse20 | nmse_val | 0.01049 | 0.002236 |
| 16 | mse30 | nmse_val | 0.01131 | 0.001788 |
| 16 | mse40 | nmse_val | 0.01273 | 0.00192 |
| 17 | mse20 | nmse_val | 0.006527 | 0.001974 |
| 17 | mse30 | nmse_val | 0.006866 | 0.002 |
| 17 | mse40 | nmse_val | 0.008749 | 0.002317 |
| 18 | mse20 | nmse_val | 0.005733 | 0.001403 |
| 18 | mse30 | nmse_val | 0.004791 | 0.0001939 |
| 18 | mse40 | nmse_val | 0.00855 | 0.002375 |
| 19 | mse20 | nmse_val | 0.00573 | 0.001403 |
| 19 | mse30 | nmse_val | 0.004549 | 0.0002191 |
| 19 | mse40 | nmse_val | 0.006445 | 0.001945 |
| 20 | mse20 | nmse_val | 0.004426 | 0.0001571 |
| 20 | mse30 | nmse_val | 0.003856 | 0.0005946 |
| 20 | mse40 | nmse_val | 0.006257 | 0.002001 |

## z1

| method | seed | symbolic core | T0 val MSE | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---:|---|---|
| mi20-mi | 0 | 20 | 556.7 | 557.7 | 660.5 | -659.5 | valid | `tau + log(A_s*(omega_b + omega_cdm)**2*exp(-2*n_s)/(H0**2*omega_b**2*...` |
| mi20-mi | 1 | 20 | 10.21 | 10.11 | 11.97 | -10.97 | valid | `log(-tau + log(H0**2*omega_b*(n_s - 0.5812182)**2/(A_s*(omega_b - 0.7...` |
| mi20-mi | 2 | 20 | 684.5 | 685.6 | 812.1 | -811.1 | valid | `tau - log(H0**2*omega_b*(n_s - 0.20020296)**4/(A_s*(omega_b - 0.71547...` |
| mi20-mi | 3 | 19 | 1018 | 1018 | 1205 | -1204 | valid | `-tau + log(H0**2*omega_b*exp(2*exp(n_s))/(A_s*(omega_b - 0.74252105*o...` |
| mi20-mi | 4 | 20 | 762.4 | 763.6 | 904.4 | -903.4 | valid | `-n_s + omega_cdm + tau + log(A_s*(omega_b - omega_cdm)**2/(H0**2*n_s*...` |
| mi20-mse | 0 | 13 | 0.8564 | 0.8447 | 1 | -0.0004047 | valid | `0.194341515781422*A_s*omega_cdm**2/(H0**2*omega_b**2*(0.4408418262613...` |
| mi20-mse | 1 | 14 | 0.8564 | 0.8447 | 1 | -0.0004047 | valid | `A_s*(omega_b - omega_cdm)**2/(H0**2*omega_b*(n_s - 0.5691215)**2)` |
| mi20-mse | 2 | 15 | 0.8564 | 0.8447 | 1 | -0.0004047 | valid | `0.242379941804788*A_s*omega_cdm**2/(H0**2*omega_b**2*(-0.492320974370...` |
| mi20-mse | 3 | 13 | 0.8564 | 0.8447 | 1 | -0.0004047 | valid | `0.194284246892964*A_s*omega_cdm**2/(H0**2*omega_b**2*(0.4407768674658...` |
| mi20-mse | 4 | 16 | 0.8564 | 0.8447 | 1 | -0.0004047 | valid | `A_s*(omega_b*(tau - 3.222361) + omega_cdm)/(H0**2*(n_s - 0.76890296)*...` |
| mse20 | 0 | 19 | 0.07887 | 0.07953 | 0.09419 | 0.9058 | valid | `(n_s*(0.09251828*H0*n_s + 223.01692*omega_b - tau) - 70.4190956240408...` |
| mse20 | 1 | 19 | 0.07785 | 0.07611 | 0.09014 | 0.9099 | valid | `n_s/omega_cdm + (H0*omega_b - tau)**2/n_s - 8.299721/n_s - 147.20245/...` |
| mse20 | 2 | 20 | 0.05874 | 0.05747 | 0.06806 | 0.9319 | valid | `229.86078*omega_b - log(A_s) - 17.15859 - tau/n_s - 4450.4395*omega_c...` |
| mse20 | 3 | 20 | 0.07387 | 0.0733 | 0.08681 | 0.9132 | valid | `1.3824773*(H0 + 10.047512/omega_cdm)*(omega_b + 0.04679829) + 1.14116...` |
| mse20 | 4 | 20 | 0.04672 | 0.04645 | 0.05501 | 0.945 | valid | `H0*(n_s*(2*omega_b + 0.17511581) - omega_cdm) - 2*log(A_s) - 46.80709` |
| mse30 | 0 | 30 | 0.02253 | 0.02373 | 0.02811 | 0.9719 | valid | `(1.0419122*H0*(2*omega_b - omega_cdm + 0.15936542) - n_s*(3.545336893...` |
| mse30 | 1 | 30 | 0.01127 | 0.01179 | 0.01396 | 0.986 | valid | `A_s + 0.0947753452193385*H0 + 238.71527*omega_b - 25.5351334329*tau**...` |
| mse30 | 2 | 26 | 0.03242 | 0.03038 | 0.03598 | 0.964 | valid | `0.0953087860422342*H0 + n_s - 3.2192442*tau - 3.2192442*log(2*A_s) - ...` |
| mse30 | 3 | 28 | 0.07421 | 0.07337 | 0.0869 | 0.9131 | valid | `H0*(-0.08188625*n_s - omega_b)**2/omega_cdm + omega_cdm - 0.07324814 ...` |
| mse30 | 4 | 28 | 0.06509 | 0.06767 | 0.08015 | 0.9199 | valid | `(1.1324794*H0*(n_s*(0.40010464 - omega_cdm) + omega_b - 0.21622339) +...` |
| mse40 | 0 | 39 | 0.01238 | 0.01282 | 0.01518 | 0.9848 | valid | `(n_s*(H0 - exp(2*omega_b))*(omega_b**2*(2*tau - 49.891968) + (omega_b...` |
| mse40 | 1 | 21 | 0.04629 | 0.04491 | 0.05319 | 0.9468 | valid | `7.2245064*log(H0*n_s**2*omega_b**2/(0.190415417128964*A_s*omega_b + 0...` |
| mse40 | 2 | 38 | 0.07206 | 0.0723 | 0.08563 | 0.9144 | valid | `-n_s*omega_b + (tau + 3.9161375)*(0.814081942964497*H0*omega_b + n_s*...` |
| mse40 | 3 | 38 | 0.01528 | 0.01525 | 0.01806 | 0.9819 | valid | `(-0.794255562529119*H0*n_s**2*omega_b*(0.38122582*log(A_s) + 6.625871...` |
| mse40 | 4 | 38 | 0.01558 | 0.01554 | 0.0184 | 0.9816 | valid | `-n_s*omega_b - (-n_s**2/omega_cdm + 16.3510350180551*omega_b + 3.3042...` |
| h(f1) | fixed | 1e+01 | n/a | 0.0803 | 0.0951 | 0.9049 | fixed baseline | `h(H0**2*n_s**2*omega_b/(A_s*omega_cdm**2))` |
| h(f1)+g(f2), additive | fixed | 2e+01 | n/a | 0.01593 | 0.01887 | 0.9811 | fixed baseline | `h(H0**2*n_s**2*omega_b/(A_s*omega_cdm**2)) + g(n_s/log(-H0/(tau - 0.44653893)) + omega_b)` |
| h(f1)+g(f2), interaction-aware | fixed | 2e+01 | n/a | 0.01655 | 0.01961 | 0.9804 | fixed baseline | `h(H0**2*n_s**2*omega_b/(A_s*omega_cdm**2)) + g(omega_b*(tau - (n_s - omega_cdm)**4)/H0)` |

Canonical known `f2` audit source: additive residual hierarchy; expression `n_s/log(-H0/(tau - 0.44653893)) + omega_b`. The interaction-aware hierarchy remains the reconstruction denominator only.

### T0 one-standard-error readout

| method | metric | c_min | one-SE complexity | threshold | per-seed retained complexity |
|---|---|---:|---:|---:|---|
| mse20 | nmse_val | 20 | 18 | 0.0858 | s0:c18, s1:c17, s2:c18, s3:c18, s4:c18 |
| mse30 | nmse_val | 30 | 22 | 0.06225 | s0:c22, s1:c21, s2:c22, s3:c22, s4:c21 |
| mse40 | nmse_val | 39 | 21 | 0.05141 | s0:c20, s1:c21, s2:c20, s3:c21, s4:c21 |

One-SE equations are secondary confirmations and do not carry success decisions.

| method | seed | complexity | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---|---|
| mse20 | 0 | 18 | 0.08166 | 0.09671 | 0.9033 | valid | `0.10864077*H0*n_s**2 + 225.55743*omega_b - 72.77819*omega_cdm - tau -...` |
| mse20 | 1 | 17 | 0.07634 | 0.09042 | 0.9096 | valid | `n_s**2/omega_cdm + (H0*omega_b - tau)**2 - 8.299721 - 147.20245/H0` |
| mse20 | 2 | 18 | 0.06378 | 0.07555 | 0.9245 | valid | `230.8454*omega_b - log(A_s) - 17.257551 - 4447.7144*omega_cdm/(H0*n_s...` |
| mse20 | 3 | 18 | 0.07435 | 0.08805 | 0.9119 | valid | `(-14.562310495689*omega_cdm + 1.3920133*(n_s - tau**2)*(omega_b + 0.0...` |
| mse20 | 4 | 18 | 0.06204 | 0.07348 | 0.9265 | valid | `1.10475313407417*H0*(n_s*(2*omega_b + 0.16421144) - omega_cdm) - 1.10...` |
| mse30 | 0 | 22 | 0.03406 | 0.04034 | 0.9597 | valid | `(n_s*(H0*(2*omega_b - omega_cdm + 0.16523416) - 1.95359523647841*tau ...` |
| mse30 | 1 | 21 | 0.02553 | 0.03024 | 0.9698 | valid | `0.09450007*H0 + 238.50577*omega_b - 3.0546868*log(A_s) - 64.69098 - 6...` |
| mse30 | 2 | 22 | 0.04424 | 0.05239 | 0.9476 | valid | `0.101526263611352*H0*n_s - 3.22926489014041*log(A_s) - 64.03516346538...` |
| mse30 | 3 | 22 | 0.07857 | 0.09305 | 0.9069 | valid | `(H0*n_s**2*(omega_b + 0.08272548)**2 + 11.6591711798347*omega_b*(n_s ...` |
| mse30 | 4 | 21 | 0.0732 | 0.0867 | 0.9133 | valid | `-3.74246412745216*tau + 4.78926285581828*log(omega_b*exp(0.21654016*H...` |
| mse40 | 0 | 20 | 0.03015 | 0.03571 | 0.9643 | valid | `(H0*omega_b*(n_s*((omega_cdm - 3.4480197)*log(A_s) - 49.87621) - 10.0...` |
| mse40 | 1 | 21 | 0.04491 | 0.05319 | 0.9468 | valid | `7.2245064*log(H0*n_s**2*omega_b**2/(0.190415417128964*A_s*omega_b + 0...` |
| mse40 | 2 | 20 | 0.07708 | 0.0913 | 0.9087 | valid | `4.21400259611541*H0*n_s**2*omega_b + 3.5835445*n_s - 73.0419427778161...` |
| mse40 | 3 | 21 | 0.02496 | 0.02956 | 0.9704 | valid | `-0.39193708*n_s**2*log(A_s)/omega_cdm - 6.8224497*n_s**2/omega_cdm - ...` |
| mse40 | 4 | 21 | 0.01803 | 0.02136 | 0.9786 | valid | `n_s/omega_cdm - 3.3043263*tau/n_s - 4.744928/n_s - 9.5332985/(H0*n_s*...` |

### T0 common-complexity front comparison

| cut | method | metric | mean validation error | SE |
|---:|---|---|---:|---:|
| 1 | mse20 | nmse_val | 0.9998 | 6.344e-05 |
| 1 | mse30 | nmse_val | 0.9998 | 7.776e-05 |
| 1 | mse40 | nmse_val | 0.9998 | 6.344e-05 |
| 2 | mse20 | nmse_val | 0.9783 | 0 |
| 2 | mse30 | nmse_val | 0.9783 | 0 |
| 2 | mse40 | nmse_val | 0.9783 | 0 |
| 3 | mse20 | nmse_val | 0.9604 | 0 |
| 3 | mse30 | nmse_val | 0.9604 | 0 |
| 3 | mse40 | nmse_val | 0.9604 | 0 |
| 4 | mse20 | nmse_val | 0.9096 | 7.639e-05 |
| 4 | mse30 | nmse_val | 0.9095 | 1.607e-06 |
| 4 | mse40 | nmse_val | 0.923 | 0.003374 |
| 5 | mse20 | nmse_val | 0.5086 | 0.03075 |
| 5 | mse30 | nmse_val | 0.5609 | 0.02575 |
| 5 | mse40 | nmse_val | 0.5377 | 0.0323 |
| 6 | mse20 | nmse_val | 0.4863 | 0.03985 |
| 6 | mse30 | nmse_val | 0.5534 | 0.03317 |
| 6 | mse40 | nmse_val | 0.5377 | 0.0323 |
| 7 | mse20 | nmse_val | 0.3035 | 0.03229 |
| 7 | mse30 | nmse_val | 0.3738 | 0.01931 |
| 7 | mse40 | nmse_val | 0.3423 | 0.03213 |
| 8 | mse20 | nmse_val | 0.2934 | 0.03755 |
| 8 | mse30 | nmse_val | 0.3667 | 0.01232 |
| 8 | mse40 | nmse_val | 0.3336 | 0.04014 |
| 9 | mse20 | nmse_val | 0.2067 | 0.01029 |
| 9 | mse30 | nmse_val | 0.2299 | 0.02226 |
| 9 | mse40 | nmse_val | 0.2295 | 0.02169 |
| 10 | mse20 | nmse_val | 0.1741 | 0.001677 |
| 10 | mse30 | nmse_val | 0.2019 | 0.02677 |
| 10 | mse40 | nmse_val | 0.1777 | 0.01284 |
| 11 | mse20 | nmse_val | 0.1642 | 0.007456 |
| 11 | mse30 | nmse_val | 0.174 | 0.003752 |
| 11 | mse40 | nmse_val | 0.1648 | 0.007864 |
| 12 | mse20 | nmse_val | 0.1323 | 0.001893 |
| 12 | mse30 | nmse_val | 0.1352 | 0.008417 |
| 12 | mse40 | nmse_val | 0.1359 | 0.01287 |
| 13 | mse20 | nmse_val | 0.1236 | 0.005212 |
| 13 | mse30 | nmse_val | 0.1276 | 0.001262 |
| 13 | mse40 | nmse_val | 0.123 | 0.01086 |
| 14 | mse20 | nmse_val | 0.109 | 0.001566 |
| 14 | mse30 | nmse_val | 0.1154 | 0.00519 |
| 14 | mse40 | nmse_val | 0.1099 | 0.006855 |
| 15 | mse20 | nmse_val | 0.1037 | 0.00195 |
| 15 | mse30 | nmse_val | 0.1139 | 0.004105 |
| 15 | mse40 | nmse_val | 0.1003 | 0.007714 |
| 16 | mse20 | nmse_val | 0.09984 | 0.002641 |
| 16 | mse30 | nmse_val | 0.09904 | 0.004097 |
| 16 | mse40 | nmse_val | 0.09059 | 0.01492 |
| 17 | mse20 | nmse_val | 0.08673 | 0.004426 |
| 17 | mse30 | nmse_val | 0.09388 | 0.00283 |
| 17 | mse40 | nmse_val | 0.0797 | 0.01529 |
| 18 | mse20 | nmse_val | 0.08388 | 0.004731 |
| 18 | mse30 | nmse_val | 0.08856 | 0.00422 |
| 18 | mse40 | nmse_val | 0.06675 | 0.0137 |
| 19 | mse20 | nmse_val | 0.08281 | 0.004607 |
| 19 | mse30 | nmse_val | 0.08623 | 0.004147 |
| 19 | mse40 | nmse_val | 0.06201 | 0.01469 |
| 20 | mse20 | nmse_val | 0.07848 | 0.007316 |
| 20 | mse30 | nmse_val | 0.0763 | 0.009315 |
| 20 | mse40 | nmse_val | 0.05379 | 0.01457 |

## z2

| method | seed | symbolic core | T0 val MSE | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---:|---|---|
| mi20-mi | 0 | 19 | 1911 | 1913 | 1942 | -1941 | valid | `log((tau + 0.44084883)**2*(H0*omega_cdm/n_s + 0.8925628)/(A_s**2*(ome...` |
| mi20-mi | 1 | 20 | 314.6 | 315.4 | 320.1 | -319.1 | valid | `log((0.5243555 - exp(tau))*(omega_b - 0.11740347)*log((H0*omega_cdm +...` |
| mi20-mi | 2 | 20 | 1930 | 1933 | 1961 | -1960 | valid | `log((H0*omega_cdm + 0.72941446)*exp(-n_s + 4*tau)*log(omega_b)**2/A_s...` |
| mi20-mi | 3 | 19 | 116 | 115.6 | 117.3 | -116.3 | valid | `omega_b - log((0.095370451258642*tau + 1)**2*log(A_s/log((H0*omega_cd...` |
| mi20-mi | 4 | 19 | 533.6 | 534.6 | 542.5 | -541.5 | valid | `tau + log((tau + 0.9386916)*log(H0*omega_cdm/n_s)/(A_s*(omega_b + 0.0...` |
| mi20-mse | 0 | 3 | 1.008 | 0.9854 | 1 | -6.834e-06 | valid | `0.00069618196 - A_s` |
| mi20-mse | 1 | 1 | 1.008 | 0.9854 | 1 | -3.671e-06 | valid | `A_s` |
| mi20-mse | 2 | 10 | 1.008 | 0.9854 | 1 | -3.671e-06 | valid | `A_s/((tau + 0.42595297)*log(H0*omega_cdm))` |
| mi20-mse | 3 | 3 | 1.008 | 0.9854 | 1 | -7.376e-06 | valid | `A_s + 0.00079753407` |
| mi20-mse | 4 | 1 | 1.008 | 0.9854 | 1 | -3.671e-06 | valid | `A_s` |
| mse20 | 0 | 20 | 0.4722 | 0.4676 | 0.4745 | 0.5255 | valid | `17.08514*n_s*omega_b/omega_cdm - 17.08514*omega_b + tau**2 - 17.08514...` |
| mse20 | 1 | 20 | 0.1104 | 0.1082 | 0.1099 | 0.8901 | valid | `-2*omega_cdm + tau + 8.996951 - 3.7835147e-8*tau/A_s - 1.1077998e-8/A...` |
| mse20 | 2 | 20 | 0.01397 | 0.01387 | 0.01408 | 0.9859 | valid | `(n_s*(8.509195*log(A_s) + 175.07002) - 0.17109773*(H0 + 24.323713)*(n...` |
| mse20 | 3 | 20 | 0.1914 | 0.1822 | 0.1849 | 0.8151 | valid | `-1.1513755*omega_cdm - 16.746387*tau + 8.357865*log(A_s) + 168.33783623` |
| mse20 | 4 | 20 | 0.05439 | 0.05267 | 0.05345 | 0.9466 | valid | `-0.90866697*log(tau) + 0.0324404576133494 + 353.522000473541/H0 - 6.6...` |
| mse30 | 0 | 29 | 0.001653 | 0.00168 | 0.001705 | 0.9983 | valid | `(omega_cdm + 0.375861315)**2*(-0.220376016*H0*omega_b*omega_cdm + 8.7...` |
| mse30 | 1 | 27 | 0.04751 | 0.04899 | 0.04972 | 0.9503 | valid | `-omega_cdm - 12.4894978131747*omega_cdm/(omega_b + 0.524976) + 12.489...` |
| mse30 | 2 | 30 | 0.0236 | 0.02193 | 0.02225 | 0.9777 | valid | `(3.025129188*A_s*n_s**2 + 5.393399*A_s*(n_s**2*(n_s - omega_cdm) + om...` |
| mse30 | 3 | 30 | 0.2184 | 0.2153 | 0.2185 | 0.7815 | valid | `-1.1608334*(n_s - tau)*(A_s*n_s*tau - 1.1608334*A_s*n_s*(2*omega_cdm*...` |
| mse30 | 4 | 21 | 0.4707 | 0.4654 | 0.4723 | 0.5277 | valid | `-34.93179*(tau - 0.54168844)/(log(H0*omega_cdm) + 0.034986433) - 0.05...` |
| mse40 | 0 | 37 | 0.01276 | 0.01178 | 0.01195 | 0.988 | valid | `(-0.0579337991333041*A_s*H0*omega_cdm + 1.39417319255902*n_s*(6.81003...` |
| mse40 | 1 | 39 | 0.04205 | 0.04231 | 0.04294 | 0.9571 | valid | `(-A_s*omega_cdm*(1.3860478*n_s + exp(tau)) - (A_s*n_s*(log((omega_cdm...` |
| mse40 | 2 | 12 | 0.2903 | 0.2911 | 0.2955 | 0.7045 | valid | `(0.40627283*A_s - 4.0068514e-8*omega_cdm*(omega_cdm + tau))/(A_s*omeg...` |
| mse40 | 3 | 29 | 0.002033 | 0.00207 | 0.002101 | 0.9979 | valid | `(H0*n_s*(tau*(omega_b - omega_cdm) - 0.29783544) + H0*(omega_b - omeg...` |
| mse40 | 4 | 39 | 0.0009128 | 0.0009361 | 0.0009499 | 0.9991 | valid | `(H0*(2*tau + (n_s + 18.793062*omega_b)*(tau + 4.351114) + 963.5995116...` |
| h(f1) | fixed | 8 | n/a | 0.05183 | 0.0526 | 0.9474 | fixed baseline | `h(A_s/log(H0*(omega_cdm + tau)))` |
| h(f1)+g(f2), additive | fixed | 2e+01 | n/a | 0.007243 | 0.00735 | 0.9926 | fixed baseline | `h(A_s/log(H0*(omega_cdm + tau))) + g(n_s**2*omega_b*tau/(omega_cdm*tau + 0.00031008976))` |
| h(f1)+g(f2), interaction-aware | fixed | 2e+01 | n/a | 0.007313 | 0.007422 | 0.9926 | fixed baseline | `h(A_s/log(H0*(omega_cdm + tau))) + g(n_s**2*omega_b*tau/(omega_cdm*tau + 0.0003273979))` |

Canonical known `f2` audit source: additive residual hierarchy; expression `n_s**2*omega_b*tau/(omega_cdm*tau + 0.00031008976)`. The interaction-aware hierarchy remains the reconstruction denominator only.

### T0 one-standard-error readout

| method | metric | c_min | one-SE complexity | threshold | per-seed retained complexity |
|---|---|---:|---:|---:|---|
| mse20 | nmse_val | 20 | 11 | 0.2482 | s0:c11, s1:c11, s2:c10, s3:c10, s4:c11 |
| mse30 | nmse_val | 30 | 12 | 0.239 | s0:c12, s1:c12, s2:c11, s3:c11, s4:c11 |
| mse40 | nmse_val | 39 | 18 | 0.1244 | s0:c17, s1:c18, s2:c12, s3:c17, s4:c16 |

One-SE equations are secondary confirmations and do not carry success decisions.

| method | seed | complexity | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---|---|
| mse20 | 0 | 11 | 0.4918 | 0.4991 | 0.5009 | valid | `-3.278335 - 1.8635898*tau/omega_cdm + 35.72718/(H0*omega_cdm)` |
| mse20 | 1 | 11 | 0.1284 | 0.1303 | 0.8697 | valid | `(8.600947*A_s - 3.7828805e-8*omega_cdm - 3.7828805e-8*tau - 1.0915615...` |
| mse20 | 2 | 10 | 0.131 | 0.1329 | 0.8671 | valid | `(omega_cdm + tau + 8.273824)*log(A_s) + 169.05579` |
| mse20 | 3 | 10 | 0.1876 | 0.1904 | 0.8096 | valid | `-16.74989*tau + 8.4642725*log(A_s) + 170.3342` |
| mse20 | 4 | 11 | 0.15 | 0.1522 | 0.8478 | valid | `4.1710253 + 0.529943/(omega_cdm + tau) - 1.492475e-8/A_s` |
| mse30 | 0 | 12 | 0.1104 | 0.112 | 0.888 | valid | `(-3.7717893*omega_cdm - 1.918071*tau + log(A_s) + 20.551517)/omega_cdm` |
| mse30 | 1 | 12 | 0.1612 | 0.1636 | 0.8364 | valid | `4466441961.62788*A_s - 14.8634800504972*tau - 7.43174002524859*exp(om...` |
| mse30 | 2 | 11 | 0.128 | 0.1299 | 0.8701 | valid | `(8.512266*A_s - 3.697159e-8*omega_cdm - 3.697159e-8*tau - 1.089755583...` |
| mse30 | 3 | 11 | 0.2461 | 0.2498 | 0.7502 | valid | `(1.187372*A_s + H0*tau*(A_s - 2.5796034e-9))/A_s` |
| mse30 | 4 | 11 | 0.4854 | 0.4926 | 0.5074 | valid | `-0.47441462*H0*omega_cdm - 16.519215*tau + 5.034941` |
| mse40 | 0 | 17 | 0.1034 | 0.1049 | 0.8951 | valid | `5.395268*n_s + 1.2070274788026*tau/omega_cdm + 0.29039632707016/omega...` |
| mse40 | 1 | 18 | 0.07846 | 0.07963 | 0.9204 | valid | `0.825472564470026*(-A_s*log((H0*omega_cdm - 5.791741)/H0) + (38.94304...` |
| mse40 | 2 | 12 | 0.2911 | 0.2955 | 0.7045 | valid | `(0.40627283*A_s - 4.0068514e-8*omega_cdm*(omega_cdm + tau))/(A_s*omeg...` |
| mse40 | 3 | 17 | 0.02378 | 0.02413 | 0.9759 | valid | `4035209500.0*A_s - 16.688637*tau - 15.0161295 + 0.43158054/omega_cdm ...` |
| mse40 | 4 | 16 | 0.1099 | 0.1115 | 0.8885 | valid | `-0.24582634861374*H0*tau - 8.724445*omega_cdm + 8.724445*log(A_s) + 1...` |

### T0 common-complexity front comparison

| cut | method | metric | mean validation error | SE |
|---:|---|---|---:|---:|
| 1 | mse20 | nmse_val | 1 | 1.479e-06 |
| 1 | mse30 | nmse_val | 1 | 6.39e-07 |
| 1 | mse40 | nmse_val | 1 | 4.887e-07 |
| 2 | mse20 | nmse_val | 0.9696 | 5.551e-17 |
| 2 | mse30 | nmse_val | 0.9696 | 5.551e-17 |
| 2 | mse40 | nmse_val | 0.9696 | 5.551e-17 |
| 3 | mse20 | nmse_val | 0.9049 | 3.462e-06 |
| 3 | mse30 | nmse_val | 0.9049 | 1.765e-06 |
| 3 | mse40 | nmse_val | 0.9127 | 0.007726 |
| 4 | mse20 | nmse_val | 0.7292 | 0.039 |
| 4 | mse30 | nmse_val | 0.8072 | 0.04777 |
| 4 | mse40 | nmse_val | 0.7776 | 0.04477 |
| 5 | mse20 | nmse_val | 0.6378 | 0.0267 |
| 5 | mse30 | nmse_val | 0.6645 | 2.069e-07 |
| 5 | mse40 | nmse_val | 0.6108 | 0.03288 |
| 6 | mse20 | nmse_val | 0.5839 | 0.03292 |
| 6 | mse30 | nmse_val | 0.6375 | 0.02697 |
| 6 | mse40 | nmse_val | 0.5838 | 0.03293 |
| 7 | mse20 | nmse_val | 0.5338 | 0.02199 |
| 7 | mse30 | nmse_val | 0.55 | 0.0182 |
| 7 | mse40 | nmse_val | 0.5334 | 0.02268 |
| 8 | mse20 | nmse_val | 0.4189 | 0.07769 |
| 8 | mse30 | nmse_val | 0.4462 | 0.06881 |
| 8 | mse40 | nmse_val | 0.4649 | 0.0501 |
| 9 | mse20 | nmse_val | 0.3541 | 0.07769 |
| 9 | mse30 | nmse_val | 0.3511 | 0.06718 |
| 9 | mse40 | nmse_val | 0.3314 | 0.0572 |
| 10 | mse20 | nmse_val | 0.2485 | 0.07976 |
| 10 | mse30 | nmse_val | 0.3097 | 0.07394 |
| 10 | mse40 | nmse_val | 0.2459 | 0.05963 |
| 11 | mse20 | nmse_val | 0.2213 | 0.07146 |
| 11 | mse30 | nmse_val | 0.2508 | 0.06588 |
| 11 | mse40 | nmse_val | 0.2459 | 0.05963 |
| 12 | mse20 | nmse_val | 0.2184 | 0.0723 |
| 12 | mse30 | nmse_val | 0.232 | 0.07206 |
| 12 | mse40 | nmse_val | 0.1938 | 0.02614 |
| 13 | mse20 | nmse_val | 0.2079 | 0.07048 |
| 13 | mse30 | nmse_val | 0.2234 | 0.07258 |
| 13 | mse40 | nmse_val | 0.1755 | 0.03184 |
| 14 | mse20 | nmse_val | 0.1814 | 0.07946 |
| 14 | mse30 | nmse_val | 0.2168 | 0.07431 |
| 14 | mse40 | nmse_val | 0.1638 | 0.03469 |
| 15 | mse20 | nmse_val | 0.1787 | 0.07696 |
| 15 | mse30 | nmse_val | 0.1992 | 0.07849 |
| 15 | mse40 | nmse_val | 0.1461 | 0.03592 |
| 16 | mse20 | nmse_val | 0.1724 | 0.07937 |
| 16 | mse30 | nmse_val | 0.18 | 0.08601 |
| 16 | mse40 | nmse_val | 0.1461 | 0.03592 |
| 17 | mse20 | nmse_val | 0.1721 | 0.07911 |
| 17 | mse30 | nmse_val | 0.174 | 0.08732 |
| 17 | mse40 | nmse_val | 0.1302 | 0.04331 |
| 18 | mse20 | nmse_val | 0.1691 | 0.0803 |
| 18 | mse30 | nmse_val | 0.1736 | 0.08752 |
| 18 | mse40 | nmse_val | 0.1203 | 0.04482 |
| 19 | mse20 | nmse_val | 0.1691 | 0.08032 |
| 19 | mse30 | nmse_val | 0.1682 | 0.08856 |
| 19 | mse40 | nmse_val | 0.1043 | 0.04918 |
| 20 | mse20 | nmse_val | 0.1673 | 0.08097 |
| 20 | mse30 | nmse_val | 0.1666 | 0.08921 |
| 20 | mse40 | nmse_val | 0.08568 | 0.05121 |

## z3

| method | seed | symbolic core | T0 val MSE | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---:|---|---|
| mi20-mi | 0 | 19 | 0.99 | 1.022 | 1.047 | -0.04717 | valid | `omega_b - exp((H0*(-1.02594449476132*n_s - 2*omega_cdm + tau**3) - 2....` |
| mi20-mi | 1 | 20 | 12.71 | 12.38 | 12.69 | -11.69 | valid | `log(n_s**2*(omega_b + 0.11972135)*(omega_cdm + 0.11387834 + (1.468140...` |
| mi20-mi | 2 | 20 | 0.8562 | 0.9145 | 0.9372 | 0.06279 | valid | `log(n_s + log(2*omega_cdm + exp(3.2191007*omega_b - (tau - 2.6334786)...` |
| mi20-mi | 3 | 18 | 0.8616 | 0.9341 | 0.9573 | 0.04274 | valid | `log(n_s - 2.6130590290296*omega_b/(18.7285698339675*omega_b - omega_c...` |
| mi20-mi | 4 | 20 | 6.668 | 6.457 | 6.618 | -5.618 | valid | `n_s + log(n_s*(omega_b + 0.122276284)*(H0*(omega_cdm + 0.11773269) - ...` |
| mi20-mse | 0 | 2 | 0.8764 | 0.9334 | 0.9565 | 0.04347 | valid | `log(n_s)` |
| mi20-mse | 1 | 2 | 0.8764 | 0.9334 | 0.9565 | 0.04347 | valid | `log(n_s)` |
| mi20-mse | 2 | 20 | 0.8562 | 0.9145 | 0.9372 | 0.06279 | valid | `log(n_s + log(2*omega_cdm + exp(3.2191007*omega_b - (tau - 2.6334786)...` |
| mi20-mse | 3 | 18 | 0.8616 | 0.9341 | 0.9573 | 0.04274 | valid | `log(n_s - 2.6130590290296*omega_b/(18.7285698339675*omega_b - omega_c...` |
| mi20-mse | 4 | 2 | 0.8764 | 0.9334 | 0.9565 | 0.04347 | valid | `log(n_s)` |
| mse20 | 0 | 19 | 0.002835 | 0.002916 | 0.002988 | 0.997 | valid | `-0.018443113*H0 - n_s*(tau - 25.242214*exp(2*omega_cdm)) + 109.6465*o...` |
| mse20 | 1 | 20 | 0.002976 | 0.002959 | 0.003033 | 0.997 | valid | `31.8354113579254*n_s + 92.7338683579254*omega_b + 60.898457*omega_cdm...` |
| mse20 | 2 | 19 | 0.006895 | 0.006328 | 0.006485 | 0.9935 | valid | `(n_s*(-n_s*(0.019183831*H0 - 12.799086) + 63.230583*omega_b + 62.2305...` |
| mse20 | 3 | 19 | 0.002009 | 0.002089 | 0.002141 | 0.9979 | valid | `(-0.00040654212*H0 + omega_b*(-n_s*(tau - 31.799374) + 61.12067*omega...` |
| mse20 | 4 | 20 | 0.002703 | 0.002713 | 0.002781 | 0.9972 | valid | `-n_s*(0.019217668*H0 + 0.019217668*tau - 33.182472) + 61.543453*omega...` |
| mse30 | 0 | 26 | 0.002609 | 0.002686 | 0.002752 | 0.9972 | valid | `(28.0988947133257*n_s**2*(omega_b + omega_cdm + 0.121937395892955)**2...` |
| mse30 | 1 | 29 | 0.002593 | 0.002494 | 0.002556 | 0.9974 | valid | `n_s*(-0.75683698*tau + 1.5796308497482*(log((0.312011604335588*n_s + ...` |
| mse30 | 2 | 29 | 0.002058 | 0.00215 | 0.002203 | 0.9978 | valid | `(H0*(-tau**2*log(n_s*omega_cdm)**2 + 3.4988878*log(omega_cdm**2) - 2....` |
| mse30 | 3 | 30 | 0.002436 | 0.002551 | 0.002614 | 0.9974 | valid | `(-29.526375*H0 + n_s*(H0 + tau**2)*(2*omega_b + 957.70917*omega_cdm*(...` |
| mse30 | 4 | 29 | 0.001954 | 0.002063 | 0.002115 | 0.9979 | valid | `-30.60156*omega_b**2 + 61.20312*omega_cdm - tau**2*log(omega_cdm)**2 ...` |
| mse40 | 0 | 37 | 0.00211 | 0.002173 | 0.002227 | 0.9978 | valid | `(n_s + 0.011812089*omega_cdm)*(H0*omega_b*omega_cdm*(4.4714913 - 3.41...` |
| mse40 | 1 | 26 | 0.001972 | 0.002029 | 0.00208 | 0.9979 | valid | `31.774082*n_s + 61.427013*omega_cdm - 36.5154592998264 - 0.0549261897...` |
| mse40 | 2 | 38 | 0.002382 | 0.002435 | 0.002496 | 0.9975 | valid | `-5.46425439142318*omega_cdm - 0.724104205256895*tau - 3.8262739564598...` |
| mse40 | 3 | 22 | 0.003839 | 0.00378 | 0.003874 | 0.9961 | valid | `-0.0187756448561935*H0 + n_s*(omega_b + 31.98304) + 112.28677*omega_b...` |
| mse40 | 4 | 37 | 0.002475 | 0.002592 | 0.002657 | 0.9973 | valid | `-(omega_cdm + 4.8607607)*(omega_b + tau**2 - 6.17498130987532*log(n_s...` |
| h(f1) | fixed | 3 | n/a | 0.08215 | 0.08419 | 0.9158 | fixed baseline | `h(n_s + omega_cdm)` |
| h(f1)+g(f2), additive | fixed | 1e+01 | n/a | 0.01132 | 0.0116 | 0.9884 | fixed baseline | `h(n_s + omega_cdm) + g(H0/(omega_b**2*omega_cdm**2))` |
| h(f1)+g(f2), interaction-aware | fixed | 1e+01 | n/a | 0.01139 | 0.01168 | 0.9883 | fixed baseline | `h(n_s + omega_cdm) + g((H0 + 89.375175)/(omega_b*omega_cdm))` |

Canonical known `f2` audit source: additive residual hierarchy; expression `H0/(omega_b**2*omega_cdm**2)`. The interaction-aware hierarchy remains the reconstruction denominator only.

### T0 one-standard-error readout

| method | metric | c_min | one-SE complexity | threshold | per-seed retained complexity |
|---|---|---:|---:|---:|---|
| mse20 | nmse_val | 20 | 18 | 0.004787 | s0:c17, s1:c18, s2:c17, s3:c18, s4:c18 |
| mse30 | nmse_val | 30 | 23 | 0.002713 | s0:c23, s1:c23, s2:c23, s3:c23, s4:c23 |
| mse40 | nmse_val | 38 | 29 | 0.003177 | s0:c29, s1:c26, s2:c29, s3:c22, s4:c26 |

One-SE equations are secondary confirmations and do not carry success decisions.

| method | seed | complexity | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---|---|
| mse20 | 0 | 17 | 0.003268 | 0.003349 | 0.9967 | valid | `-0.018599834*H0 + 25.21363*n_s*exp(2*omega_cdm) + 109.69107*omega_b -...` |
| mse20 | 1 | 18 | 0.003277 | 0.003359 | 0.9966 | valid | `31.8060218969198*n_s + 93.4375488969198*omega_b + 61.631527*omega_cdm...` |
| mse20 | 2 | 17 | 0.006459 | 0.006619 | 0.9934 | valid | `(n_s*(-n_s*(0.019192379*H0 - 12.815793) + 62.22466*omega_b + 62.22466...` |
| mse20 | 3 | 18 | 0.002458 | 0.002519 | 0.9975 | valid | `-0.018506166*H0 + 31.759764*n_s + 61.125614*omega_cdm - 35.11835 - 0....` |
| mse20 | 4 | 18 | 0.002734 | 0.002802 | 0.9972 | valid | `-n_s*(0.019111466*H0 - 33.11919) + 61.432922*omega_cdm + 2.4828823*lo...` |
| mse30 | 0 | 23 | 0.002812 | 0.002882 | 0.9971 | valid | `(28.0019071129221*n_s**2*(omega_b + omega_cdm + 0.122525421928822)**2...` |
| mse30 | 1 | 23 | 0.003027 | 0.003102 | 0.9969 | valid | `-tau + 1.52273698329023*(log((0.312051971382088*n_s + omega_b + 0.596...` |
| mse30 | 2 | 23 | 0.002328 | 0.002385 | 0.9976 | valid | `(H0*(-tau + 3.5140877*log(omega_cdm**2) - 1.9728056) + 14.44692056332...` |
| mse30 | 3 | 23 | 0.002557 | 0.002621 | 0.9974 | valid | `957.70917*omega_b*omega_cdm + 40.1920926281464*omega_cdm - (tau + 0.4...` |
| mse30 | 4 | 23 | 0.002079 | 0.002131 | 0.9979 | valid | `(omega_b*(61.221058*omega_cdm - 0.76098853*tau + 30.610529*log(n_s) -...` |
| mse40 | 0 | 29 | 0.002606 | 0.002671 | 0.9973 | valid | `(H0*omega_b*omega_cdm*(5.3967156 - 0.60173255*tau) + (1.8849965*omega...` |
| mse40 | 1 | 26 | 0.002029 | 0.00208 | 0.9979 | valid | `31.774082*n_s + 61.427013*omega_cdm - 36.5154592998264 - 0.0549261897...` |
| mse40 | 2 | 29 | 0.003076 | 0.003152 | 0.9968 | valid | `-5.36751106740526*omega_cdm - 3.8480370036263*log((omega_b - 0.070723...` |
| mse40 | 3 | 22 | 0.00378 | 0.003874 | 0.9961 | valid | `-0.0187756448561935*H0 + n_s*(omega_b + 31.98304) + 112.28677*omega_b...` |
| mse40 | 4 | 26 | 0.002731 | 0.002799 | 0.9972 | valid | `(H0*(2*omega_b + omega_cdm)*(-omega_b - 0.66779876*tau + 30.652874*lo...` |

### T0 common-complexity front comparison

| cut | method | metric | mean validation error | SE |
|---:|---|---|---:|---:|
| 1 | mse20 | nmse_val | 1.003 | 7.988e-07 |
| 1 | mse30 | nmse_val | 1.003 | 1.688e-06 |
| 1 | mse40 | nmse_val | 1.003 | 3.677e-07 |
| 2 | mse20 | nmse_val | 0.9639 | 5.551e-17 |
| 2 | mse30 | nmse_val | 0.9639 | 5.551e-17 |
| 2 | mse40 | nmse_val | 0.9639 | 5.551e-17 |
| 3 | mse20 | nmse_val | 0.929 | 5.551e-17 |
| 3 | mse30 | nmse_val | 0.929 | 5.551e-17 |
| 3 | mse40 | nmse_val | 0.929 | 5.551e-17 |
| 4 | mse20 | nmse_val | 0.7775 | 0 |
| 4 | mse30 | nmse_val | 0.7775 | 0 |
| 4 | mse40 | nmse_val | 0.7775 | 0 |
| 5 | mse20 | nmse_val | 0.3364 | 3.535e-05 |
| 5 | mse30 | nmse_val | 0.3364 | 2.932e-05 |
| 5 | mse40 | nmse_val | 0.3364 | 2.94e-05 |
| 6 | mse20 | nmse_val | 0.3363 | 3.929e-05 |
| 6 | mse30 | nmse_val | 0.3363 | 3.423e-05 |
| 6 | mse40 | nmse_val | 0.3363 | 3.423e-05 |
| 7 | mse20 | nmse_val | 0.1422 | 0.04598 |
| 7 | mse30 | nmse_val | 0.2339 | 0.05618 |
| 7 | mse40 | nmse_val | 0.1882 | 0.05632 |
| 8 | mse20 | nmse_val | 0.09622 | 1.989e-05 |
| 8 | mse30 | nmse_val | 0.1579 | 0.02967 |
| 8 | mse40 | nmse_val | 0.1738 | 0.04882 |
| 9 | mse20 | nmse_val | 0.0325 | 0.0001355 |
| 9 | mse30 | nmse_val | 0.0326 | 0.0001022 |
| 9 | mse40 | nmse_val | 0.06347 | 0.03031 |
| 10 | mse20 | nmse_val | 0.03235 | 9.949e-05 |
| 10 | mse30 | nmse_val | 0.03237 | 8.752e-05 |
| 10 | mse40 | nmse_val | 0.03273 | 0.0003994 |
| 11 | mse20 | nmse_val | 0.01731 | 5.093e-05 |
| 11 | mse30 | nmse_val | 0.02481 | 0.002389 |
| 11 | mse40 | nmse_val | 0.02718 | 0.002981 |
| 12 | mse20 | nmse_val | 0.01731 | 5.093e-05 |
| 12 | mse30 | nmse_val | 0.02202 | 0.001312 |
| 12 | mse40 | nmse_val | 0.02433 | 0.002791 |
| 13 | mse20 | nmse_val | 0.01319 | 0.0001514 |
| 13 | mse30 | nmse_val | 0.01715 | 0.00248 |
| 13 | mse40 | nmse_val | 0.02016 | 0.00266 |
| 14 | mse20 | nmse_val | 0.01314 | 0.000159 |
| 14 | mse30 | nmse_val | 0.01421 | 0.001219 |
| 14 | mse40 | nmse_val | 0.01704 | 0.002287 |
| 15 | mse20 | nmse_val | 0.008442 | 0.001186 |
| 15 | mse30 | nmse_val | 0.01388 | 0.001303 |
| 15 | mse40 | nmse_val | 0.01449 | 0.0008231 |
| 16 | mse20 | nmse_val | 0.008442 | 0.001186 |
| 16 | mse30 | nmse_val | 0.011 | 0.001795 |
| 16 | mse40 | nmse_val | 0.01348 | 0.0007581 |
| 17 | mse20 | nmse_val | 0.005533 | 0.0009454 |
| 17 | mse30 | nmse_val | 0.00707 | 0.002122 |
| 17 | mse40 | nmse_val | 0.01312 | 0.000576 |
| 18 | mse20 | nmse_val | 0.004206 | 0.0009096 |
| 18 | mse30 | nmse_val | 0.006115 | 0.001736 |
| 18 | mse40 | nmse_val | 0.0113 | 0.001985 |
| 19 | mse20 | nmse_val | 0.00395 | 0.000944 |
| 19 | mse30 | nmse_val | 0.004779 | 0.001046 |
| 19 | mse40 | nmse_val | 0.009025 | 0.002208 |
| 20 | mse20 | nmse_val | 0.003831 | 0.0009555 |
| 20 | mse30 | nmse_val | 0.003933 | 0.0007422 |
| 20 | mse40 | nmse_val | 0.005571 | 0.001888 |

## z4

| method | seed | symbolic core | T0 val MSE | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---:|---|---|
| mi20-mi | 0 | 20 | 132.7 | 132.3 | 133.2 | -132.2 | valid | `(-n_s - (log(log(H0)) + 0.39339703)*exp(tau) + log(A_s) + log((-0.440...` |
| mi20-mi | 1 | 20 | 35.12 | 35.27 | 35.51 | -34.51 | valid | `n_s - omega_cdm - log(A_s*H0*omega_cdm*(0.0432008270366328*H0 + 1)**2...` |
| mi20-mi | 2 | 20 | 49.07 | 49.25 | 49.58 | -48.58 | valid | `n_s - omega_cdm + log(omega_b*(tau + 0.43412754)/(A_s*H0**2*omega_cdm...` |
| mi20-mi | 3 | 20 | 119.9 | 120.2 | 121 | -120 | valid | `n_s - log(A_s*omega_cdm*(0.0726314836854435*H0 - 1)**2*(0.93119276947...` |
| mi20-mi | 4 | 20 | 61.1 | 61.31 | 61.72 | -60.72 | valid | `-omega_cdm + log(omega_b*exp(n_s + 2*tau)/(A_s*H0**2*omega_cdm*log(H0...` |
| mi20-mse | 0 | 14 | 1.006 | 0.9934 | 1 | -3.166e-05 | valid | `-A_s*omega_cdm*(0.000126357771252783*H0**2 - tau)/(n_s*omega_b)` |
| mi20-mse | 1 | 7 | 1.006 | 0.9934 | 1 | -3.166e-05 | valid | `-A_s*omega_cdm*(H0 - 40.11763)` |
| mi20-mse | 2 | 7 | 1.006 | 0.9934 | 1 | -3.166e-05 | valid | `-A_s*omega_cdm*(H0 - 40.138134)` |
| mi20-mse | 3 | 9 | 1.006 | 0.9934 | 1 | -3.126e-05 | valid | `A_s*H0**2*(-omega_cdm + tau**2)` |
| mi20-mse | 4 | 7 | 1.006 | 0.9934 | 1 | -3.166e-05 | valid | `-A_s*omega_cdm*(H0 - 40.07763)` |
| mse20 | 0 | 20 | 0.0804 | 0.07695 | 0.07747 | 0.9225 | valid | `-1.0523636 + tau/omega_cdm - 0.014016496/(omega_b*omega_cdm) - log(A_...` |
| mse20 | 1 | 19 | 0.1156 | 0.1128 | 0.1136 | 0.8864 | valid | `-0.1521146*H0 + 0.482751905219907*n_s/omega_cdm + 10.6252533587986 + ...` |
| mse20 | 2 | 19 | 0.1181 | 0.1174 | 0.1182 | 0.8818 | valid | `189.394471611184*omega_b - 1.3348532*omega_cdm*(H0 - 40.72927) + 8.40...` |
| mse20 | 3 | 19 | 0.1166 | 0.1139 | 0.1147 | 0.8853 | valid | `8.372509*tau - 11.461645 + 0.5285362/omega_cdm - 0.09353723/(n_s*omeg...` |
| mse20 | 4 | 20 | 0.1155 | 0.1127 | 0.1134 | 0.8866 | valid | `-0.15219526*H0 + 2.1972709*n_s**2 + 23.9974*omega_b/omega_cdm + 8.385...` |
| mse30 | 0 | 30 | 0.001561 | 0.001574 | 0.001584 | 0.9984 | valid | `(A_s*omega_cdm*(n_s + (n_s + omega_cdm)*(n_s**2 + omega_b) - 0.250276...` |
| mse30 | 1 | 26 | 0.01387 | 0.0144 | 0.0145 | 0.9855 | valid | `-1.3006971*H0*omega_cdm*exp(-tau) - n_s*tau + 10.007565*n_s - 0.09877...` |
| mse30 | 2 | 30 | 0.02604 | 0.02501 | 0.02518 | 0.9748 | valid | `-A_s - 8.672121*H0*n_s*omega_b*(log(H0) - 4.6987495) - 8.672121*omega...` |
| mse30 | 3 | 30 | 0.004057 | 0.004023 | 0.00405 | 0.9959 | valid | `omega_cdm**2 - tau - 9.8783636861445 - 0.908729931206565*omega_cdm/om...` |
| mse30 | 4 | 30 | 0.0005005 | 0.000529 | 0.0005326 | 0.9995 | valid | `8.49345471848303*A_s - 0.152350817352476*H0 + 4.35105721988329*n_s - ...` |
| mse40 | 0 | 38 | 0.002678 | 0.002564 | 0.002581 | 0.9974 | valid | `-0.0942166610105264*H0 + n_s**2 - (omega_b + tau)**2 + 3.3386119 + ta...` |
| mse40 | 1 | 38 | 0.00805 | 0.007382 | 0.007431 | 0.9926 | valid | `1.8916922*(tau - 0.97797483)*(0.806602178278494*n_s + omega_cdm*(-121...` |
| mse40 | 2 | 40 | 0.00305 | 0.002965 | 0.002985 | 0.997 | valid | `-omega_b - omega_cdm + (n_s/omega_cdm - log(n_s))*(-0.011025735*H0 + ...` |
| mse40 | 3 | 38 | 0.0006462 | 0.0006216 | 0.0006258 | 0.9994 | valid | `4.30332076935801*n_s - 3*omega_cdm - 2*tau**2 + 8.79173634134096*tau ...` |
| mse40 | 4 | 38 | 0.005388 | 0.005275 | 0.005311 | 0.9947 | valid | `(A_s*omega_cdm*(H0 - 1.0456314)*(omega_cdm - 1.65389991043216*tau**2 ...` |
| h(f1) | fixed | 9 | n/a | 0.07866 | 0.07918 | 0.9208 | fixed baseline | `h(A_s*H0**2*omega_cdm*exp(-2*tau))` |
| h(f1)+g(f2), additive | fixed | 2e+01 | n/a | 0.007265 | 0.007313 | 0.9927 | fixed baseline | `h(A_s*H0**2*omega_cdm*exp(-2*tau)) + g(log(H0)/(n_s*omega_b))` |
| h(f1)+g(f2), interaction-aware | fixed | 2e+01 | n/a | 0.005313 | 0.005348 | 0.9947 | fixed baseline | `h(A_s*H0**2*omega_cdm*exp(-2*tau)) + g((n_s*tau + log(H0))/(n_s*omega_b))` |

Canonical known `f2` audit source: additive residual hierarchy; expression `log(H0)/(n_s*omega_b)`. The interaction-aware hierarchy remains the reconstruction denominator only.

### T0 one-standard-error readout

| method | metric | c_min | one-SE complexity | threshold | per-seed retained complexity |
|---|---|---:|---:|---:|---|
| mse20 | nmse_val | 20 | 16 | 0.1159 | s0:c16, s1:c15, s2:c15, s3:c15, s4:c15 |
| mse30 | nmse_val | 30 | 30 | 0.01396 | s0:c30, s1:c26, s2:c30, s3:c30, s4:c30 |
| mse40 | nmse_val | 40 | 27 | 0.005204 | s0:c27, s1:c27, s2:c27, s3:c26, s4:c27 |

One-SE equations are secondary confirmations and do not carry success decisions.

| method | seed | complexity | T2 MSE | T2 NMSE | T2 R² | decision domain | expression |
|---|---:|---:|---:|---:|---:|---|---|
| mse20 | 0 | 16 | 0.09004 | 0.09064 | 0.9094 | valid | `-log(A_s) - 25.139017 + tau/omega_cdm - 0.013890403/(omega_b*omega_cd...` |
| mse20 | 1 | 15 | 0.116 | 0.1167 | 0.8833 | valid | `0.4727699*n_s/omega_cdm + tau/omega_cdm - 0.33562234/omega_b + 16.591...` |
| mse20 | 2 | 15 | 0.1242 | 0.1251 | 0.8749 | valid | `(231.27841*omega_b*(0.7055078*n_s + tau) - omega_cdm*(H0 - 37.94883))...` |
| mse20 | 3 | 15 | 0.126 | 0.1268 | 0.8732 | valid | `-10.773924 + tau/omega_cdm + 0.45907027/omega_cdm - 0.09933187/omega_...` |
| mse20 | 4 | 15 | 0.1136 | 0.1143 | 0.8857 | valid | `(22.476374*n_s*omega_b + omega_cdm*(6.0423284 - 0.15234275*H0) + tau)...` |
| mse30 | 0 | 30 | 0.001574 | 0.001584 | 0.9984 | valid | `(A_s*omega_cdm*(n_s + (n_s + omega_cdm)*(n_s**2 + omega_b) - 0.250276...` |
| mse30 | 1 | 26 | 0.0144 | 0.0145 | 0.9855 | valid | `-1.3006971*H0*omega_cdm*exp(-tau) - n_s*tau + 10.007565*n_s - 0.09877...` |
| mse30 | 2 | 30 | 0.02501 | 0.02518 | 0.9748 | valid | `-A_s - 8.672121*H0*n_s*omega_b*(log(H0) - 4.6987495) - 8.672121*omega...` |
| mse30 | 3 | 30 | 0.004023 | 0.00405 | 0.9959 | valid | `omega_cdm**2 - tau - 9.8783636861445 - 0.908729931206565*omega_cdm/om...` |
| mse30 | 4 | 30 | 0.000529 | 0.0005326 | 0.9995 | valid | `8.49345471848303*A_s - 0.152350817352476*H0 + 4.35105721988329*n_s - ...` |
| mse40 | 0 | 27 | 0.004298 | 0.004327 | 0.9957 | valid | `-0.0880467394355359*H0 + n_s**2 + n_s + 3.830791 + tau/omega_cdm - 0....` |
| mse40 | 1 | 27 | 0.0107 | 0.01077 | 0.9892 | valid | `(-898190.537269494*A_s*omega_cdm*(0.0232562953047168*H0 + 1)**4 - 0.4...` |
| mse40 | 2 | 27 | 0.003118 | 0.003139 | 0.9969 | valid | `-0.011047057*H0*n_s/omega_cdm - n_s*omega_cdm + n_s*tau/omega_cdm + 1...` |
| mse40 | 3 | 26 | 0.001418 | 0.001428 | 0.9986 | valid | `4.32220013818074*n_s + 8.74231405418513*tau - 4.32220013818074*log(A_...` |
| mse40 | 4 | 27 | 0.005675 | 0.005713 | 0.9943 | valid | `22.5915507652302*omega_b/omega_cdm - 2.0760078*log(H0) + 1.0380039*ta...` |

### T0 common-complexity front comparison

| cut | method | metric | mean validation error | SE |
|---:|---|---|---:|---:|
| 1 | mse20 | nmse_val | 0.986 | 0 |
| 1 | mse30 | nmse_val | 0.986 | 0 |
| 1 | mse40 | nmse_val | 0.9915 | 0.003321 |
| 2 | mse20 | nmse_val | 0.986 | 0 |
| 2 | mse30 | nmse_val | 0.986 | 0 |
| 2 | mse40 | nmse_val | 0.9907 | 0.00284 |
| 3 | mse20 | nmse_val | 0.982 | 0 |
| 3 | mse30 | nmse_val | 0.982 | 0 |
| 3 | mse40 | nmse_val | 0.982 | 0 |
| 4 | mse20 | nmse_val | 0.8971 | 0.01988 |
| 4 | mse30 | nmse_val | 0.9215 | 0.0192 |
| 4 | mse40 | nmse_val | 0.9309 | 0.01507 |
| 5 | mse20 | nmse_val | 0.3514 | 0.008605 |
| 5 | mse30 | nmse_val | 0.3645 | 0.006795 |
| 5 | mse40 | nmse_val | 0.365 | 0.006916 |
| 6 | mse20 | nmse_val | 0.3514 | 0.008605 |
| 6 | mse30 | nmse_val | 0.3509 | 0.008303 |
| 6 | mse40 | nmse_val | 0.365 | 0.006916 |
| 7 | mse20 | nmse_val | 0.3005 | 0.01302 |
| 7 | mse30 | nmse_val | 0.3316 | 0.01382 |
| 7 | mse40 | nmse_val | 0.3388 | 0.008499 |
| 8 | mse20 | nmse_val | 0.2866 | 0.01024 |
| 8 | mse30 | nmse_val | 0.2719 | 0.01183 |
| 8 | mse40 | nmse_val | 0.3062 | 0.006963 |
| 9 | mse20 | nmse_val | 0.2449 | 0.001202 |
| 9 | mse30 | nmse_val | 0.2315 | 0.01388 |
| 9 | mse40 | nmse_val | 0.2557 | 0.005448 |
| 10 | mse20 | nmse_val | 0.231 | 0.009466 |
| 10 | mse30 | nmse_val | 0.2156 | 0.01537 |
| 10 | mse40 | nmse_val | 0.2464 | 0.002435 |
| 11 | mse20 | nmse_val | 0.1802 | 0.006668 |
| 11 | mse30 | nmse_val | 0.1719 | 0.005659 |
| 11 | mse40 | nmse_val | 0.1742 | 0.007368 |
| 12 | mse20 | nmse_val | 0.1641 | 0.008284 |
| 12 | mse30 | nmse_val | 0.1703 | 0.005598 |
| 12 | mse40 | nmse_val | 0.1698 | 0.005485 |
| 13 | mse20 | nmse_val | 0.1325 | 0.003099 |
| 13 | mse30 | nmse_val | 0.1567 | 0.01672 |
| 13 | mse40 | nmse_val | 0.135 | 0.01367 |
| 14 | mse20 | nmse_val | 0.1297 | 0.002065 |
| 14 | mse30 | nmse_val | 0.1482 | 0.01578 |
| 14 | mse40 | nmse_val | 0.132 | 0.01223 |
| 15 | mse20 | nmse_val | 0.1224 | 0.002656 |
| 15 | mse30 | nmse_val | 0.1296 | 0.01598 |
| 15 | mse40 | nmse_val | 0.09492 | 0.01431 |
| 16 | mse20 | nmse_val | 0.1146 | 0.006337 |
| 16 | mse30 | nmse_val | 0.1193 | 0.014 |
| 16 | mse40 | nmse_val | 0.0812 | 0.01323 |
| 17 | mse20 | nmse_val | 0.1116 | 0.005379 |
| 17 | mse30 | nmse_val | 0.09428 | 0.02072 |
| 17 | mse40 | nmse_val | 0.06139 | 0.01967 |
| 18 | mse20 | nmse_val | 0.11 | 0.006998 |
| 18 | mse30 | nmse_val | 0.07621 | 0.02205 |
| 18 | mse40 | nmse_val | 0.05926 | 0.01909 |
| 19 | mse20 | nmse_val | 0.1091 | 0.006723 |
| 19 | mse30 | nmse_val | 0.0698 | 0.02044 |
| 19 | mse40 | nmse_val | 0.04749 | 0.02013 |
| 20 | mse20 | nmse_val | 0.1087 | 0.007189 |
| 20 | mse30 | nmse_val | 0.04106 | 0.02028 |
| 20 | mse40 | nmse_val | 0.04727 | 0.01994 |

## Shuffled-target controls

| method | latent | seed | T0 val R² vs true | T0 val R² vs shuffle | T2 R² vs true | T2 R² vs independent shuffle |
|---|---:|---:|---:|---:|---:|---:|
| mse20-shuffled | z2 | 0 | -0.004196 | -0.001007 | -0.002165 | -0.001119 |
| mse20-shuffled | z2 | 1 | 0.005746 | -0.000812 | 0.004816 | -0.0003905 |
| mse20-shuffled | z2 | 2 | -8.745e-05 | -0.0006654 | -0.0001174 | -0.0001174 |
| mse40-shuffled | z2 | 0 | -0.005758 | -0.001302 | -0.005675 | -1.028e-05 |
| mse40-shuffled | z2 | 1 | 0.005743 | -0.0008186 | 0.004815 | -0.0003909 |
| mse40-shuffled | z2 | 2 | -8.748e-05 | -0.0006653 | -0.0001173 | -0.0001173 |

---
_Generated by `scripts/consolidate_mse_one_stage.py confirm`._
