#!/usr/bin/env python3
"""The trunk continuation's thin driver (DECLARATION.md §3, §4; deviations entries 31 and 32): `cont-s<k>` is the
trunk seed's own run resumed by `train_ppo_g2.py`'s own `--resume` path, under its own recipe, with these deltas and
no other. The trunk arc's files are read, never written.

  1. The trunk's `checkpoint.pt` (update 2,605) is COPIED byte for byte to `artifacts/cont-s<k>/trunk-checkpoint.pt`
     (sha256 in `cont-manifest.json`); the run resumes from `checkpoint.pt` beside it, the same record with
     `flat_streak` reset to 0 (the checkpoint carries 3).
  2. NO PLATEAU STOP UNDER THE CAP (entry 32, her word 2026-11-12 "let's set a 20M floor": the floor is the 20M
     lineage cap). `plateau_flat` still runs and every bin's `flat` flag and `flat_streak` are recorded as the frozen
     rule would have set them (R-3 replays them); only the stop is off. The welfare stops stay armed as written.
  3. A policy checkpoint `ckpt-u<update>.pt` at every closed bin (as Phase 2; the checkpoint-ladder rungs).
  4. Segment 1 of the trunk's own seed stripe — the trainer's resume rule, nothing set here (guard g5).
`--total-ticks` stays 20,000,000, so `schedules()` continues the trunk's own schedule from progress 0.40.

    VIRTUAL_ENV=$A/.venv caffeinate -s nohup $A/.venv/bin/python3 -B train_ppo_cont.py cont-s1 > artifacts/cont-s1.log 2>&1 &
    (A = experiments/minifriend-phase2-2026-11-06, the declared binding. A run that was interrupted is re-run with
    the same command: the trainer's own resume rule continues it from its last checkpoint, one segment on.)
    --dry --out-dir <scratch>: the guards' resume with zero updates (test_cont.py); never a run.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
TRUNK_ARC = HERE.parent / "gen2-trunk-training-2026-10-18"
sys.path.insert(0, str(TRUNK_ARC / "trainer"))
import train_ppo_g2 as T  # noqa: E402

SLOT = {"cont-s1": "trunk-s1", "cont-s2": "trunk-s2", "cont-s4": "trunk-s4"}
RESUME_UPDATE = 2_605
TPU = 256 * 12                                             # ticks an update: the trainer's fragment x n_worlds defaults
CAP_UPDATES = 20_000_000 // TPU


def closes_bin(update):
    """Does update index `update` close a 1M-tick bin (the trainer's own test)?"""
    ticks = (update + 1) * TPU
    return ticks // T.BIN_TICKS > (ticks - TPU) // T.BIN_TICKS


def bin_checkpoints(start=RESUME_UPDATE, total=CAP_UPDATES):
    """[(update index, lineage ticks)] of every bin a run from `start` closes under the cap."""
    return [(u, (u + 1) * TPU) for u in range(start, total) if closes_bin(u)]


def prepare(name, out):
    """The byte copy of the trunk checkpoint and the resume record beside it (flat_streak 0, nothing else touched)."""
    src = TRUNK_ARC / "artifacts" / f"ppo-g2-{SLOT[name]}" / "checkpoint.pt"
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "checkpoint.pt").exists(), f"{out} holds a started run; the trainer resumes it, it is never re-prepared"
    shutil.copyfile(src, out / "trunk-checkpoint.pt")
    sha = T.sha256(out / "trunk-checkpoint.pt")
    assert sha == T.sha256(src), "the copy differs from the trunk checkpoint"
    rk = torch.load(out / "trunk-checkpoint.pt", map_location="cpu", weights_only=False)
    assert (rk["update"], rk["segment"], rk["flat_streak"]) == (RESUME_UPDATE, 0, 3), (rk["update"], rk["segment"], rk["flat_streak"])
    rk["flat_streak"] = 0
    torch.save(rk, out / "checkpoint.pt")
    (out / "cont-manifest.json").write_text(json.dumps({
        "name": name, "trunk_slot": SLOT[name], "trunk_checkpoint": str(src), "trunk_checkpoint_sha256": sha,
        "resume_update": RESUME_UPDATE, "resume_ticks": RESUME_UPDATE * TPU, "cap_updates": CAP_UPDATES, "cap_ticks": CAP_UPDATES * TPU,
        "deltas": ["flat_streak reset to 0", "no plateau stop under the cap (deviations entry 32)", "ckpt-u<update>.pt at every closed bin"],
        "bin_checkpoints": bin_checkpoints(), "python": sys.prefix,
        "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip()}, indent=1) + "\n")


def apply_deltas(name, out):
    """Deltas 2 and 3 on the imported trainer module (its file is never edited)."""
    T.PLATEAU_BINS = float("inf")
    inner_schedules, inner_collect, at = T.schedules, T.collect_fragment, {}

    def schedules(update, total_updates, args):
        at["update"] = update
        return inner_schedules(update, total_updates, args)

    def collect_fragment(runner, policy, critic, vstats, fragment):
        u = at["update"] - 1                                   # the update just finished; the policy is its result
        if u >= RESUME_UPDATE and closes_bin(u):
            torch.save({"hyper": policy.hyper, "state_dict": policy.state_dict(), "arm": name, "update": u, "ticks": (u + 1) * TPU},
                       out / f"ckpt-u{u}.pt")
        return inner_collect(runner, policy, critic, vstats, fragment)

    T.schedules, T.collect_fragment = schedules, collect_fragment


def run(name, out=None, dry=False):
    out = Path(out) if out else HERE / "artifacts" / name
    assert not dry or HERE / "artifacts" not in out.resolve().parents, "a dry resume never writes under artifacts/"
    if not (out / "checkpoint.pt").exists():
        prepare(name, out)
    apply_deltas(name, out)
    sys.argv = ["train_ppo_g2.py", "--slot", SLOT[name], "--resume", "--out-dir", str(out)] + (["--total-ticks", str(RESUME_UPDATE * TPU)] if dry else [])
    T.main()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name", choices=sorted(SLOT))
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    assert a.dry or a.out_dir is None, "a declared run writes artifacts/<name>; --out-dir is the guards'"
    run(a.name, a.out_dir, a.dry)
