# Gen 2 inputs banked from the step-5 shakeout

Written 2026-09-11, for review before Gen 2 design. Gen 1 scope is
closed against all of it: the owner ruled the free-register question
"do nothing for Gen 1" (verbatim: "For now let's go with option 3 (do
nothing), I feel like we have enough moving parts here before we seat
our gen 1 kitties without adding more speculative work"). Everything
below is Gen 2 sitting material, none of it blocks the reseat.

## The organizing finding: behavior persists when the world values it

The shakeout's cleanest controlled contrast, no instrument between the
reader and the claim: nothing rewards speaking, yet the fog arms held
here-words at ~130–150/1k decisions through 9M PPO ticks while the
nofog arm shed them (109 → 84/1k and falling). Same corpus, same
leash, same reward — under fog a here-word informs a teammate who
cannot see, and that information reaches team return through better
decisions. Meanwhile every behavior whose value the world does NOT
realize decayed: groom-other fell from the imitated ~13/1k to
0.9–8.4/1k (fixed for Gen 1 by the spec-054 reprice), and the free
register lives on entropy income and the lesson prior (mechanism
settled 2026-09-11: entropy bonus on consequence-free heads, gated by
KL affordability; the purr-rest / chirp-play mapping is amplified
symmetry breaking from the frozen trunk, not communication — nobody
routes on the words, approach 0.35–0.36 vs 0.49 want_cuddle).

## The free register: hearable options (deferred whole)

The digest already delivers all 15 words (kitty*.msg.purr.rate etc.,
A5-verified for masked and visible speakers) — "hearable" needs no
schema change, only a consequence. The ladder, as discussed:

1. **Scripted listener rung** (law-class): a needs_driven cat hears
   purr from an unseen friend and drifts toward it. Reads only the
   digest (imitable); seeds corpus demonstrations; the natural sibling
   of the banked cuddle_response / play_response rungs (whose trigger
   fired in phase 2). Does not touch the "free register never
   scripted" ruling — scripted cats would hear, never speak.
2. **Purr conduction** (pricing, spec-054's class): proximity to a
   purring cat pays a small cuddle drip. Anchors both sides through
   team return with no reward term (F-018 layer 2 clean). Needs the
   cuddle-economy doctrine applied — rider tier, no stacking with the
   mutual tier — or a purr-pile is the next F-027-class attractor.
3. **Do nothing; let Gen 2's world supply the value** — RULED for
   Gen 1. Under hidden needs an honest state signal is information a
   teammate cannot get otherwise, the same mechanism that anchored
   here-words under fog. The risk to carry into the sitting: value
   that is merely available has not been enough; the gradient has to
   find it.

Success metric already exists: `phase2_read.py`'s approach read with
purr/chirp in the word list (run once 2026-09-11).

**Revisit trigger for doctrine rules 5 and 6 (owner, 2026-09-13).**
Rule 6 makes lineage rows the free register's only seed. Rule 5 makes
a Gen 1 policy's rows an illegal read once Gen 2 hides the needs it
decided on, and a policy cannot be re-recorded under a narrower view.
Rule 7 now carries the resolution: where the world gives a word
something to say, the register may start unseeded, from the entropy
bonus and the scarcity, which is the contrast F-022 names as its own
invalidator (F-022 was measured under global vision, where F-026
found the channel redundant). If the Gen 2 free register stays silent
under real scarcity, the gap is back and one of the two rules bends:
a rule 5 carve-out for lineage rows (the word arrives without its
cause, a known cost), or a second seed source in rule 6. Levers to
try before bending either: give the register a fact no law-named
word carries (Want* already covers hidden needs; candidates are a
resource last seen under fog, the speaker's next move, a third cat's
state); a positive-signaling loss on the message head, a training
device under rule 1's outside-the-rule clause, carrying rule 7's cost
if the world does not value the word. The owner expects some design
assumptions to move before the sound-named words come alive.

## Imagining the friend: a mini-friend-model inside the mind (owner's idea, 2026-09-14; banked as a Gen 2 design input)

The roster-wide mind can pilot any seat (§"Where personality lives").
Use that: distil from the mind a very small per-friend predictor,
"what would I do in that cat's place", capped so it can hold only the
friend's most common behaviours and never a functional clone; feed
its prediction back to the mind as imagination; then, once that
baseline works, correct each mini-model with the friend's observed
behaviour. Simulation-theory theory of mind with a capacity cap.

Why it fits here. In self-play every friend IS the same mind, so
"predict the friend" and "predict myself in its seat" are one
training signal and no extra corpus is needed; under five served
networks the friend drifts from self by a seed's worth, which is what
the observed-behaviour correction closes. Gen 2 is where it earns
its keep: with needs hidden, predicting a friend's next act from
visible cues is inference of its hidden state, rule 8's third route
to a fact. The free-time plan's "helping a friend's favourites" needs
a place to hold a belief about what the friend wants; this is it.

The design question is the consumer, not the model (rule 7: a
prediction nobody acts on decays into an unused auxiliary). Three
consumers already have instruments: proposal acceptance (the
partnered-refusal tax, Biscuit ~5%, read off the refusal stamp by
`reason`; the first benefit instrument), meeting a friend (the
into-the-fog response, §Friend-in-fog pursuit), and consent (learned
rather than scripted). Doctrine: the mini-model lives inside the
mind and reads only what the mind sees (rule 5); its training loss is
a device under rule 1's outside-the-rule clause, never a reward term;
it predicts acts, not words (rule 6); no schema change while the
imagination stays internal (it attaches naturally to the entity
transformer's kitty rows). Risks to design against: over-trust (a
tiny confident model is confidently wrong out of distribution: a
scripted cat, a new roster; calibration is the read, and the
correction should be a running per-friend error signal the mind can
see, so it learns when to discount the prior) and shortcutting (where
the mind can read the friend's needs directly, as at Gen 1, it will
ignore the model; train it where the direct route is closed).

## Encouraging emergence without shaping — the levers, ranked

1. **Design scarcity of information, not incentives for behavior.**
   Hidden needs is fog's scale-up: once a friend's needs are hidden,
   every honest signal becomes decision-relevant and the team reward
   anchors it unshaped.
2. **Prices as physics, not nudges.** Price states of the world
   (warmth conducts, dirt exists), never behaviors (no bonus for
   approaching). Spec 054 sits on the right side of the line.
3. **Stage the leash.** The KL leash is the deliberate anti-emergence
   force; a Gen 2 recipe could hold it early and release late (or
   re-anchor to the policy's own earlier self), with the welfare stops
   as the guardrail instead of the teacher pull.
4. **Match horizons to the hoped-for behaviors.** γ 0.998 is a
   ~500-tick horizon; reciprocity-class behaviors mature slower and
   are invisible to the gradient regardless of value.
5. **Vary the world, not the reward.** Episodes with different
   scarcity profiles give niche behaviors episodes where they win.

Counterweight, from this project's own record: exp-003's collapse and
F-017's mixed arms are why demonstrations-plus-leash exists. The
doctrine is a division of labor — reward stays team welfare only,
demonstrations buy what is cheap to demonstrate, and the world's
design is where to be opinionated.

## Friend-in-fog pursuit: build at Gen 2 corpus collection (RULED by the owner 2026-09-13, "Defer to gen 2"; analysis of 2026-09-11 below)

Owed before this sitting: a live read of unanswered from-the-fog
calls per hour on the served Gen 1 roster, off the refusal stamp's
`reason` field, so the cost of waiting is a number here.


The cue-answer rungs (cuddle_response / play_response) are ruled
wanted but deliberately NOT built for Gen 1. Timing rule, from the
shakeout's own evidence: build a behavior when the world that values
it exists — a behavior built earlier is leash-held, not
reward-anchored, and decays (groom-other, 13 to 0.9/1k). Gen 1's
world assigns pursuit near-zero marginal value (needs visible, roster
dense: friend-in-view .80, nn 1.41 — an adjacent friend offers the
identical mutual-tier relief with no travel), so a Gen 1 rung's
demonstrations would be shed by PPO and need a reprice-style rescue.
At Gen 2, hidden needs makes the call the only channel for a friend's
state and the rung rides the mandatory corpus/prereg cycle at ~zero
marginal process cost; the FR-036 cuddle-clause revisit travels with
it. Cost of waiting: the Gen 1 serving period shows unanswered
FROM-THE-FOG calls only — the minority slice; visible callers are
answered at ~2x baseline (finding-4 revision, RESULTS.md @ aab284b).

**Design constraint this places on Gen 2's world**: the world must
actually deliver the scarcity that anchors pursuit — hidden needs at
minimum, and the density/size question read against it — or the rung
repeats the Gen 1 pattern. Verify with the fresh-start-conditioned
response read (this week's instrument) before and after the rung
lands.

## Corner and edge coverage in training (RULED by the owner 2026-09-15, "Corner and edge coverage in training seems wise. Let's add that to Gen 2")

**The finding.** The step-7 battery's only catastrophe shape is a corner
attractor (`fog-gen1-cert/RESULTS.md` §Battery, swaps digest): a cat
with eat or drink at 90–100 alternating two moves on the world's corner
tiles, (0,0) / (0,1) / (1,0), for hundreds of ticks, with chow visible
in 40% of those rows and Eat chosen in a tenth of them. The chosen move
carries p ≈ 0.53 against 0.19, so it is a learned preference in that
pocket, not a greedy tie. Across the 100 swap legs 1.8% of runs reached
a distress age of 150 this way, more than half of them in a seat whose
mind had not been swapped; Pumpkin's seat (eat rate 0.6, double the
others') carries the most. The scripted roster never fails there.

**Why the pocket is untrained.** Every episode, in corpus collection
and in PPO, starts each cat on its configured tile (`[[kitty]] x, y`
in the served config; the trainer's episodes reset the same world).
Corners and edges are reached only by drift, so the corpus and the
rollouts under-sample them, and a roster-wide mind that is asked to
drive from a corner is off its data. Under fog this compounds: at a
corner half the disc is off-world, the cat sees less, and the memory
token is the only route back to a bowl it cannot see.

**The recipe item (Gen 2; a training-distribution change, not a
teacher or price change, so rule 9 orphans nothing scripted; the served
config keeps its fixed starts).**

1. Randomised start positions at corpus collection and in every PPO
   episode: each cat's start tile drawn over the whole map, with the
   edge ring and the four corners weighted so they appear at a declared
   share (pencil 25% of starts on the edge ring, 5% on a corner; pick
   from the coverage instrument below). Declared as a training-config
   deviation beside the radius and the shakeout keys.
2. Element placement draws where the served world allows (bowls and
   beams already spawn under `[elements.*]` rules; check the rule
   covers edge tiles rather than assuming it).
3. **A coverage instrument before the pass**: visit share of the edge
   ring and the corners per cat-tick, corpus vs probes vs the served
   world's own logs, so the declared start shares are set from a
   number and the pass can show the pocket got filled.
4. **A stuck read as an INVESTIGATE row**: net-zero displacement over N
   ticks with an armed need (the corner signature), per seat, off the
   probe rows; the same detector is the decoding-time guard the
   deferred distress intervention would key on (BACKLOG; the
   LLM → local → scripted fallback chain).

**What it is not.** Not a reprice: the Nash team reward already makes
a starving cat dominate, and the Gen 1 minds feed Pumpkin five points
better than the scripted cat in ordinary operation. The owner's
question of 2026-09-15 (is eat worth more under fog?) was assessed
against the replay and answered no for Gen 1; the Gen 2 identity
vectors (trait draws in training) are where a high eat rate stops being
one seat's special case.

## The clock input is a de-synchroniser (found 2026-09-15 at the step-7 export; `fog-gen1-cert/RESULTS.md` §"The clock input"; **RULED a Gen 2 fix by the owner, 2026-09-15: "Let's ensure we fix this in gen 2"**)

The served seam pins the episode-clock observation to 0; training ran
it as t / 2000. Re-running the certified roster with the clock pinned
raised the catastrophe tail from 0 to 3 runs in 120 while leaving
welfare means untouched, and the worst case was a perfect two-tile
limit cycle (MoveW / MoveE 174 / 174 at p 0.96 with the bowl in view).
With a pinned clock the observation repeats exactly tick to tick, so a
greedy policy that maps two adjacent states to opposite moves never
escapes; a moving clock never repeats the state. The Gen 1 minds have
been leaning on the clock as noise. Gen 2 recipe inputs: either drop
the clock input entirely and train the mind to break its own cycles
(the corner/edge coverage item above is the same family of fix), or
keep it and serve it as trained. Independently of the clock, a stuck
detector at decoding (net-zero displacement over N ticks with an armed
need; the deferred distress intervention's trigger) is the served-side
guard that does not depend on what the mind was trained with.

## Also standing on the Gen 2 shelf (pointers, ruled elsewhere)

- World-size × radius screen; first data point = the shakeout's r-3
  tolerance (policy holds welfare at pin−1 where the anchor degrades).
- Hidden needs (the Gen 2 half of the fog split); F-026 deferred here;
  F-035 waterline contagion input.
- Rate-based A17 + config-aware declarations (#367's root fix) and the
  scene-span instrument (blocks the uptake reads).
- consent_line for needs_driven and empty-bowl early end (owner
  shelvings, BACKLOG #368).
- Social-grooming demand (corrected 2026-09-13, RESULTS.md
  `groom_cells.py`; the earlier "row 0–1 slot bias = corpus density"
  reading was wrong): all-policy rosters keep themselves clean
  (self-groom ~2× the teacher), so the only dirt left for a friend to
  groom is Biscuit's, and Biscuit's teacher never grooms anyone. A Gen
  2 world that wants visible social grooming has to supply dirt the
  self form cannot clear as fast (rule 8 variance, rule 2 physics),
  and Biscuit's teacher needs a groom response if that seat is to
  give bath as well as take it. For Gen 1 the owner ruled (2026-09-13)
  Biscuit's non-grooming a declared trait: Biscuit gives play where
  the others give bath, reciprocity in another currency. Decide the
  two together: dirt the self form cannot clear makes a non-grooming
  seat one fifth of the givers missing.
- Beam naps are not world-valued at Gen 1 (step-7 beam screen,
  `fog-gen1-cert/RESULTS.md` §"Beam naps"; owner ruled 2026-09-15 the
  beam stays at 7). Policies sleep 12–14% of ticks against the
  teacher's 8% and take the plain 5.0 sleep wherever they are; a 7, 10
  or 15 beam premium never moves the in-beam share out of the seed
  spread (0.014–0.066), while the β 0.10 leash holds the teacher's
  0.21–0.22. Rule 7 reading: while sleep is cheap anywhere, the beam
  premium is invisible to the sleep budget. A Gen 2 world that wants
  beam naps has to make off-beam sleep worse (rule 2, a state of the
  world: colder ground, slower relief), not the beam better; the price
  lever has been screened and does not work. Biscuit's seat naps on
  beams least of all (0.006–0.022) at every price and dose.
  **The beam package (owner's proposal 2026-09-15, under consideration,
  not ruled):** three world changes together. (a) Off-beam sleep relief
  down (5 → about 3 against the beam's 7): a need-40 nap goes from 8
  ticks in the open to 13, so a beam saves ~7 ticks and pays for a
  6–7 tile walk, which is where the served 4–5 beams already sit
  (break-even today is 2–3 tiles, and reaching it by count alone would
  take 20–25 beams on the 20×20 meadow). (b) Beams long-lived (today
  `ttl = 300`, then respawn elsewhere; the owner's refinement of
  2026-09-15 is a much longer lifetime rather than permanence): under
  radius 4 the walk to a beam is on memory, and a remembered beam that
  has expired makes the walk a bet. The staleness odds are about
  (memory age + walk) / lifetime: with a typical memory age near 100
  ticks and a 6-tile walk, a 300-tick beam is gone about a third of the
  time, a 3,000-tick beam about 3.5%, a 6,000-tick beam under 2%. A
  lifetime of 2,000–4,000 ticks (25–55 minutes of watching at 800 ms a
  tick, several naps and walks) buys nearly all of permanence's value
  for the walk while keeping what permanence loses: a beam camp
  dissolves when its beam moves, layouts keep changing so the mind
  cannot memorise a map and the memory token stays load-bearing, and
  the meadow still shifts over a sitting. The cosleep-on-beam charm
  (0–10 opportunities per probe today on every arm but β 0.10) needs a
  beam that outlasts a nap and a friend's approach, which any of these
  lifetimes gives. The day/night cycle is client-side only
  (`client/props.js`); the engine's beam lifetime is independent of
  it, and the owner reads beam movement as marginal charm beside the
  cycle, the cats and the bugs. (c) A couple
  more beams for the look of the meadow, a visual choice under the
  served-world density ruling. Costs to weigh: the moving sun is the
  only sign of time passing on the meadow (Client's call how to keep
  it); permanent beams with conduction and the cosleep drip are a
  reliable spot to farm cuddle by sleeping unsleepy (rule 4 check:
  sleeping ticks with sleep need under threshold, per seat); a fixed
  layout invites map memorisation, which the long-lived (not
  permanent) variant avoids by itself; permanent beams would need the
  layout randomised per episode beside the corner/edge starts. Prediction if
  adopted: in-beam sleep share rises toward the scripted 0.26–0.29 at
  β ≤ 0.04 without the leash carrying it; instruments = `step7_reads`
  beam share and `phase2_read` cosleep opportunities. Rule 9: the
  teacher walks to beams more when they are always there, so the whole
  package waits for the Gen 2 collection.
- Critic compression rewatch (#365): the critic ranks correctly but
  does not extrapolate down; matters if training enters new return
  regimes. Step-7 rewatch on the B3 critic: EV 0.65–0.72 flat across
  every bin on twenty arms, no recurrence.
- Here-word emergence proof (the `announce_here = 0` no-seeding
  control, the F-026 overturn test): DEFERRED here from step 7 (owner,
  2026-09-13). The current recipe cannot run it fairly: the leash sums
  KL over both heads, so a silent clone anchor pulls the message head
  toward silence and a null reads as leash-held. Design it with the
  free-register question above (message head off the leash, or an
  entropy bonus on it, as a declared arm) so both contrasts run
  against hidden needs in one pass.
- Where personality lives (clarified with the owner 2026-09-13).
  Every Gen 1 candidate is one roster-wide mind that drove all five
  seats in self-play; it is playful in Biscuit's seat and needs-driven
  elsewhere because it infers its seat from the world's fingerprint
  (by-id rows, the neighbours' need patterns, its own need vector) and
  copies that seat's teacher (matched-state read: Biscuit's seat keeps
  playing at .48–.52 where the other seats play at .00–.09, teacher
  .56 / .04–.08). Biscuit 2.0 was the same shape. So a mind seated
  elsewhere becomes that seat's cat, and a roster change (a swapped cat,
  reordered ids) scrambles the fingerprint the mind keys identity on;
  nothing certifies that because the roster never changes within a
  generation. The portable alternative, a trait vector in the
  observation with training across trait draws (rule 8 variation, the
  served roster as majority episode) and one parameterized teacher
  (comfort line and need rates as its dials, dissolving the
  playful / needs_driven split), is a schema change and Gen 2 material;
  **RULED 2026-09-13 (owner): identity vectors are a GEN 2 member;
  free time is GEN 3.** The Gen 2 block, self-only in the
  observation: six need-rate multipliers, comfort as ticks of slack,
  the consent line, and a per-source favourite weight vector (one-hot
  the single-source case); one parameterized teacher (comfort line +
  favourite, the consent gate on every partnered favourite) replaces
  the playful / needs_driven split; the corpus samples trait draws
  with the served roster as the majority episode (rule 8); a toml
  change inside the trained region needs no retrain. Until Gen 3's
  enjoyment economy lands, a favourite is one of the needs and is
  valued through that need's relief (Biscuit's play today), so it is
  world-anchored to that extent and leash-held beyond it (rule 7's
  declared-personality carve-out); Gen 3 is where favourites outside
  the needs get their value. Design detail on `ROADMAP.md` §free time,
  "Teacher side" (the slack formulation, the Pumpkin case, the
  per-cat scripted sweep as the pin procedure). The capacity
  side of the question (does driving every seat cost the mind
  capacity) is being measured on the B3 corpus (`fog-gen1-cert/PREREG.md`
  §Capacity check).
- Doctrine rule 5 view holes, fixed at the Gen 2 schema bump (moved
  here from DESIGN-DOCTRINE.md 2026-09-13): the fog view still exposes
  friend-record fields no rule reads (strip them as memory was); the
  exploration rule follows a stop on a private route the observation
  does not carry (add the direction to the waypoint as observation
  cells). Until then nothing may read either. Becomes a hole the day
  Gen 2 hides needs (Product, 2026-09-13): the groom-response
  valuation reads the groomee's bath through `groom_cuddle_pay`
  (`crates/cloudkitty-core/src/behavior/needs_driven.rs:426`), legal
  while needs are visible.
