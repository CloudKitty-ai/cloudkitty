"""Phase-1 certification harness: the exp-006 battery's welfare and
stress instrument (the prereg §8 "cert harness (post-wall port)").

Port of attn-cert-2026-08-14/cert_harness.py to the post-wall surface
(obs 225, heads 34+16, 5-seat cutover config) with mixed seat types:

  v4:<name>    expanded attention artifact (<name>-o4.ckpolicy),
               forwarded by the acceptance-blessed numpy_forward_v4 —
               the same independent reimplementation that licensed the
               expansion (prereg §5), so the instrument inherits its
               validation.
  mlp:<name>   expanded MLP artifact, acceptance float64 forward.
  ppo:<dir>    torch EntityPolicyV4 policy-final.pt (lineage
               candidates).
  scripted     engine needs_driven via ParallelEnv control= (the
               harness never drives these seats).

Metrics transcribed verbatim from the attn harness (welfare.rs
definitions; the state layout survived the wall):
  floor_touches, low_share (< 45.0), max_distress_age (per-(kitty,
  need) flag streak), team nash = engine per-tick team reward.

Validation protocol (D-001 precedent, run before any battery leg):
  (a) val-scripted: all seats controlled; state-derived metrics must
      EXACT-MATCH kitty-eval --brain needs_driven on the same
      seed/config (identical trajectories by determinism). Team nash
      is not read on this leg (no policy agents); the scripted anchor
      comes from kitty-eval natively, as in the 08-14 battery.
  (b) val-homog: one expanded artifact on every seat vs kitty-eval
      --artifact; only permitted divergence is the numpy-vs-Rust
      forward gap (~1e-5 logits -> greedy near-tie flips).

One continuous world per run (horizon = ticks), greedy, post-tick
metric reads — kitty-eval's convention. Prints engine/binding
provenance into every row.
"""
import argparse
import json
import subprocess
import sys
import tomllib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
REPO = EXPTS.parent
sys.path.insert(0, str(EXPTS / "attn-oracle-2026-08-15"))
sys.path.insert(0, str(HERE))

LOW_HAPPINESS = 45.0
PER_KITTY, HAP, DIST0 = 32, 6, 20
N_ACT, N_MSG = 34, 16
N_HEADS = N_ACT + N_MSG  # 50
NEG_INF = float("-inf")

O4 = HERE / "expanded-candidates"

SEATINGS = {
    # roster/config order: Miso, Biscuit, Pumpkin, Kittybear, Clementine
    "candidate": ["v4:attn-a1-s1", "ppo:ppo-L-04-s1", "v4:attn-a1-s3",
                  "v4:attn-a1-s3", "mlp:e004-a1-s2"],
    "reference": ["v4:attn-a1-s1", "mlp:e004-a1-s2", "v4:attn-a1-s3",
                  "v4:attn-a1-s3", "scripted"],
    "val-scripted": ["scripted"] * 5,
    "val-homog": ["v4:attn-a1-s1"] * 5,
    # validation-only cell for the D-001 nonzero-streak cross-check;
    # never a gate leg
    "val-homog-mlp": ["mlp:e004-a1-s2"] * 5,
    # r3/r5 stress shapes — owner's seat rule: candidate minds by
    # kitty ID order (run with --config pointing at the family world)
    "candidate-r3": ["v4:attn-a1-s1", "ppo:ppo-L-04-s1",
                     "v4:attn-a1-s3"],
    "candidate-r5": ["v4:attn-a1-s1", "ppo:ppo-L-04-s1",
                     "v4:attn-a1-s3", "v4:attn-a1-s3",
                     "mlp:e004-a1-s2"],
    # localization cell for the r5 failure write-up (owner's ID rule
    # applied to the reference composition); never a gate leg
    "reference-r5": ["v4:attn-a1-s1", "mlp:e004-a1-s2",
                     "v4:attn-a1-s3", "v4:attn-a1-s3", "scripted"],
    # report-only forensics follow-up (r5-forensics-2026-08-20.md):
    # s3 seated solo (scripted fill at Kittybear) — measures the twin
    # deadlock's removal and whether Clementine's company covers the
    # kin dose-response solo cost; never a gate leg
    "solo-s3": ["v4:attn-a1-s1", "ppo:ppo-L-04-s1", "v4:attn-a1-s3",
                "scripted", "mlp:e004-a1-s2"],
}
BANDS = {"eval": 870_001, "stress": 880_001}


def load_model(spec):
    if spec == "scripted":
        return None
    kind, name = spec.split(":", 1)
    if kind == "v4":
        from numpy_forward_v4 import load_artifact, numpy_forward
        p = load_artifact((O4 / f"{name}-o4.ckpolicy").read_bytes())
        return lambda rows: numpy_forward(p, rows)
    if kind == "mlp":
        from expansion_acceptance import fwd_mlp, read_mlp
        _header, layers = read_mlp(O4 / f"{name}-o4.ckpolicy")
        return lambda rows: fwd_mlp(layers, rows)
    if kind == "ppo":
        import torch
        from model_v4 import EntityPolicyV4
        ck = torch.load(HERE / "artifacts" / name / "policy-final.pt",
                        map_location="cpu", weights_only=True)
        m = EntityPolicyV4(**ck["hyper"])
        m.load_state_dict(ck["state_dict"])
        m.eval()

        def fwd(rows):
            with torch.no_grad():
                return m(torch.from_numpy(rows)).numpy()
        return fwd
    raise ValueError(spec)


def run_one(args):
    seating_name, seed, ticks, config_path = args
    import cloudkitty
    import numpy as np

    with open(config_path, "rb") as f:
        cfg = tomllib.load(f)
    floor = cfg["happiness"]["floor"]
    kitties = cfg["kitty"]
    roster = len(kitties)
    seats = SEATINGS[seating_name]
    assert len(seats) == roster, (seating_name, roster)

    control = {f"kitty_{k['id']}": "needs_driven"
               for k, s in zip(kitties, seats) if s == "scripted"}
    models = {s: load_model(s) for s in set(seats) if s != "scripted"}

    env = cloudkitty.ParallelEnv(str(config_path),
                                 control=control or None, horizon=ticks)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    expect = [f"kitty_{k['id']}" for k, s in zip(kitties, seats)
              if s != "scripted"]
    assert names == expect, (names, expect)
    seat_of = {f"kitty_{k['id']}": s for k, s in zip(kitties, seats)}

    if names:
        w = np.asarray(obs[names[0]], np.float32).shape[0]
        mw = len(infos[names[0]]["mask"])
        assert (w, mw) == (225, N_HEADS), (w, mw)

    hap_sum = np.zeros(roster)
    low_ticks = np.zeros(roster, np.int64)
    floor_touches = np.zeros(roster, np.int64)
    dist_streak = np.zeros((roster, 6), np.int64)
    max_dist_age = 0
    reward_sum, n_ticks = 0.0, 0

    for _t in range(ticks):
        acts = {}
        if names:
            ob = np.stack([np.asarray(obs[a], np.float32) for a in names])
            mk = np.stack([np.asarray(infos[a]["mask"], np.uint8)
                           for a in names]).astype(bool)
            lg = np.zeros((len(names), N_HEADS), np.float32)
            for s, fwd in models.items():
                rows = [i for i, a in enumerate(names) if seat_of[a] == s]
                if rows:
                    lg[rows] = np.asarray(fwd(ob[rows]), np.float32)
            a0 = np.where(mk[:, :N_ACT], lg[:, :N_ACT], NEG_INF).argmax(1)
            g0 = np.where(mk[:, N_ACT:], lg[:, N_ACT:], NEG_INF).argmax(1)
            acts = {a: (int(a0[i]), int(g0[i]))
                    for i, a in enumerate(names)}
        obs, rew, _term, _trunc, infos = env.step(acts)
        st = np.asarray(env.state(), np.float32)
        if names:
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
        "nash": (reward_sum / max(1, n_ticks)) if names else None,
        "mean_happiness": (hap_sum / max(1, n_ticks)).round(4).tolist(),
        "low_share": (low_ticks / max(1, n_ticks)).round(6).tolist(),
        "floor_touches": floor_touches.tolist(),
        "max_distress_age": max_dist_age,
    }


def provenance(config_path):
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    import hashlib
    cfg_sha = hashlib.sha256(Path(config_path).read_bytes()).hexdigest()
    import cloudkitty
    return {"git_head": head, "config_sha256": cfg_sha,
            "binding": getattr(cloudkitty, "__version__", "unknown"),
            "binding_engine": getattr(cloudkitty, "ENGINE_COMMIT", None)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seating", choices=list(SEATINGS))
    ap.add_argument("band", choices=list(BANDS))
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--seed0", type=int, default=None,
                    help="override the band's first seed (validation "
                         "cells targeting a specific seed)")
    ap.add_argument("--ticks", type=int, default=20_000)
    ap.add_argument("--config", type=Path, default=REPO / "cloudkitty.toml")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out-dir", type=Path, default=HERE / "results-raw")
    args = ap.parse_args()

    prov = provenance(args.config)
    print("provenance:", json.dumps(prov))
    seed0 = args.seed0 if args.seed0 is not None else BANDS[args.band]
    jobs = [(args.seating, seed0 + i, args.ticks, args.config)
            for i in range(args.seeds)]
    args.out_dir.mkdir(exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers) as px:
        for r in px.map(run_one, jobs):
            rows.append(r)
            nash = "None" if r["nash"] is None else f"{r['nash']:.4f}"
            print(f"{r['seating']} {args.band} seed {r['seed']}: "
                  f"nash {nash} mda {r['max_distress_age']} "
                  f"ft {sum(r['floor_touches'])}", flush=True)
    out = args.out_dir / f"battery-{args.seating}--{args.band}.json"
    out.write_text(json.dumps({"provenance": prov, "rows": rows},
                              indent=1) + "\n")
    import numpy as np
    nashes = [r["nash"] for r in rows if r["nash"] is not None]
    print(f"\n{args.seating} {args.band}: "
          f"nash {np.mean(nashes):.4f} | " if nashes else "", end="")
    print(f"worst mda {max(r['max_distress_age'] for r in rows)} | "
          f"floor {sum(sum(r['floor_touches']) for r in rows)} | "
          f"max low_share {max(max(r['low_share']) for r in rows):.4f}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
