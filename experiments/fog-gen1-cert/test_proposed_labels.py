#!/usr/bin/env python3
"""Guard for bc-collect's proposed-label columns (plain asserts).

CLI:        test_proposed_labels.py NEW_ROLLOUT_DIR [OLD_ROLLOUT_DIR]
Self-test:  test_proposed_labels.py            (no args; runs test_*)

Message half (`label_msg_proposed.npy`): the proposed file exists with
the row count; a downgrade only ever goes to Silent (applied != Silent
implies proposed == applied); every proposed label is legal under the
start-of-tick message mask; and at least one row was downgraded.

Activity half (`label_proposed.npy`, PR #459): the PROPOSED action
under the collection codec, row-aligned with label.npy. An
inexpressible proposed action falls back to the APPLIED label and is
counted in meta `proposed_inexpressible` — never index 0 (head 0 is
Move North, not Idle; the message half's unwrap_or(0) convention would
mislabel here). A divergent row is therefore always a real,
expressible disagreement, so file divergence must equal meta
`action_downgraded`. Unlike label.npy, proposed rows may be
mask-illegal (~3% live — the mask guards the APPLIED action only), so
there is deliberately NO mask-legality assert on this column.

The fallback has never fired live (`proposed_inexpressible` is 0 on
every run to date), so no live rollout can red a collector
"simplified" to unwrap_or(0). The self-test pins the invariant on
planted payloads instead: two copies of a real fixture rollout that
differ only in what the fallback wrote — the correct twin (fallback
rows repeat the applied label) must pass check_rollout, the
unwrap_or(0) twin must fail it.

With OLD_ROLLOUT_DIR (the same seed, config and ticks recorded by the
previous tool): every file in BYTE_IDENTICAL is byte-identical, so the
running clones' data did not move. The list now includes both proposed
columns; comparisons against a pre-#459 old dir fail loudly on the
missing file rather than skipping it.

Fixture: `results-raw/fixture-proposed/config-00-rollout-00` — a real
capture (gen2-world-draft-2026-10-15.toml, 1 rollout x 400 ticks,
seed 996201, bc-collect at 5c5f32a3; its meta carries the
engine_commit). Deterministic: a re-capture reproduces the bytes
given the same binary. Never delete it; the self-test depends on it.
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
FIXTURE = HERE / "results-raw" / "fixture-proposed" / "config-00-rollout-00"

BYTE_IDENTICAL = ("obs", "mask", "label", "mask_msg", "label_msg",
                  "label_msg_proposed", "label_proposed",
                  "kitty", "tick", "reward", "state")


def check_rollout(new):
    # Message half (unchanged from the original guard).
    applied = np.load(new / "label_msg.npy")
    proposed = np.load(new / "label_msg_proposed.npy")
    mask_msg = np.load(new / "mask_msg.npy").astype(bool)
    n = len(applied)
    assert proposed.shape == (n,) and proposed.dtype == applied.dtype, (proposed.shape, proposed.dtype)
    spoke = applied != 0
    assert (proposed[spoke] == applied[spoke]).all(), "an applied word must be the proposed word"
    assert mask_msg[np.arange(n), proposed].all(), "a proposed label outside the start-of-tick mask"
    down = int((proposed != applied).sum())
    assert down > 0, "no downgraded row: the proposed file repeats the applied labels"
    meta_text = (new / "meta.json").read_text()
    assert f'"msg_downgraded": {down}' in meta_text, "meta.json msg_downgraded disagrees with the file"

    # Activity half (PR #459).
    label = np.load(new / "label.npy")
    prop = np.load(new / "label_proposed.npy")
    assert prop.shape == label.shape and prop.dtype == label.dtype, (prop.shape, prop.dtype)
    meta = json.loads(meta_text)
    assert "proposed_inexpressible" in meta, "meta.json lost proposed_inexpressible"
    diff = int((prop != label).sum())
    assert diff == meta["action_downgraded"], (
        f"label_proposed divergence {diff} != meta action_downgraded "
        f"{meta['action_downgraded']}: a fallback writing anything but the "
        "applied label (e.g. unwrap_or(0)) lands here")
    assert diff > 0, "no divergent action row: label_proposed repeats label"
    print(f"proposed labels ok: {n} rows, {down} msg downgraded, "
          f"{diff} action downgraded, "
          f"{meta['proposed_inexpressible']} inexpressible")


def check_bytes(new, old):
    for f in BYTE_IDENTICAL:
        a, b = (new / f"{f}.npy").read_bytes(), (old / f"{f}.npy").read_bytes()
        assert a == b, f"{f}.npy moved between the two collectors"
    print("byte-identical across the two collections")


# ---------------------------------------------------------------- self-test

def plant(td, mutate):
    """Copy the fixture rollout into td and hand it to `mutate(dir)`;
    refuse a plant that changes no file."""
    d = Path(td) / "rollout"
    shutil.copytree(FIXTURE, d)
    before = {p.name: p.read_bytes() for p in d.iterdir()}
    mutate(d)
    after = {p.name: p.read_bytes() for p in d.iterdir()}
    assert before != after, "vacuous plant: mutation changed nothing"
    return d


def _fallback_rows(d, k=5):
    """Rows a correct collector's fallback is indistinguishable on:
    proposed == applied and applied != 0."""
    label = np.load(d / "label.npy")
    prop = np.load(d / "label_proposed.npy")
    rows = np.flatnonzero((prop == label) & (label != 0))[:k]
    assert len(rows) == k
    return rows


def _bump_inexpressible(d, k):
    meta = json.loads((d / "meta.json").read_text())
    meta["proposed_inexpressible"] += k
    (d / "meta.json").write_text(json.dumps(meta, indent=2))


def test_fixture_passes():
    check_rollout(FIXTURE)
    check_bytes(FIXTURE, FIXTURE)


def test_unwrap_or_0_fallback_rejected():
    """The pin, FAIL side: what a collector 'simplified' to unwrap_or(0)
    would have written — fallback rows carry 0, counters untouched."""
    def mutate(d):
        rows = _fallback_rows(d)
        prop = np.load(d / "label_proposed.npy")
        prop[rows] = 0
        np.save(d / "label_proposed.npy", prop)
        _bump_inexpressible(d, len(rows))
    with tempfile.TemporaryDirectory() as td:
        d = plant(td, mutate)
        try:
            check_rollout(d)
        except AssertionError as e:
            assert "action_downgraded" in str(e), e
        else:
            raise AssertionError("unwrap_or(0) fallback output accepted")


def test_correct_fallback_accepted():
    """The pin, PASS side: the same rows marked inexpressible, proposed
    column untouched (the correct fallback repeats the applied label)."""
    def mutate(d):
        _bump_inexpressible(d, len(_fallback_rows(d)))
    with tempfile.TemporaryDirectory() as td:
        check_rollout(plant(td, mutate))


def test_collector_wired_to_applied_rejected():
    """A collector writing the applied column twice: diff == meta == 0
    satisfies the equality; diff > 0 is what rejects it."""
    def mutate(d):
        label = np.load(d / "label.npy")
        np.save(d / "label_proposed.npy", label)
        meta = json.loads((d / "meta.json").read_text())
        meta["action_downgraded"] = 0
        (d / "meta.json").write_text(json.dumps(meta, indent=2))
    with tempfile.TemporaryDirectory() as td:
        d = plant(td, mutate)
        try:
            check_rollout(d)
        except AssertionError as e:
            assert "repeats label" in str(e), e
        else:
            raise AssertionError("applied-wired proposed column accepted")


def test_byte_identity_catches_moved_proposed():
    def mutate(d):
        raw = bytearray((d / "label_proposed.npy").read_bytes())
        raw[-1] ^= 1
        (d / "label_proposed.npy").write_bytes(raw)
    with tempfile.TemporaryDirectory() as td:
        d = plant(td, mutate)
        try:
            check_bytes(d, FIXTURE)
        except AssertionError as e:
            assert "label_proposed" in str(e), e
        else:
            raise AssertionError("moved label_proposed.npy accepted")


def test_malformed_rollout_rejected():
    def truncate(d):
        prop = np.load(d / "label_proposed.npy")
        np.save(d / "label_proposed.npy", prop[:-1])
    def drop_key(d):
        meta = json.loads((d / "meta.json").read_text())
        del meta["proposed_inexpressible"]
        (d / "meta.json").write_text(json.dumps(meta, indent=2))
    for mutate in (truncate, drop_key):
        with tempfile.TemporaryDirectory() as td:
            d = plant(td, mutate)
            try:
                check_rollout(d)
            except AssertionError:
                pass
            else:
                raise AssertionError(f"{mutate.__name__} plant accepted")


def main():
    if len(sys.argv) > 1:
        check_rollout(Path(sys.argv[1]))
        if len(sys.argv) > 2:
            check_bytes(Path(sys.argv[1]), Path(sys.argv[2]))
        return
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
    print(f"{sum(1 for n in globals() if n.startswith('test_'))} passed")


if __name__ == "__main__":
    main()
