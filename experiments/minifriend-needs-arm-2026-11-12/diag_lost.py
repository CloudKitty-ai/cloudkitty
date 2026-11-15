#!/usr/bin/env python3
"""Diagnosis of the needs scout's long streaks (deviations entry 36; her words 2026-11-14: "Let's dig in on the eat
and cuddle failure cases we saw, likely causes and possible solutions", then "Run the replay reads"). One replay per
world from the leg's recorded acts (`replay.replay`: the actions are the record's, nothing covered decides), the
no-head arm's leg on the same world beside it. A diagnostic read with no guard of its own; its one self-check is a
printed number (`stamp_check`), never an assert. Per world:
  streaks   each seat's longest run of any own distress flag; for runs >= 300: the need, the span, company, what was
            legal / proposed / refused, the walk to the nearest bowl (snapshots every 50 ticks)
  closing   every moved tick of a LONELY cat (cuddle >= 50, unpartnered, no friend in sight): the nearest HEARD friend
            (a row whose present cell is 0 and whose spatial group is set: the stamp of that friend's last call inside
            the 30-tick digest window, docs/encodings.md), the walk to that stamp, the stamp's age, how far the friend
            has since walked from it, and whether the move closed on the stamp
  runs      each maximal lonely run of 50+ ticks: length, net displacement over moves made (straightness)
  rescue    while a cat is LOST (lonely with cuddle >= 90): every unpartnered friend's moved tick — whether it hears
            the lost cat and whether the move closed on it
  drink     drink proposals against the cat's own thirst, by whether any own distress flag is up; inside the long
            streaks the free-choice ticks (more than one legal act): what was legal and what was chosen
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B diag_lost.py --out reads/diag-lost.json [--md]     (about 4 minutes)
(A = experiments/minifriend-phase2-2026-11-06.)
"""
import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P2 = HERE.parent / "minifriend-phase2-2026-11-06"
sys.path.insert(0, str(P2))
import diag_nohead_s1 as G  # noqa: E402  (the v6 layout names, the menu, longest_run)
import p2_common as C  # noqa: E402
import replay as RP  # noqa: E402

L, MENU, N_ACT = G.L, G.MENU, G.N_ACT
NEEDS = L.NEED_KINDS
CUD, EAT_N, DRINK_N = NEEDS.index("cuddle"), NEEDS.index("eat"), NEEDS.index("drink")
DRINK = MENU.index("drink")
PARTNER_ACTS = [i for i, a in enumerate(MENU) if a.startswith(("rest_with", "sleep_with", "groom_kitty"))]
VISION = {40: 5, 100: 6}
DIGEST = 30
WORLDS = {40: (905012, 905004, 905030), 100: (905001, 905002, 905003)}
JOBS = [(arm, seating, sub if size == 100 else "legs", size, seed)
        for arm, seating, sub in (("needs", "p2u-needs-s1", "scouts"), ("nohead", "p2u-nohead-s1", "legs"))
        for size in (40, 100) for seed in WORLDS[size]]
D_BINS, AGE_BINS, ERR_BINS = (0, 10, 20, 40, 70, 1e9), (0, 10, 20, 31), (0, 2, 6, 1e9)


def r(x, n=3):
    return round(float(x), n)


def l1(a, b):
    return np.abs(a - b).sum(-1)


def world(job):
    arm, seating, sub, size, seed = job
    acts_p = C.RAW / "legs" / seating / sub / f"size{size}" / "acts" / f"acts-{seed}.npz"
    need, pos, part, flag, act, mask, row, spoke, refused, water, chow = [], [], [], [], [], [], [], [], [], [], {}
    for rec in RP.replay(acts_p, C.LEG_TOML[size], want_obs=True):
        p, o = rec["pre"], rec["obs"]
        need.append(p[0]); pos.append(p[2] * size); part.append(p[4]); flag.append(p[6])
        act.append(rec["acts"][:, 0]); mask.append(rec["mask"][:, :N_ACT])
        row.append(np.stack([o[:, L.BLOCKS[i][0]:L.BLOCKS[i][0] + 5] for i in range(4)], 1))
        water.append(o[:, L.SELF_IN_WATER] > 0.5)
        recs = [rec["recs"][n] for n in rec["names"]]
        spoke.append([v["applied_message"] is not None for v in recs])
        refused.append([v["proposed_action_name"] != v["applied_action_name"] for v in recs])
        if rec["tick"] % 50 == 0:
            snap = rec["env"].snapshot()
            snap = json.loads(bytes(snap) if not isinstance(snap, (str, bytes)) else snap)
            chow[rec["tick"] + 1] = np.asarray([(e["pos"]["x"], e["pos"]["y"]) for e in snap["world"]["elements"] if e["kind"] == "chow"], float)
    need, pos, part, flag, act, mask, row, spoke, refused, water = map(np.asarray, (need, pos, part, flag, act, mask, row, spoke, refused, water))
    T, R = act.shape
    others = [[j for j in range(R) if j != k] for k in range(R)]
    vr = VISION[size]
    seen = row[..., 0] > 0.5                                                    # (T, R, 4)
    heard = ~seen & (np.abs(row[..., 1:5]).sum(-1) > 1e-6)
    tgt = pos[:, :, None, :] + row[..., 1:3] * np.expm1(row[..., 4] * np.log1p(400.0))[..., None]      # the row's place, absolute
    last_t, last_p, cur_t, cur_p = np.full((T, R), -10 ** 6), np.zeros((T, R, 2)), np.full(R, -10 ** 6), np.zeros((R, 2))
    for t in range(T):
        last_t[t], last_p[t] = cur_t, cur_p
        cur_t, cur_p = np.where(spoke[t], t, cur_t), np.where(spoke[t][:, None], pos[t], cur_p)
    age = np.arange(T)[:, None] - last_t                                        # ticks since the friend's last call
    dist = l1(pos[:, :, None, :], pos[:, None, :, :]).astype(float)
    dist[:, np.arange(R), np.arange(R)] = np.inf
    near = dist.min(2)
    cud = need[:, :, CUD]
    lonely = (cud >= 50) & ~part & ~seen.any(2)
    moved = np.zeros((T, R), bool)
    moved[:-1] = (pos[1:] != pos[:-1]).any(2)
    anyflag = flag.any(2)
    in_streak = np.zeros((T, R), bool)
    out = {"arm": arm, "size": size, "seed": seed, "ticks": T, "seats": {}}

    # streaks
    for k in range(R):
        best, end = G.longest_run(anyflag[:, k])
        s = {"streak": int(best)}
        if best >= 300:
            w = slice(end - best + 1, end + 1)
            in_streak[w, k] = True
            n = int(flag[w, k].mean(0).argmax())
            legal = mask[w, k][:, PARTNER_ACTS].any(1)
            prop = np.isin(act[w, k], PARTNER_ACTS)
            free = mask[w, k].sum(1) > 1
            ticks = [t for t in chow if w.start <= t <= end and len(chow[t])]
            s |= {"need": NEEDS[n], "span": [w.start, end], "flag_share": {NEEDS[i]: r(flag[w, k, i].mean()) for i in range(6) if flag[w, k, i].any()},
                  "needs_mean": {NEEDS[i]: r(need[w, k, i].mean(), 1) for i in range(6)},
                  "nearest_friend_mean": r(near[w, k].mean(), 1), "friend_in_sight": r(seen[w, k].any(1).mean()), "friend_heard": r(heard[w, k].any(1).mean()),
                  "partner_act_legal": r(legal.mean()), "partner_act_proposed_when_legal": r(prop[legal].mean()) if legal.any() else None,
                  "refused_when_proposed": r(refused[w, k][prop].mean()) if prop.any() else None,
                  "moved": r(moved[w, k].mean()), "pos_range": [r(x, 1) for x in pos[w, k].max(0) - pos[w, k].min(0)],
                  "on_water": r(water[w, k].mean()), "free_ticks": int(free.sum()),
                  "free_legal": {"move": r(mask[w, k][free][:, :4].any(1).mean()), "drink": r(mask[w, k][free][:, DRINK].mean()), "eat": r(mask[w, k][free][:, G.EAT].mean())} if free.any() else None,
                  "free_chosen": {MENU[i]: int(c) for i, c in sorted(zip(*np.unique(act[w, k][free], return_counts=True)), key=lambda x: -x[1])[:5]},
                  "nearest_bowl_walk": {"mean": r(np.mean([l1(pos[min(t, T - 1), k], chow[t]).min() for t in ticks]), 1),
                                        "range": [r(f([l1(pos[min(t, T - 1), k], chow[t]).min() for t in ticks]), 1) for f in (min, max)]} if ticks else None}
        out["seats"][str(k)] = s

    # closing: rows [seat, tick, walk to the nearest stamp, its age, the friend's walk from it, closed, friends heard, in a long streak, the friend]
    rows, check = [], []
    for k in range(R):
        for t in np.nonzero(lonely[:, k] & moved[:, k] & heard[:, k].any(1))[0]:
            d = np.where(heard[t, k], l1(tgt[t, k], pos[t, k]), np.inf)
            i = int(d.argmin())
            j = others[k][i]
            rows.append((k, t, d[i], age[t, j], l1(tgt[t, k, i], pos[t, j]), l1(pos[t + 1, k], tgt[t, k, i]) < d[i] - 1e-6, heard[t, k].sum(), in_streak[t, k], j))
            check.append(l1(tgt[t, k, i], last_p[t, j]) <= 1.0)
    out["closing_rows"] = np.asarray(rows, float).reshape(-1, 9).tolist()
    out["stamp_check"] = {"rows": len(check), "row_place_is_the_last_call_place": r(np.mean(check)) if check else None,
                          "lonely_ticks": int(lonely.sum()), "lonely_no_friend_heard": r((lonely & ~heard.any(2)).mean() / max(lonely.mean(), 1e-12)),
                          "lonely_free_move_proposed": r((act[lonely & mask[:, :, :4].any(2)] < 4).mean()) if lonely.any() else None}

    # runs
    out["runs"] = []
    for k in range(R):
        on, t = lonely[:, k], 0
        while t < T:
            if on[t]:
                e = t
                while e + 1 < T and on[e + 1]:
                    e += 1
                if e - t + 1 >= 50:
                    m = int(moved[t:e + 1, k].sum())
                    out["runs"].append([e - t + 1, m, r(l1(pos[e, k], pos[t, k]) / m) if m else None])
                t = e + 1
            else:
                t += 1

    # rescue: rows [the friend hears the lost cat, its move closed on the lost cat, the friend's own worst need]
    res = []
    lost = lonely & (cud >= 90)
    for k in range(R):
        for t in np.nonzero(lost[:-1, k])[0]:
            for j in others[k]:
                if moved[t, j] and not part[t, j]:
                    res.append((heard[t, j, others[j].index(k)], l1(pos[t + 1, j], pos[t, k]) < dist[t, j, k], need[t, j].max()))
    res = np.asarray(res, float).reshape(-1, 3)
    out["rescue"] = {"friend_moves": len(res), "hears_the_lost_cat": r(res[:, 0].mean()) if len(res) else None,
                     "closed_when_hearing": [r(res[res[:, 0] > 0, 1].mean()), int((res[:, 0] > 0).sum())] if (res[:, 0] > 0).any() else None,
                     "closed_when_content": [r(res[(res[:, 0] > 0) & (res[:, 2] < 50), 1].mean()), int(((res[:, 0] > 0) & (res[:, 2] < 50)).sum())] if ((res[:, 0] > 0) & (res[:, 2] < 50)).any() else None,
                     "lost_cat_ticks": int(lost.sum())}

    # drink
    free, dr, thirst = mask.sum(2) > 1, act == DRINK, need[:, :, DRINK_N]
    quench = free & (thirst < 10) & mask[:, :, DRINK]
    out["drink"] = {"proposed_share": r(dr.mean()), "proposed_with_thirst_under_10": r((dr & (thirst < 10)).sum() / max(dr.sum(), 1)),
                    "idle_drink_rate_no_flag": [r(dr[quench & ~anyflag].mean()), int((quench & ~anyflag).sum())] if (quench & ~anyflag).any() else None,
                    "idle_drink_rate_flagged": [r(dr[quench & anyflag].mean()), int((quench & anyflag).sum())] if (quench & anyflag).any() else None}
    return out


def table(rows, col, bins):
    out = {}
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (rows[:, col] >= lo) & (rows[:, col] < hi)
        out[f"{int(lo)}+" if hi > 1e8 else f"{int(lo)}-{int(hi)}"] = [r(rows[m, 5].mean()), int(m.sum())] if m.any() else None
    return out


def pool(res):
    out = {}
    for arm in ("needs", "nohead"):
        for size in (40, 100):
            ws = [o for o in res if o["arm"] == arm and o["size"] == size]
            rows = np.asarray([x for o in ws for x in o["closing_rows"]], float).reshape(-1, 9)
            runs = [x for o in ws for x in o["runs"]]
            st = [x[2] for x in runs if x[2] is not None]
            same = [a[8] == b[8] for o in ws for a, b in zip(o["closing_rows"][:-1], o["closing_rows"][1:]) if a[0] == b[0] and b[1] - a[1] <= 3]
            out[f"{arm}/{size}"] = {
                "moves": len(rows), "closed": r(rows[:, 5].mean()) if len(rows) else None,
                "closed_in_long_streaks": [r(rows[rows[:, 7] > 0, 5].mean()), int((rows[:, 7] > 0).sum())] if (rows[:, 7] > 0).any() else None,
                "by_walk_to_stamp": table(rows, 2, D_BINS), "by_stamp_age": table(rows, 3, AGE_BINS), "by_friend_walk_from_stamp": table(rows, 4, ERR_BINS),
                "by_friends_heard": {str(n): [r(rows[rows[:, 6] == n, 5].mean()), int((rows[:, 6] == n).sum())] for n in (1, 2, 3, 4) if (rows[:, 6] == n).any()},
                "friend_walk_from_stamp_median": r(np.median(rows[:, 4]), 1) if len(rows) else None, "stamp_age_median": r(np.median(rows[:, 3]), 1) if len(rows) else None,
                "same_target_next_move": r(np.mean(same)) if same else None,
                "runs_50plus": len(runs), "run_length_median_max": [r(np.median([x[0] for x in runs]), 0), int(max(x[0] for x in runs))] if runs else None,
                "straightness_median": r(np.median(st)) if st else None,
                "rescue": {k: [o["rescue"][k] for o in ws] for k in ("hears_the_lost_cat", "closed_when_hearing", "closed_when_content", "lost_cat_ticks")},
                "drink": {k: [o["drink"][k] for o in ws] for k in ws[0]["drink"]},
                "stamp_check": [o["stamp_check"] for o in ws]}
    return out


def md(out):
    f = lambda v: "—" if v is None else f"{v[0]:.3f} ({v[1]})"
    Lm = ["# The lost-cat and drink reads (replays of recorded legs; needs scout seed 1 beside the no-head arm, same worlds)", "",
          "Closing = the share of a lonely cat's moves that shorten its walk to the nearest heard friend's call place (moves in brackets).", "",
          "| arm / size | all | in long streaks | walk 0-10 | 10-20 | 20-40 | 40-70 | 70+ | call age 0-10 | 10-20 | 20-30 | friend walked 0-2 | 2-6 | 6+ | same target next move | straightness |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, v in out["pooled"].items():
        Lm.append(f"| {name} | {v['closed']:.3f} ({v['moves']}) | {f(v['closed_in_long_streaks'])} | " + " | ".join(f(x) for x in v["by_walk_to_stamp"].values()) + " | "
                  + " | ".join(f(x) for x in v["by_stamp_age"].values()) + " | " + " | ".join(f(x) for x in v["by_friend_walk_from_stamp"].values())
                  + f" | {v['same_target_next_move']} | {v['straightness_median']} |")
    Lm += ["", "| arm / size | friends hearing a lost cat | their moves closing on it | of content friends | idle drink rate, no flag | flagged |", "|---|---|---|---|---|---|"]
    for name, v in out["pooled"].items():
        Lm.append(f"| {name} | {v['rescue']['hears_the_lost_cat']} | {v['rescue']['closed_when_hearing']} | {v['rescue']['closed_when_content']} | "
                  f"{v['drink']['idle_drink_rate_no_flag']} | {v['drink']['idle_drink_rate_flagged']} |")
    Lm += ["", "Streaks of 300+ ticks:", "", "| arm / size / world / seat | need | length | nearest friend | in sight | heard | cuddle act legal | proposed when legal | refused | moved | on water | free ticks: chosen | bowl walk |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for o in out["worlds"]:
        for k, s in o["seats"].items():
            if s["streak"] >= 300:
                Lm.append(f"| {o['arm']} / {o['size']} / {o['seed']} / {k} | {s['need']} | {s['streak']} | {s['nearest_friend_mean']} | {s['friend_in_sight']} | {s['friend_heard']} | {s['partner_act_legal']} | "
                          f"{s['partner_act_proposed_when_legal']} | {s['refused_when_proposed']} | {s['moved']} | {s['on_water']} | {s['free_ticks']}: {s['free_chosen']} | {s['nearest_bowl_walk']} |")
    return "\n".join(Lm) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True); ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    with ProcessPoolExecutor(6) as ex:
        res = list(ex.map(world, JOBS))
    out = {"pooled": pool(res), "worlds": [{k: v for k, v in o.items() if k != "closing_rows"} for o in res]}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    if a.md:
        a.out.with_suffix(".md").write_text(md(out))
    print(json.dumps({k: {x: v[x] for x in ("moves", "closed", "closed_in_long_streaks", "same_target_next_move", "straightness_median")} for k, v in out["pooled"].items()}))
