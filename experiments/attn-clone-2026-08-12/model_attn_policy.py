"""Entity-attention two-head policy with pointer action heads.

Forward takes FLAT obs rows (N, 197) and returns (N, 43) logits
[activity 34 | message 9] — drop-in for the v4 trunk, so bc_loss2 and
the v4 evaluate/tables machinery reuse unchanged.

Design pinned here (what an artifact-v3 spec would encode):
- per-type linear embeddings; kitty tokens share ONE type embedding and
  critter tokens share one (identity by content — the F-010 thesis);
  message kinds get one embedding each (kind identity IS the position
  in HEAD_KINDS); chow/water/sunbeam one each; self and clock their own.
- 2 pre-norm transformer encoder layers, d=64, 4 heads, FFN 128;
  vacant slots key-padding-masked.
- summary = [self token out ∥ masked mean pool] (2d).
- POINTER HEADS for entity-targeted actions: the menu logit for
  (slot k, verb) is a verb-specific linear read of slot k's OUTPUT
  embedding — slot-order-free, and the piece that generalizes to
  schema 4's variable rosters unchanged. Dense heads (from the
  summary) for the 11 non-entity actions and the 9-way message head.

Menu map (ActionCodec::v2): dense [0-4,8,12,16,17,25,33]; kitty slot k
verbs rest/sleep/groom/chase/play -> 5+k / 9+k / 13+k / 22+k / 30+k;
critter slot j verbs chase/play -> 18+j / 26+j.
"""
import torch
from torch import nn

from obs_tokens import (CHOW_F, CLOCK_F, CRIT_F, KITTY_F, MSG_F, N_CHOW,
                        N_CRIT, N_KITTY, N_MSG, N_SUN, N_WATER, SELF_F,
                        SUN_F, WATER_F, tokenize_obs)

N_ACT, N_MSGHEAD = 34, 9
DENSE_ACT = [0, 1, 2, 3, 4, 8, 12, 16, 17, 25, 33]
KITTY_MENU = torch.tensor([[5 + k, 9 + k, 13 + k, 22 + k, 30 + k]
                           for k in range(N_KITTY)])          # (3, 5)
CRIT_MENU = torch.tensor([[18 + j, 26 + j] for j in range(N_CRIT)])  # (4, 2)


class EntityPolicy(nn.Module):
    def __init__(self, d_model=64, heads=4, layers=2, ffn=128):
        super().__init__()
        self.hyper = {"d_model": d_model, "heads": heads,
                      "layers": layers, "ffn": ffn}
        self.embed = nn.ModuleDict({
            "self": nn.Linear(SELF_F, d_model),
            "kitty": nn.Linear(KITTY_F, d_model),
            "chow": nn.Linear(CHOW_F, d_model),
            "water": nn.Linear(WATER_F, d_model),
            "sunbeam": nn.Linear(SUN_F, d_model),
            "critter": nn.Linear(CRIT_F, d_model),
            "msg": nn.Linear(MSG_F, d_model),
            "clock": nn.Linear(CLOCK_F, d_model),
        })
        # type-embedding rows: self, kitty(shared), chow, water, sunbeam,
        # critter(shared), msg x8 (per kind), clock
        self.type_emb = nn.Parameter(torch.zeros(6 + N_MSG + 1, d_model))
        layer = nn.TransformerEncoderLayer(
            d_model, heads, dim_feedforward=ffn, dropout=0.0,
            batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(layer, layers)
        self.norm = nn.LayerNorm(2 * d_model)
        self.dense_act = nn.Linear(2 * d_model, len(DENSE_ACT))
        self.msg_head = nn.Linear(2 * d_model, N_MSGHEAD)
        self.kitty_ptr = nn.Linear(d_model, KITTY_MENU.shape[1])
        self.crit_ptr = nn.Linear(d_model, CRIT_MENU.shape[1])

    def forward(self, obs):
        toks, pads = tokenize_obs(obs)
        order = ["self", "kitty", "chow", "water", "sunbeam", "critter",
                 "msg", "clock"]
        trows = {"self": [0], "kitty": [1] * N_KITTY, "chow": [2],
                 "water": [3], "sunbeam": [4], "critter": [5] * N_CRIT,
                 "msg": list(range(6, 6 + N_MSG)), "clock": [6 + N_MSG]}
        xs, ms = [], []
        for name in order:
            e = self.embed[name](toks[name]) + self.type_emb[trows[name]]
            xs.append(e)
            ms.append(pads[name])
        x = torch.cat(xs, dim=1)          # (N, 23, d)
        mask = torch.cat(ms, dim=1)       # (N, 23)
        h = self.encoder(x, src_key_padding_mask=mask)

        h0 = h[:, 0]                                       # self token
        hm = h.masked_fill(mask.unsqueeze(-1), 0.0)
        pool = hm.sum(1) / (~mask).sum(1, keepdim=True).clamp(min=1)
        summary = self.norm(torch.cat([h0, pool], dim=1))

        n = obs.shape[0]
        act = obs.new_zeros(n, N_ACT)
        act[:, DENSE_ACT] = self.dense_act(summary)
        k0 = 1                                             # kitty tokens
        hk = h[:, k0:k0 + N_KITTY]                         # (N, 3, d)
        act[:, KITTY_MENU.flatten()] = self.kitty_ptr(hk).reshape(n, -1)
        c0 = 1 + N_KITTY + N_CHOW + N_WATER + N_SUN        # critter tokens
        hc = h[:, c0:c0 + N_CRIT]                          # (N, 4, d)
        act[:, CRIT_MENU.flatten()] = self.crit_ptr(hc).reshape(n, -1)
        return torch.cat([act, self.msg_head(summary)], dim=1)
