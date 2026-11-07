#!/usr/bin/env python3
"""Phase 2 (DECLARATION.md): the shared constants, paths and record
loaders every Phase 2 instrument imports. Nothing here decides; it names
the frozen inputs (the trunk seeds and their finals, the probe dumps,
the battery rows, the head stores) and replays a recorded world.

Run everything on the arc venv (BINDING.md):
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B ...
"""
import hashlib
import json
import sys
import tomllib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
TRUNK_ARC = EXPTS / "gen2-trunk-training-2026-10-18"
TRUNK_ARTS = TRUNK_ARC / "artifacts"
TRUNK_TOML = EXPTS / "gen2-comparator-legs-2026-10-14" / "g2leg-20.toml"
LEG_TOML = {20: TRUNK_TOML,
            40: EXPTS / "gen2-comparator-legs-2026-10-14" / "g2leg-40.toml",
            100: EXPTS / "gen2-comparator-legs-2026-10-14" / "g2leg-100.toml"}
BATTERY = EXPTS / "gen2-cert-battery-2026-10-20"
ACT_ARC = EXPTS / "minifriend-act-2026-11-03"
LADDER_ARC = EXPTS / "minifriend-act-ladder-2026-11-04"
HARNESS = EXPTS / "fog-gen1-cert"
ARTS = HERE / "artifacts"                      # this arc's trained arms (gitignored, never deleted)
RAW = HERE / "results-raw"                     # this arc's legs and reads (gitignored, never deleted)
for p in (EXPTS / "attn-oracle-2026-08-15", TRUNK_ARC / "trainer", ACT_ARC, LADDER_ARC, HARNESS, EXPTS):
    sys.path.insert(0, str(p))

# The three frozen trunk seeds the arms graft from (DECLARATION §2, §3;
# finals' sha256 as recorded there).
TRUNK_SEEDS = (1, 2, 4)
TRUNK_FINAL_SHA = {1: "a22b8713f517f794dd441ffe59a07004953c3e7637166093dbf78dee1f458364",
                   2: "4040554abaaa1b4255fce455bbccfcadea65d0d61f3aa0396269c0fc7acba086",
                   4: "69d7248c7c33395173889ee068dcf86f7a7e9e18ed4dab59dd316f03ed94b690"}
TRUNK_PARAMS = 84_450
PROBE_SEEDS = [40_001, 40_002, 40_003]
ROSTER = 5
OBS_DIM, SELF_BLOCK, KITTY_W, N_ROWS = 399, 109, 58, 4
STALENESS_NORMALISER = 40.0                    # docs/encodings.md element memory: (tick - last)/40 clamped 1


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def trunk_final(k):
    p = TRUNK_ARTS / f"ppo-g2-trunk-s{k}" / "policy-final.pt"
    assert p.exists(), p
    return p


def check_trunk_final(k):
    """The final named in the declaration, by sha256 (never by path alone)."""
    p = trunk_final(k)
    s = sha256(p)
    assert s == TRUNK_FINAL_SHA[k], f"trunk-s{k} final sha {s} is not the declared {TRUNK_FINAL_SHA[k]}"
    return p


def last_probe_dump(slot="trunk-s1"):
    """The highest-update probe-u<N>.npz of a trunk run (the last probe before its plateau)."""
    d = TRUNK_ARTS / f"ppo-g2-{slot}"
    dumps = sorted(d.glob("probe-u*.npz"), key=lambda p: int(p.stem.split("u")[1]))
    assert dumps, d
    return dumps[-1]


def dump_rows(z, seed):
    """The dumped decision rows of one probe seed, ordered (tick, kitty id): obs (T, 5, 399), mask (T, 5, 51),
    act / msg (T, 5) in kitty-id order 1..5."""
    sel = z["seed"] == seed
    tick, kitty = z["tick"][sel], z["kitty"][sel]
    order = np.lexsort((kitty, tick))
    T = int(tick.max()) + 1
    assert sel.sum() == T * ROSTER, (sel.sum(), T)
    out = {k: z[k][sel][order].reshape((T, ROSTER) + z[k].shape[1:]) for k in ("obs", "mask", "act", "msg")}
    assert (out["act"].shape == (T, ROSTER)) and np.array_equal(kitty[order].reshape(T, ROSTER)[0], np.arange(1, ROSTER + 1))
    return out


def replay_dump(rows, seed, config=TRUNK_TOML, snapshot_at=None, mode="restore", horizon=None):
    """Replay a probe dump's recorded actions from reset(seed) on the binding in use and return the observation and mask
    streams the binding produced, (T, 5, 399) / (T, 5, 51). With snapshot_at = t: snapshot() after tick t's step, finish
    the replay, then (mode 'restore') restore() and replay the tail again, or (mode 'fork') fork() and replay the tail on the
    fork; returns (obs, mask, obs_tail_branch) so the caller compares the two tails. The probe loop's own calls
    (train_ppo_g2.run_probe): ParallelEnv(config) with no horizon, reset(seed), step with the recorded (act, msg)."""
    import cloudkitty
    env = cloudkitty.ParallelEnv(str(config), horizon=horizon)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    assert names == [f"kitty_{i}" for i in range(1, ROSTER + 1)], names
    T = rows["act"].shape[0]
    O = np.zeros((T, ROSTER, OBS_DIM), np.float32)
    M = np.zeros((T, ROSTER, rows["mask"].shape[-1]), bool)
    snap, branch_from = None, None

    def collect(t, obs, infos):
        O[t] = np.stack([np.asarray(obs[a], np.float32) for a in names])
        M[t] = np.stack([np.asarray(infos[a]["mask"], np.uint8) for a in names]).astype(bool)

    def act(t):
        return {a: (int(rows["act"][t, j]), int(rows["msg"][t, j])) for j, a in enumerate(names)}

    for t in range(T):
        collect(t, obs, infos)
        obs, _r, _te, _tr, infos = env.step(act(t))
        if snapshot_at is not None and t == snapshot_at:
            snap = env.snapshot()
            branch_from = t + 1
    if snapshot_at is None:
        return O, M
    if mode == "restore":
        obs, infos = env.restore(snap)
        branch = env
    else:
        # fork() = a new env of the same config restored from the live env's state (here the END of the replay);
        # restoring the mid-way snapshot into it then gives the branch's first observations (restore returns what
        # reset returns).
        branch = env.fork()
        obs, infos = branch.restore(snap)
    OB = np.zeros((T - branch_from, ROSTER, OBS_DIM), np.float32)
    for i, t in enumerate(range(branch_from, T)):
        OB[i] = np.stack([np.asarray(obs[a], np.float32) for a in names])
        obs, _r, _te, _tr, infos = branch.step(act(t))
    return O, M, OB


def battery_rows(seating, size, band="g2cmp", n=30, ticks=20_000):
    """{seed: row} of a recorded cert-battery leg (header line dropped)."""
    p = BATTERY / "results-raw" / seating / "legs" / f"size{size}" / f"{seating}-{band}-{n}x{ticks}.jsonl"
    lines = p.read_text().splitlines()
    return {r["seed"]: r for r in (json.loads(l) for l in lines[1:])}


def team(row):
    return float(np.mean(row["mean_happiness"]))


def config_world(config=TRUNK_TOML):
    with open(config, "rb") as f:
        return tomllib.load(f)


if __name__ == "__main__":
    print(json.dumps({"trunk_finals": {k: sha256(trunk_final(k)) for k in TRUNK_SEEDS},
                      "last_probe_dump": str(last_probe_dump()), "arts": str(ARTS)}, indent=1))
