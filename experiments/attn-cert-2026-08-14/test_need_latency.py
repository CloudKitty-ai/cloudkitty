#!/usr/bin/env python3
"""Guard for need_latency.py -- synthetic traces with hand-computed
answers (rule 5: every assertion here was driven red in-run before
commit; the mutations used are noted per block).

All traces: one seat "Test", one moving need ("play", rise 0.5/tick),
polls every 10 ticks, other needs flat 0. Default band: armed >= 30,
serviced when a relief leaves the level below 25.
"""
import need_latency as nl

W6 = {k: 1 / 6 for k in nl.NEEDS}


def mkpolls(rows, need="play", happiness=None):
    """rows: [(tick, level, last_relief_tick)] -> poll list."""
    return [{"tick": t, "kitties": [{
        "id": 1, "name": "Test",
        "needs": {n: (lvl if n == need else 0.0) for n in nl.NEEDS},
        "last_relief": {need: lr},
        **({"happiness": happiness} if happiness is not None else {})}]}
        for t, lvl, lr in rows]


def get(polls, **kw):
    return nl.analyze(polls, weights=W6, **kw)["seats"]["Test"]["play"]


# Trace A: rises 20->35 across polls, stamped relief at tick 136 to
# residual 2 (poll t=140 reads 4 = 2 + 0.5*4). Hand answers: rate 0.5;
# crossing 30 at t=120 exactly; latency 136-120 = 16; time above 30 =
# 16 ticks of the 50-tick window (the reconstructed peak 38 at the
# stamped tick); above 10 = 36 ticks (residual 2 never regains 10).
A = [(100, 20, 90), (110, 25, 90), (120, 30, 90),
     (130, 35, 90), (140, 4, 136), (150, 9, 136)]


def test_excursion_latency_exact():
    m = get(mkpolls(A))
    # reds: relief stamp 136->138 (latency 18); crossing interpolation
    # mutated to drop `- la` (latency 15.0); slope 0.5->0.6 (rate).
    assert m["rate"] == 0.5
    assert m["armed_excursions"] == 1
    assert m["latency"]["p50"] == 16.0
    assert m["reliefs_observed"] == 1 and m["bad_gaps"] == 0
    # reds: time_above mutated to charge whole segments (0.42 / 0.8).
    assert m["time_above"][30] == round(16 / 50, 4)
    assert m["time_above"][10] == round(36 / 50, 4)


# Trace B: never armed at 30 (peaks at 10, relief at tick 24 to
# residual 1). The zero must be a measurement, not a structural
# inability to emit (F-029): the SAME trace armed at 8 must yield an
# excursion, crossing at t=16, serviced at 24 -> latency 8.
B = [(0, 0, -10), (10, 5, -10), (20, 10, -10), (30, 4, 24), (40, 9, 24)]


def test_quiet_trace_zero_and_emit_proof():
    m = get(mkpolls(B))
    assert m["armed_excursions"] == 0
    assert m["time_above"][30] == 0.0
    low = get(mkpolls(B), arm_at=8.0)   # emit proof (red: arm_at=80 -> 0)
    assert low["armed_excursions"] == 1
    assert low["latency"]["p50"] == 8.0


# Trace D: arms (crosses 30 at t=20) and the window ends unserviced.
# No latency may be emitted; the excursion is right-censored.
D = [(0, 20, -10), (10, 25, -10), (20, 30, -10), (30, 35, -10)]


def test_unserviced_excursion_is_censored_not_counted():
    m = get(mkpolls(D))
    # red: appending a servicing relief poll (censored 0, excursions 1).
    assert m["armed_excursions"] == 0 and m["censored_right"] == 1


# Trace E: partial relief. Armed at t=120; relief at 136 leaves 27
# (>= disarm 25: still armed, partial); relief at 144 leaves 3 ->
# serviced. Latency 144 - 120 = 24, one partial on the way.
E = [(100, 20, 90), (110, 25, 90), (120, 30, 90),
     (130, 35, 90), (140, 29, 136), (150, 6, 144)]


def test_partial_relief_does_not_end_the_excursion():
    m = get(mkpolls(E))
    # red: residual threshold flipped so 27 counts as service (lat 16).
    assert m["armed_excursions"] == 1
    assert m["latency"]["p50"] == 24.0
    assert m["partial_reliefs"] == 1


# Trace F: crossings that do NOT land on poll ticks, so the time-above
# interpolation itself is on the hook. 13 -> 23 over 20 ticks: crosses
# 20 at t=14, giving 6 ticks above of a 20-tick window.
F = [(0, 13, -10), (10, 18, -10), (20, 23, -10)]


def test_time_above_interpolates_mid_segment():
    m = get(mkpolls(F))
    # red: `cross` mutated to charge the whole segment (0.5).
    assert m["time_above"][20] == round(6 / 20, 4)
    assert m["time_above"][10] == 1.0


def test_happiness_residual_flags_wrong_weights():
    # eat=6, equal weights 1/6 -> happiness 99. red: happiness=98 -> 1.0
    polls = mkpolls([(0, 6, -10), (10, 11, -10)], need="eat", happiness=None)
    for p, hap in zip(polls, (99.0, 100 - 11 / 6)):
        p["kitties"][0]["happiness"] = hap
    r = nl.analyze(polls, weights=W6)
    assert r["happiness_residual_max"] == 0.0


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
