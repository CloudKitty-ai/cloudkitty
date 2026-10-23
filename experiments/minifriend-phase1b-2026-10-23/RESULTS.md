# Mini-friend Phase 1b — RESULTS (collected and read 2026-10-23 UTC)

Declaration: `DECLARATION.md`, ruled as declared (owner 2026-10-23 "No
need to change the declaration. Let's run this as proposed"); her ask
of the same day quoted in the declaration's header; deviations entry
11. Prereg basis frozen 18f06f84, §8 items 3–4. Binding: Phase 1's arc
venv (`../minifriend-phase1-2026-10-22/BINDING.md`; engine a2e8d044,
the certified engine plus spec 065). Every read is descriptive
(doctrine rule 10); nothing gates. Phase 1's floor, verdicts and F-064
stand; nothing here re-reads them.

## Headline

With one friend grave at reset and her four observers at the served
default, the grave estimate is harder than Phase 1's all-grave worlds
showed. At Phase 1's width (24) the pooled mind-visible grave MSE on
the per-cat worlds is 908.10 for the natural-frequency head (RMS 30.1
need points) against 591.58 on the all-grave worlds read by the same
heads: the all-grave worlds were about a third easier in squared error
(R5b, q = 0.651 ± 0.033, READ), which puts a number on Phase 1's second
limitation. Width moves every cell in one direction, beyond seed noise
on every NF cell and on the DR cells at 48 over 24 (DR's 12-over-24
ratios fall inside its wider seed spread): NF grave loss 1098.53 /
908.10 / 790.22 at widths 12 / 24 / 48 (ratios to 24 of 1.210 ± 0.070
and 0.870 ± 0.053, both READ), DR 924.87 / 827.69 / 684.51 (1.117 ±
0.231 not READ, 0.827 ± 0.124 READ). Common-state cells move
by a similar ratio for NF (0.884 ± 0.022 at 48) and, on the means, a
larger one for DR (0.767 ± 0.163 against 0.827 ± 0.124, inside the
SDs), so in proportion the size effect is not grave-specific; in points² the grave stratum gains
most (117.88 for NF and 143.18 for DR from 24 to 48, against 2.94 and
9.35 in common states). The cap binds: capacity above the 8,445 budget
buys 13% (NF) to 17% (DR) of grave loss at this geometry, and the
over-cap head stays a probe. The ostrich signature is broader and
deeper in this register than in Phase 1: NF's pooled grave bias in
sight is −10.10 points at width 24 (Phase 1: −3.80), the signature
fires on four of the five friends (all but Clementine, whose grave bias
is +2.27), and distress reweighting no longer removes the pooled
optimism (DR −7.57; Phase 1: +1.71). The dissolution procedure fails at
every width, and the reweighted head is pooled BETTER on grave loss at
every width here (NF/DR 1.188, 1.097, 1.154), the reverse of Phase 1's
read on its own evaluation worlds (0.944; its grave samples mostly
from the all-grave set G, about a tenth from W). Pumpkin, insufficient in Phase 1, is covered
(398 mind-visible grave samples) and reads among the easier three
friends at every width.

## Data as collected

| set | worlds | ticks | covered cat-ticks | aborts | distress ticks (Miso / Biscuit / Pumpkin / Kittybear / Clementine) | worst single-need streak | streaks ≥ 150 (F-043 crossings) |
|---|---|---|---|---|---|---|---|
| P1 (Miso alone grave at reset; 1095451–1095470, `g2leg-20-P1.toml`) | 20 | 4,000 | 400,000 | 0 | 1,641 / 0 / 0 / 0 / 0 | 321 | Miso 1095451 (163), 1095453 (321), 1095459 (159) |
| P2 (Biscuit; 1095471–1095490, `-P2.toml`) | 20 | 4,000 | 400,000 | 0 | 0 / 1,357 / 0 / 0 / 0 | 601 | Biscuit 1095486 (601) |
| P3 (Pumpkin; 1095491–1095510, `-P3.toml`) | 20 | 4,000 | 400,000 | 0 | 0 / 0 / 828 / 0 / 0 | 63 | none |
| P4 (Kittybear; 1095511–1095530, `-P4.toml`) | 20 | 4,000 | 400,000 | 0 | 0 / 0 / 0 / 1,105 / 0 | 173 | Kittybear 1095525 (173) |
| P5 (Clementine; 1095531–1095550, `-P5.toml`) | 20 | 4,000 | 400,000 | 0 | 0 / 0 / 0 / 0 / 950 | 79 | none |

Sets L, W and G are Phase 1's recorded worlds, read through symlinks
under `results-raw/` (no rollout was added to them). Every P world
seats the certified roster rot2 (greedy masked argmax, served clock,
schema 6 observations, the served 20×20 as in Phase 1) on its set's
own config: the served
`g2leg-20.toml` plus one `initial_needs` line inside kitty k's
`[[kitty]]` block (every need drawn in {60, 95}, spec 065's per-kitty
× per-need draws; `make_configs.py`, guard s2). The F-053 stop (streak
1,000) was armed on every world; scouts first, one world per friend
(the first seed of each block), read with `check_P.py` before the rest
were launched. `P-check.json` holds every world's reset state: the
grave kitty's six needs inside the band and varying, the other four
kitties exactly at the served default (every need 0, happiness 100).

Welfare line, actual: 2,000,000 covered cat-ticks against the declared
ceiling of 4.0M, 400,000 of them cat-ticks from the 100 grave-start cat-episodes
(one cat per world) against the 0.8M ceiling; the extension blocks X1..X5 were not
run (coverage below); 0 aborts; the F-053 line never reached; five
streaks ≥ 150, all under it; distress confined to the grave kitty in
all 100 worlds. The grave kitty's reset happiness: mean 21.4–22.4 per
set, lowest 14.1 (Biscuit, P2), highest 29.5. Each seat's run-mean
happiness, averaged over a set's 20 worlds, stays 86.2–88.2 in every
set (the grave seat's own: Miso 86.7, Biscuit 87.2, Pumpkin 86.2,
Kittybear 87.4, Clementine 86.3): the roster relieves a single
distressed start as it relieved Phase 1's wide and all-grave starts
(W and G together: 86.2–88.0).
Pumpkin's seat again relieves fastest (828 distress ticks over 20
worlds, the fewest); Biscuit's carries the one long streak (601).

## Samples and coverage (group P evaluation worlds)

Split by world (`split.json`, seed 20261023; L/W/G verbatim from Phase
1's split, guard s1): 50 P evaluation worlds (ten per set; the lists
are in `split.json` and in the read's `eval_worlds`), 4,000,000
samples. Non-evaluation worlds: Phase 1's 41 (L, W, G) plus 50 P worlds;
validation re-carved from all of them under this arc's split seed
(round(0.2·n) per set): 34 + 40 training worlds, 7 + 10 validation
(two P worlds per set). Because the carve is seeded by this arc's
split seed (20261023), the L/W/G validation worlds differ from Phase
1's (L 905003; W 1095414, 1095418, 1095421; G 1095431, 1095436,
1095438), so the width-24 heads here differ from Phase 1's in the
validation carve as well as in the training data. Phase 1's G evaluation worlds (eight)
form group G, read for R5b and for the grave-only note in R3b.

Coverage per friend on group P (mind-visible / all-states;
`strata-counts.json`, `phase1b-read.json`):

| friend | GRAVE | DA (GRAVE ∪ ADJACENT) | GRAVE reads |
|---|---|---|---|
| Miso | 572 / 2,440 | 713 / 2,832 | both versions |
| Biscuit | 364 / 1,760 | 478 / 2,184 | both versions |
| Pumpkin | 398 / 2,108 | 672 / 3,076 | both versions |
| Kittybear | 933 / 3,224 | 1,164 / 4,164 | both versions |
| Clementine | 260 / 1,972 | 489 / 2,644 | both versions |

Every friend clears min-n 200 mind-visible after P alone, so the
extension clause did not fire and no friend is insufficient coverage;
Pumpkin, insufficient in Phase 1 (170), is covered here (398). In P a
friend's GRAVE spell is the start of her episode: 2,440 all-states
GRAVE samples for Miso over 40 observer-episodes is about 61 grave
ticks per observer-episode (a count, not a timing) before the roster
relieves her, against the whole-roster grave openings of G. A grave friend is in an observer's
sight for 13–29% of her grave ticks (Clementine 260 / 1,972 to
Kittybear 933 / 3,224).

What P changes about the grave read. In G every cat started grave
together, so an observer's own needs predicted the friend's at the
start (Phase 1's second limitation). In P the observer starts at the
served default (every need 0) while the friend starts grave: the
observer's self block carries no such cue, and the grave estimate has
to come from the friend's row. Each friend's grave stratum also
arrives with a different observer mix: it is read by the other four
seats, who never go grave themselves (they do pass through ADJACENT:
216 Clementine friend-samples in P3, 180 Pumpkin in P5).

## Heads (R6b)

`train_heads.py --hidden h`: Linear(167 → h) + ReLU, GRU(h), Linear(h →
7); **3,043 / 7,807 / 22,519 parameters** at h = 12 / 24 / 48 against
the §8 item 4 cap of 8,445 (10% of the trunk's 84,450). Width 24 is
Phase 1's head retrained on the enlarged training set; width 48 is 2.7×
the cap, accepted only under `--over-cap`, marked `over_cap: true` in
every one of its six manifests, and never a Phase 2 candidate. Inputs,
targets, loss (bath at 0.1), optimiser and early stopping as in Phase 1
(its RESULTS §Heads). Training set: 34 L/W/G worlds plus 40 P training
worlds; validation 7 L/W/G plus 10 P worlds, re-carved under this arc's
split seed (§Samples; not Phase 1's seven). DR weights recomputed on this training set: GRAVE / ADJACENT
/ COMMON 41.013 / 41.013 / 0.820 (the 50× cap binds on both rare
strata; Phase 1: 39.87 / 39.87 / 0.797). Seeds 1, 2, 3, the NF/DR pair
sharing each.

| run | params | best epoch / epochs run | best validation loss |
|---|---|---|---|
| NF-h12-s1 | 3,043 | 63 / 73 | 0.00545 |
| NF-h12-s2 | 3,043 | 68 / 78 | 0.00550 |
| NF-h12-s3 | 3,043 | 72 / 82 | 0.00535 |
| DR-h12-s1 | 3,043 | 39 / 49 | 0.02231 |
| DR-h12-s2 | 3,043 | 22 / 32 | 0.02517 |
| DR-h12-s3 | 3,043 | 23 / 33 | 0.02788 |
| NF-h24-s1 | 7,807 | 59 / 69 | 0.00465 |
| NF-h24-s2 | 7,807 | 68 / 78 | 0.00456 |
| NF-h24-s3 | 7,807 | 65 / 75 | 0.00470 |
| DR-h24-s1 | 7,807 | 39 / 49 | 0.02033 |
| DR-h24-s2 | 7,807 | 22 / 32 | 0.02149 |
| DR-h24-s3 | 7,807 | 21 / 31 | 0.02347 |
| NF-h48-s1 | 22,519 (over cap) | 52 / 62 | 0.00423 |
| NF-h48-s2 | 22,519 (over cap) | 54 / 64 | 0.00421 |
| NF-h48-s3 | 22,519 (over cap) | 57 / 67 | 0.00420 |
| DR-h48-s1 | 22,519 (over cap) | 53 / 63 | 0.01803 |
| DR-h48-s2 | 22,519 (over cap) | 22 / 32 | 0.02036 |
| DR-h48-s3 | 22,519 (over cap) | 40 / 50 | 0.01916 |

Every run plateaued before the 200-epoch cap. The DR runs stop earlier
and vary more between seeds (best epoch 21–53 against NF's 52–72),
and their between-seed SDs below are correspondingly wider. (The DR
validation loss is DR-weighted; the columns are not comparable across
heads.) Wall clock: widths 12 / 24 / 48 took 12 / 14 / 17 minutes with
six runs in parallel.

## R1b — accuracy by width, group P (mean squared error on the five hidden needs, need points²)

Mean ± SD over three seeds; per friend then pooled (sample-weighted
over the five friends, all covered). DA = GRAVE ∪ ADJACENT; GRAVE
alone beside it. Square roots are RMS error in need points.

Mind-visible, width 12:

| friend | NF COMMON | NF DA | NF GRAVE | DR COMMON | DR DA | DR GRAVE |
|---|---|---|---|---|---|---|
| Miso | 29.78 ± 1.96 | 693.62 ± 18.30 | 746.20 ± 29.91 | 49.43 ± 6.66 | 628.14 ± 156.71 | 648.84 ± 173.77 |
| Biscuit | 28.26 ± 1.17 | 1244.52 ± 79.59 | 1400.75 ± 107.04 | 49.20 ± 7.98 | 1019.41 ± 19.02 | 1096.65 ± 34.62 |
| Pumpkin | 31.69 ± 1.32 | 796.54 ± 30.84 | 914.71 ± 17.99 | 52.40 ± 8.12 | 672.09 ± 73.12 | 798.03 ± 113.26 |
| Kittybear | 26.26 ± 1.11 | 1174.61 ± 149.12 | 1343.05 ± 198.26 | 47.29 ± 7.92 | 970.73 ± 189.16 | 1081.74 ± 226.98 |
| Clementine | 35.69 ± 1.08 | 625.59 ± 45.35 | 854.43 ± 111.16 | 58.74 ± 7.32 | 699.02 ± 24.83 | 922.90 ± 28.28 |
| pooled | 30.39 ± 1.26 | 937.96 ± 31.63 | 1098.53 ± 48.58 | 51.48 ± 7.58 | 813.01 ± 106.25 | 924.87 ± 139.56 |

Mind-visible, width 24 (Phase 1's head, retrained):

| friend | NF COMMON | NF DA | NF GRAVE | DR COMMON | DR DA | DR GRAVE |
|---|---|---|---|---|---|---|
| Miso | 24.94 ± 0.65 | 591.45 ± 103.01 | 613.31 ± 78.46 | 38.41 ± 5.91 | 463.62 ± 78.62 | 480.05 ± 84.11 |
| Biscuit | 24.05 ± 0.81 | 1089.56 ± 10.04 | 1245.18 ± 19.55 | 37.71 ± 6.14 | 933.72 ± 57.87 | 1011.13 ± 66.77 |
| Pumpkin | 26.77 ± 0.71 | 617.52 ± 37.89 | 714.87 ± 22.05 | 41.41 ± 7.00 | 631.73 ± 51.23 | 697.68 ± 93.75 |
| Kittybear | 21.86 ± 0.44 | 940.47 ± 85.83 | 1081.52 ± 111.77 | 36.78 ± 7.08 | 898.86 ± 196.41 | 1021.69 ± 218.83 |
| Clementine | 28.93 ± 0.20 | 545.12 ± 26.74 | 758.16 ± 72.85 | 46.18 ± 8.13 | 616.86 ± 56.80 | 838.55 ± 49.32 |
| pooled | 25.34 ± 0.52 | 773.25 ± 20.58 | 908.10 ± 33.43 | 40.15 ± 6.85 | 725.06 ± 97.39 | 827.69 ± 117.06 |

Mind-visible, width 48 (over-cap probe):

| friend | NF COMMON | NF DA | NF GRAVE | DR COMMON | DR DA | DR GRAVE |
|---|---|---|---|---|---|---|
| Miso | 21.97 ± 0.66 | 484.84 ± 66.23 | 522.94 ± 74.78 | 29.28 ± 4.34 | 406.90 ± 60.84 | 423.88 ± 59.63 |
| Biscuit | 20.98 ± 0.24 | 854.74 ± 64.60 | 969.67 ± 82.02 | 29.58 ± 3.89 | 855.11 ± 67.95 | 933.20 ± 75.40 |
| Pumpkin | 23.58 ± 0.53 | 567.27 ± 36.63 | 674.19 ± 33.73 | 32.80 ± 3.70 | 506.08 ± 48.41 | 548.79 ± 44.87 |
| Kittybear | 19.36 ± 0.38 | 861.53 ± 37.22 | 983.31 ± 34.38 | 27.65 ± 3.41 | 706.84 ± 28.67 | 808.63 ± 45.43 |
| Clementine | 25.97 ± 0.13 | 449.82 ± 42.10 | 611.70 ± 67.88 | 34.53 ± 4.13 | 489.34 ± 70.35 | 672.07 ± 92.11 |
| pooled | 22.40 ± 0.31 | 670.72 ± 32.07 | 790.22 ± 38.88 | 30.80 ± 3.88 | 597.56 ± 38.59 | 684.51 ± 33.26 |

All-states (every tick, seen or not), pooled rows; the per-friend
all-states tables are in `phase1b-read.md`:

| width | NF COMMON | NF DA | NF GRAVE | DR COMMON | DR DA | DR GRAVE |
|---|---|---|---|---|---|---|
| 12 | 38.25 ± 1.02 | 941.89 ± 35.57 | 1062.98 ± 43.33 | 66.88 ± 8.71 | 734.53 ± 93.34 | 789.04 ± 115.78 |
| 24 | 33.68 ± 0.54 | 795.12 ± 19.89 | 894.45 ± 21.77 | 54.48 ± 8.30 | 680.36 ± 59.05 | 729.70 ± 65.46 |
| 48 | 30.73 ± 0.38 | 710.53 ± 50.49 | 796.99 ± 60.87 | 42.98 ± 5.54 | 591.30 ± 26.32 | 633.73 ± 23.24 |

Baselines on group P (pooled, mind-visible / all-states; training-split
statistics, the same at every width): marginal COMMON 75.10 / 78.84, DA
2,751.25 / 2,995.87, GRAVE 3,264.16 / 3,422.93; persistence proxy
COMMON 72.67 / 77.59, DA 2,749.84 / 2,978.35, GRAVE 3,261.15 / 3,402.49.

What the tables say. (a) Common states at width 24: pooled mind-visible
RMS 5.0 points (NF) and 6.3 (DR), close to Phase 1's 5.3 and 6.0 on its
own evaluation worlds. (b) For NF the grave stratum in this register is
about 36 times harder than common in squared error at every width
(1098.53 / 30.39, 908.10 / 25.34, 790.22 / 22.40 = 36.1, 35.8, 35.3;
Phase 1's NF on its own evaluation worlds: 23): pooled mind-visible grave RMS
33.1 / 30.1 / 28.1 points for NF and 30.4 / 28.8 / 26.2 for DR at 12 /
24 / 48, against baselines at 57.1. Both heads clear both baselines by
a factor of 3.0 to 4.8 on grave (against the marginal: NF 2.97 / 3.59
/ 4.13, DR 3.53 / 3.94 / 4.77). (c) The friends split into a harder pair and an easier three
at every width: Biscuit and Kittybear read grave loss of 1,000 or more
at width 24 under either head (1245.18 / 1081.52 NF, 1011.13 / 1021.69
DR), Miso, Pumpkin and Clementine 480–839 (NF alone 613–758). In Phase 1's read
Biscuit was the friend NF read best (590.14); here she is the
one it reads worst at widths 12 and 24 (Kittybear at 48, 983.31
against 969.67). (d) Reweighting costs common-state accuracy at
every width (+21.09, +14.81, +8.40 points² pooled mind-visible at 12 /
24 / 48, narrowing as the head widens) and buys grave accuracy pooled
at every width (−173.66, −80.41, −105.71 points²), on four friends at
every width and never on Clementine (+68.47, +80.39, +60.37). (e) Mind-visible
versus all-states: common error rises out of sight at every width
(25.34 → 33.68 NF, 40.15 → 54.48 DR at width 24), as in Phase 1; the
grave cell reads lower all-states than in sight for DR at every width
and for NF at 12 and 24 (908.10 → 894.45, 827.69 → 729.70 at 24; NF at
48 reads 790.22 → 796.99, higher), and as in Phase 1 the two pools
differ (all-states contains the in-sight ticks), so
that is not an out-of-sight read.

## R2b — the size effect

r(h) = pooled loss at width h over the loss at width 24, per head ×
class × version; SD by first-order propagation, r · √(cv_h² + cv_24²);
READ when |r − 1| exceeds that SD (descriptive; no bar). Group P.

Mind-visible:

| head | class | w12 | w24 | w48 | r(12/24) | r(48/24) |
|---|---|---|---|---|---|---|
| NF | GRAVE | 1098.53 ± 48.58 | 908.10 ± 33.43 | 790.22 ± 38.88 | 1.210 ± 0.070 READ | 0.870 ± 0.053 READ |
| NF | DA | 937.96 ± 31.63 | 773.25 ± 20.58 | 670.72 ± 32.07 | 1.213 ± 0.052 READ | 0.867 ± 0.047 READ |
| NF | COMMON | 30.39 ± 1.26 | 25.34 ± 0.52 | 22.40 ± 0.31 | 1.199 ± 0.055 READ | 0.884 ± 0.022 READ |
| DR | GRAVE | 924.87 ± 139.56 | 827.69 ± 117.06 | 684.51 ± 33.26 | 1.117 ± 0.231 | 0.827 ± 0.124 READ |
| DR | DA | 813.01 ± 106.25 | 725.06 ± 97.39 | 597.56 ± 38.59 | 1.121 ± 0.210 | 0.824 ± 0.123 READ |
| DR | COMMON | 51.48 ± 7.58 | 40.15 ± 6.85 | 30.80 ± 3.88 | 1.282 ± 0.289 | 0.767 ± 0.163 READ |

All-states (ratios; the losses are in R1b's pooled table):

| head | class | r(12/24) | r(48/24) |
|---|---|---|---|
| NF | GRAVE | 1.188 ± 0.056 READ | 0.891 ± 0.071 READ |
| NF | DA | 1.185 ± 0.054 READ | 0.894 ± 0.067 READ |
| NF | COMMON | 1.136 ± 0.035 READ | 0.912 ± 0.018 READ |
| DR | GRAVE | 1.081 ± 0.186 | 0.868 ± 0.084 READ |
| DR | DA | 1.080 ± 0.166 | 0.869 ± 0.085 READ |
| DR | COMMON | 1.228 ± 0.246 | 0.789 ± 0.158 READ |

Monotone in width on every cell of both heads, both versions. For NF
every ratio is READ: halving the width costs about 20% of the loss
(1.199–1.213 in sight), doubling it past the cap buys about 12–13%
(0.867–0.884). For DR the 48/24 ratios are READ on every cell
(0.767–0.827 in sight) and the 12/24 ratios are not, because DR's
between-seed spread, propagated into the ratio, exceeds the width
difference (on grave, SD 117.06 on the width-24 cell against a width
difference of 97.18; on common the single-cell SDs are under the
difference and the propagated ratio SD, 0.289, is not). The cap-binds question, r(48) on GRAVE: READ
under 1 for both heads (0.870 ± 0.053, 0.827 ± 0.124), so capacity
above the 8,445 budget buys grave accuracy at this geometry. It buys
common-state accuracy in a similar proportion for NF (0.884 against
0.870) and, on the means, a larger one for DR (0.767 against 0.827,
inside the SDs): the size effect
is a general one, not a grave-specific one. In points
the grave stratum gains most because it is the largest cell: NF grave
RMS 30.1 → 28.1, common 5.0 → 4.7, from 24 to 48. Nothing here moves
the cap; a wider Phase 2 head is a deviations entry on the owner's
word, with this table as its evidence.

## R3b — the dissolution procedure at each width (information)

Phase 1's R2 procedure verbatim on group P: floor = DR's pooled
mind-visible GRAVE loss (mean of three seeds); pooled clause NF ≤ 1.10
× floor; per-friend clause NF_grave − 1.10 × DR_grave ≤ NF's
between-seed SD on every covered friend. Phase 1's floor (682.11) and
verdict stand; these are inputs to the Phase 2 head choice (hers).

| width | floor (DR) | NF pooled | ratio | pooled clause | friends exceeding | dissolves |
|---|---|---|---|---|---|---|
| 12 | 924.87 | 1098.53 | 1.188 | fails | Miso, Biscuit, Pumpkin | no |
| 24 | 827.69 | 908.10 | 1.097 | holds | Miso, Biscuit | no |
| 48 | 684.51 | 790.22 | 1.154 | fails | Pumpkin, Kittybear | no |

Per friend (NF grave / DR grave / excess over 1.10 × DR / NF SD):

| friend | width 12 | width 24 | width 48 |
|---|---|---|---|
| Miso | 746.20 / 648.84 / +32.48 / 29.91 EXCEEDS | 613.31 / 480.05 / +85.26 / 78.46 EXCEEDS | 522.94 / 423.88 / +56.67 / 74.78 ok |
| Biscuit | 1400.75 / 1096.65 / +194.43 / 107.04 EXCEEDS | 1245.18 / 1011.13 / +132.94 / 19.55 EXCEEDS | 969.67 / 933.20 / −56.85 / 82.02 ok |
| Pumpkin | 914.71 / 798.03 / +36.89 / 17.99 EXCEEDS | 714.87 / 697.68 / −52.57 / 22.05 ok | 674.19 / 548.79 / +70.52 / 33.73 EXCEEDS |
| Kittybear | 1343.05 / 1081.74 / +153.14 / 198.26 ok | 1081.52 / 1021.69 / −42.35 / 111.77 ok | 983.31 / 808.63 / +93.82 / 34.38 EXCEEDS |
| Clementine | 854.43 / 922.90 / −160.76 / 111.16 ok | 758.16 / 838.55 / −164.25 / 72.85 ok | 611.70 / 672.07 / −127.57 / 67.88 ok |

The procedure fails at every width, and in the opposite shape to
Phase 1. There, on Phase 1's evaluation worlds (the grave stratum
mostly from the all-grave set G), NF was pooled under DR's
floor (0.944) and the per-friend clause failed on Miso alone. Here,
with the observer not grave, DR is pooled better on grave at every
width (NF over the floor by 18.8%, 9.7%, 15.4%), the pooled clause
holds only at width 24 and only just (1.097 against 1.10), and the
friends that exceed change with width (Miso, Biscuit and Pumpkin at
12, Miso and Biscuit at 24, Pumpkin and Kittybear at 48; Clementine
never, her grave loss being lower under NF at every width). Two
readings of the shifting set: the per-friend clause is paid in units
of NF's own between-seed SD, so a similar excess passes at one width
and fails at another (Kittybear: +153.14 against an SD of 198.26 at
12, ok; +93.82 against 34.38 at 48, exceeds); and the DR head's seeds
disagree enough (R6b) that a friend's DR grave mean moves by 56–213
points² between neighbouring widths against between-seed SDs of the
same order (up to 226.98), so every per-friend DR difference here is
read against a wide seed spread. What is
stable across widths: pooled, reweighting helps grave estimation in
this register; per friend, it helps four of five and hurts
Clementine. The Phase 1 verdict ("The tension is present, friend-specific and
narrow.") stands on its own worlds; on these worlds the tension is
broader (DR better pooled, NF better on one friend). The width did not
change it (the procedure fails at every width); what differs from Phase
1 is the register together with the retrained heads, their training
set and validation carve, and on the all-grave G worlds these same
heads read NF/DR grave 1.227 / 1.018 / 0.997 at 12 / 24 / 48
(`phase1b-read.json`, group G), so Phase 1's pooled NF advantage is
absent for these heads there too at 12 and 24.

## R4b — the ostrich metric at each width

Signed bias = predicted − true, mean over the five hidden needs, in
need points; negative = the friend predicted LESS needy than she is.
Gap = GRAVE-bin bias − COMMON-bin bias. Signature (prereg §8 item 4):
|GRAVE bias| ≥ 1.5 × |COMMON bias| with the GRAVE bias negative. Mean
of three seeds. Group P.

Mind-visible, grave / common / gap:

| friend | NF w12 | NF w24 | NF w48 | DR w12 | DR w24 | DR w48 |
|---|---|---|---|---|---|---|
| Miso | −8.12 / −0.48 / −7.65 SIG | −5.77 / −0.21 / −5.57 SIG | −7.00 / −0.39 / −6.61 SIG | −1.85 / −0.22 / −1.63 SIG | −3.59 / −0.21 / −3.38 SIG | −2.84 / −0.27 / −2.57 SIG |
| Biscuit | −15.48 / +0.38 / −15.86 SIG | −11.59 / +0.47 / −12.06 SIG | −9.44 / +0.13 / −9.57 SIG | −8.60 / +0.46 / −9.06 SIG | −8.22 / +0.55 / −8.77 SIG | −8.49 / +0.48 / −8.97 SIG |
| Pumpkin | −9.60 / −0.35 / −9.25 SIG | −6.83 / −0.10 / −6.73 SIG | −6.92 / −0.16 / −6.76 SIG | −2.69 / −0.31 / −2.39 SIG | −4.12 / −0.07 / −4.05 SIG | −4.58 / −0.17 / −4.42 SIG |
| Kittybear | −20.91 / +0.72 / −21.63 SIG | −17.01 / +0.65 / −17.66 SIG | −16.08 / +0.26 / −16.35 SIG | −15.37 / +1.31 / −16.68 SIG | −14.15 / +1.31 / −15.45 SIG | −10.25 / +0.83 / −11.08 SIG |
| Clementine | −2.69 / −0.91 / −1.78 SIG | +2.27 / −0.56 / +2.83 | +2.89 / −0.54 / +3.44 | +3.69 / −0.82 / +4.51 | +2.89 / −0.57 / +3.46 | +3.06 / −0.57 / +3.62 |
| pooled | −13.58 / −0.14 / −13.44 SIG | −10.10 / +0.05 / −10.15 SIG | −9.68 / −0.15 / −9.53 SIG | −7.38 / +0.08 / −7.45 SIG | −7.57 / +0.19 / −7.77 SIG | −6.06 / +0.06 / −6.11 SIG |

All-states, pooled: NF −12.08 / −0.08 / −12.00 SIG, −8.67 / +0.05 /
−8.72 SIG, −9.05 / −0.12 / −8.93 SIG at 12 / 24 / 48; DR −5.21 / +0.39
/ −5.60 SIG, −5.90 / +0.34 / −6.25 SIG, −4.43 / +0.15 / −4.58 SIG. The
per-friend all-states tables are in `phase1b-read.md`.

In this register the ostrich signature is broader and deeper than in
Phase 1's read (its grave samples mostly from the all-grave set G),
and width does not remove it. At Phase 1's
width the natural-frequency head reads a grave friend in sight 10.10
points less needy than she is (Phase 1: 3.80), against a common-state
bias within 0.5 of zero, and the signature fires on four of the five
friends: Biscuit, whom Phase 1 read without it (+0.59), is now at
−11.59, and Kittybear at −17.01 is the deepest. Clementine is the
exception at widths 24 and 48 (+2.27, +2.89: read as MORE needy than
she is) and the one friend DR does not help in R1b and R3b. Distress
reweighting no longer removes the pooled optimism: DR reads −7.57 at
width 24 in sight (Phase 1: +1.71) and carries the signature on the
same four friends. Width moves the NF bias from −13.58 to −10.10 to
−9.68 and DR's from −7.38 to −7.57 to −6.06 (not monotone): the widest
NF head is still more optimistic than the narrowest DR head, and the
over-cap probe still reads a grave friend 9.68 points short. As in Phase 1 the
1.5× lift is met trivially wherever the common bias is near zero, so
the gap in points is the informative column. The declaration's reading
of the register applies: with the observer not grave, her own state
no longer stands in for her friend's, and what is left under natural
frequency is a head that under-reads need where need is highest.

## R5b — the all-grave confound, G over P

q = pooled GRAVE loss on group G (Phase 1's eight G evaluation worlds,
every cat grave at reset) over the same heads' pooled GRAVE loss on
group P (one cat grave at reset), per width × head × version; SD and
READ rule as in R2b. q under 1 − SD says the all-grave worlds were
EASIER. Each side is pooled over its own covered friends: in sight the G side
four (Pumpkin is under min-n on G alone, 166) and the P side five;
all-states both sides five (Pumpkin 744 on G).

| width | NF in sight | DR in sight | NF all-states | DR all-states |
|---|---|---|---|---|
| 12 | 0.741 ± 0.064 READ | 0.718 ± 0.152 READ | 0.730 ± 0.094 READ | 0.739 ± 0.123 READ |
| 24 | 0.651 ± 0.033 READ | 0.702 ± 0.102 READ | 0.613 ± 0.016 READ | 0.691 ± 0.063 READ |
| 48 | 0.669 ± 0.055 READ | 0.774 ± 0.057 READ | 0.666 ± 0.055 READ | 0.793 ± 0.038 READ |

G-side losses (pooled mind-visible GRAVE, these heads): NF 814.28 ±
60.14 / 591.58 ± 20.73 / 528.31 ± 35.21, DR 663.61 ± 98.63 / 580.94 ±
17.77 / 529.91 ± 29.13 at 12 / 24 / 48 (`phase1b-read.md`, group G).

Every cell is READ under 1: the all-grave worlds are 21–39% easier in
squared error than the per-cat ones for the same heads (23–35% in
sight), at every width and under both weightings. This is the number behind Phase 1's second
limitation ("the observer's own needs are informative about the
friend's at the start"): at Phase 1's width the per-cat worlds show
about half again the grave loss of the all-grave worlds for the same
heads (1 / 0.651 = 1.54). The ratio bounds the difference between the
registers; it does not isolate the cue's share (different evaluation
worlds and, in sight, different friend pools). Phase 1's
grave RMS of about 25 was an upper bound on inference skill, as it
said; the per-cat figure at the same width is 30.1 (NF) and 28.8
(DR). For NF the gap widens from 12 to 24 (0.741 → 0.651: the wider head
gains more on the all-grave worlds than on the per-cat ones) and holds
at 48 (0.669). The G-side numbers here are not Phase
1's cells (different training set, G-only evaluation worlds) and are
not compared to them.

## Not read

Consumers, clone_fraction, any welfare claim (Phase 1's list). The G
group's non-grave cells beyond R5b. Any comparison that pools P with
G. Phase 1's floor and verdicts are not re-read; the R3b numbers are
inputs to the Phase 2 head choice (hers), never a replacement. The
extension blocks X1..X5 were not run.

## Regeneration

Phase 1's arc venv (`A=experiments/minifriend-phase1-2026-10-22`,
`B=experiments/minifriend-phase1b-2026-10-23`, run from the repository
root; `VIRTUAL_ENV=$PWD/$A/.venv` on every line; `MINIFRIEND_ARC=$PWD/$B`
points Phase 1's modules at this arc's `split.json` and `results-raw/`).
Raws: `$B/results-raw/P{1..5}/streams-<seed>.npz` (100 worlds),
`$B/results-raw/{L,W,G}` → symlinks to Phase 1's raws,
`$B/results-raw/heads/{NF,DR}-h{12,24,48}-s{1,2,3}/` (the 18 runs read
here).

### Collect

```sh
# scouts, one world per friend; check_P must show no abort before the rest
(cd $B && for k in 1 2 3 4 5; do ./run_P.sh $k $((1095451 + 20*(k-1))); done)
# the rest (never `seq` for the seeds: BSD seq prints 1.09555e+06)
(cd $B && for k in 1 2 3 4 5; do b=$((1095451 + 20*(k-1))); for ((s=b+1; s<=b+19; s++)); do echo $s; done | xargs -P 5 -n 1 ./run_P.sh $k; done)
# Phase 1's raws reachable under this arc
(cd $B && for s in L W G; do ln -s ../../minifriend-phase1-2026-10-22/results-raw/$s results-raw/$s; done)
# the eighteen heads (≈ 45 min wall: widths in sequence, six in parallel)
(cd $B && caffeinate -s ./run_heads.sh > results-raw/heads/run-all.log 2>&1)
```

### Read

```sh
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $B/check_P.py --out $B/P-check.json                                     # ≈ 2 s
MINIFRIEND_ARC=$PWD/$B VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/count_strata.py --sets P1 P2 P3 P4 P5 --out $B/strata-counts.json    # ≈ 1 s (P only; L/W/G are symlinked here and must not pool)
MINIFRIEND_ARC=$PWD/$B VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $B/read_phase1b.py --out $B/phase1b-read.json --md > $B/phase1b-read.md  # ≈ 40 s (stdout is the markdown; the 'wrote' line goes to stderr)
```

Guards (plain-assert runners, Phase 1's venv): `$B/test_phase1b.py` 6
(s1, s2, b1–b3, p1); `$A/test_train_heads.py` 6 (h6 added for this
arc); `$A/test_count_strata.py` 4 (c4, the `--sets` filter, added
after gate round 1). Reds on record via `scripts/mutate.sh` in the
declaration's §Instrument (h6, s1, s2, b1, b2, b3; p1 twice; c4).

Accuracy gate: **PASS**, 2026-10-23, round 5 (fresh subagent per
round; every round regenerated the four outputs byte-identically and
matched every number). Rounds 1–4 FAILED on prose and provenance, not
numbers: round 1 six contradicted claims plus the strata-count fence
pooling the L/W/G symlinks (remedied by `count_strata.py --sets`,
guard c4); round 2 a pooling scope, the c4 red not yet on record, and
the fence not writing the markdown read; round 3 PASS with four weak
wordings tightened; round 4 one sentence introduced by the round-2 fix
and two scope labels; round 5 PASS: about 560 reader-backed cells and
about 100 derived numbers matched, thresholds all sourced, no
characterisation contradicted, provenance all located, three guard
runners at their stated counts, instrument matched to the declaration.
Two wordings the round reported as weak were scoped after the verdict
without a number changing (R1b (b) "For NF"; §Samples' use of group
G). The F-065 copy check ran as further copy-only rounds after round 5
until it passed, each restoring qualifiers the entry had dropped
(numbers never at fault; the rounds are in the gate's TRIALS.md). Raw-dir hashes (`scripts/rawdir-hash.sh`
refuses symlinks, so the bundle is stamped per sub-directory; the
L/W/G links resolve to Phase 1's bundle, stamped `v1:b693200d5f159e90`
in its RESULTS): heads `v1:fb233ec6c9eec4f3`, P1 `v1:5a72da8fc67f4cfd`,
P2 `v1:cab363f9f574725a`, P3 `v1:75a9171562b06cc9`, P4
`v1:1fd53de9123185dc`, P5 `v1:2d2a885d4fa1c97b` (each
`scripts/rawdir-hash.sh experiments/minifriend-phase1b-2026-10-23/results-raw/<dir>`).
