# Phase 1e read: confirming

### NF1e-h24+p on the confirming half

| cell | T-H0 det | E-H1 det | N-H2 det | N-H3 det | N-H4 det | N-H2 antic | N-H3 antic | N-H4 antic | FA covered N /10k | FA scripted-from-mask N /10k |
|---|---|---|---|---|---|---|---|---|---|---|
| t0.05-B2 | 1.000 ± 0.000 | 0.786 ± 0.082 | 0.920 ± 0.006 | 0.880 ± 0.006 | 0.863 ± 0.000 | 0.843 ± 0.053 | 0.871 ± 0.030 | 0.892 ± 0.014 | 2.4002 ± 1.0702 | 5.3708 ± 2.0587 |
| t0.10-B0 | 1.000 ± 0.000 | 0.717 ± 0.071 | 0.897 ± 0.011 | 0.832 ± 0.017 | 0.783 ± 0.038 | 0.766 ± 0.040 | 0.796 ± 0.037 | 0.817 ± 0.040 | 1.8635 ± 0.8257 | 4.2376 ± 1.4270 |

### the frozen NF-h24+p on the confirming half (same reader)

| cell | T-H0 det | E-H1 det | N-H2 det | N-H3 det | N-H4 det | N-H2 antic | N-H3 antic | N-H4 antic | FA covered N /10k | FA scripted-from-mask N /10k |
|---|---|---|---|---|---|---|---|---|---|---|
| t0.05-B2 | 1.000 ± 0.000 | 0.489 ± 0.022 | 0.596 ± 0.092 | 0.444 ± 0.110 | 0.421 ± 0.134 | 0.253 ± 0.059 | 0.211 ± 0.077 | 0.275 ± 0.108 | 0.6308 ± 0.2269 | 1.4714 ± 0.6489 |
| t0.10-B0 | 1.000 ± 0.000 | 0.409 ± 0.025 | 0.526 ± 0.081 | 0.392 ± 0.094 | 0.383 ± 0.135 | 0.199 ± 0.087 | 0.152 ± 0.075 | 0.167 ± 0.076 | 1.4783 ± 0.9831 | 1.0901 ± 0.4363 |

### the price, retrained head (arm N, confirming half)

| cell | class | false runs per 10k observer-ticks | mean run length | observer-ticks under a false alarm per 10k | false runs per observer per 1,000 ticks |
|---|---|---|---|---|---|
| t0.05-B2 | scripted_before_first_mask | 0.7223 | 4.3 | 3.1 | 0.0722 |
| t0.05-B2 | scripted_from_first_mask | 5.3708 | 16.6 | 89.0 | 0.5371 |
| t0.05-B2 | covered_friends | 2.4002 | 17.8 | 42.7 | 0.7201 |
| t0.10-B0 | scripted_before_first_mask | 0.2213 | 2.5 | 0.6 | 0.0221 |
| t0.10-B0 | scripted_from_first_mask | 4.2376 | 14.2 | 60.0 | 0.4238 |
| t0.10-B0 | covered_friends | 1.8635 | 15.8 | 29.4 | 0.5590 |

### the price, frozen probe (arm N, confirming half)

| cell | class | false runs per 10k observer-ticks | mean run length | observer-ticks under a false alarm per 10k | false runs per observer per 1,000 ticks |
|---|---|---|---|---|---|
| t0.05-B2 | scripted_before_first_mask | 0.3844 | 4.6 | 1.8 | 0.0384 |
| t0.05-B2 | scripted_from_first_mask | 1.4714 | 10.5 | 15.4 | 0.1471 |
| t0.05-B2 | covered_friends | 0.6308 | 12.9 | 8.1 | 0.1892 |
| t0.10-B0 | scripted_before_first_mask | 10.1350 | 1.0 | 10.5 | 1.0135 |
| t0.10-B0 | scripted_from_first_mask | 1.0901 | 9.0 | 9.8 | 0.1090 |
| t0.10-B0 | covered_friends | 1.4783 | 4.7 | 7.0 | 0.4435 |

S = t0.05-B2 (reads/S.json)

```
{
 "S": "t0.05-B2",
 "frozen_pick": {
  "T-H0": 1.0,
  "E-H1": 0.4891,
  "N-H2": 0.5962,
  "N-H3": 0.444,
  "N-H4": 0.4208
 },
 "P16": {
  "detected_S": {
   "N-H2": 0.9199,
   "N-H3": 0.8802,
   "N-H4": 0.8625
  },
  "detected_frozen_pick": {
   "N-H2": 0.5962,
   "N-H3": 0.444,
   "N-H4": 0.4208
  },
  "gain": {
   "N-H2": 0.3237000000000001,
   "N-H3": 0.4362,
   "N-H4": 0.44170000000000004
  },
  "mean_gain": 0.40053333333333335,
  "clause_1_each_above": true,
  "clause_2_mean_gain": true,
  "met": true
 },
 "P17": {
  "E-H1_S": 0.7862,
  "E-H1_frozen_pick": 0.4891,
  "T-H0_S": 1.0,
  "met": true
 },
 "false_runs_covered_N": {
  "new_S": 2.4002,
  "frozen_pick": 0.6308,
  "new_pick": 2.4002,
  "ratio_new_S_over_frozen_pick": 3.805009511731135
 }
}
```
