#!/usr/bin/env python3
"""Guard for starts_check.py (plain asserts, python3 -B). Fixtures are
REAL payloads: the engine-emitted golden vectors (committed, CI
byte-pinned), three recorded knob-on bc-collect metas
(results-raw/fixture-starts-echo/, g2leg-20 at g2cmp seeds — never
delete), and the pilot manifest. Mutate cycles run via
scripts/mutate.sh on starts_check.py."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import starts_check as sc

GOLDEN = HERE.parents[1] / "specs/062-randomized-starts/contracts/golden-draws.json"
FIXTURES = HERE / "results-raw/fixture-starts-echo"
LEGS20 = HERE.parent / "gen2-comparator-legs-2026-10-14/g2leg-20.toml"
MANIFEST = HERE / "results-raw/pilot-30/manifest.json"


def test_golden_byte_exact():
    assert sc.check_golden(GOLDEN) == 0


def test_golden_sensitivity_seed():
    # A one-bit input change must change the draw stream: the same case
    # at seed+1 may not reproduce the recorded u64s (self-test that the
    # comparison would catch a stream break).
    case = json.load(open(GOLDEN))["cases"][0]
    draws = []
    sc.engine_draw(case["seed"] + 1, case["width"], case["height"],
                   case["edge_ring_share"], case["corner_share"],
                   case["roster"], collect_u64s=draws)
    assert draws != case["u64_draws"]


def test_engine_echo_fixtures():
    for seed in (905001, 905013, 905029):
        assert sc.check_meta(FIXTURES / f"meta-{seed}.json", LEGS20) == 0


def test_echo_sensitivity():
    # A tampered echo position must fail: flip one coordinate.
    meta = json.load(open(FIXTURES / "meta-905001.json"))
    meta["starts"][0]["x"] = (meta["starts"][0]["x"] + 1) % 20
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(meta, f)
    assert sc.check_meta(f.name, LEGS20) == 1


def test_manifest_replay():
    assert sc.check_manifest(MANIFEST) == 0


def test_explicit_kitty_consumes_no_draws():
    # Law property: pinning a kitty explicit shifts no other draw.
    case = json.load(open(GOLDEN))["cases"][0]
    base = sc.engine_draw(case["seed"], case["width"], case["height"],
                          case["edge_ring_share"], case["corner_share"],
                          case["roster"])
    first = base[0]
    pinned = [dict(case["roster"][0], x=first[1], y=first[2])] + case["roster"][1:]
    # The law's clause: an explicit kitty consumes ZERO draws, so the
    # remaining kitties read the stream from its start — the pinned
    # run's u64 sequence is a prefix of the base run's, two shorter.
    draws_base, draws_pinned = [], []
    sc.engine_draw(case["seed"], case["width"], case["height"],
                   case["edge_ring_share"], case["corner_share"],
                   case["roster"], collect_u64s=draws_base)
    sc.engine_draw(case["seed"], case["width"], case["height"],
                   case["edge_ring_share"], case["corner_share"], pinned,
                   collect_u64s=draws_pinned)
    assert len(draws_pinned) == len(draws_base) - 2
    assert draws_pinned == draws_base[:len(draws_pinned)]


if __name__ == "__main__":
    passed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
            passed += 1
    print(f"{passed} passed")
