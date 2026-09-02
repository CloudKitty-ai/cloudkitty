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
Addendum 1 pins, from the same three /world polls (ticks 214/227/240):
  (d) Biscuit cuddle is 30.4 / 35.6 / 40.9 -> share>=30 = 3/3, mean
      35.63; drink 24.9 / 28.8 / 32.7 -> 1/3; eat 0/3. The roster's 12
      rows carry ONE drink >=30 (Kittybear 33.6 @214) and ONE cuddle
      (Clementine 33.1 @227) -> 1/12 each.
  (e) Biscuit's announce_armed is non-empty in all 3 rows (cuddle 3/3,
      drink 1/3); the roster arms in 2 of 12 rows.
  (f) Biscuit happiness 82.1 / 78.9 / 75.6 -> worst 75.6, share under
      80 = 2/3.
Addendum 2 pins, fixtures/c30-off-20260911-consent-slice.json (three real
Biscuit duet starts from the c30 sweep run, bracketing census polls
unedited):
  (g) consent gate at line 30: the 1537 start (Pumpkin cuddle 35.2 >
      play 0.4) is BLOCKED; 1835 (Clementine play 29.4 over a 13.05 top)
      and 1521 (Pumpkin top 29.4, under the line) are not. Strictness:
      with the line set AT the 1537 top exactly, it is NOT blocked.
  (h) hungry_start: Pumpkin's 1521 start interpolates eat 29.4 -> not
      hungry for the partner; Biscuit at 1537 reads her own needs.
  (i) refusal_tax on fixtures/consent30-probe-refusals.json (a real
      /events/refusal payload from the 047 binary, tick 13-315): Biscuit
      (id 2) has 24 absorbed==false rows, none of her 17 absorbed rows
      count; by_action splits play_kitty from the rest; the window is
      inclusive at both ends (first refused row tick 20, last 310).
Each shown red in-run (mutating score.py) before commit.

Run: python3 test_score.py
"""
import json
from pathlib import Path

from score import (announce_share, consent_blocked, happiness_trough, hungry_play,
                   hungry_start, interp_need, low_need, need_shares, refusal_tax,
                   series)

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

# (d) per-need share>=30 and mean over (poll, kitty) rows
W = FIX["world_polls"]
nb = need_shares(W, {2})
assert nb["cuddle"]["share_armed"] == 1.0 and close(nb["cuddle"]["mean"], 35.63, 0.02), nb["cuddle"]
assert close(nb["drink"]["share_armed"], 1 / 3, 1e-9) and nb["eat"]["share_armed"] == 0.0, nb
nr = need_shares(W, {1, 3, 4, 5})
assert close(nr["drink"]["share_armed"], 1 / 12, 1e-9) and close(nr["cuddle"]["share_armed"], 1 / 12, 1e-9), nr

# (e) announce share, any need and per need
ab, ar = announce_share(W, {2}), announce_share(W, {1, 3, 4, 5})
assert ab["any"] == 1.0 and ab["cuddle"] == 1.0 and close(ab["drink"], 1 / 3, 1e-9), ab
assert close(ar["any"], 2 / 12, 1e-9), ar

# (f) happiness trough: worst poll and share under the bar
assert happiness_trough(W, 2, 80.0) == (min(k["happiness"] for p in W for k in p["kitties"] if k["id"] == 2), 2 / 3)
assert close(happiness_trough(W, 2, 80.0)[0], 75.6, 0.05)

# (g) the consent gate on three recorded duet starts
CS = json.loads((HERE / "fixtures" / "c30-off-20260911-consent-slice.json").read_text())
CSER = series(CS["census_polls"])
verdicts = {e["started"]: consent_blocked(CSER, e["activity"]["target"]["id"], e["started"]) for e in CS["events"]}
assert verdicts == {1537: True, 1835: False, 1521: False}, verdicts
top_1537 = max(interp_need(CSER, 3, 1537, n) for n in ("eat", "drink", "sleep", "cuddle", "bath"))
assert close(top_1537, 35.2, 0.05)
assert consent_blocked(CSER, 3, 1537, line=top_1537) is False     # strict >, not >=: AT the line is not over it

# (h) hungry_start reads the named seat's own eat/drink at the start tick
assert hungry_start(CSER, 3, 1521) is False and close(interp_need(CSER, 3, 1521, "eat"), 29.4, 0.05)
assert hungry_start(CSER, 2, 1537) == (max(interp_need(CSER, 2, 1537, n) for n in ("eat", "drink")) >= 30)

# (i) refusal tax off a real spec-046 ring payload
RF = json.loads((HERE / "fixtures" / "consent30-probe-refusals.json").read_text())["events"]
tax = refusal_tax(RF, 2, 13, 315)
assert tax["refused_idle"] == 24 and sum(1 for e in RF if e["kitty_id"] == 2) == 41, tax
assert close(tax["share_of_ticks"], 24 / 303, 1e-9), tax
# window is inclusive at both ends: her first refused row sits at tick 20, last at 310
assert refusal_tax(RF, 2, 20, 310)["refused_idle"] == 24 and refusal_tax(RF, 2, 21, 309)["refused_idle"] == 22
assert sum(tax["by_action"].values()) == 24 and "play_kitty" in tax["by_action"], tax["by_action"]
# R8 as declared is the PARTNERED tax (a play-with-friend proposal bounced): 13 of her 24 refused rows
assert tax["partnered"] == 13 and close(tax["partnered_share"], 13 / 303, 1e-9), tax

print("test_score: 10 pins ok")
