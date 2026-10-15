#!/usr/bin/env python3
"""Guard for collect_corpus.py (plain asserts, no pytest).

Geometry by hand literals; sampling pinned on a seeded RNG; patching
round-tripped on the real anchor.toml; and one real 30-tick collection
whose state.npy tick-0 positions must equal the manifest's sampled
starts (independent literals: global-state v2 stride 40, position at
block offset 7 — global_state.rs)."""
import json
import sys
import tempfile
import tomllib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import collect_corpus as cc  # noqa: E402

ANCHOR = REPO / "experiments/fog-gen1-shakeout/anchor.toml"


def test_category_hand_literals():
    w = h = 20
    assert cc.category(0, 0, w, h) == "corner"
    assert cc.category(19, 19, w, h) == "corner"
    assert cc.category(0, 19, w, h) == "corner"
    assert cc.category(19, 0, w, h) == "corner"
    assert cc.category(0, 7, w, h) == "edge"
    assert cc.category(5, 19, w, h) == "edge"
    assert cc.category(1, 1, w, h) == "interior"
    assert cc.category(10, 18, w, h) == "interior"


def test_sampling_is_unique_in_category_and_near_pencil_shares():
    rng = np.random.default_rng(7)
    counts = {"corner": 0, "edge": 0, "interior": 0}
    n = 0
    for _ in range(2000):
        starts, cats = cc.sample_starts(rng, 5, 20, 20, 0.25, 0.05)
        assert len(set(starts)) == 5
        for (x, y), cat in zip(starts, cats):
            assert 0 <= x < 20 and 0 <= y < 20
            assert cc.category(x, y, 20, 20) == cat, ((x, y), cat)
            counts[cat] += 1
            n += 1
    edge_ring = (counts["edge"] + counts["corner"]) / n
    corner = counts["corner"] / n
    assert abs(edge_ring - 0.25) < 0.02, edge_ring
    assert abs(corner - 0.05) < 0.01, corner


def test_patch_starts_moves_only_xy():
    base = ANCHOR.read_text()
    starts = [(0, 0), (19, 5), (10, 10), (1, 1), (5, 19)]
    patched = cc.patch_starts(base, starts)
    a, b = tomllib.loads(base), tomllib.loads(patched)
    for k, (x, y) in zip(b["kitty"], starts):
        assert (k["x"], k["y"]) == (x, y), (k["name"], k["x"], k["y"])
    for ka, kb in zip(a["kitty"], b["kitty"]):
        for key in ka:
            if key not in ("x", "y"):
                assert ka[key] == kb[key], (ka.get("name"), key)
    a.pop("kitty"), b.pop("kitty")
    assert a == b, "patching touched something outside [[kitty]] x/y"


def test_prepare_manifest_and_seed_rule():
    class A:
        base_config, rollouts, ticks = ANCHOR, 3, 20000
        seed_base, draw_seed = 910_001, 42
        edge_share, corner_share, trace = 0.25, 0.05, True

    with tempfile.TemporaryDirectory() as td:
        A.out_dir = td
        m = cc.prepare(A)
        assert [r["seed_base"] for r in m["rollouts"]] == [910_001, 911_001, 912_001]
        assert m["world"] == [20, 20] and m["roster"] == 5
        cats = [c for r in m["rollouts"] for c in r["categories"]]
        want_edge = sum(c in ("edge", "corner") for c in cats) / len(cats)
        assert m["realized_shares"]["edge_ring"] == want_edge
        for r in m["rollouts"]:
            p = Path(r["config"])
            assert p.exists()
            parsed = tomllib.loads(p.read_text())
            got = [(k["x"], k["y"]) for k in parsed["kitty"]]
            assert got == [tuple(s) for s in r["starts"]], r["rollout"]
        assert json.loads((Path(td) / "manifest.json").read_text())["draw_seed"] == 42


def test_real_tiny_collection_state_tick0_equals_sampled_starts():
    if not cc.BC.exists():
        raise AssertionError(f"{cc.BC} not built — build bc-collect first; "
                             "this guard needs the real collector")
    with tempfile.TemporaryDirectory() as td:
        cc.main(["--base-config", str(ANCHOR), "--out-dir", td,
                 "--rollouts", "1", "--ticks", "30", "--seed-base", "991101",
                 "--draw-seed", "99", "--jobs", "1"])
        m = json.loads((Path(td) / "manifest.json").read_text())
        rd = Path(td) / "r00" / "config-00-rollout-00"
        meta = json.loads((rd / "meta.json").read_text())
        assert meta["world_seed"] == 991_101 and meta["observation_schema"] == 6
        st = np.load(rd / "state.npy")
        # independent literals: v2 stride 40, position at offset 7 (x/w)
        assert st.shape[1] == 237, st.shape
        got = [(round(float(st[0, k * 40 + 7]) * 20), round(float(st[0, k * 40 + 8]) * 20))
               for k in range(5)]
        want = [tuple(s) for s in m["rollouts"][0]["starts"]]
        assert got == want, (got, want)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
