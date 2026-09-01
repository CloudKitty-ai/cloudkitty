#!/usr/bin/env python3
"""Guard for score.py's primitives on a RECORDED slice (prereg.md §Guard).

fixtures/w35-off-20260912-slice.json is cut unedited from the 600-tick
smoke run of 2026-09-01: two census-poll pairs bracketing two real
Biscuit play-duet scenes (started 552 and 669), and three consecutive
/world polls (ticks 214/227/240) around two play relief stamps.

Pins, worked by hand from the recorded numbers:
  (a) eat at tick 552 sits 4/12 of the way from 3.9 (t548) to 7.5
      (t560) = 5.1; at tick 669, 6/13 of the way from 38.4 (t663) to
      3.3 (t676) = 22.2.
  (b) the stamp seen at t227 (226 > 212) is NOT hungry (eat 21.3,
      drink 28.8); the one at t240 (239 > 226) IS (drink 32.7 >= 30).
  (c) sleep at 552 interpolates to 31.5 (30.3 -> 33.9), so the scene is
      dropped from the low-need set although eat/drink are ~5/~2;
      the 669 scene (eat 22.2, drink 2.7, sleep 28.8) is kept.
Each shown red in-run (mutating score.py) before commit.

Run: python3 test_score.py
"""
import json
from pathlib import Path

from score import hungry_play, interp_need, low_need, series

HERE = Path(__file__).resolve().parent
FIX = json.loads((HERE / "fixtures" / "w35-off-20260912-slice.json").read_text())
SER = series(FIX["census_polls"])


def close(a, b, tol=0.01):
    return abs(a - b) <= tol


# (a) interpolated need at a scene start
assert close(interp_need(SER, 2, 552, "eat"), 5.1), interp_need(SER, 2, 552, "eat")
assert close(interp_need(SER, 2, 669, "eat"), 22.2), interp_need(SER, 2, 669, "eat")
assert close(interp_need(SER, 2, 548, "eat"), 3.9, 1e-6)  # a poll tick is the poll

# (b) a play stamp counts hungry only when eat or drink >= 30 at that poll
assert hungry_play(FIX["world_polls"], 2) == (1, 2), hungry_play(FIX["world_polls"], 2)

# (c) the low-need filter drops a scene whose interpolated sleep crosses 30
scenes = {e["started"]: low_need(SER, 2, e["started"]) for e in FIX["events"]}
assert scenes == {552: False, 669: True}, scenes

print("test_score: 3 pins ok")
