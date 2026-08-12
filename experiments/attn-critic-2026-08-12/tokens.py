"""Tokenizer: global state v1 (flat 197) -> entity tokens.

Layout (crates/cloudkitty-rl/src/global_state.rs, padded to 5 kitties by
exp-002's pad_states): per kitty in stable id order, 32 features — needs
(6), happiness (1), position (2), activity one-hot (7), social flag (1),
partner present + index (2), progress (1), distress flags (6), traits
(6) — then per element type (water, chow, bug, greeble, sunbeam) 7
features: count + 2 center-nearest as (present, x, y); then total chow
servings (1) and the episode clock (1).

Vacant kitty blocks are exact zero rows (pad_states writes zeros; a live
kitty always has nonzero happiness/traits), which is what the padding
mask keys on.
"""
import numpy as np
import torch

N_KITTY, KITTY_F = 5, 32
N_ELEM, ELEM_F = 5, 7
GLOBAL_F = 2
STATE_DIM = N_KITTY * KITTY_F + N_ELEM * ELEM_F + GLOBAL_F  # 197


def tokenize(states):
    """(N, 197) -> (kitty (N,5,32), elem (N,5,7), glob (N,1,2), pad (N,5))."""
    s = torch.as_tensor(np.asarray(states, dtype=np.float32))
    assert s.ndim == 2 and s.shape[1] == STATE_DIM, s.shape
    split = N_KITTY * KITTY_F
    k = s[:, :split].reshape(-1, N_KITTY, KITTY_F)
    e = s[:, split:split + N_ELEM * ELEM_F].reshape(-1, N_ELEM, ELEM_F)
    g = s[:, -GLOBAL_F:].reshape(-1, 1, GLOBAL_F)
    pad = k.abs().sum(dim=2) == 0.0
    return k, e, g, pad
