"""R-7, the block read on the dual-head arm (deviations entry 33, P55; her word 2026-11-11 "Let's run the block read").
Dump-only over p2u-both-s1's three RECORDED uniform legs: one replay per world, the arm's two heads stepped online
over the recorded observations, no world served, zero covered cost. R-4 zeroed every appended cell at once; this
read takes the cells one BLOCK at a time — act (the B15 head's 13 cells a friend row), needs (the needs head's seven
estimates + P(grave)), tsl (the time-since-live cell every arm carries) — and asks which block the policy's greedy
act leans on.
  leg    per world, per block and "all": the decision rows whose greedy act changes when the block is ZEROED (R-4's
         ablation; P55's registered quantity) and when it is PERMUTED across the seat's own ticks (the four friend
         rows moved together; a fixed generator per world x seat x block) — zero is off-distribution for a
         probability vector, the permutation is not. Counted on all rows and on FLAGGED rows (some friend row's
         P(grave) cell >= 0.5). Fences: the recorded act is a maximiser of the replayed masked logits
         (read_r5.fence_act); "all" zeroed reproduces R-4's recorded rows and changed count for the world.
  score  per leg: pooled shares per block and mode on all / free-choice / flagged / unflagged rows; the worlds
         ranked by their needs-block share against the paired team-happiness delta over the same-seed act15 leg
         (the arm that differs by the needs block alone); P55.
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_blocks.py leg <size> [--seeds a,b] --out reads/r7/p2u-both-s1-<size>.json
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_blocks.py score --dir reads/r7 --out reads/r7/score.json [--md]
(A = experiments/minifriend-phase2-2026-11-06, the arc whose venv, legs and artifacts this reads.)
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
P2 = HERE.parent / "minifriend-phase2-2026-11-06"
sys.path.insert(0, str(P2))
import p2_common as C  # noqa: E402
import replay as RP  # noqa: E402
import heads_online as HO  # noqa: E402
import read_r5 as R5  # noqa: E402
import read_r1 as R1  # noqa: E402

N_ACT = R5.N_ACT
SEATING, PAIR, SIZES, WORLDS = "p2u-both-s1", "p2u-act15-s1", (20, 40, 100), 30
W = HO.ARMS["both"]["cells"]
BLOCKS = {"act": (0, HO.ACT_CELLS), "needs": (HO.NEEDS_OFF, HO.NEEDS_OFF + HO.NEEDS_CELLS), "tsl": (HO.NEEDS_OFF + HO.NEEDS_CELLS, W)}
assert sorted(c for a, b in BLOCKS.values() for c in range(a, b)) == list(range(W)), f"the blocks do not partition the arm's {W} cells: {BLOCKS}"
BLOCKS["all"] = (0, W)
PG = HO.NEEDS_OFF + HO.NEEDS_CELLS - 1                      # the P(grave) cell of a friend row
FLAG, MIN_N = 0.5, 200
MODES = ("zero", "perm")
R4 = HERE / "reads" / "r4"
TERCILES = ("bottom", "mid", "top")


def masked_logits(policy, obs, cells, mask):
    with torch.no_grad():
        la = policy(torch.from_numpy(np.concatenate([obs, cells.reshape(len(obs), -1)], 1)))[:, :N_ACT].numpy()
    return np.where(mask[:, :N_ACT], la, -np.inf)


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
    assert arm == "both" and policy.cells == W, (arm, policy.cells)
    r4 = {w["seed"]: w for w in json.loads((R4 / f"{SEATING}-{size}.json").read_text())["worlds"]}
    out = {"seating": SEATING, "size": size, "arm": arm, "policy": specs[0], "blocks": BLOCKS, "worlds": []}
    for seed in (sorted(rows) if seeds is None else seeds):
        for a in actors:
            a.reset()
        O, CL, M, AR, TK = ([[] for _ in actors] for _ in range(5))
        for rec in RP.replay(RP.acts_path(SEATING, size, seed, None), C.LEG_TOML[size], want_obs=True, check_row=rows[seed]):
            for i, actor in enumerate(actors):
                o = rec["obs"][i:i + 1]
                _x, cells = actor.widen(o)
                O[i].append(o[0]); CL[i].append(cells[0]); M[i].append(rec["mask"][i]); AR[i].append(int(rec["acts"][i, 0])); TK[i].append(rec["tick"])
        w = {"seed": seed, "rows": 0, "free_rows": 0, "flagged_rows": 0, "ties": 0,
             **{m: {b: {"changed": 0, "changed_flagged": 0} for b in BLOCKS} for m in MODES}}
        for i in range(len(actors)):                                      # one seat at a time: 20k rows a forward
            obs, cells, mask = np.stack(O[i]), np.stack(CL[i]), np.stack(M[i])
            ml = masked_logits(policy, obs, cells, mask)
            for j in np.flatnonzero(ml.argmax(1) != np.asarray(AR[i])):   # the act fence (raises unless a tie)
                w["ties"] += int(R5.fence_act(ml[j], AR[i][j], TK[i][j], i)[1])
            base = ml.argmax(1)
            flagged = cells[:, :, PG].max(1) >= FLAG
            w["rows"] += len(obs); w["free_rows"] += int((mask[:, :N_ACT].sum(1) >= 2).sum()); w["flagged_rows"] += int(flagged.sum())
            for bi, b in enumerate(BLOCKS):
                for m in MODES:
                    ch = masked_logits(policy, obs, ablate(cells, b, m, np.random.default_rng([seed, i, bi])), mask).argmax(1) != base
                    w[m][b]["changed"] += int(ch.sum()); w[m][b]["changed_flagged"] += int((ch & flagged).sum())
        assert (w["rows"], w["zero"]["all"]["changed"]) == (r4[seed]["rows"], r4[seed]["changed"]), \
            (f"FENCE: {SEATING} {size} world {seed}: all cells zeroed changes {w['zero']['all']['changed']} of {w['rows']} rows, "
             f"R-4 recorded {r4[seed]['changed']} of {r4[seed]['rows']}")
        out["worlds"].append(w)
        print("world", seed, json.dumps(w), flush=True)
    return out


def score(d):
    res = {"legs": {}}
    for size in SIZES:
        ws = {w["seed"]: w for w in json.loads((d / f"{SEATING}-{size}.json").read_text())["worlds"]}
        arm_rows, _h = RP.leg_rows(SEATING, size, None)
        pair_rows, _h = RP.leg_rows(PAIR, size, None)
        assert len(ws) == WORLDS and set(ws) == set(arm_rows) == set(pair_rows), \
            f"{SEATING} {size}: {len(ws)} worlds read, {len(arm_rows)} arm rows, {len(pair_rows)} act15 rows — a partial leg is never scored"
        tot = lambda k: sum(w[k] for w in ws.values())
        rows, free, flg = tot("rows"), tot("free_rows"), tot("flagged_rows")
        leg_ = {"size": size, "worlds": len(ws), "rows": rows, "free_rows": free, "flagged_rows": flg, "ties": tot("ties"), "share": {}}
        for m in MODES:
            for b in BLOCKS:
                ch = sum(w[m][b]["changed"] for w in ws.values()); cf = sum(w[m][b]["changed_flagged"] for w in ws.values())
                leg_["share"][f"{m}/{b}"] = {"all_rows": ch / rows, "free_choice": ch / free,
                                             "flagged": cf / flg if flg >= MIN_N else None, "unflagged": (ch - cf) / (rows - flg)}
        share = lambda s: ws[s]["zero"]["needs"]["changed"] / ws[s]["rows"]
        seeds = sorted(ws, key=lambda s: (share(s), s))
        delta = {s: R1.team(arm_rows[s]) - R1.team(pair_rows[s]) for s in seeds}
        k = WORLDS // 3
        rk = lambda v: np.argsort(np.argsort(v))
        leg_["needs_share_vs_delta_act15"] = {
            "paired_delta_mean": float(np.mean(list(delta.values()))),
            "terciles": {name: {"needs_share_range": [share(seeds[i * k]), share(seeds[(i + 1) * k - 1])],
                                "paired_delta_mean": float(np.mean([delta[s] for s in seeds[i * k:(i + 1) * k]]))} for i, name in enumerate(TERCILES)},
            "spearman": float(np.corrcoef(rk(np.asarray([share(s) for s in seeds])), rk(np.asarray([delta[s] for s in seeds])))[0, 1])}
        res["legs"][str(size)] = leg_
    z = lambda size, b, col="all_rows": res["legs"][str(size)]["share"][f"zero/{b}"][col]
    a = {str(s): z(s, "needs") >= 0.010 for s in SIZES}
    b = {str(s): (None if z(s, "needs", "flagged") is None else z(s, "needs", "flagged") > z(s, "needs", "unflagged")) for s in SIZES}
    c = {str(s): z(s, "act") > z(s, "needs") for s in SIZES}
    decided = [v for v in b.values() if v is not None]
    half_b = "UNDECIDABLE" if not decided else ("MET" if all(decided) else "NOT MET")
    res["P55"] = {"a_needs_share_at_least_0.010": a, "half_a": "MET" if all(a.values()) else "NOT MET",
                  "b_needs_share_flagged_above_unflagged": b, "half_b": half_b,
                  "c_act_share_above_needs_share": c, "half_c": "MET" if all(c.values()) else "NOT MET"}
    return res


def md(res):
    f = lambda v: "INSUFFICIENT" if v is None else f"{v:.4f}"
    out = ["# R-7 — the block read on the dual-head arm (p2u-both-s1's recorded uniform legs; 30 worlds a leg)", "",
           "Share = decision rows whose greedy act changes when the block's cells are zeroed (zero) or permuted across the "
           "seat's own ticks (perm). Blocks: act = the B15 head's 13 cells a friend row; needs = the needs head's seven "
           f"estimates + P(grave); tsl = the time-since-live cell; all = every appended cell (R-4's read). Flagged = rows where "
           f"some friend row's P(grave) cell is at least {FLAG}; under {MIN_N} flagged rows a leg reads INSUFFICIENT.", "",
           "| size | mode | block | all rows | free-choice rows | flagged rows | unflagged rows |", "|---|---|---|---|---|---|---|"]
    for size, v in res["legs"].items():
        for key, s in v["share"].items():
            m, b = key.split("/")
            out.append(f"| {size}×{size} | {m} | {b} | {s['all_rows']:.4f} | {s['free_choice']:.4f} | {f(s['flagged'])} | {s['unflagged']:.4f} |")
    out += ["", "| size | rows | free-choice rows | flagged rows | ties | both − act15 paired Δ | Δ bottom tercile of needs share | Δ mid | Δ top | Spearman needs share ~ Δ |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for size, v in res["legs"].items():
        n = v["needs_share_vs_delta_act15"]; t = n["terciles"]
        out.append(f"| {size}×{size} | {v['rows']:,} | {v['free_rows']:,} | {v['flagged_rows']:,} | {v['ties']} | {n['paired_delta_mean']:+.3f} | "
                   f"{t['bottom']['paired_delta_mean']:+.3f} | {t['mid']['paired_delta_mean']:+.3f} | {t['top']['paired_delta_mean']:+.3f} | {n['spearman']:+.3f} |")
    p = res["P55"]
    out += ["", f"**P55.** (a) needs-block share at least 0.010 at every size: {p['a_needs_share_at_least_0.010']} — {p['half_a']}. "
            f"(b) needs-block share higher on flagged rows than unflagged: {p['b_needs_share_flagged_above_unflagged']} — {p['half_b']}. "
            f"(c) act-block share above needs-block share: {p['c_act_share_above_needs_share']} — {p['half_c']}."]
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
        print(json.dumps(res["P55"], indent=1))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(res, indent=1) + "\n")
