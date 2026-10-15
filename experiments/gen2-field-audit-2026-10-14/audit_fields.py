#!/usr/bin/env python3
"""Gen 2 prereg skeleton §3 field-level audit (the [BLANK] at skeleton
L139-141): observation rows for others carry WHICH visible fields
exactly — position, activity, bath, message digest, purr — and nothing
else leaks at the field level.

The audit is map-level: it proves the SHIPPED binding's
COLUMN_MAPS[6] kitty row equals the spec 058 contract's 58-cell
enumeration (specs/058-gen2-observation-schema/contracts/
observation-v6.md §Kitty row), cell for cell with no gap, overlap or
extra, and that no hidden-state name (needs beyond bath, happiness,
identity, distress, memory, progress, pursuit) appears in the row.
Value-level leakage (a cell whose NAME is legal carrying a hidden
VALUE) is Part A's job on the fresh Gen 2 corpus, not this audit's.

Expected offsets and widths below are the CONTRACT's literals,
restated by hand — never imported from obs_layout_v6, which the same
binding verifies (a fixture that moves with the reader proves
nothing).

    experiments/exp-006-character-gen/.venv/bin/python \\
        experiments/gen2-field-audit-2026-10-14/audit_fields.py [--md]

Exit 1 on any mismatch. Guard: test_audit_fields.py.
"""
import argparse
import sys

# Contract table (observation-v6.md §Kitty row), by hand:
# name -> (block-relative offset, width, field category for the §3
# blank). Categories quote the contract's own justification paragraph.
EXPECTED = {
    "present":          (0, 1, "position (row state)"),
    "bearing_x":        (1, 1, "position"),
    "bearing_y":        (2, 1, "position"),
    "linear":           (3, 1, "position"),
    "log":              (4, 1, "position"),
    "bath":             (5, 1, "bath (the one visible need)"),
    "activity_block":   (6, 7, "activity"),
    "partner":          (13, 1, "activity (visible acts)"),
    "is_my_target":     (14, 1, "activity (visible acts)"),
    "in_water":         (15, 1, "world fact about a visible cat"),
    "on_sunbeam":       (16, 1, "world fact about a visible cat"),
    "scene_age":        (17, 1, "world fact about a visible cat"),
    "msg_block":        (18, 30, "message digest (purr = a HEAD_KINDS row)"),
    "want_block":       (48, 6, "message digest (want intensities)"),
    "answers_me_block": (54, 4, "message digest (answers-me bits)"),
}
ROW_WIDTH = 58
BLOCK_START, N_ROWS = 109, 4
# A kitty-row cell name containing any of these is hidden state leaking
# at the field level. "needs" (not "bath"): the five hidden needs and
# any needs.* spelling; the rest are self-block-only families.
FORBIDDEN = ("needs", "happiness", "identity", "distress", "memory",
             "progress", "pursuit", "wall", "waypoint", "dirt")


def audit(column_map):
    """All findings for one column map; empty list = PASS."""
    problems = []
    blk = column_map["blocks"].get("kitty_row")
    if blk != (BLOCK_START, ROW_WIDTH, N_ROWS):
        problems.append(f"kitty_row block {blk} != contract "
                        f"{(BLOCK_START, ROW_WIDTH, N_ROWS)}")
    shipped = {k.split(".", 1)[1]: v for k, v in column_map["cells"].items()
               if k.startswith("kitty_row.")}
    for name, (off, _w, _cat) in EXPECTED.items():
        if name not in shipped:
            problems.append(f"contract cell kitty_row.{name} missing from the binding")
        elif shipped[name] != off:
            problems.append(f"kitty_row.{name} at {shipped[name]}, contract says {off}")
    for name in sorted(set(shipped) - set(EXPECTED)):
        problems.append(f"binding ships kitty_row.{name} (offset {shipped[name]}) "
                        "— not in the contract's kitty-row table")
    covered = []
    for name, (off, w, _cat) in EXPECTED.items():
        covered += list(range(off, off + w))
    if sorted(covered) != list(range(ROW_WIDTH)):
        problems.append(f"contract table does not tile 0..{ROW_WIDTH} "
                        f"(covered {len(covered)} cells)")
    for name in shipped:
        hits = [f for f in FORBIDDEN if f in name]
        if hits:
            problems.append(f"kitty_row.{name} matches hidden-state family {hits}")
    return problems


def purr_digest_cells():
    """Where purr lives inside msg_block: HEAD_KINDS index 5 (binding-
    verified order via obs_layouts at import), so recency 18+2*5=28,
    rate 29 — stated so the blank's 'purr' has a cell to point at."""
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "attn-oracle-2026-08-15"))
    import obs_layout_v6
    i = obs_layout_v6.HEAD_KINDS.index("purr")
    return 18 + 2 * i, 18 + 2 * i + 1


def table_md(column_map):
    lines = ["| cell | offset | width | §3 field |", "|---|---|---|---|"]
    for name, (off, w, cat) in sorted(EXPECTED.items(), key=lambda kv: kv[1][0]):
        lines.append(f"| kitty_row.{name} | {off} | {w} | {cat} |")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", action="store_true", help="print the audit table as markdown")
    a = ap.parse_args(argv)
    import cloudkitty
    cm = cloudkitty.COLUMN_MAPS[6]
    problems = audit(cm)
    rec, rate = purr_digest_cells()
    if a.md:
        print(table_md(cm))
        print(f"\npurr digest cells: recency {rec}, rate {rate} (HEAD_KINDS index 5)")
    for p in problems:
        print(f"LEAK/mismatch: {p}")
    print(f"audit {'FAIL' if problems else 'PASS'}: kitty_row vs the 058 contract, "
          f"{len(EXPECTED)} named cells tiling {ROW_WIDTH}, "
          f"{len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
