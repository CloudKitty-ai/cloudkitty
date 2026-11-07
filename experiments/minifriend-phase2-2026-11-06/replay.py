#!/usr/bin/env python3
"""Replay a recorded Phase 2 leg (cert_harness_fog --record-dir: `acts-<seed>.npz`, every policy seat's chosen
(act, msg) per tick) on the arc binding and yield what the after-the-fact reads need per tick — the engine's ground
truth (needs, happiness, position, activity, partner), 068's tick_records (proposed / validated / applied names and
provenance) and, when asked, the observation rows and masks the seats saw (for the heads, R-4 / R-5). A replay is
the leg again without the policies: ~2 s per 20k-tick world; nothing covered decides (the actions are the record's).
The replay asserts it reproduces the recorded row's mean happiness per seat (the leg's own summary) at the end.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p2_common as C  # noqa: E402

# global_state.rs v2 per-kitty block (40): needs 0-5, happiness 6, pos 7-8, activity one-hot 9-15, social flag 16,
# partner present 17, partner index / (n-1) 18, progress 19, distress flags 20-25, identity 26-39.
PK, HAP, POS0, ACT0, SOCIAL, PARTNER_PRESENT, PARTNER_IDX, DIST0 = 40, 6, 7, 9, 16, 17, 18, 20
ACTIVITY_KINDS = ["idle", "resting", "sleeping", "eating", "drinking", "playing", "grooming"]


def legs_dir(seating, size, root=None):
    return (root or C.RAW) / "legs" / seating / "legs" / f"size{size}"


def leg_rows(seating, size, root=None, n=30, ticks=20_000, band="g2cmp"):
    """{seed: row} of one of this arc's legs (header dropped) and the header."""
    p = legs_dir(seating, size, root) / f"{seating}-{band}-{n}x{ticks}.jsonl"
    lines = p.read_text().splitlines()
    return {r["seed"]: r for r in (json.loads(l) for l in lines[1:])}, json.loads(lines[0])


def acts_path(seating, size, seed, root=None):
    return legs_dir(seating, size, root) / "acts" / f"acts-{seed}.npz"


def kitty_truth(st, roster=C.ROSTER):
    """(needs (R, 6) x100, hap (R,) x100, pos (R, 2) normalised, activity (R,) int, partnered (R,) bool, partner (R,)
    int or -1, distress (R, 6) bool) from a v2 global state vector."""
    k = np.asarray(st, np.float32)[:roster * PK].reshape(roster, PK)
    partnered = k[:, PARTNER_PRESENT] > 0.5
    partner = np.where(partnered, np.rint(k[:, PARTNER_IDX] * (roster - 1)).astype(int), -1)
    return (k[:, :6] * 100, k[:, HAP] * 100, k[:, POS0:POS0 + 2], k[:, ACT0:ACT0 + 7].argmax(1), partnered, partner,
            k[:, DIST0:DIST0 + 6] > 0.5)


def replay(acts_npz, config, want_obs=False, horizon=None, check_row=None, want_snapshot=False):
    """Yield per tick dicts: tick, pre (truth before the step), post (truth after), acts (R, 2), recs (tick_records
    per seat name), names, env (the live env, for forks), with want_obs the start-of-tick obs (R, 399) and masks
    (R, 51), with want_snapshot the pre-step snapshot bytes (restore into env.fork() for a one-tick branch). The actions are the record's; every seat is a policy seat (the Phase 2 legs seat no scripted cat).
    check_row: the leg's recorded row — its mean_happiness per seat is asserted against the replay's at the end."""
    import cloudkitty
    z = np.load(acts_npz)
    acts, names = z["acts"], [str(n) for n in z["names"]]
    seed, T = int(z["seed"]), int(z["ticks"])
    assert C.sha256(config) == str(z["config_sha256"]), "the replay's config is not the leg's"
    env = cloudkitty.ParallelEnv(str(config), horizon=horizon or T)
    obs, infos = env.reset(seed=seed)
    assert list(env.possible_agents) == names, (names, list(env.possible_agents))
    hap_sum = np.zeros(len(names))
    for t in range(T):
        pre = kitty_truth(env.state())
        rec = {"tick": t, "pre": pre, "acts": acts[t], "names": names, "env": env, "seed": seed}
        if want_obs:
            rec["obs"] = np.stack([np.asarray(obs[a], np.float32) for a in names])
            rec["mask"] = np.stack([np.asarray(infos[a]["mask"], np.uint8) for a in names]).astype(bool)
        if want_snapshot:
            rec["snapshot_pre"] = env.snapshot()          # the pre-step world, for one-tick branches (068 fork + restore)
        obs, _r, _te, _tr, infos = env.step({a: (int(acts[t, i, 0]), int(acts[t, i, 1])) for i, a in enumerate(names)})
        rec["recs"] = env.tick_records()
        rec["post"] = kitty_truth(env.state())
        hap_sum += rec["post"][1]
        yield rec
    if check_row is not None:
        got = (hap_sum / T).round(4).tolist()
        assert got == check_row["mean_happiness"], f"replay of {seed} does not reproduce the recorded row: {got} vs {check_row['mean_happiness']}"


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("acts")
    ap.add_argument("--config", default=str(C.TRUNK_TOML))
    a = ap.parse_args()
    n = sum(1 for _ in replay(a.acts, a.config))
    print(json.dumps({"ticks": n}))
