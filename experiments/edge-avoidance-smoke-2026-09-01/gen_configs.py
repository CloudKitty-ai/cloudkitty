#!/usr/bin/env python3
"""Generate the 15 edge-avoidance-smoke lab configs from the served TOML.

Textual transforms only, so everything not named here is byte-identical
to the served world (cloudkitty.toml @ dfa4b6b):
  - all five seats -> behavior = "needs_driven" (scripted arms)
  - tick_ms 800 -> 40 (fast lab; poller at 0.03s sees ~every tick)
  - seed -> per-run paired seed (same set across arms)
  - bind -> per-run port (8100+idx)
  - snapshot_path -> per-run scratch file
  - groom_cuddle_relief 2.0 -> 0.5 (ruling 6: canonical, not the temp bump)
  - per-arm [water]/[behavior] dials appended
  - arm E only: bath_gain_ceiling 25, safeguard 98, distress 99 -- the
    validate_water headroom budget (ceiling + gain*ratio*factor < safeguard)
    caps the factor at ~2.14 under served law; the positive control needs
    10x. Disclosed in the prereg.
"""
import re
import sys
from pathlib import Path

SRC = Path("/Users/elizabethkelly/ai/cloudkitty/cloudkitty.toml").read_text()
OUT = Path(__file__).parent / "configs"
OUT.mkdir(exist_ok=True)
SEEDS = [20260901, 20260902, 20260903]

ARMS = {
    "A": {"ladder": False, "factor": 0.0, "membership": None},
    "B": {"ladder": False, "factor": 1.0, "membership": "option_a"},
    "C": {"ladder": True, "factor": 1.0, "membership": "option_a"},
    "D": {"ladder": True, "factor": 1.0, "membership": "bidirectional"},
    "E": {"ladder": True, "factor": 10.0, "membership": "bidirectional",
          "crank_budget": True},
    # Addendum 1: E's drift-matched control -- E with avoidance made
    # impossible. Ports 8115+ so A-E configs regenerate byte-identical.
    "F": {"ladder": False, "factor": 10.0, "membership": "bidirectional",
          "crank_budget": True},
}

idx = 0
for arm, spec in ARMS.items():
    for seed in SEEDS:
        t = SRC
        t, n = re.subn(r'^behavior = "policy:[^"]+"$',
                       'behavior = "needs_driven"', t, flags=re.M)
        assert n == 5, n
        t, n = re.subn(r"^tick_ms = 800$", "tick_ms = 40", t, flags=re.M)
        assert n == 1
        t, n = re.subn(r"^seed = \d+$", f"seed = {seed}", t, flags=re.M)
        assert n == 1
        port = 8100 + idx
        t, n = re.subn(r'^bind = "[^"]+"$', f'bind = "127.0.0.1:{port}"',
                       t, flags=re.M)
        assert n == 1
        snap = OUT.parent / "snaps" / f"{arm}-{seed}.json"
        t, n = re.subn(r'^snapshot_path = "[^"]+"$',
                       f'snapshot_path = "{snap}"', t, flags=re.M)
        assert n == 1
        t, n = re.subn(r"^groom_cuddle_relief = 2.0$",
                       "groom_cuddle_relief = 0.5", t, flags=re.M)
        assert n == 1
        if spec.get("crank_budget"):
            t, n = re.subn(r"^safeguard = 75.0$", "safeguard = 98.0",
                           t, flags=re.M)
            assert n == 1
            t, n = re.subn(r"^distress = 90.0$", "distress = 99.0",
                           t, flags=re.M)
            assert n == 1
        water = ["", "[water]"]
        if spec.get("crank_budget"):
            water.append("bath_gain_ceiling = 25.0")
        if spec["factor"]:
            water.append(f"contagion_factor = {spec['factor']}")
        if spec["membership"]:
            water.append(f'contagion_membership = "{spec["membership"]}"')
        block = "\n".join(water) + "\n" if len(water) > 2 or spec["factor"] \
            else ""
        t += block
        if spec["ladder"]:
            t, n = re.subn(r"^\[behavior\]$",
                           "[behavior]\ncontagion_aware_ladder = true",
                           t, flags=re.M)
            assert n == 1
        (OUT / f"{arm}-{seed}.toml").write_text(t)
        idx += 1
print(f"wrote {idx} configs to {OUT}")
