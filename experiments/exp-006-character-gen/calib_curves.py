#!/usr/bin/env python3
"""E1's per-(observer, target) calibration curves — the owed prereg bank.

exp-006 §4 registered the E1 arm's aux head with "per-pair calibration
error logged and BANKED (the care-coupling program's pre-fog baseline,
design-inputs §4c)". The logging shipped: `train_ppo6.calibration` writes a
5x5 MAE matrix and its 5x5 sample counts on nearly every update. The BANK
is this — the curves themselves, reduced from the run logs to a form the
eventual C-grounded/C-free comparison can read.

**Why per-pair and never the average** (design-inputs §4c, verbatim in
intent): *a wireheader can stay calibrated on cats it ignores*. A mind that
tracks one partner closely and lets the rest drift shows a healthy mean and
a ruined spread, so the mean is the one number that cannot be trusted here.
Everything below is reported per pair first; aggregates come last and are
labelled as summaries of a distribution, not as the result.

Units: needs are the global-state block's first 6 features, normalised /100
(`crates/cloudkitty-rl/src/global_state.rs`), and the MAE is the mean over
those 6. So **0.010 = one need point** on the 0-100 scale the world speaks.

Reads `artifacts/ppo-E1-s{1,2}/metrics.jsonl`; writes the curves to
`results-raw/e1-calib-curves.json` and prints the markdown the results doc
carries.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from census_provenance import stamp  # noqa: E402

SEATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]


def load(seed_dir):
    """(ticks, mae[T,5,5], n[T,5,5]) for one run's logged updates."""
    rows = [json.loads(ln) for ln in
            (seed_dir / "metrics.jsonl").read_text().splitlines()]
    rows = [r for r in rows if r.get("calib_mae") is not None]
    ticks = np.array([r["ticks"] for r in rows], np.int64)
    mae = np.array([[[np.nan if v is None else v for v in row]
                     for row in r["calib_mae"]] for r in rows], np.float64)
    n = np.array([r["calib_n"] for r in rows], np.int64)
    return ticks, mae, n


def window(mae, n, lo, hi):
    """Count-weighted mean MAE per pair over updates [lo, hi).

    Weighted by samples, not by update: an update where a pair was barely
    observed should not count as much as one where it was observed 3,072
    times, and pairs differ in coverage by an order of magnitude.
    """
    m, c = mae[lo:hi], n[lo:hi].astype(np.float64)
    live = np.isfinite(m) & (c > 0)
    num = np.where(live, np.nan_to_num(m) * c, 0.0).sum(axis=0)
    den = np.where(live, c, 0.0).sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        out = np.where(den > 0, num / den, np.nan)
    return out, den


def table(title, m, fmt="{:.4f}"):
    lines = [f"**{title}**", "",
             "| observer \\ target | " + " | ".join(SEATS) + " |",
             "|---|" + "---|" * len(SEATS)]
    for i, name in enumerate(SEATS):
        cells = ["—" if not np.isfinite(m[i, j]) else fmt.format(m[i, j])
                 for j in range(len(SEATS))]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def curve(ticks, mae, n, bins=40):
    """Downsample to `bins` count-weighted points per pair, for plotting."""
    edges = np.linspace(0, len(ticks), bins + 1).astype(int)
    pts = []
    for b in range(bins):
        lo, hi = edges[b], edges[b + 1]
        if hi <= lo:
            continue
        m, den = window(mae, n, lo, hi)
        pts.append({"ticks": int(ticks[hi - 1]),
                    "mae": [[None if not np.isfinite(v) else round(float(v), 5)
                             for v in row] for row in m],
                    "n": [[int(v) for v in row] for row in den]})
    return pts


def baseline(config, seating, seed, ticks):
    """Constant-predictor MAD on a played world — the scale the MAE needs.

    A calibration MAE means nothing without the error of predicting no
    signal at all. Two references are computed on the same rollout: the
    per-(seat, need) mean (an oracle that knows each cat's habitual level
    but never looks at it) and the global per-need mean (knows only the
    roster's average). An estimator at or above these is tracking the
    marginal distribution, not the cats.

    PROXY, not a matched control: training ran on the family worlds under
    a mixed-population draw, and its need distribution shifted as the
    policy learned to satisfy needs. The exact version is a constant-
    predictor MAE logged beside `calib_mae` on the same fragment — a
    one-line trainer change, and every future run interprets itself.
    """
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(HERE / "trainer"))
    from cert_harness6 import SEATINGS, load_model, N_ACT, N_HEADS, NEG_INF
    import cloudkitty
    per_kitty, needs_f = 32, 6
    seats = list(SEATINGS[seating])
    models = {s: load_model(s) for s in set(seats)}
    env = cloudkitty.ParallelEnv(str(config), horizon=ticks)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    seat_of = {a: s for a, s in zip(names, seats)}
    rows = []
    for _ in range(ticks):
        ob = np.stack([np.asarray(obs[a], np.float32) for a in names])
        mk = np.stack([np.asarray(infos[a]["mask"], np.uint8)
                       for a in names]).astype(bool)
        lg = np.zeros((len(names), N_HEADS), np.float32)
        for s, fwd in models.items():
            r = [i for i, a in enumerate(names) if seat_of[a] == s]
            if r:
                lg[r] = np.asarray(fwd(ob[r]), np.float32)
        a0 = np.where(mk[:, :N_ACT], lg[:, :N_ACT], NEG_INF).argmax(1)
        g0 = np.where(mk[:, N_ACT:], lg[:, N_ACT:], NEG_INF).argmax(1)
        obs, _r, term, trunc, infos = env.step(
            {a: (int(a0[i]), int(g0[i])) for i, a in enumerate(names)})
        st = np.asarray(env.state(), np.float32)
        rows.append([st[k * per_kitty:k * per_kitty + needs_f]
                     for k in range(len(names))])
        if any(term.values()) or any(trunc.values()):
            break
    x = np.array(rows)
    return {
        "config": str(config), "seating": seating, "seed": seed,
        "ticks": int(x.shape[0]), "mean_need": round(float(x.mean()), 4),
        "mad_per_seat_mean": round(
            float(np.abs(x - x.mean(axis=0, keepdims=True)).mean()), 4),
        "mad_global_mean": round(
            float(np.abs(x - x.mean(axis=(0, 1), keepdims=True)).mean()), 4),
        "note": "proxy scale, not a matched control — see baseline() docstring",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", default=["ppo-E1-s1", "ppo-E1-s2"])
    ap.add_argument("--bins", type=int, default=40)
    ap.add_argument("--baseline-config", type=Path,
                    default=HERE / "configs/phase1-cutover-bugs2.toml")
    ap.add_argument("--baseline-seating", default="c006a-L04s3")
    ap.add_argument("--baseline-ticks", type=int, default=4000)
    ap.add_argument("--no-baseline", action="store_true")
    args = ap.parse_args()

    out = {"provenance": stamp(__file__), "units": "MAE of needs/100 — "
           "0.010 = one need point on the 0-100 scale", "runs": {}}
    md = []
    for run in args.runs:
        ticks, mae, n = load(HERE / "artifacts" / run)
        third = len(ticks) // 3
        early, early_n = window(mae, n, 0, third)
        late, late_n = window(mae, n, len(ticks) - third, len(ticks))
        out["runs"][run] = {
            "updates": len(ticks),
            "ticks": [int(ticks[0]), int(ticks[-1])],
            "early_mae": [[None if not np.isfinite(v) else round(float(v), 5)
                           for v in row] for row in early],
            "late_mae": [[None if not np.isfinite(v) else round(float(v), 5)
                          for v in row] for row in late],
            "late_samples": [[int(v) for v in row] for row in late_n],
            "curve": curve(ticks, mae, n, args.bins),
        }

        diag = np.array([late[i, i] for i in range(len(SEATS))])
        off = late[~np.eye(len(SEATS), dtype=bool)]
        seen = np.isfinite(late) & (late_n > 0)
        md.append(f"### {run} — {len(ticks)} logged updates, "
                  f"{ticks[0]:,}–{ticks[-1]:,} ticks\n")
        md.append(table(f"Late-training MAE per pair (final third)", late))
        md.append("")
        md.append(table("Early-training MAE per pair (first third)", early))
        md.append("")
        md.append(
            f"- pairs with any supervision late: **{int(seen.sum())} of 25**\n"
            f"- self (diagonal): mean {np.nanmean(diag):.4f}, "
            f"worst {np.nanmax(diag):.4f}\n"
            f"- others (off-diagonal): mean {np.nanmean(off):.4f}, "
            f"worst {np.nanmax(off[np.isfinite(off)]):.4f}, "
            f"spread {np.nanmax(off[np.isfinite(off)]) - np.nanmin(off[np.isfinite(off)]):.4f}\n"
            f"- early -> late change, count-weighted over live pairs: "
            f"{np.nansum((late - early) * late_n) / max(1.0, late_n[np.isfinite(late - early)].sum()):+.4f}\n")

    if not args.no_baseline:
        out["baseline"] = baseline(args.baseline_config, args.baseline_seating,
                                   870_001, args.baseline_ticks)
        b = out["baseline"]
        md.append(
            f"### Constant-predictor baseline (proxy scale)\n\n"
            f"`{b['seating']}` on `{Path(b['config']).name}`, {b['ticks']:,} "
            f"ticks, mean need {b['mean_need']:.4f}:\n\n"
            f"- predict each **seat's own mean need**: MAD "
            f"**{b['mad_per_seat_mean']:.4f}**\n"
            f"- predict the **global per-need mean**: MAD "
            f"**{b['mad_global_mean']:.4f}**\n")
    raw = HERE / "results-raw" / "e1-calib-curves.json"
    raw.write_text(json.dumps(out, indent=1) + "\n")
    print("\n".join(md))
    print(f"-> {raw}")


if __name__ == "__main__":
    main()
