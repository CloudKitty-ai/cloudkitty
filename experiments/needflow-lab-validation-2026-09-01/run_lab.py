#!/usr/bin/env python3
"""Drive the needflow-lab-validation runs (prereg.md — read it first).

Per run: boot the arm's headless server fresh, discard WARMUP_TICKS,
measure MEASURE_TICKS via scene_census.py, archive the final /world +
/welfare and the boot log, shut down. Sequential.

usage: run_lab.py <scratch dir containing configs/> [glob]
Raws land in results-raw/ (uncommitted, house rule).
"""
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SCRATCH = Path(sys.argv[1])
GLOB = sys.argv[2] if len(sys.argv) > 2 else "*.toml"
CONFIGS = sorted((SCRATCH / "configs").glob(GLOB))
SERVER = REPO / "target/debug/cloudkitty-server"
INSTRUMENT = HERE / "scene_census.py"
RAW = HERE / "results-raw"
WARMUP_TICKS, MEASURE_TICKS, INTERVAL_S = 1500, 20000, 0.5
assert CONFIGS, (SCRATCH, GLOB)
RAW.mkdir(exist_ok=True)


def fetch(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.load(r)


for cfg in CONFIGS:
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
            continue
        while fetch(f"{base}/world")["tick"] < WARMUP_TICKS:
            time.sleep(1.0)
        r = subprocess.run(
            [sys.executable, INSTRUMENT, "--base", base, "--ticks", str(MEASURE_TICKS),
             "--interval", str(INTERVAL_S), "--raw", RAW / f"{run}-census.json"],
            capture_output=True, text=True)
        (RAW / f"{run}-instrument.out").write_text(r.stdout + r.stderr)
        (RAW / f"{run}-final.json").write_text(json.dumps(
            {"world": fetch(f"{base}/world"), "welfare": fetch(f"{base}/welfare")},
            indent=1) + "\n")
        print(f"{run}: done ({r.returncode})", flush=True)
    finally:
        srv.terminate()
        srv.wait(timeout=30)

print("all runs complete", flush=True)
