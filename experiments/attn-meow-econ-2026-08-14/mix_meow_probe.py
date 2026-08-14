"""Meow economics probe for the attention PPO seeds (owner ask,
2026-08-14): who says what, in which circumstances, with what causal
effect on hearers — per seed AND with the seeds mixed in one world.

One composition = a seat->model assignment over the served world's four
seats, rotated across probe seeds so seat traits don't confound model
identity. Per composition this collects, in one pass:

- head census + emission contexts per (model, kind): related-need level,
  happiness, distance-to-nearest, moving share — each against the
  matched declined-legal baseline (the house pattern).
- reply structure: (speaker model, kind) -> (answerer model, kind)
  within the 10-tick window, speaker attribution reconstructed from our
  own emission log (freshest-other rule, matching freshest_audible).
- per-kind causal flips: zero kind k's digest slot, re-forward, count
  decision changes on audible rows — keyed (speaker model, hearer
  model, kind), plus Move->Move steering toward/away and top flip
  pairs. Greedy determinism = exact causality (the flip-test lineage).
- welfare: per-seat happiness, distress-flag ticks, activity census.

Run from the repo root with exp-001's venv. Env knobs:
MEOW_TICKS (default 10000), MEOW_SEEDS (default 5), MEOW_COMPS
(comma list; default all), MEOW_SMOKE=1 substitutes the BC clone for
every seat (mechanics check before the PPO finals exist).
"""
import json
import os
import sys
from collections import Counter
from pathlib import Path

import cloudkitty
import numpy as np
import torch

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
sys.path.insert(0, str(EXPTS / "attn-clone-2026-08-12"))
sys.path.insert(1, str(EXPTS / "exp-004-meow-channel" / "trainer"))

from data import ACTION_NAMES  # noqa: E402
from model_attn_policy import EntityPolicy  # noqa: E402

REPO = EXPTS.parent
CONFIG = str(REPO / "cloudkitty.toml")
PPO_ART = EXPTS / "attn-ppo-2026-08-13" / "artifacts"

NEG_INF = float("-inf")
N_ACT, N_KINDS, WINDOW = 34, 8, 10
MSG_NAMES = ["Silent", "WantEat", "WantDrink", "FollowMe", "WantPlay",
             "WantCuddle", "Purr", "WantBath", "WantSleep"]
KIND_NAMES = MSG_NAMES[1:]
NEED_IDX = {"WantEat": 0, "WantDrink": 1, "WantSleep": 2, "WantPlay": 3,
            "WantCuddle": 4, "WantBath": 5}  # NeedKind::ALL order
CHASE_IDX = {i for i, n in enumerate(ACTION_NAMES) if n.startswith("Chase")}
MOVE_D = {0: (0, -1), 1: (1, 0), 2: (0, 1), 3: (-1, 0)}

TICKS = int(os.environ.get("MEOW_TICKS", "10000"))
N_SEEDS = int(os.environ.get("MEOW_SEEDS", "5"))
SMOKE = os.environ.get("MEOW_SMOKE") == "1"

COMPOSITIONS = {
    "hom-s1": ["s1", "s1", "s1", "s1"],
    "hom-s2": ["s2", "s2", "s2", "s2"],
    "hom-s3": ["s3", "s3", "s3", "s3"],
    "mix-4th-s1": ["s1", "s2", "s3", "s1"],
    "mix-4th-s2": ["s1", "s2", "s3", "s2"],
    "mix-4th-s3": ["s1", "s2", "s3", "s3"],
}


def load_model(name):
    if SMOKE:
        path = EXPTS / "attn-clone-2026-08-12" / "artifacts" / "attn-clone.pt"
    else:
        path = PPO_ART / f"attn-A1-{name}" / "policy-final.pt"
    ck = torch.load(path, map_location="cpu", weights_only=True)
    m = EntityPolicy(**ck["hyper"])
    m.load_state_dict(ck["state_dict"])
    m.eval()
    return m


def masked_pair(logits, mk):
    m = mk.astype(bool)
    a = np.where(m[:, :N_ACT], logits[:, :N_ACT], NEG_INF).argmax(1)
    g = np.where(m[:, N_ACT:], logits[:, N_ACT:], NEG_INF).argmax(1)
    return a, g


def forward_by_model(models, seat_model, ob):
    logits = np.zeros((ob.shape[0], 43), np.float32)
    with torch.no_grad():
        for name in set(seat_model):
            rows = [i for i, s in enumerate(seat_model) if s == name]
            logits[rows] = models[name](
                torch.from_numpy(ob[rows])).numpy()
    return logits


def dist_nearest(ob_row, max_dist):
    ds = []
    for k in range(3):
        base = 34 + 20 * k
        if ob_row[base] > 0:
            ds.append(float(ob_row[base + 3]) * max_dist)
    return float(min(ds)) if ds else float(max_dist)


def run_composition(comp, seats, models, out_dir):
    agg = {
        "comp": comp, "seats": seats, "ticks": TICKS, "n_seeds": N_SEEDS,
        "kitty_ticks": 0,
        "emit": Counter(), "declined": Counter(),
        "ctx": {},          # (model,kind,which) -> [need,hap,dist,moving,n]
        "reply": Counter(), "flip": Counter(), "steer": Counter(),
        "flip_pairs": Counter(), "hap": Counter(), "hap_n": Counter(),
        "distress": Counter(), "acts": Counter(),
    }

    def ctx_add(model, kind, which, need, hap, dist, moving):
        key = (model, kind, which)
        c = agg["ctx"].setdefault(key, [0.0, 0.0, 0.0, 0, 0])
        c[0] += need
        c[1] += hap
        c[2] += dist
        c[3] += moving
        c[4] += 1

    import tomllib
    with open(CONFIG, "rb") as f:
        world = tomllib.load(f)["world"]
    max_dist = world["width"] + world["height"]

    for si in range(N_SEEDS):
        seed = 820001 + si
        seat_model = seats[si:] + seats[:si]  # rotate: traits != model
        env = cloudkitty.ParallelEnv(CONFIG)
        obs, infos = env.reset(seed=seed)
        episode = 0
        recent = []  # (tick, seat_idx, kind_idx) emission log
        for t in range(TICKS):
            if not env.agents:
                episode += 1
                obs, infos = env.reset(seed=seed * 100 + episode)
                recent.clear()
            names = list(env.agents)
            ob = np.stack([np.asarray(obs[a], np.float32) for a in names])
            mk = np.stack([np.asarray(infos[a]["mask"], np.uint8)
                           for a in names])
            w = ob.shape[1]
            ds = w - 33
            sm = [seat_model[j] for j in range(len(names))]

            base = forward_by_model(models, sm, ob)
            a0, g0 = masked_pair(base, mk)

            # freshest-other speaker per (hearer, kind), from our own log
            recent = [r for r in recent if t - r[0] < WINDOW]
            speaker = {}
            for (rt, rj, rk) in recent:
                for i in range(len(names)):
                    if i != rj:
                        speaker[(i, rk)] = rj  # later entries overwrite

            audible_kinds = [k for k in range(N_KINDS)
                             if (ob[:, ds + 4 * k] > 0).any()]
            for k in audible_kinds:
                zo = ob.copy()
                zo[:, ds + 4 * k:ds + 4 * k + 4] = 0.0
                cf = forward_by_model(models, sm, zo)
                a1, g1 = masked_pair(cf, mk)
                for i in range(len(names)):
                    if ob[i, ds + 4 * k] <= 0:
                        continue
                    sp = speaker.get((i, k))
                    skey = (sm[sp] if sp is not None else "?", sm[i],
                            KIND_NAMES[k])
                    agg["flip"][skey + ("rows",)] += 1
                    if a0[i] != a1[i]:
                        agg["flip"][skey + ("act",)] += 1
                        agg["flip_pairs"][
                            (KIND_NAMES[k], ACTION_NAMES[a0[i]],
                             ACTION_NAMES[a1[i]])] += 1
                    if g0[i] != g1[i]:
                        agg["flip"][skey + ("msg",)] += 1
                    if a0[i] < 4 and a1[i] < 4:
                        dx = float(ob[i, ds + 4 * k + 1])
                        dy = float(ob[i, ds + 4 * k + 2])

                        def toward(a):
                            mx, my = MOVE_D[a]
                            return ((mx != 0 and mx * dx > 0)
                                    or (my != 0 and my * dy > 0))

                        agg["steer"][skey + ("bm",)] += 1
                        agg["steer"][skey + ("base_t",)] += toward(int(a0[i]))
                        agg["steer"][skey + ("cf_t",)] += toward(int(a1[i]))

            for i in range(len(names)):
                model = sm[i]
                hap = float(ob[i, 6]) * 100
                agg["hap"][model] += hap
                agg["hap_n"][model] += 1
                agg["distress"][model] += int((ob[i, 20:26] > 0).any())
                agg["acts"][(model, ACTION_NAMES[a0[i]])] += 1
                dn = dist_nearest(ob[i], max_dist)
                moving = int(a0[i] < 4 or a0[i] in CHASE_IDX)
                for g in range(1, 9):
                    if not mk[i, N_ACT + g]:
                        continue
                    kind = MSG_NAMES[g]
                    ni = NEED_IDX.get(kind)
                    need = float(ob[i, ni]) * 100 if ni is not None else 0.0
                    if g0[i] == g:
                        agg["emit"][(model, kind)] += 1
                        ctx_add(model, kind, "emit", need, hap, dn, moving)
                        for (rt, rj, rk) in recent:
                            if rj != i:
                                agg["reply"][
                                    (sm[rj], KIND_NAMES[rk], model, kind)
                                ] += 1
                    else:
                        agg["declined"][(model, kind)] += 1
                        ctx_add(model, kind, "declined", need, hap, dn,
                                moving)
                if g0[i] > 0:
                    recent.append((t, i, int(g0[i]) - 1))

            acts = {a: (int(a0[i]), int(g0[i]))
                    for i, a in enumerate(names)}
            obs, rew, term, trunc, infos = env.step(acts)
            agg["kitty_ticks"] += len(names)
        print(f"{comp} seed {seed} done", flush=True)

    out = {k: (v if not isinstance(v, Counter) else
               {"|".join(map(str, key)) if isinstance(key, tuple) else key: n
                for key, n in v.items()})
           for k, v in agg.items() if k != "ctx"}
    out["ctx"] = {"|".join(k): v for k, v in agg["ctx"].items()}
    path = out_dir / f"{comp}.json"
    path.write_text(json.dumps(out) + "\n")
    print(f"{comp}: wrote {path}", flush=True)


def main():
    comps = os.environ.get("MEOW_COMPS")
    comps = comps.split(",") if comps else list(COMPOSITIONS)
    names = sorted({s for c in comps for s in COMPOSITIONS[c]})
    models = {n: load_model(n) for n in names}
    out_dir = HERE / ("results-raw-smoke" if SMOKE else "results-raw")
    out_dir.mkdir(exist_ok=True)
    for comp in comps:
        run_composition(comp, COMPOSITIONS[comp], models, out_dir)


if __name__ == "__main__":
    main()
