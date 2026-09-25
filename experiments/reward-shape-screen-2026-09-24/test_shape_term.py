"""Guards for the reward-shape trainer's counterfactual-floor term.

    CERT_ARTS=../beam-world-screen-2026-09-19/artifacts \
        ../exp-006-character-gen/.venv/bin/python -B test_shape_term.py

Real payloads: 1,200 ticks of pkg-s1 all-arm on package.toml at seed
900201, capturing per-tick observations, the engine's per-tick reward,
AND the post-step global state with the beam set. Three guards:

1. Semantic: the obs-side counterfactual indicator (self offsets) must
   agree with an independent state-side derivation (needs + activity +
   position vs the beam set, the probe's method) at the one-tick
   alignment the post-apply snapshot implies: obs at loop step t+1
   describes the world state read after step t.
2. shape_rewards on a real recorded buffer: "none" is bitwise inert;
   each shape changes ONLY the reward key; hand-computed terms match at
   sampled ticks.
3. lam_step dynamics: rises under sustained violation, decays to 0
   under compliance, respects the clamp.
"""
import sys
import tomllib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "trainer"))
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
import cert_harness_fog as H  # noqa: E402
import train_ppo_shape as ts  # noqa: E402

# Independent copies (observe.rs schema 5 / global_state.rs), not
# imported from the trainer.
OBS_SLEEP_NEED, OBS_ACT_SLEEP, OBS_IN_SUNBEAM = 2, 11, 17
FLOOR100 = 15.0
CONFIG = HERE.parent / "beam-world-screen-2026-09-19" / "package.toml"


def run(ticks=1200, seed=900201):
    import cloudkitty
    with open(CONFIG, "rb") as f:
        cfg = tomllib.load(f)
    roster = len(cfg["kitty"])
    width, height = cfg["world"]["width"], cfg["world"]["height"]
    model = H.load_model("ppo:pkg-s1")
    env = cloudkitty.ParallelEnv(str(CONFIG), horizon=ticks)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    obs_stack, rewards, cf_state_side = [], [], []
    for _t in range(ticks):
        ob = np.stack([np.asarray(obs[x], np.float32) for x in names])
        ob[:, H.CLOCK_INDEX] = 0.0
        obs_stack.append(ob.copy())
        mk = np.stack([np.asarray(infos[x]["mask"], np.uint8) for x in names]).astype(bool)
        lg = np.asarray(model(ob, mk), np.float32)
        a0 = np.where(mk[:, :H.N_ACT], lg[:, :H.N_ACT], H.NEG_INF).argmax(1)
        g0 = np.where(mk[:, H.N_ACT:], lg[:, H.N_ACT:], H.NEG_INF).argmax(1)
        obs, rew, _te, _tr, infos = env.step({x: (int(a0[j]), int(g0[j])) for j, x in enumerate(names)})
        rewards.append(float(rew[names[0]]))
        st = np.asarray(env.state(), np.float32)
        beams = {(x, y) for (_id, ty, x, y) in env.elements() if ty == "Sunbeam"}
        row = np.zeros(roster, bool)
        for k in range(roster):
            b = k * H.PER_KITTY
            asleep = int(st[b + H.ACT0:b + H.ACT0 + 7].argmax()) == H.SLEEP_ACT
            pos = (int(round(float(st[b + H.POS0]) * width)), int(round(float(st[b + H.POS0 + 1]) * height)))
            need = float(st[b + H.NEED_SLEEP]) * 100
            row[k] = asleep and pos not in beams and need < FLOOR100
        cf_state_side.append(row)
    return np.stack(obs_stack), np.asarray(rewards), np.stack(cf_state_side)


def obs_cf(ob):
    return ((ob[:, OBS_ACT_SLEEP] > 0.5) & (ob[:, OBS_IN_SUNBEAM] < 0.5)
            & (ob[:, OBS_SLEEP_NEED] < FLOOR100 / 100.0))


def main():
    obs_stack, rewards, cf_state = run()
    T, roster, _ = obs_stack.shape

    # 1. Semantic alignment: obs[t+1] describes the state read after step t.
    agree = total = 0
    for t in range(T - 1):
        a, b = obs_cf(obs_stack[t + 1]), cf_state[t]
        agree += int((a == b).sum())
        total += roster
    frac = agree / total
    assert frac == 1.0, f"cf from obs disagrees with cf from state: agreement {frac:.6f}"
    n_cf = int(cf_state.sum())
    assert n_cf > 100, f"vacuous run: only {n_cf} counterfactual seat-ticks"

    # 2. shape_rewards on a real buffer (T, n=1 world, MAX_SEATS=roster).
    buf0 = {"obs": obs_stack[:, None, :, :].copy(),
            "valid": np.ones((T, 1, roster), bool),
            "reward": rewards[:, None].copy(),
            "act": np.zeros((T, 1, roster), np.int64)}
    for shape in (None, "none"):
        buf = {k: v.copy() for k, v in buf0.items()}
        cf_mean, term = ts.shape_rewards(buf, shape, 1.23)
        assert cf_mean == term == 0.0
        for k in buf0:
            assert np.array_equal(buf[k], buf0[k]), f"shape {shape} changed {k}"
    picks = [3, T // 2, T - 2]
    for shape, coef in (("hard", ts.C1), ("cvx", ts.C2), ("lam", 0.77)):
        buf = {k: v.copy() for k, v in buf0.items()}
        ts.shape_rewards(buf, shape, 0.77)
        for k in ("obs", "valid", "act"):
            assert np.array_equal(buf[k], buf0[k]), f"shape {shape} changed {k}"
        for t in picks:
            cf = obs_cf(obs_stack[t])
            if shape == "cvx":
                need = obs_stack[t][:, OBS_SLEEP_NEED]
                want = coef * float(np.where(cf, ((0.15 - need) / 0.15) ** 2, 0.0).sum()) / roster
            else:
                want = coef * float(cf.sum()) / roster
            got = float(buf0["reward"][t, 0] - buf["reward"][t, 0])
            assert abs(got - want) < 1e-9, f"{shape} term mismatch at tick {t}: {got} vs {want}"

    # 3. lam_step dynamics.
    lam = 0.0
    for _ in range(40):
        lam = ts.lam_step(lam, 0.20)
    assert lam > 0.25, f"lam did not rise under sustained violation: {lam}"
    assert abs(lam - 40 * ts.ETA * (0.20 - ts.D_TARGET)) < 1e-9
    for _ in range(2000):
        lam = ts.lam_step(lam, 0.20)
    assert lam == ts.LAM_CLAMP, f"clamp not respected: {lam}"
    for _ in range(5000):
        lam = ts.lam_step(lam, 0.0)
    assert lam == 0.0, f"lam did not decay to zero under compliance: {lam}"

    print(f"ok: {T} ticks; cf seat-ticks {n_cf}; obs/state agreement 1.0; "
          f"terms match at ticks {picks}; lam dynamics clean")


if __name__ == "__main__":
    main()
