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
  **Owner 2026-09-02**: the scripted c30 + consent anchor read 3.4–3.5%
  (Addendum 2 R8, comfort-sweep Half B), right at the line; the call
  on further action waits for Biscuit 3.0's own refusal read after
  training (step 7, this instrument).
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

# Second window: the Fog Gen 1 roster (0.3.0, 2026-09-16)

Same instrument, same prereg, one window after the reseat. Window
valid: 15,041 ticks (254..15,294 of a fresh world), 101 polls at 120 s,
zero ring gaps. Served config sha256 `4ce71e5f…547f73` (five
`policy:fog-gen1-*` seats, vision radius 4, consent_line 30), engine
head efc1a3c (tag 0.3.0), tick_ms 800. Raw:
`results-raw/refusal-baseline-254.json`, uncommitted.

| seat | taxed | absorbed | taxed rows by proposal |
|---|---|---|---|
| Miso | 1.05% | 3.86% | move 73, play:kitty 46, sleep:with 17, rest:with 14, groom:kitty 8 |
| Biscuit | 1.48% | 3.78% | play:kitty 191, move 29, sleep:with 2 |
| Pumpkin | 1.11% | 3.92% | move 103, play:kitty 32, rest:with 16, sleep:with 8 |
| Kittybear | 1.30% | 4.04% | move 122, play:kitty 37, rest:with 27, sleep:with 5 |
| Clementine | 1.56% | 4.55% | move 118, play:kitty 68, rest:with 35, sleep:with 12 |

Roster: 4,006 rows, 977 taxed + 3,029 absorbed. Taxed density
0.065/tick (was 0.119), combined 0.266/tick (was 0.334).

Decision rules: every seat is under the 3.5% INVESTIGATE line, the
highest Clementine at 1.56%. `retention_floor_15k` = 3,995 < 6,000, the
default stands. Zero gaps. Nothing to action.

Biscuit's 5.13% → 1.48% is a roster change, not a repricing read: the
seat went from scripted playful (comfort 55, no consent gate) to a
distinct network trained on the c30 + consent corpus, so doctrine rule 9
applies and the number is the new composition's, comparable to the first
window only as a reference. Her tax is still 86% partner play
(191 of 222), the F-033 shape at a third of the volume. The other four
seats now pay mostly in movement (bumped tiles) and play, where the
scripted three paid in grooming; the groom tax went from 150–252 rows a
seat to 0–8, which is the FR-014 read from the other side (the minds
groom clean, adjacent friends).

### Unanswered from-the-fog calls (reason `partner_absent`)

`partner_absent` is a kitty-targeted proposal whose target exists but is
not adjacent (spec 049 T093: under fog, a partnered proposal at a stale
heard position is a refusal by design). Per seat, per hour at 4,500
ticks/h over 3.34 h:

| seat | calls/h | taxed/h | by proposal |
|---|---|---|---|
| Miso | 67.9 | 17.1 | sleep:with 142, rest:with 59, play:kitty 18, groom:kitty 8 |
| Biscuit | 57.1 | 16.2 | sleep:with 137, play:kitty 52, rest:with 2 |
| Pumpkin | 44.9 | 11.7 | rest:with 69, sleep:with 66, play:kitty 11 |
| Kittybear | 51.8 | 15.0 | sleep:with 81, rest:with 73, play:kitty 18 |
| Clementine | 64.0 | 20.0 | rest:with 105, sleep:with 86, play:kitty 23 |

Roster 286/h, flat across the window (290, 283, 283 in the three full
hour bins). 86% of them (820 of 955) are cosleep or corest proposals at
a partner who is not beside the caller, and 72% are absorbed (the
caller was already in a scene, so the miss cost no turn). The remaining
reasons, for the record: `partner_busy` is play only (Biscuit 158/h,
the others 82–137/h; Biscuit's 42 taxed/h is her F-033 tax), and
`other` is eat at an empty tile and moves into an occupied one
(21–99/h a seat). This is the first read of the stamp on a fog roster;
no line is declared for it and none is proposed here. It is a Gen 2
input (the minds keep proposing cosleep at a partner they cannot see
beside them), banked in `fog-gen1-shakeout/GEN2-INPUTS.md`.
