# Coordinate-matched OLS audit

OLS is refitted separately in each preprocessing arm on the 4,000 T0-fit rows. Every input column is centered and scaled using T0-fit statistics before the full-rank least-squares solve; this changes conditioning, not the affine hypothesis class.

Direct reconstruction compares uncalibrated OLS with uncalibrated MSE-SR. Coordinate reconstruction applies the identical 64-bin T1-only monotone calibration to OLS and MI-SR. T2 is opened only in confirmation. GMM-MI uses the exact frozen precision-campaign subset.

`Delta` is `NMSE(SR) - NMSE(OLS)` in percentage points; positive values favor OLS. OLS/SR/inc counts classify up to five valid seedwise 95% unadjusted paired-row normal CIs. These intervals are conditional on the frozen fits and calibrators and the observed T2 variance; they do not include search-, training-, or calibration-fit uncertainty and are not a pooled global test. A verdict total below five means an invalid seed was excluded.

Every SR bracket in the tables is the median [minimum, maximum] across valid frozen search seeds, not a confidence interval.

## Summary

- `raw64`: median MI-SR MI exceeds matched OLS for 5/11 latents. Direct raw-NMSE winners: OLS 9, MSE-SR 2. Coordinate calibrated-NMSE winners: OLS 6, MI-SR 5. Mixed pipeline winners: OLS 9, MI-SR 0, MSE-SR 2.

- `physical_o1_64`: median MI-SR MI exceeds matched OLS for 7/11 latents. Direct raw-NMSE winners: OLS 6, MSE-SR 5. Coordinate calibrated-NMSE winners: OLS 6, MI-SR 5. Mixed pipeline winners: OLS 6, MI-SR 1, MSE-SR 4.

- `logamp64`: median MI-SR MI exceeds matched OLS for 6/11 latents. Direct raw-NMSE winners: OLS 7, MSE-SR 4. Coordinate calibrated-NMSE winners: OLS 7, MI-SR 4. Mixed pipeline winners: OLS 7, MI-SR 1, MSE-SR 3.

## Log-amplitude OLS −2 diagnostic

- TT z2: `b_tau / b_ln10As = -1.9785`.
- TT+EE z5: `b_tau / b_ln10As = -1.9967`.

## `raw64`

| Latent | OLS raw NMSE % | MSE-SR raw NMSE % | Direct Delta % | OLS calibrated NMSE % | MI-SR calibrated NMSE % | Calibrated Delta % | OLS MI | MI-SR MI |
|---|---:|---:|---|---:|---:|---|---:|---:|
| TT z0 | 0.186 | 0.227 [0.159,0.470] | +0.041 [-0.027,+0.284]; OLS/SR/inc=3/2/0 | 0.213 | 0.191 [0.128,0.214] | -0.022 [-0.085,+0.001]; OLS/SR/inc=0/4/1 | 3.312±0.014 | 3.278 [3.239,3.504] |
| TT z1 | 1.402 | 1.729 [1.195,2.990] | +0.327 [-0.207,+1.589]; OLS/SR/inc=3/2/0 | 1.480 | 1.710 [1.552,2.129] | +0.230 [+0.072,+0.649]; OLS/SR/inc=5/0/0 | 2.312±0.014 | 2.304 [2.197,2.324] |
| TT z2 | 0.099 | 0.243 [0.054,0.572] | +0.144 [-0.045,+0.473]; OLS/SR/inc=4/1/0 | 0.195 | 0.163 [0.133,0.186] | -0.032 [-0.061,-0.009]; OLS/SR/inc=0/5/0 | 3.521±0.013 | 3.748 [3.596,4.098] |
| TT z3 | 0.214 | 0.230 [0.201,0.508] | +0.016 [-0.013,+0.294]; OLS/SR/inc=4/1/0 | 0.243 | 0.268 [0.256,0.274] | +0.025 [+0.013,+0.031]; OLS/SR/inc=5/0/0 | 3.122±0.014 | 3.102 [3.095,3.136] |
| TT z4 | 0.054 | 0.152 [0.111,0.489] | +0.099 [+0.057,+0.435]; OLS/SR/inc=5/0/0 | 0.160 | 0.200 [0.187,0.216] | +0.040 [+0.027,+0.056]; OLS/SR/inc=5/0/0 | 3.869±0.011 | 3.631 [3.469,3.687] |
| TT+EE z0 | 3.949 | 4.139 [3.979,5.931] | +0.190 [+0.030,+1.982]; OLS/SR/inc=5/0/0 | 3.950 | 4.989 [4.501,5.341] | +1.039 [+0.551,+1.391]; OLS/SR/inc=5/0/0 | 1.724±0.015 | 1.762 [1.724,1.797] |
| TT+EE z1 | 0.097 | 0.181 [0.098,0.935] | +0.084 [+0.001,+0.838]; OLS/SR/inc=5/0/0 | 0.146 | 0.154 [0.154,0.193] | +0.008 [+0.008,+0.047]; OLS/SR/inc=5/0/0 | 3.723±0.010 | 3.693 [3.442,3.693] |
| TT+EE z2 | 0.173 | 0.186 [0.155,0.911] | +0.014 [-0.017,+0.738]; OLS/SR/inc=3/2/0 | 0.211 | 0.226 [0.211,0.228] | +0.015 [-0.000,+0.017]; OLS/SR/inc=4/0/1 | 3.264±0.014 | 3.239 [3.235,3.265] |
| TT+EE z3 | 0.311 | 0.249 [0.208,0.294] | -0.062 [-0.102,-0.017]; OLS/SR/inc=0/5/0 | 0.369 | 0.306 [0.291,0.322] | -0.063 [-0.078,-0.047]; OLS/SR/inc=0/5/0 | 2.978±0.014 | 3.136 [3.114,3.182] |
| TT+EE z4 | 4.283 | 1.217 [1.084,2.557] | -3.067 [-3.199,-1.726]; OLS/SR/inc=0/5/0 | 4.162 | 1.409 [1.226,5.486] | -2.753 [-2.935,+1.324]; OLS/SR/inc=1/4/0 | 1.844±0.013 | 2.307 [1.898,2.358] |
| TT+EE z5 | 0.115 | 0.453 [0.110,0.574] | +0.338 [-0.005,+0.459]; OLS/SR/inc=4/1/0 | 0.168 | 0.123 [0.117,0.183] | -0.045 [-0.051,+0.015]; OLS/SR/inc=1/4/0 | 3.550±0.014 | 3.918 [3.435,3.960] |

## `physical_o1_64`

| Latent | OLS raw NMSE % | MSE-SR raw NMSE % | Direct Delta % | OLS calibrated NMSE % | MI-SR calibrated NMSE % | Calibrated Delta % | OLS MI | MI-SR MI |
|---|---:|---:|---|---:|---:|---|---:|---:|
| TT z0 | 0.186 | 0.082 [0.060,0.180] | -0.104 [-0.126,-0.006]; OLS/SR/inc=0/5/0 | 0.213 | 0.178 [0.114,0.225] | -0.035 [-0.098,+0.012]; OLS/SR/inc=1/4/0 | 3.312±0.014 | 3.320 [3.230,3.631] |
| TT z1 | 1.402 | 1.507 [1.242,1.763] | +0.106 [-0.159,+0.361]; OLS/SR/inc=3/1/1 | 1.480 | 1.557 [1.532,1.853] | +0.077 [+0.051,+0.373]; OLS/SR/inc=5/0/0 | 2.312±0.014 | 2.285 [2.273,2.350] |
| TT z2 | 0.099 | 0.129 [0.094,0.167] | +0.031 [-0.005,+0.069]; OLS/SR/inc=4/1/0 | 0.195 | 0.182 [0.163,0.191] | -0.012 [-0.032,-0.003]; OLS/SR/inc=0/5/0 | 3.521±0.013 | 3.628 [3.567,3.716] |
| TT z3 | 0.214 | 0.166 [0.159,0.194] | -0.048 [-0.055,-0.020]; OLS/SR/inc=0/5/0 | 0.243 | 0.195 [0.179,0.203] | -0.048 [-0.064,-0.040]; OLS/SR/inc=0/5/0 | 3.122±0.014 | 3.308 [3.292,3.406] |
| TT z4 | 0.054 | 0.096 [0.054,0.298] | +0.042 [+0.001,+0.244]; OLS/SR/inc=4/0/1 | 0.160 | 0.183 [0.156,0.239] | +0.023 [-0.004,+0.079]; OLS/SR/inc=3/2/0 | 3.869±0.011 | 3.717 [3.528,3.983] |
| TT+EE z0 | 3.949 | 3.951 [3.467,4.028] | +0.002 [-0.482,+0.079]; OLS/SR/inc=2/1/1 | 3.950 | 4.778 [4.737,4.865] | +0.828 [+0.786,+0.915]; OLS/SR/inc=5/0/0 | 1.724±0.015 | 1.794 [1.790,1.806] |
| TT+EE z1 | 0.097 | 0.117 [0.063,0.251] | +0.021 [-0.034,+0.154]; OLS/SR/inc=4/1/0 | 0.146 | 0.169 [0.140,0.238] | +0.023 [-0.006,+0.091]; OLS/SR/inc=3/1/1 | 3.723±0.010 | 3.542 [3.455,3.776] |
| TT+EE z2 | 0.173 | 0.141 [0.124,0.156] | -0.032 [-0.049,-0.017]; OLS/SR/inc=0/5/0 | 0.211 | 0.228 [0.163,0.238] | +0.017 [-0.048,+0.027]; OLS/SR/inc=3/2/0 | 3.264±0.014 | 3.264 [3.200,3.392] |
| TT+EE z3 | 0.311 | 0.226 [0.193,0.247] | -0.085 [-0.118,-0.064]; OLS/SR/inc=0/5/0 | 0.369 | 0.276 [0.254,0.309] | -0.093 [-0.115,-0.060]; OLS/SR/inc=0/5/0 | 2.978±0.014 | 3.279 [3.086,3.293] |
| TT+EE z4 | 4.283 | 1.784 [1.379,2.712] | -2.499 [-2.904,-1.571]; OLS/SR/inc=0/5/0 | 4.162 | 1.378 [1.126,5.579] | -2.783 [-3.036,+1.417]; OLS/SR/inc=1/4/0 | 1.844±0.013 | 2.309 [2.085,2.408] |
| TT+EE z5 | 0.115 | 0.121 [0.064,0.210] | +0.006 [-0.051,+0.094]; OLS/SR/inc=3/2/0 | 0.168 | 0.171 [0.155,0.189] | +0.003 [-0.014,+0.021]; OLS/SR/inc=3/2/0 | 3.550±0.014 | 3.560 [3.452,3.703] |

## `logamp64`

| Latent | OLS raw NMSE % | MSE-SR raw NMSE % | Direct Delta % | OLS calibrated NMSE % | MI-SR calibrated NMSE % | Calibrated Delta % | OLS MI | MI-SR MI |
|---|---:|---:|---|---:|---:|---|---:|---:|
| TT z0 | 0.186 | 0.180 [0.129,0.203] | -0.006 [-0.057,+0.017]; OLS/SR/inc=2/3/0 | 0.212 | 0.160 [0.139,0.216] | -0.052 [-0.073,+0.004]; OLS/SR/inc=1/4/0 | 3.301±0.014 | 3.386 [3.154,3.466] |
| TT z1 | 1.390 | 1.402 [1.177,1.462] | +0.012 [-0.213,+0.072]; OLS/SR/inc=2/2/1 | 1.469 | 1.854 [1.786,2.027] | +0.385 [+0.317,+0.559]; OLS/SR/inc=5/0/0 | 2.322±0.015 | 2.276 [2.241,2.379] |
| TT z2 | 0.044 | 0.311 [0.109,0.366] | +0.266 [+0.064,+0.322]; OLS/SR/inc=5/0/0 | 0.140 | 0.173 [0.130,0.287] | +0.033 [-0.010,+0.146]; OLS/SR/inc=4/1/0 | 4.000±0.015 | 3.706 [3.252,4.194] |
| TT z3 | 0.214 | 0.221 [0.179,0.240] | +0.007 [-0.035,+0.025]; OLS/SR/inc=3/2/0 | 0.243 | 0.248 [0.238,0.266] | +0.005 [-0.006,+0.023]; OLS/SR/inc=4/1/0 | 3.121±0.014 | 3.162 [3.110,3.202] |
| TT z4 | 0.040 | 0.261 [0.105,0.789] | +0.221 [+0.065,+0.748]; OLS/SR/inc=5/0/0 | 0.148 | 0.199 [0.184,0.317] | +0.051 [+0.036,+0.169]; OLS/SR/inc=5/0/0 | 4.040±0.012 | 3.583 [3.182,3.687] |
| TT+EE z0 | 3.954 | 4.120 [4.054,4.183] | +0.167 [+0.100,+0.230]; OLS/SR/inc=5/0/0 | 3.955 | 5.165 [4.924,5.350] | +1.209 [+0.969,+1.395]; OLS/SR/inc=5/0/0 | 1.722±0.014 | 1.781 [1.753,1.791] |
| TT+EE z1 | 0.095 | 0.095 [0.057,0.427] | +0.000 [-0.038,+0.332]; OLS/SR/inc=3/2/0 | 0.145 | 0.126 [0.124,0.151] | -0.019 [-0.021,+0.007]; OLS/SR/inc=2/3/0 | 3.740±0.011 | 3.844 [3.646,3.873] |
| TT+EE z2 | 0.171 | 0.149 [0.113,0.193] | -0.021 [-0.058,+0.022]; OLS/SR/inc=2/3/0 | 0.209 | 0.223 [0.206,0.229] | +0.014 [-0.003,+0.020]; OLS/SR/inc=4/1/0 | 3.272±0.014 | 3.259 [3.237,3.280] |
| TT+EE z3 | 0.311 | 0.236 [0.156,0.332] | -0.075 [-0.155,+0.021]; OLS/SR/inc=1/4/0 | 0.369 | 0.314 [0.248,0.360] | -0.055 [-0.121,-0.009]; OLS/SR/inc=0/5/0 | 2.979±0.014 | 3.141 [3.068,3.331] |
| TT+EE z4 | 4.179 | 1.368 [1.118,1.598] | -2.811 [-3.062,-2.581]; OLS/SR/inc=0/5/0 | 4.062 | 1.438 [1.013,3.321] | -2.623 [-3.048,-0.740]; OLS/SR/inc=0/5/0 | 1.839±0.013 | 2.327 [2.258,2.424] |
| TT+EE z5 | 0.045 | 0.104 [0.055,0.172] | +0.059 [+0.010,+0.127]; OLS/SR/inc=5/0/0 | 0.111 | 0.134 [0.117,0.285] | +0.022 [+0.006,+0.174]; OLS/SR/inc=5/0/0 | 4.042±0.012 | 3.823 [3.237,3.956] |

The `raw64` and `physical_o1_64` OLS predictors are required to agree after T0-fit conditioning because their inputs differ only by invertible affine rescaling. They are one invariance check, not two independent wins. `logamp64` is the genuinely different affine model.

GMM-MI uncertainties are estimator bootstrap errors copied for frozen SR and recomputed for matched OLS. They are descriptive and are not treated as paired significance tests.
