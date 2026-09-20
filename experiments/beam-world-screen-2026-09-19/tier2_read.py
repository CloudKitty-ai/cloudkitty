"""Tier 2 reader (PREREG-tier2 §Reads, §Predictions 3-4): per arm, the five swap legs pooled
(the arm's placement and tick share in a served roster), the all-arm roster, the clone leg,
against tier 1's scripted and gen1-A references on the same world; then prediction 3's letter.
Usage: tier2_read.py TIER2_BATTERY_DIR TIER1_BATTERY_DIR [--out JSON]"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import screen_read as S

SLOTS = {"pkg-s1": "s3-b7-t3000-n6", "pkg-s2": "s3-b7-t3000-n6", "floor5-s1": "s5-b7-t3000-n6", "floor5-s2": "s5-b7-t3000-n6"}
KEEP, LOSE = 0.15, 0.10           # prediction 3's lines on pooled swap-leg placement
SCRIPTED_NASH_PACKAGE = None       # filled from tier 1 at read time


def pool(files):
    """Sum the beam block over every row of every file (seat legs pooled), welfare as means."""
    rows = []
    for f in files:
        _h, r = S.load_rows(f); rows += r
    return S.aggregate(rows) if rows else None


def swap_leg_seat(rows, slot):
    """In a swap leg the arm sits in ONE seat; its own numbers are that seat's."""
    return [i for i, s in enumerate(rows[0]["seats"]) if s == f"ppo:{slot}"]


def arm_in_seat(files, slot):
    """The arm's own placement / tick share / happiness pooled over its seat in each swap leg."""
    on = sleep = starts = d0 = n = 0; hap = 0.0
    for f in files:
        _h, rows = S.load_rows(f)
        for r in rows:
            for i in swap_leg_seat(rows, slot):
                b = r["beam"]; on += b["on_beam"][i]; sleep += b["sleep"][i]; starts += b["starts"][i]; d0 += b["start_dist"][i][0]
                hap += r["mean_happiness"][i]; n += 1
    return {"placement": d0 / starts if starts else None, "in_beam": on / sleep if sleep else None, "starts": starts, "sleep": sleep,
            "happiness": hap / n if n else None}


def letter(pkg, floor5):
    """Prediction 3: (a) both under LOSE, (b) package >= KEEP and floor5 < LOSE, (c) both >= KEEP; else 'other'."""
    if any(v is None for v in pkg + floor5):
        return None
    if all(v < LOSE for v in pkg + floor5):
        return "a"
    if all(v >= KEEP for v in pkg) and all(v < LOSE for v in floor5):
        return "b"
    if all(v >= KEEP for v in pkg + floor5):
        return "c"
    return "other"


def read(t2, t1):
    t2, t1 = Path(t2), Path(t1)
    out = {"arms": {}, "reference": {}}
    for slot, variant in SLOTS.items():
        d = t2 / slot
        swaps = sorted(d.glob(f"gen1-A_s?-{slot}-c0-eval-*.jsonl"))
        alls = sorted(p for p in d.glob("gen1-A_s0-*-c0-eval-*.jsonl") if p.name.count(slot) == 5)
        arm = {"world": variant, "swap_legs": len(swaps)}
        if swaps:
            arm["own_seat"] = arm_in_seat(swaps, slot)
            roster = pool(swaps); arm["roster_with_arm"] = {k: roster["pooled"][k] for k in ("in_beam", "happiness", "nash_state", "max_distress_age", "seeds_over_line")}
            arm["roster_with_arm"]["placement"] = roster["pooled"]["start_dist"][0]
        if alls:
            a = pool(alls); arm["all_arm"] = {"placement": a["pooled"]["start_dist"][0], "in_beam": a["pooled"]["in_beam"], "happiness": a["pooled"]["happiness"],
                                              "nash_state": a["pooled"]["nash_state"], "max_distress_age": a["pooled"]["max_distress_age"], "seeds_over_line": a["pooled"]["seeds_over_line"]}
        out["arms"][slot] = arm
    for variant in set(SLOTS.values()):
        ref = {}
        for seating, fn in S.FILES.items():
            f = t1 / variant / fn
            if f.exists():
                _h, rows = S.load_rows(f); a = S.aggregate(rows)
                ref[seating] = {"placement": a["pooled"]["start_dist"][0], "in_beam": a["pooled"]["in_beam"], "nash_state": a["pooled"]["nash_state"], "happiness": a["pooled"]["happiness"]}
        out["reference"][variant] = ref
    clone = sorted((t2 / "clone").glob("*.jsonl")) if (t2 / "clone").exists() else []
    if clone:
        c = pool(clone); out["clone"] = {"placement": c["pooled"]["start_dist"][0], "in_beam": c["pooled"]["in_beam"], "seeds": c["seeds"], "nash_state": c["pooled"]["nash_state"]}
    pkg = [out["arms"][s].get("own_seat", {}).get("placement") for s in ("pkg-s1", "pkg-s2")]
    f5 = [out["arms"][s].get("own_seat", {}).get("placement") for s in ("floor5-s1", "floor5-s2")]
    out["prediction3"] = {"package_placement": pkg, "floor5_placement": f5, "letter": letter(pkg, f5)}
    sn = out["reference"].get("s3-b7-t3000-n6", {}).get("scripted", {}).get("nash_state")
    out["prediction4"] = {"scripted_nash_package": sn,
                          "package_arms_nash": {s: out["arms"][s].get("roster_with_arm", {}).get("nash_state") for s in ("pkg-s1", "pkg-s2")},
                          "over_line": {s: out["arms"][s].get("roster_with_arm", {}).get("seeds_over_line") for s in SLOTS}}
    return out


if __name__ == "__main__":
    res = read(sys.argv[1], sys.argv[2])
    print(json.dumps(res, indent=1, default=str))
    if "--out" in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1, default=str)
