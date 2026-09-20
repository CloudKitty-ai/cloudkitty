# Feature Specification: The wire's DecisionRequest on the lab binding

**Feature Branch**: `055-lab-decision-request`

**Created**: 2026-09-19

**Status**: Draft

**Input**: User description: "Expose the spec 053 DecisionRequest, rendered exactly as the served wire sends it, per kitty per tick, on the Python binding (lab env). One shared core helper renders DecisionRequest from a DecisionContext; one opt-in binding surface returns the rendered JSON line per kitty; a byte-comparison test proves server path and binding path render identically; one doc sentence in docs/plugins.md. The spec must settle the seed-draw design point. Handover: experiments/llm-lab-seat/HANDOVER-product-2026-09-20.md."

## Why (one paragraph)

LLM seats are tested first in the lab's tickless world (owner, 2026-09-20;
served-world LLM seats are tabled). The served wire hands an advisor a JSON
document — the spec 053 `DecisionRequest` — while the lab hands a seat an
observation vector and a mask. If the lab prompt is rendered by separate
Python, the two texts drift, and a lab result stops predicting the served
seat (F-042: a lab read predicts the served seat only when both read the
same thing). The model must be able to read the wire's own text in both
places.

## Clarifications

### Session 2026-09-20

- Q: Should the lab render carry the exact seed the served request
  would, computed without consuming the kitty's private decision
  stream? → A: Yes — render without consuming (D1 CONFIRMED by the
  owner; FR-005 stands as written).
- Q: Should the surface be a pull method the harness calls per kitty
  (`env.decision_request(kitty_id)`), rather than a rendered line
  delivered automatically in `infos` behind an env flag? → A: Yes — the
  pull method is the surface (owner-confirmed); nothing renders unless
  asked, which subsumes FR-003's opt-in.
- Q: When the method is called where no request exists (unknown kitty
  id, before the first decision point, after the episode ends), should
  it raise a clear error rather than return an empty or placeholder
  value? → A: Yes — always a clear error naming the kitty and why
  (owner-confirmed); never None, never stale or placeholder bytes.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The lab prompt is the served prompt (Priority: P1)

An experimenter running the lab env asks, for any roster kitty at any tick,
for the decision request exactly as the served wire would send it — same
fields, same values, same bytes. They feed that text to a model under test
and trust that a result in the lab transfers to a served seat behind the
HTTP door.

**Why this priority**: this is the whole ask. Without byte fidelity the
surface is worse than nothing — it would *look* like the wire and quietly
not be it, which is the drift F-042 exists to warn about.

**Independent Test**: build one decision's inputs (world, tick, kitty, dealt
seed, config), render it through the server's path and through the binding's
path, compare the bytes.

**Acceptance Scenarios**:

1. **Given** the same start-of-tick world, tick, kitty, dealt seed, and
   config, **When** the request is rendered through the served path and
   through the lab surface, **Then** the two JSON lines are byte-identical.
2. **Given** a kitty with friends both inside and outside its vision disc,
   **When** its request is rendered on the lab surface, **Then** the
   `world` field is that kitty's fog view (in-disc entities plus global
   meows, friends' memory blanked) and never the full world.
3. **Given** a rendered request, **When** its fields are read, **Then**
   they are exactly the documented seven (`v`, `tick`, `kitty_id`, `me`,
   `world`, `seed`, `config`) with `v` equal to the current proposal wire
   version — no lab-only extras.

---

### User Story 2 - Policy seats pay nothing (Priority: P2)

An experimenter running ordinary policy-seat training or certification
opens the env exactly as today and sees identical behavior and cost: no
request is rendered unless asked for.

**Why this priority**: rendering the full snapshot and config per kitty per
tick is a real serialization cost; the certification and training loops are
hot paths that must not slow down for a surface they never read.

**Independent Test**: open the env without the surface and confirm no
request rendering occurs and existing outputs are unchanged.

**Acceptance Scenarios**:

1. **Given** an env opened without requesting the surface, **When** an
   episode runs, **Then** no decision request is rendered and the episode's
   observations, rewards, and infos are unchanged from before this feature.
2. **Given** an env opened with the surface, **When** an episode runs with
   the same seeds, **Then** the trajectory (positions, actions, RNG
   sequence) is identical to the same episode without the surface — reading
   the render never moves the world.

---

### User Story 3 - Lab users can find it (Priority: P3)

A reader of the plugin docs learns that the lab binding can hand them the
same request text the wire sends, so they build their harness against the
documented shape instead of reimplementing it.

**Why this priority**: one sentence of docs; valuable but nothing blocks on
it.

**Independent Test**: the plugins doc names the lab surface in its request
section; the wire text itself is unchanged.

**Acceptance Scenarios**:

1. **Given** `docs/plugins.md`, **When** the request section is read,
   **Then** one sentence points lab users at the binding surface, and no
   other wire documentation changed.

---

### Edge Cases

- Asking for a kitty id not on the roster: a clear error, never a partial
  or empty render.
- Asking before the first tick's decision point or after an episode ends:
  a clear error naming the kitty and why (owner-confirmed at clarify) —
  never None, never stale bytes from a previous tick.
- The request must render against the same start-of-tick snapshot the
  seats decide against (snapshots are post-apply; a render taken after
  `step` must not leak the post-step world into a request stamped with the
  decided tick).
- Two kitties sharing a tick: each render carries that kitty's own fog
  view and its own private-stream seed; renders never share or swap.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: One renderer, two callers. The served wire path and the lab
  surface MUST produce their request text through the same shared
  rendering, so the two cannot drift. After this change the served wire's
  bytes MUST be identical to what it sends today (no version bump, no
  field change, no new config key).
- **FR-002**: The lab binding MUST expose, per roster kitty per tick, the
  decision request rendered exactly as the served wire would send it for
  that kitty's decision at that tick — regardless of what kind of seat the
  kitty holds in the lab.
- **FR-003**: The surface is a pull method (`env.decision_request(kitty_id)`
  or the binding's idiomatic equivalent, owner-confirmed at clarify):
  nothing renders unless called, so an env that never calls it performs
  no request rendering and behaves identically to today.
- **FR-004**: The rendered `world` MUST be the deciding kitty's fog view
  and nothing more (design doctrine rule 5; spec 049 FR-048 — the request
  is the fog snapshot by construction).
- **FR-005** (the seed draw, D1 below): the rendered `seed` MUST be the
  value the served seat's request would carry — the first draw of the
  kitty's private decision stream for that tick — derived **without
  consuming** the stream. Rendering MUST NOT change any lab trajectory:
  the same seeds give the same episode whether or not anyone reads the
  surface.
- **FR-006**: A test MUST prove FR-001 by byte comparison: the same
  decision inputs rendered through the server path and the binding path
  compare equal as bytes, with the red half proven via the house mutation
  cycle (`scripts/mutate.sh`).
- **FR-007**: `docs/plugins.md` MUST gain one sentence pointing lab users
  at the surface; no other wire documentation changes.

### Key Entities

- **Decision request**: the spec 053 wire document — `v`, `tick`,
  `kitty_id`, `me`, `world` (fog view), `seed`, `config` — one JSON line,
  serialized with the engine's own field order.
- **Decision context**: everything one kitty's decision is made against:
  its own state, its fog view of the start-of-tick world, its private
  decision stream, the config. Both the served seat and the lab build one
  per kitty per tick; this feature makes both render the same document
  from it.
- **The lab surface**: the binding-side accessor (per kitty, per tick,
  opt-in) that returns the rendered line.

## Design decisions

- **D1 — the seed is rendered, not consumed.** Article V says the served
  seat's draw advances the kitty's stream whether or not the advisor
  answers. The lab's policy seats never touch that stream, and the handover
  offers two options: consume the draw as the served seat would, or render
  the value without consuming. This spec picks **render-without-consume**:
  the surface derives the exact value the served request would carry (the
  first draw of the private stream seeded by that kitty's dealt seed) while
  leaving the stream untouched. Rationale: (a) the bytes are identical to
  the served request either way, so fidelity loses nothing; (b) a lab world
  then has one trajectory regardless of who reads the surface, which keeps
  `llm:`-seated and policy-seated control runs step-comparable and keeps
  FR-003's "identical behavior" simple and testable; (c) consuming would
  make merely *observing* the request move the world — an instrument that
  perturbs what it measures. The served condition (where the draw does
  advance the stream) is reproduced by the harness actually seating an
  advisor, which is the experiment, not the render. Owner may overrule at
  review; the change is localized to this one rule.

## Doctrine check (CLAUDE.md rule 8)

Checked against `experiments/DESIGN-DOCTRINE.md`:

- **Rule 5** (a teacher may only act on what the student can see) moved
  FR-004: the rendered request is the fog view by construction, so
  anything trained or evaluated from it can never see more than a seat
  sees.
- Rules 1–4 and 6–10 moved nothing: this feature prices nothing, scripts
  nothing, and adds no reward or behavior — it exposes an existing
  document on a new surface.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every kitty and tick sampled in the comparison test, the
  lab-rendered request and the served-path request are byte-identical
  (100% of sampled decisions, zero tolerated diffs).
- **SC-002**: An episode run with the surface enabled and the same seeds
  reproduces the identical trajectory as one run without it (zero
  divergent ticks).
- **SC-003**: The served wire is provably unchanged: existing wire and
  config guards (including the `--include='*.toml'` config sweeps) pass
  untouched, and no wire version bump ships.
- **SC-004**: Experiments' acceptance list from the handover is satisfied:
  the comparison test with its mutation red, the doc sentence, and a
  surface their harness can call the day it lands.

## Assumptions

- The handover (`experiments/llm-lab-seat/HANDOVER-product-2026-09-20.md`,
  owner-directed) is the source of intent; the brainstorm notes
  (`BRAINSTORM-2026-09-20.md`) are context for #392 and add no engine scope
  here.
- D1 (render-without-consume) is this spec's call, flagged for the owner;
  Experiments stated no preference and will not rely on the seed beyond
  the documented tie-break.
- "Per tick" means at the tick's decision point: the render is against the
  same start-of-tick snapshot the seats decide against.
- The accessor is the pull method (owner-confirmed at clarify); only its
  idiomatic surface details (naming, error type) are plan-time choices.
- Harness-side work (LLM seat spec, batching, journal, prompt prefix,
  retries) is Experiments' and out of scope; no LLM code enters the
  engine.
