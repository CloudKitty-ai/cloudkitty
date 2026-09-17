#!/usr/bin/env python3
"""Add the message-head choice to a probe-format trace that lacks it:
the same masked argmax over logits[39:] the collecting loop used, with
the served artifacts (policies/fog-gen1-*.ckpolicy) per kitty index.

    add_msg.py IN_NPZ OUT_NPZ
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "attn-oracle-2026-08-15"))
from numpy_forward_v5 import load_artifact, numpy_forward  # noqa: E402

FILES = ["miso-cand-s2", "biscuit-cand-s1", "pumpkin-dose-lo-s1", "kittybear-cand-s4", "clementine-cand-s7"]
N_ACT = 39


def main():
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    z = np.load(src)
    obs, mask, kitty, act = z["obs"], z["mask"].astype(bool), z["kitty"], z["act"]
    msg = np.zeros(len(obs), int)
    for i, f in enumerate(FILES):
        pol = load_artifact(open(ROOT / "policies" / f"fog-gen1-{f}.ckpolicy", "rb").read())
        m = kitty == i
        lg = numpy_forward(pol, obs[m])
        a0 = np.where(mask[m][:, :N_ACT], lg[:, :N_ACT], -np.inf).argmax(1)
        assert (a0 == act[m]).all(), f"kitty {i}: activity head does not reproduce the trace's act"
        msg[m] = np.where(mask[m][:, N_ACT:], lg[:, N_ACT:], -np.inf).argmax(1)
    np.savez_compressed(dst, msg=msg, **{k: z[k] for k in z.files})
    print("rows", len(obs), "msg nonzero", int((msg != 0).sum()), "wrote", dst)


if __name__ == "__main__":
    main()
