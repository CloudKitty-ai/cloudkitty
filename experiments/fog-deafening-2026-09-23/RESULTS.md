# Fog-era deafening ablation — results

Collected 2026-09-24T02:26–02:37Z under the declaration frozen at
d5c6c74 (`prereg.md`, committed before collection). The `--deaf` mask
landed at 207f8c9 with three mutate reds (the mutations named in
`prereg.md` §Instrument); the copy that collected is
afc43ae's, whose only change is the `deaf` band entry (`tool_sha256`
3be2a687… in every battery header). Four arms, the same 30 seeds
(900101–900130), gen1-A served roster on `anchor-b3.toml`, served
clock, 20,000 ticks per seed. Raws in `results-raw/` (uncommitted,
this directory). Git HEAD moved mid-collection (the intact and want
headers record d5c6c74, the here and all headers 5cf3d03, a docs-only
commit at 02:28:42Z); the tool, config and binding hashes are
identical across all four arms.

## The table (deafen-read.md, from `results-raw/deafen-read.json`)

| arm | team happiness | paired delta vs intact | worse/n | nash_state | dist ticks | max distress age |
|---|---|---|---|---|---|---|
| intact | 92.471 | -- | -- | 0.9244 | 125 | 94 |
| want | 92.451 | -0.020 [-0.284, +0.264] | 15/30 | 0.9241 | 299 | 61 |
| here | 92.016 | -0.455 [-0.796, -0.017] | 30/30 | 0.9194 | 3891 | 290 |
| all | 85.755 | -6.716 [-11.935, -4.948] | 30/30 | 0.8487 | 470286 | 6150 |

Per-seat mean happiness (seat order Miso, Biscuit, Pumpkin, Kittybear,
Clementine): intact 93.00 / 91.05 / 93.13 / 92.89 / 92.28; all-deaf
85.67 / 86.85 / 89.27 / 89.83 / 77.15. The all-deaf cost is unevenly
carried: Clementine's seat loses 15.1 happiness, Miso's 7.3, the other
three 3.1–4.2. Low-happiness share rises from 0.0 (intact) to 0.014
(all-deaf); no seat touches the floor in any arm.

## Predictions, scored

1. **Holds.** All-deaf paired mean team-happiness delta −6.716, past
   the declared −0.15 line at 45 times its width, worse on 30 of 30
   worlds (per-seed deltas −4.948 to −11.935). No F-026 arm silenced
   everything: under global vision its deafening arms (purr, follow-me,
   both) moved team happiness by at most 0.015, and both-deaf measured
   +0.013.
2. **Holds.** Both family arms land between intact and all-deaf:
   want-deaf −0.020 (15 of 30 worse — a null), here-deaf −0.455 (30 of
   30 worse, past the line on its own). The reader's `P2_families_between`
   check tests only the lower bracket; the upper clause (neither family
   above intact by more than the band) is read off the printed deltas,
   both negative.
3. **The whisper, at scale and then some.** Distress ticks: intact 125,
   here-deaf 3,891 (31×), all-deaf 470,286 (3,762×, against the
   declared ≥ 2). Here-deaf moves the tail far more than the mean: a
   31-fold distress rise beside a 0.46 happiness cost. That is the
   direction F-026's whisper pointed, not its case — the whisper was
   purr-deafening at flat welfare, and here-deaf's mean cost is real
   (P2). All-deaf's longest distress streak runs 6,150 ticks.

## What the arms do and do not attribute

The two family arms measure 0.475 of the 6.716 between them, with
additivity between families untested: here-words alone cost 0.455,
want-words alone are welfare-null even under fog (they measurably move
listeners, F-048, and buy no happiness — the same function-without-
fitness F-026 found for the pre-fog chorus). The remaining ~6.2 is
all-deaf-only machinery this design does not separate: the free
register (mew, chirp, purr), the heard-row position channel (under
all-deaf a cat outside the vision disc is socially absent — no row, no
position, no way to be found), and their interactions. A heard-rows-only
arm would split position from meaning; it was not declared and is not
claimed. Everything removed is hearing, so the declared P1 reads on the
channel as a whole.

## Decision rules, applied

- **P1 holds → the client-copy claim "communication sustains welfare"
  is claimable for the fog generation** (prereg decision rule 1). The
  supporting number for copy is the all-deaf arm: silence the channel
  and the served roster pays 6.7 happiness and a 3,762× distress-tick
  multiplier on 30 of 30 worlds.
- **Recorded as F-052** (same commit). F-026 stays active within its
  own scope — global vision on the pre-039 world, per its SC-005 note —
  and its entry now points here for the fog-era re-run.
- The confound stands as declared (F-026 SC-005): nothing here
  attributes the change to fog alone versus the bugs-2.0 economy or the
  world; the claim is channel-fitness of the served generation on the
  served world.

## Regeneration

### Collect

Runtime: 11 minutes total on 6 workers (stage.log stamps 02:26:04 to
02:37:06). Never run by the gate.

```
cd /Users/elizabethkelly/ai/cloudkitty
caffeinate -s nohup bash experiments/fog-deafening-2026-09-23/deafen_stage.sh > experiments/fog-deafening-2026-09-23/results-raw/stage.log 2>&1 &
```

### Read

Runtime: under 5 seconds. No environment variables required.

```
cd /Users/elizabethkelly/ai/cloudkitty
experiments/exp-006-character-gen/.venv/bin/python experiments/fog-deafening-2026-09-23/deafen_read.py \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-c0-deaf-30x20000.jsonl \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-want-c0-deaf-30x20000.jsonl \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-here-c0-deaf-30x20000.jsonl \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-all-c0-deaf-30x20000.jsonl \
  --out experiments/fog-deafening-2026-09-23/results-raw/deafen-read.json \
  --md experiments/fog-deafening-2026-09-23/results-raw/deafen-read.md
```
Gate: **PASS** 2026-09-24 (first real use; initial run FAILED four
items — an F-026 arm mis-citation, a contradicted whisper equivalence,
an attribution-shaped scope line, the instrument SHA — fixed and
re-verified in two follow-up passes) · claims: 58 arithmetic, 5
threshold, 16 characterisation, 1 UNDECIDABLE (the mutate reds; no
persistent log), 12 provenance · raws 0c302f3a9c86.

## Addendum, 2026-09-24: the residual split (second collection, prereg-2.md)

The first collection's attribution section reads: "The remaining ~6.2
is all-deaf-only machinery this design does not separate: the free
register (mew, chirp, purr), the heard-row position channel (under
all-deaf a cat outside the vision disc is socially absent — no row, no
position, no way to be found), and their interactions. A heard-rows-only
arm would split position from meaning; it was not declared and is not
claimed." The second collection (declared 2ca4e23, before collection;
arms at e7ec874, two mutate reds) ran that arm and a free-register arm
on the same 30 paired seeds:

| arm | team happiness | paired delta vs intact | worse/n | nash_state | dist ticks | max distress age |
|---|---|---|---|---|---|---|
| free | 92.233 | -0.237 [-0.519, +0.117] | 28/30 | 0.9219 | 816 | 157 |
| rows | 86.100 | -6.371 [-8.780, -4.158] | 30/30 | 0.8528 | 458967 | 6094 |

Predictions 4–6 (prereg-2) all hold: rows-deaf −6.371 is past the
−0.15 line (P4); free-deaf −0.237 is more negative than want-deaf's
−0.020 (P5); neither arm lands below all-deaf's −6.716 (P6).

The split: erasing heard rows alone — position and in-fog words of
unseen cats, seen-row content intact; the arm does not separate the
two — costs 6.371 of the all-deaf 6.716, which is 0.95 of it, with
the distress profile to match (458,967 ticks against all-deaf's
470,286; longest streak 6,094 against 6,150). The channel's welfare
value under fog is dominated by knowing about cats outside the vision
disc. Free-deaf's 0.237 sits between want (−0.020) and here (−0.455)
and is an upper bound on free-word meaning, because free calls also
create heard rows, so the arm removes some position along with the
words. The three family masks are disjoint and partition all fifteen
kinds, yet their costs sum to 0.712 against all-deaf's 6.716:
strongly non-additive, the interaction being that a heard row
survives any single-family deafening while another family's call is
in the window. (P6 for the free arm — −0.237 above all-deaf's −6.716
— is read off the printed deltas; the reader's P6 check covers the
rows arm only.)

F-052's register bound is replaced under prereg-2's quoting rule. The
replaced sentence read: "**Attribution bound**: the two family arms
measure 0.475 of the 6.716 between them, additivity untested; the
rest is the free register, the heard-row position channel and
interactions, not separated by this design (no heard-rows-only arm)."
Its successor in F-052 attributes the load to what a cat hears about
unseen cats, position and words together. F-052's headline is
unchanged, per the same declared rule.

Gate (addendum): **PASS** 2026-09-24 (first run FAILED one WEAK
characterisation on the F-052 lines — position credited alone where
the rows arm removes position and unseen-cat words together — plus two
decision-rule deviations: the headline clause, reverted, and the
unquoted replaced bound, now quoted above; fixed and re-verified) ·
addendum claims: 43 arithmetic, 4 threshold, 6 characterisation, 1
UNDECIDABLE (the mutate reds), 8 provenance · raws 483a9a822b3f.

## Addendum, 2026-09-24 (2): direction without range — the R sweep (third collection, prereg-3.md)

The second collection's split sentence reads: "erasing heard rows
alone — position and in-fog words of unseen cats, seen-row content
intact; the arm does not separate the two — costs 6.371 of the
all-deaf 6.716". This collection separates the geometry: six arms on
the same 30 paired seeds keep every heard row's true bearing and
project its range to a fixed R ∈ {5, 11, 16, 20, 28, 37} tiles
(declared dcd9a83 before collection; mask at 60d899a, two mutate
reds; R anchored on the measured heard-distance distribution,
`results-raw/r-probe.json`: median 16, q25 11, q75 20, max 37).

| arm | team happiness | paired delta vs intact | worse/n | nash_state | dist ticks | max distress age |
|---|---|---|---|---|---|---|
| dir5 | 92.106 | -0.365 [-0.577, -0.006] | 30/30 | 0.9207 | 99 | 67 |
| dir11 | 92.255 | -0.216 [-0.479, +0.066] | 28/30 | 0.9222 | 352 | 81 |
| dir16 | 92.268 | -0.203 [-0.503, +0.021] | 28/30 | 0.9223 | 53 | 37 |
| dir20 | 92.176 | -0.295 [-0.573, -0.049] | 30/30 | 0.9213 | 683 | 261 |
| dir28 | 92.069 | -0.402 [-0.713, -0.093] | 30/30 | 0.9201 | 1725 | 246 |
| dir37 | 91.864 | -0.607 [-0.878, -0.358] | 30/30 | 0.9179 | 8685 | 612 |

Predictions 7–9 (prereg-3) all hold: every dir arm lands between
rows-deaf (−6.371) and intact (P7); the smallest |delta| is dir16,
the true median (P8); dir16's −0.203 is far above −3.186, half of
rows-deaf (P9).

The reading. The row without its exact range — bearing plus the
in-fog words, both of which the dir arms keep — recovers 0.97 of the
rows-deaf loss (dir16 −0.203 against −6.371). No arm separates
bearing from those words, so their shares are unmeasured; what the
sweep isolates cleanly is range itself, the intact-vs-dir16
contrast: exact range is worth at most 0.203 to these minds, and
some of that is the fixed-range distortion, not missing information
(0.203 is also the best of six sample means, not a bound with a
confidence statement). The cost is V-shaped in the fake range with
its minimum at the true median — 0.365 / 0.216 / 0.203 / 0.295 /
0.402 / 0.607 across R 5 / 11 / 16 / 20 / 28 / 37. The bias
asymmetry lives in the distress tail, not the mean: at the matched
offset (R 5 against R 28, eleven-ish tiles either side) welfare is
level — the paired difference dir28 − dir5 is −0.037, dir28 worse on
16 of 30 — while distress is not (dir5: 99 ticks on 4 seeds; dir28:
1,725 on 22; dir37: 8,685 on all 30, longest streak 612). Sounding
too near still costs the mean (dir5 −0.365, 30 of 30 worse); an
everyone-sounds-far bias costs the same in the mean at the matched
offset and much more in the tail. dir16's distress ticks landing
under intact's 125 is not claimed as an improvement: at these
magnitudes the totals rest on a few seeds (dir16's 53 come from 2
seeds; 26 of 30 intact seeds have zero distress ticks).

Gate (addendum 2): **PASS** 2026-09-24 (first run FAILED three WEAK
characterisations on the F-052 lines — the 0.97 credited to bearing
where the dir arms also keep the in-fog words, and a near/far
asymmetry claimed on welfare where it lives in the distress tail —
reworded and re-verified; the matched-offset comparison is now in the
text) · addendum claims: 60 arithmetic (one inherited rounding note,
−3.186 for −3.185), 3 threshold, 9 characterisation, 1 UNDECIDABLE
(the mutate reds), 9 provenance · raws 489d3a744b78.
