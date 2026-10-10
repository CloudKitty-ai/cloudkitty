# Feature Specification: Gen 2 Observation Schema Bump

**Feature Branch**: `product/schema-bump`

**Created**: 2026-10-09

**Status**: Draft

**Input**: User description: "schema bump package" — the Gen 2 schema bump
package relayed from the Experiments session on the owner's word
(2026-10-09, "Relay to spec to product"), one of four Gen 2 build-phase
specs, all landing before corpus collection (prereg skeleton §10).

**Ruling sources** (records beat this spec on any discrepancy):
`experiments/gen2-kickoff-rulings-2026-10-07.md` (K§2 clock),
`experiments/gen2-sitting-rulings-2026-10-08.md` (S§1 visibility, S§2
riders), `experiments/gen2-prereg-skeleton-2026-10-09.md` §3,
`experiments/fog-gen1-shakeout/GEN2-INPUTS.md` (distance-encoding rider,
owner "Approved" 2026-09-25; identity ruling 2026-09-13; doctrine rule 5
view holes).

## Why one wall

Gen 2 hides other cats' needs, adds a self-identity block, re-encodes
every spatial feature size-invariantly, and drops the clock. Each alone
would invalidate every trained policy's input contract; together they
cost one schema version bump, one re-record, one retrain ("the lineage
pays one wall, not two" — GEN2-INPUTS). Everything below rides that
single wall. The served Gen 1 world and its policies are untouched:
they stay on schema 5.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A Gen 2 mind observes a size-invariant, hidden-needs world (Priority: P1)

The Experiments thread collects a fresh teacher corpus and trains the
Gen 2 trunk. Each mind's observation now: encodes every distance the
same way at 20×20 and 100×100; shows the mind its own identity (how fast
its needs rise, its comfort slack, its consent line, its favourites); and
shows it about each friend only what a real cat could perceive —
position, activity, coat state (bath), calls, and purring — never the
friend's internal need levels, happiness, or traits.

**Why this priority**: this is the generation's input contract; corpus
collection and all training wait on it (skeleton §10 step 1 before
step 2).

**Independent Test**: encode observations for a seeded world and verify,
cell by cell against the new contract: the row layout carries no cell
for hidden friend fields while visible ones carry state; the identity
block matches the cat's configured traits; spatial cells carry bearing +
two-scale magnitude under the frozen constants; no clock cell exists.

**Acceptance Scenarios**:

1. **Given** a friend inside the vision disc with hunger 95, happiness
   12, and bath 80, **When** the observer's row for that friend is
   encoded, **Then** the row carries the friend's position, activity,
   bath, message block, and purr state, and the row layout contains no
   cell for the other five needs or happiness (hidden fields are
   removed, not zeroed).
2. **Given** the same world laid out at 20×20 and at 100×100 with a
   friend at the same bearing and distance, **When** both observations
   are encoded, **Then** the friend's spatial cells are identical —
   bearing exact, near-field magnitude equal, far-field magnitude equal.
3. **Given** a cat whose configured need-rate multipliers, comfort
   slack, consent line, and favourite weights differ from the defaults,
   **When** its own observation is encoded, **Then** its self block
   carries exactly those values, and no other cat's observation carries
   them anywhere.
4. **Given** any two ticks of a stationary world, **When** observations
   are encoded, **Then** no cell varies with the episode clock (the
   clock input no longer exists).

---

### User Story 2 - Downstream readers survive the bump by name, not by number (Priority: P2)

Every consumer that today addresses observation or action cells by raw
index — the trainer's gate reads, certification readers, probe scripts —
resolves cells through a schema-version-keyed column map published as
part of the schema artifact, so the Gen 2 bump (and any later one) moves
indices without silently corrupting a reader.

**Why this priority**: raw indices break SILENTLY at a bump — a reader
pointed at the wrong column still returns numbers. The map must ship
with the schema so readers can flip before any Gen 2 artifact exists.
(The flips themselves in `experiments/` are the Experiments thread's
lane; this spec delivers the map they flip onto.)

**Independent Test**: look up every published cell name for schema
version 5 and for the new version; verify the version-5 lookups
reproduce today's layout exactly and the new-version lookups match the
new contract; verify an unknown version or cell name fails loudly rather
than returning a default.

**Acceptance Scenarios**:

1. **Given** the published column map keyed by schema version, **When**
   a reader asks for a named cell under version 5, **Then** it receives
   today's index for that cell, unchanged.
2. **Given** the new schema version, **When** a reader asks for a named
   cell that moved, **Then** it receives the new index, and asking for a
   version or name the map does not carry is an error, never a silent
   default.
3. **Given** the Python binding, **When** a downstream script imports
   the map, **Then** the map is reachable alongside the existing schema
   version constants without reading Rust source.

---

### User Story 3 - Future compartments land without a second wall (Priority: P3)

The banked dirt-package arm (S§2 rider 3) later gives bath need a world
cause. Two observation cells are reserved for its dirt compartments at
THIS bump: zero until armed, and provably contributing nothing to a
trained mind's behavior until then, so the arm lands as a flag flip
rather than another schema wall.

**Why this priority**: valuable insurance, but nothing in Gen 2's
trunk reads these cells; the generation ships whole without the arm.

**Independent Test**: the e_col/F-058 check-1 proof form (the
present-vs-absent bit-compare is not constructible once the layout
includes the cells): (a) a property test shows both cells read exactly
0.0 over randomized worlds and configs, and (b) no encoder write path
can reach the reserve range — the only write is the reserve push
itself, so nothing upstream can contribute through them.

**Acceptance Scenarios**:

1. **Given** any world state with the dirt reserve unarmed, **When** an
   observation is encoded, **Then** both reserved cells are exactly 0.0.
2. **Given** the inertness proof, **When** it runs pre-freeze, **Then**
   it establishes non-contribution (constant-zero over the property
   battery AND no write path into the reserve range), not mere
   zeroness in sampled states — the F-058 check-1 bar.

---

### Edge Cases

- Bearing at zero distance: a friend or element on the observer's own
  tile has no direction; the bearing cells need a defined value there
  (the contract pins it; it must be the same value in training and
  serving).
- A heard-but-not-seen friend: the row's spatial cells point at the
  last audible meow position under the SAME new encoding; the removed
  hidden fields have no cells on heard rows either, and the fields a
  heard row cannot know (bath, activity, context bits, scene age) are
  masked to zero as in schema 5.
- Vacant rows (roster smaller than the row count) stay all-zero,
  including the new cells.
- At 20×20 the longest Manhattan distance (38) still caps the linear
  cell near but under 1; at 100×100 most cross-map distances clamp it
  at 1 — the log cell is what keeps them ordered. Both behaviors are
  intended and the contract states them.
- A visible entity's Manhattan distance can exceed the Euclidean
  vision radius (FR-001a): the distance cells are never clamped or
  validated against r, and a test pins the overshoot as correct.
- A cat adjacent to two walls (a corner) carries two zero
  distance-to-wall cells; zero is a legal, meaningful wall distance and
  must not collide with a "missing" sentinel.
- Gen 1 policies: a schema-5 artifact presented to a Gen 2 world (or
  vice versa) must be refused by the existing version pin, never
  reinterpreted.
- The two reserved dirt cells are additive at the END of their block
  (the e_col pattern) so arming them later moves no existing index.

## Requirements *(mandatory)*

### Functional Requirements

**Distance encoding (owner "Approved" 2026-09-25, GEN2-INPUTS rider)**

- **FR-001**: Every spatial feature in the observation MUST decompose
  into exact unit bearing (the ruled wording: "unit direction (dx/d,
  dy/d), never clamped" — owner "Approved" 2026-09-25) plus a
  two-scale magnitude: a near-field cell (distance / 40, clamped at 1)
  and a far-field cell (log1p(distance) / log1p(400)). This applies to
  kitty rows, element slots, and the element memory alike. **d is
  MANHATTAN throughout** (d = |dx| + |dy|; the bearing pair is the L1
  unit vector, |dx/d| + |dy/d| = 1): the ruled form preserved under
  the walk-cost metric — bearing stays lossless at any distance, the
  two scales and the frozen constants stand (pin confirmed with
  Experiments 2026-10-09: F-052/F-053's evidence is metric-agnostic
  and was collected under schema 5's Manhattan cells).
- **FR-001a**: No consumer may clamp, validate, or bound the distance
  cells at the vision radius: a VISIBLE entity's Manhattan distance
  can exceed the Euclidean vision radius (e.g. dx=2, dy=3 inside an
  r=4 disc). The contract states this and a test pins it, so the
  "overshoot" is never later "fixed" into a clamp.
- **FR-002**: The constants 40 and 400 MUST be frozen literals of the
  schema (the spec-049 pattern: never derived from config at
  observation time; a config change must not move an observation's
  meaning).
- **FR-003**: The two fractional self-position cells MUST be replaced
  by four distance-to-wall cells (N/E/S/W), absolute tiles under the
  linear /40 normalizer and cap only. The observation becomes fully
  egocentric; global self-localization is a known, accepted loss (no
  consumer exists).
- **FR-004**: Time normalizers (scene age /24, staleness /40) MUST be
  untouched by this bump.

**Visibility: hidden needs, five of six (S§1, amended by S§2)**

- **FR-005**: Another cat's row MUST carry only: presence/position
  (spatial cells per FR-001), activity (including partner flag and
  target bit), BATH need, the per-speaker message block (digest), purr
  state, and the scene/water/sunbeam context bits it carries today.
- **FR-006**: Another cat's row MUST NOT carry: its other five need
  values, its happiness, any distress flag, or any trait/identity
  field. Hidden fields are REMOVED from the row layout — no cell
  exists to leak into, the same "come out" form as the view-hole
  strips — so the leak audit (FR-007a) is an enumeration of the
  layout, not a runtime zero-check.
- **FR-007**: The observer's OWN block keeps its full state: all six
  needs, happiness, distress flags, and the identity block (FR-008).
  Hiding applies to knowledge of OTHERS only.
- **FR-007a**: The bump MUST include a field-level leak audit of the
  friend-row contract: an enumeration of every row cell against the
  visible-set ruling, recorded in the spec's contract, confirming
  nothing else leaks (skeleton §3 blank: "audit at spec").

**Identity block, self-only (owner ruled 2026-09-13)**

- **FR-008**: The self block MUST gain the cat's own identity vector:
  six need-rate multipliers, comfort as ticks of slack, the consent
  line, and a per-source favourite weight vector (one-hot in the
  single-source case). It MUST appear only in the cat's own block,
  never in any other cat's row.
- **FR-009**: Training-time global state (the centralized critic's
  input) MUST expose each seat's identity block, per the ruled CTDE
  declaration (critic sees global state; execution inputs stay local).

**Clock (K§2: "2) drop")**

- **FR-010**: The episode-clock observation cell MUST be removed
  entirely. No replacement de-synchronizer enters the observation (the
  stuck detector — its own spec — is the served-side net; the identity
  block removes the mirror-symmetry cause).

**View holes and waypoint cells (doctrine rule 5, GEN2-INPUTS)**

- **FR-011**: Friend-record fields that no behavior rule reads MUST be
  stripped from the observation (the strip the element memory already
  received). The enumeration runs at plan time against the CURRENT
  behavior rules (result: happiness is the sole pure view hole —
  research R3), and is RE-VERIFIED after spec 059 (teacher rework)
  merges and before corpus collection; 059's rule-5 audit only
  removes reads, so the list can only grow, never invalidate a strip.
- **FR-012**: Direction-to-waypoint observation cells MUST be added so
  the exploration rule's route is no longer private state the
  observation cannot carry; the direction encoding follows FR-001's
  bearing form.

**Reserved dirt cells (S§2 rider 2)**

- **FR-013**: Two observation cells MUST be reserved for the future
  dirt compartments: appended additively (the e_col pattern),
  zero-valued until armed, with a pre-freeze inertness proof
  (bit-identical behavior at zero — the F-058 check-1 lesson: prove
  non-contribution, not mere zeroness).

**Schema artifact and column maps (prereg §3)**

- **FR-014**: The observation schema version MUST bump; policy
  artifacts pin the version and the existing load-time gate keeps
  refusing mismatches. Any other schema whose layout this package
  moves (the training-time global state per FR-009) bumps its own
  version id; schemas untouched (action, mask) keep theirs.
- **FR-015**: The schema artifact MUST include a schema-version-keyed
  column map: every observation and action cell addressable by name
  per schema version, published through the Python binding alongside
  the existing schema-version constants. Version 5 lookups reproduce
  today's layout; unknown versions or names fail loudly.
- **FR-016**: The normative layout (the contract document) MUST state
  the full cell map for the new version, including: the zero-distance
  bearing value, the heard-row encoding, vacant-row behavior, corner
  wall-distances, and the clamp semantics at both scales.

**Vocabulary flags (S§7 — config note, no engine change)**

- **FR-017**: The Gen 2 world configuration arms trill and ekekek
  (all four free sound kinds live). This is a flag flip only — the
  message layout already carries both kinds as reserves (spec 033)
  and MUST NOT change shape for it. The served Gen 1 world's config
  is untouched.

### Key Entities

- **Observation vector**: the per-cat, per-tick input contract; one
  self block, K permanent by-id friend rows, element slots, element
  memory. This spec changes its layout and version.
- **Identity block**: the cat's own trait vector (need rates, comfort
  slack, consent line, favourite weights) — new, self-only.
- **Column map**: the named, schema-version-keyed index table published
  with the schema artifact — new.
- **Schema version pin**: the existing artifact/load-time gate that
  makes mismatched policies refuse to load — reused, value bumped.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An observation encoded at 20×20 and at 100×100 for the
  same relative scene is cell-for-cell identical in every spatial
  feature (the size-invariance the F-053 collapse motivated).
- **SC-002**: Zero cells in any other cat's row carry need (except
  bath), happiness, distress, or trait information, verified by
  field-level enumeration of the contract and by encoding tests over
  randomized states (the leak audit, FR-007a).
- **SC-003**: Every downstream reader cell-name lookup for version 5
  reproduces today's indices exactly (no reader breaks before it
  flips), and the new version's lookups match the shipped contract.
- **SC-004**: The reserved dirt cells prove inert pre-freeze: exactly
  0.0 over the randomized property battery, with no encoder write path
  into the reserve range (the constructible form of the e_col
  bit-identity bar; a cell that is constant zero with no writer
  contributes nothing to any forward pass).
- **SC-005**: No observation cell varies with the episode clock; a
  stationary world encodes identically across ticks (modulo scene-age
  and staleness cells doing their declared jobs).
- **SC-006**: A Gen 1 (schema 5) policy artifact refuses to load
  against the new schema version, and vice versa, with a clear error.
- **SC-007**: The four distance-to-wall cells replace fractional
  self-position with no other consumer regression: the full test
  suite and certification battery encode under the new layout without
  reading a removed cell.

## Doctrine check (CLAUDE.md rule 8)

Checked against `experiments/DESIGN-DOCTRINE.md`, 2026-10-09:

- **Rule 12 (own state visible, others' hidden)** moved FR-005/FR-006/
  FR-007: the visibility line is this rule applied — with the DECLARED
  departure from its letter that others' BATH stays visible as the
  in-roster control (S§1 amendment; perceptibility grounding). The
  spirit holds: what stays hidden gates cooperation, never survival.
  Whether rule 12's text gains the exception clause is an owner call
  at the prereg freeze, not this spec's.
- **Rule 8 (design scarcity of information, not incentives)** moved
  FR-005/FR-008: hiding needs while adding the identity block designs
  what information exists, not what behavior pays; headroom for Gen 2
  comes from this scarcity, not from a harder world.
- **Rule 5 (imitability — the teacher acts only on what the student
  sees)** moved FR-011/FR-012: the view-hole strips and the waypoint
  cells restore exact parity between the observation and the behavior
  rules' decision context, in both directions.
- **Rule 9 (frozen models cannot answer a reprice)** moved FR-014 and
  the one-wall packaging: Gen 1 policies are never served the new
  contract (version pin), and every Gen 2 claim is made by minds
  retrained under it.
- **Rules 1, 2, 3, 4, 6, 7, 10, 11** were checked and moved nothing:
  this spec touches no reward, price, relief, vocabulary scripting,
  or gate semantics. (Rule 6 adjacent: FR-017 arms free-register
  kinds but scripts nothing on them.)

## Assumptions

- Spec numbering: this is spec 058; the teacher rework, empty-bowl
  amendment, and stuck detector follow as their own specs and are OUT
  of scope here. The consent_line call-site flips belong to the
  teacher-rework spec (my packaging call, recorded there).
- Distance metric: PINNED Manhattan (FR-001), owner's question
  resolved in-session 2026-10-09 and confirmed metric-agnostic by
  Experiments the same day (F-052/F-053 collected under schema 5's
  Manhattan cells; lab instruments Manhattan by standing rule).
  Grounds: the ruling's /40 rationale is "native walk-cost units" and
  walk cost is Manhattan by construction (N/E/S/W moves only); every
  decision consumer is Manhattan (engine decision distances, meow
  audibility, every schema-5 observation distance cell incl. the
  nearest-K slot fill), keeping teacher context and student
  observation on one metric (doctrine rule 5); the two forms are
  exactly interconvertible given the bearing pair. The vision disc
  stays Euclidean and untouched (house convention: Euclidean decides
  WHO is visible — carried by the presence bit; Manhattan says how
  far to REACH). Constants metric-adequate: max Manhattan at 100×100
  is 198 < 400.
- FR-011's strip list was enumerated at plan time against the current
  rule set (research R3; happiness only) and the contract records it;
  the post-059 re-verify (one re-run of the read sweep) is a 058
  polish obligation, safe-direction only.
- No Gen 3 cells (season/weather/spares) are reserved at this bump
  beyond the two dirt cells. RULED, owner 2026-10-09 in the Product
  session: "Don't reserve gen 3 cells." This closes the prereg
  skeleton's sixty-second freeze question (§3); Gen 3 pays its own
  wall.
- "Scene/water/sunbeam context bits" on friend rows (FR-005) stay
  visible: they are world facts about a visible cat's situation, not
  internal state. The leak audit (FR-007a) re-confirms each at the
  field level.
- The Gen 2 world config (vocabulary flags armed, FR-017) ships as
  checked-in training config beside the schema change; the #390
  package world's other knobs are Experiments' prereg material, not
  this spec's.
