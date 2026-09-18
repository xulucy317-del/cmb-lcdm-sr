# docs/ — reading guide

The project ran in four stages (`report_conclusive.md`, at the repository
root, is the write-up of record for all of them). The documents here are the
stage-level records it draws on, in the order they were written. "Status"
says whether a document is still the reference for its subject or has been
superseded by a later one; superseded documents are kept unchanged because
later records cite them by section.

## Current

| document | what it is | status |
|---|---|---|
| [`findings_atlas.html`](findings_atlas.html) / [`findings_atlas.md`](findings_atlas.md) | the closing findings as an interactive page (open in a browser) and its text-only twin, regenerated from the HTML by `scripts/html_to_markdown.py` | current |
| [`method.md`](method.md) | the stage-1 methodology in one file: what is fixed before any search, the five instruments, the −2 read three ways, limitations; §5 covers the MSE follow-up | current for stage 1 |
| [`discovery_roadmap.md`](discovery_roadmap.md) | the pre-registered validation programme: frozen thresholds (§0.3), phases 0–10 with budgets and gates, the closure of 2026-08-09, the R-P4 post-closure pre-registration. The rules were committed before the shape-sector latents were examined | the reference for every frozen rule |
| [`results_compendium.md`](results_compendium.md) | every stage-1 number, layer by layer, traced to its `experiments/` file; §7 collects every control, §9 ranks the candidate claims | current for stage 1 |
| [`mse_one_stage_results.md`](mse_one_stage_results.md) | the one-stage MSE reconstruction study (stage 2, first campaign): what was run, the decision ledger, the known-f₂ absorption test, the expressions at each complexity ceiling | current |
| [`precision_preprocess_v1_comparison.md`](precision_preprocess_v1_comparison.md) | the float64 precision / input-preprocessing campaign, rendered from `experiments/precision_preprocess_v1_comparison.json` | current (generated) |
| [`coordinate_matched_ols_v1.md`](coordinate_matched_ols_v1.md) | the coordinate-matched OLS audit, rendered from `experiments/coordinate_matched_ols_v1.json` | current (generated) |
| [`ols_mi_sr_mse_sr_t2_comparison.md`](ols_mi_sr_mse_sr_t2_comparison.md) | the original three-way T2 snapshot (OLS vs MI-selected SR vs MSE-selected SR) that the two assessments below were both built on; also embedded verbatim in the decision checkpoint | frozen input |
| [`sr_vs_ols_decision_checkpoint.md`](sr_vs_ols_decision_checkpoint.md) | the decision checkpoint on symbolic regression versus the linear baseline, frozen 2026-08-31 — one of two independently drafted assessments. The precision-campaign consolidator reads its frozen OLS table cells (`scripts/consolidate_precision_preprocess.py --baseline-report`) | frozen input |
| [`evidence_record.md`](evidence_record.md) | **the record** for stages 2–4: what each claim rests on after the linear-baseline audit, the per-latent ledger, what stands and what is weakened, the additive-physics reading and the linear → quadratic → SR ladder, the open items and their closure. Drafted independently of the checkpoint above, then completed against it | current |
| [`sr_objective_discussion_2026-09-02.md`](sr_objective_discussion_2026-09-02.md) | the discussion behind the record: what the symbolic search was for, the four-step storyline, and the decision to write `report_conclusive.md` | current |

## Superseded

| document | what it is | superseded by |
|---|---|---|
| [`next_step.md`](next_step.md) | the methodological programme drafted after the six-input search (definitions of "interpreting a latent", the knee readout, semantic pooling, sufficiency, level sets, …), with the derivations the roadmap points back to | `discovery_roadmap.md`, which made it executable |
| [`report_content.md`](report_content.md) | the long-form stage-1 report: the full argument with every table and figure, the deviations register in place, and the build notes for figures F1–F11 | `report_conclusive.md`; still the specification of the F1–F11 figures |
| [`archive/report_stage1.md`](archive/report_stage1.md) | the stage-1 write-up as drafted on 2026-08-26 (previously `report.md` at the root) | `report_conclusive.md` |
| [`archive/paper_draft/`](archive/paper_draft/README.md) | a two-column LaTeX draft of 2026-08-14 with a placeholder author block; states a decoder-side −2 readout that was later withdrawn | `report_conclusive.md` |

## Files renamed at public release

The provenance records in `experiments/` (the MSE execution-provenance
file, the two machine-state files, the campaign confirmations) and some
older documents refer to files by the names they had while the work was
being done. Content was not changed by any of these moves.

| then | now |
|---|---|
| `docs/ols_mi_sr_mse_sr_t2_comparison_claude_output.md` | `docs/evidence_record.md` |
| `docs/ols_mi_sr_mse_sr_t2_comparison_codex_output.md` | `docs/sr_vs_ols_decision_checkpoint.md` |
| `docs/ols_mi_sr_mse_sr_t2_comparison.md.orig` | `docs/ols_mi_sr_mse_sr_t2_comparison.md` (the name the confirmations reference) |
| `report.md` (repository root) | `docs/archive/report_stage1.md` |
| `paper/main.tex`, `paper/main.pdf`, `paper/README.md` | `docs/archive/paper_draft/` |
| `paper/figs/` | `figures/` |
| `paper/figs/knee_readout_lcdm_tt_ee_lowl_envelopes.png` | removed — a copy of `experiments/knee_readout_lcdm_tt_ee_lowl_envelopes.png` |
| `docs/findings_atlas_files/figure_01.png` | removed — a copy of `figures/F4_1_envelopes.png` |
| `paper/figs/F5_3_residual_audit.{pdf,png}` | removed — the earlier two-panel render; the script now writes `F5_3_residual_structure` |

The commit history was also rewritten once, at public release, to give six
commits a descriptive subject, normalise one author identity and drop two
private session-link trailers; every commit's content and dates were kept.
Commit IDs quoted inside provenance records and older documents map to the
published history in [`commit_id_map.md`](commit_id_map.md).
