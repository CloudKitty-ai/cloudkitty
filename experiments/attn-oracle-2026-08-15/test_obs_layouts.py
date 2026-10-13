"""Guard for obs_layouts.py (plain asserts, no pytest). Run in the lab
venv so the binding-verification path is exercised, not skipped:

    .../exp-006-character-gen/.venv/bin/python -B test_obs_layouts.py

Reference values are independent literals, never the layout modules'
own sums (the stage-B shared-constant lesson).
"""
import types

import obs_layouts as OL
import obs_layout_v5 as L5
import obs_layout_v6 as L6

# Keyed lookup: known versions resolve, unknown refuse by name.
assert OL.layout_for(5) is L5 and OL.layout_for(6) is L6
try:
    OL.layout_for(7)
    raise SystemExit("an unknown schema must refuse")
except KeyError as e:
    assert "7" in str(e) and "layout" in str(e)

# Independent-literal pins over the derived constants.
assert L5.OBS_DIM == 408 and L6.OBS_DIM == 399
assert L5.CLOCK_COL == 407 and not hasattr(L6, "CLOCK_COL")
assert L5.SELF_DISTRESS == 20 and L6.SELF_DISTRESS == 22
assert L5.SELF_PURSUIT == 26 and L6.SELF_PURSUIT == 28
assert L5.ACTIVITY_KINDS.index("playing") == 5
assert L6.ACTIVITY_KINDS == L5.ACTIVITY_KINDS
assert L5.DENSE_MENU["sleep_solo"] == 9 == L6.DENSE_MENU["sleep_solo"]
assert L5.DENSE_MENU["idle"] == 38 and L6.DENSE_MENU["idle"] == 34
assert L5.DENSE_MENU["play_solo"] == 29 and L6.DENSE_MENU["play_solo"] == 27

# This is a lab-venv test by design: the binding must be importable and
# both maps verified at import.
import cloudkitty  # noqa: E402

assert OL.BINDING_VERIFIED == frozenset({5, 6}), OL.BINDING_VERIFIED

# The verification bites: one perturbed cell in a fake binding map must
# raise, naming the cell.
real = cloudkitty.COLUMN_MAPS[6]
drifted = {"observation_len": real["observation_len"],
           "blocks": dict(real["blocks"]),
           "cells": dict(real["cells"]),
           "slot_config": real["slot_config"]}
drifted["cells"]["kitty_row.bath"] = drifted["cells"]["kitty_row.bath"] + 1
fake = types.SimpleNamespace(
    COLUMN_MAPS={5: cloudkitty.COLUMN_MAPS[5], 6: drifted},
    ACTION_MENU=cloudkitty.ACTION_MENU,
    OBSERVATION_SCHEMA_VERSION=cloudkitty.OBSERVATION_SCHEMA_VERSION)
try:
    OL.verify_against_binding(fake, 6)
    raise SystemExit("a drifted cell must fail verification")
except AssertionError as e:
    assert "kitty_row.bath" in str(e), e

# And a menu drift bites on the live version.
menu = dict(cloudkitty.ACTION_MENU)
menu["sleep_solo"] = menu["sleep_solo"] + 1
fake = types.SimpleNamespace(
    COLUMN_MAPS=dict(cloudkitty.COLUMN_MAPS), ACTION_MENU=menu,
    OBSERVATION_SCHEMA_VERSION=cloudkitty.OBSERVATION_SCHEMA_VERSION)
try:
    OL.verify_against_binding(fake, 6)
    raise SystemExit("a drifted menu entry must fail verification")
except AssertionError as e:
    assert "sleep_solo" in str(e), e

print("test_obs_layouts ok")
