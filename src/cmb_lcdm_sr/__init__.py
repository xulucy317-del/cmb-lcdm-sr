"""cmb-lcdm-sr — blind symbolic regression of β-VAE CMB amplitude latents.

A distilled, standalone extraction of the blind-SR study from the parent
``cmbvae`` reproducibility project (Piras et al. 2025, arXiv:2502.09810
reproduction). This package keeps exactly one search configuration: PySR with
the pure-Julia GMM-MI inner loss, selected post hoc by held-out GMM-MI. The
question it answers: can symbolic regression rediscover the textbook TT
amplitude combination ln(A_s·e^{−2τ}) from a trained encoder alone, with no
hand-coded reference to the answer anywhere in the pipeline?

Modules:
    model    — PirasCVAE / DualEncoderCVAE (needed to load stored checkpoints)
    scaler   — ShardedScaler (per-channel refs + normalisation stats)
    dataset  — sharded spectra streaming + test-split loader
    encoder  — checkpoint loading and the encoder pass over the test split
    mi       — post-hoc GMM-MI estimator (gmm-mi package, Piras+2023)
    sr       — the Julia GMM-MI inner loss and SR input construction
"""

__version__ = "0.1.0"

from .sr import JULIA_LOSS_GMM_MI, INPUT_ALIASES, build_inputs  # noqa: F401
