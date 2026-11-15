#!/usr/bin/env python3
"""The re-anchor scout's thin driver (DECLARATION.md §3, §4; deviations entry 38): `reanchor-s1` is trunk seed 1's
own run resumed EXACTLY as `cont-s1` was (the continuation's `prepare` and `apply_deltas`, called, never copied; the
trainer's own `--resume` path) with these deltas and no other. No trainer file is edited: the deltas are set on the
imported modules and undone when the run returns.

  1. THE ANCHOR is trunk seed 1's final policy (by sha256), not the BC clone: the trainer builds its anchor from its
     init pin, and the resume then loads the checkpoint's policy over the init — the same weights, bit for bit.
  2. A fresh episode-seed stripe: run index 125 (SEED-BANDS.md, claimed 2026-11-14), segment 1 by the resume rule.
  3. TWO BINS: the run ends at update 3,255 inclusive (10,002,432 lineage ticks). `--total-ticks` stays 20,000,000 so
     the schedules continue the trunk's own from progress 0.40 (no restart, no warm-up); the stop is taken here, before
     the first fragment of update 3,256 is collected, and writes `policy-final.pt` (and the closing bin's
     `ckpt-u3255.pt`, as the continuation's checkpoints).
The harm stops are the trainer's own, armed as written; the plateau stop is off (it cannot fire in two bins).

    VIRTUAL_ENV=$A/.venv caffeinate -s nohup $A/.venv/bin/python3 -B train_ppo_reanchor.py > artifacts/reanchor-s1.log 2>&1 &
    (A = experiments/minifriend-phase2-2026-11-06, the declared binding; launched on the owner's word only. An
    interrupted run is re-run with the same command: the trainer's resume rule continues it one segment on.)
    --stop-update N --out-dir <scratch>: the guards' short runs (test_reanchor.py); never a declared run.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
CONT_ARC = HERE.parent / "gen2-trunk-continuation-2026-11-10"
sys.path.insert(0, str(CONT_ARC))
import train_ppo_cont as D  # noqa: E402
T = D.T

NAME, TRUNK_SLOT = "reanchor-s1", "trunk-s1"
RUN_INDEX = 125
STOP_UPDATE = 3_256                                         # the first update NOT run: the last is 3,255 (two bins)
ANCHOR = D.TRUNK_ARC / "artifacts" / f"ppo-g2-{TRUNK_SLOT}" / "policy-final.pt"
ANCHOR_SHA256 = "a22b8713f517f794dd441ffe59a07004953c3e7637166093dbf78dee1f458364"   # p2_common.TRUNK_FINAL_SHA[1]
ARGV_TAIL = []                                              # nothing: --total-ticks stays the trainer's 20,000,000


class Done(Exception):
    """The declared end: raised before the stop update's first fragment is collected."""


def run(out=None, stop=STOP_UPDATE):
    out = Path(out) if out else HERE / "artifacts" / NAME
    assert stop == STOP_UPDATE or HERE / "artifacts" not in out.resolve().parents, "a short run never writes under artifacts/"
    assert T.sha256(ANCHOR) == ANCHOR_SHA256, f"{ANCHOR} is not trunk seed 1's final"
    keep = (T.PLATEAU_BINS, T.schedules, T.collect_fragment, sys.argv, T.PINS["init_clone"])
    try:
        D.SLOT[NAME] = TRUNK_SLOT
        if not (out / "checkpoint.pt").exists():
            D.prepare(NAME, out)                            # the continuation's own byte copy and resume record
        D.apply_deltas(NAME, out)                           # plateau stop off; ckpt-u<update>.pt at every closed bin
        T.SLOTS[NAME] = (T.SLOTS[TRUNK_SLOT][0], RUN_INDEX)
        T.PINS["init_clone"] = str(ANCHOR)
        inner_schedules, inner_collect, at = T.schedules, T.collect_fragment, {}

        def schedules(update, total_updates, args):
            at["update"] = update
            return inner_schedules(update, total_updates, args)

        def collect_fragment(runner, policy, critic, vstats, fragment):
            if at["update"] >= stop:
                u = at["update"] - 1
                rec = {"hyper": policy.hyper, "state_dict": policy.state_dict(), "arm": NAME, "update": u, "ticks": (u + 1) * D.TPU}
                if D.closes_bin(u):
                    torch.save(rec, out / f"ckpt-u{u}.pt")
                torch.save({**rec, "stop_reason": "reanchor-end", "anchor_sha256": ANCHOR_SHA256}, out / "policy-final.pt")
                raise Done
            return inner_collect(runner, policy, critic, vstats, fragment)

        T.schedules, T.collect_fragment = schedules, collect_fragment
        (out / "reanchor-manifest.json").write_text(json.dumps({
            "name": NAME, "trunk_slot": TRUNK_SLOT, "run_index": RUN_INDEX, "seed_stripe": T.seed_stripe(RUN_INDEX),
            "anchor": str(ANCHOR), "anchor_sha256": ANCHOR_SHA256, "stop_update": stop, "end_ticks": stop * D.TPU,
            "declared": stop == STOP_UPDATE,
            "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip()}, indent=1) + "\n")
        sys.argv = ["train_ppo_g2.py", "--slot", NAME, "--resume", "--out-dir", str(out)] + ARGV_TAIL
        try:
            T.main()
        except Done:
            print(f"END: update {stop - 1} inclusive, {stop * D.TPU} lineage ticks -> {out / 'policy-final.pt'}", flush=True)
            return
        raise SystemExit("the trainer returned before the declared end (a stop or the cap): owner-routed, never auto-resumed")
    finally:
        T.PLATEAU_BINS, T.schedules, T.collect_fragment, sys.argv, T.PINS["init_clone"] = keep
        T.SLOTS.pop(NAME, None)
        D.SLOT.pop(NAME, None)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--stop-update", type=int, default=STOP_UPDATE)
    a = ap.parse_args()
    assert (a.out_dir is None) == (a.stop_update == STOP_UPDATE), "a declared run writes artifacts/reanchor-s1 and stops at 3,256; anything else is the guards'"
    run(a.out_dir, a.stop_update)
