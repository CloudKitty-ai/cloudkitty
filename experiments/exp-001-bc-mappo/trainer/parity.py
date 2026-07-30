"""Numpy-forward parity check: artifact bytes vs the torch clone.

Re-implements PolicyArtifact::forward from the artifact file alone (f32,
ReLU after every layer but the last, bias last) and compares logits with
the torch model on random dataset rows. Catches transposed weights,
truncated blobs, and dtype slips before kitty-eval ever sees the file.
Accumulation order differs between Rust/numpy/torch BLAS, so tolerance is
~1e-4 absolute on logits (f32 rounding, not a real mismatch).
"""

import argparse
import json
import struct
from pathlib import Path

import numpy as np
import torch

from data import load_dataset, stack_decisions
from model import MLP

MAGIC = b"CKPOLICY"


def read_artifact(path: Path):
    raw = path.read_bytes()
    assert raw[:8] == MAGIC, "bad magic"
    (hlen,) = struct.unpack_from("<I", raw, 8)
    header = json.loads(raw[12:12 + hlen])
    assert header["activation"] == "relu"
    off = 12 + hlen
    layers = []
    for d_in, d_out in header["layers"]:
        w = np.frombuffer(raw, dtype="<f4", count=d_in * d_out, offset=off)
        off += 4 * d_in * d_out
        b = np.frombuffer(raw, dtype="<f4", count=d_out, offset=off)
        off += 4 * d_out
        layers.append((w.reshape(d_out, d_in), b))
    assert off == len(raw), f"blob size mismatch: {len(raw) - off} trailing bytes"
    return header, layers


def numpy_forward(layers, x):
    x = x.astype(np.float32)
    for i, (w, b) in enumerate(layers):
        x = x @ w.T + b
        if i < len(layers) - 1:
            x = np.maximum(x, 0.0, dtype=np.float32)
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", type=Path,
                    default=Path("experiments/exp-001-bc-mappo/artifacts/clone/clone.ckpolicy"))
    ap.add_argument("--clone", type=Path,
                    default=Path("experiments/exp-001-bc-mappo/artifacts/clone/clone.pt"))
    ap.add_argument("--data-root", type=Path,
                    default=Path("experiments/exp-001-bc-mappo/raw/bc-v1"))
    ap.add_argument("--rows", type=int, default=100)
    ap.add_argument("--tol", type=float, default=1e-4)
    ap.add_argument("--seed", type=int, default=20260729)
    args = ap.parse_args()

    header, layers = read_artifact(args.artifact)
    ckpt = torch.load(args.clone, map_location="cpu", weights_only=True)
    model = MLP(ckpt["dims"])
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    assert header["layers"] == [[m.in_features, m.out_features]
                                for m in model.linears()], "layer shape mismatch"

    # Sample real observations — parity on the actual input distribution.
    train_r, _, dims = load_dataset(args.data_root, limit_rollouts=2)
    obs, _, _ = stack_decisions(train_r[:1])
    rng = np.random.default_rng(args.seed)
    rows = obs[rng.choice(obs.shape[0], size=args.rows, replace=False)]
    assert rows.shape[1] == header["layers"][0][0] == dims["obs_dim"]

    ours = numpy_forward(layers, rows)
    with torch.no_grad():
        theirs = model(torch.from_numpy(rows)).numpy()
    worst = float(np.abs(ours - theirs).max())
    print(f"{args.rows} rows, max |Δlogit| = {worst:.2e} (tol {args.tol:.0e})")
    assert worst <= args.tol, "PARITY FAILURE"
    print("parity OK")


if __name__ == "__main__":
    main()
