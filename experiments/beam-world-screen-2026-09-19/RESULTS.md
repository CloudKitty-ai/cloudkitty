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
