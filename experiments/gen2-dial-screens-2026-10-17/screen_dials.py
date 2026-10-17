#!/usr/bin/env python3
"""Rig: the Gen 2 dial-range screens (owner kickoff 2026-10-17:
"Screen 2 and 3 at 0,10,15,20,30").

Two one-dial-at-a-time sweeps on the Gen 2 draft world
(gen2-world-draft-2026-10-15.toml, all five seats behavior="teacher"):

  consent: [behavior] consent_line in {0, 10, 15, 20, 30}
           (anchor 30; 0 = gate OFF, world.rs line<=0 early-return —
           not "maximally refusing"; 10 is the most-refusing value)
  slack:   [behavior] comfort_slack in {0, 10, 15, 20, 30} ticks
           (anchor/default 0 = structurally inert, teacher.rs FR-003;
           cell encodes ticks/40 so 30 is inside the clamp)
  favourite: per-kitty one-hot favourite weight in {0, 0.1, 0.25,
           0.5, 1} (owner kickoff 2026-10-17; her 5 is unloadable —
           validate.rs holds weights to 0..=1 and the obs cell is raw
           [0,1], so 1 IS the ceiling and the multiplier tops at 2x).
           Anchor 0 = favourite tables absent (today's config; FR-004
           all-zero is x1.0, bit-identical). Assignment is a SCREEN
           STAND-IN aligned with the trait sheets (Miso=cuddle,
           Biscuit=play, Kittybear=bath, Clementine=sleep,
           Pumpkin=none per owner); the deployed assignment is her
           freeze call. Value dirs are hundredths (v010 = 0.1).

The other dials stay at the draft's value (consent 30 / slack absent).
Derived configs land INSIDE the out dir (gitignored results-raw — the
shipped-config sweep loads every tracked experiments toml; a derived
toml must never be tracked). Roster is scripted-only (teacher preset):
exempt under the covered-minds welfare practice.

Usage:
  screen_dials.py --dial consent|slack --values 0,10,15,20,30 \
      [--seed-base S] [--rollouts 8] [--ticks 4000] [--out DIR]
"""
import argparse
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
BASE_CONFIG = REPO / "experiments" / "gen2-world-draft-2026-10-15.toml"
BC_COLLECT = REPO / "experiments" / "tools" / "bc-collect" / "target" / "release" / "bc-collect"
CONSENT_LINE = ("consent_line = 30.0  # fog-gen1-cert: Biscuit 3.0 anchor "
                "consent gate (owner 2026-09-02); the twin runs it at 0.0")
FAVOURITES = {"Miso": "cuddle", "Biscuit": "play",
              "Kittybear": "bath", "Clementine": "sleep"}  # Pumpkin: none


def derive(dial, value):
    text = BASE_CONFIG.read_text()
    if dial == "consent":
        assert text.count(CONSENT_LINE) == 1, "consent anchor line moved"
        text = text.replace(CONSENT_LINE, f"consent_line = {value:.1f}  # SCREEN VALUE")
    elif dial == "slack":
        assert "comfort_slack" not in text, "draft grew a slack line; re-anchor"
        assert text.count("[behavior]\n") == 1
        text = text.replace("[behavior]\n",
                            f"[behavior]\ncomfort_slack = {value:.1f}  # SCREEN VALUE\n")
    elif dial == "favourite":
        assert "favourite" not in text, "draft grew a favourite; re-anchor"
        if value != 0:
            # The inline table must land on a top-level [[kitty]] key line
            # (after name =), BEFORE the [kitty.needs] sub-table header.
            for name, kind in FAVOURITES.items():
                anchor = f'name = "{name}"'
                assert text.count(anchor) == 1, f"{anchor} moved"
                text = text.replace(
                    anchor,
                    f"{anchor}\nfavourite = {{ {kind} = {value} }}  # SCREEN VALUE")
    else:
        raise SystemExit(f"unknown dial {dial!r}")
    return text


def value_dir(dial, value):
    # consent/slack dirs predate the favourite dial: integer values, v%02d.
    # favourite values are fractional: hundredths, v%03d (v010 = 0.1).
    return f"v{round(value * 100):03d}" if dial == "favourite" else f"v{int(value):02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dial", required=True, choices=["consent", "slack", "favourite"])
    ap.add_argument("--values", default="0,10,15,20,30")
    ap.add_argument("--seed-base", type=int, default=996101)
    ap.add_argument("--rollouts", type=int, default=8)
    ap.add_argument("--ticks", type=int, default=4000)
    ap.add_argument("--out", default=str(pathlib.Path(__file__).parent / "results-raw"))
    a = ap.parse_args()

    for value in [float(v) for v in a.values.split(",")]:
        vdir = pathlib.Path(a.out) / a.dial / value_dir(a.dial, value)
        vdir.mkdir(parents=True, exist_ok=True)
        cfg = vdir / "config.toml"
        cfg.write_text(derive(a.dial, value))
        cmd = [str(BC_COLLECT), "--config", str(cfg),
               "--rollouts", str(a.rollouts), "--ticks", str(a.ticks),
               "--seed-base", str(a.seed_base), "--out-dir", str(vdir), "--trace"]
        print(f"== {a.dial} {value_dir(a.dial, value)} seeds {a.seed_base}.."
              f"{a.seed_base + a.rollouts - 1}", flush=True)
        subprocess.run(cmd, check=True)
    print(f"== {a.dial} done", flush=True)


if __name__ == "__main__":
    main()
