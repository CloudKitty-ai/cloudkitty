"""r5 forensics tracer (exp-006): per-tick traces of single battery runs.

Never a gate instrument. Reuses cert_harness6's seat loaders and stepping
verbatim (same env, same greedy argmax, same post-step read), so a trace
of (seating, seed, config) IS the battery run — the summary re-derives
the battery row's mda/nash and must match it exactly, which is the
tracer's own validity check.

Written for the owner's post-battery forensics ruling
(results/battery-2026-08-20.md, fork option 1): name the mechanism
behind the r5 failures on family-11 before any gate decision.

  .venv/bin/python forensics_r5.py trace candidate-r5 880030 \
      --config family-spread/family-11.toml
  .venv/bin/python forensics_r5.py summary traces/trace-candidate-r5-880030.npz
"""
import argparse
import json
import sys
import tomllib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cert_harness6 import (LOW_HAPPINESS, N_ACT, N_HEADS, NEG_INF, SEATINGS,
                           load_model, provenance)

NEEDS = ["eat", "drink", "sleep", "play", "cuddle", "bath"]
ACTIVITIES = ["idle", "resting", "sleeping", "eating", "drinking",
              "playing", "grooming"]
# global_state.rs per-kitty layout (32): needs 0-5, happiness 6, pos 7-8,
# activity one-hot 9-15, social 16, partner 17-18, progress 19,
# distress flags 20-25, traits 26-31.
PER_KITTY = 32
OFF_NEEDS, OFF_HAP, OFF_POS, OFF_ACT, OFF_DIST = 0, 6, 7, 9, 20
ELEMENT_MAX = {"water": 5, "chow": 7, "bug": 7, "greeble": 3, "sunbeam": 5}


def trace(args):
    import cloudkitty

    with open(args.config, "rb") as f:
        cfg = tomllib.load(f)
    kitties = cfg["kitty"]
    roster = len(kitties)
    seats = SEATINGS[args.seating]
    assert len(seats) == roster, (args.seating, roster)

    control = {f"kitty_{k['id']}": "needs_driven"
               for k, s in zip(kitties, seats) if s == "scripted"}
    models = {s: load_model(s) for s in set(seats) if s != "scripted"}

    env = cloudkitty.ParallelEnv(str(args.config),
                                 control=control or None, horizon=args.ticks)
    obs, infos = env.reset(seed=args.seed)
    names = list(env.possible_agents)
    seat_of = {f"kitty_{k['id']}": s for k, s in zip(kitties, seats)}

    width = None
    states = None
    rewards = np.zeros(args.ticks, np.float32)
    chosen = np.full((args.ticks, len(names), 2), -1, np.int16)
    el_pos = {t: np.full((args.ticks, m, 2), -1, np.int8)
              for t, m in ELEMENT_MAX.items()}
    meows = {}

    for t in range(args.ticks):
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
            chosen[t] = np.stack([a0, g0], 1)
        obs, rew, _term, _trunc, infos = env.step(acts)
        st = np.asarray(env.state(), np.float32)
        if states is None:
            width = st.shape[0]
            states = np.zeros((args.ticks, width), np.float32)
        states[t] = st
        if names:
            rewards[t] = float(rew[names[0]])
        counts = dict.fromkeys(ELEMENT_MAX, 0)
        for _eid, ekind, ex, ey in env.elements():
            ekind = ekind.lower()
            assert ekind in ELEMENT_MAX, ekind
            i = counts[ekind]
            if i < ELEMENT_MAX[ekind]:
                el_pos[ekind][t, i] = (ex, ey)
                counts[ekind] = i + 1
        for mt, mk_id, word in env.recent_meows():
            meows[(int(mt), int(mk_id), word)] = None

    out_dir = args.out_dir
    out_dir.mkdir(exist_ok=True)
    stem = f"trace-{args.seating}-{args.seed}"
    np.savez_compressed(
        out_dir / f"{stem}.npz", states=states, rewards=rewards,
        chosen=chosen, **{f"pos_{k}": v for k, v in el_pos.items()})
    sidecar = {
        "provenance": provenance(args.config),
        "seating": args.seating, "seed": args.seed, "ticks": args.ticks,
        "config": str(args.config), "roster": roster,
        "kitties": [{"id": k["id"], "name": k["name"],
                     "seat": s} for k, s in zip(kitties, seats)],
        "policy_agents": names,
        "floor": cfg["happiness"]["floor"],
        "meows": sorted([t, k, w] for (t, k, w) in meows),
    }
    (out_dir / f"{stem}.json").write_text(
        json.dumps(sidecar, indent=1) + "\n")
    print(f"wrote {out_dir / stem}.npz (+.json), "
          f"{len(sidecar['meows'])} meows")
    summarize_arrays(states, rewards, sidecar, el_pos)


def streaks(flags):
    """All maximal runs of True in a 1-D bool array → (start, length)."""
    out = []
    run = 0
    for i, f in enumerate(flags):
        if f:
            run += 1
        elif run:
            out.append((i - run, run))
            run = 0
    if run:
        out.append((len(flags) - run, run))
    return out


def nearest_dist(pos_k, el_t):
    """Manhattan distance from one kitty tile to the nearest live element."""
    live = el_t[el_t[:, 0] >= 0]
    if not len(live):
        return None
    return int(np.abs(live.astype(np.int32) - pos_k.astype(np.int32))
               .sum(1).min())


def summarize_arrays(states, rewards, sidecar, el_pos):
    roster = sidecar["roster"]
    ticks = states.shape[0]
    names = [k["name"] for k in sidecar["kitties"]]
    base = np.arange(roster) * PER_KITTY
    needs = np.stack([states[:, b + OFF_NEEDS:b + OFF_NEEDS + 6]
                      for b in base], 1) * 100          # (t, k, 6)
    hap = np.stack([states[:, b + OFF_HAP] for b in base], 1) * 100
    act = np.stack([states[:, b + OFF_ACT:b + OFF_ACT + 7]
                    for b in base], 1).argmax(2)        # (t, k)
    dist = np.stack([states[:, b + OFF_DIST:b + OFF_DIST + 6]
                     for b in base], 1) > 0             # (t, k, 6)
    # positions in tiles (state stores /width, /height; family worlds are
    # square so one scale — asserted against the config)
    with open(sidecar["config"], "rb") as f:
        cfg = tomllib.load(f)
    assert cfg["world"]["width"] == cfg["world"]["height"]
    scale = cfg["world"]["width"]
    pos = np.stack([states[:, b + OFF_POS:b + OFF_POS + 2]
                    for b in base], 1) * scale          # (t, k, 2)

    has_policy = bool(sidecar["policy_agents"])
    print(f"\n=== {sidecar['seating']} seed {sidecar['seed']} "
          f"({ticks} ticks) ===")
    if has_policy:
        print(f"nash {rewards.mean():.4f}")
    all_streaks = []
    for k in range(roster):
        for n in range(6):
            for s0, ln in streaks(dist[:, k, n]):
                all_streaks.append((ln, s0, k, n))
    all_streaks.sort(reverse=True)
    print(f"max_distress_age {all_streaks[0][0] if all_streaks else 0} "
          f"(battery-row check)")
    print("\ntop distress streaks (len, ticks, kitty, need):")
    for ln, s0, k, n in all_streaks[:8]:
        print(f"  {ln:5d}  {s0}-{s0 + ln}  {names[k]:<10} {NEEDS[n]}")

    print("\nper-kitty over the full run:")
    print(f"  {'kitty':<10} {'seat':<16} hap   low%  " +
          " ".join(f"{n:>6}" for n in NEEDS) + "   top activities")
    for k in range(roster):
        shares = np.bincount(act[:, k], minlength=7) / ticks
        top = ", ".join(f"{ACTIVITIES[i]} {shares[i]:.0%}"
                        for i in np.argsort(-shares)[:3])
        low = (hap[:, k] < LOW_HAPPINESS).mean()
        print(f"  {names[k]:<10} {sidecar['kitties'][k]['seat']:<16} "
              f"{hap[:, k].mean():5.1f} {low:5.1%}  " +
              " ".join(f"{needs[:, k, n].mean():6.1f} " f""
                       for n in range(6)) + f"  {top}")

    water = el_pos["water"]
    wcount = (water[:, :, 0] >= 0).sum(1)
    uniq = {tuple(map(tuple, water[t][water[t, :, 0] >= 0]))
            for t in range(ticks)}
    print(f"\nwater: count min {wcount.min()} max {wcount.max()}, "
          f"{len(uniq)} distinct position-sets over the run")
    for k in range(roster):
        d = [nearest_dist(pos[t, k], water[t]) for t in
             range(0, ticks, 100)]
        d = [x for x in d if x is not None]
        print(f"  {names[k]:<10} mean dist to nearest water "
              f"{np.mean(d):5.1f} tiles (sampled)")
    return dict(needs=needs, hap=hap, act=act, dist=dist, pos=pos)


def summary(args):
    z = np.load(args.trace)
    sidecar = json.loads(Path(str(args.trace).replace(".npz", ".json"))
                         .read_text())
    el_pos = {k: z[f"pos_{k}"] for k in ELEMENT_MAX}
    summarize_arrays(z["states"], z["rewards"], sidecar, el_pos)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("trace")
    t.add_argument("seating", choices=list(SEATINGS))
    t.add_argument("seed", type=int)
    t.add_argument("--ticks", type=int, default=20_000)
    t.add_argument("--config", type=Path, required=True)
    t.add_argument("--out-dir", type=Path, default=HERE / "traces")
    t.set_defaults(fn=trace)
    s = sub.add_parser("summary")
    s.add_argument("trace", type=Path)
    s.set_defaults(fn=summary)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
