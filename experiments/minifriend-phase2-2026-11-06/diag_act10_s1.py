"""Entry-26 localisation of the p2-act10-s1 halt (frozen probe-distress stop at update 3499 / 10,752,000 ticks), with the
entry-25 instrument (diag_nohead_s1: own SELF_DISTRESS flags localise the streak; window / contrast / share reads).
Dump-only: reads the halted run's own probe dumps; zero regeneration, zero collection. Asserts the recorded per-seed
streaks ([0, 378, 0]) reproduce from the dump before reading anything.

  VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B diag_act10_s1.py [--out reads/diag-act10-s1.json]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diag_nohead_s1 as G  # noqa: E402  (p2_common on its path puts the act arc + trunk trainer on sys.path)

RUN = G.C.ARTS / "p2-act10-s1"
STOP_PROBE = "probe-u3499"
STOP_UPDATE = 3499
CONTRAST_PROBES = ("probe-u3449", "probe-u3399", "probe-u3299")   # the three probes before the trip, same world / kitty / ticks
SHARE_PROBES = ("probe-u399", "probe-u1999", "probe-u3449", STOP_PROBE)
PRE_TICKS = 170


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "reads" / "diag-act10-s1.json")
    a = ap.parse_args()
    names = G.kitty_names()
    recorded = [json.loads(l) for l in (RUN / "metrics.jsonl").read_text().splitlines() if '"probe": true' in l][-1]
    assert recorded["update"] == STOP_UPDATE, recorded["update"]
    d = G.load(RUN / f"{STOP_PROBE}.npz")
    loc = G.localise(d)
    per_seed = {s: max(v[0] for v in loc[s].values()) for s in loc}
    worst = max(per_seed.values())
    assert worst == recorded["max_distress_streak"], f"streak did not reproduce: {worst} vs recorded {recorded['max_distress_streak']}"
    assert list(per_seed.values()) == recorded["max_distress_streak_per_seed"], (per_seed, recorded["max_distress_streak_per_seed"])
    seed = max(per_seed, key=per_seed.get)
    kitty = max(loc[seed], key=lambda k: loc[seed][k][0])
    streak, span = loc[seed][kitty]
    located = {"seed": seed, "kitty": kitty, "name": names[kitty - 1], "streak": streak, "span": list(span), "per_seed_max_streak": per_seed,
               "recorded": recorded["max_distress_streak_per_seed"], "nash_at_stop": recorded["nash"],
               "all_streaks_this_world": {names[k - 1]: v[0] for k, v in loc[seed].items()}}
    history = [{"update": r["update"], "ticks": r["ticks"], "per_seed": r["max_distress_streak_per_seed"]}
               for r in (json.loads(l) for l in (RUN / "metrics.jsonl").read_text().splitlines() if '"probe": true' in l)
               if r["max_distress_streak"] > 0]
    window = G.window_read(d, seed, kitty, span)
    pre = G.window_read(d, seed, kitty, (max(0, span[0] - PRE_TICKS), span[0] - 1))
    others = {}
    for k in sorted(np.unique(d["kitty"]).tolist()):
        if k == kitty:
            continue
        s = (d["seed"] == seed) & (d["kitty"] == k) & (d["tick"] >= span[0]) & (d["tick"] <= span[1])
        others[names[k - 1]] = {"applied_eat_ticks": int((d["applied"][s] == G.D.ACT_NAMES.index("eat")).sum()),
                                "applied_drink_ticks": int((d["applied"][s] == G.D.ACT_NAMES.index("drink")).sum()),
                                "eat_need_mean": round(float((d["obs"][s][:, G.L.SELF_NEEDS] * 100).mean()), 1),
                                "hap_min": round(float(d["hap"][s].min()), 1)}
    contrast = {}
    for p in CONTRAST_PROBES:
        e = G.load(RUN / f"{p}.npz")
        sel = (e["seed"] == seed) & (e["kitty"] == kitty)
        on = G.own_flags(e["obs"][sel]).any(1)
        wr = G.window_read(e, seed, kitty, span)
        contrast[p] = {"flagged_ticks_world": int(on.sum()), "longest_run_world": G.longest_run(on)[0],
                       "flag_ticks_in_window": {n: wr["flag_ticks_by_kind"][n] for n in G.L.NEED_KINDS if wr["flag_ticks_by_kind"][n]},
                       "act_hist_top8": dict(list(wr["act_hist"].items())[:8]), "mean_legal_acts": wr["mean_legal_acts"],
                       "eat_legal_ticks": len(wr["eat_legal_ticks"]), "chow_memory_present_share": wr["memory_present_share"]["chow"],
                       "kitty_rows_present_share": wr["kitty_rows_present_share"], "partnered_share": wr["partnered_share"]}
    shares = {p: G.whole_probe_shares(G.load(RUN / f"{p}.npz")) for p in SHARE_PROBES}
    out = {"run": str(RUN), "stop_probe": STOP_PROBE, "located": located, "nonzero_streak_history": history,
           "behaviour": {"window": window, "pre": pre}, "others_in_window": others,
           "contrast_same_kitty_world_window": contrast, "whole_probe_shares": shares,
           "method": "dump-only via diag_nohead_s1.localise / window_read (entry 25's instrument); no regeneration, no collection"}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    w = {k: v for k, v in window.items() if k != "eat_legal_ticks"}
    w["eat_legal_ticks_n"] = len(window["eat_legal_ticks"])
    print(json.dumps({"located": located, "history": history, "window": w, "others": others}, indent=1))


if __name__ == "__main__":
    main()
