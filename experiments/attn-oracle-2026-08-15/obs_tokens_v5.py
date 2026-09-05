"""Tokenizer: obs schema 5 (flat 408, spec 049 layout) -> entity tokens.
Delta from schema 4: self 34->85 (scene age, message block, element
memory), kitty rows 3x20 -> 4x63 (fog row states, message block, want,
answers-me, water + on-sunbeam bits), and the 15 message-kind tokens are
gone (repetition rides the kitty rows). Seven token types remain.
Layout constants come from obs_layout_v5, never restated here.
"""
import torch

from obs_layout_v5 import COUNTS, OBS_DIM, WIDTHS

_W = dict(WIDTHS)
SELF_F = _W["self"]
N_KITTY, KITTY_F = COUNTS["kitty"], _W["kitty"]
N_CHOW, CHOW_F = COUNTS["chow"], _W["chow"]
N_WATER, WATER_F = COUNTS["water"], _W["water"]
N_SUN, SUN_F = COUNTS["sunbeam"], _W["sunbeam"]
N_CRIT, CRIT_F = COUNTS["critter"], _W["critter"]
CLOCK_F = _W["clock"]
assert OBS_DIM == 408

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
        if name in ("self", "clock"):
            pads[name] = torch.zeros(t.shape[0], n, dtype=torch.bool,
                                     device=t.device)
        else:
            # Schema 4 padded on `present <= 0`. Under fog (spec 049,
            # FR-012) a HEARD kitty row has present 0 but a live message
            # block and dx/dy to the last call; padding it would deafen
            # the policy. Pad only rows that are entirely zero (Silent
            # friends, vacant slots). Element slots are unchanged by this:
            # a filled slot always has present 1.
            pads[name] = ~(t != 0.0).any(-1)
    return toks, pads
