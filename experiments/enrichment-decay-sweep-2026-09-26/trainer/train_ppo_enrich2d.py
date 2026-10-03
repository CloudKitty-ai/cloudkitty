#!/usr/bin/env python3
"""Joint release arm trainer (PREREG-D.md; owner's word "Go",
2026-10-03; design per the Professor's joint-arm critique and the
validated instrument in ../validation-joint-arm/).

j14: leash 0.01 (tf pin "beta_probe") AND E visible — appended as
obs column 408 (schema 5 + 1, lab buffers only; the clock keeps col
407). Policy and anchor are the ADDITIVE form: EntityPolicyV5 plus
e_col (zero-init d_model vector) entering the self token as
+ e_col*E — bit-identical to stock at e_col=0 (validation check 1),
so the anchor is the stock clone loaded as-is. e_col's gradient is
clipped in its OWN group at the same max-norm (split clip, declared:
joint clipping breaks the bit-exact control; validation check 2).
--threads 2 pinned by the prereg (recorded-control parity).

The reward term is stage B's enrich2b_terms at beta 0.14, accrual
gate False — identical to l14's. The rollout E uses roll_E_step
(train_ppo_enrich2c, guard-proven == enrich2b_terms).

    .../train_ppo_enrich2d.py --slot j14-s1
"""
import sys
from pathlib import Path

import numpy as np
import torch

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
from train_ppo_enrich2c import LEASH_PROBE, roll_E_step  # noqa: E402

import model_v5 as mv  # noqa: E402
from obs_layout_v5 import OBS_DIM  # noqa: E402
from obs_tokens_v5 import (N_CHOW, N_CRIT, N_KITTY, N_SUN, N_WATER,  # noqa: E402
                           tokenize_obs)

BETA = 0.14
E_COL = OBS_DIM  # 408: appended, never a schema-5 slot

_idx = 94
SLOT_PARAMS = {}
for _s in (1, 2):
    slot = f"j14-s{_s}"
    SLOT_PARAMS[slot] = True
    tb.WORLD[slot] = ((3.0, 7.0, 3000, 6), BEAM / "package.toml")
    tb.SLOTS[slot] = ("pin", "beta_probe", "init_lesson", _s, _idx)
    _idx += 1
# tb.install() replaces tf.PINS wholesale; the pin lives in BOTH
# (the PREREG-C deviation-1 lesson).
tb.PINS["beta_probe"] = LEASH_PROBE
tf.PINS["beta_probe"] = LEASH_PROBE

ROLL = {"Eo": None, "Ec": None}
CLIP_DIAG = {"steps": 0, "main_fired": 0, "ecol_ratio_sum": 0.0}


class PolicyV5AddE(mv.EntityPolicyV5):
    """Additive E (validation check 1): stock modules untouched;
    E = obs[:, 408] enters the self token as + e_col*E. At e_col=0
    the forward is bitwise the stock forward for any E, and for a
    408-wide input (the anchor path, run_probe) the term is skipped."""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.e_col = torch.nn.Parameter(torch.zeros(self.hyper["d_model"]))
        self.e_col._is_e_col = True

    def load_state_dict(self, sd, strict=True):
        if "e_col" not in sd:  # stock clone checkpoints carry no e_col
            r = super().load_state_dict(sd, strict=False)
            assert set(r.missing_keys) == {"e_col"} and not r.unexpected_keys, r
            return r
        return super().load_state_dict(sd, strict=strict)

    def forward(self, obs):
        base, e = obs[:, :OBS_DIM], obs[:, OBS_DIM:]
        toks, pads = tokenize_obs(base)
        xs, ms = [], []
        for name in mv.ORDER:
            x = self.embed[name](toks[name]) + self.type_emb[mv.TYPE_ROW[name]]
            if name == "self" and e.shape[1]:
                x = x + self.e_col * e.reshape(-1, 1, 1)
            xs.append(x)
            ms.append(pads[name])
        x = torch.cat(xs, dim=1)
        mask = torch.cat(ms, dim=1)
        h = self.encoder(x, src_key_padding_mask=mask)
        h0 = h[:, 0]
        hm = h.masked_fill(mask.unsqueeze(-1), 0.0)
        pool = hm.sum(1) / (~mask).sum(1, keepdim=True).clamp(min=1)
        summary = self.norm(torch.cat([h0, pool], dim=1))
        n = obs.shape[0]
        act = obs.new_zeros(n, mv.N_ACT)
        act[:, mv.DENSE_ACT] = self.dense_act(summary)
        hk = h[:, 1:1 + N_KITTY]
        act[:, mv.KITTY_MENU_T.flatten()] = self.kitty_ptr(hk).reshape(n, -1)
        c0 = 1 + N_KITTY + N_CHOW + N_WATER + N_SUN
        hc = h[:, c0:c0 + N_CRIT]
        act[:, mv.CRIT_MENU_T.flatten()] = self.crit_ptr(hc).reshape(n, -1)
        return torch.cat([act, self.msg_head(summary)], dim=1)


def split_clip(params, max_norm, **kw):
    """Declared split clip (PREREG-D §Design): e_col in its own group
    at the same max-norm; the main group is exactly the stock param
    list. Logs the clip diagnostic the prereg declares."""
    ps = list(params)
    main = [p for p in ps if not getattr(p, "_is_e_col", False)]
    ecol = [p for p in ps if getattr(p, "_is_e_col", False)]
    gn = _ORIG_CLIP(main, max_norm, **kw)
    if ecol:
        en = _ORIG_CLIP(ecol, max_norm, **kw)
        CLIP_DIAG["steps"] += 1
        CLIP_DIAG["main_fired"] += int(float(gn) > max_norm)
        CLIP_DIAG["ecol_ratio_sum"] += float(en) / max(float(gn), 1e-12)
    return gn


_ORIG_CLIP = torch.nn.utils.clip_grad_norm_


def install_collect_e_append():
    """Fork of tf.collect_fragment (the enrich2c pattern): buffers
    widened to obs_dim+1, the online stock written into col 408
    before the policy acts and stored, so rollout and PPO update see
    the same input."""
    def collect_with_e(runner, policy, critic, vstats, T):
        mean, std = vstats
        n = runner.n_worlds
        obs_dim, mask_dim = runner.dims
        buf = {
            "obs": np.zeros((T, n, tf.MAX_SEATS, obs_dim + 1), np.float32),
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
                oe = np.concatenate(
                    [obs, ((ROLL["Eo"] + ROLL["Ec"])[:, :, None]).astype(np.float32)], -1)
                to = torch.from_numpy(oe[valid])
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
                buf["obs"][t], buf["mask"][t], buf["valid"][t] = oe, mask, valid
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
    assert slot in SLOT_PARAMS, slot
    tb.CURRENT["slot"] = slot
    tb.install()
    tf.SHAKEOUT = SCREEN
    tf.EntityPolicyV5 = PolicyV5AddE
    torch.nn.utils.clip_grad_norm_ = split_clip
    install_collect_e_append()
    # enrich2b_terms reads self-block cols 0-14 only; the appended
    # col 408 is invisible to it. The reward term is l14's exactly.
    e2b.SLOT_PARAMS[slot] = (BETA, False)
    e2b.install_enrich2b(slot)
    # Clip diagnostic (PREREG-D §Instrument): cumulative counters
    # snapshotted once per collect; a snapshot reflects clip steps up
    # to the PREVIOUS update's optimization. The read takes fractions
    # from the final row.
    import json
    orig_collect = tf.collect_fragment
    diag_path = SCREEN / "artifacts" / f"ppo-fog-{slot}" / "clip-diag.jsonl"
    seen = {"u": 0}

    def collect_with_diag(*a, **kw):
        out = orig_collect(*a, **kw)
        seen["u"] += 1
        if CLIP_DIAG["steps"]:
            diag_path.parent.mkdir(parents=True, exist_ok=True)
            with diag_path.open("a") as f:
                f.write(json.dumps({"collect": seen["u"], **CLIP_DIAG}) + "\n")
        return out

    tf.collect_fragment = collect_with_diag
    sys.argv = [sys.argv[0]] + argv
    tf.main()


if __name__ == "__main__":
    main()
