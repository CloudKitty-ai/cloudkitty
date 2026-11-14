# The block read on the needs-only arm (p2u-needs-s1's recorded uniform legs; 30 worlds a leg)

Share = decision rows whose greedy act changes when the block's cells are zeroed (zero) or permuted across the seat's own ticks (perm). Blocks: needs = the needs head's seven estimates + P(grave); tsl = the time-since-live cell; all = every appended cell. Flagged = rows where some friend row's P(grave) cell is at least 0.5; under 200 flagged rows a leg reads INSUFFICIENT.

| size | mode | block | all rows | free-choice rows | flagged rows | unflagged rows |
|---|---|---|---|---|---|---|
| 20×20 | zero | needs | 0.0287 | 0.0514 | 0.0966 | 0.0286 |
| 20×20 | zero | tsl | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 20×20 | zero | all | 0.0287 | 0.0514 | 0.0966 | 0.0286 |
| 20×20 | perm | needs | 0.0196 | 0.0351 | 0.1013 | 0.0195 |
| 20×20 | perm | tsl | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 20×20 | perm | all | 0.0197 | 0.0353 | 0.1009 | 0.0196 |
| 40×40 | zero | needs | 0.0252 | 0.0414 | 0.0917 | 0.0246 |
| 40×40 | zero | tsl | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 40×40 | zero | all | 0.0252 | 0.0414 | 0.0917 | 0.0246 |
| 40×40 | perm | needs | 0.0204 | 0.0336 | 0.0812 | 0.0199 |
| 40×40 | perm | tsl | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 40×40 | perm | all | 0.0204 | 0.0336 | 0.0816 | 0.0199 |

| size | rows | free-choice rows | flagged rows | ties | needs − no-head paired Δ | Δ bottom tercile of needs share | Δ mid | Δ top | Spearman needs share ~ Δ |
|---|---|---|---|---|---|---|---|---|---|
| 20×20 | 3,000,000 | 1,674,629 | 2,794 | 0 | -0.235 | -0.208 | -0.220 | -0.277 | -0.390 |
| 40×40 | 3,000,000 | 1,823,717 | 27,670 | 1 | -0.442 | -0.367 | -0.410 | -0.548 | -0.539 |

**N3, per size read** (a: the needs cells drive at least 0.010 of acts; b: more on flagged rows than unflagged, None = under the flagged-row minimum): 20×20 a True, b True; 40×40 a True, b True. Not read: 100×100.
