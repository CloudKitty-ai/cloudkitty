#!/usr/bin/env python3
"""The block read on the needs-only arm's recorded legs (DECLARATION.md §6, §7 N3; entry 33's read at C = 9).
Dump-only: one replay per world of p2u-needs-s<k>'s RECORDED uniform legs, the needs head stepped online over the
recorded observations, no world served, zero covered cost. The arm appends 9 cells a friend row: needs (the seven
estimates + P(grave), at offset 0 — there is no act head) and tsl (ticks since live).
  leg    per world, per block and "all": the decision rows whose greedy act changes when the block is ZEROED (N3's
         quantity) and when it is PERMUTED across the seat's own ticks (descriptive), on all rows and on FLAGGED rows
         (some friend row's P(grave) cell >= 0.5). Fences: the recorded act is a maximiser of the replayed masked
         logits (read_r5.fence_act); "all" zeroed equals the trainer's own cells-in-use count on the same rows
         (train_ppo_p2.cells_in_use).
  score  per size with a whole leg read: pooled shares; the worlds ranked by needs-block share against the paired
         team-happiness delta over the same-seed no-head leg (descriptive); N3 per size.
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_blocks_needs.py leg <size> [--seeds a,b] --out reads/blocks/p2u-needs-s1-<size>.json
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_blocks_needs.py score --dir reads/blocks --out reads/blocks/score.json [--md]
(A = experiments/minifriend-phase2-2026-11-06.)
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P2 = HERE.parent / "minifriend-phase2-2026-11-06"
sys.path.insert(0, str(P2))
sys.path.insert(0, str(HERE.parent / "gen2-trunk-continuation-2026-11-10"))
import p2_common as C  # noqa: E402
import replay as RP  # noqa: E402
import heads_online as HO  # noqa: E402
import read_r5 as R5  # noqa: E402
import read_r1 as R1  # noqa: E402
import train_ppo_p2 as P  # noqa: E402  (cells_in_use: the trainer's own ablation, the fence)
import read_blocks as RB  # noqa: E402  (masked_logits, FLAG, MIN_N, MODES: entry 33's reader)

ARM, SEED, SIZES, WORLDS = "needs", 1, (20, 40, 100), 30
SEATING, PAIR = f"p2u-needs-s{SEED}", f"p2u-nohead-s{SEED}"
W = HO.ARMS[ARM]["cells"]
OFF = HO.needs_off(ARM)
BLOCKS = {"needs": (OFF, OFF + HO.NEEDS_CELLS), "tsl": (OFF + HO.NEEDS_CELLS, W)}
assert sorted(c for a, b in BLOCKS.values() for c in range(a, b)) == list(range(W)), f"the blocks do not partition the arm's {W} cells: {BLOCKS}"
BLOCKS["all"] = (0, W)
PG = OFF + HO.NEEDS_CELLS - 1                               # the P(grave) cell of a friend row
N3_SHARE = 0.010
TERCILES = ("bottom", "mid", "top")


def ablate(cells, block, mode, rng):
    a, b = BLOCKS[block]
    out = cells.copy()
    out[:, :, a:b] = 0.0 if mode == "zero" else cells[rng.permutation(len(cells))][:, :, a:b]
    return out


def leg(size, seeds=None):
    rows, header = RP.leg_rows(SEATING, size, None)
    specs = header["seats"]
    assert len(set(specs)) == 1 and specs[0].startswith("p2:"), f"a uniform Phase 2 seating is read, got {specs}"
    actors = [HO.actor_from_artifact(C.ARTS / specs[0].split(":", 1)[1] / "policy-final.pt", n_obs=1)[0] for _ in specs]
    arm, policy = actors[0].arm, actors[0].policy
    assert arm == ARM and policy.cells == W, (arm, policy.cells)
    out = {"seating": SEATING, "size": size, "arm": arm, "policy": specs[0], "blocks": BLOCKS, "worlds": []}
    with tempfile.TemporaryDirectory() as td:
        dump = Path(td) / "rows.npz"
        for seed in (sorted(rows) if seeds is None else seeds):
            for a in actors:
                a.reset()
            O, CL, M, AR, TK = ([[] for _ in actors] for _ in range(5))
            for rec in RP.replay(RP.acts_path(SEATING, size, seed, None), C.LEG_TOML[size], want_obs=True, check_row=rows[seed]):
                for i, actor in enumerate(actors):
                    o = rec["obs"][i:i + 1]
                    _x, cells = actor.widen(o)
                    O[i].append(o[0]); CL[i].append(cells[0]); M[i].append(rec["mask"][i]); AR[i].append(int(rec["acts"][i, 0])); TK[i].append(rec["tick"])
            w = {"seed": seed, "rows": 0, "free_rows": 0, "flagged_rows": 0, "ties": 0, "trainer_changed": 0,
                 **{m: {b: {"changed": 0, "changed_flagged": 0} for b in BLOCKS} for m in RB.MODES}}
            for i in range(len(actors)):                                      # one seat at a time: 20k rows a forward
                obs, cells, mask = np.stack(O[i]), np.stack(CL[i]), np.stack(M[i])
                ml = RB.masked_logits(policy, obs, cells, mask)
                for j in np.flatnonzero(ml.argmax(1) != np.asarray(AR[i])):   # the act fence (raises unless a tie)
                    w["ties"] += int(R5.fence_act(ml[j], AR[i][j], TK[i][j], i)[1])
                base = ml.argmax(1)
                flagged = cells[:, :, PG].max(1) >= RB.FLAG
                w["rows"] += len(obs); w["free_rows"] += int((mask[:, :RB.N_ACT].sum(1) >= 2).sum()); w["flagged_rows"] += int(flagged.sum())
                for bi, b in enumerate(BLOCKS):
                    for m in RB.MODES:
                        ch = RB.masked_logits(policy, obs, ablate(cells, b, m, np.random.default_rng([seed, i, bi])), mask).argmax(1) != base
                        w[m][b]["changed"] += int(ch.sum()); w[m][b]["changed_flagged"] += int((ch & flagged).sum())
                np.savez(dump, obs=obs, cells=cells, mask=mask)
                r = P.cells_in_use(policy, dump, policy.cells)
                w["trainer_changed"] += int(round(r["changed_share"] * r["rows"]))
            assert w["zero"]["all"]["changed"] == w["trainer_changed"], \
                (f"FENCE: {SEATING} {size} world {seed}: all cells zeroed changes {w['zero']['all']['changed']} of {w['rows']} rows, "
                 f"the trainer's cells-in-use counts {w['trainer_changed']}")
            out["worlds"].append(w)
            print("world", seed, json.dumps(w), flush=True)
    return out


def score(d):
    res = {"legs": {}, "missing": []}
    for size in SIZES:
        f = d / f"{SEATING}-{size}.json"
        if not f.exists():
            res["missing"].append(size)
            continue
        ws = {w["seed"]: w for w in json.loads(f.read_text())["worlds"]}
        arm_rows, _h = RP.leg_rows(SEATING, size, None)
        pair_rows, _h = RP.leg_rows(PAIR, size, None)
        assert len(ws) == WORLDS and set(ws) == set(arm_rows) == set(pair_rows), \
            f"{SEATING} {size}: {len(ws)} worlds read, {len(arm_rows)} arm rows, {len(pair_rows)} no-head rows — a partial leg is never scored"
        tot = lambda k: sum(w[k] for w in ws.values())
        rows, free, flg = tot("rows"), tot("free_rows"), tot("flagged_rows")
        leg_ = {"size": size, "worlds": len(ws), "rows": rows, "free_rows": free, "flagged_rows": flg, "ties": tot("ties"), "share": {}}
        for m in RB.MODES:
            for b in BLOCKS:
                ch = sum(w[m][b]["changed"] for w in ws.values()); cf = sum(w[m][b]["changed_flagged"] for w in ws.values())
                leg_["share"][f"{m}/{b}"] = {"all_rows": ch / rows, "free_choice": ch / free,
                                             "flagged": cf / flg if flg >= RB.MIN_N else None, "unflagged": (ch - cf) / (rows - flg)}
        share = lambda s: ws[s]["zero"]["needs"]["changed"] / ws[s]["rows"]
        seeds = sorted(ws, key=lambda s: (share(s), s))
        delta = {s: R1.team(arm_rows[s]) - R1.team(pair_rows[s]) for s in seeds}
        k = WORLDS // 3
        rk = lambda v: np.argsort(np.argsort(v))
        leg_["needs_share_vs_delta_nohead"] = {
            "paired_delta_mean": float(np.mean(list(delta.values()))),
            "terciles": {name: float(np.mean([delta[s] for s in seeds[i * k:(i + 1) * k]])) for i, name in enumerate(TERCILES)},
            "spearman": float(np.corrcoef(rk(np.asarray([share(s) for s in seeds])), rk(np.asarray([delta[s] for s in seeds])))[0, 1])}
        z = leg_["share"]["zero/needs"]
        leg_["N3"] = {"a_share_at_least_0.010": z["all_rows"] >= N3_SHARE,
                      "b_flagged_above_unflagged": None if z["flagged"] is None else z["flagged"] > z["unflagged"]}
        res["legs"][str(size)] = leg_
    return res


def md(res):
    f = lambda v: "INSUFFICIENT" if v is None else f"{v:.4f}"
    out = ["# The block read on the needs-only arm (p2u-needs-s1's recorded uniform legs; 30 worlds a leg)", "",
           "Share = decision rows whose greedy act changes when the block's cells are zeroed (zero) or permuted across the "
           "seat's own ticks (perm). Blocks: needs = the needs head's seven estimates + P(grave); tsl = the time-since-live "
           f"cell; all = every appended cell. Flagged = rows where some friend row's P(grave) cell is at least {RB.FLAG}; "
           f"under {RB.MIN_N} flagged rows a leg reads INSUFFICIENT.", "",
           "| size | mode | block | all rows | free-choice rows | flagged rows | unflagged rows |", "|---|---|---|---|---|---|---|"]
    for size, v in res["legs"].items():
        for key, s in v["share"].items():
            m, b = key.split("/")
            out.append(f"| {size}×{size} | {m} | {b} | {s['all_rows']:.4f} | {s['free_choice']:.4f} | {f(s['flagged'])} | {s['unflagged']:.4f} |")
    out += ["", "| size | rows | free-choice rows | flagged rows | ties | needs − no-head paired Δ | Δ bottom tercile of needs share | Δ mid | Δ top | Spearman needs share ~ Δ |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for size, v in res["legs"].items():
        n = v["needs_share_vs_delta_nohead"]; t = n["terciles"]
        out.append(f"| {size}×{size} | {v['rows']:,} | {v['free_rows']:,} | {v['flagged_rows']:,} | {v['ties']} | {n['paired_delta_mean']:+.3f} | "
                   f"{t['bottom']:+.3f} | {t['mid']:+.3f} | {t['top']:+.3f} | {n['spearman']:+.3f} |")
    out += ["", "**N3, per size read** (a: the needs cells drive at least 0.010 of acts; b: more on flagged rows than unflagged, None = "
            "under the flagged-row minimum): " + "; ".join(f"{z}×{z} a {v['N3']['a_share_at_least_0.010']}, b {v['N3']['b_flagged_above_unflagged']}" for z, v in res["legs"].items())
            + ". Not read: " + (", ".join(f"{z}×{z}" for z in res["missing"]) or "none") + "."]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("leg"); a.add_argument("size", type=int); a.add_argument("--seeds", default=None); a.add_argument("--out", type=Path, required=True)
    b = sub.add_parser("score"); b.add_argument("--dir", type=Path, required=True); b.add_argument("--out", type=Path, required=True)
    b.add_argument("--md", action="store_true")
    args = ap.parse_args()
    if args.cmd == "leg":
        res = leg(args.size, [int(s) for s in args.seeds.split(",")] if args.seeds else None)
    else:
        res = score(args.dir)
        if args.md:
            args.out.with_suffix(".md").write_text(md(res))
        print(json.dumps({z: v["N3"] for z, v in res["legs"].items()}))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(res, indent=1) + "\n")
