# Feature Specification: Playful 2.0 — partner-value play selection

**Feature Branch**: `042-playful-partner-value`

**Created**: 2026-08-29

**Status**: Draft

**Input**: The owner-routed Biscuit 3.0 teacher-side lever
(`experiments/biscuit3-design-note-2026-08-26.md` @ e489d4b, Levers
§1–2 — the per-need comfort weights were rolled into this spec by the
owner 2026-08-29, and the partner-value score supersedes the earlier
bare floor filter, owner 2026-08-28). The scripted Playful behavior
today picks its play target purely by distance and gets serious on an
unweighted highest-pressure check; both throw away information the
teacher needs before Biscuit 3.0's demonstrations are generated.
Evidence is banked and needs no re-deriving: the design note, F-033
(the partnered-refusal tax and hungry-play share),
`experiments/need-latency-baseline-2026-08-26.md`, and
`experiments/pre041-census-2026-08-28.md`.

## Clarifications

### Session 2026-08-29

- Q: When the best-scoring friend fails the partner-value threshold
  but a lower-scoring friend would pass it, may the cat play with the
  lower-scoring friend? → A: **Eligibility filter** — the thresholds
  define who is worth bothering: friends below `t_partner` (or all
  friends, when own need < `t_self`) are dropped from the ranking,
  and the pick is the best of eligible friends plus critters. A
  passing lower-value friend can win; a nearby low-value friend never
  vetoes partner play by out-scoring on distance alone.
- Q: A distant friend's high play need may be satisfied by the time
  the cat arrives (needs run low, other cats are closer) — how is
  stale value accounted for? → A: Three ways, no new dial: linear
  staleness folds into the existing `w_value`-to-distance ratio (the
  sweep prices it implicitly); selection re-evaluates every decision
  tick, so a mid-journey value collapse redirects the cat within one
  tick (now an explicit requirement, FR-010); and arrival at a
  satisfied-but-free friend degrades to a legal low-value game, never
  a refusal. **Competition** (discounting a candidate because other
  eager playmates are nearer to it) is explicitly out of scope —
  noted as a candidate for a future theory-of-mind arc.
- Q: Does a friend's seriousness cost read its highest pressure
  across all needs, or all needs except play? → A: **Highest
  non-play pressure** — wanting to play is the opposite of being
  about to get serious, so play pressure never counts against a
  candidate; `w_value` and `w_serious` stay independent axes for the
  sweep.
- Q: Is the critter appeal constant scaled by the value weight like
  friends are, or standalone? → A: **Standalone** — a critter's score
  is its appeal minus distance, untouched by `w_value`; each dial
  moves exactly one thing in the sweep.

### Session 2026-08-30 (medium-review reconciliation)

- The busy-friend admission rule is now a requirement, not a plan
  aside (review #8): a mid-scene friend enters the ranking **only
  while `w_value` is above zero** — at the identity default the value
  term is dead, there is no anticipatory signal to act on, and the
  classic hard busy-filter stands (the byte-identity witness).
  `w_value` therefore carries two documented effects: it scales
  friend valuation, and it switches busy-friend admission.
- The score and gate are scoped to the **playful behavior's own play
  path** (review #1): the shared classic nearest-pick that other
  behaviors and the serious path consume ignores every dial, so the
  sweep can never silently move a non-playful cat.
- `t_partner` at its identity 0.0 is **no bar at all** (review #2):
  once `w_busy`/`w_serious` are live a friend's value can go
  negative, and an un-raised threshold must not convert those ranking
  costs into a veto. The bar applies only when raised above zero.
- Comfort weights are **strictly positive** (review #5): a zero
  weight would disable the get-serious trigger for that need outright
  — beyond what any lawful comfort line (itself > 0) could do.
  Down-weighting defers a need; disabling is not on the dial.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A playful cat picks partners by worth, not just distance (Priority: P1)

A playful cat weighing where to play considers what a game is worth to
each candidate friend — how much that friend actually wants to play,
how long it would have to be waited for if mid-scene, and whether it
is about to get serious about a pressing need — and balances that
against distance. High-value distant friends can beat low-value near
ones. Two thresholds gate *who* the cat bothers: it approaches a
friend only when its own play urge is real and the friend's value
clears a bar; otherwise it plays with a critter or by itself, exactly
as it always could. The thresholds gate who the cat bothers, never
whether the cat plays — that is the character, and it is the owner's
explicit intent.

**Why this priority**: This is the teacher-side lever. Biscuit 3.0 is
cloned from demonstrations of this behavior; a teacher that offers
play to whoever is nearest — including cats who don't want it — is
where the residual refusal tax and the low-value-play pattern come
from. Fixing the teacher is the mechanism both Biscuit 3.0 vectors
ride.

**Independent Test**: Unit-level, staged worlds: with the score
weights raised, a distant high-play-need friend outranks an adjacent
zero-need one; with thresholds raised, a zero-need adjacent friend is
left in peace and the cat takes its critter/solo game instead.

**Acceptance Scenarios**:

1. **Given** two idle candidate friends — one adjacent with no play
   need, one farther with high play need — and score weights active,
   **When** the playful cat selects a play target, **Then** the
   high-need friend is selected despite the distance.
2. **Given** the best candidate friend's value below the partner
   threshold (or the cat's own play need below the self threshold),
   **When** the cat would otherwise propose partner play, **Then** it
   takes its unconditional critter or solo game instead — it never
   simply stands idle because partner play is gated.
3. **Given** a mid-scene friend whose scene is nearly over and a free
   but low-value friend farther away, **When** the wait-cost weight
   is moderate, **Then** the cat may approach the soon-free friend —
   and **no play proposal is made until that friend is actually
   free** (the existing hard rule for proposals is untouched; gating
   by approach never creates a new way to be refused).
4. **Given** all score dials at their launch defaults, **When** the
   cat selects a play target, **Then** the choice — including the
   critter-beats-friend distance tie — is identical to today's
   nearest-target pick, tick for tick.

---

### User Story 2 - Getting serious is weighed per need (Priority: P2)

The playful cat's "some things cannot wait" check — the comfort line
that pulls it out of play when a need presses — weighs each need
before comparing to the comfort threshold. A world's configuration
can make the cat food-attentive (weight hunger up) without also
making it interrupt games for a routine bath peak (weight bath down
or leave it at parity). At the default weights the check is exactly
today's: the single comfort line against the plain highest pressure.

**Why this priority**: The measured shape of Biscuit's welfare gap is
lopsided — eat excursions peak 35–52 with a 78-tick armed latency on
record, while every seat's bath routinely peaks 30–40. A single
global comfort value low enough to buy food-attentiveness also taxes
play for slow, low-stakes needs; per-need weights let the sweep
target the food band precisely and preserve more of the character.

**Independent Test**: Unit-level: a config weighting eat above 1.0
gets serious on an eat pressure that the unweighted check ignores; a
config weighting bath below 1.0 stays playful on a bath pressure that
the unweighted check would have tripped on. At all-1.0 weights,
behavior is identical to today.

**Acceptance Scenarios**:

1. **Given** an eat weight above 1.0 and an eat pressure below the
   comfort line but above line-divided-by-weight, **When** the
   playful cat takes its turn, **Then** it gets serious — where the
   unweighted check would have kept playing.
2. **Given** a bath weight below 1.0 and a bath pressure above the
   comfort line but below line-divided-by-weight, **When** the
   playful cat takes its turn, **Then** it keeps playing — where the
   unweighted check would have gotten serious.
3. **Given** all weights at 1.0, **When** any pressure profile is
   evaluated, **Then** the serious/playful decision matches today's
   unweighted check exactly.
4. **Given** the weighted check trips, **When** the cat gets
   serious, **Then** what it then does is decided exactly as today —
   the weights move only the trigger, never the serious cat's choice
   of relief.

---

### User Story 3 - The dial surface launches inert and sweep-ready (Priority: P3)

An operator (and Experiments' joint lab campaign) can set every new
dial independently: the score weights, the two gate thresholds, the
critter appeal constant, and the six per-need comfort weights. At
launch every dial sits at its identity value, and the world's
evolution is provably unchanged — byte-identical — so the change
ships ahead of the sweep that will price the dials, with zero
behavioral risk.

**Why this priority**: Pure prerequisite, same discipline as every
recent dial launch: the inert launch is separately verifiable, and
the pricing belongs to Experiments' comfort × score × weights
campaign (one lab campaign answers both levers), which the owner
sequences after all pre-fog economy changes.

**Independent Test**: Land the change alone and run the instrument
continuity check: identical seed + config + tick count produces
byte-identical world state at the launch defaults. Set each dial
alone in a scratch config and observe only its own effect.

**Acceptance Scenarios**:

1. **Given** the launch defaults (score dials at zero, weights at
   1.0), **When** the continuity check runs, **Then** world state is
   byte-identical to the pre-change build.
2. **Given** any single dial moved in a config, **When** the config
   loads, **Then** it validates (finite, in-range values) and only
   that dial's documented effect(s) change — `w_value` documents two
   (valuation scale and busy-friend admission, FR-012); every other
   dial documents one.
3. **Given** a malformed value (negative where nonsensical, or a
   non-finite number) on any new dial, **When** the config loads,
   **Then** it is rejected with an error naming the field.

---

### Edge Cases

- **Adjacent-but-busy best target**: when the gated pick is a friend
  that cannot be proposed to *this tick* (mid-scene), the cat must
  never stall idle beside it — the unconditional critter/solo game is
  the fallback for the tick, exactly the suppression the current
  hard busy-filter exists to prevent. Approach toward a
  busy-but-soon-free friend is allowed; waiting is spent playing, not
  idling.
- **Proposal safety is inherited, not new**: proposals to busy
  friends were illegal before and remain unproposed — the score
  changes which lawful proposal is made, never adds an unlawful one.
  No new refusal exposure; the residual timing-seam refusal tax
  stays (the owner kept it).
- **Wait estimate past the minimum**: a partner whose scene has
  already run past its minimum could end any tick — its expected
  wait is zero, never negative.
- **Score ties**: equal scores fall back to the existing
  deterministic tie order (distance, critter-before-friend, id) — the
  same total order as today, behind the score instead of in front of
  it.
- **No numeric poison**: every new dial is validated finite at load;
  the score computation introduces no NaN source, preserving the
  total order determinism requires (Article V).
- **Chase bookkeeping still applies**: chase-exclusion (targets given
  up on) and chase-patience interact with the scored pick exactly as
  they do with the distance pick — an excluded or hopeless target is
  not re-picked just because it scores well.
- **Weighted trigger, unweighted life**: the comfort weights touch
  only the get-serious *trigger*. The serious cat's choice of what to
  do, every other behavior's checks, and the engine's distress/
  safeguard machinery (Article I) read the same unweighted needs as
  ever.
- **Scope of the dials**: all new dials are world-level behavior
  configuration, like the comfort line today — they tune every seat
  running the playful behavior in that world. Per-kitty weighting is
  out of scope.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The playful behavior's play-target selection — and ONLY
  the playful behavior's; the shared nearest-pick other behaviors
  consume MUST ignore every dial (2026-08-30 reconciliation) — MUST
  rank every candidate friend by a partner-value score combining, per
  candidate: the candidate's own play need; a wait cost for a
  mid-scene candidate (how long until its scene could end, zero for a
  free candidate, never negative); a seriousness cost for a candidate
  under pressure (its highest pressure among the non-play needs —
  play pressure never counts against a candidate, clarified
  2026-08-29); and distance. Each
  component MUST carry its own configurable weight (value weight,
  wait weight, seriousness weight).
- **FR-002**: Critters MUST enter the same ranking, scored as a
  single configurable flat appeal constant minus distance —
  standalone, not scaled by the value weight (clarified 2026-08-29),
  so each dial moves exactly one thing. At launch defaults the
  ranking MUST reproduce today's pick exactly, including the
  critter-beats-friend distance tie.
- **FR-003**: Partner play MUST be gated by two thresholds acting as
  an **eligibility filter** (clarified 2026-08-29): a friend is
  eligible only when the cat's own play need meets the self threshold
  AND — when the partner threshold is raised above its identity zero
  (2026-08-30: zero is no bar, never a veto on negative values) —
  that friend's value meets it; ineligible
  friends are dropped from the ranking, and the pick is the
  best-scoring of eligible friends and critters. Critter and solo
  play MUST remain unconditional — the thresholds gate who the cat
  bothers, never whether it plays, and a tick with no eligible friend
  MUST fall through to the critter/solo game, never to idle.
- **FR-004**: Play *proposals* MUST remain restricted to free
  partners exactly as today (the established conscription rule) — the
  score may steer *approach* toward a busy-but-soon-free friend, but
  no proposal is made until the friend is free. The change MUST NOT
  create any new refusal exposure.
- **FR-005**: The get-serious check MUST compare per-need weighted
  pressures against the comfort line: for each need, its pressure
  times its configurable weight; the cat gets serious when any
  weighted pressure meets the line. Weights default to 1.0 per need,
  reproducing today's unweighted check exactly. The weights MUST
  affect only this trigger — target selection after getting serious,
  and every reading of needs outside this check, stay unweighted.
- **FR-006**: Every new dial MUST launch at its identity value (score
  and gate dials at 0.0, comfort weights at 1.0, critter appeal at
  0.0) and the launch MUST be behavior-preserving: byte-identical
  world evolution at defaults, verified by the instrument continuity
  check before merge.
- **FR-007**: Determinism MUST be preserved (Article V): the scored
  selection is a total order — equal scores resolve by the existing
  deterministic tie-break (distance, critter-before-friend, id) — and
  no code path introduces a non-finite score. All new dials MUST be
  validated at load (finite; negative values rejected where they have
  no meaning), with errors naming the field.
- **FR-008**: Chase-exclusion and chase-patience rules MUST apply to
  the scored pick unchanged: an excluded target is not ranked, and a
  stalled pursuit is abandoned on the same terms as today.
- **FR-009**: The change MUST be confined to behavior configuration
  and the scripted behavior layer: no action-schema, menu,
  observation-layout, mask-semantics, or engine-law change. Proposals
  continue to flow through the engine's single validation funnel
  (Article IV) with unchanged rules.
- **FR-010**: Per-tick re-selection (clarified 2026-08-29): the
  scored selection MUST be re-evaluated from the current world state
  on every decision tick — no target lock-in — so a candidate whose
  value collapses mid-journey (serviced by another cat, need drained)
  is re-ranked or abandoned within one tick. This is the structural
  answer to stale value; wasted investment is bounded by travel ticks
  already spent, never by a committed plan.
- **FR-011**: Test discipline (house rules 5/6): every existing
  selection and playful-behavior test MUST stay green at the launch
  defaults, and every new dial MUST land with a red-first guard
  demonstrating its effect (for the weights: a weighted crossing
  where the unweighted check would not trip, and the reverse; for the
  gates: a zero-need adjacent friend left in peace in favor of
  critter/solo play).

- **FR-012** (2026-08-30 reconciliation, review #8): A mid-scene
  friend MUST enter the candidate ranking only while `w_value` is
  above zero (anticipatory approach exists only when the value signal
  it serves does); at the identity default the classic hard
  busy-filter MUST stand unchanged. Chase bookkeeping (FR-008)
  applies to both picks.

### Key Entities

- **Partner-value score**: per-candidate quantity — weighted play
  need minus weighted wait cost minus weighted seriousness cost (top
  non-play pressure),
  traded against distance; critters at standalone flat appeal minus
  distance. Deterministic
  total order with the existing tie-break behind it.
- **The gate**: two thresholds (self play-need, partner value) that
  decide whether the best friend is worth bothering; never gates
  critter/solo play.
- **Comfort weights**: six per-need multipliers (default 1.0) applied
  to pressures only inside the playful get-serious check.
- **The dial family**: value/wait/seriousness weights, self/partner
  thresholds, critter appeal, six comfort weights — all world-level
  behavior configuration, all inert at launch, all priced later by
  Experiments' joint sweep.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At launch defaults the change is byte-identical: same
  seed + config + ticks reproduces the pre-change world state exactly
  (instrument continuity, house ×3 practice).
- **SC-002**: With score weights active in a staged scenario, a
  high-play-need distant friend is selected over a zero-need adjacent
  friend — deterministically, every run.
- **SC-003**: Zero new refusal exposure at any dial setting: no play
  proposal toward a mid-scene partner is ever emitted (the count of
  such proposals is zero across the test battery and any staged
  sweep world).
- **SC-004**: At any dial setting, a playful cat with a reachable
  critter or the solo option still plays on the tick partner play is
  gated away — gated ticks resolve to play, not idle, in every staged
  gate scenario.
- **SC-005**: A config weighting eat above bath gets serious on a
  staged eat peak the unweighted check ignores AND stays playful on a
  staged bath peak the unweighted check trips on — both directions
  demonstrated.
- **SC-006**: Every new dial is independently settable and
  validated: each loads alone in a config, malformed values are
  rejected naming the field, and Experiments' joint campaign can
  address each dial without touching any other.

## Assumptions

- **Pricing is not this spec's job**: all dials launch inert; the
  comfort × score × weights values come from Experiments' joint lab
  campaign (owner-sequenced after all pre-fog economy changes land;
  041 is in), and the owner pins served values as always. Open owner
  calls named in the design note (the comfort value itself, the
  identity question, same-generation shipping of the score) stay
  open — nothing here forecloses them.
- **World-level scope**: like the comfort line today, the new dials
  tune the playful behavior per world, not per kitty.
- **Character preservation is structural**: critter/solo play stays
  unconditional by construction, so no dial setting can make a
  playful cat play less in kind — only redirect who it bothers.
  Expected effect at real weights is redistribution of partner play
  toward high-need partners; the F-027 frozen-cluster tail benchmark
  (`family-11-r5`) runs before any roster decision, and matters more
  here, not less.
- **Teachability is the point, not a requirement here**: every score
  input is observable by the clone today except scene age, which
  arrives with the step-3 bundle — and Biscuit 3.0 trains post-wall,
  so the wait term is learnable exactly when it matters. This spec
  only fixes the teacher.
- **Sequencing**: rides outside spec 041 and outside the step-3
  wall (behavior + config only, no schema). Must land (inert) before
  Experiments' joint sweep begins.
- **Contested targets are a theory-of-mind candidate, not this spec**
  (owner, 2026-08-29): discounting a candidate because other eager
  playmates sit nearer to it requires modeling other cats' likely
  choices — banked as a candidate use case for a future
  theory-of-mind arc. The sweep's wasted-travel measurements will
  show whether reality asks for it.
