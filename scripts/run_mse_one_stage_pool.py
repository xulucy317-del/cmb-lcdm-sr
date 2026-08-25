#!/usr/bin/env python
"""Scheduler-free executor for the frozen MSE one-stage task matrices.

The Slurm launchers in ``hpc/`` remain the single definition of task identity:
this runner reads their ``PRINT_MATRIX=1`` tables and rebuilds byte-identical
``run_blind_sr.py`` / ``run_shuffled_control.py`` argument vectors, so a task
executed here is the same task the array would have executed.  What changes is
only the process model:

* tasks run inside **persistent worker processes**, so Julia/PySR start once per
  worker instead of once per task (the CSD3 smoke run spent ~156 s of 215 s in
  startup);
* a task whose ``report.json`` already exists *and validates* is skipped, so the
  run is resumable across studio shutdowns (Lightning free-plan sessions stop);
* every attempt is appended to a JSONL ledger for provenance.

Usage::

    # what is left to do (no compute, no Julia)
    python scripts/run_mse_one_stage_pool.py --family all --dry-run

    # end-to-end environment check that cannot touch the frozen namespace
    python scripts/run_mse_one_stage_pool.py --family main --smoke lightning1 \
        --task-ids 36 --limit 1 --no-worker-logs

    # one real task, timed: the benchmark the plan asks for before scaling
    python scripts/run_mse_one_stage_pool.py --family main --limit 1 \
        --no-worker-logs

    # resume everything on this machine
    python scripts/run_mse_one_stage_pool.py --family all --workers 1

Re-running the same command after an interruption resumes; it never overwrites
an existing valid report.
"""
from __future__ import annotations

import argparse
import csv
import json
import multiprocessing as mp
import os
import platform
import queue
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
INPUTS = ["omega_b", "omega_cdm", "H0", "tau", "A_s", "n_s"]

FAMILIES = {
    "main": {
        "launcher": REPO / "hpc" / "slurm_mse_one_stage_sr.sh",
        "script": SCRIPTS / "run_blind_sr.py",
        "module": "run_blind_sr",
        "total": 165,
    },
    "control": {
        "launcher": REPO / "hpc" / "slurm_mse_one_stage_control.sh",
        "script": SCRIPTS / "run_shuffled_control.py",
        "module": "run_shuffled_control",
        "total": 12,
    },
}

# Frozen search settings (identical to the launchers).
N_SAMPLES = 5000
NITERATIONS = 200
POPULATIONS = 15
# SMOKE=1 settings (identical to the launchers).
SMOKE_N_SAMPLES = 500
SMOKE_NITERATIONS = 1
SMOKE_POPULATIONS = 2


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------
# Task matrix (read from the launchers, never re-derived here)
# --------------------------------------------------------------------------
def read_matrix(family: str) -> list[dict]:
    launcher = FAMILIES[family]["launcher"]
    env = dict(os.environ, PRINT_MATRIX="1")
    proc = subprocess.run(["bash", str(launcher)], cwd=REPO, env=env,
                          check=True, text=True, capture_output=True)
    rows = list(csv.DictReader(proc.stdout.splitlines(), delimiter="\t"))
    expected = FAMILIES[family]["total"]
    if len(rows) != expected:
        raise SystemExit(
            f"[err] {launcher.name} printed {len(rows)} tasks, expected {expected}")
    return rows


def build_task(family: str, row: dict, smoke: str | None) -> dict:
    run_dir = row["run_dir"]
    run_name = Path(run_dir).name
    latent = int(row["latent"])
    seed = int(row["seed"])
    maxsize = int(row["maxsize"])
    task_id = int(row["task_id"])
    n_samples, niterations, populations = N_SAMPLES, NITERATIONS, POPULATIONS
    if smoke:
        n_samples, niterations, populations = (
            SMOKE_N_SAMPLES, SMOKE_NITERATIONS, SMOKE_POPULATIONS)

    if family == "main":
        if smoke:
            out_dir = (Path("results") / run_name /
                       f"mse_one_stage_smoke_{smoke}_ms{maxsize}" /
                       f"z{latent}_seed{seed}")
        else:
            out_dir = (Path("results") / run_name /
                       f"mse_one_stage_ms{maxsize}" / f"z{latent}_seed{seed}")
        argv = [
            "--run-dir", run_dir,
            "--dataset-dir", "data",
            "--latent-index", str(latent),
            "--inputs", *INPUTS,
            "--n-samples", str(n_samples),
            "--niterations", str(niterations),
            "--populations", str(populations),
            "--maxsize", str(maxsize),
            "--inner-loss", "mse",
            "--selection-metric", "mse",
            "--posthoc-mi", "none",
            "--turbo",
            "--parallelism", "multithreading",
            "--seed", str(seed),
            "--out-dir", str(out_dir),
        ]
    else:
        base = (f"mse_one_stage_control_ms{maxsize}" if not smoke else
                f"mse_one_stage_control_smoke_{smoke}_ms{maxsize}")
        out_dir = (Path("results") / run_name / base /
                   f"z{latent}_shuffle{seed}_seed{seed}")
        argv = [
            "--run-dir", run_dir,
            "--dataset-dir", "data",
            "--target-index", str(latent),
            "--inputs", *INPUTS,
            "--n-samples", str(n_samples),
            "--niterations", str(niterations),
            "--populations", str(populations),
            "--maxsize", str(maxsize),
            "--inner-loss", "mse",
            "--selection-metric", "mse",
            "--posthoc-mi", "none",
            "--turbo",
            "--parallelism", "multithreading",
            "--shuffle-seed", str(seed),
            "--pysr-seed", str(seed),
            "--out-dir", str(out_dir),
        ]
    return {
        "family": family,
        "task_id": task_id,
        "run_dir": run_dir,
        "run": run_name,
        "latent": latent,
        "seed": seed,
        "maxsize": maxsize,
        "out_dir": str(out_dir),
        "module": FAMILIES[family]["module"],
        "script": str(FAMILIES[family]["script"]),
        "argv": argv,
        "smoke": smoke,
    }


def enumerate_tasks(family: str, smoke: str | None) -> list[dict]:
    return [build_task(family, row, smoke) for row in read_matrix(family)]


# --------------------------------------------------------------------------
# Resume contract: skip only a report that validates against its task
# --------------------------------------------------------------------------
def _finite(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) \
        and value == value and abs(value) != float("inf")


def validate_report(path: Path, task: dict) -> tuple[bool, str]:
    """Return (valid, reason). Only a valid report may be skipped."""
    try:
        report = json.loads(path.read_text())
    except FileNotFoundError:
        return False, "missing"
    except Exception as exc:                                     # noqa: BLE001
        return False, f"unreadable: {exc}"
    if not isinstance(report, dict):
        return False, "not a JSON object"

    checks: list[tuple[str, bool]] = [
        ("regime", report.get("regime") == task["run"]),
        ("inner_loss", report.get("inner_loss") == "mse"),
        ("selection_metric", report.get("selection_metric") == "mse"),
        ("maxsize", (report.get("pysr_kwargs") or {}).get("maxsize")
         == task["maxsize"]),
        ("best_index", isinstance(report.get("best_index"), int)),
        ("best_expression", bool(report.get("best_expression"))),
        ("equations", bool(report.get("all_equations"))),
    ]
    if task["family"] == "main":
        checks += [
            ("latent_index", report.get("latent_index") == task["latent"]),
            ("seed", report.get("seed") == task["seed"]),
            ("best_mse_val", _finite(report.get("best_mse_val"))),
        ]
    else:
        checks += [
            ("control", report.get("control") == "shuffled_target"),
            ("target_index", report.get("target_index") == task["latent"]),
            ("shuffle_seed", report.get("shuffle_seed") == task["seed"]),
            ("pysr_seed", report.get("pysr_seed") == task["seed"]),
            ("best_mse_val_shuffled_eval",
             _finite(report.get("best_mse_val_shuffled_eval"))),
        ]
    bad = [name for name, ok in checks if not ok]
    return (not bad), ("ok" if not bad else "failed checks: " + ",".join(bad))


def task_status(task: dict) -> tuple[str, str]:
    report = REPO / task["out_dir"] / "report.json"
    if not report.exists():
        return "pending", "no report.json"
    valid, reason = validate_report(report, task)
    return ("done", reason) if valid else ("invalid", reason)


def next_run_id(task: dict) -> str:
    """A PySR state dir that does not collide with an interrupted attempt."""
    state = REPO / task["out_dir"] / "pysr_state"
    for n in range(1000):
        if not (state / f"run_{n}").exists():
            return f"run_{n}"
    return f"run_{int(time.time())}"


# --------------------------------------------------------------------------
# Worker: one persistent Julia/PySR session, many tasks
# --------------------------------------------------------------------------
def _run_one_in_process(task: dict) -> None:
    """Execute one task by calling the frozen runner's main() in-process."""
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import importlib

    module = importlib.import_module(task["module"])
    argv = list(task["argv"]) + ["--pysr-run-id", next_run_id(task)]
    old_argv = sys.argv
    sys.argv = [task["script"], *argv]
    try:
        module.main()
    finally:
        sys.argv = old_argv


def _worker(worker_id: int, tasks: list, counter, result_q, stop_evt,
            opts: dict) -> None:
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    os.chdir(REPO)
    if opts["worker_log_dir"]:
        log_path = Path(opts["worker_log_dir"]) / (
            f"pool_{opts['stamp']}_worker{worker_id}.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        os.dup2(fd, 1)
        os.dup2(fd, 2)
        os.close(fd)
        sys.stdout = os.fdopen(1, "w", buffering=1)
        sys.stderr = os.fdopen(2, "w", buffering=1)

    os.environ["JULIA_NUM_THREADS"] = str(opts["threads"])
    os.environ["PYTHONUNBUFFERED"] = "1"
    t0 = time.time()
    import pysr                                                  # noqa: PLC0415

    # Start Julia and load SymbolicRegression here rather than lazily inside
    # the first PySRRegressor.fit(). Without this the first task of a worker
    # charges the whole Julia/JIT start to its reported fit_seconds, which is
    # both misleading and unlike the CSD3 reports.
    julia_version = None
    try:
        from pysr.julia_import import SymbolicRegression, jl     # noqa: F401

        julia_version = str(jl.seval("string(VERSION)"))
    except Exception as exc:                                     # noqa: BLE001
        print(f"[worker {worker_id}] warm-up import failed ({exc}); Julia will "
              "start inside the first fit", flush=True)
    startup = time.time() - t0
    result_q.put({"kind": "startup", "worker": worker_id,
                  "seconds": startup, "pysr_version": pysr.__version__,
                  "julia_version": julia_version,
                  "threads": opts["threads"]})
    print(f"[worker {worker_id}] pysr {pysr.__version__} / julia "
          f"{julia_version} ready in {startup:.1f}s with "
          f"{opts['threads']} thread(s)", flush=True)

    done = 0
    while not stop_evt.is_set():
        # A shared counter, not a queue: every task is known before the first
        # worker starts, so an index hand-out cannot race a feeder thread.
        with counter.get_lock():
            index = counter.value
            if index >= len(tasks):
                break
            counter.value = index + 1
        task = tasks[index]
        started = time.time()
        print(f"\n[worker {worker_id}] === {task['family']} task "
              f"{task['task_id']}: {task['out_dir']} ===", flush=True)
        record = {"kind": "task", "worker": worker_id,
                  "started_utc": utc_now(), **{
                      k: task[k] for k in ("family", "task_id", "run", "latent",
                                           "seed", "maxsize", "out_dir")}}
        try:
            _run_one_in_process(task)
            record["status"] = "ok"
        except BaseException as exc:                             # noqa: BLE001
            record["status"] = "failed"
            record["error"] = f"{type(exc).__name__}: {exc}"
            print(f"[worker {worker_id}] task {task['task_id']} FAILED: "
                  f"{record['error']}", flush=True)
        record["seconds"] = time.time() - started
        report = REPO / task["out_dir"] / "report.json"
        if record["status"] == "ok":
            valid, reason = validate_report(report, task)
            if not valid:
                record["status"] = "invalid_report"
                record["error"] = reason
            else:
                try:
                    record["fit_seconds"] = json.loads(
                        report.read_text()).get("fit_seconds")
                except Exception:                                # noqa: BLE001
                    pass
        record["finished_utc"] = utc_now()
        result_q.put(record)
        done += 1
        if opts["recycle_after"] and done >= opts["recycle_after"]:
            print(f"[worker {worker_id}] recycling after {done} tasks",
                  flush=True)
            break
    result_q.put({"kind": "worker_exit", "worker": worker_id, "tasks": done})


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------
def parse_ids(spec: str | None, total: int) -> set[int] | None:
    if not spec:
        return None
    ids: set[int] = set()
    for part in spec.replace(" ", "").split(","):
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            ids.update(range(int(lo), int(hi) + 1))
        else:
            ids.add(int(part))
    bad = sorted(i for i in ids if not 0 <= i < total)
    if bad:
        raise SystemExit(f"[err] task ids out of range 0-{total - 1}: {bad}")
    return ids


def append_ledger(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def main() -> int:
    cpu = os.cpu_count() or 1
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--family", choices=["main", "control", "all"],
                   default="all")
    p.add_argument("--task-ids", default=None,
                   help="Subset such as '36-164' or '0,5,7' (per family).")
    p.add_argument("--workers", type=int, default=1,
                   help="Persistent worker processes (default 1).")
    p.add_argument("--threads", type=int, default=None,
                   help=f"Julia threads per worker (default: cpu/workers; "
                        f"this machine reports {cpu} CPUs).")
    p.add_argument("--limit", type=int, default=None,
                   help="Stop after N tasks (benchmarking).")
    p.add_argument("--time-budget-minutes", type=float, default=None,
                   help="Start no new task after this much wall time.")
    p.add_argument("--smoke", default=None, metavar="TAG",
                   help="Cheap end-to-end check in an isolated smoke "
                        "namespace (500 rows, 1 iteration, 2 populations).")
    p.add_argument("--dry-run", action="store_true",
                   help="Report the matrix status and exit; no Julia, no fit.")
    p.add_argument("--ledger", default="logs/mse_one_stage_pool_ledger.jsonl")
    p.add_argument("--worker-log-dir", default="logs")
    p.add_argument("--no-worker-logs", action="store_true",
                   help="Leave worker output on this console.")
    p.add_argument("--recycle-after", type=int, default=None,
                   help="Restart a worker after N tasks (memory hygiene).")
    p.add_argument("--max-consecutive-failures", type=int, default=3)
    p.add_argument("--rerun-invalid", action="store_true",
                   help="Also rerun tasks whose existing report fails "
                        "validation (default: report and skip them).")
    args = p.parse_args()

    os.chdir(REPO)
    families = ["main", "control"] if args.family == "all" else [args.family]
    if args.workers < 1:
        raise SystemExit("[err] --workers must be >= 1")
    threads = args.threads or max(1, cpu // args.workers)

    tasks: list[dict] = []
    summary: dict[str, dict[str, int]] = {}
    invalid: list[tuple[dict, str]] = []
    for family in families:
        family_tasks = enumerate_tasks(family, args.smoke)
        wanted = parse_ids(args.task_ids, FAMILIES[family]["total"])
        counts = {"done": 0, "pending": 0, "invalid": 0, "skipped_filter": 0}
        for task in family_tasks:
            if wanted is not None and task["task_id"] not in wanted:
                counts["skipped_filter"] += 1
                continue
            status, reason = task_status(task)
            counts[status] += 1
            if status == "done":
                continue
            if status == "invalid":
                invalid.append((task, reason))
                if not args.rerun_invalid:
                    continue
            tasks.append(task)
        summary[family] = counts

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    print(f"[pool] repo={REPO}")
    print(f"[pool] host={socket.gethostname()} cpus={cpu} "
          f"workers={args.workers} threads/worker={threads}")
    print(f"[pool] python={platform.python_version()} stamp={stamp}"
          + (f" smoke={args.smoke}" if args.smoke else ""))
    for family, counts in summary.items():
        total = FAMILIES[family]["total"]
        print(f"[pool] {family}: {counts['done']}/{total} complete, "
              f"{counts['pending']} pending, {counts['invalid']} invalid"
              + (f", {counts['skipped_filter']} outside --task-ids"
                 if counts["skipped_filter"] else ""))
    for task, reason in invalid:
        print(f"[pool] INVALID {task['family']} task {task['task_id']} "
              f"{task['out_dir']}: {reason}")
    if invalid and not args.rerun_invalid:
        print("[pool] invalid reports are NOT rerun automatically; inspect "
              "them, then pass --rerun-invalid to redo those tasks.")

    if args.limit is not None:
        tasks = tasks[:args.limit]
    if args.dry_run:
        for task in tasks:
            print(f"[dry-run] {task['family']} {task['task_id']:>3} "
                  f"{task['out_dir']}")
        print(f"[dry-run] {len(tasks)} task(s) would run")
        return 0
    if not tasks:
        print("[pool] nothing to do")
        return 0

    ledger = Path(args.ledger)
    ctx = mp.get_context("fork")
    result_q = ctx.Queue()
    stop_evt = ctx.Event()
    counter = ctx.Value("i", 0)

    opts = {"threads": threads, "stamp": stamp,
            "worker_log_dir": None if args.no_worker_logs
            else args.worker_log_dir,
            "recycle_after": args.recycle_after}
    append_ledger(ledger, {
        "kind": "session", "utc": utc_now(), "stamp": stamp,
        "host": socket.gethostname(), "cpus": cpu, "workers": args.workers,
        "threads_per_worker": threads, "family": args.family,
        "smoke": args.smoke, "queued": len(tasks),
        "python": platform.python_version(), "summary": summary,
    })

    t_start = time.time()
    budget = (args.time_budget_minutes * 60.0
              if args.time_budget_minutes else None)
    interrupted = {"flag": False}

    def _stop(signum, _frame):
        if interrupted["flag"]:
            print("\n[pool] second signal: terminating workers now")
            for proc in procs:
                proc.terminate()
            return
        interrupted["flag"] = True
        stop_evt.set()
        print(f"\n[pool] signal {signum}: finishing the running task(s), then "
              "stopping. Re-run the same command to resume.")

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    procs = []
    def _spawn(worker_id: int):
        proc = ctx.Process(target=_worker, name=f"pool-w{worker_id}",
                           args=(worker_id, tasks, counter, result_q,
                                 stop_evt, opts))
        proc.daemon = False
        proc.start()
        procs.append(proc)
        return proc

    live = {i: _spawn(i) for i in range(args.workers)}
    if opts["worker_log_dir"]:
        print(f"[pool] worker output -> {opts['worker_log_dir']}/"
              f"pool_{stamp}_worker*.log")

    completed = failed = 0
    consecutive_failures = 0
    while live:
        try:
            record = result_q.get(timeout=1.0)
        except queue.Empty:
            for worker_id, proc in list(live.items()):
                if not proc.is_alive():
                    live.pop(worker_id)
            if budget and not stop_evt.is_set() and \
                    time.time() - t_start > budget:
                stop_evt.set()
                print(f"[pool] time budget {args.time_budget_minutes} min "
                      "reached; no new task will start")
            continue

        kind = record.pop("kind")
        if kind == "startup":
            append_ledger(ledger, {"utc": utc_now(), "stamp": stamp,
                                   "kind": "startup", **record})
            print(f"[pool] worker {record['worker']} startup "
                  f"{record['seconds']:.1f}s (pysr {record['pysr_version']}, "
                  f"julia {record.get('julia_version')})")
            continue
        if kind == "worker_exit":
            worker_id = record["worker"]
            proc = live.pop(worker_id, None)
            if proc is not None:
                proc.join(timeout=30)
            if (args.recycle_after and not stop_evt.is_set()
                    and counter.value < len(tasks)):
                new_id = max(list(live) + [worker_id]) + 1
                live[new_id] = _spawn(new_id)
            continue

        record.update({"stamp": stamp, "kind": "task"})
        append_ledger(ledger, record)
        if record["status"] == "ok":
            completed += 1
            consecutive_failures = 0
        else:
            failed += 1
            consecutive_failures += 1
        elapsed = time.time() - t_start
        left = len(tasks) - completed - failed
        rate = elapsed / max(completed + failed, 1)
        print(f"[pool] {record['status']:>14} {record['family']} task "
              f"{record['task_id']:>3} in {record['seconds']:.0f}s "
              f"| done {completed} failed {failed} left {left} "
              f"| eta {left * rate / 60:.0f} min")
        if consecutive_failures >= args.max_consecutive_failures:
            print(f"[pool] {consecutive_failures} consecutive failures; "
                  "stopping so the cause can be inspected")
            stop_evt.set()

    for proc in procs:
        proc.join(timeout=60)
    total_min = (time.time() - t_start) / 60
    append_ledger(ledger, {"kind": "session_end", "utc": utc_now(),
                           "stamp": stamp, "completed": completed,
                           "failed": failed, "minutes": total_min})
    print(f"[pool] session done: {completed} completed, {failed} failed, "
          f"{total_min:.1f} min wall")
    if interrupted["flag"]:
        return 130
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
