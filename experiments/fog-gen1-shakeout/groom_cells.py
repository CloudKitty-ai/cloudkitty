"""Who grooms whom, corpus vs probes, against who was dirty, visible
and legal (the finding-6 slot-bias read, 2026-09-13).

    groom_cells.py [N_CORPUS_ROLLOUTS] [ARM ...]

Rows are by-id permanent (kitty_slots 4, A15): observer i's row k is
the k-th other id ascending, so GroomKitty index 15+k names a fixed
friend per observer. A cell is grooms / (row present AND row bath >=
the announce threshold AND GroomKitty legal), with the row's visible
share in parentheses. Guard: test_groom_cells.py."""
import glob
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "/Users/elizabethkelly/ai/cloudkitty/experiments/attn-oracle-2026-08-15")
import obs_layout_v5 as L  # noqa: E402

KB = dict(L.WIDTHS)["self"]
KW = L.KITTY_W
IDS = [1, 2, 3, 4, 5]
NAMES = {1: "Miso", 2: "Biscuit", 3: "Pumpkin", 4: "Kittybear", 5: "Clem"}
DIRTY = 0.20  # announce threshold 20 / 100


def cells(obs, kitty, act, mask):
    """returns dict (i,j) -> [grooms, dirty_visible, dirty_visible_legal, visible]"""
    out = {}
    for i in IDS:
        sel = kitty == i
        o, a, m = obs[sel], act[sel], mask[sel]
        others = [j for j in IDS if j != i]
        for k, j in enumerate(others):
            b = KB + k * KW
            present = o[:, b + L.ROW_PRESENT] > 0
            bath = o[:, b + L.ROW_NEEDS + 5]
            legal = m[:, 15 + k] > 0
            dv = present & (bath >= DIRTY)
            out[(i, j)] = [int((a == 15 + k).sum()), int(dv.sum()),
                           int((dv & legal).sum()), int(present.sum())]
    return out


def dirty_share(obs, kitty):
    return {j: float((obs[kitty == j][:, L.SELF_NEEDS + 5] >= DIRTY).mean())
            for j in IDS}


def show(tag, c, ds, n):
    print(f"\n== {tag}  ({n} decisions)")
    print("dirty share (own bath>=20):", {NAMES[j]: round(v, 2) for j, v in ds.items()})
    print(f"{'observer':>10} " + " ".join(f"{NAMES[j]:>16}" for j in IDS))
    for i in IDS:
        row = []
        for j in IDS:
            if i == j:
                row.append(f"{'-':>16}")
            else:
                g, dv, dvl, p = c[(i, j)]
                row.append(f"{g:>4}/{dvl:<5}({p/n*5:.2f})")
        print(f"{NAMES[i]:>10} " + " ".join(row))
    tot = sum(v[0] for v in c.values())
    byrow = [0, 0, 0, 0]
    for i in IDS:
        others = [j for j in IDS if j != i]
        for k, j in enumerate(others):
            byrow[k] += c[(i, j)][0]
    print(f"grooms by row k: {byrow}  total {tot}   (cell = grooms/dirty-visible-legal (visible share))")


def add(c1, c2):
    for k, v in c2.items():
        c1.setdefault(k, [0, 0, 0, 0])
        for n in range(4):
            c1[k][n] += v[n]
    return c1


if __name__ == "__main__":
    # FOG_ROOT / FOG_CORPUS point the read at another pass (the cert pass:
    # root experiments/fog-gen1-cert, corpus results-raw/bc-corpus-b3/flat)
    root = Path(os.environ.get(
        "FOG_ROOT", "/Users/elizabethkelly/ai/cloudkitty/experiments/fog-gen1-shakeout"))
    corpus = os.environ.get("FOG_CORPUS", "results-raw/bc-corpus/flat")
    nroll = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    ctot, n, dsum = {}, 0, {j: 0.0 for j in IDS}
    for d in sorted(root.glob(f"{corpus}/config-00-rollout-*"))[:nroll]:
        obs = np.load(d / "obs.npy", mmap_mode="r")
        kitty = np.load(d / "kitty.npy")
        act = np.load(d / "label.npy").astype(int)
        mask = np.load(d / "mask.npy", mmap_mode="r")
        obs = np.asarray(obs)
        mask = np.asarray(mask)
        add(ctot, cells(obs, kitty, act, mask))
        ds = dirty_share(obs, kitty)
        for j in IDS:
            dsum[j] += ds[j] / nroll
        n += len(kitty)
    show(f"CORPUS teacher, {nroll} rollouts", ctot, dsum, n)
    for arm in sys.argv[2:] or ["ref-s1", "ref-s2", "leash", "vocab", "mixed"]:
        fs = sorted(root.glob(f"artifacts/ppo-fog-{arm}/probe-u*.npz"),
                    key=lambda s: int(s.name.split("-u")[1][:-4]))
        p = np.load(fs[-1])
        c = cells(p["obs"], p["kitty"], p["act"].astype(int), p["mask"][:, :39])
        show(f"{arm} final probe {fs[-1].name}", c, dirty_share(p["obs"], p["kitty"]), len(p["kitty"]))
        p = np.load(fs[0])
        c = cells(p["obs"], p["kitty"], p["act"].astype(int), p["mask"][:, :39])
        show(f"{arm} first probe {fs[0].name}", c, dirty_share(p["obs"], p["kitty"]), len(p["kitty"]))
