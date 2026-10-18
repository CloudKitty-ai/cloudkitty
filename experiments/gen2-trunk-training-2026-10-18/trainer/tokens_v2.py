"""Tokenizer: global state v2 (flat 237) -> entity tokens.

Layout (crates/cloudkitty-rl/src/global_state.rs, schema 2 — spec 058
FR-009): per kitty in stable id order, 40 features — needs (6),
happiness (1), position (2), activity one-hot (7), social flag (1),
partner present + index (2), progress (1), distress flags (6), the
identity block (14: need-rate multipliers 6, comfort slack /40, consent
line /100, favourite weights 6) — then per element type (water, chow,
bug, greeble, sunbeam) 7 features: count + 2 center-nearest as
(present, x, y); then total chow servings (1) and the episode clock
(1). Delta from v1 (attn-critic-2026-08-12/tokens.py): the kitty
block's traits (6) grew into the identity block (14), 32 -> 40.

Gen 2 trains on the served roster only (5 seats, ruled staging), so the
width is always 237 and no padding applies. Vacant-row padding keys on
exact-zero rows as before (a live kitty always has nonzero happiness).
"""
import numpy as np
import torch

N_KITTY, KITTY_F = 5, 40
N_ELEM, ELEM_F = 5, 7
GLOBAL_F = 2
STATE_DIM = N_KITTY * KITTY_F + N_ELEM * ELEM_F + GLOBAL_F  # 237


def tokenize(states):
    """(N, 237) -> (kitty (N,5,40), elem (N,5,7), glob (N,1,2), pad (N,5))."""
    s = torch.as_tensor(np.asarray(states, dtype=np.float32))
    assert s.ndim == 2 and s.shape[1] == STATE_DIM, s.shape
    split = N_KITTY * KITTY_F
    k = s[:, :split].reshape(-1, N_KITTY, KITTY_F)
    e = s[:, split:split + N_ELEM * ELEM_F].reshape(-1, N_ELEM, ELEM_F)
    g = s[:, -GLOBAL_F:].reshape(-1, 1, GLOBAL_F)
    pad = k.abs().sum(dim=2) == 0.0
    return k, e, g, pad
