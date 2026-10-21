#!/usr/bin/env python3
"""Rotation driver (DECLARATION.md beside this file): the scripted
reference, then g2-rot1..5, each on seeds 905001-905005 x 20,000 ticks,
one roster at a time with its five worlds in parallel. A roster seats
only eligible finals (stop_reason plateau or cap). The F-053 abort is
armed on every world; a roster with an abort is reported for the owner
and the next roster runs (each is its own composition).

    run_rotation.py [--ticks 20000] [--dry-run]
"""
import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
PY = EXPTS / "exp-006-character-gen/.venv/bin/python"
ARTS = EXPTS / "gen2-trunk-training-2026-10-18/artifacts"
sys.path.insert(0, str(EXPTS / "fog-gen1-cert"))
from cert_harness_fog import SEATINGS  # noqa: E402

ROSTERS = ["scripted"] + [f"g2-rot{r}" for r in range(1, 6)]
SEEDS = list(range(905001, 905006))


def eligible(spec):
    if spec == "scripted":
        return True
    import torch
    p = ARTS / f"ppo-g2-{spec.split(':')[1]}" / "policy-final.pt"
    if not p.exists():
        return False
    ck = torch.load(p, map_location="cpu", weights_only=True)
    return ck["stop_reason"] in ("plateau", "cap")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticks", type=int, default=20000)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    stopped = []
    for roster in ROSTERS:
        bad = [s for s in set(SEATINGS[roster]) if not eligible(s)]
        if bad:
            print(f"== {roster} SKIPPED: no eligible final for {sorted(bad)}; owner-routed", flush=True)
            stopped.append(roster)
            continue
        outs = [HERE / f"results-raw/{roster}/streams-{s}.npz" for s in SEEDS]
        cmds = [[str(PY), "-B", str(HERE / "seating_collect_g2.py"), "--seating", roster,
                 "--seed", str(s), "--ticks", str(a.ticks), "--out", str(o)]
                for s, o in zip(SEEDS, outs)]
        print(f"== {roster} start: {SEATINGS[roster]}", flush=True)
        if a.dry_run:
            continue
        with ThreadPoolExecutor(max_workers=len(cmds)) as ex:
            rcs = list(ex.map(lambda c: subprocess.run(c).returncode, cmds))
        if any(rcs):
            print(f"== {roster} FAILED: collector exit codes {rcs}; stopping", flush=True)
            sys.exit(1)
        aborts = []
        for s, o in zip(SEEDS, outs):
            meta = json.loads(str(np.load(o)["meta"]))
            if meta["aborted_at"]:
                aborts.append((s, meta["aborted_at"]))
        if aborts:
            print(f"== {roster} STOPPED: F-053 abort(s) {aborts}; owner-routed", flush=True)
            stopped.append(roster)
        else:
            print(f"== {roster} done: {len(SEEDS)} worlds, no abort", flush=True)
    print(f"== rotation done; stopped or skipped: {stopped or 'none'}", flush=True)


if __name__ == "__main__":
    main()
