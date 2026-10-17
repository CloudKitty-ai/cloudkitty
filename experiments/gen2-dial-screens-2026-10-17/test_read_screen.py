#!/usr/bin/env python3
"""Suite for read_screen.py. Plain asserts, self-running (python -B).

The fixture is a REAL captured trace (results-raw/fixture/
trace-consent30-seed996001.jsonl — the draft world as shipped, consent
30, seed 996001, 2000 ticks; re-capture via bc-collect --trace on the
draft toml if lost; wall-clock-free, so a re-capture reproduces bytes
given the same binary). Literals below were derived by an independent
flat scan, not by the reader.

Planted-defect traces are the fixture with a JSON mutation; every
plant asserts the mutation changed the text (no-op plants refused).
"""
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from read_screen import read_run, run_scalars, sweep  # noqa: E402

HERE = pathlib.Path(__file__).parent
FIXTURE = HERE / "results-raw" / "fixture" / "trace-consent30-seed996001.jsonl"

# Independent literals (flat scan, 2026-10-17):
TICKS, KITTIES = 2000, 5
MEAN_HAPPINESS = 83.8741479053
PLAYING_KTICKS = 1337
REFUSALS = {"consent_declined": 188, "other": 126,
            "partner_absent": 406, "partner_busy": 913}


def plant(mutate, out_path):
    """Copy the fixture line-by-line through `mutate(tick, record)`;
    refuse a plant that changes nothing."""
    changed = False
    with open(FIXTURE) as src, open(out_path, "w") as dst:
        for tick, line in enumerate(src):
            rec = json.loads(line)
            before = json.dumps(rec, sort_keys=True)
            mutate(tick, rec)
            changed = changed or json.dumps(rec, sort_keys=True) != before
            dst.write(json.dumps(rec) + "\n")
    assert changed, "vacuous plant: mutation changed nothing"


def test_fixture_metrics():
    run = read_run(FIXTURE)
    assert run["ticks"] == TICKS and run["kitties"] == KITTIES
    assert round(run["mean_happiness"], 6) == round(MEAN_HAPPINESS, 6)
    assert run["distress_ticks"] == 0 and run["max_distress_streak"] == 0
    assert run["activity_share"]["playing"] == PLAYING_KTICKS / (TICKS * KITTIES)
    assert run["refusals"] == REFUSALS


def test_streak_counts_consecutive_and_resets_on_gap():
    def mutate(tick, rec):
        if tick in (100, 101, 102, 103, 104, 200, 201):
            for k in rec["snapshot"]["kitties"]:
                if k["id"] == 3:
                    k["in_distress"] = ["eat"]
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "t.jsonl"
        plant(mutate, p)
        run = read_run(p)
        assert run["distress_ticks"] == 7, run["distress_ticks"]
        assert run["max_distress_streak"] == 5, (
            "the tick-200 pair must NOT extend the tick-104 run: "
            f"{run['max_distress_streak']}")


def test_streak_is_per_kitty_never_pooled():
    def mutate(tick, rec):
        for k in rec["snapshot"]["kitties"]:
            if (k["id"] == 1 and tick in (10, 11)) or \
               (k["id"] == 2 and tick in (12, 13)):
                k["in_distress"] = ["sleep"]
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "t.jsonl"
        plant(mutate, p)
        run = read_run(p)
        assert run["max_distress_streak"] == 2, (
            f"adjacent streaks on different kitties pooled: "
            f"{run['max_distress_streak']}")


def _mini_sweep(td, anchor_copies, shifted_value, shift):
    """A sweep dir from real payloads: v30 = fixture verbatim,
    v<shifted> = fixture with every happiness shifted."""
    def shifted(tick, rec):
        for k in rec["snapshot"]["kitties"]:
            k["happiness"] += shift
    for v, builder in ((30, None), (shifted_value, shifted)):
        for r in range(anchor_copies):
            d = pathlib.Path(td) / f"v{v:02d}" / f"config-00-rollout-{r:02d}"
            d.mkdir(parents=True)
            if builder is None:
                (d / "trace.jsonl").write_text(FIXTURE.read_text())
            else:
                plant(builder, d / "trace.jsonl")


def test_sweep_paired_delta_is_within_seed():
    with tempfile.TemporaryDirectory() as td:
        _mini_sweep(td, anchor_copies=2, shifted_value=0, shift=-1.0)
        result = sweep(td, anchor=30)
        row = result["values"][0]
        assert round(row["paired_delta_mean"]["mean_happiness"], 9) == -1.0
        lo, hi = row["paired_delta_range"]["mean_happiness"]
        assert round(lo, 9) == round(hi, 9) == -1.0
        anchor_row = result["values"][30]
        assert anchor_row["paired_delta_mean"]["mean_happiness"] == 0.0


def test_sweep_refuses_unequal_seed_counts():
    with tempfile.TemporaryDirectory() as td:
        _mini_sweep(td, anchor_copies=2, shifted_value=0, shift=-1.0)
        extra = pathlib.Path(td) / "v00" / "config-00-rollout-02"
        extra.mkdir(parents=True)
        (extra / "trace.jsonl").write_text(FIXTURE.read_text())
        try:
            sweep(td, anchor=30)
        except AssertionError as e:
            assert "unequal seed counts" in str(e)
        else:
            raise AssertionError("unequal seed counts accepted")


def test_sweep_refuses_missing_anchor():
    with tempfile.TemporaryDirectory() as td:
        _mini_sweep(td, anchor_copies=1, shifted_value=0, shift=-1.0)
        try:
            sweep(td, anchor=15)
        except AssertionError as e:
            assert "anchor" in str(e)
        else:
            raise AssertionError("missing anchor accepted")


def test_run_scalars_names_the_consume_columns():
    run = read_run(FIXTURE)
    row = run_scalars(run)
    assert row["play_share"] == PLAYING_KTICKS / (TICKS * KITTIES)
    assert row["consent_refusals"] == REFUSALS["consent_declined"]


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
    print(f"{sum(1 for n in globals() if n.startswith('test_'))} passed")
