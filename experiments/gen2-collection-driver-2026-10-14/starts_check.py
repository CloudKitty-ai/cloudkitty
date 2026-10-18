#!/usr/bin/env python3
"""Position-level starts check (banked at the 062 merge; owner "Starts
check first", 2026-10-18). Two independent legs:

A. ENGINE LAW: a pure-Python port of draw-law v1
   (specs/062-randomized-starts/contracts/draw-law-v1.md — ChaCha8Rng
   sub-stream "ck-starts-v1", two u64 draws per drawn kitty in id
   order, category by share thresholds, canonical-order free list,
   v2 mod len) validated BYTE-EXACT against the engine-emitted golden
   vectors (contracts/golden-draws.json: raw u64 sequences AND final
   positions), then against any knob-on bc-collect meta's starts echo
   (--meta, repeatable; seed = the meta's world_seed, shares/roster
   from --config).

B. DRIVER DRAW: re-derive collect_corpus.py's sampled starts from a
   pilot manifest's draw_seed and compare against (1) the manifest's
   recorded starts/categories and (2) the explicit x/y actually
   written into every rollout config. Guards manifest/config
   integrity for driver-drawn corpora.

    python3 -B starts_check.py --golden ../../specs/062-randomized-starts/contracts/golden-draws.json
    python3 -B starts_check.py --meta M.json --config C.toml   # leg A, engine echo
    python3 -B starts_check.py --manifest results-raw/pilot-30/manifest.json  # leg B

Exit nonzero on any mismatch, naming it. Guard: test_starts_check.py.
"""
import argparse
import json
import sys
import tomllib
from pathlib import Path

MASK32 = 0xFFFFFFFF


def _quarter(s, a, b, c, d):
    s[a] = (s[a] + s[b]) & MASK32
    s[d] = ((s[d] ^ s[a]) << 16 | (s[d] ^ s[a]) >> 16) & MASK32
    s[c] = (s[c] + s[d]) & MASK32
    s[b] = ((s[b] ^ s[c]) << 12 | (s[b] ^ s[c]) >> 20) & MASK32
    s[a] = (s[a] + s[b]) & MASK32
    s[d] = ((s[d] ^ s[a]) << 8 | (s[d] ^ s[a]) >> 24) & MASK32
    s[c] = (s[c] + s[d]) & MASK32
    s[b] = ((s[b] ^ s[c]) << 7 | (s[b] ^ s[c]) >> 25) & MASK32


class ChaCha8:
    """ChaCha8, djb variant as rand_chacha 0.3 runs it: 32-byte key,
    64-bit block counter (words 12-13) from 0, 64-bit stream (words
    14-15) = 0; u32s stream out block by block, little-endian; a u64 is
    two consecutive u32s, first = low half."""

    def __init__(self, seed32: bytes):
        assert len(seed32) == 32
        self.key = [int.from_bytes(seed32[i:i + 4], "little") for i in range(0, 32, 4)]
        self.counter = 0
        self.buf = []

    def _block(self, ctr):
        const = [0x61707865, 0x3320646E, 0x79622D32, 0x6B206574]
        start = const + self.key + [ctr & MASK32, (ctr >> 32) & MASK32, 0, 0]
        s = list(start)
        for _ in range(4):  # 8 rounds = 4 double rounds
            _quarter(s, 0, 4, 8, 12)
            _quarter(s, 1, 5, 9, 13)
            _quarter(s, 2, 6, 10, 14)
            _quarter(s, 3, 7, 11, 15)
            _quarter(s, 0, 5, 10, 15)
            _quarter(s, 1, 6, 11, 12)
            _quarter(s, 2, 7, 8, 13)
            _quarter(s, 3, 4, 9, 14)
        return [(x + y) & MASK32 for x, y in zip(s, start)]

    def next_u32(self):
        if not self.buf:
            self.buf = self._block(self.counter)
            self.counter += 1
        return self.buf.pop(0)

    def next_u64(self):
        lo = self.next_u32()
        hi = self.next_u32()
        return (hi << 32) | lo


def law_rng(world_seed: int) -> ChaCha8:
    seed = world_seed.to_bytes(8, "little") + b"ck-starts-v1" + bytes(12)
    return ChaCha8(seed)


def categories(w, h):
    corner, edge, interior = [], [], []
    for y in range(h):          # canonical order: y outer, x inner
        for x in range(w):
            ox = x == 0 or x == w - 1
            oy = y == 0 or y == h - 1
            (corner if ox and oy else edge if ox or oy else interior).append((x, y))
    return {"corner": corner, "edge_ring": edge, "interior": interior}


def engine_draw(world_seed, w, h, edge_ring_share, corner_share, roster,
                collect_u64s=None):
    """roster: list of {'id': i, optional 'x','y'}; returns id-ordered
    [(kitty, x, y, category, drawn)]."""
    rng = law_rng(world_seed)
    cats = categories(w, h)
    occupied = {(k["x"], k["y"]) for k in roster if "x" in k}
    out = []
    for k in sorted(roster, key=lambda r: r["id"]):
        if "x" in k:
            cx, cy = k["x"], k["y"]
            cat = next(c for c, tiles in cats.items() if (cx, cy) in tiles)
            out.append((k["id"], cx, cy, cat, False))
            continue
        v1 = rng.next_u64()
        if collect_u64s is not None:
            collect_u64s.append(v1)
        u = (v1 >> 11) * 2.0 ** -53
        cat = ("corner" if u < corner_share
               else "edge_ring" if u < edge_ring_share else "interior")
        free = [t for t in cats[cat] if t not in occupied]
        if not free:
            raise SystemExit(f"category {cat} exhausted at kitty {k['id']}")
        v2 = rng.next_u64()
        if collect_u64s is not None:
            collect_u64s.append(v2)
        tile = free[v2 % len(free)]
        occupied.add(tile)
        out.append((k["id"], tile[0], tile[1], cat, True))
    return out


def check_golden(path):
    g = json.load(open(path))
    assert g["starts_law_version"] == 1, g["starts_law_version"]
    bad = 0
    for case in g["cases"]:
        draws = []
        got = engine_draw(case["seed"], case["width"], case["height"],
                          case["edge_ring_share"], case["corner_share"],
                          case["roster"], collect_u64s=draws)
        want = [(s["kitty"], s["x"], s["y"], s["category"], s["drawn"])
                for s in case["starts"]]
        if draws != case["u64_draws"]:
            bad += 1
            print(f"FAIL {case['name']}: u64 stream diverges at index "
                  f"{next(i for i, (a, b) in enumerate(zip(draws, case['u64_draws'])) if a != b) if draws else 0}")
        elif got != want:
            bad += 1
            print(f"FAIL {case['name']}: positions differ: {got} vs {want}")
        else:
            print(f"ok  {case['name']}: {len(draws)} u64s + "
                  f"{len(want)} positions byte-exact")
    return bad


def check_meta(meta_path, config_path):
    meta = json.load(open(meta_path))
    cfg = tomllib.load(open(config_path, "rb"))
    assert meta.get("starts_law_version") == 1, "meta has no law-v1 stamp"
    echo = meta["starts"]
    assert echo, f"{meta_path}: no starts echo (knob off?)"
    roster = [{k: kit[k] for k in ("id", "x", "y") if k in kit}
              for kit in cfg["kitty"]]
    got = engine_draw(meta["world_seed"], cfg["world"]["width"],
                      cfg["world"]["height"],
                      cfg["starts"]["edge_ring_share"],
                      cfg["starts"]["corner_share"], roster)
    want = [(s["kitty"], s["x"], s["y"], s["category"], s["drawn"]) for s in echo]
    if got != want:
        print(f"FAIL {meta_path}: {got} vs echo {want}")
        return 1
    print(f"ok  {meta_path}: {len(want)} echoed positions match the law "
          f"(seed {meta['world_seed']})")
    return 0


def check_manifest(manifest_path):
    """Leg B: re-derive collect_corpus's draw and compare manifest +
    the explicit x/y in every rollout config."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import collect_corpus as cc
    import numpy as np
    man = json.load(open(manifest_path))
    root = Path(manifest_path).parent
    w, h = man["world"]
    rng = np.random.default_rng(man["draw_seed"])
    # Replay the driver's exact consumption order (collect_corpus.main):
    # class permutation first, then per rollout starts -> class draws.
    n = len(man["rollouts"])
    rng.permutation(n)
    dl = man["draw_law"]
    bad = 0
    for row in man["rollouts"]:
        starts, cats = cc.sample_starts(rng, man["roster"], w, h,
                                        man["pencil_shares"]["edge_ring"],
                                        man["pencil_shares"]["corner"])
        drawn_consent = None
        if row["class"] == "enrichment":
            drawn_consent = round(float(rng.uniform(*dl["enrich_consent"])), 3)
        elif row["class"] == "traits":
            cc.draw_dials(rng, man["roster"], *dl["slack_range"],
                          *dl["mult_range"], dl["mult_k"])
        if drawn_consent is not None and drawn_consent != row["consent_line"]:
            bad += 1
            print(f"FAIL rollout {row['rollout']}: consent {drawn_consent} "
                  f"!= manifest {row['consent_line']}")
            continue
        if [list(s) for s in starts] != row["starts"] or cats != row["categories"]:
            bad += 1
            print(f"FAIL rollout {row['rollout']}: re-derived draw differs "
                  f"({starts} / {cats} vs manifest)")
            continue
        cfg = tomllib.load(open(root.parent.parent / row["config"], "rb")) \
            if not (root / "configs").exists() \
            else tomllib.load(open(Path(row["config"]), "rb"))
        xy = [(k["x"], k["y"]) for k in cfg["kitty"]]
        if xy != [tuple(s) for s in starts]:
            bad += 1
            print(f"FAIL rollout {row['rollout']}: config x/y {xy} != drawn {starts}")
            continue
        print(f"ok  rollout {row['rollout']:02d}: manifest + config match "
              f"the re-derived draw ({cats.count('edge')}E/{cats.count('corner')}C)")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", type=Path)
    ap.add_argument("--meta", type=Path, action="append", default=[])
    ap.add_argument("--config", type=Path)
    ap.add_argument("--manifest", type=Path)
    a = ap.parse_args()
    bad = 0
    if a.golden:
        bad += check_golden(a.golden)
    for m in a.meta:
        bad += check_meta(m, a.config)
    if a.manifest:
        bad += check_manifest(a.manifest)
    if bad:
        raise SystemExit(f"starts_check: {bad} FAILURES")
    print("starts_check: all checks pass")


if __name__ == "__main__":
    main()
