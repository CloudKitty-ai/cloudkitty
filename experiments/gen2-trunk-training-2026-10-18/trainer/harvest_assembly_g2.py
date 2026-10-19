#!/usr/bin/env python3
"""Rung (i) harvest assembly (MITIGATION.md; deviations entry 2).

Selects the paid-for archive rollouts that enrich the critic's
coverage, dedups by array hash, and writes the extension manifest
with achieved post-harvest coverage against the declared targets.

Selection rule (declared): a deduped archive group joins the harvest
when its below-45 occupancy exceeds the corpus baseline (0.3756%
all-ticks) OR its 45–70 occupancy exceeds the 6% target. full-100 is
the corpus itself, never harvested; pilot-30 enters per class under
the same rule. Happiness numbers are RAW points (state /100 at read).

    harvest_assembly_g2.py [--out ../artifacts/extension-manifest.json]

Run from trainer/, exp-006 venv. Reads archive-inventory.json beside
the artifacts; re-derives per-rollout stats from the raws (the
inventory is group-level); computes per-rollout censored returns
(γ 0.998, min_future 1500) for the span report.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

HERE = Path(__file__).resolve().parent
ARC = HERE.parent
EXP = HERE.parents[1]
sys.path.insert(0, str(HERE))

from train_critic_g2 import critic_arrays  # noqa: E402

BASELINE_B45 = 0.003756          # corpus all-ticks below-45 fraction
TARGET_B45, TARGET_4570 = 0.015, 0.06
TARGET_SPAN = 220.0
HCOLS = [k * 40 + 6 for k in range(5)]
CORPUS_KT = 10_000_000
CORPUS_B45_KT = 37_564
CORPUS_4570_KT = 230_695


def rollout_dirs(group: str):
    """Rollout dirs for an inventory group name (path under experiments/)."""
    g = EXP / group
    if g.is_dir():
        return sorted(d.parent for d in g.glob("**/meta.json")
                      if (d.parent / "state.npy").exists())
    # pilot-30/<class> style: filter by manifest class
    coll_root, cls = g.parent, g.name
    man = json.loads((coll_root / "manifest.json").read_text())
    classes = {r["rollout"]: r["class"] for r in man["rollouts"]}
    return sorted(d / "config-00-rollout-00" for d in coll_root.glob("r*")
                  if classes.get(int(d.name[1:])) == cls
                  and (d / "config-00-rollout-00/state.npy").exists())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=ARC / "artifacts/extension-manifest.json")
    args = ap.parse_args()

    inv = json.loads(
        (ARC / "artifacts/archive-inventory.json").read_text())
    selected = [g for g in inv["groups"]
                if "full-100" not in g["group"]
                and (g["frac_below_45"] > BASELINE_B45
                     or g["frac_45_70"] > TARGET_4570)]

    rows, hashes = [], {}
    for g in selected:
        for d in rollout_dirs(g["group"]):
            state = np.load(d / "state.npy", mmap_mode="r")
            h = np.asarray(state[:, HCOLS], dtype=np.float64)
            digest = hashlib.sha256(np.ascontiguousarray(state)).hexdigest()
            if digest in hashes:
                rows.append({"path": str(d.relative_to(EXP)),
                             "group": g["group"], "duplicate_of":
                             hashes[digest], "included": False})
                continue
            hashes[digest] = str(d.relative_to(EXP))
            r = SimpleNamespace(
                name=d.parent.name,
                state=state,
                reward=np.asarray(np.load(d / "reward.npy"), np.float32))
            _x, y = critic_arrays([r], gamma=0.998, min_future=1500)
            rows.append({
                "path": str(d.relative_to(EXP)), "group": g["group"],
                "included": True, "sha256": digest,
                "ticks": int(state.shape[0]), "kt": int(h.size),
                "b45_kt": int((h < 0.45).sum()),
                "b4570_kt": int(((h >= 0.45) & (h < 0.70)).sum()),
                "return_min": float(y.min()),
                "return_mean": float(y.mean()),
                "censored_states": int(len(y))})

    inc = [r for r in rows if r["included"]]
    kt = sum(r["kt"] for r in inc)
    b45 = sum(r["b45_kt"] for r in inc)
    b4570 = sum(r["b4570_kt"] for r in inc)
    span_min = min(r["return_min"] for r in inc)
    post = {
        "harvest_rollouts": len(inc),
        "harvest_duplicates_excluded": len(rows) - len(inc),
        "harvest_kt": kt, "harvest_b45_kt": b45, "harvest_4570_kt": b4570,
        "harvest_return_min": span_min,
        "postmix_b45": (CORPUS_B45_KT + b45) / (CORPUS_KT + kt),
        "postmix_4570": (CORPUS_4570_KT + b4570) / (CORPUS_KT + kt),
        "targets": {"b45": TARGET_B45, "f4570": TARGET_4570,
                    "span": TARGET_SPAN},
    }
    post["b45_met"] = post["postmix_b45"] >= TARGET_B45
    post["f4570_met"] = post["postmix_4570"] >= TARGET_4570
    post["span_met"] = span_min <= TARGET_SPAN

    out = {"selection_rule":
           f"frac_below_45 > {BASELINE_B45} or frac_45_70 > {TARGET_4570}; "
           "full-100 excluded; dedup by state.npy sha256",
           "coverage": post, "rollouts": rows}
    args.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(post, indent=1))


if __name__ == "__main__":
    main()
