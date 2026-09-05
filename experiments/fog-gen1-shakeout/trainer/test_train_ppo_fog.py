"""Guard for train_ppo_fog's pure parts (plain asserts, no pytest).

    experiments/exp-006-character-gen/.venv/bin/python \\
        experiments/fog-gen1-shakeout/trainer/test_train_ppo_fog.py

The Part C plateau predicate, the per-arm config derivation (anchor.toml
with only `[vision] radius` moved), the no-fog radius, and the slot
table's seed claim. The PPO loop itself is the exp-006 recipe carried
verbatim and is exercised by the --smoke run, not here.
"""
import sys
import tempfile
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import train_ppo_fog as tf  # noqa: E402


def test_plateau_flat_needs_both_return_and_kl_flat():
    # red: drop the KL clause, or flip `<` on the return clause
    prev = {"ret": 1.000, "kl": 0.100}
    assert tf.plateau_flat(prev, {"ret": 1.004, "kl": 0.105})        # both flat
    assert not tf.plateau_flat(prev, {"ret": 1.006, "kl": 0.105})    # return moved
    assert not tf.plateau_flat(prev, {"ret": 1.004, "kl": 0.125})    # KL +25%, +0.025
    assert tf.plateau_flat(prev, {"ret": 1.004, "kl": 0.119})        # +19% but < 0.02 abs
    assert tf.plateau_flat(prev, {"ret": 0.900, "kl": 0.100})        # a drop is "flat"
    assert not tf.plateau_flat({"ret": None, "kl": 0.1}, {"ret": 1.0, "kl": 0.1})


def test_derive_config_moves_only_the_radius():
    # red: substitute a second `radius` line, or skip the equality check
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "config.toml"
        cfg = tf.derive_config(9, out)
        assert cfg["vision"]["radius"] == 9
        with tf.ANCHOR_TOML.open("rb") as f:
            base = tomllib.load(f)
        base["vision"]["radius"] = 9
        assert cfg == base
        text = out.read_text()
        assert text.count("radius = 9") == 1 and "radius = 5" not in text


def test_whole_world_radius_covers_the_far_corner():
    # red: use max(w, h) instead of the diagonal
    cfg = {"world": {"width": 20, "height": 20}}
    r = tf.whole_world_radius(cfg)
    assert r == 27 and r * r >= 19 * 19 + 19 * 19 and (r - 1) ** 2 < 19 * 19 * 2


def test_slots_claim_run_indices_12_to_17_once_each():
    # red: duplicate a run index in SLOTS
    idx = sorted(v[4] for v in tf.SLOTS.values())
    assert idx == list(range(12, 18)), idx
    assert all(v[1] in tf.PINS and v[2] in tf.PINS for v in tf.SLOTS.values())
    assert {v[0] for v in tf.SLOTS.values()} == {"pin", "pin+1", "whole"}


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
