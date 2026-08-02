"""Slimmed post-024 training-world search (F-013 follow-up).

Served-world-centered candidate slate, probe + welfare gate per
search.py's registered methodology (cluster-robust channel_metrics,
absolute S(gamma), needs_driven welfare floor 0.78). Policy seats in
cloudkitty.toml are neutralized to needs_driven EXPLICITLY (the probe's
registry would fall back to needs_driven anyway, provenance-marked, but
the candidate configs should say what they run).

Usage: search_post024.py [seed_start]  (7001/8001/9001 = 100-world
rounds; the 150-world finalist runs set SEED_START/SEEDS in-process
-- see results/world-search-2026-08-02-post024.md)
"""
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "experiments/tools/world-search"))
import search  # noqa: E402

search.GAMMAS = (0.995, 0.998, 0.9985, 1.0)

WS = REPO / "experiments/exp-001-bc-mappo/raw/world-search-post024"
WS.mkdir(exist_ok=True)
FAMILY_GEN = REPO / "experiments/tools/family-gen/target/release/family-gen"
TWIN_PROBE = REPO / "experiments/tools/twin-probe/target/release/twin-probe"
KITTY_EVAL = REPO / "target/release/kitty-eval"
SEED_START = int(sys.argv[1]) if len(sys.argv) > 1 else 7001
SEEDS = ",".join(str(s) for s in range(SEED_START, SEED_START + 100))

NEUTRAL = ["kitty.0.behavior=needs_driven", "kitty.3.behavior=needs_driven"]
SCARCITY_1 = ["elements.water.min=3", "elements.water.max=4",
              "elements.chow.min=3", "elements.chow.max=4",
              "elements.sunbeam.min=2", "elements.sunbeam.max=2"]
SCARCITY_MID = ["elements.water.min=5", "elements.water.max=6",
                "elements.chow.min=5", "elements.chow.max=6",
                "elements.sunbeam.min=3", "elements.sunbeam.max=4"]


def rates(mult):
    base = {"eat": 0.4, "drink": 0.4, "sleep": 0.3, "play": 0.4,
            "cuddle": 0.4, "bath": 0.2}
    return [f"needs.{k}={v * mult}" for k, v in base.items()]


def roster5_base():
    """cloudkitty.toml + Clementine (needs_driven, cuddly, free tile)."""
    text = (REPO / "cloudkitty.toml").read_text()
    block = ('[[kitty]]\nid = 5\nname = "Clementine"\nx = 12\ny = 12\n'
             'behavior = "needs_driven"\n[kitty.needs]\ncuddle = 0.7\n\n')
    out = text.replace("\n[needs]\n", "\n" + block + "[needs]\n", 1)
    assert out != text, "insertion anchor [needs] not found"
    p = WS / "base-roster5.toml"
    p.write_text(out)
    return p


def roster3_base():
    """cloudkitty.toml minus Kittybear (id 4, the last [[kitty]] block)."""
    lines = (REPO / "cloudkitty.toml").read_text().splitlines(keepends=True)
    starts = [i for i, l in enumerate(lines) if l.strip() == "[[kitty]]"]
    kb = next(i for i in starts if any("Kittybear" in l for l in lines[i:i + 6]))
    end = next(i for i in range(kb + 1, len(lines))
               if re.match(r"\[(?!\[)(?!kitty\.)", lines[i].strip()))
    p = WS / "base-roster3.toml"
    p.write_text("".join(lines[:kb] + lines[end:]))
    return p


CANDIDATES = {
    "served":     (REPO / "cloudkitty.toml", NEUTRAL),
    "scarce1":    (REPO / "cloudkitty.toml", NEUTRAL + SCARCITY_1),
    "scarce-mid": (REPO / "cloudkitty.toml", NEUTRAL + SCARCITY_MID),
    "tempo125":   (REPO / "cloudkitty.toml", NEUTRAL + rates(1.25)),
    "size22":     (REPO / "cloudkitty.toml", NEUTRAL + ["world.width=22", "world.height=22"]),
    "size26":     (REPO / "cloudkitty.toml", NEUTRAL + ["world.width=26", "world.height=26"]),
    "roster5":    (roster5_base, NEUTRAL),
    "roster3":    (roster3_base, ["kitty.0.behavior=needs_driven"]),
    "gym":        (REPO / "training.toml", ["world.seed=1"]),  # incumbent control
}


def build(name, base, patches):
    base_path = base() if callable(base) else base
    cfg = WS / f"{name}.toml"
    cmd = [FAMILY_GEN, "--base", base_path, "--out", cfg]
    for p in patches:
        cmd += ["--set", p]
    subprocess.run([str(c) for c in cmd], check=True, capture_output=True)
    return cfg


def probe(name, cfg):
    out = WS / f"{name}.w{SEED_START}.jsonl"
    r = subprocess.run(
        [str(TWIN_PROBE), "--config", str(cfg), "--samples", "1000",
         "--trace-len", "1200", "--seeds", SEEDS, "--probe-seed", "42",
         "--quiet", "--out", str(out)],
        check=True, capture_output=True, text=True)
    dpd = json.loads(r.stdout)["decision_point_density"]
    return out, dpd


def welfare(name, cfg):
    out = WS / f"{name}.eval.json"
    subprocess.run(
        [str(KITTY_EVAL), "--brain", "needs_driven", "--config", str(cfg),
         "--seeds", "1,2,3", "--ticks", "20000", "--json", str(out)],
        check=True, capture_output=True)
    return search.welfare_metrics(out)


def analyze(jsonl):
    recs = [json.loads(l) for l in open(jsonl)]
    seeds = [r["world_seed"] for r in recs]
    return search.channel_metrics([r["dr"] for r in recs], seeds)


def one(name):
    base, patches = CANDIDATES[name]
    cfg = build(name, base, patches)
    (jsonl, dpd) = probe(name, cfg)
    w = welfare(name, cfg)
    dr = analyze(jsonl)
    row = {"name": name, "seed_start": SEED_START, "dpd": round(dpd, 3),
           "dr": dr, "welfare": w}
    print(json.dumps(row))
    return row


def main():
    names = list(CANDIDATES)
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(one, names))
    (WS / f"rows.w{SEED_START}.json").write_text(json.dumps(rows, indent=1))
    print(f"\n{'candidate':<12} {'S.998':>8} {'S.9985':>8} {'sig':>4} "
          f"{'peak@k':>10} {'bands':<30} {'dpd':>5} {'welf-min':>8} pass")
    for r in sorted(rows, key=lambda r: -r["dr"].get("S_0.998", 0)):
        m, w = r["dr"], r["welfare"]
        if m.get("significant_ticks", 0) == 0:
            print(f"{r['name']:<12} {'--':>8}")
            continue
        bands = ",".join(f"{a}-{b}" for a, b in m.get("bands", [])[:4])
        print(f"{r['name']:<12} {m['S_0.998']:>8.4f} {m['S_0.9985']:>8.4f} "
              f"{m['significant_ticks']:>4} "
              f"{m['peak_amp']:.2g}@{m['peak_k']:>4} {bands:<30} "
              f"{r['dpd']:>5} {w['team_welfare_min']:>8.3f} {w['bounds_pass']}")


if __name__ == "__main__":
    main()
