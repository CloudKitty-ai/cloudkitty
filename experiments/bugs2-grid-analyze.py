#!/usr/bin/env python3
"""Reduce the bugs-2.0 acceptance grid to EV tables and the verdict.

Reads experiments/bugs2-grid/<cell>.txt (chase-census outputs, expiry
tagging included), computes effective value per invested tick with the
per-tick relief semantics (stickers unchanged by 039: solo 10, duet 20
each side, bug 25, greeble 35), and checks the pre-registered bars:

  1. unskilled bug EV > 10 (solo's rate — the gradient exists)
  2. skilled bug EV within [self-duet, team-duet] (opportunistic)
  3. ruin <= ~1% of engaged hunts at ttl 600
  cell rule: adopt the largest roam_cell that clears bar 1.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRID = HERE / (sys.argv[1] if len(sys.argv) > 1 else "bugs2-grid")
PKG = sys.argv[2] if len(sys.argv) > 2 else "pkg"
RELIEF = {"bug": 25.0, "greeble": 35.0}

ROW = re.compile(
    r"^  (bug|greeble): pursuits (\d+) \| chase ticks (\d+) \| catches (\d+)"
    r" \| abandons (\d+) \| chase-ticks/catch \S+ \| catch-rate ([\d.]+)%"
    r" \| pounce starts (\d+) \| play scenes (\d+) \(mean len ([\d.]+)\)"
    r" \| expiry: chase (\d+) scene (\d+)")
DUET = re.compile(
    r"^  kitty-chase ticks (\d+) \| duets: (\d+) starts, (\d+) ticks")


def parse(path):
    out = {}
    beh = None
    for line in path.read_text().splitlines():
        h = re.match(r"^\[(\w+)\]", line)
        if h:
            beh = h.group(1)
            out[beh] = {}
            continue
        m = ROW.match(line)
        if m and beh:
            ty = m.group(1)
            g = [float(x) for x in m.groups()[1:]]
            out[beh][ty] = dict(
                pursuits=g[0], chase=g[1], catches=g[2], abandons=g[3],
                rate=g[4], pounce=g[5], scenes=g[6], mlen=g[7],
                exp_chase=g[8], exp_scene=g[9])
        d = DUET.match(line)
        if d and beh:
            out[beh]["duet"] = dict(
                kchase=float(d.group(1)), starts=float(d.group(2)),
                ticks=float(d.group(3)))
    return out


def ev(row, relief):
    """Effective relief per invested tick: paid ticks over chase + scene.

    `mlen` is the census's MEASURED mean scene length, never the config's
    nominal duration, and the difference is real rather than noise —
    critter play scenes end SHORT of play's 2-tick minimum, so this
    function already carries the early-termination penalty. Do not
    "correct" it toward the nominal length, and do not read a short mlen
    as an instrument fault.

    Why they end short (verified 2026-08-23, engine + live world):
    `World::prune_dead_activity` (world.rs:464) ends an element play
    scene when the element is gone OR no longer adjacent, and pruning
    runs before the duration minimum is enforced. Critters move on
    alternate ticks ((tick + id) % 2), so every critter scene contains
    exactly one move opportunity; when that move breaks adjacency the
    scene dies at one tick. It is NOT the 600-tick ttl — measured scene
    expiry is ~0.3% (15 in 5,244) against a ~20% cut rate.

    Shipped-world means, for orientation when a future census is read:
    bug 1.8 · greeble 1.5 (they dart, so they break adjacency more) ·
    duet 2.0 (a partner does not hop away, and cut rate is 0%). The live
    served world independently reproduces the bug figure: 20% of Biscuit
    2.0's bug scenes ran one tick, and 0.8x2 + 0.2x1 = 1.8 exactly.

    Owner ruled 2026-08-23 to keep the mechanic as it stands (a grace
    tick was costed and dropped), so these are the durable numbers —
    a future census showing bug mlen near 1.8 is the world working.
    """
    scene_ticks = row["scenes"] * row["mlen"]
    inv = row["chase"] + scene_ticks
    return (scene_ticks * relief / inv) if inv else 0.0


def duet_ev(d):
    inv = d["kchase"] + d["ticks"]
    return (d["ticks"] * 20 / inv, d["ticks"] * 40 / inv) if inv else (0, 0)


def ruin(row):
    eng = row["pursuits"] + row["scenes"]
    return (row["exp_chase"] + row["exp_scene"]) / eng if eng else 0.0


def main():
    cells = {}
    for p in sorted(GRID.glob("*.toml.txt")) or sorted(GRID.glob("*.txt")):
        name = p.name.replace(".toml", "").replace(".txt", "")
        cells[name] = parse(p)

    print(f"{'cell':<22} {'skill':<13} {'bugEV':>6} {'grbEV':>6} "
          f"{'duet s/t':>11} {'ruin%':>6} {'catch%':>7}")
    table = {}
    for name, c in sorted(cells.items()):
        for beh, rows in c.items():
            if "bug" not in rows:
                continue
            bev = ev(rows["bug"], RELIEF["bug"])
            gev = ev(rows["greeble"], RELIEF["greeble"]) if "greeble" in rows else 0
            ds, dt = duet_ev(rows["duet"]) if "duet" in rows else (0, 0)
            r = ruin(rows["bug"])
            table[(name, beh)] = dict(bev=bev, ds=ds, dt=dt, ruin=r)
            print(f"{name:<22} {beh:<13} {bev:6.1f} {gev:6.1f} "
                  f"{ds:5.1f}/{dt:5.1f} {100*r:6.2f} {rows['bug']['rate']:7.1f}")

    def cell(name, beh):
        return table.get((name, beh))

    print("\n== Verdict (pre-registered bars) ==")
    for geo in ("g20", "g26"):
        pkg_nd = cell(f"{geo}-{PKG}-nd-pile", "needs_driven")
        pkg_pf = cell(f"{geo}-{PKG}-pf-pile", "playful")
        c3_nd = cell(f"{geo}-c3-nd-pile", "needs_driven")
        if not (pkg_nd and pkg_pf):
            continue
        b1 = pkg_nd["bev"] > 10.0
        b2 = pkg_pf["ds"] <= pkg_pf["bev"] <= pkg_pf["dt"]
        b3 = max(pkg_nd["ruin"], pkg_pf["ruin"]) <= 0.012
        print(f"[{geo}] bar1 unskilled bugEV {pkg_nd['bev']:.1f} > 10: "
              f"{'PASS' if b1 else 'FAIL'} | bar2 skilled {pkg_pf['bev']:.1f} "
              f"in [{pkg_pf['ds']:.1f}, {pkg_pf['dt']:.1f}]: "
              f"{'PASS' if b2 else 'FAIL'} | bar3 ruin "
              f"{100*max(pkg_nd['ruin'], pkg_pf['ruin']):.2f}% <= ~1%: "
              f"{'PASS' if b3 else 'FAIL'}")
        if c3_nd:
            print(f"[{geo}] cell rule: 4x4 unskilled {pkg_nd['bev']:.1f}, "
                  f"3x3 unskilled {c3_nd['bev']:.1f} -> adopt "
                  f"{'4x4' if b1 else ('3x3' if c3_nd['bev'] > 10 else 'NEITHER')}")


if __name__ == "__main__":
    main()
