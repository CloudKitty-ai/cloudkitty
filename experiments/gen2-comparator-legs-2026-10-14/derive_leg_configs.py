#!/usr/bin/env python3
"""Derive the Gen 2 comparator-leg configs (skeleton §7, freeze sitting
2026-10-17) from the Gen 2 draft world.

Three configs — g2leg-20 / g2leg-40 / g2leg-100 — each the draft plus:

- `[starts] edge_ring_share = 0.25, corner_share = 0.05` (the
  collection share law) and every [[kitty]] x/y REMOVED: spec 062's
  engine draw (draw-law v1) places the roster per WORLD SEED,
  deterministically — the pairing artifact the §7 ruling wants, since
  a trained leg on seed s reproduces the comparator's starts by
  construction, with no per-seed derived configs.
- Sizes 40/100: world.width/height scaled, and every element min/max
  scaled with AREA (x4 / x25) — the §7 gates line, RULED: "Element
  density scaled with area at served per-tile density".

Checks, all hard: toml parse; deep-diff against the draft (exactly the
declared keys differ, nothing else moves); scaled counts equal base x
area ratio; a real engine load per config (bc-collect, 5 ticks, which
also exercises the [starts] knob). SHA-256 printed per config.

    python3 -B derive_leg_configs.py [--out DIR]   # default: this dir
"""
import argparse
import hashlib
import re
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SRC = REPO / "experiments" / "gen2-world-draft-2026-10-15.toml"
BC = REPO / "experiments/tools/bc-collect/target/release/bc-collect"
ELEMENTS = ("water", "chow", "bug", "greeble", "sunbeam")
SIZES = {20: 1, 40: 4, 100: 25}  # size -> area ratio vs the 20x20 draft
STARTS_BLOCK = "[starts]\nedge_ring_share = 0.25\ncorner_share = 0.05\n\n"


def derive(base_text, size, ratio):
    out, section = [], None
    for line in base_text.splitlines(keepends=True):
        header = re.match(r"\[+([\w.]+)\]+", line.strip())
        if header:
            section = header.group(1)
            if section == "world":
                out.append(STARTS_BLOCK)
        m = re.match(r"^(width|height|min|max)\s*=\s*(\d+)\s*$", line.strip())
        if m and section == "world" and m.group(1) in ("width", "height"):
            line = f"{m.group(1)} = {size}\n"
        elif m and section.startswith("elements.") and m.group(1) in ("min", "max"):
            line = f"{m.group(1)} = {int(m.group(2)) * ratio}\n"
        elif section == "kitty" and re.match(r"^[xy]\s*=\s*\d+\s*$", line.strip()):
            continue  # drawn per seed (062 knob-on, x/y absent)
        out.append(line)
    return "".join(out)


def check(base, derived, size, ratio):
    b, d = tomllib.loads(base), tomllib.loads(derived)
    assert d["starts"] == {"edge_ring_share": 0.25, "corner_share": 0.05}
    assert d["world"]["width"] == d["world"]["height"] == size
    for e in ELEMENTS:
        for k in ("min", "max"):
            assert d["elements"][e][k] == b["elements"][e][k] * ratio, (e, k)
    for kb, kd in zip(b["kitty"], d["kitty"]):
        assert "x" not in kd and "y" not in kd, kd.get("name")
        for key in kb:
            if key not in ("x", "y"):
                assert kb[key] == kd[key], (kb.get("name"), key)
    # Nothing else moves: normalize the declared diffs away, then equate.
    d.pop("starts")
    for t in (b, d):
        t["world"]["width"] = t["world"]["height"] = 0
        for e in ELEMENTS:
            t["elements"][e]["min"] = t["elements"][e]["max"] = 0
        for k in t["kitty"]:
            k.pop("x", None), k.pop("y", None)
    assert b == d, f"size{size}: an undeclared key moved"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE)
    a = ap.parse_args()
    base = SRC.read_text()
    for size, ratio in SIZES.items():
        text = derive(base, size, ratio)
        check(base, text, size, ratio)
        p = a.out / f"g2leg-{size}.toml"
        p.write_text(text)
        if not BC.exists():
            raise SystemExit(f"{BC} not built")
        with tempfile.TemporaryDirectory() as td:
            r = subprocess.run([str(BC), "--config", str(p), "--rollouts", "1",
                                "--ticks", "5", "--seed-base", "1",
                                "--out-dir", td],
                               capture_output=True, text=True)
            if r.returncode != 0:
                raise SystemExit(f"size{size} failed engine load:\n{r.stderr[-400:]}")
        print(f"g2leg-{size}.toml  sha256 {hashlib.sha256(text.encode()).hexdigest()[:16]}")


if __name__ == "__main__":
    main()
