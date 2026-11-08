"""Entry-26 analysis of the failed seed p2-act10-s1 (owner 2026-11-07 "Act10 s1 replace and analyze the failed seed"),
with entry 25's instrument (diag_nohead_s1: own SELF_DISTRESS flags localise a streak; window / share reads). Dump-only:
every read is off the runs' own probe dumps (3 worlds × 2,000 ticks × 5 seats each); zero regeneration, zero collection.

Reads: (1) HISTORY — every probe of the halted run: the longest own-flag streak per (world, kitty), the per-world maxima
asserted equal to metrics.jsonl's probe row at EVERY probe (the fence), and where the streaks land; (2) THE SEAT —
Pumpkin (kitty_3) on world 40,002 at every probe: longest streak, flagged ticks by need, happiness min, chow in memory /
sight, eat-legal ticks, ticks eaten, moves / solo / partner shares; (3) PAIRED — the same seat series on p2-act15-s1,
p2-nohead-s1r and the parent trunk-s1 (the same deterministic probe worlds), and where each run's streaks land;
(4) PER-SEAT shares at each run's final probe (is Pumpkin's seat behaviourally distinct?); (5) DIVERGENCE — on 40,002
the first tick at which the clean probe before the trip (u3449) and the trip probe (u3499) propose differently.

  VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B diag_act10_s1_seed.py [--out reads/diag-act10-s1-seed.json]
"""
import argparse
import glob
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diag_nohead_s1 as G  # noqa: E402

RUNS = {"p2-act10-s1": G.C.ARTS / "p2-act10-s1", "p2-act15-s1": G.C.ARTS / "p2-act15-s1",
        "p2-nohead-s1r": G.C.ARTS / "p2-nohead-s1r", "trunk-s1": G.C.TRUNK_ARTS / "ppo-g2-trunk-s1"}
FAILED = "p2-act10-s1"
SEAT = (40002, 3)            # world 40,002, kitty_3 = Pumpkin's seat (entry 26's localisation)
CLEAN_BEFORE, TRIP = 3449, 3499
LAND_MIN = 10                # streaks at or above this are listed per run with their (update, world, kitty)


def probes(run):
    ps = sorted(glob.glob(str(run / "probe-u*.npz")), key=lambda p: int(p.split("-u")[1].split(".")[0]))
    return [(int(p.split("-u")[1].split(".")[0]), Path(p)) for p in ps]


def recorded_rows(run):
    return {r["update"]: r for r in (json.loads(l) for l in (run / "metrics.jsonl").read_text().splitlines()) if r.get("probe")}


def seat_read(d, seed, kitty, names):
    sel = (d["seed"] == seed) & (d["kitty"] == kitty)
    t = d["tick"][sel]
    w = G.window_read(d, seed, kitty, (int(t.min()), int(t.max())))
    flags = G.own_flags(d["obs"][sel])
    r = {"streak": G.longest_run(flags.any(1))[0], "flag_ticks": int(flags.any(1).sum()),
         "flag_ticks_by_kind": {k: v for k, v in w["flag_ticks_by_kind"].items() if v},
         "chow_memory": w["memory_present_share"]["chow"], "chow_visible": w["chow_visible_share"],
         "eat_legal_n": len(w["eat_legal_ticks"]), "eat_proposed": w["eat_proposed"], "moves_proposed": w["moves_proposed"],
         "mean_legal_acts": w["mean_legal_acts"], "partnered_share": w["partnered_share"],
         "needs_max": {n: round(float((d["obs"][sel][:, G.L.SELF_NEEDS + i] * 100).max()), 1) for i, n in enumerate(G.L.NEED_KINDS)}}
    sub = {"act": d["act"][sel], "mask": d["mask"][sel]}
    sh = G.whole_probe_shares(sub)
    r.update({"solo": sh["solo"], "partner": sh["partner"], "eat_when_legal": sh["eat_when_legal"]})
    if "hap" in d:
        r["hap_min"] = w["hap_min"]
    if "applied" in d:
        r["ticks_eaten"] = int((d["applied"][sel] == G.D.ACT_NAMES.index("eat")).sum())
    return r


def per_seat_shares(d, names):
    out = {}
    for k in sorted(np.unique(d["kitty"]).tolist()):
        sel = d["kitty"] == k
        sh = G.whole_probe_shares({"act": d["act"][sel], "mask": d["mask"][sel]})
        sh = {x: sh[x] for x in ("solo", "partner", "eat", "eat_when_legal", "moves", "mean_legal")}
        sh["flag_tick_share"] = round(float(G.own_flags(d["obs"][sel]).any(1).mean()), 4)
        if "hap" in d:
            sh["hap_mean"] = round(float(d["hap"][sel].mean()), 1)
        out[names[k - 1]] = sh
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "reads" / "diag-act10-s1-seed.json")
    a = ap.parse_args()
    names = G.kitty_names()
    out = {"runs": {}, "seat": {"world": SEAT[0], "kitty": SEAT[1], "name": names[SEAT[1] - 1]}, "divergence": None,
           "method": "dump-only via diag_nohead_s1 (own SELF_DISTRESS flags; window / share reads); no regeneration, no collection"}
    keep = {}
    for tag, run in RUNS.items():
        rows = recorded_rows(run)
        ps = probes(run)
        landed, seat_series, fenced = [], {}, 0
        for u, p in ps:
            d = G.load(p)
            loc = G.localise(d)
            per_seed = [max(v[0] for v in loc[s].values()) for s in sorted(loc)]
            if u in rows:   # the fence: the dump reproduces the stop instrument's own record at every probe
                rec = rows[u]["max_distress_streak_per_seed"]
                assert per_seed == rec, f"{tag} u{u}: streak did not reproduce: {per_seed} vs recorded {rec}"
                fenced += 1
            for s in sorted(loc):
                for k, (st, span) in loc[s].items():
                    if st >= LAND_MIN:
                        landed.append({"update": u, "world": s, "kitty": k, "name": names[k - 1], "streak": st, "span": list(span)})
            seat_series[u] = seat_read(d, *SEAT, names)
            if tag == FAILED and u in (CLEAN_BEFORE, TRIP):
                keep[u] = d
        final_u, final_p = ps[-1]
        d = G.load(final_p)
        by_name = {}
        for e in landed:
            by_name.setdefault(e["name"], []).append(e["streak"])
        out["runs"][tag] = {"n_probes": len(ps), "n_fenced": fenced, "final_update": final_u,
                            "max_streak": max(e["streak"] for e in landed) if landed else 0,
                            "landed_ge_%d" % LAND_MIN: landed, "landed_by_name": {n: sorted(v, reverse=True) for n, v in by_name.items()},
                            "seat_series": seat_series, "final_per_seat": per_seat_shares(d, names)}
        print(f"{tag}: {len(ps)} probes ({fenced} fenced), max streak {out['runs'][tag]['max_streak']}, "
              f"streaks >= {LAND_MIN} by seat {out['runs'][tag]['landed_by_name']}")
    # (5) divergence between the clean probe before the trip and the trip probe, world 40,002
    a0, a1 = keep[CLEAN_BEFORE], keep[TRIP]
    div = {}
    for k in sorted(np.unique(a1["kitty"]).tolist()):
        s0 = (a0["seed"] == SEAT[0]) & (a0["kitty"] == k)
        s1 = (a1["seed"] == SEAT[0]) & (a1["kitty"] == k)
        assert (a0["tick"][s0] == a1["tick"][s1]).all()
        diff = np.nonzero(a0["act"][s0] != a1["act"][s1])[0]
        div[names[k - 1]] = {"first_tick_proposals_differ": int(a0["tick"][s0][diff[0]]) if len(diff) else None,
                             "ticks_differ": int(len(diff)), "ticks": int(s1.sum())}
    out["divergence"] = {"world": SEAT[0], "probes": [CLEAN_BEFORE, TRIP], "per_seat": div}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    # a compact print of the seat series: streak / hap min / chow memory / eat legal / ticks eaten per probe, per run
    for tag, r in out["runs"].items():
        ser = r["seat_series"]
        cells = [f"u{u}:{v['streak']}/{v.get('hap_min', '-')}/{v['chow_memory']}/{v['eat_legal_n']}/{v.get('ticks_eaten', '-')}" for u, v in ser.items()
                 if v["streak"] > 0 or v["flag_ticks"] > 0]
        print(f"{tag} {names[SEAT[1] - 1]} on {SEAT[0]}, probes with any own flag (streak/hap min/chow mem/eat legal/eaten): {len(cells)} of {len(ser)}")
        print("  " + " ".join(cells))
    print("divergence", json.dumps(out["divergence"]["per_seat"]))


if __name__ == "__main__":
    main()
