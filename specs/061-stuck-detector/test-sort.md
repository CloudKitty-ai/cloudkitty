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

## Review remediation record (2026-10-15)

An independent high-effort review (fresh subagent, scratch-clone staged
mutations) found no production defect and eight test-side findings; the
owner ruled "Remediate 1-8". What changed, and the new cycles (each
prediction written before its run; outcomes recorded below):

1. **RNG-blind byte-identity guards** (review staged an extra
   `ctx.rng.gen_u64()` on the forwarding path: GREEN — every wrapped
   fixture drew nothing). Both pairings now run `SamplingDither`, which
   draws one u64 per decision (the sampling policy-seat shape), so an
   added, dropped, or reordered draw diverges the worlds.
2. **`wrap_mind_seats` plugin arm untested** (review staged
   `is_mind_plugin && false`: GREEN). New lib.rs test drives
   wrap_mind_seats with a declared `class = "mind"` plugin, a scripted
   plugin, a policy seat, and a built-in; Arc identity asserts wrapped
   vs pass-through, set equality asserts the observer feed.
3. **Settings rows never asserted live values** (review rendered
   defaults in all five rows: GREEN). New settings test builds on a
   non-default StuckConfig and pins each row's live value AND default
   column. The boot line moved from main.rs into `stuck::log_boot`
   and gained a capture-rig contract test on non-default dials.
4. **Timed-out fire tick can log a false enforce record** (served,
   budgeted path only): not fixable here — the timeout lives in core's
   `decide_one` (FR-006 forbids the edit). Recorded as the third
   accepted served-path residual in plan.md Constraints, with the
   budget-cost note; a real fix needs a budget-aware decide seam
   (deferred distress intervention is the natural owner).
5. **Anchor orientation and armed values unpinned** (review swapped
   anchor x/y and zeroed ArmedRow: GREEN — diagonal fixtures,
   type-only asserts). The unit enforce test now pins
   `anchor == [2, 3]` (asymmetric), the integration fixture moved to
   (4, 7) and pins `[4, 7]`, and a new armed-surface test pins
   confined/streak/hottest-need values mid-window.
6. **Armed-line boundary unguarded** (review staged `>=` → `>`:
   GREEN — every fixture armed at 100). New boundary test sits a need
   exactly AT 75.0 (fires) and at 74.9 (never fires).
7. **Boxed-in test's message claimed a refused substitute** (false:
   the substitute brain checks occupancy at decision time, so a fully
   boxed seat gets Idle). Message fixed and the Idle substitute pinned;
   a NEW test constructs the genuine refusal — a same-tick tile
   contest the substitute loses on the turn-order draw (window 14
   pinned by consequence, the [rng-sequence] precedent; scan record:
   windows 6/14/20 refuse on this fixture) — and asserts the safe
   no-op resolution, `last_action == Idle`, and the record standing.
8. **FR-005 vacuity guard counted the playful seat too.** Narrowed to
   the needs_driven seat (kitty 1); the assert still sweeps every
   scripted seat.

| # | Mutation (production) | Predicted red | Outcome |
|---|---|---|---|
| 15 | StuckGuard `try_decide` forwarding arm gains `let _ = ctx.rng.gen_u64();` (the review's exact staged bug) | off-paired byte-identity: "an off detector changes nothing" (observe pairing reds too) | RED CONFIRMED |
| 16 | lib.rs `is_mind_plugin` gated `&& false` (the review's staged bug) | wrap test: "exactly the class = \"mind\" plugin feeds the observer's tracking rule" | RED CONFIRMED |
| 17 | settings mode row renders `sd.mode` (the default) | "stuck_detector.mode is the live value" | RED CONFIRMED |
| 18 | signature armed check `>=` → `>` | "exactly at the line arms (>=)" | RED CONFIRMED |
| 19 | fire record anchor `[x, y]` → `[y, x]` | "the anchor is the window-opening tile, [x, y]" | RED CONFIRMED |
| 20 | observer ArmedRow `confined` → `0` | "live trigger values after ten confined armed observations" | RED CONFIRMED |
| 21 | `fire()` drops `self.shared.record(record)` | refused-substitute test: "the refused fire is still on the record, once" | RED CONFIRMED |
| 22 | teacher decide stamps `Some(Mew)` (cycle 9 restaged under the narrowed vacuity guard) | FR-005 sweep: "a scripted brain spoke the free register" | RED CONFIRMED |
| 23 | `log_boot` drops the `radius` field | boot-line test: "the boot line renders the LIVE dial radius" | RED CONFIRMED |

## Contract §3 rendering correction (2026-10-15, post-merge)

Experiments' rule-3 report (verified): the §3 example block's VALUE
renderings never matched the shipped formatter — names held, shapes
did not (name was unquoted Display, armed_need Debug, actions render
with spaces and braces, empty messages bare, need_value full-precision
f64). While fixing the example the owner asked for spaced kitty names
to be handled: an unquoted spaced name (`name=Mr Whiskers tick=…`)
destroys the key=value boundary for every consumer. The fix quotes
`name` (Debug rendering) — the one deliberate rendering change, relayed
to Experiments before landing since their FR-011 reader (8bd65364)
parses the old shape.

Sorted checks, predictions written before any run:

- **Must fail (guards of the change)**: T010's `name=Biscuit` assert
  goes RED under the quoted rendering — predicted failure message
  "contract field name=Biscuit missing" — proving the old assert
  guarded the old rendering; it is then updated to `name="Biscuit"`.
  OUTCOME: RED as predicted, exact message, then updated and green.
- **Must pass (kept behavior)**: every other T010 field assert
  (levels, names, Idle shapes), the full server suite, byte-identity
  pairings (rendering is log-only; no decision path touched).

| # | Mutation (production) | Predicted red | Outcome |
|---|---|---|---|
| 24 | `log_fire` name reverts `?record.name` → `%record.name` (the unquoted rendering) | rendering test: "a spaced name stays one quoted token" | RED CONFIRMED |
| 25 | `substitute = %substitute` → `?substitute` (quotes the action) | rendering test: exact `substitute=Move { direction: East }` | RED CONFIRMED |
| 26 | `mode = "enforce"` → `mode = %"enforce"` (unquotes mode) | rendering test: `mode="enforce"` quoted | RED CONFIRMED |
