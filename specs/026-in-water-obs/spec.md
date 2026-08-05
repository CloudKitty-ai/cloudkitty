# Feature Specification: Observation Schema 2 — the In-Water Self-Signal and Raised Wet-Fur Pricing

**Feature Branch**: `026-in-water-obs`

**Created**: 2026-08-05

**Status**: Draft

**Input**: User description: "Observation schema generation 2: the
in-water self-signal and the raised wet-fur pricing (pre-exp-003 batch
items 1+2 from HANDOFF-2026-08-05-pre-exp-003-world-batch.md). Add an
explicit in-water flag to the observation self block (schema 1→2,
length 182→183), raise [water] bath_gain 1.5→3.5 and bath_gain_ceiling
50→65 (owner-decided 2026-08-05), and make the schema-mismatch boot
failure legible. Lands on main freely; must not be deployed before a
schema-2 winner exists."

## The generation framing *(read first)*

This is exp-003's reason to exist, taken as a deliberate,
all-at-once generation break. A kitty standing in water today cannot
*see* that it is standing in water: sunbeam occupancy has an explicit
self-block flag, but water occupancy must be inferred from the
nearest-water slot sitting at distance 0 — an inference PPO must
discover rather than a fact it is handed. Adding the flag is the
§4-forbidden schema change that voids every warm start, so it opens a
new artifact generation: observation schema 1 → 2, observation length
182 → 183, no compatibility shim in either direction.

The pricing rides in the same break on the exp-002 evidence: the §9.1
dial resolution failed its gates at both bath_gain 1.5 and 2.5, and the
measured slope (≈ −0.84 pp lounging per dial unit) extrapolates to a
dial near 5 to reach the gates by penalty alone. The bit and the
penalty therefore ship *together* — the owner set the pair at **3.5**
with ceiling **60** (2026-08-05, see Clarifications): substantial
without being gate-reaching on its own, and a higher ceiling so the
*accumulated* happiness cost of lounging is large enough for PPO to
learn from.

Deployment posture (owner, 2026-08-05): the served box keeps its
schema-1 binary and config until a single hand rollout after exp-003.
Both deployed policies (`e001-a2-s6`, `e002-m0-g998-s1`) are schema-1
and 182-wide; a schema-2 binary refuses them at boot, by design. Merge
freely, deploy never — until a schema-2 winner exists. Nothing
deploys mid-soak.

## Clarifications

### Session 2026-08-05

- Q: The owner's dial pair (3.5/65) fails certification-hygiene
  validation against the FROZEN exam `evals/v1/heterogeneity.toml`
  (its 4x-bath Miso draws a 14-point charge; 65 + 14 = 79 >= 75), and
  the exam can never be edited. Resolve the ceiling? -> A: **3.5 / 60**
  (owner). Keeps the gain; the ceiling drops to the exact roofline the
  frozen suite permits (60 + 14 = 74 < 75). The Input block above
  quotes the original 65 as history; every requirement in this spec
  uses 60.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A kitty can see that it is wet (Priority: P1)

Every observation a learned kitty receives carries an explicit
signal for "I am standing on a water tile right now", the same way it
already carries "I am standing in a sunbeam". The signal is a fact
about the frozen start-of-tick world, not an inference over the
nearest-water slots.

**Why this priority**: This is the schema change itself — the single
reason a new artifact generation exists and exp-003's hypothesis
depends on it.

**Independent Test**: Encode observations for a kitty placed on a
water tile and on a grass tile; assert the flag reads 1 and 0
respectively, that the vector is exactly one value longer than
generation 1, and that nothing else in the layout moved.

**Acceptance Scenarios**:

1. **Given** a kitty whose tile holds a water element at the
   start-of-tick snapshot, **When** its observation is encoded,
   **Then** the in-water flag is 1.0.
2. **Given** a kitty on any tile without a water element, **When** its
   observation is encoded, **Then** the in-water flag is 0.0 — even if
   water is adjacent, and even if the kitty's activity is
   water-related.
3. **Given** the default slot configuration, **When** the observation
   length is computed, **Then** it is 183, and the declared observation
   schema version is 2.
4. **Given** any non-default slot configuration, **When** the
   observation length is computed, **Then** it is exactly one greater
   than generation 1's length for the same slots (the flag lives in
   the self block, which every configuration carries once).
5. **Given** the same seed, config, and tick count, **When** the world
   runs twice, **Then** world states are identical — the flag is a
   pure read of existing state and adds no randomness (Article V).

---

### User Story 2 - Lounging in water costs enough to learn from (Priority: P2)

The wet-fur pricing rises so that occupying water is a decision with
teeth: the per-tick charge more than doubles, and the cap on how much
bath pressure water can accumulate rises, so the total happiness cost
of lounging in a pond is large enough to show up in a learner's
reward signal.

**Why this priority**: Owner-committed alongside the bit; the evidence
says neither the bit nor a tolerable penalty reaches exp-003's gates
alone. Ships in the same break so the generation pays one
re-baseline, not two.

**Independent Test**: Boot a world from a config that never mentions
`[water]`; assert the effective dials are the new defaults, that the
boot banner names them, and that the existing certification-hygiene
guard still proves the safeguard threshold unreachable by water alone.

**Acceptance Scenarios**:

1. **Given** a config with no `[water]` section, **When** the world
   boots, **Then** the effective `bath_gain` is 3.5 and
   `bath_gain_ceiling` is 60, and `GET /config` reports both.
2. **Given** the shipped roster (all bath ratios 1.0), **When** config
   validation runs, **Then** it passes: ceiling + largest single
   charge = 60 + 3.5 = 63.5, below the safeguard threshold (75).
3. **Given** a config whose ceiling + largest trait-scaled charge
   reaches the safeguard threshold, **When** validation runs, **Then**
   it is rejected at startup with the existing error naming the cat
   and the remedies (unchanged rule, new arithmetic).
4. **Given** a kitty occupying water with bath already at the ceiling
   (pre-charge), **When** the tick resolves, **Then** no further
   wet-fur charge lands — the ceiling semantics are unchanged, only
   the number moved.
5. **Given** a config that explicitly writes the old values, **When**
   the world boots, **Then** the explicit values win — defaults
   changed, the knob did not.

---

### User Story 3 - The generation wall is legible the day someone hits it (Priority: P3)

When a policy artifact from one generation meets a binary from
another, the refusal message is the entire diagnosis: it names the
artifact file, the generation it carries, the generation the binary
speaks, and the remedy — a re-trained artifact. Under the deployment
posture nobody meets this error for weeks, which is exactly why the
message must stand on its own when someone finally does.

**Why this priority**: Costs a few lines, pays for itself the one day
it fires. The wall itself (fail-fast, no degraded mode) already
exists; this story is only about what it says.

**Independent Test**: Attempt to load a schema-1 artifact under
schema-2 expectations (and the reverse); assert the error text carries
the artifact path, both generation numbers, and the re-train remedy,
and that the server still refuses to boot (exit nonzero, no partial
world).

**Acceptance Scenarios**:

1. **Given** a schema-1 artifact named by a kitty's seat, **When** a
   schema-2 server boots, **Then** boot fails and the error names: the
   artifact path, the policy name it resolved, schema found (1) vs
   expected (2), and that a re-trained artifact is required.
2. **Given** an artifact whose declared schema matches but whose first
   layer is 182-wide, **When** a schema-2 server boots, **Then** boot
   fails and the error carries the same context (path, policy name,
   widths found vs expected, remedy) — the shape gate is as legible as
   the schema gate.
3. **Given** a schema-2 artifact, **When** a schema-1 binary loads it,
   **Then** the refusal is symmetric and equally legible (found 2,
   expected 1).
4. **Given** any of these failures, **When** boot aborts, **Then** no
   degraded or partial mode exists — the fail-fast posture is
   unchanged (Article IV: a missing advisor is a config error at
   startup, not a runtime fallback).

---

### User Story 4 - Main stays runnable between the break and the rollout (Priority: P2)

Anyone who clones the repository and runs the server gets a working
world on the day this merges — even though the two committed policy
artifacts are schema-1 and cannot load under the new binary. The
default world seats those two kitties on scripted behaviors until
schema-2 winners exist; the artifacts, their `[rl.policy]` blocks, and
their provenance records stay in place, because unreferenced policy
blocks never open their artifacts.

**Why this priority**: Without it, merging the break makes a fresh
clone unbootable for the whole exp-003 window — which also breaks the
Client thread's local server workflow on next pull. Same priority
tier as the pricing: the break is not safe to land without it.

**Independent Test**: From the merged tree, boot the server with the
repo's default config; assert it serves a world with all four kitties
acting, and that no artifact file was opened.

**Acceptance Scenarios**:

1. **Given** a fresh clone at the merged commit, **When** the server
   boots with the default config, **Then** it serves the world —
   no schema error, because no kitty references a policy.
2. **Given** the default config, **When** the roster is inspected,
   **Then** Miso and Kittybear run scripted behaviors, with config
   comments naming the parked artifacts and the condition for
   re-seating (a schema-2 winner from exp-003).
3. **Given** the `policies/` directory, **When** its README is read,
   **Then** it records that both artifacts are generation 1, why they
   are temporarily unseated, and that the served box (schema-1 binary)
   still runs them until the post-exp-003 rollout.

---

### Edge Cases

- **Tile occupancy, not activity**: the flag keys on a water element
  occupying the kitty's tile in the snapshot — a kitty "swimming" by
  activity on a tile whose water expired reads 0; a kitty idling on a
  puddle reads 1. One definition, no special cases.
- **Sunbeam and water flags are independent by construction**:
  elements are one-per-tile, so both flags can never be 1 together —
  but neither flag consults the other, so a future multi-element tile
  would not silently break either.
- **Configs that validated yesterday may fail today**: the ceiling
  raise shrinks trait headroom — a cat with bath rise > ~4.28× the
  baseline now trips the certification-hygiene guard that passed at
  ceiling 50 (headroom was ~16.7×); the frozen heterogeneity exam's
  4× cat sits just inside the new roofline, and deliberately so. That is the guard doing its job;
  the existing error names the cat and the remedies. Called out in
  the config comments so an operator meeting it can orient.
- **Water with a TTL**: default puddles are permanent, but water may
  be configured with a TTL; the flag reads whatever the snapshot
  holds, so an expiring tile reads 1 up to and including its last
  snapshot and 0 after — no smoothing, no memory.
- **Both gates stay independent**: an artifact could declare schema 2
  yet carry a 182-wide first layer (a mis-built file); the schema gate
  and the shape gate each reject on their own, and both must be
  legible (US3 scenario 2).
- **The engine-defaults stamp moves**: changing shipped defaults
  changes `engine_defaults_sha256`, killing every anchor keyed to
  `12bf386241…`. Expected and planned — this batch is the
  generation's break, and §4 of the handoff sequences the
  re-baseline. Not this spec's job to re-measure; its job is to not
  pretend the stamp survives.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The observation self block MUST carry an explicit
  in-water flag: 1.0 when a water element occupies the observing
  kitty's tile in the start-of-tick snapshot, 0.0 otherwise. The flag
  MUST be a pure function of the snapshot (no randomness, no history)
  and MUST sit in the self block adjacent to the existing in-sunbeam
  flag, with the rest of the layout unmoved.
- **FR-002**: The observation schema version MUST advance from 1 to 2
  and the default-slot observation length from 182 to 183 in the same
  change. The length increase MUST live in the self block so it
  applies exactly once under every slot configuration.
- **FR-003**: Artifact validation MUST keep its two independent gates
  — declared schema version, and first-layer width against the
  compiled observation length — and each MUST reject a generation-1
  artifact on its own. No dual-schema loading, no conversion, no
  degraded mode: an artifact from another generation is a startup
  error, never a runtime fallback (Article IV posture unchanged).
- **FR-004**: The default `[water] bath_gain` MUST become 3.5
  (was 1.5). The charge semantics — per occupied tick, trait-scaled by
  the cat's bath rise relative to baseline, stopped at the ceiling —
  MUST NOT change.
- **FR-005**: The default `[water] bath_gain_ceiling` MUST become 60
  (was 50). The ceiling's pre-charge gate semantics MUST NOT change.
- **FR-006**: The certification-hygiene validation rule (ceiling plus
  largest trait-scaled single charge strictly below the safeguard
  threshold) MUST remain in force unaltered and MUST pass at the new
  defaults for the shipped roster (63.5 < 75) and for every frozen
  exam — heterogeneity.toml's 4× bath cat binds it (60 + 14 = 74 < 75).
- **FR-007**: A schema or shape refusal at artifact load MUST report,
  in one message: the artifact's file path, the policy name being
  resolved, what the artifact carries versus what the binary expects
  (schema numbers, or layer widths), and the remedy — that an
  artifact re-trained for this binary's generation is required.
- **FR-008**: The repository's default world MUST boot and serve on
  the generation-2 binary from the merged commit onward: the two
  policy-seated kitties revert to scripted behaviors until schema-2
  artifacts exist. The `[rl.policy]` blocks, the committed artifacts,
  and their provenance records MUST remain in place (unreferenced
  blocks never open their artifacts), with comments stating why the
  seats are parked and what re-seats them.
- **FR-009**: Documentation MUST move with the change: the normative
  observation-layout doc gains the flag and the new length, the
  config's `[water]` commentary explains the new numbers and the
  owner's rationale (accumulated-cost signal for learning), and
  `policies/README.md` records the generation gap and the deployment
  posture.

### Key Entities

- **Observation (generation 2)**: the fixed-size per-kitty vector; the
  self block grows by one flag (in-water), everything else — kitty
  slots, element slots, meow digest, clock — is unchanged from
  generation 1.
- **Policy artifact**: a trained network file stamped with the
  observation schema it was trained against; generation-1 artifacts
  remain valid history (and remain deployed on the served box) but are
  unloadable by a generation-2 binary.
- **Wet-fur pricing**: the `[water]` dial pair; per-tick charge 3.5,
  accumulation ceiling 60, trait-scaled, safeguard-bounded by
  validation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An observation encoded for a kitty on a water tile
  reads flag 1.0; on any other tile 0.0; the default-slot vector is
  exactly 183 long; every value before and after the flag matches
  generation 1's layout.
- **SC-002**: Both committed generation-1 artifacts are refused by
  the new binary at boot with a message containing the artifact path,
  both generation numbers, and the word "re-train" (or equivalent
  remedy phrasing); the server exits with a failure status and serves
  nothing.
- **SC-003**: A fresh clone at the merged commit boots the default
  world with zero configuration and serves all four kitties.
- **SC-004**: A config that never writes `[water]` reports gain 3.5 /
  ceiling 60 on `GET /config`, and the boot banner names the same
  values.
- **SC-005**: The full test suite passes; determinism holds (same
  seed + config + ticks → identical world state, asserted by the
  existing suite); no Article I–III property test weakens.

## Assumptions

- **Deployment posture** (owner, 2026-08-05): merge is not deploy.
  The served box stays on its schema-1 binary and config until one
  hand rollout after exp-003; the 48h+ Stage-2 soak running since
  2026-08-04 is against schema-1 and is not interrupted. Nothing in
  this spec touches the served box.
- **Dial magnitudes** (owner, 2026-08-05): 3.5 / 60, chosen so the
  penalty is substantial but not gate-reaching alone (keeping a gate
  pass attributable to the bit + penalty jointly) and the raised
  ceiling extends the accumulated cost PPO can observe. Recorded here
  so the pair is legible later.
- **Temporary reseat vs. the 2026-07-31 decision**: "a fresh clone
  serves the roster as-is" is honored in its intent — the clone boots
  and serves — but the roster runs scripted until exp-003 produces
  schema-2 winners. The seats flip back at rollout. This is the one
  deviation this spec introduces beyond the handoff's text, made so
  the break can land without stranding main.
- **The trainer inherits the pricing by design**: `training.toml`
  writes no `[water]` section, so exp-003's training world picks up
  3.5/60 from defaults with no config edit.
- **Experiments owns the aftermath**: rebuilding the trainer's engine
  binding, re-baselining the measurement stack, and re-measuring the
  anchors keyed to the old stamp (handoff §4) happen after this
  merges and before exp-003's prereg freezes. The policy-seated
  anchors cannot be re-measured on the new engine at all (the seats'
  artifacts are generation-1); that is known and expected.
- **Worldgen changes are a separate spec**: the 2×2 lake and
  edge-avoidance weighting (handoff §3) are spec 027; they move the
  same stamp and merge inside the same batch window.

## Out of Scope

- Any dual-schema or fallback loading path (the posture handles the
  gap by not crossing it).
- Any change to the served box, its config, or its policies.
- The worldgen batch (mandatory lake, edge weighting, feasibility
  validation, spawn-constant config promotion) — spec 027.
- Item 3b of the handoff (minimum same-type element separation) —
  **withdrawn by the owner; deliberately not built**.
- evals/v2 small-world exams (post-exp-003, separate sitting).
- Retraining or re-certifying any policy (exp-003's job).
