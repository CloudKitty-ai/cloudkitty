"""Tokenizer: obs schema 6 (flat 399, spec 058 layout) -> entity tokens.
Delta from schema 5: the clock token is gone (six token types), self
85->109 (walls, identity block, waypoint bearing, dirt reserve), kitty
rows 4x63 -> 4x58 (five-of-six row visibility), critter slots 4 -> 2
(#445 trim). Padding rule unchanged (numpy_forward_v6): self is never
padding; every other token pads iff its whole feature row is zero (a
HEARD kitty row has present 0 but live cells — padding it would deafen
the policy). Layout constants come from obs_layout_v6, never restated
here.
"""
import torch

from obs_layout_v6 import COUNTS, OBS_DIM, WIDTHS

_W = dict(WIDTHS)
SELF_F = _W["self"]
N_KITTY, KITTY_F = COUNTS["kitty"], _W["kitty"]
N_CHOW, CHOW_F = COUNTS["chow"], _W["chow"]
N_WATER, WATER_F = COUNTS["water"], _W["water"]
N_SUN, SUN_F = COUNTS["sunbeam"], _W["sunbeam"]
N_CRIT, CRIT_F = COUNTS["critter"], _W["critter"]
assert OBS_DIM == 399

_BOUNDS = {}
_o = 0
for name, f in WIDTHS:
    n = COUNTS[name]
    _BOUNDS[name] = (_o, _o + n * f, n, f)
    _o += n * f
assert _o == OBS_DIM


def tokenize_obs(obs):
    assert obs.ndim == 2 and obs.shape[1] == OBS_DIM, obs.shape
    toks, pads = {}, {}
    for name, (a, b, n, f) in _BOUNDS.items():
        t = obs[:, a:b].reshape(-1, n, f)
        toks[name] = t
        if name == "self":
            pads[name] = torch.zeros(t.shape[0], n, dtype=torch.bool,
                                     device=t.device)
        else:
            pads[name] = ~(t != 0.0).any(-1)
    return toks, pads
