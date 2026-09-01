#!/usr/bin/env python3
"""Drive the 15 edge-avoidance-smoke runs (prereg.md — read it first).

Per run: boot the arm's headless server fresh, 60 s warmup discarded,
300 s measured via waterline_exposure.py, archive final /world +
/welfare samples and the boot log's contagion lines (dial provenance is
the BOOT LOG, never config memory), shut down. Sequential; ~1.6 h.

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
SCRATCH = Path(sys.argv[1]) if len(sys.argv) > 1 else None
if SCRATCH is None:
    sys.exit("usage: run_smoke.py <scratch dir containing configs/>")
CONFIGS = sorted((SCRATCH / "configs").glob("*.toml"))
SERVER = REPO / "target/debug/cloudkitty-server"
INSTRUMENT = REPO / "experiments/attn-cert-2026-08-14/waterline_exposure.py"
RAW = HERE / "results-raw"
WARMUP_S, MEASURE_S, INTERVAL_S = 60, 300, 0.03

assert len(CONFIGS) == 15, CONFIGS


def fetch(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.load(r)


for cfg in CONFIGS:
    run = cfg.stem                      # e.g. "C-20260902"
    port = re.search(r'bind = "127\.0\.0\.1:(\d+)"',
                     cfg.read_text()).group(1)
    base = f"http://127.0.0.1:{port}"
    bootlog = RAW / f"{run}-boot.log"
    with bootlog.open("w") as bl:
        srv = subprocess.Popen(
            [SERVER, "--config", cfg, "--fresh", "--no-backup"],
            stdout=bl, stderr=subprocess.STDOUT)
    try:
        for _ in range(60):             # wait for boot
            try:
                fetch(f"{base}/world")
                break
            except Exception:
                time.sleep(0.5)
        else:
            print(f"{run}: server never served /world", flush=True)
            continue
        time.sleep(WARMUP_S)
        r = subprocess.run(
            [sys.executable, INSTRUMENT, str(MEASURE_S), str(INTERVAL_S),
             "--base", base, "--raw", RAW / f"{run}-exposure.json"],
            capture_output=True, text=True)
        (RAW / f"{run}-instrument.out").write_text(r.stdout + r.stderr)
        (RAW / f"{run}-final.json").write_text(json.dumps(
            {"world": fetch(f"{base}/world"),
             "welfare": fetch(f"{base}/welfare")}, indent=1) + "\n")
        print(f"{run}: done ({r.returncode})", flush=True)
    finally:
        srv.terminate()
        srv.wait(timeout=30)

print("all runs complete", flush=True)
