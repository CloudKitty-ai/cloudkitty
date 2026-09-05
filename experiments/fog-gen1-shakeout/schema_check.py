#!/usr/bin/env python3
"""Part A of PREREG.md (the schema-defect checklist) over a recorded trace.

    schema_check.py TRACE_DIR [--json OUT] [--policy-trace NPZ]

TRACE_DIR is a bc-collect `--trace` rollout directory (docs/encodings.md
§bc-collect): trace_obs.npy, trace_mask.npy, trace_kitty.npy,
trace_tick.npy, trace.jsonl (per tick: the start-of-tick snapshot every
observation was encoded from, the target tables, the tick's refusals and
the re-encode verdict) and meta.json. Every row A1-A18 re-derives what the
observation should say from the snapshot and compares. Offsets and kind
orders come from obs_layout_v5 by name; nothing here counts to a cell.

What the snapshot cannot settle: a meow is stamped mid-tick over the
speaker's live view (world.rs, the apply loop), after its own move. The
speaker's position at emission is its position in the NEXT snapshot;
element positions are the current snapshot's (nothing spawns, moves or
expires until the environment phase); a bowl emptied earlier in the same
tick and a friend that entered a scene earlier in the apply order are the
only facts neither snapshot shows. A8 and A9 read exactly where they can
and report the rest as "soft", never as green.

Exit status: 1 on any red among the stop rows (PREREG reading rule), else
0. Guard: test_schema_check.py.
"""
import argparse
import fnmatch
import json
import math
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "attn-oracle-2026-08-15"))
from obs_layout_v5 import (  # noqa: E402
    BLOCKS, COUNTS, ELEMENT_KINDS, HEAD_KINDS, HERE_KINDS, KITTY_SPAN,
    KITTY_W, MEMORY_SLOT, MSG_BLOCK, N_ACT, NEED_KINDS, OBS_DIM,
    ROW_ACTIVITY, ROW_ANSWERS_ME, ROW_DIST, ROW_DX, ROW_DY, ROW_INTENSITY,
    ROW_MSG_BLOCK, ROW_NEEDS, ROW_PRESENT, ROW_SCENE_AGE, ROW_SUNBEAM_BIT,
    ROW_WATER_BIT, SCENE_AGE_NORMALISER, SELF_ACTIVITY, SELF_IN_SUNBEAM,
    SELF_IN_WATER, SELF_MEMORY, SELF_MSG_BLOCK, SELF_NEEDS, SELF_SCENE_AGE,
    SLOT_DX, SLOT_DY, SLOT_PRESENT, STALENESS_NORMALISER, WANT_FOR_HERE,
    WANT_KINDS, WIDTHS)

ATOL = 1e-5
STOP_ROWS = {"A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A12", "A14",
             "A15", "A16", "A17", "A18"}
NEED_OF_WANT = {"want_eat": "eat", "want_drink": "drink", "want_play": "play",
                "want_cuddle": "cuddle", "want_bath": "bath",
                "want_sleep": "sleep"}
CRITTER_KINDS = [k for k in ELEMENT_KINDS if k in ("bug", "greeble")]
N_KITTY = COUNTS["kitty"]
SELF_W = dict(WIDTHS)["self"]


# --------------------------------------------------------------------- trace

@dataclass
class Trace:
    obs: np.ndarray            # [rows, OBS_DIM] f32
    mask: np.ndarray           # [rows, N_ACT + 16] bool
    kitty: np.ndarray          # [rows] kitty id
    tick: np.ndarray           # [rows] tick
    lines: list                # per tick dict: snapshot, tables, refusals, reencode
    meta: dict
    cfg: dict
    row_of: dict = field(default_factory=dict)   # (tick, kitty) -> row

    @property
    def radius(self):
        return int(self.meta["vision_radius"])

    @property
    def window(self):
        return int(self.cfg["meow"]["digest_window_ticks"])

    @property
    def cooldown(self):
        return int(self.cfg["meow"]["recent_window_ticks"])

    @property
    def margin(self):
        """[meow] relief_memory_margin (spec 050): a remembered tile is
        relief only within radius + margin Manhattan; key absent = None,
        the unbounded rule."""
        m = self.cfg["meow"].get("relief_memory_margin")
        return None if m is None else int(m)

    def snap(self, i):
        return self.lines[i]["snapshot"]

    def row(self, tick, kitty):
        return self.obs[self.row_of[(int(tick), int(kitty))]]


def load_trace(d, config=None):
    d = Path(d)
    meta = json.loads((d / "meta.json").read_text())
    assert meta.get("trace"), f"{d} was not recorded with --trace"
    assert meta["observation_schema"] == 5 and meta["obs_width"] == OBS_DIM, meta
    cfg_path = Path(config) if config else Path(meta["config"])
    with open(cfg_path, "rb") as f:
        cfg = tomllib.load(f)
    obs = np.load(d / "trace_obs.npy").astype(np.float32)
    mask = np.load(d / "trace_mask.npy").astype(bool)
    kitty = np.load(d / "trace_kitty.npy")
    tick = np.load(d / "trace_tick.npy")
    lines = [json.loads(l) for l in (d / "trace.jsonl").read_text().splitlines()]
    tr = Trace(obs, mask, kitty, tick, lines, meta, cfg)
    tr.row_of = {(int(t), int(k)): i for i, (t, k) in enumerate(zip(tick, kitty))}
    assert len(lines) == len(set(tick.tolist())), "one trace line per tick"
    assert [l["tick"] for l in lines] == sorted(set(tick.tolist()))
    return tr


# ------------------------------------------------------------ engine in python

def kitties_by_id(snap):
    return {k["id"]: k for k in snap["kitties"]}


def visible(a, b, r):
    dx, dy = a["x"] - b["x"], a["y"] - b["y"]
    return dx * dx + dy * dy <= r * r


def manhattan(a, b):
    return abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])


def adjacent(a, b):
    return manhattan(a, b) <= 1


def audible(m, now, window):
    return m["tick"] < now and now - m["tick"] < window


def elements_of(snap, kind):
    return [e for e in snap["elements"] if e["kind"] == kind]


def stocked(e):
    return e["kind"] != "chow" or e.get("servings", 0) > 0


def row_state(snap, me, friend, r, window):
    """Seen / Heard(pos) / Silent for `friend` as seen by `me` (FR-012)."""
    if visible(me["pos"], friend["pos"], r):
        return "seen", friend["pos"]
    calls = [m for m in snap["recent_meows"]
             if m["kitty_id"] == friend["id"] and audible(m, snap["tick"], window)]
    if calls:
        return "heard", max(calls, key=lambda m: m["tick"])["pos"]
    return "silent", None


def msg_block(snap, speaker, window, cooldown, with_intensity):
    now = snap["tick"]
    max_calls = max(window // max(cooldown, 1), 1)
    mine = [m for m in snap["recent_meows"]
            if m["kitty_id"] == speaker and audible(m, now, window)]
    out = []
    for kind in HEAD_KINDS:
        of_kind = [m for m in mine if m["kind"] == kind]
        if of_kind:
            freshest = max(m["tick"] for m in of_kind)
            out.append(min(max(1.0 - (now - freshest) / window, 0.0), 1.0))
        else:
            out.append(0.0)
        out.append(min(len(of_kind) / max_calls, 1.0))
    if with_intensity:
        for kind in WANT_KINDS:
            of_kind = [m for m in mine if m["kind"] == kind]
            out.append(min(max(max(of_kind, key=lambda m: m["tick"])["intensity"], 0.0), 1.0)
                       if of_kind else 0.0)
    return out


def freshest_tick(snap, speaker, kind, window):
    ts = [m["tick"] for m in snap["recent_meows"]
          if m["kitty_id"] == speaker and m["kind"] == kind
          and audible(m, snap["tick"], window)]
    return max(ts) if ts else None


def answers_me(snap, observer, friend, window):
    bits = []
    for here in HERE_KINDS:
        my_want = freshest_tick(snap, observer, WANT_FOR_HERE[here], window)
        their_here = freshest_tick(snap, friend, here, window)
        bits.append(1.0 if (my_want is not None and their_here is not None
                            and their_here > my_want) else 0.0)
    return bits


def scene_age(k, tick):
    clock = k.get("activity_clock")
    if clock is None:
        return 0.0
    return min((tick - clock["started"] + 1) / SCENE_AGE_NORMALISER, 1.0)


def tile_holds(snap, pos, kind):
    return any(e["kind"] == kind and e["pos"] == pos for e in snap["elements"])


def need_rate(cfg, kitty_id, need):
    """Config::need_rate_for: the [kitty.needs] override, else [needs]."""
    for k in cfg.get("kitty", []):
        if k.get("id") == kitty_id and need in k.get("needs", {}):
            return float(k["needs"][need])
    return float(cfg["needs"][need])


def refresh_memory(prev, origin, elements, r, timeout, seen_at):
    """world.rs::refresh_memories for one cat: sight-only, nearest by
    (Manhattan, id), refuted when the remembered tile is in view."""
    out = []
    for slot, kind in enumerate(ELEMENT_KINDS):
        seen = [e for e in elements if e["kind"] == kind and visible(origin, e["pos"], r)]
        if seen:
            e = min(seen, key=lambda e: (manhattan(origin, e["pos"]), e["id"]))
            out.append({"pos": e["pos"], "last_seen": seen_at})
        elif prev[slot] is not None:
            refuted = visible(origin, prev[slot]["pos"], r)
            expired = timeout > 0 and seen_at - prev[slot]["last_seen"] > timeout
            out.append(None if (refuted or expired) else prev[slot])
        else:
            out.append(None)
    return out


class Lattice:
    """crate::explore::Lattice."""

    def __init__(self, width, height, radius):
        self.xs, self.ys = self.axis(width, radius), self.axis(height, radius)

    @staticmethod
    def axis(length, radius):
        inset = math.floor(radius / math.sqrt(2))
        spacing = max(math.floor(radius * math.sqrt(2)), 1)
        last = max(length - 1, 0)
        if last < 2 * inset + 1:
            return [last // 2]
        span = last - 2 * inset
        n = -(-span // spacing) + 1
        return [inset + math.floor(k * span / (n - 1) + 0.5) for k in range(n)]

    def snake_len(self):
        return len(self.xs) * len(self.ys)

    def cycle_len(self):
        n = self.snake_len()
        return 2 * n - 2 if n >= 2 else 1

    def snake(self, i):
        nx = len(self.xs)
        row, col = divmod(i, nx)
        x = self.xs[col] if row % 2 == 0 else self.xs[nx - 1 - col]
        return {"x": x, "y": self.ys[row]}

    def waypoint(self, index):
        n = self.snake_len()
        i = index % self.cycle_len()
        return self.snake(i) if i < n else self.snake(2 * n - 2 - i)


def kitty_rows(obs_row):
    return obs_row[KITTY_SPAN[0]:KITTY_SPAN[1]].reshape(N_KITTY, KITTY_W)


def col_name(i):
    """A human name for observation column i (A1's constant list)."""
    if i < SELF_W:
        if i < SELF_SCENE_AGE:
            return f"self.schema4[{i}]"
        if i == SELF_SCENE_AGE:
            return "self.scene_age"
        if i < SELF_MEMORY:
            k, part = divmod(i - SELF_MSG_BLOCK, 2)
            return f"self.msg.{HEAD_KINDS[k]}.{'recency' if part == 0 else 'rate'}"
        k, part = divmod(i - SELF_MEMORY, MEMORY_SLOT)
        return f"self.memory.{ELEMENT_KINDS[k]}.{['present', 'dx', 'dy', 'staleness'][part]}"
    if i < KITTY_SPAN[1]:
        k, c = divmod(i - KITTY_SPAN[0], KITTY_W)
        if c < ROW_WATER_BIT:
            return f"kitty{k}.schema4[{c}]"
        if c < ROW_MSG_BLOCK:
            return f"kitty{k}.{['water_bit', 'sunbeam_bit', 'scene_age'][c - ROW_WATER_BIT]}"
        if c < ROW_INTENSITY:
            j, part = divmod(c - ROW_MSG_BLOCK, 2)
            return f"kitty{k}.msg.{HEAD_KINDS[j]}.{'recency' if part == 0 else 'rate'}"
        if c < ROW_ANSWERS_ME:
            return f"kitty{k}.want.{WANT_KINDS[c - ROW_INTENSITY]}"
        return f"kitty{k}.answers_me.{HERE_KINDS[c - ROW_ANSWERS_ME]}"
    if i == OBS_DIM - 1:
        return "clock"
    for j, (off, w) in enumerate(BLOCKS[N_KITTY:]):
        if off <= i < off + w:
            return f"element_block{j}[{i - off}]"
    return f"col{i}"


def element_slots(tr, obs_row):
    """(kind, slot values) for chow, water, sunbeam, critter slots."""
    kinds = ["chow"] * COUNTS["chow"] + ["water"] * COUNTS["water"] + \
        ["sunbeam"] * COUNTS["sunbeam"] + ["critter"] * COUNTS["critter"]
    return [(kind, obs_row[off:off + w])
            for kind, (off, w) in zip(kinds, BLOCKS[N_KITTY:])]


# ------------------------------------------------------------------- findings

@dataclass
class Finding:
    row: str
    status: str            # ok | RED | unproven | n/a
    summary: str
    detail: dict = field(default_factory=dict)


def ok_or_red(row, bad, summary, detail=None):
    return Finding(row, "RED" if bad else "ok", summary, detail or {})


OVERDUE_FACTOR = 5.0   # a rare column is red once the corpus is this many expected waits long


def declared_groups(declared_constant):
    """`{reason: patterns}` for structural groups and `{reason: spec}` for
    rare ones, from declared_constant.json or a bare list. A list value is
    structural; an object is rare when it carries `expected_per_1000`
    (with `patterns`, `wiring`), otherwise structural with `patterns` and
    optional flags (`a17_exempt`, see a17_exempt_patterns)."""
    structural, rare = {}, {}
    if isinstance(declared_constant, dict):
        for reason, v in declared_constant.items():
            if isinstance(v, list):
                structural[reason] = v
            elif isinstance(v, dict) and isinstance(v.get("patterns"), list):
                (rare if "expected_per_1000" in v else structural)[reason] = (
                    v if "expected_per_1000" in v else v["patterns"])
    else:
        structural["declared"] = list(declared_constant)
    return structural, rare


def a17_exempt_patterns(declared_constant):
    """`{reason: patterns}` for the groups whose columns may move under a
    policy that the scripted anchor never moved: every RARE group, plus
    structural groups flagged `a17_exempt` (constant by ROSTER behaviour,
    not by law: the anchor never says mew, a policy may)."""
    out = {}
    if isinstance(declared_constant, dict):
        for reason, v in declared_constant.items():
            if isinstance(v, dict) and isinstance(v.get("patterns"), list) and (
                    "expected_per_1000" in v or v.get("a17_exempt")):
                out[reason] = v["patterns"]
    return out


def matches_any(name, groups):
    return any(fnmatch.fnmatchcase(name, p)
               for pats in groups.values() for p in pats)


def check_a1(tr, declared_constant=()):
    """Zero-variance columns must each match a declared pattern
    (declared_groups). A structural match is ok for any corpus length. A
    rare match reads unproven, and red once the corpus is OVERDUE_FACTOR
    expected waits long (`expected_per_1000` setting events per 1000
    ticks; null never turns red). A reason matching no constant column is
    stale: the column moved, the good outcome for a rare group."""
    var = tr.obs.var(axis=0)
    constant = [col_name(i) for i in np.flatnonzero(var == 0)]
    structural, rare = declared_groups(declared_constant)
    n_ticks = len(tr.lines)
    matched, stale, unproven, overdue = {}, [], [], []
    for reason, pats in structural.items():
        hits = [c for c in constant if any(fnmatch.fnmatchcase(c, p) for p in pats)]
        matched[reason] = len(hits)
        if not hits:
            stale.append(reason)
    for reason, spec in rare.items():
        hits = [c for c in constant if any(fnmatch.fnmatchcase(c, p) for p in spec["patterns"])]
        matched[reason] = len(hits)
        if not hits:
            stale.append(reason)
            continue
        rate = spec.get("expected_per_1000")
        if rate and n_ticks * rate / 1000.0 >= OVERDUE_FACTOR:
            overdue.extend(hits)
        else:
            unproven.extend(hits)
    rare_pats = {k: v["patterns"] for k, v in rare.items()}
    extra = sorted(c for c in constant
                   if not matches_any(c, structural) and not matches_any(c, rare_pats))
    status = "RED" if extra or overdue else "unproven" if unproven else "ok"
    return Finding("A1", status,
                   f"{len(constant)} constant columns, {len(extra)} undeclared, "
                   f"{len(overdue)} rare overdue, {len(unproven)} rare unproven, "
                   f"{len(stale)} stale reasons",
                   {"constant": constant, "undeclared": extra, "overdue": overdue,
                    "unproven": unproven, "matched": matched, "stale": stale})


def check_a2(tr):
    r, timeout = tr.radius, int(tr.cfg["vision"].get("memory_timeout_ticks", 0))
    W, H = tr.snap(0)["width"], tr.snap(0)["height"]
    drift, sets, refutations, token_bad = 0, 0, 0, 0
    for i in range(len(tr.lines)):
        snap = tr.snap(i)
        prev = kitties_by_id(tr.snap(i - 1)) if i > 0 else None
        for k in snap["kitties"]:
            if prev is not None:
                want = refresh_memory(prev[k["id"]]["memory"], k["pos"], snap["elements"],
                                      r, timeout, snap["tick"])
                if want != k["memory"]:
                    drift += 1
                for a, b in zip(prev[k["id"]]["memory"], k["memory"]):
                    sets += a is None and b is not None
                    refutations += a is not None and b is None
            # The self memory token (FR-009) against the snapshot slot.
            tok = tr.row(snap["tick"], k["id"])[SELF_MEMORY:SELF_MEMORY + len(ELEMENT_KINDS) * MEMORY_SLOT]
            want = []
            for slot in k["memory"]:
                if slot is None:
                    want += [0.0] * MEMORY_SLOT
                else:
                    want += [1.0, (slot["pos"]["x"] - k["pos"]["x"]) / W,
                             (slot["pos"]["y"] - k["pos"]["y"]) / H,
                             min((snap["tick"] - slot["last_seen"]) / STALENESS_NORMALISER, 1.0)]
            token_bad += not np.allclose(tok, want, atol=ATOL)
    bad = drift or token_bad
    f = ok_or_red("A2", bad, f"memory drift {drift}, token mismatches {token_bad}; "
                  f"set-events {sets}, refutations {refutations}",
                  {"drift": drift, "token_bad": token_bad, "sets": sets,
                   "refutations": refutations})
    if not bad and refutations == 0:
        f.status, f.summary = "unproven", f.summary + " (refutation path never emitted)"
    return f


def check_a3(tr):
    r, window = tr.radius, tr.window
    W, H = tr.snap(0)["width"], tr.snap(0)["height"]
    maxd = W + H
    bad, seen_n, masked_n, edge_n = 0, 0, 0, 0
    for line in tr.lines:
        snap = line["snapshot"]
        byid = kitties_by_id(snap)
        for me_id, table in line["tables"].items():
            me = byid[int(me_id)]
            rows = kitty_rows(tr.row(snap["tick"], me["id"]))
            for k, fid in enumerate(table["kitties"]):
                row = rows[k]
                if fid is None:
                    bad += bool(np.any(row != 0))
                    continue
                friend = byid[fid]
                geom_visible = visible(me["pos"], friend["pos"], r)
                dx2 = (me["pos"]["x"] - friend["pos"]["x"]) ** 2 + (me["pos"]["y"] - friend["pos"]["y"]) ** 2
                edge_n += dx2 == r * r
                if geom_visible:
                    seen_n += 1
                    want = [1.0, (friend["pos"]["x"] - me["pos"]["x"]) / W,
                            (friend["pos"]["y"] - me["pos"]["y"]) / H,
                            manhattan(me["pos"], friend["pos"]) / maxd]
                    want += [friend["needs"][n] / 100.0 for n in NEED_KINDS]
                    bad += not np.allclose(row[:ROW_NEEDS + len(NEED_KINDS)], want, atol=ATOL)
                else:
                    masked_n += 1
                    # present 0 and every knowledge cell (needs .. scene age) 0
                    bad += row[ROW_PRESENT] != 0 or np.any(row[ROW_NEEDS:ROW_MSG_BLOCK] != 0)
    f = ok_or_red("A3", bad, f"{bad} rows disagree with the r={r} disc; "
                  f"seen {seen_n}, masked {masked_n}, on-edge {edge_n}",
                  {"bad": bad, "seen": seen_n, "masked": masked_n, "edge": edge_n})
    if not bad and (seen_n == 0 or masked_n == 0 or edge_n == 0):
        f.status = "unproven"
    return f


def check_a4(tr):
    r, window = tr.radius, tr.window
    W, H = tr.snap(0)["width"], tr.snap(0)["height"]
    heard, bad_pos, bad_stamp, moved_between = 0, 0, 0, 0
    next_pos = {}   # (tick, kitty) -> pos in the following snapshot
    for line in tr.lines[1:]:
        for k in line["snapshot"]["kitties"]:
            next_pos[(line["snapshot"]["tick"] - 1, k["id"])] = k["pos"]
    for line in tr.lines:
        snap = line["snapshot"]
        byid = kitties_by_id(snap)
        # every meow's pos is the speaker's position at emission = its
        # position in the next snapshot (FR-040; moves apply before words)
        for m in snap["recent_meows"]:
            p = next_pos.get((m["tick"], m["kitty_id"]))
            if p is not None and p != m["pos"]:
                bad_stamp += 1
        for me_id, table in line["tables"].items():
            me = byid[int(me_id)]
            rows = kitty_rows(tr.row(snap["tick"], me["id"]))
            for k, fid in enumerate(table["kitties"]):
                if fid is None:
                    continue
                state, pos = row_state(snap, me, byid[fid], r, window)
                if state != "heard":
                    continue
                heard += 1
                moved_between += pos != byid[fid]["pos"]
                want = [0.0, (pos["x"] - me["pos"]["x"]) / W, (pos["y"] - me["pos"]["y"]) / H,
                        manhattan(me["pos"], pos) / (W + H)]
                bad_pos += not np.allclose(rows[k][:ROW_NEEDS], want, atol=ATOL)
    bad = bad_pos or bad_stamp
    f = ok_or_red("A4", bad, f"heard rows {heard}: {bad_pos} carry a wrong call position; "
                  f"{bad_stamp} meows stamped off the speaker's tile; "
                  f"{moved_between} heard rows point where the cat no longer is",
                  {"heard": heard, "bad_pos": bad_pos, "bad_stamp": bad_stamp,
                   "moved_between": moved_between})
    if not bad and moved_between == 0:
        f.status = "unproven"   # a static pos and a live pos are indistinguishable
    return f


def check_a5(tr):
    r, window, cooldown = tr.radius, tr.window, tr.cooldown
    bad_self, bad_row, heard_zero, heard, heard_off_head = 0, 0, 0, 0, 0
    for line in tr.lines:
        snap = line["snapshot"]
        byid = kitties_by_id(snap)
        for me_id, table in line["tables"].items():
            me = byid[int(me_id)]
            obs = tr.row(snap["tick"], me["id"])
            want = msg_block(snap, me["id"], window, cooldown, False)
            bad_self += not np.allclose(obs[SELF_MSG_BLOCK:SELF_MSG_BLOCK + MSG_BLOCK], want, atol=ATOL)
            rows = kitty_rows(obs)
            for k, fid in enumerate(table["kitties"]):
                if fid is None:
                    continue
                state, _ = row_state(snap, me, byid[fid], r, window)
                if state == "silent":
                    continue
                want = msg_block(snap, fid, window, cooldown, False)
                got = rows[k][ROW_MSG_BLOCK:ROW_INTENSITY]
                bad_row += not np.allclose(got, want, atol=ATOL)
                if state == "heard":
                    heard += 1
                    # `wait_for_me` is the engine's own word, outside
                    # HEAD_KINDS: a row heard only through it has a position
                    # and an empty digest. Counted apart, not as a defect.
                    in_head = any(m["kitty_id"] == fid and m["kind"] in HEAD_KINDS
                                  and audible(m, snap["tick"], window) for m in snap["recent_meows"])
                    if not in_head:
                        heard_off_head += 1
                    else:
                        heard_zero += not np.any(got[0::2] > 0)
    bad = bad_self or bad_row or heard_zero
    return ok_or_red("A5", bad, f"self blocks wrong {bad_self}, friend blocks wrong {bad_row}, "
                     f"heard rows with zero recency {heard_zero}/{heard} "
                     f"(heard through wait_for_me only: {heard_off_head})",
                     {"bad_self": bad_self, "bad_row": bad_row, "heard_zero": heard_zero,
                      "heard": heard, "heard_off_head": heard_off_head})


def check_a6(tr):
    r, window, cooldown = tr.radius, tr.window, tr.cooldown
    bad_cells, off_need, wants, rows_nonzero = 0, 0, 0, 0
    nxt = {}
    for line in tr.lines[1:]:
        for k in line["snapshot"]["kitties"]:
            nxt[(line["snapshot"]["tick"] - 1, k["id"])] = k
    for i, line in enumerate(tr.lines):
        snap = line["snapshot"]
        byid = kitties_by_id(snap)
        # every want stamp lies between the caller's need at the start and
        # end of its tick (stamped mid-tick, after its own action)
        for m in snap["recent_meows"]:
            if m["kind"] not in WANT_KINDS or m["tick"] != snap["tick"] - 1:
                continue
            wants += 1
            k1 = nxt.get((m["tick"], m["kitty_id"]))
            k0 = kitties_by_id(tr.snap(i - 1)).get(m["kitty_id"]) if i > 0 else None
            if k0 is None or k1 is None:
                continue
            # stamped after the caller's own action and before phase 4's
            # rise (world.rs advance_needs: one configured rate per (cat,
            # need), plus the bath gain on a water tile scaled by
            # Config::bath_ratio = own rate / [needs] bath), so the stamp
            # lies in [min(start, end) - rise, max(start, end)]
            need = NEED_OF_WANT[m["kind"]]
            rise = need_rate(tr.cfg, m["kitty_id"], need)
            if need == "bath":
                base = float(tr.cfg["needs"]["bath"])
                ratio = rise / base if base > 0 else 1.0
                rise += float(tr.cfg["water"].get("bath_gain", 0.0)) * ratio
            lo = (min(k0["needs"][need], k1["needs"][need]) - rise) / 100.0
            hi = max(k0["needs"][need], k1["needs"][need]) / 100.0
            off_need += not (lo - 1e-3 <= m["intensity"] <= min(hi, 1.0) + 1e-3)
        for me_id, table in line["tables"].items():
            me = byid[int(me_id)]
            rows = kitty_rows(tr.row(snap["tick"], me["id"]))
            for k, fid in enumerate(table["kitties"]):
                if fid is None:
                    continue
                state, _ = row_state(snap, me, byid[fid], r, window)
                if state == "silent":
                    continue
                want = msg_block(snap, fid, window, cooldown, True)[MSG_BLOCK:]
                got = rows[k][ROW_INTENSITY:ROW_ANSWERS_ME]
                rows_nonzero += bool(np.any(got > 0))
                bad_cells += not np.allclose(got, want, atol=ATOL)
    bad = bad_cells or off_need
    f = ok_or_red("A6", bad, f"intensity cells wrong {bad_cells}; {off_need}/{wants} want stamps "
                  f"outside the caller's [start, end] need; rows with intensity {rows_nonzero}",
                  {"bad_cells": bad_cells, "off_need": off_need, "wants": wants,
                   "rows_nonzero": rows_nonzero})
    if not bad and rows_nonzero == 0:
        f.status = "unproven"
    return f


def check_a7(tr):
    r, window = tr.radius, tr.window
    bad, ones, replies = 0, 0, 0
    seen_meows = set()
    for line in tr.lines:
        snap = line["snapshot"]
        byid = kitties_by_id(snap)
        for m in snap["recent_meows"]:
            key = (m["tick"], m["kitty_id"], m["kind"])
            if m.get("reply") and key not in seen_meows:
                replies += 1
            seen_meows.add(key)
        for me_id, table in line["tables"].items():
            me = byid[int(me_id)]
            rows = kitty_rows(tr.row(snap["tick"], me["id"]))
            for k, fid in enumerate(table["kitties"]):
                if fid is None:
                    continue
                state, _ = row_state(snap, me, byid[fid], r, window)
                want = answers_me(snap, me["id"], fid, window) if state != "silent" else [0.0] * 4
                got = rows[k][ROW_ANSWERS_ME:ROW_ANSWERS_ME + len(HERE_KINDS)]
                ones += int(np.sum(got > 0))
                bad += not np.array_equal(got, want)
    f = ok_or_red("A7", bad, f"answers-me rows wrong {bad}; bits set {ones}; "
                  f"reply-stamped heres {replies}",
                  {"bad": bad, "ones": ones, "replies": replies})
    if not bad and ones == 0:
        f.status = "unproven"
    return f


def meows_emitted_at(tr, i):
    """Meows stamped during tick i (they surface in snapshot i+1)."""
    if i + 1 >= len(tr.lines):
        return []
    t = tr.snap(i)["tick"]
    return [m for m in tr.snap(i + 1)["recent_meows"] if m["tick"] == t]


def check_a8(tr):
    r, window = tr.radius, tr.window
    heres, hard, soft, replies = 0, 0, 0, 0
    for i in range(len(tr.lines) - 1):
        snap, after = tr.snap(i), tr.snap(i + 1)
        pos_after = {k["id"]: k["pos"] for k in after["kitties"]}
        for m in meows_emitted_at(tr, i):
            if m["kind"] not in HERE_KINDS:
                continue
            heres += 1
            replies += bool(m["reply"])
            want = WANT_FOR_HERE[m["kind"]]
            audible_want = any(x["kind"] == want and x["kitty_id"] != m["kitty_id"]
                               and audible(x, snap["tick"], window)
                               for x in snap["recent_meows"])
            speaker = pos_after[m["kitty_id"]]
            kinds = CRITTER_KINDS if m["kind"] == "here_critter" else \
                [{"here_food": "chow", "here_water": "water", "here_sunbeam": "sunbeam"}[m["kind"]]]
            referent = any(e["kind"] in kinds and stocked(e) and visible(speaker, e["pos"], r)
                           for e in snap["elements"])
            expect = audible_want and referent
            if bool(m["reply"]) == expect:
                continue
            # The one fact no snapshot shows: a bowl emptied earlier this tick.
            if m["kind"] == "here_food" and not m["reply"] and expect:
                soft += 1
            else:
                hard += 1
    f = ok_or_red("A8", hard, f"heres {heres}, replies {replies}; stamp rule broken {hard} "
                  f"(soft/emptied-bowl {soft})",
                  {"heres": heres, "replies": replies, "hard": hard, "soft": soft})
    if not hard and replies == 0:
        f.status = "unproven"
    return f


def top_need(needs):
    """needs.rs::highest_pressure: strict `>` scanning NeedKind::ALL in
    order, so a tie goes to the earlier kind (eat < drink < sleep < play
    < cuddle < bath). Ties are common: needs start equal and eat, drink
    and sleep share a rate until one is relieved."""
    best = NEED_KINDS[0]
    for kind in NEED_KINDS[1:]:
        if needs[kind] > needs[best]:
            best = kind
    return best


def relief_known(want, kitty, snap, pos, r, margin=None):
    """meow.rs::known_relief read from one snapshot at `pos`. A remembered
    tile counts only within r + margin Manhattan of `pos` (inclusive);
    margin None is the unbounded rule."""
    def within_reach(slot):
        return slot is not None and (margin is None or manhattan(pos, slot["pos"]) <= r + margin)
    remembered = {k: within_reach(kitty["memory"][j]) for j, k in enumerate(ELEMENT_KINDS)}
    vis = lambda kind: any(e["kind"] == kind and visible(pos, e["pos"], r) for e in snap["elements"])  # noqa: E731
    idle_friend = any(k["id"] != kitty["id"] and k.get("activity_clock") is None
                      and visible(pos, k["pos"], r) for k in snap["kitties"])
    if want == "want_eat":
        return any(e["kind"] == "chow" and stocked(e) and visible(pos, e["pos"], r)
                   for e in snap["elements"]) or remembered["chow"]
    if want == "want_drink":
        return vis("water") or remembered["water"]
    if want == "want_cuddle":
        return idle_friend
    if want == "want_play":
        return idle_friend or any(vis(k) for k in CRITTER_KINDS) or any(remembered[k] for k in CRITTER_KINDS)
    return False   # bath, sleep


def check_a9(tr):
    r = tr.radius
    wants, hard, soft = 0, 0, {"armed": 0, "top": 0, "relief": 0}
    for i in range(len(tr.lines) - 1):
        snap, after = tr.snap(i), tr.snap(i + 1)
        k0s, k1s = kitties_by_id(snap), kitties_by_id(after)
        for m in meows_emitted_at(tr, i):
            if m["kind"] not in WANT_KINDS:
                continue
            wants += 1
            need = NEED_OF_WANT[m["kind"]]
            k0, k1 = k0s[m["kitty_id"]], k1s[m["kitty_id"]]
            armed = [need in k["announce_armed"] for k in (k0, k1)]
            top = [top_need(k["needs"]) == need for k in (k0, k1)]
            # memory is the start snapshot's (refreshed only in the
            # environment phase); sight from the post-move tile
            relief = [relief_known(m["kind"], k0, snap, k0["pos"], r, tr.margin),
                      relief_known(m["kind"], k0, snap, k1["pos"], r, tr.margin)]
            if m["kind"] == "want_bath":
                checks = {"armed": armed}
            else:
                checks = {"armed": armed, "top": top, "relief": [not x for x in relief]}
            for name, pair in checks.items():
                if not any(pair):
                    hard += 1          # false at both ends of the tick
                elif not all(pair):
                    soft[name] += 1    # mid-tick ambiguity
    f = ok_or_red("A9", hard, f"wants {wants}; law violated at both tick ends {hard}; "
                  f"mid-tick ambiguous {soft}",
                  {"wants": wants, "hard": hard, "soft": soft})
    if not hard and wants == 0:
        f.status = "unproven"
    return f


def lattice_coverage(W, H, r):
    lat = Lattice(W, H, r)
    covered = np.zeros((W, H), bool)
    for i in range(lat.cycle_len()):
        wp = lat.waypoint(i)
        for x in range(W):
            for y in range(H):
                if (x - wp["x"]) ** 2 + (y - wp["y"]) ** 2 <= r * r:
                    covered[x, y] = True
    return int((~covered).sum()), lat


def check_a10(tr):
    W, H, r = tr.snap(0)["width"], tr.snap(0)["height"], tr.radius
    uncovered = {rr: lattice_coverage(W, H, rr)[0] for rr in (2, 3, 4, 5, r)}
    lat = Lattice(W, H, r)
    bad_index, advances, blind, blind_closer = 0, 0, 0, 0
    for i in range(1, len(tr.lines)):
        prev, snap = kitties_by_id(tr.snap(i - 1)), tr.snap(i)
        positions = {k["id"]: k["pos"] for k in snap["kitties"]}
        for k in snap["kitties"]:
            idx = prev[k["id"]]["explore_waypoint"]
            wp = lat.waypoint(idx)
            held = any(o != k["id"] and p == wp for o, p in positions.items())
            expect = (idx + 1) % lat.cycle_len() if (k["pos"] == wp or (held and adjacent(k["pos"], wp))) else idx
            bad_index += k["explore_waypoint"] != expect
            advances += expect != idx
            # blind: nothing remembered, nothing in view, idle -> the next
            # step should not move away from the waypoint (reported, not
            # asserted: the anchor's other drives also read as idle)
            p = prev[k["id"]]
            nothing_seen = not any(visible(p["pos"], e["pos"], r) for e in tr.snap(i - 1)["elements"])
            if all(s is None for s in p["memory"]) and nothing_seen and p["activity"].get("state") == "idle":
                blind += 1
                wp0 = lat.waypoint(idx)
                blind_closer += manhattan(k["pos"], wp0) <= manhattan(p["pos"], wp0)
    bad = bad_index or uncovered[r]
    return ok_or_red("A10", bad, f"uncovered tiles by radius {uncovered}; index off-rule {bad_index}, "
                     f"advances {advances}; blind idle steps {blind}, not-away {blind_closer}",
                     {"uncovered": uncovered, "bad_index": bad_index, "advances": advances,
                      "blind": blind, "blind_closer": blind_closer,
                      "lattice": {"xs": lat.xs, "ys": lat.ys}})


def check_a11(tr):
    r, window = tr.radius, tr.window
    bad_self, bad_row, bad_climb = 0, 0, 0
    for i, line in enumerate(tr.lines):
        snap = line["snapshot"]
        byid = kitties_by_id(snap)
        prev = kitties_by_id(tr.snap(i - 1)) if i > 0 else {}
        for me_id, table in line["tables"].items():
            me = byid[int(me_id)]
            obs = tr.row(snap["tick"], me["id"])
            # own in-water is tile-derived, own in-sunbeam is the activity's
            # flag (observe.rs, the self block); friend rows' bits are both
            # tile-derived
            act = me["activity"]
            want_self = [scene_age(me, snap["tick"]),
                         1.0 if tile_holds(snap, me["pos"], "water") else 0.0,
                         1.0 if act.get("state") == "sleeping" and act.get("in_sunbeam") else 0.0]
            got_self = [obs[SELF_SCENE_AGE], obs[SELF_IN_WATER], obs[SELF_IN_SUNBEAM]]
            bad_self += not np.allclose(got_self, want_self, atol=ATOL)
            # the clock climbs one tick per tick inside a scene, resets outside
            p = prev.get(me["id"])
            if p and p.get("activity_clock") and me.get("activity_clock") \
                    and p["activity_clock"]["started"] == me["activity_clock"]["started"]:
                a0, a1 = scene_age(p, snap["tick"] - 1), scene_age(me, snap["tick"])
                bad_climb += not (a1 >= 1.0 - 1e-9 or abs(a1 - a0 - 1 / SCENE_AGE_NORMALISER) < 1e-6)
            rows = kitty_rows(obs)
            for k, fid in enumerate(table["kitties"]):
                if fid is None:
                    continue
                friend = byid[fid]
                state, _ = row_state(snap, me, friend, r, window)
                if state == "seen":
                    want = [1.0 if tile_holds(snap, friend["pos"], "water") else 0.0,
                            1.0 if tile_holds(snap, friend["pos"], "sunbeam") else 0.0,
                            scene_age(friend, snap["tick"])]
                else:
                    want = [0.0, 0.0, 0.0]
                bad_row += not np.allclose(rows[k][ROW_WATER_BIT:ROW_SCENE_AGE + 1], want, atol=ATOL)
    bad = bad_self or bad_row or bad_climb
    return ok_or_red("A11", bad, f"self cells wrong {bad_self}, friend cells wrong {bad_row}, "
                     f"clock not climbing 1/tick {bad_climb}",
                     {"bad_self": bad_self, "bad_row": bad_row, "bad_climb": bad_climb})


def check_a12(tr):
    r = tr.radius
    W, H = tr.snap(0)["width"], tr.snap(0)["height"]
    bad, filled, empty = 0, 0, 0
    for line in tr.lines:
        snap = line["snapshot"]
        byid = kitties_by_id(snap)
        for me_id, table in line["tables"].items():
            me = byid[int(me_id)]
            obs = tr.row(snap["tick"], me["id"])
            counts = {}
            for kind, slot in element_slots(tr, obs):
                if slot[SLOT_PRESENT] == 0:
                    empty += 1
                    bad += bool(np.any(slot != 0))
                    continue
                filled += 1
                counts[kind] = counts.get(kind, 0) + 1
                pos = {"x": round(me["pos"]["x"] + slot[SLOT_DX] * W),
                       "y": round(me["pos"]["y"] + slot[SLOT_DY] * H)}
                kinds = CRITTER_KINDS if kind == "critter" else [kind]
                there = any(e["kind"] in kinds and e["pos"] == pos for e in snap["elements"])
                bad += not (there and visible(me["pos"], pos, r))
            for kind in ("chow", "water", "sunbeam", "critter"):
                kinds = CRITTER_KINDS if kind == "critter" else [kind]
                n_vis = sum(e["kind"] in kinds and visible(me["pos"], e["pos"], r)
                            for e in snap["elements"])
                bad += counts.get(kind, 0) != min(n_vis, COUNTS[kind])
            # the table's critter ids are visible critters
            for cid in table["critters"]:
                if cid is not None:
                    e = next((e for e in snap["elements"] if e["id"] == cid), None)
                    bad += e is None or not visible(me["pos"], e["pos"], r)
    return ok_or_red("A12", bad, f"element slots wrong {bad}; filled {filled}, empty {empty}",
                     {"bad": bad, "filled": filled, "empty": empty})


def check_a13(tr):
    """First-emission tick per category. Required (PREREG A13): the
    kitty-row on-sunbeam bit at 1 on a Seen row, the water bit at 1."""
    first = {}

    def hit(name, tick):
        first.setdefault(name, int(tick))

    ticks = tr.tick
    rows = tr.obs[:, KITTY_SPAN[0]:KITTY_SPAN[1]].reshape(len(tr.obs), N_KITTY, KITTY_W)
    present = rows[..., ROW_PRESENT] > 0
    live = (rows != 0).any(-1)
    for name, hits in (("kitty_row.seen", present.any(1)),
                       ("kitty_row.heard", (live & ~present).any(1)),
                       ("kitty_row.silent", (~live).any(1)),
                       ("kitty_row.sunbeam_bit@seen", (present & (rows[..., ROW_SUNBEAM_BIT] > 0)).any(1)),
                       ("kitty_row.water_bit@seen", (present & (rows[..., ROW_WATER_BIT] > 0)).any(1)),
                       ("self.in_water", tr.obs[:, SELF_IN_WATER] > 0),
                       ("self.in_sunbeam", tr.obs[:, SELF_IN_SUNBEAM] > 0),
                       ("kitty_row.answers_me", (rows[..., ROW_ANSWERS_ME:ROW_ANSWERS_ME + 4] > 0).any((1, 2))),
                       ("kitty_row.intensity", (rows[..., ROW_INTENSITY:ROW_ANSWERS_ME] > 0).any((1, 2)))):
        idx = np.flatnonzero(hits)
        if len(idx):
            hit(name, ticks[idx[0]])
    for j, kind in enumerate(ELEMENT_KINDS):
        idx = np.flatnonzero(tr.obs[:, SELF_MEMORY + j * MEMORY_SLOT] > 0)
        if len(idx):
            hit(f"self.memory.{kind}", ticks[idx[0]])
    for i, line in enumerate(tr.lines):
        snap = line["snapshot"]
        for m in snap["recent_meows"]:
            hit(f"meow.{m['kind']}", m["tick"])
            if m.get("reply"):
                hit("meow.reply", m["tick"])
        for e in line["refusals"]:
            hit(f"refusal.{e['reason']}", e["tick"])
        if i > 0:
            prev = kitties_by_id(tr.snap(i - 1))
            for k in snap["kitties"]:
                for a, b in zip(prev[k["id"]]["memory"], k["memory"]):
                    if a is not None and b is None:
                        hit("memory.refutation", snap["tick"])
    required = ["kitty_row.sunbeam_bit@seen", "kitty_row.water_bit@seen"]
    missing = [n for n in required if n not in first]
    f = Finding("A13", "unproven" if missing else "ok",
                f"{len(first)} categories emitted; required missing: {missing}",
                {"first_emission": dict(sorted(first.items(), key=lambda kv: kv[1])),
                 "missing_required": missing})
    return f


def check_a14(tr):
    """No legality bit reads a masked fact: the bits below are implied by
    the observation alone (kitty menus by a Seen row, critter menus by a
    filled critter slot, here-words by a visible referent, want-words by
    the self needs and the absence of known relief in view or memory)."""
    from obs_layout_v5 import CRIT_MENU, KITTY_MENU
    act, msg = tr.mask[:, :N_ACT], tr.mask[:, N_ACT:]
    rows = tr.obs[:, KITTY_SPAN[0]:KITTY_SPAN[1]].reshape(len(tr.obs), N_KITTY, KITTY_W)
    seen = rows[..., ROW_PRESENT] > 0
    bad = {}
    for k in range(N_KITTY):
        bad[f"kitty{k}_menu_without_seen_row"] = int((act[:, KITTY_MENU[k]].any(1) & ~seen[:, k]).sum())
    crit = [tr.obs[:, off + SLOT_PRESENT] > 0 for off, _w in BLOCKS[N_KITTY + 6:N_KITTY + 10]]
    for j in range(COUNTS["critter"]):
        bad[f"critter{j}_menu_without_slot"] = int((act[:, CRIT_MENU[j]].any(1) & ~crit[j]).sum())
    slot_present = {}
    kinds = ["chow"] * 2 + ["water"] * 2 + ["sunbeam"] * 2 + ["critter"] * 4
    for kind, (off, _w) in zip(kinds, BLOCKS[N_KITTY:]):
        slot_present[kind] = slot_present.get(kind, np.zeros(len(tr.obs), bool)) | (tr.obs[:, off + SLOT_PRESENT] > 0)
    head = {k: msg[:, 1 + HEAD_KINDS.index(k)] for k in HEAD_KINDS}
    for here, kind in (("here_food", "chow"), ("here_water", "water"),
                       ("here_sunbeam", "sunbeam"), ("here_critter", "critter")):
        bad[f"{here}_without_visible_referent"] = int((head[here] & ~slot_present[kind]).sum())
    needs = tr.obs[:, SELF_NEEDS:SELF_NEEDS + len(NEED_KINDS)]
    top = needs.argmax(1)
    # A remembered element is known relief only within radius + margin
    # Manhattan (spec 050); the reach is read off the token's own dx/dy
    # (observe.rs normalises by world width/height), so no snapshot fact
    # enters. Margin None (key absent) is the unbounded rule.
    W, H = tr.snap(0)["width"], tr.snap(0)["height"]
    mem = {}
    for j, k in enumerate(ELEMENT_KINDS):
        slot = tr.obs[:, SELF_MEMORY + j * MEMORY_SLOT:SELF_MEMORY + (j + 1) * MEMORY_SLOT]
        present = slot[:, 0] > 0
        if tr.margin is not None:
            reach = np.rint(np.abs(slot[:, 1]) * W) + np.rint(np.abs(slot[:, 2]) * H)
            present = present & (reach <= tr.radius + tr.margin)
        mem[k] = present
    idle_friend = (seen & (rows[..., ROW_ACTIVITY] > 0)).any(1)
    thr = float(tr.cfg["meow"]["announce_threshold"]) - float(tr.cfg["meow"].get("announce_hysteresis", 0.0))
    for want in WANT_KINDS:
        need = NEED_OF_WANT[want]
        bit = head[want]
        bad[f"{want}_below_arm_floor"] = int((bit & (needs[:, NEED_KINDS.index(need)] * 100 < thr - 1e-3)).sum())
        if want == "want_bath":
            continue
        bad[f"{want}_not_top_need"] = int((bit & (top != NEED_KINDS.index(need))).sum())
    relief = {"want_eat": slot_present["chow"] | mem["chow"],
              "want_drink": slot_present["water"] | mem["water"],
              "want_cuddle": idle_friend,
              "want_play": idle_friend | slot_present["critter"] | mem["bug"] | mem["greeble"]}
    for want, known in relief.items():
        bad[f"{want}_with_known_relief"] = int((head[want] & known).sum())
    total = sum(bad.values())
    return ok_or_red("A14", total, f"{total} mask bits not implied by the observation",
                     {k: v for k, v in bad.items() if v} or {"all": 0})


def check_a15(tr):
    bad, per_observer = 0, {}
    for line in tr.lines:
        roster = sorted(k["id"] for k in line["snapshot"]["kitties"])
        for me_id, table in line["tables"].items():
            me = int(me_id)
            expect = [i for i in roster if i != me][:N_KITTY]
            expect += [None] * (N_KITTY - len(expect))
            if table["kitties"] != expect:
                bad += 1
            prev = per_observer.setdefault(me, table["kitties"])
            bad += prev != table["kitties"]
    # the recorded row order per tick is the same roster order every tick
    order = tr.kitty.reshape(len(tr.lines), -1)
    bad += int((order != order[0]).any())
    return ok_or_red("A15", bad, f"{bad} ticks where a row map moved or is not the roster minus me",
                     {"bad": bad, "maps": {k: v for k, v in per_observer.items()}})


def check_a16(tr):
    """answers-me bit == the engine reply stamp: bit 1 on (row s, kind h)
    at tick t iff s's freshest audible h was stamped reply; a reply-stamped
    here is seen as a bit by some observer on the next tick unless the
    answered want aged out at that very tick, or the wanter re-called on
    the reply's own tick (the engine compares strictly, observe.rs
    push_answers_me: a same-tick want is a new, unanswered want)."""
    r, window = tr.radius, tr.window
    bit_without_reply, reply_without_bit, aged, tied, bits, replies = 0, 0, 0, 0, 0, 0
    for i, line in enumerate(tr.lines):
        snap = line["snapshot"]
        byid = kitties_by_id(snap)
        for me_id, table in line["tables"].items():
            me = byid[int(me_id)]
            rows = kitty_rows(tr.row(snap["tick"], me["id"]))
            for k, fid in enumerate(table["kitties"]):
                if fid is None:
                    continue
                for j, here in enumerate(HERE_KINDS):
                    if rows[k][ROW_ANSWERS_ME + j] <= 0:
                        continue
                    bits += 1
                    t = freshest_tick(snap, fid, here, window)
                    m = next(x for x in snap["recent_meows"]
                             if x["kitty_id"] == fid and x["kind"] == here and x["tick"] == t)
                    bit_without_reply += not m["reply"]
        if i + 1 < len(tr.lines):
            after = tr.snap(i + 1)
            for m in meows_emitted_at(tr, i):
                if m["kind"] not in HERE_KINDS or not m["reply"]:
                    continue
                replies += 1
                j = HERE_KINDS.index(m["kind"])
                hit = False
                for line2_me, table in tr.lines[i + 1]["tables"].items():
                    if int(line2_me) == m["kitty_id"]:
                        continue
                    k = table["kitties"].index(m["kitty_id"])
                    hit |= kitty_rows(tr.row(after["tick"], int(line2_me)))[k][ROW_ANSWERS_ME + j] > 0
                if not hit:
                    want = WANT_FOR_HERE[m["kind"]]
                    still = any(x["kind"] == want and x["kitty_id"] != m["kitty_id"]
                                and audible(x, after["tick"], window) for x in after["recent_meows"])
                    same_tick = any(x["kind"] == want and x["kitty_id"] != m["kitty_id"]
                                    and x["tick"] == m["tick"] for x in after["recent_meows"])
                    if not still:
                        aged += 1
                    elif same_tick:
                        tied += 1
                    else:
                        reply_without_bit += 1
    bad = bit_without_reply or reply_without_bit
    f = ok_or_red("A16", bad, f"bits {bits}, replies {replies}; bit without reply stamp "
                  f"{bit_without_reply}, reply without any bit {reply_without_bit} "
                  f"(aged out {aged}, wanter re-called same tick {tied})",
                  {"bits": bits, "replies": replies, "bit_without_reply": bit_without_reply,
                   "reply_without_bit": reply_without_bit, "aged": aged, "tied": tied})
    if not bad and replies == 0:
        f.status = "unproven"
    return f


def check_a17(tr, policy_npz=None, declared_constant=()):
    """Can-vary must agree between anchor and policy, except on columns an
    A1 group exempts (a17_exempt_patterns): RARE groups and roster-constant
    structural ones may move under a policy the scripted anchor never
    exercises (distress under early PPO, the free register) and are
    reported apart, not red. Law-constant groups (the refused vocabulary)
    stay red if they move."""
    if policy_npz is None:
        return Finding("A17", "n/a", "no policy trace given (--policy-trace)")
    pol = np.load(policy_npz)
    pobs = pol["obs"].reshape(-1, OBS_DIM).astype(np.float32)
    var_a, var_p = tr.obs.var(0) > 0, pobs.var(0) > 0
    exempt = a17_exempt_patterns(declared_constant)
    differ = [col_name(i) for i in np.flatnonzero(var_a != var_p)]
    rare_moved = [c for c in differ if matches_any(c, exempt)]
    disagree = [c for c in differ if c not in rare_moved]
    rows_a = tr.obs[:, KITTY_SPAN[0]:KITTY_SPAN[1]].reshape(-1, N_KITTY, KITTY_W)
    rows_p = pobs[:, KITTY_SPAN[0]:KITTY_SPAN[1]].reshape(-1, N_KITTY, KITTY_W)
    seen_a = float((rows_a[..., ROW_PRESENT] > 0).mean())
    seen_p = float((rows_p[..., ROW_PRESENT] > 0).mean())
    return ok_or_red("A17", bool(disagree) or abs(seen_a - seen_p) > 0.25,
                     f"{len(disagree)} columns differ in can-vary ({len(rare_moved)} declared "
                     f"exempt); seen share anchor {seen_a:.3f} policy {seen_p:.3f}",
                     {"disagree": disagree, "rare_moved": rare_moved,
                      "seen_share": [seen_a, seen_p]})


def check_a18(tr):
    bad = sum(not v for line in tr.lines for v in line["reencode_identical"].values())
    n = sum(len(line["reencode_identical"]) for line in tr.lines)
    return ok_or_red("A18", bad, f"{bad}/{n} re-encodes differ byte for byte", {"bad": bad, "n": n})


CHECKS = [check_a1, check_a2, check_a3, check_a4, check_a5, check_a6, check_a7,
          check_a8, check_a9, check_a10, check_a11, check_a12, check_a13,
          check_a14, check_a15, check_a16, check_a17, check_a18]


def run_all(tr, declared_constant=(), policy_npz=None):
    out = []
    for fn in CHECKS:
        if fn is check_a1:
            out.append(fn(tr, declared_constant))
        elif fn is check_a17:
            out.append(fn(tr, policy_npz, declared_constant))
        else:
            out.append(fn(tr))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trace_dir", type=Path)
    ap.add_argument("--config", type=Path, default=None,
                    help="config toml if meta.json's path is not reachable")
    ap.add_argument("--declared-constant", type=Path, default=None,
                    help="json list of column names allowed constant (A1)")
    ap.add_argument("--policy-trace", type=Path, default=None, help="probe .npz for A17")
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()
    tr = load_trace(args.trace_dir, args.config)
    declared = json.loads(args.declared_constant.read_text()) if args.declared_constant else []
    findings = run_all(tr, declared, args.policy_trace)
    stop = False
    for f in findings:
        print(f"{f.row:>4} {f.status:<9} {f.summary}")
        stop |= f.status == "RED" and f.row in STOP_ROWS
    if args.json:
        args.json.write_text(json.dumps(
            {"trace_dir": str(args.trace_dir), "meta": tr.meta,
             "findings": [{"row": f.row, "status": f.status, "summary": f.summary,
                           "detail": f.detail} for f in findings]}, indent=1, default=str) + "\n")
    if stop:
        print("STOP THE PASS: a stop row is red (PREREG Part A reading rule)")
        sys.exit(1)


if __name__ == "__main__":
    main()
