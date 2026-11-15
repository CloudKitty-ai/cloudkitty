#!/usr/bin/env python3
"""The scripted-rescue probe's reads (DECLARATION.md §6 R-1, R-2, R-3; §7's predictions scored; §8's grammar applied
to T − P at 100×100). Reads the legs' rows and replays their recorded acts (nothing covered decides in a read).

  R-1  team happiness per world (the mean of the five seats' mean happiness), paired by world: T − P (primary),
       T − baseline, P − baseline, O − baseline; worlds positive, the paired mean, a bootstrap interval over worlds;
       only worlds run whole (20,000 ticks, no abort) in both members of a pair
  R-2  lost cat-ticks per leg (cuddle >= 90, unpartnered, no friend in sight: no kitty row present in the cat's own
       observation; beside it §3's line, no kitty within the vision radius by Manhattan walk), streaks of 300+, aborts
  R-3  the missions: count, length, share ending in a partner act, how they closed, the rule's share of all acts, and
       the rescuer's own happiness and highest hidden need over its mission ticks against the same seat over the same
       ticks of the baseline world

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_rescue.py --out reads/rescue.json [--md]      (about 5 minutes)
    (A = ../minifriend-phase2-2026-11-06.) A leg that has not run is left out and named.
"""
import argparse
import json
import sys
import tomllib
from concurrent.futures import ProcessPoolExecutor
from math import comb
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rescue as RS  # noqa: E402
C, RP, L = RS.C, RS.RP, RS.L

SEATING = {"T": "rescue-T", "P": "rescue-P", "O": "rescue-O", "base": "p2u-nohead-s1"}
LEGS = (("T", 100), ("P", 100), ("T", 40), ("P", 40), ("O", 100))
PAIRS = (("T", "P"), ("T", "base"), ("P", "base"), ("O", "base"))
SEEDS = tuple(range(905_001, 905_031))
TICKS = 20_000
PAYS_LEVEL = sum(comb(30, x) for x in range(21, 31)) / 2 ** 30      # the sign-test level of 21 of 30 (§8): 0.0214


def radius(size):
    return tomllib.loads(Path(C.LEG_TOML[size]).read_text())["vision"]["radius"]


def leg_dir(kind, size):
    return (C.RAW if kind == "base" else HERE / "results-raw") / "legs" / SEATING[kind] / "legs" / f"size{size}"


def load(kind, size, path=None):
    """{seed: row} of one leg. Refused: a file of another seating or overlay, another size's config, a seed outside
    the battery or repeated."""
    seating = SEATING[kind]
    lines = [json.loads(l) for l in open(path or leg_dir(kind, size) / f"{seating}-g2cmp-30x{TICKS}.jsonl")]
    head, rows = lines[0], lines[1:]
    assert head["provenance"]["config_sha256"] == C.sha256(C.LEG_TOML[size]), f"the leg file is not a {size}x{size} leg"
    for r in rows:
        assert r["seating"] == seating and r.get("overlay", {}).get("kind") == (None if kind == "base" else kind), \
            f"the leg file is not {seating}'s (a row of {r['seating']}, overlay {r.get('overlay', {}).get('kind')})"
    out = {r["seed"]: r for r in rows}
    assert len(out) == len(rows) and set(out) <= set(SEEDS), sorted(out)
    return out


def team(r):
    return sum(r["mean_happiness"]) / len(r["mean_happiness"])


def whole(r):
    return "aborted_streak" not in r and r["ticks"] == TICKS


def paired(a, b, boot=10_000):
    """The paired read of two legs' rows ({seed: row}) over the worlds run whole in both."""
    seeds = sorted(s for s in a if s in b and whole(a[s]) and whole(b[s]))
    d = np.array([team(a[s]) - team(b[s]) for s in seeds])
    pos, neg = int((d > 0).sum()), int((d < 0).sum())
    n = pos + neg
    tail = lambda k: sum(comb(n, x) for x in range(k, n + 1)) / 2 ** n if n else 1.0      # noqa: E731
    rng = np.random.default_rng(39)
    means = d[rng.integers(0, len(d), (boot, len(d)))].mean(1) if len(d) else np.array([np.nan])
    return {"worlds": len(seeds), "seeds": seeds, "positive": pos, "negative": neg, "mean": float(d.mean()) if len(d) else None,
            "ci95": [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))], "p_positive": tail(pos), "p_negative": tail(neg),
            "left_out": sorted(s for s in set(a) | set(b) if s not in seeds)}


def lost_counts(recs, size, radius):
    """Per-seat counts over replayed ticks (each with its start-of-tick obs): lost by sight, lost by §3's Manhattan
    line, and the per-tick happiness and highest hidden need (T, R)."""
    sight = manh = None
    hap, need = [], []
    for rec in recs:
        needs, h, pos, _a, partnered, _p, _d = rec["pre"]
        lonely = (needs[:, RS.CUD] >= RS.LOST_CUDDLE) & ~partnered
        seen = np.stack([rec["obs"][:, o + L.ROW_PRESENT] > 0.5 for o in RS.ROW0], 1).any(1)
        tile = np.rint(pos * size).astype(int)
        dist = np.abs(tile[:, None] - tile[None]).sum(-1) + np.eye(len(tile), dtype=int) * 10 ** 6
        s, m = lonely & ~seen, lonely & (dist.min(1) > radius)
        sight, manh = (s.astype(int), m.astype(int)) if sight is None else (sight + s, manh + m)
        hap.append(h)
        need.append(needs[:, :RS.HIDDEN].max(1))
    return sight, manh, np.asarray(hap, np.float32), np.asarray(need, np.float32)


def world(job):
    kind, size, seed = job
    acts = leg_dir(kind, size) / "acts" / f"acts-{seed}.npz"
    sight, manh, hap, need = lost_counts(RP.replay(acts, C.LEG_TOML[size], want_obs=True), size, radius(size))
    z = np.load(acts)
    out = {"kind": kind, "size": size, "seed": seed, "ticks": int(z["ticks"]), "lost_sight": int(sight.sum()), "lost_manhattan": int(manh.sum()),
           "hap": hap, "need": need}
    if kind != "base":
        out |= {"rule_set": z["rule_set"], "changed": z["rule_set"] & (z["acts"][:, :, 0] != z["policy_acts"]), "act": z["acts"][:, :, 0]}
    return out


def missions(rows, worlds, base_worlds):
    """R-3 over one overlay leg: `rows` {seed: row}, `worlds` / `base_worlds` {seed: world()} of the leg and the baseline."""
    n = ticks = partner_end = 0
    lengths, why, d_hap, d_need, w = [], {}, [], [], []
    rule = changed = cat_ticks = 0
    for seed, r in rows.items():
        o, b = worlds[seed], base_worlds.get(seed)
        rule, changed, cat_ticks = rule + int(o["rule_set"].sum()), changed + int(o["changed"].sum()), cat_ticks + o["rule_set"].size
        for m in r["overlay"]["missions"]:
            k, t0, t1 = m["rescuer"], m["open"], m["close"] if m["close"] is not None else o["ticks"]
            n, why[m["why"]] = n + 1, why.get(m["why"], 0) + 1
            lengths.append(t1 - t0)
            set_ = np.nonzero(o["rule_set"][t0:t1, k])[0]
            partner_end += bool(len(set_)) and int(o["act"][t0 + set_[-1], k]) in RS.PARTNER_ACTS
            if b is not None and t1 > t0 and b["ticks"] >= t1:
                d_hap.append(float(o["hap"][t0:t1, k].mean() - b["hap"][t0:t1, k].mean()))
                d_need.append(float(o["need"][t0:t1, k].mean() - b["need"][t0:t1, k].mean()))
                w.append(t1 - t0)
    avg = lambda x: float(np.average(x, weights=w)) if w else None      # noqa: E731
    return {"missions": n, "per_world": n / max(1, len(rows)), "length_median": float(np.median(lengths)) if lengths else None,
            "length_mean": float(np.mean(lengths)) if lengths else None, "ended_in_partner_act": partner_end / n if n else None, "closed": why,
            "rule_set_share": rule / max(1, cat_ticks), "changed_share": changed / max(1, cat_ticks),
            "rescuer_happiness_vs_baseline": avg(d_hap), "rescuer_need_vs_baseline": avg(d_need), "missions_compared": len(w)}


def grammar(tp, s1_met):
    """§8 on T − P at 100×100: the welfare half is the sign test at the level of 21 of 30."""
    up, down = tp["p_positive"] <= PAYS_LEVEL + 1e-12, tp["p_negative"] <= PAYS_LEVEL + 1e-12
    if down:
        return "COSTS"
    if up and s1_met:
        return "PAYS"
    if s1_met:
        return "TAIL ONLY"
    return "OUTSIDE THE GRAMMAR (welfare up at the level, S1 not met)" if up else "LEVEL"


def read(workers=6):
    legs = [(k, s) for k, s in LEGS + (("base", 100), ("base", 40)) if (leg_dir(k, s) / f"{SEATING[k]}-g2cmp-30x{TICKS}.jsonl").exists()]
    rows = {(k, s): load(k, s) for k, s in legs}
    jobs = [(k, s, seed) for (k, s), r in rows.items() for seed in sorted(r)]
    with ProcessPoolExecutor(workers) as ex:
        worlds = {}
        for w in ex.map(world, jobs):
            worlds.setdefault((w["kind"], w["size"]), {})[w["seed"]] = w
    out = {"legs_read": [f"{k}@{s}" for k, s in legs], "legs_missing": [f"{k}@{s}" for k, s in LEGS if (k, s) not in rows],
           "pays_level": PAYS_LEVEL, "welfare": {}, "tail": {}, "missions": {}}
    for (k, s), r in rows.items():
        ws = worlds[(k, s)]
        out["tail"][f"{k}@{s}"] = {
            "worlds": len(r), "team_mean_whole_worlds": float(np.mean([team(x) for x in r.values() if whole(x)])),
            "lost_sight": sum(w["lost_sight"] for w in ws.values()), "lost_manhattan": sum(w["lost_manhattan"] for w in ws.values()),
            "lost_sight_by_world": {str(seed): ws[seed]["lost_sight"] for seed in sorted(ws)},
            "worlds_300": sum(x["max_distress_age"] >= 300 for x in r.values()), "worst_streak": max(x["max_distress_age"] for x in r.values()),
            "aborts": {str(x["seed"]): x["aborted_streak"]["at_tick"] for x in r.values() if "aborted_streak" in x}}
        if k != "base" and ("base", s) in rows:
            out["missions"][f"{k}@{s}"] = missions(r, ws, worlds[("base", s)])
    for size in (100, 40):
        for a, b in PAIRS:
            if (a, size) in rows and (b, size) in rows:
                p = paired(rows[(a, size)], rows[(b, size)])
                both = [seed for seed in p["seeds"]]
                p["lost_sight"] = {x: sum(worlds[(x, size)][seed]["lost_sight"] for seed in both) for x in (a, b)}
                p["lost_manhattan"] = {x: sum(worlds[(x, size)][seed]["lost_manhattan"] for seed in both) for x in (a, b)}
                out["welfare"][f"{a}-{b}@{size}"] = p
    out["predictions"], w = {}, out["welfare"]
    if "T-P@100" in w:
        tp = w["T-P@100"]
        cut = {x: 1 - tp[x]["T"] / tp[x]["P"] if tp[x]["P"] else None for x in ("lost_sight", "lost_manhattan")}
        s1 = cut["lost_sight"] is not None and cut["lost_sight"] >= 0.30
        out["predictions"]["S1"] = {"cut_by_sight": cut["lost_sight"], "cut_by_manhattan": cut["lost_manhattan"], "met": bool(s1)}
        out["predictions"]["S2"] = {"positive": tp["positive"], "worlds": tp["worlds"], "mean": tp["mean"], "met": bool(tp["positive"] >= 20 and tp["mean"] < 0.5)}
        out["grammar"] = grammar(tp, s1)
    if "T-P@40" in w:
        tp = w["T-P@40"]
        out["predictions"]["S3"] = {"positive": tp["positive"], "worlds": tp["worlds"], "mean": tp["mean"], "met": bool(abs(tp["mean"]) <= 0.15 and 10 <= tp["positive"] <= 20)}
    if "P-base@100" in w and "P-base@40" in w:
        out["predictions"]["S4"] = {"mean_100": w["P-base@100"]["mean"], "mean_40": w["P-base@40"]["mean"], "met": bool(w["P-base@100"]["mean"] <= 0 and w["P-base@40"]["mean"] <= 0)}
    if "O-base@100" in w and "T-base@100" in w:
        o, t = w["O-base@100"]["mean"], w["T-base@100"]["mean"]
        out["predictions"]["S5"] = {"O_minus_base": o, "T_minus_base": t, "met": bool(o * t > 0 and abs(o) >= abs(t) / 2)}
    return out


def md(out):
    Lm = ["# Scripted-rescue probe: the reads", "", f"Legs read: {', '.join(out['legs_read'])}. Missing: {', '.join(out['legs_missing']) or 'none'}.", "",
          "## R-1 welfare (team happiness, paired by world; worlds run whole in both)", "",
          "| pair | worlds | positive | negative | paired mean | 95% interval | sign test (up / down) | left out |", "|---|---|---|---|---|---|---|---|"]
    for name, p in out["welfare"].items():
        Lm.append(f"| {name} | {p['worlds']} | {p['positive']} | {p['negative']} | {p['mean']:+.3f} | [{p['ci95'][0]:+.3f}, {p['ci95'][1]:+.3f}] | "
                  f"{p['p_positive']:.4f} / {p['p_negative']:.4f} | {', '.join(map(str, p['left_out'])) or 'none'} |")
    Lm += ["", f"The PAYS / COSTS level is the sign test of 21 of 30: {out['pays_level']:.4f}.", "", "## R-2 the tail", "",
           "| leg | worlds | team happiness (whole worlds) | lost cat-ticks (sight) | lost cat-ticks (Manhattan) | worlds with a 300+ streak | worst streak | aborts (world: tick) |",
           "|---|---|---|---|---|---|---|---|"]
    for name, t in out["tail"].items():
        Lm.append(f"| {name} | {t['worlds']} | {t['team_mean_whole_worlds']:.3f} | {t['lost_sight']} | {t['lost_manhattan']} | {t['worlds_300']} | {t['worst_streak']} | "
                  f"{', '.join(f'{k}: {v}' for k, v in t['aborts'].items()) or 'none'} |")
    Lm += ["", "Lost cat-ticks over the worlds whole in both members of a pair:", "", "| pair | by sight | by Manhattan |", "|---|---|---|"]
    for name, p in out["welfare"].items():
        Lm.append(f"| {name} | {' / '.join(f'{k} {v}' for k, v in p['lost_sight'].items())} | {' / '.join(f'{k} {v}' for k, v in p['lost_manhattan'].items())} |")
    Lm += ["", "## R-3 the missions", "",
           "| leg | missions | per world | length median / mean | ended in a partner act | closed | rule set the act | rule changed the act | rescuer happiness vs baseline | rescuer highest need vs baseline |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    f = lambda x, s="{:+.3f}": "n/a" if x is None else s.format(x)      # noqa: E731
    for name, m in out["missions"].items():
        Lm.append(f"| {name} | {m['missions']} | {m['per_world']:.1f} | {f(m['length_median'], '{:.0f}')} / {f(m['length_mean'], '{:.1f}')} | {f(m['ended_in_partner_act'], '{:.3f}')} | "
                  f"{', '.join(f'{k} {v}' for k, v in sorted(m['closed'].items()))} | {m['rule_set_share']:.4f} | {m['changed_share']:.4f} | "
                  f"{f(m['rescuer_happiness_vs_baseline'])} | {f(m['rescuer_need_vs_baseline'])} |")
    Lm += ["", "## Predictions and grammar", ""]
    for k, v in out["predictions"].items():
        Lm.append(f"- {k}: {'MET' if v['met'] else 'NOT MET'} ({', '.join(f'{a} {b:+.3f}' if isinstance(b, float) else f'{a} {b}' for a, b in v.items() if a != 'met')})")
    if "grammar" in out:
        Lm.append(f"- §8 on T − P at 100×100: **{out['grammar']}**")
    return "\n".join(Lm) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    out = read(a.workers)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    if a.md:
        a.out.with_suffix(".md").write_text(md(out))
    print(md(out))
