"""Guards for beam_plan.py on RECORDED rows (fixtures/plan-fixture.npz from record_plan_fixture.py:
gen1-A on the package world, seed 870001). Run: python -B test_beam_plan.py"""
from pathlib import Path
import numpy as np
import beam_plan as P
import obs_layout_v5 as L

F = np.load(Path(__file__).resolve().parent / "fixtures" / "plan-fixture.npz")


def planner_for(logits):
    return P.BeamPlanner(lambda rows: logits[: len(rows)])


def chosen(mask, act_logits):
    return int(np.where(mask[:L.N_ACT], act_logits, -np.inf).argmax())


# TRIGGER rows: the mind wants a solo nap off a beam with a beam in reach -> the order forces one
# legal move that brings the cat closer, never the nap itself
for o, m, lg in zip(F["trigger_obs"], F["trigger_mask"], F["trigger_logits"]):
    assert chosen(m, lg[:L.N_ACT]) == P.SLEEP_SOLO and o[L.SELF_IN_SUNBEAM] < 0.5 and o[L.SELF_ACTIVITY + 2] < 0.5
    kb = P.known_beam(o); assert kb is not None and 0 < kb[0] <= P.REACH, kb
    assert P.trigger(o, m, P.SLEEP_SOLO) == kb[1]
    pl = planner_for(lg[None]); out = pl(o[None], m[None])[0]
    a = chosen(m, out[:L.N_ACT])
    assert a in P.MOVES and m[a], ("a legal move", a)
    x, y = P.me_pos(o); dx, dy = P.STEP[a]; tx, ty = kb[1]
    assert max(abs(tx - x - dx), abs(ty - y - dy)) <= max(abs(tx - x), abs(ty - y)) and \
        abs(tx - x - dx) + abs(ty - y - dy) < abs(tx - x) + abs(ty - y), "the forced step reduces the distance to the beam"
    assert np.array_equal(out[L.N_ACT:], lg[L.N_ACT:]), "the message head is the mind's"
    assert pl.stats["orders"] == 1 and pl.stats["forced_ticks"] == 1

# ARRIVED rows: on a beam with the nap legal -> the order (if any) ends in a forced solo nap
o, m, lg = F["arrived_obs"][0], F["arrived_mask"][0], F["arrived_logits"][0]
pl = planner_for(lg[None]); pl.orders[0] = {"target": P.me_pos(o), "ticks": 3, "stuck": 0}
out = pl(o[None], m[None])[0]
assert chosen(m, out[:L.N_ACT]) == P.SLEEP_SOLO and 0 not in pl.orders and pl.stats["arrived"] == 1

# NOBEAM rows: the mind wants a nap and no beam is known -> logits pass through untouched
for o, m, lg in zip(F["nobeam_obs"], F["nobeam_mask"], F["nobeam_logits"]):
    pl = planner_for(lg[None]); out = pl(o[None], m[None])[0]
    assert np.array_equal(out, lg) and pl.stats["orders"] == 0

# an order that never arrives gives up after MAX_TICKS (the same trigger row fed every tick)
o, m, lg = F["trigger_obs"][0], F["trigger_mask"][0], F["trigger_logits"][0]
pl = planner_for(lg[None])
for _ in range(P.MAX_TICKS + 1):
    pl(o[None], m[None])
assert 0 not in pl.orders and pl.stats["gave_up_long"] == 1 and pl.stats["orders"] == 1, pl.stats
# ...and a hunger emergency releases it at once
pl = planner_for(lg[None]); pl(o[None], m[None]); hungry = o.copy(); hungry[P.NEED_EAT] = P.EMERGENCY
out = pl(hungry[None], m[None])[0]
assert 0 not in pl.orders and pl.stats["released_emergency"] == 1 and chosen(m, out[:L.N_ACT]) == P.SLEEP_SOLO
# a row already on a beam never starts an order, whatever the mind picks
o2 = o.copy(); o2[L.SELF_IN_SUNBEAM] = 1.0
pl = planner_for(lg[None]); out = pl(o2[None], m[None])[0]
assert pl.stats["orders"] == 0 and np.array_equal(out, lg)
# a cat already asleep (its Sleep is a continue) never starts an order either: by the activity
# bit alone, and with its moves masked as the engine has them
o3 = o.copy(); o3[L.SELF_ACTIVITY:L.SELF_ACTIVITY + 7] = 0; o3[L.SELF_ACTIVITY + 2] = 1.0
pl = planner_for(lg[None]); out = pl(o3[None], m[None])[0]
assert pl.stats["orders"] == 0 and np.array_equal(out, lg), "asleep is not a nap start"
m3 = m.copy(); m3[:4] = False
pl = planner_for(lg[None]); out = pl(o3[None], m3[None])[0]
assert pl.stats["orders"] == 0 and np.array_equal(out, lg)
print("test_beam_plan ok")
