"""Entry-29 (D) analysis of the two halted act10 seeds (owner 2026-11-08 "let's start with D. We can decide between A and
C based on that, leaning C"), with entries 25 / 26's instruments (diag_nohead_s1: own SELF_DISTRESS flags localise a
streak; diag_act10_s1_seed: seat series, per-seat shares, the fence against metrics.jsonl). Dump-only: every read is off
the runs' own probe dumps (3 worlds × 2,000 ticks × 5 seats each); zero regeneration, zero collection, no world served.

Per failed seed (s2: probe-distress-stop u1149, world 40,002; s4: f053-line-crossed u3349, world 40,001):
  (1) HISTORY — every probe of the halted run: per-world maxima asserted equal to metrics.jsonl's probe row at EVERY
      probe (the fence), streaks >= LAND_MIN listed by (update, world, kitty);
  (2) THE SEAT(S) — the trip world's flagged seat(s) at every probe of the halted run (s2: Pumpkin on 40,002; s4: all
      five on 40,001): streak, flags by need, happiness min, chow in memory / sight, eat-legal ticks, eaten, moves;
  (3) PAIRED — the same world and seat(s) on the sibling arms of the SAME trunk seed at the same update (act15-s<k>,
      nohead-s<k>; the deterministic probe worlds are shared) and on the parent trunk's probe at the same update where
      it exists (trunk-s2 has u1149) or its last (trunk-s4 ends at u2599); landings >= LAND_MIN per run as (1);
  (4) PER-SEAT shares at the trip probe of the halted run and the same update of its siblings;
  (5) DIVERGENCE — on the trip world, the first tick at which the clean probe before the trip and the trip probe
      propose differently, per seat;
  (6) ONSET (s4) — per seat on 40,001 at u3349: first own-flag tick, the flag's needs, applied eat / drink ticks in
      the probe, partnered share, kitty rows in sight — the F-060 pile read (onset spread, who ate, who moved).

  VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B diag_act10_s2s4.py [--out reads/diag-act10-s2s4.json] [--md]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diag_nohead_s1 as G  # noqa: E402
import diag_act10_s1_seed as S1  # noqa: E402

LAND_MIN = 10
CASES = {
    "s2": {"failed": "p2-act10-s2", "trip": 1149, "clean_before": 1099, "world": 40002, "seats": [3],
           "siblings": {"p2-act15-s2": None, "p2-nohead-s2": None}, "trunk": ("trunk-s2", "ppo-g2-trunk-s2")},
    "s4": {"failed": "p2-act10-s4", "trip": 3349, "clean_before": 3299, "world": 40001, "seats": [1, 2, 3, 4, 5],
           "siblings": {"p2-act15-s4": None, "p2-nohead-s4": None}, "trunk": ("trunk-s4", "ppo-g2-trunk-s4")},
}


def landings(d, u, names):
    loc = G.localise(d)
    per_seed = [max(v[0] for v in loc[s].values()) for s in sorted(loc)]
    landed = [{"update": u, "world": s, "kitty": k, "name": names[k - 1], "streak": st, "span": list(span)}
              for s in sorted(loc) for k, (st, span) in loc[s].items() if st >= LAND_MIN]
    return per_seed, landed


def history(run, names, world, seats, keep_updates=()):
    """(1) + (2) for one run: fenced landings at every probe and the trip seats' series on the trip world."""
    rows = S1.recorded_rows(run)
    ps = S1.probes(run)
    out = {"n_probes": len(ps), "n_fenced": 0, "final_update": ps[-1][0], "landed": [], "seat_series": {}}
    keep = {}
    for u, p in ps:
        d = G.load(p)
        per_seed, landed = landings(d, u, names)
        if u in rows:
            rec = rows[u]["max_distress_streak_per_seed"]
            assert per_seed == rec, f"{run.name} u{u}: streak did not reproduce: {per_seed} vs recorded {rec}"
            out["n_fenced"] += 1
        out["landed"] += landed
        out["seat_series"][u] = {names[k - 1]: S1.seat_read(d, world, k, names) for k in seats}
        if u in keep_updates:
            keep[u] = d
    by_name = {}
    for e in out["landed"]:
        by_name.setdefault(e["name"], []).append(e["streak"])
    out["landed_by_name"] = {n: sorted(v, reverse=True) for n, v in by_name.items()}
    out["max_streak"] = max((e["streak"] for e in out["landed"]), default=0)
    return out, keep


def onset(d, world, names):
    """(6) per seat on one world: first own-flag tick, flagged needs, applied eat / drink, company."""
    res = {}
    eat, drink = G.D.ACT_NAMES.index("eat"), G.D.ACT_NAMES.index("drink")
    for k in sorted(np.unique(d["kitty"]).tolist()):
        sel = (d["seed"] == world) & (d["kitty"] == k)
        t, o = d["tick"][sel], d["obs"][sel]
        fl = G.own_flags(o)
        anyf = fl.any(1)
        first = int(t[np.argmax(anyf)]) if anyf.any() else None
        r = {"first_flag_tick": first, "flag_ticks": int(anyf.sum()),
             "flags_by_kind": {n: int(fl[:, i].sum()) for i, n in enumerate(G.L.NEED_KINDS) if fl[:, i].any()},
             "needs_at_end": {n: round(float(o[-1, G.L.SELF_NEEDS + i] * 100), 1) for i, n in enumerate(G.L.NEED_KINDS)},
             "partnered_share": round(float(o[:, G.L.SELF_PARTNERED].mean()), 3),
             "moves_proposed": int((d["act"][sel] < 4).sum()),
             "chow_visible_share": G.window_read(d, world, k, (int(t.min()), int(t.max())))["chow_visible_share"]}
        if "applied" in d:
            r["applied_eat_ticks"] = int((d["applied"][sel] == eat).sum())
            r["applied_drink_ticks"] = int((d["applied"][sel] == drink).sum())
        if "hap" in d:
            r["hap_min"] = round(float(d["hap"][sel].min()), 1)
            r["hap_at_end"] = round(float(d["hap"][sel][-1]), 1)
        res[names[k - 1]] = r
    firsts = [r["first_flag_tick"] for r in res.values() if r["first_flag_tick"] is not None]
    return {"per_seat": res, "n_flagged": len(firsts), "onset_spread_ticks": (max(firsts) - min(firsts)) if firsts else None}


def divergence(a0, a1, world, names):
    div = {}
    for k in sorted(np.unique(a1["kitty"]).tolist()):
        s0 = (a0["seed"] == world) & (a0["kitty"] == k)
        s1 = (a1["seed"] == world) & (a1["kitty"] == k)
        assert (a0["tick"][s0] == a1["tick"][s1]).all()
        diff = np.nonzero(a0["act"][s0] != a1["act"][s1])[0]
        div[names[k - 1]] = {"first_tick_proposals_differ": int(a0["tick"][s0][diff[0]]) if len(diff) else None,
                             "ticks_differ": int(len(diff)), "ticks": int(s1.sum())}
    return div


def analyse(case, names):
    c = CASES[case]
    failed = G.C.ARTS / c["failed"]
    out = {"failed": c["failed"], "trip": c["trip"], "clean_before": c["clean_before"], "world": c["world"],
           "seats": {k: names[k - 1] for k in c["seats"]}, "runs": {}, "paired": {}, "per_seat_at_trip": {}}
    h, keep = history(failed, names, c["world"], c["seats"], keep_updates=(c["clean_before"], c["trip"]))
    out["runs"][c["failed"]] = {k: v for k, v in h.items() if k != "seat_series"}
    out["seat_series"] = {c["failed"]: h["seat_series"]}
    trip_d = keep[c["trip"]]
    out["per_seat_at_trip"][c["failed"]] = S1.per_seat_shares(trip_d, names)
    out["divergence"] = {"world": c["world"], "probes": [c["clean_before"], c["trip"]],
                         "per_seat": divergence(keep[c["clean_before"]], trip_d, c["world"], names)}
    out["onset_at_trip"] = {c["failed"]: onset(trip_d, c["world"], names)}
    # (3) siblings: full fenced history (their own landings) + the trip world's seats at the trip update
    for sib in c["siblings"]:
        run = G.C.ARTS / sib
        hs, ks = history(run, names, c["world"], c["seats"], keep_updates=(c["trip"],))
        out["runs"][sib] = {k: v for k, v in hs.items() if k != "seat_series"}
        out["seat_series"][sib] = hs["seat_series"]
        if c["trip"] in ks:
            out["per_seat_at_trip"][sib] = S1.per_seat_shares(ks[c["trip"]], names)
            out["onset_at_trip"][sib] = onset(ks[c["trip"]], c["world"], names)
    tag, tdir = c["trunk"]
    trun = G.C.TRUNK_ARTS / tdir
    ht, kt = history(trun, names, c["world"], c["seats"], keep_updates=(c["trip"],))
    out["runs"][tag] = {k: v for k, v in ht.items() if k != "seat_series"}
    out["seat_series"][tag] = ht["seat_series"]
    tu = c["trip"] if c["trip"] in kt else ht["final_update"]
    td = kt.get(c["trip"]) or G.load(dict(S1.probes(trun))[tu])
    out["per_seat_at_trip"][tag] = S1.per_seat_shares(td, names)
    out["onset_at_trip"][tag] = onset(td, c["world"], names)
    out["trunk_probe_used"] = {tag: tu}
    return out


def md(res):
    lines = ["# Entry 29 (D): the two halted act10 seeds, dump-only", ""]
    for case, r in res["cases"].items():
        c = CASES[case]
        lines += [f"## {case}: {r['failed']} tripped at u{r['trip']} on world {r['world']}", "",
                  "| run | probes (fenced) | final u | max streak | streaks >= %d by seat |" % LAND_MIN, "|---|---|---|---|---|"]
        for tag, h in r["runs"].items():
            lines.append(f"| {tag} | {h['n_probes']} ({h['n_fenced']}) | u{h['final_update']} | {h['max_streak']} | {json.dumps(h['landed_by_name'])} |")
        lines += ["", f"Trip world {r['world']} at u{r['trip']} (trunk at u{list(r['trunk_probe_used'].values())[0]}), per seat: "
                  "first flag tick / flagged ticks / flags / hap min / applied eat / applied drink / moves / partnered / chow seen", ""]
        lines += ["| run | " + " | ".join(r["seats"].values()) + " |", "|---|" + "---|" * len(r["seats"])]
        for tag, o in r["onset_at_trip"].items():
            cells = []
            for nm in r["seats"].values():
                p = o["per_seat"][nm]
                cells.append(f"{p['first_flag_tick']} / {p['flag_ticks']} / {','.join(p['flags_by_kind']) or '-'} / {p.get('hap_min', '-')} / "
                             f"{p.get('applied_eat_ticks', '-')} / {p.get('applied_drink_ticks', '-')} / {p['moves_proposed']} / {p['partnered_share']} / {p['chow_visible_share']}")
            lines.append(f"| {tag} (n flagged {o['n_flagged']}, onset spread {o['onset_spread_ticks']}) | " + " | ".join(cells) + " |")
        lines += ["", "Divergence (clean probe before vs trip probe, first tick proposals differ / ticks differ): "
                  + json.dumps({n: [v["first_tick_proposals_differ"], v["ticks_differ"]] for n, v in r["divergence"]["per_seat"].items()}), ""]
        for tag, ser in r["seat_series"].items():
            for nm in r["seats"].values():
                cells = [f"u{u}:{v[nm]['streak']}/{v[nm].get('hap_min', '-')}/{v[nm]['chow_memory']}/{v[nm]['eat_legal_n']}/{v[nm].get('ticks_eaten', '-')}"
                         for u, v in ser.items() if v[nm]["streak"] > 0 or v[nm]["flag_ticks"] > 0]
                lines.append(f"- {tag} {nm} on {r['world']}: probes with any own flag {len(cells)} of {len(ser)} (u:streak/hap min/chow mem/eat legal/eaten): " + " ".join(cells))
        lines.append("")
    lines.append("Facts off the dumps; nothing scored, nothing selected (entry 29: the consequence is hers).")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "reads" / "diag-act10-s2s4.json")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--cases", default="s2,s4")
    a = ap.parse_args()
    names = G.kitty_names()
    res = {"method": "dump-only via diag_nohead_s1 + diag_act10_s1_seed (own SELF_DISTRESS flags; window / share reads; "
                     "the fence: every probe's per-world maxima reproduce metrics.jsonl); no regeneration, no collection",
           "land_min": LAND_MIN, "cases": {}}
    for case in a.cases.split(","):
        res["cases"][case] = analyse(case, names)
        r = res["cases"][case]
        for tag, h in r["runs"].items():
            print(f"{case} {tag}: {h['n_probes']} probes ({h['n_fenced']} fenced), max streak {h['max_streak']}, by seat {h['landed_by_name']}")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(res, indent=1) + "\n")
    if a.md:
        text = md(res)
        a.out.with_suffix(".md").write_text(text + "\n")
        print(text)


if __name__ == "__main__":
    main()
