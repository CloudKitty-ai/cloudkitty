#!/usr/bin/env python3
"""Guards for the needy set (DECLARATION.md §10; plain asserts, the arc
venv). Each is red on record before it is trusted (scripts/mutate.sh);
the reds are listed in RESULTS.md's Guards section as they land.

  n9  configs: each E file differs from its N file in exactly the three
      declared keys, each N file from the served config in exactly its
      three, and every file loads on the engine.
  split: split.json is split.py's output and the halves alternate.
"""
import json
import subprocess
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_configs as M  # noqa: E402
import split as SP  # noqa: E402

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


if __name__ == "__main__":
    n = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
            n += 1
    print(f"{n} passed")
