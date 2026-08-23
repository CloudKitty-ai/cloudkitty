#!/usr/bin/env python3
"""Behavior census for bio updates: who spends time with whom, paired
behavior distribution and directionality, meow/purr dialect, time
budgets — per seat, on any cert_harness6 seating.

Reproducible per roster change: same command, new seating name.
Reads the engine's global state per tick (global_state.rs layout:
pos 7-8 normalized by map size; activity one-hot 9-15 in the order
Idle/Resting/Sleeping/Eating/Drinking/Playing/Grooming; partner
present flag 16; partner resolved flag 17 + roster index/(n-1) at
18). Directionality conventions:
  - groom: the actor's activity is Grooming with a partner resolved;
    the groomee's own activity does not change — so actor->target is
    read directly from state.
  - rest/sleep/play with partner: mutual states; "initiations" count
    the seat that TRANSITIONS into the partnered activity (a seat
    joining an already-partnered mate counts; both transitioning on
    the same tick counts one initiation each — the pair formed).
  - dialect: the msg head each policy seat actually emits per tick
    (masked argmax, greedy — the harness's selection rule).

Provenance-stamped per F-028. Output:
results-raw/bio-census-<seating>--<seed0>x<seeds>.json
"""
import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
import sys  # noqa: E402
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "attn-oracle-2026-08-15"))

from cert_harness6 import (  # noqa: E402
    BANDS, N_ACT, N_HEADS, NEG_INF, PER_KITTY, SEATINGS, load_model,
    provenance)

OFF_HAP, OFF_POS, OFF_ACT, OFF_SOCIAL, OFF_PARTNER = 6, 7, 9, 16, 17
ACTIVITIES = ["Idle", "Resting", "Sleeping", "Eating", "Drinking",
              "Playing", "Grooming"]
PAIRED = ["Resting", "Sleeping", "Playing", "Grooming"]
MSGS = ["Silent", "WantEat", "WantDrink", "Mew", "WantPlay",
        "WantCuddle", "Purr", "WantBath", "WantSleep", "HereFood",
        "HereWater", "HereCritter", "HereSunbeam", "Chirp", "Trill",
        "Ekekek"]


def run_one(job):
    seating_name, seed, ticks, config_path = job
    import tomllib

    import cloudkitty

    with open(config_path, "rb") as f:
        cfg = tomllib.load(f)
    kitties = cfg["kitty"]
    roster = len(kitties)
    width, height = cfg["world"]["width"], cfg["world"]["height"]
    seats = list(SEATINGS[seating_name])
    assert len(seats) == roster, (seating_name, roster)
    assert all(s != "scripted" for s in seats), \
        "census reads the msg head; scripted seats have none"
    models = {s: load_model(s) for s in set(seats)}

    env = cloudkitty.ParallelEnv(str(config_path), horizon=ticks)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    seat_of = {f"kitty_{k['id']}": s for k, s in zip(kitties, seats)}
    assert names == [f"kitty_{k['id']}" for k in kitties], names

    pos = np.zeros((ticks, roster, 2), np.int16)
    act = np.zeros((ticks, roster), np.int8)
    partner = np.full((ticks, roster), -1, np.int8)
    msg = np.zeros((ticks, roster), np.int8)
    hap = np.zeros((ticks, roster), np.float32)

    for t in range(ticks):
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
        obs, _r, term, trunc, infos = env.step(acts)
        st = np.asarray(env.state(), np.float32)
        msg[t] = g0
        for k in range(roster):
            b = k * PER_KITTY
            onehot = st[b + OFF_ACT:b + OFF_ACT + 7]
            assert abs(onehot.sum() - 1.0) < 1e-4, \
                "activity one-hot broken - wrong state offset?"
            act[t, k] = onehot.argmax()
            pos[t, k] = (round(st[b + OFF_POS] * width),
                         round(st[b + OFF_POS + 1] * height))
            if st[b + OFF_PARTNER] > 0.5:
                p = round(st[b + OFF_PARTNER + 1] * (roster - 1))
                assert p != k, "partner resolved to self"
                partner[t, k] = p
            hap[t, k] = st[b + OFF_HAP] * 100
        if any(term.values()) or any(trunc.values()):
            pos, act, partner = pos[:t + 1], act[:t + 1], partner[:t + 1]
            msg, hap = msg[:t + 1], hap[:t + 1]
            break

    return analyze(seed, [k["name"] for k in kitties],
                   pos, act, partner, msg, hap)


def analyze(seed, names, pos, act, partner, msg, hap):
    ticks, roster = act.shape
    out = {"seed": seed, "ticks": ticks}

    # who spends time with whom: Chebyshev <= 1 (same or adjacent tile)
    cheb = np.abs(pos[:, :, None, :] - pos[:, None, :, :]).max(-1)
    out["together_share"] = {
        f"{names[i]}|{names[j]}": round(float((cheb[:, i, j] <= 1).mean()), 4)
        for i in range(roster) for j in range(i + 1, roster)}
    out["mean_tile_dist"] = {
        f"{names[i]}|{names[j]}": round(float(cheb[:, i, j].mean()), 2)
        for i in range(roster) for j in range(i + 1, roster)}

    # paired behavior: shares + initiations, directional (actor->partner)
    paired_share, initiations = {}, {}
    for ai, aname in enumerate(ACTIVITIES):
        if aname not in PAIRED:
            continue
        for k in range(roster):
            in_state = (act[:, k] == ai) & (partner[:, k] >= 0)
            for j in range(roster):
                if j == k:
                    continue
                with_j = in_state & (partner[:, k] == j)
                if not with_j.any():
                    continue
                key = f"{names[k]}->{names[j]}|{aname}"
                paired_share[key] = round(float(with_j.mean()), 4)
                starts = with_j[1:] & ~with_j[:-1]
                initiations[key] = int(starts.sum())
    out["paired_share"] = paired_share
    out["initiations"] = initiations

    # dialect: msg mix per seat, per 1k ticks
    dialect = {}
    for k in range(roster):
        counts = np.bincount(msg[:, k], minlength=16)
        nonsilent = int(counts.sum() - counts[0])
        d = {"per_1k_nonsilent": round(1000.0 * nonsilent / ticks, 2)}
        if nonsilent:
            for m in np.argsort(counts[1:])[::-1] + 1:
                if counts[m]:
                    d[MSGS[m]] = round(float(counts[m] / nonsilent), 3)
        dialect[names[k]] = d
    out["dialect"] = dialect

    # time budgets + play venue split (state-level, G3 language)
    budgets = {}
    for k in range(roster):
        b = {ACTIVITIES[a]: round(float((act[:, k] == a).mean()), 4)
             for a in range(7) if (act[:, k] == a).any()}
        playing = act[:, k] == ACTIVITIES.index("Playing")
        if playing.any():
            duet = playing & (partner[:, k] >= 0)
            b["play_partnered_share"] = round(
                float(duet.sum() / playing.sum()), 3)
        budgets[names[k]] = b
    out["time_budget"] = budgets
    out["happiness"] = {names[k]: round(float(hap[:, k].mean()), 2)
                        for k in range(roster)}
    return out


def aggregate(rows):
    """Mean across seeds for every numeric leaf that appears anywhere;
    counts (initiations) are means too — per-20k-tick rates."""
    agg = {}
    for section in ("together_share", "mean_tile_dist", "paired_share",
                    "initiations", "happiness"):
        keys = sorted({k for r in rows for k in r[section]})
        agg[section] = {
            k: round(float(np.mean([r[section].get(k, 0.0)
                                    for r in rows])), 4)
            for k in keys}
    agg["dialect"] = {}
    for name in rows[0]["dialect"]:
        keys = sorted({k for r in rows for k in r["dialect"][name]})
        agg["dialect"][name] = {
            k: round(float(np.mean([r["dialect"][name].get(k, 0.0)
                                    for r in rows])), 3)
            for k in keys}
    agg["time_budget"] = {}
    for name in rows[0]["time_budget"]:
        keys = sorted({k for r in rows for k in r["time_budget"][name]})
        agg["time_budget"][name] = {
            k: round(float(np.mean([r["time_budget"][name].get(k, 0.0)
                                    for r in rows])), 4)
            for k in keys}
    return agg


def budget_table(agg):
    """Markdown activity-% table, one row per cat — the standard
    post-placement summary. Idle includes travel (moving ticks carry
    the Idle activity); partnered-play share is duets as a fraction
    of that cat's play ticks."""
    cols = ["Idle", "Sleeping", "Playing", "Grooming", "Eating",
            "Drinking", "Resting"]
    lines = ["| cat | " + " | ".join(c.lower() for c in cols)
             + " | partnered play |",
             "|---|" + "---|" * (len(cols) + 1)]
    for name, b in agg["time_budget"].items():
        cells = [f"{100 * b.get(c, 0.0):.1f}%" for c in cols]
        pp = b.get("play_partnered_share")
        cells.append(f"{100 * pp:.0f}%" if pp is not None else "—")
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seating", choices=list(SEATINGS))
    ap.add_argument("--band", choices=list(BANDS), default="eval")
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--ticks", type=int, default=20_000)
    ap.add_argument("--config", type=Path,
                    default=HERE / "configs/phase1-cutover-bugs2.toml")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out-dir", type=Path, default=HERE / "results-raw")
    args = ap.parse_args()

    prov = provenance(args.config)
    print("provenance:", json.dumps(prov))
    seed0 = BANDS[args.band]
    jobs = [(args.seating, seed0 + i, args.ticks, args.config)
            for i in range(args.seeds)]
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers) as px:
        for r in px.map(run_one, jobs):
            rows.append(r)
            print(f"seed {r['seed']} done ({r['ticks']} ticks)",
                  flush=True)
    agg = aggregate(rows)
    out = {"provenance": prov, "seating": args.seating,
           "config": str(args.config), "seeds": args.seeds,
           "ticks": args.ticks, "aggregate": agg, "per_seed": rows}
    p = args.out_dir / (f"bio-census-{args.seating}--"
                        f"{seed0}x{args.seeds}.json")
    p.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(agg, indent=1))
    print("\n" + budget_table(agg) + "\n")
    print(f"wrote {p}")


if __name__ == "__main__":
    main()
