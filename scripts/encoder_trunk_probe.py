#!/usr/bin/env python
"""Layer-wise linear probe of the encoder trunk, and encoder input optimisation.

The remaining two of the three LLM-interpretability transfers in §0.1 item 4 of
`docs/ols_mi_sr_mse_sr_t2_comparison_claude_output.md` (item 10 of §5.1 of
`docs/sr_objective_discussion_2026-09-02.md`); the first, gradient attribution,
is `scripts/encoder_gradient_attribution.py`.

**probe** — where does the degenerate amplitude combination first become
linearly decodable? The encoder trunk is three Conv1d→CPAct→BatchNorm blocks
then Flatten then one Linear head, so there are five natural read-off points:
the standardised input, the three block outputs, and mu itself. At each, a
ridge probe is fitted on held-out-split T1 rows and scored by out-of-sample
R^2, for three targets that answer the question together:

    ln10As - 2*tau   the degenerate combination the physics predicts
    ln10As, tau      its two constituents, separately

If the combination is decodable well before either constituent is, the network
has built the degenerate coordinate rather than the parameters — the same fact
the whole study circles, read off the representation instead of the outputs.
The four other sampled parameters are probed as controls.

Ridge is solved in the dual (Gram) form because the block-1 features are
wider than the sample (16 x 823 = 13168), with alpha chosen by 5-fold CV on
the training rows only.

**steer** — encoder input optimisation. Starting from an anchor spectrum,
find the input perturbation that moves one latent while holding the others,

    min_delta  -(mu_k - mu_k^0) + w_hold * sum_{j != k} (mu_j - mu_j^0)^2
               + w_norm * ||delta||^2

and compare the resulting spectral pattern against the true parameter response
templates t_j(ell) = d log10 D_ell / d u_j (`data/spectral_templates_v1.npz`).
Reported as cosines against every template. Note what this can and cannot do:
the (tau, lnA_s) templates are near-antiparallel, so the *decomposition* is as
ill-posed here as it was for the decoder in Phase 7b (gate G4b). The cosines
are reported as a pattern check, never as a coefficient split.

    python scripts/encoder_trunk_probe.py --run lcdm_tt_ee_lowl --mode probe

Writes experiments/encoder_trunk_probe_<run>.json (probe) and
experiments/encoder_input_optimisation_<run>.json (steer).

Post-hoc and descriptive; no gate, no frozen threshold.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")

import _bootstrap  # noqa: F401,E402

import numpy as np  # noqa: E402
import torch  # noqa: E402
import torch.nn as nn  # noqa: E402

from cmb_lcdm_sr import tiers  # noqa: E402
from cmb_lcdm_sr.dataset import ShardedSpectraDataset  # noqa: E402
from cmb_lcdm_sr.encoder import load_checkpoint, resolve_shard_dirs  # noqa: E402
from cmb_lcdm_sr.scaler import ShardedScaler  # noqa: E402

RUNS = ("lcdm_tt_beta3e-4", "lcdm_tt_ee_lowl")
SEED = 20260903
SAMPLED = ("omega_b", "omega_cdm", "H0", "tau", "ln10As", "n_s")
ALPHAS = (1e-2, 1e-1, 1.0, 1e1, 1e2, 1e3, 1e4, 1e5)


def load_run(run: str, models_root: str, shards_root: str | None):
    run_dir = Path(models_root) / run
    with open(run_dir / "config_used.json") as f:
        data_cfg = json.load(f)["data"]
    scaler = ShardedScaler.load(run_dir / "scaler.npz")
    dirs = resolve_shard_dirs(run_dir, shards_root=shards_root)
    refs = {ch: scaler.refs[ch].astype(np.float32) for ch in scaler.channels}
    lengths = {ch: refs[ch].shape[0] for ch in scaler.channels}
    dict_mode = (len(set(lengths.values())) > 1
                 or bool(data_cfg.get("force_dict_mode", False)))
    ds = ShardedSpectraDataset(
        shard_dirs={ch: str(dirs[ch]) for ch in scaler.channels},
        refs=refs, indices=np.where(np.load("data/splits_v1.npz")["split_id"] == 2)[0],
        expected_n=int(data_cfg.get("expected_n", 500_000)),
        n_shards=int(data_cfg.get("n_shards", 100)), return_dict=dict_mode)
    model, _ = load_checkpoint(run_dir / "best_model.pt", device="cpu")
    return model, scaler, ds, dict_mode


def normalise(raw, scaler, dict_mode: bool):
    """Replicate NormWrapper on a list of dataset items."""
    stats = {ch: scaler.channel_stats(ch) for ch in scaler.channels}
    if dict_mode:
        return {ch: ((torch.stack([r[ch] for r in raw])
                      - torch.tensor(stats[ch][0], dtype=torch.float32))
                     / torch.tensor(stats[ch][1], dtype=torch.float32))
                for ch in scaler.channels}
    mu_s = torch.tensor(np.stack([stats[ch][0] for ch in scaler.channels]),
                        dtype=torch.float32)
    sd_s = torch.tensor(np.stack([stats[ch][1] for ch in scaler.channels]),
                        dtype=torch.float32)
    return (torch.stack(raw) - mu_s) / sd_s


def trunk_activations(model, x, dict_mode: bool) -> dict[str, np.ndarray]:
    """Flattened features at the input, each of the 3 conv blocks, and mu."""
    stacks = (model.encoders if dict_mode
              else {"tt": model.encoder})
    out: dict[str, list[np.ndarray]] = {f"block{i}": [] for i in (1, 2, 3)}
    with torch.no_grad():
        for ch, stack in stacks.items():
            h = x[ch].unsqueeze(1) if dict_mode else x
            block = 0
            for layer in stack:
                h = layer(h)
                if isinstance(layer, nn.BatchNorm1d):
                    block += 1
                    out[f"block{block}"].append(
                        h.reshape(h.shape[0], -1).numpy())
        mu, _ = model.encode(x)
    feats = {"input": (np.concatenate(
        [x[ch].numpy() for ch in x] if dict_mode
        else [x.reshape(x.shape[0], -1).numpy()], axis=1))}
    for i in (1, 2, 3):
        feats[f"block{i}"] = np.concatenate(out[f"block{i}"], axis=1)
    feats["mu"] = mu.numpy()
    return feats


def gram(F: np.ndarray, n_train: int) -> np.ndarray:
    """Gram matrix of train-standardised features — computed once per layer."""
    F = F.astype(np.float64)
    F = (F - F[:n_train].mean(0)) / (F[:n_train].std(0) + 1e-12)
    return F @ F.T


def dual_ridge_r2(K: np.ndarray, y: np.ndarray, n_train: int,
                  rng: np.random.Generator) -> tuple[float, float]:
    """Held-out R^2 of a ridge probe, alpha by 5-fold CV on the train rows."""
    y = (y - y[:n_train].mean()) / (y[:n_train].std() + 1e-12)
    tr, te = slice(0, n_train), slice(n_train, len(y))

    folds = np.array_split(rng.permutation(n_train), 5)
    best, best_a = -np.inf, ALPHAS[0]
    for a in ALPHAS:
        errs = []
        for f in folds:
            m = np.ones(n_train, bool)
            m[f] = False
            Ktt = K[:n_train, :n_train][np.ix_(m, m)]
            coef = np.linalg.solve(Ktt + a * np.eye(m.sum()), y[:n_train][m])
            pred = K[:n_train, :n_train][np.ix_(~m, m)] @ coef
            errs.append(((pred - y[:n_train][~m]) ** 2).mean())
        score = -float(np.mean(errs))
        if score > best:
            best, best_a = score, a
    coef = np.linalg.solve(K[tr, tr] + best_a * np.eye(n_train), y[tr])
    pred = K[te, tr] @ coef
    ss = ((y[te] - pred) ** 2).sum() / ((y[te] - y[te].mean()) ** 2).sum()
    return float(1.0 - ss), float(best_a)


def run_probe(args) -> None:
    theta = np.load(Path(args.dataset_dir) / "theta.npy")
    sid = np.load(Path(args.dataset_dir) / "splits_v1.npz")["split_id"]
    th = theta[sid == 2]
    rng = np.random.default_rng(SEED)
    rows = np.sort(rng.choice(np.arange(tiers.T1.start, tiers.T1.stop),
                              size=args.n_rows, replace=False))
    n_train = int(0.8 * args.n_rows)

    targets = {"ln10As_minus_2tau": th[rows, 4] - 2.0 * th[rows, 3]}
    for j, name in enumerate(SAMPLED):
        targets[name] = th[rows, j]

    for run in ([args.run] if args.run else list(RUNS)):
        model, scaler, ds, dict_mode = load_run(run, args.models_root,
                                                args.shards_root)
        feats: dict[str, list[np.ndarray]] = {}
        for start in range(0, args.n_rows, args.batch_size):
            batch = rows[start:start + args.batch_size]
            x = normalise([ds[int(r)] for r in batch], scaler, dict_mode)
            for name, arr in trunk_activations(model, x, dict_mode).items():
                feats.setdefault(name, []).append(arr)
            print(f"  [{run}] activations {min(start + args.batch_size, args.n_rows)}"
                  f"/{args.n_rows}")
        feats = {k: np.concatenate(v) for k, v in feats.items()}

        record = {
            "kind": "encoder_trunk_probe", "version": 1,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "run": run, "n_rows": args.n_rows, "n_train": n_train,
            "tier": "T1", "seed": SEED,
            "probe": "dual ridge, features standardised on train rows, "
                     "alpha by 5-fold CV on train, held-out R^2",
            "feature_dims": {k: int(v.shape[1]) for k, v in feats.items()},
            "r2": {}, "alpha": {},
        }
        order = ["input", "block1", "block2", "block3", "mu"]
        grams = {}
        for layer in order:
            grams[layer] = gram(feats[layer], n_train)
            print(f"  [{run}] gram {layer} "
                  f"(d={feats[layer].shape[1]})")
        print(f"\n### {run} — held-out linear-probe R^2 by trunk depth")
        print(f"  {'target':<20} " + "  ".join(f"{k:>8}" for k in order))
        for tname, y in targets.items():
            record["r2"][tname], record["alpha"][tname] = {}, {}
            cells = []
            for layer in order:
                r2, a = dual_ridge_r2(grams[layer], y.astype(np.float64),
                                      n_train, np.random.default_rng(SEED))
                record["r2"][tname][layer] = r2
                record["alpha"][tname][layer] = a
                cells.append(f"{r2:>8.4f}")
            print(f"  {tname:<20} " + "  ".join(cells))

        out = Path(args.out_dir) / f"encoder_trunk_probe_{run}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as f:
            json.dump(record, f, indent=1, sort_keys=True)
        print(f"  wrote {out}")


def _flat(d, channels, dict_mode):
    return (torch.cat([d[ch].reshape(d[ch].shape[0], -1) for ch in channels], 1)
            if dict_mode else d.reshape(d.shape[0], -1))


def run_steer(args) -> None:
    """Trust-region input optimisation: sweep the step budget and watch the
    steering direction leave the physical response manifold."""
    templates = np.load(Path(args.dataset_dir) / "spectral_templates_v1.npz")
    rng = np.random.default_rng(SEED)
    anchors = np.sort(rng.choice(np.arange(tiers.T1.start, tiers.T1.stop),
                                 size=args.n_anchors, replace=False))

    for run in ([args.run] if args.run else list(RUNS)):
        model, scaler, ds, dict_mode = load_run(run, args.models_root,
                                                args.shards_root)
        stats = {ch: scaler.channel_stats(ch) for ch in scaler.channels}
        chans = list(scaler.channels)
        n_lat = model.latent_dim

        # Step budgets in units of a real parameter move: eps_unit is the norm,
        # in the encoder's standardised input space, of one u-unit (one prior
        # half-width) along the amplitude template. So budget 1.0 is "as big a
        # perturbation as changing ln10As by half the prior range".
        unit = float(np.sqrt(sum(
            np.sum((templates[f"templates_{ch}"][4] / stats[ch][1]) ** 2)
            for ch in chans)))

        record = {
            "kind": "encoder_input_optimisation", "version": 2,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "run": run, "n_anchors": args.n_anchors, "steps": args.steps,
            "w_hold": args.w_hold, "seed": SEED,
            "budget_unit": unit,
            "budget_unit_meaning": "||d log10 D / d u_lnAs||, in standardised "
                                   "input units — one prior half-width of the "
                                   "amplitude parameter",
            "budgets": list(args.budgets),
            "note": "cosines are a pattern check, never a coefficient split: "
                    "the (tau, lnA_s) templates are near-antiparallel, so any "
                    "decomposition is as ill-posed here as it was for the "
                    "decoder in Phase 7b (gate G4b).",
            "latents": {},
        }
        x0 = normalise([ds[int(r)] for r in anchors], scaler, dict_mode)
        with torch.no_grad():
            mu0, _ = model.encode(x0)

        print(f"\n### {run} — trust-region encoder input optimisation")
        print(f"  budget unit ||t_lnAs/sigma|| = {unit:.1f} "
              f"(standardised input norm of a one-half-prior-width move)")
        for k in range(n_lat):
            record["latents"][f"z{k}"] = {"by_budget": {}}
            for b in args.budgets:
                eps = b * unit
                if dict_mode:
                    delta = {ch: torch.zeros_like(x0[ch], requires_grad=True)
                             for ch in chans}
                    params = list(delta.values())
                else:
                    delta = torch.zeros_like(x0, requires_grad=True)
                    params = [delta]
                opt = torch.optim.Adam(params, lr=args.lr * eps)
                for _ in range(args.steps):
                    opt.zero_grad()
                    xp = ({ch: x0[ch] + delta[ch] for ch in chans}
                          if dict_mode else x0 + delta)
                    mu, _ = model.encode(xp)
                    d = mu - mu0
                    hold = torch.cat([d[:, :k], d[:, k + 1:]], dim=1)
                    (-d[:, k].mean()
                     + args.w_hold * (hold ** 2).sum(1).mean()).backward()
                    opt.step()
                    with torch.no_grad():          # project onto ||delta|| <= eps
                        n = _flat(delta, chans, dict_mode).norm(dim=1)
                        scale = torch.clamp(eps / (n + 1e-12), max=1.0)
                        for pr in params:
                            pr.mul_(scale.reshape(-1, *([1] * (pr.ndim - 1))))

                with torch.no_grad():
                    xp = ({ch: x0[ch] + delta[ch] for ch in chans}
                          if dict_mode else x0 + delta)
                    mu, _ = model.encode(xp)
                    dm = (mu - mu0).numpy()
                cos = {}
                for ci, ch in enumerate(chans):
                    g = (delta[ch] if dict_mode else delta[:, ci]).detach().numpy()
                    phys = (g / stats[ch][1]).mean(axis=0)
                    T = templates[f"templates_{ch}"]
                    nrm = float(np.linalg.norm(phys))
                    cos[ch] = ({SAMPLED[j]: float(phys @ T[j]
                                / (nrm * np.linalg.norm(T[j])))
                                for j in range(len(SAMPLED))} if nrm > 0 else {})
                best = max(
                    ((ch, n, v) for ch, c in cos.items() for n, v in c.items()),
                    key=lambda t: abs(t[2]), default=("", "", 0.0))
                record["latents"][f"z{k}"]["by_budget"][f"{b:g}"] = {
                    "eps": eps,
                    "delta_mu_k": float(dm[:, k].mean()),
                    "delta_mu_others_rms": float(
                        np.sqrt((np.delete(dm, k, axis=1) ** 2).mean())),
                    "max_abs_cos": abs(float(best[2])),
                    "max_abs_cos_template": f"{best[0]}:{best[1]}",
                    "cosines": cos,
                }
            by = record["latents"][f"z{k}"]["by_budget"]
            print(f"  z{k}: " + "  ".join(
                f"b={b:g} dmu {by[f'{b:g}']['delta_mu_k']:+7.3f} "
                f"|cos|max {by[f'{b:g}']['max_abs_cos']:.3f}"
                for b in args.budgets))

        out = Path(args.out_dir) / f"encoder_input_optimisation_{run}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as f:
            json.dump(record, f, indent=1, sort_keys=True)
        print(f"  wrote {out}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=("probe", "steer"), default="probe")
    p.add_argument("--run", choices=RUNS, default=None)
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--models-root", default="models")
    p.add_argument("--shards-root", default=None)
    p.add_argument("--out-dir", default="experiments")
    p.add_argument("--n-rows", type=int, default=2500, help="probe rows")
    p.add_argument("--batch-size", type=int, default=250)
    p.add_argument("--n-anchors", type=int, default=32, help="steer anchors")
    p.add_argument("--steps", type=int, default=200)
    p.add_argument("--lr", type=float, default=0.05,
                   help="Adam lr as a fraction of the step budget")
    p.add_argument("--w-hold", type=float, default=1.0)
    p.add_argument("--budgets", type=float, nargs="+",
                   default=(0.1, 0.3, 1.0, 3.0),
                   help="step budgets in units of one prior half-width move")
    args = p.parse_args()
    torch.manual_seed(SEED)
    (run_probe if args.mode == "probe" else run_steer)(args)


if __name__ == "__main__":
    main()
