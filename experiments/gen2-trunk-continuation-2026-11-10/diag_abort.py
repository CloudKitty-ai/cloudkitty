#!/usr/bin/env python3
"""Diagnosis of the continuation's two F-053 aborts at 40×40 (deviations entry 31; her question 2026-11-14: "what is
the cause of the distress? Vision radius solvable eat? Deadlock?"). One replay per world from the leg's recorded acts
(`replay.replay`: the actions are the record's, nothing covered decides). Per world:
  streaks   each seat's longest run of its own engine distress flags (the v6 self block), with its span
  window    over the ticks every streak seat shares: eat need, eat-legal ticks, moves legal / proposed, partnered share,
            chow in sight / in element memory, where the seat stood; the last tick each seat saw chow
  bowls     at sampled ticks of the window: the bowl count and each seat's straight-line and walking (Manhattan)
            distance to the nearest bowl, off the engine snapshot (the vision radius at 40×40 is 5)
  search    over the whole world: cat-ticks with no chow in sight or memory, and among them with eat need >= 50 and
            >= 90 — how often a move was legal, how often a move was proposed when legal, the partnered share
The no-head arm's leg on the same world is read beside as the contrast.
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B diag_abort.py --out reads/diag-abort.json     (about a minute)
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P2 = HERE.parent / "minifriend-phase2-2026-11-06"
sys.path.insert(0, str(P2))
import diag_nohead_s1 as G  # noqa: E402  (the v6 layout names, the menu, longest_run)
import p2_common as C  # noqa: E402
import replay as RP  # noqa: E402

L, SIZE = G.L, 40
EAT_NEED, CHOW = L.NEED_KINDS.index("eat"), L.ELEMENT_KINDS.index("chow")
WORLDS = [("cont-s1 final", "cont-s1", "legs", HERE / "results-raw", 905007),
          ("cont-s1 at 12M", "r6-cont-s1-u3906", "scouts", HERE / "results-raw", 905002),
          ("no-head s1 final", "p2u-nohead-s1", "legs", None, 905007)]


def world(seating, sub, root, seed, samples=6):
    acts = (root or C.RAW) / "legs" / seating / sub / f"size{SIZE}" / "acts" / f"acts-{seed}.npz"
    obs, mask, act, pos, snaps = [], [], [], [], []
    for rec in RP.replay(acts, C.LEG_TOML[SIZE], want_obs=True, want_snapshot=True):
        obs.append(rec["obs"]); mask.append(rec["mask"]); act.append(rec["acts"][:, 0]); pos.append(rec["pre"][2] * SIZE); snaps.append(rec["snapshot_pre"])
    obs, mask, act, pos = np.stack(obs), np.stack(mask)[:, :, :G.N_ACT], np.stack(act), np.stack(pos)
    T, R = act.shape
    flags = obs[:, :, L.SELF_DISTRESS:L.SELF_DISTRESS + 6] > 0.5
    eat = obs[:, :, L.SELF_NEEDS + EAT_NEED] * 100
    mem = obs[:, :, L.SELF_MEMORY:L.SELF_MEMORY + len(L.ELEMENT_KINDS) * L.MEMORY_SLOT].reshape(T, R, len(L.ELEMENT_KINDS), L.MEMORY_SLOT)[:, :, CHOW, 0] > 0.5
    vis = obs[:, :, L.BLOCKS[4][0]:L.BLOCKS[5][0] + L.BLOCKS[5][1]].reshape(T, R, 2, 6)[:, :, :, L.SLOT_PRESENT].max(2) > 0.5
    part = obs[:, :, L.SELF_PARTNERED] > 0.5
    mv_legal, mv = mask[:, :, :4].any(2), act < 4
    out = {"ticks": T, "streaks": {}}
    for k in range(R):
        best, end = G.longest_run(flags[:, k].any(1))
        out["streaks"][str(k)] = {"length": int(best), "span": [int(end - best + 1), int(end)] if best else None,
                                  "eat_flag_share": round(float(flags[end - best + 1:end + 1, k, EAT_NEED].mean()), 3) if best else None}
    seats = [k for k in range(R) if out["streaks"][str(k)]["length"] >= 300]
    if seats:
        lo, hi = max(out["streaks"][str(k)]["span"][0] for k in seats), min(out["streaks"][str(k)]["span"][1] for k in seats)
        w = slice(lo, hi + 1)
        out["window"] = {"span": [lo, hi], "seats": {str(k): {
            "eat_need_mean": round(float(eat[w, k].mean()), 1), "eat_legal_ticks": int(mask[w, k, G.EAT].sum()),
            "move_legal_share": round(float(mv_legal[w, k].mean()), 3), "moves_proposed": int(mv[w, k].sum()), "partnered_share": round(float(part[w, k].mean()), 3),
            "chow_in_sight_share": round(float(vis[w, k].mean()), 3), "chow_in_memory_share": round(float(mem[w, k].mean()), 3),
            "last_tick_chow_in_sight": int(np.nonzero(vis[:hi + 1, k])[0].max()) if vis[:hi + 1, k].any() else None,
            "pos_mean": [round(float(x), 1) for x in pos[w, k].mean(0)], "pos_range": [round(float(x), 1) for x in pos[w, k].max(0) - pos[w, k].min(0)]} for k in seats}}
        out["bowls"] = []
        for t in np.linspace(lo, hi, samples).astype(int).tolist():
            xy = np.asarray([(e["pos"]["x"], e["pos"]["y"]) for e in json.loads(bytes(snaps[t]) if not isinstance(snaps[t], (str, bytes)) else snaps[t])["world"]["elements"] if e["kind"] == "chow"], float)
            d, m = np.sqrt(((pos[t][seats][:, None] - xy[None]) ** 2).sum(-1)).min(1), np.abs(pos[t][seats][:, None] - xy[None]).sum(-1).min(1)
            out["bowls"].append({"tick": t, "bowls": len(xy), "nearest_straight": [round(float(x), 1) for x in d], "nearest_walk": [int(x) for x in m]})
    foodless = ~mem & ~vis
    out["search"] = {}
    for lab, cond in (("foodless", foodless), ("foodless_eat50", foodless & (eat >= 50)), ("foodless_eat90", foodless & (eat >= 90))):
        free = cond & mv_legal
        out["search"][lab] = {"cat_ticks": int(cond.sum()), "move_legal_share": round(float(free.sum() / cond.sum()), 3) if cond.any() else None,
                              "move_proposed_when_legal": round(float(mv[free].mean()), 3) if free.any() else None,
                              "partnered_share": round(float(part[cond].mean()), 3) if cond.any() else None}
    out["longest_foodless_run"] = [int(G.longest_run(foodless[:, k])[0]) for k in range(R)]
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    out = {name: {"seating": seating, "seed": seed} | world(seating, sub, root, seed) for name, seating, sub, root, seed in WORLDS}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    for name, v in out.items():
        print(name, {k: s["length"] for k, s in v["streaks"].items()}, v.get("window", {}).get("span"), [b["nearest_straight"] for b in v.get("bowls", [])][:2], v["search"]["foodless_eat50"], v["longest_foodless_run"])
