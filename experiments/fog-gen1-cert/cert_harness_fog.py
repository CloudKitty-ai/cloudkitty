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
import os
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
# global_state.rs per-kitty layout: needs 6 (sleep at 2), happiness, pos 2, activity one-hot 7
# (idle, rest, sleep, eat, drink, play, groom), social flag, partner present, partner index /
# (roster - 1), progress, distress 6, traits 6.
NEED_SLEEP, POS0, ACT0, SLEEP_ACT, PARTNER_PRESENT, PARTNER_IDX = 2, 7, 9, 2, 17, 18
NEED_BINS = (5.0, 10.0, 20.0, 40.0)  # beam-world screen: sleep need at a sleep start, bins <5, 5-10, 10-20, 20-40, >=40 (rule 4 read)
N_ACT, N_MSG = 39, 16
N_HEADS = N_ACT + N_MSG
OBS_DIM = 408
NEG_INF = float("-inf")
# CERT_ARTS: another pass's artifact root (beam-world screen tier 2, 2026-09-19); read at import so
# spawned workers see it too. Seat specs stay `ppo:<slot>` -> <root>/ppo-fog-<slot>/policy-final.pt.
ARTS = Path(os.environ["CERT_ARTS"]) if os.environ.get("CERT_ARTS") else HERE / "artifacts"
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
BANDS = {"eval": 870_001, "stress": 880_001, "probe": 40_001, "rep1": 890_001, "rep2": 895_001,
         # fog-deafening-2026-09-23: 4 arms x the SAME 30 seeds (paired by design)
         "deaf": 900_101}


def load_model(spec):
    """`scripted` -> None; `ppo:<slot>` -> a forward over observation rows; `plan:<slot>` -> the
    same forward under the beam planner (beam-world screen tier 3), which also reads the masks.
    Every callable takes (rows, masks); the plain forward ignores the masks."""
    if spec == "scripted":
        return None
    kind, name = spec.split(":", 1)
    if kind == "plan":
        sys.path.insert(0, str(EXPTS / "beam-world-screen-2026-09-19"))
        from beam_plan import BeamPlanner
        return BeamPlanner(load_model(f"ppo:{name}"))
    if kind != "ppo":
        raise ValueError(spec)
    import torch
    from train_ppo_fog import load_policy_ckpt
    torch.set_num_threads(1)
    policy, _ck = load_policy_ckpt(ARTS / f"ppo-fog-{name}" / "policy-final.pt")
    policy.eval()

    def fwd(rows, masks=None):
        with torch.no_grad():
            return policy(torch.from_numpy(rows)).numpy()
    return fwd


def beam_acc(roster):
    return {"sleep": [0] * roster, "on_beam": [0] * roster, "conducted": [0] * roster,
            "starts": [0] * roster, "start_dist": [[0, 0, 0, 0] for _ in range(roster)],
            "start_need_bins": [[0] * (len(NEED_BINS) + 1) for _ in range(roster)], "start_need_sum": [0.0] * roster}


def beam_account(st, beams, roster, width, height, prev_sleep, acc):
    """One tick of beam accounting on the global state (beam-world screen, 2026-09-19).

    Per seat: sleeping ticks; ticks asleep ON a beam tile; ticks asleep off-beam beside a
    direct partner who is on a beam (the spec-031 conduction case, read from the state's
    partner slot, without the engine's settled check); sleep starts (a tick asleep after a
    tick not asleep), the Chebyshev distance from the start tile to the nearest beam in the
    WORLD (0 / 1 / 2 / 3-or-more-or-none; Chebyshev by tier 1's declaration, a ring measure, NOT
    the engine's walk distance, which is `walk_distance`), and the sleep need at the start (binned by
    NEED_BINS; the low bins are the rule-4 farming read). Returns this tick's sleeping mask.
    """
    import numpy as np
    sleeping = np.zeros(roster, bool)
    pos = []
    for k in range(roster):
        b = k * PER_KITTY
        pos.append((int(round(float(st[b + POS0]) * width)), int(round(float(st[b + POS0 + 1]) * height))))
        sleeping[k] = int(st[b + ACT0:b + ACT0 + 7].argmax()) == SLEEP_ACT
    for k in range(roster):
        if not sleeping[k]:
            continue
        b = k * PER_KITTY
        acc["sleep"][k] += 1
        if pos[k] in beams:
            acc["on_beam"][k] += 1
        elif st[b + PARTNER_PRESENT] > 0.5:
            p = int(round(float(st[b + PARTNER_IDX]) * (roster - 1)))
            if pos[p] in beams:
                acc["conducted"][k] += 1
        if not prev_sleep[k]:
            acc["starts"][k] += 1
            d = min((max(abs(pos[k][0] - x), abs(pos[k][1] - y)) for x, y in beams), default=3)
            acc["start_dist"][k][min(d, 3)] += 1
            need = float(st[b + NEED_SLEEP]) * 100
            acc["start_need_bins"][k][sum(need >= edge for edge in NEED_BINS)] += 1
            acc["start_need_sum"][k] += need
    return sleeping


def walk_distance(a, b):
    """The engine's walking distance between two tiles: Manhattan. Direction is strictly N/E/S/W, so
    a walk costs |dx| + |dy| steps, adjacency is Manhattan 1, and priced travel is Manhattan plus terrain
    (`grid.rs`: Chebyshev "is *not* a walk cost", its one engine consumer is spawn spreading). Every
    lab instrument that asks "how far is X" or "is X within reach" uses this; the one Chebyshev measure
    in the lab is `beam_account`'s nearest-beam bin, kept as declared in tier 1 and labelled there."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


CLOCK_INDEX = OBS_DIM - 1  # the episode-clock input, the last float of the observation
TRAIN_HORIZON = 2000       # rl.episode.horizon default; the PPO episodes and the probes ran this clock

# --- Hearer-side deafening (fog-deafening-2026-09-23: F-026's fog-era re-run) ---
# Schema-5 layout (observe.rs block_widths; guarded by test_deafen_mask.py):
# SELF_BLOCK 85, KITTY_SLOT 63, four rows. Row-relative: message (recency,
# rate) pairs at 23 (HEAD_KINDS order, 15 kinds), want intensities at 53
# (WANT_KINDS order, 6), answers-me bits at 59 (HERE_KINDS order, 4).
KITTY0, KSLOT, N_KITTY_ROWS = 85, 63, 4
ROW_MSG, ROW_WANT, ROW_ANS, ROW_END = 23, 53, 59, 63
HEAD_WANT = [0, 1, 3, 4, 6, 7]   # HEAD_KINDS indices of the six want kinds
HEAD_HERE = [8, 9, 10, 11]       # HEAD_KINDS indices of the Here family
HEAD_FREE = [2, 5, 12, 13, 14]  # HEAD_KINDS indices of the free register: mew, purr, chirp (+ trill, ekekek reserves)
DEAF_ARMS = {
    "want": (HEAD_WANT, list(range(6)), []),
    "here": (HEAD_HERE, [], list(range(4))),
    "free": (HEAD_FREE, [], []),
    "all": (list(range(15)), list(range(6)), list(range(4))),
    # "rows" is not a kind mask: it erases every heard-only row (present 0,
    # live position) whole, leaving seen-row word content intact -- the
    # position-of-the-unseen channel alone (second collection, prereg-2.md).
    "rows": None,
    # "dir" keeps every heard row's true bearing and destroys its range:
    # the caller is projected to Manhattan distance --dir-r (tiles) along
    # the same bearing (third collection, prereg-3.md: a sweep of R values
    # anchored on dir_r_probe.py's measured heard-distance distribution).
    # Words and answers-me stay.
    "dir": None,
}


def deafen(ob, deaf, dims=None):
    """Zero what hearing put in these observations, in place. Per kitty row:
    the deafened kinds' (recency, rate) pairs, their want intensities, and
    (here-derived) answers-me bits; then any row that exists only by a
    deafened call -- present 0, a live position, and no surviving message
    float -- is zeroed whole, because a deaf hearer would have had a Silent
    row (heard rows carry the call's position). Self-speech (the own message
    block in SELF) and element memory (sight-only, world.rs) stay: neither
    is hearing. The served roster seats no scripted brain, so no WaitForMe
    row exists to survive a mask that only knows HEAD_KINDS."""
    import numpy as np
    if deaf == "rows":
        for r in range(N_KITTY_ROWS):
            row = KITTY0 + r * KSLOT
            heard = (ob[:, row] == 0.0) & (ob[:, row + 3] > 0.0)
            ob[heard, row:row + KSLOT] = 0.0
        return
    if deaf == "dir":
        width, height, dir_r = dims
        for r in range(N_KITTY_ROWS):
            row = KITTY0 + r * KSLOT
            heard = (ob[:, row] == 0.0) & (ob[:, row + 3] > 0.0)
            dx = ob[heard, row + 1] * width
            dy = ob[heard, row + 2] * height
            k = dir_r / (np.abs(dx) + np.abs(dy))
            ob[heard, row + 1] = dx * k / width
            ob[heard, row + 2] = dy * k / height
            ob[heard, row + 3] = dir_r / (width + height)
        return
    kinds, wants, heres = DEAF_ARMS[deaf]
    for r in range(N_KITTY_ROWS):
        row = KITTY0 + r * KSLOT
        for k in kinds:
            ob[:, row + ROW_MSG + 2 * k:row + ROW_MSG + 2 * k + 2] = 0.0
        for w in wants:
            ob[:, row + ROW_WANT + w] = 0.0
        for h in heres:
            ob[:, row + ROW_ANS + h] = 0.0
        heard_only = (
            (ob[:, row] == 0.0)
            & (ob[:, row + 3] > 0.0)
            & (np.abs(ob[:, row + ROW_MSG:row + ROW_END]).max(1) == 0.0)
        )
        ob[heard_only, row:row + KSLOT] = 0.0


def run_one(args):
    seating_name, seed, ticks, config_path, seats_override, control_brain, clock_mode, deaf, dir_r = args
    # clock_mode "served": the engine's policy seam pins the clock input to 0 at deploy
    # (behavior.rs decide_sync: "No episode runs at deploy"); the harness does the same so
    # the battery reads the served condition. Verified 2026-09-15: with the clock pinned the
    # harness loop matches the served engine action for action (cloudkitty-server, seed
    # 40001, 14 ticks, five seats). "episode": the binding's t/horizon clock, the training
    # schedule, kept for the record.
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
    dist_ticks = np.zeros(roster, np.int64)  # ticks with any distress flag up (F-026's whisper measure)
    floor_touches = np.zeros(roster, np.int64)
    dist_streak = np.zeros((roster, 6), np.int64)
    max_dist_age = 0
    max_dist_age_seat = np.zeros(roster, np.int64)
    reward_sum, n_ticks = 0.0, 0
    nash_state_sum = 0.0
    width, height = cfg["world"]["width"], cfg["world"]["height"]
    beams_acc = beam_acc(roster)
    prev_sleep = np.zeros(roster, bool)
    # message head per policy seat: counts of the chosen head index per tick (0 = Silent, then HEAD_KINDS
    # order); scripted seats decide inside the engine and are not counted (beam-world screen tier 5, P4)
    msg_counts = {a: [0] * N_MSG for a in names}

    for _t in range(ticks):
        acts = {}
        if names:
            ob = np.stack([np.asarray(obs[a], np.float32) for a in names])
            if clock_mode == "served":
                ob[:, CLOCK_INDEX] = 0.0
            elif clock_mode == "train":
                # the training schedule: t / rl.episode.horizon (default 2000), cycling, no world reset
                ob[:, CLOCK_INDEX] = (n_ticks % TRAIN_HORIZON) / TRAIN_HORIZON
            if deaf:
                deafen(ob, deaf, (width, height, dir_r))
            mk = np.stack([np.asarray(infos[a]["mask"], np.uint8) for a in names]).astype(bool)
            lg = np.zeros((len(names), N_HEADS), np.float32)
            for s, fwd in models.items():
                rows = [i for i, a in enumerate(names) if seat_of[a] == s]
                if rows:
                    lg[rows] = np.asarray(fwd(ob[rows], mk[rows]), np.float32)
            a0 = np.where(mk[:, :N_ACT], lg[:, :N_ACT], NEG_INF).argmax(1)
            g0 = np.where(mk[:, N_ACT:], lg[:, N_ACT:], NEG_INF).argmax(1)
            acts = {a: (int(a0[i]), int(g0[i])) for i, a in enumerate(names)}
            for i, a in enumerate(names):
                msg_counts[a][int(g0[i])] += 1
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
            if flags.any():
                dist_ticks[k] += 1
            dist_streak[k] = np.where(flags, dist_streak[k] + 1, 0)
            age = int(dist_streak[k].max())
            max_dist_age_seat[k] = max(max_dist_age_seat[k], age)
            max_dist_age = max(max_dist_age, age)
        beams = {(x, y) for (_id, ty, x, y) in env.elements() if ty == "Sunbeam"}
        prev_sleep = beam_account(st, beams, roster, width, height, prev_sleep, beams_acc)

    return {
        "beam": beams_acc,
        "plan": {s: dict(m.stats) for s, m in models.items() if hasattr(m, "stats")},
        "msg": msg_counts,
        "seating": seating_name, "seats": seats, "seed": seed, "ticks": n_ticks, "clock": clock_mode,
        "nash": (reward_sum / max(1, n_ticks)) if names else None,
        "nash_state": nash_state_sum / max(1, n_ticks),
        "mean_happiness": (hap_sum / max(1, n_ticks)).round(4).tolist(),
        "low_share": (low_ticks / max(1, n_ticks)).round(6).tolist(),
        "floor_touches": floor_touches.tolist(),
        "max_distress_age": max_dist_age,
        "max_distress_age_seat": max_dist_age_seat.tolist(),
        "dist_ticks": dist_ticks.tolist(),
    }


def provenance(config_path, seats):
    """Stamp the run: config sha, binding, toolchain, and the sha of every policy artifact the
    seating actually uses (was: every artifact in SEATINGS, which breaks under CERT_ARTS)."""
    from census_provenance import binding_identity, stamp
    import cloudkitty
    rustc = subprocess.run(["rustc", "-V"], capture_output=True, text=True)
    return stamp(__file__, repo=REPO, extra={
        "config_sha256": hashlib.sha256(Path(config_path).read_bytes()).hexdigest(),
        "binding": getattr(cloudkitty, "__version__", "unknown"),
        "binding_engine": getattr(cloudkitty, "ENGINE_COMMIT", None),
        "rustc": rustc.stdout.strip() or None,
        "binding_artifacts": binding_identity(cloudkitty),
        "artifacts_root": str(ARTS),
        "artifacts": {s: hashlib.sha256((ARTS / f"ppo-fog-{s.split(':', 1)[1]}" / "policy-final.pt").read_bytes()).hexdigest()
                      for s in sorted(set(seats)) if s != "scripted"},
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
    ap.add_argument("--clock", choices=("served", "train", "episode"), default="served",
                    help="served = clock input pinned to 0 as the engine seam does (default); "
                         "train = (t mod 2000)/2000, the PPO/probe schedule, without world resets; "
                         "episode = the binding's t/horizon clock over the whole run (the pre-22:00 legs)")
    ap.add_argument("--control-brain", default=None,
                    help="validation only: force this engine brain on every scripted seat "
                         "(kitty-eval --brain NAME seats one brain everywhere)")
    ap.add_argument("--deaf", choices=tuple(DEAF_ARMS), default=None,
                    help="hearer-side deafening arm (fog-deafening-2026-09-23): zero the named "
                         "kind family in every policy observation before the forward")
    ap.add_argument("--dir-r", type=float, default=None,
                    help="dir arm only: the fixed heard Manhattan distance in tiles")
    a = ap.parse_args()
    assert (a.deaf == "dir") == (a.dir_r is not None), "--dir-r goes with --deaf dir, both or neither"
    seats = list(SEATINGS[a.seating])
    tag = a.seating
    for ov in a.seat:
        i, spec = ov.split("=", 1)
        seats[int(i)] = spec
        tag += f"_s{i}-{spec.split(':', 1)[-1]}"
    seed0 = a.seed0 if a.seed0 is not None else BANDS[a.band]
    jobs = [(a.seating, seed0 + i, a.ticks, str(a.config), seats, a.control_brain, a.clock, a.deaf, a.dir_r) for i in range(a.seeds)]
    if a.control_brain:
        tag += f"_val-{a.control_brain}"
    if a.deaf == "dir":
        tag += f"-deaf-dir-r{int(a.dir_r)}"
    elif a.deaf:
        tag += f"-deaf-{a.deaf}"
    if a.clock == "served" and any(s != "scripted" for s in seats):
        tag += "-c0"  # legs before 2026-09-15 22:00 ran the episode clock and carry no suffix
    elif a.clock == "train" and any(s != "scripted" for s in seats):
        tag += "-ctrain"
    a.out_dir.mkdir(parents=True, exist_ok=True)
    out = a.out_dir / f"{tag}-{a.band}-{a.seeds}x{a.ticks}.jsonl"
    with out.open("w") as f:
        f.write(json.dumps({"provenance": provenance(a.config, seats), "seats": seats,
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
