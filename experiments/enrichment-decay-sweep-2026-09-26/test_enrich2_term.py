"""Guards for the enrichment-decay trainer's channel (stage A).

    CERT_ARTS=experiments/enrichment-decay-sweep-2026-09-26/artifacts \
        experiments/exp-006-character-gen/.venv/bin/python -B \
        experiments/enrichment-decay-sweep-2026-09-26/test_enrich2_term.py

Real payloads: 1,200 ticks of the gen1-A seating on package.toml at
seed 900401 (this screen's band), captured as observations + engine
rewards. Guards:

1. enrich2_terms vs an independently coded reference — full-tick on
   BOTH corner extremes (d 0.25%/2.5% and 1%/10%), terms AND the
   banked-payout share (the reward depends only on total glow, so a
   bucket-attribution bug shows only in the banked share — it is
   asserted at the same tolerance).
2. Discriminating cases counted: closed-gate play ticks (the Ec
   earner), decay-interior ticks, banked payout strictly positive,
   and a planted truncation reset.
3. Channel properties: terms never negative, zero before any play,
   purity (enrich2_terms mutates nothing).
4. The install wrapper ADDS the term (sign guard).
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "trainer"))
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
import cert_harness_fog as H  # noqa: E402
import train_ppo_enrich2 as te  # noqa: E402

OBS_GATE, OBS_HAP, OBS_ACT_PLAY = [0, 1, 2, 4, 5], 6, 14
CONFIG = HERE.parent / "beam-world-screen-2026-09-19" / "package.toml"


def run(ticks=1200, seed=900401):
    import cloudkitty
    import tomllib
    with open(CONFIG, "rb") as f:
        cfg = tomllib.load(f)
    roster = len(cfg["kitty"])
    models = [H.load_model(s) for s in H.SEATINGS["gen1-A"]]
    env = cloudkitty.ParallelEnv(str(CONFIG), horizon=ticks)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    obs_stack, rewards = [], []
    for _t in range(ticks):
        ob = np.stack([np.asarray(obs[x], np.float32) for x in names])
        ob[:, H.CLOCK_INDEX] = 0.0
        obs_stack.append(ob.copy())
        mk = np.stack([np.asarray(infos[x]["mask"], np.uint8) for x in names]).astype(bool)
        lg = np.stack([np.asarray(models[j](ob[j:j + 1], mk[j:j + 1]), np.float32)[0]
                       for j in range(roster)])
        a0 = np.where(mk[:, :H.N_ACT], lg[:, :H.N_ACT], H.NEG_INF).argmax(1)
        g0 = np.where(mk[:, H.N_ACT:], lg[:, H.N_ACT:], H.NEG_INF).argmax(1)
        obs, rew, _te_, _tr, infos = env.step({x: (int(a0[j]), int(g0[j])) for j, x in enumerate(names)})
        rewards.append(float(rew[names[0]]))
    return np.stack(obs_stack), np.asarray(rewards)


def ref_terms(obs_stack, trunc, d_min, d_max):
    """Independent reference: plain-python per seat, separately written."""
    import math
    T, roster, _ = obs_stack.shape
    Eo = [0.0] * roster
    Ec = [0.0] * roster
    out = np.zeros(T)
    pay = banked = 0.0
    for t in range(T):
        ob = obs_stack[t].astype(np.float64)
        base, lifted = [], []
        for k in range(roster):
            worst = max(ob[k][i] for i in OBS_GATE)
            frac = min(1.0, max(0.0, (worst - te.THETA_LO) / (te.THETA_HI - te.THETA_LO)))
            g = min(1.0, max(0.0, (te.THETA_HI - worst) / (te.THETA_HI - te.THETA_LO)))
            d = d_min + frac * (d_max - d_min)
            if ob[k][OBS_ACT_PLAY] > 0.5:
                add = min(te.GAIN, max(0.0, 1.0 - (Eo[k] + Ec[k])))
                if g > 0.0:
                    Eo[k] += add
                else:
                    Ec[k] += add
            else:
                Eo[k] *= (1.0 - d)
                Ec[k] *= (1.0 - d)
            E = Eo[k] + Ec[k]
            h = ob[k][OBS_HAP]
            base.append(max(h + te.EPS, te.TERM_FLOOR))
            lifted.append(max(h + te.BETA * E * g + te.EPS, te.TERM_FLOOR))
            pay += te.BETA * g * E
            banked += te.BETA * g * Ec[k]
        W = lambda xs: math.exp(sum(math.log(x) for x in xs) / len(xs)) - te.EPS  # noqa: E731
        out[t] = W(lifted) - W(base)
        if trunc[t]:
            Eo = [0.0] * roster
            Ec = [0.0] * roster
    return out, (banked / pay if pay > 0 else 0.0)


def main():
    obs_stack, rewards = run()
    T, roster, _ = obs_stack.shape

    worst_all = np.stack([obs_stack[t][:, OBS_GATE].max(-1) for t in range(T)])
    play_all = np.stack([obs_stack[t][:, OBS_ACT_PLAY] > 0.5 for t in range(T)])
    n_play = int(play_all.sum())
    n_closed_play = int((play_all & (worst_all >= te.THETA_HI)).sum())
    n_interior = int(((worst_all > te.THETA_LO) & (worst_all < te.THETA_HI)).sum())
    assert n_play > 100, n_play
    assert n_closed_play > 10, ("the Ec earner must occur", n_closed_play)
    assert n_interior > 100, n_interior

    trunc = np.zeros((T, 1), bool)
    trunc[700, 0] = True
    buf0 = {"obs": obs_stack[:, None, :, :].copy(),
            "valid": np.ones((T, 1, roster), bool),
            "trunc": trunc.copy(),
            "reward": rewards[:, None].copy()}
    for d_min, d_max in ((0.0025, 0.025), (0.01, 0.10)):
        buf = {k: v.copy() for k, v in buf0.items()}
        got, Eo_f, Ec_f, stats = te.enrich2_terms(buf, d_min, d_max,
                                                  np.zeros((1, roster)), np.zeros((1, roster)))
        for k in buf0:
            assert np.array_equal(buf[k], buf0[k]), f"enrich2_terms changed {k}"
        want, want_banked = ref_terms(obs_stack, trunc[:, 0], d_min, d_max)
        bad = np.where(np.abs(got[:, 0] - want) > 1e-9)[0]
        assert bad.size == 0, f"d {d_min}/{d_max}: term mismatch at tick {bad[0]}: {got[bad[0], 0]} vs {want[bad[0]]}"
        assert abs(stats["banked_payout_share"] - want_banked) < 1e-9, \
            (d_min, d_max, stats["banked_payout_share"], want_banked)
        assert stats["banked_payout_share"] > 0, "banked payout must occur in this leg"
        assert (got >= -1e-15).all()
        first_play = int(np.where(play_all.any(1))[0][0])
        assert np.allclose(got[:first_play], 0.0)

    # The two corners must actually differ (the curve is live).
    a, _, _, sa = te.enrich2_terms({k: v.copy() for k, v in buf0.items()}, 0.0025, 0.025,
                                   np.zeros((1, roster)), np.zeros((1, roster)))
    b, _, _, sb = te.enrich2_terms({k: v.copy() for k, v in buf0.items()}, 0.01, 0.10,
                                   np.zeros((1, roster)), np.zeros((1, roster)))
    assert a.sum() > b.sum(), "gentler decay must retain more glow"
    assert sb["banked_payout_share"] < sa["banked_payout_share"], \
        "harsher max decay must drain more banked glow"

    orig_collect = te.tf.collect_fragment
    try:
        te.tf.collect_fragment = lambda *args, **kw: ({k: v.copy() for k, v in buf0.items()}, None, 0, 0, 0)
        te.ES["Eo"] = te.ES["Ec"] = None
        te.install_enrich2("d25-250-s1")
        out = te.tf.collect_fragment(None, None, None, None, T)
        assert np.allclose(out[0]["reward"], buf0["reward"] + a), "wrapper must ADD the term to the reward"
    finally:
        te.tf.collect_fragment = orig_collect
    trace = te.SCREEN / "artifacts" / "ppo-fog-d25-250-s1" / "enrich2-trace.jsonl"
    if trace.exists():
        rows = [r for r in trace.read_text().splitlines() if r.strip()]
        trace.write_text("\n".join(rows[:-1]) + ("\n" if rows[:-1] else ""))

    print(f"ok: {T} ticks; terms + banked share match reference on both corners; "
          f"play {n_play}, closed-play {n_closed_play}, interior {n_interior}; "
          f"banked shares {sa['banked_payout_share']:.4f} (gentle) vs {sb['banked_payout_share']:.4f} (harsh)")


if __name__ == "__main__":
    main()
