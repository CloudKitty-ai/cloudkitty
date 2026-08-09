#!/usr/bin/env python3
"""A1's shaped family: the v5 family verbatim + [rl.reward.shaping].

Arm A1 (prereg §3) differs from A0 by exactly one registered block —
Φ(s) = −c × (active distress entries / roster), c = 0.5, γ_Φ = 0.998
PINNED = training γ (the compiled default 1.0 silently voids the
invariance proof). The shaping is engine-side (spec 028 FR-009): the
trainer sees only the shaped reward, so the arm IS the config.

Deterministic append; regenerating after a family change reproduces
byte-for-byte from the source family.
"""

from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
SRC = EXP / "family"
DST = EXP / "family-a1-shaped"
DST.mkdir(exist_ok=True)

BLOCK = """
# Arm A1 (exp-004 prereg §3): potential-based distress shaping, the one
# registered difference from A0. gamma is PINNED to the training gamma —
# an unmatched gamma_Phi voids the invariance proof and the arm.
[rl.reward.shaping]
enabled = true
gamma = 0.998
distress_coefficient = 0.5
"""

n = 0
for src in sorted(SRC.glob("family-*.toml")):
    text = src.read_text()
    assert "[rl.reward.shaping]" not in text, f"{src.name} already shaped"
    (DST / src.name).write_text(text + BLOCK)
    n += 1
assert n == 15, n
print(f"wrote {n} shaped variants to {DST}")
