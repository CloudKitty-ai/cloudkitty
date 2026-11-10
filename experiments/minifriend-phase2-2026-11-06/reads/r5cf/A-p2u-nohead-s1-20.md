# R-5 counterfactual — p2u-nohead-s1 20×20, mode A (30 worlds; ties 0)

tick divergence on live rows 0.182; forced-choice share of live rows 0.434; Spearman head entropy ~ trunk action entropy 0.055, ~ arm action entropy 0.064

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.142 (1582252) | 0.190 (1582251) | 0.211 (1582251) |
| heard | 0.168 (2413725) | 0.185 (2413722) | 0.194 (2413724) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.342 (846638) | 0.312 (846637) | 0.359 (846637) |
| heard | 0.302 (1414986) | 0.313 (1414985) | 0.317 (1414986) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (2206842) | 0.126 (957662) | 0.466 (1582250) |
| heard | 0.000 (2996214) | 0.120 (1831235) | 0.456 (2413722) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 5203056 | 0.000 | 0.435 |
| 2-3 | 0 | — | — |
| 4-6 | 40 | 0.000 | 0.604 |
| 7-12 | 3642297 | 0.315 | 0.537 |
| 13-99 | 3142532 | 0.328 | 0.418 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.033 (2699656) | 0.443 (1296319) |
| mid | — (0) | 0.044 (2681655) | 0.464 (1314320) |
| high | — (0) | 0.052 (2610639) | 0.471 (1385336) |
