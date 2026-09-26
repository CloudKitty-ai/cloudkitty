#!/usr/bin/env python3
"""Enrichment-bonus screen trainer (PREREG.md, 2026-09-26): the beam
trainer's install pattern with this screen's slots, plus the BONUS
channel -- the Gen 3 free-time prototype. Nothing in the PPO loop, the
stop rules, the probe cadence or the manifest changes; the wrapper
recomposes `buf["reward"]` in place between collection and GAE.

The channel, per world-tick, from each cat's OWN observation (self
block, schema 5): a glow stock E rises while the cat is Playing and
decays otherwise; a need-space gate g ramps off the cat's WORST gate
need (Eat, Drink, Sleep, Cuddle, Bath -- Play excluded); the bonus
b = beta * E * g enters each cat's happiness BEFORE the Nash mean:

  reward += W(h + b) - W(h),   W(x) = exp(mean ln(x + eps)) - eps

so the term is the exact team-welfare lift the engine would report if
happiness carried the bonus -- positive only, gated per cat, worthless
at low welfare by arithmetic AND gate (the owner's operating-range
correction, 2026-09-26).

    experiments/exp-006-character-gen/.venv/bin/python \\
        experiments/enrichment-bonus-screen-2026-09-26/trainer/train_ppo_enrich.py --slot bonus-s1
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

# Self-block offsets (observe.rs schema 5): the five gate needs (Eat,
# Drink, Sleep, Cuddle, Bath; Play=3 excluded), own happiness, the
# Playing cell of the activity one-hot. Guarded semantically by
# ../test_enrich_term.py against an independent state-side derivation.
GATE_OBS = (0, 1, 2, 4, 5)
HAP_OBS = 6
ACT_PLAY = 14
# PREREG pins (2026-09-26; measured bases in PREREG.md §Calibration):
# ramp 15->25 on the worst gate need (x100: full bonus at <=15, zero at
# >=25; the gen1-A p50/p90), beta 0.03 full / 0.015 dose, glow gain
# 0.25 per playing tick capped at 1, decay 0.005 (half-life ~139
# ticks), reward eps 0.01 (rl.reward default).
THETA_LO, THETA_HI = 0.15, 0.25
BETA, BETA_LO = 0.03, 0.015
GAIN, DECAY = 0.25, 0.005
EPS, TERM_FLOOR = 0.01, 1e-4

_idx = 65
for _slot_beta, _s in (("bonus", 1), ("bonus", 2), ("bonus-lo", 1), ("bonus-lo", 2)):
    slot = f"{_slot_beta}-s{_s}"
    tb.WORLD[slot] = ((3.0, 7.0, 3000, 6), BEAM / "package.toml")
    tb.SLOTS[slot] = ("pin", "beta_low", "init_lesson", _s, _idx)
    _idx += 1

ES = {"E": None}


def nash(x, valid):
    """The engine's welfare aggregate (reward.rs, p=0): per world, the
    geometric mean of (x + eps) over valid seats, minus eps."""
    xv = np.where(valid, np.maximum(x + EPS, TERM_FLOOR), 1.0)
    n = np.maximum(valid.sum(-1), 1)
    return np.exp(np.log(xv).sum(-1) / n) - EPS


def enrich_terms(buf, beta, E0):
    """The bonus term per (t, world), from the obs, with the glow stock
    carried forward IN E0's copy; returns (terms, E_final, stats).
    Pure: reads buf, writes nothing."""
    obs, valid, trunc = buf["obs"], buf["valid"], buf["trunc"]
    T = obs.shape[0]
    E = E0.copy()
    gate_idx = np.array(GATE_OBS)
    out = np.zeros((T, obs.shape[1]))
    e_sum = g_sum = play_sum = term_sum = 0.0
    n_ct = 0
    for t in range(T):
        v = valid[t]
        playing = v & (obs[t, :, :, ACT_PLAY] > 0.5)
        worst = obs[t][:, :, gate_idx].max(-1).astype(np.float64)
        g = np.clip((THETA_HI - worst) / (THETA_HI - THETA_LO), 0.0, 1.0)
        E = np.where(playing, np.minimum(1.0, E + GAIN), E * (1.0 - DECAY))
        b = beta * E * g
        h = obs[t, :, :, HAP_OBS].astype(np.float64)
        out[t] = nash(h + b, v) - nash(h, v)
        e_sum += float(E[v].sum())
        g_sum += float(g[v].sum())
        play_sum += float(playing.sum())
        n_ct += int(v.sum())
        # A truncated world resets (fresh world, fresh cats): the glow
        # resets with it, after the tick it closes.
        E[trunc[t]] = 0.0
    term_sum = float(out.mean())
    stats = {"mean_E": e_sum / max(1, n_ct), "mean_g": g_sum / max(1, n_ct),
             "play_share": play_sum / max(1, n_ct), "mean_term": term_sum}
    return out, E, stats


def install_enrich(slot):
    beta = BETA_LO if slot.startswith("bonus-lo") else BETA
    trace = SCREEN / "artifacts" / f"ppo-fog-{slot}" / "enrich-trace.jsonl"
    orig = tf.collect_fragment
    state = {"update": 0}

    def collect_enriched(runner, policy, critic, vstats, T):
        out = orig(runner, policy, critic, vstats, T)
        buf = out[0]
        if ES["E"] is None or ES["E"].shape != buf["valid"].shape[1:]:
            ES["E"] = np.zeros(buf["valid"].shape[1:])
        terms, ES["E"], stats = enrich_terms(buf, beta, ES["E"])
        buf["reward"] += terms
        state["update"] += 1
        trace.parent.mkdir(parents=True, exist_ok=True)
        with trace.open("a") as f:
            f.write(json.dumps({"update": state["update"], "beta": beta, **stats}) + "\n")
        return out

    tf.collect_fragment = collect_enriched


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    slot = argv[argv.index("--slot") + 1]
    tb.CURRENT["slot"] = slot
    tb.install()
    tf.SHAKEOUT = SCREEN  # artifacts/ppo-fog-<slot> under this screen's directory
    install_enrich(slot)
    sys.argv = [sys.argv[0]] + argv
    tf.main()


if __name__ == "__main__":
    main()
