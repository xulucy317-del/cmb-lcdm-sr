"""Phase-4 screen consolidation: subset stats, Pareto + 1-SE keeps, emission."""
import json
import pathlib
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

from consolidate_subsets import (  # noqa: E402
    annotate_minimality,
    consolidate_latent,
    emit_finalists,
    gate_g2,
    load_screen,
    pick_s_star,
    screen_recurrence,
    select_finalists,
    subset_stats,
)

POOL = ["omega_b", "omega_cdm", "H0", "tau", "A_s", "n_s"]

# (config_id, inputs, {seed: [(c, mi)]}) — engineered so that:
#   c04 (1 var)  -> frontier (smallest support and knee)
#   c18 (2 var)  -> frontier (eta 0.960 at c*=5)
#   c36 (3 var)  -> dominated by c18, outside 1 SE -> dropped
#   c44 (4 var)  -> dominated by c18, inside 1 SE  -> 1-SE keep
#   c62 (all 6)  -> the in-screen reference, frontier (eta = 1)
FIXTURE = [
    ("c04_S-As", ["A_s"],
     {0: [(1, 0.30)], 1: [(1, 0.32)]}),
    ("c18_S-tau-As", ["tau", "A_s"],
     {0: [(2, 0.50), (5, 0.96)], 1: [(2, 0.52), (5, 0.98)]}),
    ("c36_S-oc-As-ns", ["omega_cdm", "A_s", "n_s"],
     {0: [(6, 0.90)], 1: [(6, 0.92)]}),
    ("c44_S-ob-oc-tau-As", ["omega_b", "omega_cdm", "tau", "A_s"],
     {0: [(7, 0.955)], 1: [(7, 0.975)]}),
    ("c62_S-all", POOL,
     {0: [(8, 1.00)], 1: [(8, 1.02)]}),
]


def build_tree(tmp_path, run="lcdm_tt_beta3e-4", latent=0):
    sweep = tmp_path / "results" / run / "hpsweep_subsets_v1"
    configs = []
    n = 0
    for cid, inputs, seeds in FIXTURE:
        configs.append({"config_id": cid, "label": cid.split("_", 1)[1],
                        "niterations": 100, "populations": 15, "maxsize": 20,
                        "extra": {}, "inputs": inputs})
        for s, rows in seeds.items():
            d = sweep / cid / f"z{latent}_seed{s}"
            d.mkdir(parents=True)
            eqs = [{"complexity": c, "mi_val": mi, "mi_val_err": 0.01,
                    "expression_simplified": f"f_{cid}_{c}", "index": i}
                   for i, (c, mi) in enumerate(rows)]
            (d / "report.json").write_text(json.dumps({"all_equations": eqs}))
            n += 1
    (sweep / "manifest.json").write_text(json.dumps(
        {"configs": configs, "n_tasks": n, "run_dir": f"models/{run}",
         "run_name": run, "sweep_name": "subsets_v1"}))
    return sweep


def test_subset_stats_mean_se_knee():
    st = subset_stats({0: [(2, 0.50, 0.01, "a"), (5, 0.96, 0.01, "b")],
                       1: [(2, 0.52, 0.01, "a"), (5, 0.98, 0.01, "c")]})
    assert np.isclose(st["mi"], 0.97) and np.isclose(st["se"], 0.01)
    assert st["c_star"] == 5 and st["n_seeds"] == 2
    assert st["best_mi"] == 0.98 and st["best_expr"] == "c"


def test_consolidate_latent_frontier_and_1se(tmp_path):
    sweep = build_tree(tmp_path)
    configs, fronts, _m = load_screen(sweep)
    lat = consolidate_latent(0, configs, fronts)
    assert np.isclose(lat["ref"]["mi"], 1.01)
    by = {e["config_id"]: e for e in lat["entries"]}
    assert by["c04_S-As"]["frontier"]
    e18 = by["c18_S-tau-As"]
    assert e18["frontier"] and np.isclose(e18["eta"], 0.97 / 1.01)
    assert e18["c_star"] == 5
    assert by["c62_S-all"]["frontier"] and np.isclose(by["c62_S-all"]["eta"], 1.0)
    # dominated well outside 1 SE -> dropped
    e36 = by["c36_S-oc-As-ns"]
    assert not e36["frontier"] and not e36["keep_1se"]
    # dominated but within one SE of non-dominance -> kept
    e44 = by["c44_S-ob-oc-tau-As"]
    assert not e44["frontier"] and e44["keep_1se"] and e44["finalist"]
    assert lat["n_finalists"] == 4
    assert lat["staircase"]["2"]["config_id"] == "c18_S-tau-As"


def test_select_finalists_pure_logic():
    a = {"config_id": "a", "size": 1, "c_star": 3, "eta": 0.5, "eta_se": 0.01}
    b = {"config_id": "b", "size": 2, "c_star": 5, "eta": 0.9, "eta_se": 0.01}
    c = {"config_id": "c", "size": 2, "c_star": 6, "eta": 0.7, "eta_se": 0.01}
    select_finalists([a, b, c])
    assert a["frontier"] and b["frontier"]
    assert not c["frontier"] and not c["keep_1se"]


def test_emit_finalists_excludes_all6(tmp_path):
    sweep = build_tree(tmp_path)
    configs, fronts, _m = load_screen(sweep)
    lat = consolidate_latent(0, configs, fronts)
    out = tmp_path / "finals"
    n = emit_finalists("lcdm_tt_beta3e-4", "models/lcdm_tt_beta3e-4",
                       {"z0": lat}, out)
    lines = (out / "tasks.tsv").read_text().strip().split("\n")
    header, rows = lines[0].split("\t"), [ln.split("\t") for ln in lines[1:]]
    assert n == 15 and len(rows) == 15          # 3 finalists x 5 seeds
    assert header[0] == "idx" and header[-1] == "out_dir"
    cids = {r[1] for r in rows}
    assert cids == {"c04_S-As", "c18_S-tau-As", "c44_S-ob-oc-tau-As"}
    assert all(r[4] == "200" for r in rows)     # full protocol ni200
    r18 = next(r for r in rows if r[1] == "c18_S-tau-As")
    assert r18[9] == "tau A_s"
    assert json.loads((out / "manifest.json").read_text())["n_tasks"] == 15


def test_main_end_to_end(tmp_path, monkeypatch):
    import consolidate_subsets

    build_tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["consolidate_subsets.py",
                                      "--run", "lcdm_tt_beta3e-4",
                                      "--emit-finalists"])
    assert consolidate_subsets.main() == 0
    payload = json.loads(
        (tmp_path / "experiments/subset_selection_lcdm_tt_beta3e-4.json")
        .read_text())
    assert payload["latents"]["z0"]["n_finalists"] == 4
    assert payload["latents"]["z1"] is None     # screen has no z1 fronts
    assert payload["finals"] is None            # no finalist reports yet
    md = (tmp_path /
          "experiments/subset_selection_lcdm_tt_beta3e-4.md").read_text()
    assert "frontier" in md and "1-SE keep" in md
    assert (tmp_path / "results/lcdm_tt_beta3e-4/hpsweep_subsets_v1_finals"
            / "tasks.tsv").exists()


# ---- 4b: minimality, screen recurrence, gate G2 -----------------------------

def _entry(cid, inputs, mi, se, size=None, c_star=5, per_seed=None):
    e = {"config_id": cid, "inputs": inputs, "size": size or len(inputs),
         "mi": mi, "se": se, "c_star": c_star, "eta": mi, "eta_se": se}
    if per_seed is not None:
        e["per_seed_max"] = {str(s): v for s, v in per_seed.items()}
    return e


def test_minimality_and_s_star():
    e2 = _entry("c18", ["tau", "A_s"], 0.99, 0.01)
    e1 = _entry("c04", ["A_s"], 0.35, 0.01)
    e4 = _entry("c44", ["omega_b", "omega_cdm", "tau", "A_s"], 1.00, 0.01)
    e6 = _entry("c62", POOL, 1.000, 0.01)   # gap -0.01 vs tol 0.0141
    entries = [e1, e2, e4, e6]
    annotate_minimality(entries)
    # {A_s} is far below its supersets -> not minimal
    assert not e1["minimal"]
    # {tau,A_s} within hypot(0.01,0.01) of every superset -> minimal
    assert e2["minimal"] and e4["minimal"] and e6["minimal"]
    assert e2["worst_superset"]["config_id"] in ("c44", "c62")
    s = pick_s_star(entries)
    assert s["config_id"] == "c18"
    # if the 2-input subset falls > 1 SE behind, the 4-input one wins
    e2b = _entry("c18", ["tau", "A_s"], 0.90, 0.01)
    entries = [e1, e2b, e4, e6]
    annotate_minimality(entries)
    assert not e2b["minimal"]
    assert pick_s_star(entries)["config_id"] == "c44"


def test_screen_recurrence_per_seed():
    scr = [
        _entry("c18", ["tau", "A_s"], 0.97, 0.01,
               per_seed={0: 0.96, 1: 0.98}),
        _entry("c62", POOL, 0.975, 0.01, per_seed={0: 0.965, 1: 0.985}),
    ]
    rec = screen_recurrence(scr, ["tau", "A_s"])
    # both seeds: within hypot(0.01, 0.01) of the all-6 superset
    assert rec["seed_minimal"] == {"0": True, "1": True}
    assert rec["recurrent"] and rec["same_pick_all_seeds"]
    assert rec["seed_s_star"]["0"] == ["tau", "A_s"]
    # push seed 0's all-6 far above -> seed 0 no longer minimal
    scr[1]["per_seed_max"]["0"] = 1.10
    rec = screen_recurrence(scr, ["tau", "A_s"])
    assert rec["seed_minimal"] == {"0": False, "1": True}
    assert not rec["recurrent"]


def _fin(s_star, entries, recurrent):
    return {"s_star": s_star, "entries": entries,
            "screen_recurrence": {"recurrent": recurrent},
            "ref": {"mi": 1.0, "se": 0.01}, "staircase": {}}


def test_gate_g2_verdicts():
    two = _entry("c18", ["tau", "A_s"], 0.99, 0.01)
    sup = _entry("c50", ["omega_b", "tau", "A_s"], 1.10, 0.01)
    # amplitude PASS: S* = {A_s, tau}, recurrent
    g = gate_g2(2, {"z2": _fin(two, [two, sup], True)})
    assert g["per_latent"]["z2"]["verdict"] == "PASS"
    assert g["overall"] == "PASS"
    # amplitude, right subset but not screen-recurrent -> FAIL
    g = gate_g2(2, {"z2": _fin(two, [two, sup], False)})
    assert g["per_latent"]["z2"]["verdict"].startswith("FAIL")
    # superset finding: S* strictly above {A_s,tau} and beats it by > 1 SE
    g = gate_g2(2, {"z2": _fin(sup, [two, sup], True)})
    assert g["per_latent"]["z2"]["verdict"] == "PASS (superset finding)"
    assert g["per_latent"]["z2"]["beats_2input_by_gt1se"]
    # shape latent: recurrence alone decides
    g = gate_g2(2, {"z0": _fin(two, [two], True),
                    "z2": _fin(two, [two, sup], True)})
    assert g["per_latent"]["z0"]["verdict"] == "PASS"
    g = gate_g2(2, {"z0": _fin(two, [two], False),
                    "z2": _fin(two, [two, sup], True)})
    assert g["per_latent"]["z0"]["verdict"].startswith("ATTENTION")
    assert g["overall"].startswith("PARTIAL")


def _write_family_reports(root, cid_or_none, latent, seed_rows):
    for s, rows in seed_rows.items():
        d = (root / cid_or_none if cid_or_none else root) / \
            f"z{latent}_seed{s}"
        d.mkdir(parents=True, exist_ok=True)
        eqs = [{"complexity": c, "mi_val": mi, "mi_val_err": 0.01,
                "expression_simplified": f"g_{c}", "index": i}
               for i, (c, mi) in enumerate(rows)]
        (d / "report.json").write_text(json.dumps({"all_equations": eqs}))


def test_main_finals_fold_in(tmp_path, monkeypatch):
    import consolidate_subsets

    build_tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["consolidate_subsets.py",
                                      "--run", "lcdm_tt_beta3e-4",
                                      "--emit-finalists"])
    assert consolidate_subsets.main() == 0   # emits the finals tasks.tsv

    run_dir = tmp_path / "results/lcdm_tt_beta3e-4"
    finals = run_dir / "hpsweep_subsets_v1_finals"
    # full-protocol all-6 reference (5 seeds)
    _write_family_reports(run_dir / "allparams", None, 0,
                          {s: [(8, 1.00 + 0.005 * s)] for s in range(5)})
    # finalist reruns: 2-input within 1 SE of everything, 1-input far below,
    # 4-input equal to the reference
    _write_family_reports(finals, "c18_S-tau-As", 0,
                          {s: [(5, 1.00 + 0.004 * s)] for s in range(5)})
    _write_family_reports(finals, "c04_S-As", 0,
                          {s: [(1, 0.34 + 0.004 * s)] for s in range(5)})
    _write_family_reports(finals, "c44_S-ob-oc-tau-As", 0,
                          {s: [(7, 1.00 + 0.004 * s)] for s in range(5)})

    monkeypatch.setattr(sys, "argv", ["consolidate_subsets.py",
                                      "--run", "lcdm_tt_beta3e-4"])
    assert consolidate_subsets.main() == 0
    payload = json.loads(
        (tmp_path / "experiments/subset_selection_lcdm_tt_beta3e-4.json")
        .read_text())
    fin = payload["finals"]
    assert fin["coverage"]["n_reports"] == 15
    z0 = fin["latents"]["z0"]
    assert z0["s_star"]["inputs"] == ["tau", "A_s"]
    by = {e["config_id"]: e for e in z0["entries"]}
    assert not by["c04_S-As"]["minimal"]
    assert by["c18_S-tau-As"]["minimal"] and by["allparams"]["minimal"]
    # z0 is a shape latent for this run (amp_idx=2); screen fixture has the
    # 2-input subset > 1 SE below all-6 per seed -> not screen-recurrent
    assert not z0["screen_recurrence"]["recurrent"]
    assert fin["gate_G2"]["per_latent"]["z0"]["verdict"].startswith(
        "ATTENTION")
    assert fin["clusters"]["skipped"]           # no knee JSON in tmp tree
    md = (tmp_path /
          "experiments/subset_selection_lcdm_tt_beta3e-4.md").read_text()
    assert "# 4b finals" in md and "# Gate G2" in md and "S\\*" in md
