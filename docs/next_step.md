> **STATUS (2026-08-06): superseded.** This programme was made executable
> as [`docs/discovery_roadmap.md`](discovery_roadmap.md) (phases 0-10 with
> budgets and pre-registered gates) and has been carried out; results live
> in `experiments/` (final synthesis: `latent_cards_<run>.{md,json}`).
> Kept for the original motivation and derivations; section references
> (§2.1, §3, ...) in the roadmap point here.

## Core diagnosis

The remaining bottleneck is **not PySR search capacity**. The current results already show that increasing capacity mostly lets symbolic regression reconstruct more of the deterministic encoder map, while the low-complexity front is essentially saturated across hyperparameters. The amplitude direction is robust, but the shape latents still lack validated representation statements. Therefore, the next stage should move from

[
\max_f I(f(\theta);z_k)
]

to **minimal sufficient coordinates, recurrence, and intervention-based validation**. 

## 1. Define what “interpreting a latent” should mean

Let

[
\theta\in\mathbb R^6,\qquad
\mu_k(\theta)=\mathbb E_{q_\phi(z\mid x(\theta))}[z_k]
]

be the encoder posterior mean, and let

[
f_S:\mathbb R^{|S|}\to\mathbb R
]

be a symbolic coordinate using variables indexed by (S).

Because MI is invariant under invertible scalar recalibrations, the interpretation is not one literal expression but the equivalence class

[
[f_S]={h\circ f_S:h\text{ is invertible on the observed domain}}.
]

I would call (z_k) interpreted by (f_S) only when four properties hold:

1. **Sufficiency:** after fitting an arbitrary one-dimensional calibration (h),

   [
   \mu_k(\theta)\approx h(f_S(\theta_S)),
   ]

   and the residual contains little information about the remaining parameters.

2. **Minimality:** no simpler expression or strict subset (S'\subset S) explains essentially as much.

3. **Stability:** the same semantic coordinate recurs across SR seeds, data resamples, and eventually VAE training seeds.

4. **Interventional consistency:** changing nuisance parameters while keeping (f_S) fixed approximately preserves (z_k), while changing (f_S) changes (z_k).

This gives a much sharper target than “highest validation MI”.

---

## 2. First close everything possible without new SR runs

### 2.1 Build an uncertainty-aware knee readout

For each latent and each run, define the cumulative Pareto envelope

[
M_{k,s}(c)
==========

\max_{\substack{f\in\mathcal F_{k,s}\ C(f)\leq c}}
\widehat I_{\mathrm{val}}(f;\mu_k),
]

where (C(f)) is symbolic complexity.

Use the maxsize-30 runs as a temporary empirical plateau (\widehat I_k^{\mathrm{plat}}), and report

[
\eta_k(f)
=========

\frac{\widehat I(f;\mu_k)}
{\widehat I_k^{\mathrm{plat}}}.
]

Rather than fixing one arbitrary threshold, report the simplest expressions reaching (90%), (95%), and (99%), together with a **one-standard-error knee**:

[
c_k^\star
=========

\min\left{
c:
M_k(c)\geq
\widehat I_k^{\mathrm{plat}}
----------------------------

\operatorname{SE}(\widehat I_k^{\mathrm{plat}})
\right}.
]

This immediately distinguishes:

* a simple dominant coordinate;
* a simple coordinate plus meaningful residual modulation;
* an intrinsically complicated or mixed latent.

### 2.2 Pool semantic forms, not expression strings

Exact syntax recurrence will underestimate stability. For example, local Taylor forms and exponential forms can encode nearly the same direction without being algebraically identical.

Pool candidates using three increasingly permissive equivalences:

1. **Algebraic:** SymPy simplification, constant normalization, commutative ordering.
2. **Output-semantic:** evaluate on a fixed anchor set and compare rank-transformed outputs.
3. **Gradient-semantic:** compare normalized gradient fields in standardized parameter coordinates,

   [
   d_{\nabla}(f,g)
   ===============

   1-
   \mathbb E_\theta
   \left[
   \left|
   \frac{
   \nabla f(\theta)^\top\nabla g(\theta)
   }{
   |\nabla f(\theta)||\nabla g(\theta)|
   }
   \right|
   \right].
   ]

The recurrence of a semantic cluster (\mathcal C) can then be defined as

[
R_k(\mathcal C)
===============

\frac1{N_{\mathrm{seed}}}
\sum_s
\mathbf 1
\left[
\exists f\in\mathcal C
\text{ on seed }s
\text{ with }\eta_k(f)\geq 1-\varepsilon
\right].
]

Select the **simplest representative of the most recurrent sufficiently informative cluster**, rather than the highest-MI expression.

### 2.3 Generalize the hand-designed (r)-ratio

The current (r)-ratio is an excellent amplitude diagnostic, but it is answer-specific. Replace it with an answer-agnostic six-dimensional sensitivity signature.

For standardized or dimensionless coordinates (u_j), report

[
g_j(f)
======

\frac{
\mathbb E_\theta\left[
\left|\partial f/\partial u_j\right|
\right]
}{
\sum_i
\mathbb E_\theta\left[
\left|\partial f/\partial u_i\right|
\right]
}.
]

Also compute first- and total-order Sobol indices for each symbolic candidate. This provides, for every shape latent:

* dominant variables;
* important interactions;
* whether the encoded direction is approximately global or strongly state-dependent.

It is a natural answer-agnostic replacement for textbook regex scans.

---

## 3. Test sufficiency directly, rather than only through MI

For each selected candidate (f), fit a flexible scalar calibration (h) by cross-fitting:

[
\widehat\mu_k=h(f(\theta)).
]

A monotone spline is appropriate when the relationship is expected to be invertible; a general one-dimensional spline can be used otherwise. Define the held-out residual

[
e_k(\theta)
===========

\mu_k(\theta)-h(f(\theta)).
]

Then test whether (e_k) remains predictable from (\theta). Useful diagnostics are:

[
R^2_{\mathrm{res}}
==================

R^2\bigl(e_k\leftarrow\theta\bigr),
]

and

[
I(e_k;\theta_j),\qquad j=1,\ldots,6.
]

The shuffled-target controls already provide a natural null level. A candidate is close to sufficient when residual prediction and residual MI are near that null.

This also supports a hierarchical interpretation. When residual structure remains, run a second discovery stage targeting the residual or conditional information:

[
f_2
===

\arg\max_f
I(\mu_k;f\mid f_1)
------------------

\lambda C(f).
]

The result can then be stated as:

[
z_k
\approx
h(f_1,f_2),
]

with (f_1) the primary physical coordinate and (f_2) a secondary modulation. This is likely more informative for the shape latents than forcing one complexity-20 composite into a single verbal label.

---

## 4. Make variable selection genuinely blind

Since there are only six cosmological parameters, variable selection can be much more systematic than reading support from one winning expression.

For every non-empty subset (S\subseteq{1,\ldots,6}), search for the best low-complexity coordinate and construct the three-objective Pareto set

[
\left(
|S|,
C(f_S),
-\eta_k(f_S)
\right).
]

There are only (2^6-1=63) subsets. A practical staged version is:

1. Screen all 63 subsets with two seeds and reduced iterations, while retaining maxsize (20) or (30).
2. Keep the subset-complexity Pareto frontier.
3. Rerun only those finalists with five seeds and the full protocol.
4. Select the smallest stable subset whose sufficiency is statistically indistinguishable from larger subsets.

This closes the human choice of ((A_s,\tau)) and also determines whether a latent primarily depends on two variables, genuinely requires five variables, or only appears to do so because the unrestricted search reconstructs small residual effects.

The existing sweep result strongly suggests **not** using maxsize (10) for this screening: search with sufficient capacity, then slice the resulting front at reporting time.

---

## 5. Replace the empirical MI plateau with an intrinsic finite ceiling

The deterministic posterior mean causes the conceptual MI problem. The cleanest correction is to interpret the actual stochastic latent:

[
Z_k\mid\theta
\sim
\mathcal N!\left(
\mu_k(\theta),\sigma_k^2(\theta)
\right).
]

Then (I(Z_k;\theta)) is finite. Moreover,

[
I(Z_k;\theta)
=============

## H(Z_k)

\mathbb E_\theta
\left[
\frac12\log\left(2\pi e,\sigma_k^2(\theta)\right)
\right],
]

because the conditional entropy is known analytically from the encoder posterior variance. Only the one-dimensional marginal entropy (H(Z_k)) must be estimated.

For a symbolic coordinate, estimate

[
I(Z_k;f(\theta))
]

using the existing scalar–scalar GMM-MI machinery, and report the intrinsic sufficiency ratio

[
\eta_k^{\mathrm{post}}(f)
=========================

\frac{I(Z_k;f(\theta))}
{I(Z_k;\theta)}.
]

This would turn “fraction of the maxsize-30 plateau” into “fraction of the information actually stored in the stochastic latent”. The current posterior-mean analysis can remain as the high-resolution diagnostic, but the posterior-sampled score should become the principled headline metric.

---

## 6. Validate candidates through level-set interventions

Association alone does not establish that (f) is the latent coordinate. The defining test is invariance along the level sets of (f).

Using the existing 50k samples, construct matched pairs ((\theta,\theta')) satisfying

[
|f(\theta)-f(\theta')|<\delta,
]

while maximizing their distance in nuisance coordinates. Measure

[
E_{\mathrm{inv}}(f)
===================

\frac{
\mathbb E\left[
(\mu_k(\theta)-\mu_k(\theta'))^2
\mid
|f(\theta)-f(\theta')|<\delta
\right]
}{
\operatorname{Var}(\mu_k)
}.
]

A strong interpretation should have low (E_{\mathrm{inv}}), even when the unused parameters differ substantially.

The complementary test is to match nuisance variables while varying (f), and verify a stable one-dimensional response in (z_k). Existing samples can provide the initial audit; targeted CLASS/CAMB simulations around selected level sets would be the stronger final validation.

---

## 7. Connect latent meaning to its decoded spectral effect

For each latent, compute the decoder Jacobian

[
d_k(\ell)
=========

\frac{\partial,\mathrm{Decoder}(z)_\ell}
{\partial z_k}.
]

This gives an answer-agnostic observable-domain description of what changing (z_k) does to TT or EE.

Separately compute finite-difference spectral templates for all six parameters,

[
t_j(\ell)
=========

\frac{\partial C_\ell}{\partial\theta_j}.
]

Then solve, symmetrically over all parameters,

[
a_k^\star
=========

\arg\min_a
\left|
d_k-\sum_j a_jt_j
\right|_W^2
+
\lambda|a|_1.
]

Agreement between

1. the symbolic candidate’s gradient signature,
2. the parameter-template coefficients (a_k^\star), and
3. the decoder intervention pattern,

would be much stronger evidence than either SR or textbook matching alone. For shape latents, the decoder curve may also provide the clearest human-readable label: peak shift, relative peak modulation, broad tilt, damping-tail change, and so forth—but those labels should be assigned only after observing the derived curve.

---

## 8. Do not assume every factor is axis-aligned to one latent

A β-VAE does not guarantee that every scientific factor occupies exactly one latent coordinate. When no scalar candidate passes the sufficiency tests, test whether a small latent subspace does.

For a candidate (f), find the smallest latent subset (A) such that

[
I(f(\theta);Z_A)
]

is close to (I(f(\theta);Z)). Alternatively, use sparse CCA or a sparse linear probe from (Z) to (f). This separates:

* **axis-aligned factors:** one (z_k);
* **distributed factors:** a two- or three-latent subspace;
* **genuinely entangled representations.**

Similarly, two latents may encode overlapping versions of the same parameter combination. Conditional tests such as

[
I(z_i;f\mid z_j)
]

can identify redundancy.

---

## 9. Distinguish search stability from representation stability

Five PySR seeds establish search recurrence for one trained model. They do not establish that the learned representation itself is stable.

For a strong representation claim, train several VAE seeds and align latent spaces using absolute-correlation matching, CCA, or Procrustes alignment on a common parameter set. Then ask whether the same semantic candidate recurs after alignment.

This gives two distinct quantities:

[
R_{\mathrm{SR}}
===============

\text{recurrence across symbolic-search seeds},
]

[
R_{\mathrm{model}}
==================

\text{recurrence across independently trained VAEs}.
]

The current checkpoint can support a valid **per-model interpretation**. A general statement about what the architecture learns should require (R_{\mathrm{model}}).

---

## Recommended order

| Stage | Main output                                  |                                         New SR runs |
| ----- | -------------------------------------------- | --------------------------------------------------: |
| 1     | Knee tables for all 11 latents               |                                                  No |
| 2     | Semantic clustering and recurrence           |                                                  No |
| 3     | Gradient/Sobol signatures and residual audit |                                                  No |
| 4     | Blind subset selection and restricted reruns |                                                 Yes |
| 5     | Posterior-noise finite MI ceiling            | Encoder cache update, not necessarily new SR search |
| 6     | Level-set and decoder interventions          |                               Limited targeted runs |

The most useful immediate deliverable would be one **latent card** per (z_k), containing

[
\boxed{
\text{formula cluster},
S,
C,
\eta,
R_{\mathrm{SR}},
\text{sensitivity profile},
\text{residual dependence},
E_{\mathrm{inv}},
\text{decoder effect}
}
]

and one of four statuses:

* **interpreted:** minimal, recurrent, sufficient, intervention-validated;
* **primarily interpreted:** stable primary coordinate but structured residual remains;
* **subspace/mixed:** no adequate one-dimensional coordinate;
* **unresolved:** search or validation is unstable.

The highest-priority change is therefore: **implement semantic recurrence plus residual sufficiency before running more large PySR searches**. That would turn the existing fronts into actual representation claims and reveal exactly which shape latents require further experiments.
