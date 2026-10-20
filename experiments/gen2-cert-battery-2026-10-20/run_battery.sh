#!/usr/bin/env bash
# Step-8 cert battery driver (DECLARATION.md): three uniform trunk
# seatings through run_legs (scouts-first per displaced size, F-053
# 1000 stop armed everywhere). A scout miss SystemExits run_legs and
# set -e stops this driver — asymmetric, owner-routed, never
# auto-continued.
set -euo pipefail
cd "$(dirname "$0")"
LEGS=../gen2-comparator-legs-2026-10-14
PY=../exp-006-character-gen/.venv/bin/python
for s in g2-s1 g2-s2 g2-s4; do
  echo "== seating $s start $(date -u +%FT%TZ)"
  "$PY" "$LEGS/run_legs.py" \
    --config-20 "$LEGS/g2leg-20.toml" \
    --config-40 "$LEGS/g2leg-40.toml" \
    --config-100 "$LEGS/g2leg-100.toml" \
    --band g2cmp --seeds 30 --ticks 20000 --workers 6 \
    --seating "$s" --out-dir "results-raw/$s"
  echo "== seating $s done $(date -u +%FT%TZ)"
done
echo "== battery done $(date -u +%FT%TZ)"
