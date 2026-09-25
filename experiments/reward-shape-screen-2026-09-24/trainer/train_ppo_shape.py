#!/usr/bin/env python3
"""Reward-shape screen trainer (PREREG.md, frozen 2026-09-24): the beam
trainer's install pattern with this screen's slots, plus an
objective-side counterfactual-floor term. Nothing in the PPO loop, the
stop rules, the probe cadence or the manifest changes; the wrapper
shapes `buf["reward"]` in place between collection and GAE.

The counterfactual state is read from each cat's OWN observation --
self sleep need, the sleeping one-hot, the in-sunbeam bit (schema-5
self-block offsets, guarded by ../test_shape_term.py against an
independent state-side derivation). The term (per world-tick, mean
over valid seats):

  hard: C1 * 1[asleep, off-beam, need < 15]
  cvx:  C2 * 1[...] * ((0.15 - need)/0.15)^2
  lam:  lambda * 1[...]; lambda <- clamp(lambda + ETA*(mean_cf - D), 0, 5)
        after each fragment, traced to artifacts/<slot>/shape-trace.jsonl

    experiments/exp-006-character-gen/.venv/bin/python \\
        experiments/reward-shape-screen-2026-09-24/trainer/train_ppo_shape.py --slot hard-s1
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SCREEN = HERE.parent
EXPTS = SCREEN.parent
BEAM = EXPTS / "beam-world-screen-2026-09-19"
sys.path.insert(0, str(BEAM / "trainer"))
sys.path.insert(0, str(BEAM))
sys.path.insert(0, str(EXPTS / "fog-gen1-shakeout" / "trainer"))
import train_ppo_beam as tb  # noqa: E402
import train_ppo_fog as tf  # noqa: E402

# Self-block offsets (observe.rs schema 5): sleep need, the sleeping cell
# of the activity one-hot, the in-sunbeam bit. Guarded semantically.
SLEEP_NEED, ACT_SLEEP, IN_SUNBEAM = 2, 11, 17
# PREREG pins (frozen 2026-09-24; bases in PREREG.md).
C1, C2, D_TARGET, ETA, LAM_CLAMP, FLOOR = 0.6, 1.0, 0.06, 0.05, 5.0, 0.15

SHAPES = ("hard", "cvx", "lam")
_idx = 59
for _shape in SHAPES:
    for _s in (1, 2):
        slot = f"{_shape}-s{_s}"
        tb.WORLD[slot] = ((3.0, 7.0, 3000, 6), BEAM / "package.toml")
        tb.SLOTS[slot] = ("pin", "beta_low", "init_lesson", _s, _idx)
        _idx += 1

LAM = {"lam": 0.0, "update": 0}


def cf_fields(obs, valid):
    """Per-seat counterfactual indicator and squared depth, from the obs."""
    need = obs[..., SLEEP_NEED]
    cf = valid & (obs[..., ACT_SLEEP] > 0.5) & (obs[..., IN_SUNBEAM] < 0.5) & (need < FLOOR)
    depth2 = np.where(cf, ((FLOOR - need) / FLOOR) ** 2, 0.0)
    return cf, depth2


def shape_rewards(buf, shape, lam_value):
    """Subtract the shape's term from buf["reward"] IN PLACE; returns
    (mean cf occupancy, mean term) over the fragment. shape None or
    "none" leaves the buffer untouched (bitwise) and returns zeros."""
    if shape in (None, "none"):
        return 0.0, 0.0
    cf, depth2 = cf_fields(buf["obs"], buf["valid"])
    n_valid = np.maximum(buf["valid"].sum(-1), 1)
    cf_mean = cf.sum(-1) / n_valid            # (T, n)
    if shape == "hard":
        term = C1 * cf_mean
    elif shape == "cvx":
        term = C2 * depth2.sum(-1) / n_valid
    elif shape == "lam":
        term = lam_value * cf_mean
    else:
        raise ValueError(shape)
    buf["reward"] -= term
    return float(cf_mean.mean()), float(term.mean())


def lam_step(lam_value, cf_mean):
    """One dual-ascent step (PREREG pins): the price rises while the
    fragment's occupancy exceeds the target, clamped to [0, LAM_CLAMP]."""
    return float(np.clip(lam_value + ETA * (cf_mean - D_TARGET), 0.0, LAM_CLAMP))


def install_shape(slot):
    shape = slot.split("-", 1)[0]
    assert shape in SHAPES, slot
    trace = SCREEN / "artifacts" / f"ppo-fog-{slot}" / "shape-trace.jsonl"
    orig = tf.collect_fragment

    def collect_shaped(runner, policy, critic, vstats, T):
        out = orig(runner, policy, critic, vstats, T)
        buf = out[0]
        lam_value = LAM["lam"]
        cf_mean, term_mean = shape_rewards(buf, shape, lam_value)
        if shape == "lam":
            LAM["lam"] = lam_step(LAM["lam"], cf_mean)
        LAM["update"] += 1
        trace.parent.mkdir(parents=True, exist_ok=True)
        with trace.open("a") as f:
            f.write(json.dumps({"update": LAM["update"], "shape": shape,
                                "lam": lam_value, "lam_next": LAM["lam"],
                                "mean_cf": cf_mean, "mean_term": term_mean}) + "\n")
        return out

    tf.collect_fragment = collect_shaped


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    slot = argv[argv.index("--slot") + 1]
    tb.CURRENT["slot"] = slot
    tb.install()
    tf.SHAKEOUT = SCREEN  # artifacts/ppo-fog-<slot> under this screen's directory
    install_shape(slot)
    sys.argv = [sys.argv[0]] + argv
    tf.main()


if __name__ == "__main__":
    main()
