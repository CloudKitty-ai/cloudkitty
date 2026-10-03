"""Check 2 — training inertness of the additive E fork (joint-arm
instrument shakeout, pre-prereg).

Question: does the forked trainer (policy/anchor = PolicyV5AddE with
zero-init e_col, obs buffer widened to 409 with the E column HELD AT
ZERO) reproduce the stock l14 trainer bitwise over N updates? If yes,
Professor req-4's schema-matched control arm IS the recorded l14 run
and the joint arm costs two seeds, not four.

Modes (one subprocess each; module state is single-use):
  stock      the l14-s1 path of train_ppo_enrich2c, verbatim
  stock2     same again (replicability baseline for bit-compare)
  fork       patched: tf.EntityPolicyV5 -> PolicyV5AddE, collect
             fragment widened to obs_dim+1 with col 408 = 0.0
  fork-red   fork with e_col=1e-3 AND E col=1.0 (channel live):
             the comparison harness MUST see this diverge, or it is
             vacuous. Predicted before running: diverges.

All runs: --threads 1, 20 updates (total-ticks 61440), probes and
mid-run ckpts suppressed; out dirs + the enrich2b trace redirected to
this scratch dir (e2b.SCREEN), never the recorded probe artifacts.
Seeds are the recorded l14-s1 arm's own (run_index 90) — a re-tread
of its first updates, no new band claimed; shakeout only, never cited
as results.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import torch

SCRATCH = Path(__file__).resolve().parent
ENRICH = Path("/Users/elizabethkelly/ai/cloudkitty/experiments/enrichment-decay-sweep-2026-09-26")
sys.path.insert(0, str(ENRICH / "trainer"))

import train_ppo_enrich2c as tc  # noqa: E402  (wires tb/tf/e2b, pins, slots)

tb, tf, e2b = tc.tb, tc.tf, tc.e2b
SLOT = "l14-s1"
N_UPDATES = 20
TICKS = N_UPDATES * 256 * 12  # fragment x n_worlds


def make_add_e(e_col_init, e_fill):
    from model_v5 import EntityPolicyV5

    class PolicyV5AddE(EntityPolicyV5):
        """Additive E: self-token embed + e_col * E (E = obs col 408).
        e_col zero-init = exactly the stock function (check 1)."""

        def __init__(self, **kw):
            super().__init__(**kw)
            self.e_col = torch.nn.Parameter(
                torch.full((self.hyper["d_model"],), float(e_col_init)))
            self.e_col._is_e_col = True

        def load_state_dict(self, sd, strict=True):
            if "e_col" not in sd:
                r = super().load_state_dict(sd, strict=False)
                assert set(r.missing_keys) == {"e_col"} and not r.unexpected_keys, r
                return r
            return super().load_state_dict(sd, strict=strict)

        def forward(self, obs):
            from obs_layout_v5 import OBS_DIM
            base, e = obs[:, :OBS_DIM], obs[:, OBS_DIM:]
            toks, pads = __import__("obs_tokens_v5").tokenize_obs(base)
            xs, ms = [], []
            import model_v5 as mv
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
            from obs_tokens_v5 import N_CHOW, N_CRIT, N_KITTY, N_SUN, N_WATER
            hk = h[:, 1:1 + N_KITTY]
            act[:, mv.KITTY_MENU_T.flatten()] = self.kitty_ptr(hk).reshape(n, -1)
            c0 = 1 + N_KITTY + N_CHOW + N_WATER + N_SUN
            hc = h[:, c0:c0 + N_CRIT]
            act[:, mv.CRIT_MENU_T.flatten()] = self.crit_ptr(hc).reshape(n, -1)
            return torch.cat([act, self.msg_head(summary)], dim=1)

    def collect_append(runner, policy, critic, vstats, T):
        """Stock tf.collect_fragment with the buffer widened by one
        column; col obs_dim holds e_fill (0.0 = the control)."""
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
        with torch.no_grad():
            for t in range(T):
                states = runner.states()
                v_raw = critic(torch.from_numpy(states)).squeeze(-1).numpy() * std + mean
                obs, mask, valid = runner.flat_obs(obs_dim, mask_dim)
                oe = np.concatenate(
                    [obs, np.full((n, tf.MAX_SEATS, 1), e_fill, np.float32)], -1)
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
            v_last = critic(torch.from_numpy(runner.states())
                            ).squeeze(-1).numpy() * std + mean
        meow_rate = 1000.0 * meow_n / max(1, dec_n)
        return buf, v_last, ent_sum / T, viol_sum / T, meow_rate

    return PolicyV5AddE, collect_append


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True,
                    choices=["stock", "stock2", "fork", "fork-red", "fork-split"])
    a = ap.parse_args()
    out = SCRATCH / f"run-{a.mode}"

    e2b.SCREEN = SCRATCH  # trace -> scratch, NEVER the recorded artifacts
    tb.CURRENT["slot"] = SLOT
    tb.install()
    tf.SHAKEOUT = SCRATCH

    if a.mode in ("fork", "fork-red", "fork-split"):
        e_col_init, e_fill = (1e-3, 1.0) if a.mode == "fork-red" else (0.0, 0.0)
        cls, collect = make_add_e(e_col_init, e_fill)
        tf.EntityPolicyV5 = cls
        tf.collect_fragment = collect
        if a.mode == "fork-split":
            # Design under test: e_col is gradient-clipped in its own
            # group, so the main clip call sees the stock param list
            # exactly and its norm stack is unchanged.
            orig_clip = torch.nn.utils.clip_grad_norm_

            def split_clip(params, max_norm, **kw):
                ps = list(params)
                main = [p for p in ps if not getattr(p, "_is_e_col", False)]
                ecol = [p for p in ps if getattr(p, "_is_e_col", False)]
                gn = orig_clip(main, max_norm, **kw)
                if ecol:
                    orig_clip(ecol, max_norm, **kw)
                return gn

            torch.nn.utils.clip_grad_norm_ = split_clip

    e2b.SLOT_PARAMS[SLOT] = (tc.BETA, False)
    e2b.install_enrich2b(SLOT)
    sys.argv = [sys.argv[0], "--slot", SLOT,
                "--total-ticks", str(TICKS), "--threads", "1",
                "--probe-every", "1000000", "--ckpt-every", "1000000",
                "--out-dir", str(out)]
    tf.main()


if __name__ == "__main__":
    main()
