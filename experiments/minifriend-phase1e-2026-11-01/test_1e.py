#!/usr/bin/env python3
"""Guards for Phase 1e (DECLARATION.md §7); every red via
`scripts/mutate.sh --expect` on the committed files before the training
set is collected, the heads trained, or any read runs.

  e1  the data module: on a 1b world data_1e's pairs and arrays equal
      phase1_data's (20 pairs; x, y, vis, code identical); on a needy-set
      world (the TN format, same collector, same config) the observers are
      the four covered seats, the scripted seat is a friend of each, and x /
      vis equal needy_read.pair_x
  e2  the split: split.json is split_1e.py's; 1b's eight sets verbatim and
      first (phase1_data.roles() on this arc carves the 1b validation worlds
      exactly as the frozen NF-h24-s1 manifest records); TN / TE seeds lie
      inside the claimed band, disjoint from every needy-set band and its
      held seeds, 23 / 8 per block; no evaluation world
  e3  the selection rule on a hand grid: the bound is inclusive, ties go to
      the higher threshold then the smaller burn-in, no candidate -> None;
      cell names round-trip; the bound read from the ladder is the frozen
      pick's tuning rates
  e4  the needy reader (read_1e.world_record with level alarms) reproduces
      the ladder's cells on the first E and N tuning worlds (frozen probe
      seed 1, the pick and the registered cells) and step 7's committed
      confirming arm N record at the pick
  e5  the splice reader with the frozen NF-h24+p at H = 100 reproduces the
      committed phase1d-history.json rows per seed (detected, control
      fired) at 0.10; the committed-rows loader carries 0 … 2000
  e6  the estimate reader with the frozen NF-h24 pred files reproduces 1b's
      pooled mind-visible GRAVE mse5 on group P per seed and the seed mean
      908.0954 (phase1b-read.json /reads/24/P/heads/NF/mse5/visible/GRAVE/pooled)
  e7  the lived reader: the committed pgrave of NF-h24-s1+p on group P at
      0.10 / B 0 reproduces the sweep's reset detection row and false-run
      rate (phase1d-sweep.json); the burn-in forces exactly the first B
      ticks of every slice off

    test_1e.py [e1 e2 ...]      # default: all (e4-e7 load the frozen heads; about two minutes)
"""
import json
import os
import subprocess
import sys
import traceback
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
NEEDY = EXPTS / "needy-set-2026-10-28"
PHASE1B = EXPTS / "minifriend-phase1b-2026-10-23"
PHASE1D = EXPTS / "minifriend-phase1d-2026-10-24"
sys.path.insert(0, str(HERE))
import read_1e as RE  # noqa: E402

KEYS = ("latency", "lead", "lead_not_at_offset_B", "fa", "fa_at_offset_B", "fa_run_ticks")
_fix = {}


def _torch1():
    import torch
    torch.set_num_threads(1)


# ---- e1 / e2 run data_1e in a subprocess: it pins MINIFRIEND_ARC to this arc, the readers pin theirs ----

def _sub(code):
    env = dict(os.environ)
    env.pop("MINIFRIEND_ARC", None)
    r = subprocess.run([sys.executable, "-B", "-c", code], cwd=str(HERE), env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(r.stdout + r.stderr)
    return r.stdout


def test_e1_the_data_module_matches_phase1_data_and_needy_read():
    # red: `for k in w["observers"]` -> `for k in range(ROSTER)` in data_1e.pairs
    # -> the needy world yields 20 pairs and the first assertion on it (16 pairs) fails
    _sub(f"""
import sys, json, numpy as np
sys.path.insert(0, {str(HERE)!r})
import data_1e as E
import phase1_data as D
from pathlib import Path
D.ARC = Path({str(PHASE1B)!r})          # phase1_data reads raws under its arc root; 1b's hold P1
w = E.load_world("P1", 1095451); wd = D.load_world("P1", 1095451)
assert w["observers"] == [0, 1, 2, 3, 4] and list(E.pairs(w)) == list(D.pairs(wd)) and len(list(E.pairs(w))) == 20
for k, j in [(0, 1), (3, 4), (4, 0)]:
    a, b = E.pair_arrays(w, k, j), D.pair_arrays(wd, k, j)
    for i in range(4):
        assert np.array_equal(a[i], b[i]), (k, j, i)
sys.path.insert(0, {str(NEEDY)!r})
import needy_read as R
p = {str(NEEDY / 'results-raw/set/N1/streams-1095711.npz')!r}
E.SPLIT["sets"]["TN1"]["ticks"] = 6000
E.NEW_SETS.append("TNX"); E.SPLIT["sets"]["TNX"] = dict(E.SPLIT["sets"]["TN1"], raw_dir="needy-set-2026-10-28/results-raw/set/N1")
w = E.load_world("TNX", 1095711); wr = R.load_world(p)
prs = list(E.pairs(w))
assert len(prs) == 16, ("a scripted seat admitted as an observer", len(prs))
assert w["observers"] == [1, 2, 3, 4] and w["scripted"] == [0] and all(k != 0 for k, _j in prs) and sum(j == 0 for _k, j in prs) == 4
assert prs == R.observer_pairs(wr)
for k, j in [(1, 0), (4, 2)]:
    x, y, vis, code = E.pair_arrays(w, k, j); xr, vr = R.pair_x(wr, k, j)
    assert np.array_equal(x, xr) and np.array_equal(vis, vr) and np.array_equal(code, wr["codes"][:, j])
    assert np.allclose(y[:, :5] * 100.0, wr["needs"][:, j, :5]) and np.allclose(y[:, 5] * 100.0, wr["hap"][:, j])
try:
    E.pair_arrays(w, 0, 1); raise SystemExit("the scripted seat built a pair")
except AssertionError:
    pass
print("e1 ok")
""")


def test_e2_the_split_is_1bs_sets_verbatim_plus_the_claimed_band():
    # red: `N_PER_BLOCK, E_PER_BLOCK = 23, 8` -> `24, 8` in split_1e.py -> `split.json differs from split_1e.py`
    r = subprocess.run([sys.executable, "-B", str(HERE / "split_1e.py"), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    sp = json.loads((HERE / "split.json").read_text())
    b = json.loads((PHASE1B / "split.json").read_text())
    names = list(sp["sets"])
    assert names[:8] == list(b["sets"]) and sp["split_seed"] == b["split_seed"]
    for n in b["sets"]:
        assert sp["sets"][n]["train"] == b["sets"][n]["train"] and sp["sets"][n]["eval"] == b["sets"][n]["eval"], n
    _sub(f"""
import sys, json
sys.path.insert(0, {str(HERE)!r})
import data_1e as E
m = json.load(open({str(PHASE1B / 'results-raw/heads/NF-h24-s1/run-manifest.json')!r}))["roles"]
r = E.roles()
assert all(r[n] == m[n] for n in m), "the 1b validation carve moved"
new = {{n: r[n] for n in r if n not in m}}
assert set(new) == {{f"TN{{k}}" for k in range(1, 6)}} | {{f"TE{{k}}" for k in range(1, 6)}}, sorted(new)
assert all(len(v["eval"]) == 0 for v in new.values())
assert all(len(new[f"TN{{k}}"]["train"]) + len(new[f"TN{{k}}"]["val"]) == 23 and len(new[f"TN{{k}}"]["val"]) == 5 for k in range(1, 6))
assert all(len(new[f"TE{{k}}"]["train"]) + len(new[f"TE{{k}}"]["val"]) == 8 and len(new[f"TE{{k}}"]["val"]) == 2 for k in range(1, 6))
print("e2 roles ok")
""")
    needy = json.loads((NEEDY / "split.json").read_text())
    claimed = set()
    for arm in needy["arms"].values():
        claimed |= set(arm["seeds"])
    for lo, hi in list(needy["scout_bands"].values()) + [needy["held"]]:
        claimed |= set(range(lo, hi + 1))
    lo, hi = sp["band"]
    used = set()
    for n in names[8:]:
        s = sp["sets"][n]
        assert all(lo <= x <= hi for x in s["train"]) and s["eval"] == [] and s["train"] == sorted(s["train"]), n
        assert s["stripe"][0] <= s["train"][0] and s["train"][-1] <= s["stripe"][1], n
        assert not (set(s["train"]) & used), n
        used |= set(s["train"])
    assert not (used & claimed), "a Phase 1e training seed lies in a needy-set band"
    assert lo > max(claimed), (lo, max(claimed))
    assert len(used) == 5 * 23 + 5 * 8


def test_e3_the_selection_rule_on_a_hand_grid():
    # red: `r["fa_cov"] <= bound["fa_cov"]` -> `<` in read_1e.select_from -> the on-bound best cell drops out
    # and t0.20-B0 is chosen instead of t0.05-B2 (the two 0.55 cells tie; the rule's own tie-break goes to
    # the higher threshold — the first prediction said t0.10-B0 and was red for the wrong reason, exit 7)
    bound = {"fa_cov": 0.70, "fa_scr": 1.50}
    rows = {"t0.05-B2": {"th": 0.05, "b": 2, "det_N": 0.60, "fa_cov": 0.70, "fa_scr": 1.50},   # on the bound: a candidate
            "t0.10-B0": {"th": 0.10, "b": 0, "det_N": 0.55, "fa_cov": 0.10, "fa_scr": 0.20},
            "t0.20-B0": {"th": 0.20, "b": 0, "det_N": 0.55, "fa_cov": 0.10, "fa_scr": 0.20},   # ties t0.10-B0: higher threshold wins
            "t0.02-B0": {"th": 0.02, "b": 0, "det_N": 0.90, "fa_cov": 0.71, "fa_scr": 0.20},   # over the covered bound
            "t0.02-B2": {"th": 0.02, "b": 2, "det_N": 0.90, "fa_cov": 0.10, "fa_scr": 1.51},   # over the scripted bound
            "t0.50-B2": {"th": 0.50, "b": 2, "det_N": None, "fa_cov": 0.0, "fa_scr": 0.0}}     # no stratum populated
    sel = RE.select_from(rows, bound)
    assert sel["chosen"] == "t0.05-B2", sel
    assert sel["candidates"] == ["t0.05-B2", "t0.10-B0", "t0.20-B0"], sel
    rows2 = {c: r for c, r in rows.items() if c != "t0.05-B2"}
    assert RE.select_from(rows2, bound)["chosen"] == "t0.20-B0"
    rows2["t0.20-B2"] = {"th": 0.20, "b": 2, "det_N": 0.55, "fa_cov": 0.10, "fa_scr": 0.20}      # ties t0.20-B0: smaller B wins
    assert RE.select_from(rows2, bound)["chosen"] == "t0.20-B0"
    assert RE.select_from({"t0.02-B0": rows["t0.02-B0"]}, bound)["chosen"] is None
    for c in RE.CELLS + RE.EXT_CELLS:
        assert RE.cell_name(*RE.parse_cell(c)) == c
    assert len(RE.CELLS) == 12 and len(RE.EXT_CELLS) == 12 and RE.PICK in RE.CELLS and RE.REG in RE.CELLS
    assert not (set(RE.CELLS) & set(RE.EXT_CELLS)) and min(RE.EXT_THRESHOLDS) > max(RE.THRESHOLDS)
    b = RE.bound_from_ladder()
    assert round(b["fa_cov"], 4) == 0.7077 and round(b["fa_scr"], 4) == 1.4965, b
    # the alarms: the first B ticks forced off, NaN under every threshold
    P = np.full((10, 5, 5), 0.5, np.float32)
    P[:, 0, 0] = np.nan
    al = RE.level_alarms(P, ["t0.10-B2", "t0.50-B0"])
    a, b2 = al["t0.10-B2"]
    assert b2 == 2 and not a[:2].any() and a[2:, 0, 1].all() and not a[:, 0, 0].any()
    assert al["t0.50-B0"][0][:, 0, 1].all()


def test_e4_the_needy_reader_reproduces_the_ladder_and_step_7():
    # red: `R.refuse_unless(arm, k, seed, half)` removed from read_1e.world_record -> the ladder and step 7
    # compares still pass (the same worlds) and the last assertion, "a confirming seed passed as tuning", fails
    # (rise.cells_from_alarms carries its own red, r1 of the probe-rise read)
    _torch1()
    rise, R, L = RE._needy_modules()
    probe = {1: R.load_probe(1)[:2]}
    cells = [RE.PICK, RE.REG]
    for arm in ("E", "N"):
        arm_, k, seed, ticks, path = [w for w in rise.worlds("tuning") if w[0] == arm][0]
        mine = RE.world_record(rise, R, L, arm_, k, seed, ticks, path, "tuning", probe, cells)
        theirs = L.world_record(arm_, k, seed, ticks, path, probe)
        assert mine["crossing"] == theirs["crossing"] and mine["onset"] == theirs["onset"] and mine["stratum"] == theirs["stratum"]
        assert mine["sight_at_crossing"] == theirs["sight_at_crossing"] and mine["observer_ticks"] == theirs["observer_ticks"]
        for c in cells:
            for key in KEYS:
                assert mine["cells"]["1"][c][key] == theirs["cells"]["1"][c][key], (arm, c, key, mine["cells"]["1"][c][key], theirs["cells"]["1"][c][key])
    s7 = json.loads((NEEDY / "reads" / "step7.json").read_text())
    rec = [r for r in s7["records"] if r["half"] == "confirming" and r["arm"] == "N"][0]
    arm_, k, seed, ticks, path = [w for w in rise.worlds("confirming") if (w[0], w[1], w[2]) == ("N", rec["block"], rec["seed"])][0]
    mine = RE.world_record(rise, R, L, arm_, k, seed, ticks, path, "confirming", probe, [RE.PICK])
    for key in KEYS:
        assert mine["cells"]["1"][RE.PICK][key] == rec["cells"]["1"]["t0.05-B2"][key], ("confirming", key)
    try:
        RE.world_record(rise, R, L, arm_, k, seed, ticks, path, "tuning", probe, [RE.PICK])
        raise AssertionError("a confirming seed passed as tuning")
    except PermissionError:
        pass


def test_e5_the_splice_reader_reproduces_the_committed_H100_rows():
    # red: `r[f"{t:.2f}"]["all"]["detected_frac"]` -> `["onset_visible"]["detected_frac"]` in read_1e.splice_one
    # -> seed 1's detected fraction at H = 100 (the 14 in-sight donors' rate) differs from the committed 200-donor row
    _torch1()
    HR = RE._hist_modules()
    hist = json.loads((PHASE1D / "phase1d-history.json").read_text())["splice"]["NF-h24+p"]["100"]["per_seed"]
    idx_p = HR.P.R.eval_index(HR.C.GROUPS["P"])
    idx_l = HR.P.R.eval_index([HR.L_SET])
    donors, recips = HR.donor_list(idx_p), HR.recipient_list(idx_l)
    RE.HISTORIES = (100,)
    try:
        for i, s in enumerate(RE.SEEDS):
            model, probe = HR.load_probe(s)
            rows = RE.splice_one(HR, model, probe, donors, recips, (0.10,))
            got, want = rows["100"]["0.10"], hist[i]["0.10"]
            assert got["detected"] == want["all"]["detected_frac"], (s, got["detected"], want["all"]["detected_frac"])
            assert got["control_fired"] == want["control_fired"], (s, got["control_fired"], want["control_fired"])
    finally:
        RE.HISTORIES = (0, 1, 2, 5, 10, 20, 50, 100, 500, 2000)
    cm = RE.committed_splice()
    assert sorted(int(h) for h in cm) == list(RE.HISTORIES), sorted(cm)
    assert round(cm["100"]["detected"], 3) == 0.358 and round(cm["0"]["detected"], 3) == 0.995 and round(cm["20"]["detected"], 3) == 0.537, cm


def test_e6_the_estimate_reader_reproduces_1bs_headline_cell():
    # red: `m &= idx["vis"]` is 1b's; here `out[a:b] = cache[(n, s)][:, k, j]` -> `[:, j, k]` in read_1e.load_pred_dir
    # -> the per-seed grave mse5 from the pred dir differs from read_phase1.load_pred's
    RP = RE._phase1_reader()
    ref = json.loads((PHASE1B / "phase1b-read.json").read_text())["reads"]["24"]["P"]["heads"]["NF"]["mse5"]["visible"]["GRAVE"]["pooled"]
    idx = RP.eval_index(RE.GROUP_P)
    per = []
    for s in RE.SEEDS:
        theirs = RE.estimate_cells(RP, RP.load_pred(f"NF-h24-s{s}", idx), idx)
        mine = RE.estimate_cells(RP, RE.load_pred_dir(PHASE1B / "results-raw" / "heads" / f"NF-h24-s{s}", idx), idx)
        assert mine == theirs, s
        per.append(theirs["visible"]["GRAVE"]["mse5"])
    assert abs(float(np.mean(per)) - ref["mean"]) < 1e-6, (np.mean(per), ref["mean"])
    assert round(float(np.mean(per)), 2) == 908.10


def test_e7_the_lived_reader_reproduces_the_sweep_and_burns_exactly_B():
    # red: `s[a:a + b] = 0.0` -> `s[a:a + b + 1] = 0.0` in read_1e.burn -> the B = 2 check (tick 2 kept) fails
    _torch1()
    HR = RE._hist_modules()
    P = HR.P
    idx = P.R.eval_index(HR.C.GROUPS["P"])
    eps = P.episodes(idx)
    sig = P.load_p("NF-h24-s1+p", idx)
    rows = RE.lived_rows(P, idx, eps, sig, ["t0.10-B0"])["t0.10-B0"]
    # the sweep's committed per-seed row for NF-h24-s1+p on group P at 0.10 (R4d's latency, the same function)
    sweep = json.loads((PHASE1D / "phase1d-sweep.json").read_text())["by_set"]["P"]["heads"]["NF-h24+p"]["rows"]["0.10"]["per_seed"][0]
    assert rows["reset_detected"] == sweep["reset"]["detected_frac"], (rows["reset_detected"], sweep["reset"]["detected_frac"])
    assert rows["fa_per_10k"] == sweep["false_alarms"]["per_10k_ticks"], (rows["fa_per_10k"], sweep["false_alarms"]["per_10k_ticks"])
    assert rows["reset_episodes"] == 200, rows["reset_episodes"]
    b = RE.burn(sig, idx, 2)
    for _n, _s, _k, _j, a, bb in idx["slices"][:5]:
        assert b[a] == 0.0 and b[a + 1] == 0.0 and b[a + 2] == sig[a + 2] and b[bb - 1] == sig[bb - 1]
    assert np.array_equal(RE.burn(sig, idx, 0), sig)


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
