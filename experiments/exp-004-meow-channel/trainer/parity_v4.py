"""Numpy-forward parity for the v2 (two-head) artifact.

exp-001's check over the v4 loader: re-implements the artifact forward
(f32, ReLU between layers, bias last) from the file bytes and compares
all 43 logits with the torch clone on random dataset rows. Head-split is
downstream convention, so parity on the full logit vector covers both.
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
    assert header["artifact_version"] == 2, header["artifact_version"]
    off = 12 + hlen
    layers = []
    for d_in, d_out in header["layers"]:
        w = np.frombuffer(raw, dtype="<f4", count=d_in * d_out, offset=off)
        off += 4 * d_in * d_out
        b = np.frombuffer(raw, dtype="<f4", count=d_out, offset=off)
        off += 4 * d_out
        layers.append((w.reshape(d_out, d_in), b))
    assert off == len(raw), f"{len(raw) - off} trailing bytes"
    return header, layers


def numpy_forward(layers, x):
    h = x.astype(np.float32)
    for i, (w, b) in enumerate(layers):
        h = h @ w.T + b
        if i < len(layers) - 1:
            h = np.maximum(h, 0.0, dtype=np.float32)
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clone", type=Path,
                    default=Path("experiments/exp-004-meow-channel/artifacts/clone/clone.pt"))
    ap.add_argument("--artifact", type=Path,
                    default=Path("experiments/exp-004-meow-channel/artifacts/clone/clone.ckpolicy"))
    ap.add_argument("--data-root", type=Path,
                    default=Path("experiments/exp-004-meow-channel/raw/bc-v4"))
    ap.add_argument("--rows", type=int, default=100)
    ap.add_argument("--tol", type=float, default=1e-4)
    ap.add_argument("--limit-rollouts", type=int, default=4)
    args = ap.parse_args()

    ckpt = torch.load(args.clone, map_location="cpu", weights_only=True)
    model = MLP(ckpt["dims"])
    model.load_state_dict(ckpt["state_dict"])
    model.eval()

    header, layers = read_artifact(args.artifact)
    assert [list(x) for x in zip(ckpt["dims"], ckpt["dims"][1:])] == \
        header["layers"], "layer shapes disagree"

    train_r, val_r, dims = load_dataset(args.data_root, args.limit_rollouts)
    obs = stack_decisions(train_r + val_r)[0]
    rng = np.random.default_rng(42)
    rows = rng.choice(obs.shape[0], size=min(args.rows, obs.shape[0]),
                      replace=False)
    x = np.asarray(obs[np.sort(rows)], dtype=np.float32)

    with torch.no_grad():
        torch_logits = model(torch.from_numpy(x)).numpy()
    np_logits = numpy_forward(layers, x)
    delta = np.abs(torch_logits - np_logits).max()
    print(f"{x.shape[0]} rows, {torch_logits.shape[1]} logits: "
          f"max |delta| = {delta:.2e} (tol {args.tol})")
    assert delta <= args.tol, "parity failed"
    print("parity OK")


if __name__ == "__main__":
    main()
