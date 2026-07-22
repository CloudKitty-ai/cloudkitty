# Phase 1 Data Model: Multi-Agent RL Readiness

Entities from the spec's Key Entities, made concrete. Field-exact widths
are pinned by the contracts ([contracts/encodings.md](contracts/encodings.md)
carries the normative layouts); this document defines the entities, their
relationships, validation rules, and state transitions. Everything here is
derived from the frozen start-of-tick `WorldSnapshot` (`width`, `height`,
`tick`, `kitties`, `elements`, `recent_meows`) — the same information a
behavior's decision context exposes, nothing more (FR-005).

## Engine-side entities (`cloudkitty-core`)

### JointProposal

One tick's worth of externally supplied proposals.

- **Fields**: map `KittyId → Action` (the existing engine `Action` enum —
  `Move`, `Rest{with}`, `Sleep{with}`, `Groom{target}`, `Eat`, `Drink`,
  `Chase(TargetRef)`, `Play{target}`, `Meow{message}`, `Idle`; `Purr` is
  retired and never proposed).
- **Validation**: none at construction — absence, duplication (last write
  wins at the map level), and malformation resolve per kitty to idle
  inside the tick (Article IV). Unknown kitty ids are ignored with the
  entry reported as unconsumed in the TickReport.
- **Relationships**: consumed by `World::tick_with_proposals`; produced by
  the Episode (from decoded menu indices) or by any external driver.

### TickReport

The honest record of one tick.

- **Fields**: per kitty — `proposed: Action`, `validated: Action` (what
  survived validation; idle if rejected), `applied: Action` (after
  duration enforcement — the rewrite made visible), `provenance:
  PolicyMade | FallbackTaken` (headless dispatch marking, FR-017; for the
  joint-action seam every entry is externally proposed and the mark
  records absent/malformed substitution); plus tick-level `distress_events`
  and `activity_endings` produced this tick.
- **Validation**: totality — every kitty in the roster appears exactly
  once, every tick.
- **Relationships**: returned by both the joint-action seam and the
  headless behavior-driven driver (whose report also carries the
  dispatched proposals, enabling golden parity — research.md R4).

### Decision seeds

- Per-kitty per-tick seeds drawn from the master RNG in stable id order
  before any decision (existing engine discipline, FR-002). Exposed
  read-only through the seam and surfaced in per-agent infos so trainer
  exploration and deploy-time sampling share one stochasticity mechanism
  (FR-015).

## Encoding entities (`cloudkitty-rl`, all versioned)

### ObservationSchema (v1)

Fixed-size per-kitty vector, deterministic function of the snapshot.
Blocks, in order:

1. **Self block**: 6 needs (normalized /100); happiness (/100); position
   (x/width, y/height); activity one-hot (7: idle, resting, sleeping,
   eating, drinking, playing, grooming) + social flag + in-sunbeam flag +
   activity progress (elapsed/min, clamped); distress flags per need;
   pursuit/chase state; **static traits**: 6 per-need rise rates,
   normalized by the configured reference rate (FR-005).
2. **Kitty slots × 3** (config): present flag; relative position (dx, dy
   normalized); distance (normalized); needs (/100); happiness; activity
   one-hot + social flag; **`is-activity-target` bit** (research.md R1).
3. **Element slots** (config: 2 chow, 2 water, 2 sunbeam, 4 critter):
   present flag; relative position + distance; per-kind extras — chow:
   servings (normalized by configured max); sunbeam: remaining-ttl
   fraction and occupied flag; critter: kind bit (bug/greeble), heading
   one-hot for greebles, and **`is-activity-target` bit** (research.md
   R1).
4. **Meow digest**: per learned meow kind (6), recency-weighted presence
   from `recent_meows` plus nearest-emitter direction.
5. **Episode clock**: tick/horizon.

- **Slot fill rule (normative)**: distance-ordered nearest, ties broken by
  id — **except the entity the observing kitty's ongoing activity
  references is always granted a slot in its table** (the referenced
  kitty of a cuddle, co-sleep, groom, or social play in a kitty slot; a
  played-with critter in a critter slot), displacing the farthest
  otherwise-eligible occupant (target-priority, research.md R1). The
  engine-side key is `Activity::partner()` plus the `Playing` element
  target — not `duet_partner()`, which omits co-sleep and groom. Chow,
  water, and sunbeam slots are pure nearest-K (no activity references
  them by identity).
- **Validation**: same snapshot → identical vector (encoder determinism
  test); all values in documented bounds; total size ~160–200 values,
  exact size a constant of the schema version.
- **Relationships**: input to policies (train and deploy — FR-007 single
  implementation); parent of the TargetTable.

### TargetTable

Per-observation mapping from slot indices to concrete identities
(`kitty slot k → KittyId`, `critter slot j → ElementId`), built from the
same snapshot by the same fill rule.

- **Validation**: consistent with the observation's present flags; vacant
  slots map to none.
- **Relationships**: the bridge the ActionCodec uses to decode targeted
  menu entries into engine proposals.

### ActionCodec (v1)

The versioned bijection between the 40-entry flat menu and engine
proposals (normative index table in contracts/encodings.md).

- **Validation**: total both directions — every index decodes to a
  proposal (vacant/stale slots decode to proposals the engine lawfully
  resolves to idle); every proposable action encodes to an index.
  Codec-totality proptest guards both directions.
- **Extensibility doctrine**: the menu grows only by codec version bump;
  indices never repurposed; no reserved indices (spec Assumptions).

### LegalActionMask (v1, versioned with the codec)

40 bits per observation: entry set iff the proposal, made as the world
stood at the start of the tick, would be applied **as proposed** —
validation passes and duration enforcement would not rewrite it.

- **Invariants**: inside an activity's minimum the mask reduces to the
  exact continuation (`enforce_durations` rewrites everything else,
  including same-kind proposals it normalizes); **never all-zero** —
  structural under target-priority (every targeted continuation's entity
  — cuddle/co-sleep/groom/social-play kitty, played-with critter — holds
  a slot; untargeted continuations are untargeted entries). Advisory:
  within-tick contention stays the engine's (a masked-in action that
  loses a contest lawfully idles).
- **Validation**: pure-oracle proptest — for every menu entry, mask
  verdict equals the engine's validate-plus-enforcement verdict, no
  carve-outs (amended FR-018).

### GlobalState (v1, versioned)

Privileged critic view (FR-019): every kitty's full state **without slot
truncation** (needs, happiness, position, activity + partner + progress,
distress, traits), a bounded configured element summary (per-type counts,
total chow servings, positions of the K nearest elements per type to the
world center, K in config), and the episode clock.

- **Validation**: fixed size for a given config; training/evaluation
  consumers only — the deployed behavior type cannot receive it
  (decentralized execution enforced by API shape, not discipline).

## Training entities (`cloudkitty-rl`)

### Episode

- **Fields**: seed, config (immutable after construction), horizon
  (≥ 1 tick; zero rejected at construction), current tick, control map
  (per kitty: `External` or `Builtin(name)` — FR-020 mixed control).
- **Transitions**: `reset(seed)` → fresh world, tick 0, returns
  observations + masks + global state; `step(actions)` → decode external
  actions via codec + target table, resolve scripted kitties from their
  own decision streams, one joint-action tick, returns per-agent
  observations, the broadcast team reward, terminations (all false,
  always), truncations (all false until tick = horizon), infos (applied
  action, survived-validation flag, next mask, decision seed, provenance).
- **Validation**: never persisted; agent set constant for the episode's
  life; stepping after truncation is an error.

### TeamReward (config `[rl.reward]`)

- **Fields**: `p` (power-mean exponent, default 0 = Nash), `epsilon`
  (default 0.01), `mode` (level default | delta), optional potential-based
  shaping table (default off, coefficients in config).
- **Computation**: unclamped happiness per kitty recomputed from needs ×
  configured weights, normalized to [0,1], power mean over the **full
  roster** (scripted kitties included). One scalar, broadcast to every
  external agent.
- **Validation**: strictly increasing and concave for p ≤ 1 (unit tests
  at p = 1, 0, −8); finite value and gradient at zero happiness (ε).

### VectorizedEnvironment

- **Fields**: N independent Episodes (separate seeds/RNGs/worlds), worker
  count (config).
- **Behavior**: batch reset/step fans out across a scoped thread pool with
  the GIL released; results gathered positionally (research.md R6).
- **Validation**: per-world trajectories bit-identical to the same world
  stepped alone (independence test).

## Deployment entities (`cloudkitty-rl` + server wiring)

### PolicyArtifact

- **Format**: single file — JSON header (artifact format version;
  observation, action, mask schema versions; layer shapes; activation) +
  little-endian f32 weight blob; SHA-256 content hash computed at load,
  logged, exposed (FR-016; research.md R3).
- **Validation at startup**: readable, header parses, schema versions
  match the compiled encoders, shapes consistent, hash recorded; any
  failure fails startup with an error naming the config field.

### PolicyBehavior

- **Pipeline** per decision: encode observation (+ target table) → MLP
  forward pass → apply legal-action mask → deterministic selection
  (greedy default; optional sampling from the kitty's own decision
  stream) → decode to proposal. Masked selection is total (mask never
  all-zero); NaN/garbage logits still select an in-range action.
- **Contract**: a non-built-in under the existing behavior seam — served
  world: time budget + panic isolation + fallback; headless: budgetless
  dispatch, provenance-marked (FR-017). No I/O, no awaiting (FR-014).
- **Config wiring**: a kitty's behavior names a configured policy
  (`behavior = "policy:<name>"`, `[rl.policy.<name>] artifact = "path"`),
  validated at startup like any unknown behavior name.

### Welfare metrics (`cloudkitty-rl::welfare`)

The long-run welfare accounting lifted from the CI suite into one shared
module (research.md R7): mean happiness, low-happiness streaks and share,
floor touches, pinned streaks, distress age — consumed by both the
existing long-run test and the evaluation harness, so the gate and the
scorecard are the same code.
