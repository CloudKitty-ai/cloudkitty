# R-5 counterfactual — p2u-nohead-s4 40×40, mode A (30 worlds; ties 1)

tick divergence on live rows 0.175; forced-choice share of live rows 0.416; Spearman head entropy ~ trunk action entropy 0.036, ~ arm action entropy 0.039

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.141 (1180390) | 0.188 (1180389) | 0.202 (1180389) |
| heard | 0.166 (2816117) | 0.178 (2816116) | 0.180 (2816116) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.338 (645738) | 0.300 (645737) | 0.332 (645737) |
| heard | 0.285 (1687935) | 0.295 (1687934) | 0.295 (1687934) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (1603956) | 0.125 (756823) | 0.451 (1180389) |
| heard | 0.000 (3384546) | 0.120 (2247688) | 0.428 (2816115) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 4988502 | 0.000 | 0.475 |
| 2-3 | 0 | — | — |
| 4-6 | 0 | — | — |
| 7-12 | 4303229 | 0.297 | 0.548 |
| 13-99 | 2697786 | 0.306 | 0.465 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.037 (2685417) | 0.425 (1311088) |
| mid | — (0) | 0.048 (2648210) | 0.440 (1348293) |
| high | — (0) | 0.052 (2659381) | 0.439 (1337128) |
