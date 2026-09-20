# Implementation Plan: Shallow ground sleep

**Branch**: `056-shallow-ground-sleep` | **Date**: 2026-09-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/056-shallow-ground-sleep/spec.md`

## Summary

One world law, one config key: off-beam sleep relieves the Sleep need only
down to `actions.sleep_floor_off_beam` (default 0 = today's law); on-beam
or conducted sleep (spec 031) clears to 0. The sleep scene's early-end
"finished" level becomes the lowest level the sleeper's current
circumstances can reach (owner-confirmed D1). Two engine touch points
(`apply_sleep_relief`, `resolve_activity_ends`) share one warmth
predicate so the rate choice and the floor escape can never drift.

## Technical Context

**Language/Version**: Rust (workspace toolchain pin, `rust-toolchain.toml`)

**Primary Dependencies**: existing workspace crates only — `cloudkitty-core` (law + config), `cloudkitty-server` (settings surface); no new dependencies

**Storage**: TOML config (`cloudkitty.toml` and test fixtures); no persistence change — the snapshot schema is untouched (needs are already stored values)

**Testing**: `cargo test` unit tests beside the code they guard; every new assertion red-proven via `scripts/mutate.sh --expect` (house rule 5)

**Target Platform**: the existing server/lab builds; no deploy rides this arc

**Project Type**: simulation engine world law

**Performance Goals**: none new — one f32 compare and one clamp per sleep tick

**Constraints**: default-0 must be step-for-step identical to today (FR-007); no wire, clock, RNG, or snapshot change; only `Activity::Sleeping` semantics move

**Scale/Scope**: ~5 files in core, 1 in server, 1 config comment, 1 changelog line

## Constitution Check

*GATE: evaluated pre-Phase 0; re-checked post-design — PASS both times.*

- **Article I (no suffering)**: needs stay bounded 0–100; the floor never
  raises a need, and a beam always relieves fully. Corrected at review
  (2026-09-20): safeguard spawning covers Eat and Drink only — beam
  supply is the world's element rules, not a spawned guarantee — and the
  `floor < [thresholds] distress` bound (configured value,
  owner-confirmed) prevents distress from being plain ground's *parked*
  state; the need still regrows between naps. Distress stays a signal,
  never a punishment (Article I's own framing), and the Article I
  property suite runs randomized configs over the new law.
- **Article II (no death)**: untouched.
- **Article III (never alone)**: untouched.
- **Article IV (engine is the law)**: the law lands in the engine's
  relief application; behaviors see only its outcomes. No proposal
  handling changes.
- **Article V (deterministic)**: no randomness added; the floor is a pure
  function of config and world state. Default-0 equivalence (FR-007) is
  the determinism claim's test.
- **Article VI (spec-first, constants in config)**: this spec precedes
  code; the floor is a documented config key with a default, never a
  magic number; every new claim is test-guarded with a mutation red.

No violations — Complexity Tracking not needed.

## Project Structure

### Documentation (this feature)

```text
specs/056-shallow-ground-sleep/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── config-key.md    # The key, its bounds, and its /settings row
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── config/mod.rs        # ActionsConfig: sleep_floor_off_beam field, serde default 0.0,
│                        #   doc comment; Default impl; unit test (absent = 0, bounds)
├── config/validate.rs   # finite/≥0 sweep row + cross-field bound: floor < [thresholds] distress
├── action.rs            # apply_sleep_relief: clamp off-beam relief at the floor;
│                        #   warmth predicate extracted so world.rs shares it;
│                        #   unit tests beside sleeping_in_a_sunbeam_is_more_restful
└── world.rs             # resolve_activity_ends: Sleeping's finished level =
                         #   reachable floor (shared predicate); end-tick tests

crates/cloudkitty-server/src/
└── settings.rs          # the key joins the spec-052 key-settings rows + its lists

cloudkitty.toml          # one comment line in [actions] beside sleep_relief*
CHANGELOG.md             # one-liner to ## Unreleased (public-voice at write time)
```

**Structure Decision**: existing crate layout; no new modules. The one
refactor is extracting the warmth circumstance (`in_sunbeam ||
partner_warm`, including the spec-041 `is_settled` mutual gate) into a
single `World` helper called by both `apply_sleep_relief` and
`resolve_activity_ends` — the spec's "one predicate, never two that can
drift" edge case, and rule 6's changed-behavior sort depends on it.

## Design notes (Phase 1 digest)

- **The clamp**: off-beam relief per tick becomes
  `amount = relief.min((need − floor).max(0))` — relieving by that amount
  clamps at the floor and leaves an already-under-floor need untouched,
  with no new write path (`lower_need` unchanged).
- **The finished level**: `resolve_activity_ends`' `need_zero` predicate
  gains a per-kitty finished level for `Activity::Sleeping`:
  `if warm { 0.0 } else { floor }`, compared with the existing `<=`. All
  other activities keep the literal 0. At floor 0 the predicate is
  byte-equal to today's, which is FR-007's cheap proof at this layer.
- **Duet sides**: the either-side rule is untouched; each side's finished
  level uses its own warmth. Within a mutual duet the levels agree
  whenever either partner stands on a beam (conduction covers the other),
  so the mixed-level case is transient only (wandered partner) — noted in
  the spec's edge cases.
- **Validation**: the floor joins the finite/≥0 `[actions]` sweep in
  `validate.rs`, plus one cross-field check against the configured
  `[thresholds] distress` (the sweep's rows are single-key; the bound needs the
  needs section, so it lands beside the other cross-field checks).
- **Settings**: one row in `settings.rs` (pattern: the
  `relief_memory_margin` rows at ~201/382/451 — value, default, and the
  two list registrations, each list already test-guarded).
- **Spec-050 precedent** for a defaulted dial: unit test proves absent =
  default = old rule and refuses out-of-range at parse/validate time
  (`relief_memory_margin_is_optional_and_refuses_a_negative_value`,
  config/mod.rs ~1976). Same shape here.

## Rule-5/6 test plan (the red ledger)

Changed behavior: sleep relief clamping and the sleep finished level.
Sort before running (rule 6):

- **Must go red then green (new guards, each via `scripts/mutate.sh --expect`)**:
  1. floor holds on plain ground (mutate: drop the clamp);
  2. beam clears to 0 under a floor (mutate: apply the clamp
     unconditionally);
  3. conducted clears to 0 under a floor (mutate: drop `partner_warm`
     from the escape);
  4. an under-floor need is never raised (mutate: clamp with
     `max(floor, …)` on the need itself instead of capping the amount);
  5. early-end fires at the reachable floor (mutate: keep finished = 0
     for sleeping);
  6. config bounds refused (mutate: drop the distress cross-check).
- **Must stay green (kept behavior)**: every existing sleep/cosleep test
  (they all run at floor 0 — they are the default-equivalence proof at
  the unit layer), `sleeping_in_a_sunbeam_is_more_restful`, the spec-031
  conduction tests, the spec-028 cosleep tier tests, the Article I
  property suite, both config sweeps, the settings lists' tests.

## Phase 1 artifacts

- research.md — decisions on type, default mechanics, validation home,
  equivalence proof shape (all resolved; no NEEDS CLARIFICATION).
- data-model.md — the floor, the warmth predicate, the finished level.
- contracts/config-key.md — the key's contract and /settings row.
- quickstart.md — build, targeted tests, mutation cycle, a floor-20 toml
  snippet to see the law by hand.
