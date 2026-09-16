#!/usr/bin/env python3
"""Step-7 certification battery harness: the exp-006 `cert_harness6.py`
ported to the fog surface (schema 5: obs 408, heads 39 + 16 = 55) with
one torch policy PER SEAT, so a five-network roster can be read.

Seat specs (one per roster seat, in kitty id order):
  ppo:<slot>   `artifacts/ppo-fog-<slot>/policy-final.pt` (EntityPolicyV5,
               loaded by the shakeout trainer's own loader), greedy on
               both heads under the engine mask
  scripted     the engine's own behavior for that seat (needs_driven at
               four seats, playful at Biscuit's, as the config seats
               them) via ParallelEnv control=; the harness never
               drives these seats

Metrics verbatim from cert_harness6 (global_state.rs layout: PER_KITTY
32, happiness at 6, distress flags at 20..26): mean happiness, low_share
(< 45), floor_touches, max_distress_age (per-(kitty, need) flag streak),
team nash = the engine's per-tick team reward. One continuous world per
run (horizon = ticks), greedy, post-tick metric reads: kitty-eval's
convention, so the all-scripted leg must EXACT-MATCH kitty-eval
--brain needs_driven on the same seed and config (validation (a) of the
006 protocol, run before any battery leg).

    cert_harness_fog.py SEATING BAND [--seeds 30] [--ticks 20000]
                        [--config anchor-b3.toml] [--workers 6]
"""
import argparse
import hashlib
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
sys.path.insert(0, str(EXPTS / "fog-gen1-shakeout" / "trainer"))
sys.path.insert(0, str(EXPTS / "exp-006-character-gen"))
sys.path.insert(0, str(EXPTS))

LOW_HAPPINESS = 45.0
# reward.rs: Nash welfare = exp(mean ln(h/100 + eps)) - eps at p = 0, eps 0.01 (the
# [rl.reward] default; anchor-b3.toml sets none). The engine's reward uses UNCLAMPED
# happiness; the state carries the engine's clamped value, so `nash_state` equals the
# reward wherever no seat sits at the floor (floor_touches 0), which is every leg read
# so far. It exists so the all-scripted roster, which has no policy agent and therefore
# no reward stream, gets a paired team number.
REWARD_EPS, TERM_FLOOR = 0.01, 1e-4
PER_KITTY, HAP, DIST0 = 32, 6, 20
N_ACT, N_MSG = 39, 16
N_HEADS = N_ACT + N_MSG
OBS_DIM = 408
NEG_INF = float("-inf")
ARTS = HERE / "artifacts"
DEFAULT_CONFIG = HERE / "anchor-b3.toml"

# Seat order = kitty id order in the config: Miso, Biscuit, Pumpkin, Kittybear, Clementine.
SEATINGS = {
    "scripted": ["scripted"] * 5,
    # Gen 1 candidate roster A (Experiments' proposal 2026-09-15 from RESULTS.md;
    # five distinct networks; the seats are the owner's after the battery):
    #   Miso cand-s2 · Biscuit cand-s1 (giver row 0, duets 62/1k, breach .018)
    #   Pumpkin dose-lo-s1 (clean on every seat over 108k ticks, nash .929)
    #   Kittybear cand-s4 · Clementine cand-s7
    "gen1-A": ["ppo:cand-s2", "ppo:cand-s1", "ppo:dose-lo-s1", "ppo:cand-s4", "ppo:cand-s7"],
}
# rep1/rep2: the owner's tail replication of the seated roster (2026-09-15), two more
# disjoint 30-seed bands beyond the declared eval/stress pair
BANDS = {"eval": 870_001, "stress": 880_001, "probe": 40_001, "rep1": 890_001, "rep2": 895_001}


def load_model(spec):
    if spec == "scripted":
        return None
    kind, name = spec.split(":", 1)
    if kind != "ppo":
        raise ValueError(spec)
    import torch
    from train_ppo_fog import load_policy_ckpt
    torch.set_num_threads(1)
    policy, _ck = load_policy_ckpt(ARTS / f"ppo-fog-{name}" / "policy-final.pt")
    policy.eval()

    def fwd(rows):
        with torch.no_grad():
            return policy(torch.from_numpy(rows)).numpy()
    return fwd


def run_one(args):
    seating_name, seed, ticks, config_path, seats_override, *rest = args
    control_brain = rest[0] if rest else None  # validation only: force one brain on every scripted seat
    import cloudkitty
    import numpy as np

    with open(config_path, "rb") as f:
        cfg = tomllib.load(f)
    floor = cfg["happiness"]["floor"]
    kitties = cfg["kitty"]
    roster = len(kitties)
    seats = list(seats_override or SEATINGS[seating_name])
    assert len(seats) == roster, (seating_name, roster)

    # control= names the seats the ENGINE drives; each keeps its configured behavior
    control = {f"kitty_{k['id']}": control_brain or k["behavior"]
               for k, s in zip(kitties, seats) if s == "scripted"}
    models = {s: load_model(s) for s in set(seats) if s != "scripted"}

    env = cloudkitty.ParallelEnv(str(config_path), control=control or None, horizon=ticks)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    expect = [f"kitty_{k['id']}" for k, s in zip(kitties, seats) if s != "scripted"]
    assert names == expect, (names, expect)
    seat_of = {f"kitty_{k['id']}": s for k, s in zip(kitties, seats)}
    if names:
        w = np.asarray(obs[names[0]], np.float32).shape[0]
        mw = len(infos[names[0]]["mask"])
        assert (w, mw) == (OBS_DIM, N_HEADS), (w, mw)

    hap_sum = np.zeros(roster)
    low_ticks = np.zeros(roster, np.int64)
    floor_touches = np.zeros(roster, np.int64)
    dist_streak = np.zeros((roster, 6), np.int64)
    max_dist_age = 0
    max_dist_age_seat = np.zeros(roster, np.int64)
    reward_sum, n_ticks = 0.0, 0
    nash_state_sum = 0.0

    for _t in range(ticks):
        acts = {}
        if names:
            ob = np.stack([np.asarray(obs[a], np.float32) for a in names])
            mk = np.stack([np.asarray(infos[a]["mask"], np.uint8) for a in names]).astype(bool)
            lg = np.zeros((len(names), N_HEADS), np.float32)
            for s, fwd in models.items():
                rows = [i for i, a in enumerate(names) if seat_of[a] == s]
                if rows:
                    lg[rows] = np.asarray(fwd(ob[rows]), np.float32)
            a0 = np.where(mk[:, :N_ACT], lg[:, :N_ACT], NEG_INF).argmax(1)
            g0 = np.where(mk[:, N_ACT:], lg[:, N_ACT:], NEG_INF).argmax(1)
            acts = {a: (int(a0[i]), int(g0[i])) for i, a in enumerate(names)}
        obs, rew, _term, _trunc, infos = env.step(acts)
        st = np.asarray(env.state(), np.float32)
        if names:
            reward_sum += float(rew[names[0]])
        n_ticks += 1
        h_norm = st[HAP:roster * PER_KITTY:PER_KITTY].astype(np.float64)
        nash_state_sum += float(np.exp(np.log(np.maximum(h_norm + REWARD_EPS, TERM_FLOOR)).mean()) - REWARD_EPS)
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
            age = int(dist_streak[k].max())
            max_dist_age_seat[k] = max(max_dist_age_seat[k], age)
            max_dist_age = max(max_dist_age, age)

    return {
        "seating": seating_name, "seats": seats, "seed": seed, "ticks": n_ticks,
        "nash": (reward_sum / max(1, n_ticks)) if names else None,
        "nash_state": nash_state_sum / max(1, n_ticks),
        "mean_happiness": (hap_sum / max(1, n_ticks)).round(4).tolist(),
        "low_share": (low_ticks / max(1, n_ticks)).round(6).tolist(),
        "floor_touches": floor_touches.tolist(),
        "max_distress_age": max_dist_age,
        "max_distress_age_seat": max_dist_age_seat.tolist(),
    }


def provenance(config_path):
    from census_provenance import binding_identity, stamp
    import cloudkitty
    rustc = subprocess.run(["rustc", "-V"], capture_output=True, text=True)
    return stamp(__file__, repo=REPO, extra={
        "config_sha256": hashlib.sha256(Path(config_path).read_bytes()).hexdigest(),
        "binding": getattr(cloudkitty, "__version__", "unknown"),
        "binding_engine": getattr(cloudkitty, "ENGINE_COMMIT", None),
        "rustc": rustc.stdout.strip() or None,
        "binding_artifacts": binding_identity(cloudkitty),
        "artifacts": {s: hashlib.sha256((ARTS / f"ppo-fog-{s.split(':', 1)[1]}" / "policy-final.pt").read_bytes()).hexdigest()
                      for seats in SEATINGS.values() for s in seats if s != "scripted"},
    })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seating", choices=list(SEATINGS))
    ap.add_argument("band", choices=list(BANDS))
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--seed0", type=int, default=None)
    ap.add_argument("--ticks", type=int, default=20_000)
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out-dir", type=Path, default=HERE / "results-raw" / "battery")
    ap.add_argument("--seat", action="append", default=[],
                    help="override one seat: INDEX=SPEC (report-only swaps)")
    ap.add_argument("--control-brain", default=None,
                    help="validation only: force this engine brain on every scripted seat "
                         "(kitty-eval --brain NAME seats one brain everywhere)")
    a = ap.parse_args()
    seats = list(SEATINGS[a.seating])
    tag = a.seating
    for ov in a.seat:
        i, spec = ov.split("=", 1)
        seats[int(i)] = spec
        tag += f"_s{i}-{spec.split(':', 1)[-1]}"
    seed0 = a.seed0 if a.seed0 is not None else BANDS[a.band]
    jobs = [(a.seating, seed0 + i, a.ticks, str(a.config), seats, a.control_brain) for i in range(a.seeds)]
    if a.control_brain:
        tag += f"_val-{a.control_brain}"
    a.out_dir.mkdir(parents=True, exist_ok=True)
    out = a.out_dir / f"{tag}-{a.band}-{a.seeds}x{a.ticks}.jsonl"
    with out.open("w") as f:
        f.write(json.dumps({"provenance": provenance(a.config), "seats": seats,
                            "band": a.band, "seed0": seed0}) + "\n")
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            for r in ex.map(run_one, jobs):
                f.write(json.dumps(r) + "\n")
                f.flush()
                print(f"seed {r['seed']} nash {r['nash']} hap {r['mean_happiness']} "
                      f"mda {r['max_distress_age']} floor {r['floor_touches']}", flush=True)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
