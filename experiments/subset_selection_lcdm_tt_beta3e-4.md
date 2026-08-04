# Blind subset selection — `lcdm_tt_beta3e-4` (roadmap Phase 4, screen 4a)

All 63 non-empty input subsets x 2 seeds per latent at the reduced screen budget (ni100, maxsize 20). Per subset: Î_S (across-seed mean front-max val MI), its one-SE knee C_S, and within-screen sufficiency η̃_S = Î_S / Î_all-6 at the SAME budget. Finalists = Pareto frontier of (|S|, C_S, −η̃_S) plus subsets non-dominated when credited one SE of their η̃; finalists go to the 4b full-protocol rerun (ni200, 5 seeds). Gate G2 is judged on 4b, not on this screen.

_Screen coverage: 630/630 reports present._


## z0 — omega_b

In-screen reference Î_all-6 = 3.311 +/- 0.199 nat (63 subsets scored, 18 finalists).

Staircase (best η̃ per support size): |S|=1: 0.275; |S|=2: 0.403; |S|=3: 0.639; |S|=4: 0.840; |S|=5: 1.002; |S|=6: 1.000.

| finalist | S | \|S\| | C_S | η̃ +/- SE | Î_S | best screen form |
|---|---|---:|---:|---|---:|---|
| frontier | {omega_b} | 1 | 2 | 0.275 +/- 0.017 | 0.911 | `log(omega_b)` |
| frontier | {n_s} | 1 | 1 | 0.015 +/- 0.001 | 0.049 | `n_s` |
| frontier | {omega_b, n_s} | 2 | 6 | 0.403 +/- 0.024 | 1.336 | `(omega_b - 0.008396179)*exp(-n_s)` |
| frontier | {omega_b, A_s} | 2 | 2 | 0.276 +/- 0.017 | 0.913 | `(-2.34074139753544*omega_b - 75.776715929051` |
| 1-SE keep | {omega_b, tau} | 2 | 2 | 0.275 +/- 0.017 | 0.911 | `log(omega_b)` |
| frontier | {omega_b, omega_cdm, n_s} | 3 | 18 | 0.639 +/- 0.038 | 2.116 | `4.48270394725609*(0.472313078202718*n_s - 0.` |
| frontier | {omega_b, H0, n_s} | 3 | 17 | 0.443 +/- 0.027 | 1.468 | `log(-H0 + 0.25499480189401*n_s/omega_b**2 + ` |
| frontier | {omega_b, A_s, n_s} | 3 | 8 | 0.409 +/- 0.025 | 1.356 | `-omega_b/(n_s*log(A_s) - 13.968324)` |
| frontier | {omega_b, tau, n_s} | 3 | 6 | 0.403 +/- 0.024 | 1.336 | `(omega_b - 0.008386334)*exp(-n_s)` |
| 1-SE keep | {omega_b, tau, A_s} | 3 | 2 | 0.275 +/- 0.017 | 0.911 | `log(omega_b)` |
| frontier | {omega_b, omega_cdm, H0, n_s} | 4 | 16 | 0.840 +/- 0.051 | 2.781 | `log(log(-H0 + exp(omega_cdm)/omega_cdm**2 - ` |
| frontier | {omega_b, omega_cdm, A_s, n_s} | 4 | 12 | 0.664 +/- 0.040 | 2.200 | `(omega_b*(omega_cdm + 0.5513558) - 2.2550416` |
| frontier | {omega_b, omega_cdm, tau, n_s} | 4 | 9 | 0.635 +/- 0.038 | 2.103 | `4849.76774354229*omega_cdm*(0.014359507*n_s ` |
| frontier | {omega_b, tau, A_s, n_s} | 4 | 8 | 0.412 +/- 0.025 | 1.364 | `omega_b*(n_s - 2.6000133)/log(A_s)` |
| frontier | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | 20 | 1.002 +/- 0.061 | 3.318 | `-omega_cdm + log((log(A_s) - 2.9048544475877` |
| frontier | {omega_b, omega_cdm, H0, tau, n_s} | 5 | 17 | 0.852 +/- 0.052 | 2.823 | `omega_b*omega_cdm*(n_s + 2.217867)/(n_s*omeg` |
| frontier | {omega_b, omega_cdm, tau, A_s, n_s} | 5 | 11 | 0.663 +/- 0.041 | 2.196 | `omega_b/(n_s*log(A_s) + 5.455205*log(omega_c` |
| frontier | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 15 | 1.000 +/- 0.085 | 3.311 | `log((-0.00896427565828934*n_s*log(H0) + omeg` |

## z1 — omega_cdm

In-screen reference Î_all-6 = 2.236 +/- 0.061 nat (63 subsets scored, 12 finalists).

Staircase (best η̃ per support size): |S|=1: 0.123; |S|=2: 0.244; |S|=3: 0.406; |S|=4: 0.540; |S|=5: 0.861; |S|=6: 1.000.

| finalist | S | \|S\| | C_S | η̃ +/- SE | Î_S | best screen form |
|---|---|---:|---:|---|---:|---|
| frontier | {omega_cdm} | 1 | 1 | 0.123 +/- 0.003 | 0.274 | `omega_cdm` |
| frontier | {omega_cdm, H0} | 2 | 19 | 0.244 +/- 0.007 | 0.546 | `7.86956736470245e+17*exp(-22.5637403962018*o` |
| frontier | {omega_cdm, n_s} | 2 | 4 | 0.202 +/- 0.006 | 0.451 | `(0.148601463580864*n_s**2 - omega_cdm)**2/n_` |
| frontier | {omega_cdm, H0, n_s} | 3 | 15 | 0.406 +/- 0.012 | 0.909 | `-1.23476627158602*exp(-0.000138774521965582*` |
| frontier | {omega_cdm, H0, A_s} | 3 | 8 | 0.283 +/- 0.008 | 0.634 | `((omega_cdm - 0.2326288)*(-H0 + omega_cdm + ` |
| frontier | {omega_cdm, A_s, n_s} | 3 | 7 | 0.246 +/- 0.007 | 0.550 | `A_s*omega_cdm**2/n_s**4` |
| frontier | {omega_b, omega_cdm, H0, n_s} | 4 | 17 | 0.540 +/- 0.016 | 1.207 | `(-n_s*omega_cdm + omega_b*(-H0*n_s**2 + omeg` |
| frontier | {omega_cdm, H0, A_s, n_s} | 4 | 14 | 0.509 +/- 0.014 | 1.138 | `omega_cdm - log(H0**2*(0.890659440687247*n_s` |
| frontier | {omega_cdm, H0, tau, n_s} | 4 | 13 | 0.435 +/- 0.012 | 0.974 | `(-n_s**2*(H0 + 13.549342) + omega_cdm*(-n_s ` |
| frontier | {omega_b, omega_cdm, H0, A_s} | 4 | 10 | 0.376 +/- 0.011 | 0.841 | `exp(-4*omega_cdm - 4*(0.48309177 - omega_b)*` |
| frontier | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | 16 | 0.861 +/- 0.025 | 1.924 | `log((0.143171301598937*H0 + 1)**2*(n_s - ome` |
| frontier | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 19 | 1.000 +/- 0.039 | 2.236 | `n_s - exp(tau) + log(H0**2*n_s**4*omega_b/(A` |
|  | {omega_cdm, H0, tau, A_s, n_s} | 5 | 19 | 0.581 +/- 0.016 | 1.299 | `(-omega_cdm + exp(tau) + log(A_s*omega_cdm**` |
|  | {omega_b, omega_cdm, H0, tau, n_s} | 5 | 17 | 0.569 +/- 0.016 | 1.273 | `n_s**2*(-omega_b*(H0 - 13.277359) + tau - 0.` |

## z2 — amplitude (A_s, tau)

In-screen reference Î_all-6 = 3.298 +/- 0.393 nat (63 subsets scored, 21 finalists).

Staircase (best η̃ per support size): |S|=1: 0.097; |S|=2: 0.249; |S|=3: 0.352; |S|=4: 0.579; |S|=5: 0.721; |S|=6: 1.000.

| finalist | S | \|S\| | C_S | η̃ +/- SE | Î_S | best screen form |
|---|---|---:|---:|---|---:|---|
| frontier | {A_s} | 1 | 11 | 0.097 +/- 0.012 | 0.320 | `-1.5150065 + 1.1721553/log(2*A_s)**4` |
| frontier | {tau} | 1 | 2 | 0.074 +/- 0.009 | 0.245 | `tau**2` |
| frontier | {tau, A_s} | 2 | 17 | 0.249 +/- 0.030 | 0.822 | `log(log((9.29960136858074e-14/(tau**2 - 0.00` |
| frontier | {omega_cdm, A_s} | 2 | 4 | 0.134 +/- 0.016 | 0.443 | `A_s*log(omega_cdm)` |
| 1-SE keep | {H0, A_s} | 2 | 11 | 0.129 +/- 0.015 | 0.426 | `exp(0.00047466482/log(A_s/log(log(log(H0))))` |
| 1-SE keep | {omega_b, tau} | 2 | 2 | 0.074 +/- 0.009 | 0.245 | `tau**2` |
| 1-SE keep | {tau, n_s} | 2 | 2 | 0.074 +/- 0.009 | 0.245 | `tau**2` |
| frontier | {omega_cdm, tau, A_s} | 3 | 8 | 0.352 +/- 0.042 | 1.160 | `-A_s*(tau - 0.57426715)*log(omega_cdm)` |
| 1-SE keep | {H0, tau, A_s} | 3 | 15 | 0.345 +/- 0.041 | 1.138 | `A_s*(tau - 0.5840776)/(0.12401262*H0 + 11.50` |
| frontier | {tau, A_s, n_s} | 3 | 7 | 0.256 +/- 0.031 | 0.843 | `-A_s*(n_s*(tau - 0.2952891) - 0.2966003)` |
| frontier | {omega_cdm, H0, A_s} | 3 | 6 | 0.181 +/- 0.022 | 0.596 | `A_s*(H0*(0.28289446 - omega_cdm) + 8.938494)` |
| frontier | {omega_cdm, H0, tau, A_s} | 4 | 19 | 0.579 +/- 0.069 | 1.910 | `log(log(exp(3.73897177089241*(omega_cdm + 0.` |
| frontier | {omega_cdm, tau, A_s, n_s} | 4 | 12 | 0.380 +/- 0.046 | 1.254 | `A_s*exp(-2*(n_s*tau + 2*omega_cdm)/n_s)` |
| 1-SE keep | {omega_b, H0, tau, A_s} | 4 | 13 | 0.374 +/- 0.045 | 1.232 | `A_s*(H0*omega_b + 0.22174291*H0*(0.25969103 ` |
| 1-SE keep | {H0, tau, A_s, n_s} | 4 | 15 | 0.372 +/- 0.044 | 1.228 | `A_s*(-0.0134906362460507*H0*tau + 0.50173273` |
| 1-SE keep | {omega_b, omega_cdm, tau, A_s} | 4 | 15 | 0.366 +/- 0.044 | 1.207 | `(-2.6554112*omega_b + omega_cdm*exp(exp(1.30` |
| frontier | {omega_cdm, H0, tau, A_s, n_s} | 5 | 17 | 0.721 +/- 0.086 | 2.378 | `-2*omega_cdm + (tau + 10.426105)*log(log(ome` |
| 1-SE keep | {omega_b, omega_cdm, H0, tau, A_s} | 5 | 18 | 0.707 +/- 0.084 | 2.330 | `log((5.4159436*omega_b - tau - 10.592033)*lo` |
| frontier | {omega_b, omega_cdm, tau, A_s, n_s} | 5 | 14 | 0.421 +/- 0.050 | 1.387 | `0.0259643154791886*A_s*exp(-2*tau)*log(n_s/o` |
| 1-SE keep | {omega_b, H0, tau, A_s, n_s} | 5 | 16 | 0.417 +/- 0.050 | 1.376 | `A_s*exp(4*omega_b*exp(n_s**2) - 2*tau)/log(H` |
| frontier | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 19 | 1.000 +/- 0.169 | 3.298 | `log(log((H0*omega_cdm + n_s)/(A_s**2*n_s*(om` |

## z3 — n_s

In-screen reference Î_all-6 = 3.042 +/- 0.002 nat (63 subsets scored, 18 finalists).

Staircase (best η̃ per support size): |S|=1: 0.180; |S|=2: 0.578; |S|=3: 0.728; |S|=4: 0.983; |S|=5: 1.005; |S|=6: 1.000.

| finalist | S | \|S\| | C_S | η̃ +/- SE | Î_S | best screen form |
|---|---|---:|---:|---|---:|---|
| frontier | {n_s} | 1 | 2 | 0.180 +/- 0.000 | 0.548 | `-1.44969544174554*exp(-1.3980745*exp(0.00032` |
| frontier | {A_s} | 1 | 1 | 0.008 +/- 0.000 | 0.025 | `-2.2324676468984*A_s - 0.0102352999999999` |
| frontier | {omega_cdm, n_s} | 2 | 5 | 0.578 +/- 0.000 | 1.758 | `1.0617761540153*(4.4374533*n_s + log(omega_c` |
| frontier | {H0, n_s} | 2 | 2 | 0.188 +/- 0.008 | 0.571 | `log(385.0622 + (0.9181854 - n_s)/H0)` |
| 1-SE keep | {tau, n_s} | 2 | 2 | 0.185 +/- 0.005 | 0.563 | `(log((exp(2*exp(2*exp(-n_s**2 + 0.6933911*ta` |
| frontier | {omega_b, omega_cdm, n_s} | 3 | 18 | 0.728 +/- 0.002 | 2.215 | `log((0.191762643869924*n_s + 0.1917626438699` |
| frontier | {omega_cdm, H0, n_s} | 3 | 10 | 0.662 +/- 0.002 | 2.013 | `log((omega_cdm + 1.2863992/H0)*exp(3.7931411` |
| 1-SE keep | {omega_cdm, A_s, n_s} | 3 | 5 | 0.578 +/- 0.000 | 1.758 | `(A_s + 0.0237129952955877*exp(-exp(-0.000142` |
| frontier | {H0, tau, n_s} | 3 | 4 | 0.198 +/- 0.018 | 0.601 | `n_s*exp(-exp((-2.0334446*tau*(H0 - n_s + tau` |
| frontier | {tau, A_s, n_s} | 3 | 2 | 0.191 +/- 0.011 | 0.581 | `exp(0.0995203128193966*n_s**19324.6434539345` |
| frontier | {omega_b, omega_cdm, H0, n_s} | 4 | 17 | 0.983 +/- 0.002 | 2.990 | `-0.27419615*n_s - omega_b + 0.059806615/(ome` |
| frontier | {omega_b, omega_cdm, tau, n_s} | 4 | 12 | 0.734 +/- 0.005 | 2.233 | `-tau + log(omega_cdm)/(n_s**2*(omega_b + 0.2` |
| frontier | {omega_b, omega_cdm, A_s, n_s} | 4 | 9 | 0.727 +/- 0.002 | 2.211 | `(-n_s*omega_b*(omega_cdm + 0.38178703) + 0.0` |
| 1-SE keep | {H0, tau, A_s, n_s} | 4 | 2 | 0.188 +/- 0.008 | 0.571 | `(n_s - 0.9182062)/H0` |
| frontier | {omega_b, omega_cdm, H0, tau, n_s} | 5 | 20 | 1.005 +/- 0.008 | 3.057 | `(H0*(log(omega_b) - 11.87361) - 1.5343687867` |
| 1-SE keep | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | 17 | 0.983 +/- 0.008 | 2.989 | `-log(9.6807436211929e-5/omega_b**2 + 2.40355` |
| 1-SE keep | {omega_b, omega_cdm, tau, A_s, n_s} | 5 | 16 | 0.732 +/- 0.003 | 2.227 | `tau**2 - 2.04258933575955*log(n_s**4*(omega_` |
| frontier | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 18 | 1.000 +/- 0.001 | 3.042 | `(H0*omega_b + 0.56592214*n_s*(H0*(omega_cdm ` |
|  | {omega_cdm, tau, n_s} | 3 | 15 | 0.585 +/- 0.001 | 1.779 | `2.39699777027925*exp(2.11449696431153e-5*(-t` |
|  | {omega_cdm, H0, tau, n_s} | 4 | 19 | 0.670 +/- 0.001 | 2.038 | `(tau - exp(tau) + log(257.249648822073*n_s +` |
|  | {omega_cdm, H0, A_s, n_s} | 4 | 11 | 0.663 +/- 0.002 | 2.017 | `log(n_s + log(omega_cdm + 0.36986372 + 1.285` |
|  | {omega_cdm, tau, A_s, n_s} | 4 | 17 | 0.587 +/- 0.002 | 1.786 | `((n_s + 2*omega_cdm)**2*(n_s**4 + log(A_s)) ` |
|  | {omega_cdm, H0, tau, A_s, n_s} | 5 | 12 | 0.666 +/- 0.003 | 2.026 | `log(n_s + 2*omega_cdm - 9.66076606397012*(ta` |

## z4 — H0

In-screen reference Î_all-6 = 3.647 +/- 0.123 nat (63 subsets scored, 12 finalists).

Staircase (best η̃ per support size): |S|=1: 0.139; |S|=2: 0.195; |S|=3: 0.278; |S|=4: 0.379; |S|=5: 0.625; |S|=6: 1.000.

| finalist | S | \|S\| | C_S | η̃ +/- SE | Î_S | best screen form |
|---|---|---:|---:|---|---:|---|
| frontier | {H0} | 1 | 3 | 0.139 +/- 0.005 | 0.508 | `log(H0)*log(exp(0.00115401322600837/H0**2))/` |
| frontier | {omega_cdm, H0} | 2 | 5 | 0.195 +/- 0.007 | 0.712 | `H0 - 3.3344421/omega_cdm` |
| frontier | {omega_cdm, H0, A_s} | 3 | 15 | 0.278 +/- 0.009 | 1.014 | `(1.3840696 - 0.38210055*log(H0))/(A_s*H0**4*` |
| frontier | {omega_cdm, H0, tau} | 3 | 12 | 0.243 +/- 0.008 | 0.888 | `log((3.3013034 - tau)*log(95.176277523889*om` |
| frontier | {H0, tau, A_s} | 3 | 9 | 0.224 +/- 0.008 | 0.817 | `H0 - 5.54117606447268e-8*exp(2*tau)/A_s` |
| frontier | {omega_b, omega_cdm, H0} | 3 | 7 | 0.218 +/- 0.007 | 0.795 | `-omega_b/(omega_cdm*(H0 - 41.721355))` |
| frontier | {omega_cdm, H0, n_s} | 3 | 6 | 0.199 +/- 0.007 | 0.724 | `log(n_s/omega_cdm)/H0` |
| frontier | {omega_cdm, H0, tau, A_s} | 4 | 20 | 0.379 +/- 0.013 | 1.382 | `(log(H0 - 1.37539757884061e-7*exp(2*tau)/(A_` |
| frontier | {omega_b, omega_cdm, H0, A_s} | 4 | 14 | 0.346 +/- 0.012 | 1.263 | `-omega_b + omega_cdm + log(A_s*omega_cdm/(om` |
| frontier | {omega_b, omega_cdm, H0, tau} | 4 | 10 | 0.298 +/- 0.010 | 1.087 | `exp(-(H0*omega_b*(tau + 0.47014457) - log(om` |
| frontier | {omega_b, omega_cdm, H0, tau, A_s} | 5 | 17 | 0.625 +/- 0.022 | 2.280 | `log(-H0**2 + H0/omega_cdm + omega_b*exp(2*ta` |
| frontier | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 20 | 1.000 +/- 0.048 | 3.647 | `n_s - omega_cdm - log(A_s*H0**2*omega_cdm*(H` |

---
_Generated by `scripts/consolidate_subsets.py` from `hpsweep_subsets_v1`._


# 4b finals — full protocol (ni200 x 5 seeds)

_Finals coverage: 380/380 reports. Reference = `allparams` (full-protocol all-6, 5 seeds). S* = smallest |S| (ties: smaller knee C) whose Î_S is within one combined SE of every measured superset; recurrence = the same minimality holds in each 4a screen seed separately._


## z0 — omega_b

Reference Î_all-6 = 3.337 +/- 0.024 nat.
**S\* = {omega_b, omega_cdm, H0, A_s, n_s}** — η_S = 1.003 +/- 0.020, C_S = 19, screen-recurrent: False (per-seed minimal: s0=False, s1=True; per-seed picks agree: False).

Staircase (best η_S per support size): |S|=1: 0.273; |S|=2: 0.400; |S|=3: 0.630; |S|=4: 0.835; |S|=5: 1.003; |S|=6: 1.000.

| | S | \|S\| | C_S | η_S +/- SE | Î_S +/- SE | minimal | best form |
|---|---|---:|---:|---|---|---|---|
|  | {omega_b} | 1 | 2 | 0.273 +/- 0.002 | 0.911 +/- 0.000 | no | `log(omega_b)` |
|  | {n_s} | 1 | 9 | 0.021 +/- 0.003 | 0.072 +/- 0.010 | no | `-n_s*(n_s - 0.9839874)/(159595.72*n_s - 1570` |
|  | {omega_b, n_s} | 2 | 7 | 0.400 +/- 0.003 | 1.335 +/- 0.003 | no | `(609.5965*n_s + omega_b + 350.3551033152)/(n` |
|  | {omega_b, A_s} | 2 | 2 | 0.273 +/- 0.002 | 0.911 +/- 0.000 | no | `log(omega_b)` |
|  | {omega_b, tau} | 2 | 2 | 0.273 +/- 0.002 | 0.911 +/- 0.000 | no | `log(omega_b)` |
|  | {omega_b, omega_cdm, n_s} | 3 | 11 | 0.630 +/- 0.005 | 2.102 +/- 0.005 | no | `omega_b*omega_cdm**2/(3.55682418197613*omega` |
|  | {omega_b, H0, n_s} | 3 | 13 | 0.438 +/- 0.004 | 1.462 +/- 0.005 | no | `log(-H0 + 0.08971138*(n_s + 0.6861281)**2/om` |
|  | {omega_b, A_s, n_s} | 3 | 11 | 0.409 +/- 0.003 | 1.364 +/- 0.001 | no | `exp(-omega_b/(n_s*log(A_s) - 13.440298))` |
|  | {omega_b, tau, n_s} | 3 | 10 | 0.401 +/- 0.003 | 1.337 +/- 0.001 | no | `12.3858787654462*omega_b/log(0.18626378/n_s)` |
|  | {omega_b, tau, A_s} | 3 | 2 | 0.273 +/- 0.002 | 0.911 +/- 0.000 | no | `log(exp(exp(0.569928748328717*exp(4.35936975` |
|  | {omega_b, omega_cdm, H0, n_s} | 4 | 14 | 0.835 +/- 0.008 | 2.787 +/- 0.018 | no | `-1.9012555/log(-0.0056098355*H0/omega_cdm - ` |
|  | {omega_b, omega_cdm, A_s, n_s} | 4 | 13 | 0.664 +/- 0.005 | 2.216 +/- 0.003 | no | `-omega_b/((n_s + 0.59309566)*(log(A_s) - log` |
|  | {omega_b, omega_cdm, tau, n_s} | 4 | 12 | 0.633 +/- 0.005 | 2.112 +/- 0.003 | no | `exp(-0.09903916*omega_b**2/(-0.24773481*n_s*` |
|  | {omega_b, tau, A_s, n_s} | 4 | 10 | 0.408 +/- 0.003 | 1.361 +/- 0.001 | no | `omega_b/(n_s*log(A_s) - 13.969693)` |
| **S\*** | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | 19 | 1.003 +/- 0.020 | 3.347 +/- 0.063 | yes | `log(log(n_s*(log(A_s) - log(omega_b))*(H0 - ` |
|  | {omega_b, omega_cdm, H0, tau, n_s} | 5 | 18 | 0.834 +/- 0.006 | 2.782 +/- 0.006 | no | `omega_b*(tau*(n_s + 0.54691976) + 83.66754*e` |
|  | {omega_b, omega_cdm, tau, A_s, n_s} | 5 | 15 | 0.666 +/- 0.005 | 2.224 +/- 0.006 | no | `log((-0.009269168*n_s + omega_b*omega_cdm - ` |
|  | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 19 | 1.000 +/- 0.000 | 3.337 +/- 0.024 | yes | `log(n_s*(omega_b*(tau**2 + log(H0)) + 0.4207` |

Re-clustered finalist forms (Phase-2 machinery, 880 forms): top cluster rep `n_s/omega_b` (c=3, support {omega_b, n_s}, R_allparams=0.8).

## z1 — omega_cdm

Reference Î_all-6 = 2.334 +/- 0.005 nat.
**S\* = {omega_b, omega_cdm, H0, tau, A_s, n_s}** — η_S = 1.000 +/- 0.000, C_S = 20, screen-recurrent: True (per-seed minimal: s0=True, s1=True; per-seed picks agree: True).

Staircase (best η_S per support size): |S|=1: 0.120; |S|=2: 0.235; |S|=3: 0.385; |S|=4: 0.514; |S|=5: 0.824; |S|=6: 1.000.

| | S | \|S\| | C_S | η_S +/- SE | Î_S +/- SE | minimal | best form |
|---|---|---:|---:|---|---|---|---|
|  | {omega_cdm} | 1 | 15 | 0.120 +/- 0.002 | 0.281 +/- 0.004 | no | `1.2657905*omega_cdm + 34847.3071522114*(0.01` |
|  | {omega_cdm, H0} | 2 | 15 | 0.235 +/- 0.001 | 0.548 +/- 0.002 | no | `-omega_cdm + 60322.683244926 - 493.797503445` |
|  | {omega_cdm, n_s} | 2 | 11 | 0.194 +/- 0.001 | 0.454 +/- 0.002 | no | `log(n_s/omega_cdm - 5.852781/n_s)**2` |
|  | {omega_cdm, H0, n_s} | 3 | 13 | 0.385 +/- 0.001 | 0.899 +/- 0.002 | no | `1518.7882*n_s**2/omega_cdm + (H0 + exp(n_s))` |
|  | {omega_cdm, H0, A_s} | 3 | 9 | 0.271 +/- 0.001 | 0.633 +/- 0.002 | no | `exp(A_s*H0*(omega_cdm - 1)/(omega_cdm*(log(A` |
|  | {omega_cdm, A_s, n_s} | 3 | 13 | 0.236 +/- 0.001 | 0.552 +/- 0.001 | no | `log(log(((n_s - 0.66611344)/(omega_cdm - 0.0` |
|  | {omega_b, omega_cdm, H0, n_s} | 4 | 15 | 0.514 +/- 0.002 | 1.200 +/- 0.003 | no | `H0*(-n_s**2 + omega_b + 1.5324805*omega_cdm)` |
|  | {omega_cdm, H0, A_s, n_s} | 4 | 19 | 0.499 +/- 0.002 | 1.164 +/- 0.003 | no | `exp(2*log(log((H0*(n_s - omega_cdm)**2 - 27.` |
|  | {omega_cdm, H0, tau, n_s} | 4 | 14 | 0.417 +/- 0.001 | 0.974 +/- 0.002 | no | `H0*(-n_s**2 + omega_cdm*exp(3.07667381901029` |
|  | {omega_b, omega_cdm, H0, A_s} | 4 | 10 | 0.358 +/- 0.002 | 0.834 +/- 0.003 | no | `log((omega_b*(H0 - 33.75204) + 6.7582*(omega` |
|  | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | 17 | 0.824 +/- 0.006 | 1.923 +/- 0.012 | no | `-1.2091329/(log(omega_b*(0.316690568359496*H` |
| **S\*** | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 20 | 1.000 +/- 0.000 | 2.334 +/- 0.005 | yes | `-tau + log(H0**2*omega_b*exp(2*exp(n_s))/(A_` |

Re-clustered finalist forms (Phase-2 machinery, 366 forms): top cluster rep `H0*n_s**2/omega_cdm` (c=6, support {omega_cdm, H0, n_s}, R_allparams=0.8).

## z2 — amplitude (A_s, tau)

Reference Î_all-6 = 3.843 +/- 0.055 nat.
**S\* = {omega_b, omega_cdm, H0, tau, A_s, n_s}** — η_S = 1.000 +/- 0.000, C_S = 19, screen-recurrent: True (per-seed minimal: s0=True, s1=True; per-seed picks agree: True).

Staircase (best η_S per support size): |S|=1: 0.083; |S|=2: 0.214; |S|=3: 0.299; |S|=4: 0.499; |S|=5: 0.619; |S|=6: 1.000.

| | S | \|S\| | C_S | η_S +/- SE | Î_S +/- SE | minimal | best form |
|---|---|---:|---:|---|---|---|---|
|  | {A_s} | 1 | 8 | 0.083 +/- 0.001 | 0.320 +/- 0.003 | no | `-3.5091463e-5*log(-log(A_s)) - 1.71274320225` |
|  | {tau} | 1 | 2 | 0.064 +/- 0.001 | 0.245 +/- 0.000 | no | `tau**2` |
|  | {tau, A_s} | 2 | 5 | 0.214 +/- 0.003 | 0.823 +/- 0.002 | no | `A_s*(tau - 0.024579916)**2/(A_s + (tau - 0.0` |
|  | {omega_cdm, A_s} | 2 | 10 | 0.115 +/- 0.002 | 0.443 +/- 0.000 | no | `-log(omega_cdm - 0.29198268*log(A_s) + 18044` |
|  | {H0, A_s} | 2 | 9 | 0.112 +/- 0.002 | 0.431 +/- 0.004 | no | `log(H0 - 22.374554)/A_s` |
|  | {omega_b, tau} | 2 | 13 | 0.065 +/- 0.001 | 0.249 +/- 0.002 | no | `tau*(1.3587387*omega_b*(tau - 0.017220784) +` |
|  | {tau, n_s} | 2 | 2 | 0.064 +/- 0.001 | 0.245 +/- 0.000 | no | `tau + (tau - 6.5895e-5/(tau - 0.02800559))**` |
|  | {omega_cdm, tau, A_s} | 3 | 8 | 0.299 +/- 0.005 | 1.151 +/- 0.006 | no | `A_s*(tau - 0.5744104)*log(omega_cdm)` |
|  | {H0, tau, A_s} | 3 | 15 | 0.297 +/- 0.005 | 1.141 +/- 0.006 | no | `-5.53001701530935*A_s*exp(-(tau + log(log(H0` |
|  | {tau, A_s, n_s} | 3 | 13 | 0.225 +/- 0.003 | 0.864 +/- 0.001 | no | `A_s*(n_s + exp(A_s/(tau - 0.1292945)**2))*ex` |
|  | {omega_cdm, H0, A_s} | 3 | 14 | 0.155 +/- 0.002 | 0.594 +/- 0.001 | no | `2.75907161205555*exp(0.0985992689594882/log(` |
|  | {omega_cdm, H0, tau, A_s} | 4 | 14 | 0.499 +/- 0.007 | 1.920 +/- 0.004 | no | `106.349821886025*(0.096968709651926*tau + 1)` |
|  | {omega_cdm, tau, A_s, n_s} | 4 | 10 | 0.324 +/- 0.005 | 1.244 +/- 0.005 | no | `A_s*exp(-2*tau)*log(omega_cdm/n_s)` |
|  | {omega_b, H0, tau, A_s} | 4 | 17 | 0.320 +/- 0.005 | 1.231 +/- 0.001 | no | `0.49686998*A_s*exp(-2*tau + 9.217652*exp(ome` |
|  | {H0, tau, A_s, n_s} | 4 | 17 | 0.320 +/- 0.005 | 1.228 +/- 0.001 | no | `0.0928945240831609*(1.20169968745718e-7*n_s*` |
|  | {omega_b, omega_cdm, tau, A_s} | 4 | 14 | 0.314 +/- 0.005 | 1.209 +/- 0.010 | no | `A_s*exp(-2*tau)*log(omega_cdm)/log(omega_b)` |
|  | {omega_cdm, H0, tau, A_s, n_s} | 5 | 17 | 0.619 +/- 0.009 | 2.381 +/- 0.007 | no | `108.546830053561*(0.0959823607456716*tau + 1` |
|  | {omega_b, omega_cdm, H0, tau, A_s} | 5 | 18 | 0.602 +/- 0.009 | 2.314 +/- 0.010 | no | `log(log(-(omega_b - 0.068843)*(H0*omega_cdm ` |
|  | {omega_b, omega_cdm, tau, A_s, n_s} | 5 | 15 | 0.360 +/- 0.005 | 1.385 +/- 0.006 | no | `A_s*exp(-(n_s*(-9.12020027230182*omega_b + 2` |
|  | {omega_b, H0, tau, A_s, n_s} | 5 | 12 | 0.326 +/- 0.029 | 1.254 +/- 0.108 | no | `A_s*exp(-2*tau)/((omega_b - 0.12984979)*log(` |
| **S\*** | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 19 | 1.000 +/- 0.000 | 3.843 +/- 0.055 | yes | `log((H0*omega_cdm + 0.72941446)*exp(-n_s + 4` |

Re-clustered finalist forms (Phase-2 machinery, 537 forms): top cluster rep `log(H0*(omega_cdm + tau))/A_s` (c=8, support {omega_cdm, H0, tau, ln10As}, R_allparams=0.6).

## z3 — n_s

Reference Î_all-6 = 3.064 +/- 0.010 nat.
**S\* = {omega_b, omega_cdm, H0, tau, n_s}** — η_S = 0.997 +/- 0.005, C_S = 19, screen-recurrent: True (per-seed minimal: s0=True, s1=True; per-seed picks agree: True).

Staircase (best η_S per support size): |S|=1: 0.179; |S|=2: 0.574; |S|=3: 0.725; |S|=4: 0.975; |S|=5: 0.997; |S|=6: 1.000.

| | S | \|S\| | C_S | η_S +/- SE | Î_S +/- SE | minimal | best form |
|---|---|---:|---:|---|---|---|---|
|  | {n_s} | 1 | 7 | 0.179 +/- 0.001 | 0.548 +/- 0.000 | no | `2.26354738078266*exp(-5.359835e-5*exp(-n_s))` |
|  | {A_s} | 1 | 10 | 0.008 +/- 0.000 | 0.025 +/- 0.000 | no | `-3.94632249814609*(A_s + 0.00108626425534677` |
|  | {omega_cdm, n_s} | 2 | 15 | 0.574 +/- 0.002 | 1.760 +/- 0.001 | no | `exp((n_s + omega_cdm)**2)*log(4.5259075*n_s ` |
|  | {H0, n_s} | 2 | 5 | 0.185 +/- 0.004 | 0.568 +/- 0.011 | no | `0.000153517274378945*H0/(0.0123902088109501*` |
|  | {tau, n_s} | 2 | 4 | 0.181 +/- 0.002 | 0.556 +/- 0.005 | no | `-4.34422534359579*(0.770185325073661*log(0.6` |
|  | {omega_b, omega_cdm, n_s} | 3 | 18 | 0.725 +/- 0.003 | 2.223 +/- 0.006 | no | `-omega_b**4 + 0.07082517 + 0.000314219230012` |
|  | {omega_cdm, H0, n_s} | 3 | 12 | 0.660 +/- 0.002 | 2.021 +/- 0.003 | no | `log(227.438762831329*n_s**2*(0.0663082792583` |
|  | {omega_cdm, A_s, n_s} | 3 | 13 | 0.577 +/- 0.002 | 1.769 +/- 0.004 | no | `-exp(exp(-0.11377507*log(-omega_cdm/(n_s**2 ` |
|  | {H0, tau, n_s} | 3 | 18 | 0.196 +/- 0.005 | 0.601 +/- 0.015 | no | `0.40121186*log(exp((0.0044544354*n_s - 0.004` |
|  | {tau, A_s, n_s} | 3 | 2 | 0.179 +/- 0.001 | 0.548 +/- 0.001 | no | `(-8.5201961451395*n_s + (1.63324380217459*n_` |
|  | {omega_b, omega_cdm, H0, n_s} | 4 | 17 | 0.975 +/- 0.005 | 2.987 +/- 0.014 | no | `n_s + 1.9523982*omega_cdm - exp(28.082127931` |
|  | {omega_b, omega_cdm, tau, n_s} | 4 | 14 | 0.723 +/- 0.004 | 2.215 +/- 0.010 | no | `log(omega_cdm*exp(4.427859*n_s)/(tau - 5.093` |
|  | {omega_b, omega_cdm, A_s, n_s} | 4 | 15 | 0.719 +/- 0.003 | 2.203 +/- 0.007 | no | `47.861794*(0.0208934917901322*(n_s + omega_b` |
|  | {H0, tau, A_s, n_s} | 4 | 5 | 0.190 +/- 0.005 | 0.583 +/- 0.015 | no | `4.13569309525967*exp(0.5990084*(n_s - 0.9119` |
| **S\*** | {omega_b, omega_cdm, H0, tau, n_s} | 5 | 19 | 0.997 +/- 0.005 | 3.055 +/- 0.012 | yes | `H0*(omega_cdm + (n_s - tau**3)*(omega_cdm + ` |
|  | {omega_b, omega_cdm, H0, A_s, n_s} | 5 | 19 | 0.983 +/- 0.004 | 3.012 +/- 0.007 | no | `exp(omega_b) + log(-log((H0*(omega_b + 0.003` |
|  | {omega_b, omega_cdm, tau, A_s, n_s} | 5 | 19 | 0.729 +/- 0.003 | 2.234 +/- 0.007 | no | `10.643872594646*(0.306513894550781*tau**2 - ` |
|  | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 20 | 1.000 +/- 0.000 | 3.064 +/- 0.010 | yes | `n_s + log(n_s*(omega_b + 0.122276284)*(H0*(o` |

Re-clustered finalist forms (Phase-2 machinery, 617 forms): top cluster rep `n_s + omega_cdm` (c=3, support {omega_cdm, n_s}, R_allparams=1.0).

## z4 — H0

Reference Î_all-6 = 3.620 +/- 0.053 nat.
**S\* = {omega_b, omega_cdm, H0, tau, A_s, n_s}** — η_S = 1.000 +/- 0.000, C_S = 20, screen-recurrent: True (per-seed minimal: s0=True, s1=True; per-seed picks agree: True).

Staircase (best η_S per support size): |S|=1: 0.140; |S|=2: 0.198; |S|=3: 0.279; |S|=4: 0.384; |S|=5: 0.639; |S|=6: 1.000.

| | S | \|S\| | C_S | η_S +/- SE | Î_S +/- SE | minimal | best form |
|---|---|---:|---:|---|---|---|---|
|  | {H0} | 1 | 15 | 0.140 +/- 0.002 | 0.506 +/- 0.000 | no | `-3.64982775134539e+15*(H0 + 0.00021219947865` |
|  | {omega_cdm, H0} | 2 | 5 | 0.198 +/- 0.003 | 0.715 +/- 0.003 | no | `6.78883971735916e-5*omega_cdm**2/(0.28876212` |
|  | {omega_cdm, H0, A_s} | 3 | 18 | 0.279 +/- 0.004 | 1.011 +/- 0.002 | no | `78.1306204324*A_s*omega_cdm*(0.0110847700026` |
|  | {omega_cdm, H0, tau} | 3 | 16 | 0.245 +/- 0.004 | 0.886 +/- 0.001 | no | `-(H0 - 1.1845531)*log(-H0*(tau - 0.2379105)*` |
|  | {H0, tau, A_s} | 3 | 13 | 0.229 +/- 0.003 | 0.829 +/- 0.004 | no | `exp(126.666831492496*A_s*(0.0888522738540811` |
|  | {omega_b, omega_cdm, H0} | 3 | 10 | 0.220 +/- 0.003 | 0.795 +/- 0.002 | no | `85.9256218619839*omega_cdm/(H0**4*(omega_b -` |
|  | {omega_cdm, H0, n_s} | 3 | 6 | 0.200 +/- 0.003 | 0.724 +/- 0.000 | no | `log(n_s/omega_cdm)/H0` |
|  | {omega_cdm, H0, tau, A_s} | 4 | 16 | 0.384 +/- 0.006 | 1.391 +/- 0.008 | no | `(A_s*H0**4*omega_cdm - 0.0654118365203833*ta` |
|  | {omega_b, omega_cdm, H0, A_s} | 4 | 14 | 0.344 +/- 0.006 | 1.244 +/- 0.009 | no | `(H0 - (omega_cdm + log(42.939632*A_s*omega_c` |
|  | {omega_b, omega_cdm, H0, tau} | 4 | 12 | 0.304 +/- 0.005 | 1.100 +/- 0.006 | no | `(-omega_b - 0.25901407*omega_cdm)/(H0*omega_` |
|  | {omega_b, omega_cdm, H0, tau, A_s} | 5 | 19 | 0.639 +/- 0.010 | 2.312 +/- 0.011 | no | `(omega_cdm - log(-H0**2 + omega_b*exp(2*tau)` |
| **S\*** | {omega_b, omega_cdm, H0, tau, A_s, n_s} | 6 | 20 | 1.000 +/- 0.000 | 3.620 +/- 0.053 | yes | `n_s - omega_cdm - log(A_s*H0*omega_cdm*(0.04` |

Re-clustered finalist forms (Phase-2 machinery, 212 forms): top cluster rep `A_s*H0**2*omega_cdm*exp(-2*tau)` (c=9, support {omega_cdm, H0, tau, ln10As}, R_allparams=0.8).


# Gate G2

| latent | role | S* | η_S | screen-recurrent | verdict |
|---|---|---|---|---|---|
| z0 | shape | {A_s, H0, n_s, omega_b, omega_cdm} | 1.003 | False | **ATTENTION (not screen-recurrent)** |
| z1 | shape | {A_s, H0, n_s, omega_b, omega_cdm, tau} | 1.000 | True | **PASS** |
| z2 | amplitude | {A_s, H0, n_s, omega_b, omega_cdm, tau} | 1.000 | True | **PASS (superset finding)** |
| z3 | shape | {H0, n_s, omega_b, omega_cdm, tau} | 0.997 | True | **PASS** |
| z4 | shape | {A_s, H0, n_s, omega_b, omega_cdm, tau} | 1.000 | True | **PASS** |

**Overall: PARTIAL (z0 flagged)**
