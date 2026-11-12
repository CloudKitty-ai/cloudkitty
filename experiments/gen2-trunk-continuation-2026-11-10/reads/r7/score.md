# R-7 — the block read on the dual-head arm (p2u-both-s1's recorded uniform legs; 30 worlds a leg)

Share = decision rows whose greedy act changes when the block's cells are zeroed (zero) or permuted across the seat's own ticks (perm). Blocks: act = the B15 head's 13 cells a friend row; needs = the needs head's seven estimates + P(grave); tsl = the time-since-live cell; all = every appended cell (R-4's read). Flagged = rows where some friend row's P(grave) cell is at least 0.5; under 200 flagged rows a leg reads INSUFFICIENT.

| size | mode | block | all rows | free-choice rows | flagged rows | unflagged rows |
|---|---|---|---|---|---|---|
| 20×20 | zero | act | 0.0613 | 0.1096 | 0.0733 | 0.0613 |
| 20×20 | zero | needs | 0.0325 | 0.0582 | 0.0572 | 0.0325 |
| 20×20 | zero | tsl | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 20×20 | zero | all | 0.0796 | 0.1425 | 0.0817 | 0.0796 |
| 20×20 | perm | act | 0.0459 | 0.0822 | 0.0580 | 0.0459 |
| 20×20 | perm | needs | 0.0162 | 0.0289 | 0.0534 | 0.0161 |
| 20×20 | perm | tsl | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 20×20 | perm | all | 0.0491 | 0.0879 | 0.0775 | 0.0491 |
| 40×40 | zero | act | 0.0539 | 0.0896 | 0.0556 | 0.0539 |
| 40×40 | zero | needs | 0.0273 | 0.0455 | 0.0628 | 0.0272 |
| 40×40 | zero | tsl | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 40×40 | zero | all | 0.0683 | 0.1136 | 0.0901 | 0.0682 |
| 40×40 | perm | act | 0.0393 | 0.0653 | 0.0428 | 0.0392 |
| 40×40 | perm | needs | 0.0159 | 0.0265 | 0.0537 | 0.0158 |
| 40×40 | perm | tsl | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 40×40 | perm | all | 0.0432 | 0.0718 | 0.0711 | 0.0431 |
| 100×100 | zero | act | 0.0473 | 0.0739 | 0.0467 | 0.0474 |
| 100×100 | zero | needs | 0.0289 | 0.0451 | 0.0604 | 0.0271 |
| 100×100 | zero | tsl | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 100×100 | zero | all | 0.0625 | 0.0975 | 0.0835 | 0.0613 |
| 100×100 | perm | act | 0.0381 | 0.0594 | 0.0378 | 0.0381 |
| 100×100 | perm | needs | 0.0243 | 0.0379 | 0.0533 | 0.0227 |
| 100×100 | perm | tsl | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 100×100 | perm | all | 0.0478 | 0.0745 | 0.0679 | 0.0466 |

| size | rows | free-choice rows | flagged rows | ties | both − act15 paired Δ | Δ bottom tercile of needs share | Δ mid | Δ top | Spearman needs share ~ Δ | same, aborted worlds out | flagged share ~ Δ | needs share ~ flagged share | flagged share ~ team happiness, both / act15 | aborted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20×20 | 3,000,000 | 1,676,604 | 2,361 | 0 | +0.233 | +0.233 | +0.230 | +0.236 | -0.203 | -0.203 | +0.253 | -0.154 | +0.238 / +0.055 | — |
| 40×40 | 3,000,000 | 1,803,535 | 12,708 | 0 | +0.379 | +0.380 | +0.387 | +0.370 | +0.000 | +0.000 | -0.261 | +0.269 | -0.300 / +0.149 | — |
| 100×100 | 2,896,345 | 1,856,701 | 155,623 | 0 | +0.591 | +0.776 | +0.626 | +0.370 | -0.620 | -0.573 | -0.446 | +0.595 | -0.542 / +0.026 | [905014, 905019] |

**P55.** (a) needs-block share at least 0.010 at every size: {'20': True, '40': True, '100': True} — MET. (b) needs-block share higher on flagged rows than unflagged: {'20': True, '40': True, '100': True} — MET. (c) act-block share above needs-block share: {'20': True, '40': True, '100': True} — MET.
