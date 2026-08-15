"""World-side digest ablation (ROADMAP phase-0 rider; the exp-004
"does the chorus PAY" question, registered in the purr batteries).

Persistently zero a kind's digest slot in every hearer's obs before
the policy forward — the deafened world settles into its own
equilibrium (emission still legal; answers vanish because they were
causally hearing-driven). Deployed roster B, greedy, paired seeds vs
intact. Arms: intact, purr-deaf, followme-deaf, both-deaf.

Measures per arm: per-seat + team happiness, distress ticks, contact
share, cosleep decisions, groom decisions, emissions by kind.
Screen-grade (probe band, no world clustering).

Env: ABL_TICKS (10000), ABL_SEEDS (10), ABL_ARMS.
"""
import json
import os
import sys
from collections import Counter
from pathlib import Path

import cloudkitty
import numpy as np
import torch

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
sys.path.insert(0, str(EXPTS / "attn-cert-2026-08-14"))
sys.path.insert(1, str(EXPTS / "attn-clone-2026-08-12"))
sys.path.insert(2, str(EXPTS / "exp-001-bc-mappo" / "trainer"))
from cert_harness import load_model  # noqa: E402

CONFIG = str(EXPTS.parent / "cloudkitty.toml")
NEG_INF = float("-inf")
N_ACT = 34
SEATS = ["attn:s1", "mlp:A1-s2", "attn:s3", "attn:s3"]
NAMES = ["Miso", "Biscuit", "Pumpkin", "Kittybear"]
MSG_NAMES = ["Silent", "WantEat", "WantDrink", "FollowMe", "WantPlay",
             "WantCuddle", "Purr", "WantBath", "WantSleep"]
# digest kind indices (HEAD_KINDS order): FollowMe=2, Purr=5
ARMS = {"intact": [], "purr-deaf": [5], "followme-deaf": [2],
        "both-deaf": [2, 5]}

TICKS = int(os.environ.get("ABL_TICKS", "10000"))
N_SEEDS = int(os.environ.get("ABL_SEEDS", "10"))
RUN_ARMS = os.environ.get("ABL_ARMS", ",".join(ARMS)).split(",")


def main():
    models = {s: load_model(s) for s in set(SEATS)}
    report = {}
    for arm in RUN_ARMS:
        deaf = ARMS[arm]
        agg = Counter()
        for si in range(N_SEEDS):
            seed = 820001 + si
            env = cloudkitty.ParallelEnv(CONFIG)
            obs, infos = env.reset(seed=seed)
            ep = 0
            for _t in range(TICKS):
                if not env.agents:
                    ep += 1
                    obs, infos = env.reset(seed=seed * 100 + ep)
                names = list(env.agents)
                ob = np.stack([np.asarray(obs[a], np.float32)
                               for a in names])
                ds = ob.shape[1] - 33
                for k in deaf:
                    ob[:, ds + 4 * k:ds + 4 * k + 4] = 0.0
                mk = np.stack([np.asarray(infos[a]["mask"], np.uint8)
                               for a in names]).astype(bool)
                with torch.no_grad():
                    lg = np.zeros((4, 43), np.float32)
                    for s in set(SEATS):
                        rows = [i for i, x in enumerate(SEATS) if x == s]
                        lg[rows] = models[s](
                            torch.from_numpy(ob[rows])).numpy()
                a0 = np.where(mk[:, :N_ACT], lg[:, :N_ACT],
                              NEG_INF).argmax(1)
                g0 = np.where(mk[:, N_ACT:], lg[:, N_ACT:],
                              NEG_INF).argmax(1)
                st = np.asarray(env.state(), np.float32)
                pos = [(st[k * 32 + 7], st[k * 32 + 8]) for k in range(4)]
                for k in range(4):
                    b = k * 32
                    agg[(k, "ticks")] += 1
                    agg[(k, "hap")] += float(st[b + 6]) * 100
                    agg[(k, "distress")] += int(
                        (st[b + 20:b + 26] > 0).any())
                    d = min(abs(pos[k][0] - pos[j][0])
                            + abs(pos[k][1] - pos[j][1])
                            for j in range(4) if j != k) * 20
                    agg[(k, "contact")] += int(d <= 1.05)
                    if g0[k] > 0:
                        agg[("emit", MSG_NAMES[g0[k]])] += 1
                    an = ["Move" if a0[k] < 4 else "x"][0]
                    if 9 <= a0[k] <= 11:
                        agg[(k, "cosleep")] += 1
                    if 13 <= a0[k] <= 15:
                        agg[(k, "groom")] += 1
                acts = {a: (int(a0[i]), int(g0[i]))
                        for i, a in enumerate(names)}
                obs, rew, term, trunc, infos = env.step(acts)
            print(f"{arm} seed {seed} done", flush=True)
        report[arm] = {"|".join(map(str, k)): v for k, v in agg.items()}
    out = HERE / "results-raw.json"
    out.write_text(json.dumps(report, indent=1) + "\n")

    for arm in RUN_ARMS:
        r = report[arm]
        t = r["0|ticks"]
        team = sum(r[f"{k}|hap"] for k in range(4)) / (4 * t)
        emits = {kk.split("|")[1]: round(v / (4 * t) * 1000, 1)
                 for kk, v in r.items() if kk.startswith("emit|")}
        print(f"{arm:14s} team {team:.3f} | " + " ".join(
            f"{NAMES[k]} {r[f'{k}|hap']/t:.2f}" for k in range(4))
            + f" | contact {sum(r[f'{k}|contact'] for k in range(4))/(4*t):.3f}"
            + f" cosleep {sum(r.get(f'{k}|cosleep',0) for k in range(4))/(4*t):.3f}"
            + f" groom {sum(r.get(f'{k}|groom',0) for k in range(4))/(4*t):.3f}"
            + f" dist {sum(r.get(f'{k}|distress',0) for k in range(4))}"
            + f" | emits/1k {emits}")


if __name__ == "__main__":
    main()
