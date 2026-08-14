"""Pumpkin-seat diagnosis (owner investigation, cert G2d): per-seat
need pressure, distress attribution, and activity budgets for the
candidate seating and the owner's two reseating alternatives.

Seatings (kitty order Miso, Biscuit, Pumpkin, Kittybear):
  cand  = [s1, s2, s3, s3]   (the frozen candidate)
  altA  = [s3, s2, s1, s3]   (s3 to Miso; cuddler takes the snacky seat)
  altB  = [s1, s3, s2, s3]   (s3 to Biscuit; loner takes the snacky seat)

Probe band 820001+ (screens never touch cert bands), 5 seeds x 10k,
greedy, FIXED seats (the seat effect is the subject — no rotation).
Per seat: happiness, per-need means, distress ticks by need, activity
budget (groom-other / cosleep / eat / drink / move), grooming given.
"""
import json
import sys
from collections import Counter
from pathlib import Path

import cloudkitty
import numpy as np
import torch

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
sys.path.insert(0, str(EXPTS / "attn-clone-2026-08-12"))
sys.path.insert(1, str(EXPTS / "exp-004-meow-channel" / "trainer"))
from data import ACTION_NAMES  # noqa: E402
from model_attn_policy import EntityPolicy  # noqa: E402

CONFIG = str(EXPTS.parent / "cloudkitty.toml")
NEG_INF = float("-inf")
N_ACT = 34
NAMES = ["Miso", "Biscuit", "Pumpkin", "Kittybear"]
NEEDS = ["eat", "drink", "sleep", "play", "cuddle", "bath"]

SEATINGS = {
    "cand": ["s1", "s2", "s3", "s3"],
    "altA": ["s3", "s2", "s1", "s3"],
    "altB": ["s1", "s3", "s2", "s3"],
}


def load(n):
    ck = torch.load(EXPTS / "attn-ppo-2026-08-13" / "artifacts"
                    / f"attn-A1-{n}" / "policy-final.pt",
                    map_location="cpu", weights_only=True)
    m = EntityPolicy(**ck["hyper"])
    m.load_state_dict(ck["state_dict"])
    m.eval()
    return m


def group(a):
    if a.startswith("GroomKitty"):
        return "groom_other"
    if a.startswith("SleepWith"):
        return "cosleep"
    for g in ("Eat", "Drink"):
        if a == g:
            return g.lower()
    if a.startswith("Move"):
        return "move"
    return "other"


def main():
    models = {n: load(n) for n in ("s1", "s2", "s3")}
    report = {}
    for comp, seats in SEATINGS.items():
        agg = Counter()
        for si in range(5):
            seed = 820001 + si
            env = cloudkitty.ParallelEnv(CONFIG)
            obs, infos = env.reset(seed=seed)
            episode = 0
            for _t in range(10000):
                if not env.agents:
                    episode += 1
                    obs, infos = env.reset(seed=seed * 100 + episode)
                names = list(env.agents)
                ob = np.stack([np.asarray(obs[a], np.float32)
                               for a in names])
                mk = np.stack([np.asarray(infos[a]["mask"], np.uint8)
                               for a in names]).astype(bool)
                with torch.no_grad():
                    lg = np.zeros((len(names), 43), np.float32)
                    for nm in set(seats):
                        rows = [i for i, s in enumerate(seats) if s == nm]
                        lg[rows] = models[nm](
                            torch.from_numpy(ob[rows])).numpy()
                a0 = np.where(mk[:, :N_ACT], lg[:, :N_ACT],
                              NEG_INF).argmax(1)
                g0 = np.where(mk[:, N_ACT:], lg[:, N_ACT:],
                              NEG_INF).argmax(1)
                st = np.asarray(env.state(), np.float32)
                for k in range(4):
                    b = k * 32
                    agg[(k, "ticks")] += 1
                    agg[(k, "hap")] += float(st[b + 6]) * 100
                    for ni, nn in enumerate(NEEDS):
                        agg[(k, f"need_{nn}")] += float(st[b + ni]) * 100
                        if st[b + 20 + ni] > 0:
                            agg[(k, f"dist_{nn}")] += 1
                    agg[(k, group(ACTION_NAMES[a0[k]]))] += 1
                acts = {a: (int(a0[i]), int(g0[i]))
                        for i, a in enumerate(names)}
                obs, rew, term, trunc, infos = env.step(acts)
            print(f"{comp} seed {seed} done", flush=True)
        report[comp] = {"seats": seats,
                        "agg": {f"{k[0]}|{k[1]}": v for k, v in agg.items()}}
    (HERE / "pumpkin-diag.json").write_text(json.dumps(report, indent=1)
                                            + "\n")

    for comp, r in report.items():
        a = r["agg"]
        print(f"\n== {comp} {r['seats']} ==")
        for k in range(4):
            t = a[f"{k}|ticks"]
            dist = {n: a.get(f"{k}|dist_{n}", 0) for n in NEEDS}
            print(f" {NAMES[k]:9s}({r['seats'][k]}): "
                  f"hap {a[f'{k}|hap']/t:.2f} eat-need "
                  f"{a[f'{k}|need_eat']/t:.1f} | distress {dist} | "
                  f"groom {a.get(f'{k}|groom_other',0)/t:.3f} cosleep "
                  f"{a.get(f'{k}|cosleep',0)/t:.3f} eat "
                  f"{a.get(f'{k}|eat',0)/t:.3f} move "
                  f"{a.get(f'{k}|move',0)/t:.3f}")


if __name__ == "__main__":
    main()
