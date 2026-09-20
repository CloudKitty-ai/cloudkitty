"""Guards for screen_read.py on RECORDED harness output (fixtures/*-eval-2x400.jsonl, the
2-seed × 400-tick smoke of the patched harness on anchor-b3). Run: python -B test_screen_read.py"""
import json
from pathlib import Path
import screen_read as S

HERE = Path(__file__).resolve().parent
for fn in ("scripted-eval-2x400.jsonl", "gen1-A-c0-eval-2x400.jsonl"):
    head, rows = S.load_rows(HERE / "fixtures" / fn)
    assert len(rows) == 2 and all("beam" in r for r in rows), fn
    agg = S.aggregate(rows)
    R = 5
    # pooled shares are sums over seeds AND seats, divided by the right denominator
    sleep = sum(r["beam"]["sleep"][i] for r in rows for i in range(R))
    on = sum(r["beam"]["on_beam"][i] for r in rows for i in range(R))
    starts = sum(r["beam"]["starts"][i] for r in rows for i in range(R))
    assert agg["ticks"] == sum(r["ticks"] for r in rows) == 800
    assert abs(agg["pooled"]["in_beam"] - on / sleep) < 1e-12, (agg["pooled"]["in_beam"], on / sleep)
    assert abs(agg["pooled"]["sleep_share"] - sleep / (800 * R)) < 1e-12, "pooled sleep share is per cat-tick (ticks x seats), not per world tick"
    assert abs(sum(agg["seats"][nm]["sleep_share"] for nm in S.SEATS) / R - agg["pooled"]["sleep_share"]) < 1e-12
    assert agg["pooled"]["starts"] == starts
    assert abs(sum(agg["pooled"]["start_dist"]) - 1.0) < 1e-9, agg["pooled"]["start_dist"]
    assert abs(sum(agg["pooled"]["start_need_bins"]) - 1.0) < 1e-9
    d0 = sum(r["beam"]["start_dist"][i][0] for r in rows for i in range(R))
    assert abs(agg["pooled"]["start_dist"][0] - d0 / starts) < 1e-12, "start-distance shares are per START, not per sleeping tick"
    # per-seat numbers use that seat's own denominators
    for i, nm in enumerate(S.SEATS):
        s_i = sum(r["beam"]["sleep"][i] for r in rows); o_i = sum(r["beam"]["on_beam"][i] for r in rows)
        if s_i:
            assert abs(agg["seats"][nm]["in_beam"] - o_i / s_i) < 1e-12, nm
        else:
            assert agg["seats"][nm]["in_beam"] is None
        assert abs(agg["seats"][nm]["happiness"] - sum(r["mean_happiness"][i] for r in rows) / 2) < 1e-9
    # welfare: happiness is a mean over seeds and seats, nash a mean over seeds, distress the max
    assert abs(agg["pooled"]["happiness"] - sum(sum(r["mean_happiness"]) for r in rows) / (2 * R)) < 1e-9
    assert abs(agg["pooled"]["nash_state"] - sum(r["nash_state"] for r in rows) / 2) < 1e-12
    assert agg["pooled"]["max_distress_age"] == max(r["max_distress_age"] for r in rows)
    assert agg["pooled"]["seeds_over_line"] == [] if agg["pooled"]["max_distress_age"] < S.DIST_LINE else True

# the message-head counter (tier 5, P4): one count per policy seat per tick, 16 heads wide, none for scripted seats
head, rows = S.load_rows(HERE / "fixtures" / "gen1-A-c0-eval-2x400.jsonl")
for r in rows:
    assert set(r["msg"]) == {f"kitty_{i}" for i in range(1, 6)} and all(len(v) == 16 for v in r["msg"].values())
    assert all(sum(v) == r["ticks"] for v in r["msg"].values()), "every policy tick chooses exactly one head"
head, rows = S.load_rows(HERE / "fixtures" / "scripted-eval-2x400.jsonl")
assert all(r["msg"] == {} for r in rows), "scripted seats are not counted"

# variant naming and the level parse
m = S.NAME.match("s3-b10-t3000-n7"); assert m and m.group("ttl") == "3000" and m.group("count") == "7"
assert S.NAME.match("anchor") is None
# checks() on an empty read returns unreadable, not wrong
ch = S.checks({})
assert ch["P1"]["holds"] is None and ch["P2"]["clears_bar"] is None and ch["P3"]["under_0.15"] is None and ch["P4"]["holds"] is None and ch["P5"] == {}
print("test_screen_read ok")
