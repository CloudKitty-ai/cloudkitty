# Feature Specification: Welfare-Hazard Acknowledgement Guard

**Feature Branch**: `product/066-welfare-hazard`

**Created**: 2026-10-26

**Status**: Draft

**Input**: Owner kickoff 2026-10-26 (her words in this session: "Agreed,
let's start the guard. Let Experiments know what we're doing so they
can account for it"; her framing: "Can we add an additional guard to
ensure this mode, and any other welfare hazardous modes, are not
activated inadvertently? Perhaps an unsafe mode world flag?"). Context:
spec 065 (`specs/065-initial-needs/spec.md`, FR-009) and the banked
needy-preset relay (Experiments, 2026-10-25; its spec waits on her
word and depends on this one). Experiments' migration facts and
preference: their message of 2026-10-26, quoted where used below.

## Why now

The engine now has one way to create a world in distress on purpose
(spec 065, a manufactured distressed start) and is about to get a
second (a scripted "needy" preset that holds a seat's needs high).
Both are training instruments: wanted in a lab world, never in the
served world or a certification exam. Today the only thing keeping
them out of those places is a sentence in spec 065 — "no served or
committed experiment config carries the section" — with no check
behind it: a copied config block, a template edited in the wrong file,
or a collection config promoted to the served box would start a
distressed world with nothing to stop it and nothing to show it
happened. Her question names the gap exactly: welfare-hazardous modes
need a guard against inadvertent activation, one guard for all of
them, before the second mode lands.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A hazardous mode cannot be activated by accident (Priority: P1)

An operator or experimenter loads a config that turns on a
welfare-hazardous mode (today: a distressed start with any need raised
above zero). Unless the config also carries an explicit acknowledgement
naming that mode, the config fails to load, and the error names the
mode, the section that activated it, and the exact line to add. With
the acknowledgement present and exact, the config loads as it does
today.

**Why this priority**: this is the guard itself. Every other story is
a place the guard is applied or a property that keeps it honest.

**Independent Test**: a config with a raised initial need and no
acknowledgement fails validation with the named error; the same config
plus the acknowledgement line validates; the same config with every
need left at its default needs no acknowledgement and validates.

**Acceptance Scenarios**:

1. **Given** a config whose distressed-start section raises at least
   one need above zero (roster-wide or for one kitty) and no
   acknowledgement, **When** it is loaded on any path that validates
   the engine config, **Then** loading fails and the error names the
   mode, the activating section, and the acknowledgement line to add.
2. **Given** the same config with an acknowledgement naming exactly
   that mode, **When** it is loaded, **Then** it validates and the
   generated world is identical to the one spec 065 generates today.
3. **Given** a distressed-start section present but every need at zero
   (fixed zero, or absent), **When** it is loaded without any
   acknowledgement, **Then** it validates: nothing hazardous is active,
   so nothing needs acknowledging.
4. **Given** an acknowledgement naming a mode the engine does not know
   (a typo, or a mode from a newer engine), **When** it is loaded,
   **Then** loading fails naming the unknown mode.
5. **Given** an acknowledgement naming a known mode that the config
   does NOT activate, **When** it is loaded, **Then** loading fails
   naming the stale acknowledgement — an acknowledgement is exact, so a
   blanket list copied between configs never silently covers the next
   mode.

---

### User Story 2 - Absent means inert; the guard itself changes nothing (Priority: P1)

Every existing config without the acknowledgement section and without
a hazardous mode active behaves byte-for-byte as today: same decisions,
same RNG consumption, same serialized config, same defaults stamp,
same goldens. The guard is a check at load time and a declaration in
the config; it never changes a world.

**Why this priority**: inert-when-absent is the standing gate on every
config addition (the 062–065 pattern); a leaking default would move
every golden and every frozen pin.

**Independent Test**: the full suite green with zero golden, pin or
fixture re-cuts; a fixed-seed run on a pre-feature config
byte-identical to the pre-feature engine; the defaults stamp and
`GET /config` unmoved when the section is absent.

**Acceptance Scenarios**:

1. **Given** any config without the section, **When** a full run
   executes on the new engine, **Then** every readable output surface
   is byte-identical to the pre-feature engine at the same seed, the
   serialized config and the defaults stamp included.
2. **Given** a config with the section present and exact, **When** the
   world is generated and run, **Then** the world is identical to the
   one the same config generates without the section on the
   pre-feature engine — the acknowledgement changes what may load,
   never what a loaded world does.

---

### User Story 3 - The served world and the frozen exams can never be hazardous (Priority: P2)

A maintainer commits a config. If a hazardous mode is active in any
tracked config outside the experiments tree — the served world
config, the training config, a frozen certification exam, a spec
fixture — the shipped-config sweeps fail by file name. Inside the
experiments tree a hazardous config is allowed, and because the sweeps
load every tracked config, it must carry its acknowledgement or the
sweeps fail there too. Spec 065's FR-009 prose becomes a red.

**Why this priority**: the served box and the exams are where an
inadvertent activation does lasting harm (a served world of distressed
kitties; an exam whose score means something else). The sweep is the
cheapest layer that sees every committed file.

**Independent Test**: a staged hazardous config outside the
experiments tree fails the sweep naming the file; the same file inside
the experiments tree with an exact acknowledgement passes; without the
acknowledgement it fails at load.

**Acceptance Scenarios**:

1. **Given** a tracked config outside the experiments tree with a
   hazardous mode active (acknowledged or not), **When** the sweeps
   run, **Then** they fail naming the file and the mode.
2. **Given** a tracked config inside the experiments tree with a
   hazardous mode active and an exact acknowledgement, **When** the
   sweeps run, **Then** it loads and passes.
3. **Given** the seven committed spec-065 configs under
   `experiments/minifriend-phase1-2026-10-22/` and
   `experiments/minifriend-phase1b-2026-10-23/` carrying the
   acknowledgement line, **When** the sweeps run on the landed tree,
   **Then** they pass (the migration — see Assumptions).

---

### User Story 4 - A hazardous world is served only on purpose, and is visible as such (Priority: P2)

An operator starts the server on a config with a hazardous mode active
and acknowledged. Without an explicit server start-up option saying
that a hazardous world is intended, the server refuses to start and
says why. With the option, it serves the world, logs the acknowledged
modes at boot, and the served config surface shows the acknowledgement
from the moment the world exists — a welfare reader auditing the box
later sees that the world was created hazardous, from tick 0, not
inferred from the needs that followed.

**Why this priority**: the server is the one path that puts a world in
front of a client and a register for a long time; two independent
statements of intent (the config's acknowledgement and the operator's
start-up option) are the house shape for a deliberate crossing. The
visibility half is the welfare practice's register-real requirement
(owner 2026-09-26).

**Independent Test**: server start on an acknowledged hazardous config
without the option exits non-zero with a message naming the modes;
with the option it serves, the boot log names the modes, and the
config surface carries the acknowledgement; on a non-hazardous config
the option is accepted and changes nothing.

**Acceptance Scenarios**:

1. **Given** an acknowledged hazardous config and no start-up option,
   **When** the server starts, **Then** it refuses before creating or
   resuming any world, naming the acknowledged modes and the option.
2. **Given** the same config and the option, **When** the server
   starts, **Then** it serves; the boot log carries one line naming
   the acknowledged modes; the served config surface carries the
   acknowledgement section; the key-settings block (spec 052) carries a
   row naming the acknowledged modes.
3. **Given** a non-hazardous config, **When** the server starts with
   or without the option, **Then** it serves exactly as today; the
   key-settings block has no welfare-hazard row; the served config
   surface is unchanged.
4. **Given** a saved world created under a hazardous config, **When**
   the server resumes it under a config whose acknowledgement is
   missing or stale, **Then** it refuses at config load as in Story 1 —
   no special resume path.

---

### Edge Cases

- A hazardous section present but inert (a distressed start with every
  need at zero): not hazardous, needs no acknowledgement, and an
  acknowledgement of it is stale (Story 1, scenario 5).
- The section present with an empty acknowledgement list and no
  hazardous mode active: exact (nothing acknowledged, nothing active),
  so it validates. It serializes, so the served config surface grows by
  the empty section — the operator wrote it; that is theirs.
- Two or more hazardous modes active (possible once the needy preset
  lands): the acknowledgement must name all of them; the error for a
  partial list names the missing ones.
- Duplicate names in the list: rejected, one name per mode.
- Per-kitty activation only (one kitty's distressed-start entry, the
  roster-wide section absent — the phase-1b shape): hazardous exactly
  as a roster-wide activation; the error names the kitty's entry.
- The server's start-up option on a non-hazardous config: accepted and
  inert, so a deploy script can carry it unconditionally only if the
  operator chooses to; the recommended practice is to pass it per
  deliberate deploy. The deploy script in `docs/deploy/` is not changed
  by this feature.
- Paths that load the engine config without the server (the Python
  environment, the evaluation binary, the sweeps, tools): Story 1
  applies in full; Story 4's start-up option is the server's alone,
  since only the server serves a world.
- Future modes: a mode is hazardous only when the engine registers it
  as such; the registration names the mode, states when it counts as
  active, and states whether a seat in such a world may serve as a
  teacher for a learning corpus (the distressed start: yes, it IS the
  corpus-extension world; the needy preset will say no). Exposing the
  teacher-eligibility bit to the collection path is the needy spec's
  job; this spec makes the bit exist so every registered mode must
  declare it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST be one optional top-level config
  section holding a list of acknowledged hazardous-mode names. Absent
  section means today's behavior exactly, and such a config is
  indistinguishable on every surface from one written before this
  feature existed. Unknown keys inside the section MUST be rejected
  like everywhere else in the config.
- **FR-002**: With the section absent and no hazardous mode active,
  the engine MUST be byte-identical to the pre-feature engine on every
  readable surface — decisions, RNG consumption, serialized config
  (defaults stamp and `GET /config` must not grow), collection arrays,
  goldens. Zero re-cuts. The engine's world fingerprint (the settings a
  saved world must agree with to be resumable) MUST NOT include the
  section, so adding an acknowledgement to an existing config never
  changes which saved worlds it can resume.
- **FR-003**: The engine MUST hold a closed registry of
  welfare-hazardous modes. Each entry names the mode, defines when the
  mode counts as ACTIVE in a given config, and states whether a seat in
  a world running that mode may serve as a teacher for a learning
  corpus. The first entry is the spec-065 distressed start, active when
  any need — roster-wide or per-kitty — is given a fixed value above
  zero or a range whose upper bound is above zero; teacher-eligible.
  Adding a mode is adding an entry; a mode not in the registry is not
  guarded, so every spec that introduces a hazardous mode MUST add its
  entry (the needy preset's spec is the first consumer).
- **FR-004**: Config validation MUST fail when the set of acknowledged
  names is not EXACTLY the set of active hazardous modes: a missing
  name (an active mode not acknowledged), a stale name (an acknowledged
  mode not active), an unknown name, or a duplicate each fail. The
  error MUST name the mode(s) concerned, the section or per-kitty entry
  that activates each missing one, and the exact acknowledgement line
  to add. Validation runs on every path that validates the engine
  config — there is no load path that skips it.
- **FR-005**: Both shipped-config sweeps (the engine's and the RL
  surface's) MUST fail, naming the file and the mode, when any tracked
  config outside the `experiments/` tree has a hazardous mode active,
  acknowledged or not. Tracked configs inside `experiments/` with an
  active mode load through FR-004 and therefore MUST carry an exact
  acknowledgement or the sweeps fail at load. This supersedes spec
  065's FR-009 prose with a check.
- **FR-006**: The server MUST refuse to start — before any world is
  created or resumed — when the loaded config acknowledges one or more
  hazardous modes and the operator did not pass an explicit start-up
  option stating that a hazardous world is intended. The refusal names
  the acknowledged modes and the option. The option on a non-hazardous
  config MUST be accepted and inert.
- **FR-007**: When the server serves an acknowledged hazardous world,
  the acknowledgement MUST be visible from boot on the served config
  surface (the section serializes when present), in one boot-log line
  naming the modes, and as one row of the key-settings block (spec
  052) naming the modes. With no acknowledged mode, none of the three
  changes: no row, no line, no section.
- **FR-008**: No behavior-API or observation surface changes, no new
  read at decision time, no change to any world's law: the feature
  decides what may LOAD and what the server will SERVE, and declares
  it (Article IV untouched; Article V's server-authoritative path is
  where the serve-time check lives).
- **FR-009**: The seven committed spec-065 configs (listed under
  Assumptions) MUST receive their acknowledgement line in the same PR
  that lands FR-004, or main's sweeps go red between the two. The PR
  body declares the crossing (`cross-lane:` per THREADS.md §2) and
  quotes Experiments' consent; the merge takes the owner's word as
  every merge does. No other committed config changes.

### Key Entities

- **Welfare-hazard acknowledgement**: one optional top-level config
  section; a list of mode names; exact against the active modes.
- **Hazardous-mode registry**: the engine's closed list of modes, each
  with a name, an activity predicate over a config, and a
  teacher-eligibility flag. One entry today (the distressed start);
  the needy preset adds the second.
- **Start-up intent option**: the server's explicit operator statement
  that serving a hazardous world is intended; required whenever the
  config acknowledges any mode, inert otherwise.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A full run at a fixed seed on a pre-feature config is
  byte-identical on every readable output surface to the pre-feature
  engine; zero golden, pin or fixture changes in this feature's PR
  beyond the seven acknowledgement lines of the migration.
- **SC-002**: Every one of the five failure shapes (missing, stale,
  unknown, duplicate, partial) is rejected at load with an error that
  names the mode and, for a missing one, the line to add; the two
  legal shapes (exact, and nothing-to-acknowledge) load.
- **SC-003**: A staged hazardous config outside `experiments/` fails
  both sweeps by name; the landed tree, with the seven migrated files,
  passes both sweeps; main is never red between the validator and the
  migration.
- **SC-004**: Server start on an acknowledged hazardous config without
  the option exits non-zero before any world exists; with the option
  the boot log, the served config surface and the key-settings block
  each show the acknowledged modes; on the served `cloudkitty.toml`
  none of the three changes.
- **SC-005**: The engine's world fingerprint for each of the seven
  migrated configs is unchanged by the migration, so no saved world or
  recorded fingerprint from those arcs is invalidated.

## Design-doctrine check (CLAUDE.md rule 8)

This spec scripts what may load and what may be served, and declares
welfare-visible state, so each doctrine rule was checked before
planning:

- **Rule 12 (relief is always available; kitties cannot suffer) —
  moved choices.** FR-004 to FR-007 make the constitutional default
  the only thing that can happen by accident: a world that departs from
  it loads only when the config says so by name, is served only when
  the operator says so again, and is visible as such from tick 0. The
  guard changes no world's law and leaves relief availability
  untouched (FR-008); it is the activation half of the welfare practice
  (owner 2026-09-26, part 3): a declaration that seats an acknowledged
  config is where the welfare-cost line attaches, and the
  acknowledgement is what that line points at. Scripted-exempt modes
  still need the entry, because the guard is about activation, not the
  welfare status of the seat.
- **Rule 9 (frozen models / pins) — moved choices.** FR-002: absent is
  byte-inert, so no pin or golden re-cuts and no deploy question. The
  migration adds a line to seven committed files whose arcs are done;
  the engine fingerprint excludes the section (FR-002, SC-005), so no
  recorded world identity moves. Whether a declaration that recorded a
  file's text hash needs a deviations entry is Experiments' call in
  their lane.
- **Rule 8 (scarcity / headroom) — moved a choice.** FR-005: the
  served config, the training config and the frozen exams can never
  carry a hazardous mode; the served world stays the majority episode
  by check, not by convention.
- **Rule 5 (teacher sees what the student sees) — checked, moved
  nothing.** No new read at decision time; the registry's
  teacher-eligibility flag records a property for the corpus path to
  consume later and changes no decision.
- **Rules 1, 2 (reward, prices) — checked, moved nothing.** No reward
  term, no price.
- **Rules 3, 4, 6, 7, 10, 11 — checked, moved nothing.** No rider,
  edge, spoken word, behavior build, gate bar or invalidation clause.

## Assumptions

- **Migration set** (Experiments, 2026-10-26, verified against the
  tree: `git grep -l initial_needs -- '*.toml'` returns exactly these):
  `experiments/minifriend-phase1-2026-10-22/g2leg-20-W.toml` and
  `g2leg-20-G.toml` (roster-wide section), and
  `experiments/minifriend-phase1b-2026-10-23/g2leg-20-P1.toml` through
  `g2leg-20-P5.toml` (one kitty's entry). All in DONE arcs whose data
  exists; nothing in flight. Each gets the one acknowledgement line and
  nothing else. Experiments' preference, their words: "loud load
  failure, not a one-release warning" — adopted (FR-004).
- **Lane crossing of the migration**: the seven files are in
  Experiments' lane; the top-level config rejects unknown sections, so
  the line cannot be added before the section exists, and FR-009 says
  why it cannot land after. The PR therefore carries the seven edits
  under `cross-lane:` with Experiments' consent quoted; their
  deviations entry, if any, is theirs.
- **Fingerprint**: the engine's `fingerprint()` is width, height, seed
  and kitty ids today; FR-002 pins that the section stays out of it.
  Experiments asked for this ("excluded from the world fingerprint");
  the text hash of a config file is a different thing and does move
  when a line is added — Experiments were told so.
- **Exactness** (stale acknowledgement is an error) is this spec's
  choice for the owner's stated purpose — a blanket list copied between
  configs would otherwise cover the next mode silently. If the owner
  prefers over-acknowledgement to be legal, FR-004 loses the "stale"
  clause and nothing else changes.
- **Hazard predicate for the distressed start**: any configured value
  or range upper bound above zero. A lower bar (above the safeguard or
  distress threshold) would leave a world of kitties starting at 70
  unguarded while calling itself a welfare guard; the predicate is
  deliberately the widest.
- The start-up option's name and the registry's representation are
  plan-level; the deploy script is not changed by this feature, and
  whether the live box ever passes the option is a deploy ruling in its
  own right.
- The welfare practice text in `experiments/README.md` is Experiments'
  file; a one-line pointer there ("hazardous modes are acknowledged per
  spec 066") is proposed to the owner, not written by this spec.
- The needy-preset spec depends on this one: it adds the second
  registry entry (teacher-ineligible) and consumes the eligibility flag
  in the collection path.
