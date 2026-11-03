# Phase 1e read: score

```
{
 "S": "t0.05-B2",
 "S_source": "reads/S.json",
 "tuning_selection": {
  "bound": {
   "fa_cov": 0.7077,
   "fa_scr": 1.4965
  },
  "candidates": [],
  "chosen": null
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
 "P18": {
  "H100_detected": 0.5983,
  "H100_bar_exclusive": 0.358,
  "H0_detected": 0.9883,
  "H0_min": 0.95,
  "control_fired_from_H2": {
   "2": 0.0,
   "5": 0.0,
   "10": 0.0,
   "20": 0.0,
   "50": 0.0017,
   "100": 0.0133,
   "500": 0.0017,
   "2000": 0.0
  },
  "control_max": 0.05,
  "clause_H100": true,
  "clause_H0": true,
  "clause_control": true,
  "met": true
 },
 "P19": {
  "groups": {
   "P": {
    "new_S": 0.2433,
    "frozen_pick": 0.2575,
    "ratio": 0.9448543689320388
   },
   "LWG": {
    "new_S": 0.8762,
    "frozen_pick": 0.5464,
    "ratio": 1.6035871156661785
   }
  },
  "ratio_max": 2.0,
  "met": true,
  "reset_detected_P": {
   "new_S": 0.9883,
   "frozen_pick": 0.985
  }
 },
 "P20": {
  "P_visible_GRAVE_mse5_ratio": 0.8455293353539727,
  "LWG_visible_COMMON_mse5_ratio": 1.0228501810293467,
  "ratio_max": 1.1,
  "P_visible_GRAVE_mse5": {
   "new": {
    "mean": 767.8213,
    "sd": 60.3842,
    "n_seeds": 3
   },
   "frozen": {
    "mean": 908.0954,
    "sd": 33.4288,
    "n_seeds": 3
   }
  },
  "met": true
 },
 "met": {
  "P16": true,
  "P17": true,
  "P18": true,
  "P19": true,
  "P20": true
 }
}
```
