# R-5 counterfactual — p2u-act15-s2 20×20, mode B (30 worlds; ties 0)

tick divergence on live rows 0.171; forced-choice share of live rows 0.429; Spearman head entropy ~ trunk action entropy 0.046, ~ arm action entropy 0.051

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.148 (1554512) | 0.180 (1554511) | 0.203 (1554511) |
| heard | 0.154 (2441366) | 0.171 (2441363) | 0.177 (2441364) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.336 (843875) | 0.298 (843875) | 0.344 (843875) |
| heard | 0.276 (1439414) | 0.287 (1439411) | 0.289 (1439412) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (2131909) | 0.115 (977114) | 0.459 (1554511) |
| heard | 0.000 (3005856) | 0.105 (1876873) | 0.422 (2441364) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 5137765 | 0.000 | 0.441 |
| 2-3 | 0 | — | — |
| 4-6 | 72 | 0.000 | 0.582 |
| 7-12 | 3863943 | 0.289 | 0.536 |
| 13-99 | 2985847 | 0.314 | 0.414 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.031 (2680109) | 0.429 (1315767) |
| mid | — (0) | 0.040 (2684263) | 0.436 (1311611) |
| high | — (0) | 0.046 (2627377) | 0.443 (1368500) |
