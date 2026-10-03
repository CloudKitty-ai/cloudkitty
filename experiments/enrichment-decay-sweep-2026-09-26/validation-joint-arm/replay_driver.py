"""Professor's induction-hole check: does the CURRENT code reproduce
the RECORDED l14 runs? Re-runs a recorded l14 seed with its recorded
invocation (all defaults: threads 2, total-ticks 20M — the schedules
depend on total_updates, so no shortening) into scratch; the caller
kills the process once 20 metrics rows exist. Trace redirected via
e2b.SCREEN; out-dir in scratch; nothing recorded is touched.
"""
import argparse
import sys
from pathlib import Path

SCRATCH = Path(__file__).resolve().parent
ENRICH = Path("/Users/elizabethkelly/ai/cloudkitty/experiments/enrichment-decay-sweep-2026-09-26")
sys.path.insert(0, str(ENRICH / "trainer"))

import train_ppo_enrich2c as tc  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--slot", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()

tc.e2b.SCREEN = SCRATCH
tc.tb.CURRENT["slot"] = a.slot
tc.tb.install()
tc.tf.SHAKEOUT = SCRATCH
assert tc.SLOT_PARAMS[a.slot][1] is False  # l14 path: stock collect
tc.e2b.SLOT_PARAMS[a.slot] = (tc.BETA, False)
tc.e2b.install_enrich2b(a.slot)
sys.argv = [sys.argv[0], "--slot", a.slot, "--out-dir", a.out]
tc.tf.main()
