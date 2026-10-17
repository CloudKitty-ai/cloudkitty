# Contract: Config Surface (FR-001, FR-002, FR-006, FR-008)

## 1. The `[starts]` table

```toml
# Absent table = knob off = today's explicit-starts behavior, byte for byte.
[starts]
edge_ring_share = 0.25   # P(drawn start on the edge ring) — corners-INCLUSIVE:
                         #   this share CONTAINS corner_share, matching
                         #   coverage_read.py's edge-ring count. The draw law's
                         #   EdgeRing category is the corners-EXCLUSIVE
                         #   remainder (probability edge_ring_share − corner_share).
corner_share = 0.05      # P(drawn start on one of the 4 corner tiles)
```

- Unknown keys are a load-time error (`deny_unknown_fields`), as everywhere.
- Both fields are required when the table is present.
- Shares are per-kitty probabilities, not quotas (owner ruling 2026-10-15).
- The table is ENGINE config (unlike `[stuck_detector]`'s foreign table): it
  changes world generation. It is `Option` + skip-if-none, so the compiled
  defaults' serialization — and the `engine_defaults_sha256` stamp — do not
  move.

## 2. `[[kitty]]` coordinates

- `x` and `y` become optional in the schema. Semantics:
  - both set: the kitty is **explicit** — keeps its tile exactly as today,
    knob on or off; with the knob on, its tile is pre-marked occupied before
    any draw.
  - neither set: the kitty is **drawn** — legal only with the knob on.
  - exactly one set: load-time error naming the kitty, always.
- A config without `[starts]` in which any kitty lacks coordinates is a
  load-time error naming the kitty (preserves today's "x/y required"
  behavior, enforced by validation now that the schema admits absence).

## 3. Load-time validation (Config::validate)

New section `validate_starts()` appended at position 19 (spec 020 order
contract: append, never reorder). Errors name the offending field and the
allowed relation:

| Condition | Error names |
|---|---|
| `edge_ring_share` ∉ [0, 1] | the field and the range |
| `corner_share` ∉ [0, 1] | the field and the range |
| `corner_share > edge_ring_share` | both fields and the relation (non-corner edge probability would be negative) |
| table present and `world.width < 3 || world.height < 3` | the dimension and the ≥3 rule (edge ring and interior must be distinct, corners must be 4 distinct tiles) |

Roster slot (position 2) additions — these fire only on configs that could
not previously parse, so no existing config's first-failing message changes:

| Condition | Error names |
|---|---|
| kitty with exactly one of x/y | the kitty name and the missing field |
| knob off, kitty missing coordinates | the kitty name and that `[starts]` is absent |

Explicit coordinates keep today's checks unchanged: in-bounds, no shared
tile ("same tile" error).

## 4. Build-time failure (World::try_generate)

The only draw failure is category exhaustion: a kitty draws a category whose
free-tile list is empty (after explicit tiles and earlier draws are marked
occupied). The error names the category, the number of kitties drawn into it,
and its total tile capacity — never silent, never spilling into another
category. `World::generate` keeps its signature and panics with the same
message; `World::try_generate` returns it as `Err`.

## 5. Knob-off invariance (FR-001 / SC-004)

A config without `[starts]`: identical parse, identical validation messages,
identical world, identical serialization. The shipped-config sweep, every
golden, and every pin pass untouched in this feature's PRs.
