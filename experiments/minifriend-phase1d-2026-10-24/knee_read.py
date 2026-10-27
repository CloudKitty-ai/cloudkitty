#!/usr/bin/env python3
"""Phase 1d §Addendum 5 — R8d, the knee: the §Addendum 4 splice unchanged at
H ∈ {1, 2, 5, 10, 20, 50} clean ticks of history (DECLARATION §Addendum 5).

`history_read.splice_rows_nf` / `splice_rows_sd` on the same 200 covered
reset-grave donors and 60 clean L recipients, NF-h24+p seeds 1–3 and SD width
16 seeds 1–3, every table at 0.10 / 0.30 / 0.50, the junction control beside.
Guard of construction: H = 100 is re-run and must equal the committed
`phase1d-history.json` rows exactly before any new H is read. The knee: the
smallest H at which the seed-mean detected fraction at 0.10 is at or under
the midpoint between the committed H = 0 reset detection and the committed
plateau (mean of H = 500 and 2,000). The Professor's P9 scored as declared.

    knee_read.py --out phase1d-knee.json --md > phase1d-knee.md
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import history_read as HR  # noqa: E402
import read_phase1d as P  # noqa: E402

KNEE_H = (1, 2, 5, 10, 20, 50)
PIN_H = 100
PLATEAU_H = ("500", "2000")
THRESH = "0.10"
P9 = {"H_low": "10", "det_max": 0.70, "H_near": "20", "H_ref": "100"}
EXPECT = {"control_fire_max": 0.05, "from_H": 5}
COMMITTED = HERE / "phase1d-history.json"


def knee_of(det_by_H, top, plateau):
    """The smallest H (ascending) whose detected fraction is AT OR UNDER the midpoint of top and
    plateau; None if none is. det_by_H: {H (int): seed-mean detected fraction}."""
    mid = (top + plateau) / 2.0
    for H in sorted(det_by_H):
        if det_by_H[H] <= mid:
            return {"H": H, "midpoint": mid, "detected": det_by_H[H]}
    return {"H": None, "midpoint": mid, "detected": None}


def score_p9(rows, committed, thresh=THRESH):
    """P9 as declared: (i) seed-mean detected at H = 10 < 0.70; (ii) |seed-mean at H = 20 − committed
    H = 100 mean| ≤ committed H = 100 seed SD. rows / committed: {H: {thresh: {"all": {"detected_frac":
    {"mean", "sd"}}}}} (the msd tree)."""
    d10 = rows[P9["H_low"]][thresh]["all"]["detected_frac"]["mean"]
    d20 = rows[P9["H_near"]][thresh]["all"]["detected_frac"]["mean"]
    ref = committed[P9["H_ref"]][thresh]["all"]["detected_frac"]
    i_ok = bool(d10 < P9["det_max"])
    ii_ok = bool(abs(d20 - ref["mean"]) <= ref["sd"])
    return {"threshold": thresh, "det_H10": d10, "bar_H10": P9["det_max"], "i_ok": i_ok,
            "det_H20": d20, "ref_H100_mean": ref["mean"], "ref_H100_sd": ref["sd"], "abs_delta": abs(d20 - ref["mean"]),
            "ii_ok": ii_ok, "met": i_ok and ii_ok}


def pin_H100(new_per_seed, committed_per_seed, head):
    """Per seed and threshold: the re-run H = 100 detected fraction and median latency equal the committed."""
    for si, (new, old) in enumerate(zip(new_per_seed, committed_per_seed)):
        for t in (f"{x:.2f}" for x in HR.THRESHOLDS):
            for key in ("detected_frac", "median_latency"):
                a, b = new[t]["all"][key], old[t]["all"][key]
                assert a == b or (a is None and b is None) or abs(a - b) < 1e-9, (head, si, t, key, a, b)


def msd_rows(per_seed_by_H):
    return {str(H): {"per_seed": v, **P.msd_tree(v)} for H, v in per_seed_by_H.items()}


def read_all(seeds=HR.SEEDS):
    committed = json.loads(COMMITTED.read_text())
    idx_p = P.R.eval_index(HR.C.GROUPS["P"])
    idx_l = P.R.eval_index([HR.L_SET])
    donors = HR.donor_list(idx_p)
    recips = HR.recipient_list(idx_l)
    assert len(donors) == committed["splice"]["donors"] and len(recips) == committed["splice"]["recipients"], \
        (len(donors), len(recips))
    out = {"histories": list(KNEE_H), "pin_H": PIN_H, "thresholds": list(HR.THRESHOLDS), "seeds": list(seeds),
           "committed_sha_note": "phase1d-history.json as committed beside this reader",
           "splice": {"donors": len(donors), "recipients": len(recips)}, "reproduces": {}}
    Hs = (PIN_H,) + KNEE_H
    nf = {H: [] for H in Hs}
    for si, seed in enumerate(seeds):
        model, probe = HR.load_probe(seed)
        out["reproduces"][str(seed)] = HR.check_reproduces(model, probe, seed, idx_p)
        nf[PIN_H].append(HR.splice_rows_nf(model, probe, donors, recips, PIN_H))
        pin_H100(nf[PIN_H][-1:], committed["splice"]["NF-h24+p"][str(PIN_H)]["per_seed"][si:si + 1], "NF-h24+p")
        for H in KNEE_H:
            nf[H].append(HR.splice_rows_nf(model, probe, donors, recips, H))
    sd = {H: [] for H in Hs}
    for ri, run in enumerate(HR.SD_RUNS):
        sd_model = HR.load_sd(run)
        sd[PIN_H].append(HR.splice_rows_sd(sd_model, donors, recips, PIN_H))
        pin_H100(sd[PIN_H][-1:], committed["splice"]["SD-w16"][str(PIN_H)]["per_seed"][ri:ri + 1], "SD-w16")
        for H in KNEE_H:
            sd[H].append(HR.splice_rows_sd(sd_model, donors, recips, H))
    out["splice"]["NF-h24+p"] = msd_rows(nf)
    out["splice"]["SD-w16"] = msd_rows(sd)
    out["committed"] = {head: {H: committed["splice"][head][H] for H in ("0", "0r", "100", "500", "2000")}
                        for head in ("NF-h24+p", "SD-w16")}
    out["knee"] = {}
    for head in ("NF-h24+p", "SD-w16"):
        c = out["committed"][head]
        top = c["0"][THRESH]["reset"]["detected_frac"]["mean"]
        plateau = float(np.mean([c[H][THRESH]["all"]["detected_frac"]["mean"] for H in PLATEAU_H]))
        det = {H: out["splice"][head][str(H)][THRESH]["all"]["detected_frac"]["mean"] for H in Hs}
        ctl = {H: out["splice"][head][str(H)][THRESH]["control_fired"]["mean"] for H in Hs}
        quiet = [H for H in sorted(ctl) if ctl[H] < EXPECT["control_fire_max"]]
        out["knee"][head] = {"top_H0_reset": top, "plateau_500_2000": plateau, **knee_of(det, top, plateau),
                             "detected_by_H": {str(H): det[H] for H in Hs}, "control_by_H": {str(H): ctl[H] for H in Hs},
                             "control_quiet_from_H": quiet[0] if quiet else None}
    out["p9"] = score_p9(out["splice"]["NF-h24+p"], out["committed"]["NF-h24+p"])
    ctl = out["knee"]["NF-h24+p"]["control_by_H"]
    out["expectations"] = {"control_fired_at_0.10_from_H5": {
        "per_H": {H: v for H, v in ctl.items() if int(H) >= EXPECT["from_H"]}, "max": EXPECT["control_fire_max"],
        "holds": all(v < EXPECT["control_fire_max"] for H, v in ctl.items() if int(H) >= EXPECT["from_H"])}}
    return out


def fmt(m, d=3):
    return P.fmt(m, d)


def md(out):
    L = ["# Phase 1d §Addendum 5 — R8d the knee (the §Addendum 4 splice at H ∈ {1, 2, 5, 10, 20, 50}; NF-h24+p seeds 1–3, SD width 16 seeds 1–3; mean ± SD)", ""]
    L.append("reproduces the committed P(grave) on the first P evaluation world to: " + ", ".join(f"s{s} {v:.1e}" for s, v in out["reproduces"].items()))
    L.append(f"H = {out['pin_H']} re-run and equal to the committed rows per seed and threshold (asserted); {out['splice']['donors']} donors, {out['splice']['recipients']} recipients")
    for head in ("NF-h24+p", "SD-w16"):
        L.append(f"\n## {head}")
        L.append("| H | P ≥ | episodes | detected | median lat | p90 lat | within 10 | in-sight det | fog det | FA in history /10k | control fired |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|")
        rows = out["splice"][head]
        for H in [str(h) for h in out["histories"]] + [str(out["pin_H"])]:
            for t in (f"{x:.2f}" for x in out["thresholds"]):
                r = rows[H][t]
                a = r["all"]
                L.append(f"| {H}{' (pin)' if H == str(out['pin_H']) else ''} | {t} | {fmt(a['episodes'], 0)} | {fmt(a['detected_frac'])} | {fmt(a['median_latency'], 1)} | {fmt(a['p90_latency'], 1)} | {fmt(a['within_10_frac'])} "
                         f"| {fmt(r['midworld_visible']['detected_frac'])} | {fmt(r['midworld_fog']['detected_frac'])} | {fmt(r['false_alarms']['per_10k_ticks'])} | {fmt(r['control_fired'])} |")
        c = out["committed"][head]
        L.append("committed §Addendum 4 rows at 0.10, detected: " + ", ".join(
            f"H={H} {fmt(c[H]['0.10']['reset' if H == '0' else 'all']['detected_frac'])}" for H in ("0", "0r", "100", "500", "2000")))
        k = out["knee"][head]
        L.append(f"knee at 0.10: top (H = 0 reset) {fmt(k['top_H0_reset'])}, plateau (500 / 2,000) {fmt(k['plateau_500_2000'])}, midpoint {fmt(k['midpoint'])} → "
                 f"first H at or under it: {k['H']} (detected {fmt(k['detected'])}); control under {EXPECT['control_fire_max']} from H = {k['control_quiet_from_H']}")
    p = out["p9"]
    L.append(f"\nP9 (NF-h24+p at {p['threshold']}): (i) detected at H = 10 {fmt(p['det_H10'])} < {p['bar_H10']} → {p['i_ok']}; "
             f"(ii) detected at H = 20 {fmt(p['det_H20'])} vs committed H = 100 {fmt(p['ref_H100_mean'])} ± {fmt(p['ref_H100_sd'])}, |Δ| {fmt(p['abs_delta'])} → {p['ii_ok']}; met: {p['met']}")
    e = out["expectations"]["control_fired_at_0.10_from_H5"]
    L.append("\n## expectation (this thread's, not a scored prediction)")
    L.append("junction control fired at 0.10 for H ≥ 5: " + ", ".join(f"H={H} {fmt(v)}" for H, v in e["per_H"].items()) + f" (bar < {e['max']}) → holds {e['holds']}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "phase1d-knee.json")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--threads", type=int, default=3)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    out = read_all()
    a.out.write_text(json.dumps(out, indent=1, default=float))
    print(f"wrote {a.out}", file=sys.stderr)
    if a.md:
        print(md(out))


if __name__ == "__main__":
    main()
