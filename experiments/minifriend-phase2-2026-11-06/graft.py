#!/usr/bin/env python3
"""The graft (DECLARATION.md §4, ruling 3): a trunk seed's EntityPolicyV6 with its kitty embedding Linear(58 -> 64)
widened to Linear(58 + C -> 64), the new C columns ZERO, every other weight byte-equal. The widened map is held as
two blocks — the trunk's Linear(58 -> 64) untouched and a bias-free Linear(C -> 64) for the new columns, summed —
which is the same linear map (Adam is elementwise, so the training is the same too) and makes the first forward
BIT-EQUAL to the trunk's (one block held as one wider matrix reproduced the trunk to 2e-5 only, float accumulation
order). The widened policy reads a
WIDE observation x (N, 399 + 4·C): the trunk's 399 cells, then the four friend rows' appended cells (row order = the
observation's kitty rows), which the forward concatenates onto each kitty row before the embedding. Its first forward
on any observation therefore equals the trunk's (guard g1). Parameters: 84,450 + 64·C (no new bias).

The tokenizer's padding rule is the trunk's (obs_tokens_v6): a kitty row pads iff its 58 cells are all zero — the
appended cells never un-pad a silent row (a changed token set would break the identity). So the head cells act on
SEEN and HEARD rows only; on a silent row they are inert (DECLARATION §3 record note).

    graft.py --trunk-seed 1 --arm act15 --out <path>.pt     # writes the grafted init (sha-recorded in the manifest)
"""
import argparse
import json
import sys
from pathlib import Path

import torch
from torch import nn

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p2_common as C  # noqa: E402  (sys.path: attn-oracle, trunk trainer)
from model_v6 import EntityPolicyV6, ORDER, TYPE_ROW, KITTY_MENU_T, CRIT_MENU_T, KITTY_TOK, CRIT_TOK  # noqa: E402
from obs_layout_v6 import DENSE_ACT, N_ACT  # noqa: E402
from obs_tokens_v6 import tokenize_obs  # noqa: E402

OBS_DIM, N_ROWS, KITTY_W = C.OBS_DIM, C.N_ROWS, C.KITTY_W


def wide_dim(c):
    return OBS_DIM + N_ROWS * c


class PolicyP2(EntityPolicyV6):
    """EntityPolicyV6 whose kitty embedding takes 58 + C cells; forward(x_wide)."""

    def __init__(self, cells, d_model=64, heads=4, layers=2, ffn=128):
        super().__init__(d_model, heads, layers, ffn)
        self.cells = int(cells)
        self.embed_cells = nn.Linear(self.cells, d_model, bias=False)   # the new C columns of the kitty embedding
        nn.init.zeros_(self.embed_cells.weight)

    def split(self, x):
        n = x.shape[0]
        assert x.shape[1] == wide_dim(self.cells), (x.shape, self.cells)
        return x[:, :OBS_DIM], x[:, OBS_DIM:].reshape(n, N_ROWS, self.cells)

    def forward(self, x):
        obs, cells = self.split(x)
        toks, pads = tokenize_obs(obs)                 # padding by the 58-cell row only (trunk rule)
        xs, ms = [], []
        for name in ORDER:
            e = self.embed[name](toks[name])
            if name == "kitty":
                e = e + self.embed_cells(cells.to(obs.dtype))
            xs.append(e + self.type_emb[TYPE_ROW[name]])
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
        act[:, KITTY_MENU_T.flatten()] = self.kitty_ptr(h[:, KITTY_TOK]).reshape(n, -1)
        act[:, CRIT_MENU_T.flatten()] = self.crit_ptr(h[:, CRIT_TOK]).reshape(n, -1)
        return torch.cat([act, self.msg_head(summary)], dim=1)


def widen(trunk: EntityPolicyV6, cells: int) -> PolicyP2:
    """The graft itself: copy every trunk weight; the new C columns (embed_cells.weight) zero."""
    p2 = PolicyP2(cells, **trunk.hyper)
    sd = {k: v.clone() for k, v in trunk.state_dict().items()}
    sd["embed_cells.weight"] = torch.zeros(p2.embed_cells.weight.shape, dtype=sd["embed.kitty.weight"].dtype)
    p2.load_state_dict(sd, strict=True)
    # eval, as the trunk is loaded everywhere it acts: nn.TransformerEncoder takes its fused fast path only out of
    # training mode, and the two paths differ by ~1e-5 in the logits (found at g1; the trunk's own rollouts ran the
    # slow path, as this arc's training does, so bit-equality is checked eval against eval).
    p2.eval()
    return p2


def load_trunk(k):
    ck = torch.load(C.check_trunk_final(k), map_location="cpu", weights_only=True)
    trunk = EntityPolicyV6(**ck["hyper"])
    trunk.load_state_dict(ck["state_dict"])
    trunk.eval()
    return trunk, ck


def n_params(m):
    return sum(p.numel() for p in m.parameters())


def save_policy(p2, path, **record):
    torch.save({"hyper": p2.hyper, "cells": p2.cells, "state_dict": p2.state_dict(), **record}, path)


def load_policy(path):
    ck = torch.load(path, map_location="cpu", weights_only=True)
    p2 = PolicyP2(ck["cells"], **ck["hyper"])
    p2.load_state_dict(ck["state_dict"])
    p2.eval()
    return p2, ck


def graft(trunk_seed, cells):
    trunk, ck = load_trunk(trunk_seed)
    p2 = widen(trunk, cells)
    assert n_params(p2) == C.TRUNK_PARAMS + p2.embed_cells.out_features * cells, n_params(p2)
    return p2, trunk, ck


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trunk-seed", type=int, required=True, choices=C.TRUNK_SEEDS)
    ap.add_argument("--cells", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    p2, _trunk, ck = graft(a.trunk_seed, a.cells)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    save_policy(p2, a.out, graft={"trunk_seed": a.trunk_seed, "trunk_final": str(C.trunk_final(a.trunk_seed)),
                                  "trunk_final_sha256": C.TRUNK_FINAL_SHA[a.trunk_seed], "cells": a.cells,
                                  "params": n_params(p2), "trunk_stop_reason": ck.get("stop_reason")})
    print(json.dumps({"out": str(a.out), "params": n_params(p2), "sha256": C.sha256(a.out)}))


if __name__ == "__main__":
    main()
