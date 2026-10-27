# Research: Needy Behaviour Preset

No NEEDS CLARIFICATION markers remain (three owner rulings 2026-10-26 in
spec §Clarifications; the Professor's four changes folded; FR-016 from
her seventh-need note). The decisions below resolve the plan-level
unknowns, each measured against the tree at c9d85721.

## D1. Where the schedule's state lives: on the kitty, in the world

- **Decision**: `Kitty.needy: Option<NeedyState>` with
  `#[serde(default, skip_serializing_if = "Option::is_none")]`
  (kitty.rs:245–300 already carries `pursuit`, `abandoned_chases`,
  `last_relief` with exactly that pattern). `NeedyState` holds the
  preset variant (`hold: bool`), the private sub-stream (`ChaCha8Rng`,
  serialized like `World.rng`), the current episode (ordinal, onset,
  masked set, release tick when released), the next onset, and the
  phase.
- **Rationale**: `Behavior::decide(&self, &DecisionContext)`
  (behavior/mod.rs:84) is stateless and builtins are shared
  `Arc<dyn Behavior>` across kitties (mod.rs:146–150), so a per-seat
  schedule cannot live in the behaviour. The release-at-level rule
  depends on the need trajectory, so the phase is not a pure function
  of (seed, id, tick); state must persist. On the kitty it rides the
  snapshot (save/resume continues the same schedule — spec Edge Cases),
  is visible to the preset as `ctx.me.needy` (its own state, rule 12's
  own-state read), to the engine's verdict, and to every snapshot
  reader (D10). Absent for every non-needy kitty: byte-identical
  snapshots, `GET /state`, decision requests (the request carries `me`
  and the fogged world — a non-needy world's wire is unchanged).
- **Alternatives**: a side table on `World` keyed by kitty id —
  rejected: two homes for one kitty's state and a second serialization
  site; re-deriving at resume by replay — rejected: level release
  depends on the path.

## D2. The sub-stream: domain-tagged ChaCha8 from (world seed, kitty id)

- **Decision**: `needy::sub_stream_seed(world_seed, kitty_id)`: seed
  bytes = world seed LE (0..8), kitty id LE (8..12), the domain tag
  `b"ck-needy-v1"` (12..23), zeros — the exact shape of
  `starts::sub_stream_seed` (starts.rs:94) and
  `init_needs::sub_stream_seed` (init_needs.rs:40, tag
  `ck-initnd-v1`), with the kitty id added so two needy seats draw
  independent streams (spec Edge Cases). The stream is created at
  `World::try_generate` for each needy seat and carried in
  `NeedyState.rng`; every schedule draw (first-onset level, tick within
  level, m, need set, gap) comes from it and nothing else. The master
  `World.rng` and every `DecisionRng` are untouched: SC-002's guard is
  "add a needy seat → every other kitty's decision-seed sequence and the
  master stream's draws are byte-identical".
- **Rationale**: Article V and the 062/065 precedent; one law change =
  one domain-tag bump.

## D3. The schedule law (contracts/needy-law.md §2–§4)

- **Decision**: at generation, draw the first onset: a level index by
  the level weights (cumulative, one `f32` draw), then a tick within
  `[lo, hi)` of that level, flat (`lo + u·(hi−lo)`) or log-uniform
  (`exp(ln lo' + u·(ln hi − ln lo'))`, `lo' = max(lo, 1)`), one `f32`
  draw; then the episode's m by the N weights (one draw) and m distinct
  needs by a partial Fisher–Yates over `NeedKind::ALL` (m draws).
  Phase `Resting` until onset; at onset → `Held`; release per preset;
  at release draw the gap (one draw, flat in `[gap.min, gap.max]`) →
  `Resting` with `next_onset = release + gap`, and draw the NEXT
  episode's m and set at that moment (so the mask is known before it
  applies and the recorder can see "next onset" if a reader wants it;
  the contract pins the draw order). Ordinal increments at each onset;
  0 before the first.
- **Rationale**: the Professor's §Q2 schedule-over-coin; draw order
  pinned so replication needs the seed alone; log-uniform offered as
  the config's `onset_draw` because the Professor names both.

## D4. Advance point: Phase 4, after `advance_needs`

- **Decision**: `self.advance_needy(config)` immediately after
  `self.advance_needs(config)` (world.rs:492) and before
  `record_distress`. The step: for each kitty with `needy = Some`, if
  `Resting` and `tick + 1 == next_onset` → open (ordinal += 1, phase
  Held, and END the kitty's own activity if its governing need is now
  masked — `Activity::governing_need` (kitty.rs:152) is the one
  mapping; ending uses the existing `end_activity` path so a bound duet
  partner's clock clears as today, world.rs:737); if `Held` and
  released per the rule (level: every masked need ≥ L on the
  post-advance needs; hold: `tick + 1 − onset ≥ T`; the level preset
  also releases at T) → `Releasing{by_level|by_limit}` for that tick's
  record, then `Resting` with the next draws (D3).
- **Rationale**: the needs the release rule reads are this tick's
  risen needs; the mask the next decide reads is in place before Phase
  1 of the next tick; the recorder sees the transition on the tick it
  happened.

## D5. Enforcement: the needy verdict at the apply slot + partner availability

- **Decision** (Article IV): `World::needy_verdict(proposer, validated,
  config) -> Action` runs directly after `consent_verdict` at BOTH
  sites (the served loop world.rs:419 and `apply_slot_verdict`
  world.rs:662). It resolves to `Idle` when (a) the proposer is masked
  on the need the action's activity governs (`Action` → `Activity` →
  `governing_need`, kitty.rs:152), or (b) the action names a partner or
  target who is masked on the need the action relieves FOR THEM
  (`action::partner_relief`: Groom{target} → Bath; Play{target} → Play;
  Rest{with} → Cuddle; Sleep{with} → Cuddle — read off
  `apply_activity_effects`, action.rs:777–990). A refusal is recorded by
  the existing refusal stamp (spec 046) as a resolved-to-Idle proposal,
  no new record type (spec Edge Cases). Second half: `available_friend_in`
  (world.rs:1511) returns false when the friend is masked on the duet's
  partner-relief need, so an in-progress duet with a newly masked
  partner degrades to solo exactly as when a friend walks off
  (action.rs:839–863, 877–895: `partner = with_friend.filter(|f|
  world.is_available_friend(..))`), and a groom in progress on a newly
  masked target stops delivering through the same availability read.
- **Rationale**: the consent gate is the precedent for the engine
  judging a proposal about a target's hidden state at the apply slot
  (world.rs:666–705); `apply_activity_effects` is the one place partner
  relief lands, and its availability filter is the one hook that stops
  relief mid-scene without a second mechanism. Duration enforcement
  (world.rs: "inside an activity's minimum the engine continues the
  scene") cannot override the verdict for a NEW proposal because D4
  ends the needy kitty's own masked-need activity at onset.
- **Guard (cross-check, rule 5)**: a test applies each partnered action
  on a probe world and asserts the needs that moved on the partner are
  exactly `partner_relief(action)` — the table cannot drift from the
  effects.

## D6. The preset: `Needy { hold: bool }` wrapping `Teacher::GEN2`

- **Decision**: `behavior/needy.rs`: `pub struct Needy { hold: bool }`,
  `pub const NAME = "needy"`, `pub const HOLD_NAME = "needy_hold"`,
  registered in `with_builtins` (mod.rs:146) after `teacher`;
  `is_builtin() = true`; `teaches() = false` (D8). `decide`: build a
  masked view of `ctx` — `me.needs` with masked needs read as 0 — and
  run `Teacher::GEN2.decide_action` on it (teacher.rs:88, already
  `pub(crate)`), then the post-filter: if the chosen action's governing
  need is masked (luxury play is the case the zeroed view cannot stop:
  masked play reads as low pressure, which is exactly when luxury
  play fires, teacher.rs:120–128), fall through to `wander`/Idle. The
  message channel is the teacher's unchanged (`super::announce(ctx)` on
  the UNMASKED context, teacher.rs:156–158), so calling stays on
  (FR-005, FR-007; owner "A").
- **Rationale**: the three presets stay byte-equal (nothing in
  `Teacher` changes; FR-002 US2 scenario 2); the engine verdict (D5)
  is the law, so the behaviour's filter only saves wasted turns —
  research D14 records the redundancy and its test.
- **Alternatives**: threading an exclusion set through `selection` and
  every rung — rejected: touches the three presets' code paths and
  needs a byte-equality proof per rung.

## D7. Config: `[needy]` optional top-level section, N-sized

- **Decision**: `Config.needy: Option<NeedyConfig>` skip-if-none after
  `welfare_hazard` (mod.rs: the 062–066 attribute pair). `NeedyConfig {
  mix: Vec<f32> (len N), release_level: f32, hold_ticks: u64, gap:
  {min, max}, onset_levels: Vec<u64> (ascending edges, ≥ 6 edges = ≥ 5
  levels; the last edge is the latest first onset), onset_weights:
  Vec<f32> (len = levels), onset_draw: Flat | LogUniform, floors:
  BTreeMap<String, f32> keyed by `NeedKind::as_str()` }`.
  `NeedyConfig::default()` = the coverage design (A4): mix (0.5, 0.2,
  0.15, 0.15, 0, 0) sized by `NeedKind::ALL.len()` at runtime
  (`[0.5,0.2,0.15,0.15]` then zeros to N), release 90, hold 1,500,
  gap 300–1,200, edges [0, 10, 100, 500, 2000, 8000] with weights
  (0.2, 0.2, 0.2, 0.2, 0.2), flat, floors {sleep: engine floor read at
  validation}. Section absent + needy seat → defaults apply (the
  section is parameters, the seat is the hazard). Validation position
  22 (after `validate_welfare_hazard`, mod.rs:1750): FR-008's rules, the
  wrong-length mix error naming N (FR-016), `release_level >
  actions.sleep_floor_off_beam` when sleep is reachable, unknown floor
  key refused by name.
- **Rationale**: FR-008/FR-016; the error-text shape follows 065's
  `[initial_needs].<need>` convention (`[needy].mix`, `[needy].floors.<need>`).

## D8. Teacher eligibility: `Behavior::teaches()`

- **Decision**: `fn teaches(&self) -> bool { true }` on the trait
  (behavior/mod.rs:80–92), `false` for `Needy`;
  `BehaviorRegistry::teaches(&self, name) -> Option<bool>`. The
  collector (`experiments/tools/bc-collect/src/main.rs`: records every
  config behaviour as a demonstrator, provenance at :498–512) skips a
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
  (main.rs ~497–511): an unknown behaviour name is stamped `needs_driven`
  because that is what the engine runs for it, exp-002 families depend
  on that path, and a mistyped needy name runs needs_driven, teaches as
  it does and is stamped truthfully — so the refusal keys on
  `teaches(name) == Some(false)` ONLY; `None` keeps today's fallback
  and stamp; (4) the PR
  body quotes the consent and Experiments reads the collector hunk
  before the owner merges.
- **Rationale**: spec 066 deferred the flag to its first reader; the
  collector is the reader; one `bool` on the trait is the smallest
  surface and lets a future plugin seat declare itself too.

## D9. Hazard registry: two modes, name = preset name

- **Decision**: `HazardMode::{InitialNeeds, Needy, NeedyHold}`, `ALL` in
  that order (guard-law §2 of 066 gains two rows), `name()` returns the
  preset name constants from `behavior/needy.rs` (one home), `activation`
  = the first kitty in config order whose `behavior == NAME`
  (`[[kitty]] 'Mochi' (id 3) behavior = "needy"`). N4 from #469's
  review: a test with an exhaustive `match` over `HazardMode` that
  builds the list and asserts it equals `ALL` — a new variant fails to
  compile until it is placed.
- **Rationale**: spec FR-009; owner "B" (two presets, each its own
  mode).

## D10. Observability: on the kitty in the snapshot + a binding accessor

- **Decision**: FR-012's "lab recorder's per-kitty record" is realised
  as `Kitty.needy` in the world snapshot (every snapshot reader —
  the server API, the census tools that walk `world.kitties` — sees
  mask/ordinal/phase for a needy seat and nothing new for any other
  kitty) plus `ParallelEnv.needy()` in the binding returning
  `[(kitty_id, [need names], ordinal, phase)]` for needy seats only,
  beside `recent_meows()` and `elements()` (cloudkitty-py/src/lib.rs:494,
  :511 — the existing pattern for world-state readers that are not
  observations). The binding's `infos` stay per EXTERNAL agent
  (episode.rs:114–120 and the "only external agents are encoded" rule
  at :500) — unchanged.
- **Rationale**: no observation-schema or `infos` shape change
  (FR-014; non-needy records byte-identical); the accessor is the
  recorder's read; the snapshot is the server's.

## D11. Byte-inertness proof

- **Decision**: with no needy seat: `Kitty.needy` is `None` and skipped;
  `advance_needy` iterates zero kitties; `needy_verdict` returns the
  input when neither party has state (first line); `available_friend_in`
  gains one `is_none()` short-circuit; the config section is absent and
  skip-if-none. Guards: stamp unchanged (recorded before/after), default
  JSON lacks `needy`, a fixed-seed world ticked 300 ticks byte-identical
  to the pre-feature engine's serialized world (the 066 T009 shape),
  the three presets' decisions byte-equal on a seeded world (a golden
  of 200 decisions per preset recorded on the base commit and compared).

## D12. The three presets stay byte-equal

- **Decision**: no edit to `Teacher`'s fields, constants or
  `decide_action` body; `needy.rs` calls into it. Guard: D11's decision
  golden; mutation = make the needy wrapper's masked view leak into the
  teacher path (there is none to leak, so the guard's red is a seeded
  decision-trace comparison against a recorded baseline, red when any
  teacher rung is edited).

## D13. Documentation

CHANGELOG `## Unreleased` entry (public voice; no compatibility marker:
stamp, obs-schema, fingerprint and draw order unmoved — a needy seat is
research-only under spec 066). `specs/INDEX.md` already carries the 067
row (regenerated at specify time); the spec's `Status: Draft` stays per
house practice. 066's `contracts/guard-law.md` §2 gains the two mode
rows (a 066 contract touch recorded as such in the PR).

## D14. Recorded redundancy: engine law + behaviour view

The mask is enforced in the engine (D5) and respected in the preset's
own ladder (D6). Test: on a probe world, with the behaviour's masked
view and post-filter deleted (the mutation), every action the needy
kitty's proposals RESOLVE to is still legal under the mask (the engine
verdict holds) and only the count of refused turns changes — this pins
which half is the law. The preset's half exists so a needy kitty spends
its masked turns servicing other needs instead of being refused.
