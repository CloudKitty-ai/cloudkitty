#!/usr/bin/env python3
"""R-4 — the heads on the arms' own rollouts, on the LEGS (DECLARATION.md §6 R-4, §8.2; the probe-time half lives in
train_ppo_p2.run_probe_p2 and metrics.jsonl). A recorded leg of an act arm is replayed by its recorded actions with
the arm's heads inline (g2); per (observer, friend row, tick) the head's y0 distribution, the friend's applied act
(tick_records) and her true stratum give:
  (b) F-074's monitor: y0 top-1 ≥ 0.60 on the arm's rollouts (all / seen / heard / silent);
  (c) F-075's monitor: top-prob ECE < 0.05 in sight and heard (calib_act's bins);
  (a, d) the ostrich / optimism read behind the demotion trigger: for every (observer, friend) row whose predicted
         class differs from the friend's applied act, in GRAVE (all) and a fixed-rng sample of COMMON rows (≤ 300 per
         world), the world is forked at the tick (068), the friend's act replaced by the predicted class's legal entry
         her own (arm) policy ranks highest, stepped once, d_hap = branch − real; per version × stratum × friend;
         trigger_eval's rule (lift 1.5, min-n 200) on the leg's pooled rows — on the legs this is a READ reported
         beside the trainer's probe-time trigger, never a halt (the arms are already trained).
Trunk seats in a roster-shaped leg carry no head and are not read.

    read_r4.py --seating p2u-act15-s1 --size 20 [--seeds ...] --out reads/r4/p2u-act15-s1-20.json
    read_r4.py score --out reads/r4.json [--md]
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
import heads_online as HO  # noqa: E402
import train_ppo_p2 as P  # noqa: E402  (class_menu, branch_action, applied_class, monitor_reads, trigger_eval, new_trigger_acc)
import data_act as D  # noqa: E402
sys.path.insert(0, str(C.EXPTS / "minifriend-phase1-2026-10-22"))
import strata as S  # noqa: E402
import cloudkitty  # noqa: E402

READS = HERE / "reads"
COMMON_CAP_PER_WORLD = 300


def seat_models(seats):
    """Per seat: (actor or None, trunk policy) — p2 seats get their P2Actor (heads sized 1) and the trunk seed they
    were grafted from is irrelevant here; g2 seats get the trunk policy (for the branch's own-policy ranking)."""
    import graft as G
    actors, policies = {}, {}
    for i, spec in enumerate(seats):
        kind, name = spec.split(":", 1)
        if kind == "p2":
            actor, _ck = HO.actor_from_artifact(C.ARTS / name / "policy-final.pt", n_obs=1)
            actors[i] = actor
        elif kind == "g2":
            k = int(name.split("-s")[1])
            policies[i], _ = G.load_trunk(k)
        else:
            raise ValueError(spec)
    return actors, policies


def read_world(seating, size, seed, root=None, rng=None):
    rows, header = RP.leg_rows(seating, size, root)
    row = rows[seed]
    actors, policies = seat_models(header["seats"])
    head_seats = [i for i, a in actors.items() if a.heads is None or a.heads.head is not None]
    head_seats = [i for i in head_seats if HO.ARMS[actors[i].arm]["head"] is not None]
    if not head_seats:
        return None
    for a in actors.values():
        a.reset()
    menu = list(cloudkitty.ACTION_MENU)
    cm, idle_ix = P.class_menu(menu), menu.index("idle")
    rng = rng or np.random.default_rng(20261106 + seed)
    T = row["ticks"]
    common_ticks = set(rng.choice(T, min(T, COMMON_CAP_PER_WORLD), replace=False).tolist())
    mon = {k: [] for k in ("cells", "applied", "live", "visible", "friend")}
    acc = P.new_trigger_acc()
    branches = 0
    for rec in RP.replay(RP.acts_path(seating, size, seed, root), C.LEG_TOML[size], want_obs=True, want_snapshot=True, check_row=row):
        t, env, obs, mask, names = rec["tick"], rec["env"], rec["obs"], rec["mask"], rec["names"]
        codes = S.stratum(rec["pre"][0], rec["pre"][1])
        applied = np.array([(-1 if (c := P.applied_class(rec["recs"][a]["applied_action_name"])) is None else c) for a in names])
        hap_real = rec["post"][1]
        logits, cells = {}, {}
        with torch.no_grad():
            for i in range(C.ROSTER):
                o = obs[i:i + 1]
                if i in actors:
                    x, kc = actors[i].widen(o)
                    cells[i] = kc[0]
                    logits[i] = actors[i].policy(torch.from_numpy(x))[0].numpy()
                else:
                    logits[i] = policies[i](torch.from_numpy(o))[0].numpy()
        grave_c, common_c = [], []
        for i in head_seats:
            kc = cells[i]
            friends = [j for j in range(C.ROSTER) if j != i]
            blk = obs[i, C.SELF_BLOCK:C.SELF_BLOCK + C.N_ROWS * C.KITTY_W].reshape(C.N_ROWS, C.KITTY_W)
            st = HO.row_states(blk)
            mon["cells"].append(kc); mon["applied"].append(applied[friends]); mon["live"].append(st != D.SILENT)
            mon["visible"].append(st == D.SEEN); mon["friend"].append(np.array(friends))
            pred = kc[:, :D.N_ACTS].argmax(1)
            for r, j in enumerate(friends):
                if applied[j] < 0 or pred[r] == applied[j]:
                    continue
                (grave_c if codes[j] == S.GRAVE else common_c if codes[j] == S.COMMON else []).append((i, r, j, int(pred[r]), bool(st[r] == D.SEEN)))
        todo = grave_c + ([common_c[int(rng.integers(len(common_c)))]] if (t in common_ticks and common_c) else [])
        cache = {}
        for i, r, j, cls, seen in todo:
            a_b = P.branch_action(D.ACT_NAMES[cls], mask[j], logits[j], cm, idle_ix)
            if a_b is None:
                continue
            if (j, a_b) not in cache:
                br = env.fork()
                br.restore(rec["snapshot_pre"])
                acts_b = {a: (int(rec["acts"][k, 0]), int(rec["acts"][k, 1])) for k, a in enumerate(names)}
                acts_b[names[j]] = (int(a_b), int(rec["acts"][j, 1]))
                br.step(acts_b)
                stb = np.asarray(br.state(), np.float32)
                cache[(j, a_b)] = float(stb[j * RP.PK + RP.HAP] * 100 - hap_real[j])
            d_hap = cache[(j, a_b)]
            branches += 1
            strat = S.NAMES[codes[j]]
            for v in (("visible", "all") if seen else ("all",)):
                acc[v][strat][P.FRIENDS[j]].append(d_hap)
                acc[v][strat]["pooled"].append(d_hap)
    M = {k: np.concatenate(v) for k, v in mon.items()}
    return {"seating": seating, "size": size, "seed": seed, "monitors": P.monitor_reads(M["cells"], M["applied"], M["live"], M["visible"]),
            "branches": branches, "trigger_acc": acc}


def read_leg(seating, size, root=None, seeds=None):
    rows, _h = RP.leg_rows(seating, size, root)
    acc = P.new_trigger_acc()
    worlds = {}
    for seed in (sorted(rows) if seeds is None else seeds):
        w = read_world(seating, size, seed, root)
        if w is None:
            return {"seating": seating, "size": size, "state": "no head seat"}
        worlds[str(seed)] = {"monitors": w["monitors"], "branches": w["branches"]}
        for v in acc:
            for st in acc[v]:
                for f in acc[v][st]:
                    acc[v][st][f] += w["trigger_acc"][v][st][f]
    top1 = [w["monitors"]["all"]["top1"] for w in worlds.values() if w["monitors"]["all"].get("top1") is not None]
    return {"seating": seating, "size": size, "worlds": worlds, "pooled_top1_all": float(np.mean(top1)) if top1 else None,
            "f074_ok_all_worlds": all(w["monitors"]["f074_ok"] for w in worlds.values()),
            "f075_ok_all_worlds": all(w["monitors"]["f075_ok"] for w in worlds.values()),
            "trigger_read": P.trigger_eval(acc), "branches": int(sum(w["branches"] for w in worlds.values()))}


def score():
    return {p.stem: json.loads(p.read_text()) for p in sorted((READS / "r4").glob("*.json"))}


def md(out):
    L = ["# R-4 — the heads on the arms' legs", "", "| leg | y0 top-1 (all, pooled) | F-074 all worlds | F-075 all worlds | trigger read (visible / all) | branches |", "|---|---|---|---|---|---|"]
    for name, r in out.items():
        if "state" in r:
            L.append(f"| {name} | {r['state']} | | | | |")
            continue
        tr = r["trigger_read"]["by_version"]
        L.append(f"| {name} | {r['pooled_top1_all']} | {r['f074_ok_all_worlds']} | {r['f075_ok_all_worlds']} | {tr['visible']['state']} / {tr['all']['state']} (grave {tr['all'].get('grave')}, common {tr['all'].get('common')}, n {tr['all']['n_grave']} / {tr['all']['n_common']}) | {r['branches']} |")
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
        p = a.out or READS / "r4" / f"{a.seating}-{a.size}.json"
    else:
        out = score()
        p = a.out or READS / "r4.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=1) + "\n")
    if a.md and a.cmd == "score":
        p.with_suffix(".md").write_text(md(out))
        print(md(out))
    else:
        print(json.dumps({k: v for k, v in out.items() if k != "worlds"}, indent=1) if a.cmd == "leg" else f"wrote {p}")


if __name__ == "__main__":
    main()
