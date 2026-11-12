# R-5 counterfactual — p2u-both-s1 20×20, mode B (30 worlds; ties 1)

tick divergence on live rows 0.162; forced-choice share of live rows 0.441; Spearman head entropy ~ trunk action entropy 0.057, ~ arm action entropy 0.061

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.128 (1423136) | 0.179 (1423136) | 0.183 (1423136) |
| heard | 0.149 (2572350) | 0.166 (2572341) | 0.170 (2572346) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.318 (752734) | 0.295 (752733) | 0.313 (752734) |
| heard | 0.276 (1480052) | 0.285 (1480051) | 0.282 (1480052) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (2011207) | 0.104 (835065) | 0.429 (1423136) |
| heard | 0.000 (3276882) | 0.099 (1867811) | 0.413 (2572344) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 5288089 | 0.000 | 0.445 |
| 2-3 | 0 | — | — |
| 4-6 | 12 | 0.000 | 0.601 |
| 7-12 | 3898102 | 0.277 | 0.534 |
| 13-99 | 2800242 | 0.309 | 0.426 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.028 (2718518) | 0.415 (1276963) |
| mid | — (0) | 0.035 (2667307) | 0.422 (1328173) |
| high | — (0) | 0.039 (2605136) | 0.418 (1390348) |
