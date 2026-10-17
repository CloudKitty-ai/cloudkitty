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
GEN2 = REPO / "experiments/gen2-world-draft-2026-10-15.toml"


class DrawArgs:
    """prepare() args at the ruled dial-draw law (defaults mirror main's)."""
    base_config, ticks = GEN2, 20000
    seed_base, draw_seed = 910_001, 42
    edge_share, corner_share, trace = 0.25, 0.05, False
    enrich_share, trait_share = 0.12, 0.28
    base_consent, enrich_consent = 0.0, (20.0, 25.0)
    slack_range, mult_range, mult_k = (2.0, 5.0), (0.5, 2.0), 3


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
        # anchor.toml has no live consent_line; pure-served, untouched.
        enrich_share, trait_share, base_consent = 0.0, 0.0, None
        enrich_consent, slack_range = (20.0, 25.0), (2.0, 5.0)
        mult_range, mult_k = (0.5, 2.0), 3

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


def test_mix_counts_exact_and_seeded():
    A = type("A", (DrawArgs,), {"rollouts": 25})
    with tempfile.TemporaryDirectory() as td:
        A.out_dir = td
        m = cc.prepare(A)
        classes = [r["class"] for r in m["rollouts"]]
        # round(25*.12)=3 enrichment, round(25*.28)=7 traits, 15 served —
        # exact counts, never probabilistic.
        assert classes.count("enrichment") == 3, classes
        assert classes.count("traits") == 7
        assert classes.count("served") == 15
        assert m["mix"] == {"served": 15, "enrichment": 3, "traits": 7,
                            "shares": {"enrichment": 0.12, "traits": 0.28}}
    with tempfile.TemporaryDirectory() as td2:
        A.out_dir = td2
        assert [r["class"] for r in cc.prepare(A)["rollouts"]] == classes, \
            "class assignment must be deterministic in the draw seed"


def test_enrichment_consent_per_episode_and_base_zero():
    A = type("A", (DrawArgs,), {"rollouts": 25})
    with tempfile.TemporaryDirectory() as td:
        A.out_dir = td
        m = cc.prepare(A)
        for r in m["rollouts"]:
            parsed = tomllib.loads(Path(r["config"]).read_text())
            got = parsed["behavior"]["consent_line"]
            if r["class"] == "enrichment":
                assert 20.0 <= r["consent_line"] <= 25.0, r["consent_line"]
                assert got == r["consent_line"], (r["rollout"], got)
            else:
                assert r["consent_line"] == 0.0 and got == 0.0, (r["class"], got)


def test_trait_draws_follow_the_ruled_law():
    A = type("A", (DrawArgs,), {"rollouts": 25})
    base_needs = tomllib.loads(GEN2.read_text())["needs"]
    with tempfile.TemporaryDirectory() as td:
        A.out_dir = td
        m = cc.prepare(A)
        traits = [r for r in m["rollouts"] if r["class"] == "traits"]
        assert traits
        for r in traits:
            parsed = tomllib.loads(Path(r["config"]).read_text())
            for kitty, d in zip(parsed["kitty"], r["dials"]):
                assert 2.0 <= d["comfort_slack"] <= 5.0
                assert kitty["comfort_slack"] == d["comfort_slack"], kitty["name"]
                mults = d["need_multipliers"]
                assert len(mults) == 3, (kitty["name"], mults)
                assert set(kitty["needs"]) == set(mults), \
                    "undrawn kinds must be ABSENT (reference = multiplier 1.0)"
                for kind, mult in mults.items():
                    assert 0.5 <= mult <= 2.0, (kind, mult)
                    assert kitty["needs"][kind] == round(mult * base_needs[kind], 4)
        served = [r for r in m["rollouts"] if r["class"] == "served"]
        parsed = tomllib.loads(Path(served[0]["config"]).read_text())
        base = tomllib.loads(GEN2.read_text())
        for kb, kp in zip(base["kitty"], parsed["kitty"]):
            assert kb["needs"] == kp["needs"], "served roster must keep its trait sheets"
            assert "comfort_slack" not in kp, "served roster draws no slack"


def test_multiplier_draw_is_log_uniform():
    rng = np.random.default_rng(5)
    mults = [m for _ in range(700)
             for d in cc.draw_dials(rng, 1, 2, 5, 0.5, 2.0, 3)
             for m in d["need_multipliers"].values()]
    assert len(mults) == 2100
    assert all(0.5 <= m <= 2.0 for m in mults)
    med = float(np.median(mults))
    # log-uniform median is 1.0; a linear-uniform draw's is ~1.25.
    assert 0.93 <= med <= 1.08, med


def test_real_drawn_configs_load_in_the_engine():
    """One traits and one enrichment config through the real collector:
    the draw law must produce configs the validator accepts."""
    if not cc.BC.exists():
        raise AssertionError(f"{cc.BC} not built")
    A = type("A", (DrawArgs,), {"rollouts": 25})
    with tempfile.TemporaryDirectory() as td:
        A.out_dir = td
        m = cc.prepare(A)
        import subprocess
        for cls in ("traits", "enrichment"):
            r = next(x for x in m["rollouts"] if x["class"] == cls)
            p = subprocess.run([str(cc.BC), "--config", r["config"],
                                "--rollouts", "1", "--ticks", "10",
                                "--seed-base", "1",
                                "--out-dir", str(Path(td) / f"load-{cls}")],
                               capture_output=True, text=True)
            assert p.returncode == 0, (cls, p.stderr[-400:])


def test_real_tiny_collection_state_tick0_equals_sampled_starts():
    if not cc.BC.exists():
        raise AssertionError(f"{cc.BC} not built — build bc-collect first; "
                             "this guard needs the real collector")
    with tempfile.TemporaryDirectory() as td:
        cc.main(["--base-config", str(ANCHOR), "--out-dir", td,
                 "--rollouts", "1", "--ticks", "30", "--seed-base", "991101",
                 "--draw-seed", "99", "--jobs", "1",
                 "--enrich-share", "0", "--trait-share", "0",
                 "--base-consent", "-1"])
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
