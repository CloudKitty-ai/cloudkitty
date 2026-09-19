"""Guards for cert_harness_fog.beam_account on a RECORDED payload (fixtures/beam-fixture.json,
written by record_fixture.py from the scripted roster on anchor-b3, seed 870001).
Run: python -B test_beam_metrics.py"""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
import cert_harness_fog as H

F = json.load(open(HERE / "fixtures" / "beam-fixture.json"))
R, W, Hh = F["roster"], F["width"], F["height"]


def beams_of(row):
    return {(x, y) for (_i, ty, x, y) in row["elements"] if ty == "Sunbeam"}


def sleepers(row):
    st = np.asarray(row["state"], np.float32)
    return [k for k in range(R) if int(st[k * H.PER_KITTY + H.ACT0:k * H.PER_KITTY + H.ACT0 + 7].argmax()) == H.SLEEP_ACT]


def run(before, at):
    acc = H.beam_acc(R)
    prev = H.beam_account(np.asarray(before["state"], np.float32), beams_of(before), R, W, Hh, np.zeros(R, bool), acc)
    acc = H.beam_acc(R)  # count only the second tick, with the first as history
    H.beam_account(np.asarray(at["state"], np.float32), beams_of(at), R, W, Hh, prev, acc)
    return acc, prev


# on-beam case: the recorded seat sleeps on a beam tile at `at`
on = F["on"]; acc, prev = run(on["before"], on["at"]); k = on["seat"]
assert tuple(on["pos"]) in beams_of(on["at"])
assert acc["sleep"][k] == 1 and acc["on_beam"][k] == 1 and acc["conducted"][k] == 0, acc
assert sum(acc["sleep"]) == len(sleepers(on["at"])), (acc["sleep"], sleepers(on["at"]))
# a start is counted only on the first sleeping tick: the seat's start count is 1 iff it was not asleep before
was_asleep = bool(prev[k])
assert acc["starts"][k] == (0 if was_asleep else 1), (acc["starts"], was_asleep)
if not was_asleep:
    assert acc["start_dist"][k][0] == 1, acc["start_dist"][k]

# off-beam case: the recorded seat sleeps on a tile that is no beam
off = F["off"]; acc, prev = run(off["before"], off["at"]); k = off["seat"]
assert tuple(off["pos"]) not in beams_of(off["at"])
assert acc["sleep"][k] == 1 and acc["on_beam"][k] == 0, acc
# conducted only if a direct partner sits on a beam; recompute the claim from the payload
st = np.asarray(off["at"]["state"], np.float32); b = k * H.PER_KITTY
partner_on = False
if st[b + H.PARTNER_PRESENT] > 0.5:
    p = int(round(float(st[b + H.PARTNER_IDX]) * (R - 1))); pb = p * H.PER_KITTY
    ppos = (int(round(float(st[pb + H.POS0]) * W)), int(round(float(st[pb + H.POS0 + 1]) * Hh)))
    partner_on = ppos in beams_of(off["at"])
assert acc["conducted"][k] == int(partner_on), (acc["conducted"], partner_on)
# nearest-beam distance bin at the start is the Chebyshev minimum over the world's beams, capped at 3
if acc["starts"][k]:
    d = min(max(abs(off["pos"][0] - x), abs(off["pos"][1] - y)) for x, y in beams_of(off["at"]))
    assert acc["start_dist"][k][min(d, 3)] == 1, (d, acc["start_dist"][k])
    need = float(st[b + H.NEED_SLEEP]) * 100
    assert sum(acc["start_need_bins"][k]) == 1
    assert acc["start_need_bins"][k][sum(need >= e for e in H.NEED_BINS)] == 1, (need, acc["start_need_bins"][k])
    assert abs(acc["start_need_sum"][k] - need) < 1e-4

# a sleeper who was already asleep is never a start, whatever the tile
acc2 = H.beam_acc(R)
H.beam_account(np.asarray(on["at"]["state"], np.float32), beams_of(on["at"]), R, W, Hh, np.ones(R, bool), acc2)
assert sum(acc2["starts"]) == 0 and sum(acc2["sleep"]) == len(sleepers(on["at"])), acc2
print("test_beam_metrics ok")
