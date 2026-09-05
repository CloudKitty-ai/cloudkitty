"""Guard for model_v5 (plain asserts, no pytest).

    .venv/bin/python test_model_v5.py

The torch EntityPolicyV5 loaded with the seeded oracle's weights must
reproduce fixtures/oracle-v5.parity (numpy_forward_v5's logits, the
reference the Rust forward is certified against) within 1e-4 on every
row, including the stress rows (every kitty row heard, self + clock
only). A second test pins the surface: 408 in, 55 out, and a state_dict
whose every tensor is claimed by the artifact order (no stray module).
"""
import struct
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from model_v5 import EntityPolicyV5, load_artifact_state  # noqa: E402
from numpy_forward_v5 import load_artifact  # noqa: E402
from obs_layout_v5 import N_LOGITS, OBS_DIM  # noqa: E402

FIX = HERE / "fixtures"


def oracle():
    params = load_artifact((FIX / "oracle-v5.ckpolicy").read_bytes())
    h = params["header"]
    model = EntityPolicyV5(h["d_model"], h["heads"], h["encoder_layers"], h["ffn"])
    model.load_state_dict(load_artifact_state(params))   # strict: every key claimed
    model.eval()
    return model


def parity_rows():
    buf = (FIX / "oracle-v5.parity").read_bytes()
    n, obs_dim, n_logits = struct.unpack("<III", buf[:12])
    assert (obs_dim, n_logits) == (OBS_DIM, N_LOGITS), (obs_dim, n_logits)
    body = np.frombuffer(buf, "<f4", offset=12).reshape(n, obs_dim + n_logits)
    return body[:, :obs_dim].copy(), body[:, obs_dim:].copy()


def test_torch_forward_matches_the_certified_oracle():
    # red: swap two kitty-row pointer columns, or pad on present <= 0
    model = oracle()
    obs, want = parity_rows()
    with torch.no_grad():
        got = model(torch.from_numpy(obs)).numpy()
    assert got.shape == want.shape, (got.shape, want.shape)
    err = np.abs(got - want).max()
    assert err < 1e-4, f"max |torch - numpy| = {err}"


def test_surface_pins():
    model = EntityPolicyV5()
    with torch.no_grad():
        out = model(torch.zeros(3, OBS_DIM))
    assert out.shape == (3, N_LOGITS)
    assert torch.isfinite(out).all()
    # an all-zero observation pads every token but self and clock; the
    # forward must not NaN on the empty pool
    assert model.type_emb.shape[0] == 7


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
