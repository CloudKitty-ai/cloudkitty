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
construction**. Cause, from the mechanics: `eat_relief` is 35 points, so
a cat that eats at 55 drops to 20 and dwells long above 30 before each
meal; a cat that eats at 30 drops to 0 and cycles 0 → 30 → 0. Fewer,
longer excursions at high comfort; more, shorter ones at low comfort.
Excursions per 1k counts cycles, not lateness. The prereg pinned a
measure that cannot move in the direction it asked for. That is a
design error in the prereg, recorded here; the exploratory reading is
time>30 alone, and the decision rule below is applied to it with that
label.

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
comfort line moves for ALL needs, so bath and cuddle at 35–55 also pull
her out of play (hungry-play share 0.32 vs 0.35, nearly equal food
behaviour; element play 141.6 vs 107.0). Comfort on non-food needs was
costing play without buying food. Per-need weights are the right shape
for lever 1.

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
  down on the side of feeding her, the sweep's shape says do it with
  per-need weights (food band at 35, others at 55: w35) rather than a
  flat comfort, and expect ~11% less play, ~half the hungry-play share,
  eat p50 88 → 31. A flat c35 buys a little more food (0.62 vs 0.51)
  for twice the play loss.
- **For Biscuit 3.0's clone**: whatever is chosen is the ANCHOR's
  behaviour; the clone inherits it with the leash's fidelity and the
  transfer is the training's to show (prereg §What this is not).
- **For spec 042's dials**: `t_partner 5.0` is far above the realized
  partner value distribution (mean partner play need at duet start
  4.3). Any shipped default needs the next sweep.
- **For the prereg method**: two measures failed as bars. Excursions
  per 1k is a cycle counter under partial relief (do not use it as a
  lateness measure again; time-above and latency p50 are the lateness
  measures). "Low-need play" as a share of life below 30 is
  compositional; a character bound has to be on a quantity the
  treatment cannot move by construction, and total play was the only
  one here.

## Bars as pinned, summary

| bar | result |
|---|---|
| P1 | c45/w35/c35 PASS on total play; c30-off MISS (0.70x). Low-need half compositional, never binds. |
| P2 | MISS every arm as pinned (excursion measure inverted). On time>30 alone: c30 0.91 (clears 2/3 both seeds), c35 0.62, w35 0.51, c45 0.26. |
| Decision | middle case → owner call on the curve. |
| P3 | PASS: w35 closes 0.51 vs c35 0.62 (within 0.25×), keeps 209 vs 179 play. |
| P4 | PASS for all score-off arms (0.96–1.06x); MISS for all score-on arms (0.46–0.51x). |
| P5 | partner-need PASS, play PASS, supply MISS at every comfort; dials not shippable. |

Report-only: no watchdog entry in 20 runs; happiness table in
`score.json`; Biscuit eat max 48–81 across runs (no starvation; the
041 economy holds).
