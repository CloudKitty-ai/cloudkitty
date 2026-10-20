#!/usr/bin/env python3
"""Guards for the step-8 battery extensions (DECLARATION.md; plain
asserts, no pytest): the harness's g2 seat spec + schema keying +
dispersion accounting, and run_legs' seating passthrough. Run with the
lab venv (torch). Kept behavior is guarded by the standing files
(test_run_legs, test_cert_state_key, test_step7_reads)."""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
sys.path.insert(0, str(EXPTS / "fog-gen1-cert"))
sys.path.insert(0, str(EXPTS / "gen2-comparator-legs-2026-10-14"))
sys.path.insert(0, str(EXPTS / "attn-oracle-2026-08-15"))

import cert_harness_fog as ch  # noqa: E402
import run_legs as rl  # noqa: E402

G2LEG20 = EXPTS / "gen2-comparator-legs-2026-10-14" / "g2leg-20.toml"


def test_schema_dims_v6_match_the_layout_module():
    import obs_layout_v6 as ol
    assert ch.SCHEMA_DIMS["v6"] == (ol.OBS_DIM, ol.N_ACT, ol.N_LOGITS), \
        (ch.SCHEMA_DIMS["v6"], (ol.OBS_DIM, ol.N_ACT, ol.N_LOGITS))
    assert ch.SCHEMA_DIMS["v5"] == (408, 39, 55)


def test_artifact_path_resolves_g2_and_ppo_separately():
    g2 = ch.artifact_path("g2:trunk-s1")
    assert g2 == ch.G2_ARTS / "ppo-g2-trunk-s1" / "policy-final.pt", g2
    assert g2.exists(), g2
    ppo = ch.artifact_path("ppo:cand-s2")
    assert "ppo-fog-cand-s2" in str(ppo), ppo


def test_g2_load_model_forwards_v6_logits():
    fwd = ch.load_model("g2:trunk-s1")
    rows = np.zeros((2, ch.SCHEMA_DIMS["v6"][0]), np.float32)
    out = np.asarray(fwd(rows))
    assert out.shape == (2, ch.SCHEMA_DIMS["v6"][2]), out.shape
    assert np.isfinite(out).all()


def test_dispersion_pairs_chains_and_solos():
    stride = ch.PER_KITTY
    w, h = 20, 20

    def state(positions):
        st = np.zeros(len(positions) * stride, np.float32)
        for k, (x, y) in enumerate(positions):
            st[k * stride + ch.POS0] = x / w
            st[k * stride + ch.POS0 + 1] = y / h
        return st

    # pair + solo: (0,0)-(0,1) adjacent, (5,5) alone -> 2 groups
    acc = ch.disp_acc(3)
    ch.disp_account(state([(0, 0), (0, 1), (5, 5)]), 3, w, h, acc)
    assert acc["together_ticks"] == [1, 1, 0], acc
    assert acc["group_count_sum"] == 2 and acc["ticks"] == 1, acc
    # transitive chain (0,0)-(1,0)-(2,0): ONE component of three, even
    # though the ends are 2 apart (catches pairwise-only grouping)
    acc = ch.disp_acc(3)
    ch.disp_account(state([(0, 0), (1, 0), (2, 0)]), 3, w, h, acc)
    assert acc["together_ticks"] == [1, 1, 1], acc
    assert acc["group_count_sum"] == 1, acc
    # same tile counts as together; diagonal (Chebyshev 1, Manhattan 2)
    # does NOT (walk adjacency, movement-is-manhattan)
    acc = ch.disp_acc(2)
    ch.disp_account(state([(3, 3), (3, 3)]), 2, w, h, acc)
    assert acc["together_ticks"] == [1, 1], acc
    acc = ch.disp_acc(2)
    ch.disp_account(state([(3, 3), (4, 4)]), 2, w, h, acc)
    assert acc["together_ticks"] == [0, 0] and acc["group_count_sum"] == 2, acc


def test_run_one_refuses_untruthful_clock_and_deaf_for_g2():
    for args, word in (
        (("g2-s1", 905001, 5, str(G2LEG20), None, None, "train",
          None, None, None), "served"),
        (("g2-s1", 905001, 5, str(G2LEG20), None, None, "served",
          "want", None, None), "schema-5"),
    ):
        try:
            ch.run_one(args)
        except AssertionError as e:
            assert word in str(e), (word, e)
        else:
            raise AssertionError(f"run_one accepted g2 args it must refuse: {args}")


def test_mixed_rosters_are_seat_balanced():
    # MIXED-DECLARATION.md: every network sits in every seat exactly
    # once across the three rosters (seat personality never confounds
    # network identity), each roster is 2-2-1, and each network is the
    # singleton exactly once.
    nets = {"g2:trunk-s1", "g2:trunk-s2", "g2:trunk-s4"}
    mixes = [ch.SEATINGS[f"g2-mix{i}"] for i in (1, 2, 3)]
    for seat in range(5):
        assert {m[seat] for m in mixes} == nets, ("seat", seat, [m[seat] for m in mixes])
    singles = []
    for m in mixes:
        counts = sorted(m.count(n) for n in nets)
        assert counts == [1, 2, 2], (m, counts)
        singles.append(next(n for n in nets if m.count(n) == 1))
    assert sorted(singles) == sorted(nets), singles


def test_run_legs_plan_carries_the_seating_into_cmd_and_gate_file():
    cfgs = {20: "c20.toml", 40: "c40.toml", 100: "c100.toml"}
    stages = rl.plan(cfgs, "g2cmp", 30, 20000, 6, "/tmp/out",
                     scout_seeds=3, seating="g2-s1")
    by_name = {n: (cmd, gate) for n, cmd, gate in stages}
    for n, (cmd, gate) in by_name.items():
        assert cmd[2] == "g2-s1", (n, cmd)
    gate = by_name["scout-40"][1]
    assert str(gate).endswith("g2-s1-g2cmp-3x20000.jsonl"), gate
    # default stays the comparator shape
    stages = rl.plan(cfgs, "g2cmp", 30, 20000, 6, "/tmp/out", scout_seeds=3)
    assert str(dict((n, g) for n, c, g in stages)["scout-40"]).endswith(
        "scripted-g2cmp-3x20000.jsonl")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
