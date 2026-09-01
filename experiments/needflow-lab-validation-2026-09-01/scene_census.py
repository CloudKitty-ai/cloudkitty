#!/usr/bin/env python3
"""Scene census for the needflow lab validation (prereg.md — read it first).

Polls one lab server's /events/activity and /world for a fixed tick
window and reports scenes per 1k cat-ticks by needflow's classes, plus
time-mean needs and happiness. Scenes are read off /events/activity
(F-031: the only honest span source; `activity.state` is a one-tick
flag for play/eat/drink), deduped by (kitty_id, started, ended), and
counted in the window iff `started >= t0 and ended <= t1`.

Classes (needflow RESULTS.md column names):
  rest        resting  partnered: with_friend present at the end OR any
                       tier tick counted (the engine drops a wandered-off
                       partner to None, clock untouched — action.rs
                       Resting arm — so end-state alone under-counts)
  rest-solo   resting  never partnered: with_friend absent AND both tiers 0
                       (posture-only; reported)
  cosleep     sleeping partnered, same rule
  sleep-solo  sleeping never partnered
  groom-other grooming target present
  groom-self  grooming target absent
  play-duet   playing  target.target == "kitty"
  play-elem   playing  target.target == "element"   (critter/bug hunting —
                                                    outside needflow's model)
  play-solo   playing  target absent
  eat / drink                                        (reported)

Rest tiers (spec 041 FR-011): `mutual_ticks` / `drip_ticks` on a rest
event are the tiers' emit-proofs (F-029). Absent fields read as zero.

usage: scene_census.py --base URL --ticks N [--interval S] [--raw PATH]
"""
import argparse
import json
import statistics as st
import time
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

CLASSES = ["rest", "rest-solo", "cosleep", "sleep-solo", "groom-other",
           "groom-self", "play-duet", "play-elem", "play-solo", "eat",
           "drink"]
NEEDS = ["eat", "drink", "sleep", "play", "cuddle", "bath"]


def classify(e):
    """needflow class for one /events/activity event."""
    activity = e["activity"]
    state = activity.get("state")
    partnered = (activity.get("with_friend") is not None
                 or e.get("mutual_ticks", 0) + e.get("drip_ticks", 0) > 0)
    if state == "resting":
        return "rest" if partnered else "rest-solo"
    if state == "sleeping":
        return "cosleep" if partnered else "sleep-solo"
    if state == "grooming":
        return "groom-other" if activity.get("target") is not None else "groom-self"
    if state == "playing":
        tgt = activity.get("target")
        if tgt is None:
            return "play-solo"
        return "play-duet" if tgt.get("target") == "kitty" else "play-elem"
    if state in ("eating", "drinking"):
        return "eat" if state == "eating" else "drink"
    return f"other:{state}"


def span(e):
    return e["ended"] - e["started"] + 1  # INCLUSIVE (events.rs)


def summarize(events, polls, t0, t1, n_kitties, windows=4):
    """Aggregate deduped events + polls over the measured tick window.

    `events`: iterable of /events/activity objects; `polls`: list of
    {"tick", "kitties": [{"needs", "happiness"}...]} samples. Returns the
    dict written as the raw's "summary".
    """
    inwin = [e for e in events if e["started"] >= t0 and e["ended"] <= t1]
    ticks = t1 - t0 + 1
    cat_ticks = ticks * n_kitties
    counts = Counter(classify(e) for e in inwin)
    spans = defaultdict(list)
    for e in inwin:
        spans[classify(e)].append(span(e))
    per_1k = {c: 1000.0 * counts.get(c, 0) / cat_ticks for c in CLASSES}
    # Sustained: rest scenes per equal sub-window of the measured range.
    edges = [t0 + i * ticks // windows for i in range(windows)] + [t1 + 1]
    rest_by_window = [
        sum(1 for e in inwin if classify(e) == "rest"
            and edges[i] <= e["started"] < edges[i + 1])
        for i in range(windows)]
    rest_events = [e for e in inwin if classify(e) == "rest"]
    tiers = {
        "mutual_emitting": sum(1 for e in rest_events if e.get("mutual_ticks", 0) > 0),
        "drip_emitting": sum(1 for e in rest_events if e.get("drip_ticks", 0) > 0),
        "rest_events": len(rest_events),
    }
    inpolls = [p for p in polls if t0 <= p["tick"] <= t1]
    need_means = {n: st.fmean(k["needs"][n] for p in inpolls for k in p["kitties"])
                  for n in NEEDS} if inpolls else {}
    happiness = st.fmean(k["happiness"] for p in inpolls for k in p["kitties"]) \
        if inpolls else None
    return {
        "t0": t0, "t1": t1, "ticks": ticks, "n_kitties": n_kitties,
        "cat_ticks": cat_ticks, "events_in_window": len(inwin),
        "counts": dict(counts), "per_1k_cat_ticks": per_1k,
        "mean_span": {c: st.fmean(v) for c, v in spans.items()},
        "rest_by_window": rest_by_window, "rest_tiers": tiers,
        "play_total_per_1k": per_1k["play-duet"] + per_1k["play-elem"] + per_1k["play-solo"],
        "cosleep_to_solo": (per_1k["cosleep"] / per_1k["sleep-solo"]
                            if per_1k["sleep-solo"] else None),
        "need_means": need_means, "happiness_mean": happiness,
        "polls_in_window": len(inpolls),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", required=True)
    p.add_argument("--ticks", type=int, required=True,
                   help="measured window length in ticks, from the first polled tick")
    p.add_argument("--interval", type=float, default=0.5)
    p.add_argument("--raw", default=None)
    a = p.parse_args()

    def get(path):
        with urllib.request.urlopen(f"{a.base}{path}", timeout=10) as r:
            return json.load(r)

    events, polls = {}, []
    t0 = None
    while True:
        try:
            world = get("/world")
            acts = get("/events/activity")
        except Exception as e:
            print(f"poll error: {e}", flush=True)
            time.sleep(a.interval)
            continue
        tick = world["tick"]
        t0 = tick if t0 is None else t0
        polls.append({"tick": tick, "kitties": [
            {"id": k["id"], "needs": k["needs"], "happiness": k["happiness"]}
            for k in world["kitties"]]})
        for e in acts:
            events[(e["kitty_id"], e["started"], e["ended"])] = e
        if tick >= t0 + a.ticks:
            break
        time.sleep(a.interval)
    t1 = t0 + a.ticks - 1
    # One more read so scenes ending at t1 are all in the log.
    time.sleep(a.interval)
    for e in get("/events/activity"):
        events[(e["kitty_id"], e["started"], e["ended"])] = e
    n = len(polls[0]["kitties"])
    summary = summarize(events.values(), polls, t0, t1, n)
    out = {"base": a.base, "summary": summary, "polls": polls,
           "events": sorted(events.values(), key=lambda e: (e["started"], e["kitty_id"]))}
    raw = Path(a.raw) if a.raw else Path(__file__).parent / "results-raw" / f"scene-census-{t0}.json"
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: summary[k] for k in
                      ("ticks", "events_in_window", "per_1k_cat_ticks", "rest_by_window",
                       "rest_tiers", "cosleep_to_solo", "happiness_mean")}, indent=1))
    print(f"raw -> {raw}")


if __name__ == "__main__":
    main()
