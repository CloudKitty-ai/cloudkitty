#!/usr/bin/env python3
"""Phase 1d §Addendum 3 — R6d, the burn-in as an instrument (read-only on the
three NF-h24+p probe runs' saved P(grave)).

The alarm is forced off for the first B ticks of every observer slice (the
saved P(grave) replaced by −1.0 at offsets 0 … B − 1; nothing else changes)
and R4d's `latency` instrument runs unchanged on the masked signal, at every
BURNINS × THRESHOLDS cell, on group P and on L / W / G (the sweep's SETS).
Per cell beside R4d's columns: the blind fraction of observer-ticks; the
mid-world episodes whose onset falls inside the burn-in and their detection;
the false-alarm runs beginning exactly at offset B; all-runs false alarms per
100 detected mid-world episodes. Three identities are asserted before writing
(`pin_sweep`): B = 0 equals the sweep's NF-h24+p cells; onsets at or after B
keep their B = 0 latency; at B = 100 the run count equals the sweep's
runs-after-tick-100 plus the runs beginning at offset 100. Post-read
additions (DECLARATION §Addendum 3): where the mid-world onsets fall (offsets,
the slices they share with a reset episode, grave after tick 100) and the
start-up split (slices whose alarm fires within the first WINDOW ticks, among
slices with a grave tick in that window and among slices without one).
Descriptive — no reading rule; the burn-in length is the owner's.
"""
import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
os.environ.setdefault("MINIFRIEND_ARC", str(HERE))
sys.path.insert(0, str(HERE))
import read_phase1d as P  # noqa: E402
import sweep_threshold as SW  # noqa: E402

BURNINS = (0, 25, 50, 100, 150, 200, 300)
THRESHOLDS = SW.THRESHOLDS
SETS = SW.SETS
HEAD = "NF"                     # decision 2 ruled NF
PICK_T, PICK_B = 0.10, 100      # the two printed cross-sections: burn-in ladder at 0.10; threshold ladder at 100
MASKED = -1.0                   # under every threshold
WINDOW = 100                    # post-read: the start-up window of the split (= PICK_B)


def mask_burnin(idx, signal, burnin):
    """The signal with offsets 0 … burnin − 1 of every slice forced under every threshold."""
    sig = np.array(signal, np.float64, copy=True)
    for _n, _s, _k, _j, a, b in idx["slices"]:
        sig[a:b][np.arange(b - a) < burnin] = MASKED
    return sig


def blind_frac(idx, burnin):
    """Observer-ticks the alarm cannot fire on, as a fraction of all."""
    return float(sum(min(burnin, b - a) for _n, _s, _k, _j, a, b in idx["slices"]) / idx["n"])


def episode_latencies(above, eps):
    """Per episode the first tick at or over the threshold as a latency from onset (None = missed)."""
    out = []
    for st, en, _a in eps:
        hit = np.where(above[st:en])[0]
        out.append(int(hit[0]) if len(hit) else None)
    return out


def boundary_runs(idx, above, burnin):
    """False-alarm runs (no grave tick) beginning exactly at offset `burnin` of their slice."""
    grave = idx["code"] == P.S.GRAVE
    n = 0
    for _n, _s, _k, _j, a, b in idx["slices"]:
        for st, en in P._runs(above[a:b]):
            if st == burnin and not grave[a + st:a + en].any():
                n += 1
    return n


def burnin_row(idx, signal, thresh, burnin, eps):
    """R4d's `latency` on the masked signal plus the burn-in columns; asserts identity 2."""
    masked = mask_burnin(idx, signal, burnin)
    row = P.latency(idx, masked, thresh, eps)
    above_m = masked >= thresh
    above_0 = np.asarray(signal, np.float64) >= thresh
    inside = [e for e in eps if e[0] != e[2] and e[0] - e[2] < burnin]
    after = [e for e in eps if e[0] != e[2] and e[0] - e[2] >= burnin]
    assert episode_latencies(above_m, after) == episode_latencies(above_0, after)   # identity 2: onsets at or after B keep their latency
    row["midworld_onset_in_burnin"] = P.latency(idx, masked, thresh, inside)["all"]
    row["midworld_after_burnin"] = {"episodes": len(after)}
    row["blind_frac"] = blind_frac(idx, burnin)
    row["fa_runs_at_boundary"] = boundary_runs(idx, above_m, burnin)
    det = sum(1 for lat in episode_latencies(above_m, after + inside) if lat is not None)
    fa = row["false_alarms"]["runs"]
    row["derived"] = {"midworld_detected": det, "fa_per_100_midworld_detected": 100.0 * fa / det if det else None}
    return row


def onset_offsets(idx, eps, window=WINDOW):
    """Post-read: where the mid-world onsets fall — offsets from the slice start (n, min, median, max,
    counts at or under 25 / 50 / window), how many share their slice with a reset episode; and per
    slice whether a grave tick falls inside the first `window` ticks, after them, and how many."""
    offs = sorted(st - a for st, _en, a in eps if st != a)
    reset_slices = {a for st, _en, a in eps if st == a}
    grave = idx["code"] == P.S.GRAVE
    sl = idx["slices"]
    return {"midworld_n": len(offs), "min": offs[0] if offs else None, "median": float(np.median(offs)) if offs else None,
            "max": offs[-1] if offs else None, "le_25": sum(o <= 25 for o in offs), "le_50": sum(o <= 50 for o in offs),
            f"le_{window}": sum(o <= window for o in offs),
            "in_slice_with_reset": sum(1 for st, _en, a in eps if st != a and a in reset_slices),
            "slices": len(sl), f"slices_grave_in_{window}": int(sum(grave[a:a + window].any() for *_r, a, b in sl)),
            f"slices_grave_after_{window}": int(sum(grave[a + window:b].any() for *_r, a, b in sl)),
            f"grave_ticks_after_{window}": int(sum(grave[a + window:b].sum() for *_r, a, b in sl))}


def startup_split(idx, signal, thresh, window=WINDOW):
    """Post-read: among slices with a grave tick inside the first `window` ticks and among slices with
    none, the fraction whose alarm fires (any tick at or over the threshold) inside that window."""
    above = np.asarray(signal, np.float64) >= thresh
    grave = idx["code"] == P.S.GRAVE
    g, c = [], []
    for *_r, a, b in idx["slices"]:
        (g if grave[a:a + window].any() else c).append(bool(above[a:a + window].any()))
    return {"window": window, "grave_slices": len(g), "fired_given_grave": sum(g) / len(g) if g else None,
            "clean_slices": len(c), "fired_given_clean": sum(c) / len(c) if c else None}


def grid(idx, ps, burnins=BURNINS, thresholds=THRESHOLDS):
    eps = P.episodes(idx)
    out = {"episodes_total": len(eps), "episodes_reset": sum(st == a for st, _en, a in eps),
           "episodes_midworld": sum(st != a for st, _en, a in eps), "n_ticks": idx["n"],
           "onsets": onset_offsets(idx, eps), "startup": {}, "rows": {}}
    for t in thresholds:
        per = [startup_split(idx, p, t) for p in ps]
        out["startup"][f"{t:.2f}"] = {"per_seed": per, **P.msd_tree(per)}
    for burnin in burnins:
        out["rows"][str(burnin)] = {}
        for t in thresholds:
            per = [burnin_row(idx, p, t, burnin, eps) for p in ps]
            out["rows"][str(burnin)][f"{t:.2f}"] = {"per_seed": per, **P.msd_tree(per)}
    return out


EXTRA = ("midworld_onset_in_burnin", "midworld_after_burnin", "blind_frac", "fa_runs_at_boundary", "derived")


def pin_sweep(grid_rows, n_ticks, path=HERE / "phase1d-sweep.json", set_name="P"):
    """Identities 1 and 3 against the committed sweep (NF-h24+p): every B = 0 cell equals the sweep's
    `latency` cells; at B = 100 the false-alarm run count equals the sweep's runs starting after tick
    100 plus the runs beginning exactly at offset 100."""
    ref = json.loads(path.read_text())["by_set"][set_name]["heads"][f"{HEAD}-h24+p"]["rows"]
    for t, cell in grid_rows.get("0", {}).items():
        got = json.loads(json.dumps(cell["per_seed"], default=float))
        want = json.loads(json.dumps(ref[t]["per_seed"]))
        for g, w in zip(got, want):
            for k in EXTRA:
                g.pop(k)
            for k in ("derived", "nongrave_above_per_10k", "fa_detail"):
                w.pop(k)
            assert g == w, ("B=0 differs from the sweep", set_name, t)
    for t, cell in grid_rows.get("100", {}).items():
        for g, w in zip(cell["per_seed"], ref[t]["per_seed"]):
            late = w["fa_detail"]["late_runs_per_10k"] * n_ticks / 1e4
            assert abs(late - round(late)) < 1e-6
            assert g["false_alarms"]["runs"] == round(late) + g["fa_runs_at_boundary"], ("B=100 runs", set_name, t)


def read_all():
    out = {"burnins": list(BURNINS), "thresholds": list(THRESHOLDS), "sets": SETS, "seeds": list(P.SEEDS),
           "head": f"{HEAD}-h24+p", "runs": P.PROBES[HEAD], "pick": {"threshold": PICK_T, "burnin": PICK_B}, "by_set": {}}
    for sname, sets in SETS.items():
        idx = P.R.eval_index(sets)
        g = grid(idx, [P.load_p(run, idx) for run in P.PROBES[HEAD]])
        pin_sweep(g["rows"], idx["n"], set_name=sname)
        out["by_set"][sname] = {"eval_sets": sets, "n_samples": idx["n"], **g}
    return out


def fmt(m, d=3):
    return P.fmt(m, d)


HEADER = ("| burn-in | P ≥ | blind | mw-sight det | p90 lat | mw-fog det | p90 lat | mw onsets in burn-in | their det | their med lat "
          "| reset det | reset med lat | FA /10k | FA len | FA at boundary | FA per 100 mw det |")
RULE = "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"


def _line(burnin, t, r):
    mv, mf, rs, fa, ib, dv = r["midworld_visible"], r["midworld_fog"], r["reset"], r["false_alarms"], r["midworld_onset_in_burnin"], r["derived"]
    return (f"| {burnin} | {t} | {fmt(r['blind_frac'])} | {fmt(mv['detected_frac'])} | {fmt(mv['p90_latency'], 1)} "
            f"| {fmt(mf['detected_frac'])} | {fmt(mf['p90_latency'], 1)} | {fmt(ib['episodes'], 0)} | {fmt(ib['detected_frac'])} | {fmt(ib['median_latency'], 1)} "
            f"| {fmt(rs['detected_frac'])} | {fmt(rs['median_latency'], 1)} | {fmt(fa['per_10k_ticks'])} | {fmt(fa['run_median_length'], 1)} "
            f"| {fmt(r['fa_runs_at_boundary'], 1)} | {fmt(dv['fa_per_100_midworld_detected'], 1)} |")


def md(out):
    L = [f"# Phase 1d §Addendum 3 — R6d the burn-in, {out['head']} (mean ± SD over seeds 1–3)", ""]
    tp = f"{PICK_T:.2f}"
    for sname, blk in out["by_set"].items():
        L.append(f"## {sname} ({', '.join(blk['eval_sets'])}; {blk['n_samples']:,} observer-ticks): episodes {blk['episodes_total']}, "
                 f"reset {blk['episodes_reset']}, mid-world {blk['episodes_midworld']}")
        o = blk["onsets"]
        L.append(f"mid-world onset offsets: n {o['midworld_n']}, min {o['min']}, median {fmt(o['median'], 1)}, max {o['max']}; "
                 f"at or under 25 / 50 / {WINDOW} ticks: {o['le_25']} / {o['le_50']} / {o[f'le_{WINDOW}']}; "
                 f"in a slice that also has a reset episode: {o['in_slice_with_reset']}. "
                 f"Slices {o['slices']}: with a grave tick in the first {WINDOW} ticks {o[f'slices_grave_in_{WINDOW}']}, "
                 f"with a grave tick after tick {WINDOW} {o[f'slices_grave_after_{WINDOW}']} ({o[f'grave_ticks_after_{WINDOW}']} grave ticks).")
        L.append("")
        L.append(f"### start-up split: slices whose alarm fires within the first {WINDOW} ticks")
        L.append("| P ≥ | slices with grave in window | fired, given grave | slices without | fired, given none |")
        L.append("|---|---|---|---|---|")
        for t, r in blk["startup"].items():
            L.append(f"| {t} | {fmt(r['grave_slices'], 0)} | {fmt(r['fired_given_grave'])} | {fmt(r['clean_slices'], 0)} | {fmt(r['fired_given_clean'])} |")
        L.append("")
        L.append(f"### burn-in ladder at P ≥ {tp}")
        L.extend([HEADER, RULE])
        for b in out["burnins"]:
            L.append(_line(b, tp, blk["rows"][str(b)][tp]))
        L.append("")
        L.append(f"### threshold ladder at burn-in {PICK_B}")
        L.extend([HEADER, RULE])
        for t in out["thresholds"]:
            L.append(_line(PICK_B, f"{t:.2f}", blk["rows"][str(PICK_B)][f"{t:.2f}"]))
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "phase1d-burnin.json")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    out = read_all()
    a.out.write_text(json.dumps(out, indent=1, default=float))
    print(f"wrote {a.out}", file=sys.stderr)
    if a.md:
        print(md(out))


if __name__ == "__main__":
    main()
