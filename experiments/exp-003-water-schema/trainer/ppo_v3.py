"""exp-003 PPO: exp-002's training loop over the v3 loader and family.

The loop itself is unchanged and deliberately so — exp-002's
train_ppo_v2 is the registered algorithm (§5 inherits it verbatim), and
the arms differ only in init, mix and gamma, which are flags.

**Why this binds modules explicitly instead of ordering sys.path.**
Three generations of trainer each ship a `data.py`, and two ship a
`ppo_env.py`, so the names collide. Path order alone cannot resolve it:
`train_ppo_v2` inserts exp-001's trainer at index 1 when it loads, which
would push exp-002's *behind* it and make `from ppo_env import
MAX_SEATS` find exp-001's single-roster runner. That is not a subtle
failure — it raises ImportError — but the same shadowing on `data` would
be silent and would train against the wrong split.

So the modules that must be pinned are loaded into `sys.modules` under
their canonical names first. `import X` consults `sys.modules` before
the path, so these win no matter how the path is later rearranged:

  data     -> v3's (this directory): the four-rollout split
  ppo_env  -> exp-002's: the mixed-population vectorized runner
  the rest -> exp-001's, resolved normally by train_ppo_v2 itself

Usage:
  experiments/exp-001-bc-mappo/trainer/.venv/bin/python \
    experiments/exp-003-water-schema/trainer/ppo_v3.py \
    --init clone --mix-pct 33 --gamma 0.998 --seed 1 \
    --family-dir  experiments/exp-003-water-schema/family \
    --clone       experiments/exp-003-water-schema/artifacts/clone/clone.pt \
    --critic-dir  experiments/exp-003-water-schema/artifacts/clone \
    --out-dir     experiments/exp-003-water-schema/artifacts/<arm>
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP2 = HERE.parents[1] / "exp-002-mixed-population" / "trainer"


def _bind(name: str, path: Path):
    """Load `path` as the canonical module `name`, ahead of any path search."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


sys.path.insert(1, str(EXP2))
_bind("data", HERE / "data.py")
_bind("ppo_env", EXP2 / "ppo_env.py")

import train_ppo_v2  # noqa: E402 — must follow the bindings above

if __name__ == "__main__":
    # Fail loudly if the bindings ever stop taking, rather than training
    # a whole arm against the wrong split.
    assert sys.modules["data"].__file__ == str(HERE / "data.py"), (
        f"`data` resolved to {sys.modules['data'].__file__}, not v3's"
    )
    assert sys.modules["ppo_env"].__file__ == str(EXP2 / "ppo_env.py"), (
        f"`ppo_env` resolved to {sys.modules['ppo_env'].__file__}, not exp-002's"
    )
    train_ppo_v2.main()
