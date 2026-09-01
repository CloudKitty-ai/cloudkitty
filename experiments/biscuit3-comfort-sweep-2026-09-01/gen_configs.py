#!/usr/bin/env python3
"""Generate the Biscuit 3.0 comfort x score x weights sweep configs from
the served TOML (prereg.md -- read it first).

Textual transforms only (the needflow-lab pattern), so everything not
named is byte-identical to the served world:
  - Biscuit's seat -> behavior = "playful" (her scripted anchor); the
    other four -> "needs_driven" (theirs)
  - tick_ms 800 -> 40; seed / bind / snapshot_path per run
  - groom_cuddle_relief 2.0 -> 0.5 (the canonical 041 economy Biscuit
    3.0 trains under; the served 2.0 is a temporary bump -- and F-036:
    scripted seats never read the dial when deciding anyway)
  - comfort arm: playful_comfort 55 -> {55, 45, 35, 30}
  - weights arm W35: comfort 55 with eat/drink/sleep weights 55/35 so
    the food band gets serious at 35 while bath/cuddle keep the 55 line
  - score on/off: the spec-042 dials at the candidate weights or absent
No [water] block: contagion is shelved for Gen 1.

usage: gen_configs.py <scratch dir>   (writes <scratch>/configs/*.toml)
"""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "cloudkitty.toml"
OUT = Path(sys.argv[1]) / "configs"
OUT.mkdir(parents=True, exist_ok=True)
SEEDS = [20260911, 20260912]
# (label, playful_comfort, food weight) -- W35 = 55 * (1/35) rounded so
# eat/drink/sleep trip the line at 35.00.
COMFORT_ARMS = [("c55", 55.0, None), ("c45", 45.0, None), ("c35", 35.0, None),
                ("c30", 30.0, None), ("w35", 55.0, 55.0 / 35.0)]
# Candidate score dials (first pass, chosen before any data; see prereg).
SCORE = {"w_value": 0.5, "w_busy": 1.0, "w_serious": 0.5,
         "t_self": 5.0, "t_partner": 5.0, "critter_appeal": 0.0}

src = SRC.read_text()
idx = 0
for label, comfort, food_w in COMFORT_ARMS:
    for score_on in (False, True):
        for seed in SEEDS:
            t = src
            # Biscuit is the second seat; her policy line is unique.
            t, n = re.subn(r'^behavior = "policy:e006a-L-04-s3"$',
                           'behavior = "playful"', t, flags=re.M)
            assert n == 1, n
            t, n = re.subn(r'^behavior = "policy:[^"]+"$',
                           'behavior = "needs_driven"', t, flags=re.M)
            assert n == 4, n
            t, n = re.subn(r"^tick_ms = 800$", "tick_ms = 40", t, flags=re.M)
            assert n == 1
            t, n = re.subn(r"^seed = \d+$", f"seed = {seed}", t, flags=re.M)
            assert n == 1
            port = 8300 + idx
            t, n = re.subn(r'^bind = "[^"]+"$', f'bind = "127.0.0.1:{port}"',
                           t, flags=re.M)
            assert n == 1
            run = f"{label}-{'on' if score_on else 'off'}-{seed}"
            snap = OUT.parent / "snaps" / f"{run}.json"
            t, n = re.subn(r'^snapshot_path = "[^"]+"$',
                           f'snapshot_path = "{snap}"', t, flags=re.M)
            assert n == 1
            t, n = re.subn(r"^groom_cuddle_relief = 2.0$",
                           "groom_cuddle_relief = 0.5", t, flags=re.M)
            assert n == 1
            dials = [f"playful_comfort = {comfort}"]
            if score_on:
                dials += [f"{k} = {v}" for k, v in SCORE.items()]
            if food_w is not None:
                dials += ["[behavior.comfort_weight]",
                          f"eat = {food_w:.6f}", f"drink = {food_w:.6f}",
                          f"sleep = {food_w:.6f}",
                          "play = 1.0", "cuddle = 1.0", "bath = 1.0"]
            # The weights table must close the [behavior] section, so the
            # dial block replaces playful_comfort and the rest of
            # [behavior]'s keys are moved above it.
            t, n = re.subn(r"^playful_comfort = 55.0$", "\n".join(dials), t, flags=re.M)
            assert n == 1
            if food_w is not None:
                head, tail = t.split("[behavior.comfort_weight]\n", 1)
                weights, rest = tail.split("bath = 1.0\n", 1)
                nxt = re.search(r"^\[", rest, flags=re.M)
                behavior_rest, after = rest[:nxt.start()], rest[nxt.start():]
                t = head + behavior_rest + "[behavior.comfort_weight]\n" + weights + "bath = 1.0\n\n" + after
            assert "[water]" not in t
            (OUT / f"{run}.toml").write_text(t)
            idx += 1
print(f"wrote {idx} configs to {OUT}")
