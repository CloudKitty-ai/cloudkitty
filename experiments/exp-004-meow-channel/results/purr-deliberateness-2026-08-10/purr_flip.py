"""Counterfactual purr test: on-policy states, erase the purr digest slot,
count decision flips. Greedy heads are deterministic, so any flip is exact
causal dependence of the listener's decision on the heard purr.

Digest layout (observe.rs): obs = [...][digest 32][clock 1]; per HEAD_KINDS
kind 4 values [recency, dx, dy, intensity]; Purr = HEAD_KINDS[5].
Run from trainer/: uses its model shim + env chaining pattern (h1_probe).
"""
import json
import sys
from collections import Counter
from pathlib import Path

import cloudkitty
import numpy as np
import torch

import os
sys.path.insert(0, os.getcwd())  # run with cwd = exp-004 trainer/
from model import MLP  # noqa: E402
from data import ACTION_NAMES, MSG_NAMES  # noqa: E402

NEG_INF = float("-inf")
N_ACT = 34
SEEDS = [820001 + i for i in range(5)]
TICKS = 6000
CKPT = Path("../artifacts/A1-s2/policy-final.pt")
CONFIG = "../../../cloudkitty.toml"


def masked_pair(logits, mask):
    m = mask.astype(bool)
    a = np.where(m[:, :N_ACT], logits[:, :N_ACT], NEG_INF).argmax(axis=1)
    g = np.where(m[:, N_ACT:], logits[:, N_ACT:], NEG_INF).argmax(axis=1)
    return a, g


def main():
    ck = torch.load(CKPT, map_location="cpu", weights_only=True)
    model = MLP(ck["dims"])
    model.load_state_dict(ck["state_dict"])
    model.eval()

    rows = {"audible": 0, "silent_ctl": 0}
    act_flips = {"audible": 0, "silent_ctl": 0}
    msg_flips = {"audible": 0, "silent_ctl": 0}
    null_act_flips = 0  # WantEat-slot zeroing on the same audible rows
    null_msg_flips = 0
    flip_pairs = Counter()
    msg_flip_pairs = Counter()
    kitty_ticks = 0

    for seed in SEEDS:
        env = cloudkitty.ParallelEnv(CONFIG)
        obs, infos = env.reset(seed=seed)
        episode = 0
        for _ in range(TICKS):
            if not env.agents:
                episode += 1
                obs, infos = env.reset(seed=seed * 100 + episode)
            agents = list(env.agents)
            ob = np.stack([np.asarray(obs[a], dtype=np.float32)
                           for a in agents])
            mk = np.stack([np.asarray(infos[a]["mask"], dtype=np.uint8)
                           for a in agents])
            w = ob.shape[1]
            ds = w - 33
            purr = slice(ds + 5 * 4, ds + 6 * 4)
            wanteat = slice(ds + 0, ds + 4)

            with torch.no_grad():
                base = model(torch.from_numpy(ob)).numpy()
            zp = ob.copy()
            zp[:, purr] = 0.0
            with torch.no_grad():
                cf = model(torch.from_numpy(zp)).numpy()
            zn = ob.copy()
            zn[:, wanteat] = 0.0
            with torch.no_grad():
                nl = model(torch.from_numpy(zn)).numpy()

            a0, g0 = masked_pair(base, mk)
            a1, g1 = masked_pair(cf, mk)
            a2, g2 = masked_pair(nl, mk)
            audible = ob[:, purr.start] > 0.0

            for i in range(len(agents)):
                key = "audible" if audible[i] else "silent_ctl"
                rows[key] += 1
                if a0[i] != a1[i]:
                    act_flips[key] += 1
                    if audible[i]:
                        flip_pairs[(ACTION_NAMES[a0[i]],
                                    ACTION_NAMES[a1[i]])] += 1
                if g0[i] != g1[i]:
                    msg_flips[key] += 1
                    if audible[i]:
                        msg_flip_pairs[(MSG_NAMES[g0[i]],
                                        MSG_NAMES[g1[i]])] += 1
                if audible[i]:
                    null_act_flips += a0[i] != a2[i]
                    null_msg_flips += g0[i] != g2[i]

            acts = {a: (int(a0[i]), int(g0[i]))
                    for i, a in enumerate(agents)}
            obs, rew, term, trunc, infos = env.step(acts)
            kitty_ticks += len(agents)
        print(f"seed {seed} done ({kitty_ticks} kitty-ticks cum)")

    out = {
        "kitty_ticks": kitty_ticks,
        "rows": rows,
        "purr_audible_share": rows["audible"] / max(1, sum(rows.values())),
        "act_flip_rate_audible": act_flips["audible"] / max(1, rows["audible"]),
        "msg_flip_rate_audible": msg_flips["audible"] / max(1, rows["audible"]),
        "act_flip_rate_silent_sanity": act_flips["silent_ctl"] / max(1, rows["silent_ctl"]),
        "msg_flip_rate_silent_sanity": msg_flips["silent_ctl"] / max(1, rows["silent_ctl"]),
        "null_wanteat_act_flip_rate": null_act_flips / max(1, rows["audible"]),
        "null_wanteat_msg_flip_rate": null_msg_flips / max(1, rows["audible"]),
        "top_act_flips": [(f"{a}->{b}", n)
                          for (a, b), n in flip_pairs.most_common(12)],
        "top_msg_flips": [(f"{a}->{b}", n)
                          for (a, b), n in msg_flip_pairs.most_common(8)],
    }
    print(json.dumps(out, indent=1))
    (Path(__file__).parent / "purr_flip.json").write_text(
        json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
