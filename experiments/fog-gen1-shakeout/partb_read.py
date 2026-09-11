#!/usr/bin/env python3
"""Part B probe readout: the radius-screen welfare measures plus the
activity census, over a policy probe .npz (PREREG Part B, pass of
2026-09-10).

    partb_read.py PROBE_NPZ --config CONFIG_TOML [--out FILE]

The welfare accumulator is radius_screen.screen VERBATIM: this file only
adapts probe obs rows into the per-tick snapshot dicts screen consumes.
The adapter is validated by equivalence: on a bc-collect --trace anchor
rollout, screen over obs-derived snapshots must reproduce screen over
the recorded true snapshots (test_partb_read.py runs both). Two facts
make the adaptation exact: A3/A12 (probe-1, all arms green) proved the
obs discs and element slots agree with the geometry, and empty bowls
vanish from the world, so every visible chow is stocked.

Beyond screen: per-seat engine-class shares (H4 domination), the
39-menu census with legal-but-never-chosen (H3), scene starts by class
(the activity-mix band's scene count), and the message-head census.
Needs come back clamped at 100 (obs scale), so need_max saturates
there; the watchdog and distress reads count episode AGE and are exact.
Run from the repo root with the exp-006 venv.
"""
import argparse
import json
import sys
import tomllib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parent / "attn-cert-2026-08-14"))
sys.path.insert(2, str(HERE.parent / "attn-oracle-2026-08-15"))

import obs_layout_v5 as L  # noqa: E402
from radius_screen import screen  # noqa: E402

W = H = 20  # served world; every pass config keeps [world] 20x20
N_ACT = 39


def rows_by_seed(z):
    """Split an npz's decision rows into per-seed dicts sorted by
    (tick, kitty); every probe seed is its own rollout."""
    out = {}
    for s in np.unique(z["seed"]):
        m = z["seed"] == s
        order = np.lexsort((z["kitty"][m], z["tick"][m]))
        out[int(s)] = {k: z[k][m][order] for k in z.files}
    return out


def snapshots_from_obs(rows):
    """Per-tick snapshot dicts (radius_screen.screen's input) from obs.

    Elements: the union over observers of each one's visible slots,
    de-duplicated by absolute tile; servings 1 (a visible bowl is a
    stocked bowl). Memory: present bit -> a non-None marker."""
    obs, ticks, kitties = rows["obs"], rows["tick"], rows["kitty"]
    for t in np.unique(ticks):
        m = ticks == t
        o, kid = obs[m], kitties[m]
        snap = {"kitties": [], "elements": []}
        seen = set()
        for i in range(len(kid)):
            row = o[i]
            x = float(np.round(row[L.SELF_POS] * W))
            y = float(np.round(row[L.SELF_POS + 1] * H))
            mem = row[L.SELF_MEMORY:L.SELF_MEMORY
                      + len(L.ELEMENT_KINDS) * L.MEMORY_SLOT]
            snap["kitties"].append({
                "id": int(kid[i]), "pos": {"x": x, "y": y},
                "needs": {n: float(row[L.SELF_NEEDS + j]) * 100.0
                          for j, n in enumerate(L.NEED_KINDS)},
                "memory": [1 if mem[k * L.MEMORY_SLOT] > 0 else None
                           for k in range(len(L.ELEMENT_KINDS))],
            })
            for kind, base, count in _element_blocks():
                for slot in range(count):
                    b = base + slot * dict(L.WIDTHS)[kind]
                    if row[b + L.SLOT_PRESENT] <= 0:
                        continue
                    ex = x + float(np.round(row[b + L.SLOT_DX] * W))
                    ey = y + float(np.round(row[b + L.SLOT_DY] * H))
                    key = (kind, ex, ey)
                    if key in seen:
                        continue
                    seen.add(key)
                    snap["elements"].append(
                        {"kind": kind, "pos": {"x": ex, "y": ey},
                         "servings": 1})
        yield snap


def _element_blocks():
    """(block kind, obs offset of slot 0, slot count) per element block.
    Block order is the layout's (chow, water, sunbeam, critter); blind()
    reads chow and water only, so the critter block's kind label is the
    block name, not bug/greeble."""
    widths = dict(L.WIDTHS)
    off = widths["self"] + widths["kitty"] * L.COUNTS["kitty"]
    out = []
    for kind in ("chow", "water", "sunbeam", "critter"):
        out.append((kind, off, L.COUNTS[kind]))
        off += widths[kind] * L.COUNTS[kind]
    return out


def act7_census(rows):
    """Per-seat engine-class share over cat-ticks (H4 domination)."""
    obs, kitties = rows["obs"], rows["kitty"]
    out = {}
    for k in np.unique(kitties):
        one_hot = obs[kitties == k, L.SELF_ACTIVITY:L.SELF_ACTIVITY + 7]
        shares = one_hot.mean(0)
        out[int(k)] = {"shares": [round(float(s), 4) for s in shares],
                       "max_share": round(float(shares.max()), 4),
                       "argmax": int(shares.argmax())}
    return out


def menu_census(rows):
    """39-menu choice counts and the legal-but-never-chosen list (H3)."""
    act, mask = rows["act"], rows["mask"][:, :N_ACT]
    chosen = np.bincount(act, minlength=N_ACT)
    legal = mask.sum(0)
    dead = [{"menu_index": int(i), "legal_rows": int(legal[i])}
            for i in range(N_ACT) if legal[i] > 0 and chosen[i] == 0]
    return {"chosen": chosen.tolist(), "legal_rows": legal.tolist(),
            "hard_zero_legal": dead}


def scene_starts(rows):
    """Scene starts by engine class: a start is a tick where a seat's
    scene age falls below its previous value (reset), classed by the
    activity one-hot at the start tick."""
    obs, ticks, kitties = rows["obs"], rows["tick"], rows["kitty"]
    counts = np.zeros(7, int)
    for k in np.unique(kitties):
        m = kitties == k
        o = obs[m][np.argsort(ticks[m])]
        age = o[:, L.SELF_SCENE_AGE]
        starts = np.flatnonzero(np.diff(age) < 0) + 1
        for t in starts:
            counts[int(o[t, L.SELF_ACTIVITY:L.SELF_ACTIVITY + 7].argmax())] += 1
    return counts.tolist()


def msg_census(rows):
    """Message-head choice counts (Silent = index 0)."""
    return np.bincount(rows["msg"], minlength=L.N_HEAD).tolist()


def read_npz(path, config):
    with open(config, "rb") as f:
        cfg = tomllib.load(f)
    r = int(cfg["vision"]["radius"])
    out = []
    for seed, rows in sorted(rows_by_seed(np.load(path)).items()):
        res = screen(snapshots_from_obs(rows), r,
                     cfg["thresholds"]["distress"],
                     cfg["thresholds"]["safeguard"],
                     cfg["meow"]["announce_threshold"])
        res.update({"seed": seed, "probe": str(path),
                    "act7": act7_census(rows),
                    "menu": menu_census(rows),
                    "scene_starts_by_class": scene_starts(rows),
                    "msg_census": msg_census(rows)})
        out.append(res)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("probe", type=Path)
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    rows = read_npz(args.probe, args.config)
    for x in rows:
        print(f"seed {x['seed']}: wd {x['watchdog_entries']} "
              f"dist/1k {x['distress_episodes_per_1k']:.2f} "
              f"maxage {x['max_distress_age']} "
              f"nn-euc {x['dispersion']['euc_median']:.2f} "
              f"friend {x['friend_in_view_share']:.3f} "
              f"blindH/1k {x['blind_eat']['cat_ticks_per_1k']:.1f} "
              f"dom {max(v['max_share'] for v in x['act7'].values()):.2f}")
    if args.out:
        args.out.write_text(json.dumps(rows, indent=1) + "\n")


if __name__ == "__main__":
    main()
