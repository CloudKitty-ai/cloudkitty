# Gen 2 §3 other-row field audit (2026-10-14)

Closes the pre-sitting half of the skeleton §3 blank
(`gen2-prereg-skeleton-2026-10-09.md` L139-141):

> [BLANK] Observation rows for others carry WHICH visible fields
> exactly (position, activity, bath, message digest, purr;
> confirm nothing else leaks at the field level — audit at spec).

Spec 058 landed (#444-446); this audit confirms the SHIPPED binding
against the spec's contract, so the sitting can confirm-and-cite
instead of re-deciding. The sitting's word still pins the blank.

## Method

`audit_fields.py` compares `cloudkitty.COLUMN_MAPS[6]` (the binding's
own map, `cloudkitty_rl::schema_map::column_map(6)`, derived from the
encoder's offset constants) against the kitty-row table of
`specs/058-gen2-observation-schema/contracts/observation-v6.md`,
restated in the auditor as independent literals. Four checks: block
shape (109, 58, 4); every contract cell present at its contract
offset and no shipped cell outside the contract; the restated table's
cells tile all 58 offsets with no gap or overlap (a property of the
contract table, which the offset agreement then pins to the binding);
no kitty-row cell name in a
hidden-state family (needs, happiness, identity, distress, memory,
progress, pursuit, wall, waypoint, dirt). Binding: the lab venv's
cloudkitty 0.3.0, maturin-rebuilt 2026-10-12 from main.

## Result — PASS (0 problems)

| cell | offset | width | §3 field |
|---|---|---|---|
| kitty_row.present | 0 | 1 | position (row state) |
| kitty_row.bearing_x | 1 | 1 | position |
| kitty_row.bearing_y | 2 | 1 | position |
| kitty_row.linear | 3 | 1 | position |
| kitty_row.log | 4 | 1 | position |
| kitty_row.bath | 5 | 1 | bath (the one visible need) |
| kitty_row.activity_block | 6 | 7 | activity |
| kitty_row.partner | 13 | 1 | activity (visible acts) |
| kitty_row.is_my_target | 14 | 1 | activity (visible acts) |
| kitty_row.in_water | 15 | 1 | world fact about a visible cat |
| kitty_row.on_sunbeam | 16 | 1 | world fact about a visible cat |
| kitty_row.scene_age | 17 | 1 | world fact about a visible cat |
| kitty_row.msg_block | 18 | 30 | message digest (purr = a HEAD_KINDS row) |
| kitty_row.want_block | 48 | 6 | message digest (want intensities) |
| kitty_row.answers_me_block | 54 | 4 | message digest (answers-me bits) |

Purr: audible, inside the message digest — HEAD_KINDS index 5, so
kitty-row offsets recency 28, rate 29.

The blank's five-word list covers twelve of the fifteen named cells:
position takes the five row-state/spatial cells; activity takes the
one-hot plus partner and is-my-target (the contract's "visible
acts"); bath takes its cell; message digest takes the message block,
want intensities and answers-me bits (the contract's "the audible
digest"), with purr inside the message block. Three cells sit outside
the list — in-water, on-sunbeam and scene-age — and the contract's
leak-audit paragraph (FR-007a) justifies them as "world facts about a
visible cat". The sitting pins whether the blank's field list is
recorded as this fifteen-cell enumeration.

No hidden state at the field level: the five hidden needs, happiness,
identity, distress, memory, progress and pursuit appear nowhere in
the kitty row. The contract's removed-vs-v5 claim (five need cells
and happiness gone) holds in the shipped map.

## Scope

Field-level (names and offsets) only. Value-level leakage — a
legally-named cell carrying a hidden value — is the Part A checker's
job on the fresh Gen 2 corpus and is not claimed here.

## Regeneration

```
experiments/exp-006-character-gen/.venv/bin/python \
    experiments/gen2-field-audit-2026-10-14/audit_fields.py --md
```

Guard: `test_audit_fields.py` (8 plain-assert tests; synthetic maps
use the contract's literals, never the auditor's table).
