"""Spec-049 oracle fixtures (schema 5, T031): a seeded synthetic
entity-attention mind at the new surface -- no trained checkpoint can
carry across the fog wall (every embedding width moved), and a parity
oracle needs no training, only an INDEPENDENT reference forward --
exported v3-FORMAT at the schema-5 pins, plus a 408/55 parity file with
seeded synthetic rows covering per-class vacancy, the self+clock
extreme and every-kitty-row-heard (present 0, message block live). numpy only (no torch in any venv on the build machine); the
Rust forward (`artifact_v3_parity.rs`) is checked against
`numpy_forward_v5` within 1e-4.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from numpy_forward_v5 import load_artifact, numpy_forward  # noqa: E402
from obs_layout_v5 import (BLOCKS, CRITTER_SPAN, DENSE_ACT, ELEMENT_SPAN, KITTY_SPAN,  # noqa: E402
                           KITTY_W, N_HEAD, N_LOGITS, N_TYPE_ROWS, OBS_DIM, WIDTHS)

SEED = 20260903
D_MODEL, HEADS, LAYERS, FFN = 64, 4, 2, 128
N_REAL_LIKE, N_STRESS = 112, 40


def seeded_weights():
    rng = np.random.default_rng(SEED)
    blob = bytearray()

    def put(shape, scale):
        a = rng.normal(0.0, scale, size=shape).astype("<f4")
        blob.extend(a.tobytes())

    def put_ln(n):
        blob.extend(np.ones(n, "<f4").tobytes())
        blob.extend(np.zeros(n, "<f4").tobytes())

    d, ffn = D_MODEL, FFN
    for _, w in WIDTHS:
        put((d, w), 1.0 / np.sqrt(w))
        put((d,), 0.02)
    put((N_TYPE_ROWS, d), 0.1)
    for _ in range(LAYERS):
        put_ln(d)
        put((3 * d, d), 1.0 / np.sqrt(d))
        put((3 * d,), 0.02)
        put((d, d), 1.0 / np.sqrt(d))
        put((d,), 0.02)
        put_ln(d)
        put((ffn, d), 1.0 / np.sqrt(d))
        put((ffn,), 0.02)
        put((d, ffn), 1.0 / np.sqrt(ffn))
        put((d,), 0.02)
    put_ln(2 * d)
    put((len(DENSE_ACT), 2 * d), 1.0 / np.sqrt(2 * d))
    put((len(DENSE_ACT),), 0.02)
    put((N_HEAD, 2 * d), 1.0 / np.sqrt(2 * d))
    put((N_HEAD,), 0.02)
    put((5, d), 1.0 / np.sqrt(d))
    put((5,), 0.02)
    put((2, d), 1.0 / np.sqrt(d))
    put((2,), 0.02)
    header = json.dumps({
        "artifact_version": 3, "observation_schema": 5,
        "action_schema": 3, "mask_schema": 3,
        "architecture": "entity_attention",
        "d_model": D_MODEL, "heads": HEADS,
        "encoder_layers": LAYERS, "ffn": FFN,
    }).encode() + b"\n"
    return b"CKPOLICY" + struct.pack("<I", len(header)) + header + bytes(blob)


def synth_rows():
    rng = np.random.default_rng(SEED)
    obs = rng.uniform(0.0, 1.0, size=(N_REAL_LIKE + N_STRESS, OBS_DIM)).astype(np.float32)
    for i in range(obs.shape[0]):
        for (a, w) in BLOCKS:
            if rng.uniform() < 0.35:
                obs[i, a:a + w] = 0.0
    s = N_REAL_LIKE
    obs[s + 0:s + 8, KITTY_SPAN[0]:KITTY_SPAN[1]] = 0.0        # every kitty row vacant / silent
    obs[s + 8:s + 16, CRITTER_SPAN[0]:CRITTER_SPAN[1]] = 0.0   # every critter vacant
    obs[s + 16:s + 24, ELEMENT_SPAN[0]:ELEMENT_SPAN[1]] = 0.0  # every chow/water/sunbeam vacant
    obs[s + 24:s + 32, KITTY_SPAN[0]:CRITTER_SPAN[1]] = 0.0    # self + clock only
    # every kitty row HEARD (spec 049 review): present 0, the rest live --
    # the token attends; a "present <= 0" pad rule masks it (the bug).
    for i in range(s + 32, s + 40):
        for k in range(4):
            a = KITTY_SPAN[0] + KITTY_W * k
            obs[i, a:a + KITTY_W] = rng.uniform(0.05, 1.0, KITTY_W)
            obs[i, a] = 0.0
    return obs


def main():
    out = HERE / "fixtures"
    out.mkdir(exist_ok=True)
    art = seeded_weights()
    (out / "oracle-v5.ckpolicy").write_bytes(art)
    params = load_artifact(art)
    obs = synth_rows()
    logits = numpy_forward(params, obs).astype("<f4")
    n = obs.shape[0]
    assert logits.shape == (n, N_LOGITS)
    assert np.isfinite(logits).all()
    body = b"".join(np.concatenate([obs[i], logits[i]]).astype("<f4").tobytes() for i in range(n))
    (out / "oracle-v5.parity").write_bytes(struct.pack("<III", n, OBS_DIM, N_LOGITS) + body)
    print(f"rows {n} | artifact {len(art)} bytes | logits finite | obs {OBS_DIM} logits {N_LOGITS}")
    for f in ("oracle-v5.ckpolicy", "oracle-v5.parity"):
        print(f, hashlib.sha256((out / f).read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
