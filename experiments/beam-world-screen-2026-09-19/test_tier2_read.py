"""Guards for tier2_read.py: the swap-leg seat pick and the arm-in-seat pooling on a RECORDED
harness leg (fixtures/gen1-A-c0-eval-2x400.jsonl, seats renamed to stage a swap), and the
prediction-3 letter on its declared lines. Run: python -B test_tier2_read.py"""
import json, tempfile
from pathlib import Path
import screen_read as S
import tier2_read as T

HERE = Path(__file__).resolve().parent
head, rows = S.load_rows(HERE / "fixtures" / "gen1-A-c0-eval-2x400.jsonl")

# stage a swap leg: seat 2 holds the arm, the other four the gen1-A minds (rows are real harness output)
with tempfile.TemporaryDirectory() as d:
    f = Path(d) / "gen1-A_s2-pkg-s1-c0-eval-2x400.jsonl"
    staged = []
    for r in rows:
        r = dict(r); r["seats"] = ["ppo:cand-s2", "ppo:cand-s1", "ppo:pkg-s1", "ppo:cand-s4", "ppo:cand-s7"]; staged.append(r)
    with f.open("w") as fh:
        fh.write(json.dumps(head) + "\n")
        for r in staged: fh.write(json.dumps(r) + "\n")
    assert T.swap_leg_seat(staged, "pkg-s1") == [2]
    own = T.arm_in_seat([f], "pkg-s1")
    starts = sum(r["beam"]["starts"][2] for r in rows); d0 = sum(r["beam"]["start_dist"][2][0] for r in rows)
    sleep = sum(r["beam"]["sleep"][2] for r in rows); on = sum(r["beam"]["on_beam"][2] for r in rows)
    assert own["starts"] == starts and own["sleep"] == sleep
    assert (own["placement"] is None and starts == 0) or abs(own["placement"] - d0 / starts) < 1e-12, "placement is the ARM'S seat only"
    assert (own["in_beam"] is None and sleep == 0) or abs(own["in_beam"] - on / sleep) < 1e-12
    # the same leg twice pools to the same shares with doubled counts
    own2 = T.arm_in_seat([f, f], "pkg-s1")
    assert own2["starts"] == 2 * starts and (own2["placement"] == own["placement"])
    # pool() over the roster keeps the seat structure of aggregate()
    p = T.pool([f]); assert p["seeds"] == 2 and abs(p["pooled"]["in_beam"] - S.aggregate(rows)["pooled"]["in_beam"]) < 1e-12

# prediction 3's letter on the declared lines (0.15 keep, 0.10 lose)
assert T.letter([0.05, 0.08], [0.03, 0.09]) == "a"
assert T.letter([0.20, 0.16], [0.04, 0.09]) == "b"
assert T.letter([0.20, 0.16], [0.15, 0.30]) == "c"
assert T.letter([0.20, 0.12], [0.04, 0.09]) == "other"   # one package seed between the lines
assert T.letter([0.20, 0.16], [0.12, 0.09]) == "other"   # floor5 between the lines
assert T.letter([0.20, None], [0.04, 0.09]) is None      # unreadable, not wrong
assert T.letter([0.15, 0.15], [0.10, 0.10]) == "other"   # floor5 AT the lose line is not under it
print("test_tier2_read ok")
