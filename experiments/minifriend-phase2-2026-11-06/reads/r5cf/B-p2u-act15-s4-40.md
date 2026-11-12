# R-5 counterfactual — p2u-act15-s4 40×40, mode B (30 worlds; ties 0)

tick divergence on live rows 0.168; forced-choice share of live rows 0.408; Spearman head entropy ~ trunk action entropy 0.036, ~ arm action entropy 0.038

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.134 (1139566) | 0.178 (1139565) | 0.188 (1139565) |
| heard | 0.161 (2856670) | 0.172 (2856667) | 0.172 (2856668) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.311 (626409) | 0.291 (626408) | 0.309 (626409) |
| heard | 0.270 (1739927) | 0.280 (1739927) | 0.278 (1739926) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (1539470) | 0.104 (739661) | 0.434 (1139565) |
| heard | 0.000 (3350225) | 0.106 (2363113) | 0.417 (2856667) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 4889695 | 0.000 | 0.482 |
| 2-3 | 0 | — | — |
| 4-6 | 0 | — | — |
| 7-12 | 4486149 | 0.278 | 0.555 |
| 13-99 | 2612857 | 0.294 | 0.464 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.033 (2684318) | 0.412 (1311916) |
| mid | — (0) | 0.043 (2651796) | 0.427 (1344437) |
| high | — (0) | 0.047 (2656350) | 0.425 (1339884) |
