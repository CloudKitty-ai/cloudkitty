#!/usr/bin/env bash
# Displaced-size radius cell driver (DECLARATION.md): 40×40 at radius 4
# (the law's 5 minus one), scripted then the certified roster rot2,
# through run_legs (scout 3 worlds → leg 30, F-053 1000 stop armed
# everywhere). A scout miss or a leg stop SystemExits run_legs and
# set -e stops this driver — asymmetric, owner-routed, never
# auto-continued. --config-20/-100 are the driver's required inputs;
# --only 40 means they never run.
set -euo pipefail
cd "$(dirname "$0")"
LEGS=../gen2-comparator-legs-2026-10-14
PY=../exp-006-character-gen/.venv/bin/python
mkdir -p results-raw
for s in scripted g2-rot2; do
  echo "== seating $s start $(date -u +%FT%TZ)"
  "$PY" "$LEGS/run_legs.py" \
    --config-20 "$LEGS/g2leg-20.toml" \
    --config-40 g2leg-40-r4.toml \
    --config-100 "$LEGS/g2leg-100.toml" \
    --band g2cmp --seeds 30 --ticks 20000 --workers 6 --only 40 \
    --seating "$s" --out-dir "results-raw/$s" "$@"
  echo "== seating $s done $(date -u +%FT%TZ)"
done
echo "== cell done $(date -u +%FT%TZ)"
