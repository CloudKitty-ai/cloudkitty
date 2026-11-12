# R-5 counterfactual — p2u-nohead-s1 100×100, mode A (30 worlds; ties 0)

tick divergence on live rows 0.191; forced-choice share of live rows 0.352; Spearman head entropy ~ trunk action entropy 0.054, ~ arm action entropy 0.057

## divergence by head-entropy tercile, all live rows (read_r5's binning)

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.124 (1042378) | 0.177 (1042377) | 0.208 (1042377) |
| heard | 0.192 (2934999) | 0.203 (2934998) | 0.201 (2934998) |

## the same on FREE-CHOICE ticks only

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.275 (620056) | 0.272 (620055) | 0.309 (620056) |
| heard | 0.291 (1955913) | 0.303 (1955912) | 0.301 (1955912) |

## divergence by the TRUNK's action-entropy tercile

| regime | low | mid | high |
|---|---|---|---|
| seen | 0.000 (1266965) | 0.109 (817790) | 0.423 (1042377) |
| heard | 0.000 (2937258) | 0.128 (2932739) | 0.468 (2934998) |

## divergence by legal-menu size (live rows)

| legal actions | n | divergence | mean head entropy |
|---|---|---|---|
| 1-1 | 4204223 | 0.000 | 0.500 |
| 2-3 | 0 | — | — |
| 4-6 | 40 | 0.000 | 0.636 |
| 7-12 | 4732165 | 0.315 | 0.579 |
| 13-99 | 2995699 | 0.265 | 0.499 |

## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows

| head \ trunk | low | mid | high |
|---|---|---|---|
| low | — (0) | 0.048 (2748446) | 0.438 (1228929) |
| mid | — (0) | 0.062 (2592577) | 0.466 (1384797) |
| high | — (0) | 0.065 (2613726) | 0.465 (1363652) |
