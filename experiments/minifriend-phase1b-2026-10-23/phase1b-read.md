## Phase 1b read (derived columns)

### R1b/R2b pooled mind-visible loss by width, group P (P1, P2, P3, P4, P5 eval worlds)
| head | class | w12 | w24 | w48 | r(12/24) | r(48/24) |
|---|---|---|---|---|---|---|
| NF | GRAVE | 1098.53 ± 48.58 | 908.10 ± 33.43 | 790.22 ± 38.88 | 1.210 ± 0.070 READ | 0.870 ± 0.053 READ |
| NF | DA | 937.96 ± 31.63 | 773.25 ± 20.58 | 670.72 ± 32.07 | 1.213 ± 0.052 READ | 0.867 ± 0.047 READ |
| NF | COMMON | 30.39 ± 1.26 | 25.34 ± 0.52 | 22.40 ± 0.31 | 1.199 ± 0.055 READ | 0.884 ± 0.022 READ |
| DR | GRAVE | 924.87 ± 139.56 | 827.69 ± 117.06 | 684.51 ± 33.26 | 1.117 ± 0.231 | 0.827 ± 0.124 READ |
| DR | DA | 813.01 ± 106.25 | 725.06 ± 97.39 | 597.56 ± 38.59 | 1.121 ± 0.210 | 0.824 ± 0.123 READ |
| DR | COMMON | 51.48 ± 7.58 | 40.15 ± 6.85 | 30.80 ± 3.88 | 1.282 ± 0.289 | 0.767 ± 0.163 READ |
coverage GRAVE mind-visible: Miso 572, Biscuit 364, Pumpkin 398, Kittybear 933, Clementine 260

#### group P: samples, worlds, coverage
n_samples 4000000; eval worlds [('P1', 1095452), ('P1', 1095454), ('P1', 1095455), ('P1', 1095456), ('P1', 1095460), ('P1', 1095461), ('P1', 1095462), ('P1', 1095468), ('P1', 1095469), ('P1', 1095470), ('P2', 1095472), ('P2', 1095473), ('P2', 1095475), ('P2', 1095477), ('P2', 1095479), ('P2', 1095480), ('P2', 1095481), ('P2', 1095483), ('P2', 1095487), ('P2', 1095490), ('P3', 1095493), ('P3', 1095495), ('P3', 1095496), ('P3', 1095497), ('P3', 1095499), ('P3', 1095500), ('P3', 1095503), ('P3', 1095506), ('P3', 1095509), ('P3', 1095510), ('P4', 1095515), ('P4', 1095516), ('P4', 1095520), ('P4', 1095524), ('P4', 1095525), ('P4', 1095526), ('P4', 1095527), ('P4', 1095528), ('P4', 1095529), ('P4', 1095530), ('P5', 1095533), ('P5', 1095534), ('P5', 1095536), ('P5', 1095537), ('P5', 1095540), ('P5', 1095541), ('P5', 1095542), ('P5', 1095546), ('P5', 1095547), ('P5', 1095548)]
coverage visible: GRAVE Miso 572, Biscuit 364, Pumpkin 398, Kittybear 933, Clementine 260; DA Miso 713, Biscuit 478, Pumpkin 672, Kittybear 1164, Clementine 489; COMMON Miso 382197, Biscuit 384426, Pumpkin 377340, Kittybear 379667, Clementine 399984
coverage all: GRAVE Miso 2440, Biscuit 1760, Pumpkin 2108, Kittybear 3224, Clementine 1972; DA Miso 2832, Biscuit 2184, Pumpkin 3076, Kittybear 4164, Clementine 2644; COMMON Miso 797168, Biscuit 797816, Pumpkin 796924, Kittybear 795836, Clementine 797356

#### R1b w12 visible: MSE on the five hidden needs per friend (mean ± SD over seeds)
| friend | NF COMMON | NF DA | NF GRAVE | DR COMMON | DR DA | DR GRAVE |
|---|---|---|---|---|---|---|
| Miso | 29.78 ± 1.96 | 693.62 ± 18.30 | 746.20 ± 29.91 | 49.43 ± 6.66 | 628.14 ± 156.71 | 648.84 ± 173.77 |
| Biscuit | 28.26 ± 1.17 | 1244.52 ± 79.59 | 1400.75 ± 107.04 | 49.20 ± 7.98 | 1019.41 ± 19.02 | 1096.65 ± 34.62 |
| Pumpkin | 31.69 ± 1.32 | 796.54 ± 30.84 | 914.71 ± 17.99 | 52.40 ± 8.12 | 672.09 ± 73.12 | 798.03 ± 113.26 |
| Kittybear | 26.26 ± 1.11 | 1174.61 ± 149.12 | 1343.05 ± 198.26 | 47.29 ± 7.92 | 970.73 ± 189.16 | 1081.74 ± 226.98 |
| Clementine | 35.69 ± 1.08 | 625.59 ± 45.35 | 854.43 ± 111.16 | 58.74 ± 7.32 | 699.02 ± 24.83 | 922.90 ± 28.28 |
| pooled | 30.39 ± 1.26 | 937.96 ± 31.63 | 1098.53 ± 48.58 | 51.48 ± 7.58 | 813.01 ± 106.25 | 924.87 ± 139.56 |

#### R1b w12 all: MSE on the five hidden needs per friend (mean ± SD over seeds)
| friend | NF COMMON | NF DA | NF GRAVE | DR COMMON | DR DA | DR GRAVE |
|---|---|---|---|---|---|---|
| Miso | 37.84 ± 1.70 | 871.88 ± 48.90 | 908.81 ± 54.13 | 64.60 ± 7.45 | 661.35 ± 173.44 | 655.00 ± 187.09 |
| Biscuit | 36.50 ± 1.08 | 987.78 ± 74.91 | 1071.63 ± 88.51 | 64.81 ± 9.02 | 766.31 ± 20.89 | 791.34 ± 27.96 |
| Pumpkin | 39.33 ± 0.99 | 799.68 ± 26.10 | 896.01 ± 53.34 | 67.55 ± 9.00 | 645.98 ± 43.22 | 686.20 ± 77.19 |
| Kittybear | 33.57 ± 0.89 | 1200.68 ± 33.50 | 1405.29 ± 44.54 | 63.62 ± 10.36 | 859.06 ± 165.25 | 957.46 ± 203.30 |
| Clementine | 44.02 ± 0.69 | 736.84 ± 60.90 | 864.85 ± 90.33 | 73.81 ± 7.83 | 693.56 ± 19.55 | 787.42 ± 14.92 |
| pooled | 38.25 ± 1.02 | 941.89 ± 35.57 | 1062.98 ± 43.33 | 66.88 ± 8.71 | 734.53 ± 93.34 | 789.04 ± 115.78 |

#### R3b w12: floor 924.87, NF pooled 1098.53, ratio 1.188, pooled_ok False, friends_ok False → dissolves False
| friend | NF grave | DR grave | excess over 1.10 × DR | NF SD | clause |
|---|---|---|---|---|---|
| Miso | 746.20 | 648.84 | +32.48 | 29.91 | EXCEEDS |
| Biscuit | 1400.75 | 1096.65 | +194.43 | 107.04 | EXCEEDS |
| Pumpkin | 914.71 | 798.03 | +36.89 | 17.99 | EXCEEDS |
| Kittybear | 1343.05 | 1081.74 | +153.14 | 198.26 | ok |
| Clementine | 854.43 | 922.90 | -160.76 | 111.16 | ok |

#### R4b w12 visible: bias (pred − true, need points) grave / common / gap, SIG = signature
| friend | NF | DR |
|---|---|---|
| Miso | -8.12 / -0.48 / -7.65 SIG | -1.85 / -0.22 / -1.63 SIG |
| Biscuit | -15.48 / +0.38 / -15.86 SIG | -8.60 / +0.46 / -9.06 SIG |
| Pumpkin | -9.60 / -0.35 / -9.25 SIG | -2.69 / -0.31 / -2.39 SIG |
| Kittybear | -20.91 / +0.72 / -21.63 SIG | -15.37 / +1.31 / -16.68 SIG |
| Clementine | -2.69 / -0.91 / -1.78 SIG | +3.69 / -0.82 / +4.51 |
| pooled | -13.58 / -0.14 / -13.44 SIG | -7.38 / +0.08 / -7.45 SIG |

#### R4b w12 all: bias (pred − true, need points) grave / common / gap, SIG = signature
| friend | NF | DR |
|---|---|---|
| Miso | -10.22 / -0.28 / -9.94 SIG | -3.82 / +0.20 / -4.02 SIG |
| Biscuit | -11.70 / +0.34 / -12.04 SIG | -4.42 / +0.71 / -5.13 SIG |
| Pumpkin | -8.23 / -0.37 / -7.86 SIG | -2.52 / -0.03 / -2.49 SIG |
| Kittybear | -21.02 / +0.78 / -21.81 SIG | -13.12 / +1.66 / -14.78 SIG |
| Clementine | -4.22 / -0.88 / -3.34 SIG | +2.39 / -0.60 / +2.99 |
| pooled | -12.08 / -0.08 / -12.00 SIG | -5.21 / +0.39 / -5.60 SIG |

#### R1b w24 visible: MSE on the five hidden needs per friend (mean ± SD over seeds)
| friend | NF COMMON | NF DA | NF GRAVE | DR COMMON | DR DA | DR GRAVE |
|---|---|---|---|---|---|---|
| Miso | 24.94 ± 0.65 | 591.45 ± 103.01 | 613.31 ± 78.46 | 38.41 ± 5.91 | 463.62 ± 78.62 | 480.05 ± 84.11 |
| Biscuit | 24.05 ± 0.81 | 1089.56 ± 10.04 | 1245.18 ± 19.55 | 37.71 ± 6.14 | 933.72 ± 57.87 | 1011.13 ± 66.77 |
| Pumpkin | 26.77 ± 0.71 | 617.52 ± 37.89 | 714.87 ± 22.05 | 41.41 ± 7.00 | 631.73 ± 51.23 | 697.68 ± 93.75 |
| Kittybear | 21.86 ± 0.44 | 940.47 ± 85.83 | 1081.52 ± 111.77 | 36.78 ± 7.08 | 898.86 ± 196.41 | 1021.69 ± 218.83 |
| Clementine | 28.93 ± 0.20 | 545.12 ± 26.74 | 758.16 ± 72.85 | 46.18 ± 8.13 | 616.86 ± 56.80 | 838.55 ± 49.32 |
| pooled | 25.34 ± 0.52 | 773.25 ± 20.58 | 908.10 ± 33.43 | 40.15 ± 6.85 | 725.06 ± 97.39 | 827.69 ± 117.06 |

#### R1b w24 all: MSE on the five hidden needs per friend (mean ± SD over seeds)
| friend | NF COMMON | NF DA | NF GRAVE | DR COMMON | DR DA | DR GRAVE |
|---|---|---|---|---|---|---|
| Miso | 33.29 ± 0.71 | 706.39 ± 82.97 | 716.65 ± 68.61 | 52.70 ± 7.17 | 510.38 ± 45.48 | 493.32 ± 46.92 |
| Biscuit | 32.33 ± 0.75 | 863.83 ± 39.64 | 938.45 ± 51.76 | 52.23 ± 7.54 | 744.25 ± 26.48 | 766.85 ± 26.66 |
| Pumpkin | 35.06 ± 0.64 | 683.48 ± 12.81 | 767.35 ± 4.97 | 55.61 ± 8.56 | 617.34 ± 40.94 | 633.30 ± 54.46 |
| Kittybear | 29.55 ± 0.42 | 982.94 ± 34.81 | 1149.32 ± 41.75 | 51.00 ± 9.47 | 818.38 ± 158.74 | 926.47 ± 180.10 |
| Clementine | 38.18 ± 0.22 | 667.50 ± 19.33 | 794.36 ± 26.17 | 60.83 ± 8.82 | 665.63 ± 33.94 | 770.40 ± 38.57 |
| pooled | 33.68 ± 0.54 | 795.12 ± 19.89 | 894.45 ± 21.77 | 54.48 ± 8.30 | 680.36 ± 59.05 | 729.70 ± 65.46 |

#### R3b w24: floor 827.69, NF pooled 908.10, ratio 1.097, pooled_ok True, friends_ok False → dissolves False
| friend | NF grave | DR grave | excess over 1.10 × DR | NF SD | clause |
|---|---|---|---|---|---|
| Miso | 613.31 | 480.05 | +85.26 | 78.46 | EXCEEDS |
| Biscuit | 1245.18 | 1011.13 | +132.94 | 19.55 | EXCEEDS |
| Pumpkin | 714.87 | 697.68 | -52.57 | 22.05 | ok |
| Kittybear | 1081.52 | 1021.69 | -42.35 | 111.77 | ok |
| Clementine | 758.16 | 838.55 | -164.25 | 72.85 | ok |

#### R4b w24 visible: bias (pred − true, need points) grave / common / gap, SIG = signature
| friend | NF | DR |
|---|---|---|
| Miso | -5.77 / -0.21 / -5.57 SIG | -3.59 / -0.21 / -3.38 SIG |
| Biscuit | -11.59 / +0.47 / -12.06 SIG | -8.22 / +0.55 / -8.77 SIG |
| Pumpkin | -6.83 / -0.10 / -6.73 SIG | -4.12 / -0.07 / -4.05 SIG |
| Kittybear | -17.01 / +0.65 / -17.66 SIG | -14.15 / +1.31 / -15.45 SIG |
| Clementine | +2.27 / -0.56 / +2.83 | +2.89 / -0.57 / +3.46 |
| pooled | -10.10 / +0.05 / -10.15 SIG | -7.57 / +0.19 / -7.77 SIG |

#### R4b w24 all: bias (pred − true, need points) grave / common / gap, SIG = signature
| friend | NF | DR |
|---|---|---|
| Miso | -7.72 / -0.09 / -7.62 SIG | -4.90 / +0.07 / -4.97 SIG |
| Biscuit | -7.83 / +0.43 / -8.25 SIG | -4.98 / +0.63 / -5.62 SIG |
| Pumpkin | -5.47 / -0.16 / -5.31 SIG | -4.22 / +0.01 / -4.23 SIG |
| Kittybear | -17.02 / +0.72 / -17.75 SIG | -13.12 / +1.49 / -14.60 SIG |
| Clementine | -0.35 / -0.62 / +0.27 | +2.04 / -0.47 / +2.51 |
| pooled | -8.67 / +0.05 / -8.72 SIG | -5.90 / +0.34 / -6.25 SIG |

#### R1b w48 visible: MSE on the five hidden needs per friend (mean ± SD over seeds)
| friend | NF COMMON | NF DA | NF GRAVE | DR COMMON | DR DA | DR GRAVE |
|---|---|---|---|---|---|---|
| Miso | 21.97 ± 0.66 | 484.84 ± 66.23 | 522.94 ± 74.78 | 29.28 ± 4.34 | 406.90 ± 60.84 | 423.88 ± 59.63 |
| Biscuit | 20.98 ± 0.24 | 854.74 ± 64.60 | 969.67 ± 82.02 | 29.58 ± 3.89 | 855.11 ± 67.95 | 933.20 ± 75.40 |
| Pumpkin | 23.58 ± 0.53 | 567.27 ± 36.63 | 674.19 ± 33.73 | 32.80 ± 3.70 | 506.08 ± 48.41 | 548.79 ± 44.87 |
| Kittybear | 19.36 ± 0.38 | 861.53 ± 37.22 | 983.31 ± 34.38 | 27.65 ± 3.41 | 706.84 ± 28.67 | 808.63 ± 45.43 |
| Clementine | 25.97 ± 0.13 | 449.82 ± 42.10 | 611.70 ± 67.88 | 34.53 ± 4.13 | 489.34 ± 70.35 | 672.07 ± 92.11 |
| pooled | 22.40 ± 0.31 | 670.72 ± 32.07 | 790.22 ± 38.88 | 30.80 ± 3.88 | 597.56 ± 38.59 | 684.51 ± 33.26 |

#### R1b w48 all: MSE on the five hidden needs per friend (mean ± SD over seeds)
| friend | NF COMMON | NF DA | NF GRAVE | DR COMMON | DR DA | DR GRAVE |
|---|---|---|---|---|---|---|
| Miso | 30.32 ± 0.44 | 616.38 ± 102.38 | 628.84 ± 115.01 | 41.58 ± 5.69 | 491.32 ± 73.19 | 469.22 ± 74.21 |
| Biscuit | 29.29 ± 0.44 | 723.20 ± 61.80 | 782.20 ± 73.69 | 41.71 ± 5.64 | 682.13 ± 63.87 | 699.91 ± 60.45 |
| Pumpkin | 32.03 ± 0.49 | 669.88 ± 29.41 | 764.55 ± 27.41 | 44.82 ± 5.53 | 537.88 ± 20.29 | 547.75 ± 13.60 |
| Kittybear | 26.98 ± 0.46 | 898.41 ± 76.88 | 1041.15 ± 89.81 | 39.13 ± 4.93 | 661.41 ± 48.36 | 752.94 ± 70.56 |
| Clementine | 35.02 ± 0.37 | 552.32 ± 17.27 | 653.75 ± 16.85 | 47.67 ± 5.96 | 575.09 ± 65.59 | 675.25 ± 72.10 |
| pooled | 30.73 ± 0.38 | 710.53 ± 50.49 | 796.99 ± 60.87 | 42.98 ± 5.54 | 591.30 ± 26.32 | 633.73 ± 23.24 |

#### R3b w48: floor 684.51, NF pooled 790.22, ratio 1.154, pooled_ok False, friends_ok False → dissolves False
| friend | NF grave | DR grave | excess over 1.10 × DR | NF SD | clause |
|---|---|---|---|---|---|
| Miso | 522.94 | 423.88 | +56.67 | 74.78 | ok |
| Biscuit | 969.67 | 933.20 | -56.85 | 82.02 | ok |
| Pumpkin | 674.19 | 548.79 | +70.52 | 33.73 | EXCEEDS |
| Kittybear | 983.31 | 808.63 | +93.82 | 34.38 | EXCEEDS |
| Clementine | 611.70 | 672.07 | -127.57 | 67.88 | ok |

#### R4b w48 visible: bias (pred − true, need points) grave / common / gap, SIG = signature
| friend | NF | DR |
|---|---|---|
| Miso | -7.00 / -0.39 / -6.61 SIG | -2.84 / -0.27 / -2.57 SIG |
| Biscuit | -9.44 / +0.13 / -9.57 SIG | -8.49 / +0.48 / -8.97 SIG |
| Pumpkin | -6.92 / -0.16 / -6.76 SIG | -4.58 / -0.17 / -4.42 SIG |
| Kittybear | -16.08 / +0.26 / -16.35 SIG | -10.25 / +0.83 / -11.08 SIG |
| Clementine | +2.89 / -0.54 / +3.44 | +3.06 / -0.57 / +3.62 |
| pooled | -9.68 / -0.15 / -9.53 SIG | -6.06 / +0.06 / -6.11 SIG |

#### R4b w48 all: bias (pred − true, need points) grave / common / gap, SIG = signature
| friend | NF | DR |
|---|---|---|
| Miso | -9.05 / -0.27 / -8.78 SIG | -4.11 / -0.05 / -4.06 SIG |
| Biscuit | -8.01 / +0.11 / -8.12 SIG | -4.09 / +0.53 / -4.62 SIG |
| Pumpkin | -7.86 / -0.20 / -7.67 SIG | -4.31 / -0.13 / -4.18 SIG |
| Kittybear | -16.24 / +0.34 / -16.57 SIG | -10.00 / +0.96 / -10.96 SIG |
| Clementine | +0.52 / -0.56 / +1.08 | +3.85 / -0.54 / +4.40 |
| pooled | -9.05 / -0.12 / -8.93 SIG | -4.43 / +0.15 / -4.58 SIG |

#### R1b baselines on group P (pooled, mind-visible / all-states; training-split statistics, width-independent)
COMMON: marginal 75.10 / 78.84; proxy 72.67 / 77.59
DA: marginal 2751.25 / 2995.87; proxy 2749.84 / 2978.35
GRAVE: marginal 3264.16 / 3422.93; proxy 3261.15 / 3402.49

### R1b/R2b pooled mind-visible loss by width, group G (G eval worlds)
| head | class | w12 | w24 | w48 | r(12/24) | r(48/24) |
|---|---|---|---|---|---|---|
| NF | GRAVE | 814.28 ± 60.14 | 591.58 ± 20.73 | 528.31 ± 35.21 | 1.376 ± 0.113 READ | 0.893 ± 0.067 READ |
| NF | DA | 750.00 ± 50.30 | 559.51 ± 7.14 | 497.29 ± 33.09 | 1.340 ± 0.092 READ | 0.889 ± 0.060 READ |
| NF | COMMON | 32.24 ± 1.55 | 26.79 ± 0.60 | 23.78 ± 0.41 | 1.204 ± 0.064 READ | 0.888 ± 0.025 READ |
| DR | GRAVE | 663.61 ± 98.63 | 580.94 ± 17.77 | 529.91 ± 29.13 | 1.142 ± 0.173 | 0.912 ± 0.057 READ |
| DR | DA | 632.47 ± 93.17 | 541.68 ± 32.62 | 486.85 ± 32.93 | 1.168 ± 0.186 | 0.899 ± 0.081 READ |
| DR | COMMON | 53.36 ± 6.82 | 42.40 ± 5.87 | 33.04 ± 4.11 | 1.259 ± 0.237 READ | 0.779 ± 0.145 READ |
coverage GRAVE mind-visible: Miso 506, Biscuit 734, Pumpkin 166, Kittybear 638, Clementine 284

### R5b GRAVE loss, G over P (mind-visible)
w12: NF 0.741 ± 0.064 READ, DR 0.718 ± 0.152 READ
w24: NF 0.651 ± 0.033 READ, DR 0.702 ± 0.102 READ
w48: NF 0.669 ± 0.055 READ, DR 0.774 ± 0.057 READ

### R6b runs
w12: NF-h12-s1 params 3043 best 63/73; NF-h12-s2 params 3043 best 68/78; NF-h12-s3 params 3043 best 72/82; DR-h12-s1 params 3043 best 39/49; DR-h12-s2 params 3043 best 22/32; DR-h12-s3 params 3043 best 23/33
w24: NF-h24-s1 params 7807 best 59/69; NF-h24-s2 params 7807 best 68/78; NF-h24-s3 params 7807 best 65/75; DR-h24-s1 params 7807 best 39/49; DR-h24-s2 params 7807 best 22/32; DR-h24-s3 params 7807 best 21/31
w48: NF-h48-s1 params 22519 best 52/62; NF-h48-s2 params 22519 best 54/64; NF-h48-s3 params 22519 best 57/67; DR-h48-s1 params 22519 best 53/63; DR-h48-s2 params 22519 best 22/32; DR-h48-s3 params 22519 best 40/50
