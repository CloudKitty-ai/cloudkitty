# R-5 counterfactual — p2u-nohead-s1 40×40, mode A (30 worlds; ties 0)

tick divergence on live rows 0.175; forced-choice share of live rows 0.395; Spearman head entropy ~ trunk action entropy 0.053, ~ arm action entropy 0.057

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.126 (1247878) | 0.178 (1247877) | 0.202 (1247877) |
| heard | 0.167 (2748566) | 0.180 (2748569) | 0.185 (2748563) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.296 (708117) | 0.277 (708117) | 0.319 (708117) |
| heard | 0.278 (1708502) | 0.288 (1708505) | 0.290 (1708499) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (1619281) | 0.110 (876475) | 0.429 (1247876) |
| heard | 0.000 (3120192) | 0.111 (2376942) | 0.436 (2748564) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 4739473 | 0.000 | 0.465 |
| 2-3 | 0 | — | — |
| 4-6 | 0 | — | — |
| 7-12 | 4216042 | 0.295 | 0.549 |
| 13-99 | 3033815 | 0.281 | 0.458 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.036 (2727690) | 0.417 (1268753) |
| mid | — (0) | 0.047 (2641560) | 0.440 (1354882) |
| high | — (0) | 0.053 (2623634) | 0.445 (1372811) |
