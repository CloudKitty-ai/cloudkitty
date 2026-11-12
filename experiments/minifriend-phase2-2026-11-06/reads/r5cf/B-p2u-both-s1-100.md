# R-5 counterfactual — p2u-both-s1 100×100, mode B (30 worlds; ties 1)

tick divergence on live rows 0.192; forced-choice share of live rows 0.359; Spearman head entropy ~ trunk action entropy 0.058, ~ arm action entropy 0.050

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.112 (835324) | 0.175 (835323) | 0.189 (835323) |
| heard | 0.194 (3023993) | 0.207 (3023997) | 0.202 (3023989) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.264 (491294) | 0.266 (491294) | 0.277 (491294) |
| heard | 0.300 (1982527) | 0.313 (1982525) | 0.306 (1982526) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (1032088) | 0.106 (638559) | 0.394 (835323) |
| heard | 0.000 (3124401) | 0.129 (2923587) | 0.478 (3023991) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 4156489 | 0.000 | 0.521 |
| 2-3 | 0 | — | — |
| 4-6 | 60 | 0.200 | 0.556 |
| 7-12 | 4929750 | 0.327 | 0.587 |
| 13-99 | 2491650 | 0.244 | 0.520 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.051 (2684400) | 0.439 (1174916) |
| mid | — (0) | 0.061 (2506185) | 0.471 (1353131) |
| high | — (0) | 0.061 (2528045) | 0.469 (1331272) |
