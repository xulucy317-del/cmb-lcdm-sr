"""Phase-2 semantic recurrence: family knees, per-family R_SR, canonical pick."""
import json
import pathlib
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

from semantic_recurrence import (  # noqa: E402
    family_knee,
    latent_recurrence,
)

# plausible prior box in the sampled basis (omega_b, omega_cdm, H0, tau,
# ln10As, n_s) — only used to synthesise anchors for the equivalence tests
MID = np.array([0.022, 0.115, 71.0, 0.07, 3.04, 0.965])
HALF = np.array([0.002, 0.015, 9.0, 0.04, 0.14, 0.025])


def anchors(n=256, seed=0):
    rng = np.random.default_rng(seed)
    return MID + (2.0 * rng.random((n, 6)) - 1.0) * HALF


def front(rows, maxsize):
    return {"rows": rows, "maxsize": maxsize}


TAYLOR = "A_s*(tau - 0.6)"
EXPFORM = "A_s*exp(-2*tau)"
LOGFORM = "2*tau - log(A_s)"


def fixture():
    """Two families; amplitude family split across string variants + n_s."""
    ms10 = {0: front([(1, 0.10, 0.01, "tau"),            # below floor
                      (3, 0.50, 0.01, "n_s"),
                      (4, 0.92, 0.01, TAYLOR)], 6),
            1: front([(1, 0.12, 0.01, "A_s"),
                      (3, 0.48, 0.01, "n_s**2"),
                      (5, 0.92, 0.01, EXPFORM)], 6)}
    ms20 = {0: front([(1, 0.20, 0.01, "tau"),
                      (7, 0.95, 0.01, LOGFORM)], 8),
            1: front([(1, 0.20, 0.01, "tau"),
                      (7, 0.95, 0.01, "-log(A_s) + 2*tau")], 8)}
    return {"allparams_ms10": ms10, "allparams": ms20}


def test_family_knee_hand_numbers():
    kn = family_knee(fixture()["allparams_ms10"])
    assert kn["n_seeds"] == 2
    # equal per-seed maxima -> SE and SD 0, knee level = the plateau itself
    assert np.isclose(kn["plat"], 0.92) and kn["se"] == 0.0
    assert kn["sd"] == 0.0 and np.isclose(kn["knee_mi_seed"], kn["knee_mi"])
    # pooled envelope: c4 = (0.92 + 0.48)/2, first reaches 0.92 at c5
    assert kn["c_star"] == 5
    assert np.isclose(kn["knee_mi"], 0.92)


def test_latent_recurrence_clusters_and_rsr():
    lat = latent_recurrence(fixture(), plat_ref=1.0, anchors=anchors(),
                            half=HALF, eta_floor=0.25)
    assert lat["n_unparseable"] == 0
    # Taylor/exp/log variants pool into ONE cluster; n_s forms into another;
    # sub-floor rows (tau, A_s at mi ~0.1) are excluded entirely
    assert len(lat["clusters"]) == 2
    amp = lat["clusters"][0]
    assert amp["r_sr_headline"] == 1.0
    assert amp["n_forms"] == 4 and amp["textbook_any"]
    # representative = simplest member (Taylor at c4)
    assert amp["representative"] == TAYLOR and amp["rep_complexity"] == 4
    assert amp["rep_support"] == ["tau", "ln10As"]
    # ms10 family: both seeds hit at knee level, but via DIFFERENT strings —
    # semantic recurrence 2/2, best exact-string recurrence 1/2
    r10 = amp["r_sr"]["allparams_ms10"]
    assert (r10["hits"], r10["n_seeds"]) == (2, 2)
    assert np.isclose(r10["best_exact_r"], 0.5)
    # ms20 family: same canonical string both seeds -> exact pooling ties
    r20 = amp["r_sr"]["allparams"]
    assert (r20["hits"], r20["n_seeds"]) == (2, 2)
    assert np.isclose(r20["best_exact_r"], 0.5)  # two spellings, one each
    # all four amplitude variants are directly pairwise equivalent
    assert amp["rep_linked"] == 1.0 and amp["pair_cohesion"] == 1.0
    # n_s cluster never reaches knee level in either family
    ns = lat["clusters"][1]
    assert ns["r_sr_headline"] == 0.0
    assert not ns["textbook_any"]
    assert lat["canonical_cluster"] == amp["cluster"]


def test_cohesion_flags_transitive_chaining():
    # gradient directions e_tau, e_tau + 0.2*e_ns, e_tau + 0.4*e_ns in
    # u-coordinates: adjacent pairs pass d_grad <= 0.05 (cos 0.981, 0.983)
    # but the extremes fail (cos 0.928) — union-find chains all three
    a = "tau"
    b = f"tau + {0.2 * HALF[3] / HALF[5]:.6f}*(n_s - {MID[5]})"
    c = f"tau + {0.4 * HALF[3] / HALF[5]:.6f}*(n_s - {MID[5]})"
    fams = {"allparams": {0: front([(2, 0.9, 0.01, a), (4, 0.85, 0.01, b),
                                    (6, 0.8, 0.01, c)], 8)}}
    lat = latent_recurrence(fams, plat_ref=1.0, anchors=anchors(2048),
                            half=HALF)
    assert len(lat["clusters"]) == 1
    cl = lat["clusters"][0]
    assert cl["n_forms"] == 3 and cl["representative"] == a
    # rep links to b only; of the 3 member pairs exactly (a,b) and (b,c) pass
    assert np.isclose(cl["rep_linked"], 0.5)
    assert np.isclose(cl["pair_cohesion"], 2 / 3)


def test_representative_skips_outlier_stub():
    # angles 0/16/30/44 deg in the (u_tau, u_ns) gradient plane: the c3 stub
    # links only to B (16 deg), while B links to both S and C — the majority
    # rule must elect B, not the simplest-but-unrepresentative stub
    k = 1.6  # HALF[3]/HALF[5]
    s = "tau"
    b = f"tau + {0.2867 * k:.6f}*(n_s - {MID[5]})"
    c = f"tau + {0.5774 * k:.6f}*(n_s - {MID[5]})"
    d = f"tau + {0.9657 * k:.6f}*(n_s - {MID[5]})"
    fams = {"allparams": {0: front([(3, 0.95, 0.01, s), (5, 0.9, 0.01, b),
                                    (6, 0.85, 0.01, c),
                                    (7, 0.8, 0.01, d)], 8)}}
    lat = latent_recurrence(fams, plat_ref=1.0, anchors=anchors(2048),
                            half=HALF)
    assert len(lat["clusters"]) == 1
    cl = lat["clusters"][0]
    assert cl["representative"] == b and cl["rep_complexity"] == 5


def test_rsr_uses_seed_level_sd_tolerance():
    # per-seed maxima 1.0 / 0.86: SD tolerance (0.099) admits the weaker
    # seed decisively, where the SE-of-mean rule (0.07) would sit exactly on
    # the boundary — the artifact the documented deviation removes
    fams = {"allparams": {0: front([(5, 1.00, 0.01, EXPFORM)], 8),
                          1: front([(5, 0.86, 0.01, EXPFORM)], 8)}}
    lat = latent_recurrence(fams, plat_ref=1.0, anchors=anchors(), half=HALF)
    r = lat["clusters"][0]["r_sr"]["allparams"]
    assert (r["hits"], r["n_seeds"]) == (2, 2) and r["r"] == 1.0


def test_unparseable_forms_dropped_not_fatal():
    fams = {"allparams": {0: front([(3, 0.9, 0.01, "garbage((("),
                                    (5, 0.8, 0.01, EXPFORM)], 8)}}
    lat = latent_recurrence(fams, plat_ref=1.0, anchors=anchors(), half=HALF)
    assert lat["n_unparseable"] == 1
    assert len(lat["clusters"]) == 1
    assert lat["clusters"][0]["representative"] == EXPFORM


def test_all_nan_form_stays_singleton():
    # sqrt of a strictly negative quantity on the box -> all-NaN values;
    # only canonical identity could merge it, so it must stay separate
    bad = "log(-omega_b)"
    fams = {"allparams": {0: front([(4, 0.9, 0.01, EXPFORM),
                                    (6, 0.85, 0.01, bad)], 8)}}
    lat = latent_recurrence(fams, plat_ref=1.0, anchors=anchors(), half=HALF)
    reps = {c["representative"] for c in lat["clusters"]}
    assert reps == {EXPFORM, bad}
    nanc = next(c for c in lat["clusters"] if c["representative"] == bad)
    assert nanc["finite_frac_min"] == 0.0


def test_main_end_to_end(tmp_path, monkeypatch):
    import semantic_recurrence

    run = "toy"
    base = tmp_path / "results" / run
    for fam, runs in fixture().items():
        for s, f in runs.items():
            d = base / fam / f"z0_seed{s}"
            d.mkdir(parents=True)
            eqs = [{"complexity": c, "mi_val": mi, "mi_val_err": err,
                    "expression_simplified": e, "expression_raw": e,
                    "index": i} for i, (c, mi, err, e) in enumerate(f["rows"])]
            (d / "report.json").write_text(json.dumps(
                {"all_equations": eqs, "latent_index": 0,
                 "pysr_kwargs": {"maxsize": f["maxsize"],
                                 "random_state": s}}))
    knee = {"latents": {"z0": {"plateau": {"mi_plat": 1.0}}}}
    (tmp_path / "knee.json").write_text(json.dumps(knee))

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", [
        "semantic_recurrence.py", "--run", run,
        "--subdirs", "allparams", "allparams_ms10",
        "--knee-json", "knee.json",
        "--dataset-dir", str(REPO / "data"),
        "--out", "experiments/sem_toy"])
    assert semantic_recurrence.main() == 0

    payload = json.loads((tmp_path / "experiments/sem_toy.json").read_text())
    z0 = payload["latents"]["z0"]
    assert z0["canonical_cluster"] == z0["clusters"][0]["cluster"]
    assert z0["clusters"][0]["r_sr_headline"] == 1.0
    md = (tmp_path / "experiments/sem_toy.md").read_text()
    assert "Canonical coordinate" in md and "exact 1/2" in md
