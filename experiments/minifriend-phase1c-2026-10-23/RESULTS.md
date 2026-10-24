# Mini-friend Phase 1c — RESULTS (read 2026-10-24 UTC)

Declaration: `DECLARATION.md` (owner 2026-10-23 "Let's try it.
Currently our accuracy is low enough that we can reevaluate model size
limit if needed. Let's test this approach first though"; §Addendum the
same day, "Let's try 3 model sizes this time as well so we can get an
idea of what more/less parameters buy"); deviations entry 12. Prereg
basis frozen 18f06f84, §8 items 3–4; amendment A4's working direction.
Binding: Phase 1's arc venv (`../minifriend-phase1-2026-10-22/
BINDING.md`; engine a2e8d044). No new rollout: 0 covered cat-ticks.
Every read is descriptive (doctrine rule 10); nothing gates. Phase 1's
and 1b's floors, verdicts, F-064 and F-065 stand; the width-24
comparators are 1b's runs re-read here, pinned to 1b's gated cells
(the mechanical pin is the pooled mind-visible GRAVE mse5 and bias;
every other borrowed cell was checked against 1b's RESULTS at the
gate).

## Headline

The structured discrete head (SD) does not help on the declared
criteria. At the declared width (16; 6,679 parameters) its pooled
mind-visible grave MSE on the per-cat worlds is 1119.69 (RMS 33.5 need
points) against NF-h24's 908.10 (RMS 30.1): ratio 1.233 ± 0.091, READ,
over 1, so criterion (i) is not met. Its pooled grave bias in sight is
−15.01 need points against NF's −10.10 and DR's −7.57, with the
signature on all five friends (NF and DR: four), so criterion (ii) is
not met. In common states the same head is better than NF by about a
fifth (19.96 against 25.34; 0.787 ± 0.022 READ) and better than DR by
half (0.497 ± 0.085 READ). Width moves every pooled SD loss cell in one
direction (R9c, in sight on P: 1.414 ± 0.190 at 8 over 16 and 0.819 ± 0.080 at
32 over 16 on grave, 1.237 ± 0.025 and 0.848 ± 0.026 in common states,
all READ), in proportion not grave-specific, as 1b found for NF. At
width 32 (15,783 parameters, 1.9× the cap, a probe) SD ties NF-h24 on
grave (917.44; 1.010 ± 0.083, not READ; by Phase 1's dissolution
procedure with NF-h24 as the floor it clears, 1.010 pooled and every
friend inside the clause) and is better by a third in common states
(16.92; 0.668 ± 0.021 READ); its grave bias is −11.07, still signed on
all five friends. The grave probability the head emits (R4c) is close
to the diagonal at width 16 above p = 0.7 (realised grave fraction
0.795 / 0.851 / 0.936 in the 0.7–0.8 / 0.8–0.9 / 0.9–1.0 bins) and
under-confident below it, and the mean P(grave) on grave samples is
0.474: a belief that puts about half its probability on grave reads,
through its mean, as a point estimate well below the truth. The MSE
and bias columns score such a belief through its mean, and the ostrich
metric as declared does not separate that from optimism. The act
embryo (p_rel) discriminates relief at AUROC 0.979 in sight and 0.797
under fog at width 16. Six of the nine runs reached the 200-epoch cap
before the plateau rule fired (every 1b run plateaued by epoch 82);
the SD numbers are those of heads still improving slowly at the cap,
which is reported, not re-run. Wall clock 10–14 hours per run against
1b's 12–17 minutes for six.

## Decision rules, applied

Source: `DECLARATION.md` §Reads, "What would count as the approach
helping" (domain: group P evaluation worlds, mind-visible, pooled over
covered friends, mean of seeds 1–3, width 16, comparators 1b's
width-24 runs re-read here).

| criterion | bar | read | met |
|---|---|---|---|
| (i) R2c GRAVE, SD over NF-h24 | READ under 1 | 1.233 ± 0.091, READ, over 1 | no |
| (ii) R3c pooled GRAVE bias in sight | within ±5.0 and no pooled signature | −15.01 ± 1.74, signature | no |

Neither holds; by the declared text "the approach does not help at
this capacity, and the cap question is hers with that read in hand".
The Phase 2 head choice remains hers (F-064, F-065 and this read in
hand). Nothing here is a welfare claim.

## Data

No new collection. Training, validation and evaluation worlds are
Phase 1b's split byte for byte (guard t6): 74 training worlds, 17
validation, 69 evaluation (L 3, W 8, G 8, P 50). Group P = the P1..P5
evaluation worlds (4,000,000 samples; mind-visible GRAVE coverage Miso
572, Biscuit 364, Pumpkin 398, Kittybear 933, Clementine 260; 2,527
GRAVE samples in sight, of which 168 happiness-only); group G = Phase
1's G evaluation worlds (640,000 samples; Pumpkin insufficient on
mind-visible GRAVE, 166). Baselines on P in sight (marginal / proxy):
GRAVE 3264.16 / 3261.15, COMMON 75.10 / 72.67. The data tables are
1b's RESULTS §Data and Phase 1's.

## Heads (R8c)

`sd_head.py --hidden r [--over-cap]`: per hidden need a histogram over
20 bins of 5 points, drifting up at a learned per-(friend, need) rate
and down on relief by a learned per-need size with probability p_rel
from a width-r GRU over the 167 input cells, a logit residual from the
same GRU (zeroed at prediction time for the `nores/` read), learned
priors; cross-entropy against two-hot targets + 0.5 × BCE on the
relief indicator + Phase 1's happiness and 0.1 × bath terms; natural
frequency; Phase 1's chunking, optimiser, batch, stopping rule and
seeds. The filter's own parameters (25 rates, 5 relief sizes, 500
prior logits) are 530 at every width.

| run | width r | params | vs cap 8,445 | best epoch / epochs run | best validation loss | stop |
|---|---|---|---|---|---|---|
| SD-h8-s1 | 8 | 3,279 | under | 193 / 200 | 1.2492 | epoch cap |
| SD-h8-s2 | 8 | 3,279 | under | 200 / 200 | 1.2576 | epoch cap |
| SD-h8-s3 | 8 | 3,279 | under | 200 / 200 | 1.2395 | epoch cap |
| SD-s1 | 16 | 6,679 | under | 157 / 167 | 1.0996 | plateau |
| SD-s2 | 16 | 6,679 | under | 193 / 200 | 1.0847 | epoch cap |
| SD-s3 | 16 | 6,679 | under | 198 / 200 | 1.0970 | epoch cap |
| SD-h32-s1 | 32 | 15,783 | OVER (1.9×), probe | 196 / 200 | 1.0079 | epoch cap |
| SD-h32-s2 | 32 | 15,783 | OVER (1.9×), probe | 167 / 177 | 1.0135 | plateau |
| SD-h32-s3 | 32 | 15,783 | OVER (1.9×), probe | 123 / 133 | 1.0263 | plateau |

The width-16 runs keep the launch name `SD-s<seed>` (they were training
when the addendum was written); the width-32 manifests carry
`over_cap: true`. The validation loss is the SD loss (cross-entropy
plus the auxiliary terms), not comparable to NF's or DR's columns. Six
of nine runs reached the 200-epoch cap with the validation loss still
improving by more than the plateau margin inside every ten-epoch
window (mean decline 1.4–4.2 × 10⁻⁴ per epoch from epoch 170 to 200
against the 10⁻⁴ margin; 10–20 new bests by more than the
margin in epochs 151–200; SD-s2's last five: 1.0896, 1.0854, 1.0860,
1.0904, 1.0873 against its best 1.0847); every 1b run plateaued
between epochs 31 and 82. Per-epoch
cost: the width-16 runs took a median 165 s while the three ran alone
(three threads each) and 257–281 s once nine ran; widths 8 and 32 at
two threads 314–326 s while nine ran and 192–227 s after the width-16
runs finished (whole-run medians 232–324 s); wall clock 10.3–12.5 h (width
16, started 2026-10-23T23:14Z), 14.0–14.1 h (width 8) and 10.8–14.3 h
(width 32; both started 2026-10-24T03:12Z). The cost is the per-tick
filter loop, not the width.

## R1c — accuracy at each width, group P (MSE on the five hidden needs, need points²; pooled over covered friends, mean ± SD over seeds)

In sight:

| width | head | GRAVE | DA | COMMON | GRAVE bias | COMMON bias |
|---|---|---|---|---|---|---|
| 8 | SD | 1582.84 ± 187.15 | 1308.78 ± 138.98 | 24.69 ± 0.10 | −21.80 ± 3.51 | +0.43 ± 0.13 |
| 16 | SD | 1119.69 ± 71.25 | 921.40 ± 43.02 | 19.96 ± 0.39 | −15.01 ± 1.74 | +0.42 ± 0.02 |
| 32 | SD | 917.44 ± 67.65 | 761.34 ± 43.20 | 16.92 ± 0.40 | −11.07 ± 2.42 | +0.41 ± 0.09 |
| 24 | NF (1b) | 908.10 ± 33.43 | 773.25 ± 20.58 | 25.34 ± 0.52 | −10.10 ± 1.08 | +0.05 ± 0.14 |
| 24 | DR (1b) | 827.69 ± 117.06 | 725.06 ± 97.39 | 40.15 ± 6.85 | −7.57 ± 0.93 | +0.19 ± 0.25 |

All states:

| width | head | GRAVE | DA | COMMON | GRAVE bias | COMMON bias |
|---|---|---|---|---|---|---|
| 8 | SD | 1531.05 ± 119.76 | 1341.98 ± 103.70 | 36.65 ± 0.53 | −21.63 ± 2.28 | +0.56 ± 0.10 |
| 16 | SD | 1082.26 ± 80.26 | 951.08 ± 64.17 | 30.38 ± 0.30 | −14.38 ± 1.92 | +0.49 ± 0.02 |
| 32 | SD | 911.95 ± 36.04 | 808.97 ± 26.87 | 26.94 ± 0.39 | −11.11 ± 0.95 | +0.47 ± 0.13 |
| 24 | NF (1b) | 894.45 ± 21.77 | 795.12 ± 19.89 | 33.68 ± 0.54 | −8.67 ± 0.32 | +0.05 ± 0.13 |
| 24 | DR (1b) | 729.70 ± 65.46 | 680.36 ± 59.05 | 54.48 ± 8.30 | −5.90 ± 0.21 | +0.34 ± 0.46 |

Per friend at width 16, in sight (GRAVE / COMMON):

| friend | SD GRAVE | NF GRAVE | DR GRAVE | SD COMMON | NF COMMON | DR COMMON |
|---|---|---|---|---|---|---|
| Miso | 696.22 ± 92.24 | 613.31 ± 78.46 | 480.05 ± 84.11 | 18.80 ± 0.33 | 24.94 ± 0.65 | 38.41 ± 5.91 |
| Biscuit | 1383.92 ± 225.50 | 1245.18 ± 19.55 | 1011.13 ± 66.77 | 17.53 ± 0.45 | 24.05 ± 0.81 | 37.71 ± 6.14 |
| Pumpkin | 848.70 ± 66.79 | 714.87 ± 22.05 | 697.68 ± 93.75 | 21.81 ± 0.67 | 26.77 ± 0.71 | 41.41 ± 7.00 |
| Kittybear | 1429.29 ± 233.36 | 1081.52 ± 111.77 | 1021.69 ± 218.83 | 18.46 ± 0.47 | 21.86 ± 0.44 | 36.78 ± 7.08 |
| Clementine | 985.26 ± 235.02 | 758.16 ± 72.85 | 838.55 ± 49.32 | 23.06 ± 0.50 | 28.93 ± 0.20 | 46.18 ± 8.13 |
| pooled | 1119.69 ± 71.25 | 908.10 ± 33.43 | 827.69 ± 117.06 | 19.96 ± 0.39 | 25.34 ± 0.52 | 40.15 ± 6.85 |

SD's grave loss is above NF's on every friend at width 16 (by 83 to
348 points²) and below NF's and DR's in common states on every friend.
At width 32 SD is below NF on Miso (548.47 against 613.31), Biscuit
(1066.78 against 1245.18) and Clementine (726.99 against 758.16) and
above on Pumpkin (833.94 against 714.87) and Kittybear (1174.08
against 1081.52); the pooled cell ties. The per-friend ordering of
difficulty is the one 1b read: Biscuit and Kittybear hardest at every
width and for every head.

## R2c — contrast with the width-24 comparators (ratio SD / comparator, first-order SD; READ when |r − 1| > SD)

Group P:

| width | version | SD / NF GRAVE | SD / NF DA | SD / NF COMMON | SD / DR GRAVE | SD / DR DA | SD / DR COMMON |
|---|---|---|---|---|---|---|---|
| 8 | in sight | 1.743 ± 0.216 READ | 1.693 ± 0.185 READ | 0.974 ± 0.020 READ | 1.912 ± 0.353 READ | 1.805 ± 0.309 READ | 0.615 ± 0.105 READ |
| 16 | in sight | 1.233 ± 0.091 READ | 1.192 ± 0.064 READ | 0.787 ± 0.022 READ | 1.353 ± 0.210 READ | 1.271 ± 0.181 READ | 0.497 ± 0.085 READ |
| 32 | in sight | 1.010 ± 0.083 | 0.985 ± 0.062 | 0.668 ± 0.021 READ | 1.108 ± 0.177 | 1.050 ± 0.153 | 0.421 ± 0.073 READ |
| 8 | all | 1.712 ± 0.140 READ | 1.688 ± 0.137 READ | 1.088 ± 0.024 READ | 2.098 ± 0.250 READ | 1.972 ± 0.229 READ | 0.673 ± 0.103 READ |
| 16 | all | 1.210 ± 0.094 READ | 1.196 ± 0.086 READ | 0.902 ± 0.017 READ | 1.483 ± 0.173 READ | 1.398 ± 0.154 READ | 0.558 ± 0.085 READ |
| 32 | all | 1.020 ± 0.047 | 1.017 ± 0.042 | 0.800 ± 0.017 READ | 1.250 ± 0.123 READ | 1.189 ± 0.110 READ | 0.494 ± 0.076 READ |

The headline cell (width 16, in sight, GRAVE, SD / NF) is 1.233 ±
0.091, READ, over 1. The grave and distress-adjacent columns move
together at every width; the common-state column favours SD against
both comparators at every width in sight (at width 8 against NF by a
hair, 0.974 ± 0.020, READ) and at widths 16 and 32 in all states; at
width 8 in all states SD is worse than NF (1.088 ± 0.024 READ). At
width
32 the grave cells tie NF (1.010 in sight, 1.020 all states, neither
READ) and tie DR in sight (1.108 ± 0.177) while READ over DR in all
states (1.250 ± 0.123).

## R3c — the ostrich metric (grave bias / common bias / gap, need points; SIG = Phase 1's R4 signature, grave bias negative and |grave bias| ≥ 1.5 × |common bias|)

Group P, in sight:

| friend | SD w8 | SD w16 | SD w32 | NF-h24 | DR-h24 |
|---|---|---|---|---|---|
| Miso | −20.43 / +0.37 / −20.80 SIG | −11.43 / +0.35 / −11.79 SIG | −7.86 / +0.40 / −8.26 SIG | −5.77 / −0.21 / −5.57 SIG | −3.59 / −0.21 / −3.38 SIG |
| Biscuit | −22.61 / +0.38 / −22.99 SIG | −16.95 / +0.22 / −17.18 SIG | −13.16 / +0.23 / −13.38 SIG | −11.59 / +0.47 / −12.06 SIG | −8.22 / +0.55 / −8.77 SIG |
| Pumpkin | −19.04 / +0.49 / −19.54 SIG | −11.61 / +0.54 / −12.15 SIG | −8.59 / +0.49 / −9.08 SIG | −6.83 / −0.10 / −6.73 SIG | −4.12 / −0.07 / −4.05 SIG |
| Kittybear | −25.98 / +0.63 / −26.61 SIG | −19.68 / +0.54 / −20.22 SIG | −15.91 / +0.50 / −16.41 SIG | −17.01 / +0.65 / −17.66 SIG | −14.15 / +1.31 / −15.45 SIG |
| Clementine | −12.89 / +0.29 / −13.19 SIG | −8.56 / +0.42 / −8.98 SIG | −1.61 / +0.43 / −2.04 SIG | +2.27 / −0.56 / +2.83 | +2.89 / −0.57 / +3.46 |
| pooled | −21.80 / +0.43 / −22.23 SIG | −15.01 / +0.42 / −15.42 SIG | −11.07 / +0.41 / −11.48 SIG | −10.10 / +0.05 / −10.15 SIG | −7.57 / +0.19 / −7.77 SIG |

SD's grave estimate in sight is low on every friend at every width,
and the signature fires on all five (Clementine, positive for NF and
DR, is −8.56 for SD at width 16 and −1.61 at width 32, still flagged
because SD's common bias is a steady +0.4). Width narrows the pooled
grave bias from −21.80 to −15.01 to −11.07; at width 32 it is within a
point of NF-h24's. The common-state bias is +0.41 to +0.43 at every
width (NF +0.05, DR +0.19): the histogram mean sits slightly high in
ordinary states, a half-bin effect of the two-hot target at the low
end of the range. All-states pooled: −21.63 / −14.38 / −11.11 (NF
−8.67, DR −5.90), all SIG. Read beside R4c before calling this
optimism: the point estimate is a histogram mean.

## R4c — calibration of the grave probability (P(grave by need) = 1 − ∏(1 − grave mass_i); group P; against the true stratum, happiness-only grave samples counting against the head)

In sight (2,527 GRAVE samples, 168 of them happiness-only; about 1.92
million samples in the lowest bin at every width):

| width | Brier | mean p on GRAVE | mean p on COMMON | realised grave fraction in bins 0.5–0.6 / 0.7–0.8 / 0.8–0.9 / 0.9–1.0 (seed-1 n; the read lists all three) |
|---|---|---|---|---|
| 8 | 0.0009 ± 0.0001 | 0.294 ± 0.075 | 0.001 ± 0.000 | 0.662 / 0.776 / 0.741 / 0.538 (381 / 227 / 181 / 130) |
| 16 | 0.0006 ± 0.0001 | 0.474 ± 0.115 | 0.000 ± 0.000 | 0.623 / 0.795 / 0.851 / 0.936 (335 / 238 / 170 / 136) |
| 32 | 0.0005 ± 0.0001 | 0.545 ± 0.087 | 0.000 ± 0.000 | 0.733 / 0.785 / 0.881 / 0.964 (284 / 291 / 327 / 870) |

Full reliability tables per width and version are in
`phase1c-read.md`. At width 16 the head is under-confident below p =
0.7 (bin 0.1–0.2 realises 0.251, bin 0.3–0.4 realises 0.446) and on
the diagonal above it; at width 32 the top bin holds 870 / 318 / 559
samples by seed at a realised 0.964; at width 8 the top bin is
over-confident (0.538 realised, the mean of two seeds; seed 3 puts no
sample there). The realised fractions are means over the seeds with
samples in the bin and the counts are per seed. The mean P(grave) on
grave samples rises with width (0.294 / 0.474 / 0.545) while the mean
on common samples stays at 0.000–0.001. Happiness-only grave samples (6.6% in sight, 11.1% all
states) cannot be carried by the need histograms and bound the
achievable mean p on GRAVE below 1. All states: Brier 0.0016 / 0.0013
/ 0.0011, mean p on GRAVE 0.366 / 0.494 / 0.529.

What the two reads say together, at width 16: on a grave sample the
head puts, on average, about half its probability on grave and the
rest lower; the histogram mean of such a belief sits below the truth,
and that distance is what the bias column reports (−15.01 pooled).
The read carries the mean P(grave), not the histogram's shape. The declared point estimate (the
histogram mean, chosen so Phase 1's reader reads SD unchanged) turns a
two-moded belief into a conditional mean, the same quantity the
ostrich read was built to expose in NF and DR. Whether a consumer
should read the probability rather than the mean is a Phase 2 design
question (prereg item 4's entry gate acts on a predicted quantity),
hers; this arc only reports that the two columns disagree about what
the head knows.

## R5c — rate recovery (learned rise rate, need points per tick, mean ± SD over seeds / empirical median positive one-tick step on the training worlds' truth streams; never the served config)

Width 16:

| friend | eat | drink | sleep | play | cuddle |
|---|---|---|---|---|---|
| Miso | 0.11 ± 0.03 / 0.30 | 0.28 ± 0.03 / 0.40 | 0.82 ± 0.00 / 0.60 | 0.03 ± 0.00 / 0.30 | 0.15 ± 0.03 / 0.40 |
| Biscuit | 0.11 ± 0.03 / 0.30 | 0.05 ± 0.01 / 0.30 | 0.17 ± 0.02 / 0.30 | 0.32 ± 0.02 / 0.80 | 0.15 ± 0.03 / 0.40 |
| Pumpkin | 1.23 ± 0.15 / 0.60 | 0.29 ± 0.03 / 0.40 | 0.06 ± 0.02 / 0.20 | 0.06 ± 0.00 / 0.40 | 0.15 ± 0.03 / 0.40 |
| Kittybear | 0.33 ± 0.05 / 0.40 | 0.05 ± 0.01 / 0.30 | 0.15 ± 0.02 / 0.30 | 0.03 ± 0.00 / 0.30 | 0.14 ± 0.03 / 0.40 |
| Clementine | 0.38 ± 0.05 / 0.40 | 0.29 ± 0.02 / 0.40 | 0.20 ± 0.02 / 0.30 | 0.03 ± 0.00 / 0.30 | 0.71 ± 0.02 / 0.70 |

Learned relief sizes (points per relieving tick) at width 16: eat
35.44 ± 0.45, drink 27.25 ± 9.39, sleep 10.78 ± 2.28, play 18.82 ±
0.26, cuddle 19.31 ± 2.43 (width 8: 39.41 / 37.32 / 13.60 / 19.70 /
27.76; width 32: 35.22 / 18.97 / 9.03 / 17.98 / 17.59).

The rates are learned with the residual present, so the filter need
not be physical, and it is not: the per-friend emphases are recovered
(Pumpkin's eat is the largest eat rate at every width, Clementine's
cuddle 0.71 against 0.70, Miso's sleep the largest sleep rate), many
ordinary cells sit well under the empirical step (eat 0.11 against
0.30 for Miso and Biscuit, drink 0.05 against 0.30 for Biscuit and
Kittybear), and the play rate collapses to 0.03–0.06 against
0.30–0.40 for four friends at width 16 (Biscuit's, empirical 0.80, is
learned at 0.32). The width-8 and width-32 tables are
in `phase1c-read.md`; the pattern is the same, with most ordinary
cells lower as width grows (18 of the 22 fall at both steps, 21 from
8 to 32; Miso eat 0.18 / 0.11 / 0.07): more residual, less filter.

## R6c — residual share and the act embryo

(a) SD with the residual zeroed (`nores/`) over the full head, group P
(ratio, first-order SD; reading rule: the structure carries the fit if
the no-residual grave loss is within 2× the full head's):

| width | version | GRAVE | DA | COMMON | carries (≤ 2.0×) |
|---|---|---|---|---|---|
| 8 | in sight | 1.426 ± 0.223 READ | 1.437 ± 0.207 READ | 3.440 ± 0.480 READ | yes |
| 16 | in sight | 2.013 ± 0.231 READ | 2.052 ± 0.224 READ | 7.676 ± 0.401 READ | no (by 0.013) |
| 32 | in sight | 2.948 ± 0.218 READ | 2.952 ± 0.168 READ | 10.457 ± 0.396 READ | no |
| 8 | all | 1.400 ± 0.207 READ | 1.407 ± 0.200 READ | 2.824 ± 0.270 READ | yes |
| 16 | all | 1.932 ± 0.190 READ | 1.959 ± 0.191 READ | 5.656 ± 0.145 READ | yes |
| 32 | all | 2.810 ± 0.120 READ | 2.805 ± 0.102 READ | 7.339 ± 0.261 READ | no |

The no-residual grave loss in sight is 2256.95 / 2253.93 / 2704.63 at
widths 8 / 16 / 32 against the marginal baseline's 3264.16; its
common-state loss is 84.92 / 153.18 / 176.94 against the marginal
75.10, so the filter alone is worse than the marginal mean in ordinary
states at every width, and on grave about a third better than it at
widths 8 and 16 and a sixth better at 32. The
residual's share of the fit grows with width; at width 16 the reading
rule is missed by 0.013 in sight and met in all states.

(b) p_rel against the true relief indicator (the need fell since the
previous tick), AUROC pooled over friends, group P:

| width | in sight | under fog | all |
|---|---|---|---|
| 8 | 0.960 ± 0.005 | 0.755 ± 0.018 | 0.883 ± 0.010 |
| 16 | 0.979 ± 0.002 | 0.797 ± 0.009 | 0.914 ± 0.006 |
| 32 | 0.988 ± 0.000 | 0.823 ± 0.003 | 0.932 ± 0.001 |

In sight the friend's activity is in the row and the relief read is
near-perfect; under fog the GRU infers it at 0.80 at width 16. This is
the act predictor in embryo (amendment A4; prereg item 4's prediction
gap), read offline on recorded worlds; no consumer uses it here.

## R7c — against the floors (information; Phase 1's dissolution procedure, tolerance 1.10, per-friend clause by the candidate's between-seed SD; licenses head choice only)

Group P, in sight:

| candidate | floor | floor pooled | candidate pooled | ratio | pooled | friends | clears |
|---|---|---|---|---|---|---|---|
| SD w8 | DR-h24 | 827.69 | 1582.84 | 1.912 | no | no (5 exceed) | no |
| SD w8 | NF-h24 | 908.10 | 1582.84 | 1.743 | no | no (5 exceed) | no |
| SD w16 | DR-h24 | 827.69 | 1119.69 | 1.353 | no | no (Miso, Biscuit, Pumpkin, Kittybear exceed) | no |
| SD w16 | NF-h24 | 908.10 | 1119.69 | 1.233 | no | no (Kittybear exceeds, +239.62 against SD 233.36) | no |
| SD w32 | DR-h24 | 827.69 | 917.44 | 1.108 | no (by 0.008) | yes | no |
| SD w32 | NF-h24 | 908.10 | 917.44 | 1.010 | yes | yes | yes |
| NF-h24 (1b's R3b) | DR-h24 | 827.69 | 908.10 | 1.097 | yes | no (Miso, Biscuit exceed) | no |

The declared head does not clear either floor. The over-cap probe
clears NF-h24 as a floor and misses DR-h24 by 0.008 on the pooled
clause with every friend inside; it is a probe (1.9× the cap) and
never a Phase 2 candidate under the standing cap. Phase 1's floor and
verdict are not re-read.

## R9c — the size effect (SD pooled MSE at width h over width 16; first-order SD; READ when |r − 1| > SD)

| group | version | w8 GRAVE | w8 DA | w8 COMMON | w32 GRAVE | w32 DA | w32 COMMON |
|---|---|---|---|---|---|---|---|
| P | in sight | 1.414 ± 0.190 READ | 1.420 ± 0.165 READ | 1.237 ± 0.025 READ | 0.819 ± 0.080 READ | 0.826 ± 0.061 READ | 0.848 ± 0.026 READ |
| P | all | 1.415 ± 0.152 READ | 1.411 ± 0.145 READ | 1.206 ± 0.021 READ | 0.843 ± 0.071 READ | 0.851 ± 0.064 READ | 0.887 ± 0.015 READ |
| G | in sight | 1.666 ± 0.419 READ | 1.574 ± 0.322 READ | 1.232 ± 0.027 READ | 0.838 ± 0.144 READ | 0.858 ± 0.120 READ | 0.850 ± 0.032 READ |
| G | all | 1.604 ± 0.457 READ | 1.565 ± 0.413 READ | 1.178 ± 0.022 READ | 0.806 ± 0.146 READ | 0.826 ± 0.142 READ | 0.878 ± 0.025 READ |

Every ratio is READ in the expected direction. Halving the width costs
about 41% of grave loss in sight on P and doubling it past the cap
buys about 18% (NF in 1b: 21% and 13%); in common states the steps
are 24% and 15% (NF: 20% and 12%). In proportion the SD size effect is
not grave-specific (0.819 on grave against 0.848 in common states, SDs
overlapping), as 1b read for NF; in points² the grave stratum gains
most (202.25 from 16 to 32 against 3.04 in common states). The cap
binds for this head as it did for NF: capacity above the 8,445 budget
buys grave accuracy, on the means at a rate like NF's or steeper
(0.819 ± 0.080 against 0.870 ± 0.053, the spreads overlapping and
the parameter steps unequal, ×2.4 against ×2.9; in points² 202.25
against 117.88), and SD starts further behind. What a parameter buys, in the headline cell: NF-h12 →
h24 → h48 (3,043 → 7,807 → 22,519) read 1098.53 → 908.10 → 790.22 in
1b; SD w8 → w16 → w32 (3,279 → 6,679 → 15,783) reads 1582.84 →
1119.69 → 917.44. At about equal parameters SD is behind NF at every
rung (3.3k: 1582.84 against 1098.53; 6.7k against 7.8k: 1119.69
against 908.10), and SD-h32 at 15.8k reaches NF-h24's cell, not
NF-h48's.

## Group G (Phase 1's all-grave evaluation worlds; information)

At width 16 in sight SD's pooled grave loss is 734.34 ± 82.43 against
NF-h24's 591.58 ± 20.73 and DR-h24's 580.94 ± 17.77 (SD / NF 1.241 ±
0.146 READ; SD / DR 1.264 ± 0.147 READ); common states 21.59 against
26.79 and 42.40 (0.806 ± 0.023 READ; 0.509 ± 0.071 READ); pooled grave
bias −6.66 against −4.94 and −0.66, SIG. At width 32: 615.09 ± 80.23
(1.040 ± 0.140 and 1.059 ± 0.142, neither READ), common 18.36 (0.685
READ), bias −5.59 SIG. The same picture as P with every head's grave
loss lower, as F-065 read (the all-grave worlds were the easier
register). Pumpkin is insufficient on mind-visible GRAVE here (166);
no comparison pools P with G.

## Limitations

- **Under-training.** Six of nine SD runs reached the 200-epoch cap
  before the plateau rule fired (every 1b comparator plateaued by
  epoch 82). Their best epochs are 193–200; the validation loss was
  still edging down. The declared stopping rule is Phase 1's and was
  not changed; the numbers above are those of heads that had not
  stopped improving, which biases the comparison against SD by an
  amount this arc did not measure. A longer cap is a new run on her
  word.
- **Point estimate.** Every MSE and bias cell reads the histogram
  mean (declared, so Phase 1's reader reads SD unchanged). §R4c shows
  the belief behind it; the two columns disagree about what the head
  knows on grave samples, and the declared criteria are MSE and bias.
- **Compute against the declaration.** §Welfare expected about 90 s
  per epoch and one to three hours; the runs took 165–326 s per epoch
  and 10–14 hours each. The expectation was wrong by an order of
  magnitude; no welfare cost attaches (0 cat-ticks).- **Auxiliary target.** SD saw the relief indicator (a transform of the
  same truth stream) and NF and DR did not; declared as the approach,
  not a confound; the comparison is approach against approach at equal
  capacity, and SD lost it on the declared cells.
- **Cost.** 10–14 hours per run against minutes for the comparators;
  the sequential per-tick filter in Python is the cost, which an
  engine-side implementation would not pay per se, but an online
  Phase 2 head of this shape would need the loop vectorised before any
  training budget is set.
- **Capacity match.** The width-32 probe (15,783) is 2.0× NF-h24's
  parameters (7,807) and 0.7× NF-h48's (22,519); "ties NF-h24" is a
  tie at twice the parameters.
- **Five friends, one engine, recorded worlds.** As Phase 1 and 1b: an
  offline estimate from recorded observations; no consumer; no welfare
  claim.

## Not read

Consumers, clone_fraction, any welfare claim (Phase 1's list); the
Phase 2 consumer reads; any comparison pooling P with G; happiness and
bath cells (reference only; the aux head is a linear read kept so the
columns exist); Phase 1's and 1b's floors and verdicts (not re-read;
R7c is information); any read not declared.

## Regeneration

Phase 1's arc venv (`A=experiments/minifriend-phase1-2026-10-22`,
`C=experiments/minifriend-phase1c-2026-10-23`, run from the repository
root; `VIRTUAL_ENV=$PWD/$A/.venv` on every line; `MINIFRIEND_ARC=$PWD/$C`
points Phase 1's modules at this arc's `split.json` and `results-raw/`).
Raws: `$C/results-raw/heads/SD-s{1,2,3}` (width 16), `SD-h8-s{1,2,3}`,
`SD-h32-s{1,2,3}` (the nine runs read here: `pred-*.npz`,
`belief-*.npz`, `nores/pred-*.npz`, `run-manifest.json`, `done.json`,
`metrics.jsonl`); `$C/results-raw/{L,W,G}` → symlinks to Phase 1's
raws; `$C/results-raw/P{1..5}` → symlinks to 1b's; `$C/results-raw/
heads/{NF,DR}-h24-s{1,2,3}` → symlinks to 1b's runs.

### Collect

```sh
# no rollout; the heads only (width 16 first, then 8 and 32; 10–14 h per run)
(cd $C && for s in L W G; do ln -s ../../minifriend-phase1-2026-10-22/results-raw/$s results-raw/$s; done; for k in 1 2 3 4 5; do ln -s ../../minifriend-phase1b-2026-10-23/results-raw/P$k results-raw/P$k; done; for h in NF DR; do for s in 1 2 3; do ln -s ../../../minifriend-phase1b-2026-10-23/results-raw/heads/$h-h24-s$s results-raw/heads/$h-h24-s$s; done; done)
(cd $C && WIDTHS="16" THREADS=3 caffeinate -s nohup ./run_sd.sh > results-raw/heads/run-all.log 2>&1)
(cd $C && WIDTHS="8 32" THREADS=2 caffeinate -s nohup ./run_sd.sh > results-raw/heads/run-sizes.log 2>&1)
```

### Read

```sh
MINIFRIEND_ARC=$PWD/$C VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $C/read_phase1c.py --out $C/phase1c-read.json --md > $C/phase1c-read.md   # ≈ 65 s (stdout is the markdown; the 'wrote' line goes to stderr)
```

Guards (plain-assert runner, Phase 1's venv): `$C/test_phase1c.py` 8
(t1–t8; about 15 s). Reds on record via
`scripts/mutate.sh` in the declaration's §Instrument and §Addendum
(t1–t8).

Accuracy gate: **PASS**, 2026-10-24, round 3 (fresh subagent per
round; every round regenerated the read byte-identically, matched
every number and the 8-guard count). Round 1 FAILED on three prose
claims (the epoch-cap mechanism stated backwards; the R4c reliability
counts printed from seed 1 beside a seed-mean fraction, remedied in
the reader with guard t8's hand case; a common-state claim lacking
its in-sight scope) and five weak wordings; round 2 FAILED on two
one-phrase claims (the signature rule missing "grave bias negative";
"nine-wide" per-epoch time taken over whole runs); round 3 PASS:
about 410 reader-backed cells and about 170 derived numbers matched,
nine thresholds all sourced, no characterisation contradicted,
provenance all located. After the verdict, without a number changing:
"18 fall at both steps", the provenance pin's scope, "two-moded"
dropped for the measured quantity, and the compute-expectation
limitation added from the round's note. The F-066 copy check ran as
two copy-only rounds (round 1 five dropped labels, round 2 PASS with
five advisories applied). Raw-dir hashes (`scripts/rawdir-hash.sh`
refuses symlinks, so the bundle is stamped per run directory; the
L/W/G links resolve to Phase 1's bundle `v1:b693200d5f159e90`, the
P1..P5 and NF/DR-h24 links to 1b's bundles, stamped in its RESULTS):
SD-s1 `v1:d55b34903afddae0`, SD-s2 `v1:ec413399a3b37d30`, SD-s3
`v1:a2d69d013f806cab`, SD-h8-s1 `v1:67c7da5ae192ad94`, SD-h8-s2
`v1:3cee863d67a8e27d`, SD-h8-s3 `v1:03f0a0f54eecd72a`, SD-h32-s1
`v1:9f2a53b233819788`, SD-h32-s2 `v1:0d578e051bd1e49b`, SD-h32-s3
`v1:5d62ace7d0d38ab2` (each `scripts/rawdir-hash.sh
experiments/minifriend-phase1c-2026-10-23/results-raw/heads/<run>`).
