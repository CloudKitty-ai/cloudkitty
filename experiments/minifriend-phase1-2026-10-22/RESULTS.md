# Mini-friend Phase 1 — RESULTS (collected and read 2026-10-22/23)

Declaration: `DECLARATION.md`, ruled as declared (owner 2026-10-22
"Fix the stale draft and go as declared"); prereg basis frozen
18f06f84, §8 items 3–4 and §9. Binding: `BINDING.md` (the arc's own
venv; engine a2e8d044, which is the certified engine plus spec 065,
verified by set L below). Every read here is descriptive (doctrine
rule 10); nothing gates, and the one procedure pin (R2) licenses head
choice for Phase 2 only, never welfare adequacy.

## Headline

A 7,807-parameter belief head (9.2% of the trunk) reading only what a
Gen 2 cat sees estimates a friend's five hidden needs to a root-mean-
square error of about 5.4 need points when the friend is in sight and
in a common state, and about 26 points in the grave stratum, where the
trivial baselines sit at about 53. The natural-frequency head carries
the ostrich signature on every covered friend: in grave states it
predicts the friend 8.6 points less needy than she is, against a bias
near zero in common states. Distress reweighting removes that pooled
optimism (grave bias +1.6) at a cost of 7.4 points² of common-state
error, and the two heads tie on pooled grave loss (ratio 1.017). The
declared dissolution test nevertheless FAILS on its per-friend clause:
Miso's and Kittybear's grave loss under NF exceeds 1.10 × DR's by more
than the between-seed SD, while Biscuit's goes the other way by a wider
margin. The tension is present and friend-specific, not uniform. Pumpkin's
mind-visible grave stratum stayed under min-n after every declared set
and is reported as insufficient coverage.

## Data as collected

| set | worlds | ticks | covered cat-ticks | aborts | distress ticks (Miso / Biscuit / Pumpkin / Kittybear / Clementine) | worst single-need streak | streaks ≥ 150 (F-043 crossings) |
|---|---|---|---|---|---|---|---|
| L (lived; g2cmp 905001–905010, `g2leg-20.toml` as served) | 10 | 20,000 | 1,000,000 | 0 | 0 / 0 / 0 / 0 / 0 | 0 | none |
| W (wide starts {0, 90}; 1095401–1095425, `g2leg-20-W.toml`) | 25 | 6,000 | 750,000 | 0 | 249 / 251 / 63 / 164 / 191 (918) | 199 | Biscuit's seat, world 1095421 (199) |
| G (grave starts {60, 95}; 1095426–1095450, `g2leg-20-G.toml`) | 25 | 4,000 | 500,000 | 0 | 1,577 / 2,096 / 763 / 1,311 / 1,005 (6,752) | 756 | Biscuit 1095429 (704), Kittybear 1095434 (332), Clementine 1095448 (235), Miso 1095449 (234), Biscuit 1095450 (756) |

All three sets seat the certified roster rot2 (Miso s2, Biscuit s4,
Pumpkin s6, Kittybear s7, Clementine s1), greedy masked argmax, served
clock, the F-053 stop (streak 1,000) armed on every world, scouts first
on W and G (the band's first three worlds, read with `check_set.py`
before the rest were launched).

Welfare line, actual: 2.25M covered cat-ticks against the declared
ceiling of 4.25M (L ran 1.0M, ten lived worlds being enough for the
common stratum), 1.25M of them from varied or distressed starts; 0
aborts; the F-053 line never reached; six streaks ≥ 150, all under it.
In W, 25 of 125 cats start in GRAVE (mean start happiness per seat
51.5–56.8); in G all 125 do (mean 21.0–23.0, lowest 11.5). Each
seat's run-mean happiness, averaged over a set's 25 worlds, stays
86.2–88.0 in both sets (single worlds range wider): the roster
relieves distressed starts, and Pumpkin's seat relieves them fastest
(the fewest G distress ticks, 763).

Engine check (set L): every L world equals the certified rot2 battery
row on mean happiness per seat and on distress ticks (`check_L.py`,
`L-check.json`); worlds 905001–905005 are array-equal to the Gen 2 lab
binding's own rot2 streams on needs, happiness, position, activity,
distress, messages and actions. The arc binding reproduces the
certified engine on the served config.

## Samples and coverage (evaluation worlds)

A sample is (observer, friend ≠ observer, tick): the observer's saved
start-of-tick observation and the friend's true state that view was
built from (`needs[t−1]`, the reset state at t = 0). Split by world
(`split.json`, seed 20261022): 19 evaluation worlds (L 905001, 905008,
905009; W 1095404, 1095406, 1095409, 1095411, 1095412, 1095416,
1095417, 1095424; G 1095429, 1095434, 1095437, 1095440, 1095442,
1095446, 1095449, 1095450), 2,800,000 samples. Training worlds 34,
validation worlds 7 (carved from the training worlds: L 905006; W
1095401, 1095414, 1095422; G 1095436, 1095439, 1095447).

Coverage per friend (mind-visible / all-states; `strata-counts.json`,
`phase1-read.json`):

| friend | GRAVE | DA (GRAVE ∪ ADJACENT) | GRAVE reads |
|---|---|---|---|
| Miso | 664 / 3,392 | 1,013 / 4,584 | both versions |
| Biscuit | 746 / 6,544 | 1,011 / 7,296 | both versions |
| Pumpkin | **170** / 768 | 726 / 2,500 | all-states only; mind-visible INSUFFICIENT COVERAGE |
| Kittybear | 671 / 3,320 | 980 / 4,124 | both versions |
| Clementine | 316 / 1,584 | 806 / 2,908 | both versions |

Pumpkin's mind-visible GRAVE stratum is 170 < 200 after L, W and G
(the declared remedy list ended at G): fail-closed, no number is read
from it, and every pooled mind-visible GRAVE figure below pools the
other four friends. On set L alone GRAVE was 0 for every friend and
after W it was 158 / 12 / 4 / 33 / 32: the prereg's foreseen case, met
by the declared probe sets in their declared order.

Two limitations on the grave stratum. One was declared before the
data: G measures whether the head sees a friend who STARTS in
distress, not one sliding into it; in this data the sliding case
exists only in W (cats that start outside GRAVE and enter it later),
and in no lived world (L has no grave tick). The second is seen in the
data, not declared: in G every cat starts in GRAVE together, so the
observer's own needs are informative about the friend's at the start
in a way lived distress would not be. For the second reason in
particular, the grave numbers are best read as an upper bound on
inference skill.

## Heads (R6)

`train_heads.py`: Linear(167 → 24) + ReLU, GRU(24), Linear(24 → 7):
**7,807 parameters**, under the §8 item 4 cap of 8,445 (10% of the
trunk's 84,450), counted and asserted before training. Input per
sample: the observer's self block (109) and the friend's permanent row
(58). Hidden state zero at each world's start, carried across 500-tick
chunks. Loss: weighted MSE over the five hidden needs plus happiness
plus bath (targets /100); NF weight 1; DR weight by the friend's true
stratum on the training samples, inverse frequency capped at 50× the
common stratum's and renormalised to mean 1: training frequencies
GRAVE 0.00309, ADJACENT 0.00209, COMMON 0.99482 → weights 39.87 /
39.87 / 0.797 (the cap binds on both rare strata). Adam 1e-3; early
stop on the validation loss (margin 1e-4, patience 10, cap 200). Seeds
1, 2, 3, the NF/DR pair sharing each.

| run | best epoch / epochs run | best validation loss |
|---|---|---|
| NF-s1 | 65 / 75 | 0.00676 |
| NF-s2 | 81 / 91 | 0.00652 |
| NF-s3 | 72 / 82 | 0.00678 |
| DR-s1 | 55 / 65 | 0.02677 |
| DR-s2 | 57 / 67 | 0.02720 |
| DR-s3 | 69 / 79 | 0.02857 |

Every run plateaued before the cap. (The DR validation loss is DR-
weighted, so the two columns are not comparable across heads.)

## R1 — the 2 × 2, mean squared error on the five hidden needs (need points²)

Mean ± SD over three seeds; per friend then pooled (sample-weighted
over covered friends). The prereg's distress-adjacent column is DA;
GRAVE alone beside it. Square roots are the RMS error in need points.

Mind-visible (the friend's row present):

| friend | NF COMMON | NF DA | NF GRAVE | DR COMMON | DR DA | DR GRAVE |
|---|---|---|---|---|---|---|
| Miso | 29.03 ± 1.25 | 755.63 ± 31.89 | 823.76 ± 37.50 | 34.78 ± 0.71 | 566.75 ± 37.98 | 586.84 ± 56.80 |
| Biscuit | 28.01 ± 0.63 | 615.67 ± 26.50 | 573.68 ± 18.46 | 36.07 ± 2.08 | 870.23 ± 92.45 | 891.81 ± 117.45 |
| Pumpkin | 30.87 ± 0.92 | 374.13 ± 12.56 | insufficient | 38.03 ± 0.76 | 325.82 ± 8.99 | insufficient |
| Kittybear | 25.91 ± 0.67 | 705.31 ± 32.04 | 702.18 ± 34.01 | 33.52 ± 2.33 | 582.09 ± 52.63 | 586.98 ± 55.38 |
| Clementine | 33.66 ± 1.38 | 526.78 ± 39.64 | 707.33 ± 68.96 | 42.15 ± 0.61 | 467.73 ± 24.78 | 612.29 ± 67.75 |
| pooled | 29.52 ± 0.94 | 611.84 ± 9.33 | 696.55 ± 15.21 | 36.94 ± 1.26 | 581.55 ± 33.62 | 685.15 ± 50.76 |

All-states (every tick, seen or not):

| friend | NF COMMON | NF DA | NF GRAVE | DR COMMON | DR DA | DR GRAVE |
|---|---|---|---|---|---|---|
| Miso | 37.61 ± 1.32 | 739.48 ± 15.28 | 790.25 ± 21.44 | 44.70 ± 0.58 | 611.42 ± 36.74 | 624.70 ± 48.94 |
| Biscuit | 36.48 ± 0.81 | 492.23 ± 35.26 | 474.28 ± 34.48 | 45.76 ± 1.85 | 745.03 ± 64.78 | 748.59 ± 70.25 |
| Pumpkin | 39.43 ± 1.09 | 469.92 ± 23.40 | 669.50 ± 59.35 | 47.58 ± 0.37 | 416.20 ± 10.34 | 533.21 ± 16.31 |
| Kittybear | 33.78 ± 0.89 | 624.58 ± 21.64 | 596.10 ± 29.53 | 42.82 ± 1.92 | 623.62 ± 46.07 | 604.39 ± 52.18 |
| Clementine | 43.02 ± 1.43 | 595.77 ± 38.79 | 683.53 ± 62.42 | 52.24 ± 0.22 | 583.94 ± 11.47 | 661.66 ± 16.50 |
| pooled | 38.07 ± 1.09 | 582.11 ± 5.79 | 599.70 ± 11.08 | 46.62 ± 0.97 | 632.77 ± 30.69 | 671.57 ± 37.54 |

What the table says. (a) Common states are estimated well: pooled
mind-visible RMS error 5.4 points (NF) and 6.1 (DR). (b) The grave
stratum is 18 to 24 times harder in squared error (685.15 / 36.94 for
DR, 696.55 / 29.52 for NF): pooled mind-visible RMS 26.4 (NF) and 26.2
(DR). (c) Reweighting costs common-state
accuracy on every friend (+5.8 to +8.5 points² mind-visible) and buys
grave accuracy on three of the four covered friends (Miso −236.9,
Kittybear −115.2, Clementine −95.0 points² mind-visible) while losing
it on Biscuit (+318.1); pooled, the two heads tie on GRAVE (685 vs 697)
and DR is lower on DA (582 vs 612). (d) Mind-visible versus all-states
diverge in both directions: common-state error rises when the friend
is out of sight (29.5 → 38.1 for NF, 36.9 → 46.6 for DR), as a belief
carried on stale evidence should; the pooled GRAVE cell reads lower
all-states than in sight for both heads (696.6 → 599.7 for NF, 685.2
→ 671.6 for DR), but the two pools differ (all-states admits Pumpkin
and contains the in-sight ticks), so that is not an out-of-sight read
and none was declared.

## R2 — the dissolution test (procedure frozen in the declaration)

Read order: (1) the floor = DR's pooled mind-visible GRAVE loss, mean
of three seeds: **685.15**; (2) NF's, same split and seeds: **696.55**;
(3) ratio 1.017 against the declared tolerance 1.10: the pooled clause
HOLDS. Per-friend clause (NF_grave − 1.10 × DR_grave ≤ NF's between-
seed SD, on the covered friends):

| friend | NF grave | DR grave | excess over 1.10 × DR | NF SD | clause |
|---|---|---|---|---|---|
| Miso | 823.76 | 586.84 | +178.24 | 37.50 | EXCEEDS |
| Biscuit | 573.68 | 891.81 | −407.31 | 18.46 | ok |
| Pumpkin | insufficient | insufficient | — | — | not read |
| Kittybear | 702.18 | 586.98 | +56.51 | 34.01 | EXCEEDS |
| Clementine | 707.33 | 612.29 | +33.81 | 68.96 | ok |

Verdict: **the tension is NOT dissolved** (pooled clause holds, per-
friend clause fails on Miso and Kittybear). Scope, as ruled: this
licenses head choice for Phase 2 only. The shape of the failure is the
finding: the natural-frequency head is not uniformly worse on grave
states (Biscuit's grave loss is 36% lower under NF), it is worse on
specific friends, and pooling hides that. A single head for Phase 2
carries one of two costs: NF's grave loss on Miso and Kittybear (its
grave optimism, R4, is on all four covered friends), or DR's
common-state cost everywhere and its grave cost on Biscuit.

## R3 — trivial baselines beside the floor (reference reads)

Both predict the five hidden needs from training-split statistics:
marginal = each need's training mean (16.4 / 14.3 / 17.3 / 3.8 / 12.7
for eat / drink / sleep / play / cuddle); persistence proxy = the
training mean conditional on the friend's visible activity one-hot and
partner bit (15 possible keys, "not present" one of them; 12 occur in
the training samples).

| cell (pooled, mind-visible) | marginal | persistence proxy | NF | DR |
|---|---|---|---|---|
| COMMON | 77.23 | 74.79 | 29.52 | 36.94 |
| DA | 2,251.26 | 2,243.67 | 611.84 | 581.55 |
| GRAVE | 2,814.09 | 2,809.14 | 696.55 | 685.15 |

Per friend on GRAVE mind-visible the baselines read 2,388–3,168
(marginal) and 2,394–3,160 (proxy). Both heads clear both baselines by
a factor of about four in squared error on the grave stratum, and the
proxy is barely better than the marginal: the friend's visible activity
says almost nothing about how high her hidden needs are. The head's
grave skill is therefore not a lookup on the friend's visible activity
and partner bit (the proxy reads no other row cell and no self block).

## R4 — the ostrich metric (both heads)

Signed bias = predicted − true, mean over the five hidden needs, in
need points; negative = the friend predicted LESS needy than she is.
Ostrich gap = GRAVE-bin bias − COMMON-bin bias. Signature (prereg §8
item 4): |GRAVE bias| ≥ 1.5 × |COMMON bias| with the GRAVE bias
negative. Mean of three seeds.

Mind-visible:

| friend | NF grave / common / gap | DR grave / common / gap |
|---|---|---|
| Miso | −11.66 / −0.40 / −11.26 SIG | −3.59 / −0.41 / −3.18 SIG |
| Biscuit | −5.44 / +0.55 / −5.99 SIG | +10.83 / +0.53 / +10.30 |
| Pumpkin | insufficient | insufficient |
| Kittybear | −9.73 / +0.81 / −10.54 SIG | −2.71 / +0.93 / −3.64 SIG |
| Clementine | −6.93 / −0.67 / −6.26 SIG | −0.39 / −0.82 / +0.43 |
| pooled | −8.56 / +0.03 / −8.59 SIG | +1.57 / −0.02 / +1.59 |

All-states:

| friend | NF grave / common / gap | DR grave / common / gap |
|---|---|---|
| Miso | −9.18 / −0.27 / −8.91 SIG | +1.74 / −0.31 / +2.05 |
| Biscuit | −4.20 / +0.46 / −4.66 SIG | +13.72 / +0.47 / +13.24 |
| Pumpkin | −12.79 / −0.22 / −12.57 SIG | −5.27 / −0.34 / −4.93 SIG |
| Kittybear | −7.07 / +0.75 / −7.82 SIG | +0.86 / +0.87 / −0.01 |
| Clementine | −5.84 / −0.72 / −5.13 SIG | +1.72 / −0.83 / +2.55 |
| pooled | −6.48 / −0.00 / −6.48 SIG | +6.23 / −0.03 / +6.25 |

The natural-frequency head carries the ostrich signature on every
covered friend in both versions and pooled: in grave states it reads
the friend 8.6 points (in sight) and 6.5 points (all states) less needy
than she is, against a common-state bias within 0.9 of zero. The
reweighted head removes the pooled optimism (+1.57 in sight, +6.23 all
states, both on the pessimistic side) and keeps a small signature only
on Miso and Kittybear in sight (−3.6, −2.7) and on Pumpkin all-states
(−5.3); on Biscuit it overshoots to +10.8 / +13.7. The 1.5× lift
is met trivially wherever the common bias is near zero (the lift
values in `phase1-read.json` run from 0.5 to the thousands, the large
ones exactly there), so the gap in points is the informative column;
the signature column reports the rule as written.

## R5 — bath, the visible need (pipeline-noise bound)

Bath is a copy task when the friend is in sight. Pooled MSE, need
points²: NF in sight COMMON 0.92 ± 0.26, GRAVE 27.73 ± 8.35; all
states COMMON 15.64 ± 0.16, GRAVE 219.48 ± 17.57. DR in sight COMMON
3.07 ± 0.45, GRAVE 54.80 ± 8.86; all states COMMON 20.39 ± 0.90,
GRAVE 233.26 ± 1.00. So the pipeline floor is about 1 point RMS (NF,
in sight, common). Bath error rises in grave states although bath is
visible, consistent with the 24-unit state being shared across the
seven outputs (not tested here); and out of sight bath must be
inferred like any other need. Never pooled with R1.

## Not read

Consumers (refusal tax, harm prediction, food yielding): Phase 2's.
clone_fraction (A2′, uncomputable offline). Any welfare claim. No head
with the global state, other friends' rows or the trunk's activations
was trained. No set beyond G was run.

## Regeneration

Arc venv `.venv` (BINDING.md; `A=experiments/minifriend-phase1-2026-10-22`,
run from the repository root; `VIRTUAL_ENV=$PWD/$A/.venv` on every
line). Raws: `results-raw/{L,W,G}/streams-<seed>.npz` (60 worlds) and
`results-raw/heads/{NF,DR}-s{1,2,3}/` (six runs; `DR-s1-smoke/` is a
two-epoch smoke of the writer, never read).

### Collect

```sh
# L, first world then the rest (each 20k ticks ≈ 30 s)
(cd $A && ./run_L.sh 905001 && printf '%s\n' 9050{02..10} | xargs -P 5 -n 1 ./run_L.sh)
# W and G, scouts first; check_set must show no abort before the rest
(cd $A && ./run_set.sh W 1095401 1095402 1095403 && printf '%s\n' 10954{04..25} | xargs -P 5 -n 1 ./run_set.sh W)
(cd $A && ./run_set.sh G 1095426 1095427 1095428 && printf '%s\n' 10954{29..50} | xargs -P 5 -n 1 ./run_set.sh G)
# the six heads (≈ 10 min wall, six in parallel)
(cd $A && caffeinate -s ./run_heads.sh > results-raw/heads/run-all.log 2>&1)
```

### Read

```sh
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/check_L.py --out $A/L-check.json            # ≈ 20 s
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/check_set.py W --out $A/W-check.json        # ≈ 10 s
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/check_set.py G --out $A/G-check.json        # ≈ 10 s
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/count_strata.py --out $A/strata-counts.json # ≈ 30 s
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/read_phase1.py --out $A/phase1-read.json --md  # ≈ 10 s
```

Guards (plain-assert runners, arc venv): `test_strata.py` 2,
`test_count_strata.py` 3, `test_train_heads.py` 5, `test_read_phase1.py`
5; collector guard in `../seating-analysis-g2-2026-10-21/test_seating_g2.py`
(10). Reds on record via `scripts/mutate.sh` in the commit messages
50f4bb27 (collector save-obs; strata edges), 375fd53e (check_L),
ecfde71e (count_strata present cell; check_set band) and this
section's own commit (trainer and data module: weights from the
train worlds only, roles, friend row; truth alignment; the reader's
four).

Accuracy gate: **PASS**, 2026-10-23, round 2 (fresh subagent per
round; round 1 FAILED on prose only: four provenance misses, one
arithmetic ratio, three contradicted characterisations, one weak
claim in the R2 paragraph; every number matched the fresh JSON from
round 1). Round 2: about 300 arithmetic values matched (two rounding
notes), 10 thresholds all sourced, 29 characterisations (26
supported, 3 weak outside decision lines, reworded after the round),
9 undecidable, provenance all hits; fresh JSON byte-identical to the
recorded. Raw-dir hash `v1:14975af6c7118473`
(`scripts/rawdir-hash.sh experiments/minifriend-phase1-2026-10-22/results-raw`).
