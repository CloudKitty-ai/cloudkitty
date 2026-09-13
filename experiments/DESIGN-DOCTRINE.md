# Design doctrine — DRAFT (walkthrough in progress, 2026-09-12)

The rules for shaping worlds, rewards, and behaviors — assembled here
for the first time from where they lived (config comments, spec text,
code comments, findings, GEN2-INPUTS). Process rules live in
`README.md §Design discipline`; empirical findings in `FINDINGS.md`;
this file holds the design principles between them.

Status: the ten rules below are captured as-is; walkthrough with the
owner in progress (rules 1-6 BANKED 2026-09-12, rule 7 2026-09-13;
rules 8-10 pending).
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
INPUT FOR THE CONSISTENCY PASS (from the 2026-09-12 clean-room A/B
test of rules 1-5): rule 9 must say a frozen policy's behavior does
shift under a reprice through the states the reprice changes; what it
cannot do is answer what the price now rewards. (The test's other
finding, reach, is now rule 3's third check.)
Rule 5 must point at rule 6: rule 5's test licenses a read of a heard
free word's kind (it is in the shared view), rule 6 forbids it, and
rule 5's repair menu and strip remedy do not apply to that field.
Rule 3's re-open trigger is a level read; rule 7 demands a contrast:
the pass should say why both stand. Groom-other now sits in three
rules (1, 2, 7): one owner, two pointers.

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
   it, never speak it. (Spec 033 FR-002b; bootstrap doctrine
   2026-08-18, restated 2026-09-02.) BANKED — full form below.
7. **Build a behavior when the world that values it exists** —
   earlier, the leash carries it and the rate falls to a floor the
   dose sets. (2026-09-11, GEN2-INPUTS; evidence: groom-other 13 →
   0.9-8.4/1k.) BANKED — full form below.
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

Welfare is the goal itself; anything else in the reward is a proxy,
and a proxy is what the gradient optimizes instead of the goal. So the
reward, the return the policy climbs, is the Nash mean of roster
happiness (the geometric mean, so one miserable cat drags the whole
team) and nothing else. Every cat is paid the same team number, so a
friend's relief counts for the actor as much as its own. Behavior
preferences route through pricing (rule 2) or world design.

- **Boundary test**: would the term distinguish two futures with
  identical welfare trajectories? Yes -> reward term, banned. No ->
  not a reward term; test it as pricing under rule 2.
- **Carve-outs (compatible, not exceptions)**: declared team-level
  potential shaping (`gamma*Phi(s') - Phi(s)`, Phi a function of team
  state only, exact form checked at declaration), compatible because
  it sums to nothing over an episode and cannot change what is
  optimal; estimator-side decompositions (critic heads, baselines:
  anything that leaves the return itself unchanged).
- **Outside the rule**: the imitation leash and the entropy bonus are
  training devices, not reward. They shape how the policy learns,
  never what it is for.
- **Known cost**: low-welfare-impact behaviors starve (groom-other ->
  spec 054); pay them with pricing, knowingly.
- **Diagnostic**: flat returns near the welfare ceiling are ambiguous
  between success and signal exhaustion. Read downtime (share of
  cat-ticks with all needs < T) against a same-generation baseline
  (rule 9): downtime still rising is success, downtime flat is
  exhaustion.
- **Amendment path**: the welfare DEFINITION can be amended by ruling
  at a generation boundary; never as a behavior-payment backdoor.

### 2. Prices are physics, not nudges
*(Generalizes F-018; spec 054 exemplar. Banked 2026-09-12.)*

A price is a rule about the world, not about the choice: it describes
what happens when an action lands (whose need moves, by how much),
never a payment for choosing it. Physics generalizes across cats,
policies, and generations and is bounded by what the world supplies; a
nudge is bounded only by how fast the action repeats, which is what
makes farms.

- **Boundary test**: does the number come from a consequence in the
  world (something moved, or a real state held), or from the
  designer's wish for the behavior? Wish -> nudge, banned. Wording is
  not the test; a nudge can always be phrased as a state. Ask instead
  what bounds the pay: what the world supplies (physics) or how fast
  the act repeats (nudge).
- **Hidden states are legal**: a price may key to a state the actor
  cannot observe (054: grooming a friend pays by the dirt removed
  even when the actor cannot see the dirt). This is the lever for
  behavior we did not script, not a defect.
- **Trait scaling is physics of the cat** (>=0.5x floor): keyed to
  who, never to which policy or to a schedule.
- **Two clocks**: scripted teachers answer a reprice immediately
  (F-016); policies answer
  only after retraining, so a frozen-roster census after a reprice
  measures the roster, not the price (rule 9). Declare the teacher
  side before recording any teacher turns (rule 5) that follow the
  change; where the price keys to a state the teacher cannot see, the
  declared answer is none.
- **When the behavior has no consequence in the world**, give it one
  (world design, rule 8) rather than paying for the behavior. Hidden
  is not absent: a state the actor cannot see still counts.
- **Known cost**: a wanted behavior with no consequence cannot be
  bought at all; giving it one is world work and a retrain (rules 7,
  9).
- **Exception**: the prosocial edge, rule 4, paid as the groom floor.

### 3. Side relief never makes a specialist unnecessary
*(Spec 041. Banked 2026-09-12.)*

Every need gets a specialist, the activity that finishes it. Some
activities relieve a second need on the side (co-sleep warms; the
groomer is warmed). Side relief contributes to that need but never
suffices for it: a need whose riders suffice loses its activity from
the repertoire.

- **Side relief (a rider)** = relief to a need other than the
  activity's own. Grooming a friend delivers bath relief as the
  specialist, not as a rider; only its cuddle floor is side relief.
- **Three checks, all required**: insufficiency (one scene, one
  continuous run of the activity, cannot finish the need from
  measured demand); rate order (per-tick side relief below the
  specialist's; 054's ceiling against the cuddle specialist is the
  exemplar); and reach (the specialist needs nothing its riders do
  not). A precondition only the specialist carries, a free partner
  or consent, makes the riders the default route and the specialist
  the exception. Drop it, as 041 did when rest stopped binding its
  partner, or count it as rate order failing.
  Before 041 every check failed at once: all three riders finished
  the need inside one scene, two matched the specialist's rate, and
  the specialist alone needed a free, consenting partner. It ran zero
  scenes.
- **Accepted holes**: per scene, not per pair (a reciprocal pair earns
  twice); riders from successive activities add up. Re-open if a
  census on a retrained roster (rule 9) shows the specialist's scenes
  falling or absent.
- **Re-verify**: demand is measured, never assumed; re-check every
  rider at any roster or need-rate change, or reprice or legality
  change of either activity.

### 4. Unfarmable first, prosocial second, charm last
*(Spec 054; the project's benevolence goal. Banked 2026-09-12.)*

Three things, in order; each bounds the next.

1. **Unfarmable.** Some side relief (rule 3) is paid per tick for
   being in an activity beside a friend, whatever the activity
   delivers: the groom floor, the rest and co-sleep drips. Beyond
   rule 3's checks, such pay is never the best route to the need it
   relieves: an activity with the same preconditions (the same friend
   beside you) must already pay as much per tick to that need (rule
   3's reach check, pointed at the rider). One activity per tick, so
   repetition earns nothing the world did not already allow. No such
   activity, no such pay.
2. **Prosocial gets the edge, not the field.** Where a behavior has a
   self form and an other form (groom self, groom a friend), the other
   form pays more by the value delivered to the friend, and when
   neither is in need it still pays a small edge over the self form,
   never over the need's other routes (item 1). The self form stays a
   full specialist for the actor's own need, so self-sufficiency is
   always viable.
   Cases: friend in need -> the other form wins by value delivered
   (physics, rule 2); neither in need -> the edge alone; actor in need
   -> the self form must still finish it alone.
3. **Charm at marginal cost.** All else equal, a behavior we find
   charming may be paid, only within item 1's bound. It buys the tie,
   not presence; value delivered is what carries a behavior.

- **Standing under rule 2**: the rest and co-sleep drips are physics
  (a friend beside you warms). The groom floor, which pays item 2's
  edge, pays when nothing was delivered: a nudge, a declared
  exception, admitted because item 1 makes it harmless. It dissolves
  the day the edge is derived from a state priced the same wherever
  it holds.
- **Re-verify** every fixed side pay and edge at any reprice of the
  activity that bounds it.
- **Values enter through the world**: benevolence is what the world
  makes real, and rule 1 already counts the friend's relief. The edge
  is the only thumb on the scale, and it lives at ties.

### 5. A teacher may only act on what the student can see
*(The imitability principle; spec 028 FR-019, spec 049 FR-021.
Banked 2026-09-12.)*

Scripted cats are teachers: their recorded turns are what a policy is
first trained to copy and what the leash (the training pull back
toward those turns) holds it near. So a scripted rule may act only on
what the policy it will teach can observe, and its decision to speak
never costs it the turn. A teacher that acts on something the student
cannot see teaches the action without its cause; the student copies
it at the right rate and the wrong moments, and training erodes it or
finds an unrelated cue that happens to correlate.

- **Boundary test**: is every input to the scripted rule a function
  of the observation alone? Derived quantities are fine (the nearest
  visible friend); a read of anything outside it is not. Private
  state counts as outside: a counter or a route the teacher keeps for
  itself is invisible unless the observation carries it too (the
  memory cells). Chance is not a cause; a teacher may roll dice. If
  the test fails, either stop reading the hidden thing or add it to
  the observation, as the raw fact (the friend's position) rather
  than a judgment built from it (worth chasing). Add it when the
  student needs the same fact to do the behavior at all; otherwise
  drop the read.
- **Speaking rides along**: a scripted cat decides what to say
  separately from what to do, from the same view, and never idles to
  speak, so the student does not learn that speaking means stopping.
- **Enforced by construction**: scripted rules, the observation
  encoder, and the legal-action masks are handed the same fog-filtered
  view (049 FR-021). Where it still leaks, nothing may read the leak,
  and the view is fixed at the next schema boundary.
- **Carve-out**: whatever sees everything during training but never
  acts and never enters the corpus (the critic) teaches nothing.
- **Known cost**: whatever a teacher reads becomes part of the
  observation, so a new read is a schema change and a retrain
  boundary (rule 9). Teachers are deliberately less informed than the
  engine, and a price keyed to a state they cannot see gets no
  teacher answer at all (rule 2, two clocks).
- **Diagnostic**: the student's rate of a behavior matches the
  teacher's while its timing against the cause does not. That is this
  failure, not a training shortfall.
- **Holes on record, fix at the Gen 2 wall**: the view exposes some
  facts about friends that no rule reads today (strip them as memory
  was); the exploration rule follows a stop on a private route the
  observation does not carry (add the direction to it as observation
  cells with the Gen 2 schema).
- **Re-verify**: every scripted rule whenever the observation changes.
  "Can see" is per generation: when Gen 2 hides needs, a rule that
  reads a visible friend's needs becomes illegal. A corpus recorded
  under a read found illegal is re-recorded at the next generation.

### 6. The free register is never scripted
*(Spec 033 FR-002b; bootstrap doctrine 2026-08-18, restated by the
2026-09-02 Here*-teacher ruling. Banked 2026-09-12.)*

Law-named words (Want*, Here*, Purr, WaitForMe) mean what their
legality rule enforces, so a script may speak them and teaches nothing
false. Sound-named words (mew, chirp, the reserves trill and ekekek)
mean whatever the cats make them mean. A script that speaks one
authors the meaning: every corpus row where it says chirp under some
condition teaches the clone chirp means that condition, and the leash
(rule 5) holds it there.

- **Scripted** = a rule a person wrote (engine behaviors, a teacher
  seat filled by one, a plugin). A trained policy in a teacher seat is
  a mind; its free words are lineage, the register's only source of
  demonstrations (F-022).
- **Speaking test**: no scripted rule emits a sound-named kind or
  filters by one (gating a mind's free words, or dropping its corpus
  rows, by the word). Kind-blind law such as the cooldown is not a
  filter.
- **Hearing test**: no scripted decision depends on a heard word's
  kind or tier. What the law attaches to every call (who, where, when,
  whether a reply) is fair to use. The kind sits in the shared view, so
  rule 5's test passes and its repairs do not apply: the fault is who
  authors the meaning, not what the student can see.
- **Carve-out**: a lab emitter may speak a free word to probe hearers
  when nothing learns from it (no corpus, no training rollout, no
  served world).
- **Known cost**: a scripted corpus teaches silence in the register,
  and the leash covers the message head. Call a silent word unused
  only after comparing a scripted-corpus clone's free-register rate
  against a lineage clone's.
- **Re-verify** at every behavior change: no free kind named in
  behavior code outside tests; hearing kind-blind (a heard mew places
  the friend at its stamped tile, nothing more). Both hold today.
- **Amendment path**: to give a free word a meaning, move it to the
  law-named tier (rename for the meaning, enforce by predicate).
  Drift sign: a free word given a meaning by anything but the cats'
  use.

### 7. Build a behavior when the world that values it exists
*(GEN2-INPUTS 2026-09-11; shakeout RESULTS: here-words under fog vs
nofog, the groom-other decay curve; spec 054 is the rescue. Banked
2026-09-13.)*

To build a behavior is to put it into training: a scripted rule in
the corpus, or for the free register the lineage rows (rule 6). It
survives training only when a consequence in the world carries it to
team return. Otherwise only the leash holds it up: the rate falls to
a floor the leash dose sets, and the floor costs welfare (F-019).

- **"Values it" has three parts**: a consequence in the world (rule
  2); a path from it to team return inside the training horizon
  (about 500 ticks at gamma 0.998); a cue in the observation if the
  behavior is to be conditional (without one the world anchors only a
  base rate). Repairs, all before the seed: world work; a new
  observation cell (a schema boundary, rule 9); a longer horizon at
  gamma, never physics compressed to fit (rule 2: a delay set by the
  wish is a nudge).
- **Order**: world, then the seed at that generation's corpus
  collection, then train. The seed is still required (F-022: no
  channel came alive by exploration); the entropy bonus (rule 1) only
  keeps unspoken words on the table.
- **Diagnostic**: vary the leash dose. A world-anchored rate ignores
  it; a leash-held rate orders by it. A low rate measures the world
  or the corpus (rule 6's comparison), never the cats' ability; a
  reprice answers it only once the diagnostic says world.
- **Carve-outs**: personality held by the leash on purpose, declared
  in advance (F-019; rule 1's outside-the-rule clause), is a welfare
  cost paid knowingly. Scripted seats never decay (F-036); their
  corpus rows shedding in the policies is not a defect. Charm pay
  (rule 4) is not a build.
- **Known cost**: the served roster waits a generation.
- **Re-verify**: a contrast, never a level. After the retrain (rule
  9), the rate at the loosest leash under the valuing world against
  the same recipe under the world without the value, or the prior
  world (fog vs nofog; 054 repriced vs flat). A gap inside noise is
  no pass (rule 10). A failed contrast means the world does not value
  it yet: pull the seed or do more world work, never re-declare it
  personality.
