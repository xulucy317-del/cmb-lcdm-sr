"""cmb-lcdm-sr — blind symbolic interpretation of β-VAE CMB latents.

The library behind the study: loading the two stored β-VAE checkpoints
(trained in a separate reproduction of Piras et al. 2025, arXiv:2502.09810),
the encoder pass, the pure-Julia GMM-MI inner loss for PySR with post-hoc
held-out GMM-MI selection, the T0/T1/T2 data-hygiene tiers, and the semantic
and calibration machinery of the validation programme. The question it was
built to answer: can symbolic regression rediscover what a latent computes —
for the amplitude sector, the textbook combination ln(A_s·e^{−2τ}) — from a
trained encoder alone, with no hand-coded reference to the answer anywhere
in the pipeline?

Modules:
    model    — PirasCVAE / DualEncoderCVAE (needed to load stored checkpoints)
    scaler   — ShardedScaler (per-channel refs + normalisation stats)
    dataset  — sharded spectra streaming + test-split loader
    encoder  — checkpoint loading and the encoder pass over the test split
    mi       — post-hoc GMM-MI estimator (gmm-mi package, Piras+2023)
    sr       — the Julia GMM-MI inner loss and SR input construction
    tiers    — T0/T1/T2 evaluation slices + prior-box geometry (roadmap §0.4)
    semantics— form evaluation, equivalence clustering, Sobol (roadmap M3)
    calibrate— cross-fitted calibration h + residual diagnostics (roadmap M4)
"""

__version__ = "1.0.0"

from .sr import JULIA_LOSS_GMM_MI, INPUT_ALIASES, build_inputs  # noqa: F401
