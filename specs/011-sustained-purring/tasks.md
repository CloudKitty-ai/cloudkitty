# Tasks: Sustained Purring

**Input**: Design documents from `/specs/011-sustained-purring/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/purr-contract.md, quickstart.md

**Tests**: included (Article VI; the rhythm is the observable contract).

**Organization**: US1 (background purr) is the engine phase + retired
action; US2 (one meow + visible state) rides the same phase plus the viewer
cue; US3 (saved/replayed) is compatibility + determinism verification.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 Confirm branch baseline green (`cargo test --workspace`, HEAD
      `d614a22`)

## Phase 2: Foundational

- [X] T002 In `crates/cloudkitty-core/src/config.rs`: add `PurrConfig`
      (`min_ticks` 6 / `max_ticks` 15 / `cooldown_ticks` 30) as
      `#[serde(default)] pub purr: PurrConfig` with per-field defaults, the
      `Default` impl, and validation (`1 ≤ min_ticks ≤ max_ticks`, standard
      naming-the-field errors) (plan R6)
- [X] T003 In `crates/cloudkitty-core/src/config.rs` tests: absent-table
      default, `min_ticks = 0` rejected, `min_ticks > max_ticks` rejected
- [X] T004 [P] Document the `[purr]` section (contract wording) in
      `cloudkitty.toml`, `cloudkitty16.toml`, `cloudkitty48.toml`; reconcile
      spec.md FR-004's tunable spelling to the table form (Article VI)
- [X] T005 In `crates/cloudkitty-core/src/kitty.rs`: add `purring_until:
      Option<u64>` (`skip_serializing_if` none) and `purr_cooldown_until:
      u64`, both `#[serde(default)]`, initialized quiet in `Kitty::new`;
      confirm the old-JSON fixture test still deserializes (proves FR-007
      compat) (plan R2)

## Phase 3: User Story 1 — The purr runs in the background (P1) 🎯 MVP

- [X] T006 [US1] In `crates/cloudkitty-core/src/world.rs`: add `purr_phase`
      called right after `advance_needs`/`record_distress` in the tick —
      stable kitty-id order; end due purrs (stamp cooldown), then start
      earned off-cooldown purrs with one world-RNG draw
      `min + gen_range(0, max−min+1)` and record the purr meow directly
      (push + cooldown stamp, bypassing the proposal gate) (plan R1/R3/R4)
- [X] T007 [US1] In `crates/cloudkitty-core/src/action.rs`: Purr validation
      arm → unconditionally illegal (doc comment: variant retained for
      pre-011 `last_action` wire compat, plan R5); apply arm → documented
      no-op; rewrite `purring_must_be_earned` as
      `purring_is_no_longer_an_action`
- [X] T008 [US1] Delete the purr-proposal blocks from
      `crates/cloudkitty-core/src/behavior/needs_driven.rs` and
      `crates/cloudkitty-core/src/behavior/playful.rs`
- [X] T009 [US1] In `crates/cloudkitty-core/src/world.rs` tests: the phase
      unit tests — earned start (duration in bounds, exactly one purr meow
      stamped that tick), cooldown respected while earned, scheduled end
      stamps `purr_cooldown_until`, and a purring kitty beside chow with
      high eat pressure begins Eating while `purring_until` stays set (the
      action slot is provably free)

## Phase 4: User Story 2 — One meow per rumble, and a visible purr (P2)

- [X] T010 [US2] In `client/app.js`: append ` · purring 💕` to the card's
      doing-line when `kitty.purring_until != null` (keep the old `'purr'`
      last_action case for restored frames); no other client changes
- [X] T011 [US2] In `crates/cloudkitty-core/tests/welfare_longrun.rs`: the
      purr-rhythm property run (plan R7.4) — 2,000 default-config ticks
      tracking transitions per kitty: every duration within
      `[min_ticks, max_ticks]`, consecutive purrs separated by ≥
      `cooldown_ticks`, exactly one purr meow per start (and none
      mid-purr), at least one purr observed

## Phase 5: User Story 3 — Saved, replayed, identical (P3)

- [X] T012 [US3] Full suite: `cargo test --workspace` — 5k-tick replay and
      save/restore determinism now cover the purr draw and state; welfare
      bounds and 009/010 guards stay green

## Phase 6: Polish & Cross-Cutting

- [X] T013 Gates: clippy `-D warnings`, `cargo fmt --check`,
      `node client/test-meadow.mjs`
- [X] T014 Demo: rebuild + relaunch the throwaway world on `:8093`; confirm
      `/kitties` serves `purring_until` and the card cue reads
      `· purring 💕`

## Dependencies & Execution Order

```text
T001 → T002 → T003, T004 [P], T005
     → US1: T006 → T007, T008 [P] → T009
     → US2: T010 [P] with T011
     → US3: T012 → T013 → T014
```

## Implementation Strategy

**MVP = through T009**: purring is sustained, background, engine-owned.
US2 makes it audible-once and visible; US3 certifies replay. One commit on
the shared batch branch when green.

## Implementation notes (2026-07-20, all tasks complete)

- **Spec FR-004 reconciled** in the same change (Article VI): the three
  tunables are spelled as the `[purr]` table (`min_ticks`, `max_ticks`,
  `cooldown_ticks`) rather than the draft's `purr_*_ticks` flat keys —
  same names, table form, whole-table serde default for the strongest
  zero-edit compatibility.
- **`Action::Purr` variant retained deliberately** (plan R5): serialized
  `last_action` in pre-011 snapshots may contain `"purr"`, so the variant
  must stay deserializable; validation refuses it unconditionally and the
  apply arm is a documented no-op. `validate`'s `config` parameter became
  `_config` (the retired Purr arm was its last consumer) — kept in the
  signature so Article IV's surface doesn't churn with individual rules.
- **The start meow bypasses the proposal cooldown gate** (plan R4),
  recorded directly with the cooldown stamped — exactly one meow per purr
  even under a zero purr-cooldown.
- **Verification evidence**: 220 lib tests + all integration suites green
  first run — purr-phase units (bounded draw, one meow, cooldown holds,
  scheduled end, a purring kitty still eats), the 2,000-tick purr-rhythm
  property run, 20k welfare bounds, 5k replay, meadow harness, clippy,
  fmt. Demo world on :8093 serves `[purr]` config and live
  `purring_until` state; the card line reads `· purring 💕` mid-activity.
