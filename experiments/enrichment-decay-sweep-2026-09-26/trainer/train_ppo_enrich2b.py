#!/usr/bin/env python3
"""Enrichment-decay sweep, stage B trainer (PREREG-B.md, 2026-09-27):
the β response curve and the accrual-gate arm, all on the d100-1000
corner (D_MIN 1%, D_MAX 10%). Owner's rulings: β {0.06, 0.10, 0.14}
× three seeds ("Yes to 1 and 2"); the accrual-gate arm at β 0.10
("yes on 0.10"); brackets deferred to stage C ("stage C approved").

Differences from stage A's trainer:
- β varies by slot; the corner is fixed.
- The ag slots run the ACCRUAL GATE (the owner's original
  mechanism): closed-gate play earns NOTHING (E_closed gain = 0);
  the decay curve still applies to whatever glow exists.
- The trace gains the glow distribution (at-cap share, E median) so
  the read-glow-distribution-first condition is satisfiable from
  the record.

    experiments/exp-006-character-gen/.venv/bin/python \\
        experiments/enrichment-decay-sweep-2026-09-26/trainer/train_ppo_enrich2b.py --slot b10-s1
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
THETA_LO, THETA_HI = 0.15, 0.25
GAIN = 0.25
D_MIN, D_MAX = 0.01, 0.10
EPS, TERM_FLOOR = 0.01, 1e-4
AT_CAP = 0.95

# slot -> (beta, accrual_gate)
FAMS = {"b06": (0.06, False), "b10": (0.10, False), "b14": (0.14, False),
        "ag10": (0.10, True)}
SEEDS_PER = {"b06": 3, "b10": 3, "b14": 3, "ag10": 2}

_idx = 79
SLOT_PARAMS = {}
for _fam, (_beta, _ag) in FAMS.items():
    for _s in range(1, SEEDS_PER[_fam] + 1):
        slot = f"{_fam}-s{_s}"
        SLOT_PARAMS[slot] = (_beta, _ag)
        tb.WORLD[slot] = ((3.0, 7.0, 3000, 6), BEAM / "package.toml")
        tb.SLOTS[slot] = ("pin", "beta_low", "init_lesson", _s, _idx)
        _idx += 1

ES = {"Eo": None, "Ec": None}


def nash(x, valid):
    xv = np.where(valid, np.maximum(x + EPS, TERM_FLOOR), 1.0)
    n = np.maximum(valid.sum(-1), 1)
    return np.exp(np.log(xv).sum(-1) / n) - EPS


def enrich2b_terms(buf, beta, accrual_gate, Eo0, Ec0):
    """Stage-B bonus term per (t, world): β parameterized, optional
    accrual gate (closed-gate play earns nothing), glow-distribution
    stats. Pure: reads buf, writes nothing."""
    obs, valid, trunc = buf["obs"], buf["valid"], buf["trunc"]
    T = obs.shape[0]
    Eo, Ec = Eo0.copy(), Ec0.copy()
    gate_idx = np.array(GATE_OBS)
    out = np.zeros((T, obs.shape[1]))
    e_sum = g_sum = play_sum = 0.0
    pay_sum = pay_banked = 0.0
    cap_sum = 0.0
    e_all = []
    n_ct = 0
    for t in range(T):
        v = valid[t]
        playing = v & (obs[t, :, :, ACT_PLAY] > 0.5)
        worst = obs[t][:, :, gate_idx].max(-1).astype(np.float64)
        g = np.clip((THETA_HI - worst) / (THETA_HI - THETA_LO), 0.0, 1.0)
        d = D_MIN + np.clip((worst - THETA_LO) / (THETA_HI - THETA_LO), 0.0, 1.0) * (D_MAX - D_MIN)
        room = np.maximum(0.0, 1.0 - (Eo + Ec))
        add = np.where(playing, np.minimum(GAIN, room), 0.0)
        closed_add = np.where(g > 0.0, 0.0, add)
        if accrual_gate:
            closed_add = np.zeros_like(closed_add)
        Eo = np.where(playing, Eo + np.where(g > 0.0, add, 0.0), Eo * (1.0 - d))
        Ec = np.where(playing, Ec + closed_add, Ec * (1.0 - d))
        E = Eo + Ec
        b = beta * E * g
        h = obs[t, :, :, HAP_OBS].astype(np.float64)
        out[t] = nash(h + b, v) - nash(h, v)
        pay = beta * g * E
        pay_sum += float(pay[v].sum())
        pay_banked += float((beta * g * Ec)[v].sum())
        e_sum += float(E[v].sum())
        g_sum += float(g[v].sum())
        play_sum += float(playing.sum())
        cap_sum += float((E[v] >= AT_CAP).sum())
        e_all.append(E[v])
        n_ct += int(v.sum())
        Eo[trunc[t]] = 0.0
        Ec[trunc[t]] = 0.0
    e_cat = np.concatenate(e_all) if e_all else np.zeros(1)
    stats = {"mean_E": e_sum / max(1, n_ct), "mean_g": g_sum / max(1, n_ct),
             "play_share": play_sum / max(1, n_ct), "mean_term": float(out.mean()),
             "banked_payout_share": (pay_banked / pay_sum) if pay_sum > 0 else 0.0,
             "at_cap_share": cap_sum / max(1, n_ct),
             "E_p50": float(np.median(e_cat))}
    return out, Eo, Ec, stats


def install_enrich2b(slot):
    beta, ag = SLOT_PARAMS[slot]
    trace = SCREEN / "artifacts" / f"ppo-fog-{slot}" / "enrich2b-trace.jsonl"
    orig = tf.collect_fragment
    state = {"update": 0}

    def collect_enriched(runner, policy, critic, vstats, T):
        out = orig(runner, policy, critic, vstats, T)
        buf = out[0]
        if ES["Eo"] is None or ES["Eo"].shape != buf["valid"].shape[1:]:
            ES["Eo"] = np.zeros(buf["valid"].shape[1:])
            ES["Ec"] = np.zeros(buf["valid"].shape[1:])
        terms, ES["Eo"], ES["Ec"], stats = enrich2b_terms(buf, beta, ag, ES["Eo"], ES["Ec"])
        buf["reward"] += terms
        state["update"] += 1
        trace.parent.mkdir(parents=True, exist_ok=True)
        with trace.open("a") as f:
            f.write(json.dumps({"update": state["update"], "beta": beta,
                                "accrual_gate": ag, **stats}) + "\n")
        return out

    tf.collect_fragment = collect_enriched


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    slot = argv[argv.index("--slot") + 1]
    tb.CURRENT["slot"] = slot
    tb.install()
    tf.SHAKEOUT = SCREEN
    install_enrich2b(slot)
    sys.argv = [sys.argv[0]] + argv
    tf.main()


if __name__ == "__main__":
    main()
