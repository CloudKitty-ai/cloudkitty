#!/usr/bin/env python3
"""Guard for needflow.py -- each baseline assertion is driven red in the same
run by the exact bug class it exists to catch (OLD=1-style, permanent red).

Post-041 the served config IS the sibling economy (riders partial, rest
availability two-tier), so the baseline claims flipped: rest must be
NONZERO now, and the retired pre-041 economy is the red arm that shows the
near-zero was riders saturating, not a dead branch (F-029's rule, model
edition).
"""
import needflow

T = 10000

def full(overrides=None, **params):
    saved = {k: getattr(needflow, k) for k in params}
    for k, v in params.items():
        setattr(needflow, k, v)
    try:
        return needflow.sim(overrides, ticks=T)
    finally:
        for k, v in saved.items():
            setattr(needflow, k, v)

def per1k(overrides=None, **params):
    return full(overrides, **params)["per_1k_cat_ticks"]

base_full = full()
base = base_full["per_1k_cat_ticks"]

# 1. The sibling baseline restores rest demand (the 041 point)...
assert base.get("rest_avail", 0) > 5.0, base
# ...red: the retired pre-041 economy (riders saturating, rest conscript)
# collapses rest back to the old near-zero (bug class: rider saturation).
pre041 = per1k({"cosleep_drip": 3.0, "cosleep_mutual": 8.0,
                "groom_cuddle": 8.0, "rest_cuddle": 8.0,
                "rest_passive": 0.0, "rest_mode": "conscript"})
assert pre041.get("rest_duet", 0) <= 1.0, pre041
assert "rest_avail" not in pre041, pre041

# 2. Co-sleep dominates solo sleep (its cuddle edge)...
assert base["cosleep"] > 5 * base.get("sleep_solo", 0), base
# ...red: remove the edge and solo takes the niche (bug class: edge mispriced).
edgeless = per1k({"cosleep_drip": 0, "cosleep_mutual": 0})
assert edgeless.get("cosleep", 0) <= 5 * edgeless.get("sleep_solo", 0), edgeless

# 3. Both groom modes and both play venues present (the diversity the owner
# points to as working)...
for k in ("groom_self", "groom_other"):
    assert base.get(k, 0) > 1.0, (k, base)
for k in ("play_solo", "play_duet"):
    assert base.get(k, 0) > 5.0, (k, base)
# ...red: non-persistent ever-present adjacency (the actual bug this model
# shipped with first) erases every solo niche.
crowded = per1k(P_ADJ=0.999)
assert crowded.get("groom_self", 0) <= 1.0, crowded
assert crowded.get("sleep_solo", 0) <= 0.1, crowded

# 4. ...red for play: an unpriced duet loses its venue (bug class: payload
# table drops a field -- blendLayouts' lesson, one economy over).
unpaid = per1k({"play_duet": 0.0})
assert unpaid.get("play_duet", 0) <= 5.0, unpaid

# 5. Waterline contagion: the dial is fully inert at 0 even with exposure
# set (bug class: a charge not gated on the factor)...
wet = {"wet_p": needflow.EXPOSURE["high"]}
assert full(wet) == base_full, "factor 0 must be byte-identical"
# ...and the ceiling gate holds: a zero ceiling means the charge never
# lands, so the ECONOMY is byte-identical (the diagnostic charge counters
# still record skip events -- strip them; they are readout, not economy)...
def economy(r):
    return {k: v for k, v in r.items() if k != "contagion_charges"}
assert economy(full({**wet, "contagion": 1.0, "wet_ceiling": 0.0})) == economy(base_full), \
    "ceiling 0 must leave the economy byte-identical"
# ...red: at factor 1 the charge lands and grooming absorbs it -- both
# groom modes must rise (bug class: charge computed but never applied).
charged = full({**wet, "contagion": 1.0})
assert charged != base_full, "factor 1 must move the economy"
assert charged["per_1k_cat_ticks"]["groom_other"] > base["groom_other"], charged
assert charged["per_1k_cat_ticks"]["groom_self"] > base["groom_self"], charged

# 6. Option A membership + adjacency (owner-ruled 2026-08-31; engine
# @172fcd9): a referenced cat never pays for the asymmetric kinds, a wet
# namer's scene charges nobody, a mid-scene adjacency lapse blocks the
# charge, and play stays reciprocal (its dry member pays from either role)...
ch = charged["contagion_charges"]
assert ch["partner_asym"] == 0, ch
assert ch["wet_namer_skip"] > 0, ch
assert ch["nonadjacent_skip"] > 0, ch
assert ch["partner_play"] > 0, ch
# ...red: the retired coin-flip membership (the pre-ruling model -- the
# exact pricing bug this section exists to catch) charges referenced cats
# for asymmetric kinds and never skips a wet namer or a lapsed pair.
retired = full({**wet, "contagion": 1.0, "membership": "coinflip-retired"})
rch = retired["contagion_charges"]
assert rch["partner_asym"] > 0, rch
assert rch["wet_namer_skip"] == 0 and rch["nonadjacent_skip"] == 0, rch

print("needflow guard: all green (each assertion shown red under its bug)")
