## Phase 1c read (derived columns)

### Width 8 (the small candidate), group P (P1, P2, P3, P4, P5 eval worlds): n_samples 4000000
coverage GRAVE mind-visible: Miso 572, Biscuit 364, Pumpkin 398, Kittybear 933, Clementine 260

#### R1c visible: pooled mse5 on the five hidden needs (mean ± SD over seeds) and pooled bias
| head | GRAVE mse5 | DA mse5 | COMMON mse5 | GRAVE bias | DA bias | COMMON bias |
|---|---|---|---|---|---|---|
| SD | 1582.84 ± 187.15 | 1308.78 ± 138.98 | 24.69 ± 0.10 | -21.80 ± 3.51 | -18.94 ± 2.75 | 0.43 ± 0.13 |
| NF | 908.10 ± 33.43 | 773.25 ± 20.58 | 25.34 ± 0.52 | -10.10 ± 1.08 | -8.96 ± 1.27 | 0.05 ± 0.14 |
| DR | 827.69 ± 117.06 | 725.06 ± 97.39 | 40.15 ± 6.85 | -7.57 ± 0.93 | -7.13 ± 0.83 | 0.19 ± 0.25 |
| SD_nores | 2256.95 ± 231.44 | 1880.37 ± 183.74 | 84.92 ± 11.84 | -31.30 ± 3.26 | -28.31 ± 2.82 | -1.91 ± 0.09 |
baselines mse5 (marginal / proxy): GRAVE 3264.16 / 3261.15; DA 2751.25 / 2749.84; COMMON 75.10 / 72.67

#### R1c visible per friend: mse5 GRAVE / COMMON per head
| friend | SD GRAVE | NF GRAVE | DR GRAVE | SD COMMON | NF COMMON | DR COMMON |
|---|---|---|---|---|---|---|
| Miso | 1086.36 ± 166.68 | 613.31 ± 78.46 | 480.05 ± 84.11 | 23.81 ± 0.14 | 24.94 ± 0.65 | 38.41 ± 5.91 |
| Biscuit | 1891.99 ± 62.30 | 1245.18 ± 19.55 | 1011.13 ± 66.77 | 21.64 ± 0.06 | 24.05 ± 0.81 | 37.71 ± 6.14 |
| Pumpkin | 1299.34 ± 225.14 | 714.87 ± 22.05 | 697.68 ± 93.75 | 26.40 ± 0.14 | 26.77 ± 0.71 | 41.41 ± 7.00 |
| Kittybear | 1980.50 ± 385.07 | 1081.52 ± 111.77 | 1021.69 ± 218.83 | 22.77 ± 0.23 | 21.86 ± 0.44 | 36.78 ± 7.08 |
| Clementine | 1249.33 ± 162.30 | 758.16 ± 72.85 | 838.55 ± 49.32 | 28.68 ± 0.37 | 28.93 ± 0.20 | 46.18 ± 8.13 |
| pooled | 1582.84 ± 187.15 | 908.10 ± 33.43 | 827.69 ± 117.06 | 24.69 ± 0.10 | 25.34 ± 0.52 | 40.15 ± 6.85 |

#### R2c visible: SD loss over the comparator's, per class (READ when |r − 1| > SD)
| comparator | GRAVE | DA | COMMON |
|---|---|---|---|
| SD / NF | 1.743 ± 0.216 READ | 1.693 ± 0.185 READ | 0.974 ± 0.020 READ |
| SD / DR | 1.912 ± 0.353 READ | 1.805 ± 0.309 READ | 0.615 ± 0.105 READ |

#### R3c visible: bias grave / common / gap (need points), SIG = signature, per head
| friend | SD | NF | DR |
|---|---|---|---|
| Miso | -20.43 / +0.37 / -20.80 SIG | -5.77 / -0.21 / -5.57 SIG | -3.59 / -0.21 / -3.38 SIG |
| Biscuit | -22.61 / +0.38 / -22.99 SIG | -11.59 / +0.47 / -12.06 SIG | -8.22 / +0.55 / -8.77 SIG |
| Pumpkin | -19.04 / +0.49 / -19.54 SIG | -6.83 / -0.10 / -6.73 SIG | -4.12 / -0.07 / -4.05 SIG |
| Kittybear | -25.98 / +0.63 / -26.61 SIG | -17.01 / +0.65 / -17.66 SIG | -14.15 / +1.31 / -15.45 SIG |
| Clementine | -12.89 / +0.29 / -13.19 SIG | +2.27 / -0.56 / +2.83 | +2.89 / -0.57 / +3.46 |
| pooled | -21.80 / +0.43 / -22.23 SIG | -10.10 / +0.05 / -10.15 SIG | -7.57 / +0.19 / -7.77 SIG |

#### R6c(a) visible: residual share — SD with the residual zeroed over the full head, per class: GRAVE 1.426 ± 0.223 READ, DA 1.437 ± 0.207 READ, COMMON 3.440 ± 0.480 READ → structure carries the fit (GRAVE ≤ 2.0×): True

#### R1c all: pooled mse5 on the five hidden needs (mean ± SD over seeds) and pooled bias
| head | GRAVE mse5 | DA mse5 | COMMON mse5 | GRAVE bias | DA bias | COMMON bias |
|---|---|---|---|---|---|---|
| SD | 1531.05 ± 119.76 | 1341.98 ± 103.70 | 36.65 ± 0.53 | -21.63 ± 2.28 | -19.44 ± 2.00 | 0.56 ± 0.10 |
| NF | 894.45 ± 21.77 | 795.12 ± 19.89 | 33.68 ± 0.54 | -8.67 ± 0.32 | -7.84 ± 0.41 | 0.05 ± 0.13 |
| DR | 729.70 ± 65.46 | 680.36 ± 59.05 | 54.48 ± 8.30 | -5.90 ± 0.21 | -5.73 ± 0.23 | 0.34 ± 0.46 |
| SD_nores | 2144.04 ± 268.58 | 1888.72 ± 224.71 | 103.48 ± 9.79 | -29.04 ± 4.09 | -27.21 ± 3.68 | -2.08 ± 0.22 |
baselines mse5 (marginal / proxy): GRAVE 3422.93 / 3402.49; DA 2995.87 / 2978.35; COMMON 78.84 / 77.59

#### R1c all per friend: mse5 GRAVE / COMMON per head
| friend | SD GRAVE | NF GRAVE | DR GRAVE | SD COMMON | NF COMMON | DR COMMON |
|---|---|---|---|---|---|---|
| Miso | 1311.93 ± 179.56 | 716.65 ± 68.61 | 493.32 ± 46.92 | 35.90 ± 0.60 | 33.29 ± 0.71 | 52.70 ± 7.17 |
| Biscuit | 1653.62 ± 23.97 | 938.45 ± 51.76 | 766.85 ± 26.66 | 33.42 ± 0.46 | 32.33 ± 0.75 | 52.23 ± 7.54 |
| Pumpkin | 1316.69 ± 113.77 | 767.35 ± 4.97 | 633.30 ± 54.46 | 38.79 ± 0.50 | 35.06 ± 0.64 | 55.61 ± 8.56 |
| Kittybear | 1998.07 ± 281.09 | 1149.32 ± 41.75 | 926.47 ± 180.10 | 33.53 ± 0.47 | 29.55 ± 0.42 | 51.00 ± 9.47 |
| Clementine | 1158.40 ± 108.86 | 794.36 ± 26.17 | 770.40 ± 38.57 | 41.61 ± 0.71 | 38.18 ± 0.22 | 60.83 ± 8.82 |
| pooled | 1531.05 ± 119.76 | 894.45 ± 21.77 | 729.70 ± 65.46 | 36.65 ± 0.53 | 33.68 ± 0.54 | 54.48 ± 8.30 |

#### R2c all: SD loss over the comparator's, per class (READ when |r − 1| > SD)
| comparator | GRAVE | DA | COMMON |
|---|---|---|---|
| SD / NF | 1.712 ± 0.140 READ | 1.688 ± 0.137 READ | 1.088 ± 0.024 READ |
| SD / DR | 2.098 ± 0.250 READ | 1.972 ± 0.229 READ | 0.673 ± 0.103 READ |

#### R3c all: bias grave / common / gap (need points), SIG = signature, per head
| friend | SD | NF | DR |
|---|---|---|---|
| Miso | -20.99 / +0.59 / -21.58 SIG | -7.72 / -0.09 / -7.62 SIG | -4.90 / +0.07 / -4.97 SIG |
| Biscuit | -23.40 / +0.53 / -23.93 SIG | -7.83 / +0.43 / -8.25 SIG | -4.98 / +0.63 / -5.62 SIG |
| Pumpkin | -20.40 / +0.59 / -20.99 SIG | -5.47 / -0.16 / -5.31 SIG | -4.22 / +0.01 / -4.23 SIG |
| Kittybear | -27.49 / +0.74 / -28.22 SIG | -17.02 / +0.72 / -17.75 SIG | -13.12 / +1.49 / -14.60 SIG |
| Clementine | -12.60 / +0.37 / -12.97 SIG | -0.35 / -0.62 / +0.27 | +2.04 / -0.47 / +2.51 |
| pooled | -21.63 / +0.56 / -22.20 SIG | -8.67 / +0.05 / -8.72 SIG | -5.90 / +0.34 / -6.25 SIG |

#### R6c(a) all: residual share — SD with the residual zeroed over the full head, per class: GRAVE 1.400 ± 0.207 READ, DA 1.407 ± 0.200 READ, COMMON 2.824 ± 0.270 READ → structure carries the fit (GRAVE ≤ 2.0×): True

#### R4c visible: grave probability 1 − ∏(1 − m): Brier 0.0009 ± 0.0001; mean p on GRAVE 0.294 ± 0.075, on COMMON 0.001 ± 0.000; GRAVE samples 2527, of which happiness-only 168
| p bin | n | mean p | realised grave fraction |
|---|---|---|---|
| [0.0, 0.1) | 1922847 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| [0.1, 0.2) | 1180 | 0.144 ± 0.001 | 0.285 ± 0.077 |
| [0.2, 0.3) | 697 | 0.247 ± 0.001 | 0.435 ± 0.060 |
| [0.3, 0.4) | 659 | 0.348 ± 0.001 | 0.533 ± 0.074 |
| [0.4, 0.5) | 514 | 0.447 ± 0.004 | 0.543 ± 0.089 |
| [0.5, 0.6) | 381 | 0.547 ± 0.005 | 0.662 ± 0.108 |
| [0.6, 0.7) | 314 | 0.647 ± 0.003 | 0.752 ± 0.095 |
| [0.7, 0.8) | 227 | 0.744 ± 0.001 | 0.776 ± 0.165 |
| [0.8, 0.9) | 181 | 0.851 ± 0.012 | 0.741 ± 0.301 |
| [0.9, 1.0) | 130 | 0.936 ± 0.005 | 0.538 ± 0.032 |

#### R4c all: grave probability 1 − ∏(1 − m): Brier 0.0016 ± 0.0001; mean p on GRAVE 0.366 ± 0.051, on COMMON 0.001 ± 0.000; GRAVE samples 11504, of which happiness-only 1280
| p bin | n | mean p | realised grave fraction |
|---|---|---|---|
| [0.0, 0.1) | 3971812 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| [0.1, 0.2) | 9130 | 0.146 ± 0.002 | 0.114 ± 0.091 |
| [0.2, 0.3) | 6721 | 0.249 ± 0.002 | 0.320 ± 0.101 |
| [0.3, 0.4) | 4178 | 0.347 ± 0.002 | 0.557 ± 0.046 |
| [0.4, 0.5) | 3028 | 0.447 ± 0.004 | 0.705 ± 0.008 |
| [0.5, 0.6) | 2123 | 0.541 ± 0.004 | 0.763 ± 0.060 |
| [0.6, 0.7) | 1441 | 0.643 ± 0.004 | 0.693 ± 0.043 |
| [0.7, 0.8) | 761 | 0.744 ± 0.003 | 0.564 ± 0.106 |
| [0.8, 0.9) | 599 | 0.854 ± 0.009 | 0.616 ± 0.050 |
| [0.9, 1.0) | 207 | 0.928 ± 0.005 | 0.537 ± 0.079 |

#### R6c(b): p_rel AUROC against the true relief indicator — in sight 0.960 ± 0.005, under fog 0.755 ± 0.018, all 0.883 ± 0.010

#### R7c SD against the DR floor: floor 827.69, candidate pooled 1582.84, ratio 1.912, pooled_ok False, friends_ok False → clears False
| friend | candidate grave | floor grave | excess over 1.10 × floor | candidate SD | clause |
|---|---|---|---|---|---|
| Miso | 1086.36 | 480.05 | +558.30 | 166.68 | EXCEEDS |
| Biscuit | 1891.99 | 1011.13 | +779.75 | 62.30 | EXCEEDS |
| Pumpkin | 1299.34 | 697.68 | +531.89 | 225.14 | EXCEEDS |
| Kittybear | 1980.50 | 1021.69 | +856.63 | 385.07 | EXCEEDS |
| Clementine | 1249.33 | 838.55 | +326.92 | 162.30 | EXCEEDS |

#### R7c SD against NF: floor 908.10, candidate pooled 1582.84, ratio 1.743, pooled_ok False, friends_ok False → clears False
| friend | candidate grave | floor grave | excess over 1.10 × floor | candidate SD | clause |
|---|---|---|---|---|---|
| Miso | 1086.36 | 613.31 | +411.71 | 166.68 | EXCEEDS |
| Biscuit | 1891.99 | 1245.18 | +522.29 | 62.30 | EXCEEDS |
| Pumpkin | 1299.34 | 714.87 | +512.98 | 225.14 | EXCEEDS |
| Kittybear | 1980.50 | 1081.52 | +790.83 | 385.07 | EXCEEDS |
| Clementine | 1249.33 | 758.16 | +415.35 | 162.30 | EXCEEDS |

#### R7c NF against the DR floor (1b's R3b at width 24): floor 827.69, candidate pooled 908.10, ratio 1.097, pooled_ok True, friends_ok False → clears False
| friend | candidate grave | floor grave | excess over 1.10 × floor | candidate SD | clause |
|---|---|---|---|---|---|
| Miso | 613.31 | 480.05 | +85.26 | 78.46 | EXCEEDS |
| Biscuit | 1245.18 | 1011.13 | +132.94 | 19.55 | EXCEEDS |
| Pumpkin | 714.87 | 697.68 | -52.57 | 22.05 | ok |
| Kittybear | 1081.52 | 1021.69 | -42.35 | 111.77 | ok |
| Clementine | 758.16 | 838.55 | -164.25 | 72.85 | ok |

### Width 8 (the small candidate), group G (G eval worlds): n_samples 640000
coverage GRAVE mind-visible: Miso 506, Biscuit 734, Pumpkin 166, Kittybear 638, Clementine 284

#### R1c visible: pooled mse5 on the five hidden needs (mean ± SD over seeds) and pooled bias
| head | GRAVE mse5 | DA mse5 | COMMON mse5 | GRAVE bias | DA bias | COMMON bias |
|---|---|---|---|---|---|---|
| SD | 1223.76 ± 275.26 | 1070.35 ± 203.55 | 26.59 ± 0.34 | -16.85 ± 4.73 | -15.27 ± 3.54 | 0.40 ± 0.11 |
| NF | 591.58 ± 20.73 | 559.51 ± 7.14 | 26.79 ± 0.60 | -4.94 ± 0.81 | -5.50 ± 0.78 | 0.04 ± 0.13 |
| DR | 580.94 ± 17.77 | 541.68 ± 32.62 | 42.40 ± 5.87 | -0.66 ± 1.24 | -0.85 ± 0.85 | 0.21 ± 0.27 |
| SD_nores | 1894.73 ± 140.40 | 1642.98 ± 129.33 | 80.38 ± 11.48 | -28.27 ± 3.02 | -25.88 ± 3.14 | -2.21 ± 0.10 |
baselines mse5 (marginal / proxy): GRAVE 2857.36 / 2851.80; DA 2614.03 / 2607.11; COMMON 78.12 / 75.73

#### R1c visible per friend: mse5 GRAVE / COMMON per head
| friend | SD GRAVE | NF GRAVE | DR GRAVE | SD COMMON | NF COMMON | DR COMMON |
|---|---|---|---|---|---|---|
| Miso | 1162.18 ± 155.80 | 564.50 ± 59.96 | 453.75 ± 68.97 | 26.53 ± 0.75 | 27.62 ± 0.74 | 41.16 ± 4.87 |
| Biscuit | 1143.05 ± 458.76 | 502.03 ± 46.90 | 604.64 ± 96.60 | 25.31 ± 0.40 | 26.79 ± 1.12 | 41.97 ± 5.16 |
| Pumpkin | — | — | — | 26.74 ± 0.91 | 27.37 ± 0.96 | 42.40 ± 5.50 |
| Kittybear | 1386.49 ± 262.81 | 730.08 ± 69.60 | 611.51 ± 104.98 | 24.08 ± 0.72 | 22.43 ± 0.49 | 38.46 ± 6.48 |
| Clementine | 1176.49 ± 197.10 | 560.15 ± 56.15 | 677.58 ± 52.90 | 30.13 ± 0.63 | 29.59 ± 0.21 | 47.76 ± 7.31 |
| pooled | 1223.76 ± 275.26 | 591.58 ± 20.73 | 580.94 ± 17.77 | 26.59 ± 0.34 | 26.79 ± 0.60 | 42.40 ± 5.87 |

#### R2c visible: SD loss over the comparator's, per class (READ when |r − 1| > SD)
| comparator | GRAVE | DA | COMMON |
|---|---|---|---|
| SD / NF | 2.069 ± 0.471 READ | 1.913 ± 0.365 READ | 0.993 ± 0.026 |
| SD / DR | 2.107 ± 0.478 READ | 1.976 ± 0.394 READ | 0.627 ± 0.087 READ |

#### R3c visible: bias grave / common / gap (need points), SIG = signature, per head
| friend | SD | NF | DR |
|---|---|---|---|
| Miso | -17.33 / +0.22 / -17.55 SIG | -6.47 / -0.26 / -6.21 SIG | -2.33 / -0.29 / -2.04 SIG |
| Biscuit | -12.88 / +0.37 / -13.25 SIG | -1.86 / +0.52 / -2.38 SIG | +4.00 / +0.66 / +3.34 |
| Pumpkin | insufficient | insufficient | insufficient |
| Kittybear | -19.60 / +0.60 / -20.20 SIG | -8.81 / +0.65 / -9.46 SIG | -5.39 / +1.36 / -6.74 SIG |
| Clementine | -20.08 / +0.36 / -20.44 SIG | -1.51 / -0.55 / -0.95 SIG | +0.94 / -0.54 / +1.48 |
| pooled | -16.85 / +0.40 / -17.25 SIG | -4.94 / +0.04 / -4.98 SIG | -0.66 / +0.21 / -0.87 SIG |

#### R6c(a) visible: residual share — SD with the residual zeroed over the full head, per class: GRAVE 1.548 ± 0.367 READ, DA 1.535 ± 0.316 READ, COMMON 3.022 ± 0.433 READ → structure carries the fit (GRAVE ≤ 2.0×): True

#### R1c all: pooled mse5 on the five hidden needs (mean ± SD over seeds) and pooled bias
| head | GRAVE mse5 | DA mse5 | COMMON mse5 | GRAVE bias | DA bias | COMMON bias |
|---|---|---|---|---|---|---|
| SD | 1234.34 ± 331.15 | 1155.39 ± 287.68 | 38.67 ± 0.51 | -14.48 ± 5.46 | -13.76 ± 4.64 | 0.52 ± 0.08 |
| NF | 548.66 ± 6.00 | 532.98 ± 8.26 | 35.48 ± 0.62 | -3.50 ± 1.31 | -3.61 ± 1.14 | 0.07 ± 0.13 |
| DR | 504.47 ± 9.92 | 498.03 ± 9.18 | 54.30 ± 4.58 | 0.26 ± 1.10 | 0.36 ± 1.01 | 0.30 ± 0.38 |
| SD_nores | 2013.88 ± 203.71 | 1870.96 ± 193.20 | 95.76 ± 9.51 | -27.67 ± 4.18 | -26.13 ± 4.26 | -2.54 ± 0.20 |
baselines mse5 (marginal / proxy): GRAVE 2644.99 / 2629.79; DA 2518.74 / 2503.94; COMMON 81.86 / 80.61

#### R1c all per friend: mse5 GRAVE / COMMON per head
| friend | SD GRAVE | NF GRAVE | DR GRAVE | SD COMMON | NF COMMON | DR COMMON |
|---|---|---|---|---|---|---|
| Miso | 1235.28 ± 194.01 | 564.30 ± 20.55 | 443.10 ± 51.25 | 37.95 ± 0.51 | 35.81 ± 0.79 | 53.28 ± 3.65 |
| Biscuit | 1135.80 ± 587.99 | 442.02 ± 16.38 | 469.47 ± 26.67 | 36.16 ± 0.40 | 34.71 ± 1.03 | 52.84 ± 4.55 |
| Pumpkin | 1264.54 ± 91.32 | 960.92 ± 138.53 | 590.91 ± 20.74 | 39.58 ± 1.11 | 36.33 ± 0.73 | 53.95 ± 3.55 |
| Kittybear | 1412.86 ± 225.37 | 635.07 ± 11.89 | 531.20 ± 40.62 | 36.55 ± 0.90 | 30.93 ± 0.43 | 50.91 ± 6.12 |
| Clementine | 1272.22 ± 102.16 | 596.97 ± 55.83 | 682.80 ± 35.81 | 42.97 ± 1.03 | 39.54 ± 0.31 | 60.41 ± 5.15 |
| pooled | 1234.34 ± 331.15 | 548.66 ± 6.00 | 504.47 ± 9.92 | 38.67 ± 0.51 | 35.48 ± 0.62 | 54.30 ± 4.58 |

#### R2c all: SD loss over the comparator's, per class (READ when |r − 1| > SD)
| comparator | GRAVE | DA | COMMON |
|---|---|---|---|
| SD / NF | 2.250 ± 0.604 READ | 2.168 ± 0.541 READ | 1.090 ± 0.024 READ |
| SD / DR | 2.447 ± 0.658 READ | 2.320 ± 0.579 READ | 0.712 ± 0.061 READ |

#### R3c all: bias grave / common / gap (need points), SIG = signature, per head
| friend | SD | NF | DR |
|---|---|---|---|
| Miso | -17.40 / +0.44 / -17.84 SIG | -3.47 / -0.15 / -3.32 SIG | -0.40 / -0.07 / -0.33 SIG |
| Biscuit | -9.91 / +0.56 / -10.47 SIG | -0.87 / +0.55 / -1.41 SIG | +3.58 / +0.74 / +2.84 |
| Pumpkin | -21.12 / +0.50 / -21.63 SIG | -18.11 / -0.19 / -17.93 SIG | -10.61 / -0.09 / -10.51 SIG |
| Kittybear | -19.48 / +0.70 / -20.18 SIG | -6.05 / +0.75 / -6.80 SIG | -3.35 / +1.47 / -4.83 SIG |
| Clementine | -14.95 / +0.38 / -15.33 SIG | -2.30 / -0.61 / -1.70 SIG | +0.08 / -0.51 / +0.59 |
| pooled | -14.48 / +0.52 / -15.00 SIG | -3.50 / +0.07 / -3.56 SIG | +0.26 / +0.30 / -0.04 |

#### R6c(a) all: residual share — SD with the residual zeroed over the full head, per class: GRAVE 1.632 ± 0.468 READ, DA 1.619 ± 0.436 READ, COMMON 2.476 ± 0.248 READ → structure carries the fit (GRAVE ≤ 2.0×): True

### Width 16 (the declared head), group P (P1, P2, P3, P4, P5 eval worlds): n_samples 4000000
coverage GRAVE mind-visible: Miso 572, Biscuit 364, Pumpkin 398, Kittybear 933, Clementine 260

#### R1c visible: pooled mse5 on the five hidden needs (mean ± SD over seeds) and pooled bias
| head | GRAVE mse5 | DA mse5 | COMMON mse5 | GRAVE bias | DA bias | COMMON bias |
|---|---|---|---|---|---|---|
| SD | 1119.69 ± 71.25 | 921.40 ± 43.02 | 19.96 ± 0.39 | -15.01 ± 1.74 | -12.95 ± 1.29 | 0.42 ± 0.02 |
| NF | 908.10 ± 33.43 | 773.25 ± 20.58 | 25.34 ± 0.52 | -10.10 ± 1.08 | -8.96 ± 1.27 | 0.05 ± 0.14 |
| DR | 827.69 ± 117.06 | 725.06 ± 97.39 | 40.15 ± 6.85 | -7.57 ± 0.93 | -7.13 ± 0.83 | 0.19 ± 0.25 |
| SD_nores | 2253.93 ± 215.69 | 1890.40 ± 186.32 | 153.18 ± 7.41 | -31.59 ± 3.16 | -28.50 ± 3.23 | -1.82 ± 0.56 |
baselines mse5 (marginal / proxy): GRAVE 3264.16 / 3261.15; DA 2751.25 / 2749.84; COMMON 75.10 / 72.67

#### R1c visible per friend: mse5 GRAVE / COMMON per head
| friend | SD GRAVE | NF GRAVE | DR GRAVE | SD COMMON | NF COMMON | DR COMMON |
|---|---|---|---|---|---|---|
| Miso | 696.22 ± 92.24 | 613.31 ± 78.46 | 480.05 ± 84.11 | 18.80 ± 0.33 | 24.94 ± 0.65 | 38.41 ± 5.91 |
| Biscuit | 1383.92 ± 225.50 | 1245.18 ± 19.55 | 1011.13 ± 66.77 | 17.53 ± 0.45 | 24.05 ± 0.81 | 37.71 ± 6.14 |
| Pumpkin | 848.70 ± 66.79 | 714.87 ± 22.05 | 697.68 ± 93.75 | 21.81 ± 0.67 | 26.77 ± 0.71 | 41.41 ± 7.00 |
| Kittybear | 1429.29 ± 233.36 | 1081.52 ± 111.77 | 1021.69 ± 218.83 | 18.46 ± 0.47 | 21.86 ± 0.44 | 36.78 ± 7.08 |
| Clementine | 985.26 ± 235.02 | 758.16 ± 72.85 | 838.55 ± 49.32 | 23.06 ± 0.50 | 28.93 ± 0.20 | 46.18 ± 8.13 |
| pooled | 1119.69 ± 71.25 | 908.10 ± 33.43 | 827.69 ± 117.06 | 19.96 ± 0.39 | 25.34 ± 0.52 | 40.15 ± 6.85 |

#### R2c visible: SD loss over the comparator's, per class (READ when |r − 1| > SD)
| comparator | GRAVE | DA | COMMON |
|---|---|---|---|
| SD / NF | 1.233 ± 0.091 READ | 1.192 ± 0.064 READ | 0.787 ± 0.022 READ |
| SD / DR | 1.353 ± 0.210 READ | 1.271 ± 0.181 READ | 0.497 ± 0.085 READ |

#### R3c visible: bias grave / common / gap (need points), SIG = signature, per head
| friend | SD | NF | DR |
|---|---|---|---|
| Miso | -11.43 / +0.35 / -11.79 SIG | -5.77 / -0.21 / -5.57 SIG | -3.59 / -0.21 / -3.38 SIG |
| Biscuit | -16.95 / +0.22 / -17.18 SIG | -11.59 / +0.47 / -12.06 SIG | -8.22 / +0.55 / -8.77 SIG |
| Pumpkin | -11.61 / +0.54 / -12.15 SIG | -6.83 / -0.10 / -6.73 SIG | -4.12 / -0.07 / -4.05 SIG |
| Kittybear | -19.68 / +0.54 / -20.22 SIG | -17.01 / +0.65 / -17.66 SIG | -14.15 / +1.31 / -15.45 SIG |
| Clementine | -8.56 / +0.42 / -8.98 SIG | +2.27 / -0.56 / +2.83 | +2.89 / -0.57 / +3.46 |
| pooled | -15.01 / +0.42 / -15.42 SIG | -10.10 / +0.05 / -10.15 SIG | -7.57 / +0.19 / -7.77 SIG |

#### R6c(a) visible: residual share — SD with the residual zeroed over the full head, per class: GRAVE 2.013 ± 0.231 READ, DA 2.052 ± 0.224 READ, COMMON 7.676 ± 0.401 READ → structure carries the fit (GRAVE ≤ 2.0×): False

#### R1c all: pooled mse5 on the five hidden needs (mean ± SD over seeds) and pooled bias
| head | GRAVE mse5 | DA mse5 | COMMON mse5 | GRAVE bias | DA bias | COMMON bias |
|---|---|---|---|---|---|---|
| SD | 1082.26 ± 80.26 | 951.08 ± 64.17 | 30.38 ± 0.30 | -14.38 ± 1.92 | -12.60 ± 1.69 | 0.49 ± 0.02 |
| NF | 894.45 ± 21.77 | 795.12 ± 19.89 | 33.68 ± 0.54 | -8.67 ± 0.32 | -7.84 ± 0.41 | 0.05 ± 0.13 |
| DR | 729.70 ± 65.46 | 680.36 ± 59.05 | 54.48 ± 8.30 | -5.90 ± 0.21 | -5.73 ± 0.23 | 0.34 ± 0.46 |
| SD_nores | 2090.60 ± 135.13 | 1862.80 ± 130.54 | 171.82 ± 4.07 | -29.13 ± 2.97 | -27.39 ± 3.09 | -2.09 ± 0.58 |
baselines mse5 (marginal / proxy): GRAVE 3422.93 / 3402.49; DA 2995.87 / 2978.35; COMMON 78.84 / 77.59

#### R1c all per friend: mse5 GRAVE / COMMON per head
| friend | SD GRAVE | NF GRAVE | DR GRAVE | SD COMMON | NF COMMON | DR COMMON |
|---|---|---|---|---|---|---|
| Miso | 827.58 ± 44.41 | 716.65 ± 68.61 | 493.32 ± 46.92 | 29.31 ± 0.47 | 33.29 ± 0.71 | 52.70 ± 7.17 |
| Biscuit | 1150.29 ± 150.04 | 938.45 ± 51.76 | 766.85 ± 26.66 | 27.80 ± 0.51 | 32.33 ± 0.75 | 52.23 ± 7.54 |
| Pumpkin | 900.62 ± 28.82 | 767.35 ± 4.97 | 633.30 ± 54.46 | 32.33 ± 0.66 | 35.06 ± 0.64 | 55.61 ± 8.56 |
| Kittybear | 1487.10 ± 257.71 | 1149.32 ± 41.75 | 926.47 ± 180.10 | 27.91 ± 0.34 | 29.55 ± 0.42 | 51.00 ± 9.47 |
| Clementine | 868.95 ± 105.12 | 794.36 ± 26.17 | 770.40 ± 38.57 | 34.54 ± 0.38 | 38.18 ± 0.22 | 60.83 ± 8.82 |
| pooled | 1082.26 ± 80.26 | 894.45 ± 21.77 | 729.70 ± 65.46 | 30.38 ± 0.30 | 33.68 ± 0.54 | 54.48 ± 8.30 |

#### R2c all: SD loss over the comparator's, per class (READ when |r − 1| > SD)
| comparator | GRAVE | DA | COMMON |
|---|---|---|---|
| SD / NF | 1.210 ± 0.094 READ | 1.196 ± 0.086 READ | 0.902 ± 0.017 READ |
| SD / DR | 1.483 ± 0.173 READ | 1.398 ± 0.154 READ | 0.558 ± 0.085 READ |

#### R3c all: bias grave / common / gap (need points), SIG = signature, per head
| friend | SD | NF | DR |
|---|---|---|---|
| Miso | -13.70 / +0.53 / -14.22 SIG | -7.72 / -0.09 / -7.62 SIG | -4.90 / +0.07 / -4.97 SIG |
| Biscuit | -14.99 / +0.28 / -15.27 SIG | -7.83 / +0.43 / -8.25 SIG | -4.98 / +0.63 / -5.62 SIG |
| Pumpkin | -11.41 / +0.57 / -11.98 SIG | -5.47 / -0.16 / -5.31 SIG | -4.22 / +0.01 / -4.23 SIG |
| Kittybear | -21.65 / +0.61 / -22.26 SIG | -17.02 / +0.72 / -17.75 SIG | -13.12 / +1.49 / -14.60 SIG |
| Clementine | -5.98 / +0.48 / -6.46 SIG | -0.35 / -0.62 / +0.27 | +2.04 / -0.47 / +2.51 |
| pooled | -14.38 / +0.49 / -14.88 SIG | -8.67 / +0.05 / -8.72 SIG | -5.90 / +0.34 / -6.25 SIG |

#### R6c(a) all: residual share — SD with the residual zeroed over the full head, per class: GRAVE 1.932 ± 0.190 READ, DA 1.959 ± 0.191 READ, COMMON 5.656 ± 0.145 READ → structure carries the fit (GRAVE ≤ 2.0×): True

#### R4c visible: grave probability 1 − ∏(1 − m): Brier 0.0006 ± 0.0001; mean p on GRAVE 0.474 ± 0.115, on COMMON 0.000 ± 0.000; GRAVE samples 2527, of which happiness-only 168
| p bin | n | mean p | realised grave fraction |
|---|---|---|---|
| [0.0, 0.1) | 1923514 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| [0.1, 0.2) | 893 | 0.144 ± 0.003 | 0.251 ± 0.093 |
| [0.2, 0.3) | 550 | 0.247 ± 0.001 | 0.322 ± 0.095 |
| [0.3, 0.4) | 521 | 0.350 ± 0.001 | 0.446 ± 0.128 |
| [0.4, 0.5) | 424 | 0.448 ± 0.001 | 0.544 ± 0.099 |
| [0.5, 0.6) | 335 | 0.548 ± 0.002 | 0.623 ± 0.154 |
| [0.6, 0.7) | 349 | 0.649 ± 0.003 | 0.704 ± 0.079 |
| [0.7, 0.8) | 238 | 0.748 ± 0.004 | 0.795 ± 0.158 |
| [0.8, 0.9) | 170 | 0.851 ± 0.004 | 0.851 ± 0.088 |
| [0.9, 1.0) | 136 | 0.947 ± 0.006 | 0.936 ± 0.021 |

#### R4c all: grave probability 1 − ∏(1 − m): Brier 0.0013 ± 0.0001; mean p on GRAVE 0.494 ± 0.061, on COMMON 0.001 ± 0.000; GRAVE samples 11504, of which happiness-only 1280
| p bin | n | mean p | realised grave fraction |
|---|---|---|---|
| [0.0, 0.1) | 3981858 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| [0.1, 0.2) | 3000 | 0.146 ± 0.001 | 0.188 ± 0.092 |
| [0.2, 0.3) | 2651 | 0.251 ± 0.002 | 0.357 ± 0.094 |
| [0.3, 0.4) | 3284 | 0.346 ± 0.005 | 0.495 ± 0.088 |
| [0.4, 0.5) | 2943 | 0.447 ± 0.001 | 0.603 ± 0.052 |
| [0.5, 0.6) | 2269 | 0.550 ± 0.000 | 0.723 ± 0.050 |
| [0.6, 0.7) | 1597 | 0.648 ± 0.002 | 0.766 ± 0.044 |
| [0.7, 0.8) | 896 | 0.747 ± 0.002 | 0.747 ± 0.082 |
| [0.8, 0.9) | 922 | 0.854 ± 0.003 | 0.824 ± 0.067 |
| [0.9, 1.0) | 580 | 0.939 ± 0.008 | 0.921 ± 0.029 |

#### R6c(b): p_rel AUROC against the true relief indicator — in sight 0.979 ± 0.002, under fog 0.797 ± 0.009, all 0.914 ± 0.006

#### R7c SD against the DR floor: floor 827.69, candidate pooled 1119.69, ratio 1.353, pooled_ok False, friends_ok False → clears False
| friend | candidate grave | floor grave | excess over 1.10 × floor | candidate SD | clause |
|---|---|---|---|---|---|
| Miso | 696.22 | 480.05 | +168.16 | 92.24 | EXCEEDS |
| Biscuit | 1383.92 | 1011.13 | +271.68 | 225.50 | EXCEEDS |
| Pumpkin | 848.70 | 697.68 | +81.26 | 66.79 | EXCEEDS |
| Kittybear | 1429.29 | 1021.69 | +305.43 | 233.36 | EXCEEDS |
| Clementine | 985.26 | 838.55 | +62.86 | 235.02 | ok |

#### R7c SD against NF: floor 908.10, candidate pooled 1119.69, ratio 1.233, pooled_ok False, friends_ok False → clears False
| friend | candidate grave | floor grave | excess over 1.10 × floor | candidate SD | clause |
|---|---|---|---|---|---|
| Miso | 696.22 | 613.31 | +21.58 | 92.24 | ok |
| Biscuit | 1383.92 | 1245.18 | +14.22 | 225.50 | ok |
| Pumpkin | 848.70 | 714.87 | +62.34 | 66.79 | ok |
| Kittybear | 1429.29 | 1081.52 | +239.62 | 233.36 | EXCEEDS |
| Clementine | 985.26 | 758.16 | +151.29 | 235.02 | ok |

#### R7c NF against the DR floor (1b's R3b at width 24): floor 827.69, candidate pooled 908.10, ratio 1.097, pooled_ok True, friends_ok False → clears False
| friend | candidate grave | floor grave | excess over 1.10 × floor | candidate SD | clause |
|---|---|---|---|---|---|
| Miso | 613.31 | 480.05 | +85.26 | 78.46 | EXCEEDS |
| Biscuit | 1245.18 | 1011.13 | +132.94 | 19.55 | EXCEEDS |
| Pumpkin | 714.87 | 697.68 | -52.57 | 22.05 | ok |
| Kittybear | 1081.52 | 1021.69 | -42.35 | 111.77 | ok |
| Clementine | 758.16 | 838.55 | -164.25 | 72.85 | ok |

### Width 16 (the declared head), group G (G eval worlds): n_samples 640000
coverage GRAVE mind-visible: Miso 506, Biscuit 734, Pumpkin 166, Kittybear 638, Clementine 284

#### R1c visible: pooled mse5 on the five hidden needs (mean ± SD over seeds) and pooled bias
| head | GRAVE mse5 | DA mse5 | COMMON mse5 | GRAVE bias | DA bias | COMMON bias |
|---|---|---|---|---|---|---|
| SD | 734.34 ± 82.43 | 680.06 ± 51.62 | 21.59 ± 0.39 | -6.66 ± 2.51 | -7.03 ± 2.01 | 0.40 ± 0.02 |
| NF | 591.58 ± 20.73 | 559.51 ± 7.14 | 26.79 ± 0.60 | -4.94 ± 0.81 | -5.50 ± 0.78 | 0.04 ± 0.13 |
| DR | 580.94 ± 17.77 | 541.68 ± 32.62 | 42.40 ± 5.87 | -0.66 ± 1.24 | -0.85 ± 0.85 | 0.21 ± 0.27 |
| SD_nores | 1864.43 ± 92.81 | 1606.54 ± 98.49 | 140.84 ± 10.05 | -29.66 ± 2.34 | -26.47 ± 2.56 | -2.27 ± 0.47 |
baselines mse5 (marginal / proxy): GRAVE 2857.36 / 2851.80; DA 2614.03 / 2607.11; COMMON 78.12 / 75.73

#### R1c visible per friend: mse5 GRAVE / COMMON per head
| friend | SD GRAVE | NF GRAVE | DR GRAVE | SD COMMON | NF COMMON | DR COMMON |
|---|---|---|---|---|---|---|
| Miso | 652.75 ± 37.01 | 564.50 ± 59.96 | 453.75 ± 68.97 | 21.76 ± 0.87 | 27.62 ± 0.74 | 41.16 ± 4.87 |
| Biscuit | 824.88 ± 125.55 | 502.03 ± 46.90 | 604.64 ± 96.60 | 20.60 ± 0.23 | 26.79 ± 1.12 | 41.97 ± 5.16 |
| Pumpkin | — | — | — | 21.72 ± 0.24 | 27.37 ± 0.96 | 42.40 ± 5.50 |
| Kittybear | 734.87 ± 148.73 | 730.08 ± 69.60 | 611.51 ± 104.98 | 18.76 ± 0.14 | 22.43 ± 0.49 | 38.46 ± 6.48 |
| Clementine | 644.52 ± 141.02 | 560.15 ± 56.15 | 677.58 ± 52.90 | 24.95 ± 0.72 | 29.59 ± 0.21 | 47.76 ± 7.31 |
| pooled | 734.34 ± 82.43 | 591.58 ± 20.73 | 580.94 ± 17.77 | 21.59 ± 0.39 | 26.79 ± 0.60 | 42.40 ± 5.87 |

#### R2c visible: SD loss over the comparator's, per class (READ when |r − 1| > SD)
| comparator | GRAVE | DA | COMMON |
|---|---|---|---|
| SD / NF | 1.241 ± 0.146 READ | 1.215 ± 0.094 READ | 0.806 ± 0.023 READ |
| SD / DR | 1.264 ± 0.147 READ | 1.255 ± 0.122 READ | 0.509 ± 0.071 READ |

#### R3c visible: bias grave / common / gap (need points), SIG = signature, per head
| friend | SD | NF | DR |
|---|---|---|---|
| Miso | -7.21 / +0.24 / -7.45 SIG | -6.47 / -0.26 / -6.21 SIG | -2.33 / -0.29 / -2.04 SIG |
| Biscuit | -2.64 / +0.21 / -2.85 SIG | -1.86 / +0.52 / -2.38 SIG | +4.00 / +0.66 / +3.34 |
| Pumpkin | insufficient | insufficient | insufficient |
| Kittybear | -9.61 / +0.51 / -10.12 SIG | -8.81 / +0.65 / -9.46 SIG | -5.39 / +1.36 / -6.74 SIG |
| Clementine | -9.47 / +0.48 / -9.96 SIG | -1.51 / -0.55 / -0.95 SIG | +0.94 / -0.54 / +1.48 |
| pooled | -6.66 / +0.40 / -7.06 SIG | -4.94 / +0.04 / -4.98 SIG | -0.66 / +0.21 / -0.87 SIG |

#### R6c(a) visible: residual share — SD with the residual zeroed over the full head, per class: GRAVE 2.539 ± 0.312 READ, DA 2.362 ± 0.230 READ, COMMON 6.523 ± 0.480 READ → structure carries the fit (GRAVE ≤ 2.0×): False

#### R1c all: pooled mse5 on the five hidden needs (mean ± SD over seeds) and pooled bias
| head | GRAVE mse5 | DA mse5 | COMMON mse5 | GRAVE bias | DA bias | COMMON bias |
|---|---|---|---|---|---|---|
| SD | 769.70 ± 73.81 | 738.43 ± 65.20 | 32.81 ± 0.43 | -3.76 ± 3.75 | -3.89 ± 3.13 | 0.51 ± 0.03 |
| NF | 548.66 ± 6.00 | 532.98 ± 8.26 | 35.48 ± 0.62 | -3.50 ± 1.31 | -3.61 ± 1.14 | 0.07 ± 0.13 |
| DR | 504.47 ± 9.92 | 498.03 ± 9.18 | 54.30 ± 4.58 | 0.26 ± 1.10 | 0.36 ± 1.01 | 0.30 ± 0.38 |
| SD_nores | 2042.35 ± 87.14 | 1898.11 ± 83.95 | 151.21 ± 5.94 | -30.70 ± 2.56 | -28.83 ± 2.57 | -2.83 ± 0.47 |
baselines mse5 (marginal / proxy): GRAVE 2644.99 / 2629.79; DA 2518.74 / 2503.94; COMMON 81.86 / 80.61

#### R1c all per friend: mse5 GRAVE / COMMON per head
| friend | SD GRAVE | NF GRAVE | DR GRAVE | SD COMMON | NF COMMON | DR COMMON |
|---|---|---|---|---|---|---|
| Miso | 765.50 ± 57.75 | 564.30 ± 20.55 | 443.10 ± 51.25 | 31.83 ± 1.01 | 35.81 ± 0.79 | 53.28 ± 3.65 |
| Biscuit | 733.89 ± 116.91 | 442.02 ± 16.38 | 469.47 ± 26.67 | 31.34 ± 0.20 | 34.71 ± 1.03 | 52.84 ± 4.55 |
| Pumpkin | 1094.42 ± 190.25 | 960.92 ± 138.53 | 590.91 ± 20.74 | 33.35 ± 0.31 | 36.33 ± 0.73 | 53.95 ± 3.55 |
| Kittybear | 756.63 ± 32.88 | 635.07 ± 11.89 | 531.20 ± 40.62 | 30.12 ± 0.46 | 30.93 ± 0.43 | 50.91 ± 6.12 |
| Clementine | 800.27 ± 193.50 | 596.97 ± 55.83 | 682.80 ± 35.81 | 37.30 ± 0.30 | 39.54 ± 0.31 | 60.41 ± 5.15 |
| pooled | 769.70 ± 73.81 | 548.66 ± 6.00 | 504.47 ± 9.92 | 32.81 ± 0.43 | 35.48 ± 0.62 | 54.30 ± 4.58 |

#### R2c all: SD loss over the comparator's, per class (READ when |r − 1| > SD)
| comparator | GRAVE | DA | COMMON |
|---|---|---|---|
| SD / NF | 1.403 ± 0.135 READ | 1.385 ± 0.124 READ | 0.925 ± 0.020 READ |
| SD / DR | 1.526 ± 0.149 READ | 1.483 ± 0.134 READ | 0.604 ± 0.052 READ |

#### R3c all: bias grave / common / gap (need points), SIG = signature, per head
| friend | SD | NF | DR |
|---|---|---|---|
| Miso | -4.80 / +0.43 / -5.23 SIG | -3.47 / -0.15 / -3.32 SIG | -0.40 / -0.07 / -0.33 SIG |
| Biscuit | +0.75 / +0.35 / +0.40 | -0.87 / +0.55 / -1.41 SIG | +3.58 / +0.74 / +2.84 |
| Pumpkin | -18.39 / +0.59 / -18.97 SIG | -18.11 / -0.19 / -17.93 SIG | -10.61 / -0.09 / -10.51 SIG |
| Kittybear | -7.20 / +0.61 / -7.81 SIG | -6.05 / +0.75 / -6.80 SIG | -3.35 / +1.47 / -4.83 SIG |
| Clementine | -6.91 / +0.56 / -7.47 SIG | -2.30 / -0.61 / -1.70 SIG | +0.08 / -0.51 / +0.59 |
| pooled | -3.76 / +0.51 / -4.26 SIG | -3.50 / +0.07 / -3.56 SIG | +0.26 / +0.30 / -0.04 |

#### R6c(a) all: residual share — SD with the residual zeroed over the full head, per class: GRAVE 2.653 ± 0.278 READ, DA 2.570 ± 0.254 READ, COMMON 4.608 ± 0.191 READ → structure carries the fit (GRAVE ≤ 2.0×): False

### Width 32 (the over-cap probe), group P (P1, P2, P3, P4, P5 eval worlds): n_samples 4000000
coverage GRAVE mind-visible: Miso 572, Biscuit 364, Pumpkin 398, Kittybear 933, Clementine 260

#### R1c visible: pooled mse5 on the five hidden needs (mean ± SD over seeds) and pooled bias
| head | GRAVE mse5 | DA mse5 | COMMON mse5 | GRAVE bias | DA bias | COMMON bias |
|---|---|---|---|---|---|---|
| SD | 917.44 ± 67.65 | 761.34 ± 43.20 | 16.92 ± 0.40 | -11.07 ± 2.42 | -9.56 ± 1.85 | 0.41 ± 0.09 |
| NF | 908.10 ± 33.43 | 773.25 ± 20.58 | 25.34 ± 0.52 | -10.10 ± 1.08 | -8.96 ± 1.27 | 0.05 ± 0.14 |
| DR | 827.69 ± 117.06 | 725.06 ± 97.39 | 40.15 ± 6.85 | -7.57 ± 0.93 | -7.13 ± 0.83 | 0.19 ± 0.25 |
| SD_nores | 2704.63 ± 16.28 | 2247.29 ± 8.13 | 176.94 ± 5.25 | -38.21 ± 0.47 | -34.10 ± 0.34 | -1.83 ± 0.19 |
baselines mse5 (marginal / proxy): GRAVE 3264.16 / 3261.15; DA 2751.25 / 2749.84; COMMON 75.10 / 72.67

#### R1c visible per friend: mse5 GRAVE / COMMON per head
| friend | SD GRAVE | NF GRAVE | DR GRAVE | SD COMMON | NF COMMON | DR COMMON |
|---|---|---|---|---|---|---|
| Miso | 548.47 ± 203.95 | 613.31 ± 78.46 | 480.05 ± 84.11 | 16.14 ± 0.48 | 24.94 ± 0.65 | 38.41 ± 5.91 |
| Biscuit | 1066.78 ± 90.75 | 1245.18 ± 19.55 | 1011.13 ± 66.77 | 14.92 ± 0.33 | 24.05 ± 0.81 | 37.71 ± 6.14 |
| Pumpkin | 833.94 ± 102.66 | 714.87 ± 22.05 | 697.68 ± 93.75 | 18.32 ± 0.76 | 26.77 ± 0.71 | 41.41 ± 7.00 |
| Kittybear | 1174.08 ± 115.48 | 1081.52 ± 111.77 | 1021.69 ± 218.83 | 15.88 ± 0.15 | 21.86 ± 0.44 | 36.78 ± 7.08 |
| Clementine | 726.99 ± 191.31 | 758.16 ± 72.85 | 838.55 ± 49.32 | 19.26 ± 0.42 | 28.93 ± 0.20 | 46.18 ± 8.13 |
| pooled | 917.44 ± 67.65 | 908.10 ± 33.43 | 827.69 ± 117.06 | 16.92 ± 0.40 | 25.34 ± 0.52 | 40.15 ± 6.85 |

#### R2c visible: SD loss over the comparator's, per class (READ when |r − 1| > SD)
| comparator | GRAVE | DA | COMMON |
|---|---|---|---|
| SD / NF | 1.010 ± 0.083 | 0.985 ± 0.062 | 0.668 ± 0.021 READ |
| SD / DR | 1.108 ± 0.177 | 1.050 ± 0.153 | 0.421 ± 0.073 READ |

#### R3c visible: bias grave / common / gap (need points), SIG = signature, per head
| friend | SD | NF | DR |
|---|---|---|---|
| Miso | -7.86 / +0.40 / -8.26 SIG | -5.77 / -0.21 / -5.57 SIG | -3.59 / -0.21 / -3.38 SIG |
| Biscuit | -13.16 / +0.23 / -13.38 SIG | -11.59 / +0.47 / -12.06 SIG | -8.22 / +0.55 / -8.77 SIG |
| Pumpkin | -8.59 / +0.49 / -9.08 SIG | -6.83 / -0.10 / -6.73 SIG | -4.12 / -0.07 / -4.05 SIG |
| Kittybear | -15.91 / +0.50 / -16.41 SIG | -17.01 / +0.65 / -17.66 SIG | -14.15 / +1.31 / -15.45 SIG |
| Clementine | -1.61 / +0.43 / -2.04 SIG | +2.27 / -0.56 / +2.83 | +2.89 / -0.57 / +3.46 |
| pooled | -11.07 / +0.41 / -11.48 SIG | -10.10 / +0.05 / -10.15 SIG | -7.57 / +0.19 / -7.77 SIG |

#### R6c(a) visible: residual share — SD with the residual zeroed over the full head, per class: GRAVE 2.948 ± 0.218 READ, DA 2.952 ± 0.168 READ, COMMON 10.457 ± 0.396 READ → structure carries the fit (GRAVE ≤ 2.0×): False

#### R1c all: pooled mse5 on the five hidden needs (mean ± SD over seeds) and pooled bias
| head | GRAVE mse5 | DA mse5 | COMMON mse5 | GRAVE bias | DA bias | COMMON bias |
|---|---|---|---|---|---|---|
| SD | 911.95 ± 36.04 | 808.97 ± 26.87 | 26.94 ± 0.39 | -11.11 ± 0.95 | -9.80 ± 0.93 | 0.47 ± 0.13 |
| NF | 894.45 ± 21.77 | 795.12 ± 19.89 | 33.68 ± 0.54 | -8.67 ± 0.32 | -7.84 ± 0.41 | 0.05 ± 0.13 |
| DR | 729.70 ± 65.46 | 680.36 ± 59.05 | 54.48 ± 8.30 | -5.90 ± 0.21 | -5.73 ± 0.23 | 0.34 ± 0.46 |
| SD_nores | 2562.64 ± 42.11 | 2269.51 ± 34.50 | 197.69 ± 6.42 | -37.17 ± 0.55 | -34.71 ± 0.42 | -1.98 ± 0.18 |
baselines mse5 (marginal / proxy): GRAVE 3422.93 / 3402.49; DA 2995.87 / 2978.35; COMMON 78.84 / 77.59

#### R1c all per friend: mse5 GRAVE / COMMON per head
| friend | SD GRAVE | NF GRAVE | DR GRAVE | SD COMMON | NF COMMON | DR COMMON |
|---|---|---|---|---|---|---|
| Miso | 758.97 ± 82.72 | 716.65 ± 68.61 | 493.32 ± 46.92 | 26.04 ± 0.32 | 33.29 ± 0.71 | 52.70 ± 7.17 |
| Biscuit | 910.14 ± 78.40 | 938.45 ± 51.76 | 766.85 ± 26.66 | 24.68 ± 0.50 | 32.33 ± 0.75 | 52.23 ± 7.54 |
| Pumpkin | 840.34 ± 76.53 | 767.35 ± 4.97 | 633.30 ± 54.46 | 28.73 ± 0.68 | 35.06 ± 0.64 | 55.61 ± 8.56 |
| Kittybear | 1176.10 ± 128.32 | 1149.32 ± 41.75 | 926.47 ± 180.10 | 24.93 ± 0.28 | 29.55 ± 0.42 | 51.00 ± 9.47 |
| Clementine | 747.55 ± 109.96 | 794.36 ± 26.17 | 770.40 ± 38.57 | 30.30 ± 0.54 | 38.18 ± 0.22 | 60.83 ± 8.82 |
| pooled | 911.95 ± 36.04 | 894.45 ± 21.77 | 729.70 ± 65.46 | 26.94 ± 0.39 | 33.68 ± 0.54 | 54.48 ± 8.30 |

#### R2c all: SD loss over the comparator's, per class (READ when |r − 1| > SD)
| comparator | GRAVE | DA | COMMON |
|---|---|---|---|
| SD / NF | 1.020 ± 0.047 | 1.017 ± 0.042 | 0.800 ± 0.017 READ |
| SD / DR | 1.250 ± 0.123 READ | 1.189 ± 0.110 READ | 0.494 ± 0.076 READ |

#### R3c all: bias grave / common / gap (need points), SIG = signature, per head
| friend | SD | NF | DR |
|---|---|---|---|
| Miso | -11.56 / +0.51 / -12.07 SIG | -7.72 / -0.09 / -7.62 SIG | -4.90 / +0.07 / -4.97 SIG |
| Biscuit | -10.67 / +0.24 / -10.91 SIG | -7.83 / +0.43 / -8.25 SIG | -4.98 / +0.63 / -5.62 SIG |
| Pumpkin | -10.43 / +0.53 / -10.97 SIG | -5.47 / -0.16 / -5.31 SIG | -4.22 / +0.01 / -4.23 SIG |
| Kittybear | -17.40 / +0.54 / -17.95 SIG | -17.02 / +0.72 / -17.75 SIG | -13.12 / +1.49 / -14.60 SIG |
| Clementine | -1.36 / +0.50 / -1.87 SIG | -0.35 / -0.62 / +0.27 | +2.04 / -0.47 / +2.51 |
| pooled | -11.11 / +0.47 / -11.57 SIG | -8.67 / +0.05 / -8.72 SIG | -5.90 / +0.34 / -6.25 SIG |

#### R6c(a) all: residual share — SD with the residual zeroed over the full head, per class: GRAVE 2.810 ± 0.120 READ, DA 2.805 ± 0.102 READ, COMMON 7.339 ± 0.261 READ → structure carries the fit (GRAVE ≤ 2.0×): False

#### R4c visible: grave probability 1 − ∏(1 − m): Brier 0.0005 ± 0.0001; mean p on GRAVE 0.545 ± 0.087, on COMMON 0.000 ± 0.000; GRAVE samples 2527, of which happiness-only 168
| p bin | n | mean p | realised grave fraction |
|---|---|---|---|
| [0.0, 0.1) | 1923314 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| [0.1, 0.2) | 651 | 0.146 ± 0.001 | 0.338 ± 0.136 |
| [0.2, 0.3) | 422 | 0.250 ± 0.002 | 0.521 ± 0.143 |
| [0.3, 0.4) | 386 | 0.348 ± 0.004 | 0.502 ± 0.099 |
| [0.4, 0.5) | 337 | 0.447 ± 0.003 | 0.706 ± 0.072 |
| [0.5, 0.6) | 284 | 0.548 ± 0.001 | 0.733 ± 0.054 |
| [0.6, 0.7) | 248 | 0.651 ± 0.001 | 0.738 ± 0.095 |
| [0.7, 0.8) | 291 | 0.751 ± 0.004 | 0.785 ± 0.045 |
| [0.8, 0.9) | 327 | 0.852 ± 0.001 | 0.881 ± 0.047 |
| [0.9, 1.0) | 870 | 0.962 ± 0.005 | 0.964 ± 0.019 |

#### R4c all: grave probability 1 − ∏(1 − m): Brier 0.0011 ± 0.0001; mean p on GRAVE 0.529 ± 0.062, on COMMON 0.000 ± 0.000; GRAVE samples 11504, of which happiness-only 1280
| p bin | n | mean p | realised grave fraction |
|---|---|---|---|
| [0.0, 0.1) | 3980801 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| [0.1, 0.2) | 2750 | 0.146 ± 0.002 | 0.212 ± 0.108 |
| [0.2, 0.3) | 2485 | 0.250 ± 0.003 | 0.410 ± 0.122 |
| [0.3, 0.4) | 3175 | 0.348 ± 0.002 | 0.533 ± 0.083 |
| [0.4, 0.5) | 2393 | 0.449 ± 0.004 | 0.763 ± 0.061 |
| [0.5, 0.6) | 1751 | 0.549 ± 0.003 | 0.771 ± 0.062 |
| [0.6, 0.7) | 1708 | 0.648 ± 0.002 | 0.806 ± 0.059 |
| [0.7, 0.8) | 1518 | 0.748 ± 0.002 | 0.821 ± 0.046 |
| [0.8, 0.9) | 1651 | 0.848 ± 0.003 | 0.867 ± 0.047 |
| [0.9, 1.0) | 1768 | 0.950 ± 0.003 | 0.961 ± 0.023 |

#### R6c(b): p_rel AUROC against the true relief indicator — in sight 0.988 ± 0.000, under fog 0.823 ± 0.003, all 0.932 ± 0.001

#### R7c SD against the DR floor: floor 827.69, candidate pooled 917.44, ratio 1.108, pooled_ok False, friends_ok True → clears False
| friend | candidate grave | floor grave | excess over 1.10 × floor | candidate SD | clause |
|---|---|---|---|---|---|
| Miso | 548.47 | 480.05 | +20.42 | 203.95 | ok |
| Biscuit | 1066.78 | 1011.13 | -45.46 | 90.75 | ok |
| Pumpkin | 833.94 | 697.68 | +66.50 | 102.66 | ok |
| Kittybear | 1174.08 | 1021.69 | +50.22 | 115.48 | ok |
| Clementine | 726.99 | 838.55 | -195.41 | 191.31 | ok |

#### R7c SD against NF: floor 908.10, candidate pooled 917.44, ratio 1.010, pooled_ok True, friends_ok True → clears True
| friend | candidate grave | floor grave | excess over 1.10 × floor | candidate SD | clause |
|---|---|---|---|---|---|
| Miso | 548.47 | 613.31 | -126.17 | 203.95 | ok |
| Biscuit | 1066.78 | 1245.18 | -302.91 | 90.75 | ok |
| Pumpkin | 833.94 | 714.87 | +47.58 | 102.66 | ok |
| Kittybear | 1174.08 | 1081.52 | -15.59 | 115.48 | ok |
| Clementine | 726.99 | 758.16 | -106.98 | 191.31 | ok |

#### R7c NF against the DR floor (1b's R3b at width 24): floor 827.69, candidate pooled 908.10, ratio 1.097, pooled_ok True, friends_ok False → clears False
| friend | candidate grave | floor grave | excess over 1.10 × floor | candidate SD | clause |
|---|---|---|---|---|---|
| Miso | 613.31 | 480.05 | +85.26 | 78.46 | EXCEEDS |
| Biscuit | 1245.18 | 1011.13 | +132.94 | 19.55 | EXCEEDS |
| Pumpkin | 714.87 | 697.68 | -52.57 | 22.05 | ok |
| Kittybear | 1081.52 | 1021.69 | -42.35 | 111.77 | ok |
| Clementine | 758.16 | 838.55 | -164.25 | 72.85 | ok |

### Width 32 (the over-cap probe), group G (G eval worlds): n_samples 640000
coverage GRAVE mind-visible: Miso 506, Biscuit 734, Pumpkin 166, Kittybear 638, Clementine 284

#### R1c visible: pooled mse5 on the five hidden needs (mean ± SD over seeds) and pooled bias
| head | GRAVE mse5 | DA mse5 | COMMON mse5 | GRAVE bias | DA bias | COMMON bias |
|---|---|---|---|---|---|---|
| SD | 615.09 ± 80.23 | 583.42 ± 68.42 | 18.36 ± 0.61 | -5.59 ± 1.49 | -5.55 ± 1.92 | 0.38 ± 0.09 |
| NF | 591.58 ± 20.73 | 559.51 ± 7.14 | 26.79 ± 0.60 | -4.94 ± 0.81 | -5.50 ± 0.78 | 0.04 ± 0.13 |
| DR | 580.94 ± 17.77 | 541.68 ± 32.62 | 42.40 ± 5.87 | -0.66 ± 1.24 | -0.85 ± 0.85 | 0.21 ± 0.27 |
| SD_nores | 2215.51 ± 19.23 | 1894.30 ± 27.41 | 164.26 ± 5.88 | -35.51 ± 0.38 | -31.99 ± 0.34 | -2.38 ± 0.21 |
baselines mse5 (marginal / proxy): GRAVE 2857.36 / 2851.80; DA 2614.03 / 2607.11; COMMON 78.12 / 75.73

#### R1c visible per friend: mse5 GRAVE / COMMON per head
| friend | SD GRAVE | NF GRAVE | DR GRAVE | SD COMMON | NF COMMON | DR COMMON |
|---|---|---|---|---|---|---|
| Miso | 543.97 ± 39.68 | 564.50 ± 59.96 | 453.75 ± 68.97 | 19.04 ± 0.97 | 27.62 ± 0.74 | 41.16 ± 4.87 |
| Biscuit | 597.59 ± 137.84 | 502.03 ± 46.90 | 604.64 ± 96.60 | 16.91 ± 0.49 | 26.79 ± 1.12 | 41.97 ± 5.16 |
| Pumpkin | — | — | — | 18.26 ± 1.09 | 27.37 ± 0.96 | 42.40 ± 5.50 |
| Kittybear | 772.81 ± 171.49 | 730.08 ± 69.60 | 611.51 ± 104.98 | 16.10 ± 0.63 | 22.43 ± 0.49 | 38.46 ± 6.48 |
| Clementine | 432.70 ± 143.46 | 560.15 ± 56.15 | 677.58 ± 52.90 | 21.34 ± 0.43 | 29.59 ± 0.21 | 47.76 ± 7.31 |
| pooled | 615.09 ± 80.23 | 591.58 ± 20.73 | 580.94 ± 17.77 | 18.36 ± 0.61 | 26.79 ± 0.60 | 42.40 ± 5.87 |

#### R2c visible: SD loss over the comparator's, per class (READ when |r − 1| > SD)
| comparator | GRAVE | DA | COMMON |
|---|---|---|---|
| SD / NF | 1.040 ± 0.140 | 1.043 ± 0.123 | 0.685 ± 0.027 READ |
| SD / DR | 1.059 ± 0.142 | 1.077 ± 0.142 | 0.433 ± 0.062 READ |

#### R3c visible: bias grave / common / gap (need points), SIG = signature, per head
| friend | SD | NF | DR |
|---|---|---|---|
| Miso | -3.70 / +0.29 / -3.99 SIG | -6.47 / -0.26 / -6.21 SIG | -2.33 / -0.29 / -2.04 SIG |
| Biscuit | -4.83 / +0.19 / -5.03 SIG | -1.86 / +0.52 / -2.38 SIG | +4.00 / +0.66 / +3.34 |
| Pumpkin | insufficient | insufficient | insufficient |
| Kittybear | -9.64 / +0.47 / -10.10 SIG | -8.81 / +0.65 / -9.46 SIG | -5.39 / +1.36 / -6.74 SIG |
| Clementine | -1.87 / +0.45 / -2.32 SIG | -1.51 / -0.55 / -0.95 SIG | +0.94 / -0.54 / +1.48 |
| pooled | -5.59 / +0.38 / -5.97 SIG | -4.94 / +0.04 / -4.98 SIG | -0.66 / +0.21 / -0.87 SIG |

#### R6c(a) visible: residual share — SD with the residual zeroed over the full head, per class: GRAVE 3.602 ± 0.471 READ, DA 3.247 ± 0.384 READ, COMMON 8.946 ± 0.436 READ → structure carries the fit (GRAVE ≤ 2.0×): False

#### R1c all: pooled mse5 on the five hidden needs (mean ± SD over seeds) and pooled bias
| head | GRAVE mse5 | DA mse5 | COMMON mse5 | GRAVE bias | DA bias | COMMON bias |
|---|---|---|---|---|---|---|
| SD | 620.52 ± 95.41 | 610.06 ± 89.72 | 28.81 ± 0.75 | -5.31 ± 1.53 | -5.08 ± 1.73 | 0.44 ± 0.12 |
| NF | 548.66 ± 6.00 | 532.98 ± 8.26 | 35.48 ± 0.62 | -3.50 ± 1.31 | -3.61 ± 1.14 | 0.07 ± 0.13 |
| DR | 504.47 ± 9.92 | 498.03 ± 9.18 | 54.30 ± 4.58 | 0.26 ± 1.10 | 0.36 ± 1.01 | 0.30 ± 0.38 |
| SD_nores | 2433.15 ± 32.37 | 2271.41 ± 33.90 | 176.02 ± 5.79 | -37.47 ± 0.42 | -35.70 ± 0.42 | -2.89 ± 0.18 |
baselines mse5 (marginal / proxy): GRAVE 2644.99 / 2629.79; DA 2518.74 / 2503.94; COMMON 81.86 / 80.61

#### R1c all per friend: mse5 GRAVE / COMMON per head
| friend | SD GRAVE | NF GRAVE | DR GRAVE | SD COMMON | NF COMMON | DR COMMON |
|---|---|---|---|---|---|---|
| Miso | 626.80 ± 92.71 | 564.30 ± 20.55 | 443.10 ± 51.25 | 28.65 ± 0.94 | 35.81 ± 0.79 | 53.28 ± 3.65 |
| Biscuit | 542.18 ± 132.21 | 442.02 ± 16.38 | 469.47 ± 26.67 | 26.83 ± 0.68 | 34.71 ± 1.03 | 52.84 ± 4.55 |
| Pumpkin | 894.84 ± 105.84 | 960.92 ± 138.53 | 590.91 ± 20.74 | 29.40 ± 1.49 | 36.33 ± 0.73 | 53.95 ± 3.55 |
| Kittybear | 690.21 ± 157.54 | 635.07 ± 11.89 | 531.20 ± 40.62 | 26.17 ± 0.44 | 30.93 ± 0.43 | 50.91 ± 6.12 |
| Clementine | 667.68 ± 161.13 | 596.97 ± 55.83 | 682.80 ± 35.81 | 32.90 ± 0.69 | 39.54 ± 0.31 | 60.41 ± 5.15 |
| pooled | 620.52 ± 95.41 | 548.66 ± 6.00 | 504.47 ± 9.92 | 28.81 ± 0.75 | 35.48 ± 0.62 | 54.30 ± 4.58 |

#### R2c all: SD loss over the comparator's, per class (READ when |r − 1| > SD)
| comparator | GRAVE | DA | COMMON |
|---|---|---|---|
| SD / NF | 1.131 ± 0.174 | 1.145 ± 0.169 | 0.812 ± 0.025 READ |
| SD / DR | 1.230 ± 0.191 READ | 1.225 ± 0.182 READ | 0.531 ± 0.047 READ |

#### R3c all: bias grave / common / gap (need points), SIG = signature, per head
| friend | SD | NF | DR |
|---|---|---|---|
| Miso | -3.13 / +0.41 / -3.54 SIG | -3.47 / -0.15 / -3.32 SIG | -0.40 / -0.07 / -0.33 SIG |
| Biscuit | -4.53 / +0.26 / -4.78 SIG | -0.87 / +0.55 / -1.41 SIG | +3.58 / +0.74 / +2.84 |
| Pumpkin | -15.50 / +0.49 / -15.99 SIG | -18.11 / -0.19 / -17.93 SIG | -10.61 / -0.09 / -10.51 SIG |
| Kittybear | -8.17 / +0.52 / -8.69 SIG | -6.05 / +0.75 / -6.80 SIG | -3.35 / +1.47 / -4.83 SIG |
| Clementine | -1.67 / +0.54 / -2.21 SIG | -2.30 / -0.61 / -1.70 SIG | +0.08 / -0.51 / +0.59 |
| pooled | -5.31 / +0.44 / -5.75 SIG | -3.50 / +0.07 / -3.56 SIG | +0.26 / +0.30 / -0.04 |

#### R6c(a) all: residual share — SD with the residual zeroed over the full head, per class: GRAVE 3.921 ± 0.605 READ, DA 3.723 ± 0.550 READ, COMMON 6.109 ± 0.256 READ → structure carries the fit (GRAVE ≤ 2.0×): False

### R9c: size effect — SD pooled mse5 at width h over width 16 (first-order SD; READ when |r − 1| > SD)
| group | version | w8 GRAVE | w8 DA | w8 COMMON | w32 GRAVE | w32 DA | w32 COMMON |
|---|---|---|---|---|---|---|---|
| P | visible | 1.414 ± 0.190 READ | 1.420 ± 0.165 READ | 1.237 ± 0.025 READ | 0.819 ± 0.080 READ | 0.826 ± 0.061 READ | 0.848 ± 0.026 READ |
| P | all | 1.415 ± 0.152 READ | 1.411 ± 0.145 READ | 1.206 ± 0.021 READ | 0.843 ± 0.071 READ | 0.851 ± 0.064 READ | 0.887 ± 0.015 READ |
| G | visible | 1.666 ± 0.419 READ | 1.574 ± 0.322 READ | 1.232 ± 0.027 READ | 0.838 ± 0.144 READ | 0.858 ± 0.120 READ | 0.850 ± 0.032 READ |
| G | all | 1.604 ± 0.457 READ | 1.565 ± 0.413 READ | 1.178 ± 0.022 READ | 0.806 ± 0.146 READ | 0.826 ± 0.142 READ | 0.878 ± 0.025 READ |

### R5c width 8: learned rise rates (points per tick, mean ± SD over seeds) against the training worlds' median positive step
| friend | eat learned / empirical | drink learned / empirical | sleep learned / empirical | play learned / empirical | cuddle learned / empirical |
|---|---|---|---|---|---|
| Miso | 0.18 ± 0.01 / 0.30 | 0.29 ± 0.01 / 0.40 | 0.70 ± 0.06 / 0.60 | 0.04 ± 0.00 / 0.30 | 0.23 ± 0.01 / 0.40 |
| Biscuit | 0.18 ± 0.01 / 0.30 | 0.12 ± 0.04 / 0.30 | 0.18 ± 0.02 / 0.30 | 0.30 ± 0.03 / 0.80 | 0.24 ± 0.01 / 0.40 |
| Pumpkin | 0.66 ± 0.03 / 0.60 | 0.30 ± 0.01 / 0.40 | 0.08 ± 0.01 / 0.20 | 0.08 ± 0.01 / 0.40 | 0.26 ± 0.01 / 0.40 |
| Kittybear | 0.29 ± 0.02 / 0.40 | 0.12 ± 0.04 / 0.30 | 0.15 ± 0.02 / 0.30 | 0.04 ± 0.00 / 0.30 | 0.23 ± 0.01 / 0.40 |
| Clementine | 0.34 ± 0.01 / 0.40 | 0.30 ± 0.01 / 0.40 | 0.20 ± 0.02 / 0.30 | 0.04 ± 0.01 / 0.30 | 0.67 ± 0.07 / 0.70 |
relief sizes learned (points per relieving tick): eat 39.41 ± 0.97, drink 37.32 ± 2.99, sleep 13.60 ± 0.66, play 19.70 ± 1.15, cuddle 27.76 ± 3.72

### R5c width 16: learned rise rates (points per tick, mean ± SD over seeds) against the training worlds' median positive step
| friend | eat learned / empirical | drink learned / empirical | sleep learned / empirical | play learned / empirical | cuddle learned / empirical |
|---|---|---|---|---|---|
| Miso | 0.11 ± 0.03 / 0.30 | 0.28 ± 0.03 / 0.40 | 0.82 ± 0.00 / 0.60 | 0.03 ± 0.00 / 0.30 | 0.15 ± 0.03 / 0.40 |
| Biscuit | 0.11 ± 0.03 / 0.30 | 0.05 ± 0.01 / 0.30 | 0.17 ± 0.02 / 0.30 | 0.32 ± 0.02 / 0.80 | 0.15 ± 0.03 / 0.40 |
| Pumpkin | 1.23 ± 0.15 / 0.60 | 0.29 ± 0.03 / 0.40 | 0.06 ± 0.02 / 0.20 | 0.06 ± 0.00 / 0.40 | 0.15 ± 0.03 / 0.40 |
| Kittybear | 0.33 ± 0.05 / 0.40 | 0.05 ± 0.01 / 0.30 | 0.15 ± 0.02 / 0.30 | 0.03 ± 0.00 / 0.30 | 0.14 ± 0.03 / 0.40 |
| Clementine | 0.38 ± 0.05 / 0.40 | 0.29 ± 0.02 / 0.40 | 0.20 ± 0.02 / 0.30 | 0.03 ± 0.00 / 0.30 | 0.71 ± 0.02 / 0.70 |
relief sizes learned (points per relieving tick): eat 35.44 ± 0.45, drink 27.25 ± 9.39, sleep 10.78 ± 2.28, play 18.82 ± 0.26, cuddle 19.31 ± 2.43

### R5c width 32: learned rise rates (points per tick, mean ± SD over seeds) against the training worlds' median positive step
| friend | eat learned / empirical | drink learned / empirical | sleep learned / empirical | play learned / empirical | cuddle learned / empirical |
|---|---|---|---|---|---|
| Miso | 0.07 ± 0.00 / 0.30 | 0.24 ± 0.01 / 0.40 | 0.96 ± 0.06 / 0.60 | 0.03 ± 0.00 / 0.30 | 0.11 ± 0.00 / 0.40 |
| Biscuit | 0.07 ± 0.00 / 0.30 | 0.03 ± 0.00 / 0.30 | 0.15 ± 0.02 / 0.30 | 0.35 ± 0.02 / 0.80 | 0.11 ± 0.00 / 0.40 |
| Pumpkin | 1.09 ± 0.05 / 0.60 | 0.24 ± 0.01 / 0.40 | 0.03 ± 0.00 / 0.20 | 0.06 ± 0.00 / 0.40 | 0.12 ± 0.00 / 0.40 |
| Kittybear | 0.25 ± 0.01 / 0.40 | 0.03 ± 0.00 / 0.30 | 0.14 ± 0.01 / 0.30 | 0.03 ± 0.00 / 0.30 | 0.11 ± 0.00 / 0.40 |
| Clementine | 0.30 ± 0.01 / 0.40 | 0.24 ± 0.01 / 0.40 | 0.19 ± 0.02 / 0.30 | 0.03 ± 0.00 / 0.30 | 0.80 ± 0.03 / 0.70 |
relief sizes learned (points per relieving tick): eat 35.22 ± 0.19, drink 18.97 ± 0.36, sleep 9.03 ± 0.16, play 17.98 ± 0.07, cuddle 17.59 ± 0.26

### R8c runs
SD-h8-s1: width 8 params 3279 (cap 8445) best 193/200 val 1.2492
SD-h8-s2: width 8 params 3279 (cap 8445) best 200/200 val 1.2576
SD-h8-s3: width 8 params 3279 (cap 8445) best 200/200 val 1.2395
SD-s1: width 16 params 6679 (cap 8445) best 157/167 val 1.0996
SD-s2: width 16 params 6679 (cap 8445) best 193/200 val 1.0847
SD-s3: width 16 params 6679 (cap 8445) best 198/200 val 1.0970
SD-h32-s1: width 32 params 15783 (cap 8445, OVER-CAP PROBE) best 196/200 val 1.0079
SD-h32-s2: width 32 params 15783 (cap 8445, OVER-CAP PROBE) best 167/177 val 1.0135
SD-h32-s3: width 32 params 15783 (cap 8445, OVER-CAP PROBE) best 123/133 val 1.0263

provenance: comparators NF-h24-s1, NF-h24-s2, NF-h24-s3, DR-h24-s1, DR-h24-s2, DR-h24-s3 re-read here equal /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase1b-2026-10-23/phase1b-read.json at width 24 on pooled mind-visible GRAVE mse5 + bias, NF and DR
