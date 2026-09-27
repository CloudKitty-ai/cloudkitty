#!/bin/bash
# Seating-analysis v1 collection (DECLARATION.md): 5 legs, sequential,
# nice'd beside the stage-B driver. Never edit while running.
set -u
cd "$(dirname "$0")"
PY=../exp-006-character-gen/.venv/bin/python
for seed in 900501 900502 900503 900504 900505; do
  echo "== leg $seed"
  OMP_NUM_THREADS=1 nice caffeinate -s "$PY" seating_collect.py \
    --seed "$seed" --ticks 20000 --out "results-raw/streams-$seed.npz"
done
echo "== seating collection done"
