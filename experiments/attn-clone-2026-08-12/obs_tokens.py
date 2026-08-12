"""Tokenizer: obs schema 3 (flat 197, served slot config) -> entity tokens.

Layout (crates/cloudkitty-rl/src/observe.rs, slot config 3 kitty / 2 chow
/ 2 water / 2 sunbeam / 4 critter):

  self 34 | kitty 3x20 | chow 2x5 | water 2x4 | sunbeam 2x6
  | critter 4x10 | meow digest 8x4 (per HEAD_KINDS kind) | clock 1

Every slot's first feature is its presence flag (kitty/element slots) or
recency (message kinds); vacant slots are exact zero blocks — that is
the engine's own "absent" encoding, and it is what the padding masks
key on. Self and clock are always present.
"""
import torch

SELF_F = 34
N_KITTY, KITTY_F = 3, 20
N_CHOW, CHOW_F = 2, 5
N_WATER, WATER_F = 2, 4
N_SUN, SUN_F = 2, 6
N_CRIT, CRIT_F = 4, 10
N_MSG, MSG_F = 8, 4
CLOCK_F = 1

OBS_DIM = (SELF_F + N_KITTY * KITTY_F + N_CHOW * CHOW_F + N_WATER * WATER_F
           + N_SUN * SUN_F + N_CRIT * CRIT_F + N_MSG * MSG_F + CLOCK_F)
assert OBS_DIM == 197

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
    """(N, 197) tensor -> {name: (N, n, f)} plus {name: (N, n) bool pad}.

    Pads are True where the token is absent (vacant slot / silent kind);
    self and clock are never padded.
    """
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
