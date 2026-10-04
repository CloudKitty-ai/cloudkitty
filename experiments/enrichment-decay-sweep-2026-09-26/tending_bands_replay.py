"""Step-1 instrument (PREREG-L §Step 1): deterministic replays of
the four recorded arms recording per-tick activity argmax + E, and
the banded tending-start read. Control legs (l14) run the stock
policy at clock-pinned 0; live legs (j14) run the AddE policy with
E appended — each leg verified tick-exact against its recorded
battery row (mean_happiness equality) before use.

    CERT_ARTS=artifacts tending_bands_replay.py --slot l14-s1 \
        --out results-raw/tending-bands/l14-s1.npz
    CERT_ARTS=artifacts tending_bands_replay.py --summary results-raw/tending-bands/summary.json
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
# PREREG-L restates PREREG-D's frozen literals
EDGE_LOW = 0.43660981456438697
EDGE_HIGH = 0.8065612316131592
MIN_OCC = 10_000
# act stores the ARGMAX INDEX over self cols 9..15, so codes are
# 0-based enum positions (Idle 0, Resting 1, Sleeping 2, Eating 3,
# Drinking 4, Playing 5, Grooming 6 — encodings.md activity order),
# NOT absolute obs columns. First summary run compared against
# columns 11/12/13 and read all-zero — the vacuous output was the
# tell; fixed before any write-up.
ACT_SLEEP, ACT_EAT, ACT_DRINK = 2, 3, 4
TEND = {"eat": ACT_EAT, "drink": ACT_DRINK, "sleep": ACT_SLEEP}
CATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]


def recorded_rows(slot):
    name = ("j14-legs.jsonl" if slot.startswith("j14") else
            "gen1-A_" + "_".join(f"s{i}-{slot}" for i in range(5)) + "-c0-eval-30x20000.jsonl")
    rows = {}
    for line in (B / slot / name).read_text().splitlines():
        r = json.loads(line)
        if "seed" in r:
            rows[r["seed"]] = r
    return rows


def make_fwd(slot):
    import torch
    import cert_harness_fog as H
    if slot.startswith("l14"):
        return H.load_model(f"ppo:{slot}"), False
    import probe_eval_j14 as pj
    return pj.load_j14(slot), True


def leg(slot, seed, fwd, live):
    import cloudkitty
    import cert_harness_fog as H
    import train_ppo_enrich2c as tc
    env = cloudkitty.ParallelEnv(str(CONFIG), horizon=TICKS)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    roster = len(names)
    hap_sum = np.zeros(roster)
    Eo = np.zeros((1, roster))
    Ec = np.zeros((1, roster))
    E_track = np.zeros((TICKS, roster), np.float32)
    act_track = np.zeros((TICKS, roster), np.int8)
    for t in range(TICKS):
        ob = np.stack([np.asarray(obs[a], np.float32) for a in names])
        valid = np.ones((1, roster), bool)
        Eo, Ec = tc.roll_E_step(ob[None, :, :], valid, Eo, Ec)
        E_now = (Eo + Ec)[0].astype(np.float32)
        E_track[t] = E_now
        act_track[t] = ob[:, 9:16].argmax(1)  # activity one-hot argmax
        ob[:, H.CLOCK_INDEX] = 0.0
        if live:
            ob = np.concatenate([ob, E_now[:, None]], 1)
        mk = np.stack([np.asarray(infos[a]["mask"], np.uint8) for a in names]).astype(bool)
        lg = np.asarray(fwd(ob, mk), np.float32)
        a0 = np.where(mk[:, :H.N_ACT], lg[:, :H.N_ACT], H.NEG_INF).argmax(1)
        g0 = np.where(mk[:, H.N_ACT:], lg[:, H.N_ACT:], H.NEG_INF).argmax(1)
        obs, _r, _te, _tr, infos = env.step(
            {a: (int(a0[i]), int(g0[i])) for i, a in enumerate(names)})
        st = np.asarray(env.state(), np.float32)
        for k in range(roster):
            hap_sum[k] += float(st[k * H.PER_KITTY + H.HAP]) * 100
    return E_track, act_track, (hap_sum / TICKS).round(4).tolist()


def run_slot(slot, out):
    import torch
    torch.set_num_threads(1)
    fwd, live = make_fwd(slot)
    rec = recorded_rows(slot)
    E_all = np.zeros((N_SEEDS, TICKS, 5), np.float32)
    act_all = np.zeros((N_SEEDS, TICKS, 5), np.int8)
    for i in range(N_SEEDS):
        seed = SEED0 + i
        E_all[i], act_all[i], mean_hap = leg(slot, seed, fwd, live)
        assert mean_hap == rec[seed]["mean_happiness"], (
            f"REPLAY DRIFT {slot} seed {seed}: {mean_hap} != {rec[seed]['mean_happiness']}")
        print(f"{slot} seed {seed}: verified vs recorded row", flush=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, E=E_all, act=act_all, seed0=SEED0, slot=slot)
    print("wrote", out)


def starts(act, code):
    """(seeds, ticks, 5) bool of 0->1 transitions into activity `code`;
    tick 0 counts as a start if the leg begins in it."""
    flag = act == code
    prev = np.zeros_like(flag)
    prev[:, 1:] = flag[:, :-1]
    return flag & ~prev


def band_rates(E, act):
    low, high = E <= EDGE_LOW, E >= EDGE_HIGH
    out = {}
    for kind, code in TEND.items():
        st = starts(act, code)
        per = {}
        for k in range(5):
            lo, hi = low[:, :, k], high[:, :, k]
            per[k] = {
                "occ_low": int(lo.sum()), "occ_high": int(hi.sum()),
                "rate_low": float(st[:, :, k][lo].mean()),
                "rate_high": float(st[:, :, k][hi].mean()),
            }
            per[k]["contrast"] = per[k]["rate_high"] - per[k]["rate_low"]
            per[k]["read"] = bool(lo.sum() >= MIN_OCC and hi.sum() >= MIN_OCC)
        out[kind] = per
    return out


def summarize(out_path):
    d = out_path.parent
    data = {}
    for p in sorted(d.glob("*.npz")):
        z = np.load(p)
        data[str(z["slot"])] = band_rates(z["E"], z["act"])
    ctrl_slots = [s for s in data if s.startswith("l14")]
    live_slots = [s for s in data if s.startswith("j14")]
    # pooled control per kind (recompute over concatenated arrays)
    zs = [np.load(d / f"{s}.npz") for s in ctrl_slots]
    ctrl_pool = band_rates(np.concatenate([z["E"] for z in zs]),
                           np.concatenate([z["act"] for z in zs]))
    summary = {"per_slot": data, "control_pooled": ctrl_pool,
               "edges": {"low": EDGE_LOW, "high": EDGE_HIGH, "min_occ": MIN_OCC},
               "excess": {}, "control_spread": {}, "declared_reading": {}}
    for kind in TEND:
        spread = {k: abs(data[ctrl_slots[0]][kind][k]["contrast"]
                         - data[ctrl_slots[1]][kind][k]["contrast"]) for k in range(5)}
        summary["control_spread"][kind] = spread
        exc = {}
        for s in live_slots:
            exc[s] = {k: (data[s][kind][k]["contrast"] - ctrl_pool[kind][k]["contrast"]
                          if data[s][kind][k]["read"] else None) for k in range(5)}
        summary["excess"][kind] = exc
        # declared form: >=3/5 seats consistent sign on BOTH live seeds,
        # pooled |magnitude| > 2x the kind's largest control spread
        verdicts = []
        for sign in (1, -1):
            ok = all(sum(1 for k in range(5)
                         if exc[s][k] is not None and np.sign(exc[s][k]) == sign) >= 3
                     for s in live_slots)
            verdicts.append(ok)
        pooled_mag = float(np.mean([abs(v) for s in live_slots
                                    for v in exc[s].values() if v is not None]))
        summary["declared_reading"][kind] = {
            "consistent_sign_3of5_both": verdicts[0] or verdicts[1],
            "sign": (1 if verdicts[0] else (-1 if verdicts[1] else 0)),
            "pooled_abs_excess": pooled_mag,
            "two_x_max_spread": 2 * max(spread.values()),
            "fires": bool((verdicts[0] or verdicts[1])
                          and pooled_mag > 2 * max(spread.values())),
        }
    out_path.write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: summary["declared_reading"][k] for k in TEND}, indent=1))
    for kind in TEND:
        print(f"\n{kind}: ctrl pooled contrast / live contrasts / excess per seat")
        for k in range(5):
            row = [f"{data[s][kind][k]['contrast']:+.6f}/{summary['excess'][kind][s][k]:+.6f}"
                   if summary["excess"][kind][s][k] is not None else "UNREAD"
                   for s in live_slots]
            print(f"  {CATS[k]}: ctrl {ctrl_pool[kind][k]['contrast']:+.6f} | " + " | ".join(row))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--summary", type=Path)
    a = ap.parse_args()
    if a.summary:
        summarize(a.summary)
    else:
        run_slot(a.slot, a.out)


if __name__ == "__main__":
    main()
