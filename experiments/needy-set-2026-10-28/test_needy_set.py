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
                                  "gap": {"min": 300, "max": 1200}, "onset_levels": [0, 2, 10, 50, 200, 20000],
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
    # (b) a level release: every need masked on the tick before sits at 90 or over now
    for t in np.where(phase == lvl)[0]:
        assert phase[t - 1] == held and mask[t] == 0 and bits[t - 1].any(), t
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


if __name__ == "__main__":
    n = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
            n += 1
    print(f"{n} passed")
