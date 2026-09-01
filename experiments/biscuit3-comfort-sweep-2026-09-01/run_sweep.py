#!/usr/bin/env python3
"""Drive the Biscuit 3.0 comfort sweep runs (prereg.md -- read it first).

Per run: boot the arm's headless server fresh, wait out WARMUP_TICKS,
then poll two ways for MEASURE_TICKS -- scene_census.py (the needflow
lab's scene instrument, as a subprocess) and this file's /world poller
in the need_latency.py shape -- archive final /world + /welfare and the
boot log, shut down. PARALLEL runs at a time; raws land in results-raw/
(uncommitted, house rule).

usage: run_sweep.py <scratch dir containing configs/> [glob]
"""
import json
import re
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SCRATCH = Path(sys.argv[1])
GLOB = sys.argv[2] if len(sys.argv) > 2 else "*.toml"
CONFIGS = sorted((SCRATCH / "configs").glob(GLOB))
SERVER = REPO / "target/debug/cloudkitty-server"
CENSUS = HERE.parent / "needflow-lab-validation-2026-09-01" / "scene_census.py"
RAW = HERE / "results-raw"
import os  # noqa: E402  (SWEEP_WARMUP / SWEEP_MEASURE override for smoke runs only)
WARMUP_TICKS = int(os.environ.get("SWEEP_WARMUP", 1500))
MEASURE_TICKS = int(os.environ.get("SWEEP_MEASURE", 20000))
INTERVAL_S, PARALLEL = 0.5, 5
assert CONFIGS, (SCRATCH, GLOB)
RAW.mkdir(exist_ok=True)


def fetch(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.load(r)


def poll_world(base, t_end, out):
    """need_latency.py's live poll shape, until the world passes t_end."""
    while True:
        try:
            w = fetch(f"{base}/world")
        except Exception as e:
            print(f"{base}: world poll {e}", file=sys.stderr)
            time.sleep(INTERVAL_S)
            continue
        out.append({"tick": w["tick"], "kitties": [
            {"id": k["id"], "name": k["name"], "pos": k["pos"], "needs": k["needs"],
             "last_relief": k.get("last_relief", {}),
             "announce_armed": k.get("announce_armed", []),
             "happiness": k["happiness"], "activity": k["activity"]}
            for k in w["kitties"]]})
        if w["tick"] >= t_end:
            return
        time.sleep(INTERVAL_S)


def one_run(cfg):
    run = cfg.stem
    port = re.search(r'bind = "127\.0\.0\.1:(\d+)"', cfg.read_text()).group(1)
    base = f"http://127.0.0.1:{port}"
    with (RAW / f"{run}-boot.log").open("w") as bl:
        srv = subprocess.Popen([SERVER, "--config", cfg, "--fresh", "--no-backup"],
                               stdout=bl, stderr=subprocess.STDOUT)
    try:
        for _ in range(60):
            try:
                fetch(f"{base}/world")
                break
            except Exception:
                time.sleep(0.5)
        else:
            print(f"{run}: server never served /world", flush=True)
            return
        while fetch(f"{base}/world")["tick"] < WARMUP_TICKS:
            time.sleep(1.0)
        t0 = fetch(f"{base}/world")["tick"]
        polls = []
        th = threading.Thread(target=poll_world, args=(base, t0 + MEASURE_TICKS, polls))
        th.start()
        r = subprocess.run(
            [sys.executable, CENSUS, "--base", base, "--ticks", str(MEASURE_TICKS),
             "--interval", str(INTERVAL_S), "--raw", RAW / f"{run}-census.json"],
            capture_output=True, text=True)
        th.join()
        (RAW / f"{run}-instrument.out").write_text(r.stdout + r.stderr)
        (RAW / f"{run}-world-polls.json").write_text(json.dumps(
            {"base": base, "interval_s": INTERVAL_S, "polls": polls}) + "\n")
        (RAW / f"{run}-final.json").write_text(json.dumps(
            {"world": fetch(f"{base}/world"), "welfare": fetch(f"{base}/welfare")},
            indent=1) + "\n")
        print(f"{run}: done (census rc {r.returncode}, {len(polls)} world polls)", flush=True)
    finally:
        srv.terminate()
        srv.wait(timeout=30)


for i in range(0, len(CONFIGS), PARALLEL):
    batch = CONFIGS[i:i + PARALLEL]
    print(f"batch {i // PARALLEL + 1}: {[c.stem for c in batch]}", flush=True)
    threads = [threading.Thread(target=one_run, args=(c,)) for c in batch]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

print("all runs complete", flush=True)
