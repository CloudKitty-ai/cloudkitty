"""Independent numpy reference forward for the v3 entity-attention
artifact — the parity oracle's oracle. Reads the artifact's own bytes
(never the torch state dict) and reimplements the forward from the
contract text alone: pre-norm encoder layers (x + attn(norm1 x);
x + ffn(norm2 x)), packed QKV in-proj, masked softmax over keys,
LayerNorm eps 1e-5 biased variance, ReLU FFN, [self ∥ masked mean
pool] summary, dense + pointer head scatter per ActionCodec::v2.
"""
import json
import struct

import numpy as np

WIDTHS = [("self", 34), ("kitty", 20), ("chow", 5), ("water", 4),
          ("sunbeam", 6), ("critter", 10), ("msg", 4), ("clock", 1)]
COUNTS = {"self": 1, "kitty": 3, "chow": 2, "water": 2, "sunbeam": 2,
          "critter": 4, "msg": 8, "clock": 1}
TYPE_ROW = {"self": [0], "kitty": [1] * 3, "chow": [2], "water": [3],
            "sunbeam": [4], "critter": [5] * 4,
            "msg": list(range(6, 14)), "clock": [14]}
DENSE_ACT = [0, 1, 2, 3, 4, 8, 12, 16, 17, 25, 33]
KITTY_MENU = [[5 + k, 9 + k, 13 + k, 22 + k, 30 + k] for k in range(3)]
CRIT_MENU = [[18 + j, 26 + j] for j in range(4)]
EPS = 1e-5


def load_artifact(buf):
    assert buf[:8] == b"CKPOLICY"
    (hlen,) = struct.unpack("<I", buf[8:12])
    header = json.loads(buf[12:12 + hlen])
    assert header["artifact_version"] == 3
    assert header["architecture"] == "entity_attention"
    d, ffn = header["d_model"], header["ffn"]
    layers, heads = header["encoder_layers"], header["heads"]
    off = [12 + hlen]

    def take(*shape):
        n = int(np.prod(shape))
        a = np.frombuffer(buf, "<f4", n, off[0]).reshape(shape)
        off[0] += 4 * n
        return a.astype(np.float64)

    p = {"header": header}
    for name, w in WIDTHS:
        p[f"emb.{name}.w"] = take(d, w)
        p[f"emb.{name}.b"] = take(d)
    p["type_emb"] = take(15, d)
    for i in range(layers):
        p[f"L{i}.n1.w"], p[f"L{i}.n1.b"] = take(d), take(d)
        p[f"L{i}.qkv.w"], p[f"L{i}.qkv.b"] = take(3 * d, d), take(3 * d)
        p[f"L{i}.out.w"], p[f"L{i}.out.b"] = take(d, d), take(d)
        p[f"L{i}.n2.w"], p[f"L{i}.n2.b"] = take(d), take(d)
        p[f"L{i}.ff1.w"], p[f"L{i}.ff1.b"] = take(ffn, d), take(ffn)
        p[f"L{i}.ff2.w"], p[f"L{i}.ff2.b"] = take(d, ffn), take(d)
    p["sum.w"], p["sum.b"] = take(2 * d), take(2 * d)
    p["dense.w"], p["dense.b"] = take(11, 2 * d), take(11)
    p["msg.w"], p["msg.b"] = take(9, 2 * d), take(9)
    p["kptr.w"], p["kptr.b"] = take(5, d), take(5)
    p["cptr.w"], p["cptr.b"] = take(2, d), take(2)
    assert off[0] == len(buf), (off[0], len(buf))
    return p


def _ln(x, w, b):
    mu = x.mean(-1, keepdims=True)
    var = x.var(-1, keepdims=True)  # biased, matching PyTorch
    return (x - mu) / np.sqrt(var + EPS) * w + b


def numpy_forward(p, obs):
    obs = np.asarray(obs, np.float64)
    n = obs.shape[0]
    d = p["header"]["d_model"]
    heads = p["header"]["heads"]
    hd = d // heads

    toks, pad = [], []
    o = 0
    for name, w in WIDTHS:
        cnt = COUNTS[name]
        t = obs[:, o:o + cnt * w].reshape(n, cnt, w)
        o += cnt * w
        e = t @ p[f"emb.{name}.w"].T + p[f"emb.{name}.b"]
        e = e + p["type_emb"][TYPE_ROW[name]]
        toks.append(e)
        if name in ("self", "clock"):
            pad.append(np.zeros((n, cnt), bool))
        else:
            pad.append(t[:, :, 0] <= 0.0)
    x = np.concatenate(toks, 1)          # (n, 23, d)
    mask = np.concatenate(pad, 1)        # (n, 23)

    for i in range(p["header"]["encoder_layers"]):
        h = _ln(x, p[f"L{i}.n1.w"], p[f"L{i}.n1.b"])
        qkv = h @ p[f"L{i}.qkv.w"].T + p[f"L{i}.qkv.b"]
        q, k, v = np.split(qkv, 3, axis=-1)

        def split_heads(t):
            return t.reshape(n, -1, heads, hd).transpose(0, 2, 1, 3)

        q, k, v = split_heads(q), split_heads(k), split_heads(v)
        scores = q @ k.transpose(0, 1, 3, 2) / np.sqrt(hd)
        scores = np.where(mask[:, None, None, :], -np.inf, scores)
        a = np.exp(scores - scores.max(-1, keepdims=True))
        a = a / a.sum(-1, keepdims=True)
        att = (a @ v).transpose(0, 2, 1, 3).reshape(n, -1, d)
        x = x + att @ p[f"L{i}.out.w"].T + p[f"L{i}.out.b"]
        h = _ln(x, p[f"L{i}.n2.w"], p[f"L{i}.n2.b"])
        h = np.maximum(h @ p[f"L{i}.ff1.w"].T + p[f"L{i}.ff1.b"], 0.0)
        x = x + h @ p[f"L{i}.ff2.w"].T + p[f"L{i}.ff2.b"]

    h0 = x[:, 0]
    xm = np.where(mask[:, :, None], 0.0, x)
    pool = xm.sum(1) / np.maximum((~mask).sum(1, keepdims=True), 1)
    summary = _ln(np.concatenate([h0, pool], 1), p["sum.w"], p["sum.b"])

    act = np.zeros((n, 34))
    act[:, DENSE_ACT] = summary @ p["dense.w"].T + p["dense.b"]
    hk = x[:, 1:4]
    act[:, np.array(KITTY_MENU).flatten()] = (
        hk @ p["kptr.w"].T + p["kptr.b"]).reshape(n, -1)
    hc = x[:, 10:14]
    act[:, np.array(CRIT_MENU).flatten()] = (
        hc @ p["cptr.w"].T + p["cptr.b"]).reshape(n, -1)
    msg = summary @ p["msg.w"].T + p["msg.b"]
    return np.concatenate([act, msg], 1).astype(np.float32)
