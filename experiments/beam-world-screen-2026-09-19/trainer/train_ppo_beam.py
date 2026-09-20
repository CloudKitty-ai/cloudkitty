#!/usr/bin/env python3
"""Beam-world screen, tier 2: the shakeout trainer
(`fog-gen1-shakeout/trainer/train_ppo_fog.py`) with this screen's tables,
the way `fog-gen1-cert/trainer/train_ppo_cert.py` did it for the step-7
pass. Nothing in the PPO loop, the stop rules, the probe cadence or the
manifest changes; what changes is declared in `PREREG-tier2.md`:

  - anchor = `fog-gen1-cert/anchor-b3.toml`, and each slot's WORLD is the
    anchor with the five beam-package keys moved by `derive_configs.derive`
    (the tier-1 derivation, guard `test_derive_configs.py`), byte-identical
    to the committed `package.toml` / `floor5.toml`;
  - SLOTS = four arms, run indices 41-44 (bands [920M, 1000M));
  - PINS: `init_lesson` = the package-corpus lesson clone (stage 1),
    `critic` = the B3 critic (reused, declared), `beta_low` 0.04;
  - MIX is empty (all-policy).

    experiments/exp-006-character-gen/.venv/bin/python \\
        experiments/beam-world-screen-2026-09-19/trainer/train_ppo_beam.py --slot pkg-s1

Run from the repo root with the exp-006 venv. Guard: test_train_ppo_beam.py.
"""
import hashlib
import json
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
BEAM = HERE.parent
EXPTS = BEAM.parent
CERT = EXPTS / "fog-gen1-cert"
sys.path.insert(0, str(EXPTS / "fog-gen1-shakeout" / "trainer"))
sys.path.insert(0, str(BEAM))
import train_ppo_fog as tf  # noqa: E402
import derive_configs as dc  # noqa: E402

ANCHOR_TOML = CERT / "anchor-b3.toml"
TIER2 = BEAM / "results-raw" / "tier2"

PINS = {
    "radius": 4,          # the served pin (#351); anchor-b3 already carries it
    "beta_low": 0.04,     # the pool's dose, F-019 low end
    # package-corpus lesson clone (stage 1: strip, then teach); bars in bars-proposed.json beside it
    "init_lesson": str(TIER2 / "clones" / "pkg-vocab" / "pkg-vocab.pt"),
    # B3 critic reused (declared in PREREG-tier2 §Critic), as the consent-off twin reused it
    "critic": str(CERT / "results-raw" / "clones" / "b3-critic" / "critic6-0p998.pt"),
}

# slot -> (sleep_relief, sleep_relief_sunbeam, sunbeam ttl, sunbeam count[, off-beam sleep floor]); the
# committed file it must equal. Tier 5 (spec 056, PREREG-tier5.md): the package world plus the floor key.
WORLD = {
    "pkg-s1": ((3.0, 7.0, 3000, 6), BEAM / "package.toml"),
    "pkg-s2": ((3.0, 7.0, 3000, 6), BEAM / "package.toml"),
    "floor5-s1": ((5.0, 7.0, 3000, 6), BEAM / "floor5.toml"),
    "floor5-s2": ((5.0, 7.0, 3000, 6), BEAM / "floor5.toml"),
}
# The floor worlds are committed (spec 056 merged 2026-09-20, fbd06e0) and also pinned by the SHA-256
# PREREG-tier5.md declares; derive_config_beam checks both.
for _f in (10, 15, 20, 25):
    for _s in (1, 2):
        WORLD[f"sg{_f}-s{_s}"] = ((3.0, 7.0, 3000, 6, _f), BEAM / f"shallow-{_f}.toml")
# Tier 6 (PREREG-tier6.md): floor 15 at counts 5 / 7 / 8 (count 6 = sg15-s1/s2 as trained).
for _n in (5, 7, 8):
    for _s in (1, 2):
        WORLD[f"cnt{_n}-s{_s}"] = ((3.0, 7.0, 3000, _n, 15), BEAM / f"count-{_n}.toml")

PREREGS = ("PREREG-tier5.md", "PREREG-tier6.md")


def declared_sha(name):
    """The SHA-256 a prereg declares for a derived world (`- <name> `<sha>``): PREREG-tier5.md for the
    shallow-N floor worlds, PREREG-tier6.md for the count-N worlds."""
    import re
    for p in PREREGS:
        m = re.search(rf"^- {re.escape(name)} `([0-9a-f]{{64}})`", (BEAM / p).read_text(), re.M)
        if m:
            return m.group(1)
    raise AssertionError(f"{name} has no declared sha in {PREREGS}")
# slot -> (radius rule, beta pin, init pin, seed, run_index); run indices 41-44 follow the cert's 21-40,
# 45-52 are tier 5's (PREREG-tier5.md)
SLOTS = {
    "pkg-s1": ("pin", "beta_low", "init_lesson", 1, 41),
    "pkg-s2": ("pin", "beta_low", "init_lesson", 2, 42),
    "floor5-s1": ("pin", "beta_low", "init_lesson", 1, 43),
    "floor5-s2": ("pin", "beta_low", "init_lesson", 2, 44),
}
_idx = 45
for _f in (10, 15, 20, 25):
    for _s in (1, 2):
        SLOTS[f"sg{_f}-s{_s}"] = ("pin", "beta_low", "init_lesson", _s, _idx); _idx += 1
# 53-58 are tier 6's (PREREG-tier6.md; bands [1160M, 1280M))
for _n in (5, 7, 8):
    for _s in (1, 2):
        SLOTS[f"cnt{_n}-s{_s}"] = ("pin", "beta_low", "init_lesson", _s, _idx); _idx += 1
MIX = {}
CURRENT = {"slot": None}


def derive_config_beam(radius, out_path):
    """The slot's world: anchor-b3 with the package keys moved (tier-1 derivation), radius
    untouched (the anchor carries the pin). Re-read and checked equal to the committed file."""
    levels, committed = WORLD[CURRENT["slot"]]
    text = dc.derive(ANCHOR_TOML.read_text(), *levels)
    out_path.write_text(text)
    with out_path.open("rb") as f:
        cfg = tomllib.load(f)
    assert cfg["vision"]["radius"] == radius, (cfg["vision"], radius)
    with ANCHOR_TOML.open("rb") as f:
        base = tomllib.load(f)
    assert dc.moved_keys(base, cfg) <= dc.MOVED, dc.moved_keys(base, cfg)
    sb = cfg["elements"]["sunbeam"]
    assert (cfg["actions"]["sleep_relief"], cfg["actions"]["sleep_relief_sunbeam"], sb["ttl"], sb["min"]) == levels[:4]
    if len(levels) == 5:
        assert cfg["actions"][dc.FLOOR_KEY] == levels[4], (cfg["actions"].get(dc.FLOOR_KEY), levels)
    else:
        assert dc.FLOOR_KEY not in cfg["actions"]
    assert out_path.read_bytes() == committed.read_bytes(), f"derived world differs from {committed.name}"
    if len(levels) == 5:
        assert hashlib.sha256(out_path.read_bytes()).hexdigest() == declared_sha(committed.stem), f"derived world differs from the sha PREREG-tier5.md declares for {committed.stem}"
    (out_path.parent / "beam-world.json").write_text(json.dumps({
        "slot": CURRENT["slot"], "levels": levels, "world": committed.name,
        "world_sha256": hashlib.sha256(out_path.read_bytes()).hexdigest()}, indent=2) + "\n")
    return cfg


def install():
    tf.ANCHOR_TOML = ANCHOR_TOML
    tf.SHAKEOUT = BEAM          # artifacts/ppo-fog-<slot> under this directory (gitignored)
    tf.PINS = PINS
    tf.SLOTS = SLOTS
    tf.MIX = MIX
    tf.derive_config = derive_config_beam


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--slot" in argv:
        CURRENT["slot"] = argv[argv.index("--slot") + 1]
    install()
    sys.argv = [sys.argv[0]] + argv
    tf.main()


if __name__ == "__main__":
    main()
