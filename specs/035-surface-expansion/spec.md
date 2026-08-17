# Feature Specification: Surface-Expansion Export

**Feature Branch**: `035-surface-expansion`

**Created**: 2026-08-17

**Status**: Draft — design pre-settled (owner + Experiments, 2026-08-17); owner may adjust any ruling until the exp-006 prereg freezes

**Input**: Experiments' expansion-export requirements (owner-directed handoff
2026-08-17) + the five-question design settlement recorded in Clarifications.
Purpose: the phase-1 seating plan keeps the current certified minds across the
033 generation wall — Miso, Pumpkin, and Kittybear keep their attention minds,
Clementine (the new seat) gets the exp-004 mind, and only Biscuit's seat takes
a new phase-1 lineage mind. Every committed artifact pins the pre-wall schemas
and cannot load on the current engine, so carrying a mind across the wall
requires a production-grade surface-expansion export: certified old-surface
artifact in, behaviorally-identical new-surface artifact out.

## Clarifications

### Session 2026-08-17 (pre-specify settlement, owner-directed)

- Q: How are the new input-side parameters initialized? → A: **Exactly
  zero, all of them** (new message-kind type rows and new digest-slot
  parameters). Zero makes deafness a provable invariant instead of an
  accident of seed, composes with the structural check ("provably zero" is
  checkable; "harmlessly random" is not), and trains up fine if a future
  finetune ever teaches the words — re-initialization would be a
  registered act. (Experiments concur with Product recommendation.)
- Q: Where does behavioral parity run, given the current engine refuses to
  load the source artifacts? → A: **Division by failure mode**: the tool
  proves PLACEMENT (bijective weight mapping, head floor, zeroed inputs —
  structural, exhaustive, no sampling); Experiments' independent numpy
  harness proves SEMANTICS (behavioral parity on old dims — which catches
  a wrong token map that a bijection check would bless). The parity number
  is a certification leg, pinned in the exp-006 prereg §5. The tool only
  attests its structural checks.
- Q: What runs the pre-expansion self in the seat-paired battery? → A:
  **Nothing — it never runs.** By the parity invariant the expanded
  artifact IS the source on the new surface; "vs its pre-expansion self"
  is operationalized as reference-composition runs of the expanded
  artifacts themselves, and the per-seat gate measures the company change.
  The only consumer of the source forward is the parity leg (Experiments'
  harness, observation rows sampled from archived pre-wall datasets).
- Q: Naming and provenance? → A: Source name + surface token: `-o4` (for
  observation-schema 4), e.g. `attn-a1-s1-o4.ckpolicy`. Provenance lives
  in the registry row's recipe field ("expanded from `<source sha>` by
  `<tool> vN`"); artifact headers gain nothing (they stay strict), and
  spec 034's optional header block remains a future rider. Display strings
  unchanged per the owner's 2026-08-16 ruling (architecture alone).
- Q: Retirement choreography at the cutover? → A: Sources retire to
  `policies/retired/` with their registry rows kept; expanded successors
  sit at top level with new rows; the README's Superseded-by column points
  source → expanded successor. **Superseded-by is artifact lineage, not
  seat inheritance**: the exp-004 mind's successor seats at Clementine (a
  different seat), and Biscuit's new lineage mind supersedes nothing.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A certified mind crosses the generation wall unchanged (Priority: P1)

The operator points the expansion tool at a certified pre-wall artifact and
receives a new-surface artifact that is the same mind: on everything the mind
could see and say before the wall, its decisions are identical, and the new
artifact loads and serves on the current engine exactly like any
current-generation artifact.

**Why this priority**: This is the feature — four of five phase-1 seats keep
their minds only if this works, and it is needed before the certification
battery (~one week).

**Independent Test**: Expand a fixture old-surface artifact; verify the
output loads through the standard serving loader, seats in a test world, and
the tool's structural attestation shows every source parameter placed and
every new parameter at its specified value.

**Acceptance Scenarios**:

1. **Given** a certified pre-wall artifact (either the MLP or the
   entity-attention format), **When** the operator runs the expansion,
   **Then** the tool emits a new artifact targeting the current compiled
   surface, reports the new sha256, and attests its structural checks.
2. **Given** the expanded artifact, **When** the current server loads it
   through the ordinary seating path, **Then** it passes every schema gate
   with no special-casing and drives its kitty in a running world.
3. **Given** the same source, target surface, and tool version, **When**
   the expansion runs twice, **Then** the outputs are byte-identical (same
   sha256) — determinism is part of the contract.

---

### User Story 2 - The expanded mind is deaf and mute in the new vocabulary (Priority: P1)

Viewers and experimenters can rely on an expanded mind being *exactly its
old self*: it never speaks any post-wall message kind, and hearing neighbors
speak them changes nothing about its behavior — until a future finetune
deliberately teaches it, as a registered act.

**Why this priority**: The mask cannot be the silencer — chirp and the Here*
kinds are mask-legal for any mind, so only initialization keeps an expanded
mind from speaking words it never learned. Symmetrically, once Biscuit's new
mind speaks, the expanded minds must not respond to those words through
arbitrary untrained parameters.

**Independent Test**: Seat an expanded fixture mind in a test world with the
full vocabulary enabled and a neighbor emitting new kinds; observe zero
new-kind emissions from the expanded mind, and identical decisions with the
new-kind observation inputs present versus absent.

**Acceptance Scenarios**:

1. **Given** an expanded mind in a world with every vocabulary flag on,
   **When** it runs for an extended period, **Then** it emits no message of
   any post-wall kind (mute invariant: new head outputs pinned below a
   stated negative floor).
2. **Given** an expanded mind whose neighbor emits post-wall kinds,
   **When** its decisions are compared against the same world state with
   those signals zeroed, **Then** the decisions are identical (deaf
   invariant: all new input-side parameters exactly zero).

---

### User Story 3 - The expanded artifact is a first-class citizen of the artifact machinery (Priority: P2)

The expanded artifact enters `policies/` exactly like any certified
artifact: a registry row in the same PR (spec 034 law), provenance naming its
source and the tool that made it, the `-o4` naming convention, and — at the
cutover — the retirement choreography that keeps the ledger legible.

**Why this priority**: The wall's audit chain (sha-keyed registry, README
ledger, certification records) must not fork into a special case for
expanded artifacts.

**Independent Test**: Reading `policies/README.md` and `registry.toml` alone
answers: what is this artifact, what was it expanded from, by what, and what
does it display.

**Acceptance Scenarios**:

1. **Given** an expanded artifact landing in `policies/`, **When** its PR
   is assembled, **Then** it carries its registry row (same-PR law), with
   display per the owner's architecture-alone ruling and recipe provenance
   "expanded from `<source sha>` by `<tool> vN`".
2. **Given** the phase-1 cutover, **When** sources retire, **Then** rows
   are kept, Superseded-by points source → expanded successor (artifact
   lineage, not seat inheritance), and the top level holds exactly what
   the served config names.

---

### Edge Cases

- **Source already on the current surface**: nothing to expand — the tool
  refuses with a clear message rather than emitting a byte-copy (a no-op
  export would mint a second sha for the same mind and split its record).
- **Source newer than the tool knows** (unknown artifact version or schema
  ahead of the compiled surface): refuse, naming what was found and what
  the tool supports.
- **Corrupted source**: refuse naming the path and failure, the artifact
  loaders' fail-loud doctrine.
- **Serving gates untouched**: the tool's ability to read old-generation
  artifacts is tool-scoped only; the server's loader continues to refuse
  them (the generation gate's guarantee is not weakened by this feature).
- **Expanded-artifact registry rows are new rows**: keyed by the new sha;
  the source's row is untouched (rows never change except the sanctioned
  display amendment; rows never leave).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A deterministic expansion tool MUST convert a certified
  pre-wall artifact (both committed formats: the MLP family and the
  entity-attention family) into an artifact targeting the current compiled
  surface: same source + tool version → byte-identical output, new sha256.
- **FR-002**: The tool MUST read old-generation artifacts without weakening
  any serving gate: the server's loader keeps refusing them; only the tool
  may read past the schema pins, and only to expand.
- **FR-003**: The tool MUST prove PLACEMENT structurally and exhaustively:
  every source parameter lands at its mapped position (bijective — no
  source value lost, no target position double-written), no sampling. The
  attestation is part of the tool's output.
- **FR-004** (mute invariant): every output dimension corresponding to a
  post-wall message kind MUST be initialized so the mind can never select
  that kind — pinned below a stated negative floor, never zero-initialized.
  Rationale, binding: chirp and the Here* kinds are mask-legal, so the mask
  cannot be the silencer for words the mind never learned.
- **FR-005** (deaf invariant): every new input-side parameter (post-wall
  message-kind type rows and new digest-slot parameters) MUST be exactly
  zero, so new-kind observation tokens contribute nothing to the forward.
  Both invariants are part of the FR-003 attestation ("provably zero,
  provably floored").
- **FR-006**: Behavioral parity on the old dimensions is certification's
  leg, not the tool's: Experiments' independent harness reimplements both
  layouts and measures parity (exp-006 prereg §5, house tolerance bar);
  the spec binds the DIVISION — tool attests structure, battery attests
  semantics — so neither side assumes the other's proof.
- **FR-007**: The expanded artifact MUST load through the standard serving
  loader with all current schema gates and no special-casing — a
  first-class current-generation artifact.
- **FR-008**: Naming: source name + `-o4` (observation-schema-4 surface
  token), e.g. `attn-a1-s1-o4.ckpolicy`; the convention MUST be recorded
  in `policies/README.md`'s Naming section, consistent with its
  name-identifies-a-run rule (same run, new surface — the surface token is
  the one distinguishing axis).
- **FR-009**: Each expanded artifact MUST get its spec-034 registry row in
  the same PR that lands it: display unchanged per the owner's
  architecture-alone ruling; recipe field carries the provenance
  "expanded from `<source sha256>` by `<tool> vN`".
- **FR-010**: The tool MUST carry a version, stamped into the provenance;
  determinism (FR-001) is keyed to it.
- **FR-011**: The rollout section of the cutover (executed at phase-1
  seating, not in this feature): sources retire to `policies/retired/`
  with rows kept; Superseded-by points source → expanded successor —
  artifact lineage, not seat inheritance (the exp-004 mind's successor
  seats at Clementine; Biscuit's lineage mind supersedes nothing). This
  spec delivers the tool and the three expanded artifacts as certification
  candidates; seating stays gated on Experiments' battery and the owner's
  word.
- **FR-012**: Nothing existing moves: no engine, schema-pin, config,
  fingerprint, or stamp change; the feature is repo tooling plus
  `policies/` content. The full pre-existing suite passes unmodified.

### Key Entities

- **Expansion tool**: versioned, deterministic; reads both pre-wall
  artifact formats, writes current-surface artifacts, attests placement +
  the two invariants.
- **Expanded artifact**: a new `.ckpolicy` with its own sha256, named
  `<source>-o4`, first-class on the current engine, certification
  candidate.
- **Provenance record**: the registry row (spec 034) carrying source sha +
  tool version in the recipe field; display untouched.
- **The three candidates**: `attn-a1-s1` (`d8e31021…`), `attn-a1-s3`
  (`dfef0ec2…`), `e004-a1-s2` (`21d19730…`), each onto the 225 surface.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All three named artifacts expand successfully; each output
  loads through the ordinary seating path on the current engine and drives
  a kitty in a running test world.
- **SC-002**: Re-running any expansion reproduces the identical artifact
  (same sha256), across runs and machines.
- **SC-003**: An expanded fixture mind, seated with the full vocabulary
  enabled and a new-kind-speaking neighbor, emits zero post-wall-kind
  messages over an extended run, and its decision stream is identical with
  the new-kind inputs present versus zeroed.
- **SC-004**: The structural attestation for each expanded artifact is
  machine-checkable and reproducible: bijective placement, all new input
  parameters exactly zero, all new head outputs at or below the stated
  floor.
- **SC-005**: The full pre-existing test suite passes with no modified
  assertions; no compatibility marker applies to the CHANGELOG entry.
- **SC-006**: Reading `policies/README.md` + `registry.toml` alone
  identifies any expanded artifact's source, tool version, and display.

## Assumptions

- Timing: needed before the phase-1 certification battery, roughly a week
  from 2026-08-17.
- The behavioral-parity tolerance and the battery design (reference
  compositions, per-seat gates) live in Experiments' exp-006 prereg — this
  spec deliberately does not restate their numbers, only the division of
  proof (FR-006).
- The proven expansion mapping (the 033 parity oracle's
  `expanded_checkpoint`) is the reference for the weight geometry; its
  seeded-random init for new parameters is exactly what this spec's
  invariants replace (zero inputs, floored heads).
- The tool is repository tooling, never a served surface; where it lives
  (crate, language) is a plan decision.
- The three expanded artifacts land as certification candidates; the
  cutover config PR and `--fresh` deploy are the routine seating machinery
  Product owns at rollout time, outside this spec.
- The owner may adjust any settled ruling until the exp-006 prereg
  freezes; the spec's Clarifications record the current owner-approved
  state.
