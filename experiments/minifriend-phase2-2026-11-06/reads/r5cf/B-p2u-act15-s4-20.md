# R-5 counterfactual — p2u-act15-s4 20×20, mode B (30 worlds; ties 0)

tick divergence on live rows 0.170; forced-choice share of live rows 0.452; Spearman head entropy ~ trunk action entropy 0.042, ~ arm action entropy 0.052

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.145 (1487884) | 0.188 (1487884) | 0.199 (1487884) |
| heard | 0.155 (2507370) | 0.169 (2507369) | 0.175 (2507370) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.358 (757455) | 0.329 (757454) | 0.359 (757455) |
| heard | 0.286 (1430336) | 0.294 (1430335) | 0.294 (1430335) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (2191288) | 0.104 (784481) | 0.478 (1487883) |
| heard | 0.000 (3231103) | 0.098 (1783637) | 0.429 (2507369) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 5422391 | 0.000 | 0.441 |
| 2-3 | 0 | — | — |
| 4-6 | 4 | 0.000 | 0.609 |
| 7-12 | 3883667 | 0.285 | 0.536 |
| 13-99 | 2679699 | 0.349 | 0.411 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.023 (2670108) | 0.447 (1325146) |
| mid | — (0) | 0.033 (2683143) | 0.445 (1312110) |
| high | — (0) | 0.040 (2637255) | 0.449 (1357999) |
