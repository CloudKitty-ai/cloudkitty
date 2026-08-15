"""Tokenizer: obs schema 4 (flat 225, spec 033 layout) -> entity tokens.
Delta from schema 3: digest 8->15 kinds (HEAD_KINDS + Here*x4 + chirp,
trill, ekekek). Everything else unchanged.
"""
import torch

SELF_F = 34
N_KITTY, KITTY_F = 3, 20
N_CHOW, CHOW_F = 2, 5
N_WATER, WATER_F = 2, 4
N_SUN, SUN_F = 2, 6
N_CRIT, CRIT_F = 4, 10
N_MSG, MSG_F = 15, 4
CLOCK_F = 1

OBS_DIM = (SELF_F + N_KITTY * KITTY_F + N_CHOW * CHOW_F + N_WATER * WATER_F
           + N_SUN * SUN_F + N_CRIT * CRIT_F + N_MSG * MSG_F + CLOCK_F)
assert OBS_DIM == 225

_BOUNDS = {}
_o = 0
for name, n, f in (("self", 1, SELF_F), ("kitty", N_KITTY, KITTY_F),
                   ("chow", N_CHOW, CHOW_F), ("water", N_WATER, WATER_F),
                   ("sunbeam", N_SUN, SUN_F), ("critter", N_CRIT, CRIT_F),
                   ("msg", N_MSG, MSG_F), ("clock", 1, CLOCK_F)):
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
            pads[name] = t[:, :, 0] <= 0.0
    return toks, pads
