# Design doctrine — DRAFT (walkthrough in progress, 2026-09-12)

The rules for shaping worlds, rewards, and behaviors — assembled here
for the first time from where they lived (config comments, spec text,
code comments, findings, GEN2-INPUTS). Process rules live in
`README.md §Design discipline`; empirical findings in `FINDINGS.md`;
this file holds the design principles between them.

Status: the ten rules below are captured as-is; walkthrough with the
owner in progress (rules 1-6 BANKED 2026-09-12, rules 7-10 2026-09-13).
Cross-rule consistency pass applied 2026-09-13. NEXT: a full read of
all ten, then final analysis and compression.
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
6. **The free register is never scripted** — a scripted cat neither
   speaks it nor decides by it. (Spec 033 FR-002b; bootstrap doctrine
   2026-08-18, restated 2026-09-02.) BANKED — full form below.
7. **Build a behavior when the world that values it exists** —
   earlier, the leash carries it and the rate falls to a floor the
   dose sets. (2026-09-11, GEN2-INPUTS; evidence: the groom-other
   decay curve, shakeout RESULTS.) BANKED — full form below.
8. **Design scarcity of information, not incentives for behavior.**
   Headroom is variance or enrichment, never a harder served config;
   counterweight: demonstrations buy what is cheap to demonstrate.
   (GEN2-INPUTS; evidence: here-words under fog vs nofog.) BANKED —
   full form below.
9. **Frozen models cannot answer a reprice** — a behavior change is
   answered only by the generation retrained under it; a frozen
   roster shifts, it does not answer. (Owner ruling 2026-09-01; the
   #368 shelvings; spec 054 FR-013.) BANKED — full form below.
10. **Two-layer welfare gates; a noise reading is never a pass bar.**
    The floor is absolute; above it a seating declares a trade, never
    inherits a bar. (Certification gate philosophy 2026-08-14; owner
    reshaping 2026-09-13.) BANKED — full form below.

## Banked rules

### 1. Reward is team welfare only; pricing is never a reward term
*(F-018 layer 2 / ROADMAP guard 3. Banked 2026-09-12.)*

Welfare is the goal itself; anything else in the reward is a proxy,
and a proxy is what the gradient optimizes instead of the goal. So the
reward, the return the policy climbs, is the Nash mean of roster
happiness (the geometric mean, so one miserable cat drags the whole
team) and nothing else. Every cat is paid the same team number, so a
friend's relief counts for the actor as much as its own. Behavior
preferences route through pricing (rule 2) or information design
(rule 8).

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
- **Known cost**: low-welfare-impact behaviors starve (groom-other,
  spec 054); the rescue is rule 7's.
- **Diagnostic**: flat returns near the welfare ceiling are ambiguous
  between success and signal exhaustion. Read downtime (share of
  cat-ticks with all needs < T) against a same-generation baseline
  (rule 9): downtime still rising is success, downtime flat is
  exhaustion.
- **Amendment path**: the welfare DEFINITION can be amended by ruling
  at a generation boundary, under rule 8's enrichment conditions;
  never as a behavior-payment backdoor.

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
  patterns we did not script over acts the corpus carries (rule 7),
  not a defect.
- **Trait scaling is physics of the cat** (>=0.5x floor): keyed to
  who, never to which policy or to a schedule.
- **Two clocks**: a scripted rule answers a state change at once
  (F-016) and a payout change never (F-036); a policy answers either
  only after retraining, so a census before the retrain is rule 9's.
  Before recording teacher turns that follow a change, declare which
  clock the scripted side is on; a payout, or a state the teacher
  cannot see (rule 5), gets none.
- **No consequence, no price**: a wanted behavior with no consequence
  in the world cannot be bought at all. Give it a state to move,
  hidden if need be (the lever above), rather than paying for the
  choice; that is world work and a retrain (rules 7, 9).
- **Exceptions**: the prosocial edge, rule 4, paid as the groom
  floor; rule 9's interim dial, temporary.

### 3. Side relief never makes a specialist unnecessary
*(Spec 041. Banked 2026-09-12.)*

Every need gets a specialist, the activity that finishes it. Some
activities relieve a second need on the side (co-sleep warms; the
groomer is warmed). Side relief contributes to that need but never
suffices for it: a need whose riders suffice loses its activity from
the repertoire.

- **Side relief (a rider)** = relief to a need other than the
  activity's own. Grooming a friend delivers bath relief as the
  specialist, not as a rider; only its groom floor (cuddle relief) is
  side relief.
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
  absent or falling: a repertoire read, so a level suffices; whether
  the world values the activity is rule 7's contrast, a different
  question.
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
   3's reach and rate-order checks, pointed at the rider). One activity per tick, so
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
  is the only standing thumb on the scale (rule 9's interim dial is
  temporary), and it lives at ties.

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
  drop the read. One field passes this test and is still barred: a
  heard free word's kind (rule 6).
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
  engine; what a price they cannot see does to them is rule 2's two
  clocks.
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
  collection, then train. A seed is required where the world gives
  the word nothing to say (F-022, measured under global vision, where
  the channel was redundant: F-026). Where it does (rule 8), an
  unseeded free register is the contrast F-022 invites, not a
  violation: at a schema boundary, lineage rows seed where rule 5
  allows them, and elsewhere the register restarts from the entropy
  bonus (rule 1), which keeps unspoken words on the table, and the
  scarcity. Revisit trigger in GEN2-INPUTS.
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

### 8. Design scarcity of information, not incentives for behavior
*(GEN2-INPUTS; F-026, F-021, F-030; ROADMAP fog split and free-time
entry. Banked 2026-09-13.)*

A signal or a pursuit is worth doing only when the cat cannot
otherwise see the thing: under global vision the channel was
welfare-redundant (F-026); fog held the here-words nofog shed. This
rule owns who can see what.

- **Boundary test**: for a wanted behavior, ask what a cat would need
  to know, or not know, for it to be worth doing, and change that.
  "Not paid enough" is rule 2's question, not this rule's.
- **Scarcity pairs with a route to the fact** the actor can run from
  its view and memory: a speaker who has it (the Here* adjacency
  law), a search (fog with memory), or an inference (a friend's
  unseen favorites show in what it does: the free-time plan's
  helping, ROADMAP). Hiding a state takes the actor's cue away too.
- **Headroom at the ceiling** comes from variance or enrichment,
  never from replacing the served config with a harder one
  (exam-vs-gym skew: training.toml's 1.5x need rates). Variance =
  declared tail episodes; the served config stays the majority
  episode and the world rule 10's floor is measured in; changing it
  is a generation ruling (rule 9). Enrichment is a rule 1 amendment
  at a generation boundary: states of the cat enter happiness, never acts
  or words, through a stock that saturates so the act cannot be
  farmed; anything else is rule 1's backdoor. It lands with its own
  contrast, since it reshapes returns where they were flat.
- **Counterweight**: demonstrations buy what is cheap to demonstrate
  (F-022, F-017). Scarcity makes a seed survive; whether it can
  replace one is rule 7's open contrast.
- **Known costs**: scarcity is paid in welfare (the Gen 1 cap; rule
  10's catastrophe gates bound it, its floor moves with the world).
  Its settings are composition numbers (F-023), and a scarcity change
  is an observation change (rule 5).
- **Re-verify**: rule 7's contrast, with and without the scarcity;
  the composition numbers re-measured at every roster change.

### 9. Frozen models cannot answer a reprice
*(Owner ruling 2026-09-01; spec 041's early deploy, spec 054 FR-013's
hold, the #368 shelvings; one-retrain ruling 2026-08-27. Banked
2026-09-13.)*

A frozen roster is the seated policies, weights fixed. It carries
the old world's answer, so a behavior change (a reprice, a legality
or world change) is answered only by the generation retrained under
it. A generation is one retrain and reseat on one observation
schema, one teacher ruleset, and one served config apart from
deploys that pass the test below; the boundary is where they may
change together; a same-generation baseline is a lab arm trained
under the same three (the clone anchor).

- **A frozen roster shifts, never answers**: its behavior moves
  through the states the change moves; a newly legal action goes
  unchosen, a newly illegal one vanishes through the refusal funnel.
- **Deploy test, before the retrain**, both required: no artifact
  becomes invalid (a teacher change orphans the corpus, clones, and
  bars; an rng-sequence change orphans seed pins; these wait for the
  boundary and the re-cut); and the old habit at the new price is
  declared harmless, welfare and every need's route holding (041:
  zero rest scenes pre-declared), or compensated below. Harmful
  waits (054 FR-013).
- **Interim compensation**: a temporary dial on an activity the
  frozen roster already performs at a material rate (the groom bump).
  A declared, temporary exception to rule 2: no time term in the
  dial, the revert a deploy at the reseat or sooner if rule 10's
  live layer fires. The dial passes the same deploy test. Cost: it
  pays the old habit at the new price (the bump bought Clementine's
  loop, hence the revert).
- **Census rule**: after the change and before the retrain a census
  measures the roster's choices, not the price. State readings stand
  (needs, demand, welfare: rule 3's arithmetic and rule 10's live
  layer run now); choice shares carry a re-verify trigger naming the
  next seating, never a conclusion, which rule 7's contrast reads
  after the retrain. No census inside the deploy transient: wait until
  needs oscillate around a stable mean.
- **One retrain per generation**: bundle the changes at the boundary;
  a served retrain before a schema change is throwaway work (lab
  arms are not reseats). Attribution confound accepted; ablation is
  the fallback if a result surprises.

### 10. Two-layer welfare gates; a noise reading is never a pass bar
*(Owner direction 2026-08-14, attn-cert selection; ROADMAP guards 1
and 2; reshaped by the owner 2026-09-13. Banked 2026-09-13.)*

A seating gate answers two questions with different bars. Is the
world no worse than the scripted roster makes it? That is the floor:
the question is fixed, its number floats with the world it is
measured in. Is what this seating is for worth what it costs? That
is a trade, declared per seating, ruled by the owner (ROADMAP
principle 4). An incumbent-relative bar folds the two and ratchets:
every winner raises it, so a seat class chosen for anything but
welfare could never seat.

- **The floor**: rule 1's team Nash, seat-paired, at or above the
  scripted baseline of the same battery, plus the catastrophe gates
  (distress age, stress bar, fallback bounds); thresholds are
  multiples of the re-measured baseline, never constants (F-021).
  No noise allowance; a miss inside noise is replicated on disjoint
  worlds before it counts (F-004). A world change (rule 8) or a
  welfare amendment (rule 1) moves both sides, so only the
  catastrophe gates bound what either costs; the amendment's own
  contrast (rule 8) is its check.
- **The trade**: before instruments run, the selection doc declares
  what the seating is for, the instrument that measures that benefit
  (F-010's out-of-distribution test, fingerprints, probes), and the
  welfare it may cost, which is that seating's own bar. The delta
  against the incumbent at the same seat (guard 2) is the reading it
  is held to, cross-generation by nature (rule 9). A benefit asserted
  and not measured does not seat; a cost inside the allowance against
  a null benefit is the owner's ruling, on the record.
- **Boundary test, bar or reading**: a bar was declared before the
  instrument ran, names its battery, and changes only on the owner's
  word; a trade bar is never inherited from another seating. A reading (the noise floor, a parity band,
  a screen prediction) may set a bar, never be one. No trade bar sits
  inside noise, and a result inside noise establishes nothing: a
  benefit or a contrast is absent for the decision, a cost is
  uncharged. Gates confer eligibility, never precedence.
- **Failure**: a selection gate stops, reports, and waits for the
  owner. The live layer (catastrophe gates on the running world, the
  watchdog, the soak) acts without a ruling and can trigger rule 9's
  early revert; rule 9's mid-generation readings feed it, never the
  floor.
- **Carve-outs**: a seat class whose operating mode breaks a gate as
  written gets it reshaped to ask the same question, never waived
  (LLM seats: a declared fallback band replaces zero-fallback). Lab
  passes owe the same declare-before-you-run shape: welfare stops and
  a plateau rule on unshaped return. Diagnostics (F-037) inform,
  never gate.
- **Known cost, re-verify**: the floor is battery-bound (F-009), so
  the battery runs on the served config plus the worlds that trigger
  known failures (F-010) in the deployed company (F-012, F-023); the
  floor and noise floor are re-measured, clustered by world (F-004),
  at any change of them, and every fixed dimension is stated with the
  claim.
