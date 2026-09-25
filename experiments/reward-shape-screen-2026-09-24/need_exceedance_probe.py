"""Sleep-need exceedance probe (reward-shape screen: the measured basis
for the cost channel's threshold and target).

    CERT_ARTS=<root> need_exceedance_probe.py CONFIG SEAT_SPEC --out x.json

Runs SEAT_SPEC in all five seats (the all-arm seating) on CONFIG for
--seeds x --ticks, greedy, served clock, and records the fraction of
cat-ticks with sleep need above each threshold in {20, 30, 40, 50, 60},
pooled and per seed. Read-only: no battery is touched.
"""
import argparse
import json
import sys
import tomllib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
import cert_harness_fog as H  # noqa: E402

THRESHOLDS = (20, 30, 40, 50, 60)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("seat_spec")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--seed0", type=int, default=900201)
    ap.add_argument("--ticks", type=int, default=5000)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()

    import cloudkitty
    with open(a.config, "rb") as f:
        cfg = tomllib.load(f)
    roster = len(cfg["kitty"])
    model = H.load_model(a.seat_spec)
    per_seed = {}
    for i in range(a.seeds):
        seed = a.seed0 + i
        env = cloudkitty.ParallelEnv(a.config, horizon=a.ticks)
        obs, infos = env.reset(seed=seed)
        names = list(env.possible_agents)
        width, height = cfg["world"]["width"], cfg["world"]["height"]
        over = np.zeros(len(THRESHOLDS), np.int64)
        cf_state = 0   # cat-ticks asleep, off-beam, sleep need < 15 (the counterfactual-floor state)
        cf_depth2 = 0.0  # sum over those ticks of ((15 - need)/15)^2, the smooth shape's kernel
        sleep_ticks = 0
        offbeam_sleep = 0
        n = 0
        for _t in range(a.ticks):
            ob = np.stack([np.asarray(obs[x], np.float32) for x in names])
            ob[:, H.CLOCK_INDEX] = 0.0
            mk = np.stack([np.asarray(infos[x]["mask"], np.uint8) for x in names]).astype(bool)
            lg = np.asarray(model(ob, mk), np.float32)
            a0 = np.where(mk[:, :H.N_ACT], lg[:, :H.N_ACT], H.NEG_INF).argmax(1)
            g0 = np.where(mk[:, H.N_ACT:], lg[:, H.N_ACT:], H.NEG_INF).argmax(1)
            obs, _r, _te, _tr, infos = env.step({x: (int(a0[j]), int(g0[j])) for j, x in enumerate(names)})
            st = np.asarray(env.state(), np.float32)
            sleep = st[H.NEED_SLEEP:roster * H.PER_KITTY:H.PER_KITTY] * 100
            for ti, t in enumerate(THRESHOLDS):
                over[ti] += int((sleep > t).sum())
            beams = {(x, y) for (_id, ty, x, y) in env.elements() if ty == "Sunbeam"}
            for k in range(roster):
                b = k * H.PER_KITTY
                asleep = int(st[b + H.ACT0:b + H.ACT0 + 7].argmax()) == H.SLEEP_ACT
                if not asleep:
                    continue
                sleep_ticks += 1
                pos = (int(round(float(st[b + H.POS0]) * width)), int(round(float(st[b + H.POS0 + 1]) * height)))
                if pos not in beams:
                    offbeam_sleep += 1
                    if sleep[k] < 15:
                        cf_state += 1
                        cf_depth2 += ((15.0 - float(sleep[k])) / 15.0) ** 2
            n += roster
        per_seed[str(seed)] = {
            **{str(t): over[ti] / n for ti, t in enumerate(THRESHOLDS)},
            "cf_state_frac": cf_state / n,
            "cf_mean_depth2": (cf_depth2 / cf_state) if cf_state else None,
            "sleep_tick_frac": sleep_ticks / n,
            "offbeam_share_of_sleep": (offbeam_sleep / sleep_ticks) if sleep_ticks else None,
        }
    pooled = {k: float(np.mean([per_seed[s][k] for s in per_seed if per_seed[s][k] is not None]))
              for k in list(map(str, THRESHOLDS)) + ["cf_state_frac", "cf_mean_depth2", "sleep_tick_frac", "offbeam_share_of_sleep"]}
    out = {"config": a.config, "seat_spec": a.seat_spec, "seeds": sorted(per_seed),
           "ticks": a.ticks, "thresholds": list(THRESHOLDS),
           "pooled_frac_over": pooled, "per_seed": per_seed}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1))
    print(json.dumps({"seat": a.seat_spec, "config": Path(a.config).name, "pooled": pooled}))


if __name__ == "__main__":
    main()
