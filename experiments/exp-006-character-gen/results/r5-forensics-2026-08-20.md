# r5 failure forensics (exp-006) — the co-sleep deadlock

**Owner's ruling (verbatim, 2026-08-20):** "Let's start with forensics.
If we've found an unusually hard world, that's worth investigating and
documenting. It could be a useful distribution tail benchmark going
forward."

**Headline: the r5 failures are not water contention.** Nothing was
scarce in any distressed run. The catastrophe is a behavioral deadlock:
the attn-a1-s3 twins (the same artifact seated at both Pumpkin and
Kittybear, in candidate and reference compositions alike) lock into
mutual sleep-with-partner at the far corner of the map and stop
servicing every other need. A second, independent pathology has the
e004-a1-s2 MLP pacing near resources without consuming. The lineage
candidate's contribution is adherence: it joins the sleeping pile and
grooms it instead of leaving. Family-11 does not cause any of this; its
geometry (26×26, one 2×2 pond) gives the deadlock room and makes every
locked tick expensive.

## Instrument and validity

`forensics_r5.py` traces single battery runs per tick (full global
state, chosen action/message heads, element positions, meow log),
reusing cert_harness6's seat loaders and stepping. Each trace re-derives
its battery row as a validity check. All four match exactly:

| trace | battery row | trace reads |
|---|---|---|
| candidate-r5 880030 | mda 2331, nash 0.8730 | 2331, 0.8730 |
| candidate-r5 880015 | mda 443 | 443 |
| candidate-r5 880001 | mda 0 | 0 |
| reference-r5 880008 | mda 465, nash 0.9200 | 465, 0.9200 |

Menu-index decoding cross-checked against the codec's normative-order
test (`codec.rs`: 0=Move, 8=SleepSolo, 9–11=SleepWithKitty(slot),
16=Eat, 17=Drink, 33=Idle).

## Scarcity ruled out

In every traced run, water is 4 tiles at fixed positions for all 20,000
ticks: a single 2×2 pond at (7–8, 2–3). Chow holds at 6 elements with
22–30 total servings through the entire 880030 distress window; bugs
hold at 3. No element count dips during any distress window. Cats in
drink distress stood 5–37 tiles from standing water the whole time.
The battery doc's suspected mechanism (water contention among five
cats) is refuted; there is also no kitty-kitty tile exclusion in the
engine, so water cannot be blocked by occupancy at all.

## Mechanism 1: the twin co-sleep deadlock (the catastrophe carrier)

Seed 880030, ticks 4417–6748 (the 2331-tick streak). Entry: the twins
play-chase each other into the SE corner around tick 4200–4300 (chosen
actions: chaseK0/playK0 interleaved with moves), settle on adjacent
tiles at (24,25)/(24,24), and begin co-sleeping while eat and drink are
already climbing. Then the loop holds:

- Pumpkin chooses `SleepWithKitty(slot 0)` for **2151 of 2200**
  decisions in ticks 4500–6700; Kittybear for **2084 of 2200**.
- Partner fields confirm the pairing is mutual: each twin's partner
  points at the other for ~80% of the window (the rest are the 1-tick
  wakes between sleep bouts).
- Co-sleep relieves sleep and drips cuddle, so those two needs stay
  low (~4 mean) while eat, drink, play, and bath saturate at 100.
  Each wake tick, the policy observes an adjacent sleeping twin and
  re-chooses co-sleep. The same mind holds both seats, so both make
  the same wrong choice, and each one's choice renews the other's
  context. Position does not change for thousands of ticks.
- The meow channel broadcasts the distress throughout (want_eat /
  want_drink from ids 3 and 4 all window). Nobody responds; no mind
  in this roster has a fetch-or-lead behavior. This is exactly the
  failure class the meow-signal / Here*-teacher work targets.
- Release: the pair had drifted to (19,19) by tick 6640 (occasional
  wake-play breaks move them a little). At ~6700, coincident with
  Miso transiting the east side at 13 tiles' distance, both switch to
  move/eat within ten ticks of each other, beeline 30+ tiles to the
  pond, and fully recover by ~6850. The policy is not confused about
  what to do once out of the loop; the loop itself is the defect.

The same deadlock carries the other two distressed runs:

- **reference-r5 880008** (streaks 465/453): same twins, same
  `sleepK0` loop, corner (22, 20–21), broken after ~500 ticks. The
  reference composition fails through the identical mechanism; the
  battery's "world-level component" is the twins' component. Both
  compositions seat attn-a1-s3 twice per the §6 plan.
- **candidate-r5 880015** (streaks 443/347/276): the triadic variant.
  Twins co-sleep at (24–25, 23–24); ppo-L-04-s1 stands over the pile
  choosing `groomK0`/`groomK1` for 370 of ~475 decisions while its own
  drink pins at 100. All three break out together at ~3995.

Consistency check across shapes: r3 (Miso, Biscuit, Pumpkin) seats
only one copy of s3, so the dyadic attractor cannot form, and r3
passed with worst streak 50. Shape iii on the cutover config seats the
same twins and showed only brief events (worst 137): on 20×20 with
7–9 water tiles the loop gets interrupted early and relief is near.

## Mechanism 2: e004-a1-s2 corner pacing (independent of the twins)

In 880030, Clementine (e004 MLP) idles and paces the NW corner for
~1500 ticks at eat/drink 100, nine tiles from the pond, choosing a
near-uniform mix of moves, groomSelf, and idle. At ~6000 she touches
the water tile, relieves briefly, wanders back to (0,0), and saturates
again. In reference-880008 the same artifact does the same pacing at
Biscuit's seat (moves and idle around (0,0)). This is a separate MLP
pathology, milder than the deadlock, present wherever e004-a1-s2 sits.

## Decomposition, restated with mechanisms attached

- **World-level component** (battery doc's (a)): the twin deadlock,
  present in both compositions because both seat s3 twice. Different
  carrier seeds are the seed lottery over when the twins happen to
  play-chase into a quiet corner (F-009).
- **Candidate-specific increment** (battery doc's (b)): composition
  effects on top of the same attractor. The candidate replaces
  scripted Clementine (who keeps moving and perturbing) with the
  pacing MLP, and seats L-04-s1, which adheres to the pile rather
  than leaving it. One traced catastrophe per composition is too few
  to apportion the 2331-vs-465 duration gap precisely; the structural
  difference in pile-adjacent behavior is the observed candidate-side
  mechanism. Biscuit's chronic ~7-point happiness gap is separate,
  present in the cleanest run (880001: 86.2 mean, zero distress), and
  matches its known leash profile (needs held at 15–20 rather than
  5–10; 77% idle plus 14% playing).
- **Family-11's role**: amplifier, not cause. 26×26 with one 2×2 pond
  (vs cutover 20×20 with 7–9 water tiles) puts the far corner 37
  tiles from relief, lengthens every recovery walk, and starves the
  corner of passing stimuli that break the loop early. The streak
  metric integrates all of that.

## On the owner's tail-benchmark idea

Family-11 r5 is a strong probe for exactly one thing: dyadic
self-interaction deadlocks under twin seating, plus consume-avoidance
pacing. That makes it a good distribution-tail benchmark for any
future roster that seats one artifact on multiple seats, and a poor
one for water-economy questions (its water is never contested). Worth
naming and keeping regardless of the gate decision. Related precedent:
exp-003's collapse finding (self-interaction failure) and F-010
(roster-OOD catatonia); this is the served-composition sibling of
both, and a register-note candidate.

## Follow-up measurements (owner's tactical questions, 2026-08-20)

**Is the deadlock possible on the seated (cutover) world?** Traced the
two worst cutover-config battery events. Neither is the co-sleep loop:
candidate×stress 880013 (mda 137) is Pumpkin choosing `drink` for 121
of 137 ticks at the pond while its eat need waits (serial
prioritization, self-resolving); reference×eval 870005 (mda 87) is a
brief pacing episode. Across 2.4M cutover ticks (both compositions,
eval + stress) the deadlock never formed. The cutover geometry (20×20,
water 7–9 scattered, stimuli-dense) both starves the attractor's entry
and caps its cost. This is a frequency bound from 120 runs, not an
impossibility proof; the policy preference that sustains the loop
exists regardless of world.

**solo-s3 report-only cell** (never a gate leg; SEATINGS `solo-s3`:
s1 / L-04-s1 / s3 / scripted / e004 — s3 seated once, neutral scripted
fill at Kittybear):

| cell | nash | worst mda | >225 | >150 | max low |
|---|---|---|---|---|---|
| solo-s3 × eval (cutover) | 0.9385 | 25 | 0 | 0 | 0.0000 |
| solo-s3 × stress (family-11) | 0.9128 | 159 | 0 | 1 | 0.0057 |

Readings, against the twinned compositions:

- **The deadlock class vanishes with the twin pair**, and e004's
  pacing never breached alone: family-11 stress goes from 2
  exceedances / worst 2331 (twinned candidate) to 0 exceedances /
  worst 159. Clementine's >bar pacing streaks in 880030 co-occurred
  with the twins' deadlock and did not recur without it.
- **The residual 159** (seed 880013, Pumpkin eat, ticks 6436–6595) is
  directed travel: 113 of 159 chosen actions are a consistent
  north-east march to food. On a 26-tile map a far-corner need spike
  costs more than 150 ticks of locomotion; the constitutional clause
  as frozen prices world size, not policy health. (Same seed, same
  kitty, same need carried the cutover stress worst at 137 — 880013
  appears to draw a hard need-phase alignment.)
- **Kin-gap arithmetic**: Pumpkin solo reads 94.28 vs 94.78 twinned
  (−0.50) with Clementine present, against the pre-wall kin
  dose-response gap of −0.94 (94.87 kin / 93.93 alone; cross-surface,
  so directional only). Company covers roughly half the kin benefit.
  Clementine's own reading is unchanged (94.74 vs 94.99).
- **Team cost of the cell**: 0.9385 vs 0.9478 (−0.0093), dominated by
  the scripted fill at Kittybear (91.36 vs 94.94 at that seat). Any
  policy fill re-raises the multiples question: e004 at Kittybear
  twins the pacing mind with Clementine's seat, s1 at Kittybear twins
  s1. Scripted is the only fill with no dyadic unknowns, and it was
  the one measured.

## E-arm fill cell (solo-s3-e0: ppo-E0-s1 at Kittybear; report-only)

Owner's follow-up question: other viable candidates from the pool.
As Biscuit candidates the E arms are disqualified by the fingerprint
record (play 0.34–0.44×, bug 0.00×, duets 0.04–0.05× — full
character erasure; that is what the control arms are for). As the
fill for the vacated s3 seat:

| cell | nash | worst mda | >225 | >150 | max low |
|---|---|---|---|---|---|
| solo-s3-e0 × eval (cutover) | 0.9476 | 74 | 0 | 0 | 0.0026 |
| solo-s3-e0 × stress (family-11) | 0.9207 | 435 | 1 | 2 | 0.0163 |

- **Eval**: the E fill recovers the scripted fill's team cost
  entirely — 0.9476 vs twinned 0.9478 vs scripted-fill 0.9385. The
  E0 seat itself reads 95.22; Pumpkin solo 94.42.
- **Stress**: the fill re-imports a tail. The 435 (seed 880017,
  ticks 365–800) is a heterogeneous pile: solo Pumpkin choosing
  SleepWithKitty 382/435 while ppo-L-04-s1 grooms the sleeper
  366/435 and the E arm half-adheres. Same seed under scripted fill:
  mda 0. F-027 point 5 records the refinement: twins make the lock
  self-renewing, heterogeneous piles are weaker but bar-relevant,
  and scripted seats are perturbation sources — every scripted seat
  replaced by a policy mind removes a stabilizer.

**The estimator question**: E1-s1 and E1-s2 carry the D-002 aux head
(Linear, summary 128 → 5×6 — all five kitties' six needs; E1-s1 val
calibration MAE diag .033 / offdiag .0375 / worst pair .041). E0
seeds are the estimator-off controls. At the fingerprint level E1 and
E0 are statistically indistinguishable, and the policy-artifact
contract exports the actor only, so the head stays in the training
checkpoint either way — it is a training/telemetry organ today, and
the reason to prefer an E1 seed is fog-era analysis value, not served
behavior. Harness note: seating an E1 requires the estimator-stripped
copy (commands in fingerprints-2026-08-20.md).

## E1 dialect census (owner's question; report-only)

Measured in the seat under consideration: each E1 seed
(estimator-stripped actor — the exportable object) at Kittybear in
the solo-s3 fill composition, cutover config, eval seeds
870001–870003 × 20k, every meow counted by emitter from the engine's
own log.

| word | E1-s1 | E1-s2 |
|---|---|---|
| rate | **34.8/1k** (32.8/31.6/40.0) | **59.0/1k** (54.6/59.8/62.5) |
| purr | 859 (41.2%) | 3143 (88.8%) |
| mew | 858 (41.1%) | 99 (2.8%) |
| here_water | 256 (12.3%) | 126 (3.6%) |
| here_critter | 80 (3.8%) | 148 (4.2%) |
| here_sunbeam | 9 (0.4%) | 5 (0.1%) |
| want_* (all six) | 25 (1.2%) | 18 (0.5%) |
| here_food | 0 | 0 |

Readings:

- **E1-s1 is a conversationalist**: purr and mew in even measure
  (41/41) with a real here_water habit — one meow in eight announces
  water. **E1-s2 is a purrbox**: 89% purr, mew nearly absent.
- **Company reshapes volume (F-012 on display)**: E1-s2 ran 178.7/1k
  in its training environment and 59.0/1k in this composition;
  E1-s1's 42.3 → 34.8 barely moved. The dialect *mix* is the stable
  signature; the volume is contextual.
- **Spontaneous here_water is notable for the fog program**: the
  Here* register is never scripted (§4b), and here-words are
  mask-legal only near the referent, so these are grounded
  announcements. E1-s1 carries the strongest spontaneous
  grounded-reference habit measured in the pool — under global
  vision, where F-026 says it earns nothing.

## Regeneration

Traces are deterministic and gitignored (`traces/`):

    .venv/bin/python forensics_r5.py trace candidate-r5 880030 \
        --config family-spread/family-11.toml
    # likewise: candidate-r5 880015, candidate-r5 880001,
    #           reference-r5 880008
    .venv/bin/python forensics_r5.py summary traces/trace-candidate-r5-880030.npz

Window probes in this doc read the npz directly (states, chosen,
pos_*, sidecar meows); layouts are documented in forensics_r5.py.
