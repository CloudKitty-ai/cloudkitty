#!/usr/bin/env python3
"""A17 probe read, pooled (#367 fix 1, owner ruled 2026-09-10).

The probe npz pools its worlds (PROBE_SEEDS trio), so the anchor side
must pool the matching bc-collect rollouts - a single-rollout anchor
misses rare events by luck and reds A17 for sampling, not wiring
(the #367 red). This driver only pools and delegates; the check and
the exemption logic stay schema_check's.

    parta_pool_a17.py POLICY_NPZ ANCHOR_ROLLOUT_DIR [DIR ...]
        [--declared-constant JSON]
"""
import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parents[0] / "attn-oracle-2026-08-15"))
from schema_check import check_a17, load_trace  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("policy_npz", type=Path)
    ap.add_argument("anchor_dirs", type=Path, nargs="+")
    ap.add_argument("--declared-constant", type=Path,
                    default=HERE / "declared_constant.json")
    args = ap.parse_args()

    declared = json.loads(args.declared_constant.read_text())
    pooled = SimpleNamespace(obs=np.concatenate(
        [load_trace(d, None).obs for d in args.anchor_dirs]))
    f = check_a17(pooled, args.policy_npz, declared)
    print(f"A17(pooled x{len(args.anchor_dirs)}) {f.status:<9} {f.summary}")
    for k in ("disagree", "rare_moved"):
        if f.detail.get(k):
            print(f"  {k}: {f.detail[k]}")
    sys.exit(1 if f.status == "RED" else 0)


if __name__ == "__main__":
    main()
