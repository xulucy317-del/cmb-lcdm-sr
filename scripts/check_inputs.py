"""What can this checkout run? Check every input the pipeline needs.

The repository commits the code, the two checkpoints, the parameter table and
the consolidated results, but three kinds of input are too large or too
derived to live in git. This script reports which are present, verifies the
ones that have a canonical sha256, and says what each missing group blocks:

  repo            data/, models/<run>/{best_model.pt,scaler.npz,config_used.json}
                  -> always present in a clone; verified against pinned hashes
  encoder caches  models/<run>/analysis/encoder_{means,logvars}_test.npy
                  -> every SR search and audit starts from these (stages 1-3,
                     the MSE/precision campaigns, most figures)
  residual caches models/<run>/analysis/{residual,f1hat}_z<k>_v1.npy (22 files)
                  -> the entry points of phases 5-8 and stages 2-3; committed
                     too, because rebuilding them (sufficiency_audit.py,
                     build_f1hat_cache.py) needs the raw stage-1 fronts.
                     residual_ols_z<k>_v1.npy (+ residual_ols_v1_fit.json) are
                     the stage-3 targets, built only where that search ran
                     (EE z0, z4) — reported when present
  shards          <shards-root>/shards_global_lhs{,_ee_lowl}/spectra_*.npz
                  -> only the encoder pass, spectral_templates.py and the
                     stage-4 encoder attribution read the spectra
  results         results/<run>/<campaign>/**/report.json
                  -> only needed to re-consolidate the published campaigns
                     without re-running their searches

Canonical hashes come from data/inputs_manifest.json when it exists (written
with --write-manifest on a machine that holds everything), otherwise from the
hashes pinned in experiments/mse_one_stage_state_csd3.json.

    python scripts/check_inputs.py                      # report + verify
    python scripts/check_inputs.py --shards-root /path  # also check the shards
    python scripts/check_inputs.py --full               # hash every shard too
    python scripts/check_inputs.py --write-manifest --shards-root /path
                                                        # maintainers: record
                                                        # what a complete tree
                                                        # looks like

Exit status is 0 unless a file that is present does not match its canonical
hash, or a file that ships with the repository is missing.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import platform
import sys
import zipfile
from pathlib import Path

REPO = Path(os.environ.get("CMB_LCDM_SR_REPO", Path(__file__).resolve().parents[1]))
MANIFEST_DEFAULT = REPO / "data" / "inputs_manifest.json"
STATE_FALLBACK = REPO / "experiments" / "mse_one_stage_state_csd3.json"

RUNS = {"lcdm_tt_beta3e-4": 5, "lcdm_tt_ee_lowl": 6}
SHARD_DIRS = ("shards_global_lhs", "shards_global_lhs_ee_lowl")
N_SHARDS = 100

REPO_FILES = [
    "data/theta.npy", "data/splits_v1.npz", "data/meta.json",
    "data/sham_v1.json", "data/sham_v1_ob.npy", "data/sham_v1_tau.npy", "data/sham_v1_ns.npy",
    "data/spectral_templates_v1.npz",
] + [f"models/{run}/{name}" for run in RUNS
     for name in ("best_model.pt", "scaler.npz", "config_used.json")]

CACHE_FILES = [f"models/{run}/analysis/encoder_{kind}_test.npy"
               for run in RUNS for kind in ("means", "logvars")]


def derived_files() -> list[str]:
    """The 22 residual caches every later phase starts from (all hash-pinned)."""
    out = []
    for run, n_latents in RUNS.items():
        for k in range(n_latents):
            for stem in ("residual", "f1hat"):
                out.append(f"models/{run}/analysis/{stem}_z{k}_v1.npy")
    return out


def ols_residual_files() -> list[str]:
    """Stage-3 targets; exist only for the latents that search ran on."""
    out = [f"models/{run}/analysis/residual_ols_v1_fit.json" for run in RUNS]
    for run, n_latents in RUNS.items():
        for k in range(n_latents):
            out.append(f"models/{run}/analysis/residual_ols_z{k}_v1.npy")
    return out


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} GB"


# ---------------------------------------------------------------- canonical

def load_canonical(manifest_path: Path) -> tuple[dict, str]:
    """{relpath: sha256} for individually pinned files, plus the source name."""
    if manifest_path.is_file():
        payload = json.loads(manifest_path.read_text())
        pinned = {rel: entry["sha256"] for rel, entry in payload.get("files", {}).items()}
        return pinned, str(manifest_path.relative_to(REPO)) if manifest_path.is_relative_to(REPO) else str(manifest_path)
    if STATE_FALLBACK.is_file():
        payload = json.loads(STATE_FALLBACK.read_text())
        pinned = dict(payload.get("inputs_sha256", {}))
        pinned.update(payload.get("baseline_reports_sha256", {}))
        return pinned, str(STATE_FALLBACK.relative_to(REPO))
    return {}, "(no canonical hashes available)"


def load_manifest(manifest_path: Path) -> dict | None:
    return json.loads(manifest_path.read_text()) if manifest_path.is_file() else None


# ------------------------------------------------------------------ checks

def check_file(rel: str, pinned: dict, hash_it: bool = True) -> dict:
    path = REPO / rel
    if not path.is_file():
        return {"path": rel, "status": "missing"}
    entry = {"path": rel, "bytes": path.stat().st_size}
    if hash_it:
        digest = sha256(path)
        entry["sha256"] = digest
        want = pinned.get(rel)
        if want is None:
            entry["status"] = "present"
        elif want == digest:
            entry["status"] = "canonical"
        else:
            entry["status"] = "MISMATCH"
            entry["expected"] = want
    else:
        entry["status"] = "present"
    return entry


def check_shards(shards_root: Path | None, pinned: dict, full: bool) -> dict:
    if shards_root is None:
        return {"status": "not checked", "detail": "pass --shards-root to check"}
    report = {"status": "ok", "channels": {}}
    for d in SHARD_DIRS:
        directory = shards_root / d
        files = sorted(glob.glob(str(directory / "spectra_*.npz")))
        info = {"dir": str(directory), "n_files": len(files)}
        if len(files) != N_SHARDS:
            info["status"] = "missing" if not files else f"incomplete ({len(files)}/{N_SHARDS})"
            report["status"] = "incomplete"
        else:
            probe = files if full else [files[0], files[-1]]
            bad = []
            for f in probe:
                try:
                    with zipfile.ZipFile(f) as z:
                        if z.testzip() is not None:
                            bad.append(os.path.basename(f))
                except zipfile.BadZipFile:
                    bad.append(os.path.basename(f))
            mismatched = []
            if full:
                for f in files:
                    rel = f"shards/{d}/{os.path.basename(f)}"
                    want = pinned.get(rel)
                    if want is not None and sha256(Path(f)) != want:
                        mismatched.append(os.path.basename(f))
            if bad:
                info["status"] = f"CORRUPT ({len(bad)} of {len(probe)} probed shards fail zip test: {bad[:3]})"
                report["status"] = "corrupt"
            elif mismatched:
                info["status"] = f"MISMATCH ({len(mismatched)} shards differ from the manifest)"
                report["status"] = "mismatch"
            else:
                info["status"] = "ok" + (" (all hashed)" if full else " (first/last shard zip-tested; --full hashes all)")
        report["channels"][d] = info
    return report


def campaign_reports() -> dict[str, list[Path]]:
    """{'<run>/<campaign>': [report.json, ...]} for everything under results/."""
    out: dict[str, list[Path]] = {}
    root = REPO / "results"
    if not root.is_dir():
        return out
    for run in RUNS:
        run_dir = root / run
        if not run_dir.is_dir():
            continue
        for path in sorted(run_dir.rglob("report.json")):
            rel = path.relative_to(run_dir)
            campaign = rel.parts[0] if len(rel.parts) > 1 else "(root)"
            out.setdefault(f"{run}/{campaign}", []).append(path)
    return out


def aggregate_hash(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(str(p.relative_to(REPO)).encode())
        h.update(b"\0")
        h.update(sha256(p).encode())
        h.update(b"\n")
    return h.hexdigest()


def check_results(manifest: dict | None, full: bool) -> dict:
    found = campaign_reports()
    expected = (manifest or {}).get("results", {})
    rows = {}
    for key in sorted(set(found) | set(expected)):
        have = found.get(key, [])
        want = expected.get(key)
        row = {"n_reports": len(have)}
        if want is None:
            row["status"] = "present (not in manifest)" if have else "missing"
        elif not have:
            row["status"] = f"missing ({want['n_reports']} reports expected)"
        elif len(have) != want["n_reports"]:
            row["status"] = f"incomplete ({len(have)}/{want['n_reports']} reports)"
        elif full:
            row["status"] = "canonical" if aggregate_hash(have) == want["sha256_aggregate"] else "MISMATCH"
        else:
            row["status"] = "complete (count matches; --full verifies content)"
        rows[key] = row
    return rows


# ----------------------------------------------------------------- manifest

def write_manifest(out: Path, shards_root: Path | None) -> None:
    files = {}
    groups = [(REPO_FILES, "repo"), (CACHE_FILES, "encoder caches"),
              (derived_files(), "residual caches"), (ols_residual_files(), "ols residual caches")]
    for rels, group in groups:
        for rel in rels:
            path = REPO / rel
            if path.is_file():
                files[rel] = {"sha256": sha256(path), "bytes": path.stat().st_size, "group": group}
    if shards_root is not None:
        for d in SHARD_DIRS:
            for f in sorted(glob.glob(str(shards_root / d / "spectra_*.npz"))):
                rel = f"shards/{d}/{os.path.basename(f)}"
                files[rel] = {"sha256": sha256(Path(f)), "bytes": os.path.getsize(f), "group": "shards"}
    results = {}
    for key, paths in campaign_reports().items():
        results[key] = {"n_reports": len(paths), "sha256_aggregate": aggregate_hash(paths),
                        "bytes": sum(p.stat().st_size for p in paths)}
    payload = {
        "schema_version": 1,
        "kind": "cmb_lcdm_sr_inputs_manifest",
        "generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": platform.node(),
        "note": ("sha256 of every input the pipeline reads beyond the committed code. "
                 "'shards/<dir>/<file>' entries are relative to the shards root; "
                 "'results' entries hash each campaign's report.json files as one aggregate "
                 "(sorted path\\0sha256\\n per file). Verify with scripts/check_inputs.py."),
        "files": files,
        "results": results,
    }
    out.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    print(f"[manifest] wrote {out}: {len(files)} files, {len(results)} result campaigns")


# --------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--shards-root", default=os.environ.get("SHARDS_ROOT"),
                    help="directory holding shards_global_lhs/ and shards_global_lhs_ee_lowl/ "
                         "(default: $SHARDS_ROOT)")
    ap.add_argument("--manifest", default=str(MANIFEST_DEFAULT))
    ap.add_argument("--full", action="store_true",
                    help="hash every shard and every campaign's reports, not just probe them")
    ap.add_argument("--write-manifest", action="store_true",
                    help="record the sha256 of everything present as the canonical manifest")
    args = ap.parse_args()
    manifest_path = Path(args.manifest)
    shards_root = Path(args.shards_root).expanduser() if args.shards_root else None

    if args.write_manifest:
        write_manifest(manifest_path, shards_root)
        return 0

    pinned, source = load_canonical(manifest_path)
    manifest = load_manifest(manifest_path)
    problems = 0

    def show(group: str, entries: list[dict]) -> None:
        print(f"\n{group}")
        for e in entries:
            size = f"{human(e['bytes']):>9}" if "bytes" in e else f"{'':>9}"
            print(f"  {e['status']:<10} {size}  {e['path']}")

    repo = [check_file(rel, pinned) for rel in REPO_FILES]
    show("repo files (committed)", repo)
    problems += sum(e["status"] in ("missing", "MISMATCH") for e in repo)

    caches = [check_file(rel, pinned) for rel in CACHE_FILES]
    show("encoder caches [checklist A1] (models/<run>/analysis/)", caches)
    problems += sum(e["status"] == "MISMATCH" for e in caches)

    derived = [check_file(rel, pinned) for rel in derived_files()]
    n_derived = sum(e["status"] != "missing" for e in derived)
    bad_derived = [e for e in derived if e["status"] == "MISMATCH"]
    n_pinned = sum(rel in pinned for rel in derived_files())
    n_canonical = sum(e["status"] == "canonical" for e in derived)
    print(f"\nresidual caches [checklist A2]: {n_derived}/{len(derived)} present"
          + (f", {len(bad_derived)} MISMATCH" if bad_derived else "")
          + (f", {n_canonical}/{n_pinned} canonical" if n_pinned else "")
          + " (residual_z*, f1hat_z*: rebuilt only from the raw fronts)")
    for e in bad_derived:
        print(f"  MISMATCH   {e['path']}")
    problems += len(bad_derived)

    ols = [check_file(rel, pinned) for rel in ols_residual_files()]
    ols_present = [e for e in ols if e["status"] != "missing"]
    bad_ols = [e for e in ols if e["status"] == "MISMATCH"]
    print(f"OLS residual caches [checklist A2.3]: {len(ols_present)} present"
          + (f", {len(bad_ols)} MISMATCH" if bad_ols else "")
          + " (stage-3 targets; built only for the latents that search ran on — EE z0, z4 at least)")
    for e in ols_present:
        print(f"  {e['status']:<10} {human(e['bytes']):>9}  {e['path']}")
    problems += len(bad_ols)

    shards = check_shards(shards_root, pinned, args.full)
    print(f"\nspectra shards [checklist C]: {shards['status']}" + (f" — {shards['detail']}" if "detail" in shards else ""))
    for d, info in shards.get("channels", {}).items():
        print(f"  {info['status']:<10} {info['n_files']:>3} files  {info['dir']}")
    problems += shards["status"] in ("corrupt", "mismatch")

    results = check_results(manifest, args.full)
    if results:
        print("\nraw results [checklist D] (results/<run>/<campaign>):")
        for key, row in results.items():
            print(f"  {row['status']:<48} {row['n_reports']:>5} reports  {key}")
    else:
        print("\nraw results [checklist D]: none under results/ (only needed to re-consolidate the published campaigns)")
    problems += sum(row["status"] == "MISMATCH" for row in results.values())

    caches_ok = all(e["status"] in ("canonical", "present") for e in caches)
    canonical = all(e["status"] == "canonical" for e in caches if e["path"].endswith("means_test.npy"))
    print("\nwhat this checkout can run")
    print("  tests, figures from experiments/*.json ........ yes")
    derived_ok = n_derived == len(derived)
    ols_ok = any(e["path"].endswith(("residual_ols_z0_v1.npy",)) and "lcdm_tt_ee_lowl" in e["path"] for e in ols_present) \
        and any(e["path"].endswith("residual_ols_z4_v1.npy") and "lcdm_tt_ee_lowl" in e["path"] for e in ols_present)
    print("  SR searches on the latents (stage 1) ........... "
          + ("yes" if caches_ok else "NO — encoder caches missing")
          + ("" if canonical or not caches_ok else " (present but not the canonical bytes: numbers may differ at float32 precision)"))
    print("  audits and campaigns on the residuals (phases 5-8, stage 2) "
          + ("yes" if caches_ok and derived_ok else f"NO — {len(derived) - n_derived} residual caches missing"))
    print("  stage-3 search on the OLS residual (EE z0, z4) .. "
          + ("yes" if caches_ok and ols_ok else "NO — residual_ols_z{0,4}_v1.npy for lcdm_tt_ee_lowl missing"))
    print("  encoder pass, templates, stage-4 attribution ... "
          + ("yes" if shards["status"] == "ok" else "NO — spectra shards " + shards["status"]))
    print("  re-consolidate published campaigns ............ "
          + (f"{sum(1 for r in results.values() if not r['status'].startswith(('missing', 'incomplete')))}"
             f"/{len(results)} campaigns present" if results else "NO — results/ empty"))
    print(f"\ncanonical hashes from {source}; the item-by-item checklist is docs/inputs_checklist.md")
    if problems:
        sys.stdout.flush()
        print(f"\n{problems} problem(s): a present file does not match its canonical hash, "
              "or a committed file is missing", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
