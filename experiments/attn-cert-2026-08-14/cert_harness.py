"""Certification harness for the frozen selection doc: drives an
arbitrary seat->model seating (mixed rosters kitty-eval cannot seat)
and computes the §9 welfare metrics with the welfare.rs definitions
transcribed verbatim:

  floor_touches:    ticks with happiness <= config happiness.floor
  low_share:        share of ticks with happiness < 45.0 (LOW_HAPPINESS)
  max_distress_age: longest per-(kitty, need) streak of the in_distress
                    flag (state distress flags), max over all
  team nash:        mean per-tick engine team reward (the engine's own
                    Nash welfare — never re-derived)

Validation protocol (deviation-31 env-chain-replay precedent, recorded
as D-001): (a) metric implementations exact-match kitty-eval on a
fully scripted world — identical trajectories by determinism, so any
metric difference is an implementation bug; (b) the policy path is
compared on a homogeneous artifact cell vs kitty-eval, where the only
permitted divergence is torch-vs-Rust forward at ~1e-5 logits
(greedy near-ties). Run `--validate` before any battery.

One continuous world per run (horizon = ticks), greedy, post-tick
metric reads — kitty-eval's convention.
"""
import argparse
import json
import os
import sys
import tomllib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
REPO = EXPTS.parent
sys.path.insert(0, str(EXPTS / "attn-clone-2026-08-12"))
sys.path.insert(1, str(EXPTS / "exp-001-bc-mappo" / "trainer"))

LOW_HAPPINESS = 45.0
PER_KITTY, HAP, DIST0 = 32, 6, 20
N_ACT = 34
NEG_INF = float("-inf")

SEATINGS = {
    # kitty order = config roster order: Miso, Biscuit, Pumpkin, Kittybear
    "candidate": ["attn:s1", "attn:s2", "attn:s3", "attn:s3"],
    "incumbent": ["mlp:A1-s2"] * 4,
    "val-s1": ["attn:s1"] * 4,  # validation cell vs kitty-eval only
}
BANDS = {"eval": 870_001, "stress": 880_001}


def load_model(spec):
    import torch
    if spec.startswith("attn:"):
        from model_attn_policy import EntityPolicy
        ck = torch.load(EXPTS / "attn-ppo-2026-08-13" / "artifacts"
                        / f"attn-A1-{spec[5:]}" / "policy-final.pt",
                        map_location="cpu", weights_only=True)
        m = EntityPolicy(**ck["hyper"])
    else:
        from model import MLP
        ck = torch.load(EXPTS / "exp-004-meow-channel" / "artifacts"
                        / spec[4:] / "policy-final.pt",
                        map_location="cpu", weights_only=True)
        m = MLP(ck["dims"])
    m.load_state_dict(ck["state_dict"])
    m.eval()
    return m


def run_one(args):
    seating_name, seed, ticks, config_path = args
    import cloudkitty
    import numpy as np
    import torch

    with open(config_path, "rb") as f:
        cfg = tomllib.load(f)
    floor = cfg["happiness"]["floor"]
    roster = len(cfg["kitty"])

    seats = SEATINGS[seating_name]
    models = {s: load_model(s) for s in set(seats)}
    env = cloudkitty.ParallelEnv(str(config_path), horizon=ticks)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    assert len(names) == roster == len(seats)

    hap_sum = np.zeros(roster)
    low_ticks = np.zeros(roster, np.int64)
    floor_touches = np.zeros(roster, np.int64)
    dist_streak = np.zeros((roster, 6), np.int64)
    max_dist_age = 0
    reward_sum, n_ticks = 0.0, 0

    for _t in range(ticks):
        if not env.agents:
            break  # horizon == ticks: should not trigger before the end
        ob = np.stack([np.asarray(obs[a], np.float32) for a in names])
        mk = np.stack([np.asarray(infos[a]["mask"], np.uint8)
                       for a in names]).astype(bool)
        with torch.no_grad():
            lg = np.zeros((roster, 43), np.float32)
            for s in set(seats):
                rows = [i for i, x in enumerate(seats) if x == s]
                lg[rows] = models[s](torch.from_numpy(ob[rows])).numpy()
        a0 = np.where(mk[:, :N_ACT], lg[:, :N_ACT], NEG_INF).argmax(1)
        g0 = np.where(mk[:, N_ACT:], lg[:, N_ACT:], NEG_INF).argmax(1)
        obs, rew, term, trunc, infos = env.step(
            {a: (int(a0[i]), int(g0[i])) for i, a in enumerate(names)})
        # post-tick reads, kitty-eval's convention
        st = np.asarray(env.state(), np.float32)
        reward_sum += float(rew[names[0]])
        n_ticks += 1
        for k in range(roster):
            b = k * PER_KITTY
            h = float(st[b + HAP]) * 100
            hap_sum[k] += h
            if h <= floor:
                floor_touches[k] += 1
            if h < LOW_HAPPINESS:
                low_ticks[k] += 1
            flags = st[b + DIST0:b + DIST0 + 6] > 0
            dist_streak[k] = np.where(flags, dist_streak[k] + 1, 0)
            max_dist_age = max(max_dist_age, int(dist_streak[k].max()))

    return {
        "seating": seating_name, "seed": seed, "ticks": n_ticks,
        "nash": reward_sum / max(1, n_ticks),
        "mean_happiness": (hap_sum / max(1, n_ticks)).round(4).tolist(),
        "low_share": (low_ticks / max(1, n_ticks)).round(6).tolist(),
        "floor_touches": floor_touches.tolist(),
        "max_distress_age": max_dist_age,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seating", choices=list(SEATINGS))
    ap.add_argument("band", choices=list(BANDS))
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--ticks", type=int, default=20_000)
    ap.add_argument("--config", type=Path, default=REPO / "cloudkitty.toml")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out-dir", type=Path, default=HERE / "results-raw")
    args = ap.parse_args()

    seed0 = BANDS[args.band]
    jobs = [(args.seating, seed0 + i, args.ticks, args.config)
            for i in range(args.seeds)]
    args.out_dir.mkdir(exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers) as px:
        for r in px.map(run_one, jobs):
            rows.append(r)
            print(f"{r['seating']} {args.band} seed {r['seed']}: "
                  f"nash {r['nash']:.4f} mda {r['max_distress_age']} "
                  f"ft {sum(r['floor_touches'])}", flush=True)
    out = args.out_dir / f"{args.seating}--{args.band}.json"
    out.write_text(json.dumps(rows, indent=1) + "\n")
    import numpy as np
    print(f"\n{args.seating} {args.band}: nash "
          f"{np.mean([r['nash'] for r in rows]):.4f} | worst mda "
          f"{max(r['max_distress_age'] for r in rows)} | floor "
          f"{sum(sum(r['floor_touches']) for r in rows)} | "
          f"max low_share {max(max(r['low_share']) for r in rows):.4f}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
