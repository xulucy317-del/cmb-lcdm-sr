# Input completeness checklist

*Snapshot 2026-09-18. The public repository holds the code, both
checkpoints, the parameter table and every consolidated result; the items
below are the inputs it does **not** yet hold. Work through the sections in
order — each names the files, where the canonical copy lives, the command
that checks it and the output that means "done". `python scripts/check_inputs.py`
runs every machine check at once and labels its output with the same item
IDs. Tick a box only when its check passes.*

Canonical copies of everything live on CSD3 under
`PROJ=/rds/user/zx332/hpc-work/cmb-lcdm-sr` (results, caches) and
`/rds/user/zx332/hpc-work/cmbvae/data` (spectra shards). Before anything
else, on CSD3: `cd $PROJ && git fetch && git reset --hard origin/main`.

---

## A · Caches under `models/<run>/analysis/` → commit to git

`.gitignore` admits exactly these files (4 + 22 + the OLS-residual set,
≈15 MB). With them a clone runs every search, audit and campaign of
stages 1–3 without any other input.

### A1 · Encoder caches (4 files) — the target of every search

| # | file | shape | bytes | canonical sha256 | done |
|---|---|---|---|---|---|
| A1.1 | `models/lcdm_tt_beta3e-4/analysis/encoder_means_test.npy` | (50000, 5) float32 | 1,000,128 | `742822033dd8267d15a472e7f09eafc36c57bfa666b21bdb9872976aca58e5fa` | [ ] |
| A1.2 | `models/lcdm_tt_beta3e-4/analysis/encoder_logvars_test.npy` | (50000, 5) float32 | 1,000,128 | recorded by the manifest (B1) | [ ] |
| A1.3 | `models/lcdm_tt_ee_lowl/analysis/encoder_means_test.npy` | (50000, 6) float32 | 1,200,128 | `cf1d8b09744f8a2a6a5c7412ee2463fbc251ca55a8b27d067259f69cf3ad1467` | [ ] |
| A1.4 | `models/lcdm_tt_ee_lowl/analysis/encoder_logvars_test.npy` | (50000, 6) float32 | 1,200,128 | recorded by the manifest (B1) | [ ] |

### A2 · Residual caches (22 files, all hash-pinned) — entry points of phases 5–8 and stage 2

Rebuilding these needs the raw stage-1 fronts (`sufficiency_audit.py` reads
them), so they are committed rather than regenerated.

| # | files (per run: k = 0…4 for TT, 0…5 for EE) | bytes each (float64) | canonical sha256 | done |
|---|---|---|---|---|
| A2.1 | `models/<run>/analysis/residual_z<k>_v1.npy` — stage-1 residual e₁ = μ − h(f₁) (11 files) | 400,128 | pinned in `experiments/mse_one_stage_state_csd3.json` | [ ] |
| A2.2 | `models/<run>/analysis/f1hat_z<k>_v1.npy` — stage-1 prediction h(f₁) (11 files) | 400,128 | pinned in `experiments/mse_one_stage_state_csd3.json` | [ ] |
| A2.3 | `models/lcdm_tt_ee_lowl/analysis/residual_ols_z<k>_v1.npy` — the stage-3 targets, built only for the EE latents that search ran on (z₀ and z₄ at least), plus `residual_ols_v1_fit.json`, their provenance | 400,128 | recorded by the manifest (B1); per-file sha256 also inside `residual_ols_v1_fit.json` | [ ] |

**Do (on CSD3):**

```bash
python scripts/check_inputs.py        # A1: "canonical" for A1.1 and A1.3; A2: 22/22 present, 22/22 canonical; A2.3 lists what exists
git add models/lcdm_tt_beta3e-4/analysis/ models/lcdm_tt_ee_lowl/analysis/
git status --short models/            # 4 + 22 + the A2.3 files, nothing else (everything else in analysis/ stays ignored)
git commit -m "Ship the canonical encoder and residual caches" && git push
```

**Check:** `git ls-files models/*/analysis/ | wc -l` → `26` plus the A2.3
files; `python scripts/check_inputs.py` → `SR searches on the latents
(stage 1) ... yes`, `audits and campaigns on the residuals ... yes` and
`stage-3 search on the OLS residual (EE z0, z4) .. yes`, with no `MISMATCH`
anywhere and no "not the canonical bytes" caveat.

> The copy of A1.1/A1.2 on the Mac checkout is **not** canonical (its
> `encoder_means_test.npy` hashes to `31a30cb9…`, an encoder pass on
> different hardware). It must not be committed; see E1.

---

## B · Manifest → commit to git

| # | file | done |
|---|---|---|
| B1 | `data/inputs_manifest.json` — sha256 of every file in A, of each of the 200 spectra shards, and one aggregate per campaign of raw fronts, with counts | [ ] |

**Do (on CSD3, after A, with `results/` present):**

```bash
python scripts/check_inputs.py --write-manifest --shards-root /rds/user/zx332/hpc-work/cmbvae/data
python - <<'EOF'
import json; m = json.load(open("data/inputs_manifest.json"))
print(len(m["files"]), "files;", len(m["results"]), "campaigns;",
      sum(v["n_reports"] for v in m["results"].values()), "report.json in total")
EOF
git add data/inputs_manifest.json && git commit -m "Record the inputs manifest" && git push
```

**Check:** the print shows `240 files` plus the A2.3 files (14 repo + 4 +
22 caches + 200 shards + A2.3) and a campaign list matching table D; from then on `check_inputs.py` ends
with `canonical hashes from data/inputs_manifest.json`.

---

## C · Spectra shards → deposit outside git (≈7 GB)

Read only by the encoder pass, `spectral_templates.py` and the stage-4
attribution scripts (`encoder_gradient_attribution.py`,
`encoder_trunk_probe.py`).

| # | files | count | size | done |
|---|---|---|---|---|
| C1 | `shards_global_lhs/spectra_00000.npz … spectra_00099.npz` (TT channel) | 100 | roughly 35 MB each, ≈3.4 GB | [ ] |
| C2 | `shards_global_lhs_ee_lowl/spectra_00000.npz … spectra_00099.npz` (EE channel) | 100 | roughly 35 MB each, ≈3.4 GB | [ ] |
| C3 | persistent identifier (DOI / release URL) recorded in `README.md` "Data and models" and `data/README.md` | — | — | [ ] |

**Do (on CSD3):**

```bash
tar -C /rds/user/zx332/hpc-work/cmbvae/data -czf cmb-lcdm-sr-shards.tar.gz shards_global_lhs shards_global_lhs_ee_lowl
sha256sum cmb-lcdm-sr-shards.tar.gz > cmb-lcdm-sr-shards.tar.gz.sha256
```

then deposit (Zenodo takes 50 GB per record; GitHub release assets are
capped at 2 GB per file) and record the identifier.

**Check (anywhere, after extracting the archive to `<dir>`):**
`python scripts/check_inputs.py --shards-root <dir> --full` →
both channels `ok (all hashed)` (needs B1; before B1 only the zip-integrity
test runs) and `encoder pass, templates, stage-4 attribution ... yes`.

---

## D · Raw fronts → deposit outside git

Needed only to re-run a `consolidate_*` script on the published campaigns
instead of re-running their searches. Counts are per checkpoint
(TT = `lcdm_tt_beta3e-4`, 5 latents; EE = `lcdm_tt_ee_lowl`, 6 latents); the
manifest (B1) records the exact number of `report.json` files per campaign
and is the authority where a row says "varies".

| campaign directory under `results/<run>/` | TT | EE | total | what |
|---|---|---|---|---|
| `symbolic_regression_gmm_mi_seed<0–4>` | 5 | 5 | 10 | reference (A_s, τ) study |
| `symbolic_regression_shuffled_seed<0–2>` | 3 | 3 | 6 | its shuffled controls |
| `allparams` (+ `shuffled_z<amp>_s*` controls) | 25 | 30 | 55 + controls | six-input search, maxsize 20 |
| `allparams_ms10` | 25 | 30 | 55 | maxsize-10 rerun |
| `allparams_ms30` | 15 | 18 | 33 | maxsize-30 rerun, 3 seeds |
| `hpsweep_hp_v1` | 36 | 36 | 72 | hyperparameter sweep |
| `hpsweep_subsets_v1` | 630 | 756 | 1,386 | Phase-4 screen: 63 supports × latents × 2 seeds |
| `hpsweep_subsets_v1_finals` | varies | varies | — | Phase-4b finalists at full protocol |
| `hpsweep_subsets_full` | 1,575 | 1,890 | 3,465 | R-P4 exhaustive grid (2,425 fresh, the rest linked from finals/allparams) |
| `sham_control` | 75 | 90 | 165 | R-P4 dilution control: 3 donors × latents × 5 seeds |
| `residual_sr` (+ shuffled-residual controls) | 25 | 30 | 55 + controls | Phase-6 second-stage search |
| `residual_sr_ia` (+ 6 controls) | 25 | 30 | 61 | interaction-aware rerun |
| `mse_one_stage_ms20`, `_ms30`, `_ms40` | 25 each | 30 each | 165 | stage 2, MSE ladder |
| `mse_one_stage_control_ms20`, `_ms40` | 3 each | 3 each | 12 | its shuffled controls |
| `precision_preprocess_v1/{raw64,physical_o1_64,logamp64}` | 165 | 165 | 330 | stage 2, float64 arms |
| `coordinate_matched_ols_v1` | fit / calibration / confirmation JSON, no searches | | — | stage 2, OLS audit |
| `residual_sr_ols` | — | 14 | 14 | stage 3: EE z₀, z₄ searches + controls |

| # | item | done |
|---|---|---|
| D1 | archive of `results/` without the `pareto.png` renders (keep `report.json`, `equations.csv`, manifests, `tasks.tsv`, the campaign `{manifest,calibration,confirmation}.json`) | [ ] |
| D2 | persistent identifier recorded in `README.md` and `results/README.md` | [ ] |

**Do (on CSD3):**

```bash
tar --exclude='*.png' -czf cmb-lcdm-sr-results.tar.gz results/
sha256sum cmb-lcdm-sr-results.tar.gz > cmb-lcdm-sr-results.tar.gz.sha256
du -sh cmb-lcdm-sr-results.tar.gz      # decides Zenodo vs a GitHub release (2 GB/file cap)
```

**Check (anywhere, after extracting at the repository root):**
`python scripts/check_inputs.py --full` → every campaign `canonical`,
and `re-consolidate published campaigns ... N/N campaigns present`.

---

## E · Local checkouts

| # | machine | do | done |
|---|---|---|---|
| E1 | Mac (`~/Downloads/csd3/cmb-lcdm-sr`) | `rm models/lcdm_tt_beta3e-4/analysis/encoder_{means,logvars}_test.npy && git pull` — the non-canonical copies would otherwise block the pull; then `python scripts/check_inputs.py` → all `canonical` | [ ] |
| E2 | CSD3 (`$PROJ`) | `git fetch && git reset --hard origin/main` before A; `git status` clean after B | [ ] |
| E3 | any new clone | `git clone … && pytest -q && python scripts/check_inputs.py` → the summary reads `yes` for stages 1–3 with nothing fetched; `--shards-root` / the results archive only for the last two lines | [ ] |

---

## Not on this list

* `logs/`, `.venv*`, PySR state, `figures/_cache_audit_mi.npz`: scratch,
  regenerated on use.
* `experiments/`: complete in git (every consolidated deliverable).
* The archived write-ups and the paper draft: complete in git.
