# R-5 counterfactual — p2u-act15-s2 40×40, mode B (30 worlds; ties 0)

tick divergence on live rows 0.170; forced-choice share of live rows 0.385; Spearman head entropy ~ trunk action entropy 0.040, ~ arm action entropy 0.038

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.137 (1177981) | 0.169 (1177980) | 0.199 (1177981) |
| heard | 0.162 (2818551) | 0.175 (2818548) | 0.175 (2818550) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.289 (686822) | 0.270 (686821) | 0.309 (686821) |
| heard | 0.265 (1772308) | 0.275 (1772309) | 0.273 (1772306) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (1473478) | 0.105 (882483) | 0.427 (1177981) |
| heard | 0.000 (3138726) | 0.106 (2498375) | 0.417 (2818548) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 4612204 | 0.000 | 0.481 |
| 2-3 | 0 | — | — |
| 4-6 | 28 | 0.143 | 0.697 |
| 7-12 | 4548576 | 0.281 | 0.553 |
| 13-99 | 2828783 | 0.269 | 0.466 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.037 (2706356) | 0.405 (1290170) |
| mid | — (0) | 0.047 (2641851) | 0.427 (1354682) |
| high | — (0) | 0.051 (2644852) | 0.427 (1351680) |
