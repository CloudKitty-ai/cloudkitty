# Seating analysis v1 — gen1-A baseline (the served seating)

First run of the standing instrument (DECLARATION.md; design record
`../seating-analysis-inputs-2026-09-28.md`). Everything here is a
READING under doctrine rule 10 — a baseline for comparing future
seatings and generations, never a bar. Collected 2026-09-27 (local),
declaration committed 4768c2b before collection.

Setup: gen1-A (the served composition, verified off the running
server: all five `.ckpolicy` hashes match the handoff table; the
served config differs from `anchor-b3.toml` only in seat wiring) —
the battery-measured torch actors on `anchor-b3.toml`, clock `train`
(the served seam), greedy both heads under the mask. Seeds
900501–900505 × 20,000 ticks. **No leg aborted; the streak-abort
line (1,000) was armed on every leg and never fired** (worst
distress-flag ages are not the streak table below — the max
worst-NEED≥25 streak was 233 ticks, Kittybear, and distress flags
rose twice in 500,000 cat-ticks; both rows verified in the raws).

## The numbers (summary printer output, verbatim)

```
legs: [(900501, 20000, None), (900502, 20000, None), (900503, 20000, None), (900504, 20000, None), (900505, 20000, None)]
nash per seed: [0.9231, 0.9234, 0.9246, 0.9247, 0.9245]
gap mean/p95 per seed: [(6.14, 11.72), (6.39, 12.48), (6.19, 11.54), (6.15, 10.99), (6.32, 11.83)]

PER-CAT (pooled across seeds: activity shares are means of per-seed shares;
cadences/latencies are means of per-seed medians; totals are sums)
| cat | Idle | Rest | Sleep | Eat | Drink | Play | Groom | contact | company | partnered | nearest med/p95 | hap mean/p5 | H bits | transH | home |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Miso | 0.541 | 0.117 | 0.188 | 0.023 | 0.029 | 0.036 | 0.066 | 0.464 | 0.774 | 0.236 | 2.0/12.2 | 93.0/88.3 | 2.00 | 1.20 | 204 |
| Biscuit | 0.543 | 0.015 | 0.149 | 0.012 | 0.017 | 0.227 | 0.038 | 0.468 | 0.783 | 0.178 | 2.0/11.4 | 91.0/85.7 | 1.82 | 1.11 | 209 |
| Pumpkin | 0.615 | 0.129 | 0.090 | 0.048 | 0.030 | 0.041 | 0.047 | 0.411 | 0.748 | 0.196 | 2.0/12.0 | 93.1/88.1 | 1.88 | 1.18 | 236 |
| Kittybear | 0.573 | 0.116 | 0.115 | 0.025 | 0.022 | 0.035 | 0.114 | 0.469 | 0.798 | 0.205 | 2.0/11.6 | 92.9/88.5 | 1.96 | 1.19 | 240 |
| Clementine | 0.592 | 0.184 | 0.105 | 0.024 | 0.025 | 0.033 | 0.037 | 0.514 | 0.835 | 0.273 | 1.0/10.0 | 92.3/87.3 | 1.84 | 1.10 | 225 |

NEEDS AND TENDING (pooled means of per-seed values; streak max = worst seed)
| cat | worst-gate med/p95 | max streak>=25 | eat cadence med | drink cadence med | water directness |
|---|---|---|---|---|---|
| Miso | 13.6/23.9 | 94 | 43 | 36 | -0.440 |
| Biscuit | 19.3/31.8 | 193 | 82 | 62 | -0.245 |
| Pumpkin | 13.4/27.5 | 118 | 18 | 31 | -0.405 |
| Kittybear | 13.5/24.0 | 233 | 39 | 45 | -0.386 |
| Clementine | 14.8/26.6 | 152 | 40 | 39 | -0.369 |

PLAY/SLEEP ELEMENT PARTNERS (summed ticks across seeds)
| cat | play ticks | element-play ticks | sleep ticks | beam-sleep ticks |
|---|---|---|---|---|
| Miso | 3619 | 557 | 18787 | 1525 |
| Biscuit | 22659 | 5898 | 14895 | 125 |
| Pumpkin | 4063 | 458 | 8951 | 81 |
| Kittybear | 3540 | 704 | 11504 | 513 |
| Clementine | 3285 | 364 | 10524 | 517 |

PAIRS (means across seeds), sorted by pair ticks
| pair | pair ticks | scenes | dist med | territory JS | reciprocity |
|---|---|---|---|---|---|
| Biscuit-Clementine | 1952 | 471 | 8.4 | 0.116 | 0.85 |
| Miso-Clementine | 1793 | 449 | 9.8 | 0.113 | 0.83 |
| Miso-Biscuit | 1679 | 399 | 8.8 | 0.144 | 0.96 |
| Pumpkin-Kittybear | 1616 | 385 | 8.4 | 0.077 | 0.90 |
| Kittybear-Clementine | 1581 | 404 | 10.2 | 0.114 | 0.81 |
| Pumpkin-Clementine | 1483 | 365 | 10.4 | 0.131 | 0.72 |
| Miso-Kittybear | 1441 | 363 | 11.2 | 0.172 | 0.96 |
| Miso-Pumpkin | 965 | 226 | 12.6 | 0.204 | 0.90 |
| Biscuit-Pumpkin | 938 | 236 | 10.6 | 0.180 | 0.87 |
| Biscuit-Kittybear | 928 | 261 | 12.0 | 0.165 | 0.95 |

SOCIAL (pooled): concentration and modal top partner; distress totals
| cat | concentration | top partner | distress onsets | responded | latency med (mean of seeds) |
|---|---|---|---|---|---|
| Miso | 0.35 | Clementine/Kittybear | 0 | 0 | n/a |
| Biscuit | 0.37 | Clementine | 0 | 0 | n/a |
| Pumpkin | 0.33 | Kittybear | 1 | 1 | 0.0 |
| Kittybear | 0.33 | Clementine/Pumpkin | 1 | 1 | 12.0 |
| Clementine | 0.32 | Biscuit | 0 | 0 | n/a |

SPEECH (pooled shares; top-3 non-silent heads; speak rate by worst-need bin <15 / 15-25 / >=25,
mean of per-seed rates)
  Miso: silent 0.688; Purr 0.1050, HereWater 0.0512, HereFood 0.0488; rate by bin 0.333/0.281/0.279
  Biscuit: silent 0.630; Purr 0.1165, Mew 0.0552, HereWater 0.0394; rate by bin 0.374/0.376/0.347
  Pumpkin: silent 0.690; Purr 0.0849, HereFood 0.0560, HereWater 0.0497; rate by bin 0.331/0.284/0.265
  Kittybear: silent 0.738; HereFood 0.0491, HereWater 0.0480, Chirp 0.0471; rate by bin 0.266/0.253/0.281
  Clementine: silent 0.773; HereWater 0.0507, HereFood 0.0491, Chirp 0.0291; rate by bin 0.233/0.218/0.233

ROUTINE dominant lag per seed (ticks), per cat
  Miso: [1787, 1024, 925, 1659, 2483]
  Biscuit: [3243, 2963, 69, 3391, 3686]
  Pumpkin: [1282, 216, 2186, 1898, 885]
  Kittybear: [1632, 51, 2739, 1742, 3095]
  Clementine: [941, 51, 3095, 364, 2459]

CONVERGENCE (successive 2,000-tick window JS per seed): mean of first 3, mean of last 3, trend
  900501: first3 0.167  last3 0.176  min 0.142  max 0.220  n 9
  900502: first3 0.211  last3 0.247  min 0.154  max 0.272  n 9
  900503: first3 0.203  last3 0.164  min 0.148  max 0.212  n 9
  900504: first3 0.222  last3 0.209  min 0.135  max 0.293  n 9
  900505: first3 0.199  last3 0.247  min 0.186  max 0.292  n 9
```

## The reading

- **Welfare is level and equitable across seeds**: team nash
  0.9231–0.9247 (spread 0.0016), happiness p5 85.7–88.5, mean
  worst-cat gap 6.14–6.39. Two distress-flag onsets in 500,000
  cat-ticks, both met by contact (one at latency 0, one at 12
  ticks) — too few events for any latency characterisation.
- **Biscuit is a different economy from the other four**: play
  share 0.227 vs 0.033–0.041 (5.6–6.9× the others' play ticks),
  26.0% of its play ticks solo within reach of a critter, Rest
  nearly absent (0.015), and the price shows in its needs row —
  worst-gate median 19.3 vs 13.4–14.8, the sparsest tending
  cadences (eat 82 vs the others' 18–43; drink 62 vs 31–45), the
  weakest water approach (−0.245), and the lowest happiness (91.0
  mean, 85.7 p5). The trait sheet's play 0.8 is visible across the
  activity, needs, and welfare columns.
- **Everyone approaches water when thirsty**: water directness is
  negative for all five (−0.245 to −0.440 tiles per tick while
  drink need ≥ 25 and not drinking).
- **Beam sleep is a small share on the served (floor-0) world**:
  0.8–8.1% of sleep ticks per cat, pooled 4.3% — at F-047's
  measured level (recorded local: in-beam share 0.041 live pooled;
  the one-tick relief differential does not move sleep placement).
  The Gen 2 floor-15 world is where this column becomes
  informative.
- **Social structure is diffuse, not monopolized**: partner
  concentration 0.32–0.37, reciprocity 0.72–0.96. The most
  overlapping pair is Pumpkin–Kittybear: the lowest territory JS
  (0.077 — the most overlapping home ranges), the top pair from
  each of their own sides by pair ticks (1,616), and Pumpkin's
  modal top partner is Kittybear (Kittybear's own mode is a
  Clementine/Pumpkin tie). Clementine is the roster's connector:
  the highest partnered share (0.273), highest contact and company
  shares, and a top-two pair by pair ticks from every other cat's
  side.
- **Speech splits into two registers by cat** (descriptive only —
  F-048's row-vs-word attribution is OPEN): Miso, Biscuit and
  Pumpkin lead with Purr (0.085–0.117); Kittybear and Clementine
  lead with Here-words and Chirp and are the two most silent seats
  (0.738, 0.773). Speak rate vs own worst-need bin: absolute
  swings are ≤ 0.066, and for Miso and Pumpkin the rate falls
  monotonically as need rises (0.333→0.279 and 0.331→0.265, 16%
  and 20% relative); the other three move ≤ 0.029.
- **No stable routine**: dominant autocorrelation lags scatter
  across seeds within every cat (51–3,686 ticks); no cat holds a
  period across seeds. That is the extent of what was measured.
- **Steady state (her item 2), answered as declared**: successive
  2,000-tick window JS shows no visible transient and no
  consistent direction across seeds — first-3 means 0.167–0.222 vs
  last-3 means 0.164–0.247, per-seed shifts −0.039 to +0.048 with
  mixed sign (3 up, 2 down), window range 0.135–0.293 throughout.
  With n = 9 successive-window values per seed this is a reading
  of "no trend at this window size", not a stationarity test; what
  the 0.135–0.293 level is made of (moving elements, need cycles,
  sampling variance at n = 2,000) was not separated here. For
  pre-generation: no burn-in was visible at this granularity, and
  windows shorter than ~2,000 ticks will carry at least this
  window-to-window variance.
- **Home ranges are broad**: 204–240 of 400 tiles hold 90% of each
  cat's occupancy — territory on this world is overlap, not
  partition (pairwise territory JS 0.077–0.204).

**Heatmap artifact for Client**: `heatmap-gen1-A.json` (tracked) —
per-cat and all-cat tile counts summed over the five seeds, water
tiles per seed, config sha. Comparability caveats as declared:
same-world comparators only; per-seed water positions; a future
seating's heatmap compares within a world config, shapes only
across generations.

## Guard (rule 5)

`test_seating_read.py`: 10 tests on the real 300-tick fixture
(seed 900506), references independent (R_* literals, independent
loops). Three mutate reds, each predicted before the run:

- Manhattan → Chebyshev in `pair_dist` → `test_contact_company_nearest`
  failed as predicted (RED CONFIRMED).
- Bath dropped from the worst-gate index set →
  `test_worst_gate` failed as predicted (RED CONFIRMED) — after one
  VACUOUS first attempt: the test sampled only Pumpkin, the one cat
  whose fixture median is insensitive to Bath; the guard now
  references all five cats.
- JS mixture removed (`m = q`) → `test_js_analytic` failed as
  predicted (RED CONFIRMED).

Cycle note: the first red needed `PYTHONDONTWRITEBYTECODE=1` — a
same-length mutation restored within the same mtime second leaves a
stale `__pycache__` that fakes a post-restore failure.

## Deviations

None from DECLARATION.md. `seating_summary.py` (formatting only, no
metric) was added after collection so the Read fence prints every
derived column this doc uses; the metrics themselves are the
declared reader's, under the guard. Gate round 1 found the
printer's modal-top-partner cell hash-seed nondeterministic on two
real 2–2 ties (Miso, Kittybear); the printer now prints ties
joined, deterministically, and the block above is the fixed
printer's output.

## Regeneration

### Collect

`run_legs.sh` (5 legs, sequential; the fixture came from
`seating_collect.py --seed 900506 --ticks 300`). Never run by the
gate.

### Read

Runtime: under 60 seconds total. No environment variables required.

```
cd /Users/elizabethkelly/ai/cloudkitty
experiments/exp-006-character-gen/.venv/bin/python experiments/seating-analysis-2026-09-28/seating_read.py \
  --raws experiments/seating-analysis-2026-09-28/results-raw/streams-900501.npz \
         experiments/seating-analysis-2026-09-28/results-raw/streams-900502.npz \
         experiments/seating-analysis-2026-09-28/results-raw/streams-900503.npz \
         experiments/seating-analysis-2026-09-28/results-raw/streams-900504.npz \
         experiments/seating-analysis-2026-09-28/results-raw/streams-900505.npz \
  --out <scratch>/seating-read-fresh.json
experiments/exp-006-character-gen/.venv/bin/python experiments/seating-analysis-2026-09-28/seating_summary.py <scratch>/seating-read-fresh.json
```

GATE: PASS round 2 of 2, 2026-09-28 — arithmetic ~41 (1 rounding
note), threshold 5, characterisation ~16 (1 WEAK reported, wording
adopted: "most overlapping pair"), undecidable 5, provenance ~14;
raw-dir hash 9a318ef70d8c4938. Round 1 FAIL: printer tie-break
nondeterminism (fixed, block re-pasted), two contradicted
social-structure sentences, F-047 wording, steady-state overclaim.

## Addendum 2026-09-28 — flagged values (owner's representation rule)

Owner's rule (2026-09-28): "flag values for individual cats that
are 1-2 sigma from the group median … easier to quickly identify
interesting values during review." Implemented as a printer mode
(`--flags-only`; the default output is byte-identical to the gated
fence above): per metric, each cat's |x − group median| in units of
the group's sample σ (ddof=1, n = 5 cats); † = 1–2σ, ‡ = ≥ 2σ. A
review-highlighting heuristic, not a statistic — at n = 5 roughly a
third of cells pass 1σ by chance, and one extreme value inflates σ,
so ‡ marks only strong standouts. Flag math under the guard
(`test_flag_z`, mutate red: median→mean, confirmed).

Output, verbatim:

```
FLAGGED VALUES (|x - group median| / group sigma, ddof=1, n=5 cats;
dagger 1-2 sigma, double-dagger >=2; heuristic, not a statistic --
at n=5 about a third of cells pass 1 sigma by chance)
  † Pumpkin · activity Idle: 0.6152 (group median 0.57306, 1.32σ)
  † Biscuit · activity Rest: 0.01493 (group median 0.11652, 1.66σ)
  † Clementine · activity Rest: 0.18423 (group median 0.11652, 1.11σ)
  † Miso · activity Sleep: 0.18787 (group median 0.11504, 1.85σ)
  † Pumpkin · activity Eat: 0.0479 (group median 0.02419, 1.81σ)
  † Biscuit · activity Drink: 0.01652 (group median 0.02517, 1.58σ)
  ‡ Biscuit · activity Play: 0.22659 (group median 0.03619, 2.24σ)
  ‡ Kittybear · activity Groom: 0.11427 (group median 0.04747, 2.07σ)
  † Pumpkin · contact: 0.41133 (group median 0.46788, 1.55σ)
  † Clementine · contact: 0.5139 (group median 0.46788, 1.26σ)
  † Pumpkin · company: 0.74814 (group median 0.7826, 1.08σ)
  † Clementine · company: 0.83483 (group median 0.7826, 1.63σ)
  † Clementine · partnered: 0.27258 (group median 0.20508, 1.81σ)
  ‡ Clementine · nearest median: 1 (group median 2, 2.24σ)
  † Clementine · nearest p95: 10 (group median 11.6, 1.85σ)
  ‡ Biscuit · happiness mean: 90.9731 (group median 92.9093, 2.20σ)
  ‡ Biscuit · happiness p5: 85.7169 (group median 88.0769, 2.09σ)
  † Miso · entropy bits: 1.99852 (group median 1.88257, 1.50σ)
  † Biscuit · transition entropy bits: 1.11099 (group median 1.1769, 1.40σ)
  † Clementine · transition entropy bits: 1.10082 (group median 1.1769, 1.61σ)
  † Miso · home range: 203.8 (group median 225.4, 1.33σ)
  † Biscuit · home range: 208.6 (group median 225.4, 1.03σ)
  ‡ Biscuit · worst-gate median: 19.32 (group median 13.58, 2.28σ)
  † Biscuit · worst-gate p95: 31.82 (group median 26.64, 1.60σ)
  † Miso · max streak >=25: 94 (group median 152, 1.03σ)
  † Kittybear · max streak >=25: 233 (group median 152, 1.44σ)
  † Biscuit · eat cadence: 82.2 (group median 39.8, 1.81σ)
  † Biscuit · drink cadence: 62.2 (group median 38.6, 1.96σ)
  † Biscuit · water directness: -0.244765 (group median -0.386474, 1.91σ)
  ‡ Biscuit · play ticks: 22659 (group median 3619, 2.24σ)
  ‡ Biscuit · element-play ticks: 5898 (group median 557, 2.22σ)
  † Miso · sleep ticks: 18787 (group median 11504, 1.85σ)
  † Miso · beam-sleep ticks: 1525 (group median 513, 1.74σ)
  † Biscuit · silent share: 0.63029 (group median 0.68981, 1.09σ)
  † Clementine · silent share: 0.77338 (group median 0.68981, 1.53σ)
  † Miso · partner concentration: 0.351154 (group median 0.333666, 1.02σ)
  † Biscuit · partner concentration: 0.366756 (group median 0.333666, 1.93σ)
```

Reading: 37 flags, 8 at ‡. Biscuit carries six of the eight ‡
(the play economy and its welfare price, already the doc's second
bullet). The two ‡ the prose had not led with: Kittybear's groom
share (0.114 vs group median 0.047) and Clementine's nearest-cat
median (1 tile vs 2 — the connector reading, sharpened). Miso's
† profile (sleep 0.188, beam-sleep 1,525, home range 203.8) reads
as the sleeper-homebody of the roster.

### Read (addendum)

Runtime: under 10 seconds. No environment variables required.

```
cd /Users/elizabethkelly/ai/cloudkitty
experiments/exp-006-character-gen/.venv/bin/python experiments/seating-analysis-2026-09-28/seating_summary.py --flags-only \
  experiments/seating-analysis-2026-09-28/results-raw/seating-read.json
```

GATE (addendum): PASS scoped round 2, 2026-09-28 — arithmetic 14,
hedge/characterisation 6, implementation/guard 4, undecidable 2;
block reproduces byte-identical; default-mode md5 unchanged from
the r2 stamp. Scoped round 1 FAIL: the reading paragraph miscounted
the ‡ rows in the block pasted directly above it (7 for 8; five for
six) and mis-cited a bullet position — the corrector-needs-the-gate
class again.

## Addendum 2026-09-28 — pair structure (owner's reading, confirmed)

Owner, reviewing the territory map: "It also looks like the two
pairs are biscuit/clem and pumpkin/kittybear." Confirmed against
the pair table, and recorded because it names the roster's social
architecture in one line:

- **Biscuit–Clementine** is the #1 pair by partnered time (1,952
  pair ticks, 471 scenes) and it is mutual: Biscuit's modal top
  partner is Clementine and Clementine's is Biscuit.
- **Pumpkin–Kittybear** is #1 from both of its own sides (1,616
  pair ticks) with the roster's lowest territory JS (0.077; every
  other pair ≥ 0.113), mutual up to Kittybear's 2–2 modal tie
  (Clementine/Pumpkin).
- **Miso is the odd cat out**: its top pair is Miso–Clementine
  (1,793 ticks, the roster's second-highest), but Clementine's top
  is Biscuit, and no cat's #1 pair is Miso. The structure is two
  dyads plus Miso attached to the Biscuit–Clementine pair (to
  Clementine 1,793, to Biscuit 1,679 — both members, Clementine
  slightly ahead).
- Spatially the dyads are the map's clusters: the north group
  (Miso, with Biscuit and Clementine ranging between halves) and
  the southern Pumpkin–Kittybear ground. Verified in the raws
  beyond the summed map: per-seed mean y puts Miso north (4.9–7.3)
  and Pumpkin and Kittybear south of Miso in all five seeds
  (y 9.1–11.4; three of those ten cat-seeds sit just north of the
  9.5 midline);
  per-seed mean x puts Pumpkin west of center in all five
  (7.6–9.2), Kittybear roughly neutral (8.2–10.5), and the
  Biscuit/Clementine east lean holds in three of five seeds
  (both neutral-to-west in 900504/900505) — a pooled tendency,
  softer than the north–south axis.

Watch across reseats (a reading, not a bar): whether "who ends up
unpaired" tracks traits or is a seating accident — the standing
analysis now measures this per generation.

### Read (pair-structure addendum)

Pair/modal/JS numbers: the main Read fence (pairs, reciprocity,
territory_js, SOCIAL table). Per-seed spatial means, from the raws:

```
cd /Users/elizabethkelly/ai/cloudkitty
experiments/exp-006-character-gen/.venv/bin/python -c "
import numpy as np
for s in [900501,900502,900503,900504,900505]:
    z=np.load(f'experiments/seating-analysis-2026-09-28/results-raw/streams-{s}.npz')
    print(s, z['pos'][:,:,0].mean(0).round(1).tolist(), z['pos'][:,:,1].mean(0).round(1).tolist())
"
```

GATE (pair-structure addendum): PASS scoped round 2, 2026-09-28 —
pair/structure 11, spatial 8, characterisation 3, hedges 2,
undecidable 1 (the quote's verbatimness — it is verbatim; the
owner typed it in this session). Scoped round 1 FAIL: "south in
ALL five seeds" conflated south-of-midline with south-of-Miso
(three cat-seeds sit north of 9.5), and "through Clementine"
understated Miso's tie to Biscuit (1,679, 94% of 1,793) — both
compression errors in the summary sentence, not the table.
