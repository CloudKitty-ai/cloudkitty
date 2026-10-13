#!/usr/bin/env python3
"""Guard for placement_read.py (plain asserts, no pytest).

A synthetic v5-shaped trace pins the share arithmetic; the canonical
20k anchor trace pins agreement with step7_reads' pooled beam number
(GEN2-INPUTS declares the placement read as "step7_reads beam share" —
this instrument is its schema-keyed home and must not drift from it);
a meta/width mismatch must refuse by name.
"""
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "experiments/attn-oracle-2026-08-15"))
import obs_layouts  # noqa: E402
import placement_read as pr  # noqa: E402

CANONICAL = (ROOT / "experiments/fog-gen1-shakeout/results-raw/"
             "anchor-resmoke-050-20k/config-00-rollout-00")


def synth_dir(td, schema, rows, obs_width=None):
    """rows: list of (kitty_id, activity_name, in_beam)."""
    L = obs_layouts.layout_for(schema)
    rd = Path(td) / "rollout"
    rd.mkdir()
    obs = np.zeros((len(rows), obs_width or L.OBS_DIM), np.float32)
    kitty = np.zeros(len(rows), np.uint32)
    ids = sorted({k for k, _, _ in rows})
    for i, (kid, act, beam) in enumerate(rows):
        kitty[i] = kid
        obs[i, L.SELF_ACTIVITY + L.ACTIVITY_KINDS.index(act)] = 1.0
        obs[i, L.SELF_IN_SUNBEAM] = 1.0 if beam else 0.0
    np.save(rd / "obs.npy", obs)
    np.save(rd / "kitty.npy", kitty)
    (rd / "meta.json").write_text(json.dumps(
        {"observation_schema": schema,
         "experts": {str(k): "needs_driven" for k in ids}}))
    return rd


def test_share_arithmetic_per_seat_and_pooled():
    rows = [(1, "sleeping", True), (1, "sleeping", False), (1, "idle", True),
            (2, "sleeping", True), (2, "eating", False)]
    with tempfile.TemporaryDirectory() as td:
        r = pr.read_dir(synth_dir(td, 5, rows))
    assert r["sleep_ticks"] == 3
    assert r["in_beam_share"] == 2 / 3
    assert r["per_seat"]["1"] == {"sleep_ticks": 2, "in_beam_share": 0.5}
    assert r["per_seat"]["2"] == {"sleep_ticks": 1, "in_beam_share": 1.0}


def test_v6_traces_read_through_the_keyed_layout():
    rows = [(1, "sleeping", True), (2, "sleeping", False)]
    with tempfile.TemporaryDirectory() as td:
        r = pr.read_dir(synth_dir(td, 6, rows))
    assert r["schema"] == 6 and r["in_beam_share"] == 0.5


def test_no_sleep_ticks_reads_none_not_zero():
    with tempfile.TemporaryDirectory() as td:
        r = pr.read_dir(synth_dir(td, 5, [(1, "idle", False)]))
    assert r["sleep_ticks"] == 0 and r["in_beam_share"] is None


def test_meta_width_mismatch_refuses_by_name():
    with tempfile.TemporaryDirectory() as td:
        rd = synth_dir(td, 6, [(1, "idle", False)], obs_width=408)
        try:
            pr.read_dir(rd)
        except SystemExit as e:
            assert "408" in str(e) and "399" in str(e)
        else:
            raise AssertionError("408-wide rows under a schema-6 meta must refuse")


def test_pooling_weights_by_sleep_ticks():
    with tempfile.TemporaryDirectory() as t1, tempfile.TemporaryDirectory() as t2:
        a = synth_dir(t1, 5, [(1, "sleeping", True)])
        b = synth_dir(t2, 5, [(1, "sleeping", False), (1, "sleeping", False),
                              (1, "sleeping", False)])
        out = pr.read([a, b])
    assert out["sleep_ticks"] == 4 and out["in_beam_share"] == 1 / 4


def test_agrees_with_step7_reads_on_the_real_trace():
    sys.path.insert(0, str(ROOT / "experiments/fog-gen1-cert"))
    import step7_reads as s7
    ours = pr.read_dir(CANONICAL)
    theirs = s7.beam_sleep_share(s7.load_rows(CANONICAL))["pooled"]
    assert ours["sleep_ticks"] == theirs["sleep_ticks"]
    assert ours["in_beam_share"] == theirs["in_beam_share"], (
        ours["in_beam_share"], theirs["in_beam_share"])


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
