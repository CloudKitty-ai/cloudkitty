"""Spec-033 oracle fixtures: the trained attn-clone EXPANDED to the new
surface (real weights carry; 7 new type-emb rows + 7 new msg-head rows
seeded deterministically), exported v3-FORMAT at the new schema pins,
plus a 225/50 parity file with seeded synthetic rows covering per-class
vacancy, the self+clock extreme, and nonzero reserve-kind digest slots
(FR-013). Self-check: numpy-from-bytes vs torch <= 1e-4 + exact argmax.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from model_v4 import EntityPolicyV4  # noqa: E402
from numpy_forward_v4 import load_artifact, numpy_forward  # noqa: E402
from obs_tokens_v4 import OBS_DIM  # noqa: E402

SEED = 20260815
N_REAL_LIKE, N_STRESS = 112, 32
EMBED_ORDER = ["self", "kitty", "chow", "water", "sunbeam", "critter",
               "msg", "clock"]


def expanded_checkpoint():
    old = torch.load(HERE.parent / "attn-clone-2026-08-12" / "artifacts"
                     / "attn-clone.pt", map_location="cpu",
                     weights_only=True)
    torch.manual_seed(SEED)
    m = EntityPolicyV4(**old["hyper"])
    sd = m.state_dict()
    osd = old["state_dict"]
    for k, v in osd.items():
        if k == "type_emb":
            sd[k][0:6] = v[0:6]          # self..critter rows
            sd[k][6:14] = v[6:14]        # 8 legacy msg kinds
            sd[k][21] = v[14]            # clock row moves 14 -> 21
            # rows 14..20 (7 new kinds) keep seeded init
        elif k in ("msg_head.weight", "msg_head.bias"):
            sd[k][:9] = v                # Silent + 8 legacy
        else:
            sd[k] = v
    m.load_state_dict(sd)
    m.eval()
    return m


def dump(model):
    sd = model.state_dict()
    blob = bytearray()

    def put(t):
        blob.extend(np.ascontiguousarray(
            t.detach().numpy().astype("<f4")).tobytes())

    for name in EMBED_ORDER:
        put(sd[f"embed.{name}.weight"])
        put(sd[f"embed.{name}.bias"])
    put(sd["type_emb"])
    for layer in (0, 1):
        p = f"encoder.layers.{layer}"
        for part in ("norm1.weight", "norm1.bias",
                     "self_attn.in_proj_weight", "self_attn.in_proj_bias",
                     "self_attn.out_proj.weight", "self_attn.out_proj.bias",
                     "norm2.weight", "norm2.bias",
                     "linear1.weight", "linear1.bias",
                     "linear2.weight", "linear2.bias"):
            put(sd[f"{p}.{part}"])
    put(sd["norm.weight"])
    put(sd["norm.bias"])
    for head in ("dense_act", "msg_head", "kitty_ptr", "crit_ptr"):
        put(sd[f"{head}.weight"])
        put(sd[f"{head}.bias"])
    header = json.dumps({
        "artifact_version": 3, "observation_schema": 4,
        "action_schema": 3, "mask_schema": 3,
        "architecture": "entity_attention",
        "d_model": model.hyper["d_model"], "heads": model.hyper["heads"],
        "encoder_layers": model.hyper["layers"], "ffn": model.hyper["ffn"],
    }).encode() + b"\n"
    return b"CKPOLICY" + struct.pack("<I", len(header)) + header + bytes(blob)


def synth_rows():
    """Seeded plausible rows: values in [0,1], presence-flag structure
    respected, then stress patterns layered on."""
    rng = np.random.default_rng(SEED)
    obs = rng.uniform(0.0, 1.0, size=(N_REAL_LIKE + N_STRESS, OBS_DIM)
                      ).astype(np.float32)
    # presence flags crisp: block starts either ~present (>=0.5 -> 1.0
    # semantics preserved by leaving value) or vacant (zero whole block)
    blocks = [(34 + 20 * k, 20) for k in range(3)]
    blocks += [(94 + 5 * j, 5) for j in range(2)]
    blocks += [(104 + 4 * j, 4) for j in range(2)]
    blocks += [(112 + 6 * j, 6) for j in range(2)]
    blocks += [(124 + 10 * j, 10) for j in range(4)]
    blocks += [(164 + 4 * k, 4) for k in range(15)]
    for i in range(obs.shape[0]):
        for (a, w) in blocks:
            if rng.uniform() < 0.35:
                obs[i, a:a + w] = 0.0
    s = N_REAL_LIKE
    # stress: per-class full vacancy
    obs[s + 0:s + 4, 34:94] = 0.0            # all kitties
    obs[s + 4:s + 8, 124:164] = 0.0          # all critters
    obs[s + 8:s + 12, 94:124] = 0.0          # all elements
    obs[s + 12:s + 16, 164:224] = 0.0        # digest silent
    obs[s + 16:s + 20, 34:224] = 0.0         # self+clock only
    # FR-013: reserve kinds (trill idx 13, ekekek idx 14) NONZERO
    for r in range(s + 20, s + 28):
        for kind in (13, 14):
            base = 164 + 4 * kind
            obs[r, base:base + 4] = rng.uniform(0.1, 1.0, 4)
    # chirp + all four Here* audible together
    for r in range(s + 28, s + 32):
        for kind in (8, 9, 10, 11, 12):
            base = 164 + 4 * kind
            obs[r, base:base + 4] = rng.uniform(0.1, 1.0, 4)
    return obs


def main():
    m = expanded_checkpoint()
    out = HERE / "fixtures"
    out.mkdir(exist_ok=True)
    art = dump(m)
    (out / "oracle-v4.ckpolicy").write_bytes(art)
    obs = synth_rows()
    with torch.no_grad():
        logits = m(torch.from_numpy(obs)).numpy().astype("<f4")
    n = obs.shape[0]
    assert logits.shape == (n, 50)
    body = b"".join(np.concatenate([obs[i], logits[i]]).astype("<f4")
                    .tobytes() for i in range(n))
    (out / "oracle-v4.parity").write_bytes(
        struct.pack("<III", n, OBS_DIM, 50) + body)
    params = load_artifact(art)
    np_logits = numpy_forward(params, obs)
    err = np.abs(np_logits - logits).max()
    ok = (np_logits[:, :34].argmax(1) == logits[:, :34].argmax(1)).all()
    ok_m = (np_logits[:, 34:].argmax(1) == logits[:, 34:].argmax(1)).all()
    print(f"rows {n} | artifact {len(art)} bytes | numpy-vs-torch max "
          f"|d| {err:.2e} | argmax act {bool(ok)} msg {bool(ok_m)}")
    assert err <= 1e-4 and ok and ok_m
    for f in ("oracle-v4.ckpolicy", "oracle-v4.parity"):
        print(f, hashlib.sha256((out / f).read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
