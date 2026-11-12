# R-5 counterfactual — p2u-nohead-s4 20×20, mode A (30 worlds; ties 0)

tick divergence on live rows 0.181; forced-choice share of live rows 0.450; Spearman head entropy ~ trunk action entropy 0.042, ~ arm action entropy 0.053

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.152 (1505522) | 0.197 (1505521) | 0.210 (1505521) |
| heard | 0.166 (2489917) | 0.180 (2489914) | 0.189 (2489914) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.374 (781119) | 0.334 (781118) | 0.371 (781118) |
| heard | 0.308 (1415308) | 0.314 (1415308) | 0.319 (1415308) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (2173209) | 0.124 (837837) | 0.491 (1505518) |
| heard | 0.000 (3223821) | 0.119 (1756011) | 0.451 (2489913) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 5397030 | 0.000 | 0.441 |
| 2-3 | 0 | — | — |
| 4-6 | 56 | 0.214 | 0.571 |
| 7-12 | 3803779 | 0.310 | 0.532 |
| 13-99 | 2785444 | 0.357 | 0.415 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.030 (2662186) | 0.460 (1333250) |
| mid | — (0) | 0.040 (2687658) | 0.466 (1307778) |
| high | — (0) | 0.048 (2641028) | 0.472 (1354409) |
