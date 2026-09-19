"""Guard for train_ppo_beam.py (plain asserts). Run from the repo root:
    experiments/exp-006-character-gen/.venv/bin/python experiments/beam-world-screen-2026-09-19/trainer/test_train_ppo_beam.py"""
import hashlib
import sys
import tempfile
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import train_ppo_beam as tb  # noqa: E402

# four slots claim run indices 41-44 once each; pairs share seeds across the two worlds
idx = sorted(v[4] for v in tb.SLOTS.values())
assert idx == [41, 42, 43, 44], idx
assert tb.SLOTS["pkg-s1"][3] == tb.SLOTS["floor5-s1"][3] == 1 and tb.SLOTS["pkg-s2"][3] == tb.SLOTS["floor5-s2"][3] == 2
assert all(v[0] == "pin" and v[1] == "beta_low" and v[2] == "init_lesson" for v in tb.SLOTS.values())
assert set(tb.WORLD) == set(tb.SLOTS)
assert tb.MIX == {}
assert tb.PINS["beta_low"] == 0.04 and tb.PINS["radius"] == 4
assert Path(tb.PINS["critic"]).exists(), "the B3 critic is the declared reuse"

# the derived world equals the committed file byte for byte and moves only the package keys
with tb.ANCHOR_TOML.open("rb") as f:
    base = tomllib.load(f)
for slot, (levels, committed) in tb.WORLD.items():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "config.toml"
        tb.CURRENT["slot"] = slot
        cfg = tb.derive_config_beam(4, out)
        assert out.read_bytes() == committed.read_bytes(), slot
        sb = cfg["elements"]["sunbeam"]
        assert (cfg["actions"]["sleep_relief"], cfg["actions"]["sleep_relief_sunbeam"], sb["ttl"], sb["min"], sb["max"]) == (*levels, levels[3] + 1)
        assert cfg["vision"]["radius"] == 4
        moved_sections = {"elements"}
        if (levels[0], levels[1]) != (base["actions"]["sleep_relief"], base["actions"]["sleep_relief_sunbeam"]):
            moved_sections.add("actions")
        assert {k for k in cfg if cfg[k] != base[k]} == moved_sections, (slot, {k for k in cfg if cfg[k] != base[k]})
        meta = (Path(d) / "beam-world.json").read_text()
        assert hashlib.sha256(committed.read_bytes()).hexdigest() in meta
# the two worlds differ in the off-beam relief only
p = tomllib.load(open(tb.WORLD["pkg-s1"][1], "rb")); f5 = tomllib.load(open(tb.WORLD["floor5-s1"][1], "rb"))
assert p["actions"]["sleep_relief"] == 3.0 and f5["actions"]["sleep_relief"] == 5.0
p["actions"]["sleep_relief"] = 5.0
assert p == f5
# a wrong radius is refused
try:
    tb.CURRENT["slot"] = "pkg-s1"
    with tempfile.TemporaryDirectory() as d:
        tb.derive_config_beam(5, Path(d) / "c.toml")
    raise SystemExit("radius 5 was accepted")
except AssertionError:
    pass
print("test_train_ppo_beam ok")
