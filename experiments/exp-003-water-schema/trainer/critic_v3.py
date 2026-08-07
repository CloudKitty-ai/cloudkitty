"""exp-003 critic pretrains: exp-001's loop over the v3 loader.

This directory's data.py (v3: the four-rollout split, scripted-only)
shadows exp-001's on sys.path, so train_critic runs unchanged. Pass the
v3 paths explicitly:

  experiments/exp-001-bc-mappo/trainer/.venv/bin/python \
    experiments/exp-003-water-schema/trainer/clone_v3.py \
    --data-root experiments/exp-003-water-schema/raw/bc-v3 \
    --out-dir experiments/exp-003-water-schema/artifacts/clone \
    --gammas 0.995,0.998
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(1, str(HERE.parents[1] / "exp-001-bc-mappo" / "trainer"))

import train_critic  # exp-001's — its `import data` resolves to ours

if __name__ == "__main__":
    train_critic.main()
