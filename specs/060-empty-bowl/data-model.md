# Data Model: Empty-Bowl Early End (spec 060)

No new entities, fields, config keys, or events. The amendment
re-combines state that already exists. Anchors from research.md.

## Entities (all existing)

### Eating scene
- Carried as `Activity::Eating` + `ActivityClock { started, applied }`
  on the kitty (kitty.rs). No target-bowl field exists and none is
  added (clarify Q1: the meal is positional, not bowl-bound).
- Derived values: `elapsed = tick - started + 1` (kitty.rs:233),
  `serviced_before = tick - started` (kitty.rs:239).
- Bounds: `Activity::bounds` → `durations.eat`
  (`DurationBounds { min, max }`, shipped `{ min = 2, max = 3 }`).

### Chow element (the bowl)
- `ElementKind::Chow { servings: u32 }` (element.rs:73); "stocked"
  = `servings > 0` (world.rs:1907).
- Consumption: one serving per fed eat tick
  (action.rs:792-803, `saturating_sub(1)`).
- Reaping: `is_expired` true at `servings == 0` (element.rs:107-115),
  removed in the environment phase (world.rs:870), after the end rule
  runs.

### Activity-end record
- Written by `end_activity` (world.rs:479-498) into `activity_log` +
  `pending_endings` — unchanged shape; early ends are ordinary ends
  (FR-003: no refusal-log row, ever).

## The one state-transition change

Scene-end resolution for `Activity::Eating`, evaluated once per tick
in `resolve_activity_ends` after all apply slots:

| Condition at resolution | Today (spec 006) | Under 060 |
|---|---|---|
| `elapsed >= bounds.max` | end | end (unchanged) |
| `elapsed >= min` and need 0 | end | end (unchanged) |
| `elapsed >= min` and feeding condition fails | end | end (unchanged) |
| `elapsed < min`, need 0, feeding condition holds | continue (lick to min) | continue (unchanged, FR-002) |
| `elapsed < min`, feeding condition fails | **continue (paused, zero relief)** | **end** |

Feeding condition = `adjacent_stocked_chow(kitty.pos).is_some()` —
the same predicate validate's Eat arm and the per-tick effect read
(one predicate, four consumers; research R2 carries the
nearest-vs-any owner flag).

## Validation rules

- No config change: `validate_durations` (`1 <= min <= max`) untouched.
- Determinism: the rule reads post-apply world state at a fixed point
  in tick order; divergence enters only via the declared
  `[rng-sequence]` re-record (FR-005).
