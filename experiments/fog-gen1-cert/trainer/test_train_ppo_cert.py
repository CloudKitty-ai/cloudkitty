#!/usr/bin/env python3
"""Guard for train_ppo_cert.py (plain asserts, no pytest).
    experiments/exp-006-character-gen/.venv/bin/python \\
        experiments/fog-gen1-cert/trainer/test_train_ppo_cert.py
The twenty-slot table's run-index claim and pairings, the empty mix,
the pin keys, and the override derivation (anchor-b3 with the radius
and exactly the declared dials moved; absent 054 dials inserted).
"""
import sys
import tempfile
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import train_ppo_cert as tc  # noqa: E402


def test_slots_claim_run_indices_21_to_40_once_each():
    idx = sorted(v[4] for v in tc.SLOTS.values())
    assert idx == list(range(21, 41)), idx
    assert len(tc.SLOTS) == 20
    assert all(v[0] == "pin" for v in tc.SLOTS.values())
    assert all(v[1] in tc.PINS and v[2] in tc.PINS for v in tc.SLOTS.values())
    # pairings: the twin shares cand-s1's seed; flat-sN pairs cand-sN
    assert tc.SLOTS["twin-off"][3] == tc.SLOTS["cand-s1"][3] == 1
    assert tc.SLOTS["twin-off"][2] == "init_lesson_off"
    for n in (1, 2, 3):
        assert tc.SLOTS[f"flat-s{n}"][3] == tc.SLOTS[f"cand-s{n}"][3] == n
    assert tc.SLOTS["dose-lo-s1"][1] == "beta_lo" and tc.SLOTS["dose-hi-s1"][1] == "beta_hi"
    assert tc.PINS["beta_lo"] == 0.02 and tc.PINS["beta_hi"] == 0.10 and tc.PINS["beta_low"] == 0.04
    assert tc.SLOTS["plain-s1"][2] == "init_plain"


def test_mix_is_empty():
    assert tc.MIX == {}


def test_overrides_move_only_the_declared_keys():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "config.toml"
        with tc.ANCHOR_TOML.open("rb") as f:
            base = tomllib.load(f)
        assert "groom_cuddle_floor" not in base["actions"]  # 054 dials are defaults
        assert base["actions"]["sleep_relief_sunbeam"] == 7.0
        # beam: an existing line is rewritten
        tc.CURRENT["slot"] = "beam15-s1"
        cfg = tc.derive_config_with_overrides(4, out)
        assert cfg["actions"]["sleep_relief_sunbeam"] == 15.0
        assert cfg["vision"]["radius"] == 4
        want = dict(base); want["vision"] = dict(base["vision"], radius=4)
        want["actions"] = dict(base["actions"], sleep_relief_sunbeam=15.0)
        assert cfg == want
        # flat: absent keys are inserted under [actions]
        tc.CURRENT["slot"] = "flat-s2"
        cfg = tc.derive_config_with_overrides(4, out)
        assert (cfg["actions"]["groom_cuddle_floor"], cfg["actions"]["groom_cuddle_slope"],
                cfg["actions"]["groom_cuddle_ceiling"]) == (0.5, 0.0, 0.5)
        assert cfg["actions"]["sleep_relief_sunbeam"] == 7.0
        # a pool arm: nothing but the radius
        tc.CURRENT["slot"] = "cand-s3"
        cfg = tc.derive_config_with_overrides(4, out)
        want = dict(base); want["vision"] = dict(base["vision"], radius=4)
        assert cfg == want
        tc.CURRENT["slot"] = None


def test_install_points_the_shakeout_trainer_here():
    tc.install()
    assert tc.tf.ANCHOR_TOML == tc.ANCHOR_TOML and tc.tf.SLOTS is tc.SLOTS
    assert tc.tf.MIX == {} and tc.tf.derive_config is tc.derive_config_with_overrides


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"ok  {t.__name__}")
    print(f"{len(tests)}/{len(tests)} green")
