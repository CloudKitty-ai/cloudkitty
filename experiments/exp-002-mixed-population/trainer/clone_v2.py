"""exp-002 scratch clone: exp-001's training loop over the v2 loader.

This directory's data.py (v2: mixed rosters, frozen §5 split) shadows
exp-001's on sys.path, so train_clone runs unchanged. Pass the v2
paths explicitly:

  trainer/.venv/bin/python experiments/exp-002-mixed-population/trainer/clone_v2.py \
    --data-root experiments/exp-002-mixed-population/raw/bc-v2 \
    --out-dir experiments/exp-002-mixed-population/artifacts/clone-v2
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(1, str(HERE.parents[1] / "exp-001-bc-mappo" / "trainer"))

import train_clone  # exp-001's — its `import data` resolves to ours

if __name__ == "__main__":
    train_clone.main()
