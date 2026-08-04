"""Post-wet-fur calibration probe — the "after" side of the water baseline.

Same world, same recipe, same measurements as water_baseline.py (the
frozen "before" side, results/water-baseline-2026-08-01.md), rerun on
the wet-fur engine at the shipped starting dial (served config has no
[water] section, so engine defaults apply: bath_gain 1.5, ceiling 50).
New trajectories by design — dynamics changed, so the Nash checksum
does NOT apply; the before/after comparison IS the calibration
(register 2b: convert the dial into welfare delta).

Adds to the baseline instrument (new fields, nothing renamed):
  - bath-need stats per kitty: mean while on water, max anywhere
    (clamp check: must stay < safeguard), grooming ticks anywhere
  - drink-on-tile vs wading already split (the doc's Article I note)

Seeds run in a process pool (new machine, 18 cores); per-seed JSONs
land in results/water-calibration-2026-08-02/.

Usage: trainer/.venv/bin/python water_calibration.py [label] [config]
  label:  archive dir name under results/ (default the 08-02 record)
  config: world config override (default the served cloudkitty.toml) —
          lets the instrument anchor non-served regimes, e.g. the §9.1
          escalated dial. Seeds are fixed at 1..10 (the registered set).
"""
import json
import sys
import tomllib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

TRAINER = Path(__file__).resolve().parent
sys.path.insert(0, str(TRAINER))

REPO = TRAINER.parents[2]
CONFIG = (Path(sys.argv[2]).resolve() if len(sys.argv) > 2
          else REPO / "cloudkitty.toml")
# Each run archives under its own label: past dirs are committed records
# (a rerun must never overwrite them). Pass the label as argv[1].
OUTDIR = TRAINER.parent / "results" / (
    sys.argv[1] if len(sys.argv) > 1 else "water-calibration-2026-08-02"
)
TICKS = 20_000
NAMES = ["Miso", "Biscuit", "Pumpkin", "Kittybear"]
ACTIVITIES = ["Idle", "Resting", "Sleeping", "Eating", "Drinking",
              "Playing", "Grooming"]
PER_KITTY = 32
POS_OFF, ACT_OFF, BATH_OFF = 7, 9, 5

with CONFIG.open("rb") as f:
    _world = tomllib.load(f)["world"]
WIDTH, HEIGHT = _world["width"], _world["height"]


def load(path):
    import torch
    from model import MLP
    ck = torch.load(path, map_location="cpu", weights_only=True)
    pol = MLP(ck["dims"])
    pol.load_state_dict(ck["state_dict"])
    pol.eval()
    return pol


def run_seed(seed):
    import cloudkitty
    import numpy as np
    import torch
    from bc_loss import NEG_INF

    torch.set_num_threads(1)  # seeds parallelize across processes instead
    s6 = load(TRAINER.parent / "artifacts/arm2-g0p998-s6/policy-final.pt")
    s3 = load(TRAINER.parent / "artifacts/arm2-g0p998-s3/policy-final.pt")
    control = {"kitty_2": "playful", "kitty_3": "needs_driven"}
    seats = {"kitty_4": s3}
    env = cloudkitty.ParallelEnv(str(CONFIG), horizon=TICKS, control=control)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    roster = len(NAMES)

    on_water_act = np.zeros((roster, len(ACTIVITIES)), np.int64)
    entries = np.zeros(roster, np.int64)
    drink_dist = np.zeros((roster, 2), np.int64)  # Drinking at d=0 / d=1
    groom_total = np.zeros(roster, np.int64)
    bath_on_sum = np.zeros(roster)
    bath_max = np.zeros(roster)
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
                bath = state[b + BATH_OFF] * 100.0
                bath_max[k] = max(bath_max[k], bath)
                if ACTIVITIES[a] == "Grooming":
                    groom_total[k] += 1
                on = (x, y) in water
                if on:
                    on_water_act[k, a] += 1
                    bath_on_sum[k] += bath
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

    on_total = on_water_act.sum(axis=1)
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
        "bath": {NAMES[k]: {
            "mean_on_water": (bath_on_sum[k] / on_total[k]
                              if on_total[k] else None),
            "max": bath_max[k],
            "groom_ticks_total": int(groom_total[k]),
        } for k in range(roster)},
    }


def main():
    seeds = list(range(1, 11))  # the registered 10-seed set
    OUTDIR.mkdir(exist_ok=True)
    with ProcessPoolExecutor(max_workers=min(len(seeds), 10)) as pool:
        for r in pool.map(run_seed, seeds):
            out = OUTDIR / f"seed-{r['seed']}.json"
            out.write_text(json.dumps(r, indent=1) + "\n")
            on = {k: sum(v.values())
                  for k, v in r["on_water_by_activity"].items()}
            print(f"seed {r['seed']}: nash {r['nash']:.4f}, "
                  f"on-water ticks {on}", flush=True)


if __name__ == "__main__":
    main()
