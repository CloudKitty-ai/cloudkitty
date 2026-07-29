"""Export a trained clone as a .ckpolicy artifact.

Byte layout per specs/014-multi-agent-rl/contracts/policy-artifact.md,
reference writer cloudkitty_rl::policy::write_artifact:
  b"CKPOLICY" | u32-LE header length | JSON header + "\n" (newline counted
  in the length) | per layer: f32-LE weights [out][in] (PyTorch
  nn.Linear.weight layout, no transpose), then bias [out].
No checksum in the file; the loader hashes the whole file at load.
"""

import argparse
import hashlib
import json
import struct
from pathlib import Path

import numpy as np
import torch

from model import MLP


def export(clone_path: Path, out_path: Path) -> str:
    ckpt = torch.load(clone_path, map_location="cpu", weights_only=True)
    model = MLP(ckpt["dims"])
    model.load_state_dict(ckpt["state_dict"])
    model.eval()

    linears = model.linears()
    header = {
        "artifact_version": 1,
        "observation_schema": 1,
        "action_schema": 1,
        "mask_schema": 1,
        "layers": [[m.in_features, m.out_features] for m in linears],
        "activation": "relu",
    }
    # serde emits compact JSON + trailing newline; loader only parses, but
    # matching the reference writer keeps artifacts byte-comparable.
    header_json = (json.dumps(header, separators=(",", ":")) + "\n").encode()

    blob = bytearray()
    for m in linears:
        w = m.weight.detach().numpy()  # (out, in), C-order == [out][in]
        b = m.bias.detach().numpy()
        assert w.shape == (m.out_features, m.in_features)
        blob += np.ascontiguousarray(w, dtype="<f4").tobytes()
        blob += np.ascontiguousarray(b, dtype="<f4").tobytes()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(b"CKPOLICY" + struct.pack("<I", len(header_json))
                         + header_json + bytes(blob))
    sha = hashlib.sha256(out_path.read_bytes()).hexdigest()
    print(f"wrote {out_path} ({out_path.stat().st_size} bytes)")
    print(f"layers {header['layers']}")
    print(f"sha256 {sha}")
    return sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clone", type=Path,
                    default=Path("experiments/exp-001-bc-mappo/artifacts/clone/clone.pt"))
    ap.add_argument("--out", type=Path,
                    default=Path("experiments/exp-001-bc-mappo/artifacts/clone/clone.ckpolicy"))
    args = ap.parse_args()
    export(args.clone, args.out)


if __name__ == "__main__":
    main()
