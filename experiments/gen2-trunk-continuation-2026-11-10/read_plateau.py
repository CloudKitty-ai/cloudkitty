"""R-3, the plateau-rule replay (DECLARATION §6 R-3, §7 P52; her item 3 of 2026-11-10: a finer plateau rule for Gen 3;
guard g7). Zero cost: recorded `metrics.jsonl` bins only.
Every recorded bin series — the eleven trunk seeds, the twelve Phase 2 runs, the continuations once they exist — is
replayed under the FROZEN rule and five candidates; per rule: the bin and tick it would have stopped the series at,
and the return left on the table (the series' last recorded bin return minus the return at that stop). A rule that
does not fire inside the recorded series reads "no stop": the series was itself ended by the frozen rule or a welfare
stop, so nothing past its end exists to score (DECLARATION §10).
Rules (a bin is FLAT against its predecessor; N flat bins in a row stop):
  frozen       return gain < 0.005 AND anchor-KL moved < 10% relative or < 0.02 absolute; N = 3  (train_ppo_g2.plateau_flat)
  ret0.002x3   the same with the return line at 0.002          ret0.001x3   at 0.001
  ret0.005x5   the frozen flatness, N = 5                      return-only  the frozen return line, KL clause dropped, N = 3
  slope2       stop at the first bin whose return is < 0.004 above the bin two before it (< 0.002 a bin over the last two)
Floors: a Phase 2 run's bins count as its trainer counted them (train_ppo_p2.plateau_step: a bin is flat only if it
and its predecessor closed after 8,002,560 ticks); a trunk series has no floor.
The frozen replay must reproduce every recorded flat flag and every recorded stop (g7) or this reader raises.
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_plateau.py --out reads/r3/plateau.json [--md]
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import read_curves as RC  # noqa: E402
sys.path.insert(0, str(RC.EXPTS / "minifriend-phase2-2026-11-06"))
import train_ppo_p2 as P  # noqa: E402  (puts the trunk trainer on the path; FLOOR_TICKS, plateau_step)
import train_ppo_g2 as T  # noqa: E402  (plateau_flat, the frozen constants)

# name: (return line, KL clause, flat bins to stop)
RULES = {"frozen": (T.PLATEAU_RETURN, True, T.PLATEAU_BINS), "ret0.002x3": (0.002, True, 3), "ret0.001x3": (0.001, True, 3),
         "ret0.005x5": (T.PLATEAU_RETURN, True, 5), "return-only": (T.PLATEAU_RETURN, False, 3)}
SLOPE2 = 0.002


def flat(prev, cur, ret_line, kl_clause):
    if prev["ret"] is None or cur["ret"] is None:
        return False
    d_kl = abs(cur["kl"] - prev["kl"])
    kl_flat = d_kl < T.PLATEAU_KL_REL * abs(prev["kl"]) or d_kl < T.PLATEAU_KL_ABS
    return bool(cur["ret"] - prev["ret"] < ret_line and (kl_flat or not kl_clause))


def replay(bins, floor, rule):
    """(flat flags, index of the stopping bin or None) for one rule over one series."""
    ret_line, kl_clause, n = RULES[rule]
    flags, streak, stop = [], 0, None
    for i, b in enumerate(bins):
        f = i > 0 and b["ticks"] > floor and bins[i - 1]["ticks"] > floor and flat(bins[i - 1], b, ret_line, kl_clause)
        flags.append(f)
        streak = streak + 1 if f else 0
        if stop is None and streak >= n:
            stop = i
    return flags, stop


def replay_slope2(bins, floor):
    for i in range(2, len(bins)):
        if bins[i - 2]["ticks"] > floor and None not in (bins[i]["ret"], bins[i - 2]["ret"]) and (bins[i]["ret"] - bins[i - 2]["ret"]) / 2 < SLOPE2:
            return i
    return None


def all_series():
    runs = [(d.name, d, 0) for d in sorted(RC.TRUNK.glob("ppo-g2-trunk-s*"), key=lambda p: int(p.name.rsplit("s", 1)[1]))]
    runs += [(d.name, d, P.FLOOR_TICKS) for d in sorted(RC.P2.glob("p2-*")) if d.is_dir()]
    runs += [(d.name, d, None) for d in sorted(RC.CONT.glob("cont-s*")) if (d / "metrics.jsonl").exists()]
    return runs


def read():
    out, loaded = {}, []
    for name, d, floor in all_series():
        assert floor is not None, "a continuation's floor is deviations entry 32's ruling; not wired until she rules"
        loaded.append((name, floor, RC.series(d)) + RC.stop(d))
    # g7, first over every series: the frozen replay reproduces every recorded stop (a plateau stop at the last bin;
    # a run halted by a welfare stop shows none)
    for name, floor, bins, ticks, reason in loaded:
        stop = replay(bins, floor, "frozen")[1]
        want = len(bins) - 1 if reason == "plateau" else None
        assert stop == want, f"{name}: frozen replay stops at bin {None if stop is None else stop + 1}, the record ({reason}) at bin {None if want is None else want + 1}"
    # then the stricter half: every recorded flat flag, and this file's frozen flatness equals the trainer's own
    for name, floor, bins, ticks, reason in loaded:
        flags = replay(bins, floor, "frozen")[0]
        assert flags == [b["flat"] for b in bins], f"{name}: frozen replay flags {flags} != recorded {[b['flat'] for b in bins]}"
        assert all(flat(bins[i - 1], bins[i], T.PLATEAU_RETURN, True) == T.plateau_flat(bins[i - 1], bins[i]) for i in range(1, len(bins))), name
    for name, floor, bins, ticks, reason in loaded:
        row = {"bins": len(bins), "floor": floor, "stop_ticks": ticks, "stop_reason": reason, "rules": {}}
        for rule in list(RULES) + ["slope2"]:
            s = replay_slope2(bins, floor) if rule == "slope2" else replay(bins, floor, rule)[1]
            row["rules"][rule] = None if s is None else {"bin": s + 1, "ticks": bins[s]["ticks"], "ret": bins[s]["ret"],
                                                         "left_on_table": bins[-1]["ret"] - bins[s]["ret"], "bins_before_end": len(bins) - 1 - s}
        out[name] = row
    return out


def md(out):
    rules = list(RULES) + ["slope2"]
    L = ["# R-3 — the plateau-rule replay on every recorded bin series", "",
         "Cell = the bin the rule would have stopped the series at (return left on the table: the last recorded bin's return minus the return at that stop); "
         "— = the rule does not fire inside the recorded series.", "",
         "| series | bins | recorded stop (ticks, reason) | " + " | ".join(rules) + " |", "|---|---|---|" + "---|" * len(rules)]
    for name, r in out.items():
        cells = ["—" if r["rules"][k] is None else f"bin {r['rules'][k]['bin']} ({r['rules'][k]['left_on_table']:+.4f})" for k in rules]
        L.append(f"| {name} | {r['bins']} | {r['stop_ticks']:,}, {r['stop_reason']} | " + " | ".join(cells) + " |")
    plateau = [n for n, r in out.items() if r["stop_reason"] == "plateau"]
    L += ["", f"Series ended by the plateau rule: {len(plateau)} of {len(out)}. Per rule, over those {len(plateau)}: "
          + "; ".join(f"{k} stops {sum(out[n]['rules'][k] is not None and out[n]['rules'][k]['bins_before_end'] == 0 for n in plateau)} at the recorded bin, "
                      f"{sum(out[n]['rules'][k] is not None and out[n]['rules'][k]['bins_before_end'] > 0 for n in plateau)} earlier, "
                      f"{sum(out[n]['rules'][k] is None for n in plateau)} not inside the record" for k in rules) + "."]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True); ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    res = read()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(res, indent=1) + "\n")
    if a.md:
        a.out.with_suffix(".md").write_text(md(res))
    print(json.dumps({n: {k: (None if v is None else v["bin"]) for k, v in r["rules"].items()} for n, r in res.items()}))
