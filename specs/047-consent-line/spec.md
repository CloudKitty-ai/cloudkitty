# Feature Specification: Partner Consent Line for Playful Targeting

**Feature Branch**: `047-consent-line`

**Created**: 2026-09-01

**Status**: Draft

**Input**: User description: "Owner-approved amendment to the spec-042 playful
character family (brief relayed by Experiments 2026-09-01; owner's rule pinned
in `experiments/biscuit3-comfort-sweep-2026-09-01/prereg.md` §Addendum 2): add
a `consent_line` dial. Owner's rule, verbatim: play can always be proposed if
the friend's top need is play; it cannot be proposed if a non-play need is the
friend's top need and that need is over the line. Default off with byte
identity. Friends only; hard eligibility drop, not a ranking cost."

## Why (context, not requirements)

The engine's refusal mechanism only protects a kitty who is already mid-scene:
a free friend has no way to decline a play invitation. Experiments' offline
pricing of the Biscuit 3.0 c30 raws found 21% of Biscuit's duets (565/2,693)
conscript a friend whose top non-play need is over 30 (median 36.6, p90 51) —
and in 84% of those an eligible idle friend stood within a median 2 tiles.
Since the invited side cannot refuse, consent has to live in the chooser's
selection. Rejection is not the target; consent is.

## Clarifications

### Session 2026-09-01

- Q: The brief's gate site (the partner ranking's eligibility filter) covers
  only one of three playful friend-play start paths — do get-serious relief
  and adjacent opportunism get gated too? → A: **Yes — all three paths**
  (Experiments confirmed 2026-09-01 after Product's leak analysis; the
  owner's rule is unconditional and the prereg pins it that way; a one-site
  gate would make bar C2 a test of the leak, not the rule). Playful-scoped:
  needs-driven kitties are untouched even with the dial set. Sizing from the
  c30 raws: get-serious carries ~6% of duets (167/2,693; 22 of the 565
  would-be-blocked); the adjacency-heavy opportunism path is the material
  leak (partner adjacent at the last poll in 68% of blocked duets).
- Q: May the three sites read the friend's needs differently? → A: No — all
  three read the same decision-time world snapshot the selector already
  consults, so Experiments' consent-share readout (R7) has exactly one
  definition to pin.
- Q: Blocking the only playmate re-prices play as solo (distance 0, the
  absent-friend rule), which near the play/eat crossover can buy solo play
  a tick over a moderately higher need — is that intended? → A: **Accepted
  by the owner 2026-09-01** (medium-review finding 1): the scripted cat is
  a training teacher and marginal scoring detours wash out in training;
  what matters is that consideration of other cats' needs is modeled so it
  is learnable. Bounded (solo play relieves play; safeguard urgency wins
  past 75); pinned as intended in the flip test; Experiments' R2
  (hungry-play share, both arms, report-only) watches the aggregate.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A burdened friend is left in peace (Priority: P1)

Watching the meadow, Elizabeth sees a playful kitty pick play partners. With
the consent line set, a friend who urgently needs something else — food, sleep,
a bath — is no longer dragged into a duet; the playful kitty picks a willing
partner, a critter, an element, or plays solo instead. A friend whose top need
IS play is always fair game, however high that need runs.

**Why this priority**: This is the feature — the owner's consent rule. Without
it the dial does nothing.

**Independent Test**: Configure a playful kitty next to friends with
hand-set needs and a consent line of 30; observe which targets survive
play-target eligibility.

**Acceptance Scenarios**:

1. **Given** a consent line of 30 and an adjacent friend with play need 10 and
   eat need 40, **When** the playful kitty ranks play targets, **Then** that
   friend is not eligible (top non-play need is over the line and tops play).
2. **Given** the same friend with eat need 25 instead, **When** targets are
   ranked, **Then** the friend remains eligible (top non-play need is under
   the line).
3. **Given** the same friend with play need 45 and eat need 40, **When**
   targets are ranked, **Then** the friend remains eligible (play is the top
   need — play is always proposable).
4. **Given** a critter adjacent to a friend who is blocked by the line,
   **When** targets are ranked, **Then** the critter is unaffected and can be
   chosen.

---

### User Story 2 - Nothing changes until the dial is turned (Priority: P2)

Every existing world, config, and certified character behaves exactly as
before: the dial's default is off, and off means byte-for-byte identical
evolution.

**Why this priority**: House delivery contract for character-family dials
(the spec-042 pattern): additive knob, identity at default, provable by the
existing witnesses.

**Independent Test**: Run the existing golden-evolution and character-stamp
witnesses against a build carrying the dial at its default.

**Acceptance Scenarios**:

1. **Given** the dial absent from config (default 0.0), **When** the golden
   evolution and character stamp are recomputed, **Then** both digests are
   unmoved.
2. **Given** an existing config file that does not mention the dial, **When**
   the server loads it, **Then** the config is accepted and behaves as today.

---

### User Story 3 - A bad dial value is refused loudly (Priority: P3)

A negative consent line is meaningless (needs are non-negative). Config
validation rejects it at load with a clear error instead of silently doing
something surprising.

**Why this priority**: Guard rail; cheap, and the house pattern for every
dial.

**Independent Test**: Load a config with a negative value and observe the
rejection.

**Acceptance Scenarios**:

1. **Given** a config with a negative consent line, **When** the server
   validates it, **Then** load fails with an error naming the dial.

---

### Edge Cases

- Top non-play need exactly AT the line: the friend stays eligible — the
  owner's rule says "over" the line (strictly greater blocks).
- Friend's play need exactly equal to its top non-play need: the friend stays
  eligible — blocking requires the non-play need to strictly top play.
- Every adjacent friend blocked: the playful kitty still has critters,
  elements, and solo play; selection degrades exactly as if those friends were
  absent, never to a stuck state.
- Dial set but no friends in range: no behavior change of any kind.
- A blocked friend standing adjacent: the opportunism pass skips them (a
  critter in reach is still batted at; with nothing else in reach the rung
  yields nothing and the ladder moves on) — adjacency is not a bypass.
- A playful kitty above its comfort line whose winning need is play: the
  get-serious pick honors the gate exactly as the ranking does.
- The gate composes with the existing eligibility thresholds (self-urge and
  partner-value floors) and with partner scoring on or off: it is an
  independent AND-condition, not a replacement for or modifier of any of them.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The playful character family MUST gain a `consent_line` dial
  with default 0.0 meaning OFF; at the default, world evolution MUST be
  byte-identical to a build without the dial (proven by the existing
  golden-evolution and character-stamp witnesses, unmoved).
- **FR-002**: When `consent_line` > 0, a FRIEND MUST be dropped as a play
  target if and only if the friend's top non-play need (highest of eat,
  drink, sleep, cuddle, bath) is strictly greater than `consent_line` AND
  strictly greater than the friend's play need — on EVERY play-proposal path
  of the playful behavior: the partner ranking, get-serious play relief, and
  adjacent opportunism (Clarifications 2026-09-01).
- **FR-003**: A friend whose top need is play (including a tie with the top
  non-play need) MUST always remain proposable, regardless of how high any
  need runs.
- **FR-004**: The gate MUST apply to friend targets only; critter targets,
  element play, and solo play MUST be unaffected, including when they stand
  adjacent to a blocked friend.
- **FR-005**: The gate MUST be a hard drop evaluated alongside each path's
  existing conditions — never a ranking cost — and MUST act independently of
  partner scoring being on or off and of every other dial's value. It MUST
  NOT alter any non-playful behavior's selection even when the dial is set
  (the spec-042 doctrine: the family's dials never move anyone else).
- **FR-006**: Config validation MUST reject a negative `consent_line` at load
  with an error naming the dial.
- **FR-007**: The dial MUST be documented where the playful family's dials are
  documented (the served config's commented row and any dial table the family
  keeps).
- **FR-008**: Each behavioral guard MUST be shown red first against the exact
  bug it catches, per house rules 5/6, with the cycles recorded in the
  feature's redden list: identity at default, the three US1 eligibility
  cases, critter-unaffected, needs-driven-untouched, validation rejection,
  and ONE guard PER GATED PATH (ranking, get-serious, opportunism), each red
  when its own site's check is removed (Experiments' ask, 2026-09-01).
- **FR-009**: All three gated sites MUST read the friend's needs from the
  same decision-time world snapshot the selector already consults — one
  consent definition across paths (Experiments' ask, 2026-09-01).

### Key Entities

- **Consent line**: a per-character threshold in the playful family; a need
  level above which an unwilling friend's burden vetoes a play invitation.
- **Friend's top non-play need**: the highest of the candidate friend's
  eat/drink/sleep/cuddle/bath needs at proposal time, read from the same
  world state the selector already consults.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With the dial at default, the golden-evolution digest and the
  character stamp are byte-for-byte unmoved (100% identity).
- **SC-002**: In a controlled scene with the line at 30: a friend at play 10 /
  eat 40 is chosen as a play target in 0% of proposals; the same friend at
  eat 25, or at play 45 / eat 40, remains choosable.
- **SC-003**: A critter adjacent to a blocked friend is chosen at the same
  rate as with the dial off.
- **SC-004**: A negative dial value is rejected at 100% of load attempts with
  an error that names the dial.

### Downstream (not gated by this feature)

Experiments' pinned acceptance run (prereg Addendum 2, bars C1–C5: identity,
consent share < 0.05, play kept, roster supply, welfare) prices the dial at
c30 on the trained policy. Those bars belong to Experiments' run on the new
binary; this feature's gate is the engine behavior above.

## Assumptions

- Strict inequalities on both comparisons, from the owner's wording "over 30"
  and the relayed formulation; ties leave the friend eligible.
- The friend's needs are readable at proposal time (already true — the
  existing partner-value pass reads them); no new snapshot or timing is
  introduced.
- The dial rides the spec-042 playful family serialization (additive field,
  serde-default pattern); worlds saved before this feature load unchanged.
- This spec directory (047) is the amendment vehicle for the spec-042 family
  change, per one-spec-per-arc house practice; spec 042's own artifacts are
  not modified.
- Experiments' acceptance run and any retraining are out of scope; Product
  delivers the engine gate, the guards, and the docs.
