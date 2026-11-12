# R-4 — cells-in-use by world size (Phase 2's recorded uniform legs; 30 worlds a leg)

Changed share = decision rows whose greedy act changes when the appended cells are zeroed. Paired Δ = the arm's team happiness minus the same-seed no-head leg's, per world; terciles = the leg's worlds ranked by their changed share.

| leg | changed share, all rows | changed share, free-choice rows | free-choice share of rows | paired Δ vs no-head | Δ bottom tercile | Δ mid | Δ top tercile | Spearman share~Δ | ties | aborted |
|---|---|---|---|---|---|---|---|---|---|---|
| p2u-act15-s1-20 | 0.0664 | 0.1184 | 0.561 | -0.225 | -0.215 | -0.185 | -0.274 | -0.007 | 1 | — |
| p2u-act15-s1-40 | 0.0573 | 0.0948 | 0.604 | -0.353 | -0.383 | -0.356 | -0.320 | +0.263 | 0 | — |
| p2u-act15-s1-100 | 0.0487 | 0.0750 | 0.649 | -0.387 | -0.389 | -0.259 | -0.513 | -0.110 | 0 | [905009] |
| p2u-act15-s2-20 | 0.0573 | 0.1003 | 0.571 | -0.401 | -0.405 | -0.411 | -0.386 | +0.077 | 0 | — |
| p2u-act15-s2-40 | 0.0524 | 0.0851 | 0.615 | -0.727 | -0.701 | -0.739 | -0.740 | -0.088 | 0 | — |
| p2u-act15-s4-20 | 0.0689 | 0.1259 | 0.548 | -0.143 | -0.204 | -0.096 | -0.129 | +0.364 | 0 | — |
| p2u-act15-s4-40 | 0.0618 | 0.1044 | 0.592 | -0.215 | -0.200 | -0.264 | -0.180 | +0.257 | 0 | — |
| p2u-both-s1-20 | 0.0796 | 0.1425 | 0.559 | +0.008 | +0.020 | +0.011 | -0.007 | -0.148 | 0 | — |
| p2u-both-s1-40 | 0.0683 | 0.1136 | 0.601 | +0.026 | +0.026 | +0.045 | +0.006 | -0.108 | 0 | — |
| p2u-both-s1-100 | 0.0625 | 0.0975 | 0.641 | +0.203 | +0.270 | +0.328 | +0.011 | -0.362 | 0 | [905009, 905014, 905019] |

**P53 NOT MET.** Share rises with size: {'s1 40>20': False, 's2 40>20': False, 's4 40>20': False, 's1 100>40': False} (half a not met); top-tercile Δ below bottom-tercile Δ at 40×40: {'s1': False, 's2': True, 's4': False} (half b not met).

No-head fence (0 changed rows): fence-p2u-nohead-s1-100 (2 worlds, 200000 rows), fence-p2u-nohead-s1-20 (2 worlds, 200000 rows), fence-p2u-nohead-s1-40 (2 worlds, 200000 rows), fence-p2u-nohead-s2-20 (2 worlds, 200000 rows), fence-p2u-nohead-s2-40 (2 worlds, 200000 rows), fence-p2u-nohead-s4-20 (2 worlds, 200000 rows), fence-p2u-nohead-s4-40 (2 worlds, 200000 rows).
