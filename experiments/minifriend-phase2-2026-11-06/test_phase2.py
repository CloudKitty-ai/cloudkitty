#!/usr/bin/env python3
"""Guards g0–g10 of DECLARATION.md §9; each red on record via scripts/mutate.sh --expect before any seed trains.

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B test_phase2.py [g0a g0b ...]

g0a / g0b / g0c read the trunk's recorded probe dumps and one recorded battery row; g0c re-runs one 20k-tick trunk leg
(trunk minds only; ~2 min). Nothing here writes outside the scratch directory.
"""
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p2_common as C  # noqa: E402

SCRATCH = Path(os.environ.get("P2_SCRATCH", "/tmp/p2-scratch"))


def _probe_rows(seed=40_001):
    z = np.load(C.last_probe_dump("trunk-s1"))
    return C.dump_rows(z, seed)


def g0a():
    """the binding reproduces the trunk's probe world: replaying trunk-s1's last dumped probe (seed 40,001) by its recorded
    actions gives the dumped observation and mask streams exactly, every tick, every seat."""
    rows = _probe_rows()
    O, M = C.replay_dump(rows, 40_001)
    assert O.shape == rows["obs"].shape, (O.shape, rows["obs"].shape)
    bad = np.flatnonzero(~np.all(O == rows["obs"], axis=(1, 2)))
    assert bad.size == 0, f"replay diverges from the dump at tick {bad[0]} (first of {bad.size})"
    assert np.array_equal(M, rows["mask"]), "masks differ"


def g0b():
    """068 restore-vs-replay equality (DECLARATION §12 call 6b): on three recorded probe worlds, snapshot() mid-way and
    restore() reproduces the replay's own tail exactly; so does fork(). Before any 068 read is cited."""
    z = np.load(C.last_probe_dump("trunk-s1"))
    for seed in C.PROBE_SEEDS:
        rows = C.dump_rows(z, seed)
        for mode in ("restore", "fork"):
            O, _M, OB = C.replay_dump(rows, seed, snapshot_at=999, mode=mode)
            assert np.array_equal(O, rows["obs"]), (seed, "the straight replay diverged")
            bad = np.flatnonzero(~np.all(OB == O[1000:], axis=(1, 2)))
            assert bad.size == 0, f"{mode} tail diverges from the replay at tick {1000 + bad[0]} (seed {seed})"


def g0c():
    """the binding reproduces a recorded battery leg: g2-s1 uniform on world 905001 at 20x20 (cert battery results-raw)
    re-run by the harness's run_one on this binding gives the recorded row's team happiness, nash, distress columns."""
    import cert_harness_fog as H
    rec = C.battery_rows("g2-s1", 20)[905_001]
    row = H.run_one(("g2-s1", 905_001, 20_000, str(C.TRUNK_TOML), None, None, "served", None, None, 1_000))
    for k in ("mean_happiness", "max_distress_age", "max_distress_age_seat", "dist_ticks", "low_share", "floor_touches", "ticks"):
        assert row[k] == rec[k], (k, row[k], rec[k])
    assert abs(row["nash"] - rec["nash"]) < 1e-12, (row["nash"], rec["nash"])


GUARDS = {"g0a": g0a, "g0b": g0b, "g0c": g0c}

if __name__ == "__main__":
    names = sys.argv[1:] or [n for n in GUARDS if n != "g0c"]
    for n in names:
        GUARDS[n]()
        print(f"{n} ok", flush=True)
    print(f"{len(names)} passed")
