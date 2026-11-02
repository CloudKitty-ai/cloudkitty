# Probe-rise read — results (2026-11-01; declared 48dae5cf before its data; owner "Ok, let's try it")

Declaration: `DECLARATION.md` (this directory). Reader `rise.py`, guards
`test_rise.py` r1–r4, reads `reads/rise.json` and `reads/rise.md` (the
md is the reader's own print; the tables below are row-subsets of it
with two derived columns added, "× pick" and "mean N gain vs pick",
recomputed from the JSON means, and some of its columns dropped; the
E-H2 figures quoted in the prose come from `reads/rise.json`, which
holds every (arm, stratum) group; a `|L` cell name is escaped in the
tables here and printed raw in `reads/rise.md`). Welfare cost 0 covered cat-ticks: no world ran, no
weight moved; the needy set's raws (`results-raw/set`,
`v1:973e5cf5a4541ba5`) and the frozen NF-h24+p, three probe seeds.

## Headline

**A rule on the probe logit's rise does not buy late detection at the
level rule's false-run price. P12 NOT MET; P13, P14, P15 MET.** On the
tuning half, the only pure `rise` cell whose covered-friend and
scripted-friend false-alarm rates stay at or under her pick's (0.7077
and 1.4965 per 10,000 observer-ticks in arm N) is w10-k3.0, which
detects 0.138 / 0.076 / 0.086 of the N-H2 / H3 / H4 crossings (the pick
0.536 / 0.459 / 0.409). OR-ed with the pick and read on the confirming
half it adds 0.000 / 0.000 / +0.013 to the pick's 0.596 / 0.444 /
0.421, mean gain +0.004 against P12's 0.10. The climb the needy set's
R3 profile showed is in the per-slice logit: at w = 100, k = 0.5 the
pure rise alarm starts a run inside [mask onset, crossing), past the
slice's first alarmable tick, in 0.702 / 0.870 of N-H3 / N-H4
observer-episodes and detects 0.855 / 0.781 / 0.898, but at 36.43
false runs per 10,000 covered-friend observer-ticks, 51 times the
pick's, about one false run per 275 observer-ticks. Between those two
corners the trade-off is steep: no cell within twice the pick's
covered-friend rate gains more than +0.059 in mean N detection (tuning
half; w100-k3.0|L at 1.7×), and the best gain within three times it is
+0.102 (w100-k0.5+f at 2.8×). The false-run rates say why: under the
1d scatter of 0.94 logits per tick, independent tick to tick, the step
statistic's SD would be 0.42 / 0.27 / 0.19 / 0.13 at w = 10 / 25 / 50
/ 100 and k = 3.0 at w = 100 would be 23 SDs out; it fires 0.89 times
per 10,000 observer-ticks on covered friends. The probe's logit on a
clean slice wanders on a scale a two-window statistic cannot average
away. The information recommendation 1 asked about is in the head as
a population mean and as a noisy per-slice trend, not as a per-slice
signal a reader can act on at this price. Recommendation 2 (Phase 1e,
a retrain with late-world graves in the training data) is the next
thing that could move the late-history curve; that call is hers.

## What ran

`rise.py read` once, 62 s: 180 tuning worlds (T 25, E 40, N 115), all
62 cells; the selection rule; then 180 confirming worlds, three cells
(S = w10-k3.0, S|L = w10-k3.0|L, L:t0.05-B2). First-episode status,
tuning: T {H0: 25}; E {H1: 24, H2: 13, unreleased: 3}; N {H2: 35, H3:
45, H4: 32, released_no_crossing: 3}. Confirming: T {H0: 25}; E {H1:
23, H2: 11, released_no_crossing: 1, unreleased: 5}; N {H2: 26, H3:
64, H4: 20, released_no_crossing: 5}. Friend episodes per primary
group, tuning / confirming: T-H0 25 / 25, E-H1 24 / 23, N-H2 35 / 26,
N-H3 45 / 64, N-H4 32 / 20 (E-H2 13 / 11, printed apart). The level
pick's five confirming detection figures re-derived by this reader
equal R5's at three decimals (the reader asserts it before scoring).

## The grid (tuning half)

Columns: arm N covered-friend false-alarm runs per 10,000
observer-ticks and their ratio to the pick's; detection per primary
stratum; the unweighted mean gain over N-H2 / H3 / H4 against the
pick; anticipation past the first alarmable tick per N stratum; N-H3
median latency. Full tables for all 62 cells, every printed column:
`reads/rise.md`; every group and column, `reads/rise.json`.

### Level cells (tuning half)

| cell | FA covered /10k (N) | × pick | T-H0 det | E-H1 det | N-H2 det | N-H3 det | N-H4 det | mean N gain vs pick | N-H2 antic | N-H3 antic | N-H4 antic | N-H3 med lat |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L:t0.05-B2 | 0.71 ± 0.22 | 1.0 | 1.000 ± 0.000 | 0.528 ± 0.091 | 0.536 ± 0.077 | 0.459 ± 0.111 | 0.409 ± 0.144 | +0.000 | 0.150 ± 0.047 | 0.232 ± 0.125 | 0.307 ± 0.098 | 15.8 ± 14.1 |
| L:t0.10-B0 | 1.51 ± 0.98 | 2.1 | 1.000 ± 0.000 | 0.451 ± 0.063 | 0.464 ± 0.088 | 0.407 ± 0.108 | 0.362 ± 0.124 | -0.057 | 0.079 ± 0.025 | 0.180 ± 0.114 | 0.237 ± 0.055 | 24.3 ± 19.9 |

### Rise cells within four times the pick's covered-friend false-alarm rate on the tuning half (every family; sorted by mean N gain; the other 30 cells are in `reads/rise.md`)

| cell | FA covered /10k (N) | × pick | T-H0 det | E-H1 det | N-H2 det | N-H3 det | N-H4 det | mean N gain vs pick | N-H2 antic | N-H3 antic | N-H4 antic | N-H3 med lat |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| w100-k0.5+f | 1.99 ± 0.89 | 2.8 | 0.000 ± 0.000 | 0.226 ± 0.034 | 0.643 ± 0.119 | 0.541 ± 0.080 | 0.526 ± 0.179 | +0.102 | 0.145 ± 0.039 | 0.350 ± 0.125 | 0.427 ± 0.160 | 3.3 ± 4.2 |
| w10-k0.5+f | 2.27 ± 0.98 | 3.2 | 0.460 ± 0.046 | 0.500 ± 0.091 | 0.655 ± 0.082 | 0.502 ± 0.092 | 0.516 ± 0.137 | +0.089 | 0.343 ± 0.100 | 0.385 ± 0.132 | 0.443 ± 0.162 | 6.5 ± 3.0 |
| w25-k0.5+f | 2.13 ± 0.99 | 3.0 | 0.173 ± 0.032 | 0.472 ± 0.100 | 0.664 ± 0.104 | 0.504 ± 0.076 | 0.503 ± 0.126 | +0.089 | 0.352 ± 0.095 | 0.394 ± 0.126 | 0.443 ± 0.162 | 3.3 ± 3.1 |
| w100-k1.0+f | 1.81 ± 0.76 | 2.6 | 0.000 ± 0.000 | 0.212 ± 0.042 | 0.619 ± 0.138 | 0.533 ± 0.088 | 0.508 ± 0.176 | +0.085 | 0.143 ± 0.036 | 0.320 ± 0.129 | 0.417 ± 0.157 | 5.0 ± 6.6 |
| w50-k0.5+f | 2.13 ± 1.01 | 3.0 | 0.010 ± 0.010 | 0.295 ± 0.016 | 0.657 ± 0.108 | 0.528 ± 0.073 | 0.474 ± 0.148 | +0.085 | 0.312 ± 0.111 | 0.376 ± 0.119 | 0.443 ± 0.162 | 7.5 ± 10.9 |
| w25-k1.0+f | 1.94 ± 0.89 | 2.7 | 0.137 ± 0.042 | 0.413 ± 0.116 | 0.650 ± 0.097 | 0.483 ± 0.073 | 0.484 ± 0.129 | +0.071 | 0.319 ± 0.097 | 0.368 ± 0.117 | 0.438 ± 0.157 | 12.8 ± 12.3 |
| w50-k1.0+f | 2.02 ± 0.95 | 2.9 | 0.000 ± 0.000 | 0.271 ± 0.036 | 0.638 ± 0.111 | 0.517 ± 0.082 | 0.445 ± 0.139 | +0.065 | 0.298 ± 0.119 | 0.368 ± 0.122 | 0.435 ± 0.155 | 12.2 ± 12.8 |
| w100-k3.0\|L | 1.22 ± 0.44 | 1.7 | 1.000 ± 0.000 | 0.528 ± 0.091 | 0.600 ± 0.126 | 0.487 ± 0.111 | 0.495 ± 0.174 | +0.059 | 0.238 ± 0.125 | 0.257 ± 0.130 | 0.388 ± 0.164 | 12.0 ± 13.7 |
| w100-k1.5+f | 1.56 ± 0.62 | 2.2 | 0.000 ± 0.000 | 0.191 ± 0.069 | 0.562 ± 0.135 | 0.520 ± 0.087 | 0.479 ± 0.172 | +0.053 | 0.129 ± 0.019 | 0.298 ± 0.116 | 0.398 ± 0.164 | 9.0 ± 11.5 |
| w10-k2.0\|L | 2.41 ± 1.93 | 3.4 | 1.000 ± 0.000 | 0.566 ± 0.124 | 0.564 ± 0.079 | 0.493 ± 0.123 | 0.458 ± 0.141 | +0.037 | 0.317 ± 0.188 | 0.341 ± 0.183 | 0.378 ± 0.141 | 13.5 ± 13.8 |
| w50-k1.5+f | 1.86 ± 0.83 | 2.6 | 0.000 ± 0.000 | 0.254 ± 0.057 | 0.605 ± 0.090 | 0.491 ± 0.079 | 0.398 ± 0.124 | +0.030 | 0.288 ± 0.115 | 0.341 ± 0.132 | 0.417 ± 0.142 | 16.3 ± 14.2 |
| w50-k3.0\|L | 2.07 ± 1.14 | 2.9 | 1.000 ± 0.000 | 0.528 ± 0.091 | 0.555 ± 0.083 | 0.474 ± 0.112 | 0.432 ± 0.152 | +0.019 | 0.371 ± 0.244 | 0.315 ± 0.159 | 0.401 ± 0.161 | 11.0 ± 10.5 |
| w25-k3.0\|L | 1.62 ± 1.11 | 2.3 | 1.000 ± 0.000 | 0.535 ± 0.100 | 0.557 ± 0.069 | 0.459 ± 0.111 | 0.435 ± 0.147 | +0.016 | 0.314 ± 0.227 | 0.291 ± 0.134 | 0.357 ± 0.133 | 10.7 ± 9.2 |
| w100-k2.0+f | 1.28 ± 0.46 | 1.8 | 0.000 ± 0.000 | 0.184 ± 0.074 | 0.517 ± 0.144 | 0.491 ± 0.100 | 0.438 ± 0.156 | +0.014 | 0.107 ± 0.040 | 0.254 ± 0.122 | 0.367 ± 0.160 | 12.3 ± 15.7 |
| w25-k1.5+f | 1.64 ± 0.76 | 2.3 | 0.110 ± 0.072 | 0.333 ± 0.099 | 0.581 ± 0.069 | 0.441 ± 0.070 | 0.417 ± 0.126 | +0.012 | 0.260 ± 0.089 | 0.322 ± 0.112 | 0.406 ± 0.136 | 22.3 ± 13.3 |
| w10-k3.0\|L | 0.73 ± 0.21 | 1.0 | 1.000 ± 0.000 | 0.556 ± 0.117 | 0.540 ± 0.076 | 0.463 ± 0.114 | 0.424 ± 0.146 | +0.008 | 0.162 ± 0.057 | 0.239 ± 0.118 | 0.315 ± 0.110 | 14.7 ± 13.7 |
| w10-k1.0+f | 1.47 ± 0.68 | 2.1 | 0.370 ± 0.020 | 0.351 ± 0.071 | 0.562 ± 0.083 | 0.435 ± 0.061 | 0.424 ± 0.137 | +0.006 | 0.243 ± 0.111 | 0.291 ± 0.084 | 0.349 ± 0.115 | 31.0 ± 19.0 |
| w50-k2.0+f | 1.60 ± 0.71 | 2.3 | 0.000 ± 0.000 | 0.229 ± 0.058 | 0.567 ± 0.078 | 0.433 ± 0.066 | 0.362 ± 0.111 | -0.014 | 0.264 ± 0.118 | 0.294 ± 0.127 | 0.388 ± 0.135 | 20.3 ± 17.6 |
| w100-k3.0 | 0.89 ± 0.36 | 1.3 | 0.000 ± 0.000 | 0.149 ± 0.052 | 0.445 ± 0.173 | 0.398 ± 0.115 | 0.414 ± 0.136 | -0.049 | 0.026 ± 0.018 | 0.169 ± 0.120 | 0.349 ± 0.182 | 21.0 ± 23.3 |
| w25-k2.0+f | 1.21 ± 0.67 | 1.7 | 0.053 ± 0.045 | 0.295 ± 0.093 | 0.493 ± 0.061 | 0.400 ± 0.048 | 0.326 ± 0.105 | -0.062 | 0.198 ± 0.080 | 0.220 ± 0.061 | 0.328 ± 0.081 | 32.8 ± 21.4 |
| w100-k3.0+f | 0.68 ± 0.24 | 1.0 | 0.000 ± 0.000 | 0.149 ± 0.052 | 0.402 ± 0.137 | 0.391 ± 0.126 | 0.357 ± 0.117 | -0.085 | 0.071 ± 0.061 | 0.181 ± 0.133 | 0.312 ± 0.171 | 22.3 ± 23.0 |
| w50-k3.0 | 1.80 ± 1.10 | 2.5 | 0.000 ± 0.000 | 0.181 ± 0.069 | 0.429 ± 0.112 | 0.341 ± 0.062 | 0.284 ± 0.106 | -0.117 | 0.226 ± 0.153 | 0.230 ± 0.126 | 0.326 ± 0.130 | 28.8 ± 21.9 |
| w10-k1.5+f | 0.57 ± 0.42 | 0.8 | 0.230 ± 0.036 | 0.226 ± 0.057 | 0.400 ± 0.068 | 0.344 ± 0.095 | 0.299 ± 0.114 | -0.120 | 0.148 ± 0.046 | 0.165 ± 0.089 | 0.213 ± 0.086 | 58.7 ± 32.1 |
| w50-k3.0+f | 0.90 ± 0.43 | 1.3 | 0.000 ± 0.000 | 0.181 ± 0.069 | 0.400 ± 0.112 | 0.341 ± 0.062 | 0.266 ± 0.088 | -0.133 | 0.152 ± 0.104 | 0.150 ± 0.073 | 0.276 ± 0.099 | 33.8 ± 17.5 |
| w10-k2.0 | 1.74 ± 1.75 | 2.5 | 0.103 ± 0.015 | 0.194 ± 0.068 | 0.314 ± 0.064 | 0.289 ± 0.077 | 0.221 ± 0.107 | -0.193 | 0.229 ± 0.152 | 0.174 ± 0.064 | 0.164 ± 0.078 | 80.7 ± 30.1 |
| w25-k3.0 | 1.09 ± 1.04 | 1.5 | 0.013 ± 0.023 | 0.163 ± 0.074 | 0.321 ± 0.047 | 0.270 ± 0.045 | 0.195 ± 0.092 | -0.206 | 0.248 ± 0.237 | 0.137 ± 0.042 | 0.201 ± 0.082 | 51.2 ± 25.1 |
| w25-k3.0+f | 0.40 ± 0.40 | 0.6 | 0.013 ± 0.023 | 0.153 ± 0.061 | 0.321 ± 0.047 | 0.269 ± 0.048 | 0.193 ± 0.088 | -0.207 | 0.074 ± 0.034 | 0.089 ± 0.035 | 0.169 ± 0.071 | 60.8 ± 36.6 |
| w10-k2.0+f | 0.17 ± 0.09 | 0.2 | 0.103 ± 0.015 | 0.156 ± 0.038 | 0.290 ± 0.065 | 0.267 ± 0.073 | 0.213 ± 0.101 | -0.211 | 0.074 ± 0.042 | 0.085 ± 0.059 | 0.075 ± 0.037 | 77.7 ± 34.2 |
| w10-k3.0 | 0.03 ± 0.01 | 0.0 | 0.010 ± 0.010 | 0.087 ± 0.026 | 0.138 ± 0.011 | 0.076 ± 0.021 | 0.086 ± 0.021 | -0.368 | 0.019 ± 0.027 | 0.013 ± 0.012 | 0.016 ± 0.021 | 168.8 ± 60.2 |
| w10-k3.0+f | 0.02 ± 0.01 | 0.0 | 0.010 ± 0.010 | 0.066 ± 0.006 | 0.138 ± 0.011 | 0.074 ± 0.022 | 0.086 ± 0.021 | -0.369 | 0.009 ± 0.011 | 0.011 ± 0.010 | 0.008 ± 0.008 | 175.0 ± 67.3 |

30 cells within 4 × 0.7077 = 2.8308 per 10,000; 30 outside.

### The best-detecting cell per family regardless of price (tuning half)

| cell | FA covered /10k (N) | × pick | T-H0 det | E-H1 det | N-H2 det | N-H3 det | N-H4 det | mean N gain vs pick | N-H2 antic | N-H3 antic | N-H4 antic | N-H3 med lat |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| w100-k0.5 | 36.43 ± 2.38 | 51.5 | 0.000 ± 0.000 | 0.226 ± 0.034 | 0.855 ± 0.142 | 0.781 ± 0.075 | 0.898 ± 0.098 | +0.377 | 0.045 ± 0.046 | 0.702 ± 0.013 | 0.870 ± 0.047 | 0.0 ± 0.0 |
| w100-k0.5+f | 1.99 ± 0.89 | 2.8 | 0.000 ± 0.000 | 0.226 ± 0.034 | 0.643 ± 0.119 | 0.541 ± 0.080 | 0.526 ± 0.179 | +0.102 | 0.145 ± 0.039 | 0.350 ± 0.125 | 0.427 ± 0.160 | 3.3 ± 4.2 |
| w100-k0.5\|L | 36.50 ± 2.37 | 51.6 | 1.000 ± 0.000 | 0.542 ± 0.075 | 0.855 ± 0.142 | 0.789 ± 0.082 | 0.898 ± 0.098 | +0.379 | 0.464 ± 0.247 | 0.852 ± 0.107 | 0.870 ± 0.047 | 0.0 ± 0.0 |

**How the grid reads.** Pure `rise` cells trade detection for false
runs steeply: at k = 0.5 the covered-friend rate is
183.15 / 112.01 / 67.02 / 36.43 per 10,000 at w = 10 / 25 / 50 / 100
(a run every 55 to 275 observer-ticks) with N detection 0.71–0.91; at
k = 3.0 it is 0.03 / 1.09 / 1.80 / 0.89 with N detection 0.08–0.45.
The floor (`rise+f`, P ≥ 0.01) cuts the false runs by more than half
in 17 of the 20 cells (not at k = 3.0 for w = 10, 50, 100) and keeps
part of the detection: w100-k0.5+f detects 0.643 /
0.541 / 0.526 at 1.99 per 10,000 (2.8× the pick), the largest mean
gain among cells within three times the pick's rate (+0.102). The
consumer rule (`rise|L`) keeps T-H0 at 1.000 in every cell and E-H1
at or above the pick's 0.528 (0.528–0.691), and its gains come with
most of the rise cell's false runs on top of the pick's (sub-additive:
w100-k3.0|L runs at 1.22 against 0.89 + 0.71): w100-k3.0|L +0.059 at
1.22 (1.7×), w100-k2.0|L +0.131 at 3.34 (4.7×), w100-k0.5|L +0.379 at
36.50 (51.6×). Where the rise alarm fires it fires early: at w = 100,
k ≤ 1.0 the N-H3 median latency is 0.0 and anticipation is
0.600–0.702 in N-H3 and 0.807–0.870 in N-H4 (N-H2's anticipation
windows lie mostly before the statistic is defined at tick 199: 5,549
of their 6,120 ticks, with 16 of the 35 crossings themselves before
it; hence its 0.045–0.050). A pure rise rule
misses the reset: T-H0 detection 0.460 at w10-k0.5 (the scatter after
the first-frame fall), 0.173 at w25-k0.5, 0.010 at w50-k0.5 and 0.000
at every other w ≥ 50 cell. Arm E is not helped at any price near the
pick's: within four times the pick's covered-friend rate the highest
E-H1 is 0.566 (w10-k2.0|L) against the pick's 0.528, and the highest
E-H2 (13 episodes, apart) is 0.340 (w50-k3.0|L) against 0.301; pure
rise E-H1 runs 0.087–0.594 over the grid, its top at w10-k0.5 (259
times the pick's rate), and E-H2 reaches 0.494 pure and 0.526 OR-ed
only at w50-k0.5 (95 times the pick's rate).

## Selection and the confirming read

Declared rule: pure `rise` cells with arm N covered-friend AND
scripted-from-first-mask false-alarm rates at or under the pick's on
the tuning half (0.7077 and 1.4965 per 10,000); the highest mean
detection over N-H2 / H3 / H4; ties to the smaller w, then k. One
candidate: **w10-k3.0** (tuning: mean N detection 0.100, covered
0.0330, scripted from first mask 0.0661 per 10,000). Five `rise+f`
cells also sit under both bounds (w10-k3.0+f, w10-k2.0+f, w25-k3.0+f,
w10-k1.5+f, w100-k3.0+f); the rule was declared on the pure family and
is applied as declared, and none of the five detects more than the
pick (mean N gains −0.369 to −0.085, the table above).

Confirming half (180 worlds; S, S|L and the pick, same accounting;
`reads/rise.md` verbatim):

| cell | T-H0 det | E-H1 det | N-H2 det | N-H3 det | N-H4 det | N-H2 antic | N-H3 antic | N-H4 antic | N-H2 med lat | N-H3 med lat | N-H4 med lat | FA covered /10k (N) | FA scripted from mask /10k (N) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| w10-k3.0 | 0.000 ± 0.000 | 0.145 ± 0.107 | 0.099 ± 0.020 | 0.079 ± 0.046 | 0.029 ± 0.026 | 0.019 ± 0.010 | 0.021 ± 0.004 | 0.017 ± 0.029 | 58.0 ± 46.5 | 92.0 ± 22.9 | 47.0 ± 66.5 | 0.03 ± 0.02 | 0.12 ± 0.04 |
| w10-k3.0\|L | 1.000 ± 0.000 | 0.511 ± 0.033 | 0.596 ± 0.092 | 0.444 ± 0.110 | 0.433 ± 0.155 | 0.266 ± 0.053 | 0.220 ± 0.084 | 0.275 ± 0.108 | 23.3 ± 12.0 | 34.3 ± 27.8 | 2.3 ± 3.2 | 0.66 ± 0.22 | 1.53 ± 0.65 |
| L:t0.05-B2 | 1.000 ± 0.000 | 0.489 ± 0.022 | 0.596 ± 0.092 | 0.444 ± 0.110 | 0.421 ± 0.134 | 0.253 ± 0.059 | 0.211 ± 0.077 | 0.275 ± 0.108 | 23.7 ± 12.1 | 35.0 ± 26.7 | 2.3 ± 3.2 | 0.63 ± 0.23 | 1.47 ± 0.65 |

S alone on the confirming half detects 0.099 / 0.079 / 0.029 of the N
crossings (tuning 0.138 / 0.076 / 0.086) and none of the resets. E-H2
on the confirming half: 0.386 at S|L and at the pick, 0.030 at S (11
episodes, apart).

## Predictions scored (§6; S|L against the pick on the confirming half)

- **P12** (the climb is readable: S|L above the pick in each N stratum
  AND mean gain ≥ 0.10) — **NOT MET**: S|L 0.596 / 0.444 / 0.433
  against the pick's 0.596 / 0.444 / 0.421, gains 0.000 / 0.000 /
  +0.013, mean +0.004; clause 1 fails in N-H2 and N-H3 (equal, not
  above), clause 2 fails.
- **P13** (no help where there is no climb; no harm to the reset: E-H1
  within ±0.05, T-H0 1.000) — **MET**: E-H1 0.511 against 0.489
  (+0.022); T-H0 1.000.
- **P14** (the price: S|L's arm N covered-friend false alarms ≤ 1.5
  per 10,000) — **MET**: 0.655 against the pick's 0.631.
- **P15** (a late detector, not an early warning: anticipation gain
  < 0.10 in every N stratum) — **MET**: gains +0.013 / +0.009 / 0.000.

P13 to P15 are met because S adds almost nothing to the pick (S's
own false-run rate is 0.03 per 10,000, its N detection 0.03–0.10 and
its E-H1 0.145);
they are met trivially and say nothing about a rise rule that
detects. P12 is the prediction that carried the question, and it
fails under the declared rule.

**Expectations stated, not scored**, against the grid: pure rise
T-H0 near 0 — holds for w ≥ 50 (0.000–0.010) and at k = 3.0 for every
w (0.000–0.013), not at k ≤ 2.0 for w = 10 (0.103–0.460) or w = 25
(0.053–0.173), where the scatter after the first-frame fall fires the
statistic. False runs falling with w at
fixed k — holds at k = 0.5 only (183.15 → 112.01 → 67.02 → 36.43); at
every k ≥ 1.0 the rate rises from w = 10 to w = 25, at k = 3.0 on to
w = 50, before it falls (k = 1.0: 63.67 → 66.83 → 39.85 → 17.84;
k = 3.0: 0.03 → 1.09 → 1.80 → 0.89: a longer window averages the
tick-to-tick scatter but integrates the slow wander). Rising as k
falls — holds at every w. Rise latency at w = 100 "tens of ticks
after the crossing" — holds in N-H2 (median 22.8–71.3 at every k) and
at k = 3.0 in N-H3 (21.0); it fails at k ≤ 2.0 in N-H3 (0.0–4.8) and
at every k in N-H4 (0.0), and at k ≤ 1.0 in those two strata an
anticipation run past the first alarmable tick has started before the
crossing in 0.600–0.870 of
observer-episodes, because the statistic integrates the 100-tick
climb (the expectation was reasoned from a step, the data is a ramp). E-H2 not helped — holds within four times the pick's rate
(at most 0.340 against 0.301), not at any price (0.494 pure at
w50-k0.5).

## Decision rules, applied

§5 names none beyond reporting; no stop (reads only); the selection
rule produced one candidate and the confirming read ran as declared on
three cells. The 59 other cells never touched the confirming half.
The pick after this read is hers; nothing here moves 0.05 / B = 2.

## What stands alone

Nothing mints. The null amends F-071 by a dated addendum (this
commit): the rise the needy set saw in the mean logit profile is a
population mean and a noisy per-slice trend; within the level rule's
false-run budget the one pure `rise` cell detects a tenth of the late
crossings and no cell of any family detects more of them than the
pick does (every in-budget mean N gain is negative; the best gain
within twice the pick's rate is +0.059, w100-k3.0|L at 1.7×), while
the pure `rise` cells that do detect them (w = 100, k ≤ 1.0:
0.69–0.90, an alarm run starting inside [mask onset, crossing) past
the first alarmable tick in 0.60–0.87 of N-H3 / N-H4
observer-episodes) pay 17.84 to 36.43 false runs per 10,000
covered-friend observer-ticks, 25 to 51 times the pick's; between
the two, the same windows with a P ≥ 0.01 floor (w100-k0.5+f,
w100-k1.0+f) detect 0.51–0.64 at 1.81–1.99 per 10,000 (2.6–2.8×), a
mean N gain of +0.085 to +0.102 over the pick on the tuning half. The
scope is this one detector family (two adjacent window means) on the
frozen NF-h24+p over the needy set's scripted-friend crossings; a
smoothed level rule, a CUSUM or a retrained head are not read here.

## Guards (`test_rise.py`; reds via `scripts/mutate.sh --expect` on the committed files, 2026-11-01)

| guard | mutation (rise.py) | predicted first failure | observed | verdict |
|---|---|---|---|---|
| r1 accounting = the ladder's | detection latency `+ 1` in the copy | `('E', 'L:t0.05-B2', 'latency', …)` | `('N', 'L:t0.05-B2', 'latency', {'1': 1, '2': 38, '3': 33, '4': 41}, {'1': 0, '2': 37, '3': 32, '4': 40})` — WRONG REASON (exit 7): on the first E tuning world no observer detects at the pick, so the E compare could not see the bug; prediction corrected to arm N and the cycle re-run | RED CONFIRMED on the re-run (prediction `('N', 'L:t0.05-B2', 'latency'`) |
| r2 the step statistic | recent window `cs[t − w + 1]` → `cs[t − w]` (w + 1 ticks) | `s[114] = 1.2` | `AssertionError: s[114] = 1.2000000000000002, s[119] = 0.20000000000000018` | RED CONFIRMED |
| r3a the halves (refuse_unless is live) | `== half` → `!= half` in `worlds` | `PermissionError: T1 seed <n> is a confirming seed; this read is declared on tuning seeds only` | matched | RED CONFIRMED |
| r3b the halves (order) | `out.append(...)` → `out.insert(0, ...)` | `tuning worlds differ from the ladder's` | matched | RED CONFIRMED |
| r4 the selection rule | covered bound `<=` → `<` | `'chosen': 'w25-k0.5'` (the on-bound best drops out) | matched | RED CONFIRMED |

Baseline and post-restore: 1 passed, 0 failed for each cycle; the
suite 4 passed, 0 failed at 48dae5cf. The r1 miss is on record as a
lesson: a rule-5 prediction that names WHICH world fails first needs
the world's own figures (here: whether any observer detects at the
cell), not the stratum's mean.

## Limitations

Declared in §8 and unchanged: a scripted friend; one detector family
and one grid, tuning figures for 59 of the 62 cells; the frozen
probe's logit, so a retrained head is not read; covered-friend
false-run rates measured where covered friends rarely cross. Added
from the read: the statistic is undefined for a slice's first 2w − 1
ticks, so at w = 100 the N-H2 stratum (crossings at 100–300) is read
mostly after its anticipation window has passed, and the 20-episode
N-H4 cell on the confirming half is the smallest primary cell this
read scores (detection SDs 0.13–0.16 at the two scored cells).

## Regeneration

`A = experiments/needy-set-2026-10-28`; `P = experiments/probe-rise-2026-11-01`; env as the needy set's step 3.

### Read

```sh
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $P/rise.py plan                                              # about 1 s
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $P/rise.py read --out $P/reads/rise.json --md > $P/reads/rise.md   # about 1 min (360 worlds, 3 probe seeds)
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $P/test_rise.py                                              # about 5 s
```

Accuracy gate: **PASS** 2026-11-01, four rounds, a fresh subagent
each; the reader reproduced exactly in every round (459 table cells,
fresh md byte-identical to the recorded but for the run-time line,
fresh JSON equal but for `seconds`). Round 1 FAIL: one range over a
family computed from the cells remembered rather than the family
(pure rise E-H1 0.149 for 0.087); "the only rise cell" where five
`rise+f` cells also sat inside the budget, copied into all three
companions; "a tenth" on the F-071 line true of the pure family only;
a re-rounded range in the deviations entry. Round 2 FAIL: "N-H2's
crossings fall mostly before tick 199" where 16 of 35 do (the
anticipation-window ticks do, 5,549 of 6,120); "the alarm on at the
crossing" for an anticipation figure; the F-071 sentence without its
family word and without the `+f` middle ground. Round 3 FAIL:
"before the crossing" without "past the first alarmable tick" on the
F-071 line (inclusive 0.71–0.87 against the printed 0.60–0.87). Round
4 PASS: about 205 prose numbers exact, 6 sourced thresholds, about 26
characterisations (1 WEAK, the tables-as-copies line, reworded
after), 10 undecidable (the mutate strings; four mechanism
parentheticals), 8 provenance checks clean; six `|L` table rows
escaped after. Raw dir `results-raw/set` `v1:973e5cf5a4541ba5`
(unchanged since the needy set's step 5; `scripts/rawdir-hash.sh`).
