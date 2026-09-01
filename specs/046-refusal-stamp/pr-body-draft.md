# PR body draft: spec 046 — Refusal Stamp

Records every Article IV refusal — a non-Idle proposal `action::validate`
resolves to Idle — into a bounded ring on the `World`, each event carrying
the kitty, the proposal **verbatim** (targets included), the tick, and an
`absorbed` flag from the enforcement outcome (Experiments ruling (b),
2026-09-01: `absorbed == false` rows are the taxed ticks; census
definition quoted in the spec). Ring sized by `[events] refusal_retention`
(default 4,000 — a floor on taxed density), served at
`GET /events/refusal`, recorded once in the shared apply pipeline so both
tick drivers stamp identical streams.

Additive delivery proven:

- Dynamics byte-identical: the 10k-tick evolution digest with the new
  `refusal_log` key stripped equals the 041 pin exactly (RNG and all
  sibling state included); golden regenerated per its own doctrine with
  the witness recorded in `specs/046-refusal-stamp/redden-list.md`.
- `engine_defaults_sha256` unmoved (skip-at-default, guard test).
- Pre-046 saves resume: `persist::load_and_validate` re-stamps the ring's
  capacity from config (retention is configuration, the behavior
  re-stamp doctrine).
- 13 red-first cycles + live emit-proof payload in `redden-list.md`.
  Suite 774 → 787, nothing lost.

## Reported, not fixed (CLAUDE.md rule 3)

**Sibling-ring capacity gap**: `EventLog` serializes its `capacity`, and
nothing re-sizes the **distress** or **activity** rings on load — an
operator's retention edit for those rings silently loses to the capacity
persisted in the world save on every resume. Pre-046 worlds have never
hit it (those retentions have never been edited mid-life). The 046 ring
gets the load-time re-stamp; extending it to the siblings is a separate
small change if wanted.

## Spec-artifact deviations (recorded during implement)

- T018 lives in `persist.rs` tests, not `core/tests/snapshot_resume.rs`:
  core tests cannot import the server crate (dependency direction).
- T020's "golden passes unregenerated" was unsatisfiable as written for
  an additive world field; replaced by the strip-witness proof above.
  SC-003 (byte-identical kitty traces) holds — the witness proves more.
- Contract examples updated to the REAL wire tag (`"action"`, not the
  provisional `"kind"`), pinned by the emit-proof test.
