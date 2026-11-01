#!/usr/bin/env python3
"""§11 step 6 — R4, the ladder (DECLARATION.md §5 R4; owner "Run step 6",
2026-11-01). Tuning seeds only: every world passes `refuse_unless(...,
"tuning")` before it loads (n6); nothing on a confirming seed is read
before her pick.

The grid: thresholds {0.05, 0.10, 0.20, 0.30, 0.50} x burn-ins {0, 2, 5,
10}. Per cell, on the scripted friend's FIRST episode of each world (§4:
later episodes are R7's), per primary stratum (H0 from arm T, H1 from arm
E, H2-H4 from arm N; every other (arm, stratum) cell printed apart, never
pooled): detection, latency, anticipation; and false alarms per class.
No rule. The pick is hers, with its price printed.

Definitions, all from §4 (R4d's where it says so):
- an observer slice is (covered observer k, friend j), the whole world;
  the alarm is P(grave) >= threshold with the slice's first B ticks forced
  off (R6d's burn-in); P(grave) is NF-h24+p's, three probe seeds, state
  zero at the world's start (needy_read.probe_world, n8);
- the friend's grave episode is a maximal GRAVE run on its truth aligned
  to the observation (obs[t] with needs[t - 1]); its first tick is the
  crossing; H = the crossing (the slice starts at tick 0); the stratum is
  H's (STRATA). Arm N / E: the first episode is the one whose crossing
  lies in the first mask window; a first window unreleased at the world's
  end enters no stratum (§3); a crossing outside every window is unmasked
  and counted apart. Arm T: the first episode is the reset episode
  (crossing at tick 0, H0); an arm T world not grave at tick 0 is counted
  apart;
- detection: the alarm is on at any tick of [crossing, end); latency is
  that first tick minus the crossing (0 = at the crossing);
- anticipation: an alarm run that STARTS inside [mask onset, crossing); a
  run that began before the onset and spans it is not one (it is a
  false alarm of its class if it touches no grave tick). Lead = crossing
  - the start of the first such run (§4's "first alarm tick at or after
  mask onset", read over anticipation runs). Beside it, the same with
  runs starting at the slice's first alarmable tick (offset B) left out,
  run by run: the next anticipation run, if any, counts. Arm T has no
  mask (no anticipation column);
- false alarms: alarm runs touching no grave tick of the slice's friend,
  anticipation runs excluded, per 10,000 observer-ticks of their class:
  the scripted friend before its first mask onset, the scripted friend
  from its first onset on ("between episodes"), and covered friends. Runs
  starting at the slice's first alarmable tick (offset B) are counted
  apart (R4d). The anticipation exclusion applies to every mask window of
  the scripted friend that holds a crossing, not only the first;
- every figure is the seed mean +- SD (ddof 1) over the three probe
  seeds, the episode counts (friend episodes, observer-episodes) beside it.

    ladder.py plan                       # the tuning worlds per arm and block
    ladder.py read --out F [--md]        # the ladder; about 30 s
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import needy_read as R  # noqa: E402
import set_run as SR  # noqa: E402

THRESHOLDS = (0.05, 0.10, 0.20, 0.30, 0.50)
BURNINS = (0, 2, 5, 10)
HALF = "tuning"
PRIMARY = {"H0": "T", "H1": "E", "H2": "N", "H3": "N", "H4": "N"}     # stratum -> the arm it is read from (§5 R4)
FA_CLASSES = ("scripted_before_first_mask", "scripted_from_first_mask", "covered_friends")


def cell_name(th, b):
    return f"t{th:.2f}-B{b}"


def worlds():
    """[(arm, k, seed, ticks, path)] — the set's tuning worlds in the set's
    burn order (set_run.worlds restricted by the split); each passes the
    gate before it is loaded."""
    out = []
    for arm, k, _cfg, seed, ticks, path in SR.worlds():
        if R.half_of(arm, k, seed) == HALF:
            out.append((arm, k, seed, ticks, path))
    return out


def plan():
    ws = worlds()
    by = {}
    for arm, k, seed, ticks, _p in ws:
        a = by.setdefault(arm, {"worlds": 0, "per_block": {}, "ticks": ticks})
        a["worlds"] += 1
        a["per_block"][str(k)] = a["per_block"].get(str(k), 0) + 1
    return {"half": HALF, "thresholds": THRESHOLDS, "burnins": BURNINS, "arms": by, "worlds": len(ws),
            "observer_slices": len(ws) * 16, "probe_seeds": R.PROBE_SEEDS}


# ---- one world -------------------------------------------------------------

def runs(mask):
    d = np.diff(np.concatenate([[0], mask.astype(np.int8), [0]]))
    return list(zip(np.where(d == 1)[0].tolist(), np.where(d == -1)[0].tolist()))


def first_episode(w, arm):
    """The scripted friend's first episode and its anchors, or the reason
    there is none: {'status', 'crossing', 'end', 'onset', 'stratum', 'm',
    'masked', 'edge', 'windows', 'episodes'}."""
    f = w["scripted"][0]
    codes = w["codes"][:, f]
    episodes = R.grave_episodes(codes)
    rec = {"friend": f, "episodes": episodes, "windows": [], "status": None, "crossing": None, "end": None,
           "onset": None, "stratum": None, "m": None, "masked": None, "edge": None}
    if arm == "T":
        if episodes and episodes[0][0] == 0:
            c, e = episodes[0]
            rec.update(status="H0", crossing=0, end=e, stratum="H0")
        else:
            rec["status"] = "T_not_grave_at_tick0"
        return rec
    windows = R.mask_windows(w)
    rec["windows"] = windows
    if not windows:
        rec["status"] = "no_onset"
        return rec
    on, close, _o = windows[0]
    bits = int(w["needy_mask"][on])
    rec["onset"] = on
    rec["masked"] = [n for i, n in enumerate(R.NEED_NAMES) if (bits >> i) & 1]
    rec["m"] = len(rec["masked"])
    inside = [(c, e) for (c, e) in episodes if R.window_of(c, windows) == 0]
    if close >= w["ticks"]:
        rec["status"] = "unreleased"          # §3: enters no stratum, crossing or not
        return rec
    if not inside:
        rec["status"] = "released_no_crossing"
        return rec
    c, e = inside[0]
    over = [n for n, v in zip(R.NEED_NAMES[:5], w["needs"][c, f, :5]) if v >= R.S.NEED_DISTRESS]
    rec.update(status=R.stratum_of(c), crossing=int(c), end=int(e), stratum=R.stratum_of(c), edge="need" if over else "happiness")
    return rec


def anticipation_windows(w, fe):
    """[(onset, crossing)) of every mask window of the scripted friend that
    holds a crossing: alarm runs starting inside are anticipation, never
    false alarms."""
    out = []
    for j, (on, _close, _o) in enumerate(fe["windows"]):
        inside = [c for (c, _e) in fe["episodes"] if R.window_of(c, fe["windows"]) == j]
        if inside:
            out.append((on, min(inside)))
    return out


def world_cells(w, arm, p_by_seed, fe):
    """Per probe seed and cell: the first episode's per-observer latency,
    anticipation lead and sight at the crossing; and the false-alarm runs
    per class (counts, plus runs starting at offset B)."""
    T = w["ticks"]
    f = fe["friend"]
    obs = R.observers(w)
    assert len(obs) == 4 and f not in obs
    grave_of = {j: (w["codes"][:, j] == R.S.GRAVE) for j in range(R.ROSTER)}
    antic = anticipation_windows(w, fe)
    first_onset = fe["windows"][0][0] if fe["windows"] else None
    vis = {k: R.pair_x(w, k, f)[1] for k in obs}
    out = {"sight_at_crossing": None, "cells": {}}
    if fe["crossing"] is not None:
        out["sight_at_crossing"] = {str(k): bool(vis[k][fe["crossing"]]) for k in obs}
    ticks = {"scripted_before_first_mask": 4 * (first_onset if first_onset is not None else 0),
             "scripted_from_first_mask": 4 * (T - first_onset) if first_onset is not None else 4 * T,
             "covered_friends": 12 * T}
    if arm == "T":
        ticks = {"scripted_before_first_mask": 0, "scripted_from_first_mask": 4 * T, "covered_friends": 12 * T}
    out["observer_ticks"] = ticks
    for s, P in p_by_seed.items():
        P = np.nan_to_num(P, nan=-1.0)                              # no pair runs there: under every threshold
        for th in THRESHOLDS:
            above_all = P >= th
            for b in BURNINS:
                above = above_all.copy()
                above[:b] = False                                   # R6d: the alarm forced off for the slice's first B ticks
                cell = {"latency": {}, "lead": {}, "lead_not_at_offset_B": {}, "fa": {c: 0 for c in FA_CLASSES},
                        "fa_at_offset_B": {c: 0 for c in FA_CLASSES}, "fa_run_ticks": {c: 0 for c in FA_CLASSES}}
                for k in obs:
                    for j in range(R.ROSTER):
                        if j == k:
                            continue
                        a = above[:, k, j]
                        if j == f:
                            rs = runs(a)
                            if fe["crossing"] is not None:
                                c, e = fe["crossing"], fe["end"]
                                hit = np.flatnonzero(a[c:e])
                                cell["latency"][str(k)] = int(hit[0]) if len(hit) else None
                                if fe["onset"] is not None:
                                    # anticipation runs: those STARTING inside [onset, crossing); lead from the first;
                                    # beside it the first one not starting at offset B (R4d's runs-at-reset, counted apart)
                                    starts = [st for st, _en in rs if fe["onset"] <= st < c]
                                    cell["lead"][str(k)] = int(c - starts[0]) if starts else None
                                    later = [st for st in starts if st != b]
                                    cell["lead_not_at_offset_B"][str(k)] = int(c - later[0]) if later else None
                            for st, en in rs:
                                if grave_of[j][st:en].any() or any(on <= st < c for on, c in antic):
                                    continue
                                cls = "scripted_before_first_mask" if first_onset is not None and st < first_onset else "scripted_from_first_mask"
                                cell["fa"][cls] += 1
                                cell["fa_run_ticks"][cls] += en - st
                                cell["fa_at_offset_B"][cls] += st == b
                        else:
                            for st, en in runs(a):
                                if grave_of[j][st:en].any():
                                    continue
                                cell["fa"]["covered_friends"] += 1
                                cell["fa_run_ticks"]["covered_friends"] += en - st
                                cell["fa_at_offset_B"]["covered_friends"] += st == b
                out["cells"].setdefault(str(s), {})[cell_name(th, b)] = cell
    return out


def world_record(arm, k, seed, ticks, path, probes):
    R.refuse_unless(arm, k, seed, HALF)
    w = R.load_world(path)
    assert w["meta"]["aborted_at"] is None and w["ticks"] == ticks and w["scripted"] == [k - 1], (arm, k, seed)
    fe = first_episode(w, arm)
    p_by_seed = {s: R.probe_world(m, p, w) for s, (m, p) in probes.items()}
    rec = {"arm": arm, "block": k, "seed": seed, "ticks": ticks, "friend": fe["friend"], "status": fe["status"],
           "crossing": fe["crossing"], "end": None if fe["crossing"] is None else fe["end"],
           "length": None if fe["crossing"] is None else fe["end"] - fe["crossing"],
           "onset": fe["onset"], "stratum": fe["stratum"], "m": fe["m"], "masked": fe["masked"], "edge": fe["edge"],
           "friend_episodes": len(fe["episodes"]), "mask_windows": len(fe["windows"]),
           "unmasked_crossings": sum(1 for (c, _e) in fe["episodes"] if fe["windows"] and R.window_of(c, fe["windows"]) is None)}
    rec.update(world_cells(w, arm, p_by_seed, fe))
    return rec


# ---- the ladder ---------------------------------------------------------------

def msd(xs):
    a = np.asarray([x for x in xs if x is not None], float)
    if len(a) == 0:
        return None
    return {"mean": round(float(a.mean()), 4), "sd": round(float(a.std(ddof=1)), 4) if len(a) > 1 else None, "n_seeds": len(a)}


def _median(xs):
    return float(np.median(xs)) if len(xs) else None


def stratum_cell(recs, cell, with_sight):
    """One (arm, stratum) group's figures for one cell: per probe seed over
    the observer-episodes, then mean +- SD over seeds."""
    per_seed = {}
    for s in map(str, R.PROBE_SEEDS):
        lats, leads, leads_later, lat_sight, lat_fog = [], [], [], [], []
        for r in recs:
            c = r["cells"][s][cell]
            for k, lat in c["latency"].items():
                lats.append(lat)
                (lat_sight if r["sight_at_crossing"][k] else lat_fog).append(lat)
            for k, lead in c["lead"].items():
                leads.append(lead)
                leads_later.append(c["lead_not_at_offset_B"][k])
        det = [l for l in lats if l is not None]
        row = {"detected": len(det) / len(lats) if lats else None,
               "median_latency": _median(det), "p90_latency": float(np.percentile(det, 90)) if det else None,
               "within_10": sum(l <= 10 for l in det) / len(lats) if lats else None}
        if with_sight:
            row["detected_in_sight"] = (sum(l is not None for l in lat_sight) / len(lat_sight)) if lat_sight else None
            row["detected_under_fog"] = (sum(l is not None for l in lat_fog) / len(lat_fog)) if lat_fog else None
            row["anticipated"] = sum(l is not None for l in leads) / len(leads) if leads else None
            row["median_lead_anticipated"] = _median([l for l in leads if l is not None])
            # the same with runs starting at the slice's first alarmable tick (offset B) left out, run by run
            row["anticipated_run_not_at_offset_B"] = sum(l is not None for l in leads_later) / len(leads_later) if leads_later else None
            row["median_lead_run_not_at_offset_B"] = _median([l for l in leads_later if l is not None])
        per_seed[s] = row
    keys = list(next(iter(per_seed.values())))
    out = {key: msd([per_seed[s][key] for s in per_seed]) for key in keys}
    out["per_seed"] = per_seed
    return out


def false_alarm_cell(recs, cell):
    """Per class: runs per 10,000 observer-ticks of the class (seed mean +-
    SD), the mean run length, and the share of runs starting at offset B."""
    out = {}
    for cls in FA_CLASSES:
        ticks = sum(r["observer_ticks"][cls] for r in recs)
        rates, lens, atb = [], [], []
        for s in map(str, R.PROBE_SEEDS):
            n = sum(r["cells"][s][cell]["fa"][cls] for r in recs)
            t = sum(r["cells"][s][cell]["fa_run_ticks"][cls] for r in recs)
            a = sum(r["cells"][s][cell]["fa_at_offset_B"][cls] for r in recs)
            rates.append(n / ticks * 1e4 if ticks else None)
            lens.append(t / n if n else None)
            atb.append(a / n if n else None)
        out[cls] = {"observer_ticks": ticks, "per_10k_ticks": msd(rates), "mean_run_length": msd(lens), "share_at_offset_B": msd(atb)}
    return out


def ladder(recs):
    groups = {}
    for r in recs:
        if r["stratum"] is not None:
            groups.setdefault((r["arm"], r["stratum"]), []).append(r)
    status = {}
    for r in recs:
        status.setdefault(r["arm"], {}).setdefault(r["status"], 0)
        status[r["arm"]][r["status"]] += 1
    cells = [cell_name(th, b) for th in THRESHOLDS for b in BURNINS]
    out = {"half": HALF, "thresholds": THRESHOLDS, "burnins": BURNINS, "probe_seeds": R.PROBE_SEEDS,
           "worlds": {arm: sum(1 for r in recs if r["arm"] == arm) for arm in ("T", "E", "N")},
           "first_episode_status": status, "primary": PRIMARY, "groups": {}, "false_alarms": {}}
    for (arm, st), rs in sorted(groups.items()):
        name = f"{arm}-{st}"
        g = {"arm": arm, "stratum": st, "primary": PRIMARY.get(st) == arm, "friend_episodes": len(rs),
             "observer_episodes": 4 * len(rs), "in_sight_at_crossing": sum(sum(r["sight_at_crossing"].values()) for r in rs),
             "H": {"min": min(r["crossing"] for r in rs), "median": _median([r["crossing"] for r in rs]), "max": max(r["crossing"] for r in rs)},
             "length_median": _median([r["length"] for r in rs]),
             "m": {str(m): sum(1 for r in rs if r["m"] == m) for m in sorted({r["m"] for r in rs}, key=lambda x: (x is None, x))},
             "edge": {e: sum(1 for r in rs if r["edge"] == e) for e in ("need", "happiness")} if arm != "T" else None,
             "cells": {c: stratum_cell(rs, c, with_sight=arm != "T") for c in cells}}
        out["groups"][name] = g
    for arm in ("T", "E", "N"):
        rs = [r for r in recs if r["arm"] == arm]
        out["false_alarms"][arm] = {c: false_alarm_cell(rs, c) for c in cells}
    return out


def read(progress=True):
    import torch
    torch.set_num_threads(1)
    probes = {s: R.load_probe(s)[:2] for s in R.PROBE_SEEDS}
    ws = worlds()
    recs = []
    t0 = time.time()
    for i, (arm, k, seed, ticks, path) in enumerate(ws):
        recs.append(world_record(arm, k, seed, ticks, path, probes))
        if progress and (i + 1) % 20 == 0:
            print(f"  {i + 1}/{len(ws)} worlds, {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
    out = ladder(recs)
    out["records"] = recs
    out["seconds"] = round(time.time() - t0)
    return out


def _f(m, d=3):
    if m is None:
        return "-"
    return f"{m['mean']:.{d}f} ± {m['sd']:.{d}f}" if m["sd"] is not None else f"{m['mean']:.{d}f}"


def md(out):
    lines = [f"## R4 — the ladder (tuning half: T {out['worlds']['T']}, E {out['worlds']['E']}, N {out['worlds']['N']} worlds; "
             f"seed mean ± SD over probe seeds {list(out['probe_seeds'])})", "",
             f"First-episode status per arm: {out['first_episode_status']}", ""]
    prim = [g for g in out["groups"].values() if g["primary"]]
    other = [g for g in out["groups"].values() if not g["primary"]]
    # the pick table: every cell on one row, the primary strata across (seed means; SDs in the per-stratum tables)
    names = [f"{PRIMARY[st]}-{st}" for st in ("H0", "H1", "H2", "H3", "H4")]
    have = [n for n in names if n in out["groups"]]
    lines += ["### The pick table (seed means; detected = share of observer-episodes; anticipated = alarm run starting in [mask onset, crossing), "
              "runs starting at offset B counted apart; false alarms per 10,000 observer-ticks, arm N)", "",
              "| threshold | B | " + " | ".join(f"det {n}" for n in have) + " | " + " | ".join(f"antic {n} (not at B)" for n in have if not n.startswith("T"))
              + " | FA N scripted from first mask | FA N covered friends |",
              "|" + "---|" * (2 + len(have) + len([n for n in have if not n.startswith("T")]) + 2)]
    for th in out["thresholds"]:
        for b in out["burnins"]:
            cn = cell_name(th, b)
            det = [f"{out['groups'][n]['cells'][cn]['detected']['mean']:.3f}" for n in have]
            ant = [f"{_f(out['groups'][n]['cells'][cn]['anticipated']).split(' ')[0]} ({_f(out['groups'][n]['cells'][cn]['anticipated_run_not_at_offset_B']).split(' ')[0]})"
                   for n in have if not n.startswith("T")]
            fa = out["false_alarms"]["N"][cn]
            lines.append(f"| {th:.2f} | {b} | " + " | ".join(det) + " | " + " | ".join(ant) + f" | {_f(fa['scripted_from_first_mask']['per_10k_ticks'], 2)} | {_f(fa['covered_friends']['per_10k_ticks'], 2)} |")
    lines.append("")
    for title, gs in (("Primary strata", prim), ("Printed apart, never pooled", other)):
        if not gs:
            continue
        lines += [f"### {title}", ""]
        for g in gs:
            lines += [f"**{g['arm']}-{g['stratum']}** — {g['friend_episodes']} friend episodes, {g['observer_episodes']} observer-episodes "
                      f"({g['in_sight_at_crossing']} in sight at the crossing); H min/median/max {g['H']['min']}/{g['H']['median']}/{g['H']['max']}; "
                      f"episode length median {g['length_median']}; m {g['m']}; edge {g['edge']}", "",
                      "| threshold | B | detected | median latency | p90 latency | within 10 | in sight | under fog | anticipated | median lead | anticipated, run not at B | median lead, not at B |",
                      "|---|---|---|---|---|---|---|---|---|---|---|---|"]
            for th in out["thresholds"]:
                for b in out["burnins"]:
                    c = g["cells"][cell_name(th, b)]
                    lines.append(f"| {th:.2f} | {b} | {_f(c['detected'])} | {_f(c['median_latency'], 1)} | {_f(c['p90_latency'], 1)} | {_f(c['within_10'])} | "
                                 f"{_f(c.get('detected_in_sight'))} | {_f(c.get('detected_under_fog'))} | {_f(c.get('anticipated'))} | {_f(c.get('median_lead_anticipated'), 1)} | "
                                 f"{_f(c.get('anticipated_run_not_at_offset_B'))} | {_f(c.get('median_lead_run_not_at_offset_B'), 1)} |")
            lines.append("")
    lines += ["### False alarms per 10,000 observer-ticks (anticipation runs excluded; mean run length in ticks; share of runs starting at offset B)", ""]
    for arm in ("T", "E", "N"):
        fa = out["false_alarms"][arm]
        t = next(iter(fa.values()))
        lines += [f"**arm {arm}** — observer-ticks per class: " + ", ".join(f"{c} {t[c]['observer_ticks']:,}" for c in FA_CLASSES), "",
                  "| threshold | B | scripted before first mask | len | at B | scripted from first mask | len | at B | covered friends | len | at B |",
                  "|---|---|---|---|---|---|---|---|---|---|---|"]
        for th in out["thresholds"]:
            for b in out["burnins"]:
                c = fa[cell_name(th, b)]
                lines.append(f"| {th:.2f} | {b} | " + " | ".join(
                    f"{_f(c[cls]['per_10k_ticks'], 2)} | {_f(c[cls]['mean_run_length'], 1)} | {_f(c[cls]['share_at_offset_B'], 2)}" for cls in FA_CLASSES) + " |")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "read"])
    ap.add_argument("--out")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    if a.cmd == "plan":
        print(json.dumps(plan(), indent=1))
    else:
        out = read()
        if a.out:
            # compact: the per-world records carry every cell's per-observer latency and lead
            Path(a.out).write_text(json.dumps(out, separators=(",", ":")) + "\n")
        print(md(out) if a.md else json.dumps({k: v for k, v in out.items() if k != "records"}, indent=1))
