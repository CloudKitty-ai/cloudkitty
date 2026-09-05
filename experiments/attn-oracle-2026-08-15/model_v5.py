"""EntityPolicy at the spec-049 surface (schema 5): 16 tokens, seven
token types, menu 39, message head 16, 55 logits. The certified v4
forward with only the layout moved (numpy_forward_v5 is the reference):
the message-kind token group is gone, kitty rows are 4 x 63, self is 85,
and a token is padding iff its whole feature row is zero (obs_tokens_v5).
Layout constants come from obs_layout_v5, never restated here.
"""
import torch
from torch import nn

from obs_layout_v5 import (COUNTS, CRIT_MENU, DENSE_ACT, KITTY_MENU, N_ACT, N_HEAD,
                           N_TYPE_ROWS, TYPE_ROW, WIDTHS)
from obs_tokens_v5 import N_CHOW, N_CRIT, N_KITTY, N_SUN, N_WATER, tokenize_obs

ORDER = [name for name, _w in WIDTHS]
KITTY_MENU_T = torch.tensor(KITTY_MENU)
CRIT_MENU_T = torch.tensor(CRIT_MENU)


class EntityPolicyV5(nn.Module):
    def __init__(self, d_model=64, heads=4, layers=2, ffn=128):
        super().__init__()
        self.hyper = {"d_model": d_model, "heads": heads,
                      "layers": layers, "ffn": ffn}
        self.embed = nn.ModuleDict({name: nn.Linear(w, d_model) for name, w in WIDTHS})
        self.type_emb = nn.Parameter(torch.zeros(N_TYPE_ROWS, d_model))
        layer = nn.TransformerEncoderLayer(
            d_model, heads, dim_feedforward=ffn, dropout=0.0,
            batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(layer, layers, enable_nested_tensor=False)
        self.norm = nn.LayerNorm(2 * d_model)
        self.dense_act = nn.Linear(2 * d_model, len(DENSE_ACT))
        self.msg_head = nn.Linear(2 * d_model, N_HEAD)
        self.kitty_ptr = nn.Linear(d_model, KITTY_MENU_T.shape[1])
        self.crit_ptr = nn.Linear(d_model, CRIT_MENU_T.shape[1])

    def forward(self, obs):
        toks, pads = tokenize_obs(obs)
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


def load_artifact_state(params):
    """numpy_forward_v5.load_artifact params -> an EntityPolicyV5
    state_dict (the forward-v3.md module order, weights as (out, in))."""
    t = {k: torch.as_tensor(v, dtype=torch.float32) for k, v in params.items()
         if k != "header"}
    sd = {}
    for name in ORDER:
        sd[f"embed.{name}.weight"] = t[f"emb.{name}.w"]
        sd[f"embed.{name}.bias"] = t[f"emb.{name}.b"]
    sd["type_emb"] = t["type_emb"]
    for i in range(params["header"]["encoder_layers"]):
        L = f"encoder.layers.{i}"
        sd[f"{L}.norm1.weight"], sd[f"{L}.norm1.bias"] = t[f"L{i}.n1.w"], t[f"L{i}.n1.b"]
        sd[f"{L}.self_attn.in_proj_weight"] = t[f"L{i}.qkv.w"]
        sd[f"{L}.self_attn.in_proj_bias"] = t[f"L{i}.qkv.b"]
        sd[f"{L}.self_attn.out_proj.weight"] = t[f"L{i}.out.w"]
        sd[f"{L}.self_attn.out_proj.bias"] = t[f"L{i}.out.b"]
        sd[f"{L}.norm2.weight"], sd[f"{L}.norm2.bias"] = t[f"L{i}.n2.w"], t[f"L{i}.n2.b"]
        sd[f"{L}.linear1.weight"], sd[f"{L}.linear1.bias"] = t[f"L{i}.ff1.w"], t[f"L{i}.ff1.b"]
        sd[f"{L}.linear2.weight"], sd[f"{L}.linear2.bias"] = t[f"L{i}.ff2.w"], t[f"L{i}.ff2.b"]
    sd["norm.weight"], sd["norm.bias"] = t["sum.w"], t["sum.b"]
    sd["dense_act.weight"], sd["dense_act.bias"] = t["dense.w"], t["dense.b"]
    sd["msg_head.weight"], sd["msg_head.bias"] = t["msg.w"], t["msg.b"]
    sd["kitty_ptr.weight"], sd["kitty_ptr.bias"] = t["kptr.w"], t["kptr.b"]
    sd["crit_ptr.weight"], sd["crit_ptr.bias"] = t["cptr.w"], t["cptr.b"]
    return sd
