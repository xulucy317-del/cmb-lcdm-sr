#!/usr/bin/env python
"""Encoder-side gradient attribution — which multipoles does latent k read?

The first of the three LLM-interpretability transfers listed in §0.1 item 4 of
`docs/evidence_record.md`, and item 9 of §5.1 of
`docs/sr_objective_discussion_2026-09-02.md`. One backward pass per latent:

    g_k(ell) = d mu_k / d x_ell

where x is exactly what the encoder sees — log10(D_ell / ref_ell), per-ell
standardised with the run's stored scaler. This is the **encoder** side, and
that is the point. Phase 7b already computed the decoder Jacobian
d Decoder(z)_ell / d z_k (`scripts/decoder_effect.py`) and it delivered real
attribution, but gate G4b FAILED on both models because reading the amplitude
split out of it requires decomposing a curve onto the (tau, lnA_s) response
templates, which are near-antiparallel (uncentered cos -0.9902 EE / -0.9996
TT). g_k(ell) never touches a parameter basis, so that degeneracy cannot
arise; the price is that it answers "which multipoles", not "what
coefficient".

**The test this is designed for.** Per the run configs, the TT encoder sees
ell in [30, 2500] and the TT+EE model's EE channel sees ell in [2, 2500]. The
low-ell EE reionization bump is therefore the *only* place in either model
where the A_s-tau degeneracy can be broken, and the TT encoder structurally
cannot see it. If the E3 reading is right — TT+EE splits the amplitude sector
into two latents while TT needs one — the EE amplitude latents must put real
gradient mass on ell < 30, and no TT latent can. That is falsifiable from the
band table below and independent of every instrument used so far.

**The projection that makes this readable.** The input is ~5000-dimensional
while the data manifold is 6-dimensional, so almost every input direction is
one training never constrained. Measured: only **0.03-1.3%** of |g_k|^2 lies
in the span of the six physical response templates t_j(ell)/sigma_ell. The
raw per-ell gradient is therefore *not* a safe fine-grained attribution — it
is dominated by off-manifold directions. The primary readout is the
**projected** gradient P g, the component inside that six-dimensional span,
i.e. the part of the sensitivity that any actual change of cosmology can
excite. The raw curve is reported alongside, and the two agree on the
qualitative band structure.

Two curves per latent, both reported:

  * **normalised** dmu/dx_ell — the primary attribution. x is the network's
    own input, and its per-ell scale already encodes how much that bin varies
    across the training set, so |dmu/dx| is "how far the latent moves per
    standard deviation of that bin".
  * **physical** dmu/dlog10 D_ell = (dmu/dx_ell) / sigma_ell — the same curve
    in spectrum units. `decoder_effect.py` multiplies by sigma on the output
    side; the input-side chain rule divides.

Evaluated at `--n-anchors` rows drawn deterministically from T1, never from
the T0 rows the searches used. Reported as the across-anchor mean, with the
across-anchor std as a stability band.

Reads:  models/<run>/{best_model.pt, scaler.npz, config_used.json},
        data/{splits_v1.npz, spectral_templates_v1.npz}, the spectra shards.
Writes: experiments/encoder_gradient_attribution_<run>.{json,npz}

    python scripts/encoder_gradient_attribution.py --run lcdm_tt_ee_lowl

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

from cmb_lcdm_sr import tiers  # noqa: E402
from cmb_lcdm_sr.dataset import ShardedSpectraDataset  # noqa: E402
from cmb_lcdm_sr.encoder import load_checkpoint, resolve_shard_dirs  # noqa: E402
from cmb_lcdm_sr.scaler import ShardedScaler  # noqa: E402

RUNS = ("lcdm_tt_beta3e-4", "lcdm_tt_ee_lowl")
SEED = 20260903
# The reionization window is the first band; the rest are the usual acoustic
# ranges. Edges are inclusive-lower, exclusive-upper except the last.
BANDS = ((2, 30), (30, 100), (100, 500), (500, 1500), (1500, 2501))


def template_projector(templates, scaler) -> np.ndarray:
    """Orthonormal basis for the 6 physical responses, standardised units."""
    basis = np.concatenate(
        [templates[f"templates_{ch}"] / scaler.channel_stats(ch)[1]
         for ch in scaler.channels], axis=1).T          # (D, 6)
    q, _ = np.linalg.qr(basis)
    return q


def band_mass(ell: np.ndarray, g: np.ndarray) -> dict[str, float]:
    """|g| mass per band, as a fraction of this latent's total over all bins."""
    return {f"{lo}-{hi - 1}": float(np.abs(g[(ell >= lo) & (ell < hi)]).sum())
            for lo, hi in BANDS}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", choices=RUNS, default=None,
                   help="default: both checkpoints")
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--models-root", default="models")
    p.add_argument("--shards-root", default=None)
    p.add_argument("--n-anchors", type=int, default=64)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--out-dir", default="experiments")
    args = p.parse_args()

    torch.manual_seed(SEED)
    templates = np.load(Path(args.dataset_dir) / "spectral_templates_v1.npz")
    split_id = np.load(Path(args.dataset_dir) / "splits_v1.npz")["split_id"]
    idx_test = np.where(split_id == 2)[0]

    # Deterministic anchor positions inside T1, never T0.
    rng = np.random.default_rng(SEED)
    anchors = np.sort(rng.choice(np.arange(tiers.T1.start, tiers.T1.stop),
                                 size=args.n_anchors, replace=False))

    for run in ([args.run] if args.run else list(RUNS)):
        run_dir = Path(args.models_root) / run
        with open(run_dir / "config_used.json") as f:
            data_cfg = json.load(f)["data"]
        scaler = ShardedScaler.load(run_dir / "scaler.npz")
        dirs = resolve_shard_dirs(run_dir, shards_root=args.shards_root)
        refs = {ch: scaler.refs[ch].astype(np.float32) for ch in scaler.channels}
        lengths = {ch: refs[ch].shape[0] for ch in scaler.channels}
        dict_mode = (len(set(lengths.values())) > 1
                     or bool(data_cfg.get("force_dict_mode", False)))

        ds = ShardedSpectraDataset(
            shard_dirs={ch: str(dirs[ch]) for ch in scaler.channels},
            refs=refs, indices=idx_test,
            expected_n=int(data_cfg.get("expected_n", 500_000)),
            n_shards=int(data_cfg.get("n_shards", 100)),
            return_dict=dict_mode)
        model, _ = load_checkpoint(run_dir / "best_model.pt", device="cpu")

        stats = {ch: scaler.channel_stats(ch) for ch in scaler.channels}
        ell = {ch: templates[f"ell_{ch}"] for ch in scaler.channels}
        n_lat = model.latent_dim
        # per-anchor gradients, normalised space
        grads = {ch: np.zeros((n_lat, args.n_anchors, lengths[ch]),
                              dtype=np.float64) for ch in scaler.channels}

        print(f"\n### {run}: {n_lat} latents, {args.n_anchors} T1 anchors, "
              f"channels {scaler.channels}")
        done = 0
        for start in range(0, args.n_anchors, args.batch_size):
            rows = anchors[start:start + args.batch_size]
            raw = [ds[int(r)] for r in rows]
            if dict_mode:
                x = {ch: torch.stack([r[ch] for r in raw]) for ch in scaler.channels}
                x = {ch: ((x[ch] - torch.tensor(stats[ch][0], dtype=torch.float32))
                          / torch.tensor(stats[ch][1], dtype=torch.float32)
                          ).requires_grad_(True)
                     for ch in scaler.channels}
                leaves = [x[ch] for ch in scaler.channels]
            else:
                mu_s = torch.tensor(np.stack([stats[ch][0] for ch in scaler.channels]),
                                    dtype=torch.float32)
                sd_s = torch.tensor(np.stack([stats[ch][1] for ch in scaler.channels]),
                                    dtype=torch.float32)
                stacked = torch.stack(raw)
                x = ((stacked - mu_s) / sd_s).requires_grad_(True)
                leaves = [x]

            mu, _ = model.encode(x)
            sl = slice(start, start + len(rows))
            for k in range(n_lat):
                gs = torch.autograd.grad(mu[:, k].sum(), leaves,
                                         retain_graph=(k < n_lat - 1))
                if dict_mode:
                    for ch, g in zip(scaler.channels, gs):
                        grads[ch][k, sl] = g.detach().numpy()
                else:
                    arr = gs[0].detach().numpy()          # (B, C, L)
                    for c, ch in enumerate(scaler.channels):
                        grads[ch][k, sl] = arr[:, c, :]
            done += len(rows)
            print(f"  anchors {done}/{args.n_anchors}")

        record = {
            "kind": "encoder_gradient_attribution",
            "version": 1,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "run": run,
            "quantity": "g_k(ell) = d mu_k / d x_ell, x = per-ell standardised "
                        "log10(D_ell/ref); physical = g / sigma_ell",
            "anchors": {"n": args.n_anchors, "tier": "T1", "seed": SEED,
                        "positions": anchors.tolist()},
            "channels": list(scaler.channels),
            "ell_range": {ch: [int(ell[ch][0]), int(ell[ch][-1])]
                          for ch in scaler.channels},
            "bands": [f"{lo}-{hi - 1}" for lo, hi in BANDS],
            "latents": {},
        }
        proj = template_projector(templates, scaler)
        record["projection"] = (
            "P = orthonormal span of the six templates t_j/sigma; "
            "'projected' quantities use P P^T g, the on-manifold component")
        edges = np.cumsum([0] + [lengths[ch] for ch in scaler.channels])
        curves = {}
        for k in range(n_lat):
            mean = {ch: grads[ch][k].mean(axis=0) for ch in scaler.channels}
            flat = np.concatenate([mean[ch] for ch in scaler.channels])
            projected = proj @ (proj.T @ flat)
            on_manifold = float((projected @ projected) / (flat @ flat))

            entry = {"on_manifold_frac": on_manifold,
                     "total_abs_mass": float(np.abs(flat).sum()),
                     "total_abs_mass_projected": float(np.abs(projected).sum()),
                     "channel_mass": {}, "bands": {}, "bands_projected": {}}
            tot = float(np.abs(flat).sum())
            tot_p = float(np.abs(projected).sum())
            for c, ch in enumerate(scaler.channels):
                gp = projected[edges[c]:edges[c + 1]]
                curves[f"g_{ch}_z{k}"] = mean[ch]
                curves[f"gstd_{ch}_z{k}"] = grads[ch][k].std(axis=0)
                curves[f"gphys_{ch}_z{k}"] = mean[ch] / stats[ch][1]
                curves[f"gproj_{ch}_z{k}"] = gp
                entry["channel_mass"][ch] = float(np.abs(mean[ch]).sum()) / tot
                entry["bands"][ch] = {b: v / tot for b, v
                                      in band_mass(ell[ch], mean[ch]).items()}
                entry["bands_projected"][ch] = {
                    b: v / tot_p for b, v in band_mass(ell[ch], gp).items()}
            record["latents"][f"z{k}"] = entry

        out = Path(args.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(out / f"encoder_gradient_attribution_{run}.npz",
                            **curves,
                            **{f"ell_{ch}": ell[ch] for ch in scaler.channels},
                            anchors=anchors)
        with open(out / f"encoder_gradient_attribution_{run}.json", "w") as f:
            json.dump(record, f, indent=1, sort_keys=True)

        head = "  ".join(f"{b:>10}" for b in record["bands"])
        for key, label in (("bands_projected", "PROJECTED (primary)"),
                           ("bands", "raw")):
            for ch in scaler.channels:
                print(f"\n  |g| mass fraction by ell band, {label} — channel "
                      f"{ch} (ell {record['ell_range'][ch][0]}"
                      f"-{record['ell_range'][ch][1]})")
                print(f"  {'lat':<5} {'on-manif':>10}  {head}")
                for k in range(n_lat):
                    e = record["latents"][f"z{k}"]
                    cells = "  ".join(f"{e[key][ch][b]:>10.4f}"
                                      for b in record["bands"])
                    print(f"  z{k:<4} {e['on_manifold_frac']:>10.4f}  {cells}")
        print(f"\n  wrote {out}/encoder_gradient_attribution_{run}.{{json,npz}}")


if __name__ == "__main__":
    main()
