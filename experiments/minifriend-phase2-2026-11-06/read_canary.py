#!/usr/bin/env python3
"""Entry 27's reading grammar on the canary arm `both`, one seed at a time (gen2-deviations.md entry 27; P45–P47).
Record-only: it reads recorded legs (replay.leg_rows), the R-2 episode records read_r2 derives from them, the
trainer's own metrics.jsonl, and — the one replay here — the frozen needs head stepped over a recorded leg's
observations (R-4 extended to the needs head; nothing covered decides, the actions are the record's). Nothing
here is a selector: every verdict column is reported for her, the consequence is hers (entry 27's grammar).

    read_canary.py score      [--seed 1] [--size 20] [--slot p2-both-s1] --out reads/canary-s1.json [--md]
    read_canary.py needs-leg  --seating p2u-both-s1 --size 20 [--seeds 905001,...] --out reads/canary/needs-leg-p2u-both-s1-20.json

The grammar's three columns, one seed k (the scout is s1):
 (1) R-1a — paired team happiness per world on the 20×20 uniform legs: both-s_k − act15-s_k (P46: |mean Δ| ≤ the
     uniform edge statistic, 0.326 at 20×20, read_r1's recipe), both-s_k − trunk-s_k (the recorded battery row), and
     both-s_k − nohead-s_k beside; act15-s_k − trunk-s_k as the reference pair. One seed clears nothing (the
     three-seed valve): the read is harm, null or signal, hers to name.
 (2) R-2a / R-2b on both-s_k against trunk-s_k, act15-s_k beside (read_r2's episode records; the same cells, p90,
     min-n and +25% rule): P47 = no stratum with a readable OTHER-relief cell on both sides is DEGRADED (entry 27:
     "other-relief p90 within +25% in every stratum with n ≥ 200"); no readable stratum = UNDECIDABLE, never met.
     R-2b's approach-propensity differential on both, act15 and trunk encounters.
 (3) the needs read's trajectory from the trainer's metrics.jsonl: per probe the cumulative `needs_trigger` state
     per version and the per-probe `needs_bias_probe` grave bias (mean, SD, n); P45's lived half = the cumulative
     in-sight grave bias at the last probe within one of its own SDs of the gate's in-sight figure
     (minifriend-phase2-gate reads/needs.json summary/NF1e/visible/grave = −3.17), UNDECIDABLE under min-n 200;
     P45's leg half = the needs-leg read's state (SIGNATURE at the first sufficient stratum).
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p2_common as C  # noqa: E402
import replay as RP  # noqa: E402
import read_r1 as R1  # noqa: E402
import read_r2 as R2  # noqa: E402

READS = HERE / "reads"
GATE_NEEDS = C.EXPTS / "minifriend-phase2-gate-2026-11-05" / "reads" / "needs.json"
MIN_N = 200                         # the frozen min-n (train_ppo_p2.TRIGGER_MIN_N; §8.2)


# ---------------------------------------------------------------- (1) R-1a, one seed

def edge(size):
    """The uniform edge statistic at `size` by read_r1's declared recipe (the battery's printed trained means)."""
    gj = json.loads((C.BATTERY / "gate-read.json").read_text())
    e = R1.edge_statistic([gj[f"g2-s{k}/{size}"]["trained_mean"] for k in R1.SEEDS])
    if size in R1.EDGE_DECLARED:
        assert round(e, 3) == R1.EDGE_DECLARED[size], (size, e)
    return e


def paired(rows_a, rows_b):
    """Per-WORLD team deltas a − b keyed by the world seed (never by position); the two legs must cover the same worlds."""
    assert set(rows_a) == set(rows_b), (sorted(set(rows_a) ^ set(rows_b)))
    d = {s: C.team(rows_a[s]) - C.team(rows_b[s]) for s in sorted(rows_a)}
    v = list(d.values())
    return {"n": len(v), "mean": float(np.mean(v)), "positive": int(sum(x > 0 for x in v)),
            "range": [float(min(v)), float(max(v))], "per_world": {str(k): float(x) for k, x in d.items()}}


def p46(delta_vs_act15, bar):
    """P46: |mean paired Δ both − act15| ≤ the edge statistic (a null). One seed: reported, never a clearance."""
    v = abs(delta_vs_act15["mean"])
    return {"value": v, "bar": bar, "met": bool(v <= bar), "signed_mean": delta_vs_act15["mean"],
            "text": "|both − act15| paired team happiness ≤ the uniform edge statistic (one seed; clears nothing alone)"}


def leg_or_none(seating, size, root):
    try:
        return RP.leg_rows(seating, size, root)[0]
    except FileNotFoundError:
        return None


def r1a(seed, size, root=None):
    both = leg_or_none(f"p2u-both-s{seed}", size, root)
    if both is None:
        return {"state": f"p2u-both-s{seed} leg not recorded at {size}"}
    act15 = leg_or_none(f"p2u-act15-s{seed}", size, root)
    nohead = leg_or_none(f"p2u-nohead-s{seed}", size, root)
    trunk = C.battery_rows(f"g2-s{seed}", size)
    bar = edge(size)
    out = {"edge": bar, "team": {"both": float(np.mean([C.team(r) for r in both.values()])),
                                 "trunk": float(np.mean([C.team(r) for r in trunk.values()]))},
           "worst_streak_max": {"both": int(max(r["max_distress_age"] for r in both.values()))},
           "aborted_worlds": {"both": sorted(s for s in both if "aborted_streak" in both[s])},
           "f053_events": {"both": sorted(s for s in both if both[s]["max_distress_age"] >= R1.F053)},
           "paired": {"both_minus_trunk": paired(both, trunk)}}
    if act15 is not None:
        out["team"]["act15"] = float(np.mean([C.team(r) for r in act15.values()]))
        out["worst_streak_max"]["act15"] = int(max(r["max_distress_age"] for r in act15.values()))
        out["paired"]["both_minus_act15"] = paired(both, act15)
        out["paired"]["act15_minus_trunk"] = paired(act15, trunk)
        out["P46"] = p46(out["paired"]["both_minus_act15"], bar)
    else:
        out["P46"] = {"met": None, "state": f"p2u-act15-s{seed} leg not recorded at {size}"}
    if nohead is not None:
        out["team"]["nohead"] = float(np.mean([C.team(r) for r in nohead.values()]))
        out["paired"]["both_minus_nohead"] = paired(both, nohead)
    return out


# ---------------------------------------------------------------- (2) R-2a / R-2b, one seed

def p47(verdicts):
    """P47 over the per-stratum OTHER-relief verdicts {stratum: HELD | DEGRADED | UNDECIDABLE}: met iff at least one
    stratum is readable and none is DEGRADED; no readable stratum is UNDECIDABLE, never met."""
    readable = {st: v for st, v in verdicts.items() if v != "UNDECIDABLE"}
    met = bool(readable) and not any(v == "DEGRADED" for v in readable.values())
    return {"met": met, "state": "UNDECIDABLE (no stratum reaches min-n on both sides)" if not readable else ("MET" if met else "NOT MET"),
            "readable": sorted(readable), "degraded": sorted(st for st, v in readable.items() if v == "DEGRADED"),
            "text": "R-2a other-relief p90 on both not DEGRADED (> +25%) against trunk in any stratum with n ≥ 200 on both sides"}


def r2(seed, size):
    eps = {name: R2.load_ep(seating, size) for name, seating in
           (("both", f"p2u-both-s{seed}"), ("act15", f"p2u-act15-s{seed}"), ("trunk", f"g2-s{seed}"))}
    missing = [n for n in ("both", "trunk") if eps[n] is None]
    if missing:
        return {"state": f"episode records missing for {missing} at {size} (read_r2.py episodes --seating ... first)"}
    pooled = {n: (R2.pool(e, "episodes") if e is not None else None) for n, e in eps.items()}
    strata = {}
    other_verdicts = {}
    for st in R2.STRATA_R2A:
        row = {}
        for n, es in pooled.items():
            if es is None:
                continue
            sel = [e for e in es if e["stratum"] == st]
            row[n] = {"all": R2.r2a_cell(sel), "other": R2.r2a_cell([e for e in sel if e["source"] == "other"])}
        for kind in ("all", "other"):
            b, t = row["both"][kind], row["trunk"][kind]
            row[f"both_vs_trunk_{kind}"] = R2.held_or_degraded(b.get("p90"), t.get("p90")) if b["state"] == "READ" and t["state"] == "READ" else "UNDECIDABLE"
            if "act15" in row:
                a = row["act15"][kind]
                row[f"act15_vs_trunk_{kind}"] = R2.held_or_degraded(a.get("p90"), t.get("p90")) if a["state"] == "READ" and t["state"] == "READ" else "UNDECIDABLE"
        other_verdicts[st] = row["both_vs_trunk_other"]
        strata[st] = row
    out = {"r2a": strata, "P47": p47(other_verdicts),
           "r2b": {n: R2.score_r2b(R2.pool(e, "encounters")) for n, e in eps.items() if e is not None}}
    return out


# ---------------------------------------------------------------- (3) the needs read's trajectory (metrics.jsonl)

def gate_reference():
    s = json.loads(GATE_NEEDS.read_text())["summary"]["NF1e"]
    return {v: {"grave": s[v]["grave"], "common": s[v]["common"], "n_grave": s[v]["n_grave"]} for v in ("visible", "all")}


def trajectory(metrics_lines):
    """Probe rows of a canary run's metrics.jsonl -> the per-probe series: the CUMULATIVE `needs_trigger` state per
    version and the PER-PROBE `needs_bias_probe` grave bias (mean / SD / n) per version."""
    series = []
    for line in metrics_lines:
        r = json.loads(line) if isinstance(line, str) else line
        if not r.get("probe") or r.get("needs_trigger") is None:
            continue
        cum, per = r["needs_trigger"]["by_version"], r["needs_bias_probe"]["by_version"]
        series.append({"update": r["update"], "ticks": r["ticks"],
                       "cumulative": {v: {"state": cum[v]["state"], "grave": cum[v]["grave"], "grave_sd": cum[v]["grave_sd"],
                                          "n_grave": cum[v]["n_grave"], "common": cum[v]["common"]} for v in cum},
                       "probe": {v: {"grave": per[v]["grave"], "grave_sd": per[v]["grave_sd"], "n_grave": per[v]["n_grave"],
                                     "common": per[v]["common"]} for v in per}})
    return series


def p45_lived(series, ref, version="visible", min_n=MIN_N):
    """P45's lived half: the cumulative grave bias (`version`) at the last probe within one of its own SDs of the
    gate's figure; UNDECIDABLE under min-n (no probe reached it)."""
    if not series:
        return {"met": None, "state": "UNDECIDABLE (no probe)"}
    last = series[-1]["cumulative"][version]
    if last["n_grave"] < min_n or last["grave"] is None:
        return {"met": None, "state": f"UNDECIDABLE (cumulative n_grave {last['n_grave']} < {min_n})", "n_grave": last["n_grave"]}
    dist = abs(last["grave"] - ref[version]["grave"])
    return {"met": bool(dist <= last["grave_sd"]), "state": "MET" if dist <= last["grave_sd"] else "NOT MET",
            "cumulative_grave": last["grave"], "sd": last["grave_sd"], "gate_grave": ref[version]["grave"], "distance": dist,
            "n_grave": last["n_grave"], "cumulative_state": last["state"],
            "text": f"cumulative {version} grave bias at the last probe within one SD of the gate's {ref[version]['grave']:.2f}"}


def trajectory_summary(series, version="visible"):
    g = [(s["update"], s["probe"][version]["grave"], s["probe"][version]["n_grave"]) for s in series]
    with_grave = [(u, v, n) for u, v, n in g if v is not None]
    first_suff = next((s["update"] for s in series if s["cumulative"][version]["state"] != "INSUFFICIENT"), None)
    states = [s["cumulative"][version]["state"] for s in series]
    return {"n_probes": len(series), "first_sufficient_update": first_suff,
            "cumulative_states": {st: states.count(st) for st in ("INSUFFICIENT", "CLEAR", "SIGNATURE")},
            "final_cumulative_state": states[-1] if states else None,
            "per_probe_grave": {"n_probes_with_grave_rows": len(with_grave),
                                "mean_of_probe_means": float(np.mean([v for _u, v, _n in with_grave])) if with_grave else None,
                                "min": float(min(v for _u, v, _n in with_grave)) if with_grave else None,
                                "max": float(max(v for _u, v, _n in with_grave)) if with_grave else None,
                                "total_grave_rows": int(sum(n for _u, _v, n in g))}}


# ---------------------------------------------------------------- the needs head on a recorded leg (R-4 extended)

def needs_bias_rows(cells_rows, needs_true, friend_j, needs_off):
    """The trainer's convention (train_ppo_p2.run_probe_p2): per (observer, friend) row, the needs head's five hidden
    estimates × 100 minus the friend's TRUE hidden needs (need points), averaged over the five; negative = read less
    needy than she is."""
    return (cells_rows[:, needs_off:needs_off + 5] * 100.0 - needs_true[friend_j, :5]).mean(1)


def needs_leg(seating, size, seeds=None, root=None):
    """The frozen needs head (ARMS['both']) stepped over every tick of a recorded leg's observations, the bias
    accumulated per version × stratum × friend as the trainer does, needs_eval's rule on the pooled leg (SIGNATURE /
    CLEAR / INSUFFICIENT, a READ). The replay fences itself against the recorded row."""
    import heads_online as HO
    import train_ppo_p2 as P
    import data_act as D
    sys.path.insert(0, str(C.EXPTS / "minifriend-phase1-2026-10-22"))
    import strata as S
    rows, header = RP.leg_rows(seating, size, root)
    acc = P.new_needs_acc()
    worlds = {}
    roster = C.ROSTER
    friends_of = [[j for j in range(roster) if j != k] for k in range(roster)]
    friend_j = np.array([friends_of[k][r] for k in range(roster) for r in range(C.N_ROWS)])
    for seed in (sorted(rows) if seeds is None else seeds):
        heads = HO.OnlineHeads("both", roster)
        per = P.new_needs_acc()
        for rec in RP.replay(RP.acts_path(seating, size, seed, root), C.LEG_TOML[size], want_obs=True, check_row=rows[seed]):
            needs_true, hap_true = rec["pre"][0], rec["pre"][1]
            codes = S.stratum(needs_true, hap_true)
            cells = heads.step(rec["obs"]).reshape(roster * C.N_ROWS, -1)
            blk = rec["obs"][:, C.SELF_BLOCK:C.SELF_BLOCK + C.N_ROWS * C.KITTY_W].reshape(roster, C.N_ROWS, C.KITTY_W)
            visible = HO.row_states(blk).reshape(-1) == D.SEEN
            bias = needs_bias_rows(cells, needs_true, friend_j, HO.NEEDS_OFF)
            P.needs_accumulate(acc, bias, codes[friend_j], friend_j, visible)
            P.needs_accumulate(per, bias, codes[friend_j], friend_j, visible)
        ev = P.needs_eval(per)
        worlds[str(seed)] = {v: {"state": ev["by_version"][v]["state"], "grave": ev["by_version"][v]["grave"],
                                 "n_grave": ev["by_version"][v]["n_grave"], "common": ev["by_version"][v]["common"]} for v in ev["by_version"]}
    ev = P.needs_eval(acc)
    return {"seating": seating, "size": size, "seats": header["seats"], "worlds": worlds, "pooled": ev,
            "state": {v: ev["by_version"][v]["state"] for v in ev["by_version"]}}


# ---------------------------------------------------------------- score

def score(seed=1, size=20, slot=None, root=None):
    slot = slot or f"p2-both-s{seed}"
    out = {"seed": seed, "size": size, "slot": slot, "r1a": r1a(seed, size, root), "r2": r2(seed, size)}
    mp = C.ARTS / slot / "metrics.jsonl"
    if mp.exists():
        series = trajectory(mp.read_text().splitlines())
        ref = gate_reference()
        out["needs"] = {"gate_reference": ref, "series": series,
                        "summary": {v: trajectory_summary(series, v) for v in ("visible", "all")},
                        "P45_lived": {v: p45_lived(series, ref, v) for v in ("visible", "all")}}
    else:
        out["needs"] = {"state": f"{mp} absent"}
    leg = READS / "canary" / f"needs-leg-p2u-both-s{seed}-{size}.json"
    if leg.exists():
        out["needs_leg"] = json.loads(leg.read_text())
        st = out["needs_leg"]["state"]                      # {version: SIGNATURE | CLEAR | INSUFFICIENT}
        out["P45_leg"] = {"met": st["visible"] == "SIGNATURE" or st["all"] == "SIGNATURE", "state": st,
                          "text": "the needs read on the arm's own 20×20 leg shows the SIGNATURE at the first sufficient stratum"}
    else:
        out["needs_leg"] = {"state": f"{leg.name} not read (read_canary.py needs-leg)"}
    return out


def md(out):
    L = [f"# Entry 27 reading grammar — {out['slot']} ({out['size']}×{out['size']})", ""]
    r = out["r1a"]
    if "state" in r:
        L.append(f"R-1a: {r['state']}")
    else:
        L += ["## (1) R-1a paired team happiness", "", "| pair | mean Δ | +/n | range |", "|---|---|---|---|"]
        for k, d in r["paired"].items():
            L.append(f"| {k} | {d['mean']:+.3f} | {d['positive']}/{d['n']} | [{d['range'][0]:+.3f}, {d['range'][1]:+.3f}] |")
        L += ["", f"team: {json.dumps({k: round(v, 3) for k, v in r['team'].items()})}; edge {r['edge']:.3f}; worst streak max {r['worst_streak_max']}; aborts {r['aborted_worlds']}; F-053 {r['f053_events']}",
              f"P46: {'MET' if r['P46'].get('met') else r['P46'].get('state', 'NOT MET')} — {json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r['P46'].items() if k != 'text'})}"]
    r = out["r2"]
    L += ["", "## (2) R-2a / R-2b", ""]
    if "state" in r:
        L.append(r["state"])
    else:
        L += ["| stratum | both p90 (n) all / other | trunk p90 (n) all / other | act15 p90 (n) all / other | both vs trunk all / other | act15 vs trunk all / other |", "|---|---|---|---|---|---|"]
        for st, row in r["r2a"].items():
            cell = lambda n, kind: f"{row[n][kind].get('p90')} ({row[n][kind]['n']})" if n in row else "—"
            L.append(f"| {st} | {cell('both', 'all')} / {cell('both', 'other')} | {cell('trunk', 'all')} / {cell('trunk', 'other')} | {cell('act15', 'all')} / {cell('act15', 'other')} | {row['both_vs_trunk_all']} / {row['both_vs_trunk_other']} | {row.get('act15_vs_trunk_all', '—')} / {row.get('act15_vs_trunk_other', '—')} |")
        L += ["", f"P47: {r['P47']['state']} (degraded: {r['P47']['degraded']}; readable: {r['P47']['readable']})",
              "R-2b differential: " + json.dumps({n: v["differential"] for n, v in r["r2b"].items()})]
    n = out["needs"]
    L += ["", "## (3) the needs read's trajectory", ""]
    if "state" in n:
        L.append(n["state"])
    else:
        for v in ("visible", "all"):
            s = n["summary"][v]
            L.append(f"- {v}: {s['n_probes']} probes, cumulative states {s['cumulative_states']}, first sufficient update {s['first_sufficient_update']}, final {s['final_cumulative_state']}; per-probe grave bias over {s['per_probe_grave']['n_probes_with_grave_rows']} probes with grave rows: mean of means {s['per_probe_grave']['mean_of_probe_means']}, range [{s['per_probe_grave']['min']}, {s['per_probe_grave']['max']}], grave rows {s['per_probe_grave']['total_grave_rows']}")
            L.append(f"  P45 lived ({v}): {n['P45_lived'][v]['state']} — {json.dumps({k: (round(x, 3) if isinstance(x, float) else x) for k, x in n['P45_lived'][v].items() if k not in ('text', 'state')})}")
        L += ["", "| update | ticks | cum visible | cum all | probe grave visible (n) | probe grave all (n) |", "|---|---|---|---|---|---|"]
        for s in n["series"]:
            pv, pa = s["probe"]["visible"], s["probe"]["all"]
            L.append(f"| {s['update']} | {s['ticks']} | {s['cumulative']['visible']['state']} | {s['cumulative']['all']['state']} | {None if pv['grave'] is None else round(pv['grave'], 2)} ({pv['n_grave']}) | {None if pa['grave'] is None else round(pa['grave'], 2)} ({pa['n_grave']}) |")
    L += ["", "## the needs head on the leg (R-4 extended)", ""]
    nl = out["needs_leg"]
    if isinstance(nl.get("state"), str):
        L.append(nl["state"])
    else:
        bv = nl["pooled"]["by_version"]
        L.append(f"pooled: {json.dumps({v: {k: bv[v][k] for k in ('state', 'grave', 'common', 'n_grave', 'n_common')} for v in bv})}")
        L.append(f"P45 leg: {'MET' if out['P45_leg']['met'] else 'NOT MET'} — {out['P45_leg']['state']}")
    L += ["", "One seed clears nothing (the three-seed valve); every consequence is hers (entry 27's grammar)."]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["score", "needs-leg"])
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--size", type=int, default=20)
    ap.add_argument("--slot", default=None)
    ap.add_argument("--seating", default=None)
    ap.add_argument("--seeds", default=None, help="needs-leg: comma list of worlds (default all 30)")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--root", type=Path, default=None)
    a = ap.parse_args()
    if a.cmd == "needs-leg":
        import torch
        torch.set_num_threads(1)
        seeds = None if a.seeds is None else [int(s) for s in a.seeds.split(",")]
        out = needs_leg(a.seating, a.size, seeds, a.root)
        p = a.out or READS / "canary" / f"needs-leg-{a.seating}-{a.size}.json"
    else:
        out = score(a.seed, a.size, a.slot, a.root)
        p = a.out or READS / f"canary-s{a.seed}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=1) + "\n")
    if a.cmd == "score" and a.md:
        p.with_suffix(".md").write_text(md(out))
        print(md(out))
    else:
        print(json.dumps({k: v for k, v in out.items() if k not in ("worlds", "series")}, indent=1, default=str)[:4000])


if __name__ == "__main__":
    main()
