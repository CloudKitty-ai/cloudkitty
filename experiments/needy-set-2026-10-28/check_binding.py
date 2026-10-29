#!/usr/bin/env python3
"""Guard n3 (DECLARATION.md §10): the arc binding reproduces the
certified engine. The needy venv runs rot2 on L seed 905001 for 2,000
ticks (the one covered run in §11 step 2: 10,000 covered cat-ticks, no
needy seat, the certified five-network composition) and every recorded
array equals the first 2,000 ticks of Phase 1's L stream for that seed,
collected 2026-10-22 on the Phase 1 arc binding (a2e8d044).

    check_binding.py collect     # the covered run -> results-raw/binding-check/streams-905001.npz
    check_binding.py compare     # pure: fresh vs reference, exit 1 on any difference

The two halves are separate so the rule-5 red (REF_SEED pointed at
another seed's stream) cycles the compare alone and burns nothing.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "seating-analysis-g2-2026-10-21"))

SEED, TICKS = 905001, 2000
REF_SEED = 905001
REF = HERE.parent / "minifriend-phase1-2026-10-22" / "results-raw" / "L"
FRESH = HERE / "results-raw" / "binding-check" / f"streams-{SEED}.npz"
SEATING = "g2-rot2"


def collect():
    import seating_collect_g2 as C
    import torch
    torch.set_num_threads(1)
    arrays, meta = C.collect(SEATING, SEED, TICKS, 1000, config=C.CONFIG, save_obs=True)
    FRESH.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(FRESH, meta=json.dumps(meta), **arrays)
    print(f"wrote {FRESH}: {meta['ticks']} ticks, binding {meta['provenance']['binding_engine']}")


def compare(fresh_path=FRESH, ref_path=None):
    ref_path = ref_path or REF / f"streams-{REF_SEED}.npz"
    fresh, ref = np.load(fresh_path), np.load(ref_path)
    fm, rm = json.loads(str(fresh["meta"])), json.loads(str(ref["meta"]))
    print(f"fresh {fresh_path.name} seed {fm['seed']} binding {fm['provenance']['binding_engine'][:8]} | "
          f"reference {ref_path.name} seed {rm['seed']} binding {rm['provenance']['binding_engine'][:8]}")
    assert fm["seats"] == rm["seats"] and fm["config"] == rm["config"], (fm["seats"], rm["seats"])
    assert fm["ticks"] == TICKS and rm["ticks"] >= TICKS and fm["aborted_at"] is None
    keys = [k for k in ref.files if k != "meta"]
    assert set(keys) == set(k for k in fresh.files if k != "meta"), (keys, fresh.files)
    bad = []
    for k in sorted(keys):
        a, b = fresh[k], ref[k]
        if a.ndim and a.shape[0] == TICKS and b.shape[0] >= TICKS and k not in ("needs0", "hap0"):
            b = b[:TICKS]
        same = a.shape == b.shape and a.dtype == b.dtype and np.array_equal(a, b)
        print(f"  {k:13s} {str(a.shape):18s} {'equal' if same else 'DIFFERS'}")
        if not same:
            bad.append(k)
    if bad:
        print(f"n3 FAIL: {bad} differ from the certified stream (seed {rm['seed']})")
        return False
    print(f"n3 PASS: every array equals the first {TICKS} ticks of the certified stream, seed {rm['seed']}")
    return True


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "compare"
    if cmd == "collect":
        collect()
    elif cmd == "compare":
        sys.exit(0 if compare() else 1)
    else:
        sys.exit(f"usage: {sys.argv[0]} collect|compare")
