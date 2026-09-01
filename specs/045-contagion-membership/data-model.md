# Data Model: spec 045

No new runtime state. Both dials are pure configuration; every derived
quantity is recomputed per tick (membership) or per decision (exposure)
from existing world state.

## Config entities

### `ContagionMembership` (new enum, `config/mod.rs`)

| variant | TOML value | meaning |
|---|---|---|
| `OptionA` (default) | `"option_a"` | the shipped 044 rule: only the dry NAMER pays |
| `Bidirectional` | `"bidirectional"` | any dry member of a wet/dry pair pays, either role |

- Field: `WaterConfig.contagion_membership`, `#[serde(default,
  skip_serializing_if = "ContagionMembership::is_option_a")]`.
- Absent ≡ `option_a` ≡ shipped 044 behavior, byte-identical (stamp
  guard + explicit-default TOML arm).
- Unknown TOML value → config rejected at load (serde unknown-variant
  error names both legal values).
- Validation: no bounds, no budget interaction (D8) — asserted, not
  assumed.

### `BehaviorConfig.contagion_aware_ladder` (new bool)

- Default `false`; `#[serde(default, skip_serializing_if =
  "bool_is_false")]` (new helper beside `f32_is_zero`).
- `false`/absent: every 045 chooser seam short-circuits before any
  exposure arithmetic — structurally byte-identical.
- No validation bounds.

## Derived (never stored)

### Contagion membership set (per tick, `advance_needs`)

- Existing: `wet_ids: BTreeSet<KittyId>` (cats on water), `contagious:
  BTreeSet<KittyId>` (dry cats admitted by own-naming + adjacency).
- 045 extension (bidirectional only): also admit dry cat `d` when some
  wet cat `w`'s `Activity::partner() == Some(d)` and
  `is_available_friend(w, d)`.
- Uniqueness: `BTreeSet` — a cat admitted by both roles, or referenced
  by several wet cats, is one member → exactly one charge per tick
  (FR-003 is structural).
- Lifecycle: rebuilt from scratch each tick from the activity snapshot;
  no carryover, no timer.

### Expected scene exposure (per decision, `behavior/selection.rs`)

```text
exposure(ctx, kind, partner) =
  Σ_{payer ∈ payers(membership, me, partner)}
      min( factor × bath_gain × bath_ratio(payer) × E_ticks(kind),
           max(0, bath_gain_ceiling − payer.bath) )
```

- `payers(option_a)`: `{me}` iff me dry ∧ partner wet (the namer is the
  decider).
- `payers(bidirectional)`: each dry member of the {me, partner} pair
  whose counterpart is wet (0, 1 members possible; never 2 — a pair has
  at most one dry-beside-wet member paying per counterpart... both-dry
  and both-wet yield ∅; one-wet-one-dry yields exactly the dry one).
- `E_ticks(kind)`: midpoint of the governing `[durations]`
  `DurationBounds` (D5 mapping).
- Units: bath need-points — subtracted directly from selection scores
  and candidate values (the score's existing currency).
- Consumed at the three gated seams (D6): `scored()` for
  Playmate/Friend relief, `play_score()` per candidate, the groom seam
  (decline when exposure > groomee's bath pressure).

## Invariants preserved

- Article I budget: per-cat per-tick worst case unchanged under either
  membership (one charge, same magnitude, same ceiling) — the 044
  headroom law stands verbatim.
- Article IV: exposure pricing changes what the built-in advisor
  *proposes*, never what is legal.
- Article V: no new RNG; BTree ordering; same-seed determinism asserted
  for both dials.
- Stamp/golden: both new fields skip at default; default world runs
  byte-identical.
