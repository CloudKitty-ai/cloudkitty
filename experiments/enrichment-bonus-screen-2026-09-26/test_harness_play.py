"""Live guard for the cert harness's play block (enrichment-bonus
screen): one short gen1-A leg on the package world, asserted on state
properties the calibration read established, so a wrong activity index
or a start counted on every playing tick shows here.

Run from the repo root:
  CERT_ARTS=experiments/enrichment-bonus-screen-2026-09-26/artifacts \
    experiments/exp-006-character-gen/.venv/bin/python -B \
    experiments/enrichment-bonus-screen-2026-09-26/test_harness_play.py
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
assert os.environ.get("CERT_ARTS"), "CERT_ARTS must point at this screen's artifacts"
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
import cert_harness_fog as H  # noqa: E402

CFG = HERE.parent / "beam-world-screen-2026-09-19" / "package.toml"
TICKS = 600
r = H.run_one(("gen1-A", 870001, TICKS, str(CFG), None, None, "served"))
p = r["play"]
assert len(p["ticks"]) == 5 and all(len(b) == 3 for b in p["start_gate_bins"])
share = [t / TICKS for t in p["ticks"]]
# Biscuit (seat 1, play dial 0.8) dominates play: calibration read
# 2026-09-26 has her at 0.225-0.232 against 0.032-0.049 elsewhere. A
# wrong activity index (Drinking, Grooming...) has no such seat profile.
assert share[1] > 0.10, share
assert all(share[1] > 2 * share[k] for k in (0, 2, 3, 4)), share
# Every seat plays a little (calibration floor 0.03), and the bins are
# an exact partition of the starts.
assert all(s > 0 for s in p["starts"]), p["starts"]
for k in range(5):
    assert sum(p["start_gate_bins"][k]) == p["starts"][k], (k, p)
    assert p["starts"][k] <= p["ticks"][k], (k, p)
# This leg is a prefix of the kept-green 1,500-tick run (deterministic
# greedy, same seed) which carried zero distress ticks, so no start can
# see a distressed teammate here.
assert p["starts_teammate_distressed"] == [0] * 5, p["starts_teammate_distressed"]
print("test_harness_play ok", {"share": [round(s, 3) for s in share], "starts": p["starts"]})
