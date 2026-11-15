# Re-anchor scout: R-A and R-B

Missing: none.

## R-A the step (training bins)

Trunk seed 1's last bin: return 0.8802.

| run | bin 1 return | bin 1 KL to its anchor | bin 2 return | bin 2 KL | step over the trunk's last bin |
|---|---|---|---|---|---|
| reanchor | 0.8931 | 0.2366 | 0.8956 | 0.2809 | +0.0129 |
| cont | 0.8814 | 0.5365 | 0.8820 | 0.5461 | +0.0011 |
| nohead | 0.8914 | 0.2062 | 0.8940 | 0.2979 | +0.0112 |

## R-B welfare (30 worlds × 20k ticks, paired by world)

| leg | team happiness | vs trunk s1 (mean, worlds up) | worlds with a 300+ streak | worst streak | aborts |
|---|---|---|---|---|---|
| reanchor@20 | 89.043 | +1.729, 30/30 | 0 | 106 | none |
| reanchor@40 | 87.983 | +1.841, 30/30 | 0 | 150 | none |
| cont_10M@40 | 86.281 | +0.139, 27/30 | 0 | 86 | none |
| nohead_2M@40 | 87.819 | +1.678, 30/30 | 8 | 897 | none |

reanchor@40 vs cont 10M: +1.702, 30/30 worlds up.

reanchor@40 vs nohead 2M: +0.163, 30/30 worlds up.

## Predictions and grammar

- A1: MET (step +0.0129, kl_first_bin +0.2366)
- A2: MET (positive 30, mean_vs_trunk +1.8411, mean_vs_cont_10M +1.7016)
- A3: MET (arm_vs_trunk +1.8411, nohead_2M_vs_trunk +1.6777)
- §8: **A1 and A2 met: the anchor alone is sufficient on this seed**
