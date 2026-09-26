"""Guards for the enrichment-bonus trainer's channel.

    CERT_ARTS=experiments/enrichment-bonus-screen-2026-09-26/artifacts \
        experiments/exp-006-character-gen/.venv/bin/python -B \
        experiments/enrichment-bonus-screen-2026-09-26/test_enrich_term.py

Real payloads: 1,200 ticks of the gen1-A seating on package.toml at
seed 900304, capturing per-tick observations, the engine's per-tick
reward, and the post-step global state. Four guards:

1. Semantic: the obs-side fields (worst gate need, Playing cell, own
   happiness) agree with an independent state-side derivation at the
   post-apply alignment (obs at loop step t+1 describes the state read
   after step t), and the trainer's Nash recomposition of the obs
   happiness reproduces the engine's reward stream.
2. enrich_terms vs an independently coded reference on the real
   buffer, full-tick, with the discriminating cases counted (play
   ticks, interior-gate ticks, zero-gate ticks, glow-suppressed-by-gate
   ticks, a truncation reset) so an offset or polarity bug cannot hide.
3. Channel properties: terms are never negative, zero before any play,
   the full-beta term dominates the half-beta term, and enrich_terms
   mutates nothing.
4. The install wrapper ADDS the term to buf["reward"] (sign guard).
"""
import sys
import tomllib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "trainer"))
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
import cert_harness_fog as H  # noqa: E402
import train_ppo_enrich as te  # noqa: E402

# Independent copies (observe.rs schema 5 / global_state.rs / reward.rs),
# not imported from the trainer.
OBS_GATE, OBS_HAP, OBS_ACT_PLAY = [0, 1, 2, 4, 5], 6, 14
ST_GATE = [0, 1, 2, 4, 5]
ST_PLAY_ACT = 5
CONFIG = HERE.parent / "beam-world-screen-2026-09-19" / "package.toml"


def run(ticks=1200, seed=900304):
    import cloudkitty
    with open(CONFIG, "rb") as f:
        cfg = tomllib.load(f)
    roster = len(cfg["kitty"])
    models = [H.load_model(s) for s in H.SEATINGS["gen1-A"]]
    env = cloudkitty.ParallelEnv(str(CONFIG), horizon=ticks)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    obs_stack, rewards, st_rows = [], [], []
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
        st = np.asarray(env.state(), np.float32)
        rows = []
        for k in range(roster):
            b = k * H.PER_KITTY
            rows.append({
                "worst": max(float(st[b + g]) for g in ST_GATE),
                "playing": int(st[b + H.ACT0:b + H.ACT0 + 7].argmax()) == ST_PLAY_ACT,
                "hap": float(st[b + H.HAP]),
            })
        st_rows.append(rows)
    return np.stack(obs_stack), np.asarray(rewards), st_rows


def ref_terms(obs_stack, trunc, beta):
    """Independent reference: plain-python per seat, state math from the
    same obs but a separately written path."""
    import math
    T, roster, _ = obs_stack.shape
    E = [0.0] * roster
    out = np.zeros(T)
    for t in range(T):
        ob = obs_stack[t].astype(np.float64)
        base, lifted = [], []
        for k in range(roster):
            worst = max(ob[k][i] for i in OBS_GATE)
            g = min(1.0, max(0.0, (te.THETA_HI - worst) / (te.THETA_HI - te.THETA_LO)))
            playing = ob[k][OBS_ACT_PLAY] > 0.5
            E[k] = min(1.0, E[k] + te.GAIN) if playing else E[k] * (1.0 - te.DECAY)
            h = ob[k][OBS_HAP]
            base.append(max(h + te.EPS, te.TERM_FLOOR))
            lifted.append(max(h + beta * E[k] * g + te.EPS, te.TERM_FLOOR))
        W = lambda xs: math.exp(sum(math.log(x) for x in xs) / len(xs)) - te.EPS  # noqa: E731
        out[t] = W(lifted) - W(base)
        if trunc[t]:
            E = [0.0] * roster
    return out


def main():
    obs_stack, rewards, st_rows = run()
    T, roster, _ = obs_stack.shape

    # 1a. Semantic alignment: obs[t+1] fields == state fields after step t.
    agree = total = 0
    for t in range(T - 1):
        ob = obs_stack[t + 1].astype(np.float64)
        for k in range(roster):
            s = st_rows[t][k]
            ok = (abs(max(ob[k][i] for i in OBS_GATE) - s["worst"]) < 1e-6
                  and (ob[k][OBS_ACT_PLAY] > 0.5) == s["playing"]
                  and abs(ob[k][OBS_HAP] - s["hap"]) < 1e-6)
            agree += int(ok)
            total += 1
    frac = agree / total
    assert frac == 1.0, f"obs fields disagree with state: agreement {frac:.6f}"

    # 1b. Nash recomposition: W(h from obs[t+1]) reproduces reward[t].
    gaps = []
    for t in range(T - 1):
        h = obs_stack[t + 1][:, OBS_HAP].astype(np.float64)
        w = float(np.exp(np.log(np.maximum(h + te.EPS, te.TERM_FLOOR)).mean()) - te.EPS)
        gaps.append(abs(w - rewards[t]))
    max_gap = max(gaps)
    assert max_gap < 1e-3, f"Nash recomposition off by {max_gap} (formula, eps, or scale wrong)"

    # Discriminating cases in the run, so an unexercised branch cannot pass.
    worst_all = np.stack([obs_stack[t][:, OBS_GATE].max(-1) for t in range(T)])
    play_all = np.stack([obs_stack[t][:, OBS_ACT_PLAY] > 0.5 for t in range(T)])
    n_play = int(play_all.sum())
    n_interior = int(((worst_all > te.THETA_LO) & (worst_all < te.THETA_HI)).sum())
    n_zero_gate = int((worst_all >= te.THETA_HI).sum())
    assert n_play > 100, f"vacuous: {n_play} playing seat-ticks"
    assert n_interior > 100, f"vacuous for the ramp interior: {n_interior}"
    assert n_zero_gate > 50, f"vacuous for the closed gate: {n_zero_gate}"

    # 2. enrich_terms vs the reference, with a truncation planted mid-run.
    trunc = np.zeros((T, 1), bool)
    trunc[700, 0] = True
    buf0 = {"obs": obs_stack[:, None, :, :].copy(),
            "valid": np.ones((T, 1, roster), bool),
            "trunc": trunc.copy(),
            "reward": rewards[:, None].copy()}
    for beta in (te.BETA, te.BETA_LO):
        buf = {k: v.copy() for k, v in buf0.items()}
        got, E_fin, stats = te.enrich_terms(buf, beta, np.zeros((1, roster)))
        for k in buf0:
            assert np.array_equal(buf[k], buf0[k]), f"enrich_terms changed {k}"
        want = ref_terms(obs_stack, trunc[:, 0], beta)
        bad = np.where(np.abs(got[:, 0] - want) > 1e-9)[0]
        assert bad.size == 0, f"beta {beta}: term mismatch at tick {bad[0]}: {got[bad[0], 0]} vs {want[bad[0]]}"
    # The glow-suppressed-by-gate case occurred: E > 0 while g = 0.
    E = np.zeros(roster)
    n_suppressed = 0
    for t in range(T):
        for k in range(roster):
            E[k] = min(1.0, E[k] + te.GAIN) if play_all[t][k] else E[k] * (1.0 - te.DECAY)
            if E[k] > 0.05 and worst_all[t][k] >= te.THETA_HI:
                n_suppressed += 1
        if trunc[t, 0]:
            E[:] = 0.0
    assert n_suppressed > 10, f"vacuous for the gate-vs-glow interaction: {n_suppressed}"

    # 3. Channel properties.
    got_full, _, _ = te.enrich_terms({k: v.copy() for k, v in buf0.items()}, te.BETA, np.zeros((1, roster)))
    got_lo, _, _ = te.enrich_terms({k: v.copy() for k, v in buf0.items()}, te.BETA_LO, np.zeros((1, roster)))
    assert (got_full >= -1e-15).all(), "the bonus channel went negative"
    assert (got_full - got_lo >= -1e-12).all() and got_full.sum() > got_lo.sum() > 0, \
        "full beta must dominate half beta"
    first_play = int(np.where(play_all.any(1))[0][0])
    assert np.allclose(got_full[:first_play], 0.0), "terms before any play must be zero (E starts 0)"

    # 4. The wrapper ADDS the term.
    class FakeRunner:
        pass
    orig_collect = te.tf.collect_fragment
    try:
        te.tf.collect_fragment = lambda *a, **kw: ({k: v.copy() for k, v in buf0.items()}, None, 0, 0, 0)
        te.ES["E"] = None
        te.install_enrich("bonus-s1")
        out = te.tf.collect_fragment(None, None, None, None, T)
        shaped = out[0]["reward"]
        assert np.allclose(shaped, buf0["reward"] + got_full), "wrapper must ADD the term to the reward"
    finally:
        te.tf.collect_fragment = orig_collect
    trace = te.SCREEN / "artifacts" / "ppo-fog-bonus-s1" / "enrich-trace.jsonl"
    if trace.exists():  # the wrapper check above appends one test row; drop it
        rows = [r for r in trace.read_text().splitlines() if r.strip()]
        trace.write_text("\n".join(rows[:-1]) + ("\n" if rows[:-1] else ""))

    print(f"ok: {T} ticks; obs/state agreement 1.0; recomposition max gap {max_gap:.2e}; "
          f"terms match at every tick (both betas); play {n_play}, interior {n_interior}, "
          f"closed-gate {n_zero_gate}, glow-suppressed {n_suppressed}")


if __name__ == "__main__":
    main()
