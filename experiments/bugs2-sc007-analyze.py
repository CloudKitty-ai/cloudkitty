#!/usr/bin/env python3
"""SC-007 amended census reducer (d06f0b4: greeble dart schedule).

Pre-registered bars (spec-input §Greeble-schedule + §THE RULING):
  bug bars re-verified at sticker 28:
    B1 unskilled bug EV > 10        B2 skilled bug EV in [self-duet, team-duet]
    B3 bug ruin <= ~1% both rows
  greeble bars at sticker 35:
    G1 skilled greeble EV < team-duet EV (both geometries)
    G2 greeble ruin <= ~1% (both skill rows)
  ordering: bug-vs-greeble EV per row — REPORT, escalate on flip
  Biscuit-cost read: playful chase-tick spend + EVs vs b044827 sweep r28.
"""
import importlib.util
import sys
from pathlib import Path

SP = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "grid_analyze",
    "/Users/elizabethkelly/ai/cloudkitty/experiments/bugs2-grid-analyze.py")
ga = importlib.util.module_from_spec(spec)
spec.loader.exec_module.__self__ if False else spec.loader.exec_module(ga)

RELIEF = {"bug": 28.0, "greeble": 35.0}


def reduce_cell(path):
    c = ga.parse(path)
    out = {}
    for beh, rows in c.items():
        if "bug" not in rows:
            continue
        ds, dt = ga.duet_ev(rows["duet"]) if "duet" in rows else (0, 0)
        out[beh] = dict(
            bev=ga.ev(rows["bug"], RELIEF["bug"]),
            gev=ga.ev(rows["greeble"], RELIEF["greeble"]),
            ds=ds, dt=dt,
            bruin=ga.ruin(rows["bug"]),
            gruin=ga.ruin(rows["greeble"]),
            bchase=rows["bug"]["chase"], gchase=rows["greeble"]["chase"],
            bcatch=rows["bug"]["rate"], gcatch=rows["greeble"]["rate"],
        )
    return out


def main():
    cells = {}
    for geo in ("g20", "g26"):
        nd = reduce_cell(SP / "sc007" / f"{geo}-r28-nd-pile-dart.txt")
        pf = reduce_cell(SP / "sc007" / f"{geo}-r28-pf-pile-dart.txt")
        cells[geo] = dict(nd=nd["needs_driven"], pf=pf["playful"])

    print(f"{'cell':<10} {'bugEV':>6} {'grbEV':>6} {'duet s/t':>11} "
          f"{'bruin%':>7} {'gruin%':>7} {'bcatch%':>8} {'gcatch%':>8}")
    for geo, rows in cells.items():
        for skill, r in rows.items():
            print(f"{geo}-{skill:<6} {r['bev']:6.1f} {r['gev']:6.1f} "
                  f"{r['ds']:5.1f}/{r['dt']:5.1f} {100*r['bruin']:7.2f} "
                  f"{100*r['gruin']:7.2f} {r['bcatch']:8.1f} {r['gcatch']:8.1f}")

    print("\n== Verdict (pre-registered bars) ==")
    for geo, rows in cells.items():
        nd, pf = rows["nd"], rows["pf"]
        b1 = nd["bev"] > 10.0
        b2 = pf["ds"] <= pf["bev"] <= pf["dt"]
        b3 = max(nd["bruin"], pf["bruin"]) <= 0.012
        g1 = pf["gev"] < pf["dt"]
        g2 = max(nd["gruin"], pf["gruin"]) <= 0.012
        print(f"[{geo}] B1 unskilled bugEV {nd['bev']:.1f} > 10: "
              f"{'PASS' if b1 else 'FAIL'} | B2 skilled bugEV {pf['bev']:.1f} "
              f"in [{pf['ds']:.1f}, {pf['dt']:.1f}]: {'PASS' if b2 else 'FAIL'}"
              f" | B3 bug ruin {100*max(nd['bruin'], pf['bruin']):.2f}%: "
              f"{'PASS' if b3 else 'FAIL'}")
        print(f"[{geo}] G1 skilled grbEV {pf['gev']:.1f} < team-duet "
              f"{pf['dt']:.1f}: {'PASS' if g1 else 'FAIL'} | G2 greeble ruin "
              f"{100*max(nd['gruin'], pf['gruin']):.2f}%: "
              f"{'PASS' if g2 else 'FAIL'}")
        print(f"[{geo}] ordering (report): unskilled grb {nd['gev']:.1f} vs "
              f"bug {nd['bev']:.1f} -> "
              f"{'grb>bug FLIP' if nd['gev'] > nd['bev'] else 'bug first, holds'}"
              f" | skilled grb {pf['gev']:.1f} vs bug {pf['bev']:.1f} -> "
              f"{'grb>bug FLIP' if pf['gev'] > pf['bev'] else 'bug first, holds'}")


if __name__ == "__main__":
    main()
