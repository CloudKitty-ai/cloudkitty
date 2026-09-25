#!/usr/bin/env bash
# Reward-shape screen: six overnight arms (PREREG frozen 2026-09-24).
# Launch ONLY after the world-size collection completes (owner's
# sequencing). Tier-5 pattern: parallel, 2 threads each, nice.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=experiments/exp-006-character-gen/.venv/bin/python
TR=experiments/reward-shape-screen-2026-09-24/trainer/train_ppo_shape.py
LOGS=experiments/reward-shape-screen-2026-09-24/results-raw/train-logs
mkdir -p "$LOGS"
for SLOT in hard-s1 hard-s2 cvx-s1 cvx-s2 lam-s1 lam-s2; do
  OMP_NUM_THREADS=2 nice caffeinate -s $PY $TR --slot $SLOT > "$LOGS/$SLOT.log" 2>&1 &
  echo "launched $SLOT pid $!"
done
wait
echo "== all six arms done $(date -u +%FT%TZ)"
