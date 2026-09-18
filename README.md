# cmb-lcdm-sr

**Blind symbolic interpretation of the latents of two CMB β-VAE compressors.**
Starting from the six ΛCDM parameters alone, can a symbolic search recover
the formula each latent computes — and prove it is right? The search is
scored by mutual information (invariant to how a latent is scaled), the
textbook answer `A_s·e^{−2τ}` is computed nowhere in the pipeline, every
pass/fail rule was frozen before the results were seen, and a pre-registered
linear baseline was run afterwards to find out what the search had added.

**The report is [`index.html`](index.html)** — open it in a browser (or
serve it with GitHub Pages).

## Findings

1. **Discovery.** Every one of the 11 latents has a recurring symbolic
   coordinate. The −2 of `A_s·e^{−2τ}` is recovered blind five independent
   ways (derivative ratio −1.974 ± 0.018 TT / −1.993 ± 0.008 TT+EE). Adding
   polarization *splits* the amplitude information across two latents rather
   than duplicating it. 10/11 latents are "primarily interpreted" under the
   frozen rules.
2. **Linear baseline.** A seven-number linear fit matches or beats the
   discovered formulas on most latents, on reconstruction and on
   information — and the search never generated the linear candidate. Over
   this parameter box the latents are ~99.8 % weighted sums of the
   parameters, because in the log-spectrum basis the leading physics *is*
   additive.
3. **The ladder.** An exact quadratic closes most of what the linear fit
   leaves for nine latents; on the other two the search finds a pole in τ
   (`A_s/τ`) and a rational curvature no polynomial expresses.
4. **Inside the encoder.** One latent alone reads the reionization window;
   the temperature-only network discards the (A_s, τ) split at its final
   compression step.

<p align="center">
  <img src="figures/amplitude_scatter.png" width="85%"
       alt="Amplitude latent of each network against ln(A_s e^-2tau)">
</p>

## Quick start

```bash
git clone https://github.com/xulucy317-del/cmb-lcdm-sr.git && cd cmb-lcdm-sr
python3.12 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
pytest -q                          # 347 tests, ~8 min
python scripts/check_inputs.py     # what this checkout can run
# one blind search on the TT amplitude latent (PySR fetches Julia on first use)
python scripts/run_blind_sr.py --run-dir models/lcdm_tt_beta3e-4 --latent-index 2 --inputs A_s tau --seed 0
```

A clone runs every search, audit and campaign of stages 1–3 as is; the raw
fronts of the ≈5,100 published searches are a 13 MB asset of release
[`v1.0.0`](https://github.com/xulucy317-del/cmb-lcdm-sr/releases/tag/v1.0.0),
and the spectra themselves are not published. What a clone needs, the full
pipeline and how to run it on another cluster:
[`scripts/README.md`](scripts/README.md) and [`hpc/README.md`](hpc/README.md).

## Layout

```
index.html         interactive report
src/cmb_lcdm_sr/   library: models, encoder pass, GMM-MI inner loss, tiers, semantics
scripts/           every runner, audit and consolidator          → scripts/README.md
hpc/               launchers, and wrappers for other clusters    → hpc/README.md
experiments/       consolidated results of every campaign        → experiments/README.md
figures/           report figures and their generators           → figures/README.md
data/  models/     parameter table, splits, priors; the two checkpoints and their caches
tests/             pytest suite
```

## Citation

Cite the repository ([`CITATION.cff`](CITATION.cff)). The β-VAE architecture
follows [Piras, Herold, Lucie-Smith & Komatsu (2025)](https://arxiv.org/abs/2502.09810);
the MI estimator is [GMM-MI](https://github.com/dpiras/GMM-MI); the search
engine is [PySR](https://github.com/MilesCranmer/PySR). MIT License.
