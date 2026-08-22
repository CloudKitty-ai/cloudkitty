#!/usr/bin/env python3
"""The playful anchor: scripted `playful` at the Biscuit seat, engine
behaviors everywhere else, per-kitty mean happiness over the run.

This is the engine-native cell from the body-price correction (the
79.72 reading): ParallelEnv with control = needs_driven at every seat
except Biscuit, which runs `playful` — the demonstration generator,
i.e. THE CHARACTER. Committed as its own instrument per F-028 (the
original run was a scratchpad one-off; this file replaces it).

Usage: playful_anchor.py <config> [seeds=5] [ticks=20000]
"""
import json
import subprocess
import sys
from pathlib import Path

import tomllib

import numpy as np

import cloudkitty
from cert_harness6 import HAP, PER_KITTY

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent


def load_config(path):
    with open(path, "rb") as f:
        return tomllib.load(f)


def provenance(config_path):
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain"],
                           capture_output=True, text=True).stdout.strip()
    import hashlib
    return {
        "git_head": head,
        "dirty": sorted(l.split()[-1] for l in dirty.splitlines()) or None,
        "config_sha256": hashlib.sha256(
            Path(config_path).read_bytes()).hexdigest(),
        "instrument_sha256": hashlib.sha256(
            Path(__file__).read_bytes()).hexdigest(),
    }


def run_one(config_path, seed, ticks):
    cfg = load_config(config_path)
    kitties = cfg["kitty"]
    control = {f"kitty_{k['id']}": "needs_driven" for k in kitties}
    biscuit = next(k for k in kitties if k["name"] == "Biscuit")
    control[f"kitty_{biscuit['id']}"] = "playful"
    env = cloudkitty.ParallelEnv(str(config_path), control=control,
                                 horizon=ticks)
    env.reset(seed=seed)
    roster = len(kitties)
    hap_sum = np.zeros(roster)
    for _t in range(ticks):
        env.step({})
        st = np.asarray(env.state(), np.float32)
        for k in range(roster):
            hap_sum[k] += float(st[k * PER_KITTY + HAP]) * 100
    return (hap_sum / ticks).round(4).tolist()


def main():
    config = Path(sys.argv[1])
    n_seeds = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    ticks = int(sys.argv[3]) if len(sys.argv) > 3 else 20_000
    prov = provenance(config)
    print("provenance:", json.dumps(prov))
    cfg = load_config(config)
    names = [k["name"] for k in cfg["kitty"]]
    rows = []
    for i in range(n_seeds):
        seed = 870_001 + i
        means = run_one(config, seed, ticks)
        rows.append({"seed": seed, "mean_happiness": means})
        print(f"seed {seed}: " + " ".join(
            f"{n} {m:.2f}" for n, m in zip(names, means)), flush=True)
    per = list(zip(*[r["mean_happiness"] for r in rows]))
    print("\nmeans: " + " ".join(
        f"{n} {float(np.mean(v)):.2f}" for n, v in zip(names, per)))
    out = HERE / "results-raw" / f"playful-anchor-{config.stem}.json"
    out.write_text(json.dumps({"provenance": prov, "rows": rows},
                              indent=1) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
