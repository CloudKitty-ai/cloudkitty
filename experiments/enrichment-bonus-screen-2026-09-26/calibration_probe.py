"""Enrichment-bonus screen: the calibration read (pre-declaration
baseline, the F-054 exceedance-probe pattern).

    CERT_ARTS=<root> calibration_probe.py CONFIG SEATING --out x.json

Runs the named harness SEATING (e.g. gen1-A: its five recorded minds
in their own seats) on CONFIG, greedy, served clock, and records what
the bonus channel's pins are set from:

- the distribution of each cat-tick's WORST (maximum) gate need --
  needs are urges, 0 sated, 100 starving -- over Eat, Drink, Sleep,
  Cuddle, Bath (Play excluded, it is the enrichment-linked need); the
  ramp thresholds come from its percentiles;
- play share, pooled and per seat -- the baseline P1 compares against;
- play-START events (a cat-tick entering Playing from any other
  activity), with the starter's worst gate need and whether any teammate
  held an active distress entry at that tick -- the P2/P3 baselines;
- happiness percentiles, for beta sizing.

Read-only; no battery is touched.
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

GATE_NEEDS = (0, 1, 2, 4, 5)  # Eat, Drink, Sleep, Cuddle, Bath (Play=3 excluded)
PLAY_ACT = 5                  # Activity one-hot order: Idle, Resting, Sleeping, Eating, Drinking, Playing, Grooming
N_DIST = 6
PCTS = (5, 10, 25, 50, 75, 90, 95)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("seating", choices=list(H.SEATINGS))
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--seed0", type=int, default=900301)
    ap.add_argument("--ticks", type=int, default=5000)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()

    import cloudkitty
    with open(a.config, "rb") as f:
        cfg = tomllib.load(f)
    roster = len(cfg["kitty"])
    models = [H.load_model(s) for s in H.SEATINGS[a.seating]]
    assert len(models) == roster, (a.seating, roster)
    per_seed = {}
    for i in range(a.seeds):
        seed = a.seed0 + i
        env = cloudkitty.ParallelEnv(a.config, horizon=a.ticks)
        obs, infos = env.reset(seed=seed)
        names = list(env.possible_agents)
        worst_needs = []        # worst (max) gate need per cat-tick, x100
        hap = []                # happiness per cat-tick, x100
        play_ticks = np.zeros(roster, np.int64)
        starts = 0
        start_worst_needs = []  # worst gate need at each play start, x100
        starts_teammate_dist = 0
        was_playing = np.zeros(roster, bool)
        n = 0
        for _t in range(a.ticks):
            ob = np.stack([np.asarray(obs[x], np.float32) for x in names])
            ob[:, H.CLOCK_INDEX] = 0.0
            mk = np.stack([np.asarray(infos[x]["mask"], np.uint8) for x in names]).astype(bool)
            lg = np.stack([np.asarray(models[j](ob[j:j + 1], mk[j:j + 1]), np.float32)[0]
                           for j in range(roster)])
            a0 = np.where(mk[:, :H.N_ACT], lg[:, :H.N_ACT], H.NEG_INF).argmax(1)
            g0 = np.where(mk[:, H.N_ACT:], lg[:, H.N_ACT:], H.NEG_INF).argmax(1)
            obs, _r, _te, _tr, infos = env.step({x: (int(a0[j]), int(g0[j])) for j, x in enumerate(names)})
            st = np.asarray(env.state(), np.float32)
            acts = np.array([int(st[k * H.PER_KITTY + H.ACT0:k * H.PER_KITTY + H.ACT0 + 7].argmax())
                             for k in range(roster)])
            playing = acts == PLAY_ACT
            dist_any = np.array([bool((st[k * H.PER_KITTY + H.DIST0:k * H.PER_KITTY + H.DIST0 + N_DIST] > 0.5).any())
                                 for k in range(roster)])
            for k in range(roster):
                b = k * H.PER_KITTY
                mn = float(max(st[b + g] for g in GATE_NEEDS)) * 100
                worst_needs.append(mn)
                hap.append(float(st[b + H.HAP]) * 100)
                if playing[k]:
                    play_ticks[k] += 1
                    if not was_playing[k]:
                        starts += 1
                        start_worst_needs.append(mn)
                        if dist_any[np.arange(roster) != k].any():
                            starts_teammate_dist += 1
            was_playing = playing
            n += roster
        mn_arr = np.array(worst_needs)
        smn = np.array(start_worst_needs) if start_worst_needs else np.array([np.nan])
        per_seed[str(seed)] = {
            "cat_ticks": n,
            "worst_gate_need_pcts": {str(p): float(np.percentile(mn_arr, p)) for p in PCTS},
            "happiness_pcts": {str(p): float(np.percentile(np.array(hap), p)) for p in PCTS},
            "play_share_pooled": float(play_ticks.sum() / n),
            "play_share_per_seat": [float(x / (n / roster)) for x in play_ticks],
            "play_starts": starts,
            "start_worst_need_pcts": {str(p): float(np.percentile(smn, p)) for p in PCTS},
            "starts_with_teammate_distressed": starts_teammate_dist,
        }
    pool_pcts = {str(p): float(np.mean([per_seed[s]["worst_gate_need_pcts"][str(p)] for s in per_seed])) for p in PCTS}
    out = {"config": a.config, "seating": a.seating, "seeds": sorted(per_seed),
           "ticks": a.ticks, "gate_needs": list(GATE_NEEDS),
           "pooled_worst_gate_need_pcts": pool_pcts,
           "pooled_play_share": float(np.mean([per_seed[s]["play_share_pooled"] for s in per_seed])),
           "per_seed": per_seed}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1))
    print(json.dumps({"pooled_worst_gate_need_pcts": pool_pcts,
                      "pooled_play_share": out["pooled_play_share"],
                      "play_starts": {s: per_seed[s]["play_starts"] for s in per_seed},
                      "starts_teammate_dist": {s: per_seed[s]["starts_with_teammate_distressed"] for s in per_seed}}))


if __name__ == "__main__":
    main()
