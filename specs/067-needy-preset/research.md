# Research: Needy Behaviour Preset

No NEEDS CLARIFICATION markers remain (three owner rulings 2026-10-26 in
spec §Clarifications; the Professor's four changes folded; FR-016 from
her seventh-need note). The decisions below resolve the plan-level
unknowns, each measured against the tree at c9d85721 and re-measured at
5841a478 (main merged in) after the 2026-10-26 analyze pass
(`analysis-2026-10-26.md`): D1, D3, D4, D5, D6, D7, D10 were rewritten
there; D15–D17 are new.

## D1. Where the schedule's state lives: on the kitty, in the world

- **Decision**: `Kitty.needy: Option<NeedyState>` with
  `#[serde(default, skip_serializing_if = "Option::is_none")]`
  (kitty.rs:288–308 already carries `pursuit`, `abandoned_chases`,
  `last_relief`, `activity_clock` with exactly that pattern).
  `NeedyState` holds the preset variant (`hold: bool`), the private
  sub-stream (`ChaCha8Rng`, serialized like `World.rng`), the ordinal,
  the phase (`Resting { next_onset }` or `Held { onset, masked }`), the
  NEXT episode's masked set (drawn ahead, D3) and the last release
  (`tick`, `by`) for the recorder.
- **Rationale**: `Behavior::decide(&self, &DecisionContext)`
  (behavior/mod.rs:84) is stateless and builtins are shared
  `Arc<dyn Behavior>` across kitties (mod.rs:146–152), so a per-seat
  schedule cannot live in the behaviour. The release-at-level rule
  depends on the need trajectory, so the phase is NOT a pure function
  of (seed, id, tick): the state must persist and the saved world is
  authoritative on resume (spec FR-003 and the save/resume Edge Case,
  amended at analyze H5). On the kitty it rides the snapshot, is
  visible to the preset as `ctx.me.needy` (its own state, rule 12's
  own-state read), to the engine's verdict and sweep, and to the
  operator's surfaces (D10). Absent for every non-needy kitty.
- **Visibility (analyze H4)**: `fog_for` (world.rs:1734–1751) clones
  every visible kitty into the observer's view and blanks only
  `memory` and `explore_waypoint` on friends; the view is the plugin
  `DecisionRequest`'s world, the policy observation's input and the
  collector's trace. So `fog_for` blanks `needy` on every kitty but the
  observer: a needy kitty's state is its own (FR-012 as amended). The
  observer's own `needy` stays — a needy kitty's own view carries it,
  and a needy kitty is never a plugin or policy seat (D16).
- **Alternatives**: a side table on `World` keyed by kitty id —
  rejected: two homes for one kitty's state and a second serialization
  site; re-deriving at resume by replay — rejected: level release
  depends on the path.

## D2. The sub-stream: domain-tagged ChaCha8 from (world seed, kitty id)

- **Decision**: `needy::sub_stream_seed(world_seed, kitty_id)`: seed
  bytes = world seed LE (0..8), kitty id LE (8..12), the domain tag
  `b"ck-needy-v1"` (12..23), zeros — the shape of
  `starts::sub_stream_seed` and `init_needs::sub_stream_seed`
  (init_needs.rs:40–45, tag `ck-initnd-v1`), with the kitty id added so
  two needy seats draw independent streams (spec Edge Cases). The
  stream is created at `World::try_generate` for each needy seat and
  carried in `NeedyState.rng`; every schedule draw comes from it and
  nothing else. The master `World.rng` and every `DecisionRng` are
  untouched.
- **Rationale**: Article V and the 062/065 precedent; one law change =
  one domain-tag bump.

## D3. The schedule law (contracts/needy-law.md §2–§4)

- **Decision**: ONE conversion from the stream to a uniform, the
  init-law §5 recipe (`init_needs::draw_value`, init_needs.rs:50–53):
  `u = (next_u64() >> 11) as f64 / 2^53` in [0, 1). Every draw is one
  `u`: a weighted index is `cumulative(weights) > u·total` (first
  index); a tick within a level is `lo + floor(u·(hi − lo))` (flat) or
  `floor(exp(ln lo' + u·(ln hi − ln lo')))` with `lo' = max(lo, 1)`
  (log-uniform), clamped into `[lo, hi)`; a partial Fisher–Yates step
  is `j = i + floor(u·(N − i))`; a gap is `min + floor(u·(max − min +
  1))`. At generation: first-onset level, tick within level, then the
  first episode's m and set. At each release: the gap, then the NEXT
  episode's m and set — so the mask is fixed before it applies and the
  draw order is pinned. Ordinal increments at each onset; 0 before the
  first. (Analyze LOW: "one draw per step" through rand's `gen_range`
  is not how `gen_range` consumes; pinning the conversion makes the
  law porting-grade like init-law §5.)
- **Rationale**: the Professor's §Q2 schedule-over-coin; replication
  needs the seed alone; log-uniform offered because the Professor
  names both.

## D4. Advance point: Phase 4, after `advance_needs`; "tick" pinned

- **Decision**: `self.advance_needy(config)` immediately after
  `self.advance_needs(config)` (world.rs:492) and before
  `update_announce_arming`. "Tick" in the law is the tick the NEXT
  snapshot carries, `t = self.tick + 1` (the increment is at
  world.rs:500, after this step), so the recorder sees a transition on
  the tick it reads it (analyze M3). The step, per kitty with state:
  - `Resting { next_onset }` and `t >= next_onset` (AT OR PAST, analyze
    H7: an onset of 0 opens on tick 1 and no onset is skipped) → `Held
    { onset: t, masked: next }`, ordinal += 1, then the ONSET SWEEP
    (D5): end the kitty's own activity if its continuation's
    proposer-relief set meets the mask; degrade or end other kitties'
    scenes whose partner-relief on this kitty meets the mask.
  - `Held { onset, masked }` → released by LEVEL (`needy` only) when
    every masked need ≥ `release_level` on the post-rise needs, else by
    LIMIT (both presets) when `t − onset >= hold_ticks`; level is
    checked first. On release: `last_release = Some { tick: t, by }`,
    draw the gap, draw the next set, phase = `Resting { next_onset: t +
    gap }` — one step, no intermediate state (analyze H7's gap-1
    stall: `gap >= 1` puts the next onset at `t + 1` or later, so a
    release and the next onset never share a step).
- **Rationale**: the needs the release rule reads are this tick's
  risen needs; the mask the next decide reads is in place before Phase
  1 of the next tick.

## D5. Enforcement: the needy verdict + the onset sweep (engine law)

- **Decision** (Article IV): `World::needy_verdict(proposer, validated,
  config) -> Action` runs directly after `consent_verdict` at BOTH
  sites (the served loop world.rs:419 and `apply_slot_verdict`
  world.rs:662). First line: when neither the proposer nor the named
  partner carries state, return the input (the inert path). It
  resolves to `Idle` when (a) `proposer_relief(action)` meets the
  PROPOSER's mask, or (b) the action names a partner or target `p` and
  `partner_relief(action)` meets `p`'s mask. Both tables live in
  `core/src/needy.rs`, read off `apply_activity_effects`
  (action.rs:777–912) and `apply_sleep_relief` (914–973) — analyze H1:
  the actor also gains Cuddle from grooming a friend
  (`groom_cuddle_pay`, :829–834) and from co-sleep (:969–970), so a
  governing-need test would leak Cuddle through the kitty's own groom
  response and block grooming a friend under a Bath mask:

  | action | proposer relief | partner relief (on the named kitty) |
  |--------|-----------------|-------------------------------------|
  | Eat / Drink | eat / drink | — |
  | Sleep { None } | sleep | — |
  | Sleep { Some p } | sleep, cuddle | cuddle |
  | Rest { None } | — (posture) | — |
  | Rest { Some p } | cuddle | cuddle |
  | Groom { None } | bath | — |
  | Groom { Some p } | cuddle | bath |
  | Play { None / element } | play | — |
  | Play { Kitty p } | play | play |
  | Chase, Move, Idle, Meow, Purr | — | — |

  Chase relieves nothing itself, so the law does not refuse it; the
  preset's own filter treats it as pursuit of Play (D6, analyze M1).
- **Onset sweep** (the second half; analyze H2): the mask is HIDDEN
  state, so it must not enter `available_friend_in` (world.rs:1969) —
  that body is read by validate (action.rs:385/389/394), by
  `refusal_reason` (:482), by the RL legal-mask replay
  (`cloudkitty-rl/src/mask.rs`), by the prune and its snapshot twin
  (`counterpart_gone_in`, world.rs:1950), by contagion and by
  `is_conscriptable_friend` — a rule there would leak the target's
  mask into a covered seat's legal mask and mislabel refusals. Instead
  the engine acts ONCE, at the onset tick, in `advance_needy`: the
  needy kitty's own activity ends through `end_activity` (world.rs:539;
  a social-play duet ends for both) when its continuation's proposer
  relief meets the mask; every other kitty whose activity names the
  needy kitty (`Activity::partner()`, kitty.rs:105) and whose partner
  relief meets the mask is handled by kind — Grooming → `end_activity`;
  Playing { Kitty } → `end_activity` (duet); Resting / Sleeping { with }
  → the companion is dropped (`with_friend = None`, clock untouched —
  the spec-041 solo-posture degrade the effects arms apply when a
  friend wanders off, action.rs:871/:900). After the sweep no running
  scene delivers masked relief; a NEW scene cannot start because the
  verdict refuses it; a continuation proposal (`is_continued_by`) of a
  degraded scene continues the solo scene. The effects arms and the
  groom arm are untouched.
- **Guards (rule 5, "wrong layer")**: the relief tables are
  cross-checked against the effects on a probe world — apply each
  action for one tick with the partner adjacent and settled and every
  need at 50; the set of the ACTOR's needs that moved equals
  `proposer_relief`, the PARTNER's equals `partner_relief`, for every
  row (Chase and Rest { None } move nothing). The sweep's guard: a
  co-sleep in progress with the needy partner stops lowering the needy
  kitty's cuddle from the onset tick while the friend's own sleep
  relief continues; a groom of the needy kitty in progress ends on the
  onset tick.
- **Rationale**: the consent gate is the precedent for the engine
  judging a proposal about a target's hidden state at the apply slot
  (world.rs:677–706); duration enforcement cannot override the verdict
  for a NEW proposal because the sweep ended the masked scene.

## D6. The preset: `Needy { hold: bool }` wrapping `Teacher::GEN2`

- **Decision**: `behavior/needy.rs`: `pub struct Needy { hold: bool }`,
  registered in `with_builtins` (mod.rs:146) under `needy::NAME` and
  `needy::HOLD_NAME` (constants in `core/src/needy.rs`, one home);
  `is_builtin() = true`; `teaches() = false` (D8). `decide`: when
  `ctx.me.needy` is absent or its mask is empty, DELEGATE to
  `Teacher::GEN2.decide(ctx)` — the pre-onset trace is byte-equal by
  construction (analyze M2). Under a non-empty mask: build a MASKED
  context — `me` with the masked needs read as 0, the same `world` and
  `config` `Arc`s, and `rng: ctx.rng.fork()` (a new `DecisionRng`
  method cloning the ChaCha8 state; `DecisionContext` is not `Clone`
  and `DecisionRng` is a mutex, rng.rs:71–91) — run
  `Teacher::GEN2.decide_action(&masked)` (teacher.rs:83, already
  `pub(crate)`), then the POST-FILTER: if `proposer_relief(action)`
  meets the mask, or the action is a Chase while Play is masked
  (luxury play returns Chase, which the zeroed view cannot stop), then
  `Sleep { Some }` under a Cuddle-only mask becomes `Sleep { None }`
  (the kitty still sleeps, alone — spec FR-005 as amended) and
  anything else becomes `Idle`. The message is `super::announce(ctx)`
  on the UNMASKED context (teacher.rs:156–158 shape; `announce` draws
  no rng and reads `ctx.me.needs` and `message_legal`), so calling
  stays on (FR-005, FR-007; owner "A").
- **Rationale**: the three presets stay byte-equal (nothing in
  `Teacher` changes; FR-002 US2 scenario 2); the engine verdict (D5)
  is the law, so the behaviour's filter only saves wasted turns —
  D14 records the redundancy and its test.
- **Alternatives**: threading an exclusion set through `selection` and
  every rung — rejected: touches the three presets' code paths and
  needs a byte-equality proof per rung.

## D7. Config: `[needy]` optional top-level section, N-sized

- **Decision**: `Config.needy: Option<NeedyConfig>` skip-if-none after
  `welfare_hazard` (mod.rs:122; the 062–066 attribute pair).
  `NeedyConfig { mix: Vec<f32> (len N), release_level: f32,
  hold_ticks: u64, gap: { min, max }, onset_levels: Vec<u64> (ascending
  tick edges, ≥ 6 edges = ≥ 5 levels; the last edge is the exclusive
  bound of the last level), onset_weights: Vec<f32> (len = levels),
  onset_draw: Flat | LogUniform }`, `deny_unknown_fields`. NO per-need
  floor table (analyze LOW: `NeedyConfig::default()` cannot read the
  engine floor, and no mechanism reads a floor — the release rule
  reads the engine's own `actions.sleep_floor_off_beam`; spec FR-008
  amended). `NeedyConfig::default()` = the coverage design (A4): mix
  `[0.5, 0.2, 0.15, 0.15]` then zeros to `NeedKind::ALL.len()`,
  release 90, hold 1,500, gap 300–1,200, edges `[0, 2, 10, 50, 200,
  20000]` — straddling the F-070 knee (analyze M16: 0.978 after 2
  clean ticks, 0.658 after 10, 0.537 after 20, 0.362 after 50; a
  0–10 level would pool 0.98 with 0.66) with the last level running to
  the end of a 20,000-tick world (analyze M13) — weights 0.2 each,
  flat. Section absent + needy seat → defaults apply (the section is
  parameters, the seat is the hazard). Validation position 22 (after
  `validate_welfare_hazard()?`, mod.rs:1751): FR-008's rules, the
  wrong-length mix error naming N (FR-016), `release_level >
  actions.sleep_floor_off_beam`.
- **Rationale**: FR-008/FR-016; the error-text shape follows 065's
  `[initial_needs].<need>` convention (`[needy].mix`).

## D8. Teacher eligibility: `Behavior::teaches()`

- **Decision**: `fn teaches(&self) -> bool { true }` on the trait
  (behavior/mod.rs:80–108), `false` for `Needy`;
  `BehaviorRegistry::teaches(&self, name) -> Option<bool>`. The
  collector (`experiments/tools/bc-collect/src/main.rs`: records every
  config behaviour as a demonstrator, provenance at :497–512) skips a
  seat with `teaches == Some(false)` and logs the refusal once per run
  (FR-011). Lane: Experiments' — CONSENTED 2026-10-26 to option (a),
  the collector half rides this PR under `cross-lane:` (their grounds:
  between a 067 merge and a later collector change a needy seat would
  be recordable as a teacher, the exact state FR-011 forbids). Their
  four conditions, all binding on the PR: (1) its own rule-5 red (a
  config seating a needy kitty → that kitty's rows absent, the other
  seats' rows unchanged, the refusal logged once per run); (2) the
  provenance stamp names the refused seats explicitly
  (`teachers_refused: [<kitty id>, ...]`, empty when none), so a corpus
  recorded after the flag is distinguishable; (3) WITHDRAWN by
  Experiments the same day on reading the collector's fallback
  (main.rs:497–511): an unknown behaviour name is stamped `needs_driven`
  because that is what the engine runs for it, exp-002 families depend
  on that path, and a mistyped needy name runs needs_driven, teaches as
  it does and is stamped truthfully — so the refusal keys on
  `teaches(name) == Some(false)` ONLY; `None` keeps today's fallback
  and stamp; (4) the PR body quotes the consent and Experiments reads
  the collector hunk before the owner merges.
- **CI note (analyze M14, rule 3)**: `.github/workflows/experiments.yml`
  only BUILDS bc-collect; its tests never run in CI. The collector's
  red is local evidence recorded in the PR body; the gap is reported
  to Harness, not fixed here.
- **Rationale**: spec 066 deferred the flag to its first reader; the
  collector is the reader; one `bool` on the trait is the smallest
  surface and lets a future plugin seat declare itself too.

## D9. Hazard registry: two modes, name = preset name

- **Decision**: `HazardMode::{InitialNeeds, Needy, NeedyHold}`, `ALL` in
  that order (guard-law §2 of 066 gains two rows), `name()` returns the
  preset name constants from `core/src/needy.rs` (one home),
  `activation` = the first kitty in config order whose `behavior ==
  name` (`[[kitty]] 'Mochi' (id 3) behavior = "needy"`). N4 from #469's
  review: a test with an exhaustive `match` over `HazardMode` that
  builds the list and asserts it equals `ALL` — a new variant fails to
  compile until it is placed. 066's `the_registry_names_are_unique_and_in_all`
  (welfare_hazard.rs:218) and every test pinning the known-names text
  (`known: initial_needs`) are updated: the known list is built from
  `ALL`, so the text becomes `initial_needs, needy, needy_hold`
  (analyze M9; rule 6 — those kept tests go red for the right reason
  and are re-pinned).
- **Rationale**: spec FR-009; owner "B" (two presets, each its own
  mode).

## D10. Observability: the kitty's own snapshot entry + a binding accessor

- **Decision**: FR-012's "lab recorder's per-kitty record" is realised
  as `Kitty.needy` in the world snapshot (the saved world, `GET /state`
  and every tool that walks `world.kitties` see mask/ordinal/phase for
  a needy seat and nothing new for any other kitty) plus
  `ParallelEnv.needy()` in the binding returning `[(kitty_id, [need
  names], ordinal, phase)]` for needy seats only, beside
  `recent_meows()` and `elements()` (cloudkitty-py/src/lib.rs:494,
  :511 — the existing pattern for world-state readers that are not
  observations). Phase strings: `resting`, `held`, and on the release
  tick `released_level` or `released_limit` (from `last_release`). The
  binding's `infos` stay per EXTERNAL agent (episode.rs:114–120 and the
  "only external agents are encoded" rule at :497–500) — unchanged.
  Friends' views never carry it (D1).
- **Rationale**: no observation-schema or `infos` shape change
  (FR-014; non-needy records byte-identical); the accessor is the
  recorder's read; the snapshot is the operator's.

## D11. Byte-inertness proof

- **Decision**: with no needy seat: `Kitty.needy` is `None` and skipped;
  `advance_needy` iterates zero kitties; `needy_verdict` returns the
  input when neither party has state (first line); `fog_for`'s blank
  writes `None` over `None`; the config section is absent and
  skip-if-none; the invariant check (D16) reads a `bool` per kitty.
  Guards: stamp unchanged (recorded before/after), default JSON lacks
  `needy`, a fixed-seed world ticked 300 ticks byte-identical to the
  pre-feature engine's serialized world (the 066 T009 shape), the three
  presets' decisions byte-equal on seeded worlds against COMMITTED
  goldens (D12).

## D12. The three presets stay byte-equal

- **Decision**: no edit to `Teacher`'s fields, constants or
  `decide_action` body; `needy.rs` calls into it. Guard: a 200-decision
  trace per preset at three seeds, recorded on the base commit (the
  real payload, not a hand-written fixture) and COMMITTED under
  `crates/cloudkitty-core/tests/goldens/` beside the existing goldens
  (`starts_goldens.rs`, `evolution_golden.rs` are the precedent), read
  by an integration test that runs in CI — not an env-var-skipped
  test (analyze M10). Mutation: edit one teacher rung (the wander
  pressure line `< 20.0` at teacher.rs:139 → `< 21.0`) → the trace
  test must go red; this proves the golden can see a teacher change,
  which is the guard's job. (The analyze record's T010 mutation C — a
  read of `ctx.me.needy` inside `Teacher` — is vacuous on a plain
  world and is dropped.)

## D13. Documentation

CHANGELOG `## Unreleased` entry (public voice; no compatibility marker:
stamp, obs-schema, fingerprint and draw order unmoved — a needy seat is
research-only under spec 066). `specs/INDEX.md` already carries the 067
row; the spec's `Status: Draft` stays per house practice. 066's
`contracts/guard-law.md` §2 gains the two mode rows (a 066 contract
touch recorded as such in the PR).

## D14. Recorded redundancy: engine law + behaviour view

The mask is enforced in the engine (D5) and respected in the preset's
own ladder (D6). Test (analyze M11 — the earlier phrasing compared the
verdict with itself): on a probe world, with the behaviour's masked
view and post-filter disabled by a test-only switch, run 300 ticks and
assert the masked needs never DECREASE during `Held` except by the
Article I safeguard (the world's relief, FR-013) — the engine holds the
line without the behaviour's help — and that the count of refused
turns is strictly higher than with the filter on (the filter is advice
quality). This pins which half is the law.

## D15. The refusal reason (analyze M8)

- **Decision**: `RefusalReason::NeedyMasked` (wire name
  `needy_masked`), beside `ConsentDeclined` (events.rs:93–108).
  `action::refusal_reason` (action.rs:442–487) re-derives the reason at
  the stamp; it gains one check in the slot's own order: when
  `validate` would have passed the proposal, consent is asked first
  (the existing block), then the needy verdict — so a friend's refused
  Rest { with: needy } reads `needy_masked`, not `PartnerBusy`, and the
  needy kitty's own refused Eat reads `needy_masked`, not `Other`. A
  proposal validate itself refused keeps today's reasons (validate ran
  first in the slot). No new record type (spec Edge Cases).
- **Inertness**: the variant is emitted only when a needy verdict
  refused, so no pre-feature world ever serializes it; every exhaustive
  `match` over `RefusalReason` (census readers in `cloudkitty-rl`, the
  server's event rendering) gains an arm — found by the compiler.

## D16. The construction guard: state ⇔ a needy configured behaviour (analyze H3)

- **Decision**: a kitty carries `needy` state exactly when its
  CONFIGURED behaviour is a needy name. Enforced at every door: (1)
  `World::try_generate` creates state for exactly those seats; (2)
  `invariants::check` (invariants.rs:31) asserts the pairing every
  tick (`needy.is_some() == needy::is_needy_name(&kitty.behavior)`);
  (3) `Episode::new` (cloudkitty-rl/src/episode.rs:154–183) refuses a
  `control` entry that disagrees with the config seat about needy-ness
  — `Builtin("needy")` on a `teacher` config seat, or `External` /
  `Policy` / another builtin on a needy config seat — with
  `EpisodeError::Config` naming the kitty (the binding defaults unnamed
  kitties to External, so a needy config seat left unnamed is fine:
  the registry seats it); (4) the server's resume (persist.rs:118–129
  re-stamps `behavior` from config) refuses a saved world whose needy
  state disagrees with the configured roster, naming the kitty — a
  needy seat cannot be added or removed on resume. `kitty-eval --brain
  needy` builds its own config, so the hazard guard (066) refuses it
  unless acknowledged; the control-override door is (3).
- **Rationale**: the advance step and the verdict key on the state; a
  policy seat with state would be a covered mind under a mask
  (doctrine rule 12's second guard, spec Edge Cases). Keying them on
  the behaviour string instead would re-read config at every tick and
  still leave a stale-state hole; the invariant is the smallest
  closed guard.

## D17. SC-002 as a holdable comparison (analyze H6)

- **Decision**: "adding a needy seat leaves the master stream
  untouched" cannot hold — `deal_decision_seeds` (world.rs:277–286)
  deals one seed per kitty per tick and `draw_turn_order` (:523–530)
  draws `len − 1` swaps, so roster SIZE moves the master stream. The
  spec's SC-002 now holds the roster fixed and SWAPS one seat's preset:
  a world with kitty k on `teacher` and the same world with k on
  `needy` are identical at generation except k's `behavior` and
  `needy`, and tick identically on every surface except those two
  fields until k's first onset. Test: generate both at one seed with a
  late first onset (edges forcing ≥ 100), tick 100, strip the two
  fields from k in both serialized worlds, assert byte equality.
