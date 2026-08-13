# Official write-up (draft)

`main.tex` — the paper, drafted 2026-08-09 from
[`docs/results_compendium.md`](../docs/results_compendium.md) (commit
`cb1221a`). Every number is a T2-confirmed value tracing to a consolidated
deliverable in `experiments/`; the claim structure follows the compendium's
§9 ranked menu (C1–C8).

Build (two passes; plain `article`, no bibtex needed):

```bash
pdflatex main && pdflatex main
```

Figures (`figs/`):

* `amplitude_scatter.pdf` — Fig. 1, amplitude latent vs. the textbook
  combination (post-hoc illustration only; the derived combination is computed
  in the figure script, never in the search pipeline). Regenerate:
  `.venv/bin/python figs/make_fig_amplitude.py`.
* `knee_readout_lcdm_tt_ee_lowl_envelopes.png` — Fig. 2, copied verbatim from
  `experiments/`.
* `decoder_amplitude.pdf` — Fig. 3, amplitude rows of the decoder-effect
  curves, rebuilt in physical units from
  `experiments/decoder_effect_lcdm_tt_ee_lowl_curves.npz`. Regenerate:
  `.venv/bin/python figs/make_fig_decoder.py`.

Before submission: replace the placeholder author block (marked `TODO` in
`main.tex`).
