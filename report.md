# Blind symbolic interpretation of CMB β-VAE latents

*Figure and table identifiers are stable project identifiers. Where material is not included in this version, the numbering is not contiguous.*

---

## Part I — Setup

### 1. Introduction

Machine-learned compression models are now routinely placed between cosmological theory and statistical inference, and their internal latent variables are often treated as if they were physical quantities. This study investigates whether the physical content of such a latent variable can be recovered symbolically from data alone.

The study makes three contributions. First, it develops a blind discovery pipeline: a symbolic-regression protocol in which both the search loss and the selection metric are mutual-information estimators, combined with a fixed suite of validation tests. Second, it produces a validated summary for every latent variable of two trained networks. Each summary records a canonical symbolic coordinate together with how reproducibly the search finds it, how completely it exhausts the information available to its own parameters, and how it behaves under interventional tests. Third, it reports structural findings about how the encoder organises information. Each discovered coordinate extracts essentially all the information carried by its own parameters, yet no coordinate fully accounts for its latent. The unexplained remainder forms a hierarchy that does not terminate after two levels. One latent demonstrably mixes amplitude and shape information multiplicatively. And when polarization data are added, the amplitude information splits into two complementary latents rather than being duplicated.

### 2. Data and models

The two compressors are stored β-VAE checkpoints from the parent reproduction of Piras, Herold, Lucie-Smith & Komatsu (2025) [1]. Both were trained on the same 500,000-sample Latin-hypercube (LHS) design over the six ΛCDM parameters of Table T2.1, mapped to CMB power spectra by the CLASS Boltzmann solver [6]. Spectra are handled as $\log_{10} D_\ell$, with $D_\ell \equiv \ell(\ell+1)C_\ell/2\pi$, taken relative to a fixed reference spectrum and standardised per multipole bin. Both use the β-VAE objective [5] at $\beta = 3\times10^{-4}$, training seed 42, 750 epochs, batch size 1024, learning rate $10^{-3}$:

* **TT**: a single-encoder convolutional β-VAE with **5 latents** over the temperature (TT) channel alone, 2471 multipole bins.
* **EE**: a dual-encoder variant with **6 latents** over TT plus an EE-polarization channel that includes the low-$\ell$ reionization regime, 2471 + 2499 bins.

There are eleven latents in total. For each latent $k$ the encoder returns a posterior mean $\mu_k(\theta)$ and a log-variance $\log\sigma_k^2(\theta)$, and the stochastic latent is

$$Z_k \;=\; \mu_k(\theta) + \sigma_k(\theta)\,\varepsilon_k, \qquad \varepsilon_k \sim \mathcal N(0,1).$$

The symbolic-regression target throughout is the deterministic mean map $\mu_k(\theta)$ on the 50,000-row held-out test split. The stochastic latent $Z_k$, drawn using the cached log-variances, supplies the intrinsic information ceiling of §5.

The test split is divided into three tiers:

* **T0** (rows 0–4999) is exactly the slice the symbolic-regression protocol consumes (4000 rows for fitting, 1000 for validation). Because the search itself uses these rows, they are treated as contaminated for all later testing. Keeping this slice identical to the pre-existing protocol keeps every earlier result comparable.
* **T1** (rows 5000–24999) serves everything that must subsequently be fit on data: the cross-fitted calibration $h$, the residual audits, the fixed 2048-row anchor set used for semantic comparisons, the construction of level-set pairs, the decoder anchors, and the probe training.
* **T2** (rows 25000–49999) is reserved for confirmatory numbers, computed once.

The separation between T1 and T2 is what makes the frozen thresholds falsifiable, because a threshold crossing recomputed on the same rows an instrument was tuned on is not a genuine test. Every figure caption below names the tier it draws on.

#### T2.1 — Parameters and priors

The table lists the six raw inputs of the search. The amplitude sector is the parameter pair $(\tau, A_s)$, and the shape sector is $\{\omega_b, \omega_{\mathrm{cdm}}, H_0, n_s\}$.

| sampled parameter | symbol | LHS range |
|---|---|---|
| baryon density | $\omega_b$ | [0.020, 0.024] |
| cold-dark-matter density | $\omega_{\mathrm{cdm}}$ | [0.100, 0.130] |
| Hubble constant | $H_0$ | [62, 80] |
| reionization optical depth | $\tau$ | [0.01, 0.13] |
| scalar amplitude (log) | $\ln 10^{10}A_s$ | [2.90, 3.18] |
| scalar tilt | $n_s$ | [0.92, 1.01] |

Latin hypercube, 500,000 samples, seed 42. The **audit basis** $u$ standardises each parameter to its prior box,

$$u_j = \frac{\theta_j - \mathrm{mid}_j}{w_j},$$

with $\mathrm{mid}_j$ and $w_j$ the box midpoint and half-width. One convention applies everywhere below. The amplitude is *sampled* as $x \equiv \ln 10^{10}A_s$, but the search receives it in linear scale, $A_s = 10^{-10}e^{x}$. This is a fixed, order-preserving transformation of a single parameter rather than a derived combination, and statements based on mutual information are unaffected by it. Discovered expressions therefore contain $A_s$. All derivatives and $u$-coordinates are taken in the sampled basis, whose amplitude direction we write $\ln A_s$, and the chain rule $\partial f/\partial \ln A_s = A_s\,\partial f/\partial A_s$ is applied throughout. In lists of parameter supports we write the amplitude member simply as $A_s$.

#### F2.2 — The raw disentanglement audit reveals the expected roles before symbolic search

![F2.2 — MI(mu_k; theta_j) heatmap, both checkpoints](paper/figs/F2_2_audit_heatmap.png)

**Figure F2.2.** Mutual information between each latent's posterior mean and each raw parameter, for all 11 latents and 6 parameters, with the two checkpoints side by side (Kraskov–Stögbauer–Grassberger $k$-nearest-neighbour estimates [3] on T1 rows). This audit fixes the *expected role* of each latent, which is used everywhere downstream. The boxed $(\tau, \ln A_s)$ columns already show a structural result to which §9 returns: **one** latent loads on the amplitude pair in TT, but **two** do in EE. There, $z_4$ is anchored to $\tau$ (0.5 and 0.3 nat on $\tau$ and $\ln A_s$ respectively), while $z_5$ carries the damped combination (0.3 and 0.4 nat).

### 3. Blind symbolic interpretation and pre-registered inference

For random variables $X, Y$ the mutual information

$$I(X;Y) \;=\; \int p(x,y)\,\ln\frac{p(x,y)}{p(x)\,p(y)}\,dx\,dy$$

is invariant under bijections of either argument: $I(g(X);Y) = I(X;Y)$ for any invertible $g$. Because the inner search loss is a real MI estimator, it shares this invariance class with the selection metric, and the search is rewarded only for *functional dependence* on $\theta$, never for matching the encoder's calibration, offset, or scale. Information is reported in nats throughout, and $\hat I$ denotes an estimate.

The composite $g\circ f$ scores exactly what $f$ scores, so a whole family of expressions is indistinguishable to the pipeline by construction. This has two consequences. First, **the answer is an equivalence class rather than a single equation**. Section 4 therefore clusters expressions by algebraic and statistical equivalence and reports a canonical representative of each cluster. Second, for a monotone $g$ we have $\nabla(g\circ f) = g'\,\nabla f$, so *ratios of partial derivatives are invariant across the equivalence class while fitted coefficients are not*. Section 5.x accordingly reads the amplitude exponent from ratios of partial derivatives rather than from any fitted coefficient.

**The inner loss and the selection metric.** The symbolic-regression engine is PySR [4]. Its inner loss is

$$\mathcal L[f] \;=\; \exp\!\big(-\hat I_{2}\big(f(\theta);\,\mu_k\big)\big),$$

where $\hat I_2$ is a Gaussian-mixture MI estimate with a fixed two-component mixture fit by expectation–maximisation (EM) on a strided 300-row subsample. Selection is a separate step: every Pareto-front expression is re-scored on held-out rows with the full GMM-MI estimator of Piras et al. (2023) [2], with the component count selected by cross-validation and uncertainties from bootstrap resampling. The search protocol is fixed throughout: 5000 T0 samples (4000 for fitting, 1000 for validation), 200 iterations, 15 populations, maximum expression size 20 unless stated otherwise (engine defaults elsewhere), and 5 seeds per configuration. The unary operators are $\{\exp, \log, \mathrm{neg}, \mathrm{square}\}$ and the binary operators are $\{+, -, \times, \div\}$.

**Pre-registration.** Every decision threshold below was frozen before any shape-sector latent was unblinded. The instruments were validated first on the amplitude sector, whose answer is known from physics. This serves as the positive control of §5. Pre-registered pass/fail criteria are reported beside the instruments they test. Judgement calls made after the freeze were not applied silently: each is recorded in a register of deviations and reported beside the instrument it affects (§5, §6.x, §7).

---

## Part II — Pipeline

### 4. Every latent has a recurrent, low-complexity primary coordinate

The discovery stage is six-input blind symbolic regression, returning Pareto fronts of held-out MI against expression complexity $c$ (the expression-tree node count). The primary coordinate is then selected *from* those fronts. Fronts are pooled over three search-capacity families (maximum expression size 10, 20, or 30, with 5, 5, and 3 seeds respectively).

**Selection rules.** Selection is based on saturation of the information curve, not on the single highest-scoring expression. Writing $M(c)$ for the best held-out MI among front expressions of complexity at most $c$, the plateau value $\hat I_{\mathrm{plat}}$ is the cross-seed mean of the front maximum in the highest-capacity family, with standard error taken as the cross-seed standard deviation divided by $\sqrt n$. The saturation point $c^{*}$ is the smallest complexity whose envelope comes within one standard error of the plateau,

$$c^{*} \;=\; \min\{\,c : M(c) \ge \hat I_{\mathrm{plat}} - \mathrm{SE}\,\}.$$

Simplest sufficient forms are read off at the levels $\eta \ge 0.90/0.95/0.99$ of the plateau, where "sufficient" defaults to $\eta \ge 0.95$. The quantity $M(c{\le}10)$, the best front MI at complexity 10 or below, is also recorded so that searches of different capacities can be compared at a common complexity. Recurrence is judged semantically rather than by comparing expression strings: two forms join the same cluster if any one of three tests succeeds:

1. identical canonical algebraic form after symbolic simplification;
2. $|\rho_S| \ge 0.98$ (Spearman rank correlation) on the fixed 2048-point anchor set. On an interval a continuous bijection is monotone, so rank agreement is exactly MI-equivalence on the observed domain;
3. gradient distance $d_\nabla \le 0.05$, where $d_\nabla(f,g) = 1 - \langle\,|\cos(\nabla_u f, \nabla_u g)|\,\rangle_{\mathrm{anchors}}$.

Clusters are formed by union-find over these pairwise tests. **R_SR** is the fraction of seeds whose front carries a member of the latent's dominant cluster at the saturation point (the front restricted to complexity at most $c^{*}$). Cluster *cohesion* is the fraction of sampled cluster members directly equivalent to the reported representative.

**A hyperparameter finding.** A dedicated sweep (12 configurations × 3 seeds × both checkpoints) shows that the maximum MI at the top of the front is controlled almost entirely by search capacity: changing the maximum expression size alone moves it from 1.6 to 4.05 nat. In contrast, the capacity-matched value $M(c{\le}10)$ is essentially flat across every setting (about 1.89 nat for TT and 2.02 nat for EE). Moreover, a search restricted to maximum size 10 produces a *worse* front at $c\le10$ than a maximum-size-20 search read off at $c\le10$ (1.60 versus 1.89 nat for TT, and 1.69 versus 2.02 for EE). Complexity should therefore be treated as a reporting threshold rather than a search constraint: search with generous capacity, then read results off at the desired complexity.

**Result.** A recurrent primary coordinate exists for every latent, and every latent is a multi-parameter composite: the top front forms use at least five of the six parameters. **Next question:** does the primary coordinate actually account for the latent?

#### F4.1 — Cumulative Pareto envelopes, both checkpoints, with the null in-panel

![F4.1 — cumulative Pareto envelopes with shuffled-target null](paper/figs/F4_1_envelopes.png)

**Figure F4.1.** Validation MI against expression complexity for each latent: the combined envelope (heavy line) over the per-family means (maximum sizes 10/20/30, faint), the plateau band (mean ± SE), and the saturation point $c^{*}$ marked. The **shuffled-target control**, in which the same search is run against a row-shuffled latent, is drawn in the same axes at the bottom of each row. It reaches at most 0.06 nat, against real plateaus of 1.79 to 4.31 nat, so the null result is displayed directly beside the measurement it controls. T0-validation fronts, per-checkpoint scope.

#### T4.1 — Primary coordinates, discovery columns

**TT (temperature only)**

| $z$ | expected role | canonical $f_1$ | $C$ | $c_{0.90}$ | $c^{*}$ | $\hat I_{\mathrm{plat}}\pm$SE [nat] | $M(c{\le}10)$ | R_SR | seeds w/ cluster (ms10/20/30) | forms pooled |
|---|---|---|---:|---:|---:|---|---:|---:|---|---:|
| 0 | $\omega_b$ | $n_s/\omega_b$ | 3 | 16 | 26 | 3.570 ± 0.059 | 2.561 | 1.00 | 5/5 · 4/5 · 3/3 | 157 |
| 1 | $\omega_{\mathrm{cdm}}$ | $H_0^2 n_s^2\,\omega_b/(A_s\,\omega_{\mathrm{cdm}}^2)$ | 10 | 19 | 29 | 2.515 ± 0.013 | 1.211 | 0.80 | 3/5 · 4/5 · 2/3 | 103 |
| 2 | amplitude $(\tau, A_s)$ | $A_s/\ln\!\big(H_0(\omega_{\mathrm{cdm}}+\tau)\big)$ | 8 | 19 | 24 | 4.175 ± 0.043 | 1.891 | 1.00 | 4/5 · 3/5 · 3/3 | 446 |
| 3 | $n_s$ | $n_s+\omega_{\mathrm{cdm}}$ | 3 | 13 | 27 | 3.147 ± 0.030 | 2.279 | 1.00 | 4/5 · 5/5 · 3/3 | 141 |
| 4 | $H_0$ | $A_s H_0^2\,\omega_{\mathrm{cdm}}\,e^{-2\tau}$ | 9 | 21 | 24 | 4.313 ± 0.120 | 1.318 | 0.80 | 4/5 · 4/5 · 2/3 | 101 |

**EE (temperature + low-$\ell$ polarization)**

| $z$ | expected role | canonical $f_1$ | $C$ | $c_{0.90}$ | $c^{*}$ | $\hat I_{\mathrm{plat}}\pm$SE [nat] | $M(c{\le}10)$ | R_SR | seeds w/ cluster (ms10/20/30) | forms pooled |
|---|---|---|---:|---:|---:|---|---:|---:|---|---:|
| 0 | $\omega_{\mathrm{cdm}}$ / early ISW | $\omega_{\mathrm{cdm}}/(H_0\,n_s\,\omega_b)$ | 7 | 12 | 19 | 1.788 ± 0.008 | 1.457 | 1.00 | 5/5 · 4/5 · 2/3 | 119 |
| 1 | $H_0$ | $H_0^2\,\omega_{\mathrm{cdm}}$ | 4 | 20 | 25 | 4.006 ± 0.045 | 1.952 | 1.00 | 5/5 · 4/5 · 2/3 | 133 |
| 2 | $\omega_b$ | $\omega_b/n_s^2$ | 4 | 10 | 22 | 3.330 ± 0.020 | 3.057 | 1.00 | 5/5 · 4/5 · 3/3 | 145 |
| 3 | $n_s$ | $\ln(\omega_b)/(n_s+\omega_{\mathrm{cdm}})$ | 6 | 13 | 18 | 3.212 ± 0.071 | 2.048 | 0.80 | 4/5 · 4/5 · 2/3 | 145 |
| 4 | $\tau$ (amplitude sector) | $-A_s/(\tau-0.4454238)$ | 5 | 17 | 20 | 2.370 ± 0.082 | 1.905 | 1.00 | 4/5 · 4/5 · 3/3 | 160 |
| 5 | amplitude $(\tau, A_s)$ | $A_s\,e^{-2\tau}$ | 5 | 18 | 28 | 4.087 ± 0.004 | 2.019 | 1.00 | 5/5 · 4/5 · 3/3 | 461 |

**Table T4.1.** "Expected role" is the role fixed in advance by the audit of F2.2. $C$ is the complexity of the canonical representative, $c_{0.90}$ the smallest complexity whose envelope reaches $0.90\,\hat I_{\mathrm{plat}}$, and $c^{*}$ the one-standard-error saturation point. R_SR is the maximum over the three capacity families (ms = maximum expression size). The per-family seed fractions are listed so that the recurrence can be seen not to be an artifact of a single family. "Forms pooled" is the number of distinct front expressions that the semantic clustering absorbed into the latent's dominant cluster. "Early ISW" stands for early integrated Sachs–Wolfe. T0-validation.

**The shape of the envelope is itself a result.** Each envelope is classified by comparing $c_{0.90}$ against a fixed "simple form" threshold of $c\le10$. An envelope *saturates early* if $c_{0.90}$ and $c^{*}$ are both at most 10, it *rises early then climbs slowly* if $c_{0.90}\le 10 < c^{*}$, and it is *diffuse* if $c_{0.90}>10$. **No latent in either checkpoint saturates early.** Ten of eleven are diffuse. EE $z_2$ alone rises early then climbs slowly, and only marginally so: $c_{0.90}=10$ exactly, where $\omega_b + 1.868\times10^{-3}\,(n_s-\omega_{\mathrm{cdm}})\ln A_s$ reaches $\eta = 0.933$ before the envelope climbs on to $c^{*}=22$. The information in the front is therefore spread over a range of complexities rather than concentrated in one simple form: the search keeps finding real mutual information as complexity increases.

### 5. Primary coordinates saturate their own support but not the full latent

"Interpretation" needs a precise definition. Four instruments are deployed, each with its own null test. The first is the **sensitivity signature**, the normalised mean absolute gradient $g_j = \langle|\partial f/\partial u_j|\rangle \big/ \sum_i \langle|\partial f/\partial u_i|\rangle$ over the anchor points, together with the answer-agnostic **constant-ratio detector** of §5.x. The second is an **exhaustive subset campaign** over all $2^6-1 = 63$ non-empty variable sets, which yields an information ceiling for each restricted set of input parameters. The third is the **intrinsic ceiling** estimated from the stochastic latent (T5.3). The fourth is **calibrated sufficiency**: a five-fold cross-fitted monotone recalibration followed by a residual audit against permutation nulls (F5.3).

**The calibration and the residual.** Because MI identifies $f$ only up to a bijection of its output, sufficiency is never tested on raw mean-squared error. A scalar calibration $h$ absorbs the arbitrary bijection, and everything is tested on the stage-1 residual. The calibration is an isotonic regression on quantile-bin means, interpolated monotonically, and it is five-fold cross-fitted so that each row's prediction comes from a fold model that never saw that row. The residual is

$$e_1(\theta) \;=\; \mu_k(\theta) - h\big(f_1(\theta)\big).$$

**The η ladder.** Three ratios that would otherwise be conflated:

* $\eta_S = \hat I(f)/\hat I_S$ compares $f$ against the **support-restricted ceiling** $\hat I_S$, the empirical front maximum attainable when the search is restricted to $f$'s own variable set $S$ (from the 63-subset campaign). It answers: does $f$ saturate its own variables? Fronts are evaluated on T0-validation and the reported value is confirmed on T2. This ratio is a status criterion, with threshold $\eta_S \ge 0.95$.
* $\eta_{\mathrm{plat}} = \hat I(f)/\hat I_{\mathrm{plat}}$ compares $f$ against the empirical all-parameter plateau. It answers: what fraction of the searchable mean map does $f$ capture? It is evaluated on T0-validation and is a reporting quantity only, never a status criterion.
* $\hat\eta_{\mathrm{post}} = \hat I(Z_k; f)/\hat I(Z_k; \mu_k)$ compares $f$ against what the stochastic latent actually transmits. It answers: what fraction of the information the latent physically stores does $f$ carry? It is evaluated on T2 and is the demotion criterion under the frozen 0.95 rule. The analytic variant $\eta_{\mathrm{post}} = \hat I(Z_k;f)/I(Z_k;\theta)$ remains the headline number (T5.3).

A latent can honestly score $\eta_S = 1.00$ while scoring $\eta_{\mathrm{plat}} = 0.35$. That distinction is what makes "primarily interpreted" a precise status rather than a hedge. Preferring the same-estimator ratio $\hat\eta_{\mathrm{post}}$ over $\eta_{\mathrm{post}}$ as the decision metric is itself a registered deviation from the pre-specified ratio. It was adopted because the GMM-MI numerator carries a small upward estimator bias that an identically estimated denominator cancels. The choice was made on a synthetic positive control before any real data were scored, and the two ratios agree to within 0.03 on every latent.

Subset minimality is defined as follows: $S^{*}$ is the smallest support (with ties broken toward smaller complexity) whose $\eta_S$ sits within one standard error of the best value over all supersets, and it is required to recur across screening seeds. The **residual pass** requires both a cross-fitted $R^2(e_1 \leftarrow \theta) \le 0.05$ (gradient-boosted regressor) and a largest per-parameter MI, $\max_j \hat I(e_1;\theta_j)$, at or below the 97.5th percentile of the permutation null. If either condition fails, the audit fails.

**The positive control.** The amplitude latents' $\{\tau, A_s\}$ entry in the subset campaign is the reference case with a known physical answer. The frozen machinery must rediscover that support among all 63 subsets with no special treatment, saturate against its own ceiling, recover the $-2$ exponent, and still report the stage-1 residual as structured. The control can therefore fail in either direction: it fails if the instruments fabricate sufficiency, and it fails equally if they miss real structure. **The control passes on both models** ($\eta_S = 1.000$ for TT and 1.015 for EE, the exponent is recovered, and the residual is correctly reported as structured).

**Result.** For every latent, $\eta_S \approx 1$ while $\hat\eta_{\mathrm{post}}(f_1) < 1$, and every stage-1 residual is structured. Each primary coordinate therefore saturates its own variables yet accounts for only part of what its latent physically stores, and the positive control shows that the instruments do not fabricate sufficiency. **Next question:** what is in the residual?

#### F5.1 — The η ladder, per latent: saturation of own support, not of the latent

![F5.1 — the eta ladder for all 11 latents](paper/figs/F5_1_eta_ladder.png)

**Figure F5.1.** The report's central quantitative figure. For each of the 11 latents, three aligned markers are shown: $\eta_S$ (light circle, essentially at the dashed saturation line), $\eta_{\mathrm{plat}}$ at the saturation-point slice (square), and $\hat\eta_{\mathrm{post}}(f_1)$ (diamond). The visible gap between $\eta_S \approx 1$ and $\hat\eta_{\mathrm{post}} < 1$ is precisely the claim in the section title. EE $z_4$ sits slightly above 1.0, at $\eta_S = 1.068 \pm 0.026$: its canonical coordinate scores above the cross-seed mean ceiling of its own minimal support $\{\omega_b, \tau, A_s\}$. Because $\hat I_S$ is an empirical front maximum rather than an analytic bound, a ratio slightly above 1 reflects uncertainty in the ceiling estimate, not genuine super-saturation. Latents are shown in the same order as the summary tables, for both checkpoints, and the plotted ratios are confirmed on T2. Per-checkpoint scope.

#### F5.3 — The structure of the stage-1 residual, shown directly

![F5.3 — EE z5 residual against its leading parameter](paper/figs/F5_3_residual_structure.png)

**Figure F5.3.** The EE amplitude latent's stage-1 residual $e_1 = \mu - h(f_1)$ against $\omega_{\mathrm{cdm}}$, its leading residual direction, with the binned mean overlaid ($|\rho_S| = 0.78$), on a T1 subsample. The residual is not noise, and it is worth *seeing* that rather than only scoring it.

**What the audit finds across all 11 latents.** After five-fold cross-fitted monotone recalibration, the calibration itself is good: $R^2_{\mathrm{cal}}$ ranges from 0.904 to 0.955, so $h(f_1)$ is a genuine account of each latent's leading behaviour. Yet the residual that remains is strongly predictable from the raw parameters, with $R^2_{\mathrm{res}}$ between 0.960 and 0.994 against permutation nulls of roughly $\pm 0.002$. The frozen rule demands $R^2 \le 0.05$, so the first condition alone fails by a factor of about 20. The second condition fails by a wider margin still: the largest per-parameter MI between residual and raw parameter sits far above its permutation null, which is 0.001 nat for nine of the eleven latents (0.014 for EE $z_0$ and 0.019 for EE $z_4$):

| model | $z$ | $\max_j \hat I(e_1;\theta_j)$ [nat] (leading parameter) |
|---|---|---|
| TT | 0 | 0.450 ($\omega_{\mathrm{cdm}}$) |
| TT | 1 | 0.393 ($n_s$) |
| TT | 2 | 0.199 ($\omega_{\mathrm{cdm}}$) |
| TT | 3 | 0.440 ($\omega_{\mathrm{cdm}}$) |
| TT | 4 | 0.596 ($\omega_b$) |
| EE | 0 | 0.220 ($A_s$) |
| EE | 1 | 0.357 ($\omega_b$) |
| EE | 2 | 0.640 ($\omega_{\mathrm{cdm}}$) |
| EE | 3 | 0.548 ($\omega_{\mathrm{cdm}}$) |
| EE | 4 | 0.690 ($\tau$) |
| EE | 5 | 0.455 ($\omega_{\mathrm{cdm}}$) |

The residual depends on many parameters, not only those in the coordinate's own support: all six parameters sit above their null for eight latents, five of six do for EE $z_2$ and EE $z_3$, and four of six for EE $z_5$. The residual audit therefore returns FAIL for all 11 latents, and that is the informative outcome: an instrument reporting PASS on these residuals would be fabricating sufficiency. The negative control confirms that the audit works in the other direction as well. Shuffled coordinates explain essentially nothing of the true latent (MI of 0.001–0.245 nat and $R^2_{\mathrm{cal}}$ of 0.05–0.38), so their residual is essentially the latent itself and $R^2_{\mathrm{res}}$ is trivially about 0.99, which the audit correctly reports as *total* insufficiency. T1 calibration, T2 confirmation.


#### T5.3 — Intrinsic ceilings and the posterior signal-to-noise ratio

The intrinsic ceiling is estimated from the stochastic latent as

$$I(Z_k;\theta) \;=\; H(Z_k) - \mathbb E_\theta\!\left[\tfrac12 \ln\!\big(2\pi e\,\sigma_k^2(\theta)\big)\right],$$

with $H(Z_k)$ from held-out Gaussian-mixture cross-entropy on posterior draws, and the posterior signal-to-noise ratio defined as $\mathrm{SNR}_k = \mathrm{Var}_\theta(\mu_k)/\mathbb E_\theta[\sigma_k^2]$.

| model | $z$ | $I(Z_k;\theta)\pm$SE [nat] | posterior SNR | $\eta_{\mathrm{post}}(f_1)$ | $\hat\eta_{\mathrm{post}}(f_1)$ | $\hat\eta_{\mathrm{post}}(f_1{+}f_2)$ |
|---|---|---|---:|---:|---:|---:|
| TT | 0 | 1.984 ± 0.002 | 55.4 | 0.545 ± 0.005 | 0.531 ± 0.006 | 0.903 |
| TT | 1 | 0.919 ± 0.003 | 5.1 | 0.761 ± 0.014 | 0.770 ± 0.018 | 0.957 |
| TT | 2 | 4.304 ± 0.003 | 5490.8 | 0.347 ± 0.003 | 0.347 ± 0.003 | 0.601 |
| TT | 3 | 2.646 ± 0.003 | 204.7 | 0.449 ± 0.004 | 0.447 ± 0.004 | 0.838 |
| TT | 4 | 3.441 ± 0.003 | 986.5 | 0.370 ± 0.004 | 0.371 ± 0.004 | 0.758 |
| EE | 0 | 1.343 ± 0.003 | 11.5 | 0.737 ± 0.009 | 0.756 ± 0.012 | 0.842 |
| EE | 1 | 3.835 ± 0.003 | 2179.5 | 0.352 ± 0.003 | 0.348 ± 0.004 | 0.663 |
| EE | 2 | 2.180 ± 0.003 | 78.6 | 0.576 ± 0.006 | 0.574 ± 0.006 | 0.963 |
| EE | 3 | 2.724 ± 0.003 | 234.1 | 0.493 ± 0.005 | 0.493 ± 0.005 | 0.864 |
| EE | 4 | 1.535 ± 0.003 | 17.7 | 0.811 ± 0.006 | 0.842 ± 0.011 | 0.842 |
| EE | 5 | 4.176 ± 0.003 | 4278.3 | 0.290 ± 0.003 | 0.289 ± 0.003 | 0.590 |

**Table T5.3.** Evaluated on T2. The last column anticipates §6 ($f_2$ is the second-stage coordinate, and the combined account is defined there). The SNR column settles a decisive question: the amplitude posteriors are near-deterministic (TT $z_2$ at 5,491 and EE $z_5$ at 4,278), so their structured stage-1 residuals cannot be dismissed as detail below the noise level. They are real stored information. The data-processing-inequality check $\hat I(Z;f) \le \hat I(Z;\mu_k)$, this stage's pre-registered sanity condition, holds for every candidate on both models.

---

#### 5.x The amplitude sector, recovered blind

For multipoles above the reionization regime, primary CMB spectra respond to the scalar amplitude and the optical depth almost exclusively through the damped combination

$$C_\ell \;\propto\; A_s\,e^{-2\tau},$$

so $(\tau, A_s)$ is degenerate in TT and the degeneracy is broken only by low-$\ell$ polarization. This subsection collects in one place every blind measurement of that structure, namely of the $-2$ exponent, although the measurements arise at different points of the pipeline. The known physical combination is never referenced anywhere inside the pipeline, the measurements are methodologically independent, and the two checkpoints agree.

##### F5.5 — The amplitude latent against the textbook combination

![F5.5 — amplitude latent against ln(A_s e^{-2 tau}), both checkpoints](paper/figs/amplitude_scatter.png)

**Figure F5.5.** The amplitude latent's posterior mean against $\ln(A_s e^{-2\tau})$ for both checkpoints: tight monotone curves. The physical combination is computed here only to display the result. It is computed nowhere inside the pipeline.

##### T5.2 — Every blind measurement of the −2 exponent

**Measurement 1: the discovered forms themselves.** The canonical coordinate of EE $z_5$ is literally $A_s e^{-2\tau}$ (complexity 5, R_SR 1.00, cluster cohesion 1.00), recovered by a search that was never shown the combination. At the saturation slice, the TT front's amplitude form is the affine expression $A_s(\tau - 0.598)$, and the EE front carries $A_s(\tau - 0.579)$. Both constants match the prediction of a first-order Taylor expansion. Linearising about the prior midpoint $\bar\tau$:

$$e^{-2\tau} = e^{-2\bar\tau}\big[1 - 2(\tau-\bar\tau)\big] + \mathcal O\big((\tau-\bar\tau)^2\big) = -2e^{-2\bar\tau}\left(\tau - \bar\tau - \tfrac12\right) + \ldots,$$

so within the prior box the combination is MI-equivalent to $A_s(\tau - c)$ with $c = \bar\tau + \tfrac12 = 0.570$ ($\bar\tau = 0.07$). The discovered constants sit within 1.5–5 % of it.

**Measurement 2: the derivative ratio over all top forms.** Because ratios of partial derivatives are invariant across the search's equivalence class (§3), the exponent can be read as

$$r \;=\; \frac{\partial f/\partial\tau}{\partial f/\partial \ln A_s}$$

evaluated at the prior midpoint, for every top form of the unrestricted six-input search. The result is $r = \mathbf{-1.974 \pm 0.018}$ for TT ($n=5$ seeds) and $\mathbf{-1.993 \pm 0.008}$ for EE ($n=5$). This is a property of the whole front population rather than of one fortunate expression, and it holds in every hyperparameter configuration of the §4 sweep, where $r$ stays between about $-1.97$ and $-2.00$.

**Measurement 3: the frozen, answer-agnostic constant-ratio detector.** For *every* variable pair $(i,j)$ with non-negligible sensitivity, the detector computes the ratio field $\rho_{ij} = (\partial f/\partial u_i)/(\partial f/\partial u_j)$ over the anchor points and flags pairs whose ratio is constant, meaning a coefficient of variation below 5%. For flagged pairs it reports the raw-coordinate slope $r^{\mathrm{raw}}_{ij} = \rho_{ij}\, w_j/w_i = (\partial f/\partial\theta_i)/(\partial f/\partial\theta_j)$. The detector is not told which pair to examine. The $(\tau, \ln A_s)$ pair emerges with $r^{\mathrm{raw}} = \mathbf{-2.0000}$ (coefficient of variation 0.000, valid on 100% of anchor points) in the summaries of TT $z_4$ and EE $z_5$. The zero spread is an algebraic identity and is itself evidence: whenever a form depends on $(\tau, A_s)$ only through the product $m = A_s e^{-2\tau}$, that is, whenever $f = F(m,\text{shape})$, then $r \equiv -2$ identically. The latent-level values from the positive control agree: $r_{\mathrm{lin}} = -1.977$ for TT (stored value $-1.988$) and $-1.995$ for EE (stored value $-1.9995$).

**No fourth measurement is available from the observable domain.** The decoder-template analysis of §8 does not produce one. The $(\tau, \ln A_s)$ spectral templates are nearly antiparallel in both designs, so the fitted amplitude split drifts along a degenerate ridge. EE's value of $-1.87$ is one point on that ridge (the value ranges from $-1.67$ to $-2.32$ across fit variants), and TT gives $+0.351$ (ranging from $+0.60$ to $-2.85$). The pre-registered decoder-side criterion fails on both models (§8). All three surviving measurements come from the encoder side.

**An unplanned fourth appearance, inside another latent's residual.** The second-stage coordinate of the EE $H_0$ latent (§6) is literally $A_s e^{-2\tau}/\omega_b^2$, whose $(\tau, \ln A_s)$ ratio is $-2.0000$ with zero spread. It was found twice, by two independent searches: the additive stage-2 pass, and again the interaction-aware rerun of §6.x.

Both regimes matter, and their agreement is the result. TT is the arm in which the degeneracy is present, so the model is forced into the combination. EE is the arm in which the degeneracy is broken: the model could in principle separate $A_s$ and $\tau$, yet its amplitude latent still organises around $A_s e^{-2\tau}$.

##### F5.7 — Why TT reports an affine form and EE the literal exponential

![F5.7 — exp(-2 tau) over the prior with its best affine fit](paper/figs/F5_7_affine_vs_literal.png)

**Figure F5.7.** $e^{-2\tau}$ over the prior range $\tau\in[0.01, 0.13]$ with its best affine fit. The deviation panel shows a maximum deviation of 0.52%. Over this range the two forms are statistically indistinguishable, since they tie in MI, so the parsimony criterion deterministically prefers the cheaper affine form whenever nothing else separates them. The difference between the forms reported for TT and EE is therefore structural rather than an accident of the random seed. This is a pure function plot involving no data.

---

### 6. The latent map contains structure beyond two symbolic coordinates

Stage 2 runs blind symbolic regression on the stage-1 residual $e_1 = \mu_k - h(f_1)$, again with all six inputs and five seeds, yielding a second coordinate $f_2$ and the hierarchical account

$$\mu_k \;\approx\; h(f_1) + g(f_2),$$

with $g$ a second cross-fitted monotone calibration fit to $e_1$. An interaction-aware rerun (§6.x) then exposes the stage-1 prediction $\hat f_1 = h(f_1)$ as an additional input. The null test consists of identical searches against row-shuffled residuals. The combined posterior fraction $\hat\eta_{\mathrm{post}}(f_1{+}f_2) = \hat I(Z_k;\, h(f_1)+g(f_2))/\hat I(Z_k;\mu_k)$ is scored on T2 with the same posterior draw as T5.3.

**Result.** A recurrent second coordinate exists for every latent and produces a large gain in $\hat\eta_{\mathrm{post}}$, but the stage-2 residuals remain structured under both the additive model and the enriched one. The finding that holds globally is the persistence of structure beyond two coordinates. **Next question:** is the failure to reach a complete account a property of the representation, or of the assumed additive form? Section 6.x answers this for one latent.

#### F6.1 — What the second coordinate buys

![F6.1 — stage-2 gain in posterior fraction](paper/figs/F6_1_stage2_gain.png)

**Figure F6.1.** For each latent, a paired-marker segment connects $\hat\eta_{\mathrm{post}}(f_1)$ to $\hat\eta_{\mathrm{post}}(f_1{+}f_2)$: values of 0.29–0.84 rise to 0.59–0.96, against the dashed saturation line at 1.0. Every latent improves, and none reaches saturation. EE $z_4$ is the one latent that does not move (0.842 to 0.842): its $f_2$ is the bare parameter $\tau$, which a one-dimensional monotone recalibration cannot add to an account already built on $-A_s/(\tau - 0.445)$. Evaluated on T2.

#### T6.1 — Second coordinates

The own-latent probe $R^2$ column is computed by the instrument of §9 and is placed here so that §9 can remain descriptive.

**TT**

| $z$ | canonical $f_2$ | support | shape-sector | R_SR | $\hat I(f_2;e_1)\pm$SE | $R^2(e_1)$ | comb. $R^2(\mu)$ | $\hat\eta_{\mathrm{post}}(f_1{+}f_2)$ | own-latent probe $R^2$ |
|---|---|---|---|---:|---|---:|---:|---:|---:|
| 0 | $n_s\,(H_0 + 1325.0747\,\omega_{\mathrm{cdm}})$ | $\{\omega_{\mathrm{cdm}}, H_0, n_s\}$ | yes | 0.80 | 1.106 ± 0.011 | 0.887 | 0.989 | 0.903 | 0.012 |
| 1 | $n_s/\ln\!\big({-H_0}/(\tau - 0.44653893)\big) + \omega_b$ | $\{\omega_b, H_0, \tau, n_s\}$ | no | 0.80 | 0.888 ± 0.014 | 0.802 | 0.981 | 0.957 | 0.056 |
| 2 | $n_s^2\,\omega_b\,\tau\,/\big(\omega_{\mathrm{cdm}}\tau + 3.1009{\times}10^{-4}\big)$ | $\{\omega_b, \omega_{\mathrm{cdm}}, \tau, n_s\}$ | no | 0.80 | 1.058 ± 0.012 | 0.864 | 0.993 | 0.601 | 0.010 |
| 3 | $H_0/(\omega_b^2\,\omega_{\mathrm{cdm}}^2)$ | $\{\omega_b, \omega_{\mathrm{cdm}}, H_0\}$ | yes | 0.80 | 1.087 ± 0.014 | 0.863 | 0.989 | 0.838 | 0.256 |
| 4 | $\ln(H_0)/(n_s\,\omega_b)$ | $\{\omega_b, H_0, n_s\}$ | yes | 0.80 | 1.186 ± 0.013 | 0.908 | 0.993 | 0.758 | 0.224 |

**EE**

| $z$ | canonical $f_2$ | support | shape-sector | R_SR | $\hat I(f_2;e_1)\pm$SE | $R^2(e_1)$ | comb. $R^2(\mu)$ | $\hat\eta_{\mathrm{post}}(f_1{+}f_2)$ | own-latent probe $R^2$ |
|---|---|---|---|---:|---|---:|---:|---:|---:|
| 0 | $A_s\,H_0\,\omega_{\mathrm{cdm}}/n_s$ | $\{\omega_{\mathrm{cdm}}, H_0, A_s, n_s\}$ | no | 0.80 | 0.401 ± 0.010 | 0.406 | 0.955 | 0.842 | 0.057 |
| 1 | $A_s\,e^{-2\tau}/\omega_b^2$ | $\{\omega_b, \tau, A_s\}$ | no | 0.80 | 1.281 ± 0.013 | 0.921 | 0.995 | 0.663 | 0.062 |
| 2 | $n_s\,\big(A_s + 1.0352{\times}10^{-5}\,\omega_b\,\omega_{\mathrm{cdm}}^2\big)$ | $\{\omega_b, \omega_{\mathrm{cdm}}, A_s, n_s\}$ | no | 0.80 | 1.765 ± 0.013 | 0.966 | 0.998 | 0.963 | 0.083 |
| 3 | $H_0/\omega_{\mathrm{cdm}}^2$ | $\{\omega_{\mathrm{cdm}}, H_0\}$ | yes | 0.80 | 1.065 ± 0.013 | 0.880 | 0.992 | 0.864 | 0.221 |
| 4 | $\tau$ | $\{\tau\}$ | no | 0.80 | 0.702 ± 0.011 | 0.033 | 0.957 | 0.842 | 0.583 |
| 5 | $H_0\,\omega_{\mathrm{cdm}}/n_s$ | $\{\omega_{\mathrm{cdm}}, H_0, n_s\}$ | yes | 0.80 | 1.250 ± 0.014 | 0.919 | 0.993 | 0.590 | 0.081 |

**Table T6.1.** "Shape-sector" marks supports containing no amplitude-sector parameter. $R^2(e_1)$ is the calibrated account of the residual, and "comb. $R^2(\mu)$" is that of $h(f_1)+g(f_2)$ against the latent. The $\eta$ and $R^2$ columns are evaluated on T2.

**Null floor for the MI column.** Searches against shuffled residuals reach 0.066–0.074 nat for the true TT $z_2$ residual and 0.009–0.060 nat for EE $z_5$. The largest null value anywhere (0.074 nat) sits 5.4 times below the smallest real value (0.401) and 24 times below the largest (1.765). Every stage-2 residual nevertheless fails the frozen residual audit, so the hierarchy continues beyond two levels. The $f_2$ of EE $z_1$ is the fourth appearance of the $-2$ exponent (§5.x).

---

#### 6.x A multiplicative amplitude–shape interaction defeats the additive hierarchy

This subsection demonstrates the specific mechanism in the TT amplitude latent. That latent's top-front forms are products of an amplitude factor and a shape factor, and an additive two-level account $h(f_1) + g(f_2)$ cannot absorb a multiplicative interaction. The pre-registered separation criterion for the amplitude latents requires the support of $f_2$ to contain only shape-sector parameters. This criterion is **met on EE**, where $f_2 = H_0\,\omega_{\mathrm{cdm}}/n_s$, and **not met on TT**, which is recorded as a deviation. Concretely, the $f_2$ of TT $z_2$ retains $\tau$, and clamping $\tau$ to its midpoint costs 0.20 nat of MI against $e_1$. The form also falls outside the frozen equivalence class relative to its shape-only approximation, with a Spearman correlation of 0.92 against the 0.98 threshold and a gradient distance of 0.127 against the 0.05 threshold.

The **interaction-aware rerun** settles whether this is real structure or a limitation of the assumed search form. It comprises 55 runs plus 6 controls (98 core-hours), with the stage-1 prediction $\hat f_1 = h(f_1)$ exposed as a seventh input and reconstructed exactly (T2 reconstruction error of 0.0 on every latent). It returns three verdicts:

1. **The TT non-separation is real structure, not an artifact of the assumed additive form.** Given the chance to express the interaction directly, the search for TT $z_2$ returns the same $\tau$-bearing coordinate as the additive run and does not use $\hat f_1$ at all, even though the search demonstrably used $\hat f_1$ elsewhere in the same batch. The additive hierarchy is therefore not failing for lack of expressiveness.
2. **EE $z_0$ improves but remains unresolved.** Its $f_2$ becomes the interaction form $-A_s H_0^2(\hat f_1 - 10.8708)$, found by every seed, lifting R_SR from 0.80 to 1.00 and the MI against $e_1$ from 0.401 to 0.499 nat. Yet the joint level-set error (§7) barely moves, from 0.060 to 0.062 ± 0.002 (0.067 on T2, against a predicted band of 0.046–0.093), and the stage-2 residual account remains at $R^2 = 0.39$. This latent needs a third coordinate, not a better second one.
3. **The additive account is otherwise robust.** Eight of eleven latents return the identical canonical $f_2$ in the enriched input space, where identity is judged by the frozen semantic-equivalence tests rather than by comparing expression strings. The representative for TT $z_0$ differs only in a fitted constant (1325.07 versus 1311.27). The residual coordinate of EE $z_1$ is again literally $A_s e^{-2\tau}/\omega_b^2$, and the EE amplitude criterion is still met. Where interactions are real, the machinery does detect them: TT $z_4$ finds more residual MI in the enriched space (2.20 to 2.40 nat, with the combined $\hat\eta_{\mathrm{post}}$ rising from 0.758 to 0.787), and the recurrence of TT $z_3$ strengthens to R_SR 1.00. Every stage-2 residual still fails the audit, and no latent's status changes. Searches against shuffled residuals in the seven-input space reach 0.010–0.053 nat.

The scope of this claim is deliberately narrow: the multiplicative interaction is demonstrated at TT $z_2$, and it is not asserted of every latent.

---

### 7. The joint coordinate pair, not the primary alone, is the latent's coordinate system

Association, however sufficient and recurrent, does not yet establish a coordinate. The defining test is interventional. The level-set test holds the discovered coordinate fixed, moves everything else along the nuisance directions, and measures how much the latent moves. Within equal-count bins of the coordinate (joint quantile cells for the pair $(f_1, f_2)$), disjoint row pairs are drawn to maximise separation in the complementary, nuisance $u$-coordinates, and the invariance error is

$$E_{\mathrm{inv}}(f) \;=\; \frac{\mathbb E\big[(\mu_k - \mu_k')^2 \,\big|\, \text{level-set pair}\big]}{2\,\mathrm{Var}(\mu_k)},$$

normalised so that randomly matched pairs score 1. The frozen rule has two conditions. First, $E_{\mathrm{inv}} \le 0.05$. Second, the response at matched nuisance must be one-dimensional: with the nuisance parameters held fixed, the pooled response of $\mu_k$ against $f$ must collapse onto a single curve, with cross-fitted spline $R^2 \ge 0.9$.

**$f_1$ alone fails everywhere, and the joint pair restores invariance.** $E_{\mathrm{inv}}(f_1)$ ranges from 0.051 to 0.226 against the threshold of 0.05, a failure for every latent on both models, and an informative one. The response condition passes throughout ($R^2$ of 0.906–0.955), so this is not a confounded response but the structured residual of §5 appearing interventionally. Adding $f_2$ reduces $E_{\mathrm{inv}}$ by roughly an order of magnitude wherever the test is defined: TT $z_0$ falls from 0.205 to 0.022, TT $z_3$ from 0.122 to 0.013, EE $z_1$ from 0.169 to 0.023, EE $z_2$ from 0.164 to 0.014, EE $z_3$ from 0.086 to 0.014, EE $z_4$ from 0.051 to 0.031, and the EE amplitude latent $z_5$ from 0.226 to 0.029 (T2 confirmation 0.030, response $R^2$ of 0.992). Seven of the eight testable latents pass. For three TT latents ($z_1$, $z_2$, $z_4$) the union support fills all six parameters once $f_2$ is added, leaving no nuisance direction to vary. $E_{\mathrm{inv}}$ is undefined there, only the response conditions provide evidence ($R^2$ of 0.981–0.995), and these cases are recorded in the register of deviations as untestable for lack of nuisance directions rather than counted as passes. **EE $z_0$ is the one joint failure**, at 0.060 ± 0.002. That value lies inside the band its own calibration predicts (0.045–0.091), so the failure reflects the residual rather than an instrument artifact, and it is the localised obstacle behind the "unresolved" status of §10. The null results, in the same units, are far away: level sets built from shuffled forms score 0.81–2.20 (TT) and 1.59–1.81 (EE), transfers of a coordinate to the wrong latent score 0.23–2.79, and the tightest margin anywhere is a factor of 8. T1 pairs, T2 confirmation.

---

### 8. Observable-domain triangulation: agreement where identifiable, and a structural non-identifiability

The last instrument leaves the parameter domain entirely. Automatic differentiation through the stored decoder gives the **decoder-effect template** of latent $k$,

$$d_k(\ell) \;=\; \frac{\partial\, \mathrm{Dec}(z)_\ell}{\partial z_k},$$

evaluated at the T1 mean latent, with a spread computed over 64 T1 posterior-mean rows. The decoder's standardised output is converted to the physical effect $\partial \log_{10} D_\ell/\partial z_k$ using the stored per-bin scale. Each $d_k$ is decomposed onto data-driven *parameter* templates $t_j(\ell) = \partial\log_{10}D_\ell/\partial u_j$ by least squares,

$$d_k(\ell) \;\approx\; \sum_j a_{kj}\, t_j(\ell),$$

and the loading vector $a^{*}_k$ is compared against the symbolic sensitivity signature $g_j$ of §5 through $\cos(a^{*}, g)$. In raw parameter units the loadings are $b_j = a_j/w_j$, and the decoder-side amplitude ratio is $r_{\mathrm{dec}} = b_\tau/b_{\ln A_s}$.

**Positive result.** The decomposition is essentially complete, and the decoder-side loadings agree with the symbolic sensitivity signatures. For the shape sector this is a cross-domain confirmation of which parameters each latent moves. **Negative result.** The $(\tau, \ln A_s)$ templates are nearly collinear in both designs, so the amplitude split lies along a degenerate ridge and is not identifiable. The frozen criterion fails on both models, and the ratio it produces drifts across fit variants. The decoder therefore yields no fourth measurement of the $-2$ exponent. **Next question:** is a coordinate a property of its own latent, or of the latent space as a whole? (§9.)

#### F8.1 — Decoder-effect atlas

![F8.1 — decoder effect curves, TT-only](experiments/decoder_effect_lcdm_tt_beta3e-4_curves.png)

![F8.1 — decoder effect curves, TT+EE-lowl](experiments/decoder_effect_lcdm_tt_ee_lowl_curves.png)

**Figure F8.1.** $d_k(\ell)$ for every latent of each checkpoint (anchor curve plus the mean ± spread over 64 T1 posterior-mean rows) with the template reconstruction overlaid.

#### F8.2 — Cross-domain agreement, honestly weighted

![F8.2 — cosine agreement per latent](paper/figs/F8_2_agreement.png)

**Figure F8.2.** $\cos(a^{*}, g)$ per latent, ranging from 0.77 to 1.00: the decoder-side loading vector compared against the symbolic sensitivity signature $g_j$ of §5. Shape-sector points are drawn solid. The amplitude-latent points are drawn hollow because their cosines rest partly on components that drift along the ridge of F8.3, which is the qualification behind the phrase "where identifiable" in the section title.

#### F8.3 — The ridge: why the decoder provides no fourth measurement

![F8.3 — template collinearity and the drifting amplitude split](paper/figs/F8_3_ridge.png)

**Figure F8.3.** (a) $t_\tau(\ell)$ and $-t_{\ln A_s}(\ell)$ overlaid after scaling, per channel. They lie on top of each other, with uncentered cosines of $-0.9996$ (TT channel), $-0.9770$ (EE channel), and $-0.9902$ for the EE concatenated design, at condition numbers 70.2 and 14.2. Moving $\theta$ along $(\delta\tau, \delta\ln A_s) \propto (1, 2)$, the direction that holds $A_s e^{-2\tau}$ fixed, leaves these spectra essentially unchanged. (b), (c): the fitted amplitude split for the amplitude latent of each checkpoint, in $b = a/w$ units, across four fit variants (ordinary least squares, $(2\ell{+}1)$-weighted, half-bandwidth templates, and anchor-point curve). Every variant lands on the same grey ridge line with essentially no change in the decomposition $R^2_W$, while the implied $r_{\mathrm{dec}}$ slides along the ridge: $-1.87$, $-1.67$, $-1.77$, and $-2.32$ for EE, and $+0.35$, $+0.60$, $+0.60$, and $-2.85$ for TT. The dashed line marks where $r_{\mathrm{dec}} = -2$ would sit. The panel works in the scaler-standardised design space ($T_{\mathrm{norm}} = T_{\mathrm{phys}}/\sigma$). Raw physical templates do not reproduce the quoted cosines.

**The decoder-side criterion, condition by condition.** The criterion has three frozen conditions, and it fails on both models. The **amplitude-sector mass** condition, $(|a_\tau| + |a_{\ln A_s}|)/\sum_j |a_j| \ge 0.8$, returns 0.64 on TT and 0.79 on EE, a failure on both, though on EE only barely. The condition **$|r_{\mathrm{dec}} + 2| \le 0.3$** fails outright on TT, where $r_{\mathrm{dec}} = +0.351$. On EE it returns a nominal pass at $-1.873$, which we classify as unidentifiable rather than accept as a result: across fit variants the same quantity spans $-1.67$ to $-2.32$, so the nominal pass reflects which fit happened to be run first, not a property of the decoder. The condition on the **decomposition quality, $R^2_W \ge 0.8$**, passes comfortably on both models, at 1.000 and 1.000. Indeed the templates account for the decoder effect across all latents, with $R^2_W$ of 0.988–1.000. The stage's machinery works. What the design cannot express is the split within the $(\tau, \ln A_s)$ pair.

**What survives as identifiable.** Two things survive. The first is the set of shape-sector coefficients: $\omega_b = -0.52$ for TT $z_0$ and $n_s = +0.47$ for TT $z_3$, $\omega_b = +0.42$ with $n_s = -0.35$ for EE $z_2$, and $n_s = +0.43$ for EE $z_3$. The second is the projection of the fitted $(\tau, \ln A_s)$ loading onto the degeneracy-*breaking* direction $(-2, 1)/\sqrt5$, which for EE $z_5$ is 0.047 and is stable across all four fit variants (0.046, 0.048, 0.047, 0.048). What does not survive: the component along the degenerate direction, $r_{\mathrm{dec}}$, and the amplitude mass, all reported for completeness rather than as claims. The scope is per checkpoint, and the mechanism, template collinearity, is a property of the observable design rather than of either encoder.

---

### 9. Degeneracy breaking splits rather than duplicates the amplitude sector

Two instruments interrogate the latent *space* rather than single latents: sparse cross-validated linear probes, which locate the latents from which each discovered coordinate can be decoded, and slab-conditional MI, which distinguishes redundancy from synergy between latents. The probes predict the rank-Gaussianised coordinate from all latents along a lasso regularisation path (sufficiency is defined throughout up to a monotone recalibration). The **carrier set** $A^{*}$ is the smallest subset of latents whose probe performance lies within one standard error of the all-latents reference, and a coordinate is called *axis-aligned* precisely when $A^{*}$ is exactly its own latent. Redundancy is scored as

$$\mathrm{red}(b\,|\,a) \;=\; 1 - \frac{\hat I(z_b; f \mid z_a)}{\hat I(z_b; f)},$$

with the conditional MI estimated over equal-count slabs of the conditioning latent. The slab approximation biases the conditional MI upward, which works against detecting redundancy and is therefore conservative for redundancy claims. The null tests are shuffled probes and MI floors computed with shuffled coordinates.

**The number of amplitude latents is a blind, model-level signature.** As F2.2 already showed, TT carries **one** amplitude-sector latent and EE carries **two**, with $z_4$ anchored to $\tau$ and $z_5$ carrying the damped combination. This is visible in the raw parameter MI before any symbolic search runs. Degeneracy breaking is therefore legible in how the latent space is organised, not only in its coordinates.

**Split, not duplicated.** After the symbolic analysis, the EE τ-direction turns out to be carried essentially by $z_4$ alone: its carrier set $A^{*} = \{z_2, z_4\}$ is the smallest in either model, and $z_4$ decodes its own coordinate at $R^2 = 0.946$. If the two amplitude latents were redundant copies, conditioning one on the other would destroy information. Instead it *creates* information: conditioning the information $z_1$ holds about $A_s e^{-2\tau}$ on $z_5$ raises it from 0.013 to 0.473 nat. Nor is this an isolated case. **No redundant pair exists in either model, and every conditional between the top two carriers is synergistic**, with redundancy scores from $-3.99$ to $-34.63$.

**Primary coordinates are anchored to their own latents, while the remainders are distributed.** Every canonical $f_1$ is linearly decodable from its own latent at rank-normal $R^2$ of 0.88–0.95, and the latent's own axis always lies inside the carrier set. But it is never the only member: axis-alignment is false for all 11 coordinates, so the remaining information is spread across the latent space. The residual coordinates $f_2$ are genuinely distributed by comparison, with own-latent $R^2$ of 0.01–0.58 (per-latent values in T6.1). The shuffled-probe null sits at a maximum $R^2$ of essentially zero, with shuffled-coordinate MI floors of about 0.001 nat, so none of this reflects mere probe capacity. T1 probes, T2 confirmation.

---

### 10. The symbolic latent atlas

This section collects the final classification. Under the frozen criteria, **10 of the 11 latents across the two checkpoints reach the status "primarily interpreted", with one explicitly unresolved case** (EE $z_0$). The per-latent evidence has already been presented: $f_1$ and its recurrence in T4.1, the η ladder in F5.1 and T5.3, $f_2$ in T6.1, and the level-set outcomes in §7.

**The status definitions, as frozen.** *Interpreted* requires a minimal stable support $S^{*}$, R_SR ≥ 0.8, $\eta_S \ge 0.95$, a residual-audit pass, $\eta_{\mathrm{post}} \ge 0.95$, and a level-set pass. *Primarily interpreted* relaxes exactly one requirement: the residual audit fails, the residual is structured, and $f_2$ is documented, while the rest ($\eta_S \ge 0.95$, R_SR ≥ 0.6, and a level-set pass) still holds. *Subspace/mixed* covers latents that admit no one-dimensional account but do admit one over a subspace of at most three latents, and *unresolved* covers everything else. No latent in this study reaches "interpreted", and that is a statement about the representation rather than about the instruments.

**What "primarily interpreted" licenses.** It licenses four statements. The latent has a recurrent one-dimensional symbolic primary coordinate that saturates its own variable support ($\eta_S \ge 0.99$ for all ten). The coordinate is stable across search seeds (R_SR ≥ 0.8, with eight of eleven at 1.00). Holding the pair $(f_1, f_2)$ fixed while moving everything else leaves the latent approximately unchanged, at or below the frozen 0.05 threshold. And the pair accounts for between 0.59 and 0.96 of what the latent physically stores.

**What it does not license.** It does not license the claim that the latent is *explained*: no latent passes the full sufficiency bar, and the stage-1 and stage-2 residuals are structured in every case. It does not license any claim across VAE training seeds, because the representation-stability replicate was never run, so every statement is specific to its checkpoint. It does not license any claim of axis-alignment, because the residual information is distributed across the latent space for all 11 latents. And for the three latents whose joint support fills the whole parameter space (TT $z_1$, $z_2$, $z_4$), it does not license an interventional level-set pass, because no nuisance direction remains to test, and a missing test is not a pass.

**What "unresolved" means for EE $z_0$.** It does not mean the coordinate is wrong: its $f_1$ recurs at R_SR 1.00 with $\eta_S = 1.000$. The obstacle is localised and identified. The stage-2 account is the study's weakest ($R^2$ of 0.39–0.41), and the joint level-set error sits at 0.060–0.062 against the frozen threshold of 0.05, inside the band its own calibration predicts. The interaction-aware rerun raises R_SR to 1.00 and the MI to 0.499 nat without moving $E_{\mathrm{inv}}$. Its residual simply holds more than one coordinate's worth of structure, and a third level was not attempted.

---

## References

1. D. Piras, L. Herold, L. Lucie-Smith & E. Komatsu, *𝛽-variational autoencoders for the ΛCDM cosmology*, arXiv:2502.09810 (2025). The parent reproduction supplying both trained compressors.
2. D. Piras, H. V. Peiris, A. Pontzen, L. Lucie-Smith, N. Guo & B. Nord, *A robust estimator of mutual information for deep learning interpretability* (GMM-MI), Mach. Learn.: Sci. Technol. 4, 025006 (2023), arXiv:2211.00567.
3. A. Kraskov, H. Stögbauer & P. Grassberger, *Estimating mutual information*, Phys. Rev. E 69, 066138 (2004).
4. M. Cranmer, *Interpretable machine learning for science with PySR and SymbolicRegression.jl*, arXiv:2305.01582 (2023).
5. I. Higgins et al., *β-VAE: Learning basic visual concepts with a constrained variational framework*, ICLR (2017).
6. D. Blas, J. Lesgourgues & T. Tram, *The Cosmic Linear Anisotropy Solving System (CLASS) II*, JCAP 07, 034 (2011), arXiv:1104.2933.
