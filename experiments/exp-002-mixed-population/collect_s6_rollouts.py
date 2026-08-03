"""Dataset v2, policy side: s6-seated rollouts on the frozen family.

One rollout per family variant, EVERY seat driven by the deployed s6
(greedy) — the most policy-like state distribution available for
critic pretraining, and the meow-label source for the scratch clone's
prior (register §1 lever 4; scripted meows are codec-inexpressible and
drop, s6's are chosen from the codec and encode).

Output matches bc-collect's per-rollout layout (obs/mask/label/kitty/
tick/reward/state npy + meta.json), with two documented divergences:
  - label = the policy's CHOSEN action (masked greedy argmax), not the
    engine's applied action — for cloning a policy, the chosen action
    IS the demonstrator mapping (meta: "labeling": "chosen").
  - clock: the env runs one 8000-tick world; obs/state clock features
    are overwritten with bc-collect's sawtooth ((t % 2000) / 2000),
    and the policy DECIDES on that sawtooth clock (training-era
    semantics — this is data collection, not deployment).

Usage: trainer/.venv/bin/python collect_s6_rollouts.py
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TRAINER = REPO / "experiments/exp-001-bc-mappo/trainer"
sys.path.insert(0, str(TRAINER))

import cloudkitty  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
from bc_loss import NEG_INF  # noqa: E402
from model import MLP  # noqa: E402

FAMILY = HERE / "family/v2-dial1.5"
OUT = HERE / "raw/bc-v2"
TICKS = 8_000
HORIZON = 2_000  # sawtooth period, = [rl.episode] horizon (bc-collect parity)
SEED_BASE = 500_001
ARTIFACT = TRAINER.parent / "artifacts/arm2-g0p998-s6/policy-final.pt"


def load_policy():
    ck = torch.load(ARTIFACT, map_location="cpu", weights_only=True)
    pol = MLP(ck["dims"])
    pol.load_state_dict(ck["state_dict"])
    pol.eval()
    return pol


def run_variant(ci, config, pol):
    seed = SEED_BASE + ci * 1_000
    env = cloudkitty.ParallelEnv(str(config), horizon=TICKS)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    ids = [int(n.split("_")[1]) for n in names]

    obs_rows, mask_rows, labels, kitties, ticks = [], [], [], [], []
    rewards, states = [], []
    with torch.no_grad():
        for t in range(TICKS):
            clock = (t % HORIZON) / HORIZON
            state = np.array(env.state(), dtype=np.float32)
            state[-1] = clock
            states.append(state)
            acts = {}
            for name, kid in zip(names, ids):
                row = np.array(obs[name], dtype=np.float32)
                row[-1] = clock
                mask = np.array(infos[name]["mask"]).astype(bool)
                x = torch.from_numpy(row).unsqueeze(0)
                m = torch.from_numpy(mask).unsqueeze(0)
                a = int(pol(x).masked_fill(~m, NEG_INF).argmax(-1))
                assert mask[a], "greedy label must be legal"
                acts[name] = a
                obs_rows.append(row)
                mask_rows.append(mask.astype(np.uint8))
                labels.append(a)
                kitties.append(kid)
                ticks.append(t)
            obs, rew, _te, _tr, infos = env.step(acts)
            rewards.append(rew[names[0]])

    d = OUT / f"config-{ci:02}-s6-rollout-00"
    d.mkdir(parents=True, exist_ok=True)
    np.save(d / "obs.npy", np.stack(obs_rows))
    np.save(d / "mask.npy", np.stack(mask_rows))
    np.save(d / "label.npy", np.array(labels, np.uint16))
    np.save(d / "kitty.npy", np.array(kitties, np.uint32))
    np.save(d / "tick.npy", np.array(ticks, np.uint32))
    np.save(d / "reward.npy", np.array(rewards, np.float32))
    np.save(d / "state.npy", np.stack(states))
    text = Path(config).read_text()
    meta = {
        "config": str(config.relative_to(REPO)),
        "config_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "world_seed": seed,
        "ticks": TICKS,
        "decisions": len(labels),
        "dropped_inexpressible": 0,
        "mask_mismatch": 0,
        "horizon": HORIZON,
        "expert": "policy:s6 (all seats, greedy)",
        "labeling": "chosen",
    }
    (d / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    classes = len(set(labels))
    print(f"config {ci:02}: {len(labels)} decisions, roster {len(names)}, "
          f"{classes} distinct label rows", flush=True)


def main():
    pol = load_policy()
    configs = sorted(FAMILY.glob("family-*.toml"))
    assert len(configs) == 15, configs
    for ci, cfg in enumerate(configs):
        run_variant(ci, cfg, pol)


if __name__ == "__main__":
    main()
