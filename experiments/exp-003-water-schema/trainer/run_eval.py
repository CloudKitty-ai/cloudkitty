"""§8 evaluation sweep for exp-003 — exp-002's harness, exp-003's shapes.

The sweep logic (evaluate-once ledger, per-shape skip, fallback
counting, parallel workers) is exp-002's and is imported rather than
copied. What exp-003 owns is the SHAPES table: **fresh seed bands** and
**this generation's family worlds** for the roster gate.

Seed bands (700k series) are disjoint by construction from training
(>= 1e6), collection (600_001-614_004), the in-training probes
(40_001-3), exp-002's shapes (100k-320k), the screens (330k, 340k) and
exp-001/002 collection (400k, 500k).

Roster worlds come from exp-003's own family, so they carry this
generation's stratification: `family-00` is roster 3 **and** 20x20
**and** lakeless; `family-02` is roster 5, 24x24, with a lake. Those
axes are confounded — the family stratifies them jointly and no two
variants differ in roster alone. For §9.2 that is acceptable and if
anything conservative: the gate asks whether F-010 catatonia appears
*anywhere* on the deploy surface, so a harder world is a stronger test,
not a weaker one. It would not be acceptable for attributing a
difference to roster, and nothing here does that.

  python run_eval.py <artifacts-dir> <shape> [--ticks N] [--seeds N]
    shape = i | iii | roster3 | roster5
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
REPO = EXP.parents[1]
_EXP2 = REPO / "experiments" / "exp-002-mixed-population" / "trainer"

_spec = importlib.util.spec_from_file_location("exp002_run_eval", _EXP2 / "run_eval.py")
_v2 = importlib.util.module_from_spec(_spec)
sys.modules["exp002_run_eval"] = _v2
_spec.loader.exec_module(_v2)

# Read at call time by both run_one() and main(), so overriding the
# table here reconfigures the sweep without duplicating it.
_v2.SHAPES = {
    #  name        roster flag     seed band start   config
    "i":       ("mixed",      700_001, REPO / "cloudkitty.toml"),
    "iii":     ("all-policy", 710_001, REPO / "cloudkitty.toml"),
    "roster3": ("all-policy", 720_001, EXP / "family" / "family-00.toml"),
    "roster5": ("all-policy", 730_001, EXP / "family" / "family-02.toml"),
}

if __name__ == "__main__":
    _v2.main()
