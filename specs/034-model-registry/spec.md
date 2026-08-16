# Feature Specification: Model Registry & Served Behavior Descriptions

**Feature Branch**: `034-model-registry`

**Created**: 2026-08-15

**Status**: Ready for planning — clarifications resolved

**Input**: Owner-approved shape relayed from Experiments 2026-08-15: replace the
raw model id shown on kitty cards (e.g. "e004-a1-s2") with a terse, human-readable
per-kitty model summary (e.g. "Transformer · BC+PPO"), served from a
machine-readable registry in `policies/` keyed by artifact sha256, updated
atomically with the artifacts it describes, and self-enforcing so a seating can
never silently skip the registry update. Owner's word: "Send the shape to
Product for spec'ing."

## Context

Today the client receives each kitty's `behavior` string verbatim (e.g.
`policy:e004-a1-s2`) and the traits dialog strips the `policy:` prefix, showing
the bare run id. Run ids are deliberately terse experiment identifiers
(`policies/README.md` Naming: "a name's job is to be a unique, stable
identifier tied to a record. It is not a spec sheet") — meaningless to a viewer.
The README anticipated this exact feature: "when a 'show brain' feature is
specced, [the human-readable description belongs] in a served field" — and
warned that a `description =` config key must not be added before a spec exists
because `PolicyConfig` refuses unknown fields. This is that spec, and it
supersedes the README's suggested placement (see Rejected Alternatives).

## Clarifications

### Session 2026-08-15

- Q: When the server is asked to seat an artifact whose sha256 has no
  registry row, should it refuse to start or warn and boot anyway? → A:
  **Refuse** — startup error naming the artifact path + sha, same doctrine
  as every other config validation failure. (Owner, direct.)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A viewer learns what kind of mind drives each cat (Priority: P1)

A person watching the meadow opens a kitty's traits dialog and reads, in plain
words, what drives that cat: "Transformer · BC+PPO" for an attention policy,
"MLP · BC+PPO" for the previous generation, "Scripted" for a needs-driven seat.
They do not need to know what "e004-a1-s2" means. The exact model id stays
available but demoted (small print / tooltip — presentation is the client's).

**Why this priority**: This is the feature — the whole point is that the
current display is meaningless to users.

**Independent Test**: Boot a world with a policy-seated kitty whose artifact
has a registry row; fetch the kitty from the read API and confirm the served
description matches the registry's display line; confirm a scripted kitty
serves "Scripted".

**Acceptance Scenarios**:

1. **Given** a kitty seated `policy:<name>` whose artifact sha has a registry
   row with display line "Transformer · BC+PPO", **When** a client fetches that
   kitty (REST or live stream), **Then** the kitty object carries
   `behavior_description: "Transformer · BC+PPO"` alongside the unchanged
   `behavior` string.
2. **Given** a kitty on a built-in behavior (`needs_driven` or any scripted
   builtin), **When** a client fetches it, **Then** it carries
   `behavior_description: "Scripted"` with no registry involvement.
3. **Given** a client older than this feature, **When** it receives kitty
   objects with the new field, **Then** nothing breaks — the field is additive
   and existing fields are unchanged.

---

### User Story 2 - The registry is the auditable, atomic source of truth (Priority: P2)

Experiments certifies a new artifact and, in the same PR that lands the
`.ckpolicy` file, adds one registry row: sha256 → architecture, recipe, display
line. The mapping can never drift from the artifact it describes because they
change together. Anyone can audit "what is this cat running and how was it
trained" from one file, keyed by the same sha256 the server logs at startup and
`policies/README.md` records.

**Why this priority**: Serve-don't-hand-sync is the owner's chosen mechanism;
without it US1 is a hand-maintained string that rots.

**Independent Test**: Parse the registry file standalone; confirm every
artifact at `policies/` top level has a row whose key matches the file's actual
sha256, and that rows carry all required fields.

**Acceptance Scenarios**:

1. **Given** the three currently certified artifacts, **When** the registry
   ships, **Then** it contains exactly their rows: `e004-a1-s2.ckpolicy`
   (sha `21d19730…`) → "MLP · BC+PPO"; `attn-a1-s1.ckpolicy` (sha `d8e31021…`)
   → "Transformer · BC+PPO"; `attn-a1-s3.ckpolicy` (sha `dfef0ec2…`) →
   "Transformer · BC+PPO".
2. **Given** an artifact is renamed on disk, **When** nothing else changes,
   **Then** the registry is untouched and still resolves — sha256 is the
   identity, the filename is a label (same rule as `policies/README.md`).
3. **Given** an artifact is retired to `policies/retired/`, **When** the move
   lands, **Then** its registry row is kept — rows are history, keyed by an
   identity that never changes.

---

### User Story 3 - A seating cannot silently skip the registry (Priority: P2)

An operator (or a future session) seats an artifact whose sha256 has no
registry row. The server does not let this pass silently at startup, and the
repository's test suite fails the PR that created the situation — the same
release-honest pattern as the CHANGELOG gate: the process physically cannot
forget the update.

**Why this priority**: Without enforcement the registry decays into the
hand-sync failure mode the owner explicitly rejected.

**Independent Test**: Point a config at a valid artifact deliberately absent
from the registry; boot; observe the refusal naming the artifact and sha
(FR-007). Run the repo test with a top-level artifact missing its row;
observe the failure naming the file and its sha.

**Acceptance Scenarios**:

1. **Given** a config seating an artifact with no registry row, **When** the
   server starts, **Then** startup fails with an error naming the artifact
   path and sha256 (FR-007).
2. **Given** a `.ckpolicy` at `policies/` top level with no registry row (or a
   row whose sha matches no file and no retired row), **When** the test suite
   runs, **Then** a test fails naming the mismatch.

---

### Edge Cases

- **Plugin-driven kitty**: a plugin is an external process, not a certified
  artifact — "Scripted" would be a lie and there is no registry row. The
  description field is simply absent; the client falls back to the behavior
  name (its existing rendering). Documented in Assumptions.
- **Malformed registry file** (unparseable, duplicate sha keys, missing
  required fields): startup error when the server needs the registry; repo test
  failure always.
- **Zero policy seats** (today's wall-window config): the server boots exactly
  as it does now — no lookup occurs, kitties serve "Scripted". A malformed
  registry is still caught by the repo test.
- **Row exists, artifact gone**: legal — rows outlive artifacts (US2 scenario
  3). The repo test checks the file→row direction, not row→file, except that a
  row's sha must correspond to *some* current or retired artifact recorded in
  `policies/` history; a row for a sha that never existed anywhere is flagged
  by review, not machinery (no reliable oracle).
- **Same artifact seated on multiple kitties**: each kitty serves the same
  description — resolution is per-artifact, applied per-seat (today
  `attn-a1-s3` drives two seats).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A machine-readable registry file MUST live in `policies/`,
  keyed by artifact sha256. Each row MUST carry: architecture (spelled out —
  "Transformer", "MLP"; never internal shorthand like "attn" — owner style
  ruling), training recipe (e.g. "BC+PPO"), and the display line served to
  clients (e.g. "Transformer · BC+PPO").
- **FR-002**: The registry MUST ship with rows for the three currently
  certified artifacts (User Story 2, scenario 1), with shas taken verbatim
  from `policies/README.md`'s Active table. Anticipated forward values
  ("Scripted" for builtins; "Transformer · BC+PPO+leash" for phase-1 lineage
  seats if the leash doctrine lands) are documentation, not rows — rows exist
  only for real artifacts.
- **FR-003**: Registry maintenance is part of the artifact's change: a PR that
  lands a new `.ckpolicy` at `policies/` top level MUST add its row in the
  same PR (Experiments authors the row at certification time — their
  seating-checklist line). Retirement keeps the row. This process rule MUST be
  stated in `policies/README.md`.
- **FR-004**: At startup, for each seated policy artifact, the server MUST
  resolve the artifact's sha256 against the registry and attach the row's
  display line to every kitty driven by that artifact, as a new field on the
  served kitty object, `behavior_description` (name finalized — plan research
  D6), on **every**
  surface that serves kitty objects carrying `behavior` today (read API and
  live stream alike). The `behavior` string itself is unchanged (FR-009).
- **FR-005**: Kitties on built-in behaviors (`needs_driven` and the scripted
  builtins) MUST serve the fixed description "Scripted" with no registry row.
  Kitties on plugin behaviors serve no description (field absent).
- **FR-006**: The description is presentation-only and served verbatim: the
  server MUST NOT parse, derive, or transform it beyond the registry lookup,
  and the client contract is render-verbatim with fallback to the model id
  when the field is absent. (Client-side rendering is the Client thread's
  work; this spec defines only the served contract.)
- **FR-007**: Seating an artifact whose sha256 has no registry row MUST
  **refuse startup** with an error naming the artifact path and sha256
  (owner ruling, 2026-08-15) — the same doctrine as every other config
  validation failure here (unknown behavior name, missing artifact, schema
  mismatch, missing plugin binary), and the enforcement arm of
  `policies/README.md`'s existing rule that a file without a row is a
  deployment error. No warn mode, no opt-out. Refusal cannot strand the
  frozen box: the new binary reaches it only at the phase-1 rollout, whose
  artifacts get rows at certification per FR-003.
- **FR-008**: A repository test MUST enforce registry integrity independent of
  any seating: the registry parses, rows carry all required fields, no
  duplicate keys, and every `.ckpolicy` at `policies/` top level has a row
  whose key equals the file's actual sha256 (the release-honest pattern —
  CI fails the PR that lands an artifact without its row, even during a wall
  window when no seat is live).
- **FR-009**: The exact model id MUST remain served exactly as today (the
  `behavior` string, verbatim on `GET /config` and kitty objects) — demoted in
  presentation, never removed. Nothing this spec adds may alter any existing
  served field.
- **FR-010**: `policies/README.md`'s Naming section MUST be amended: the
  standing pointer "the human-readable description belongs … in a served field
  on `[rl.policy.*]`" is superseded by the registry (that placement is now a
  rejected alternative), and the don't-add-`description =` warning stays, now
  citing this spec.
- **FR-011**: No stamp, schema, or fingerprint movement: the new field is
  additive on served kitty objects; the registry is not part of `Config`, does
  not move `Config::fingerprint`, and requires no `--fresh`. The plan MUST
  verify this (constitution check), and the CHANGELOG entry carries no
  `[stamp]`/`[obs-schema]` marker.

### Key Entities

- **Registry row**: sha256 (key, the artifact's identity) → architecture,
  recipe, display line. Lives in one machine-readable file in `policies/`,
  beside the artifacts and their README ledger.
- **Behavior description**: the display line, attached per-kitty at
  startup/seating resolution, served read-only alongside `behavior`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every kitty in a served world, a viewer can read the kind of
  mind and training recipe in plain words (or "Scripted") without knowing any
  internal run id; verified end-to-end by booting the shipped config and a
  policy-seated test config and inspecting served kitty objects.
- **SC-002**: Every artifact at `policies/` top level has a matching registry
  row; a PR adding an artifact without one fails CI (test named in FR-008).
- **SC-003**: Existing clients and every existing served field are unchanged:
  the full pre-existing test suite passes without modification to any
  assertion about current fields.
- **SC-004**: Registry resolution happens once per artifact at
  startup/seating — zero per-tick lookup cost; serving overhead is one short
  string per kitty object.

## Rejected Alternatives *(owner-reviewed — do not re-derive)*

- **Hand-set free text in the served config** (e.g. `description =` on
  `[rl.policy.*]`): drifts from the artifact it describes, and presentation
  strings don't belong in a stamped, constitution-guarded surface. Also
  refused mechanically today (`deny_unknown_fields`).
- **Artifact-header metadata as the sole mechanism**: `policies/` artifacts
  are byte-identical forever — deployed v2/v3 artifacts can never gain the
  field. (An optional display block in the artifact contract for *future*
  exports, with the registry as backstop for the past, was noted as a
  reasonable future rider; out of scope here — the registry alone is
  sufficient and authoritative.)

## Assumptions

- Field name `behavior_description` — final (naming was delegated to Product
  in the owner-approved shape; settled at plan review, research D6). It
  extends the existing `behavior` field it rides beside.
- Plugin-driven kitties serve no description rather than a false "Scripted"
  (no certification record exists for an external process); the client's
  existing fallback covers them.
- Registry rows are append-and-keep: retirement and renames never remove or
  edit a row's key (sha is identity, matching the README's rename rule).
- Deployment timing: this is a server-binary change landing on main inside
  the open generation wall; the frozen box gains it at the phase-1 rollout
  (only `--client-only` deploys are safe until then). Nothing in this spec
  touches the box now. Merging the registry file and rows is safe
  immediately.
- Sizing per Experiments: small and independent — may ride the phase-1
  rollout or merge before it.
