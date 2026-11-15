# The lost-cat and drink reads (replays of recorded legs; needs scout seed 1 beside the no-head arm, same worlds)

Closing = the share of a lonely cat's moves that shorten its walk to the nearest heard friend's call place (moves in brackets).

| arm / size | all | in long streaks | walk 0-10 | 10-20 | 20-40 | 40-70 | 70+ | call age 0-10 | 10-20 | 20-30 | friend walked 0-2 | 2-6 | 6+ | same target next move | straightness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| needs/40 | 0.651 (3308) | 0.475 (451) | 0.938 (242) | 0.798 (919) | 0.550 (1947) | 0.605 (200) | — | 0.653 (3212) | 0.543 (81) | 0.600 (15) | 0.653 (2718) | 0.650 (531) | 0.525 (59) | 0.876 | 0.288 |
| needs/100 | 0.595 (9913) | 0.489 (2266) | 0.943 (279) | 0.835 (1697) | 0.578 (4215) | 0.487 (3075) | 0.439 (647) | 0.598 (9708) | 0.447 (170) | 0.600 (35) | 0.597 (8199) | 0.595 (1581) | 0.481 (133) | 0.927 | 0.336 |
| nohead/40 | 0.861 (509) | — | 0.920 (137) | 0.873 (245) | 0.766 (124) | 1.000 (3) | — | 0.855 (491) | 1.000 (14) | 1.000 (4) | 0.852 (420) | 0.895 (86) | 1.000 (3) | 0.857 | 0.517 |
| nohead/100 | 0.805 (5000) | 0.562 (160) | 0.976 (375) | 0.919 (1545) | 0.741 (2239) | 0.699 (778) | 0.556 (63) | 0.805 (4917) | 0.807 (83) | — | 0.806 (4108) | 0.792 (821) | 0.859 (71) | 0.915 | 0.7 |

| arm / size | friends hearing a lost cat | their moves closing on it | of content friends | idle drink rate, no flag | flagged |
|---|---|---|---|---|---|
| needs/40 | [0.921, 1.0, 1.0] | [[0.56, 1019], [0.657, 627], [0.602, 826]] | [[0.56, 905], [0.654, 621], [0.602, 826]] | [[0.088, 7187], [0.077, 7464], [0.066, 7053]] | [[0.917, 521], [0.673, 107], [0.825, 154]] |
| needs/100 | [0.994, 1.0, 1.0] | [[0.571, 5192], [0.52, 1980], [0.612, 3678]] | [[0.555, 4216], [0.513, 1856], [0.601, 3368]] | [[0.186, 6855], [0.108, 2161], [0.138, 5493]] | [[0.729, 885], [0.732, 399], [0.733, 829]] |
| nohead/40 | [None, 1.0, None] | [None, [0.361, 36], None] | [None, [0.361, 36], None] | [[0.08, 8851], [0.079, 8420], [0.082, 8508]] | [None, [0.75, 24], None] |
| nohead/100 | [1.0, 1.0, 1.0] | [[0.579, 432], [0.532, 990], [0.734, 124]] | [[0.519, 343], [0.507, 815], [0.69, 71]] | [[0.056, 7089], [0.06, 7524], [0.059, 7249]] | [[0.176, 34], [0.533, 152], [0.222, 9]] |

Streaks of 300+ ticks:

| arm / size / world / seat | need | length | nearest friend | in sight | heard | cuddle act legal | proposed when legal | refused | moved | on water | free ticks: chosen | bowl walk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| needs / 40 / 905012 / 2 | eat | 984 | 22.7 | 0.097 | 1.0 | 0.025 | 0.88 | 0.0 | 0.002 | 0.0 | 496: {'drink': 464, 'play_solo': 13, 'sleep_with_kitty_0': 12, 'play_critter_0': 3, 'chase_kitty_0': 2} | {'mean': 9.0, 'range': [7.0, 13.0]} |
| needs / 40 / 905004 / 2 | cuddle | 337 | 35.1 | 0.015 | 1.0 | 0.006 | 1.0 | 0.0 | 0.757 | 0.003 | 295: {'move_east': 102, 'move_west': 96, 'move_south': 22, 'move_north': 21, 'eat': 15} | {'mean': 9.3, 'range': [7.0, 12.0]} |
| needs / 40 / 905030 / 4 | cuddle | 427 | 34.6 | 0.012 | 1.0 | 0.005 | 1.0 | 0.0 | 0.473 | 0.0 | 316: {'move_east': 82, 'drink': 76, 'move_west': 72, 'move_north': 25, 'move_south': 23} | {'mean': 9.2, 'range': [1.0, 13.0]} |
| needs / 100 / 905001 / 1 | cuddle | 910 | 58.9 | 0.005 | 1.0 | 0.002 | 1.0 | 0.0 | 0.705 | 0.038 | 776: {'move_west': 234, 'move_east': 193, 'move_south': 87, 'chase_critter_0': 78, 'move_north': 40} | {'mean': 7.1, 'range': [1.0, 14.0]} |
| needs / 100 / 905001 / 2 | cuddle | 382 | 29.0 | 0.016 | 1.0 | 0.0 | None | None | 0.149 | 0.0 | 223: {'drink': 145, 'move_south': 25, 'move_north': 22, 'move_west': 8, 'play_solo': 8} | {'mean': 12.9, 'range': [12.0, 16.0]} |
| needs / 100 / 905001 / 3 | eat | 326 | 34.3 | 0.018 | 1.0 | 0.006 | 1.0 | 0.0 | 0.304 | 0.003 | 211: {'drink': 93, 'move_south': 40, 'move_west': 31, 'move_east': 21, 'sleep_solo': 8} | {'mean': 13.3, 'range': [9.0, 16.0]} |
| needs / 100 / 905002 / 0 | cuddle | 999 | 71.8 | 0.0 | 1.0 | 0.0 | None | None | 0.31 | 0.026 | 649: {'drink': 233, 'move_west': 101, 'move_east': 91, 'move_south': 89, 'sleep_solo': 36} | {'mean': 7.0, 'range': [1.0, 12.0]} |
| needs / 100 / 905002 / 1 | cuddle | 415 | 45.7 | 0.022 | 1.0 | 0.007 | 1.0 | 0.0 | 0.542 | 0.005 | 320: {'move_west': 90, 'move_east': 64, 'drink': 54, 'move_north': 28, 'move_south': 19} | {'mean': 9.4, 'range': [1.0, 12.0]} |
| needs / 100 / 905003 / 1 | cuddle | 483 | 47.1 | 0.012 | 1.0 | 0.004 | 1.0 | 0.0 | 0.72 | 0.0 | 413: {'move_west': 116, 'move_east': 109, 'move_south': 50, 'chase_critter_0': 41, 'move_north': 28} | {'mean': 9.0, 'range': [1.0, 14.0]} |
| needs / 100 / 905003 / 2 | cuddle | 999 | 55.8 | 0.0 | 1.0 | 0.0 | None | None | 0.534 | 0.005 | 773: {'move_west': 211, 'move_east': 201, 'drink': 126, 'move_south': 94, 'play_critter_0': 51} | {'mean': 8.1, 'range': [4.0, 12.0]} |
| needs / 100 / 905003 / 3 | cuddle | 627 | 34.1 | 0.01 | 1.0 | 0.005 | 1.0 | 0.0 | 0.112 | 0.129 | 337: {'drink': 232, 'move_south': 20, 'move_east': 18, 'move_west': 18, 'move_north': 14} | {'mean': 12.0, 'range': [3.0, 17.0]} |
| nohead / 100 / 905002 / 0 | cuddle | 446 | 53.1 | 0.016 | 1.0 | 0.004 | 1.0 | 0.0 | 0.363 | 0.007 | 304: {'move_east': 58, 'drink': 57, 'move_west': 46, 'play_critter_0': 46, 'chase_critter_0': 40} | {'mean': 13.1, 'range': [9.0, 19.0]} |
