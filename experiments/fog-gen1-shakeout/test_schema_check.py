#!/usr/bin/env python3
"""Guard for schema_check.py (plain asserts, no pytest).

    test_schema_check.py TRACE_DIR

Every row A1-A18 is shown red once: a real trace is loaded, one named
defect is planted in a copy (an observation cell, a mask bit, a snapshot
field or a table entry), and the row must stop being "ok". The unplanted
trace must read green on every row first, so a red here is the plant and
not the trace. A17 is driven with a synthetic policy dump.
"""
import copy
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import schema_check as sc  # noqa: E402
from schema_check import (  # noqa: E402
    BLOCKS, HERE_KINDS, KITTY_SPAN, KITTY_W, N_ACT, N_KITTY, ROW_ANSWERS_ME,
    ROW_MSG_BLOCK, ROW_PRESENT, ROW_SUNBEAM_BIT, ROW_WATER_BIT, SELF_MEMORY,
    SLOT_PRESENT, WANT_KINDS, kitties_by_id, row_state)

BASE = None
DECLARED = json.loads((HERE / "declared_constant.json").read_text())


def fresh():
    """A copy of the loaded trace the test may deface."""
    tr = copy.copy(BASE)
    tr.obs = BASE.obs.copy()
    tr.mask = BASE.mask.copy()
    tr.lines = json.loads(json.dumps(BASE.lines))
    return tr


def rows_of(tr, i):
    return tr.obs[i, KITTY_SPAN[0]:KITTY_SPAN[1]].reshape(N_KITTY, KITTY_W)


def find_row(tr, state):
    """(obs row, slot, tick line index, observer, friend) for the first
    kitty row in `state`."""
    for i, line in enumerate(tr.lines):
        snap = line["snapshot"]
        byid = kitties_by_id(snap)
        for me_id, table in line["tables"].items():
            me = byid[int(me_id)]
            for k, fid in enumerate(table["kitties"]):
                if fid is None:
                    continue
                st, _ = row_state(snap, me, byid[fid], tr.radius, tr.window)
                if st == state:
                    return tr.row_of[(snap["tick"], me["id"])], k, i, me["id"], fid
    raise AssertionError(f"no {state} row in the trace")


def first_meow(tr, pred):
    for i, line in enumerate(tr.lines):
        snap = line["snapshot"]
        for m in snap["recent_meows"]:
            if m["tick"] == snap["tick"] - 1 and pred(m):
                return i, m
    raise AssertionError("no meow matches")


def not_ok(finding):
    assert finding.status != "ok", f"{finding.row} still ok: {finding.summary}"


def test_unplanted_trace_is_green():
    # the baseline every plant is measured against
    for f in sc.run_all(BASE, DECLARED):
        assert f.status in ("ok", "n/a"), f"{f.row} {f.status}: {f.summary}"


def test_a1_undeclared_constant_and_stale_reason():
    # red: a constant column no reason covers; stale: a reason whose
    # column moved
    tr = fresh()
    assert sc.check_a1(tr, {}).status == "RED"
    declared = dict(DECLARED, **{"clock never moves": ["clock"]})
    f = sc.check_a1(tr, declared)
    assert f.status == "ok" and f.detail["stale"] == ["clock never moves"]


def test_a2_memory_token_without_a_remembered_slot():
    # red: the self memory token says "chow remembered" while the
    # snapshot slot is None
    tr = fresh()
    slot = sc.ELEMENT_KINDS.index("chow")
    i = int(np.flatnonzero(tr.obs[:, SELF_MEMORY + slot * sc.MEMORY_SLOT] == 0)[0])
    tr.obs[i, SELF_MEMORY + slot * sc.MEMORY_SLOT] = 1.0
    not_ok(sc.check_a2(tr))


def test_a3_present_on_a_heard_row():
    # red: a friend outside the disc reads present
    tr = fresh()
    r, k, *_ = find_row(tr, "heard")
    rows_of(tr, r)[k, ROW_PRESENT] = 1.0
    not_ok(sc.check_a3(tr))


def test_a4_call_position_tracks_the_live_cat():
    # red: a meow stamped where the speaker was not
    tr = fresh()
    i, m = first_meow(tr, lambda m: True)
    m["pos"] = {"x": (m["pos"]["x"] + 7) % tr.snap(0)["width"], "y": m["pos"]["y"]}
    not_ok(sc.check_a4(tr))


def test_a5_heard_row_with_an_empty_digest():
    # red: heard, but the message block is zero
    tr = fresh()
    r, k, *_ = find_row(tr, "heard")
    rows_of(tr, r)[k, ROW_MSG_BLOCK:ROW_MSG_BLOCK + sc.MSG_BLOCK] = 0.0
    not_ok(sc.check_a5(tr))


def test_a6_want_stamp_outside_the_callers_need():
    # red: intensity 1.0 on a want whose caller was nowhere near 100
    tr = fresh()
    i, m = first_meow(tr, lambda m: m["kind"] in WANT_KINDS and m["intensity"] < 0.9)
    m["intensity"] = 1.0
    not_ok(sc.check_a6(tr))


def test_a7_answers_me_bit_without_a_want():
    # red: a bit lit for an observer who never asked
    tr = fresh()
    r, k, *_ = find_row(tr, "seen")
    row = rows_of(tr, r)[k]
    assert not row[ROW_ANSWERS_ME:ROW_ANSWERS_ME + len(HERE_KINDS)].any()
    row[ROW_ANSWERS_ME] = 1.0
    not_ok(sc.check_a7(tr))


def test_a8_reply_stamp_with_no_paired_want():
    # red: a plain here-word re-stamped as a reply
    tr = fresh()
    i, m = first_meow(tr, lambda m: m["kind"] in HERE_KINDS and not m["reply"])
    snap = tr.snap(i)
    want = sc.WANT_FOR_HERE[m["kind"]]
    assert not any(x["kind"] == want and x["kitty_id"] != m["kitty_id"]
                   and sc.audible(x, m["tick"], tr.window) for x in snap["recent_meows"])
    m["reply"] = True
    not_ok(sc.check_a8(tr))


def test_a9_want_word_with_relief_in_memory():
    # red: want_drink while water is remembered (known relief, both ends)
    tr = fresh()
    i, m = first_meow(tr, lambda m: m["kind"] in WANT_KINDS)
    m["kind"] = "want_drink"
    not_ok(sc.check_a9(tr))


def test_a10_waypoint_index_off_rule():
    # red: an index that jumps two waypoints in one tick
    tr = fresh()
    k = tr.snap(3)["kitties"][0]
    k["explore_waypoint"] = k["explore_waypoint"] + 2
    not_ok(sc.check_a10(tr))


def test_a11_water_bit_on_dry_ground():
    # red: a seen friend flagged on water while its tile holds none
    tr = fresh()
    r, k, i, me, fid = find_row(tr, "seen")
    snap = tr.snap(i)
    assert not sc.tile_holds(snap, kitties_by_id(snap)[fid]["pos"], "water")
    rows_of(tr, r)[k, ROW_WATER_BIT] = 1.0
    not_ok(sc.check_a11(tr))


def test_a12_filled_slot_with_nothing_in_view():
    # red: a critter slot present with no visible critter behind it
    tr = fresh()
    off, _w = BLOCKS[N_KITTY + 6 + 3]        # critter slot 3, never filled
    assert not tr.obs[:, off + SLOT_PRESENT].any()
    tr.obs[0, off + SLOT_PRESENT] = 1.0
    not_ok(sc.check_a12(tr))


def test_a13_required_category_never_emitted():
    # unproven: no seen row ever shows the sunbeam bit
    tr = fresh()
    rows = tr.obs[:, KITTY_SPAN[0]:KITTY_SPAN[1]].reshape(len(tr.obs), N_KITTY, KITTY_W)
    rows[..., ROW_SUNBEAM_BIT] = 0.0
    not_ok(sc.check_a13(tr))


def test_a14_kitty_menu_on_an_unseen_row():
    # red: RestWith slot k legal while row k is not Seen
    from obs_layout_v5 import KITTY_MENU
    tr = fresh()
    r, k, *_ = find_row(tr, "heard")
    tr.mask[r, KITTY_MENU[k][0]] = True
    not_ok(sc.check_a14(tr))


def test_a15_row_order_moves():
    # red: two table entries swapped for one observer on one tick
    tr = fresh()
    table = next(iter(tr.lines[5]["tables"].values()))["kitties"]
    table[0], table[1] = table[1], table[0]
    not_ok(sc.check_a15(tr))


def test_a16_bit_without_a_reply_stamp():
    # red: the freshest here-word behind a lit bit was not a reply
    tr = fresh()
    for i, line in enumerate(tr.lines):
        snap = line["snapshot"]
        hit = False
        for me_id, table in line["tables"].items():
            row = rows_of(tr, tr.row_of[(snap["tick"], int(me_id))])
            for k, fid in enumerate(table["kitties"]):
                for j, here in enumerate(HERE_KINDS):
                    if fid is not None and row[k, ROW_ANSWERS_ME + j] > 0:
                        t = sc.freshest_tick(snap, fid, here, tr.window)
                        for m in snap["recent_meows"]:
                            if m["kitty_id"] == fid and m["kind"] == here and m["tick"] == t:
                                m["reply"] = False
                                hit = True
        if hit:
            break
    assert hit
    not_ok(sc.check_a16(tr))


def test_a17_policy_moves_a_corpus_constant(tmp):
    # red: the policy dump varies a column the corpus never moved
    tr = fresh()
    pobs = tr.obs.copy()
    col = int(np.flatnonzero(tr.obs.var(0) == 0)[0])
    pobs[0, col] = 1.0 - pobs[0, col]
    path = tmp / "policy.npz"
    np.savez(path, obs=pobs)
    not_ok(sc.check_a17(tr, path))
    np.savez(path, obs=tr.obs)
    assert sc.check_a17(tr, path).status == "ok"


def test_a18_reencode_verdict_false():
    # red: one re-encode reported unequal
    tr = fresh()
    line = tr.lines[7]
    key = next(iter(line["reencode_identical"]))
    line["reencode_identical"][key] = False
    not_ok(sc.check_a18(tr))


if __name__ == "__main__":
    import tempfile
    trace_dir = Path(sys.argv[1])
    BASE = sc.load_trace(trace_dir)
    with tempfile.TemporaryDirectory() as td:
        for name, fn in sorted(globals().items()):
            if not name.startswith("test_"):
                continue
            if name == "test_a17_policy_moves_a_corpus_constant":
                fn(Path(td))
            else:
                fn()
            print(f"ok {name}")
