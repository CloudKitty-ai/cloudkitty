# Implementation Plan: Refusal Stamp

**Branch**: `046-refusal-stamp` | **Date**: 2026-09-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/046-refusal-stamp/spec.md`

## Summary

Record every Article IV refusal — a non-Idle proposal resolved to Idle
by `action::validate` — into a new bounded ring on the `World`, each
event carrying an `absorbed` flag from the enforcement outcome
(Experiments ruling 2026-09-01: `absorbed == false` rows are the taxed
ticks F-033 compares against; absorbed rows are proposal-quality
evidence). Ring sized by a new `[events] refusal_retention` knob
(default 4,000), served at `/events/refusal`. One recording site in the
shared apply pipeline covers both tick drivers. Zero dynamics change;
config stamp and evolution golden must not move.

## Technical Context

**Language/Version**: Rust (workspace toolchain pinned by
`rust-toolchain.toml`, spec #305)

**Primary Dependencies**: existing workspace only — serde/serde_json,
axum (server routes). No new crates (CLAUDE.md rule 2).

**Storage**: the persisted world save (`persist.rs` serializes the whole
`World`); the ring rides it as an additive serde-default field.

**Testing**: cargo test; CI's exact clippy invocation
(`cargo clippy --workspace --all-targets -- -D warnings`) before push
(lesson from PR #336).

**Target Platform**: server binary (`cloudkitty-server`) + core library;
no client work.

**Performance Goals**: recording is one branch + one ring push per
refused kitty per tick — negligible. Serving/persisting a 4,000-event
ring: see research R4 (~360 KB worst-case JSON, acceptable at the
persist and poll cadences).

**Constraints**: byte-identical dynamics (SC-003, evolution golden);
`engine_defaults_sha256` stamp unmoved (SC-004); pre-046 saves resume
(FR-006); RL mask/observation surface untouched (US3-4).

**Scale/Scope**: ~0.23 refusals/tick on the 5-seat roster; ring default
4,000 ≈ ≥15k-tick window.

## Constitution Check

- **Article I (no suffering)**: PASS — the stamp is a signal, recorded
  and never read by the engine; nothing makes a kitty's life worse.
  Mirrors the distress-log precedent verbatim.
- **Article II (no death)**: PASS — no lifecycle change.
- **Article III (not alone)**: PASS — no social mechanic change.
- **Article IV (engine is the law)**: PASS — the stamp *reports* the
  enforcement surface; it does not alter proposal resolution. The
  recording predicate reads `validate`'s output, never re-derives
  legality.
- **Article V (server-authoritative, deterministic)**: PASS — recording
  happens inside the deterministic apply loop in turn order; the ring is
  world state that round-trips saves; the client computes nothing.
- **Article VI (spec-first, test-guarded)**: this plan; red-first per
  CLAUDE.md rules 5/6 with cycles recorded in `redden-list.md`.

Post-design re-check: unchanged, all PASS.

## Project Structure

```
crates/cloudkitty-core/src/
  events.rs            # RefusalEvent, RefusalLog, EventLog::set_capacity
  world.rs             # refusal_log field (serde-default), recording site
  config/mod.rs        # EventsConfig.refusal_retention + skip helper
  config/defaults.rs   # default_refusal_retention() = 4000
  config/validate.rs   # nonzero row (spec 020 D2 shape)
crates/cloudkitty-server/src/
  persist.rs           # capacity re-stamp on load (research R3)
  sim_task.rs          # refusals in the served state
  api.rs               # get_refusals
  lib.rs               # route /events/refusal
crates/cloudkitty-core/tests/
  snapshot_resume.rs   # pre-046 save resume + capacity re-stamp
  (unit tests live beside their modules, house style)
specs/046-refusal-stamp/
  redden-list.md       # red-first cycle record
```

## Design Decisions (Phase 0 output: research.md)

R1–R6 in [research.md](research.md). Headlines:

- **R1 recording site**: inside `run_applied_phases_from_decisions`'s
  per-kitty loop, after `enforce_durations` — predicate
  `proposal != Action::Idle && validated == Action::Idle`, with
  `absorbed = (enforced != Action::Idle)`. Both tick drivers call this
  one pipeline (`world.rs:183`, `seam.rs:271`), so FR-002 is
  structural.
- **R2 stamp discipline**: `refusal_retention` gets
  `#[serde(default = "default_refusal_retention", skip_serializing_if = "is_default_refusal_retention")]`
  keyed to the default *value* (043/045 precedent), plus a line in
  `roam_cell_stays_out_of_the_default_serialization`.
- **R3 capacity re-stamp on load**: `EventLog` serializes its capacity,
  and a pre-046 save deserializes the new field to capacity 0 (ring of
  one) — permanently, since nothing re-sizes it. Retention is
  *configuration*, not world state (the behavior re-stamp precedent in
  `persist.rs`), so `load_and_validate` re-stamps the refusal ring's
  capacity from config. Without this the deployed box — which resumes,
  never regenerates — would break the census the feature exists for.
  Sibling rings have the same latent gap; reported, not fixed (rule 3).
- **R4 sizing**: ~90 bytes/event serialized → ≤ ~360 KB ring, additive
  to a save already carrying the 1000-event activity and distress rings;
  poll payload same order. Acceptable; no endpoint pagination.
- **R5 event shape**: `RefusalEvent { kitty_id, proposed: Action, tick, absorbed }`
  — the proposal verbatim (targets ride free), the flag always
  serialized. No reason code, no
  validated/applied copy (KittyTickRecord already carries those for seam
  consumers).
- **R6 no gate**: recording is unconditional; the only knob is
  retention. No boot line (nothing is armed or off).

## Phase 1 artifacts

- [data-model.md](data-model.md) — entities, fields, validation,
  serialization rules.
- [contracts/refusal-event.md](contracts/refusal-event.md) — wire shape
  of the event and endpoint.
- [quickstart.md](quickstart.md) — end-to-end validation runbook.

## Complexity Tracking

No constitution deviations; no new dependencies; one deliberate
scope-shaped decision (R3's load-time re-stamp touches `persist.rs`,
justified above and confined to the new ring).
