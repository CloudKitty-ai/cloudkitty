"""Live guard for the tier 6 read aids: on one short all-arm leg, distress_inspect's longest streak per
seat equals the cert harness's max_distress_age_seat, and lowneed_crosstab's start total equals the
harness's nap-start count. Both aids re-implement the harness's step loop, so the bug they can carry
(a wrong state offset, a start counted on every sleeping tick) shows as disagreement with the harness on
the same seed. Run from the repo root with CERT_ARTS pointing at the screen's artifacts:
CERT_ARTS=experiments/beam-world-screen-2026-09-19/artifacts experiments/exp-006-character-gen/.venv/bin/python -B experiments/beam-world-screen-2026-09-19/test_distress_inspect.py"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
assert os.environ.get("CERT_ARTS"), "CERT_ARTS must point at the screen's artifacts"
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
import cert_harness_fog as C  # noqa: E402
import distress_inspect as D  # noqa: E402
import lowneed_crosstab as L  # noqa: E402

CFG, SEED, TICKS, SLOT = HERE / "count-7.toml", 870009, 2300, "cnt7-s1"   # Biscuit's 520-tick drink streak, ticks 1,692-2,212
seats = [f"ppo:{SLOT}"] * 5
r = C.run_one(("gen1-A", SEED, TICKS, str(CFG), seats, None, "served"))
assert r["ticks"] == TICKS and max(r["max_distress_age_seat"]) > 0, ("the leg must carry some distress", r["max_distress_age_seat"])

windows = D.inspect(CFG, SEED, seats, TICKS)
longest = {k: 0 for k in range(5)}
for w in windows:
    longest[w["seat"]] = max(longest[w["seat"]], w["len"])
assert [longest[k] for k in range(5)] == r["max_distress_age_seat"], (longest, r["max_distress_age_seat"])
assert all(w["need"] in D.NEEDS and w["len"] == w["end"] - w["start"] for w in windows)

t = L.crosstab(CFG, SEED, SLOT, TICKS)
assert t["starts"] == sum(r["beam"]["starts"]), (t["starts"], r["beam"]["starts"])
assert t["starts"] == sum(v for v, _ in t["table"].values())

# the scripted teacher's cross-tab (spec 057 acceptance read) against the harness's all-scripted leg
import teacher_nap_crosstab as TN  # noqa: E402
rs = C.run_one(("scripted", SEED, TICKS, str(CFG), None, None, "served"))
tt = TN.crosstab(CFG, SEED, TICKS)
assert tt["starts"] == sum(rs["beam"]["starts"]) > 0, (tt["starts"], rs["beam"]["starts"])
assert tt["floor"] == 15.0 and abs(tt["sleep_share"] - sum(rs["beam"]["sleep"]) / (TICKS * 5)) < 1e-9
assert C.walk_distance((0, 0), (3, 4)) == 7 and C.walk_distance((2, 2), (2, 2)) == 0, "walking is Manhattan (grid.rs), never king-moves"
print("test_distress_inspect ok", r["max_distress_age_seat"], t["starts"], tt["starts"])
