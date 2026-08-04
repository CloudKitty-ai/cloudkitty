"""§8 evaluation sweep: every candidate × the deployment shapes.

Shapes use disjoint seed bands from the evaluate-once ledger (§11):
  i   one-agent    -> kitty-eval --roster mixed       (seeds 100_001+)
  iii full-agent   -> kitty-eval --roster all-policy  (seeds 300_001+)
Shape iii additionally runs the F-010 stability gate on rosters 3 and
5 (family variants supply those worlds; the served world is roster 4).

Evaluate-once: a (run, shape) pair already recorded in the ledger is
skipped, never re-run. Results land beside the ledger.

  python run_eval.py <artifacts-dir> <shape> [--ticks N]
    shape = i | iii | roster3 | roster5
"""
import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
REPO = EXP.parents[1]
KITTY_EVAL = REPO / "target/release/kitty-eval"

SHAPES = {
    #  name        roster flag     seed band start   config
    "i":       ("mixed",      100_001, REPO / "cloudkitty.toml"),
    "iii":     ("all-policy", 300_001, REPO / "cloudkitty.toml"),
    "roster3": ("all-policy", 310_001, EXP / "family/v2-dial1.5/family-00.toml"),
    "roster5": ("all-policy", 320_001, EXP / "family/v2-dial1.5/family-02.toml"),
}


def run_one(entry, shape, n_seeds, ticks, outdir):
    roster, seed0, config = SHAPES[shape]
    seeds = ",".join(str(seed0 + i) for i in range(n_seeds))
    out_json = outdir / f"{entry['run']}--shape-{shape}.json"
    cmd = [str(KITTY_EVAL), "--artifact", entry["artifact"],
           "--config", str(config), "--seeds", seeds, "--ticks", str(ticks),
           "--roster", roster, "--json", str(out_json)]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    agg = [l for l in p.stdout.splitlines() if l.startswith("aggregate delta")]
    fallbacks = sum(int(l.split("fallbacks")[1].strip().rstrip(","))
                    for l in p.stdout.splitlines() if "fallbacks" in l)
    return {
        "run": entry["run"], "shape": shape, "rc": p.returncode,
        "fallbacks_total": fallbacks,
        "aggregate": agg[-1] if agg else "",
        "json": str(out_json),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("artifacts", type=Path)
    ap.add_argument("shape", choices=list(SHAPES))
    ap.add_argument("--ticks", type=int, default=20_000)
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args()

    ledger_path = args.artifacts / "eval-ledger.json"
    ledger = json.loads(ledger_path.read_text())
    done = set(ledger["evaluated"].get(args.shape, []))
    todo = [e for e in ledger["candidates"] if e["run"] not in done]
    if not todo:
        print(f"shape {args.shape}: all {len(ledger['candidates'])} already evaluated")
        return
    outdir = args.artifacts / "eval"
    outdir.mkdir(exist_ok=True)
    print(f"shape {args.shape}: {len(todo)} candidates × {args.seeds} seeds "
          f"× {args.ticks} ticks")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(
            lambda e: run_one(e, args.shape, args.seeds, args.ticks, outdir),
            todo))

    ok = []
    for r in sorted(results, key=lambda r: r["run"]):
        flag = "" if r["rc"] == 0 else f"  rc={r['rc']}"
        fb = "" if r["fallbacks_total"] == 0 else \
             f"  !! FALLBACKS {r['fallbacks_total']}"
        print(f"  {r['run']:22s} {r['aggregate']}{flag}{fb}")
        if r["rc"] == 0:
            ok.append(r["run"])
    ledger["evaluated"][args.shape] = sorted(done | set(ok))
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")
    print(f"shape {args.shape}: {len(ok)}/{len(todo)} evaluated, ledger updated")


if __name__ == "__main__":
    main()
