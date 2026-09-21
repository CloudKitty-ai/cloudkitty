#!/usr/bin/env python3
"""Which need held a battery seed's longest distress streak, and what the cat was doing.

Re-runs one cert-harness leg (same config, seats, seed, ticks, served clock) through the
harness's own model loader and step loop, and for every (seat, need) keeps the longest
flag streak: its tick window, the need's value at start / peak / end, the activity
histogram over the window, and the share of the window asleep on a beam. Reads the same
global-state layout the harness reads (needs 0..5, activity one-hot at 9, distress flags at
20..25, NeedKind::ALL order). Beam-world screen tier 6, 2026-09-21.

    CERT_ARTS=<arts> distress_inspect.py <config.toml> <seed> [--seat k=ppo:slot ...] [--ticks 20000]
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
import cert_harness_fog as C  # noqa: E402

NEEDS = ("eat", "drink", "sleep", "play", "cuddle", "bath")
ACTS = ("idle", "rest", "sleep", "eat", "drink", "play", "groom")


def inspect(config_path, seed, seats, ticks, clock_mode="served"):
    import cloudkitty
    import numpy as np
    import tomllib
    with open(config_path, "rb") as f:
        cfg = tomllib.load(f)
    kitties = cfg["kitty"]
    roster = len(kitties)
    assert len(seats) == roster, (len(seats), roster)
    control = {f"kitty_{k['id']}": k["behavior"] for k, s in zip(kitties, seats) if s == "scripted"}
    models = {s: C.load_model(s) for s in set(seats) if s != "scripted"}
    env = cloudkitty.ParallelEnv(str(config_path), control=control or None, horizon=ticks)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    seat_of = {f"kitty_{k['id']}": s for k, s in zip(kitties, seats)}
    width, height = cfg["world"]["width"], cfg["world"]["height"]

    streak = np.zeros((roster, 6), np.int64)
    cur = [[None] * 6 for _ in range(roster)]   # open window record per (seat, need)
    best = [[None] * 6 for _ in range(roster)]

    def close(k, j, t):
        w = cur[k][j]
        if w is None:
            return
        w["end"] = t
        w["len"] = t - w["start"]
        w["need_end"] = w["need_last"]
        if best[k][j] is None or w["len"] > best[k][j]["len"]:
            best[k][j] = w
        cur[k][j] = None

    for t in range(ticks):
        acts = {}
        if names:
            ob = np.stack([np.asarray(obs[a], np.float32) for a in names])
            if clock_mode == "served":
                ob[:, C.CLOCK_INDEX] = 0.0
            mk = np.stack([np.asarray(infos[a]["mask"], np.uint8) for a in names]).astype(bool)
            lg = np.zeros((len(names), C.N_HEADS), np.float32)
            for s, fwd in models.items():
                rows = [i for i, a in enumerate(names) if seat_of[a] == s]
                if rows:
                    lg[rows] = np.asarray(fwd(ob[rows], mk[rows]), np.float32)
            a0 = np.where(mk[:, :C.N_ACT], lg[:, :C.N_ACT], C.NEG_INF).argmax(1)
            g0 = np.where(mk[:, C.N_ACT:], lg[:, C.N_ACT:], C.NEG_INF).argmax(1)
            acts = {a: (int(a0[i]), int(g0[i])) for i, a in enumerate(names)}
        obs, _rew, _term, _trunc, infos = env.step(acts)
        st = np.asarray(env.state(), np.float32)
        beams = {(x, y) for (_id, ty, x, y) in env.elements() if ty == "Sunbeam"}
        for k in range(roster):
            b = k * C.PER_KITTY
            flags = st[b + C.DIST0:b + C.DIST0 + 6] > 0
            act = int(st[b + C.ACT0:b + C.ACT0 + 7].argmax())
            pos = (int(round(float(st[b + C.POS0]) * width)), int(round(float(st[b + C.POS0 + 1]) * height)))
            hap = float(st[b + C.HAP]) * 100
            for j in range(6):
                need = float(st[b + j]) * 100
                if flags[j]:
                    if cur[k][j] is None:
                        cur[k][j] = {"seat": k, "need": NEEDS[j], "start": t, "need_start": need, "need_peak": need,
                                     "hap_start": hap, "hap_min": hap, "acts": [0] * 7, "on_beam_asleep": 0,
                                     "beams_seen": set()}
                    w = cur[k][j]
                    w["need_peak"] = max(w["need_peak"], need)
                    w["need_last"] = need
                    w["hap_min"] = min(w["hap_min"], hap)
                    w["acts"][act] += 1
                    if act == C.SLEEP_ACT and pos in beams:
                        w["on_beam_asleep"] += 1
                    w["beams_seen"].add(len(beams))
                else:
                    close(k, j, t)
    for k in range(roster):
        for j in range(6):
            close(k, j, ticks)
    out = []
    for k in range(roster):
        for j in range(6):
            w = best[k][j]
            if w is None:
                continue
            w["acts"] = {ACTS[i]: n for i, n in enumerate(w["acts"]) if n}
            w["beams_seen"] = sorted(w["beams_seen"])
            w["seat_spec"] = seats[k]
            w["kitty"] = kitties[k]["name"]
            out.append(w)
    out.sort(key=lambda w: -w["len"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config", type=Path)
    ap.add_argument("seed", type=int)
    ap.add_argument("--seat", action="append", default=[], help="k=ppo:slot (default gen1-A seating)")
    ap.add_argument("--ticks", type=int, default=20_000)
    ap.add_argument("--top", type=int, default=6)
    a = ap.parse_args()
    seats = list(C.SEATINGS["gen1-A"])
    for s in a.seat:
        k, spec = s.split("=", 1)
        seats[int(k)] = spec
    for w in inspect(a.config, a.seed, seats, a.ticks)[:a.top]:
        print(json.dumps(w))


if __name__ == "__main__":
    main()
