#!/bin/sh
# The exp-004 grid (prereg §3): A0 x5, A1 x5, D1 x5 — 15 runs, 20M
# ticks each, launched concurrently (the box is sized for 15 + headroom).
# Run from a DEDICATED WORKTREE (prereg §11), never the main checkout:
#   git worktree add ../cloudkitty-exp004-grid <frozen sha>
# Each run checkpoints every 50 updates and honors --resume, so an
# interrupted grid resumes with:  run_grid_v4.sh --resume
set -e
V="$(pwd)/experiments/exp-001-bc-mappo/trainer/.venv/bin/python"
P="experiments/exp-004-meow-channel/trainer"
RESUME="$1"

for arm in A0 A1 D1; do
  for seed in 1 2 3 4 5; do
    out="experiments/exp-004-meow-channel/artifacts/${arm}-s${seed}"
    PYTHONPATH="$P" "$V" "$P/train_ppo_v4.py" \
      --arm "$arm" --seed "$seed" $RESUME \
      > "${arm}-s${seed}.log" 2>&1 &
  done
done
echo "15 runs launched; tail the *.log files. Interrupt + rerun with"
echo "  run_grid_v4.sh --resume   to continue from checkpoints."
wait
