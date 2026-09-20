"""Tier 3: a planner over a policy executor, for beams only (owner 2026-09-20, "Let's try the
planner/executor for beams as an extension to the work we're currently doing on beam sleep").

The seat's own Gen 1 mind decides every tick. One standing order sits above it: when the mind
chooses a solo nap off a beam and a beam it knows about is within reach, walk to that beam first,
then nap there. Everything else, including the message head, is the mind's. The order gives up
when the walk stalls, runs long, the beam is gone, or a hunger or thirst emergency arrives.

Reads only the observation row (obs layout v5) and the legal mask, like any advisor. No engine
change: the planner is a `plan:<slot>` seat spec in cert_harness_fog.py that wraps `ppo:<slot>`.
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
SUNBEAM_SLOTS = [b for b, w in L.BLOCKS if w == 6]           # two nearest-K beam slots, width 6
SLOT_TTL, SLOT_OCCUPIED = 4, 5                                # after present, dx, dy, dist
MEM_SUNBEAM = L.SELF_MEMORY + L.ELEMENT_KINDS.index("sunbeam") * L.MEMORY_SLOT   # present, dx, dy, staleness/40
NEED_EAT, NEED_DRINK = L.NEED_KINDS.index("eat"), L.NEED_KINDS.index("drink")
FORCE = 1e6

# Order parameters (declared in PREREG-tier3.md)
REACH = 6            # Chebyshev tiles; the scripted teacher's priced reach is 8
MAX_TICKS = 30       # give up after this many ticks in the order
MAX_STUCK = 3        # consecutive ticks with no legal distance-reducing step
MEM_FRESH = 0.5      # remembered beam usable while staleness/40 is under this (20 ticks)
EMERGENCY = 0.60     # eat or drink need (0..1) at or above this releases the order


def me_pos(row):
    return int(round(float(row[L.SELF_POS]) * W)), int(round(float(row[L.SELF_POS + 1]) * H))


def known_beam(row):
    """The nearest known unoccupied beam as an (x, y) target, or None: visible slots first
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


def step_toward(row, mask, target):
    """The legal move that most reduces (Chebyshev, Manhattan) distance to target, or None."""
    x, y = me_pos(row); tx, ty = target
    now = (max(abs(tx - x), abs(ty - y)), abs(tx - x) + abs(ty - y))
    best = None
    for m in MOVES:
        if not mask[m]:
            continue
        dx, dy = STEP[m]; nx, ny = x + dx, y + dy
        d = (max(abs(tx - nx), abs(ty - ny)), abs(tx - nx) + abs(ty - ny))
        if d < now and (best is None or d < best[0]):
            best = (d, m)
    return None if best is None else best[1]


def trigger(row, mask, mind):
    """The beam target if this row STARTS an order: the mind picks a solo nap, the cat is not on a
    beam and not already asleep (a sleeping cat's `Sleep` is a continue and its moves are masked),
    a known unoccupied beam sits within REACH, and a legal step toward it exists. Else None."""
    if mind != SLEEP_SOLO or row[L.SELF_IN_SUNBEAM] > 0.5:
        return None
    if int(row[L.SELF_ACTIVITY:L.SELF_ACTIVITY + 7].argmax()) == 2 and row[L.SELF_ACTIVITY + 2] > 0.5:
        return None
    kb = known_beam(row)
    if kb is None or kb[0] > REACH or kb[0] == 0:
        return None
    return kb[1] if step_toward(row, mask, kb[1]) is not None else None


class BeamPlanner:
    """Wraps a seat's policy forward. `__call__(rows, masks)` returns logits with the order's
    action forced (a large bonus on one legal index) where an order is active; the harness's
    masked argmax then takes it. State is per row index (one world per process)."""

    def __init__(self, fwd):
        self.fwd = fwd
        self.orders = {}          # row index -> {"target", "ticks", "stuck"}
        self.stats = {"orders": 0, "arrived": 0, "gave_up_stuck": 0, "gave_up_long": 0,
                      "gave_up_gone": 0, "released_emergency": 0, "forced_ticks": 0}

    def __call__(self, rows, masks):
        logits = np.array(self.fwd(rows), np.float32)
        for i in range(len(rows)):
            logits[i, :L.N_ACT] = self.overlay(i, rows[i], masks[i], logits[i, :L.N_ACT])
        return logits

    def overlay(self, i, row, mask, act_logits):
        mind = int(np.where(mask[:L.N_ACT], act_logits, -np.inf).argmax())
        in_beam = row[L.SELF_IN_SUNBEAM] > 0.5
        order = self.orders.get(i)
        if order is None:
            target = trigger(row, mask, mind)
            if target is None:
                return act_logits
            order = self.orders[i] = {"target": target, "ticks": 0, "stuck": 0}
            self.stats["orders"] += 1
        order["ticks"] += 1
        if row[NEED_EAT] >= EMERGENCY or row[NEED_DRINK] >= EMERGENCY:
            self.stats["released_emergency"] += 1; del self.orders[i]; return act_logits
        if me_pos(row) == order["target"] or in_beam:
            del self.orders[i]
            if mask[SLEEP_SOLO]:
                self.stats["arrived"] += 1; self.stats["forced_ticks"] += 1
                return self.force(act_logits, SLEEP_SOLO)
            return act_logits
        if order["ticks"] > MAX_TICKS:
            self.stats["gave_up_long"] += 1; del self.orders[i]; return act_logits
        kb = known_beam(row)
        if kb is None:
            self.stats["gave_up_gone"] += 1; del self.orders[i]; return act_logits
        order["target"] = kb[1]                       # re-aim at the nearest known beam each tick
        m = step_toward(row, mask, order["target"])
        if m is None:
            order["stuck"] += 1
            if order["stuck"] >= MAX_STUCK:
                self.stats["gave_up_stuck"] += 1; del self.orders[i]
            return act_logits
        order["stuck"] = 0
        self.stats["forced_ticks"] += 1
        return self.force(act_logits, m)

    @staticmethod
    def force(act_logits, index):
        out = np.array(act_logits, np.float32); out[index] = FORCE
        return out
