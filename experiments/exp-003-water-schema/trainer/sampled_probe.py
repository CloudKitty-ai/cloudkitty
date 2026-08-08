"""Sampled selection on the deployed candidate — measure, do not adopt.

The exp-004 design inputs (§2) park sampled selection with a proposed
~20-minute test: the §9.1 water band and the deployed-composition
distress probe under `--sample`, against the committed greedy records on
the same world and seeds. This is that test.

Seating is the deployed composition (the candidate at Miso + Kittybear,
scripted Biscuit playful / Pumpkin needs_driven), served 20x20 world,
seeds 800_001-800_030 x 20k ticks — the exact geometry of the two greedy
anchors this compares against:

  water   screens/geometry-20x20-optE-2026-08-07/water-band/
          wb-opte-20x20/A2-m0-g998-s3.json     (seeds ..001-..010)
  crossings  screens/geometry-20x20-optE-2026-08-07/seeds/
          deployed-composition.json, optE rows (seeds ..001-..030)

Selection mirrors the engine's sampled path (`select` in
cloudkitty-rl/src/behavior.rs): temperature-1 softmax over the masked,
finite logits. The draw stream is torch's, seeded per run — a
*statistical* twin of the engine's DecisionRng, not a bit-identical one;
this probe compares distributions, never replays ticks.

Usage (repo root):
  experiments/exp-001-bc-mappo/trainer/.venv/bin/python \
      experiments/exp-003-water-schema/trainer/sampled_probe.py <out-dir>
"""
import json
import sys
import tomllib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
REPO = EXP.parents[1]
sys.path.insert(1, str(REPO / "experiments" / "exp-001-bc-mappo" / "trainer"))

CONFIG = REPO / "cloudkitty.toml"
PT = EXP / "artifacts" / "A2-m0-g998-s3" / "policy-final.pt"
TICKS = 20_000
SEEDS = list(range(800_001, 800_031))
WATER_SEEDS = set(range(800_001, 800_011))  # the paired greedy water record
NAMES = ["Miso", "Biscuit", "Pumpkin", "Kittybear"]
ACTIVITIES = ["Idle", "Resting", "Sleeping", "Eating", "Drinking",
              "Playing", "Grooming"]
LOUNGE = {"Resting", "Sleeping", "Grooming"}
PER_KITTY, POS_OFF, ACT_OFF = 32, 7, 9
POLICY_SEATS = ("Miso", "Kittybear")
NEEDS = ["eat", "drink", "sleep", "play", "cuddle", "bath"]
TH = 0.90

# The 20x20 same-engine scripted baseline, policy seats
# (rebaseline-2026-08-06/optE-B/verdict.json).
B_INWATER, B_LOUNGE = 0.0418025, 0.01831

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
    ck = torch.load(PT, map_location="cpu", weights_only=True)
    pol = MLP(ck["dims"])
    pol.load_state_dict(ck["state_dict"])
    pol.eval()
    gen = torch.Generator().manual_seed(seed)

    control = {"kitty_2": "playful", "kitty_3": "needs_driven"}
    env = cloudkitty.ParallelEnv(str(CONFIG), horizon=TICKS, control=control)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)

    on_water = np.zeros((len(NAMES), len(ACTIVITIES)), np.int64)
    water_tiles = 0
    counts = [0] * 6
    streak = {}
    longest = 0
    with torch.no_grad():
        for _t in range(TICKS):
            water = {(x, y) for (_i, kind, x, y) in env.elements()
                     if kind == "Water"}
            water_tiles += len(water)
            state = env.state()
            for k in range(len(NAMES)):
                b = k * PER_KITTY
                x = int(round(state[b + POS_OFF] * WIDTH))
                y = int(round(state[b + POS_OFF + 1] * HEIGHT))
                if (x, y) in water:
                    a = int(np.argmax(state[b + ACT_OFF:b + ACT_OFF + 7]))
                    on_water[k, a] += 1
            acts = {}
            for name in names:
                a = np.asarray(obs[name])
                hot = False
                for i in range(6):
                    if a[i] > TH:
                        counts[i] += 1
                        hot = True
                streak[name] = streak.get(name, 0) + 1 if hot else 0
                longest = max(longest, streak[name])
                row = torch.from_numpy(a).unsqueeze(0)
                row[:, -1] = 0.0  # pin clock, deploy semantics
                mask = torch.from_numpy(
                    np.array(infos[name]["mask"]).astype(bool)).unsqueeze(0)
                probs = torch.softmax(
                    pol(row).masked_fill(~mask, NEG_INF), dim=-1)
                acts[name] = int(torch.multinomial(probs, 1, generator=gen))
            obs, _rew, _term, _trunc, infos = env.step(acts)

    return {"seed": seed,
            "config": str(CONFIG),
            "mean_water_tiles": water_tiles / TICKS,
            "counts": counts,
            "longest": longest,
            "on_water_by_activity": {NAMES[k]: dict(zip(ACTIVITIES,
                                                        on_water[k].tolist()))
                                     for k in range(len(NAMES))}}


def water_verdict(results):
    total = TICKS * len(results) * len(POLICY_SEATS)
    acc = {a: 0 for a in ACTIVITIES}
    for r in results:
        for s in POLICY_SEATS:
            for a, c in r["on_water_by_activity"][s].items():
                acc[a] += c
    inwater = sum(acc.values()) / total
    lounge = sum(v for a, v in acc.items() if a in LOUNGE) / total
    return {
        "seeds": [r["seed"] for r in results],
        "inwater_share": inwater, "lounge_share": lounge,
        "grooming_on_water_share": acc["Grooming"] / total,
        "by_activity_share": {a: c / total for a, c in acc.items()},
        "B_inwater": B_INWATER, "B_lounge": B_LOUNGE,
        "ceiling": 1.5 * B_INWATER, "floor": 0.5 * B_INWATER,
        "pass_ceiling": inwater <= 1.5 * B_INWATER,
        "pass_floor": inwater >= 0.5 * B_INWATER,
        "pass_lounge": lounge <= B_LOUNGE,
        "band_pass": (0.5 * B_INWATER <= inwater <= 1.5 * B_INWATER
                      and lounge <= B_LOUNGE),
    }


def main():
    outdir = REPO / sys.argv[1]
    outdir.mkdir(parents=True, exist_ok=False)  # never overwrite a record

    results = []
    with ProcessPoolExecutor(max_workers=10) as pool:
        for r in pool.map(run_seed, SEEDS):
            results.append(r)
            print(f"seed {r['seed']}: crossings {sum(r['counts'])}, "
                  f"longest {r['longest']}, "
                  f"{r['mean_water_tiles']:.1f} water tiles", flush=True)

    configs = {r["config"] for r in results}
    tiles = {round(r["mean_water_tiles"], 3) for r in results}
    assert len(configs) == 1, f"seeds disagree on the world: {configs}"

    wv = water_verdict([r for r in results if r["seed"] in WATER_SEEDS])
    crossings = {
        "seeds": SEEDS,
        "seeds_with_crossing": sum(1 for r in results if sum(r["counts"]) > 0),
        "worst_streak": max(r["longest"] for r in results),
        "counts_by_need": {n: sum(r["counts"][i] for r in results)
                           for i, n in enumerate(NEEDS)},
    }
    verdict = {
        "candidate": "A2-m0-g998-s3", "selection": "sampled",
        "config": next(iter(configs)),
        "ticks": TICKS,
        "mean_water_tiles": sum(tiles) / len(tiles),
        "water_band_paired_seeds": wv,
        "deployed_composition": crossings,
    }
    for r in results:
        (outdir / f"seed-{r['seed']}.json").write_text(
            json.dumps(r, indent=1) + "\n")
    (outdir / "verdict.json").write_text(json.dumps(verdict, indent=1) + "\n")
    print(json.dumps(verdict, indent=1))


if __name__ == "__main__":
    main()
