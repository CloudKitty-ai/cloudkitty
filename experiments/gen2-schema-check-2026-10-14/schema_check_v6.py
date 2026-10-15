#!/usr/bin/env python3
"""Schema-6 trace checker, tranche 1 (the Gen 2 port of the Part A
idea; the FULL Gen 2 Part A checklist lands with the Gen 2 prereg —
this file carries only the rows whose law landed specs already pin).

    schema_check_v6.py TRACE_DIR [--config TOML] [--json OUT]

TRACE_DIR is a bc-collect --trace rollout dir recorded by the 058-era
binary (observation_schema 6; a schema-5 trace refuses by name — its
checker is fog-gen1-shakeout/schema_check.py). Rows implemented:

  A1   constant-column census — REPORT ONLY here: the Gen 2
       declared-constant list is a prereg artifact that does not
       exist yet, so nothing reds; the census is printed for it.
  A3   kitty rows re-derived cell for cell from the snapshot
       (contracts/observation-v6.md §Kitty row): Seen rows carry the
       spatial group, bath (five-of-six: THE ONE visible need),
       activity, partner, is-my-target, tile bits, scene age, digest;
       Heard rows carry spatial-to-last-meow + digest with bath and
       offsets 6-17 ZERO (hearing carries no coat state); Silent rows
       all zero. Full-row equality IS the value-level leak audit:
       there is no cell left for a hidden need or happiness to ride.
  A11  self block: needs, happiness, walls N/E/S/W (tiles-to-wall /40
       — observe.rs near_cell order y, w-1-x, h-1-y, x), activity,
       partnered, in-sunbeam (activity-derived), in-water
       (tile-derived), distress flags, own scene age. Progress and
       pursuit are REPORTED, not asserted (their duration/patience
       law joins a later tranche).
  AID  identity block vs the config: need-rate multipliers
       (need_rate_for / [rl.observation] reference_need_rate, clamp
       [0,4]), comfort slack (/40 clamp), consent line (/100),
       favourite weights (override or 0).
  A15  row maps permanent: roster minus me in id order, constant.
  A18  re-encode determinism (the collector's own byte check).

NOT HERE (lands with the prereg's checklist): memory token (A2), meow
stamp/position laws (A4-A9), lattice (A10), element slots (A12/A13),
mask implication (A14), policy-trace can-vary (A17).

Snapshot-law helpers come from the v5 checker (one home): visibility,
row state, message digests and scene age are layout-agnostic.

Exit 1 on any RED among implemented asserting rows.
Guard: test_schema_check_v6.py.
"""
import argparse
import json
import math
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fog-gen1-shakeout"))
sys.path.insert(0, str(HERE.parent / "attn-oracle-2026-08-15"))
from schema_check import (  # noqa: E402  (v5 checker: layout-agnostic law)
    Finding, answers_me, audible, kitties_by_id, msg_block, need_rate,
    ok_or_red, row_state, scene_age, tile_holds, visible)
import obs_layout_v6 as L6  # noqa: E402

ATOL = 1e-5
ASSERTING = {"A3", "A11", "AID", "A15", "A18"}


@dataclass
class TraceV6:
    obs: np.ndarray
    kitty: np.ndarray
    tick: np.ndarray
    lines: list
    meta: dict
    cfg: dict
    rl: dict
    row_of: dict = field(default_factory=dict)

    @property
    def radius(self):
        return int(self.meta["vision_radius"])

    @property
    def window(self):
        return int(self.cfg["meow"]["digest_window_ticks"])

    @property
    def cooldown(self):
        return int(self.cfg["meow"]["recent_window_ticks"])

    def snap(self, i):
        return self.lines[i]["snapshot"]

    def row(self, tick, kitty):
        return self.obs[self.row_of[(int(tick), int(kitty))]]


def load_trace(d, config=None):
    d = Path(d)
    meta = json.loads((d / "meta.json").read_text())
    assert meta.get("trace"), f"{d} was not recorded with --trace"
    if meta["observation_schema"] != 6:
        raise SystemExit(
            f"schema_check_v6.py is the schema-6 ({L6.OBS_DIM}-cell) "
            f"instrument; {d}/meta.json says observation_schema="
            f"{meta['observation_schema']}. The schema-5 checker is "
            "experiments/fog-gen1-shakeout/schema_check.py.")
    assert meta["obs_width"] == L6.OBS_DIM, meta
    cfg_path = Path(config) if config else Path(meta["config"])
    text = cfg_path.read_text()
    cfg = tomllib.loads(text)
    rl = cfg.get("rl", {})
    obs = np.load(d / "trace_obs.npy").astype(np.float32)
    kitty = np.load(d / "trace_kitty.npy")
    tick = np.load(d / "trace_tick.npy")
    lines = [json.loads(l) for l in (d / "trace.jsonl").read_text().splitlines()]
    tr = TraceV6(obs, kitty, tick, lines, meta, cfg, rl)
    tr.row_of = {(int(t), int(k)): i for i, (t, k) in enumerate(zip(tick, kitty))}
    assert len(lines) == len(set(tick.tolist()))
    return tr


# ---------------------------------------------------------------- law helpers

def spatial(me_pos, pos):
    """The v6 spatial cell group (contract §Conventions): Manhattan
    bearing pair + linear /40 clamped + log1p(d)/log1p(400)."""
    dx, dy = pos["x"] - me_pos["x"], pos["y"] - me_pos["y"]
    d = abs(dx) + abs(dy)
    bx, by = (dx / d, dy / d) if d else (0.0, 0.0)
    return [bx, by, min(d / 40.0, 1.0), math.log1p(d) / math.log1p(400.0)]


def partner_of(act):
    """Activity::partner() in snapshot spelling: resting/sleeping
    with_friend; playing TargetRef::Kitty; grooming target."""
    s = act.get("state")
    if s in ("resting", "sleeping"):
        return act.get("with_friend")
    if s == "playing":
        t = act.get("target") or {}
        return t.get("id") if t.get("target") == "kitty" else None
    if s == "grooming":
        return act.get("target")
    return None


def activity_onehot(act):
    out = [0.0] * len(L6.ACTIVITY_KINDS)
    s = act.get("state", "idle")
    name = {"resting": "resting", "sleeping": "sleeping", "eating": "eating",
            "drinking": "drinking", "playing": "playing",
            "grooming": "grooming"}.get(s, "idle")
    out[L6.ACTIVITY_KINDS.index(name)] = 1.0
    return out


def kitty_rows(obs_row):
    return obs_row[L6.KITTY_SPAN[0]:L6.KITTY_SPAN[1]].reshape(
        L6.COUNTS["kitty"], L6.KITTY_W)


def expected_row(tr, snap, me, friend):
    """All 58 cells of one kitty row from the snapshot."""
    state, pos = row_state(snap, me, friend, tr.radius, tr.window)
    if state == "silent":
        return [0.0] * L6.KITTY_W, state
    digest = msg_block(snap, friend["id"], tr.window, tr.cooldown, True)
    bits = answers_me(snap, me["id"], friend["id"], tr.window)
    if state == "heard":
        return ([0.0] + spatial(me["pos"], pos)
                + [0.0] * (1 + 7 + 1 + 1 + 1 + 1 + 1)
                + digest + bits, state)
    row = [1.0] + spatial(me["pos"], friend["pos"])
    row += [friend["needs"]["bath"] / 100.0]
    row += activity_onehot(friend["activity"])
    row += [1.0 if partner_of(friend["activity"]) is not None else 0.0]
    row += [1.0 if partner_of(me["activity"]) == friend["id"] else 0.0]
    row += [1.0 if tile_holds(snap, friend["pos"], "water") else 0.0]
    row += [1.0 if tile_holds(snap, friend["pos"], "sunbeam") else 0.0]
    row += [scene_age(friend, snap["tick"])]
    row += digest + bits
    return row, state


# -------------------------------------------------------------------- checks

def check_a3(tr):
    bad, seen_n, heard_n, silent_n = 0, 0, 0, 0
    for line in tr.lines:
        snap = line["snapshot"]
        byid = kitties_by_id(snap)
        for me_id, table in line["tables"].items():
            me = byid[int(me_id)]
            rows = kitty_rows(tr.row(snap["tick"], me["id"]))
            for k, fid in enumerate(table["kitties"]):
                if fid is None:
                    bad += bool(np.any(rows[k] != 0))
                    continue
                want, state = expected_row(tr, snap, me, byid[fid])
                seen_n += state == "seen"
                heard_n += state == "heard"
                silent_n += state == "silent"
                bad += not np.allclose(rows[k], want, atol=ATOL)
    f = ok_or_red("A3", bad,
                  f"{bad} kitty rows disagree with the 058 contract; "
                  f"seen {seen_n}, heard {heard_n}, silent {silent_n} "
                  "(full-row equality = the five-of-six leak audit)",
                  {"bad": bad, "seen": seen_n, "heard": heard_n,
                   "silent": silent_n})
    if not bad and (seen_n == 0 or heard_n == 0):
        f.status = "unproven"
    return f


def check_a11(tr):
    W, H = tr.snap(0)["width"], tr.snap(0)["height"]
    near = lambda t: min(t / 40.0, 1.0)  # noqa: E731
    bad_needs, bad_walls, bad_act, bad_dist, bad_age = 0, 0, 0, 0, 0
    for line in tr.lines:
        snap = line["snapshot"]
        for me_id in line["tables"]:
            me = kitties_by_id(snap)[int(me_id)]
            obs = tr.row(snap["tick"], me["id"])
            want_needs = [me["needs"][n] / 100.0 for n in L6.NEED_KINDS] \
                + [me["happiness"] / 100.0]
            bad_needs += not np.allclose(
                obs[L6.SELF_NEEDS:L6.SELF_HAPPINESS + 1], want_needs, atol=ATOL)
            x, y = me["pos"]["x"], me["pos"]["y"]
            want_walls = [near(y), near(W - 1 - x), near(H - 1 - y), near(x)]
            bad_walls += not np.allclose(
                obs[L6.SELF_WALLS:L6.SELF_WALLS + 4], want_walls, atol=ATOL)
            act = me["activity"]
            want_act = activity_onehot(act) \
                + [1.0 if partner_of(act) is not None else 0.0,
                   1.0 if (act.get("state") == "sleeping" and act.get("in_sunbeam")) else 0.0,
                   1.0 if tile_holds(snap, me["pos"], "water") else 0.0]
            bad_act += not np.allclose(
                obs[L6.SELF_ACTIVITY:L6.SELF_PROGRESS], want_act, atol=ATOL)
            want_dist = [1.0 if n in me["in_distress"] else 0.0 for n in L6.NEED_KINDS]
            bad_dist += not np.allclose(
                obs[L6.SELF_DISTRESS:L6.SELF_DISTRESS + 6], want_dist, atol=ATOL)
            bad_age += not np.isclose(obs[L6.SELF_SCENE_AGE],
                                      scene_age(me, snap["tick"]), atol=ATOL)
    bad = bad_needs + bad_walls + bad_act + bad_dist + bad_age
    return ok_or_red("A11", bad,
                     f"self cells wrong: needs+hap {bad_needs}, walls {bad_walls}, "
                     f"activity/flags {bad_act}, distress {bad_dist}, scene age "
                     f"{bad_age} (progress + pursuit reported, not asserted)",
                     {"needs": bad_needs, "walls": bad_walls, "act": bad_act,
                      "dist": bad_dist, "age": bad_age})


def identity_expected(tr, kid):
    ref = float(tr.rl.get("observation", {}).get("reference_need_rate", 1.0))
    beh = tr.cfg["behavior"]
    me = next(k for k in tr.cfg["kitty"] if k["id"] == kid)
    out = [max(0.0, min(need_rate(tr.cfg, kid, n) / ref, 4.0)) for n in L6.NEED_KINDS]
    # [behavior] comfort_slack / consent_line serde-default to 0.0
    # (config/mod.rs BehaviorConfig::default; keys skip-serialized at 0)
    slack = float(me.get("comfort_slack", beh.get("comfort_slack", 0.0)))
    out.append(max(0.0, min(slack / 40.0, 1.0)))
    out.append(float(me.get("consent_line", beh.get("consent_line", 0.0))) / 100.0)
    fav = me.get("favourite", {})
    out += [float(fav.get(n, 0.0)) for n in L6.NEED_KINDS]
    return out


def check_aid(tr):
    bad, per = 0, {}
    for line in tr.lines[:1]:   # identity is config-static; one tick suffices
        for me_id in line["tables"]:
            kid = int(me_id)
            obs = tr.row(line["snapshot"]["tick"], kid)
            want = identity_expected(tr, kid)
            got = obs[L6.SELF_IDENTITY:L6.SELF_IDENTITY + L6.IDENTITY_BLOCK]
            ok = np.allclose(got, want, atol=ATOL)
            bad += not ok
            if not ok:
                per[kid] = {"got": got.tolist(), "want": want}
    # ... and static over the whole trace
    ids = sorted({int(k) for k in tr.kitty.tolist()})
    moved = 0
    for kid in ids:
        rows = tr.obs[tr.kitty == kid][:, L6.SELF_IDENTITY:L6.SELF_IDENTITY + L6.IDENTITY_BLOCK]
        moved += bool((rows != rows[0]).any())
    return ok_or_red("AID", bad + moved,
                     f"{bad} identity blocks disagree with the config; "
                     f"{moved} seats whose identity moved mid-trace",
                     {"bad": per, "moved": moved})


def check_a15(tr):
    bad, per_observer = 0, {}
    n_rows = L6.COUNTS["kitty"]
    for line in tr.lines:
        roster = sorted(k["id"] for k in line["snapshot"]["kitties"])
        for me_id, table in line["tables"].items():
            me = int(me_id)
            expect = [i for i in roster if i != me][:n_rows]
            expect += [None] * (n_rows - len(expect))
            bad += table["kitties"] != expect
            prev = per_observer.setdefault(me, table["kitties"])
            bad += prev != table["kitties"]
    return ok_or_red("A15", bad,
                     f"{bad} ticks where a row map moved or is not the "
                     "roster minus me", {"bad": bad})


def check_a18(tr):
    bad = sum(not v for line in tr.lines for v in line["reencode_identical"].values())
    n = sum(len(line["reencode_identical"]) for line in tr.lines)
    return ok_or_red("A18", bad, f"{bad}/{n} re-encodes differ byte for byte",
                     {"bad": bad, "n": n})


def col_name(i):
    if i < 109:
        return f"self[{i}]"
    if i < L6.KITTY_SPAN[1]:
        k, c = divmod(i - L6.KITTY_SPAN[0], L6.KITTY_W)
        return f"kitty{k}[{c}]"
    for j, (off, w) in enumerate(L6.BLOCKS[L6.COUNTS['kitty']:]):
        if off <= i < off + w:
            return f"element_block{j}[{i - off}]"
    return f"col{i}"


def check_a1(tr):
    constant = [col_name(i) for i in np.flatnonzero(tr.obs.var(axis=0) == 0)]
    return Finding("A1", "reported",
                   f"{len(constant)} constant columns (census only: the Gen 2 "
                   "declared-constant list lands with the prereg)",
                   {"constant": constant})


CHECKS = [check_a1, check_a3, check_a11, check_aid, check_a15, check_a18]


def run_all(tr):
    return [fn(tr) for fn in CHECKS]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trace_dir", type=Path)
    ap.add_argument("--config", type=Path, default=None)
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()
    tr = load_trace(args.trace_dir, args.config)
    findings = run_all(tr)
    stop = False
    for f in findings:
        print(f"{f.row:>4} {f.status:<9} {f.summary}")
        stop |= f.status == "RED" and f.row in ASSERTING
    if args.json:
        args.json.write_text(json.dumps(
            {"trace_dir": str(args.trace_dir), "meta": tr.meta,
             "findings": [{"row": f.row, "status": f.status,
                           "summary": f.summary, "detail": f.detail}
                          for f in findings]}, indent=1, default=str) + "\n")
    if stop:
        print("STOP: an asserting row is red")
        sys.exit(1)


if __name__ == "__main__":
    main()
