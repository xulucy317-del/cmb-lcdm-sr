"""Blind-SR input construction and explicit GMM-MI/MSE loss dispatch.

Inner loss
----------
``JULIA_LOSS_GMM_MI`` is the custom ``loss_function`` handed to PySR: a
pure-Julia 2-D GMM-MI estimator (fixed K=2 Gaussian mixture, EM with up to 30
iterations + convergence check, regularised covariances). MI is a Monte-Carlo
average over the fit samples:

    MI ≈ (1/N) Σ_i [log p_xy(xi, yi) − log p_x(xi) − log p_y(yi)]

mapped to a positive loss via ``exp(−MI)`` (PySR's HallOfFame takes log(loss)
for relative-score reporting and fails on non-positive losses). Batches are
strided-subsampled to N_INNER=300 and standardised per axis before EM.

Being a real MI estimator, the loss is invariant under any bijection of either
variable — the search is rewarded for functional dependence only, never for
matching the encoder's calibration. It shares this invariance class with the
post-hoc selection metric (``mi.mutual_information_gmm``).

``JULIA_LOSS_MSE`` is the elementwise squared-error objective used by the
one-stage latent-reconstruction experiment.  It is intentionally
calibration-sensitive and is passed through PySR's ``elementwise_loss``
keyword, never through the custom batch-loss path above.

"""
from __future__ import annotations

import numpy as np

# --- SR input columns ---------------------------------------------------------
#
# theta.npy column order is fixed by the dataset:
#   [omega_b, omega_cdm, H0, tau_reio, ln10^{10}A_s, n_s]
# The blind protocol feeds PySR *raw* parameters only 

THETA_COLS = ["omega_b", "omega_cdm", "H0", "tau_reio", "ln10As", "n_s"]
INPUT_ALIASES = {
    "omega_b":   ("omega_b",   lambda t: t[:, 0]),
    "omega_cdm": ("omega_cdm", lambda t: t[:, 1]),
    "H0":        ("H0",        lambda t: t[:, 2]),
    "tau":       ("tau",       lambda t: t[:, 3]),
    "tau_reio":  ("tau",       lambda t: t[:, 3]),
    "ln10As":    ("ln10As",    lambda t: t[:, 4]),
    "n_s":       ("n_s",       lambda t: t[:, 5]),
    "A_s":       ("A_s",       lambda t: np.exp(t[:, 4]) * 1e-10),
    # Order-one physical-unit aliases. Distinct emitted labels keep stored
    # expressions unambiguous in downstream physical-coordinate evaluation.
    "wb100":      ("wb100",      lambda t: 100.0 * t[:, 0]),
    "wc10":       ("wc10",       lambda t: 10.0 * t[:, 1]),
    "h":          ("h",          lambda t: t[:, 2] / 100.0),
    "A9":         ("A9",         lambda t: np.exp(t[:, 4]) / 10.0),
}


# Named sensitivity arms bind the coordinate system to numeric precision, so
# an arm called ``raw64`` cannot silently inherit PySR's Float32 default.
_FLOAT64_PYSR_KWARGS = {"precision": 64, "print_precision": 17}
INPUT_CONFIGS = {
    "raw64": {
        "inputs": ("omega_b", "omega_cdm", "H0", "tau", "A_s", "n_s"),
        "sampled_expressions": {
            "omega_b": "omega_b", "omega_cdm": "omega_cdm", "H0": "H0",
            "tau": "tau", "A_s": "exp(ln10As)*1e-10", "n_s": "n_s",
        },
        "pysr_kwargs": dict(_FLOAT64_PYSR_KWARGS),
    },
    "physical_o1_64": {
        "inputs": ("wb100", "wc10", "h", "tau", "A9", "n_s"),
        "sampled_expressions": {
            "wb100": "100*omega_b", "wc10": "10*omega_cdm",
            "h": "H0/100", "tau": "tau", "A9": "exp(ln10As)/10",
            "n_s": "n_s",
        },
        "pysr_kwargs": dict(_FLOAT64_PYSR_KWARGS),
    },
    "logamp64": {
        "inputs": ("omega_b", "omega_cdm", "H0", "tau", "ln10As", "n_s"),
        "sampled_expressions": {
            "omega_b": "omega_b", "omega_cdm": "omega_cdm", "H0": "H0",
            "tau": "tau", "ln10As": "ln10As", "n_s": "n_s",
        },
        "pysr_kwargs": dict(_FLOAT64_PYSR_KWARGS),
    },
}


def resolve_input_config(name: str) -> dict:
    """Return a defensive copy of one named SR input/precision profile."""
    try:
        config = INPUT_CONFIGS[name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown input config '{name}'. Choices: {list(INPUT_CONFIGS)}"
        ) from exc
    return {
        "inputs": list(config["inputs"]),
        "sampled_expressions": dict(config["sampled_expressions"]),
        "pysr_kwargs": dict(config["pysr_kwargs"]),
    }


def build_inputs(theta: np.ndarray, names: list[str]) -> tuple[np.ndarray, list[str]]:
    """Assemble the (N, k) SR input matrix from theta columns by alias name."""
    cols, labels = [], []
    for nm in names:
        if nm not in INPUT_ALIASES:
            raise ValueError(f"Unknown input name '{nm}'. Choices: {list(INPUT_ALIASES)}")
        label, getter = INPUT_ALIASES[nm]
        cols.append(getter(theta))
        labels.append(label)
    return np.column_stack(cols), labels


# --- Julia loss_function ------------------------------------------------------
#
# Signature: (tree, dataset, options) → loss::L. Higher loss = worse; PySR minimises. 

JULIA_LOSS_GMM_MI = r"""
function _log_gauss2d(x::L, y::L, mux::L, muy::L, sxx::L, sxy::L, syy::L) where L
    # 2-D log Gaussian density. Σ = [[sxx, sxy], [sxy, syy]].
    det_s = sxx * syy - sxy * sxy
    if det_s < L(1e-30) || !isfinite(det_s)
        return L(-Inf)
    end
    inv_det = L(1) / det_s
    a = syy * inv_det
    b = -sxy * inv_det
    c = sxx * inv_det
    dx = x - mux
    dy = y - muy
    quad = a * dx * dx + L(2) * b * dx * dy + c * dy * dy
    return -L(1.8378770664093453) - L(0.5) * log(det_s) - L(0.5) * quad
end
function _log_gauss1d(x::L, mu::L, var::L) where L
    if var < L(1e-30) || !isfinite(var)
        return L(-Inf)
    end
    dx = x - mu
    return -L(0.5) * (log(L(2.0 * 3.141592653589793) * var) + dx * dx / var)
end
function _logsumexp2(a::L, b::L) where L
    m = max(a, b)
    if !isfinite(m)
        return m
    end
    return m + log(exp(a - m) + exp(b - m))
end
function _gmm_mi_2d(xs::Vector{L}, ys::Vector{L}) where L
    n = length(xs)
    if n < 16
        return L(NaN)
    end
    # Initialise K=2 GMM: split by xs median.
    sorted_idx = sortperm(xs)
    mid = div(n, 2)
    w1 = L(0.5); w2 = L(0.5)
    mux1 = zero(L); muy1 = zero(L); mux2 = zero(L); muy2 = zero(L)
    sxx1 = L(1); sxy1 = zero(L); syy1 = L(1)
    sxx2 = L(1); sxy2 = zero(L); syy2 = L(1)
    @inbounds for q in 1:mid
        i = sorted_idx[q]; mux1 += xs[i]; muy1 += ys[i]
    end
    @inbounds for q in (mid + 1):n
        i = sorted_idx[q]; mux2 += xs[i]; muy2 += ys[i]
    end
    mux1 /= L(mid); muy1 /= L(mid)
    mux2 /= L(n - mid); muy2 /= L(n - mid)
    reg = L(1e-6)
    prev_ll = L(-Inf)
    log_w1 = log(w1); log_w2 = log(w2)
    for iter in 1:30
        # E-step: γ_i1, γ_i2.
        ll = zero(L)
        s_g1 = zero(L); s_g2 = zero(L)
        m1x = zero(L); m1y = zero(L); m2x = zero(L); m2y = zero(L)
        c1xx = zero(L); c1xy = zero(L); c1yy = zero(L)
        c2xx = zero(L); c2xy = zero(L); c2yy = zero(L)
        ok = true
        @inbounds for i in 1:n
            lp1 = log_w1 + _log_gauss2d(xs[i], ys[i], mux1, muy1, sxx1, sxy1, syy1)
            lp2 = log_w2 + _log_gauss2d(xs[i], ys[i], mux2, muy2, sxx2, sxy2, syy2)
            lse = _logsumexp2(lp1, lp2)
            if !isfinite(lse); ok = false; break; end
            g1 = exp(lp1 - lse)
            g2 = L(1) - g1
            ll += lse
            s_g1 += g1; s_g2 += g2
            m1x += g1 * xs[i]; m1y += g1 * ys[i]
            m2x += g2 * xs[i]; m2y += g2 * ys[i]
        end
        if !ok; return L(NaN); end
        if s_g1 < L(1e-12) || s_g2 < L(1e-12); return L(NaN); end
        m1x /= s_g1; m1y /= s_g1
        m2x /= s_g2; m2y /= s_g2
        @inbounds for i in 1:n
            lp1 = log_w1 + _log_gauss2d(xs[i], ys[i], mux1, muy1, sxx1, sxy1, syy1)
            lp2 = log_w2 + _log_gauss2d(xs[i], ys[i], mux2, muy2, sxx2, sxy2, syy2)
            lse = _logsumexp2(lp1, lp2)
            g1 = exp(lp1 - lse); g2 = L(1) - g1
            dx1 = xs[i] - m1x; dy1 = ys[i] - m1y
            dx2 = xs[i] - m2x; dy2 = ys[i] - m2y
            c1xx += g1 * dx1 * dx1; c1xy += g1 * dx1 * dy1; c1yy += g1 * dy1 * dy1
            c2xx += g2 * dx2 * dx2; c2xy += g2 * dx2 * dy2; c2yy += g2 * dy2 * dy2
        end
        c1xx = c1xx / s_g1 + reg; c1xy /= s_g1; c1yy = c1yy / s_g1 + reg
        c2xx = c2xx / s_g2 + reg; c2xy /= s_g2; c2yy = c2yy / s_g2 + reg
        w1 = s_g1 / L(n); w2 = L(1) - w1
        mux1 = m1x; muy1 = m1y; sxx1 = c1xx; sxy1 = c1xy; syy1 = c1yy
        mux2 = m2x; muy2 = m2y; sxx2 = c2xx; sxy2 = c2xy; syy2 = c2yy
        log_w1 = log(max(w1, L(1e-30)))
        log_w2 = log(max(w2, L(1e-30)))
        if iter > 4 && abs(ll - prev_ll) < L(1e-4) * abs(prev_ll); break; end
        prev_ll = ll
    end
    # MI = (1/N) Σ [log p_xy − log p_x − log p_y].
    mi = zero(L)
    @inbounds for i in 1:n
        lp1_xy = log_w1 + _log_gauss2d(xs[i], ys[i], mux1, muy1, sxx1, sxy1, syy1)
        lp2_xy = log_w2 + _log_gauss2d(xs[i], ys[i], mux2, muy2, sxx2, sxy2, syy2)
        lp_xy = _logsumexp2(lp1_xy, lp2_xy)
        lp1_x = log_w1 + _log_gauss1d(xs[i], mux1, sxx1)
        lp2_x = log_w2 + _log_gauss1d(xs[i], mux2, sxx2)
        lp_x = _logsumexp2(lp1_x, lp2_x)
        lp1_y = log_w1 + _log_gauss1d(ys[i], muy1, syy1)
        lp2_y = log_w2 + _log_gauss1d(ys[i], muy2, syy2)
        lp_y = _logsumexp2(lp1_y, lp2_y)
        mi += lp_xy - lp_x - lp_y
    end
    mi /= L(n)
    return mi
end
function eval_loss(tree, dataset::Dataset{T,L}, options) where {T,L}
    prediction, flag = eval_tree_array(tree, dataset.X, options)
    if !flag
        return L(Inf)
    end
    n = length(prediction)
    N_INNER = 300
    step = max(1, div(n, N_INNER))
    m = 0
    p_sub = L[]
    y_sub = L[]
    i = 1
    while i <= n && m < N_INNER
        push!(p_sub, L(prediction[i]))
        push!(y_sub, L(dataset.y[i]))
        m += 1
        i += step
    end
    if m < 16
        return L(Inf)
    end
    # Standardise both axes (helps EM initialisation).
    sx = zero(L); sy = zero(L)
    @inbounds for j in 1:m; sx += p_sub[j]; sy += y_sub[j]; end
    mx = sx / L(m); my = sy / L(m)
    vx = zero(L); vy = zero(L)
    @inbounds for j in 1:m
        vx += (p_sub[j] - mx)^2; vy += (y_sub[j] - my)^2
    end
    vx = sqrt(vx / L(m)); vy = sqrt(vy / L(m))
    if vx < L(1e-30) || vy < L(1e-30); return L(1.0); end
    @inbounds for j in 1:m
        p_sub[j] = (p_sub[j] - mx) / vx
        y_sub[j] = (y_sub[j] - my) / vy
    end
    mi = _gmm_mi_2d(p_sub, y_sub)
    if !isfinite(mi); return L(Inf); end
    return exp(-max(mi, L(0)))
end
"""

INNER_LOSS_NAME = "gmm_mi"
LOSS_KIND_LABEL = "batch_exp_neg_gmm_mi_pure_julia"

# PySR's elementwise loss syntax is Julia source.  Keep it explicit rather
# than relying on the library default so reports completely specify the
# reconstruction objective.
JULIA_LOSS_MSE = "loss(prediction, target) = (prediction - target)^2"
MSE_LOSS_NAME = "mse"
MSE_LOSS_KIND_LABEL = "elementwise_squared_error"

LOSS_SPECS = {
    INNER_LOSS_NAME: {
        "name": INNER_LOSS_NAME,
        "kind_label": LOSS_KIND_LABEL,
        "pysr_kwarg": "loss_function",
        "source": JULIA_LOSS_GMM_MI,
        "default_selection": "mi",
        "plot_label": "exp(-GMM-MI)",
    },
    MSE_LOSS_NAME: {
        "name": MSE_LOSS_NAME,
        "kind_label": MSE_LOSS_KIND_LABEL,
        "pysr_kwarg": "elementwise_loss",
        "source": JULIA_LOSS_MSE,
        "default_selection": "mse",
        "plot_label": "squared error",
    },
}

SELECTION_DIRECTIONS = {"mi": "max", "mse": "min"}
POSTHOC_MI_MODES = {"auto", "full", "none"}


def resolve_loss(inner_loss: str = INNER_LOSS_NAME,
                 selection_metric: str = "auto") -> tuple[dict, str]:
    """Return the frozen loss spec and resolved validation selector.

    ``auto`` preserves the original GMM-MI/MI pipeline and maps the new MSE
    objective to validation MSE.  Explicit cross-objective selectors remain
    available for the selector-controlled ablations in the experiment plan.
    """
    if inner_loss not in LOSS_SPECS:
        raise ValueError(
            f"Unknown inner loss '{inner_loss}'. Choices: {sorted(LOSS_SPECS)}"
        )
    if selection_metric == "auto":
        selection_metric = LOSS_SPECS[inner_loss]["default_selection"]
    if selection_metric not in SELECTION_DIRECTIONS:
        raise ValueError(
            "Unknown selection metric "
            f"'{selection_metric}'. Choices: auto, {sorted(SELECTION_DIRECTIONS)}"
        )
    return dict(LOSS_SPECS[inner_loss]), selection_metric


def pysr_loss_kwargs(inner_loss: str = INNER_LOSS_NAME) -> dict[str, str]:
    """The mutually-exclusive PySR keyword for one registered inner loss."""
    spec, _ = resolve_loss(inner_loss)
    return {spec["pysr_kwarg"]: spec["source"]}


def resolve_posthoc_mi(mode: str, selection_metric: str) -> str:
    """Resolve optional full GMM-MI front diagnostics.

    MI-selected fronts must compute MI. MSE-selected fronts skip the costly
    full GMM-MI estimator by default because it cannot affect their ranking;
    callers may still request it explicitly for a diagnostic run.
    """
    if mode not in POSTHOC_MI_MODES:
        raise ValueError(
            f"Unknown post-hoc MI mode '{mode}'. Choices: "
            f"{sorted(POSTHOC_MI_MODES)}"
        )
    if mode == "auto":
        resolved = "full" if selection_metric == "mi" else "none"
    else:
        resolved = mode
    if selection_metric == "mi" and resolved != "full":
        raise ValueError(
            "post-hoc MI cannot be disabled when selection_metric='mi'"
        )
    return resolved


def rank_front(rows: list[dict], selection_metric: str) -> list[dict]:
    """Rank valid front rows with deterministic parsimony tie-breaking.

    MI is maximised and MSE minimised.  Rows without a finite requested metric
    are omitted.  Exact metric ties prefer lower complexity, then lower
    equation index.
    """
    if selection_metric not in SELECTION_DIRECTIONS:
        raise ValueError(
            f"Unknown selection metric '{selection_metric}': "
            f"{sorted(SELECTION_DIRECTIONS)}"
        )
    metric_key = f"{selection_metric}_val"
    valid = []
    for row in rows:
        value = row.get(metric_key)
        if value is None or not np.isfinite(value):
            continue
        valid.append(row)

    def key(row):
        value = float(row[metric_key])
        primary = value if selection_metric == "mse" else -value
        return (primary, int(row.get("complexity", 10**9)),
                int(row.get("index", 10**9)))

    return sorted(valid, key=key)
