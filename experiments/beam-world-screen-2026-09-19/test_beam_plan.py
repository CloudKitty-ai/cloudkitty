"""Guards for beam_plan.py on RECORDED rows (fixtures/plan-fixture.npz from record_plan_fixture.py:
gen1-A under the planner on the package world, seed 870001). Run: python -B test_beam_plan.py"""
from pathlib import Path
import numpy as np
import beam_plan as P
import obs_layout_v5 as L

F = np.load(Path(__file__).resolve().parent / "fixtures" / "plan-fixture.npz")


def planner_for(logits):
    return P.BeamPlanner(lambda rows: logits[: len(rows)])


def chosen(mask, act_logits):
    return int(np.where(mask[:L.N_ACT], act_logits, -np.inf).argmax())


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# BEAM order (TRIGGER rows): the mind wants a solo nap off a beam with a beam in reach and no
# friend order applying -> one legal move that brings the cat closer, never the nap itself
for o, m, lg in zip(F["trigger_obs"], F["trigger_mask"], F["trigger_logits"]):
    assert chosen(m, lg[:L.N_ACT]) == P.SLEEP_SOLO and o[L.SELF_IN_SUNBEAM] < 0.5 and not P.asleep_now(o)
    kb = P.known_beam(o); assert kb is not None and 0 < kb[0] <= P.REACH, kb
    assert P.trigger(o, m, P.SLEEP_SOLO) == kb[1] and P.trigger_friend(o, m, P.SLEEP_SOLO) is None
    pl = planner_for(lg[None]); out = pl(o[None], m[None])[0]
    a = chosen(m, out[:L.N_ACT])
    assert a in P.MOVES and m[a], ("a legal move", a)
    x, y = P.me_pos(o); dx, dy = P.STEP[a]; tx, ty = kb[1]
    assert max(abs(tx - x - dx), abs(ty - y - dy)) <= max(abs(tx - x), abs(ty - y)) and \
        manhattan((x + dx, y + dy), (tx, ty)) < manhattan((x, y), (tx, ty)), "the forced step reduces the distance to the beam"
    assert np.array_equal(out[L.N_ACT:], lg[L.N_ACT:]), "the message head is the mind's"
    assert pl.stats["beam_orders"] == 1 and pl.stats["beam_forced_ticks"] == 1 and pl.stats["friend_orders"] == 0

assert P.REACH == 5 and P.FRIEND_REACH == 3   # tier 4's pins

# ARRIVED rows: on a beam with the nap legal -> the beam order ends in a forced solo nap
o, m, lg = F["arrived_obs"][0], F["arrived_mask"][0], F["arrived_logits"][0]
pl = planner_for(lg[None]); pl.orders[0] = {"kind": "beam", "slot": None, "target": P.me_pos(o), "ticks": 3, "stuck": 0}
out = pl(o[None], m[None])[0]
assert chosen(m, out[:L.N_ACT]) == P.SLEEP_SOLO and 0 not in pl.orders and pl.stats["beam_arrived"] == 1

# NOBEAM rows: the mind wants a nap and nothing is known -> logits pass through untouched
for o, m, lg in zip(F["nobeam_obs"], F["nobeam_mask"], F["nobeam_logits"]):
    pl = planner_for(lg[None]); out = pl(o[None], m[None])[0]
    assert np.array_equal(out, lg) and pl.stats["beam_orders"] == 0 and pl.stats["friend_orders"] == 0

# FRIEND order (FRIEND rows): the mind wants a nap, a friend sleeps on a beam within 3, not adjacent
# -> a legal move that reduces the MANHATTAN distance to the friend; the friend order wins
for o, m, lg in zip(F["friend_obs"], F["friend_mask"], F["friend_logits"]):
    mind = chosen(m, lg[:L.N_ACT]); assert mind in P.SLEEPS and o[L.SELF_IN_SUNBEAM] < 0.5 and not P.asleep_now(o)
    fb = P.friend_on_beam(o); assert fb is not None and fb[0] <= P.FRIEND_REACH, fb
    k, pos = P.trigger_friend(o, m, mind); assert k == fb[1] and not m[P.SLEEP_WITH[k]]
    pl = planner_for(lg[None]); out = pl(o[None], m[None])[0]
    a = chosen(m, out[:L.N_ACT])
    assert a in P.MOVES and m[a], ("a legal move", a)
    x, y = P.me_pos(o); dx, dy = P.STEP[a]
    assert manhattan((x + dx, y + dy), pos) < manhattan((x, y), pos), "the forced step reduces the Manhattan distance to the friend"
    assert pl.orders[0]["kind"] == "friend" and pl.stats["friend_orders"] == 1 and pl.stats["beam_orders"] == 0, "the friend order wins"

# FRIEND_ADJ rows: adjacent with the cosleep legal -> the order forces SleepWith that friend at once
for o, m, lg in zip(F["friend_adj_obs"], F["friend_adj_mask"], F["friend_adj_logits"]):
    mind = chosen(m, lg[:L.N_ACT]); k, pos = P.trigger_friend(o, m, mind); assert m[P.SLEEP_WITH[k]]
    pl = planner_for(lg[None]); out = pl(o[None], m[None])[0]
    assert chosen(m, out[:L.N_ACT]) == P.SLEEP_WITH[k] and 0 not in pl.orders and pl.stats["friend_arrived"] == 1

# an order that never arrives gives up after MAX_TICKS (the same trigger row fed every tick)
o, m, lg = F["trigger_obs"][0], F["trigger_mask"][0], F["trigger_logits"][0]
pl = planner_for(lg[None])
for _ in range(P.MAX_TICKS + 1):
    pl(o[None], m[None])
assert 0 not in pl.orders and pl.stats["beam_gave_up_long"] == 1 and pl.stats["beam_orders"] == 1, pl.stats
# ...a distress flag releases it at once (tier 4: flags, not a need level)
pl = planner_for(lg[None]); pl(o[None], m[None]); hurt = o.copy(); hurt[P.SELF_DISTRESS + 0] = 1.0
out = pl(hurt[None], m[None])[0]
assert 0 not in pl.orders and pl.stats["beam_released_distress"] == 1 and chosen(m, out[:L.N_ACT]) == P.SLEEP_SOLO
# ...a friend who leaves the beam ends the friend order
o, m, lg = F["friend_obs"][0], F["friend_mask"][0], F["friend_logits"][0]
pl = planner_for(lg[None]); pl(o[None], m[None]); gone = o.copy()
for b in P.KITTY_ROWS: gone[b + L.ROW_SUNBEAM_BIT] = 0.0
pl(gone[None], m[None]); assert 0 not in pl.orders and pl.stats["friend_gave_up_gone"] == 1
# a row already on a beam never starts an order, whatever the mind picks
o, m, lg = F["trigger_obs"][0], F["trigger_mask"][0], F["trigger_logits"][0]
o2 = o.copy(); o2[L.SELF_IN_SUNBEAM] = 1.0
pl = planner_for(lg[None]); out = pl(o2[None], m[None])[0]
assert pl.stats["beam_orders"] == 0 and pl.stats["friend_orders"] == 0 and np.array_equal(out, lg)
# a cat already asleep (its Sleep is a continue) never starts an order either
o3 = o.copy(); o3[L.SELF_ACTIVITY:L.SELF_ACTIVITY + 7] = 0; o3[L.SELF_ACTIVITY + 2] = 1.0
pl = planner_for(lg[None]); out = pl(o3[None], m[None])[0]
assert pl.stats["beam_orders"] == 0 and pl.stats["friend_orders"] == 0 and np.array_equal(out, lg), "asleep is not a nap start"
# a cat that is NOT choosing a nap never gets the friend order, warm friend or not (rule 4)
o4, m4, lg4 = F["friend_obs"][0], F["friend_mask"][0], F["friend_logits"][0].copy()
lg4[:L.N_ACT] = -1.0; lg4[38] = 5.0  # Idle
pl = planner_for(lg4[None]); out = pl(o4[None], m4[None])[0]
assert pl.stats["friend_orders"] == 0 and np.array_equal(out, lg4), "the trigger is the mind's own nap"
print("test_beam_plan ok")
