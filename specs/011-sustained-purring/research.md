# Research: Sustained Purring

**Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Seven decisions (R1–R7), grounded in the tick loop (fixed phase order,
Article V), the serialized `Kitty` shape (notably: `last_action:
Option<Action>` rides in snapshots), the meow machinery (`emit_meow` is
cooldown-gated), and the two behaviors' existing purr-proposal blocks.

## R1 — The engine owns the purr; behaviors lose the code entirely

**Decision**: purr start/end/cooldown live in a new `purr_phase` on `World`,
run inside the tick immediately after `advance_needs`/`record_distress`
(happiness and `happiness_rose` are freshest there), iterating kitties in
stable id order. The purr-proposal blocks in `needs_driven` and `playful`
are deleted outright.

**Rationale**: FR-001/FR-002 — "the world starts purrs itself; behaviors do
not propose them" is the spec verbatim, and an engine phase is the only home
that can guarantee "never occupies the action slot". Running after needs
settle means a purr can begin the very tick happiness crosses the line.

**Alternatives considered**: a behavior-side "purr intent" channel (a second
proposal surface for a thing behaviors may not control — Article IV noise);
piggybacking on `apply` (ties purring to whether a kitty acted).

## R2 — Two fields on `Kitty`, absolute ticks, serde-defaulted

**Decision**: `purring_until: Option<u64>` (Some(end) while purring;
`skip_serializing_if` none) and `purr_cooldown_until: u64` (default 0).
Both `#[serde(default)]`: pre-011 snapshots load quiet and immediately
eligible (FR-007), proven by the existing old-JSON kitty fixture test.

**Rationale**: absolute end-ticks are the established idiom
(`abandoned_chases.until`, meow cooldowns) — resume-safe with no per-tick
bookkeeping; `Option` doubles as the served "is purring" signal, so the
viewer needs no derived field.

**Alternatives considered**: remaining-tick counters (must be decremented —
busywork and a resume hazard); a nested `PurrState` struct (two scalars do
not need a struct's ceremony).

## R3 — Duration drawn at start, runs to completion

**Decision**: at purr start, one draw from the world RNG:
`min_ticks + gen_range(0, max−min+1)` — a draw even when min == max, so
config cannot change the draw *count* (the determinism-shape rule spawn
already follows). The purr then runs its full drawn duration; nothing ends
it early — the earned rule gates starting only (spec Assumption, verbatim).

**Rationale**: FR-003 and Article V; a fixed draw-count keeps replay
alignment across config tweaks of the same world.

**Alternatives considered**: early end on happiness drop (rejected in the
spec — purrs have momentum, and Article I's floor means no kitty is ever
miserable while rumbling); per-kitty RNG (the decision RNGs belong to
behaviors; this is engine state, so the world RNG is the lawful source).

## R4 — The start meow bypasses the proposal cooldown gate

**Decision**: the purr meow is recorded directly at purr start (push to
`recent_meows` + stamp the kitty's Purr cooldown), *not* through
cooldown-gated `emit_meow`. Exactly one meow per purr, by construction.

**Rationale**: FR-005 says exactly once per purr — including back-to-back
purrs under a zero cooldown (spec edge case), which the 15-tick meow
cooldown would silently swallow. A state announcement is not a proposal;
the cooldown gate exists to stop *proposal* spam, and the purr cooldown
itself now bounds the announcement rate. Stamping the cooldown keeps every
other meow rule untouched.

**Alternatives considered**: routing through `emit_meow` (silently violates
exactly-once under legal configs); not stamping the cooldown (would let a
hypothetical future purr-adjacent message fire immediately after — stamping
preserves today's observable cadence).

## R5 — `Action::Purr` retires but the variant stays

**Decision**: validation's Purr arm becomes unconditionally illegal
(resolves to Idle); the apply arm becomes a documented no-op; the enum
variant itself **stays**. Behaviors no longer construct it anywhere.

**Rationale**: `last_action: Option<Action>` is serialized in snapshots — a
pre-011 save whose kitty last purred contains `"last_action": "purr"`, and
deleting the variant would break FR-007's "old snapshots load cleanly" at
the deserializer. Keeping the variant with validation closed is the
smallest honest wire posture (and FR-006's "stale or external purr proposal
resolves to idle" falls out of it directly).

**Alternatives considered**: deleting the variant (breaks old-save loading
on the `last_action` field); a serde alias/migration shim (machinery to
avoid one documented arm).

## R6 — Config: a `[purr]` table, whole-table defaulted

**Decision**: `PurrConfig { min_ticks: 6, max_ticks: 15, cooldown_ticks: 30 }`
as `#[serde(default)] pub purr: PurrConfig` — the entire section may be
absent (every pre-011 config runs unedited), and each field also defaults
individually. Validation: `1 ≤ min_ticks ≤ max_ticks`, standard
naming-the-field errors. Documented `[purr]` section added to the three
shipped worlds. Spec FR-004's `purr_min_ticks`-style names are reconciled
to this table spelling in the same change (Article VI: spec and code agree).
Defaults read right at the 800 ms watching pace: rumbles of ~5–12 s,
~24 s of rest.

**Rationale**: three related tunables are exactly what a table is for, and
whole-table defaulting is the strongest zero-edit compatibility shape.

**Alternatives considered**: three loose keys under `[behavior]` (purring is
engine state now, not behavior preference); under `[thresholds]` (those are
shared trigger lines, not timings).

## R7 — Verification: rhythm as a property, plumbing as units

**Decision**: (1) `world.rs` unit tests for the phase — an earned kitty off
cooldown starts purring with a duration in bounds and exactly one purr meow
stamped that tick; a purr ends on schedule and stamps the cooldown; an
earned kitty inside its cooldown stays quiet; a purring kitty still eats
(the action slot is provably free). (2) `config.rs` tests — absent table
defaults, `min_ticks = 0` and `min > max` rejected naming the field.
(3) `action.rs` — the old `purring_must_be_earned` test becomes
`purring_is_no_longer_an_action` (always Idle). (4) A purr-rhythm run in
`welfare_longrun.rs`: 2,000 default-config ticks tracking every transition —
each purr's duration within `[min, max]`, consecutive purrs separated by at
least the cooldown, exactly one purr meow per start, at least one purr
observed (the default world is a happy one). (5) The full suite (welfare
bounds, 5k replay, save/restore) re-run. (6) Viewer cue checked live on the
demo world.

**Rationale**: the rhythm is the feature's observable contract (SC-002);
the existing determinism suites already re-verify Article V once the state
serializes.

**Alternatives considered**: asserting purr timing inside the 20k welfare
run (mixes concerns; a dedicated bounded run reads and fails clearer).
