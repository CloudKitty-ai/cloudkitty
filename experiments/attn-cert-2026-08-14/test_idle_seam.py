r"""F-032 guard: the discriminator must be "idle on the tick AFTER a scene
ends", not "idle on the ending tick".

That distinction is the whole finding. The ending tick is by definition a
play or chase, so an off-by-one reports 0% for every seat and the
Biscuit-vs-roster contrast vanishes into "nobody idles at scene ends" --
a tidy, plausible, wrong answer.

To see it red, put the off-by-one into the real tool and re-run:

    sed -i '' 's/if acts\[i\] == "idle"/if acts[i - 1] == "idle"/' idle_seam.py
    python3 test_idle_seam.py          # must FAIL: asker 0.0 != 100.0
    git checkout idle_seam.py

Fixture asserts against the shipped `analyse`, not a copy of its logic.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from idle_seam import analyse  # noqa: E402

POS = {"x": 5, "y": 5}
BUG = [{"kind": "bug", "pos": {"x": 9, "y": 5}}]

# Asker: two scenes, each ending INTO an idle tick. Quiet: one scene,
# ending into a groom, with an unrelated idle later. Same idle count,
# opposite discriminator.
SCRIPT = {
    "Asker": [("play", "kitty"), ("play", "kitty"), ("idle", None),
              ("chase", "element"), ("chase", "element"), ("idle", None),
              ("groom", None), ("groom", None)],
    "Quiet": [("play", "kitty"), ("play", "kitty"), ("groom", None),
              ("groom", None), ("idle", None), ("move", None),
              ("move", None), ("move", None)],
}

rows = []
for t in range(len(SCRIPT["Asker"])):
    kitties = []
    for name, script in SCRIPT.items():
        action, target = script[t]
        la = {"action": action}
        if target:
            la["target"] = target
            la["id"] = 4
        kitties.append({"name": name, "pos": POS, "state": None, "last_action": la})
    rows.append({"tick": 1000 + t, "kitties": kitties, "elements": BUG})

got = analyse(rows)
a, q = got["Asker"], got["Quiet"]
print("Asker: endings=%d idle@end=%s idle=%d preimage=%s"
      % (a["scene_endings"], a["idle_after_ending_pct"], a["idle_ticks"], a["idle_preimage"]))
print("Quiet: endings=%d idle@end=%s idle=%d preimage=%s"
      % (q["scene_endings"], q["idle_after_ending_pct"], q["idle_ticks"], q["idle_preimage"]))

assert a["scene_endings"] == 2, a["scene_endings"]
assert a["idle_after_ending_pct"] == 100.0, a["idle_after_ending_pct"]
assert q["scene_endings"] == 1, q["scene_endings"]
assert q["idle_after_ending_pct"] == 0.0, q["idle_after_ending_pct"]
# both seats idle the same number of times -- only the seam differs
assert a["idle_ticks"] == 2 and q["idle_ticks"] == 1, (a["idle_ticks"], q["idle_ticks"])
# the refused ask is attributed to the duet, not to the chase
assert a["idle_preimage"]["prev target KITTY (duet)"] == 1, a["idle_preimage"]
assert a["idle_preimage"]["prev target element/none"] == 1, a["idle_preimage"]
assert q["idle_preimage"] == {"prev groom": 1}, q["idle_preimage"]
assert a["moved_while_idle"] == 0
print("idle-seam discriminator OK")
