"""Seating-analysis collector (DECLARATION.md, 2026-09-28): the
cert-harness run_one loop recording per-tick STREAMS instead of
aggregate accounts. gen1-A on anchor-b3.toml, clock `train` (the
served seam), greedy both heads under the mask.

    seating_collect.py --seed 900501 --ticks 20000 \
        --out results-raw/streams-900501.npz

Streams (T = ticks actually run):
    pos       (T, R, 2) int16   tile coordinates
    activity  (T, R)    int8    engine activity argmax (0..6)
    msg       (T, R)    int8    chosen message head (0 = Silent)
    needs     (T, R, 6) float32 x100
    hap       (T, R)    float32 x100
    partner   (T, R, 2) int8    (present, partner index; -1 = none)
    distress  (T, R)    uint8   6-flag bitmask
    nash      (T,)      float64 team nash (state)
    elements  (T, E, 3) int16   (type code, x, y), -1-padded, E = 64
    element_types               the type-code table (json in meta)
Abort: the leg stops the tick any distress streak reaches
--abort-streak (default 1000); meta records it.
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
sys.path.insert(0, str(HERE.parent / "fog-gen1-shakeout" / "trainer"))
import cert_harness_fog as H

CONFIG = HERE.parent / "fog-gen1-cert" / "anchor-b3.toml"
SEATS = H.SEATINGS["gen1-A"]
E_MAX = 64


def collect(seed, ticks, abort_streak):
    import cloudkitty
    import tomllib
    with open(CONFIG, "rb") as f:
        cfg = tomllib.load(f)
    kitties = cfg["kitty"]
    roster = len(kitties)
    width, height = cfg["world"]["width"], cfg["world"]["height"]
    models = {s: H.load_model(s) for s in set(SEATS)}
    env = cloudkitty.ParallelEnv(str(CONFIG), horizon=ticks)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    assert names == [f"kitty_{k['id']}" for k in kitties], names
    seat_of = dict(zip(names, SEATS))

    etypes = {}

    def ecode(ty):
        if ty not in etypes:
            etypes[ty] = len(etypes)
        return etypes[ty]

    T = ticks
    pos = np.zeros((T, roster, 2), np.int16)
    activity = np.zeros((T, roster), np.int8)
    msg = np.zeros((T, roster), np.int8)
    needs = np.zeros((T, roster, 6), np.float32)
    hap = np.zeros((T, roster), np.float32)
    partner = np.full((T, roster, 2), -1, np.int8)
    distress = np.zeros((T, roster), np.uint8)
    nash = np.zeros(T, np.float64)
    elements = np.full((T, E_MAX, 3), -1, np.int16)

    dist_streak = np.zeros((roster, 6), np.int64)
    aborted_at = None
    n = 0
    for _t in range(ticks):
        ob = np.stack([np.asarray(obs[a], np.float32) for a in names])
        ob[:, H.CLOCK_INDEX] = (n % H.TRAIN_HORIZON) / H.TRAIN_HORIZON
        mk = np.stack([np.asarray(infos[a]["mask"], np.uint8) for a in names]).astype(bool)
        lg = np.zeros((roster, H.N_HEADS), np.float32)
        for s, fwd in models.items():
            rows = [i for i, a in enumerate(names) if seat_of[a] == s]
            lg[rows] = np.asarray(fwd(ob[rows], mk[rows]), np.float32)
        a0 = np.where(mk[:, :H.N_ACT], lg[:, :H.N_ACT], H.NEG_INF).argmax(1)
        g0 = np.where(mk[:, H.N_ACT:], lg[:, H.N_ACT:], H.NEG_INF).argmax(1)
        obs, _r, _te, _tr, infos = env.step({a: (int(a0[i]), int(g0[i])) for i, a in enumerate(names)})
        st = np.asarray(env.state(), np.float32)
        for k in range(roster):
            b = k * H.PER_KITTY
            pos[n, k] = (round(float(st[b + H.POS0]) * width), round(float(st[b + H.POS0 + 1]) * height))
            activity[n, k] = int(st[b + H.ACT0:b + H.ACT0 + 7].argmax())
            needs[n, k] = st[b:b + 6] * 100
            hap[n, k] = float(st[b + H.HAP]) * 100
            if st[b + H.PARTNER_PRESENT] > 0.5:
                partner[n, k] = (1, round(float(st[b + H.PARTNER_IDX]) * (roster - 1)))
            flags = st[b + H.DIST0:b + H.DIST0 + 6] > 0
            distress[n, k] = int(np.packbits(flags, bitorder="little")[0])
            dist_streak[k] = np.where(flags, dist_streak[k] + 1, 0)
        msg[n] = g0
        h_norm = st[H.HAP:roster * H.PER_KITTY:H.PER_KITTY].astype(np.float64)
        nash[n] = float(np.exp(np.log(np.maximum(h_norm + H.REWARD_EPS, H.TERM_FLOOR)).mean()) - H.REWARD_EPS)
        els = env.elements()
        assert len(els) <= E_MAX, len(els)
        for j, (_id, ty, x, y) in enumerate(els):
            elements[n, j] = (ecode(ty), x, y)
        n += 1
        if abort_streak is not None and dist_streak.max() >= abort_streak:
            aborted_at = n
            break

    meta = {
        "seed": seed, "ticks": n, "requested_ticks": ticks,
        "seats": SEATS, "clock": "train", "config": CONFIG.name,
        "config_sha256": hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
        "element_types": etypes, "width": width, "height": height,
        "abort_streak": abort_streak,
        "aborted_at": aborted_at,
        "artifacts": {s: hashlib.sha256((H.ARTS / f"ppo-fog-{s.split(':', 1)[1]}" / "policy-final.pt").read_bytes()).hexdigest()
                      for s in sorted(set(SEATS))},
        "collected_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    arrays = dict(pos=pos[:n], activity=activity[:n], msg=msg[:n], needs=needs[:n],
                  hap=hap[:n], partner=partner[:n], distress=distress[:n],
                  nash=nash[:n], elements=elements[:n])
    return arrays, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--ticks", type=int, default=20000)
    ap.add_argument("--abort-streak", type=int, default=1000)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    import torch
    torch.set_num_threads(1)
    arrays, meta = collect(a.seed, a.ticks, a.abort_streak)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, meta=json.dumps(meta), **arrays)
    print(f"wrote {out}: {meta['ticks']} ticks"
          + (f" ABORTED at {meta['aborted_at']}" if meta["aborted_at"] else ""))


if __name__ == "__main__":
    main()
