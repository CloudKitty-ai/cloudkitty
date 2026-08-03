"""exp-002 critic pretrains: exp-001's loop over the v2 loader.

States are padded to the 5-kitty layout (data.py); one critic per γ,
never reused across γ (prereg §5). Pass the v2 paths explicitly:

  trainer/.venv/bin/python experiments/exp-002-mixed-population/trainer/critic_v2.py \
    --data-root experiments/exp-002-mixed-population/raw/bc-v2 \
    --out-dir experiments/exp-002-mixed-population/artifacts/clone-v2 \
    --gammas 0.995,0.998
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(1, str(HERE.parents[1] / "exp-001-bc-mappo" / "trainer"))

import train_critic  # exp-001's — its `import data` resolves to ours

if __name__ == "__main__":
    train_critic.main()
