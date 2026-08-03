# Feature Specification: Per-Target Play Relief

**Feature Branch**: `025-play-relief-split`

**Created**: 2026-08-02

**Status**: Draft

**Input**: User description: "Per-target play relief split per
HANDOFF-2026-08-02-play-relief-split.md — split the uniform
`play_relief` (20) by play target so the play economy has a value
gradient, solo < cat < bug < greeble (10/20/25/35), with two executable
config guards (ordering, duet ceiling). Owner-decided 2026-08-02; the
generation's second and FINAL planned comparability break, landing
before the exp-002 prereg freezes."

## The break framing *(read first)*

This is a mini spec and a deliberate one: four config keys, one
match-arm split, two validators. It is also the exp-002 generation's
**second and final planned comparability break** — taken now, before
anything has trained, because every invalidated measurement regenerates
in about an hour today and would cost a full re-baseline after the
pilot starts. Experiments is idle on exp-002 until this lands: speed
matters more than polish. Nothing else rides along — no schema changes
(observation dim 182 and codec 40 untouched), no served-world config
edits, no other dynamics changes.

Why the gradient (measured 2026-08-02 on `6d955ab`): post-024, the
play/chase cooperative credit collapsed to 0.1× — every play option
paying the same 20 makes "which play" team-neutral. The chase census
prices the proposed values: greebles are 1.5–2.9× harder per catch
than bugs and 4× scarcer, so at 35 a greeble is an in-the-moment
temptation with no grind exploit, while duets keep a 40-per-tick team
margin. The social dilemma this creates — myopic deciders defect to
greebles, far-sighted ones cooperate — is the training signal exp-002
wants.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The play economy gets a value gradient (Priority: P1)

Today every non-solo play pays the same `play_relief` (20): batting a
bug, wrestling a greeble, and a duet with a friend are
indistinguishable to any decider weighing outcomes. After this change,
play relief routes by target — solo 10, friend 20 (each), bug 25,
greeble 35 — so "which play" is a real decision with a team
consequence: a duet relieves both cats (2×20 = 40 team per tick), a
greeble pays one cat 35, and a far-sighted decider can tell the
difference.

**Why this priority**: This is the change itself — the value gradient
is the reason the spec exists, and exp-002's prereg is holding for it.

**Independent Test**: Drive a headless world placing one kitty into
each play form (solo, duet, bug, greeble); assert the per-tick relief
magnitudes match the four configured values and that the duet still
relieves both parties and stamps the partner serviced.

**Acceptance Scenarios**:

1. **Given** a kitty playing with an adjacent bug, **When** a serviced
   tick lands, **Then** its play need falls by the bug value (default
   25) — not the generic 20.
2. **Given** a kitty playing with an adjacent greeble, **When** a
   serviced tick lands, **Then** its play need falls by the greeble
   value (default 35).
3. **Given** two kitties in a play duet, **When** a serviced tick
   lands, **Then** both parties' play need falls by the kitty value
   (default 20, today's `play_relief`) and the partner is stamped
   serviced — the duet arm's mechanics are byte-for-byte today's.
4. **Given** a kitty pouncing at nothing, **When** a serviced tick
   lands, **Then** relief is `solo_play_relief` (default 10),
   unchanged from today.
5. **Given** default values, **When** any kitty faces the play menu,
   **Then** the gradient holds: solo 10 < kitty 20 < bug 25 <
   greeble 35, and a duet's team total (40) exceeds a greeble (35).

---

### User Story 2 - The guards are executable, not prose (Priority: P2)

The gradient and the duet ceiling are load-bearing economics: if
`greeble ≥ 2 × kitty`, cats *should* ignore each other and the meow
economy dies; if the ordering breaks, the "playing together stays the
better deal" doctrine silently inverts. Both constraints live in
`validate_actions` as hard config errors with messages that teach —
the same doctrine as every ordering guard since spec 017 (executable
guards, tighten-only).

**Why this priority**: Without the guards the values are just numbers
someone can misconfigure; with them the economics are a contract. They
land in the same batch but are independently testable.

**Independent Test**: Feed configs violating each bound (and each
equality boundary) to validation; assert each is rejected with an
error naming the offending key, its value, and the economic reason.
Feed the defaults and the served config's values; assert both pass.

**Acceptance Scenarios**:

1. **Given** a config with `solo_play_relief ≥ play_relief`, or
   `play_relief ≥ play_relief_bug`, or `play_relief_bug ≥
   play_relief_greeble`, **When** it is validated, **Then** it is
   rejected with an error naming the two keys that collide and the
   ordering rule (strict: equality is also rejected).
2. **Given** a config with `play_relief_greeble ≥ 2 × play_relief`,
   **When** it is validated, **Then** it is rejected with an error
   that says why: a duet relieves both cats, so team welfare pays
   2×kitty per duet tick — above this ceiling solo greeble-hunting
   beats social play and WantPlay recruitment loses its value.
3. **Given** a negative or non-finite value in any of the four play
   relief keys, **When** it is validated, **Then** it is rejected
   (the existing finite/≥0 checks extend to the new keys).
4. **Given** the shipped defaults (10/20/25/35), **When** validated,
   **Then** they pass — including the ceiling (35 < 40).

---

### User Story 3 - Existing configs keep their meaning (Priority: P3)

Every config in the wild — the served `cloudkitty.toml`, frozen exam
configs, test fixtures — carries at most `play_relief` and
`solo_play_relief`. All of them must keep parsing with today's
meaning: `play_relief` remains the duet value, the new keys default in
(25/35), nothing needs editing, and no frozen artifact changes bytes.

**Why this priority**: Back-compat is a constraint, not a feature —
but it is independently testable and a review will check it first.

**Independent Test**: Parse a config carrying only today's keys;
assert the new fields take their defaults, `play_relief` lands in the
duet/kitty role, and validation passes. Confirm frozen exam configs
and hash pins are untouched by the diff.

**Acceptance Scenarios**:

1. **Given** a config file naming only `play_relief = 20` and
   `solo_play_relief = 10`, **When** it is parsed, **Then**
   `play_relief_bug = 25` and `play_relief_greeble = 35` default in
   and the config validates.
2. **Given** the served `cloudkitty.toml`, **When** this change lands,
   **Then** the file is not edited (defaults carry the new values) and
   it still parses and validates.
3. **Given** the `/config` endpoint, **When** the new engine serves
   it, **Then** the payload gains exactly two additive keys
   (`play_relief_bug`, `play_relief_greeble`); every existing key
   keeps its name and meaning.

---

### Edge Cases

- **The despawn edge (must be pinned — the effect arm never looks the
  element up)**: elements expire and are removed by the environment
  phase (`world.rs:807`). *(Corrected during implementation:)* the
  slot pipeline already ends a vanished-target scene before its next
  effect lands — `prune_dead_activity` (`world.rs:421-456`) fires at
  the kitty's slot, and
  `world::tests::a_vanished_critter_ends_play_where_it_stands` guards
  it ("relief already granted is kept; none is invented"). So no
  post-despawn tail exists in the canonical loop, on either engine.
  **Pin: a lookup miss pays `solo_play_relief`** — as defense-in-depth,
  not exploit closure: `apply` is a public entry point and must stay
  total, and the effect body must never pay a critter's price for an
  id it cannot resolve. The fallback is unreachable through the loop
  today and priced honestly (pouncing at nothing) if any caller or
  future reordering reaches it.
- **Non-critter element as play target**: unreachable through
  validation (`action.rs:385-388` requires `is_critter()` plus
  adjacency at proposal time), but the effect body stays total: any
  element that is not a bug or greeble routes to the same
  `solo_play_relief` fallback as a missing one. No panic, no silent
  generic value.
- **Equality at the guard boundaries**: the ordering chain is strict
  (`<` everywhere). Today's guard (`validate.rs:551`) allowed
  `solo == play_relief`; the new chain rejects it. No shipped or
  frozen config sits on a boundary (checked: eval configs carry no
  play keys; served config is 10/20).
- **The duet arm and the solo arm do not change**: both-parties
  relief, the serviced stamp on the partner, and the solo value are
  byte-for-byte today's semantics. Only the `Element` arm gains logic.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST relieve the play need per serviced tick
  of a `Playing` activity by a per-target amount: solo (no target)
  pays `solo_play_relief`; a kitty duet pays `play_relief` to **both**
  parties (mechanics unchanged, including the partner serviced stamp);
  an element target pays `play_relief_bug` for a bug and
  `play_relief_greeble` for a greeble, resolved by looking the element
  up by id at effect time.
- **FR-002**: Shipped defaults MUST be `solo_play_relief = 10` (already
  shipped, no change), `play_relief = 20` (already shipped, no
  change), `play_relief_bug = 25`, `play_relief_greeble = 35`
  (owner-fixed 2026-08-02).
- **FR-003**: When the element lookup at effect time finds no element
  for the target id, or finds an element that is not a critter, the
  tick MUST pay `solo_play_relief`. The scene's clock, ending rules,
  and activity state are otherwise untouched.
- **FR-004**: Naming and back-compat (Product's call, exercised here):
  the existing key `play_relief` KEEPS its name and becomes formally
  "the kitty/duet value" (doc comment updated; the handoff's
  `play_relief_kitty` is documentation, not a key). The two new keys
  are `play_relief_bug` and `play_relief_greeble`, each with a serde
  default so absent keys parse. No `deny_unknown_fields`, no aliases,
  no renames: existing configs parse with today's meaning, frozen exam
  configs stay byte-identical and valid, hash pins untouched, and the
  `/config` payload changes only by two additive keys.
- **FR-005**: `validate_actions` MUST enforce the strict ordering
  `solo_play_relief < play_relief < play_relief_bug <
  play_relief_greeble`, superseding the existing solo-vs-play guard
  (`validate.rs:551`, "playing together must stay the better deal" —
  the phrase survives in the new error). Each violation's error names
  the colliding keys and values.
- **FR-006**: `validate_actions` MUST enforce the duet ceiling
  `play_relief_greeble < 2 × play_relief`, with an error message that
  states the economics: a duet relieves both cats, so team welfare
  pays 2×kitty per duet tick; at or above the ceiling, solo
  greeble-hunting dominates social play and meow recruitment loses
  its value.
- **FR-007**: The finite/non-negative validation applied to
  `solo_play_relief` today MUST extend to `play_relief`,
  `play_relief_bug`, and `play_relief_greeble`.
- **FR-008**: The observation layout (dim 182) and the action codec
  (40) MUST NOT change; relief values are dynamics only. The exp-002
  warm-start lever is unaffected.
- **FR-009**: The served `cloudkitty.toml` MUST NOT be edited; the new
  values arrive as defaults. (The served world stays on its old binary
  until the exp-002 winner deploys — sequencing unchanged, FR-010
  posture of spec 024 still in force.)
- **FR-010**: Goldens and long-run guards MUST be reconciled exactly
  once as this break's visible mark: `run-json.golden.json`
  regenerates (values golden), `engine_defaults_sha256` moves, and
  `welfare_longrun` re-clears (play services faster, so happiness
  bounds — floors — are expected to gain margin, but must be
  verified, not assumed).
- **FR-011**: Tests MUST cover: each of the four routing arms at
  default values; the despawn fallback (element removed mid-scene →
  solo value that tick); each ordering-boundary rejection including
  equality; the ceiling rejection at exactly `2 × play_relief`; the
  defaults passing; and a today's-keys-only config parsing with
  defaulted new keys.

### Key Entities

- **`ActionEffects` (config `[actions]`)**: gains `play_relief_bug`
  and `play_relief_greeble` (serde-defaulted); `play_relief` re-scoped
  in documentation to the kitty/duet value; `solo_play_relief`
  untouched.
- **`Activity::Playing { target }` effect arm**: the `Element` case
  gains an effect-time element-type lookup; `None` and `Kitty` cases
  untouched.
- **`validate_actions`**: the solo-vs-play guard grows into the strict
  four-value chain plus the duet ceiling.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a default-config world, one serviced play tick moves
  the play need by exactly 10 (solo), 20 (each duet partner), 25
  (bug), 35 (greeble) — observable via the API's need read-back.
- **SC-002**: A config valid today that names only today's keys parses
  and validates identically after the change; zero config files in the
  repo need editing (the diff touches no `.toml` outside tests).
- **SC-003**: Every guard violation produces a config error naming the
  offending key(s) and value(s); the ceiling error explains the duet
  economics in its message text.
- **SC-004**: After a play target despawns, no tick ever pays a
  critter rate for it: the canonical loop ends the scene with no
  further relief (existing guard,
  `a_vanished_critter_ends_play_where_it_stands`), and a direct
  `apply` caller reaching the arm pays the solo value (new guard).
- **SC-005**: `engine_defaults_sha256` changes exactly once;
  observation dim (182) and codec (40) are byte-identical; frozen exam
  configs and hash pins show no diff.
- **SC-006**: On merge, Experiments' registered prediction becomes
  testable: the play/chase probe class rises off its 0.1× floor on the
  re-run measurement stack (~1 hr). (Verified by Experiments, not this
  spec — but this spec must not block it.)

## Assumptions

- The four values (10/20/25/35) are owner-fixed by the handoff
  (2026-08-02), grounded in the chase census; this spec does not
  re-litigate them.
- The despawn fallback (miss → `solo_play_relief`) is Product's pin,
  and implementation corrected its rationale: the canonical loop
  already ends vanished-target scenes (`prune_dead_activity`), so the
  fallback is defense-in-depth for the public `apply` path, not
  exploit closure. It remains the one place this spec adds semantics
  the handoff left open, and the handoff's premise ("today's arm never
  looks the element up") described the effect body accurately but the
  engine incompletely — the end rules do look.
- Keeping the `play_relief` key name (vs renaming to
  `play_relief_kitty` with an alias) is Product's naming call:
  it satisfies back-compat with zero alias machinery and keeps the
  `/config` wire payload additive-only. The gradient's legibility
  lives in the doc comments and the validators' error messages.
- The strict (`<`) chain intentionally tightens today's guard (which
  permitted equality); no existing config sits on a boundary, and
  tighten-only is house doctrine (spec 017). A second tightening rides
  FR-007: a non-finite or negative `play_relief` was previously
  accepted by accident of comparison semantics (`solo > NaN` is false)
  and is now rejected.
- Scripted behavior does not re-rank: needs_driven selects relief by
  shape, never magnitude (verified — the one `solo_play_relief` read
  in `behavior/selection.rs` is test code, and solo's value does not
  change). Served-world choice structure is unchanged; only scene
  cadence shifts, and only after a future redeploy.
- Client: no work — no visible or wire-level change beyond the two
  additive `/config` keys.
