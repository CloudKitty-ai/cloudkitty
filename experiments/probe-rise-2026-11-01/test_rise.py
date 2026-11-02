#!/usr/bin/env python3
"""Guards for rise.py (DECLARATION.md section 7); every red via
`scripts/mutate.sh --expect` before the read runs.

  r1  the copied accounting reproduces the ladder's cells (level alarms
      through rise.cells_from_alarms equal ladder.world_cells on the first
      E and N tuning worlds, probe seed 1) and step 7's committed confirming
      record at the pick
  r2  the step statistic on a hand series: NaN before 2w - 1, zero on a flat
      stretch, the alarm run of a +2 step at k = 1, no alarm across a gap
  r3  the halves: rise.worlds("tuning") is the ladder's world list, the two
      halves partition set_run.worlds(), no world is in both
  r4  the selection rule on a hand grid: the bound is inclusive, ties go to
      the smaller w then the smaller k, no candidate -> None

    test_rise.py [r1 r2 r3 r4]      # default: all
"""
import json
import sys
import traceback
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rise  # noqa: E402
R, L = rise.R, rise.L

_fix = {}


def _probe1():
    import torch
    torch.set_num_threads(1)
    if "p1" not in _fix:
        _fix["p1"] = R.load_probe(1)[:2]
    return _fix["p1"]


KEYS = ("latency", "lead", "lead_not_at_offset_B", "fa", "fa_at_offset_B", "fa_run_ticks")


def _mine(arm, k, seed, ticks, path, half, keep):
    model, probe = _probe1()
    return rise.world_record(arm, k, seed, ticks, path, half, {1: (model, probe)}, keep)


def test_r1_the_accounting_reproduces_the_ladders_cells():
    # red: `cell["latency"][str(k)] = int(hit[0])` -> `int(hit[0]) + 1` in rise.cells_from_alarms
    # -> the first compare (arm E, L:t0.05-B2, latency) fails
    model, probe = _probe1()
    for arm in ("E", "N"):
        arm_, k, seed, ticks, path = [w for w in rise.worlds("tuning") if w[0] == arm][0]
        mine = _mine(arm_, k, seed, ticks, path, "tuning", list(rise.LEVEL))
        theirs = L.world_record(arm_, k, seed, ticks, path, {1: (model, probe)})
        assert mine["crossing"] == theirs["crossing"] and mine["onset"] == theirs["onset"] and mine["stratum"] == theirs["stratum"]
        assert mine["sight_at_crossing"] == theirs["sight_at_crossing"] and mine["observer_ticks"] == theirs["observer_ticks"]
        for name, (th, b) in rise.LEVEL.items():
            a, bb = mine["cells"]["1"][name], theirs["cells"]["1"][L.cell_name(th, b)]
            for key in KEYS:
                assert a[key] == bb[key], (arm, name, key, a[key], bb[key])
    # step 7's committed record of the first confirming arm N world at the pick
    s7 = json.loads((rise.STEP7).read_text())
    rec = [r for r in s7["records"] if r["half"] == "confirming" and r["arm"] == "N"][0]
    arm_, k, seed, ticks, path = [w for w in rise.worlds("confirming") if (w[0], w[1], w[2]) == ("N", rec["block"], rec["seed"])][0]
    mine = _mine(arm_, k, seed, ticks, path, "confirming", [rise.PICK])
    a, bb = mine["cells"]["1"][rise.PICK], rec["cells"]["1"]["t0.05-B2"]
    for key in KEYS:
        assert a[key] == bb[key], ("confirming", key, a[key], bb[key])


def test_r2_the_step_statistic_on_a_hand_series():
    # red: `cs[t - w + 1]` -> `cs[t - w]` in the recent window of rise.step_stat
    # -> the recent mean runs over w + 1 ticks; s[104] and s[109] still read
    # 1.0 and 2.0 but s[114] reads 1.2 (recent 2.2 minus prior 1.0): the
    # falling-side assertion fails first
    w, T = 10, 300
    l = np.zeros((T, 1))
    l[100:] = 2.0
    s = rise.step_stat(l, w)[:, 0]
    assert np.isnan(s[:2 * w - 1]).all(), "defined before 2w - 1"
    assert s[2 * w - 1] == 0.0 and s[99] == 0.0, "a flat stretch is not a rise"
    # the step: s climbs 0.2 per tick from t = 100, peaks at 2.0 at t = 109, falls back to 0 at t = 119
    assert abs(s[104] - 1.0) < 1e-12 and abs(s[109] - 2.0) < 1e-12, (s[104], s[109])
    assert abs(s[114] - 1.0) < 1e-12 and abs(s[119]) < 1e-12, f"s[114] = {s[114]}, s[119] = {s[119]}"
    with np.errstate(invalid="ignore"):
        alarm = s >= 1.0
    assert L.runs(alarm) == [(104, 115)], L.runs(alarm)
    # a missing value poisons every window that holds it, nothing else
    l2 = l.copy()
    l2[150] = np.nan
    s2 = rise.step_stat(l2, w)[:, 0]
    assert np.isnan(s2[150:170]).all() and not np.isnan(s2[149]) and not np.isnan(s2[170])
    assert np.array_equal(np.nan_to_num(s2[:150], nan=-9), np.nan_to_num(s[:150], nan=-9))
    # a series shorter than 2w has no defined value
    assert np.isnan(rise.step_stat(np.zeros((2 * w - 1, 1)), w)).all()
    # the alarm families compose as declared (read at k = 0.5, whose crossings
    # sit 0.1 clear of the recovered logit's rounding: s >= 0.5 from t = 102
    # (0.6) to t = 116 (0.6), off at 117 (0.4))
    P = 1 / (1 + np.exp(-l))[:, :, None].repeat(5, 1).repeat(5, 2)
    al = rise.alarms(P)
    r, b = al[rise.cell_name(w, 0.5, "rise")]
    assert b == 2 * w - 1 and L.runs(r[:, 0, 1]) == [(102, 117)], (b, L.runs(r[:, 0, 1]))
    lvl, _ = al[rise.PICK]
    assert np.array_equal(al[rise.cell_name(w, 0.5, "rise|L")][0], r | lvl)
    assert np.array_equal(al[rise.cell_name(w, 0.5, "rise+f")][0], r & (P >= rise.FLOOR))


def test_r3_the_halves_partition_the_set_and_tuning_is_the_ladders_list():
    # red: `== half` -> `!= half` in rise.worlds -> the tuning list is the confirming list
    tun = rise.worlds("tuning")
    assert [(a, k, s) for a, k, s, _t, _p in tun] == [(a, k, s) for a, k, s, _t, _p in L.worlds()], "tuning worlds differ from the ladder's"
    con = rise.worlds("confirming")
    key = lambda ws: {(a, k, s) for a, k, s, _t, _p in ws}
    assert not (key(tun) & key(con)), "a world in both halves"
    assert key(tun) | key(con) == {(a, k, s) for a, k, _c, s, _t, _p in rise.SR.worlds()}, "the halves do not partition the set"
    assert len(tun) == len(con) == 180, (len(tun), len(con))
    for a, k, s, _t, _p in con:
        R.refuse_unless(a, k, s, "confirming")


def test_r4_the_selection_rule_on_a_hand_grid():
    # red: `r["fa_cov"] <= bound["fa_cov"]` -> `<` in rise.select_from -> the cell sitting
    # exactly on the bound (the best) drops out and w25-k1.0 is chosen instead of w10-k0.5
    bound = {"fa_cov": 0.70, "fa_scr": 1.50}
    rows = {
        "w10-k0.5": {"w": 10, "k": 0.5, "det_N": 0.60, "fa_cov": 0.70, "fa_scr": 1.50},   # on the bound: a candidate
        "w25-k1.0": {"w": 25, "k": 1.0, "det_N": 0.55, "fa_cov": 0.10, "fa_scr": 0.20},
        "w25-k0.5": {"w": 25, "k": 0.5, "det_N": 0.55, "fa_cov": 0.10, "fa_scr": 0.20},   # ties with w25-k1.0: smaller k wins
        "w50-k0.5": {"w": 50, "k": 0.5, "det_N": 0.90, "fa_cov": 0.71, "fa_scr": 0.20},   # over the covered bound
        "w100-k0.5": {"w": 100, "k": 0.5, "det_N": 0.90, "fa_cov": 0.10, "fa_scr": 1.51},  # over the scripted bound
        "w10-k3.0": {"w": 10, "k": 3.0, "det_N": None, "fa_cov": 0.0, "fa_scr": 0.0},     # no stratum populated
    }
    sel = rise.select_from(rows, bound)
    assert sel["chosen"] == "w10-k0.5", sel
    assert sel["candidates"] == ["w10-k0.5", "w25-k0.5", "w25-k1.0"], sel
    rows2 = {c: r for c, r in rows.items() if c != "w10-k0.5"}
    assert rise.select_from(rows2, bound)["chosen"] == "w25-k0.5"
    rows3 = {c: r for c, r in rows2.items() if c != "w25-k0.5"}
    rows3["w10-k1.0"] = {"w": 10, "k": 1.0, "det_N": 0.55, "fa_cov": 0.10, "fa_scr": 0.20}   # ties with w25-k1.0: smaller w wins
    assert rise.select_from(rows3, bound)["chosen"] == "w10-k1.0"
    assert rise.select_from({"w50-k0.5": rows["w50-k0.5"]}, bound)["chosen"] is None
    # the cell names round-trip
    for c in rise.rise_cells():
        w, k, fam = rise.parse_cell(c)
        assert rise.cell_name(w, k, fam) == c


def main(argv):
    names = [n for n in sorted(globals()) if n.startswith("test_")]
    want = argv[1:]
    if want:
        names = [n for n in names if any(n.startswith(f"test_{w}_") for w in want)]
    failed = 0
    for n in names:
        try:
            globals()[n]()
            print(f"PASS {n}")
        except Exception:
            failed += 1
            print(f"FAIL {n}")
            traceback.print_exc(file=sys.stdout)
    print(f"{len(names) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
