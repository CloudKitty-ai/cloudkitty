"""Oracle fixtures for spec 030 (Product's certification gate).

Produces, from the step-2 checkpoint (artifacts/attn-clone.pt):
  fixtures/oracle.ckpolicy — the checkpoint as a v3 artifact
  fixtures/oracle.parity   — 128 real val rows + expected logits

v3 container (Product's inlined contract, 2026-08-13): b"CKPOLICY",
u32-LE header length, JSON header (exactly nine keys, newline counted),
then every tensor <f4, weights row-major [out][in], biases [out], in
the module order fixed by the contract. Type-embedding table stays its
own [15][64] block. Parity file: u32-LE n_rows, obs_len, logit_len,
then per row obs[197] ++ logits[43], all <f4.

Self-check before anything is handed over: the artifact is re-read
from ITS OWN BYTES and re-run through an independent numpy forward
(numpy_forward_v3.py); max |Δlogit| vs torch must be <= 1e-4 and the
greedy activity argmax must match on every row — the same gate
Product's #[ignore]d test applies.

Run from the repo root with exp-001's venv.
"""
import json
import struct
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parent / "exp-004-meow-channel" / "trainer"))

from data import load_dataset  # noqa: E402
from model_attn_policy import EntityPolicy  # noqa: E402
from numpy_forward_v3 import load_artifact, numpy_forward  # noqa: E402

N_REAL, N_STRESS, OBS_LEN, LOGIT_LEN = 128, 16, 197, 43
N_ROWS = N_REAL + N_STRESS
EMBED_ORDER = ["self", "kitty", "chow", "water", "sunbeam", "critter",
               "msg", "clock"]


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
        put(sd[f"{p}.norm1.weight"])
        put(sd[f"{p}.norm1.bias"])
        put(sd[f"{p}.self_attn.in_proj_weight"])
        put(sd[f"{p}.self_attn.in_proj_bias"])
        put(sd[f"{p}.self_attn.out_proj.weight"])
        put(sd[f"{p}.self_attn.out_proj.bias"])
        put(sd[f"{p}.norm2.weight"])
        put(sd[f"{p}.norm2.bias"])
        put(sd[f"{p}.linear1.weight"])
        put(sd[f"{p}.linear1.bias"])
        put(sd[f"{p}.linear2.weight"])
        put(sd[f"{p}.linear2.bias"])
    put(sd["norm.weight"])
    put(sd["norm.bias"])
    for head in ("dense_act", "msg_head", "kitty_ptr", "crit_ptr"):
        put(sd[f"{head}.weight"])
        put(sd[f"{head}.bias"])

    header = json.dumps({
        "artifact_version": 3, "observation_schema": 3,
        "action_schema": 2, "mask_schema": 2,
        "architecture": "entity_attention",
        "d_model": model.hyper["d_model"], "heads": model.hyper["heads"],
        "encoder_layers": model.hyper["layers"], "ffn": model.hyper["ffn"],
    }).encode() + b"\n"
    return b"CKPOLICY" + struct.pack("<I", len(header)) + header + bytes(blob)


def pick_rows():
    """128 deterministic real rows off the val split, spread across
    rollouts — real vacancy patterns exercise the padding mask."""
    _, val_r, _ = load_dataset(
        Path("experiments/exp-004-meow-channel/raw/bc-v4"))
    per = -(-N_REAL // len(val_r))  # ceil so truncation lands at N_REAL
    rows = []
    for r in val_r:
        n = r.obs.shape[0]
        idx = np.linspace(0, n - 1, per, dtype=np.int64)
        rows.append(np.asarray(r.obs[idx], dtype=np.float32))
    rows = np.concatenate(rows)[:N_REAL]
    assert rows.shape == (N_REAL, OBS_LEN), rows.shape

    # Derived vacancy-stress rows (real family worlds never leave
    # critter/sunbeam slots empty, but the padding mask must handle
    # them — zeroed blocks are the engine's own vacant encoding):
    # 0-3 critters vacant, 4-7 sunbeams, 8-11 chow+water, 12-15 every
    # optional token gone (self+clock only).
    s = rows[:N_STRESS].copy()
    s[0:4, 124:164] = 0.0
    s[4:8, 112:124] = 0.0
    s[8:12, 94:112] = 0.0
    s[12:16, 34:94] = 0.0
    s[12:16, 94:196] = 0.0
    return np.concatenate([rows, s])


def main():
    ck = torch.load(HERE / "artifacts/attn-clone.pt", weights_only=True)
    model = EntityPolicy(**ck["hyper"])
    model.load_state_dict(ck["state_dict"])
    model.eval()

    out = HERE / "fixtures"
    out.mkdir(exist_ok=True)
    art = dump(model)
    (out / "oracle.ckpolicy").write_bytes(art)

    obs = pick_rows()
    kitty_vacant = int((obs[:, 34] == 0).sum())  # first kitty slot present flag
    with torch.no_grad():
        logits = model(torch.from_numpy(obs)).numpy().astype("<f4")
    assert logits.shape == (N_ROWS, LOGIT_LEN)
    body = b"".join(np.concatenate([obs[i], logits[i]]).astype("<f4").tobytes()
                    for i in range(N_ROWS))
    (out / "oracle.parity").write_bytes(
        struct.pack("<III", N_ROWS, OBS_LEN, LOGIT_LEN) + body)

    # Self-check: numpy forward from the artifact's own bytes.
    params = load_artifact(art)
    np_logits = numpy_forward(params, obs)
    err = np.abs(np_logits - logits).max()
    argmax_ok = (np_logits[:, :34].argmax(1) == logits[:, :34].argmax(1)).all()
    print(f"rows {N_ROWS} (rows with a vacant first kitty slot: "
          f"{kitty_vacant}); artifact {len(art)} bytes")
    print(f"numpy-vs-torch max |dlogit| {err:.2e}; "
          f"greedy argmax match: {bool(argmax_ok)}")
    assert err <= 1e-4 and argmax_ok

    import hashlib
    for f in ("oracle.ckpolicy", "oracle.parity"):
        print(f, hashlib.sha256((out / f).read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
