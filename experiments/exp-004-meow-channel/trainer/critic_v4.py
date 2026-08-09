"""exp-004 critic pretrain: exp-001's loop over the v4 loader.

This directory's data.py (v4: two-channel rows, rollout-03 split)
shadows exp-001's on sys.path, so train_critic runs unchanged — the
critic never sees labels, only (padded state, censored MC return).

  experiments/exp-001-bc-mappo/trainer/.venv/bin/python \
    experiments/exp-004-meow-channel/trainer/critic_v4.py \
    --data-root experiments/exp-004-meow-channel/raw/bc-v4 \
    --out-dir experiments/exp-004-meow-channel/artifacts/clone \
    --gammas 0.998
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(1, str(HERE.parents[1] / "exp-001-bc-mappo" / "trainer"))

import train_critic  # exp-001's — its `import data` resolves to ours

if __name__ == "__main__":
    train_critic.main()
