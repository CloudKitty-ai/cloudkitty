# Mini-friend Phase 1 — RESULTS (collected and read 2026-10-23 UTC)

Declaration: `DECLARATION.md`, ruled as declared (owner 2026-10-22
"Fix the stale draft and go as declared"); prereg basis frozen
18f06f84, §8 items 3–4 and §9. This is the re-read of 2026-10-23
after the heads were retrained with bath downweighted (deviations
entry 10); the superseded first read is in git at d0de3213. Binding:
`BINDING.md` (the arc's own venv; engine a2e8d044, which is the
certified engine plus spec 065, verified by set L below). Every read
here is descriptive (doctrine rule 10); nothing gates, and the one
procedure pin (R2) licenses head choice for Phase 2 only, never
welfare adequacy.

## Headline

A 7,807-parameter belief head (9.2% of the trunk) reading only what a
Gen 2 cat sees estimates a friend's five hidden needs to a root-mean-
square error of about 5.3 need points when the friend is in sight and
in a common state, and about 25 points in the grave stratum, where the
trivial baselines sit at about 53. The natural-frequency head carries
the ostrich signature on three of the four covered friends: pooled, in
grave states it predicts the friend 3.8 points less needy than she is,
against a bias within 0.9 of zero in common states. Distress
reweighting removes that pooled optimism (grave bias +1.7) at a cost of
7.5 points² of common-state error and is pooled WORSE on grave loss
(ratio NF/DR 0.944). The declared dissolution test still FAILS on its
per-friend clause, on one friend: Miso's grave loss under NF exceeds
1.10 × DR's by 96.76 against a between-seed SD of 79.56; Biscuit's goes
the other way by 401.27. The tension is present, friend-specific and
narrow. Pumpkin's mind-visible grave stratum stayed under min-n after
every declared set and is reported as insufficient coverage.

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
(the fewest G distress ticks, 763). The retrain added no rollout.

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
exists in W (cats that start outside GRAVE and enter it later) and as
re-entries in G (cats relieved early that slide back), and in no lived
world (L has no grave tick). The second is seen in the
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
plus 0.1 × bath (targets /100; bath DOWNWEIGHTED per prereg §8 item
3, so the seventh output is fitted enough to report in R5 without
driving the shared state; a first pass that fitted bath at weight 1
is superseded, kept unread under `results-raw/heads-pass1/`,
deviations entry 10); NF weight 1; DR weight by the friend's true
stratum on the training samples, inverse frequency capped at 50× the
common stratum's and renormalised to mean 1: training frequencies
GRAVE 0.00309, ADJACENT 0.00209, COMMON 0.99482 → weights 39.87 /
39.87 / 0.797 (the cap binds on both rare strata). Adam 1e-3; early
stop on the validation loss (margin 1e-4, patience 10, cap 200). Seeds
1, 2, 3, the NF/DR pair sharing each.

| run | best epoch / epochs run | best validation loss |
|---|---|---|
| NF-s1 | 85 / 95 | 0.00478 |
| NF-s2 | 74 / 84 | 0.00497 |
| NF-s3 | 71 / 81 | 0.00509 |
| DR-s1 | 55 / 65 | 0.01931 |
| DR-s2 | 47 / 57 | 0.01918 |
| DR-s3 | 74 / 84 | 0.02005 |

Every run plateaued before the cap. (The DR validation loss is DR-
weighted, so the two columns are not comparable across heads.)

## R1 — the 2 × 2, mean squared error on the five hidden needs (need points²)

Mean ± SD over three seeds; per friend then pooled (sample-weighted
over covered friends). The prereg's distress-adjacent column is DA;
GRAVE alone beside it. Square roots are the RMS error in need points.

Mind-visible (the friend's row present):

| friend | NF COMMON | NF DA | NF GRAVE | DR COMMON | DR DA | DR GRAVE |
|---|---|---|---|---|---|---|
| Miso | 27.44 ± 0.56 | 668.74 ± 83.36 | 714.98 ± 79.56 | 32.99 ± 1.14 | 538.76 ± 20.07 | 562.02 ± 32.12 |
| Biscuit | 26.96 ± 0.75 | 637.43 ± 33.06 | 590.14 ± 42.50 | 35.12 ± 2.48 | 883.43 ± 110.43 | 901.28 ± 152.95 |
| Pumpkin | 29.42 ± 1.41 | 319.02 ± 19.60 | insufficient | 37.50 ± 2.52 | 308.22 ± 13.88 | insufficient |
| Kittybear | 24.91 ± 1.01 | 645.61 ± 68.80 | 626.66 ± 86.95 | 33.01 ± 2.76 | 564.58 ± 52.05 | 575.47 ± 61.61 |
| Clementine | 32.37 ± 1.19 | 495.41 ± 20.18 | 659.15 ± 76.75 | 40.17 ± 2.43 | 479.86 ± 26.57 | 643.48 ± 83.79 |
| pooled | 28.25 ± 0.93 | 569.99 ± 23.09 | 644.04 ± 30.61 | 35.78 ± 2.21 | 573.79 ± 5.24 | 682.11 ± 19.77 |

All-states (every tick, seen or not):

| friend | NF COMMON | NF DA | NF GRAVE | DR COMMON | DR DA | DR GRAVE |
|---|---|---|---|---|---|---|
| Miso | 35.99 ± 0.88 | 662.80 ± 34.61 | 695.11 ± 43.29 | 43.14 ± 1.34 | 566.90 ± 16.27 | 573.55 ± 17.70 |
| Biscuit | 35.35 ± 0.92 | 524.89 ± 51.95 | 506.38 ± 56.37 | 44.79 ± 2.29 | 764.11 ± 152.02 | 768.25 ± 169.37 |
| Pumpkin | 37.97 ± 1.16 | 423.70 ± 26.86 | 571.32 ± 20.92 | 46.47 ± 2.50 | 388.47 ± 0.98 | 489.74 ± 34.67 |
| Kittybear | 32.96 ± 1.08 | 608.39 ± 44.35 | 582.26 ± 54.66 | 42.40 ± 2.59 | 626.69 ± 46.96 | 617.21 ± 61.24 |
| Clementine | 41.46 ± 1.24 | 591.65 ± 23.61 | 675.85 ± 33.81 | 49.92 ± 2.42 | 572.54 ± 24.95 | 653.55 ± 59.89 |
| pooled | 36.75 ± 1.04 | 567.75 ± 28.50 | 583.93 ± 40.25 | 45.35 ± 2.15 | 625.55 ± 49.82 | 668.47 ± 66.22 |

What the table says. (a) Common states are estimated well: pooled
mind-visible RMS error 5.3 points (NF) and 6.0 (DR). (b) The grave
stratum is 19 to 23 times harder in squared error (682.11 / 35.78 for
DR, 644.04 / 28.25 for NF): pooled mind-visible RMS 25.4 (NF) and 26.1
(DR). (c) Reweighting costs common-state accuracy on every friend
(+5.6 to +8.2 points² mind-visible) and buys grave accuracy on three
of the four covered friends (Miso −152.96, Kittybear −51.19,
Clementine −15.67 points² mind-visible) while losing it on Biscuit
(+311.14); pooled, NF is LOWER on GRAVE (644 vs 682) and the two tie
on DA (570 vs 574). (d) Mind-visible versus all-states: common-state
error rises when the friend is out of sight (28.2 → 36.8 for NF, 35.8
→ 45.4 for DR), as a belief carried on stale evidence should; the
pooled GRAVE cell reads lower all-states than in sight for both heads
(644.0 → 583.9 for NF, 682.1 → 668.5 for DR), but the two pools
differ (all-states admits Pumpkin and contains the in-sight ticks), so
that is not an out-of-sight read and none was declared.

## R2 — the dissolution test (procedure frozen in the declaration)

Read order: (1) the floor = DR's pooled mind-visible GRAVE loss, mean
of three seeds: **682.11**; (2) NF's, same split and seeds: **644.04**;
(3) ratio 0.944 against the declared tolerance 1.10: the pooled clause
HOLDS (NF under the floor). Per-friend clause (NF_grave − 1.10 ×
DR_grave ≤ NF's between-seed SD, on the covered friends):

| friend | NF grave | DR grave | excess over 1.10 × DR | NF SD | clause |
|---|---|---|---|---|---|
| Miso | 714.98 | 562.02 | +96.76 | 79.56 | EXCEEDS |
| Biscuit | 590.14 | 901.28 | −401.27 | 42.50 | ok |
| Pumpkin | insufficient | insufficient | — | — | not read |
| Kittybear | 626.66 | 575.47 | −6.36 | 86.95 | ok |
| Clementine | 659.15 | 643.48 | −48.67 | 76.75 | ok |

Verdict: **the tension is NOT dissolved** (pooled clause holds, per-
friend clause fails on Miso, by 17.20 over her SD). Scope, as ruled:
this licenses head choice for Phase 2 only. The shape of the result is
the finding: pooled, the natural-frequency head is the better grave
estimator; the reweighted head is better on Miso (and marginally on
Kittybear and Clementine) and far worse on Biscuit (its grave loss is
35% lower under NF). A single head for Phase 2 carries one of two
costs: NF's grave loss on Miso (its grave optimism, R4, is on Miso,
Kittybear and Clementine), or DR's common-state cost everywhere and
its grave cost on Biscuit.

## R3 — trivial baselines beside the floor (reference reads)

Both predict the five hidden needs from training-split statistics:
marginal = each need's training mean (16.4 / 14.3 / 17.3 / 3.8 / 12.7
for eat / drink / sleep / play / cuddle); persistence proxy = the
training mean conditional on the friend's visible activity one-hot and
partner bit (15 possible keys, "not present" one of them; 12 occur in
the training samples).

| cell (pooled, mind-visible) | marginal | persistence proxy | NF | DR |
|---|---|---|---|---|
| COMMON | 77.23 | 74.79 | 28.25 | 35.78 |
| DA | 2,251.26 | 2,243.67 | 569.99 | 573.79 |
| GRAVE | 2,814.09 | 2,809.14 | 644.04 | 682.11 |

Per friend on GRAVE mind-visible the baselines read 2,388–3,168
(marginal) and 2,394–3,160 (proxy). Both heads clear both baselines by
a factor of about four in squared error on the grave stratum (4.4 for
NF, 4.1 for DR), and the proxy is barely better than the marginal: the
friend's visible activity says almost nothing about how high her
hidden needs are. The head's grave skill is therefore not a lookup on
the friend's visible activity and partner bit (the proxy reads no
other row cell and no self block).

## R4 — the ostrich metric (both heads)

Signed bias = predicted − true, mean over the five hidden needs, in
need points; negative = the friend predicted LESS needy than she is.
Ostrich gap = GRAVE-bin bias − COMMON-bin bias. Signature (prereg §8
item 4): |GRAVE bias| ≥ 1.5 × |COMMON bias| with the GRAVE bias
negative. Mean of three seeds.

Mind-visible:

| friend | NF grave / common / gap | DR grave / common / gap |
|---|---|---|
| Miso | −7.61 / −0.17 / −7.44 SIG | −3.21 / −0.11 / −3.10 SIG |
| Biscuit | +0.59 / +0.61 / −0.01 | +10.16 / +0.84 / +9.31 |
| Pumpkin | insufficient | insufficient |
| Kittybear | −5.54 / +0.88 / −6.42 SIG | −2.01 / +1.19 / −3.20 SIG |
| Clementine | −2.48 / −0.63 / −1.84 SIG | +0.00 / −0.42 / +0.42 |
| pooled | −3.80 / +0.12 / −3.92 SIG | +1.71 / +0.31 / +1.39 |

All-states:

| friend | NF grave / common / gap | DR grave / common / gap |
|---|---|---|
| Miso | −4.13 / −0.09 / −4.04 SIG | +0.76 / +0.04 / +0.72 |
| Biscuit | +2.94 / +0.57 / +2.36 | +12.55 / +0.84 / +11.71 |
| Pumpkin | −8.38 / −0.13 / −8.25 SIG | −5.72 / +0.06 / −5.78 SIG |
| Kittybear | −2.66 / +0.87 / −3.53 SIG | +1.57 / +1.21 / +0.36 |
| Clementine | −1.49 / −0.66 / −0.83 SIG | +1.63 / −0.43 / +2.05 |
| pooled | −0.80 / +0.11 / −0.91 SIG | +5.64 / +0.34 / +5.30 |

The natural-frequency head carries the ostrich signature on three of
the four covered friends in sight (Miso, Kittybear, Clementine; not
Biscuit, whose grave bias is +0.59) and pooled: in grave states it
reads the friend 3.8 points less needy than she is in sight, against
a common-state bias within 0.9 of zero; all-states the pooled bias
shrinks to −0.80 (the signature flag still fires by the rule, on a
gap of 0.91 points). The reweighted head removes the pooled optimism
(+1.71 in sight, +5.64 all states, both on the pessimistic side) and
keeps a small signature on Miso and Kittybear in sight (−3.21, −2.01)
and on Pumpkin all-states (−5.72); on Biscuit it overshoots to +10.16
/ +12.55. The 1.5× lift is met trivially wherever the common bias is
near zero (the lift values in `phase1-read.json` run from 0.01 to 96,
the large ones exactly there), so the gap in points is the informative
column; the signature column reports the rule as written.

## R5 — bath, the visible need (pipeline-noise bound)

Bath is a copy task when the friend is in sight, fitted here at
weight 0.1 (R6). Pooled MSE, need points²: NF in sight COMMON 3.99 ±
0.67, GRAVE 138.56 ± 36.13; all states COMMON 21.16 ± 0.83, GRAVE
422.50 ± 29.44. DR in sight COMMON 28.15 ± 7.35, GRAVE 335.09 ±
134.33; all states COMMON 36.05 ± 2.55, GRAVE 433.72 ± 48.21. So the
pipeline floor under a downweighted output is about 2 points RMS (NF,
in sight, common). Bath error rises in grave states although bath is
visible, consistent with the 24-unit state being shared across the
seven outputs and a 0.1-weight output yielding first (not tested
here); out of sight bath must be inferred like any other need. Never
pooled with R1.

## Not read

Consumers (refusal tax, harm prediction, food yielding): Phase 2's.
clone_fraction (A2′, uncomputable offline). Any welfare claim. No head
with the global state, other friends' rows or the trunk's activations
was trained. No set beyond G was run. The superseded first pass
(`results-raw/heads-pass1/`) is not read.

## Regeneration

Arc venv `.venv` (BINDING.md; `A=experiments/minifriend-phase1-2026-10-22`,
run from the repository root; `VIRTUAL_ENV=$PWD/$A/.venv` on every
line). Raws: `results-raw/{L,W,G}/streams-<seed>.npz` (60 worlds) and
`results-raw/heads/{NF,DR}-s{1,2,3}/` (the six runs read here;
`results-raw/heads-pass1/` holds the superseded bath-at-1.0 pass and
its two-epoch smoke `DR-s1-smoke/`, never read).

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
ecfde71e (count_strata present cell; check_set band), d0de3213
(trainer and data module: weights from the train worlds only, roles,
friend row; truth alignment; the reader's four) and 0bcd7158's
follow-up in this section's own commit (the bath weight).

Accuracy gate: **PASS**, 2026-10-23, round 4 (fresh subagent per
round). History: rounds 1–2 gated the superseded bath-at-1.0 read
(round 1 FAIL on prose, round 2 PASS; committed d0de3213); the F-064
copy check then found the loss slip (deviations entry 10) and the
heads were retrained; round 3 on this re-read FAILED on one
mechanical miss (the reader's guard runner pointed at the moved smoke
run; repointed at a real run) with every number matching; round 4
PASS: about 250 numbers matched (two rounding notes in R1(d)), 11
thresholds sourced, about 16 characterisations all supported, 1
undecidable (the hedged R5 mechanism), provenance all hits, five
guard runners at their stated counts (2 / 3 / 5 / 5 / 10), fresh JSON
byte-identical to the recorded. Raw-dir hash `v1:b693200d5f159e90`
(`scripts/rawdir-hash.sh experiments/minifriend-phase1-2026-10-22/results-raw`,
covering the 60 worlds, the six runs read and the superseded pass).
