#!/usr/bin/env python3
"""Guard for audit_fields.py (plain asserts, no pytest).

Synthetic column maps with hand-built defects pin the audit's four
failure modes; the real binding pins the PASS end. Synthetic maps are
built from independent literals (the 058 contract's own numbers),
never from audit_fields' EXPECTED table — a fixture that moves with
the auditor proves nothing (the coverage_read lesson, af2e55ed).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import audit_fields as af  # noqa: E402

# The 058 contract's kitty-row table, restated here by hand.
CONTRACT_CELLS = {
    "kitty_row.present": 0, "kitty_row.bearing_x": 1, "kitty_row.bearing_y": 2,
    "kitty_row.linear": 3, "kitty_row.log": 4, "kitty_row.bath": 5,
    "kitty_row.activity_block": 6, "kitty_row.partner": 13,
    "kitty_row.is_my_target": 14, "kitty_row.in_water": 15,
    "kitty_row.on_sunbeam": 16, "kitty_row.scene_age": 17,
    "kitty_row.msg_block": 18, "kitty_row.want_block": 48,
    "kitty_row.answers_me_block": 54,
}


def synth_map(cells=None, block=(109, 58, 4)):
    return {"blocks": {"kitty_row": block},
            "cells": dict(CONTRACT_CELLS if cells is None else cells)}


def test_contract_shaped_map_passes():
    assert af.audit(synth_map()) == []


def test_real_binding_passes():
    import cloudkitty
    problems = af.audit(cloudkitty.COLUMN_MAPS[6])
    assert problems == [], problems


def test_extra_cell_is_flagged():
    cells = dict(CONTRACT_CELLS)
    cells["kitty_row.happiness"] = 5   # a shipped cell the contract lacks
    problems = af.audit(synth_map(cells))
    assert any("kitty_row.happiness" in p and "not in the contract" in p
               for p in problems), problems
    # ... and the same cell trips the hidden-state family scan
    assert any("hidden-state family" in p and "happiness" in p
               for p in problems), problems


def test_leak_scan_fires_on_needs_spelling():
    cells = dict(CONTRACT_CELLS)
    cells["kitty_row.needs.eat"] = 5
    problems = af.audit(synth_map(cells))
    assert any("hidden-state family" in p and "needs" in p for p in problems), problems


def test_moved_offset_is_flagged():
    cells = dict(CONTRACT_CELLS)
    cells["kitty_row.bath"] = 6
    problems = af.audit(synth_map(cells))
    assert any("kitty_row.bath at 6" in p and "contract says 5" in p
               for p in problems), problems


def test_missing_cell_is_flagged():
    cells = {k: v for k, v in CONTRACT_CELLS.items() if k != "kitty_row.want_block"}
    problems = af.audit(synth_map(cells))
    assert any("kitty_row.want_block missing" in p for p in problems), problems


def test_wrong_block_shape_is_flagged():
    problems = af.audit(synth_map(block=(109, 59, 4)))
    assert any("kitty_row block" in p for p in problems), problems


def test_purr_lives_in_the_digest():
    rec, rate = af.purr_digest_cells()
    assert (rec, rate) == (28, 29), (rec, rate)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
