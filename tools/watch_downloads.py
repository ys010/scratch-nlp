#!/usr/bin/env python3
"""
watch_downloads.py

Watches a downloads folder (default ~/Downloads) for new Scratch .sb3
snapshots, moves each one into a run's snapshots/ directory, parses it with
sb3_parser.py (with a diff against the previous snapshot), and appends one
line to the run's events.jsonl. The tutor watches events.jsonl rather than
polling snapshots/ itself.

Usage:
    python tools/watch_downloads.py --run-dir runs/noa/loops-intro/2026-09-27_1830
    python tools/watch_downloads.py --run-dir <run-dir> --source ~/Downloads

Only one watcher should run per run-dir; the PID is recorded in
<run-dir>/.watcher.pid so start/resume/end-lesson can stop a stale one.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sb3_parser import load_project_json, parse_project, diff_snapshots  # noqa: E402

POLL_SECONDS = 1.5
STABLE_CHECKS = 2  # how many consecutive stable size-reads before we trust a file is done writing


def is_stable(path, last_sizes):
    """
    Returns True once `path`'s size has stopped changing across
    STABLE_CHECKS consecutive polls. Tracks state in `last_sizes` (a dict
    the caller keeps across polls) so a still-downloading file isn't picked
    up mid-write.
    """
    try:
        size = path.stat().st_size
    except FileNotFoundError:
        return False
    prev_size, stable_count = last_sizes.get(path, (None, 0))
    if size == prev_size and size > 0:
        stable_count += 1
    else:
        stable_count = 0
    last_sizes[path] = (size, stable_count)
    return stable_count >= STABLE_CHECKS


def next_snapshot_number(snapshots_dir):
    existing = sorted(p.stem for p in snapshots_dir.glob("*.sb3"))
    if not existing:
        return 1
    return int(existing[-1]) + 1


def process_new_file(sb3_path, run_dir):
    snapshots_dir = run_dir / "snapshots"
    parsed_dir = run_dir / "parsed"
    n = next_snapshot_number(snapshots_dir)
    name = f"{n:03d}"
    dest = snapshots_dir / f"{name}.sb3"
    sb3_path.replace(dest)

    project_json = load_project_json(dest)
    sprites, opcodes, block_ids = parse_project(project_json)
    result = {"sprites": sprites, "opcodes_present": sorted(opcodes), "diff": None}

    changed = True
    prev_name = f"{n - 1:03d}"
    prev_path = snapshots_dir / f"{prev_name}.sb3"
    if n > 1 and prev_path.exists():
        prev_json = load_project_json(prev_path)
        _, prev_opcodes, prev_block_ids = parse_project(prev_json)
        result["diff"] = diff_snapshots(prev_opcodes, prev_block_ids, opcodes, block_ids)
        changed = result["diff"]["changed"]

    parsed_path = parsed_dir / f"{name}.json"
    parsed_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    event = {"n": name, "time": datetime.now(timezone.utc).isoformat(), "changed": changed}
    with open(run_dir / "events.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    print(f"[watch_downloads] {dest.name} -> parsed/{name}.json (changed={changed})", flush=True)
    return name


def run_watch_loop(run_dir, source_dir):
    snapshots_dir = run_dir / "snapshots"
    parsed_dir = run_dir / "parsed"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    parsed_dir.mkdir(parents=True, exist_ok=True)

    pid_file = run_dir / ".watcher.pid"
    pid_file.write_text(str(os.getpid()), encoding="utf-8")

    print(f"[watch_downloads] watching {source_dir} for new .sb3 files -> {run_dir}", flush=True)

    seen = {p.resolve() for p in source_dir.glob("*.sb3")}
    last_sizes = {}
    pending = set()

    try:
        while True:
            time.sleep(POLL_SECONDS)
            current = {p.resolve() for p in source_dir.glob("*.sb3")}
            new_files = current - seen
            pending |= new_files
            seen |= new_files

            still_pending = set()
            for path in pending:
                if not path.exists():
                    continue
                if is_stable(path, last_sizes):
                    try:
                        process_new_file(path, run_dir)
                    except Exception as exc:  # noqa: BLE001 - surface and keep watching
                        print(f"[watch_downloads] failed to process {path}: {exc}", file=sys.stderr, flush=True)
                    last_sizes.pop(path, None)
                else:
                    still_pending.add(path)
            pending = still_pending
    finally:
        if pid_file.exists() and pid_file.read_text(encoding="utf-8").strip() == str(os.getpid()):
            pid_file.unlink()


def try_watchdog(run_dir, source_dir):
    """Prefer the `watchdog` package's filesystem events when available; falls back to polling otherwise."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        return False

    class Handler(FileSystemEventHandler):
        def __init__(self):
            self.last_sizes = {}
            self.pending = set()

        def on_any_event(self, event):
            if event.is_directory or not event.src_path.endswith(".sb3"):
                return
            self.pending.add(Path(event.src_path))

    handler = Handler()
    observer = Observer()
    observer.schedule(handler, str(source_dir), recursive=False)
    observer.start()

    snapshots_dir = run_dir / "snapshots"
    parsed_dir = run_dir / "parsed"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    parsed_dir.mkdir(parents=True, exist_ok=True)
    pid_file = run_dir / ".watcher.pid"
    pid_file.write_text(str(os.getpid()), encoding="utf-8")
    print(f"[watch_downloads] (watchdog) watching {source_dir} -> {run_dir}", flush=True)

    try:
        while True:
            time.sleep(POLL_SECONDS)
            still_pending = set()
            for path in handler.pending:
                if not path.exists():
                    continue
                if is_stable(path, handler.last_sizes):
                    try:
                        process_new_file(path, run_dir)
                    except Exception as exc:  # noqa: BLE001
                        print(f"[watch_downloads] failed to process {path}: {exc}", file=sys.stderr, flush=True)
                    handler.last_sizes.pop(path, None)
                else:
                    still_pending.add(path)
            handler.pending = still_pending
    finally:
        observer.stop()
        observer.join()
        if pid_file.exists() and pid_file.read_text(encoding="utf-8").strip() == str(os.getpid()):
            pid_file.unlink()
    return True


def main():
    parser = argparse.ArgumentParser(description="Watch for new Scratch .sb3 snapshots and parse them")
    parser.add_argument("--run-dir", required=True, help="the run directory to write snapshots/parsed/events into")
    parser.add_argument("--source", default=str(Path.home() / "Downloads"), help="folder to watch (default ~/Downloads)")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    source_dir = Path(args.source).expanduser().resolve()
    run_dir.mkdir(parents=True, exist_ok=True)

    if not try_watchdog(run_dir, source_dir):
        run_watch_loop(run_dir, source_dir)


if __name__ == "__main__":
    main()
