# Displaced-size radius cell, Gen 2 — declaration (2026-10-21)

Authorization: owner, 2026-10-21, verbatim: "Call 1: run it", on the
§8.5 question as put to her ("Run the cell (one radius value at a
displaced size, scouts-first) or record it as not triggered?"). The
trigger it answers is the prereg's declared future read
(`../gen2-prereg-2026-10-17.md` §8 item 5, frozen 18f06f84): "if the
trained-vs-scripted gap moves with size across cert legs, one
displaced-size radius cell runs, scouts-first per the carryover." The
record that reached her: `../gen2-cert-battery-2026-10-20/RESULTS.md`
§"§8.5, the declared future read" (the paired gap +5.566 ± 0.623 at
20×20, +4.594 ± 0.451 at 40×40, +7.187 ± 1.704 at 100×100; the prereg
names no margin, so the ruling is hers). Committed before any cell
data exists. A `--dry-run` of the driver ran before this commit; it
executes nothing.

## Question

Under the vision law (prereg, owner 2026-10-17) the sight radius steps
with world size: 4 at 20×20, 5 at 40×40, 6 at 100×100. Every cross-size
row therefore moves two things at once, and the 0.97 fall in the gap
between the two cert legs cannot be read as a size effect or a radius
effect from the record. This cell holds the size at 40×40 and moves the
radius alone, one step below the law (5 → 4, the served base), both
sides of the pairing. With the recorded 40×40 rows at radius 5 it forms
a 2 × 2 on the same 30 worlds:

| | radius 5 (law) | radius 4 (this cell) |
|---|---|---|
| scripted teacher | EXISTS: `../gen2-comparator-legs-2026-10-14/results-raw/vision5-40/legs/size40/` | runs |
| certified roster rot2 | EXISTS: `../gen2-cert-battery-2026-10-20/results-raw/g2-rot2/legs/size40/` | runs |

Reading, declared now (descriptive, rule 10): if the paired gap at
(40×40, radius 4) sits near the 20×20 gap (+5.566), the fall between
the cert legs travelled with the radius; if it sits near the 40×40 law
gap (+4.594), it travelled with the size. Anything in between, or
inside the paired SD, is reported as such and establishes nothing. No
bar, no gate, no trigger reads this cell; the certificate stands as
issued.

## Cell

- Config `g2leg-40-r4.toml` (sha256 87f4cb2e…): byte-for-byte the law
  config `../gen2-comparator-legs-2026-10-14/g2leg-40.toml` (sha256
  f45a5183…, the config the rot2 cert leg ran) with ONE line changed,
  `[vision] radius = 5` → `4` (line 555; `diff` shows that line alone).
  The vocabulary flags stay armed as the roster was trained and
  certified. This is NOT the pre-law "v4" comparator config (sha256
  84bc50b5…, radius 4 with trill/ekekek unarmed); that row is kept as a
  check only, see R4.
- Driver: `../gen2-comparator-legs-2026-10-14/run_legs.py --only 40`,
  band `g2cmp` (seeds 905001–905030, the pairing band; deliberate
  reuse, no new burn, a touch note goes on its SEED-BANDS row), 30 ×
  20,000 ticks, served clock, `--abort-streak 1000` armed by the
  driver. Two seatings in sequence: `scripted`, then `g2-rot2` (Miso
  s2, Biscuit s4, Pumpkin s6, Kittybear s7, Clementine s1; policy-final
  sha256s a22b8713 / 4040554a / 69d7248c / c93a4424 / 8ca8a517 as the
  certificate records them).
- Harness: the standing `../fog-gen1-cert/cert_harness_fog.py`, same
  instrument as both recorded rows. Binding: the lab venv's
  `cloudkitty.abi3.so` sha256 e3bcc79a…, ENGINE_COMMIT b5aaa8cd, the
  binary that trained the roster and ran the battery (deviations entry
  5: held fixed for Gen 2).
- Output: `results-raw/<seating>/scouts/size40/` and
  `results-raw/<seating>/legs/size40/`, log `results-raw/run.log`.
  Never deleted.

## Reads, declared now

R1. **The 2 × 2.** Team happiness (mean of the five seats' mean
happiness) per world, each of the four cells; the paired gap (rot2 −
scripted, same world) at radius 4 and at radius 5, mean ± per-world SD,
SE, sign count over 30. The radius effect on each side alone (radius 4
− radius 5, paired by world): scripted and rot2 separately. The
difference of the gaps (gap at 4 − gap at 5) with its paired per-world
SD and SE. The 20×20 cert-leg gap (+5.566 ± 0.623) printed beside for
the reading above, not recomputed here.

R2. **Per seat.** Each seat's mean happiness in the four cells and its
paired rot2 − scripted gap at both radii, so a radius effect that lives
in one or two seats is visible (the owed reads found Pumpkin and
Clementine below their teacher at every size).

R3. **Welfare beside.** Worst distress streak (mean, max over 30
worlds), F-053 line events and aborts, each of the four cells, as the
battery prints them.

R4. **Instrument check.** The new scripted radius-4 row against the
pre-law v4 scripted row (`../gen2-comparator-legs-2026-10-14/results-raw/legs/size40/`,
config 84bc50b5…): per-world team happiness equal to the printed
precision. The comparator arc found the vocabulary arming byte-inert
for scripted seats (its vocab-armed re-run, 90 of 90 rows identical);
this cell re-reads that on its own rows before any number above is
trusted. A mismatch is reported first and read as an instrument finding.

Not read: play, speech, dispersion, beam placement (no new reader for
them here; the harness rows carry what they carry and a later arc may
read them). No network trains at radius 4 (the S§6 arm's
trained-at-radius side is a separate declared arm, not this cell).

## Doctrine check (CLAUDE.md rule 8)

- Rule 9 moved the claim's scope: rot2 is a frozen roster under an
  altered world dial. The cell reads how the certified roster
  TRANSFERS across one radius step at 40×40; it says nothing about
  what a roster trained at radius 4 would do there, and it decides no
  dial. The vision law stays as ruled.
- Rule 10 moved the reporting: descriptive, paired per-world SD and SE,
  sign counts, inside-noise differences establish nothing, n = 30
  worlds stated with every number; no bar is set after the data.
- Rule 8 (scarcity of information): the radius IS the information
  scarcity dial; the cell moves it one step to attribute an observed
  effect and proposes no change to it.
- Rules 1–7, 11, 12: checked, moved nothing (no reward, price,
  teacher, relief or world change ships from here; no invalidation
  clause).
- FINDINGS read (CLAUDE.md rule 7): F-053 (frozen Gen 1 minds under
  size displacement at radius 4) is the harm line this cell's stops
  guard; F-050 and its 2026-10-21 addendum (beam placement under floor
  15, one density) are not touched; the comparator arc's vision-4
  record (40×40 scripted 80.341 vs the law's 81.634, paired +1.294) is
  the scripted side's prior at this radius.

## Stops and welfare (practice, owner 2026-09-26; asymmetric)

- Scouts-first per the K§5 carryover: the band's first 3 worlds at
  full ticks for each seating before its leg, each with the F-053
  1,000-tick distress-streak stop; a scout miss stops that seating and
  the driver, taken to the owner, never auto-continued. The leg itself
  is gated on its own rows (entry-4 remedy): an aborted row, a row at
  the line, or a short file stops the driver.
- Welfare-cost line: the rot2 seating exposes 5 covered minds × (3 +
  30) worlds × 20,000 ticks = 3.3M cat-ticks at one radius step below
  the law, a milder fog than the certified 40×40 leg (visible share
  rises from 5.06% toward the served 12.25%); the scripted seating
  exposes none. Benefit: attributes the one cross-size movement the
  certificate left unexplained, as the prereg declared. Prior: rot2's
  40×40 scouts and leg at radius 5 ran clean (worst scout streak 602
  across the step-8 seatings; no aborts on the certified roster).

## Instrument

- Reader: `radius_read.py` here, `--out radius-read.json --md`, stdlib
  python3 from the lab venv. Guards in `test_radius.py`, each with a
  predicted red via `scripts/mutate.sh` before it is trusted: (g1) the
  radius-5 paired gap reproduces the certificate's +4.594 at 40×40 to
  three decimals (a reader that drops the pairing or reads the wrong
  row cannot); (g2) the difference of gaps equals the per-world
  arithmetic of the two paired gaps (a reader that averages before
  pairing cannot); (g3) R4's identity check compares per world, not
  per mean (a permuted scripted row set must fail it).
- Driver guard: `run_legs.py` is unchanged; `test_run_legs.py` stays
  green (10).

## Run

```
cd experiments/radius-cell-g2-2026-10-21 && caffeinate -s bash run_cell.sh > results-raw/run.log 2>&1
```

Scripted then rot2, each: scout 3 worlds → leg 30 worlds. The step-8
battery ran a full three-size seating in about 3 minutes; this cell is
two 40×40 seatings, minutes.

## Read

```
cd experiments/radius-cell-g2-2026-10-21 && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B radius_read.py --out radius-read.json --md
```

RESULTS.md follows, gated by `/accuracy-gate` before commit.
