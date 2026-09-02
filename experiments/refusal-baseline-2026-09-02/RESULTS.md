# Live refusal baseline (spec 046) — results, 2026-09-02

Declared in `PREREG.md` @ 5831cde before collection. Window valid:
15,134 ticks (1,295,817..1,310,950), 95 polls at 120 s, zero ring
gaps (the ring held every row since boot for the whole window, oldest
row 1,295,021). Served config sha256 `275a3d7b…bbed0`, world 20×20,
tick_ms 800, seed 20260718; instrument head 5831cde (dirty paths are
other folders' results-raw only). Raw:
`results-raw/refusal-baseline-1295817.json`, uncommitted.

## The baseline

| seat | taxed | absorbed | taxed rows by proposal |
|---|---|---|---|
| Miso | 0.70% | 5.20% | move 64, sleep:with 33, eat 5, groom 4 |
| Biscuit | **5.13%** | 6.30% | play:kitty 734, move 19, groom 15, rest:with 6, eat 3 |
| Pumpkin | 1.86% | 3.56% | groom 150, move 89, play:kitty 23, sleep:with 12, eat 7 |
| Kittybear | 1.91% | 3.05% | groom 179, move 88, sleep:with 13, eat 6, play 3 |
| Clementine | 2.30% | 3.41% | groom 252, move 77, sleep:with 19 |

Roster: 5,059 rows, 1,801 taxed + 3,258 absorbed. Taxed density
0.119/tick, combined 0.334/tick.

## Decision rules, applied

- Step-5 INVESTIGATE line (owner ruled 2026-09-01: 3.5% of a seat's
  ticks, not a retrain gate; spec 046's >10% is the earlier value):
  Biscuit at 5.13% is above it, every other seat is under (next is
  Clementine at 2.30%). The owner's 2026-09-01 ruling already
  disposes of this reading: Biscuit 2.0 at parity welfare paying
  ~4.7% is not actionable, and the reading that counts is Biscuit
  3.0's after training. Logged, no action.
- Retention: `retention_floor_15k` = 5,014 < 6,000. **The default
  stands**; no config change owed. The combined density is 1.45× the
  taxed-only 0.23/tick the knob was sized on, and the 6,000 default's
  headroom covers it with 20% to spare.
- Zero gaps, window valid, nothing blocks the v2.10 tag (the
  INVESTIGATE line is a step-5 instrument, not a tag prereq).

## Reading

Biscuit's tax is partner play: 734 of her 777 taxed rows (94%) are
`play:kitty`. That is the F-033 mechanism on the served world, read off
the stamp instead of the seam probe. The number is not comparable to
F-033's 4.7% (or Biscuit 2.0's 4.6% seam read), which were pre-048
and counted dead-scene rows that b9f9c00 removed; this 5.13% is the
new reference, and the fact that it lands near the old seam number after
048 took rows away says the seam probe undercounted the live tax rather
than that 048 did nothing.

The other four seats pay in grooming and movement, not play: their
taxed play rows are 3–23 across 15k ticks. Miso's tax is the lowest
(0.70%) and her absorbed share the highest of the transformer seats
(5.20%, 448 of it `sleep:with`): she proposes cosleep from inside a
sleep she is already in. Biscuit absorbs 785 play proposals mid-scene
on top of the 734 taxed ones, so roughly half her play asks arrive
while she is already in something.

The absorbed stream is the step-4 teacher-collapse and H6 input the
spec described; its per-seat shape (Miso sleep-heavy, Biscuit
play-heavy, the scripted three eat/play-mixed) is recorded here as the
pre-fog reference and not interpreted further.

## Carry forward

- F-033's 4.7% and the 4.6% seam reads are retired as reference
  numbers; the step-5 INVESTIGATE line (3.5%, owner's) stands and
  reads this table. Biscuit 2.0 sits above it by ruling, not by
  oversight.
- Re-run the window after the next deploy that touches the selector
  or the roster (Biscuit 3.0 cutover at step 7); one window per deploy,
  same instrument.
