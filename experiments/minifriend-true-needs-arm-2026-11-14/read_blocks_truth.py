#!/usr/bin/env python3
"""The block read on the true-needs arm's recorded legs (DECLARATION.md §6, §7 T3; the needs arm's reader at C = 9).
Dump-only: one replay per world of the 12M checkpoint's RECORDED uniform legs, the truth cells rebuilt from the
replay's start-of-tick engine state exactly as the harness seat built them, no world served, zero covered cost.
  leg    per world, per block (truth = cells 0–7, tsl = cell 8, all): the decision rows whose greedy act changes when
         the block is ZEROED (T3's quantity) or PERMUTED across the seat's own ticks, on all rows and on GRAVE rows
         (some friend's truth cell 7 is 1: she is grave by strata.stratum). Fences: the recorded act is a maximiser of
         the replayed masked logits; "all" zeroed equals the trainer's own cells-in-use count on the same rows.
  score  per size with a whole leg read: pooled shares; T3 (the truth cells drive at least 0.025 of acts at both
         sizes, and more on grave rows than on others).
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_blocks_truth.py leg <size> [--seeds a,b] [--workers 6] --out reads/blocks/<seating>-<size>.json   (about 10 minutes a leg)
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_blocks_truth.py score --dir reads/blocks --out reads/blocks/score.json [--md]
(A = ../minifriend-phase2-2026-11-06.) The ablation, the blocks and the fences are the needs arm's and Phase 2's, imported.
"""
import argparse
import json
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "minifriend-needs-arm-2026-11-12"))
import read_r1_truth as R1T  # noqa: E402
import read_blocks_needs as BN  # noqa: E402  (ablate, BLOCKS, PG, W at C = 9; RB, R5, P: the fences)
import cert_harness_fog as H  # noqa: E402
HO, RB, R5, P, C, RP = BN.HO, BN.RB, BN.R5, BN.P, BN.C, BN.RP

SEATING, SIZES, WORLDS = R1T.CKPT, (20, 40), 30
BLOCKS = {"truth": BN.BLOCKS["needs"], "tsl": BN.BLOCKS["tsl"], "all": BN.BLOCKS["all"]}
BLOCK_OF = {"truth": "needs", "tsl": "tsl", "all": "all"}   # the needs reader's name for the same cells
GRAVE = BN.PG                                               # cell 7: 1 if the friend is grave
T3_SHARE = 0.025


def world(job):
    seating, size, seed, raw = job
    rows = R1T.RR.leg(seating, size, Path(raw))
    actor = HO.actor_from_artifact(H.artifact_path(H.SEATINGS[seating][0]), n_obs=C.ROSTER)[0]
    assert actor.arm == "truth" and actor.policy.cells == BN.W, (actor.arm, actor.policy.cells)
    policy = actor.policy
    O, CL, M, AR, TK = [], [], [], [], []
    for rec in RP.replay(RP.acts_path(seating, size, seed, Path(raw)), C.LEG_TOML[size], want_obs=True, check_row=rows[seed]):
        _x, cells = actor.widen(rec["obs"], rec["state"])
        O.append(rec["obs"]); CL.append(cells); M.append(rec["mask"]); AR.append(rec["acts"][:, 0]); TK.append(rec["tick"])
    O, CL, M, AR = np.stack(O), np.stack(CL), np.stack(M), np.stack(AR)                   # (T, R, …)
    w = {"seed": seed, "rows": 0, "free_rows": 0, "grave_rows": 0, "ties": 0, "trainer_changed": 0,
         **{m: {b: {"changed": 0, "changed_grave": 0} for b in BLOCKS} for m in RB.MODES}}
    with tempfile.TemporaryDirectory() as td:
        dump = Path(td) / "rows.npz"
        for i in range(C.ROSTER):                                                         # one seat at a time, as the needs reader
            obs, cells, mask, ar = O[:, i], CL[:, i], M[:, i], AR[:, i]
            ml = RB.masked_logits(policy, obs, cells, mask)
            for j in np.flatnonzero(ml.argmax(1) != ar):                                  # the act fence (raises unless a tie)
                w["ties"] += int(R5.fence_act(ml[j], int(ar[j]), TK[j], i)[1])
            base = ml.argmax(1)
            grave = cells[:, :, GRAVE].max(1) >= RB.FLAG
            w["rows"] += len(obs); w["free_rows"] += int((mask[:, :RB.N_ACT].sum(1) >= 2).sum()); w["grave_rows"] += int(grave.sum())
            for bi, b in enumerate(BLOCKS):
                for m in RB.MODES:
                    ch = RB.masked_logits(policy, obs, BN.ablate(cells, BLOCK_OF[b], m, np.random.default_rng([seed, i, bi])), mask).argmax(1) != base
                    w[m][b]["changed"] += int(ch.sum()); w[m][b]["changed_grave"] += int((ch & grave).sum())
            np.savez(dump, obs=obs, cells=cells, mask=mask)
            r = P.cells_in_use(policy, dump, policy.cells)
            w["trainer_changed"] += int(round(r["changed_share"] * r["rows"]))
    assert w["zero"]["all"]["changed"] == w["trainer_changed"], \
        f"FENCE: {seating} {size} world {seed}: all cells zeroed changes {w['zero']['all']['changed']} of {w['rows']} rows, the trainer's cells-in-use counts {w['trainer_changed']}"
    print("world", seed, json.dumps(w), flush=True)
    return w


def leg(size, seeds=None, seating=SEATING, raw=R1T.RAW, workers=1):
    seeds = sorted(R1T.RR.leg(seating, size, raw)) if seeds is None else seeds
    jobs = [(seating, size, s, str(raw)) for s in seeds]
    if workers > 1:
        with ProcessPoolExecutor(workers) as ex:
            ws = list(ex.map(world, jobs))
    else:
        ws = [world(j) for j in jobs]
    return {"seating": seating, "size": size, "blocks": BLOCKS, "worlds": ws}


def t3(shares):
    """T3 on {size: zero/truth's {all_rows, grave, others}}: at least 0.025 of acts at both sizes and more on grave
    rows than on others at both; a size under the grave-row minimum (grave None) leaves the second half unscored."""
    a = all(shares[z]["all_rows"] >= T3_SHARE for z in SIZES)
    b = None if any(shares[z]["grave"] is None for z in SIZES) else all(shares[z]["grave"] > shares[z]["others"] for z in SIZES)
    return {"a_share_at_least_0.025": a, "b_grave_above_others": b, "met": None if b is None and a else bool(a and b)}


def score(d, seating=SEATING, raw=R1T.RAW):
    res = {"legs": {}, "missing": []}
    for size in SIZES:
        f = d / f"{seating}-{size}.json"
        if not f.exists():
            res["missing"].append(size)
            continue
        ws = {w["seed"]: w for w in json.loads(f.read_text())["worlds"]}
        rows = R1T.RR.leg(seating, size, raw)
        assert len(ws) == WORLDS and set(ws) == set(rows), f"{seating} {size}: {len(ws)} worlds read, {len(rows)} leg rows — a partial leg is never scored"
        tot = lambda k: sum(w[k] for w in ws.values())                                    # noqa: E731
        n, free, gr = tot("rows"), tot("free_rows"), tot("grave_rows")
        leg_ = {"size": size, "worlds": len(ws), "rows": n, "free_rows": free, "grave_rows": gr, "ties": tot("ties"), "share": {}}
        for m in RB.MODES:
            for b in BLOCKS:
                ch = sum(w[m][b]["changed"] for w in ws.values()); cg = sum(w[m][b]["changed_grave"] for w in ws.values())
                leg_["share"][f"{m}/{b}"] = {"all_rows": ch / n, "free_choice": ch / free, "grave": cg / gr if gr >= RB.MIN_N else None, "others": (ch - cg) / (n - gr)}
        res["legs"][str(size)] = leg_
    if not res["missing"]:
        res["T3"] = t3({z: res["legs"][str(z)]["share"]["zero/truth"] for z in SIZES})
    return res


def md(res):
    f = lambda v: "INSUFFICIENT" if v is None else f"{v:.4f}"                             # noqa: E731
    out = [f"# The block read on the true-needs arm ({SEATING}'s recorded uniform legs; 30 worlds a leg)", "",
           "Share = decision rows whose greedy act changes when the block's cells are zeroed (zero) or permuted across the seat's own ticks (perm). "
           "Blocks: truth = each friend's true needs, happiness, bath and GRAVE flag; tsl = the time-since-live cell; all = every appended cell. "
           f"Grave rows = some friend is grave by the engine's state; under {RB.MIN_N} grave rows a leg reads INSUFFICIENT.", "",
           "| size | mode | block | all rows | free-choice rows | grave rows | other rows |", "|---|---|---|---|---|---|---|"]
    for size, v in res["legs"].items():
        for key, s in v["share"].items():
            m, b = key.split("/")
            out.append(f"| {size}×{size} | {m} | {b} | {s['all_rows']:.4f} | {s['free_choice']:.4f} | {f(s['grave'])} | {s['others']:.4f} |")
    out += ["", "| size | rows | free-choice rows | grave rows | ties |", "|---|---|---|---|---|"]
    out += [f"| {z}×{z} | {v['rows']:,} | {v['free_rows']:,} | {v['grave_rows']:,} | {v['ties']} |" for z, v in res["legs"].items()]
    if "T3" in res:
        t = res["T3"]
        out += ["", f"**T3 {'UNSCORED (too few grave rows)' if t['met'] is None else 'MET' if t['met'] else 'NOT MET'}** (a: the truth cells drive at least {T3_SHARE} of acts at both sizes: "
                f"{t['a_share_at_least_0.025']}; b: more on grave rows than on others at both: {t['b_grave_above_others']})."]
    out += ["", "Not read: " + (", ".join(f"{z}×{z}" for z in res["missing"]) or "none") + "."]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("leg"); a.add_argument("size", type=int); a.add_argument("--seeds", default=None); a.add_argument("--workers", type=int, default=6)
    a.add_argument("--out", type=Path, required=True)
    b = sub.add_parser("score"); b.add_argument("--dir", type=Path, required=True); b.add_argument("--out", type=Path, required=True)
    b.add_argument("--md", action="store_true")
    args = ap.parse_args()
    if args.cmd == "leg":
        res = leg(args.size, [int(s) for s in args.seeds.split(",")] if args.seeds else None, workers=args.workers)
    else:
        res = score(args.dir)
        if args.md:
            args.out.with_suffix(".md").write_text(md(res))
        print(json.dumps(res.get("T3")))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(res, indent=1) + "\n")
