#!/usr/bin/env python3
"""Score the Biscuit 3.0 comfort sweep against prereg.md's pinned bars.

Reads results-raw/{run}-census.json (scene_census raws: events + needs
polls), {run}-world-polls.json (need_latency-shaped polls) and
{run}-final.json. Pools per arm over seeds, prints R1-R6 and P1-P5,
writes results-raw/score.json. Bar definitions transcribe prereg.md;
written before the first full run finished (2026-09-01).

usage: score.py [results-raw dir]
"""
import bisect
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "attn-cert-2026-08-14"))
sys.path.insert(0, str(HERE.parent / "needflow-lab-validation-2026-09-01"))
from need_latency import analyze  # noqa: E402
from scene_census import classify  # noqa: E402

RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "results-raw"
SEEDS = [20260911, 20260912]
COMFORT = ["c55", "c45", "c35", "c30", "w35"]
ARMS = [f"{c}-{s}" for c in COMFORT for s in ("off", "on")] + ["c32-off", "c28-off", "c25-off", "c20-off"]
# Addendum 2: c30 on the spec-047 binary, gate off (identity) and at 30.
ARMS += ["c30-off2", "c30-consent30"]
CONSENT_LINE = 30.0
REFUSAL_LINE = 0.035   # owner 2026-09-01: investigate above this, not a retrain gate
NON_PLAY = ("eat", "drink", "sleep", "cuddle", "bath")
NEEDS5 = ("eat", "drink", "sleep", "cuddle", "bath")
PARITY = 0.05  # Addendum 1 E1: Biscuit share>=30 within +0.05 of the roster's
TROUGH = 60.0  # Addendum 1 E4: happiness bar for a trough poll
BISCUIT = 2
FOOD = ("eat", "drink", "sleep")
ARMED = 30.0


# ---- primitives (guarded in test_score.py) --------------------------------

def series(polls):
    """kitty_id -> (ticks, [needs dict per tick]) from either poll shape."""
    out = defaultdict(lambda: ([], []))
    for p in sorted(polls, key=lambda p: p["tick"]):
        for k in p["kitties"]:
            out[k["id"]][0].append(p["tick"])
            out[k["id"]][1].append(k["needs"])
    return out


def interp_need(ser, kitty_id, tick, need):
    """Linear interpolation of one need between the bracketing polls;
    clamps to the nearest poll outside the polled range. Reliefs inside
    a gap are invisible here (poll-level approximation, prereg R3)."""
    ticks, needs = ser[kitty_id]
    i = bisect.bisect_left(ticks, tick)
    if i == 0:
        return needs[0][need]
    if i >= len(ticks):
        return needs[-1][need]
    if ticks[i] == tick:
        return needs[i][need]
    t0, t1 = ticks[i - 1], ticks[i]
    a, b = needs[i - 1][need], needs[i][need]
    return a + (b - a) * (tick - t0) / (t1 - t0)


def hungry_play(world_polls, kitty_id):
    """(hungry, total) play relief stamps for one seat: a stamp counts when
    last_relief.play advanced since the previous poll, hungry when eat or
    drink >= ARMED at the poll that shows it."""
    prev, hungry, total = None, 0, 0
    for p in sorted(world_polls, key=lambda p: p["tick"]):
        k = next(k for k in p["kitties"] if k["id"] == kitty_id)
        stamp = k["last_relief"].get("play")
        if prev is not None and stamp is not None and stamp > prev:
            total += 1
            if max(k["needs"]["eat"], k["needs"]["drink"]) >= ARMED:
                hungry += 1
        if stamp is not None:
            prev = stamp
    return hungry, total


def consent_blocked(ser, kitty_id, tick, line=CONSENT_LINE):
    """Spec 047's gate read off interpolated needs at a duet start: the
    partner's top NON-play need strictly over the line AND strictly over
    its own play need. Play on top (ties included) is never blocked."""
    top = max(interp_need(ser, kitty_id, tick, n) for n in NON_PLAY)
    return top > line and top > interp_need(ser, kitty_id, tick, "play")


def hungry_start(ser, kitty_id, tick):
    """R2 by scene: eat or drink interpolated >= ARMED at the scene start."""
    return max(interp_need(ser, kitty_id, tick, n) for n in ("eat", "drink")) >= ARMED


def refusal_tax(events, kitty_id, t0, t1):
    """R8 off the spec-046 ring: the seat's refused-into-idle rows
    (absorbed == false) in [t0, t1], total and by proposed action; a
    continuation re-proposal at a busy friend is enforced, hence absorbed,
    and never counts."""
    rows = [e for e in events if e["kitty_id"] == kitty_id and t0 <= e["tick"] <= t1
            and not e["absorbed"]]
    by = Counter(e["proposed"]["action"] + ("_" + e["proposed"]["target"]
                 if e["proposed"]["action"] == "play" and "target" in e["proposed"] else "")
                 for e in rows)
    return {"refused_idle": len(rows), "share_of_ticks": len(rows) / (t1 - t0 + 1),
            "by_action": dict(by)}


def low_need(ser, kitty_id, tick):
    return all(interp_need(ser, kitty_id, tick, n) < ARMED for n in FOOD)


# ---- per run --------------------------------------------------------------

def need_shares(world_polls, kitty_ids):
    """Addendum 1 R1: per need, mean level and share of polls at or above
    ARMED, pooled over the (poll, kitty) rows of kitty_ids."""
    vals = defaultdict(list)
    for p in world_polls:
        for k in p["kitties"]:
            if k["id"] in kitty_ids:
                for n in NEEDS5:
                    vals[n].append(k["needs"][n])
    return {n: {"mean": sum(v) / len(v), "share_armed": sum(x >= ARMED for x in v) / len(v)}
            for n, v in vals.items()}


def announce_share(world_polls, kitty_ids):
    """Addendum 1 R5: share of (poll, kitty) rows with a non-empty
    announce_armed, plus the per-need shares."""
    rows, any_, per = 0, 0, Counter()
    for p in world_polls:
        for k in p["kitties"]:
            if k["id"] in kitty_ids:
                rows += 1
                armed = k.get("announce_armed", [])
                any_ += bool(armed)
                per.update(armed)
    return {"any": any_ / rows, **{n: per[n] / rows for n in NEEDS5}}


def happiness_trough(world_polls, kitty_id, bar):
    """Addendum 1 E4: (worst poll, share of polls under bar) for one kitty."""
    h = [k["happiness"] for p in world_polls for k in p["kitties"] if k["id"] == kitty_id]
    return min(h), sum(x < bar for x in h) / len(h)


def load(run):
    c = json.loads((RAW / f"{run}-census.json").read_text())
    w = json.loads((RAW / f"{run}-world-polls.json").read_text())["polls"]
    f = json.loads((RAW / f"{run}-final.json").read_text())
    return c, w, f


def load_refusals(run):
    """Addendum 2 runs archive the deduped spec-046 ring; older runs have none."""
    p = RAW / f"{run}-refusals.json"
    return json.loads(p.read_text()) if p.exists() else None


def per_run(run):
    c, w, f = load(run)
    s = c["summary"]
    t0, t1 = s["t0"], s["t1"]
    ticks = t1 - t0 + 1
    ev = [e for e in c["events"] if e["started"] >= t0 and e["ended"] <= t1]
    ser = series(c["polls"])
    names = {k["id"]: k["name"] for k in f["world"]["kitties"]}
    per_seat = defaultdict(Counter)
    for e in ev:
        per_seat[e["kitty_id"]][classify(e)] += 1
    bplay = [e for e in ev if e["kitty_id"] == BISCUIT and classify(e).startswith("play")]
    lowneed = sum(low_need(ser, BISCUIT, e["started"]) for e in bplay)
    duets = [e for e in bplay if classify(e) == "play-duet"]
    pneed = [interp_need(ser, e["activity"]["target"]["id"], e["started"], "play") for e in duets]
    hungry, total = hungry_play(w, BISCUIT)
    blocked = sum(consent_blocked(ser, e["activity"]["target"]["id"], e["started"]) for e in duets)
    hs = Counter(classify(e) for e in bplay if hungry_start(ser, BISCUIT, e["started"]))
    refusals = load_refusals(run)
    lat = analyze(w)
    others = [i for i in names if i != BISCUIT]
    wf = f["welfare"]
    hap = defaultdict(list)
    for p in c["polls"]:
        for k in p["kitties"]:
            hap[k["id"]].append(k["happiness"])
    return {
        "run": run, "ticks": ticks, "polls_census": s["polls_in_window"], "polls_world": len(w),
        "watchdog": {"alarm_live": wf["alarm_live"], "entries": len(wf["entries"])},
        "names": names,
        "biscuit_play_per_1k": {c_: 1000.0 * per_seat[BISCUIT][c_] / ticks
                                for c_ in ("play-duet", "play-elem", "play-solo")},
        "biscuit_play_total_per_1k": 1000.0 * len(bplay) / ticks,
        "biscuit_lowneed_play_per_1k": 1000.0 * lowneed / ticks,
        "biscuit_duet_share": len(duets) / len(bplay) if bplay else None,
        "partner_play_need_at_duet_start": sum(pneed) / len(pneed) if pneed else None,
        "hungry_play": {"hungry": hungry, "total": total,
                        "share": hungry / total if total else None},
        "others_duet_per_1k": 1000.0 * sum(per_seat[i]["play-duet"] for i in others) / (ticks * len(others)),
        "others_duet_per_seat_per_1k": {names[i]: 1000.0 * per_seat[i]["play-duet"] / ticks for i in others},
        "latency": {names[i]: {n: lat["seats"][names[i]][n] for n in ("eat", "drink")}
                    for i in names},
        "demand_price": lat["demand_price_happiness_pts"],
        "happiness": {names[i]: sum(v) / len(v) for i, v in hap.items()},
        # Addendum 1
        "needs_biscuit": need_shares(w, {BISCUIT}),
        "needs_roster": need_shares(w, set(others)),
        "announce_biscuit": announce_share(w, {BISCUIT}),
        "announce_roster": announce_share(w, set(others)),
        "trough_biscuit": happiness_trough(w, BISCUIT, TROUGH),
        # Addendum 2
        "consent": {"blocked": blocked, "duets": len(duets),
                    "share": blocked / len(duets) if duets else None},
        "hungry_start_by_class": {c_: {"hungry": hs[c_], "n": per_seat[BISCUIT][c_]}
                                  for c_ in ("play-duet", "play-elem", "play-solo")},
        "refusal_tax": (refusal_tax(refusals["events"], BISCUIT, t0, t1)
                        | {"ring_gaps": refusals["ring_gaps"]}) if refusals else None,
    }


def food(r, seat, need, key):
    m = r["latency"][seat][need]
    if key == "above30":
        return m["time_above"][30]
    if key == "exc_per_1k":
        return 1000.0 * m["armed_excursions"] / r["ticks"]
    if key == "p50":
        return m.get("latency", {}).get("p50")


def pool(runs, fn):
    vals = [fn(r) for r in runs]
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else None


def main():
    runs = {}
    for a in ARMS:
        for s in SEEDS:
            run = f"{a}-{s}"
            if (RAW / f"{run}-census.json").exists():
                runs[(a, s)] = per_run(run)
    out = {"runs": {f"{a}-{s}": r for (a, s), r in runs.items()}, "arms": {}, "bars": {}}
    ok = lambda b: "PASS" if b else "MISS"

    print("== validity")
    for (a, s), r in runs.items():
        v = r["polls_census"] >= 1000 and r["polls_world"] >= 1000
        print(f"  {a}-{s}: census polls {r['polls_census']} world polls {r['polls_world']} "
              f"{ok(v)}  watchdog {r['watchdog']}")

    def arm(a):
        return [runs[(a, s)] for s in SEEDS if (a, s) in runs]

    def others_food(r, key, need="eat"):
        seats = [n for i, n in r["names"].items() if i != BISCUIT]
        return sum(food(r, n, need, key) for n in seats) / len(seats)

    A = {}
    print("== R1-R6 per arm (pooled; seeds in brackets)")
    for a in ARMS:
        rs = arm(a)
        if not rs:
            continue
        d = {
            "eat_above30": pool(rs, lambda r: food(r, "Biscuit", "eat", "above30")),
            "eat_exc_per_1k": pool(rs, lambda r: food(r, "Biscuit", "eat", "exc_per_1k")),
            "eat_p50": pool(rs, lambda r: food(r, "Biscuit", "eat", "p50")),
            "drink_above30": pool(rs, lambda r: food(r, "Biscuit", "drink", "above30")),
            "drink_exc_per_1k": pool(rs, lambda r: food(r, "Biscuit", "drink", "exc_per_1k")),
            "floor_eat_above30": pool(rs, lambda r: others_food(r, "above30")),
            "floor_eat_exc_per_1k": pool(rs, lambda r: others_food(r, "exc_per_1k")),
            "hungry_share": pool(rs, lambda r: r["hungry_play"]["share"]),
            "play_total": pool(rs, lambda r: r["biscuit_play_total_per_1k"]),
            "lowneed_play": pool(rs, lambda r: r["biscuit_lowneed_play_per_1k"]),
            "duet_share": pool(rs, lambda r: r["biscuit_duet_share"]),
            "partner_need": pool(rs, lambda r: r["partner_play_need_at_duet_start"]),
            "others_duet": pool(rs, lambda r: r["others_duet_per_1k"]),
            "biscuit_price": pool(rs, lambda r: r["demand_price"]["Biscuit"]),
            "biscuit_hap": pool(rs, lambda r: r["happiness"]["Biscuit"]),
            "roster_hap": pool(rs, lambda r: sum(r["happiness"].values()) / len(r["happiness"])),
            "needs_biscuit": {n: {k: pool(rs, lambda r: r["needs_biscuit"][n][k]) for k in ("mean", "share_armed")} for n in NEEDS5},
            "needs_roster": {n: {k: pool(rs, lambda r: r["needs_roster"][n][k]) for k in ("mean", "share_armed")} for n in NEEDS5},
            "announce_biscuit": {k: pool(rs, lambda r: r["announce_biscuit"][k]) for k in ("any",) + NEEDS5},
            "announce_roster": {k: pool(rs, lambda r: r["announce_roster"][k]) for k in ("any",) + NEEDS5},
            "trough_worst": min(r["trough_biscuit"][0] for r in rs),
            "trough_share": pool(rs, lambda r: r["trough_biscuit"][1]),
            "play_split": {c_: pool(rs, lambda r: r["biscuit_play_per_1k"][c_]) for c_ in ("play-duet", "play-elem", "play-solo")},
            "seeds": {r["run"]: {
                "parity": {n: r["needs_biscuit"][n]["share_armed"] - r["needs_roster"][n]["share_armed"] for n in NEEDS5},
                "trough": r["trough_biscuit"],
                "eat_above30": food(r, "Biscuit", "eat", "above30"),
                "eat_exc_per_1k": food(r, "Biscuit", "eat", "exc_per_1k"),
                "floor_eat_above30": others_food(r, "above30"),
                "floor_eat_exc_per_1k": others_food(r, "exc_per_1k"),
                "play_total": r["biscuit_play_total_per_1k"],
                "lowneed_play": r["biscuit_lowneed_play_per_1k"],
                "partner_need": r["partner_play_need_at_duet_start"],
                "others_duet": r["others_duet_per_1k"]} for r in rs},
        }
        A[a] = d
        print(f"  {a:8s} eat>30 {d['eat_above30']:.3f} (floor {d['floor_eat_above30']:.3f})"
              f"  exc/1k {d['eat_exc_per_1k']:.2f} (floor {d['floor_eat_exc_per_1k']:.2f})"
              f"  p50 {d['eat_p50']}  hungry {d['hungry_share']:.2f}"
              f"  play {d['play_total']:.1f} low-need {d['lowneed_play']:.1f}"
              f"  duet-share {d['duet_share']:.2f} partner-need {d['partner_need']:.1f}"
              f"  others-duet {d['others_duet']:.2f}  price {d['biscuit_price']:.2f}"
              f"  hap B {d['biscuit_hap']:.1f} roster {d['roster_hap']:.1f}")
    out["arms"] = A

    print("== Addendum 1 R1/R5: per-need share>=30 (mean), Biscuit | roster; announce any; trough")
    for a in ARMS:
        if a not in A:
            continue
        d = A[a]
        cells = "  ".join(f"{n} {d['needs_biscuit'][n]['share_armed']:.2f}({d['needs_biscuit'][n]['mean']:.1f})"
                          f"|{d['needs_roster'][n]['share_armed']:.2f}({d['needs_roster'][n]['mean']:.1f})" for n in NEEDS5)
        print(f"  {a:8s} {cells}  announce B {d['announce_biscuit']['any']:.2f} R {d['announce_roster']['any']:.2f}"
              f"  trough worst {d['trough_worst']:.1f} <{TROUGH:.0f} {d['trough_share']:.4f}"
              f"  play {d['play_split']['play-duet']:.1f}+{d['play_split']['play-elem']:.1f}+{d['play_split']['play-solo']:.1f}")

    base = A.get("c55-off")
    if not base:
        print("no baseline arm yet")
        (RAW / "score.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
        return

    def closure(d, key):
        gap = base[key] - base["floor_" + key]
        return (base[key] - d[key]) / gap if gap > 0 else None

    def closure_seed(a, key):
        # both seeds: each seed's own closure against ITS paired baseline seed
        vals = []
        for s in SEEDS:
            b = base["seeds"].get(f"c55-off-{s}")
            d = A[a]["seeds"].get(f"{a}-{s}")
            if b and d:
                gap = b[key] - b["floor_" + key]
                vals.append((b[key] - d[key]) / gap if gap > 0 else None)
        return vals

    print("== P1/P2/P4 per arm vs c55-off")
    bars = {}
    for a in ARMS:
        if a not in A or a == "c55-off":
            continue
        d = A[a]
        p1 = (d["lowneed_play"] >= 0.85 * base["lowneed_play"]
              and d["play_total"] >= 0.75 * base["play_total"])
        c_a, c_e = closure(d, "eat_above30"), closure(d, "eat_exc_per_1k")
        sa, se = closure_seed(a, "eat_above30"), closure_seed(a, "eat_exc_per_1k")
        p2 = (c_a is not None and c_e is not None and c_a >= 2 / 3 and c_e >= 2 / 3
              and all(v is not None and v >= 2 / 3 for v in sa + se))
        p4 = d["others_duet"] >= 0.85 * base["others_duet"]
        bars[a] = {"P1": p1, "P2": p2, "P4": p4, "closure_above30": c_a, "closure_exc": c_e,
                   "closure_seeds_above30": sa, "closure_seeds_exc": se}
        print(f"  {a:8s} P1 {ok(p1)} (low-need {d['lowneed_play'] / base['lowneed_play']:.2f}x,"
              f" total {d['play_total'] / base['play_total']:.2f}x)"
              f"  P2 {ok(p2)} (closure >30 {c_a if c_a is None else round(c_a, 2)}"
              f" exc {c_e if c_e is None else round(c_e, 2)}; seeds {[None if v is None else round(v, 2) for v in sa]}"
              f" {[None if v is None else round(v, 2) for v in se]})"
              f"  P4 {ok(p4)} ({d['others_duet'] / base['others_duet']:.2f}x)")

    if "c35-off" in A and "w35-off" in A:
        c35, w35 = A["c35-off"], A["w35-off"]
        ca, ce = closure(c35, "eat_above30"), closure(c35, "eat_exc_per_1k")
        wa, we = closure(w35, "eat_above30"), closure(w35, "eat_exc_per_1k")
        p3 = (ca is not None and wa is not None and wa >= ca - 0.25 * abs(ca)
              and ce is not None and we is not None and we >= ce - 0.25 * abs(ce)
              and w35["play_total"] >= c35["play_total"])
        bars["P3"] = {"pass": p3, "c35_closure": (ca, ce), "w35_closure": (wa, we),
                      "play": (c35["play_total"], w35["play_total"])}
        print(f"== P3 weights {ok(p3)}: closure c35 ({ca:.2f},{ce:.2f}) w35 ({wa:.2f},{we:.2f});"
              f" play c35 {c35['play_total']:.1f} w35 {w35['play_total']:.1f}")

    print("== Addendum 1 E1-E4 per arm (E1 parity on eat/drink/sleep/cuddle, pooled + both seeds)")
    c30 = A.get("c30-off")
    for a in ARMS:
        if a not in A or a == "c55-off":
            continue
        d = A[a]
        gaps = {n: d["needs_biscuit"][n]["share_armed"] - d["needs_roster"][n]["share_armed"] for n in NEEDS5}
        e1 = (all(gaps[n] <= PARITY for n in NEEDS5[:4])
              and all(all(s["parity"][n] <= PARITY for n in NEEDS5[:4]) for s in d["seeds"].values()))
        e2 = d["play_total"] / base["play_total"]
        e3 = d["others_duet"] >= 0.85 * base["others_duet"]
        e4 = c30 is not None and d["trough_share"] <= c30["trough_share"]
        bars[f"E-{a}"] = {"E1": e1, "E1_gaps": gaps, "E2_ratio": e2, "E3": e3, "E4": e4}
        print(f"  {a:8s} E1 {ok(e1)} gaps " + " ".join(f"{n} {gaps[n]:+.2f}" for n in NEEDS5)
              + f"  E2 {e2:.2f}x  E3 {ok(e3)}  E4 {ok(e4)} (<{TROUGH:.0f} share {d['trough_share']:.4f})")

    print("== P5 score-on vs score-off (comfort-matched)")
    for c in COMFORT:
        off, on = A.get(f"{c}-off"), A.get(f"{c}-on")
        if not (off and on):
            continue
        need_up = all(
            on["seeds"].get(f"{c}-on-{s}", {}).get("partner_need") is not None
            and off["seeds"].get(f"{c}-off-{s}", {}).get("partner_need") is not None
            and on["seeds"][f"{c}-on-{s}"]["partner_need"] > off["seeds"][f"{c}-off-{s}"]["partner_need"]
            for s in SEEDS)
        play_flat = abs(on["play_total"] - off["play_total"]) <= 0.10 * off["play_total"]
        supply = on["others_duet"] >= 0.85 * off["others_duet"]
        bars[f"P5-{c}"] = {"partner_need_up_both_seeds": need_up, "play_flat": play_flat,
                           "supply": supply, "pass": need_up and play_flat and supply}
        print(f"  {c}: partner-need {off['partner_need']:.1f} -> {on['partner_need']:.1f} {ok(need_up)}"
              f"  play {off['play_total']:.1f} -> {on['play_total']:.1f} {ok(play_flat)}"
              f"  others-duet {off['others_duet']:.2f} -> {on['others_duet']:.2f} {ok(supply)}"
              f"  duet-share {off['duet_share']:.2f} -> {on['duet_share']:.2f}")
    print("== Addendum 2 R7/R8/R2-split per arm (consent share pooled [seeds]; refusal tax; hungry starts by class)")
    for a in ARMS:
        if a not in A:
            continue
        rs = arm(a)
        cs = [r["consent"]["share"] for r in rs]
        A[a]["consent_share"] = pool(rs, lambda r: r["consent"]["share"])
        A[a]["consent_seeds"] = cs
        A[a]["refusal_tax"] = pool(rs, lambda r: (r["refusal_tax"] or {}).get("share_of_ticks"))
        A[a]["hungry_start"] = {c_: pool(rs, lambda r: r["hungry_start_by_class"][c_]["hungry"] * 1000.0 / r["ticks"])
                                for c_ in ("play-duet", "play-elem", "play-solo")}
        gaps = [r["refusal_tax"]["ring_gaps"] for r in rs if r["refusal_tax"]]
        tax = A[a]["refusal_tax"]
        print(f"  {a:14s} R7 {A[a]['consent_share']:.3f} {[round(c_, 3) for c_ in cs]}"
              f"  R8 tax {'n/a' if tax is None else f'{tax:.4f}'} ring-gaps {sum(len(g) for g in gaps)}"
              f"  hungry-start/1k duet {A[a]['hungry_start']['play-duet']:.1f}"
              f" elem {A[a]['hungry_start']['play-elem']:.1f} solo {A[a]['hungry_start']['play-solo']:.1f}")

    old30, off2, con = A.get("c30-off"), A.get("c30-off2"), A.get("c30-consent30")
    if old30 and off2:
        # C1: same config, new binary; pooled play +-5%, eat>=30 +-0.02
        c1 = (abs(off2["play_total"] - old30["play_total"]) <= 0.05 * old30["play_total"]
              and abs(off2["eat_above30"] - old30["eat_above30"]) <= 0.02)
        bars["C1"] = {"pass": c1, "play": (old30["play_total"], off2["play_total"]),
                      "eat_above30": (old30["eat_above30"], off2["eat_above30"])}
        print(f"== Addendum 2 C1 identity {ok(c1)}: play {old30['play_total']:.1f} -> {off2['play_total']:.1f}"
              f" ({off2['play_total'] / old30['play_total']:.3f}x)  eat>30 {old30['eat_above30']:.3f} -> {off2['eat_above30']:.3f}")
    if off2 and con:
        # C2-C5 read against the identity re-run on the same binary (C1 says
        # it stands in for the old c30-off); the old-arm ratio is printed too.
        c2 = all(c_ is not None and c_ < 0.05 for c_ in con["consent_seeds"]) and len(con["consent_seeds"]) == len(SEEDS)
        dd = con["play_split"]["play-duet"] / off2["play_split"]["play-duet"]
        pt = con["play_total"] / off2["play_total"]
        c3 = dd >= 0.90 and pt >= 0.96
        od = con["others_duet"] / off2["others_duet"]
        c4 = od >= 0.95
        g_off = {n: off2["needs_biscuit"][n]["share_armed"] - off2["needs_roster"][n]["share_armed"] for n in NEEDS5}
        g_con = {n: con["needs_biscuit"][n]["share_armed"] - con["needs_roster"][n]["share_armed"] for n in NEEDS5}
        widen = {n: g_con[n] - g_off[n] for n in NEEDS5}
        roster_d = {n: con["needs_roster"][n]["share_armed"] - off2["needs_roster"][n]["share_armed"] for n in NEEDS5}
        c5 = all(widen[n] <= 0.02 for n in NEEDS5) and all(abs(roster_d[n]) <= 0.02 for n in NEEDS5)
        bars.update({"C2": {"pass": c2, "consent_seeds": con["consent_seeds"], "off2_seeds": off2["consent_seeds"]},
                     "C3": {"pass": c3, "duet_ratio": dd, "play_ratio": pt,
                            "duets": (off2["play_split"]["play-duet"], con["play_split"]["play-duet"])},
                     "C4": {"pass": c4, "others_duet_ratio": od},
                     "C5": {"pass": c5, "gap_widening": widen, "roster_delta": roster_d},
                     "R8": {"off2": off2["refusal_tax"], "consent30": con["refusal_tax"]}})
        print(f"== Addendum 2 C2 consent {ok(c2)}: R7 {off2['consent_share']:.3f} -> {con['consent_share']:.3f}"
              f" seeds {[round(c_, 3) for c_ in con['consent_seeds']]}")
        print(f"== Addendum 2 C3 play kept {ok(c3)}: duets/1k {off2['play_split']['play-duet']:.1f} -> "
              f"{con['play_split']['play-duet']:.1f} ({dd:.3f}x; vs old c30-off "
              f"{con['play_split']['play-duet'] / old30['play_split']['play-duet'] if old30 else float('nan'):.3f}x)"
              f"  total play {off2['play_total']:.1f} -> {con['play_total']:.1f} ({pt:.3f}x)")
        print(f"== Addendum 2 C4 roster supply {ok(c4)}: others-duet {off2['others_duet']:.2f} -> {con['others_duet']:.2f} ({od:.3f}x)")
        print(f"== Addendum 2 C5 welfare {ok(c5)}: gap widening " + " ".join(f"{n} {widen[n]:+.3f}" for n in NEEDS5)
              + "  roster delta " + " ".join(f"{n} {roster_d[n]:+.3f}" for n in NEEDS5))
        t_off, t_con = off2["refusal_tax"], con["refusal_tax"]
        print(f"== Addendum 2 R8 refusal tax (investigate line {REFUSAL_LINE:.3f}): off2 "
              f"{'n/a' if t_off is None else f'{t_off:.4f}'} consent30 {'n/a' if t_con is None else f'{t_con:.4f}'}"
              f"  E1 gaps consent30 " + " ".join(f"{n} {g_con[n]:+.3f}" for n in NEEDS5))
    out["bars"] = bars
    (RAW / "score.json").write_text(json.dumps(out, indent=1, default=str) + "\n")


if __name__ == "__main__":
    main()
