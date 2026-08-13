"""Sunbeam-use probe: how much do the deployed policies sleep in sunbeams?

Self-block layout (observe.rs): [needs 6, happiness 1, pos 2, activity
one-hot 7, partner flag 1, SLEEPING-IN-SUNBEAM flag @17, wet 1,
progress 1, distress 6, pursuit 2, traits 6]. obs[17] is 1.0 iff the
cat is currently Sleeping{in_sunbeam: true}.

Counts per kitty-tick: chosen sleep decisions (solo 8 / with 9-11),
sunbeam-sleep flag, cosleep+sunbeam overlap. Run from exp-004 trainer/.
"""
import sys
import os
import numpy as np
import torch
import cloudkitty

sys.path.insert(0, os.getcwd())
from model import MLP  # noqa: E402

NEG_INF = float("-inf")
N_ACT = 34
SEEDS = [820001 + i for i in range(5)]
TICKS = 6000
CKPT = "../artifacts/A1-s2/policy-final.pt"
SLEEP_SOLO, SLEEP_WITH = 8, (9, 10, 11)
SUN_FLAG = 17

ck = torch.load(CKPT, map_location="cpu", weights_only=True)
model = MLP(ck["dims"])
model.load_state_dict(ck["state_dict"])
model.eval()

tot = {"ticks": 0, "sleep_solo": 0, "sleep_with": 0, "sun_flag": 0,
       "sun_and_with": 0, "sleep_any_flagtick": 0}
for seed in SEEDS:
    env = cloudkitty.ParallelEnv("../../../cloudkitty.toml")
    obs, infos = env.reset(seed=seed)
    episode = 0
    for _ in range(TICKS):
        if not env.agents:
            episode += 1
            obs, infos = env.reset(seed=seed * 100 + episode)
        agents = list(env.agents)
        ob = np.stack([np.asarray(obs[a], dtype=np.float32) for a in agents])
        mk = np.stack([np.asarray(infos[a]["mask"], dtype=np.uint8)
                       for a in agents])
        with torch.no_grad():
            lg = model(torch.from_numpy(ob)).numpy()
        m = mk.astype(bool)
        a = np.where(m[:, :N_ACT], lg[:, :N_ACT], NEG_INF).argmax(1)
        g = np.where(m[:, N_ACT:], lg[:, N_ACT:], NEG_INF).argmax(1)
        tot["ticks"] += len(agents)
        tot["sleep_solo"] += int((a == SLEEP_SOLO).sum())
        tot["sleep_with"] += int(np.isin(a, SLEEP_WITH).sum())
        flag = ob[:, SUN_FLAG] > 0.0
        tot["sun_flag"] += int(flag.sum())
        tot["sun_and_with"] += int((flag & np.isin(a, SLEEP_WITH)).sum())
        acts = {ag: (int(a[i]), int(g[i])) for i, ag in enumerate(agents)}
        obs, rew, term, trunc, infos = env.step(acts)
    print(f"seed {seed}: cum {tot}", flush=True)

t = tot["ticks"]
print(f"\nper-kitty-tick shares over {t}:")
print(f"  sleep decisions solo {tot['sleep_solo']/t:.4f}  "
      f"with {tot['sleep_with']/t:.4f}")
print(f"  SLEEPING-IN-SUNBEAM {tot['sun_flag']/t:.4f} "
      f"({tot['sun_flag']} ticks)")
print(f"  of which choosing SleepWith {tot['sun_and_with']}")
