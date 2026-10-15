# Spec 061 test sort (CLAUDE.md rule 6)

Started at T005 (first cut, before the suites were treated as
evidence); extended as each phase lands; finalized at T017.

## Changed behaviour (new feature): guards that MUST go red

Every assertion below is new; its red is staged through
`scripts/mutate.sh --expect <prediction>` against the committed
module. The cycle table at the bottom records each run.

| Guard | Staged bug (production mutation) | Predicted red |
|---|---|---|
| flicker pauses (T005) | any scene tick clears every streak (the rejected strict gate) | `a_scene_flicker...` expects fire at 31, strict gives 41 |
| pacer parity + refire gap (T005/FR-007) | delete the post-fire reset | parity expects `200/window` fires, unreset fires every tick from the first completion |
| enforce substitutes (T007/T009) | enforce arm returns the inner decision | `dispatch uses the scripted substitute` |
| plan targets next tick (T006/C2) | plan stamped `world.tick + 1` | exact-tick equality / plan-target assert |
| observe is inert (T014/FR-008) | observe arm returns the substitute | observe byte-identity vs plain world |
| mind rule bounds tracking (T016/FR-003) | `is_mind` matches every behavior | scripted seat appears in status |
| attribution intact (SC-003) | `confined_span` recorded as 0 | `confined_span >= window` |
| config validation (T004) | `validate` accepts `window = 1` | invalid-values test names `window` |
| FR-005 silence sweep (T009) | teacher decide stamps a free-register message | the sweep names the kind |
| /stuck surface (T011/T013) | staged after wiring — see additions below | |
| settings keys pinned (T012) | staged after wiring | |
| determinism (T015) | staged after the suite exists | |

## Kept behaviour: MUST stay green (read, not only run)

- The whole existing workspace suite: no engine rule, tick order, or
  serving surface this feature touches may change behavior — the only
  production edits outside the new module are (a) the core config
  foreign-table passthrough (guarded by `the_foreign_tables_never_
  serialize`, which itself gets a red cycle on `skip_serializing`),
  (b) `sim_task::spawn` and `settings::build` signature threading
  (their existing tests updated mechanically, assertions untouched),
  (c) registry wrapping in `lib.rs` (off-mode byte-identity is the
  guard that wrapping alone changes nothing).
- `watchdog.rs` suite: untouched file, must stay green as-is.
- `determinism.rs` (core): untouched; the detector adds no RNG draw on
  any path core tests exercise.
- Read-check: the off-mode byte-identity test is the one place "kept
  behaviour" is asserted for wrapped seats; it pairs a wrapped-off
  registry against a bare one over 2000 ticks, so a wrapper that so
  much as reorders an RNG draw goes red there.

## Cycle record

(prediction written before each run; all via `scripts/mutate.sh --expect`)

| # | Mutation (production) | Predicted red | Outcome |
|---|---|---|---|
| 1 | scene branch `if relief == Some(kind)` → `if true` (strict gate) | flicker test: "the flicker pauses, never resets" | RED CONFIRMED, restore green |
| 2 | post-fire reset deleted | pacer parity: "fires every full window" | RED CONFIRMED (fires every tick past the first completion) |
| 3 | `Enforce => Some(substitute)` → `=> inner` | "dispatch uses the scripted substitute" | RED CONFIRMED |
| 4 | plan `target_tick: world.tick` → `+ 1` | "post-tick stamp IS the next" (exact-tick equality) | RED CONFIRMED (first run exit 7: my --expect regex miscounted the apostrophe; same assertion, regex fixed, re-run clean) |
| 5 | `Observe => inner` → `=> Some(substitute)` | observe byte-identity: "observe substitutes nothing" | RED CONFIRMED |
| 6 | `is_mind` → `!behavior.is_empty()` | scripted invisibility: "no seat row" | RED CONFIRMED |
| 7 | record `confined_span` → `0` | "confined_span >= window" | RED CONFIRMED |
| 8 | `validate` window bound `< 2` → `< 1` | invalid-values: "must fail at load" | RED CONFIRMED |
| 9 | teacher.rs decide stamps `Some(Mew)` | FR-005 sweep: "a scripted brain spoke the free register" | RED CONFIRMED |
| 10 | core config: ForeignTable given a Serialize impl + `skip_serializing` dropped | leak test: "stuck_detector leaked into serialization" | RED CONFIRMED (note: the bare attribute-drop is a compile error — ForeignTable has no Serialize — so the leak is type-blocked twice over; the mutation had to add the impl to even reach the test) |
| 11 | settings row key `radius` → `confinement_radius` | pinned golden: "the key settings list moved" | RED CONFIRMED |
| 12 | observer serves `armed: Vec::new()` | /stuck integration: "live trigger row" | RED CONFIRMED |
| 13 | fire record tick += wall-clock nanos % 97 | determinism replay: "fire sequence is identical" | RED CONFIRMED |
| 14 | observe-mode log line at WARN | log-line contract test: "observe-only record logs at INFO" | RED CONFIRMED |

## Notes and honest substitutions

- The planned "mutate world-visible state in the observe path" red
  (T014) is TYPE-IMPOSSIBLE: the observer takes `&World` and the
  wrapper returns a `Decision` — there is no mutable path to stage.
  Cycle 5 (observe returns the substitute) is the strongest reachable
  bug in that class and reddens the same byte-identity guard.
- Exact-fire-tick conventions, both pinned as equalities: unit/
  budgetless harness (first observe after the first tick) fires at
  decision tick == window; the served path (spawn-time observe steps
  the signature once at world.tick 0) fires at window − 1 on a fresh
  world. The integration test documents the served convention in
  place.
- Kept pile read AND run: full workspace suite at T019 = **82 suites,
  1041 tests, 0 failures** (the 060 close recorded 1019 — the 22 new
  are this spec's); the signature-threading edits (sim_task::spawn,
  settings::build, AppState) changed arities only — every pre-existing
  assertion is untouched, verified by reading the diffs. One
  pre-existing assertion WAS updated, deliberately: the settings
  entry-count golden (21 → 26, the five new [stuck_detector] rows),
  which is that test doing its job.
- T019 anchor: the committed `stuck_rule_replay.py` re-run from the
  native checkout post-implementation reproduces the verification
  table under both `--relief` rules, and the regenerated
  `stuck-rule-fires.json` is byte-identical to the committed dump.
- wrap_mind_seats REBUILDS the registry (register panics on duplicate
  names — the uniqueness law found by the first integration run; the
  lib.rs shadow-check comment I initially read as last-write-wins is
  the opposite: a backstop panic).
