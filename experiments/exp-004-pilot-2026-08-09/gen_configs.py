#!/usr/bin/env python3
"""Generates the 30 dial-pricing pilot cells (prereg §6; design-inputs §5).

Sweep: drip {1,2,3,5,15=control} x mutual {off,on} x cuddle_relief
{15=control,8,5}, routing change held constant (whatever the base config
ships is what every cell runs).

Mutual-axis definition (recorded assumption, 2026-08-09): "on" prices the
mutual tier at REST-DUET PARITY -- cosleep_mutual_relief = cuddle_relief,
the config's own launch rule ("both launch equal to cuddle_relief") -- so
the tier tracks axis 3; "off" makes the tier inert (= drip). The control
cell (d15/on/c15) reproduces the shipped 15/15 defaults byte-for-byte.
"""

import re
import sys
from pathlib import Path

BASE = Path(sys.argv[1] if len(sys.argv) > 1 else "cloudkitty.toml")
OUT = Path(__file__).parent / "configs"
OUT.mkdir(exist_ok=True)

text = BASE.read_text()
DIALS = ["cuddle_relief", "cosleep_drip_relief", "cosleep_mutual_relief"]


def patch(text: str, name: str, value: float) -> str:
    pat = re.compile(rf"^{name} = [0-9.]+$", re.M)
    out, n = pat.subn(f"{name} = {value}", text)
    assert n == 1, f"{name}: expected exactly one assignment, found {n}"
    return out


cells = []
for drip in (1, 2, 3, 5, 15):
    for mutual in ("off", "on"):
        for relief in (15, 8, 5):
            m = relief if mutual == "on" else drip
            cell = f"d{drip:02}-m{mutual}-c{relief:02}"
            t = text
            for name, v in zip(DIALS, (float(relief), float(drip), float(m))):
                t = patch(t, name, v)
            (OUT / f"{cell}.toml").write_text(t)
            cells.append(cell)

print(f"wrote {len(cells)} cells to {OUT}")
assert len(cells) == 30
