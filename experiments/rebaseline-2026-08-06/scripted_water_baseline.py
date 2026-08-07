"""Scripted water occupancy on the post-027 engine — exp-003's H2 floor.

Why this exists. exp-002 registered H2 as a one-sided gate (in-water
<= 3.0%), which is maximally satisfied by never touching water, and the
owner's stated preference is explicitly not to eliminate water behaviour.
exp-003 therefore registers a *band*, and a band needs a floor. The floor
must be a scripted cat's water use measured on the same engine — not a
remembered constant, because wet fur prices water for every decider,
scripted ladders included, so the floor itself moves when the dial does.

The old reference (0.31% lounging / 1.63% in-water) was measured at dial
1.5 on engine-defaults 12bf386241, taken from the Biscuit + Pumpkin seats
of runs whose Miso/Kittybear seats held policies. Two things have since
changed it: the dial is 3.5/60, and spec 027 gives the served world a
guaranteed 2x2 lake. Both move water occupancy, and in-water share is
exp-003's dependent variable.

Geometry is dial_resolution.py's, deliberately, so the numbers are
comparable: served world, seeds 1-10 x 20k ticks, per-tick position read
from the privileged state, water tiles from the pyo3 elements() accessor,
activity from the state's one-hot block.

The one difference is that no seat holds a policy. Since spec 026 parked
Miso and Kittybear on needs_driven, the served config is now entirely
scripted, so every seat can be driven by the engine and the run needs no
agent actions at all. That makes the measurement *better* than the old
reference rather than merely equivalent: the old one could only speak for
Biscuit and Pumpkin, while exp-003's policy will sit at Miso and
Kittybear. Both are reported -- the pair for continuity with the old
anchor, the policy seats for the floor the prereg should actually cite.

What this cannot report is Nash. Team reward reaches Python through the
per-agent reward dict, and a world driven entirely by config behaviours
has no agent seats. The policy-side Nash anchors died with the schema
bump regardless; exp-003 measures Nash against its own same-engine runs.

Usage (repo root):
  experiments/exp-001-bc-mappo/trainer/.venv/bin/python \
      experiments/rebaseline-2026-08-06/scripted_water_baseline.py \
      <out-label> [config.toml]

The optional config lets the same instrument run the decomposition
variants in configs/ (old dial, no edge penalty, both) so the move from
the pre-027 anchor can be attributed rather than guessed at.
"""
import json
import subprocess
import sys
import tomllib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CONFIG = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else REPO / "cloudkitty.toml"
OUTDIR = HERE / sys.argv[1]
TICKS = 20_000
SEEDS = list(range(1, 11))
NAMES = ["Miso", "Biscuit", "Pumpkin", "Kittybear"]
ACTIVITIES = ["Idle", "Resting", "Sleeping", "Eating", "Drinking",
              "Playing", "Grooming"]
LOUNGE = {"Resting", "Sleeping", "Grooming"}
PER_KITTY, POS_OFF, ACT_OFF = 32, 7, 9

# The seats exp-003's policy will occupy (the parked policy seats), and
# the seats the pre-027 reference was averaged over.
POLICY_SEATS = ("Miso", "Kittybear")
LEGACY_REFERENCE_SEATS = ("Biscuit", "Pumpkin")

with CONFIG.open("rb") as f:
    _cfg = tomllib.load(f)
WIDTH, HEIGHT = _cfg["world"]["width"], _cfg["world"]["height"]
# Drive every seat from the config's own behaviour, so this measures the
# served world as it actually runs rather than a hand-built seating.
CONTROL = {f"kitty_{k['id']}": k["behavior"] for k in _cfg["kitty"]}


def run_seed(seed):
    import cloudkitty
    import numpy as np

    env = cloudkitty.ParallelEnv(str(CONFIG), horizon=TICKS, control=CONTROL)
    env.reset(seed=seed)
    assert not env.possible_agents, (
        f"expected a fully scripted world, got seats {env.possible_agents}")

    on_water_act = np.zeros((len(NAMES), len(ACTIVITIES)), np.int64)
    water_tiles = 0
    for _t in range(TICKS):
        water = {(x, y) for (_i, kind, x, y) in env.elements() if kind == "Water"}
        water_tiles += len(water)
        state = env.state()
        for k in range(len(NAMES)):
            b = k * PER_KITTY
            x = int(round(state[b + POS_OFF] * WIDTH))
            y = int(round(state[b + POS_OFF + 1] * HEIGHT))
            if (x, y) in water:
                a = int(np.argmax(state[b + ACT_OFF:b + ACT_OFF + 7]))
                on_water_act[k, a] += 1
        env.step({})

    return {
        "seed": seed,
        "ticks": TICKS,
        "mean_water_tiles": water_tiles / TICKS,
        "on_water_by_activity": {
            NAMES[k]: dict(zip(ACTIVITIES, on_water_act[k].tolist()))
            for k in range(len(NAMES))
        },
    }


def shares(results, seats):
    """(lounging-on-water share, total in-water share) over `seats`."""
    total = TICKS * len(results) * len(seats)
    lounge = inwater = 0
    for r in results:
        for n in seats:
            acts = r["on_water_by_activity"][n]
            inwater += sum(acts.values())
            lounge += sum(v for a, v in acts.items() if a in LOUNGE)
    return lounge / total, inwater / total


def main():
    OUTDIR.mkdir(parents=True, exist_ok=False)  # never overwrite a record
    stamp = subprocess.run(
        [str(REPO / "target/release/kitty-eval"), "--brain", "needs_driven",
         "--config", str(CONFIG), "--seeds", "1", "--ticks", "1"],
        capture_output=True, text=True).stdout
    engine = next((ln.split()[-1] for ln in stamp.splitlines()
                   if ln.startswith("engine defaults ")), "unknown")

    results = []
    with ProcessPoolExecutor(max_workers=len(SEEDS)) as pool:
        for r in pool.map(run_seed, SEEDS):
            (OUTDIR / f"seed-{r['seed']}.json").write_text(
                json.dumps(r, indent=1) + "\n")
            results.append(r)
            print(f"seed {r['seed']}: {r['mean_water_tiles']:.1f} water tiles",
                  flush=True)

    policy_l, policy_w = shares(results, POLICY_SEATS)
    legacy_l, legacy_w = shares(results, LEGACY_REFERENCE_SEATS)
    all_l, all_w = shares(results, tuple(NAMES))
    verdict = {
        "engine_defaults_sha256": engine,
        "config": str(CONFIG.relative_to(REPO)),
        "seats": CONTROL,
        "seeds": SEEDS,
        "ticks": TICKS,
        "mean_water_tiles": sum(r["mean_water_tiles"] for r in results) / len(results),
        "policy_seats": {"seats": list(POLICY_SEATS),
                         "lounge_share": policy_l, "inwater_share": policy_w},
        "legacy_reference_seats": {"seats": list(LEGACY_REFERENCE_SEATS),
                                   "lounge_share": legacy_l,
                                   "inwater_share": legacy_w},
        "all_seats": {"lounge_share": all_l, "inwater_share": all_w},
        "per_seat": {
            n: {"lounge": sum(sum(v for a, v in r["on_water_by_activity"][n].items()
                                  if a in LOUNGE) for r in results) / (TICKS * len(results)),
                "inwater": sum(sum(r["on_water_by_activity"][n].values())
                               for r in results) / (TICKS * len(results))}
            for n in NAMES
        },
    }
    (OUTDIR / "verdict.json").write_text(json.dumps(verdict, indent=1) + "\n")
    print(json.dumps(verdict, indent=1))


if __name__ == "__main__":
    main()
