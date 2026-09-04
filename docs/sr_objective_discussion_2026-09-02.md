# Discussion record — what SR was for

*Saved 2026-09-03 from the 2026-09-02 session; both sides of the conversation.
Companion to `docs/ols_mi_sr_mse_sr_t2_comparison_claude_output.md`, which is
the **record**. This file is the **discussion** — kept separate so the record
stays a record. Questions are quoted verbatim; answers are the worked replies.
Where an answer is reasoning rather than a repo artifact, it says so.*

**To resume:** nothing is open here any more. §5.1 was closed on 2026-09-03
(all 10 items, including the rsync). **§5.2 was closed on 2026-09-04**: the
paper-shape decision (A) was taken and the two parked campaigns (B, C) were
dropped; the write-up is `report_conclusive.md` at the repository root. §4 Q8
is the reasoning behind the decision; §6 is the follow-up discussion that
generated §5.1 items 5, 6 and 9.

---

## 3. The storyline

Written in this session and committed as **§0.1 of the record** — not duplicated
here. Four steps: (1) the aim and the `A_s·e^{−2τ}` probe; (2) what the affine
baseline actually showed, and why narrow priors are only half the diagnosis;
(3) why we then searched the residual; (4) what transfers from LLM
interpretability.

---

## 4. The eight questions

### Q1. "whats means by at high capacity the returned forms become idiosyncratic rather than convergent?"

At low maxsize (c≤5, c≤10) the five seeds tend to return the *same* algebraic
family — that is what R_SR measures, and why recurrence was a gate. Raise
maxsize to 20 and 40 and accuracy keeps improving or saturates, but the seeds
increasingly return *different* 20–30-node expressions from each other, each
fitting about equally well. **Consensus decays while accuracy doesn't.** That is
TM8.

Mechanism: at high complexity the set of expressions fitting to within noise is
enormous and degenerate. Which one you get is set by the seed's random
trajectory, not by the data. So a high-capacity form tells you about the search,
not the target.

This was the *first* internal warning that the forms weren't identified — before
the OLS baseline made it undeniable. It pairs with the hp sweep: top-of-front MI
rises 1.6 → 4.05 nat on maxsize alone, but budget-matched MI at c≤10 is flat
across every configuration. **Capacity buys fit, not discovery.**

### Q2. "why does that not mean the latents are linear"

Because "OLS wins" ranks two approximations against each other and says nothing
about the distance to the truth.

The settling number: OLS reaches NMSE ≈ 2×10⁻³. Take that residual, fit it with
gradient boosting **from the same six parameters**, and 97–99% of it comes back
— NMSE drops to ≈ 3×10⁻⁵. A nonlinear function of θ does ~60× better than the
linear one. So the 0.2% OLS leaves is *structure*, not noise; μ_k(θ) is a
smooth, essentially deterministic, genuinely nonlinear function that happens to
be 99.8% captured by a plane.

Both OLS and the ms40 expression sit ~2 orders of magnitude above the achievable
floor. What survives is a statement about **evidence, not about the latents**:
reconstruction accuracy discriminates weakly here, because a plain affine map
already reaches 10⁻³. Which is exactly the argument for selecting on a
bijection-invariant criterion — the reasoning the protocol had already
committed to. (This over-reading was corrected in commit `71b395c`.)

### Q3. "the residual is predictable doesn't this mean the complexity isn't enough at the beginning?"

Partly, but not in a way that rescues the search.

**Was the budget too small?** For the MI arm at ms20, yes, precisely: a dense
6-input affine map costs ≈25 nodes, so ms20 *cannot represent it* — that
comparison was budget-asymmetric against SR. But the MSE arm at ms40 **can**
represent it, with in-search constant optimisation, and still lost 6–9 of 11.

**Would more complexity have helped?** §2.5 says no. Replaying the stored OLS
coefficients against the returned fronts: in **38 of 55** runs OLS has lower fit
MSE than *every* equation on the front, at any complexity the search explored.
Injecting the OLS expression at its true complexity into the frozen candidate
sets, it would be retained in 43/55 and win the unchanged selection in 39/55.
**Selection never discarded affine candidates; generation never produced one.**

So the failure is **generative, not budgetary**. More maxsize gives more
idiosyncratic high-complexity forms (Q1), not convergence.

Deeper point: the residual being 97–99% predictable at *every* level means this
is not a threshold you cross. Stage-1 residuals structured 11/11, stage-2
residuals structured 11/11, the ms40 expressions still leaking f₂-dependence at
10–140× the permutation null, the OLS residual GBM-predictable. That is E4 — no
small exact description in any probed class. The hierarchy does not terminate.

### Q4. "what are the quadratic terms closing?"

The **beyond-affine gap** = the NMSE remaining after the best affine fit.
EE z3: affine 0.311% → quadratic 0.096%, so the 21 second-order terms (all
pairwise products including squares; 28 coefficients with the intercept) removed
(0.311−0.096)/0.311 = **69% of what affine left**.

Which terms carry it is itself the finding: mostly shape-sector squares and
crosses — ω_b·ω_cdm, ω_b², ω_cdm², H₀² — with τ² where the amplitude sector
enters. That is peak-height curvature, exactly where §6.1 predicts it, entering
at (Δθ/θ)² ~ 10⁻².

Readout: for 9/11 latents, 21 *exact* coefficients close 33–94% of the gap — so
what lies beyond affine is mostly ordinary smooth second-order response. The two
that resist (EE z0 at 4%, EE z4 at 8%) are where the remaining structure is
**not polynomial at all**: a pole in τ at z4, a rational form with a pole just
outside the H₀ box at z0.

### Q5. "why you are saying the limit is 2/11, isnt that what we found out?"

**You were right; the "2 of 11" framing was wrong and is retracted here.**

The ladder answered **all 11**. Step 1 (quadratic, exact, all 11) established
that 9/11 are essentially closed at second order. Step 2 ran only on the 2 that
Step 1 flagged *because those were the only 2 still open*. "2 of 11" is not a
yield or a failure rate — it is correct triage.

The caveats that actually remain are narrower:

* **Non-coverage.** Step 2 was never run on the other 9. Closing 94% of a tiny
  gap doesn't prove there is no compact coordinate in the last 6% — we just have
  no reason to look.
* **Selection.** The 2 successes are not an unbiased sample; they were
  pre-selected as the hardest cases.
* **Post-hoc.** All of it on T2 rows already read.

**The result itself.** EE z4: `A_s/τ` at complexity 3, unanimous (R_SR 1.00),
MI 0.771–0.891 nat against a 0.051–0.056 null; statistically the same class as
the old f₂ (ρ 0.986), so z4's original stage 2 was never mop-up. Hybrid 2.407%
(frozen monotone) / **1.304%** (free 1-D map), against a previous best ~1.38%
and a quadratic wall of 3.87%. EE z0: `(ω_cdm/(ω_b·(H0−85.5)))²`, R_SR 0.80,
MI 0.498–0.541 against a 0.066–0.072 null; a *different* direction from its old
f₂ (ρ 0.58), so that one **was** mop-up — plus the mechanism finding, that the
monotone calibrator turns 0.5 nat into 5% of the residual where a free map turns
it into 54%.

### Q6. "why our 'steering' failed on the decoder side? that means we cant see which latents correspond to which physical param?"

**No — attribution is fine.** G4b was not "which latent is which parameter". It
was the much narrower attempt to read the **−2 exponent from the decoder side**,
as a readout independent of the encoder.

*Why it cannot work* — this is reasoning, not something the record spells out:
above the reionization scale τ enters **only** through the prefactor e^{−2τ}, so
∂ln C_ℓ/∂τ = −2 and ∂ln C_ℓ/∂lnA_s = +1, both **constant in ℓ**. The two
response templates are therefore exactly parallel vectors in ℓ-space.
Decomposing any decoder direction onto them is ill-posed: individual
coefficients are unstable even though their combination is perfectly determined.

Which makes G4b's failure **confirmation rather than a bug** — it is the same
degeneracy the whole study is about. The only thing breaking it is the low-ℓ EE
reionization bump, where τ enters differently. And that is precisely why the
TT+EE model splits the amplitude sector into two latents while TT needs one
(E3). The physics is self-consistent throughout.

Meanwhile the decoder leg **did** deliver attribution: template decomposition at
R²_W 0.988–1.000, cos(a*, g) 0.77–1.00 — literally which ℓ-space components each
latent moves; one of five agreeing instruments. So: latent↔parameter, robustly,
five ways. Latent→the −2 coefficient *from the decoder alone*, blocked by an
exact degeneracy.

This is also why gradient attribution ∂z_k/∂C_ℓ is worth doing: encoder-side
ℓ-space attribution that never requires decomposing onto collinear templates.

### Q7. "why probing ladder is affine, quadratic, sr?"

Ordered by hypothesis-class size **and** by trustworthiness of a negative
result, cheapest and most trustworthy first.

* **Affine** — 7 coefficients, closed form, seconds. Establishes the floor: how
  much of this latent is a weighted sum? 99.8%.
* **Quadratic** — 28 coefficients, closed form, minutes. The smallest class
  expressing curvature, and still *exact least squares*: no seeds, no
  stochasticity, so a negative result here is trustworthy in a way a failed
  search never is.
* **SR** — unbounded class, stochastic, hours, and per §2.5 an unreliable
  optimizer with demonstrated false negatives.

The logic: **exhaust what exact solvers can express, so that when you finally
spend the unreliable stochastic search, you are pointing it at a target you have
*proven* is beyond every cheaper alternative.** That converts SR from "a
discovery engine whose output you must then audit" into "a last resort applied
to a pre-certified target."

It also fixes the exact pathology this study fell into. Without the ladder, SR
returns a nonlinear form and you read it as evidence the latent is nonlinear.
With the ladder you know an exact quadratic already covers most of what is there
in 9/11 — so a nonlinear form on *those* latents is search idiosyncrasy, not a
finding. §6.2: the method detects curvature where the data contain it, and its
nulls elsewhere are the physics being flat.

### Q8. "what's our aim of using sr method on the vae fitted latents? im losing my objective"

You are right that attribution does not need SR. Five instruments give
latent↔parameter and four are SR-free. If attribution were the goal, SR is
redundant. So — what could SR have been for, scored against what happened:

| | Objective | Verdict |
|---|---|---|
| **A** | "Which parameter does latent k encode?" | Raw MI answers it *before any search*. **SR redundant.** |
| **B** | "What function of the parameters is latent k?" — the stated aim | **Mostly defeated.** For 8–9/11 the answer is "a linear combination", and the data cannot distinguish the discovered form from the affine map (W1). |
| **C** | "Does the network find a physically meaningful *combination*?" | **Delivered, and a different question from A.** `A_s·e^{−2τ}` is not a parameter but a derived degenerate combination. The asymmetry that makes this SR-specific: OLS reads the −2 only *after* being handed the log-amplitude coordinate; the blind search **synthesised the logarithm itself**. Basis discovery is what a linear probe structurally cannot do. |
| **D** | "Where is the representation genuinely non-polynomial?" | **Only SR answers this**, and it did: z4's pole in τ, z0's rational curvature — both beyond every exact class tried, both landing where the physics says nonlinearity should live. |
| **E** | "Is the representation compressible at all?" | Answered **negatively and robustly**: no small exact description in any probed class (E4). A finding, not a failure. |
| **F** | Methodological | What blind SR on a scientific autoencoder does and does not establish, *with a full control programme*. Arguably the most transferable output (E6). |

**The honest reframing:**

> SR was hired to **name** the latents. Most latents turn out not to need naming
> — they are sums, and the name is the coefficient vector. What SR is
> demonstrably good for here is three narrower things: **finding the right
> basis** when the natural coordinates are not the sampled ones; **locating
> genuine non-polynomial structure** once the cheap exact classes are exhausted;
> and **being the subject of a methodological study**.

**The decision that resolves the disorientation** is not "was SR worth it" but
**which paper this is** — and the answer changes what SR was for:

* **A paper about the latents.** SR is one instrument among five, contributing
  basis discovery and the two beyond-polynomial coordinates. The deliverable is
  the attribution atlas — (w_k, template a_k, quadratic verdict, beyond-affine
  coordinate where one exists) — and SR fills the last column, only where it
  earns it. Modest, defensible, already the chosen direction.
* **A paper about the method.** SR is the *subject*, and affine parity is the
  **headline result, not an embarrassment**. Most SR-for-science papers run no
  matched classical baseline at all — and this programme caught its own problem
  with machinery pre-registered before it knew it would need it. That is a
  contribution, and a rarer one than another discovered formula.

You have unusually strong material for the second, largely written. What you do
not have — the honest gap — is a *discovery* headline strong enough to carry the
first alone: EE z4 plus the amplitude basis is real but narrow.

**Read:** the crisis is that you set out to write paper 1 and the evidence wrote
paper 2. The §6 attribution framing is the bridge — it lets you tell the latent
story *and* keep the audit as the spine: shape (a) with the negative results
load-bearing rather than buried. That is the working direction already in §7
item 8, and it looks right.

---

## 5. Open threads

### 5.1 Working order — worked through 2026-09-03

*Sequenced by dependency, not by importance: protect what cannot be recovered,
make the suite trustworthy, find out whether the list is even complete, then
close the citability gaps cheapest-first, then the new instruments. Everything
here is CPU-cheap, and none of it waits on §5.2. **Status after the 2026-09-03
pass: all 10 done.** Each item now carries what came of it.*

1. **Rsync the 330 raw campaign artifacts off Lightning — DONE 2026-09-03. The
   deadline item is closed.** CSD3 could not initiate the transfer: port-22
   egress is filtered **cluster-wide** (blocked from `login-q-2`, `login-p-1`
   and `login-q-1` alike; `github.com:22` refuses too), `ssh.lightning.ai:443`
   is a TLS endpoint with no SSH banner, `:2222` is closed, and the SOCKS proxy
   in the environment (`10.143.100.11:1081`) is unreachable and scoped to
   `131.111.0.0/16`. Only outbound 443 works. The runbook's note that this was
   "verified reachable on 2026-08-25" no longer holds and should be corrected.

   **The route that worked was the reverse one**: the studio pushed to CSD3,
   which does accept inbound SSH. A key generated in the studio was added to
   `~/.ssh/authorized_keys` here with the `restrict` option (no pty, no port or
   agent forwarding — rsync needs none of them, and it keeps a key living on a
   hosted studio from being usable as a tunnel into the cluster);
   `authorized_keys.bak-20260903` holds the prior state. CSD3 enforces TOTP MFA
   on top of the key, so the transfer needs one interactive code and cannot be
   made unattended. `rsync` was absent from the studio and had to be installed.
   76 MB moved, 1,725 files.

   **Verified on arrival**, four ways: all **330/330** raw `report.json` present
   and parsing (11 latents × 5 seeds × 3 arms × 2 objectives, `gmm_mi_ms20` and
   `mse_ms40`); the deliverable's `render_sha256` self-digest valid; all six
   `confirmation.json` **byte-identical** to the digests the studio recorded;
   and the whole comparison **rebuilt from the CSD3 copies reproduces the frozen
   payload and `docs/precision_preprocess_v1_comparison.md` exactly**, with 19
   distinct upstream files hash-checked and **zero mismatches**.

   **One provenance defect surfaced and should be fixed before any freeze.**
   `source_files` in the render artifact *and* in each `confirmation.json`
   records absolute `/teamspace/studios/this_studio/...` paths, so
   `scripts/consolidate_precision_preprocess.py`'s own `verify_artifact` refuses
   to run on CSD3 — the artifacts are pinned to a machine that no longer holds
   them. The verification above had to rewrite the prefix to proceed. Storing
   repo-relative paths would make these self-verifying anywhere. A second,
   smaller instance: the confirmations reference
   `docs/ols_mi_sr_mse_sr_t2_comparison.md`, which now lives at that path plus
   `.orig` (digest `21ca5377…`, present and matching).
2. **Test hygiene — DONE.** The failure was not the test's: `PRINT_CELLS=1` is
   a static listing of the six-cell matrix that needs no interpreter, but
   `hpc/lightning/run_precision_preprocess_consolidation.sh` checked
   `[[ -x "${PYTHON}" ]]` *before* that early exit, so it died on CSD3 where
   `.venv-lightning` does not exist. The guard moved below the listing, which
   keeps the assertion actually running on both machines instead of skipping
   it; every real invocation still refuses without the interpreter. `TODO.md`
   (stale — it describes the precision campaign, long since run) and
   `docs/zx332.code-workspace` (editor config) are removed. **Suite: 333
   passed, 0 failed.**
3. **The four failed verifiers — DONE; three confirmed open, one clean.**
   * *§7 item 1.* The §6.5 quadratic-pilot table **reproduces exactly** on an
     independent recomputation from disk — all 11 rows, every gap-closed
     percentage, both leading second-order terms per latent. The numbers are
     sound. What is missing is everything around them: no committed script, no
     `results/` or `experiments/` artifact, and §6.5's own "post-hoc,
     unregistered, T2 reused" caveat unaddressed. Step 2 has raw run
     directories (`results/lcdm_tt_ee_lowl/residual_sr_ols/` + an
     `analysis_summary.json`) and no rendered deliverable. Joint level sets
     and the second z0 round: not started.
   * *§7 item 3.* Confirmed open — no artifact mentions an OLS-index level
     set. And "one consolidator pass" is optimistic:
     `scripts/levelset_audit.py` takes its coordinate from the Phase-2
     semantics registry (`--semantic-json`), not from an arbitrary
     expression, so w·θ needs a plumbing flag first.
   * *§7 item 7.* Confirmed open — none of the wider-prior, fresh-simulation
     or description-length tests has any artifact or script.
   * *Whole-doc sweep.* Four candidate open items are stated outside §7, and
     **three are restatements**: the §2.4 "predicted (untested) corollary for
     the level sets" is what §7 item 3 would measure; §2.5's "still open from
     the full staged diagnostic" is §7 item 4; E8's "R_model/Phase 9 never
     run" is §7 item 6. The only genuine outsider is the LLM-interp trio of
     §0.1 item 4 — which is items 9–10 here, exactly as this file already
     said. **The list was complete.**
4. **The §6.1 soft spot — DONE.** Corrected in place in the record, with the
   retracted argument stated rather than silently deleted: 13× is the ratio
   0.13/0.01, while a linear fit to e^{−2τ} is governed by the absolute
   exponent span 2Δτ = 0.24, so the 99.9% restates that the box is narrow
   instead of defending against it. The bullet now carries the
   range-independent version (exact linearity in the sampled basis, at any
   prior width), which is strictly stronger, so nothing downstream moves. The
   fourth bullet's separate use of 13× is sound and is flagged as such: there
   the physics is a power of τ, where a ratio is the right measure.
5. **Train/validation gap — DONE.** `scripts/capacity_and_noise_floor.py` →
   `experiments/capacity_and_noise_floor_v1.{json,md}`, tabulated as **TM10**
   in `docs/mse_one_stage_results.md` §9.1 and read in §6.7 of the record.
   3234 front members: median val/fit 0.98–1.02 at every complexity c=1→40,
   p90 ≤ 1.10, worst of 3234 equal to 1.128. **No overfitting knee anywhere.**
   Controls: a size-40 tree absorbs 0.45% of pure-noise variance on 4,000
   rows.
6. **Determinism bound — DONE.** Same script, **TM11**. GBM floor
   4.1×10⁻⁶–9.3×10⁻⁴ of Var(μ) (reproducing §2.4's "97–99%" as 97.1–99.1%),
   and a difference-based variance estimate whose zero-separation intercept is
   ≤ 4.3×10⁻⁴ or negative for all eleven — consistent with zero — with the
   pure-d² model explaining 97.1–99.8% of the pair-gap profile. Together with
   item 5 this gives §6.7's reading: **what decays with capacity is agreement,
   not generalisation**; those high-complexity forms are non-identified rather
   than overfitted, held-out MSE is structurally blind to it, and R_SR is not.
7. **η̂_post for the OLS index — DONE, and it is the biggest result of the
   pass.** `scripts/eta_post_ols_index.py` →
   `experiments/eta_post_ols_index_v1.json`, tabulated as **§2.7** of the
   record. The plain affine index beats the canonical coordinate f₁ on η̂_post
   in **10/11** latents and the full hierarchical f₁+f₂ composite in **9/11**,
   at η̂_post 0.80–0.97, with **no DPI violation**. W2 and W4 are now table
   rows, exactly as §7 item 2 predicted. The trap was avoided as specified:
   the audit's `ols_mi` is MI against the encoder *mean* and cannot serve as
   the numerator, so MI(Z_k; w·θ) was recomputed on the ceiling study's own
   T2 posterior draw. **The single latent that resists is EE z4** — on both
   comparisons — the same latent §6.6 found genuinely beyond-polynomial. The
   information criterion and the nonlinearity ladder select the same latent
   independently.
8. **§2.5 injection replay — DONE.** `scripts/replay_ols_injection.py` →
   `experiments/ols_injection_replay_v1.json` regenerates §2.5 from the stored
   fronts and **reproduces every number**: 39/55 validation (TT 24/25, EE
   15/30), 38/55 fit-side (TT 23/25, EE 15/30), 43/55 retained (TT 24/25, EE
   19/30), 39/55 wins selection, median ratio 1.445 over the range 0.43–329,
   and both exception lists element-for-element — including the TT z2 seed-4
   split between retention and selection. It also reproduces each report's
   frozen `ols_baseline` at **0** relative error, tightening §2.5's claimed
   "< 10⁻⁶".
9. **Encoder-side gradient attribution ∂z_k/∂C_ℓ — DONE, and the structural
   prediction holds.** `scripts/encoder_gradient_attribution.py` →
   `experiments/encoder_gradient_attribution_<run>.{json,npz}`; the result is
   §6.8 of the record. One qualification had to be measured first: the input
   is ~5000-dimensional and the data manifold is 6-dimensional, and only
   **0.03–1.3%** of |g_k|² lies in the span of the physical response
   templates — so the raw per-ℓ gradient is not a safe fine-grained
   attribution, and the primary readout is its projection onto that span. On
   the projected gradient, **EE z4 puts 24.1% of its mass on the 28 EE bins
   with ℓ < 30, against 0.3–1.0% for every other latent** (24–73×; those bins
   are 0.56% of all bins, so z4 over-weights them ~43× while everything else
   sits at or below uniform), and every TT latent is at exactly 0.0000 because
   the TT encoder's input starts at ℓ = 30. The prediction is confirmed and
   **refined**: it is z4 (τ) alone that reads the reionization bump, not z4
   *and* z5 — which is the right physics, since the bump constrains τ and A_s
   then follows from the high-ℓ amplitude. EE z4 also carries the largest
   EE-channel share (0.366) and the largest on-manifold fraction (0.0134,
   10× the median) of any latent.
10. **The other two LLM-interp proposals — DONE, one positive and one clean
    negative.** `scripts/encoder_trunk_probe.py`, both modes.
    * *Layer-wise trunk probe* (`--mode probe` →
      `experiments/encoder_trunk_probe_<run>.json`): held-out ridge-probe R²
      at the standardised input, each of the three Conv→CPAct→BatchNorm
      blocks, and μ. See §6.8 of the record for the table. The result answers
      §0.1's "where does (lnA_s − 2τ) first become linearly decodable" in an
      unexpected direction — and lands on E3 again. **Everything is decodable
      from the raw input and stays so through all three conv blocks, in both
      models**, so the trunk is essentially lossless. The two models separate
      only at μ: TT collapses to τ **0.41** / lnA_s **0.63** while keeping
      lnA_s − 2τ at **0.997**, whereas TT+EE keeps τ **0.977** and lnA_s
      **0.985** as well. The degeneracy is not built up through the layers —
      **it is created by the bottleneck, and only in the model whose inputs
      cannot break it.** Which is the same fact item 9 found from the input
      side: TT structurally cannot see the ℓ < 30 window that EE z4 reads.
    * *Encoder input optimisation* (`--mode steer` →
      `experiments/encoder_input_optimisation_<run>.json`): a trust-region
      sweep over step budgets calibrated in units of one prior half-width.
      **Clean negative.** Over all 44 latent × budget cells the steering
      direction stays essentially orthogonal to every physical response
      template — **max |cos| 0.011–0.133, median 0.051** — while moving the
      target latent by 2.7 to 789 units, and shrinking the budget does not
      help. It finds adversarial directions, not physical ones: the same fact
      as item 9's on-manifold fraction, seen from the other side. Worth reporting as a methodological result: **encoder
      input optimisation is uninformative here without an explicit manifold
      constraint**, and the instrument that works is the projected gradient at
      the data point.

### 5.2 Parked — closed 2026-09-04

*Moved out of the working order on 2026-09-03: one decision, and the two
campaigns whose value depends on how it goes. Sequencing them before the
decision would be guessing, and nothing in §5.1 waits on any of them.*

**Resolution (2026-09-04).** A is decided: the write-up is a report about the
latents whose spine is the audit — the four-step storyline of §0.1 of the
record, with the affine baseline load-bearing and SR kept for the three roles
§4 Q8 identified (basis discovery, beyond-polynomial localisation, the
methodological subject). It is written as `report_conclusive.md`, which
supersedes `report.md` and adds three figures (F12.1 affine parity, F13.1 the
nonlinearity ladder, F14.1 encoder-side attribution). **B and C are dropped,
not deferred.** What that leaves unclaimed is stated in the report's §7:
the discovery-versus-constant-tuning split of the generative failure stays
unseparated, and every claim stays per-checkpoint.

A. **Decide the paper's shape** (§4 Q8). Not a task but a judgment call, and the
   live thread of this file. Everything about the write-up — which figures,
   which claims, how much of the record's §5 W1–W6 goes in the abstract — waits
   on it.
B. **The template-hybrid arm on the current pin.** `TemplateExpressionSpec` is
   already in `pysr==1.5.10` (`pysr/expression_specs.py:128`), so no upgrade, no
   v2, no parallel env. The truncated-seed ladder is the follow-on that actually
   diagnoses the generative failure: seed the 2-, 3- and 4-term affine prefixes
   and measure whether evolution *extends* them. A real campaign, and it earns
   its cost mainly if A lands on the methods paper.
C. **Phase 9 for TT.** No GPU needed: the retrained seeds already exist in the
   parent repo (`cmbvae/results/lcdm_tt_beta3e-4_seed{7,123,2024}`, complete
   checkpoints from 2026-06-08). Encoder pass + `scripts/align_latents.py`
   (absent) + ≈135 core-h. EE genuinely still needs GPU. R_model is a robustness
   claim, so what it is worth depends on which claims survive A.

---

## 6. Follow-up — 2026-09-03

*Four questions from the next session; the fifth was cut off mid-typing and is
unanswered. §6.2 and §6.3 contain **new measurements** made in answering them —
they are not in the record — **since resolved: items 5–6 of §5.1 put them
there, as TM10/TM11 and §6.7.** Bare
section numbers (§2.5, §6.1, §7) refer to the **record**, as everywhere else in
this file; this file's own sections are written "§6.2 here".*

### 6.1 "What's TM8?"

**A table in a third document** — `docs/mse_one_stage_results.md:540`, "Form
family and parameter count against the ceiling". That file numbers its tables
TM1–TM9 (T = table, M = the MSE one-stage study); §4 Q1 here and §0.1 of the
record both cite TM8 without saying where it lives.

It holds, for each of the 11 latents at ceilings c≤5 / 10 / 20 / 40, the
**dominant algebraic form family among the five seeds**, how many seeds agree,
and how many of the six parameters appear:

```text
TT z3 | separable 5/5 | separable+log 2/5 | coupled+log 1/5 | coupled+log 2/5 | 2 5 5
EE z0 | coupled   3/5 | coupled      5/5  | coupled+log 3/5 | coupled     3/5 | 3 5 5
EE z4 | separable 5/5 | separable+log 3/5 | coupled+log 2/5 | c+log+exp   2/5 | 2 3 5
```

TT z3 at c≤20 is the sharpest cell in the table: the dominant family holds
**1 of 5** — all five seeds returned a different family.

Three readouts; the first is the one §4 Q1 invokes. **Consensus decays with
capacity** — at c≤5 seven of eleven latents have 5/5 seed agreement, by c≤40 the
dominant family usually holds 2–3 of 5. **Parameters are recruited at ~1 per
five nodes.** **Coupling arrives early** — separable → genuine product/quotient
between c≤5 and c≤10, logs from c≤8.

TM8 is the evidence for "idiosyncratic rather than convergent" because it runs
on the **same axis as TM6 and moves the opposite way**. TM6 (median R² on T0
validation) goes 0.47–0.87 at c≤5 → 0.96–0.998 by c≤20–30, then flat. Over
c = 20→40 accuracy is saturated and agreement is still falling. "Capacity buys
fit, not discovery" is those two tables side by side.

### 6.2 "Did we have a metric to see at what complexity the SR starts to fit to noise?"

**Yes — three. All three say the searches never reach that regime, and the
reason is structural: the target has essentially no noise to fit.** Two of the
three were computed for the first time on 2026-09-03; those numbers are new and
appear nowhere in the record.

**(a) The train/validation gap — pre-specified, stored per equation, never
reported.** `experiments/mse_one_stage_sr_plan.md:418` lists it as risk 2:
*"Larger trees overfit 4000 rows. Select on held-out T0 validation, **inspect
train/validation gaps**, use shuffled controls, and confirm only once on T2."*
Every `report.json` stores `mse_fit_eval` (4000 fit rows) and `mse_val` (1000
held-out) for every front member, so the curve has existed since the campaign
ran. **No table in the repo reports it.** Over all **3234 equations from the 165
MSE runs** on disk (11 latents × 5 seeds × 3 budgets), standardized units:

| c | n | med fit | med val | med val/fit | p90 | max |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 165 | 1.000 | 1.017 | 1.017 | 1.040 | 1.064 |
| 5 | 165 | 0.4476 | 0.4440 | 1.005 | 1.044 | 1.058 |
| 10 | 80 | 0.1435 | 0.1497 | 0.999 | 1.066 | 1.077 |
| 20 | 101 | 0.02137 | 0.02101 | 0.990 | 1.059 | 1.101 |
| 30 | 54 | 0.005943 | 0.006048 | 0.988 | 1.048 | 1.091 |
| 40 | 12 | 0.003067 | 0.003209 | 0.992 | 1.068 | 1.092 |

Flat from c=1 to c=40. **No knee, no upturn**; the median ratio never leaves
0.98–1.02 at any complexity, p90 ≤ 1.10, and the worst single equation over all
3234 is 1.13. With n_val = 1000 the validation MSE carries √(2/1000) ≈ 4.5%
relative standard error, so the p90 spread *is* the sampling noise: the
measurement bounds overfitting at ≲5% of fit error at **every** complexity, and
cannot resolve anything smaller.

**(b) Shuffled-target controls — memorisation capacity, measured directly.**
TM9, plus the same recomputation over the 221 control-front equations. On a
permuted target the best expression drives fit MSE from 1.000 only to **0.9955**
at c≈39: a size-40 tree absorbs **0.45%** of pure-noise variance on 4000 rows.
On T2 every control sits within |R²| ≤ 0.006 of zero against both targets, and
ms20 → ms40 buys a shuffled target nothing. Same picture in the MI objective:
shuffled-target MI at maxsize 20 with all six inputs is **0.004–0.060 nat**
against 3.83 nat real (EE z5,
`experiments/allparams_blind_sr_lcdm_tt_ee_lowl.md`).

So noise-fitting capacity at the largest budget used is ~0.5% of variance while
the signal being fitted is 96–99.8% — about 200:1. That is why no knee appears.

**(c) The structural reason — μ_k(θ) is deterministic, and this had never been
measured.** The shards are noiseless CLASS D_ℓ (no noise term anywhere in
`cmbvae`'s generation path), so θ → D_ℓ → encoder mean is a deterministic
composition. Two independent bounds:

* **6-input GBM floor** on the OLS residual: NMSE **4.1×10⁻⁶ – 9.3×10⁻⁴** across
  the 11 latents (table in §6.3 here). Reproduces the record's "97–99% of the
  OLS residual" to the digit: 97.1–99.1%.
* **Difference-based variance estimate.** Fit E[(μ_i−μ_j)²/2] = a + b·d² over
  the 50k nearest-neighbour pairs in standardized θ (NN distances: min 0.094,
  median 0.425, max 0.836). The zero-separation intercept a/Var(μ) is **≤
  4.3×10⁻⁴ or negative** for all eleven — a negative variance intercept is
  unphysical and just says the d² extrapolation slightly overshoots, i.e. the
  estimate is consistent with **zero** noise. The pure-d² model explains
  **97.1–99.8%** of the pair-gap profile, which is what a C¹ function gives: no
  white-noise pedestal, no fractal component. The one loose case is EE z4
  (intercept −4.1×10⁻³, d² fit R² 0.971) — the worst-fitting latent, as expected
  given its pole in τ.

**The consequence, and it is a paper-level point.** What TM8 measures is **not
overfitting**. It is non-identifiability *at constant generalisation gap*: those
idiosyncratic 20–30-node forms all generalise fine, they simply are not the same
expression. The standard defence in SR-for-science is "we validated on held-out
data" — this study passes that test at every complexity and it buys nothing,
because held-out MSE is **structurally blind** to the actual failure mode. The
instrument that sees it is cross-seed recurrence R_SR, which the frozen protocol
gated on before it knew it would need the defence. That is a concrete addition to
E6 and to §4 Q8's "paper about the method" column.

**Caveat.** This rules out variance overfitting *with respect to θ*. It says
nothing about overfitting to a single trained checkpoint — that is R_model /
Phase 9, and per §5.2 item C TT is not GPU-blocked.

### 6.3 "Further explain: μ_k(θ) is a smooth, essentially deterministic, genuinely nonlinear function that happens to be 99.8% captured by a plane"

Four claims. The first three are settled by §6.2 here and the table below; the
apparent contradiction is between the last two, and it dissolves once NMSE stops
being read as "how nonlinear".

| | OLS NMSE | GBM floor | ratio | nonlinear part<br>(rms, % of σ_μ) | floor<br>(rms, % of σ_μ) |
|---|---:|---:|---:|---:|---:|
| TT z0 | 1.81e-3 | 2.39e-5 | 75× | 4.25% | 0.49% |
| TT z1 | 1.37e-2 | 2.29e-4 | 60× | 11.7% | 1.51% |
| TT z2 | 4.52e-4 | 8.44e-6 | 54× | 2.13% | 0.29% |
| TT z3 | 2.16e-3 | 2.33e-5 | 93× | 4.65% | 0.48% |
| TT z4 | 3.87e-4 | 4.12e-6 | 94× | 1.97% | 0.20% |
| EE z0 | 4.02e-2 | 9.34e-4 | 43× | 20.0% | 3.06% |
| EE z1 | 9.07e-4 | 7.93e-6 | 114× | 3.01% | 0.28% |
| EE z2 | 1.69e-3 | 3.40e-5 | 50× | 4.12% | 0.58% |
| EE z3 | 3.11e-3 | 5.16e-5 | 60× | 5.57% | 0.72% |
| EE z4 | 4.27e-2 | 4.31e-4 | 99× | 20.7% | 2.07% |
| EE z5 | 4.51e-4 | 1.31e-5 | 34× | 2.12% | 0.36% |

*OLS in the sampled (logamp) basis, coefficients from T0-fit rows; GBM trained
on T1[5000:15000], scored on T1[15000:25000]. The frozen T0-val OLS numbers in
`results/*/coordinate_matched_ols_v1/logamp64/fit.json` agree: 3.85e-4 – 1.30e-2
for 9/11, 3.80e-2 / 3.94e-2 for EE z0 / EE z4, **median 1.71e-3 → R² = 0.9983**.
That median is where "99.8%" comes from.*

**The plane is 99.8% only in the variance metric, and only in this basis.** The
basis is the *sampled* one, which already contains ln10¹⁰A_s — which is why
`b_τ/b_lnAs` = −1.9785 (TT z2) and −1.9967 (TT+EE z5) fall out of a linear fit
at standardised condition number 1.021. The basis is doing real work.

**Read amplitudes and the picture inverts.** TT z0's nonlinear part is 4.25% of
a latent standard deviation: a systematic, reproducible, deterministic 4%
modulation of which a GBM recovers 98.7%. Two things hold at once — the
nonlinear part's **variance share** is tiny (0.2%), and its **signal-to-noise**
is enormous (75×, up to 114× at EE z1). NMSE conflates them; that is the trap.

**Geometrically**: over the prior box μ_k is a gently curved sheet. The box is
narrow — ω_b ∈ [0.020, 0.024] is ±9%, lnA_s spans 0.28 — so departure from the
tangent plane goes like (Δθ/θ)² ~ 10⁻², and its *variance* contribution squares
that again. Which is exactly why 21 exact quadratic coefficients close 33–94% of
the beyond-affine gap in 9/11 (§4 Q4 here): the curvature is ordinary
second-order Taylor response, arriving where §6.1 of the record predicts.

So the honest sentence is: **the function is nonlinear; the linear part
dominates the variance budget because the box is small.** Widen the box and the
plane degrades — which is why §7 item 7's parking of the wider-prior campaign is
correctly a decision about *scope*, not content.

**And the evidential punchline**, which is why the sentence is in §4 Q2 at all:
both OLS (10⁻³) and the ms40 winner sit ~2 orders of magnitude above the
achievable floor (10⁻⁵). Both are poor approximations by the standard the data
can support. "OLS beats symbolic 8/11" ranks two bad approximations against each
other and carries no information about whether the latent is linear. That is W1,
and the reason the protocol selected on a bijection-invariant criterion.

### 6.4 "Is the decoder-side gradient attribution still the open item?"

**It is encoder-side — and that is not a naming quibble. The decoder-side
instrument is the one that already ran and hit the wall.**

**Decoder side: done, and closed as a documented negative.**
`scripts/decoder_effect.py` computes d_k(ℓ) = ∂Decoder(z)_ℓ/∂z_k by JVP
(`torch.autograd.functional.jvp`, line 95), Phase 7b. It delivered real
attribution — template decomposition at R²_W 0.988–1.000, cos(a\*, g)
0.77–1.00, identifiable shape-sector coefficients and proj_brk. It failed only
on the amplitude split: **G4b FAIL on both models** by collinearity — the
(τ, lnA_s) templates are near-antiparallel (uncentered cos −0.9902 EE / −0.9996
TT; cond 14.2 / 70.2), so r_dec drifts along the degenerate ridge: −1.67 to
−2.32 across EE fit variants, +0.351 for TT. Recorded at
`docs/results_compendium.md:57,306`, `docs/method.md:191,218`, roadmap §7b.
**A settled result with a physical cause, not a to-do.**

**Encoder side: open, and never started** *(as of the exchange; run later the
same day — see the priority note at the end of this subsection)*. ∂z_k/∂C_ℓ had
**zero implementations** — no `.backward()`, `.grad`, `vjp`, `jacrev` or
`jacfwd` in any `scripts/*.py`; `scripts/encode_latents.py` is forward-only; the
string appeared only in §0.1 item 4 of the record and in this file. It is §5.1 item 9 here, and — as items 9
and 10 there record — none of the three proposals is in §7's open-items list.

Why it is the right instrument: one backward pass per latent, CPU, and it never
decomposes onto a parameter basis, so the collinearity that killed G4b cannot
arise. It answers "which multipoles does this latent listen to", not "how does it
split τ against lnA_s".

**The designed test is structural, and sharp.** Per
`cmbvae/configs/lcdm_tt_ee_lowl.yaml`, the TT encoder sees ℓ ∈ [30, 2500] and
the EE channel ℓ ∈ [2, 2500]. The low-ℓ EE reionization bump is therefore the
*only* place in either model where the amplitude degeneracy can break — and the
TT encoder structurally cannot see it. So if the E3 story is right, ∂z_k/∂C_ℓ
must show EE z4/z5 loading on ℓ ≲ 30 while the TT amplitude latent (TT z2)
cannot. Falsifiable, cheap, and independent of every instrument used so far.

**Caveat, so it is not oversold**: it does not rescue the −2. Projecting
∂z_k/∂C_ℓ back onto a τ-vs-lnA_s split re-enters the same degeneracy. What it
gives is ℓ-space support, not a coefficient. *(A second caveat surfaced only on
running it: the input is ~5000-dimensional and the data manifold is 6, and just
0.03–1.3% of |g_k|² lies in the span of the physical response templates. The raw
per-ℓ gradient is not a safe fine-grained attribution; the projected one is what
the band table uses.)*

**Priority**: item 9 of 10 in §5.1. **Run on 2026-09-03 — the prediction below
holds, and sharply**: on the on-manifold projection of the gradient, EE z4 puts
24.1% of its mass on the 28 EE bins with ℓ < 30 against 0.3–1.0% for every other
latent, and every TT latent is at exactly zero. See §5.1 item 9 and §6.8 of the
record. The refinement: it is z4 (τ) alone that reads the bump, not z4 and z5.

### 6.5 Replay recipe for §6.2–§6.3

All inputs are on disk; this is the whole computation, ~40 lines. Kept here
because the numbers above are otherwise prose-only — the failure mode §5.1
item 8 exists to fix.

```python
import json, glob, numpy as np, statistics as st
from collections import defaultdict
from sklearn.neighbors import NearestNeighbors
from sklearn.ensemble import HistGradientBoostingRegressor

# (a) train/validation gap over every stored MSE front member
by = defaultdict(list)
for p in glob.glob("results/*/mse_one_stage_ms*/z*_seed*/report.json"):
    for e in json.load(open(p))["all_equations"]:
        if min(e["finite_frac_fit"], e["finite_frac_val"]) >= 0.999 and e["mse_fit_eval"] > 0:
            by[e["complexity"]].append(e["mse_val"] / e["mse_fit_eval"])
for c in sorted(by):                       # swap the glob for */mse_one_stage_control_ms*/*/ for (b)
    print(c, len(by[c]), round(st.median(by[c]), 3))

# (c) determinism + the GBM floor, per latent
theta = np.load("data/theta.npy")[np.load("data/splits_v1.npz")["split_id"] == 2]
FIT, T1a, T1b = slice(0, 4000), slice(5000, 15000), slice(15000, 25000)
X = (theta - theta[FIT].mean(0)) / theta[FIT].std(0)
A = np.hstack([np.ones((len(X), 1)), X])
d, idx = NearestNeighbors(n_neighbors=2, n_jobs=1).fit(X).kneighbors(X)
d1, j1 = d[:, 1], idx[:, 1]
q = np.quantile(d1, np.linspace(0, 1, 21))
for run in ("lcdm_tt_beta3e-4", "lcdm_tt_ee_lowl"):
    mu = np.load(f"models/{run}/analysis/encoder_means_test.npy").astype(np.float64)
    for k in range(mu.shape[1]):
        y = mu[:, k]
        w, *_ = np.linalg.lstsq(A[FIT], y[FIT], rcond=None)
        r, v = y - A @ w, y[T1b].var()
        g = HistGradientBoostingRegressor(max_iter=400, random_state=0).fit(X[T1a], r[T1a])
        n_ols = (r[T1b] ** 2).mean() / v
        n_gbm = ((r[T1b] - g.predict(X[T1b])) ** 2).mean() / v
        # difference-based variance: E[(mu_i-mu_j)^2/2] = a + b d^2, intercept a/Var(mu)
        gap = (y - y[j1]) ** 2 / 2.0 / y.var()
        m = [(d1 >= a_) & (d1 < b_) for a_, b_ in zip(q[:-1], q[1:])]
        xs = np.array([(d1[s] ** 2).mean() for s in m]); ys = np.array([gap[s].mean() for s in m])
        (a0, _), *_ = np.linalg.lstsq(np.vstack([np.ones_like(xs), xs]).T, ys, rcond=None)
        print(run, k, f"{n_ols:.3e} {n_gbm:.3e} {n_ols/n_gbm:.0f}x  intercept {a0:+.2e}")
```

Run single-threaded (`OMP_NUM_THREADS=1`) on a login node — per the standing
note, sustained multi-core work there gets SIGKILLed. Wall time ≈ 2 min.
