# Entry 27 reading grammar — p2-both-s1 (20×20)

## (1) R-1a paired team happiness

| pair | mean Δ | +/n | range |
|---|---|---|---|
| both_minus_trunk | +2.708 | 30/30 | [+2.472, +2.914] |
| both_minus_act15 | +0.233 | 30/30 | [+0.099, +0.569] |
| act15_minus_trunk | +2.475 | 30/30 | [+2.076, +2.794] |
| both_minus_nohead | +0.008 | 19/30 | [-0.134, +0.165] |

team: {"both": 90.021, "trunk": 87.314, "act15": 89.789, "nohead": 90.013}; edge 0.326; worst streak max {'both': 89, 'act15': 461}; aborts {'both': []}; F-053 {'both': []}
P46: MET — {"value": 0.233, "bar": 0.326, "met": true, "signed_mean": 0.233}

## (2) R-2a / R-2b

| stratum | both p90 (n) all / other | trunk p90 (n) all / other | act15 p90 (n) all / other | both vs trunk all / other | act15 vs trunk all / other |
|---|---|---|---|---|---|
| eat | 16.0 (1) / None (0) | 77.0 (3) / None (0) | 271.0 (9) / 271.0 (1) | UNDECIDABLE / UNDECIDABLE | UNDECIDABLE / UNDECIDABLE |
| drink | None (0) / None (0) | None (0) / None (0) | 461.0 (2) / None (0) | UNDECIDABLE / UNDECIDABLE | UNDECIDABLE / UNDECIDABLE |
| sleep | None (0) / None (0) | None (0) / None (0) | None (0) / None (0) | UNDECIDABLE / UNDECIDABLE | UNDECIDABLE / UNDECIDABLE |
| play | None (0) / None (0) | None (0) / None (0) | None (0) / None (0) | UNDECIDABLE / UNDECIDABLE | UNDECIDABLE / UNDECIDABLE |
| cuddle | 89.0 (3) / 89.0 (3) | 6.0 (1) / 6.0 (1) | None (0) / None (0) | UNDECIDABLE / UNDECIDABLE | UNDECIDABLE / UNDECIDABLE |
| happiness | None (0) / None (0) | 55.0 (1) / None (0) | 36.0 (1) / 36.0 (1) | UNDECIDABLE / UNDECIDABLE | UNDECIDABLE / UNDECIDABLE |

P47: UNDECIDABLE (no stratum reaches min-n on both sides) (degraded: []; readable: [])
R-2b differential: {"both": {"state": "INSUFFICIENT"}, "act15": {"state": "INSUFFICIENT"}, "trunk": {"state": "INSUFFICIENT"}}

## (3) the needs read's trajectory

- visible: 78 probes, cumulative states {'INSUFFICIENT': 78, 'CLEAR': 0, 'SIGNATURE': 0}, first sufficient update None, final INSUFFICIENT; per-probe grave bias over 1 probes with grave rows: mean of means 10.561878974621113, range [10.561878974621113, 10.561878974621113], grave rows 26
  P45 lived (visible): UNDECIDABLE (cumulative n_grave 26 < 200) — {"met": null, "n_grave": 26}
- all: 78 probes, cumulative states {'INSUFFICIENT': 78, 'CLEAR': 0, 'SIGNATURE': 0}, first sufficient update None, final INSUFFICIENT; per-probe grave bias over 2 probes with grave rows: mean of means 4.296146338399596, range [0.9168855757094346, 7.675407101089756], grave rows 152
  P45 lived (all): UNDECIDABLE (cumulative n_grave 152 < 200) — {"met": null, "n_grave": 152}

| update | ticks | cum visible | cum all | probe grave visible (n) | probe grave all (n) |
|---|---|---|---|---|---|
| 49 | 153600 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 99 | 307200 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 149 | 460800 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 199 | 614400 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 249 | 768000 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 299 | 921600 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 349 | 1075200 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 399 | 1228800 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 449 | 1382400 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 499 | 1536000 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 549 | 1689600 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 599 | 1843200 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 649 | 1996800 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 699 | 2150400 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 749 | 2304000 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 799 | 2457600 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 849 | 2611200 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 899 | 2764800 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 949 | 2918400 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 999 | 3072000 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1049 | 3225600 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1099 | 3379200 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1149 | 3532800 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1199 | 3686400 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1249 | 3840000 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1299 | 3993600 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1349 | 4147200 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1399 | 4300800 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1449 | 4454400 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1499 | 4608000 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1549 | 4761600 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1599 | 4915200 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1649 | 5068800 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1699 | 5222400 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1749 | 5376000 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1799 | 5529600 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1849 | 5683200 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1899 | 5836800 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1949 | 5990400 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 1999 | 6144000 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 2049 | 6297600 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 2099 | 6451200 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 2149 | 6604800 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 2199 | 6758400 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 2249 | 6912000 | INSUFFICIENT | INSUFFICIENT | 10.56 (26) | 7.68 (48) |
| 2299 | 7065600 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 2349 | 7219200 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 2399 | 7372800 | INSUFFICIENT | INSUFFICIENT | None (0) | 0.92 (104) |
| 2449 | 7526400 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 2499 | 7680000 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 2549 | 7833600 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 2599 | 7987200 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 2649 | 8140800 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 2699 | 8294400 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 2749 | 8448000 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 2799 | 8601600 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 2849 | 8755200 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 2899 | 8908800 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 2949 | 9062400 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 2999 | 9216000 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 3049 | 9369600 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 3099 | 9523200 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 3149 | 9676800 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 3199 | 9830400 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 3249 | 9984000 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 3299 | 10137600 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 3349 | 10291200 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 3399 | 10444800 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 3449 | 10598400 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 3499 | 10752000 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 3549 | 10905600 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 3599 | 11059200 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 3649 | 11212800 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 3699 | 11366400 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 3749 | 11520000 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 3799 | 11673600 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 3849 | 11827200 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |
| 3899 | 11980800 | INSUFFICIENT | INSUFFICIENT | None (0) | None (0) |

## the needs head on the leg (R-4 extended)

pooled: {"visible": {"state": "INSUFFICIENT", "grave": 5.038925313949585, "common": 0.8594883218520126, "n_grave": 55, "n_common": 4268871}, "all": {"state": "CLEAR", "grave": 10.665887772364002, "common": 1.7568300556596472, "n_grave": 620, "n_common": 11997800}}
P45 leg: NOT MET — {'visible': 'INSUFFICIENT', 'all': 'CLEAR'}

One seed clears nothing (the three-seed valve); every consequence is hers (entry 27's grammar).
