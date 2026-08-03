"""Phase-1 knee & plateau readout: envelopes, plateau selection, eta forms."""
import json
import pathlib
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

from knee_readout import (  # noqa: E402
    classify,
    discover_families,
    latent_readout,
    pool_family,
    seed_envelope,
)


def front(rows, maxsize):
    return {"rows": rows, "maxsize": maxsize}


def write_report(dirpath, rows, maxsize, latent, seed):
    dirpath.mkdir(parents=True)
    eqs = [{"complexity": c, "mi_val": mi, "mi_val_err": err,
            "expression_simplified": expr, "expression_raw": expr, "index": i}
           for i, (c, mi, err, expr) in enumerate(rows)]
    eqs.append({"complexity": 99, "mi_val": None, "mi_val_err": None,
                "expression_simplified": "dropped", "index": len(eqs)})
    (dirpath / "report.json").write_text(json.dumps({
        "all_equations": eqs, "latent_index": latent,
        "pysr_kwargs": {"maxsize": maxsize, "random_state": seed}}))


# Latent-0 fixture used across tests: plateau family per-seed maxima
# [1.0, 1.1, 0.9] -> plat 1.0, SE = std(ddof=1)/sqrt(3) = 0.0577.
def latent0_families():
    ms6 = {0: front([(1, 0.2, 0.01, "A_s"), (3, 0.5, 0.01, "A_s*tau"),
                     (5, 0.55, 0.01, "A_s*tau + n_s")], 6),
           1: front([(1, 0.3, 0.01, "tau"), (3, 0.45, 0.01, "A_s*(tau - 1)"),
                     (6, 0.5, 0.01, "A_s*(tau - 1) + H0")], 6)}
    ms8 = {0: front([(1, 0.2, 0.01, "A_s"), (4, 0.8, 0.02, "A_s*(tau - 0.6)"),
                     (8, 1.0, 0.02, "A_s*(tau - 0.6)*n_s")], 8),
           1: front([(1, 0.25, 0.01, "tau"), (4, 0.7, 0.02, "A_s*tau"),
                     (8, 1.1, 0.02, "A_s*exp(-2*tau) + omega_b")], 8),
           2: front([(1, 0.15, 0.01, "A_s"), (4, 0.75, 0.02, "A_s*tau"),
                     (8, 0.9, 0.02, "A_s*(tau - 0.55)*H0")], 8)}
    return {"allparams": ms6, "allparams_ms8": ms8}


def test_seed_envelope_cummax_and_extension():
    grid = np.arange(1, 11)
    env = seed_envelope([(3, 0.5, 0.0, "a"), (1, 0.2, 0.0, "b"),
                         (5, 0.55, 0.0, "c")], grid)
    assert np.allclose(env, [0.2, 0.2, 0.5, 0.5] + [0.55] * 6)
    # non-monotone front: later, worse rows never lower the envelope
    env = seed_envelope([(1, 0.5, 0.0, "a"), (2, 0.3, 0.0, "b")], grid)
    assert np.allclose(env, [0.5] * 10)
    # NaN below the front's smallest complexity
    env = seed_envelope([(2, 0.4, 0.0, "a")], grid)
    assert np.isnan(env[0]) and np.allclose(env[1:], 0.4)


def test_pool_family_mean_se_counts():
    grid = np.arange(1, 4)
    pooled = pool_family({0: np.array([1.0, 2.0, 3.0]),
                          1: np.array([3.0, np.nan, 5.0])}, grid)
    assert np.allclose(pooled["mean"], [2.0, 2.0, 4.0])
    assert list(pooled["n"]) == [2, 1, 2]
    assert np.allclose(pooled["se"][[0, 2]], [1.0, 1.0])
    assert np.isnan(pooled["se"][1])


def test_latent_readout_plateau_knee_and_forms():
    r = latent_readout(latent0_families(), [0.90, 0.95, 0.99], simple_c=10)
    p = r["plateau"]
    assert p["family"] == "allparams_ms8" and p["maxsize"] == 8
    assert np.isclose(p["mi_plat"], 1.0)
    assert np.isclose(p["se"], np.std([1.0, 1.1, 0.9], ddof=1) / np.sqrt(3))
    # combined envelope: ms6 mean 0.25 at c1-2, 0.475 at c3; ms8 0.75 at c4-7,
    # 1.0 from c8; one-SE knee and all eta crossings land at c=8
    assert r["c_star"] == 8
    assert np.isclose(r["mi_at_c_star"], 1.0)
    assert np.isclose(r["mi_at_c10"], 1.0)
    assert all(c == 8 for c in r["eta_crossings"].values())
    assert r["classification"] == "single dominant knee"
    # simplest single form >= 0.9*plat: both c8 rows qualify, tie-break by MI
    f90 = r["eta_forms"]["0.90"]
    assert f90["complexity"] == 8 and np.isclose(f90["mi_val"], 1.1)
    assert f90["family"] == "allparams_ms8" and f90["seed"] == 1
    assert f90["support"] == ["omega_b", "tau", "A_s"]
    assert np.isclose(f90["eta_achieved"], 1.1)
    # best form in the simple regime (all fixture rows sit at c <= 10)
    sf = r["simple_form"]
    assert sf["complexity"] == 8 and np.isclose(sf["mi_val"], 1.1)
    assert sf["support"] == ["omega_b", "tau", "A_s"]


def test_plateau_family_tiebreak_prefers_non_sweep():
    fams = {"hpsweep_hp_v1/c07_ms30":
                {s: front([(1, 0.3, 0.0, "A_s"), (8, 2.0, 0.0, "A_s*tau")], 8)
                 for s in range(3)},
            "allparams_ms8":
                {s: front([(1, 0.2, 0.0, "A_s"), (8, 1.5, 0.0, "A_s*tau")], 8)
                 for s in range(3)}}
    r = latent_readout(fams, [0.90], simple_c=10)
    # equal maxsize and seed count -> canonical namespace, despite lower MI
    assert r["plateau"]["family"] == "allparams_ms8"
    # the sweep family still feeds the combined envelope
    assert np.isclose(r["mi_at_c10"], 2.0)


def test_classify_branches():
    assert classify(c90=4, c_star=7, simple_c=10) == "single dominant knee"
    assert classify(c90=8, c_star=17, simple_c=10) == "knee + slow climb"
    assert classify(c90=14, c_star=18, simple_c=10) == "no knee (diffuse)"
    assert classify(c90=None, c_star=None, simple_c=10) == "no knee (diffuse)"


def test_discover_families_skips_controls_and_scans_sweep(tmp_path):
    base = tmp_path / "results" / "toy"
    rows = [(1, 0.2, 0.01, "A_s")]
    write_report(base / "allparams" / "z0_seed0", rows, 20, 0, 0)
    write_report(base / "allparams" / "z0_seed1", rows, 20, 0, 1)
    write_report(base / "allparams" / "shuffled_z0_s0", rows, 20, 0, 0)
    write_report(base / "allparams" / "pooled_z0", rows, 20, 0, 0)
    write_report(base / "hpsweep_hp_v1" / "c07_ms30" / "z0_seed0", rows, 30,
                 0, 0)
    fams = discover_families(tmp_path / "results", "toy",
                             ["allparams", "hpsweep_hp_v1", "absent"])
    assert sorted(fams) == ["allparams", "hpsweep_hp_v1/c07_ms30"]
    assert sorted(fams["allparams"][0]) == [0, 1]
    assert sorted(fams["hpsweep_hp_v1/c07_ms30"][0]) == [0]


def test_main_end_to_end(tmp_path, monkeypatch):
    import knee_readout

    base = tmp_path / "results" / "toy"
    for fam, sub in [("allparams", latent0_families()["allparams"]),
                     ("allparams_ms8", latent0_families()["allparams_ms8"])]:
        for s, f in sub.items():
            write_report(base / fam / f"z0_seed{s}", f["rows"], f["maxsize"],
                         0, s)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv",
                        ["knee_readout.py", "--run", "toy",
                         "--subdirs", "allparams", "allparams_ms8",
                         "--out", "experiments/knee_toy"])
    assert knee_readout.main() == 0

    payload = json.loads((tmp_path / "experiments/knee_toy.json").read_text())
    z0 = payload["latents"]["z0"]
    assert z0["c_star"] == 8 and z0["classification"] == "single dominant knee"
    assert np.isclose(z0["plateau"]["mi_plat"], 1.0)
    assert set(z0["envelopes"]) == {"allparams", "allparams_ms8"}
    assert np.isclose(z0["combined_envelope"]["max_of_means"][7], 1.0)
    md = (tmp_path / "experiments/knee_toy.md").read_text()
    assert "| z0 |" in md and "single dominant knee" in md
    assert (tmp_path / "experiments/knee_toy_envelopes.png").exists()


def test_main_fails_cleanly_on_empty(tmp_path, monkeypatch):
    import knee_readout

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["knee_readout.py", "--run", "nothing"])
    assert knee_readout.main() == 1
