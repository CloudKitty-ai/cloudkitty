"""Pre-wet-fur water baseline — a now-or-never descriptive measurement.

Captures water-tile behavior on the CURRENT (pre-wet-fur) engine over
the served Seating-B world (Miso=s6, Biscuit playful, Pumpkin
needs_driven, Kittybear=s3), seeds 1-10 x 20k ticks, pin_clock deploy
semantics — the exact pair-screen replay recipe, so mean Nash is a
checksum against pair-screen-2026-07-31.md (Seating B: 0.8977) proving
these are the same trajectories.

Per kitty, per tick, from the privileged state + the pyo3 `elements()`
accessor (water puddles are permanent single tiles; the set is
re-read every tick anyway):
  - ON a water tile (exact position match), split by activity
  - entries onto water (off->on transitions) for crossing/dwell stats
  - Drinking ticks split by distance to nearest water (0 = standing on
    the tile, 1 = beside it) — decides how much drinking would be
    incidentally exposed to an on-tile cost

Dies the moment wet-fur dynamics land (that is the point). Descriptive:
evaluate-once does not apply.

Usage: trainer/.venv/bin/python water_baseline.py [seed ...]
Writes one JSON per seed next to nothing precious:
  results/water-baseline-2026-08-01/seed-<n>.json
"""
import json
import sys
import tomllib
from pathlib import Path

TRAINER = Path(__file__).resolve().parent
sys.path.insert(0, str(TRAINER))

import cloudkitty  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
from bc_loss import NEG_INF  # noqa: E402
from model import MLP  # noqa: E402

REPO = TRAINER.parents[2]
CONFIG = REPO / "cloudkitty.toml"
OUTDIR = TRAINER.parent / "results" / "water-baseline-2026-08-01"
TICKS = 20_000
NAMES = ["Miso", "Biscuit", "Pumpkin", "Kittybear"]
ACTIVITIES = ["Idle", "Resting", "Sleeping", "Eating", "Drinking",
              "Playing", "Grooming"]
PER_KITTY = 32
POS_OFF, ACT_OFF = 7, 9

with CONFIG.open("rb") as f:
    _world = tomllib.load(f)["world"]
WIDTH, HEIGHT = _world["width"], _world["height"]


def load(path):
    ck = torch.load(path, map_location="cpu", weights_only=True)
    pol = MLP(ck["dims"])
    pol.load_state_dict(ck["state_dict"])
    pol.eval()
    return pol


def run_seed(seed, s6, s3):
    control = {"kitty_2": "playful", "kitty_3": "needs_driven"}
    seats = {"kitty_4": s3}
    env = cloudkitty.ParallelEnv(str(CONFIG), horizon=TICKS, control=control)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    roster = len(NAMES)

    on_water_act = np.zeros((roster, len(ACTIVITIES)), np.int64)
    entries = np.zeros(roster, np.int64)
    drink_dist = np.zeros((roster, 2), np.int64)  # Drinking at d=0 / d=1
    was_on = [False] * roster
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
                a = int(np.argmax(state[b + ACT_OFF:b + ACT_OFF + 7]))
                on = (x, y) in water
                if on:
                    on_water_act[k, a] += 1
                    if not was_on[k]:
                        entries[k] += 1
                was_on[k] = on
                if ACTIVITIES[a] == "Drinking":
                    d = min(abs(x - wx) + abs(y - wy) for wx, wy in water)
                    if d <= 1:
                        drink_dist[k, d] += 1
            acts = {}
            for name in names:
                row = torch.from_numpy(np.array(obs[name])).unsqueeze(0)
                row[:, -1] = 0.0  # pin clock, deploy semantics
                mask = torch.from_numpy(
                    np.array(infos[name]["mask"]).astype(bool)).unsqueeze(0)
                pol = seats.get(name, s6)
                acts[name] = int(pol(row).masked_fill(~mask, NEG_INF).argmax(-1))
            obs, rew, _term, _trunc, infos = env.step(acts)
            rew_sum += rew[names[0]]

    return {
        "seed": seed,
        "ticks": TICKS,
        "nash": rew_sum / TICKS,
        "n_water_tiles": len(water),
        "on_water_by_activity": {NAMES[k]: dict(zip(ACTIVITIES,
                                                    on_water_act[k].tolist()))
                                 for k in range(roster)},
        "entries": dict(zip(NAMES, entries.tolist())),
        "drinking_at_distance": {NAMES[k]: {"on_tile": int(drink_dist[k, 0]),
                                            "beside": int(drink_dist[k, 1])}
                                 for k in range(roster)},
    }


def main():
    seeds = [int(a) for a in sys.argv[1:]] or list(range(1, 11))
    OUTDIR.mkdir(exist_ok=True)
    s6 = load(TRAINER.parent / "artifacts/arm2-g0p998-s6/policy-final.pt")
    s3 = load(TRAINER.parent / "artifacts/arm2-g0p998-s3/policy-final.pt")
    for seed in seeds:
        r = run_seed(seed, s6, s3)
        out = OUTDIR / f"seed-{seed}.json"
        out.write_text(json.dumps(r, indent=1) + "\n")
        on = {k: sum(v.values()) for k, v in r["on_water_by_activity"].items()}
        print(f"seed {seed}: nash {r['nash']:.4f}, on-water ticks {on}",
              flush=True)


if __name__ == "__main__":
    main()
