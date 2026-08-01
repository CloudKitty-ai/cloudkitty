"""Build results/figures/data/ — the committed inputs for make_figures.py.

The raw sources (artifacts/, raw/) are gitignored, so each figure's
input is snapshotted here in small, committed form. Sections whose
local inputs are missing are skipped with a note: the committed data/
copies are then the canonical record (the certification JSONs in
particular are kitty-eval outputs and must NOT be regenerated —
evaluate-once).

Sections:
  curves   — per-seed training curves from artifacts/arm*/metrics.jsonl
  labels   — bc-v1 action-label histogram (raw/bc-v1/*/label.npy)
  traj     — seed 1-3 x 20k-tick descriptive replays of the three
             served-world arms (all-scripted / baseline / Seating B) on
             the CURRENT config+engine; deterministic re-reads in the
             pair-screen arms' shape (prereg deviation 2026-07-31e),
             plus the all-scripted control. Positions, happiness, meows.
  copy     — certification JSONs + pairing matrices produced elsewhere

Run from anywhere: trainer/.venv/bin/python generate_data.py [section ...]
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np

FIGDIR = Path(__file__).resolve().parent
REPO = FIGDIR.parents[3]
EXP = FIGDIR.parents[1]
DATA = FIGDIR / "data"
DATA.mkdir(exist_ok=True)


def curves():
    out = {}
    seeds = []
    for d in sorted((EXP / "artifacts").glob("arm[23]-*")):
        mfile = d / "metrics.jsonl"
        if not mfile.exists():
            continue
        ticks, ret, ent = [], [], []
        for line in open(mfile):
            m = json.loads(line)
            if m.get("ep_return_mean") is not None:
                ticks.append(m["ticks"])
                ret.append(m["ep_return_mean"])
                ent.append(m["entropy"])
        out[f"{d.name}_ticks"] = np.array(ticks, np.int64)
        out[f"{d.name}_ret"] = np.array(ret, np.float32)
        out[f"{d.name}_ent"] = np.array(ent, np.float32)
        seeds.append(d.name)
    if not seeds:
        print("curves: no artifacts/arm*/metrics.jsonl found, skipped")
        return
    np.savez_compressed(DATA / "training-curves.npz",
                        seeds=np.array(seeds), **out)
    print(f"curves: {len(seeds)} runs -> training-curves.npz")


def labels():
    root = EXP / "raw/bc-v1"
    dirs = sorted(root.glob("config-*-rollout-*"))
    if not dirs:
        print("labels: raw/bc-v1 not found, skipped")
        return
    counts = np.zeros(40, np.int64)
    for d in dirs:
        counts += np.bincount(
            np.load(d / "label.npy", mmap_mode="r"), minlength=40)
    np.savez_compressed(DATA / "bc-label-hist.npz", counts=counts,
                        rollouts=len(dirs))
    print(f"labels: {counts.sum():,} decisions over {len(dirs)} rollouts "
          "-> bc-label-hist.npz")


def traj():
    sys.path.insert(0, str(EXP / "trainer"))
    import torch
    from forensics_replay import replay
    from model import MLP

    def load(path):
        ck = torch.load(path, map_location="cpu", weights_only=True)
        pol = MLP(ck["dims"])
        pol.load_state_dict(ck["state_dict"])
        pol.eval()
        return pol

    s6 = load(EXP / "artifacts/arm2-g0p998-s6/policy-final.pt")
    s3 = load(EXP / "artifacts/arm2-g0p998-s3/policy-final.pt")
    arms = {
        "all-scripted": dict(
            control={"kitty_1": "needs_driven", "kitty_2": "playful",
                     "kitty_3": "needs_driven", "kitty_4": "needs_driven"},
            seats=None),
        "baseline": dict(
            control={"kitty_2": "playful", "kitty_3": "needs_driven",
                     "kitty_4": "needs_driven"}, seats=None),
        "seating-b": dict(
            control={"kitty_2": "playful", "kitty_3": "needs_driven"},
            seats={"kitty_4": s3}),
    }
    ticks, seeds, width = 20_000, [1, 2, 3], 24
    for arm, cfg in arms.items():
        pos, hap, mrows = [], [], []
        for seed in seeds:
            log, _ = replay(s6, REPO / "cloudkitty.toml", seed, ticks,
                            horizon=ticks, pin_clock=True,
                            control=cfg["control"], seats=cfg["seats"])
            pos.append(np.clip(np.rint(log["pos"] * width), 0, width - 1)
                       .astype(np.uint8))
            hap.append(log["happiness"])
            for t, k, kind in log["meows"]:
                mrows.append((seed, int(t), int(k), str(kind)))
            print(f"traj {arm} seed {seed}: reward {log['reward'].mean():.4f}",
                  flush=True)
        kinds = sorted({r[3] for r in mrows})
        np.savez_compressed(
            DATA / f"traj-{arm}.npz",
            seeds=np.array(seeds), pos=np.stack(pos), hap=np.stack(hap),
            meow=np.array([(s, t, k, kinds.index(kd))
                           for s, t, k, kd in mrows], np.int64)
                 .reshape(-1, 4),
            meow_kinds=np.array(kinds))
        print(f"traj: {arm} -> traj-{arm}.npz ({len(mrows)} meows)")


def copy():
    scratch = sorted(Path("/private/tmp").glob(
        "claude-*/-Users-elizabethkelly-ai-cloudkitty/*/scratchpad"))
    src = {
        "r2-s3.json": [s / "r2-s3.json" for s in scratch],
        "r2-s4.json": [s / "r2-s4.json" for s in scratch],
        "r2-s6.json": [s / "r2-s6.json" for s in scratch],
        "arm0-cert.json": [s / "arm0-cert.json" for s in scratch],
        "clone-report30.json": [EXP / "artifacts/clone/report30.json"],
        "pair-partner-all-scripted.npy":
            [s / "pair-partner-all-scripted.npy" for s in scratch],
        "pair-partner-baseline.npy":
            [s / "pair-partner-baseline.npy" for s in scratch],
        "pair-partner-B-kittybear.npy":
            [s / "pair-partner-B-kittybear.npy" for s in scratch],
    }
    for name, candidates in src.items():
        dst = DATA / name
        found = next((c for c in candidates if c.exists()), None)
        if found:
            shutil.copy2(found, dst)
            print(f"copy: {found} -> data/{name}")
        elif dst.exists():
            print(f"copy: {name} already committed, source gone (fine)")
        else:
            print(f"copy: MISSING {name} — no source and no committed copy")


SECTIONS = {"curves": curves, "labels": labels, "traj": traj, "copy": copy}

if __name__ == "__main__":
    wanted = sys.argv[1:] or list(SECTIONS)
    for w in wanted:
        SECTIONS[w]()
