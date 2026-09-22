#!/usr/bin/env python3
"""Cross-tab of the scripted teacher's nap starts by (sleep need at or under the floor) x (warm: on a
beam, or a partner present) for an all-scripted leg. Spec 057 acceptance read (2026-09-21): under the
floor a nap begun at or under it with no beam underfoot and no partner relieves nothing; the rule on the
branch should drive that cell to zero. Same state layout and nap-start definition as the cert harness
(`beam_account`): a nap start is a tick asleep after a tick not asleep. Needs no policy artifacts.

    teacher_nap_crosstab.py <config.toml> <seed0> <n_seeds> [ticks]
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
import cert_harness_fog as C  # noqa: E402


def crosstab(config, seed, ticks=20_000):
    import cloudkitty
    import numpy as np
    import tomllib
    cfg = tomllib.load(open(config, "rb"))
    kitties = cfg["kitty"]
    roster = len(kitties)
    floor = float(cfg["actions"].get("sleep_floor_off_beam", 0.0))
    control = {f"kitty_{k['id']}": k["behavior"] for k in kitties}
    env = cloudkitty.ParallelEnv(str(config), control=control, horizon=ticks)
    env.reset(seed=seed)
    assert list(env.possible_agents) == [], "all seats must be engine-driven"
    W, H = cfg["world"]["width"], cfg["world"]["height"]
    prev = np.zeros(roster, bool)
    tab = {}
    sleep_ticks = 0
    for _t in range(ticks):
        env.step({})
        st = np.asarray(env.state(), np.float32)
        beams = {(x, y) for (_i, ty, x, y) in env.elements() if ty == "Sunbeam"}
        for k in range(roster):
            b = k * C.PER_KITTY
            asleep = int(st[b + C.ACT0:b + C.ACT0 + 7].argmax()) == C.SLEEP_ACT
            sleep_ticks += asleep
            if asleep and not prev[k]:
                pos = (int(round(float(st[b + C.POS0]) * W)), int(round(float(st[b + C.POS0 + 1]) * H)))
                need = float(st[b + C.NEED_SLEEP]) * 100
                key = ("need<=floor" if need <= floor else "need>floor", "beam" if pos in beams else "ground",
                       "partner" if st[b + C.PARTNER_PRESENT] > 0.5 else "solo")
                tab[key] = tab.get(key, 0) + 1
            prev[k] = asleep
    tot = sum(tab.values())
    return {"seed": seed, "floor": floor, "starts": tot, "sleep_share": sleep_ticks / (ticks * roster),
            "worthless": tab.get(("need<=floor", "ground", "solo"), 0),
            "table": {" ".join(k): v for k, v in sorted(tab.items())}}


def main():
    config, seed0, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    ticks = int(sys.argv[4]) if len(sys.argv) > 4 else 20_000
    for s in range(seed0, seed0 + n):
        print(json.dumps(crosstab(config, s, ticks)), flush=True)


if __name__ == "__main__":
    main()
