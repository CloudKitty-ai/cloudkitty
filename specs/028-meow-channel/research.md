# Research: spec 028 design decisions

Phase 0 output. No NEEDS CLARIFICATION markers existed (all design inputs settled
on the record; three judgment calls clarified 2026-08-08 in spec.md). This file
records the plan-level design decisions, each grounded in recon of the tree at
`d872132`.

---

## R1. The pair type: `Decision { activity: Action, message: Message }`

**Decision**: A new core type crosses the seam:
`Decision { activity: Action, message: Message }` where
`Message = Option<MessageKind>` behind a newtype-free alias (`None` = Silent) —
serialized as the wire string of the kind or absent/null for Silent. The
`Behavior` trait's `decide` returns `Decision`; `JointProposal`,
`ResolvedDecision`, and `KittyTickRecord` carry it.

**Rationale**: `Action` is `Copy` + internally-tagged serde and is carried by ~10
seam/engine sites typed on `(KittyId, Action)` (seam.rs:84,97,117-129,162-164;
world.rs:254-269; behavior/mod.rs:271-353). Growing every `Action` variant with a
message field would poison 40 menu entries and every wire shape; a pair type
changes the *carrier* once and leaves `Action` untouched. `Option<MessageKind>`
keeps `Copy` and gives Silent an unmistakable representation.

**Alternatives considered**: (a) message field on `Action` — rejected, combinatorial
wire churn; (b) side-channel map alongside the proposal — rejected, two things to
keep in sync across the seam is exactly the bug class the seam exists to prevent.

## R2. `Action::Meow` retires by the `Action::Purr` precedent

**Decision**: The `Meow` variant keeps parsing (`"meow"` wire tag) but
`validate` returns `false`; a retired meow proposal lawfully degrades
(fallback/idle per Article IV), mirroring `Action::Purr => false`
(action.rs:336-342, spec 011) and its tests
(`the_legacy_purr_action_is_still_refused`,
`a_retired_purr_proposal_lawfully_resolves_to_idle`).

**Rationale**: External advisors (plugins) may still send old-shape proposals;
Article IV demands they resolve safely, never error. The round-trip corpus test
(action.rs:1998-2012) keeps the wire shape exercised.

**Alternatives**: deleting the variant — rejected: breaks proposal parsing for
old advisors and the corpus contract.

## R3. Message legality is engine law; the mask stays a pure oracle

**Decision**: `message_legal(kitty, kind, tick, config) -> bool` lives in
cloudkitty-core (meow.rs). Rules: `Silent` → always true; want-kinds → armed
(hysteresis state, R4) AND per-kind cooldown clear; `Purr` →
`purr_earned` AND `tick >= purr_cooldown_until` (motor-consistent); `FollowMe` →
cooldown clear only (no grounding predicate exists); `WaitForMe` → false
(head-excluded; the yield rule emits it engine-side, not through the head).
Enforcement at apply: an illegal proposed message downgrades to Silent, recorded
in the tick record; the paired activity is untouched. The RL
`legal_message_mask` derives from `message_legal` by probing, exactly as
`legal_action_mask` probes `validate` (mask.rs:38-59), preserving the spec-014
"no carve-outs" doctrine and the FR-018-analogue structurally: `message_legal`
returns true for Silent unconditionally, so the message mask is never all-zero
by construction.

**Rationale**: mask.rs is deliberately rule-free (the oracle property test
`the_mask_is_a_pure_oracle_and_never_all_zero` enforces it). Putting grounding
in the mask instead of the engine would be the first carve-out and would let
scripted cats bypass the law.

## R4. Hysteresis needs state: `announce_armed` on the kitty

**Decision**: `Kitty.announce_armed: BTreeSet<NeedKind>`
(`#[serde(default, skip_serializing_if = "BTreeSet::is_empty")]`, matching the
`distress_since` wire-hygiene precedent, kitty.rs:286). Updated deterministically
in the environment/needs phase alongside `record_distress` (world.rs:862-895,
same edge-rule style): need ≥ `announce_threshold` → insert; need <
`announce_threshold − announce_hysteresis` → remove; in between → unchanged. No
RNG. Old snapshots deserialize with an empty set (disarmed; re-arms on the next
crossing — harmless, one-window-at-most delay).

**Rationale**: the mask must be a pure function of the start-of-tick snapshot
(the oracle contract), and "was legal last tick" is state by definition. Keying
by `NeedKind` (not `MessageKind`) keeps it meaningful — only want-kinds ground —
and `for_need` (now total, R6) maps it to head rows.

**Alternatives**: deriving armedness from `meow_cooldowns`/recent emissions —
rejected: a cat can be armed without ever having emitted.

## R5. Cooldown reuses `meow_cooldowns` exactly as shaped

**Decision**: The owner's per-cat-per-kind clarification means the existing
`meow_cooldowns: BTreeMap<MessageKind, u64>` (kitty.rs:254) is *already the
right state* — the batch changes its meaning from voluntary courtesy record to
enforced mask input. Emission stamps `tick + recent_window_ticks` uniformly;
`cooldown_for` (meow.rs:76-87) and its urgent branch are **deleted** with the
courtesy trio. `can_meow` survives as the one read point (renamed semantics:
consulted by `message_legal`, no longer "the engine enforces nothing with
this"). Pruning (`prune_meow_cooldowns`) is unchanged.

**Rationale**: zero state migration; pre-028 snapshots carry only old-kind
entries and deserialize into the extended enum untouched; the "harmless courtesy
record" compat test flips meaning but keeps its fixture.

## R6. Vocabulary and order: `HEAD_KINDS`, appended not reshuffled

**Decision**: `MessageKind` grows `WantBath`, `WantSleep` (appended after
`WaitForMe` in declaration order — enum order is not wire-visible;
snake_case strings are). `for_need`/`related_need` become total over all six
`NeedKind`s. The normative head order is a new
`pub const HEAD_KINDS: [MessageKind; 8]` in cloudkitty-rl (successor of
`LEARNED_MEOWS`, observe.rs:58-65): the six current kinds in their existing
normative order, then `WantBath`, `WantSleep`. Message head index 0 = Silent,
indices 1–8 = `HEAD_KINDS` order. The digest iterates `HEAD_KINDS`.

**Rationale**: order is normative for digest and head (the old doc says so
explicitly); appending minimizes diff-vs-doc churn even though the schema bump
would technically allow reshuffling. `LEARNED_MEOWS` is renamed rather than kept:
the "learned" framing is obsolete once scripted cats use every kind.

## R7. Digest v3: coherent 4-tuple, intensity stamped on the `Meow`

**Decision**: `Meow` grows `intensity: f32` (`#[serde(default)]` — old snapshot
meows read 0.0). `emit` stamps want-kinds with `need.get(kind)/100` from the
kitty at emission; `Purr`/`FollowMe`/`WaitForMe` stamp 0.0. Digest per kind:
select the **freshest** audible emitter (max tick; tie-break lower `kitty_id`),
then emit `[recency, dx, dy, intensity]` all from that one meow/emitter —
replacing today's presence-from-freshest + direction-from-nearest blend
(observe.rs:331-359). `MEOW_DIGEST = HEAD_KINDS.len() * 4 = 32`;
`observation_len` 183 → **197**; `OBSERVATION_SCHEMA_VERSION = 3`.

**Rationale**: the incoherence is real and measured (recon confirmed the
min_by_key-on-distance selector); freshest wins because recency is the value the
presence field already privileges, and the emitter position is resolvable
forever (Article II). WaitForMe stays digest-excluded as today.

**Note carried from spec edge case**: mask (start-of-tick snapshot) and stamp
(apply time) agree because actions apply before the needs phase raises needs —
verify in implementation with an assertion-backed test.

## R8. Menu v2 and the message head; schema bumps

**Decision**: `ActionCodec::v1` → `v2`: drop the `LEARNED_MEOWS` extend
(codec.rs:112) → 34 rows; fix the stale `+7` capacity hint (codec.rs:97).
New `MessageCodec` (Silent + `HEAD_KINDS`) with total decode and
encode-inverts-decode, mirroring the activity codec's test style.
`ACTION_SCHEMA_VERSION = 2`, `MASK_SCHEMA_VERSION = 2`.
The old normative table in specs/014's contract stays frozen (historical);
the new tables live in this spec's `contracts/encodings-v2.md`.

## R9. Artifact v2: one trunk, split final layer

**Decision**: `ARTIFACT_VERSION = 2`. Layout unchanged (magic, JSON header, f32
blob) except the final layer's output width MUST equal
`menu_len + message_head_len` (34 + 9 = 43 at default slots); logits split
`[0..34)` activity / `[34..43)` message. `SchemaExpectations` grows
`message_head_len`; the width-mismatch error message follows the byte-frozen
style of policy.rs:169-181. v1 artifacts fail the `artifact_version` check
first — the loud wall (schema-mismatch text already says "no conversion or
compatibility mode").

**Rationale**: a single concatenated output layer keeps the artifact format,
loader, and forward pass single-chain (no header ambiguity about two parallel
layers); the split is a documented index convention, exactly like the menu.

**Alternatives**: two head matrices in the header — rejected: breaks the
contiguous `layers: Vec<[usize;2]>` chain validation for no capability gain in
a stateless MLP.

## R10. Two-head selection: split one u64

**Decision**: In `behavior.rs::select`, sampling draws **one**
`DecisionRng::gen_u64`, splits it into two u32s (high → activity, low →
message), and derives each head's uniform from its own u32. Greedy path draws
nothing (argmax per head), as today. Episode `step` takes per-agent
`(activity_index, message_index)`; py binding exposes
`MultiDiscrete([menu_len, head_len])` and mask reshape `[n, 43]`.

**Rationale**: the design inputs pin this exact shape ("split the one
DecisionRng u64 (two u32s), never a 2nd decision") — the master stream still
deals one u64 per kitty (`deal_decision_seeds` unchanged), and the policy path
keeps a fixed draw shape.

## R11. Mask wire form: one concatenated 43-wide vector

**Decision**: Engine/rl expose `legal_action_mask` (34) and
`legal_message_mask` (9) separately; every serialized surface (AgentInfo.mask,
py info dict, bc `mask.npy`, artifact-facing width checks) carries the
**concatenation** `[activity | message]`, width 43, `mask_schema = 2` with
widths recorded in dataset meta.

**Rationale**: one array keeps episode info, py stacking, and npy shapes
single-tensor (BC slices by the documented widths); two arrays would ripple
through every info-dict consumer for no information gain.

## R12. Config: `[meow]` three keys + sentinel retirement; new dials

**Decision**:
- `MeowConfig` → `recent_window_ticks: u64` (10), `announce_threshold: f32`
  (30.0), `announce_hysteresis: f32` (5.0), plus **five** retired sentinels
  (`Option<_>`, `#[serde(default, skip_serializing)]`): the spec-023 pair
  already there and the newly-retired `courtesy_ticks`,
  `urgent_courtesy_ticks`, `urgent_need_threshold`. `validate_meow` rewritten:
  new-dial range checks (threshold in (0, 100]; hysteresis ≥ 0 and <
  threshold; window ≥ 1) plus loud retirement errors in the frozen
  `ConfigError::invalid("[meow] key", value, "retired by spec 028: …")` style.
  Wait: `deny_unknown_fields` alone would reject unknown keys with serde's
  generic message — the sentinel pattern exists precisely to give the named,
  guided migration error (spec 022/023 precedent), so all three retirees get
  sentinels.
- `ActionEffects` grows `cosleep_drip_relief: f32` (15.0) and
  `cosleep_mutual_relief: f32` (15.0), serde-defaulted (old configs
  behavior-preserving); `validate_actions` tier-1 finiteness loop grows to 12
  dials (message bytes per row, spec 020 D2 loop shape).
- `BehaviorConfig` grows `cuddle_real_threshold: f32` (15.0), serde-defaulted —
  **one** dial shared by the groom response and the cosleep routing (both are
  "my cuddle need is real"; the spec's two gates are one concept, and one dial
  is what the analysis band priced).
- `cloudkitty.toml`: `[meow]` rewritten to the three keys; `[actions]` and
  `[behavior]` gain the new keys with comments; stamp moves (declared).

## R13. Cosleep mutual tier: the contact-census definition

**Decision**: In `apply_sleep_relief` (action.rs:765-792): partner resolved as
today (`is_available_friend` — adjacency only, non-conscription intact); tier =
**mutual** iff the partner's activity `matches!(Sleeping{..} | Resting{..})`,
else passive. Rate = `cosleep_mutual_relief` or `cosleep_drip_relief`; both
parties receive the tier's rate; sleeper's own Sleep relief unchanged. The rest
duet (action.rs:738-745) and groomer payment (action.rs:698-707) keep
`cuddle_relief` untouched — the three-flow coupling is severed.

**Rationale**: "each by own choice" is exactly what the contact-census
instrument already operationalizes ("mutual" = companion itself Sleeping or
Resting) — aligning the engine tier with the measurement instrument means the
pilot's baseline numbers (mutual already 31.5% of serviced ticks) price the
dial without a definition skew.

## R14. Scripted two-channel: deterministic announce, one new rung, routed naps

**Decision**:
- **Announce rule (shared)**: after choosing the activity, a scripted decider
  sets message = the highest-pressure need whose want-kind is `message_legal`
  (armed + cooldown clear), else Silent. Deterministic — the `gen_bool(0.3)` /
  `gen_bool(0.15)` announce lotteries are deleted (their restraint job is now
  the mask's). Playful's chase announce collapses into the same rule
  (`WantPlay` announces when Play is genuinely ≥ threshold — grounding is law
  for everyone). `wait_for_them` returns `(Idle, WaitForMe)` — the yield still
  spends the turn standing (that is its function); only the word rides the
  message channel.
- **Groom response**: new needs_driven rung between opportunism and the potter:
  if own Cuddle ≥ `cuddle_real_threshold` AND the snapshot's audible
  `WantBath` set (self-excluded) is non-empty → target the freshest emitter
  (digest-coherent choice, R7): adjacent → `Groom { target: Some(emitter) }`,
  else step toward. Keys ONLY on `recent_meows` + positions — the imitability
  principle (policy-observable inputs), enforced by a test that gives the
  responder a wet-but-silent neighbor and asserts no response.
- **Cosleep routing**: in the `ReliefSource::Sunbeam` pursue arm
  (needs_driven.rs:166-181): when own Cuddle ≥ `cuddle_real_threshold`, prefer
  the friend — adjacent friend → `Sleep { with: Some(friend) }`; reachable
  friend (within `sunbeam_reach`, reusing the existing reach discipline) → step
  toward; else existing sunbeam logic. Companion behavior unchanged.

**Rationale**: deterministic announce is the honest broadcast the design asks
for ("meow whenever legal"), removes RNG shape variance, and makes the
collector acceptance check (announcing cats are mid-errand) true by
construction — the activity is computed before and independent of the message.

## R15. Distress-tick counter: `WelfareAccumulator` attach, census semantics

**Decision**: Counter state (`ticks_at: per kitty × need`, `episodes`, edge
flag) joins `WelfareAccumulator` (welfare.rs:78-91), updated in `observe`
(post-tick world, `need ≥ thresholds.distress`, episode edge below→at/above) —
the *verbatim* convention of `experiments/tools/distress-census/src/main.rs:162-189`
(the 810/810 instrument). Lands in `WelfareReport` as
`distress_census: Vec<KittyDistressCounts>` → rides `RunOutcome`, kitty-eval
JSON, and one human-panel line. Reported, never gated — no verdict reads it.
Acceptance test: an in-repo comparison run — the accumulator's counts vs an
inline observer implementing the census closure — must agree exactly over
seeded scripted runs (the census tool itself lives out-of-workspace and stays
Experiments').

## R16. Snapshot resume fixture

**Decision**: Before any engine change lands (implementation phase 0), generate
and commit `crates/cloudkitty-core/tests/fixtures/pre-028-world.json` — a
`World` serialized by the pre-028 engine after a few hundred ticks of the
shipped config (meows, cooldowns, distress state, purr state all populated).
Test `a_pre_028_world_resumes_and_runs`: deserialize `World`, tick it N times,
assert invariants — plus a server-side `persist::load_and_validate` variant is
NOT needed (fingerprint changes with config by design; the compat claim is
about serde shape, which the direct deserialize pins).

## R17. Eval/py/tooling surfaces

- kitty-eval exit codes, suite flow, `engine_defaults_sha256` machinery: **no
  structural change**; the stamp value moves (by design, no pinned literal
  exists in-tree — the gate is property-based), record new stamp in CHANGELOG
  entry with `[obs-schema]`, `[rng-sequence]`, `[stamp]`.
- cloudkitty-py: `recent_meows` currently leaks Debug spelling
  (`format!("{:?}")` → `WantEat`) instead of wire names (lib.rs:401-409). The
  binding is being rebuilt anyway (mandatory after engine changes); fix to
  serde wire names **in this batch** since the two new kinds would otherwise
  ship a wart into client-adjacent tooling. Small, contained, noted in the
  contract.
- Global state: `GLOBAL_STATE_SCHEMA_VERSION` (=1) — verify during
  implementation whether the global-state encoding references messages or menu
  size; bump only if it does (recon found no digest coupling; expected
  unchanged).
- FromConfig type-level refactor (017 close-out, "at next harness touch"):
  assessed at tasks time; adopted only if it's a net simplification inside
  files already being edited — otherwise explicitly skipped in the tasks notes.

## R18. What deliberately does NOT change

Server code (serde carries the additive payload), `evals/v1` frozen exams,
`experiments/**` (tools recompile on Experiments' side; seam types stay
public), reward/shaping configs, `[purr]` including `announce_probability`,
`WaitForMe` yield mechanics, `Rest`'s conscription semantics, the fairness and
Article I–III property suites (they must pass unmodified except where menu
width literals appear in test fixtures).
