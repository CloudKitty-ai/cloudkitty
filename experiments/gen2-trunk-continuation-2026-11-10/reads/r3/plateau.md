# R-3 — the plateau-rule replay on every recorded bin series

Cell = the bin the rule would have stopped the series at (return left on the table: the last recorded bin's return minus the return at that stop); — = the rule does not fire inside the recorded series.

| series | bins | recorded stop (ticks, reason) | frozen | ret0.002x3 | ret0.001x3 | ret0.005x5 | return-only | slope2 |
|---|---|---|---|---|---|---|---|---|
| ppo-g2-trunk-s1 | 8 | 8,002,560, plateau | bin 8 (+0.0000) | bin 8 (+0.0000) | — | — | bin 8 (+0.0000) | bin 7 (+0.0014) |
| ppo-g2-trunk-s2 | 8 | 8,002,560, plateau | bin 8 (+0.0000) | — | — | — | bin 8 (+0.0000) | bin 7 (+0.0024) |
| ppo-g2-trunk-s3 | 0 | 768,000, probe-distress-stop | — | — | — | — | — | — |
| ppo-g2-trunk-s4 | 8 | 8,002,560, plateau | bin 8 (+0.0000) | — | — | — | bin 8 (+0.0000) | bin 7 (+0.0006) |
| ppo-g2-trunk-s5 | 0 | 614,400, probe-distress-stop | — | — | — | — | — | — |
| ppo-g2-trunk-s6 | 8 | 8,002,560, plateau | bin 8 (+0.0000) | — | — | — | bin 8 (+0.0000) | bin 7 (+0.0031) |
| ppo-g2-trunk-s7 | 9 | 9,000,960, plateau | bin 9 (+0.0000) | — | — | — | bin 8 (-0.0001) | bin 8 (-0.0001) |
| ppo-g2-trunk-s8 | 0 | 921,600, probe-distress-stop | — | — | — | — | — | — |
| ppo-g2-trunk-s9 | 8 | 8,002,560, plateau | bin 8 (+0.0000) | bin 8 (+0.0000) | — | — | bin 8 (+0.0000) | bin 7 (+0.0019) |
| ppo-g2-trunk-s10 | 8 | 8,002,560, plateau | bin 8 (+0.0000) | — | — | — | bin 8 (+0.0000) | bin 8 (+0.0000) |
| ppo-g2-trunk-s11 | 0 | 307,200, probe-distress-stop | — | — | — | — | — | — |
| p2-act10-s1 | 10 | 10,752,000, probe-distress-stop | — | — | — | — | — | — |
| p2-act10-s1r | 12 | 12,002,304, plateau | bin 12 (+0.0000) | — | — | — | bin 12 (+0.0000) | bin 12 (+0.0000) |
| p2-act10-s2 | 3 | 3,532,800, probe-distress-stop | — | — | — | — | — | — |
| p2-act10-s4 | 10 | 10,291,200, f053-line-crossed | — | — | — | — | — | — |
| p2-act15-s1 | 13 | 13,000,704, plateau | bin 13 (+0.0000) | bin 13 (+0.0000) | — | — | bin 12 (+0.0001) | bin 12 (+0.0001) |
| p2-act15-s2 | 12 | 12,002,304, plateau | bin 12 (+0.0000) | — | — | — | bin 12 (+0.0000) | bin 11 (+0.0022) |
| p2-act15-s4 | 12 | 12,002,304, plateau | bin 12 (+0.0000) | — | — | — | bin 12 (+0.0000) | bin 11 (-0.0007) |
| p2-both-s1 | 12 | 12,002,304, plateau | bin 12 (+0.0000) | bin 12 (+0.0000) | bin 12 (+0.0000) | — | bin 12 (+0.0000) | bin 11 (+0.0010) |
| p2-nohead-s1 | 1 | 1,228,800, probe-distress-stop | — | — | — | — | — | — |
| p2-nohead-s1r | 15 | 15,000,576, plateau | bin 15 (+0.0000) | — | — | — | bin 12 (+0.0012) | bin 11 (+0.0054) |
| p2-nohead-s2 | 15 | 15,000,576, plateau | bin 15 (+0.0000) | bin 15 (+0.0000) | bin 15 (+0.0000) | — | bin 12 (-0.0018) | bin 11 (+0.0009) |
| p2-nohead-s4 | 12 | 12,002,304, plateau | bin 12 (+0.0000) | bin 12 (+0.0000) | — | — | bin 12 (+0.0000) | bin 11 (-0.0017) |
| cont-s1 | 19 | 19,998,720, cap | bin 11 (-0.0002) | bin 11 (-0.0002) | bin 12 (+0.0015) | bin 13 (+0.0063) | bin 11 (-0.0002) | bin 10 (-0.0001) |
| cont-s2 | 19 | 19,998,720, cap | bin 11 (-0.0002) | bin 11 (-0.0002) | bin 16 (+0.0029) | bin 13 (-0.0028) | bin 11 (-0.0002) | bin 10 (+0.0003) |
| cont-s4 | 19 | 19,998,720, cap | bin 11 (+0.0045) | — | — | bin 13 (+0.0032) | bin 11 (+0.0045) | bin 10 (+0.0068) |

Series ended by the plateau rule: 15 of 26. Per rule, over those 15: frozen stops 15 at the recorded bin, 0 earlier, 0 not inside the record; ret0.002x3 stops 6 at the recorded bin, 0 earlier, 9 not inside the record; ret0.001x3 stops 2 at the recorded bin, 0 earlier, 13 not inside the record; ret0.005x5 stops 0 at the recorded bin, 0 earlier, 15 not inside the record; return-only stops 11 at the recorded bin, 4 earlier, 0 not inside the record; slope2 stops 2 at the recorded bin, 13 earlier, 0 not inside the record.

P52, first clause (the frozen rule's flags on the first three bins closing after §4's declared floor; all flat = a stop at lineage bin 19): cont-s1 bins [17, 18, 19] flat [True, True, True]; cont-s2 bins [17, 18, 19] flat [True, True, True]; cont-s4 bins [17, 18, 19] flat [True, True, True] — 3 of 3 would have stopped at bin 19.
