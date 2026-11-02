#!/usr/bin/env python3
"""Phase 1e — the late-grave training set's collection (DECLARATION.md
§3; runs only after the declaration is ruled, on her word).

TN<k>: `g2leg-20-N<k>.toml` (the needy set's arm N config, byte for
byte), 6,000 ticks; TE<k>: `g2leg-20-E<k>-n60.toml` (arm E's at the
pinned n), 1,000 ticks. Each world is covered_scout's call, world for
world: `g2-rot2` less seat k's network, seat k scripted on its config
behaviour, every covered observation saved, S1 = F-053's 1,000-tick
single-need streak armed on the covered seats only; any covered abort
saves what was collected, exits 3, and goes to her. Seeds and counts
from split.json (split_1e.py). Resumable; burn order TE then TN.

    collect_1e.py plan          # worlds, present, covered cat-ticks
    collect_1e.py run
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
sys.path.insert(0, str(EXPTS / "needy-set-2026-10-28"))
sys.path.insert(0, str(EXPTS / "seating-analysis-g2-2026-10-21"))
import covered_scout as CS  # noqa: E402  (SEATING, S1_STREAK; the needy set's collector call)

SPLIT = json.loads((HERE / "split.json").read_text())
SETS = [n for n in SPLIT["sets"] if n.startswith("TE")] + [n for n in SPLIT["sets"] if n.startswith("TN")]


def worlds():
    """[(set, seed, config, ticks, scripted_seat, out)] in burn order."""
    out = []
    for name in SETS:
        s = SPLIT["sets"][name]
        for seed in s["train"]:
            out.append((name, seed, EXPTS / s["config"], s["ticks"], s["scripted_seat"], EXPTS / s["raw_dir"] / f"streams-{seed}.npz"))
    return out


def plan():
    ws = worlds()
    by = {}
    for name, _seed, _cfg, ticks, _scr, out in ws:
        a = by.setdefault(name[:2], {"worlds": 0, "present": 0, "ticks": ticks, "covered_cat_ticks": 0})
        a["worlds"] += 1
        a["present"] += out.exists()
        a["covered_cat_ticks"] += 4 * ticks
    return {"seating": CS.SEATING, "s1_streak_covered_only": CS.S1_STREAK, "kinds": by, "worlds": len(ws),
            "covered_cat_ticks_total": sum(a["covered_cat_ticks"] for a in by.values()),
            "covered_cat_ticks_remaining": sum(4 * t for _n, _s, _c, t, _k, o in ws if not o.exists())}


def run():
    import torch
    import seating_collect_g2 as C
    torch.set_num_threads(1)
    ws = worlds()
    t0 = time.time()
    for i, (name, seed, cfg, ticks, scr, out) in enumerate(ws):
        if out.exists():
            print(f"[{i + 1}/{len(ws)}] {name} {seed}: present, skipped", flush=True)
            continue
        t1 = time.time()
        arrays, meta = C.collect(CS.SEATING, seed, ticks, CS.S1_STREAK, config=cfg, save_obs=True,
                                 scripted_seat=scr, abort_covered_only=True)
        out.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(out, meta=json.dumps(meta), **arrays)
        covered = [j for j, s in enumerate(meta["seats"]) if s != "scripted"]
        assert covered == [j for j in range(5) if j != scr] and meta["abort_seats"] == covered, meta["seats"]
        assert meta["needy_seat"] == scr, (name, meta["needy_seat"])
        hap = arrays["hap"][:, covered].mean()
        print(f"[{i + 1}/{len(ws)}] {name} {seed}: {meta['ticks']} ticks, covered mean happiness {hap:.2f}, "
              f"{time.time() - t1:.0f}s (total {time.time() - t0:.0f}s)", flush=True)
        if meta["aborted_at"] is not None:
            print(f"== ABORT: covered seat at the S1 line in {name} {seed} at tick {meta['aborted_at']}; "
                  f"the collection stops here and goes to her (DECLARATION §10)", flush=True)
            sys.exit(3)
    print(f"== training set done: {len(ws)} worlds, {time.time() - t0:.0f}s", flush=True)


def read():
    """The run record (DECLARATION §11 step 3), per kind: worlds and covered
    cat-ticks burned, the covered seats' mean happiness over worlds, S1's
    worst covered single-need streak (under the line in every world), the
    scripted friend's grave ticks and episodes; aborts listed."""
    import needy_read as R
    kinds, aborts = {}, []
    worst = (0, None)
    for name, seed, _cfg, ticks, scr, out in worlds():
        meta = json.loads(str(np.load(out, allow_pickle=True)["meta"]))
        if meta["aborted_at"] is not None:
            aborts.append((name, seed, meta["aborted_at"]))
            continue
        w = R.load_world(out)
        cov = [j for j in range(5) if j != scr]
        assert meta["scripted_seat"] == scr and w["ticks"] == ticks and w["scripted"] == [scr], (name, seed)
        streaks = R.longest_streaks(w["distress"])
        cs = int(streaks[cov].max())
        a = kinds.setdefault(name[:2], {"worlds": 0, "ticks_per_world": ticks, "covered_cat_ticks": 0, "covered_mean_happiness": [],
                                       "worst_covered_streak": 0, "worlds_with_covered_grave": 0, "scripted_grave_ticks": [],
                                       "scripted_grave_episodes": [], "first_crossing": []})
        a["worlds"] += 1
        a["covered_cat_ticks"] += 4 * ticks
        a["covered_mean_happiness"].append(float(w["hap"][:, cov].mean()))
        a["worst_covered_streak"] = max(a["worst_covered_streak"], cs)
        a["worlds_with_covered_grave"] += bool((w["codes"][:, cov] == R.S.GRAVE).any())
        eps = R.grave_episodes(w["codes"][:, scr])
        a["scripted_grave_ticks"].append(int((w["codes"][:, scr] == R.S.GRAVE).sum()))
        a["scripted_grave_episodes"].append(len(eps))
        a["first_crossing"].append(eps[0][0] if eps else None)
        if cs > worst[0]:
            worst = (cs, f"{name} {seed}")
    for a in kinds.values():
        h = np.asarray(a["covered_mean_happiness"])
        a["covered_mean_happiness"] = {"mean": round(float(h.mean()), 2), "min": round(float(h.min()), 2), "max": round(float(h.max()), 2)}
        a["scripted_grave_ticks_mean"] = round(float(np.mean(a.pop("scripted_grave_ticks"))), 1)
        a["scripted_grave_episodes_total"] = int(sum(a.pop("scripted_grave_episodes")))
        fc = a.pop("first_crossing")
        a["first_crossing_strata"] = {s: sum(1 for c in fc if c is not None and R.stratum_of(c) == s) for s in R.STRATA}
        a["first_crossing_strata"]["none"] = sum(1 for c in fc if c is None)
    return {"seating": CS.SEATING, "s1_streak_covered_only": CS.S1_STREAK, "kinds": kinds, "aborts": aborts,
            "worlds": sum(a["worlds"] for a in kinds.values()), "covered_cat_ticks": sum(a["covered_cat_ticks"] for a in kinds.values()),
            "s1_held": all(a["worst_covered_streak"] < CS.S1_STREAK for a in kinds.values()) and not aborts,
            "worst_covered_streak": worst}


def md(r):
    lines = ["| kind | worlds | ticks | covered cat-ticks | covered mean happiness (mean / min / max) | worst covered streak | worlds with covered grave | scripted friend: mean grave ticks, episodes, first crossings by stratum |",
             "|---|---|---|---|---|---|---|---|"]
    for k in ("TE", "TN"):
        a = r["kinds"][k]
        h = a["covered_mean_happiness"]
        lines.append(f"| {k} | {a['worlds']} | {a['ticks_per_world']:,} | {a['covered_cat_ticks']:,} | {h['mean']:.2f} / {h['min']:.2f} / {h['max']:.2f} | "
                     f"{a['worst_covered_streak']} | {a['worlds_with_covered_grave']} | {a['scripted_grave_ticks_mean']}, {a['scripted_grave_episodes_total']}, {a['first_crossing_strata']} |")
    lines.append(f"\nworlds {r['worlds']}, covered cat-ticks {r['covered_cat_ticks']:,}, aborts {len(r['aborts'])}, S1 held: {r['s1_held']}; "
                 f"worst covered streak {r['worst_covered_streak'][0]} ({r['worst_covered_streak'][1]})")
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "run", "read"])
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
