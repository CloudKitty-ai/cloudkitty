#!/usr/bin/env python3
"""Scripted comparator-leg driver (Gen 2 prereg skeleton §7, RULED):
legs at 20/40/100 run PRE-freeze in battery shape (30 x 20k, scripted
seating); the prereg pins the realized numbers. Displaced sizes (40,
100) are SCOUTS-FIRST (skeleton §6, RULED K§5): one-world scout with a
stop at the F-053 1,000-tick distress-streak line gates each full leg;
a scout miss STOPS that leg and the driver — the stop is asymmetric,
never auto-continued.

The driver orchestrates cert_harness_fog.py (which keys its state
stride off the live binding, 2026-10-14) and decides nothing the
sitting owns: band, seeds, ticks and the three config paths are
inputs. The Gen 2 size configs do not exist yet — they land with the
§2 toml diff at freeze prep, and their 40/100 kitty START POSITIONS
need deliberate placement (world-size-screen's size100.toml kept the
20x20 starts, clustering all five cats in one corner — do not reuse
them for a welfare-bearing comparator).

    experiments/exp-006-character-gen/.venv/bin/python \\
        experiments/gen2-comparator-legs-2026-10-14/run_legs.py \\
        --config-20 C20.toml --config-40 C40.toml --config-100 C100.toml \\
        --band BAND [--seeds 30] [--ticks 20000] [--workers 6]
        [--only 20,40] [--dry-run]

Guard: test_run_legs.py.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS = HERE.parent / "fog-gen1-cert" / "cert_harness_fog.py"
PYTHON = HERE.parents[1] / "experiments/exp-006-character-gen/.venv/bin/python"
F053_STREAK = 1000   # the F-053 1,000-tick distress-streak line
SIZES = (20, 40, 100)
DISPLACED = (40, 100)


def harness_cmd(config, band, seeds, ticks, workers, out_dir):
    """One cert_harness_fog invocation, scripted seating, the F-053
    streak stop always armed."""
    return [str(PYTHON), str(HARNESS), "scripted", band,
            "--seeds", str(seeds), "--ticks", str(ticks),
            "--workers", str(workers), "--config", str(config),
            "--out-dir", str(out_dir), "--abort-streak", str(F053_STREAK)]


def scout_verdict(jsonl_path, expect_seeds=None):
    """(ok, reason) for a scout file: row 1 is provenance, every later
    row is one scouted seed. ALL seeds must be clean — the gate fails
    on an armed abort, on a streak at/over the line even unaborted, on
    an unreadable file, or on fewer rows than seeds scouted (a dead
    worker is not a clean scout)."""
    p = Path(jsonl_path)
    try:
        lines = p.read_text().splitlines()
        rows = [json.loads(l) for l in lines[1:]]
    except (OSError, json.JSONDecodeError) as e:
        return False, f"scout file unreadable: {p} ({e})"
    if not rows or (expect_seeds is not None and len(rows) != expect_seeds):
        return False, (f"scout file carries {len(rows)} seed rows, "
                       f"expected {expect_seeds}: {p}")
    worst = -1
    for row in rows:
        seed = row.get("seed")
        if "aborted_streak" in row:
            a = row["aborted_streak"]
            return False, (f"scout seed {seed} ABORTED at tick {a['at_tick']} "
                           f"(distress streak reached {a['limit']})")
        if row.get("max_distress_age", 0) >= F053_STREAK:
            return False, (f"scout seed {seed} distress streak "
                           f"{row['max_distress_age']} >= the F-053 line "
                           f"{F053_STREAK}")
        worst = max(worst, row.get("max_distress_age", 0))
    return True, (f"{len(rows)} scout seeds clean: worst distress streak "
                  f"{worst}")


def plan(configs, band, seeds, ticks, workers, out_dir, only=SIZES,
         scout_seeds=3):
    """Ordered stages: per size (ascending), scout-then-gate for the
    displaced sizes, then the full leg. Each stage: (name, cmd,
    scout_file_to_gate_on_or_None). Scout coverage (owner 2026-10-15):
    scout_seeds worlds per displaced size — the band's FIRST seeds, so
    every scouted world recurs in the full leg — all gated on the
    F-053 line before the leg runs."""
    out_dir = Path(out_dir)
    stages = []
    for size in SIZES:
        if size not in only:
            continue
        cfg = configs[size]
        if size in DISPLACED:
            sdir = out_dir / f"scouts/size{size}"
            stages.append((f"scout-{size}",
                           harness_cmd(cfg, band, scout_seeds, ticks,
                                       min(scout_seeds, workers), sdir),
                           sdir / f"scripted-{band}-{scout_seeds}x{ticks}.jsonl"))
        stages.append((f"leg-{size}",
                       harness_cmd(cfg, band, seeds, ticks, workers,
                                   out_dir / f"legs/size{size}"),
                       None))
    return stages


def main(argv=None):
    ap = argparse.ArgumentParser()
    for s in SIZES:
        ap.add_argument(f"--config-{s}", type=Path, required=True)
    ap.add_argument("--band", required=True,
                    help="seed band name (must exist in cert_harness_fog BANDS; "
                         "the Gen 2 comparator band is added there when ruled)")
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--ticks", type=int, default=20_000)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out-dir", type=Path, default=HERE / "results-raw")
    ap.add_argument("--only", default=None,
                    help="comma list of sizes to run, e.g. 20,40")
    ap.add_argument("--scout-seeds", type=int, default=3,
                    help="worlds scouted per displaced size before its leg "
                         "(the band's first seeds; all must pass the F-053 gate)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    only = tuple(int(s) for s in a.only.split(",")) if a.only else SIZES
    bad = [s for s in only if s not in SIZES]
    if bad:
        raise SystemExit(f"run_legs: unknown sizes {bad}; sizes are {SIZES}")
    configs = {s: getattr(a, f"config_{s}") for s in SIZES}
    stages = plan(configs, a.band, a.seeds, a.ticks, a.workers, a.out_dir, only,
                  a.scout_seeds)
    for name, cmd, scout_file in stages:
        print(f"== {name}: {' '.join(cmd)}", flush=True)
        if a.dry_run:
            continue
        r = subprocess.run(cmd)
        if r.returncode != 0:
            raise SystemExit(f"run_legs: {name} exited {r.returncode}; stopping")
        if scout_file is not None:
            ok, reason = scout_verdict(scout_file, expect_seeds=a.scout_seeds)
            print(f"== {name} verdict: {reason}", flush=True)
            if not ok:
                raise SystemExit(
                    f"run_legs: {name} FAILED the F-053 gate — the full leg "
                    "does not run; the stop is asymmetric (welfare practice, "
                    "owner 2026-09-26). Take the scout row to the owner.")
    print("== done" if not a.dry_run else "== dry run only")


if __name__ == "__main__":
    main()
