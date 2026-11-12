# R-5 counterfactual — p2r-nohead 20×20, mode A (30 worlds; ties 0)

tick divergence on live rows 0.198; forced-choice share of live rows 0.450; Spearman head entropy ~ trunk action entropy 0.044, ~ arm action entropy 0.051

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.165 (976254) | 0.212 (976254) | 0.229 (976254) |
| heard | 0.184 (1420892) | 0.196 (1420889) | 0.205 (1420891) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.389 (506319) | 0.372 (506318) | 0.407 (506318) |
| heard | 0.336 (812069) | 0.341 (812070) | 0.345 (812068) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (1409807) | 0.147 (542701) | 0.524 (976254) |
| heard | 0.000 (1826465) | 0.139 (1015316) | 0.485 (1420891) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 3236272 | 0.000 | 0.441 |
| 2-3 | 0 | — | — |
| 4-6 | 12 | 0.333 | 0.553 |
| 7-12 | 2192067 | 0.340 | 0.535 |
| 13-99 | 1763083 | 0.384 | 0.417 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.037 (1609112) | 0.497 (788033) |
| mid | — (0) | 0.047 (1608940) | 0.499 (788201) |
| high | — (0) | 0.055 (1576236) | 0.505 (820912) |
