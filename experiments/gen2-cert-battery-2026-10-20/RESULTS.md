# Gen 2 cert battery — step 8 results (2026-10-20)

Declaration: `DECLARATION.md` (committed before data). Departure:
`../gen2-deviations.md` entry 4 (seating-level abort stop not
enforced; OPEN, owner-routed). Rows the declared stop would have
prevented are marked POST-STOP and are not gate evidence until she
rules.

## Gate read (paired by seed vs the vision-law comparator, 30 × 20k)

| seating | size | trained | paired Δ | seeds + | Δ range | worst streak mean / max | aborts | verdict |
|---|---|---|---|---|---|---|---|---|
| g2-s1 | 20 | 87.314 | +5.393 | 30/30 | [4.573, 6.837] | 6.5 / 77 | 0 | PASS |
| g2-s1 | 40 | 86.142 | +4.507 | 30/30 | [3.760, 5.626] | 23.9 / 219 | 0 | PASS |
| g2-s1 | 100 | 83.889 | +7.266 | 30/30 | [3.240, 10.301] | 125.3 / 467 | 0 | characterize |
| g2-s2 | 20 | 87.257 | +5.336 | 30/30 | [3.818, 7.037] | 66.9 / 1000 | 1 | PASS (F-053 event) |
| g2-s2 | 40 | 86.012 | +4.378 | 30/30 | [3.645, 5.446] | 19.5 / 120 | 0 | POST-STOP |
| g2-s2 | 100 | 82.800 | +6.176 | 29/30 | [−1.626, 9.861] | 377.3 / 1000 | 5 | POST-STOP |
| g2-s4 | 20 | 87.746 | +5.826 | 30/30 | [5.020, 7.355] | 19.6 / 535 | 0 | PASS |
| g2-s4 | 40 | 86.499 | +4.865 | 30/30 | [4.182, 5.901] | 70.8 / 687 | 0 | PASS |
| g2-s4 | 100 | 83.800 | +7.177 | 30/30 | [2.926, 10.520] | 641.2 / 1000 | 11 | characterize (post-stop after 1st abort) |

Comparator (prereg §7 pins): 20×20 81.921, streak 178/401; 40×40
81.634, 197/626; 100×100 76.623, 443/716; zero F-053 events at
every size.

Reading. On happiness, the trunk beats the scripted teacher roster
at every size, in every seed at the gated sizes (+4.4 to +5.8 at
20/40). The welfare tail is the open question, and it does not
follow happiness. s1 is the only seating that is fully in-protocol
and tail-clean: zero aborts at any size, gated worst streaks 77 and
219, both under the comparator's maxima. s2 reached the F-053 line
once at the served 20×20 (seed 905008, tick 18949), which is the
seating's declared stop. s4 is clean at the gated sizes but
reached the line in 11 of 30 worlds at 100×100. Four of those
aborts land at tick 1128 or 1224 across different seeds; that
repeat is noted and not investigated. Dispersion columns are in the
raws and not yet read.

## Read (gate; seconds; stdlib python3, repo root)

```
cd experiments/gen2-cert-battery-2026-10-20 && python3 -B gate_read.py --out gate-read.json
```
