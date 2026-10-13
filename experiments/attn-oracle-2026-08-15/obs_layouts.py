"""Schema-keyed layout lookup + binding verification (the Gen 2
reader-flip ruling, prereg skeleton §3 R§carried: every obs/action
index a schema-version-keyed lookup; no raw indices downstream).

`layout_for(schema)` hands back the layout module for a trace or
corpus `observation_schema`, refusing unknown versions by name. When
the `cloudkitty` binding is importable, importing THIS module verifies
every offset the layout modules restate against the binding's
`COLUMN_MAPS` (both directions: every binding cell has a computed
expectation, every expectation matches), and the v6 dense menu
against `ACTION_MENU` — so a drifted restatement fails loudly at the
first keyed import instead of misreading silently. `BINDING_VERIFIED`
holds the versions checked; empty means the binding was not
importable, never that a check failed (a failed check raises).
"""
import obs_layout_v5
import obs_layout_v6

LAYOUTS = {5: obs_layout_v5, 6: obs_layout_v6}


def layout_for(schema):
    if schema not in LAYOUTS:
        raise KeyError(
            f"observation_schema {schema!r}: no layout module here "
            f"(known: {sorted(LAYOUTS)}). A new schema's layout lands "
            "with its spec; do not guess offsets.")
    return LAYOUTS[schema]


def _self_cells(L):
    cells = {
        "self.happiness": L.SELF_HAPPINESS,
        "self.activity_block": L.SELF_ACTIVITY,
        "self.social": L.SELF_PARTNERED,
        "self.in_sunbeam": L.SELF_IN_SUNBEAM,
        "self.in_water": L.SELF_IN_WATER,
        "self.progress": L.SELF_PROGRESS,
        "self.distress_block": L.SELF_DISTRESS,
        "self.pursuit_block": L.SELF_PURSUIT,
        "self.scene_age": L.SELF_SCENE_AGE,
        "self.msg_block": L.SELF_MSG_BLOCK,
        "self.memory_block": L.SELF_MEMORY,
    }
    for i, k in enumerate(L.NEED_KINDS):
        cells[f"self.needs.{k}"] = L.SELF_NEEDS + i
    return cells


def _row_cells(L):
    return {
        "kitty_row.present": L.ROW_PRESENT,
        "kitty_row.activity_block": L.ROW_ACTIVITY,
        "kitty_row.partner": L.ROW_PARTNERED,
        "kitty_row.is_my_target": L.ROW_IS_TARGET,
        "kitty_row.in_water": L.ROW_WATER_BIT,
        "kitty_row.on_sunbeam": L.ROW_SUNBEAM_BIT,
        "kitty_row.scene_age": L.ROW_SCENE_AGE,
        "kitty_row.msg_block": L.ROW_MSG_BLOCK,
        "kitty_row.want_block": L.ROW_INTENSITY,
        "kitty_row.answers_me_block": L.ROW_ANSWERS_ME,
    }


def _expected_cells(version):
    """Every cell name COLUMN_MAPS[version] serves, computed from the
    layout module's own sums."""
    L = LAYOUTS[version]
    cells = _self_cells(L)
    cells.update(_row_cells(L))
    if version == 5:
        cells.update({
            "self.pos.x": L.SELF_POS, "self.pos.y": L.SELF_POS + 1,
            "self.traits_block": L.SELF_TRAITS,
            "clock": L.CLOCK_COL,
            "kitty_row.dx": L.ROW_DX, "kitty_row.dy": L.ROW_DY,
            "kitty_row.distance": L.ROW_DIST,
            "kitty_row.happiness": L.ROW_HAPPINESS,
        })
        for i, k in enumerate(L.NEED_KINDS):
            cells[f"kitty_row.needs.{k}"] = L.ROW_NEEDS + i
        spatial = {"dx": L.SLOT_DX, "dy": L.SLOT_DY,
                   "distance": L.SLOT_DIST}
        tail = L.SLOT_DIST
    else:
        cells.update({
            "self.identity_block": L.SELF_IDENTITY,
            "self.identity.need_rates": L.SELF_IDENTITY,
            "self.identity.comfort_slack": L.SELF_IDENTITY + 6,
            "self.identity.consent_line": L.SELF_IDENTITY + 7,
            "self.identity.favourite_block": L.SELF_IDENTITY + 8,
            "self.waypoint_block": L.SELF_WAYPOINT,
            "self.dirt_reserve_block": L.SELF_DIRT_RESERVE,
            "self.wall.n": L.SELF_WALLS, "self.wall.e": L.SELF_WALLS + 1,
            "self.wall.s": L.SELF_WALLS + 2, "self.wall.w": L.SELF_WALLS + 3,
            "kitty_row.bearing_x": L.ROW_BEARING,
            "kitty_row.bearing_y": L.ROW_BEARING + 1,
            "kitty_row.linear": L.ROW_LINEAR, "kitty_row.log": L.ROW_LOG,
            "kitty_row.bath": L.ROW_BATH,
        })
        spatial = {"bearing_x": L.SLOT_BEARING,
                   "bearing_y": L.SLOT_BEARING + 1,
                   "linear": L.SLOT_LINEAR, "log": L.SLOT_LOG}
        tail = L.SLOT_LOG
    for kind in ("chow", "water", "sunbeam", "critter"):
        cells[f"{kind}.present"] = L.SLOT_PRESENT
        for name, off in spatial.items():
            cells[f"{kind}.{name}"] = off
    # Per-kind tails after the spatial group (observe.rs order).
    cells["chow.servings"] = tail + 1
    cells["sunbeam.ttl"] = tail + 1
    cells["sunbeam.occupied"] = tail + 2
    cells["critter.is_greeble"] = tail + 1
    cells["critter.heading_block"] = tail + 2        # four heading cells
    cells["critter.is_activity_target"] = tail + 6
    return cells


def _expected_blocks(L):
    blocks, off = {}, dict(L.WIDTHS)["self"]
    for name, w in L.WIDTHS[1:]:
        if name == "clock":
            continue
        key = "kitty_row" if name == "kitty" else name
        blocks[key] = (off, w, L.COUNTS[name])
        off += w * L.COUNTS[name]
    return blocks


def verify_against_binding(cloudkitty, version):
    """Assert one layout module against COLUMN_MAPS[version]; for the
    live version, the dense menu against ACTION_MENU too."""
    L, m = LAYOUTS[version], cloudkitty.COLUMN_MAPS[version]
    bad = []
    if m["observation_len"] != L.OBS_DIM:
        bad.append(f"observation_len {m['observation_len']} != {L.OBS_DIM}")
    exp_blocks = _expected_blocks(L)
    if dict(m["blocks"]) != exp_blocks:
        bad.append(f"blocks {dict(m['blocks'])} != {exp_blocks}")
    exp = _expected_cells(version)
    got = dict(m["cells"])
    for k in sorted(set(exp) | set(got)):
        if k not in got:
            bad.append(f"cell {k}: expected {exp[k]}, binding serves none")
        elif k not in exp:
            bad.append(f"cell {k}: binding serves {got[k]}, no expectation "
                       "computed here (extend obs_layouts.py)")
        elif got[k] != exp[k]:
            bad.append(f"cell {k}: binding {got[k]} != layout {exp[k]}")
    if version == cloudkitty.OBSERVATION_SCHEMA_VERSION:
        menu = dict(cloudkitty.ACTION_MENU)
        if len(menu) != L.N_ACT:
            bad.append(f"menu {len(menu)} entries != N_ACT {L.N_ACT}")
        for name, idx in L.DENSE_MENU.items():
            if menu.get(name) != idx:
                bad.append(f"menu {name}: binding {menu.get(name)} != {idx}")
        for k in range(L.COUNTS["kitty"]):
            exp_k = [menu[f"{v}_kitty_{k}"] for v in
                     ("rest_with", "sleep_with", "groom", "chase", "play")]
            if L.KITTY_MENU[k] != exp_k:
                bad.append(f"KITTY_MENU[{k}] {L.KITTY_MENU[k]} != {exp_k}")
        for j in range(L.COUNTS["critter"]):
            exp_j = [menu[f"chase_critter_{j}"], menu[f"play_critter_{j}"]]
            if L.CRIT_MENU[j] != exp_j:
                bad.append(f"CRIT_MENU[{j}] {L.CRIT_MENU[j]} != {exp_j}")
    if bad:
        raise AssertionError(
            f"obs_layout_v{version} drifted from the binding's "
            f"COLUMN_MAPS[{version}]:\n  " + "\n  ".join(bad))


BINDING_VERIFIED = frozenset()
try:
    import cloudkitty as _ck
except ImportError:
    pass
else:
    for _v in sorted(LAYOUTS):
        verify_against_binding(_ck, _v)
    BINDING_VERIFIED = frozenset(LAYOUTS)
