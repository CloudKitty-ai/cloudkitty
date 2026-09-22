#!/usr/bin/env python3
"""Cross-tab of nap starts by (sleep need < 5) x (on a beam) x (partner present) for one all-arm leg.

Tier 6 read aid (2026-09-21): says what the low-need nap starts the harness bins are, beam
sitting or cosleep joins. Same state layout and step loop as the cert harness; a nap start is
a tick asleep after a tick not asleep, as in `beam_account`.

    CERT_ARTS=<arts> lowneed_crosstab.py <config.toml> <seed> <slot> [ticks]
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
import cert_harness_fog as C  # noqa: E402


def crosstab(config, seed, slot, ticks=20_000):
    import cloudkitty
    import numpy as np
    import tomllib
    cfg = tomllib.load(open(config, "rb"))
    roster = len(cfg["kitty"])
    spec = f"ppo:{slot}"
    fwd = C.load_model(spec)
    env = cloudkitty.ParallelEnv(str(config), control=None, horizon=ticks)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    W, H = cfg["world"]["width"], cfg["world"]["height"]
    prev = np.zeros(roster, bool)
    tab = {}
    for _t in range(ticks):
        ob = np.stack([np.asarray(obs[a], np.float32) for a in names])
        ob[:, C.CLOCK_INDEX] = 0.0
        mk = np.stack([np.asarray(infos[a]["mask"], np.uint8) for a in names]).astype(bool)
        lg = np.asarray(fwd(ob, mk), np.float32)
        a0 = np.where(mk[:, :C.N_ACT], lg[:, :C.N_ACT], C.NEG_INF).argmax(1)
        g0 = np.where(mk[:, C.N_ACT:], lg[:, C.N_ACT:], C.NEG_INF).argmax(1)
        obs, _r, _te, _tr, infos = env.step({a: (int(a0[i]), int(g0[i])) for i, a in enumerate(names)})
        st = np.asarray(env.state(), np.float32)
        beams = {(x, y) for (_i, ty, x, y) in env.elements() if ty == "Sunbeam"}
        for k in range(roster):
            b = k * C.PER_KITTY
            asleep = int(st[b + C.ACT0:b + C.ACT0 + 7].argmax()) == C.SLEEP_ACT
            if asleep and not prev[k]:
                pos = (int(round(float(st[b + C.POS0]) * W)), int(round(float(st[b + C.POS0 + 1]) * H)))
                need = float(st[b + C.NEED_SLEEP]) * 100
                key = ("need<5" if need < 5 else "need>=5", "beam" if pos in beams else "ground",
                       "partner" if st[b + C.PARTNER_PRESENT] > 0.5 else "solo")
                tab[key] = tab.get(key, 0) + 1
            prev[k] = asleep
    tot = sum(tab.values())
    return {"config": str(config), "seed": seed, "slot": slot, "ticks": ticks, "starts": tot,
            "table": {" ".join(k): (v, round(v / tot, 3) if tot else None) for k, v in sorted(tab.items())}}


if __name__ == "__main__":
    print(json.dumps(crosstab(sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 20_000)))
