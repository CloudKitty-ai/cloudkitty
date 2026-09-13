# Design doctrine — DRAFT (walkthrough in progress, 2026-09-12)

The rules for shaping worlds, rewards, and behaviors — assembled here
for the first time from where they lived (config comments, spec text,
code comments, findings, GEN2-INPUTS). Process rules live in
`README.md §Design discipline`; empirical findings in `FINDINGS.md`;
this file holds the design principles between them.

Status: the ten rules below are captured as-is; walkthrough with the
owner in progress (rules 1-5 BANKED 2026-09-12; rules 6-10 pending).
PROCESS (owner-set): each rule is explored in session against five
questions — purpose, benefit, downsides, exceptions, refinements —
and what lands here is the TERSE decision-bearing residue only (the
rule, its boundary tests, carve-outs, known costs, amendment paths),
not the five-part structure. Rule 1 below is the format exemplar.
ADMISSION: a banked rule carries the rule, its boundary tests,
carve-outs, known costs, and enough rationale to tell when the rule
has drifted from its objective. Declined ideas, design sketches, and
measured values live elsewhere (ROADMAP, specs, RESULTS, FINDINGS);
spec and finding ids stay as pointers.

## The rules

1. **Reward is team welfare only; pricing is never a reward term.**
   (F-018 layer 2 / ROADMAP guard 3.) BANKED — full form below.
2. **Prices are physics, not nudges** — price states of the world,
   never behaviors you want to see. (2026-09-11, generalizing F-018.)
   BANKED — full form below.
3. **Side relief never makes a specialist unnecessary** — a rider
   that finishes the need kills the dedicated activity. (Spec 041.)
   BANKED — full form below.
4. **Unfarmable first, prosocial second, charm last.** (Spec 054.)
   BANKED — full form below.
5. **A teacher may only act on what the student can see** — the
   imitability principle. (Specs 028, 049.) BANKED — full form below.
6. **The free register is never scripted** — scripted cats may hear
   it, never speak it. (Owner ruling 2026-09-02.)
7. **Build a behavior when the world that values it exists** —
   earlier means leash-held and decaying. (2026-09-11, GEN2-INPUTS;
   evidence: groom-other 13 → 0.9/1k.)
8. **Design scarcity of information, not incentives for behavior.**
   Companion levers: staged leash, matched horizons, world variation;
   counterweight: demonstrations buy what is cheap to demonstrate.
   (GEN2-INPUTS; evidence: here-words under fog vs nofog.)
9. **Frozen models cannot answer a reprice** — behavior changes land
   with retraining generations, never on frozen rosters. (Memory;
   the #368 shelvings; spec 054's merge-hold.)
10. **Two-layer welfare gates; a noise reading is never a pass bar.**
    (Certification gate philosophy.)

## Banked rules

### 1. Reward is team welfare only; pricing is never a reward term
*(F-018 layer 2 / ROADMAP guard 3. Banked 2026-09-12.)*

The Nash mean of roster happiness is the only thing the gradient may
want; behavior preferences route through pricing or world design.

- **Boundary test**: would the term distinguish two futures with
  identical welfare trajectories? Yes -> reward term, banned. No ->
  pricing, allowed.
- **Carve-outs (compatible, not exceptions)**: declared team-level
  potential shaping (`gamma*Phi(s') - Phi(s)`, state-only Phi, exact
  form checked at declaration); estimator-side decompositions (change
  the estimator, not the objective).
- **Known cost**: low-welfare-impact behaviors starve (groom-other ->
  spec 054); pay them with pricing, knowingly.
- **Diagnostic**: flat returns near the welfare ceiling are ambiguous
  between success and signal exhaustion. Read downtime (share of
  cat-ticks with all needs < T) against a baseline.
- **Amendment path**: the welfare DEFINITION can be amended by ruling
  at a generation boundary; never as a behavior-payment backdoor.

### 2. Prices are physics, not nudges
*(Generalizes F-018; spec 054 exemplar. Banked 2026-09-12.)*

A price is a rule about the world, not about the cat: it describes
what happens when an action lands (whose need moves, by how much),
never a payment for the choice itself. Physics generalizes across
seats and generations and is bounded by what the world supplies; a
nudge is bounded only by how fast the action repeats, which is what
makes farms.

- **Boundary test**: does the number come from a consequence in the
  world (something moved, or a real state held), or from the
  designer's wish for the behavior? Wish -> nudge, banned. Wording is
  not the test; a nudge can always be phrased as a state.
- **Hidden states are legal**: a price may key to a state the actor
  cannot observe (054's ramp under hidden needs). This is the
  emergence lever, not a defect.
- **Trait scaling is physics of the cat** (>=0.5x floor): keyed to
  who, never to which policy or to a schedule.
- **Two clocks**: scripted teachers answer a reprice immediately
  (F-016); policies answer
  only after retraining, so a frozen-roster census after a reprice
  measures the roster, not the price (rule 9). Declare the teacher
  side before any corpus collection that follows the change.
- **When the behavior has no consequence in the world**, give it one
  (world design, rule 8) rather than paying for the behavior. Hidden
  is not absent: a state the actor cannot see still counts.
- **Exception**: the prosocial edge, rule 4.

### 3. Side relief never makes a specialist unnecessary
*(Spec 041; the 054 ratio. Banked 2026-09-12.)*

Every need has a specialist, the activity that finishes it. Some
specialists relieve a second need on the side (co-sleep warms; the
groomer is warmed). Side relief contributes to that need but never
suffices for it.

- **Two checks, both required**: insufficiency (one scene cannot
  finish the need from typical demand) and rate order (per-tick side
  relief below the specialist's). Rate order alone is not enough: it
  held before 041 while rest ran zero scenes.
- **Side relief** = relief to a need other than the activity's own.
  Grooming a friend is the bath specialist acting on the target.
- **Accepted holes**: per scene, not per pair (a reciprocal pair earns
  twice); riders stack. Re-open if a census shows the specialist's
  scenes falling.
- **Re-verify**: insufficiency is checked against measured demand;
  re-check every rider at any roster or need-rate change.

### 4. Unfarmable first, prosocial second, charm last
*(Spec 054; the project's benevolence goal. Banked 2026-09-12.)*

Three things, in order; each bounds the next.

1. **Unfarmable.** Any flat payment sits at or below the lowest-paying
   existing route to the same need, under preconditions no harder than
   the behavior's. Activities are exclusive, so such a payment never
   raises a need's per-tick income above what the world already
   allowed; repetition earns nothing new. No existing route, no flat
   payment.
2. **Prosocial gets the edge, not the field.** Where a behavior has a
   self form and an other form (groom self, groom a friend), the other
   form pays more by the value delivered to the friend, and at a tie
   it still pays a small edge. The self form stays a full specialist
   for the actor's own need, so self-sufficiency is always viable.
   Cases: friend in need -> the other form wins by value delivered
   (physics, rule 2); neither in need -> the edge alone; actor in need
   -> the self form must still finish it alone.
3. **Charm at marginal cost.** All else equal, a behavior we find
   charming may be paid, only within item 1's bound. It buys the tie,
   not presence; value delivered is what carries a behavior.

- **Standing under rule 2**: the edge is a nudge, a declared exception,
  admitted because item 1 makes it harmless. It dissolves the day the
  edge is derived from a state priced the same wherever it holds.
- **Re-verify** every edge at any reprice of the route that bounds it.
- **Values enter through the world**: benevolence is what the world
  makes real, and rule 1 already counts the friend's relief. The edge
  is the only thumb on the scale, and it lives at ties.

### 5. A teacher may only act on what the student can see
*(The imitability principle; spec 028 FR-019, spec 049 FR-021.
Banked 2026-09-12.)*

Scripted cats are teachers: their recorded turns are what a policy is
first trained to copy and what the leash pulls it back toward. So a
scripted rule may act only on what the policy it will teach can
observe, and its decision to speak never costs it the turn. A teacher
that acts on something the student cannot see teaches the action
without its cause; the student copies it at the right rate and the
wrong moments, and training erodes it or finds an unrelated cue that
happens to correlate.

- **Boundary test**: could the scripted rule be rewritten to read
  only the observation, directly or in one step? If not, either stop
  reading the hidden thing or add it to the observation, as the raw
  fact rather than a judgment built from it.
- **Speaking rides along**: a scripted cat decides what to say
  separately from what to do and never idles to speak, so the student
  does not learn that speaking means stopping.
- **Enforced by construction**: scripted rules, the observation
  encoder, and the legal-action masks are handed the same fog-filtered
  view (049 FR-021). Where it still leaks, fix the view.
- **Carve-out**: the critic sees everything during training; it never
  acts and teaches nothing.
- **Known cost**: whatever a teacher reads becomes part of the
  observation, so a new read is a schema change and a retrain
  boundary (rule 9). Teachers are deliberately less informed than
  the engine.
- **Holes on record, fix at the Gen 2 wall**: some friend-record
  fields leak through the view (nothing reads them today; strip them
  as memory was); the exploration rule follows a tour position the
  observation does not carry (add the direction as cells with the Gen
  2 schema).
- **Re-verify**: every scripted rule whenever the observation changes.
  "Can see" is per generation: when Gen 2 hides needs, a rule that
  reads a visible friend's needs becomes illegal.
