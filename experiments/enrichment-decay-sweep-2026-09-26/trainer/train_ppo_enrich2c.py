#!/usr/bin/env python3
"""Dead-or-held probe trainer (PREREG-C.md, 2026-09-30; the Professor
review's recommended probe, owner's word "run the probe").

Two arms x two seeds at beta 0.14 on the d100-1000 corner:
  l14  leash lowered to 0.01 (tf pin "beta_probe"); obs untouched.
  o14  E VISIBLE: the enrichment stock is written into the obs CLOCK
       slot (column 407) during collection, before the policy acts,
       and stored in the buffer so the PPO update sees the same
       input. Leash stays 0.04. Declared deviation from "append E":
       schema 5 has no spare float and a 409th column breaks the
       tokenizer; the clock input is already ruled for removal at
       Gen 2. CONFOUND, declared: o14 removes the cycling clock and
       adds E in one move.

The o14 rollout E uses the recurrence of enrich2b_terms exactly
(same gate indices, gain, corner decay, trunc reset); the reward
term is stage B's enrich2b_terms at beta 0.14, accrual_gate False.

    .../train_ppo_enrich2c.py --slot l14-s1
"""
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
import train_ppo_enrich2b as e2b  # noqa: E402

BETA = 0.14
E_COL = 407  # the clock slot (obs_layout_v5: clock token, width 1)
LEASH_PROBE = 0.01

# slot -> (leash pin key, e_in_obs)
FAMS = {"l14": ("beta_probe", False), "o14": ("beta_low", True)}
_idx = 90
SLOT_PARAMS = {}
for _fam, (_pin, _eobs) in FAMS.items():
    for _s in (1, 2):
        slot = f"{_fam}-s{_s}"
        SLOT_PARAMS[slot] = (_pin, _eobs)
        tb.WORLD[slot] = ((3.0, 7.0, 3000, 6), BEAM / "package.toml")
        tb.SLOTS[slot] = ("pin", _pin, "init_lesson", _s, _idx)
        _idx += 1
# tb.install() REPLACES tf.PINS with tb's own dict (train_ppo_beam
# line "tf.PINS = PINS"), so the probe pin must live in tb.PINS — the
# dict that survives install. (First l14 launch crashed on exactly
# this: KeyError 'beta_probe'; prereg-c-deviations.md.)
tb.PINS["beta_probe"] = LEASH_PROBE
tf.PINS["beta_probe"] = LEASH_PROBE

ROLL = {"Eo": None, "Ec": None}


def roll_E_step(obs_t, valid_t, Eo, Ec):
    """One tick of the o14 rollout stock, enrich2b_terms' recurrence
    verbatim on the flat (worlds, seats, obs) tick slice: playing from
    ACT_PLAY, worst over GATE_OBS, corner decay, cap room. Returns the
    updated (Eo, Ec). Trunc reset is the caller's (post-step), as in
    enrich2b_terms."""
    gate_idx = np.array(e2b.GATE_OBS)
    playing = valid_t & (obs_t[:, :, e2b.ACT_PLAY] > 0.5)
    worst = obs_t[:, :, gate_idx].max(-1).astype(np.float64)
    g = np.clip((e2b.THETA_HI - worst) / (e2b.THETA_HI - e2b.THETA_LO), 0.0, 1.0)
    d = e2b.D_MIN + np.clip((worst - e2b.THETA_LO) / (e2b.THETA_HI - e2b.THETA_LO),
                            0.0, 1.0) * (e2b.D_MAX - e2b.D_MIN)
    room = np.maximum(0.0, 1.0 - (Eo + Ec))
    add = np.where(playing, np.minimum(e2b.GAIN, room), 0.0)
    closed_add = np.where(g > 0.0, 0.0, add)
    Eo = np.where(playing, Eo + np.where(g > 0.0, add, 0.0), Eo * (1.0 - d))
    Ec = np.where(playing, Ec + closed_add, Ec * (1.0 - d))
    return Eo, Ec


def install_collect_e():
    """o14 only: fork of tf.collect_fragment that writes the online
    stock into E_COL before the policy acts and stores it in the
    buffer, so rollout and PPO update see the same input."""
    def collect_with_e(runner, policy, critic, vstats, T):
        # Fork of tf.collect_fragment (we cannot hook per tick inside
        # it): identical to the original except the three E lines.
        import torch
        mean, std = vstats
        n = runner.n_worlds
        obs_dim, mask_dim = runner.dims
        buf = {
            "obs": np.zeros((T, n, tf.MAX_SEATS, obs_dim), np.float32),
            "mask": np.zeros((T, n, tf.MAX_SEATS, mask_dim), bool),
            "valid": np.zeros((T, n, tf.MAX_SEATS), bool),
            "act": np.zeros((T, n, tf.MAX_SEATS), np.int64),
            "msg": np.zeros((T, n, tf.MAX_SEATS), np.int64),
            "logp": np.zeros((T, n, tf.MAX_SEATS), np.float32),
            "state": np.zeros((T, n, critic.dims[0]), np.float32),
            "reward": np.zeros((T, n), np.float64),
            "trunc": np.zeros((T, n), bool),
            "final_v": np.zeros((T, n), np.float32),
            "value": np.zeros((T, n), np.float32),
        }
        ent_sum, viol_sum, meow_n, dec_n = 0.0, 0.0, 0, 0
        if ROLL["Eo"] is None or ROLL["Eo"].shape != (n, tf.MAX_SEATS):
            ROLL["Eo"] = np.zeros((n, tf.MAX_SEATS))
            ROLL["Ec"] = np.zeros((n, tf.MAX_SEATS))
        with torch.no_grad():
            for t in range(T):
                states = runner.states()
                v_raw = critic(torch.from_numpy(states)).squeeze(-1).numpy() * std + mean
                obs, mask, valid = runner.flat_obs(obs_dim, mask_dim)
                ROLL["Eo"], ROLL["Ec"] = roll_E_step(obs, valid, ROLL["Eo"], ROLL["Ec"])
                obs[:, :, E_COL] = (ROLL["Eo"] + ROLL["Ec"]).astype(np.float32)
                to = torch.from_numpy(obs[valid])
                tm = torch.from_numpy(mask[valid])
                logits = policy(to)
                d_act, d_msg = tf.two_head(logits, tm)
                a = d_act.sample()
                g = d_msg.sample()
                logp_v = d_act.log_prob(a) + d_msg.log_prob(g)
                ent, viol = tf.joint_entropy_and_viol(logits, tm)
                ent_sum += ent
                viol_sum += viol
                msg_np = g.numpy()
                meow_n += int((msg_np != 0).sum())
                dec_n += len(msg_np)
                actions = np.zeros((n, tf.MAX_SEATS, 2), np.int64)
                actions[valid] = np.stack([a.numpy(), msg_np], axis=1)
                rewards, truncated, final_states = runner.step(actions)
                if truncated.any():
                    fv = critic(torch.from_numpy(final_states[truncated])
                                ).squeeze(-1).numpy() * std + mean
                    buf["final_v"][t, truncated] = fv
                buf["obs"][t], buf["mask"][t], buf["valid"][t] = obs, mask, valid
                buf["act"][t][valid] = a.numpy()
                buf["msg"][t][valid] = msg_np
                buf["logp"][t][valid] = logp_v.numpy()
                buf["state"][t], buf["reward"][t] = states, rewards
                buf["trunc"][t], buf["value"][t] = truncated, v_raw
                ROLL["Eo"][truncated] = 0.0
                ROLL["Ec"][truncated] = 0.0
            v_last = critic(torch.from_numpy(runner.states())
                            ).squeeze(-1).numpy() * std + mean
        meow_rate = 1000.0 * meow_n / max(1, dec_n)
        return buf, v_last, ent_sum / T, viol_sum / T, meow_rate

    tf.collect_fragment = collect_with_e


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    slot = argv[argv.index("--slot") + 1]
    pin, e_in_obs = SLOT_PARAMS[slot]
    tb.CURRENT["slot"] = slot
    tb.install()
    tf.SHAKEOUT = SCREEN
    if e_in_obs:
        install_collect_e()
    # the reward term rides ON TOP of whichever collect is installed
    e2b.SLOT_PARAMS[slot] = (BETA, False)
    e2b.install_enrich2b(slot)
    sys.argv = [sys.argv[0]] + argv
    tf.main()


if __name__ == "__main__":
    main()
