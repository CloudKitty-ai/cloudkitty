# R-5 counterfactual — p2r-nohead 40×40, mode A (30 worlds; ties 0)

tick divergence on live rows 0.201; forced-choice share of live rows 0.408; Spearman head entropy ~ trunk action entropy 0.040, ~ arm action entropy 0.042

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.159 (778317) | 0.209 (778316) | 0.232 (778317) |
| heard | 0.194 (1619530) | 0.205 (1619529) | 0.207 (1619529) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.355 (430930) | 0.350 (430929) | 0.380 (430929) |
| heard | 0.324 (987860) | 0.334 (987859) | 0.335 (987860) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (1042162) | 0.151 (514474) | 0.501 (778314) |
| heard | 0.000 (1895009) | 0.151 (1344051) | 0.480 (1619528) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 2937171 | 0.000 | 0.479 |
| 2-3 | 0 | — | — |
| 4-6 | 4 | 0.000 | 0.694 |
| 7-12 | 2560225 | 0.338 | 0.556 |
| 13-99 | 1696138 | 0.344 | 0.463 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.048 (1622976) | 0.478 (774869) |
| mid | — (0) | 0.061 (1584894) | 0.491 (812953) |
| high | — (0) | 0.067 (1587822) | 0.491 (810024) |
