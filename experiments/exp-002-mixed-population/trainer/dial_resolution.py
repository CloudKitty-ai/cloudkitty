"""§9.1 wet-fur dial resolution readout (prereg, registered rule).

The water_calibration instrument geometry with the PILOT seated at
both policy seats (Miso = kitty_1, Kittybear = kitty_4), scripted
Biscuit playful / Pumpkin needs_driven, served world, 10 seeds x 20k
ticks, pinned clock (deploy semantics). Two metrics, averaged over the
two seats:

  1. lounging-on-water share (Sleeping+Grooming+Resting on water /
     total ticks)  — pass <= 1.0%
  2. total in-water share                         — pass <= 3.0%

Anchors (frozen s6+s3, post-025 re-verification): 4.14% / 9.21%;
scripted 0.31% / 1.63%.

Usage (repo root or pilot worktree):
  trainer/.venv/bin/python experiments/exp-002-mixed-population/trainer/dial_resolution.py \
      <policy-final.pt> <out-label>
"""
import json
import sys
import tomllib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
EXP1_TRAINER = REPO / "experiments/exp-001-bc-mappo/trainer"
sys.path.insert(1, str(EXP1_TRAINER))

POLICY = Path(sys.argv[1]).resolve()
OUTDIR = HERE.parent / "results" / sys.argv[2]
CONFIG = REPO / "cloudkitty.toml"
TICKS = 20_000
NAMES = ["Miso", "Biscuit", "Pumpkin", "Kittybear"]
ACTIVITIES = ["Idle", "Resting", "Sleeping", "Eating", "Drinking",
              "Playing", "Grooming"]
LOUNGE = {"Resting", "Sleeping", "Grooming"}
PER_KITTY, POS_OFF, ACT_OFF = 32, 7, 9
PILOT_SEATS = ("Miso", "Kittybear")

with CONFIG.open("rb") as f:
    _world = tomllib.load(f)["world"]
WIDTH, HEIGHT = _world["width"], _world["height"]


def run_seed(seed):
    import cloudkitty
    import numpy as np
    import torch
    from bc_loss import NEG_INF
    from model import MLP

    torch.set_num_threads(1)
    ck = torch.load(POLICY, map_location="cpu", weights_only=True)
    pol = MLP(ck["dims"])
    pol.load_state_dict(ck["state_dict"])
    pol.eval()

    control = {"kitty_2": "playful", "kitty_3": "needs_driven"}
    env = cloudkitty.ParallelEnv(str(CONFIG), horizon=TICKS, control=control)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)  # kitty_1 + kitty_4, both the pilot
    roster = len(NAMES)

    on_water_act = np.zeros((roster, len(ACTIVITIES)), np.int64)
    rew_sum = 0.0
    with torch.no_grad():
        for _t in range(TICKS):
            water = {(x, y) for (_i, kind, x, y) in env.elements()
                     if kind == "Water"}
            state = env.state()
            for k in range(roster):
                b = k * PER_KITTY
                x = int(round(state[b + POS_OFF] * WIDTH))
                y = int(round(state[b + POS_OFF + 1] * HEIGHT))
                if (x, y) in water:
                    a = int(np.argmax(state[b + ACT_OFF:b + ACT_OFF + 7]))
                    on_water_act[k, a] += 1
            acts = {}
            for name in names:
                row = torch.from_numpy(np.array(obs[name])).unsqueeze(0)
                row[:, -1] = 0.0  # pin clock, deploy semantics
                mask = torch.from_numpy(
                    np.array(infos[name]["mask"]).astype(bool)).unsqueeze(0)
                acts[name] = int(pol(row).masked_fill(~mask, NEG_INF).argmax(-1))
            obs, rew, _term, _trunc, infos = env.step(acts)
            rew_sum += rew[names[0]]

    return {
        "seed": seed, "ticks": TICKS, "nash": rew_sum / TICKS,
        "on_water_by_activity": {NAMES[k]: dict(zip(ACTIVITIES,
                                                    on_water_act[k].tolist()))
                                 for k in range(roster)},
    }


def main():
    OUTDIR.mkdir(parents=True, exist_ok=False)  # never overwrite a record
    seeds = list(range(1, 11))
    results = []
    with ProcessPoolExecutor(max_workers=10) as pool:
        for r in pool.map(run_seed, seeds):
            (OUTDIR / f"seed-{r['seed']}.json").write_text(
                json.dumps(r, indent=1) + "\n")
            results.append(r)
            print(f"seed {r['seed']}: nash {r['nash']:.4f}", flush=True)

    # §9.1 metrics: averaged over the two pilot seats, pooled over seeds.
    total = TICKS * len(results)
    lounge_t = {n: 0 for n in PILOT_SEATS}
    water_t = {n: 0 for n in PILOT_SEATS}
    for r in results:
        for n in PILOT_SEATS:
            acts = r["on_water_by_activity"][n]
            water_t[n] += sum(acts.values())
            lounge_t[n] += sum(v for a, v in acts.items() if a in LOUNGE)
    lounge = sum(lounge_t.values()) / (2 * total)
    inwater = sum(water_t.values()) / (2 * total)
    per_seat = {n: {"lounge": lounge_t[n] / total, "inwater": water_t[n] / total}
                for n in PILOT_SEATS}
    verdict = {
        "policy": str(POLICY),
        "lounge_share": lounge, "inwater_share": inwater,
        "per_seat": per_seat,
        "pass_lounge_1pct": lounge <= 0.010,
        "pass_inwater_3pct": inwater <= 0.030,
        "both_pass": lounge <= 0.010 and inwater <= 0.030,
        "nash_mean": sum(r["nash"] for r in results) / len(results),
    }
    (OUTDIR / "verdict.json").write_text(json.dumps(verdict, indent=1) + "\n")
    print(json.dumps(verdict, indent=1))


if __name__ == "__main__":
    main()
