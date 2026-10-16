#!/usr/bin/env python3
"""Guard for dispersion_read.py (plain asserts, no pytest).

Synthetic rollouts write state via INDEPENDENT literals (pos 7,
happiness 6, distress 20 — global_state.rs; never the reader's
constants, the af2e55ed lesson); hand geometry pins the metrics; a
constructed monotone relation pins Spearman's sign; the real v6 dev
trace pins the loader end to end."""
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import dispersion_read as dr  # noqa: E402

ANCHOR_TOML = ROOT / "experiments/fog-gen1-shakeout/anchor.toml"
DEV_V6 = ROOT / ("experiments/gen2-schema-check-2026-10-14/results-raw/"
                 "dev-v6-400/config-00-rollout-00")


def synth_rollout(td, pos, hap=None, distress=None, w=20, h=20, pk=32,
                  radius=5, name="config-00-rollout-00"):
    """pos: (T, roster, 2) tiles; hap: (T, roster) in [0,100];
    distress: (T, roster) bool."""
    rd = Path(td) / name
    rd.mkdir(parents=True)
    pos = np.asarray(pos)
    T, roster, _ = pos.shape
    toml = Path(td) / "world.toml"
    if not toml.exists():
        toml.write_text(f"[world]\nwidth = {w}\nheight = {h}\n")
    state_width = roster * pk + 7 + 30
    state = np.zeros((T, state_width), np.float32)
    # independent literals: happiness 6, position 7/8, distress 20
    for i in range(roster):
        state[:, i * pk + 7] = pos[:, i, 0] / w
        state[:, i * pk + 8] = pos[:, i, 1] / h
        if hap is not None:
            state[:, i * pk + 6] = np.asarray(hap)[:, i] / 100.0
        if distress is not None:
            state[:, i * pk + 20] = np.asarray(distress)[:, i].astype(float)
    np.save(rd / "state.npy", state)
    (rd / "meta.json").write_text(json.dumps(
        {"experts": {str(i + 1): "needs_driven" for i in range(roster)},
         "state_width": state_width, "ticks": T, "vision_radius": radius,
         "config": str(toml)}))
    return rd


def test_start_geometry_hand_literals():
    # 3 cats: (0,0), (0,4), (10,10). Pairwise Manhattan: 4, 20, 16.
    # Mean 40/3, min 4. Visible pairs at r=5 (Euclidean): only (0,0)-(0,4).
    pos = np.tile(np.array([[(0, 0), (0, 4), (10, 10)]]), (6, 1, 1))
    with tempfile.TemporaryDirectory() as td:
        r = dr.read_rollout(synth_rollout(td, pos), early=3)
    assert np.isclose(r["start_mean_pairwise"], 40 / 3), r["start_mean_pairwise"]
    assert r["start_min_pairwise"] == 4
    assert r["start_visible_pairs"] == 1
    assert r["trace_mean_pairwise"] == r["start_mean_pairwise"]  # static world


def test_early_late_windows_read_happiness_and_distress():
    # 4 ticks, 2 cats; happiness falls 100->40 over time; cat 1 in
    # distress for the last 2 ticks. early=2: hap (100+100+80+80)/4=90,
    # distress 0; late=2: hap (60+60+40+40)/4=50, distress 2/4.
    pos = np.tile(np.array([[(1, 1), (2, 2)]]), (4, 1, 1))
    hap = np.array([[100, 100], [80, 80], [60, 60], [40, 40]])
    distress = np.array([[0, 0], [0, 0], [0, 1], [0, 1]], bool)
    with tempfile.TemporaryDirectory() as td:
        r = dr.read_rollout(synth_rollout(td, pos, hap, distress), early=2)
    assert r["early_happiness"] == 90.0, r["early_happiness"]
    assert r["early_distress_share"] == 0.0
    assert r["late_happiness"] == 50.0, r["late_happiness"]
    assert r["late_distress_share"] == 0.5, r["late_distress_share"]


def test_block_trajectory_and_max_streaks():
    # 6 ticks, 2 cats; happiness steps 100->0. Cat 1's distress has TWO
    # separated runs (2 then 1): a counter that fails to reset between
    # runs reads 3, the true max is 2 — the first fixture here had one
    # run per cat and a no-reset mutation survived it (VACUOUS,
    # 2026-10-15). Cat 2: one run of 2. Blocks of 2: means 90, 50, 10.
    pos = np.tile(np.array([[(1, 1), (2, 2)]]), (6, 1, 1))
    hap = np.array([[100, 100], [80, 80], [60, 60], [40, 40], [20, 20], [0, 0]])
    distress = np.array([[1, 0], [1, 0], [0, 0], [1, 0], [0, 1], [0, 1]], bool)
    with tempfile.TemporaryDirectory() as td:
        r = dr.read_rollout(synth_rollout(td, pos, hap, distress),
                            early=2, block=2)
    assert r["block_happiness"] == [90.0, 50.0, 10.0], r["block_happiness"]
    assert r["max_distress_streaks"] == [2, 2], r["max_distress_streaks"]
    assert r["block_ticks"] == 2
    # without the flag, the trajectory keys stay absent
    with tempfile.TemporaryDirectory() as td:
        r = dr.read_rollout(synth_rollout(td, pos, hap, distress), early=2)
    assert "block_happiness" not in r and "max_distress_streaks" not in r


def test_spearman_signs_on_a_constructed_relation():
    # 6 rollouts: wider start dispersion <-> lower early happiness
    # (monotone, non-linear) -> spearman -1; and +1 against itself.
    rollouts = [{"start_mean_pairwise": d, "start_min_pairwise": d,
                 "start_visible_pairs": 10 - d,
                 "early_happiness": 100 - d ** 2, "early_distress_share": 0.0,
                 "late_happiness": 50.0, "late_distress_share": 0.0,
                 "trace_mean_pairwise": float(d), "trace_happiness": 70.0}
                for d in (1, 2, 3, 4, 5, 6)]
    c = dr.correlations(rollouts)
    assert c["n"] == 6
    assert c["start_mean_pairwise"]["early_happiness"] == -1.0
    assert c["start_mean_pairwise"]["trace_mean_pairwise"] == 1.0
    # constant downstream -> None, not a number
    assert c["start_mean_pairwise"]["late_happiness"] is None


def test_small_n_reports_instead_of_correlating():
    c = dr.correlations([{"start_mean_pairwise": 1.0}] * 2)
    assert c["n"] == 2 and "not computed" in c["note"]


def test_real_v6_dev_trace_end_to_end():
    assert DEV_V6.exists(), f"{DEV_V6} missing — recollect the dev trace " \
        "(bc-collect, anchor.toml, 400 ticks, seed 992001)"
    r = dr.read_rollout(DEV_V6, early=100, config_override=str(ANCHOR_TOML))
    assert r["ticks"] == 400 and r["roster"] == 5
    assert 0 < r["start_mean_pairwise"] < 40
    assert 0 <= r["early_distress_share"] <= 1
    assert 0 < r["early_happiness"] <= 100 and 0 < r["late_happiness"] <= 100
    # the anchor's hand starts: (8,10),(16,15),(13,6),(4,4),(10,16)
    # mean pairwise Manhattan = 12.4 by hand; the state must agree.
    assert np.isclose(r["start_mean_pairwise"], 12.4), r["start_mean_pairwise"]


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
