#!/usr/bin/env python3
"""Generate the needflow-lab-validation configs from the served TOML.

Textual transforms only (the edge-avoidance smoke's pattern), so
everything not named is byte-identical to the served world:
  - all five seats -> behavior = "needs_driven" (scripted; needflow's
    greedy chooser is a proxy for these, not for the frozen policies)
  - tick_ms 800 -> 40
  - seed / bind / snapshot_path per run
  - arm "canon": groom_cuddle_relief 2.0 -> 0.5 (the canonical 041 design
    economy needflow's baseline row prices)
  - arm "serve": groom_cuddle_relief left at 2.0 (the temporary serving
    bump, needflow's 2.0 row)
No [water] block: contagion is shelved for Gen 1 (2026-09-01 ruling).

usage: gen_configs.py <scratch dir>   (writes <scratch>/configs/*.toml)
"""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "cloudkitty.toml"
OUT = Path(sys.argv[1]) / "configs"
OUT.mkdir(parents=True, exist_ok=True)
SEEDS = [20260901, 20260902, 20260903]
ARMS = {"canon": 0.5, "serve": 2.0}

src = SRC.read_text()
idx = 0
for arm, relief in ARMS.items():
    for seed in SEEDS:
        t = src
        t, n = re.subn(r'^behavior = "policy:[^"]+"$',
                       'behavior = "needs_driven"', t, flags=re.M)
        assert n == 5, n
        t, n = re.subn(r"^tick_ms = 800$", "tick_ms = 40", t, flags=re.M)
        assert n == 1
        t, n = re.subn(r"^seed = \d+$", f"seed = {seed}", t, flags=re.M)
        assert n == 1
        port = 8200 + idx
        t, n = re.subn(r'^bind = "[^"]+"$', f'bind = "127.0.0.1:{port}"',
                       t, flags=re.M)
        assert n == 1
        snap = OUT.parent / "snaps" / f"{arm}-{seed}.json"
        t, n = re.subn(r'^snapshot_path = "[^"]+"$',
                       f'snapshot_path = "{snap}"', t, flags=re.M)
        assert n == 1
        t, n = re.subn(r"^groom_cuddle_relief = 2.0$",
                       f"groom_cuddle_relief = {relief}", t, flags=re.M)
        assert n == 1
        assert "[water]" not in t
        (OUT / f"{arm}-{seed}.toml").write_text(t)
        idx += 1
print(f"wrote {idx} configs to {OUT}")
