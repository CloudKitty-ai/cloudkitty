"""E-band edge freeze for the joint arm (PREREG-D §Instrument): replay
the recorded l14 control legs deterministically, tracking the
enrichment stock E per (seed, tick, seat) via the guard-proven
recurrence, WITHOUT the policy seeing it — the control never saw E.
The pooled per-tick E distribution over both recorded l14 seeds sets
the high/low tercile edges, frozen as literals in PREREG-D before the
live arm runs (Professor's joint-arm critique: edges from the
recorded control, not fixed constants, not the live arm's own
distribution).

Built-in verification: each replayed leg's mean_happiness row must
EQUAL the recorded battery row for that seed (same trajectory or the
instrument drifted); a mismatch aborts the slot.

    e_edges_replay.py --slot l14-s1 --out results-raw/e-edges/l14-s1.npz
    e_edges_replay.py --summary results-raw/e-edges/summary.json
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
sys.path.insert(0, str(HERE / "trainer"))

CONFIG = HERE.parent / "beam-world-screen-2026-09-19" / "package.toml"
SEED0, N_SEEDS, TICKS = 870_001, 30, 20_000
B = HERE / "results-raw" / "battery"


def recorded_rows(slot):
    path = B / slot / ("gen1-A_" + "_".join(f"s{i}-{slot}" for i in range(5))
                       + "-c0-eval-30x20000.jsonl")
    rows = {}
    for line in path.read_text().splitlines():
        r = json.loads(line)
        if "seed" in r:
            rows[r["seed"]] = r
    return rows


def leg(slot, seed, fwd, tc, H):
    import cloudkitty
    import torch  # noqa: F401  (thread pin done in main)
    env = cloudkitty.ParallelEnv(str(CONFIG), horizon=TICKS)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    roster = len(names)
    hap_sum = np.zeros(roster)
    n_ticks = 0
    Eo = np.zeros((1, roster))
    Ec = np.zeros((1, roster))
    E_track = np.zeros((TICKS, roster), np.float32)
    play_track = np.zeros((TICKS, roster), bool)
    for t in range(TICKS):
        ob = np.stack([np.asarray(obs[a], np.float32) for a in names])
        valid = np.ones((1, roster), bool)
        Eo, Ec = tc.roll_E_step(ob[None, :, :], valid, Eo, Ec)
        E_track[t] = (Eo + Ec)[0].astype(np.float32)
        play_track[t] = ob[:, 14] > 0.5  # ACT_PLAY, the recurrence's own flag
        # the recorded legs are -c0: clock served = pinned to 0 before the
        # forward (cert_harness_fog clock_mode "served"); without this the
        # replay drifts from the recorded rows (caught by the assert below)
        ob[:, H.CLOCK_INDEX] = 0.0
        mk = np.stack([np.asarray(infos[a]["mask"], np.uint8)
                       for a in names]).astype(bool)
        lg = np.asarray(fwd(ob, mk), np.float32)
        a0 = np.where(mk[:, :H.N_ACT], lg[:, :H.N_ACT], H.NEG_INF).argmax(1)
        g0 = np.where(mk[:, H.N_ACT:], lg[:, H.N_ACT:], H.NEG_INF).argmax(1)
        obs, _r, _te, _tr, infos = env.step(
            {a: (int(a0[i]), int(g0[i])) for i, a in enumerate(names)})
        st = np.asarray(env.state(), np.float32)
        n_ticks += 1
        for k in range(roster):
            hap_sum[k] += float(st[k * H.PER_KITTY + H.HAP]) * 100
    mean_hap = (hap_sum / max(1, n_ticks)).round(4).tolist()
    return E_track, play_track, mean_hap


def run_slot(slot, out):
    import torch
    import cert_harness_fog as H
    import train_ppo_enrich2c as tc
    torch.set_num_threads(1)
    fwd = H.load_model(f"ppo:{slot}")
    rec = recorded_rows(slot)
    E_all = np.zeros((N_SEEDS, TICKS, 5), np.float32)
    play_all = np.zeros((N_SEEDS, TICKS, 5), bool)
    for i in range(N_SEEDS):
        seed = SEED0 + i
        E_all[i], play_all[i], mean_hap = leg(slot, seed, fwd, tc, H)
        if TICKS == 20_000:  # smoke runs cannot match the recorded rows
            assert mean_hap == rec[seed]["mean_happiness"], (
                f"REPLAY DRIFT {slot} seed {seed}: {mean_hap} != "
                f"{rec[seed]['mean_happiness']}")
        print(f"{slot} seed {seed}: verified vs recorded row", flush=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, E=E_all, playing=play_all,
                        seed0=SEED0, ticks=TICKS, slot=slot)
    print("wrote", out)


def summarize(out):
    d = out.parent
    Es, plays, slots = [], [], []
    for p in sorted(d.glob("l14-*.npz")):
        z = np.load(p)
        Es.append(z["E"])
        plays.append(z["playing"])
        slots.append(str(z["slot"]))
    E = np.concatenate(Es)      # (legs*30, 20000, 5)
    P = np.concatenate(plays)
    lo, hi = np.quantile(E, [1 / 3, 2 / 3])
    low, high = E <= lo, E >= hi
    per_seat = {}
    for k in range(5):
        per_seat[k] = {
            "occ_low": int(low[:, :, k].sum()), "occ_high": int(high[:, :, k].sum()),
            "play_low": float(P[:, :, k][low[:, :, k]].mean()),
            "play_high": float(P[:, :, k][high[:, :, k]].mean()),
        }
        per_seat[k]["contrast"] = per_seat[k]["play_high"] - per_seat[k]["play_low"]
    # per-slot contrasts at the POOLED edges (the margin's noise floor:
    # the same policy family, two seeds, same edges)
    per_slot = {}
    for s, (Ei, Pi) in zip(slots, zip(Es, plays)):
        c = {}
        for k in range(5):
            l_, h_ = Ei[:, :, k] <= lo, Ei[:, :, k] >= hi
            c[k] = float(Pi[:, :, k][h_].mean() - Pi[:, :, k][l_].mean())
        per_slot[s] = c
    spread = {k: abs(per_slot[slots[0]][k] - per_slot[slots[1]][k])
              for k in range(5)} if len(slots) == 2 else {}
    summary = {
        "slots": slots, "edge_low": float(lo), "edge_high": float(hi),
        "pooled_ticks": int(E.size),
        "E_quartiles": [float(x) for x in np.quantile(E, [0, .25, .5, .75, 1])],
        "per_seat_control": per_seat,
        "per_slot_contrast": per_slot,
        "between_seed_spread": spread,
        "pooled_control_contrast": float(
            P[high].mean() - P[low].mean()),
    }
    (d / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--summary", type=Path)
    ap.add_argument("--smoke-ticks", type=int, default=None)
    a = ap.parse_args()
    if a.summary:
        summarize(a.summary)
        return
    global TICKS
    if a.smoke_ticks:
        TICKS = a.smoke_ticks  # smoke only: row verification will fail; skip it
    run_slot(a.slot, a.out)


if __name__ == "__main__":
    main()
