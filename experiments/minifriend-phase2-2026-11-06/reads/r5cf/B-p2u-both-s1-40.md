# R-5 counterfactual — p2u-both-s1 40×40, mode B (30 worlds; ties 0)

tick divergence on live rows 0.168; forced-choice share of live rows 0.399; Spearman head entropy ~ trunk action entropy 0.055, ~ arm action entropy 0.052

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.114 (1075360) | 0.173 (1075359) | 0.182 (1075359) |
| heard | 0.163 (2920887) | 0.177 (2920888) | 0.176 (2920886) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.277 (606787) | 0.271 (606787) | 0.285 (606787) |
| heard | 0.276 (1795467) | 0.285 (1795466) | 0.280 (1795467) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (1405717) | 0.103 (745003) | 0.399 (1075358) |
| heard | 0.000 (3376261) | 0.108 (2465513) | 0.425 (2920887) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 4781978 | 0.000 | 0.481 |
| 2-3 | 0 | — | — |
| 4-6 | 8 | 0.500 | 0.588 |
| 7-12 | 4553328 | 0.289 | 0.552 |
| 13-99 | 2653425 | 0.263 | 0.474 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.036 (2749930) | 0.404 (1246315) |
| mid | — (0) | 0.045 (2623042) | 0.427 (1373204) |
| high | — (0) | 0.047 (2619518) | 0.423 (1376730) |
