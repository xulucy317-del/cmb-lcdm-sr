"""Answer-agnostic analysis of discovered symbolic forms.

Phase-0 infrastructure of ``docs/discovery_roadmap.md`` (M3), shared by the
Phase 1–4 consolidators. Everything here treats a Pareto-front expression as
a *function on the prior box* — never as a string — because the GMM-MI loss
identifies forms only up to a bijection of the output:

* **Evaluation with masking** — sympy → numpy lambdification in the sampled
  basis (``tiers.THETA_ORDER``; any ``A_s`` occurrence is rewritten to
  ``exp(ln10As)·1e-10`` first), with non-finite/complex results masked to
  NaN and the finite fraction reported instead of raised.
* **Gradients in u-coordinates** — ∂f/∂u_j on the prior box
  (u_j = (θ_j − mid_j)/half_j), the common scale on which sensitivity
  signatures are comparable across parameters.
* **Equivalence tests + clustering** — two forms are the *same semantic
  coordinate* if any of: identical canonical sympy; |Spearman ρ| ≥ 0.98 on
  the fixed anchor set (a continuous bijection on an interval is monotone,
  so rank agreement is exactly MI-equivalence on the observed domain);
  gradient-cosine distance ≤ 0.05. Union-find clustering over pairs.
* **Sensitivity signature + constant-ratio pairs** — normalised mean
  |∂f/∂u_j|, and the answer-agnostic generalisation of the study's r-ratio:
  for every variable pair the ratio field (∂f/∂u_i)/(∂f/∂u_j); where its
  spread is small the form depends on (i, j) only through a fixed linear
  combination, whose raw-coordinate slope is reported. The textbook −2 must
  *emerge* here (pair tau/ln10As with r_raw ≈ −2), never be asked for.
* **Sobol indices** — first-order and total (Jansen estimators, scrambled
  Sobol QMC) on the prior box.

Thresholds are frozen in the roadmap §0.3; keyword defaults here mirror them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence

import numpy as np
import sympy

from .tiers import SAMPLED_LABELS

# --- symbols -----------------------------------------------------------------

SAMPLED_SYMBOLS = tuple(sympy.Symbol(name) for name in SAMPLED_LABELS)
A_S = sympy.Symbol("A_s")
_LN10AS = SAMPLED_SYMBOLS[SAMPLED_LABELS.index("ln10As")]
_A_S_REWRITE = {A_S: sympy.exp(_LN10AS) * sympy.Float(1e-10)}
KNOWN_SYMBOLS = set(SAMPLED_SYMBOLS) | {A_S}

_PARSE_LOCALS = {s.name: s for s in SAMPLED_SYMBOLS}
_PARSE_LOCALS["A_s"] = A_S
# PySR raw-expression operator spellings not native to sympy.
_PARSE_LOCALS["square"] = lambda x: x**2
_PARSE_LOCALS["neg"] = lambda x: -x


# --- extra input columns (post-closure interaction-aware experiments) --------

@dataclass
class ExtraInput:
    """One SR input symbol beyond the six sampled parameters.

    ``values_fn(theta) -> (n,)`` evaluates the column on sampled-basis rows
    (composite through whatever deterministic θ-function defines it);
    ``grads_fn(theta) -> (n, 6)`` its u-gradient via the chain rule, or None
    when unavailable — gradients of expressions using the symbol are then
    NaN and the gradient-based instruments abstain.
    """
    name: str
    symbol: sympy.Symbol
    values_fn: Callable
    grads_fn: Optional[Callable] = None


#: name -> ExtraInput. Empty by default, so every frozen Phase 1–8 code path
#: is bit-identical. The interaction-aware stage-2 consolidator registers
#: ``f1hat`` (the stage-1 prediction h(f1) as a θ-function) per latent.
EXTRA_INPUTS: dict[str, ExtraInput] = {}


def register_extra_input(name: str, values_fn: Callable,
                         grads_fn: Optional[Callable] = None) -> None:
    EXTRA_INPUTS[name] = ExtraInput(name, sympy.Symbol(name), values_fn, grads_fn)


def clear_extra_inputs() -> None:
    EXTRA_INPUTS.clear()


def _extras_in(expr: sympy.Expr) -> list[ExtraInput]:
    free = expr.free_symbols
    return [e for e in EXTRA_INPUTS.values() if e.symbol in free]


def parse_expr(expr_str: str) -> Optional[sympy.Expr]:
    """Parse an SR expression string; None if unparseable or has unknown symbols."""
    locals_ = dict(_PARSE_LOCALS)
    known = set(KNOWN_SYMBOLS)
    for e in EXTRA_INPUTS.values():
        locals_[e.name] = e.symbol
        known.add(e.symbol)
    try:
        expr = sympy.sympify(expr_str, locals=locals_)
    except Exception:
        return None
    if not isinstance(expr, sympy.Expr):
        return None
    if not expr.free_symbols <= known:
        return None
    return expr


def canonical_form(expr: sympy.Expr | str) -> str:
    """Canonical sympy string (same reduction as scripts/pool_sr_runs.py)."""
    if isinstance(expr, str):
        parsed = parse_expr(expr)
        if parsed is None:
            return expr.strip()
        expr = parsed
    try:
        return str(sympy.simplify(expr))
    except Exception:
        return str(expr)


# --- evaluation with masking -------------------------------------------------

def _sampledify(expr: sympy.Expr) -> sympy.Expr:
    """Rewrite to the sampled basis (A_s → exp(ln10As)·1e-10)."""
    return expr.xreplace(_A_S_REWRITE)


def _eval_sampled(expr: sympy.Expr, theta: np.ndarray) -> np.ndarray:
    """Evaluate a sampled-basis expression on (n, 6) theta rows → (n,) with NaN."""
    n = theta.shape[0]
    extras = _extras_in(expr)
    syms = SAMPLED_SYMBOLS + tuple(e.symbol for e in extras)
    try:
        fn = sympy.lambdify(syms, expr, modules=["numpy"])
    except Exception:
        return np.full(n, np.nan)
    cols = [theta[:, j] for j in range(6)]
    for e in extras:
        try:
            with np.errstate(all="ignore"):
                cols.append(np.asarray(e.values_fn(theta), dtype=np.float64))
        except Exception:
            return np.full(n, np.nan)
    with np.errstate(all="ignore"):
        try:
            v = fn(*cols)
        except Exception:
            return np.full(n, np.nan)
    v = np.asarray(v)
    if v.dtype == object:
        try:
            v = v.astype(np.complex128)
        except Exception:
            return np.full(n, np.nan)
    if np.iscomplexobj(v):
        v = np.where(np.abs(v.imag) <= 1e-9 * (1.0 + np.abs(v.real)), v.real, np.nan)
    v = np.broadcast_to(np.asarray(v, dtype=np.float64), (n,)).copy()
    v[~np.isfinite(v)] = np.nan
    return v


def evaluate_on_theta(expr: sympy.Expr | str, theta: np.ndarray) -> np.ndarray:
    """f(θ) on sampled-basis rows, NaN where invalid. Accepts str or Expr."""
    if isinstance(expr, str):
        parsed = parse_expr(expr)
        if parsed is None:
            return np.full(theta.shape[0], np.nan)
        expr = parsed
    return _eval_sampled(_sampledify(expr), theta)


def gradients_on_theta(expr: sympy.Expr | str, theta: np.ndarray,
                       half: np.ndarray) -> np.ndarray:
    """(n, 6) array of ∂f/∂u_j on the rows; NaN where invalid.

    u_j = (θ_j − mid_j)/half_j in the sampled basis, so
    ∂f/∂u_j = half_j · ∂f/∂θ_j (the ln10As column absorbs the A_s chain rule
    through the rewrite).
    """
    if isinstance(expr, str):
        parsed = parse_expr(expr)
        if parsed is None:
            return np.full((theta.shape[0], 6), np.nan)
        expr = parsed
    sampled = _sampledify(expr)
    n = theta.shape[0]
    out = np.full((n, 6), np.nan)
    extras = _extras_in(sampled)
    if any(e.grads_fn is None for e in extras):
        return out  # no chain rule available for an extra input → abstain
    chain = np.zeros((n, 6))
    ok = np.ones(n, dtype=bool)
    for e in extras:
        try:
            de = sympy.diff(sampled, e.symbol)
        except Exception:
            return out
        dv = _eval_sampled(de, theta)                       # ∂f/∂e on the rows
        with np.errstate(all="ignore"):
            eg = np.asarray(e.grads_fn(theta), dtype=np.float64)  # (n, 6), u-units
        ok &= np.isfinite(dv) & np.isfinite(eg).all(axis=1)
        with np.errstate(all="ignore"):
            term = dv[:, None] * eg
        chain += np.where(np.isfinite(term), term, 0.0)
    for j, sym in enumerate(SAMPLED_SYMBOLS):
        try:
            d = sympy.diff(sampled, sym)
        except Exception:
            continue
        col = _eval_sampled(d, theta) * float(half[j]) + chain[:, j]
        col[~ok] = np.nan
        out[:, j] = col
    return out


# --- per-form container ------------------------------------------------------

@dataclass
class FormEval:
    """One expression evaluated on the anchor set."""
    expr_str: str
    expr: sympy.Expr
    canonical: str
    values: np.ndarray                       # (n_anchors,) NaN-masked
    grads_u: np.ndarray                      # (n_anchors, 6) NaN-masked
    complexity: Optional[int] = None
    meta: dict = field(default_factory=dict)  # seed, mi_val, ... (caller-owned)

    @property
    def finite_frac(self) -> float:
        return float(np.isfinite(self.values).mean())

    @property
    def support(self) -> list[str]:
        """Sampled-basis labels (+ registered extra inputs) the form depends on."""
        syms = _sampledify(self.expr).free_symbols
        sup = [lab for lab, s in zip(SAMPLED_LABELS, SAMPLED_SYMBOLS) if s in syms]
        sup += [e.name for e in EXTRA_INPUTS.values() if e.symbol in syms]
        return sup


def evaluate_form(expr_str: str, theta_anchors: np.ndarray, half: np.ndarray,
                  complexity: Optional[int] = None,
                  meta: Optional[dict] = None) -> Optional[FormEval]:
    """Parse + evaluate one expression on the anchors; None if unparseable."""
    expr = parse_expr(expr_str)
    if expr is None:
        return None
    return FormEval(
        expr_str=expr_str, expr=expr, canonical=canonical_form(expr),
        values=evaluate_on_theta(expr, theta_anchors),
        grads_u=gradients_on_theta(expr, theta_anchors, half),
        complexity=complexity, meta=dict(meta or {}),
    )


# --- equivalence tests + clustering ------------------------------------------

def spearman_abs(x: np.ndarray, y: np.ndarray,
                 min_overlap: float = 0.5) -> Optional[float]:
    """|Spearman ρ| on jointly finite entries; None if overlap is too thin."""
    from scipy.stats import spearmanr

    m = np.isfinite(x) & np.isfinite(y)
    if m.mean() < min_overlap or m.sum() < 32:
        return None
    rho = spearmanr(x[m], y[m]).statistic
    return abs(float(rho)) if np.isfinite(rho) else None


def gradient_distance(g1: np.ndarray, g2: np.ndarray,
                      min_overlap: float = 0.5) -> Optional[float]:
    """d_∇ = 1 − mean |cos(∇f, ∇g)| over rows where both gradients are usable."""
    finite = np.isfinite(g1).all(axis=1) & np.isfinite(g2).all(axis=1)
    n1 = np.linalg.norm(np.where(np.isfinite(g1), g1, 0.0), axis=1)
    n2 = np.linalg.norm(np.where(np.isfinite(g2), g2, 0.0), axis=1)
    m = finite & (n1 > 1e-12) & (n2 > 1e-12)
    if m.mean() < min_overlap or m.sum() < 32:
        return None
    cos = np.abs(np.sum(g1[m] * g2[m], axis=1)) / (n1[m] * n2[m])
    return float(1.0 - cos.mean())


def same_cluster(f1: FormEval, f2: FormEval, rho_min: float = 0.98,
                 grad_max: float = 0.05, min_overlap: float = 0.5) -> bool:
    """Frozen equivalence rule (roadmap §0.3): any one test suffices."""
    if f1.canonical == f2.canonical:
        return True
    rho = spearman_abs(f1.values, f2.values, min_overlap=min_overlap)
    if rho is not None and rho >= rho_min:
        return True
    d = gradient_distance(f1.grads_u, f2.grads_u, min_overlap=min_overlap)
    return d is not None and d <= grad_max


def cluster_forms(forms: Sequence[FormEval], rho_min: float = 0.98,
                  grad_max: float = 0.05, min_overlap: float = 0.5) -> list[int]:
    """Union-find cluster labels (0-based, order of first appearance)."""
    parent = list(range(len(forms)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(forms)):
        for j in range(i + 1, len(forms)):
            ri, rj = find(i), find(j)
            if ri == rj:
                continue
            if same_cluster(forms[i], forms[j], rho_min=rho_min,
                            grad_max=grad_max, min_overlap=min_overlap):
                parent[max(ri, rj)] = min(ri, rj)

    labels, remap = [], {}
    for i in range(len(forms)):
        r = find(i)
        if r not in remap:
            remap[r] = len(remap)
        labels.append(remap[r])
    return labels


# --- sensitivity signature + constant-ratio pairs ----------------------------

def sensitivity_signature(grads_u: np.ndarray) -> np.ndarray:
    """g_j = mean|∂f/∂u_j| / Σ_i mean|∂f/∂u_i| (NaN-safe; zeros if degenerate)."""
    with np.errstate(all="ignore"):
        mean_abs = np.nanmean(np.abs(grads_u), axis=0)
    mean_abs = np.where(np.isfinite(mean_abs), mean_abs, 0.0)
    total = mean_abs.sum()
    return mean_abs / total if total > 0 else np.zeros(6)


def constant_ratio_pairs(grads_u: np.ndarray, half: np.ndarray,
                         cv_max: float = 0.05, min_share: float = 0.01,
                         min_frac: float = 0.8, trim: float = 0.05) -> list[dict]:
    """Variable pairs on which the form is a fixed linear combination.

    For every pair (i, j) with both sensitivity shares ≥ min_share, the ratio
    field ρ_ij = (∂f/∂u_i)/(∂f/∂u_j) over the anchors, trimmed of its `trim`
    tails. A pair qualifies when the ratio is defined on ≥ min_frac of the
    anchors and its coefficient of variation is ≤ cv_max; the raw-coordinate
    slope r_raw = (∂f/∂θ_i)/(∂f/∂θ_j) = ρ_ij · half_j/half_i is reported
    (pair (tau, ln10As): the textbook exponent, −2).
    """
    sig = sensitivity_signature(grads_u)
    out = []
    for i in range(6):
        for j in range(6):
            if i == j or sig[i] < min_share or sig[j] < min_share:
                continue
            if i > j:
                continue  # report each unordered pair once, as (i, j) with i < j
            gi, gj = grads_u[:, i], grads_u[:, j]
            valid = np.isfinite(gi) & np.isfinite(gj) & (np.abs(gj) > 1e-12)
            frac = float(valid.mean())
            if frac < min_frac or valid.sum() < 32:
                continue
            ratio = np.sort(gi[valid] / gj[valid])
            k = int(len(ratio) * trim)
            core = ratio[k:len(ratio) - k] if len(ratio) > 2 * k else ratio
            mean = float(core.mean())
            if abs(mean) < 1e-12:
                continue
            cv = float(core.std() / abs(mean))
            if cv > cv_max:
                continue
            out.append({
                "i": i, "j": j,
                "pair": (SAMPLED_LABELS[i], SAMPLED_LABELS[j]),
                "ratio_u": mean, "cv": cv, "frac_valid": frac,
                "r_raw": mean * float(half[j]) / float(half[i]),
            })
    return out


# --- Sobol indices (Jansen estimators, QMC) ----------------------------------

def sobol_indices(expr: sympy.Expr | str, mid: np.ndarray, half: np.ndarray,
                  n_base: int = 2048, seed: int = 0) -> dict:
    """First-order and total Sobol indices of f on the prior box.

    Scrambled Sobol QMC sample pair (A, B) of n_base points each; Jansen
    estimators:  S1_j = 1 − E[(f(B) − f(AB_j))²]/(2V),
                 ST_j = E[(f(A) − f(AB_j))²]/(2V),
    with AB_j = A with column j taken from B. Rows where any evaluation is
    non-finite are dropped from every estimator (n_effective reported).
    Valid because the LHS prior is an independent uniform box.
    """
    from scipy.stats import qmc

    if isinstance(expr, str):
        parsed = parse_expr(expr)
        if parsed is None:
            return {"S1": np.full(6, np.nan), "ST": np.full(6, np.nan),
                    "variance": np.nan, "n_effective": 0}
        expr = parsed
    sampled = _sampledify(expr)

    d = 6
    u = qmc.Sobol(d=2 * d, scramble=True, seed=seed).random(n_base)
    A = mid + (2.0 * u[:, :d] - 1.0) * half
    B = mid + (2.0 * u[:, d:] - 1.0) * half

    fA = _eval_sampled(sampled, A)
    fB = _eval_sampled(sampled, B)
    fAB = np.empty((n_base, d))
    for j in range(d):
        ABj = A.copy()
        ABj[:, j] = B[:, j]
        fAB[:, j] = _eval_sampled(sampled, ABj)

    ok = np.isfinite(fA) & np.isfinite(fB) & np.isfinite(fAB).all(axis=1)
    n_eff = int(ok.sum())
    if n_eff < 16:
        return {"S1": np.full(6, np.nan), "ST": np.full(6, np.nan),
                "variance": np.nan, "n_effective": n_eff}
    fA, fB, fAB = fA[ok], fB[ok], fAB[ok]
    var = float(np.concatenate([fA, fB]).var())
    if var <= 0:
        return {"S1": np.zeros(6), "ST": np.zeros(6),
                "variance": 0.0, "n_effective": n_eff}
    s1 = 1.0 - ((fB[:, None] - fAB) ** 2).mean(axis=0) / (2.0 * var)
    st = ((fA[:, None] - fAB) ** 2).mean(axis=0) / (2.0 * var)
    return {"S1": s1, "ST": st, "variance": var, "n_effective": n_eff}
