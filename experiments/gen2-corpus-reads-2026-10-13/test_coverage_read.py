#!/usr/bin/env python3
"""Guard for coverage_read.py (plain asserts, no pytest).

Synthetic rollouts with hand-placed positions pin the geometry (edge
ring, corners, pooling); the real canonical 20k anchor trace pins the
loader end-to-end (run from the repo root, or the meta's repo-relative
config path misses — the real-trace check passes --config explicitly
so it holds anywhere).
"""
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import coverage_read as cr  # noqa: E402

ANCHOR_TOML = ROOT / "experiments/fog-gen1-shakeout/anchor.toml"
CANONICAL = ROOT / "experiments/fog-gen1-shakeout/results-raw/anchor-resmoke-050-20k"


def synth_rollout(td, positions, w=20, h=20, state_width=197, pk=32):
    """One fake rollout dir. positions: (T, roster, 2) int tile coords,
    roster must be 5 (state_width 197 = 5*32 + 7 + 15*2)."""
    rd = Path(td) / "config-00-rollout-00"
    rd.mkdir(parents=True)
    pos = np.asarray(positions)
    T, roster, _ = pos.shape
    toml = Path(td) / "world.toml"
    toml.write_text(f"[world]\nwidth = {w}\nheight = {h}\n")
    meta = {"experts": {str(i + 1): "needs_driven" for i in range(roster)},
            "state_width": state_width, "ticks": T, "config": str(toml)}
    (rd / "meta.json").write_text(json.dumps(meta))
    state = np.zeros((T, state_width), np.float32)
    for i in range(roster):
        state[:, i * pk + cr.POS_OFF] = pos[:, i, 0] / w
        state[:, i * pk + cr.POS_OFF + 1] = pos[:, i, 1] / h
    np.save(rd / "state.npy", state)
    return rd


def test_geometry_shares_from_hand_placed_positions():
    # kitty 1 parked on the (0,0) corner, kitty 2 on the east edge off
    # the corners, kitties 3-5 interior: pooled edge 8/20, corner 4/20.
    T = 4
    pos = np.zeros((T, 5, 2), int)
    pos[:, 0] = (0, 0)
    pos[:, 1] = (19, 5)
    pos[:, 2] = (10, 10)
    pos[:, 3] = (1, 1)      # one in from the corner: interior
    pos[:, 4] = (5, 18)     # one in from the south edge: interior
    with tempfile.TemporaryDirectory() as td:
        rd = synth_rollout(td, pos)
        r = cr.read_rollout(rd)
    assert r["ticks"] == T and r["roster"] == 5 and r["world"] == [20, 20]
    assert r["global_state_version"] == 1
    assert r["edge_ring_share"] == 8 / 20, r["edge_ring_share"]
    assert r["corner_share"] == 4 / 20, r["corner_share"]
    assert r["per_kitty"]["1"] == {"edge_ring_share": 1.0, "corner_share": 1.0}
    assert r["per_kitty"]["2"] == {"edge_ring_share": 1.0, "corner_share": 0.0}
    for kid in ("3", "4", "5"):
        assert r["per_kitty"][kid] == {"edge_ring_share": 0.0, "corner_share": 0.0}


def test_all_four_corners_and_far_edges_count():
    pos = np.zeros((1, 5, 2), int)
    pos[0] = [(0, 19), (19, 0), (19, 19), (0, 7), (7, 19)]
    with tempfile.TemporaryDirectory() as td:
        r = cr.read_rollout(synth_rollout(td, pos))
    assert r["edge_ring_share"] == 1.0
    assert r["corner_share"] == 3 / 5


def test_source_pooling_weights_by_samples():
    # Two rollouts under one source dir, different lengths: the pooled
    # share is sample-weighted, not a mean of means.
    with tempfile.TemporaryDirectory() as td:
        p1 = np.zeros((1, 5, 2), int)          # all 5 on (0,0): edge 1.0
        p2 = np.full((3, 5, 2), 10, int)       # all interior: edge 0.0
        rd1 = synth_rollout(Path(td) / "a", p1)
        rd2 = synth_rollout(Path(td) / "b", p2)
        src = Path(td)
        r = cr.read_source("x", src)
    assert r["samples"] == 20
    assert r["edge_ring_share"] == 5 / 20, r["edge_ring_share"]


def test_unknown_state_width_refuses():
    try:
        cr.infer_block(198, 5)
    except SystemExit as e:
        assert "198" in str(e) and "refusing" in str(e)
    else:
        raise AssertionError("state_width 198 at roster 5 fits nothing and must refuse")


def test_v2_identity_block_width_is_recognized():
    # global_state.rs v2: per-kitty 40 (identity 14), K=2 summary.
    assert cr.infer_block(5 * 40 + 7 + 30, 5) == (2, 40, 2)
    assert cr.infer_block(197, 5) == (1, 32, 2)


def test_real_canonical_trace_reads_end_to_end():
    r = cr.read_source("corpus", CANONICAL, config_override=str(ANCHOR_TOML))
    assert len(r["rollouts"]) == 3
    assert r["samples"] == 3 * 20000 * 5
    assert 0.0 < r["edge_ring_share"] < 1.0
    assert 0.0 <= r["corner_share"] <= r["edge_ring_share"]
    for ro in r["rollouts"]:
        assert ro["world"] == [20, 20] and ro["global_state_version"] == 1


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
