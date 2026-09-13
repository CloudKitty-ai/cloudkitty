#!/usr/bin/env python3
"""Fog Gen 1 step-7 certification pass: the shakeout trainer
(`fog-gen1-shakeout/trainer/train_ppo_fog.py`) with this pass's
tables in place of the shakeout's. Nothing in the PPO loop, the stop
rules, the probe cadence or the manifest changes; what changes is
declared in `fog-gen1-cert/PREREG.md` §"The run table":

  - anchor = `fog-gen1-cert/anchor-b3.toml` (Biscuit 3.0 teacher);
  - SLOTS = the twenty arms, run indices 21-40 (bands [520M, 920M));
  - PINS gain `beta_lo` / `beta_hi` and the three B3 clone inits;
  - MIX is empty (all-policy, no exception);
  - per-slot dial OVERRIDES applied beside the radius line by a
    `derive_config` that re-reads the result and checks it against the
    anchor with exactly those keys moved (the shakeout's own check,
    extended). Absent keys (the 054 dials are defaults in the served
    file) are inserted under their section header.

    experiments/exp-006-character-gen/.venv/bin/python \\
        experiments/fog-gen1-cert/trainer/train_ppo_cert.py --slot cand-s1

Run from the repo root with the exp-006 venv. Guard: test_train_ppo_cert.py.
"""
import json
import re
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT = HERE.parent
sys.path.insert(0, str(CERT.parent / "fog-gen1-shakeout" / "trainer"))
import train_ppo_fog as tf  # noqa: E402

ANCHOR_TOML = CERT / "anchor-b3.toml"
CLONES = CERT / "results-raw" / "clones"
_derive_radius_only = tf.derive_config  # the shakeout's, captured before install()

# ---------------------------------------------------------------- owner pins
# None = not yet pinned; the launcher refuses the slot outside --smoke.
PINS = {
    "radius": 4,                    # shakeout pin, carried (#351)
    "beta_low": 0.04,               # F-019 low end, the pool's dose
    "beta_lo": 0.02,                # dose sweep, low  (owner 2026-09-13)
    "beta_hi": 0.10,                # dose sweep, high (owner 2026-09-13)
    "init_lesson": None,            # B3 lesson clone, bars pending
    "init_plain": None,             # B3 plain clone, bars pending
    "init_lesson_off": None,        # B3-off lesson clone (twin), bars pending
    "critic": None,                 # B3 critic
}

# slot -> (radius rule, beta pin, init pin, seed, run_index); the
# shakeout's tuple shape. Run indices 21-40 follow the shakeout's 12-20.
SLOTS = {}
_idx = 21
for _s in range(1, 8):
    SLOTS[f"cand-s{_s}"] = ("pin", "beta_low", "init_lesson", _s, _idx); _idx += 1
SLOTS["twin-off"] = ("pin", "beta_low", "init_lesson_off", 1, _idx); _idx += 1
for _s in range(1, 3):
    SLOTS[f"plain-s{_s}"] = ("pin", "beta_low", "init_plain", _s, _idx); _idx += 1
for _s in range(1, 4):
    SLOTS[f"flat-s{_s}"] = ("pin", "beta_low", "init_lesson", _s, _idx); _idx += 1
for _s in range(1, 3):
    SLOTS[f"dose-lo-s{_s}"] = ("pin", "beta_lo", "init_lesson", _s, _idx); _idx += 1
for _s in range(1, 3):
    SLOTS[f"dose-hi-s{_s}"] = ("pin", "beta_hi", "init_lesson", _s, _idx); _idx += 1
for _s in range(1, 3):
    SLOTS[f"beam10-s{_s}"] = ("pin", "beta_low", "init_lesson", _s, _idx); _idx += 1
SLOTS["beam15-s1"] = ("pin", "beta_low", "init_lesson", 1, _idx); _idx += 1
assert _idx == 41

MIX = {}  # all-policy, no exception (owner 2026-09-13)

# slot -> [(section, key, value)]; every other slot trains at the anchor.
FLAT = [("actions", "groom_cuddle_floor", 0.5),
        ("actions", "groom_cuddle_slope", 0.0),
        ("actions", "groom_cuddle_ceiling", 0.5)]
OVERRIDES = {
    "flat-s1": FLAT, "flat-s2": FLAT, "flat-s3": FLAT,
    "beam10-s1": [("actions", "sleep_relief_sunbeam", 10.0)],
    "beam10-s2": [("actions", "sleep_relief_sunbeam", 10.0)],
    "beam15-s1": [("actions", "sleep_relief_sunbeam", 15.0)],
}


def apply_overrides(text, overrides):
    """Rewrite `key = value` inside its `[section]` (one line), or insert
    the line right under the section header when the key is absent."""
    for section, key, value in overrides:
        head = re.search(rf"(?m)^\[{re.escape(section)}\]\s*$", text)
        assert head, f"no [{section}] section"
        nxt = re.search(r"(?m)^\[", text[head.end():])
        end = head.end() + (nxt.start() if nxt else len(text) - head.end())
        body = text[head.end():end]
        line = f"{key} = {value}"
        new, n = re.subn(rf"(?m)^{re.escape(key)} = .*$", line, body)
        assert n <= 1, (section, key, n)
        if n == 0:
            new = f"\n{line}  # fog-gen1-cert slot override\n" + body.lstrip("\n")
        text = text[:head.end()] + new + text[end:]
    return text


def derive_config_with_overrides(radius, out_path):
    """The shakeout's derive_config (radius only), then this slot's
    overrides, checked the same way: the result equals the anchor with
    the radius and exactly these keys moved."""
    tf.ANCHOR_TOML = ANCHOR_TOML
    _derive_radius_only(radius, out_path)
    overrides = OVERRIDES.get(CURRENT["slot"], [])
    if overrides:
        out_path.write_text(apply_overrides(out_path.read_text(), overrides))
    with out_path.open("rb") as f:
        cfg = tomllib.load(f)
    with ANCHOR_TOML.open("rb") as f:
        base = tomllib.load(f)
    base["vision"]["radius"] = radius
    for section, key, value in overrides:
        base[section][key] = value
    assert cfg == base, "derived config differs from anchor beyond radius + declared overrides"
    (out_path.parent / "cert-overrides.json").write_text(
        json.dumps({"slot": CURRENT["slot"], "overrides": overrides}, indent=2) + "\n")
    return cfg


CURRENT = {"slot": None}


def install():
    """Point the shakeout trainer at this pass's tables."""
    tf.ANCHOR_TOML = ANCHOR_TOML
    tf.SHAKEOUT = CERT
    tf.PINS = PINS
    tf.SLOTS = SLOTS
    tf.MIX = MIX
    tf.derive_config = derive_config_with_overrides


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--slot" in argv:
        CURRENT["slot"] = argv[argv.index("--slot") + 1]
    install()
    sys.argv = [sys.argv[0]] + argv
    tf.main()


if __name__ == "__main__":
    main()
