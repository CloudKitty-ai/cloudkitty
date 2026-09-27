"""Guards for the stage-B trainer (β family + accrual gate).

    CERT_ARTS=experiments/enrichment-decay-sweep-2026-09-26/artifacts \
        experiments/exp-006-character-gen/.venv/bin/python -B \
        experiments/enrichment-decay-sweep-2026-09-26/test_enrich2b_term.py

Real payloads: the same 1,200-tick gen1-A leg the stage-A guard uses
(seed 900401, this screen's band). Guards:

1. enrich2b_terms vs an independently coded reference, full-tick,
   terms AND banked share AND at-cap share AND E_p50, on THREE
   settings: (β 0.10, throttle), (β 0.10, accrual gate), (β 0.14,
   throttle).
2. Structural: the accrual arm's Ec stays exactly zero for the whole
   run and its banked payout share is exactly 0; the throttle arm's
   banked share is > 0 on this leg (closed-gate play occurs 26
   times); with β equal, the accrual arm's terms are <= the throttle
   arm's everywhere and strictly below somewhere.
3. β wiring: SLOT_PARAMS maps every b06/b10/b14/ag10 slot to its
   ruled (β, gate) pair; 11 slots at run indices 79–89.
4. Purity and the wrapper ADD (sign guard).
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "trainer"))
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
import cert_harness_fog as H  # noqa: E402
import train_ppo_enrich2b as te  # noqa: E402

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


# Independent copies of the pins (PREREG-B): never read from the
# trainer, or a mutated trainer constant moves both sides and the
# guard goes vacuous (the at-cap red proved it).
R_THETA_LO, R_THETA_HI, R_GAIN = 0.15, 0.25, 0.25
R_D_MIN, R_D_MAX = 0.01, 0.10
R_EPS, R_FLOOR, R_AT_CAP = 0.01, 1e-4, 0.95


def ref_terms(obs_stack, trunc, beta, accrual_gate):
    import math
    T, roster, _ = obs_stack.shape
    Eo = [0.0] * roster
    Ec = [0.0] * roster
    out = np.zeros(T)
    pay = banked = cap = 0.0
    es = []
    n_ct = 0
    for t in range(T):
        ob = obs_stack[t].astype(np.float64)
        base, lifted = [], []
        for k in range(roster):
            worst = max(ob[k][i] for i in OBS_GATE)
            frac = min(1.0, max(0.0, (worst - R_THETA_LO) / (R_THETA_HI - R_THETA_LO)))
            g = min(1.0, max(0.0, (R_THETA_HI - worst) / (R_THETA_HI - R_THETA_LO)))
            d = R_D_MIN + frac * (R_D_MAX - R_D_MIN)
            if ob[k][OBS_ACT_PLAY] > 0.5:
                add = min(R_GAIN, max(0.0, 1.0 - (Eo[k] + Ec[k])))
                if g > 0.0:
                    Eo[k] += add
                elif not accrual_gate:
                    Ec[k] += add
            else:
                Eo[k] *= (1.0 - d)
                Ec[k] *= (1.0 - d)
            E = Eo[k] + Ec[k]
            h = ob[k][OBS_HAP]
            base.append(max(h + R_EPS, R_FLOOR))
            lifted.append(max(h + beta * E * g + R_EPS, R_FLOOR))
            pay += beta * g * E
            banked += beta * g * Ec[k]
            cap += 1.0 if E >= R_AT_CAP else 0.0
            es.append(E)
            n_ct += 1
        W = lambda xs: math.exp(sum(math.log(x) for x in xs) / len(xs)) - R_EPS  # noqa: E731
        out[t] = W(lifted) - W(base)
        if trunc[t]:
            Eo = [0.0] * roster
            Ec = [0.0] * roster
    stats = {"banked": (banked / pay if pay > 0 else 0.0),
             "at_cap": cap / n_ct, "E_p50": float(np.median(np.array(es)))}
    return out, stats


def main():
    # 3. Slot wiring first (cheap).
    assert set(te.SLOT_PARAMS) == {f"b06-s{i}" for i in (1, 2, 3)} | {f"b10-s{i}" for i in (1, 2, 3)} | \
        {f"b14-s{i}" for i in (1, 2, 3)} | {"ag10-s1", "ag10-s2"}
    for slot, (beta, ag) in te.SLOT_PARAMS.items():
        fam = slot.rsplit("-s", 1)[0]
        assert (beta, ag) == {"b06": (0.06, False), "b10": (0.10, False),
                              "b14": (0.14, False), "ag10": (0.10, True)}[fam], slot
    idxs = sorted(te.tb.SLOTS[s][4] for s in te.SLOT_PARAMS)
    assert idxs == list(range(79, 90)), idxs

    obs_stack, rewards = run()
    T, roster, _ = obs_stack.shape
    worst_all = np.stack([obs_stack[t][:, OBS_GATE].max(-1) for t in range(T)])
    play_all = np.stack([obs_stack[t][:, OBS_ACT_PLAY] > 0.5 for t in range(T)])
    n_closed_play = int((play_all & (worst_all >= R_THETA_HI)).sum())
    assert n_closed_play > 10, ("the accrual gate's discriminating case must occur", n_closed_play)

    trunc = np.zeros((T, 1), bool)
    trunc[700, 0] = True
    buf0 = {"obs": obs_stack[:, None, :, :].copy(),
            "valid": np.ones((T, 1, roster), bool),
            "trunc": trunc.copy(),
            "reward": rewards[:, None].copy()}
    results = {}
    for name, (beta, ag) in (("b10", (0.10, False)), ("ag10", (0.10, True)), ("b14", (0.14, False))):
        buf = {k: v.copy() for k, v in buf0.items()}
        got, Eo_f, Ec_f, stats = te.enrich2b_terms(buf, beta, ag, np.zeros((1, roster)), np.zeros((1, roster)))
        for k in buf0:
            assert np.array_equal(buf[k], buf0[k]), f"{name} changed {k}"
        want, wstats = ref_terms(obs_stack, trunc[:, 0], beta, ag)
        bad = np.where(np.abs(got[:, 0] - want) > 1e-9)[0]
        assert bad.size == 0, f"{name}: term mismatch at tick {bad[0]}"
        assert abs(stats["banked_payout_share"] - wstats["banked"]) < 1e-9, name
        assert abs(stats["at_cap_share"] - wstats["at_cap"]) < 1e-9, name
        assert abs(stats["E_p50"] - wstats["E_p50"]) < 1e-9, name
        if ag:
            assert stats["banked_payout_share"] == 0.0 and float(np.abs(Ec_f).max()) == 0.0, \
                "the accrual arm must never hold closed-earned glow"
        results[name] = (got, stats)

    g_b10, s_b10 = results["b10"]
    g_ag, s_ag = results["ag10"]
    assert s_b10["banked_payout_share"] > 0, "throttle arm must bank on this leg"
    assert (g_ag <= g_b10 + 1e-15).all() and g_ag.sum() < g_b10.sum(), \
        "at equal beta the accrual arm's terms are bounded by the throttle's"
    g_b14, _ = results["b14"]
    assert g_b14.sum() > g_b10.sum(), "beta 0.14 must pay more than 0.10 on the same trajectory"

    orig_collect = te.tf.collect_fragment
    try:
        te.tf.collect_fragment = lambda *a, **kw: ({k: v.copy() for k, v in buf0.items()}, None, 0, 0, 0)
        te.ES["Eo"] = te.ES["Ec"] = None
        te.install_enrich2b("b10-s1")
        out = te.tf.collect_fragment(None, None, None, None, T)
        assert np.allclose(out[0]["reward"], buf0["reward"] + g_b10), "wrapper must ADD the term"
    finally:
        te.tf.collect_fragment = orig_collect
    trace = te.SCREEN / "artifacts" / "ppo-fog-b10-s1" / "enrich2b-trace.jsonl"
    if trace.exists():
        rows = [r for r in trace.read_text().splitlines() if r.strip()]
        trace.write_text("\n".join(rows[:-1]) + ("\n" if rows[:-1] else ""))

    print(f"ok: {T} ticks; three settings match reference (terms, banked, at-cap, E_p50); "
          f"closed-play {n_closed_play}; ag banked 0 vs b10 {s_b10['banked_payout_share']:.4f}; "
          f"at-cap b10 {s_b10['at_cap_share']:.4f}")


if __name__ == "__main__":
    main()
