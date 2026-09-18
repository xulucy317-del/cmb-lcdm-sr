#!/usr/bin/env python
"""Replay the §2.5 OLS-injection diagnostic from the stored `mse40` fronts.

`docs/evidence_record.md` §2.5 reports, from a
2026-08-31 pass whose code was never committed, that placing the exact T0-fit
OLS expression into each frozen `mse40` candidate set at its true complexity
and applying the unchanged rules would retain it in 43/55 runs and win the
unchanged minimum-validation-MSE selection in 39/55. The result is cited in
§4, §5 and §7 item 4 and cannot currently be re-derived: there is no script,
no artifact, and nothing in the repository mentions it. Every input is on
disk, so this is a replay, not a campaign.

Three readouts, all on the 55 stored `results/*/mse_one_stage_ms40/*/report.json`:

  * **validation gap** — OLS T0-validation MSE against the validation-selected
    SR winner, with the median ratio MSE_val(SR)/MSE_val(OLS);
  * **fit-side dominance** — how often OLS beats *every* front member on the
    4,000 T0-fit rows, i.e. the search never produced an affine-competitive
    candidate at any complexity it explored;
  * **injection** — retention (lower fit MSE than every stored member of
    complexity <= the injected complexity) and whether the unchanged selector
    would pick it.

The OLS map is refitted here in the search's own basis and target convention
(`raw64` inputs — omega_b, omega_cdm, H0, tau, A_s = exp(ln10As)*1e-10, n_s —
against the standardized target, T0-fit rows only). The refit is checked
against each report's frozen `ols_baseline`: coefficients and `mse_val` must
agree, so the replay cannot silently drift from what the campaign stored.

    python scripts/replay_ols_injection.py

Post-hoc on T0 rows; a mechanism diagnostic, not a gate. Deterministic.
"""
from __future__ import annotations

import argparse
import glob
import json
import statistics as st
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401

import numpy as np

from cmb_lcdm_sr.tiers import T0_FIT, T0_VAL

# 6 variables + 7 constants + 12 operators for a dense six-input affine map.
OLS_COMPLEXITY = 25
FINITE_MIN = 0.999
RTOL = 1e-6


def raw64_inputs(theta_test: np.ndarray) -> np.ndarray:
    """The `raw64` design the mse_one_stage searches were given."""
    return np.column_stack([
        theta_test[:, 0], theta_test[:, 1], theta_test[:, 2], theta_test[:, 3],
        np.exp(theta_test[:, 4]) * 1e-10, theta_test[:, 5],
    ])


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset-dir", default="data")
    p.add_argument("--models-root", default="models")
    p.add_argument("--results-root", default="results")
    p.add_argument("--complexity", type=int, default=OLS_COMPLEXITY)
    p.add_argument("--out", default="experiments/ols_injection_replay_v1.json")
    args = p.parse_args()

    data = Path(args.dataset_dir)
    theta = np.load(data / "theta.npy")
    sid = np.load(data / "splits_v1.npz")["split_id"]
    X = raw64_inputs(theta[sid == 2])
    design = np.hstack([X, np.ones((len(X), 1))])          # bias last, as stored

    means = {}
    rows = []
    for path in sorted(glob.glob(
            f"{args.results_root}/*/mse_one_stage_ms40/z*_seed*/report.json")):
        with open(path) as f:
            rep = json.load(f)
        run = rep["regime"]
        if run not in means:
            means[run] = np.load(Path(args.models_root) / run / "analysis"
                                 / "encoder_means_test.npy").astype(np.float64)
        k = rep["latent_index"]
        tf = rep["target_transform"]
        y = (means[run][:, k] - tf["mean"]) / tf["std"]

        coef, *_ = np.linalg.lstsq(design[T0_FIT], y[T0_FIT], rcond=None)
        ols_fit = float(((design[T0_FIT] @ coef - y[T0_FIT]) ** 2).mean())
        ols_val = float(((design[T0_VAL] @ coef - y[T0_VAL]) ** 2).mean())

        stored = rep["ols_baseline"]
        drift_mse = abs(ols_val - stored["mse_val"]) / stored["mse_val"]
        drift_coef = float(np.max(np.abs(
            (coef - np.asarray(stored["coefs"]))
            / np.maximum(np.abs(stored["coefs"]), 1e-30))))
        if drift_mse > RTOL:
            raise SystemExit(
                f"{path}: replayed OLS mse_val drifts {drift_mse:.2e} from "
                f"the stored baseline; conventions do not match")

        front = [e for e in rep["all_equations"]
                 if min(e["finite_frac_fit"], e["finite_frac_val"]) >= FINITE_MIN]
        if not front:
            raise SystemExit(f"{path}: no valid front members")
        # The campaign's own selector: minimum validation MSE, ties to lower
        # complexity then lower equation index.
        winner = min(front, key=lambda e: (e["mse_val"], e["complexity"],
                                           e["index"]))
        eligible = [e for e in front if e["complexity"] <= args.complexity]

        rows.append({
            "path": path, "run": run, "latent": k, "seed": rep["seed"],
            "ols_mse_fit": ols_fit, "ols_mse_val": ols_val,
            "stored_ols_mse_val": stored["mse_val"],
            "replay_rel_drift_mse_val": drift_mse,
            "replay_rel_drift_coef_max": drift_coef,
            "sr_winner_complexity": winner["complexity"],
            "sr_winner_mse_val": winner["mse_val"],
            "sr_winner_mse_fit": winner["mse_fit_eval"],
            "val_ratio_sr_over_ols": winner["mse_val"] / ols_val,
            "ols_wins_validation": bool(ols_val < winner["mse_val"]),
            "ols_beats_every_front_member_on_fit":
                bool(all(ols_fit < e["mse_fit_eval"] for e in front)),
            "n_front": len(front),
            "n_eligible_at_complexity": len(eligible),
            "injected_retained":
                bool(all(ols_fit < e["mse_fit_eval"] for e in eligible)),
            "injected_wins_selection":
                bool(ols_val < winner["mse_val"]
                     or (ols_val == winner["mse_val"]
                         and args.complexity < winner["complexity"])),
        })

    def tally(key, subset=None):
        sel = [r for r in rows if subset is None or r["run"] == subset]
        return sum(r[key] for r in sel), len(sel)

    runs = sorted({r["run"] for r in rows})
    summary = {
        "n_runs": len(rows),
        "injected_complexity": args.complexity,
        "max_replay_rel_drift_mse_val":
            max(r["replay_rel_drift_mse_val"] for r in rows),
        "max_replay_rel_drift_coef": max(r["replay_rel_drift_coef_max"]
                                         for r in rows),
        "median_val_ratio_sr_over_ols":
            st.median(r["val_ratio_sr_over_ols"] for r in rows),
        "val_ratio_range": [min(r["val_ratio_sr_over_ols"] for r in rows),
                            max(r["val_ratio_sr_over_ols"] for r in rows)],
    }
    for key in ("ols_wins_validation", "ols_beats_every_front_member_on_fit",
                "injected_retained", "injected_wins_selection"):
        n, tot = tally(key)
        summary[key] = {"overall": f"{n}/{tot}",
                        **{r: "{}/{}".format(*tally(key, r)) for r in runs}}

    exceptions = sorted(
        (r["run"], f"z{r['latent']}", r["seed"]) for r in rows
        if not r["ols_beats_every_front_member_on_fit"])
    keeps_sr = sorted(
        (r["run"], f"z{r['latent']}", r["seed"]) for r in rows
        if not r["injected_wins_selection"])

    record = {
        "kind": "ols_injection_replay",
        "version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source": "results/*/mse_one_stage_ms40/z*_seed*/report.json",
        "basis": "raw64 (omega_b, omega_cdm, H0, tau, A_s, n_s), "
                 "standardized target, OLS fitted on T0_fit only",
        "status": "post-hoc mechanism diagnostic on T0 rows; not a gate",
        "summary": summary,
        "fit_side_exceptions": exceptions,
        "selection_keeps_sr": keeps_sr,
        "runs": rows,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(record, f, indent=1, sort_keys=True)

    print(f"{len(rows)} stored ms40 runs replayed")
    print(f"replay vs stored ols_baseline: max relative drift "
          f"{summary['max_replay_rel_drift_mse_val']:.2e} (mse_val), "
          f"{summary['max_replay_rel_drift_coef']:.2e} (coefficients)")
    for key in ("ols_wins_validation", "ols_beats_every_front_member_on_fit",
                "injected_retained", "injected_wins_selection"):
        s = summary[key]
        detail = ", ".join(f"{r} {s[r]}" for r in runs)
        print(f"  {key:<42} {s['overall']}   ({detail})")
    print(f"  median MSE_val(SR)/MSE_val(OLS){'':<11} "
          f"{summary['median_val_ratio_sr_over_ols']:.3f}   "
          f"(range {summary['val_ratio_range'][0]:.2f}"
          f"-{summary['val_ratio_range'][1]:.0f})")
    tag = {"lcdm_tt_beta3e-4": "TT", "lcdm_tt_ee_lowl": "EE"}
    fmt = lambda xs: ", ".join(f"{tag[a]} {b} s{c}" for a, b, c in xs)
    print(f"\nfit-side exceptions ({len(exceptions)}): {fmt(exceptions)}")
    print(f"selection keeps SR ({len(keeps_sr)}): {fmt(keeps_sr)}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
