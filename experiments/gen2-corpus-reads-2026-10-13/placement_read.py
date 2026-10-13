#!/usr/bin/env python3
"""Corpus placement-bar read (Gen 2 prereg skeleton §4 RULED S§6):
the teacher's in-beam sleep share on the fresh corpus, read pre-PPO.
The pencil bar is >= 0.40; the prereg pins the number at the freeze,
so this instrument REPORTS the share and prints the pencil bar as
reference, never a verdict.

This is the schema-keyed home of the step7_reads beam read (the read
GEN2-INPUTS declares): same definition — of all sleeping cat-ticks,
the share with the self in-sunbeam bit set — with every index taken
by name from the keyed layout (obs_layouts.layout_for on the trace's
own observation_schema), so it reads v5 and v6 trace dirs alike. On a
v5 trace it must agree with step7_reads' pooled beam number exactly
(pinned by test).

    experiments/exp-006-character-gen/.venv/bin/python \\
        experiments/gen2-corpus-reads-2026-10-13/placement_read.py \\
        TRACE_DIR [...] [--out OUT.json]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "attn-oracle-2026-08-15"))
import obs_layouts  # noqa: E402

PENCIL_BAR = 0.40  # S§6 'about 0.4'; the real bar is pinned at the freeze


def read_dir(rd):
    rd = Path(rd)
    meta = json.load(open(rd / "meta.json"))
    schema = meta["observation_schema"]
    L = obs_layouts.layout_for(schema)
    obs = np.load(rd / "obs.npy", mmap_mode="r")
    if obs.shape[1] != L.OBS_DIM:
        raise SystemExit(
            f"placement_read: {rd} obs width {obs.shape[1]} != schema "
            f"{schema}'s {L.OBS_DIM} — the trace disagrees with its meta.")
    kitty = np.load(rd / "kitty.npy").astype(int)
    act = np.asarray(obs[:, L.SELF_ACTIVITY:L.SELF_ACTIVITY + len(L.ACTIVITY_KINDS)])
    sleeping = act.argmax(1) == L.ACTIVITY_KINDS.index("sleeping")
    in_beam = np.asarray(obs[:, L.SELF_IN_SUNBEAM]) > 0.5
    per_seat = {}
    for kid in sorted(int(i) for i in meta["experts"]):
        sel = kitty == kid
        n = int((sleeping & sel).sum())
        per_seat[str(kid)] = {
            "sleep_ticks": n,
            "in_beam_share": float((sleeping & sel & in_beam).sum() / n) if n else None}
    n = int(sleeping.sum())
    return {"dir": str(rd), "schema": schema, "rows": int(len(kitty)),
            "sleep_ticks": n,
            "in_beam_share": float((sleeping & in_beam).sum() / n) if n else None,
            "per_seat": per_seat}


def read(paths):
    rollouts = [read_dir(p) for p in paths]
    n = sum(r["sleep_ticks"] for r in rollouts)
    hits = sum(r["in_beam_share"] * r["sleep_ticks"] for r in rollouts
               if r["in_beam_share"] is not None)
    return {"rollouts": rollouts, "sleep_ticks": n,
            "in_beam_share": (hits / n) if n else None,
            "pencil_bar": PENCIL_BAR}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args(argv)
    out = read(a.dirs)
    share = out["in_beam_share"]
    print(f"pooled in-beam sleep share {share if share is None else f'{share:.4f}'} "
          f"over {out['sleep_ticks']} sleep ticks in {len(out['rollouts'])} rollouts "
          f"(pencil bar {PENCIL_BAR}, pinned at the freeze)")
    for r in out["rollouts"]:
        seats = " ".join(f"{k}:{v['in_beam_share'] if v['in_beam_share'] is None else format(v['in_beam_share'], '.3f')}/{v['sleep_ticks']}"
                         for k, v in r["per_seat"].items())
        print(f"  {Path(r['dir']).name} (schema {r['schema']}): "
              f"{r['in_beam_share'] if r['in_beam_share'] is None else format(r['in_beam_share'], '.4f')} "
              f"of {r['sleep_ticks']} | {seats}")
    if a.out:
        a.out.write_text(json.dumps(out, indent=1) + "\n")
    return out


if __name__ == "__main__":
    main()
