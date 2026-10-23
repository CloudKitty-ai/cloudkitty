#!/usr/bin/env python3
"""Guards for Phase 1b's split, configs and reader (Phase 1 arc venv;
Phase 1's raws and head runs present — they stand in for Phase 1b's
until P exists, so every contrast here is an identity or a hand-built
case and the guards test the arithmetic, not the result).

s1  split.json: L, W, G equal Phase 1's split.json verbatim; each P block
    is 20 contiguous seeds from 1095451, 10 eval / 10 train, blocks and
    the reserved X blocks pairwise disjoint; the file equals split.py
s2  configs: each g2leg-20-P<k>.toml parses to the served config plus
    kitty k's initial_needs, every need {min 60, max 95}, and no other
    kitty carries one; the files equal make_configs.py
b1  size ratio: identical cells → ratio 1 (not READ); a cell scaled by
    1.2 → ratio 1.2 with the first-order SD by hand, READ iff |r−1| > SD
b2  the eval-set filter: the Phase 1 reader on ["G"] alone reads the G
    eval worlds only and its mind-visible GRAVE coverage per friend
    equals strata-counts.json's recorded G totals
b3  group contrast: G over W GRAVE loss equals the two reads' pooled
    cells divided by hand, per head and version
"""
import copy
import json
import math
import os
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHASE1 = HERE.parent / "minifriend-phase1-2026-10-22"
os.environ["MINIFRIEND_ARC"] = str(PHASE1)        # Phase 1's raws and runs stand in
sys.path.insert(0, str(HERE))
import split as SP  # noqa: E402  — THIS arc's split.py, imported before read_phase1b puts Phase 1's dir first
import make_configs as MC  # noqa: E402
assert Path(SP.__file__).parent == HERE, SP.__file__
import read_phase1b as B  # noqa: E402
import read_phase1 as R  # noqa: E402

P1_RUNS = [(h, f"{h}-s{s}") for h in ("NF", "DR") for s in (1, 2, 3)]
_cache = {}


def _read(sets):
    key = tuple(sets)
    if key not in _cache:
        _cache[key] = R.read(P1_RUNS, sets)
    return _cache[key]


def test_s1_split_blocks():
    cur = json.loads((HERE / "split.json").read_text())
    p1 = json.loads((PHASE1 / "split.json").read_text())
    assert cur == SP.split(), "split.json differs from split.py"
    for n in ("L", "W", "G"):
        assert cur["sets"][n] == p1["sets"][n], n
    blocks = []
    for k in range(1, 6):
        s = cur["sets"][f"P{k}"]
        assert s["seeds"] == list(range(1095451 + 20 * (k - 1), 1095451 + 20 * k)), k
        assert len(s["eval"]) == 10 and len(s["train"]) == 10, (k, len(s["eval"]), "10 eval expected")
        assert sorted(s["eval"] + s["train"]) == s["seeds"]
        assert cur["grave_kitty"][f"P{k}"] == {"id": k, "name": SP.SEATS[k - 1]}
        x = cur["extension"][f"X{k}"]
        assert x["seeds"] == list(range(1095551 + 20 * (k - 1), 1095551 + 20 * k)) and len(x["eval"]) == 10
        blocks += [set(s["seeds"]), set(x["seeds"])]
    assert all(not (a & b) for i, a in enumerate(blocks) for b in blocks[i + 1:])


def test_s2_configs_one_grave_kitty_each():
    served = tomllib.loads(MC.SERVED.read_text())
    for k in range(1, 6):
        text = (HERE / f"g2leg-20-P{k}.toml").read_text()
        assert text == MC.render(k), f"g2leg-20-P{k}.toml differs from make_configs.py"
        cfg = tomllib.loads(text)
        assert "initial_needs" not in cfg
        for i, kit in enumerate(cfg["kitty"], start=1):
            base = dict(served["kitty"][i - 1])
            if i == k:
                assert kit.pop("initial_needs") == {n: {"min": 60, "max": 95} for n in MC.NEEDS}, (k, kit.get("initial_needs"))
            else:
                assert "initial_needs" not in kit, (k, i)
            assert kit == base, (k, i)
        rest = {s: v for s, v in cfg.items() if s != "kitty"}
        assert rest == {s: v for s, v in served.items() if s != "kitty"}


def test_b1_size_ratio_arithmetic():
    a = {"mean": 100.0, "sd": 10.0, "seeds": 3}
    same = B.ratio(a, a)
    assert same["ratio"] == 1.0 and same["read"] is False
    b = {"mean": 120.0, "sd": 6.0, "seeds": 3}
    r = B.ratio(b, a)
    sd = 1.2 * math.sqrt((6 / 120) ** 2 + (10 / 100) ** 2)
    assert abs(r["ratio"] - 1.2) < 1e-12 and abs(r["sd"] - sd) < 1e-12, r
    assert r["read"] is (abs(1.2 - 1.0) > sd)
    assert B.ratio({"mean": 130.0, "sd": 1.0, "seeds": 3}, a)["read"] is True       # |0.3| > sd
    assert B.ratio({"mean": 101.0, "sd": 1.0, "seeds": 3}, a)["read"] is False      # |0.01| < sd
    assert B.ratio(None, a) is None and B.ratio({"mean": 5.0, "sd": None, "seeds": 1}, a)["sd"] >= 0
    # through size_effect: the same read under two widths → every ratio 1
    g = _read(["G"])
    se = B.size_effect({24: {"G": g}, 12: {"G": copy.deepcopy(g)}}, "G")
    for head in B.HEADS:
        for cls in B.CLASSES:
            rr = se[head]["visible"][cls]["ratio_to_ref"][12]
            assert rr is None or (rr["ratio"] == 1.0 and rr["read"] is False), (head, cls, rr)


def test_b2_eval_set_filter_reads_only_that_set():
    g = _read(["G"])
    split = json.loads((PHASE1 / "split.json").read_text())
    assert g["eval_sets"] == ["G"] and [s for _, s in g["eval_worlds"]] == sorted(split["sets"]["G"]["eval"]), g["eval_worlds"]
    counts = json.loads((PHASE1 / "strata-counts.json").read_text())["sets"]["G"]["total"]
    for f, n in g["coverage"]["visible"]["GRAVE"].items():
        assert n == counts[f]["GRAVE"]["visible"], (f, n, counts[f]["GRAVE"]["visible"])
    assert sum(g["coverage"]["all"]["COMMON"].values()) < sum(_read(["G", "W"])["coverage"]["all"]["COMMON"].values())


def test_b3_group_contrast_by_hand():
    g, w = _read(["G"]), _read(["W"])
    c = B.group_contrast({24: {"G": g, "P": w}})[24]
    for head in B.HEADS:
        for v in R.VERSIONS:
            num, den = g["heads"][head]["mse5"][v]["GRAVE"]["pooled"], w["heads"][head]["mse5"][v]["GRAVE"]["pooled"]
            if num is None or den is None:
                assert c[head][v] is None
                continue
            assert abs(c[head][v]["ratio"] - num["mean"] / den["mean"]) < 1e-12, ("contrast", head, v)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
