#!/usr/bin/env python3
"""The scripted scout (DECLARATION.md §7 "Scripted scout" / "Arm E's
scripted scout", §11 step 3): 0 covered cat-ticks. Every seat runs its
config behaviour inside the engine (seat k `needy`, the others
`teacher`); nothing shaped by experience is in these worlds.

Two instruments per world, the same world (bc-collect seeds the engine
from `--seed-base` exactly as `ParallelEnv.reset(seed)` does; `run`
checks it per world and records the check):

- the collector (`../seating-analysis-g2-2026-10-21/seating_collect_g2.py`,
  `--seating scripted`): the streams the reader and n5 rest on, with the
  needy schedule per tick (n2) -> `results-raw/scout/<arm>/streams-<seed>.npz`;
- bc-collect `--trace`: the only instrument that carries refusal REASONS
  (the engine's refusal log is not readable through the binding; R8).
  Its trace (about 116 MB a 6,000-tick world, mostly per-tick
  observation rows no read uses) is written to the session scratchpad;
  what is kept is every refusal event verbatim, with the world-identity
  check -> `results-raw/scout/<arm>/refusals-<seed>.json`.

    scout.py run  --arm N|E [--edge E]          # burns the scout band in declared order; resumable
    scout.py read --arm N|E [--edge E] --out F [--md]  # the §7 read
    scout.py size [--edge E] --out F [--md]     # the sizing rule, the n pin, S3, the welfare numbers

Seeds: arm N 1095651-1095700, 10 per block in block order, 6,000 ticks,
then the second scripted block 1096461-1096510 (RESULTS.md step 3); arm
E 1096011-1096160, for each n in {50, 55, 60} 10 per block in block
order, 800 ticks (`split.json` scout_bands).

`--edge` is the late onset level's top edge the arm N configs carried
when the worlds burned (DECLARATION.md §13 amendment 1): 20000 (the
default; the two blocks above, `results-raw/scout/`) or 4500 (the
re-scout, seeds 1096511-1096610 as two more blocks of 50 in the same
order, `results-raw/scout-edge4500/`). `run --arm N` refuses a config
whose top edge is not the one asked for. Arm E has one generation: its
first onset is drawn inside level 0 and never reads the top edge.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "seating-analysis-g2-2026-10-21"))
import needy_read as R  # noqa: E402

RAW = HERE / "results-raw" / "scout"
BC = HERE.parent / "tools" / "bc-collect" / "target" / "release" / "bc-collect"
SCOUT = R.SPLIT["scout_bands"]
BLOCKS = (1, 2, 3, 4, 5)
N_VALUES = (50, 55, 60)
TICKS = {"N": 6000, "E": 800}
PER_BLOCK = 10
HIDDEN = R.NEED_NAMES[:5]
FLOOR = 50            # §7: first-episode friend-episodes per stratum, pooled over the halves
W_CAP = 60            # §7 S3
CAP_COVERED = 8_000_000
S1_STREAK = 1000      # F-053; watches no seat here (all scripted), recorded for the meta


HELD = R.SPLIT["held"]       # [1096461, 1096650]; the second scripted block takes its first 50
N_SCOUT_BLOCKS = 2           # owner "Do it" 2026-10-30: pooled 100 set the share, no third block
EDGES = (20000, 4500)        # the late level's top edge per arm N scout generation (§13 amendment 1)
# arm N block starts per edge: two blocks of 50 (10 per block) each
N_BLOCK_STARTS = {20000: (SCOUT["N"][0], HELD[0]), 4500: (HELD[0] + 50, HELD[0] + 100)}
RAW_BY_EDGE = {20000: RAW, 4500: HERE / "results-raw" / "scout-edge4500"}


def worlds(arm, edge=20000):
    """[(group, config, seed, ticks)] in burn order. Arm N is two scripted
    blocks of 50 per edge: at 20000 the scout band, then the first 50 of
    the held band (RESULTS.md §11 step 3, the second block); at 4500 the
    next 100 of the held band, 1096511-1096610 (the re-scout). The read
    pools the two blocks of one edge."""
    assert edge in EDGES, edge
    out = []
    if arm == "N":
        starts = N_BLOCK_STARTS[edge][:N_SCOUT_BLOCKS]
        for b, lo in enumerate(starts):
            for k in BLOCKS:
                for i in range(PER_BLOCK):
                    out.append((f"N{k}", HERE / f"g2leg-20-N{k}.toml", lo + (k - 1) * PER_BLOCK + i, TICKS["N"]))
            assert out[-1][2] == lo + 49 and out[-1][2] <= HELD[1]
        assert starts[0] in (SCOUT["N"][0], HELD[0] + 50) and (edge == 20000) == (starts[0] == SCOUT["N"][0])
    else:
        lo = SCOUT["E"][0]
        for ni, n in enumerate(N_VALUES):
            for k in BLOCKS:
                for i in range(PER_BLOCK):
                    seed = lo + ni * PER_BLOCK * len(BLOCKS) + (k - 1) * PER_BLOCK + i
                    out.append((f"E{k}-n{n}", HERE / f"g2leg-20-E{k}-n{n}.toml", seed, TICKS["E"]))
        assert out[-1][2] == SCOUT["E"][1]
    return out


def paths(group, seed, edge=20000):
    d = (RAW_BY_EDGE[edge] if group.startswith("N") else RAW) / group
    return d / f"streams-{seed}.npz", d / f"refusals-{seed}.json"


def config_edge(config):
    return tomllib.load(open(config, "rb"))["needy"]["onset_levels"][-1]


# ---- run ----------------------------------------------------------------

def collect_world(config, seed, ticks, out):
    import seating_collect_g2 as C
    arrays, meta = C.collect("scripted", seed, ticks, S1_STREAK, config=config, abort_covered_only=True)
    assert meta["aborted_at"] is None and meta["ticks"] == ticks and meta["abort_seats"] == [], meta
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, meta=json.dumps(meta), **arrays)
    return arrays, meta


def refusals_world(config, seed, ticks, arrays, meta, out, scratch):
    """bc-collect --trace on the same seed; keep the refusal events and the
    world-identity check (the pre-tick snapshot at t equals the collector's
    post-step state at t - 1, and at t = 0 the reset state)."""
    tmp = Path(tempfile.mkdtemp(prefix=f"bc-{seed}-", dir=scratch))
    try:
        r = subprocess.run([str(BC), "--config", str(config), "--rollouts", "1", "--ticks", str(ticks),
                            "--seed-base", str(seed), "--trace", "--out-dir", str(tmp)],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-2000:]
        (roll,) = [p for p in tmp.iterdir() if p.is_dir()]
        bmeta = json.loads((roll / "meta.json").read_text())
        assert bmeta["world_seed"] == seed and bmeta["ticks"] == ticks, bmeta
        events, tn, th, nticks = [], [], [], 0
        with open(roll / "trace.jsonl") as f:
            for line in f:
                o = json.loads(line)
                assert o["tick"] == nticks, (o["tick"], nticks)
                nticks += 1
                ks = o["snapshot"]["kitties"]
                tn.append([[kk["needs"][n] for n in R.NEED_NAMES] for kk in ks])
                th.append([kk["happiness"] for kk in ks])
                events.extend(o["refusals"])
        assert nticks == ticks, (nticks, ticks)
        tn, th = np.asarray(tn, np.float32), np.asarray(th, np.float32)
        d_needs = float(max(np.abs(tn[1:] - arrays["needs"][:ticks - 1]).max(), np.abs(tn[0] - arrays["needs0"]).max()))
        d_hap = float(max(np.abs(th[1:] - arrays["hap"][:ticks - 1]).max(), np.abs(th[0] - arrays["hap0"]).max()))
        cfg = tomllib.load(open(config, "rb"))
        friend_id = cfg["kitty"][meta["needy_seat"]]["id"]
        by = {}
        toward = {}
        for e in events:
            by[e["reason"]] = by.get(e["reason"], 0) + 1
            p = e.get("proposed") or {}
            if p.get("target") == "kitty" and p.get("id") == friend_id:
                toward[e["reason"]] = toward.get(e["reason"], 0) + 1
        rec = {"seed": seed, "config": config.name, "config_sha256": bmeta["config_sha256"],
               "engine_commit": bmeta["engine_commit"], "ticks": ticks, "friend_id": friend_id,
               "teachers_refused": bmeta["teachers_refused"], "decisions_recorded": bmeta["decisions"],
               "matches_collector": {"max_abs_needs": d_needs, "max_abs_happiness": d_hap,
                                     "same_world": bool(d_needs < 1e-3 and d_hap < 1e-3)},
               "by_reason": dict(sorted(by.items())), "toward_friend_by_reason": dict(sorted(toward.items())),
               "events": events}
        out.write_text(json.dumps(rec))
        return rec
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run(arm, scratch, edge=20000):
    import torch
    torch.set_num_threads(1)
    assert BC.exists(), f"{BC}: build it (cargo build --release) first"
    todo = worlds(arm, edge)
    if arm == "N":
        edges = {config_edge(c) for _g, c, _s, _t in todo}
        assert edges == {edge}, f"arm N configs carry top edge {edges}, the run asked for {edge}"
    t0 = time.time()
    for i, (group, config, seed, ticks) in enumerate(todo):
        npz, rj = paths(group, seed, edge)
        if npz.exists() and rj.exists():
            print(f"[{i + 1}/{len(todo)}] {group} {seed}: present, skipped", flush=True)
            continue
        arrays, meta = collect_world(config, seed, ticks, npz)
        rec = refusals_world(config, seed, ticks, arrays, meta, rj, scratch)
        m = rec["matches_collector"]
        print(f"[{i + 1}/{len(todo)}] {group} {seed}: {ticks} ticks, friend seat {meta['needy_seat']}, "
              f"{len(rec['events'])} refusals, same world {m['same_world']} (needs {m['max_abs_needs']:.2e}), "
              f"{time.time() - t0:.0f}s", flush=True)
    print(f"== scout {arm} done: {len(todo)} worlds, 0 covered cat-ticks, {time.time() - t0:.0f}s", flush=True)


# ---- read ---------------------------------------------------------------

def scout_block(seed, edge):
    """1 or 2: which of the edge's two blocks of 50 the seed is in."""
    starts = N_BLOCK_STARTS[edge]
    return 2 if seed >= starts[1] else 1


def world_record(group, seed, edge=20000):
    npz, rj = paths(group, seed, edge)
    w = R.load_world(npz)
    f = w["needy_seat"]
    assert w["scripted"] == list(range(R.ROSTER)) and w["meta"]["aborted_at"] is None
    codes = w["codes"][:, f]
    episodes = R.grave_episodes(codes)
    windows = R.mask_windows(w)
    mask, phase = w["needy_mask"], w["needy_phase"]
    lvl, lim = R.PHASES.index("released_level"), R.PHASES.index("released_limit")
    rec = {"group": group, "seed": seed, "ticks": w["ticks"], "friend_seat": f,
           "scout_block": scout_block(seed, edge) if group.startswith("N") else 1,
           "onset_top_edge": edge if group.startswith("N") else None,
           "grave_at_tick0": bool(codes[0] == R.S.GRAVE),
           "episodes_of_friend": len(episodes), "mask_windows": len(windows),
           "releases": {"level": 0, "limit": 0, "unreleased": 0}, "windows": [], "unmasked_crossings": [],
           "first": None}
    attributed = set()
    for j, (on, close, o) in enumerate(windows):
        bits = [n for i, n in enumerate(R.NEED_NAMES) if (int(mask[on]) >> i) & 1]
        released = R.PHASES[int(phase[close - 1])] if close - 1 >= 0 and phase[close - 1] in (lvl, lim) else "unreleased"
        rec["releases"]["level" if released == "released_level" else "limit" if released == "released_limit" else "unreleased"] += 1
        inside = [(c, e) for (c, e) in episodes if R.window_of(c, windows) == j]
        climbs = {}
        for n in bits:
            i = R.NEED_NAMES.index(n)
            hit = np.where(w["post_needs"][on:, f, i] >= R.S.NEED_DISTRESS)[0]
            climbs[n] = int(hit[0]) if len(hit) else None
        win = {"ordinal": o, "onset": on, "close": close, "release": released, "m": len(bits), "masked": bits,
               "climb_ticks": climbs, "crossing": None}
        if inside:
            c, e = inside[0]
            attributed.update(inside)
            needs_c, hap_c = w["needs"][c, f], float(w["hap"][c, f])
            over = [n for n, v in zip(HIDDEN, needs_c[:5]) if v >= R.S.NEED_DISTRESS]
            win["crossing"] = {"H": int(c), "stratum": R.stratum_of(int(c)), "length": int(e - c),
                               "edge": "need" if over else "happiness", "needs_at_90": over,
                               "happiness": hap_c, "episodes_inside": len(inside)}
        rec["windows"].append(win)
    rec["unmasked_crossings"] = [{"H": int(c), "length": int(e - c)} for (c, e) in episodes if (c, e) not in attributed]
    if windows:
        rec["first"] = rec["windows"][0]
    streaks = R.longest_streaks(w["distress"])
    rec["longest_streak"] = {"friend": int(streaks[f].max()),
                             "others_max": int(np.delete(streaks, f, 0).max()),
                             "per_seat": streaks.max(1).tolist()}
    rf = json.loads(rj.read_text())
    rec["refusals"] = {"same_world": rf["matches_collector"]["same_world"], "by_reason": rf["by_reason"],
                       "toward_friend_by_reason": rf["toward_friend_by_reason"], "total": len(rf["events"])}
    return rec


def _q(xs):
    xs = sorted(xs)
    if not xs:
        return None
    a = np.asarray(xs, float)
    return {"n": len(xs), "min": float(a.min()), "q1": float(np.percentile(a, 25)), "median": float(np.median(a)),
            "q3": float(np.percentile(a, 75)), "max": float(a.max())}


def _sum_dicts(ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out[k] = out.get(k, 0) + v
    return dict(sorted(out.items()))


def first_status(rec):
    fw = rec["first"]
    if fw is None:
        return "no_onset"
    if fw["release"] == "unreleased":
        # §3: a first episode not released by the world's end is printed as
        # unreleased and enters no stratum, crossing or not
        return "unreleased"
    if fw["crossing"] is not None:
        return fw["crossing"]["stratum"]
    return f"{fw['release']}_no_crossing"


def summarise(recs):
    """One group's (or the pool's) read."""
    n = len(recs)
    status = [first_status(r) for r in recs]
    strata = list(R.STRATA) + ["none"]
    counts = {s: 0 for s in strata}
    for s in status:
        counts[s if s in counts else "none"] += 1
    firsts = [r["first"]["crossing"] for r in recs if r["first"] and r["first"]["crossing"] and r["first"]["release"] != "unreleased"]
    unreleased_crossed = [r["first"]["crossing"]["H"] for r in recs
                          if r["first"] and r["first"]["crossing"] and r["first"]["release"] == "unreleased"]
    climbs = {nm: [] for nm in R.NEED_NAMES}
    for r in recs:
        for win in r["windows"]:
            for nm, c in win["climb_ticks"].items():
                if c is not None:
                    climbs[nm].append(c)
    Hs = [c["H"] for c in firsts]
    # unmasked crossings: after a release (ticks from the latest release step,
    # close - 1, to the crossing step, H - 1: that is H - close) or before any window
    after, before = [], 0
    for r in recs:
        closes = [win["close"] for win in r["windows"]]
        for u in r["unmasked_crossings"]:
            prev = [cl for cl in closes if cl <= u["H"] - 1]
            if prev:
                after.append(u["H"] - max(prev))
            else:
                before += 1
    out = {
        "worlds": n,
        "first_crossing_status": {k: v for k, v in sorted(_sum_dicts([{s: 1} for s in status]).items())},
        "stratum_share": {s: counts[s] / n for s in strata},
        "stratum_count": counts,
        "H": _q(Hs),
        "H_splice_bins": {f"[{lo},{hi})": sum(lo <= h < hi for h in Hs) for lo, hi in R.SPLICE_BINS},
        "first_edge": _sum_dicts([{c["edge"]: 1} for c in firsts]),
        "first_needs_at_90": _sum_dicts([{nm: 1} for c in firsts for nm in c["needs_at_90"]]),
        "first_length": _q([c["length"] for c in firsts]),
        "first_m": _sum_dicts([{str(r["first"]["m"]): 1} for r in recs if r["first"]]),
        "first_onset": _sum_dicts([{str(r["first"]["onset"]): 1} for r in recs if r["first"]]),
        "first_release": _sum_dicts([{r["first"]["release"]: 1} for r in recs if r["first"]]),
        "grave_at_tick0_share": sum(r["grave_at_tick0"] for r in recs) / n,
        "unreleased_first_with_crossing": {"n": len(unreleased_crossed), "H": sorted(unreleased_crossed)},
        "mask_windows_per_world": _q([r["mask_windows"] for r in recs]),
        "episodes_of_friend_per_world": _q([r["episodes_of_friend"] for r in recs]),
        "releases": _sum_dicts([r["releases"] for r in recs]),
        "unmasked_crossings": sum(len(r["unmasked_crossings"]) for r in recs),
        "unmasked_after_release": {"n": len(after), "ticks_after_release_step": _q(after)},
        "unmasked_before_any_window": before,
        "climb_ticks": {nm: _q(v) for nm, v in climbs.items() if v},
        "longest_streak_friend": _q([r["longest_streak"]["friend"] for r in recs]),
        "longest_streak_others_max": _q([r["longest_streak"]["others_max"] for r in recs]),
        "refusals_by_reason": _sum_dicts([r["refusals"]["by_reason"] for r in recs]),
        "refusals_toward_friend_by_reason": _sum_dicts([r["refusals"]["toward_friend_by_reason"] for r in recs]),
        "refusals_same_world": all(r["refusals"]["same_world"] for r in recs),
    }
    return out


def read(arm, edge=20000):
    ws = worlds(arm, edge)
    recs = [world_record(g, s, edge) for g, _c, s, _t in ws]
    groups = []
    for g in dict.fromkeys(r["group"] for r in recs):
        groups.append(g)
    out = {"arm": arm, "ticks": TICKS[arm], "worlds": len(recs), "covered_cat_ticks": 0,
           "per_group": {g: summarise([r for r in recs if r["group"] == g]) for g in groups},
           "records": recs}
    if arm == "N":
        out["onset_top_edge"] = edge
        out["pooled"] = summarise(recs)
        out["per_scout_block"] = {str(b): summarise([r for r in recs if r["scout_block"] == b])
                                  for b in sorted({r["scout_block"] for r in recs})}
    else:
        out["per_n"] = {str(n): summarise([r for r in recs if r["group"].endswith(f"-n{n}")]) for n in N_VALUES}
        shares = {n: out["per_n"][str(n)]["stratum_share"]["H1"] for n in N_VALUES}
        pin, best = None, -1.0
        for n in N_VALUES:                       # ascending: a tie keeps the smaller n
            if shares[n] > best:
                pin, best = n, shares[n]
        retired = [n for n in N_VALUES if out["per_n"][str(n)]["grave_at_tick0_share"] > 0]
        out["pin"] = {"n": pin, "H1_share": best, "H1_share_by_n": {str(n): shares[n] for n in N_VALUES},
                      "retired_by_grave_at_tick0": retired}
    return out


def md_read(out):
    arm = out["arm"]
    edge = f", onset top edge {out['onset_top_edge']}" if arm == "N" else ""
    lines = [f"## Scripted scout, arm {arm} ({out['worlds']} worlds x {out['ticks']} ticks, 0 covered cat-ticks{edge})", ""]
    keys = list(out["per_group"]) + (["pooled"] if arm == "N" else [])
    tables = dict(out["per_group"])
    if arm == "N":
        for b, s in out["per_scout_block"].items():
            tables[f"scout block {b}"] = s
            keys.append(f"scout block {b}")
        tables["pooled"] = out["pooled"]
    else:
        for n in N_VALUES:
            tables[f"n = {n}"] = out["per_n"][str(n)]
            keys.append(f"n = {n}")
    cols = ["worlds", "H1", "H2", "H3", "H4", "none", "H median", "edge need/hap", "len median", "level/limit/unrel",
            "unmasked", "streak friend max", "refusals", "toward friend"]
    lines.append("| group | " + " | ".join(cols) + " |")
    lines.append("|" + "---|" * (len(cols) + 1))
    for g in keys:
        s = tables[g]
        sh = s["stratum_share"]
        rel = s["releases"]
        ed = s["first_edge"]
        lines.append(f"| {g} | {s['worlds']} | {sh['H1']:.2f} | {sh['H2']:.2f} | {sh['H3']:.2f} | {sh['H4']:.2f} | {sh['none']:.2f} | "
                     f"{s['H']['median'] if s['H'] else '-'} | {ed.get('need', 0)}/{ed.get('happiness', 0)} | "
                     f"{s['first_length']['median'] if s['first_length'] else '-'} | "
                     f"{rel.get('level', 0)}/{rel.get('limit', 0)}/{rel.get('unreleased', 0)} | {s['unmasked_crossings']} | "
                     f"{int(s['longest_streak_friend']['max'])} | {sum(s['refusals_by_reason'].values())} | "
                     f"{sum(s['refusals_toward_friend_by_reason'].values())} |")
    pooled = out["pooled"] if arm == "N" else None
    for g in ([("pooled", pooled)] if pooled else [(f"n = {n}", out["per_n"][str(n)]) for n in N_VALUES]):
        name, s = g
        lines += ["", f"**{name}.** first-crossing status {s['first_crossing_status']}; onset ticks {s['first_onset']}; "
                  f"m {s['first_m']}; needs at 90 at the first crossing {s['first_needs_at_90']}; "
                  f"H splice bins {s['H_splice_bins']}; grave at tick 0 share {s['grave_at_tick0_share']:.3f}; "
                  f"first windows unreleased at the end but crossed (no stratum, §3) {s['unreleased_first_with_crossing']}; "
                  f"unmasked crossings after a release {s['unmasked_after_release']}, before any window {s['unmasked_before_any_window']}; "
                  f"climb ticks (median) { {k: v['median'] for k, v in s['climb_ticks'].items()} }; "
                  f"friend's longest single-need streak median {s['longest_streak_friend']['median']} max {int(s['longest_streak_friend']['max'])}, "
                  f"other seats' max {int(s['longest_streak_others_max']['max'])}; "
                  f"refusals by reason {s['refusals_by_reason']}; toward the friend {s['refusals_toward_friend_by_reason']}; "
                  f"same world under both instruments: {s['refusals_same_world']}."]
    if arm == "E":
        p = out["pin"]
        lines += ["", f"**Pin (mechanical, §7):** n = {p['n']} (H1 share {p['H1_share']:.3f}; by n {p['H1_share_by_n']}; "
                  f"retired by grave-at-tick-0: {p['retired_by_grave_at_tick0'] or 'none'})."]
    return "\n".join(lines) + "\n"


# ---- size ---------------------------------------------------------------

def smallest_even(share):
    """The smallest even w with 5 w x share >= FLOOR; None when share is 0."""
    if share <= 0:
        return None
    w = int(np.ceil(FLOOR / (5 * share)))
    return w + (w % 2)


def size(read_n, read_e):
    sh = read_n["pooled"]["stratum_share"]
    min_share = min(sh["H2"], sh["H3"], sh["H4"])
    w = smallest_even(min_share)
    pin = read_e["pin"]
    w_e = smallest_even(pin["H1_share"])
    t_cov = 50 * 4000 * 4
    scout_n = 2 * PER_BLOCK * TICKS["N"] * 4          # 10 seeds x 2 runs, 4 covered seats
    scout_e = 2 * PER_BLOCK * TICKS["E"] * 4
    n3 = 10_000
    set_n = 5 * (w or 0) * TICKS["N"] * 4
    set_e = 5 * (w_e or 0) * TICKS["E"] * 4
    total = t_cov + scout_n + scout_e + n3 + set_n + set_e
    s3 = {"zero_share_stratum": [s for s in ("H2", "H3", "H4") if sh[s] == 0] + (["H1"] if pin["H1_share"] == 0 else []),
          "w_over_cap": w is None or w > W_CAP, "w_E_over_cap": w_e is None or w_e > W_CAP,
          "H1_under_sixth_at_every_n": all(v < 1 / 6 for v in pin["H1_share_by_n"].values()),
          "total_over_cap": total > CAP_COVERED}
    return {"onset_top_edge": read_n["onset_top_edge"], "arm_N_worlds_read": read_n["worlds"],
            "arm_N": {"shares": {s: sh[s] for s in ("H1", "H2", "H3", "H4", "none")}, "min_share_H2_H3_H4": min_share,
                      "w": w, "worlds": 5 * (w or 0), "expected_first_episodes_min_stratum": 5 * (w or 0) * min_share},
            "arm_E": {"n": pin["n"], "H1_share": pin["H1_share"], "H1_share_by_n": pin["H1_share_by_n"], "w_E": w_e,
                      "worlds": 5 * (w_e or 0), "expected_H1_first_episodes": 5 * (w_e or 0) * pin["H1_share"]},
            "rule": f"smallest even w with 5w x share >= {FLOOR}; cap {W_CAP}",
            "covered_cat_ticks": {"arm_T": t_cov, "covered_scout_N": scout_n, "covered_scout_E": scout_e, "n3": n3,
                                  "arm_N": set_n, "arm_E": set_e, "total": total, "cap": CAP_COVERED},
            "S3": s3, "S3_trips": any(v for v in s3.values() if not isinstance(v, list)) or bool(s3["zero_share_stratum"])}


def md_size(s):
    N, E, c = s["arm_N"], s["arm_E"], s["covered_cat_ticks"]
    return "\n".join([
        f"## Sizing (§7, mechanical; arm N scout at onset top edge {s['onset_top_edge']}, {s['arm_N_worlds_read']} worlds)", "",
        f"- Arm N shares (pooled, first crossing): H2 {N['shares']['H2']:.2f}, H3 {N['shares']['H3']:.2f}, "
        f"H4 {N['shares']['H4']:.2f}, none {N['shares']['none']:.2f}; the smallest {N['min_share_H2_H3_H4']:.2f} -> "
        f"w = {N['w']} ({N['worlds']} worlds, {N['expected_first_episodes_min_stratum']:.1f} expected first episodes in the thinnest stratum).",
        f"- Arm E pin n = {E['n']} (H1 share {E['H1_share']:.2f}; by n {E['H1_share_by_n']}) -> w_E = {E['w_E']} "
        f"({E['worlds']} worlds, {E['expected_H1_first_episodes']:.1f} expected H1 first episodes).",
        f"- Covered cat-ticks: arm T {c['arm_T']:,}; covered scouts {c['covered_scout_N']:,} + {c['covered_scout_E']:,}; "
        f"n3 {c['n3']:,}; arm N {c['arm_N']:,}; arm E {c['arm_E']:,}; total {c['total']:,} of the {c['cap']:,} cap.",
        f"- S3: {s['S3']} -> {'TRIPS, back to her' if s['S3_trips'] else 'clear'}.", ""])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "read", "size"])
    ap.add_argument("--arm", choices=["N", "E"])
    ap.add_argument("--out", type=Path)
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--scratch", type=Path, default=Path(os.environ.get("SCOUT_SCRATCH", tempfile.gettempdir())))
    ap.add_argument("--edge", type=int, choices=EDGES, default=20000,
                    help="arm N's onset top edge generation (reads scout-N.json at 20000, scout-N-edge<E>.json otherwise)")
    a = ap.parse_args()
    if a.cmd == "run":
        run(a.arm, a.scratch, a.edge)
        return
    if a.cmd == "read":
        out = read(a.arm, a.edge)
        text = md_read(out)
    else:
        n_name = "scout-N.json" if a.edge == 20000 else f"scout-N-edge{a.edge}.json"
        rn = json.loads((a.out.parent / n_name).read_text())
        re_ = json.loads((a.out.parent / "scout-E.json").read_text())
        assert rn.get("onset_top_edge", 20000) == a.edge, (rn.get("onset_top_edge"), a.edge)
        out = size(rn, re_)
        text = md_size(out)
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(out, indent=1))
    if a.md:
        print(text)
    else:
        print(json.dumps({k: v for k, v in out.items() if k != "records"}, indent=1))


if __name__ == "__main__":
    main()
