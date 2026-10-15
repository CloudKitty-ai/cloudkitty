#!/usr/bin/env python3
"""Guard for run_legs.py (plain asserts, no pytest).

Synthetic scout rows pin the F-053 gate; plan() ordering pins
scouts-first; one real tiny run (anchor-b3, 60 ticks) pins the
subprocess wiring end to end, scout gate included.
"""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_legs as rl  # noqa: E402

ANCHOR_B3 = HERE.parent / "fog-gen1-cert" / "anchor-b3.toml"


def write_scout(td, band, ticks, row):
    p = Path(td) / f"scripted-{band}-1x{ticks}.jsonl"
    p.write_text(json.dumps({"provenance": {}}) + "\n" + json.dumps(row) + "\n")
    return p


def test_scout_gate_passes_a_clean_row():
    with tempfile.TemporaryDirectory() as td:
        p = write_scout(td, "probe", 50, {"max_distress_age": 12, "ticks": 50})
        ok, reason = rl.scout_verdict(p)
    assert ok and "12" in reason, (ok, reason)


def test_scout_gate_fails_an_aborted_row():
    with tempfile.TemporaryDirectory() as td:
        p = write_scout(td, "probe", 50, {
            "aborted_streak": {"limit": 1000, "at_tick": 4321},
            "max_distress_age": 1000, "ticks": 4321})
        ok, reason = rl.scout_verdict(p)
    assert not ok and "4321" in reason, (ok, reason)


def test_scout_gate_fails_an_at_line_streak_even_unaborted():
    # A row that reached the line without the abort recorded (e.g. a
    # harness run without --abort-streak) still fails the gate.
    with tempfile.TemporaryDirectory() as td:
        p = write_scout(td, "probe", 50, {"max_distress_age": 1000, "ticks": 50})
        ok, reason = rl.scout_verdict(p)
    assert not ok and "1000" in reason, (ok, reason)


def test_scout_gate_fails_a_missing_file():
    ok, reason = rl.scout_verdict(Path("/nonexistent/scout.jsonl"))
    assert not ok and "unreadable" in reason


def test_plan_is_scouts_first_for_displaced_sizes_only():
    cfgs = {20: "c20.toml", 40: "c40.toml", 100: "c100.toml"}
    stages = rl.plan(cfgs, "probe", 30, 20000, 6, "/tmp/out")
    names = [s[0] for s in stages]
    assert names == ["leg-20", "scout-40", "leg-40", "scout-100", "leg-100"], names
    by_name = dict((n, (cmd, gate)) for n, cmd, gate in stages)
    # the 20x20 leg has no scout and no gate; each displaced scout
    # carries its gate file and runs 1 seed with the F-053 stop
    assert by_name["leg-20"][1] is None
    for size in (40, 100):
        cmd, gate = by_name[f"scout-{size}"]
        assert gate is not None and f"size{size}" in str(gate)
        assert cmd[cmd.index("--seeds") + 1] == "1"
        assert cmd[cmd.index("--abort-streak") + 1] == "1000"
        assert by_name[f"leg-{size}"][1] is None
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
    rl.scout_verdict = lambda p: (False, "forced miss")
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


def test_real_tiny_run_scout_gate_end_to_end():
    # anchor-b3 for every size slot: the driver's wiring is under test,
    # not the configs. --only 40 exercises scout -> gate -> leg.
    with tempfile.TemporaryDirectory() as td:
        rl.main([f"--config-20={ANCHOR_B3}", f"--config-40={ANCHOR_B3}",
                 f"--config-100={ANCHOR_B3}", "--band", "probe",
                 "--seeds", "1", "--ticks", "60", "--workers", "1",
                 "--out-dir", td, "--only", "40"])
        scout = Path(td) / "scouts/size40/scripted-probe-1x60.jsonl"
        leg = Path(td) / "legs/size40/scripted-probe-1x60.jsonl"
        assert scout.exists() and leg.exists()
        ok, reason = rl.scout_verdict(scout)
        assert ok, reason


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
