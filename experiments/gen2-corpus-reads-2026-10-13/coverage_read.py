#!/usr/bin/env python3
"""Coverage instrument (Gen 2 prereg skeleton §9 item 6, ruled shelf):
edge-ring / corner VISIT shares per source, read before the start-share
pass. The declared loop resolution (skeleton §4): collection runs on
the pencil start shares (25% edge ring / 5% corner); this instrument
reads the corpus; the FINAL shares are pinned at the freeze.

Positions come from the collector's global state (`state.npy`, one row
per world tick, ground truth — never decoded from observations; v6 has
no self-position cell). Per-kitty block width is keyed by global-state
version, inferred from `state_width` (v1 traits block = 32, v2
identity block = 40 — global_state.rs); an ambiguous or unmatched
width refuses loudly. World size comes from the rollout's config toml
(`--config` overrides metas whose recorded path is gone).

Geometry: the edge ring is the outermost tile ring (x or y at 0 or
max); the four corner tiles are reported separately AND are inside the
edge-ring count. Uniform occupancy on 20x20 would read edge 0.19,
corner 0.01.

Sources are labeled: `label=path`, where path is one rollout dir or a
dir of them (any dir holding meta.json with state.npy beside it).
Probe .npz and served-log adapters land when those reads are scheduled
(probes carry no global state; a v6 probe position would come from the
wall cells, v5 from SELF_POS).

    experiments/exp-006-character-gen/.venv/bin/python \\
        experiments/gen2-corpus-reads-2026-10-13/coverage_read.py \\
        corpus=experiments/fog-gen1-shakeout/results-raw/anchor-resmoke-050-20k \\
        [--config CONFIG.toml] [--out OUT.json]
"""
import argparse
import json
import sys
import tomllib
from pathlib import Path

import numpy as np

# Per-kitty block widths by global-state version (global_state.rs):
# v1 needs 6 + happiness + pos 2 + activity 7 + social + partner 2 +
# progress + distress 6 + traits 6; v2's identity block (14) replaces
# the traits.
PER_KITTY = {1: 32, 2: 40}
# Element summary + totals: 5 types x (count + K x (present, x, y))
# + total chow servings + episode clock.
N_ELEMENT_TYPES = 5
POS_OFF = 6 + 1  # needs, happiness, then x, y


def infer_block(state_width, roster):
    """(version, per_kitty, elements_per_type) from the recorded width,
    refusing anything but exactly one fit."""
    fits = []
    for ver, pk in PER_KITTY.items():
        rest = state_width - roster * pk - N_ELEMENT_TYPES - 2
        if rest >= 0 and rest % (N_ELEMENT_TYPES * 3) == 0:
            fits.append((ver, pk, rest // (N_ELEMENT_TYPES * 3)))
    if len(fits) != 1:
        raise SystemExit(
            f"coverage_read: state_width {state_width} at roster {roster} "
            f"fits {len(fits)} known global-state layouts {sorted(PER_KITTY)} "
            "— refusing to guess; check global_state.rs for a new version.")
    return fits[0]


def rollout_dirs(path):
    p = Path(path)
    if (p / "meta.json").exists():
        return [p]
    dirs = sorted({m.parent for m in p.rglob("meta.json")
                   if (m.parent / "state.npy").exists()})
    if not dirs:
        raise SystemExit(f"coverage_read: no rollout dirs under {p}")
    return dirs


def world_size(meta, config_override):
    cfg = config_override or meta["config"]
    p = Path(cfg)
    if not p.is_absolute():
        p = Path.cwd() / p
    if not p.exists():
        raise SystemExit(
            f"coverage_read: config {cfg} not found (meta paths are "
            "repo-relative — run from the repo root, or pass --config).")
    with open(p, "rb") as f:
        world = tomllib.load(f)["world"]
    return int(world["width"]), int(world["height"])


def read_rollout(rd, config_override=None):
    meta = json.load(open(rd / "meta.json"))
    w, h = world_size(meta, config_override)
    roster = len(meta["experts"])
    state = np.load(rd / "state.npy")
    if state.shape[1] != meta["state_width"]:
        raise SystemExit(f"coverage_read: {rd} state.npy width "
                         f"{state.shape[1]} != meta state_width {meta['state_width']}")
    ver, pk, _k = infer_block(state.shape[1], roster)
    kitty_ids = sorted(int(i) for i in meta["experts"])  # state block order
    x = np.stack([np.round(state[:, i * pk + POS_OFF] * w).astype(int)
                  for i in range(roster)], axis=1)
    y = np.stack([np.round(state[:, i * pk + POS_OFF + 1] * h).astype(int)
                  for i in range(roster)], axis=1)
    on_x_edge = (x == 0) | (x == w - 1)
    on_y_edge = (y == 0) | (y == h - 1)
    edge = on_x_edge | on_y_edge
    corner = on_x_edge & on_y_edge
    per_kitty = {str(kid): {"edge_ring_share": float(edge[:, i].mean()),
                            "corner_share": float(corner[:, i].mean())}
                 for i, kid in enumerate(kitty_ids)}
    return {"dir": str(rd), "ticks": int(state.shape[0]), "roster": roster,
            "world": [w, h], "global_state_version": ver,
            "edge_ring_share": float(edge.mean()),
            "corner_share": float(corner.mean()),
            "per_kitty": per_kitty,
            "samples": int(edge.size)}


def read_source(label, path, config_override=None):
    rollouts = [read_rollout(rd, config_override) for rd in rollout_dirs(path)]
    n = sum(r["samples"] for r in rollouts)
    edge = sum(r["edge_ring_share"] * r["samples"] for r in rollouts) / n
    corner = sum(r["corner_share"] * r["samples"] for r in rollouts) / n
    return {"source": label, "path": str(path), "rollouts": rollouts,
            "samples": n,
            "edge_ring_share": edge, "corner_share": corner}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+", metavar="label=path")
    ap.add_argument("--config", default=None,
                    help="config toml for world size, overriding every meta")
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args(argv)
    out = []
    for s in a.sources:
        label, _, path = s.partition("=")
        if not path:
            raise SystemExit(f"coverage_read: source {s!r} is not label=path")
        out.append(read_source(label, path, a.config))
    for r in out:
        print(f"{r['source']}: edge-ring {r['edge_ring_share']:.4f} "
              f"corner {r['corner_share']:.4f} "
              f"({r['samples']} kitty-ticks over {len(r['rollouts'])} rollouts)")
    if a.out:
        a.out.write_text(json.dumps(out, indent=1) + "\n")
    return out


if __name__ == "__main__":
    main()
