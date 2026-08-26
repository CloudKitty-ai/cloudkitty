# Feature Specification: Rest becomes co-sleep's sibling

**Feature Branch**: `041-rest-cuddle-sibling`

**Created**: 2026-08-26

**Status**: Draft

**Input**: The owner-decided cuddle-economy sibling package
(`experiments/cuddle-economy-handoff-2026-08-26.md`, at f4b3708 or
later — the review amendments are load-bearing). Rest (actual
cuddling) runs zero scenes live because every cuddle rider saturates
the need and rest is the only cuddle route that can be refused. The
fix is one repricing principle — **within each need, one saturating
specialist; every rider partial** — plus making rest structurally
isomorphic to co-sleep. Evidence and derivations are banked and need
no re-deriving: the spec-input doc (+ §10), the need-flow model
(`experiments/cuddle-economy-model/RESULTS.md`), and FINDINGS F-033,
F-031, F-027.

## Clarifications

### Session 2026-08-26

- Q: Should the retired `cuddle_relief` config key remain
  accepted-but-inert, or be deleted so configs carrying it are
  rejected? → A: Keep it accepted-but-inert (deprecated; loading
  succeeds, key has no effect). Owner-ratified.
- Q: How should the drip < mutual tier-order rule be enforced — by
  config validation at load time, or as a documented convention
  only? → A: Convention only — documented in the dial comments, no
  new validation (matches the cosleep pair's existing covenant).
- Q: Should this ship as one PR with two verified steps, or as two
  separate PRs? → A: One PR — split commit first (byte-identical
  continuity check), then the engine sibling + reprice commits,
  reviewed together; stale-comment fixes ride the same PR.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Rest runs like co-sleep (Priority: P1)

A cat with a cuddle need settles beside any adjacent friend and rests.
Nobody is conscripted: the friend keeps doing whatever it was doing,
no refusal is possible, and the scene's value tracks what the friend
is actually doing — a merely-present friend pays a small drip; a
friend who is itself resting or sleeping pays the full mutual rate to
both. Piles of resting and sleeping cats emerge from synchronization,
not from binding, exactly as co-sleep piles already do.

**Why this priority**: This is the package's point. Rest is today the
only cuddle route that can be refused (its share of F-033's
partnered-refusal tax), and the one activity the economy starves.
The sibling shape deletes the refusal structurally instead of
patching it.

**Independent Test**: Unit-level: with the new shape, a rest proposal
toward a busy adjacent friend validates as legal, binds nobody, and
pays the drip tier; the same scene pays the mutual tier on the tick
the partner settles. A cat resting beside a *sleeping* friend
collects the mutual rate from its own side — self-service, no longer
dependent on the sleeper having named it.

**Acceptance Scenarios**:

1. **Given** an adjacent friend who is mid-activity (busy), **When** a
   cat proposes rest-with that friend, **Then** the proposal is legal,
   the friend is not bound and its activity clock is untouched, and
   the rester (and the friend) receive the drip-tier cuddle relief.
2. **Given** a rest scene whose partner is merely present, **When**
   the partner itself begins resting or sleeping, **Then** from that
   tick the scene pays the mutual tier to both parties — resolved per
   tick off the partner's live state, by the same shared predicate
   co-sleep's mutual check uses.
3. **Given** a cat resting beside a sleeping friend that never named
   the rester, **When** the rest scene is serviced, **Then** the
   rester collects the mutual rate from its own slot (the symmetry
   the config's "one price everywhere it happens" comment promises).
4. **Given** a rest scene whose partner walks out of adjacency,
   **When** the scene is next serviced, **Then** it continues as solo
   rest (posture only, no relief) under the unchanged duration rules —
   mirroring how co-sleep drops a wandered-off companion.
5. **Given** a snapshot taken before this change carrying a bound
   rest duet (both partners in `Resting` naming each other), **When**
   it is loaded and resumed, **Then** both scenes continue lawfully as
   synchronized resters paying the mutual tier — no error state, no
   reshaping.

---

### User Story 2 - Riders go partial (Priority: P2)

The owner reprices the cuddle economy so that co-sleep and the
groomer's warmth *contribute to* the cuddle need without *finishing*
it. Rest — the dedicated cuddle activity — remains the one saturating
specialist. Standing (partial) cuddle demand is what makes rest worth
choosing at all; without this repricing the sibling shape yields zero
scenes because the need is already gone.

**Why this priority**: The demand half of the mechanism. Sibling shape
(P1) without this delivers no visible change; this without P1 leaves
the refusal tax in place. They ship together; P1 carries the
engine risk.

**Independent Test**: Config-only dial move on top of the split (User
Story 3). Verify per-scene deliveries against the need arithmetic:
each rider's `rate × min_ticks` lands below the measured mean need,
and the tier order (drip < mutual) holds.

**Acceptance Scenarios**:

1. **Given** the repriced dials, **When** a minimum-length scene of
   each rider runs (co-sleep drip, co-sleep mutual, groom-rider),
   **Then** per-scene delivery is partial against the measured mean
   cuddle need (~5.1): none of the riders can finish the need in one
   minimum scene from a single slot.
2. **Given** the repriced dials, **When** a cat with any cuddle need
   chooses between co-sleep and solo sleep beside an available
   friend, **Then** co-sleep retains a strictly positive edge (a
   smaller edge than today is accepted and wanted, as diversity).
3. **Given** a *reciprocal* mutual co-sleep pair (both naming each
   other), **When** both slots service in one tick, **Then** each cat
   receives the tier rate twice — per-scene partiality is not a
   per-pair saturation guarantee. This is the engine's existing
   payment shape, the need-flow model prices it in, and instruments
   must count scenes, not relief events.

---

### User Story 3 - The dial split, behavior-preserving (Priority: P3)

An operator can move the rest duet's price and the groomer's-warmth
price independently. The shared dial is split into two named dials
that land at the classic value first — provably changing nothing —
before any value moves. Historical configs that still carry the old
key keep loading with current tools.

**Why this priority**: Pure prerequisite. It carries no user-visible
value of its own — its value is that the split is separately
verifiable (byte-identical) so the later dial moves are pure config
diffs.

**Independent Test**: Land the split alone and run the instrument
continuity check: identical seed + config + tick count produces
byte-identical world state before and after the split. Load a
historical config carrying the old key with a current-tools build and
observe it accepted (and inert).

**Acceptance Scenarios**:

1. **Given** the split landed with both new dials at the classic
   value, **When** the continuity check runs (same seed, config,
   ticks), **Then** world state is byte-identical to the pre-split
   build.
2. **Given** any of the 181 committed configs carrying the deprecated
   key, **When** a current-tools build loads it, **Then** the config
   is accepted, the key is inert, and the strict
   unknown-field rejection still applies to genuinely unknown keys.
3. **Given** the split, **When** either new dial is moved alone,
   **Then** only its own site's payment changes (the two call sites
   are provably independent).

---

### Edge Cases

- **Reciprocal double payment**: both parties naming each other means
  each slot pays both — relief-*event* counts double while delivered
  relief clamps at the need. Intended (co-sleep's existing shape);
  the acceptance instruments count scenes, not relief events.
- **Partner wanders mid-scene**: the per-tick partner re-check drops
  the scene to solo rest (posture-only); the scene's duration clock
  is not reset. Mirrors co-sleep's companion re-check.
- **Partner state flaps** (settles, wakes, settles): the tier is
  resolved fresh every serviced tick; no hysteresis, no memory —
  exactly co-sleep's rule.
- **Pre-change snapshots**: a bound rest duet loads as two
  synchronized resters (User Story 1, scenario 5). The retired
  conscription legality is never consulted for continuations.
- **Mask semantics shift, not layout**: the rest-with-friend menu
  entry becomes legal when the partner is busy. Verified: the
  legality mask does **not** feed observations (it gates action
  selection only), so incumbent policies see an unchanged observation
  distribution; what changes is a newly-legal menu entry they were
  never trained to value. Pre-declared expectation: **zero** live
  rest scenes from the incumbent all-policy roster until a retrain;
  the deploy soak therefore watches welfare/watchdog signals, not
  rest counts.
- **Scripted seats respond immediately**: no retrain needed; the
  first live rest scenes are expected from scripted seats and are the
  cheap early read on the demand mechanism.
- **Stale lab bindings**: any new config field can be rejected by a
  stale binding's strict unknown-field rule; a rebuild is never
  compiler-only and must be gated by the binding-continuity check.
- **Dyadic lock-in**: two both-restful partnered activities go past
  the known-positive for the F-027 attractor class. Prices cannot
  prevent attractors; the named tail benchmark (`family-11-r5`) must
  run before any roster decision.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A rest-with-friend proposal MUST be legal whenever the
  named friend is adjacent — regardless of the friend's activity
  state. Rest MUST NOT conscript: the partner is never bound into the
  scene, keeps its own activity and clock, and no partner-side
  serviced stamp exists. (This is `Sleep{with}`'s exact legality and
  binding shape; it deletes rest's share of the partnered-refusal
  tax structurally.)
- **FR-002**: The rest scene MUST resolve one of two tiers per
  serviced tick from the partner's live state: **mutual** when the
  partner is itself resting or sleeping, **drip** otherwise. Both
  parties receive the resolved tier's relief. Tier resolution MUST
  use the *same shared predicate* as co-sleep's mutual check — one
  function, used by co-sleep pricing, warmth conduction, and rest
  tier resolution, so the three can never disagree about whether a
  pile is mutual.
- **FR-003**: Rest legality MUST flow through the engine's single
  validation funnel (Article IV; the same probe-the-rule surface the
  RL masks derive from — one rule, no parallel definition). The menu
  layout, kitty-slot observation layout, and message head MUST NOT
  change; the rest-with-friend mask bit changes meaning only.
- **FR-004**: The shared cuddle-relief dial MUST be split into two
  dials — one for the rest duet's mutual tier, one for the groomer's
  warmth — landing at the classic value (behavior-preserving), with
  the byte-identical continuity check passed, **before** any value
  moves. A new drip-tier dial for rest is introduced alongside.
  (Spec 028's own launch pattern for the cosleep pair.)
- **FR-005**: The deprecated key MUST remain accepted-but-inert: a
  config carrying `cuddle_relief` loads with current tools and the
  key has no effect. Strict rejection of genuinely unknown fields is
  unchanged. (Preserves the F-029 census re-cut workflow over the
  181 committed historical configs.)
- **FR-006**: The reprice MUST land as its own step (a pure config
  diff on top of the split), with these model-derived starting
  values, owner-pinnable as usual: co-sleep drip 0.25, co-sleep
  mutual 0.6, groom-warmth 0.5, rest drip 0.25, rest mutual 8.0
  (unchanged — the specialist keeps saturating). Tier order
  (drip < mutual) within each activity is a documented convention
  carried by the dial comments — no load-time validation (the cosleep
  pair's existing covenant; owner-ratified, see Clarifications).
- **FR-007**: Solo rest MUST stay posture-only (no relief), and all
  activity durations MUST stay unchanged (cuddle min 6 / max 12).
  No play dial moves; the play ladder comment is untouched.
- **FR-008**: The stale config comments MUST be corrected in the same
  change: the "mean cuddle need of 11.6" claim (measured 5.1 mean /
  2.8 median) and both cosleep tier comments that describe saturating
  deliveries — rewritten to the riders-partial principle.
- **FR-009**: Snapshots recorded before this change MUST load and
  resume lawfully: a bound rest duet resumes as synchronized resters;
  no proposal path errors (Article IV's safe resolutions only).
- **FR-010**: Determinism MUST be preserved (Article V): same seed +
  config + tick count → same world state, before and after each of
  the two steps; the split step is additionally byte-identical.

### Key Entities

- **Rest scene (new shape)**: an activity a single cat owns, naming
  an adjacent friend; unbound partner; tier resolved per serviced
  tick (mutual/drip) off the partner's live state; both parties paid.
- **The dial family after the split**: rest mutual (specialist,
  saturating), rest drip (new), groom warmth, co-sleep mutual,
  co-sleep drip — five independent prices, one per site/tier; the
  legacy shared key accepted-but-inert.
- **The shared mutual predicate**: the single "partner is itself
  sleeping or resting" rule used by co-sleep pricing, warmth
  conduction, and rest tier resolution.

## Success Criteria *(mandatory)*

### Measurable Outcomes

All live/soak measurements use F-029-corrected instruments and F-031
span rules (`/events/activity`, inclusive +1), counting **scenes, not
relief events**. Experiments runs the pre/post censuses and the
re-baseline; Product owns the spec, implementation, and PR.

- **SC-001**: The split step is byte-identical: same seed + config +
  ticks reproduces the pre-split world state exactly (instrument
  continuity, house ×3 practice).
- **SC-002**: Every one of the 181 committed configs carrying the
  deprecated key loads with current tools after the change.
- **SC-003**: On a served or soak world after the reprice, rest
  scenes are **greater than zero and sustained** — any stable
  double-digit count per 10k cat-ticks passes "non-zero and real"
  (the model's greedy ceiling is ~12 per 1k).
- **SC-004**: Both rest tiers are **observed** before any tier claim
  is banked — the mutual/drip distinction shown able to emit
  (F-029's rule).
- **SC-005**: Co-sleep remains dominant over solo sleep (model ~6:1),
  and the play mix stays within ~2 per 1k of its baseline, with the
  hunting cat's critter rate watched against its 280/1k baseline; the
  groom self/other mix is retained.
- **SC-006**: Pre-retrain incumbent behavior matches the pre-declared
  expectation of zero rest scenes, and the deploy soak completes on
  welfare/watchdog signals with no new alarms attributable to the
  change.
- **SC-007**: Certification anchors are re-derived (re-baseline)
  before any bar is applied to a policy trained under the new
  economy — standing cuddle demand costs about 1 happiness point in
  the model, so pre-change bars are invalid by construction.

## Assumptions

- **Deprecated-key decision — settled** (owner-ratified, see
  Clarifications): `cuddle_relief` stays accepted-but-inert,
  preserving re-cutting historical censuses with current tools.
- **Delivery shape — settled** (owner-ratified, see Clarifications):
  one PR, two verified steps — the split commits first with its
  byte-identical check, the reprice and sibling shape follow.
  Stale-comment fixes ride the same PR.
- **Per-scene, not per-pair**: the "delivers" arithmetic in the
  handoff table is per-scene. A reciprocal mutual pair can clear the
  need within a minimum scene (2 × mutual × min); the model prices
  this in, so the predicted mixes stand. No preemptive retune: if the
  owner later wants reciprocal pairs under saturation too, mutual
  would need ≤ 0.42 — the acceptance census decides whether reality
  asks for it.
- **Sequencing with the tabled waterline rule**: rest's legality
  change and the tabled waterline pairing rule touch the same
  validation funnel. The waterline decision is slotted at the fog
  timeline's step 2½ (`experiments/fog-gen1-timeline-2026-08-26.md`);
  this feature makes its pass over the funnel now and MUST NOT
  implement or foreclose the waterline rule — the spec's only
  obligation is that the funnel remains a single rule with no
  parallel definitions, so the later change is one more predicate,
  not a second pass.
- **Behavior change rides a retrain** for policy seats; scripted
  seats respond immediately and provide the early read. Seating and
  deploy are the owner's word, as always.
- **Gates inherited from house practice**: the binding-continuity
  check gates any lab rebuild (stale bindings reject new fields);
  the `family-11-r5` tail benchmark runs before any roster decision
  (F-027 attractor class); re-baseline lands before any
  certification freeze.
- **Known test-surface reddening** (rule 6 — sort before running):
  the config sweep that bumps the shared dial, the nan-validation
  table, the rest-duet/groomer tests asserting the classic value by
  name, and the two config sweeps any root-toml change reddens. Guards
  of the old conscription shape MUST go red; kept behavior (co-sleep,
  grooming, play, durations) MUST stay green.
