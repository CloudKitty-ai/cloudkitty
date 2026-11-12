# R-5 counterfactual — p2u-nohead-s2 40×40, mode A (30 worlds; ties 1)

tick divergence on live rows 0.201; forced-choice share of live rows 0.394; Spearman head entropy ~ trunk action entropy 0.045, ~ arm action entropy 0.041

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.165 (1120074) | 0.203 (1120074) | 0.248 (1120074) |
| heard | 0.189 (2876273) | 0.203 (2876268) | 0.204 (2876270) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.354 (634029) | 0.343 (634028) | 0.392 (634028) |
| heard | 0.312 (1787458) | 0.324 (1787454) | 0.323 (1787455) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (1458137) | 0.132 (782014) | 0.524 (1120071) |
| heard | 0.000 (3266444) | 0.134 (2486099) | 0.481 (2876268) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 4724581 | 0.000 | 0.489 |
| 2-3 | 0 | — | — |
| 4-6 | 0 | — | — |
| 7-12 | 4791499 | 0.319 | 0.558 |
| 13-99 | 2472953 | 0.354 | 0.467 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.046 (2729658) | 0.488 (1266686) |
| mid | — (0) | 0.057 (2621918) | 0.497 (1374425) |
| high | — (0) | 0.061 (2641109) | 0.493 (1355237) |
