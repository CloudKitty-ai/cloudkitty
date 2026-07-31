"""Per-tick forensic replay of a policy artifact (F-008 investigation).

Replays a trained policy greedy on a chosen world/seed — the exact
deployment condition `kitty-eval` certifies — while logging per-tick,
per-kitty internals decoded from the privileged state vector
(global_state.rs layout: 32-float kitty blocks — needs[0:6], happiness
[6], pos[7:9], activity one-hot [9:16], ..., distress flags [20:26]).

Writes an .npz for later plotting plus a text summary: onset detection
(first sustained drop of rolling team reward below a threshold), per-
kitty happiness at onset, and action-class histograms before/after.

  trainer/.venv/bin/python trainer/forensics_replay.py \
      --policy artifacts/arm2-g0p998-s2/policy-final.pt --seed 8
"""

import argparse
from pathlib import Path

import cloudkitty
import numpy as np
import torch

from bc_loss import NEG_INF
from data import ACTION_GROUPS, ACTION_NAMES
from model import MLP

PER_KITTY = 32
HAPPINESS_OFF = 6
DISTRESS_OFF = 20


def replay(policy, config_path, seed, ticks, horizon=None, pin_clock=False):
    # config_path None = compiled defaults — the world `kitty-eval`
    # actually certifies on when invoked without --config (3 kitties).
    env = cloudkitty.ParallelEnv(str(config_path) if config_path else None,
                                 horizon=horizon)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    roster = len(names)
    log = {
        "reward": np.zeros(ticks, np.float64),
        "happiness": np.zeros((ticks, roster), np.float32),
        "distress": np.zeros((ticks, roster), np.int8),
        "pos": np.zeros((ticks, roster, 2), np.float32),
        "action": np.full((ticks, roster), -1, np.int16),
    }
    with torch.no_grad():
        for t in range(ticks):
            state = env.state()
            for k in range(roster):
                b = k * PER_KITTY
                log["happiness"][t, k] = state[b + HAPPINESS_OFF] * 100.0
                log["distress"][t, k] = int(state[b + DISTRESS_OFF:b + DISTRESS_OFF + 6].any())
                log["pos"][t, k] = state[b + 7:b + 9]
            to = torch.from_numpy(np.stack([obs[a] for a in names]))
            if pin_clock:
                to[:, -1] = 0.0  # deploy semantics: decide_sync pins the episode clock
            tm = torch.from_numpy(np.stack([infos[a]["mask"] for a in names]).astype(bool))
            acts = policy(to).masked_fill(~tm, NEG_INF).argmax(-1).numpy()
            obs, rew, _term, trunc, infos = env.step(
                {a: int(acts[j]) for j, a in enumerate(names)})
            log["reward"][t] = rew[names[0]]
            for j, a in enumerate(names):
                ap = infos[a]["applied_action"]
                log["action"][t, j] = -1 if ap is None else ap
            if any(trunc.values()):
                obs, infos = env.reset()
    return log, names


def group_of(idx):
    for g, rng in ACTION_GROUPS.items():
        if idx in rng:
            return g
    return "none"


def summarize(log, names, window, threshold):
    ticks = log["reward"].shape[0]
    roll = np.convolve(log["reward"], np.ones(window) / window, mode="valid")
    below = roll < threshold
    onset = None
    run = 0
    for i, b in enumerate(below):  # sustained: a full window below threshold
        run = run + 1 if b else 0
        if run >= window:
            onset = i + window - 1
            break
    print(f"rolling({window}) team reward: start {roll[:window].mean():.3f}  "
          f"min {roll.min():.3f} @ t={int(roll.argmin())}  end {roll[-window:].mean():.3f}")
    print(f"onset (rolling < {threshold} sustained {window}): "
          f"{'t=' + str(onset) if onset is not None else 'never'}")
    print(f"distress ticks per kitty: "
          + ", ".join(f"{names[k]}={int(log['distress'][:, k].sum())}"
                      for k in range(len(names))))
    segs = [("pre", 0, onset if onset else ticks)]
    if onset:
        segs.append(("post", onset, ticks))
    for label, a, b in segs:
        acts = log["action"][a:b].ravel()
        acts = acts[acts >= 0]
        hist = {}
        for g in ACTION_GROUPS:
            hist[g] = 0
        for x in acts:
            hist[group_of(int(x))] += 1
        total = max(1, len(acts))
        top = sorted(np.bincount(acts, minlength=40).argsort()[::-1][:5])
        print(f"[{label} t={a}..{b}] groups: "
              + " ".join(f"{g}={c / total:.3f}" for g, c in hist.items()))
        counts = np.bincount(acts, minlength=40)
        top5 = counts.argsort()[::-1][:5]
        print(f"[{label}] top actions: "
              + ", ".join(f"{ACTION_NAMES[i]}={counts[i] / total:.3f}" for i in top5))
        hap = log["happiness"][a:b]
        print(f"[{label}] happiness mean per kitty: "
              + ", ".join(f"{names[k]}={hap[:, k].mean():.1f}" for k in range(len(names))))
    return onset


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", type=Path, required=True)
    ap.add_argument("--config", type=Path, default=None,
                    help="world config; omit for compiled defaults (= bare kitty-eval)")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--ticks", type=int, default=20000)
    ap.add_argument("--window", type=int, default=500)
    ap.add_argument("--threshold", type=float, default=0.75)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--horizon", type=int, default=None,
                    help="continuous run: set to --ticks to remove episode resets")
    ap.add_argument("--pin-clock", action="store_true")
    args = ap.parse_args()

    ck = torch.load(args.policy, map_location="cpu", weights_only=True)
    policy = MLP(ck["dims"])
    policy.load_state_dict(ck["state_dict"])
    policy.eval()

    log, names = replay(policy, args.config, args.seed, args.ticks,
                        horizon=args.horizon, pin_clock=args.pin_clock)
    print(f"== {args.policy.parent.name} seed {args.seed} ({args.ticks} ticks) ==")
    summarize(log, names, args.window, args.threshold)
    tagbits = ("h" + str(args.horizon) if args.horizon else "episodic") + ("-pinned" if args.pin_clock else "")
    out = args.out or args.policy.parent / f"forensics-seed{args.seed}-{tagbits}.npz"
    np.savez_compressed(out, **log, names=np.array(names))
    print(f"saved {out}")


if __name__ == "__main__":
    main()
