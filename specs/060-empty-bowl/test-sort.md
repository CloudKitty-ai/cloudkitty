# Spec 060 rule-6 test sort (T002/T003)

Sorted 2026-10-12 at branch e16da92d, BEFORE the engine edit. Baseline:
`cargo test --workspace` 1017 passed / 0 failed / clean tree (T001).
Every body below was READ, not just run. `elapsed = tick - started + 1`;
test config eat bounds min 2 (interrupt lawful on the 3rd tick).

## Must flip (guards of the change — red before T007, green after)

| Test | Pre-edit prediction |
|---|---|
| `an_emptied_bowl_pauses_below_the_minimum_and_ends_at_it` (world.rs:3718) | REWRITTEN as `an_emptied_bowl_ends_the_meal_below_the_minimum`: asserts end at the FIRST resolution (activity Idle, clock None, span 1, exactly one serving's relief, freed kitty's Move applies next tick). On the unamended engine the first `close_tick` leaves the scene live (elapsed 1 < min 2 gates the old condition), so the `activity == Idle` assert fails with `Eating`. Covers acceptance scenario 1 + the one-tick-meal edge case (T005 a+d — `dinner_table(1)` IS the start-on-last-serving meal). |
| NEW `a_shared_bowl_emptying_ends_every_meal_at_it` (T005 b, scenario 4) | Two eaters, one bowl, servings 2, both start tick 100, both consume in their slots; resolution finds servings 0 → BOTH end, span 1 each, regardless of slot order. Pre-edit: both continue (below min) → `activity == Idle` asserts fail with `Eating`. |
| NEW `a_meal_never_stretches_across_to_a_farther_bowl` (T005 c, scenario 5 end case + id tie) | Bowl underfoot (d0) drains beside a stocked d1 bowl → predicate None → end below min; same for two d1 bowls where the lower-id one drains (tie-break reads the empty one). Pre-edit: scenes continue → `Idle` asserts fail with `Eating`. |
| NEW `a_vanished_bowl_ends_the_meal_at_the_next_resolution` (T005 e) | Mid-meal bowl removed (the env-phase ttl/despawn pathway, applied directly — close_tick does not run the environment phase); next resolution: predicate None → end below min, and the Idle-proposal continuation records NO refusal row. Pre-edit: paused meal continues to min → `Idle` assert fails with `Eating`. |
| NEW FR-003 assertions inside the above (T006) | Early end writes exactly one activity_log end record and refusal_log stays EMPTY. Pre-edit the log-record asserts fail (no end has happened yet) — red for the right reason alongside the state asserts. |

## Must stay green (kept behavior — read and re-run, not weakened)

- `need_zero_before_the_minimum_waits_for_the_minimum` (world.rs:3699)
  — pins the exact clause 060 keeps (FR-002). Asserts clock LIVE after
  tick 1 (need 0, bowl stocked at 5 servings), end at min.
- `a_meal_runs_its_minimum_with_relief_every_tick` (3470) — 5 servings;
  mid-min Move superseded; relief every tick.
- `a_finished_need_ends_the_meal_at_the_first_lawful_tick` (3548) —
  min-met + need-0 end, 5 servings.
- `an_ended_scene_records_its_true_span_in_the_activity_log` (3435) —
  3-tick meal, 5 servings; span accounting unchanged.
- `instant_bounds_reproduce_pre_006_pacing` (3751) — min=max=1.
- `re_proposing_sleep_never_resets_the_clock_and_the_cap_holds` (3511),
  `a_ground_nap_ends_at_the_reachable_floor` (3571),
  `a_floor_zero_nap_ends_exactly_as_today` (3600),
  `the_floor_never_leaks_onto_a_groomed_sleepers_bath` (3630),
  `a_nap_begun_at_the_floor_ends_at_the_minimum` (3672) — non-Eating
  activities; `out_of_chow` is Eating-gated, nothing moves.
- `a_refused_proposal_is_stamped_with_kitty_proposal_and_tick` (3229),
  `duration_enforcement_decides_the_absorbed_flag_never_the_refusal`
  (3273), `a_refusal_past_the_scene_minimum_is_still_absorbed` (3328),
  `a_same_tick_duet_race_is_still_a_stamped_refusal` (3774) — refusal
  surface; scene ends route through end_activity only.
- action.rs: `eating_requires_nearby_chow` (1103),
  `empty_chow_cannot_be_eaten` (1213),
  `eating_consumes_one_serving_and_relieves_hunger` (1228) — validate
  and effect, untouched.
- action.rs `announcing_food_and_eating_it_all_is_lawful` (3542) —
  T003 verdict: calls `apply` directly, never starts a clocked scene
  or runs `resolve_activity_ends`; asserts emission-time truth,
  despawn-at-env-resolve, full relief. NOT in the must-flip pile.
- `welfare_longrun.rs:41` crowded-out kitty — retarget/respawn path.

## Red record (T004-T009)

Pre-edit reds (all four guards against the unamended engine, predicted
failures confirmed verbatim): `an_emptied_bowl_ends…` ("the first
resolution…" left Eating / right Idle), `a_shared_bowl_emptying…`
("kitty 1's meal ends with the bowl"), `a_meal_never_stretches…` ("the
fed-from bowl is empty…"). VACUOUS FIRST-CUT on record:
`a_vanished_bowl…` v1 removed the bowl a tick too late (elapsed had
reached the minimum, where the OLD rule ends the meal too) and stayed
green; restaged to remove the bowl inside the meal's first tick, then
RED with the predicted failure.

Mutate cycles (scripts/mutate.sh, all RED CONFIRMED, baseline ==
restored):

1. Revert `done_naturally` to the spec-006 grouping → the four guards
   red (`--expect` matched "the first resolution…"); `need_zero_before`
   in the same run stayed green (kept clause intact under mutation).
2. Feeding-blind end (`out_of_chow` forced false) → four guards red
   (`--expect` matched the vanished-bowl message).
3. Stretch-across predicate (filter stocked BEFORE picking nearest in
   `adjacent_stocked_chow_in`) → no-stretching guard red (`--expect`
   matched "fed-from bowl is empty|tied lower-id bowl drained") — pins
   the clarify-2026-10-11 ruling in code.
4. Double-record in `end_activity` → log-count asserts red (`--expect`
   "one ordinary end record").

Not separately mutated, with reason: the `refusal_log.is_empty()`
asserts are absence pins whose positive surface is already guarded by
`duration_enforcement_decides_the_absorbed_flag_never_the_refusal`
(kept pile); no one-line mutation produces a refusal from the
resolution path without inventing the very code the design forbids.

## Pin sweep record (T010-T012)

- fog_continuity: first-divergence ticks captured pre-re-record — pre-fog
  76/76 (a cat Moves where it held an absorbed Eat), preladder r=5 at 52;
  justification paragraphs appended in both history blocks; fixtures
  re-recorded via the ignored mains; comparisons green.
- evolution_golden: BOTH pins moved (whole-world dynamics change) —
  golden a3fd38e5… → 1ceba1bf…, strip witness 3c4e86cd… → 8f59ef5c…,
  history paragraphs appended in-file.
- activity_durations.rs `twenty_thousand_ticks_of_activities_respect_their_bounds`
  reddened — a spec-006 SC-001 property pin MISSED BY THE T002 SORT
  (reported per rule 6, then moved with the spec): Eating added to
  `counterpart_can_leave` (a drained/vanished bowl is the meal's
  counterpart leaving), module doc updated. Its red was observed before
  the edit; it is the property-layer red for FR-001.
- Everything else green unchanged: snapshot_resume, joint_action_parity,
  roam_tether, consent_gate, waterline_contagion; ALL rl pins
  (run_json_golden, eval_suite, welfare_longrun, harness_policy,
  mixed_control, clock_and_range, artifact_v3_parity, vocabulary_flags)
  — their runs contain no below-minimum bowl-drain event, a legitimate
  no-divergence (they are not guards of 060), recorded here so the
  green is a claim, not an oversight.
- Workspace after sweep: 1019 passed / 0 failed (core lib 554 → 557:
  one test rewritten, three added).
