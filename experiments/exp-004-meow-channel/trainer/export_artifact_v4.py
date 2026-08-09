"""Export the two-head clone as a v2 .ckpolicy artifact.

exp-001's writer with one generation change: `artifact_version` 2 —
the loader (`cloudkitty_rl::policy`, ARTIFACT_VERSION = 2) validates the
final layer as menu_len + message_head_len (34 + 9 = 43) against its
compiled expectations, so a wrong-width export fails at load, loudly.
Schema stamps still come from the binding, never literals (the 2026-08-06
lesson recorded in exp-001's exporter).
"""

import argparse
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path

import cloudkitty as ck
import numpy as np
import torch

from model import MLP

_EXP1 = Path(__file__).resolve().parents[2] / "exp-001-bc-mappo" / "trainer"

ARTIFACT_VERSION = 2  # spec 028; the loader rejects anything else


def export(clone_path: Path, out_path: Path) -> str:
    ckpt = torch.load(clone_path, map_location="cpu", weights_only=True)
    model = MLP(ckpt["dims"])
    model.load_state_dict(ckpt["state_dict"])
    model.eval()

    linears = model.linears()
    header = {
        "artifact_version": ARTIFACT_VERSION,
        "observation_schema": ck.OBSERVATION_SCHEMA_VERSION,
        "action_schema": ck.ACTION_SCHEMA_VERSION,
        "mask_schema": ck.MASK_SCHEMA_VERSION,
        "layers": [[m.in_features, m.out_features] for m in linears],
        "activation": "relu",
    }
    header_json = (json.dumps(header, separators=(",", ":")) + "\n").encode()

    blob = bytearray()
    for m in linears:
        w = m.weight.detach().numpy()
        b = m.bias.detach().numpy()
        assert w.shape == (m.out_features, m.in_features)
        blob += np.ascontiguousarray(w, dtype="<f4").tobytes()
        blob += np.ascontiguousarray(b, dtype="<f4").tobytes()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(b"CKPOLICY" + struct.pack("<I", len(header_json))
                         + header_json + bytes(blob))
    sha = hashlib.sha256(out_path.read_bytes()).hexdigest()
    print(f"wrote {out_path} ({out_path.stat().st_size} bytes)")
    print(f"layers {header['layers']}  artifact v{ARTIFACT_VERSION}")
    print(f"schemas obs {header['observation_schema']} "
          f"action {header['action_schema']} mask {header['mask_schema']}")
    print(f"sha256 {sha}")
    return sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clone", type=Path,
                    default=Path("experiments/exp-004-meow-channel/artifacts/clone/clone.pt"))
    ap.add_argument("--out", type=Path,
                    default=Path("experiments/exp-004-meow-channel/artifacts/clone/clone.ckpolicy"))
    args = ap.parse_args()
    export(args.clone, args.out)


if __name__ == "__main__":
    main()
