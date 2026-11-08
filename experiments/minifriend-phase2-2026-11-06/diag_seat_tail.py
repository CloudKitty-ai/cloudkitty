"""Per-seat distress TAIL across every probe of a run set (owner 2026-11-07/08, on entry 26's seed read: "If pumpkin is
always the source of streaks, we should maybe look at rebalancing her need traits? When we initially set them, the goal
was for them to be roughly welfare neutral"). Dump-only, zero regeneration: for each run and each seat, over all its probe
dumps — own-flag ticks per 1,000 seat-ticks, eat-flag ticks per 1,000, happiness mean (where the dump carries it), and
the count of own-flag streaks >= 10 ticks; the per-world streak maxima fenced against metrics.jsonl at every probe.
The banked Gen 3 input (gen3-roadmap-inputs-2026-10-04.md) cites this read.

  VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B diag_seat_tail.py [--out reads/seat-tail.json]
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diag_nohead_s1 as G  # noqa: E402
import diag_act10_s1_seed as Q  # noqa: E402

RUNS = {"p2-act10-s1": G.C.ARTS / "p2-act10-s1", "p2-act15-s1": G.C.ARTS / "p2-act15-s1", "p2-nohead-s1r": G.C.ARTS / "p2-nohead-s1r",
        "trunk-s1": G.C.TRUNK_ARTS / "ppo-g2-trunk-s1", "trunk-s2": G.C.TRUNK_ARTS / "ppo-g2-trunk-s2", "trunk-s4": G.C.TRUNK_ARTS / "ppo-g2-trunk-s4"}
EAT = G.L.NEED_KINDS.index("eat")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "reads" / "seat-tail.json")
    a = ap.parse_args()
    names = G.kitty_names()
    out = {"runs": {}, "method": "dump-only via diag_nohead_s1 (own SELF_DISTRESS flags); per-world maxima fenced against metrics.jsonl at every probe"}
    for tag, run in RUNS.items():
        rows = Q.recorded_rows(run)
        acc = {k: {"ticks": 0, "flag_ticks": 0, "eat_flag_ticks": 0, "hap_sum": 0.0, "hap_n": 0, "streaks_ge_10": 0} for k in range(1, 6)}
        fenced = 0
        for u, p in Q.probes(run):
            d = G.load(p)
            loc = G.localise(d)
            if u in rows:
                per_seed = [max(v[0] for v in loc[s].values()) for s in sorted(loc)]
                rec = rows[u]["max_distress_streak_per_seed"]
                assert per_seed == rec, f"{tag} u{u}: streak did not reproduce: {per_seed} vs recorded {rec}"
                fenced += 1
            for k, c in acc.items():
                sel = d["kitty"] == k
                f = G.own_flags(d["obs"][sel])
                c["ticks"] += int(sel.sum())
                c["flag_ticks"] += int(f.any(1).sum())
                c["eat_flag_ticks"] += int(f[:, EAT].sum())
                if "hap" in d:
                    c["hap_sum"] += float(d["hap"][sel].sum())
                    c["hap_n"] += int(sel.sum())
                c["streaks_ge_10"] += sum(1 for s in loc for kk, (st, _) in loc[s].items() if kk == k and st >= 10)
        seats = {}
        for k, c in acc.items():
            seats[names[k - 1]] = {"flag_per_1k": round(c["flag_ticks"] / c["ticks"] * 1000, 2), "eat_flag_per_1k": round(c["eat_flag_ticks"] / c["ticks"] * 1000, 2),
                                   "streaks_ge_10": c["streaks_ge_10"], "hap_mean": round(c["hap_sum"] / c["hap_n"], 1) if c["hap_n"] else None}
        out["runs"][tag] = {"n_probes": len(Q.probes(run)), "n_fenced": fenced, "seats": seats}
        print(tag, out["runs"][tag]["n_probes"], "probes:", json.dumps(seats))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
