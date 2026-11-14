# The needs trigger's read on the needs-only arm (p2-needs-s1: every probe, and its recorded legs)

Grave bias = the head's estimate minus the friend's true hidden need, in need points, on GRAVE rows; negative = a grave friend read less needy than she is (the optimism direction). SIGNATURE = grave bias negative and at least 1.5× the common bias in size, at 200 rows or more in both strata. The read is logged, never a stop (shape (ii)).

| leg | version | grave rows | grave bias (SD) | common bias | state |
|---|---|---|---|---|---|
| 20×20 | visible | 840 | +8.02 (9.79) | +0.87 | CLEAR |
| 20×20 | all | 2,692 | +9.43 (10.28) | +1.71 | CLEAR |
| 40×40 | visible | 1,958 | +3.46 (8.83) | -0.41 | CLEAR |
| 40×40 | all | 38,244 | +10.48 (8.40) | +0.77 | CLEAR |

Not read: 100×100.

| probes | version | cumulative state INSUFFICIENT / CLEAR / SIGNATURE (probes) | first sufficient update | last probe: grave rows, grave bias, state |
|---|---|---|---|---|
| 78 | visible | 48 / 30 / 0 | 2449 | 379, +14.19, CLEAR |
| 78 | all | 37 / 30 / 11 | 1899 | 2,328, +8.37, CLEAR |

Probes at which the cumulative read fired (updates): [1899, 1949, 1999, 2049, 2099, 2149, 2199, 2249, 2299, 2349, 2399].

**N4 MET on the legs read** (fires: {'20': False, '40': False}).
