# Feature Specification: Initial-Needs Distribution at World Creation

**Feature Branch**: `product/initial-needs`

**Created**: 2026-10-18

**Status**: Draft

**Input**: Owner kickoff 2026-10-18 (her word in this session: "Initial
needs work approved"; relayed ask from Experiments, her words in their
session: "Relay initial needs work to product"). Requirements context:
`experiments/gen2-trunk-training-2026-10-18/MITIGATION.md` rung (ii)
and deviations ledger entry 2 (`experiments/gen2-deviations.md`).
Professor advisory note:
`~/ai/professor/notes/for-experiments-corpus-extension-design-2026-10-18.md`
(design detail advisory; this spec is Product's).

## Why now

Today every kitty is born with all six needs at zero and happiness at
100; no configuration can create a world any other way. That means a
critic-training corpus cannot contain manufactured distressed INITIAL
states — worlds that begin in distress and let competent relief play
out, so the path INTO distress is never paid for while the data is
exactly what a value estimator needs (distressed state now, recovery
returns ahead). The Gen 2 trunk critic failed its acceptance probe for
exactly this coverage gap; the ruled mitigation's rung (ii) was
superseded FOR NOW because this engine path does not exist. This knob
reopens the cleaner mechanism. Not blocking Experiments' lane (their
degraded-dial route covers the bins meanwhile); lands when it lands.

## Clarifications

### Session 2026-10-18

- Q: Should the initial-needs section apply one shared distribution to
  every kitty in the roster, or also allow per-kitty overrides?
  (FR-003) → A: Roster-wide with per-kitty settings that override
  (her words: "Roster wide with per kitty settings that override
  (covers both options fully)").
- Q: When a need is given a draw range, should each kitty draw its own
  value, or should the world draw one value shared by all kitties it
  governs? (FR-005) → A: Per-kitty draws, independent per need (kitty ×
  need granularity) — her word "A" 2026-10-18, on Experiments'
  consumer recommendation (relayed on her word; their grounds: breaks
  world-level collinearity, staggers recoveries for contrast pairing,
  loses nothing — lockstep stays expressible via point ranges or
  overrides).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A toggleable feature that is inert when absent (Priority: P1)

An operator runs any existing config on the new engine. With the
feature absent (no roster-wide section, no per-kitty entry — FR-001),
every world behaves byte-for-byte as today. With either present, the
same config otherwise unchanged starts kitties at the configured need
levels — so corpus-extension collection is a pure config addition (the
062/063/064 pattern).

**Why this priority**: inert-when-absent is the standing gate on every
world knob; a leaking default poisons every golden and every frozen
pin.

**Independent Test**: full suite green with zero golden/pin re-cuts; a
collection run at a fixed seed, feature absent, byte-identical to the
pre-feature engine; a feature-bearing config validates and runs.

**Acceptance Scenarios**:

1. **Given** a config with the feature absent (FR-001's definition),
   **When** a full run executes on the new engine, **Then** every
   readable output surface is byte-identical to the pre-feature engine
   at the same seed (serialized config and defaults stamp included —
   they must not grow).
2. **Given** a config carrying the section, per-kitty entries, or
   both, **When** validation and a full run execute, **Then** both
   succeed.

---

### User Story 2 - A world can start already in distress (Priority: P2)

An experimenter writes a config that starts every kitty's cuddle need
at 80 (or draws each need from a declared range). The generated world's
kitties stand at those need levels at tick 0, their happiness is the
engine's own weighted-needs number for those levels (floored per
Article I), and relief plays out from there under unchanged law.

**Why this priority**: this is the mechanism itself — manufactured
initial conditions for critic coverage (the mitigation's true rung
(ii), and the return-span floor: all needs armed reaches below the
paid-for archive's floor by construction).

**Independent Test**: staged configs with fixed values and with ranges;
generated worlds carry exactly the configured (or drawn) levels;
happiness equals the engine's happiness function of those levels.

**Acceptance Scenarios**:

1. **Given** a fixed per-need value (cuddle 80), **When** the world is
   generated, **Then** every kitty's cuddle need is exactly 80 at tick
   0 and its happiness equals the engine's weighted-needs happiness for
   its full need vector.
2. **Given** a per-need range (cuddle 60–95), **When** the world is
   generated, **Then** each kitty's cuddle need lies in [60, 95],
   kitties draw independently (two kitties may land on different
   values; two ranged needs on one kitty draw separately), and the
   same seed + config always reproduces the same per-kitty values.
3. **Given** all six needs armed high, **When** the world is
   generated, **Then** happiness sits at the engine's floored value
   and the world still satisfies every standing invariant.
4. **Given** the section present but a need left unspecified at both
   levels, **When** the world is generated, **Then** that need starts
   at today's value (zero).
5. **Given** a roster-wide cuddle setting and a per-kitty override for
   one kitty's cuddle, **When** the world is generated, **Then** that
   kitty gets the override's outcome and every other kitty the
   roster-wide one; the override kitty's OTHER needs still follow the
   roster-wide settings (need-by-need precedence).

---

### User Story 3 - Distressed starts are register-real (Priority: P2)

A welfare reader audits a collection run later. Worlds that were
CREATED in distress are visible as such from the start: the distress
record shows the manufactured distress from tick 0, not from the first
tick a need happened to move. No one-tick (or longer) blind spot
exists between creation and the first needs phase.

**Why this priority**: welfare practice (owner 2026-09-26) — the
register records added scripted distress ticks so a future register
read is never surprised; manufactured states are register-real and
priced. The existing distress record is keyed to a need CROSSING the
threshold; a need initialized ABOVE it never crosses, which is exactly
the blind spot this story forbids.

**Independent Test**: a world generated with a need above the distress
threshold shows that kitty-need pair in the distress record at tick 0
and in the kitty's distress state before any tick runs; a world
generated below the threshold shows neither.

**Acceptance Scenarios**:

1. **Given** a need initialized above the distress threshold, **When**
   the world is generated, **Then** a distress event for that kitty
   and need exists at tick 0 and the kitty's own distress state
   reflects it before the first tick.
2. **Given** a need initialized above the safeguard threshold but
   below distress, **When** the first environment phase runs, **Then**
   the standing relief guarantee behaves exactly as it does for a need
   that rose there mid-run (a capable, reachable resource exists or is
   spawned) — no new rule, no exemption.
3. **Given** needs initialized below both thresholds, **When** the
   world is generated, **Then** the distress record is empty — the
   knob alone never fabricates distress entries.

---

### Edge Cases

- Values at the bounds: 0 and 100 are legal (needs are bounded 0–100,
  Article I); values outside [0, 100], or a range with min > max,
  REJECT at config validation with a clear error — never clamp
  silently.
- All needs at 100: happiness computes to the Article I floor, never
  below; the safeguard machinery owes every elevated need the standing
  relief guarantee on the next environment phase. This is the
  mitigation's "floor-initialized, all needs armed" case and must be
  expressible.
- Range with min == max: degenerates to the fixed value; whether any
  draw occurs for it is design-level, but determinism and the
  configured outcome are identical either way.
- Composition with randomized starts (spec 062): both knobs on — a
  kitty's position comes from the starts law, its needs from this one;
  neither draw disturbs the other or the master stream.
- Save/load: initial needs are generation-time only. A saved world
  resumed under a different initial-needs section does not re-seed —
  needs are world state, carried as-is (the 062/064 precedent for
  generation-time knobs).
- Snapshot restore into the RL env: out of scope — this feature covers
  world GENERATION only (the mitigation names snapshot starts as the
  other missing path; it stays missing, deliberately).
- Distress-at-tick-0 and the first deciders: the generated world is the
  tick-0 world the first deciders read (the 049 precedent for memory
  seeding); distress state seeded at generation is part of that view,
  consistent on every surface that exposes it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST be one optional config section plus the
  per-kitty override entries. The feature's OFF state is: no
  roster-wide section AND no per-kitty initial-needs entry anywhere in
  the config — "feature absent" below means exactly that. Feature
  absent means today's behavior exactly, and such a config is
  indistinguishable on every surface from one written before this
  feature existed. Unknown keys inside the section or an override MUST
  be rejected like everywhere else in the config.
- **FR-002**: With the feature absent, the engine MUST be
  byte-identical to the pre-feature engine on every readable surface —
  decisions, RNG consumption, serialized config (defaults stamp and
  `GET /config` must not grow), collection arrays, goldens. Zero
  re-cuts.
- **FR-003**: The section MUST express, per need kind, either a fixed
  initial value or a draw range (both bounds in [0, 100]; drawn values
  never leave the range; the exact value mapping is the law contract's
  to pin), in the needs' own 0–100 units; unspecified needs start at
  today's zero. The section is
  roster-wide, with optional per-kitty override entries (keyed to a
  rostered kitty) whose per-need settings take precedence over the
  roster-wide ones need-by-need; a need absent from both starts at
  zero. Validation MUST reject out-of-bounds values, inverted ranges,
  and overrides naming a kitty not in the roster, at startup with a
  clear error.
- **FR-004**: Initial needs MUST be applied at world generation, after
  placement and before the world's own generation-time happiness
  derivation, so each kitty's tick-0 happiness is the engine's one
  happiness function of its initialized needs (Article I floor
  included) — never a separately configured number.
- **FR-005**: Worlds with the section MUST remain deterministic per
  seed + config. A ranged need draws INDEPENDENTLY per kitty and per
  need (kitty × need granularity — clarified 2026-10-18): kitties may
  differ within one world, and one kitty's needs never share a single
  scalar draw, so mixed profiles (one need high, another low) are
  expressible. All draws come from the section's own domain-separated
  sub-stream keyed off the world seed (the spec 062 starts law): the
  master stream and every existing sub-stream are untouched, so
  section-on divergence is attributable to this feature alone and
  composition with 062 changes neither draw.
- **FR-006**: Register-real from tick 0: a need initialized at or
  above the distress threshold MUST produce the same records and
  kitty-visible distress state at tick 0 that a mid-run threshold
  crossing produces at its tick — distress events in the record, the
  kitty's own distress flags set, duration clocks anchored at 0. The
  same tick-0 consistency applies to the whole needs-phase state
  family initialized values would have set mid-run (announce arming
  included): the generated world carries the state its need levels
  imply, through the engine's existing definitions. No surface may
  show a distressed-created world as healthy at tick 0.
- **FR-007**: The standing Article I relief guarantee MUST apply to
  initialized needs exactly as to risen ones (safeguard-threshold
  check on the next environment phase; no new rule, no carve-out), and
  initialization MUST NOT create any state the engine forbids: needs
  clamped semantics unchanged, happiness never below its floor,
  Articles I–III invariants green from tick 0.
- **FR-008**: No behavior-API or observation surface changes: only the
  initial VALUES of existing engine state move (Article IV untouched;
  no new read at decision time — doctrine rule 5). The creation path
  stays server-authoritative (Article V).
- **FR-009**: No served or committed experiment config carries the
  section in this feature's PRs (training-only intent; turning it on
  in a served or collection world is a deploy/freeze ruling in its own
  lane — doctrine rules 8 and 9). The full existing test and config
  surface MUST pass unchanged, and new tests MUST fail if the section
  leaks into section-absent generation.

### Key Entities

- **Initial-needs section**: one optional config section; per-need
  entries, each a fixed value or an inclusive range in need units
  (0–100); roster-wide by default, with optional per-kitty override
  entries that take precedence need-by-need (clarified 2026-10-18).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A full run at a fixed seed on a pre-feature config is
  byte-identical on every readable output surface to the pre-feature
  engine; zero golden, pin, or fixture changes in this feature's PRs.
- **SC-002**: Across staged configs, fixed values land exactly, drawn
  values land inside their declared ranges, and unspecified needs
  start at zero — for every kitty, with tick-0 happiness equal to the
  engine's happiness function of the initialized vector.
- **SC-003**: Identical seed + config with the section present
  produces identical worlds and runs; with 062 starts also on, both
  knobs' outcomes are unchanged by each other's presence.
- **SC-004**: A world initialized above the distress threshold is
  register-visible as distressed at tick 0 (events recorded, kitty
  distress state set); one initialized below both thresholds adds no
  records.
- **SC-005**: A 4,000-tick run initialized "all needs armed" (the
  mitigation's floor-initialized case) completes with every standing
  invariant green and relief playing out under unchanged law —
  supporting Experiments' corpus-extension collection as a pure config
  addition on the landed binary (their reads, their lane).

## Design-doctrine check (CLAUDE.md rule 8)

This spec scripts world setup (what state a world is born in) and
touches welfare-visible state, so each doctrine rule was checked
before planning:

- **Rule 12 (relief is always available; kitties cannot suffer) —
  moved choices.** FR-006/FR-007: a manufactured distressed start gets
  the full standing machinery — register records from tick 0, the
  safeguard relief guarantee on the next environment phase, Article I
  bounds and floor — so initialization changes where a world starts,
  never what the world owes its kitties. The welfare-cost accounting
  for running such worlds is already declared in the mitigation
  (register-real, priced per the philosophy-round qualifier); this
  spec supplies the mechanism that keeps the register honest.
- **Rule 9 (frozen models / pins) — moved choices.** FR-002/FR-009:
  section absent is byte-inert, so no pin or golden re-cuts and no
  deploy question; carrying it in a served or collection world is a
  freeze-sitting/deploy ruling, not this spec's. FR-005's sub-stream
  constraint exists so section-on divergence is attributable to this
  feature alone.
- **Rule 8 (scarcity / headroom) — moved a choice.** Manufactured
  distressed worlds are declared TAIL/training-side variance; the
  served config stays the majority episode. FR-009 keeps the knob out
  of every served and committed config in this feature's PRs.
- **Rule 5 (teacher sees what the student sees) — checked, moved
  nothing.** No new read at decision time: only initial values of
  existing state move, and a kitty's own needs are already in its own
  view (rule 12 gloss), so a distressed start is observable by its
  owner exactly as a risen need is.
- **Rules 1, 2 (reward, prices) — checked, moved nothing.** No reward
  term, no price: where a world starts is world setup, not a payment
  for any choice.
- **Rules 3, 4, 6, 7, 10, 11 — checked, moved nothing.** No rider,
  edge, spoken word, behavior build, gate bar, or invalidation clause.
  Rule 10's gates live with the consumer (Experiments' acceptance
  checks in the mitigation), not in this mechanism.

## Assumptions

- Whether a min == max range consumes a draw is design-level;
  determinism and the configured outcome are identical either way
  (draw semantics themselves are ruled — FR-005).
- Section naming and placement follow the house serialization
  discipline (absent never serializes; stamp unmoved); exact naming is
  plan-level.
- Distress-state seeding at generation reuses the engine's one
  definition of entering distress (same records, same fields), not a
  parallel path — verified at plan time.
- Experiments' collection protocol (configs derived from trunk legs,
  scripted teacher seats, 4k–8k ticks, seed band 1095001–1095300) lives
  in the mitigation declaration and is not duplicated here.
