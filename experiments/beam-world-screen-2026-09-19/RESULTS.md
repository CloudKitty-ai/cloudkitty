# Beam-world screen — results, 2026-09-19

Prereg `PREREG.md` (a920ad8, committed before the first leg). 25 configs
× 2 seatings × 30 seeds × 20,000 ticks, served clock, all 50 legs
complete (`results-raw/run.log`, about 45 minutes). Reader
`screen_read.py` → `results-raw/screen-read.json`; the full 50-row
table is `screen_read.py results-raw/battery --md`. Raws uncommitted.

## The short version

- **Beam count sets where the teacher sleeps; lifetime adds a little;
  the relief numbers add nothing.** Share of the scripted teacher's
  naps that begin on a beam: 4 beams 0.31, 5 → 0.38, 6 → 0.44, 7 →
  0.48 at lifetime 300, each about 0.02 higher at 3,000. Off-beam
  relief 3 vs 5 and beam relief 7 vs 10 move that share by at most
  0.01. The reach gate in numbers.
- **Floor 3 lengthens off-beam naps, so the tick-weighted in-beam
  share falls by 0.07–0.08** even though placement is identical. The
  prereg's headline measure was the tick share, so prediction 1 fails
  as written and the package corner misses the 0.40 bar on that
  measure (0.365); on placement it clears (0.458). Which measure the
  corpus bar is read on is the owner's call (below).
- **The frozen Gen 1 minds follow count at one sixth the level and
  ignore lifetime and relief**: naps starting on a beam 0.046 (anchor)
  → 0.057 / 0.068 / 0.077 at 5 / 6 / 7 beams, the same at 300 and
  3,000 ticks, the same at every relief pair. Rule 9 in numbers.
- **Floor 3 costs the frozen roster under 0.1 happiness and crosses
  no line. More beams at the served relief do cross it**: seven of the
  twelve relief-5 variants put one seed of thirty over distress age
  150 (Biscuit four times, Kittybear three, worst 236), where the
  anchor reads 49 and every floor-3 variant reads under 150.
- **No farming.** Sleep need at nap start moves up under the slower
  floor, not down, on both seatings.

## Teacher (scripted roster): placement and tick share

Pooled over five seats and 30 seeds. Placement = share of sleep starts
on a beam tile; tick share = share of sleeping ticks on a beam (the
declared headline). Beam relief 7 shown; beam relief 10 sits within
0.01 of every cell.

| beams | lifetime | placement, floor 5 | placement, floor 3 | tick share, floor 5 | tick share, floor 3 |
|---|---|---|---|---|---|
| 4 (anchor) | 300 | 0.313 | | 0.299 | |
| 5 | 300 | 0.380 | 0.380 | 0.363 | 0.294 |
| 5 | 3000 | 0.406 | 0.407 | 0.391 | 0.319 |
| 6 | 300 | 0.437 | 0.435 | 0.419 | 0.343 |
| 6 | 3000 | 0.453 | 0.458 | 0.438 | 0.365 |
| 7 | 300 | 0.480 | 0.480 | 0.460 | 0.382 |
| 7 | 3000 | 0.508 | 0.505 | 0.492 | 0.408 |

Per seat at the package corner (s3-b7-t3000-n6, tick share): Miso
0.34, Biscuit 0.29, Pumpkin 0.44, Kittybear 0.40, Clementine 0.39;
anchor 0.29–0.31 at every seat. Conducted sleep (asleep off-beam beside
a direct partner on a beam) rises with count, 0.031 → 0.047 at six
beams. Sleep share of cat-ticks: 0.077 at the anchor, 0.074 at floor 5
with more beams, 0.086–0.088 at floor 3 (×1.17).

Why the tick share falls under floor 3 while placement does not: a nap
begun off-beam takes 13 ticks instead of 8 to clear the same need and a
nap on a beam still takes 6, so the off-beam naps carry more of the
sleeping ticks. The teacher never chose differently.

## Frozen Gen 1 roster (gen1-A)

| beams | lifetime | placement, floor 5 | placement, floor 3 | tick share, floor 5 | tick share, floor 3 | happiness, floor 5 → 3 | max distress age, floor 5 / 3 |
|---|---|---|---|---|---|---|---|
| 4 (anchor) | 300 | 0.046 | | 0.046 | | 92.49 | 49 |
| 5 | 300 | 0.057 | 0.058 | 0.057 | 0.053 | 92.45 → 92.35 | 21 / 40 |
| 5 | 3000 | 0.058 | 0.056 | 0.058 | 0.052 | 92.43 → 92.36 | **183** / 40 |
| 6 | 300 | 0.068 | 0.068 | 0.068 | 0.063 | 92.41 → 92.33 | 76 / 93 |
| 6 | 3000 | 0.067 | 0.068 | 0.067 | 0.063 | 92.40 → 92.32 | **162** / 133 |
| 7 | 300 | 0.076 | 0.074 | 0.076 | 0.068 | 92.40 → 92.31 | **181** / 66 |
| 7 | 3000 | 0.078 | 0.075 | 0.078 | 0.070 | 92.39 → 92.31 | **236** / 67 |

Beam relief 10 reads the same within 0.01 on every column; its own
crossings are s5-b10-t300-n7 (207), s5-b10-t3000-n5 (183),
s5-b10-t3000-n6 (151). Nash 0.923–0.925 everywhere. Per seat the
placement is Miso's: 0.09 at the anchor to 0.12 at six or seven beams,
Clementine 0.06 → 0.09, Kittybear 0.04 → 0.07, Biscuit and Pumpkin
under 0.02 throughout.

**The crossings.** Seven variants, one seed each, every one at the
served relief (floor 5): seed 870022 Kittybear at 183 twice (both
five-beam, 3,000-tick variants), 870019 Kittybear 236, 870004 /
870006 / 870014 / 870025 Biscuit at 181 / 162 / 151 / 207. None of the
twelve floor-3 variants crosses (max 133). The anchor on these seeds
reads 49 (the battery's served-clock read was 47). This is F-043's
roster tail moved by a world change: more or longer beams at the
served relief put the Biscuit and Kittybear seats over the line on
about one seed in thirty, which is the swap legs' rate (1.8% of runs).
Not a Gen 2 reading (the minds are frozen), but a deploy reading: the
served Gen 1 roster under a beam-count change alone is not the roster
the battery certified.

## Farming (rule 4)

Sleep need at a nap start, share under 5 / mean: teacher 0.08 / 15.9 at
the anchor, 0.04–0.06 / 16.4–17.8 on the floor-3 and more-beam
variants (beam relief 10 lifts the under-5 share to 0.10–0.11, +0.03);
gen1-A 0.42 / 6.8 at the anchor, 0.28 / 8.8 under floor 3. Nothing is
flagged (the rule was +0.10 on the under-5 share or ±5 on the mean).
The slower floor moves need at start up, which is the opposite of
farming; the frozen minds nap early by habit (42% of their naps begin
under need 5) and that habit does not change with the world.

## Predictions

1. **Fails as written.** Lifetime and count moved the teacher's tick
   share up in every one of the 20 declared contrasts, but the relief
   contrast is 0.07–0.08, not under 0.03. The cause is nap length, not
   placement; on placement the relief contrast is ≤ 0.01 and the
   prediction's intent holds. The measure was the wrong one for the
   claim, and that is on the prereg, not the world.
2. **Not cleared on the declared measure.** s3-b7-t3000-n6 reads 0.365
   in tick share (0.458 in placement). By the decision rule, count 7
   clears it (0.408) and lifetime past 3,000 would not (300 → 3,000
   bought 0.02).
3. **Holds.** gen1-A's tick share never exceeds 0.078; relief
   contrasts ≤ 0.009.
4. **Half holds.** Happiness under floor 3 drops 0.06–0.10 (predicted
   under 1.5); the sleep share rises ×1.06 (predicted about ×1.5 on
   off-beam naps; the naps lengthen but the frozen minds' nap count
   falls with it). The no-crossing clause fails, on the floor-5
   variants rather than the floor-3 ones (above).
5. **Holds.** No farming shift on either seating.

## Decision rules, applied

- **The corpus bar at count 6.** On the declared tick share the package
  corner is under 0.40, so the rule says count 7 or a longer lifetime,
  and the table says count 7. On placement, the share of the teacher's
  naps that begin on a beam, count 6 is at 0.458 and clears. Placement
  is what a clone has to imitate (the walk and the lie-down); the
  sleeping-on-a-beam rows are its consequence, and floor 3 changes
  their weight without changing a decision. Experiments' recommendation
  is to pin the bar on placement and keep the count the owner's visual
  call; the declared measure said otherwise, so this goes to her.
- **Distress crossings.** Reported by name above; no variant is dropped.
- **Nothing here changes the served world.**

## What this settles for the Gen 2 collection

The teacher's beam-seeking under the package is count-driven: about
0.06 of placement per extra beam, 0.02 for the long lifetime, nothing
from relief. Whatever count the owner picks, the corpus will carry
that share of beam-started naps, and the F-047 re-verify on the clone
reads against it. Floor 3 does its work on the clone's side of the
reward, not in the corpus, exactly as the mechanism note in the prereg
said; whether the clone answers it is tier 2.

## Regeneration

```
experiments/exp-006-character-gen/.venv/bin/python experiments/beam-world-screen-2026-09-19/derive_configs.py \
  experiments/beam-world-screen-2026-09-19/results-raw/configs --sha experiments/beam-world-screen-2026-09-19/results-raw/configs/sha256.json
cp experiments/fog-gen1-cert/anchor-b3.toml experiments/beam-world-screen-2026-09-19/results-raw/configs/s5-b7-t300-n4.toml
nohup bash experiments/beam-world-screen-2026-09-19/run_screen.sh \
  experiments/beam-world-screen-2026-09-19/results-raw/configs experiments/beam-world-screen-2026-09-19/results-raw/battery 6 \
  > experiments/beam-world-screen-2026-09-19/results-raw/run.log 2>&1 &
experiments/exp-006-character-gen/.venv/bin/python experiments/beam-world-screen-2026-09-19/screen_read.py \
  experiments/beam-world-screen-2026-09-19/results-raw/battery --md --out experiments/beam-world-screen-2026-09-19/results-raw/screen-read.json
```

# Tier 2 — results, 2026-09-20

Prereg `PREREG-tier2.md` (ab6a6c9, before collection). Stage 1 corpus
and clone 2026-09-19 19:07–22:36Z, stage 2 PPO 22:36–04:15Z, stage 3
battery 04:18–05:04Z. Reader `tier2_read.py` →
`results-raw/tier2/tier2-read.json`. Raws uncommitted under
`results-raw/tier2/` (corpus 8.5 GB, clones, pass logs, battery) and
`artifacts/ppo-fog-{pkg,floor5}-s{1,2}/`.

## The short version: letter (a)

The corpus carries beam seeking into the clone in full, and β 0.04 PPO
takes all of it away on both worlds. Neither the count-6 / 3,000-tick
corpus nor the floor-3 reward holds it. The leash is the remaining
lever, and F-047 stands in full.

| stage | placement (naps begun on a beam) | tick share |
|---|---|---|
| teacher on the package corpus (40 rollouts) | 0.458 | 0.364 |
| package clone `pkg-vocab`, all five seats, package world, 5 seeds | 0.511 | 0.418 |
| pkg-s1 in its gen1-A seat, package world, 30 seeds | 0.070 | 0.065 |
| pkg-s2 | 0.037 | 0.035 |
| floor5-s1 in its gen1-A seat, floor5 world | 0.019 | 0.019 |
| floor5-s2 | 0.028 | 0.028 |
| gen1-A itself on the package / floor5 world (tier 1) | 0.068 / 0.067 | 0.063 / 0.067 |

Every arm ends where the Gen 1 minds already are, at or under the
mind it replaced. The probe series puts the loss between 2.5 M and
4.6 M ticks, the stretch where KL to the anchor climbs from 0.05 to
0.5 as the leash relaxes toward its 0.04 pin: pkg-s1 0.57 → 0.48 →
0.13 → 0.09, pkg-s2 0.55 → 0.48 → 0.19 → 0.04, floor5-s1 0.50 → 0.39 →
0.08 → 0.03, floor5-s2 0.48 → 0.48 → 0.15 → 0.04 (probe 1, ~2.5 M,
~4.6 M, plateau). Arms plateaued at 9.0 / 10.0 / 11.0 / 9.0 M ticks.

## Predictions

1. **Holds.** Teacher placement 0.458 (declared 0.42–0.50), tick share
   0.364 (0.33–0.40); per-seat tick shares Miso .34 / Biscuit .28 /
   Pumpkin .44 / Kittybear .41 / Clementine .38, tier 1's numbers.
2. **Holds, above the bar.** The clone clears the BC bars on the
   proposed read (reply mass .70–.79, msg@1 .954, wants 0.91–0.99);
   the applied read misses want_cuddle at 1.154, the tick's downgrade
   bias to the third decimal of the Gen 1 clone's 1.155. Its placement
   before PPO is 0.511 (declared ≥ 0.30), Nash 0.871 against the
   scripted 0.868.
3. **Letter (a).** Package 0.070 / 0.037, floor5 0.019 / 0.028, all
   under the 0.10 line.
4. **Holds on welfare, with crossings to name.** Package arms' team
   Nash in a gen1-A roster 0.923 on both seeds against the scripted
   0.868; no welfare stop fired. Distress age ≥ 150 in the swap legs,
   one seed of 150 per arm: pkg-s1 seed 870011 at seat 2 (215), pkg-s2
   870019 seat 0 (209), floor5-s1 870007 seat 0 (223), floor5-s2 870006
   seat 2 (250); in the all-arm rosters pkg-s2 870004 seat 2 (177) and
   floor5-s2 870008 seat 2 (192). About 0.7% of swap-leg seeds, under
   F-043's 1.8% swap rate, and tier 1's gen1-A on the same worlds read
   133 and 162.

## Reading

The BC clone is the beam-seeking mind the package was meant to produce:
it starts more naps on beams than its teacher. PPO at the pool's dose
then removes the behaviour as thoroughly as it did for Gen 1, and the
floor-3 reward, which pays about seven ticks a nap for the walk, does
not change that. So the Gen 2 collection can expect the same: whatever
count and lifetime the corpus carries, a β 0.04 fine-tune will not keep
the walk unless something else holds it. The candidates, in the order
Experiments would try them: a tighter leash (dose-hi held 0.21 on Gen
1), a leash that stays tight for the sleep decision only, or a planner
above the mind (tier 3, the owner's word 2026-09-20). The corpus bar on
#390 is moot as a lever on the mind, and the count stays the owner's
visual call.

Not read here: whether PPO loses the walk because it does not pay
(seven ticks a nap against the pile's cuddle drip and the play budget)
or because the leash simply lets it drift; the dose-hi contrast would
say, and is not run.

## Regeneration

```
caffeinate -s nohup bash experiments/beam-world-screen-2026-09-19/stage1.sh > .../results-raw/tier2/stage1.log 2>&1 &
caffeinate -s nohup bash experiments/beam-world-screen-2026-09-19/stage2.sh > .../results-raw/tier2/stage2.log 2>&1 &
caffeinate -s nohup bash experiments/beam-world-screen-2026-09-19/stage3.sh > .../results-raw/tier2/stage3.log 2>&1 &
experiments/exp-006-character-gen/.venv/bin/python experiments/beam-world-screen-2026-09-19/tier2_read.py \
  experiments/beam-world-screen-2026-09-19/results-raw/tier2/battery experiments/beam-world-screen-2026-09-19/results-raw/battery
```
Stage 3 needs the gen1-A artifacts reachable under `CERT_ARTS`
(symlinks `artifacts/ppo-fog-{cand-s2,cand-s1,dose-lo-s1,cand-s4,cand-s7}`
→ `fog-gen1-cert/artifacts/`); the first launch failed without them
(`stage3-first-attempt.log`).

# Tier 3 — results, 2026-09-20

Prereg `PREREG-tier3.md` (c42f308, before the legs). The beam order over
all five Gen 1 minds (`plan:` seats), two worlds, 30 seeds × 20k, served
clock; comparators = tier 1's gen1-A legs on the same worlds and seeds.
Raws `results-raw/tier3/{package,anchor}/`, uncommitted.

## The short version

The order does what it was told at a 91% completion rate and costs the
cat nothing measurable; what it was told covers 9% of naps. Placement
more than doubles on both worlds and misses the declared lines, because
the trigger is a solo nap with a known beam in reach and most of these
minds' naps are cosleeps, which the order never touches.

| | package: gen1-A → with the order | anchor (served): gen1-A → with the order |
|---|---|---|
| naps begun on a beam | 0.068 → **0.153** | 0.046 → **0.112** |
| tick share on a beam | 0.063 → 0.144 | 0.046 → 0.111 |
| roster happiness | 92.32 → 92.25 | 92.49 → 92.39 |
| team Nash | 0.923 → 0.922 | 0.925 → 0.924 |
| sleep share of cat-ticks | 0.135 → 0.132 | 0.130 → 0.128 |
| nap starts under sleep need 5 | 0.28 → 0.30 | 0.42 → 0.41 |
| orders, share of nap starts | 0.091 | 0.072 |
| arrived / stuck / long / gone / emergency | 0.91 / 0.08 / 0.00 / 0.02 / 0.00 | 0.88 / 0.07 / 0.00 / 0.05 / 0.00 |
| forced ticks, share of cat-ticks | 0.012 | 0.010 |
| worst distress age (seeds over 150) | 133 → 183 (870019, Miso's seat) | 49 → 208 (870027, Miso's seat) |

Per seat, package, gen1-A → order: Miso 0.128 → 0.229, Pumpkin 0.014
→ 0.211, Kittybear 0.071 → 0.205, Clementine 0.087 → 0.104, Biscuit
0.014 → 0.028. Anchor: Miso 0.088 → 0.172, Pumpkin 0.008 → 0.147,
Kittybear 0.044 → 0.145, Clementine 0.056 → 0.075, Biscuit 0.009 →
0.019. Per-seat happiness moves 0.01–0.15 down, every seat. Conducted
warmth (asleep off-beam beside a partner on a beam) rises at every seat,
0.012–0.023 → 0.019–0.035 on the package world: more partners now lie
on beams.

The arithmetic closes: on the package world the order fired on 9.1% of
nap starts and arrived on 8.3%, and placement rose by 8.5 points.

## Predictions

1. **Fails on both worlds.** 0.153 against ≥ 0.30, 0.112 against ≥
   0.20. Not the walk: arrivals 91% / 88%, stalls 8% / 7%, no order hit
   the 30-tick limit. The trigger window binds. The seats that nap
   alone (Miso, Pumpkin, Kittybear) tripled; Biscuit, who cosleeps on
   93% of her sleeping polls live, barely moved. The prereg declared
   cosleep out of scope and predicted around the teacher's solo share
   without checking how few of the minds' naps are solo; that is on the
   prereg.
2. **Holds.** Happiness within 0.10, Nash within 0.001, sleep share
   within 0.003, on both worlds.
3. **Holds.** Arrivals 0.91 / 0.88; forced ticks 1.2% / 1.0%.
4. **Holds.** Under-5 share moves 0.02 / 0.01.
5. **Fails as stated, one seed per world.** 870019 at Miso's seat (183)
   on the package world, 870027 at Miso's seat (208) on the anchor,
   where the comparators read 133 and 49. Both at the seat the order
   fires most at. One seed in thirty on each world, the same order as
   tier 1's count-and-lifetime crossings and F-043's swap rate; the
   order's forced walks are the plausible cause (a cat marched away
   from food or a partner for up to 30 ticks), and the emergency
   release at need 60 did not fire once, so it sits too high to catch
   it. Reported, not tuned.

## Reading

A standing order above a frozen mind recovers the part of beam seeking
it is pointed at, completely and at no welfare cost the battery can
see, on the served world as it is. The ceiling is the trigger, not the
executor. The next parameter, if the owner wants the number, is the
trigger's scope: intercepting cosleep starts (walk the pair to a beam,
or walk to a beam and wait for the friend) would reach the majority of
naps, and is a different order with its own give-up rules, declared as
a new tier. The emergency release wants a lower line or a distress
flag as its trigger before any served use.

For the LLM lab seat: this is the executor baseline a model planner is
read against. A planner that emits the same order gains exactly this;
what a model would add is choosing when to emit it, and orders this
hand-written one does not know.

## Regeneration

```
caffeinate -s nohup bash experiments/beam-world-screen-2026-09-19/results-raw/tier3/run.sh > .../results-raw/tier3/run.log 2>&1 &
```
(`run.sh` in the raws: the two harness invocations with all five `plan:` seats, `CERT_ARTS` at this directory's artifacts.)

# Tier 4 — results, 2026-09-20

Prereg `PREREG-tier4.md` (b9b01a1, before the legs). The friend order
(cosleep beside a friend asleep on a beam within 3) over the solo beam
order (reach lowered to 5), release on distress flags; all five gen1-A
seats, two worlds, 30 seeds × 20k. Raws `results-raw/tier4/`,
uncommitted.

## The short version

The friend order fires on 1–2% of nap starts and changes nothing the
battery can see: warm share (on a beam or conducted beside a partner
on one) is tier 3's on both worlds. The precondition binds. At any
moment few friends are asleep on a beam, fewer within three tiles, and
when one is, the mind already chooses to cosleep with it, so the order
confirms a choice more than it changes one. The lower solo reach cost
nothing and bought nothing.

| | package: gen1-A / tier 3 / tier 4 | anchor: gen1-A / tier 3 / tier 4 |
|---|---|---|
| warm share of sleeping ticks | 0.079 / 0.169 / **0.166** | 0.057 / 0.129 / **0.124** |
| placement (naps begun on a beam) | 0.068 / 0.153 / 0.148 | 0.046 / 0.112 / 0.105 |
| conducted share | 0.016 / 0.025 / 0.027 | 0.012 / 0.018 / 0.020 |
| roster happiness | 92.32 / 92.25 / 92.26 | 92.49 / 92.39 / 92.39 |
| team Nash | 0.923 / 0.922 / 0.922 | 0.925 / 0.924 / 0.924 |
| nap starts under sleep need 5 | 0.28 / 0.30 / 0.30 | 0.42 / 0.41 / 0.42 |
| worst distress age | 133 / 183 / **62** | 49 / 208 / **104** |
| friend order: share of starts, arrived / gone | 0.016, 0.80 / 0.20 | 0.011, 0.82 / 0.18 |
| beam order: share of starts, arrived / stuck / gone | 0.083, 0.92 / 0.07 / 0.01 | 0.062, 0.91 / 0.07 / 0.02 |
| forced ticks, share of cat-ticks | 0.011 | 0.009 |

Per seat warm share, package, gen1-A → tier 4: Miso 0.123 → 0.217,
Pumpkin 0.025 → 0.213, Kittybear 0.083 → 0.213, Clementine 0.098 →
0.130, Biscuit 0.037 → 0.064. Tier 3's per-seat numbers sit within
0.01 of each.

## Predictions

1. **Fails.** Warm share 0.166 / 0.124 against ≥ 0.30 / ≥ 0.20; Biscuit
   0.064 against ≥ 0.20. The friend order's opportunity is the bind,
   not its execution (80–82% arrivals, no stalls, the rest a friend who
   woke or left the beam).
2. **Holds.** Happiness within 0.10, Nash within 0.001 of gen1-A; the
   lower solo reach did not recover tier 3's 0.07–0.10 dip.
3. **Holds.** Arrivals 0.80–0.92 per order kind; forced ticks about 1%.
4. **Holds.** Under-5 share within 0.02.
5. **Half holds.** No seed crossed 150 on either world (package worst
   62, anchor 104), which reads tier 3's two crossings as seed variance
   rather than the walks; the flag release never fired, so the "fires
   at least once" clause fails for the good reason that no cat under an
   order reached distress.

## Reading

Two orders above the frozen minds recover about a tenth of sleeping
ticks as beam-rate sleep on the package world and eight points on the
served one, at no measurable welfare cost, and that number is the solo
order's. To reach the cosleeping majority a third precondition is
needed, and the two candidates are different orders: a wider friend
reach (six tiles would roughly quadruple the opportunities; the walk
gets longer and the friend more likely to wake), or the case both
prereg files declared out, walking a pair to a free beam (the partner
does not follow; the order becomes "go to the beam and wait", with a
give-up when the friend does not come). Either is a tier on the
owner's word. Tier 4's solo-reach 5 and the flag release stay as the
planner's pins.

For the LLM lab seat: the executor baseline is tier 3's number; tier 4
adds that a second hand-written order with a rare precondition is
nearly free and nearly inert, which is the case a model planner would
have to earn its keep on.

## Regeneration

```
caffeinate -s nohup bash experiments/beam-world-screen-2026-09-19/results-raw/tier4/run.sh > .../results-raw/tier4/run.log 2>&1 &
```

## Addendum, 2026-09-20: nap lengths (owner's question)

A nap runs `[actions.durations] sleep = { min = 6, max = 12 }`: relief
every tick, and a cleared need ends it early once six ticks have
passed. Read off the tier 1 and tier 4 legs (sleeping snapshots per
nap; the post-apply snapshot counts one fewer than the engine's
duration, so 5.0 here is the six-tick minimum):

| | beam nap | off-beam nap |
|---|---|---|
| scripted teacher, served world | 6 | 6.4 |
| scripted teacher, package world (floor 3) | 6 | 8.4 |
| gen1-A, either world | 6 | 6.0–6.4 |
| gen1-A under the orders (tier 4), either world | 6 | 6.0–6.4 |

Every beam nap is the minimum, and for the minds every nap is the
minimum whatever the tile: they begin naps at a sleep need of 7–9 on
average (tier 1's start-need bins), and six ticks at the off-beam rate
clear 30. The beam's higher rate therefore changes nothing about a
mind's nap, not its length and not its outcome; it pays only to a cat
that sleeps needy, which is the scripted teacher (mean start need 16,
naps to 8.4 ticks under floor 3) and never these minds. That is the
mechanism under F-047's "one tick per nap": for the served minds the
differential is worth zero ticks, and floor 3 moves that only for a cat
whose nap runs past the minimum. It also bounds what any beam order can
buy a frozen mind in welfare: nothing, which is what tiers 3 and 4
measured (happiness within 0.1). A beam matters to a mind that naps
needy, which is a Gen 2 question about when the mind chooses to sleep,
not where.

# Tier 5 — results, 2026-09-20: shallow ground sleep

Prereg `PREREG-tier5.md` (9f24321, before the engine change; floor
worlds 4a57e83 after spec 056 merged at fbd06e0). Comparators and eight
arms on the merged engine (a first staging on a pre-review build was
stopped and parked as `results-raw/tier5-stale-c6b8481/`, nothing from
it cited). Arms plateaued at 9.0 M (six), 10.0 M (sg25-s1) and 11.0 M
(sg15-s2); Part A clean at probe 1 on all eight. Reader `tier5_read.py`
→ `results-raw/tier5/tier5-read.json`; meow rates from
`results-raw/tier5/meow/` (5 seeds × 5k per leg, the harness's new
message counter). Raws uncommitted.

## The short version

Once the tile changes a nap's outcome, beam seeking survives the
fine-tune, at every floor. The package clone that lost everything under
β 0.04 PPO in tier 2 (0.04–0.07 in its seat) keeps 0.46–0.81 of its naps
on beams under shallow ground, more the deeper the floor, and learns
to cosleep beside beam sleepers for conduction on top. A learning mind
pays about 1.5 happiness for any floor; a frozen mind pays 1.4 to 5.2
and spends up to 40% of its ticks in naps that relieve nothing.

## Per floor (package world, 30 seeds × 20k)

| floor | frozen gen1-A: placement / hap / sleep share | arm in its seat: placement s1 / s2 | arm own-seat hap s1 / s2 (gain over frozen mean) | all-arm roster: hap / Nash / sleep / placement / conducted | over 150: frozen ; swap legs (of 150) ; all-arm (of 30) |
|---|---|---|---|---|---|
| 0 (tier 2) | 0.068 / 92.32 / 0.135 | 0.070 / 0.037 | 92.3 / 92.4 | 91.9 / 0.919 / — / 0.067 / — | 0 ; 1, 1 ; 0, 1 |
| 10 | 0.057 / 90.89 / 0.221 | **0.508 / 0.460** | 91.41 / 91.28 (+0.5 / +0.4) | 91.04, 90.93 / 0.910, 0.909 / 0.145, 0.158 / 0.399, 0.396 / 0.114, 0.127 | 2 ; 6, 4 ; 0, 0 |
| 15 | 0.054 / 89.81 / 0.285 | **0.443 / 0.724** | 90.91 / 91.30 (+1.1 / +1.5) | 90.86, 91.13 / 0.908, 0.911 / 0.172, 0.133 / 0.355, 0.579 / 0.246, 0.190 | 0 ; 6, 5 ; 3, 4 |
| 20 | 0.044 / 88.55 / 0.347 | **0.686 / 0.502** | 90.85 / 90.75 (+2.3 / +2.2) | 90.61, 90.71 / 0.905, 0.906 / 0.135, 0.137 / 0.468, 0.414 / 0.257, 0.217 | 0 ; 10, 10 ; 1, 1 |
| 25 | 0.037 / 87.15 / 0.399 | **0.808 / 0.649** | 90.88 / 90.70 (+3.7 / +3.6) | 90.90, 90.55 / 0.908, 0.905 / 0.097, 0.162 / 0.606, 0.497 / 0.262, 0.259 | 1 ; 15, 13 ; 0, 0 |

The teacher's placement on the same floor worlds: 0.395 / 0.341 /
0.272 / 0.249 (floor 0: 0.458). It falls because the scripted sleep
rule does not read the floor: the teacher naps on the spot when no
beam is within reach and those naps now relieve nothing, so it naps
again, and the extra ground naps dilute its placement (its sleep share
0.088 → 0.163).

Probe trajectories (same network in all seats, 2k ticks × 3 seeds):
every arm held 0.32–0.62 through 2.5–4.6 M ticks, the stretch where
tier 2's arms fell to 0.13–0.19, and the plateau values order by floor
(10: 0.37–0.39, 15: 0.44–0.59, 20: 0.45–0.52, 25: 0.52–0.63).

Nap lengths stay at the six-tick minimum on and off beams at every
floor, for teacher, frozen minds and arms alike: under spec 056's
early-end rule a ground nap finishes at the floor. What moves is the
need at nap start (frozen minds 8.8 → 12.9 / 16.3 / 20.4 / 24.8; arms
9.5–13.2) and, for the frozen minds, the nap count.

## Meows (5 seeds × 5k, per 1k cat-ticks, policy seats)

| | want_sleep | here_sunbeam | all wants | any speech |
|---|---|---|---|---|
| gen1-A floor 0 | 2.1 | 27.8 | 22.0 | 302.8 |
| gen1-A floor 10 / 15 / 20 / 25 | 7.5 / 44.3 / 57.5 / 63.0 | 43.2 / 64.8 / 60.5 / 57.5 | 30.8 / 73.6 / 93.0 / 97.4 | 352 / 416 / 449 / 452 |
| arms (all-arm), floor 10 / 15 / 20 / 25 | 6.2 / 10.6 / 13.9 / 13.9 | 51.1 / 62.1 / 67.3 / 65.7 | 33.5 / 38.6 / 40.6 / 42.4 | 244 / 234 / 245 / 237 |

A frozen mind under a floor is armed for `want_sleep` most of the time
from floor 15 up (the need spends its time above the announce line
between useless naps); a mind that sleeps on beams asks four to five
times less. `here_sunbeam` replies double for everyone, since beams are
asked about more.

## Predictions

1. **Holds on the cost, fails on the mechanism.** The frozen roster's
   happiness drops 1.4 / 2.5 / 3.8 / 5.2, well past 0.3 at every floor,
   with sleep share up to 0.40 and need at nap start rising with the
   floor. The predicted longer off-beam naps did not happen: the
   early-end rule ends a ground nap at the floor, so naps stay at the
   minimum and the cost arrives as more naps, not longer ones.
2. **Holds at 20 and 25, and at 10 and 15 too.** Own-seat placement
   0.51 / 0.46 (10), 0.44 / 0.72 (15), 0.69 / 0.50 (20), 0.81 / 0.65
   (25), all above the 0.15 line. The floor-10 clause, "under 0.10
   like tier 2", fails in the good direction: even a floor under the
   minds' own start need is enough once the need climbs to it between
   naps.
3. **Holds on direction, fails on size.** Every arm is happier in its
   seat than the frozen roster's mean on the same floor (+0.4 to +3.7)
   with Nash above; the arms recover 30–70% of the floor's cost, not
   all of it. An all-arm roster sits at 90.5–91.1 on every floor
   against 92.3 at floor 0: about 1.5 happiness is the price of shallow
   ground to a mind that has learned it, flat across floors.
4. **Holds in shape, off in place.** `want_sleep` rises with the floor
   and jumps between 10 and 15 rather than 15 and 20 (the need spends
   time above the announce line before the floor reaches it).
5. **Farming: holds. Distress: reported.** Nap starts under need 5 fall
   from 0.28 to 0.02–0.05. Swap-leg crossings run 3–10% of seed-legs,
   rising with the floor, almost all at the frozen seats beside the arm
   (Miso's, Biscuit's, Kittybear's), F-043's mixed-roster tail under a
   law those minds never learned; all-arm rosters cross 0 / 3–4 / 1 / 0
   times in 30 at floors 10 / 15 / 20 / 25, with floor 15's pair the
   only ones above the floor-0 comparator.

## Decision rules, applied

- **The finding stands**: the beam matters to a mind once the tile
  changes the nap's outcome, and the Gen 2 world gets a floor. Which
  floor is the owner's. Read against predictions 1, 3 and 4: the
  learning mind's cost is flat across floors (about 1.5), placement and
  warm sleep rise with the floor, the all-arm distress tail does not
  rise with it, and `want_sleep` for a roster that sleeps on beams
  stays under 15 per 1k at every floor. Experiments' lean was 25, with
  20 as the conservative pick. **Owner ruled 15 (2026-09-20, #390)**:
  the aim is a floor that ensures beam behaviour and marks a bend point
  for future minds, not one that maximises it; 15 and 20 read the same
  on placement and learned-mind cost, and 15 keeps the floor clear of
  the announce line (arm 20, disarm 15) so a naive mind's `want_sleep`
  cycles instead of saturating.
- **The teacher needs the law before the Gen 2 re-record.** Under a
  floor the scripted `needs_driven` naps on the spot into nothing; its
  sleep rule has to know that a ground nap under the floor is worth
  nothing (walk to a beam within reach, or do something else), or the
  corpus teaches the loop the frozen minds show. A Product spec, small,
  before the Gen 2 collection; flagged on the shelf.
- **Nothing deploys.** The served world keeps floor 0; the Gen 1 minds
  under a floor are the frozen column above.

## Regeneration

```
caffeinate -s nohup bash experiments/beam-world-screen-2026-09-19/stage5.sh > .../results-raw/tier5/stage5.log 2>&1 &
experiments/exp-006-character-gen/.venv/bin/python experiments/beam-world-screen-2026-09-19/tier5_read.py \
  experiments/beam-world-screen-2026-09-19/results-raw/tier5/battery experiments/beam-world-screen-2026-09-19/results-raw/battery --out .../tier5-read.json
```
Meow legs: the harness with `--seeds 5 --ticks 5000` on each floor world for gen1-A and each arm's all-arm seating (`results-raw/tier5/meow/`).

# Tier 6 — results, 2026-09-21: beam count 5 / 6 / 7 / 8 under floor 15

Prereg `PREREG-tier6.md` (7d3b1d8, before any leg). Count worlds
`count-{5,7,8}.toml` derived from the floor-15 package world (count 6
is tier 5's `shallow-15`, its arms sg15-s1 / s2 reused as trained).
Six new arms plateaued at 8.0 M (cnt7-s1), 9.0 M (four) and 10.0 M
(cnt8-s2). Reader `tier6_read.py` → `results-raw/tier6/tier6-read.json`;
meow rates from `results-raw/tier6/meow/`; the distress inspection
from `distress_inspect.py` (`results-raw/tier6/distress-inspect-cnt7-s1.txt`).
Raws uncommitted.

## The short version

For a mind that has learned the floor, count is flat from six beams up
and costs about 0.6 happiness at five. Frozen minds do not feel it
(span 0.14 over the four worlds). Beam seeking holds at every count
(own-seat placement 0.44–0.72), and the count-6 arms dropped onto the
5, 7 and 8 worlds without retraining are never worse than the arms
retrained there, so the count can move at the Gen 2 collection without
a new screen. The one distress flag (cnt7-s1, a 3,015-tick episode) is
one seed's drink fault at Biscuit's seat, not the count.

## Per count (30 seeds × 20k, served clock)

| count | teacher: placement / hap | frozen gen1-A: placement / hap / sleep share | arm in its seat: placement s1 / s2 | arm own-seat hap s1 / s2 (gain over frozen) | all-arm roster: hap / Nash / placement / conducted | over 150: frozen ; swap legs (of 150) ; all-arm (of 30) |
|---|---|---|---|---|---|---|
| 5 | 0.289 / 86.11 | 0.047 / 89.77 / 0.292 | **0.477 / 0.520** | 90.88 / 91.16 (+1.1 / +1.4) | 89.78, 90.92 / 0.897, 0.909 / 0.359, 0.431 / 0.167, 0.148 | 0 ; 1, 9 ; 4, 1 |
| 6 (tier 5) | 0.341 / 86.18 | 0.054 / 89.81 / 0.285 | **0.443 / 0.724** | 90.91 / 91.30 (+1.1 / +1.5) | 90.86, 91.13 / 0.908, 0.911 / 0.355, 0.579 / 0.246, 0.190 | 0 ; 6, 5 ; 3, 4 |
| 7 | 0.399 / 86.37 | 0.061 / 89.85 / 0.279 | **0.601 / 0.570** | 91.04 / 91.04 (+1.2 / +1.2) | 90.58, 90.66 / 0.905, 0.906 / 0.468, 0.451 / 0.235, 0.215 | 1 ; 13, 10 ; 16, 3 |
| 8 | 0.442 / 86.48 | 0.070 / 89.90 / 0.272 | **0.617 / 0.573** | 91.19 / 91.48 (+1.3 / +1.6) | 90.81, 91.30 / 0.907, 0.912 / 0.471, 0.449 / 0.225, 0.193 | 4 ; 7, 5 ; 7, 0 |

All-arm happiness by seed pair: 89.78 / 90.92 at five, then 90.86 /
91.13, 90.58 / 90.66, 90.81 / 91.30. The seed spread at five (1.14) is
one weak arm, cnt5-s1; from six up the eight numbers sit inside 0.75 of
each other and no count orders on both seeds (7 sits under 6 on both,
8 over 7 on both). Against the floor-0 all-arm level (91.9–92.3) the
floored minds pay about 0.6–1.7 at six to eight beams and about 2.1
(cnt5-s1) to 1.0 (cnt5-s2) at five. Nash follows happiness at every
cell.

The teacher's placement rises with count (0.29 → 0.44) at flat
happiness, tier 1's reach-gated walk under the floor; its happiness is
86.1–86.5 at every count because its sleep rule still naps on the spot
into nothing (tier 5). The frozen roster's placement rises 0.047 →
0.070 and nothing else moves.

**Transfer.** The count-6 arms seated all-arm on the 5 / 7 / 8 worlds,
happiness (placement) against the arms retrained there:

| world | sg15-s1: transfer vs retrained s1 | sg15-s2: transfer vs retrained s2 |
|---|---|---|
| count 5 | 90.57 vs 89.78 (0.284 vs 0.359) | 91.06 vs 90.92 (0.539 vs 0.431) |
| count 7 | 90.93 vs 90.58 (0.394 vs 0.468) | 91.23 vs 90.66 (0.604 vs 0.451) |
| count 8 | 91.02 vs 90.81 (0.425 vs 0.471) | 91.29 vs 91.30 (0.629 vs 0.449) |

The transferred arm is happier than the retrained one in five cells of
six and level in the sixth (−0.01). Placement moves with the arm, not
the world: sg15-s1 keeps its 0.28–0.43 and sg15-s2 its 0.54–0.63 on
every count.

## The cnt7-s1 distress flag

Sixteen all-arm seeds over the 150-tick line at count 7 on cnt7-s1
(three on cnt7-s2; 0–7 elsewhere), the longest 3,015 ticks. Re-running
the three longest seeds with the state traced: every long streak is
**drink**, at Biscuit's seat (seat 1) and at Miso's. On seed 870015 the
cnt7-s1 mind in Biscuit's seat holds drink at 100 from tick 7,838 to
10,853, idle for 2,189 of those ticks, sleeping 249, grooming 240,
playing 135, and never drinking; happiness falls from 65 to 40 and
recovers only when the streak ends. The same mind in its seat-1 swap
leg crosses on 9 of 30 seeds (max 749) while its other four seats
cross on 0–1, and cnt7-s2 all-arm on the same world crosses once at that seat.
So the flag is one PPO seed under-serving drink at Biscuit's seat, a
mind property, and the count-7 all-arm numbers carry it (its all-arm
Biscuit-seat happiness 86.9 against 87.3–88.0 for the other arms). Seat
2's eleven crossings in the same all-arm leg do not appear in cnt7-s1's
seat-2 swap leg (0), a roster interaction of five such minds. The beam law is not
involved.

## Nap starts under need 5 (rule 4 read), and a correction to tier 5

The all-arm rosters start 0.16 (count 5) to 0.32–0.33 (counts 6–8) of
their naps with sleep need under 5; the arms alone in their swap seats
0.14–0.32 (cnt5 0.16 / 0.14, sg15 0.18 / 0.32, cnt7 0.30 / 0.26, cnt8
0.30 / 0.21); the frozen roster 0.008–0.012 at every count; the
floor-0 frozen roster 0.28 (F-047's beam-sitting). Tier 5's "0.02–0.05"
under prediction 5 was the swap-leg roster pooled over five seats,
four of them frozen at 0.01; the arm's own share at floor 15 is
0.18 / 0.32, and the correction is recorded here. What these naps are,
from one seed each of cnt7-s1, cnt5-s1 and sg15-s2 all-arm with every
nap start cross-tabbed (`lowneed-crosstab.txt`): about three fifths on
a beam (solo 0.07–0.19 of all starts, partnered 0.02–0.07) and two
fifths a cosleep join on the ground (0.05–0.11); a solo ground nap
under need 5 happens 0–1 times in 2,700–2,900 starts. A learned mind
under the floor naps early only where the tile or a partner pays,
which is the law working, and whether the beam half is warmth farming
in rule 4's sense is a Gen 2 read on the corpus, not a count question:
the share does not order with count.

## Meows (5 seeds × 5k, per 1k cat-ticks, policy seats)

| | want_sleep | here_sunbeam | all wants | any speech |
|---|---|---|---|---|
| gen1-A, count 5 / 6 / 7 / 8 | 47.0 / 44.3 / 42.9 / 41.2 | 53.1 / 64.8 / 71.9 / 76.9 | 76.1 / 73.6 / 72.0 / 69.2 | 415 / 416 / 415 / 418 |
| arms all-arm s1, count 5 / 6 / 7 / 8 | 16.5 / 10.5 / 10.4 / 10.6 | 56.7 / 61.1 / 62.5 / 65.0 | 45.6 / 38.5 / 40.2 / 39.2 | 279 / 237 / 280 / 259 |
| arms all-arm s2, count 5 / 6 / 7 / 8 | 15.2 / 10.7 / 8.4 / 10.6 | 59.9 / 63.0 / 66.0 / 66.8 | 42.1 / 38.6 / 35.3 / 34.6 | 270 / 231 / 257 / 236 |

`here_sunbeam` rises with count for everyone (more beams to name).
`want_sleep` for the learned rosters is flat at 8–11 from six beams up
and 15–17 at five, the same shape as happiness; the frozen roster asks
for sleep 41–47 times per 1k at every count.

## Predictions

1. **Fails as an ordering, holds as a shape.** All-arm happiness does
   not order 5 < 6 < 7 < 8 on both seeds (7 under 6 on both, 8 over 7
   on both, 6–8 inside 0.75). The 5→6 gain (0.64, seed means) exceeds
   the 7→8 gain (0.44); count 8 sits within 1.0 of the floor-0 level on
   its better seed and count 5 more than 1.5 under it on its worse.
   Nash tracks happiness. The curve is a step at six, then flat.
2. **Holds.** Frozen happiness spans 0.14 across the four worlds;
   teacher placement rises 0.29 → 0.44 at flat happiness.
3. **Holds on placement, fails on the orderings.** Own-seat placement
   0.44–0.72 on every seed at every count, all past 0.15. All-arm
   placement does not order with count (0.36 / 0.43, 0.36 / 0.58,
   0.47 / 0.45, 0.47 / 0.45), and conducted share does not fall with it
   (0.17 / 0.15, 0.25 / 0.19, 0.24 / 0.22, 0.23 / 0.19): both are seed
   properties.
4. **Fails as declared, in the transfer's favour.** The rule was
   two-sided (within 0.5 happiness and 0.10 placement) and four cells
   of six leave the band: +0.78 and +0.57 happiness, and placement
   +0.11 / +0.15 / +0.18 on the sg15-s2 side. No cell is worse than
   −0.01. Rule 9 did not bite: count changes what the policy sees, not
   what an action is worth.
5. **Farming: no movement with count; the level is reported above.
   Distress: reported, one flag explained.** Start-need bins do not
   move down with count (0.16 at five, 0.32–0.33 from six). Crossings
   by name are in the table; only cnt7-s1's order with anything, and
   that is drink at one seat.

## Decision rules, applied

- **The count is the owner's (#390 (c)).** By the declared line rule,
  the smallest count whose gain to the next sits inside its own
  two-seed spread, the line is **5**: the 5→6 gain (0.64) is inside the
  spread at five (1.14), and that spread is cnt5-s1's weak seed. Read
  past the rule, the curve says a learned mind pays for five beams and
  gains nothing measurable from seven or eight over six. Experiments'
  offer is **6**: the package world as it stands, with the count-6 arms
  and tier 5's numbers intact. The transfer read makes 7 or 8 a free
  move later; the case for it is the teacher's corpus placement (0.34
  at six, 0.40 at seven, 0.44 at eight against the shelf's ~0.4 bar),
  which the sleep-rule spec should lift first. **Owner ruled 6
  (2026-09-21, #390: "6 beams")**, and sent the teacher sleep-rule
  spec to Product the same day (`HANDOVER-product-2026-09-21.md`).
- **Prediction 4 holding in substance means the count can move at the
  Gen 2 collection without a new screen**; a mind trained at one count
  reads the others. Recorded as F-051.
- **Nothing deploys.** The served world keeps floor 0 and its count.

## Regeneration

```
caffeinate -s nohup bash experiments/beam-world-screen-2026-09-19/stage6.sh > .../results-raw/tier6/stage6.log 2>&1 &
experiments/exp-006-character-gen/.venv/bin/python experiments/beam-world-screen-2026-09-19/tier6_read.py \
  experiments/beam-world-screen-2026-09-19/results-raw/tier6/battery experiments/beam-world-screen-2026-09-19/results-raw/tier5/battery --out .../tier6-read.json
bash experiments/beam-world-screen-2026-09-19/results-raw/tier6/meow/run.sh
CERT_ARTS=<arts> .../distress_inspect.py experiments/beam-world-screen-2026-09-19/count-7.toml 870015 --seat 0=ppo:cnt7-s1 ... --seat 4=ppo:cnt7-s1
```

# Spec 057 acceptance read, 2026-09-22: the teacher's sleep rule reads the floor

Product's branch `057-teacher-sleep-floor` at d850df8 (not merged; the
owner reviews after this read), against main at 705290d. The branch's
binding was built into a throwaway venv; the lab venv stays on main.
Scripted comparator legs through `cert_harness_fog.py scripted eval`
(30 × 20k, served clock) on both bindings, and the nap cross-tab
`teacher_nap_crosstab.py` (10 seeds × 20k) on both. Raws
`results-raw/spec057-d850df8/` (uncommitted).

| measure, teacher on the floor-15 package world (count 6) | main 705290d | branch d850df8 | package world at floor 0 |
|---|---|---|---|
| naps begun on a beam (placement) | 0.341 | **0.606** | 0.458 |
| ticks asleep on a beam | 0.333 | 0.583 | 0.365 |
| conducted cosleep share | 0.050 | 0.094 | — |
| sleep share of ticks | 0.118 | **0.078** | 0.088 |
| nap starts (30 seeds) | 68,547 | 44,669 | — |
| mean sleep need at nap start | 18.5 | 19.9 | 17.8 |
| happiness (per-seed range) | 86.18 (85.84–86.55) | 86.62 (86.32–87.03) | 86.90 |
| Nash | 0.860 | 0.865 | 0.868 |
| max distress age; seeds over 150 | 134; 0 | 138; 0 | 93; 0 |

Nap starts by need and warmth, 10 seeds (`crosstab-main.jsonl`,
`crosstab-057.jsonl`), share of all starts:

| | need ≤ 15, ground, solo | need ≤ 15, ground, partner | need ≤ 15, beam | need > 15, ground solo | need > 15, ground partner | need > 15, beam |
|---|---|---|---|---|---|---|
| main | **0.045 (1,019)** | 0.036 | 0.145 | 0.260 | 0.317 | 0.197 |
| branch | **0.000 (1)** | 0.054 | 0.251 | 0.054 | 0.282 | 0.359 |

## Against the handover's acceptance list

- **Floor 0 byte-identical: holds.** The all-scripted leg on
  `anchor-b3.toml` (the served world) gives 30 of 30 rows identical
  between the two bindings, every field. (Tier 5's shallow-15 rows
  differ from a fresh main run only by the later `msg` key; the
  dynamics are unchanged.)
- **The loop is gone: holds.** Naps begun at or under the floor with no
  beam underfoot and no partner fall from 1,019 to 1 in 10 seeds. The
  one is on seed 870003 and is most likely the post-apply read: a nap
  begun a fraction above the floor relieves to the floor in its first
  tick and the state then reads need = 15.0 (inferred from the layout,
  not traced). Sleep share falls 0.118 → 0.078, under the package
  world's floor-0 value; nap starts fall by a third; the need at nap
  start rises to 19.9 and the 20–40 bin takes 0.45 of starts (0.31
  before). Solo ground naps above the floor fall 0.26 → 0.05: the
  teacher now waits for a beam, a partner, or a need worth a ground nap.
- **Welfare not worse: holds.** Happiness +0.44, Nash +0.005, no seed
  over the distress line on either binding. The branch's per-seed range
  sits above main's, so "within the seed spread" is exceeded in the
  good direction.
- **Placement, reported**: 0.341 → 0.606, past the shelf's ~0.4 corpus
  bar and past the floor-0 package world's 0.458. The bar itself is
  read on the recorded corpus, not here.
- **Mutate reds**: Product reports three on the branch (raw-need term,
  gate disabled, warm predicate always true), predictions declared
  first. Not re-run here. The cross-tab instrument has its own live
  guard in `test_distress_inspect.py` (starts and sleep share equal the
  harness's on the same leg) with a red on the start definition.

Product's two fixture traps (the potter gate wanders 40% of ticks
under pressure 20, so the no-nap rule is partly stochastic at floor 15;
a world with no beam known takes the exploration rung) are consistent
with the read: the cross-tab shows the rule holding at the population
level on the real world, which is what the corpus records.

## What this changes downstream

The Gen 2 re-record can proceed on the merged rule with the floor-15
count-6 package world as ruled. The teacher's placement under the floor
is now higher than at floor 0, so the corpus read's ~0.4 bar is
expected to clear with margin; the here-word density pins (F-034, A1b)
still need their re-check on the new corpus, since `here_sunbeam` rises
with beam use. Regeneration:

```
# branch binding into a scratch venv, from <worktree>/crates/cloudkitty-py:
VIRTUAL_ENV=<venv> PATH=<venv>/bin:$PATH maturin develop --release
<venv>/bin/python experiments/fog-gen1-cert/cert_harness_fog.py scripted eval --config experiments/beam-world-screen-2026-09-19/shallow-15.toml --workers 6 --out-dir .../spec057-d850df8/shallow-15
<venv>/bin/python experiments/fog-gen1-cert/cert_harness_fog.py scripted eval --config experiments/fog-gen1-cert/anchor-b3.toml --workers 6 --out-dir .../spec057-d850df8/floor0
<venv>/bin/python experiments/beam-world-screen-2026-09-19/teacher_nap_crosstab.py experiments/beam-world-screen-2026-09-19/shallow-15.toml 870001 10
```

## Addendum, 2026-09-22: the partnered cell, on the round-2 head (02d4c46)

Product's round-2 review (PR #409) found that the cross-tab surfaced
only the solo cell, while a surviving loop variant would live in the
partnered one: with cuddle above `cuddle_real_threshold` and an awake
friend adjacent, the spec-028 cosleep route fires before any warm
check and the nap lands off-beam at floored relief. The instrument
now splits a partnered ground nap by the partner's tile (beside a
partner on a beam it conducts, spec 031) and counts, for ground
cosleeps beside a ground partner, how many had a beam within Chebyshev
8 (an upper bound on the priced reach). Re-run on both bindings, 10
seeds × 20k (`crosstab-{main,02d4c46}-reach.jsonl`); the round-2 head
reproduces d850df8's dynamics on this world exactly (14,801 starts,
same cells).

| ground cosleep beside a ground partner | main | 02d4c46 |
|---|---|---|
| at or under the floor (the loop variant) | 299 (295 with a beam within 8) | **2** (2) |
| above the floor (floored relief, need − 15) | 6,262 (6,053) | 2,909 (2,907) |
| beside a partner on a beam, at or under the floor (conducts) | 531 | 804 |

So the variant is 2 naps in 14,801 starts at the floor. Above the
floor the 028 route is a fifth of all naps, nearly always with a beam
within eight tiles, each relieving to the floor rather than clearing,
and paying cuddle. Whether that route should read the floor is the
owner's call on #409; this table is the input. The reach flag is a
reported count with no guard of its own; the instrument's guard covers
starts and sleep share.
