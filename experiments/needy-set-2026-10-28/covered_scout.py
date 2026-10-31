#!/usr/bin/env python3
"""§11 step 4: the covered scout and the S2 read (DECLARATION.md §7
"Covered scout", "S2, harm, the covered scout"; owner "Go", 2026-10-31).

Worlds, in burn order (every one on rot2 less one network, seat k
scripted on its config behaviour, the four covered seats' observations
saved, S1 armed on the covered seats only, F-053's 1,000-tick line):

- arm T's first world per block: P's `g2leg-20-P<k>.toml`, seat k
  scripted (`teacher`), T<k>'s first evaluation seed, 4,000 ticks ->
  `results-raw/set/T<k>/streams-<seed>.npz` (counted in the set if clean);
- arm N pairs: the covered-scout band 1095701-1095710, 2 per block in
  block order, each seed twice: seat k `teacher` on the served
  g2leg-20.toml (the control), then seat k `needy` on `g2leg-20-N<k>.toml`
  (edge 4,500); 6,000 ticks -> `results-raw/covered/N<k>/streams-<seed>-{teacher,needy}.npz`;
- arm E pairs: the first two seeds of each E block (1096161-1096162, ...),
  each twice: seat k `teacher` on the served config from the default
  start, then `g2leg-20-E<k>-n60.toml`; 800 ticks ->
  `results-raw/covered/E<k>/streams-<seed>-{teacher,needy}.npz`.

Any covered abort (meta aborted_at set) saves what was collected, stops
the run and exits 3: the step stops and goes to her (§7 S2).

    covered_scout.py run                      # resumable; skips present worlds
    covered_scout.py read --out F [--md]      # S2's two reads and the price columns

The S2 read: per pair, the four covered seats' mean happiness (the
collector's post-step `hap`, 0-100) in the teacher world minus the needy
world, over the whole world (arm N 6,000 ticks, arm E 800) and, for arm
N, over the first episode's window [mask onset, release + 300) alone.
Pooled over the pairs (mean, SD, min, max per read). Rule per read, on
the pooled mean: under 1.0 launches; 1.0 to 4.4 launches on her word;
over 4.4 does not launch.
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

SERVED = HERE.parent / "gen2-comparator-legs-2026-10-14" / "g2leg-20.toml"
P_CONFIGS = HERE.parent / "minifriend-phase1b-2026-10-23"
RAW = HERE / "results-raw" / "covered"
RAW_SET = HERE / "results-raw" / "set"
SEATING = "g2-rot2"
S1_STREAK = 1000
BLOCKS = (1, 2, 3, 4, 5)
TICKS = {"T": 4000, "N": 6000, "E": 800}
N_PIN = 60
WINDOW_TAIL = 300          # §7 S2: the episode window runs to release + 300
S2_LOW, S2_HIGH = 1.0, 4.4  # §7 S2: under 1.0 launches; 1.0-4.4 her word; over 4.4 no launch
TEAM_BASELINE = 87.49      # rot2's team happiness, the scale the 4.4 (5%) is set on
COVERED_BAND = R.SPLIT["scout_bands"]["covered"]   # [1095701, 1095710]


def worlds():
    """[(arm, k, kind, config, seed, ticks, out)] in burn order."""
    out = []
    for k in BLOCKS:
        seed = R.arm_block("T", k)["seeds"][0]
        out.append(("T", k, "T", P_CONFIGS / f"g2leg-20-P{k}.toml", seed, TICKS["T"],
                    RAW_SET / f"T{k}" / f"streams-{seed}.npz"))
    for k in BLOCKS:
        for seed in (COVERED_BAND[0] + 2 * (k - 1), COVERED_BAND[0] + 2 * (k - 1) + 1):
            for kind, cfg in (("teacher", SERVED), ("needy", HERE / f"g2leg-20-N{k}.toml")):
                out.append(("N", k, kind, cfg, seed, TICKS["N"], RAW / f"N{k}" / f"streams-{seed}-{kind}.npz"))
    assert out[-1][4] == COVERED_BAND[1]
    for k in BLOCKS:
        for seed in R.arm_block("E", k)["seeds"][:2]:
            for kind, cfg in (("teacher", SERVED), ("needy", HERE / f"g2leg-20-E{k}-n{N_PIN}.toml")):
                out.append(("E", k, kind, cfg, seed, TICKS["E"], RAW / f"E{k}" / f"streams-{seed}-{kind}.npz"))
    return out


def covered_cat_ticks(ws):
    return {"arm_T_first_worlds": sum(t * 4 for a, *_r, t, _o in ws if a == "T"),
            "arm_N_pairs": sum(t * 4 for a, *_r, t, _o in ws if a == "N"),
            "arm_E_pairs": sum(t * 4 for a, *_r, t, _o in ws if a == "E")}


# ---- run ----------------------------------------------------------------

def run():
    import torch
    import seating_collect_g2 as C
    torch.set_num_threads(1)
    ws = worlds()
    t0 = time.time()
    for i, (arm, k, kind, cfg, seed, ticks, out) in enumerate(ws):
        if out.exists():
            print(f"[{i + 1}/{len(ws)}] {arm}{k} {kind} {seed}: present, skipped", flush=True)
            continue
        t1 = time.time()
        arrays, meta = C.collect(SEATING, seed, ticks, S1_STREAK, config=cfg, save_obs=True,
                                 scripted_seat=k - 1, abort_covered_only=True)
        out.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(out, meta=json.dumps(meta), **arrays)
        covered = [j for j, s in enumerate(meta["seats"]) if s != "scripted"]
        assert covered == [j for j in range(5) if j != k - 1] and meta["abort_seats"] == covered, meta["seats"]
        assert (meta["needy_seat"] == k - 1) == (kind == "needy"), (kind, meta["needy_seat"])
        hap = arrays["hap"][:, covered].mean()
        print(f"[{i + 1}/{len(ws)}] {arm}{k} {kind} {seed}: {meta['ticks']} ticks, covered mean happiness {hap:.2f}, "
              f"{time.time() - t1:.0f}s (total {time.time() - t0:.0f}s)", flush=True)
        if meta["aborted_at"] is not None:
            print(f"== ABORT: covered seat at the S1 line in {arm}{k} {kind} {seed} at tick {meta['aborted_at']}; "
                  f"the step stops here and goes to her (§7)", flush=True)
            sys.exit(3)
    print(f"== covered scout done: {len(ws)} worlds, {time.time() - t0:.0f}s", flush=True)


# ---- read ---------------------------------------------------------------

def load(path):
    w = R.load_world(path)
    assert w["meta"]["aborted_at"] is None, (path, w["meta"]["aborted_at"])
    return w


def same_until(wa, wb):
    """The first post-step index at which two worlds differ in any seat's
    needs, happiness, position or activity (their length if never)."""
    T = min(wa["ticks"], wb["ticks"])
    assert np.array_equal(wa["meta"]["seats"], wb["meta"]["seats"])
    diff = np.zeros(T, bool)
    for key in ("post_needs", "post_hap"):
        a, b = wa[key][:T], wb[key][:T]
        diff |= (a != b).reshape(T, -1).any(1)
    za, zb = np.load(wa["path"]), np.load(wb["path"])
    for key in ("pos", "activity"):
        diff |= (za[key][:T] != zb[key][:T]).reshape(T, -1).any(1)
    hit = np.flatnonzero(diff)
    return int(hit[0]) if len(hit) else T


def s2_class(drop):
    """§7 S2 on one read's pooled mean drop (teacher minus needy)."""
    if drop < S2_LOW:
        return "launches"
    if drop <= S2_HIGH:
        return "her word"
    return "no launch"


def covered_mean(w, lo=0, hi=None):
    cov = R.observers(w)
    assert len(cov) == 4 and w["needy_seat" if "needy_seat" in w else "ticks"] is not None
    return float(w["post_hap"][lo:hi, cov].mean())


def seat_price(w, lo=0, hi=None):
    """R8's price columns for the covered seats over [lo, hi): mean
    happiness, distress ticks (any need), grave ticks on the §4 truth, the
    worst single-need streak and its need; the scripted seat's worst streak."""
    cov = R.observers(w)
    hi = w["ticks"] if hi is None else hi
    streaks = R.longest_streaks(w["distress"][lo:hi])
    any_distress = (w["distress"][lo:hi, cov] != 0).sum(0)
    grave = (w["codes"][lo:hi][:, cov] == R.S.GRAVE).sum(0)
    return {"covered_seats": cov, "ticks": hi - lo, "mean_happiness_per_seat": w["post_hap"][lo:hi, cov].astype(np.float64).mean(0).round(2).tolist(),
            "distress_ticks_per_seat": any_distress.tolist(), "grave_ticks_per_seat": grave.tolist(),
            "worst_streak_per_seat": streaks[cov].max(1).tolist(),
            "worst_streak_need_per_seat": [R.NEED_NAMES[i] if streaks[k].max() > 0 else None for k, i in zip(cov, streaks[cov].argmax(1))],
            "worst_streak_covered": int(streaks[cov].max()), "scripted_seat_worst_streak": int(streaks[w["scripted"][0]].max()),
            "scripted_seat_grave_ticks": int((w["codes"][lo:hi, w["scripted"][0]] == R.S.GRAVE).sum())}


def pair_record(arm, k, seed):
    wt = load(RAW / f"{arm}{k}" / f"streams-{seed}-teacher.npz")
    wn = load(RAW / f"{arm}{k}" / f"streams-{seed}-needy.npz")
    assert wt["scripted"] == wn["scripted"] == [k - 1] and wn["needy_seat"] == k - 1
    rec = {"arm": arm, "block": k, "seed": seed, "ticks": wn["ticks"], "friend_seat": k - 1,
           "whole": {"teacher": covered_mean(wt), "needy": covered_mean(wn)},
           "price": {"teacher": seat_price(wt), "needy": seat_price(wn)}}
    rec["whole"]["drop"] = rec["whole"]["teacher"] - rec["whole"]["needy"]
    windows = R.mask_windows(wn)
    rec["first_window"] = None
    rec["window"] = None
    if arm == "N":
        rec["same_until"] = same_until(wt, wn)
        if windows:
            on, close, _o = windows[0]
            hi = min(close + WINDOW_TAIL, wn["ticks"])
            bits = int(wn["needy_mask"][on])
            rec["first_window"] = {"onset": on, "close": close, "read_lo": on, "read_hi": hi, "ticks": hi - on,
                                   "masked": [n for i, n in enumerate(R.NEED_NAMES) if (bits >> i) & 1]}
            rec["window"] = {"teacher": covered_mean(wt, on, hi), "needy": covered_mean(wn, on, hi)}
            rec["window"]["drop"] = rec["window"]["teacher"] - rec["window"]["needy"]
            rec["window"]["price"] = {"teacher": seat_price(wt, on, hi), "needy": seat_price(wn, on, hi)}
            rec["window"]["covered_seats_grave_in_window"] = int((np.asarray(rec["window"]["price"]["needy"]["grave_ticks_per_seat"]) > 0).sum())
    else:
        assert windows and windows[0][0] in (0, 1), windows[:1]
        rec["first_window"] = {"onset": windows[0][0], "close": windows[0][1]}
    return rec


def pooled(drops):
    a = np.asarray(drops, float)
    return {"n": len(a), "mean": float(a.mean()), "sd": float(a.std(ddof=1)) if len(a) > 1 else None,
            "min": float(a.min()), "max": float(a.max()), "s2": s2_class(float(a.mean()))}


def read():
    ws = worlds()
    out = {"seating": SEATING, "s1_streak_covered_only": S1_STREAK, "rule": "teacher minus needy, covered seats' mean happiness; "
           f"under {S2_LOW} launches; {S2_LOW}-{S2_HIGH} her word; over {S2_HIGH} no launch", "team_baseline": TEAM_BASELINE,
           "covered_cat_ticks": covered_cat_ticks(ws), "arm_T_first_worlds": [], "pairs": [], "reads": {}}
    for arm, k, kind, _cfg, seed, ticks, path in ws:
        if arm == "T":
            w = load(path)
            assert w["scripted"] == [k - 1] and "needy_seat" not in w
            out["arm_T_first_worlds"].append({"block": k, "seed": seed, "ticks": w["ticks"], "clean": w["meta"]["aborted_at"] is None,
                                              "covered_mean_happiness": covered_mean(w), "price": seat_price(w)})
    done = set()
    for arm, k, kind, _cfg, seed, ticks, path in ws:
        if arm != "T" and (arm, k, seed) not in done:
            done.add((arm, k, seed))
            out["pairs"].append(pair_record(arm, k, seed))
    n_pairs = [p for p in out["pairs"] if p["arm"] == "N"]
    e_pairs = [p for p in out["pairs"] if p["arm"] == "E"]
    out["reads"] = {"whole_world_N": pooled([p["whole"]["drop"] for p in n_pairs]),
                    "episode_window_N": pooled([p["window"]["drop"] for p in n_pairs if p["window"]]),
                    "whole_world_E": pooled([p["whole"]["drop"] for p in e_pairs])}
    out["reads"]["episode_window_N"]["pairs_without_a_first_window"] = sum(1 for p in n_pairs if not p["window"])
    out["same_until_ge_onset"] = all(p["same_until"] >= (p["first_window"]["onset"] if p["first_window"] else p["ticks"]) for p in n_pairs)
    out["aborts"] = 0
    out["worst_covered_streak"] = max([p["price"][s]["worst_streak_covered"] for p in out["pairs"] for s in ("teacher", "needy")]
                                      + [t["price"]["worst_streak_covered"] for t in out["arm_T_first_worlds"]])
    out["S2"] = {name: r["s2"] for name, r in out["reads"].items()}
    out["S2_launches"] = all(v == "launches" for v in out["S2"].values())
    return out


def md(out):
    lines = ["## Covered scout and S2 (§7; §11 step 4)", "",
             f"Covered cat-ticks: {out['covered_cat_ticks']}; S1 armed on the covered seats at {out['s1_streak_covered_only']}; aborts {out['aborts']}; "
             f"worst covered single-need streak {out['worst_covered_streak']}.", "",
             "| read | pairs | drop mean | SD | min | max | S2 |", "|---|---|---|---|---|---|---|"]
    for name, r in out["reads"].items():
        lines.append(f"| {name} | {r['n']} | {r['mean']:.3f} | {r['sd']:.3f} | {r['min']:.3f} | {r['max']:.3f} | {r['s2']} |")
    lines += ["", "| pair | seed | same until | first window (onset, close, read to) | whole: teacher / needy / drop | window: teacher / needy / drop | worst covered streak t / n |",
              "|---|---|---|---|---|---|---|"]
    for p in out["pairs"]:
        fw = p["first_window"]
        fws = f"{fw['onset']}, {fw['close']}, {fw.get('read_hi', '-')}" if fw else "none"
        win = f"{p['window']['teacher']:.2f} / {p['window']['needy']:.2f} / {p['window']['drop']:.3f}" if p["window"] else "-"
        lines.append(f"| {p['arm']}{p['block']} | {p['seed']} | {p.get('same_until', '-')} | {fws} | "
                     f"{p['whole']['teacher']:.2f} / {p['whole']['needy']:.2f} / {p['whole']['drop']:.3f} | {win} | "
                     f"{p['price']['teacher']['worst_streak_covered']} / {p['price']['needy']['worst_streak_covered']} |")
    lines += ["", "| arm N pair | masked at the first window | covered seats grave in the window (needy / teacher) | grave ticks per covered seat, needy | mean happiness per covered seat, needy | teacher |", "|---|---|---|---|---|---|"]
    for p in out["pairs"]:
        if p["arm"] == "N" and p["window"]:
            pn, pt = p["window"]["price"]["needy"], p["window"]["price"]["teacher"]
            lines.append(f"| N{p['block']} {p['seed']} | {', '.join(p['first_window']['masked'])} | {p['window']['covered_seats_grave_in_window']} / "
                         f"{int((np.asarray(pt['grave_ticks_per_seat']) > 0).sum())} | {pn['grave_ticks_per_seat']} | {pn['mean_happiness_per_seat']} | {pt['mean_happiness_per_seat']} |")
    lines += ["", "| world | seat | worst covered streak (need) | distress ticks per covered seat | grave ticks per covered seat |", "|---|---|---|---|---|"]
    for p in out["pairs"]:
        for kind in ("teacher", "needy"):
            pr = p["price"][kind]
            if pr["worst_streak_covered"] > 0:
                i = int(np.argmax(pr["worst_streak_per_seat"]))
                lines.append(f"| {p['arm']}{p['block']} {p['seed']} {kind} | {pr['covered_seats'][i]} | {pr['worst_streak_covered']} ({pr['worst_streak_need_per_seat'][i]}) | "
                             f"{pr['distress_ticks_per_seat']} | {pr['grave_ticks_per_seat']} |")
    lines += ["", "| arm T first world | seed | ticks | clean | covered mean happiness | worst covered streak |", "|---|---|---|---|---|---|"]
    for t in out["arm_T_first_worlds"]:
        lines.append(f"| T{t['block']} | {t['seed']} | {t['ticks']} | {t['clean']} | {t['covered_mean_happiness']:.2f} | {t['price']['worst_streak_covered']} |")
    lines += ["", f"S2: {out['S2']} -> {'the set launches' if out['S2_launches'] else 'to her'}.", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "read", "plan"])
    ap.add_argument("--out", type=Path)
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    if a.cmd == "plan":
        ws = worlds()
        for w in ws:
            print(w[0], w[1], w[2], w[3].name, w[4], w[5], w[6].relative_to(HERE))
        print(covered_cat_ticks(ws))
        return
    if a.cmd == "run":
        run()
        return
    out = read()
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(out, indent=1))
    print(md(out) if a.md else json.dumps({k: v for k, v in out.items() if k != "pairs"}, indent=1))


if __name__ == "__main__":
    main()
