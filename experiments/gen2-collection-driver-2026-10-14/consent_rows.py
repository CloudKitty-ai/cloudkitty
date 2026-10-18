#!/usr/bin/env python3
"""Consent-refused row extraction for the trunk trainer (frozen prereg
S4: the trunk trainer consumes PROPOSED-where-consent-refused, applied
everywhere else — pinned at the freeze with the trainer config).

Only enrichment-class rollouts can refuse (served/traits run consent
base 0, gate off). For each one, a traced deterministic re-run
(bc-collect --trace, same config + world_seed) yields the refusal ring;
rows = the kept corpus rows whose (tick, kitty) carries a
`consent_declined` stamp. Output: one JSON per corpus with, per
rollout, the (tick, kitty, absorbed, row) list — the loader swaps
label -> label_proposed on exactly those rows.

    python3 -B consent_rows.py --corpus results-raw/full-100 \
        --scratch SCRATCH --out results-raw/consent-rows-full-100.json

Guard: test_consent_rows.py. The re-run is byte-deterministic (SC-004 /
the mask-mismatch composition fence precedent); the script asserts the
re-run's decision count equals the corpus meta's.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BC = ROOT / "experiments/tools/bc-collect/target/release/bc-collect"


def refused_pairs(trace_path):
    """(tick, kitty_id, absorbed) for every consent_declined stamp."""
    out = []
    with open(trace_path) as f:
        for line in f:
            d = json.loads(line)
            for e in d["refusals"]:
                if e["reason"] == "consent_declined":
                    out.append((int(e["tick"]), int(e["kitty_id"]),
                                bool(e["absorbed"])))
    return out


def map_rows(rollout_dir, pairs):
    """Kept-row index for each refused (tick, kitty); a pair whose row
    was skipped (mask-mismatch) maps to None and is reported."""
    tick = np.load(rollout_dir / "tick.npy")
    kitty = np.load(rollout_dir / "kitty.npy")
    index = {(int(t), int(k)): i for i, (t, k) in enumerate(zip(tick, kitty))}
    assert len(index) == len(tick), "duplicate (tick, kitty) in corpus"
    kits = set(int(k) for k in np.unique(kitty))
    rows = []
    for t, k, absorbed in pairs:
        assert k in kits, f"refusal kitty {k} not a corpus kitty id {kits}"
        rows.append({"tick": t, "kitty": k, "absorbed": absorbed,
                     "row": index.get((t, k))})
    return rows


def run_one(cfg_path, world_seed, scratch):
    scratch.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [str(BC), "--config", str(cfg_path), "--rollouts", "1",
         "--ticks", "20000", "--seed-base", str(world_seed),
         "--out-dir", str(scratch), "--trace"],
        check=True, capture_output=True)
    (d,) = sorted(scratch.glob("config-00-rollout-*"))
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--scratch", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    man = json.load(open(a.corpus / "manifest.json"))
    enrich = [r for r in man["rollouts"] if r["class"] == "enrichment"]
    assert enrich, "no enrichment rollouts in the manifest"
    result = {"corpus": str(a.corpus), "note":
              "consent_declined stamps from traced deterministic re-runs; "
              "row = kept corpus row (None = skipped by bc-collect)",
              "rollouts": []}
    for r in enrich:
        rdir = a.corpus / f"r{r['rollout']:02d}" / "config-00-rollout-00"
        meta = json.load(open(rdir / "meta.json"))
        cfg = Path(r["config"])        # manifest paths are driver-relative
        if not cfg.is_absolute():
            cfg = HERE / cfg
        assert cfg.exists(), cfg
        scratch = a.scratch / f"r{r['rollout']:02d}"
        tdir = run_one(cfg, meta["world_seed"], scratch)
        re_meta = json.load(open(tdir / "meta.json"))
        assert re_meta["decisions"] == meta["decisions"], \
            (r["rollout"], re_meta["decisions"], meta["decisions"])
        assert re_meta["world_seed"] == meta["world_seed"]
        pairs = refused_pairs(tdir / "trace.jsonl")
        rows = map_rows(rdir, pairs)
        result["rollouts"].append(
            {"rollout": r["rollout"], "world_seed": meta["world_seed"],
             "consent_line": r["consent_line"], "refused": rows})
        mapped = sum(1 for x in rows if x["row"] is not None)
        print(f"r{r['rollout']:02d}: {len(rows)} consent_declined, "
              f"{mapped} mapped to kept rows "
              f"(absorbed {sum(1 for x in rows if x['absorbed'])})")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    json.dump(result, open(a.out, "w"), indent=1)
    tot = sum(len(r["refused"]) for r in result["rollouts"])
    print(f"wrote {a.out}: {len(result['rollouts'])} rollouts, {tot} stamps")


if __name__ == "__main__":
    main()
