# Feature Specification: Parameterized Teacher Rework

**Feature Branch**: `product/teacher-rework`

**Created**: 2026-10-10

**Status**: Draft

**Input**: The owner's kickoff in the Product session, 2026-10-10 — the
second of the four Gen 2 build-phase specs (prereg skeleton §10), after
the schema wall (spec 058, merged with the critter-slot cut and review
fixes).

**Ruling sources** (records beat this spec on any discrepancy):
`experiments/gen2-sitting-rulings-2026-10-08.md` S§2 (teacher rework,
bath-visible control), S§4 (grooming pair, no suppression), S§6
(consent_line extension IN; corpus placement bar),
`experiments/gen2-kickoff-rulings-2026-10-07.md` K§3 rider 2
(adjacency-legal demonstrations), the 2026-09-13 shelf ruling (one
teacher, identity dials), spec 057 (sleep rule reads the floor),
prereg skeleton §4. Design discussion settled with Experiments
2026-10-10 on the owner's relay word (slack gates entry; cue-answer
shape pins; presets, not rename) — their answers quoted in the
Assumptions.

## Why now

Gen 2's corpus must be collected by a teacher whose decisions a student
can imitate from what it can see (doctrine rule 5), under the identity
dials the schema bump already encodes. Spec 058 shipped the dials into
the observation; nothing reads them yet — the review's top finding.
This spec closes that gap: the teacher runs on the SAME dials the cat's
own observation shows, and every teacher read of another cat's hidden
state comes out or re-keys to visible signals. It lands before corpus
collection (skeleton §10 step 1), and the mandatory Gen 2 re-record
absorbs every behavioral change in one `[rng-sequence]` boundary.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One teacher, dialed per cat (Priority: P1)

The two scripted brains (`playful`, `needs_driven`) become ONE
parameterized teacher whose behavior is set by the cat's identity
dials — need-rate multipliers, comfort slack, consent line, favourite
weights — read through the same accessors the observation encoder uses.
The old names survive as PRESETS: aliases that resolve to the one
teacher with frozen dial defaults, so 349 committed configs, the CI
config sweep, the cert harness's `--brain` strings, and the Biscuit 3.0
c30 certification anchor all stay byte-valid.

**Why this priority**: the corpus is collected by this teacher; every
Gen 2 claim sits on it. The dial/observation identity ("the cat sees
the dials its teacher ran on") is the design's honesty condition.

**Independent Test**: configure two cats with different dials; the one
teacher produces behaviors that differ exactly as the dials say, and a
cat whose preset is `playful` behaves identically to today's playful
on the same seeds.

**Acceptance Scenarios**:

1. **Given** a cat with preset `playful` and no dial overrides,
   **When** it runs on the deterministic suite the presets pin,
   **Then** its decisions match the frozen preset reference — the c30
   anchor's certification reference still holds.
2. **Given** two cats identical except one has a higher comfort slack,
   **When** both satisfy a need, **Then** the higher-slack cat returns
   to luxury behavior later, by the slack difference, and the gate
   reads the same number the cat's slack CELL encodes.
3. **Given** a cat with a favourite weight on Play, **When** it
   chooses among partnered activities of equal relief value, **Then**
   the favourite tips the choice as its weight says.
4. **Given** any cat, **When** its consent line is set per-kitty,
   **Then** partnered proposals against it are blocked at ITS line,
   not the world line (the two call-site flips to the `_consenting`
   variants, folded into this spec by recorded call).

---

### User Story 2 - The imitability audit: hidden reads come out (Priority: P1)

Every scripted decision that reads another cat's HIDDEN state (the five
non-bath needs, happiness) is removed or re-keyed to signals the
deciding cat can see (position, activity, bath, the audible digest).
Bath reads stay — bath is the ruled visible need. Effect-body pays at
apply time are world pricing and exempt (doctrine rule 2).

**Why this priority**: a teacher acting on what the student cannot see
poisons the corpus (doctrine rule 5); Gen 2's hidden-needs claims
require the teacher clean.

**Independent Test**: the field-read audit over the behavior rules
finds zero decision reads of a friend's hidden needs or happiness; the
known work list (the groomee's remaining-need read in
finish-what-you-started; the partner-Play, top-non-play, and
consent-blocks reads in selection) is each resolved and its resolution
recorded.

**Acceptance Scenarios**:

1. **Given** the audited teacher, **When** the friend-record read sweep
   runs (the spec-058 T024 sweep), **Then** decision reads of friends
   touch only: id, position, activity/activity-clock, bath, and
   digest-derived signals.
2. **Given** a friend whose hidden hunger is extreme, **When** the
   teacher decides for an observer, **Then** the decision is identical
   to the same state with the friend's hunger ordinary (the row-
   visibility property, now at the behavior layer).
3. **Given** the bath-read sites (the announce-threshold decline and
   the exposure-vs-value comparison), **When** the audit lists them,
   **Then** they are RETAINED and documented as visible-need reads.

---

### User Story 3 - Cue-answer rungs (Priority: P2)

Two demonstration rungs are added so the corpus carries answers to
audible need-calls: `cuddle_response` and `play_response`. A friend's
digest-visible want-call raises the hearer's VALUATION of the matching
partnered activity for a bounded window; consent and adjacency gates
are checked unchanged after it. The response is intensity-keyed
(louder calls are likelier answered) and fires only while the cue is
digest-visible, with the window long enough that an answer can
physically complete at walk speed.

**Why this priority**: the rungs exist so the leash can carry
answer-behavior into Gen 2 minds (doctrine rule 7); they are additive
demonstrations, not required for the teacher to function.

**Independent Test**: with a cue in the digest, the teacher's
valuation of the matching activity is raised within the window and
reverts after it; a consent-blocked or non-adjacent answer stays
blocked; the scripted teacher never emits or decides by free-register
kinds.

**Acceptance Scenarios**:

1. **Given** a digest-visible want_cuddle from an adjacent friend,
   **When** the hearer's teacher evaluates partnered rest, **Then**
   the valuation carries the response term, and the resulting proposal
   still passes the unchanged consent and adjacency gates.
2. **Given** the same call no longer digest-visible, **When** the
   teacher evaluates, **Then** no response term applies (a teacher
   answering what the student cannot see is the exact rule-5 violation
   this spec removes elsewhere).
3. **Given** two calls differing only in intensity, **When** the
   response threshold is applied, **Then** the louder call clears it
   at states where the quieter does not.
4. **Given** FR-036's cuddle-clause revisit changes consent semantics
   later, **When** the response fires, **Then** it inherits the change
   with no amendment (valuation-only placement).

---

### Edge Cases

- A preset plus explicit per-kitty dial overrides: overrides win; the
  preset only supplies defaults.
- Slack zero (the world default): entry gating is inert — behavior
  matches today's needs_driven on that axis.
- The slack gate and the get-serious pressure line disagree: pressure
  governs exit, slack governs entry; they never compose into one
  trigger (the settled design).
- Two simultaneous digest-visible cues of different kinds: each
  response term applies to its own activity's valuation; selection
  proceeds normally.
- A cue from a cat that then left the audible window mid-approach: the
  response term expires with digest visibility; the engine's normal
  counterpart-gone handling covers an in-flight scene.
- Biscuit's groom response: gained by construction from the one
  teacher (no suppression — S§4); her Gen 1 character survives as
  favourite weighting, not as a missing behavior.
- The teacher reads the slack CELL's value (post-encode), so clamping
  (slack/40 capped at 1) is part of the semantics the teacher and
  student share.

## Requirements *(mandatory)*

### Functional Requirements

**One teacher (shelf 2026-09-13; S§2)**

- **FR-001**: One parameterized teacher MUST replace the playful and
  needs_driven brains. Its dials are the identity block's four groups,
  read through the SAME config accessors the observation encoder uses
  (`need_rate_for`, `comfort_slack_for`, `consent_line_for`,
  `favourite_weight_for`) — one home, so teacher behavior and the
  observed identity cells can never diverge.
- **FR-002**: `playful` and `needs_driven` MUST survive as preset
  aliases resolving to the one teacher with frozen dial defaults. The
  spec's contract carries the preset→dial table as the citable
  reference; a config naming either string loads and behaves
  byte-identically to today on the preset's reference suite (the
  Biscuit 3.0 c30 anchor stays a valid certification reference — S§2).
- **FR-003**: Comfort slack MUST gate ENTRY to luxury behavior only
  (return-to-play after needs are satisfied); exit stays on the
  existing pressure × comfort-weight line. The gate MUST read the
  value the slack CELL encodes (slack/40, clamped), not a separate
  internal quantity.
- **FR-004**: Favourite weights MUST tip selection among partnered
  activities as per-cat preference (the Biscuit trait's new home);
  all-zero favourite reproduces today's unweighted selection.
- **FR-005**: The consent_line gate MUST read the per-kitty line
  (`consent_line_for`) at the two needs_driven call sites by flipping
  them to the existing `_consenting` variants (S§6, folded in by
  recorded call). The step-7 consent-transfer read's numbers become
  reference-only (ruled).
- **FR-006**: The sleep rule MUST keep reading the floor (057,
  carried).

**The imitability audit (S§2; doctrine rule 5)**

- **FR-007**: No teacher DECISION may read another cat's hidden state:
  the five non-bath needs and happiness. The audit's work list (the
  known read sites in finish-what-you-started and selection's
  partner-value / top-non-play / consent-blocks) is resolved
  one-by-one — removed, or re-keyed to visible/audible signals — and
  the resolution of each site is recorded in the spec's contract.
- **FR-008**: The bath reads STAY (the announce-threshold decline and
  the exposure-vs-value comparison): bath is the ruled visible need.
  Effect-body pays at apply time stay: world pricing, exempt.
- **FR-009**: Demonstrations MUST be adjacency-legal only (K§3 rider
  2): the teacher never proposes a partnered activity at a
  non-adjacent partner.

**Cue-answer rungs (S§2; settled shape 2026-10-10)**

- **FR-010**: `cuddle_response` and `play_response` MUST key to
  digest-visible want-calls only, raise the matching activity's
  VALUATION only, and expire with digest visibility; consent and
  adjacency gates are checked unchanged after the response term.
- **FR-011**: The response threshold MUST key to the call's intensity
  cells (graded: louder is likelier answered), and the response
  window MUST be at least the typical approach time at walk speed so
  an answer can physically complete.
- **FR-012**: The scripted teacher MUST NOT emit or decide by any
  free-register kind (mew, chirp, trill, ekekek) — doctrine rule 6
  carried through the rework; the rungs key to want-kinds only.

**Boundaries**

- **FR-013**: OUT of this spec: dirt-keyed teacher behavior (the
  banked B arm), the scripted purr-listener rung (#391 stands), and
  the dial RANGES per trait draw (a prereg blank Experiments pins
  before collection — this spec exposes the dials, not their draws).
- **FR-014**: The rework rides the mandatory Gen 2 re-record: no
  claim about existing corpora survives it (`[rng-sequence]`
  consequence recorded), and the spec-058 T024 obligation (re-run the
  friend-field read sweep, re-verify the strip list) executes at this
  spec's close.

### Key Entities

- **The parameterized teacher**: one scripted brain, four dial groups,
  replacing two brains — the corpus's demonstrator.
- **Preset**: a named alias (`playful`, `needs_driven`) binding frozen
  dial defaults; the compatibility surface for 349 configs, the cert
  harness, and the c30 anchor.
- **Response term**: a bounded, intensity-keyed, digest-gated valuation
  modifier — the demonstrable form of answering a call.
- **The audit record**: the per-site resolution list for every hidden
  read — the contract's evidence that rule 5 holds.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On the preset reference suite, `playful` and
  `needs_driven` presets reproduce today's two brains decision-for-
  decision on the same seeds (byte-stable c30 anchor included).
- **SC-002**: The friend-field read sweep over the reworked behavior
  rules reports zero decision reads of hidden needs or happiness;
  bath and digest reads only (T024's re-verify doubles as this
  check's record).
- **SC-003**: A friend's hidden-state extremes cannot move the
  teacher's decision: paired decisions over randomized hidden states
  are identical (the behavior-layer twin of spec 058's row-visibility
  property).
- **SC-004**: Each dial moves behavior measurably and independently:
  slack delays return-to-luxury by its tick count; a favourite tips
  equal-value selection; a per-kitty consent line blocks at its own
  value; all-defaults reproduce the presets.
- **SC-005**: With a digest-visible cue, answer behavior appears in
  the teacher's demonstrations (nonzero answered-call rate on a
  seeded corpus sample) and NO response fires outside digest
  visibility or against consent/adjacency.
- **SC-006**: Every existing config loads unchanged: the CI config
  sweep (349 tomls) stays green with zero config edits.

## Doctrine check (CLAUDE.md rule 8)

Checked against `experiments/DESIGN-DOCTRINE.md`, 2026-10-10:

- **Rule 5 (imitability)** moved FR-001/FR-003/FR-007-FR-011: the
  whole spec is this rule applied — dials the student sees, reads the
  student could make, responses keyed to audible cues, windows bounded
  by digest visibility.
- **Rule 6 (free register never scripted)** moved FR-012: the rungs
  key to want-kinds; the teacher stays mute and deaf in the free
  register.
- **Rule 2 (prices are physics)** moved FR-008's exemption line:
  effect-body pays are world pricing and stay; the response term is a
  decision preference, not a payment, and changes no world rule.
- **Rule 7 (build behavior when the world values it)** moved FR-010:
  the rungs exist as demonstrations for the leash to carry; their
  rate in minds is the dose's business, not a reward's.
- **Rule 9 (frozen models cannot answer a reprice)** moved FR-014:
  every behavioral change lands inside the one mandatory re-record;
  no frozen-corpus claim survives.
- **Rules 1, 3, 4, 8, 10, 11, 12** were checked and moved nothing:
  no reward term, no relief rider, no observation change (058's wall
  stands), no gate semantics.

## Assumptions

- Spec numbering: this is spec 059; empty-bowl (spec-006 amendment)
  and the stuck detector follow separately and are OUT of scope.
- The three design choices were settled with Experiments on the
  owner's relay word (2026-10-10): slack gates entry, read off the
  slack cell ("state it as a read of the slack CELL (post-encode),
  not of internal teacher state"); cue-answer = valuation-only,
  window ≤ digest visibility and ≥ approach time, intensity-keyed
  ("the rung is 'more willing,' never 'consent-overridden'");
  presets not rename ("349 committed tomls … a rename reds the sweep
  repo-wide", `cert_harness_fog --brain` pins the strings, and "the
  Biscuit c30 anchor's certification reference depends on 'playful'
  resolving to today's exact dials").
- The preset dial defaults are DERIVED from today's two brains'
  effective behavior (playful: today's playful_comfort-equivalent
  slack and Play favourite; needs_driven: zero slack, no favourite),
  pinned at plan time against the deterministic reference suite —
  byte-equality on the suite is the acceptance bar, not a hand-waved
  "similar".
- "Typical approach time" for the response window is derived at plan
  time from the digest window and walk speed already in config —
  stated as a frozen relation, not a new tunable, unless planning
  shows a tunable is unavoidable.
- The exact re-keying for each audited read site (remove vs re-key to
  a visible signal) is plan-time work recorded in the contract; the
  spec constrains the OUTCOME (SC-002/SC-003), not each site's
  choice.
- Experiments' corpus-side reads (placement bar ≥ 0.40, density-pin
  re-checks, dial-range draws) happen at collection in their lane;
  this spec's deliverable ends at the merged engine + audit record.
