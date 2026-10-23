#!/usr/bin/env python3
"""The five per-cat grave configs g2leg-20-P<k>.toml (DECLARATION.md
§Data): the served g2leg-20.toml byte for byte, plus ONE line inside
kitty k's own [[kitty]] block — spec 065's per-kitty `initial_needs`
inline table, every need drawn in {min 60, max 95} (set G's band) — and a
trailing provenance comment. The other four kitties carry no entry and
start at the served default (every need 0, happiness 100; FR-003
"unspecified needs start at today's zero"). The line sits right after
`name = …`, before the block's [kitty.needs] sub-table, so it belongs to
the kitty, not to its needs table.

    make_configs.py           # writes the five files beside this script
    make_configs.py --check   # exits non-zero if any differs
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERVED = HERE.parent / "gen2-comparator-legs-2026-10-14" / "g2leg-20.toml"
SEATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]
LO, HI = 60, 95
NEEDS = ("eat", "drink", "sleep", "play", "cuddle", "bath")
LINE = "initial_needs = { " + ", ".join(f"{n} = {{ min = {LO}, max = {HI} }}" for n in NEEDS) + " }"


def render(k):
    name = SEATS[k - 1]
    src = SERVED.read_text()
    needle = f'\n[[kitty]]\nid = {k}\nname = "{name}"\n'
    assert src.count(needle) == 1, needle
    insert = (f"# ---- mini-friend Phase 1b set P{k} (minifriend-phase1b-2026-10-23/DECLARATION.md §Data):\n"
              f"# {name} ALONE starts grave — spec 065 per-kitty initial needs, every need drawn in\n"
              f"# {{min {LO}, max {HI}}} at reset (ck-initnd-v1 law, seeded by the world seed). The other four\n"
              f"# kitties carry no entry and start at the served default. Nothing else differs from g2leg-20.toml.\n"
              f"{LINE}\n")
    out = src.replace(needle, needle + insert)
    out += (f"\n# ---- mini-friend Phase 1b set P{k}: g2leg-20.toml as served, plus the one per-kitty\n"
            f"# `initial_needs` line inside {name}'s [[kitty]] block above (make_configs.py).\n")
    return out


def main():
    bad = []
    for k in range(1, 6):
        p = HERE / f"g2leg-20-P{k}.toml"
        text = render(k)
        if "--check" in sys.argv:
            if not p.exists() or p.read_text() != text:
                bad.append(p.name)
        else:
            p.write_text(text)
            print("wrote", p.name)
    if "--check" in sys.argv:
        assert not bad, f"differ from make_configs.py: {bad}"
        print("configs match")


if __name__ == "__main__":
    main()
