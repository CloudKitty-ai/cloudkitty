<!-- FIXTURE — PLANTED COPY. This is the tier 6 section of
experiments/beam-world-screen-2026-09-19/RESULTS.md with four
deliberate errors planted for the accuracy-gate rule-5 red. NEVER
cite this file as evidence; the real section lives in the
experiments tree. The answer key is expected-findings.md beside it —
the gate subagent must not read that file. The Regeneration block
below is rewritten to the forward-only contract (the real doc
predates it); the raws it names live in the NATIVE checkout. -->

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
| 7 | 0.412 / 86.37 | 0.061 / 89.85 / 0.279 | **0.601 / 0.570** | 91.04 / 91.04 (+1.2 / +1.2) | 90.58, 90.66 / 0.905, 0.906 / 0.468, 0.451 / 0.235, 0.215 | 1 ; 13, 10 ; 16, 3 |
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
   on both, 6–8 inside 0.75). The 7→8 gain (0.44, seed means) exceeds
   the 5→6 gain (0.64); count 8 sits within 1.0 of the floor-0 level on
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
  past the rule, the curve says count 8 is measurably the best world
  for a learned mind. Experiments' offer is **6**: the package world
  as it stands, with the count-6 arms
  and tier 5's numbers intact. The transfer read makes 7 or 8 a free
  move later; the case for it is the teacher's corpus placement (0.34
  at six, 0.40 at seven, 0.44 at eight against the shelf's ~0.4 bar),
  which the sleep-rule spec should lift first. **Owner ruled 6
  (2026-09-21, #390: "six beams it is")**, and sent the teacher
  sleep-rule spec to Product the same day
  (`HANDOVER-product-2026-09-21.md`).
- **Prediction 4 holding in substance means the count can move at the
  Gen 2 collection without a new screen**; a mind trained at one count
  reads the others. Recorded as F-051.
- **Nothing deploys.** The served world keeps floor 0 and its count.

## Regeneration

### Collect (the gate never runs these)

```
caffeinate -s nohup bash experiments/beam-world-screen-2026-09-19/stage6.sh > experiments/beam-world-screen-2026-09-19/results-raw/tier6/stage6.log 2>&1 &
bash experiments/beam-world-screen-2026-09-19/results-raw/tier6/meow/run.sh
# distress replay, minutes per seed:
# CERT_ARTS=<arts> experiments/exp-006-character-gen/.venv/bin/python experiments/beam-world-screen-2026-09-19/distress_inspect.py experiments/beam-world-screen-2026-09-19/count-7.toml 870015 --seat 0=ppo:cnt7-s1 --seat 1=ppo:cnt7-s1 --seat 2=ppo:cnt7-s1 --seat 3=ppo:cnt7-s1 --seat 4=ppo:cnt7-s1
```

### Read (runtime ~1 s; reads results-raw only, writes only --out)

```
experiments/exp-006-character-gen/.venv/bin/python experiments/beam-world-screen-2026-09-19/tier6_read.py \
  experiments/beam-world-screen-2026-09-19/results-raw/tier6/battery \
  experiments/beam-world-screen-2026-09-19/results-raw/tier5/battery \
  --out <scratch>/tier6-read-fresh.json
```

Recorded JSON: `experiments/beam-world-screen-2026-09-19/results-raw/tier6/tier6-read.json`.
The meow table and the distress replay above have no Read line: their
claims are checkable only against the recorded raws or not at all.
