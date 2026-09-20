"""Tiers 3 and 4: a planner over a policy executor, for beams only (owner 2026-09-20).

The seat's own Gen 1 mind decides every tick. Two standing orders sit above it, both gated on
the mind's OWN nap decision (rule 4: no cat sleeps because a friend is warm):

  friend order (tier 4, wins when both apply): the mind picks a nap (solo or with anyone) and a
      friend is asleep on a beam within FRIEND_REACH -> walk until adjacent (Manhattan 1) and
      cosleep with that friend (spec 031 conducts the beam rate to the cosleeper).
  beam order (tier 3, reach lowered to 5 in tier 4): the mind picks a solo nap off a beam and a
      known unoccupied beam is within REACH -> walk to it, nap on it.

Everything else, including the message head, is the mind's. An order gives up when the walk
stalls, runs long, its target is gone, or any of the cat's distress flags is up (tier 4; tier 3
released on eat or drink need >= 0.60 and never fired).

Reads only the observation row (obs layout v5) and the legal mask, like any advisor. No engine
change: the planner is a `plan:<slot>` seat spec in cert_harness_fog.py wrapping `ppo:<slot>`.
"""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "attn-oracle-2026-08-15"))
import obs_layout_v5 as L  # noqa: E402

W = H = 20
MOVES = (0, 1, 2, 3)                      # North (y-1), East (x+1), South (y+1), West (x-1): Direction::ALL
STEP = {0: (0, -1), 1: (1, 0), 2: (0, 1), 3: (-1, 0)}
SLEEP_SOLO = 9
SLEEP_WITH = [10 + k for k in range(L.COUNTS["kitty"])]      # SleepWith kitty row k; row k <-> menu slot k
SLEEPS = {SLEEP_SOLO, *SLEEP_WITH}
KITTY_ROWS = [85 + k * L.KITTY_W for k in range(L.COUNTS["kitty"])]
ROW_ASLEEP = L.ROW_ACTIVITY + 2                               # activity one-hot: idle, rest, sleep, ...
SUNBEAM_SLOTS = [b for b, w in L.BLOCKS if w == 6]           # two nearest-K beam slots, width 6
SLOT_TTL, SLOT_OCCUPIED = 4, 5                                # after present, dx, dy, dist
MEM_SUNBEAM = L.SELF_MEMORY + L.ELEMENT_KINDS.index("sunbeam") * L.MEMORY_SLOT   # present, dx, dy, staleness/40
SELF_DISTRESS = 20                                            # six flags after progress (observe.rs self block)
FORCE = 1e6

# Order parameters (declared in PREREG-tier4.md)
REACH = 5            # beam order: Chebyshev tiles (tier 3 ran 6; the scripted teacher's priced reach is 8)
FRIEND_REACH = 3     # friend order: Chebyshev tiles to a friend asleep on a beam
MAX_TICKS = 30       # give up after this many ticks in an order
MAX_STUCK = 3        # consecutive ticks with no legal distance-reducing step (or no legal cosleep when adjacent)
MEM_FRESH = 0.5      # remembered beam usable while staleness/40 is under this (20 ticks)


def me_pos(row):
    return int(round(float(row[L.SELF_POS]) * W)), int(round(float(row[L.SELF_POS + 1]) * H))


def distressed(row):
    return bool((row[SELF_DISTRESS:SELF_DISTRESS + 6] > 0.5).any())


def known_beam(row):
    """The nearest known unoccupied beam as (chebyshev, (x, y)), or None: visible slots first
    (nearest-K order), then the sunbeam memory slot while it is fresh."""
    x, y = me_pos(row)
    best = None
    for b in SUNBEAM_SLOTS:
        if row[b + L.SLOT_PRESENT] > 0.5 and row[b + SLOT_OCCUPIED] < 0.5:
            tx = x + int(round(float(row[b + L.SLOT_DX]) * W)); ty = y + int(round(float(row[b + L.SLOT_DY]) * H))
            d = max(abs(tx - x), abs(ty - y))
            if best is None or d < best[0]:
                best = (d, (tx, ty))
    if best is None and row[MEM_SUNBEAM] > 0.5 and row[MEM_SUNBEAM + 3] < MEM_FRESH:
        tx = x + int(round(float(row[MEM_SUNBEAM + 1]) * W)); ty = y + int(round(float(row[MEM_SUNBEAM + 2]) * H))
        best = (max(abs(tx - x), abs(ty - y)), (tx, ty))
    return best


def friend_on_beam(row):
    """The nearest visible friend asleep on a beam as (chebyshev, slot k, (x, y)), or None."""
    x, y = me_pos(row)
    best = None
    for k, b in enumerate(KITTY_ROWS):
        if row[b + L.ROW_PRESENT] > 0.5 and row[b + ROW_ASLEEP] > 0.5 and row[b + L.ROW_SUNBEAM_BIT] > 0.5:
            fx = x + int(round(float(row[b + L.ROW_DX]) * W)); fy = y + int(round(float(row[b + L.ROW_DY]) * H))
            d = max(abs(fx - x), abs(fy - y))
            if best is None or d < best[0]:
                best = (d, k, (fx, fy))
    return best


def step_toward(row, mask, target, metric="beam"):
    """The legal move that most reduces the distance to target, or None. metric 'beam' orders by
    (Chebyshev, Manhattan); 'friend' by (Manhattan, Chebyshev), since adjacency is Manhattan 1."""
    x, y = me_pos(row); tx, ty = target
    def dist(px, py):
        c, m = max(abs(tx - px), abs(ty - py)), abs(tx - px) + abs(ty - py)
        return (c, m) if metric == "beam" else (m, c)
    now = dist(x, y)
    best = None
    for mv in MOVES:
        if not mask[mv]:
            continue
        dx, dy = STEP[mv]; d = dist(x + dx, y + dy)
        if d < now and (best is None or d < best[0]):
            best = (d, mv)
    return None if best is None else best[1]


def asleep_now(row):
    return row[L.SELF_ACTIVITY + 2] > 0.5


def trigger_friend(row, mask, mind):
    """The friend order's start: the mind picks a nap (any), the cat is not on a beam and not
    already asleep, a friend is asleep on a beam within FRIEND_REACH, and either cosleeping with
    that friend is legal now or a legal step toward them exists. Returns (slot, (x, y)) or None."""
    if mind not in SLEEPS or row[L.SELF_IN_SUNBEAM] > 0.5 or asleep_now(row):
        return None
    fb = friend_on_beam(row)
    if fb is None or fb[0] > FRIEND_REACH:
        return None
    d, k, pos = fb
    if mask[SLEEP_WITH[k]] or step_toward(row, mask, pos, "friend") is not None:
        return (k, pos)
    return None


def trigger(row, mask, mind):
    """The beam order's start (tier 3's rule at REACH): the mind picks a solo nap, the cat is not
    on a beam and not already asleep, a known unoccupied beam sits within REACH, and a legal step
    toward it exists. Returns the beam (x, y) or None."""
    if mind != SLEEP_SOLO or row[L.SELF_IN_SUNBEAM] > 0.5 or asleep_now(row):
        return None
    kb = known_beam(row)
    if kb is None or kb[0] > REACH or kb[0] == 0:
        return None
    return kb[1] if step_toward(row, mask, kb[1]) is not None else None


class BeamPlanner:
    """Wraps a seat's policy forward. `__call__(rows, masks)` returns logits with the order's
    action forced (a large bonus on one legal index) where an order is active; the harness's
    masked argmax then takes it. State is per row index (one world per process)."""

    KEYS = ("orders", "arrived", "gave_up_stuck", "gave_up_long", "gave_up_gone", "released_distress", "forced_ticks")

    def __init__(self, fwd):
        self.fwd = fwd
        self.orders = {}          # row index -> {"kind", "target", "slot", "ticks", "stuck"}
        self.stats = {f"{kind}_{k}": 0 for kind in ("beam", "friend") for k in self.KEYS}

    def __call__(self, rows, masks):
        logits = np.array(self.fwd(rows), np.float32)
        for i in range(len(rows)):
            logits[i, :L.N_ACT] = self.overlay(i, rows[i], masks[i], logits[i, :L.N_ACT])
        return logits

    def bump(self, kind, key):
        self.stats[f"{kind}_{key}"] += 1

    def end(self, i, kind, key, act_logits):
        self.bump(kind, key); del self.orders[i]; return act_logits

    def overlay(self, i, row, mask, act_logits):
        mind = int(np.where(mask[:L.N_ACT], act_logits, -np.inf).argmax())
        order = self.orders.get(i)
        if order is None:
            tf = trigger_friend(row, mask, mind)
            if tf is not None:
                order = self.orders[i] = {"kind": "friend", "slot": tf[0], "target": tf[1], "ticks": 0, "stuck": 0}
            else:
                tb = trigger(row, mask, mind)
                if tb is None:
                    return act_logits
                order = self.orders[i] = {"kind": "beam", "slot": None, "target": tb, "ticks": 0, "stuck": 0}
            self.bump(order["kind"], "orders")
        kind = order["kind"]
        order["ticks"] += 1
        if distressed(row):
            return self.end(i, kind, "released_distress", act_logits)
        if order["ticks"] > MAX_TICKS:
            return self.end(i, kind, "gave_up_long", act_logits)
        if kind == "friend":
            fb = friend_on_beam(row)
            if fb is None or fb[1] != order["slot"]:
                return self.end(i, kind, "gave_up_gone", act_logits)
            order["target"] = fb[2]
            k = order["slot"]
            if mask[SLEEP_WITH[k]]:
                self.bump(kind, "arrived"); self.bump(kind, "forced_ticks"); del self.orders[i]
                return self.force(act_logits, SLEEP_WITH[k])
            mv = step_toward(row, mask, order["target"], "friend")
        else:
            if me_pos(row) == order["target"] or row[L.SELF_IN_SUNBEAM] > 0.5:
                del self.orders[i]
                if mask[SLEEP_SOLO]:
                    self.bump(kind, "arrived"); self.bump(kind, "forced_ticks")
                    return self.force(act_logits, SLEEP_SOLO)
                return act_logits
            kb = known_beam(row)
            if kb is None:
                return self.end(i, kind, "gave_up_gone", act_logits)
            order["target"] = kb[1]                   # re-aim at the nearest known beam each tick
            mv = step_toward(row, mask, order["target"])
        if mv is None:
            order["stuck"] += 1
            if order["stuck"] >= MAX_STUCK:
                return self.end(i, kind, "gave_up_stuck", act_logits)
            return act_logits
        order["stuck"] = 0
        self.bump(kind, "forced_ticks")
        return self.force(act_logits, mv)

    @staticmethod
    def force(act_logits, index):
        out = np.array(act_logits, np.float32); out[index] = FORCE
        return out
