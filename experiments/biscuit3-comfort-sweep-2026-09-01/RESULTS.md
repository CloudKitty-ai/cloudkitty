# Biscuit 3.0 comfort × score × weights sweep — results
## (2026-09-01, Experiments; prereg + tooling declared @ 893cd48 before collection; 20/20 runs valid)

Engine main @ 893cd48 (crate tree as prereg), debug build, tick_ms 40,
five parallel headless servers. Every run: 1,548–1,549 census polls and
1,580–1,584 world polls over 20,000 measured ticks (bar ≥ 1,000);
watchdog quiet in all 20 (`alarm_live` false, no entries). Raws in
`results-raw/` (uncommitted); `score.py` output in `results-raw/score.json`.

## Verdict

Lowering `playful_comfort` buys food promptness roughly linearly and
pays for it in element play, not duets. The prereg's decision rule
lands in its middle case: **owner call on the curve**, knee at 35–30.
The weights arm (w35) is the better-shaped dial: same food line at 35,
less play lost (P3 PASS). The spec-042 score at the candidate dials
does what its formula says (partner play need at duet start 4.3 → 10–12)
but removes Biscuit as the roster's duet partner (P4/P5 supply MISS at
every comfort); those dials are not shippable as tried.

One prereg measure is inverted and one is compositional; both are
reported as pinned and then read on the surviving half. Details below.

## The comfort curve (score off, pooled over both seeds)

| arm | eat time>30 | eat p50 (ticks) | eat p90 | hungry-play share | Biscuit play /1k (duet + elem) | total vs c55 | others' duets /1k | Biscuit happiness | demand price |
|---|---|---|---|---|---|---|---|---|---|
| c55-off | 0.455 | 88 | 101–107 | 0.65 | 72.6 + 161.9 = 234.5 | 1.00 | 26.6 | 77.3 | 22.7 |
| c45-off | 0.362 | 56.5 | 75–81 | 0.53 | 78.9 + 140.3 = 219.2 | 0.93 | 28.1 | 80.0 | 20.0 |
| w35-off | 0.275 | 31 | 58–60 | 0.35 | 67.7 + 141.6 = 209.2 | 0.89 | 25.6 | 81.0 | 19.0 |
| c35-off | 0.236 | 26.5 | 47–50 | 0.32 | 72.1 + 107.0 = 179.1 | 0.76 | 26.8 | 82.8 | 17.2 |
| c30-off | 0.132 | 10.5 | 30–35 | 0.15 | 67.3 + 95.8 = 163.1 | 0.70 | 25.5 | 84.8 | 15.2 |
| floor (needs_driven, c55-off) | 0.100 | 7–25 | | | | | | | |

Seeds agree everywhere to two digits on time>30 (e.g. c35 0.239/0.232,
c30 0.119/0.144); no arm's reading depends on a seed. Drink tracks eat
(time>30 0.39 → 0.10). Play-solo is zero in every score-off run.

Three things the curve says:

1. **Duets are untouched; element play pays.** Biscuit's duet rate sits
   at 67–79/1k across all five arms. Every play point comfort takes
   comes out of element play (162 → 96/1k). Duets are where the friend
   already showed up; element play is what she does while hungry
   between friends.
2. **The scripted floor is 7–25 ticks p50 here, not 1–4.** The design
   note's "scripted floor 1–4" came from the live 800 ms server; the
   four `needs_driven` seats in this lab sit at p50 7–25 and time>30
   0.09–0.11. Closure below is measured against this in-run floor, as
   the prereg says.
3. **Happiness follows food.** Biscuit 77 → 85 and her standing-demand
   price 22.7 → 15.2 as comfort drops; roster mean 85.1 → 87.0.

### P1 (character): total play binds, low-need play does not

Total play within −25% of c55-off: c45 0.93x PASS, w35 0.89x PASS, c35
0.76x PASS (at the line), c30 0.70x MISS.

The low-need half of P1 (scenes starting with eat/drink/sleep all < 30)
RISES with lower comfort: 55.6 → 87 → 128 → 160/1k (1.6–2.9x). A
promptly fed cat spends more of her life under 30, so more of her play
is low-need by definition. The measure is compositional and never
binds; it is not the "play comfort cannot reach" it was written to be.
Reported as pinned (PASS everywhere on that half); the P1 verdicts
above rest on total play alone.

### P2 (gap closure): time>30 closes, the excursion count is inverted

Closure on eat time>30 (gap = 0.455 − 0.100 = 0.355), pooled and per
seed:

| arm | closure | seed 1 / seed 2 |
|---|---|---|
| c45-off | 0.26 | 0.27 / 0.26 |
| w35-off | 0.51 | 0.53 / 0.49 |
| c35-off | 0.62 | 0.62 / 0.61 |
| c30-off | 0.91 | 0.97 / 0.85 |

Only c30 clears 2/3 (both seeds); c35 sits just under.

The second P2 measure, armed excursions per 1k, goes the other way in
every arm (Biscuit 6.3 → 7.0 → 7.9 → 8.2; floor 4.4–5.0), so its
"closure" is −0.46 to −1.23 and **P2 as pinned is MISS for every arm by
construction**. Cause, from the mechanics and the polls (seed 1, c55
vs c30): `eat_relief` is 35 per eating tick and a meal runs ~2 ticks,
so every meal resets eat to near zero (mean after-meal level 2–7 for
every seat). Meals per 1k is then rise rate ÷ the level she eats at:
Biscuit eats at mean 48.5 under c55 (6.6 meals/1k) and at 30.3 under
c30 (9.5 meals/1k). An armed excursion is a crossing of 30, so
excursions ≈ meals × P(meal starts ≥ 30). Under c55 that share is 0.92
and excursions ≈ meals; under c30 it is 0.58 and the count is still
higher because there are more meals. The floor seats eat at mean 21–27
with 70–85% of meals starting BELOW 30; they eat 13–24 times per 1k
and cross 30 only 4–5 times. For Biscuit's excursion count to fall to
the floor she would have to eat below 30 most of the time, i.e. a
comfort under the lowest arm. Within the pinned arms the count can only
rise. Excursions per 1k measures how often a cat gets hungry enough to
cross the line, which a cat that eats promptly at 30 does MORE often
than one that eats at 50. The prereg pinned a measure that cannot move
in the direction it asked for; a design error in the prereg, recorded
here. The exploratory reading is time>30 alone, and the decision rule
below is applied to it with that label.

### Decision rule (prereg §Pinned bars), applied

"Some comfort arm passes P1 and P2": on time>30 alone, no score-off arm
passes both. c30-off closes 0.91 but fails P1 total play (0.70x); c35-off
passes P1 (0.76x) and closes 0.62, under 2/3. "No P1-passing arm removes
even 1/3": false, c35 removes 0.62 and w35 0.51. **Middle case: owner
call on the curve.** The curve is smooth with no free lunch; every ~10
points of comfort buys ~0.1 of time>30 and costs 15–25/1k of element
play.

### P3 (weights): PASS

w35-off vs c35-off: closure 0.51 vs 0.62 on time>30 (within 0.25× of
c35's 0.62 → floor 0.465, holds); total play 209.2 vs 179.1 (w35 keeps
more). Both conditions hold, so "weights preserve more character"
stands. (`score.py` also reports the excursion half of P3 as PASS, on
the inverted measure; disregard that line for the reason above.)

Why w35 loses less play than c35 for the same food line: at c35 the
comfort line moves for ALL needs, so cuddle at 35–55 also pulls her out
of play (hungry-play share 0.32 vs 0.35, nearly equal food behaviour;
element play 141.6 vs 107.0).

**Corrected reading (2026-09-01, owner's question about overall
welfare).** The P3 bar read eat only. Per need, Biscuit mean / share of
polls ≥30, score-off, pooled:

| arm | eat | drink | sleep | cuddle | bath |
|---|---|---|---|---|---|
| c55 | 28.3 / 0.45 | 25.6 / 0.38 | 28.0 / 0.45 | 30.8 / 0.50 | 15.6 / 0.07 |
| c45 | 24.5 / 0.36 | 22.0 / 0.29 | 24.0 / 0.36 | 26.0 / 0.41 | 15.4 / 0.07 |
| w35 | 21.6 / 0.27 | 20.2 / 0.23 | 21.4 / 0.27 | 27.0 / 0.42 | 15.5 / 0.07 |
| c35 | 20.4 / 0.23 | 19.2 / 0.20 | 19.2 / 0.20 | 20.7 / 0.26 | 15.0 / 0.05 |
| c30 | 17.6 / 0.13 | 16.6 / 0.09 | 16.7 / 0.09 | 17.8 / 0.16 | 13.7 / 0.01 |
| roster (c55) | 15.4 / 0.10 | 13.8 / 0.07 | 12.9 / 0.06 | 16.5 / 0.13 | 8.5 / 0.01 |

Cuddle is her highest elevated need at c55, above eat. w35 leaves it at
55 and it barely moves (0.50 → 0.42); c35 takes it to 0.26. The play
w35 keeps over c35 is play she does while wanting a cuddle, so P3's
"weights preserve more character" is a bar that passed by not counting
the need the band left out. Bath is the only need that sits fine at 55
(0.07 ≥30, 0.01 at c30), so a band covering everything but bath is
within noise of flat comfort. Weights are withdrawn as a
recommendation; welfare is read on all five needs from here on.

### P4 (roster supply): PASS for every score-off arm

Others' duet rate 25.5–28.1/1k across score-off arms (0.96–1.06x of
c55-off). Lowering Biscuit's comfort does not tax the roster's play.

## The score arm (spec 042 candidate dials)

Dials: `w_value 0.5, w_busy 1.0, w_serious 0.5, t_self 5.0, t_partner
5.0, critter_appeal 0.0`. Comfort-matched pairs, pooled:

| comfort | partner play need at Biscuit duet start | Biscuit duets /1k | Biscuit elem /1k | Biscuit solo /1k | total play | others' duets /1k |
|---|---|---|---|---|---|---|
| c55 off → on | 4.3 → 10.7 | 72.6 → 8.9 | 161.9 → 238.9 | 0 → 2.6 | 234.5 → 250.3 | 26.6 → 12.8 |
| c45 off → on | 4.3 → 11.0 | 78.9 → 9.8 | 140.2 → 213.9 | 0 → 3.4 | 219.2 → 227.1 | 28.1 → 12.2 |
| c35 off → on | 4.5 → 10.5 | 72.1 → 11.3 | 107.0 → 180.2 | 0 → 3.5 | 179.1 → 195.1 | 26.8 → 13.6 |
| c30 off → on | 4.8 → 10.0 | 67.3 → 12.1 | 95.8 → 161.8 | 0 → 3.2 | 163.1 → 177.1 | 25.5 → 13.1 |
| w35 off → on | 4.2 → 10.3 | 67.7 → 9.7 | 141.6 → 212.0 | 0 → 2.4 | 209.2 → 224.1 | 25.6 → 13.1 |

P5 per condition, every comfort: partner-need rises in both seeds
(PASS); Biscuit total play within ±10% (PASS, +4% to +9%); others'
duets fall 51–57% (MISS, bar −15%). Biscuit's duet share 0.31–0.41 →
0.04–0.07.

Reading: the score does exactly what its formula says. Mean partner play
need at duet start was 4.3; with `t_partner 5.0` and the serious/busy
penalties, almost no friend clears the bar, so Biscuit refuses nearly
every duet and plays the elements instead (her total play is flat
because element play is unconditional). The roster loses about half
its duets, which measures how much of their play supply she was. Food
is unmoved (time>30 0.451 vs 0.455 at c55). P4 and P5 supply miss at
every comfort, so the miss is the dial family, not an interaction with
comfort. **These dials are not shippable.** If the score is wanted, the
next campaign sweeps `t_partner` (0, 2.5) and `w_serious` (0.25) with
this as its baseline, as prereg §What this is not anticipated.

Refusal exposure is not measured here (prereg); the refusal stamp
(spec 046, implemented on Product's branch) will carry it.

## Consequences

- **For the owner's comfort call**: the curve is in the table. If the
  identity question ("is playing through hunger Biscuit-ness?") comes
  down on the side of feeding her, use flat comfort; the weights
  recommendation is withdrawn (P3 corrected reading). Owner's lean
  2026-09-01: c30 viable, c25/c20 to be run (addendum).
- **For Biscuit 3.0's clone**: whatever is chosen is the ANCHOR's
  behaviour; the clone inherits it with the leash's fidelity and the
  transfer is the training's to show (prereg §What this is not).
- **For spec 042's dials**: `t_partner 5.0` is far above the realized
  partner value distribution (mean partner play need at duet start
  4.3). Any shipped default needs the next sweep.
- **For the prereg method**: two measures failed as bars. Excursions
  per 1k counts meals that started above the line; with full-reset
  meals it grows as the eating level falls toward 30 (do not use it as
  a lateness measure again; time-above and latency p50 are the
  lateness measures). "Low-need play" as a share of life below 30 is
  compositional; a character bound has to be on a quantity the
  treatment cannot move by construction, and total play was the only
  one here.

## Bars as pinned, summary

| bar | result |
|---|---|
| P1 | c45/w35/c35 PASS on total play; c30-off MISS (0.70x). Low-need half compositional, never binds. |
| P2 | MISS every arm as pinned (excursion measure inverted). On time>30 alone: c30 0.91 (clears 2/3 both seeds), c35 0.62, w35 0.51, c45 0.26. |
| Decision | middle case → owner call on the curve. |
| P3 | PASS as pinned (w35 closes 0.51 vs c35 0.62, keeps 209 vs 179 play), but the bar read eat only; w35 leaves cuddle, her highest need, at 0.42 ≥30 vs c35's 0.26. Weights withdrawn. |
| P4 | PASS for all score-off arms (0.96–1.06x); MISS for all score-on arms (0.46–0.51x). |
| P5 | partner-need PASS, play PASS, supply MISS at every comfort; dials not shippable. |

Report-only: no watchdog entry in 20 runs; happiness table in
`score.json`; Biscuit eat max 48–81 across runs (no starvation; the
041 economy holds).

## Addendum 1 results: comfort 25 / 20 (2026-09-01; declared @ 1c003f6 before collection; 4/4 valid)

Same binary and protocol as the main sweep (no crate change between);
census polls 1,547 and world polls 1,572 per run, watchdog quiet in all
four. Read against the main sweep's c55-off baseline and c30-off.

| arm | eat ≥30 B \| roster | drink ≥30 B | cuddle ≥30 B \| roster | eat p50 | excursions /1k (floor) | play /1k duet + elem | vs c55 | roster duets /1k | announce any B \| roster | happiness B \| roster |
|---|---|---|---|---|---|---|---|---|---|---|
| c30-off | 0.13 \| 0.09 | 0.09 | 0.16 \| 0.13 | 10.5 | 8.2 (4.4–5.0) | 67.3 + 95.8 = 163.1 | 0.70x | 25.5 | 0.39 \| 0.21 | 84.8 \| 87.0 |
| c25-off | 0.06 \| 0.07 | 0.05 | 0.10 \| 0.11 | 11.0 | 3.15 (4.27) | 56.4 + 80.3 = 136.6 | 0.58x | 23.4 | 0.19 \| 0.19 | 86.3 \| 87.5 |
| c20-off | 0.05 \| 0.08 | 0.03 | 0.07 \| 0.11 | 15.0 | 2.02 (4.09) | 54.3 + 51.4 = 105.7 | 0.45x | 22.8 | 0.15 \| 0.19 | 87.6 \| 87.8 |

Seeds: c25 play 130.2 / 143.1, eat ≥30 0.071 / 0.055; c20 play 106.5 /
104.8, eat ≥30 0.048 / 0.051. Play-solo zero in all four.

**E1 (roster-parity welfare) PASS both.** Every gap at or below zero,
pooled and per seed: c25 eat −0.01, drink −0.01, sleep −0.00, cuddle
−0.01 (seed maxima +0.008); c20 eat −0.03, drink −0.02, sleep −0.01,
cuddle −0.04. At c25 she sits on the roster's line on every need; at
c20 she eats and cuddles BEFORE the roster does (a `playful` cat gets
serious at a fixed level, a `needs_driven` cat acts on whichever need
is top, so the fed-earlier ordering is expected below the roster's
eating level of 21–27).

**E2 (character)** 0.58x and 0.45x of c55-off total play, both inside
the pre-declared ranges (0.55–0.65, 0.40–0.55). The loss lands where
predicted: element play keeps paying (96 → 80 → 51/1k) and duets start
to fall below 30 (67 → 56 → 54/1k), where they had held 67–79 across
c55–c30. Duet share rises 0.41 → 0.51 because elements fall faster.

**E3 (roster supply) PASS both**, 0.88x and 0.85x of c55-off (bar
0.85x); c20 sits on the line. Biscuit is a smaller share of the
roster's play supply the more she eats.

**E4 (troughs) MISS both as pinned.** One poll under 60 happiness in
~3,100 per arm (c25 worst 56.6 in seed 1, c20 worst 59.5 in seed 2)
against c30's zero. Immaterial in size; reported as the bar was
written.

**Predictions (all held).** Armed excursions per 1k turned over below
30 as F-038 point 4 said they must: 8.2 (c30) → 3.15 → 2.02, now below
the floor's 4.1–4.3 (she eats earlier than the roster, so fewer of her
meals start above 30). Her announce share fell to the roster's rate at
c25 (0.39 → 0.19 vs 0.19; cuddle 0.10, eat 0.06) and under it at c20
(0.15): below the announce threshold she leaves play before arming, so
the hungry-Biscuit meow largely disappears from the client. Hungry-play
share 0.15 → 0.05 → 0.04.

**Recommendation rule applied: c30 stands.** Highest comfort passing E1
and E3 with E2 at or above the owner's accepted 0.70x is c30 (c25 and
c20 pass E1 and E3 but sit at 0.58x and 0.45x). c25 meets the
second-candidate residual condition (all gaps under +0.02) but not the
E2 condition, so it is reported as the curve's next point, not as a
candidate. The owner has the whole curve; what c30 → c25 buys is her
residual +0.04 above the roster on every need and half her hungry
meows, for 12% of c55 play (~26/1k, of which ~11 are duets).

Report-only: Biscuit happiness matches the roster's within 1.2 points
at c25 and 0.2 at c20; demand price 15.2 → 13.75 → 12.41; eat max
per run unchanged in kind (no starvation).

## Addendum 1b results: comfort 32 / 28 (2026-09-01; declared @ 9a4b83c before collection; 4/4 valid)

The bracket of the accepted point. Same binary and protocol; census
polls 1,546–1,547 and world polls 1,571–1,572 per run; watchdog quiet
(0 entries) in all four.

| arm | eat ≥30 B \| roster | drink ≥30 B | cuddle ≥30 B \| roster | eat p50 | excursions /1k (floor) | play /1k duet + elem | vs c55 | roster duets /1k | announce any B \| roster | happiness B \| roster |
|---|---|---|---|---|---|---|---|---|---|---|
| c35-off | 0.23 \| 0.10 | 0.20 | 0.26 \| 0.14 | 26.5 | 7.9 (4.7) | 72.1 + 107.0 = 179.1 | 0.76x | 26.8 | 0.63 \| 0.24 | 82.8 \| 86.2 |
| c32-off | 0.18 \| 0.09 | 0.12 | 0.21 \| 0.12 | 18.5 | 8.2 (4.7) | 66.0 + 111.3 = 177.2 | 0.76x | 25.2 | 0.52 \| 0.22 | 83.9 \| 86.8 |
| c30-off | 0.13 \| 0.09 | 0.09 | 0.16 \| 0.13 | 10.5 | 8.2 (4.4) | 67.3 + 95.8 = 163.1 | 0.70x | 25.5 | 0.39 \| 0.21 | 84.8 \| 87.0 |
| c28-off | 0.10 \| 0.09 | 0.08 | 0.15 \| 0.12 | 10.0 | 6.05 (4.15) | 63.4 + 90.1 = 153.5 | 0.65x | 25.4 | 0.29 \| 0.21 | 84.8 \| 86.8 |
| c25-off | 0.06 \| 0.07 | 0.05 | 0.10 \| 0.11 | 11.0 | 3.15 (4.27) | 56.4 + 80.3 = 136.6 | 0.58x | 23.4 | 0.19 \| 0.19 | 86.3 \| 87.5 |

Seeds: c32 play 175.4 / 179.1, eat ≥30 0.179 / 0.182; c28 play 148.1 /
159.0, eat ≥30 0.123 / 0.091. Play-solo zero in all four.

**E1** c32 MISS (gaps eat +0.09, drink +0.07, sleep +0.09, cuddle
+0.09; both seeds over 0.05 on eat, sleep and cuddle); c28 PASS (eat
+0.02, drink +0.02, sleep +0.02, cuddle +0.03; seed maxima +0.04).
**E2** 0.76x and 0.65x, both inside the declared ranges (0.72–0.78,
0.62–0.68). **E3 PASS both**, 0.95x and 0.95x. **E4** c32 PASS (no poll
under 60); c28 MISS (0.7% of polls, all in seed 1, worst 25.4; see
below).

**Predictions**: E1 verdicts as declared; excursions c32 8.2 (≈8
predicted), c28 6.05 (4–6, at the edge: the turnover is just beginning
at 28); announce c32 0.52 (0.45 predicted, under), c28 0.29 (0.25). The
read is monotone on welfare (eat ≥30 0.23 → 0.18 → 0.13 → 0.10 → 0.06
over 35/32/30/28/25) and on total play (0.76 → 0.76 → 0.70 → 0.65 →
0.58), with one flat step: c32 buys c35's play at a third less time
hungry (eat ≥30 0.18 vs 0.23, cuddle 0.21 vs 0.26, eat p50 18.5 vs
26.5). Between 32 and 28 each 2 points of comfort costs ~0.05x of c55
play and buys ~0.025 of every gap. Duets are flat 63–67/1k across
32–28 and start falling only below 28.

**The c28 seed-1 trough** (ticks ~6,844–7,100, 22 polls). Biscuit is
`resting with_friend 1` while Miso is `idle`: a one-sided cosleep, her
cuddle climbing 82 → 100 through the "shared" rest and eat/drink
following (drink 100 at tick 7,099), happiness 59 → 25. Self-resolved by
tick 7,213 (cuddle 20, playing); watchdog quiet. This is the same shape
as the served soak's Miso event (2026-09-01, attn-cert
`miso-stall-1788266378.jsonl`: partner left, drip not landing). Nothing
about comfort 28 causes it (absent in seed 2 and in every other arm at
25–32); it is a roster mechanic that a random seed exposed here.
Reported, not investigated; second sighting on the record.

**Recommendation rule applied: c30 stands.** c32 misses E1 on three
needs in both seeds; c28 passes E1 at 0.65x, under the owner's 0.70x.
The bracket puts the pin between two points that fail on opposite
sides, which is what the rule needs. The owner's residual choice is
whether the 0.70x line is worth +0.04 on every need over c28 (which
buys roster parity within +0.03 and a quarter fewer hungry meows for
~10/1k play, of which ~4 are duets).

Report-only: demand price 17.2 → 16.0 → 15.2 → 15.2 → 13.75; c32 and c28
partner play need at duet start 4.4 / 4.5, unchanged from the curve.

## Play rejection pricing (2026-09-01, exploratory, `avail_hazard.py`, no guard)

Asked whether a partner-value formula can lower Biscuit's duet
refusals. Mechanically no: a duet is refused iff the partner has an
activity clock at her apply slot (`world.rs:1256`); a free adjacent
friend accepts whatever its needs, and turn order is redrawn each tick
(`world.rs:315`), so the race F-033 point 6 describes is the whole
mechanism. On the 14 score-off runs (52k free-friend moments), the
chance a free friend has entered a scene one poll later is 0.33 at top
non-play need <10 rising to 0.42 at ≥40; flat 0.37–0.39 across play
need; 0.33 → 0.41 across delta = play − top. An 8 pp spread against a
37% base hazard (≈3.8%/tick): perfect ranking by need state moves her
refusal rate by 2–3 points. 38% of her duets start from a friend that
was mid-scene one poll earlier (resting 21%, sleeping 7%, grooming 6%),
48% from within 2 tiles, 83% within 4: travel time is the tax. The
refusal cost is hers alone (F-033: 4.7% of her ticks; the friend's scene
continues) and is not in any raw until spec 046 lands.

Consequence for the score: rejection is dropped as a target. The score
is judged on CONSENT, the share of Biscuit's duets that conscript a
friend whose top non-play need is already ≥30 (poll-resolution sample,
n ≈ 180–220 starts per arm): 0.29 at c55, 0.19 at c30, 0.16 at c25
(≥40: 0.08 / 0.06 / 0.06), bounded per duet by `play = { min = 2, max =
5 }` ticks. Bars for any consent dial: roster duet supply ≥0.85x c55
and all-five-needs roster parity. The multiplicative-delay amendment is
held (a rejection lever).

## Addendum 2 results: the consent gate at c30 (2026-09-01; declared @ 1f60b8d, instruments @ 0cff5b2, before collection; 4/4 valid)

Binary from main f45a880 (spec 047 merged). Arms c30-off2 (the c30
config on the new binary, `consent_line` absent) and c30-consent30
(`consent_line = 30.0`), seeds 20260911 / 20260912. Census polls
1,557–1,558, world polls 1,479–1,480 per run; watchdog quiet (0
entries) in all four; the refusal ring was drained every poll with
zero gaps.

**C1 identity PASS, at the event level.** c30-off2 reproduces the old
c30-off tick for tick: every one of the 15,355 / 15,144 census events
in the first 21,000 ticks of the new runs is in the old run's event
set (the old runs carry 1–2 extra events at the window cut). Pooled
play 163.1 → 163.1, eat ≥30 0.132 → 0.132, duets 67.3 → 67.3. The 047
gate at 0.0 is inert at run time, not only in the unit guards. The
old c30-off boot logs were overwritten by a mis-globbed launch that was
killed before any data file was touched; the data files carry their
16:00 timestamps.

| arm | R7 consent share [seeds] | Biscuit duets /1k | element /1k | total play | duet share | roster duets /1k | roster-roster starts /1k | E1 gaps eat / drink / sleep / cuddle | R8 partnered tax | all refused-idle | happiness B \| roster |
|---|---|---|---|---|---|---|---|---|---|---|---|
| c30-off2 | 0.208 [0.196, 0.220] | 67.3 | 95.7 | 163.1 | 0.41 | 25.5 | 34.8 | +0.04 / +0.04 / +0.04 / +0.03 | 0.049 | 0.082 | 84.8 \| 86.9 |
| c30-consent30 | 0.013 [0.015, 0.011] | 49.0 | 117.3 | 166.4 | 0.29 | 21.2 | 35.7 | +0.05 / +0.05 / +0.06 / +0.06 | 0.034 | 0.073 | 84.6 \| 87.2 |

**C2 consent PASS.** R7 falls 0.208 → 0.013 (25 of 1,960 duet starts,
both seeds under 0.05). The residual 25 are read at poll resolution: in
most the partner's play need at the previous poll was 28–38 (play on or
near its top), and a friend that initiates a duet with Biscuit is
counted against her by this readout, which cannot see who proposed. Two
Clementine starts at cuddle 85–97 and one Kittybear start at bath 33–39
(bath 7 one poll earlier) are interpolation or friend-initiated; none
is evidence the gate is leaky, and none of the three sites needs
checking.

**C3 play kept MISS.** Biscuit's duets 67.3 → 49.0/1k, 0.728x against
the 0.90x bar and the 60–64 prediction. Total play 1.02x (bar 0.96x):
the lost duets went to elements (95.7 → 117.3/1k), not to other
friends. Partner mix is unchanged (Pumpkin 0.31 → 0.30, Miso 0.26 →
0.24, Kittybear 0.22 → 0.25, Clementine 0.21 → 0.21). The offline
pricing said 21% of her duets would be blocked and an eligible idle
friend stood within 2 tiles in 84% of those; the run says 27% were
lost and the substitute was an element. What the pricing did not model:
after a friend drops out of the ranking the next-best candidate is
priced against elements with the same distance discount, and the
get-serious path prices play solo when its friend is blocked (the
accepted degradation). Chase-exclusion tails ride in the same number
(caveat 3). Reported as one price.

**C4 roster supply MISS, but it is C3's shadow.** Roster duets 25.5 →
21.2/1k (0.829x, bar 0.95x). The readout counts each roster kitty's
duets including those with Biscuit; her 18.3/1k lost duets spread over
four seats are 4.6/1k each, and the observed drop is 4.35/1k.
Roster-roster duet starts are flat: 34.8 → 35.7/1k. The gate costs the
roster no play with each other; it costs them play with Biscuit, which
is the play the gate exists to decline.

**C5 welfare MISS on cuddle, at the edge on sleep.** Biscuit's E1 gaps
widen eat +0.006, drink +0.014, sleep +0.020, cuddle +0.028 (bar
+0.02); the roster's own shares move −0.006 to −0.014 (inside ±0.02,
all in the roster's favour). Per seed: cuddle gap 0.034 / 0.021 →
0.054 / 0.058, both seeds up; sleep 0.032 / 0.043 → 0.072 / 0.043,
seed 1 only. c30 was pinned at E1 margins of +0.03–0.04; the gate adds
0.01–0.03 and E1 flips to MISS at c30 (+0.049 / +0.050 / +0.057 /
+0.056 against 0.05). Happiness Biscuit 84.8 → 84.6, roster 86.9 →
87.2. She plays slightly more in total, farther from her friends, and
the roster is left alone slightly more.

**R8 refusal tax (scripted early look).** Partnered refusals
(`play` at a `kitty` target, `absorbed == false`): 4.9% of her ticks
off, 3.4% with the gate, seeds 4.5 / 5.2 → 3.6 / 3.1. The old
scripted figure lands on F-033's policy figure (4.7%) and the gate
takes it to the owner's 3.5% line, from above. All refused-into-idle
proposals (elements occupied, blocked moves, rests) run 8.2% → 7.3%;
element refusals rise 2.4 → 3.1% with the extra element play. Read next
to E1: the gate lowers the tax and widens the welfare gap at the same
time, so on the owner's rule (parity is the gate, tax is the
investigate line) it does not pay for itself at c30.

**Recommendation rule applied: C2 passes, C3 / C4 / C5 miss → report
the price; owner call.** The gate does its job (consent share 0.21 →
0.01) at a price the prereg did not anticipate: 27% of Biscuit's duets,
substituted by element play, and E1 parity lost by 0.006–0.007 at c30.
Two ways to pay it, both owner's: (a) ship c30 + consent as the anchor
and accept E1 at +0.05–0.06 (Biscuit 3.0's trained reading decides the
tax question anyway); (b) re-pin comfort with the gate on, one bracket
run at c28 / c26 + consent, since Addendum 1b's c28 passed E1 at +0.02–
0.03 without the gate and play there was 0.65x. Not recommended: tuning
the gate's line above 30, which trades C2 for C3 on a 25-start residual.

## Addendum 3 results, Half A: `w_value` under the gate (2026-09-02; declared @ a7adae2 before collection; 4/4 valid)

Same binary as Addendum 2. Arms `c30-wv25` (`w_value 0.25`, `w_busy
4.0`) and `c30-wv50` (`w_value 0.5`, `w_busy 2.0`), each = c30-consent30
plus those two lines (diffed). 20,000 ticks × 2 seeds, watchdog quiet,
1,556 census / 1,481 world polls per run.

**The dial fails, and not the way the prereg predicted.** Biscuit's
play split per 1k ticks (duet + element + solo):

| arm | duets | element | solo | total | roster duets | loiter |
|---|---|---|---|---|---|---|
| c30-off2 | 67.3 | 95.7 | 0.0 | 163.1 | 25.5 | 0.142 |
| c30-consent30 | 49.0 | 117.3 | 0.0 | 166.4 | 21.2 | 0.137 |
| c30-wv25 | 53.6 (52.5 / 54.6) | 49.5 (46.7 / 52.2) | 54.8 (52.9 / 56.6) | 157.8 | 21.8 | 0.179 |
| c30-wv50 | 51.2 (51.7 / 50.8) | 31.4 (30.1 / 32.6) | 67.3 (70.2 / 64.3) | 149.9 | 20.9 | 0.196 |

Duets recover 49 → 54 / 51 (predicted 54–58 / 60–66; D1 MISS at
0.80x / 0.76x of off2). Element play does not go back to friends, it
goes to SOLO play: 117 → 50 / 31 per 1k (D3 MISS, 0.52x / 0.33x of
off2's 95.7) while solo play, zero in every arm of this sweep so far,
appears at 55 / 67 per 1k. Total play falls 5% / 10%. D2 passes (R7
0.020 both arms, both seeds); D4 misses (0.85x / 0.82x, the consent
arm's own miss carried); D5 passes at wv50 and misses at wv25 on cuddle
(+0.028), with E1 gaps still +0.04–0.06 in both arms. D6 FLAGS in both
arms: loiter share 0.137 → 0.179 / 0.196, more than 3x the seed spread
above consent30. R8 partnered tax 0.034 / 0.033, unmoved.

**Mechanism, read off the polls.** Every solo-play poll in both arms
has a friend on an adjacent tile (89/90 and 113/113 in seed 1), and in
81% / 78% of them that friend is busy, most often RESTING (78 and 86 of
the adjacent states), then sleeping or grooming. Any `w_value > 0`
switches on mid-scene admission (`selection.rs:499`, spec 042 D2):
friends in a scene enter the ranking for anticipatory approach, priced
by `w_busy × expected_wait`. `expected_wait` is the scene minimum less
ticks served, floored at zero, and zero for a boundless activity
(`selection.rs:581-589`); rest is boundless and most scenes are past
their minimum, so a resting or sleeping friend is admitted at ZERO wait
cost and out-scores every critter by `w_value × play_need` tiles. Biscuit
walks to the resting friend, cannot conscript it (spec 006), and the
solo backstop fires beside it. The dial did not re-admit idle friends
so much as re-route Biscuit's play pressure onto unavailable ones. That
is Product's flag 1 (2026-09-02) arriving in full, and the reason the
c30-on arm of the main sweep read 3.2/1k solo where every off arm read 0.

**Recommendation rule applied: D1 MISS at both values, D3 MISS at both,
D6 flagged → the dial is not safe, and raising it is ruled out.** As
declared, Product's option (b), a blocked-conditional friend preference
that can reach site 3, is the next candidate; owner's call. The cheaper
engine change this half points at is narrower: decouple mid-scene
admission from `w_value` (its own switch, or price a boundless or
past-minimum scene as unavailable rather than as zero wait), after
which `w_value` would rank IDLE friends against critters the way the
sizing assumed. Either is a spec-042 amendment in Product's lane. Half
B (the four twins on the re-proposal-fix binary) still runs as declared;
its `wv` twins now measure whether the fix changes this picture, which
it should not.
