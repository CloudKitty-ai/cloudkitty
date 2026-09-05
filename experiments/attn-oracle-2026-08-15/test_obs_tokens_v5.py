"""Guard for obs_tokens_v5 (plain asserts, no pytest).

    .venv/bin/python test_obs_tokens_v5.py [trace_obs.npy]

With a bc-collect `--trace` obs file the last test proves the fog row
states are actually emitted (F-029: an absent category is not evidence
until the instrument can emit it).
"""
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from obs_layout_v5 import BLOCKS, KITTY_SPAN, KITTY_W, OBS_DIM  # noqa: E402
from obs_tokens_v5 import _BOUNDS, tokenize_obs  # noqa: E402

# Kitty-row offsets by name from the engine (observe.rs::offsets).
ROW_PRESENT, ROW_DX, ROW_MSG_BLOCK = 0, 1, 23


def kitty_row(obs, k):
    a = KITTY_SPAN[0] + k * KITTY_W
    return obs[:, a:a + KITTY_W]


def test_bounds_tile_the_observation():
    # red: drop a name from WIDTHS -> the last bound ends short of OBS_DIM
    ends = sorted(b for (_a, b, _n, _f) in _BOUNDS.values())
    starts = sorted(a for (a, _b, _n, _f) in _BOUNDS.values())
    assert starts[0] == 0 and ends[-1] == OBS_DIM
    assert ends[:-1] == starts[1:], "gaps or overlaps between token groups"
    a, _b, n, f = _BOUNDS["kitty"]
    assert (a, n * f) == (KITTY_SPAN[0], KITTY_SPAN[1] - KITTY_SPAN[0])
    assert [(a, f) for (a, f) in BLOCKS[:4]] == [
        (KITTY_SPAN[0] + k * KITTY_W, KITTY_W) for k in range(4)]


def test_heard_row_is_not_padded():
    # red: pad on `present <= 0` (the schema-4 rule) -> heard row pads
    obs = torch.zeros(1, OBS_DIM)
    row = kitty_row(obs, 1)
    row[0, ROW_PRESENT] = 0.0            # heard: present 0 ...
    row[0, ROW_DX] = 0.25                # ... dx/dy to the last call ...
    row[0, ROW_MSG_BLOCK] = 0.9          # ... and a live message block
    _toks, pads = tokenize_obs(obs)
    assert pads["kitty"][0].tolist() == [True, False, True, True]


def test_silent_and_vacant_rows_pad():
    # red: pad = zeros -> silent rows attend
    obs = torch.zeros(2, OBS_DIM)
    kitty_row(obs, 0)[0, ROW_PRESENT] = 1.0   # seen in sample 0 only
    _toks, pads = tokenize_obs(obs)
    assert pads["kitty"].tolist() == [[False, True, True, True],
                                      [True, True, True, True]]
    for name in ("chow", "water", "sunbeam", "critter"):
        assert pads[name].all(), name


def test_self_and_clock_never_pad():
    # red: pad self on all-zero -> a fresh reset row (all zero) pads
    obs = torch.zeros(3, OBS_DIM)
    _toks, pads = tokenize_obs(obs)
    assert not pads["self"].any() and not pads["clock"].any()


def test_tokens_are_views_of_the_flat_row():
    # red: reshape with wrong (n, f) -> token 2 no longer equals row 2
    obs = torch.arange(OBS_DIM, dtype=torch.float32).unsqueeze(0)
    toks, _pads = tokenize_obs(obs)
    assert torch.equal(toks["kitty"][0, 2], kitty_row(obs, 2)[0])
    assert toks["clock"][0, 0, 0] == OBS_DIM - 1


def test_emits_all_three_row_states(trace_obs):
    # F-029 emit-proof on a real trace: seen, heard and silent rows all
    # occur, and the pad follows the state.
    obs = torch.from_numpy(np.load(trace_obs).astype(np.float32))
    _toks, pads = tokenize_obs(obs)
    rows = obs[:, KITTY_SPAN[0]:KITTY_SPAN[1]].reshape(-1, 4, KITTY_W)
    present = rows[..., ROW_PRESENT] > 0
    live = (rows != 0).any(-1)
    seen, heard, silent = present, live & ~present, ~live
    print(f"  rows: seen {int(seen.sum())} heard {int(heard.sum())} "
          f"silent {int(silent.sum())}")
    assert seen.any() and heard.any() and silent.any()
    assert torch.equal(pads["kitty"], silent)


if __name__ == "__main__":
    trace = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_"):
            continue
        if name == "test_emits_all_three_row_states":
            if trace is None:
                print(f"skip {name} (no trace_obs.npy given)")
                continue
            fn(trace)
        else:
            fn()
        print(f"ok {name}")
