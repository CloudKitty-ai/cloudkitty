"""j14 greedy battery legs (PREREG-D §Instrument, written before any
leg is read): the cert-harness leg loop with the obs clock pinned to 0
at col 407 (`-c0`, the recorded control's condition) and the online E
appended at col 408 via the guard-proven recurrence — the condition
j14 trained under. Accounting blocks are cert_harness_fog's own
functions (imported, never edited); rows carry the run_one schema so
enrich2d_read.py treats these legs like any battery jsonl. Per-tick
(seed, tick, seat) E and playing flags are recorded beside the rows
(the banded primary's live-arm side; the control side is
results-raw/e-edges/). Seeds/ticks/abort as stage B's legs.

    CERT_ARTS=artifacts probe_eval_j14.py --slot j14-s1 \\
        --out results-raw/battery/j14-s1/j14-legs.jsonl
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
sys.path.insert(0, str(HERE / "trainer"))
import cert_harness_fog as H  # noqa: E402
import train_ppo_enrich2c as tc  # noqa: E402
import train_ppo_enrich2d as td  # noqa: E402

CONFIG = HERE.parent / "beam-world-screen-2026-09-19" / "package.toml"
SEED0, N_SEEDS, TICKS, ABORT = 870_001, 30, 20_000, 1000


def load_j14(slot):
    import torch
    ck = torch.load(HERE / "artifacts" / f"ppo-fog-{slot}" / "policy-final.pt",
                    map_location="cpu", weights_only=False)
    policy = td.PolicyV5AddE(**ck["hyper"])
    policy.load_state_dict(ck["state_dict"])  # carries e_col
    assert float(policy.e_col.abs().max()) > 0.0, "e_col untrained? wrong artifact"
    policy.eval()

    def fwd(ob, mk):
        with torch.no_grad():
            return policy(torch.from_numpy(ob)).numpy()
    return fwd


def leg(slot, seed, fwd):
    import cloudkitty
    import tomllib
    with open(CONFIG, "rb") as f:
        cfg = tomllib.load(f)
    floor = cfg["happiness"]["floor"]
    roster = len(cfg["kitty"])
    width, height = cfg["world"]["width"], cfg["world"]["height"]
    env = cloudkitty.ParallelEnv(str(CONFIG), horizon=TICKS)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    assert len(names) == roster, names

    hap_sum = np.zeros(roster)
    low_ticks = np.zeros(roster, np.int64)
    dist_ticks = np.zeros(roster, np.int64)
    floor_touches = np.zeros(roster, np.int64)
    dist_streak = np.zeros((roster, 6), np.int64)
    max_dist_age = 0
    max_dist_age_seat = np.zeros(roster, np.int64)
    nash_state_sum, n_ticks = 0.0, 0
    beams_acc = H.beam_acc(roster)
    prev_sleep = np.zeros(roster, bool)
    plays_acc = H.play_acc(roster)
    prev_play = [False] * roster
    needs_hist = H.needs_acc(roster)
    msg_counts = {a: [0] * H.N_MSG for a in names}
    aborted_at = None
    Eo = np.zeros((1, roster))
    Ec = np.zeros((1, roster))
    E_track = np.zeros((TICKS, roster), np.float32)
    play_track = np.zeros((TICKS, roster), bool)

    for _t in range(TICKS):
        ob = np.stack([np.asarray(obs[a], np.float32) for a in names])
        valid = np.ones((1, roster), bool)
        Eo, Ec = tc.roll_E_step(ob[None, :, :], valid, Eo, Ec)
        E_now = (Eo + Ec)[0].astype(np.float32)
        E_track[n_ticks] = E_now
        play_track[n_ticks] = ob[:, 14] > 0.5
        ob[:, H.CLOCK_INDEX] = 0.0  # -c0: the control's clock condition
        ob9 = np.concatenate([ob, E_now[:, None]], 1)  # E appended, col 408
        mk = np.stack([np.asarray(infos[a]["mask"], np.uint8) for a in names]).astype(bool)
        lg = np.asarray(fwd(ob9, mk), np.float32)
        a0 = np.where(mk[:, :H.N_ACT], lg[:, :H.N_ACT], H.NEG_INF).argmax(1)
        g0 = np.where(mk[:, H.N_ACT:], lg[:, H.N_ACT:], H.NEG_INF).argmax(1)
        obs, _r, _te, _tr, infos = env.step({a: (int(a0[i]), int(g0[i])) for i, a in enumerate(names)})
        for i, a in enumerate(names):
            msg_counts[a][int(g0[i])] += 1
        st = np.asarray(env.state(), np.float32)
        n_ticks += 1
        h_norm = st[H.HAP:roster * H.PER_KITTY:H.PER_KITTY].astype(np.float64)
        nash_state_sum += float(np.exp(np.log(np.maximum(h_norm + H.REWARD_EPS, H.TERM_FLOOR)).mean()) - H.REWARD_EPS)
        for k in range(roster):
            b = k * H.PER_KITTY
            h = float(st[b + H.HAP]) * 100
            hap_sum[k] += h
            if h <= floor:
                floor_touches[k] += 1
            if h < H.LOW_HAPPINESS:
                low_ticks[k] += 1
            flags = st[b + H.DIST0:b + H.DIST0 + 6] > 0
            if flags.any():
                dist_ticks[k] += 1
            dist_streak[k] = np.where(flags, dist_streak[k] + 1, 0)
            age = int(dist_streak[k].max())
            max_dist_age_seat[k] = max(max_dist_age_seat[k], age)
            max_dist_age = max(max_dist_age, age)
        beams = {(x, y) for (_id, ty, x, y) in env.elements() if ty == "Sunbeam"}
        prev_sleep = H.beam_account(st, beams, roster, width, height, prev_sleep, beams_acc)
        prev_play = H.play_account(st, roster, prev_play, plays_acc)
        H.needs_account(st, roster, needs_hist)
        if max_dist_age >= ABORT:
            aborted_at = n_ticks
            break

    row = {
        **({"aborted_streak": {"limit": ABORT, "at_tick": aborted_at}}
           if aborted_at is not None else {}),
        "play": plays_acc, "needs": needs_hist, "beam": beams_acc,
        "msg": msg_counts, "seating": "j14-eappend", "seats": [f"ppo:{slot}"] * roster,
        "seed": seed, "ticks": n_ticks, "clock": "c0+E-appended-col408",
        "nash": None, "nash_state": nash_state_sum / max(1, n_ticks),
        "mean_happiness": (hap_sum / max(1, n_ticks)).round(4).tolist(),
        "low_share": (low_ticks / max(1, n_ticks)).round(6).tolist(),
        "floor_touches": floor_touches.tolist(),
        "max_distress_age": max_dist_age,
        "max_distress_age_seat": max_dist_age_seat.tolist(),
        "dist_ticks": dist_ticks.tolist(),
    }
    return row, E_track[:n_ticks], play_track[:n_ticks]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", required=True)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    import torch
    torch.set_num_threads(1)
    fwd = load_j14(a.slot)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    E_all = np.full((N_SEEDS, TICKS, 5), np.nan, np.float32)
    play_all = np.zeros((N_SEEDS, TICKS, 5), bool)
    tick_counts = np.zeros(N_SEEDS, np.int64)
    with a.out.open("w") as f:
        f.write(json.dumps({"header": {"slot": a.slot, "seed0": SEED0, "seeds": N_SEEDS,
                                       "ticks": TICKS, "abort_streak": ABORT,
                                       "clock": "c0 + E appended col 408 (PREREG-D)",
                                       "config": CONFIG.name}}) + "\n")
        for i in range(N_SEEDS):
            row, E_t, play_t = leg(a.slot, SEED0 + i, fwd)
            n = E_t.shape[0]
            E_all[i, :n], play_all[i, :n], tick_counts[i] = E_t, play_t, n
            f.write(json.dumps(row) + "\n")
            f.flush()
            print(f"seed {SEED0 + i}: hap {np.mean(row['mean_happiness']):.3f}"
                  + (" ABORTED" if "aborted_streak" in row else ""), flush=True)
    np.savez_compressed(a.out.parent / f"{a.slot}-ebands.npz",
                        E=E_all, playing=play_all, ticks=tick_counts,
                        seed0=SEED0, slot=a.slot)
    print("wrote", a.out, "and", a.out.parent / f"{a.slot}-ebands.npz")


if __name__ == "__main__":
    main()
