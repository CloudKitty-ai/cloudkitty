# The block read on the true-needs arm (p2u-truth-s1-u3906's recorded uniform legs; 30 worlds a leg)

Share = decision rows whose greedy act changes when the block's cells are zeroed (zero) or permuted across the seat's own ticks (perm). Blocks: truth = each friend's true needs, happiness, bath and GRAVE flag; tsl = the time-since-live cell; all = every appended cell. Grave rows = some friend is grave by the engine's state; under 200 grave rows a leg reads INSUFFICIENT.

| size | mode | block | all rows | free-choice rows | grave rows | other rows |
|---|---|---|---|---|---|---|
| 20×20 | zero | truth | 0.0383 | 0.0672 | INSUFFICIENT | 0.0383 |
| 20×20 | zero | tsl | 0.0000 | 0.0000 | INSUFFICIENT | 0.0000 |
| 20×20 | zero | all | 0.0383 | 0.0672 | INSUFFICIENT | 0.0383 |
| 20×20 | perm | truth | 0.0478 | 0.0839 | INSUFFICIENT | 0.0478 |
| 20×20 | perm | tsl | 0.0000 | 0.0000 | INSUFFICIENT | 0.0000 |
| 20×20 | perm | all | 0.0479 | 0.0840 | INSUFFICIENT | 0.0479 |
| 40×40 | zero | truth | 0.0422 | 0.0679 | 0.1045 | 0.0420 |
| 40×40 | zero | tsl | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 40×40 | zero | all | 0.0422 | 0.0679 | 0.1045 | 0.0420 |
| 40×40 | perm | truth | 0.0497 | 0.0801 | 0.1114 | 0.0496 |
| 40×40 | perm | tsl | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 40×40 | perm | all | 0.0496 | 0.0798 | 0.1110 | 0.0494 |

| size | rows | free-choice rows | grave rows | grave rows changed, truth zeroed | ties |
|---|---|---|---|---|---|
| 20×20 | 3,000,000 | 1,709,140 | 84 | 19 | 0 |
| 40×40 | 3,000,000 | 1,862,525 | 7,514 | 785 | 1 |

**T3 UNSCORED (too few grave rows)** (a: the truth cells drive at least 0.025 of acts at both sizes: True; b: more on grave rows than on others at both: None).

Not read: none.
