#!/usr/bin/env python3
"""Enrichment-decay sweep trainer (stage A; PREREG.md, 2026-09-26):
the bonus channel of the enrichment-bonus screen with the owner's
need-proportional decay curve added, the impact gate kept as the
backstop (her word: "keep+add"), and the glow split into open- and
closed-earned parts so the trace reads banking directly.

Per cat, from its OWN observation (schema-5 self block):

  W  = worst gate need (max of Eat, Drink, Sleep, Cuddle, Bath)
  g  = impact gate, clamp((0.25 - W)/0.10, 0, 1)  [unchanged backstop]
  d(W) = D_MIN + clamp((W - 0.15)/0.10, 0, 1) * (D_MAX - D_MIN)
  E  = E_open + E_closed; a playing tick adds GAIN (capped so E <= 1)
       to E_open when g > 0, else to E_closed; both parts decay by
       d(W) per non-playing tick
  b  = BETA * E * g;  reward += W_nash(h + b) - W_nash(h)

D_MIN / D_MAX come from the slot name (stage A corners): d25-250,
d25-1000, d100-250, d100-1000 = {0.25%, 1%} x {2.5%, 10%} per tick.

    experiments/exp-006-character-gen/.venv/bin/python \\
        experiments/enrichment-decay-sweep-2026-09-26/trainer/train_ppo_enrich2.py --slot d25-250-s1
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

GATE_OBS = (0, 1, 2, 4, 5)
HAP_OBS = 6
ACT_PLAY = 14
# PREREG pins (2026-09-26): gate ramp and decay brackets both 15->25 in
# stage A (stage B moves the decay brackets only); beta and gain carried
# from the enrichment-bonus screen (owner: "We can always sweep B and E
# before gen 3").
THETA_LO, THETA_HI = 0.15, 0.25
BETA, GAIN = 0.03, 0.25
EPS, TERM_FLOOR = 0.01, 1e-4

# Stage A corners: (D_MIN, D_MAX) per tick, slot-named in basis points.
CORNERS = {"d25-250": (0.0025, 0.025), "d25-1000": (0.0025, 0.10),
           "d100-250": (0.01, 0.025), "d100-1000": (0.01, 0.10)}

_idx = 69
for _c in CORNERS:
    for _s in (1, 2):
        slot = f"{_c}-s{_s}"
        tb.WORLD[slot] = ((3.0, 7.0, 3000, 6), BEAM / "package.toml")
        tb.SLOTS[slot] = ("pin", "beta_low", "init_lesson", _s, _idx)
        _idx += 1

ES = {"Eo": None, "Ec": None}


def nash(x, valid):
    xv = np.where(valid, np.maximum(x + EPS, TERM_FLOOR), 1.0)
    n = np.maximum(valid.sum(-1), 1)
    return np.exp(np.log(xv).sum(-1) / n) - EPS


def enrich2_terms(buf, d_min, d_max, Eo0, Ec0):
    """The decay-curve bonus term per (t, world), from the obs, with the
    split glow carried forward in copies of Eo0/Ec0; returns
    (terms, Eo, Ec, stats). Pure: reads buf, writes nothing."""
    obs, valid, trunc = buf["obs"], buf["valid"], buf["trunc"]
    T = obs.shape[0]
    Eo, Ec = Eo0.copy(), Ec0.copy()
    gate_idx = np.array(GATE_OBS)
    out = np.zeros((T, obs.shape[1]))
    e_sum = g_sum = play_sum = 0.0
    pay_sum = pay_banked = 0.0
    n_ct = 0
    for t in range(T):
        v = valid[t]
        playing = v & (obs[t, :, :, ACT_PLAY] > 0.5)
        worst = obs[t][:, :, gate_idx].max(-1).astype(np.float64)
        g = np.clip((THETA_HI - worst) / (THETA_HI - THETA_LO), 0.0, 1.0)
        d = d_min + np.clip((worst - THETA_LO) / (THETA_HI - THETA_LO), 0.0, 1.0) * (d_max - d_min)
        # A playing tick earns GAIN into the bucket the gate says it is
        # in (open: g > 0), capped so Eo + Ec never exceeds 1; a
        # non-playing tick decays both buckets by d(W).
        room = np.maximum(0.0, 1.0 - (Eo + Ec))
        add = np.where(playing, np.minimum(GAIN, room), 0.0)
        Eo = np.where(playing, Eo + np.where(g > 0.0, add, 0.0), Eo * (1.0 - d))
        Ec = np.where(playing, Ec + np.where(g > 0.0, 0.0, add), Ec * (1.0 - d))
        E = Eo + Ec
        b = BETA * E * g
        h = obs[t, :, :, HAP_OBS].astype(np.float64)
        out[t] = nash(h + b, v) - nash(h, v)
        pay = BETA * g * E
        pay_sum += float(pay[v].sum())
        pay_banked += float((BETA * g * Ec)[v].sum())
        e_sum += float(E[v].sum())
        g_sum += float(g[v].sum())
        play_sum += float(playing.sum())
        n_ct += int(v.sum())
        Eo[trunc[t]] = 0.0
        Ec[trunc[t]] = 0.0
    stats = {"mean_E": e_sum / max(1, n_ct), "mean_g": g_sum / max(1, n_ct),
             "play_share": play_sum / max(1, n_ct), "mean_term": float(out.mean()),
             "banked_payout_share": (pay_banked / pay_sum) if pay_sum > 0 else 0.0}
    return out, Eo, Ec, stats


def install_enrich2(slot):
    corner = slot.rsplit("-s", 1)[0]
    d_min, d_max = CORNERS[corner]
    trace = SCREEN / "artifacts" / f"ppo-fog-{slot}" / "enrich2-trace.jsonl"
    orig = tf.collect_fragment
    state = {"update": 0}

    def collect_enriched(runner, policy, critic, vstats, T):
        out = orig(runner, policy, critic, vstats, T)
        buf = out[0]
        if ES["Eo"] is None or ES["Eo"].shape != buf["valid"].shape[1:]:
            ES["Eo"] = np.zeros(buf["valid"].shape[1:])
            ES["Ec"] = np.zeros(buf["valid"].shape[1:])
        terms, ES["Eo"], ES["Ec"], stats = enrich2_terms(buf, d_min, d_max, ES["Eo"], ES["Ec"])
        buf["reward"] += terms
        state["update"] += 1
        trace.parent.mkdir(parents=True, exist_ok=True)
        with trace.open("a") as f:
            f.write(json.dumps({"update": state["update"], "d_min": d_min,
                                "d_max": d_max, **stats}) + "\n")
        return out

    tf.collect_fragment = collect_enriched


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    slot = argv[argv.index("--slot") + 1]
    tb.CURRENT["slot"] = slot
    tb.install()
    tf.SHAKEOUT = SCREEN
    install_enrich2(slot)
    sys.argv = [sys.argv[0]] + argv
    tf.main()


if __name__ == "__main__":
    main()
