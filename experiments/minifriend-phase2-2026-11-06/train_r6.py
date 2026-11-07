#!/usr/bin/env python3
"""R-6 — the row-only side read (DECLARATION.md §6 R-6; ruled 2026-11-04 "2", 2026-11-06 "run it"): a MEMORYLESS act
head — Linear(167 -> 11) softmax on the observer's self block ++ the friend's row, no GRU — trained by the act arc's
recipe verbatim (train_act: the same split, targets y0 / y10, loss, Adam 1e-3, batch, early stop) on Phase 1e's
training worlds, three seeds, and read on the needy TUNING half beside B10 / B15 by the act arc's own reader
(read_act.evaluate). It separates what the GRU's memory adds from what the heard row's windowed cells already carry
(the Professor's memory-vs-row question). One head, zero collection, no covered mind; not a gate.

    train_r6.py train --seed 1 [--smoke]          # heads land in the act arc's store as R0-s<seed>
    train_r6.py read  --out reads/r6.json [--md]  # R0 / B10 / B15 × seeds 1-3 on the needy tuning half (+ lived eval worlds)
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p2_common as C  # noqa: E402
import ladder_act as LA  # noqa: E402
import train_act as TA  # noqa: E402
import read_act as R  # noqa: E402
import data_act as D  # noqa: E402

ARM = "R0"
PARAMS = 2 * (TA.X_DIM * D.N_ACTS + D.N_ACTS)       # two Linear(167 -> 11): 3,696
SEEDS = (1, 2, 3)


class RowOnly(nn.Module):
    """No state: y0 and y10 logits are linear in x_t alone."""
    def __init__(self):
        super().__init__()
        self.out0 = nn.Linear(TA.X_DIM, D.N_ACTS)
        self.out10 = nn.Linear(TA.X_DIM, D.N_ACTS)

    def forward(self, x, h0=None):                       # (T, B, 167) -> the trainer's (o0, o10, hn) contract
        # hn is a dummy zero state (1, B, 1) so train_act.run_epoch's h.detach() has a tensor; nothing reads it
        return self.out0(x), self.out10(x), x.new_zeros(1, x.shape[1], 1)


def register():
    """R0 into the act arc's tables (ladder_act.register's pattern), make_model routing to RowOnly."""
    LA.register()
    TA.WIDTH[ARM] = 0
    TA.DECLARED_PARAMS[ARM] = PARAMS
    TA.ARMS = tuple(TA.ARMS) + ((ARM,) if ARM not in TA.ARMS else ())
    orig = TA.make_model

    def make_model(arm, seed):
        return RowOnly() if arm == ARM else orig(arm, seed)
    if getattr(TA.make_model, "__name__", "") != "make_model_r6":
        make_model.__name__ = "make_model_r6"
        TA.make_model = make_model


def train(seed, smoke=False, threads=3):
    register()
    argv = sys.argv
    sys.argv = ["train_act.py", "--arm", ARM, "--seed", str(seed), "--threads", str(threads)] + (["--smoke"] if smoke else [])
    try:
        TA.main()
    finally:
        sys.argv = argv


def read(progress=True):
    """read_act.evaluate on the lived evaluation worlds and the needy TUNING half, heads R0 / B10 / B15 × seeds."""
    register()
    torch.set_num_threads(1)
    arms = (ARM, "B10", "B15")
    heads = {(a, s): TA.load_act(a, s)[0] for a in arms for s in SEEDS}
    worlds = [(g, (lambda n=n, s=s: R.load_lived(n, s))) for g, n, s in R.lived_worlds()]
    for arm, k, seed, _t, path in R.needy_worlds("tuning"):
        worlds.append(("needy-tuning", (lambda p=path, a=arm, kk=k, sd=seed: R.load_needy(p, a, kk, sd, "tuning"))))
    tables, base = R.evaluate(worlds, heads, progress, "r6")
    summary = R.summarise(tables, arms)
    prim, fog, seen, heard = R.PRIMARY, R.FOG, dict(R.PRIMARY, state="seen"), dict(R.PRIMARY, state="heard")
    cells = {a: {k: R.cell(summary, a, spec) for k, spec in (("all", prim), ("seen", seen), ("heard", heard), ("silent", fog))} for a in arms}
    out = {"half": "tuning", "arms": list(arms), "seeds": list(SEEDS), "params": {ARM: PARAMS, "B10": 8182, "B15": 12438},
           "baseline": base, "cells_top1_needy_tuning_covered_y0": cells,
           "memory_gain": {a: {k: (cells[a][k] - cells[ARM][k]) if cells[a][k] is not None and cells[ARM][k] is not None else None
                               for k in cells[a]} for a in ("B10", "B15")},
           "summary": summary, "tables": tables,
           "note": "the row-only head carries no state: its gap to B10 / B15 per regime is what the GRU's memory adds "
                   "beyond the heard row's windowed cells (seen: the row names the activity; heard: the message block; silent: nothing)"}
    return out


def md(out):
    L = ["# R-6 — the row-only act head beside B10 / B15 (needy tuning half, covered friends, y0 top-1)", "",
         "| regime | R0 (no memory) | B10 | B15 | B10 − R0 | B15 − R0 |", "|---|---|---|---|---|---|"]
    c, g = out["cells_top1_needy_tuning_covered_y0"], out["memory_gain"]
    f = lambda v: "—" if v is None else f"{v:.3f}"
    for k in ("all", "seen", "heard", "silent"):
        L.append(f"| {k} | {f(c['R0'][k])} | {f(c['B10'][k])} | {f(c['B15'][k])} | {f(g['B10'][k])} | {f(g['B15'][k])} |")
    L += ["", out["note"]]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["train", "read"])
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--out", type=Path, default=HERE / "reads" / "r6.json")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    if a.cmd == "train":
        train(a.seed, a.smoke, a.threads)
    else:
        out = read(progress=not a.quiet)
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(out, indent=1) + "\n")
        if a.md:
            a.out.with_suffix(".md").write_text(md(out))
            print(md(out))
        else:
            print(json.dumps(out["cells_top1_needy_tuning_covered_y0"], indent=1))


if __name__ == "__main__":
    main()
