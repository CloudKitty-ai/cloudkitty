#!/usr/bin/env python3
"""Spec 061 verification instrument (see verification-2026-10-13.md
beside this file for the reads).

Replays the FR-001/FR-002 stuck signature over recorded healthy
behavior and prints fires per sweep setting:

    python3 specs/061-stuck-detector/stuck_rule_replay.py \
        [--strict-gate] [--relief governing|value-fell]

Run from the repo root of a checkout whose experiments/ raws are
populated (the native checkout). --strict-gate replays the rejected
draft gate (any scene tick resets the window) to reproduce the
masked-episode defect FR-002 names. --relief picks the clearing rule:
"governing" (default) is the implementation rule — a streak clears
only when the seat's own scene governs that need per the engine's
Activity::governing_need, read pessimistically where the recording
lacks fields (arm B's one-hot carries no groom target or rest
partner, so grooming and resting there clear nothing); "value-fell"
is the original clarify-gate rule (the need's value fell in-scene).
A synthetic F-044 two-tile pacer self-test always runs first: the
rig must fire before a zero means anything. Stdlib + numpy only;
writes one fire dump JSON beside this file.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
# Raws are untracked and live in the NATIVE checkout: resolve them against
# the invoking directory, which the docstring pins to that repo root.
ROOT = Path.cwd()
WINDOWS = [20, 30, 50]
ARMED = [75.0, 90.0]
STRICT = "--strict-gate" in sys.argv
RELIEF = sys.argv[sys.argv.index("--relief") + 1] if "--relief" in sys.argv else "governing"
assert RELIEF in ("governing", "value-fell"), RELIEF
NEED_ORDER = ["eat", "drink", "sleep", "play", "cuddle", "bath"]
SEATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]

# Engine Activity::governing_need (kitty.rs), restricted to the SEAT's own
# relief: grooming WITH a target relieves the friend's bath, not the
# groomer's, and solo rest governs nothing. Keyed by the serialized state.
def arm_a_relieves(activity):
    state = activity["state"]
    if state == "eating":
        return {"eat"}
    if state == "drinking":
        return {"drink"}
    if state == "sleeping":
        return {"sleep"}
    if state == "playing":
        return {"play"}
    if state == "grooming":
        return set() if activity.get("target") is not None else {"bath"}
    if state == "resting":
        return {"cuddle"} if activity.get("with_friend") is not None else set()
    return set()


# Arm B's one-hot (idle,resting,sleeping,eating,drinking,playing,grooming)
# carries no target/partner, so resting and grooming are read PESSIMISTICALLY
# (clear nothing -> streaks survive longer -> more chances to fire): a zero
# under this reading is a zero under every reading.
ARM_B_RELIEVES = [set(), set(), {"sleep"}, {"eat"}, {"drink"}, {"play"}, set()]


def run_stream(rows, n, armed_line, label, fires):
    """rows: (tick, (x, y), needs dict, in_scene, relieves set, extra).
    FR-001/FR-002: confinement = never leaving Manhattan radius 1 of the
    anchor; a need fires on n armed scene-free ticks, scene ticks pausing
    its streak and a scene relieving it clearing it (rule per RELIEF)."""
    anchor, confined, streak, last = None, 0, {}, None
    for tick, pos, needs, in_scene, relieves, extra in rows:
        if anchor is None or abs(pos[0] - anchor[0]) + abs(pos[1] - anchor[1]) > 1:
            anchor, confined, streak = pos, 1, {}
        else:
            confined += 1
        if STRICT and in_scene:
            confined, streak = 0, {}
        for k, v in needs.items():
            if RELIEF == "governing":
                relieving = in_scene and k in relieves
            else:
                relieving = in_scene and last is not None and v < last.get(k, v) - 0.5
            if relieving:
                streak[k] = 0
            elif in_scene:
                pass
            elif v >= armed_line:
                streak[k] = streak.get(k, 0) + 1
            else:
                streak[k] = 0
        last = needs
        hot = [k for k, v in streak.items() if v >= n]
        if confined >= n and hot:
            fires.append({"arm": label, "tick": tick, "needs": hot,
                          "pos": list(pos),
                          "need_values": {k: round(float(needs[k]), 1) for k in hot},
                          **extra})
            anchor, confined, streak = None, 0, {}


def arm_a_streams():
    base = ROOT / "experiments/fog-gen1-shakeout/results-raw/anchor-resmoke-050-20k"
    for ro in ["config-00-rollout-00", "config-00-rollout-01", "config-00-rollout-02"]:
        per_kitty = {}
        with open(base / ro / "trace.jsonl") as fh:
            for line in fh:
                snap = json.loads(line)["snapshot"]
                for k in snap["kitties"]:
                    per_kitty.setdefault(k["id"], []).append((
                        snap["tick"], (k["pos"]["x"], k["pos"]["y"]), k["needs"],
                        k["activity"]["state"] != "idle",
                        arm_a_relieves(k["activity"]),
                        {"rollout": ro, "seat": k["name"]}))
        yield from per_kitty.values()


def arm_b_streams():
    z = np.load(ROOT / "experiments/fog-gen1-cert/results-raw/live/lab-dispersion-gen1A-trace.npz")
    obs, tick, kitty, seed = z["obs"], z["tick"], z["kitty"], z["seed"]
    # v5 self block: needs 0-5 (x100), pos 7-8 (x20), activity one-hot 9-15
    # with slot 0 = Idle (observe.rs push_activity).
    assert np.allclose(obs[:, 9:16].sum(1), 1.0)
    scene = obs[:, 9] < 0.5
    idle_share = 1.0 - scene.mean()
    assert 0.5 < idle_share < 0.65, idle_share  # live poll measured 0.57
    for s in np.unique(seed):
        for ki in range(5):
            idx = np.where((seed == s) & (kitty == ki))[0]
            idx = idx[np.argsort(tick[idx])]
            pos = np.rint(obs[idx, 7:9] * 20).astype(int)
            needs = obs[idx, 0:6] * 100.0
            act_slot = obs[idx, 9:16].argmax(1)
            yield [(int(tick[i]), (int(pos[j, 0]), int(pos[j, 1])),
                    dict(zip(NEED_ORDER, needs[j].tolist())), bool(scene[idx][j]),
                    ARM_B_RELIEVES[int(act_slot[j])],
                    {"seed": int(s), "seat": SEATS[ki]})
                   for j, i in enumerate(idx)]


def selftest():
    for n in WINDOWS:
        for armed_line in ARMED:
            fires = []
            rows = [(t, (10 + t % 2, 10), {"eat": 95.0}, False, set(),
                     {"seat": "synthetic"})
                    for t in range(200)]
            run_stream(rows, n, armed_line, "selftest", fires)
            assert len(fires) == 200 // n, (n, armed_line, len(fires))
    print("# selftest: the synthetic F-044 two-tile pacer fires at every setting")


def main():
    selftest()
    streams_a, streams_b = list(arm_a_streams()), list(arm_b_streams())
    print(f"# gate: {'strict (rejected draft)' if STRICT else 'pause-not-reset (FR-002)'}"
          f", relief: {RELIEF}")
    print(f"# arm A {sum(len(s) for s in streams_a)} cat-ticks, "
          f"arm B {sum(len(s) for s in streams_b)} cat-ticks")
    all_fires = []
    for n in WINDOWS:
        for armed_line in ARMED:
            for label, streams in [("A-scripted", streams_a), ("B-policy", streams_b)]:
                fires = []
                for rows in streams:
                    run_stream(rows, n, armed_line, label, fires)
                by_seat = {}
                for f in fires:
                    f["params"] = f"N={n} armed>={armed_line:.0f}"
                    by_seat[f["seat"]] = by_seat.get(f["seat"], 0) + 1
                print(f"N={n} armed>={armed_line:.0f} {label:11s} fires {len(fires):3d}  {by_seat}")
                all_fires.extend(fires)
    out = HERE / "stuck-rule-fires.json"
    out.write_text(json.dumps(all_fires, indent=1))
    print(f"# fire detail -> {out} ({len(all_fires)} rows)")


if __name__ == "__main__":
    main()
