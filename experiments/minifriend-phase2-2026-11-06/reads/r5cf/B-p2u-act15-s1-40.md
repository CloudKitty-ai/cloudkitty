# R-5 counterfactual — p2u-act15-s1 40×40, mode B (30 worlds; ties 0)

tick divergence on live rows 0.154; forced-choice share of live rows 0.396; Spearman head entropy ~ trunk action entropy 0.048, ~ arm action entropy 0.049

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.115 (1202462) | 0.170 (1202461) | 0.184 (1202461) |
| heard | 0.147 (2793836) | 0.157 (2793834) | 0.156 (2793834) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.264 (690584) | 0.268 (690583) | 0.286 (690584) |
| heard | 0.245 (1722280) | 0.253 (1722277) | 0.248 (1722279) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (1535633) | 0.093 (869291) | 0.402 (1202460) |
| heard | 0.000 (3214668) | 0.087 (2373003) | 0.386 (2793833) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 4750301 | 0.000 | 0.474 |
| 2-3 | 0 | — | — |
| 4-6 | 52 | 0.077 | 0.578 |
| 7-12 | 4304451 | 0.253 | 0.548 |
| 13-99 | 2934084 | 0.259 | 0.467 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.031 (2724684) | 0.386 (1271611) |
| mid | — (0) | 0.038 (2638308) | 0.395 (1357988) |
| high | — (0) | 0.040 (2629600) | 0.390 (1366697) |
