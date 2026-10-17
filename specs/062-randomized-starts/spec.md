# Feature Specification: Randomized Starts

**Feature Branch**: `product/randomized-starts`

**Created**: 2026-10-15

**Status**: Draft

**Input**: Owner kickoff 2026-10-15 (banked spec; Experiments' requirements
note `experiments/gen2-randomized-starts-requirements-2026-10-15.md`, relayed
on her condition after 061 closed). Ruling basis, her words: "Corner/edge
randomized starts at collection and in every PPO episode" (shelf ruling
2026-09-15, via skeleton §4); "I think as long as placement is deterministic
for seed, we should do that for every unique seed"; legs confirmed: "Starts
should be deterministically randomized by seed yes"; implementation home, her
proposal: "Perhaps we can build this in the engine, and allow overriding in
the toml?"

## Why now

Gen 2 collection and every PPO episode are ruled to run on randomized kitty
start positions (25% edge ring / 5% corner pencil shares, final shares pinned
at the freeze as config). Episode resets happen inside the engine, so no
driver can reach them: collection has a committed stopgap (a driver that
derives one config per rollout), but PPO episodes force an engine home, and
one home then serves collection, episodes, battery legs, the server, and any
future consumer under one law. Experiments' corpus collection is gated on
this mechanism (alongside their own gates); the freeze pin must land as
config, not code.

## Clarifications

### Session 2026-10-15

- Q: Should category shares be per-kitty probabilities or exact per-world
  quotas? → A: Probabilities — each kitty independently draws its category;
  acceptance checks use binomial tolerance (quota sampling, the recorded
  alternative, declined).
- Q: With the placement knob on, what happens to kitties that still carry
  explicit x/y coordinates? → A: Per-kitty override — explicit kitties keep
  their tiles, drawn kitties treat them as occupied; mixed configs are legal.
- Q: On a degenerate world (under 3×3), should share-based placement be
  rejected at load or stay defined? → A: Reject loudly at config load when
  shares are enabled and either dimension is under 3; explicit-starts configs
  on tiny worlds stay legal as today.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A world draws its own starts, lawfully (Priority: P1)

An experimenter turns on share-based placement in a world config, giving an
edge-ring share and a corner share. Every world built from that config with a
seed places each kitty by the ruled law: corner with the corner share,
non-corner edge ring with the remainder of the edge share, interior
otherwise; a uniform free tile within the drawn category. The same seed and
config produce the same starts on any machine, every time.

**Why this priority**: This is the ruled mechanism itself. Without it there
is no engine-native randomized start, and collection, PPO episodes, and legs
stay on per-run stopgaps or wait.

**Independent Test**: Build worlds from one share-enabled config across many
seeds; verify every start is in-bounds, unshared, and classified into its
category by an independent geometry check; verify realized category shares
match the configured shares within sampling tolerance; rebuild any seed and
get identical positions.

**Acceptance Scenarios**:

1. **Given** a config with share-based placement (edge 0.25, corner 0.05) and
   seed S, **When** the world is built twice (same engine build, any
   machine), **Then** both worlds place every kitty on identical tiles.
2. **Given** the same config across many seeds, **When** tick-0 positions are
   classified by an independent classifier (the coverage instrument's
   geometry), **Then** realized corner / non-corner-edge / interior shares
   match the configured probabilities within binomial tolerance, and every
   start is in-bounds and unique.
3. **Given** a share-enabled config, **When** the roster's `[[kitty]]` tables
   are reordered in the file without changing ids, **Then** the drawn starts
   per kitty id are unchanged (the draw keys on kitty-id order, not file
   order).
4. **Given** any consumer that builds worlds — collection, PPO episode
   resets, battery legs, the certification harness, the server — **When**
   it builds from a share-enabled config, **Then** starts come from the one
   engine draw site; no consumer samples positions for itself.

---

### User Story 2 - The baseline stays attributable (Priority: P2)

An experimenter comparing a knob-on world against an explicit-starts world
must be able to attribute every divergence to the starts themselves, never to
a shifted random stream. Configs that do not use the knob — every existing
toml — behave exactly as today.

**Why this priority**: The accurate-diff/baseline-attribution trap. If the
start draw consumed from the main world stream, every downstream element
spawn would shift, and even two worlds with IDENTICAL starts would diverge —
poisoning every A/B that touches this knob. And if existing configs changed
at all, every golden, pin, and shipped config would re-cut for a feature they
do not use.

**Independent Test**: Run a knob-on world and an explicit-starts world whose
explicit starts equal the drawn ones, same seed; compare full-run outputs
byte for byte. Run the existing config suite untouched.

**Acceptance Scenarios**:

1. **Given** a share-enabled config on seed S whose draw yields starts P,
   **When** the same world runs with the knob off and explicit starts set to
   P, **Then** the two runs are byte-identical on every readable surface over
   a full run — element history included.
2. **Given** every existing config (none carries the knob), **When** the
   engine loads and runs them, **Then** behavior is exactly today's: the
   shipped-config sweep and all existing pins stay green without re-cutting.
3. **Given** two worlds on the same seed with different shares (hence
   different starts), **When** they run, **Then** they may diverge freely —
   only the draw's stream isolation is claimed, not post-start trajectories.

---

### User Story 3 - A trace ties to its draw law (Priority: P3)

An experimenter auditing a collected corpus can tie its drawn starts to the
build that drew them, and read what was drawn without re-deriving it: the
collection run's metadata carries the engine identity and echoes each kitty's
drawn position and category.

**Why this priority**: Starts are fully determined by (config, seed, engine
build), and a draw-law change is a versioned break. Today collection metadata
stamps the config and seed but not the engine; without the stamp a corpus's
starts cannot be audited against the law that produced them. The per-kitty
echo is what lets the share acceptance check compare a position's independent
classification against the category the engine actually drew.

**Independent Test**: Run a collection; verify its metadata names the engine
identity and lists, per kitty, the drawn position and category; verify the
echoed positions equal the tick-0 state readback.

**Acceptance Scenarios**:

1. **Given** a collection run from a share-enabled config, **When** its
   metadata is read, **Then** it carries an engine-identity field naming the
   build, and a per-kitty echo of drawn position and drawn category.
2. **Given** the echoed positions, **When** compared against tick-0 world
   state, **Then** they match exactly, and each echoed category agrees with
   an independent classification of the position.

---

### Edge Cases

- A world too small to place the roster under the category constraints (more
  kitties drawn into a category than it has free tiles, after resampling
  within the category is exhausted) fails loudly at world build with an error
  naming the category and the counts — never silently, never by quietly
  spilling into another category.
- Share values outside [0, 1], a corner share exceeding the edge share, or
  shares otherwise inconsistent are rejected at config load with an error
  naming the field and the allowed relation.
- Two kitties drawing the same tile: the later draw resamples a free tile
  within its category; determinism holds (the resample is part of the law).
- A config with the knob on and explicit coordinates on some kitties: the
  explicit kitties keep their tiles (the override), drawn kitties treat those
  tiles as occupied. An explicit tile that itself violates validation fails
  as today.
- Degenerate geometry (a world 1 or 2 tiles on a side, where the edge ring
  is every tile and corners coincide): share-based placement on such a world
  is rejected loudly at config load (both dimensions must be at least 3 when
  the knob is on); explicit-starts configs on tiny worlds stay legal as
  today.
- A seed that produces a long resample run: the draw must terminate — within-
  category resampling walks free tiles, never loops unboundedly.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A config without the placement knob MUST behave exactly as
  today, byte for byte: every existing toml, golden, pin, and the
  shipped-config sweep untouched. Explicit `[[kitty]]` x/y stays the default.
- **FR-002**: The config MUST offer a knob that selects share-based placement
  and carries the share values in the config itself (an edge-ring share and a
  corner share), so the Gen 2 freeze pin lands as a config diff, not code.
  Exact spelling is this spec's call at design time.
- **FR-003**: Drawn starts MUST be a pure function of (world seed, world
  dimensions, shares, roster in kitty-id order) under the versioned draw law:
  same seed + same config + same engine build = same starts, on any machine.
  File order of the roster tables MUST NOT affect the draw.
- **FR-004**: The draw MUST NOT consume from the main world random stream. It
  draws from a sub-stream keyed off (world seed, a fixed domain tag), so a
  knob-on world and an explicit-starts world whose explicit starts equal the
  drawn starts are byte-identical on the same seed, element history included.
- **FR-005**: Placement geometry MUST match the coverage instrument's
  definitions: the edge ring is the outermost tile ring; the four corner
  tiles count as inside the edge ring. Per kitty, independently: corner with
  probability p_corner, non-corner edge with p_edge − p_corner, interior
  otherwise; uniform over free tiles within the drawn category; a collision
  resamples within the category. Shares are probabilities, not quotas.
- **FR-006**: Existing start validation (in-bounds, no shared tile) MUST hold
  for drawn starts. A placement the law cannot satisfy fails loudly at world
  build; invalid share values, and shares enabled on a world with either
  dimension under 3, fail loudly at config load.
- **FR-007**: There MUST be exactly one draw site, in world generation; every
  consumer (collection, PPO episode resets, battery legs, certification
  harness, server) inherits it. No consumer samples positions for itself.
- **FR-008**: With the knob on, a kitty carrying explicit coordinates MUST
  keep them; kitties without explicit coordinates are drawn, treating pinned
  tiles as occupied.
- **FR-009**: Collection-run metadata (bc-collect's meta.json) MUST gain an
  engine-identity field tying a trace's drawn starts to the draw law's build,
  matching the identity the certification harness already stamps.
- **FR-010**: Collection-run metadata MUST echo, per kitty, the drawn
  position and the drawn category, so audits compare the engine's draw
  against independent classification without re-deriving it.
- **FR-011**: The draw law's sub-stream derivation MUST be documented
  precisely enough that an independent implementation can reproduce exact
  positions from (seed, dimensions, shares, roster) — position-level
  auditing, not law-level only.
- **FR-012**: A change to the draw law is a versioned break: the law's
  version MUST be identifiable from the engine identity (FR-009); the law
  never changes silently under a stable identity.

### Key Entities

- **Placement knob**: the config surface selecting share-based placement and
  carrying the share values; absent means today's explicit-starts behavior.
- **Start category**: corner, non-corner edge ring, interior — the coverage
  instrument's geometry, shared by the draw and every classifier that reads
  it.
- **Draw law**: the versioned pure function from (seed, dimensions, shares,
  roster order) to positions, including category draw, within-category
  uniformity, and collision resampling.
- **Start sub-stream**: the domain-separated random stream the draw consumes,
  keyed (world seed, fixed tag), isolated from the main world stream.
- **Provenance stamp**: collection metadata's engine identity plus the
  per-kitty echo of drawn position and category.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Over many seeded draws from one share-enabled config, realized
  category shares match the configured shares within binomial tolerance,
  read off tick-0 world state by an independent classifier.
- **SC-002**: Every drawn start, across the same sweep, is in-bounds, unique
  within its world, and classified into a lawful category — zero violations.
- **SC-003**: One full run, same seed: knob-on vs knob-off-with-explicit-
  starts-set-to-the-drawn-starts are byte-identical on every readable output
  surface (collection arrays byte-equal, trace lines equal).
- **SC-004**: The entire existing test and config surface passes unchanged:
  shipped-config sweep green, no golden or pin re-cut in this feature's PRs.
- **SC-005**: An independent reimplementation of the documented draw law
  reproduces the engine's exact positions on sampled (seed, config) pairs.
- **SC-006**: A collection run's metadata carries engine identity and the
  per-kitty draw echo, and the echo matches tick-0 state exactly.

## Design-doctrine check (CLAUDE.md rule 8)

This spec scripts world setup (where kitties start), so each doctrine rule
was checked before planning:

- **Rule 9 (frozen models / seed pins) — moved choices.** The domain-
  separated sub-stream (FR-004) exists because inserting draws into the main
  stream would shift every downstream element spawn: worlds with identical
  starts would diverge, the baseline-attribution trap. FR-001's knob-off
  byte-identity means no existing pin or golden re-cuts: the change
  attributes every divergence it causes (none, knob off), the 048/054
  precedent satisfied trivially.
- **Rule 8 (scarcity / variance) — moved a choice.** Randomized starts are
  placement variance on the collection and training side. The served config
  stays the majority episode: the knob ships absent from every served toml
  (FR-001), and turning it on anywhere served would be a deploy ruling, not
  this spec's.
- **Rule 5 (teacher sees what the student sees) — checked, moved nothing.**
  Starts change no observation; positions are already in view. The teacher-
  side coping package (waypoint start-index, beacon pinning) is explicitly
  out of scope, designed separately.
- **Rules 1–4, 6, 7, 10–12 — checked, moved nothing.** No reward term, no
  price, no spoken word, no behavior build, no gate or welfare bar moves:
  start placement is world setup before tick 0, and relief availability
  (rule 12) is untouched — validation still guarantees lawful placement.

## Assumptions

- The per-kitty draw echo (FR-010) is included as a requirement rather than
  the note's nice-to-have: it is cheap and it is what makes Experiments'
  category-level acceptance check runnable.
- The collection tool's metadata (FR-009, FR-010) lives in Experiments'
  lane; their requirements note explicitly asks this spec to close the gap,
  so the implementation PR carries a cross-lane reason citing it.
- The coverage instrument (`coverage_read.py`) is the reference geometry;
  the spec adopts its definitions rather than inventing parallel ones.
