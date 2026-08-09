"""exp-001's artifact-expressible MLP, re-exported unchanged.

The two-head policy is ONE trunk with a 43-wide final layer (34 + 9,
split by index convention downstream) — the artifact contract sees a
plain MLP, which is the whole point of the ride-along design.
"""

import importlib.util
import sys
from pathlib import Path

_EXP1 = Path(__file__).resolve().parents[2] / "exp-001-bc-mappo" / "trainer"
_spec = importlib.util.spec_from_file_location("exp001_model", _EXP1 / "model.py")
_v1 = importlib.util.module_from_spec(_spec)
sys.modules["exp001_model"] = _v1
_spec.loader.exec_module(_v1)

MLP = _v1.MLP
