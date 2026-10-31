#!/usr/bin/env python3
"""Guards for the needy set (DECLARATION.md §10; plain asserts, the arc
venv). Each is red on record before it is trusted (scripts/mutate.sh);
the reds are listed in RESULTS.md's Guards section as they land.

  n9  configs: each E file differs from its N file in exactly the three
      declared keys, each N file from the served config in exactly its
      three, and every file loads on the engine.
  split: split.json is split.py's output and the halves alternate.
  n1  the covered-only stop: the scripted friend's streak never stops a
      world; a covered seat at the line still does.
  n2  the needy schedule recorded per tick, held to the engine's own law
      on real payloads (all-scripted fixtures, 0 covered cat-ticks).
  n4  the reader pairs covered observers only; the scripted seat as an
      observer trips the recorded-observation assertion.
  n5  anchors, on the scripted scout's real payloads (results-raw/scout):
      every level release is grave on the obs-aligned truth inside its own
      window, every crossing attributed to a window lies inside it, arm
      E's first onset is tick 0 or 1 and no arm E world is grave at tick 0.
      The anticipation clause (no alarm run outside a window) needs
      covered observers and lands with the covered scout (step 4).
  n6  R4/R5's gate refuses a seed from the other half.
  n8  the frozen probe reproduces the committed pgrave file in this venv.

    test_needy_set.py            # every guard
    test_needy_set.py n1 n2      # the guards whose name carries a tag
"""
import json
import subprocess
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402

import make_configs as M  # noqa: E402
import split as SP  # noqa: E402

sys.path.insert(0, str(HERE.parent / "seating-analysis-g2-2026-10-21"))
import seating_collect_g2 as C  # noqa: E402
import needy_read as R  # noqa: E402

E1 = HERE / "g2leg-20-E1-n60.toml"
_fix = {}


def _fixture(name, **tables):
    """E1 at n = 60 (mask open at tick 0 or 1, needs at 60) with [needy] lines
    replaced, written under a temp dir (never tracked: the shipped-config
    sweep loads every tracked experiments toml)."""
    import tempfile
    if name not in _fix:
        text = E1.read_text()
        for key, val in tables.items():
            line = next(l for l in text.splitlines() if l.startswith(f"{key} = "))
            text = text.replace(line, f"{key} = {val}")
        d = Path(tempfile.mkdtemp())
        (d / f"{name}.toml").write_text(text)
        _fix[name] = d / f"{name}.toml"
    return _fix[name]

SERVED = tomllib.load(M.SERVED.open("rb"))


def _diff(a, b, path=""):
    """Leaf paths at which two parsed tomls differ."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                out.append(f"{path}.{key}")
            else:
                out += _diff(a[key], b[key], f"{path}.{key}")
        return out
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b) \
            and any(isinstance(x, (dict, list)) for x in a):
        return sum((_diff(x, y, f"{path}[{i}]") for i, (x, y) in enumerate(zip(a, b))), [])
    return [] if a == b else [path]


def test_n9_configs_differ_from_their_bases_in_the_declared_keys_only():
    # red: one config's n moved by one (sed on the committed E file) ->
    # its initial_needs no longer equal the n in its name (the --check at
    # the end would catch it too; the value assertions run first so the
    # red names the moved number)
    for k in range(1, 6):
        n_cfg = tomllib.load((HERE / f"g2leg-20-N{k}.toml").open("rb"))
        assert sorted(_diff(SERVED, n_cfg)) == sorted([f".kitty[{k - 1}].behavior", ".needy", ".welfare_hazard"]), _diff(SERVED, n_cfg)
        assert n_cfg["kitty"][k - 1]["behavior"] == "needy"
        assert n_cfg["needy"] == {"mix": [0.5, 0.2, 0.15, 0.15, 0.0, 0.0], "release_level": 90.0, "hold_ticks": 1500,
                                  "gap": {"min": 300, "max": 1200}, "onset_levels": [0, 2, 10, 50, 200, 4500],
                                  "onset_weights": [0.1, 0.1, 0.1, 0.1, 0.6], "onset_draw": "log_uniform"}, n_cfg["needy"]
        assert n_cfg["welfare_hazard"] == {"acknowledged": ["needy"]}
        for n in M.N_VALUES:
            e_cfg = tomllib.load((HERE / f"g2leg-20-E{k}-n{n}.toml").open("rb"))
            got = sorted(_diff(n_cfg, e_cfg))
            assert got == sorted([f".kitty[{k - 1}].initial_needs", ".needy.onset_weights", ".welfare_hazard.acknowledged"]), got
            assert e_cfg["kitty"][k - 1]["initial_needs"] == {need: n for need in M.HIDDEN}, (k, n, e_cfg["kitty"][k - 1]["initial_needs"])
            assert e_cfg["needy"]["onset_weights"] == [1.0, 0.0, 0.0, 0.0, 0.0]
            assert e_cfg["welfare_hazard"]["acknowledged"] == ["initial_needs", "needy"]
    subprocess.run([sys.executable, "-B", str(HERE / "make_configs.py"), "--check"], check=True, capture_output=True)


def test_n9_every_config_loads_on_the_engine_with_its_needy_seat():
    import cloudkitty
    for name, _text in M.files():
        env = cloudkitty.ParallelEnv(str(HERE / name), horizon=3)
        env.reset(seed=1)
        k = int(name.split("-")[2][1])
        assert len(env.possible_agents) == 4 and f"kitty_{k}" not in env.possible_agents, (name, env.possible_agents)
        assert env.needy() == [(k, [], 0, "resting")], (name, env.needy())


def test_split_is_the_script_output_and_alternates_within_every_block():
    # red (n6's partner): one seed's half flipped in split.json
    cur = json.loads((HERE / "split.json").read_text())
    assert cur == SP.split()
    for name, s in cur["arms"].items():
        seeds = s["seeds"]
        assert seeds == sorted(seeds) and len(seeds) == (10 if name[0] == "T" else 60), name
        assert s["tuning"] == seeds[0::2] and s["confirming"] == seeds[1::2], name
        assert not set(s["tuning"]) & set(s["confirming"])
    n_all = [x for k in range(1, 6) for x in cur["arms"][f"N{k}"]["seeds"]]
    e_all = [x for k in range(1, 6) for x in cur["arms"][f"E{k}"]["seeds"]]
    assert n_all == list(range(1095711, 1096011)) and e_all == list(range(1096161, 1096461))
    bands = [tuple(cur["scout_bands"]["N"]), tuple(cur["scout_bands"]["covered"]), (1095711, 1096010),
             tuple(cur["scout_bands"]["E"]), (1096161, 1096460), tuple(cur["held"])]
    assert bands == sorted(bands) and all(a[1] < b[0] for a, b in zip(bands, bands[1:])), bands
    assert bands[0][0] == 1095651 and bands[-1][1] == 1096650


def test_n1_abort_seats_watch_the_named_seats_only():
    # red: abort_due ignores abort_seats (reads the roster max) -> the
    # covered-only case stops on the scripted seat's 150
    streak = np.zeros((5, 6), np.int64)
    streak[0, 4] = 150   # the scripted friend (seat 0), the long run
    streak[2, 0] = 50    # a covered seat, under the line
    assert C.abort_due(streak, 100) is True
    assert C.abort_due(streak, 100, abort_seats=[1, 2, 3, 4]) is False
    assert C.abort_due(streak, 100, abort_seats=[]) is False
    assert C.abort_due(streak, None, abort_seats=[0]) is False
    streak[2, 0] = 100   # a covered seat AT the line still aborts (must pass)
    assert C.abort_due(streak, 100, abort_seats=[1, 2, 3, 4]) is True


def test_n1_the_scripted_friends_streak_never_stops_a_covered_only_world():
    # red: the option mutated to count every seat -> this all-scripted
    # needy world (0 covered cat-ticks) aborts on the friend's own streak.
    # Fixture: every need masked at once (mix on m = 6) from tick 0 or 1
    # at n = 60, so Miso's sleep (0.6/tick) sits at 90 from tick ~50 while
    # bath climbs; the line is lowered to 30 ticks.
    cfg = _fixture("n1-allmasked", mix="[0.0, 0.0, 0.0, 0.0, 0.0, 1.0]")
    arrays, meta = C.collect("scripted", 905001, 150, 30, config=cfg, abort_covered_only=True)
    assert meta["abort_seats"] == [] and meta["needy_seat"] == 0
    assert meta["aborted_at"] is None and meta["ticks"] == 150, (meta["aborted_at"], meta["ticks"])
    streak = np.zeros((5, 6), np.int64)
    flags = np.unpackbits(arrays["distress"][:, :, None], axis=2, bitorder="little")[:, :, :6]
    longest = 0
    for t in range(150):
        streak = np.where(flags[t] > 0, streak + 1, 0)
        longest = max(longest, int(streak[0].max()))
    assert longest >= 30, longest   # the fixture did put the friend over the line
    assert (arrays["needy_phase"] == C.NEEDY_PHASES.index("held")).sum() > 100


def _n2_world():
    if "n2" not in _fix:
        cfg = _fixture("n2-short", hold_ticks="120", gap="{ min = 5, max = 10 }")
        _fix["n2"] = C.collect("scripted", 905001, 600, None, config=cfg)
    return _fix["n2"]


def test_n2_needy_schedule_is_recorded_on_the_engines_own_law():
    # red: the schedule read one tick off (before the step instead of
    # after) -> on a level-release tick the masked need is still under 90
    arrays, meta = _n2_world()
    seat = meta["needy_seat"]
    mask, ordinal, phase = arrays["needy_mask"], arrays["needy_ordinal"], arrays["needy_phase"]
    needs = arrays["needs"][:, seat]
    held, lvl, lim = (C.NEEDY_PHASES.index(x) for x in ("held", "released_level", "released_limit"))
    bits = np.array([(mask >> i) & 1 for i in range(6)], bool).T          # (T, 6)
    releases = np.where((phase == lvl) | (phase == lim))[0]
    assert (phase == lvl).any() and len(releases) >= 2, (np.bincount(phase, minlength=4).tolist())
    # (b) a level release is the FIRST tick every masked need sits at 90 or
    # over: not all of them were there the tick before, all of them are now
    for t in np.where(phase == lvl)[0]:
        assert phase[t - 1] == held and mask[t] == 0 and bits[t - 1].any(), t
        assert not (needs[t - 1][bits[t - 1]] >= 90.0).all(), ("release one tick late", t, needs[t - 1][bits[t - 1]])
        assert (needs[t][bits[t - 1]] >= 90.0 - 1e-4).all(), (t, needs[t][bits[t - 1]])
    # (a) while held, a masked need never falls
    for t in range(1, len(phase)):
        if phase[t] == held and phase[t - 1] == held and ordinal[t] == ordinal[t - 1]:
            assert mask[t] == mask[t - 1]
            assert (needs[t][bits[t]] >= needs[t - 1][bits[t]] - 1e-4).all(), (t, needs[t - 1][bits[t]], needs[t][bits[t]])
    # (c) every onset after the first is the previous release plus a gap inside {5, 10}
    onsets = np.where((phase == held) & (np.concatenate([[0], ordinal[:-1]]) != ordinal))[0]
    assert len(onsets) == ordinal.max() >= 3 and onsets[0] <= 1, (onsets[:3], ordinal.max())
    for o in onsets[1:]:
        r = releases[releases < o].max()
        assert 5 <= o - r <= 10, (o, r)
    # the limit release: hold_ticks after its onset
    for t in np.where(phase == lim)[0]:
        o = onsets[onsets <= t].max()
        assert t - o == 120, (t, o)


def test_n2_needy_streams_are_absent_without_a_needy_seat():
    arrays, meta = C.collect("scripted", 905001, 5, None)
    assert meta["needy_seat"] is None and "needy_mask" not in arrays


def _mixed_world():
    """rot2 with Miso scripted on N1 (the set's own shape), 20 ticks, obs
    saved: 80 covered cat-ticks, the certified networks in a world they
    have run."""
    if "mixed" not in _fix:
        _fix["mixed"] = C.collect("g2-rot2", 905001, 20, 1000, config=HERE / "g2leg-20-N1.toml",
                                  save_obs=True, scripted_seat=0, abort_covered_only=True)
        import tempfile
        out = Path(tempfile.mkdtemp()) / "streams-905001.npz"
        arrays, meta = _fix["mixed"]
        np.savez_compressed(out, meta=json.dumps(meta), **arrays)
        _fix["mixed_path"] = out
    return _fix["mixed_path"]


def test_n4_reader_pairs_covered_observers_only():
    # red: the scripted seat admitted as an observer -> pair_x's
    # recorded-observation assertion trips on its first pair
    w = R.load_world(_mixed_world())
    assert w["scripted"] == [0] and w["meta"]["abort_seats"] == [1, 2, 3, 4] and w["needy_seat"] == 0
    pairs = R.observer_pairs(w)
    for k, j in pairs:
        x, vis = R.pair_x(w, k, j)
        assert x.shape == (20, 167) and x.dtype == np.float16
    assert len(pairs) == 16 and all(k != 0 for k, _j in pairs) and sum(j == 0 for _k, j in pairs) == 4, pairs
    try:
        R.pair_x(w, 0, 1)
    except AssertionError as e:
        assert "never an observer" in str(e)
    else:
        raise AssertionError("pair_x accepted the scripted seat as an observer")
    model, probe, _m = R.load_probe(1)
    p = R.probe_world(model, probe, w)
    assert p.shape == (20, 5, 5) and np.isnan(p[:, 0, :]).all() and np.isfinite(p[:, 1:, 0]).all()
    assert np.isnan(p[:, np.arange(5), np.arange(5)]).all()


def _scout_worlds(arm):
    """Every scout world of the arm: arm N at both onset top edges (the
    two blocks at 20000 and the re-scout at 4500, §13 amendment 1), arm E's
    one generation."""
    import scout as SC
    edges = SC.EDGES if arm == "N" else (20000,)
    ws = [(g, s, e) for e in edges for g, _c, s, _t in SC.worlds(arm, e)]
    missing = [s for g, s, e in ws if not SC.paths(g, s, e)[0].exists()]
    assert not missing, f"scout {arm} not run: {len(missing)} worlds missing (scout.py run --arm {arm} --edge E)"
    assert len(ws) == (200 if arm == "N" else 150), len(ws)
    return [(g, SC.paths(g, s, e)[0]) for g, s, e in ws]


def test_n5_anchors_hold_on_the_scripted_scouts_payloads():
    # red: the mask window shifted by one tick (needy_read.mask_windows,
    # both ends - 1) -> the first window of the first arm N world: its
    # onset no longer equals the stream's first held step
    GRAVE = R.S.GRAVE
    held, lvl, lim = (R.PHASES.index(x) for x in ("held", "released_level", "released_limit"))
    hidden_bits = sum(1 << i for i in range(5))
    n_level = n_inside = 0
    for g, path in _scout_worlds("N") + _scout_worlds("E"):
        w = R.load_world(path)
        f, mask, phase, ordinal = w["needy_seat"], w["needy_mask"], w["needy_phase"], w["needy_ordinal"]
        codes = w["codes"][:, f]
        windows, episodes = R.mask_windows(w), R.grave_episodes(codes)
        # the stream's own anchors: the first held step of each ordinal, every release step
        onsets = np.where((phase == held) & (np.concatenate([[0], ordinal[:-1]]) != ordinal))[0]
        releases = np.where((phase == lvl) | (phase == lim))[0]
        assert len(windows) == len(onsets), (g, w["seed"], len(windows), len(onsets))
        for j, (on, close, o) in enumerate(windows):
            assert on == onsets[j] and mask[on] != 0 and (on == 0 or mask[on - 1] == 0), ("window onset", g, w["seed"], o, on, int(onsets[j]))
        for r in releases:
            # the release step is the last step of its own window: on <= r < close = r + 1
            j = R.window_of(int(r) + 1, windows)
            assert j is not None and windows[j][1] == r + 1, ("release outside its window", g, w["seed"], int(r), windows)
            on, close, o = windows[j]
            if phase[r] == lvl and mask[r - 1] & hidden_bits and close < w["ticks"]:
                # a level release of a hidden need is grave on the obs-aligned truth at the
                # window's close (obs[close] carries needs[r])
                n_level += 1
                assert codes[close] == GRAVE, ("level release not grave at the window's close", g, w["seed"], o, on, close)
                (c, e), = [(c, e) for (c, e) in episodes if c <= close < e]
                # the episode holding the release crossed inside the window, or before its onset (unmasked)
                assert R.window_of(c, windows) == j or c - 1 < on, (g, w["seed"], o, c, on, close)
                n_inside += R.window_of(c, windows) == j
        for c, e in episodes:
            j = R.window_of(c, windows)
            if j is not None:
                on, close, _o = windows[j]
                assert on <= c - 1 < close and codes[c - 1] != GRAVE, (g, w["seed"], c, on, close)
    assert n_level >= 50 and n_inside >= 50, (n_level, n_inside)
    for g, path in _scout_worlds("E"):
        w = R.load_world(path)
        f = w["needy_seat"]
        windows = R.mask_windows(w)
        assert windows and windows[0][2] == 1 and windows[0][0] in (0, 1), (g, w["seed"], windows[:1])
        assert w["codes"][0, f] != GRAVE, ("grave at tick 0", g, w["seed"])


def test_n6_the_gate_refuses_the_other_half():
    # red: refuse_unless lets the other half through -> no PermissionError
    assert R.seeds("N", 1, "tuning", w=20) == list(range(1095711, 1095731, 2))
    assert R.seeds("T", 3, "confirming") == [1095495, 1095497, 1095500, 1095506, 1095510]
    assert R.refuse_unless("N", 1, 1095711, "tuning") == 1095711
    for arm, k, seed, half in (("N", 1, 1095712, "tuning"), ("N", 1, 1095711, "confirming"),
                               ("E", 5, 1096402, "tuning"), ("T", 1, 1095452, "confirming")):
        try:
            R.refuse_unless(arm, k, seed, half)
        except PermissionError as e:
            assert str(seed) in str(e) and half in str(e)
        else:
            raise AssertionError(f"{arm}{k} {seed} passed as {half}: did not raise")
    try:
        R.half_of("N", 1, 1096161)
    except KeyError:
        pass
    else:
        raise AssertionError("a seed outside the block did not raise")


def test_n8_the_probe_reproduces_the_committed_file():
    # red: the reference pointed at another probe seed's file
    worst = R.check_probe_reproduces(seeds=(1,))
    assert worst == {1: 0.0}, worst


if __name__ == "__main__":
    n = 0
    tags = sys.argv[1:]
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and (not tags or any(t in name for t in tags)):
            fn()
            print(f"ok {name}")
            n += 1
    print(f"{n} passed")
