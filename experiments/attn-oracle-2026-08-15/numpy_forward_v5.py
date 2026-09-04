"""Independent numpy reference forward for the spec-049 surface (schema
5) -- the certified numpy_forward_v4 with only the layout moved: seven
token types, no message group, kitty rows 4 x 62, self 85, menu 39,
55 logits. Reads the artifact's own bytes (forward-v3.md module order).

One rule moved with the layout (spec 049 review): a token is padding iff
its whole feature row is zero. Under schema 5 a kitty row is permanent
by id and its first cell is "seen this tick", so a HEARD friend (present
0, message block live) is a real token; only a silent or vacant row (all
zero) is masked -- and an absent element slot is all zero as before.
"""
import json
import struct

import numpy as np

from obs_layout_v5 import (COUNTS, CRIT_MENU, CRIT_TOK, DENSE_ACT, KITTY_MENU,
                           KITTY_TOK, N_ACT, N_HEAD, N_TYPE_ROWS, TYPE_ROW,
                           WIDTHS)

EPS = 1e-5


def load_artifact(buf):
    assert buf[:8] == b"CKPOLICY"
    (hlen,) = struct.unpack("<I", buf[8:12])
    header = json.loads(buf[12:12 + hlen])
    assert header["artifact_version"] == 3
    assert header["observation_schema"] == 5
    d, ffn = header["d_model"], header["ffn"]
    layers = header["encoder_layers"]
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
    p["type_emb"] = take(N_TYPE_ROWS, d)
    for i in range(layers):
        p[f"L{i}.n1.w"], p[f"L{i}.n1.b"] = take(d), take(d)
        p[f"L{i}.qkv.w"], p[f"L{i}.qkv.b"] = take(3 * d, d), take(3 * d)
        p[f"L{i}.out.w"], p[f"L{i}.out.b"] = take(d, d), take(d)
        p[f"L{i}.n2.w"], p[f"L{i}.n2.b"] = take(d), take(d)
        p[f"L{i}.ff1.w"], p[f"L{i}.ff1.b"] = take(ffn, d), take(ffn)
        p[f"L{i}.ff2.w"], p[f"L{i}.ff2.b"] = take(d, ffn), take(d)
    p["sum.w"], p["sum.b"] = take(2 * d), take(2 * d)
    p["dense.w"], p["dense.b"] = take(len(DENSE_ACT), 2 * d), take(len(DENSE_ACT))
    p["msg.w"], p["msg.b"] = take(N_HEAD, 2 * d), take(N_HEAD)
    p["kptr.w"], p["kptr.b"] = take(5, d), take(5)
    p["cptr.w"], p["cptr.b"] = take(2, d), take(2)
    assert off[0] == len(buf), (off[0], len(buf))
    return p


def _ln(x, w, b):
    mu = x.mean(-1, keepdims=True)
    var = x.var(-1, keepdims=True)
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
            pad.append(~np.any(t != 0.0, axis=-1))
    x = np.concatenate(toks, 1)
    mask = np.concatenate(pad, 1)
    for i in range(p["header"]["encoder_layers"]):
        h = _ln(x, p[f"L{i}.n1.w"], p[f"L{i}.n1.b"])
        qkv = h @ p[f"L{i}.qkv.w"].T + p[f"L{i}.qkv.b"]
        q, k, v = np.split(qkv, 3, axis=-1)

        def sh(t):
            return t.reshape(n, -1, heads, hd).transpose(0, 2, 1, 3)

        q, k, v = sh(q), sh(k), sh(v)
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
    act = np.zeros((n, N_ACT))
    act[:, DENSE_ACT] = summary @ p["dense.w"].T + p["dense.b"]
    act[:, np.array(KITTY_MENU).flatten()] = (
        x[:, KITTY_TOK] @ p["kptr.w"].T + p["kptr.b"]).reshape(n, -1)
    act[:, np.array(CRIT_MENU).flatten()] = (
        x[:, CRIT_TOK] @ p["cptr.w"].T + p["cptr.b"]).reshape(n, -1)
    msg = summary @ p["msg.w"].T + p["msg.b"]
    return np.concatenate([act, msg], 1).astype(np.float32)
