# R-5 counterfactual — p2u-act15-s1 20×20, mode B (30 worlds; ties 2)

tick divergence on live rows 0.163; forced-choice share of live rows 0.439; Spearman head entropy ~ trunk action entropy 0.056, ~ arm action entropy 0.064

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.132 (1549526) | 0.181 (1549525) | 0.192 (1549525) |
| heard | 0.151 (2446150) | 0.163 (2446154) | 0.167 (2446144) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.317 (825453) | 0.303 (825452) | 0.328 (825452) |
| heard | 0.276 (1414916) | 0.280 (1414917) | 0.276 (1414915) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (2172219) | 0.100 (926833) | 0.445 (1549524) |
| heard | 0.000 (3093700) | 0.093 (1798599) | 0.413 (2446149) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 5265919 | 0.000 | 0.435 |
| 2-3 | 0 | — | — |
| 4-6 | 88 | 0.182 | 0.554 |
| 7-12 | 3752920 | 0.272 | 0.530 |
| 13-99 | 2968097 | 0.316 | 0.415 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.027 (2704668) | 0.426 (1291007) |
| mid | — (0) | 0.033 (2673997) | 0.428 (1321677) |
| high | — (0) | 0.038 (2612683) | 0.423 (1382992) |
