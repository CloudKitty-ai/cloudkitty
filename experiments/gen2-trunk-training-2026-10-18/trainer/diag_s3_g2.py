#!/usr/bin/env python3
"""Entry-3 s3 diagnosis (owner "Analyze the s3 failure", 2026-10-20):
read 1 — regenerate the three probe seeds at the halted checkpoint
(greedy, deterministic, run_probe's exact loop), record per-tick
engine-distress flags, locate the 317-streak (world, kitty, need
kinds, tick span), assert the recorded max streak reproduces;
read 2 — that kitty's actions/messages through the window from the
run's own probe-u249.npz; read 3 — the same kitty/world at u199 would
need the u199 checkpoint (ckpt-every 50 keeps checkpoint.pt rolling),
so the contrast uses the u199 TRACE (behavior) only, stated in the
output.

    diag_s3_g2.py [--out ../artifacts/diag-s3.json]
"""
import argparse
import json
import sys
import tomllib
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ARC = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parents[1] / "attn-oracle-2026-08-15"))

import cloudkitty  # noqa: E402
from obs_layout_v6 import N_ACT  # noqa: E402
from train_ppo_g2 import (DISTRESS_N, DISTRESS_OFF, PER_KITTY,  # noqa: E402
                          PROBE_SEEDS, SLOTS, kitty_distress_flags)

RUN = ARC / "artifacts/ppo-g2-trunk-s3"
CONFIG = HERE.parents[1] / "gen2-comparator-legs-2026-10-14/g2leg-20.toml"
NEEDS = ("eat", "drink", "sleep", "play", "cuddle", "bath")
NEG_INF = float("-inf")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ARC / "artifacts/diag-s3.json")
    ap.add_argument("--ticks", type=int, default=2000)
    args = ap.parse_args()

    from model_v6 import EntityPolicyV6
    clone_ck = torch.load(ARC / "artifacts/trunk-clone/trunk-clone.pt",
                          map_location="cpu", weights_only=True)
    policy = EntityPolicyV6(**clone_ck["hyper"])
    ck = torch.load(RUN / "checkpoint.pt", map_location="cpu",
                    weights_only=False)
    policy.load_state_dict(ck["policy"])
    policy.eval()
    # the stop checkpoint stores update+1 (resume convention); its
    # policy weights ARE the u249-probed ones (rk is built before the
    # probe block from the current policy)
    assert ck["update"] == 250, ck["update"]

    # read 1: regenerate, locate the streak
    worst_overall, located = 0, None
    per_seed = {}
    for s in PROBE_SEEDS:
        env = cloudkitty.ParallelEnv(str(CONFIG))
        obs, infos = env.reset(seed=s)
        roster = len(env.possible_agents)
        streak = np.zeros(roster, np.int64)
        worst = np.zeros(roster, np.int64)
        flags_t = []
        with torch.no_grad():
            for tick in range(args.ticks):
                st = np.asarray(env.state(), np.float32)
                k = st[:roster * PER_KITTY].reshape(roster, PER_KITTY)
                fl = (k[:, DISTRESS_OFF:DISTRESS_OFF + DISTRESS_N] > 0.5)
                flags_t.append(fl)
                flagged = fl.any(axis=1)
                streak = np.where(flagged, streak + 1, 0)
                worst = np.maximum(worst, streak)
                names = list(obs)
                o = torch.from_numpy(
                    np.stack([obs[a] for a in names]).astype(np.float32))
                m = torch.from_numpy(
                    np.stack([infos[a]["mask"] for a in names]).astype(bool))
                logits = policy(o)
                act = logits[:, :N_ACT].masked_fill(
                    ~m[:, :N_ACT], NEG_INF).argmax(-1).numpy()
                msg = logits[:, N_ACT:].masked_fill(
                    ~m[:, N_ACT:], NEG_INF).argmax(-1).numpy()
                obs, _r, _t, trunc, infos = env.step(
                    {a: (int(act[j]), int(msg[j]))
                     for j, a in enumerate(names)})
                if any(trunc.values()):
                    obs, infos = env.reset()
                    streak[:] = 0
        per_seed[s] = int(worst.max())
        if worst.max() > worst_overall:
            worst_overall = int(worst.max())
            kid = int(worst.argmax())
            fl3 = np.stack(flags_t)  # (ticks, roster, 6)
            on = fl3[:, kid, :].any(axis=1).astype(np.int8)
            # the maximal run's span
            best_len, best_end, cur = 0, -1, 0
            for t, v in enumerate(on):
                cur = cur + 1 if v else 0
                if cur > best_len:
                    best_len, best_end = cur, t
            span = (best_end - best_len + 1, best_end)
            kinds = {NEEDS[j]: int(fl3[span[0]:span[1] + 1, kid, j].sum())
                     for j in range(6)}
            located = {"seed": s, "kitty": kid, "streak": best_len,
                       "span": list(span), "flag_ticks_by_kind": kinds}
    assert worst_overall == 317, f"streak did not reproduce: {worst_overall}"

    # read 2: behavior through the window, from the run's own trace
    behav = {}
    for tag in ("probe-u249", "probe-u199"):
        z = np.load(RUN / f"{tag}.npz")
        sel = (z["seed"] == located["seed"]) & (z["kitty"] == located["kitty"])
        t = z["tick"][sel]
        act, msg, mask = z["act"][sel], z["msg"][sel], z["mask"][sel]
        if tag == "probe-u249":
            win = (t >= located["span"][0]) & (t <= located["span"][1])
        else:
            win = (t >= located["span"][0]) & (t <= located["span"][1])
        au, ac = np.unique(act[win], return_counts=True)
        mu, mc = np.unique(msg[win], return_counts=True)
        behav[tag] = {
            "window_rows": int(win.sum()),
            "act_hist": {int(a): int(c) for a, c in zip(au, ac)},
            "msg_hist": {int(a): int(c) for a, c in zip(mu, mc)},
            "mean_legal_acts": float(mask[win][:, :N_ACT].sum(1).mean())
            if win.any() else None}
    out = {"checkpoint_update": int(ck["update"]),
           "per_seed_max_streak": per_seed,
           "located": located, "behavior": behav,
           "contrast_note": "u199 uses the trace only (behavior); the "
                            "u199 policy ckpt was overwritten by the "
                            "rolling checkpoint"}
    print(json.dumps(out, indent=1))
    args.out.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
