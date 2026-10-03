"""Check 1 — pad-equivalence (joint-arm instrument shakeout, pre-prereg).

Claim under test: padding the BC anchor's self-embed with one
zero-weight column (self 85 -> 86, E appended python-side) leaves the
forward numerically identical, so the padded clone is the SAME anchor.

Plan: load clone-fog.pt stock and padded; feed real schema-5 obs
(collected live from the gen1-A cert config, random masked actions,
seed 777 — shakeout only, outside every claimed band) with junk in the
E column; compare logits for bit-identity, else max |diff|.

Red (predicted before running): setting the pad column to 1e-3 with
random E MUST break equality — if it does not, the test is vacuous.
"""
import sys
from pathlib import Path

import numpy as np
import torch

EXP = Path("/Users/elizabethkelly/ai/cloudkitty/experiments")
sys.path.insert(0, str(EXP / "attn-oracle-2026-08-15"))

from model_v5 import EntityPolicyV5, ORDER  # noqa: E402
from obs_layout_v5 import (CRIT_MENU, DENSE_ACT, KITTY_MENU, N_ACT,  # noqa: E402
                           N_HEAD, OBS_DIM, TYPE_ROW)
from obs_tokens_v5 import (N_CHOW, N_CRIT, N_KITTY, N_SUN, N_WATER,  # noqa: E402
                           tokenize_obs)

CLONE = EXP / "fog-gen1-shakeout/results-raw/clones/clone-fog/clone-fog.pt"
CONFIG = EXP / "beam-world-screen-2026-09-19/package.toml"
SEED, TICKS = 777, 200

KITTY_MENU_T = torch.tensor(KITTY_MENU)
CRIT_MENU_T = torch.tensor(CRIT_MENU)


class PolicyV5PadE(EntityPolicyV5):
    """The planned joint-arm fork: obs 409 = schema 5 ++ [E]; E joins
    the token named by `target` ("self": 85 -> 86, or "clock": 1 -> 2).
    `target=None` is the transcription control: no pad, no E, forward
    copy must be bit-identical to stock or the copy itself drifted."""

    def __init__(self, target, **kw):
        super().__init__(**kw)
        self.target = target
        if target is not None:
            old = self.embed[target]
            self.embed[target] = torch.nn.Linear(old.in_features + 1,
                                                 old.out_features)

    def load_padded(self, sd):
        sd = dict(sd)
        if self.target is not None:
            w = sd[f"embed.{self.target}.weight"]
            sd[f"embed.{self.target}.weight"] = torch.cat(
                [w, torch.zeros(w.shape[0], 1, dtype=w.dtype)], dim=1)
        self.load_state_dict(sd)

    def forward(self, obs):
        base, e = obs[:, :OBS_DIM], obs[:, OBS_DIM:]
        toks, pads = tokenize_obs(base)
        toks = dict(toks)
        if self.target is not None:
            toks[self.target] = torch.cat(
                [toks[self.target], e.reshape(-1, 1, 1)], dim=-1)
        xs, ms = [], []
        for name in ORDER:
            xs.append(self.embed[name](toks[name]) + self.type_emb[TYPE_ROW[name]])
            ms.append(pads[name])
        x = torch.cat(xs, dim=1)
        mask = torch.cat(ms, dim=1)
        h = self.encoder(x, src_key_padding_mask=mask)
        h0 = h[:, 0]
        hm = h.masked_fill(mask.unsqueeze(-1), 0.0)
        pool = hm.sum(1) / (~mask).sum(1, keepdim=True).clamp(min=1)
        summary = self.norm(torch.cat([h0, pool], dim=1))
        n = obs.shape[0]
        act = obs.new_zeros(n, N_ACT)
        act[:, DENSE_ACT] = self.dense_act(summary)
        hk = h[:, 1:1 + N_KITTY]
        act[:, KITTY_MENU_T.flatten()] = self.kitty_ptr(hk).reshape(n, -1)
        c0 = 1 + N_KITTY + N_CHOW + N_WATER + N_SUN
        hc = h[:, c0:c0 + N_CRIT]
        act[:, CRIT_MENU_T.flatten()] = self.crit_ptr(hc).reshape(n, -1)
        return torch.cat([act, self.msg_head(summary)], dim=1)


class PolicyV5AddE(EntityPolicyV5):
    """Additive form of the same fork: self token embed becomes
    Linear85(x) + e_col * E with e_col zero-init. Mathematically the
    padded column; computationally the stock matmul plus a separate
    rank-1 term, so e_col=0 adds an exact-zero tensor."""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.e_col = torch.nn.Parameter(
            torch.zeros(self.hyper["d_model"] if "d_model" in self.hyper else 64))

    def forward(self, obs):
        base, e = obs[:, :OBS_DIM], obs[:, OBS_DIM:]
        toks, pads = tokenize_obs(base)
        xs, ms = [], []
        for name in ORDER:
            x = self.embed[name](toks[name]) + self.type_emb[TYPE_ROW[name]]
            if name == "self":
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
        act = obs.new_zeros(n, N_ACT)
        act[:, DENSE_ACT] = self.dense_act(summary)
        hk = h[:, 1:1 + N_KITTY]
        act[:, KITTY_MENU_T.flatten()] = self.kitty_ptr(hk).reshape(n, -1)
        c0 = 1 + N_KITTY + N_CHOW + N_WATER + N_SUN
        hc = h[:, c0:c0 + N_CRIT]
        act[:, CRIT_MENU_T.flatten()] = self.crit_ptr(hc).reshape(n, -1)
        return torch.cat([act, self.msg_head(summary)], dim=1)


def collect_obs():
    import cloudkitty
    env = cloudkitty.ParallelEnv(str(CONFIG), horizon=TICKS + 1)
    obs, infos = env.reset(seed=SEED)
    names = list(env.possible_agents)
    rng = np.random.default_rng(SEED)
    rows = []
    for _ in range(TICKS):
        acts = {}
        for a in names:
            rows.append(np.asarray(obs[a], np.float32))
            mk = np.asarray(infos[a]["mask"], np.uint8).astype(bool)
            n_act = 39
            acts[a] = (int(rng.choice(np.flatnonzero(mk[:n_act]))),
                       int(rng.choice(np.flatnonzero(mk[n_act:]))))
        obs, _r, _te, _tr, infos = env.step(acts)
    return np.stack(rows)


def main():
    torch.set_num_threads(1)
    art = torch.load(CLONE, map_location="cpu", weights_only=False)
    hyper, sd = art["hyper"], art["state_dict"]
    stock = EntityPolicyV5(**hyper)
    stock.load_state_dict(sd)
    stock.eval()

    obs = torch.from_numpy(collect_obs())
    print(f"obs batch: {tuple(obs.shape)} (expect (*, {OBS_DIM}))")
    g = torch.Generator().manual_seed(SEED)
    e_junk = torch.rand(obs.shape[0], 1, generator=g)

    with torch.no_grad():
        ref = stock(obs)

        ctrl = PolicyV5PadE(None, **hyper)
        ctrl.load_padded(sd)
        ctrl.eval()
        out = ctrl(torch.cat([obs, e_junk], dim=1))
        print(f"transcription control (no pad): bit-identical={torch.equal(ref, out)}"
              f"  max|diff|={float((ref - out).abs().max()):.3e}")

        for target in ("self", "clock"):
            padded = PolicyV5PadE(target, **hyper)
            padded.load_padded(sd)
            padded.eval()
            for tag, e in (("E=junk", e_junk), ("E=0", torch.zeros_like(e_junk)),
                           ("E=1", torch.ones_like(e_junk))):
                out = padded(torch.cat([obs, e], dim=1))
                bit = torch.equal(ref, out)
                print(f"pad={target} {tag}: bit-identical={bit}"
                      + ("" if bit else f"  max|diff|={float((ref - out).abs().max()):.3e}"))
            # RED: pad column 1e-3, random E -> equality must break.
            padded.embed[target].weight.data[:, -1] = 1e-3
            out = padded(torch.cat([obs, e_junk], dim=1))
            print(f"pad={target} RED nonzero-pad: bit-identical={torch.equal(ref, out)} "
                  f"max|diff|={float((ref - out).abs().max()):.3e} (must NOT be identical)")

        add = PolicyV5AddE(**hyper)
        add.load_state_dict(sd, strict=False)  # e_col stays zero-init
        add.eval()
        outs = {}
        for tag, e in (("E=junk", e_junk), ("E=0", torch.zeros_like(e_junk)),
                       ("E=1", torch.ones_like(e_junk))):
            out = add(torch.cat([obs, e], dim=1))
            outs[tag] = out
            bit = torch.equal(ref, out)
            print(f"additive {tag}: bit-identical={bit}"
                  + ("" if bit else f"  max|diff|={float((ref - out).abs().max()):.3e}"))
        print(f"additive E-invariance (junk vs 0, bitwise): "
              f"{torch.equal(outs['E=junk'], outs['E=0'])}")
        # RED: e_col nonzero, random E -> equality must break.
        add.e_col.data[:] = 1e-3
        out = add(torch.cat([obs, e_junk], dim=1))
        print(f"additive RED nonzero e_col: bit-identical={torch.equal(ref, out)} "
              f"max|diff|={float((ref - out).abs().max()):.3e} (must NOT be identical)")


if __name__ == "__main__":
    main()
