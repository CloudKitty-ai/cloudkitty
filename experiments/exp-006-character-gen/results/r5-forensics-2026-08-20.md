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

## Regeneration

Traces are deterministic and gitignored (`traces/`):

    .venv/bin/python forensics_r5.py trace candidate-r5 880030 \
        --config family-spread/family-11.toml
    # likewise: candidate-r5 880015, candidate-r5 880001,
    #           reference-r5 880008
    .venv/bin/python forensics_r5.py summary traces/trace-candidate-r5-880030.npz

Window probes in this doc read the npz directly (states, chosen,
pos_*, sidecar meows); layouts are documented in forensics_r5.py.
