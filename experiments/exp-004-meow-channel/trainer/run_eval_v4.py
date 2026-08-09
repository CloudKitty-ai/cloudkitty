"""§8/§9 evaluation sweep for exp-004 — exp-002's harness, this
generation's shapes and the FROZEN seed bands (prereg §6 ledger):

  i        mixed        870_001+  (the eval band; H4 welfare shape)
  iii      all-policy   880_001+  (stress band) served world
  roster3  all-policy   880_001+  family-00 (v5: roster 3, 20x20, lakeless)
  roster5  all-policy   880_001+  family-02 (v5: roster 5, 24x24, lake)

The stress shapes share the declared 880k band (same 30 seeds, three
worlds) exactly as the ledger registers. Evaluate-once is enforced by
the harness's ledger.

  python run_eval_v4.py <artifacts-dir> <shape> [--ticks N] [--seeds N]
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
REPO = EXP.parents[1]
_EXP2 = REPO / "experiments" / "exp-002-mixed-population" / "trainer"

_spec = importlib.util.spec_from_file_location("exp002_run_eval",
                                               _EXP2 / "run_eval.py")
_v2 = importlib.util.module_from_spec(_spec)
sys.modules["exp002_run_eval"] = _v2
_spec.loader.exec_module(_v2)

_v2.SHAPES = {
    "i":       ("mixed",      870_001, REPO / "cloudkitty.toml"),
    "iii":     ("all-policy", 880_001, REPO / "cloudkitty.toml"),
    "roster3": ("all-policy", 880_001, EXP / "family" / "family-00.toml"),
    "roster5": ("all-policy", 880_001, EXP / "family" / "family-02.toml"),
}

if __name__ == "__main__":
    _v2.main()
