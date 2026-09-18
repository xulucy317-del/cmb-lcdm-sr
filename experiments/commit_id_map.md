# Commit ID map (development history → published history)

The development history was rewritten at public release — once on the
morning of 2026-09-18 (descriptive subjects for six commits, one author
identity, private session-link trailers dropped) and once that evening
(the author identity set to the repository owner's, tool co-author
trailers removed, and the day's release-engineering commits collapsed
into three). **Every commit's content (tree), author date and committer
date were kept**, so the ordering that the pre-registration claims rest on
is unchanged, and any old commit ID can be checked against its replacement
by comparing tree hashes. Commit IDs quoted inside the provenance records
(`experiments/mse_one_stage_execution_provenance.json`,
`experiments/mse_one_stage_lightning_runbook.md`, the latent cards and
`scripts/build_latent_cards.py`) are the
development-history IDs in the first column; the second column is the
ID under which the same commit was briefly published between the two
rewrites; the third is the published history.

56 commits, oldest first. The three public-release commits that
follow them in the history had no prior IDs to map.

| development | interim | published | tree | date | subject |
|---|---|---|---|---|---|
| `7de2944cf1` | `012a7c2a97` | `fc60b5ce3e` | `baf2cee2ab` | 2026-08-01 | Extract the blind-SR study into a standalone repository *(was “setup”)* |
| `32f4c23f4a` | `55fa9f3f76` | `1a1ed2962a` | `c6b5c4bbf8` | 2026-08-01 | All-params blind SR + automated PySR hyperparameter-sweep pipeline |
| `7d53a43986` | `f9b5e49762` | `e175dc0c1a` | `d60c9a0152` | 2026-08-03 | Discovery roadmap and its Phase-0 infrastructure *(was “pipeline”)* |
| `bfad12576f` | `5c27c732a7` | `5631592b99` | `331a798137` | 2026-08-03 | Phase 1: knee & plateau saturation readout (+ ms30-firmed deliverables) |
| `fb51ba1912` | `017aa02f34` | `08cf320418` | `54a7fe9b0f` | 2026-08-03 | Phase 2: semantic clustering & seed recurrence |
| `b34e352ad7` | `7e6aed0970` | `df5a77de54` | `d94407cf07` | 2026-08-03 | Phase 3: sensitivity signatures + calibrated sufficiency audit; gate G1 PASS |
| `8dede79b7c` | `d38748573e` | `198ab237cd` | `4853d64fd8` | 2026-08-03 | Phase 4a: blind subset-screen specs + consolidation (screen submitted) |
| `7b70f2f98e` | `a4a0f6c458` | `7e49746e3f` | `c407deaa09` | 2026-08-04 | Phase 4a screen complete + 4b fold-in machinery; finalists submitted |
| `7bcbc9ebdf` | `ac1722c1d6` | `ff1d483a46` | `4b2193c4ca` | 2026-08-04 | Phase 4 complete: 4b finals consolidated, gate G2 evaluated |
| `fb2b1479b6` | `795591843f` | `9054baf0f2` | `8afc6d94bd` | 2026-08-05 | Phase 5: intrinsic posterior ceiling + gate G3 (TT; EE job in flight) |
| `68851fb8e4` | `57f527ec40` | `d09cc8144e` | `4d30e459db` | 2026-08-05 | Phase 6 machinery: residual SR wrapper, shuffled-residual control, consolidator |
| `61db1255a1` | `774b27a3a0` | `8dca21a30a` | `63ecd4c1b8` | 2026-08-05 | Phase 7a: level-set invariance audit, both models; gate G4a honest FAIL |
| `248f60d756` | `335a122e7d` | `a8d3b3768b` | `7ceeccc69e` | 2026-08-05 | Phase 5 complete: EE posterior ceiling; gate G3 PASS both models |
| `fb540a1c81` | `8d135fa5a2` | `716555c794` | `2617c9cdd2` | 2026-08-05 | Phase 7b: decoder-effect triangulation + data-driven spectral templates |
| `7f3c051b95` | `5f36808c1b` | `993bd5089f` | `32ba2d8239` | 2026-08-06 | Phase 6 consolidation: parallel perm-null MI, stage timing, 12h wrapper |
| `a38e6c8a6f` | `a3b648bce5` | `269c34f876` | `d69a5fe2c9` | 2026-08-06 | Phase 6 complete: residual SR results, f2 for all 11 latents |
| `a1f7b2be00` | `c413eb9e81` | `1372784e2d` | `52fdc64a9c` | 2026-08-06 | Phase 7a follow-up: joint (f1,f2) level-set audit; G4a-joint PASS on EE |
| `4b52261fc4` | `73d737b13b` | `91018dc493` | `0b35e30f48` | 2026-08-06 | Phase 8 machinery: subspace probe (lasso carrier sets + slab-conditional MI) |
| `dc7f9cb85d` | `aca54a68fa` | `06f61f0756` | `99240418c5` | 2026-08-06 | Phase 10 machinery: latent-card builder (frozen predicates + deviations) |
| `fcb36fcbba` | `0c431b3bf9` | `6556fc2977` | `d585d5dbf6` | 2026-08-06 | Phase 8 complete: subspace probe results, both models |
| `cb92168b8d` | `5d2e1dc2ab` | `3871ee682b` | `f8115974dd` | 2026-08-06 | Phase 10 complete: latent cards both models; README + method.md synthesis |
| `dbd77dc18b` | `895f80b906` | `ec3d7bd1a3` | `938072a8bb` | 2026-08-09 | Close the discovery roadmap without Phase 9 *(was “wrap up”)* |
| `2ab12e3025` | `14c761ace1` | `22c58542c2` | `c005afbae7` | 2026-08-09 | Interaction-aware stage 2 complete: D-DoD-z2 is real structure; EE z0 f2 unanimous but card stays unresolved |
| `cb1221a2a7` | `2485b8938c` | `845b094906` | `5b4b513cf0` | 2026-08-09 | Results compendium: every result in one digest, for the official write-up |
| `03380b6217` | `ff4f6c3698` | `a5c8a65126` | `1c7da5c50f` | 2026-08-13 | Paper draft: official write-up from the results compendium |
| `dd512b5b7d` | `64713ec753` | `d24b0c4a69` | `714d8a8b2e` | 2026-08-18 | Report skeleton, and method.md rewritten as the methodology pipeline *(was “report”)* |
| `f60de00b9d` | `2d4e59e33d` | `3a76085289` | `25966359ec` | 2026-08-13 | R-P4 pre-registration: exhaustive support at full protocol + sham dilution control |
| `34d6632f4d` | `1ddc45c873` | `28eb154d7b` | `d15719a5a1` | 2026-08-13 | R-P4 consolidators: written blind, before the grid finished |
| `f750e040a9` | `dcad4ed8c7` | `3dcbc33235` | `20c1e1107e` | 2026-08-14 | R-P4 complete: exhaustive grid + sham control, consolidated under the frozen rules |
| `3a61ce05a0` | `aec83c2817` | `5c481a94c7` | `f6a94735e5` | 2026-08-14 | Cards carry R-P4: s_star.exhaustive_full field + N-G2 dispositions |
| `aa1907db43` | `c5d20b1521` | `31f48f5d11` | `3bcf00032d` | 2026-08-14 | R-P4 folded into the compendium and the paper draft |
| `cbd93858b1` | `1ad382ae21` | `dbaec4c8b0` | `a8d5af09c4` | 2026-08-18 | Report figures: one make_fig_ script per figure ID, renders, build notes *(was “figs”)* |
| `346b65843f` | `34d6702250` | `08a7b0b400` | `388bcbaf8f` | 2026-08-25 | One-stage MSE latent reconstruction: search, controls, consolidation |
| `bb285a1582` | `7906d38a1a` | `1d9c4a5bf8` | `0cd01d4f5d` | 2026-08-25 | Scheduler-free resume kit: finish the MSE experiment off CSD3 |
| `434e8930f8` | `8802dc7e19` | `c9176f58b5` | `488fc0e835` | 2026-08-25 | bootstrap: seed pip when uv creates the venv |
| `89e438fcad` | `69e780b74c` | `48d39a9c01` | `5c2186d521` | 2026-08-26 | Fix argument parsing in both consolidation launchers |
| `ac7b7049e0` | `93ea9f3413` | `96522ade1b` | `73d45455a4` | 2026-08-26 | Record the Lightning Studio machine state |
| `346e43d15e` | `211c7653c7` | `a3e96c779b` | `e19cc675a7` | 2026-08-26 | One-stage MSE experiment complete: no latent replaces the two-stage hierarchy |
| `982a229efb` | `a0cf69697d` | `ce7a6fb739` | `08b1738919` | 2026-08-26 | docs: combined one-stage MSE write-up, methods, compendium entry |
| `44b8fe8b90` | `7ac264a1f7` | `3bf0b55f24` | `2a15283638` | 2026-08-26 | docs: include the searched expressions in the combined write-up |
| `1fb51ebe02` | `282a8a6c97` | `44f6187333` | `1de6d5d567` | 2026-08-26 | Stage-1 report: report.md built out from the content plan *(was “report”)* |
| `15b23e9b74` | `9961183c97` | `f78fce4934` | `399c93e5c8` | 2026-08-26 | docs: restyle the result tables in the report's T4.1 conventions |
| `71b395cd9f` | `cd982c106a` | `a323162bcb` | `817316cec2` | 2026-08-26 | docs: correct the linearity over-reading in section 5.2 and TM4 |
| `ee4a08fbd5` | `2413dd0bfb` | `7a2b4f3b1a` | `ae849f58e6` | 2026-08-26 | docs: summarise the MSE expression families by complexity ceiling |
| `5a0b44b9d0` | `4ae3e2e031` | `35b08b5cf0` | `c88ebdee6f` | 2026-08-26 | docs: show the expressions themselves at each complexity ceiling |
| `821946b5b1` | `0f93b00209` | `1cd9a7776e` | `fb2a007fbf` | 2026-09-02 | feat: float64 precision/preprocessing arms and the v1 campaign |
| `e03b44c794` | `bc67cf76af` | `9a02868081` | `139103db46` | 2026-09-02 | feat: coordinate-matched OLS audit of the precision campaign |
| `0cb1d2e871` | `22bc8aa718` | `d75b704d39` | `6856a78cd2` | 2026-09-02 | feat: step-2 blind SR on the exact OLS residual |
| `e7f98330ea` | `13eab41060` | `a10b207be0` | `6c24576244` | 2026-09-02 | docs: the OLS vs MI-SR vs MSE-SR decision checkpoints |
| `675a2a1324` | `66827623d8` | `ba05f6110f` | `ef5601f154` | 2026-09-03 | docs: discussion record — what SR was for, and the verified repo status |
| `70cad8007a` | `8a3ac345ee` | `4dbafe4090` | `ec133c610a` | 2026-09-03 | chore: green the suite on CSD3 and drop stale tree files |
| `964b38e23f` | `19e381a2f1` | `b9bb47b8ef` | `281744e794` | 2026-09-03 | feat: close three citability gaps — capacity, noise floor, and the OLS ceiling |
| `00a4e64af2` | `15d778d8d3` | `f32f960e40` | `ae0d5fe9b4` | 2026-09-03 | feat: encoder-side attribution — gradients, trunk probe, input optimisation |
| `a29ae9e80c` | `b3e87748f1` | `ee26320b7b` | `844ed837ce` | 2026-09-03 | docs: fold the 2026-09-03 pass into the record and the discussion |
| `7cc278e617` | `994ebcc168` | `3abf3fda5a` | `0785f5b20f` | 2026-09-04 | docs: conclusive report for newcomers, plus figures F12.1–F14.1 |
| `86d515c81e` | `c38821396a` | `2327861ca6` | `77193597db` | 2026-09-10 | chore: close out the repo — prune dead files, point the README at the record |
