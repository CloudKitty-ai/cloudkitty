# Data Model: Config Restructure (spec 020)

No serialized, configured, or externally visible data changes (FR-005/
FR-009). This file records the module layout, the table-row shape, and
the spec-contract call sequence.

## Module layout (`crates/cloudkitty-core/src/config/`)

| File | Contents | Notes |
|---|---|---|
| `mod.rs` | all config structs + `ConfigError` + `validate()` entry + `#[cfg(test)]` module | types are the module's primary content (FR-003); tests byte-untouched (FR-007); serde attrs become `default = "defaults::…"` |
| `defaults.rs` | the ~20 `default_*` free fns | bodies unchanged; `pub(super)` |
| `validate.rs` | all section validators + table-row loops | `pub(super)`; every message string verbatim from baseline |

Public surface: `crate::config::*` and root re-exports unchanged — no
consumer edit anywhere (FR-006, SC-004).

## The table-row shape (D2)

Per-cluster arrays of `(field: &str, value: String, expected: &str)`
(or the cluster's existing shared-message form where the baseline
already shares one string). Rows carry the **exact** baseline message,
rationale parentheticals included. Adding a bounded field = one row
(US1); no message generation exists anywhere.

## Section validators and the documented call sequence (D3, amended FR-004)

`validate()` calls, in this order — the spec-contract sequence; future
reordering is a spec change, not a refactor:

1. `validate_world`
2. `validate_roster`
3. `validate_thresholds`
4. `validate_happiness`
5. `validate_needs`
6. `validate_elements`
7. `validate_behavior` *(now `[behavior]` only)*
8. `validate_purr` *(new home for the two `[purr]` checks)*
9. `validate_actions` *(new — `[actions]` rules from the catch-all)*
10. `validate_viewer` *(new)*
11. `validate_events` *(new)*
12. `validate_persistence` *(new)*
13. `validate_durations`
14. `validate_capacity`

Positions 1–7 and 13–14 are today's entry order verbatim (baseline
config.rs:777–788); positions 7–12 expand the old catch-all in its slot
by its internal first-occurrence order. The 8–12 tail order
(purr → actions → viewer → events → persistence) is confirmed against
the baseline catch-all during implementation and corrected here if the
file says otherwise — the *rule* is "the catch-all's first-occurrence
order," the listing is its expected expansion. Within every validator,
today's field order is preserved exactly.

## Invariants

- Every rejection path's message: byte-identical (single-fault absolute;
  multi-fault per the amended FR-004 — within-section order exact,
  cross-section per the sequence above).
- No validator touches fields outside its named section (SC-002); the
  170-line catch-all no longer exists.
- Serde: accepted shapes, omitted-field defaults, unknown-field
  handling, section names — all untouched (FR-005).
- The `#[cfg(test)]` module's content is byte-unmodified (FR-007); it
  merely lives in `mod.rs` after the split.
