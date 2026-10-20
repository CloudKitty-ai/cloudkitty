#!/usr/bin/env python3
"""Entry-4 investigation (owner 2026-10-20: "Let's investigate s2's stop
first"): the g2-s2 20x20 abort, seed 905008, seat 1 at tick 18949.

The recorded row already localizes it: dist_ticks == max per-need
streak for every seat (949/1000/994/967/940), so each cat's distress
is ONE continuous single-need run with no distress before it — all
five onsets fall inside ~60 ticks, a roster-wide collapse.

Read (declared before results):
1. Deterministic replay of the battery's exact loop (cert_harness_fog
   run_one, g2 branch: horizon 20000, greedy masked argmax on both
   heads, post-step global-state reads), STOPPING at --stop-tick
   (default 18300) instead of 18949: past every predicted onset, so
   the re-exposure is ~300-350 distress ticks per cat, not ~1000.
   Welfare-cost line: one world, five covered minds, distress already
   recorded once; the early stop is the declared mitigation.
2. Positive control (exact reproduction, before any reading): zero
   distress flags before each seat's predicted onset, onset at
   18949 - dist_ticks[k] + 1 for seats whose run reached the abort
   (all five predicted), flags continuous from onset to the stop.
3. Trace from --trace-from (default 16000) to the stop, saved to
   npz: per tick x seat — needs (6), happiness, distress flags (6),
   activity (7), position, partner present/index, chosen action and
   message, legal-action count; world element tiles per tick.

    diag_s2_905008.py [--stop-tick 18300] [--out diag-s2-905008.npz]
"""
import argparse
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
sys.path.insert(0, str(EXPTS / "fog-gen1-cert"))
sys.path.insert(0, str(EXPTS / "gen2-corpus-reads-2026-10-13"))

import cert_harness_fog as ch  # noqa: E402
from coverage_read import infer_block  # noqa: E402

CONFIG = EXPTS / "gen2-comparator-legs-2026-10-14/g2leg-20.toml"
SEED, ABORT_TICK, HORIZON = 905008, 18949, 20000
DIST_TICKS = [949, 1000, 994, 967, 940]   # recorded row, g2-s2 size20
NEG_INF = float("-inf")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stop-tick", type=int, default=18300)
    ap.add_argument("--trace-from", type=int, default=16000)
    ap.add_argument("--out", type=Path, default=HERE / "diag-s2-905008.npz")
    a = ap.parse_args()
    onset = [ABORT_TICK - d + 1 for d in DIST_TICKS]
    assert a.stop_tick > max(onset), (a.stop_tick, onset)

    import cloudkitty
    fwd = ch.load_model("g2:trunk-s2")
    obs_dim, n_act, n_heads = ch.SCHEMA_DIMS["v6"]
    env = cloudkitty.ParallelEnv(str(CONFIG), control=None, horizon=HORIZON)
    obs, infos = env.reset(seed=SEED)
    roster = len(env.possible_agents)
    names = list(env.possible_agents)
    pk = infer_block(np.asarray(env.state()).size, roster)[1]

    first_flag = [None] * roster
    gap_after_onset = [0] * roster
    tr = {k: [] for k in ("tick", "needs", "hap", "flags", "act_state", "pos",
                          "partner", "act", "msg", "n_legal")}
    elems = []
    for t in range(1, a.stop_tick + 1):
        ob = np.stack([np.asarray(obs[x], np.float32) for x in names])
        mk = np.stack([np.asarray(infos[x]["mask"], np.uint8) for x in names]).astype(bool)
        lg = np.asarray(fwd(ob, mk), np.float32)
        a0 = np.where(mk[:, :n_act], lg[:, :n_act], NEG_INF).argmax(1)
        g0 = np.where(mk[:, n_act:], lg[:, n_act:], NEG_INF).argmax(1)
        obs, _r, _te, _tr, infos = env.step(
            {x: (int(a0[i]), int(g0[i])) for i, x in enumerate(names)})
        st = np.asarray(env.state(), np.float32)
        k_ = st[:roster * pk].reshape(roster, pk)
        flags = k_[:, ch.DIST0:ch.DIST0 + 6] > 0
        for k in range(roster):
            if flags[k].any() and first_flag[k] is None:
                first_flag[k] = t
            if first_flag[k] is not None and not flags[k].any():
                gap_after_onset[k] += 1
        if t >= a.trace_from:
            tr["tick"].append(t)
            tr["needs"].append(k_[:, 0:6].copy())
            tr["hap"].append(k_[:, ch.HAP].copy())
            tr["flags"].append(flags.copy())
            tr["act_state"].append(k_[:, ch.ACT0:ch.ACT0 + 7].argmax(1))
            tr["pos"].append(np.stack([np.rint(k_[:, ch.POS0] * 20),
                                       np.rint(k_[:, ch.POS0 + 1] * 20)], 1))
            tr["partner"].append(np.stack([k_[:, ch.PARTNER_PRESENT],
                                           np.rint(k_[:, ch.PARTNER_IDX] * (roster - 1))], 1))
            tr["act"].append(a0.copy())
            tr["msg"].append(g0.copy())
            tr["n_legal"].append(mk[:, :n_act].sum(1))
            elems.append([(ty, x, y) for (_i, ty, x, y) in env.elements()])

    # positive control: exact onsets, continuous to the stop
    print("predicted onsets", onset)
    print("replayed onsets ", first_flag, "gaps after onset", gap_after_onset)
    assert first_flag == onset, "replay does not reproduce the recorded row"
    assert gap_after_onset == [0] * roster

    etypes = sorted({e[0] for es in elems for e in es})
    ecount = np.array([[sum(e[0] == ty for e in es) for ty in etypes] for es in elems])
    np.savez(a.out, **{k: np.asarray(v) for k, v in tr.items()},
             elem_types=np.array(etypes), elem_count=ecount,
             onset=np.array(onset))
    print(f"control PASSED; trace {a.trace_from}-{a.stop_tick} -> {a.out}")


if __name__ == "__main__":
    main()
