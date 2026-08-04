# Blind subset selection — `lcdm_tt_ee_lowl` (roadmap Phase 4, screen 4a)

All 63 non-empty input subsets x 2 seeds per latent at the reduced screen budget (ni100, maxsize 20). Per subset: Î_S (across-seed mean front-max val MI), its one-SE knee C_S, and within-screen sufficiency η̃_S = Î_S / Î_all-6 at the SAME budget. Finalists = Pareto frontier of (|S|, C_S, −η̃_S) plus subsets non-dominated when credited one SE of their η̃; finalists go to the 4b full-protocol rerun (ni200, 5 seeds). Gate G2 is judged on 4b, not on this screen.

_Screen coverage: 756/756 reports present._


## z0 — omega_cdm

In-screen reference Î_all-6 = 1.695 +/- 0.085 nat (63 subsets scored, 15 finalists).

Staircase (best η̃ per support size): |S|=1: 0.189; |S|=2: 0.374; |S|=3: 0.636; |S|=4: 0.849; |S|=5: 1.032; |S|=6: 1.000.

| finalist | S | \|S\| | C_S | η̃ +/- SE | Î_S | best screen form |
|---|---|---:|---:|---|---:|---|
| frontier | {omega_cdm} | 1 | 4 | 0.189 +/- 0.011 | 0.320 | `log(omega_cdm - 0.098680586)` |
| frontier | {H0} | 1 | 1 | 0.090 +/- 0.011 | 0.152 | `3.75067284151594e+37*H0**4*log(H0)**4*log(ex` |
| frontier | {omega_cdm, H0} | 2 | 14 | 0.374 +/- 0.019 | 0.634 | `(5.153258e-6*omega_cdm + exp(0.0019621921*ex` |
| frontier | {omega_b, omega_cdm} | 2 | 10 | 0.319 +/- 0.016 | 0.541 | `log(log(log(exp(exp(7.565331e-7*omega_cdm/om` |
| frontier | {omega_cdm, n_s} | 2 | 9 | 0.216 +/- 0.012 | 0.366 | `exp(-59.4744617357222*(0.101710992486711*n_s` |
| frontier | {omega_b, n_s} | 2 | 3 | 0.111 +/- 0.006 | 0.187 | `n_s*omega_b` |
| frontier | {omega_b, omega_cdm, H0} | 3 | 18 | 0.636 +/- 0.032 | 1.078 | `exp(omega_b*(H0*(omega_cdm - 0.20204695) - 1` |
| frontier | {omega_cdm, H0, n_s} | 3 | 9 | 0.456 +/- 0.023 | 0.773 | `exp(0.8106866*exp(exp(0.0027513268727025*ome` |
| frontier | {omega_b, omega_cdm, n_s} | 3 | 7 | 0.385 +/- 0.019 | 0.652 | `n_s/(omega_cdm*(omega_b - 0.04359558))` |
| frontier | {omega_b, omega_cdm, H0, n_s} | 4 | 16 | 0.849 +/- 0.043 | 1.440 | `omega_cdm*(omega_b**2*(H0 + 22.734632*n_s) +` |
| frontier | {omega_b, omega_cdm, H0, tau} | 4 | 12 | 0.630 +/- 0.032 | 1.068 | `359657902846.213*(-5.25680952462043e-7*omega` |
| 1-SE keep | {omega_cdm, H0, tau, n_s} | 4 | 9 | 0.455 +/- 0.023 | 0.771 | `omega_cdm/(n_s*(H0 + 15.881314))` |
| frontier | {omega_b, omega_cdm, tau, n_s} | 4 | 6 | 0.383 +/- 0.019 | 0.650 | `-0.22925517*n_s**2*omega_b**2/omega_cdm**2 +` |
| frontier | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | 17 | 1.032 +/- 0.052 | 1.749 | `n_s + log(exp(0.05039724*H0 - 0.88328314*ome` |
| frontier | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 15 | 1.000 +/- 0.071 | 1.695 | `-0.024744758*H0*n_s*omega_b*log(A_s)/omega_c` |
|  | {omega_b, omega_cdm, H0, A_s} | 4 | 17 | 0.704 +/- 0.035 | 1.193 | `log(A_s*omega_cdm**4/(H0**3*omega_b**4))**2` |
|  | {omega_b, omega_cdm, H0, tau, n_s} | 5 | 17 | 0.850 +/- 0.043 | 1.441 | `omega_cdm*(H0 - 5.18356010934955*exp(n_s))/(` |
|  | {omega_b, omega_cdm, H0, tau, A_s} | 5 | 16 | 0.704 +/- 0.035 | 1.193 | `(omega_b*(0.02243011*H0 + 4.305718*omega_cdm` |

## z1 — H0

In-screen reference Î_all-6 = 3.462 +/- 0.340 nat (63 subsets scored, 13 finalists).

Staircase (best η̃ per support size): |S|=1: 0.185; |S|=2: 0.409; |S|=3: 0.506; |S|=4: 0.617; |S|=5: 0.843; |S|=6: 1.000.

| finalist | S | \|S\| | C_S | η̃ +/- SE | Î_S | best screen form |
|---|---|---:|---:|---|---:|---|
| frontier | {H0} | 1 | 19 | 0.185 +/- 0.018 | 0.639 | `-3.40156437628711*log(exp(exp(0.0005457697/H` |
| frontier | {omega_cdm} | 1 | 3 | 0.048 +/- 0.005 | 0.167 | `omega_cdm**4` |
| frontier | {omega_cdm, H0} | 2 | 5 | 0.409 +/- 0.040 | 1.416 | `H0 - 4.458398/omega_cdm` |
| frontier | {H0, tau} | 2 | 4 | 0.185 +/- 0.018 | 0.640 | `H0*(H0 - 0.05592164/(1.2171707 - 0.05592164/` |
| frontier | {omega_b, omega_cdm, H0} | 3 | 15 | 0.506 +/- 0.050 | 1.752 | `((-0.510477246315863*omega_b - 1666.02687524` |
| frontier | {omega_cdm, H0, tau} | 3 | 12 | 0.436 +/- 0.043 | 1.509 | `-tau + log(omega_cdm**2*(0.117590214330508*H` |
| 1-SE keep | {omega_cdm, H0, n_s} | 3 | 12 | 0.413 +/- 0.041 | 1.430 | `(-H0*omega_cdm + n_s + 3.5357182)/omega_cdm` |
| frontier | {omega_b, omega_cdm, H0, A_s} | 4 | 14 | 0.617 +/- 0.061 | 2.137 | `log(3.85127798759968e+15*omega_cdm**2*(0.011` |
| frontier | {omega_b, omega_cdm, H0, tau} | 4 | 12 | 0.581 +/- 0.057 | 2.010 | `log(H0*omega_cdm*(tau + log(omega_b))*log(om` |
| frontier | {omega_b, omega_cdm, H0, tau, A_s} | 5 | 19 | 0.843 +/- 0.083 | 2.920 | `-log(omega_cdm*(0.13591345632124*H0 + 0.3461` |
| frontier | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | 16 | 0.647 +/- 0.064 | 2.240 | `n_s + omega_b + log(omega_b**2/(A_s*(0.04644` |
| 1-SE keep | {omega_b, omega_cdm, H0, tau, n_s} | 5 | 18 | 0.602 +/- 0.059 | 2.083 | `log(log(H0**2*(0.012316842 - omega_cdm)*(n_s` |
| frontier | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 19 | 1.000 +/- 0.139 | 3.462 | `log(n_s*omega_b**2*exp(2*tau)/(A_s*omega_cdm` |
|  | {omega_b, omega_cdm, H0, n_s} | 4 | 17 | 0.514 +/- 0.051 | 1.781 | `-0.11010935*n_s - 1.90464523163686*omega_cdm` |
|  | {omega_cdm, H0, tau, A_s, n_s} | 5 | 13 | 0.507 +/- 0.051 | 1.756 | `4*(-0.240370539840504*H0*(omega_cdm + 0.0859` |

## z2 — omega_b

In-screen reference Î_all-6 = 3.238 +/- 0.018 nat (63 subsets scored, 24 finalists).

Staircase (best η̃ per support size): |S|=1: 0.142; |S|=2: 0.447; |S|=3: 0.736; |S|=4: 1.002; |S|=5: 0.996; |S|=6: 1.000.

| finalist | S | \|S\| | C_S | η̃ +/- SE | Î_S | best screen form |
|---|---|---:|---:|---|---:|---|
| frontier | {omega_b} | 1 | 14 | 0.142 +/- 0.004 | 0.460 | `exp(447.12637*omega_b)` |
| frontier | {n_s} | 1 | 6 | 0.074 +/- 0.000 | 0.241 | `exp(-6.24731e-6*n_s)` |
| frontier | {omega_cdm} | 1 | 2 | 0.017 +/- 0.000 | 0.056 | `(omega_cdm + 0.870927)**2 - 297060.427765234` |
| frontier | {omega_b, n_s} | 2 | 9 | 0.447 +/- 0.003 | 1.449 | `log(log(omega_b*(n_s - 1.5708729) + 47.45688` |
| frontier | {omega_b, A_s} | 2 | 7 | 0.136 +/- 0.002 | 0.441 | `exp(-A_s*exp(2*exp(58.196407*omega_b) - exp(` |
| frontier | {omega_b, H0} | 2 | 4 | 0.132 +/- 0.003 | 0.427 | `log(0.024855774 - omega_b)` |
| frontier | {omega_b, tau} | 2 | 3 | 0.132 +/- 0.003 | 0.427 | `tau + exp(0.00071733136*omega_b/(tau - 0.081` |
| 1-SE keep | {omega_cdm, H0} | 2 | 2 | 0.017 +/- 0.000 | 0.056 | `exp(omega_cdm)` |
| 1-SE keep | {omega_cdm, A_s} | 2 | 2 | 0.017 +/- 0.000 | 0.056 | `exp(omega_cdm)` |
| frontier | {H0, A_s} | 2 | 1 | 0.003 +/- 0.001 | 0.011 | `4284.88657231203*(0.0152767276088431*H0 - 1)` |
| frontier | {omega_b, omega_cdm, n_s} | 3 | 16 | 0.736 +/- 0.004 | 2.383 | `(-8.667906*(omega_b + 0.015736919)*log(omega` |
| frontier | {omega_b, A_s, n_s} | 3 | 11 | 0.482 +/- 0.004 | 1.562 | `omega_b*exp(-1.611823*n_s)/log(0.006379484/A` |
| frontier | {omega_b, tau, n_s} | 3 | 8 | 0.448 +/- 0.003 | 1.451 | `25.9239175471519*exp(0.0024068155*omega_b*(n` |
| frontier | {omega_b, H0, n_s} | 3 | 6 | 0.446 +/- 0.003 | 1.446 | `omega_b*(n_s - 1.5538526) - 207.17464` |
| 1-SE keep | {omega_cdm, H0, A_s} | 3 | 2 | 0.017 +/- 0.000 | 0.056 | `exp(omega_cdm)` |
| frontier | {omega_b, omega_cdm, A_s, n_s} | 4 | 17 | 1.002 +/- 0.010 | 3.244 | `log((-n_s/log((0.94726616 - omega_b)**2)**2 ` |
| frontier | {omega_b, omega_cdm, tau, n_s} | 4 | 9 | 0.733 +/- 0.005 | 2.375 | `65.675820899844*(0.123394909861252*n_s - 1)*` |
| 1-SE keep | {omega_b, H0, tau, n_s} | 4 | 8 | 0.447 +/- 0.003 | 1.449 | `log(1.2555652*log((omega_b + 0.013241855/H0)` |
| frontier | {omega_b, omega_cdm, H0, tau} | 4 | 5 | 0.167 +/- 0.013 | 0.541 | `exp(omega_cdm**2*exp(-0.00265321362118599/om` |
| 1-SE keep | {omega_cdm, H0, tau, A_s} | 4 | 2 | 0.017 +/- 0.000 | 0.056 | `exp(omega_cdm)` |
| frontier | {omega_b, omega_cdm, tau, A_s, n_s} | 5 | 16 | 0.996 +/- 0.006 | 3.224 | `log(n_s*(log(A_s) - 2.08483172263926)*(log(o` |
| frontier | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | 13 | 0.989 +/- 0.006 | 3.203 | `exp((-2*n_s + 54.0173149802303*omega_b + 2*e` |
| frontier | {omega_b, H0, tau, A_s, n_s} | 5 | 8 | 0.487 +/- 0.003 | 1.576 | `-omega_b/((n_s - 0.35086447)*log(A_s))` |
| frontier | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 15 | 1.000 +/- 0.008 | 3.238 | `log((-n_s/(15.309143*omega_b + 0.21452974) +` |
|  | {omega_b, omega_cdm, H0, n_s} | 4 | 17 | 0.740 +/- 0.006 | 2.396 | `log(-omega_b/(64.0216505857085*exp(1.1503776` |
|  | {omega_b, omega_cdm, H0, tau, n_s} | 5 | 14 | 0.735 +/- 0.010 | 2.379 | `(0.342253368799909*n_s + 1)**2*(8.5369853633` |

## z3 — n_s

In-screen reference Î_all-6 = 3.031 +/- 0.054 nat (63 subsets scored, 23 finalists).

Staircase (best η̃ per support size): |S|=1: 0.120; |S|=2: 0.255; |S|=3: 0.669; |S|=4: 1.020; |S|=5: 1.024; |S|=6: 1.000.

| finalist | S | \|S\| | C_S | η̃ +/- SE | Î_S | best screen form |
|---|---|---:|---:|---|---:|---|
| frontier | {n_s} | 1 | 17 | 0.120 +/- 0.002 | 0.363 | `-7.96942733127275e-10*n_s**2/(n_s - 0.999975` |
| frontier | {omega_cdm} | 1 | 4 | 0.045 +/- 0.006 | 0.135 | `(omega_cdm - 0.09941572)**2` |
| frontier | {omega_b} | 1 | 1 | 0.043 +/- 0.001 | 0.129 | `log(omega_b) + 2050864.1 + 0.080035925/omega` |
| frontier | {omega_cdm, n_s} | 2 | 6 | 0.255 +/- 0.005 | 0.773 | `log(0.48381752*n_s + omega_cdm)` |
| frontier | {omega_b, n_s} | 2 | 5 | 0.243 +/- 0.004 | 0.737 | `(n_s - 1.26655)/omega_b` |
| 1-SE keep | {omega_cdm, A_s} | 2 | 4 | 0.043 +/- 0.008 | 0.130 | `(omega_cdm - 0.0994376)**2` |
| 1-SE keep | {omega_b, A_s} | 2 | 1 | 0.042 +/- 0.001 | 0.129 | `log(omega_b + 2744.5713)` |
| frontier | {omega_b, omega_cdm, n_s} | 3 | 12 | 0.669 +/- 0.012 | 2.029 | `log(((log(omega_cdm) - 0.029788466/omega_b)*` |
| frontier | {omega_b, H0, n_s} | 3 | 9 | 0.258 +/- 0.005 | 0.781 | `log(n_s**2*(omega_b + 0.30814683/H0))` |
| frontier | {omega_cdm, A_s, n_s} | 3 | 6 | 0.256 +/- 0.005 | 0.776 | `-exp(9.54704858431379e-6*exp(n_s + 2*omega_c` |
| 1-SE keep | {omega_b, A_s, n_s} | 3 | 5 | 0.234 +/- 0.010 | 0.708 | `(n_s - 1.2665405)/omega_b` |
| frontier | {omega_b, tau, A_s} | 3 | 1 | 0.044 +/- 0.002 | 0.133 | `exp(2*(0.8914372*A_s + omega_b*(omega_b - ta` |
| 1-SE keep | {omega_cdm, tau, A_s} | 3 | 4 | 0.044 +/- 0.007 | 0.132 | `(omega_cdm - 0.09953938)**2` |
| frontier | {omega_b, omega_cdm, H0, n_s} | 4 | 16 | 1.020 +/- 0.021 | 3.093 | `-exp(omega_b)*log((omega_cdm + log(H0))/(n_s` |
| 1-SE keep | {omega_b, omega_cdm, A_s, n_s} | 4 | 12 | 0.668 +/- 0.012 | 2.024 | `(3.7108579*n_s**2*omega_b - 0.031407822*n_s*` |
| 1-SE keep | {omega_b, omega_cdm, tau, n_s} | 4 | 15 | 0.667 +/- 0.012 | 2.021 | `n_s - omega_cdm + 0.4464371*log(n_s*omega_b*` |
| frontier | {omega_cdm, H0, tau, n_s} | 4 | 6 | 0.267 +/- 0.013 | 0.810 | `5.77208364472411*(0.4162303*n_s + omega_cdm ` |
| 1-SE keep | {omega_b, H0, tau, n_s} | 4 | 11 | 0.263 +/- 0.008 | 0.799 | `log(log(exp(n_s) + exp(453.270657343716*n_s*` |
| frontier | {omega_b, omega_cdm, H0, A_s} | 4 | 3 | 0.101 +/- 0.002 | 0.307 | `omega_b*omega_cdm` |
| frontier | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | 19 | 1.024 +/- 0.019 | 3.104 | `omega_b + omega_cdm - log(-n_s*omega_b*(omeg` |
| frontier | {omega_b, omega_cdm, H0, tau, n_s} | 5 | 13 | 1.001 +/- 0.022 | 3.035 | `-exp((omega_cdm - 0.11451867)**2 + exp((H0*(` |
| 1-SE keep | {omega_cdm, H0, tau, A_s, n_s} | 5 | 8 | 0.266 +/- 0.012 | 0.806 | `n_s**4*omega_cdm/log(H0)` |
| 1-SE keep | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 15 | 1.000 +/- 0.025 | 3.031 | `log(omega_b*(n_s**4 + 0.102433644)*(omega_b ` |
|  | {omega_b, omega_cdm, tau, A_s, n_s} | 5 | 13 | 0.668 +/- 0.012 | 2.024 | `-omega_b*(n_s - omega_cdm)*(omega_b - 0.0564` |

## z4 — tau (amplitude sector)

In-screen reference Î_all-6 = 2.009 +/- 0.054 nat (63 subsets scored, 26 finalists).

Staircase (best η̃ per support size): |S|=1: 0.259; |S|=2: 1.110; |S|=3: 1.084; |S|=4: 1.106; |S|=5: 1.123; |S|=6: 1.000.

| finalist | S | \|S\| | C_S | η̃ +/- SE | Î_S | best screen form |
|---|---|---:|---:|---|---:|---|
| frontier | {tau} | 1 | 9 | 0.259 +/- 0.008 | 0.520 | `(tau + 0.054115247)*log(tau) + exp(tau)` |
| frontier | {A_s} | 1 | 8 | 0.137 +/- 0.004 | 0.276 | `-0.9612273*log(log(A_s - log(0.13999358 + 0.` |
| frontier | {omega_cdm} | 1 | 4 | 0.018 +/- 0.001 | 0.037 | `(omega_cdm - 0.11188731)**2` |
| frontier | {H0} | 1 | 3 | 0.017 +/- 0.000 | 0.035 | `-0.35586667/H0` |
| 1-SE keep | {omega_b} | 1 | 4 | 0.016 +/- 0.008 | 0.032 | `(omega_b - 0.02375598)**2` |
| frontier | {tau, A_s} | 2 | 18 | 1.110 +/- 0.053 | 2.230 | `12.6684957440822*A_s*(-tau*(log(tau) + 1.400` |
| frontier | {omega_cdm, tau} | 2 | 15 | 0.263 +/- 0.007 | 0.528 | `(omega_cdm + 0.12129761)*(tau*(omega_cdm - 4` |
| 1-SE keep | {H0, tau} | 2 | 11 | 0.257 +/- 0.007 | 0.517 | `-(exp(12.929587*tau) - 0.18939504)*(log(tau)` |
| frontier | {tau, n_s} | 2 | 7 | 0.255 +/- 0.007 | 0.511 | `(tau**4 - 1.7998052e-6)/tau**2` |
| frontier | {omega_b, A_s} | 2 | 2 | 0.138 +/- 0.004 | 0.276 | `0.418618615500979*A_s*exp(-omega_b)` |
| 1-SE keep | {H0, A_s} | 2 | 2 | 0.137 +/- 0.004 | 0.276 | `log(A_s)` |
| 1-SE keep | {A_s, n_s} | 2 | 2 | 0.137 +/- 0.004 | 0.276 | `log(A_s)` |
| frontier | {omega_b, tau, A_s} | 3 | 11 | 1.084 +/- 0.078 | 2.178 | `A_s*exp(-omega_b)/(134.60627637803*(tau - 0.` |
| frontier | {omega_b, omega_cdm, tau} | 3 | 2 | 0.255 +/- 0.008 | 0.513 | `(omega_cdm - 3.3331158*tau)/(omega_b*tau*(ta` |
| 1-SE keep | {omega_b, omega_cdm, tau, A_s} | 4 | 18 | 1.106 +/- 0.032 | 2.221 | `692.82388833766*(0.0379916865285406*omega_b ` |
| 1-SE keep | {omega_cdm, tau, A_s, n_s} | 4 | 19 | 1.094 +/- 0.031 | 2.198 | `-log(-n_s + omega_cdm - 11.322049*log(A_s) +` |
| frontier | {omega_cdm, H0, tau, A_s} | 4 | 13 | 1.094 +/- 0.043 | 2.197 | `A_s/log(-(7.3018566*tau + 0.438925114899504)` |
| frontier | {omega_b, tau, A_s, n_s} | 4 | 12 | 1.085 +/- 0.057 | 2.179 | `-0.56660455*A_s*exp(exp(1472.9854054119*(0.0` |
| 1-SE keep | {H0, tau, A_s, n_s} | 4 | 12 | 1.071 +/- 0.078 | 2.151 | `2.47729782640356*n_s**2*tau**2/(n_s*tau*(-ex` |
| 1-SE keep | {omega_b, H0, tau, A_s} | 4 | 12 | 1.044 +/- 0.071 | 2.096 | `(tau + log(log((tau - 0.32531226)**2*(log(-l` |
| 1-SE keep | {omega_b, omega_cdm, H0, tau} | 4 | 10 | 0.259 +/- 0.008 | 0.519 | `H0 - omega_cdm/(omega_b*tau) + 32355.5244711` |
| 1-SE keep | {omega_b, omega_cdm, tau, n_s} | 4 | 2 | 0.254 +/- 0.007 | 0.510 | `log(0.028798675*n_s/tau - tau)/omega_b` |
| 1-SE keep | {omega_cdm, H0, tau, n_s} | 4 | 2 | 0.254 +/- 0.007 | 0.509 | `(tau + (tau - 0.14982179)*(-log(H0**2) + log` |
| frontier | {omega_cdm, H0, tau, A_s, n_s} | 5 | 18 | 1.123 +/- 0.044 | 2.256 | `2.73552096899614*A_s*(19187752.9970005*tau**` |
| frontier | {omega_b, omega_cdm, H0, tau, A_s} | 5 | 14 | 1.116 +/- 0.071 | 2.242 | `A_s*exp(61.91497384308*((tau + 0.1270873*log` |
| 1-SE keep | {omega_b, omega_cdm, H0, tau, n_s} | 5 | 10 | 0.253 +/- 0.007 | 0.508 | `omega_cdm*(log((0.776644860032287*omega_b - ` |
|  | {H0, tau, A_s} | 3 | 19 | 1.051 +/- 0.045 | 2.112 | `-A_s*(tau**2*exp(tau) - 0.10783893)/(tau**2 ` |
|  | {tau, A_s, n_s} | 3 | 13 | 1.033 +/- 0.033 | 2.076 | `A_s*tau*exp(0.14384435/(tau + 0.0390386))` |
|  | {omega_cdm, tau, A_s} | 3 | 13 | 0.999 +/- 0.052 | 2.006 | `A_s*exp(exp(252.691517174929*tau**4))/(log(t` |
|  | {omega_b, omega_cdm, tau, A_s, n_s} | 5 | 18 | 1.079 +/- 0.034 | 2.168 | `-0.4814401*n_s/(n_s*(log((tau + 0.06381267)*` |
|  | {omega_b, H0, tau, A_s, n_s} | 5 | 11 | 1.008 +/- 0.054 | 2.025 | `-A_s*tau/((6.659247*tau + 0.023888363)*((A_s` |
|  | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 15 | 1.000 +/- 0.038 | 2.009 | `log(tau + log(46.2082986291257*H0/tau**2 + 0` |

## z5 — amplitude (A_s, tau)

In-screen reference Î_all-6 = 3.413 +/- 0.135 nat (63 subsets scored, 25 finalists).

Staircase (best η̃ per support size): |S|=1: 0.110; |S|=2: 0.351; |S|=3: 0.491; |S|=4: 0.660; |S|=5: 0.836; |S|=6: 1.000.

| finalist | S | \|S\| | C_S | η̃ +/- SE | Î_S | best screen form |
|---|---|---:|---:|---|---:|---|
| frontier | {A_s} | 1 | 8 | 0.110 +/- 0.004 | 0.376 | `exp(1.01391789283801*(exp(0.0021346514/log(A` |
| frontier | {tau} | 1 | 2 | 0.087 +/- 0.003 | 0.296 | `tau**2` |
| frontier | {tau, A_s} | 2 | 9 | 0.351 +/- 0.014 | 1.198 | `exp(3988.4240800082*A_s*exp(-2*tau))` |
| frontier | {omega_cdm, A_s} | 2 | 5 | 0.136 +/- 0.008 | 0.463 | `A_s*log(omega_cdm)` |
| frontier | {H0, A_s} | 2 | 4 | 0.131 +/- 0.005 | 0.446 | `log(0.473583/H0)/A_s` |
| frontier | {omega_b, A_s} | 2 | 3 | 0.110 +/- 0.004 | 0.376 | `(A_s - 0.8734914)*(5.546724*A_s - 0.00553681` |
| frontier | {H0, tau} | 2 | 2 | 0.088 +/- 0.004 | 0.299 | `exp(-0.41040465/(0.0021441516*H0 + tau - 0.1` |
| 1-SE keep | {tau, n_s} | 2 | 2 | 0.087 +/- 0.003 | 0.296 | `tau**2 + 6625.443` |
| 1-SE keep | {omega_b, tau} | 2 | 2 | 0.087 +/- 0.003 | 0.296 | `tau**2` |
| 1-SE keep | {omega_cdm, tau} | 2 | 2 | 0.087 +/- 0.003 | 0.296 | `tau**2` |
| frontier | {omega_cdm, tau, A_s} | 3 | 13 | 0.491 +/- 0.019 | 1.677 | `exp(omega_cdm + exp(tau))/(A_s*exp(-omega_cd` |
| frontier | {omega_b, omega_cdm, A_s} | 3 | 4 | 0.145 +/- 0.007 | 0.494 | `A_s*omega_cdm*(omega_cdm - 0.20510776)*exp(5` |
| 1-SE keep | {omega_cdm, A_s, n_s} | 3 | 4 | 0.141 +/- 0.006 | 0.482 | `A_s*log(omega_cdm)` |
| 1-SE keep | {omega_b, omega_cdm, tau} | 3 | 2 | 0.087 +/- 0.003 | 0.296 | `tau**2` |
| 1-SE keep | {omega_b, H0, tau} | 3 | 2 | 0.087 +/- 0.003 | 0.296 | `tau**2` |
| 1-SE keep | {omega_b, tau, n_s} | 3 | 2 | 0.087 +/- 0.003 | 0.296 | `tau**2` |
| 1-SE keep | {omega_cdm, tau, n_s} | 3 | 2 | 0.087 +/- 0.003 | 0.296 | `tau**2` |
| 1-SE keep | {H0, tau, n_s} | 3 | 2 | 0.087 +/- 0.003 | 0.296 | `tau**2` |
| frontier | {omega_cdm, H0, tau, A_s} | 4 | 13 | 0.660 +/- 0.026 | 2.254 | `log(exp(2.8573888*omega_cdm + 2*tau)*log(H0)` |
| 1-SE keep | {omega_b, omega_cdm, A_s, n_s} | 4 | 4 | 0.141 +/- 0.006 | 0.482 | `A_s*log(omega_cdm)` |
| frontier | {omega_b, omega_cdm, H0, tau} | 4 | 2 | 0.097 +/- 0.011 | 0.331 | `omega_b*(H0*(omega_cdm + 0.594002393473244*t` |
| frontier | {omega_cdm, H0, tau, A_s, n_s} | 5 | 17 | 0.836 +/- 0.033 | 2.855 | `log(exp(2*tau + 2.789654*omega_cdm/n_s)*log(` |
| frontier | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | 7 | 0.163 +/- 0.007 | 0.558 | `-(omega_cdm + 0.3486698)*log(H0)/A_s` |
| frontier | {omega_b, omega_cdm, H0, tau, n_s} | 5 | 2 | 0.108 +/- 0.022 | 0.369 | `-H0*(omega_cdm**2 + (omega_cdm + tau)**2) + ` |
| frontier | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 20 | 1.000 +/- 0.056 | 3.413 | `-omega_cdm + exp(exp(2*omega_b)) - log((0.34` |
|  | {omega_cdm, tau, A_s, n_s} | 4 | 19 | 0.545 +/- 0.022 | 1.860 | `(n_s + tau - log(A_s*(0.48633355*n_s - omega` |
|  | {omega_b, omega_cdm, tau, A_s} | 4 | 17 | 0.504 +/- 0.020 | 1.722 | `((omega_b - 0.29261237)*exp(2*tau)/(A_s*(ome` |
|  | {omega_b, omega_cdm, H0, tau, A_s} | 5 | 18 | 0.723 +/- 0.029 | 2.468 | `log(A_s*exp(5.811106*omega_b - 2.905553*omeg` |
|  | {omega_b, omega_cdm, tau, A_s, n_s} | 5 | 15 | 0.571 +/- 0.024 | 1.948 | `log(A_s*exp(2*omega_b - 2*tau)/(omega_b - 0.` |

---
_Generated by `scripts/consolidate_subsets.py` from `hpsweep_subsets_v1`._


# 4b finals — full protocol (ni200 x 5 seeds)

_Finals coverage: 605/605 reports. Reference = `allparams` (full-protocol all-6, 5 seeds). S* = smallest |S| (ties: smaller knee C) whose Î_S is within one combined SE of every measured superset; recurrence = the same minimality holds in each 4a screen seed separately._


## z0 — omega_cdm

Reference Î_all-6 = 1.769 +/- 0.007 nat.
**S\* = {omega_b, omega_cdm, H0, tau, A_s, n_s}** — η_S = 1.000 +/- 0.000, C_S = 18, screen-recurrent: True (per-seed minimal: s0=True, s1=True; per-seed picks agree: True).

Staircase (best η_S per support size): |S|=1: 0.174; |S|=2: 0.356; |S|=3: 0.604; |S|=4: 0.811; |S|=5: 0.989; |S|=6: 1.000.

| | S | \|S\| | C_S | η_S +/- SE | Î_S +/- SE | minimal | best form |
|---|---|---:|---:|---|---|---|---|
|  | {omega_cdm} | 1 | 4 | 0.174 +/- 0.004 | 0.309 +/- 0.007 | no | `log(omega_cdm - 0.09838888)` |
|  | {H0} | 1 | 8 | 0.086 +/- 0.006 | 0.153 +/- 0.011 | no | `0.0167257418096133*exp(113.761091540569/H0**` |
|  | {omega_cdm, H0} | 2 | 13 | 0.356 +/- 0.003 | 0.630 +/- 0.004 | no | `exp(0.0926810659285526*omega_cdm**6) + omega` |
|  | {omega_b, omega_cdm} | 2 | 8 | 0.306 +/- 0.002 | 0.541 +/- 0.003 | no | `0.480796/log(omega_b/omega_cdm - 0.15215628)` |
|  | {omega_cdm, n_s} | 2 | 10 | 0.204 +/- 0.003 | 0.361 +/- 0.004 | no | `exp(exp(-59.7797808349821*(0.102288411689581` |
|  | {omega_b, n_s} | 2 | 10 | 0.108 +/- 0.002 | 0.190 +/- 0.003 | no | `-7.2611896e-5*omega_b + 1.112152*exp(0.47429` |
|  | {omega_b, omega_cdm, H0} | 3 | 11 | 0.604 +/- 0.003 | 1.069 +/- 0.002 | no | `-omega_b*(H0*(omega_cdm - 0.20170897) - 1.80` |
|  | {omega_cdm, H0, n_s} | 3 | 9 | 0.438 +/- 0.002 | 0.774 +/- 0.002 | no | `omega_cdm**2*(H0 - 113.93289)/n_s**2` |
|  | {omega_b, omega_cdm, n_s} | 3 | 8 | 0.370 +/- 0.002 | 0.654 +/- 0.001 | no | `145278.501308389*(0.00262361028347138*n_s/om` |
|  | {omega_b, omega_cdm, H0, n_s} | 4 | 12 | 0.811 +/- 0.003 | 1.434 +/- 0.002 | no | `omega_cdm*(omega_b**2 + 0.026196986)*exp(-n_` |
|  | {omega_b, omega_cdm, H0, tau} | 4 | 10 | 0.604 +/- 0.003 | 1.068 +/- 0.003 | no | `-omega_b*(H0*(omega_b + omega_cdm - 0.224654` |
|  | {omega_cdm, H0, tau, n_s} | 4 | 8 | 0.435 +/- 0.003 | 0.770 +/- 0.005 | no | `exp(0.00226407122601137*omega_cdm**2/((0.047` |
|  | {omega_b, omega_cdm, tau, n_s} | 4 | 7 | 0.369 +/- 0.002 | 0.652 +/- 0.001 | no | `(0.00262293004262629*n_s + omega_b*omega_cdm` |
|  | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | 17 | 0.989 +/- 0.007 | 1.749 +/- 0.009 | no | `(H0*omega_cdm + (H0*n_s*omega_b + omega_cdm*` |
| **S\*** | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 18 | 1.000 +/- 0.000 | 1.769 +/- 0.007 | yes | `omega_b*(H0 + 27.826664)*(n_s - 0.095620185)` |

Re-clustered finalist forms (Phase-2 machinery, 579 forms): top cluster rep `H0*omega_b/omega_cdm` (c=5, support {omega_b, omega_cdm, H0}, R_allparams=0.8).

## z1 — H0

Reference Î_all-6 = 3.572 +/- 0.176 nat.
**S\* = {omega_b, omega_cdm, H0, tau, A_s, n_s}** — η_S = 1.000 +/- 0.000, C_S = 18, screen-recurrent: True (per-seed minimal: s0=True, s1=True; per-seed picks agree: False).

Staircase (best η_S per support size): |S|=1: 0.177; |S|=2: 0.397; |S|=3: 0.490; |S|=4: 0.602; |S|=5: 0.829; |S|=6: 1.000.

| | S | \|S\| | C_S | η_S +/- SE | Î_S +/- SE | minimal | best form |
|---|---|---:|---:|---|---|---|---|
|  | {H0} | 1 | 4 | 0.177 +/- 0.009 | 0.631 +/- 0.008 | no | `0.89510218248256/H0**2` |
|  | {omega_cdm} | 1 | 16 | 0.044 +/- 0.002 | 0.158 +/- 0.000 | no | `5.09355899810778*exp(-4.56093716494928e-5*om` |
|  | {omega_cdm, H0} | 2 | 6 | 0.397 +/- 0.020 | 1.418 +/- 0.003 | no | `(log(H0*omega_cdm) - 0.802525753004956)/(ome` |
|  | {H0, tau} | 2 | 4 | 0.177 +/- 0.009 | 0.631 +/- 0.000 | no | `-H0 + log(tau)` |
|  | {omega_b, omega_cdm, H0} | 3 | 11 | 0.490 +/- 0.024 | 1.749 +/- 0.005 | no | `exp(omega_cdm)/(log(-H0*omega_cdm*(log(omega` |
|  | {omega_cdm, H0, tau} | 3 | 16 | 0.425 +/- 0.021 | 1.516 +/- 0.003 | no | `0.281898492979282 + 1.08233239388204/log(log` |
|  | {omega_cdm, H0, n_s} | 3 | 10 | 0.400 +/- 0.020 | 1.430 +/- 0.002 | no | `exp((-0.0070466674*H0*omega_cdm + 0.00704666` |
|  | {omega_b, omega_cdm, H0, A_s} | 4 | 19 | 0.602 +/- 0.030 | 2.149 +/- 0.002 | no | `exp((0.043133087*H0 + 0.229761326867521*omeg` |
|  | {omega_b, omega_cdm, H0, tau} | 4 | 17 | 0.569 +/- 0.028 | 2.032 +/- 0.002 | no | `tau + log(omega_b/(omega_cdm**2*(0.113700462` |
|  | {omega_b, omega_cdm, H0, tau, A_s} | 5 | 19 | 0.829 +/- 0.041 | 2.960 +/- 0.010 | no | `omega_cdm + 2*tau + log(omega_b**2/(A_s*omeg` |
|  | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | 18 | 0.634 +/- 0.031 | 2.266 +/- 0.009 | no | `-H0/(n_s + log(omega_b**2/A_s))**2 + 0.02565` |
|  | {omega_b, omega_cdm, H0, tau, n_s} | 5 | 19 | 0.590 +/- 0.029 | 2.108 +/- 0.006 | no | `-n_s*(tau + 0.7072942) - 50.906757*omega_b +` |
| **S\*** | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 18 | 1.000 +/- 0.000 | 3.572 +/- 0.176 | yes | `log(-log(n_s) + log(A_s*omega_cdm**4*(0.0014` |

Re-clustered finalist forms (Phase-2 machinery, 576 forms): top cluster rep `H0**2*omega_cdm` (c=4, support {omega_cdm, H0}, R_allparams=0.8).

## z2 — omega_b

Reference Î_all-6 = 3.282 +/- 0.022 nat.
**S\* = {omega_b, omega_cdm, A_s, n_s}** — η_S = 0.995 +/- 0.008, C_S = 16, screen-recurrent: True (per-seed minimal: s0=True, s1=True; per-seed picks agree: True).

Staircase (best η_S per support size): |S|=1: 0.131; |S|=2: 0.442; |S|=3: 0.725; |S|=4: 0.995; |S|=5: 0.993; |S|=6: 1.000.

| | S | \|S\| | C_S | η_S +/- SE | Î_S +/- SE | minimal | best form |
|---|---|---:|---:|---|---|---|---|
|  | {omega_b} | 1 | 4 | 0.131 +/- 0.003 | 0.430 +/- 0.008 | no | `log(exp(0.545885845707158*omega_b**4))**2/om` |
|  | {n_s} | 1 | 7 | 0.073 +/- 0.001 | 0.241 +/- 0.000 | no | `58674737422.4144*exp(-2.57585652e-5*n_s)` |
|  | {omega_cdm} | 1 | 9 | 0.022 +/- 0.003 | 0.073 +/- 0.011 | no | `2.88976948459684*(0.588258755260945*omega_cd` |
|  | {omega_b, n_s} | 2 | 9 | 0.442 +/- 0.003 | 1.449 +/- 0.001 | no | `6402261.09328477/log(log((omega_b + 18.69483` |
|  | {omega_b, A_s} | 2 | 6 | 0.133 +/- 0.002 | 0.438 +/- 0.006 | no | `exp(A_s*exp(340.5838410814*omega_b))` |
|  | {omega_b, H0} | 2 | 4 | 0.133 +/- 0.004 | 0.435 +/- 0.011 | no | `exp(446.11487*omega_b)` |
|  | {omega_b, tau} | 2 | 8 | 0.127 +/- 0.001 | 0.417 +/- 0.000 | no | `1.48299685562489e+19*exp(-0.0130337578606172` |
|  | {omega_cdm, H0} | 2 | 8 | 0.021 +/- 0.002 | 0.068 +/- 0.007 | no | `exp(2*H0*(omega_cdm - 0.10005605)/omega_cdm)` |
|  | {omega_cdm, A_s} | 2 | 10 | 0.018 +/- 0.000 | 0.058 +/- 0.001 | no | `0.00897531251799187*A_s/(omega_cdm - 0.10418` |
|  | {H0, A_s} | 2 | 4 | 0.003 +/- 0.001 | 0.008 +/- 0.002 | no | `4285.84756496823*(0.0152750148033987*H0 - 1)` |
|  | {omega_b, omega_cdm, n_s} | 3 | 10 | 0.725 +/- 0.005 | 2.380 +/- 0.004 | no | `(omega_cdm + 0.5359204)*(-n_s + 26.605696*om` |
|  | {omega_b, A_s, n_s} | 3 | 13 | 0.479 +/- 0.003 | 1.570 +/- 0.004 | no | `0.0430672731054336*log((0.04689203*omega_b +` |
|  | {omega_b, H0, n_s} | 3 | 18 | 0.442 +/- 0.003 | 1.451 +/- 0.001 | no | `56.4734180824034*(0.335590225578864*log(exp(` |
|  | {omega_b, tau, n_s} | 3 | 8 | 0.442 +/- 0.003 | 1.450 +/- 0.002 | no | `omega_b*(n_s - 1.5624692) - 759.66046` |
|  | {omega_cdm, H0, A_s} | 3 | 13 | 0.018 +/- 0.001 | 0.059 +/- 0.002 | no | `-omega_cdm**3/(omega_cdm**2*(H0 + 1.4876934)` |
| **S\*** | {omega_b, omega_cdm, A_s, n_s} | 4 | 16 | 0.995 +/- 0.008 | 3.264 +/- 0.012 | yes | `log(log(log(exp(exp((omega_b/(omega_cdm - 0.` |
|  | {omega_b, omega_cdm, tau, n_s} | 4 | 10 | 0.724 +/- 0.005 | 2.377 +/- 0.003 | no | `-omega_cdm + 0.625161995518996*exp(n_s - 26.` |
|  | {omega_b, H0, tau, n_s} | 4 | 8 | 0.442 +/- 0.003 | 1.449 +/- 0.001 | no | `omega_b*(n_s - 1.5649613) + 779.9856` |
|  | {omega_b, omega_cdm, H0, tau} | 4 | 8 | 0.174 +/- 0.003 | 0.572 +/- 0.009 | no | `-1.37307026130969*exp(exp(exp(-2*omega_cdm**` |
|  | {omega_cdm, H0, tau, A_s} | 4 | 2 | 0.018 +/- 0.001 | 0.058 +/- 0.002 | no | `A_s**2/(tau - 0.011431578)**2 - A_s*omega_cd` |
|  | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | 18 | 0.993 +/- 0.008 | 3.257 +/- 0.015 | yes | `log(n_s*log(0.11159694/omega_b)*log(A_s/log(` |
|  | {omega_b, omega_cdm, tau, A_s, n_s} | 5 | 17 | 0.985 +/- 0.007 | 3.234 +/- 0.010 | no | `exp((-8*n_s - 8*omega_b*(omega_cdm + 0.52580` |
|  | {omega_b, H0, tau, A_s, n_s} | 5 | 8 | 0.479 +/- 0.003 | 1.572 +/- 0.002 | no | `12.4408386189433*(n_s*log(A_s) + 0.283514432` |
|  | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 20 | 1.000 +/- 0.000 | 3.282 +/- 0.022 | yes | `H0*((n_s - 1.0812154*omega_cdm)*log(A_s) + 6` |

Re-clustered finalist forms (Phase-2 machinery, 754 forms): top cluster rep `omega_b/n_s**2` (c=4, support {omega_b, n_s}, R_allparams=0.8).

## z3 — n_s

Reference Î_all-6 = 3.117 +/- 0.024 nat.
**S\* = {omega_b, omega_cdm, H0, n_s}** — η_S = 0.992 +/- 0.010, C_S = 17, screen-recurrent: False (per-seed minimal: s0=True, s1=False; per-seed picks agree: False).

Staircase (best η_S per support size): |S|=1: 0.117; |S|=2: 0.248; |S|=3: 0.652; |S|=4: 0.992; |S|=5: 1.006; |S|=6: 1.000.

| | S | \|S\| | C_S | η_S +/- SE | Î_S +/- SE | minimal | best form |
|---|---|---:|---:|---|---|---|---|
|  | {n_s} | 1 | 14 | 0.117 +/- 0.002 | 0.365 +/- 0.004 | no | `1.0*n_s**4 - 2.33521995427032*n_s**2 + 20289` |
|  | {omega_b} | 1 | 14 | 0.044 +/- 0.002 | 0.136 +/- 0.006 | no | `-omega_b - 0.03218924/(omega_b - 0.022519022` |
|  | {omega_cdm} | 1 | 12 | 0.041 +/- 0.002 | 0.128 +/- 0.006 | no | `(omega_cdm - 0.09928881)**2` |
|  | {omega_cdm, n_s} | 2 | 6 | 0.248 +/- 0.002 | 0.773 +/- 0.000 | no | `log(n_s + 2.0668316*omega_cdm)` |
|  | {omega_b, n_s} | 2 | 12 | 0.223 +/- 0.003 | 0.695 +/- 0.009 | no | `-0.127066336720944 - 4.55610447869809e-11/(0` |
|  | {omega_cdm, A_s} | 2 | 6 | 0.046 +/- 0.002 | 0.142 +/- 0.005 | no | `(omega_cdm - 0.099475406)**2` |
|  | {omega_b, A_s} | 2 | 9 | 0.044 +/- 0.002 | 0.137 +/- 0.006 | no | `(6.09249603104346*A_s + omega_b*(omega_b - 0` |
|  | {omega_b, omega_cdm, n_s} | 3 | 13 | 0.652 +/- 0.005 | 2.032 +/- 0.005 | no | `exp(38.9241277667367*omega_b) - log(n_s**4*o` |
|  | {omega_b, H0, n_s} | 3 | 9 | 0.254 +/- 0.004 | 0.793 +/- 0.010 | no | `0.4133517*exp(exp((-2.4848341e-5*n_s*omega_b` |
|  | {omega_cdm, A_s, n_s} | 3 | 6 | 0.248 +/- 0.002 | 0.774 +/- 0.001 | no | `-6.7703949692924*log(exp(5.01078484223454e-6` |
|  | {omega_b, A_s, n_s} | 3 | 6 | 0.226 +/- 0.004 | 0.704 +/- 0.013 | no | `(n_s - 1.2664945)/omega_b` |
|  | {omega_cdm, tau, A_s} | 3 | 12 | 0.047 +/- 0.002 | 0.148 +/- 0.005 | no | `0.772976919672024*A_s/(tau - 0.04585297)**2 ` |
|  | {omega_b, tau, A_s} | 3 | 12 | 0.046 +/- 0.003 | 0.145 +/- 0.009 | no | `0.97157484/(-0.161084548287096*A_s/(omega_b ` |
| **S\*** | {omega_b, omega_cdm, H0, n_s} | 4 | 17 | 0.992 +/- 0.010 | 3.090 +/- 0.020 | yes | `log(omega_b/((n_s + 2*omega_cdm)*(omega_b - ` |
|  | {omega_b, omega_cdm, A_s, n_s} | 4 | 15 | 0.651 +/- 0.005 | 2.028 +/- 0.004 | no | `(omega_b**2 + 0.005707082)*log(n_s**4*omega_` |
|  | {omega_b, omega_cdm, tau, n_s} | 4 | 13 | 0.650 +/- 0.005 | 2.026 +/- 0.002 | no | `omega_b**2*(n_s*omega_cdm + omega_cdm - 0.02` |
|  | {omega_b, H0, tau, n_s} | 4 | 12 | 0.255 +/- 0.002 | 0.795 +/- 0.004 | no | `5.444962e-6*exp(n_s) + 5.444962e-6*log(omega` |
|  | {omega_cdm, H0, tau, n_s} | 4 | 6 | 0.252 +/- 0.004 | 0.786 +/- 0.013 | no | `omega_cdm*(n_s - 0.7176179)/log(H0)` |
|  | {omega_b, omega_cdm, H0, A_s} | 4 | 7 | 0.099 +/- 0.001 | 0.309 +/- 0.003 | no | `omega_b*(omega_cdm + 0.026575407) - 1493.072` |
|  | {omega_b, omega_cdm, H0, tau, n_s} | 5 | 17 | 1.006 +/- 0.016 | 3.134 +/- 0.043 | yes | `exp(2*H0*omega_b*exp(n_s)/(H0*omega_b*(log(o` |
|  | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | 19 | 1.000 +/- 0.009 | 3.115 +/- 0.016 | yes | `-0.5049022*n_s + omega_b - omega_cdm + 0.003` |
|  | {omega_cdm, H0, tau, A_s, n_s} | 5 | 9 | 0.248 +/- 0.002 | 0.774 +/- 0.001 | no | `exp((A_s*H0 - (n_s + 2*omega_cdm)*(omega_cdm` |
|  | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 17 | 1.000 +/- 0.000 | 3.117 +/- 0.024 | yes | `log(tau**2 + exp(-4.407752*n_s)*log(H0)/(ome` |

Re-clustered finalist forms (Phase-2 machinery, 393 forms): top cluster rep `log(omega_b*omega_cdm)/n_s` (c=6, support {omega_b, omega_cdm, n_s}, R_allparams=0.8).

## z4 — tau (amplitude sector)

Reference Î_all-6 = 2.166 +/- 0.043 nat.
**S\* = {omega_b, tau, A_s}** — η_S = 1.068 +/- 0.026, C_S = 17, screen-recurrent: False (per-seed minimal: s0=True, s1=False; per-seed picks agree: False).

Staircase (best η_S per support size): |S|=1: 0.237; |S|=2: 0.955; |S|=3: 1.068; |S|=4: 1.059; |S|=5: 1.064; |S|=6: 1.000.

| | S | \|S\| | C_S | η_S +/- SE | Î_S +/- SE | minimal | best form |
|---|---|---:|---:|---|---|---|---|
|  | {tau} | 1 | 10 | 0.237 +/- 0.005 | 0.514 +/- 0.002 | no | `(tau + 0.057059366)*(tau + log(tau) + 0.8349` |
|  | {A_s} | 1 | 2 | 0.127 +/- 0.003 | 0.276 +/- 0.000 | no | `log(A_s)` |
|  | {omega_cdm} | 1 | 4 | 0.020 +/- 0.002 | 0.042 +/- 0.005 | no | `(omega_cdm - 0.11134348)**2` |
|  | {H0} | 1 | 10 | 0.014 +/- 0.001 | 0.030 +/- 0.003 | no | `-0.22077805/H0` |
|  | {omega_b} | 1 | 9 | 0.007 +/- 0.002 | 0.014 +/- 0.005 | no | `0.02038491/(omega_b - 0.02038491)**2` |
|  | {tau, A_s} | 2 | 13 | 0.955 +/- 0.045 | 2.068 +/- 0.088 | no | `-A_s/log(0.38789064*tau/(tau*exp(-595.272635` |
|  | {omega_cdm, tau} | 2 | 9 | 0.238 +/- 0.005 | 0.516 +/- 0.005 | no | `omega_cdm*(log(log((1.55907515038449*tau + 0` |
|  | {H0, tau} | 2 | 10 | 0.238 +/- 0.005 | 0.516 +/- 0.005 | no | `log(-(tau - 0.10384653)**2 - 0.0062582484*lo` |
|  | {tau, n_s} | 2 | 11 | 0.237 +/- 0.005 | 0.514 +/- 0.003 | no | `21.270615551571*(tau - 3.92652815782611e-9)*` |
|  | {A_s, n_s} | 2 | 14 | 0.133 +/- 0.005 | 0.289 +/- 0.008 | no | `A_s*(n_s**2 - 0.9250428)**2*log(n_s**2/A_s)/` |
|  | {omega_b, A_s} | 2 | 10 | 0.129 +/- 0.003 | 0.280 +/- 0.004 | no | `0.39432669564521*exp(2*omega_b)/A_s` |
|  | {H0, A_s} | 2 | 2 | 0.127 +/- 0.003 | 0.276 +/- 0.000 | no | `-log(1.6093085e-5*log(A_s) + 5.6511736)` |
| **S\*** | {omega_b, tau, A_s} | 3 | 17 | 1.068 +/- 0.026 | 2.314 +/- 0.034 | yes | `A_s*log(log(tau) + 8.529404 + 8.020664040682` |
|  | {omega_b, omega_cdm, tau} | 3 | 12 | 0.240 +/- 0.005 | 0.521 +/- 0.006 | no | `(-tau**4*log(omega_b)**4 + tau + 0.2760499)*` |
|  | {omega_b, tau, A_s, n_s} | 4 | 17 | 1.059 +/- 0.028 | 2.294 +/- 0.039 | yes | `A_s*(n_s - omega_b)**2*log(tau + 0.078433886` |
|  | {omega_b, omega_cdm, tau, A_s} | 4 | 17 | 1.047 +/- 0.024 | 2.269 +/- 0.025 | no | `-A_s*exp(-2*omega_b)/((tau - 0.22419287)*(-t` |
|  | {omega_cdm, H0, tau, A_s} | 4 | 17 | 1.035 +/- 0.022 | 2.241 +/- 0.016 | no | `0.0103309588329508*A_s/(((tau + 0.189403325)` |
|  | {omega_cdm, tau, A_s, n_s} | 4 | 17 | 1.035 +/- 0.033 | 2.241 +/- 0.055 | yes | `exp(tau) - log(A_s*log(-n_s*tau/(A_s*(8079.6` |
|  | {omega_b, H0, tau, A_s} | 4 | 16 | 1.022 +/- 0.032 | 2.214 +/- 0.052 | no | `-A_s*(omega_b**4*(log(tau) + 11.781949) + 5.` |
|  | {H0, tau, A_s, n_s} | 4 | 15 | 0.993 +/- 0.033 | 2.152 +/- 0.056 | no | `A_s/(log(tau*((tau - 0.0993644212953972)**2 ` |
|  | {omega_b, omega_cdm, H0, tau} | 4 | 13 | 0.240 +/- 0.005 | 0.520 +/- 0.005 | no | `(tau + (omega_cdm*tau + 0.063239954)*log((-0` |
|  | {omega_b, omega_cdm, tau, n_s} | 4 | 13 | 0.237 +/- 0.005 | 0.514 +/- 0.004 | no | `log(n_s + (0.000498020548507876*omega_cdm**2` |
|  | {omega_cdm, H0, tau, n_s} | 4 | 11 | 0.236 +/- 0.005 | 0.512 +/- 0.002 | no | `166.650000851896*(0.07746354*omega_cdm + tau` |
|  | {omega_b, omega_cdm, H0, tau, A_s} | 5 | 17 | 1.064 +/- 0.024 | 2.306 +/- 0.025 | yes | `-A_s*omega_b**2/((tau + 0.035367183)*(omega_` |
|  | {omega_cdm, H0, tau, A_s, n_s} | 5 | 17 | 1.030 +/- 0.023 | 2.230 +/- 0.021 | yes | `A_s*log((n_s + 2.0463479)/(log(-log(tau)) - ` |
|  | {omega_b, omega_cdm, H0, tau, n_s} | 5 | 12 | 0.239 +/- 0.006 | 0.518 +/- 0.006 | no | `(-omega_cdm + 29.1815565558993*tau**2)/(tau*` |
|  | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 17 | 1.000 +/- 0.000 | 2.166 +/- 0.043 | yes | `exp(omega_b + tau) + log((tau*log(-A_s**2/(t` |

Re-clustered finalist forms (Phase-2 machinery, 696 forms): top cluster rep `-A_s/(tau - 0.445426)` (c=5, support {tau, ln10As}, R_allparams=0.8).

## z5 — amplitude (A_s, tau)

Reference Î_all-6 = 3.830 +/- 0.087 nat.
**S\* = {omega_b, omega_cdm, H0, tau, A_s, n_s}** — η_S = 1.000 +/- 0.000, C_S = 20, screen-recurrent: True (per-seed minimal: s0=True, s1=True; per-seed picks agree: True).

Staircase (best η_S per support size): |S|=1: 0.098; |S|=2: 0.313; |S|=3: 0.438; |S|=4: 0.589; |S|=5: 0.746; |S|=6: 1.000.

| | S | \|S\| | C_S | η_S +/- SE | Î_S +/- SE | minimal | best form |
|---|---|---:|---:|---|---|---|---|
|  | {A_s} | 1 | 6 | 0.098 +/- 0.002 | 0.376 +/- 0.000 | no | `6.871011e-6*log(A_s) - 6.006013` |
|  | {tau} | 1 | 2 | 0.077 +/- 0.002 | 0.296 +/- 0.000 | no | `tau**2` |
|  | {tau, A_s} | 2 | 6 | 0.313 +/- 0.007 | 1.200 +/- 0.004 | no | `log(0.43541218424929*A_s**2/(tau - 0.1292972` |
|  | {omega_cdm, A_s} | 2 | 14 | 0.122 +/- 0.004 | 0.467 +/- 0.009 | no | `A_s*log(omega_cdm)` |
|  | {H0, A_s} | 2 | 4 | 0.114 +/- 0.003 | 0.435 +/- 0.007 | no | `log(H0)/A_s` |
|  | {omega_b, A_s} | 2 | 9 | 0.098 +/- 0.002 | 0.376 +/- 0.000 | no | `41.2963914447567*(0.078111039684796 + exp(-A` |
|  | {omega_b, tau} | 2 | 2 | 0.079 +/- 0.002 | 0.302 +/- 0.006 | no | `0.351968628525182*omega_b*tau**3/(0.59326944` |
|  | {H0, tau} | 2 | 2 | 0.077 +/- 0.002 | 0.296 +/- 0.000 | no | `tau**2` |
|  | {omega_cdm, tau} | 2 | 2 | 0.077 +/- 0.002 | 0.296 +/- 0.000 | no | `tau**2` |
|  | {tau, n_s} | 2 | 2 | 0.077 +/- 0.002 | 0.296 +/- 0.000 | no | `tau**2` |
|  | {omega_cdm, tau, A_s} | 3 | 16 | 0.438 +/- 0.010 | 1.676 +/- 0.002 | no | `exp(8.99932081281424*(0.333345911585731*log(` |
|  | {omega_b, omega_cdm, A_s} | 3 | 17 | 0.128 +/- 0.003 | 0.489 +/- 0.007 | no | `(A_s + 7.5001597)*(exp(A_s**0.54432831536285` |
|  | {omega_cdm, A_s, n_s} | 3 | 9 | 0.125 +/- 0.003 | 0.480 +/- 0.002 | no | `A_s*log(omega_cdm)` |
|  | {omega_cdm, tau, n_s} | 3 | 17 | 0.082 +/- 0.005 | 0.313 +/- 0.017 | no | `-0.759441946172441*log(0.55575466*omega_cdm*` |
|  | {omega_b, tau, n_s} | 3 | 2 | 0.077 +/- 0.002 | 0.296 +/- 0.000 | no | `tau**2 + 4527.2505` |
|  | {omega_b, omega_cdm, tau} | 3 | 2 | 0.077 +/- 0.002 | 0.296 +/- 0.000 | no | `tau**2` |
|  | {omega_b, H0, tau} | 3 | 2 | 0.077 +/- 0.002 | 0.296 +/- 0.000 | no | `tau**2` |
|  | {H0, tau, n_s} | 3 | 2 | 0.077 +/- 0.002 | 0.296 +/- 0.000 | no | `tau**2` |
|  | {omega_cdm, H0, tau, A_s} | 4 | 15 | 0.589 +/- 0.013 | 2.256 +/- 0.001 | no | `-4.55264875659402*exp(0.014197185/log(A_s*ex` |
|  | {omega_b, omega_cdm, A_s, n_s} | 4 | 13 | 0.127 +/- 0.003 | 0.486 +/- 0.004 | no | `-1.008317*A_s*(omega_b - omega_cdm + 0.32610` |
|  | {omega_b, omega_cdm, H0, tau} | 4 | 5 | 0.084 +/- 0.006 | 0.320 +/- 0.023 | no | `H0*(omega_cdm**2 + (omega_cdm + tau)**2)` |
|  | {omega_cdm, H0, tau, A_s, n_s} | 5 | 17 | 0.746 +/- 0.017 | 2.856 +/- 0.002 | no | `log((log(H0) + 0.4462526)*exp(2*tau + 2.7900` |
|  | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | 8 | 0.141 +/- 0.006 | 0.539 +/- 0.018 | no | `A_s*(-n_s + log(omega_cdm))/log(H0)` |
|  | {omega_b, omega_cdm, H0, tau, n_s} | 5 | 20 | 0.078 +/- 0.002 | 0.297 +/- 0.001 | no | `-3.16663601890773*n_s - 38.3510567664239*ome` |
| **S\*** | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 20 | 1.000 +/- 0.000 | 3.830 +/- 0.087 | yes | `omega_b - 0.17572255*log(exp((2*n_s*tau + 2.` |

Re-clustered finalist forms (Phase-2 machinery, 265 forms): top cluster rep `A_s*exp(-2*tau)` (c=5, support {tau, ln10As}, R_allparams=0.8).


# Gate G2

| latent | role | S* | η_S | screen-recurrent | verdict |
|---|---|---|---|---|---|
| z0 | shape | {A_s, H0, n_s, omega_b, omega_cdm, tau} | 1.000 | True | **PASS** |
| z1 | shape | {A_s, H0, n_s, omega_b, omega_cdm, tau} | 1.000 | True | **PASS** |
| z2 | shape | {A_s, n_s, omega_b, omega_cdm} | 0.995 | True | **PASS** |
| z3 | shape | {H0, n_s, omega_b, omega_cdm} | 0.992 | False | **ATTENTION (not screen-recurrent)** |
| z4 | shape | {A_s, omega_b, tau} | 1.068 | False | **ATTENTION (not screen-recurrent)** |
| z5 | amplitude | {A_s, H0, n_s, omega_b, omega_cdm, tau} | 1.000 | True | **PASS (superset finding)** |

**Overall: PARTIAL (z3, z4 flagged)**
