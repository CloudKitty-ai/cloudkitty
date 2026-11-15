#!/usr/bin/env bash
# The re-anchor scout's legs (DECLARATION.md §6 R-B, §13 step 3; her launch word 2026-11-15): the arm's final in all
# five seats through run_legs.py on the Phase 2 arc venv, 20×20 then 40×40 (its 3-world scout first), the F-053 abort
# armed, acts recorded.
#
#   experiments/gen2-reanchor-scout-2026-11-14/run_legs_reanchor.sh [--only 20,40] [--workers 6]
#
# Output: results-raw/legs/reanchor-s1/{scouts,legs}/size<N>/ under this arc (gitignored, never deleted).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
A="$ROOT/experiments/minifriend-phase2-2026-11-06"
LEGS="$ROOT/experiments/gen2-comparator-legs-2026-10-14"
R="$ROOT/experiments/gen2-reanchor-scout-2026-11-14"
SEATING=reanchor-s1
cd "$ROOT"
mkdir -p "$R/results-raw/legs/$SEATING"
LOG="$R/results-raw/legs/$SEATING/run.log"
echo "== $SEATING $(date -u +%Y-%m-%dT%H:%M:%SZ) HEAD $(git rev-parse --short HEAD)" >> "$LOG"
OMP_NUM_THREADS=1 VIRTUAL_ENV="$A/.venv" caffeinate -s "$A/.venv/bin/python3" -B "$LEGS/run_legs.py" \
  --config-20 "$LEGS/g2leg-20.toml" --config-40 "$LEGS/g2leg-40.toml" --config-100 "$LEGS/g2leg-100.toml" \
  --band g2cmp --seeds 30 --ticks 20000 --workers 6 --seating "$SEATING" --record --python "$A/.venv/bin/python3" \
  --out-dir "$R/results-raw/legs/$SEATING" --only 20,40 "$@" 2>&1 | tee -a "$LOG"
