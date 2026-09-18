"""scripts/check_inputs.py on a synthetic checkout: manifest round trip,
mismatch detection, and the capability summary."""
import json
import os
import pathlib
import subprocess
import sys
import zipfile

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "check_inputs.py"
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))


def _write_npz(path, **arrays):
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, **arrays)


def _fake_checkout(tmp_path):
    """Every file the checker looks for, tiny, plus one shard dir and results."""
    import check_inputs as ci
    root = tmp_path / "repo"
    for rel in ci.REPO_FILES + ci.CACHE_FILES + ci.derived_files() + ci.ols_residual_files():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(rel.encode())
    shards = tmp_path / "shards"
    for d in ci.SHARD_DIRS:
        for i in range(ci.N_SHARDS):
            _write_npz(shards / d / f"spectra_{i:05d}.npz", spectra=np.zeros((2, 3), np.float32))
    for run in ci.RUNS:
        for campaign, n in (("allparams", 3), ("residual_sr", 2)):
            for i in range(n):
                p = root / "results" / run / campaign / f"z0_seed{i}" / "report.json"
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json.dumps({"run": run, "campaign": campaign, "seed": i}))
    return root, shards


def _run(root, *args, shards=None):
    env = dict(os.environ, CMB_LCDM_SR_REPO=str(root))
    env.pop("SHARDS_ROOT", None)
    cmd = [sys.executable, str(SCRIPT), *args]
    if shards is not None:
        cmd += ["--shards-root", str(shards)]
    return subprocess.run(cmd, env=env, text=True, capture_output=True)


def test_manifest_round_trip_is_clean(tmp_path):
    root, shards = _fake_checkout(tmp_path)
    proc = _run(root, "--write-manifest", shards=shards)
    assert proc.returncode == 0, proc.stderr
    manifest = json.loads((root / "data" / "inputs_manifest.json").read_text())
    assert len(manifest["files"]) == 14 + 4 + 22 + 13 + 200
    assert set(manifest["results"]) == {f"{run}/{c}" for run in ("lcdm_tt_beta3e-4", "lcdm_tt_ee_lowl")
                                        for c in ("allparams", "residual_sr")}
    assert manifest["results"]["lcdm_tt_beta3e-4/allparams"]["n_reports"] == 3

    proc = _run(root, "--full", shards=shards)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    out = proc.stdout
    assert "MISMATCH" not in out and "missing" not in out.split("what this checkout can run")[0]
    assert "SR searches on the latents (stage 1) ........... yes" in out
    assert "audits and campaigns on the residuals (phases 5-8, stage 2) yes" in out
    assert "stage-3 search on the OLS residual (EE z0, z4) .. yes" in out
    assert "encoder pass, templates, stage-4 attribution ... yes" in out
    assert "4/4 campaigns present" in out
    assert "canonical hashes from data/inputs_manifest.json" in out


def test_mismatch_missing_and_incomplete_are_reported(tmp_path):
    root, shards = _fake_checkout(tmp_path)
    assert _run(root, "--write-manifest", shards=shards).returncode == 0
    # a cache whose bytes differ from the canonical ones
    (root / "models/lcdm_tt_beta3e-4/analysis/encoder_means_test.npy").write_bytes(b"different")
    # the EE caches gone entirely
    for kind in ("means", "logvars"):
        (root / f"models/lcdm_tt_ee_lowl/analysis/encoder_{kind}_test.npy").unlink()
    # one campaign lost a report, one shard truncated
    (root / "results/lcdm_tt_ee_lowl/residual_sr/z0_seed1/report.json").unlink()
    (shards / "shards_global_lhs/spectra_00099.npz").write_bytes(b"PK\x03\x04 truncated")

    proc = _run(root, shards=shards)
    assert proc.returncode == 1
    out = proc.stdout
    assert "MISMATCH" in out and "encoder_means_test.npy" in out
    assert "missing" in out
    assert "NO — encoder caches missing" in out
    assert "residual caches: 22/22 present" in out
    assert "CORRUPT" in out and "NO — spectra shards corrupt" in out
    assert "incomplete (1/2 reports)" in out
    assert "3/4 campaigns present" in out
    assert "1 problem(s)" in proc.stderr or "2 problem(s)" in proc.stderr


def test_falls_back_to_the_pinned_state_file_without_a_manifest(tmp_path):
    root, _ = _fake_checkout(tmp_path)
    state = root / "experiments" / "mse_one_stage_state_csd3.json"
    state.parent.mkdir(parents=True)
    import check_inputs as ci
    theta = root / "data" / "theta.npy"
    state.write_text(json.dumps({"inputs_sha256": {"data/theta.npy": ci.sha256(theta)}}))
    proc = _run(root)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "canonical    " in proc.stdout and "data/theta.npy" in proc.stdout
    assert "canonical hashes from experiments/mse_one_stage_state_csd3.json" in proc.stdout
    assert "spectra shards: not checked" in proc.stdout
