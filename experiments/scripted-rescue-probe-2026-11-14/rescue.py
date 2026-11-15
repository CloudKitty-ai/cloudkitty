#!/usr/bin/env python3
"""The scripted-rescue probe's overlays (DECLARATION.md §3, frozen; deviations entry 39). An overlay sits between a
seating's policy and the engine in `cert_harness_fog.run_one`: each tick it may replace a seat's ACT with one legal
act. It never sees or touches the message half. A measurement: an overlaid roster is never seated, served or a teacher.

  T  the rescue on the engine's facts   lost(j): cuddle >= 90, unpartnered, no other kitty within the vision radius
                                        (Manhattan); free(k): unpartnered, every hidden need < 70, happiness >= 70, on
                                        no mission (and not a mission's target: the lost cat is never overridden);
                                        each lost cat without a rescuer gets the nearest free cat (ties: lower index);
                                        the act: a legal partner act on the target (rest-with, sleep-with, groom), else
                                        the legal move that shortens the walk (the longer axis, then N, E, S, W), else
                                        the policy's act stands; release: the target partnered, her cuddle < 50, or a
                                        hidden need of the rescuer >= 90
  P  the placebo                        T's triggers, assignment and release on the same facts; the act is a walk to
                                        the decoy (the target's tile reflected through the rescuer's at assignment,
                                        clamped to the map); no partner act
  O  the rescue on the cat's own row    no engine state (refused if handed one): a friend heard and not seen whose
                                        want-cuddle intensity >= 0.90 is calling; free by the cat's own self block;
                                        walk to the row's call place, a legal partner act once she is in sight;
                                        release: she is seen partnered, her call leaves the window, or an own hidden
                                        need >= 0.90. Each cat decides alone.

`Overlay.act` returns the acts to send; `Overlay.arrays()` (per tick and seat: the policy's own act, the mission's
target or -1, whether the rule set the act) joins the leg's acts file, `Overlay.report()` the leg's row.
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "minifriend-phase2-2026-11-06"))
import p2_common as C  # noqa: E402,F401  (puts the layout and the replay on the path)
import obs_layout_v6 as L  # noqa: E402
import replay as RP  # noqa: E402

import cloudkitty  # noqa: E402

MENU = list(cloudkitty.ACTION_MENU)
MOVES = [MENU.index(f"move_{d}") for d in ("north", "east", "south", "west")]
STEP = np.array([(0, -1), (1, 0), (0, 1), (-1, 0)])        # grid.rs Position::step: north is y - 1
PARTNER = [[MENU.index(f"{a}_{r}") for r in range(4)] for a in ("rest_with_kitty", "sleep_with_kitty", "groom_kitty")]
PARTNER_ACTS = sorted(a for acts in PARTNER for a in acts)
CUD = L.NEED_KINDS.index("cuddle")
HIDDEN = 5                                                  # eat, drink, sleep, play, cuddle; bath is in plain sight
LOST_CUDDLE, DONE_CUDDLE, FREE_NEED, FREE_HAP, QUIT_NEED = 90.0, 50.0, 70.0, 70.0, 90.0
ROW0 = [L.BLOCKS[r][0] for r in range(4)]
WANT_CUDDLE = L.ROW_INTENSITY + L.WANT_KINDS.index("want_cuddle")
SEATINGS = {"rescue-T": "T", "rescue-P": "P", "rescue-O": "O"}     # the harness seatings that carry an overlay


def friend_row(observer, friend, roster=C.ROSTER):
    return [j for j in range(roster) if j != observer].index(friend)


def step_toward(delta, legal):
    """Index (0..3: N, E, S, W) of the legal move that shortens a walk of `delta` = (dx, dy) tiles: the longer axis
    first, then N, E, S, W. None when no legal move shortens it."""
    best = None
    for m in range(4):
        axis = 0 if STEP[m][0] else 1
        if legal[m] and STEP[m][axis] * delta[axis] > 0 and (best is None or abs(delta[axis]) > abs(delta[best[1]])):
            best = (m, axis)
    return None if best is None else best[0]


def row_place(row):
    """The (dx, dy) in tiles a kitty row's spatial group names (docs/encodings.md: bearing, linear, log distance)."""
    return row[L.ROW_BEARING:L.ROW_BEARING + 2] * np.expm1(row[L.ROW_LOG] * np.log1p(400.0))


class Overlay:
    def __init__(self, kind, width, height, radius, ticks, roster=C.ROSTER):
        assert kind in ("T", "P", "O"), kind
        self.kind, self.size, self.radius, self.R = kind, np.array([width, height]), radius, roster
        self.wants_state = kind != "O"
        self.t, self.open, self.missions = 0, {}, []
        self.policy = np.full((ticks, roster), -1, np.int16)
        self.target = np.full((ticks, roster), -1, np.int8)
        self.rule = np.zeros((ticks, roster), bool)

    # -- the facts rule (T, P) ------------------------------------------------------------------------------------
    def _facts(self, state, mk):
        needs, hap, pos, _a, partnered, _p, _d = RP.kitty_truth(state, self.R)
        tile = np.rint(pos * self.size).astype(int)
        dist = np.abs(tile[:, None] - tile[None]).sum(-1)
        for k, m in list(self.open.items()):
            j = m["target"]
            why = ("partnered" if partnered[j] else "relieved" if needs[j, CUD] < DONE_CUDDLE
                   else "rescuer_need" if needs[k, :HIDDEN].max() >= QUIT_NEED else None)
            if why:
                self._close(k, why)
        targets = {m["target"] for m in self.open.values()}
        for j in range(self.R):
            others = [k for k in range(self.R) if k != j]
            if j in targets or not (needs[j, CUD] >= LOST_CUDDLE and not partnered[j] and dist[j, others].min() > self.radius):
                continue
            free = [k for k in others if k not in self.open and k not in targets and not partnered[k]
                    and needs[k, :HIDDEN].max() < FREE_NEED and hap[k] >= FREE_HAP]
            if free:
                k = min(free, key=lambda k: (dist[j, k], k))
                decoy = np.clip(2 * tile[k] - tile[j], 0, self.size - 1)
                self._open(k, j, walk=int(dist[j, k]), decoy=decoy.tolist())
                targets.add(j)
        acts = {}
        for k, m in self.open.items():
            j = m["target"]
            if self.kind == "T":
                r = friend_row(k, j, self.R)
                acts[k] = next((a[r] for a in PARTNER if mk[k, a[r]]), None)
                goal = tile[j]
            else:
                goal = np.array(m["decoy"])
            if acts.get(k) is None:
                mv = step_toward(goal - tile[k], mk[k, MOVES])
                acts[k] = None if mv is None else MOVES[mv]
        return acts

    # -- the observation rule (O) ---------------------------------------------------------------------------------
    def _own_rows(self, ob, mk):
        others = [[j for j in range(self.R) if j != k] for k in range(self.R)]
        acts = {}
        for k in range(self.R):
            me = ob[k]
            rows = [me[o:o + L.KITTY_W] for o in ROW0]
            seen = [row[L.ROW_PRESENT] > 0.5 for row in rows]
            call = [row[WANT_CUDDLE] for row in rows]
            placed = [seen[r] or float(np.abs(rows[r][L.ROW_BEARING:L.ROW_LOG + 1]).sum()) > 1e-6 for r in range(4)]
            own = me[L.SELF_NEEDS:L.SELF_NEEDS + HIDDEN].max()             # float32 cells against float32 lines
            in_need = own >= np.float32(QUIT_NEED / 100)
            if k in self.open:
                r = others[k].index(self.open[k]["target"])
                why = ("partnered" if seen[r] and rows[r][L.ROW_PARTNERED] > 0.5 else "call_gone" if call[r] <= 0 or not placed[r]
                       else "rescuer_need" if in_need else None)
                if why:
                    self._close(k, why)
            if k not in self.open:
                free = me[L.SELF_PARTNERED] <= 0.5 and own < np.float32(FREE_NEED / 100) and me[L.SELF_HAPPINESS] >= np.float32(FREE_HAP / 100)
                calling = [r for r in range(4) if not seen[r] and placed[r] and call[r] >= np.float32(LOST_CUDDLE / 100)]
                if free and calling:
                    r = min(calling, key=lambda r: (float(np.abs(np.rint(row_place(rows[r]))).sum()), r))
                    place = np.rint(row_place(rows[r])).astype(int)
                    self._open(k, others[k][r], walk=int(np.abs(place).sum()), place=place.tolist())
            if k in self.open:
                r = others[k].index(self.open[k]["target"])
                acts[k] = next((a[r] for a in PARTNER if seen[r] and mk[k, a[r]]), None)
                if acts[k] is None:
                    mv = step_toward(np.rint(row_place(rows[r])).astype(int), mk[k, MOVES])
                    acts[k] = None if mv is None else MOVES[mv]
        return acts

    # -- the seam -------------------------------------------------------------------------------------------------
    def _open(self, k, j, **kw):
        self.open[k] = {"rescuer": k, "target": j, "open": self.t, **kw}

    def _close(self, k, why):
        self.missions.append({**self.open.pop(k), "close": self.t, "why": why})

    def act(self, state, ob, mk, a0):
        """The acts to send this tick: `a0` (the policy's own, (R,)) with each mission seat's act set by the rule when
        the rule names a legal one. `mk` is the tick's legal mask (R, >= 35); T and P read `state`, O must not get it."""
        if self.wants_state:
            assert state is not None, "the facts rule ran without the engine's state"
            acts = self._facts(state, mk)
        else:
            assert state is None, "the observation rule read the engine state"
            acts = self._own_rows(ob, mk)
        out = np.array(a0).copy()
        self.policy[self.t] = a0
        for k, m in self.open.items():
            self.target[self.t, k] = m["target"]
            if acts.get(k) is not None:
                out[k], self.rule[self.t, k] = acts[k], True
        self.t += 1
        return out

    def arrays(self):
        return {"policy_acts": self.policy[:self.t], "mission_target": self.target[:self.t], "rule_set": self.rule[:self.t]}

    def report(self):
        return {"kind": self.kind, "radius": self.radius,
                "missions": self.missions + [{**m, "close": None, "why": "open_at_end"} for m in self.open.values()],
                "mission_ticks": (self.target[:self.t] >= 0).sum(0).tolist(), "rule_set_ticks": self.rule[:self.t].sum(0).tolist()}


def make(seating, cfg, ticks):
    """The seating's overlay, or None for a seating that carries none."""
    kind = SEATINGS.get(seating)
    if kind is None:
        return None
    return Overlay(kind, cfg["world"]["width"], cfg["world"]["height"], cfg["vision"]["radius"], ticks, len(cfg["kitty"]))
