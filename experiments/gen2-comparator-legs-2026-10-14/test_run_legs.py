#!/usr/bin/env python3
"""Guard for run_legs.py (plain asserts, no pytest).

Synthetic scout rows pin the F-053 gate (multi-seed coverage, owner
2026-10-15); plan() ordering pins scouts-first; one real tiny run
(anchor-b3, 60 ticks) pins the subprocess wiring end to end, scout
gate included.
"""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_legs as rl  # noqa: E402

ANCHOR_B3 = HERE.parent / "fog-gen1-cert" / "anchor-b3.toml"


def write_scout(td, band, ticks, rows):
    n = len(rows)
    p = Path(td) / f"scripted-{band}-{n}x{ticks}.jsonl"
    p.write_text("\n".join([json.dumps({"provenance": {}})]
                           + [json.dumps(r) for r in rows]) + "\n")
    return p


def test_scout_gate_passes_clean_rows_reporting_the_worst():
    rows = [{"seed": 870_001 + i, "max_distress_age": a, "ticks": 50}
            for i, a in enumerate((12, 40, 7))]
    with tempfile.TemporaryDirectory() as td:
        ok, reason = rl.scout_verdict(write_scout(td, "probe", 50, rows),
                                      expect_seeds=3)
    assert ok and "worst distress streak 40" in reason, (ok, reason)


def test_scout_gate_fails_if_any_seed_aborted_naming_it():
    rows = [{"seed": 870_001, "max_distress_age": 3, "ticks": 50},
            {"seed": 870_002, "aborted_streak": {"limit": 1000, "at_tick": 4321},
             "max_distress_age": 1000, "ticks": 4321}]
    with tempfile.TemporaryDirectory() as td:
        ok, reason = rl.scout_verdict(write_scout(td, "probe", 50, rows),
                                      expect_seeds=2)
    assert not ok and "870002" in reason and "4321" in reason, (ok, reason)


def test_scout_gate_fails_an_at_line_streak_even_unaborted():
    # A row that reached the line without the abort recorded (e.g. a
    # harness run without --abort-streak) still fails the gate.
    rows = [{"seed": 870_001, "max_distress_age": 1000, "ticks": 50}]
    with tempfile.TemporaryDirectory() as td:
        ok, reason = rl.scout_verdict(write_scout(td, "probe", 50, rows),
                                      expect_seeds=1)
    assert not ok and "1000" in reason, (ok, reason)


def test_scout_gate_fails_short_files_and_missing_files():
    # 3 seeds scouted, 2 rows written: a dead worker is not a clean scout.
    rows = [{"seed": 870_001, "max_distress_age": 1, "ticks": 50},
            {"seed": 870_002, "max_distress_age": 2, "ticks": 50}]
    with tempfile.TemporaryDirectory() as td:
        ok, reason = rl.scout_verdict(write_scout(td, "probe", 50, rows),
                                      expect_seeds=3)
    assert not ok and "2 seed rows" in reason and "expected 3" in reason
    ok, reason = rl.scout_verdict(Path("/nonexistent/scout.jsonl"))
    assert not ok and "unreadable" in reason


def test_plan_is_scouts_first_for_displaced_sizes_only():
    cfgs = {20: "c20.toml", 40: "c40.toml", 100: "c100.toml"}
    stages = rl.plan(cfgs, "probe", 30, 20000, 6, "/tmp/out", scout_seeds=3)
    names = [s[0] for s in stages]
    assert names == ["leg-20", "scout-40", "leg-40", "scout-100", "leg-100"], names
    by_name = dict((n, (cmd, gate)) for n, cmd, gate in stages)
    # the 20x20 leg has no scout; each displaced scout covers
    # scout_seeds worlds (the band's first, recurring in the leg),
    # carries its gate file, and runs with the F-053 stop; every LEG is
    # gated on its own output file (entry-4 remedy)
    for size in (20, 40, 100):
        gate = by_name[f"leg-{size}"][1]
        assert gate is not None and str(gate).endswith(
            f"legs/size{size}/scripted-probe-30x20000.jsonl"), gate
    for size in (40, 100):
        cmd, gate = by_name[f"scout-{size}"]
        assert gate is not None and f"size{size}" in str(gate)
        assert str(gate).endswith("scripted-probe-3x20000.jsonl"), gate
        assert cmd[cmd.index("--seeds") + 1] == "3"
        assert cmd[cmd.index("--abort-streak") + 1] == "1000"
    # every stage is scripted seating with the streak stop armed
    for n, (cmd, _g) in by_name.items():
        assert "scripted" in cmd and "--abort-streak" in cmd, n


def test_plan_only_filter():
    cfgs = {20: "c20.toml", 40: "c40.toml", 100: "c100.toml"}
    names = [s[0] for s in rl.plan(cfgs, "probe", 30, 20000, 6, "/tmp/out",
                                   only=(40,))]
    assert names == ["scout-40", "leg-40"], names


def test_main_stops_on_a_failed_gate_and_runs_no_leg():
    calls = []
    real_run, real_verdict = rl.subprocess.run, rl.scout_verdict
    rl.subprocess.run = lambda cmd: (calls.append(cmd),
                                     type("R", (), {"returncode": 0}))[1]
    rl.scout_verdict = lambda p, expect_seeds=None: (False, "forced miss")
    try:
        try:
            rl.main(["--config-20=c", "--config-40=c", "--config-100=c",
                     "--band", "probe", "--only", "40"])
        except SystemExit as e:
            assert "F-053" in str(e), e
        else:
            raise AssertionError("a failed scout gate must stop the driver")
        assert len(calls) == 1 and "--seeds" in calls[0], calls  # scout only, no leg
    finally:
        rl.subprocess.run, rl.scout_verdict = real_run, real_verdict


def test_main_stops_after_an_aborted_leg_and_runs_no_later_stage():
    # The entry-4 remedy: a leg whose file carries an abort stops the
    # driver; with --only 20,40 the stages are leg-20, scout-40,
    # leg-40, so a stop at leg-20 must leave exactly one harness call.
    calls = []
    real_run, real_verdict = rl.subprocess.run, rl.scout_verdict
    rl.subprocess.run = lambda cmd: (calls.append(cmd),
                                     type("R", (), {"returncode": 0}))[1]
    rl.scout_verdict = lambda p, expect_seeds=None, kind="scout": (
        (False, "leg seed 905008 ABORTED at tick 18949") if kind == "leg"
        else (True, "clean"))
    try:
        try:
            rl.main(["--config-20=c", "--config-40=c", "--config-100=c",
                     "--band", "probe", "--only", "20,40"])
        except SystemExit as e:
            assert "LEG STOP" in str(e) and "905008" in str(e), e
        else:
            raise AssertionError("a leg abort must stop the driver")
        assert len(calls) == 1 and "size20" in " ".join(calls[0]), calls
    finally:
        rl.subprocess.run, rl.scout_verdict = real_run, real_verdict


def test_leg_gate_trips_on_the_real_recorded_abort_row():
    # Recorded payload, not a hand-written one: the g2-s2 20x20 row for
    # seed 905008 copied verbatim from the battery raws (the row the
    # undeclared continuation ran past, gen2-deviations entry 4).
    p = HERE / "fixtures" / "leg-abort-g2-s2-905008.jsonl"
    ok, reason = rl.scout_verdict(p, expect_seeds=1, kind="leg")
    assert not ok and "905008" in reason and "18949" in reason, (ok, reason)


def test_real_tiny_run_scout_gate_end_to_end():
    # anchor-b3 for every size slot: the driver's wiring is under test,
    # not the configs. --only 40 exercises scout -> gate -> leg with
    # two scouted worlds.
    with tempfile.TemporaryDirectory() as td:
        rl.main([f"--config-20={ANCHOR_B3}", f"--config-40={ANCHOR_B3}",
                 f"--config-100={ANCHOR_B3}", "--band", "probe",
                 "--seeds", "1", "--ticks", "60", "--workers", "1",
                 "--scout-seeds", "2", "--out-dir", td, "--only", "40"])
        scout = Path(td) / "scouts/size40/scripted-probe-2x60.jsonl"
        leg = Path(td) / "legs/size40/scripted-probe-1x60.jsonl"
        assert scout.exists() and leg.exists()
        ok, reason = rl.scout_verdict(scout, expect_seeds=2)
        assert ok and "2 scout seeds clean" in reason, reason


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
