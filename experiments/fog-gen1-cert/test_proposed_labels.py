#!/usr/bin/env python3
"""Guard for bc-collect's `label_msg_proposed.npy` (plain asserts).

    test_proposed_labels.py NEW_ROLLOUT_DIR [OLD_ROLLOUT_DIR]

On a recorded rollout: the proposed file exists with the row count;
a downgrade only ever goes to Silent (applied != Silent implies
proposed == applied); every proposed label is legal under the
start-of-tick message mask; and at least one row was downgraded (the
whole reason the file exists; a collector that wrote the applied
label twice fails here). With OLD_ROLLOUT_DIR (the same seed, config
and ticks recorded by the previous tool): every pre-existing file is
byte-identical, so the running clones' data did not move.
"""
import sys
from pathlib import Path

import numpy as np

new = Path(sys.argv[1])
old = Path(sys.argv[2]) if len(sys.argv) > 2 else None

applied = np.load(new / "label_msg.npy")
proposed = np.load(new / "label_msg_proposed.npy")
mask_msg = np.load(new / "mask_msg.npy").astype(bool)
n = len(applied)
assert proposed.shape == (n,) and proposed.dtype == applied.dtype, (proposed.shape, proposed.dtype)
spoke = applied != 0
assert (proposed[spoke] == applied[spoke]).all(), "an applied word must be the proposed word"
assert mask_msg[np.arange(n), proposed].all(), "a proposed label outside the start-of-tick mask"
down = int((proposed != applied).sum())
assert down > 0, "no downgraded row: the proposed file repeats the applied labels"
meta = (new / "meta.json").read_text()
assert f'"msg_downgraded": {down}' in meta, "meta.json msg_downgraded disagrees with the file"
print(f"proposed labels ok: {n} rows, {down} downgraded to Silent at apply")

if old is not None:
    for f in ("obs", "mask", "label", "mask_msg", "label_msg", "kitty", "tick", "reward", "state"):
        a, b = (new / f"{f}.npy").read_bytes(), (old / f"{f}.npy").read_bytes()
        assert a == b, f"{f}.npy moved between the two collectors"
    print("pre-existing files byte-identical to the previous collection")
