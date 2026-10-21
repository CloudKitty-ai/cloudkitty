"""Read-only sweep of Gen-2 bc-collect rollout dirs -> happiness occupancy + reward inventory.

The generator of artifacts/archive-inventory.json, the measured baseline in
MITIGATION.md (2026-10-18), which harvest_assembly_g2.py reads. It ran from
the session scratchpad (script last saved and artifact written in the same
minute, 2026-10-18 22:05 local) and is committed 2026-10-21 unchanged except
OUT: that was the artifact's own path and is now a required argument, so a
re-run cannot overwrite the cited file. A re-run globs every gen2 raw on disk,
so it also lists groups collected after 2026-10-18.

Usage (exp-006 venv, any cwd): python3 -B archive_inventory.py <out.json>
"""
import glob, json, os, sys
from collections import defaultdict
import numpy as np

EXP = "/Users/elizabethkelly/ai/cloudkitty/experiments"
OUT = sys.argv[1]
HCOLS = [k * 40 + 6 for k in range(5)]  # global_state.rs: per kitty needs 6, happiness at offset 6

manifest_class = {}  # (collection, rollout_index) -> class
for coll in ("full-100", "pilot-30"):
    mp = os.path.join(EXP, "gen2-collection-driver-2026-10-14/results-raw", coll, "manifest.json")
    if os.path.exists(mp):
        for r in json.load(open(mp))["rollouts"]:
            manifest_class[(coll, r["rollout"])] = r["class"]

metas = sorted(glob.glob(os.path.join(EXP, "gen2-*/results-raw*/**/meta.json"), recursive=True))
acc = defaultdict(lambda: dict(n=0, ticks=0, hn=0, b45=0, b4570=0, hmin=np.inf, rn=0, rs=0.0, rss=0.0))
skipped = []

for mp in metas:
    d = os.path.dirname(mp)
    rel = os.path.relpath(d, EXP).split(os.sep)
    if not all(os.path.exists(os.path.join(d, f)) for f in ("state.npy", "reward.npy")):
        continue  # not a rollout dir
    try:
        meta = json.load(open(mp))
    except Exception as e:
        skipped.append({"path": "/".join(rel), "reason": f"meta.json unreadable: {e}"}); continue
    sch, w = meta.get("observation_schema"), meta.get("state_width")
    if sch != 6 or w != 237:
        skipped.append({"path": "/".join(rel), "reason": f"observation_schema={sch} state_width={w}"}); continue
    mid = rel[:-1]  # drop config-XX-rollout-NN
    if len(mid) >= 3 and mid[2] in ("full-100", "pilot-30"):
        coll = mid[2]
        ridx = int(mid[3][1:])
        group = "/".join(mid[:3]) + "/" + manifest_class.get((coll, ridx), "unclassified")
    else:
        group = "/".join(mid[:4])
    try:
        s = np.load(os.path.join(d, "state.npy"), mmap_mode="r")
        r = np.load(os.path.join(d, "reward.npy"), mmap_mode="r")
        assert s.ndim == 2 and s.shape[1] == 237, f"state shape {s.shape}"
        h = np.asarray(s[:, HCOLS], dtype=np.float64)
        assert np.all(h > 0) and np.all(h <= 1), f"happiness out of (0,1]: min={h.min()} max={h.max()}"
        rr = np.asarray(r, dtype=np.float64).ravel()
    except Exception as e:
        skipped.append({"path": "/".join(rel), "reason": f"unreadable/assert: {e}"}); continue
    for g in (group, "gen2-collection-driver-2026-10-14/results-raw/full-100/ALL") if "/full-100/" in group else (group,):
        a = acc[g]
        a["n"] += 1; a["ticks"] += s.shape[0]; a["hn"] += h.size
        a["b45"] += int((h < 0.45).sum()); a["b4570"] += int(((h >= 0.45) & (h < 0.70)).sum())
        a["hmin"] = min(a["hmin"], float(h.min()))
        a["rn"] += rr.size; a["rs"] += rr.sum(); a["rss"] += (rr * rr).sum()
    print(group, s.shape[0], file=sys.stderr)

groups = []
for g, a in acc.items():
    rm = a["rs"] / a["rn"]
    groups.append({"group": g, "n_rollouts": a["n"], "total_ticks": a["ticks"],
                   "frac_below_45": a["b45"] / a["hn"], "frac_45_70": a["b4570"] / a["hn"],
                   "min_happiness": a["hmin"], "reward_mean": rm,
                   "reward_std": float(np.sqrt(max(a["rss"] / a["rn"] - rm * rm, 0.0)))})
groups.sort(key=lambda x: -x["frac_below_45"])
json.dump({"groups": groups, "skipped": skipped}, open(OUT, "w"), indent=1)
print(f"{'group':75s} {'n':>4s} {'ticks':>9s} {'<45':>8s} {'45-70':>8s} {'hmin':>7s} {'rmean':>9s} {'rstd':>8s}")
for x in groups:
    print(f"{x['group']:75s} {x['n_rollouts']:4d} {x['total_ticks']:9d} {x['frac_below_45']:8.5f} {x['frac_45_70']:8.5f} "
          f"{x['min_happiness']:7.4f} {x['reward_mean']:9.4f} {x['reward_std']:8.4f}")
print("skipped:", len(skipped))
for x in skipped: print(" ", x)
