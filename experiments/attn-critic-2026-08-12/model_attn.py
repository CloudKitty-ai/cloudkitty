"""Entity-attention critic: tokens -> transformer encoder -> value.

Kitty tokens share ONE type embedding: identity lives in token content
(traits), never in slot position — permutation-equivariance over kitties
is the point of the exercise (F-010's slot-pattern fragility is the
failure mode this architecture is meant to remove). Element-type tokens
get one embedding each (their identity IS their position in the layout);
the global token gets its own.
"""
import torch
from torch import nn

from tokens import ELEM_F, GLOBAL_F, KITTY_F, N_ELEM


class EntityCritic(nn.Module):
    def __init__(self, d_model=64, heads=4, layers=2, ffn=128):
        super().__init__()
        self.hyper = {"d_model": d_model, "heads": heads,
                      "layers": layers, "ffn": ffn}
        self.embed_kitty = nn.Linear(KITTY_F, d_model)
        self.embed_elem = nn.Linear(ELEM_F, d_model)
        self.embed_global = nn.Linear(GLOBAL_F, d_model)
        self.type_emb = nn.Parameter(torch.zeros(1 + N_ELEM + 1, d_model))
        layer = nn.TransformerEncoderLayer(
            d_model, heads, dim_feedforward=ffn, dropout=0.0,
            batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(layer, layers)
        self.head = nn.Sequential(
            nn.LayerNorm(d_model), nn.Linear(d_model, 64), nn.ReLU(),
            nn.Linear(64, 1))

    def forward(self, k, e, g, pad):
        tk = self.embed_kitty(k) + self.type_emb[0]
        te = self.embed_elem(e) + self.type_emb[1:1 + N_ELEM]
        tg = self.embed_global(g) + self.type_emb[-1]
        x = torch.cat([tk, te, tg], dim=1)
        mask = torch.cat(
            [pad, torch.zeros(pad.shape[0], N_ELEM + 1, dtype=torch.bool,
                              device=pad.device)], dim=1)
        h = self.encoder(x, src_key_padding_mask=mask)
        h = h.masked_fill(mask.unsqueeze(-1), 0.0)
        pooled = h.sum(dim=1) / (~mask).sum(dim=1, keepdim=True).clamp(min=1)
        return self.head(pooled)
