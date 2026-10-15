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

(filled as each cycle runs; prediction written BEFORE the run)
