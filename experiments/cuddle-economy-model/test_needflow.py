#!/usr/bin/env python3
"""Guard for needflow.py -- each baseline assertion is driven red in the same
run by the exact bug class it exists to catch (OLD=1-style, permanent red).

The F-029 rule applies to models too: baseline rest ~ 0 is only evidence once
the instrument is shown able to EMIT rest -- mutation 1 does exactly that.
"""
import needflow

T = 10000

def per1k(overrides=None, **params):
    saved = {k: getattr(needflow, k) for k in params}
    for k, v in params.items():
        setattr(needflow, k, v)
    try:
        return needflow.sim(overrides, ticks=T)["per_1k_cat_ticks"]
    finally:
        for k, v in saved.items():
            setattr(needflow, k, v)

base = per1k()

# 1. Baseline reproduces the observed near-zero rest...
assert base.get("rest_duet", 0) <= 1.0, base
# ...and the model CAN emit rest: starve cuddle of every rider and rest must
# appear (bug class: silently saturating riders / a dead rest branch).
starved = per1k({"cosleep_drip": 0, "cosleep_mutual": 0, "groom_cuddle": 0})
assert starved.get("rest_duet", 0) > 1.0, starved

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

print("needflow guard: all green (each assertion shown red under its bug)")
