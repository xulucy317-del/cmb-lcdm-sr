# Discovery-study roadmap — from Pareto fronts to validated latent cards

*Drafted 2026-08-03. Builds on the status in [`README.md`](../README.md)
("Where the project stands", 2026-08-01) and the methodological programme in
[`docs/next_step.md`](next_step.md). This file is the executable version of
that programme: a phased series of plans and experiments, each with concrete
machinery, budgets, deliverables, and pass/fail gates, that takes the project
from "consolidated Pareto fronts + amplitude-sector diagnostics" to a complete
representation-discovery claim for **all 11 latents** of the two stored
models.*

---

## 0. Goal, definitions, and pre-registered decision rules

### 0.1 The end state

One **latent card** per latent (5 for `lcdm_tt_beta3e-4`, 6 for
`lcdm_tt_ee_lowl`), each carrying:

```
{ canonical formula cluster f*,  support S*,  complexity c,
  sufficiency η_S / η_plat / η_post,  knee c*,
  recurrence R_SR (and R_model where available),
  sensitivity signature g_j + constant-ratio pairs,
  residual audit (R²_res, per-param residual MI vs null),
  level-set invariance E_inv,  decoder-effect decomposition a*,
  status ∈ {interpreted, primarily interpreted, subspace/mixed, unresolved} }
```

plus an updated `docs/method.md` and a controls appendix. Every phase below
ends in a consolidated `experiments/<name>_<run>.{md,json}` pair, following
the existing convention.

### 0.2 Notation

| Symbol | Meaning |
|---|---|
| θ ∈ R⁶ | raw ΛCDM parameters, sampled coordinates `(omega_b, omega_cdm, H0, tau, ln10^{10}A_s, n_s)` (`data/meta.json`) |
| u ∈ R⁶ | θ standardised to the prior box: u_j = (θ_j − mid_j)/halfwidth_j, **in the sampled basis** (i.e. the A_s axis is ln10^{10}A_s) |
| μ_k(θ), σ_k²(θ) | encoder posterior mean / variance of latent k (`analysis/encoder_means_test.npy`, `encoder_logvars_test.npy`) |
| Z_k | the stochastic latent, Z_k \| θ ~ N(μ_k(θ), σ_k²(θ)) |
| f_S | a symbolic coordinate with variable support S ⊆ {1..6}; C(f) = PySR complexity |
| Î(f) | held-out GMM-MI between f(θ) and μ_k (val split, `src/cmb_lcdm_sr/mi.py`) |
| Î_plat(k) | empirical plateau: cross-seed mean top MI of the highest-capacity front (ms30 where available, else ms20) |
| Î_S(k) | subset ceiling: cross-seed mean top MI of runs restricted to inputs S |
| M_{k,s}(c) | cumulative Pareto envelope: max Î over front equations of seed s with complexity ≤ c |

Two sufficiency ratios (this sharpens `next_step.md` §2.1, and is what makes
the amplitude latent's numbers non-paradoxical):

* **η_plat(f) = Î(f)/Î_plat(k)** — *global* sufficiency: fraction of
  everything SR can extract from the deterministic mean map.
* **η_S(f) = Î(f)/Î_S(k)** for supp(f) ⊆ S — *support-restricted*
  sufficiency: does f capture all information available from its own
  variables? (For the amplitude latents the pre-Phase-4 proxy for Î_{A_s,τ}
  is the reference ceiling 0.822 / 1.196 nat.)

A latent like TT-z2 is *expected* to score η_S ≈ 1 on `A_s·(τ−c)` while
η_plat ≈ 0.2 (0.822/4.05): the leading-order coordinate saturates its support
but the deterministic mean also carries shape-sector modulation. The statuses
below encode exactly this distinction.

* **η_post(f) = Î(Z_k; f(θ)) / Î(Z_k; θ)** — the *intrinsic* sufficiency
  against the finite information stored in the stochastic latent (Phase 5).
  This becomes the principled headline once available.

### 0.3 Pre-registered thresholds (freeze before any shape-latent unblinding)

The interpretation layer so far was answer-aware (README gap 4). To make it
answer-agnostic these rules are fixed **now**, validated only on the
amplitude sector (whose ground truth is known), and then applied to the shape
latents without further tuning. Any later change is a reported deviation on
the affected cards.

| Rule | Value |
|---|---|
| Sufficiency levels reported | simplest forms at η ≥ 0.90 / 0.95 / 0.99; default "sufficient" = **η ≥ 0.95** |
| Knee | c\*_k = min{c : M_k(c) ≥ Î_plat − SE(Î_plat)}, SE = cross-seed std/√n (one-SE rule); MI@c≤10 kept as the budget-matched legacy readout |
| Cluster equivalence (any one ⇒ same cluster) | (i) identical canonical sympy form; (ii) \|Spearman ρ\| ≥ 0.98 on the anchor set; (iii) gradient distance d_∇ ≤ 0.05 |
| Recurrence R_SR | fraction of seeds whose front contains a cluster member reaching knee-level MI (≥ M_k(c\*) − SE) at complexity ≤ c\*; "stable" = R_SR ≥ 0.8, "primary" = R_SR ≥ 0.6 |
| Subset minimality | S\* = smallest \|S\| (ties → smaller C) with η_S within **1 SE** of the best over all supersets, recurrent across screen seeds |
| Residual pass | cross-fitted R²(e_k ← θ) ≤ 0.05 **and** max_j Î(e_k; θ_j) ≤ 97.5th percentile of permutation null |
| Level-set pass | E_inv(f) ≤ 0.05 (normalised so random pairs = 1) and the matched-nuisance response μ_k vs f is 1-D with spline R² ≥ 0.9 |
| Statuses | **interpreted**: minimal-stable S\*, R_SR ≥ 0.8, η_S ≥ 0.95, residual pass (⇒ η_plat ≈ 1), η_post ≥ 0.95, level-set pass. **primarily interpreted**: η_S ≥ 0.95, R_SR ≥ 0.6, level-set pass, residual **fails** (structured residual; f₂ documented if found). **subspace/mixed**: no 1-D f reaches η_S ≥ 0.9 for any stable S, but Phase 8 finds a ≤3-latent subspace or shared-coordinate account. **unresolved**: anything else. |

### 0.4 Evaluation tiers (data hygiene, new)

The 50k-row test split leaves room to stop reusing the SR rows for
validation-grade claims:

| Tier | Test-split rows | Used for |
|---|---|---|
| **T0** | [0 : 5000) | SR fit + val exactly as today (4000/1000) — untouched, keeps all existing results comparable |
| **T1** | [5000 : 25000) | calibration h (cross-fitted), residual audits, semantic anchors (= T1[:2048]), level-set pairs |
| **T2** | [25000 : 50000) | confirmatory card numbers: final η, η_post, E_inv recomputed once on untouched rows |

Fixed as constants in one place (`src/cmb_lcdm_sr/tiers.py`).

### 0.5 Validation-first principle

Every new instrument (knee, clustering, signatures, residual audit, subset
selection, level sets, decoder decomposition) is first run on the two
**amplitude latents**, where the answer — support {A_s, τ}, the
`ln(A_s·e^{−2τ})` direction, r = −2 — is known. Only after gate **G1** passes
do the shape latents get analysed, with thresholds frozen. The amplitude
sector is the positive control of the methodology, the shuffled-target runs
remain the negative control, and permutation nulls inside each new script
give metric-level nulls.

---

## 1. Phase map

| Phase | Question answered | Closes | New SR runs | Runs where | Est. cost | Deliverable (`experiments/`) |
|---|---|---|---|---|---|---|
| 0 | Is everything in place to analyse without new searches? | — | no | local + one rsync | dev only | gate G0 checklist |
| 1 (+1b) | Where does each front saturate; what is the simplest sufficient form? | README gap 1; NS §2.1 | 1b only: 33 | 1b on CSD3 | ~65 core-h | `knee_readout_<run>` |
| 2 | Which *semantic* coordinate recurs across seeds? | README gap 2; NS §2.2 | no | local | — | `semantic_recurrence_<run>` |
| 3 | What does each form depend on; is it sufficient after calibration? | README gap 4; NS §2.3+§3 | no | local | — | `sufficiency_audit_<run>` + gate G1 |
| 4 | Which variable subset is minimally sufficient — blindly? | README gap 3; NS §4 | ~1400 screen + ≤275 finals | CSD3 | ~1000 + ≤405 core-h | `subset_selection_<run>` + gate G2 |
| 5 | What fraction of the latent's *intrinsic* information is captured? | NS §5 | no | local | — | `posterior_ceiling_<run>` + gate G3 |
| 6 | What secondary coordinate explains structured residuals? | NS §3 (hierarchical) | ~30 | CSD3 | ~45 core-h | `residual_sr_<run>` |
| 7 | Does the coordinate survive interventions; what does the latent *do* to C_ℓ? | NS §6+§7 | no (opt. sims) | local + 1 shard pass | ~5 core-h | `levelset_audit_<run>`, `decoder_effect_<run>` + gate G4 |
| 8 | Are the non-1-D latents subspace-encoded or entangled? | NS §8 | no | local | — | `subspace_probe_<run>` |
| 9 | Is the representation stable across VAE training seeds? | NS §9 | ~90 + 6 encoder passes | parent repo (GPU) + CSD3 | ~140 core-h + training | `vae_stability_<regime>` |
| 10 | Final synthesis | all | no | local | — | `latent_cards_<run>`, docs update |

(NS = `next_step.md`. Phases 1–3 are pure consolidation and can start today;
4 is the one large compute campaign; 5–8 are cheap; 9 is the only stage
needing the parent `cmbvae` training pipeline.)

Dependency shape: 0 → 1 → 2 → 3 →(G1)→ 4 →(G2)→ {5, 6, 7} → 8 → 10, with 9
runnable any time after 4 and folded into 10. Phases 5–7 are mutually
independent.

---

## Phase 0 — sync, caches, shared infrastructure

**Aim.** All no-new-SR phases (1–3, 5, 7a, 8) need only small artifacts:
`report.json` trees, the means/logvars caches (≈1 MB each), `theta.npy` +
splits (already local). Bring those local so the consolidation layer can be
developed and run off-cluster; land the two small interface extensions every
later phase relies on.

**Steps.**

1. Sync results + caches from CSD3 (`PROJ=/rds/user/zx332/hpc-work/cmb-lcdm-sr`;
   the local SSH alias for the icelake login node is `lucyx`, and CSD3 auth is
   keyboard-interactive — run these in a terminal, or add ControlMaster to
   `~/.ssh/config` so one login covers all three):

   ```bash
   rsync -avz --prune-empty-dirs \
     --include='*/' --include='report.json' --include='pooled*' \
     --include='manifest.json' --include='tasks.tsv' --exclude='*' \
     lucyx:/rds/user/zx332/hpc-work/cmb-lcdm-sr/results/  results/
   rsync -avz lucyx:/rds/user/zx332/hpc-work/cmb-lcdm-sr/models/lcdm_tt_beta3e-4/analysis/ models/lcdm_tt_beta3e-4/analysis/
   rsync -avz lucyx:/rds/user/zx332/hpc-work/cmb-lcdm-sr/models/lcdm_tt_ee_lowl/analysis/  models/lcdm_tt_ee_lowl/analysis/
   ```

   (`pysr_state/` stays on CSD3.) Then gate G0 is checked by
   `python scripts/verify_phase0.py` (exit 0 = pass).

2. **Verify the logvar caches.** `encode_latents.py` always writes
   `encoder_logvars_test.npy` next to the means — confirm both files exist
   per model with shape (50000, L). If a cache predates this repo's encoder
   script, rerun `hpc/slurm_allparams_encode.sh` once per model (needs
   shards; CSD3 paths in `config_used.json` are valid as-is). Phase 5 is
   blocked without them.

3. **Infra M1** — `run_blind_sr.py --target-npy PATH [--target-label NAME]`:
   regress an arbitrary 50k-row column instead of a latent column (mutually
   exclusive with `--latent-index`). Needed by Phase 6 (residual targets);
   ~20 lines + a test.

4. **Infra M2** — subset mode for the sweep planner: `mode: "subsets"` in a
   sweep spec expands one config per non-empty subset of a declared input
   pool, writing per-config `inputs` into `tasks.tsv` (the column and the
   SLURM wrapper already exist; only `expand_configs`/`write_tsv` change).
   Config ids like `c17_S-As-tau` from abbreviations
   `{ob, oc, H0, tau, As, ns}`. ~40 lines + tests in `tests/test_hpsweep.py`.

5. **Infra M3–M5** (pure-Python modules, test-covered):
   * `src/cmb_lcdm_sr/tiers.py` — the T0/T1/T2 slices (§0.4).
   * `src/cmb_lcdm_sr/semantics.py` — sympy→callable lambdification with
     non-finite masking, gradients in u-coordinates, anchor-set evaluation,
     the three equivalence tests, union-find clustering, Sobol indices
     (hand-rolled Jansen estimator on the prior box, QMC, no new deps).
   * `src/cmb_lcdm_sr/calibrate.py` — K-fold cross-fitted 1-D calibration h
     (monotone PCHIP on quantile bins by default; general smoothing spline
     fallback, flagged), residual diagnostics (gradient-boosted R²_res,
     per-parameter GMM-MI reusing `mi.mutual_information_gmm`, permutation
     nulls).

6. Pin `pysr==1.5.10` (and the Julia version note) in `requirements.txt` so
   later-phase searches stay protocol-identical to the stored fronts.

**Gate G0.** `pytest -q` green including new tests; both caches verified;
one existing report re-parsed end-to-end by the new modules (lambdify → MI
on T1 reproduces the stored `mi_val` within estimator noise).

---

## Phase 1 — knee & plateau readout for all 11 latents *(no new search)*

**Aim.** Replace argmax-MI with a saturation readout (README gap 1,
`next_step.md` §2.1): per latent, the cumulative envelope M_{k,s}(c), the
plateau Î_plat ± SE, the one-SE knee c\*, and the simplest forms at
η ≥ 0.90/0.95/0.99 — everything already sits in the stored `report.json`
fronts.

**Method.** For each latent and seed build M_{k,s}(c) from `all_equations`
(val MI vs complexity); pool as mean ± SE across seeds. Î_plat from the
highest-capacity family available: `hpsweep_hp_v1/c07_ms30` (3 seeds) for
the amplitude latents, `allparams` ms20 (5 seeds) for shape latents until 1b
lands. Report per latent: Î_plat ± SE, c\*, M_k(c\*), MI@c≤10 (continuity
with the sweep tables), and the η-level forms with their supports. Classify
the envelope shape: single dominant knee / knee + slow climb / no knee
(diffuse).

**Phase 1b (recommended, small).** The ms30 ceiling currently exists only
for z2/z5. Firm the shape-latent plateaus with a maxsize-30 batch, 3 seeds,
reusing the existing wrapper (writes to `results/<run>/allparams_ms30/`):

```bash
sbatch --array=0-4 hpc/slurm_allparams_sr.sh models/lcdm_tt_beta3e-4 "0 1 2" 30
sbatch --array=0-5 hpc/slurm_allparams_sr.sh models/lcdm_tt_ee_lowl  "0 1 2" 30
```

33 runs × ~440 s at 16 threads ≈ **65 core-h**. Re-run the readout after.

**Implementation.** `scripts/knee_readout.py` (M5-style consolidator):

```bash
python scripts/knee_readout.py --run lcdm_tt_beta3e-4 \
    --subdirs allparams allparams_ms10 allparams_ms30 hpsweep_hp_v1 \
    --out experiments/knee_readout_lcdm_tt_beta3e-4
```

**Deliverable.** `experiments/knee_readout_<run>.{md,json}`: one envelope
plot + one table row per latent; the JSON feeds Phases 2–4.

**Definition of done.** All 11 latents have Î_plat ± SE, c\*, and η-level
forms; amplitude rows reproduce the known picture (TT: MI@c≤10 ≈ 1.89 of
plateau ≈ 4.05, knee form in the `A_s·(τ−c)`-times-shape-factor family).

---

## Phase 2 — semantic clustering & seed recurrence *(no new search)*

**Aim.** Selection by *recurrence of meaning*, not string identity (README
gap 2, `next_step.md` §2.2). `pool_sr_runs.py` pools exact canonical sympy
strings; Taylor forms, exponential forms, and monotone wrappers of one
direction must pool together.

**Method.** For each latent, collect every front equation with η_plat above
a floor (0.25) from all seeds/subdirs. Cluster with the three frozen
equivalence tests (§0.3): algebraic identity; \|Spearman ρ\| ≥ 0.98 on the
2048-θ anchor set (a continuous bijection on an interval is monotone, so
rank agreement is exactly MI-equivalence on the observed domain);
gradient-cosine distance d_∇ ≤ 0.05 in u-coordinates (catches direction
agreement between forms whose outputs disagree through wrappers with
plateaus). Union-find over pairwise edges; anchors where any member is
non-finite are dropped pairwise and the finite fraction recorded.

Per cluster: simplest representative, complexity range, support, per-seed
best MI, and **R_SR** (§0.3). The latent's **canonical coordinate** = the
simplest representative of the most recurrent cluster that reaches
knee-level MI.

**Implementation.** `scripts/semantic_recurrence.py` on top of
`semantics.py`; consumes `knee_readout_<run>.json`.

**Deliverable.** `experiments/semantic_recurrence_<run>.{md,json}` — per
latent: cluster table (representative, C, support, R_SR, MI stats), the
canonical coordinate, and a comparison column against `pool_sr_runs`' exact
pooling (to document how much semantic pooling changed the picture).

**Definition of done.** Amplitude latents: the `A_s·(τ−c)` /
`A_s·e^{−2τ}` / `2τ−ln A_s` family lands in **one** cluster with R_SR ≥ 0.8
(TT expects 5/5 at c≤10 from the reference study). Shape latents: clusters
with R_SR reported — whatever they are.

---

## Phase 3 — sensitivity signatures + calibrated sufficiency audit *(no new search)*

**Aim.** The answer-agnostic replacement for the r-ratio and textbook regex
(README gap 4, `next_step.md` §2.3 + §3): what does each canonical
coordinate depend on, and — after an arbitrary 1-D recalibration — is it
*sufficient* for the latent?

**Method.**

1. **Sensitivity signature.** For each candidate f: normalised mean
   absolute gradients g_j(f) = E\|∂f/∂u_j\| / Σ_i E\|∂f/∂u_i\| over T1
   anchors, plus first- and total-order Sobol indices on the prior box.
2. **Constant-ratio pairs** (answer-agnostic −2 detector). For every
   variable pair (i, j) in the support, the ratio field
   ρ_ij(θ) = (∂f/∂u_i)/(∂f/∂u_j). If its coefficient of variation over
   anchors is < 5%, f depends on (i, j) only through a fixed linear
   combination — report the implied direction (unstandardised back to raw
   coordinates). The textbook −2 must *emerge* here for the amplitude
   latents — a constant (τ, lnA_s) ratio with
   r = (∂f/∂τ)/(∂f/∂ ln A_s) ≈ −2 — rather than being asked for. The
   legacy `amp_ratio` readout in
   `consolidate_allparams.py` is kept as a cross-check column.
3. **Calibrated sufficiency.** Fit h by 5-fold cross-fitting on T1
   (monotone PCHIP default), residual e_k = μ_k − h(f(θ)); diagnostics
   R²_res(e_k ← θ) (gradient boosting) and Î(e_k; θ_j) per parameter with
   permutation nulls (§0.3). Compute e_k over all 50k rows and cache
   `models/<run>/analysis/residual_z<k>_v1.npy` for Phase 6.
4. Run the *same* audit on the best shuffled-control expressions —
   metric-level negative control.

**Implementation.** `scripts/sufficiency_audit.py` (uses `semantics.py` +
`calibrate.py`); draft latent cards v0 assembled here.

**Deliverable.** `experiments/sufficiency_audit_<run>.{md,json}` — per
latent: signature bars g_j, Sobol table, constant-ratio pairs, residual
verdicts, draft status.

**Gate G1 (must pass before any Phase-4+ shape-latent claims).** On both
amplitude latents, blind machinery recovers the known answer:
* canonical cluster support = {A_s, τ} (at the knee slice), R_SR ≥ 0.8;
* constant-ratio pair (τ, lnA_s) detected with implied r = −2.0 ± 0.05
  (matching the stored −1.974 ± 0.018 / −1.993 ± 0.008);
* η_S ≥ 0.95 against the 2-input reference ceiling;
* residual audit *fails* in the expected direction (structured shape-sector
  residual — R²_res well above null with ω_b/ω_cdm/H0/n_s loadings), i.e.
  the machinery correctly reports "primary coordinate + structured
  residual" rather than fabricating full sufficiency.

If G1 fails: fix estimators/clustering; do **not** touch thresholds after
looking at shape-latent outputs.

---

## Phase 4 — blind variable-subset selection *(the compute campaign)*

**Aim.** Close the last human choice (README gap 3, `next_step.md` §4):
instead of hand-picking `(A_s, τ)` or exposing all 6, search all 2⁶−1 = 63
supports and let a three-objective Pareto rule pick the minimal sufficient
subset — restoring interpretable marginalisation ceilings Î_S per support.

**Design.**

* **4a — screen.** All 63 subsets × 2 seeds × all latents, reduced budget
  (niterations 100 — the sweep showed ni100 ≈ baseline on the c≤10 readout,
  −0.041 nat), full maxsize 20 (the sweep's "search big, then slice"
  lesson: never screen at ms10). Spec via M2, e.g.
  `hpc/sweeps/subsets_v1_tt.json`:

  ```json
  { "name": "subsets_v1", "run_dir": "models/lcdm_tt_beta3e-4",
    "latents": [0, 1, 2, 3, 4], "seeds": [0, 1], "n_samples": 5000,
    "mode": "subsets",
    "baseline": {"niterations": 100, "populations": 15, "maxsize": 20, "extra": {}},
    "subsets": {"pool": ["omega_b", "omega_cdm", "H0", "tau", "A_s", "n_s"], "min_size": 1} }
  ```

  ```bash
  python scripts/sweep_blind_sr.py plan --spec hpc/sweeps/subsets_v1_tt.json
  sbatch --array=0-629%16 hpc/slurm_hpsweep_sr.sh results/lcdm_tt_beta3e-4/hpsweep_subsets_v1
  # EE spec analogous: latents [0..5], 63×2×6 = 756 tasks
  ```

  Within-screen sufficiency η̃_S = Î_S^screen / Î_full^screen (both at the
  ni100 budget — never mix budgets in a ratio; the S = all-6 configs are the
  in-screen reference). Keep the Pareto frontier of (\|S\|, C, −η̃_S) plus
  any subset within 1 SE of it.

* **4b — finalists.** Frontier subsets (expect ≤5 per latent) rerun at the
  full protocol (ni200, 5 seeds); the S = all-6 full-protocol reference
  already exists (`results/<run>/allparams`, 5 seeds). Final rule (§0.3): S\* =
  smallest stable subset whose η_S is within 1 SE of every superset.
  Per-latent staircase figure \|S\| vs best η — the "information budget by
  support".

* **4c — optional controls extension.** Shuffled-target controls per shape
  latent at the all-6 config (3 shuffle seeds × 11 latents ≈ 33 runs,
  ~48 core-h) — exact per-latent MI nulls for η; batchable with 4b.
  (Amplitude nulls exist: ≤ 0.06 nat.)

**Budget** (calibrated on `sweep_blind_sr.rough_seconds`; baseline run
330 s at 16 threads):

| Piece | Runs | Core-h |
|---|---:|---:|
| 4a screen, TT (5 latents) | 630 | ~460 |
| 4a screen, EE (6 latents) | 756 | ~555 |
| 4b finalists (≤5 subsets × 5 seeds × 11 latents) | ≤ 275 | ≤ 405 |
| 4c per-latent controls (optional) | 33 | ~48 |

Wall-clock at the `%16` throttle: the whole screen is ~4 h. If allocation
is tight, the pre-registered fallback is to screen only subsets of each
latent's top-4 Sobol variables (Phase 3) plus all \|S\| ≤ 2 (~30
subsets/latent, ≈ half cost) — record the truncation on the cards.

**Deliverable.** `scripts/consolidate_subsets.py` →
`experiments/subset_selection_<run>.{md,json}`: per latent S\*, the
staircase, finalist forms re-clustered with Phase-2 machinery, η_S\* at full
protocol.

**Gate G2.** Amplitude latents return S\* = {A_s, τ} (or a superset that
beats it by > 1 SE — which would itself be a finding, given the known
shape-sector residual: the rule must *choose*, and the choice must be
reproducible across screen seeds). Shape latents: S\* recurrent across the
2 screen seeds; final claims only from 4b reruns.

---

## Phase 5 — the intrinsic information ceiling from the stochastic latent *(no new search)*

**Aim.** Replace "fraction of the maxsize-30 plateau" with "fraction of the
information the latent actually stores" (`next_step.md` §5). The mean map is
deterministic, so I(μ_k; θ) is unbounded; the sampled latent gives a finite,
principled ceiling:

```
I(Z_k; θ) = H(Z_k) − E_θ[ ½ ln(2π e σ_k²(θ)) ]
```

with the conditional entropy analytic from the cached logvars
(σ_k = exp(logvar/2), clamped to (−10, 10) as in the model).

**Method.** Draw m = 4 posterior samples per row over T1∪T2; estimate
H(Z_k) with a 1-D GMM (BIC over K ≤ 5) fit/held-out split over draws;
bootstrap SE. For each finalist f: η_post(f) = Î(Z_k; f(θ)) / Î(Z_k; θ)
with the numerator from the existing scalar–scalar GMM-MI machinery on
(sampled Z_k, f(θ)) over T2. Sanity checks: data-processing bound
Î(Z_k; f) ≤ Î(Z_k; θ) within SE; Gaussian-channel reference
½ ln(1 + Var(μ_k)/E[σ_k²]) as a cross-check column; per-latent noise table
(E[σ_k²], SNR) computed first — it predicts how binding the ceiling is
(β = 3e-4 posteriors may be near-deterministic; if σ spans decades the
MC-averaged conditional entropy from the logvars is still exact).

**Implementation.** `scripts/posterior_ceiling.py`; minutes on a laptop.

**Deliverable.** `experiments/posterior_ceiling_<run>.{md,json}`: per
latent I(Z_k; θ) ± SE, noise table, η_post for the canonical coordinate and
finalists. Cards switch headline metric to η_post; η_plat stays as the
high-resolution diagnostic.

**Gate G3.** DPI holds for all candidates; amplitude η_post(f₁) reported —
if the posterior noise sits above the shape-sector modulation, η_post → ~1
and the "primarily interpreted" residual is demoted to sub-noise detail
(a cleaner headline claim); if not, the residual is genuinely stored
information and Phase 6 matters.

---

## Phase 6 — second-stage discovery on structured residuals *(targeted new SR)*

**Aim.** For every latent whose residual audit failed with real stored
information (Phase 3 ∧ Phase 5): a hierarchical account
z_k ≈ h(f₁) + g(f₂) with f₂ discovered blindly (`next_step.md` §3).

**Method.** Target = cached `analysis/residual_z<k>_v1.npy` (cross-fitted on
T1, evaluated everywhere — no leakage into T0). Inputs = all 6 raw
parameters (restricting to S\*∁ would presume separability). Protocol
config, 5 seeds, via M1:

```bash
python scripts/run_blind_sr.py --run-dir models/<run> \
    --target-npy models/<run>/analysis/residual_z<k>_v1.npy \
    --target-label res_z<k> --inputs omega_b omega_cdm H0 tau A_s n_s \
    --seed $N --turbo --out-dir results/<run>/residual_sr/z<k>_seed$N
```

Consolidate with the Phase 1–3 machinery applied to the residual fronts
(knee, clusters, R_SR, signatures). Estimated ≤ 6 latents × 5 seeds ≈ 30
runs ≈ **45 core-h**. Shuffled-residual control: 1–2 runs per model reusing
`run_shuffled_control.py` semantics on the residual target.

**Deliverable.** `experiments/residual_sr_<run>.{md,json}`; cards gain the
f₂ line and the combined η(f₁, f₂).

**Definition of done.** Amplitude latents: f₂ is a shape-sector coordinate
(support ⊆ {ω_b, ω_cdm, H0, n_s}) with its own recurrence — the all-params
top forms (`A_s·(τ−c)` × log-shape factors) predicted exactly this
decomposition; confirming it validates the hierarchical readout.

---

## Phase 7 — interventional & observable-domain validation *(no new search; one shard pass)*

Association (even sufficient, recurrent association) is not yet a coordinate
claim. Two independent tests (`next_step.md` §6–§7):

### 7a — level-set invariance audit (local, cached data only)

For each canonical f: standardise, quantile-bin f into ~200 bins
(δ ≈ 0.5%); within bins draw pairs maximising distance in the complement
coordinates u_S∁; report

```
E_inv(f) = E[(μ_k(θ) − μ_k(θ'))² | pair] / (2·Var(μ_k))     (random pairs ⇒ 1)
```

as a curve vs nuisance distance plus the scalar (§0.3 threshold ≤ 0.05).
Complement test: k-NN match on u_S∁ (caliper), vary f — the response
μ_k vs f must collapse to a tight 1-D curve (spline R² ≥ 0.9). Controls:
the same statistic for shuffled-control forms (expect ≈ 1) and for the
*wrong* latent (specificity: f_amp should NOT be invariant for z_shape).
T1 pairs, T2 confirmation. `scripts/levelset_audit.py`.

Optional 7c extension (external dependency, only if a simulator becomes
available in the parent project): targeted CLASS/CAMB pairs on selected
level sets — the strongest form of the test; not required for the cards.

### 7b — decoder-effect triangulation (local decode; templates need one shard pass on CSD3)

1. **d_k(ℓ) = ∂Decoder(z)_ℓ/∂z_k** via autograd at z = μ̄ and across a
   latent spread (mean ± band); both checkpoints ship full decoders
   (`model.decode`), per-channel curves for the dual model. Un-normalise
   through `scaler.npz` (per-ℓ std) to physical log₁₀-spectrum effect.
   Purely local.
2. **Parameter templates t_j(ℓ) = ∂ log₁₀ D_ℓ / ∂θ_j** — data-driven, from
   the train-split shards on CSD3 (`scripts/spectral_templates.py`, one
   streaming pass, local-weighted linear fit at the prior midpoint in
   u-coordinates on a ~100k-row subsample; cache
   `data/spectral_templates_v1.npz`, small, check in). Optional CLASS
   finite-difference cross-check if 7c happens.
3. **Decompose** d_k ≈ Σ_j a_j t_j (lasso, W = identity in normalised
   space; (2ℓ+1)-weighted as sensitivity check). Report a\*_k, R²_W, and
   the triangulation: cos-similarity between normalised a\*_k and the
   symbolic signature g_j(f\*_k) from Phase 3.

Human-readable shape-latent labels ("peak shift", "tilt", "damping-tail")
are assigned only *after* looking at the derived d_k(ℓ) curves — recorded
next to, never instead of, the quantitative decomposition.

**Deliverables.** `experiments/levelset_audit_<run>.{md,json}`,
`experiments/decoder_effect_<run>.{md,json}`.

**Gate G4 (amplitude).** E_inv(f_amp) ≤ 0.05 with matched-nuisance response
1-D; decoder decomposition concentrated on the amplitude sector with
**a_τ/a_lnAs ≈ −2** — a third, fully independent, observable-domain readout
of the exponent (after the discovered forms and the derivative ratio).

---

## Phase 8 — subspace & redundancy analysis for what's left *(no new search)*

**Aim.** β-VAEs don't guarantee axis-alignment (`next_step.md` §8). For
latents (or candidate coordinates) failing 1-D sufficiency: decide
*subspace/mixed* vs *unresolved*.

**Method.** (i) Cross-validated sparse linear probe Z → f per physical
candidate f (lasso path: support + R² vs \|A\|) — which latent subset
carries each coordinate. (ii) Slab-conditional GMM-MI I(z_i; f \| z_j)
(quantile-slab average; documented as an approximation) for pairwise
redundancy — e.g. the EE model's two amplitude-sector latents z4/z5: is z4
a redundant copy of the τ direction given z5? (iii) For shape latents with
no adequate f: smallest latent set A with probe R²(f ← Z_A) ≈ R²(f ← Z)
for the *best* rejected candidates, distinguishing distributed encoding
from genuine entanglement.

**Implementation.** `scripts/subspace_probe.py`.
**Deliverable.** `experiments/subspace_probe_<run>.{md,json}`; final status
inputs for the cards.

---

## Phase 9 — representation stability across VAE seeds (R_model)

**Aim.** Five PySR seeds establish *search* stability on one checkpoint;
architecture-level claims need recurrence across independently trained VAEs
(`next_step.md` §9).

**Plan.**

1. Train 3 additional seeds per regime in the parent `cmbvae` repo with the
   stored `config_used.json` (only the seed changes). GPU cost as per
   parent-project training runs; outside this repo's CPU budget.
2. Transfer each into `models/lcdm_tt_beta3e-4_s<seed>/` etc. (checkpoint +
   scaler + config, same layout); encoder pass per model
   (`hpc/slurm_allparams_encode.sh`, needs shards, CSD3).
3. **Align** latent spaces to the reference checkpoints:
   `scripts/align_latents.py`, \|Spearman\| matching of μ-columns over T1
   with Hungarian assignment (CCA/Procrustes as robustness check); record
   the matching quality.
4. Rerun **finalist configs only** (S\* inputs, protocol budget, 5 seeds)
   for the amplitude latent and every latent whose card reached
   interpreted/primary — not the full pyramid. ≈ 6 models × 3 latents ×
   5 seeds ≈ 90 runs ≈ **135 core-h**. Then Phases 1–3 consolidation on the
   new fronts (cheap, automated by now).
5. **R_model** per cluster = fraction of aligned models where the cluster
   reaches η_S ≥ 0.95 on the matched latent.

**Deliverable.** `experiments/vae_stability_<regime>.{md,json}`. Cards
gain R_model; claims are downgraded to "per-model interpretation" wherever
R_model < 2/3. A bonus blind signature to check: the *count* of
amplitude-sector latents (1 in TT, 2 in TT+EE) should reproduce across
seeds — the degeneracy-breaking fingerprint from `docs/method.md` §1.

---

## Phase 10 — consolidation: latent cards, controls appendix, paper update

**Aim.** One synthesis pass, no new computation.

* `scripts/build_latent_cards.py` merges the JSON outputs of Phases 1–9
  into `experiments/latent_cards_<run>.{md,json}` — one §0.1 card per
  latent with status assigned by the frozen predicates, confirmatory
  numbers from T2, and a deviations column (threshold changes, screen
  truncations, anything).
* Controls appendix: every metric's null (shuffled-target, permutation,
  wrong-latent specificity) in one table.
* Update `README.md` ("Where the project stands", "Remaining gaps" → what
  closed), `docs/method.md` (+§9: from amplitude rediscovery to full
  representation cards; extend the §8 manuscript draft with the shape
  sector, η_post headline, level-set and decoder validation, R_model).
* Retire/annotate `docs/next_step.md` (superseded by this roadmap +
  results).

**Definition of done for the study.** Every latent of both models carries a
status with all supporting numbers reproducible from `experiments/*.json`;
the amplitude cards read "interpreted" (or "primarily interpreted" with the
η_post caveat resolved explicitly); no claim rests on an answer-aware
instrument.

---

## Budget summary

| Phase | New runs | Core-h (icelake, 16 threads/run) | Wall-clock at %16 |
|---|---:|---:|---:|
| 1b plateau firming | 33 | ~65 | < 1 h |
| 4a subset screen (TT+EE, full 63) | 1386 | ~1015 | ~4 h |
| 4b finalists | ≤ 275 | ≤ 405 | ~1.5 h |
| 4c per-latent controls (opt.) | 33 | ~48 | < 1 h |
| 6 residual SR | ~30 | ~45 | < 1 h |
| 9 finalist reruns (6 models) | ~90 | ~135 | < 1 h |
| 9 VAE training | 6 trainings | GPU, parent repo | — |
| Everything else | 0 | ~5 (7b shard pass) | — |
| **Total CPU** | **~1850** | **~1700 core-h** | |

Reference points: the hp_v1 sweep was ~77 core-h per model; the whole
roadmap is ≈ 11× that, dominated by the one campaign (4a) that closes the
last human choice in the loop. The pre-registered fallback (§Phase 4)
halves 4a if needed.

## Risk register (short)

| Risk | Phase | Mitigation |
|---|---|---|
| ms20 plateau proxy underestimates shape-latent ceilings | 1 | 1b ms30 batch; SE-aware knee rule |
| Lambdified forms non-finite off their fit range | 2–3 | anchor masking + finite-fraction reporting (in `semantics.py`) |
| Monotone-calibration assumption wrong for some latent | 3 | general-spline fallback, flagged on the card |
| Screen budget (ni100, 2 seeds) too noisy for frontier picks | 4a | 1-SE frontier band; finalists rerun at full protocol before any claim |
| GMM-MI SE underestimates at high MI (deterministic maps) | 1–5 | bootstrap SEs everywhere; η ratios, not raw MI, drive decisions; DPI sanity in Phase 5 |
| Posterior σ near-deterministic ⇒ noisy H(Z_k) | 5 | noise table first; Gaussian-channel cross-check; exact conditional term from logvars |
| Julia/PySR version drift across phases | 0 | pinned versions; protocol config frozen in specs |
| VAE retraining diverges from stored config | 9 | reuse `config_used.json` verbatim, seed-only change; alignment quality reported |

## Appendix — new files and interface changes

| ID | File | Kind | Phase |
|---|---|---|---|
| M1 | `scripts/run_blind_sr.py` `--target-npy/--target-label` | extension | 6 |
| M2 | `scripts/sweep_blind_sr.py` `mode: "subsets"` (+ per-config inputs in `tasks.tsv`) | extension | 4 |
| M3 | `src/cmb_lcdm_sr/semantics.py`, `src/cmb_lcdm_sr/tiers.py` | new module | 2–3 |
| M4 | `src/cmb_lcdm_sr/calibrate.py` | new module | 3, 6 |
| M5 | `scripts/knee_readout.py` | new consolidator | 1 |
| M6 | `scripts/semantic_recurrence.py` | new consolidator | 2 |
| M7 | `scripts/sufficiency_audit.py` | new consolidator | 3 |
| M8 | `scripts/consolidate_subsets.py` | new consolidator | 4 |
| M9 | `scripts/posterior_ceiling.py` | new script | 5 |
| M10 | `scripts/levelset_audit.py`, `scripts/decoder_effect.py`, `scripts/spectral_templates.py` | new scripts | 7 |
| M11 | `scripts/subspace_probe.py` | new script | 8 |
| M12 | `scripts/align_latents.py` | new script | 9 |
| M13 | `scripts/build_latent_cards.py` | final consolidator | 10 |

Each ships with tests (`tests/`), follows the `_bootstrap` import pattern,
and writes deliverables to `experiments/` in the `.md` + `.json` pair
convention.
