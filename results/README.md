# results/ — raw run outputs (not committed)

Every search and audit writes its raw output under this directory, one
sub-directory per stored model:

```
results/<run>/<campaign>/<task>/report.json     one PySR search: Pareto front, per-equation scores, config
results/<run>/<campaign>/<task>/equations.csv   the same front as PySR wrote it
results/<run>/<campaign>/<task>/pareto.png
results/<run>/sr_pooled/                        cross-seed pooling (scripts/pool_sr_runs.py)
results/<run>/<campaign>/{manifest,calibration,confirmation}.json
                                                hashed stage artifacts of the MSE / precision campaigns
```

with `<run>` one of `lcdm_tt_beta3e-4` (TT-only) or `lcdm_tt_ee_lowl`
(TT+EE-lowl) and `<campaign>` such as `allparams`, `hpsweep_hp_v1`,
`residual_sr`, `mse_one_stage_ms40`, `precision_preprocess_v1/raw64`.

The directory is git-ignored: the raw fronts of the ~5,100 searches behind
the reported results live on the machines that ran them (CSD3, a Lightning
AI Studio, a Mac). What the repository commits instead is the consolidated
form of every campaign, under [`experiments/`](../experiments/README.md),
which is what the reports and figures are built from. The `consolidate_*`
scripts read this directory and write those files.

To re-consolidate a published campaign, download the raw-fronts archive
attached to release `v1.0.0`
(<https://github.com/xulucy317-del/cmb-lcdm-sr/releases/download/v1.0.0/cmb-lcdm-sr-results.tar.gz>, 13 MB; PNG renders and PySR checkpoints excluded), extract it at
the repository root so that it recreates this layout, then run
`python scripts/check_inputs.py --full` to verify it against
`data/inputs_manifest.json` before running the `consolidate_*` script:

```bash
gh release download v1.0.0 -p 'cmb-lcdm-sr-results.tar.gz*'
shasum -a 256 -c cmb-lcdm-sr-results.tar.gz.sha256 && tar -xzf cmb-lcdm-sr-results.tar.gz
python scripts/check_inputs.py --full        # 35/35 campaigns canonical
```
