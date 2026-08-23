"""Guard for pose_census.py's copy of the client's pose rule.

The census mirrors `poseFor`/`chaseDistanceFor` from client/render.js in
Python. A copy that drifts from the client reports a pose mix nobody is
looking at, so every branch of the rule gets a case here — and the two
branches that decide the pounce get their red on demand:

  GATE=99  — widen the pounce gate; the far chase must stop drawing a walk.
  NOGATE=1 — drop the unresolved-quarry carve-out; the vanished quarry
             must stop drawing a pounce.

Both knobs exist to be run: a green that has never been seen red proves
nothing. Unset, every case must pass.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pose_census as pc  # noqa: E402

GATE = int(os.environ.get("GATE", pc.POUNCE_GATE))
NOGATE = os.environ.get("NOGATE") == "1"

WORLD = {
    "elements": [{"id": 9, "kind": "bug", "pos": {"x": 3, "y": 0}},
                 {"id": 8, "kind": "greeble", "pos": {"x": 9, "y": 0}}],
    "kitties": [{"id": 2, "pos": {"x": 1, "y": 0}}],
}


def kitty(action, state="idle", **fields):
    return {"id": 1, "pos": {"x": 0, "y": 0}, "activity": {"state": state},
            "last_action": dict(action=action, **fields)}


CASES = [
    ("chase inside the gate", kitty("chase", target="element", id=9),
     True, "pouncing"),
    ("chase beyond the gate", kitty("chase", target="element", id=8),
     True, "walking"),
    ("chase, quarry vanished", kitty("chase", target="element", id=77),
     True, "pouncing"),
    ("chase a cat, inside", kitty("chase", target="kitty", id=2),
     True, "pouncing"),
    ("solo play", kitty("play"), True, "pouncing"),
    ("move", kitty("move", direction="north"), True, "walking"),
    ("move, but stood still", kitty("move", direction="north"),
     False, "idle"),
    ("groom self", kitty("groom"), False, "grooming"),
    ("groom a friend", kitty("groom", target=2), False, "grooming-other"),
    ("sleep", kitty("sleep"), False, "sleep-curl"),
    # The scene fallback: Idle/Purr/Meow name no pose of their own, so the
    # running scene still decides — the case that keeps a napping cat
    # curled on the tick its action reads idle.
    ("idle action, sleeping scene", kitty("idle", state="sleeping"),
     False, "sleep-curl"),
    ("purr while eating", kitty("purr", state="eating"), False, "eating"),
]

failures = []
for name, k, moved, want in CASES:
    cd = pc.chase_dist(k, WORLD)
    if NOGATE and cd is None and k["last_action"]["action"] == "chase":
        cd = float("inf")  # the carve-out removed: unknown quarry loses it
    got = pc.pose_for(k, moved, cd, gate=GATE)
    ok = got == want
    if not ok:
        failures.append((name, want, got))
    print(f"{'ok ' if ok else 'RED'} {name:28} cd={cd} -> {got} (want {want})")

mode = f"GATE={GATE}{' NOGATE' if NOGATE else ''}"
if failures:
    print(f"\n{mode}: {len(failures)} case(s) red")
    sys.exit(1)
print(f"\n{mode}: pose replica OK ({len(CASES)} cases)")
