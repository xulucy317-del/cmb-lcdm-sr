"""The blind-SR core: input construction and the pure-Julia GMM-MI inner loss.

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
