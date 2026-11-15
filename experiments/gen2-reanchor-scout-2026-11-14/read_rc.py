#!/usr/bin/env python3
"""R-C, distance from the clone (DECLARATION.md §6, §2.5; dump-only, scores nothing). On the recorded observations of
the no-head arm's seed 1 20×20 leg (every 20th tick of each of its 30 worlds, replayed from the recorded acts: nothing
covered decides), the KL to the BC clone of four policies: trunk seed 1's final, the no-head final, the continued
final and this arm's final. The KL is the trainer's own (`train_ppo_g2.head_quantities`: policy against anchor, summed
over the act and message heads, on the tick's legal mask), called and not copied; beside it the KL to trunk seed 1's
final, this arm's anchor. Beside each: the share of rows whose top act differs from the clone's.

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_rc.py --out reads/rc.json [--md]     (about 3 minutes)
"""
import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
K = HERE.parent / "gen2-trunk-continuation-2026-11-10"
sys.path.insert(0, str(K))
import read_r1_cont as R1C  # noqa: E402  (puts Phase 2's arc, the trainer and the harness on sys.path)
import cert_harness_fog as H  # noqa: E402
C, RP = R1C.C, R1C.RP

POLICIES = {"trunk s1 final": "g2:trunk-s1", "no-head final": "p2:p2-nohead-s1r", "continued final": "g2:cont-s1", "re-anchored final": "g2:reanchor-s1"}
SIZE, EVERY, SEEDS = 20, 20, tuple(range(905_001, 905_031))


def world(seed):
    import torch
    import train_ppo_g2 as T
    torch.set_num_threads(1)
    clone = T.load_policy_ckpt(Path(T.PINS["init_clone"]))[0].eval()
    fwd = {name: H.load_model(spec) for name, spec in POLICIES.items()}
    acc = {name: {"kl_clone": 0.0, "kl_trunk": 0.0, "differ": 0} for name in POLICIES}
    n = 0
    for rec in RP.replay(RP.acts_path("p2u-nohead-s1", SIZE, seed), C.LEG_TOML[SIZE], want_obs=True):
        if rec["tick"] % EVERY:
            continue
        ob, mk = torch.from_numpy(rec["obs"]), torch.from_numpy(rec["mask"])
        act, msg = torch.from_numpy(rec["acts"][:, 0].astype(np.int64)), torch.from_numpy(rec["acts"][:, 1].astype(np.int64))
        a_clone = T.anchor_log_softmaxes(clone, ob, mk)
        logits = {name: torch.from_numpy(np.asarray(f(rec["obs"], rec["mask"]), np.float32)) for name, f in fwd.items()}
        a_trunk = torch.cat([torch.where(mk[:, lo:hi], T.masked_log_softmax(logits["trunk s1 final"][:, lo:hi], mk[:, lo:hi]), torch.zeros(1))
                             for lo, hi in ((0, T.N_ACTIONS), (T.N_ACTIONS, T.N_ACTIONS + T.N_MSGS))], 1)
        top_clone = clone(ob).detach()[:, :T.N_ACTIONS].masked_fill(~mk[:, :T.N_ACTIONS], -1e9).argmax(1)
        for name, lg in logits.items():
            acc[name]["kl_clone"] += float(T.head_quantities(lg, a_clone, mk, act, msg)[2]) * len(ob)
            acc[name]["kl_trunk"] += float(T.head_quantities(lg, a_trunk, mk, act, msg)[2]) * len(ob)
            acc[name]["differ"] += int((lg[:, :T.N_ACTIONS].masked_fill(~mk[:, :T.N_ACTIONS], -1e9).argmax(1) != top_clone).sum())
        n += len(ob)
    return n, acc


def read(workers=6):
    with ProcessPoolExecutor(workers) as ex:
        res = list(ex.map(world, SEEDS))
    n = sum(r[0] for r in res)
    return {"rows": n, "worlds": len(res), "every": EVERY,
            "policies": {name: {k: sum(r[1][name][k] for r in res) / n for k in ("kl_clone", "kl_trunk", "differ")} for name in POLICIES}}


def md(out):
    L = ["# R-C: distance from the clone (dump-only; scores nothing)", "",
         f"{out['rows']} recorded rows: every {out['every']}th tick of the no-head arm's seed 1 20×20 leg, {out['worlds']} worlds.", "",
         "| policy | KL to the BC clone | KL to trunk s1's final | top act differs from the clone's |", "|---|---|---|---|"]
    for name, r in out["policies"].items():
        L.append(f"| {name} | {r['kl_clone']:.4f} | {r['kl_trunk']:.4f} | {r['differ']:.3f} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    out = read()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    if a.md:
        a.out.with_suffix(".md").write_text(md(out))
    print(md(out))
