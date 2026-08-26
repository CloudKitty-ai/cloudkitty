#!/usr/bin/env python3
"""need_latency.py -- needs-servicing latency census (fog-gen1 timeline
step 0; shakeout INVESTIGATE criterion 4, the "world harder" vs "mind
broken" separator, and the Biscuit 3.0 design gate).

What it measures, per seat per need, off /world polls:

- ARMED LATENCY: ticks from a need crossing the engine's own announce
  threshold (spec 028: armed at >= [meow].announce_threshold 30) until
  the relief that takes it back below the disarm line (threshold -
  hysteresis = 25). Reliefs that leave the level still armed count as
  partial, not service. Excursions cut off by the window edge are
  CENSORED and counted, never given a made-up latency.
- time-above-level shares at reference levels (10/20/30), mean and max
  level, and the standing-demand price in happiness points
  (mean_level x happiness weight -- happiness = 100 - sum(w*need)).

How it can be exact from sparse polls: needs rise linearly between
reliefs and `last_relief` in the payload carries the EXACT tick of the
latest relief per need, so a relief-free poll gap is a straight line
through its endpoints, and a gap containing a relief splits at the
stamped tick. Rise rates are MEASURED per (seat, need) from relief-free
gaps (median slope) rather than read from config: the served config has
per-kitty overrides for every seat, and bath rises extra on water tiles
(spec 024), so the trusted source is the trajectory itself.

Known limits (stated, not hidden): `last_relief` keeps only the latest
stamp, so several reliefs of one need inside one poll gap collapse to
the last (relief COUNTS are lower bounds; latency endpoints are exact
whenever the servicing relief is the last in its gap -- at armed levels
that is the normal case). A gap whose arithmetic doesn't close (bath on
water, clamp at 100) contributes its polls to the sampled means but is
excluded from exact integration; `bad_gaps` counts them.

Usage:
  python3 need_latency.py results-raw/need-latency-<tick>.json  # re-cut
  python3 need_latency.py --live [DURATION_MIN] [INTERVAL_S]    # poll
"""
import json
import statistics as st
import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from census_provenance import served, stamp  # noqa: E402

BASE = "https://kitties.ai"
NEEDS = ("eat", "drink", "sleep", "play", "cuddle", "bath")
ARM_AT = 30.0      # [meow].announce_threshold -- the engine's own bar
HYSTERESIS = 5.0   # disarm below ARM_AT - HYSTERESIS (spec 028)
REF_LEVELS = (10.0, 20.0, 30.0)
HERE = Path(__file__).resolve().parent


def happiness_weights():
    """[happiness.weights] from the repo config; the census's own
    happiness residual check will scream if these aren't the served ones."""
    try:
        import tomllib
        cfg = tomllib.loads((HERE.parents[1] / "cloudkitty.toml").read_text())
        return {k: float(v) for k, v in cfg["happiness"]["weights"].items()}
    except Exception:
        return {"eat": .20, "drink": .20, "sleep": .15,
                "play": .15, "cuddle": .15, "bath": .15}


def _series(polls):
    """(seat_name, need) -> [(tick, level, last_relief_tick)], tick-sorted."""
    out = defaultdict(list)
    for p in sorted(polls, key=lambda p: p["tick"]):
        for k in p["kitties"]:
            for need in NEEDS:
                out[(k["name"], need)].append(
                    (p["tick"], float(k["needs"][need]),
                     int((k.get("last_relief") or {}).get(need, 0))))
    return out


def _rate(series):
    """Median slope over relief-free gaps; None if no clean gap exists."""
    slopes = [(l1 - l0) / (t1 - t0)
              for (t0, l0, r0), (t1, l1, r1) in zip(series, series[1:])
              if r1 == r0 and t1 > t0 and l1 >= l0]
    return st.median(slopes) if slopes else None


def _analyze_one(series, arm_at, disarm_below, ref_levels):
    """One (seat, need) trace -> metrics dict. Exact where the gap
    arithmetic closes, sampled elsewhere; censored excursions counted."""
    rate = _rate(series)
    levels = [l for _, l, _ in series]
    m = dict(rate=round(rate, 4) if rate is not None else None,
             mean_level=round(st.fmean(levels), 2),
             max_level=round(max(levels), 2),
             reliefs_observed=0, bad_gaps=0,
             time_above={int(a): 0.0 for a in ref_levels},
             latencies=[], partial_reliefs=0,
             censored_left=0, censored_right=0)
    window = series[-1][0] - series[0][0]
    m["window_ticks"] = window
    if window <= 0:
        return m

    # Piecewise-linear reconstruction: each poll gap becomes rising
    # sub-segments (ta, La) -> (tb, Lb), split at a stamped relief.
    def rising_subsegments():
        for (t0, l0, r0), (t1, l1, r1) in zip(series, series[1:]):
            if t1 <= t0:
                continue
            if r1 == r0:
                if l1 + 1e-3 < l0:  # level fell without a stamp: not linear
                    m["bad_gaps"] += 1
                    continue
                yield (t0, l0, t1, l1, None)
            else:
                m["reliefs_observed"] += 1
                if rate is None or not (t0 <= r1 <= t1):
                    m["bad_gaps"] += 1
                    continue
                peak = l0 + rate * (r1 - t0)
                residual = l1 - rate * (t1 - r1)
                if residual < -1e-2 or peak > 100.0 + 1e-2:
                    m["bad_gaps"] += 1  # clamp or extra charge in the gap
                    continue
                residual = max(residual, 0.0)
                yield (t0, l0, r1, peak, ("relief", r1, residual))
                if t1 > r1:
                    yield (r1, residual, t1, l1, None)

    armed_since = None      # tick the level crossed arm_at, else None
    left_censored = False   # armed at window start: no honest start tick
    if levels[0] >= arm_at:
        armed_since, left_censored = series[0][0], True
        m["censored_left"] = 1
    for ta, la, tb, lb, event in rising_subsegments():
        for a in ref_levels:
            if lb > a:  # rising segment: time above = after the crossing
                cross = ta if la >= a else ta + (a - la) / ((lb - la) / (tb - ta))
                m["time_above"][int(a)] += tb - cross
        if armed_since is None and la < arm_at <= lb:
            armed_since = ta + (arm_at - la) / ((lb - la) / (tb - ta))
        if event and armed_since is not None:
            _, r_tick, residual = event
            if residual < disarm_below:
                if not left_censored:
                    m["latencies"].append(round(r_tick - armed_since, 1))
                armed_since, left_censored = None, False
            else:
                m["partial_reliefs"] += 1
    if armed_since is not None and not left_censored:
        m["censored_right"] = 1

    m["time_above"] = {a: round(v / window, 4) for a, v in m["time_above"].items()}
    lat = m.pop("latencies")
    m["armed_excursions"] = len(lat)
    if lat:
        m["latency"] = dict(n=len(lat), p50=st.median(lat), max=max(lat),
                            p90=sorted(lat)[int(.9 * (len(lat) - 1))])
    return m


def analyze(polls, arm_at=ARM_AT, hysteresis=HYSTERESIS,
            ref_levels=REF_LEVELS, weights=None):
    weights = weights or happiness_weights()
    per_seat = defaultdict(dict)
    for (name, need), series in _series(polls).items():
        per_seat[name][need] = _analyze_one(
            series, arm_at, arm_at - hysteresis, ref_levels)
    # Standing-demand price (happiness points) + payload consistency:
    # 100 - sum(w * need) must reproduce the served happiness.
    price, hap_resid = {}, 0.0
    for p in polls:
        for k in p["kitties"]:
            if "happiness" in k:
                calc = 100.0 - sum(weights[n] * float(k["needs"][n])
                                   for n in NEEDS)
                hap_resid = max(hap_resid, abs(calc - float(k["happiness"])))
    for name, by_need in per_seat.items():
        price[name] = round(sum(by_need[n]["mean_level"] * weights[n]
                                for n in NEEDS), 3)
    return dict(arm_at=arm_at, disarm_below=arm_at - hysteresis,
                seats=dict(per_seat), demand_price_happiness_pts=price,
                happiness_residual_max=round(hap_resid, 3))


def poll_live(duration_min, interval_s):
    polls, n = [], max(2, int(duration_min * 60 // interval_s))
    for i in range(n):
        try:
            with urllib.request.urlopen(f"{BASE}/world", timeout=15) as r:
                w = json.load(r)
            polls.append({"tick": w["tick"], "kitties": [
                {"id": k["id"], "name": k["name"], "pos": k["pos"],
                 "needs": k["needs"],
                 "last_relief": k.get("last_relief", {}),
                 "announce_armed": k.get("announce_armed", []),
                 "happiness": k["happiness"],
                 "activity": k["activity"]} for k in w["kitties"]]})
        except Exception as e:  # transient box hiccup: skip the poll
            print(f"poll {i}: {e}", file=sys.stderr)
        if i < n - 1:
            time.sleep(interval_s)
    return polls


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        dur = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
        iv = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
        polls = poll_live(dur, iv)
        out = dict(instrument="need_latency.py",
                   provenance=stamp(__file__), served=served(BASE),
                   base=BASE, interval_s=iv,
                   polls=len(polls),
                   tick_range=[polls[0]["tick"], polls[-1]["tick"]],
                   analysis=analyze(polls), raw_polls=polls)
        raw_dir = HERE / "results-raw"
        raw_dir.mkdir(exist_ok=True)
        path = raw_dir / f"need-latency-{out['tick_range'][0]}.json"
        path.write_text(json.dumps(out, indent=1) + "\n")
        print(json.dumps({k: v for k, v in out["analysis"].items()},
                         indent=1))
        print(f"-> {path}")
    else:
        d = json.load(open(sys.argv[1]))
        polls = d.get("raw_polls") or d.get("polls") or []
        print(json.dumps(analyze(polls), indent=1))
