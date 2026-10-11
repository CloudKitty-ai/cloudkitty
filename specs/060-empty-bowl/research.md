# Phase 0 Research: Empty-Bowl Early End (spec 060)

Code survey run 2026-10-10 in this worktree (branch `product/empty-bowl`,
base 38a30d90) by an Explore subagent; every anchor below re-stated from
its report and verifiable in-tree. No NEEDS CLARIFICATION items remained
after `/speckit-clarify` (Q1 ruled A, 2026-10-10); the decisions here are
placements, not open questions — except R2, which is flagged to the
owner.

## R1 — The one home and the exact edit

**Decision**: amend the `done_naturally` condition in
`World::resolve_activity_ends` (`crates/cloudkitty-core/src/world.rs:736-740`):

```
// today
let done_naturally = elapsed >= bounds.min && (governed_done || out_of_chow);
// amended
let done_naturally = (elapsed >= bounds.min && governed_done) || out_of_chow;
```

**Rationale**: this function is where EVERY spec-006 end lives (rest,
sleep incl. the 056 floor, groom, play, drink, eat), called once per
tick at world.rs:425 after all apply slots and before the environment
phase — so the rule binds every seat and sees the bowl after everyone's
consumption this tick, settling turn-order questions with zero new
ordering rules (FR-001, Assumption 2). `out_of_chow` is already
computed and already `Activity::Eating`-only, so the edit moves one
pair of parentheses. The `elapsed >= bounds.max` cap and
`end_activity` routing are untouched (FR-002).

**Alternatives considered**: a separate early-end check in the apply
slot (rejected: would run before later eaters' slots, resurrecting the
turn-order question and splitting the one home); pruning via
`counterpart_gone_in` (rejected: that function deliberately returns
`false` for Eating — world.rs:1842-1843 — because the emptied bowl is
"the meal's own end rule"; spec 048 owns the vanished-element case,
FR-006).

## R2 — The feeding-condition predicate (⚠ flagged to the owner)

**Decision**: reuse `World::adjacent_stocked_chow` exactly as it
stands (world.rs:1424 → `adjacent_stocked_chow_in` 1905-1908):
nearest adjacent chow by `(manhattan, id)` within Manhattan ≤ 1
(own cell + 4 orthogonals, grid.rs:42-44), then filtered to
`servings > 0`.

**Rationale**: this is the predicate validate's Eat arm reads
(action.rs:397) AND the per-tick eat effect reads (action.rs:792-803).
If the effect's read returns None, the meal delivers no relief that
tick — so ending exactly when THIS predicate fails is the only choice
that makes SC-003 true (zero zero-relief eating ticks). Any broader
"some adjacent stocked bowl exists" end-check would hold a cat at a
meal the effect cannot feed. One predicate, four consumers (end rule,
validate, effect, HereFood grounding at meow.rs:241) stays the
property.

**The catch (owner should see this)**: the predicate is "the NEAREST
adjacent chow is stocked", not "SOME adjacent stocked chow exists".
The two differ only when ≥2 bowls sit within Manhattan 1 of one eater
and the nearer (or tied-with-lower-id) one is empty — a within-tick
window, since empty bowls are reaped the same tick's environment
phase. In that geometry the meal ends despite a stocked bowl in
reach, because the engine deliberately does not stretch across
(doc comment world.rs:1420-1423: "a cat at an empty bowl beside a
fuller one pauses (and then ends) rather than stretching across").
The clarify-Q1 ruling's letter ("the engine's own meal predicate is
the one home") supports this decision; its illustrative clause ("a
second stocked bowl within reach keeps the meal alive") holds in the
common case (the surviving bowl is the selected one) but not in the
nearest-empty geometry. Spec wording is adjusted at /speckit-analyze
remediation or on her word; the code decision is not sensitive to the
wording fix.

**Alternatives considered**: an any-adjacent-stocked end check
(rejected: ends and feeding disagree → zero-relief ticks survive,
SC-003 fails); re-ordering the shared predicate to prefer stocked
bowls (rejected: changes validate + effect semantics far beyond this
spec, and reverses a documented deliberate choice).

## R3 — The one-tick meal

A meal that starts on a bowl's last serving now ends the same tick:
span 1, exactly one serving of relief, minimum never engages. Already
ruled in the spec (Edge Cases, "A one-tick meal"). Today that meal
licks to `min`. `an_ended_scene_records_its_true_span_in_the_activity_log`
semantics unchanged (5 servings); the span-1 case gets its own guard.

## R4 — Changed-behavior test sort (CLAUDE.md rule 6)

**Must go red** (guards of the change):
- `an_emptied_bowl_pauses_below_the_minimum_and_ends_at_it`
  (world.rs:3718, `dinner_table(1)`): pins today's pause-to-minimum;
  under 060 the scene ends at the first `close_tick`. Rewrite as the
  early-end guard; its red is rule 5's red for FR-001.
- `announcing_food_and_eating_it_all_is_lawful` (action.rs:3542,
  1-serving bowl): check at implementation; if it asserts the
  post-drain hold, it moves.

**Must stay green** (kept behavior):
- `need_zero_before_the_minimum_waits_for_the_minimum` (world.rs:3699)
  — pins the exact clause 060 keeps (FR-002).
- `a_meal_runs_its_minimum_with_relief_every_tick` (3470),
  `a_finished_need_ends_the_meal_at_the_first_lawful_tick` (3548),
  `an_ended_scene_records_its_true_span_in_the_activity_log` (3435),
  `instant_bounds_reproduce_pre_006_pacing` (3751), the 056 sleep-end
  tests (3571-3672), `duration_enforcement_decides_the_absorbed_flag_never_the_refusal`
  (3273, pins FR-003's refusal/scene-end split),
  `eating_requires_nearby_chow` / `empty_chow_cannot_be_eaten` /
  `eating_consumes_one_serving_and_relieves_hunger` (action.rs 1103,
  1213, 1228), `a_crowded_out_kitty_is_fed_by_retarget_and_respawn_not_by_reaching_across`
  (welfare_longrun.rs:41).

## R5 — Stream pins and the divergence artifact (FR-005, US2)

Deterministic streams that eat from draining bowls move. Known pins:
- `fog_continuity.rs` fixtures (`prefog-*.digest`,
  `preladder-r5-*.digest`): re-record via the two `#[ignore]`d
  recorder mains (`record_prefog_streams` :441,
  `record_preladder_r5_streams` :547); append the justification
  paragraph in the file's re-record history (203-227, 476-505 — the
  059 entry at 220 is the pattern) with spec 060 named and
  first-divergence ticks captured BEFORE re-recording.
- `evolution_golden.rs` (:167, :235): the refusal-ring delta shifts if
  absorbed Eat rows disappear; verify and re-pin with the same
  declaration style if red.
- Sweep at implementation: snapshot_resume, joint_action_parity,
  roam_tether, consent_gate, waterline_contagion (core);
  run_json_golden, eval_suite, welfare_longrun, harness_policy,
  mixed_control, clock_and_range, artifact_v3_parity,
  vocabulary_flags (rl); test_reproducibility / test_parallel_env
  (py binding — NOTE: rebuild via `maturin develop` with VIRTUAL_ENV
  set; the scratchpad venv binding is stale).
- CHANGELOG Unreleased gains `[rng-sequence]` naming spec 060.
- The 0.3.0 served world is untouched: no config edits
  (shipped-config sweeps `every_shipped_toml_loads_through_validation`
  core :128 / rl :121 stay green for free — 060 adds no key).
- Stale prose: cloudkitty.toml:300-304 comment says "a finished need
  (or an empty bowl) ends the activity early once `min` is met". A
  comment edit in a shipped toml is a config-file touch; per the
  hook-review carve-out this is a RECORDING comment fix, stated on
  the PR. Decide at implementation whether to fold it in or report.

## R6 — Downstream readers (no edits owed)

- **Teacher/behavior**: `finish_what_you_started`
  (needs_driven.rs:64-86) proposes Eat on need alone; today that
  yields absorbed refusal rows over an empty bowl until `min`. Under
  060 the scene is gone by the next tick (no clock → no continuation
  proposal), so those rows vanish as a CONSEQUENCE — zero behavior
  edits (FR-006). Remaining absorbed Eat rows: same-tick emptying
  (earlier turn-order slot) and ttl-expired bowls.
- **RL mask**: `legal_action_mask` (mask.rs:50-72) replays
  prune/validate/enforcement — it moves with the engine
  automatically; the oracle self-checks against `apply_slot_verdict`.
  Today's mid-meal no-bowl case (Eat masked legal while the engine
  stamps an absorbed refusal) shrinks to the same-tick window.
- **Welfare/observe**: welfare.rs:67, observe.rs:530-540,
  global_state.rs:119-120 read world state only — untouched.

## R7 — Duration config facts

`DurationBounds { min, max }` (config/mod.rs:855-858), serde default
(2,5) (defaults.rs:139-141); shipped `eat = { min = 2, max = 3 }`
(cloudkitty.toml:305-307), training.toml min 2 max 5. Validation
`1 <= min <= max` (validate.rs:19-35). Mid-slot hold:
`duration_ruling` world.rs:576-582 (`serviced_before < bounds.min` →
Continue) — UNTOUCHED: the hold still absorbs mid-scene Idle
proposals; only the end-resolution clause moves. `elapsed` semantics:
`tick - started + 1` (kitty.rs:233).
