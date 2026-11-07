#!/usr/bin/env python3
"""R-2 consumer reads and R-3 (DECLARATION.md §6), arm vs trunk on the recorded legs, by replay of every seat's
recorded actions (replay.py; the engine's ground truth and 068's tick_records, no policy forward, nothing covered
decides). Guard g7 covers the episode / p90 / UNDECIDABLE arithmetic below.

    read_r2.py episodes --seating p2u-act15-s1 --size 20 --out reads/r2/episodes-p2u-act15-s1-20.json   # one leg -> per-tick-derived records
    read_r2.py score    --out reads/r2.json [--md]                                                        # every recorded leg's records -> R-2a / R-2b / R-2c / R-3

R-2a (§9.12, the attributable outcome read): a friend's GRAVE EPISODE runs from her first tick in GRAVE (strata.stratum
on the engine's true needs / happiness) to her first tick out; episodes of the same friend separated by a gap under
k = 5 ticks MERGE (the strata have no hysteresis); an episode open at the leg's end (or an F-053 abort) is
RIGHT-CENSORED. Stratum = the need kind at / over 90 at entry (eat / drink / sleep / play / cuddle), else "happiness"
(hap < 45 with no need over the line). Relief source: SELF if the friend's activity at the exit tick is unpartnered,
OTHER if partnered (the state's partner flag). The latency read is the KAPLAN–MEIER p90 per stratum (censored episodes
enter as ≥ their observed length); min-n 200 episodes per stratum per seed-pooled cell else UNDECIDABLE; HELD iff the
arm's p90 ≤ 1.25 × the trunk's, else DEGRADED; "arm BEATS trunk" iff the arm's p90 is under the trunk's in all three
seeds (uniform) — magnitudes descriptive, never parity. Arm and trunk episodes are not paired.
R-2b (§9.11, the approach-propensity differential; THIS THREAD'S OPERATIONALISATION of the prereg's quantity, named
so in RESULTS): an ENCOUNTER opens when a friend j emits a want-message (tick_records' applied_message is a want_*
kind) at a tick t; it is GRAVE-KEYED if j is GRAVE at t, BENIGN if COMMON; its best-placed host is the nearest
unpartnered other cat by Manhattan distance at t. Over the next W = 30 ticks the host APPROACHES if its Manhattan
distance to j falls by ≥ 1 net, and PROPOSES if any of its chosen menu actions (the recorded acts; provenance policy)
names j (rest_with / sleep_with / groom / chase / play _kitty_<row of j in the host's view>).
Propensity = the share of encounters with approach (and, beside, with a proposal); the differential = grave-keyed over
benign; lift 1.5, min-n 200 per cell, fail-closed.
R-2c (F-033 / F-039's instrument, through tick_records): the refusal tax per seat = the share of ticks whose applied
action is not the proposed one, by category — VALIDATION (validated ≠ proposed: the proposal was illegal) and
APPLY (validated = proposed ≠ applied: consent / duration / needy law at the apply slot; `consent_declined` is not
separable natively in tick_records and is reported as part of APPLY) — arm NOT WORSE than trunk per category within the
10% relative tolerance.
R-3 (canalization watch): per-seat action-mix entropy (applied activity kinds, nats) and the rows' dispersion fields,
INVESTIGATE never a bar.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p2_common as C  # noqa: E402
import replay as RP  # noqa: E402
sys.path.insert(0, str(C.EXPTS / "minifriend-phase1-2026-10-22"))
import strata as S  # noqa: E402

MERGE_GAP = 5
MIN_N = 200
HELD_TOL = 1.25
LIFT = 1.5
WINDOW = 30
TAX_TOL = 1.10
NEEDS = ["eat", "drink", "sleep", "play", "cuddle", "bath"]
STRATA_R2A = ("eat", "drink", "sleep", "play", "cuddle", "happiness")
SEEDS = (1, 2, 4)
ARMS = ("act15", "act10", "nohead")
READS = HERE / "reads"


# ---------------------------------------------------------------- R-2a episodes

def grave_episodes(codes_j, exit_partnered_j, needs_j, hap_j, merge_gap=MERGE_GAP):
    """codes_j (T,) strata codes of one friend per tick; exit_partnered_j (T,) her partner flag per tick; needs_j
    (T, 6), hap_j (T,) her truth. Returns [{start, end (exclusive; T if censored), censored, latency, stratum,
    source}] with gaps under merge_gap merged."""
    T = len(codes_j)
    grave = np.asarray(codes_j) == S.GRAVE
    eps = []
    t = 0
    while t < T:
        if not grave[t]:
            t += 1
            continue
        start = t
        while t < T and grave[t]:
            t += 1
        eps.append([start, t])
    merged = []
    for s, e in eps:
        if merged and s - merged[-1][1] < merge_gap:
            merged[-1][1] = e
        else:
            merged.append([s, e])
    out = []
    for s, e in merged:
        censored = e >= T
        over = [NEEDS[i] for i in range(5) if needs_j[s, i] >= S.NEED_DISTRESS]
        stratum = over[0] if over else "happiness"
        out.append({"start": int(s), "end": int(e), "censored": bool(censored), "latency": int(e - s), "stratum": stratum,
                    "source": None if censored else ("other" if exit_partnered_j[e - 1] else "self")})
    return out


def km_quantile(latencies, censored, q=0.9):
    """Kaplan–Meier quantile: the smallest t with S(t) ≤ 1 − q; None when the curve never falls that far (too much
    censoring). Censored observations leave the risk set at their observed length without an event."""
    lat = np.asarray(latencies, np.float64)
    cen = np.asarray(censored, bool)
    if lat.size == 0:
        return None
    order = np.argsort(lat, kind="stable")
    lat, cen = lat[order], cen[order]
    n_at_risk = lat.size
    surv = 1.0
    i = 0
    while i < lat.size:
        t = lat[i]
        j = i
        d = c = 0
        while j < lat.size and lat[j] == t:
            if cen[j]:
                c += 1
            else:
                d += 1
            j += 1
        if d > 0:
            surv *= 1.0 - d / n_at_risk
            if surv <= 1.0 - q + 1e-12:
                return float(t)
        n_at_risk -= d + c
        i = j
    return None


def r2a_cell(episodes):
    """One cell (one seed's pooled episodes of one stratum): n, censored share, KM p90, other-relief share."""
    n = len(episodes)
    if n == 0:
        return {"n": 0, "state": "UNDECIDABLE"}
    lat = [e["latency"] for e in episodes]
    cen = [e["censored"] for e in episodes]
    other = [e["source"] == "other" for e in episodes if not e["censored"]]
    cell = {"n": n, "censored_share": float(np.mean(cen)), "p90": km_quantile(lat, cen), "median": km_quantile(lat, cen, 0.5),
            "other_relief_share": float(np.mean(other)) if other else None}
    cell["state"] = "UNDECIDABLE" if n < MIN_N else ("FLAGGED-CENSORING" if cell["censored_share"] > 0.10 else "READ")
    if cell["p90"] is None and n >= MIN_N:
        cell["state"] = "UNDECIDABLE (p90 never reached under censoring)"
    return cell


def held_or_degraded(arm_p90, trunk_p90, tol=HELD_TOL):
    if arm_p90 is None or trunk_p90 is None:
        return "UNDECIDABLE"
    return "HELD" if arm_p90 <= tol * trunk_p90 else "DEGRADED"


def beats(arm_p90_by_seed, trunk_p90_by_seed):
    """'arm BEATS trunk' iff the arm's p90 is under the trunk's in every one of the three seeds (all readable)."""
    vals = [(arm_p90_by_seed.get(k), trunk_p90_by_seed.get(k)) for k in SEEDS]
    if any(a is None or t is None for a, t in vals):
        return False
    return all(a < t for a, t in vals)


# ---------------------------------------------------------------- per-leg records (one replay per world)

def leg_records(seating, size, seed, root=None):
    """Replay one world of one leg -> the per-tick-derived records the reads need: the friends' strata codes, partner
    flags, truth, applied activity kinds, tick_records names, positions, messages."""
    rows, _h = RP.leg_rows(seating, size, root)
    row = rows[seed]
    T = row["ticks"]
    codes = np.zeros((T, C.ROSTER), np.int8)
    partnered = np.zeros((T, C.ROSTER), bool)
    needs = np.zeros((T, C.ROSTER, 6), np.float32)
    hap = np.zeros((T, C.ROSTER), np.float32)
    pos = np.zeros((T, C.ROSTER, 2), np.int16)
    activity = np.zeros((T, C.ROSTER), np.int8)
    msg = np.zeros((T, C.ROSTER), np.int16)
    menu_act = np.zeros((T, C.ROSTER), np.int16)
    applied_msg = np.empty((T, C.ROSTER), object)
    proposed = np.empty((T, C.ROSTER), object)
    validated = np.empty((T, C.ROSTER), object)
    applied = np.empty((T, C.ROSTER), object)
    world = C.config_world(C.LEG_TOML[size])["world"]
    W, H = world["width"], world["height"]
    for rec in RP.replay(RP.acts_path(seating, size, seed, root), C.LEG_TOML[size], check_row=row):
        t = rec["tick"]
        n_pre, h_pre, p_pre, a_pre, pr_pre, _pt, _d = rec["pre"]
        codes[t] = S.stratum(n_pre, h_pre)            # the friend's state entering t (the view the acts were chosen on)
        n_post, h_post, p_post, a_post, pr_post, _pt2, _d2 = rec["post"]
        partnered[t] = pr_post                         # the state after the tick's step (exit-tick partner flag)
        needs[t], hap[t] = n_pre, h_pre
        pos[t] = np.rint(p_post * [W, H]).astype(np.int16)
        activity[t] = a_post
        msg[t] = rec["acts"][:, 1]
        menu_act[t] = rec["acts"][:, 0]
        for i, a in enumerate(rec["names"]):
            r = rec["recs"][a]
            proposed[t, i], validated[t, i], applied[t, i] = r["proposed_action_name"], r["validated_action_name"], r["applied_action_name"]
            applied_msg[t, i] = r["applied_message"]
    return {"seating": seating, "size": size, "seed": seed, "ticks": T, "codes": codes, "partnered": partnered, "needs": needs,
            "hap": hap, "pos": pos, "activity": activity, "msg": msg, "menu_act": menu_act, "applied_msg": applied_msg,
            "proposed": proposed, "validated": validated, "applied": applied, "seats": row["seats"], "aborted": "aborted_streak" in row}


def episodes_of(rec):
    """R-2a episodes of every friend of one world."""
    out = []
    for j in range(C.ROSTER):
        for e in grave_episodes(rec["codes"][:, j], rec["partnered"][:, j], rec["needs"][:, j], rec["hap"][:, j]):
            e["friend"] = j
            out.append(e)
    return out


def encounters_of(rec, window=WINDOW):
    """R-2b encounters of one world: [{t, friend, keyed (grave/benign/other), host, approach, proposal}]."""
    import cloudkitty
    menu = list(cloudkitty.ACTION_MENU)
    T = rec["ticks"]
    out = []
    for t in range(T - window):
        for j in range(C.ROSTER):
            m = rec["applied_msg"][t, j]
            if not (isinstance(m, str) and m.startswith("want_")):
                continue
            code = rec["codes"][t, j]
            keyed = "grave" if code == S.GRAVE else ("benign" if code == S.COMMON else "adjacent")
            d0 = np.abs(rec["pos"][t] - rec["pos"][t, j]).sum(1)
            cands = [k for k in range(C.ROSTER) if k != j and not rec["partnered"][t, k]]
            if not cands:
                continue
            host = min(cands, key=lambda k: (d0[k], k))
            d_end = int(np.abs(rec["pos"][t + window, host] - rec["pos"][t + window, j]).sum())
            row_of_j = [x for x in range(C.ROSTER) if x != host].index(j)
            tag = f"_kitty_{row_of_j}"
            prop = any(menu[int(a)].endswith(tag) for a in rec["menu_act"][t + 1:t + 1 + window, host])
            out.append({"t": t, "friend": j, "keyed": keyed, "host": host, "want": m, "approach": bool(d_end <= int(d0[host]) - 1), "proposal": bool(prop)})
    return out


def tax_of(rec):
    """R-2c per seat: ticks, validation-refused share, apply-refused share."""
    out = []
    for i in range(C.ROSTER):
        p, v, a = rec["proposed"][:, i], rec["validated"][:, i], rec["applied"][:, i]
        ok = np.array([x is not None for x in p])
        val_ref = np.array([(pp is not None and vv is not None and pp != vv) for pp, vv in zip(p, v)])
        app_ref = np.array([(pp is not None and vv is not None and aa is not None and pp == vv and vv != aa) for pp, vv, aa in zip(p, v, a)])
        out.append({"seat": i, "ticks": int(ok.sum()), "validation": float(val_ref[ok].mean()) if ok.any() else None,
                    "apply": float(app_ref[ok].mean()) if ok.any() else None})
    return out


def mix_entropy(rec):
    """R-3 per seat: entropy (nats) of the applied activity kinds over the leg."""
    out = []
    for i in range(C.ROSTER):
        c = np.bincount(rec["activity"][:, i], minlength=7).astype(np.float64)
        p = c / c.sum()
        out.append(float(-(p[p > 0] * np.log(p[p > 0])).sum()))
    return out


def read_episodes(seating, size, root=None, seeds=None):
    """Every world of one leg -> the derived records (episodes, encounters, tax, mix), JSON-serialisable."""
    rows, header = RP.leg_rows(seating, size, root)
    out = {"seating": seating, "size": size, "seats": header["seats"], "worlds": {}}
    for seed in sorted(rows) if seeds is None else seeds:
        rec = leg_records(seating, size, seed, root)
        out["worlds"][str(seed)] = {"episodes": episodes_of(rec), "encounters": encounters_of(rec), "tax": tax_of(rec),
                                    "mix_entropy": mix_entropy(rec), "aborted": rec["aborted"], "ticks": rec["ticks"]}
    return out


# ---------------------------------------------------------------- scoring across legs

def pool(ep_json, key):
    return [x for w in ep_json["worlds"].values() for x in w[key]]


def score_r2a(arm_eps_by_seed, trunk_eps_by_seed):
    """arm_eps_by_seed / trunk_eps_by_seed: {seed: [episodes]} (uniform legs pooled over 30 worlds). Per stratum: the
    per-seed cells, HELD / DEGRADED per seed against the trunk seed, beats."""
    out = {}
    for st in STRATA_R2A:
        a_cells = {k: r2a_cell([e for e in arm_eps_by_seed.get(k, []) if e["stratum"] == st]) for k in SEEDS}
        t_cells = {k: r2a_cell([e for e in trunk_eps_by_seed.get(k, []) if e["stratum"] == st]) for k in SEEDS}
        a_other = {k: r2a_cell([e for e in arm_eps_by_seed.get(k, []) if e["stratum"] == st and e["source"] == "other"]) for k in SEEDS}
        t_other = {k: r2a_cell([e for e in trunk_eps_by_seed.get(k, []) if e["stratum"] == st and e["source"] == "other"]) for k in SEEDS}
        verdict = {k: (held_or_degraded(a_cells[k].get("p90"), t_cells[k].get("p90")) if a_cells[k]["state"] == "READ" and t_cells[k]["state"] == "READ" else "UNDECIDABLE") for k in SEEDS}
        out[st] = {"arm": {str(k): a_cells[k] for k in SEEDS}, "trunk": {str(k): t_cells[k] for k in SEEDS},
                   "held": {str(k): verdict[k] for k in SEEDS},
                   "beats": beats({k: a_cells[k].get("p90") if a_cells[k]["state"] == "READ" else None for k in SEEDS},
                                  {k: t_cells[k].get("p90") if t_cells[k]["state"] == "READ" else None for k in SEEDS}),
                   "other_relief": {"arm": {str(k): a_other[k] for k in SEEDS}, "trunk": {str(k): t_other[k] for k in SEEDS},
                                    "beats": beats({k: a_other[k].get("p90") if a_other[k]["state"] == "READ" else None for k in SEEDS},
                                                   {k: t_other[k].get("p90") if t_other[k]["state"] == "READ" else None for k in SEEDS})}}
    return out


def score_r2b(encounters):
    """Propensity per key and the grave-over-benign differential (lift ≥ 1.5, min-n 200 per cell, fail-closed)."""
    out = {}
    for key in ("grave", "benign"):
        es = [e for e in encounters if e["keyed"] == key]
        out[key] = {"n": len(es), "approach": float(np.mean([e["approach"] for e in es])) if es else None,
                    "proposal": float(np.mean([e["proposal"] for e in es])) if es else None}
    g, b = out["grave"], out["benign"]
    if g["n"] < MIN_N or b["n"] < MIN_N:
        out["differential"] = {"state": "INSUFFICIENT"}
    else:
        lift = (g["approach"] / b["approach"]) if b["approach"] else float("inf")
        out["differential"] = {"state": "READ", "lift_approach": lift, "clears": bool(lift >= LIFT),
                               "lift_proposal": (g["proposal"] / b["proposal"]) if b["proposal"] else None}
    return out


def score_r2c(arm_tax, trunk_tax):
    """Per category: arm mean share over seats and worlds vs trunk; NOT WORSE iff arm ≤ 1.10 × trunk."""
    out = {}
    for cat in ("validation", "apply"):
        a = float(np.mean([t[cat] for t in arm_tax if t[cat] is not None]))
        b = float(np.mean([t[cat] for t in trunk_tax if t[cat] is not None]))
        out[cat] = {"arm": a, "trunk": b, "not_worse": bool(a <= TAX_TOL * b + 1e-12)}
    return out


def load_ep(seating, size):
    p = READS / "r2" / f"episodes-{seating}-{size}.json"
    return json.loads(p.read_text()) if p.exists() else None


def score(sizes=(20, 40, 100)):
    out = {}
    for size in sizes:
        trunk = {k: load_ep(f"g2-s{k}", size) for k in SEEDS}
        if any(v is None for v in trunk.values()):
            out[str(size)] = {"state": f"trunk uniform legs not re-recorded at {size} (replay needs the recorded acts; the battery rows carry none) — R-2 waits"}
            continue
        res = {}
        for arm in ARMS:
            legs = {k: load_ep(f"p2u-{arm}-s{k}", size) for k in SEEDS}
            if any(v is None for v in legs.values()):
                res[arm] = {"state": "legs incomplete"}
                continue
            res[arm] = {"r2a": score_r2a({k: pool(legs[k], "episodes") for k in SEEDS}, {k: pool(trunk[k], "episodes") for k in SEEDS}),
                        "r2b": {"arm": score_r2b([e for k in SEEDS for e in pool(legs[k], "encounters")]),
                                "trunk": score_r2b([e for k in SEEDS for e in pool(trunk[k], "encounters")])},
                        "r2c": score_r2c([t for k in SEEDS for t in pool(legs[k], "tax")], [t for k in SEEDS for t in pool(trunk[k], "tax")]),
                        "r3_mix_entropy": {"arm": float(np.mean([h for k in SEEDS for h in pool(legs[k], "mix_entropy")])),
                                           "trunk_seeds": {str(k): float(np.mean(pool(trunk[k], "mix_entropy"))) for k in SEEDS}}}
        out[str(size)] = res
    return out


def md(out):
    L = ["# R-2 / R-3 reads", ""]
    for size, res in out.items():
        L += [f"## {size}×{size}", ""]
        if "state" in res:
            L.append(res["state"])
            continue
        for arm, r in res.items():
            if "state" in r:
                L.append(f"- {arm}: {r['state']}")
                continue
            L += [f"### {arm}", "", "| stratum | arm p90 by seed | trunk p90 by seed | held | beats | other-relief beats |", "|---|---|---|---|---|---|"]
            for st, v in r["r2a"].items():
                ap = {k: (c.get("p90"), c["n"]) for k, c in v["arm"].items()}
                tp = {k: (c.get("p90"), c["n"]) for k, c in v["trunk"].items()}
                L.append(f"| {st} | {ap} | {tp} | {v['held']} | {v['beats']} | {v['other_relief']['beats']} |")
            L += ["", f"R-2b: arm {json.dumps(r['r2b']['arm']['differential'])} / trunk {json.dumps(r['r2b']['trunk']['differential'])}",
                  f"R-2c: {json.dumps(r['r2c'])}", f"R-3 action-mix entropy: {json.dumps(r['r3_mix_entropy'])}", ""]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["episodes", "score"])
    ap.add_argument("--seating")
    ap.add_argument("--size", type=int)
    ap.add_argument("--seeds", default=None, help="episodes: comma list of worlds (default all 30)")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--root", type=Path, default=None)
    a = ap.parse_args()
    if a.cmd == "episodes":
        seeds = None if a.seeds is None else [int(s) for s in a.seeds.split(",")]
        out = read_episodes(a.seating, a.size, a.root, seeds)
        p = a.out or READS / "r2" / f"episodes-{a.seating}-{a.size}.json"
    else:
        out = score()
        p = a.out or READS / "r2.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=1) + "\n")
    if a.md and a.cmd == "score":
        p.with_suffix(".md").write_text(md(out))
        print(md(out))
    else:
        print(f"wrote {p}")


if __name__ == "__main__":
    main()
