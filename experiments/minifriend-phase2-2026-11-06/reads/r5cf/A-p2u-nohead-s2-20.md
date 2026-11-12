# R-5 counterfactual — p2u-nohead-s2 20×20, mode A (30 worlds; ties 0)

tick divergence on live rows 0.194; forced-choice share of live rows 0.438; Spearman head entropy ~ trunk action entropy 0.055, ~ arm action entropy 0.055

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.173 (1467135) | 0.207 (1467134) | 0.244 (1467135) |
| heard | 0.175 (2528533) | 0.188 (2528534) | 0.195 (2528530) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.394 (774979) | 0.365 (774978) | 0.421 (774978) |
| heard | 0.318 (1471087) | 0.321 (1471087) | 0.322 (1471087) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (2076469) | 0.132 (857801) | 0.546 (1467134) |
| heard | 0.000 (3172336) | 0.121 (1884729) | 0.469 (2528532) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 5248805 | 0.000 | 0.452 |
| 2-3 | 0 | — | — |
| 4-6 | 64 | 0.062 | 0.586 |
| 7-12 | 4086336 | 0.312 | 0.540 |
| 13-99 | 2651796 | 0.397 | 0.419 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.035 (2719633) | 0.507 (1276034) |
| mid | — (0) | 0.043 (2662850) | 0.495 (1332817) |
| high | — (0) | 0.049 (2608851) | 0.491 (1386816) |
