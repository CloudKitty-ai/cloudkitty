#!/usr/bin/env python3
"""Guards for swaps_read.py, on the real recorded rows. Plain asserts:
`python3 -B test_swaps.py` from the lab venv (after at least one swap
leg exists).

g1  a swap leg's team delta is seed-paired (the world picked by index 7
    matches a hand subtraction on that seed)
g2  the swapped seat comes from the seating name and the seat delta
    reads that seat (a leg's seat delta on a different index differs)
g3  read_leg refuses a leg whose unswapped seats differ from rot2's
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import swaps_read as sr  # noqa: E402


def first_leg():
    legs = sorted(d.name for d in sr.SWAPS.glob("g2-rot2-swap*-s*")
                  if (d / "legs/size20" / f"{d.name}-g2cmp-30x20000.jsonl").exists())
    assert legs, "no swap leg recorded yet"
    return legs[0]


def test_g1_delta_is_seed_paired():
    _, R = sr.by_seed(sr.ROT2)
    seeds = sorted(R)
    name = first_leg()
    leg = sr.read_leg(name, R, seeds)
    _, S = sr.by_seed(sr.SWAPS / name / "legs/size20" / f"{name}-g2cmp-30x20000.jsonl")
    w = seeds[7]
    assert abs(leg["per_world_delta"][7] - (sr.team(S[w]) - sr.team(R[w]))) < 1e-12


def test_g2_seat_delta_reads_the_named_seat():
    _, R = sr.by_seed(sr.ROT2)
    seeds = sorted(R)
    name = first_leg()
    k, net = sr.seat_of(name)
    leg = sr.read_leg(name, R, seeds)
    assert leg["seat"] == k and leg["alternate"] == net
    _, S = sr.by_seed(sr.SWAPS / name / "legs/size20" / f"{name}-g2cmp-30x20000.jsonl")
    hand = sum(S[w]["mean_happiness"][k] - R[w]["mean_happiness"][k] for w in seeds) / 30
    assert abs(leg["seat_delta"]["mean"] - hand) < 1e-12
    other = (k + 1) % 5
    hand_other = sum(S[w]["mean_happiness"][other] - R[w]["mean_happiness"][other] for w in seeds) / 30
    assert abs(hand - hand_other) > 1e-9, "fixture cannot tell the seats apart"


def test_g3_refuses_a_leg_whose_other_seats_differ():
    _, R = sr.by_seed(sr.ROT2)
    seeds = sorted(R)
    name = first_leg()
    k, net = sr.seat_of(name)
    # a rot2 reference with one UNSWAPPED seat renamed must be refused
    bad = {w: dict(r, seats=[("g2:trunk-sX" if i == (k + 1) % 5 else s) for i, s in enumerate(r["seats"])])
           for w, r in R.items()}
    try:
        sr.read_leg(name, bad, seeds)
    except AssertionError:
        return
    raise AssertionError("read_leg accepted a leg whose unswapped seats differ from the reference")


def test_g4_crossings_count_streaks_at_or_over_150_and_place_them():
    _, R = sr.by_seed(sr.ROT2)
    seeds = sorted(R)
    # the leg with the most long streaks on record: s9 at Pumpkin's seat
    name = "g2-rot2-swap2-s9"
    _, S = sr.by_seed(sr.SWAPS / name / "legs/size20" / f"{name}-g2cmp-30x20000.jsonl")
    k, _ = sr.seat_of(name)
    c = sr.crossings(S, seeds, k)
    hand = [(w, i) for w in seeds for i in range(5) if S[w]["max_distress_age_seat"][i] >= 150]
    assert c["total"] == len(hand) and c["in_swapped_seat"] == sum(i == k for _, i in hand), (c, len(hand))
    assert c["total"] > 0, c
    # placement reads the seat index: pointed at the seat that carries the
    # first crossing, the in-seat count is that seat's hand count
    j = hand[0][1]
    assert j != k, "fixture: the first crossing sits in the swapped seat; pick another leg"
    assert sr.crossings(S, seeds, j)["in_swapped_seat"] == sum(i == j for _, i in hand) > 0


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
