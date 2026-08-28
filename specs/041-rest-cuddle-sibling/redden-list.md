# The sorted redden list (T004 — rule 6)

Sorted BEFORE running anything. Verified against the tree at 2555205.
Every must-red entry must be seen red **for the predicted reason** in
its commit; a must-red that stays green is vacuous — fix if we made it
so, report if pre-existing (rule 3).

## Must go RED at commit 1 (the split)

**OBSERVED (2026-08-28, corrections — running is not reading):** the
pre-existing pile below stayed GREEN, and honestly so — none of it was
vacuous, the predictions were wrong:
- `cosleep_defaults_are_behavior_preserving` asserts `cuddle_relief == 15.0`
  and cosleep arithmetic — the split keeps both. GREEN, correctly.
- `cosleep_dials_never_touch_the_duet_or_the_groomer` asserts duet/groom
  pay 15.0 — after the swap they pay the new dials' identical classic
  default. GREEN numerically; its isolation claim is now carried
  stronger by the new `each_split_dial_moves_only_its_own_site`.
- `any_default_moving_moves_the_stamp` (suite.rs:1512) bumps
  `cuddle_relief` — the key still serializes into the defaults stamp
  (inert ≠ absent), so the stamp still moves. GREEN; left unchanged
  (rule 3) — the probe breaks naturally at the 3.0 deletion.
- Both shipped-config sweeps: GREEN (new keys parse; nothing pins a
  key set).

The reds that actually carried commit 1 (all observed red-first):
`the_remaining_relief_dials_reject_negative_and_non_finite_values`
(nan accepted on the three new dials before the validate.rs entries),
`the_deprecated_shared_dial_is_inert` ("got 0" — duet paid the
wrenched 999), `each_split_dial_moves_only_its_own_site` ("got 35" —
duet deaf to its own dial before the swap).

| test | site | predicted red |
|---|---|---|
| `cosleep_defaults_are_behavior_preserving` | `action.rs:2611` | asserts `cuddle_relief == 15.0` by name and cosleep defaults derived from it; the arithmetic comments cite the shared dial |
| `cosleep_dials_never_touch_the_duet_or_the_groomer` | `action.rs:2637` | asserts groomer (:2656) and rest duet (:2673) are paid by `cuddle_relief` — after the swap they are paid by the new dials |
| `any_default_moving_moves_the_stamp` | `suite.rs:1509` (bump at :1512) | bumps `core.actions.cuddle_relief` expecting the stamp to move — the key is inert after the split, the stamp no longer moves → the sweep must be re-pointed at a live dial |
| nan-validation table | `config/mod.rs:~1829` | the table test enumerates dials; three new keys must join it (the guard is the totality assertion — watch whether it reds on its own or needs the entries added red-first) |

### Watch (may red, may stay green — observe and record)

- `shipped_configs.rs` (core) and
  `shipped_configs_rl.rs::every_shipped_toml_loads_through_both_config_surfaces`
  — the two config sweeps; they load every committed toml through HEAD
  config. New keys in `cloudkitty.toml` should load fine (green); if
  either pins a key set it reds. Record which happened.
- `the_engine_defaults_stamp_is_stable_and_well_formed` — stamp moves
  at commit 1 (new fields); the test asserts self-consistency only, so
  it should stay green.

## Must go RED at commit 2 (the engine sibling)

| test | site | predicted red |
|---|---|---|
| `a_busy_or_sleeping_partner_cannot_be_conscripted` (Rest half) | `world.rs:2876` | "a cat mid-meal is not draftable" — under the sibling a cat mid-meal is exactly restable-beside; the Play half (conscription kept) must stay green |
| `a_cuddle_is_a_duet_with_one_shared_clock` | `action.rs:1826` | rest no longer binds the partner or shares a clock |
| `duet_partners_are_only_the_bound_kind` | `kitty.rs:774` | `duet_partner()` drops its Resting arm — rest is no longer a bound kind |
| `golden_evolution_flag_absent_10k_ticks` | `tests/evolution_golden.rs` | scripted choices change (busy-partner rest now legal) + counters ride the world JSON; regenerate the golden in this commit with justification (see continuity-baseline.md) |

### Non-test surfaces that MUST move in commit 2 (missed by the plan's file list, found in T004's sweep)

- `Activity::duet_partner()` (`kitty.rs:122-132`): drop the `Resting`
  arm. Load-bearing: `end_activity` (`world.rs:414`) ends the
  duet partner's scene through it — kept as-is it would end an
  UNBOUND partner's unrelated activity.
- `prune_dead_activity` (`world.rs:473-475`):
  `Resting { with_friend: Some } => !reciprocal_duet` must become
  `false` (like `Sleeping`) — the sibling's partner is never
  reciprocal, so the old arm would kill every partnered rest scene at
  its first prune. The per-tick re-filter in the effects arm is the
  lawful wander-exit (D1).
- `apply` Play arm comment (`action.rs:623`) says "like the Rest
  arm's partner filter" — comment stales when the Rest arm changes.

### Watch at commit 2

- `mask_oracle.rs` (RL): the mask derives from `validate` by probing —
  no code change (D7), but any oracle case pinning rest-with-busy as
  illegal reds and re-points.
- `approach_etiquette.rs:51`, `meow_courtesy.rs:112` — use Resting
  shapes; expected green (solo / shape-only).
- `snapshot_resume.rs` — FR-009's home for the bound-duet fixture.

**OBSERVED at commit 2 (2026-08-28):** every predicted red seen, each
for its predicted reason:
- 7 new guards red first (busy-partner legality "left: Idle"; idle
  partner bound "left: Resting{Some(1)}"; tier/pay guards "got 50";
  wander guard partner kept) → green after the rewrite.
- `a_busy_or_sleeping_partner_cannot_be_conscripted` Rest half red
  ("a cat mid-meal is not draftable") → repointed: legal, meal
  untouched; Play half stayed green (conscription kept).
- `a_cuddle_is_a_duet_with_one_shared_clock` red (partner no longer
  bound) → repointed as `a_cuddle_names_a_companion_and_owns_its_clock`.
- `duet_partners_are_only_the_bound_kind` red → Resting moved to the
  reference-without-binding kind.
- Pinned-JSON event guard red on the exact bug (zero counters leaking
  into the wire) before `skip_serializing_if` → green after.
- Counter guards red (0 vs expected) before `count_tier_tick` wiring.
- FR-009 resume guard: taught the spec-006 effects-due rule (first
  resumed tick stamps without paying); rule-5 bug-introduction pass
  (re-filter via `is_conscriptable_friend`) went red as predicted,
  reverted.
- `golden_evolution_flag_absent_10k_ticks` red (digest moved:
  legality + counters) → regenerated per its own doctrine, new pin
  `7b361b2a…`, determinism ×3 on the new pin.
- Commit-1's three pricing tests needed re-staging (idle partner now
  earns drip 0.0, not mutual) — the new semantics working as specified.
- Watch pile: mask_oracle, approach_etiquette, meow_courtesy,
  snapshot_resume existing cases, all RL schema pins — GREEN.
- **Late red, surfaced only under the repriced dials** (T004 missed
  it): `test_support::assert_orthogonal_scenes` still held Resting to
  the bound-duet every-tick adjacency law
  (`a_crowded_out_kitty_is_fed_by_retarget_and_respawn…` red at
  commit-3 verification — a scripted rest partner lawfully stepped
  away). Repointed in commit 2 (amended): Resting, like Sleeping,
  carries no every-tick adjacency law; Play keeps it. Couldn't
  trigger at drip 0.0 — no scripted rest scenes existed to wander
  from.

## Must go RED at commit 2, flipped GREEN by commit 3 alone

- The T028 riders-partial arithmetic guards (toml-driven): red against
  the un-repriced `cloudkitty.toml`, green after the pure config diff.
  Their red→green across a diff that touches no `.rs` file is their
  rule-5 cycle.

## Must stay GREEN throughout

- Co-sleep pricing tests: `cosleep_pays_the_tier_the_partners_presence_earns`
  (:2563), `a_departed_cosleeping_partner_stops_granting_cuddles` (:1752),
  `a_drip_tier_partner_on_a_beam_conducts_nothing` (:1576)
- Warmth conduction: `warmth_conducts_from_a_mutual_partner_on_a_beam`
  (:1350), `either_on_beam_warms_both_sleeping_partners`,
  `solo_rates_and_the_conduction_piles_cuddle_are_untouched` (:1614)
- Grooming: `grooming_a_friend_cleans_them_and_comforts_the_groomer` (:1308)
- Play: full battery :1783-2405 incl.
  `a_play_proposal_at_a_busy_partner_downgrades_to_solo_play` (Play
  keeps conscription), `duet_play_still_pays_both_partners_the_kitty_value`
- Durations: `activity_durations.rs` (cuddle {6,12} untouched)
- Determinism: `determinism.rs`, `joint_action_parity.rs`,
  `turn_order_fairness.rs`
- Article I–V property suites: `invariants_proptest.rs`,
  `welfare_longrun.rs` (both crates), `water_safeguard.rs`
- Wire shape: `run_json_golden.rs`, `schema_four_pins.rs`,
  `codec_totality.rs` (menu 34 entries, KITTY_SLOT, message head
  frozen — FR-003)
- Snapshot: `snapshot_resume.rs` existing cases
