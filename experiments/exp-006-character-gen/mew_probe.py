"""Mew-function probe (report-only): does the mew digest move hearers?

Two causal legs on top of the observational deixis analysis (traces):

  audit  — replay a run normally; on every tick where a policy hearer's
           mew digest is fresh, forward that hearer a second time with
           the mew digest zeroed and count greedy flips on both heads,
           recording what flipped into what. Decision-level audibility,
           the meow-econ act-flip convention on the post-wall surface.
  deaf   — run the world with every policy seat EXCEPT the emitter seat
           deafened to mew (digest slots zeroed before forward) and
           write a cert-harness-shaped row; paired against a normal run
           on the same seed it measures in-vivo function (F-026's
           hearer-side ablation pattern, one kind, one composition).

Mew = MessageKind index 2; msg digest block at obs[164:224], 4 values
per kind -> mew slots 172:176 (recency, dx, dy, intensity).
"""
import argparse
import json
import sys
import tomllib
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cert_harness6 import (N_ACT, N_HEADS, NEG_INF, SEATINGS, load_model,
                           provenance)

MEW_A, MEW_B = 172, 176


def lab(i):
    if i < 4: return ["moveN", "moveS", "moveE", "moveW"][i]
    if i == 4: return "restSolo"
    if i < 8: return f"restK{i-5}"
    if i == 8: return "sleepSolo"
    if i < 12: return f"sleepK{i-9}"
    if i == 12: return "groomSelf"
    if i < 16: return f"groomK{i-13}"
    if i == 16: return "eat"
    if i == 17: return "drink"
    if i < 22: return f"chaseC{i-18}"
    if i < 25: return f"chaseK{i-22}"
    if i == 25: return "playSolo"
    if i < 30: return f"playC{i-26}"
    if i < 33: return f"playK{i-30}"
    return "idle"


def run(args):
    import cloudkitty

    with open(args.config, "rb") as f:
        cfg = tomllib.load(f)
    kitties = cfg["kitty"]
    seats = SEATINGS[args.seating]
    assert len(seats) == len(kitties)
    emitter_agent = f"kitty_{kitties[args.emitter_idx]['id']}"

    control = {f"kitty_{k['id']}": "needs_driven"
               for k, s in zip(kitties, seats) if s == "scripted"}
    models = {s: load_model(s) for s in set(seats) if s != "scripted"}
    env = cloudkitty.ParallelEnv(str(args.config),
                                 control=control or None, horizon=args.ticks)
    obs, infos = env.reset(seed=args.seed)
    names = list(env.possible_agents)
    seat_of = {f"kitty_{k['id']}": s for k, s in zip(kitties, seats)}

    flips_act = Counter()
    flips_msg = Counter()
    fresh_ticks = Counter()
    flip_pairs = Counter()
    reward_sum = 0.0

    for _t in range(args.ticks):
        ob = np.stack([np.asarray(obs[a], np.float32) for a in names])
        mk = np.stack([np.asarray(infos[a]["mask"], np.uint8)
                       for a in names]).astype(bool)
        if args.mode == "deaf":
            ob_act = ob.copy()
            for i, a in enumerate(names):
                if a != emitter_agent:
                    ob_act[i, MEW_A:MEW_B] = 0.0
        else:
            ob_act = ob

        def fwd_all(rows_in):
            lg = np.zeros((len(names), N_HEADS), np.float32)
            for s, f in models.items():
                rows = [i for i, a in enumerate(names) if seat_of[a] == s]
                if rows:
                    lg[rows] = np.asarray(f(rows_in[rows]), np.float32)
            return lg

        lg = fwd_all(ob_act)
        a0 = np.where(mk[:, :N_ACT], lg[:, :N_ACT], NEG_INF).argmax(1)
        g0 = np.where(mk[:, N_ACT:], lg[:, N_ACT:], NEG_INF).argmax(1)

        if args.mode == "audit":
            hear = [i for i, a in enumerate(names)
                    if a != emitter_agent and ob[i, MEW_A] > 0]
            if hear:
                ob_deaf = ob.copy()
                ob_deaf[:, MEW_A:MEW_B] = 0.0
                lg_d = fwd_all(ob_deaf)
                a_d = np.where(mk[:, :N_ACT], lg_d[:, :N_ACT],
                               NEG_INF).argmax(1)
                g_d = np.where(mk[:, N_ACT:], lg_d[:, N_ACT:],
                               NEG_INF).argmax(1)
                for i in hear:
                    s = seat_of[names[i]]
                    fresh_ticks[s] += 1
                    if a_d[i] != a0[i]:
                        flips_act[s] += 1
                        flip_pairs[(s, lab(int(a0[i])), lab(int(a_d[i])))] += 1
                    if g_d[i] != g0[i]:
                        flips_msg[s] += 1

        acts = {a: (int(a0[i]), int(g0[i])) for i, a in enumerate(names)}
        obs, rew, _term, _trunc, infos = env.step(acts)
        reward_sum += float(rew[names[0]])
        st = np.asarray(env.state(), np.float32)
        if _t == 0:
            roster = len(kitties)
            hap_sum = np.zeros(roster)
            dist_streak = np.zeros((roster, 6), np.int64)
            max_dist_age = 0
        for k in range(roster):
            b = k * 32
            hap_sum[k] += float(st[b + 6]) * 100
            flags = st[b + 20:b + 26] > 0
            dist_streak[k] = np.where(flags, dist_streak[k] + 1, 0)
            max_dist_age = max(max_dist_age, int(dist_streak[k].max()))

    out = {"mode": args.mode, "seating": args.seating, "seed": args.seed,
           "ticks": args.ticks, "emitter": emitter_agent,
           "nash": reward_sum / args.ticks,
           "mean_happiness": (hap_sum / args.ticks).round(4).tolist(),
           "max_distress_age": max_dist_age,
           "provenance": provenance(args.config)}
    if args.mode == "audit":
        out["fresh_ticks"] = dict(fresh_ticks)
        out["act_flips"] = dict(flips_act)
        out["msg_flips"] = dict(flips_msg)
        out["top_flip_pairs"] = [
            {"seat": s, "from": a, "to": b, "n": n}
            for (s, a, b), n in flip_pairs.most_common(30)]
        for s in fresh_ticks:
            print(f"{s}: fresh {fresh_ticks[s]}, act-flip "
                  f"{flips_act[s]/fresh_ticks[s]:.1%}, msg-flip "
                  f"{flips_msg[s]/fresh_ticks[s]:.1%}")
    else:
        print(f"deaf {args.seed}: nash {out['nash']:.4f}")
    args.out_dir.mkdir(exist_ok=True)
    p = args.out_dir / f"mew-{args.mode}-{args.seating}-{args.seed}.json"
    p.write_text(json.dumps(out, indent=1) + "\n")
    print("wrote", p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["audit", "deaf"])
    ap.add_argument("seating", choices=list(SEATINGS))
    ap.add_argument("seed", type=int)
    ap.add_argument("--ticks", type=int, default=20_000)
    ap.add_argument("--config", type=Path, default=HERE.parent.parent / "cloudkitty.toml")
    ap.add_argument("--emitter-idx", type=int, default=3,
                    help="roster index of the emitter seat (excluded "
                         "from deafening; default Kittybear)")
    ap.add_argument("--out-dir", type=Path, default=HERE / "results-raw")
    args = ap.parse_args()
    run(args)


if __name__ == "__main__":
    main()
