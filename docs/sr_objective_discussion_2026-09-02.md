# Discussion record — what SR was for, and the verified state of the record

*Saved 2026-09-03 from the 2026-09-02 session; both sides of the conversation.
Companion to `docs/ols_mi_sr_mse_sr_t2_comparison_claude_output.md`, which is
the **record**. This file is the **discussion** — kept separate so the record
stays a record. Questions are quoted verbatim; answers are the worked replies.
Where an answer is reasoning rather than a repo artifact, it says so.*

**To resume:** §4 is the live thread — which paper this is. §5 lists everything
still open, including the one item with a deadline (§1.1).

---

## 1. Verified state of the record (checked 2026-09-02)

A nine-agent pass checked §7's open items of the record against the repo itself.
Six completed. **Items 1 (ladder promotion), 3 (level-set audit of the OLS
index), 7 (beyond-box tests) and a whole-doc sweep for open items stated outside
§7 all failed** (three on structured-output retry caps, the sweep on a usage
limit) **and were never re-run** — they remain unverified.

### 1.1 The one item with a deadline

The **330 raw searches of the precision/preprocessing campaign exist nowhere but
the Lightning studio.** `find results -path '*precision_preprocess*'` returns
zero on CSD3. The campaign survives here only as the rendered comparison plus
six sha256 digests; `experiments/precision_preprocess_v1_comparison.json`'s
`source_files` are six absolute `/teamspace/studios/this_studio/...` paths.

`.gitignore:10` is `results/*`, so **the 2026-09-02 commits did not and cannot
back these up.** If the studio and the Mac ledger are lost, the campaign is
unauditable per-run and re-running it (≈10² core-h) is the only recovery. Every
other campaign's raw outputs were pulled back; only this one was not.

### 1.2 Phase 9 is not GPU-blocked for TT

The roadmap closed without Phase 9 because "R_model needs retrained VAE seeds
from the parent `cmbvae` repo (GPU, outside this repo's CPU budget)". **Those
seeds already exist**, and predate the closure by two months:
`cmbvae/results/lcdm_tt_beta3e-4_seed{7,123,2024}`, complete checkpoints from
2026-06-08, 429/394/460 epochs. A config diff of seed7 against the canonical run
gives **3 differences out of 29 keys** — `seed: 42→7` and two `out_dir` strings.
That is exactly roadmap step 1's spec. β=3e-4, latent_dim=5, unchanged.

So for TT, Phase 9 is CPU/consolidation work: encoder pass, write
`scripts/align_latents.py` (absent), ≈90 finalist reruns ≈135 core-h. EE
genuinely still needs GPU — no EE seed variants exist. The roadmap's own clause,
"If retrained seeds appear later, Phase 9 slots in exactly as specified", is
triggered and unnoticed; no file in this repo mentions those seeds.

### 1.3 `TemplateExpressionSpec` is already in the pinned PySR

Verified at `.venv/lib/python3.12/site-packages/pysr/expression_specs.py:128`,
exported in `pysr/__init__.py`, with a `parameters: dict[str, int]` field
documented as "will be optimized during the search". So the §6.3 hybrid — fitted
affine scaffold plus a free searched part, as one search object — is expressible
**today on `pysr==1.5.10`**, no v2, no Julia port, no parallel env:

```python
TemplateExpressionSpec(
    expressions=["g"], variable_names=[...six params...], parameters={"w": 7},
    combine="w[1] + w[2]*tau + ... + w[7]*n_s + g(...)")
```

The same applies to the constants-only half of §7 item 4. **Only population
seeding genuinely needs v2's `guesses`** (zero grep hits for "guess" across
pysr 1.5.10 and SymbolicRegression.jl 1.11.3). Nothing in the repo uses
`expression_spec` at all, and `run_blind_sr.py:331-338` rejects `--pysr-extra`
keys colliding with managed kwargs, so a plumbing flag is needed either way.

### 1.4 Three smaller verified facts

* **The pin leaks.** `pyproject.toml:22` is `"pysr>=1.5"` — a fresh
  `pip install -e .` pulls PySR 2.x today. Only `requirements.txt:11` and the
  Lightning requirements hard-pin `==1.5.10`, and nothing asserts the version at
  runtime; scripts only *record* `pysr_version`.
* **Never upgrade in place.** `.venv` is a symlink to `../cmbvae/.venv`, shared
  with the training project, and PySR's Julia project defaults to
  `<venv>/julia_env`. `hpc/lightning/env.sh:16-24` is a ready-made parallel-env
  pattern.
* **A concrete v2 breakage.** `eval_loss` is 3-arg; SR.jl's `Options.jl`
  docstring says under `batching=true` the loss receives a 4th `idx` argument —
  and v2 makes auto-minibatching default above 1000 rows while the protocol uses
  5000 samples. No validation apparatus exists to catch it:
  `tests/test_sr_inputs.py:85-91` only string-matches, and no test ever executes
  the Julia block.

### 1.5 The §2.5 injection result is prose-only

43/55 retained, 39/55 wins selection, 38/55 fit-side, the 1.445 median ratio —
**no script, no artifact, zero grep hits for "inject"**, no commit. The half of
item 4 marked "done" cannot be cited or re-derived. Every input is on disk (55
`report.json` with `ols_baseline` + `all_equations`), so it is a ~100-line
replay, not a campaign.

### 1.6 Write-up status, with one staleness

`results_compendium.md:425` **already** carries "Plain six-input OLS beats the
maxsize-40 symbolic winner in 8/11 latents" (commit `982a229`), so §1 row 11 of
the record overstates the gap. `report.md`, `paper/main.tex` and
`report_content.md` have zero word-boundary "OLS" outside the unrelated decoder
fit-variant label. Revision surface mapped: `report.md` §4 L134 and
`paper/main.tex` L380 are the verbatim W3 retractions; §5/L391 is W2; §6/§7 are
W4/W5. Four figures need new captions, four don't exist yet.

### 1.7 η̂_post has a trap

The audit's `ols_mi` is MI(μ_k; w·θ) — the encoder **mean**, not a posterior
draw — so it **cannot** be reused as the η̂_post column. Normalising it by
MI(Z;μ) gives ratios up to 2.55, i.e. trivially DPI-violating. The denominators
(`ceiling.I`, `mi_mu_ref`) and the f₁+f₂ comparison column
(`hierarchy.eta_post_hat_comb`) are already stored for all 11 latents, so the
item really is one new column.

---

## 2. The injection / PySR v2 exchange

**You:**

> thinking about it makes me feel like using the guess OLS form to inject the
> expression, then this is verified to score best on the metrics then it will
> definitely be kept, so whats the point of doing this?

**The answer: you were right, and it reorders the plan.**

*The naive version is close to informationally empty.* §2.5 already ran the
injection at selection level. "Will it be kept?" is answered. Re-running it as a
live `guesses` arm and confirming that a fit-superior expression stays on a
Pareto front *defined* as best-per-complexity is not a test with an uncertain
outcome.

*The one surviving distinction is weaker than it looks.* §2.5 injected at
selection time into the final candidate set; a seeded run asks whether the
expression survives 200 iterations of live population dynamics. Formally
different — but PySR keeps the hall of fame separately from the evolving
populations, so a complexity-25 entry dominating its slot stays regardless.
Eviction is unlikely enough not to fund a campaign.

*The constant-fitting leg is nearly dead on argument alone.* The affine tree is
**linear in its constants**, so optimising them under MSE is a convex quadratic
with a closed-form minimum — and so is every additive prefix of it. The only
crack is conditioning (raw64 spans A_s ~ 10⁻⁹ to H₀ ~ 67, and PySR's bounded
BFGS fires probabilistically). **That crack was already probed**:
`physical_o1_64` is exactly the intervention that fixes conditioning without
touching the hypothesis class, and it moved direct winners 9·2 → 6·5 and no
further. Real, secondary, doesn't explain the loss.

*What is actually unknown* is not retention but **assembly** — where does the
lineage stall on the way to a 6-term sum? The likely mechanism is neither of
§7 item 4's two candidates: it is **parsimony pressure against incremental
additive construction**, where each extra term buys a small MSE gain at a large
complexity cost and the intermediates are culled before they pay off.

**The redesign that follows:** a **truncated-seed ladder**, not a finished-seed
run. Seed the 2-, 3-, and 4-term affine prefixes (with and without optimised
constants) and measure whether evolution *extends* them. If a 4-term seed never
reaches 6, that localises the failure precisely. The second live readout is
*"does evolution build on top of the seed"* — a discovery question, which would
produce hybrid `affine + correction` candidates for all 11 latents in-search,
where Step 2 got there for only EE z0 and EE z4 via a separate residual cache.

**Consequence:** the template-hybrid arm moves ahead of the guesses arm — and
per §1.3 it needs no upgrade at all. `guesses` drops to a cheap ablation ladder
and a positive control.

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

## 5. Open threads, in priority order

1. **Rsync the 330 raw campaign artifacts off Lightning** (§1.1). The only item
   with a deadline; commits do not cover it.
2. **Decide the paper's shape** (§4 Q8). Everything downstream — which figures,
   which claims, how much of §5's W1–W6 goes in the abstract — waits on this.
3. **Re-run the four failed verifiers**: §7 items 1, 3, 7 and the whole-doc
   sweep for open items outside §7. Cheap; resumable from cache.
4. **Write the §2.5 injection replay script** (§1.5) — ~100 lines, all inputs on
   disk, makes a cited result reproducible.
5. **η̂_post for the OLS index** (§1.7) — one new column, minutes of CPU, and it
   hardens W2/W4 from prose into table rows.
6. **The template-hybrid arm on the current pin** (§1.3) — no upgrade needed.
   The truncated-seed ladder (§2) is the follow-on that actually diagnoses the
   generative failure.
7. **Phase 9 for TT** (§1.2) — no GPU needed; encoder pass +
   `scripts/align_latents.py` + ≈135 core-h.
8. **Fix the §6.1 soft spot**: it cites "e^{−2τ} 99.9%-linear even over the 13×
   τ range" as evidence linearity is not a narrow-box artifact. That argument
   fails — 13× is a *ratio*, while Taylor accuracy depends on the absolute
   exponent span 2Δτ = 0.24. §0.1 states the correct version (exact linearity in
   the sampled basis, range-independent); §6.1 itself is unedited.
9. **The three LLM-interp proposals** (§0.1 item 4) are not in §7's open-items
   list. Gradient attribution ∂z_k/∂C_ℓ is the cheap one and the only instrument
   that sidesteps the collinearity that killed G4b.
10. **Test hygiene**: `test_precision_preprocess_lightning_wrappers.py::
    test_consolidation_cell_matrix_is_complete` fails on CSD3 (needs
    `.venv-lightning`); a skip guard would make the suite green on both
    machines. Also consider dropping `TODO.md` (stale) and
    `docs/zx332.code-workspace` (editor config) from the tree.
