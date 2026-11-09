#!/usr/bin/env python3
"""R-5 — the regime × confidence read (DECLARATION.md §6 R-5; guard g8). On each arm's recorded legs, replayed by
their recorded actions with the arm's heads inline (the cells the arm saw are recomputed on the observer's own
stream, g2), the TRUNK SEED the arm was grafted from is run counterfactually on the SAME observation (the un-widened
rows; zero collection, nothing decides) and the share of ticks the arm's greedy act differs from the trunk's is binned
by the friend row's regime (seen / heard) × the head's normalised-entropy tercile (terciles fitted within regime over
the leg's live rows), per friend row with a live head cell; the discount is LEARNED if divergence is largest in sight at
low entropy and smallest heard at high entropy — the WITHIN-regime ordering is P44's registered half, the cross-regime
ordering a read. The no-head arm's divergence from its trunk seed (no cells; all its rows) is the training-alone floor.
Leash-bounded by construction (the anchor cannot see the cells).

    read_r5.py --seating p2u-act15-s1 --size 20 [--seeds 905001,905002] --out reads/r5/p2u-act15-s1-20.json
    read_r5.py score --out reads/r5.json [--md]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p2_common as C  # noqa: E402
import replay as RP  # noqa: E402
import graft as G  # noqa: E402
import heads_online as HO  # noqa: E402
import data_act as D  # noqa: E402

READS = HERE / "reads"
REGIMES = ("seen", "heard")
TERCILES = ("low", "mid", "high")
N_ACT = 35
ENT_COL = D.N_ACTS + 1          # cells: 11 probs, top (11), entropy (12), ticks-since-live (13)


def divergence_rows(seating, size, seed, root=None):
    """Replay one world with every p2 seat's actor beside its trunk seed; returns per (tick, observer seat with a p2
    arm, friend row) records: regime (0 seen / 1 heard / 2 silent), entropy, differ (arm act != trunk act), plus the
    per-tick arm-vs-trunk differ flag per observer."""
    rows, header = RP.leg_rows(seating, size, root)
    seats = header["seats"]
    row = rows[seed]
    actors, trunks = {}, {}
    for i, spec in enumerate(seats):
        if spec.startswith("p2:"):
            slot = spec.split(":", 1)[1]
            actor, ck = HO.actor_from_artifact(C.ARTS / slot / "policy-final.pt", n_obs=1)
            actors[i] = actor
            trunk, _ = G.load_trunk(ck["trunk_seed"])
            trunks[i] = trunk
    assert actors, f"{seating} seats no p2 arm"
    out = {"regime": [], "entropy": [], "differ_row": [], "differ_tick": [], "observer": [], "friend_row": []}
    ties = 0
    for a in actors.values():
        a.reset()
    for rec in RP.replay(RP.acts_path(seating, size, seed, root), C.LEG_TOML[size], want_obs=True, check_row=row):
        obs, mask = rec["obs"], rec["mask"]
        for i, actor in actors.items():
            o = obs[i:i + 1]
            x, cells = actor.widen(o)
            with torch.no_grad():
                la = actor.policy(torch.from_numpy(x))[0, :N_ACT].numpy()
                lt = trunks[i](torch.from_numpy(o))[0, :N_ACT].numpy()
            m = mask[i, :N_ACT]
            ml = np.where(m, la, -np.inf)
            a_tr = int(np.where(m, lt, -np.inf).argmax())
            a_arm, tied = fence_act(ml, int(rec["acts"][i, 0]), rec["tick"], i)
            ties += int(tied)
            differ = a_arm != a_tr
            blk = o[0, C.SELF_BLOCK:C.SELF_BLOCK + C.N_ROWS * C.KITTY_W].reshape(C.N_ROWS, C.KITTY_W)
            st = HO.row_states(blk)
            for r in range(C.N_ROWS):
                out["regime"].append(int(st[r])); out["entropy"].append(float(cells[0, r, ENT_COL]) if actor.heads.head is not None else float("nan"))
                out["differ_row"].append(bool(differ)); out["observer"].append(i); out["friend_row"].append(r)
            out["differ_tick"].append(bool(differ))
    return {k: np.asarray(v) for k, v in out.items()}, {"seating": seating, "size": size, "seed": seed, "arm_seats": sorted(actors), "ties": ties}


TIE_TOL = 1e-5


def fence_act(masked_logits, a_rec, tick, seat):
    """The replay fence on the arm's act: the RECORDED act must be a maximiser of the replayed masked logits within
    TIE_TOL (the harness picks the argmax of a BATCHED forward over the seating's rows, the reader of a single-row
    forward; the two agree to the last float bits and disagree only on ties — 2026-11-09, p2u-act15-s1 world 905015
    tick 19,417 seat 3: acts 31 and 33 both at logit 9.468924, the record took 33, the replay's argmax 31). Returns
    (the recorded act, tied) — the arm's act for the divergence read is what it DID; a recorded act that is not a
    maximiser is a replay failure and raises."""
    best = float(masked_logits.max())
    gap = best - float(masked_logits[a_rec])
    assert np.isfinite(gap) and gap <= TIE_TOL, (f"the replayed arm act differs from the record at tick {tick} (seat {seat}): "
                                                 f"recorded {a_rec} at logit {float(masked_logits[a_rec]):.6f}, max {best:.6f}")
    return a_rec, int(masked_logits.argmax()) != a_rec


def bin_divergence(regime, entropy, differ, has_head=True):
    """{regime: {tercile: {n, divergence}}} with terciles fitted within regime over the live rows; the no-head arm
    (entropy nan) binned by regime only. Silent rows (no live cell) are left out."""
    out = {}
    for ri, rname in enumerate(REGIMES):
        sel = regime == ri
        n = int(sel.sum())
        if n == 0:
            out[rname] = {"n": 0}
            continue
        if not has_head:
            out[rname] = {"n": n, "divergence": float(differ[sel].mean())}
            continue
        e = entropy[sel]
        q1, q2 = np.quantile(e, [1 / 3, 2 / 3])
        terc = np.where(e <= q1, 0, np.where(e <= q2, 1, 2))
        out[rname] = {"n": n, "tercile_edges": [float(q1), float(q2)], "divergence": float(differ[sel].mean())}
        for ti, tname in enumerate(TERCILES):
            s2 = terc == ti
            out[rname][tname] = {"n": int(s2.sum()), "divergence": float(differ[sel][s2].mean()) if s2.any() else None}
    return out


def within_regime_ordering(binned):
    """P44's registered half: inside each regime, divergence low-entropy > high-entropy. Returns {regime: bool|None}."""
    out = {}
    for r in REGIMES:
        b = binned.get(r, {})
        lo, hi = b.get("low", {}).get("divergence"), b.get("high", {}).get("divergence")
        out[r] = None if lo is None or hi is None else bool(lo > hi)
    return out


def read_leg(seating, size, root=None, seeds=None):
    rows, _h = RP.leg_rows(seating, size, root)
    acc = {k: [] for k in ("regime", "entropy", "differ_row", "differ_tick")}
    meta, ties = None, 0
    for seed in (sorted(rows) if seeds is None else seeds):
        d, meta = divergence_rows(seating, size, seed, root)
        ties += meta["ties"]
        for k in acc:
            acc[k].append(d[k])
    acc = {k: np.concatenate(v) for k, v in acc.items()}
    has_head = not np.isnan(acc["entropy"]).all()
    binned = bin_divergence(acc["regime"], acc["entropy"], acc["differ_row"], has_head)
    return {**meta, "ties": ties, "worlds": len(rows) if seeds is None else len(seeds), "tick_divergence": float(acc["differ_tick"].mean()),
            "binned": binned, "within_regime_low_gt_high": within_regime_ordering(binned) if has_head else None}


def score():
    out = {}
    for p in sorted((READS / "r5").glob("*.json")):
        out[p.stem] = json.loads(p.read_text())
    return out


def md(out):
    L = ["# R-5 — regime × confidence divergence from the trunk seed", "", "| leg | tick divergence | seen low / mid / high | heard low / mid / high | within-regime low > high |", "|---|---|---|---|---|"]
    for name, r in out.items():
        def cell(reg):
            b = r["binned"].get(reg, {})
            if "low" not in b:
                return f"{b.get('divergence')}"
            return " / ".join(f"{b[t]['divergence']:.3f}" if b[t]["divergence"] is not None else "—" for t in TERCILES)
        L.append(f"| {name} | {r['tick_divergence']:.3f} | {cell('seen')} | {cell('heard')} | {r['within_regime_low_gt_high']} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="leg", choices=["leg", "score"])
    ap.add_argument("--seating")
    ap.add_argument("--size", type=int)
    ap.add_argument("--seeds", default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--root", type=Path, default=None)
    a = ap.parse_args()
    torch.set_num_threads(1)
    if a.cmd == "leg":
        seeds = None if a.seeds is None else [int(s) for s in a.seeds.split(",")]
        out = read_leg(a.seating, a.size, a.root, seeds)
        p = a.out or READS / "r5" / f"{a.seating}-{a.size}.json"
    else:
        out = score()
        p = a.out or READS / "r5.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=1) + "\n")
    if a.md and a.cmd == "score":
        p.with_suffix(".md").write_text(md(out))
        print(md(out))
    else:
        print(json.dumps({k: v for k, v in out.items() if k != "binned"}, indent=1) if a.cmd == "leg" else f"wrote {p}")


if __name__ == "__main__":
    main()
