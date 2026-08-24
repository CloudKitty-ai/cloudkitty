#!/usr/bin/env python3
"""Byte-continuity of the compiled binding across a rebuild.

House practice from the 018-020 refactor arc: an instrument that changes
underneath a campaign must be shown NOT to have changed what it measures.
This is that check for the maturin-built `cloudkitty` binding — run it
before rebuilding, rebuild, run it again, and compare the digests.

It hashes the full global-state trace of a fixed seating on a fixed seed,
so it is sensitive to any dynamics change anywhere in the engine, not to a
summary statistic that might absorb one.

    .venv/bin/python binding_continuity.py --out before.json
    (cd ../../crates/cloudkitty-py && ../../experiments/exp-006-character-gen/.venv/bin/maturin develop --release)
    .venv/bin/python binding_continuity.py --out after.json --compare before.json
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from census_provenance import stamp  # noqa: E402


def trace_digest(config, seating, seed, ticks):
    from cert_harness6 import SEATINGS, load_model, N_ACT, N_HEADS, NEG_INF
    import cloudkitty
    seats = list(SEATINGS[seating])
    models = {s: load_model(s) for s in set(seats)}
    env = cloudkitty.ParallelEnv(str(config), horizon=ticks)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    seat_of = {a: s for a, s in zip(names, seats)}
    h = hashlib.sha256()
    n = 0
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
        h.update(np.asarray(env.state(), np.float32).tobytes())
        n += 1
        if any(term.values()) or any(trunc.values()):
            break
    return h.hexdigest(), n


def binding_identity():
    import cloudkitty
    so = sorted(Path(cloudkitty.__file__).parent.glob("*.so"))
    out = {"module": cloudkitty.__file__, "artifacts": []}
    for p in so:
        out["artifacts"].append({
            "name": p.name,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "mtime": p.stat().st_mtime,
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path,
                    default=HERE / "configs/phase1-cutover-bugs2.toml")
    ap.add_argument("--seating", default="c006a-L04s3")
    ap.add_argument("--seed", type=int, default=870_001)
    ap.add_argument("--ticks", type=int, default=2000)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--compare", type=Path, default=None)
    args = ap.parse_args()

    digest, n = trace_digest(args.config, args.seating, args.seed, args.ticks)
    rec = {"provenance": stamp(__file__), "binding": binding_identity(),
           "config": str(args.config), "seating": args.seating,
           "seed": args.seed, "ticks": n, "state_trace_sha256": digest}
    args.out.write_text(json.dumps(rec, indent=1) + "\n")
    print(f"{n} ticks -> {digest}")

    if args.compare:
        prev = json.loads(args.compare.read_text())
        same_trace = prev["state_trace_sha256"] == digest
        same_bin = (prev["binding"]["artifacts"][0]["sha256"]
                    == rec["binding"]["artifacts"][0]["sha256"])
        print(f"binding bytes changed: {not same_bin}")
        print(f"state trace identical: {same_trace}")
        if not same_trace:
            print("DYNAMICS MOVED — a rebuild changed what the instrument "
                  "measures; do not carry banked numbers across it")
            sys.exit(1)
        if same_bin:
            print("NOTE: the binding did not change, so this proves nothing "
                  "about a rebuild — did maturin actually run?")
            sys.exit(2)
        print("CONTINUOUS: new binding, identical dynamics")


if __name__ == "__main__":
    main()
