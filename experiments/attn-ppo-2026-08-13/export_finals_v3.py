"""Export the three PPO finals as v3 artifacts (the certified
export_oracle_v3 code path, pointed at policy-final checkpoints).

Writes artifacts/attn-A1-s{1,2,3}.ckpolicy + prints sha256s.
"""
import hashlib
import sys
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "attn-clone-2026-08-12"))

from export_oracle_v3 import dump  # noqa: E402  the certified writer
from model_attn_policy import EntityPolicy  # noqa: E402

for s in (1, 2, 3):
    ck = torch.load(HERE / f"artifacts/attn-A1-s{s}/policy-final.pt",
                    map_location="cpu", weights_only=True)
    m = EntityPolicy(**ck["hyper"])
    m.load_state_dict(ck["state_dict"])
    m.eval()
    out = HERE / f"artifacts/attn-A1-s{s}.ckpolicy"
    blob = dump(m)
    out.write_bytes(blob)
    print(f"attn-A1-s{s}.ckpolicy {len(blob)} bytes "
          f"sha256 {hashlib.sha256(blob).hexdigest()}")
