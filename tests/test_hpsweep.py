"""Hyperparameter-sweep pipeline: planner expansion + consolidation."""
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

from sweep_blind_sr import (  # noqa: E402
    build_manifest,
    compact_ranges,
    expand_configs,
    rough_seconds,
    write_tsv,
    TSV_COLS,
)


def mini_spec(**over):
    spec = {
        "name": "unittest",
        "run_dir": "models/lcdm_tt_beta3e-4",
        "inputs": ["omega_b", "omega_cdm", "H0", "tau", "A_s", "n_s"],
        "latents": [2],
        "seeds": [0, 1],
        "n_samples": 5000,
        "mode": "star",
        "baseline": {"niterations": 10, "populations": 5, "maxsize": 10, "extra": {}},
        "axes": {"maxsize": [12], "population_size": [50]},
    }
    spec.update(over)
    return spec


# --- planner -----------------------------------------------------------------

def test_star_expansion_baseline_first_and_dedup():
    spec = mini_spec(axes={"maxsize": [10, 12], "niterations": [10, 20]})
    cfgs = expand_configs(spec)
    # value == baseline collapses into the baseline config
    assert [c["label"] for c in cfgs] == ["baseline", "ms12", "ni20"]
    assert cfgs[0]["config_id"] == "c00_baseline"
    assert cfgs[1]["maxsize"] == 12 and cfgs[1]["niterations"] == 10


def test_star_expansion_extra_axis_routed_to_extra():
    cfgs = expand_configs(mini_spec())
    ps = next(c for c in cfgs if c["label"] == "ps50")
    assert ps["extra"] == {"population_size": 50}
    assert ps["maxsize"] == 10  # core keys stay at baseline
    base = cfgs[0]
    assert base["extra"] == {}


def test_grid_expansion_is_cartesian():
    spec = mini_spec(mode="grid",
                     axes={"maxsize": [10, 12], "niterations": [10, 20]})
    cfgs = expand_configs(spec)
    assert len(cfgs) == 4
    combos = {(c["maxsize"], c["niterations"]) for c in cfgs}
    assert combos == {(10, 10), (10, 20), (12, 10), (12, 20)}


def test_forbidden_axis_rejected():
    with pytest.raises(SystemExit, match="managed by run_blind_sr.py"):
        expand_configs(mini_spec(axes={"random_state": [1, 2]}))


def test_manifest_tasks_and_tsv(tmp_path):
    spec = mini_spec()
    sweep_dir = tmp_path / "hpsweep_unittest"
    man = build_manifest(spec, sweep_dir)
    # 3 configs (baseline, ms12, ps50) x 1 latent x 2 seeds
    assert man["n_configs"] == 3 and man["n_tasks"] == 6
    assert [t["idx"] for t in man["tasks"]] == list(range(6))
    assert man["tasks"][0]["out_dir"].endswith("c00_baseline/z2_seed0")

    sweep_dir.mkdir()
    write_tsv(spec, man["tasks"], man["configs"], sweep_dir / "tasks.tsv")
    lines = (sweep_dir / "tasks.tsv").read_text().splitlines()
    assert lines[0].split("\t") == TSV_COLS
    row = dict(zip(TSV_COLS, lines[-1].split("\t")))
    assert row["config_id"] == "c02_ps50"
    assert row["extra_json"] == '{"population_size":50}'  # tab/space-free
    assert row["inputs"] == "omega_b omega_cdm H0 tau A_s n_s"


def test_rough_seconds_monotone():
    base = {"niterations": 200, "populations": 15, "maxsize": 20, "extra": {}}
    assert rough_seconds(base) == pytest.approx(330.0)
    slower = {**base, "niterations": 400}
    cheap = {**base, "maxsize": 10}
    assert rough_seconds(slower) > rough_seconds(base) > rough_seconds(cheap)


def test_compact_ranges():
    assert compact_ranges([0, 1, 2, 5, 7, 8]) == "0-2,5,7-8"
    assert compact_ranges([3]) == "3"
    assert compact_ranges([]) == ""


# --- subsets mode (Phase-4 blind variable screen; docs/discovery_roadmap.md) --

def subsets_spec(**over):
    spec = mini_spec(mode="subsets",
                     subsets={"pool": ["tau", "A_s", "n_s"], "min_size": 1})
    del spec["axes"], spec["inputs"]
    spec.update(over)
    return spec


def test_subsets_expansion_counts_labels_inputs():
    cfgs = expand_configs(subsets_spec())
    assert len(cfgs) == 7                     # 2^3 - 1, sizes ascending
    assert [c["label"] for c in cfgs] == [
        "S-tau", "S-As", "S-ns",
        "S-tau-As", "S-tau-ns", "S-As-ns", "S-tau-As-ns"]
    assert cfgs[0]["config_id"] == "c00_S-tau"
    assert cfgs[3]["inputs"] == ["tau", "A_s"]
    # PySR config pinned at the baseline throughout
    assert all(c["maxsize"] == 10 and c["niterations"] == 10 and c["extra"] == {}
               for c in cfgs)


def test_subsets_min_size_filters_singletons():
    cfgs = expand_configs(
        subsets_spec(subsets={"pool": ["tau", "A_s", "n_s"], "min_size": 2}))
    assert [c["label"] for c in cfgs] == \
        ["S-tau-As", "S-tau-ns", "S-As-ns", "S-tau-As-ns"]


def test_subsets_rejects_axes():
    with pytest.raises(SystemExit, match="does not combine"):
        expand_configs(subsets_spec(axes={"maxsize": [12]}))


def test_subsets_tsv_carries_per_config_inputs(tmp_path):
    spec = subsets_spec()
    sweep_dir = tmp_path / "hpsweep_subsets"
    man = build_manifest(spec, sweep_dir)
    assert man["n_configs"] == 7 and man["n_tasks"] == 14   # x 1 latent x 2 seeds
    sweep_dir.mkdir()
    write_tsv(spec, man["tasks"], man["configs"], sweep_dir / "tasks.tsv")
    lines = (sweep_dir / "tasks.tsv").read_text().splitlines()
    rows = [dict(zip(TSV_COLS, line.split("\t"))) for line in lines[1:]]
    inputs_by_cfg = {r["config_id"]: r["inputs"] for r in rows}
    assert inputs_by_cfg["c00_S-tau"] == "tau"
    assert inputs_by_cfg["c06_S-tau-As-ns"] == "tau A_s n_s"


# --- consolidation -----------------------------------------------------------

def fake_report(cfg, seed, mi_by_complexity):
    """Minimal report.json matching what consolidate_hp_sweep reads."""
    eqs = [{"index": i, "complexity": c, "mi_val": mi, "mi_val_err": 0.01,
            "mse_val": 0.1, "expression_simplified": expr}
           for i, (c, mi, expr) in enumerate(mi_by_complexity)]
    return {
        "pysr_kwargs": {"niterations": cfg["niterations"],
                        "populations": cfg["populations"],
                        "maxsize": cfg["maxsize"], "random_state": seed,
                        **cfg["extra"]},
        "fit_seconds": 100.0 + seed,
        "all_equations": eqs,
    }


def test_consolidate_end_to_end(tmp_path):
    import consolidate_hp_sweep as chs

    spec = mini_spec(axes={"maxsize": [12]})  # baseline + ms12
    sweep_dir = tmp_path / "hpsweep_unittest"
    sweep_dir.mkdir()
    man = build_manifest(spec, sweep_dir)
    (sweep_dir / "manifest.json").write_text(json.dumps(man))

    front = [(3, 0.50, "tau"),
             (7, 0.80, "A_s*(tau - 0.598)"),
             (12, 0.90, "A_s*(tau - 0.598) + square(omega_cdm)")]
    by_id = {c["config_id"]: c for c in man["configs"]}
    for t in man["tasks"]:
        cfg = by_id[t["config_id"]]
        out = pathlib.Path(t["out_dir"])
        out.mkdir(parents=True)
        rep = fake_report(cfg, t["seed"], front)
        if t["config_id"].endswith("ms12") and t["seed"] == 1:
            rep["pysr_kwargs"]["maxsize"] = 99  # stale output -> must be dropped
        out.joinpath("report.json").write_text(json.dumps(rep))

    md, payload = chs.consolidate(sweep_dir, cap=10)
    z2 = {c["label"]: c["latents"]["z2"] for c in payload["configs"]}

    assert z2["baseline"]["n_seeds"] == 2
    assert z2["ms12"]["n_seeds"] == 1  # stale report skipped
    assert z2["baseline"]["top_mi_mean"] == pytest.approx(0.90)
    # cap=10 excludes the complexity-12 equation
    assert z2["baseline"]["mi_cap_mean"] == pytest.approx(0.80)
    # amplitude diagnostics on z2: textbook form counted, r(top) computed
    assert z2["baseline"]["textbook_hits"] == 4  # 2 hits x 2 seeds
    assert z2["baseline"]["r_top_mean"] is not None

    text = "\n".join(md)
    assert "One-factor effects" in text
    assert "`ms12`" in text and "baseline" in text
    assert "MI@c<=10" in text
