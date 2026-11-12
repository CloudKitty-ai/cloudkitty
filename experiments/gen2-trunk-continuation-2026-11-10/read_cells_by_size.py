"""R-4, cells-in-use by world size (DECLARATION §6 R-4, §7 P53; her word 2026-11-11 "3) Yes" on her head question:
"If there is no measurable use of the heads, why are we seeing a negative impact on welfare on the headed arms?").
Dump-only over Phase 2's RECORDED uniform legs: one replay per world, the arm's heads stepped online over the
recorded observations, no world served, zero covered cost.
  leg    per world: the share of decision rows whose greedy act changes when the appended cells are zeroed —
         Phase 2's own `train_ppo_p2.cells_in_use` (imported, never copied) over a dump of the leg's rows — on ALL
         rows (P53's registered quantity) and on FREE-CHOICE rows (more than one legal act; entry 30's lesson: a
         one-legal-act row cannot change). Fences: (act) the recorded act must be a maximiser of the replayed masked
         logits (read_r5.fence_act), so the rows and cells are what the arm saw; (no-head) a no-head leg must show
         0 changed rows.
  score  per head-arm leg: the pooled shares; the leg's 30 worlds split into terciles by their changed share; the
         arm's paired team-happiness delta against the SAME-SEED no-head leg (joined by world id) per tercile; P53.
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_cells_by_size.py leg <seating> <size> [--seeds a,b] --out reads/r4/<seating>-<size>.json
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_cells_by_size.py score --dir reads/r4 --out reads/r4/score.json [--md]
(A = experiments/minifriend-phase2-2026-11-06, the arc whose venv, legs and artifacts this reads.)
"""
import argparse
import json
import sys
import tempfile
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
import train_ppo_p2 as P  # noqa: E402

N_ACT = R5.N_ACT
assert N_ACT == P.N_ACTIONS
WORLDS = 30
# head-arm leg -> its same-seed no-head leg (s1's no-head seat is the s1r rerun, as R-1 paired it)
PAIRS = {"p2u-act15-s1": "p2u-nohead-s1", "p2u-act15-s2": "p2u-nohead-s2", "p2u-act15-s4": "p2u-nohead-s4",
         "p2u-both-s1": "p2u-nohead-s1"}
SIZES = {"p2u-act15-s1": (20, 40, 100), "p2u-act15-s2": (20, 40), "p2u-act15-s4": (20, 40), "p2u-both-s1": (20, 40, 100)}
TERCILES = ("bottom", "mid", "top")


def leg(seating, size, seeds=None):
    rows, header = RP.leg_rows(seating, size, None)
    specs = header["seats"]
    assert len(set(specs)) == 1 and specs[0].startswith("p2:"), f"a uniform Phase 2 seating is read, got {specs}"
    actors = [HO.actor_from_artifact(C.ARTS / specs[0].split(":", 1)[1] / "policy-final.pt", n_obs=1)[0] for _ in specs]
    arm, policy = actors[0].arm, actors[0].policy
    out = {"seating": seating, "size": size, "arm": arm, "policy": specs[0], "worlds": []}
    with tempfile.TemporaryDirectory() as td:
        dump = Path(td) / "rows.npz"
        for seed in (sorted(rows) if seeds is None else seeds):
            for a in actors:
                a.reset()
            O, CL, M, AR, TK = ([[] for _ in actors] for _ in range(5))
            for rec in RP.replay(RP.acts_path(seating, size, seed, None), C.LEG_TOML[size], want_obs=True, check_row=rows[seed]):
                for i, actor in enumerate(actors):
                    o = rec["obs"][i:i + 1]
                    _x, cells = actor.widen(o)
                    O[i].append(o[0]); CL[i].append(cells[0]); M[i].append(rec["mask"][i]); AR[i].append(int(rec["acts"][i, 0])); TK[i].append(rec["tick"])
            w = {"seed": seed, "rows": 0, "changed": 0, "free_rows": 0, "free_changed": 0, "ties": 0}
            for i in range(len(actors)):                                  # one seat at a time: 20k rows a forward
                obs, cells, mask = np.stack(O[i]), np.stack(CL[i]), np.stack(M[i])
                with torch.no_grad():
                    la = policy(torch.from_numpy(np.concatenate([obs, cells.reshape(len(obs), -1)], 1)))[:, :N_ACT].numpy()
                ml = np.where(mask[:, :N_ACT], la, -np.inf)
                for j in np.flatnonzero(ml.argmax(1) != np.asarray(AR[i])):   # the act fence (raises unless a tie)
                    w["ties"] += int(R5.fence_act(ml[j], AR[i][j], TK[i][j], i)[1])
                np.savez(dump, obs=obs, cells=cells, mask=mask)
                r = P.cells_in_use(policy, dump, policy.cells)
                w["rows"] += r["rows"]; w["changed"] += int(round(r["changed_share"] * r["rows"]))
                free = mask[:, :N_ACT].sum(1) >= 2
                if free.any():
                    np.savez(dump, obs=obs[free], cells=cells[free], mask=mask[free])
                    r = P.cells_in_use(policy, dump, policy.cells)
                    w["free_rows"] += r["rows"]; w["free_changed"] += int(round(r["changed_share"] * r["rows"]))
            assert arm != "nohead" or w["changed"] == 0, (f"FENCE: the no-head leg {seating} {size} world {seed} shows "
                                                          f"{w['changed']} changed rows with its inert cell zeroed")
            w["changed_share"] = w["changed"] / w["rows"]
            w["free_changed_share"] = w["free_changed"] / max(1, w["free_rows"])
            out["worlds"].append(w)
            print("world", seed, w, flush=True)
    return out


def pooled(ws, a, b):
    return sum(w[a] for w in ws) / max(1, sum(w[b] for w in ws))


def score(d):
    res = {"legs": {}, "fences": {}}
    for seating, sizes in SIZES.items():
        for size in sizes:
            r4 = json.loads((d / f"{seating}-{size}.json").read_text())
            ws = {w["seed"]: w for w in r4["worlds"]}
            arm_rows, _h = RP.leg_rows(seating, size, None)
            nh_rows, _h = RP.leg_rows(PAIRS[seating], size, None)
            assert len(ws) == WORLDS and set(ws) == set(arm_rows) == set(nh_rows), \
                f"{seating} {size}: {len(ws)} worlds read, {len(arm_rows)} arm rows, {len(nh_rows)} no-head rows — a partial leg is never scored"
            seeds = sorted(ws, key=lambda s: (ws[s]["changed_share"], s))
            delta = {s: R1.team(arm_rows[s]) - R1.team(nh_rows[s]) for s in seeds}
            k = WORLDS // 3
            terc = {name: seeds[i * k:(i + 1) * k] for i, name in enumerate(TERCILES)}
            x, y = np.asarray([ws[s]["changed_share"] for s in seeds]), np.asarray([delta[s] for s in seeds])
            rk = lambda v: np.argsort(np.argsort(v))
            res["legs"][f"{seating}-{size}"] = {
                "seating": seating, "size": size, "paired_with": PAIRS[seating], "worlds": len(ws),
                "ties": sum(w["ties"] for w in ws.values()),
                "changed_share": pooled(ws.values(), "changed", "rows"),
                "free_changed_share": pooled(ws.values(), "free_changed", "free_rows"),
                "free_row_share": pooled(ws.values(), "free_rows", "rows"),
                "paired_delta_nohead_mean": float(y.mean()),
                "terciles": {name: {"n": len(ss), "changed_share_range": [ws[ss[0]]["changed_share"], ws[ss[-1]]["changed_share"]],
                                    "paired_delta_nohead_mean": float(np.mean([delta[s] for s in ss]))} for name, ss in terc.items()},
                "spearman_share_vs_delta": float(np.corrcoef(rk(x), rk(y))[0, 1]),
                "aborted_seeds": sorted(s for s in ws if "aborted_streak" in arm_rows[s] or "aborted_streak" in nh_rows[s])}
    for f in sorted(d.glob("fence-*.json")):
        r4 = json.loads(f.read_text())
        assert r4["arm"] == "nohead" and all(w["changed"] == 0 for w in r4["worlds"]), f"FENCE: {f.name} shows changed rows"
        res["fences"][f.stem] = {"worlds": len(r4["worlds"]), "rows": sum(w["rows"] for w in r4["worlds"]), "changed": 0}
    L = res["legs"]
    sh = lambda s, z: L[f"p2u-act15-{s}-{z}"]["changed_share"]
    rises = {"s1 40>20": sh("s1", 40) > sh("s1", 20), "s2 40>20": sh("s2", 40) > sh("s2", 20), "s4 40>20": sh("s4", 40) > sh("s4", 20),
             "s1 100>40": sh("s1", 100) > sh("s1", 40)}
    top_lt_bottom = {s: (L[f"p2u-act15-{s}-40"]["terciles"]["top"]["paired_delta_nohead_mean"]
                         < L[f"p2u-act15-{s}-40"]["terciles"]["bottom"]["paired_delta_nohead_mean"]) for s in ("s1", "s2", "s4")}
    half_a, half_b = all(rises.values()), sum(top_lt_bottom.values()) >= 2
    res["P53"] = {"share_rises_with_size": rises, "half_a_met": bool(half_a),
                  "top_tercile_delta_below_bottom_at_40": top_lt_bottom, "half_b_met": bool(half_b),
                  "verdict": "MET" if half_a and half_b else "NOT MET"}
    return res


def md(res):
    out = ["# R-4 — cells-in-use by world size (Phase 2's recorded uniform legs; 30 worlds a leg)", "",
           "Changed share = decision rows whose greedy act changes when the appended cells are zeroed. Paired Δ = the "
           "arm's team happiness minus the same-seed no-head leg's, per world; terciles = the leg's worlds ranked by "
           "their changed share.", "",
           "| leg | changed share, all rows | changed share, free-choice rows | free-choice share of rows | paired Δ vs no-head | Δ bottom tercile | Δ mid | Δ top tercile | Spearman share~Δ | ties | aborted |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, v in res["legs"].items():
        t = v["terciles"]
        out.append(f"| {name} | {v['changed_share']:.4f} | {v['free_changed_share']:.4f} | {v['free_row_share']:.3f} | {v['paired_delta_nohead_mean']:+.3f} | "
                   f"{t['bottom']['paired_delta_nohead_mean']:+.3f} | {t['mid']['paired_delta_nohead_mean']:+.3f} | {t['top']['paired_delta_nohead_mean']:+.3f} | "
                   f"{v['spearman_share_vs_delta']:+.3f} | {v['ties']} | {v['aborted_seeds'] or '—'} |")
    p = res["P53"]
    out += ["", f"**P53 {p['verdict']}.** Share rises with size: {p['share_rises_with_size']} (half a {'met' if p['half_a_met'] else 'not met'}); "
            f"top-tercile Δ below bottom-tercile Δ at 40×40: {p['top_tercile_delta_below_bottom_at_40']} (half b {'met' if p['half_b_met'] else 'not met'}).", "",
            "No-head fence (0 changed rows): " + (", ".join(f"{k} ({v['worlds']} worlds, {v['rows']} rows)" for k, v in res["fences"].items()) or "none read") + "."]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("leg"); a.add_argument("seating"); a.add_argument("size", type=int)
    a.add_argument("--seeds", default=None); a.add_argument("--out", type=Path, required=True)
    b = sub.add_parser("score"); b.add_argument("--dir", type=Path, required=True); b.add_argument("--out", type=Path, required=True)
    b.add_argument("--md", action="store_true")
    args = ap.parse_args()
    if args.cmd == "leg":
        res = leg(args.seating, args.size, [int(s) for s in args.seeds.split(",")] if args.seeds else None)
    else:
        res = score(args.dir)
        if args.md:
            args.out.with_suffix(".md").write_text(md(res))
        print(json.dumps(res["P53"], indent=1))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(res, indent=1) + "\n")
