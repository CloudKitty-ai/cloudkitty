# Feature Specification: Config Restructure — Table-Driven Validation, Navigable Layout

**Feature Branch**: `020-config-restructure`

**Created**: 2026-07-26

**Status**: Draft

**Input**: User description: "Restructure the core engine's configuration module: table-driven validation and a navigable layout. The configuration module is the second-largest file in the codebase (~1,800 lines) and its growth is mechanical: the validation error constructor is invoked 46 times, including roughly 13 verbatim copies of the same 7-line \"value must be at least N\" guard; one catch-all validator function has grown to ~170 lines and actually validates six unrelated configuration sections despite its name; and the file interleaves two distinct concerns — about twenty default-value functions and nine per-section validators — in one flat expanse. The file already demonstrates the fix in miniature: two existing validators use a table-loop pattern where each bounded field is one table row. Goal: (1) collapse the repeated guard boilerplate into the table-driven form the file already uses, so adding a new bounded config field costs one row instead of a new 7-line block, and the catch-all validator is dissolved into per-section validators matching the config's own section structure; (2) split the module so defaults and validation each have a navigable home. Constraints: every validation rule must be preserved exactly — same accepted configs, same rejected configs, same error messages verbatim (validation errors are user-facing; operators see them when a config is wrong) — verified by the existing unit suite passing unchanged plus a systematic before/after check that every invalid-config rejection message is byte-identical. Serde behavior (accepted TOML shapes, default values, unknown-field handling) must be completely unchanged. No new config fields, no changed defaults, no changed bounds. This is a navigability and change-cost refactor of the engine's most-edited file."

## The problem in one paragraph

Every feature that adds a tunable touches the configuration module — the
constitution requires tunables to be named in config, so this is the
engine's most-edited file — and each bounded field currently pays a
seven-line toll: the same "value must be at least N" guard, copied and
lightly edited, roughly thirteen times so far, among forty-six hand-built
validation-error constructions. One validator has quietly become a
170-line catch-all for six unrelated sections, and the module interleaves
two unrelated jobs (what values default to, and what values are allowed)
across ~1,800 flat lines. The file itself already knows the answer: two of
its validators use a table where each bounded field is one row. This
feature finishes that thought — every mechanical guard becomes a table
row, every section gets its own honestly-named validator, and defaults and
validation each get a home — without changing a single accepted config, a
single rejected config, or a single character of the error messages
operators see.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Adding a bounded field costs one row (Priority: P1)

As a maintainer adding a new tunable with a simple bound (a minimum, a
range), I add the field, its default, and one table row naming its bound —
and validation, with a correctly formatted user-facing error message,
follows from the row. No new guard block, no new hand-written error
string.

**Why this priority**: This is the recurring cost. Article VI sends every
new tunable through this module; the per-field toll compounds with every
feature. Collapsing it is the reason this refactor pays for itself.

**Independent Test**: During development, add a throwaway bounded field via
a single table row; confirm an out-of-bounds config is rejected with a
correctly formatted message and an in-bounds config is accepted; remove the
throwaway field before landing (the walkthrough and its outcome are
recorded in the feature's validation notes).

**Acceptance Scenarios**:

1. **Given** the restructured module, **When** the recorded walkthrough
   adds a hypothetical bounded field, **Then** exactly one table row (plus
   the field and its default) is required, and the rejection message
   format matches the existing message family without any hand-written
   error construction.
2. **Given** every configuration the current engine accepts or rejects,
   **When** the restructured module validates it, **Then** the outcome is
   identical — accepted stays accepted, rejected stays rejected, and every
   rejection message is byte-identical to today's.

---

### User Story 2 - Validators match the config's own structure (Priority: P2)

As a maintainer looking for where a section's rules live, I find one
validator per configuration section, named for that section — the
170-line catch-all that silently validated six unrelated sections is gone,
its rules redistributed to honestly-named homes.

**Why this priority**: Navigability of the rules themselves. Finding the
right place to add or change a rule currently requires knowing the
catch-all's undocumented true scope; after the change, the config's own
section structure is the map.

**Independent Test**: Review confirms each configuration section's rules
live in a validator named for that section; no validator checks fields
outside its named section; the catch-all no longer exists.

**Acceptance Scenarios**:

1. **Given** any configuration section, **When** a reviewer looks for its
   rules, **Then** exactly one section-named validator contains them, and
   no validator validates fields belonging to a differently-named section.

---

### User Story 3 - Defaults and validation each have a home (Priority: P3)

As a maintainer, the module's two jobs live apart: the default-value
definitions in one place, the validation rules in another, with the shared
type definitions clearly primary. Finding either no longer means scrolling
an 1,800-line flat file.

**Why this priority**: Pure navigability; valuable but delivers no new
protection — hence last.

**Independent Test**: Review confirms the split exists and every default
and every validator is findable in its stated home; the module's public
surface (what other code imports) is unchanged.

**Acceptance Scenarios**:

1. **Given** the restructured module, **When** other engine code that uses
   configuration types compiles, **Then** no consuming code required
   changes — the reorganization is invisible outside the module.

---

### Edge Cases

- Not every rule is a simple bound: some validation is relational (fields
  compared against each other, capacity checks against world geometry,
  exponent-range logic with real branching). These rules must move to
  their section's validator **as-is** — the table form is only for the
  mechanical guards that already share one shape; forcing relational rules
  into tables would obscure them.
- Error-message formatting must be preserved to the byte, including any
  existing quirks (spacing, bracketed section names, value renderings). If
  the current messages are inconsistent with each other, they stay
  inconsistent — normalizing them is out of scope, because operators and
  any scripts matching on messages see these strings.
- The order in which validation failures are detected is observable (the
  first failing rule's message is the one reported). Reordering rules
  across validators must not change which message a multiply-invalid
  config produces.
- Serialization behavior — accepted TOML shapes, defaults applied to
  omitted fields, unknown-field handling, section names — is entirely out
  of bounds; the restructure touches how rules and defaults are organized,
  never what the parser accepts.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every mechanical bound guard (the repeated "must be at least
  N"-shaped checks) MUST be expressed in the table-driven form the module
  already uses in two places: one row per bounded field, message produced
  by the shared mechanism.
- **FR-002**: The catch-all validator MUST be dissolved: each configuration
  section MUST have exactly one validator named for it, containing all of
  and only that section's rules; relational and branching rules move
  verbatim into their section's validator.
- **FR-003**: The module MUST be organized so default-value definitions
  and validation rules each have a distinct, findable home, with the
  configuration types remaining the module's clearly primary content.
- **FR-004**: Validation outcomes MUST be preserved exactly: every
  configuration accepted today is accepted, every configuration rejected
  today is rejected, and every rejection message is byte-identical —
  including which message is reported for configurations that violate
  multiple rules.
- **FR-005**: Parsing and defaulting behavior MUST be completely
  unchanged: accepted document shapes, defaults applied to omitted fields,
  unknown-field handling, and section naming are all out of scope and
  unmodified.
- **FR-006**: The module's public surface MUST NOT change: no consuming
  code elsewhere in the engine, server, tools, or bindings requires any
  modification.
- **FR-007**: All existing automated tests MUST pass without modification
  to their assertions; no test may be weakened or deleted.
- **FR-008**: Behavior preservation MUST be verified systematically, not
  by spot-check: an enumerated before/after comparison covering every
  distinct rejection path (each rule that can fire, exercised by a
  minimally-invalid configuration) MUST show byte-identical messages, and
  the procedure and results MUST be recorded in the feature's quickstart
  validation document.
- **FR-009**: No configuration fields, defaults, or bounds may be added,
  removed, or changed. (The development-time walkthrough field of User
  Story 1 is added and removed within the feature branch and MUST NOT
  land.)

### Key Entities

- **Configuration section**: a named group of related tunables (world,
  roster, needs, thresholds, behavior, and so on); the unit validators are
  organized around.
- **Bound rule**: a mechanical constraint on one field (minimum, range)
  expressible as a table row; the repeated shape this feature collapses.
- **Relational rule**: a constraint spanning fields or requiring real
  logic; preserved verbatim, relocated to its section's validator.
- **Rejection message**: the user-facing text an operator sees for an
  invalid config; the byte-stable artifact defining behavior preservation
  here.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero verbatim copies of the mechanical bound-guard shape
  remain; every such rule is one table row (the ~13 copies and the
  46-site error-construction count from the 2026-07-26 survey read as
  resolved, with hand-built constructions remaining only where a rule is
  genuinely relational).
- **SC-002**: No validator validates more than its named section; the
  170-line catch-all no longer exists; every section's rules are findable
  in one section-named place.
- **SC-003**: The enumerated rejection-path comparison shows byte-identical
  messages for every distinct rule, before vs. after (100% of rejection
  paths covered, zero differences).
- **SC-004**: The full existing automated test suite passes with zero
  assertion changes, and no code outside the configuration module changed.
- **SC-005**: The recorded walkthrough demonstrates a new bounded field
  costs one table row, with its error message produced by the shared
  mechanism.

## Assumptions

- The two existing table-loop validators define the house pattern; this
  feature extends that pattern rather than inventing a new mechanism.
- "Byte-identical rejection messages" is achievable because messages are
  deterministic functions of the config values; any message discovered to
  embed nondeterministic content would be surfaced as a finding, not
  silently accommodated.
- The behavior-preservation bar (unchanged tests plus the enumerated
  rejection-path comparison) stands in for new test development; the
  enumerated comparison itself may be retained as a regression fixture if
  cheap, at the implementer's discretion recorded in the plan.
- The engine's other large files (world, action) are out of scope; this
  feature touches the configuration module only.
- The RL crate's separate configuration module (which has its own similar
  but smaller validator) is out of scope; if this restructure proves the
  pattern, that module is a follow-up candidate noted for the backlog,
  not part of this feature.
