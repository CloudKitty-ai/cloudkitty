#!/usr/bin/env python3
"""The ostrich metric's strata (DECLARATION.md §Strata; prereg §8 item 4,
RULED S§3d with the E-review riders). Binned on the friend's TRUE state
at a tick, never on a prediction, with exactly the three ruled edges:

    GRAVE     any hidden need >= 90, or happiness < 45
    ADJACENT  not grave, and happiness < 70
    COMMON    happiness >= 70 and no hidden need >= 90

Edge sources (prereg §8 item 4 rider (a)): 45 = LOW_HAPPINESS
(crates/cloudkitty-rl/src/welfare.rs), 70 = MIN_MEAN_HAPPINESS
(welfare.rs, a run-mean bar borrowed onto the per-state axis), 90 = the
need `distress` edge, FROZEN BY VALUE (thresholds.distress = 90.0 in
cloudkitty.toml and g2leg-20.toml; the config key is provenance only, a
later config change does not move the bin). Two axes: 45 and 70 on
happiness, 90 on the need axis. Bath (need index 5) is visible and never
enters a bin: the hidden needs are indices 0..4 (eat, drink, sleep,
play, cuddle).
"""
import numpy as np

GRAVE, ADJACENT, COMMON = 0, 1, 2
NAMES = ("GRAVE", "ADJACENT", "COMMON")
HAP_GRAVE = 45.0     # happiness below this is grave      (LOW_HAPPINESS)
HAP_ADJACENT = 70.0  # happiness below this is adjacent   (MIN_MEAN_HAPPINESS)
NEED_DISTRESS = 90.0  # a hidden need at or over this is grave (thresholds.distress)
HIDDEN = slice(0, 5)  # eat, drink, sleep, play, cuddle; bath (5) excluded


def stratum(needs, hap):
    """needs (..., 6) and hap (...) on the /100 scale -> int codes (...)
    with GRAVE 0, ADJACENT 1, COMMON 2. Every tick lands in exactly one."""
    needs = np.asarray(needs, np.float64)
    hap = np.asarray(hap, np.float64)
    assert needs.shape[-1] == 6, needs.shape
    assert needs.shape[:-1] == hap.shape, (needs.shape, hap.shape)
    grave = (needs[..., HIDDEN] >= NEED_DISTRESS).any(-1) | (hap < HAP_GRAVE)
    adjacent = ~grave & (hap < HAP_ADJACENT)
    out = np.full(hap.shape, COMMON, np.int8)
    out[adjacent] = ADJACENT
    out[grave] = GRAVE
    return out


def counts(codes):
    """Occupancy per stratum, in NAMES order."""
    codes = np.asarray(codes)
    return {n: int((codes == i).sum()) for i, n in enumerate(NAMES)}
