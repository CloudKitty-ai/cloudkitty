# 048 redden list — red-first cycle record

Standard (adopted spec 047): every mutation/revert cycle runs
`cargo test --workspace --no-fail-fast`; predictions written BEFORE the run;
restore verified by RE-READING THE COUNT. Commit before every
mutate-then-revert cycle (checkout-trap rule, five occurrences on record).

Baseline count (branch tip before implementation): recorded at cycle 0.
FINAL count (T017, all tasks done): **817/0** = 809 baseline + 8 new guards
(T004-T007, T009-T011, T013). fmt + clippy CI-exact clean. Golden + strip
+ rl wire goldens regenerated with justification; defaults stamp test
untouched and green.

| # | Task | Mutation / staging | Prediction (exact reds) | Observed | Restored + count re-read |
|---|------|--------------------|-------------------------|----------|--------------------------|
| 0 | T002 | none (baseline) | — | 809/0 | — |
| A | T003 | `counterpart_gone_in` element arm → `false` | 2 reds: `a_vanished_critter_ends_play_where_it_stands`, `golden_evolution_flag_absent_10k_ticks` | 4 reds: both predicted PLUS `golden_strip_witness_refusal_ring_is_the_only_delta` + `run_json_wire_shape_matches_the_golden` — MISSED the two trajectory-companion pins (same root cause: they replay the same 10k-tick run as the golden). 805/4 | yes; 809/0 |
| B | T003 | `counterpart_gone_in` duet arm → `false` | ZERO reds — the duet prune arm is defense-in-depth: one-sided duets never arise dynamically (probe 2026-09-02: dead-at-snapshot PlayDuet = 0 across all four arms; duets end both sides in one slot), and the invariant checker (`invariants.rs:164`) guards the state, not the prune path. No existing test stages a one-sided duet through prune. | 809/0 — exactly as predicted (a predicted-vacuous cycle: the point WAS to record the coverage fact) | yes; lib 456/0 |

Cycle A honesty note: prediction under-counted by the golden's two companion
pins. Adopted for later cycles: any mutation that can move a live trajectory
predicts ALL FOUR golden-family pins (evolution golden, strip witness, JSON
wire golden, and — only if drivers diverge — joint parity) or names why not.

| C | T009 (also T004/5/7's red-first re-proof) | T008's check disabled (`if false &&`) at HEAD 7d9b980 | 4 reds: `a_scene_whose_critter_moved_away_is_not_continued`, `a_scene_whose_critter_expired_is_not_continued`, `every_builtin_declines_a_snapshot_dead_scene`, `a_dead_critter_scene_yields_a_real_action_and_no_refusal_row`; golden family GREEN (trajectory back to pin) | exactly 4/4, golden green — 810/4 | yes; lib 461/0 |
| D | T012 | groom arm of `counterpart_gone_in` → `false` | prune witness `a_groomed_friend_walking_away_ends_the_grooming` + behavior witness `a_groom_whose_friend_walked_away_is_not_continued` red; the 3 golden-family reds present EITHER WAY at this HEAD (T008 landed, T015 re-pin pending) so they are not evidence | exactly the 2 witnesses red (+3 standing golden reds, noted non-marginal) | yes; lib 463/0 |

Cycle D note: the FR-002 both-witness guard is proven in both directions —
the same one-arm weakening reds the ENGINE's ending witness and the
BEHAVIOR's declining witness, because both consult the one body.

Cycle B consequence: the duet arm of the shared predicate has NO
mutation-witness among existing tests and CANNOT get a behavior-side one
(the behavior never sees a one-sided duet — probe-proven). Its guards are
the invariant checker plus T013's race pin. Recorded per rule 3.

| E | review F1 | duet arm of `counterpart_gone_in` → `true` (always gone) | new pin `a_scene_whose_duet_is_still_reciprocal_continues` red (the F1 point: the duet arm gains a BEHAVIOR witness) + duet lifecycle tests (named: `duet_relief_lands_once_per_tick_for_both_partners`, `a_duet_ends_for_both_when_either_is_content`, `a_post_min_interrupt_frees_both_duet_partners_the_same_tick`) + 3 golden family; T013 uncertain | 10 reds: pin ✓, 2/3 named lifecycle (post_min_interrupt survived — both sides end either way), golden 3 ✓, T013 GREEN (robust), + 4 under-enumerated duet-dependent tests (`default_ring_covers_the_baseline_window_under_absorbed_load`, `twenty_thousand_ticks_of_activities_respect_their_bounds`, 2 wet-fur duet charges). Class prediction held; names under-counted, recorded honestly. 808/10 | yes; lib 465/0 |

## Review dispositions (medium, 2026-09-02; Elizabeth ruled)

1. FIXED — live-reciprocal-duet behavior pin added; cycle E gives the duet
   arm the behavior witness cycle B said was impossible for DEAD duets
   (the live direction was the testable one).
2. DOCUMENTED — reverse-race absorbed=true class recorded in spec Edge
   Cases; bounded, lands in the class R8 already excludes; relayed to
   Experiments for the re-baseline.
3. FIXED — quickstart §1 now uses a verified multi-filter command,
   "exactly 9 passed" expectation pinned.
4. FIXED — CHANGELOG entry extended: BC teacher label distribution moved;
   pre-048 policy artifacts learned the old teacher.
5. FIXED — doctrine test iterates BehaviorRegistry::with_builtins() and
   asserts a REAL action (not stale, not Idle).
6. FIXED — strip-witness prose now states the detector is DORMANT for the
   048 generation (same-run pins) and resumes at the next additive claim.
7. OWNER RULED (option 1) — `[rng-sequence]` carried by consequence per
   changelog precedent; prose states the literal draw order is untouched.
8. OWNER RULED — TABLED as banked follow-up (spec-006 meal-end-rule
   change, own spec); rationale in spec Edge Cases.
Sub-cap fold-ins: `is_conscriptable_friend` now delegates to
`is_available_friend` + clock (orphaned `friend_pair` removed);
`mid_critter_play` triplication left as-is (different modules, different
staging needs).

## probe-after (T014 results, 2026-09-02, fixed build @ T013 tip + probe 275896e ride-along)

Window 1500..21500, all four Addendum 2 arms: **`reproposed 0` on
dead-at-snapshot scenes in EVERY class** (SC-001/SC-002). Dead scenes still
occur (PlayCritter dead-at-snapshot 780–1,094/run; Groom 76–98) — the
behavior just never proposes into them, and refused/rescued/reformed are
all 0 by construction. PlayDuet same-tick race refusals persist at
2,872–3,664/run (pre-fix band 2,648–3,416; trajectories lawfully diverged
— SC-005: races untouched). Drink 0 everywhere (water permanent).

| arm | PlayCritter dead / reproposed | Groom dead / reproposed | Duet races |
|---|---|---|---|
| c30-consent30-20260911 | 1094 / 0 | 76 / 0 | 2872 |
| c30-consent30-20260912 | 933 / 0  | 98 / 0 | 3054 |
| c30-off2-20260911      | 954 / 0  | 88 / 0 | 3152 |
| c30-off2-20260912      | 780 / 0  | 80 / 0 | 3664 |

## Discipline slips (rule-3 honesty)

- T013 debugging: a `git stash && git stash drop` intended to discard a
  temporary dump ALSO discarded the uncommitted T013 test (same-tree
  hazard, stash-flavored cousin of checkout-trap occurrences one–five).
  Rewritten from context, no loss — but the rule generalizes: COMMIT the
  real work before ANY tree-level discard, stash included.
- T013 staging bug found by the dump: the interrupter's escape step aimed
  INTO the partner's tile — an illegal move interrupts nothing. Per-role
  escape directions fix it (test comment records the trap).
