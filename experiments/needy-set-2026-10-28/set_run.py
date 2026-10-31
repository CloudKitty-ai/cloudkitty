"""§11 step 5 — the set: arm T, arm N and arm E, both halves, S1 armed throughout.

Owner's word 2026-10-31 after the step 4 S2 read (episode-window drop 2.355,
her-word band) and the cascade diagnosis: "Ok, I'm satisfied that this is not a
structural issue, more of a bug. Let's proceed".

Worlds (DECLARATION §3 seeds, §7 sizing at w = 46 and w_E = 16, amendment 1):
  arm T  P's 10 evaluation seeds per block, 4,000 ticks, P's config with seat k
         on `teacher`; the first world per block ran clean in step 4 and is skipped.
  arm N  each block's first 46 seeds (23 tuning, 23 confirming), 6,000 ticks,
         `g2leg-20-N<k>.toml` (edge 4,500).
  arm E  each block's first 16 seeds (8 and 8), 800 ticks, `g2leg-20-E<k>-n60.toml`.
Collection is covered_scout's call, world for world (`g2-rot2` less seat k's
network, seat k scripted on its config behaviour, every covered observation
saved, S1 = F-053's 1,000-tick single-need streak on the covered seats only).
Any covered abort saves what was collected, exits 3, and goes to her (§7).

Burn order: arm T, arm E, arm N (the short arms first); resumable.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "seating-analysis-g2-2026-10-21"))
import needy_read as R  # noqa: E402
import covered_scout as CS  # noqa: E402

W_N, W_E = 46, 16              # §7 sizing on the edge-4,500 re-scout (RESULTS step 3, amendment 1)
RAW_SET = CS.RAW_SET
TICKS = CS.TICKS


def worlds():
    """[(arm, k, config, seed, ticks, out)] in burn order: every world of the
    set, the five arm T worlds already on disk from step 4 included (skipped
    as present by `run`)."""
    out = []
    for k in CS.BLOCKS:
        for seed in R.arm_block("T", k)["seeds"]:
            out.append(("T", k, CS.P_CONFIGS / f"g2leg-20-P{k}.toml", seed, TICKS["T"], RAW_SET / f"T{k}" / f"streams-{seed}.npz"))
    for k in CS.BLOCKS:
        for seed in R.arm_block("E", k)["seeds"][:W_E]:
            out.append(("E", k, HERE / f"g2leg-20-E{k}-n{CS.N_PIN}.toml", seed, TICKS["E"], RAW_SET / f"E{k}" / f"streams-{seed}.npz"))
    for k in CS.BLOCKS:
        for seed in R.arm_block("N", k)["seeds"][:W_N]:
            out.append(("N", k, HERE / f"g2leg-20-N{k}.toml", seed, TICKS["N"], RAW_SET / f"N{k}" / f"streams-{seed}.npz"))
    return out


def plan():
    ws = worlds()
    by_arm = {}
    for arm, k, cfg, seed, ticks, out in ws:
        a = by_arm.setdefault(arm, {"worlds": 0, "present": 0, "covered_cat_ticks": 0, "halves": {"tuning": 0, "confirming": 0}})
        a["worlds"] += 1
        a["present"] += out.exists()
        a["covered_cat_ticks"] += ticks * 4
        a["halves"][R.half_of(arm, k, seed)] += 1
    remaining = sum(t * 4 for a, k, c, s, t, o in ws if not o.exists())
    return {"w_N": W_N, "w_E": W_E, "arms": by_arm, "worlds": len(ws),
            "covered_cat_ticks_total": sum(a["covered_cat_ticks"] for a in by_arm.values()),
            "covered_cat_ticks_remaining": remaining}


def run():
    import torch
    import seating_collect_g2 as C
    torch.set_num_threads(1)
    ws = worlds()
    t0 = time.time()
    for i, (arm, k, cfg, seed, ticks, out) in enumerate(ws):
        if out.exists():
            print(f"[{i + 1}/{len(ws)}] {arm}{k} {seed}: present, skipped", flush=True)
            continue
        t1 = time.time()
        arrays, meta = C.collect(CS.SEATING, seed, ticks, CS.S1_STREAK, config=cfg, save_obs=True,
                                 scripted_seat=k - 1, abort_covered_only=True)
        out.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(out, meta=json.dumps(meta), **arrays)
        covered = [j for j, s in enumerate(meta["seats"]) if s != "scripted"]
        assert covered == [j for j in range(5) if j != k - 1] and meta["abort_seats"] == covered, meta["seats"]
        assert (meta["needy_seat"] == k - 1) == (arm != "T"), (arm, meta["needy_seat"])
        hap = arrays["hap"][:, covered].mean()
        print(f"[{i + 1}/{len(ws)}] {arm}{k} {seed}: {meta['ticks']} ticks, covered mean happiness {hap:.2f}, "
              f"{time.time() - t1:.0f}s (total {time.time() - t0:.0f}s)", flush=True)
        if meta["aborted_at"] is not None:
            print(f"== ABORT: covered seat at the S1 line in {arm}{k} {seed} at tick {meta['aborted_at']}; "
                  f"the set stops here and goes to her (§7)", flush=True)
            sys.exit(3)
    print(f"== set done: {len(ws)} worlds, {time.time() - t0:.0f}s", flush=True)


def read():
    """The run record, not a §5 read: per arm, the worlds and covered
    cat-ticks burned, the covered seats' mean happiness over worlds, S1's
    worst covered single-need streak (must be under the line in every world),
    and the scripted friend's worst streak and grave ticks (recorded, never a
    stop)."""
    arms = {}
    worst = {"covered": (0, None), "scripted": (0, None)}
    aborts = []
    for arm, k, cfg, seed, ticks, out in worlds():
        meta = json.loads(str(np.load(out, allow_pickle=True)["meta"]))
        if meta["aborted_at"] is not None:
            aborts.append((arm, k, seed, meta["aborted_at"]))
            continue
        w = R.load_world(out)
        scr = k - 1
        cov = [j for j in range(5) if j != scr]
        assert meta["scripted_seat"] == scr and w["ticks"] == ticks, (arm, k, seed, meta["scripted_seat"], w["ticks"])
        streaks = R.longest_streaks(w["distress"])          # (seats, needs)
        cov_streak = int(streaks[cov].max())
        scr_streak = int(streaks[scr].max())
        a = arms.setdefault(arm, {"worlds": 0, "ticks_per_world": ticks, "covered_cat_ticks": 0, "covered_mean_happiness": [],
                                  "worst_covered_streak": 0, "worlds_with_covered_distress": 0, "worlds_with_covered_grave": 0,
                                  "scripted_worst_streak": 0, "scripted_grave_ticks_mean": 0.0})
        a["worlds"] += 1
        a["covered_cat_ticks"] += ticks * 4
        a["covered_mean_happiness"].append(float(w["hap"][:, cov].mean()))
        a["worst_covered_streak"] = max(a["worst_covered_streak"], cov_streak)
        a["worlds_with_covered_distress"] += bool((w["distress"][:, cov] != 0).any())
        a["worlds_with_covered_grave"] += bool((w["codes"][:, cov] == R.S.GRAVE).any())
        a["scripted_worst_streak"] = max(a["scripted_worst_streak"], scr_streak)
        a["scripted_grave_ticks_mean"] += int((w["codes"][:, scr] == R.S.GRAVE).sum())
        if cov_streak > worst["covered"][0]:
            worst["covered"] = (cov_streak, f"{arm}{k} {seed}")
        if scr_streak > worst["scripted"][0]:
            worst["scripted"] = (scr_streak, f"{arm}{k} {seed}")
    for a in arms.values():
        h = np.asarray(a["covered_mean_happiness"])
        a["covered_mean_happiness"] = {"mean": round(float(h.mean()), 2), "min": round(float(h.min()), 2), "max": round(float(h.max()), 2)}
        a["scripted_grave_ticks_mean"] = round(a["scripted_grave_ticks_mean"] / a["worlds"], 1)
    return {"w_N": W_N, "w_E": W_E, "s1_streak": CS.S1_STREAK, "seating": CS.SEATING, "arms": arms,
            "worlds": sum(a["worlds"] for a in arms.values()), "aborts": aborts,
            "covered_cat_ticks": sum(a["covered_cat_ticks"] for a in arms.values()),
            "s1_held": all(a["worst_covered_streak"] < CS.S1_STREAK for a in arms.values()) and not aborts,
            "worst_covered_streak": worst["covered"], "worst_scripted_streak": worst["scripted"]}


def md(r):
    lines = ["| arm | worlds | ticks | covered cat-ticks | covered mean happiness over worlds (mean / min / max) | worst covered streak | worlds with covered distress / grave | scripted friend: worst streak, mean grave ticks |",
             "|---|---|---|---|---|---|---|---|"]
    for arm in ("T", "E", "N"):
        a = r["arms"][arm]
        h = a["covered_mean_happiness"]
        lines.append(f"| {arm} | {a['worlds']} | {a['ticks_per_world']:,} | {a['covered_cat_ticks']:,} | {h['mean']:.2f} / {h['min']:.2f} / {h['max']:.2f} | "
                     f"{a['worst_covered_streak']} | {a['worlds_with_covered_distress']} / {a['worlds_with_covered_grave']} | {a['scripted_worst_streak']}, {a['scripted_grave_ticks_mean']} |")
    lines.append(f"\nworlds {r['worlds']}, covered cat-ticks {r['covered_cat_ticks']:,}, aborts {len(r['aborts'])}, S1 held: {r['s1_held']}; "
                 f"worst covered streak {r['worst_covered_streak'][0]} ({r['worst_covered_streak'][1]}); "
                 f"worst scripted streak {r['worst_scripted_streak'][0]} ({r['worst_scripted_streak'][1]})")
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "plan", "read"])
    ap.add_argument("--out")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    if a.cmd == "plan":
        print(json.dumps(plan(), indent=1))
    elif a.cmd == "read":
        r = read()
        if a.out:
            Path(a.out).write_text(json.dumps(r, indent=1) + "\n")
        print(md(r) if a.md else json.dumps(r, indent=1))
    else:
        run()
