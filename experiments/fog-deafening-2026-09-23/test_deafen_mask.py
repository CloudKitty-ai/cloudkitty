"""Guards for `cert_harness_fog.deafen` (fog-deafening-2026-09-23).

Run: experiments/exp-006-character-gen/.venv/bin/python -B test_deafen_mask.py

Real payloads (rule 5): a 1,500-tick gen1-A run on anchor-b3 at probe
seed 40001, every policy observation captured pre-forward. Each arm's
mask is checked float-for-float against an INDEPENDENT reference mask
built from this file's own copies of the schema-5 layout constants
(observe.rs: SELF_BLOCK 85, KITTY_SLOT 63, message pairs at 23, want
intensities at 53, answers-me at 59) -- deliberately not imported from
the harness, so a constant typo on either side diverges and fails.
Non-vacuity is asserted on the run itself: heard speech, heard-only
rows and answers-me bits must all actually occur pre-mask.
"""
import sys
import tomllib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
import cert_harness_fog as H  # noqa: E402

# Independent layout copies (observe.rs schema 5) -- keep as literals.
SELF, SLOT, ROWS = 85, 63, 4
MSG, WANT, ANS, END = 23, 53, 59, 63
WANT_K = [0, 1, 3, 4, 6, 7]
HERE_K = [8, 9, 10, 11]
FREE_K = [2, 5, 12, 13, 14]
ARMS = {"want": (WANT_K, list(range(6)), []),
        "here": (HERE_K, [], list(range(4))),
        "free": (FREE_K, [], []),
        "all": (list(range(15)), list(range(6)), list(range(4))),
        "rows": None}
# The dir arm is tested separately at several R values; the world dims are
# read from the config here, independently of the harness's cfg plumbing.
import tomllib  # noqa: E402
with open(Path(__file__).resolve().parent.parent / "fog-gen1-cert" / "anchor-b3.toml", "rb") as _f:
    _cfg = tomllib.load(_f)
WH = (_cfg["world"]["width"], _cfg["world"]["height"])


def reference_mask(ob, arm, wh=None, dir_r=None):
    """The declared deafening, written independently of the harness."""
    out = ob.copy()
    if arm == "rows":
        for r in range(ROWS):
            row = SELF + r * SLOT
            heard = (out[:, row] == 0.0) & (out[:, row + 3] > 0.0)
            out[heard, row:row + SLOT] = 0.0
        return out
    if arm == "dir":
        width, height = wh
        for r in range(ROWS):
            row = SELF + r * SLOT
            heard = (out[:, row] == 0.0) & (out[:, row + 3] > 0.0)
            dx = out[heard, row + 1] * width
            dy = out[heard, row + 2] * height
            k = dir_r / (np.abs(dx) + np.abs(dy))
            out[heard, row + 1] = dx * k / width
            out[heard, row + 2] = dy * k / height
            out[heard, row + 3] = dir_r / (width + height)
        return out
    kinds, wants, heres = ARMS[arm]
    for r in range(ROWS):
        row = SELF + r * SLOT
        for k in kinds:
            out[:, row + MSG + 2 * k] = 0.0
            out[:, row + MSG + 2 * k + 1] = 0.0
        for w in wants:
            out[:, row + WANT + w] = 0.0
        for h in heres:
            out[:, row + ANS + h] = 0.0
        gone = ((out[:, row] == 0.0) & (out[:, row + 3] > 0.0)
                & (np.abs(out[:, row + MSG:row + END]).max(1) == 0.0))
        out[gone, row:row + SLOT] = 0.0
    return out


def collect(ticks=1500, seed=40001):
    import cloudkitty
    config = str(HERE.parent / "fog-gen1-cert" / "anchor-b3.toml")
    with open(config, "rb") as f:
        cfg = tomllib.load(f)
    seats = list(H.SEATINGS["gen1-A"])
    models = {s: H.load_model(s) for s in set(seats)}
    env = cloudkitty.ParallelEnv(config, horizon=ticks)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    seat_of = {f"kitty_{k['id']}": s for k, s in zip(cfg["kitty"], seats)}
    stacks = []
    for _t in range(ticks):
        ob = np.stack([np.asarray(obs[a], np.float32) for a in names])
        ob[:, H.CLOCK_INDEX] = 0.0
        stacks.append(ob.copy())
        mk = np.stack([np.asarray(infos[a]["mask"], np.uint8) for a in names]).astype(bool)
        lg = np.zeros((len(names), H.N_HEADS), np.float32)
        for s, fwd in models.items():
            rows = [i for i, a in enumerate(names) if seat_of[a] == s]
            lg[rows] = np.asarray(fwd(ob[rows], mk[rows]), np.float32)
        a0 = np.where(mk[:, :H.N_ACT], lg[:, :H.N_ACT], H.NEG_INF).argmax(1)
        g0 = np.where(mk[:, H.N_ACT:], lg[:, H.N_ACT:], H.NEG_INF).argmax(1)
        obs, _r, _te, _tr, infos = env.step({a: (int(a0[i]), int(g0[i])) for i, a in enumerate(names)})
    return stacks


def main():
    stacks = collect()
    msg_nonzero = heard_rows = heard_erased_all = answers_nonzero = 0
    for ob in stacks:
        for r in range(ROWS):
            row = SELF + r * SLOT
            m = ob[:, row + MSG:row + WANT]
            msg_nonzero += int((np.abs(m) > 0).sum())
            answers_nonzero += int((ob[:, row + ANS:row + END] > 0).sum())
            h = (ob[:, row] == 0.0) & (ob[:, row + 3] > 0.0) & (np.abs(ob[:, row + MSG:row + END]).max(1) > 0.0)
            heard_rows += int(h.sum())
        for arm in ARMS:
            want = reference_mask(ob, arm)
            got = ob.copy()
            H.deafen(got, arm)
            assert np.array_equal(got, want), f"deafen({arm}) diverges from the reference mask"
        for r_val in (5.0, 16.0, 37.0):
            want = reference_mask(ob, "dir", wh=WH, dir_r=r_val)
            got = ob.copy()
            H.deafen(got, "dir", (WH[0], WH[1], r_val))
            assert np.array_equal(got, want), f"deafen(dir R={r_val}) diverges from the reference mask"
            if arm == "all":
                for r in range(ROWS):
                    row = SELF + r * SLOT
                    assert np.abs(got[:, row + MSG:row + END]).max() == 0.0, "all-deaf leaves a message float"
                heard_erased_all += int(((ob[:, SELF::1] != got[:, SELF::1]).any()) and heard_rows > 0)
                assert np.array_equal(got[:, :SELF], ob[:, :SELF]), "all-deaf touched the self block"
                assert np.array_equal(got[:, SELF + ROWS * SLOT:], ob[:, SELF + ROWS * SLOT:]), "all-deaf touched element slots or the clock"
    assert msg_nonzero > 100, f"vacuous run: only {msg_nonzero} nonzero heard-message floats"
    assert heard_rows > 0, "vacuous run: no heard-only rows occurred"
    assert answers_nonzero > 0, "vacuous run: no answers-me bit ever set"
    print(f"ok: {len(stacks)} ticks; msg floats nonzero {msg_nonzero}, "
          f"heard rows {heard_rows}, answers-me set {answers_nonzero}")


if __name__ == "__main__":
    main()
