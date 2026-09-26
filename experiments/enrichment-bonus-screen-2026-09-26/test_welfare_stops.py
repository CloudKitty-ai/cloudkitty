"""Live guards for the two welfare-practice mechanisms (owner ruled
2026-09-26; README §Design discipline names them owed): the cert
harness's --abort-streak and the trainer's futility stop. Both are
exercised end to end where the bug would occur, never on a recorded
row.

Run from the repo root:
  CERT_ARTS=experiments/beam-world-screen-2026-09-19/artifacts \
    experiments/exp-006-character-gen/.venv/bin/python -B \
    experiments/enrichment-bonus-screen-2026-09-26/test_welfare_stops.py

Part A rides the distress leg test_distress_inspect.py pinned (count-7
world, seed 870009, Biscuit's 520-tick drink streak starting near tick
1,692): with the limit at 100 the leg must abort mid-streak; with the
limit far above any streak it must run to length untouched (the
vacuous-guard control).

Part B runs the trainer's smoke recipe with an unreachable bar (2.0 on
a nash scale that tops out near 1) and 2 probes: the run must end as
policy-final.pt with stop_reason "futility-stop" long before the tick
cap.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
BEAM = HERE.parent / "beam-world-screen-2026-09-19"
assert os.environ.get("CERT_ARTS"), "CERT_ARTS must point at the beam screen's artifacts (cnt7-s1 lives there)"
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
import cert_harness_fog as C  # noqa: E402

CFG, SEED, TICKS, SLOT = BEAM / "count-7.toml", 870009, 2300, "cnt7-s1"
STREAK_START = 1692  # documented in test_distress_inspect.py: the 520-tick drink streak

# Part A1: the abort fires mid-streak.
seats = [f"ppo:{SLOT}"] * 5
r = C.run_one(("gen1-A", SEED, TICKS, str(CFG), seats, None, "served", None, None, 100))
assert "aborted_streak" in r, "the 520-tick streak must trip a limit of 100"
assert r["aborted_streak"]["limit"] == 100
assert r["ticks"] == r["aborted_streak"]["at_tick"], (r["ticks"], r["aborted_streak"])
assert r["ticks"] < TICKS, "an aborted leg is shorter than requested"
# The property, not a location (a smaller streak may trip first): the
# abort fires the tick the age REACHES the limit, so at abort time the
# max streak age equals the limit exactly.
assert r["max_distress_age"] == 100, r["max_distress_age"]

# Part A2 (control): a limit above every streak never fires and the row
# is full length, with the documented 520-tick streak intact.
r2 = C.run_one(("gen1-A", SEED, TICKS, str(CFG), seats, None, "served", None, None, 10_000))
assert "aborted_streak" not in r2 and r2["ticks"] == TICKS, (r2.get("aborted_streak"), r2["ticks"])
assert r2["max_distress_age"] >= 520, r2["max_distress_age"]
print(f"part A ok: aborted at tick {r['ticks']} at age exactly 100; control ran {r2['ticks']} (mda {r2['max_distress_age']})")

# Part B: the futility stop ends a smoke run under an unreachable bar.
out = Path(tempfile.mkdtemp(prefix="futility-smoke-"))
try:
    py = str(REPO / "experiments/exp-006-character-gen/.venv/bin/python")
    cmd = [py, str(HERE.parent / "fog-gen1-shakeout/trainer/train_ppo_fog.py"),
           "--slot", "ref-s1", "--smoke", "--init-random",
           "--n-worlds", "2", "--horizon", "200", "--total-ticks", "4096",
           "--probe-every", "1", "--probe-ticks", "100",
           "--futility-bar", "2.0", "--futility-probes", "2",
           "--out-dir", str(out)]
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=1800)
    assert p.returncode == 0, p.stderr[-2000:]
    assert "FUTILITY STOP" in p.stdout, p.stdout[-2000:]
    import torch
    final = torch.load(out / "policy-final.pt", map_location="cpu", weights_only=False)
    assert final["stop_reason"] == "futility-stop", final["stop_reason"]
    probes = [json.loads(l) for l in (out / "metrics.jsonl").read_text().splitlines()
              if '"probe": true' in l]
    assert len(probes) == 2, ("stopped after exactly --futility-probes probes", len(probes))
    print(f"part B ok: futility stop after {len(probes)} probes, stop_reason {final['stop_reason']}")
finally:
    shutil.rmtree(out, ignore_errors=True)

print("test_welfare_stops ok")
