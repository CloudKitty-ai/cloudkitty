#!/usr/bin/env python3
"""R1d — the SD filter's spread under pure drift (DECLARATION.md §Read 1).
Read-only on Phase 1c's committed heads: a delta belief at START is
pushed n ticks through 1c's `shift_matrix` at a rate (bins per tick)
with no relief and no residual, and its standard deviation is reported
beside the closed form √(n f (1 − f)) (each tick an independent
Bernoulli step of one extra bin with probability f, the fractional
part; exact while no mass has reached the top bin).

    filter_spread.py --out spread.json        # also imported by read_phase1d.py
"""
import argparse
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
PHASE1C = HERE.parent / "minifriend-phase1c-2026-10-23"
os.environ.setdefault("MINIFRIEND_ARC", str(HERE))
sys.path.insert(0, str(PHASE1C))
import sd_head as M  # noqa: E402  (K, BIN, WIDTHS, run_name, shift_matrix, SDHead)

START = 2                                  # the sharp prior's bin
RELIEF_START = 12                          # the relief step's starting bin
TICKS = (1, 10, 50, 100, 500)
INIT_RATE_POINTS = 0.4                     # every 1c run's initial rate (sd_head.SDHead.__init__), points per tick
PROFESSOR_FIGURE_BINS = 2.7                # review §1b: sd after 100 ticks at the initial rate
CLAMP_EPS = 1e-12                          # 'clamped' = any mass at the end bin at double precision; the closed form is exact only before that
SEEDS = (1, 2, 3)
RUNS = [M.run_name(h, s) for h in M.WIDTHS for s in SEEDS]


def belief_sd(b):
    """Standard deviation in bins of a histogram (K,) about its own mean."""
    b = np.asarray(b, np.float64)
    b = b / b.sum()
    i = np.arange(len(b), dtype=np.float64)
    mu = float((b * i).sum())
    return float(math.sqrt(float(((i - mu) ** 2 * b).sum())))


def propagate(rate_bins, n, start=START, direction="up"):
    """A delta at `start` through n shifts of `rate_bins` with 1c's operator
    (double precision). Returns the belief (K,) and whether mass has
    reached the end bin (the clamp)."""
    U = M.shift_matrix(torch.tensor(float(rate_bins)), direction).double()      # (K, K), new = old @ U
    b = torch.zeros(M.K, dtype=torch.float64)
    b[start] = 1.0
    for _ in range(n):
        b = b @ U
    end = M.K - 1 if direction == "up" else 0
    return b.numpy(), bool(b[end] > CLAMP_EPS)


def closed_form(f, n):
    return math.sqrt(n * f * (1.0 - f))


def spread_row(rate_points, n):
    rate_bins = rate_points / M.BIN
    f = rate_bins - math.floor(rate_bins)
    b, clamped = propagate(rate_bins, n)
    sd = belief_sd(b)
    cf = closed_form(f, n)                                  # reported on every row; exact only while unclamped
    return {"rate_points_per_tick": float(rate_points), "rate_bins_per_tick": float(rate_bins), "n": n,
            "sd_bins": sd, "sd_points": sd * M.BIN, "clamped": clamped, "top_mass": float(b[M.K - 1]),
            "closed_form_bins": cf, "abs_diff_bins": abs(sd - cf)}


def load_head(run):
    ck = torch.load(PHASE1C / "results-raw/heads" / run / "head-best.pt", map_location="cpu", weights_only=False)
    model = M.SDHead(r=ck["manifest"]["hidden"])
    model.load_state_dict(ck["state_dict"])
    model.eval()
    return model, ck["manifest"]


def read_run(run):
    model, man = load_head(run)
    with torch.no_grad():
        rates, relief = model.rates()                       # points per tick: (5 friends, 5 needs), (5 needs)
    rates, relief = rates.numpy().astype(np.float64), relief.numpy().astype(np.float64)
    cells = rates.ravel()
    order = np.argsort(cells)
    pick = {"median": float(cells[order[len(cells) // 2]]), "max": float(cells.max()), "min": float(cells.min())}
    return {"width": man["hidden"], "rates_points_per_tick": rates.tolist(), "relief_points_per_tick": relief.tolist(),
            "cells": pick,
            "spread": {k: [spread_row(v, n) for n in TICKS] for k, v in pick.items()},
            "relief_step": [{"need": i, "size_points": float(relief[i]),
                             "sd_bins": belief_sd(propagate(relief[i] / M.BIN, 1, RELIEF_START, "down")[0])} for i in range(5)]}


def read_all():
    init = [spread_row(INIT_RATE_POINTS, n) for n in TICKS]
    runs = {r: read_run(r) for r in RUNS}
    rows = init + [row for r in runs.values() for rows_ in r["spread"].values() for row in rows_]
    unclamped = [x for x in rows if not x["clamped"]]
    max_diff = max(x["abs_diff_bins"] for x in unclamped)
    at100 = next(x for x in init if x["n"] == 100)
    rule = {"max_abs_diff_bins": max_diff, "n_rows": len(rows), "n_unclamped": len(unclamped),
            "init_sd_100_bins": at100["sd_bins"], "professor_figure_bins": PROFESSOR_FIGURE_BINS,
            "mechanism_stands": bool(max_diff <= 1e-6 and abs(at100["sd_bins"] - PROFESSOR_FIGURE_BINS) <= 0.1)}
    return {"start_bin": START, "relief_start_bin": RELIEF_START, "ticks": list(TICKS), "bin_points": M.BIN,
            "initial_rate": init, "runs": runs, "rule": rule}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    a.out.write_text(json.dumps(read_all(), indent=1))
    print(f"wrote {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
