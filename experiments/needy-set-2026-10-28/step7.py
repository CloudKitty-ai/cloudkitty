#!/usr/bin/env python3
"""§11 step 7 — the reads after her pick (DECLARATION.md §5 R1–R3, R5–R8;
§6 the registered predictions; owner "Take care of both of those, then
run step 7", 2026-11-01, after her pick "Ok, I'm convinced. 0.05, 2").

Everything here is a read on raws already on disk: 0 covered cat-ticks.
The probe is NF-h24+p (three seeds, n8), run as the ladder ran it; the
episode, crossing, anchor, anticipation and false-alarm definitions are
`ladder.py`'s (§4), with the fix of 17d1ea96 (an anticipation run STARTS
inside [mask onset, crossing)).

Cells read: the registered point 0.10 / B = 0 (§6: every prediction sits
there), its B = 2 companion (§5 R1, R2), and her pick 0.05 / B = 2 (R5).

- R5 confirm (confirming seeds only, through `refuse_unless`): the picked
  cell, R4's columns per primary stratum and the false alarms per class,
  beside the tuning values (`reads/ladder.json`); a stratum whose
  confirming value falls outside its tuning value +- 2 world-bootstrap SE
  is flagged, not failed (the SE: worlds resampled with replacement
  within the stratum, 2,000 draws, per probe seed, seed-mean).
- R1 tie-back (arm T, all 50 worlds): reset detection at 0.10, B = 0 and
  2, per block and pooled, two ways: anywhere in the episode (R4d) and
  inside both the episode and the first 100 ticks (P7's clause); beside
  P's same-seed covered figure, read from P's committed P(grave) files
  (1d) on P's own raws (1b), the covered friend in seat k, the other four
  observers.
- R2 history (arm N and E first episodes, all seeds): detection and median
  latency per primary stratum at 0.10, B = 0 and 2, beside the splice
  (§2); the episode-length distribution beside the donors' 5 / 40 / 238;
  in sight and under fog apart; which edge crossed apart; H1 also in the
  splice's bins by crossing.
- R3 anticipation (arm N and E first episodes): the fraction anticipated
  and the lead distribution per stratum, per m and per masked need, at
  0.10 / B = 0 and the pick; the probe logit aligned to the crossing, mean
  over observer-episodes from the mask onset, per stratum. P6's read.
- R6 which need (descriptive): on the scripted friend's grave samples in
  sight, how often the argmax of NF-h24's five predicted means is a
  masked hidden need (and, R3d's read, a need at 90); per masked need on
  single-need masks; fail-closed under 200 samples.
- R7 later episodes (ordinal 2 and up): by the gap since the last release
  (300-tick bands), never pooled with first episodes.
- R8 price (descriptive): the covered seats' mean happiness, distress
  ticks and worst single-need streak, in the covered scout against the
  paired controls and across the set (halves apart and pooled, as ruled
  2026-11-01); refused proposals toward the scripted friend (a covered
  seat's chosen menu action naming the friend, not applied as proposed),
  attributed to the mask by target and timing (the friend's side of the
  ask relieves a need masked at the decision's state), the rest "other".

Predictions (§6, scored on all seeds, after R5): P6, P7, P10, P11.

    step7.py plan
    step7.py read --out F [--md]        # about 4 min
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
sys.path.insert(0, str(HERE.parent / "gen2-trunk-training-2026-10-18" / "trainer"))
import needy_read as R  # noqa: E402
import set_run as SR  # noqa: E402
import ladder as L  # noqa: E402
import covered_scout as CS  # noqa: E402
from data_g2 import menu_names  # noqa: E402

PICK = (0.05, 2)                     # her word 2026-11-01: "Ok, I'm convinced. 0.05, 2"
REG = (0.10, 0)                      # §6: the registered operating point of every prediction
REG_B2 = (0.10, 2)                   # §5 R1 / R2: "B = 0 and B = 2"
CELLS = {"reg": L.cell_name(*REG), "reg_b2": L.cell_name(*REG_B2), "pick": L.cell_name(*PICK)}
P_RAW = R.PHASE1B / "results-raw"
P_PROBE = R.PHASE1D / "results-raw" / "probe"
LADDER = HERE / "reads" / "ladder.json"
BOOT = 2000
BOOT_SEED = 0
MIN_N = 200                          # R6: Phase 1's fail-closed floor
GAP_BANDS = ((300, 600), (600, 900), (900, 1201))
PROFILE = (-100, 21)                 # R3: offsets from the crossing, [-100, 20]
MENU = menu_names()
PARTNERED = {"RestWith": ("rest", ("cuddle",)), "SleepWith": ("sleep", ("sleep", "cuddle")),
             "Groom": ("groom", ("bath",)), "Chase": ("chase", ("play",)), "Play": ("play", ("play",))}

# §6, verbatim numbers
PRED = {"P7": {"bar": 0.986, "comparator": 0.995, "sd": 0.009},
        "P10": {"H2": (0.358, 0.175), "H3": (0.287, 0.143), "H4": (0.288, 0.132)},
        "P11": {"lo": 0.292, "hi": 0.432, "splice_H50": 0.362},
        "P6": {"majority": 0.5, "median_lead": 20}}
SPLICE = {"H1": {"H50": 0.362, "H10": 0.658, "H20": 0.537}, "H2": {"H100": 0.358}, "H3": {"H500": 0.287}, "H4": {"H2000": 0.288}}
DONORS = {"min": 5, "median": 40, "max": 238}


def cell(c):
    return CELLS[c]


def _q(xs):
    xs = sorted(xs)
    if not xs:
        return None
    a = np.asarray(xs, float)
    return {"n": len(xs), "min": float(a.min()), "q1": float(np.percentile(a, 25)), "median": float(np.median(a)),
            "q3": float(np.percentile(a, 75)), "max": float(a.max())}


# ---- worlds and probes ----------------------------------------------------------

def worlds():
    """Every set world, both halves, in the set's order."""
    return [(arm, k, seed, ticks, path, R.half_of(arm, k, seed)) for arm, k, _c, seed, ticks, path in SR.worlds()]


def plan():
    ws = worlds()
    return {"worlds": len(ws), "halves": {h: sum(1 for w in ws if w[5] == h) for h in ("tuning", "confirming")},
            "arms": {a: sum(1 for w in ws if w[0] == a) for a in ("T", "E", "N")}, "cells": CELLS, "pick": PICK,
            "P_worlds": sum(len(R.arm_block("T", k)["seeds"]) for k in CS.BLOCKS), "covered_scout_pairs": 20, "covered_cat_ticks": 0}


def probe_full(model, probe, w, pairs):
    """P(grave) (T, R, R) and the head's five predicted means (T, n_pairs, 5)
    for `pairs`, exactly as needy_read.probe_world runs the head."""
    import torch
    x = torch.from_numpy(np.stack([R.pair_x(w, k, j)[0] for k, j in pairs], 1))
    Tn = w["ticks"]
    ps, ms, h = [], [], None
    with torch.no_grad():
        for c0 in range(0, Tn, R.CHUNK):
            z, h = model.gru(torch.relu(model.proj(x[c0:min(c0 + R.CHUNK, Tn)].float())), h)
            ps.append(torch.sigmoid(probe(z).squeeze(-1)))
            ms.append(model.out(z)[..., :5])
    p = torch.cat(ps).numpy()
    full = np.full((Tn, R.ROSTER, R.ROSTER), np.nan, np.float32)
    for i, (k, j) in enumerate(pairs):
        full[:, k, j] = p[:, i]
    return full, torch.cat(ms).numpy()


def slot_roster(observer):
    """Kitty slot i of an observer's menu -> seat: the roster minus the
    observer, ascending (kitty ids follow seats)."""
    return [j for j in range(R.ROSTER) if j != observer]


def proposals_toward(w, f, applied_names):
    """Per covered seat: the chosen menu actions naming the scripted friend,
    how many were not applied as proposed, and of those how many fall at a
    decision state whose mask covers a need the ask relieves on the
    friend's side (attributed to the mask) vs the rest."""
    z = np.load(w["path"])
    act, ap, aw = z["act"], z["applied"], z["applied_with"]
    mask = w.get("needy_mask")
    out = {}
    for s in R.observers(w):
        roster = slot_roster(s)
        n = refused = by_mask = 0
        fam_counts = {}
        for t in np.flatnonzero(act[:, s] >= 0):
            name = MENU[act[t, s]]
            if "Kitty" not in name:
                continue
            fam, slot = name.split("Kitty")
            if roster[int(slot)] != f:
                continue
            n += 1
            ok_name, relieves = PARTNERED[fam]
            granted = applied_names[ap[t, s]] == ok_name and aw[t, s] == f
            if granted:
                continue
            refused += 1
            fam_counts[fam] = fam_counts.get(fam, 0) + 1
            bits = int(mask[t - 1]) if (mask is not None and t > 0) else 0
            if any((bits >> R.NEED_NAMES.index(nm)) & 1 for nm in relieves):
                by_mask += 1
        out[str(s)] = {"toward_friend": int(n), "refused": int(refused), "refused_by_mask": int(by_mask),
                       "refused_other": int(refused - by_mask), "refused_by_family": fam_counts}
    return out


def world_record(arm, k, seed, ticks, path, half, probes):
    w = R.load_world(path)
    assert w["meta"]["aborted_at"] is None and w["ticks"] == ticks and w["scripted"] == [k - 1], (arm, k, seed)
    f = k - 1
    fe = L.first_episode(w, arm)
    obs = R.observers(w)
    pairs_f = [(kk, f) for kk in obs]
    p_by_seed, means = {}, {}
    for s, (m, p) in probes.items():
        full, mm = probe_full(m, p, w, R.observer_pairs(w))
        p_by_seed[s] = full
        means[s] = {kk: mm[:, R.observer_pairs(w).index((kk, f)), :] for kk in obs}
    cells = L.world_cells(w, arm, p_by_seed, fe)
    rec = {"arm": arm, "block": k, "seed": seed, "half": half, "ticks": ticks, "friend": f, "status": fe["status"],
           "crossing": fe["crossing"], "end": None if fe["crossing"] is None else fe["end"],
           "length": None if fe["crossing"] is None else fe["end"] - fe["crossing"],
           "onset": fe["onset"], "stratum": fe["stratum"], "m": fe["m"], "masked": fe["masked"], "edge": fe["edge"],
           "windows": [list(x) for x in fe["windows"]], "episodes": [list(x) for x in fe["episodes"]],
           "sight_at_crossing": cells["sight_at_crossing"], "observer_ticks": cells["observer_ticks"],
           "cells": {s: {c: cells["cells"][s][c] for c in CELLS.values()} for s in cells["cells"]}}
    vis = {kk: R.pair_x(w, kk, f)[1] for kk in obs}
    # R1 / P7: detection inside both the episode and the first 100 ticks (arm T reset episodes)
    if arm == "T" and fe["crossing"] is not None:
        c, e = fe["crossing"], fe["end"]
        rec["within100"] = {}
        for s, P in p_by_seed.items():
            P = np.nan_to_num(P, nan=-1.0)
            for name, (th, b) in (("reg", REG), ("reg_b2", REG_B2)):
                a = P[:, :, f] >= th
                a[:b] = False
                rec["within100"].setdefault(str(s), {})[name] = {str(kk): bool(a[c:min(e, 100), kk].any()) for kk in obs}
    # R3: the logit aligned to the crossing from the mask onset, per observer, seed 1..3 averaged later
    if arm != "T" and fe["crossing"] is not None:
        c, on = fe["crossing"], fe["onset"]
        lo, hi = PROFILE
        prof = np.full((len(p_by_seed), len(obs), hi - lo), np.nan, np.float32)
        for si, (s, P) in enumerate(p_by_seed.items()):
            for oi, kk in enumerate(obs):
                for r in range(lo, hi):
                    t = c + r
                    if on <= t < w["ticks"]:
                        pv = float(np.clip(P[t, kk, f], 1e-6, 1 - 1e-6))
                        prof[si, oi, r - lo] = np.log(pv / (1 - pv))
        rec["logit_profile"] = np.nanmean(prof, axis=(0, 1)).round(3).tolist()   # NaN where before onset for all
        rec["logit_profile_n"] = int(np.isfinite(prof[0]).any(0).sum())
    # R6: which need, on the friend's grave samples in sight
    grave_t = np.flatnonzero(w["codes"][:, f] == R.S.GRAVE)
    r6 = {}
    for s in means:
        tot = hit_mask = hit_90 = 0
        per_need = {}
        for kk in obs:
            ts = grave_t[vis[kk][grave_t]]
            if len(ts) == 0:
                continue
            named = means[s][kk][ts].argmax(1)                       # index into the five hidden needs
            at90 = w["needs"][ts, f, :5] >= R.S.NEED_DISTRESS
            hit_90 += int(at90[np.arange(len(ts)), named].sum())
            tot += len(ts)
            if "needy_mask" in w:
                bits = w["needy_mask"][np.maximum(ts - 1, 0)]
                masked5 = ((bits[:, None] >> np.arange(5)) & 1).astype(bool)
                hit_mask += int(masked5[np.arange(len(ts)), named].sum())
                single = masked5.sum(1) == 1
                for i, nm in enumerate(R.NEED_NAMES[:5]):
                    sel = single & masked5[:, i]
                    if sel.any():
                        d = per_need.setdefault(nm, [0, 0])
                        d[0] += int(sel.sum())
                        d[1] += int((named[sel] == i).sum())
        r6[str(s)] = {"samples": tot, "named_masked": hit_mask if "needy_mask" in w else None, "named_at90": hit_90,
                      "per_masked_need": per_need}
    rec["which_need"] = r6
    # R7: later episodes by the gap since the last release
    later = []
    for j in range(1, len(fe["windows"])):
        on, close, o = fe["windows"][j]
        prev_close = fe["windows"][j - 1][1]
        inside = [(cc, ee) for (cc, ee) in fe["episodes"] if R.window_of(cc, fe["windows"]) == j]
        released = close < w["ticks"]
        ep = {"ordinal": o, "gap": on - prev_close, "released": released, "crossing": None}
        if inside and released:
            cc, ee = inside[0]
            ep.update(crossing=int(cc), length=int(ee - cc), H_since_onset=int(cc - on),
                      in_sight=int(sum(bool(vis[kk][cc]) for kk in obs)))
            for s, P in p_by_seed.items():
                P = np.nan_to_num(P, nan=-1.0)
                ep.setdefault("latency", {})[str(s)] = {}
                for name, (th, b) in (("reg", REG), ("pick", PICK)):
                    a = P[:, :, f] >= th
                    a[:b] = False
                    lat = {}
                    for kk in obs:
                        hit = np.flatnonzero(a[cc:ee, kk])
                        lat[str(kk)] = int(hit[0]) if len(hit) else None
                    ep["latency"][str(s)][name] = lat
        later.append(ep)
    rec["later_episodes"] = later
    # R8: price per covered seat and refused proposals toward the friend
    rec["price"] = CS.seat_price(w)
    rec["proposals"] = proposals_toward(w, f, w["meta"]["applied_names"])
    return rec


# ---- R1: P's same-seed covered figure ---------------------------------------------

def p_record(k, seed, probes):
    """P's world of the same seed and block: the covered friend in seat k - 1
    (its needs started in {60, 95}), the other four observers; reset
    detection at 0.10 / B = 0 and 2 from the committed P(grave) files."""
    w = R.load_world(P_RAW / f"P{k}" / f"streams-{seed}.npz")
    f = k - 1
    assert w["scripted"] == [] and w["ticks"] == 4000
    # the pairing's seat: P's covered friend in block k is seat k - 1, every need started in {60, 95}
    assert (w["needs"][0, f] >= 60).all(), ("P pairing", k, seed, f, w["needs"][0, f].tolist())
    eps = R.grave_episodes(w["codes"][:, f])
    rec = {"block": k, "seed": seed, "reset": bool(eps and eps[0][0] == 0), "detect": {}}
    if not rec["reset"]:
        return rec
    c, e = eps[0]
    rec["length"] = int(e - c)
    obs = [j for j in range(R.ROSTER) if j != f]
    for s in probes:
        P = np.nan_to_num(np.load(P_PROBE / f"{R.HEAD}-s{s}+p" / f"pgrave-P{k}-{seed}.npz")["p"], nan=-1.0)
        for name, (th, b) in (("reg", REG), ("reg_b2", REG_B2)):
            a = P[:, :, f] >= th
            a[:b] = False
            rec["detect"].setdefault(str(s), {})[name] = {
                "anywhere": {str(kk): bool(a[c:e, kk].any()) for kk in obs},
                "within100": {str(kk): bool(a[c:min(e, 100), kk].any()) for kk in obs}}
    return rec


# ---- aggregation ----------------------------------------------------------------------

def msd(xs):
    return L.msd(xs)


def _frac(flags):
    flags = [x for x in flags if x is not None]
    return sum(bool(x) for x in flags) / len(flags) if flags else None


def r1(recs, precs):
    """Arm T: reset detection per block and pooled, anywhere / within 100,
    at 0.10 B = 0 and 2; P's same-seed covered figure beside."""
    out = {}
    for name in ("reg", "reg_b2"):
        rows = {}
        for scope in ["pooled"] + [f"T{k}" for k in CS.BLOCKS]:
            sel = [r for r in recs if r["arm"] == "T" and r["crossing"] is not None and (scope == "pooled" or r["block"] == int(scope[1]))]
            psel = [p for p in precs if p["reset"] and (scope == "pooled" or p["block"] == int(scope[1]))]
            per = {}
            for s in map(str, R.PROBE_SEEDS):
                per[s] = {"anywhere": _frac([lat is not None for r in sel for lat in r["cells"][s][cell(name)]["latency"].values()]),
                          "within100": _frac([v for r in sel for v in r["within100"][s][name].values()]),
                          "P_anywhere": _frac([v for p in psel for v in p["detect"][s][name]["anywhere"].values()]),
                          "P_within100": _frac([v for p in psel for v in p["detect"][s][name]["within100"].values()])}
            rows[scope] = {"friend_episodes": len(sel), "observer_episodes": 4 * len(sel), "P_friend_episodes": len(psel),
                           "length_median": L._median([r["length"] for r in sel]), "P_length_median": L._median([p["length"] for p in psel]),
                           **{key: msd([per[s][key] for s in per]) for key in ("anywhere", "within100", "P_anywhere", "P_within100")},
                           "per_seed": per}
        out[name] = rows
    out["T_not_grave_at_tick0"] = sum(1 for r in recs if r["arm"] == "T" and r["crossing"] is None)
    out["P_not_reset"] = sum(1 for p in precs if not p["reset"])
    return out


def group_recs(recs, half=None):
    g = {}
    for r in recs:
        if r["stratum"] is not None and (half is None or r["half"] == half):
            g.setdefault(f"{r['arm']}-{r['stratum']}", []).append(r)
    return g


def r2(recs):
    """History: per (arm, stratum), at reg and reg_b2: detection, latency, in
    sight / fog, per edge; lengths beside the donors'; H1 in splice bins."""
    out = {"groups": {}, "splice": SPLICE, "donors": DONORS}
    for name, rs in sorted(group_recs(recs).items()):
        arm, st = name.split("-")
        g = {"arm": arm, "stratum": st, "primary": L.PRIMARY.get(st) == arm, "friend_episodes": len(rs), "observer_episodes": 4 * len(rs),
             "halves": {h: sum(1 for r in rs if r["half"] == h) for h in ("tuning", "confirming")},
             "H": _q([r["crossing"] for r in rs]),
             "length": {"min": min(r["length"] for r in rs), "q1": float(np.percentile([r["length"] for r in rs], 25)),
                        "median": L._median([r["length"] for r in rs]), "q3": float(np.percentile([r["length"] for r in rs], 75)),
                        "max": max(r["length"] for r in rs)},
             "edge": {e: sum(1 for r in rs if r["edge"] == e) for e in ("need", "happiness")} if arm != "T" else None,
             "m": {str(m): sum(1 for r in rs if r["m"] == m) for m in (1, 2, 3, 4)} if arm != "T" else None,
             "cells": {}}
        for cname in ("reg", "reg_b2", "pick"):
            g["cells"][cname] = L.stratum_cell(rs, cell(cname), with_sight=arm != "T")
            if arm != "T":
                g["cells"][cname]["by_edge"] = {e: L.stratum_cell([r for r in rs if r["edge"] == e], cell(cname), with_sight=True)["detected"]
                                                for e in ("need", "happiness") if any(r["edge"] == e for r in rs)}
        if st == "H1":
            bins = {}
            for lo, hi in R.SPLICE_BINS:
                sel = [r for r in rs if lo <= r["crossing"] < hi]
                if sel:
                    bins[f"[{lo},{hi})"] = {"friend_episodes": len(sel), "detected_reg": L.stratum_cell(sel, cell("reg"), with_sight=True)["detected"]}
            g["splice_bins"] = bins
        out["groups"][name] = g
    return out


def lead_rows(rs, cname, key):
    """Per seed over observer-episodes: fraction anticipated and the lead
    quartiles; seed means."""
    per = {}
    for s in map(str, R.PROBE_SEEDS):
        leads = [v for r in rs for v in r["cells"][s][cell(cname)][key].values()]
        have = [v for v in leads if v is not None]
        per[s] = {"anticipated": len(have) / len(leads) if leads else None, "median_lead": L._median(have),
                  "q1_lead": float(np.percentile(have, 25)) if have else None, "q3_lead": float(np.percentile(have, 75)) if have else None}
    return {k: msd([per[s][k] for s in per]) for k in ("anticipated", "median_lead", "q1_lead", "q3_lead")} | {"observer_episodes": 4 * len(rs)}


def r3(recs):
    """Anticipation per stratum, per m, per masked need (single-need masks),
    at reg and pick, leads from the first anticipation run and from the
    first not at offset B; the logit profile per stratum; P6's read."""
    out = {"profile_offsets": list(range(*PROFILE)), "groups": {}}
    for name, rs in sorted(group_recs(recs).items()):
        if name.startswith("T"):
            continue
        g = {"friend_episodes": len(rs), "cells": {}}
        for cname in ("reg", "pick"):
            g["cells"][cname] = {"all": lead_rows(rs, cname, "lead"), "not_at_B": lead_rows(rs, cname, "lead_not_at_offset_B"),
                                 "per_m": {str(m): lead_rows([r for r in rs if r["m"] == m], cname, "lead") for m in (1, 2, 3, 4) if any(r["m"] == m for r in rs)},
                                 "per_need_single": {nm: lead_rows([r for r in rs if r["m"] == 1 and r["masked"] == [nm]], cname, "lead")
                                                     for nm in R.NEED_NAMES if any(r["m"] == 1 and r["masked"] == [nm] for r in rs)}}
        prof = np.array([r["logit_profile"] for r in rs], float)
        g["logit_profile_mean"] = np.nanmean(prof, 0).round(3).tolist()
        g["logit_profile_n"] = np.isfinite(prof).sum(0).tolist()
        out["groups"][name] = g
    # P6: arm N first episodes, m = 1, the masked need hidden, in sight at the crossing; reg cell
    elig = [r for r in recs if r["arm"] == "N" and r["stratum"] is not None and r["m"] == 1 and r["masked"][0] in R.NEED_NAMES[:5]]
    p6 = {"eligible_friend_episodes": len(elig), "per_stratum": {}, "per_seed": {}}
    def p6_read(rs):
        per = {}
        for s in map(str, R.PROBE_SEEDS):
            leads = [r["cells"][s][cell("reg")]["lead"][kk] for r in rs for kk in r["cells"][s][cell("reg")]["lead"] if r["sight_at_crossing"][kk]]
            n = len(leads)
            have = [v for v in leads if v is not None]
            # a never-alarmed episode counts as the lowest value: median over the padded list
            padded = sorted([-1] * (n - len(have)) + have)
            med = float(np.median(padded)) if padded else None
            per[s] = {"observer_episodes": n, "majority": len(have) / n if n else None, "median_lead_padded": med}
        return {"per_seed": per, "majority": msd([per[s]["majority"] for s in per]), "median_lead_padded": msd([per[s]["median_lead_padded"] for s in per])}
    p6["pooled"] = p6_read(elig)
    for st in ("H2", "H3", "H4"):
        sel = [r for r in elig if r["stratum"] == st]
        if sel:
            p6["per_stratum"][st] = p6_read(sel)
    out["P6"] = p6
    return out


def world_bootstrap_se(rs, cname, key, rng):
    """SE of a stratum's seed-mean fraction (detected / anticipated-not-at-B)
    under resampling worlds with replacement, BOOT draws."""
    per_seed = []
    for s in map(str, R.PROBE_SEEDS):
        vals = [[v is not None for v in r["cells"][s][cell(cname)][key].values()] for r in rs]
        n = len(vals)
        stats = []
        for _ in range(BOOT):
            idx = rng.integers(0, n, n)
            flat = [x for i in idx for x in vals[i]]
            stats.append(sum(flat) / len(flat))
        per_seed.append(float(np.std(stats)))
    return float(np.mean(per_seed))


def fa_bootstrap_se(rs, cname, cls, rng):
    per_seed = []
    for s in map(str, R.PROBE_SEEDS):
        n = len(rs)
        runs = np.array([r["cells"][s][cell(cname)]["fa"][cls] for r in rs], float)
        ticks = np.array([r["observer_ticks"][cls] for r in rs], float)
        stats = []
        for _ in range(BOOT):
            idx = rng.integers(0, n, n)
            stats.append(runs[idx].sum() / ticks[idx].sum() * 1e4 if ticks[idx].sum() else 0.0)
        per_seed.append(float(np.std(stats)))
    return float(np.mean(per_seed))


def r5(recs, tuning_recs):
    """The picked cell on the confirming half, beside the tuning half's own
    figures (recomputed here from the same reader; `reads/ladder.json`
    carries the gated ones) and the flag at +- 2 world-bootstrap SE."""
    rng = np.random.default_rng(BOOT_SEED)
    conf = group_recs(recs, "confirming")
    tun = group_recs(tuning_recs, "tuning")
    out = {"cell": cell("pick"), "pick": PICK, "boot": BOOT, "groups": {}, "false_alarms": {}, "flags": []}
    for name in sorted(set(conf) | set(tun)):
        arm, st = name.split("-")
        g = {"arm": arm, "stratum": st, "primary": L.PRIMARY.get(st) == arm,
             "confirming": {"friend_episodes": len(conf.get(name, []))}, "tuning": {"friend_episodes": len(tun.get(name, []))}}
        if name in conf:
            g["confirming"].update(L.stratum_cell(conf[name], cell("pick"), with_sight=arm != "T"))
            g["confirming"]["length_median"] = L._median([r["length"] for r in conf[name]])
        if name in tun:
            g["tuning"].update(L.stratum_cell(tun[name], cell("pick"), with_sight=arm != "T"))
            g["tuning"]["length_median"] = L._median([r["length"] for r in tun[name]])
        if name in conf and name in tun:
            for key, col in (("latency", "detected"), ("lead_not_at_offset_B", "anticipated_run_not_at_offset_B")):
                if g["tuning"].get(col) is None or g["confirming"].get(col) is None:
                    continue
                se = world_bootstrap_se(tun[name], "pick", key, rng)
                t, c = g["tuning"][col]["mean"], g["confirming"][col]["mean"]
                flag = abs(c - t) > 2 * se
                g.setdefault("se", {})[col] = {"tuning_se": round(se, 4), "band": [round(t - 2 * se, 4), round(t + 2 * se, 4)], "confirming": c, "flag": flag}
                if flag:
                    out["flags"].append({"group": name, "column": col, "tuning": t, "confirming": c, "se": round(se, 4)})
        out["groups"][name] = g
    for arm in ("T", "E", "N"):
        cr = [r for r in recs if r["arm"] == arm and r["half"] == "confirming"]
        tr = [r for r in tuning_recs if r["arm"] == arm and r["half"] == "tuning"]
        fc, ft = L.false_alarm_cell(cr, cell("pick")), L.false_alarm_cell(tr, cell("pick"))
        row = {}
        for cls in L.FA_CLASSES:
            se = fa_bootstrap_se(tr, "pick", cls, rng) if ft[cls]["per_10k_ticks"] else None
            t = ft[cls]["per_10k_ticks"]["mean"] if ft[cls]["per_10k_ticks"] else None
            c = fc[cls]["per_10k_ticks"]["mean"] if fc[cls]["per_10k_ticks"] else None
            flag = bool(se is not None and c is not None and abs(c - t) > 2 * se)
            row[cls] = {"tuning": ft[cls], "confirming": fc[cls], "tuning_se": None if se is None else round(se, 4), "flag": flag}
            if flag:
                out["flags"].append({"group": f"{arm} false alarms", "column": cls, "tuning": t, "confirming": c, "se": round(se, 4)})
        out["false_alarms"][arm] = row
    return out


def r6(recs):
    out = {}
    for arm in ("T", "E", "N"):
        rs = [r for r in recs if r["arm"] == arm]
        per = {}
        for s in map(str, R.PROBE_SEEDS):
            tot = sum(r["which_need"][s]["samples"] for r in rs)
            at90 = sum(r["which_need"][s]["named_at90"] for r in rs)
            msk = sum(r["which_need"][s]["named_masked"] or 0 for r in rs) if arm != "T" else None
            pn = {}
            for r in rs:
                for nm, (n, h) in r["which_need"][s]["per_masked_need"].items():
                    d = pn.setdefault(nm, [0, 0])
                    d[0] += n
                    d[1] += h
            per[s] = {"samples": tot, "named_at90": at90 / tot if tot >= MIN_N else None,
                      "named_masked": (msk / tot if tot >= MIN_N else None) if arm != "T" else None,
                      "per_masked_need": {nm: {"samples": n, "accuracy": h / n if n >= MIN_N else None} for nm, (n, h) in pn.items()}}
        out[arm] = {"samples": per["1"]["samples"], "named_at90": msd([per[s]["named_at90"] for s in per]),
                    "named_masked": msd([per[s]["named_masked"] for s in per]) if arm != "T" else None,
                    "per_masked_need": {nm: {"samples": per["1"]["per_masked_need"][nm]["samples"],
                                             "accuracy": msd([per[s]["per_masked_need"].get(nm, {}).get("accuracy") for s in per])}
                                        for nm in per["1"]["per_masked_need"]},
                    "per_seed": per}
    return out


def r7(recs):
    out = {}
    for arm in ("E", "N"):
        eps = [(r, e) for r in recs if r["arm"] == arm for e in r["later_episodes"]]
        rows = {"episodes_ordinal_2_up": len(eps), "released_with_crossing": sum(1 for _r, e in eps if e["crossing"] is not None),
                "unreleased": sum(1 for _r, e in eps if not e["released"]), "bands": {}}
        for lo, hi in GAP_BANDS:
            sel = [(r, e) for r, e in eps if lo <= e["gap"] < hi and e["crossing"] is not None]
            if not sel:
                continue
            band = {"episodes": len(sel), "observer_episodes": 4 * len(sel), "length_median": L._median([e["length"] for _r, e in sel]),
                    "H_since_onset_median": L._median([e["H_since_onset"] for _r, e in sel]),
                    "in_sight_share": sum(e["in_sight"] for _r, e in sel) / (4 * len(sel))}
            for cname in ("reg", "pick"):
                per = {}
                for s in map(str, R.PROBE_SEEDS):
                    lats = [v for _r, e in sel for v in e["latency"][s][cname].values()]
                    det = [v for v in lats if v is not None]
                    per[s] = {"detected": len(det) / len(lats), "median_latency": L._median(det)}
                band[cname] = {k: msd([per[s][k] for s in per]) for k in ("detected", "median_latency")}
            rows["bands"][f"[{lo},{hi})"] = band
        out[arm] = rows
    return out


def r8(recs, probes):
    """Price: across the set per arm and half; the covered scout pairs
    against their controls; refused proposals toward the friend."""
    out = {"set": {}, "covered_scout": {}, "proposals": {}}
    for arm in ("T", "E", "N"):
        for half in ("tuning", "confirming", "pooled"):
            rs = [r for r in recs if r["arm"] == arm and (half == "pooled" or r["half"] == half)]
            hap = [np.mean(r["price"]["mean_happiness_per_seat"]) for r in rs]
            dis = [sum(r["price"]["distress_ticks_per_seat"]) / (4 * r["ticks"]) * 1000 for r in rs]
            grv = [sum(r["price"]["grave_ticks_per_seat"]) / (4 * r["ticks"]) * 1000 for r in rs]
            streak = [r["price"]["worst_streak_covered"] for r in rs]
            out["set"].setdefault(arm, {})[half] = {
                "worlds": len(rs), "covered_mean_happiness": {"mean": round(float(np.mean(hap)), 2), "sd": round(float(np.std(hap, ddof=1)), 2), "min": round(float(np.min(hap)), 2)},
                "distress_ticks_per_1000_covered_cat_ticks": round(float(np.mean(dis)), 2),
                "grave_ticks_per_1000_covered_cat_ticks": round(float(np.mean(grv)), 2),
                "worst_covered_streak": {"median": L._median(streak), "max": max(streak)},
                "worlds_with_covered_grave": sum(1 for r in rs if any(g > 0 for g in r["price"]["grave_ticks_per_seat"])),
                "scripted_grave_ticks_mean": round(float(np.mean([r["price"]["scripted_seat_grave_ticks"] for r in rs])), 1)}
            pr = [r["proposals"] for r in rs]
            tot = sum(v["toward_friend"] for p in pr for v in p.values())
            ref = sum(v["refused"] for p in pr for v in p.values())
            bym = sum(v["refused_by_mask"] for p in pr for v in p.values())
            ticks = sum(4 * r["ticks"] for r in rs)
            out["proposals"].setdefault(arm, {})[half] = {
                "worlds": len(rs), "toward_friend_per_1000": round(tot / ticks * 1000, 3), "refused_per_1000": round(ref / ticks * 1000, 3),
                "refused_by_mask_per_1000": round(bym / ticks * 1000, 3), "refused_other_per_1000": round((ref - bym) / ticks * 1000, 3),
                "refused_share_of_asks": round(ref / tot, 3) if tot else None,
                "refused_by_family": dict(sorted({k: sum(v["refused_by_family"].get(k, 0) for p in pr for v in p.values()) for k in PARTNERED}.items())),
                "worlds_over_100_refusals": sum(1 for p in pr if sum(v["refused"] for v in p.values()) > 100)}
    # the covered scout: pairs against their controls (step 4 raws)
    for arm in ("N", "E"):
        pairs = []
        for k in CS.BLOCKS:
            seeds = (CS.COVERED_BAND[0] + 2 * (k - 1), CS.COVERED_BAND[0] + 2 * (k - 1) + 1) if arm == "N" else tuple(R.arm_block("E", k)["seeds"][:2])
            for seed in seeds:
                wt = CS.load(CS.RAW / f"{arm}{k}" / f"streams-{seed}-teacher.npz")
                wn = CS.load(CS.RAW / f"{arm}{k}" / f"streams-{seed}-needy.npz")
                pt, pn = CS.seat_price(wt), CS.seat_price(wn)
                qt, qn = proposals_toward(wt, k - 1, wt["meta"]["applied_names"]), proposals_toward(wn, k - 1, wn["meta"]["applied_names"])
                pairs.append({"block": k, "seed": seed,
                              "d_mean_happiness": round(float(np.mean(pn["mean_happiness_per_seat"]) - np.mean(pt["mean_happiness_per_seat"])), 3),
                              "d_distress_ticks": int(sum(pn["distress_ticks_per_seat"]) - sum(pt["distress_ticks_per_seat"])),
                              "d_grave_ticks": int(sum(pn["grave_ticks_per_seat"]) - sum(pt["grave_ticks_per_seat"])),
                              "worst_streak": [pt["worst_streak_covered"], pn["worst_streak_covered"]],
                              "refused_toward_friend": [sum(v["refused"] for v in qt.values()), sum(v["refused"] for v in qn.values())],
                              "refused_by_mask_needy": sum(v["refused_by_mask"] for v in qn.values())})
        d = np.array([p["d_mean_happiness"] for p in pairs])
        out["covered_scout"][arm] = {"pairs": len(pairs), "d_mean_happiness_needy_minus_teacher": {"mean": round(float(d.mean()), 3), "sd": round(float(d.std(ddof=1)), 3), "min": float(d.min()), "max": float(d.max())},
                                     "d_distress_ticks_mean": round(float(np.mean([p["d_distress_ticks"] for p in pairs])), 1),
                                     "d_grave_ticks_mean": round(float(np.mean([p["d_grave_ticks"] for p in pairs])), 1),
                                     "refused_toward_friend_teacher_vs_needy": [sum(p["refused_toward_friend"][0] for p in pairs), sum(p["refused_toward_friend"][1] for p in pairs)],
                                     "refused_by_mask_needy": sum(p["refused_by_mask_needy"] for p in pairs), "per_pair": pairs}
    return out


# ---- predictions (§6) -------------------------------------------------------------------

def score(r1o, r2o, r3o):
    """P6, P7, P10, P11 as operationalised in §6, on all seeds."""
    out = {}
    # P7: arm T reset episodes, 0.10 / B = 0, detected inside both the episode and the first 100 ticks; seed mean >= 0.986
    w100 = r1o["reg"]["pooled"]["within100"]["mean"]
    out["P7"] = {"read": w100, "bar": PRED["P7"]["bar"], "met": w100 >= PRED["P7"]["bar"],
                 "anywhere_beside": r1o["reg"]["pooled"]["anywhere"]["mean"], "P_same_seed_within100": r1o["reg"]["pooled"]["P_within100"]["mean"]}
    # P10: clause 1 = P7's read with anywhere-in-episode detection; clause 2 = H2, H3, H4 within the comparator SD at 0.10 / B = 0
    anyw = r1o["reg"]["pooled"]["anywhere"]["mean"]
    c1 = anyw >= PRED["P7"]["bar"]
    c2 = {}
    for st, (comp, sd) in PRED["P10"].items():
        g = r2o["groups"].get(f"N-{st}")
        v = g["cells"]["reg"]["detected"]["mean"] if g else None
        c2[st] = {"read": v, "comparator": comp, "sd": sd, "within": None if v is None else abs(v - comp) <= sd}
    out["P10"] = {"clause1": {"read": anyw, "bar": PRED["P7"]["bar"], "holds": c1}, "clause2": c2,
                  "met": bool(c1 and all(x["within"] for x in c2.values()))}
    # P11: E-H1 at 0.10 / B = 0 inside [0.292, 0.432]
    g = r2o["groups"].get("E-H1")
    v = g["cells"]["reg"]["detected"]["mean"] if g else None
    out["P11"] = {"read": v, "band": [PRED["P11"]["lo"], PRED["P11"]["hi"]], "met": None if v is None else PRED["P11"]["lo"] <= v <= PRED["P11"]["hi"],
                  "above_splice_H50": None if v is None else v > PRED["P11"]["splice_H50"],
                  "by_splice_bin": {b: x["detected_reg"]["mean"] for b, x in (g.get("splice_bins", {}) if g else {}).items()},
                  "by_edge": g["cells"]["reg"].get("by_edge") if g else None}
    # P6: majority over 0.5 on the seed mean AND padded median lead >= 20, both
    p6 = r3o["P6"]["pooled"]
    maj, med = p6["majority"]["mean"], p6["median_lead_padded"]["mean"]
    out["P6"] = {"eligible_friend_episodes": r3o["P6"]["eligible_friend_episodes"], "majority": maj, "median_lead_padded": med,
                 "met": bool(maj > PRED["P6"]["majority"] and med >= PRED["P6"]["median_lead"]),
                 "per_stratum": {st: {"majority": x["majority"]["mean"], "median_lead_padded": x["median_lead_padded"]["mean"],
                                      "met": bool(x["majority"]["mean"] > PRED["P6"]["majority"] and x["median_lead_padded"]["mean"] >= PRED["P6"]["median_lead"])}
                                 for st, x in r3o["P6"]["per_stratum"].items()}}
    return out


# ---- driver -------------------------------------------------------------------------------

def read(progress=True):
    import torch
    torch.set_num_threads(1)
    probes = {s: R.load_probe(s)[:2] for s in R.PROBE_SEEDS}
    ws = worlds()
    t0 = time.time()
    recs = []
    for i, (arm, k, seed, ticks, path, half) in enumerate(ws):
        recs.append(world_record(arm, k, seed, ticks, path, half, probes))
        if progress and (i + 1) % 30 == 0:
            print(f"  {i + 1}/{len(ws)} worlds, {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
    precs = [p_record(k, seed, probes) for k in CS.BLOCKS for seed in R.arm_block("T", k)["seeds"]]
    tuning = [r for r in recs if r["half"] == "tuning"]
    out = {"pick": PICK, "cells": CELLS, "worlds": len(recs), "covered_cat_ticks": 0,
           "status": {arm: {h: {} for h in ("tuning", "confirming")} for arm in ("T", "E", "N")}}
    for r in recs:
        d = out["status"][r["arm"]][r["half"]]
        d[r["status"]] = d.get(r["status"], 0) + 1
    out["R5"] = r5(recs, tuning)
    out["R1"] = r1(recs, precs)
    out["R2"] = r2(recs)
    out["R3"] = r3(recs)
    out["R6"] = r6(recs)
    out["R7"] = r7(recs)
    out["R8"] = r8(recs, probes)
    out["predictions"] = score(out["R1"], out["R2"], out["R3"])
    out["seconds"] = round(time.time() - t0)
    out["records"] = recs
    out["P_records"] = precs
    return out


def _f(m, d=3):
    return L._f(m, d)


def md(out):
    S = []
    S += [f"## Step 7 reads (360 worlds; 0 covered cat-ticks; pick {out['pick']}; {out['seconds']} s)", "",
          f"First-episode status: {json.dumps(out['status'])}", ""]
    # R5
    r5o = out["R5"]
    S += [f"### R5 — the picked cell {r5o['cell']} on the confirming half, beside the tuning half (flag: outside tuning ± 2 world-bootstrap SE, {r5o['boot']} draws)", "",
          "| group | primary | episodes conf / tun | detected conf / tun | SE band (tun) | flag | median latency conf / tun | in sight conf / tun | fog conf / tun | anticipated not at B conf / tun | SE band | flag | median lead not at B conf / tun |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, g in r5o["groups"].items():
        c, t = g["confirming"], g["tuning"]
        se = g.get("se", {})
        d = se.get("detected", {})
        a = se.get("anticipated_run_not_at_offset_B", {})
        S.append(f"| {name} | {'yes' if g['primary'] else 'no'} | {c['friend_episodes']} / {t['friend_episodes']} | {_f(c.get('detected'))} / {_f(t.get('detected'))} | "
                 f"{d.get('band', '-')} | {'FLAG' if d.get('flag') else '-'} | {_f(c.get('median_latency'), 1)} / {_f(t.get('median_latency'), 1)} | "
                 f"{_f(c.get('detected_in_sight'))} / {_f(t.get('detected_in_sight'))} | {_f(c.get('detected_under_fog'))} / {_f(t.get('detected_under_fog'))} | "
                 f"{_f(c.get('anticipated_run_not_at_offset_B'))} / {_f(t.get('anticipated_run_not_at_offset_B'))} | {a.get('band', '-')} | {'FLAG' if a.get('flag') else '-'} | "
                 f"{_f(c.get('median_lead_run_not_at_offset_B'), 1)} / {_f(t.get('median_lead_run_not_at_offset_B'), 1)} |")
    S += ["", "| arm | class | confirming per 10k | tuning per 10k | tuning SE | flag |", "|---|---|---|---|---|---|"]
    for arm, row in r5o["false_alarms"].items():
        for cls, v in row.items():
            S.append(f"| {arm} | {cls} | {_f(v['confirming']['per_10k_ticks'], 2)} | {_f(v['tuning']['per_10k_ticks'], 2)} | {v['tuning_se']} | {'FLAG' if v['flag'] else '-'} |")
    S += ["", f"Flags: {r5o['flags'] or 'none'}", ""]
    # R1
    r1o = out["R1"]
    S += ["### R1 — tie-back (arm T reset episodes; P's same-seed covered figure beside)", "",
          "| cell | scope | friend episodes (T / P) | length median (T / P) | T anywhere | T within 100 | P anywhere | P within 100 |", "|---|---|---|---|---|---|---|---|"]
    for name in ("reg", "reg_b2"):
        for scope, row in r1o[name].items():
            S.append(f"| {cell(name)} | {scope} | {row['friend_episodes']} / {row['P_friend_episodes']} | {row['length_median']} / {row['P_length_median']} | "
                     f"{_f(row['anywhere'])} | {_f(row['within100'])} | {_f(row['P_anywhere'])} | {_f(row['P_within100'])} |")
    S += ["", f"Arm T worlds not grave at tick 0: {r1o['T_not_grave_at_tick0']}; P worlds without a reset episode: {r1o['P_not_reset']}", ""]
    # R2
    r2o = out["R2"]
    S += ["### R2 — history (first episodes, all seeds; splice comparators from DECLARATION §2; donors 5 / 40 / 238)", "",
          "| group | primary | episodes (tun + conf) | H min/median/max | length min/q1/median/q3/max | edge need/hap | m 1/2/3/4 | det 0.10 B0 | lat | in sight | fog | det 0.10 B2 | det need-edge / hap-edge (B0) | splice |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, g in r2o["groups"].items():
        c0, c2 = g["cells"]["reg"], g["cells"]["reg_b2"]
        ln = g["length"]
        be = c0.get("by_edge", {})
        S.append(f"| {name} | {'yes' if g['primary'] else 'no'} | {g['friend_episodes']} ({g['halves']['tuning']} + {g['halves']['confirming']}) | "
                 f"{g['H']['min']}/{g['H']['median']}/{g['H']['max']} | {ln['min']}/{ln['q1']}/{ln['median']}/{ln['q3']}/{ln['max']} | "
                 f"{g['edge']['need'] if g['edge'] else '-'}/{g['edge']['happiness'] if g['edge'] else '-'} | "
                 f"{'/'.join(str(g['m'][m]) for m in ('1', '2', '3', '4')) if g['m'] else '-'} | {_f(c0['detected'])} | {_f(c0['median_latency'], 1)} | "
                 f"{_f(c0.get('detected_in_sight'))} | {_f(c0.get('detected_under_fog'))} | {_f(c2['detected'])} | "
                 f"{_f(be.get('need'))} / {_f(be.get('happiness'))} | {SPLICE.get(g['stratum'], '-') if g['primary'] else '-'} |")
    e1 = r2o["groups"].get("E-H1", {})
    if e1.get("splice_bins"):
        S += ["", "E-H1 by the splice's bins (0.10 / B = 0): " + "; ".join(f"{b}: {x['friend_episodes']} episodes, {_f(x['detected_reg'])}" for b, x in e1["splice_bins"].items())
              + f" — splice H10 {SPLICE['H1']['H10']}, H20 {SPLICE['H1']['H20']}, H50 {SPLICE['H1']['H50']}"]
    S.append("")
    # R3
    r3o = out["R3"]
    S += ["### R3 — anticipation (first episodes; runs starting inside [mask onset, crossing); leads from the first such run)", "",
          "| group | cell | anticipated (all) | median lead | anticipated (not at B) | median lead | q1–q3 lead | per m: anticipated | per single masked need: anticipated |", "|---|---|---|---|---|---|---|---|---|"]
    for name, g in r3o["groups"].items():
        for cname in ("reg", "pick"):
            c = g["cells"][cname]
            pm = ", ".join(f"m{m} {_f(v['anticipated'])} (n {v['observer_episodes']})" for m, v in c["per_m"].items())
            pn = ", ".join(f"{nm} {_f(v['anticipated'])} (n {v['observer_episodes']})" for nm, v in c["per_need_single"].items())
            S.append(f"| {name} | {cell(cname)} | {_f(c['all']['anticipated'])} | {_f(c['all']['median_lead'], 1)} | {_f(c['not_at_B']['anticipated'])} | "
                     f"{_f(c['not_at_B']['median_lead'], 1)} | {_f(c['not_at_B']['q1_lead'], 1)}–{_f(c['not_at_B']['q3_lead'], 1)} | {pm} | {pn} |")
    offs = r3o["profile_offsets"]
    pick_offs = [-100, -50, -20, -10, -5, -2, -1, 0, 1, 2, 5, 10, 20]
    S += ["", "Mean probe logit aligned to the crossing (offset 0 = the crossing), from the mask onset, over observer-episodes (n at each offset in parentheses):", "",
          "| group | " + " | ".join(str(o) for o in pick_offs) + " |", "|---|" + "---|" * len(pick_offs)]
    for name, g in r3o["groups"].items():
        S.append(f"| {name} | " + " | ".join(f"{g['logit_profile_mean'][offs.index(o)]:.2f} ({g['logit_profile_n'][offs.index(o)]})" for o in pick_offs) + " |")
    p6 = r3o["P6"]
    S += ["", f"P6 read (arm N first episodes, m = 1, hidden need, in sight at the crossing; 0.10 / B = 0): eligible friend episodes {p6['eligible_friend_episodes']}; "
          f"pooled majority {_f(p6['pooled']['majority'])}, padded median lead {_f(p6['pooled']['median_lead_padded'], 1)}; per stratum "
          + "; ".join(f"{st}: majority {_f(x['majority'])}, padded median lead {_f(x['median_lead_padded'], 1)} (n obs-episodes {x['per_seed']['1']['observer_episodes']})" for st, x in p6["per_stratum"].items()), ""]
    # R6
    r6o = out["R6"]
    S += ["### R6 — which need (the scripted friend's grave samples in sight; argmax of the five predicted means)", "",
          "| arm | samples (seed 1) | names a masked need | names a need at 90 | per single masked need (samples, accuracy) |", "|---|---|---|---|---|"]
    for arm, g in r6o.items():
        pn = ", ".join(f"{nm} ({v['samples']}, {_f(v['accuracy'])})" for nm, v in g["per_masked_need"].items())
        S.append(f"| {arm} | {g['samples']} | {_f(g['named_masked'])} | {_f(g['named_at90'])} | {pn or '-'} |")
    S.append("")
    # R7
    r7o = out["R7"]
    S += ["### R7 — later episodes (ordinal 2 and up), by the gap since the last release; never pooled with first episodes", "",
          "| arm | gap band | episodes | length median | H since onset median | in sight share | det 0.10 B0 | lat | det pick | lat |", "|---|---|---|---|---|---|---|---|---|---|"]
    for arm, g in r7o.items():
        for band, b in g["bands"].items():
            S.append(f"| {arm} | {band} | {b['episodes']} | {b['length_median']} | {b['H_since_onset_median']} | {b['in_sight_share']:.2f} | "
                     f"{_f(b['reg']['detected'])} | {_f(b['reg']['median_latency'], 1)} | {_f(b['pick']['detected'])} | {_f(b['pick']['median_latency'], 1)} |")
        S.append(f"arm {arm}: {g['episodes_ordinal_2_up']} later windows, {g['released_with_crossing']} released with a crossing, {g['unreleased']} unreleased at the world's end")
    S.append("")
    # R8
    r8o = out["R8"]
    S += ["### R8 — price (covered seats)", "", "| arm | half | worlds | covered mean happiness (mean / SD / min) | distress ticks per 1,000 covered cat-ticks | grave ticks per 1,000 | worst covered streak median / max | worlds with covered grave | scripted grave ticks mean |",
          "|---|---|---|---|---|---|---|---|---|"]
    for arm, hs in r8o["set"].items():
        for half, v in hs.items():
            h = v["covered_mean_happiness"]
            S.append(f"| {arm} | {half} | {v['worlds']} | {h['mean']:.2f} / {h['sd']:.2f} / {h['min']:.2f} | {v['distress_ticks_per_1000_covered_cat_ticks']:.2f} | {v['grave_ticks_per_1000_covered_cat_ticks']:.2f} | "
                     f"{v['worst_covered_streak']['median']} / {v['worst_covered_streak']['max']} | {v['worlds_with_covered_grave']} | {v['scripted_grave_ticks_mean']} |")
    S += ["", "Refused proposals toward the scripted friend (a covered seat's chosen menu action naming the friend, not applied as proposed), per 1,000 covered cat-ticks:", "",
          "| arm | half | asks toward friend | refused | by the mask | other | refused share of asks | refused by family | worlds with over 100 refusals |", "|---|---|---|---|---|---|---|---|---|"]
    for arm, hs in r8o["proposals"].items():
        for half, v in hs.items():
            S.append(f"| {arm} | {half} | {v['toward_friend_per_1000']} | {v['refused_per_1000']} | {v['refused_by_mask_per_1000']} | {v['refused_other_per_1000']} | {v['refused_share_of_asks']} | {v['refused_by_family']} | {v['worlds_over_100_refusals']} |")
    S += ["", "Covered scout pairs (needy minus teacher, covered seats): "]
    for arm, g in r8o["covered_scout"].items():
        d = g["d_mean_happiness_needy_minus_teacher"]
        S.append(f"- arm {arm} ({g['pairs']} pairs): mean happiness {d['mean']} ± {d['sd']} (min {d['min']}, max {d['max']}); distress ticks {g['d_distress_ticks_mean']} per world; grave ticks {g['d_grave_ticks_mean']}; "
                 f"refused asks toward the friend, teacher vs needy worlds {g['refused_toward_friend_teacher_vs_needy']}, of the needy worlds' {g['refused_by_mask_needy']} attributed to the mask")
    S.append("")
    # predictions
    p = out["predictions"]
    S += ["### Predictions (§6), on all seeds", "",
          f"- P7: within-100 reset detection {_f({'mean': p['P7']['read'], 'sd': None})} against the bar {p['P7']['bar']} → {'MET' if p['P7']['met'] else 'NOT MET'} (anywhere {p['P7']['anywhere_beside']:.3f}; P's same-seed covered within-100 {p['P7']['P_same_seed_within100']:.3f})",
          f"- P10: clause 1 anywhere {p['P10']['clause1']['read']:.3f} ≥ {p['P10']['clause1']['bar']} → {p['P10']['clause1']['holds']}; clause 2 "
          + "; ".join(f"{st} {x['read']:.3f} vs {x['comparator']} ± {x['sd']} → {x['within']}" for st, x in p['P10']['clause2'].items()) + f" → {'MET' if p['P10']['met'] else 'NOT MET'}",
          f"- P11: E-H1 {p['P11']['read']:.3f} in {p['P11']['band']} → {'MET' if p['P11']['met'] else 'NOT MET'}; above the splice's H50 {p['P11']['splice_H50'] if 'splice_H50' in p['P11'] else PRED['P11']['splice_H50']}: {p['P11']['above_splice_H50']}; by bin {p['P11']['by_splice_bin']}; by edge {p['P11']['by_edge']}",
          f"- P6: eligible {p['P6']['eligible_friend_episodes']} friend episodes; majority {p['P6']['majority']:.3f} (> 0.5?), padded median lead {p['P6']['median_lead_padded']:.1f} (≥ 20?) → {'MET' if p['P6']['met'] else 'NOT MET'}; per stratum {p['P6']['per_stratum']}", ""]
    return "\n".join(S)


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
            Path(a.out).write_text(json.dumps(out, separators=(",", ":")) + "\n")
        print(md(out) if a.md else json.dumps({k: v for k, v in out.items() if k not in ("records", "P_records")}, indent=1))
