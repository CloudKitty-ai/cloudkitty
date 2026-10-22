#!/usr/bin/env python3
"""Seating-analysis collector, Gen 2 port (DECLARATION.md beside this
file). The v1 collector (../seating-analysis-2026-09-28/) with the four
Gen 2 fixes: the global-state stride keyed off the live width (v2 = 40,
never v1's 32), no clock write (schema 6 has no clock input), the
seating and config as inputs (artifact hashes through the harness's
artifact_path), and head sizes from the harness's SCHEMA_DIMS. Adds the
chosen-action stream (play-proposal share) and runs all-scripted
rosters (the reference) through the engine's control= seats.

The per-tick loop mirrors cert_harness_fog.run_one's g2 branch, and the
guard holds the two equal on the same world.

    seating_collect_g2.py --seating g2-rot1 --seed 905001 \
        --out results-raw/g2-rot1/streams-905001.npz

Streams are v1's (pos, activity, msg, needs, hap, partner, distress,
nash, elements) plus act (T, R) int8, the chosen menu action (-1 for an
engine-driven seat). Scripted seats choose inside the engine, so their
msg is recorded as 0 and meta["speech_recorded"] lists which seats
carry real message heads. Since Amendment 1 (2026-10-21) also applied
and applied_with (T, R) int8: every seat's applied action per tick (the
engine's last_action, read through decision_request, which never moves
the episode) and its partner seat, encoded by the reader's
encode_applied; the end-of-tick activity and partner flags hide each
scene's last tick.
"""
import argparse
import json
import sys
import time
import tomllib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
sys.path.insert(0, str(EXPTS / "fog-gen1-cert"))
sys.path.insert(0, str(EXPTS / "gen2-corpus-reads-2026-10-13"))
sys.path.insert(0, str(EXPTS / "seating-analysis-2026-09-28"))
import cert_harness_fog as H  # noqa: E402
from coverage_read import infer_block  # noqa: E402
from seating_read import APPLIED_NAMES, encode_applied  # noqa: E402

CONFIG = EXPTS / "gen2-comparator-legs-2026-10-14" / "g2leg-20.toml"
E_MIN = 64   # element slots at 20x20; bigger worlds size from their reset count


def abort_due(dist_streak, abort_streak, abort_seat=None):
    """The distress stop: any seat's current single-need streak at or over
    `abort_streak` — or, with `abort_seat`, that seat's alone (the tail
    replays' welfare mitigation, 2026-10-22: stop 100 ticks into the
    target cat's run even when another seat's run is longer)."""
    if abort_streak is None:
        return False
    watched = dist_streak if abort_seat is None else dist_streak[abort_seat]
    return bool(watched.max() >= abort_streak)


def collect(seating, seed, ticks, abort_streak, config=CONFIG, abort_seat=None):
    import cloudkitty
    with open(config, "rb") as f:
        cfg = tomllib.load(f)
    kitties = cfg["kitty"]
    roster = len(kitties)
    width, height = cfg["world"]["width"], cfg["world"]["height"]
    seats = list(H.SEATINGS[seating])
    assert len(seats) == roster, (seating, roster)
    assert all(s == "scripted" or s.startswith("g2:") for s in seats), seats
    n_act, n_heads = H.SCHEMA_DIMS["v6"][1:]
    control = {f"kitty_{k['id']}": k["behavior"]
               for k, s in zip(kitties, seats) if s == "scripted"}
    models = {s: H.load_model(s) for s in set(seats) if s != "scripted"}
    # horizon one past the last step: the engine closes the decision window
    # at the horizon, and the last tick's applied actions are read after it.
    # The horizon feeds only truncation and the critic's clock cell, which
    # nothing here records (schema 6 observations carry no clock).
    env = cloudkitty.ParallelEnv(str(config), control=control or None, horizon=ticks + 1)
    obs, infos = env.reset(seed=seed)
    e_max = max(E_MIN, 2 * len(env.elements()))
    pk = infer_block(np.asarray(env.state()).size, roster)[1]
    names = list(env.possible_agents)
    assert names == [f"kitty_{k['id']}" for k, s in zip(kitties, seats) if s != "scripted"], names
    seat_of = {f"kitty_{k['id']}": s for k, s in zip(kitties, seats)}
    col = {f"kitty_{k['id']}": i for i, k in enumerate(kitties)}
    ids = [k["id"] for k in kitties]
    col_of_id = {kid: i for i, kid in enumerate(ids)}

    etypes = {}

    def ecode(ty):
        if ty not in etypes:
            etypes[ty] = len(etypes)
        return etypes[ty]

    T = ticks
    pos = np.zeros((T, roster, 2), np.int16)
    activity = np.zeros((T, roster), np.int8)
    msg = np.zeros((T, roster), np.int8)
    act = np.full((T, roster), -1, np.int8)
    needs = np.zeros((T, roster, 6), np.float32)
    hap = np.zeros((T, roster), np.float32)
    partner = np.full((T, roster, 2), -1, np.int8)
    applied = np.full((T, roster), -1, np.int8)
    applied_with = np.full((T, roster), -1, np.int8)
    distress = np.zeros((T, roster), np.uint8)
    nash = np.zeros(T, np.float64)
    elements = np.full((T, e_max, 3), -1, np.int16)

    dist_streak = np.zeros((roster, 6), np.int64)
    aborted_at = None
    n = 0
    for _t in range(ticks):
        acts = {}
        if names:
            ob = np.stack([np.asarray(obs[a], np.float32) for a in names])
            mk = np.stack([np.asarray(infos[a]["mask"], np.uint8) for a in names]).astype(bool)
            lg = np.zeros((len(names), n_heads), np.float32)
            for s, fwd in models.items():
                rows = [i for i, a in enumerate(names) if seat_of[a] == s]
                if rows:
                    lg[rows] = np.asarray(fwd(ob[rows], mk[rows]), np.float32)
            a0 = np.where(mk[:, :n_act], lg[:, :n_act], H.NEG_INF).argmax(1)
            g0 = np.where(mk[:, n_act:], lg[:, n_act:], H.NEG_INF).argmax(1)
            acts = {a: (int(a0[i]), int(g0[i])) for i, a in enumerate(names)}
            for i, a in enumerate(names):
                act[n, col[a]] = a0[i]
                msg[n, col[a]] = g0[i]
        obs, _r, _te, _tr, infos = env.step(acts)
        st = np.asarray(env.state(), np.float32)
        for k in range(roster):
            b = k * pk
            pos[n, k] = (round(float(st[b + H.POS0]) * width), round(float(st[b + H.POS0 + 1]) * height))
            activity[n, k] = int(st[b + H.ACT0:b + H.ACT0 + 7].argmax())
            needs[n, k] = st[b:b + 6] * 100
            hap[n, k] = float(st[b + H.HAP]) * 100
            if st[b + H.PARTNER_PRESENT] > 0.5:
                partner[n, k] = (1, round(float(st[b + H.PARTNER_IDX]) * (roster - 1)))
            flags = st[b + H.DIST0:b + H.DIST0 + 6] > 0
            distress[n, k] = int(np.packbits(flags, bitorder="little")[0])
            dist_streak[k] = np.where(flags, dist_streak[k] + 1, 0)
        for k, kid in enumerate(ids):
            applied[n, k], applied_with[n, k] = encode_applied(
                json.loads(env.decision_request(kid))["me"]["last_action"], col_of_id)
        h_norm = st[H.HAP:roster * pk:pk].astype(np.float64)
        nash[n] = float(np.exp(np.log(np.maximum(h_norm + H.REWARD_EPS, H.TERM_FLOOR)).mean()) - H.REWARD_EPS)
        els = env.elements()
        assert len(els) <= e_max, (len(els), e_max)
        for j, (_id, ty, x, y) in enumerate(els):
            elements[n, j] = (ecode(ty), x, y)
        n += 1
        if abort_due(dist_streak, abort_streak, abort_seat):
            aborted_at = n
            break

    meta = {
        "seed": seed, "ticks": n, "requested_ticks": ticks, "seating": seating,
        "seats": seats, "clock": "none (schema 6)", "config": config.name,
        "provenance": H.provenance(config, seats),
        "speech_recorded": [s != "scripted" for s in seats],
        "element_types": etypes, "width": width, "height": height,
        "per_kitty": pk, "abort_streak": abort_streak, "aborted_at": aborted_at,
        "abort_seat": abort_seat,
        "applied_names": APPLIED_NAMES,
        "collected_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    arrays = dict(pos=pos[:n], activity=activity[:n], msg=msg[:n], act=act[:n],
                  needs=needs[:n], hap=hap[:n], partner=partner[:n],
                  distress=distress[:n], nash=nash[:n], elements=elements[:n],
                  applied=applied[:n], applied_with=applied_with[:n])
    return arrays, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seating", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--ticks", type=int, default=20000)
    ap.add_argument("--abort-streak", type=int, default=1000)
    ap.add_argument("--out", required=True)
    ap.add_argument("--config", type=Path, default=CONFIG,
                    help="world toml (default g2leg-20); play-decomposition cells pass their own")
    a = ap.parse_args()
    import torch
    torch.set_num_threads(1)
    arrays, meta = collect(a.seating, a.seed, a.ticks, a.abort_streak, config=a.config)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, meta=json.dumps(meta), **arrays)
    print(f"wrote {out}: {meta['ticks']} ticks"
          + (f" ABORTED at {meta['aborted_at']}" if meta["aborted_at"] else ""), flush=True)


if __name__ == "__main__":
    main()
