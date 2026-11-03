# Mini-friend Phase 1e diagnostics — results (reads 2026-11-02; declaration `DECLARATION.md`, DECLARED on her "Go", reds 036d24d7)

Zero collection. Every number below is read from raws already on disk
(the needy set's 360 worlds, Phase 1e's 35 validation worlds) with the
committed heads NF1e-h24-s1..3+p ("retrained") and NF-h24-s1..3+p
("frozen"), at her operating point S = t0.05-B2 (threshold 0.05,
burn-in 2), the seed mean ± SD over three heads, the frozen beside by
the same reader on the same worlds. Instrument `diag_1e.py` at
beea07d1; guards g1–g7 red on record (DECLARATION §7). One read,
`context`, is post-hoc: it was added after the five declared reads
had run, to give D1's partition its null; it is marked so wherever it
is cited and it scores nothing.

## Headline

1. **The price is mostly attention on cats that were sliding (D1).**
   Of the retrained head's covered-friend false runs beside a refusing
   friend (arm N, confirming half, S; 2.4002 ± 1.0702 per 10,000
   observer-ticks), 0.728 ± 0.046 by runs and 0.903 ± 0.038 by ticks
   under alarm sit on a friend who, inside the 50 ticks after the run
   starts, has a hidden need within 10 of the grave edge or happiness
   under 70 ("approach"); 0.024 see a grave tick of the friend inside
   the window after the run has ended ("grave-after"); 0.248 ± 0.045
   by runs and 0.090 ± 0.037 by ticks are "no approach". The post-hoc
   null: a 50-tick window started at any tick of a covered friend's
   slice classes approach 0.028 and grave-after 0.009 (per-tick
   ADJACENT 0.0132, need within 10 of the edge 0.0018, GRAVE 0.0053).
   The frozen probe's fewer runs are still more approach-or-grave by
   runs (0.848 ± 0.062; the surplus is grave-after, 0.142 against
   0.024), so **P21 is NOT MET on its second clause** (0.752 is not above 0.848) while its first clause
   holds (0.752 ≥ 0.5).
2. **A covered friend's natural crossing is detected at least as well
   as the scripted friend's (D2).** On the confirming half's covered
   friends — 251 natural grave crossings with H ≥ 100 (753
   observer-episodes, 518 in sight at the crossing) — the retrained
   head detects 0.971 ± 0.012 at S (frozen 0.564 ± 0.066), median
   latency 0.0, anticipated 0.923 ± 0.033 with a median lead of 51.3 ±
   8.4 ticks, under fog 0.956 ± 0.016. **P22 MET** (bar 0.7721, the
   midpoint of the splice at H = 100 at 0.05, 0.6567, and the scripted
   N-stratum mean at S, 0.8875). The 35 validation worlds read the same
   (0.980 ± 0.020 on 147 observer-episodes; caveat below).
3. **Persistence halves the covered false runs at k = 10, at a price
   (D3; P23 MET at k = 10 only).** On the tuning half, arm N, counting
   an alarm only after 10 consecutive ticks removes 0.534 of covered-
   friend false runs (2.7971 → 1.3048 per 10,000) with the N-stratum
   mean detection 0.938 → 0.901 (−0.037, inside the 0.05 clause) and
   the median lead 47.4 → 35.0 ticks; outside the clause it takes T-H0
   1.000 → 0.720 and E-H1 0.865 → 0.778. No other k qualifies.
4. **The need-means filter does not halve them at under 0.05
   detection cost (D4; P24 NOT MET).** λ = 70 removes 0.446 at −0.035;
   λ = 80 removes 0.719 at −0.096. The retrained head names the
   crossing need in 0.911–0.989 of N-stratum observer-episodes (frozen
   0.643–0.708).
5. **What "0.05" means (D5).** On covered friends in arm N, a tick in
   the retrained head's [0.05, 0.10) bin (mean P 0.0718) is grave now
   in 0.0329 ± 0.0141 and grave within 50 ticks in 0.2028 ± 0.0598;
   on the scripted friend 0.1025 ± 0.0027 now, 0.4635 ± 0.0229 within
   50. The frozen probe in the same bin: 0.3647 ± 0.0370 now on covered
   friends, 0.6839 ± 0.0866 on the scripted friend — under-confident by
   5–10× where the retrained head is off by about 2× (over, on covered
   friends) and 1.4× (under, on the scripted). ECE on grave-now, arm N: covered
   0.0018 ± 0.0006 retrained against 0.0032 ± 0.0004 frozen; scripted
   0.0050 ± 0.0011 against 0.0818 ± 0.0116.

## What ran

`diag_1e.py content` (50 s), `covered` (60 s), `persistence` (50 s),
`means` (56 s), `reliability` (52 s), `score`; then `content` and
`context` (post-hoc) again at beea07d1 after the approach split and the
null were added. Halves as declared: D1 / D2 / D5 on the confirming
half (T 25, E 40, N 115 worlds), D3 / D4 on the tuning half (the same
counts), every world through `needy_read.refuse_unless`. The validation
worlds: 35 (TN 25, TE 10). Outputs in `reads/`.

## D1 — the false runs' content (`reads/content.md`; null in `reads/context.md`, post-hoc)

Definitions (DECLARATION §4): a false run is the ladder's (a run on a
covered friend's slice touching no grave tick; on the scripted friend,
also not an anticipation run and from its first mask); its window is
[t0, t0 + 50) from the run's first tick; grave-after = a grave tick of
the friend inside the window; approach = the friend's worst hidden need
within 10 of 90, or happiness under 70, at any tick of the window; no
approach = neither.

**Arm N, covered friends, S (115 worlds; 8,280,000 observer-ticks of
the class per seed).**

| head | partition | runs | share of runs | share of ticks under alarm | per 10k observer-ticks | per observer per 1,000 ticks | mean run length | rising at start | in sight at start |
|---|---|---|---|---|---|---|---|---|---|
| retrained | grave-after | 47.3 ± 20.3 | 0.024 ± 0.002 | 0.007 ± 0.001 | 0.0572 ± 0.0245 | 0.0171 ± 0.0073 | 5.2 ± 0.5 | 0.939 ± 0.053 | 0.789 ± 0.077 |
| retrained | approach | 1424.0 ± 553.5 | 0.728 ± 0.046 | 0.903 ± 0.038 | 1.7198 ± 0.6685 | 0.5159 ± 0.2005 | 22.0 ± 3.4 | 0.862 ± 0.029 | 0.712 ± 0.050 |
| retrained | no approach | 516.0 ± 314.5 | 0.248 ± 0.045 | 0.090 ± 0.037 | 0.6232 ± 0.3798 | 0.1870 ± 0.1139 | 6.2 ± 0.9 | 0.441 ± 0.105 | 0.712 ± 0.037 |
| frozen | grave-after | 73.3 ± 25.9 | 0.142 ± 0.016 | 0.113 ± 0.040 | 0.0886 ± 0.0313 | 0.0266 ± 0.0094 | 10.4 ± 4.4 | 0.890 ± 0.031 | 0.753 ± 0.133 |
| frozen | approach | 372.0 ± 153.7 | 0.706 ± 0.050 | 0.818 ± 0.035 | 0.4493 ± 0.1857 | 0.1348 ± 0.0557 | 14.9 ± 1.2 | 0.854 ± 0.075 | 0.739 ± 0.169 |
| frozen | no approach | 77.0 ± 32.0 | 0.152 ± 0.062 | 0.069 ± 0.004 | 0.0930 ± 0.0387 | 0.0279 ± 0.0116 | 6.7 ± 3.3 | 0.462 ± 0.118 | 0.521 ± 0.119 |

Approach-or-grave share of runs: retrained 0.752 ± 0.045, frozen 0.848
± 0.062. The approach class split by its clause (share of all runs):
retrained, by the worst need within 10 of the edge 0.162 ± 0.033, by
happiness under 70 alone 0.566 ± 0.034; frozen 0.325 ± 0.070 and 0.381
± 0.102. Sensitivity of the retrained shares to the window: W = 20,
grave-after 0.005 / approach 0.720 / no approach 0.275; W = 100, 0.059
/ 0.712 / 0.229.

**The null (post-hoc `context`, arm N, covered friends, 2,760,000
window starts):** grave-after 0.009, approach 0.028, no approach 0.963;
per-tick base rates GRAVE 0.0053, ADJACENT 0.0132, worst need within 10
of the edge 0.0018. The retrained head's false-run windows class
approach 26× the null's rate (0.728 / 0.028); the frozen's 25×.

**The excess, attributed** (derived from the reads' stored seed means,
four decimals, which the tables print at three or four: runs
per 10,000 per partition, retrained minus frozen, total 2.4002 − 0.6308
= 1.7694; ticks under alarm per 10,000 = the class total, rate × mean
run length (42.69 against 8.11, excess 34.58), × each partition's share
of ticks):

| partition | excess runs per 10k | share of the excess runs | excess ticks under alarm per 10k | share of the excess ticks |
|---|---|---|---|---|
| grave-after | −0.0314 | −0.018 | −0.61 | −0.018 |
| approach | +1.2705 | +0.718 | +31.93 | +0.923 |
| no approach | +0.5302 | +0.300 | +3.28 | +0.095 |

In her units, a covered observer at S spends per 1,000 ticks (derived:
ticks under alarm per 10,000 of the class × 3 / 10, from the seed-mean
products) roughly 11–12 ticks under an alarm on a friend who approaches
or is adjacent inside the window, about 1.2 ticks on a friend who is
not, and about 0.1 on a friend who then crosses after the run ended;
the frozen probe about 2.0 / 0.2 / 0.3.

**Other arms and the scripted friend** (`reads/content.md`): arm E
covered friends, retrained, approach 0.761 ± 0.036 / no approach 0.201
± 0.044 (null approach 0.038); arm T covered friends 0.308 ± 0.206 /
0.692 ± 0.206 on 14.7 runs per seed (0.1222 per 10,000; null approach
0.002). The scripted friend's between-episode runs in arm N: approach
0.543 ± 0.014, no approach 0.455 ± 0.015, against a null of 0.102 /
0.730 with grave-after 0.168 — a friend near the edge by construction;
drawn on for nothing here.

## D2 — covered friends' natural crossings (`reads/covered.md`)

A covered crossing is a maximal GRAVE run on a covered friend's truth
stream, observed by the other three covered seats; H is its offset
from the world's start; lead = crossing − the start of the alarm run
that contains the crossing (or the first alarm tick of the episode)
when that run started before the crossing. A printed rate needs 20
observer-episodes.

**Confirming half** (80 of 180 worlds hold a covered episode).

| group | cell | friend episodes | observer-episodes | in sight | H median | retrained detected | frozen detected | retrained median latency | retrained p90 latency | retrained anticipated | retrained median lead | retrained in sight det | retrained fog det | edge need / hap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N-H3 | S | 18 | 54 | 31 | 656 | 0.963 ± 0.032 | 0.525 ± 0.084 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.957 ± 0.028 | 45.3 ± 7.6 | 1.000 ± 0.000 | 0.913 ± 0.075 | 16 / 2 |
| N-H4 | S | 212 | 636 | 447 | 3368 | 0.979 ± 0.013 | 0.570 ± 0.062 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.928 ± 0.031 | 52.0 ± 7.8 | 0.984 ± 0.011 | 0.967 ± 0.017 | 143 / 69 |
| N-H≥100 | S | 236 | 708 | 492 | 3274 | 0.975 ± 0.012 | 0.569 ± 0.064 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.928 ± 0.030 | 51.3 ± 8.4 | 0.982 ± 0.010 | 0.958 ± 0.017 | 163 / 73 |
| E-H≥100 | S | 15 | 45 | 26 | 454 | 0.918 ± 0.013 | 0.481 ± 0.090 | 0.0 ± 0.0 | 2.0 ± 3.5 | 0.844 ± 0.080 | 48.0 ± 6.1 | 0.910 ± 0.022 | – | 12 / 3 |
| all-H≥100 | S | 251 | 753 | 518 | 3081 | 0.971 ± 0.012 | 0.564 ± 0.066 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.923 ± 0.033 | 51.3 ± 8.4 | 0.978 ± 0.011 | 0.956 ± 0.016 | 175 / 76 |
| all-H≥100 | t0.10-B0 | 251 | 753 | 518 | 3081 | 0.955 ± 0.017 | 0.474 ± 0.076 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.877 ± 0.053 | 41.8 ± 5.8 | 0.963 ± 0.017 | 0.936 ± 0.019 | 175 / 76 |

Cells under 20 observer-episodes (E-H2 6, N-H2 18) print their counts
only. The frozen probe's median latency on all-H≥100 at S is 0.0 with a
p90 of 52.8 ± 21.7 (retrained 0.0); its anticipation 0.358 ± 0.064
with a median lead of 25.3 ± 4.7. Arm T's covered friends hold no
grave episode on the confirming half (no row).

**P22**: all-H≥100 at S, retrained, 0.971 against the bar 0.7721 →
MET. The scripted friend's N-stratum figure at S (0.8875 mean) is
below the covered friends' on the same worlds: as a proxy it
understates.

**The 35 validation worlds** (Phase 1e's; they chose the stopping
epoch — a second reading, never pooled): 13 hold a covered episode; 49
friend episodes with H ≥ 100 (46 TN, 3 TE; 147 observer-episodes),
retrained 0.980 ± 0.020 detected, 0.932 ± 0.038 anticipated, median
lead 49.0 ± 6.1; frozen 0.526 ± 0.032.

## D3 — persistence (`reads/persistence.md`; tuning half)

**Run lengths at k = 1, retrained head, arm N** (runs over all three
seeds): covered-friend false runs n 6,948, median 9.0 ± 2.6 ticks,
mean 18.1 ± 3.3, p90 49.0 ± 8.1, bands [1, 2) 1,100 / [2, 5) 1,418 /
[5, 10) 1,206 / [10, 20) 1,230 / [20, 50) 1,355 / [50, 100) 561 / 100+
78; anticipation runs on the scripted friend's first episode n 2,082,
lead (start to crossing) median 43.7 ± 9.6, mean 52.2 ± 8.6, p90 96.9
± 10.2; whole run median 37.2 ± 20.9, mean 116.5 ± 24.6. The frozen
head's covered false runs: median 8.0 ± 0.0, mean 13.3 ± 1.5 (n
1,758); its anticipation leads median 35.7 ± 10.3.

**The ladder, retrained head, arm N at S** (N mean = mean of N-H2 /
H3 / H4 detection):

| k | T-H0 | E-H1 | N-H2 | N-H3 | N-H4 | N mean | loss | N median lead | FA covered /10k | removed | ticks under FA /10k | FA scripted-from-mask /10k | runs per observer per 1,000 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.000 | 0.865 | 0.952 | 0.918 | 0.943 | 0.938 | 0.000 | 47.4 | 2.7971 | 0.000 | 50.7 | 4.8720 | 0.8391 |
| 2 | 1.000 | 0.858 | 0.950 | 0.909 | 0.935 | 0.931 | 0.006 | 46.1 | 2.3559 | 0.158 | 47.5 | 3.9254 | 0.7068 |
| 3 | 1.000 | 0.847 | 0.948 | 0.900 | 0.932 | 0.927 | 0.011 | 44.5 | 2.0974 | 0.250 | 44.9 | 3.3868 | 0.6292 |
| 5 | 1.000 | 0.837 | 0.941 | 0.887 | 0.924 | 0.917 | 0.021 | 41.4 | 1.7882 | 0.361 | 40.5 | 2.6863 | 0.5365 |
| 10 | 0.720 | 0.778 | 0.933 | 0.857 | 0.911 | 0.901 | 0.037 | 35.0 | 1.3048 | 0.534 | 32.2 | 1.7693 | 0.3914 |
| 20 | 0.637 | 0.719 | 0.898 | 0.789 | 0.875 | 0.854 | 0.084 | 29.4 | 0.8120 | 0.710 | 21.3 | 1.1449 | 0.2436 |
| 30 | 0.440 | 0.646 | 0.843 | 0.719 | 0.815 | 0.792 | 0.146 | 28.8 | 0.5624 | 0.799 | 14.6 | 0.9494 | 0.1687 |
| 50 | 0.280 | 0.524 | 0.762 | 0.619 | 0.677 | 0.686 | 0.252 | 28.0 | 0.3112 | 0.889 | 7.4 | 0.6990 | 0.0934 |

The N median latency stays 0.0 through k = 20 (0.7 at 30, 11.1 at 50).
The frozen probe's ladder is in the read; at k = 10 it removes 0.539 at
a loss of 0.058.

**P23**: k = 10 qualifies (removed 0.534 ≥ 0.5, loss 0.037 < 0.05);
k = 5 removes 0.361, k = 20 loses 0.084 → MET at one cell. Its costs
outside the clause: T-H0 1.000 → 0.720, E-H1 0.865 → 0.778, median
lead 47.4 → 35.0 (−12.4 ticks).

## D4 — the need-means filter (`reads/means.md`; tuning half)

| λ | T-H0 | E-H1 | N-H2 | N-H3 | N-H4 | N mean | loss | N median lead | FA covered /10k | removed | ticks under FA /10k | FA scripted-from-mask /10k |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 1.000 | 0.865 | 0.952 | 0.918 | 0.943 | 0.938 | 0.000 | 47.4 | 2.7971 | 0.000 | 50.7 | 4.8720 |
| 50 | 1.000 | 0.865 | 0.952 | 0.911 | 0.935 | 0.933 | 0.005 | 44.6 | 2.5821 | 0.077 | 43.9 | 3.1645 |
| 60 | 0.997 | 0.851 | 0.950 | 0.907 | 0.930 | 0.929 | 0.009 | 42.6 | 2.1900 | 0.217 | 34.5 | 2.4205 |
| 70 | 0.973 | 0.812 | 0.948 | 0.869 | 0.893 | 0.903 | 0.035 | 38.6 | 1.5483 | 0.446 | 22.2 | 1.6062 |
| 80 | 0.873 | 0.677 | 0.919 | 0.791 | 0.815 | 0.842 | 0.096 | 28.5 | 0.7854 | 0.719 | 8.7 | 0.8214 |
| 90 | 0.723 | 0.503 | 0.731 | 0.613 | 0.607 | 0.650 | 0.288 | 18.1 | 0.2025 | 0.928 | 1.5 | 0.2391 |

**P24**: no λ removes 0.5 at a loss under 0.05 → NOT MET. Naming at
the crossing (the argmax of the five means equals the truth's worst
need, need-edge crossings): retrained N-H2 0.911 ± 0.018 (n 128), N-H3
0.952 ± 0.003 (172), N-H4 0.989 ± 0.019 (120), E-H1 0.956 ± 0.020
(76); frozen 0.643 / 0.647 / 0.708 / 0.759.

## D5 — reliability (`reads/reliability.md`; confirming half, every covered observer slice after the burn-in)

Arm N, the pick's bin [0.05, 0.10) and the whole curve's summary:

| head | class | n per seed | base rate grave-now | ECE grave-now | bin n | bin mean P | grave now | within 10 | within 50 |
|---|---|---|---|---|---|---|---|---|---|
| retrained | covered friends | 8,277,240 | 0.0053 | 0.0018 ± 0.0006 | 18,358 ± 3,055 | 0.0718 | 0.0329 ± 0.0141 | 0.0553 ± 0.0267 | 0.2028 ± 0.0598 |
| retrained | scripted | 2,759,080 | 0.1074 | 0.0050 ± 0.0011 | 42,567 ± 2,709 | 0.0721 | 0.1025 ± 0.0027 | 0.1661 ± 0.0102 | 0.4635 ± 0.0229 |
| frozen | covered friends | 8,277,240 | 0.0053 | 0.0032 ± 0.0004 | 10,163 ± 1,882 | 0.0711 | 0.3647 ± 0.0370 | 0.4301 ± 0.0411 | 0.6044 ± 0.0651 |
| frozen | scripted | 2,759,080 | 0.1074 | 0.0818 ± 0.0116 | 32,876 ± 3,952 | 0.0722 | 0.6839 ± 0.0866 | 0.7257 ± 0.0733 | 0.8352 ± 0.0463 |

The retrained head's curve on covered friends is monotone and
over-confident by 1.2–2.7× from the [0.01, 0.02) bin up (bin [0.5, 1]:
mean P 0.8335, realised 0.6982); on the scripted friend it is
under-confident by 1.0–2.1× from the same bin up (2.6× in the lowest
bin; bin [0.5, 1] 0.8845 against 0.8931). The
frozen probe is under-confident in every arm N bin (covered friends,
bin [0.01, 0.02): mean P 0.0142, realised 0.1484). Arm E and arm T rows
are in the read; the ECE figures are small on covered friends for both
heads because most ticks sit in the lowest bin (arm N: about 0.98 of
the retrained head's, 0.99 of the frozen's).

## Predictions scored (DECLARATION §6)

| prediction | clause | value | bar | result |
|---|---|---|---|---|
| P21 | approach-or-grave share of covered false runs, arm N confirming, S, retrained | 0.752 | ≥ 0.5 | holds |
| P21 | … and above the frozen probe's | 0.752 vs 0.848 | above | fails |
| **P21** | | | | **NOT MET** |
| **P22** | covered crossings H ≥ 100, confirming, S, retrained, detected (753 observer-episodes ≥ 20) | 0.971 | > 0.7721 | **MET** |
| **P23** | some k: covered false runs removed ≥ 0.5 and N mean detection loss < 0.05 | k = 10: 0.534, 0.037 | | **MET** |
| **P24** | some λ: the same | λ = 70: 0.446, 0.035; λ = 80: 0.719, 0.096 | | **NOT MET** |

Unscored expectations (DECLARATION §6), checked: D1's no-approach
share higher on the frozen — not borne out in arm N (0.152 frozen,
0.248 retrained); in arm E it is nominally borne out (0.250 ± 0.309
against 0.201 ± 0.044) and in arm T not (0.603 ± 0.531 against 0.692
± 0.206), both on few runs inside large SDs; D2's fog detection below in-sight — borne out, narrowly
(0.956 against 0.978); D3's anticipation runs longer than the false
runs at the median — borne out (43.7 lead / 37.2 whole run against
9.0); D4 cutting lead more than D3 at equal removal — on the retrained head,
borne out at the low cells (λ = 50 / 60 cost 2.8 / 4.8 ticks of lead
for 0.077 / 0.217 removed against k = 2 / 3's 1.3 / 2.9 for 0.158 /
0.250) and about equal from λ = 70 up (8.8 for 0.446 against k = 5 /
10's 6.0 / 12.4 for 0.361 / 0.534; λ = 80 18.9 for 0.719 against
k = 20's 17.9 for 0.710; λ = 90 has no D3 cell at its removal); on the
frozen head D4 costs more lead at λ = 50 / 60 / 70 / 80 than D3 at the
same removal; D5's realised rate in the
pick's bin higher on the retrained head — not borne out, it is lower
(0.0329 against 0.3647 on covered friends): the frozen probe is
under-confident on these worlds; the retrained head is over-confident
by about 2× on covered friends and under-confident by 1.4× on the
scripted.

## Decision rules applied (DECLARATION §6)

- **P21 NOT MET** by the relative clause. The rule as written reads
  "the excess is mostly noise; D4's rows and a Phase 1f composition
  arm are the remedies, her call which". The partition itself says
  otherwise and both are reported: by the first clause and the
  post-hoc null, the retrained head's covered false runs are three
  quarters approach by runs and nine tenths by ticks, 26× the null;
  the excess over the frozen probe is 0.718 approach by runs and 0.923
  by ticks under alarm. What the relative clause caught is that the
  frozen probe's few runs are even more approach-or-grave (0.848; the
  surplus is grave-after, 0.142 against 0.024; by the approach class
  alone the frozen is lower, 0.706 against 0.728). The
  noise part is the no-approach quarter: 0.6232 per 10,000 against the
  frozen's 0.0930 (6.7×), short runs (6.2 ticks), 0.441 rising at
  start — about 1.2 observer-ticks per observer per 1,000 ticks. The
  rule's remedies apply to that quarter, if she wants it removed; D4
  does not separate it (the filter was not read against the
  partition). Her call.
- **P22 MET**: the scripted friend is a fair proxy and a conservative
  one (0.8875 scripted against 0.971 covered at S on the same worlds);
  the Phase 2 declaration may cite the scripted figures with D2's
  covered figures beside.
- **P23 MET at k = 10**: a persistence rule is a Phase 2 consumer
  option, priced here on the tuning half; its confirming read is
  Phase 2's. Its cost outside the clause (T-H0 1.000 → 0.720, E-H1
  0.865 → 0.778, −12.4 ticks of lead) goes beside it.
- **P24 NOT MET**: the means filter is closed as a halving filter on
  this head; λ = 70 (0.446 removed at −0.035) is reported for Phase 2.
- A FINDINGS entry: D2 stands alone (F-073); D1's partition is its
  price caveat.

## What stands alone

F-073: the retrained head NF1e-h24+p detects a COVERED friend's natural
crossing into grave after 208–5,887 ticks of lived history in 0.971 of
observer-episodes at her operating point (251 crossings, 753
observer-episodes, the needy set's confirming half), at the crossing
(median latency 0.0), anticipating in 0.923 with a median lead of 51.3
ticks, under fog 0.956 — against the frozen probe's 0.564 on the same
episodes — and its covered-friend false runs beside a refusing friend
are three quarters attention on a friend who approaches the grave edge
or falls under happiness 70 inside the next 50 ticks (26× a random
window's rate), one quarter not.

## Guards and reds

g1–g7 red on record before any read (DECLARATION §7; g7 one guard fix
and re-red). Guards of construction that held in the reads themselves:
the shared forward reproduces `needy_read.probe_world` to 0.0 and the
head's committed prediction file (g5); D3's k = 1 and D4's λ = 0 cells
reproduce Phase 1e's committed confirming record on the guard world
(g6), and their k = 1 / λ = 0 rows on the tuning half equal Phase 1e's
tuning grid at the pick (`minifriend-phase1e-2026-11-01/reads/tuning.json`:
2.7971 covered false runs per 10,000, N-H2 / H3 / H4 0.952 / 0.918 /
0.943).
The `context` read has no guard of its own beyond `window_any`'s
hand check at its commit; it is post-hoc and scores nothing.

## Limitations

1. "Approach" is a truth-side partition with a thread-chosen window
   (50 ticks) and cut (10 need points; happiness under 70). The
   happiness clause carries most of it (0.566 of runs by happiness
   alone against 0.162 by the need edge). The null is the control for
   the cut's breadth (0.028), not for what the head saw.
2. The null is post-hoc: added after the declared reads had run,
   because the declared partition had no control. It is a rate over
   every window start, not over windows matched to the alarms'
   conditions (in sight, rising).
3. D2's covered crossings are 212 of 251 in N-H4; H2 is too thin to
   print (18 observer-episodes); arm T's covered friends hold none.
   The validation worlds' rows are a second reading under their caveat.
4. D3 / D4 are ladders on the tuning half; k = 10 and λ = 70 were
   read, not selected; any confirming read of either is a new
   declaration's. P23's clause looks at the N strata only; the T-H0
   and E-H1 costs are outside it and printed.
5. D5's within-h labels are a reading aid; the probe was trained on
   grave-now. The lowest bin holds about 0.98 of the ticks, so the ECE
   is small whatever the upper bins do; its contribution comes mostly
   from the upper bins.
6. The confirming half's multiplicity grew by no cell; three
   accountings of the same alarms at S (D1, D2, D5), D2 also at the
   registered point already read by Phase 1e, and the null over every
   window start, which reads no alarm.
7. The excess attribution derives from seed-mean products (rate ×
   mean run length), not per-seed products.

## Regeneration (reads)

```
### Read (the gate runs these; fresh outputs to its scratchpad, never over reads/)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $D/diag_1e.py content     --out <scratch>/content.json     --md --quiet   # about 50 s
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $D/diag_1e.py context     --out <scratch>/context.json     --md --quiet   # about 10 s (post-hoc)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $D/diag_1e.py covered     --out <scratch>/covered.json     --md --quiet   # about 60 s
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $D/diag_1e.py persistence --out <scratch>/persistence.json --md --quiet   # about 50 s
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $D/diag_1e.py means       --out <scratch>/means.json       --md --quiet   # about 60 s
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $D/diag_1e.py reliability --out <scratch>/reliability.json --md --quiet   # about 50 s
```

(`A` = `experiments/needy-set-2026-10-28`, `D` =
`experiments/minifriend-phase1e-diag-2026-11-02`, absolute paths in
use; `score` gathers from `reads/` and is a copy, not a read.)

**Accuracy gate: PASS 2026-11-03, round 4** (rounds 1–3 FAIL on wording
and precision only; every regenerated number equal in every round: the
six reads' JSON leaf-equal to `reads/` but for `seconds`, the six md
files byte-identical). Round 1: a WEAK in Decision rules ("more
approach-shaped" for an approach-or-grave figure), six D5 cells printed
at 5 decimals from 4-decimal stored means, nine companion digits
coarser than the doc's. Round 2: the D4-vs-D3 lead expectation stated
at one crossing point and reversed over the ladder, a companion
"11.6" not in the doc, an F-068 paraphrase in an attribution. Round 3:
F-073's "four accountings" left behind when the doc recounted to three.
Round 4: all of RESULTS SUPPORTED (about 480 reader-backed cells, about
70 derived, 8 sourced thresholds, about 45 characterisations with 1
WEAK reworded after, 3 UNDECIDABLE guard claims, 14 provenance); one
companion count word ("a tenth" for 0.090) replaced by the digit after
the round, the replacement checked against this document by grep. Raw-dir
hash: not applicable (no new raws; the heads and raws are Phase 1e's
and the needy set's, hashed in their own stamps).
