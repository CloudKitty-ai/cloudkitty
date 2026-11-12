# R-5 counterfactual — p2r-act15 20×20, mode B (30 worlds; ties 0)

tick divergence on live rows 0.177; forced-choice share of live rows 0.448; Spearman head entropy ~ trunk action entropy 0.046, ~ arm action entropy 0.052

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.150 (987169) | 0.192 (987168) | 0.203 (987169) |
| heard | 0.163 (1410101) | 0.175 (1410101) | 0.181 (1410101) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.351 (514396) | 0.337 (514395) | 0.359 (514395) |
| heard | 0.297 (808911) | 0.304 (808910) | 0.305 (808911) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (1418320) | 0.119 (556018) | 0.479 (987168) |
| heard | 0.000 (1803571) | 0.110 (1016632) | 0.440 (1410100) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 3221891 | 0.000 | 0.439 |
| 2-3 | 0 | — | — |
| 4-6 | 64 | 0.125 | 0.583 |
| 7-12 | 2179070 | 0.300 | 0.534 |
| 13-99 | 1790784 | 0.345 | 0.414 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.029 (1607983) | 0.456 (789287) |
| mid | — (0) | 0.038 (1608689) | 0.456 (788577) |
| high | — (0) | 0.044 (1577865) | 0.457 (819408) |
