# R-5 counterfactual — p2r-act15 40×40, mode B (30 worlds; ties 0)

tick divergence on live rows 0.181; forced-choice share of live rows 0.403; Spearman head entropy ~ trunk action entropy 0.039, ~ arm action entropy 0.039

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.141 (775613) | 0.189 (775612) | 0.205 (775612) |
| heard | 0.174 (1622167) | 0.186 (1622164) | 0.185 (1622165) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.309 (435597) | 0.312 (435596) | 0.331 (435596) |
| heard | 0.289 (996511) | 0.300 (996508) | 0.298 (996508) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (1020048) | 0.124 (531177) | 0.451 (775612) |
| heard | 0.000 (1876969) | 0.124 (1367362) | 0.440 (1622165) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 2897017 | 0.000 | 0.481 |
| 2-3 | 0 | — | — |
| 4-6 | 0 | — | — |
| 7-12 | 2550212 | 0.302 | 0.558 |
| 13-99 | 1746104 | 0.303 | 0.464 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.040 (1619636) | 0.433 (778142) |
| mid | — (0) | 0.051 (1586908) | 0.450 (810869) |
| high | — (0) | 0.056 (1589010) | 0.447 (808768) |
