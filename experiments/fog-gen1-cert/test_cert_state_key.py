#!/usr/bin/env python3
"""Guard for cert_harness_fog's global-state stride keying (plain
asserts, no pytest). Before 2026-10-14 the harness read the state with
an unconditional PER_KITTY = 32 (global-state v1); on the rebuilt
binding the state is v2 (stride 40) and every happiness/distress read
landed mid-block, silently.

The twin below re-reads happiness from the same deterministic world
with INDEPENDENT literals (v2 roster-5 width 237, stride 40, happiness
at 6 — global_state.rs), so a harness that mis-keys the stride
disagrees with it. The literals also refuse a future engine move: if
the state width leaves 237 this guard fails by name and gets re-keyed
deliberately.
"""
import sys
import tomllib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cert_harness_fog as ch  # noqa: E402

CONFIG = HERE / "anchor-b3.toml"
SEED, TICKS = 870_001, 40
# Independent literals, never coverage_read's tables: global-state v2,
# roster 5, two element slots per type -> 5*40 + 5*(1+2*3) + 2 = 237.
V2_WIDTH, V2_STRIDE, V2_HAP = 237, 40, 6


def twin_mean_happiness():
    import cloudkitty
    with open(CONFIG, "rb") as f:
        cfg = tomllib.load(f)
    control = {f"kitty_{k['id']}": k["behavior"] for k in cfg["kitty"]}
    env = cloudkitty.ParallelEnv(str(CONFIG), control=control, horizon=TICKS)
    env.reset(seed=SEED)
    st0 = np.asarray(env.state(), np.float32)
    assert st0.size == V2_WIDTH, (
        f"twin expects the v2 roster-5 state width {V2_WIDTH}, engine says "
        f"{st0.size} — the layout moved; re-key this guard deliberately")
    hap = np.zeros(5)
    for _ in range(TICKS):
        env.step({})
        st = np.asarray(env.state(), np.float32)
        hap += st[V2_HAP:5 * V2_STRIDE:V2_STRIDE].astype(np.float64) * 100
    return (hap / TICKS).round(4).tolist()


def test_run_one_happiness_matches_independent_v2_read():
    row = ch.run_one(("scripted", SEED, TICKS, str(CONFIG), None, None,
                      "served", None, None, None))
    want = twin_mean_happiness()
    assert row["mean_happiness"] == want, (row["mean_happiness"], want)
    assert row["ticks"] == TICKS


def test_harness_keys_stride_from_the_live_state():
    ch.run_one(("scripted", SEED, 2, str(CONFIG), None, None,
                "served", None, None, None))
    assert ch.PER_KITTY == V2_STRIDE, ch.PER_KITTY


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
