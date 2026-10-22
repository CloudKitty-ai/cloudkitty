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


def _sizes(p):
    """Independent group sizes (not the harness's union-find): grow each
    cat's walk-adjacency component by breadth-first search."""
    R = len(p)
    out = []
    for k in range(R):
        seen, todo = {k}, [k]
        while todo:
            i = todo.pop()
            for j in range(R):
                if j not in seen and abs(int(p[i][0]) - int(p[j][0])) + abs(int(p[i][1]) - int(p[j][1])) <= 1:
                    seen.add(j)
                    todo.append(j)
        out.append(len(seen))
    return out


def test_hold_update_separates_normal_grouping_from_the_s2_lock():
    # red: holding without the need condition reads normal grouping as held
    z = np.load(HERE / "diag-s2-905008.npz")
    t, pos, needs, act = z["tick"], z["pos"], z["needs"] * 100.0, z["act_state"]
    for window, check in (((t < 17400), "normal"), ((t >= 17950), "lock")):
        acc = ch.hold_acc(5)
        idx = np.flatnonzero(window)
        for i in idx:
            ch.hold_update(_sizes(pos[i]), needs[i, :, 0].tolist(), needs[i, :, 1].tolist(),
                           act[i].tolist(), acc)
        n = len(idx)
        if check == "normal":
            assert sum(acc["group3_ticks"]) / (5 * n) > 0.15, acc["group3_ticks"]
            assert sum(acc["held_ticks"]) == 0, acc["held_ticks"]
        else:
            assert min(acc["held_ticks"]) / n > 0.8, acc["held_ticks"]
            assert acc["shared_hold_longest"] >= 100, acc["shared_hold_longest"]


def test_hold_update_does_not_count_a_cat_that_is_eating():
    # red: the tending exclusion dropped (analytic: cat 0 grouped at eat 90,
    # eating on tick 0, idle on tick 1 -> held once)
    acc = ch.hold_acc(5)
    for slot in (ch.EAT_ACT, 0):
        ch.hold_update([3, 3, 3, 1, 1], [90.0, 0, 0, 0, 0], [0.0] * 5,
                       [slot, 0, 0, 0, 0], acc)
    assert acc["held_ticks"] == [1, 0, 0, 0, 0], acc["held_ticks"]
    assert acc["group3_ticks"] == [2, 2, 2, 0, 0], acc["group3_ticks"]


def test_run_one_group3_matches_an_independent_read_of_the_same_world():
    # red: the harness's group sizes wrong (the read the holding rides on)
    sys.path.insert(0, str(EXPTS / "seating-analysis-g2-2026-10-21"))
    import seating_collect_g2 as sc
    arrays, _meta = sc.collect("g2-s1", 905001, 300, 1000)
    row = ch.run_one(("g2-s1", 905001, 300, str(G2LEG20), None, None, "served", None, None, 1000))
    want = np.mean([[s >= 3 for s in _sizes(p)] for p in arrays["pos"]], 0).round(6).tolist()
    assert row["holding"]["group3_share"] == want, (row["holding"]["group3_share"], want)
    assert max(want) > 0, want


def _shape_from_streams(z):
    """Feed recorded collector streams through the harness's pure shape
    account (flags from the bitmask, partner from the stream, moved from
    successive positions)."""
    fl = np.unpackbits(z["distress"][:, :, None].astype(np.uint8), axis=2,
                       bitorder="little")[:, :, :6].astype(bool)
    pos = z["pos"].astype(int)
    acc = ch.shape_acc(fl.shape[1])
    for t in range(len(fl)):
        moved = [False] * fl.shape[1] if t == 0 else (np.abs(pos[t] - pos[t - 1]).sum(1) > 0).tolist()
        ch.shape_update(fl[t].tolist(), z["activity"][t].tolist(),
                        (z["partner"][t, :, 0] == 1).tolist(), moved, acc)
    return ch.shape_close(acc)


def test_shape_kinds_analytic():
    # red: matched relief read as parked, or a moving cat read as parked
    acc = ch.shape_acc(2)
    eat_flag = [[True, False, False, False, False, False], [False] * 6]
    for slot, moved in ((4, False), (3, False), (0, True), (0, False)):   # drink, eat, walk, idle
        ch.shape_update(eat_flag, [slot, 0], [False, False], [moved, False], acc)
    ch.shape_update([[False] * 6, [False] * 6], [0, 0], [False, False], [False, False], acc)
    best = ch.shape_close(acc)[0]
    assert best == {"length": 4, "need": "eat", "tending": 0.25, "parked": 0.25,
                    "idle": 0.25, "moving": 0.25, "other": 0.0}, best
    # resting WITH a friend tends cuddle; grooming a friend does not tend bath
    assert ch.shape_kind(4, 1, True, False) == 0 and ch.shape_kind(5, 6, True, False) == 4


def test_shape_reads_the_recorded_s7_water_parking_as_parked():
    # red: the drink-while-sated run read as tending or idle (real payload:
    # rotation rot1 world 905002, s7 at Clementine, the 121-tick cuddle run)
    z = np.load(EXPTS / "seating-analysis-g2-2026-10-21/results-raw/g2-rot1/streams-905002.npz")
    best = _shape_from_streams(z)[4]
    assert (best["length"], best["need"]) == (121, "cuddle"), best
    assert best["parked"] >= 0.4 and best["tending"] <= 0.05, best


def test_run_one_streak_shape_matches_the_collector_streams_of_the_same_world():
    # red: the harness wiring (moved, partner or flags) drifts from the pure
    # account; scripted roster, so no covered minds are exposed
    sys.path.insert(0, str(EXPTS / "seating-analysis-g2-2026-10-21"))
    import seating_collect_g2 as sc
    row = ch.run_one(("scripted", 905002, 3000, str(G2LEG20), None, None, "served", None, None, 1000))
    arrays, _meta = sc.collect("scripted", 905002, 3000, 1000)
    got, want = row["streak_shape"], _shape_from_streams(arrays)
    assert got == want, (got, want)
    assert [s["length"] for s in got] == row["max_distress_age_seat"], (got, row["max_distress_age_seat"])
    assert max(s["length"] for s in got) > 0


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


def test_swap_seatings_replace_exactly_one_rot2_seat_with_the_alternate():
    # SWAPS-DECLARATION.md: g2-rot2-swap<k>-<net> is rot2 with seat k
    # alone holding the alternate; 15 names, one per (seat, alternate).
    # red: the swap writes the alternate into every seat but k
    rot2 = ch.SEATINGS["g2-rot2"]
    names = [n for n in ch.SEATINGS if n.startswith("g2-rot2-swap")]
    assert len(names) == 15, names
    for net in ("s8", "s9", "s10"):
        for k in range(5):
            s = ch.SEATINGS[f"g2-rot2-swap{k}-{net}"]
            diff = [i for i in range(5) if s[i] != rot2[i]]
            assert diff == [k], (net, k, s)
            assert s[k] == f"g2:trunk-{net}", (net, k, s)


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
