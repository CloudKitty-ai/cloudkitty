#!/usr/bin/env python3
"""Gen 2 corpus-collection driver with pencil-share starts (skeleton
§4, RULED shelf 2026-09-15 + the declared loop resolution): corner/edge
randomized starts at collection, pencil shares 25% edge ring / 5%
corner (corners inside the edge count, as coverage_read counts them);
the coverage instrument then reads the collected corpus and the FINAL
shares are pinned at the freeze.

The engine takes only explicit [[kitty]] x/y starts (config/mod.rs,
unique in-bounds tiles), so the driver derives ONE config per rollout
with sampled starts and runs bc-collect per config with
--seed-base (base + r*1000) --rollouts 1, reproducing bc-collect's own
seed rule (seed_base + ci*1000 + r) independent of any job split.
Derived configs and the draw manifest live INSIDE the out dir, so
meta.json config paths survive (the m1/nokey lesson: a trace whose
config vanished needs config= forever).

Start sampling, per kitty i.i.d. with a seeded RNG: corner with
p = corner_share, non-corner edge with p = edge_share - corner_share,
interior otherwise; uniform tile within the category; collision
redraws (engine validation refuses shared tiles). Realized shares are
reported and recorded — the pencil shares are sampling probabilities,
not quotas.

DO NOT LAUNCH before: Product's stuck detector 061 lands, bc-collect
carries label_proposed (Product, in progress), and the Gen 2 world
toml exists (§2 diff). The driver refuses nothing of this — the gate
is procedural, in the skeleton's §10.2 order.

    experiments/exp-006-character-gen/.venv/bin/python \\
        experiments/gen2-collection-driver-2026-10-14/collect_corpus.py \\
        --base-config GEN2.toml --out-dir OUT [--rollouts 30]
        [--ticks 20000] [--seed-base S] [--draw-seed D]
        [--edge-share 0.25] [--corner-share 0.05] [--trace]
        [--jobs 3] [--dry-run]

Guard: test_collect_corpus.py.
"""
import argparse
import json
import re
import subprocess
import sys
import tomllib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BC = REPO / "experiments/tools/bc-collect/target/release/bc-collect"


def category(x, y, w, h):
    """coverage_read's geometry: edge ring = outermost tile ring,
    corner = both axes at an edge (a corner is also edge)."""
    on_x, on_y = x in (0, w - 1), y in (0, h - 1)
    if on_x and on_y:
        return "corner"
    if on_x or on_y:
        return "edge"
    return "interior"


def draw_tile(rng, cat, w, h):
    if cat == "corner":
        return (int(rng.integers(2)) * (w - 1), int(rng.integers(2)) * (h - 1))
    if cat == "edge":
        while True:
            if rng.integers(2) == 0:                      # horizontal edges
                x, y = int(rng.integers(1, w - 1)), int(rng.integers(2)) * (h - 1)
            else:                                         # vertical edges
                x, y = int(rng.integers(2)) * (w - 1), int(rng.integers(1, h - 1))
            return (x, y)
    return (int(rng.integers(1, w - 1)), int(rng.integers(1, h - 1)))


def sample_starts(rng, roster, w, h, edge_share, corner_share):
    """roster distinct tiles; i.i.d. category per kitty, collision
    redraws keep the draw inside its category."""
    assert 0 <= corner_share <= edge_share <= 1, (edge_share, corner_share)
    starts, cats = [], []
    for _ in range(roster):
        u = float(rng.random())
        cat = ("corner" if u < corner_share
               else "edge" if u < edge_share
               else "interior")
        for _attempt in range(1000):
            t = draw_tile(rng, cat, w, h)
            if t not in starts:
                break
        else:
            raise SystemExit(f"collect_corpus: no free {cat} tile after 1000 draws "
                             f"(world {w}x{h}, roster {roster})")
        starts.append(t)
        cats.append(cat)
    return starts, cats


def patch_starts(base_text, starts):
    """The base toml with each [[kitty]] block's x/y replaced in file
    order. Only x and y move; everything else ships byte-identical."""
    blocks = [m.start() for m in re.finditer(r"(?m)^\[\[kitty\]\]", base_text)]
    if len(blocks) != len(starts):
        raise SystemExit(f"collect_corpus: base config has {len(blocks)} [[kitty]] "
                         f"blocks, {len(starts)} starts drawn")
    out, prev = [], 0
    for b, (x, y) in zip(blocks, starts):
        end = base_text.find("[[kitty]]", b + 1)
        end = len(base_text) if end == -1 else end
        seg = base_text[prev:b] + re.sub(
            r"(?m)^y *=.*$", f"y = {y}",
            re.sub(r"(?m)^x *=.*$", f"x = {x}", base_text[b:end], count=1),
            count=1)
        out.append(seg)
        prev = end
    out.append(base_text[prev:])
    return "".join(out)


def bc_cmd(config, seed_base, ticks, out_dir, trace):
    cmd = [str(BC), "--config", str(config), "--rollouts", "1",
           "--ticks", str(ticks), "--seed-base", str(seed_base),
           "--out-dir", str(out_dir)]
    if trace:
        cmd.insert(-2, "--trace")
    return cmd


def prepare(a):
    """Derived configs + manifest, before anything runs."""
    base_text = Path(a.base_config).read_text()
    cfg = tomllib.loads(base_text)
    w, h = cfg["world"]["width"], cfg["world"]["height"]
    roster = len(cfg["kitty"])
    rng = np.random.default_rng(a.draw_seed)
    out = Path(a.out_dir)
    (out / "configs").mkdir(parents=True, exist_ok=True)
    rollouts, n_cat = [], {"corner": 0, "edge": 0, "interior": 0}
    for r in range(a.rollouts):
        starts, cats = sample_starts(rng, roster, w, h, a.edge_share, a.corner_share)
        for c in cats:
            n_cat[c] += 1
        cfg_path = out / "configs" / f"rollout-{r:02}.toml"
        cfg_path.write_text(patch_starts(base_text, starts))
        rollouts.append({"rollout": r, "config": str(cfg_path),
                         "seed_base": a.seed_base + r * 1000,
                         "starts": starts, "categories": cats})
    n = a.rollouts * roster
    manifest = {
        "base_config": str(a.base_config), "world": [w, h], "roster": roster,
        "pencil_shares": {"edge_ring": a.edge_share, "corner": a.corner_share},
        "realized_shares": {
            "edge_ring": (n_cat["edge"] + n_cat["corner"]) / n,
            "corner": n_cat["corner"] / n},
        "draw_seed": a.draw_seed, "ticks": a.ticks, "trace": a.trace,
        "sampling": "i.i.d. per kitty; shares are probabilities, not quotas",
        "rollouts": rollouts,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-config", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--rollouts", type=int, default=30)
    ap.add_argument("--ticks", type=int, default=20_000)
    ap.add_argument("--seed-base", type=int, default=910_001)
    ap.add_argument("--draw-seed", type=int, default=20261014)
    ap.add_argument("--edge-share", type=float, default=0.25)
    ap.add_argument("--corner-share", type=float, default=0.05)
    ap.add_argument("--trace", action="store_true")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    manifest = prepare(a)
    rs = manifest["realized_shares"]
    print(f"prepared {a.rollouts} rollout configs (realized edge "
          f"{rs['edge_ring']:.3f} corner {rs['corner']:.3f}; pencil "
          f"{a.edge_share}/{a.corner_share}); manifest at {a.out_dir}/manifest.json")
    cmds = [bc_cmd(r["config"], r["seed_base"], a.ticks,
                   Path(a.out_dir) / f"r{r['rollout']:02}", a.trace)
            for r in manifest["rollouts"]]
    if a.dry_run:
        for c in cmds:
            print(" ".join(c))
        return
    if not BC.exists():
        raise SystemExit(f"collect_corpus: {BC} not built")

    def run(c):
        return subprocess.run(c, capture_output=True, text=True)

    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for c, r in zip(cmds, ex.map(run, cmds)):
            if r.returncode != 0:
                raise SystemExit(f"collect_corpus: {' '.join(c)} exited "
                                 f"{r.returncode}\n{r.stderr[-2000:]}")
            print(r.stdout.strip().splitlines()[-1], flush=True)
    print("== collection done; read it with coverage_read and placement_read")


if __name__ == "__main__":
    main()
