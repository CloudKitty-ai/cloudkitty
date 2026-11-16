# The re-anchor arm, seeds 2 and 4 (deviations entry 41)

Prior: seed 1: REPLICATES, A3 met (reads/reanchor.md; RESULTS.md, gated).

## Seed 2: **REPLICATES** (A3 MET)

Run reached the declared end: True. Missing: none.

Trunk seed 2's last bin: return 0.8789.

| run | bin 1 return | bin 1 KL to its anchor | bin 2 return | bin 2 KL | step over the trunk's last bin |
|---|---|---|---|---|---|
| reanchor | 0.8911 | 0.2479 | 0.8941 | 0.2972 | +0.0122 |
| cont | 0.8758 | 0.5037 | 0.8773 | 0.5212 | -0.0031 |
| nohead | 0.8901 | 0.2106 | 0.8930 | 0.3006 | +0.0112 |

| leg | team happiness | vs trunk (mean; worlds up of worlds in the mean; arm worlds aborted; unpaired) | worlds with a 300+ streak | worst streak | aborts |
|---|---|---|---|---|---|
| reanchor@20 | 89.338 | +1.997; 29/29; 0; 1 | 0 | 0 | none |
| reanchor@40 | 88.346 | +2.334; 30/30; 0; 0 | 1 | 398 | none |
| nohead_2M@40 | 88.112 | +2.100; 30/30; 0; 0 | 0 | 281 | none |

reanchor@20 vs cont final: +2.098, 30/30 worlds up.

reanchor@40 vs nohead 2M: +0.234, 29/30 worlds up.

Predictions:

- A1: MET (step +0.0122, kl_first_bin +0.2479)
- A3: MET (arm_vs_trunk +2.3344, nohead_2M_vs_trunk +2.1000)
- A2: MET (positive 30, mean_vs_trunk +2.3344, worlds 30, arm_aborted 0)

## Seed 4: **REPLICATES** (A3 MET)

Run reached the declared end: True. Missing: none.

Trunk seed 4's last bin: return 0.8803.

| run | bin 1 return | bin 1 KL to its anchor | bin 2 return | bin 2 KL | step over the trunk's last bin |
|---|---|---|---|---|---|
| reanchor | 0.8966 | 0.2465 | 0.9013 | 0.3135 | +0.0162 |
| cont | 0.8826 | 0.5491 | 0.8796 | 0.5265 | +0.0023 |
| nohead | 0.8957 | 0.2024 | 0.8990 | 0.3152 | +0.0153 |

| leg | team happiness | vs trunk (mean; worlds up of worlds in the mean; arm worlds aborted; unpaired) | worlds with a 300+ streak | worst streak | aborts |
|---|---|---|---|---|---|
| reanchor@20 | 89.974 | +2.227; 30/30; 0; 0 | 1 | 503 | none |
| reanchor@40 | 88.418 | +2.093; 28/28; 2; 0 | 24 | 1000 | 905004: 3913, 905010: 1128 |
| nohead_2M@40 | 89.018 | +2.519; 30/30; 0; 0 | 9 | 719 | none |

reanchor@20 vs cont final: +1.964, 30/30 worlds up.

reanchor@40 vs nohead 2M: -0.426, 0/28 worlds up.

Predictions:

- A1: MET (step +0.0162, kl_first_bin +0.2465)
- A3: MET (arm_vs_trunk +2.0926, nohead_2M_vs_trunk +2.5191)
- A2: MET (positive 28, mean_vs_trunk +2.0926, worlds 28, arm_aborted 2)

## Across seeds: **both replicate: the anchor alone is sufficient on three of three trunk seeds**
