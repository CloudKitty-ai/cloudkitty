#!/usr/bin/env python3
"""Counterfactual verbosity of a `relief_memory_radius` want law, read off a
recorded bc-collect --trace (no engine change).

    relief_radius_sweep.py TRACE_DIR [D ...]

For every D (Manhattan; 0 = the unbounded pre-050 rule, i.e. the key
absent; spec 050's `relief_memory_margin = m` is D = radius + m) and every cat-tick,
a want is LEGAL when the need is armed (>= announce_threshold), is the
top need, and no relief is known: visible relief always counts, a
remembered element counts only within D tiles of the cat. Calls are then
simulated per (cat, kind) with the configured cooldown: call on the first
legal tick, then not again for `recent_window_ticks`. Reported per kind
as legal cat-ticks and simulated calls per 1000 ticks, next to the
scripted calls the trace actually holds.

First order only: the trajectory is the recorded one, so extra calls do
not move the cats or their friends here. Cuddle has no memory clause and
bath/sleep never know relief, so those columns are constant across D.
"""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from schema_check import (  # noqa: E402
    CRITTER_KINDS, ELEMENT_KINDS, NEED_OF_WANT, WANT_KINDS, elements_of,
    kitties_by_id, load_trace, manhattan, meows_emitted_at, stocked, top_need, visible)


def known(want, kitty, snap, r, D):
    pos = kitty["pos"]

    def remembered(kind):
        m = kitty["memory"][ELEMENT_KINDS.index(kind)]
        return m is not None and (D == 0 or manhattan(pos, m["pos"]) <= D)

    def vis(kind):
        return any(visible(pos, e["pos"], r) for e in elements_of(snap, kind))

    idle_friend = any(k["id"] != kitty["id"] and k.get("activity_clock") is None
                      and visible(pos, k["pos"], r) for k in snap["kitties"])
    if want == "want_eat":
        return any(stocked(e) and visible(pos, e["pos"], r)
                   for e in elements_of(snap, "chow")) or remembered("chow")
    if want == "want_drink":
        return vis("water") or remembered("water")
    if want == "want_cuddle":
        return idle_friend
    if want == "want_play":
        return idle_friend or any(vis(k) or remembered(k) for k in CRITTER_KINDS)
    return False


def sweep(tr, Ds):
    thr, cd, r = tr.cfg["meow"]["announce_threshold"], tr.cooldown, tr.radius
    n_ticks = len(tr.lines)
    out = {}
    for D in Ds:
        legal, calls = collections.Counter(), collections.Counter()
        last = {}
        for i in range(n_ticks):
            snap = tr.snap(i)
            for k in snap["kitties"]:
                top = top_need(k["needs"])   # engine tie-break, not `max`
                for want in WANT_KINDS:
                    need = NEED_OF_WANT[want]
                    v = k["needs"][need]
                    if v < thr or need != top or known(want, k, snap, r, D):
                        continue
                    legal[want] += 1
                    key = (k["id"], want)
                    if snap["tick"] - last.get(key, -10**9) >= cd:
                        calls[want] += 1
                        last[key] = snap["tick"]
        out[D] = (legal, calls)
    actual = collections.Counter(m["kind"] for i in range(n_ticks - 1)
                                 for m in meows_emitted_at(tr, i) if m["kind"] in WANT_KINDS)
    return out, actual, n_ticks


def main():
    tr = load_trace(sys.argv[1])
    Ds = [int(x) for x in sys.argv[2:]] or [0, 3, 4, 5, 6, 8, 10]
    out, actual, n = sweep(tr, Ds)
    scale = 1000.0 / n
    print(f"trace {n} ticks, radius {tr.radius}, cooldown {tr.cooldown}; per 1000 ticks, all cats")
    print(f"{'kind':<12}{'actual':>8}" + "".join(f"{'D=' + str(D):>12}" for D in Ds))
    for want in WANT_KINDS:
        row = f"{want:<12}{actual[want] * scale:>8.0f}"
        for D in Ds:
            legal, calls = out[D]
            row += f"{calls[want] * scale:>7.0f}/{legal[want] * scale:<4.0f}"
        print(row)
    tot = f"{'all wants':<12}{sum(actual.values()) * scale:>8.0f}"
    for D in Ds:
        legal, calls = out[D]
        tot += f"{sum(calls.values()) * scale:>7.0f}/{sum(legal.values()) * scale:<4.0f}"
    print(tot)
    print("cells: simulated calls / legal cat-ticks; D=0 is the unbounded (pre-050) memory rule")


if __name__ == "__main__":
    main()
