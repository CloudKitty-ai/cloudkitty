"""Live guard for the cert harness's message-head counter (tier 5 P4): runs run_one on one short
gen1-A world so the counter is exercised where the bug would occur, not on a recorded row.
Run from the repo root: experiments/exp-006-character-gen/.venv/bin/python -B experiments/beam-world-screen-2026-09-19/test_harness_msg.py"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
import cert_harness_fog as H

r = H.run_one(("gen1-A", 870001, 60, str(H.DEFAULT_CONFIG), None, None, "served"))
assert set(r["msg"]) == {f"kitty_{i}" for i in range(1, 6)} and all(len(v) == H.N_MSG for v in r["msg"].values())
assert all(sum(v) == r["ticks"] == 60 for v in r["msg"].values()), ("every policy tick chooses exactly one head", {a: sum(v) for a, v in r["msg"].items()})
assert any(v[0] < 60 for v in r["msg"].values()), "someone spoke in 60 ticks"
s = H.run_one(("scripted", 870001, 20, str(H.DEFAULT_CONFIG), None, None, "served"))
assert s["msg"] == {}, "scripted seats are not counted"
print("test_harness_msg ok")
