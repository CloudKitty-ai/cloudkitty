"""Spec-031 dial screen: sleep_relief_sunbeam in {6, 7, 8} with the
shared-warmth rule live (merged PR #216), scripted seats, served world.

Per the design doc (`../sunbeam-warmth-2026-08-13/design-input.md`):
scripted probes, paired seeds, read welfare + sleep structure + how
often the warmth rule actually fires. All four seats forced to
needs_driven via the control override (the served config's seats hold
policies, which cannot re-learn a dial — the screen wants the scripted
dynamics the F-016 discipline asks for).

Per tick, from the privileged state (global_state v1 layout: 32/kitty
— hap@6, pos@7-8, act one-hot@9-15, partner present@17 idx@18):
happiness; Sleeping/Resting; own tile on a sunbeam; partner's tile on
a sunbeam with partner in the pile (Sleeping|Resting) = the conduction
case. Nap episodes counted at not-Sleeping -> Sleeping transitions.

Usage (repo root):  .venv/bin/python sunbeam_screen.py
Env: SUN_TICKS (20000), SUN_SEEDS (10), SUN_DIALS ("6,7,8").
"""
import json
import os
import sys
import tomllib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BASE_CONFIG = REPO / "cloudkitty.toml"
TICKS = int(os.environ.get("SUN_TICKS", "20000"))
N_SEEDS = int(os.environ.get("SUN_SEEDS", "10"))
DIALS = [s for s in os.environ.get("SUN_DIALS", "6,7,8").split(",")]

PER_KITTY, HAP, POS, ACT, PPRES, PIDX = 32, 6, 7, 9, 17, 18
SLEEP_A, REST_A = 2, 1  # activity one-hot indices (state layout order)

with BASE_CONFIG.open("rb") as f:
    _cfg = tomllib.load(f)
WIDTH, HEIGHT = _cfg["world"]["width"], _cfg["world"]["height"]
ROSTER = len(_cfg["kitty"])
CONTROL = {f"kitty_{k['id']}": "needs_driven" for k in _cfg["kitty"]}


def make_config(dial):
    text = BASE_CONFIG.read_text()
    needle = "sleep_relief_sunbeam = "
    a = text.index(needle)
    b = text.index("\n", a)
    out = HERE / f"served-sunbeam-{dial}.toml"
    out.write_text(text[:a] + f"{needle}{dial}.0" + text[b:])
    return out


def run_seed(args):
    dial, cfg_path, seed = args
    import cloudkitty
    import numpy as np

    env = cloudkitty.ParallelEnv(str(cfg_path), horizon=TICKS,
                                 control=CONTROL)
    env.reset(seed=seed)
    assert not env.possible_agents

    c = {"hap": 0.0, "sleep": 0, "sleep_own_beam": 0, "sleep_conducted": 0,
         "cosleep": 0, "cosleep_on_beam": 0, "rest": 0, "naps": 0,
         "kitty_ticks": 0}
    prev_sleep = [False] * ROSTER
    for _t in range(TICKS):
        beams = {(x, y) for (_i, kind, x, y) in env.elements()
                 if kind == "Sunbeam"}
        st = np.asarray(env.state(), np.float32)
        pos, act, pile = [], [], []
        for k in range(ROSTER):
            b = k * PER_KITTY
            x = int(round(float(st[b + POS]) * WIDTH))
            y = int(round(float(st[b + POS + 1]) * HEIGHT))
            pos.append((x, y))
            a = int(np.argmax(st[b + ACT:b + ACT + 7]))
            act.append(a)
            pile.append(a in (SLEEP_A, REST_A))
        for k in range(ROSTER):
            b = k * PER_KITTY
            c["kitty_ticks"] += 1
            c["hap"] += float(st[b + HAP]) * 100
            sleeping = act[k] == SLEEP_A
            if act[k] == REST_A:
                c["rest"] += 1
            if sleeping and not prev_sleep[k]:
                c["naps"] += 1
            prev_sleep[k] = sleeping
            if not sleeping:
                continue
            c["sleep"] += 1
            own_beam = pos[k] in beams
            if own_beam:
                c["sleep_own_beam"] += 1
            if st[b + PPRES] > 0.5:
                pj = int(round(float(st[b + PIDX]) * (ROSTER - 1)))
                c["cosleep"] += 1
                partner_beam = pile[pj] and pos[pj] in beams
                if own_beam or partner_beam:
                    c["cosleep_on_beam"] += 1
                if partner_beam and not own_beam:
                    c["sleep_conducted"] += 1
        env.step({})
    c["dial"], c["seed"] = dial, seed
    return c


def main():
    out_dir = HERE / "results-raw"
    out_dir.mkdir(exist_ok=True)
    jobs = []
    for dial in DIALS:
        cfg = make_config(dial)
        jobs += [(dial, cfg, 1 + i) for i in range(N_SEEDS)]
    rows = []
    with ProcessPoolExecutor(max_workers=min(10, os.cpu_count() - 2)) as px:
        for r in px.map(run_seed, jobs):
            rows.append(r)
            print(f"dial {r['dial']} seed {r['seed']}: "
                  f"hap {r['hap']/r['kitty_ticks']:.2f} "
                  f"sleep-conducted {r['sleep_conducted']}", flush=True)
    (out_dir / "screen.json").write_text(json.dumps(rows, indent=1) + "\n")

    print("\n=== per dial (paired seeds 1-%d, %d ticks) ===" % (N_SEEDS,
                                                                TICKS))
    for dial in DIALS:
        rs = [r for r in rows if r["dial"] == dial]
        kt = sum(r["kitty_ticks"] for r in rs)
        sl = sum(r["sleep"] for r in rs)
        print(f"dial {dial}: hap {sum(r['hap'] for r in rs)/kt:.3f} | "
              f"sleep {sl/kt:.4f} | naps {sum(r['naps'] for r in rs)} "
              f"(mean len {sl/max(1,sum(r['naps'] for r in rs)):.1f}) | "
              f"own-beam {sum(r['sleep_own_beam'] for r in rs)/max(1,sl):.4f} | "
              f"cosleep|sleep {sum(r['cosleep'] for r in rs)/max(1,sl):.3f} | "
              f"cosleep-on-beam {sum(r['cosleep_on_beam'] for r in rs)/max(1,sl):.4f} | "
              f"conducted {sum(r['sleep_conducted'] for r in rs)/max(1,sl):.4f}")


if __name__ == "__main__":
    main()
