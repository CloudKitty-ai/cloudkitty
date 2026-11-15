# Scripted-rescue probe: the reads

Legs read: T@100, T@40, P@40, O@100, base@100, base@40. Missing: P@100.

## R-1 welfare (team happiness, paired by world; worlds run whole in both)

| pair | worlds | positive | negative | paired mean | 95% interval | sign test (up / down) | left out |
|---|---|---|---|---|---|---|---|
| T-base@100 | 29 | 17 | 12 | -0.019 | [-0.138, +0.093] | 0.2291 / 0.8675 | 905009 |
| O-base@100 | 29 | 11 | 18 | -0.172 | [-0.307, -0.049] | 0.9320 / 0.1325 | 905009 |
| T-P@40 | 30 | 7 | 3 | +0.014 | [-0.003, +0.033] | 0.1719 / 0.9453 | none |
| T-base@40 | 30 | 8 | 2 | +0.014 | [+0.004, +0.027] | 0.0547 / 0.9893 | none |
| P-base@40 | 30 | 5 | 5 | +0.000 | [-0.016, +0.016] | 0.6230 / 0.6230 | none |

The PAYS / COSTS level is the sign test of 21 of 30: 0.0214.

## R-2 the tail

| leg | worlds | team happiness (whole worlds) | lost cat-ticks (sight) | lost cat-ticks (Manhattan) | worlds with a 300+ streak | worst streak | aborts (world: tick) |
|---|---|---|---|---|---|---|---|
| T@100 | 30 | 86.835 | 5377 | 5620 | 5 | 557 | none |
| T@40 | 30 | 89.022 | 235 | 249 | 0 | 67 | none |
| P@40 | 30 | 89.008 | 916 | 932 | 0 | 296 | none |
| O@100 | 30 | 86.670 | 7309 | 7529 | 8 | 906 | none |
| base@100 | 30 | 86.863 | 18444 | 18656 | 13 | 1000 | 905009: 16940 |
| base@40 | 30 | 89.007 | 1081 | 1093 | 0 | 294 | none |

Lost cat-ticks over the worlds whole in both members of a pair:

| pair | by sight | by Manhattan |
|---|---|---|
| T-base@100 | T 5140 / base 17226 | T 5370 / base 17428 |
| O-base@100 | O 6609 / base 17226 | O 6817 / base 17428 |
| T-P@40 | T 235 / P 916 | T 249 / P 932 |
| T-base@40 | T 235 / base 1081 | T 249 / base 1093 |
| P-base@40 | P 916 / base 1081 | P 932 / base 1093 |

## R-3 the missions

| leg | missions | per world | length median / mean | ended in a partner act | closed | rule set the act | rule changed the act | rescuer happiness vs baseline | rescuer highest need vs baseline |
|---|---|---|---|---|---|---|---|---|---|
| T@100 | 253 | 8.4 | 22 / 26.8 | 0.937 | partnered 253 | 0.0022 | 0.0018 | -7.170 | +9.311 |
| T@40 | 14 | 0.5 | 22 / 22.9 | 1.000 | partnered 14 | 0.0001 | 0.0001 | -4.382 | +4.442 |
| P@40 | 15 | 0.5 | 32 / 65.5 | 0.000 | partnered 12, rescuer_need 3 | 0.0002 | 0.0002 | -15.407 | +24.898 |
| O@100 | 1052 | 35.1 | 24 / 26.9 | 0.285 | call_gone 298, partnered 751, rescuer_need 3 | 0.0092 | 0.0078 | -7.136 | +7.175 |

## Predictions and grammar

- S3: NOT MET (positive 7, worlds 30, mean +0.014)
- S5: MET (O_minus_base -0.172, T_minus_base -0.019)
