"""Social-valence probe for the attention seeds (owner ask 2026-08-14):
positioning and grouping per model — solo/pair/group time, contact,
who initiates proximity — from the privileged state, while the policy
drives from its own obs (the meow-econ geometry: served config, greedy,
seat rotation, seeds 820001+).

Per kitty-tick, from global_state v1 (32/kitty; pos@7-8, act@9-15,
partner present@17 idx@18): position, activity, pile partner. Derived:
manhattan nearest-dist; neighbors within 2 tiles -> configuration
{alone: 0 near, pair: exactly 1, group: >=2}; contact (dist <= 1).

Compositions: the three homogeneous worlds (native sociality) and one
full mix (who clusters with whom, cross-model pair census).
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
sys.path.insert(0, str(EXPTS / "attn-clone-2026-08-12"))
from model_attn_policy import EntityPolicy  # noqa: E402

REPO = EXPTS.parent
CONFIG = str(REPO / "cloudkitty.toml")
PPO_ART = EXPTS / "attn-ppo-2026-08-13" / "artifacts"
NEG_INF = float("-inf")
N_ACT = 34
PER_KITTY, POS, ACT, PPRES, PIDX = 32, 7, 9, 17, 18

TICKS = int(os.environ.get("VAL_TICKS", "10000"))
N_SEEDS = int(os.environ.get("VAL_SEEDS", "5"))
COMPS = {
    "hom-s1": ["s1"] * 4, "hom-s2": ["s2"] * 4, "hom-s3": ["s3"] * 4,
    "mix": ["s1", "s2", "s3", "s1"],
}

import tomllib
with open(CONFIG, "rb") as f:
    _cfg = tomllib.load(f)
W, H = _cfg["world"]["width"], _cfg["world"]["height"]
ROSTER = len(_cfg["kitty"])


def load(name):
    ck = torch.load(PPO_ART / f"attn-A1-{name}" / "policy-final.pt",
                    map_location="cpu", weights_only=True)
    m = EntityPolicy(**ck["hyper"])
    m.load_state_dict(ck["state_dict"])
    m.eval()
    return m


def main():
    models = {n: load(n) for n in {s for c in COMPS.values() for s in c}}
    report = {}
    for comp, seats in COMPS.items():
        agg = Counter()
        pair_census = Counter()   # (modelA, modelB) contact ticks, sorted
        for si in range(N_SEEDS):
            seed = 820001 + si
            sm = seats[si:] + seats[:si]
            env = cloudkitty.ParallelEnv(CONFIG)
            obs, infos = env.reset(seed=seed)
            episode = 0
            for _t in range(TICKS):
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
                    for nm in set(sm):
                        rows = [i for i, s in enumerate(sm) if s == nm]
                        lg[rows] = models[nm](
                            torch.from_numpy(ob[rows])).numpy()
                a0 = np.where(mk[:, :N_ACT], lg[:, :N_ACT],
                              NEG_INF).argmax(1)
                g0 = np.where(mk[:, N_ACT:], lg[:, N_ACT:],
                              NEG_INF).argmax(1)

                st = np.asarray(env.state(), np.float32)
                beams = {(x, y) for (_i, kind, x, y) in env.elements()
                         if kind == "Sunbeam"}
                pos, kact, pile = [], [], []
                for k in range(ROSTER):
                    b = k * PER_KITTY
                    pos.append((int(round(float(st[b + POS]) * W)),
                                int(round(float(st[b + POS + 1]) * H))))
                    a = int(np.argmax(st[b + ACT:b + ACT + 7]))
                    kact.append(a)
                    pile.append(a in (1, 2))  # Resting, Sleeping
                for k in range(ROSTER):
                    m = sm[k]
                    d = [abs(pos[k][0] - pos[j][0])
                         + abs(pos[k][1] - pos[j][1])
                         for j in range(ROSTER) if j != k]
                    near = sum(1 for x in d if x <= 2)
                    agg[(m, "ticks")] += 1
                    agg[(m, "nearest_sum")] += min(d)
                    agg[(m, "contact")] += int(min(d) <= 1)
                    agg[(m, ("alone", "pair", "group")[min(near, 2)])] += 1
                    b = k * PER_KITTY
                    sleeping = kact[k] == 2
                    if sleeping:
                        agg[(m, "sleep")] += 1
                        if pos[k] in beams:
                            agg[(m, "sleep_own_beam")] += 1
                    if st[b + PPRES] > 0.5:
                        pj = int(round(float(st[b + PIDX]) * (ROSTER - 1)))
                        agg[(m, "in_pile")] += 1
                        pair_census[tuple(sorted((m, sm[pj])))] += 1
                        if sleeping and (pos[k] in beams
                                         or (pile[pj] and pos[pj] in beams)):
                            agg[(m, "cosleep_on_beam")] += 1
                            if pos[k] not in beams:
                                agg[(m, "conducted")] += 1
                acts = {a: (int(a0[i]), int(g0[i]))
                        for i, a in enumerate(names)}
                obs, rew, term, trunc, infos = env.step(acts)
            print(f"{comp} seed {seed} done", flush=True)
        report[comp] = {
            "|".join(k) if isinstance(k, tuple) else k: v
            for k, v in agg.items()}
        report[comp]["pairs"] = {"+".join(k): v
                                 for k, v in pair_census.items()}
    out = HERE / "valence-report.json"
    out.write_text(json.dumps(report, indent=1) + "\n")
    for comp, r in report.items():
        print(f"\n== {comp} ==")
        for m in sorted({k.split("|")[0] for k in r if "|" in k}):
            t = r.get(f"{m}|ticks", 0)
            if not t:
                continue
            print(f" {m}: nearest {r.get(f'{m}|nearest_sum',0)/t:.2f} "
                  f"contact {r.get(f'{m}|contact',0)/t:.3f} "
                  f"alone/pair/group "
                  f"{r.get(f'{m}|alone',0)/t:.3f}/"
                  f"{r.get(f'{m}|pair',0)/t:.3f}/"
                  f"{r.get(f'{m}|group',0)/t:.3f} "
                  f"pile {r.get(f'{m}|in_pile',0)/t:.3f}")
        print("  pairs:", r["pairs"])


if __name__ == "__main__":
    main()
