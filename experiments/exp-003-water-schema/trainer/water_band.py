"""§9.1 water band — the registered measurement for H1 and H2.

Geometry is exp-002's `dial_resolution.py`, deliberately unchanged so
the numbers are comparable to that instrument's record: the candidate
seated at BOTH policy seats (Miso = kitty_1, Kittybear = kitty_4),
scripted Biscuit playful / Pumpkin needs_driven, served world, 10 seeds
x 20k ticks, clock pinned to 0 (deploy semantics).

What exp-003 adds is the band and the split.

**Bounds are multiples of B**, the same-engine scripted baseline measured
by the same geometry — never absolutes. exp-002 registered "in-water
<= 3.0%" against a baseline of 1.63%; the engine moved, B became 3.44%,
and that sentence turned into one demanding the policy out-avoid the
ladder it is scored against. B is re-measured whenever the stamp moves.

  ceiling   inwater <= 1.5 * B_inwater
  floor     inwater >= 0.5 * B_inwater      (H2 — water preserved)
  lounging  lounge  <= B_lounge             (R + S + G on water)

**Grooming is split out and reported, never gated** (F-016): the wet-fur
charge raises the Bath need and grooming relieves it wherever the cat is
standing, so that channel is driven by the engine's own feedback loop.
Gating it would score the policy on the engine's behaviour.

Seeds 740_001-740_010: disjoint from training (>= 1e6), collection
(600_001-614_004), the registered shapes (700k-730k), the in-training
probes (40_001-3) and every prior experiment's band.

  python water_band.py <artifacts-dir>
"""
import argparse
import json
import sys
import tomllib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
REPO = EXP.parents[1]
sys.path.insert(1, str(REPO / "experiments" / "exp-001-bc-mappo" / "trainer"))

CONFIG = REPO / "cloudkitty.toml"      # overridable via --config
TICKS = 20_000
SEEDS = list(range(740_001, 740_011))  # overridable via --seed-base
NAMES = ["Miso", "Biscuit", "Pumpkin", "Kittybear"]
ACTIVITIES = ["Idle", "Resting", "Sleeping", "Eating", "Drinking",
              "Playing", "Grooming"]
LOUNGE = {"Resting", "Sleeping", "Grooming"}
PER_KITTY, POS_OFF, ACT_OFF = 32, 7, 9
POLICY_SEATS = ("Miso", "Kittybear")

# The same-engine scripted baseline (rebaseline-2026-08-06), policy seats.
B_INWATER, B_LOUNGE = 0.034352, 0.015000
CEIL, FLOOR = 1.5 * B_INWATER, 0.5 * B_INWATER

with CONFIG.open("rb") as f:
    _world = tomllib.load(f)["world"]
WIDTH, HEIGHT = _world["width"], _world["height"]


def run_seed(args):
    # Every world-dependent value travels in the job. Workers are *spawned*,
    # so they re-import this module and see its module-level defaults; an
    # override applied in main() never reaches them. That silently measured
    # the served world twice while reporting two different configs.
    policy_path, seed, config_path, width, height = args
    config, WIDTH, HEIGHT = Path(config_path), width, height
    import cloudkitty
    import numpy as np
    import torch
    from bc_loss import NEG_INF
    from model import MLP

    torch.set_num_threads(1)
    ck = torch.load(policy_path, map_location="cpu", weights_only=True)
    pol = MLP(ck["dims"])
    pol.load_state_dict(ck["state_dict"])
    pol.eval()

    control = {"kitty_2": "playful", "kitty_3": "needs_driven"}
    env = cloudkitty.ParallelEnv(str(config), horizon=TICKS, control=control)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)  # kitty_1 + kitty_4, both the candidate

    on_water = np.zeros((len(NAMES), len(ACTIVITIES)), np.int64)
    water_tiles = 0
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
                row = torch.from_numpy(np.array(obs[name])).unsqueeze(0)
                row[:, -1] = 0.0  # pin clock, deploy semantics
                mask = torch.from_numpy(
                    np.array(infos[name]["mask"]).astype(bool)).unsqueeze(0)
                acts[name] = int(pol(row).masked_fill(~mask, NEG_INF).argmax(-1))
            obs, _rew, _term, _trunc, infos = env.step(acts)

    return {"seed": seed,
            # Recorded so the record says which world was actually measured.
            # A --config that fails to reach the workers shows up here as an
            # unchanged tile count instead of as plausible numbers.
            "config": str(config),
            "mean_water_tiles": water_tiles / TICKS,
            "on_water_by_activity": {NAMES[k]: dict(zip(ACTIVITIES,
                                                        on_water[k].tolist()))
                                     for k in range(len(NAMES))}}


def verdict(results):
    total = TICKS * len(results) * len(POLICY_SEATS)
    acc = {a: 0 for a in ACTIVITIES}
    for r in results:
        for s in POLICY_SEATS:
            for a, c in r["on_water_by_activity"][s].items():
                acc[a] += c
    tiles = {round(r["mean_water_tiles"], 3) for r in results}
    configs = {r["config"] for r in results}
    assert len(configs) == 1, f"seeds disagree on the world: {configs}"
    inwater = sum(acc.values()) / total
    lounge = sum(v for a, v in acc.items() if a in LOUNGE) / total
    groom = acc["Grooming"] / total
    return {
        "inwater_share": inwater, "lounge_share": lounge,
        "grooming_on_water_share": groom,           # reported, NOT gated
        "lounge_excl_grooming": lounge - groom,
        "by_activity_share": {a: c / total for a, c in acc.items()},
        "config": next(iter(configs)),
        "mean_water_tiles": sum(tiles) / len(tiles),
        "B_inwater": B_INWATER, "B_lounge": B_LOUNGE,
        "ceiling": CEIL, "floor": FLOOR,
        "pass_ceiling": inwater <= CEIL,
        "pass_floor": inwater >= FLOOR,
        "pass_lounge": lounge <= B_LOUNGE,
        "band_pass": inwater <= CEIL and inwater >= FLOOR and lounge <= B_LOUNGE,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("artifacts", type=Path)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--config", type=Path, default=None,
                    help="world to measure on (default: the served config)")
    ap.add_argument("--seed-base", type=int, default=None)
    ap.add_argument("--only", default=None, help="measure one candidate")
    ap.add_argument("--label", default="water-band")
    args = ap.parse_args()
    global CONFIG, SEEDS, WIDTH, HEIGHT
    if args.config:
        CONFIG = args.config.resolve()
        with CONFIG.open("rb") as f:
            w = tomllib.load(f)["world"]
        WIDTH, HEIGHT = w["width"], w["height"]
    if args.seed_base:
        SEEDS = list(range(args.seed_base, args.seed_base + 10))

    outdir = args.artifacts / args.label
    outdir.mkdir(exist_ok=True, parents=True)
    cands = sorted(d for d in args.artifacts.glob("A[0-2]-*") if d.is_dir())
    if args.only:
        cands = [d for d in cands if d.name == args.only]

    print(f"§9.1 band — ceiling {CEIL*100:.2f}%  floor {FLOOR*100:.2f}%  "
          f"lounge {B_LOUNGE*100:.2f}%   (B_inwater {B_INWATER*100:.2f}%)\n")
    print(f"{'candidate':<18}{'in-water':>10}{'lounge':>9}{'(groom)':>10}"
          f"{'ceil':>6}{'floor':>7}{'lounge':>8}{'BAND':>7}")
    summary = {}
    for d in cands:
        pt = d / "policy-final.pt"
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            results = list(pool.map(
                run_seed,
                [(str(pt), s, str(CONFIG), WIDTH, HEIGHT) for s in SEEDS]))
        v = verdict(results)
        (outdir / f"{d.name}.json").write_text(
            json.dumps({"candidate": d.name, "seeds": SEEDS, "ticks": TICKS,
                        **v, "per_seed": results}, indent=1) + "\n")
        summary[d.name] = v
        print(f"{d.name:<18}{v['inwater_share']*100:>9.2f}%"
              f"{v['lounge_share']*100:>8.2f}%{v['grooming_on_water_share']*100:>9.2f}%"
              f"{'ok' if v['pass_ceiling'] else 'FAIL':>6}"
              f"{'ok' if v['pass_floor'] else 'FAIL':>7}"
              f"{'ok' if v['pass_lounge'] else 'FAIL':>8}"
              f"{'PASS' if v['band_pass'] else 'FAIL':>7}")
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    n = sum(v["band_pass"] for v in summary.values())
    print(f"\n§9.1: {n}/{len(summary)} candidates inside the registered band")


if __name__ == "__main__":
    main()
