# Feature Specification: Worldgen Placement — the Guaranteed Lake and Edge-Avoiding Spawns

**Feature Branch**: `027-worldgen-placement` *(stacked on `026-in-water-obs`)*

**Created**: 2026-08-05

**Status**: Draft

**Input**: User description: "Worldgen placement batch: the mandatory
2×2 lake and edge-avoiding spawns (pre-exp-003 batch items 3a+3c+5
from HANDOFF-2026-08-05-pre-exp-003-world-batch.md; item 3b is
WITHDRAWN by the owner — do not build it). Promote SPREAD_CANDIDATES
and TTL_JITTER to config (Article VI), fix the stale per-type-cap
comment, document that element rule.max is validation-only."

## The batch framing *(read first)*

The second and final half of the pre-exp-003 world batch: the changes
that move *where things are* rather than what a kitty knows or pays.
Both land before exp-003's prereg freezes, because both move exp-003's
dependent variables — a 2×2 lake changes water topology directly, and
edge avoidance moves resources toward the middle where cats travel
more. Landing them inside the frozen window would make a pass or fail
unattributable (handoff §4).

Two design constraints are inherited from spec 026's hard lesson and
from the handoff:

- **Frozen exams must keep validating.** `evals/v1/scarcity.toml`
  runs `water.min = 1` and can never be edited. So the lake guarantee
  is **conditional, not universal**: it activates when a world's
  water minimum can afford it (≥ 4) and stays silently inactive below
  that. No frozen config gains a new way to fail.
- **The lake spends welfare, it doesn't earn it** (handoff §3d). Four
  of the shipped world's eight water tiles (the engine default
is five) condense into one square,
  lengthening the mean trip to a drink. Element budgets must NOT be
  lowered on placement gains until `experiments/screens/` has run on
  the merged engine. This spec changes placement only — every
  `min`/`max` stays exactly as it is.

Item 3b — a hard minimum separation between same-type elements — was
**proposed and withdrawn the same day (owner, 2026-08-05)**. It stays
unbuilt deliberately: `pick_spread_tile`'s best-of-8 sampling is a
*preference* that can never fail, and a hard constraint could make an
Article I safeguard spawn unsatisfiable. Recorded here so it is not
helpfully reintroduced.

## Clarifications

### Session 2026-08-05

- Q: Should the lake guarantee be unconditional (validation-refusing
  sparse worlds) or conditional on the water budget? → A: Conditional
  (activates iff water minimum ≥ 4), decided by the same rule that
  re-set 026's ceiling: a frozen, un-editable exam (`scarcity.toml`,
  water min 1) must never gain a new validation failure.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Every well-watered world has a lake (Priority: P1)

A world whose water minimum is at least 4 always contains at least one
2×2 square of water tiles — a lake. The lake is placed by a dedicated
step that deliberately clusters, where ordinary spawns deliberately
spread; the remaining water beyond the lake's four tiles spreads as
today. Watchers get merged shorelines worth looking at (the 008 pond
renderer rewards adjacency), and — post-026 — lake *width* makes
crossing-versus-skirting a real decision, priced per wet tile.

**Why this priority**: The headline change; exp-003's water topology
depends on it, and it is the reason the batch exists beyond dials.

**Independent Test**: Generate many seeded worlds at the default
config; every one contains at least one 2×2 all-water square. Generate
worlds with water minimum < 4; none fails validation, none guarantees
a lake.

**Acceptance Scenarios**:

1. **Given** the shipped world (water min 8) or the engine defaults
   (min 5) — both past the threshold — **When** a world is
   generated from any seed, **Then** at least one 2×2 square of water
   tiles exists.
2. **Given** a config with water minimum < 4 (e.g. the frozen scarcity
   exam's 1), **When** it validates and generates, **Then** validation
   passes, generation succeeds, and no lake is required.
3. **Given** the lake's four tiles, **When** kitties path across the
   world, **Then** every lake tile is passable — a kitty wades when
   water is the only way forward, exactly as for scattered water.
   Traversability is invariant (spec 010 pin; Article I relief
   assumes it).
4. **Given** the same seed and config, **When** the world is generated
   twice, **Then** the lake sits at the same place — all placement
   randomness flows through the master RNG (Article V).
5. **Given** water configured with a TTL (non-default), **When** lake
   tiles expire and the restock path next runs, **Then** the guarantee
   re-forms by the same rule minimums follow: restored when room
   allows, carried to the next environment phase when it does not.
6. **Given** any world state, **When** an Article I safeguard spawn
   fires, **Then** lake logic never delays, blocks, or fails it — the
   safeguard path is untouched.

---

### User Story 2 - Spawns prefer the interior (Priority: P2)

Ordinary element spawns become less likely to land on the map's
perimeter ring. The preference is a weighting inside the existing
best-of-N candidate draw — never a hard exclusion, so a spawn (in
particular a safeguard spawn) can never fail for want of an interior
tile. Resources drift toward where cats actually travel, shortening
the mean trip — the placement gain that carries the owner's welfare
argument now that 3b is withdrawn.

**Why this priority**: The second dependent-variable mover; sized
against small worlds because 20×20 (perimeter 19% of tiles) is the
live design target.

**Independent Test**: Over many seeded generations at defaults, the
share of elements on the perimeter is well below the perimeter's area
share; with the weighting configured to zero, the distribution matches
today's.

**Acceptance Scenarios**:

1. **Given** default config, **When** many worlds generate, **Then**
   perimeter tiles hold a clearly smaller share of elements than their
   area share (measurably below it in aggregate), and no world fails
   to place its minimums.
2. **Given** the weighting set to 0, **When** worlds generate, **Then**
   spawn placement behaves exactly as before this spec (the knob
   fully disables the preference).
3. **Given** a crowded world where only perimeter tiles are free,
   **When** a spawn (ordinary or safeguard) fires, **Then** it lands
   on the perimeter — preference, never prohibition.
4. **Given** the combined constraints (lake + edge preference +
   configured minimums), **When** a config describes a world they
   cannot jointly satisfy at generation, **Then** startup validation
   refuses it with an error naming the field and the arithmetic —
   spawn time never discovers what validation could have said.

---

### User Story 3 - The last spawn constants move to config (Priority: P3)

The two remaining simulation numbers living in code — the best-of-N
candidate count (8) and the TTL jitter half-width (100) — become
configuration with those defaults, closing the Article VI gap the
config header's "every number the simulation uses lives in this file"
claim currently overstates. At defaults, behavior is bit-identical:
same values, same number of RNG draws, same worlds from the same
seeds *as this spec's own baseline* (the lake and edge steps having
already moved the sequence relative to pre-027).

**Why this priority**: Cheap to close while this exact code is open;
an inconsistency between the constitution's config doctrine and the
code is worth removing, not worth its own spec.

**Independent Test**: Defaults produce the same world as the same
seed immediately before this change (with US1/US2 features held
constant); changing either knob changes worlds and validates its
bounds.

**Acceptance Scenarios**:

1. **Given** a config that never writes the new keys, **When** the
   world boots, **Then** the effective values are 8 and 100 and
   `GET /config` reports them.
2. **Given** a candidate count below 1 or a non-finite/absurd jitter,
   **When** validation runs, **Then** the config is refused with the
   field named.
3. **Given** the stale comment above the water rules claiming the
   per-type cap is "32 for this world", **When** an operator reads
   the shipped config, **Then** it states the true cap arithmetic
   (area/32 — 18 at 24×24) and no longer names a number that went
   stale when the world shrank.
4. **Given** the element rules' `max` fields, **When** an operator
   reads their documentation, **Then** it says plainly that `max` is
   read only by config validation — the standing population is the
   minimums, and `min` is the real knob (spec 024-era finding,
   previously unwritten).

---

### Edge Cases

- **Lake vs. one-per-tile**: the lake is four ordinary water elements
  on four adjacent tiles — no multi-tile element type, no change to
  element identity, observation slots, or pathing. `free_element_tiles`
  semantics untouched.
- **Lake placement is edge-weighted too**: the lake's anchor draw
  applies the same interior preference as ordinary spawns, so the
  guaranteed feature doesn't pin itself to a corner the rest of the
  system is steering away from. Like every preference here, it yields
  when only edge space fits.
- **No free 2×2 at restock** (TTL worlds, crowded moments): the lake
  obligation carries to the next environment phase, exactly like an
  unmet minimum — it never overwrites, stacks, or evicts elements.
- **Boundary between guarantee tiers**: water minimum exactly 4 means
  the entire standing water population is the lake; minimum 3 means no
  guarantee. Both generate; the boundary is documented at the knob.
- **Resumed worlds are retrofitted**: a pre-027 snapshot resumed
  under this engine with water minimum ≥ 4 gains its lake on the
  first environment phase — up to four water tiles spliced into the
  live world, mid-life, once. Intended: the guarantee holds for every
  running world, not just freshly generated ones. The served world
  (water min 8) will visibly grow a lake at the post-exp-003 rollout;
  in permanent-water worlds the retrofit can leave the standing water
  count above the minimum (the square completes whole), which is
  lawful — the population claim "standing = minimums" is exact only
  for freshly generated permanent-water worlds.
- **Seeded-world continuity breaks, on purpose**: the lake step and
  the edge weighting change the master-RNG draw sequence, so every
  seeded world regenerates differently and the exp-002 family
  byte-stability check will flag it. Expected — those results are
  pinned to the old engine; nobody should chase the flag.
- **The engine-defaults stamp moves again**: new config keys serialize
  into the defaults hash. The batch's single re-baseline (handoff §4)
  happens after both specs merge — this spec must land inside that
  window, not after the freeze.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: World generation MUST guarantee at least one 2×2
  all-water square whenever the configured water minimum is ≥ 4, via a
  dedicated placement step that clusters deliberately (bypassing the
  spread preference) and draws all randomness through the master RNG.
- **FR-002**: The lake guarantee MUST be maintained by the restock
  path under the same semantics as minimums: when expiry breaks the
  square, it re-forms when room allows and carries over when it does
  not. Worlds with water minimum < 4 MUST validate, generate, and run
  with no lake and no error.
- **FR-003**: Lake tiles MUST remain ordinary, passable water
  elements: one element per tile, existing traversability and relief
  semantics untouched, Article I safeguard spawns never delayed or
  blocked by lake logic.
- **FR-004**: Ordinary spawn placement MUST apply a configurable
  interior preference — a weighting within the existing best-of-N
  draw that reduces perimeter placements. It MUST be a preference
  (some candidate always wins), MUST be disableable (weight 0 restores
  today's behavior exactly), and MUST apply to the lake anchor as
  well.
- **FR-005**: Config validation MUST refuse, at startup and naming the
  field, any configuration whose placement constraints are jointly
  unsatisfiable at generation (the lake's 2×2 against world size and
  the element budget), alongside the existing per-type area/32 bound.
  Spawn time MUST NOT be the first place an impossible world fails.
- **FR-006**: The best-of-N candidate count (default 8) and the TTL
  jitter half-width (default 100 ticks) MUST become configuration
  keys with documented defaults and validated bounds. At defaults,
  spawn behavior MUST be unchanged: same values, same RNG draw
  counts.
- **FR-007**: The shipped config's stale per-type-cap comment MUST
  state the real arithmetic (area/32; 18 at 24×24), and the element
  rules MUST document that `max` is read only by validation — the
  standing population is the minimums.
- **FR-008**: Item 3b (minimum same-type separation) MUST NOT be
  built; this spec records the withdrawal so the preference-never-
  constraint design of spread sampling survives future readers.
- **FR-009**: Element budgets (`min`/`max` for every type) MUST NOT
  change in this spec.

### Key Entities

- **Lake**: four ordinary water elements occupying a 2×2 tile square;
  a placement pattern, not a new element kind.
- **Interior preference**: a configured weight applied against
  perimeter candidates inside the best-of-N spawn draw.
- **Spawn dials**: the candidate count and TTL jitter, now
  configuration with their long-standing values as defaults.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of worlds generated at the default config (across a
  large seeded sample) contain at least one 2×2 all-water square; 0%
  of sub-4-minimum configs (including the frozen scarcity exam) fail
  validation or generation.
- **SC-002**: At defaults, the aggregate perimeter share of spawned
  elements over a large seeded sample is measurably below the
  perimeter's area share; with the weight at 0, placement is
  distributionally identical to pre-027 behavior.
- **SC-003**: A config omitting the new keys reports candidate count 8
  and jitter 100 on `GET /config`; every shipped TOML in the sweep
  (root, evals, experiments, specs) still validates.
- **SC-004**: Full workspace suite green; determinism holds (same
  seed + config → identical world, lake included); no Article I–III
  property test weakens; the safeguard-spawn tests pass unmodified.
- **SC-005**: The exp-002 family byte-stability check flags the
  regeneration difference (expected), and nothing else in CI does.

## Assumptions

- **Interior-preference default**: the handoff sets no magnitude. The
  spec assumes a modest default penalty (documented at the knob, and
  chosen in plan against measured perimeter shares) rather than a
  dramatic one: the goal is drift toward the interior, not a cordon —
  and `experiments/screens/` measures the welfare effect on the merged
  engine before any budget decision leans on it. Reversible by
  config.
- **Guarantee threshold at 4** = the lake's own size: the smallest
  water budget that can afford the square. Not configurable — it is
  arithmetic, not policy.
- **Stacked on 026**: this branch builds on `026-in-water-obs`; the
  two merge in order and the engine-defaults stamp settles once, after
  both.
- **Experiments owns the aftermath**: re-baseline, anchor re-measure,
  and the screens run on the merged engine (handoff §4), plus the
  trainer/tooling generation bumps already reported from 026's review.

## Out of Scope

- Item 3b (minimum same-type separation) — withdrawn; not built.
- Any element budget change (handoff §3d holds until screens run).
- Rivers (1-wide water chains) — brainstorming only; `groupWaterTiles`
  4-adjacency and shore rounding make them a Client-side project of
  their own (noted in the client-v3 record).
- Geometry changes (world stays 24×24 through exp-003; 20×20/22×22 are
  post-exp-003 owner decisions with screens already landed).
- evals/v2 small-world exams (separate sitting, held-out doctrine).
